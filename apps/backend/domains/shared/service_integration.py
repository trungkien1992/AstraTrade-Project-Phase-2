"""
Domain Service Integration with Enhanced Event Bus

Example integration of existing domain services with the enhanced event system.
Shows how to add Redis Streams event publishing to existing service methods.
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod

# Example integration for existing domain services
class EventPublishingMixin:
    """
    Mixin to add event publishing capabilities to existing domain services.
    
    Can be added to existing service classes with minimal changes.
    """
    
    def __init__(self, *args, event_bus=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._event_bus = event_bus
        self._correlation_context = {}  # Track correlation IDs for requests
    
    async def _publish_event(self, event_dict: Dict[str, Any], 
                           correlation_id: Optional[str] = None) -> None:
        """Publish event to Redis Streams if event bus is available."""
        if self._event_bus:
            if correlation_id:
                await self._event_bus.emit_with_correlation(event_dict, correlation_id)
            else:
                await self._event_bus.emit(event_dict)
    
    def set_correlation_context(self, correlation_id: str, user_id: int = None):
        """Set correlation context for current request."""
        self._correlation_context = {
            'correlation_id': correlation_id,
            'user_id': user_id
        }
    
    def get_correlation_id(self) -> Optional[str]:
        """Get current correlation ID."""
        return self._correlation_context.get('correlation_id')


# Example: Enhanced Trading Service
class EnhancedTradingService(EventPublishingMixin):
    """
    Enhanced trading service with Redis Streams event publishing.
    
    Shows how to integrate existing trading service with event bus.
    """
    
    def __init__(self, event_bus=None):
        super().__init__(event_bus=event_bus)
    
    async def execute_trade(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute trade with event publishing.
        
        Original method logic preserved, events added.
        """
        # Original trading logic (preserved)
        trade_result = self._process_trade_execution(trade_data)
        
        # NEW: Publish TradeExecuted event
        from redis_streams import create_redis_event
        
        trade_event = create_redis_event(
            event_type="Trading.TradeExecuted",
            domain="trading",
            entity_id=f"trade_{trade_result['trade_id']}",
            data={
                "trade_id": trade_result["trade_id"],
                "user_id": trade_data["user_id"],
                "asset_symbol": trade_data["asset_symbol"],
                "direction": trade_data["direction"],
                "amount": str(trade_data["amount"]),
                "entry_price": str(trade_data["entry_price"]),
                "pnl_usd": str(trade_result.get("pnl_usd", "0.00"))
            },
            correlation_id=self.get_correlation_id()
        )
        
        await self._publish_event(trade_event)
        
        # Calculate and publish rewards
        rewards = self._calculate_trading_rewards(trade_result)
        if rewards:
            rewards_event = create_redis_event(
                event_type="Trading.TradingRewardsCalculated",
                domain="trading", 
                entity_id=f"user_{trade_data['user_id']}",
                data=rewards,
                correlation_id=self.get_correlation_id()
            )
            await self._publish_event(rewards_event)
        
        return trade_result
    
    def _process_trade_execution(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Original trade execution logic (unchanged)."""
        # Simulate trade execution
        return {
            "trade_id": f"trade_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "status": "executed",
            "executed_at": datetime.now(timezone.utc).isoformat(),
            "pnl_usd": 45.75,
            **trade_data
        }
    
    def _calculate_trading_rewards(self, trade_result: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate XP and achievements for trade."""
        return {
            "user_id": trade_result["user_id"],
            "trade_id": trade_result["trade_id"],
            "xp_gained": 100,
            "achievements_unlocked": ["profitable_trade"],
            "activity_type": "trading"
        }


# Example: Enhanced Gamification Service  
class EnhancedGamificationService(EventPublishingMixin):
    """
    Enhanced gamification service that consumes trading events
    and publishes gamification events.
    """
    
    def __init__(self, event_bus=None):
        super().__init__(event_bus=event_bus)
    
    async def handle_trading_rewards(self, rewards_data: Dict[str, Any]):
        """
        Handle trading rewards and update user progression.
        
        This method would be called by the gamification consumer.
        """
        user_id = rewards_data.get("user_id")
        xp_gained = rewards_data.get("xp_gained", 0)
        
        # Original gamification logic (preserved)
        user_progression = self._update_user_xp(user_id, xp_gained)
        
        # NEW: Publish XP gained event
        from redis_streams import create_redis_event
        
        xp_event = create_redis_event(
            event_type="Gamification.XPGained",
            domain="gamification",
            entity_id=f"user_{user_id}",
            data={
                "user_id": user_id,
                "activity_type": rewards_data.get("activity_type", "trading"),
                "xp_amount": xp_gained,
                "total_xp": user_progression["total_xp"]
            },
            correlation_id=rewards_data.get("correlation_id")
        )
        
        await self._publish_event(xp_event)
        
        # Check for level up
        if user_progression.get("level_up"):
            level_event = create_redis_event(
                event_type="Gamification.LevelUp",
                domain="gamification",
                entity_id=f"user_{user_id}",
                data={
                    "user_id": user_id,
                    "old_level": user_progression["old_level"],
                    "new_level": user_progression["new_level"],
                    "rewards_unlocked": user_progression.get("rewards", [])
                },
                correlation_id=rewards_data.get("correlation_id")
            )
            
            await self._publish_event(level_event)
    
    def _update_user_xp(self, user_id: int, xp_amount: int) -> Dict[str, Any]:
        """Original XP update logic (unchanged)."""
        # Simulate XP update and level check
        current_xp = 1250  # Would fetch from database
        new_xp = current_xp + xp_amount
        
        old_level = self._get_level_from_xp(current_xp)
        new_level = self._get_level_from_xp(new_xp)
        
        return {
            "total_xp": new_xp,
            "level_up": new_level > old_level,
            "old_level": old_level,
            "new_level": new_level,
            "rewards": ["level_badge", "bonus_xp"] if new_level > old_level else []
        }
    
    def _get_level_from_xp(self, xp: int) -> int:
        """Calculate level from XP amount."""
        return min(100, max(1, int(xp / 1000) + 1))


# Service Factory for Event Bus Integration
class EventBusServiceFactory:
    """
    Factory for creating domain services with event bus integration.
    
    Enables gradual migration of existing services to event-driven architecture.
    """
    
    def __init__(self, event_bus=None):
        self.event_bus = event_bus
    
    def create_trading_service(self) -> EnhancedTradingService:
        """Create trading service with event publishing."""
        return EnhancedTradingService(event_bus=self.event_bus)
    
    def create_gamification_service(self) -> EnhancedGamificationService:
        """Create gamification service with event publishing.""" 
        return EnhancedGamificationService(event_bus=self.event_bus)
    
    # Add more service factories as needed
    # def create_social_service(self) -> EnhancedSocialService:
    # def create_financial_service(self) -> EnhancedFinancialService:
    # def create_nft_service(self) -> EnhancedNFTService:
    # def create_user_service(self) -> EnhancedUserService:


# Integration Example
async def demonstrate_service_integration():
    """
    Demonstrate how existing services integrate with event bus.
    """
    print("🔧 Service Integration Demonstration")
    print("=" * 50)
    
    # Import event bus (would be dependency injected in production)
    try:
        from redis_streams import RedisStreamsEventBus
        event_bus = RedisStreamsEventBus()
    except ImportError:
        print("📝 Simulating event bus (Redis not available)")
        event_bus = None
    
    # Create enhanced services
    factory = EventBusServiceFactory(event_bus)
    trading_service = factory.create_trading_service()
    gamification_service = factory.create_gamification_service()
    
    # Set correlation context (would come from API request)
    correlation_id = f"api_request_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    trading_service.set_correlation_context(correlation_id, user_id=123)
    
    print(f"📊 Executing trade with correlation: {correlation_id}")
    
    # Execute trade (publishes events if event bus available)
    trade_data = {
        "user_id": 123,
        "asset_symbol": "STRK",
        "direction": "LONG",
        "amount": 1000.50,
        "entry_price": 2.45
    }
    
    try:
        trade_result = await trading_service.execute_trade(trade_data)
        print(f"✅ Trade executed: {trade_result['trade_id']}")
        
        if event_bus:
            print("📡 Events published to Redis Streams")
            print("   • Trading.TradeExecuted")
            print("   • Trading.TradingRewardsCalculated")
        else:
            print("📝 Events would be published (Redis not available)")
        
        # Simulate gamification service consuming the rewards event
        rewards_data = {
            "user_id": 123,
            "trade_id": trade_result["trade_id"],
            "xp_gained": 100,
            "activity_type": "trading",
            "correlation_id": correlation_id
        }
        
        print(f"\n🎮 Processing gamification rewards...")
        await gamification_service.handle_trading_rewards(rewards_data)
        
        if event_bus:
            print("📡 Gamification events published:")
            print("   • Gamification.XPGained")
            print("   • Gamification.LevelUp (if applicable)")
        
        print(f"\n✅ Service integration demonstration complete")
        print(f"   Correlation: {correlation_id}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        if event_bus:
            await event_bus.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(demonstrate_service_integration())