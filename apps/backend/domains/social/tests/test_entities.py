"""
Test suite for Social Domain Entities

Tests aggregate root behavior, domain events, and business logic for all social entities.
"""

import pytest
from datetime import datetime, timezone
from decimal import Decimal

from ..entities import SocialProfile, Constellation, ViralContent, SocialInteraction
from ..value_objects import (
    SocialRating, InfluenceScore, PrestigeLevel, ConstellationInfo, 
    SocialInteractionContext, VerificationTier, CommunityRole, 
    ContentType, SocialInteractionType
)


class TestSocialProfile:
    """Test SocialProfile aggregate root"""
    
    def test_create_social_profile(self):
        rating = SocialRating(score=75.0)
        influence = InfluenceScore(score=200.0)
        prestige = PrestigeLevel(VerificationTier.SILVER)
        
        profile = SocialProfile(
            user_id=1,
            social_rating=rating,
            influence_score=influence,
            prestige_level=prestige
        )
        
        assert profile.user_id == 1
        assert profile.social_rating == rating
        assert profile.influence_score == influence
        assert profile.prestige_level == prestige
        assert len(profile.domain_events) > 0
    
    def test_receive_endorsement(self):
        profile = SocialProfile(
            user_id=1,
            social_rating=SocialRating(score=50.0),
            influence_score=InfluenceScore(score=100.0),
            prestige_level=PrestigeLevel(VerificationTier.NONE)
        )
        
        endorser_influence = InfluenceScore(score=300.0, constellation_leadership=True)
        old_score = profile.social_rating.score
        
        profile.receive_endorsement(endorser_influence)
        
        assert profile.social_rating.score > old_score
        assert profile.social_rating.endorsement_count == 1
    
    def test_join_constellation(self):
        profile = SocialProfile(
            user_id=1,
            social_rating=SocialRating(score=60.0),
            influence_score=InfluenceScore(score=150.0),
            prestige_level=PrestigeLevel(VerificationTier.NONE)
        )
        
        constellation_info = ConstellationInfo(
            constellation_id=1,
            name="Test Constellation",
            role=CommunityRole.ADMIN,
            member_since=datetime.now(timezone.utc)
        )
        
        old_influence = profile.influence_score.score
        profile.join_constellation(constellation_info)
        
        assert profile.constellation_info == constellation_info
        assert profile.influence_score.score > old_influence
        assert profile.influence_score.constellation_leadership is True


class TestConstellation:
    """Test Constellation aggregate root"""
    
    def test_create_constellation(self):
        constellation = Constellation(
            constellation_id=1,
            name="Test Constellation",
            owner_id=100,
            description="Test constellation",
            max_members=25
        )
        
        assert constellation.constellation_id == 1
        assert constellation.name == "Test Constellation"
        assert constellation.owner_id == 100
        assert constellation.member_count == 1  # Owner is first member
        assert len(constellation.domain_events) > 0
    
    def test_add_member(self):
        constellation = Constellation(1, "Test", 100, max_members=5)
        
        assert constellation.can_add_member()
        
        constellation.add_member(101)
        assert constellation.member_count == 2
        
        # Test domain events
        events = constellation.domain_events
        member_joined_events = [e for e in events if e.event_type == "constellation_member_joined"]
        assert len(member_joined_events) > 0
    
    def test_resource_contribution(self):
        constellation = Constellation(1, "Test", 100)
        
        constellation.contribute_resources(Decimal('1000'), Decimal('500'))
        
        assert constellation.total_stellar_shards == Decimal('1000')
        assert constellation.total_lumina == Decimal('500')
    
    def test_battle_result(self):
        constellation = Constellation(1, "Test", 100)
        
        constellation.record_battle_result(won=True, rating_change=Decimal('50'))
        
        assert constellation.total_battles == 1
        assert constellation.battles_won == 1
        assert constellation.win_rate == 1.0
        assert constellation.battle_rating == Decimal('1050.0')


class TestViralContent:
    """Test ViralContent aggregate root"""
    
    def test_create_viral_content(self):
        content = ViralContent(
            content_id=1,
            user_id=200,
            content_type=ContentType.MEME,
            content_title="Test Meme",
            content_data={"template": "success_kid", "text": "Made profit!"}
        )
        
        assert content.content_id == 1
        assert content.user_id == 200
        assert content.content_type == ContentType.MEME
        assert content.content_title == "Test Meme"
        assert content.viral_metrics.share_count == 0
    
    def test_share_to_platform(self):
        content = ViralContent(
            1, 200, ContentType.MEME, "Test", {"template": "test"}
        )
        
        content.share_to_platform("twitter", reach_estimate=1000)
        
        assert content.viral_metrics.share_count == 1
        assert content.viral_metrics.platform_shares["twitter"] == 1
        assert content.viral_metrics.viral_score > 0
        assert content.viral_metrics.reach_estimate == 1000
        
        # Test domain events
        events = content.domain_events
        shared_events = [e for e in events if e.event_type == "viral_content_shared"]
        assert len(shared_events) > 0


class TestSocialInteraction:
    """Test SocialInteraction entity"""
    
    def test_create_social_interaction(self):
        context = SocialInteractionContext(
            interaction_type=SocialInteractionType.ENDORSEMENT,
            target_user_id=300
        )
        
        source_influence = InfluenceScore(score=250.0)
        
        interaction = SocialInteraction(
            interaction_id=1,
            source_user_id=301,
            target_user_id=300,
            interaction_context=context,
            source_influence=source_influence
        )
        
        assert interaction.interaction_id == 1
        assert interaction.source_user_id == 301
        assert interaction.target_user_id == 300
        assert interaction.impact_value > 0
        assert not interaction.is_processed
        assert len(interaction.domain_events) > 0
    
    def test_mark_processed(self):
        context = SocialInteractionContext(
            SocialInteractionType.VOTE, 300
        )
        
        interaction = SocialInteraction(
            1, 301, 300, context, InfluenceScore(score=100.0)
        )
        
        interaction.mark_processed()
        
        assert interaction.is_processed
        assert interaction.processed_at is not None