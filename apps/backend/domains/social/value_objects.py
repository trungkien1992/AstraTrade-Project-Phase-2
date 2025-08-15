"""
Social Domain Value Objects

Immutable value objects representing social concepts in the AstraTrade platform.
These objects encapsulate business rules and provide type safety for social features.

Value objects implemented:
- SocialRating: User's community reputation score
- InfluenceScore: Measure of user's community impact  
- CommunityRole: User's role within social groups
- SocialBadge: Earned social recognition and achievements
- ConstellationInfo: Basic constellation/clan information
- ViralMetrics: Content sharing and engagement statistics
- SocialInteractionType: Types of social interactions
- PrestigeLevel: User prestige and verification status
"""

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field


class CommunityRole(Enum):
    """Roles within social groups and constellations"""
    MEMBER = "member"
    MODERATOR = "moderator"
    ADMIN = "admin"
    OWNER = "owner"


class VerificationTier(Enum):
    """User verification levels"""
    NONE = 0
    BRONZE = 1
    SILVER = 2
    GOLD = 3


class SocialInteractionType(Enum):
    """Types of social interactions between users"""
    ENDORSEMENT = "endorsement"
    VOTE = "vote"
    FOLLOW = "follow"
    UNFOLLOW = "unfollow"
    BLOCK = "block"
    REPORT = "report"
    RECOMMEND = "recommend"


class ContentType(Enum):
    """Types of viral content"""
    MEME = "meme"
    SNAPSHOT = "snapshot"
    ACHIEVEMENT = "achievement"
    NFT_SHOWCASE = "nft_showcase"
    TRADING_WIN = "trading_win"
    MILESTONE = "milestone"


class ModerationStatus(Enum):
    """Content moderation status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    FLAGGED = "flagged"


@dataclass(frozen=True)
class SocialRating:
    """
    User's social reputation score within the community.
    Calculated based on endorsements, contributions, and community engagement.
    """
    score: float
    max_score: float = 100.0
    endorsement_count: int = 0
    negative_feedback: int = 0
    
    def __post_init__(self):
        if self.score < 0 or self.score > self.max_score:
            raise ValueError(f"Social rating must be between 0 and {self.max_score}")
        if self.endorsement_count < 0:
            raise ValueError("Endorsement count cannot be negative")
        if self.negative_feedback < 0:
            raise ValueError("Negative feedback count cannot be negative")
    
    @property
    def percentage(self) -> float:
        """Social rating as percentage of maximum"""
        return (self.score / self.max_score) * 100
    
    @property
    def reputation_level(self) -> str:
        """Categorical reputation level"""
        if self.score >= 90:
            return "Legendary"
        elif self.score >= 75:
            return "Renowned"
        elif self.score >= 50:
            return "Respected"
        elif self.score >= 25:
            return "Emerging"
        else:
            return "Newcomer"
    
    def with_endorsement(self) -> 'SocialRating':
        """Create new rating with additional endorsement"""
        boost = min(2.0, 10.0 / max(1, self.endorsement_count))  # Diminishing returns
        new_score = min(self.max_score, self.score + boost)
        return SocialRating(
            score=new_score,
            max_score=self.max_score,
            endorsement_count=self.endorsement_count + 1,
            negative_feedback=self.negative_feedback
        )
    
    def with_negative_feedback(self) -> 'SocialRating':
        """Create new rating with negative feedback penalty"""
        penalty = min(5.0, self.score * 0.1)  # Max 10% penalty
        new_score = max(0.0, self.score - penalty)
        return SocialRating(
            score=new_score,
            max_score=self.max_score,
            endorsement_count=self.endorsement_count,
            negative_feedback=self.negative_feedback + 1
        )


@dataclass(frozen=True)
class InfluenceScore:
    """
    Measure of user's impact and influence within the community.
    Based on viral content, constellation leadership, and community contributions.
    """
    score: float
    viral_content_count: int = 0
    constellation_leadership: bool = False
    community_contributions: int = 0
    follower_count: int = 0
    
    def __post_init__(self):
        if self.score < 0:
            raise ValueError("Influence score cannot be negative")
        if self.viral_content_count < 0:
            raise ValueError("Viral content count cannot be negative")
        if self.community_contributions < 0:
            raise ValueError("Community contributions cannot be negative")
        if self.follower_count < 0:
            raise ValueError("Follower count cannot be negative")
    
    @property
    def influence_tier(self) -> str:
        """Categorical influence tier"""
        if self.score >= 1000:
            return "Cosmic Influencer"
        elif self.score >= 500:
            return "Stellar Leader"
        elif self.score >= 200:
            return "Community Guide"
        elif self.score >= 50:
            return "Rising Voice"
        else:
            return "New Member"
    
    def calculate_boost_factors(self) -> Dict[str, float]:
        """Calculate influence boost factors for various activities"""
        base_multiplier = 1.0
        
        # Leadership bonus
        if self.constellation_leadership:
            base_multiplier *= 1.5
        
        # Viral content creator bonus
        if self.viral_content_count >= 10:
            base_multiplier *= 1.3
        elif self.viral_content_count >= 5:
            base_multiplier *= 1.2
        
        # Community contributor bonus
        if self.community_contributions >= 50:
            base_multiplier *= 1.4
        elif self.community_contributions >= 20:
            base_multiplier *= 1.2
        
        return {
            "endorsement_value": base_multiplier,
            "viral_content_boost": base_multiplier * 0.1,
            "community_weight": base_multiplier * 0.2
        }


@dataclass(frozen=True)
class SocialBadge:
    """
    Social recognition and achievement badges.
    Represents accomplishments in community engagement and social activities.
    """
    badge_id: str
    name: str
    description: str
    earned_at: datetime
    rarity: str  # common, rare, epic, legendary
    category: str  # social, leadership, content, community
    
    def __post_init__(self):
        if not self.badge_id:
            raise ValueError("Badge ID cannot be empty")
        if not self.name:
            raise ValueError("Badge name cannot be empty")
        if self.rarity not in ["common", "rare", "epic", "legendary"]:
            raise ValueError("Invalid badge rarity")
        if self.category not in ["social", "leadership", "content", "community"]:
            raise ValueError("Invalid badge category")
    
    @property
    def rarity_points(self) -> int:
        """Point value based on badge rarity"""
        rarity_values = {
            "common": 10,
            "rare": 25,
            "epic": 50,
            "legendary": 100
        }
        return rarity_values[self.rarity]
    
    def is_expired(self, expiry_months: Optional[int] = None) -> bool:
        """Check if badge has expired (for time-limited badges)"""
        if expiry_months is None:
            return False
        
        expiry_date = self.earned_at.replace(
            month=self.earned_at.month + expiry_months
        )
        return datetime.now() > expiry_date


@dataclass(frozen=True)
class ConstellationInfo:
    """
    Basic constellation/clan information for social profiles.
    Contains essential details about user's clan membership.
    """
    constellation_id: int
    name: str
    role: CommunityRole
    member_since: datetime
    contribution_score: int = 0
    
    def __post_init__(self):
        if self.constellation_id <= 0:
            raise ValueError("Constellation ID must be positive")
        if not self.name:
            raise ValueError("Constellation name cannot be empty")
        if self.contribution_score < 0:
            raise ValueError("Contribution score cannot be negative")
    
    @property
    def membership_duration_days(self) -> int:
        """Days since joining the constellation"""
        return (datetime.now(timezone.utc) - self.member_since).days
    
    @property
    def is_leadership_role(self) -> bool:
        """Check if user has leadership role in constellation"""
        return self.role in [CommunityRole.OWNER, CommunityRole.ADMIN, CommunityRole.MODERATOR]
    
    def calculate_loyalty_bonus(self) -> float:
        """Calculate loyalty bonus based on membership duration and contribution"""
        days = self.membership_duration_days
        base_bonus = min(days / 30, 12)  # Max 12 months bonus
        contribution_bonus = min(self.contribution_score / 100, 5)  # Max 5 points
        role_bonus = 2 if self.is_leadership_role else 0
        
        return base_bonus + contribution_bonus + role_bonus


@dataclass(frozen=True)
class ViralMetrics:
    """
    Content sharing and engagement statistics.
    Tracks viral performance and community engagement for user content.
    """
    share_count: int
    viral_score: int
    engagement_rate: float
    platform_shares: Dict[str, int]
    reach_estimate: int = 0
    
    def __post_init__(self):
        if self.share_count < 0:
            raise ValueError("Share count cannot be negative")
        if self.viral_score < 0:
            raise ValueError("Viral score cannot be negative")
        if not (0 <= self.engagement_rate <= 1):
            raise ValueError("Engagement rate must be between 0 and 1")
        if self.reach_estimate < 0:
            raise ValueError("Reach estimate cannot be negative")
    
    @property
    def total_platform_shares(self) -> int:
        """Total shares across all platforms"""
        return sum(self.platform_shares.values())
    
    @property
    def virality_tier(self) -> str:
        """Categorical virality level"""
        if self.viral_score >= 1000:
            return "Cosmic Viral"
        elif self.viral_score >= 500:
            return "Stellar Hit"
        elif self.viral_score >= 100:
            return "Popular"
        elif self.viral_score >= 25:
            return "Trending"
        else:
            return "Emerging"
    
    def calculate_influence_points(self) -> float:
        """Calculate influence points earned from viral content"""
        base_points = self.viral_score * 0.1
        engagement_bonus = self.engagement_rate * 50
        reach_bonus = min(self.reach_estimate / 1000, 100)  # Max 100 points from reach
        
        return base_points + engagement_bonus + reach_bonus


@dataclass(frozen=True)
class PrestigeLevel:
    """
    User prestige and verification status.
    Represents user's standing and recognition within the community.
    """
    verification_tier: VerificationTier
    verification_date: Optional[datetime] = None
    spotlight_count: int = 0
    spotlight_votes: int = 0
    is_spotlight_eligible: bool = False
    aura_color: str = "#FFFFFF"
    custom_title: Optional[str] = None
    badge_collection: List[SocialBadge] = field(default_factory=list)
    
    def __post_init__(self):
        if self.spotlight_count < 0:
            raise ValueError("Spotlight count cannot be negative")
        if self.spotlight_votes < 0:
            raise ValueError("Spotlight votes cannot be negative")
        if not self.aura_color.startswith("#") or len(self.aura_color) != 7:
            raise ValueError("Aura color must be valid hex color")
        if self.custom_title and len(self.custom_title) > 100:
            raise ValueError("Custom title cannot exceed 100 characters")
    
    @property
    def is_verified(self) -> bool:
        """Check if user has any verification level"""
        return self.verification_tier != VerificationTier.NONE
    
    @property
    def verification_name(self) -> str:
        """Human-readable verification level"""
        names = {
            VerificationTier.NONE: "Unverified",
            VerificationTier.BRONZE: "Bronze Verified",
            VerificationTier.SILVER: "Silver Verified",
            VerificationTier.GOLD: "Gold Verified"
        }
        return names[self.verification_tier]
    
    @property
    def total_badge_points(self) -> int:
        """Total points from all earned badges"""
        return sum(badge.rarity_points for badge in self.badge_collection)
    
    def get_badges_by_category(self, category: str) -> List[SocialBadge]:
        """Get badges filtered by category"""
        return [badge for badge in self.badge_collection if badge.category == category]
    
    def calculate_prestige_score(self) -> float:
        """Calculate overall prestige score"""
        verification_points = self.verification_tier.value * 25
        spotlight_points = self.spotlight_count * 10
        vote_points = min(self.spotlight_votes, 500)  # Max 500 points from votes
        badge_points = self.total_badge_points
        
        return verification_points + spotlight_points + vote_points + badge_points


@dataclass(frozen=True)
class SocialInteractionContext:
    """
    Context information for social interactions.
    Provides additional data about the circumstances of social actions.
    """
    interaction_type: SocialInteractionType
    target_user_id: int
    context_data: Dict[str, Any] = field(default_factory=dict)
    interaction_weight: float = 1.0
    requires_verification: bool = False
    
    def __post_init__(self):
        if self.target_user_id <= 0:
            raise ValueError("Target user ID must be positive")
        if not (0.1 <= self.interaction_weight <= 5.0):
            raise ValueError("Interaction weight must be between 0.1 and 5.0")
    
    @property
    def is_positive_interaction(self) -> bool:
        """Check if interaction is positive (builds reputation)"""
        positive_types = {
            SocialInteractionType.ENDORSEMENT,
            SocialInteractionType.VOTE,
            SocialInteractionType.FOLLOW,
            SocialInteractionType.RECOMMEND
        }
        return self.interaction_type in positive_types
    
    def calculate_impact_value(self, source_influence: InfluenceScore) -> float:
        """Calculate the impact value of this interaction"""
        base_impact = self.interaction_weight
        
        # Influence-based multiplier
        influence_multiplier = 1.0 + (source_influence.score / 1000)
        
        # Verification requirement penalty
        verification_penalty = 0.5 if self.requires_verification else 1.0
        
        # Positive/negative interaction modifier
        sentiment_modifier = 1.0 if self.is_positive_interaction else -0.5
        
        return base_impact * influence_multiplier * verification_penalty * sentiment_modifier