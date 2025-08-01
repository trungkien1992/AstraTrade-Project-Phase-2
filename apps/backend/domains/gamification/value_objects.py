from decimal import Decimal
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class XPSource(Enum):
    """Sources of XP in the AstraTrade ecosystem"""
    TRADING = "trading"
    SOCIAL = "social"
    VAULT_DEPOSIT = "vault_deposit"
    ACHIEVEMENT = "achievement"
    BATTLE_PARTICIPATION = "battle_participation"
    STREAK_BONUS = "streak_bonus"
    REFERRAL = "referral"


class AchievementType(Enum):
    """Types of achievements in the gamification system"""
    TRADING_MILESTONE = "trading_milestone"
    PROFIT_THRESHOLD = "profit_threshold"
    STREAK_ACHIEVEMENT = "streak_achievement"
    SOCIAL_ACHIEVEMENT = "social_achievement"
    CONSTELLATION_ACHIEVEMENT = "constellation_achievement"
    VAULT_ACHIEVEMENT = "vault_achievement"
    RARE_EVENT = "rare_event"


class BadgeRarity(Enum):
    """Rarity levels for achievement badges"""
    COMMON = "common"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"


class ConstellationRole(Enum):
    """Roles within a constellation"""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    RECRUIT = "recruit"


@dataclass(frozen=True)
class ExperiencePoints:
    """Value object representing XP with source tracking"""
    amount: Decimal
    source: XPSource
    multiplier: Decimal = Decimal('1.0')
    bonus_description: Optional[str] = None
    
    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("XP amount cannot be negative")
        if self.multiplier < 0:
            raise ValueError("XP multiplier cannot be negative")
    
    @property
    def total_xp(self) -> Decimal:
        """Calculate total XP including multiplier"""
        return self.amount * self.multiplier
    
    @classmethod
    def trading_xp(cls, trade_volume: Decimal, profit_loss: Decimal) -> 'ExperiencePoints':
        """Calculate XP from trading activity"""
        base_xp = trade_volume * Decimal('0.1')  # 0.1 XP per dollar volume
        profit_bonus = max(profit_loss * Decimal('0.5'), Decimal('0'))  # Bonus for profitable trades
        return cls(
            amount=base_xp + profit_bonus,
            source=XPSource.TRADING,
            bonus_description=f"Profit bonus: {profit_bonus}" if profit_bonus > 0 else None
        )
    
    @classmethod
    def social_xp(cls, activity_type: str, engagement_score: Decimal) -> 'ExperiencePoints':
        """Calculate XP from social activities"""
        base_xp = engagement_score * Decimal('2.0')  # 2 XP per engagement point
        return cls(
            amount=base_xp,
            source=XPSource.SOCIAL,
            bonus_description=f"Social activity: {activity_type}"
        )


@dataclass(frozen=True)
class AchievementBadge:
    """Value object representing an achievement badge"""
    achievement_type: AchievementType
    name: str
    description: str
    rarity: BadgeRarity
    xp_reward: Decimal
    currency_reward: Dict[str, Decimal]  # {'stellar_shards': 100, 'lumina': 50}
    unlock_conditions: Dict[str, Any]
    icon_id: str
    
    def __post_init__(self):
        if self.xp_reward < 0:
            raise ValueError("XP reward cannot be negative")
        for currency, amount in self.currency_reward.items():
            if amount < 0:
                raise ValueError(f"Currency reward for {currency} cannot be negative")
    
    @property
    def rarity_multiplier(self) -> Decimal:
        """Get XP multiplier based on badge rarity"""
        multipliers = {
            BadgeRarity.COMMON: Decimal('1.0'),
            BadgeRarity.RARE: Decimal('1.5'),
            BadgeRarity.EPIC: Decimal('2.0'),
            BadgeRarity.LEGENDARY: Decimal('3.0'),
            BadgeRarity.MYTHIC: Decimal('5.0')
        }
        return multipliers[self.rarity]
    
    @property
    def total_xp_reward(self) -> Decimal:
        """Calculate total XP reward including rarity multiplier"""
        return self.xp_reward * self.rarity_multiplier
    
    @classmethod
    def trading_milestone(cls, trade_count: int) -> 'AchievementBadge':
        """Create a trading milestone achievement"""
        milestones = {
            10: ("First Steps", BadgeRarity.COMMON, Decimal('50')),
            100: ("Seasoned Trader", BadgeRarity.RARE, Decimal('200')),
            1000: ("Trading Master", BadgeRarity.EPIC, Decimal('500')),
            10000: ("Market Legend", BadgeRarity.LEGENDARY, Decimal('2000'))
        }
        
        if trade_count not in milestones:
            raise ValueError(f"Invalid trade count for milestone: {trade_count}")
        
        name, rarity, xp = milestones[trade_count]
        return cls(
            achievement_type=AchievementType.TRADING_MILESTONE,
            name=name,
            description=f"Complete {trade_count:,} trades",
            rarity=rarity,
            xp_reward=xp,
            currency_reward={'stellar_shards': xp * Decimal('2')},
            unlock_conditions={'trade_count': trade_count},
            icon_id=f"trading_milestone_{trade_count}"
        )


@dataclass(frozen=True)
class ConstellationRank:
    """Value object representing a user's rank within a constellation"""
    role: ConstellationRole
    contribution_score: Decimal
    stellar_shards_contributed: Decimal
    lumina_contributed: Decimal
    battles_participated: int
    authority_level: int  # 0-100, determines permissions
    
    def __post_init__(self):
        if self.contribution_score < 0:
            raise ValueError("Contribution score cannot be negative")
        if self.stellar_shards_contributed < 0:
            raise ValueError("Stellar shards contributed cannot be negative")
        if self.lumina_contributed < 0:
            raise ValueError("Lumina contributed cannot be negative")
        if self.battles_participated < 0:
            raise ValueError("Battles participated cannot be negative")
        if not 0 <= self.authority_level <= 100:
            raise ValueError("Authority level must be between 0 and 100")
    
    @property
    def total_contribution_value(self) -> Decimal:
        """Calculate total contribution value in stellar shards equivalent"""
        lumina_to_shards_rate = Decimal('10.0')  # 1 lumina = 10 stellar shards
        return self.stellar_shards_contributed + (self.lumina_contributed * lumina_to_shards_rate)
    
    @property
    def can_invite_members(self) -> bool:
        """Check if this rank can invite new members"""
        # RECRUITs cannot invite regardless of authority level
        if self.role == ConstellationRole.RECRUIT:
            return False
        return self.role in [ConstellationRole.OWNER, ConstellationRole.ADMIN] or self.authority_level >= 50
    
    @property
    def can_start_battles(self) -> bool:
        """Check if this rank can initiate constellation battles"""
        # RECRUITs cannot start battles regardless of authority level
        if self.role == ConstellationRole.RECRUIT:
            return False
        return self.role in [ConstellationRole.OWNER, ConstellationRole.ADMIN] or self.authority_level >= 75
    
    @classmethod
    def new_member(cls) -> 'ConstellationRank':
        """Create a new member rank"""
        return cls(
            role=ConstellationRole.RECRUIT,
            contribution_score=Decimal('0'),
            stellar_shards_contributed=Decimal('0'),
            lumina_contributed=Decimal('0'),
            battles_participated=0,
            authority_level=10
        )


@dataclass(frozen=True)
class SocialMetrics:
    """Value object representing social engagement metrics"""
    viral_score: Decimal
    influence_rating: Decimal
    engagement_rate: Decimal
    share_count: int
    like_count: int
    comment_count: int
    follower_count: int
    
    def __post_init__(self):
        if self.viral_score < 0:
            raise ValueError("Viral score cannot be negative")
        if self.influence_rating < 0:
            raise ValueError("Influence rating cannot be negative")
        if not 0 <= self.engagement_rate <= 1:
            raise ValueError("Engagement rate must be between 0 and 1")
        if any(count < 0 for count in [self.share_count, self.like_count, self.comment_count, self.follower_count]):
            raise ValueError("Social counts cannot be negative")
    
    @property
    def total_engagement(self) -> int:
        """Calculate total engagement across all metrics"""
        return self.share_count + self.like_count + self.comment_count
    
    @property
    def virality_tier(self) -> str:
        """Determine virality tier based on viral score"""
        if self.viral_score >= 10000:
            return "Cosmic Influencer"
        elif self.viral_score >= 5000:
            return "Stellar Creator"
        elif self.viral_score >= 1000:
            return "Rising Star"
        elif self.viral_score >= 100:
            return "Active Member"
        else:
            return "New Trader"
    
    def calculate_social_xp(self) -> ExperiencePoints:
        """Calculate XP earned from social metrics"""
        base_xp = (self.viral_score * Decimal('0.1')) + (self.influence_rating * Decimal('0.5'))
        engagement_bonus = Decimal(str(self.total_engagement)) * Decimal('0.2')
        
        return ExperiencePoints(
            amount=base_xp + engagement_bonus,
            source=XPSource.SOCIAL,
            multiplier=Decimal('1.0') + (self.engagement_rate * Decimal('0.5')),
            bonus_description=f"Engagement bonus: {engagement_bonus}"
        )


@dataclass(frozen=True)
class RewardPackage:
    """Value object representing a complete reward package"""
    xp_reward: Decimal
    stellar_shards: Decimal
    lumina: Decimal
    stardust: Decimal
    badges: List[AchievementBadge]
    nft_artifacts: List[str]  # List of artifact IDs
    special_items: Dict[str, Any]
    reward_description: str
    
    def __post_init__(self):
        currencies = [self.xp_reward, self.stellar_shards, self.lumina, self.stardust]
        if any(amount < 0 for amount in currencies):
            raise ValueError("Reward amounts cannot be negative")
    
    @property
    def total_currency_value(self) -> Decimal:
        """Calculate total value in stellar shards equivalent"""
        lumina_rate = Decimal('10.0')  # 1 lumina = 10 stellar shards
        stardust_rate = Decimal('100.0')  # 1 stardust = 100 stellar shards
        
        return (
            self.stellar_shards +
            (self.lumina * lumina_rate) +
            (self.stardust * stardust_rate)
        )
    
    @property
    def has_rare_rewards(self) -> bool:
        """Check if package contains rare or better rewards"""
        rare_badges = any(badge.rarity in [BadgeRarity.RARE, BadgeRarity.EPIC, BadgeRarity.LEGENDARY, BadgeRarity.MYTHIC] 
                         for badge in self.badges)
        return rare_badges or len(self.nft_artifacts) > 0 or self.stardust > 0
    
    @classmethod
    def achievement_reward(cls, badge: AchievementBadge) -> 'RewardPackage':
        """Create a reward package for an achievement"""
        return cls(
            xp_reward=badge.total_xp_reward,
            stellar_shards=badge.currency_reward.get('stellar_shards', Decimal('0')),
            lumina=badge.currency_reward.get('lumina', Decimal('0')),
            stardust=badge.currency_reward.get('stardust', Decimal('0')),
            badges=[badge],
            nft_artifacts=[],
            special_items={},
            reward_description=f"Achievement reward: {badge.name}"
        )
    
    @classmethod
    def battle_victory_reward(cls, battle_score: Decimal, participation_count: int) -> 'RewardPackage':
        """Create a reward package for constellation battle victory"""
        base_shards = battle_score * Decimal('10')
        participation_bonus = Decimal(str(participation_count)) * Decimal('50')
        
        return cls(
            xp_reward=battle_score * Decimal('5'),
            stellar_shards=base_shards + participation_bonus,
            lumina=battle_score * Decimal('0.1'),
            stardust=Decimal('1') if battle_score > 1000 else Decimal('0'),
            badges=[],
            nft_artifacts=[],
            special_items={'battle_victory_token': True},
            reward_description=f"Battle victory reward (Score: {battle_score})"
        )