"""
Cosmic Avatar System

Creates privacy-preserving avatar identities that completely obscure real user information
while enabling full social interaction. Part of the cosmic privacy layer that transforms
financial trading into space exploration narratives.

Research basis:
- Avatar-based identities replace real names for privacy protection
- Geographic abstraction to cosmic sectors prevents location tracking
- Cosmic callsigns enable social features without identity exposure
- Virtual currency for sharing separate from real trading metrics
"""

import asyncio
import secrets
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any, Set
from enum import Enum
import json
import random

from ..constellation.constellation_formation_service import TrustLevel, SharingPermission


class CosmicRank(str, Enum):
    """Cosmic rank progression system"""
    CADET = "cadet"                    # New users (0-2 weeks)
    NAVIGATOR = "navigator"            # Learning progression (2-8 weeks)
    EXPLORER = "explorer"              # Active participants (8-16 weeks)
    COMMANDER = "commander"            # Trusted members (16-32 weeks)
    CAPTAIN = "captain"                # High engagement (32+ weeks)
    ADMIRAL = "admiral"                # Community leaders (rare)


class CosmicSector(str, Enum):
    """Galactic sectors for geographic abstraction"""
    ALPHA_CENTAURI = "alpha_centauri"
    BETA_QUADRANT = "beta_quadrant"
    GAMMA_SECTOR = "gamma_sector"
    DELTA_NEBULA = "delta_nebula"
    OMEGA_FRONTIER = "omega_frontier"
    NEBULA_EXPANSE = "nebula_expanse"
    QUANTUM_REALM = "quantum_realm"
    STELLAR_CORE = "stellar_core"
    VOID_TERRITORIES = "void_territories"
    COSMIC_CONFLUENCE = "cosmic_confluence"


class SpecializationPath(str, Enum):
    """Cosmic specialization paths for character progression"""
    STELLAR_NAVIGATOR = "stellar_navigator"      # Risk management focus
    FLEET_COMMANDER = "fleet_commander"          # Portfolio management
    ACADEMY_INSTRUCTOR = "academy_instructor"    # Educational content
    DIPLOMATIC_ENVOY = "diplomatic_envoy"        # Social/community
    EXPLORATION_SCOUT = "exploration_scout"      # Market discovery
    QUANTUM_ANALYST = "quantum_analyst"         # Advanced strategies


class CosmicCredentials:
    """Privacy-preserving credentials for cosmic avatar"""
    
    def __init__(
        self,
        user_id: int,
        cosmic_callsign: str,
        sector_assignment: CosmicSector,
        rank: CosmicRank = CosmicRank.CADET,
        specialization: Optional[SpecializationPath] = None
    ):
        self.user_id = user_id
        self.cosmic_callsign = cosmic_callsign
        self.sector_assignment = sector_assignment
        self.rank = rank
        self.specialization = specialization
        self.created_at = datetime.now(timezone.utc)
        self.last_active = datetime.now(timezone.utc)
        
        # Privacy protection
        self.identity_hash = self._generate_identity_hash()
        self.sharing_token = secrets.token_urlsafe(32)
        
        # Cosmic credits (virtual currency for sharing)
        self.cosmic_credits = 1000  # Starting amount
        self.stellar_reputation = 0  # Earned through community contribution
        
        # Achievement tracking (abstracted from real trading)
        self.academy_certifications: Set[str] = set()
        self.exploration_badges: Set[str] = set()
        self.diplomatic_honors: Set[str] = set()
        
        # Privacy settings
        self.visibility_settings = {
            "show_sector": True,
            "show_rank": True,
            "show_specialization": True,
            "show_academy_progress": True,
            "show_exploration_history": False,
            "show_constellation_membership": True
        }
    
    def _generate_identity_hash(self) -> str:
        """Generate privacy-preserving identity hash"""
        identity_string = f"{self.user_id}_{self.cosmic_callsign}_{self.created_at.timestamp()}"
        return hashlib.sha256(identity_string.encode()).hexdigest()[:16]
    
    def update_activity(self):
        """Update last active timestamp"""
        self.last_active = datetime.now(timezone.utc)
    
    def calculate_tenure_weeks(self) -> float:
        """Calculate tenure in weeks for rank progression"""
        return (datetime.now(timezone.utc) - self.created_at).days / 7.0
    
    def should_rank_up(self, activity_score: float, achievement_count: int) -> bool:
        """Determine if avatar should rank up"""
        tenure_weeks = self.calculate_tenure_weeks()
        
        rank_requirements = {
            CosmicRank.CADET: {"weeks": 0, "activity": 0, "achievements": 0},
            CosmicRank.NAVIGATOR: {"weeks": 2, "activity": 10, "achievements": 3},
            CosmicRank.EXPLORER: {"weeks": 8, "activity": 50, "achievements": 10},
            CosmicRank.COMMANDER: {"weeks": 16, "activity": 150, "achievements": 25},
            CosmicRank.CAPTAIN: {"weeks": 32, "activity": 400, "achievements": 50},
            CosmicRank.ADMIRAL: {"weeks": 64, "activity": 1000, "achievements": 100}
        }
        
        # Check next rank requirements
        next_ranks = list(CosmicRank)
        current_index = next_ranks.index(self.rank)
        
        if current_index < len(next_ranks) - 1:
            next_rank = next_ranks[current_index + 1]
            requirements = rank_requirements[next_rank]
            
            return (
                tenure_weeks >= requirements["weeks"] and
                activity_score >= requirements["activity"] and
                achievement_count >= requirements["achievements"]
            )
        
        return False
    
    def get_shareable_profile(self) -> Dict[str, Any]:
        """Get profile data safe for sharing"""
        shareable = {
            "cosmic_callsign": self.cosmic_callsign,
            "identity_hash": self.identity_hash,
            "rank": self.rank,
            "tenure_weeks": self.calculate_tenure_weeks(),
            "cosmic_credits": self.cosmic_credits,
            "stellar_reputation": self.stellar_reputation
        }
        
        # Add optional fields based on privacy settings
        if self.visibility_settings["show_sector"]:
            shareable["sector_assignment"] = self.sector_assignment
        
        if self.visibility_settings["show_specialization"] and self.specialization:
            shareable["specialization"] = self.specialization
        
        if self.visibility_settings["show_academy_progress"]:
            shareable["academy_certifications"] = len(self.academy_certifications)
            shareable["exploration_badges"] = len(self.exploration_badges)
            shareable["diplomatic_honors"] = len(self.diplomatic_honors)
        
        return shareable


class CosmicCallsignGenerator:
    """Generates unique cosmic callsigns with thematic consistency"""
    
    def __init__(self):
        self.stellar_prefixes = [
            "Nova", "Stellar", "Cosmic", "Quantum", "Nebula", "Aurora", "Galactic",
            "Solar", "Lunar", "Astral", "Void", "Photon", "Plasma", "Fusion",
            "Hyperion", "Andromeda", "Orion", "Vega", "Sirius", "Polaris"
        ]
        
        self.exploration_terms = [
            "Explorer", "Navigator", "Voyager", "Pioneer", "Scout", "Ranger",
            "Guardian", "Sentinel", "Pilot", "Captain", "Commander", "Admiral",
            "Keeper", "Seeker", "Wanderer", "Pathfinder", "Tracker", "Hunter"
        ]
        
        self.cosmic_suffixes = [
            "Prime", "Alpha", "Beta", "Gamma", "Delta", "Omega", "Zero",
            "One", "Seven", "Nine", "X", "Z", "Neo", "Core", "Max", "Ultra"
        ]
        
        self.used_callsigns: Set[str] = set()
    
    def generate_callsign(self, user_preferences: Dict[str, Any] = None) -> str:
        """Generate unique cosmic callsign"""
        max_attempts = 100
        
        for _ in range(max_attempts):
            # Generate callsign components
            prefix = random.choice(self.stellar_prefixes)
            term = random.choice(self.exploration_terms)
            
            # Combine in various patterns
            patterns = [
                f"{prefix}{term}",
                f"{term}{prefix}",
                f"{prefix}{term}{random.choice(self.cosmic_suffixes)}",
                f"{prefix}{random.choice(self.cosmic_suffixes)}{term}",
            ]
            
            callsign = random.choice(patterns)
            
            # Ensure uniqueness
            if callsign not in self.used_callsigns:
                self.used_callsigns.add(callsign)
                return callsign
        
        # Fallback with timestamp if all attempts failed
        fallback = f"Commander{int(datetime.now().timestamp()) % 10000}"
        self.used_callsigns.add(fallback)
        return fallback
    
    def suggest_callsigns(self, count: int = 5) -> List[str]:
        """Generate multiple callsign suggestions"""
        suggestions = []
        
        for _ in range(count):
            callsign = self.generate_callsign()
            suggestions.append(callsign)
        
        return suggestions


class CosmicAvatarSystem:
    """Main system for managing cosmic avatars and privacy layer"""
    
    def __init__(self):
        self.callsign_generator = CosmicCallsignGenerator()
        self.active_avatars: Dict[int, CosmicCredentials] = {}
        self.callsign_registry: Dict[str, int] = {}  # callsign -> user_id
        self.sector_populations: Dict[CosmicSector, int] = {}
        
        # Initialize sector populations
        for sector in CosmicSector:
            self.sector_populations[sector] = 0
    
    async def create_cosmic_avatar(
        self,
        user_id: int,
        preferred_callsign: Optional[str] = None,
        sector_preference: Optional[CosmicSector] = None,
        user_metadata: Dict[str, Any] = None
    ) -> CosmicCredentials:
        """Create new cosmic avatar with privacy protection"""
        
        if user_id in self.active_avatars:
            raise ValueError("User already has cosmic avatar")
        
        # Generate or validate callsign
        if preferred_callsign and preferred_callsign not in self.callsign_registry:
            cosmic_callsign = preferred_callsign
        else:
            cosmic_callsign = self.callsign_generator.generate_callsign()
        
        # Assign sector (balance populations)
        if sector_preference and self.sector_populations[sector_preference] < 1000:
            assigned_sector = sector_preference
        else:
            assigned_sector = self._assign_balanced_sector()
        
        # Create cosmic credentials
        avatar = CosmicCredentials(
            user_id=user_id,
            cosmic_callsign=cosmic_callsign,
            sector_assignment=assigned_sector,
            rank=CosmicRank.CADET
        )
        
        # Register avatar
        self.active_avatars[user_id] = avatar
        self.callsign_registry[cosmic_callsign] = user_id
        self.sector_populations[assigned_sector] += 1
        
        # Award initial academy certification
        avatar.academy_certifications.add("galactic_orientation")
        avatar.cosmic_credits += 500  # Welcome bonus
        
        return avatar
    
    def _assign_balanced_sector(self) -> CosmicSector:
        """Assign sector to balance populations"""
        # Find sectors with lowest population
        min_population = min(self.sector_populations.values())
        available_sectors = [
            sector for sector, population in self.sector_populations.items()
            if population == min_population
        ]
        
        return random.choice(available_sectors)
    
    async def update_avatar_progression(
        self,
        user_id: int,
        activity_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update avatar progression based on activity"""
        
        if user_id not in self.active_avatars:
            raise ValueError("User does not have cosmic avatar")
        
        avatar = self.active_avatars[user_id]
        avatar.update_activity()
        
        progression_updates = {
            "rank_changed": False,
            "new_certifications": [],
            "cosmic_credits_earned": 0,
            "reputation_gained": 0
        }
        
        # Calculate activity score from various sources
        activity_score = self._calculate_activity_score(activity_data)
        achievement_count = len(avatar.academy_certifications) + len(avatar.exploration_badges) + len(avatar.diplomatic_honors)
        
        # Check for rank progression
        if avatar.should_rank_up(activity_score, achievement_count):
            old_rank = avatar.rank
            avatar.rank = self._get_next_rank(avatar.rank)
            progression_updates["rank_changed"] = True
            progression_updates["old_rank"] = old_rank
            progression_updates["new_rank"] = avatar.rank
            
            # Award rank-up bonus
            rank_bonus = self._get_rank_bonus(avatar.rank)
            avatar.cosmic_credits += rank_bonus
            progression_updates["cosmic_credits_earned"] += rank_bonus
        
        # Process certifications based on activity
        new_certs = self._process_certifications(avatar, activity_data)
        progression_updates["new_certifications"] = new_certs
        
        # Award cosmic credits for activities
        credits_earned = self._calculate_credits_earned(activity_data)
        avatar.cosmic_credits += credits_earned
        progression_updates["cosmic_credits_earned"] += credits_earned
        
        # Update reputation for community activities
        reputation_gained = self._calculate_reputation_gained(activity_data)
        avatar.stellar_reputation += reputation_gained
        progression_updates["reputation_gained"] = reputation_gained
        
        return progression_updates
    
    def _calculate_activity_score(self, activity_data: Dict[str, Any]) -> float:
        """Calculate activity score from various engagement metrics"""
        score = 0.0
        
        # Educational activities (heavily weighted)
        score += activity_data.get("learning_modules_completed", 0) * 10
        score += activity_data.get("tutorial_progress", 0) * 5
        
        # Social activities
        score += activity_data.get("constellation_interactions", 0) * 3
        score += activity_data.get("achievements_shared", 0) * 2
        
        # Trading activities (abstracted)
        score += activity_data.get("missions_completed", 0) * 1
        score += activity_data.get("exploration_attempts", 0) * 0.5
        
        return score
    
    def _get_next_rank(self, current_rank: CosmicRank) -> CosmicRank:
        """Get next rank in progression"""
        ranks = list(CosmicRank)
        current_index = ranks.index(current_rank)
        
        if current_index < len(ranks) - 1:
            return ranks[current_index + 1]
        
        return current_rank  # Already at maximum rank
    
    def _get_rank_bonus(self, rank: CosmicRank) -> int:
        """Get cosmic credits bonus for rank achievement"""
        bonuses = {
            CosmicRank.NAVIGATOR: 2000,
            CosmicRank.EXPLORER: 5000,
            CosmicRank.COMMANDER: 10000,
            CosmicRank.CAPTAIN: 20000,
            CosmicRank.ADMIRAL: 50000
        }
        
        return bonuses.get(rank, 0)
    
    def _process_certifications(
        self,
        avatar: CosmicCredentials,
        activity_data: Dict[str, Any]
    ) -> List[str]:
        """Process and award new certifications"""
        new_certifications = []
        
        # Academy certifications (educational focus)
        if (activity_data.get("risk_management_modules", 0) >= 3 and
            "risk_management_certification" not in avatar.academy_certifications):
            avatar.academy_certifications.add("risk_management_certification")
            new_certifications.append("Stellar Navigation Safety Certification")
        
        if (activity_data.get("portfolio_modules", 0) >= 5 and
            "portfolio_certification" not in avatar.academy_certifications):
            avatar.academy_certifications.add("portfolio_certification")
            new_certifications.append("Fleet Operations Management Certification")
        
        # Exploration badges (trading milestones, abstracted)
        if (activity_data.get("successful_missions", 0) >= 10 and
            "exploration_novice" not in avatar.exploration_badges):
            avatar.exploration_badges.add("exploration_novice")
            new_certifications.append("Galactic Exploration Novice Badge")
        
        if (activity_data.get("sector_diversity", 0) >= 5 and
            "multi_sector_explorer" not in avatar.exploration_badges):
            avatar.exploration_badges.add("multi_sector_explorer")
            new_certifications.append("Multi-Sector Explorer Badge")
        
        # Diplomatic honors (social achievements)
        if (activity_data.get("constellation_contributions", 0) >= 20 and
            "community_contributor" not in avatar.diplomatic_honors):
            avatar.diplomatic_honors.add("community_contributor")
            new_certifications.append("Community Contribution Honor")
        
        return new_certifications
    
    def _calculate_credits_earned(self, activity_data: Dict[str, Any]) -> int:
        """Calculate cosmic credits earned from activities"""
        credits = 0
        
        # Educational activities earn most credits
        credits += activity_data.get("learning_modules_completed", 0) * 100
        credits += activity_data.get("tutorial_progress", 0) * 50
        
        # Social activities
        credits += activity_data.get("achievements_shared", 0) * 25
        credits += activity_data.get("constellation_interactions", 0) * 10
        
        # Mission activities (limited to prevent gaming)
        credits += min(activity_data.get("missions_completed", 0) * 5, 100)
        
        return credits
    
    def _calculate_reputation_gained(self, activity_data: Dict[str, Any]) -> int:
        """Calculate stellar reputation gained from community activities"""
        reputation = 0
        
        # Community contributions
        reputation += activity_data.get("constellation_contributions", 0) * 5
        reputation += activity_data.get("peer_mentoring", 0) * 10
        reputation += activity_data.get("content_shared", 0) * 2
        
        # Educational sharing (highly valued)
        reputation += activity_data.get("educational_content_shared", 0) * 15
        
        return reputation
    
    async def spend_cosmic_credits(
        self,
        user_id: int,
        amount: int,
        purpose: str,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """Spend cosmic credits for various cosmic features"""
        
        if user_id not in self.active_avatars:
            return False
        
        avatar = self.active_avatars[user_id]
        
        if avatar.cosmic_credits < amount:
            return False
        
        avatar.cosmic_credits -= amount
        
        # Record spending for analytics
        spending_record = {
            "user_hash": avatar.identity_hash,
            "amount": amount,
            "purpose": purpose,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {}
        }
        
        return True
    
    async def get_avatar_by_callsign(self, callsign: str) -> Optional[CosmicCredentials]:
        """Get avatar by cosmic callsign"""
        user_id = self.callsign_registry.get(callsign)
        if user_id:
            return self.active_avatars.get(user_id)
        return None
    
    async def get_sector_leaderboard(
        self,
        sector: CosmicSector,
        metric: str = "stellar_reputation",
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get leaderboard for specific sector"""
        
        sector_avatars = [
            avatar for avatar in self.active_avatars.values()
            if avatar.sector_assignment == sector
        ]
        
        # Sort by specified metric
        if metric == "stellar_reputation":
            sector_avatars.sort(key=lambda x: x.stellar_reputation, reverse=True)
        elif metric == "cosmic_credits":
            sector_avatars.sort(key=lambda x: x.cosmic_credits, reverse=True)
        elif metric == "tenure":
            sector_avatars.sort(key=lambda x: x.calculate_tenure_weeks(), reverse=True)
        
        # Return top avatars with privacy protection
        leaderboard = []
        for i, avatar in enumerate(sector_avatars[:limit]):
            leaderboard.append({
                "rank": i + 1,
                "cosmic_callsign": avatar.cosmic_callsign,
                "identity_hash": avatar.identity_hash,
                "avatar_rank": avatar.rank,
                "metric_value": getattr(avatar, metric, 0),
                "academy_certifications": len(avatar.academy_certifications),
                "exploration_badges": len(avatar.exploration_badges)
            })
        
        return leaderboard
    
    async def update_privacy_settings(
        self,
        user_id: int,
        new_settings: Dict[str, bool]
    ) -> bool:
        """Update avatar privacy settings"""
        
        if user_id not in self.active_avatars:
            return False
        
        avatar = self.active_avatars[user_id]
        
        # Validate and update settings
        valid_settings = {
            "show_sector", "show_rank", "show_specialization",
            "show_academy_progress", "show_exploration_history",
            "show_constellation_membership"
        }
        
        for setting, value in new_settings.items():
            if setting in valid_settings:
                avatar.visibility_settings[setting] = value
        
        return True
    
    async def get_cosmic_analytics(self) -> Dict[str, Any]:
        """Get system-wide cosmic avatar analytics"""
        
        total_avatars = len(self.active_avatars)
        
        # Rank distribution
        rank_distribution = {}
        for rank in CosmicRank:
            rank_distribution[rank] = len([
                avatar for avatar in self.active_avatars.values()
                if avatar.rank == rank
            ])
        
        # Sector distribution
        sector_distribution = dict(self.sector_populations)
        
        # Activity metrics
        total_cosmic_credits = sum(
            avatar.cosmic_credits for avatar in self.active_avatars.values()
        )
        
        total_reputation = sum(
            avatar.stellar_reputation for avatar in self.active_avatars.values()
        )
        
        return {
            "total_avatars": total_avatars,
            "rank_distribution": rank_distribution,
            "sector_distribution": sector_distribution,
            "economy_metrics": {
                "total_cosmic_credits": total_cosmic_credits,
                "total_stellar_reputation": total_reputation,
                "average_credits_per_avatar": total_cosmic_credits / max(1, total_avatars),
                "average_reputation_per_avatar": total_reputation / max(1, total_avatars)
            },
            "privacy_compliance": True,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }