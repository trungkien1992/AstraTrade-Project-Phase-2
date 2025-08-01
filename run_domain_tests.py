#!/usr/bin/env python3
"""
Simple test runner for Trading Domain
Runs tests without pytest dependency
"""

import sys
import traceback
from decimal import Decimal

# Add the backend path
sys.path.append('apps/backend')

def run_test(test_name, test_func):
    """Run a single test and report results."""
    try:
        test_func()
        print(f"✅ {test_name}")
        return True
    except Exception as e:
        print(f"❌ {test_name}: {e}")
        # Uncomment for detailed error info:
        # traceback.print_exc()
        return False

def test_asset_creation():
    """Test Asset value object creation."""
    from domains.trading.value_objects import Asset, AssetCategory
    
    # Valid creation
    asset = Asset("BTCUSD", "Bitcoin to USD", AssetCategory.CRYPTO)
    assert asset.symbol == "BTCUSD"
    assert asset.name == "Bitcoin to USD"
    assert asset.category == AssetCategory.CRYPTO
    
    # Uppercase conversion
    asset2 = Asset("btcusd", "Bitcoin to USD", AssetCategory.CRYPTO)
    assert asset2.symbol == "BTCUSD"
    
    # Test methods
    assert asset.is_crypto() == True
    assert asset.is_forex() == False
    
    base, quote = asset.get_base_quote()
    assert base == "BTC"
    assert quote == "USD"

def test_money_creation():
    """Test Money value object creation and operations."""
    from domains.trading.value_objects import Money
    
    # Valid creation
    money1 = Money(Decimal('1000.50'), 'USD')
    assert money1.amount == Decimal('1000.50')
    assert money1.currency == "USD"
    
    # Currency conversion
    money2 = Money(Decimal('500'), 'usd')
    assert money2.currency == "USD"
    
    # Arithmetic operations
    money3 = money1.add(Money(Decimal('500'), 'USD'))
    assert money3.amount == Decimal('1500.50')
    
    money4 = money1.multiply(2)
    assert money4.amount == Decimal('2001.00')
    
    # Comparisons
    assert money1.is_positive() == True
    assert Money(Decimal('0'), 'USD').is_zero() == True

def test_trade_creation():
    """Test Trade entity creation and lifecycle."""
    from domains.trading.entities import Trade
    from domains.trading.value_objects import Asset, Money, TradeDirection, TradeStatus, AssetCategory
    
    # Create trade
    asset = Asset("BTCUSD", "Bitcoin to USD", AssetCategory.CRYPTO)
    amount = Money(Decimal('1000'), 'USD')
    trade = Trade(1, asset, TradeDirection.LONG, amount)
    
    assert trade.user_id == 1
    assert trade.asset == asset
    assert trade.direction == TradeDirection.LONG
    assert trade.amount == amount
    assert trade.status == TradeStatus.PENDING
    
    # Execute trade
    entry_price = Money(Decimal('50000'), 'USD')
    trade.execute(entry_price, "ORDER123")
    
    assert trade.status == TradeStatus.ACTIVE
    assert trade.entry_price == entry_price
    assert trade.exchange_order_id == "ORDER123"

def test_trade_pnl_calculation():
    """Test Trade P&L calculation for long and short positions."""
    from domains.trading.entities import Trade
    from domains.trading.value_objects import Asset, Money, TradeDirection, AssetCategory
    
    asset = Asset("BTCUSD", "Bitcoin to USD", AssetCategory.CRYPTO)
    amount = Money(Decimal('1000'), 'USD')
    entry_price = Money(Decimal('50000'), 'USD')
    
    # Long position profit
    long_trade = Trade(1, asset, TradeDirection.LONG, amount)
    long_trade.execute(entry_price, "ORDER123")
    
    current_price = Money(Decimal('55000'), 'USD')  # 10% increase
    pnl = long_trade.calculate_pnl(current_price)
    pnl_pct = long_trade.calculate_pnl_percentage(current_price)
    
    assert pnl.amount == Decimal('100')  # 10% of 1000
    assert pnl_pct == Decimal('10')
    assert long_trade.is_profitable(current_price) == True
    
    # Short position profit
    short_trade = Trade(2, asset, TradeDirection.SHORT, amount)
    short_trade.execute(entry_price, "ORDER456")
    
    lower_price = Money(Decimal('45000'), 'USD')  # 10% decrease
    short_pnl = short_trade.calculate_pnl(lower_price)
    short_pnl_pct = short_trade.calculate_pnl_percentage(lower_price)
    
    assert short_pnl.amount == Decimal('100')  # 10% profit on short
    assert short_pnl_pct == Decimal('10')
    assert short_trade.is_profitable(lower_price) == True

def test_position_aggregation():
    """Test Position entity aggregation of trades."""
    from domains.trading.entities import Trade, Position
    from domains.trading.value_objects import Asset, Money, TradeDirection, AssetCategory
    
    # Create position with trade
    asset = Asset("BTCUSD", "Bitcoin to USD", AssetCategory.CRYPTO)
    amount = Money(Decimal('1000'), 'USD')
    entry_price = Money(Decimal('50000'), 'USD')
    
    trade = Trade(1, asset, TradeDirection.LONG, amount)
    trade.execute(entry_price, "ORDER123")
    
    position = Position(asset, [trade])
    
    assert position.asset == asset
    assert position.quantity > Decimal('0')
    assert position.is_long() == True
    assert position.is_flat() == False
    assert position.average_entry_price is not None
    
    # Test P&L calculation
    current_price = Money(Decimal('55000'), 'USD')
    unrealized_pnl = position.calculate_unrealized_pnl(current_price)
    assert unrealized_pnl.is_positive()

def test_portfolio_management():
    """Test Portfolio entity and total value calculation."""
    from domains.trading.entities import Trade, Position, Portfolio
    from domains.trading.value_objects import Asset, Money, TradeDirection, AssetCategory
    
    # Create portfolio
    initial_balance = Money(Decimal('10000'), 'USD')
    portfolio = Portfolio(1, initial_balance)
    
    assert portfolio.user_id == 1
    assert portfolio.available_balance == initial_balance
    assert len(portfolio.positions) == 0
    
    # Add position
    asset = Asset("BTCUSD", "Bitcoin to USD", AssetCategory.CRYPTO)
    position = Position(asset)
    portfolio.add_position(position)
    
    assert len(portfolio.positions) == 1
    assert portfolio.get_position("BTCUSD") == position

def test_risk_parameters():
    """Test RiskParameters value object calculations."""
    from domains.trading.value_objects import RiskParameters, Money, TradeDirection
    
    risk_params = RiskParameters(
        max_position_pct=Decimal('10'),    # 10% max position
        stop_loss_pct=Decimal('2'),        # 2% stop loss
        take_profit_pct=Decimal('6')       # 6% take profit
    )
    
    # Test position sizing
    account_balance = Money(Decimal('10000'), 'USD')
    entry_price = Money(Decimal('100'), 'USD')
    
    position_size = risk_params.calculate_position_size(account_balance, entry_price)
    assert position_size.amount == Decimal('10')  # 10% of 10000 / 100
    
    # Test stop loss calculation
    stop_loss_long = risk_params.calculate_stop_loss_price(entry_price, TradeDirection.LONG)
    assert stop_loss_long.amount == Decimal('98')  # 100 - 2%
    
    stop_loss_short = risk_params.calculate_stop_loss_price(entry_price, TradeDirection.SHORT)
    assert stop_loss_short.amount == Decimal('102')  # 100 + 2%
    
    # Test risk/reward ratio
    ratio = risk_params.calculate_risk_reward_ratio()
    assert ratio == Decimal('3')  # 6% / 2%

def test_domain_events():
    """Test domain event system."""
    from domains.shared.events import EventStore, DomainEvent
    from dataclasses import dataclass
    
    @dataclass
    class TestEvent(DomainEvent):
        test_data: str = "default"
        
        @property
        def event_type(self) -> str:
            return "test_event"
    
    # Test event store
    event_store = EventStore()
    test_event = TestEvent(test_data="test")
    
    event_store.append(test_event)
    events = event_store.get_events("test_event")
    
    assert len(events) == 1
    assert events[0].test_data == "test"

def main():
    """Run all tests."""
    print("🧪 Running Trading Domain Tests\n")
    
    tests = [
        ("Asset Creation", test_asset_creation),
        ("Money Operations", test_money_creation),
        ("Trade Creation", test_trade_creation),
        ("Trade P&L Calculation", test_trade_pnl_calculation),
        ("Position Aggregation", test_position_aggregation),
        ("Portfolio Management", test_portfolio_management),
        ("Risk Parameters", test_risk_parameters),
        ("Domain Events", test_domain_events),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        if run_test(test_name, test_func):
            passed += 1
        
    print(f"\n📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Domain implementation is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())