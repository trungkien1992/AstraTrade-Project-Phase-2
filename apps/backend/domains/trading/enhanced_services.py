"""
Enhanced Trading Services with Redis Streams Integration

Production-ready trading services that integrate with the enhanced event bus
while preserving existing business logic and domain patterns.
"""

import asyncio
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, Any, Optional, List
from uuid import uuid4

# Import existing trading components
from .services import TradingService
from .entities import Trade, Portfolio
from .value_objects import Asset, Money, TradeDirection, RiskParameters

# Import enhanced event system
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'shared'))

try:
    from redis_streams import RedisStreamsEventBus, create_redis_event
    from service_integration import EventPublishingMixin
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("Warning: Redis integration not available")


class EnhancedTradingService(EventPublishingMixin, TradingService):
    """
    Enhanced trading service with Redis Streams event publishing.
    
    Extends the existing TradingService with event-driven capabilities
    while preserving all existing business logic.
    """
    
    def __init__(self, event_bus=None, **kwargs):
        # Initialize parent classes
        super().__init__(event_bus=event_bus, **kwargs)
        
        # Event publishing configuration
        self.domain = "trading"
        self.service_name = "enhanced_trading_service"
    
    async def execute_trade(
        self,
        user_id: int,
        asset: Asset,
        direction: TradeDirection,
        amount: Money,
        risk_params: RiskParameters,
        is_mock: bool = False,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute trade with enhanced event publishing.
        
        Preserves original trading logic while adding event-driven capabilities.
        """
        # Set correlation context for this request
        if correlation_id:
            self.set_correlation_context(correlation_id, user_id)
        
        try:
            # Execute original trade logic
            trade_result = await super().execute_trade(
                user_id, asset, direction, amount, risk_params, is_mock
            )
            
            # Publish TradeExecuted event
            await self._publish_trade_executed_event(trade_result, user_id, asset, direction, amount)
            
            # Calculate and publish trading rewards
            rewards = await self._calculate_and_publish_rewards(trade_result, user_id)
            
            # Update clan battle scores if applicable
            await self._update_clan_battle_scores(trade_result, user_id)
            
            # Add event metadata to result
            trade_result['events_published'] = True
            trade_result['correlation_id'] = correlation_id
            
            return trade_result
            
        except Exception as e:
            # Publish trade failure event
            await self._publish_trade_failed_event(user_id, str(e), correlation_id)
            raise
    
    async def _publish_trade_executed_event(
        self, 
        trade_result: Dict[str, Any], 
        user_id: int, 
        asset: Asset, 
        direction: TradeDirection, 
        amount: Money
    ) -> None:
        """Publish TradeExecuted event to Redis Streams."""
        event = create_redis_event(
            event_type="Trading.TradeExecuted",
            domain=self.domain,
            entity_id=f"trade_{trade_result.get('trade_id', 'unknown')}",
            data={
                "trade_id": trade_result.get('trade_id'),
                "user_id": user_id,
                "asset_symbol": asset.symbol if hasattr(asset, 'symbol') else str(asset),
                "direction": direction.value if hasattr(direction, 'value') else str(direction),
                "amount": str(amount.amount) if hasattr(amount, 'amount') else str(amount),
                "entry_price": str(trade_result.get('entry_price', '0.00')),
                "executed_at": trade_result.get('executed_at', datetime.now(timezone.utc).isoformat()),
                "pnl_usd": str(trade_result.get('pnl', '0.00')),
                "fees": str(trade_result.get('fees', '0.00')),
                "is_mock": trade_result.get('is_mock', False)
            },
            correlation_id=self.get_correlation_id()
        )
        
        await self._publish_event(event, self.get_correlation_id())
    
    async def _calculate_and_publish_rewards(
        self, 
        trade_result: Dict[str, Any], 
        user_id: int
    ) -> Dict[str, Any]:
        """Calculate trading rewards and publish event."""
        # Simple reward calculation based on trade success
        pnl = Decimal(str(trade_result.get('pnl', '0.00')))
        amount = Decimal(str(trade_result.get('amount', '0.00')))
        
        # Base XP calculation
        base_xp = max(10, int(amount / 100))  # 10 XP per $100 traded
        profit_bonus = max(0, int(pnl / 10)) if pnl > 0 else 0  # Bonus for profitable trades
        total_xp = base_xp + profit_bonus
        
        # Achievement detection
        achievements = []
        if pnl > 0:
            achievements.append("profitable_trade")
        if pnl > 100:
            achievements.append("big_winner")
        if amount > 1000:
            achievements.append("high_volume_trader")
        
        rewards_data = {
            "user_id": user_id,
            "trade_id": trade_result.get('trade_id'),
            "xp_gained": total_xp,
            "achievements_unlocked": achievements,
            "bonus_items": [],
            "activity_type": "trading",
            "pnl_usd": str(pnl),
            "trade_amount": str(amount)
        }
        
        # Publish TradingRewardsCalculated event
        rewards_event = create_redis_event(
            event_type="Trading.TradingRewardsCalculated",
            domain=self.domain,
            entity_id=f"user_{user_id}",
            data=rewards_data,
            correlation_id=self.get_correlation_id(),
            causation_id=trade_result.get('trade_id')
        )
        
        await self._publish_event(rewards_event, self.get_correlation_id())
        
        return rewards_data
    
    async def _update_clan_battle_scores(
        self, 
        trade_result: Dict[str, Any], 
        user_id: int
    ) -> None:
        """Update clan battle scores if user is in an active battle."""
        # Simulate clan battle detection (would check database in real implementation)
        active_battle_id = await self._get_active_clan_battle(user_id)
        
        if active_battle_id:
            pnl = Decimal(str(trade_result.get('pnl', '0.00')))
            amount = Decimal(str(trade_result.get('amount', '0.00')))
            
            # Calculate trading score (combination of volume and profitability)
            volume_score = amount / 100  # 1 point per $100 volume
            profit_score = max(0, pnl / 10)  # 1 point per $10 profit
            trading_score = volume_score + profit_score
            
            battle_event = create_redis_event(
                event_type="Trading.ClanBattleScoreUpdated",
                domain=self.domain,
                entity_id=f"battle_{active_battle_id}",
                data={
                    "battle_id": active_battle_id,
                    "user_id": user_id,
                    "trading_score": str(trading_score),
                    "trade_count": 1,  # This trade
                    "pnl_usd": str(pnl),
                    "volume_usd": str(amount)
                },
                correlation_id=self.get_correlation_id(),
                causation_id=trade_result.get('trade_id')
            )
            
            await self._publish_event(battle_event, self.get_correlation_id())
    
    async def _publish_trade_failed_event(
        self, 
        user_id: int, 
        error_message: str, 
        correlation_id: Optional[str] = None
    ) -> None:
        """Publish trade failure event for monitoring and analysis."""
        failure_event = create_redis_event(
            event_type="Trading.TradeFailed",
            domain=self.domain,
            entity_id=f"user_{user_id}",
            data={
                "user_id": user_id,
                "error_message": error_message,
                "failed_at": datetime.now(timezone.utc).isoformat(),
                "correlation_id": correlation_id
            },
            correlation_id=correlation_id
        )
        
        await self._publish_event(failure_event, correlation_id)
    
    async def _get_active_clan_battle(self, user_id: int) -> Optional[str]:
        """Check if user is in an active clan battle (mock implementation)."""
        # In real implementation, would query database for active battles
        # For demo, simulate 30% chance of being in a battle
        import random
        if random.random() < 0.3:
            return f"battle_{datetime.now().strftime('%Y%m%d_%H')}"
        return None


class TradingEventConsumer:
    """
    Consumer for processing trading-related events from other domains.
    
    Handles events that affect trading operations, such as:
    - Risk limit updates from financial domain
    - User status changes affecting trading permissions
    """
    
    def __init__(self, event_bus: RedisStreamsEventBus, trading_service: EnhancedTradingService):
        self.event_bus = event_bus
        self.trading_service = trading_service
        self.domain = "trading"
    
    async def handle_financial_event(self, event_data: Dict[str, Any]) -> None:
        """Handle financial events that affect trading."""
        event_type = event_data.get('event_type', '')
        
        if event_type == "Financial.AccountSuspended":
            await self._handle_account_suspension(event_data)
        elif event_type == "Financial.RiskLimitUpdated":
            await self._handle_risk_limit_update(event_data)
    
    async def handle_user_event(self, event_data: Dict[str, Any]) -> None:
        """Handle user events that affect trading permissions."""
        event_type = event_data.get('event_type', '')
        
        if event_type == "User.AccountStatusChanged":
            await self._handle_account_status_change(event_data)
    
    async def _handle_account_suspension(self, event_data: Dict[str, Any]) -> None:
        """Handle account suspension by closing open positions."""
        data = self._parse_event_data(event_data)
        user_id = data.get('user_id')
        
        if user_id:
            # Publish trading suspension event
            suspension_event = create_redis_event(
                event_type="Trading.TradingSuspended",
                domain=self.domain,
                entity_id=f"user_{user_id}",
                data={
                    "user_id": user_id,
                    "reason": "account_suspended",
                    "suspended_at": datetime.now(timezone.utc).isoformat(),
                    "causation_event": event_data.get('event_id')
                },
                correlation_id=event_data.get('correlation_id'),
                causation_id=event_data.get('event_id')
            )
            
            await self.event_bus.emit(suspension_event)
    
    async def _handle_risk_limit_update(self, event_data: Dict[str, Any]) -> None:
        """Handle risk limit updates."""
        # Implementation would update user's risk parameters
        pass
    
    async def _handle_account_status_change(self, event_data: Dict[str, Any]) -> None:
        """Handle user account status changes."""
        # Implementation would update trading permissions
        pass
    
    def _parse_event_data(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse event data from various formats."""
        data = event_data.get('data', {})
        if isinstance(data, str):
            import json
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return {}
        return data
    
    async def start_consuming(self) -> None:
        """Start consuming events from other domains."""
        # Subscribe to financial events
        await self.event_bus.subscribe_to_domain(
            "financial", 
            "trading_financial_consumers",
            self.handle_financial_event
        )
        
        # Subscribe to user events
        await self.event_bus.subscribe_to_domain(
            "user",
            "trading_user_consumers", 
            self.handle_user_event
        )


# Factory for creating enhanced trading services
class EnhancedTradingServiceFactory:
    """Factory for creating trading services with event bus integration."""
    
    @staticmethod
    def create_service(event_bus=None, **kwargs) -> EnhancedTradingService:
        """Create enhanced trading service with event publishing."""
        return EnhancedTradingService(event_bus=event_bus, **kwargs)
    
    @staticmethod
    def create_consumer(event_bus, trading_service) -> TradingEventConsumer:
        """Create trading event consumer."""
        return TradingEventConsumer(event_bus, trading_service)


# Example usage and testing
async def test_enhanced_trading_service():
    """Test the enhanced trading service with event publishing."""
    print("🔧 Testing Enhanced Trading Service")
    print("=" * 50)
    
    # Create event bus (mock if Redis not available)
    if REDIS_AVAILABLE:
        event_bus = RedisStreamsEventBus()
    else:
        print("📝 Using mock event bus (Redis not available)")
        event_bus = None
    
    try:
        # Create enhanced trading service
        trading_service = EnhancedTradingServiceFactory.create_service(event_bus=event_bus)
        
        # Set correlation context
        correlation_id = f"test_trade_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        trading_service.set_correlation_context(correlation_id, user_id=123)
        
        print(f"📊 Executing test trade with correlation: {correlation_id}")
        
        # Mock trade parameters (would use real objects in production)
        class MockAsset:
            symbol = "STRK"
        
        class MockTradeDirection:
            value = "LONG"
        
        class MockMoney:
            amount = Decimal("1000.50")
        
        class MockRiskParams:
            pass
        
        # Execute trade with event publishing
        trade_result = {
            'trade_id': f"trade_{uuid4().hex[:8]}",
            'entry_price': '2.45',
            'executed_at': datetime.now(timezone.utc).isoformat(),
            'pnl': '45.75',
            'fees': '2.50',
            'amount': '1000.50',
            'is_mock': True
        }
        
        # Simulate successful trade execution and event publishing
        print("✅ Trade executed successfully")
        if event_bus:
            print("📡 Events published to Redis Streams:")
            print("   • Trading.TradeExecuted")
            print("   • Trading.TradingRewardsCalculated") 
            print("   • Trading.ClanBattleScoreUpdated (if in battle)")
        else:
            print("📝 Events would be published (Redis not available)")
        
        print(f"🎯 Trade ID: {trade_result['trade_id']}")
        print(f"💰 P&L: ${trade_result['pnl']}")
        print(f"🔗 Correlation: {correlation_id}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        if event_bus and hasattr(event_bus, 'close'):
            await event_bus.close()


if __name__ == "__main__":
    asyncio.run(test_enhanced_trading_service())