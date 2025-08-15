"""
Social Domain Services

Domain services implementing complex business logic for social interactions,
constellation management, and viral content operations.

Services implemented:
- SocialProfileService: Manages user social profiles and reputation
- ConstellationService: Handles clan operations and battles  
- ViralContentService: Manages content creation and sharing
- SocialInteractionService: Processes social interactions between users

Architecture follows DDD patterns with:
- Domain service coordination of multiple aggregates
- Business rule enforcement across entities
- Integration with external domains through events
- Repository pattern for data persistence
"""

from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any, Tuple
from abc import ABC, abstractmethod

from .entities import SocialProfile, Constellation, ViralContent, SocialInteraction
from .value_objects import (
    SocialRating, InfluenceScore, SocialBadge, ConstellationInfo, ViralMetrics,
    PrestigeLevel, SocialInteractionContext, CommunityRole, VerificationTier,
    ContentType, ModerationStatus, SocialInteractionType
)
from ..shared.repositories import Repository


class SocialProfileRepository(Repository[SocialProfile]):
    """Repository interface for SocialProfile aggregate"""
    
    @abstractmethod
    async def find_by_user_id(self, user_id: int) -> Optional[SocialProfile]:
        """Find social profile by user ID"""
        pass
    
    @abstractmethod 
    async def find_by_social_rating_range(self, min_rating: float, max_rating: float) -> List[SocialProfile]:
        """Find profiles within social rating range"""
        pass
    
    @abstractmethod
    async def find_top_influencers(self, limit: int = 10) -> List[SocialProfile]:
        """Find top influencers by influence score"""
        pass


class ConstellationRepository(Repository[Constellation]):
    """Repository interface for Constellation aggregate"""
    
    @abstractmethod
    async def find_by_name(self, name: str) -> Optional[Constellation]:
        """Find constellation by name"""
        pass
    
    @abstractmethod
    async def find_by_owner_id(self, owner_id: int) -> Optional[Constellation]:
        """Find constellation owned by user"""
        pass
    
    @abstractmethod
    async def find_public_constellations(self, limit: int = 20) -> List[Constellation]:
        """Find public constellations for discovery"""
        pass
    
    @abstractmethod
    async def find_by_battle_rating_range(self, min_rating: float, max_rating: float) -> List[Constellation]:
        """Find constellations within battle rating range"""
        pass


class ViralContentRepository(Repository[ViralContent]):
    """Repository interface for ViralContent aggregate"""
    
    @abstractmethod
    async def find_by_user_id(self, user_id: int) -> List[ViralContent]:
        """Find viral content created by user"""
        pass
    
    @abstractmethod
    async def find_trending_content(self, limit: int = 20) -> List[ViralContent]:
        """Find trending viral content by viral score"""
        pass
    
    @abstractmethod
    async def find_featured_content(self, limit: int = 10) -> List[ViralContent]:
        """Find featured content"""
        pass
    
    @abstractmethod
    async def find_by_content_type(self, content_type: ContentType) -> List[ViralContent]:
        """Find content by type"""
        pass


class SocialInteractionRepository(Repository[SocialInteraction]):
    """Repository interface for SocialInteraction aggregate"""
    
    @abstractmethod
    async def find_by_target_user(self, user_id: int, limit: int = 50) -> List[SocialInteraction]:
        """Find interactions targeting a user"""
        pass
    
    @abstractmethod
    async def find_by_source_user(self, user_id: int, limit: int = 50) -> List[SocialInteraction]:
        """Find interactions performed by a user"""
        pass
    
    @abstractmethod
    async def find_recent_interactions(self, user_id: int, hours: int = 24) -> List[SocialInteraction]:
        """Find recent interactions by user"""
        pass


class SocialProfileService:
    """
    Domain service for managing user social profiles and reputation systems.
    
    Handles profile creation, reputation updates, badge management, and verification.
    """
    
    def __init__(self, profile_repository: SocialProfileRepository):
        self._profile_repository = profile_repository
    
    async def create_social_profile(self, user_id: int) -> SocialProfile:
        """Create a new social profile for a user"""
        # Check if profile already exists
        existing_profile = await self._profile_repository.find_by_user_id(user_id)
        if existing_profile:
            raise ValueError(f"Social profile already exists for user {user_id}")
        
        # Create initial social profile with default values
        initial_rating = SocialRating(score=50.0)  # Start at middle rating
        initial_influence = InfluenceScore(score=0.0)
        initial_prestige = PrestigeLevel(verification_tier=VerificationTier.NONE)
        
        profile = SocialProfile(
            user_id=user_id,
            social_rating=initial_rating,
            influence_score=initial_influence,
            prestige_level=initial_prestige
        )
        
        await self._profile_repository.save(profile)
        return profile
    
    async def update_social_rating(
        self, 
        user_id: int, 
        endorser_user_id: int,
        interaction_type: SocialInteractionType
    ) -> SocialProfile:
        """Update user's social rating based on interaction from another user"""
        profile = await self._profile_repository.find_by_user_id(user_id)
        if not profile:
            raise ValueError(f"Social profile not found for user {user_id}")
        
        endorser_profile = await self._profile_repository.find_by_user_id(endorser_user_id)
        if not endorser_profile:
            raise ValueError(f"Endorser profile not found for user {endorser_user_id}")
        
        # Process interaction based on type
        if interaction_type == SocialInteractionType.ENDORSEMENT:
            profile.receive_endorsement(endorser_profile.influence_score)
        elif interaction_type == SocialInteractionType.REPORT:
            profile.receive_negative_feedback("reported_by_user")
        # Add more interaction types as needed
        
        await self._profile_repository.save(profile)
        return profile
    
    async def award_social_badge(self, user_id: int, badge: SocialBadge) -> SocialProfile:
        """Award a social badge to a user"""
        profile = await self._profile_repository.find_by_user_id(user_id)
        if not profile:
            raise ValueError(f"Social profile not found for user {user_id}")
        
        profile.earn_badge(badge)
        await self._profile_repository.save(profile)
        return profile
    
    async def verify_user(self, user_id: int, verification_tier: VerificationTier) -> SocialProfile:
        """Update user's verification status"""
        profile = await self._profile_repository.find_by_user_id(user_id)
        if not profile:
            raise ValueError(f"Social profile not found for user {user_id}")
        
        profile.update_verification(verification_tier)
        await self._profile_repository.save(profile)
        return profile
    
    async def get_social_leaderboard(self, limit: int = 20) -> List[Tuple[SocialProfile, float]]:
        """Get social leaderboard based on overall social scores"""
        profiles = await self._profile_repository.find_all()
        
        # Calculate overall scores and sort
        profile_scores = []
        for profile in profiles:
            overall_score = profile.calculate_overall_score()
            profile_scores.append((profile, overall_score))
        
        # Sort by score descending and limit results
        profile_scores.sort(key=lambda x: x[1], reverse=True)
        return profile_scores[:limit]
    
    async def calculate_reputation_trends(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Calculate reputation trends and analytics for a user"""
        profile = await self._profile_repository.find_by_user_id(user_id)
        if not profile:
            raise ValueError(f"Social profile not found for user {user_id}")
        
        # This would typically involve historical data analysis
        # For now, return current state with trend indicators
        return {
            "current_social_rating": profile.social_rating.score,
            "rating_percentile": profile.social_rating.percentage,
            "influence_score": profile.influence_score.score,
            "influence_tier": profile.influence_score.influence_tier,
            "verification_status": profile.prestige_level.verification_name,
            "badge_count": len(profile.prestige_level.badge_collection),
            "overall_score": profile.calculate_overall_score(),
            "constellation_member": profile.constellation_info is not None,
            "days_analyzed": days
        }


class ConstellationService:
    """
    Domain service for managing constellation/clan operations.
    
    Handles constellation creation, membership management, battles, and resource sharing.
    """
    
    def __init__(
        self, 
        constellation_repository: ConstellationRepository,
        profile_repository: SocialProfileRepository
    ):
        self._constellation_repository = constellation_repository
        self._profile_repository = profile_repository
    
    async def create_constellation(
        self,
        owner_id: int,
        name: str,
        description: Optional[str] = None,
        constellation_color: str = "#7B2CBF",
        constellation_emblem: str = "star",
        is_public: bool = True,
        max_members: int = 50
    ) -> Constellation:
        """Create a new constellation/clan"""
        # Check if name is already taken
        existing = await self._constellation_repository.find_by_name(name)
        if existing:
            raise ValueError(f"Constellation name '{name}' is already taken")
        
        # Check if user already owns a constellation
        owned_constellation = await self._constellation_repository.find_by_owner_id(owner_id)
        if owned_constellation:
            raise ValueError(f"User {owner_id} already owns a constellation")
        
        # Generate new constellation ID (would typically come from database)
        constellation_id = hash(f"{owner_id}_{name}_{datetime.now().timestamp()}") % 1000000
        
        constellation = Constellation(
            constellation_id=constellation_id,
            name=name,
            owner_id=owner_id,
            description=description,
            constellation_color=constellation_color,
            constellation_emblem=constellation_emblem,
            is_public=is_public,
            max_members=max_members
        )
        
        await self._constellation_repository.save(constellation)
        
        # Update owner's social profile with constellation info
        owner_profile = await self._profile_repository.find_by_user_id(owner_id)
        if owner_profile:
            constellation_info = ConstellationInfo(
                constellation_id=constellation_id,
                name=name,
                role=CommunityRole.OWNER,
                member_since=constellation.created_at
            )
            owner_profile.join_constellation(constellation_info)
            await self._profile_repository.save(owner_profile)
        
        return constellation
    
    async def join_constellation(self, user_id: int, constellation_id: int) -> Tuple[Constellation, SocialProfile]:
        """Add a user to a constellation"""
        constellation = await self._constellation_repository.find_by_id(constellation_id)
        if not constellation:
            raise ValueError(f"Constellation {constellation_id} not found")
        
        if not constellation.can_add_member():
            raise ValueError("Cannot join: constellation is full or private")
        
        profile = await self._profile_repository.find_by_user_id(user_id)
        if not profile:
            raise ValueError(f"Social profile not found for user {user_id}")
        
        if profile.constellation_info is not None:
            raise ValueError("User is already a member of a constellation")
        
        # Add member to constellation
        constellation.add_member(user_id)
        await self._constellation_repository.save(constellation)
        
        # Update user's social profile
        constellation_info = ConstellationInfo(
            constellation_id=constellation_id,
            name=constellation.name,
            role=CommunityRole.MEMBER,
            member_since=datetime.now(timezone.utc)
        )
        profile.join_constellation(constellation_info)
        await self._profile_repository.save(profile)
        
        return constellation, profile
    
    async def leave_constellation(self, user_id: int) -> SocialProfile:
        """Remove a user from their current constellation"""
        profile = await self._profile_repository.find_by_user_id(user_id)
        if not profile:
            raise ValueError(f"Social profile not found for user {user_id}")
        
        if profile.constellation_info is None:
            raise ValueError("User is not a member of any constellation")
        
        constellation_id = profile.constellation_info.constellation_id
        constellation = await self._constellation_repository.find_by_id(constellation_id)
        
        if constellation:
            if constellation.owner_id == user_id:
                raise ValueError("Constellation owner cannot leave (transfer ownership first)")
            
            constellation.remove_member(user_id)
            await self._constellation_repository.save(constellation)
        
        profile.leave_constellation()
        await self._profile_repository.save(profile)
        
        return profile
    
    async def contribute_to_constellation(
        self, 
        user_id: int, 
        stellar_shards: Decimal, 
        lumina: Decimal
    ) -> Tuple[Constellation, SocialProfile]:
        """Contribute resources to user's constellation"""
        profile = await self._profile_repository.find_by_user_id(user_id)
        if not profile or not profile.constellation_info:
            raise ValueError("User is not a member of any constellation")
        
        constellation_id = profile.constellation_info.constellation_id
        constellation = await self._constellation_repository.find_by_id(constellation_id)
        if not constellation:
            raise ValueError("Constellation not found")
        
        # Record contribution
        constellation.contribute_resources(stellar_shards, lumina)
        await self._constellation_repository.save(constellation)
        
        # Update user's contribution score (this would typically be tracked separately)
        # For now, we'll create an updated constellation info
        updated_info = ConstellationInfo(
            constellation_id=profile.constellation_info.constellation_id,
            name=profile.constellation_info.name,
            role=profile.constellation_info.role,
            member_since=profile.constellation_info.member_since,
            contribution_score=profile.constellation_info.contribution_score + int(stellar_shards + lumina)
        )
        
        # This would require updating the profile's constellation info
        # In a real implementation, this would be handled differently
        
        return constellation, profile
    
    async def initiate_constellation_battle(
        self,
        challenger_id: int,
        defender_id: int,
        battle_type: str = "trading_duel",
        duration_hours: int = 24
    ) -> Dict[str, Any]:
        """Initiate a battle between two constellations"""
        challenger = await self._constellation_repository.find_by_id(challenger_id)
        defender = await self._constellation_repository.find_by_id(defender_id)
        
        if not challenger or not defender:
            raise ValueError("One or both constellations not found")
        
        if challenger_id == defender_id:
            raise ValueError("Constellation cannot battle itself")
        
        # Check battle eligibility (rating difference, cooldowns, etc.)
        rating_diff = abs(float(challenger.battle_rating - defender.battle_rating))
        if rating_diff > 500:  # Prevent mismatched battles
            raise ValueError("Battle rating difference too large")
        
        # Create battle record (this would typically involve a separate Battle entity)
        battle_info = {
            "battle_id": hash(f"{challenger_id}_{defender_id}_{datetime.now().timestamp()}") % 1000000,
            "challenger_id": challenger_id,
            "defender_id": defender_id,
            "battle_type": battle_type,
            "duration_hours": duration_hours,
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        return battle_info
    
    async def find_constellation_matches(self, constellation_id: int, limit: int = 10) -> List[Constellation]:
        """Find suitable constellation battle opponents"""
        constellation = await self._constellation_repository.find_by_id(constellation_id)
        if not constellation:
            raise ValueError("Constellation not found")
        
        # Find constellations with similar battle ratings
        rating = float(constellation.battle_rating)
        min_rating = rating - 200
        max_rating = rating + 200
        
        matches = await self._constellation_repository.find_by_battle_rating_range(min_rating, max_rating)
        
        # Filter out the constellation itself and return limited results
        matches = [c for c in matches if c.constellation_id != constellation_id]
        return matches[:limit]


class ViralContentService:
    """
    Domain service for managing viral content creation and sharing.
    
    Handles content creation, sharing, moderation, and virality tracking.
    """
    
    def __init__(
        self,
        content_repository: ViralContentRepository,
        profile_repository: SocialProfileRepository
    ):
        self._content_repository = content_repository
        self._profile_repository = profile_repository
    
    async def create_viral_content(
        self,
        user_id: int,
        content_type: ContentType,
        content_title: str,
        content_data: Dict[str, Any],
        content_description: Optional[str] = None,
        template_id: Optional[str] = None,
        is_public: bool = True
    ) -> ViralContent:
        """Create new viral content"""
        # Validate user exists
        profile = await self._profile_repository.find_by_user_id(user_id)
        if not profile:
            raise ValueError(f"Social profile not found for user {user_id}")
        
        # Generate content ID
        content_id = hash(f"{user_id}_{content_title}_{datetime.now().timestamp()}") % 1000000
        
        content = ViralContent(
            content_id=content_id,
            user_id=user_id,
            content_type=content_type,
            content_title=content_title,
            content_data=content_data,
            content_description=content_description,
            template_id=template_id,
            is_public=is_public
        )
        
        await self._content_repository.save(content)
        return content
    
    async def share_content_to_platform(
        self,
        content_id: int,
        platform: str,
        reach_estimate: int = 0
    ) -> ViralContent:
        """Share content to a social platform and update metrics"""
        content = await self._content_repository.find_by_id(content_id)
        if not content:
            raise ValueError(f"Viral content {content_id} not found")
        
        if content.moderation_status != ModerationStatus.APPROVED:
            raise ValueError("Cannot share content that is not approved")
        
        content.share_to_platform(platform, reach_estimate)
        await self._content_repository.save(content)
        
        # Update creator's influence score
        profile = await self._profile_repository.find_by_user_id(content.user_id)
        if profile:
            influence_boost = content.calculate_influence_contribution() * 0.01  # Small boost per share
            new_influence = InfluenceScore(
                score=profile.influence_score.score + influence_boost,
                viral_content_count=profile.influence_score.viral_content_count + (1 if platform == "first_share" else 0),
                constellation_leadership=profile.influence_score.constellation_leadership,
                community_contributions=profile.influence_score.community_contributions,
                follower_count=profile.influence_score.follower_count
            )
            # Update would require profile modification - simplified for this example
        
        return content
    
    async def moderate_content(
        self,
        content_id: int,
        status: ModerationStatus,
        reason: Optional[str] = None
    ) -> ViralContent:
        """Moderate viral content"""
        content = await self._content_repository.find_by_id(content_id)
        if not content:
            raise ValueError(f"Viral content {content_id} not found")
        
        content.moderate_content(status, reason)
        await self._content_repository.save(content)
        return content
    
    async def feature_content(self, content_id: int) -> ViralContent:
        """Feature viral content for promotion"""
        content = await self._content_repository.find_by_id(content_id)
        if not content:
            raise ValueError(f"Viral content {content_id} not found")
        
        content.feature_content()
        await self._content_repository.save(content)
        return content
    
    async def get_trending_content(self, limit: int = 20, content_type: Optional[ContentType] = None) -> List[ViralContent]:
        """Get trending viral content"""
        if content_type:
            all_content = await self._content_repository.find_by_content_type(content_type)
        else:
            all_content = await self._content_repository.find_trending_content(limit * 2)
        
        # Sort by viral score and recent activity
        now = datetime.now(timezone.utc)
        scored_content = []
        
        for content in all_content:
            # Calculate trending score (viral score + recency bonus)
            days_old = (now - content._created_at).days
            recency_bonus = max(0, 7 - days_old) * 10  # Bonus for recent content
            trending_score = content.viral_metrics.viral_score + recency_bonus
            scored_content.append((content, trending_score))
        
        # Sort by trending score and return top results
        scored_content.sort(key=lambda x: x[1], reverse=True)
        return [content for content, _ in scored_content[:limit]]
    
    async def get_user_content_analytics(self, user_id: int) -> Dict[str, Any]:
        """Get analytics for user's viral content"""
        user_content = await self._content_repository.find_by_user_id(user_id)
        
        if not user_content:
            return {
                "total_content": 0,
                "total_shares": 0,
                "total_viral_score": 0,
                "average_engagement": 0.0,
                "top_content": None
            }
        
        # Calculate analytics
        total_shares = sum(content.viral_metrics.share_count for content in user_content)
        total_viral_score = sum(content.viral_metrics.viral_score for content in user_content)
        avg_engagement = sum(content.viral_metrics.engagement_rate for content in user_content) / len(user_content)
        
        # Find top performing content
        top_content = max(user_content, key=lambda c: c.viral_metrics.viral_score)
        
        return {
            "total_content": len(user_content),
            "total_shares": total_shares,
            "total_viral_score": total_viral_score,
            "average_engagement": avg_engagement,
            "top_content": {
                "content_id": top_content.content_id,
                "title": top_content.content_title,
                "viral_score": top_content.viral_metrics.viral_score,
                "share_count": top_content.viral_metrics.share_count
            },
            "content_by_type": self._group_content_by_type(user_content)
        }
    
    def _group_content_by_type(self, content_list: List[ViralContent]) -> Dict[str, int]:
        """Group content by type for analytics"""
        type_counts = {}
        for content in content_list:
            content_type = content.content_type.value
            type_counts[content_type] = type_counts.get(content_type, 0) + 1
        return type_counts


class SocialInteractionService:
    """
    Domain service for processing social interactions between users.
    
    Handles endorsements, votes, follows, and other social actions.
    """
    
    def __init__(
        self,
        interaction_repository: SocialInteractionRepository,
        profile_repository: SocialProfileRepository
    ):
        self._interaction_repository = interaction_repository
        self._profile_repository = profile_repository
    
    async def process_social_interaction(
        self,
        source_user_id: int,
        target_user_id: int,
        interaction_type: SocialInteractionType,
        context_data: Optional[Dict[str, Any]] = None,
        interaction_weight: float = 1.0
    ) -> SocialInteraction:
        """Process a social interaction between users"""
        if source_user_id == target_user_id:
            raise ValueError("Users cannot interact with themselves")
        
        # Get source user profile for influence calculation
        source_profile = await self._profile_repository.find_by_user_id(source_user_id)
        if not source_profile:
            raise ValueError(f"Source user profile not found for user {source_user_id}")
        
        # Check for spam/rate limiting
        recent_interactions = await self._interaction_repository.find_recent_interactions(source_user_id, 1)
        if len(recent_interactions) > 10:  # Max 10 interactions per hour
            raise ValueError("Too many interactions in the past hour")
        
        # Create interaction context
        interaction_context = SocialInteractionContext(
            interaction_type=interaction_type,
            target_user_id=target_user_id,
            context_data=context_data or {},
            interaction_weight=interaction_weight
        )
        
        # Generate interaction ID
        interaction_id = hash(f"{source_user_id}_{target_user_id}_{datetime.now().timestamp()}") % 1000000
        
        # Create interaction
        interaction = SocialInteraction(
            interaction_id=interaction_id,
            source_user_id=source_user_id,
            target_user_id=target_user_id,
            interaction_context=interaction_context,
            source_influence=source_profile.influence_score
        )
        
        await self._interaction_repository.save(interaction)
        
        # Process the interaction effects on target user
        await self._apply_interaction_effects(interaction)
        
        return interaction
    
    async def _apply_interaction_effects(self, interaction: SocialInteraction) -> None:
        """Apply the effects of a social interaction to the target user"""
        target_profile = await self._profile_repository.find_by_user_id(interaction.target_user_id)
        if not target_profile:
            return  # Skip if target profile doesn't exist
        
        interaction_type = interaction.interaction_context.interaction_type
        
        if interaction_type == SocialInteractionType.ENDORSEMENT:
            # Get source profile for endorsement processing
            source_profile = await self._profile_repository.find_by_user_id(interaction.source_user_id)
            if source_profile:
                target_profile.receive_endorsement(source_profile.influence_score)
                await self._profile_repository.save(target_profile)
        
        elif interaction_type == SocialInteractionType.REPORT:
            target_profile.receive_negative_feedback("reported_by_user")
            await self._profile_repository.save(target_profile)
        
        # Mark interaction as processed
        interaction.mark_processed()
        await self._interaction_repository.save(interaction)
    
    async def get_user_interaction_summary(self, user_id: int) -> Dict[str, Any]:
        """Get summary of interactions for a user"""
        received_interactions = await self._interaction_repository.find_by_target_user(user_id, 100)
        sent_interactions = await self._interaction_repository.find_by_source_user(user_id, 100)
        
        # Analyze received interactions
        received_by_type = {}
        for interaction in received_interactions:
            itype = interaction.interaction_context.interaction_type.value
            received_by_type[itype] = received_by_type.get(itype, 0) + 1
        
        # Analyze sent interactions
        sent_by_type = {}
        for interaction in sent_interactions:
            itype = interaction.interaction_context.interaction_type.value
            sent_by_type[itype] = sent_by_type.get(itype, 0) + 1
        
        return {
            "received_interactions": {
                "total": len(received_interactions),
                "by_type": received_by_type,
                "recent_count": len([i for i in received_interactions if 
                                  (datetime.now(timezone.utc) - i.created_at).days <= 7])
            },
            "sent_interactions": {
                "total": len(sent_interactions),
                "by_type": sent_by_type,
                "recent_count": len([i for i in sent_interactions if 
                                   (datetime.now(timezone.utc) - i.created_at).days <= 7])
            }
        }
    
    async def calculate_interaction_impact(
        self,
        source_user_id: int,
        target_user_id: int,
        interaction_type: SocialInteractionType
    ) -> float:
        """Calculate the potential impact of an interaction before processing"""
        source_profile = await self._profile_repository.find_by_user_id(source_user_id)
        if not source_profile:
            return 0.0
        
        # Create temporary interaction context to calculate impact
        temp_context = SocialInteractionContext(
            interaction_type=interaction_type,
            target_user_id=target_user_id
        )
        
        return temp_context.calculate_impact_value(source_profile.influence_score)