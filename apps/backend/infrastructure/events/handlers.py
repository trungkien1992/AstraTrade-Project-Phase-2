"""
Cross-Domain Event Handlers

Event handlers that implement cross-domain business logic and integration.
These handlers demonstrate how events from one domain can trigger actions in other domains.

Key Integration Examples:
- Trading events → Gamification XP rewards
- Social interactions → Gamification streaks  
- Financial events → User profile updates
- Achievement unlocks → Social viral content
"""

import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, Any, Optional

from domains.shared.events import EventHandler, DomainEvent
from .schemas import (
    TradeExecutedEvent, SocialRatingChangedEvent, XPAwardedEvent,
    AchievementUnlockedEvent, LevelUpEvent, ViralContentSharedEvent,
    EventMetadata, DomainType, EventVersion
)

logger = logging.getLogger(__name__)


class TradingToGamificationHandler(EventHandler):
    """
    Handles trading events to award gamification XP and achievements.
    
    Business Rules:
    - Successful trades award base XP (10-50 based on trade size)
    - Consecutive profitable trades award streak bonuses  
    - Large trades (>$1000) award achievement progress
    - First trade awards "First Steps" achievement
    """
    
    def __init__(self, event_bus, gamification_service):
        self.event_bus = event_bus
        self.gamification_service = gamification_service
        self.user_trade_counts = {}  # Simple in-memory cache
    
    async def handle(self, event: Dict[str, Any]) -> None:
        """Handle TradeExecutedEvent to award XP and check achievements"""
        try:
            # Parse event data
            trade_event = TradeExecutedEvent(**event)
            user_id = trade_event.user_id
            
            logger.info(f"Processing trade event for user {user_id}: {trade_event.trade_id}")
            
            # Calculate base XP reward
            xp_amount = self._calculate_trade_xp(trade_event)
            
            # Award XP
            if xp_amount > 0:
                await self._award_xp(user_id, xp_amount, trade_event.trade_id)
            
            # Check for achievements
            await self._check_trading_achievements(user_id, trade_event)
            
            # Update streak if profitable
            if trade_event.pnl_usd and trade_event.pnl_usd > 0:
                await self._update_profitable_streak(user_id)
            
        except Exception as e:
            logger.error(f"Failed to handle trading event: {e}")
    
    def _calculate_trade_xp(self, trade_event: TradeExecutedEvent) -> int:
        """Calculate XP reward based on trade characteristics"""
        base_xp = 10
        
        # Size bonus (more XP for larger trades)
        trade_size_usd = float(trade_event.amount * trade_event.entry_price)
        size_multiplier = min(1.0 + (trade_size_usd / 1000), 5.0)  # Max 5x
        
        # Profitability bonus
        profit_multiplier = 1.0
        if trade_event.pnl_usd:
            if trade_event.pnl_usd > 0:
                profit_multiplier = 1.5  # 50% bonus for profitable trades
            elif trade_event.pnl_usd < -100:  # Large loss penalty
                profit_multiplier = 0.5
        
        return int(base_xp * size_multiplier * profit_multiplier)
    
    async def _award_xp(self, user_id: int, xp_amount: int, trade_id: str) -> None:
        """Award XP and emit event"""
        xp_event_data = {
            "metadata": EventMetadata(
                event_id=f"xp_award_{trade_id}",
                event_type="xp_awarded",
                domain=DomainType.GAMIFICATION,
                occurred_at=datetime.now(timezone.utc),
                correlation_id=trade_id
            ),
            "user_id": user_id,
            "xp_amount": xp_amount,
            "xp_source": "trade",
            "source_id": trade_id,
            "multiplier": Decimal("1.0")
        }
        
        await self.event_bus.emit(XPAwardedEvent(**xp_event_data))
        logger.info(f"Awarded {xp_amount} XP to user {user_id} for trade {trade_id}")
    
    async def _check_trading_achievements(self, user_id: int, trade_event: TradeExecutedEvent) -> None:
        """Check and award trading-related achievements"""
        # Track user trade count
        if user_id not in self.user_trade_counts:
            self.user_trade_counts[user_id] = 0
        self.user_trade_counts[user_id] += 1
        
        trade_count = self.user_trade_counts[user_id]
        
        # First trade achievement
        if trade_count == 1:
            await self._award_achievement(user_id, "first_trade", "First Steps", "bronze", 50)
        
        # Milestone achievements
        elif trade_count == 10:
            await self._award_achievement(user_id, "ten_trades", "Getting Started", "silver", 100)
        elif trade_count == 100:
            await self._award_achievement(user_id, "hundred_trades", "Experienced Trader", "gold", 500)
        elif trade_count == 1000:
            await self._award_achievement(user_id, "thousand_trades", "Trading Master", "diamond", 2000)
        
        # Large trade achievement
        trade_size_usd = float(trade_event.amount * trade_event.entry_price)
        if trade_size_usd >= 10000:
            await self._award_achievement(user_id, "whale_trade", "High Roller", "gold", 1000)
    
    async def _award_achievement(self, user_id: int, achievement_id: str, name: str, tier: str, xp_reward: int) -> None:
        """Award achievement and emit event"""
        achievement_event_data = {
            "metadata": EventMetadata(
                event_id=f"achievement_{achievement_id}_{user_id}",
                event_type="achievement_unlocked",
                domain=DomainType.GAMIFICATION,
                occurred_at=datetime.now(timezone.utc)
            ),
            "user_id": user_id,
            "achievement_id": achievement_id,
            "achievement_name": name,
            "achievement_tier": tier,
            "xp_reward": xp_reward,
            "badge_rarity": tier
        }
        
        await self.event_bus.emit(AchievementUnlockedEvent(**achievement_event_data))
        logger.info(f"Awarded achievement '{name}' to user {user_id}")
    
    async def _update_profitable_streak(self, user_id: int) -> None:
        """Update profitable trading streak"""
        # This would typically check recent trade history from a repository
        # For now, just emit a streak update event
        streak_event_data = {
            "metadata": EventMetadata(
                event_id=f"streak_update_{user_id}_{int(datetime.now().timestamp())}",
                event_type="streak_updated",
                domain=DomainType.GAMIFICATION,
                occurred_at=datetime.now(timezone.utc)
            ),
            "user_id": user_id,
            "streak_type": "profitable_trading",
            "current_streak": 1,  # Would be calculated from actual data
            "best_streak": 1,
            "streak_action": "continued"
        }
        
        # Note: In a real implementation, this would be handled by the streak service


class SocialToGamificationHandler(EventHandler):
    """
    Handles social events to update gamification metrics.
    
    Business Rules:
    - Social rating increases award XP bonuses
    - Constellation activities award community XP
    - Viral content sharing awards influence XP
    - Social endorsements improve streak multipliers
    """
    
    def __init__(self, event_bus, gamification_service):
        self.event_bus = event_bus
        self.gamification_service = gamification_service
    
    async def handle(self, event: Dict[str, Any]) -> None:
        """Handle social events for gamification integration"""
        try:
            event_type = event.get("metadata", {}).get("event_type")
            
            if event_type == "social_rating_changed":
                await self._handle_rating_change(SocialRatingChangedEvent(**event))
            elif event_type == "viral_content_shared":
                await self._handle_viral_content(event)
            elif event_type == "social_interaction_performed":
                await self._handle_social_interaction(event)
                
        except Exception as e:
            logger.error(f"Failed to handle social event: {e}")
    
    async def _handle_rating_change(self, rating_event: SocialRatingChangedEvent) -> None:
        """Handle social rating changes"""
        user_id = rating_event.user_id
        rating_increase = rating_event.change_amount
        
        # Award XP for significant rating increases
        if rating_increase >= 10:
            xp_amount = int(rating_increase * 2)  # 2 XP per rating point
            
            xp_event_data = {
                "metadata": EventMetadata(
                    event_id=f"social_xp_{user_id}_{int(datetime.now().timestamp())}",
                    event_type="xp_awarded",
                    domain=DomainType.GAMIFICATION,
                    occurred_at=datetime.now(timezone.utc)
                ),
                "user_id": user_id,
                "xp_amount": xp_amount,
                "xp_source": "social_rating",
                "source_id": f"rating_change_{rating_event.metadata.event_id}",
                "multiplier": Decimal("1.0")
            }
            
            await self.event_bus.emit(XPAwardedEvent(**xp_event_data))
            logger.info(f"Awarded {xp_amount} social XP to user {user_id}")
        
        # Check for social achievements
        if rating_event.new_rating >= 100:
            await self._award_social_achievement(user_id, "social_influencer", "Social Influencer", "gold", 500)
    
    async def _handle_viral_content(self, event: Dict[str, Any]) -> None:
        """Handle viral content sharing"""
        user_id = event.get("user_id")
        viral_score = event.get("viral_score", 0)
        
        # Award XP based on viral score
        xp_amount = min(viral_score * 5, 200)  # Max 200 XP per viral content
        
        if xp_amount > 0:
            xp_event_data = {
                "metadata": EventMetadata(
                    event_id=f"viral_xp_{user_id}_{int(datetime.now().timestamp())}",
                    event_type="xp_awarded",
                    domain=DomainType.GAMIFICATION,
                    occurred_at=datetime.now(timezone.utc)
                ),
                "user_id": user_id,
                "xp_amount": xp_amount,
                "xp_source": "viral_content",
                "source_id": str(event.get("content_id")),
                "multiplier": Decimal("1.0")
            }
            
            await self.event_bus.emit(XPAwardedEvent(**xp_event_data))
    
    async def _handle_social_interaction(self, event: Dict[str, Any]) -> None:
        """Handle social interactions"""
        source_user_id = event.get("source_user_id")
        interaction_type = event.get("interaction_type")
        impact_value = event.get("impact_value", 0)
        
        # Award XP for positive social interactions
        if impact_value > 0 and interaction_type in ["endorsement", "helpful_comment"]:
            xp_amount = int(impact_value * 10)
            
            xp_event_data = {
                "metadata": EventMetadata(
                    event_id=f"interaction_xp_{source_user_id}_{int(datetime.now().timestamp())}",
                    event_type="xp_awarded",
                    domain=DomainType.GAMIFICATION,
                    occurred_at=datetime.now(timezone.utc)
                ),
                "user_id": source_user_id,
                "xp_amount": xp_amount,
                "xp_source": "social_interaction",
                "source_id": f"{interaction_type}_{event.get('target_user_id')}",
                "multiplier": Decimal("1.0")
            }
            
            await self.event_bus.emit(XPAwardedEvent(**xp_event_data))
    
    async def _award_social_achievement(self, user_id: int, achievement_id: str, name: str, tier: str, xp_reward: int) -> None:
        """Award social achievement"""
        achievement_event_data = {
            "metadata": EventMetadata(
                event_id=f"social_achievement_{achievement_id}_{user_id}",
                event_type="achievement_unlocked",
                domain=DomainType.GAMIFICATION,
                occurred_at=datetime.now(timezone.utc)
            ),
            "user_id": user_id,
            "achievement_id": achievement_id,
            "achievement_name": name,
            "achievement_tier": tier,
            "xp_reward": xp_reward,
            "badge_rarity": tier
        }
        
        await self.event_bus.emit(AchievementUnlockedEvent(**achievement_event_data))


class GamificationToSocialHandler(EventHandler):
    """
    Handles gamification events to trigger social activities.
    
    Business Rules:
    - Achievement unlocks can trigger viral content creation
    - Level ups improve social rating multipliers
    - Leaderboard changes trigger constellation notifications
    """
    
    def __init__(self, event_bus, social_service):
        self.event_bus = event_bus
        self.social_service = social_service
    
    async def handle(self, event: Dict[str, Any]) -> None:
        """Handle gamification events for social integration"""
        try:
            event_type = event.get("metadata", {}).get("event_type")
            
            if event_type == "level_up":
                await self._handle_level_up(LevelUpEvent(**event))
            elif event_type == "achievement_unlocked":
                await self._handle_achievement_unlock(AchievementUnlockedEvent(**event))
                
        except Exception as e:
            logger.error(f"Failed to handle gamification event: {e}")
    
    async def _handle_level_up(self, level_event: LevelUpEvent) -> None:
        """Handle level up events"""
        user_id = level_event.user_id
        new_level = level_event.new_level
        
        # Significant level ups can boost social rating
        if new_level % 10 == 0:  # Every 10 levels
            rating_boost = new_level * 0.5  # 0.5 points per level
            
            # This would typically call the social service to update rating
            logger.info(f"User {user_id} leveled up to {new_level}, boosting social rating by {rating_boost}")
    
    async def _handle_achievement_unlock(self, achievement_event: AchievementUnlockedEvent) -> None:
        """Handle achievement unlocks"""
        user_id = achievement_event.user_id
        achievement_name = achievement_event.achievement_name
        tier = achievement_event.achievement_tier
        
        # High-tier achievements can trigger viral content
        if tier in ["gold", "diamond"]:
            viral_event_data = {
                "metadata": EventMetadata(
                    event_id=f"viral_achievement_{achievement_event.metadata.event_id}",
                    event_type="viral_content_shared",
                    domain=DomainType.SOCIAL,
                    occurred_at=datetime.now(timezone.utc),
                    correlation_id=achievement_event.metadata.event_id
                ),
                "content_id": int(datetime.now().timestamp()),  # Simple ID generation
                "user_id": user_id,
                "platform": "constellation",
                "viral_score": 10 if tier == "gold" else 25,
                "content_type": "achievement_share"
            }
            
            await self.event_bus.emit(ViralContentSharedEvent(**viral_event_data))
            logger.info(f"Generated viral content for achievement unlock: {achievement_name}")


class FinancialIntegrationHandler(EventHandler):
    """
    Handles financial events for cross-domain integration.
    
    Business Rules:
    - Account creation triggers user onboarding rewards
    - Large deposits award VIP status and bonuses
    - Payment successes can unlock premium features
    """
    
    def __init__(self, event_bus, user_service, gamification_service):
        self.event_bus = event_bus
        self.user_service = user_service
        self.gamification_service = gamification_service
    
    async def handle(self, event: Dict[str, Any]) -> None:
        """Handle financial events for integration"""
        try:
            event_type = event.get("metadata", {}).get("event_type")
            
            if event_type == "account_created":
                await self._handle_account_creation(event)
            elif event_type == "funds_added":
                await self._handle_funds_added(event)
            elif event_type == "payment_processed":
                await self._handle_payment_processed(event)
                
        except Exception as e:
            logger.error(f"Failed to handle financial event: {e}")
    
    async def _handle_account_creation(self, event: Dict[str, Any]) -> None:
        """Handle new account creation"""
        user_id = event.get("user_id")
        
        # Award welcome bonus XP
        xp_event_data = {
            "metadata": EventMetadata(
                event_id=f"welcome_bonus_{user_id}",
                event_type="xp_awarded",
                domain=DomainType.GAMIFICATION,
                occurred_at=datetime.now(timezone.utc)
            ),
            "user_id": user_id,
            "xp_amount": 100,
            "xp_source": "account_creation",
            "source_id": event.get("account_id"),
            "multiplier": Decimal("1.0")
        }
        
        await self.event_bus.emit(XPAwardedEvent(**xp_event_data))
        logger.info(f"Awarded welcome bonus to user {user_id}")
    
    async def _handle_funds_added(self, event: Dict[str, Any]) -> None:
        """Handle funds being added to account"""
        user_id = event.get("user_id")
        amount = Decimal(str(event.get("amount", 0)))
        
        # Large deposits get bonus XP
        if amount >= 1000:
            xp_amount = min(int(amount / 10), 500)  # 1 XP per $10, max 500
            
            xp_event_data = {
                "metadata": EventMetadata(
                    event_id=f"deposit_bonus_{event.get('transaction_id')}",
                    event_type="xp_awarded",
                    domain=DomainType.GAMIFICATION,
                    occurred_at=datetime.now(timezone.utc)
                ),
                "user_id": user_id,
                "xp_amount": xp_amount,
                "xp_source": "large_deposit",
                "source_id": event.get("transaction_id"),
                "multiplier": Decimal("1.0")
            }
            
            await self.event_bus.emit(XPAwardedEvent(**xp_event_data))
    
    async def _handle_payment_processed(self, event: Dict[str, Any]) -> None:
        """Handle payment processing"""
        user_id = event.get("user_id")
        status = event.get("status")
        subscription_tier = event.get("subscription_tier")
        
        # Successful premium subscriptions unlock features
        if status == "success" and subscription_tier in ["premium", "vip"]:
            # This would typically update user permissions and features
            logger.info(f"User {user_id} upgraded to {subscription_tier} subscription")