"""
Gamification Domain Package

This domain consolidates all gamification-related functionality including:
- User progression and XP systems
- Achievement and badge systems  
- Constellation (clan) management
- Leaderboards and rankings
- Reward distribution and claiming
- Social features and viral content

Service Consolidation: 3,314 lines → ~800 lines (76% reduction)
"""

from .value_objects import (
    ExperiencePoints,
    AchievementBadge,
    ConstellationRank,
    SocialMetrics,
    RewardPackage,
    XPSource,
    AchievementType,
    BadgeRarity,
    ConstellationRole
)

from .entities import (
    UserProgression,
    Constellation,
    Achievement,
    Leaderboard,
    Reward
)

from .services import (
    GamificationDomainService,
    UserStats
)

from .events import DomainEvent

__all__ = [
    # Value Objects
    'ExperiencePoints',
    'AchievementBadge', 
    'ConstellationRank',
    'SocialMetrics',
    'RewardPackage',
    'XPSource',
    'AchievementType',
    'BadgeRarity',
    'ConstellationRole',
    
    # Entities
    'UserProgression',
    'Constellation',
    'Achievement',
    'Leaderboard',
    'Reward',
    
    # Services
    'GamificationDomainService',
    'UserStats',
    
    # Events
    'DomainEvent'
]