#!/usr/bin/env python3
"""
Integration tests for TradingDomainService
Tests the domain service with mock dependencies
"""

import sys
import asyncio
from decimal import Decimal
from typing import Dict, List, Optional, Any

# Add the backend path
sys.path.append('apps/backend')

def run_test(test_name, test_func):
    """Run a single async test and report results."""
    try:
        asyncio.run(test_func())
        print(f"✅ {test_name}")
        return True
    except Exception as e:
        print(f"❌ {test_name}: {e}")
        import traceback
        traceback.print_exc()
        return False

# Mock implementations for testing
class MockTradeRepository:
    def __init__(self):
        self.trades = {}
        self.trade_counter = 0
    
    async def save(self, trade):
        self.trades[trade.trade_id] = trade
        return trade
    
    async def get_by_id(self, trade_id):
        return self.trades.get(trade_id)
    
    async def get_user_trades(self, user_id, limit=100):
        return [t for t in self.trades.values() if t.user_id == user_id][:limit]
    
    async def get_user_trades_count(self, user_id, since=None):
        user_trades = [t for t in self.trades.values() if t.user_id == user_id]
        if since:
            user_trades = [t for t in user_trades if t.created_at >= since]
        return len(user_trades)

class MockPortfolioRepository:
    def __init__(self):
        self.portfolios = {}
    
    async def save(self, portfolio):
        self.portfolios[portfolio.user_id] = portfolio
        return portfolio
    
    async def get_by_user_id(self, user_id):
        from domains.trading.entities import Portfolio
        from domains.trading.value_objects import Money
        
        if user_id not in self.portfolios:
            # Create default portfolio
            portfolio = Portfolio(user_id, Money(Decimal('10000'), 'USD'))
            self.portfolios[user_id] = portfolio
        return self.portfolios[user_id]

class MockExchangeClient:
    async def place_order(self, symbol, side, amount, leverage=None):
        return {
            'price': Decimal('50000'),  # Mock BTC price
            'order_id': f'MOCK-{symbol}-{side}',
            'timestamp': '2025-07-31T12:00:00Z'
        }
    
    async def get_current_price(self, symbol):
        prices = {
            'BTCUSD': Decimal('50000'),
            'ETHUSD': Decimal('3000'),
        }
        return prices.get(symbol, Decimal('100'))
    
    async def get_trades(self, start_time, end_time, limit=1000):
        return {
            'trades': [
                {
                    'symbol': 'BTCUSD',
                    'side': 'buy',
                    'quantity': '0.1',
                    'price': '50000',
                    'timestamp': start_time
                }
            ]
        }

class MockStarknetClient:
    async def update_user_points(self, user_address, points_delta):
        return True
    
    async def mint_achievement(self, user_address, achievement_id):
        return True

class MockAIAnalysisService:
    async def get_trading_recommendation(self, user_id, market_data, user_profile, trading_history):
        return {
            'recommendation': 'LONG',
            'confidence': 0.75,
            'reasoning': 'Mock AI analysis suggests bullish trend'
        }

class MockEventBus:
    def __init__(self):
        self.events = []
    
    async def emit(self, event):
        self.events.append(event)
    
    async def subscribe(self, event_type, handler):
        pass
    
    async def unsubscribe(self, event_type, handler):
        pass

async def test_trading_domain_service_initialization():
    """Test TradingDomainService can be initialized with mock dependencies."""
    from domains.trading.services import TradingDomainService
    
    service = TradingDomainService(
        trade_repository=MockTradeRepository(),
        portfolio_repository=MockPortfolioRepository(),
        exchange_client=MockExchangeClient(),
        starknet_client=MockStarknetClient(),
        ai_analysis_service=MockAIAnalysisService(),
        event_bus=MockEventBus()
    )
    
    assert service is not None

async def test_execute_mock_trade():
    """Test executing a mock trade through the domain service."""
    from domains.trading.services import TradingDomainService
    from domains.trading.value_objects import Asset, Money, RiskParameters, TradeDirection, AssetCategory
    
    # Setup service with mocks
    event_bus = MockEventBus()
    service = TradingDomainService(
        trade_repository=MockTradeRepository(),
        portfolio_repository=MockPortfolioRepository(),
        exchange_client=MockExchangeClient(),
        starknet_client=MockStarknetClient(),
        ai_analysis_service=MockAIAnalysisService(),
        event_bus=event_bus
    )
    
    # Execute trade
    asset = Asset("BTCUSD", "Bitcoin to USD", AssetCategory.CRYPTO)
    amount = Money(Decimal('1000'), 'USD')
    risk_params = RiskParameters(
        max_position_pct=Decimal('10'),
        stop_loss_pct=Decimal('2'),
        take_profit_pct=Decimal('4')
    )
    
    result = await service.execute_trade(
        user_id=1,
        asset=asset,
        direction=TradeDirection.LONG,
        amount=amount,
        risk_params=risk_params,
        is_mock=True
    )
    
    # Verify result
    assert result['status'] == 'success'
    assert 'trade_id' in result
    assert 'executed_price' in result
    assert 'rewards' in result
    
    # Verify events were emitted
    assert len(event_bus.events) >= 1

async def test_get_portfolio():
    """Test getting user portfolio through domain service."""
    from domains.trading.services import TradingDomainService
    
    service = TradingDomainService(
        trade_repository=MockTradeRepository(),
        portfolio_repository=MockPortfolioRepository(),
        exchange_client=MockExchangeClient(),
        starknet_client=MockStarknetClient(),
        ai_analysis_service=MockAIAnalysisService(),
        event_bus=MockEventBus()
    )
    
    portfolio = await service.get_portfolio(user_id=1)
    
    assert portfolio is not None
    assert portfolio.user_id == 1
    assert portfolio.available_balance.amount == Decimal('10000')

async def test_ai_trading_recommendation():
    """Test getting AI trading recommendation."""
    from domains.trading.services import TradingDomainService
    from domains.trading.value_objects import Asset, AssetCategory
    
    service = TradingDomainService(
        trade_repository=MockTradeRepository(),
        portfolio_repository=MockPortfolioRepository(),
        exchange_client=MockExchangeClient(),
        starknet_client=MockStarknetClient(),
        ai_analysis_service=MockAIAnalysisService(),
        event_bus=MockEventBus()
    )
    
    asset = Asset("BTCUSD", "Bitcoin to USD", AssetCategory.CRYPTO)
    recommendation = await service.get_ai_trading_recommendation(user_id=1, asset=asset)
    
    assert recommendation is not None
    assert 'recommendation' in recommendation
    assert recommendation['recommendation'] == 'LONG'

async def test_calculate_clan_battle_score():
    """Test clan battle score calculation."""
    from domains.trading.services import TradingDomainService
    from datetime import datetime, timezone, timedelta
    
    service = TradingDomainService(
        trade_repository=MockTradeRepository(),
        portfolio_repository=MockPortfolioRepository(),
        exchange_client=MockExchangeClient(),
        starknet_client=MockStarknetClient(),
        ai_analysis_service=MockAIAnalysisService(),
        event_bus=MockEventBus()
    )
    
    # Calculate battle score for empty period
    start_time = datetime.now(timezone.utc) - timedelta(hours=1)
    end_time = datetime.now(timezone.utc)
    
    battle_score = await service.calculate_clan_battle_score(
        user_id=1,
        battle_id=1,
        start_time=start_time,
        end_time=end_time
    )
    
    assert battle_score is not None
    assert 'total_score' in battle_score
    assert 'trade_count' in battle_score
    assert 'pnl_usd' in battle_score

def main():
    """Run all integration tests."""
    print("🧪 Running Trading Domain Integration Tests\n")
    
    tests = [
        ("TradingDomainService Initialization", test_trading_domain_service_initialization),
        ("Execute Mock Trade", test_execute_mock_trade),
        ("Get Portfolio", test_get_portfolio),
        ("AI Trading Recommendation", test_ai_trading_recommendation),
        ("Calculate Clan Battle Score", test_calculate_clan_battle_score),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        if run_test(test_name, test_func):
            passed += 1
        
    print(f"\n📊 Integration Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All integration tests passed! Domain service is working correctly.")
        return 0
    else:
        print("❌ Some integration tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())