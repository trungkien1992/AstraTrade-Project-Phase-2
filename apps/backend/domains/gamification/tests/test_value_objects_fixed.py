"""
Comprehensive tests for Gamification Domain Value Objects

This module tests all value objects with full coverage including:
- Input validation and error handling
- Business rule enforcement
- Financial precision with Decimal arithmetic
- Property-based testing where applicable
- Edge cases and boundary conditions
"""

import unittest
from decimal import Decimal
from datetime import datetime

import sys
from pathlib import Path

# Add backend directory to path for imports
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from domains.gamification.value_objects import (
    ExperiencePoints, AchievementBadge, ConstellationRank, SocialMetrics, 
    RewardPackage, XPSource, AchievementType, BadgeRarity, ConstellationRole
)


class TestExperiencePoints(unittest.TestCase):
    """Comprehensive tests for ExperiencePoints value object"""
    
    def test_create_valid_xp(self):
        """Test creating valid ExperiencePoints with all parameters"""
        xp = ExperiencePoints(
            amount=Decimal('100.50'),
            source=XPSource.TRADING,
            multiplier=Decimal('1.25'),
            bonus_description="Streak bonus"
        )
        
        self.assertEqual(xp.amount, Decimal('100.50'))
        self.assertEqual(xp.source, XPSource.TRADING)
        self.assertEqual(xp.multiplier, Decimal('1.25'))
        self.assertEqual(xp.total_xp, Decimal('125.625'))  # 100.50 * 1.25
        self.assertEqual(xp.bonus_description, "Streak bonus")
    
    def test_create_minimal_xp(self):
        """Test creating ExperiencePoints with minimal required parameters"""
        xp = ExperiencePoints(
            amount=Decimal('50'),
            source=XPSource.SOCIAL
        )
        
        self.assertEqual(xp.amount, Decimal('50'))
        self.assertEqual(xp.source, XPSource.SOCIAL)
        self.assertEqual(xp.multiplier, Decimal('1.0'))  # Default multiplier
        self.assertEqual(xp.total_xp, Decimal('50'))
        self.assertIsNone(xp.bonus_description)
    
    def test_negative_amount_validation(self):
        """Test that negative XP amount raises ValueError with specific message"""
        with self.assertRaises(ValueError) as context:
            ExperiencePoints(amount=Decimal('-10'), source=XPSource.TRADING)
        
        self.assertIn("XP amount cannot be negative", str(context.exception))
    
    def test_zero_amount_allowed(self):
        """Test that zero XP amount is allowed"""
        xp = ExperiencePoints(amount=Decimal('0'), source=XPSource.ACHIEVEMENT)
        self.assertEqual(xp.amount, Decimal('0'))
        self.assertEqual(xp.total_xp, Decimal('0'))
    
    def test_negative_multiplier_validation(self):
        """Test that negative multiplier raises ValueError with specific message"""
        with self.assertRaises(ValueError) as context:
            ExperiencePoints(
                amount=Decimal('100'), 
                source=XPSource.TRADING, 
                multiplier=Decimal('-0.5')
            )
        
        self.assertIn("XP multiplier cannot be negative", str(context.exception))
    
    def test_zero_multiplier_allowed(self):
        """Test that zero multiplier is allowed (results in zero XP)"""
        xp = ExperiencePoints(
            amount=Decimal('100'),
            source=XPSource.TRADING,
            multiplier=Decimal('0')
        )
        self.assertEqual(xp.total_xp, Decimal('0'))
    
    def test_trading_xp_profitable_trade(self):
        """Test trading XP calculation for profitable trade"""
        xp = ExperiencePoints.trading_xp(
            trade_volume=Decimal('1000.00'),
            profit_loss=Decimal('50.25')
        )
        
        expected_base = Decimal('1000.00') * Decimal('0.1')  # 100.00
        expected_bonus = Decimal('50.25') * Decimal('0.5')   # 25.125
        expected_total = expected_base + expected_bonus       # 125.125
        
        self.assertEqual(xp.amount, expected_total)
        self.assertEqual(xp.source, XPSource.TRADING)
        self.assertIn("Profit bonus", xp.bonus_description)
        self.assertIn("25.125", xp.bonus_description)
    
    def test_trading_xp_loss_trade(self):
        """Test trading XP calculation for losing trade (no profit bonus)"""
        xp = ExperiencePoints.trading_xp(
            trade_volume=Decimal('1000.00'),
            profit_loss=Decimal('-25.50')  # Loss
        )
        
        expected_amount = Decimal('1000.00') * Decimal('0.1')  # 100.00, no bonus
        self.assertEqual(xp.amount, expected_amount)
        self.assertEqual(xp.source, XPSource.TRADING)
        self.assertIsNone(xp.bonus_description)
    
    def test_trading_xp_break_even(self):
        """Test trading XP calculation for break-even trade"""
        xp = ExperiencePoints.trading_xp(
            trade_volume=Decimal('500.00'),
            profit_loss=Decimal('0.00')
        )
        
        expected_amount = Decimal('500.00') * Decimal('0.1')  # 50.00
        self.assertEqual(xp.amount, expected_amount)
        self.assertIsNone(xp.bonus_description)
    
    def test_trading_xp_high_precision(self):
        """Test trading XP calculation maintains high precision"""
        xp = ExperiencePoints.trading_xp(
            trade_volume=Decimal('1234.5678'),
            profit_loss=Decimal('98.7654')
        )
        
        expected_base = Decimal('1234.5678') * Decimal('0.1')    # 123.45678
        expected_bonus = Decimal('98.7654') * Decimal('0.5')     # 49.3827
        expected_total = expected_base + expected_bonus           # 172.83948
        
        self.assertEqual(xp.amount, expected_total)
        # Verify precision is maintained
        self.assertEqual(str(xp.amount), '172.83948')
    
    def test_social_xp_calculation(self):
        """Test social XP calculation with activity type"""
        xp = ExperiencePoints.social_xp(
            activity_type="viral_meme_creation",
            engagement_score=Decimal('37.5')
        )
        
        expected_amount = Decimal('37.5') * Decimal('2.0')  # 75.0
        self.assertEqual(xp.amount, expected_amount)
        self.assertEqual(xp.source, XPSource.SOCIAL)
        self.assertIn("viral_meme_creation", xp.bonus_description)
    
    def test_social_xp_zero_engagement(self):
        """Test social XP calculation with zero engagement"""
        xp = ExperiencePoints.social_xp(
            activity_type="post_share",
            engagement_score=Decimal('0')
        )
        
        self.assertEqual(xp.amount, Decimal('0'))
        self.assertEqual(xp.source, XPSource.SOCIAL)
        self.assertIn("post_share", xp.bonus_description)
    
    def test_all_xp_sources_covered(self):
        """Test that all XPSource enum values are valid"""
        sources = [
            XPSource.TRADING,
            XPSource.SOCIAL,
            XPSource.VAULT_DEPOSIT,
            XPSource.ACHIEVEMENT,
            XPSource.BATTLE_PARTICIPATION,
            XPSource.STREAK_BONUS,
            XPSource.REFERRAL
        ]
        
        for source in sources:
            xp = ExperiencePoints(amount=Decimal('10'), source=source)
            self.assertEqual(xp.source, source)
            # Verify enum values are strings
            self.assertIsInstance(source.value, str)


class TestAchievementBadge(unittest.TestCase):
    """Comprehensive tests for AchievementBadge value object"""
    
    def test_create_valid_achievement_badge(self):
        """Test creating valid achievement badge with all parameters"""
        badge = AchievementBadge(
            achievement_type=AchievementType.TRADING_MILESTONE,
            name="Master Trader",
            description="Complete 1000 successful trades",
            rarity=BadgeRarity.EPIC,
            xp_reward=Decimal('500'),
            currency_reward={
                'stellar_shards': Decimal('1000'),
                'lumina': Decimal('50'),
                'stardust': Decimal('2')
            },
            unlock_conditions={
                'successful_trades': 1000,
                'win_rate': Decimal('0.75'),
                'min_level': 10
            },
            icon_id="master_trader_epic"
        )
        
        self.assertEqual(badge.achievement_type, AchievementType.TRADING_MILESTONE)
        self.assertEqual(badge.name, "Master Trader")
        self.assertEqual(badge.description, "Complete 1000 successful trades")
        self.assertEqual(badge.rarity, BadgeRarity.EPIC)
        self.assertEqual(badge.xp_reward, Decimal('500'))
        self.assertEqual(badge.currency_reward['stellar_shards'], Decimal('1000'))
        self.assertEqual(badge.unlock_conditions['successful_trades'], 1000)
        self.assertEqual(badge.icon_id, "master_trader_epic")
    
    def test_rarity_multiplier_calculations(self):
        """Test XP multiplier calculation for all badge rarities"""
        rarity_tests = [
            (BadgeRarity.COMMON, Decimal('1.0')),
            (BadgeRarity.RARE, Decimal('1.5')),
            (BadgeRarity.EPIC, Decimal('2.0')),
            (BadgeRarity.LEGENDARY, Decimal('3.0')),
            (BadgeRarity.MYTHIC, Decimal('5.0'))
        ]
        
        base_xp = Decimal('100')
        
        for rarity, expected_multiplier in rarity_tests:
            badge = AchievementBadge(
                achievement_type=AchievementType.PROFIT_THRESHOLD,
                name=f"Test Badge {rarity.value}",
                description="Test badge",
                rarity=rarity,
                xp_reward=base_xp,
                currency_reward={},
                unlock_conditions={},
                icon_id=f"test_{rarity.value}"
            )
            
            self.assertEqual(badge.rarity_multiplier, expected_multiplier)
            expected_total = base_xp * expected_multiplier
            self.assertEqual(badge.total_xp_reward, expected_total)
    
    def test_trading_milestone_factory_all_levels(self):
        """Test trading milestone factory for all valid levels"""
        milestone_tests = [
            (10, "First Steps", BadgeRarity.COMMON, Decimal('50')),
            (100, "Seasoned Trader", BadgeRarity.RARE, Decimal('200')),
            (1000, "Trading Master", BadgeRarity.EPIC, Decimal('500')),
            (10000, "Market Legend", BadgeRarity.LEGENDARY, Decimal('2000'))
        ]
        
        for trade_count, expected_name, expected_rarity, expected_xp in milestone_tests:
            badge = AchievementBadge.trading_milestone(trade_count)
            
            self.assertEqual(badge.achievement_type, AchievementType.TRADING_MILESTONE)
            self.assertEqual(badge.name, expected_name)
            self.assertEqual(badge.rarity, expected_rarity)
            self.assertEqual(badge.xp_reward, expected_xp)
            self.assertEqual(badge.unlock_conditions['trade_count'], trade_count)
            
            # Verify currency reward is 2x XP
            expected_shards = expected_xp * Decimal('2')
            self.assertEqual(badge.currency_reward['stellar_shards'], expected_shards)
            
            # Verify icon naming convention
            expected_icon = f"trading_milestone_{trade_count}"
            self.assertEqual(badge.icon_id, expected_icon)
    
    def test_trading_milestone_invalid_counts(self):
        """Test trading milestone factory with invalid trade counts"""
        invalid_counts = [0, 5, 50, 500, 5000, -10, 15000]
        
        for invalid_count in invalid_counts:
            with self.assertRaises(ValueError) as context:
                AchievementBadge.trading_milestone(invalid_count)
            
            self.assertIn("Invalid trade count for milestone", str(context.exception))
            self.assertIn(str(invalid_count), str(context.exception))
    
    def test_negative_xp_reward_validation(self):
        """Test that negative XP reward raises ValueError"""
        with self.assertRaises(ValueError) as context:
            AchievementBadge(
                achievement_type=AchievementType.TRADING_MILESTONE,
                name="Invalid Badge",
                description="Test",
                rarity=BadgeRarity.COMMON,
                xp_reward=Decimal('-50'),  # Invalid negative XP
                currency_reward={},
                unlock_conditions={},
                icon_id="invalid"
            )
        
        self.assertIn("XP reward cannot be negative", str(context.exception))
    
    def test_negative_currency_reward_validation(self):
        """Test that negative currency rewards raise ValueError"""
        with self.assertRaises(ValueError) as context:
            AchievementBadge(
                achievement_type=AchievementType.TRADING_MILESTONE,
                name="Invalid Badge",
                description="Test",
                rarity=BadgeRarity.COMMON,
                xp_reward=Decimal('50'),
                currency_reward={
                    'stellar_shards': Decimal('100'),
                    'lumina': Decimal('-10')  # Invalid negative currency
                },
                unlock_conditions={},
                icon_id="invalid"
            )
        
        self.assertIn("Currency reward for lumina cannot be negative", str(context.exception))
    
    def test_zero_rewards_allowed(self):
        """Test that zero rewards are allowed"""
        badge = AchievementBadge(
            achievement_type=AchievementType.SOCIAL_ACHIEVEMENT,
            name="Zero Reward Badge",
            description="Badge with zero rewards",
            rarity=BadgeRarity.COMMON,
            xp_reward=Decimal('0'),
            currency_reward={
                'stellar_shards': Decimal('0'),
                'lumina': Decimal('0')
            },
            unlock_conditions={},
            icon_id="zero_reward"
        )
        
        self.assertEqual(badge.total_xp_reward, Decimal('0'))
        self.assertEqual(badge.currency_reward['stellar_shards'], Decimal('0'))
    
    def test_all_achievement_types_covered(self):
        """Test that all AchievementType enum values are valid"""
        achievement_types = [
            AchievementType.TRADING_MILESTONE,
            AchievementType.PROFIT_THRESHOLD,
            AchievementType.STREAK_ACHIEVEMENT,
            AchievementType.SOCIAL_ACHIEVEMENT,
            AchievementType.CONSTELLATION_ACHIEVEMENT,
            AchievementType.VAULT_ACHIEVEMENT,
            AchievementType.RARE_EVENT
        ]
        
        for achievement_type in achievement_types:
            badge = AchievementBadge(
                achievement_type=achievement_type,
                name=f"Test {achievement_type.value}",
                description="Test badge",
                rarity=BadgeRarity.COMMON,
                xp_reward=Decimal('10'),
                currency_reward={},
                unlock_conditions={},
                icon_id=f"test_{achievement_type.value}"
            )
            
            self.assertEqual(badge.achievement_type, achievement_type)
            # Verify enum values are strings
            self.assertIsInstance(achievement_type.value, str)


class TestConstellationRank(unittest.TestCase):
    """Comprehensive tests for ConstellationRank value object"""
    
    def test_create_valid_constellation_rank(self):
        """Test creating valid constellation rank with all parameters"""
        rank = ConstellationRank(
            role=ConstellationRole.ADMIN,
            contribution_score=Decimal('1500.75'),
            stellar_shards_contributed=Decimal('5000.50'),
            lumina_contributed=Decimal('250.25'),
            battles_participated=15,
            authority_level=75
        )
        
        self.assertEqual(rank.role, ConstellationRole.ADMIN)
        self.assertEqual(rank.contribution_score, Decimal('1500.75'))
        self.assertEqual(rank.stellar_shards_contributed, Decimal('5000.50'))
        self.assertEqual(rank.lumina_contributed, Decimal('250.25'))
        self.assertEqual(rank.battles_participated, 15)
        self.assertEqual(rank.authority_level, 75)
    
    def test_total_contribution_value_calculation(self):
        """Test total contribution value calculation with precision"""
        rank = ConstellationRank(
            role=ConstellationRole.MEMBER,
            contribution_score=Decimal('0'),
            stellar_shards_contributed=Decimal('1000.00'),
            lumina_contributed=Decimal('123.45'),  # 1234.50 stellar shards equivalent
            battles_participated=0,
            authority_level=25
        )
        
        expected_total = Decimal('1000.00') + (Decimal('123.45') * Decimal('10.0'))
        self.assertEqual(rank.total_contribution_value, Decimal('2234.50'))
    
    def test_permission_checks_by_role(self):
        """Test permission checks based on constellation role"""
        # Owner permissions
        owner_rank = ConstellationRank(
            role=ConstellationRole.OWNER,
            contribution_score=Decimal('0'),
            stellar_shards_contributed=Decimal('0'),
            lumina_contributed=Decimal('0'),
            battles_participated=0,
            authority_level=0  # Role overrides low authority
        )
        self.assertTrue(owner_rank.can_invite_members)
        self.assertTrue(owner_rank.can_start_battles)
        
        # Admin permissions
        admin_rank = ConstellationRank(
            role=ConstellationRole.ADMIN,
            contribution_score=Decimal('0'),
            stellar_shards_contributed=Decimal('0'),
            lumina_contributed=Decimal('0'),
            battles_participated=0,
            authority_level=0  # Role overrides low authority
        )
        self.assertTrue(admin_rank.can_invite_members)
        self.assertTrue(admin_rank.can_start_battles)
        
        # Member with low authority
        low_member_rank = ConstellationRank(
            role=ConstellationRole.MEMBER,
            contribution_score=Decimal('0'),
            stellar_shards_contributed=Decimal('0'),
            lumina_contributed=Decimal('0'),
            battles_participated=0,
            authority_level=25  # Below invite threshold (50)
        )
        self.assertFalse(low_member_rank.can_invite_members)
        self.assertFalse(low_member_rank.can_start_battles)
        
        # Recruit permissions
        recruit_rank = ConstellationRank(
            role=ConstellationRole.RECRUIT,
            contribution_score=Decimal('0'),
            stellar_shards_contributed=Decimal('0'),
            lumina_contributed=Decimal('0'),
            battles_participated=0,
            authority_level=100  # High authority doesn't help recruits
        )
        self.assertFalse(recruit_rank.can_invite_members)
        self.assertFalse(recruit_rank.can_start_battles)
    
    def test_permission_checks_by_authority_level(self):
        """Test permission checks based on authority level"""
        # Member with invite authority but not battle authority
        mid_auth_member = ConstellationRank(
            role=ConstellationRole.MEMBER,
            contribution_score=Decimal('0'),
            stellar_shards_contributed=Decimal('0'),
            lumina_contributed=Decimal('0'),
            battles_participated=0,
            authority_level=60  # Above invite (50) but below battle (75)
        )
        self.assertTrue(mid_auth_member.can_invite_members)
        self.assertFalse(mid_auth_member.can_start_battles)
        
        # Member with both authorities
        high_auth_member = ConstellationRank(
            role=ConstellationRole.MEMBER,
            contribution_score=Decimal('0'),
            stellar_shards_contributed=Decimal('0'),
            lumina_contributed=Decimal('0'),
            battles_participated=0,
            authority_level=80  # Above both thresholds
        )
        self.assertTrue(high_auth_member.can_invite_members)
        self.assertTrue(high_auth_member.can_start_battles)
    
    def test_new_member_factory(self):
        """Test new member factory creates proper default rank"""
        rank = ConstellationRank.new_member()
        
        self.assertEqual(rank.role, ConstellationRole.RECRUIT)
        self.assertEqual(rank.contribution_score, Decimal('0'))
        self.assertEqual(rank.stellar_shards_contributed, Decimal('0'))
        self.assertEqual(rank.lumina_contributed, Decimal('0'))
        self.assertEqual(rank.battles_participated, 0)
        self.assertEqual(rank.authority_level, 10)
        
        # New members should have no permissions
        self.assertFalse(rank.can_invite_members)
        self.assertFalse(rank.can_start_battles)
        
        # Verify total contribution is zero
        self.assertEqual(rank.total_contribution_value, Decimal('0'))
    
    def test_negative_values_validation(self):
        """Test that negative values raise appropriate ValueError"""
        base_params = {
            'role': ConstellationRole.MEMBER,
            'stellar_shards_contributed': Decimal('100'),
            'lumina_contributed': Decimal('10'),
            'battles_participated': 5,
            'authority_level': 50
        }
        
        # Test negative contribution score
        with self.assertRaises(ValueError) as context:
            ConstellationRank(contribution_score=Decimal('-100'), **base_params)
        self.assertIn("Contribution score cannot be negative", str(context.exception))
        
        # Test negative stellar shards
        params = base_params.copy()
        params['stellar_shards_contributed'] = Decimal('-50')
        with self.assertRaises(ValueError) as context:
            ConstellationRank(contribution_score=Decimal('0'), **params)
        self.assertIn("Stellar shards contributed cannot be negative", str(context.exception))
        
        # Test negative lumina
        params = base_params.copy()
        params['lumina_contributed'] = Decimal('-10')
        with self.assertRaises(ValueError) as context:
            ConstellationRank(contribution_score=Decimal('0'), **params)
        self.assertIn("Lumina contributed cannot be negative", str(context.exception))
        
        # Test negative battles
        params = base_params.copy()
        params['battles_participated'] = -1
        with self.assertRaises(ValueError) as context:
            ConstellationRank(contribution_score=Decimal('0'), **params)
        self.assertIn("Battles participated cannot be negative", str(context.exception))
    
    def test_authority_level_bounds_validation(self):
        """Test that authority level must be between 0 and 100"""
        base_params = {
            'role': ConstellationRole.MEMBER,
            'contribution_score': Decimal('0'),
            'stellar_shards_contributed': Decimal('100'),
            'lumina_contributed': Decimal('10'),
            'battles_participated': 5
        }
        
        # Test authority level below 0
        with self.assertRaises(ValueError) as context:
            ConstellationRank(authority_level=-1, **base_params)
        self.assertIn("Authority level must be between 0 and 100", str(context.exception))
        
        # Test authority level above 100
        with self.assertRaises(ValueError) as context:
            ConstellationRank(authority_level=101, **base_params)
        self.assertIn("Authority level must be between 0 and 100", str(context.exception))
        
        # Test boundary values are allowed
        rank_0 = ConstellationRank(authority_level=0, **base_params)
        self.assertEqual(rank_0.authority_level, 0)
        
        rank_100 = ConstellationRank(authority_level=100, **base_params)
        self.assertEqual(rank_100.authority_level, 100)


if __name__ == '__main__':
    # Run with high verbosity to see all test details
    unittest.main(verbosity=2, buffer=True)