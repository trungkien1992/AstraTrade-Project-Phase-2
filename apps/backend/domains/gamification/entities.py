from decimal import Decimal
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from .events import DomainEvent
from .value_objects import (
    ExperiencePoints, AchievementBadge, ConstellationRank, SocialMetrics, 
    RewardPackage, XPSource, AchievementType, BadgeRarity, ConstellationRole
)


@dataclass
class UserProgression:
    """Entity representing a user's gamification progression"""
    user_id: int
    total_xp: Decimal = field(default_factory=lambda: Decimal('0'))
    current_level: int = 1
    stellar_shards: Decimal = field(default_factory=lambda: Decimal('0'))
    lumina: Decimal = field(default_factory=lambda: Decimal('0'))
    stardust: Decimal = field(default_factory=lambda: Decimal('0'))
    achievement_badges: List[AchievementBadge] = field(default_factory=list)
    current_streak: int = 0
    best_streak: int = 0
    last_activity_date: Optional[datetime] = None
    xp_multiplier: Decimal = field(default_factory=lambda: Decimal('1.0'))
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    _events: List[DomainEvent] = field(default_factory=list, init=False)
    
    def __post_init__(self):
        if self.user_id <= 0:
            raise ValueError("User ID must be positive")
        if self.total_xp < 0:
            raise ValueError("Total XP cannot be negative")
        if self.current_level < 1:
            raise ValueError("Level must be at least 1")
    
    @property
    def events(self) -> List[DomainEvent]:
        """Get domain events for this entity"""
        return self._events.copy()
    
    def clear_events(self):
        """Clear domain events after processing"""
        self._events.clear()
    
    @property
    def xp_for_next_level(self) -> Decimal:
        """Calculate XP required for next level"""
        return Decimal(str(self.current_level * 1000))  # 1000 XP per level, scaling
    
    @property
    def xp_progress_percentage(self) -> Decimal:
        """Calculate percentage progress to next level"""
        current_level_xp = Decimal(str((self.current_level - 1) * 1000))
        xp_in_current_level = self.total_xp - current_level_xp
        xp_needed_for_next_level = Decimal('1000')  # Always 1000 XP per level
        if xp_needed_for_next_level == 0:
            return Decimal('100')
        return (xp_in_current_level / xp_needed_for_next_level) * Decimal('100')
    
    @property
    def total_badge_value(self) -> Decimal:
        """Calculate total value of all achievement badges"""
        return sum(badge.total_xp_reward for badge in self.achievement_badges)
    
    @property
    def rarest_badge(self) -> Optional[AchievementBadge]:
        """Get the rarest badge earned by this user"""
        if not self.achievement_badges:
            return None
        
        rarity_order = [BadgeRarity.MYTHIC, BadgeRarity.LEGENDARY, BadgeRarity.EPIC, BadgeRarity.RARE, BadgeRarity.COMMON]
        for rarity in rarity_order:
            for badge in self.achievement_badges:
                if badge.rarity == rarity:
                    return badge
        return self.achievement_badges[0]
    
    def award_xp(self, xp: ExperiencePoints) -> bool:
        """Award XP and check for level up"""
        old_level = self.current_level
        total_xp_gained = xp.total_xp * self.xp_multiplier
        
        self.total_xp += total_xp_gained
        self._calculate_level()
        self.updated_at = datetime.utcnow()
        
        # Emit XP awarded event
        self._events.append(DomainEvent(
            event_type="xp_awarded",
            entity_id=str(self.user_id),
            data={
                "xp_amount": float(total_xp_gained),
                "source": xp.source.value,
                "multiplier": float(self.xp_multiplier),
                "new_total_xp": float(self.total_xp)
            }
        ))
        
        # Check for level up
        if self.current_level > old_level:
            self._events.append(DomainEvent(
                event_type="level_up",
                entity_id=str(self.user_id),
                data={
                    "old_level": old_level,
                    "new_level": self.current_level,
                    "total_xp": float(self.total_xp)
                }
            ))
            return True
        
        return False
    
    def unlock_achievement(self, badge: AchievementBadge) -> RewardPackage:
        """Unlock an achievement and distribute rewards"""
        if badge in self.achievement_badges:
            raise ValueError(f"Achievement {badge.name} already unlocked")
        
        self.achievement_badges.append(badge)
        
        # Award achievement XP
        achievement_xp = ExperiencePoints(
            amount=badge.total_xp_reward,
            source=XPSource.ACHIEVEMENT,
            bonus_description=f"Achievement: {badge.name}"
        )
        level_up = self.award_xp(achievement_xp)
        
        # Award currency rewards
        self.stellar_shards += badge.currency_reward.get('stellar_shards', Decimal('0'))
        self.lumina += badge.currency_reward.get('lumina', Decimal('0'))
        self.stardust += badge.currency_reward.get('stardust', Decimal('0'))
        
        # Create reward package
        reward_package = RewardPackage.achievement_reward(badge)
        
        # Emit achievement unlocked event
        self._events.append(DomainEvent(
            event_type="achievement_unlocked",
            entity_id=str(self.user_id),
            data={
                "achievement_name": badge.name,
                "achievement_type": badge.achievement_type.value,
                "rarity": badge.rarity.value,
                "reward_package": {
                    "xp": float(reward_package.xp_reward),
                    "stellar_shards": float(reward_package.stellar_shards),
                    "lumina": float(reward_package.lumina),
                    "stardust": float(reward_package.stardust)
                },
                "level_up": level_up
            }
        ))
        
        return reward_package
    
    def update_streak(self) -> bool:
        """Update trading streak based on activity"""
        today = datetime.utcnow().date()
        
        if self.last_activity_date is None:
            self.current_streak = 1
            self.best_streak = max(self.best_streak, 1)  # Update best streak
            self.last_activity_date = datetime.utcnow()
            return True
        
        last_activity_date = self.last_activity_date.date()
        
        if last_activity_date == today:
            # Already active today, no change
            return False
        elif last_activity_date == today - timedelta(days=1):
            # Consecutive day, increment streak
            self.current_streak += 1
            if self.current_streak > self.best_streak:
                self.best_streak = self.current_streak
            self.last_activity_date = datetime.utcnow()
            
            # Emit streak updated event
            self._events.append(DomainEvent(
                event_type="streak_updated",
                entity_id=str(self.user_id),
                data={
                    "current_streak": self.current_streak,
                    "best_streak": self.best_streak,
                    "is_new_best": self.current_streak == self.best_streak
                }
            ))
            
            return True
        else:
            # Streak broken
            previous_streak = self.current_streak  # Store before resetting
            self.current_streak = 1
            self.last_activity_date = datetime.utcnow()
            
            # Emit streak broken event
            self._events.append(DomainEvent(
                event_type="streak_broken",
                entity_id=str(self.user_id),
                data={
                    "previous_streak": previous_streak,
                    "best_streak": self.best_streak
                }
            ))
            
            return True
    
    def _calculate_level(self):
        """Calculate current level based on total XP"""
        # Level formula: level = floor(total_xp / 1000) + 1
        self.current_level = int(self.total_xp // 1000) + 1


@dataclass
class Constellation:
    """Entity representing a constellation (clan) in the gamification system"""
    constellation_id: int
    name: str
    description: str
    owner_id: int
    member_count: int = 0
    total_stellar_shards: Decimal = field(default_factory=lambda: Decimal('0'))
    total_lumina: Decimal = field(default_factory=lambda: Decimal('0'))
    constellation_level: int = 1
    battle_rating: Decimal = field(default_factory=lambda: Decimal('1000'))
    total_battles: int = 0
    battles_won: int = 0
    is_public: bool = True
    max_members: int = 50
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    _events: List[DomainEvent] = field(default_factory=list, init=False)
    
    def __post_init__(self):
        if self.constellation_id <= 0:
            raise ValueError("Constellation ID must be positive")
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Constellation name cannot be empty")
        if self.owner_id <= 0:
            raise ValueError("Owner ID must be positive")
        if self.max_members <= 0:
            raise ValueError("Max members must be positive")
    
    @property
    def events(self) -> List[DomainEvent]:
        """Get domain events for this entity"""
        return self._events.copy()
    
    def clear_events(self):
        """Clear domain events after processing"""
        self._events.clear()
    
    @property
    def total_contribution_value(self) -> Decimal:
        """Calculate total contribution value in stellar shards equivalent"""
        lumina_to_shards_rate = Decimal('10.0')
        return self.total_stellar_shards + (self.total_lumina * lumina_to_shards_rate)
    
    @property
    def win_rate(self) -> Decimal:
        """Calculate battle win rate as percentage"""
        if self.total_battles == 0:
            return Decimal('0')
        return (Decimal(str(self.battles_won)) / Decimal(str(self.total_battles))) * Decimal('100')
    
    @property
    def is_full(self) -> bool:
        """Check if constellation is at maximum capacity"""
        return self.member_count >= self.max_members
    
    @property
    def average_contribution_per_member(self) -> Decimal:
        """Calculate average contribution per member"""
        if self.member_count == 0:
            return Decimal('0')
        return self.total_contribution_value / Decimal(str(self.member_count))
    
    def add_member(self, user_id: int, actor_id: Optional[int] = None) -> ConstellationRank:
        """Add a new member to the constellation"""
        if actor_id is not None and actor_id not in (user_id, self.owner_id):
            raise PermissionError("Not authorized to add member")
        if self.is_full:
            raise ValueError("Constellation is at maximum capacity")
        
        self.member_count += 1
        self.updated_at = datetime.utcnow()
        
        member_rank = ConstellationRank.new_member()
        
        self._events.append(DomainEvent(
            event_type="member_joined",
            entity_id=str(self.constellation_id),
            data={
                "user_id": user_id,
                "member_count": self.member_count,
                "constellation_name": self.name
            }
        ))
        
        return member_rank
    
    def remove_member(self, user_id: int, actor_id: Optional[int] = None):
        """Remove a member from the constellation"""
        if actor_id is not None and actor_id not in (user_id, self.owner_id):
            raise PermissionError("Not authorized to remove member")
        if self.member_count <= 1 and user_id == self.owner_id:
            raise ValueError("Cannot remove the last member who is also the owner")
        
        self.member_count = max(0, self.member_count - 1)
        self.updated_at = datetime.utcnow()
        
        self._events.append(DomainEvent(
            event_type="member_left",
            entity_id=str(self.constellation_id),
            data={
                "user_id": user_id,
                "member_count": self.member_count,
                "constellation_name": self.name
            }
        ))
    
    def update_contribution(self, stellar_shards: Decimal, lumina: Decimal):
        """Update constellation's total contributions"""
        if stellar_shards < 0 or lumina < 0:
            raise ValueError("Contribution amounts cannot be negative")
        
        self.total_stellar_shards += stellar_shards
        self.total_lumina += lumina
        self._calculate_level()
        self.updated_at = datetime.utcnow()
        
        # Emit contribution updated event
        self._events.append(DomainEvent(
            event_type="contribution_updated",
            entity_id=str(self.constellation_id),
            data={
                "stellar_shards_added": float(stellar_shards),
                "lumina_added": float(lumina),
                "total_contribution_value": float(self.total_contribution_value),
                "new_level": self.constellation_level
            }
        ))
    
    def record_battle_result(self, won: bool, rating_change: Decimal):
        """Record the result of a constellation battle"""
        self.total_battles += 1
        if won:
            self.battles_won += 1
        
        self.battle_rating += rating_change
        self.battle_rating = max(self.battle_rating, Decimal('100'))  # Minimum rating
        self.updated_at = datetime.utcnow()
        
        # Emit battle result event
        self._events.append(DomainEvent(
            event_type="battle_completed",
            entity_id=str(self.constellation_id),
            data={
                "won": won,
                "rating_change": float(rating_change),
                "new_rating": float(self.battle_rating),
                "total_battles": self.total_battles,
                "battles_won": self.battles_won,
                "win_rate": float(self.win_rate)
            }
        ))
    
    def _calculate_level(self):
        """Calculate constellation level based on total contributions"""
        # Level formula: level = floor(total_contribution_value / 10000) + 1
        self.constellation_level = int(self.total_contribution_value // 10000) + 1


@dataclass
class Achievement:
    """Entity representing an achievement definition"""
    achievement_id: str
    badge: AchievementBadge
    is_active: bool = True
    unlock_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    _events: List[DomainEvent] = field(default_factory=list, init=False)
    
    def __post_init__(self):
        if not self.achievement_id or len(self.achievement_id.strip()) == 0:
            raise ValueError("Achievement ID cannot be empty")
    
    @property
    def events(self) -> List[DomainEvent]:
        """Get domain events for this entity"""
        return self._events.copy()
    
    def clear_events(self):
        """Clear domain events after processing"""
        self._events.clear()
    
    @property
    def unlock_rate(self) -> Decimal:
        """Calculate unlock rate as percentage (requires total user count from service)"""
        # This would be calculated by the domain service with total user count
        return Decimal('0')  # Placeholder
    
    def check_unlock_conditions(self, user_data: Dict[str, Any]) -> bool:
        """Check if a user meets the unlock conditions for this achievement"""
        for condition_key, required_value in self.badge.unlock_conditions.items():
            user_value = user_data.get(condition_key, 0)
            
            if isinstance(required_value, (int, float)):
                if user_value < required_value:
                    return False
            elif isinstance(required_value, str):
                if user_value != required_value:
                    return False
            elif isinstance(required_value, list):
                if user_value not in required_value:
                    return False
        
        return True
    
    def record_unlock(self, user_id: int, actor_id: Optional[int] = None):
        """Record that this achievement was unlocked by a user"""
        if actor_id is not None and actor_id != user_id:
            raise PermissionError("Not authorized to record unlock")
        self.unlock_count += 1
        
        self._events.append(DomainEvent(
            event_type="achievement_unlock_recorded",
            entity_id=self.achievement_id,
            data={
                "user_id": user_id,
                "achievement_name": self.badge.name,
                "unlock_count": self.unlock_count
            }
        ))


@dataclass  
class Leaderboard:
    """Entity representing a leaderboard for rankings"""
    leaderboard_id: str
    name: str
    description: str
    leaderboard_type: str  # "individual", "constellation", "achievement"
    time_period: str  # "daily", "weekly", "monthly", "all_time"
    max_entries: int = 100
    is_active: bool = True
    last_updated: datetime = field(default_factory=datetime.utcnow)
    created_at: datetime = field(default_factory=datetime.utcnow)
    _events: List[DomainEvent] = field(default_factory=list, init=False)
    
    def __post_init__(self):
        if not self.leaderboard_id or len(self.leaderboard_id.strip()) == 0:
            raise ValueError("Leaderboard ID cannot be empty")
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Leaderboard name cannot be empty")
        if self.max_entries <= 0:
            raise ValueError("Max entries must be positive")
    
    @property
    def events(self) -> List[DomainEvent]:
        """Get domain events for this entity"""
        return self._events.copy()
    
    def clear_events(self):
        """Clear domain events after processing"""
        self._events.clear()
    
    def should_reset(self) -> bool:
        """Check if leaderboard should be reset based on time period"""
        now = datetime.utcnow()
        
        if self.time_period == "daily":
            return now.date() > self.last_updated.date()
        elif self.time_period == "weekly":
            # Reset on Mondays
            days_since_update = (now - self.last_updated).days
            return days_since_update >= 7 and now.weekday() == 0
        elif self.time_period == "monthly":
            return now.month != self.last_updated.month or now.year != self.last_updated.year
        
        return False  # all_time leaderboards never reset
    
    def reset(self):
        """Reset the leaderboard for a new time period"""
        self.last_updated = datetime.utcnow()
        
        # Emit leaderboard reset event
        self._events.append(DomainEvent(
            event_type="leaderboard_reset",
            entity_id=self.leaderboard_id,
            data={
                "leaderboard_name": self.name,
                "time_period": self.time_period,
                "reset_time": self.last_updated.isoformat()
            }
        ))
    
    def update_rankings(self, entry_count: int):
        """Update leaderboard after rankings calculation"""
        self.last_updated = datetime.utcnow()
        
        # Emit rankings updated event
        self._events.append(DomainEvent(
            event_type="rankings_updated",
            entity_id=self.leaderboard_id,
            data={
                "leaderboard_name": self.name,
                "entry_count": entry_count,
                "update_time": self.last_updated.isoformat()
            }
        ))


@dataclass
class Reward:
    """Entity representing a reward distribution record"""
    reward_id: str
    user_id: int
    reward_package: RewardPackage
    source_type: str  # "achievement", "battle", "streak", "event"
    source_id: str  # ID of the source (achievement_id, battle_id, etc.)
    is_claimed: bool = False
    claimed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    _events: List[DomainEvent] = field(default_factory=list, init=False)
    
    def __post_init__(self):
        if not self.reward_id or len(self.reward_id.strip()) == 0:
            raise ValueError("Reward ID cannot be empty")
        if self.user_id <= 0:
            raise ValueError("User ID must be positive")
        if not self.source_type or len(self.source_type.strip()) == 0:
            raise ValueError("Source type cannot be empty")
    
    @property
    def events(self) -> List[DomainEvent]:
        """Get domain events for this entity"""
        return self._events.copy()
    
    def clear_events(self):
        """Clear domain events after processing"""
        self._events.clear()
    
    @property
    def is_expired(self) -> bool:
        """Check if reward has expired"""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    @property
    def can_be_claimed(self) -> bool:
        """Check if reward can be claimed"""
        return not self.is_claimed and not self.is_expired
    
    def claim(self, actor_id: Optional[int] = None) -> RewardPackage:
        """Claim the reward"""
        if actor_id is not None and actor_id != self.user_id:
            raise PermissionError("Not authorized to claim reward")
        if self.is_claimed:
            raise ValueError("Reward has already been claimed")
        if self.is_expired:
            raise ValueError("Reward has expired")
        
        self.is_claimed = True
        self.claimed_at = datetime.utcnow()
        
        self._events.append(DomainEvent(
            event_type="reward_claimed",
            entity_id=self.reward_id,
            data={
                "user_id": self.user_id,
                "source_type": self.source_type,
                "source_id": self.source_id,
                "reward_value": float(self.reward_package.total_currency_value),
                "claimed_at": self.claimed_at.isoformat()
            }
        ))
        
        return self.reward_package