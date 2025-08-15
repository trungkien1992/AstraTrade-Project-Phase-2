"""
Event Validation Models

Pydantic models for event schema validation and governance.
Ensures event integrity across all domains and Redis Streams integration.
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, validator
import json


class EventValidationModel(BaseModel):
    """
    Pydantic model for validating enhanced DomainEvent structure.
    
    Enforces schema compliance across all domains and validates
    Redis Streams serialization compatibility.
    """
    event_id: str = Field(..., min_length=36, max_length=36, description="UUID v4 format")
    event_type: str = Field(..., min_length=3, pattern=r'^[A-Z][a-z]+\.[A-Z][a-zA-Z]+$', description="Format: Domain.EventName")
    domain: str = Field(..., min_length=3, max_length=20, description="Domain name")
    entity_id: str = Field(..., min_length=1, description="Aggregate/Entity ID")
    occurred_at: str = Field(..., description="ISO 8601 datetime format")
    event_version: int = Field(ge=1, le=999, description="Event schema version")
    correlation_id: str = Field(default="", max_length=100, description="Request correlation ID")
    causation_id: str = Field(default="", max_length=100, description="Event causation ID")
    producer: str = Field(..., min_length=5, description="Service identifier")
    data: str = Field(default="", description="JSON-serialized domain payload")
    
    @validator('occurred_at')
    def validate_datetime_format(cls, v):
        """Validate ISO 8601 datetime format."""
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
            return v
        except ValueError:
            raise ValueError('occurred_at must be valid ISO 8601 format')
    
    @validator('data')
    def validate_json_data(cls, v):
        """Validate data field contains valid JSON or empty string."""
        if v and v.strip():
            try:
                json.loads(v) if isinstance(v, str) else v
                return v
            except (json.JSONDecodeError, TypeError):
                # Allow non-JSON string data for compatibility
                return v
        return v
    
    @validator('event_type')
    def validate_event_type_format(cls, v):
        """Validate event_type follows Domain.EventName convention."""
        parts = v.split('.')
        if len(parts) != 2:
            raise ValueError('event_type must be in format Domain.EventName')
        domain, event = parts
        if not domain[0].isupper() or not event[0].isupper():
            raise ValueError('Domain and EventName must start with uppercase')
        return v


class DomainEventRegistry:
    """
    Registry for known event types across all domains.
    
    Maintains catalog of valid events for schema validation
    and cross-domain event discovery.
    """
    
    # Known event types by domain
    KNOWN_EVENTS = {
        "Trading": [
            "TradeExecuted", "TradingRewardsCalculated", "ClanBattleScoreUpdated",
            "TradeCreated", "TradeClosed", "TradeFailed"
        ],
        "Gamification": [
            "XPGained", "LevelUp", "AchievementUnlocked", "StreakUpdated",
            "LeaderboardUpdated", "ProgressionCalculated"
        ],
        "Social": [
            "SocialProfileCreated", "SocialRatingChanged", "ConstellationCreated",
            "ConstellationMemberJoined", "ViralContentShared", "SocialInteractionPerformed"
        ],
        "User": [
            "UserRegistered", "ProfileUpdated", "PreferencesChanged",
            "SessionStarted", "SessionEnded", "AccountStatusChanged"
        ],
        "Financial": [
            "AccountCreated", "FundsAdded", "FundsWithdrawn", "PaymentMethodAdded",
            "TransactionRecorded", "SubscriptionCreated", "PaymentCompleted",
            "InvoiceCreated", "InvoicePaid", "PaymentFailed"
        ],
        "NFT": [
            "NFTCreated", "NFTMinted", "NFTListed", "NFTSold", "NFTTransferred",
            "MarketplaceSale", "CollectionCreated", "RewardClaimed"
        ]
    }
    
    @classmethod
    def is_valid_event_type(cls, event_type: str) -> bool:
        """Check if event type is registered and valid."""
        try:
            domain, event = event_type.split('.')
            return domain in cls.KNOWN_EVENTS and event in cls.KNOWN_EVENTS[domain]
        except ValueError:
            return False
    
    @classmethod
    def get_events_for_domain(cls, domain: str) -> List[str]:
        """Get all registered events for a domain."""
        return cls.KNOWN_EVENTS.get(domain, [])
    
    @classmethod
    def register_event(cls, domain: str, event_name: str) -> None:
        """Register a new event type."""
        if domain not in cls.KNOWN_EVENTS:
            cls.KNOWN_EVENTS[domain] = []
        if event_name not in cls.KNOWN_EVENTS[domain]:
            cls.KNOWN_EVENTS[domain].append(event_name)


class EventValidationError(Exception):
    """Custom exception for event validation failures."""
    
    def __init__(self, message: str, event_data: Dict[str, Any] = None):
        super().__init__(message)
        self.event_data = event_data


def validate_event_schema(event_dict: Dict[str, Any]) -> EventValidationModel:
    """
    Validate event dictionary against schema.
    
    Args:
        event_dict: Event data dictionary from Redis Streams or domain
        
    Returns:
        EventValidationModel: Validated event model
        
    Raises:
        EventValidationError: If validation fails
    """
    try:
        validated = EventValidationModel(**event_dict)
        
        # Additional business rule validation
        if not DomainEventRegistry.is_valid_event_type(validated.event_type):
            raise EventValidationError(
                f"Unknown event type: {validated.event_type}",
                event_dict
            )
        
        return validated
    
    except Exception as e:
        raise EventValidationError(f"Event validation failed: {str(e)}", event_dict)


def validate_redis_stream_payload(stream_data: Dict[str, Any]) -> bool:
    """
    Validate Redis Streams payload format.
    
    Ensures all fields are string-serializable for Redis storage.
    """
    required_fields = [
        'event_id', 'event_type', 'domain', 'entity_id', 'occurred_at',
        'event_version', 'producer'
    ]
    
    for field in required_fields:
        if field not in stream_data:
            return False
        
        # Redis Streams requires all values to be strings
        if not isinstance(stream_data[field], str):
            return False
    
    return True


# Pre-configured validation models for each domain
class TradingEventModel(EventValidationModel):
    """Trading domain specific event validation."""
    
    @validator('domain')
    def validate_trading_domain(cls, v):
        if v != 'trading':
            raise ValueError('Domain must be "trading" for trading events')
        return v


class GameificationEventModel(EventValidationModel):
    """Gamification domain specific event validation."""
    
    @validator('domain')
    def validate_gamification_domain(cls, v):
        if v != 'gamification':
            raise ValueError('Domain must be "gamification" for gamification events')
        return v


class SocialEventModel(EventValidationModel):
    """Social domain specific event validation."""
    
    @validator('domain') 
    def validate_social_domain(cls, v):
        if v != 'social':
            raise ValueError('Domain must be "social" for social events')
        return v


class UserEventModel(EventValidationModel):
    """User domain specific event validation."""
    
    @validator('domain')
    def validate_user_domain(cls, v):
        if v != 'user':
            raise ValueError('Domain must be "user" for user events')
        return v


class FinancialEventModel(EventValidationModel):
    """Financial domain specific event validation."""
    
    @validator('domain')
    def validate_financial_domain(cls, v):
        if v != 'financial':
            raise ValueError('Domain must be "financial" for financial events')
        return v


class NFTEventModel(EventValidationModel):
    """NFT domain specific event validation."""
    
    @validator('domain')
    def validate_nft_domain(cls, v):
        if v != 'nft':  
            raise ValueError('Domain must be "nft" for NFT events')
        return v