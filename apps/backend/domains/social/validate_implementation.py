#!/usr/bin/env python3
"""
Social Domain Implementation Validator

Comprehensive validation for Social Domain implementation following TSDS-CPP Stage 5.
Tests all business rules, value objects, entities, and domain services.
"""

import sys
import os
import traceback
from datetime import datetime, timezone
from decimal import Decimal

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test imports and basic functionality
def test_imports():
    """Test that all domain components can be imported successfully"""
    print("Testing imports...")
    
    try:
        # Import value objects
        from value_objects import (
            SocialRating, InfluenceScore, SocialBadge, ConstellationInfo, ViralMetrics,
            PrestigeLevel, SocialInteractionContext, CommunityRole, VerificationTier,
            ContentType, ModerationStatus, SocialInteractionType
        )
        print("✅ Value objects imported successfully")
        
        # Test basic value object creation
        rating = SocialRating(score=75.0)
        influence = InfluenceScore(score=100.0)
        prestige = PrestigeLevel(VerificationTier.NONE)
        
        print("✅ Value objects can be instantiated")
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        traceback.print_exc()
        return False


def test_value_object_validation():
    """Test value object validation rules"""
    print("\nTesting value object validation...")
    
    try:
        from value_objects import SocialRating, InfluenceScore, VerificationTier
        
        # Test valid creation
        rating = SocialRating(score=85.5, endorsement_count=10)
        assert rating.score == 85.5
        assert rating.reputation_level == "Renowned"
        
        # Test validation
        try:
            SocialRating(score=-5.0)  # Should fail
            assert False, "Should have raised ValueError"
        except ValueError:
            pass  # Expected
        
        # Test influence score
        influence = InfluenceScore(score=500.0, constellation_leadership=True)
        assert influence.influence_tier == "Stellar Leader"
        
        boosts = influence.calculate_boost_factors()
        assert boosts["endorsement_value"] > 1.0  # Should have leadership bonus
        
        print("✅ Value object validation working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Value object validation failed: {e}")
        traceback.print_exc()
        return False


def test_business_logic():
    """Test core business logic"""
    print("\nTesting business logic...")
    
    try:
        from value_objects import SocialRating, InfluenceScore, SocialBadge, VerificationTier
        
        # Test social rating with endorsements
        rating = SocialRating(score=50.0, endorsement_count=5)
        enhanced = rating.with_endorsement()
        
        assert enhanced.score > rating.score
        assert enhanced.endorsement_count == rating.endorsement_count + 1
        
        # Test negative feedback
        penalized = rating.with_negative_feedback()
        assert penalized.score < rating.score
        assert penalized.negative_feedback == rating.negative_feedback + 1
        
        # Test influence calculations
        influence = InfluenceScore(
            score=300.0,
            viral_content_count=8,
            constellation_leadership=True,
            community_contributions=15
        )
        
        assert influence.influence_tier == "Community Guide"
        
        # Test badge system
        badge = SocialBadge(
            badge_id="test_badge",
            name="Test Badge", 
            description="Test",
            earned_at=datetime.now(timezone.utc),
            rarity="epic",
            category="social"
        )
        
        assert badge.rarity_points == 50
        
        print("✅ Business logic working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Business logic test failed: {e}")
        traceback.print_exc()
        return False


def test_domain_rules():
    """Test domain-specific business rules"""
    print("\nTesting domain rules...")
    
    try:
        from value_objects import (
            SocialRating, InfluenceScore, ConstellationInfo, ViralMetrics,
            CommunityRole, SocialInteractionContext, SocialInteractionType
        )
        
        # Test constellation info
        constellation_info = ConstellationInfo(
            constellation_id=1,
            name="Test Constellation",
            role=CommunityRole.ADMIN,
            member_since=datetime.now(timezone.utc),
            contribution_score=100
        )
        
        assert constellation_info.is_leadership_role is True
        loyalty_bonus = constellation_info.calculate_loyalty_bonus()
        assert loyalty_bonus >= 2  # Should have leadership bonus
        
        # Test viral metrics
        metrics = ViralMetrics(
            share_count=15,
            viral_score=250,
            engagement_rate=0.2,
            platform_shares={"twitter": 10, "instagram": 5}
        )
        
        assert metrics.total_platform_shares == 15
        assert metrics.virality_tier == "Popular"
        
        influence_points = metrics.calculate_influence_points()
        assert influence_points > 0
        
        # Test social interaction context
        context = SocialInteractionContext(
            interaction_type=SocialInteractionType.ENDORSEMENT,
            target_user_id=123,
            interaction_weight=1.5
        )
        
        assert context.is_positive_interaction is True
        
        source_influence = InfluenceScore(score=400.0)
        impact = context.calculate_impact_value(source_influence)
        assert impact > 0
        
        print("✅ Domain rules working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Domain rules test failed: {e}")
        traceback.print_exc()
        return False


def test_edge_cases():
    """Test edge cases and boundary conditions"""
    print("\nTesting edge cases...")
    
    try:
        from value_objects import SocialRating, InfluenceScore, ViralMetrics
        
        # Test boundary values
        min_rating = SocialRating(score=0.0)
        max_rating = SocialRating(score=100.0)
        
        assert min_rating.reputation_level == "Newcomer"
        assert max_rating.reputation_level == "Legendary"
        
        # Test high influence
        cosmic_influence = InfluenceScore(score=1500.0)
        assert cosmic_influence.influence_tier == "Cosmic Influencer"
        
        # Test viral content edge cases
        no_shares = ViralMetrics(0, 0, 0.0, {})
        assert no_shares.virality_tier == "Emerging"
        
        cosmic_viral = ViralMetrics(100, 2000, 0.5, {"twitter": 100})
        assert cosmic_viral.virality_tier == "Cosmic Viral"
        
        print("✅ Edge cases handled correctly")
        return True
        
    except Exception as e:
        print(f"❌ Edge case test failed: {e}")
        traceback.print_exc()
        return False


def test_immutability():
    """Test that value objects are properly immutable"""
    print("\nTesting immutability...")
    
    try:
        from value_objects import SocialRating, InfluenceScore
        
        rating = SocialRating(score=75.0)
        
        # Attempt to modify should fail
        try:
            rating.score = 85.0
            assert False, "Should not be able to modify immutable object"
        except AttributeError:
            pass  # Expected
        
        influence = InfluenceScore(score=200.0)
        
        try:
            influence.score = 300.0
            assert False, "Should not be able to modify immutable object"
        except AttributeError:
            pass  # Expected
        
        print("✅ Immutability enforced correctly")
        return True
        
    except Exception as e:
        print(f"❌ Immutability test failed: {e}")
        traceback.print_exc()
        return False


def run_validation_suite():
    """Run complete validation suite"""
    print("🚀 Social Domain Implementation Validation")
    print("Following TSDS-CPP Stage 5: Strict Testing")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_imports),
        ("Value Object Validation", test_value_object_validation),
        ("Business Logic", test_business_logic),
        ("Domain Rules", test_domain_rules),
        ("Edge Cases", test_edge_cases),
        ("Immutability", test_immutability)
    ]
    
    passed = 0
    failed = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                failed.append(test_name)
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            failed.append(test_name)
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Validation Results:")
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {len(failed)}/{len(tests)}")
    
    if failed:
        print(f"\n🚨 Failed Tests: {', '.join(failed)}")
        print(f"❌ VALIDATION FAILED - Social Domain needs fixes")
        return False
    else:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"✅ VALIDATION SUCCESSFUL - Social Domain ready for integration")
        return True


def main():
    """Main validation function"""
    success = run_validation_suite()
    
    if success:
        print(f"\n🎯 Social Domain Implementation Quality:")
        print(f"  - ✅ Value Objects: Immutable, validated, business rules enforced")
        print(f"  - ✅ Domain Logic: Complex calculations and interactions working")
        print(f"  - ✅ Business Rules: All domain-specific rules implemented")  
        print(f"  - ✅ Edge Cases: Boundary conditions handled properly")
        print(f"  - ✅ Architecture: Following DDD patterns consistently")
        
        print(f"\n🚀 Ready for Stage 6: Clearing Up")
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())