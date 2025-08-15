"""
Standardized Event Schemas

JSON schemas and Pydantic models for cross-domain event contracts.
Ensures type safety and consistency across all domain events.
"""

from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Any, Union
from enum import Enum

from pydantic import BaseModel, Field, validator
from pydantic.dataclasses import dataclass


class EventVersion(str, Enum):
    """Event schema versions for backward compatibility"""
    V1 = "1.0"
    V2 = "2.0"


class DomainType(str, Enum):
    """Domain types for event routing"""
    TRADING = "trading"
    GAMIFICATION = "gamification"
    SOCIAL = "social"
    FINANCIAL = "financial"
    NFT = "nft"
    USER = "user"


@dataclass
class EventMetadata:
    """Standard metadata for all events"""
    event_id: str
    event_type: str
    event_version: str = EventVersion.V1
    domain: DomainType
    occurred_at: datetime
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None


# Trading Domain Events

class TradeExecutedEvent(BaseModel):
    """Event emitted when a trade is executed"""
    metadata: EventMetadata
    trade_id: str
    user_id: int
    asset_symbol: str
    direction: str  # "buy" or "sell"
    amount: Decimal
    entry_price: Decimal
    executed_at: datetime
    pnl_usd: Optional[Decimal] = None
    
    class Config:
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }


class TradingRewardsCalculatedEvent(BaseModel):
    """Event emitted when trading rewards are calculated"""
    metadata: EventMetadata
    user_id: int
    trade_id: str
    xp_gained: int
    achievements_unlocked: List[str] = Field(default_factory=list)
    bonus_items: List[Dict[str, Any]] = Field(default_factory=list)
    reward_reason: str
    

class ClanBattleScoreUpdatedEvent(BaseModel):
    """Event emitted when clan battle scores are updated"""
    metadata: EventMetadata
    battle_id: int
    user_id: int
    trading_score: Decimal
    trade_count: int
    pnl_usd: Decimal
    
    class Config:
        json_encoders = {Decimal: str}


# Gamification Domain Events

class XPAwardedEvent(BaseModel):
    """Event emitted when XP is awarded to a user"""
    metadata: EventMetadata
    user_id: int
    xp_amount: int
    xp_source: str  # "trade", "achievement", "social", etc.
    source_id: Optional[str] = None  # ID of the source (trade_id, achievement_id, etc.)
    multiplier: Decimal = Decimal("1.0")
    
    class Config:
        json_encoders = {Decimal: str}


class LevelUpEvent(BaseModel):
    """Event emitted when user levels up"""
    metadata: EventMetadata
    user_id: int
    old_level: int
    new_level: int
    total_xp: int
    rewards_unlocked: List[Dict[str, Any]] = Field(default_factory=list)


class AchievementUnlockedEvent(BaseModel):
    """Event emitted when user unlocks an achievement"""
    metadata: EventMetadata
    user_id: int
    achievement_id: str
    achievement_name: str
    achievement_tier: str
    xp_reward: int
    badge_rarity: str


class StreakUpdatedEvent(BaseModel):
    """Event emitted when user's streak is updated"""
    metadata: EventMetadata
    user_id: int
    streak_type: str  # "trading", "login", "social"
    current_streak: int
    best_streak: int
    streak_action: str  # "continued", "broken", "started"


# Social Domain Events

class SocialProfileCreatedEvent(BaseModel):
    """Event emitted when a social profile is created"""
    metadata: EventMetadata
    user_id: int
    initial_social_rating: float
    profile_tier: str = "novice"


class SocialRatingChangedEvent(BaseModel):
    """Event emitted when user's social rating changes"""
    metadata: EventMetadata
    user_id: int
    old_rating: float
    new_rating: float
    change_amount: float
    reason: str
    source_user_id: Optional[int] = None


class ConstellationCreatedEvent(BaseModel):
    """Event emitted when a constellation is created"""
    metadata: EventMetadata
    constellation_id: int
    owner_id: int
    name: str
    constellation_type: str = "public"
    max_members: int = 50


class ConstellationMemberJoinedEvent(BaseModel):
    """Event emitted when user joins a constellation"""
    metadata: EventMetadata
    constellation_id: int
    user_id: int
    role: str
    invited_by: Optional[int] = None


class ViralContentSharedEvent(BaseModel):
    """Event emitted when viral content is shared"""
    metadata: EventMetadata
    content_id: int
    user_id: int
    platform: str
    viral_score: int
    content_type: str


class SocialInteractionPerformedEvent(BaseModel):
    """Event emitted when social interaction occurs"""
    metadata: EventMetadata
    source_user_id: int
    target_user_id: int
    interaction_type: str  # "endorsement", "follow", "challenge", etc.
    impact_value: float
    constellation_context: Optional[int] = None


# Financial Domain Events

class AccountCreatedEvent(BaseModel):
    """Event emitted when financial account is created"""
    metadata: EventMetadata
    account_id: str
    user_id: int
    initial_balance: Decimal
    currency: str
    
    class Config:
        json_encoders = {Decimal: str}


class FundsAddedEvent(BaseModel):
    """Event emitted when funds are added to account"""
    metadata: EventMetadata
    account_id: str
    user_id: int
    amount: Decimal
    new_balance: Decimal
    transaction_id: str
    source: str  # "deposit", "reward", "refund", etc.
    
    class Config:
        json_encoders = {Decimal: str}


class PaymentProcessedEvent(BaseModel):
    """Event emitted when payment is processed"""
    metadata: EventMetadata
    payment_id: str
    user_id: int
    amount: Decimal
    currency: str
    payment_method: str
    status: str  # "success", "failed", "pending"
    subscription_tier: Optional[str] = None
    
    class Config:
        json_encoders = {Decimal: str}


# NFT Domain Events

class NFTMintedEvent(BaseModel):
    """Event emitted when NFT is minted"""
    metadata: EventMetadata
    nft_id: str
    user_id: int
    collection_id: str
    token_uri: str
    rarity: str
    mint_cost: Optional[Decimal] = None
    
    class Config:
        json_encoders = {Decimal: str}


class NFTTradedEvent(BaseModel):
    """Event emitted when NFT is traded"""
    metadata: EventMetadata
    nft_id: str
    from_user_id: int
    to_user_id: int
    price: Decimal
    currency: str
    transaction_hash: Optional[str] = None
    
    class Config:
        json_encoders = {Decimal: str}


class NFTStakedEvent(BaseModel):
    """Event emitted when NFT is staked"""
    metadata: EventMetadata
    nft_id: str
    user_id: int
    stake_pool_id: str
    staked_at: datetime
    expected_rewards: Dict[str, Any] = Field(default_factory=dict)


# User Domain Events

class UserRegisteredEvent(BaseModel):
    """Event emitted when user registers"""
    metadata: EventMetadata
    user_id: int
    email: str
    registration_source: str  # "web", "mobile", "referral"
    referrer_id: Optional[int] = None


class UserProfileUpdatedEvent(BaseModel):
    """Event emitted when user profile is updated"""
    metadata: EventMetadata
    user_id: int
    updated_fields: List[str]
    old_values: Dict[str, Any] = Field(default_factory=dict)
    new_values: Dict[str, Any] = Field(default_factory=dict)


class UserPreferencesChangedEvent(BaseModel):
    """Event emitted when user preferences change"""
    metadata: EventMetadata
    user_id: int
    preference_category: str  # "notifications", "privacy", "trading"
    old_preferences: Dict[str, Any]
    new_preferences: Dict[str, Any]


# Event Union Type for serialization
EventType = Union[
    # Trading Events
    TradeExecutedEvent,
    TradingRewardsCalculatedEvent,
    ClanBattleScoreUpdatedEvent,
    
    # Gamification Events
    XPAwardedEvent,
    LevelUpEvent,
    AchievementUnlockedEvent,
    StreakUpdatedEvent,
    
    # Social Events
    SocialProfileCreatedEvent,
    SocialRatingChangedEvent,
    ConstellationCreatedEvent,
    ConstellationMemberJoinedEvent,
    ViralContentSharedEvent,
    SocialInteractionPerformedEvent,
    
    # Financial Events
    AccountCreatedEvent,
    FundsAddedEvent,
    PaymentProcessedEvent,
    
    # NFT Events
    NFTMintedEvent,
    NFTTradedEvent,
    NFTStakedEvent,
    
    # User Events
    UserRegisteredEvent,
    UserProfileUpdatedEvent,
    UserPreferencesChangedEvent,
]


# Event Type Registry for deserialization
EVENT_TYPE_REGISTRY = {
    # Trading Events
    "trade_executed": TradeExecutedEvent,
    "trading_rewards_calculated": TradingRewardsCalculatedEvent,
    "clan_battle_score_updated": ClanBattleScoreUpdatedEvent,
    
    # Gamification Events
    "xp_awarded": XPAwardedEvent,
    "level_up": LevelUpEvent,
    "achievement_unlocked": AchievementUnlockedEvent,
    "streak_updated": StreakUpdatedEvent,
    
    # Social Events
    "social_profile_created": SocialProfileCreatedEvent,
    "social_rating_changed": SocialRatingChangedEvent,
    "constellation_created": ConstellationCreatedEvent,
    "constellation_member_joined": ConstellationMemberJoinedEvent,
    "viral_content_shared": ViralContentSharedEvent,
    "social_interaction_performed": SocialInteractionPerformedEvent,
    
    # Financial Events
    "account_created": AccountCreatedEvent,
    "funds_added": FundsAddedEvent,
    "payment_processed": PaymentProcessedEvent,
    
    # NFT Events
    "nft_minted": NFTMintedEvent,
    "nft_traded": NFTTradedEvent,
    "nft_staked": NFTStakedEvent,
    
    # User Events
    "user_registered": UserRegisteredEvent,
    "user_profile_updated": UserProfileUpdatedEvent,
    "user_preferences_changed": UserPreferencesChangedEvent,
}


def get_event_schema(event_type: str) -> Optional[BaseModel]:
    """Get Pydantic schema class for event type"""
    return EVENT_TYPE_REGISTRY.get(event_type)


def validate_event(event_type: str, event_data: Dict[str, Any]) -> EventType:
    """Validate and deserialize event data"""
    schema_class = get_event_schema(event_type)
    if not schema_class:
        raise ValueError(f"Unknown event type: {event_type}")
    
    return schema_class(**event_data)