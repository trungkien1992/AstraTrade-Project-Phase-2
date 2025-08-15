"""
Social Domain Entities

Core business entities for the Social Domain as defined in ADR-001.
These entities encapsulate essential business concepts and invariants for social interactions.

Domain Entities implemented:
- SocialProfile: User's social identity and community reputation (Aggregate Root)
- Constellation: User-created social groups and clans (Aggregate Root)
- ViralContent: Community-generated shareable content (Aggregate Root)
- SocialInteraction: User-to-user social actions and endorsements

Architecture follows DDD patterns with:
- Immutable creation after construction
- Business rule enforcement  
- Domain event emission
- Rich domain behavior (not anemic models)
"""

from datetime import datetime, timezone, timedelta
from decimal import Decimal
from enum import Enum
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from uuid import uuid4

from .value_objects import (
    SocialRating, InfluenceScore, SocialBadge, ConstellationInfo, ViralMetrics,
    PrestigeLevel, SocialInteractionContext, CommunityRole, VerificationTier,
    ContentType, ModerationStatus, SocialInteractionType
)
from ..shared.events import DomainEvent


class SocialProfileCreated(DomainEvent):
    """Event emitted when a new social profile is created"""
    def __init__(self, user_id: int, social_rating: float):
        super().__init__("social_profile_created", {
            "user_id": user_id,
            "initial_social_rating": social_rating,
            "created_at": datetime.now(timezone.utc).isoformat()
        })


class SocialRatingChanged(DomainEvent):
    """Event emitted when user's social rating changes significantly"""
    def __init__(self, user_id: int, old_rating: float, new_rating: float, reason: str):
        super().__init__("social_rating_changed", {
            "user_id": user_id,
            "old_rating": old_rating,
            "new_rating": new_rating,
            "change_amount": new_rating - old_rating,
            "reason": reason,
            "changed_at": datetime.now(timezone.utc).isoformat()
        })


class ConstellationCreated(DomainEvent):
    """Event emitted when a new constellation is created"""
    def __init__(self, constellation_id: int, owner_id: int, name: str):
        super().__init__("constellation_created", {
            "constellation_id": constellation_id,
            "owner_id": owner_id,
            "name": name,
            "created_at": datetime.now(timezone.utc).isoformat()
        })


class ConstellationMemberJoined(DomainEvent):
    """Event emitted when a user joins a constellation"""
    def __init__(self, constellation_id: int, user_id: int, role: str):
        super().__init__("constellation_member_joined", {
            "constellation_id": constellation_id,
            "user_id": user_id,
            "role": role,
            "joined_at": datetime.now(timezone.utc).isoformat()
        })


class ViralContentShared(DomainEvent):
    """Event emitted when viral content is shared"""
    def __init__(self, content_id: int, user_id: int, platform: str, viral_score: int):
        super().__init__("viral_content_shared", {
            "content_id": content_id,
            "user_id": user_id,
            "platform": platform,
            "viral_score": viral_score,
            "shared_at": datetime.now(timezone.utc).isoformat()
        })


class SocialInteractionPerformed(DomainEvent):
    """Event emitted when a social interaction occurs"""
    def __init__(self, source_user_id: int, target_user_id: int, interaction_type: str, impact_value: float):
        super().__init__("social_interaction_performed", {
            "source_user_id": source_user_id,
            "target_user_id": target_user_id,
            "interaction_type": interaction_type,
            "impact_value": impact_value,
            "performed_at": datetime.now(timezone.utc).isoformat()
        })


class SocialProfile:
    """
    Social Profile aggregate root representing a user's social identity and community standing.
    
    Encapsulates all social-related business logic including reputation management,
    prestige tracking, and community engagement.
    """
    
    def __init__(
        self,
        user_id: int,
        social_rating: SocialRating,
        influence_score: InfluenceScore,
        prestige_level: PrestigeLevel,
        constellation_info: Optional[ConstellationInfo] = None,
        created_at: Optional[datetime] = None
    ):
        if user_id <= 0:
            raise ValueError("User ID must be positive")
        
        self._user_id = user_id
        self._social_rating = social_rating
        self._influence_score = influence_score
        self._prestige_level = prestige_level
        self._constellation_info = constellation_info
        self._created_at = created_at or datetime.now(timezone.utc)
        self._updated_at = datetime.now(timezone.utc)
        self._domain_events: List[DomainEvent] = []
        
        # Emit profile creation event
        if created_at is None:  # Only for new profiles
            self._domain_events.append(
                SocialProfileCreated(self._user_id, self._social_rating.score)
            )
    
    @property
    def user_id(self) -> int:
        return self._user_id
    
    @property
    def social_rating(self) -> SocialRating:
        return self._social_rating
    
    @property
    def influence_score(self) -> InfluenceScore:
        return self._influence_score
    
    @property
    def prestige_level(self) -> PrestigeLevel:
        return self._prestige_level
    
    @property
    def constellation_info(self) -> Optional[ConstellationInfo]:
        return self._constellation_info
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        return self._updated_at
    
    @property
    def domain_events(self) -> List[DomainEvent]:
        return self._domain_events.copy()
    
    def clear_events(self):
        """Clear domain events after processing"""
        self._domain_events.clear()
    
    def receive_endorsement(self, endorser_influence: InfluenceScore) -> None:
        """
        Process an endorsement from another user.
        Updates social rating based on endorser's influence.
        """
        old_rating = self._social_rating.score
        
        # Calculate endorsement value based on endorser influence
        boost_factors = endorser_influence.calculate_boost_factors()
        endorsement_value = boost_factors["endorsement_value"]
        
        # Update social rating with weighted endorsement
        weighted_endorsement = self._social_rating.with_endorsement()
        boosted_score = min(
            weighted_endorsement.max_score,
            weighted_endorsement.score + (endorsement_value - 1.0) * 2.0
        )
        
        self._social_rating = SocialRating(
            score=boosted_score,
            max_score=weighted_endorsement.max_score,
            endorsement_count=weighted_endorsement.endorsement_count,
            negative_feedback=weighted_endorsement.negative_feedback
        )
        
        self._updated_at = datetime.now(timezone.utc)
        
        # Emit rating change event for significant changes
        if abs(boosted_score - old_rating) >= 1.0:
            self._domain_events.append(
                SocialRatingChanged(
                    self._user_id, old_rating, boosted_score, "endorsement_received"
                )
            )
    
    def receive_negative_feedback(self, reason: str) -> None:
        """
        Process negative feedback or report against the user.
        Applies penalty to social rating.
        """
        old_rating = self._social_rating.score
        self._social_rating = self._social_rating.with_negative_feedback()
        self._updated_at = datetime.now(timezone.utc)
        
        # Emit rating change event
        self._domain_events.append(
            SocialRatingChanged(
                self._user_id, old_rating, self._social_rating.score, 
                f"negative_feedback: {reason}"
            )
        )
    
    def join_constellation(self, constellation_info: ConstellationInfo) -> None:
        """Join a constellation/clan and update social profile"""
        if self._constellation_info is not None:
            raise ValueError("User is already a member of a constellation")
        
        self._constellation_info = constellation_info
        self._updated_at = datetime.now(timezone.utc)
        
        # Update influence score for constellation membership
        new_influence = InfluenceScore(
            score=self._influence_score.score + constellation_info.calculate_loyalty_bonus(),
            viral_content_count=self._influence_score.viral_content_count,
            constellation_leadership=constellation_info.is_leadership_role,
            community_contributions=self._influence_score.community_contributions,
            follower_count=self._influence_score.follower_count
        )
        self._influence_score = new_influence
        
        # Emit constellation joined event
        self._domain_events.append(
            ConstellationMemberJoined(
                constellation_info.constellation_id, self._user_id, constellation_info.role.value
            )
        )
    
    def leave_constellation(self) -> None:
        """Leave current constellation"""
        if self._constellation_info is None:
            raise ValueError("User is not a member of any constellation")
        
        # Reduce influence score
        loyalty_bonus = self._constellation_info.calculate_loyalty_bonus()
        new_influence = InfluenceScore(
            score=max(0, self._influence_score.score - loyalty_bonus),
            viral_content_count=self._influence_score.viral_content_count,
            constellation_leadership=False,
            community_contributions=self._influence_score.community_contributions,
            follower_count=self._influence_score.follower_count
        )
        self._influence_score = new_influence
        self._constellation_info = None
        self._updated_at = datetime.now(timezone.utc)
    
    def earn_badge(self, badge: SocialBadge) -> None:
        """Add a new social badge to the profile"""
        # Check if badge already exists
        existing_badges = [b.badge_id for b in self._prestige_level.badge_collection]
        if badge.badge_id in existing_badges:
            raise ValueError(f"Badge {badge.badge_id} is already earned")
        
        # Create new prestige level with added badge
        new_badges = self._prestige_level.badge_collection + [badge]
        self._prestige_level = PrestigeLevel(
            verification_tier=self._prestige_level.verification_tier,
            verification_date=self._prestige_level.verification_date,
            spotlight_count=self._prestige_level.spotlight_count,
            spotlight_votes=self._prestige_level.spotlight_votes,
            is_spotlight_eligible=self._prestige_level.is_spotlight_eligible,
            aura_color=self._prestige_level.aura_color,
            custom_title=self._prestige_level.custom_title,
            badge_collection=new_badges
        )
        
        # Update influence score for badge achievement
        badge_influence_boost = badge.rarity_points * 0.1
        new_influence = InfluenceScore(
            score=self._influence_score.score + badge_influence_boost,
            viral_content_count=self._influence_score.viral_content_count,
            constellation_leadership=self._influence_score.constellation_leadership,
            community_contributions=self._influence_score.community_contributions + 1,
            follower_count=self._influence_score.follower_count
        )
        self._influence_score = new_influence
        self._updated_at = datetime.now(timezone.utc)
    
    def update_verification(self, tier: VerificationTier) -> None:
        """Update user's verification tier"""
        if tier.value < self._prestige_level.verification_tier.value:
            raise ValueError("Cannot downgrade verification tier")
        
        verification_date = datetime.now(timezone.utc) if tier != VerificationTier.NONE else None
        
        self._prestige_level = PrestigeLevel(
            verification_tier=tier,
            verification_date=verification_date,
            spotlight_count=self._prestige_level.spotlight_count,
            spotlight_votes=self._prestige_level.spotlight_votes,
            is_spotlight_eligible=tier != VerificationTier.NONE,
            aura_color=self._prestige_level.aura_color,
            custom_title=self._prestige_level.custom_title,
            badge_collection=self._prestige_level.badge_collection
        )
        self._updated_at = datetime.now(timezone.utc)
    
    def calculate_overall_score(self) -> float:
        """Calculate comprehensive social score combining all factors"""
        rating_score = self._social_rating.score
        influence_score = min(self._influence_score.score / 10, 50)  # Cap at 50 points
        prestige_score = min(self._prestige_level.calculate_prestige_score() / 10, 30)  # Cap at 30 points
        constellation_bonus = 10 if self._constellation_info and self._constellation_info.is_leadership_role else 0
        
        return rating_score + influence_score + prestige_score + constellation_bonus


class Constellation:
    """
    Constellation aggregate root representing a user-created social group or clan.
    
    Manages clan membership, battles, resource sharing, and community activities.
    """
    
    def __init__(
        self,
        constellation_id: int,
        name: str,
        owner_id: int,
        description: Optional[str] = None,
        constellation_color: str = "#7B2CBF",
        constellation_emblem: str = "star",
        is_public: bool = True,
        max_members: int = 50,
        created_at: Optional[datetime] = None
    ):
        if constellation_id <= 0:
            raise ValueError("Constellation ID must be positive")
        if not name or len(name) < 3:
            raise ValueError("Constellation name must be at least 3 characters")
        if owner_id <= 0:
            raise ValueError("Owner ID must be positive")
        if max_members < 5 or max_members > 200:
            raise ValueError("Max members must be between 5 and 200")
        
        self._constellation_id = constellation_id
        self._name = name
        self._owner_id = owner_id
        self._description = description
        self._constellation_color = constellation_color
        self._constellation_emblem = constellation_emblem
        self._is_public = is_public
        self._max_members = max_members
        self._member_count = 1  # Owner is first member
        self._constellation_level = 1
        self._total_stellar_shards = Decimal('0')
        self._total_lumina = Decimal('0')
        self._total_battles = 0
        self._battles_won = 0
        self._battle_rating = Decimal('1000.0')
        self._created_at = created_at or datetime.now(timezone.utc)
        self._updated_at = datetime.now(timezone.utc)
        self._domain_events: List[DomainEvent] = []
        
        # Emit constellation creation event
        if created_at is None:  # Only for new constellations
            self._domain_events.append(
                ConstellationCreated(self._constellation_id, self._owner_id, self._name)
            )
    
    @property
    def constellation_id(self) -> int:
        return self._constellation_id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def owner_id(self) -> int:
        return self._owner_id
    
    @property
    def description(self) -> Optional[str]:
        return self._description
    
    @property
    def member_count(self) -> int:
        return self._member_count
    
    @property
    def max_members(self) -> int:
        return self._max_members
    
    @property
    def constellation_level(self) -> int:
        return self._constellation_level
    
    @property
    def total_stellar_shards(self) -> Decimal:
        return self._total_stellar_shards
    
    @property
    def total_lumina(self) -> Decimal:
        return self._total_lumina
    
    @property
    def battle_rating(self) -> Decimal:
        return self._battle_rating
    
    @property
    def win_rate(self) -> float:
        return self._battles_won / max(1, self._total_battles)
    
    @property
    def is_full(self) -> bool:
        return self._member_count >= self._max_members
    
    @property
    def domain_events(self) -> List[DomainEvent]:
        return self._domain_events.copy()
    
    def clear_events(self):
        """Clear domain events after processing"""
        self._domain_events.clear()
    
    def can_add_member(self) -> bool:
        """Check if constellation can accept new members"""
        return not self.is_full and self._is_public
    
    def add_member(self, user_id: int) -> None:
        """Add a new member to the constellation"""
        if not self.can_add_member():
            raise ValueError("Cannot add member: constellation is full or private")
        
        if user_id == self._owner_id:
            raise ValueError("Owner is already a member")
        
        self._member_count += 1
        self._updated_at = datetime.now(timezone.utc)
        
        # Emit member joined event
        self._domain_events.append(
            ConstellationMemberJoined(self._constellation_id, user_id, CommunityRole.MEMBER.value)
        )
    
    def remove_member(self, user_id: int) -> None:
        """Remove a member from the constellation"""
        if user_id == self._owner_id:
            raise ValueError("Cannot remove constellation owner")
        
        if self._member_count <= 1:
            raise ValueError("Cannot remove member from empty constellation")
        
        self._member_count -= 1
        self._updated_at = datetime.now(timezone.utc)
    
    def contribute_resources(self, stellar_shards: Decimal, lumina: Decimal) -> None:
        """Add resources to constellation treasury"""
        if stellar_shards < 0 or lumina < 0:
            raise ValueError("Resource contributions must be positive")
        
        self._total_stellar_shards += stellar_shards
        self._total_lumina += lumina
        self._updated_at = datetime.now(timezone.utc)
        
        # Check for level up based on total resources
        self._check_level_up()
    
    def _check_level_up(self) -> None:
        """Check if constellation should level up based on resources and activity"""
        total_resources = float(self._total_stellar_shards + self._total_lumina)
        required_resources = self._constellation_level * 10000  # Scaling requirement
        
        if total_resources >= required_resources and self._member_count >= self._constellation_level * 5:
            self._constellation_level += 1
            # Level up could trigger additional benefits/events
    
    def record_battle_result(self, won: bool, rating_change: Decimal) -> None:
        """Record the result of a constellation battle"""
        self._total_battles += 1
        if won:
            self._battles_won += 1
        
        # Update battle rating with ELO-like system
        self._battle_rating = max(Decimal('100'), self._battle_rating + rating_change)
        self._updated_at = datetime.now(timezone.utc)
    
    def update_settings(
        self, 
        description: Optional[str] = None,
        constellation_color: Optional[str] = None,
        constellation_emblem: Optional[str] = None,
        is_public: Optional[bool] = None,
        max_members: Optional[int] = None
    ) -> None:
        """Update constellation settings (owner only)"""
        if description is not None:
            self._description = description
        if constellation_color is not None:
            self._constellation_color = constellation_color
        if constellation_emblem is not None:
            self._constellation_emblem = constellation_emblem
        if is_public is not None:
            self._is_public = is_public
        if max_members is not None:
            if max_members < self._member_count:
                raise ValueError("Cannot set max members below current member count")
            self._max_members = max_members
        
        self._updated_at = datetime.now(timezone.utc)


class ViralContent:
    """
    Viral Content aggregate root representing community-generated shareable content.
    
    Manages content creation, sharing, engagement tracking, and virality scoring.
    """
    
    def __init__(
        self,
        content_id: int,
        user_id: int,
        content_type: ContentType,
        content_title: str,
        content_data: Dict[str, Any],
        content_description: Optional[str] = None,
        template_id: Optional[str] = None,
        is_public: bool = True,
        created_at: Optional[datetime] = None
    ):
        if content_id <= 0:
            raise ValueError("Content ID must be positive")
        if user_id <= 0:
            raise ValueError("User ID must be positive")
        if not content_title:
            raise ValueError("Content title cannot be empty")
        if not content_data:
            raise ValueError("Content data cannot be empty")
        
        self._content_id = content_id
        self._user_id = user_id
        self._content_type = content_type
        self._content_title = content_title
        self._content_description = content_description
        self._content_data = content_data.copy()
        self._template_id = template_id
        self._is_public = is_public
        self._is_featured = False
        self._moderation_status = ModerationStatus.APPROVED
        self._viral_metrics = ViralMetrics(
            share_count=0,
            viral_score=0,
            engagement_rate=0.0,
            platform_shares={}
        )
        self._trading_context: Optional[Dict[str, Any]] = None
        self._achievement_context: Optional[Dict[str, Any]] = None
        self._created_at = created_at or datetime.now(timezone.utc)
        self._last_shared_at = self._created_at
        self._domain_events: List[DomainEvent] = []
    
    @property
    def content_id(self) -> int:
        return self._content_id
    
    @property
    def user_id(self) -> int:
        return self._user_id
    
    @property
    def content_type(self) -> ContentType:
        return self._content_type
    
    @property
    def content_title(self) -> str:
        return self._content_title
    
    @property
    def content_data(self) -> Dict[str, Any]:
        return self._content_data.copy()
    
    @property
    def viral_metrics(self) -> ViralMetrics:
        return self._viral_metrics
    
    @property
    def is_featured(self) -> bool:
        return self._is_featured
    
    @property
    def moderation_status(self) -> ModerationStatus:
        return self._moderation_status
    
    @property
    def domain_events(self) -> List[DomainEvent]:
        return self._domain_events.copy()
    
    def clear_events(self):
        """Clear domain events after processing"""
        self._domain_events.clear()
    
    def share_to_platform(self, platform: str, reach_estimate: int = 0) -> None:
        """Record content being shared to a social platform"""
        if not platform:
            raise ValueError("Platform cannot be empty")
        
        # Update platform shares
        new_platform_shares = self._viral_metrics.platform_shares.copy()
        new_platform_shares[platform] = new_platform_shares.get(platform, 0) + 1
        
        # Calculate new viral score
        platform_multipliers = {
            "twitter": 2.0,
            "instagram": 1.5,
            "facebook": 1.2,
            "discord": 1.8,
            "reddit": 2.5,
            "telegram": 1.3
        }
        multiplier = platform_multipliers.get(platform.lower(), 1.0)
        score_increase = int(multiplier * (1 + reach_estimate / 1000))
        
        # Update viral metrics
        self._viral_metrics = ViralMetrics(
            share_count=self._viral_metrics.share_count + 1,
            viral_score=self._viral_metrics.viral_score + score_increase,
            engagement_rate=self._calculate_engagement_rate(),
            platform_shares=new_platform_shares,
            reach_estimate=max(self._viral_metrics.reach_estimate, reach_estimate)
        )
        
        self._last_shared_at = datetime.now(timezone.utc)
        
        # Emit viral content shared event
        self._domain_events.append(
            ViralContentShared(
                self._content_id, self._user_id, platform, self._viral_metrics.viral_score
            )
        )
    
    def _calculate_engagement_rate(self) -> float:
        """Calculate engagement rate based on shares and reach"""
        if self._viral_metrics.reach_estimate == 0:
            return min(self._viral_metrics.share_count * 0.1, 1.0)
        
        return min(self._viral_metrics.share_count / self._viral_metrics.reach_estimate, 1.0)
    
    def moderate_content(self, status: ModerationStatus, reason: Optional[str] = None) -> None:
        """Update content moderation status"""
        self._moderation_status = status
        
        if status == ModerationStatus.REJECTED:
            self._is_public = False
            self._is_featured = False
    
    def feature_content(self) -> None:
        """Mark content as featured (requires approved status)"""
        if self._moderation_status != ModerationStatus.APPROVED:
            raise ValueError("Cannot feature content that is not approved")
        
        self._is_featured = True
    
    def unfeature_content(self) -> None:
        """Remove featured status from content"""
        self._is_featured = False
    
    def add_trading_context(self, context: Dict[str, Any]) -> None:
        """Add trading-related context to the content"""
        self._trading_context = context.copy()
    
    def add_achievement_context(self, context: Dict[str, Any]) -> None:
        """Add achievement-related context to the content"""
        self._achievement_context = context.copy()
    
    def calculate_influence_contribution(self) -> float:
        """Calculate how much this content contributes to user's influence score"""
        return self._viral_metrics.calculate_influence_points()


class SocialInteraction:
    """
    Social Interaction entity representing user-to-user social actions.
    
    Handles endorsements, votes, follows, and other social interactions between users.
    """
    
    def __init__(
        self,
        interaction_id: int,
        source_user_id: int,
        target_user_id: int,
        interaction_context: SocialInteractionContext,
        source_influence: InfluenceScore,
        created_at: Optional[datetime] = None
    ):
        if interaction_id <= 0:
            raise ValueError("Interaction ID must be positive")
        if source_user_id <= 0:
            raise ValueError("Source user ID must be positive")
        if target_user_id <= 0:
            raise ValueError("Target user ID must be positive")
        if source_user_id == target_user_id:
            raise ValueError("Users cannot interact with themselves")
        
        self._interaction_id = interaction_id
        self._source_user_id = source_user_id
        self._target_user_id = target_user_id
        self._interaction_context = interaction_context
        self._impact_value = interaction_context.calculate_impact_value(source_influence)
        self._is_processed = False
        self._created_at = created_at or datetime.now(timezone.utc)
        self._processed_at: Optional[datetime] = None
        self._domain_events: List[DomainEvent] = []
        
        # Emit interaction performed event
        self._domain_events.append(
            SocialInteractionPerformed(
                self._source_user_id,
                self._target_user_id,
                self._interaction_context.interaction_type.value,
                self._impact_value
            )
        )
    
    @property
    def interaction_id(self) -> int:
        return self._interaction_id
    
    @property
    def source_user_id(self) -> int:
        return self._source_user_id
    
    @property
    def target_user_id(self) -> int:
        return self._target_user_id
    
    @property
    def interaction_context(self) -> SocialInteractionContext:
        return self._interaction_context
    
    @property
    def impact_value(self) -> float:
        return self._impact_value
    
    @property
    def is_processed(self) -> bool:
        return self._is_processed
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def processed_at(self) -> Optional[datetime]:
        return self._processed_at
    
    @property
    def domain_events(self) -> List[DomainEvent]:
        return self._domain_events.copy()
    
    def clear_events(self):
        """Clear domain events after processing"""
        self._domain_events.clear()
    
    def mark_processed(self) -> None:
        """Mark the interaction as processed"""
        if self._is_processed:
            raise ValueError("Interaction is already processed")
        
        self._is_processed = True
        self._processed_at = datetime.now(timezone.utc)
    
    def is_valid_interaction(self) -> bool:
        """Validate if the interaction should be processed"""
        # Check for spam (too many interactions in short time)
        recent_threshold = datetime.now(timezone.utc) - timedelta(minutes=1)
        if self._created_at > recent_threshold:
            # Additional validation could be implemented here
            pass
        
        return True