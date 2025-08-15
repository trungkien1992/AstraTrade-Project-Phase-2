"""
Test suite for Social Domain Value Objects

Tests immutability, validation rules, and business logic for all social value objects.
"""

import pytest
from datetime import datetime, timezone
from decimal import Decimal

from ..value_objects import (
    SocialRating, InfluenceScore, SocialBadge, ConstellationInfo, ViralMetrics,
    PrestigeLevel, SocialInteractionContext, CommunityRole, VerificationTier,
    ContentType, ModerationStatus, SocialInteractionType
)


class TestSocialRating:
    """Test SocialRating value object"""
    
    def test_create_valid_social_rating(self):
        rating = SocialRating(score=75.5, endorsement_count=10)
        assert rating.score == 75.5
        assert rating.max_score == 100.0
        assert rating.endorsement_count == 10
        assert rating.negative_feedback == 0
    
    def test_social_rating_validation(self):
        with pytest.raises(ValueError, match="Social rating must be between 0 and 100"):
            SocialRating(score=-5.0)
        
        with pytest.raises(ValueError, match="Social rating must be between 0 and 100"):
            SocialRating(score=150.0)
        
        with pytest.raises(ValueError, match="Endorsement count cannot be negative"):
            SocialRating(score=50.0, endorsement_count=-1)
    
    def test_social_rating_percentage(self):
        rating = SocialRating(score=75.0)
        assert rating.percentage == 75.0
    
    def test_reputation_levels(self):
        assert SocialRating(score=95.0).reputation_level == "Legendary"
        assert SocialRating(score=80.0).reputation_level == "Renowned"
        assert SocialRating(score=60.0).reputation_level == "Respected"
        assert SocialRating(score=30.0).reputation_level == "Emerging"
        assert SocialRating(score=10.0).reputation_level == "Newcomer"
    
    def test_with_endorsement(self):
        rating = SocialRating(score=50.0, endorsement_count=5)
        new_rating = rating.with_endorsement()
        
        assert new_rating.score > rating.score
        assert new_rating.endorsement_count == rating.endorsement_count + 1
        assert new_rating.negative_feedback == rating.negative_feedback
    
    def test_with_negative_feedback(self):
        rating = SocialRating(score=80.0, negative_feedback=2)
        new_rating = rating.with_negative_feedback()
        
        assert new_rating.score < rating.score
        assert new_rating.negative_feedback == rating.negative_feedback + 1
        assert new_rating.endorsement_count == rating.endorsement_count
    
    def test_endorsement_diminishing_returns(self):
        rating = SocialRating(score=50.0, endorsement_count=0)
        first_endorsement = rating.with_endorsement()
        
        rating_high_endorsement = SocialRating(score=50.0, endorsement_count=50)
        next_endorsement = rating_high_endorsement.with_endorsement()
        
        # First endorsement should give more boost than 51st endorsement
        first_boost = first_endorsement.score - rating.score
        later_boost = next_endorsement.score - rating_high_endorsement.score
        assert first_boost > later_boost


class TestInfluenceScore:
    """Test InfluenceScore value object"""
    
    def test_create_valid_influence_score(self):
        influence = InfluenceScore(
            score=250.0,
            viral_content_count=5,
            constellation_leadership=True,
            community_contributions=20,
            follower_count=100
        )
        
        assert influence.score == 250.0
        assert influence.viral_content_count == 5
        assert influence.constellation_leadership is True
        assert influence.community_contributions == 20
        assert influence.follower_count == 100
    
    def test_influence_score_validation(self):
        with pytest.raises(ValueError, match="Influence score cannot be negative"):
            InfluenceScore(score=-10.0)
        
        with pytest.raises(ValueError, match="Viral content count cannot be negative"):
            InfluenceScore(score=100.0, viral_content_count=-1)
    
    def test_influence_tiers(self):
        assert InfluenceScore(score=1500.0).influence_tier == "Cosmic Influencer"
        assert InfluenceScore(score=750.0).influence_tier == "Stellar Leader"
        assert InfluenceScore(score=300.0).influence_tier == "Community Guide"
        assert InfluenceScore(score=75.0).influence_tier == "Rising Voice"
        assert InfluenceScore(score=25.0).influence_tier == "New Member"
    
    def test_boost_factors_calculation(self):
        # Test leadership bonus
        leader = InfluenceScore(score=100.0, constellation_leadership=True)
        leader_boosts = leader.calculate_boost_factors()
        assert leader_boosts["endorsement_value"] == 1.5
        
        # Test viral content bonus
        creator = InfluenceScore(score=100.0, viral_content_count=15)
        creator_boosts = creator.calculate_boost_factors()
        assert creator_boosts["endorsement_value"] == 1.3
        
        # Test community contributor bonus
        contributor = InfluenceScore(score=100.0, community_contributions=60)
        contributor_boosts = contributor.calculate_boost_factors()
        assert contributor_boosts["endorsement_value"] == 1.4


class TestSocialBadge:
    """Test SocialBadge value object"""
    
    def test_create_valid_social_badge(self):
        badge = SocialBadge(
            badge_id="social_butterfly",
            name="Social Butterfly",
            description="Made 100 social connections",
            earned_at=datetime.now(timezone.utc),
            rarity="rare",
            category="social"
        )
        
        assert badge.badge_id == "social_butterfly"
        assert badge.name == "Social Butterfly"
        assert badge.rarity == "rare"
        assert badge.category == "social"
    
    def test_badge_validation(self):
        base_args = {
            "badge_id": "test_badge",
            "name": "Test Badge",
            "description": "Test description",
            "earned_at": datetime.now(timezone.utc)
        }
        
        with pytest.raises(ValueError, match="Invalid badge rarity"):
            SocialBadge(**base_args, rarity="invalid", category="social")
        
        with pytest.raises(ValueError, match="Invalid badge category"):
            SocialBadge(**base_args, rarity="common", category="invalid")
        
        with pytest.raises(ValueError, match="Badge ID cannot be empty"):
            SocialBadge(**{**base_args, "badge_id": ""}, rarity="common", category="social")
    
    def test_rarity_points(self):
        common_badge = SocialBadge(
            badge_id="common", name="Common", description="Test",
            earned_at=datetime.now(timezone.utc), rarity="common", category="social"
        )
        assert common_badge.rarity_points == 10
        
        legendary_badge = SocialBadge(
            badge_id="legendary", name="Legendary", description="Test",
            earned_at=datetime.now(timezone.utc), rarity="legendary", category="social"
        )
        assert legendary_badge.rarity_points == 100
    
    def test_badge_expiry(self):
        old_badge = SocialBadge(
            badge_id="old", name="Old Badge", description="Test",
            earned_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
            rarity="common", category="social"
        )
        
        # Non-expiring badge
        assert not old_badge.is_expired()
        
        # Expiring badge (6 months)
        assert old_badge.is_expired(expiry_months=6)


class TestConstellationInfo:
    """Test ConstellationInfo value object"""
    
    def test_create_valid_constellation_info(self):
        info = ConstellationInfo(
            constellation_id=123,
            name="Test Constellation",
            role=CommunityRole.ADMIN,
            member_since=datetime.now(timezone.utc),
            contribution_score=150
        )
        
        assert info.constellation_id == 123
        assert info.name == "Test Constellation"
        assert info.role == CommunityRole.ADMIN
        assert info.contribution_score == 150
    
    def test_constellation_info_validation(self):
        base_args = {
            "name": "Test",
            "role": CommunityRole.MEMBER,
            "member_since": datetime.now(timezone.utc)
        }
        
        with pytest.raises(ValueError, match="Constellation ID must be positive"):
            ConstellationInfo(constellation_id=0, **base_args)
        
        with pytest.raises(ValueError, match="Constellation name cannot be empty"):
            ConstellationInfo(constellation_id=1, **{**base_args, "name": ""})
        
        with pytest.raises(ValueError, match="Contribution score cannot be negative"):
            ConstellationInfo(constellation_id=1, **base_args, contribution_score=-10)
    
    def test_membership_duration(self):
        past_date = datetime.now(timezone.utc).replace(day=1)  # Earlier this month
        info = ConstellationInfo(
            constellation_id=1,
            name="Test",
            role=CommunityRole.MEMBER,
            member_since=past_date
        )
        
        assert info.membership_duration_days >= 0
    
    def test_leadership_role_check(self):
        owner = ConstellationInfo(1, "Test", CommunityRole.OWNER, datetime.now(timezone.utc))
        admin = ConstellationInfo(1, "Test", CommunityRole.ADMIN, datetime.now(timezone.utc))
        moderator = ConstellationInfo(1, "Test", CommunityRole.MODERATOR, datetime.now(timezone.utc))
        member = ConstellationInfo(1, "Test", CommunityRole.MEMBER, datetime.now(timezone.utc))
        
        assert owner.is_leadership_role is True
        assert admin.is_leadership_role is True
        assert moderator.is_leadership_role is True
        assert member.is_leadership_role is False
    
    def test_loyalty_bonus_calculation(self):
        # Test with leadership role
        leader_info = ConstellationInfo(
            1, "Test", CommunityRole.OWNER, 
            datetime.now(timezone.utc), contribution_score=500
        )
        bonus = leader_info.calculate_loyalty_bonus()
        assert bonus >= 2  # Should have leadership bonus


class TestViralMetrics:
    """Test ViralMetrics value object"""
    
    def test_create_valid_viral_metrics(self):
        metrics = ViralMetrics(
            share_count=25,
            viral_score=150,
            engagement_rate=0.15,
            platform_shares={"twitter": 10, "instagram": 15},
            reach_estimate=5000
        )
        
        assert metrics.share_count == 25
        assert metrics.viral_score == 150
        assert metrics.engagement_rate == 0.15
        assert metrics.platform_shares["twitter"] == 10
        assert metrics.reach_estimate == 5000
    
    def test_viral_metrics_validation(self):
        valid_args = {
            "share_count": 10,
            "viral_score": 50,
            "engagement_rate": 0.1,
            "platform_shares": {"twitter": 5}
        }
        
        with pytest.raises(ValueError, match="Share count cannot be negative"):
            ViralMetrics(**{**valid_args, "share_count": -1})
        
        with pytest.raises(ValueError, match="Engagement rate must be between 0 and 1"):
            ViralMetrics(**{**valid_args, "engagement_rate": 1.5})
    
    def test_total_platform_shares(self):
        metrics = ViralMetrics(
            share_count=25,
            viral_score=100,
            engagement_rate=0.1,
            platform_shares={"twitter": 10, "instagram": 8, "facebook": 7}
        )
        
        assert metrics.total_platform_shares == 25
    
    def test_virality_tiers(self):
        assert ViralMetrics(0, 1500, 0.1, {}).virality_tier == "Cosmic Viral"
        assert ViralMetrics(0, 750, 0.1, {}).virality_tier == "Stellar Hit"
        assert ViralMetrics(0, 150, 0.1, {}).virality_tier == "Popular"
        assert ViralMetrics(0, 50, 0.1, {}).virality_tier == "Trending"
        assert ViralMetrics(0, 10, 0.1, {}).virality_tier == "Emerging"
    
    def test_influence_points_calculation(self):
        metrics = ViralMetrics(
            share_count=20,
            viral_score=200,
            engagement_rate=0.2,
            platform_shares={"twitter": 20},
            reach_estimate=10000
        )
        
        influence_points = metrics.calculate_influence_points()
        assert influence_points > 0
        
        # Should include base points, engagement bonus, and reach bonus
        expected = (200 * 0.1) + (0.2 * 50) + min(10000 / 1000, 100)
        assert influence_points == expected


class TestPrestigeLevel:
    """Test PrestigeLevel value object"""
    
    def test_create_valid_prestige_level(self):
        badges = [
            SocialBadge("test1", "Test 1", "Desc", datetime.now(timezone.utc), "common", "social"),
            SocialBadge("test2", "Test 2", "Desc", datetime.now(timezone.utc), "rare", "leadership")
        ]
        
        prestige = PrestigeLevel(
            verification_tier=VerificationTier.SILVER,
            verification_date=datetime.now(timezone.utc),
            spotlight_count=5,
            spotlight_votes=100,
            is_spotlight_eligible=True,
            aura_color="#FF5733",
            custom_title="Master Trader",
            badge_collection=badges
        )
        
        assert prestige.verification_tier == VerificationTier.SILVER
        assert prestige.spotlight_count == 5
        assert prestige.custom_title == "Master Trader"
        assert len(prestige.badge_collection) == 2
    
    def test_prestige_validation(self):
        with pytest.raises(ValueError, match="Spotlight count cannot be negative"):
            PrestigeLevel(VerificationTier.NONE, spotlight_count=-1)
        
        with pytest.raises(ValueError, match="Aura color must be valid hex color"):
            PrestigeLevel(VerificationTier.NONE, aura_color="invalid")
        
        with pytest.raises(ValueError, match="Custom title cannot exceed 100 characters"):
            PrestigeLevel(VerificationTier.NONE, custom_title="x" * 101)
    
    def test_verification_status(self):
        unverified = PrestigeLevel(VerificationTier.NONE)
        verified = PrestigeLevel(VerificationTier.GOLD)
        
        assert not unverified.is_verified
        assert verified.is_verified
        assert verified.verification_name == "Gold Verified"
    
    def test_badge_management(self):
        badges = [
            SocialBadge("social1", "Social 1", "Desc", datetime.now(timezone.utc), "common", "social"),
            SocialBadge("leadership1", "Leadership 1", "Desc", datetime.now(timezone.utc), "epic", "leadership"),
            SocialBadge("social2", "Social 2", "Desc", datetime.now(timezone.utc), "rare", "social")
        ]
        
        prestige = PrestigeLevel(VerificationTier.NONE, badge_collection=badges)
        
        # Test total badge points
        expected_points = 10 + 50 + 25  # common + epic + rare
        assert prestige.total_badge_points == expected_points
        
        # Test badges by category
        social_badges = prestige.get_badges_by_category("social")
        assert len(social_badges) == 2
        
        leadership_badges = prestige.get_badges_by_category("leadership")
        assert len(leadership_badges) == 1
    
    def test_prestige_score_calculation(self):
        badges = [SocialBadge("test", "Test", "Desc", datetime.now(timezone.utc), "legendary", "social")]
        
        prestige = PrestigeLevel(
            verification_tier=VerificationTier.GOLD,
            spotlight_count=3,
            spotlight_votes=250,
            badge_collection=badges
        )
        
        score = prestige.calculate_prestige_score()
        
        # Should include verification (3*25) + spotlight (3*10) + votes (250) + badges (100)
        expected = 75 + 30 + 250 + 100
        assert score == expected


class TestSocialInteractionContext:
    """Test SocialInteractionContext value object"""
    
    def test_create_valid_interaction_context(self):
        context = SocialInteractionContext(
            interaction_type=SocialInteractionType.ENDORSEMENT,
            target_user_id=123,
            context_data={"reason": "great_trader"},
            interaction_weight=1.5,
            requires_verification=True
        )
        
        assert context.interaction_type == SocialInteractionType.ENDORSEMENT
        assert context.target_user_id == 123
        assert context.context_data["reason"] == "great_trader"
        assert context.interaction_weight == 1.5
        assert context.requires_verification is True
    
    def test_interaction_validation(self):
        with pytest.raises(ValueError, match="Target user ID must be positive"):
            SocialInteractionContext(SocialInteractionType.VOTE, 0)
        
        with pytest.raises(ValueError, match="Interaction weight must be between 0.1 and 5.0"):
            SocialInteractionContext(SocialInteractionType.VOTE, 1, interaction_weight=10.0)
    
    def test_positive_interaction_check(self):
        endorsement = SocialInteractionContext(SocialInteractionType.ENDORSEMENT, 1)
        report = SocialInteractionContext(SocialInteractionType.REPORT, 1)
        follow = SocialInteractionContext(SocialInteractionType.FOLLOW, 1)
        block = SocialInteractionContext(SocialInteractionType.BLOCK, 1)
        
        assert endorsement.is_positive_interaction is True
        assert report.is_positive_interaction is False
        assert follow.is_positive_interaction is True
        assert block.is_positive_interaction is False
    
    def test_impact_value_calculation(self):
        context = SocialInteractionContext(
            SocialInteractionType.ENDORSEMENT,
            target_user_id=1,
            interaction_weight=2.0
        )
        
        high_influence = InfluenceScore(score=1000.0)
        low_influence = InfluenceScore(score=10.0)
        
        high_impact = context.calculate_impact_value(high_influence)
        low_impact = context.calculate_impact_value(low_influence)
        
        # Higher influence should create higher impact
        assert high_impact > low_impact
        assert high_impact > 0
        assert low_impact > 0