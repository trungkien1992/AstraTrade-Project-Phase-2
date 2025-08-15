"""
Gamification Domain Events

Enhanced event system using unified schema with backward compatibility.
Integrates with Redis Streams while preserving existing functionality.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from ..shared.events import DomainEvent as EnhancedDomainEvent
from ..shared.adapters import GamificationEventAdapter


# Legacy DomainEvent class for backward compatibility
@dataclass
class DomainEvent:
    """
    Legacy domain event for gamification domain.
    
    DEPRECATED: Use create_gamification_event() for new events.
    This class is maintained for backward compatibility only.
    """
    event_type: str
    entity_id: str
    data: Dict[str, Any]
    occurred_at: datetime = None
    
    def __post_init__(self):
        if self.occurred_at is None:
            self.occurred_at = datetime.now(timezone.utc)
    
    def to_enhanced_event(self) -> Dict[str, Any]:
        """Convert legacy event to enhanced schema for Redis Streams."""
        return GamificationEventAdapter.adapt_legacy_event(self)


# Enhanced Event Classes using unified schema
@dataclass
class XPGainedEvent(EnhancedDomainEvent):
    """Event raised when user gains XP from activities."""
    user_id: int = 0
    activity_type: str = ""
    xp_amount: int = 0
    total_xp: int = 0
    
    def __post_init__(self):
        super().__post_init__()
        self.domain = "gamification"
        self.entity_id = f"user_{self.user_id}"
        self.data = {
            "user_id": self.user_id,
            "activity_type": self.activity_type,  
            "xp_amount": self.xp_amount,
            "total_xp": self.total_xp
        }
    
    @property
    def event_type(self) -> str:
        return "Gamification.XPGained"


@dataclass
class LevelUpEvent(EnhancedDomainEvent):
    """Event raised when user levels up."""
    user_id: int = 0
    old_level: int = 0
    new_level: int = 0
    rewards_unlocked: list = None
    
    def __post_init__(self):
        super().__post_init__()
        self.domain = "gamification"
        self.entity_id = f"user_{self.user_id}"
        if self.rewards_unlocked is None:
            self.rewards_unlocked = []
        self.data = {
            "user_id": self.user_id,
            "old_level": self.old_level,
            "new_level": self.new_level,
            "rewards_unlocked": self.rewards_unlocked
        }
    
    @property
    def event_type(self) -> str:
        return "Gamification.LevelUp"


@dataclass  
class AchievementUnlockedEvent(EnhancedDomainEvent):
    """Event raised when user unlocks an achievement."""
    user_id: int = 0
    achievement_id: str = ""
    achievement_name: str = ""
    xp_reward: int = 0
    
    def __post_init__(self):
        super().__post_init__()
        self.domain = "gamification"
        self.entity_id = f"achievement_{self.achievement_id}"
        self.data = {
            "user_id": self.user_id,
            "achievement_id": self.achievement_id,
            "achievement_name": self.achievement_name,
            "xp_reward": self.xp_reward
        }
    
    @property
    def event_type(self) -> str:
        return "Gamification.AchievementUnlocked"


@dataclass
class StreakUpdatedEvent(EnhancedDomainEvent):
    """Event raised when user's activity streak is updated."""
    user_id: int = 0
    streak_type: str = ""
    streak_count: int = 0
    bonus_multiplier: float = 1.0
    
    def __post_init__(self):
        super().__post_init__()
        self.domain = "gamification"
        self.entity_id = f"user_{self.user_id}"
        self.data = {
            "user_id": self.user_id,
            "streak_type": self.streak_type,
            "streak_count": self.streak_count,
            "bonus_multiplier": self.bonus_multiplier
        }
    
    @property
    def event_type(self) -> str:
        return "Gamification.StreakUpdated"


@dataclass
class LeaderboardUpdatedEvent(EnhancedDomainEvent):
    """Event raised when leaderboard positions change."""
    leaderboard_id: str = ""
    user_id: int = 0
    old_position: int = 0
    new_position: int = 0
    score: int = 0
    
    def __post_init__(self):
        super().__post_init__()
        self.domain = "gamification"
        self.entity_id = f"leaderboard_{self.leaderboard_id}"
        self.data = {
            "leaderboard_id": self.leaderboard_id,
            "user_id": self.user_id,
            "old_position": self.old_position,
            "new_position": self.new_position,
            "score": self.score
        }
    
    @property
    def event_type(self) -> str:
        return "Gamification.LeaderboardUpdated"


# Helper functions for creating events
def create_gamification_event(
    event_type: str,
    entity_id: str,
    data: Dict[str, Any] = None,
    correlation_id: Optional[str] = None,
    user_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Create enhanced gamification event for Redis Streams.
    
    Recommended way to create new gamification events.
    """
    return GamificationEventAdapter.create_gamification_event(
        event_type=event_type,
        entity_id=entity_id,
        data=data,
        correlation_id=correlation_id,
        user_id=user_id
    )


def create_xp_gained_event(user_id: int, activity_type: str, xp_amount: int, total_xp: int,
                          correlation_id: Optional[str] = None) -> XPGainedEvent:
    """Create XP gained event with correlation tracking."""
    event = XPGainedEvent(
        user_id=user_id,
        activity_type=activity_type,
        xp_amount=xp_amount,
        total_xp=total_xp
    )
    if correlation_id:
        event.correlation_id = correlation_id
    return event


def create_level_up_event(user_id: int, old_level: int, new_level: int, rewards: list = None,
                         correlation_id: Optional[str] = None) -> LevelUpEvent:
    """Create level up event with correlation tracking."""
    event = LevelUpEvent(
        user_id=user_id,
        old_level=old_level,
        new_level=new_level,
        rewards_unlocked=rewards or []
    )
    if correlation_id:
        event.correlation_id = correlation_id
    return event