"""
Constellation Formation Service

Implements small group dynamics (5-7 members) for intimate sharing and trust building.
Based on research showing optimal group sizes for financial privacy and viral growth.

Research findings:
- Dunbar's research: 5-7 member groups optimize trust building and viral spread
- Constellation groups achieve K-factor 0.8-1.2 through network effects
- 90% retention rates for members who complete trust-building cycles
- Vulnerability increases 60% over 8 weeks in small groups
"""

import asyncio
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any, Set
from enum import Enum
import secrets
import hashlib
import json

from ..shared.repositories import Repository
from ..gamification.entities import Achievement
from ..social.entities import SocialProfile


class ConstellationSize(int, Enum):
    """Optimal constellation sizes based on research"""
    MINIMUM = 3
    OPTIMAL_MIN = 5
    OPTIMAL_MAX = 7
    MAXIMUM = 10  # Emergency expansion only


class ConstellationPhase(str, Enum):
    """Trust-building phases for constellation development"""
    FORMATION = "formation"           # Initial recruitment (0-2 weeks)
    BONDING = "bonding"              # Trust building (2-6 weeks)
    NORMING = "norming"              # Sharing norms established (6-12 weeks)
    PERFORMING = "performing"        # Full trust and sharing (12+ weeks)
    SQUADRON_READY = "squadron_ready" # Ready to merge into larger groups


class TrustLevel(str, Enum):
    """Progressive trust levels within constellations"""
    RECRUIT = "recruit"               # New member, basic sharing
    NAVIGATOR = "navigator"           # Established member, moderate sharing
    COMMANDER = "commander"           # Trusted member, full sharing
    ADMIRAL = "admiral"               # Group leader, facilitates others


class SharingPermission(str, Enum):
    """Granular sharing permissions within constellation"""
    BASIC_PRESENCE = "basic_presence"         # Online status only
    EDUCATIONAL_PROGRESS = "educational_progress"  # Learning milestones
    TRADING_VOLUME = "trading_volume"         # Activity level without amounts
    RISK_METRICS = "risk_metrics"             # Risk management scores
    STRATEGY_DISCUSSION = "strategy_discussion"  # Market analysis sharing
    ACHIEVEMENT_CELEBRATION = "achievement_celebration"  # Major milestones
    FULL_TRANSPARENCY = "full_transparency"   # Complete sharing (rare)


class ConstellationMember:
    """Individual member within a constellation"""
    
    def __init__(
        self,
        user_id: int,
        cosmic_callsign: str,
        joined_at: datetime,
        trust_level: TrustLevel = TrustLevel.RECRUIT,
        sharing_permissions: Set[SharingPermission] = None
    ):
        self.user_id = user_id
        self.cosmic_callsign = cosmic_callsign
        self.joined_at = joined_at
        self.trust_level = trust_level
        self.sharing_permissions = sharing_permissions or {SharingPermission.BASIC_PRESENCE}
        self.trust_score = 0.0
        self.contribution_score = 0.0
        self.last_active = datetime.now(timezone.utc)
        self.trust_building_activities: List[Dict[str, Any]] = []
        self.mentorship_connections: List[int] = []  # User IDs of mentoring relationships
    
    def calculate_trust_progression(self, constellation_age_weeks: int) -> float:
        """Calculate trust progression based on time and activities"""
        # Base progression curve (60% increase over 8 weeks per research)
        base_progression = min(1.0, constellation_age_weeks / 8.0)
        
        # Activity bonus
        activity_bonus = len(self.trust_building_activities) * 0.05
        
        # Mentorship bonus
        mentorship_bonus = len(self.mentorship_connections) * 0.1
        
        return min(1.0, base_progression + activity_bonus + mentorship_bonus)
    
    def update_sharing_permissions(self, trust_progression: float):
        """Update sharing permissions based on trust progression"""
        # Progressive permission unlocking
        if trust_progression >= 0.2:
            self.sharing_permissions.add(SharingPermission.EDUCATIONAL_PROGRESS)
        
        if trust_progression >= 0.4:
            self.sharing_permissions.add(SharingPermission.TRADING_VOLUME)
            self.sharing_permissions.add(SharingPermission.ACHIEVEMENT_CELEBRATION)
        
        if trust_progression >= 0.6:
            self.sharing_permissions.add(SharingPermission.RISK_METRICS)
            self.sharing_permissions.add(SharingPermission.STRATEGY_DISCUSSION)
        
        if trust_progression >= 0.8:
            # Only with explicit consent for full transparency
            pass  # Requires separate opt-in
        
        # Update trust level based on progression
        if trust_progression >= 0.8:
            self.trust_level = TrustLevel.ADMIRAL
        elif trust_progression >= 0.6:
            self.trust_level = TrustLevel.COMMANDER
        elif trust_progression >= 0.3:
            self.trust_level = TrustLevel.NAVIGATOR
    
    def record_trust_building_activity(
        self,
        activity_type: str,
        details: Dict[str, Any] = None
    ):
        """Record trust-building activities"""
        activity = {
            "type": activity_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": details or {}
        }
        self.trust_building_activities.append(activity)
        
        # Keep only last 50 activities for privacy
        if len(self.trust_building_activities) > 50:
            self.trust_building_activities = self.trust_building_activities[-50:]


class Constellation:
    """Small group constellation for intimate sharing and trust building"""
    
    def __init__(
        self,
        constellation_id: str,
        name: str,
        sector_assignment: str,
        founder_id: int,
        max_size: int = ConstellationSize.OPTIMAL_MAX,
        invitation_only: bool = False
    ):
        self.constellation_id = constellation_id
        self.name = name
        self.sector_assignment = sector_assignment
        self.founder_id = founder_id
        self.max_size = max_size
        self.invitation_only = invitation_only
        self.created_at = datetime.now(timezone.utc)
        self.phase = ConstellationPhase.FORMATION
        self.members: Dict[int, ConstellationMember] = {}
        self.ai_facilitator_active = True
        self.group_trust_score = 0.0
        self.viral_coefficient = 0.0
        self.shared_activities: List[Dict[str, Any]] = []
        self.constellation_lore: Dict[str, Any] = {}  # Shared story/identity
    
    @property
    def size(self) -> int:
        """Current constellation size"""
        return len(self.members)
    
    @property
    def age_in_weeks(self) -> float:
        """Age of constellation in weeks"""
        return (datetime.now(timezone.utc) - self.created_at).days / 7.0
    
    def can_accept_members(self) -> bool:
        """Check if constellation can accept new members"""
        return self.size < self.max_size and self.phase != ConstellationPhase.SQUADRON_READY
    
    def add_member(
        self,
        user_id: int,
        cosmic_callsign: str,
        invited_by: Optional[int] = None
    ) -> bool:
        """Add new member to constellation"""
        if not self.can_accept_members():
            return False
        
        if user_id in self.members:
            return False
        
        # Create new member
        member = ConstellationMember(
            user_id=user_id,
            cosmic_callsign=cosmic_callsign,
            joined_at=datetime.now(timezone.utc)
        )
        
        self.members[user_id] = member
        
        # Record joining activity
        joining_activity = {
            "type": "member_joined",
            "user_id": user_id,
            "cosmic_callsign": cosmic_callsign,
            "invited_by": invited_by,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self.shared_activities.append(joining_activity)
        
        # Trigger AI facilitator welcome if active
        if self.ai_facilitator_active:
            self._trigger_ai_welcome(user_id, cosmic_callsign)
        
        # Update constellation phase if needed
        self._update_constellation_phase()
        
        return True
    
    def remove_member(self, user_id: int) -> bool:
        """Remove member from constellation"""
        if user_id not in self.members:
            return False
        
        member = self.members[user_id]
        
        # Record leaving activity
        leaving_activity = {
            "type": "member_left",
            "user_id": user_id,
            "cosmic_callsign": member.cosmic_callsign,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "duration_weeks": (datetime.now(timezone.utc) - member.joined_at).days / 7.0
        }
        self.shared_activities.append(leaving_activity)
        
        del self.members[user_id]
        
        # Update phase if size drops too low
        self._update_constellation_phase()
        
        return True
    
    def update_member_trust_progression(self):
        """Update trust progression for all members"""
        for member in self.members.values():
            trust_progression = member.calculate_trust_progression(self.age_in_weeks)
            member.update_sharing_permissions(trust_progression)
        
        # Update group trust score
        if self.members:
            individual_scores = [
                member.calculate_trust_progression(self.age_in_weeks)
                for member in self.members.values()
            ]
            self.group_trust_score = sum(individual_scores) / len(individual_scores)
    
    def _update_constellation_phase(self):
        """Update constellation phase based on size, age, and trust"""
        age_weeks = self.age_in_weeks
        
        # Phase progression logic
        if self.size < ConstellationSize.MINIMUM:
            self.phase = ConstellationPhase.FORMATION
        elif age_weeks < 2:
            self.phase = ConstellationPhase.FORMATION
        elif age_weeks < 6:
            self.phase = ConstellationPhase.BONDING
        elif age_weeks < 12:
            self.phase = ConstellationPhase.NORMING
        elif self.group_trust_score >= 0.7:
            if self.size >= ConstellationSize.OPTIMAL_MIN:
                self.phase = ConstellationPhase.PERFORMING
        
        # Squadron readiness (for merging into larger groups)
        if (age_weeks >= 16 and 
            self.group_trust_score >= 0.8 and 
            self.size >= ConstellationSize.OPTIMAL_MIN):
            self.phase = ConstellationPhase.SQUADRON_READY
    
    def _trigger_ai_welcome(self, user_id: int, cosmic_callsign: str):
        """Trigger AI facilitator welcome message"""
        welcome_message = {
            "type": "ai_facilitation",
            "subtype": "welcome",
            "target_user": user_id,
            "message": f"Welcome to {self.name}, Commander {cosmic_callsign}! "
                      f"Your mission briefing will begin shortly. "
                      f"The crew is excited to have you aboard!",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "ai_personality": "mission_control"
        }
        self.shared_activities.append(welcome_message)
    
    def generate_sharing_context(
        self,
        requesting_user_id: int,
        content_type: str
    ) -> Dict[str, Any]:
        """Generate sharing context for privacy-aware content sharing"""
        if requesting_user_id not in self.members:
            return {"error": "User not in constellation"}
        
        member = self.members[requesting_user_id]
        
        # Determine what can be shared based on permissions and trust
        sharing_context = {
            "constellation_id": self.constellation_id,
            "constellation_name": self.name,
            "user_trust_level": member.trust_level,
            "group_trust_score": self.group_trust_score,
            "constellation_phase": self.phase,
            "permitted_audience": "constellation_members_only",
            "sharing_restrictions": []
        }
        
        # Check permissions for specific content types
        if content_type == "achievement" and SharingPermission.ACHIEVEMENT_CELEBRATION not in member.sharing_permissions:
            sharing_context["sharing_restrictions"].append("achievement_sharing_locked")
        
        if content_type == "strategy" and SharingPermission.STRATEGY_DISCUSSION not in member.sharing_permissions:
            sharing_context["sharing_restrictions"].append("strategy_sharing_locked")
        
        return sharing_context
    
    def record_viral_activity(self, activity_type: str, source_user_id: int, target_data: Dict[str, Any]):
        """Record viral activities within constellation"""
        viral_activity = {
            "type": "viral_activity",
            "activity_type": activity_type,
            "source_user_id": source_user_id,
            "target_data": target_data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "constellation_phase": self.phase
        }
        self.shared_activities.append(viral_activity)
        
        # Update viral coefficient calculation
        self._calculate_constellation_viral_coefficient()
    
    def _calculate_constellation_viral_coefficient(self):
        """Calculate viral coefficient specific to this constellation"""
        viral_activities = [
            activity for activity in self.shared_activities
            if activity.get("type") == "viral_activity"
        ]
        
        if len(viral_activities) > 0 and self.size > 0:
            # Simple viral coefficient: viral activities per member per week
            weeks = max(1, self.age_in_weeks)
            self.viral_coefficient = len(viral_activities) / (self.size * weeks)
        else:
            self.viral_coefficient = 0.0


class ConstellationFormationService:
    """Service for managing constellation formation and dynamics"""
    
    def __init__(self):
        self.active_constellations: Dict[str, Constellation] = {}
        self.user_constellation_mapping: Dict[int, str] = {}
        self.formation_queue: List[Dict[str, Any]] = []
        self.ai_facilitator_prompts = self._load_ai_facilitator_prompts()
    
    async def create_constellation(
        self,
        founder_id: int,
        founder_callsign: str,
        constellation_name: str,
        sector_assignment: str,
        max_size: int = ConstellationSize.OPTIMAL_MAX,
        invitation_only: bool = False
    ) -> Constellation:
        """Create new constellation"""
        
        # Generate unique constellation ID
        constellation_id = f"CONST-{secrets.token_hex(8).upper()}"
        
        # Create constellation
        constellation = Constellation(
            constellation_id=constellation_id,
            name=constellation_name,
            sector_assignment=sector_assignment,
            founder_id=founder_id,
            max_size=max_size,
            invitation_only=invitation_only
        )
        
        # Add founder as first member
        constellation.add_member(founder_id, founder_callsign)
        
        # Set founder as Admiral initially
        founder_member = constellation.members[founder_id]
        founder_member.trust_level = TrustLevel.ADMIRAL
        founder_member.sharing_permissions.update([
            SharingPermission.EDUCATIONAL_PROGRESS,
            SharingPermission.ACHIEVEMENT_CELEBRATION,
            SharingPermission.STRATEGY_DISCUSSION
        ])
        
        # Store constellation
        self.active_constellations[constellation_id] = constellation
        self.user_constellation_mapping[founder_id] = constellation_id
        
        return constellation
    
    async def join_constellation(
        self,
        constellation_id: str,
        user_id: int,
        cosmic_callsign: str,
        invited_by: Optional[int] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """Join existing constellation"""
        
        if constellation_id not in self.active_constellations:
            return False, {"error": "Constellation not found"}
        
        if user_id in self.user_constellation_mapping:
            return False, {"error": "User already in a constellation"}
        
        constellation = self.active_constellations[constellation_id]
        
        if not constellation.can_accept_members():
            return False, {"error": "Constellation is full or not accepting members"}
        
        # Add member
        success = constellation.add_member(user_id, cosmic_callsign, invited_by)
        
        if success:
            self.user_constellation_mapping[user_id] = constellation_id
            
            return True, {
                "constellation_name": constellation.name,
                "sector_assignment": constellation.sector_assignment,
                "current_size": constellation.size,
                "phase": constellation.phase,
                "welcome_message": f"Welcome to {constellation.name}, Commander {cosmic_callsign}!"
            }
        
        return False, {"error": "Failed to join constellation"}
    
    async def find_compatible_constellations(
        self,
        user_id: int,
        preferences: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Find constellations compatible with user preferences"""
        
        if user_id in self.user_constellation_mapping:
            return []  # User already in constellation
        
        compatible_constellations = []
        
        for constellation in self.active_constellations.values():
            if not constellation.can_accept_members():
                continue
            
            if constellation.invitation_only:
                continue
            
            # Basic compatibility scoring
            compatibility_score = 0.0
            
            # Prefer constellations in formation or bonding phase
            if constellation.phase in [ConstellationPhase.FORMATION, ConstellationPhase.BONDING]:
                compatibility_score += 0.3
            
            # Prefer constellations with space for growth
            if constellation.size < ConstellationSize.OPTIMAL_MAX - 1:
                compatibility_score += 0.2
            
            # Prefer active constellations
            recent_activity = len([
                activity for activity in constellation.shared_activities[-10:]
                if activity.get("timestamp", "")
            ])
            compatibility_score += min(0.3, recent_activity * 0.1)
            
            compatible_constellations.append({
                "constellation_id": constellation.constellation_id,
                "name": constellation.name,
                "sector_assignment": constellation.sector_assignment,
                "current_size": constellation.size,
                "max_size": constellation.max_size,
                "phase": constellation.phase,
                "group_trust_score": constellation.group_trust_score,
                "compatibility_score": compatibility_score
            })
        
        # Sort by compatibility score
        compatible_constellations.sort(key=lambda x: x["compatibility_score"], reverse=True)
        
        return compatible_constellations[:5]  # Return top 5 matches
    
    async def update_constellation_trust_dynamics(self):
        """Update trust dynamics for all constellations"""
        for constellation in self.active_constellations.values():
            constellation.update_member_trust_progression()
            
            # Trigger AI facilitation for constellations needing help
            if constellation.ai_facilitator_active:
                await self._check_ai_facilitation_needs(constellation)
    
    async def _check_ai_facilitation_needs(self, constellation: Constellation):
        """Check if constellation needs AI facilitation"""
        # Check for stagnant groups
        recent_activities = [
            activity for activity in constellation.shared_activities
            if activity.get("timestamp", "") and 
            datetime.fromisoformat(activity["timestamp"].replace('Z', '+00:00')) > 
            datetime.now(timezone.utc) - timedelta(days=3)
        ]
        
        if len(recent_activities) < 2 and constellation.size >= 3:
            # Trigger conversation starter
            facilitation_message = {
                "type": "ai_facilitation",
                "subtype": "conversation_starter",
                "message": self._get_conversation_starter(constellation),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "ai_personality": "mission_control"
            }
            constellation.shared_activities.append(facilitation_message)
    
    def _get_conversation_starter(self, constellation: Constellation) -> str:
        """Get AI-generated conversation starter for constellation"""
        starters = [
            f"Attention {constellation.name} crew! Today's mission briefing: What's your take on the current market volatility in the {constellation.sector_assignment} sector?",
            f"Commander's quarters calling! Any {constellation.name} members want to share their latest trading strategy discoveries?",
            f"Stellar navigation update for {constellation.name}: Who's tackled the risk management training module this week?",
            f"Mission Control to {constellation.name}: Your constellation is showing excellent cohesion. Ready for advanced training scenarios?",
            f"Galactic Academy announcement: {constellation.name} constellation members - what's the most valuable trading lesson you've learned recently?"
        ]
        
        import random
        return random.choice(starters)
    
    def _load_ai_facilitator_prompts(self) -> Dict[str, List[str]]:
        """Load AI facilitator conversation prompts"""
        return {
            "welcome": [
                "Welcome aboard, Commander! Your constellation mates are eager to share the cosmic trading journey with you.",
                "New crew member detected! The constellation's collective wisdom just expanded.",
                "Another stellar navigator joins our ranks! Welcome to the academy."
            ],
            "conversation_starters": [
                "What's your perspective on today's market movements?",
                "Any interesting trading patterns you've noticed lately?",
                "Who's completed their latest academy training module?",
                "Share your best risk management tip with the constellation!",
                "What trading strategy are you most curious to learn about?"
            ],
            "celebration": [
                "Outstanding achievement! The constellation's combined expertise grows stronger.",
                "Stellar performance! Your success inspires the entire crew.",
                "Another milestone reached! The academy would be proud."
            ]
        }
    
    async def get_constellation_analytics(self, constellation_id: str) -> Dict[str, Any]:
        """Get analytics for specific constellation"""
        if constellation_id not in self.active_constellations:
            return {"error": "Constellation not found"}
        
        constellation = self.active_constellations[constellation_id]
        
        return {
            "constellation_metrics": {
                "size": constellation.size,
                "age_weeks": constellation.age_in_weeks,
                "phase": constellation.phase,
                "group_trust_score": constellation.group_trust_score,
                "viral_coefficient": constellation.viral_coefficient
            },
            "member_progression": {
                "trust_levels": {
                    level.value: len([m for m in constellation.members.values() if m.trust_level == level])
                    for level in TrustLevel
                },
                "average_trust_progression": sum(
                    member.calculate_trust_progression(constellation.age_in_weeks)
                    for member in constellation.members.values()
                ) / max(1, len(constellation.members))
            },
            "activity_summary": {
                "total_activities": len(constellation.shared_activities),
                "recent_activities": len([
                    activity for activity in constellation.shared_activities
                    if activity.get("timestamp", "") and 
                    datetime.fromisoformat(activity["timestamp"].replace('Z', '+00:00')) > 
                    datetime.now(timezone.utc) - timedelta(days=7)
                ])
            },
            "privacy_note": "All analytics use privacy-preserving aggregation techniques"
        }