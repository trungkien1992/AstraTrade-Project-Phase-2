"""
Comprehensive tests for Gamification Domain Entities

This module tests all entities with full coverage including:
- Entity creation and validation
- Business logic and state transitions
- Domain event emission and handling
- Edge cases and error conditions
- Immutability and consistency rules
"""

import unittest
from decimal import Decimal
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

import sys
from pathlib import Path

# Add backend directory to path for imports
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from domains.gamification.entities import (
    UserProgression, Constellation, Achievement, Leaderboard, Reward
)
from domains.gamification.value_objects import (
    ExperiencePoints, AchievementBadge, ConstellationRank, SocialMetrics, 
    RewardPackage, XPSource, AchievementType, BadgeRarity, ConstellationRole
)
from domains.gamification.events import DomainEvent


class TestUserProgression(unittest.TestCase):
    """Comprehensive tests for UserProgression entity"""
    
    def test_create_valid_user_progression_minimal(self):
        """Test creating UserProgression with minimal required parameters"""
        progression = UserProgression(user_id=123)
        
        self.assertEqual(progression.user_id, 123)
        self.assertEqual(progression.total_xp, Decimal('0'))
        self.assertEqual(progression.current_level, 1)
        self.assertEqual(progression.stellar_shards, Decimal('0'))
        self.assertEqual(progression.lumina, Decimal('0'))
        self.assertEqual(progression.stardust, Decimal('0'))
        self.assertEqual(len(progression.achievement_badges), 0)
        self.assertEqual(progression.current_streak, 0)
        self.assertEqual(progression.best_streak, 0)
        self.assertIsNone(progression.last_activity_date)
        self.assertEqual(progression.xp_multiplier, Decimal('1.0'))
        self.assertIsInstance(progression.created_at, datetime)
        self.assertIsInstance(progression.updated_at, datetime)
        self.assertEqual(len(progression.events), 0)
    
    def test_create_valid_user_progression_full(self):
        """Test creating UserProgression with all parameters"""
        badges = [AchievementBadge.trading_milestone(10)]
        created_time = datetime(2023, 1, 1, 12, 0, 0)
        updated_time = datetime(2023, 1, 2, 12, 0, 0)
        last_activity = datetime(2023, 1, 1, 18, 0, 0)
        
        progression = UserProgression(
            user_id=456,
            total_xp=Decimal('2500.50'),
            current_level=3,
            stellar_shards=Decimal('1000.25'),
            lumina=Decimal('50.75'),
            stardust=Decimal('2.5'),
            achievement_badges=badges,
            current_streak=7,
            best_streak=12,
            last_activity_date=last_activity,
            xp_multiplier=Decimal('1.15'),
            created_at=created_time,
            updated_at=updated_time
        )
        
        self.assertEqual(progression.user_id, 456)
        self.assertEqual(progression.total_xp, Decimal('2500.50'))
        self.assertEqual(progression.current_level, 3)
        self.assertEqual(progression.stellar_shards, Decimal('1000.25'))
        self.assertEqual(progression.lumina, Decimal('50.75'))
        self.assertEqual(progression.stardust, Decimal('2.5'))
        self.assertEqual(len(progression.achievement_badges), 1)
        self.assertEqual(progression.achievement_badges[0], badges[0])
        self.assertEqual(progression.current_streak, 7)
        self.assertEqual(progression.best_streak, 12)
        self.assertEqual(progression.last_activity_date, last_activity)
        self.assertEqual(progression.xp_multiplier, Decimal('1.15'))
        self.assertEqual(progression.created_at, created_time)
        self.assertEqual(progression.updated_at, updated_time)
    
    def test_invalid_user_id_validation(self):
        """Test that invalid user IDs raise ValueError with specific messages"""
        invalid_ids = [0, -1, -100]
        
        for invalid_id in invalid_ids:
            with self.assertRaises(ValueError) as context:
                UserProgression(user_id=invalid_id)
            
            self.assertIn("User ID must be positive", str(context.exception))
    
    def test_negative_total_xp_validation(self):
        """Test that negative total XP raises ValueError"""
        with self.assertRaises(ValueError) as context:
            UserProgression(user_id=1, total_xp=Decimal('-100'))
        
        self.assertIn("Total XP cannot be negative", str(context.exception))
    
    def test_invalid_level_validation(self):
        """Test that level below 1 raises ValueError"""
        with self.assertRaises(ValueError) as context:
            UserProgression(user_id=1, current_level=0)
        
        self.assertIn("Level must be at least 1", str(context.exception))
    
    def test_xp_for_next_level_calculation(self):
        """Test XP required for next level calculation"""
        test_cases = [
            (1, Decimal('1000')),   # Level 1 needs 1000 XP for level 2
            (5, Decimal('5000')),   # Level 5 needs 5000 XP for level 6
            (10, Decimal('10000')), # Level 10 needs 10000 XP for level 11
            (100, Decimal('100000')) # Level 100 needs 100000 XP for level 101
        ]
        
        for level, expected_xp in test_cases:
            progression = UserProgression(user_id=1, current_level=level)
            self.assertEqual(progression.xp_for_next_level, expected_xp)
    
    def test_xp_progress_percentage_calculation(self):
        """Test XP progress percentage calculation"""
        # Level 1 user with 500 XP (50% to level 2)
        progression = UserProgression(user_id=1, total_xp=Decimal('500'))
        self.assertEqual(progression.xp_progress_percentage, Decimal('50'))
        
        # Level 2 user with 1750 XP (75% to level 3)
        # Level 2 starts at 1000 XP, needs 1000 more for level 3
        # Has 750 XP in current level = 75%
        progression = UserProgression(user_id=1, total_xp=Decimal('1750'), current_level=2)
        self.assertEqual(progression.xp_progress_percentage, Decimal('75'))
        
        # Edge case: exactly at level boundary
        progression = UserProgression(user_id=1, total_xp=Decimal('1000'), current_level=2)
        self.assertEqual(progression.xp_progress_percentage, Decimal('0'))
    
    def test_award_xp_without_level_up(self):
        """Test awarding XP that doesn't cause level up"""
        progression = UserProgression(user_id=1)
        initial_level = progression.current_level
        
        xp = ExperiencePoints(
            amount=Decimal('500'),
            source=XPSource.SOCIAL,
            multiplier=Decimal('1.2')
        )
        
        level_up = progression.award_xp(xp)
        
        # Should not level up
        self.assertFalse(level_up)
        self.assertEqual(progression.current_level, initial_level)
        
        # XP should be awarded with multiplier consideration
        expected_xp = Decimal('500') * Decimal('1.2') * progression.xp_multiplier
        self.assertEqual(progression.total_xp, expected_xp)
        
        # Updated timestamp should be set
        self.assertIsNotNone(progression.updated_at)
        
        # Should emit XP awarded event only
        events = progression.events
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].event_type, "xp_awarded")
        self.assertEqual(events[0].entity_id, "1")
        self.assertEqual(events[0].data["xp_amount"], float(expected_xp))
        self.assertEqual(events[0].data["source"], XPSource.SOCIAL.value)
    
    def test_award_xp_with_level_up(self):
        """Test awarding XP that causes level up"""
        progression = UserProgression(user_id=2)
        initial_level = progression.current_level
        
        # Award enough XP to level up (1500 XP should go from level 1 to 2)
        xp = ExperiencePoints(
            amount=Decimal('1500'),
            source=XPSource.TRADING,
            multiplier=Decimal('1.0')
        )
        
        level_up = progression.award_xp(xp)
        
        # Should level up
        self.assertTrue(level_up)
        self.assertEqual(progression.current_level, initial_level + 1)
        self.assertEqual(progression.total_xp, Decimal('1500'))
        
        # Should emit both XP awarded and level up events
        events = progression.events
        self.assertEqual(len(events), 2)
        
        xp_event = next(e for e in events if e.event_type == "xp_awarded")
        self.assertEqual(xp_event.entity_id, "2")
        self.assertEqual(xp_event.data["source"], XPSource.TRADING.value)
        
        levelup_event = next(e for e in events if e.event_type == "level_up")
        self.assertEqual(levelup_event.entity_id, "2")
        self.assertEqual(levelup_event.data["old_level"], initial_level)
        self.assertEqual(levelup_event.data["new_level"], initial_level + 1)
    
    def test_award_xp_multiple_level_ups(self):
        """Test awarding XP that causes multiple level ups"""
        progression = UserProgression(user_id=3)
        
        # Award massive XP to jump multiple levels
        xp = ExperiencePoints(
            amount=Decimal('5500'),  # Should go from level 1 to 6
            source=XPSource.ACHIEVEMENT
        )
        
        level_up = progression.award_xp(xp)
        
        # Should level up and reach appropriate level
        self.assertTrue(level_up)
        self.assertEqual(progression.current_level, 6)  # floor(5500/1000) + 1
        self.assertEqual(progression.total_xp, Decimal('5500'))
    
    def test_unlock_achievement_success(self):
        """Test successful achievement unlock"""
        progression = UserProgression(user_id=4)
        initial_xp = progression.total_xp
        initial_shards = progression.stellar_shards
        
        badge = AchievementBadge.trading_milestone(100)  # Rare badge
        
        reward_package = progression.unlock_achievement(badge)
        
        # Badge should be added
        self.assertIn(badge, progression.achievement_badges)
        self.assertEqual(len(progression.achievement_badges), 1)
        
        # Currency rewards should be applied
        self.assertEqual(
            progression.stellar_shards, 
            initial_shards + badge.currency_reward['stellar_shards']
        )
        
        # XP should be increased (badge XP is awarded)
        expected_total_xp = initial_xp + badge.total_xp_reward
        self.assertEqual(progression.total_xp, expected_total_xp)
        
        # Reward package should be returned
        self.assertIsInstance(reward_package, RewardPackage)
        self.assertEqual(reward_package.xp_reward, badge.total_xp_reward)
        self.assertEqual(reward_package.stellar_shards, badge.currency_reward['stellar_shards'])
        
        # Achievement unlocked event should be emitted
        events = progression.events
        achievement_events = [e for e in events if e.event_type == "achievement_unlocked"]
        self.assertEqual(len(achievement_events), 1)
        
        event = achievement_events[0]
        self.assertEqual(event.entity_id, "4")
        self.assertEqual(event.data["achievement_name"], badge.name)
        self.assertEqual(event.data["achievement_type"], badge.achievement_type.value)
        self.assertEqual(event.data["rarity"], badge.rarity.value)
    
    def test_unlock_duplicate_achievement_error(self):
        """Test that unlocking duplicate achievement raises error"""
        progression = UserProgression(user_id=5)
        badge = AchievementBadge.trading_milestone(10)
        
        # Unlock achievement first time
        progression.unlock_achievement(badge)
        progression.clear_events()  # Clear events for clean test
        
        # Try to unlock same achievement again
        with self.assertRaises(ValueError) as context:
            progression.unlock_achievement(badge)
        
        self.assertIn("already unlocked", str(context.exception))
        self.assertIn(badge.name, str(context.exception))
        
        # No new events should be emitted
        self.assertEqual(len(progression.events), 0)
    
    def test_update_streak_first_activity(self):
        """Test streak update for first activity"""
        progression = UserProgression(user_id=6)
        
        updated = progression.update_streak()
        
        self.assertTrue(updated)
        self.assertEqual(progression.current_streak, 1)
        self.assertEqual(progression.best_streak, 1)
        self.assertIsNotNone(progression.last_activity_date)
    
    @patch('domains.gamification.entities.datetime')
    def test_update_streak_consecutive_days(self, mock_datetime):
        """Test streak update for consecutive days"""
        progression = UserProgression(user_id=7)
        
        # Set up mock for consistent time
        day1 = datetime(2023, 1, 1, 12, 0, 0)
        day2 = datetime(2023, 1, 2, 12, 0, 0)
        
        # First day activity
        mock_datetime.utcnow.return_value = day1
        progression.update_streak()
        progression.clear_events()
        
        # Second day activity (consecutive)
        mock_datetime.utcnow.return_value = day2
        progression.last_activity_date = day1  # Set previous activity
        
        updated = progression.update_streak()
        
        self.assertTrue(updated)
        self.assertEqual(progression.current_streak, 2)
        self.assertEqual(progression.best_streak, 2)
        
        # Should emit streak updated event
        events = progression.events
        streak_events = [e for e in events if e.event_type == "streak_updated"]
        self.assertEqual(len(streak_events), 1)
        
        event = streak_events[0]
        self.assertEqual(event.data["current_streak"], 2)
        self.assertEqual(event.data["best_streak"], 2)
        self.assertTrue(event.data["is_new_best"])
    
    @patch('domains.gamification.entities.datetime')
    def test_update_streak_same_day_no_change(self, mock_datetime):
        """Test streak update on same day doesn't change streak"""
        progression = UserProgression(user_id=8, current_streak=3)
        
        same_day = datetime(2023, 1, 5, 12, 0, 0)
        mock_datetime.utcnow.return_value = same_day
        progression.last_activity_date = same_day
        
        updated = progression.update_streak()
        
        self.assertFalse(updated)
        self.assertEqual(progression.current_streak, 3)  # Unchanged
        self.assertEqual(len(progression.events), 0)  # No events
    
    @patch('domains.gamification.entities.datetime')
    def test_update_streak_broken(self, mock_datetime):
        """Test streak breaking after gap"""
        progression = UserProgression(user_id=9, current_streak=5, best_streak=7)
        
        # Set up dates with gap
        last_activity = datetime(2023, 1, 1, 12, 0, 0)
        current_day = datetime(2023, 1, 5, 12, 0, 0)  # 4-day gap breaks streak
        
        mock_datetime.utcnow.return_value = current_day
        progression.last_activity_date = last_activity
        
        updated = progression.update_streak()
        
        self.assertTrue(updated)
        self.assertEqual(progression.current_streak, 1)  # Reset to 1
        self.assertEqual(progression.best_streak, 7)  # Best streak unchanged
        
        # Should emit streak broken event
        events = progression.events
        streak_events = [e for e in events if e.event_type == "streak_broken"]
        self.assertEqual(len(streak_events), 1)
        
        event = streak_events[0]
        self.assertEqual(event.data["previous_streak"], 5)
        self.assertEqual(event.data["best_streak"], 7)
    
    def test_total_badge_value_calculation(self):
        """Test total badge value calculation"""
        progression = UserProgression(user_id=10)
        
        # Add badges of different rarities
        badges = [
            AchievementBadge.trading_milestone(10),   # Common: 50 * 1.0 = 50
            AchievementBadge.trading_milestone(100),  # Rare: 200 * 1.5 = 300
            AchievementBadge.trading_milestone(1000)  # Epic: 500 * 2.0 = 1000
        ]
        
        for badge in badges:
            progression.unlock_achievement(badge)
        
        expected_total = Decimal('50') + Decimal('300') + Decimal('1000')  # 1350
        self.assertEqual(progression.total_badge_value, expected_total)
    
    def test_rarest_badge_detection(self):
        """Test rarest badge detection"""
        progression = UserProgression(user_id=11)
        
        # Add badges in non-rarity order
        common_badge = AchievementBadge.trading_milestone(10)
        legendary_badge = AchievementBadge.trading_milestone(10000)
        rare_badge = AchievementBadge.trading_milestone(100)
        
        progression.unlock_achievement(common_badge)
        progression.unlock_achievement(legendary_badge)
        progression.unlock_achievement(rare_badge)
        
        # Should return the legendary badge (highest rarity)
        rarest = progression.rarest_badge
        self.assertEqual(rarest, legendary_badge)
        self.assertEqual(rarest.rarity, BadgeRarity.LEGENDARY)
    
    def test_rarest_badge_no_badges(self):
        """Test rarest badge when no badges exist"""
        progression = UserProgression(user_id=12)
        
        rarest = progression.rarest_badge
        self.assertIsNone(rarest)
    
    def test_level_calculation_from_xp(self):
        """Test level calculation based on total XP"""
        test_cases = [
            (Decimal('0'), 1),
            (Decimal('999'), 1),
            (Decimal('1000'), 2),
            (Decimal('1999'), 2),
            (Decimal('2000'), 3),
            (Decimal('5000'), 6),
            (Decimal('10000'), 11),
            (Decimal('99999'), 100)
        ]
        
        for total_xp, expected_level in test_cases:
            progression = UserProgression(user_id=1, total_xp=total_xp)
            progression._calculate_level()
            self.assertEqual(progression.current_level, expected_level)
    
    def test_event_management(self):
        """Test domain event management"""
        progression = UserProgression(user_id=13)
        
        # Initially no events
        self.assertEqual(len(progression.events), 0)
        
        # Award XP to generate events
        xp = ExperiencePoints(amount=Decimal('100'), source=XPSource.TRADING)
        progression.award_xp(xp)
        
        # Should have events
        events = progression.events
        self.assertGreater(len(events), 0)
        
        # Events should be copies (immutable)
        original_count = len(events)
        events.append(MagicMock())  # Modifying copy shouldn't affect entity
        self.assertEqual(len(progression.events), original_count)
        
        # Clear events
        progression.clear_events()
        self.assertEqual(len(progression.events), 0)


class TestConstellation(unittest.TestCase):
    """Comprehensive tests for Constellation entity"""
    
    def test_create_valid_constellation_minimal(self):
        """Test creating Constellation with minimal required parameters"""
        constellation = Constellation(
            constellation_id=1,
            name="Test Constellation",
            description="A test constellation",
            owner_id=123
        )
        
        self.assertEqual(constellation.constellation_id, 1)
        self.assertEqual(constellation.name, "Test Constellation")
        self.assertEqual(constellation.description, "A test constellation")
        self.assertEqual(constellation.owner_id, 123)
        self.assertEqual(constellation.member_count, 0)
        self.assertEqual(constellation.total_stellar_shards, Decimal('0'))
        self.assertEqual(constellation.total_lumina, Decimal('0'))
        self.assertEqual(constellation.constellation_level, 1)
        self.assertEqual(constellation.battle_rating, Decimal('1000'))
        self.assertEqual(constellation.total_battles, 0)
        self.assertEqual(constellation.battles_won, 0)
        self.assertTrue(constellation.is_public)
        self.assertEqual(constellation.max_members, 50)
        self.assertIsInstance(constellation.created_at, datetime)
        self.assertIsInstance(constellation.updated_at, datetime)
        self.assertEqual(len(constellation.events), 0)
    
    def test_create_valid_constellation_full(self):
        """Test creating Constellation with all parameters"""
        created_time = datetime(2023, 1, 1, 12, 0, 0)
        updated_time = datetime(2023, 1, 2, 12, 0, 0)
        
        constellation = Constellation(
            constellation_id=999,
            name="Elite Traders",
            description="Elite trading constellation",
            owner_id=456,
            member_count=25,
            total_stellar_shards=Decimal('50000.75'),
            total_lumina=Decimal('2500.50'),
            constellation_level=5,
            battle_rating=Decimal('1500.25'),
            total_battles=20,
            battles_won=15,
            is_public=False,
            max_members=100,
            created_at=created_time,
            updated_at=updated_time
        )
        
        self.assertEqual(constellation.constellation_id, 999)
        self.assertEqual(constellation.name, "Elite Traders")
        self.assertEqual(constellation.description, "Elite trading constellation")
        self.assertEqual(constellation.owner_id, 456)
        self.assertEqual(constellation.member_count, 25)
        self.assertEqual(constellation.total_stellar_shards, Decimal('50000.75'))
        self.assertEqual(constellation.total_lumina, Decimal('2500.50'))
        self.assertEqual(constellation.constellation_level, 5)
        self.assertEqual(constellation.battle_rating, Decimal('1500.25'))
        self.assertEqual(constellation.total_battles, 20)
        self.assertEqual(constellation.battles_won, 15)
        self.assertFalse(constellation.is_public)
        self.assertEqual(constellation.max_members, 100)
        self.assertEqual(constellation.created_at, created_time)
        self.assertEqual(constellation.updated_at, updated_time)
    
    def test_invalid_constellation_id_validation(self):
        """Test that invalid constellation ID raises ValueError"""
        invalid_ids = [0, -1, -100]
        
        for invalid_id in invalid_ids:
            with self.assertRaises(ValueError) as context:
                Constellation(
                    constellation_id=invalid_id,
                    name="Test",
                    description="Test",
                    owner_id=1
                )
            
            self.assertIn("Constellation ID must be positive", str(context.exception))
    
    def test_empty_name_validation(self):
        """Test that empty or whitespace-only name raises ValueError"""
        invalid_names = ["", "   ", "\t", "\n"]
        
        for invalid_name in invalid_names:
            with self.assertRaises(ValueError) as context:
                Constellation(
                    constellation_id=1,
                    name=invalid_name,
                    description="Test",
                    owner_id=1
                )
            
            self.assertIn("Constellation name cannot be empty", str(context.exception))
    
    def test_invalid_owner_id_validation(self):
        """Test that invalid owner ID raises ValueError"""
        invalid_owner_ids = [0, -1, -100]
        
        for invalid_owner_id in invalid_owner_ids:
            with self.assertRaises(ValueError) as context:
                Constellation(
                    constellation_id=1,
                    name="Test",
                    description="Test",
                    owner_id=invalid_owner_id
                )
            
            self.assertIn("Owner ID must be positive", str(context.exception))
    
    def test_invalid_max_members_validation(self):
        """Test that invalid max members raises ValueError"""
        invalid_max_members = [0, -1, -10]
        
        for invalid_max in invalid_max_members:
            with self.assertRaises(ValueError) as context:
                Constellation(
                    constellation_id=1,
                    name="Test",
                    description="Test",
                    owner_id=1,
                    max_members=invalid_max
                )
            
            self.assertIn("Max members must be positive", str(context.exception))


if __name__ == '__main__':
    # Run with high verbosity to see all test details
    unittest.main(verbosity=2, buffer=True)