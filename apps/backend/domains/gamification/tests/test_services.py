import unittest
from decimal import Decimal
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from typing import List, Optional

from ..services import GamificationDomainService, UserStats
from ..entities import UserProgression, Constellation, Achievement, Leaderboard, Reward
from ..value_objects import (
    ExperiencePoints, AchievementBadge, ConstellationRank, SocialMetrics, 
    RewardPackage, XPSource, AchievementType, BadgeRarity, ConstellationRole
)


class MockUserProgressionRepository:
    """Mock repository for user progression"""
    
    def __init__(self):
        self.data = {}
        self.next_id = 1
    
    async def get_by_user_id(self, user_id: int) -> Optional[UserProgression]:
        return self.data.get(user_id)
    
    async def save(self, progression: UserProgression) -> UserProgression:
        self.data[progression.user_id] = progression
        return progression
    
    async def get_top_users_by_xp(self, limit: int = 10) -> List[UserProgression]:
        sorted_users = sorted(self.data.values(), key=lambda u: u.total_xp, reverse=True)
        return sorted_users[:limit]
    
    async def get_user_rank_by_xp(self, user_id: int) -> int:
        sorted_users = sorted(self.data.values(), key=lambda u: u.total_xp, reverse=True)
        for rank, user in enumerate(sorted_users, 1):
            if user.user_id == user_id:
                return rank
        return 0


class MockConstellationRepository:
    """Mock repository for constellations"""
    
    def __init__(self):
        self.data = {}
        self.user_constellation_map = {}
    
    async def get_by_id(self, constellation_id: int) -> Optional[Constellation]:
        return self.data.get(constellation_id)
    
    async def get_by_user_id(self, user_id: int) -> Optional[Constellation]:
        constellation_id = self.user_constellation_map.get(user_id)
        return self.data.get(constellation_id) if constellation_id else None
    
    async def save(self, constellation: Constellation) -> Constellation:
        self.data[constellation.constellation_id] = constellation
        return constellation
    
    async def get_top_by_rating(self, limit: int = 10) -> List[Constellation]:
        sorted_constellations = sorted(self.data.values(), key=lambda c: c.battle_rating, reverse=True)
        return sorted_constellations[:limit]
    
    async def search_public(self, query: str, limit: int = 20) -> List[Constellation]:
        results = [c for c in self.data.values() if query.lower() in c.name.lower() and c.is_public]
        return results[:limit]


class MockAchievementRepository:
    """Mock repository for achievements"""
    
    def __init__(self):
        self.data = {}
        self.user_achievements = {}
    
    async def get_by_id(self, achievement_id: str) -> Optional[Achievement]:
        return self.data.get(achievement_id)
    
    async def get_all_active(self) -> List[Achievement]:
        return [a for a in self.data.values() if a.is_active]
    
    async def save(self, achievement: Achievement) -> Achievement:
        self.data[achievement.achievement_id] = achievement
        return achievement
    
    async def get_user_achievements(self, user_id: int) -> List[Achievement]:
        return self.user_achievements.get(user_id, [])


class MockLeaderboardRepository:
    """Mock repository for leaderboards"""
    
    def __init__(self):
        self.data = {}
        self.entries = {}
    
    async def get_by_id(self, leaderboard_id: str) -> Optional[Leaderboard]:
        return self.data.get(leaderboard_id)
    
    async def get_active_leaderboards(self) -> List[Leaderboard]:
        return [lb for lb in self.data.values() if lb.is_active]
    
    async def save(self, leaderboard: Leaderboard) -> Leaderboard:
        self.data[leaderboard.leaderboard_id] = leaderboard
        return leaderboard
    
    async def get_leaderboard_entries(self, leaderboard_id: str, limit: int = 100) -> List[dict]:
        return self.entries.get(leaderboard_id, [])[:limit]
    
    async def update_leaderboard_entries(self, leaderboard_id: str, entries: List[dict]):
        self.entries[leaderboard_id] = entries


class MockRewardRepository:
    """Mock repository for rewards"""
    
    def __init__(self):
        self.data = {}
    
    async def get_by_id(self, reward_id: str) -> Optional[Reward]:
        return self.data.get(reward_id)
    
    async def save(self, reward: Reward) -> Reward:
        self.data[reward.reward_id] = reward
        return reward
    
    async def get_unclaimed_by_user(self, user_id: int) -> List[Reward]:
        return [r for r in self.data.values() if r.user_id == user_id and not r.is_claimed]
    
    async def get_expired_rewards(self) -> List[Reward]:
        now = datetime.utcnow()
        return [r for r in self.data.values() if r.expires_at and r.expires_at < now]


class TestGamificationDomainService(unittest.IsolatedAsyncioTestCase):
    """Test GamificationDomainService integration"""
    
    def setUp(self):
        """Set up test dependencies"""
        self.user_progression_repo = MockUserProgressionRepository()
        self.constellation_repo = MockConstellationRepository()
        self.achievement_repo = MockAchievementRepository()
        self.leaderboard_repo = MockLeaderboardRepository()
        self.reward_repo = MockRewardRepository()
        
        self.service = GamificationDomainService(
            user_progression_repo=self.user_progression_repo,
            constellation_repo=self.constellation_repo,
            achievement_repo=self.achievement_repo,
            leaderboard_repo=self.leaderboard_repo,
            reward_repo=self.reward_repo
        )
    
    async def test_get_user_progression_creates_new_user(self):
        """Test getting user progression creates new user if not exists"""
        user_id = 123
        
        progression = await self.service.get_user_progression(user_id)
        
        self.assertIsNotNone(progression)
        self.assertEqual(progression.user_id, user_id)
        self.assertEqual(progression.total_xp, Decimal('0'))
        self.assertEqual(progression.current_level, 1)
    
    async def test_award_trading_xp_with_level_up(self):
        """Test awarding trading XP that causes level up"""
        user_id = 123
        trade_volume = Decimal('10000')  # Large volume
        profit_loss = Decimal('500')     # Profitable trade
        
        progression, level_up = await self.service.award_trading_xp(user_id, trade_volume, profit_loss)
        
        # Check XP calculation: (10000 * 0.1) + (500 * 0.5) = 1000 + 250 = 1250
        expected_xp = Decimal('1250')
        self.assertEqual(progression.total_xp, expected_xp)
        self.assertTrue(level_up)  # Should level up from 1 to 2
        self.assertEqual(progression.current_level, 2)
        self.assertEqual(progression.current_streak, 1)  # Trading XP updates streak
    
    async def test_award_social_xp(self):
        """Test awarding social XP"""
        user_id = 123
        activity_type = "viral_meme"
        engagement_score = Decimal('50')
        
        progression, level_up = await self.service.award_social_xp(user_id, activity_type, engagement_score)
        
        # Check XP calculation: 50 * 2.0 = 100
        expected_xp = Decimal('100')
        self.assertEqual(progression.total_xp, expected_xp)
        self.assertFalse(level_up)  # Should not level up
        # Social XP doesn't update streak
    
    async def test_check_achievements_unlocks_milestone(self):
        """Test checking achievements unlocks trading milestone"""
        user_id = 123
        
        # Create and save a trading milestone achievement
        badge = AchievementBadge.trading_milestone(10)
        achievement = Achievement(achievement_id="first_steps", badge=badge)
        await self.achievement_repo.save(achievement)
        
        # Create user stats that meet the achievement
        user_stats = UserStats(
            user_id=user_id,
            total_trades=15,  # Meets requirement of 10
            successful_trades=10,
            total_profit_loss=Decimal('100'),
            current_streak=3,
            best_streak=5,
            vault_deposits=0,
            vault_total_deposited=Decimal('0'),
            social_shares=0,
            constellation_battles=0,
            referrals_made=0
        )
        
        rewards = await self.service.check_achievements(user_id, user_stats)
        
        # Check that achievement was unlocked
        self.assertEqual(len(rewards), 1)
        reward = rewards[0]
        self.assertEqual(reward.xp_reward, badge.total_xp_reward)
        
        # Check that user progression was updated
        progression = await self.service.get_user_progression(user_id)
        self.assertIn(badge, progression.achievement_badges)
        self.assertEqual(progression.stellar_shards, badge.currency_reward['stellar_shards'])
        
        # Check that achievement unlock count was incremented
        updated_achievement = await self.achievement_repo.get_by_id("first_steps")
        self.assertEqual(updated_achievement.unlock_count, 1)
    
    async def test_check_achievements_no_duplicates(self):
        """Test that already unlocked achievements are not unlocked again"""
        user_id = 123
        
        # Create achievement and unlock it first time
        badge = AchievementBadge.trading_milestone(10)
        achievement = Achievement(achievement_id="first_steps", badge=badge)
        await self.achievement_repo.save(achievement)
        
        # First unlock
        user_stats = UserStats(
            user_id=user_id,
            total_trades=15,
            successful_trades=10,
            total_profit_loss=Decimal('100'),
            current_streak=3,
            best_streak=5,
            vault_deposits=0,
            vault_total_deposited=Decimal('0'),
            social_shares=0,
            constellation_battles=0,
            referrals_made=0
        )
        
        rewards1 = await self.service.check_achievements(user_id, user_stats)
        self.assertEqual(len(rewards1), 1)
        
        # Second check should not unlock again
        rewards2 = await self.service.check_achievements(user_id, user_stats)
        self.assertEqual(len(rewards2), 0)  # No new unlocks
    
    async def test_create_constellation(self):
        """Test creating a new constellation"""
        name = "Test Constellation"
        description = "A test constellation for unit testing"
        owner_id = 123
        
        constellation = await self.service.create_constellation(name, description, owner_id)
        
        self.assertEqual(constellation.name, name)
        self.assertEqual(constellation.description, description)
        self.assertEqual(constellation.owner_id, owner_id)
        self.assertEqual(constellation.member_count, 1)  # Owner is first member
        
        # Check that constellation was saved
        saved_constellation = await self.constellation_repo.get_by_id(constellation.constellation_id)
        self.assertEqual(saved_constellation, constellation)
    
    async def test_join_constellation(self):
        """Test joining a constellation"""
        # Create constellation first
        constellation = await self.service.create_constellation("Test", "Test", 123)
        user_id = 456
        
        member_rank = await self.service.join_constellation(user_id, constellation.constellation_id)
        
        self.assertEqual(member_rank.role, ConstellationRole.RECRUIT)
        
        # Check that constellation member count increased
        updated_constellation = await self.constellation_repo.get_by_id(constellation.constellation_id)
        self.assertEqual(updated_constellation.member_count, 2)  # Owner + new member
    
    async def test_join_constellation_already_member_raises_error(self):
        """Test joining constellation when already in one raises error"""
        # Create two constellations
        constellation1 = await self.service.create_constellation("Test1", "Test1", 123)
        constellation2 = await self.service.create_constellation("Test2", "Test2", 456)
        
        user_id = 789
        
        # Join first constellation
        await self.service.join_constellation(user_id, constellation1.constellation_id)
        # Set up mock to return constellation1 for this user
        self.constellation_repo.user_constellation_map[user_id] = constellation1.constellation_id
        
        # Try to join second constellation
        with self.assertRaises(ValueError) as context:
            await self.service.join_constellation(user_id, constellation2.constellation_id)
        self.assertIn("already in a constellation", str(context.exception))
    
    async def test_get_xp_leaderboard(self):
        """Test getting XP leaderboard"""
        # Create multiple users with different XP
        users_xp = [(1, Decimal('5000')), (2, Decimal('3000')), (3, Decimal('7000')), (4, Decimal('1000'))]
        
        for user_id, xp in users_xp:
            progression = UserProgression(user_id=user_id, total_xp=xp)
            await self.user_progression_repo.save(progression)
        
        leaderboard = await self.service.get_xp_leaderboard(limit=3)
        
        # Check that leaderboard is sorted by XP (descending)
        self.assertEqual(len(leaderboard), 3)
        self.assertEqual(leaderboard[0]['user_id'], 3)  # Highest XP (7000)
        self.assertEqual(leaderboard[0]['rank'], 1)
        self.assertEqual(leaderboard[1]['user_id'], 1)  # Second highest (5000)
        self.assertEqual(leaderboard[1]['rank'], 2)
        self.assertEqual(leaderboard[2]['user_id'], 2)  # Third highest (3000)
        self.assertEqual(leaderboard[2]['rank'], 3)
    
    async def test_calculate_constellation_battle_score(self):
        """Test calculating constellation battle score"""
        constellation_id = 1
        
        # Create member stats
        member_stats = [
            UserStats(
                user_id=1,
                total_trades=50,
                successful_trades=40,  # 400 points
                total_profit_loss=Decimal('200'),  # 20 points
                current_streak=5,  # 25 points
                best_streak=10,
                vault_deposits=0,
                vault_total_deposited=Decimal('0'),
                social_shares=0,
                constellation_battles=0,
                referrals_made=0
            ),
            UserStats(
                user_id=2,
                total_trades=30,
                successful_trades=25,  # 250 points
                total_profit_loss=Decimal('-50'),  # Negative, contributes 0
                current_streak=2,  # 10 points
                best_streak=5,
                vault_deposits=0,
                vault_total_deposited=Decimal('0'),
                social_shares=0,
                constellation_battles=0,
                referrals_made=0
            )
        ]
        
        score = await self.service.calculate_constellation_battle_score(constellation_id, member_stats)
        
        # Member 1: 40*10 + 200*0.1 + 5*5 = 400 + 20 + 25 = 445
        # Member 2: 25*10 + max(-5, 0) + 2*5 = 250 + 0 + 10 = 260
        # Total: 445 + 260 = 705
        expected_score = Decimal('705')
        self.assertEqual(score, expected_score)
    
    async def test_distribute_and_claim_reward(self):
        """Test distributing and claiming rewards"""
        user_id = 123
        
        # Create reward package
        reward_package = RewardPackage(
            xp_reward=Decimal('100'),
            stellar_shards=Decimal('500'),
            lumina=Decimal('25'),
            stardust=Decimal('1'),
            badges=[],
            nft_artifacts=[],
            special_items={'bonus': True},
            reward_description="Test reward"
        )
        
        # Distribute reward
        reward = await self.service.distribute_reward(
            user_id=user_id,
            reward_package=reward_package,
            source_type="achievement",
            source_id="test_achievement",
            expires_in_hours=24
        )
        
        self.assertEqual(reward.user_id, user_id)
        self.assertEqual(reward.source_type, "achievement")
        self.assertFalse(reward.is_claimed)
        self.assertTrue(reward.can_be_claimed)
        
        # Claim reward
        claimed_package = await self.service.claim_reward(reward.reward_id)
        
        self.assertEqual(claimed_package, reward_package)
        
        # Check that user progression was updated with rewards
        progression = await self.service.get_user_progression(user_id)
        self.assertEqual(progression.stellar_shards, reward_package.stellar_shards)
        self.assertEqual(progression.lumina, reward_package.lumina)
        self.assertEqual(progression.stardust, reward_package.stardust)
        # XP should be awarded too
        self.assertEqual(progression.total_xp, reward_package.xp_reward)
    
    async def test_calculate_viral_score(self):
        """Test calculating viral score for content"""
        content_type = "constellation_battle"
        share_count = 20
        engagement_data = {
            'likes': 100,
            'comments': 15,
            'reshares': 5
        }
        
        viral_score = await self.service.calculate_viral_score(content_type, share_count, engagement_data)
        
        # Base score: 20 * 10 = 200
        # Engagement bonus: 100*2 + 15*5 + 5*15 = 200 + 75 + 75 = 350
        # Content multiplier: 2.0 (for constellation_battle)
        # Total: (200 + 350) * 2.0 = 1100
        expected_score = Decimal('1100')
        self.assertEqual(viral_score, expected_score)
    
    async def test_award_viral_content_rewards(self):
        """Test awarding rewards for viral content"""
        user_id = 123
        viral_score = Decimal('500')  # Above minimum threshold of 100
        
        reward_package = await self.service.award_viral_content_rewards(user_id, viral_score)
        
        self.assertIsNotNone(reward_package)
        
        # Check reward calculations
        expected_shards = viral_score * Decimal('0.5')  # 250
        expected_lumina = viral_score * Decimal('0.05')  # 25
        expected_xp = viral_score * Decimal('2')  # 1000
        
        self.assertEqual(reward_package.stellar_shards, expected_shards)
        self.assertEqual(reward_package.lumina, expected_lumina)
        self.assertEqual(reward_package.xp_reward, expected_xp)
        
        # Check that reward was distributed (saved to repo)
        unclaimed_rewards = await self.service.get_unclaimed_rewards(user_id)
        self.assertEqual(len(unclaimed_rewards), 1)
        self.assertEqual(unclaimed_rewards[0].source_type, "viral_content")
    
    async def test_award_viral_content_rewards_below_threshold(self):
        """Test that viral content below threshold gets no rewards"""
        user_id = 123
        viral_score = Decimal('50')  # Below minimum threshold of 100
        
        reward_package = await self.service.award_viral_content_rewards(user_id, viral_score)
        
        self.assertIsNone(reward_package)
        
        # Check that no reward was distributed
        unclaimed_rewards = await self.service.get_unclaimed_rewards(user_id)
        self.assertEqual(len(unclaimed_rewards), 0)


if __name__ == '__main__':
    unittest.main()