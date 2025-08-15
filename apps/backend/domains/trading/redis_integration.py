"""
Trading Domain Redis Streams Integration

Demonstrates integration of Trading domain events with Redis Streams event bus.
Shows cross-domain event publishing for real-time gamification updates.
"""

import asyncio
import sys
import os
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, Any

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'shared'))

try:
    from redis_streams import RedisStreamsEventBus, create_redis_event
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("Redis integration not available")


class TradingEventPublisher:
    """
    Trading domain event publisher for Redis Streams.
    
    Publishes trading events that trigger cross-domain reactions:
    - Trading -> Gamification (XP calculation)
    - Trading -> Social (leaderboard updates)
    - Trading -> Financial (revenue tracking)
    """
    
    def __init__(self, event_bus: RedisStreamsEventBus):
        self.event_bus = event_bus
    
    async def publish_trade_executed(self, trade_data: Dict[str, Any], 
                                   correlation_id: str = None) -> str:
        """
        Publish TradeExecuted event to Redis Streams.
        
        This event triggers:
        - Gamification XP calculation
        - Social leaderboard updates
        - Financial revenue tracking
        """
        event = create_redis_event(
            event_type="Trading.TradeExecuted",
            domain="trading",
            entity_id=f"trade_{trade_data['trade_id']}",
            data={
                "trade_id": trade_data["trade_id"],
                "user_id": trade_data["user_id"],
                "asset_symbol": trade_data["asset_symbol"],
                "direction": trade_data["direction"],
                "amount": str(trade_data["amount"]),
                "entry_price": str(trade_data["entry_price"]),
                "executed_at": trade_data["executed_at"],
                "pnl_usd": str(trade_data.get("pnl_usd", "0.00"))
            },
            correlation_id=correlation_id
        )
        
        message_id = await self.event_bus.emit(event)
        print(f"📈 Published Trading.TradeExecuted -> {message_id}")
        return message_id
    
    async def publish_trading_rewards_calculated(self, rewards_data: Dict[str, Any],
                                               correlation_id: str = None) -> str:
        """
        Publish TradingRewardsCalculated event for gamification integration.
        
        This event contains XP and achievement data for the gamification domain.
        """
        event = create_redis_event(
            event_type="Trading.TradingRewardsCalculated", 
            domain="trading",
            entity_id=f"user_{rewards_data['user_id']}",
            data={
                "user_id": rewards_data["user_id"],
                "trade_id": rewards_data["trade_id"],
                "xp_gained": rewards_data["xp_gained"],
                "achievements_unlocked": rewards_data.get("achievements_unlocked", []),
                "bonus_items": rewards_data.get("bonus_items", []),
                "activity_type": "trading"
            },
            correlation_id=correlation_id,
            causation_id=correlation_id  # This event is caused by the trade
        )
        
        message_id = await self.event_bus.emit(event)
        print(f"🎯 Published Trading.TradingRewardsCalculated -> {message_id}")
        return message_id
    
    async def publish_clan_battle_score_updated(self, battle_data: Dict[str, Any],
                                              correlation_id: str = None) -> str:
        """
        Publish ClanBattleScoreUpdated event for social domain integration.
        
        Updates clan leaderboards and social rankings.
        """
        event = create_redis_event(
            event_type="Trading.ClanBattleScoreUpdated",
            domain="trading", 
            entity_id=f"battle_{battle_data['battle_id']}",
            data={
                "battle_id": battle_data["battle_id"],
                "user_id": battle_data["user_id"],
                "trading_score": str(battle_data["trading_score"]),
                "trade_count": battle_data["trade_count"],
                "pnl_usd": str(battle_data["pnl_usd"])
            },
            correlation_id=correlation_id
        )
        
        message_id = await self.event_bus.emit(event)
        print(f"⚔️ Published Trading.ClanBattleScoreUpdated -> {message_id}")
        return message_id


class GamificationEventConsumer:
    """
    Gamification domain consumer for trading events.
    
    Demonstrates cross-domain event consumption and XP calculation.
    """
    
    def __init__(self, event_bus: RedisStreamsEventBus):
        self.event_bus = event_bus
    
    async def handle_trading_event(self, event_data: Dict[str, Any]):
        """
        Handle trading events and calculate gamification rewards.
        
        This simulates the gamification domain receiving trading events
        and calculating XP, achievements, and progression updates.
        """
        event_type = event_data.get('event_type', '')
        correlation_id = event_data.get('correlation_id', '')
        
        print(f"🎮 Gamification received: {event_type}")
        print(f"   Correlation ID: {correlation_id}")
        
        if event_type == "Trading.TradeExecuted":
            await self._calculate_trading_xp(event_data, correlation_id)
        
        elif event_type == "Trading.TradingRewardsCalculated":
            await self._update_user_progression(event_data, correlation_id)
    
    async def _calculate_trading_xp(self, trade_event: Dict[str, Any], 
                                  correlation_id: str):
        """Calculate XP from trading activity."""
        data = trade_event.get('data', {})
        if isinstance(data, str):
            import json
            try:
                data = json.loads(data)
            except:
                data = {}
        
        user_id = data.get('user_id', 0)
        amount = float(data.get('amount', 0))
        
        # Simple XP calculation: 1 XP per $10 traded
        xp_gained = max(1, int(amount / 10))
        
        # Create XP gained event
        xp_event = create_redis_event(
            event_type="Gamification.XPGained",
            domain="gamification",
            entity_id=f"user_{user_id}",
            data={
                "user_id": user_id,
                "activity_type": "trading",
                "xp_amount": xp_gained,
                "total_xp": 0  # Would calculate from database
            },
            correlation_id=correlation_id,
            causation_id=trade_event.get('event_id')
        )
        
        await self.event_bus.emit(xp_event)
        print(f"   ✨ Generated {xp_gained} XP for user {user_id}")
    
    async def _update_user_progression(self, rewards_event: Dict[str, Any],
                                     correlation_id: str):
        """Update user progression from calculated rewards."""
        data = rewards_event.get('data', {})
        if isinstance(data, str):
            import json
            try:
                data = json.loads(data)
            except:
                data = {}
        
        user_id = data.get('user_id', 0)
        achievements = data.get('achievements_unlocked', [])
        
        # Simulate level up check
        if len(achievements) > 0:
            level_up_event = create_redis_event(
                event_type="Gamification.LevelUp",
                domain="gamification",
                entity_id=f"user_{user_id}",
                data={
                    "user_id": user_id,
                    "old_level": 5,
                    "new_level": 6,
                    "rewards_unlocked": achievements
                },
                correlation_id=correlation_id,
                causation_id=rewards_event.get('event_id')
            )
            
            await self.event_bus.emit(level_up_event)
            print(f"   🆙 User {user_id} leveled up!")
    
    async def start_consuming(self):
        """Start consuming trading events."""
        await self.event_bus.subscribe_to_domain(
            "trading", 
            "gamification_consumers",
            self.handle_trading_event
        )


async def demonstrate_cross_domain_events():
    """
    Demonstrate cross-domain event flow:
    Trading -> Gamification -> Social -> Financial
    """
    if not REDIS_AVAILABLE:
        print("❌ Redis not available for demonstration")
        return
    
    print("🚀 Starting Cross-Domain Event Flow Demonstration")
    print("=" * 60)
    
    # Create event bus
    event_bus = RedisStreamsEventBus()
    
    try:
        # Create publishers and consumers
        trading_publisher = TradingEventPublisher(event_bus)
        gamification_consumer = GamificationEventConsumer(event_bus)
        
        # Start gamification consumer
        await gamification_consumer.start_consuming()
        print("✅ Gamification consumer started")
        
        # Wait for consumer setup
        await asyncio.sleep(1)
        
        # Simulate a trading sequence
        correlation_id = f"trade_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        print(f"\n📊 Simulating Trading Sequence (Correlation: {correlation_id})")
        print("-" * 40)
        
        # 1. Execute trade
        trade_data = {
            "trade_id": "trade_12345",
            "user_id": 123,
            "asset_symbol": "STRK",
            "direction": "LONG",
            "amount": Decimal("1000.50"),
            "entry_price": Decimal("2.45"),
            "executed_at": datetime.now(timezone.utc).isoformat(),
            "pnl_usd": Decimal("45.75")
        }
        
        await trading_publisher.publish_trade_executed(trade_data, correlation_id)
        
        # 2. Calculate and publish rewards
        rewards_data = {
            "user_id": 123,
            "trade_id": "trade_12345",
            "xp_gained": 100,
            "achievements_unlocked": ["first_profitable_trade", "strk_trader"],
            "bonus_items": [{"type": "nft_reward", "id": "genesis_trader"}]
        }
        
        await trading_publisher.publish_trading_rewards_calculated(rewards_data, correlation_id)
        
        # 3. Update clan battle scores
        battle_data = {
            "battle_id": 456,
            "user_id": 123,
            "trading_score": Decimal("875.25"),
            "trade_count": 15,
            "pnl_usd": Decimal("145.75")
        }
        
        await trading_publisher.publish_clan_battle_score_updated(battle_data, correlation_id)
        
        print(f"\n⏳ Processing events...")
        await asyncio.sleep(3)
        
        print(f"\n🎉 Cross-domain event flow completed!")
        print(f"   Correlation ID: {correlation_id}")
        print(f"   Events published: 3 trading events")
        print(f"   Cross-domain reactions: Gamification XP + Level up")
        
    except Exception as e:
        print(f"❌ Error in demonstration: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await event_bus.close()
        print("\n✅ Event bus closed")


async def test_redis_integration():
    """Test basic Redis integration functionality."""
    if not REDIS_AVAILABLE:
        print("❌ Redis library not available")
        print("   Install with: pip install redis")
        return
    
    print("🧪 Testing Redis Integration")
    
    event_bus = RedisStreamsEventBus()
    
    # Test simple event emission
    test_event = create_redis_event(
        event_type="Testing.SimpleEvent",
        domain="testing",
        entity_id="test_001",
        data={"message": "Hello from Trading domain!"}
    )
    
    try:
        message_id = await event_bus.emit(test_event)
        print(f"✅ Event emitted successfully: {message_id}")
        
        # Test event consumption
        received_events = []
        
        async def test_handler(event_data):
            received_events.append(event_data)
            print(f"📨 Received: {event_data['event_type']}")
        
        await event_bus.subscribe("astra.testing.*", "test_group", test_handler)
        await asyncio.sleep(2)  # Wait for processing
        
        if received_events:
            print(f"✅ Event consumption successful: {len(received_events)} events")
        else:
            print("⚠️  Event consumption test inconclusive")
        
    except Exception as e:
        print(f"❌ Redis integration test failed: {e}")
    
    finally:
        await event_bus.close()


if __name__ == "__main__":
    print("🔧 AstraTrade Trading Domain - Redis Streams Integration")
    print("=" * 60)
    
    # Run integration tests
    asyncio.run(test_redis_integration())
    
    print("\n" + "=" * 60)
    
    # Run cross-domain demonstration
    asyncio.run(demonstrate_cross_domain_events())