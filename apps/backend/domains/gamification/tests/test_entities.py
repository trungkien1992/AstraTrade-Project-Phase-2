import unittest
from decimal import Decimal
from datetime import datetime, timedelta
from unittest.mock import patch

from ..entities import UserProgression, Constellation, Achievement, Leaderboard, Reward
from ..value_objects import (
    ExperiencePoints, AchievementBadge, ConstellationRank, SocialMetrics, 
    RewardPackage, XPSource, AchievementType, BadgeRarity, ConstellationRole
)


class TestUserProgression(unittest.TestCase):
    """Test UserProgression entity"""
    
    def test_create_valid_user_progression(self):
        """Test creating valid user progression"""
        progression = UserProgression(user_id=123)
        
        self.assertEqual(progression.user_id, 123)
        self.assertEqual(progression.total_xp, Decimal('0'))
        self.assertEqual(progression.current_level, 1)
        self.assertEqual(progression.current_streak, 0)
        self.assertEqual(len(progression.achievement_badges), 0)
    
    def test_invalid_user_id_raises_error(self):
        """Test that invalid user ID raises ValueError"""
        with self.assertRaises(ValueError):
            UserProgression(user_id=0)
        
        with self.assertRaises(ValueError):
            UserProgression(user_id=-1)
    
    def test_xp_for_next_level_calculation(self):
        """Test XP required for next level calculation"""
        progression = UserProgression(user_id=1, current_level=5)
        expected_xp = Decimal('5000')  # Level 5 requires 5000 XP
        self.assertEqual(progression.xp_for_next_level, expected_xp)
    
    def test_award_xp_and_level_up(self):
        """Test awarding XP and level up detection"""
        progression = UserProgression(user_id=1)
        
        # Award enough XP to level up
        xp = ExperiencePoints(amount=Decimal('1500'), source=XPSource.TRADING)
        level_up = progression.award_xp(xp)
        
        self.assertTrue(level_up)
        self.assertEqual(progression.current_level, 2)  # Should level up from 1 to 2
        self.assertEqual(progression.total_xp, Decimal('1500'))
        
        # Check that event was emitted
        events = progression.events
        self.assertEqual(len(events), 2)  # XP awarded + level up events
        self.assertEqual(events[0].event_type, "xp_awarded")
        self.assertEqual(events[1].event_type, "level_up")
    
    def test_award_xp_no_level_up(self):
        """Test awarding XP without level up"""
        progression = UserProgression(user_id=1)
        
        # Award small amount of XP
        xp = ExperiencePoints(amount=Decimal('500'), source=XPSource.SOCIAL)
        level_up = progression.award_xp(xp)
        
        self.assertFalse(level_up)
        self.assertEqual(progression.current_level, 1)  # Should stay at level 1
        self.assertEqual(progression.total_xp, Decimal('500'))
        
        # Check that only XP awarded event was emitted
        events = progression.events
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].event_type, "xp_awarded")
    
    def test_unlock_achievement(self):
        """Test unlocking an achievement"""
        progression = UserProgression(user_id=1)
        badge = AchievementBadge.trading_milestone(10)
        
        # Unlock achievement
        reward_package = progression.unlock_achievement(badge)
        
        # Check achievement was added
        self.assertIn(badge, progression.achievement_badges)
        
        # Check rewards were applied
        self.assertEqual(progression.stellar_shards, badge.currency_reward['stellar_shards'])
        
        # Check reward package
        self.assertEqual(reward_package.xp_reward, badge.total_xp_reward)
        
        # Check event was emitted
        events = progression.events
        achievement_event = next(e for e in events if e.event_type == "achievement_unlocked")
        self.assertEqual(achievement_event.data['achievement_name'], badge.name)
    
    def test_unlock_duplicate_achievement_raises_error(self):
        """Test that unlocking duplicate achievement raises error"""
        progression = UserProgression(user_id=1)
        badge = AchievementBadge.trading_milestone(10)
        
        # Unlock achievement first time
        progression.unlock_achievement(badge)
        
        # Try to unlock same achievement again
        with self.assertRaises(ValueError) as context:
            progression.unlock_achievement(badge)
        self.assertIn("already unlocked", str(context.exception))
    
    def test_update_streak_consecutive_days(self):
        """Test streak update for consecutive days"""
        progression = UserProgression(user_id=1)
        
        # First activity
        with patch('apps.backend.domains.gamification.entities.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = datetime(2023, 1, 1, 12, 0, 0)
            updated = progression.update_streak()
            
            self.assertTrue(updated)
            self.assertEqual(progression.current_streak, 1)
            self.assertEqual(progression.best_streak, 1)
        
        # Next day activity
        with patch('apps.backend.domains.gamification.entities.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = datetime(2023, 1, 2, 12, 0, 0)
            # Set last activity to yesterday
            progression.last_activity_date = datetime(2023, 1, 1, 12, 0, 0)
            
            updated = progression.update_streak()
            
            self.assertTrue(updated)
            self.assertEqual(progression.current_streak, 2)
            self.assertEqual(progression.best_streak, 2)
            
            # Check streak updated event
            events = progression.events
            streak_event = next(e for e in events if e.event_type == "streak_updated")
            self.assertEqual(streak_event.data['current_streak'], 2)
    
    def test_update_streak_broken(self):
        """Test streak breaking after gap"""
        progression = UserProgression(user_id=1, current_streak=5, best_streak=5)
        
        with patch('apps.backend.domains.gamification.entities.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = datetime(2023, 1, 5, 12, 0, 0)
            # Set last activity to 3 days ago (gap of 2 days breaks streak)
            progression.last_activity_date = datetime(2023, 1, 2, 12, 0, 0)
            
            updated = progression.update_streak()
            
            self.assertTrue(updated)
            self.assertEqual(progression.current_streak, 1)  # Reset to 1
            self.assertEqual(progression.best_streak, 5)     # Best streak unchanged
            
            # Check streak broken event
            events = progression.events
            streak_event = next(e for e in events if e.event_type == "streak_broken")
            self.assertEqual(streak_event.data['best_streak'], 5)
    
    def test_rarest_badge_detection(self):
        """Test rarest badge detection"""
        progression = UserProgression(user_id=1)
        
        # Add badges of different rarities
        common_badge = AchievementBadge(
            achievement_type=AchievementType.TRADING_MILESTONE,
            name="Common",
            description="Common",
            rarity=BadgeRarity.COMMON,
            xp_reward=Decimal('10'),
            currency_reward={},
            unlock_conditions={},
            icon_id="common"
        )
        
        epic_badge = AchievementBadge(
            achievement_type=AchievementType.PROFIT_THRESHOLD,
            name="Epic",
            description="Epic",
            rarity=BadgeRarity.EPIC,
            xp_reward=Decimal('100'),
            currency_reward={},
            unlock_conditions={},
            icon_id="epic"
        )
        
        progression.achievement_badges = [common_badge, epic_badge]
        
        rarest = progression.rarest_badge
        self.assertEqual(rarest, epic_badge)  # Epic is rarer than common
    
    def test_level_calculation_from_xp(self):
        """Test level calculation based on total XP"""
        progression = UserProgression(user_id=1)
        
        # Test various XP amounts and expected levels
        test_cases = [
            (Decimal('0'), 1),
            (Decimal('999'), 1),
            (Decimal('1000'), 2),
            (Decimal('2500'), 3),
            (Decimal('5000'), 6),
            (Decimal('10000'), 11)
        ]
        
        for total_xp, expected_level in test_cases:
            progression.total_xp = total_xp
            progression._calculate_level()
            self.assertEqual(progression.current_level, expected_level)


class TestConstellation(unittest.TestCase):
    """Test Constellation entity"""
    
    def test_create_valid_constellation(self):
        """Test creating valid constellation"""
        constellation = Constellation(
            constellation_id=1,
            name="Test Constellation",
            description="A test constellation",
            owner_id=123
        )
        
        self.assertEqual(constellation.constellation_id, 1)
        self.assertEqual(constellation.name, "Test Constellation")
        self.assertEqual(constellation.owner_id, 123)
        self.assertEqual(constellation.member_count, 0)
        self.assertEqual(constellation.battle_rating, Decimal('1000'))
    
    def test_invalid_constellation_data_raises_errors(self):
        """Test that invalid constellation data raises errors"""
        # Invalid ID
        with self.assertRaises(ValueError):
            Constellation(constellation_id=0, name="Test", description="Test", owner_id=1)
        
        # Empty name
        with self.assertRaises(ValueError):
            Constellation(constellation_id=1, name="", description="Test", owner_id=1)
        
        # Invalid owner ID
        with self.assertRaises(ValueError):
            Constellation(constellation_id=1, name="Test", description="Test", owner_id=0)
    
    def test_add_member(self):
        """Test adding a member to constellation"""
        constellation = Constellation(
            constellation_id=1,
            name="Test",
            description="Test",
            owner_id=123
        )
        
        member_rank = constellation.add_member(456)
        
        self.assertEqual(constellation.member_count, 1)
        self.assertEqual(member_rank.role, ConstellationRole.RECRUIT)
        
        # Check member joined event
        events = constellation.events
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].event_type, "member_joined")
        self.assertEqual(events[0].data['user_id'], 456)
    
    def test_add_member_when_full_raises_error(self):
        """Test adding member when constellation is full"""
        constellation = Constellation(
            constellation_id=1,
            name="Test",
            description="Test",
            owner_id=123,
            member_count=50,  # At max capacity
            max_members=50
        )
        
        with self.assertRaises(ValueError) as context:
            constellation.add_member(456)
        self.assertIn("maximum capacity", str(context.exception))
    
    def test_remove_member(self):
        """Test removing a member from constellation"""
        constellation = Constellation(
            constellation_id=1,
            name="Test",
            description="Test",
            owner_id=123,
            member_count=3
        )
        
        constellation.remove_member(456)
        
        self.assertEqual(constellation.member_count, 2)
        
        # Check member left event
        events = constellation.events
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].event_type, "member_left")
        self.assertEqual(events[0].data['user_id'], 456)
    
    def test_update_contribution(self):
        """Test updating constellation contributions"""
        constellation = Constellation(
            constellation_id=1,
            name="Test",
            description="Test",
            owner_id=123
        )
        
        constellation.update_contribution(Decimal('1000'), Decimal('50'))
        
        self.assertEqual(constellation.total_stellar_shards, Decimal('1000'))
        self.assertEqual(constellation.total_lumina, Decimal('50'))
        
        # Check contribution updated event
        events = constellation.events
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].event_type, "contribution_updated")
    
    def test_record_battle_result(self):
        """Test recording battle results"""
        constellation = Constellation(
            constellation_id=1,
            name="Test",
            description="Test",
            owner_id=123
        )
        
        # Record a victory
        constellation.record_battle_result(won=True, rating_change=Decimal('25'))
        
        self.assertEqual(constellation.total_battles, 1)
        self.assertEqual(constellation.battles_won, 1)
        self.assertEqual(constellation.battle_rating, Decimal('1025'))
        self.assertEqual(constellation.win_rate, Decimal('100'))  # 100% win rate
        
        # Record a loss
        constellation.record_battle_result(won=False, rating_change=Decimal('-15'))
        
        self.assertEqual(constellation.total_battles, 2)
        self.assertEqual(constellation.battles_won, 1)
        self.assertEqual(constellation.battle_rating, Decimal('1010'))
        self.assertEqual(constellation.win_rate, Decimal('50'))  # 50% win rate
    
    def test_constellation_level_calculation(self):
        """Test constellation level calculation based on contributions"""
        constellation = Constellation(
            constellation_id=1,
            name="Test",
            description="Test",
            owner_id=123
        )
        
        # Add contributions that should level up constellation
        constellation.total_stellar_shards = Decimal('25000')  # Level 3
        constellation.total_lumina = Decimal('1000')           # = 10000 shards, so total 35000
        constellation._calculate_level()
        
        expected_level = int(Decimal('35000') // 10000) + 1  # Level 4
        self.assertEqual(constellation.constellation_level, expected_level)


class TestAchievement(unittest.TestCase):
    """Test Achievement entity"""
    
    def test_create_valid_achievement(self):
        """Test creating valid achievement"""
        badge = AchievementBadge.trading_milestone(10)
        achievement = Achievement(achievement_id="first_steps", badge=badge)
        
        self.assertEqual(achievement.achievement_id, "first_steps")
        self.assertEqual(achievement.badge, badge)
        self.assertTrue(achievement.is_active)
        self.assertEqual(achievement.unlock_count, 0)
    
    def test_check_unlock_conditions(self):
        """Test checking unlock conditions"""
        badge = AchievementBadge(
            achievement_type=AchievementType.TRADING_MILESTONE,
            name="Test",
            description="Test",
            rarity=BadgeRarity.COMMON,
            xp_reward=Decimal('10'),
            currency_reward={},
            unlock_conditions={
                'trade_count': 10,
                'total_profit_loss': Decimal('100'),
                'trading_style': 'aggressive'
            },
            icon_id="test"
        )
        
        achievement = Achievement(achievement_id="test", badge=badge)
        
        # User meets all conditions
        user_data = {
            'trade_count': 15,
            'total_profit_loss': Decimal('150'),
            'trading_style': 'aggressive'
        }
        self.assertTrue(achievement.check_unlock_conditions(user_data))
        
        # User doesn't meet numeric condition
        user_data['trade_count'] = 5
        self.assertFalse(achievement.check_unlock_conditions(user_data))
        
        # User doesn't meet string condition
        user_data['trade_count'] = 15
        user_data['trading_style'] = 'conservative'
        self.assertFalse(achievement.check_unlock_conditions(user_data))
    
    def test_record_unlock(self):
        """Test recording achievement unlock"""
        badge = AchievementBadge.trading_milestone(10)
        achievement = Achievement(achievement_id="test", badge=badge)
        
        achievement.record_unlock(user_id=123)
        
        self.assertEqual(achievement.unlock_count, 1)
        
        # Check unlock recorded event
        events = achievement.events
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].event_type, "achievement_unlock_recorded")
        self.assertEqual(events[0].data['user_id'], 123)


class TestLeaderboard(unittest.TestCase):
    """Test Leaderboard entity"""
    
    def test_create_valid_leaderboard(self):
        """Test creating valid leaderboard"""
        leaderboard = Leaderboard(
            leaderboard_id="xp_daily",
            name="Daily XP Leaders",
            description="Top XP earners today",
            leaderboard_type="individual",
            time_period="daily"
        )
        
        self.assertEqual(leaderboard.leaderboard_id, "xp_daily")
        self.assertEqual(leaderboard.name, "Daily XP Leaders")
        self.assertEqual(leaderboard.time_period, "daily")
        self.assertTrue(leaderboard.is_active)
    
    def test_should_reset_daily(self):
        """Test daily leaderboard reset logic"""
        leaderboard = Leaderboard(
            leaderboard_id="test",
            name="Test",
            description="Test",
            leaderboard_type="individual",
            time_period="daily"
        )
        
        # Set last updated to yesterday
        yesterday = datetime.utcnow() - timedelta(days=1)
        leaderboard.last_updated = yesterday
        
        self.assertTrue(leaderboard.should_reset())
        
        # Set last updated to today
        leaderboard.last_updated = datetime.utcnow()
        self.assertFalse(leaderboard.should_reset())
    
    def test_should_reset_weekly(self):
        """Test weekly leaderboard reset logic"""
        leaderboard = Leaderboard(
            leaderboard_id="test",
            name="Test",
            description="Test",
            leaderboard_type="individual",
            time_period="weekly"
        )
        
        # Set last updated to more than a week ago on a Monday
        with patch('apps.backend.domains.gamification.entities.datetime') as mock_datetime:
            # Mock current time as Monday
            mock_datetime.utcnow.return_value = datetime(2023, 1, 9, 12, 0, 0)  # Monday
            mock_datetime.utcnow.return_value.weekday.return_value = 0  # Monday
            
            # Set last update to over a week ago
            leaderboard.last_updated = datetime(2023, 1, 1, 12, 0, 0)
            
            self.assertTrue(leaderboard.should_reset())
    
    def test_reset_leaderboard(self):
        """Test resetting leaderboard"""
        leaderboard = Leaderboard(
            leaderboard_id="test",
            name="Test",
            description="Test",
            leaderboard_type="individual",
            time_period="daily"
        )
        
        old_update_time = leaderboard.last_updated
        leaderboard.reset()
        
        self.assertGreater(leaderboard.last_updated, old_update_time)
        
        # Check reset event
        events = leaderboard.events
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].event_type, "leaderboard_reset")


class TestReward(unittest.TestCase):
    """Test Reward entity"""
    
    def test_create_valid_reward(self):
        """Test creating valid reward"""
        reward_package = RewardPackage(
            xp_reward=Decimal('100'),
            stellar_shards=Decimal('200'),
            lumina=Decimal('10'),
            stardust=Decimal('0'),
            badges=[],
            nft_artifacts=[],
            special_items={},
            reward_description="Test reward"
        )
        
        reward = Reward(
            reward_id="reward_123",
            user_id=123,
            reward_package=reward_package,
            source_type="achievement",
            source_id="first_trade"
        )
        
        self.assertEqual(reward.reward_id, "reward_123")
        self.assertEqual(reward.user_id, 123)
        self.assertEqual(reward.source_type, "achievement")
        self.assertFalse(reward.is_claimed)
        self.assertTrue(reward.can_be_claimed)
    
    def test_claim_reward(self):
        """Test claiming a reward"""
        reward_package = RewardPackage(
            xp_reward=Decimal('100'),
            stellar_shards=Decimal('200'),
            lumina=Decimal('10'),
            stardust=Decimal('0'),
            badges=[],
            nft_artifacts=[],
            special_items={},
            reward_description="Test reward"
        )
        
        reward = Reward(
            reward_id="reward_123",
            user_id=123,
            reward_package=reward_package,
            source_type="achievement",
            source_id="first_trade"
        )
        
        claimed_package = reward.claim()
        
        self.assertTrue(reward.is_claimed)
        self.assertIsNotNone(reward.claimed_at)
        self.assertFalse(reward.can_be_claimed)
        self.assertEqual(claimed_package, reward_package)
        
        # Check reward claimed event
        events = reward.events
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].event_type, "reward_claimed")
    
    def test_claim_already_claimed_reward_raises_error(self):
        """Test claiming already claimed reward raises error"""
        reward_package = RewardPackage(
            xp_reward=Decimal('100'),
            stellar_shards=Decimal('200'),
            lumina=Decimal('10'),
            stardust=Decimal('0'),
            badges=[],
            nft_artifacts=[],
            special_items={},
            reward_description="Test reward"
        )
        
        reward = Reward(
            reward_id="reward_123",
            user_id=123,
            reward_package=reward_package,
            source_type="achievement",
            source_id="first_trade",
            is_claimed=True
        )
        
        with self.assertRaises(ValueError) as context:
            reward.claim()
        self.assertIn("already been claimed", str(context.exception))
    
    def test_expired_reward(self):
        """Test expired reward handling"""
        reward_package = RewardPackage(
            xp_reward=Decimal('100'),
            stellar_shards=Decimal('200'),
            lumina=Decimal('10'),
            stardust=Decimal('0'),
            badges=[],
            nft_artifacts=[],
            special_items={},
            reward_description="Test reward"
        )
        
        # Create reward that expires in the past
        expired_time = datetime.utcnow() - timedelta(hours=1)
        reward = Reward(
            reward_id="reward_123",
            user_id=123,
            reward_package=reward_package,
            source_type="achievement",
            source_id="first_trade",
            expires_at=expired_time
        )
        
        self.assertTrue(reward.is_expired)
        self.assertFalse(reward.can_be_claimed)
        
        # Try to claim expired reward
        with self.assertRaises(ValueError) as context:
            reward.claim()
        self.assertIn("expired", str(context.exception))


if __name__ == '__main__':
    unittest.main()