#!/usr/bin/env python3
"""
Simple test runner for Gamification Domain tests
"""
import sys
import os
from pathlib import Path

# Add current directory to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_value_objects():
    """Test value objects functionality"""
    print("Testing Value Objects...")
    
    try:
        from value_objects import (
            ExperiencePoints, AchievementBadge, ConstellationRank, 
            XPSource, AchievementType, BadgeRarity, ConstellationRole
        )
        from decimal import Decimal
        
        # Test 1: ExperiencePoints creation
        xp = ExperiencePoints(
            amount=Decimal('100'),
            source=XPSource.TRADING,
            multiplier=Decimal('1.5')
        )
        assert xp.total_xp == Decimal('150'), f"Expected 150, got {xp.total_xp}"
        print("✓ ExperiencePoints creation and calculation")
        
        # Test 2: Trading XP calculation
        trading_xp = ExperiencePoints.trading_xp(
            trade_volume=Decimal('1000'),
            profit_loss=Decimal('50')
        )
        expected = Decimal('1000') * Decimal('0.1') + Decimal('50') * Decimal('0.5')  # 125
        assert trading_xp.amount == expected, f"Expected {expected}, got {trading_xp.amount}"
        print("✓ Trading XP calculation")
        
        # Test 3: Achievement Badge creation
        badge = AchievementBadge.trading_milestone(10)
        assert badge.name == "First Steps", f"Expected 'First Steps', got {badge.name}"
        assert badge.rarity == BadgeRarity.COMMON, f"Expected COMMON, got {badge.rarity}"
        print("✓ Achievement Badge creation")
        
        # Test 4: Constellation Rank permissions
        rank = ConstellationRank.new_member()
        assert rank.role == ConstellationRole.RECRUIT, f"Expected RECRUIT, got {rank.role}"
        assert not rank.can_invite_members, "New member should not be able to invite"
        print("✓ Constellation Rank permissions")
        
        return True
        
    except Exception as e:
        print(f"✗ Value Objects test failed: {e}")
        return False

def test_entities():
    """Test entities functionality"""
    print("\nTesting Entities...")
    
    try:
        from entities import UserProgression, Constellation
        from value_objects import ExperiencePoints, XPSource, AchievementBadge
        from events import DomainEvent
        from decimal import Decimal
        
        # Test 1: UserProgression creation
        progression = UserProgression(user_id=123)
        assert progression.user_id == 123, f"Expected 123, got {progression.user_id}"
        assert progression.current_level == 1, f"Expected level 1, got {progression.current_level}"
        print("✓ UserProgression creation")
        
        # Test 2: XP award and level up
        xp = ExperiencePoints(amount=Decimal('1500'), source=XPSource.TRADING)
        level_up = progression.award_xp(xp)
        assert level_up == True, "Should have leveled up"
        assert progression.current_level == 2, f"Expected level 2, got {progression.current_level}"
        print("✓ XP award and level up")
        
        # Test 3: Constellation creation
        constellation = Constellation(
            constellation_id=1,
            name="Test Constellation",
            description="Test",
            owner_id=123
        )
        assert constellation.name == "Test Constellation", f"Expected 'Test Constellation', got {constellation.name}"
        print("✓ Constellation creation")
        
        # Test 4: Constellation member management
        rank = constellation.add_member(456)
        assert constellation.member_count == 1, f"Expected 1 member, got {constellation.member_count}"
        print("✓ Constellation member management")
        
        return True
        
    except Exception as e:
        print(f"✗ Entities test failed: {e}")
        return False

def test_services():
    """Test services functionality"""
    print("\nTesting Services...")
    
    try:
        from services import GamificationDomainService, UserStats
        import asyncio
        from decimal import Decimal
        
        # Create mock repositories (simplified)
        class MockRepo:
            def __init__(self):
                self.data = {}
            async def get_by_user_id(self, user_id): return self.data.get(user_id)
            async def save(self, obj): 
                if hasattr(obj, 'user_id'):
                    self.data[obj.user_id] = obj
                return obj
            async def get_top_users_by_xp(self, limit=10): return []
            async def get_user_rank_by_xp(self, user_id): return 1
            async def get_by_id(self, id): return None
            async def get_all_active(self): return []
            async def get_unclaimed_by_user(self, user_id): return []
            async def get_expired_rewards(self): return []
            async def get_active_leaderboards(self): return []
            async def get_leaderboard_entries(self, lb_id, limit=100): return []
            async def update_leaderboard_entries(self, lb_id, entries): pass
            async def get_top_by_rating(self, limit=10): return []
            async def search_public(self, query, limit=20): return []
            async def get_by_user_id(self, user_id): return None
        
        # Create service with mock repos
        service = GamificationDomainService(
            user_progression_repo=MockRepo(),
            constellation_repo=MockRepo(),
            achievement_repo=MockRepo(),
            leaderboard_repo=MockRepo(),
            reward_repo=MockRepo()
        )
        
        print("✓ GamificationDomainService creation")
        
        # Test viral score calculation (this is an async method)
        async def test_viral():
            return await service.calculate_viral_score(
                "meme", 10, {'likes': 50, 'comments': 5, 'reshares': 2}
            )
        viral_score = asyncio.run(test_viral())
        # Simplified check - just ensure it's calculated
        assert viral_score > 0, f"Expected positive viral score, got {viral_score}"
        print("✓ Viral score calculation")
        
        return True
        
    except Exception as e:
        print(f"✗ Services test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("GAMIFICATION DOMAIN SIMPLE TEST RUNNER")
    print("=" * 60)
    
    tests = [test_value_objects, test_entities, test_services]
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            result = test()
            if result:
                passed += 1
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
    
    print(f"\n{'='*60}")
    print(f"RESULTS: {passed}/{total} test suites passed")
    
    if passed == total:
        print("🎉 ALL BASIC TESTS PASSED! 🎉")
        print("Gamification Domain core functionality verified.")
        return True
    else:
        print("❌ Some tests failed. Core functionality may have issues.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)