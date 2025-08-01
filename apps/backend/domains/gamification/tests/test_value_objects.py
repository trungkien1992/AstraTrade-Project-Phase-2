import unittest
from decimal import Decimal
from datetime import datetime

from ..value_objects import (
    ExperiencePoints, AchievementBadge, ConstellationRank, SocialMetrics, 
    RewardPackage, XPSource, AchievementType, BadgeRarity, ConstellationRole
)


class TestExperiencePoints(unittest.TestCase):
    """Test ExperiencePoints value object"""
    
    def test_create_valid_xp(self):
        """Test creating valid XP"""
        xp = ExperiencePoints(
            amount=Decimal('100'),
            source=XPSource.TRADING,
            multiplier=Decimal('1.5'),
            bonus_description="Profit bonus"
        )
        
        self.assertEqual(xp.amount, Decimal('100'))
        self.assertEqual(xp.source, XPSource.TRADING)
        self.assertEqual(xp.multiplier, Decimal('1.5'))
        self.assertEqual(xp.total_xp, Decimal('150'))
        self.assertEqual(xp.bonus_description, "Profit bonus")
    
    def test_negative_amount_raises_error(self):
        """Test that negative XP amount raises ValueError"""
        with self.assertRaises(ValueError) as context:
            ExperiencePoints(amount=Decimal('-10'), source=XPSource.TRADING)
        self.assertIn("cannot be negative", str(context.exception))
    
    def test_negative_multiplier_raises_error(self):
        """Test that negative multiplier raises ValueError"""
        with self.assertRaises(ValueError) as context:
            ExperiencePoints(
                amount=Decimal('100'), 
                source=XPSource.TRADING, 
                multiplier=Decimal('-0.5')
            )
        self.assertIn("cannot be negative", str(context.exception))
    
    def test_trading_xp_calculation(self):
        """Test trading XP calculation with profit bonus"""
        # Profitable trade
        xp = ExperiencePoints.trading_xp(
            trade_volume=Decimal('1000'),
            profit_loss=Decimal('50')
        )
        
        expected_base = Decimal('1000') * Decimal('0.1')  # 100
        expected_bonus = Decimal('50') * Decimal('0.5')   # 25
        expected_total = expected_base + expected_bonus    # 125
        
        self.assertEqual(xp.amount, expected_total)
        self.assertEqual(xp.source, XPSource.TRADING)
        self.assertIn("Profit bonus", xp.bonus_description)
    
    def test_trading_xp_no_profit_bonus(self):
        """Test trading XP calculation with loss (no bonus)"""
        xp = ExperiencePoints.trading_xp(
            trade_volume=Decimal('1000'),
            profit_loss=Decimal('-50')  # Loss
        )
        
        expected_amount = Decimal('1000') * Decimal('0.1')  # 100, no bonus
        self.assertEqual(xp.amount, expected_amount)
        self.assertIsNone(xp.bonus_description)
    
    def test_social_xp_calculation(self):
        """Test social XP calculation"""
        xp = ExperiencePoints.social_xp(
            activity_type="meme_share",
            engagement_score=Decimal('25')
        )
        
        expected_amount = Decimal('25') * Decimal('2.0')  # 50
        self.assertEqual(xp.amount, expected_amount)
        self.assertEqual(xp.source, XPSource.SOCIAL)
        self.assertIn("meme_share", xp.bonus_description)


class TestAchievementBadge(unittest.TestCase):
    """Test AchievementBadge value object"""
    
    def test_create_valid_achievement_badge(self):
        """Test creating valid achievement badge"""
        badge = AchievementBadge(
            achievement_type=AchievementType.TRADING_MILESTONE,
            name="First Trade",
            description="Complete your first trade",
            rarity=BadgeRarity.COMMON,
            xp_reward=Decimal('50'),
            currency_reward={'stellar_shards': Decimal('100')},
            unlock_conditions={'trade_count': 1},
            icon_id="first_trade"
        )
        
        self.assertEqual(badge.achievement_type, AchievementType.TRADING_MILESTONE)
        self.assertEqual(badge.name, "First Trade")
        self.assertEqual(badge.rarity, BadgeRarity.COMMON)
        self.assertEqual(badge.xp_reward, Decimal('50'))
        self.assertEqual(badge.total_xp_reward, Decimal('50'))  # Common = 1.0x multiplier
    
    def test_rarity_multiplier_calculation(self):
        """Test XP multiplier based on badge rarity"""
        rarities_and_multipliers = [
            (BadgeRarity.COMMON, Decimal('1.0')),
            (BadgeRarity.RARE, Decimal('1.5')),
            (BadgeRarity.EPIC, Decimal('2.0')),
            (BadgeRarity.LEGENDARY, Decimal('3.0')),
            (BadgeRarity.MYTHIC, Decimal('5.0'))
        ]
        
        for rarity, expected_multiplier in rarities_and_multipliers:
            badge = AchievementBadge(
                achievement_type=AchievementType.TRADING_MILESTONE,
                name="Test Badge",
                description="Test",
                rarity=rarity,
                xp_reward=Decimal('100'),
                currency_reward={},
                unlock_conditions={},
                icon_id="test"
            )
            
            self.assertEqual(badge.rarity_multiplier, expected_multiplier)
            self.assertEqual(badge.total_xp_reward, Decimal('100') * expected_multiplier)
    
    def test_trading_milestone_factory(self):
        """Test trading milestone achievement factory"""
        badge = AchievementBadge.trading_milestone(100)
        
        self.assertEqual(badge.achievement_type, AchievementType.TRADING_MILESTONE)
        self.assertEqual(badge.name, "Seasoned Trader")
        self.assertEqual(badge.rarity, BadgeRarity.RARE)
        self.assertEqual(badge.unlock_conditions['trade_count'], 100)
        self.assertEqual(badge.xp_reward, Decimal('200'))
        self.assertEqual(badge.currency_reward['stellar_shards'], Decimal('400'))
    
    def test_invalid_trade_count_raises_error(self):
        """Test invalid trade count for milestone raises error"""
        with self.assertRaises(ValueError):
            AchievementBadge.trading_milestone(50)  # Not a valid milestone
    
    def test_negative_rewards_raise_error(self):
        """Test that negative rewards raise ValueError"""
        with self.assertRaises(ValueError) as context:
            AchievementBadge(
                achievement_type=AchievementType.TRADING_MILESTONE,
                name="Test",
                description="Test",
                rarity=BadgeRarity.COMMON,
                xp_reward=Decimal('-10'),  # Negative XP
                currency_reward={},
                unlock_conditions={},
                icon_id="test"
            )
        self.assertIn("cannot be negative", str(context.exception))


class TestConstellationRank(unittest.TestCase):
    """Test ConstellationRank value object"""
    
    def test_create_valid_constellation_rank(self):
        """Test creating valid constellation rank"""
        rank = ConstellationRank(
            role=ConstellationRole.MEMBER,
            contribution_score=Decimal('500'),
            stellar_shards_contributed=Decimal('1000'),
            lumina_contributed=Decimal('50'),
            battles_participated=5,
            authority_level=25
        )
        
        self.assertEqual(rank.role, ConstellationRole.MEMBER)
        self.assertEqual(rank.contribution_score, Decimal('500'))
        self.assertEqual(rank.authority_level, 25)
    
    def test_total_contribution_value_calculation(self):
        """Test total contribution value calculation"""
        rank = ConstellationRank(
            role=ConstellationRole.MEMBER,
            contribution_score=Decimal('0'),
            stellar_shards_contributed=Decimal('1000'),
            lumina_contributed=Decimal('50'),  # = 500 stellar shards equivalent
            battles_participated=0,
            authority_level=0
        )
        
        expected_total = Decimal('1000') + (Decimal('50') * Decimal('10'))
        self.assertEqual(rank.total_contribution_value, Decimal('1500'))
    
    def test_permission_checks(self):
        """Test permission checks based on role and authority"""
        # Owner can do everything
        owner_rank = ConstellationRank(
            role=ConstellationRole.OWNER,
            contribution_score=Decimal('0'),
            stellar_shards_contributed=Decimal('0'),
            lumina_contributed=Decimal('0'),
            battles_participated=0,
            authority_level=100
        )
        self.assertTrue(owner_rank.can_invite_members)
        self.assertTrue(owner_rank.can_start_battles)
        
        # High authority member can invite but not start battles
        high_auth_member = ConstellationRank(
            role=ConstellationRole.MEMBER,
            contribution_score=Decimal('0'),
            stellar_shards_contributed=Decimal('0'),
            lumina_contributed=Decimal('0'),
            battles_participated=0,
            authority_level=60
        )
        self.assertTrue(high_auth_member.can_invite_members)
        self.assertFalse(high_auth_member.can_start_battles)
        
        # Low authority member can't do either
        low_auth_member = ConstellationRank(
            role=ConstellationRole.RECRUIT,
            contribution_score=Decimal('0'),
            stellar_shards_contributed=Decimal('0'),
            lumina_contributed=Decimal('0'),
            battles_participated=0,
            authority_level=10
        )
        self.assertFalse(low_auth_member.can_invite_members)
        self.assertFalse(low_auth_member.can_start_battles)
    
    def test_new_member_factory(self):
        """Test new member factory method"""
        rank = ConstellationRank.new_member()
        
        self.assertEqual(rank.role, ConstellationRole.RECRUIT)
        self.assertEqual(rank.contribution_score, Decimal('0'))
        self.assertEqual(rank.authority_level, 10)
        self.assertFalse(rank.can_invite_members)
        self.assertFalse(rank.can_start_battles)


class TestSocialMetrics(unittest.TestCase):
    """Test SocialMetrics value object"""
    
    def test_create_valid_social_metrics(self):
        """Test creating valid social metrics"""
        metrics = SocialMetrics(
            viral_score=Decimal('1500'),
            influence_rating=Decimal('75'),
            engagement_rate=Decimal('0.8'),
            share_count=25,
            like_count=150,
            comment_count=30,
            follower_count=500
        )
        
        self.assertEqual(metrics.viral_score, Decimal('1500'))
        self.assertEqual(metrics.engagement_rate, Decimal('0.8'))
    
    def test_total_engagement_calculation(self):
        """Test total engagement calculation"""
        metrics = SocialMetrics(
            viral_score=Decimal('0'),
            influence_rating=Decimal('0'),
            engagement_rate=Decimal('0.5'),
            share_count=10,
            like_count=50,
            comment_count=15,
            follower_count=0
        )
        
        expected_total = 10 + 50 + 15  # 75
        self.assertEqual(metrics.total_engagement, 75)
    
    def test_virality_tier_classification(self):
        """Test virality tier classification"""
        test_cases = [
            (Decimal('50'), "New Trader"),
            (Decimal('150'), "Active Member"),
            (Decimal('1500'), "Rising Star"),
            (Decimal('7500'), "Stellar Creator"),
            (Decimal('15000'), "Cosmic Influencer")
        ]
        
        for viral_score, expected_tier in test_cases:
            metrics = SocialMetrics(
                viral_score=viral_score,
                influence_rating=Decimal('0'),
                engagement_rate=Decimal('0.5'),
                share_count=0,
                like_count=0,
                comment_count=0,
                follower_count=0
            )
            self.assertEqual(metrics.virality_tier, expected_tier)
    
    def test_calculate_social_xp(self):
        """Test social XP calculation from metrics"""
        metrics = SocialMetrics(
            viral_score=Decimal('1000'),  # 100 XP
            influence_rating=Decimal('100'),  # 50 XP
            engagement_rate=Decimal('0.5'),  # 25% multiplier
            share_count=10,
            like_count=20,
            comment_count=5,
            follower_count=0
        )
        
        xp = metrics.calculate_social_xp()
        
        # Base XP = (1000 * 0.1) + (100 * 0.5) = 100 + 50 = 150
        # Engagement bonus = (10 + 20 + 5) * 0.2 = 35 * 0.2 = 7
        # Total base = 150 + 7 = 157
        # Multiplier = 1.0 + (0.5 * 0.5) = 1.25
        # Final XP = 157 * 1.25 = 196.25
        
        expected_base = Decimal('157')
        expected_multiplier = Decimal('1.25')
        
        self.assertEqual(xp.source, XPSource.SOCIAL)
        self.assertAlmostEqual(float(xp.total_xp), float(expected_base * expected_multiplier), places=2)


class TestRewardPackage(unittest.TestCase):
    """Test RewardPackage value object"""
    
    def test_create_valid_reward_package(self):
        """Test creating valid reward package"""
        badge = AchievementBadge.trading_milestone(10)
        reward = RewardPackage(
            xp_reward=Decimal('100'),
            stellar_shards=Decimal('200'),
            lumina=Decimal('10'),
            stardust=Decimal('1'),
            badges=[badge],
            nft_artifacts=['artifact_001'],
            special_items={'bonus_multiplier': 1.5},
            reward_description="Test reward"
        )
        
        self.assertEqual(reward.xp_reward, Decimal('100'))
        self.assertEqual(len(reward.badges), 1)
        self.assertEqual(len(reward.nft_artifacts), 1)
        self.assertTrue(reward.has_rare_rewards)  # Has stardust and artifacts
    
    def test_total_currency_value_calculation(self):
        """Test total currency value calculation"""
        reward = RewardPackage(
            xp_reward=Decimal('0'),
            stellar_shards=Decimal('1000'),
            lumina=Decimal('50'),     # = 500 stellar shards
            stardust=Decimal('2'),    # = 200 stellar shards
            badges=[],
            nft_artifacts=[],
            special_items={},
            reward_description="Currency test"
        )
        
        expected_total = Decimal('1000') + (Decimal('50') * Decimal('10')) + (Decimal('2') * Decimal('100'))
        self.assertEqual(reward.total_currency_value, Decimal('1700'))
    
    def test_has_rare_rewards_detection(self):
        """Test rare rewards detection"""
        # Reward with common badge only
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
        
        common_reward = RewardPackage(
            xp_reward=Decimal('10'),
            stellar_shards=Decimal('100'),
            lumina=Decimal('0'),
            stardust=Decimal('0'),
            badges=[common_badge],
            nft_artifacts=[],
            special_items={},
            reward_description="Common reward"
        )
        self.assertFalse(common_reward.has_rare_rewards)
        
        # Reward with rare badge
        rare_badge = AchievementBadge(
            achievement_type=AchievementType.TRADING_MILESTONE,
            name="Rare",
            description="Rare",
            rarity=BadgeRarity.RARE,
            xp_reward=Decimal('10'),
            currency_reward={},
            unlock_conditions={},
            icon_id="rare"
        )
        
        rare_reward = RewardPackage(
            xp_reward=Decimal('10'),
            stellar_shards=Decimal('100'),
            lumina=Decimal('0'),
            stardust=Decimal('0'),
            badges=[rare_badge],
            nft_artifacts=[],
            special_items={},
            reward_description="Rare reward"
        )
        self.assertTrue(rare_reward.has_rare_rewards)
    
    def test_achievement_reward_factory(self):
        """Test achievement reward factory"""
        badge = AchievementBadge.trading_milestone(100)
        reward = RewardPackage.achievement_reward(badge)
        
        self.assertEqual(reward.xp_reward, badge.total_xp_reward)
        self.assertEqual(reward.stellar_shards, badge.currency_reward['stellar_shards'])
        self.assertEqual(len(reward.badges), 1)
        self.assertEqual(reward.badges[0], badge)
        self.assertIn("Achievement reward", reward.reward_description)
    
    def test_battle_victory_reward_factory(self):
        """Test battle victory reward factory"""
        battle_score = Decimal('500')
        participation_count = 8
        
        reward = RewardPackage.battle_victory_reward(battle_score, participation_count)
        
        expected_base_shards = battle_score * Decimal('10')  # 5000
        expected_participation_bonus = Decimal(str(participation_count)) * Decimal('50')  # 400
        expected_total_shards = expected_base_shards + expected_participation_bonus  # 5400
        
        self.assertEqual(reward.stellar_shards, expected_total_shards)
        self.assertEqual(reward.xp_reward, battle_score * Decimal('5'))  # 2500
        self.assertIn("Battle victory reward", reward.reward_description)
        self.assertTrue(reward.special_items.get('battle_victory_token'))


if __name__ == '__main__':
    unittest.main()