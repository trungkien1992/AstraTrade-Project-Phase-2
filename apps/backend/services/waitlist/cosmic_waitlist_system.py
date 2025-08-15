"""
Cosmic Waitlist System

Implements privacy-preserving gamified waitlist mechanics inspired by Robinhood's
successful pre-launch campaign that achieved 1M users with K-factor 1.4-1.6.

Research basis:
- Robinhood's waitlist achieved viral growth through position transparency without P&L
- Gamified advancement through referrals creates FOMO without financial disclosure
- "Academy Recruitment" framing transforms waiting into learning opportunity
- Position transparency ("X ahead, Y behind") drives viral sharing
"""

import asyncio
import secrets
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum
import json
import random

from ..cosmic.cosmic_avatar_system import CosmicSector, CosmicCredentials
from ..privacy.privacy_preserving_referral_service import CosmicInviteCode, InviteCodeType


class WaitlistTier(str, Enum):
    """Waitlist tiers with cosmic theming"""
    RECRUIT_POOL = "recruit_pool"           # Standard waitlist
    PRIORITY_ACADEMY = "priority_academy"   # Referred users
    COMMANDER_TRACK = "commander_track"     # High referrers
    ADMIRAL_CIRCLE = "admiral_circle"       # VIP early access
    BETA_FLEET = "beta_fleet"              # Beta testing access


class WaitlistStatus(str, Enum):
    """Status within waitlist system"""
    PENDING = "pending"                     # Waiting for access
    ACADEMY_TRAINING = "academy_training"   # Pre-launch learning
    BETA_ACCESS = "beta_access"            # Beta testing
    FULL_ACCESS = "full_access"            # Platform access granted
    GRADUATED = "graduated"                # Successfully onboarded


class RecruitmentBonus(str, Enum):
    """Types of recruitment bonuses"""
    POSITION_ADVANCEMENT = "position_advancement"  # Move up in queue
    TIER_UPGRADE = "tier_upgrade"                 # Better waitlist tier
    EARLY_ACCESS = "early_access"                 # Skip ahead
    COSMIC_CREDITS = "cosmic_credits"             # Virtual currency
    ACADEMY_PREVIEW = "academy_preview"           # Exclusive content


class WaitlistEntry:
    """Individual entry in the cosmic waitlist"""
    
    def __init__(
        self,
        user_id: int,
        cosmic_callsign: str,
        email: str,
        sector_preference: CosmicSector,
        tier: WaitlistTier = WaitlistTier.RECRUIT_POOL,
        referral_code: Optional[str] = None
    ):
        self.user_id = user_id
        self.cosmic_callsign = cosmic_callsign
        self.email = email
        self.sector_preference = sector_preference
        self.tier = tier
        self.referral_code = referral_code
        
        # Waitlist mechanics
        self.joined_at = datetime.now(timezone.utc)
        self.position = 0  # Will be set by system
        self.status = WaitlistStatus.PENDING
        self.referrals_made = 0
        self.academy_progress = 0  # Pre-launch learning progress
        
        # Privacy protection
        self.waitlist_hash = self._generate_waitlist_hash()
        
        # Engagement tracking
        self.last_active = datetime.now(timezone.utc)
        self.academy_modules_completed: List[str] = []
        self.viral_shares_made = 0
        self.community_interactions = 0
        
        # Rewards earned
        self.cosmic_credits_earned = 0
        self.position_bonuses_received = 0
        self.tier_upgrades_received = 0
    
    def _generate_waitlist_hash(self) -> str:
        """Generate privacy-preserving waitlist hash"""
        hash_string = f"{self.user_id}_{self.cosmic_callsign}_{self.joined_at.timestamp()}"
        return hashlib.sha256(hash_string.encode()).hexdigest()[:12]
    
    def calculate_priority_score(self) -> float:
        """Calculate priority score for position in waitlist"""
        score = 0.0
        
        # Base score from join time (earlier = higher)
        days_since_join = (datetime.now(timezone.utc) - self.joined_at).days
        score += max(0, 100 - days_since_join)  # Earlier joiners get higher score
        
        # Referral bonus (major factor)
        score += self.referrals_made * 10
        
        # Academy engagement bonus
        score += len(self.academy_modules_completed) * 5
        score += self.academy_progress * 2
        
        # Community engagement bonus
        score += self.viral_shares_made * 3
        score += self.community_interactions * 1
        
        # Tier bonuses
        tier_bonuses = {
            WaitlistTier.RECRUIT_POOL: 0,
            WaitlistTier.PRIORITY_ACADEMY: 20,
            WaitlistTier.COMMANDER_TRACK: 50,
            WaitlistTier.ADMIRAL_CIRCLE: 100,
            WaitlistTier.BETA_FLEET: 200
        }
        score += tier_bonuses[self.tier]
        
        return score
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_active = datetime.now(timezone.utc)
    
    def is_eligible_for_tier_upgrade(self) -> Optional[WaitlistTier]:
        """Check if eligible for tier upgrade"""
        tier_requirements = {
            WaitlistTier.PRIORITY_ACADEMY: {"referrals": 1, "academy_progress": 20},
            WaitlistTier.COMMANDER_TRACK: {"referrals": 5, "academy_progress": 60},
            WaitlistTier.ADMIRAL_CIRCLE: {"referrals": 15, "academy_progress": 90},
            WaitlistTier.BETA_FLEET: {"referrals": 30, "academy_progress": 100}
        }
        
        current_tier_index = list(WaitlistTier).index(self.tier)
        
        for tier in list(WaitlistTier)[current_tier_index + 1:]:
            requirements = tier_requirements.get(tier, {})
            
            if (self.referrals_made >= requirements.get("referrals", 0) and
                self.academy_progress >= requirements.get("academy_progress", 0)):
                return tier
        
        return None
    
    def get_shareable_status(self) -> Dict[str, Any]:
        """Get status information safe for sharing"""
        return {
            "cosmic_callsign": self.cosmic_callsign,
            "waitlist_hash": self.waitlist_hash,
            "tier": self.tier,
            "position": self.position,
            "academy_progress": self.academy_progress,
            "recruitment_count": self.referrals_made,
            "sector_preference": self.sector_preference,
            "days_waiting": (datetime.now(timezone.utc) - self.joined_at).days,
            "cosmic_credits_earned": self.cosmic_credits_earned
        }


class CosmicWaitlistSystem:
    """Main system for managing cosmic-themed waitlist with viral mechanics"""
    
    def __init__(self):
        self.waitlist_entries: Dict[int, WaitlistEntry] = {}
        self.email_registry: Dict[str, int] = {}  # email -> user_id
        self.callsign_registry: Dict[str, int] = {}  # callsign -> user_id
        self.referral_tracking: Dict[str, List[int]] = {}  # referral_code -> [user_ids]
        
        # Waitlist configuration
        self.total_capacity = 50000  # Target pre-launch users
        self.beta_slots = 1000      # Beta testing slots
        self.daily_admissions = 100  # Users admitted per day
        
        # Academy content for pre-launch engagement
        self.academy_modules = self._initialize_academy_modules()
        
        # Viral mechanics tracking
        self.viral_metrics = {
            "total_signups": 0,
            "referral_conversions": 0,
            "k_factor": 0.0,
            "tier_distributions": {tier: 0 for tier in WaitlistTier}
        }
    
    def _initialize_academy_modules(self) -> List[Dict[str, Any]]:
        """Initialize pre-launch academy training modules"""
        return [
            {
                "id": "cosmic_trading_basics",
                "title": "Cosmic Trading Fundamentals",
                "description": "Learn the basics of navigating galactic markets",
                "progress_weight": 15,
                "unlock_requirement": None
            },
            {
                "id": "risk_navigation",
                "title": "Stellar Risk Navigation",
                "description": "Master the art of safe passage through market volatility",
                "progress_weight": 20,
                "unlock_requirement": "cosmic_trading_basics"
            },
            {
                "id": "fleet_management",
                "title": "Fleet Portfolio Management",
                "description": "Advanced strategies for multi-asset coordination",
                "progress_weight": 25,
                "unlock_requirement": "risk_navigation"
            },
            {
                "id": "diplomatic_trading",
                "title": "Intergalactic Market Diplomacy",
                "description": "Social aspects of cosmic trading communities",
                "progress_weight": 20,
                "unlock_requirement": "fleet_management"
            },
            {
                "id": "commander_certification",
                "title": "Elite Commander Certification",
                "description": "Final certification for cosmic trading mastery",
                "progress_weight": 20,
                "unlock_requirement": "diplomatic_trading"
            }
        ]
    
    async def join_waitlist(
        self,
        user_id: int,
        cosmic_callsign: str,
        email: str,
        sector_preference: CosmicSector,
        referral_code: Optional[str] = None,
        user_metadata: Dict[str, Any] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """Join the cosmic academy waitlist"""
        
        # Check for existing registration
        if user_id in self.waitlist_entries:
            return False, {"error": "Already registered for waitlist"}
        
        if email in self.email_registry:
            return False, {"error": "Email already registered"}
        
        if cosmic_callsign in self.callsign_registry:
            return False, {"error": "Cosmic callsign already taken"}
        
        # Check capacity
        if len(self.waitlist_entries) >= self.total_capacity:
            return False, {"error": "Cosmic Academy recruitment at capacity"}
        
        # Determine initial tier
        initial_tier = WaitlistTier.RECRUIT_POOL
        if referral_code:
            # Referred users get priority tier
            initial_tier = WaitlistTier.PRIORITY_ACADEMY
        
        # Create waitlist entry
        entry = WaitlistEntry(
            user_id=user_id,
            cosmic_callsign=cosmic_callsign,
            email=email,
            sector_preference=sector_preference,
            tier=initial_tier,
            referral_code=referral_code
        )
        
        # Register entry
        self.waitlist_entries[user_id] = entry
        self.email_registry[email] = user_id
        self.callsign_registry[cosmic_callsign] = user_id
        
        # Process referral if provided
        referral_bonus = None
        if referral_code:
            referral_bonus = await self._process_referral(referral_code, user_id)
        
        # Calculate initial position
        await self._recalculate_positions()
        
        # Update viral metrics
        self.viral_metrics["total_signups"] += 1
        self.viral_metrics["tier_distributions"][initial_tier] += 1
        
        if referral_code:
            self.viral_metrics["referral_conversions"] += 1
            self._update_k_factor()
        
        # Generate welcome package
        welcome_package = {
            "cosmic_callsign": cosmic_callsign,
            "waitlist_position": entry.position,
            "total_in_queue": len(self.waitlist_entries),
            "tier": initial_tier,
            "sector_assignment": sector_preference,
            "academy_access": True,
            "estimated_wait_time": self._estimate_wait_time(entry.position),
            "welcome_message": f"Welcome to the Galactic Trading Academy, Commander {cosmic_callsign}!",
            "next_steps": [
                "Begin academy training modules",
                "Invite fellow space traders to join your sector",
                "Participate in pre-launch community discussions"
            ]
        }
        
        if referral_bonus:
            welcome_package["referral_bonus"] = referral_bonus
        
        return True, welcome_package
    
    async def _process_referral(
        self,
        referral_code: str,
        new_user_id: int
    ) -> Optional[Dict[str, Any]]:
        """Process referral and award bonuses"""
        
        # Track referral
        if referral_code not in self.referral_tracking:
            self.referral_tracking[referral_code] = []
        
        self.referral_tracking[referral_code].append(new_user_id)
        
        # Find referrer (simplified - in production would decode referral_code)
        referrer_entry = None
        for entry in self.waitlist_entries.values():
            if entry.cosmic_callsign in referral_code:  # Simplified matching
                referrer_entry = entry
                break
        
        if not referrer_entry:
            return None
        
        # Award referrer bonuses
        referrer_entry.referrals_made += 1
        referrer_entry.cosmic_credits_earned += 500  # Bonus credits
        
        # Calculate position advancement bonus
        position_bonus = min(50, referrer_entry.referrals_made * 10)
        referrer_entry.position_bonuses_received += position_bonus
        
        # Check for tier upgrade
        new_tier = referrer_entry.is_eligible_for_tier_upgrade()
        if new_tier:
            old_tier = referrer_entry.tier
            referrer_entry.tier = new_tier
            referrer_entry.tier_upgrades_received += 1
            
            # Update tier distribution
            self.viral_metrics["tier_distributions"][old_tier] -= 1
            self.viral_metrics["tier_distributions"][new_tier] += 1
        
        return {
            "referrer_callsign": referrer_entry.cosmic_callsign,
            "position_advancement": position_bonus,
            "cosmic_credits_awarded": 500,
            "tier_upgrade": new_tier if new_tier else None,
            "total_referrals": referrer_entry.referrals_made
        }
    
    async def _recalculate_positions(self):
        """Recalculate waitlist positions based on priority scores"""
        
        # Sort entries by priority score (higher = better position)
        sorted_entries = sorted(
            self.waitlist_entries.values(),
            key=lambda x: x.calculate_priority_score(),
            reverse=True
        )
        
        # Assign positions
        for i, entry in enumerate(sorted_entries):
            entry.position = i + 1
    
    def _estimate_wait_time(self, position: int) -> str:
        """Estimate wait time based on position and admission rate"""
        days_to_admission = max(1, (position - self.beta_slots) // self.daily_admissions)
        
        if position <= self.beta_slots:
            return "Beta access available soon!"
        elif days_to_admission <= 7:
            return f"Approximately {days_to_admission} days"
        elif days_to_admission <= 30:
            return f"Approximately {days_to_admission // 7} weeks"
        else:
            return f"Approximately {days_to_admission // 30} months"
    
    def _update_k_factor(self):
        """Update viral coefficient (K-factor) calculation"""
        if self.viral_metrics["total_signups"] > 0:
            k_factor = self.viral_metrics["referral_conversions"] / self.viral_metrics["total_signups"]
            self.viral_metrics["k_factor"] = k_factor
    
    async def complete_academy_module(
        self,
        user_id: int,
        module_id: str
    ) -> Tuple[bool, Dict[str, Any]]:
        """Complete an academy training module"""
        
        if user_id not in self.waitlist_entries:
            return False, {"error": "Not registered for waitlist"}
        
        entry = self.waitlist_entries[user_id]
        entry.update_activity()
        
        # Find module
        module = next((m for m in self.academy_modules if m["id"] == module_id), None)
        if not module:
            return False, {"error": "Invalid module ID"}
        
        # Check if already completed
        if module_id in entry.academy_modules_completed:
            return False, {"error": "Module already completed"}
        
        # Check unlock requirements
        unlock_req = module.get("unlock_requirement")
        if unlock_req and unlock_req not in entry.academy_modules_completed:
            return False, {"error": f"Must complete {unlock_req} first"}
        
        # Mark module as completed
        entry.academy_modules_completed.append(module_id)
        entry.academy_progress += module["progress_weight"]
        entry.cosmic_credits_earned += 200  # Completion bonus
        
        # Check for tier upgrade
        new_tier = entry.is_eligible_for_tier_upgrade()
        tier_upgrade_info = None
        if new_tier:
            old_tier = entry.tier
            entry.tier = new_tier
            entry.tier_upgrades_received += 1
            
            # Update metrics
            self.viral_metrics["tier_distributions"][old_tier] -= 1
            self.viral_metrics["tier_distributions"][new_tier] += 1
            
            tier_upgrade_info = {
                "old_tier": old_tier,
                "new_tier": new_tier,
                "upgrade_message": f"Promoted to {new_tier.replace('_', ' ').title()}!"
            }
        
        # Recalculate positions (async)
        await self._recalculate_positions()
        
        completion_reward = {
            "module_completed": module["title"],
            "progress_gained": module["progress_weight"],
            "total_progress": entry.academy_progress,
            "cosmic_credits_earned": 200,
            "new_position": entry.position,
            "tier_upgrade": tier_upgrade_info
        }
        
        # Check for graduation eligibility
        if entry.academy_progress >= 100:
            completion_reward["graduation_eligible"] = True
            completion_reward["graduation_message"] = "Congratulations! You've mastered the Academy curriculum and are eligible for priority access!"
        
        return True, completion_reward
    
    async def share_waitlist_status(
        self,
        user_id: int,
        sharing_context: str = "general"
    ) -> Tuple[bool, Dict[str, Any]]:
        """Generate shareable waitlist status content"""
        
        if user_id not in self.waitlist_entries:
            return False, {"error": "Not registered for waitlist"}
        
        entry = self.waitlist_entries[user_id]
        entry.update_activity()
        entry.viral_shares_made += 1
        
        # Generate sharing content based on context
        sharing_templates = {
            "general": {
                "title": f"Commander {entry.cosmic_callsign} - Galactic Academy Recruit",
                "message": f"🚀 Joined the Galactic Trading Academy! Position #{entry.position} in the queue. The cosmic journey begins! Ready to explore the stars?",
                "call_to_action": "Join the Academy",
                "include_position": True
            },
            "progress": {
                "title": f"Academy Progress Update",
                "message": f"📚 {entry.academy_progress}% complete with Galactic Academy training! Mastering the art of cosmic trading. Join me in the stars!",
                "call_to_action": "Start Your Training",
                "include_position": False
            },
            "tier_upgrade": {
                "title": f"Cosmic Promotion Achieved!",
                "message": f"⭐ Promoted to {entry.tier.replace('_', ' ').title()}! Leading the charge toward galactic trading mastery. The academy awaits!",
                "call_to_action": "Join My Sector",
                "include_position": True
            }
        }
        
        template = sharing_templates.get(sharing_context, sharing_templates["general"])
        
        # Generate custom referral code
        referral_code = f"{entry.cosmic_callsign}-{entry.sector_preference}-RECRUIT"
        
        shareable_content = {
            "sharing_card": {
                "title": template["title"],
                "message": template["message"],
                "cosmic_callsign": entry.cosmic_callsign,
                "academy_progress": entry.academy_progress,
                "tier": entry.tier,
                "sector": entry.sector_preference,
                "cosmic_credits": entry.cosmic_credits_earned
            },
            "viral_mechanics": {
                "referral_code": referral_code,
                "call_to_action": template["call_to_action"],
                "position_transparency": entry.position if template["include_position"] else None,
                "queue_size": len(self.waitlist_entries),
                "sector_recruiting": f"{entry.sector_preference.replace('_', ' ').title()} Sector"
            },
            "incentives": {
                "referrer_bonus": "Advance your position and earn cosmic credits",
                "referee_bonus": "Join with priority academy access",
                "community_benefit": "Help build the strongest cosmic trading community"
            }
        }
        
        return True, shareable_content
    
    async def get_waitlist_analytics(self) -> Dict[str, Any]:
        """Get waitlist analytics with privacy preservation"""
        
        total_entries = len(self.waitlist_entries)
        
        # Calculate engagement metrics
        active_users = len([
            entry for entry in self.waitlist_entries.values()
            if entry.last_active > datetime.now(timezone.utc) - timedelta(days=7)
        ])
        
        academy_completion_rate = 0
        if total_entries > 0:
            completed_users = len([
                entry for entry in self.waitlist_entries.values()
                if entry.academy_progress >= 100
            ])
            academy_completion_rate = completed_users / total_entries
        
        # Referral metrics
        total_referrals = sum(entry.referrals_made for entry in self.waitlist_entries.values())
        avg_referrals_per_user = total_referrals / max(1, total_entries)
        
        return {
            "waitlist_metrics": {
                "total_entries": total_entries,
                "capacity_utilization": total_entries / self.total_capacity,
                "active_users_7d": active_users,
                "academy_completion_rate": academy_completion_rate
            },
            "viral_metrics": self.viral_metrics,
            "engagement_metrics": {
                "average_referrals_per_user": avg_referrals_per_user,
                "total_academy_modules_completed": sum(
                    len(entry.academy_modules_completed) for entry in self.waitlist_entries.values()
                ),
                "total_viral_shares": sum(
                    entry.viral_shares_made for entry in self.waitlist_entries.values()
                )
            },
            "tier_distribution": self.viral_metrics["tier_distributions"],
            "privacy_note": "All metrics use aggregated data with privacy preservation",
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    
    async def promote_beta_users(self, count: int = 100) -> List[Dict[str, Any]]:
        """Promote top waitlist users to beta access"""
        
        # Get top users by priority score
        eligible_entries = [
            entry for entry in self.waitlist_entries.values()
            if entry.status == WaitlistStatus.PENDING and entry.academy_progress >= 60
        ]
        
        # Sort by priority score
        eligible_entries.sort(key=lambda x: x.calculate_priority_score(), reverse=True)
        
        promoted_users = []
        for entry in eligible_entries[:count]:
            entry.status = WaitlistStatus.BETA_ACCESS
            entry.tier = WaitlistTier.BETA_FLEET
            
            promoted_users.append({
                "cosmic_callsign": entry.cosmic_callsign,
                "waitlist_hash": entry.waitlist_hash,
                "academy_progress": entry.academy_progress,
                "referrals_made": entry.referrals_made,
                "priority_score": entry.calculate_priority_score()
            })
        
        return promoted_users