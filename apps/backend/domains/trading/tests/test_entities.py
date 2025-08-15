"""
Tests for Trading Domain Entities

Comprehensive test suite validating all entities in the Trading Domain
following the same patterns established in other domains.
"""

import pytest
from decimal import Decimal
from datetime import datetime, timezone

from ..entities import Trade, Portfolio, Position
from ..value_objects import (
    Asset, Money, RiskParameters, TradeDirection, TradeStatus, AssetCategory
)


class TestTrade:
    """Test Trade entity"""
    
    def test_create_trade(self):
        """Test creating a new trade"""
        asset = Asset("BTC", "Bitcoin", AssetCategory.CRYPTO)
        amount = Money(Decimal("1000.00"), "USD")
        risk = RiskParameters(
            stop_loss_percentage=Decimal("5.0"),
            take_profit_percentage=Decimal("10.0"),
            max_position_size=Money(Decimal("5000.00"), "USD")
        )
        
        trade = Trade(
            user_id=123,
            asset=asset,
            direction=TradeDirection.LONG,
            amount=amount,
            risk_parameters=risk
        )
        
        assert trade.user_id == 123
        assert trade.asset == asset
        assert trade.direction == TradeDirection.LONG
        assert trade.amount == amount
        assert trade.status == TradeStatus.PENDING
        assert trade.risk_parameters == risk
        assert trade.trade_id is not None
        assert trade.created_at is not None
    
    def test_execute_trade(self):
        """Test executing a pending trade"""
        asset = Asset("BTC", "Bitcoin", AssetCategory.CRYPTO)
        amount = Money(Decimal("1000.00"), "USD")
        
        trade = Trade(
            user_id=123,
            asset=asset,
            direction=TradeDirection.LONG,
            amount=amount
        )
        
        entry_price = Money(Decimal("50000.00"), "USD")
        trade.execute(entry_price)
        
        assert trade.status == TradeStatus.ACTIVE
        assert trade.entry_price == entry_price
        assert trade.executed_at is not None
    
    def test_execute_trade_validation(self):
        """Test trade execution validation"""
        asset = Asset("BTC", "Bitcoin", AssetCategory.CRYPTO)
        amount = Money(Decimal("1000.00"), "USD")
        
        trade = Trade(
            user_id=123,
            asset=asset,
            direction=TradeDirection.LONG,
            amount=amount
        )
        
        # Execute trade first
        entry_price = Money(Decimal("50000.00"), "USD")
        trade.execute(entry_price)
        
        # Try to execute again
        with pytest.raises(ValueError, match="Trade is not in PENDING status"):
            trade.execute(entry_price)
    
    def test_close_trade(self):
        """Test closing an active trade"""
        asset = Asset("BTC", "Bitcoin", AssetCategory.CRYPTO)
        amount = Money(Decimal("1000.00"), "USD")
        
        trade = Trade(
            user_id=123,
            asset=asset,
            direction=TradeDirection.LONG,
            amount=amount
        )
        
        # Execute trade
        entry_price = Money(Decimal("50000.00"), "USD")
        trade.execute(entry_price)
        
        # Close trade
        exit_price = Money(Decimal("55000.00"), "USD")
        trade.close(exit_price)
        
        assert trade.status == TradeStatus.COMPLETED
        assert trade.exit_price == exit_price
        assert trade.closed_at is not None
    
    def test_calculate_pnl_long_profit(self):
        """Test P&L calculation for profitable long trade"""
        asset = Asset("BTC", "Bitcoin", AssetCategory.CRYPTO)
        amount = Money(Decimal("1000.00"), "USD")
        
        trade = Trade(
            user_id=123,
            asset=asset,
            direction=TradeDirection.LONG,
            amount=amount
        )
        
        # Execute and close trade with profit
        entry_price = Money(Decimal("50000.00"), "USD")
        trade.execute(entry_price)
        
        exit_price = Money(Decimal("55000.00"), "USD")
        trade.close(exit_price)
        
        pnl = trade.calculate_pnl()
        # 1000 * (55000 - 50000) / 50000 = 100
        assert pnl.amount == Decimal("100.00")
        assert pnl.currency == "USD"
    
    def test_calculate_pnl_short_profit(self):
        """Test P&L calculation for profitable short trade"""
        asset = Asset("BTC", "Bitcoin", AssetCategory.CRYPTO)
        amount = Money(Decimal("1000.00"), "USD")
        
        trade = Trade(
            user_id=123,
            asset=asset,
            direction=TradeDirection.SHORT,
            amount=amount
        )
        
        # Execute and close trade with profit
        entry_price = Money(Decimal("50000.00"), "USD")
        trade.execute(entry_price)
        
        exit_price = Money(Decimal("45000.00"), "USD")
        trade.close(exit_price)
        
        pnl = trade.calculate_pnl()
        # 1000 * (50000 - 45000) / 50000 = 100
        assert pnl.amount == Decimal("100.00")
        assert pnl.currency == "USD"
    
    def test_calculate_unrealized_pnl(self):
        """Test unrealized P&L calculation for active trade"""
        asset = Asset("BTC", "Bitcoin", AssetCategory.CRYPTO)
        amount = Money(Decimal("1000.00"), "USD")
        
        trade = Trade(
            user_id=123,
            asset=asset,
            direction=TradeDirection.LONG,
            amount=amount
        )
        
        # Execute trade
        entry_price = Money(Decimal("50000.00"), "USD")
        trade.execute(entry_price)
        
        # Calculate unrealized P&L
        current_price = Money(Decimal("52000.00"), "USD")
        unrealized_pnl = trade.calculate_unrealized_pnl(current_price)
        
        # 1000 * (52000 - 50000) / 50000 = 40
        assert unrealized_pnl.amount == Decimal("40.00")
        assert unrealized_pnl.currency == "USD"
    
    def test_trade_validation(self):
        """Test trade input validation"""
        asset = Asset("BTC", "Bitcoin", AssetCategory.CRYPTO)
        
        # Test invalid user ID
        with pytest.raises(ValueError, match="User ID must be positive"):
            Trade(
                user_id=0,
                asset=asset,
                direction=TradeDirection.LONG,
                amount=Money(Decimal("1000.00"), "USD")
            )
        
        # Test zero amount
        with pytest.raises(ValueError, match="Amount must be positive"):
            Trade(
                user_id=123,
                asset=asset,
                direction=TradeDirection.LONG,
                amount=Money(Decimal("0.00"), "USD")
            )


class TestPosition:
    """Test Position entity"""
    
    def test_create_position(self):
        """Test creating a new position"""
        asset = Asset("BTC", "Bitcoin", AssetCategory.CRYPTO)
        quantity = Decimal("0.1")
        avg_price = Money(Decimal("50000.00"), "USD")
        
        position = Position(
            user_id=123,
            asset=asset,
            quantity=quantity,
            average_price=avg_price
        )
        
        assert position.user_id == 123
        assert position.asset == asset
        assert position.quantity == quantity
        assert position.average_price == avg_price
        assert position.position_id is not None
        assert position.created_at is not None
    
    def test_update_position_add(self):
        """Test updating position by adding quantity"""
        asset = Asset("BTC", "Bitcoin", AssetCategory.CRYPTO)
        
        position = Position(
            user_id=123,
            asset=asset,
            quantity=Decimal("0.1"),
            average_price=Money(Decimal("50000.00"), "USD")
        )
        
        # Add more quantity at different price
        position.update_quantity(
            Decimal("0.1"),
            Money(Decimal("55000.00"), "USD")
        )
        
        assert position.quantity == Decimal("0.2")
        # New average: (0.1 * 50000 + 0.1 * 55000) / 0.2 = 52500
        assert position.average_price.amount == Decimal("52500.00")
        assert position.updated_at is not None
    
    def test_update_position_reduce(self):
        """Test updating position by reducing quantity"""
        asset = Asset("BTC", "Bitcoin", AssetCategory.CRYPTO)
        
        position = Position(
            user_id=123,
            asset=asset,
            quantity=Decimal("0.2"),
            average_price=Money(Decimal("50000.00"), "USD")
        )
        
        # Reduce quantity
        position.update_quantity(
            Decimal("-0.1"),
            Money(Decimal("55000.00"), "USD")  # Exit price for realized P&L
        )
        
        assert position.quantity == Decimal("0.1")
        assert position.average_price.amount == Decimal("50000.00")  # Average stays same
    
    def test_calculate_market_value(self):
        """Test market value calculation"""
        asset = Asset("BTC", "Bitcoin", AssetCategory.CRYPTO)
        
        position = Position(
            user_id=123,
            asset=asset,
            quantity=Decimal("0.1"),
            average_price=Money(Decimal("50000.00"), "USD")
        )
        
        current_price = Money(Decimal("55000.00"), "USD")
        market_value = position.calculate_market_value(current_price)
        
        # 0.1 * 55000 = 5500
        assert market_value.amount == Decimal("5500.00")
        assert market_value.currency == "USD"
    
    def test_calculate_unrealized_pnl(self):
        """Test unrealized P&L calculation"""
        asset = Asset("BTC", "Bitcoin", AssetCategory.CRYPTO)
        
        position = Position(
            user_id=123,
            asset=asset,
            quantity=Decimal("0.1"),
            average_price=Money(Decimal("50000.00"), "USD")
        )
        
        current_price = Money(Decimal("55000.00"), "USD")
        unrealized_pnl = position.calculate_unrealized_pnl(current_price)
        
        # 0.1 * (55000 - 50000) = 500
        assert unrealized_pnl.amount == Decimal("500.00")
        assert unrealized_pnl.currency == "USD"
    
    def test_position_validation(self):
        """Test position input validation"""
        asset = Asset("BTC", "Bitcoin", AssetCategory.CRYPTO)
        
        # Test invalid user ID
        with pytest.raises(ValueError, match="User ID must be positive"):
            Position(
                user_id=0,
                asset=asset,
                quantity=Decimal("0.1"),
                average_price=Money(Decimal("50000.00"), "USD")
            )
        
        # Test zero quantity
        with pytest.raises(ValueError, match="Quantity cannot be zero"):
            Position(
                user_id=123,
                asset=asset,
                quantity=Decimal("0.0"),
                average_price=Money(Decimal("50000.00"), "USD")
            )
        
        # Test zero average price
        with pytest.raises(ValueError, match="Average price must be positive"):
            Position(
                user_id=123,
                asset=asset,
                quantity=Decimal("0.1"),
                average_price=Money(Decimal("0.00"), "USD")
            )


class TestPortfolio:
    """Test Portfolio entity"""
    
    def test_create_portfolio(self):
        """Test creating a new portfolio"""
        portfolio = Portfolio(
            user_id=123,
            base_currency="USD"
        )
        
        assert portfolio.user_id == 123
        assert portfolio.base_currency == "USD"
        assert portfolio.portfolio_id is not None
        assert portfolio.created_at is not None
        assert len(portfolio.positions) == 0
        assert len(portfolio.trades) == 0
    
    def test_add_trade_to_portfolio(self):
        """Test adding trade to portfolio"""
        portfolio = Portfolio(
            user_id=123,
            base_currency="USD"
        )
        
        asset = Asset("BTC", "Bitcoin", AssetCategory.CRYPTO)
        trade = Trade(
            user_id=123,
            asset=asset,
            direction=TradeDirection.LONG,
            amount=Money(Decimal("1000.00"), "USD")
        )
        
        portfolio.add_trade(trade)
        
        assert len(portfolio.trades) == 1
        assert portfolio.trades[0] == trade
    
    def test_add_position_to_portfolio(self):
        """Test adding position to portfolio"""
        portfolio = Portfolio(
            user_id=123,
            base_currency="USD"
        )
        
        asset = Asset("BTC", "Bitcoin", AssetCategory.CRYPTO)
        position = Position(
            user_id=123,
            asset=asset,
            quantity=Decimal("0.1"),
            average_price=Money(Decimal("50000.00"), "USD")
        )
        
        portfolio.add_position(position)
        
        assert len(portfolio.positions) == 1
        assert portfolio.positions[0] == position
    
    def test_calculate_total_value(self):
        """Test total portfolio value calculation"""
        portfolio = Portfolio(
            user_id=123,
            base_currency="USD"
        )
        
        # Add positions
        btc_asset = Asset("BTC", "Bitcoin", AssetCategory.CRYPTO)
        btc_position = Position(
            user_id=123,
            asset=btc_asset,
            quantity=Decimal("0.1"),
            average_price=Money(Decimal("50000.00"), "USD")
        )
        
        eth_asset = Asset("ETH", "Ethereum", AssetCategory.CRYPTO)
        eth_position = Position(
            user_id=123,
            asset=eth_asset,
            quantity=Decimal("1.0"),
            average_price=Money(Decimal("3000.00"), "USD")
        )
        
        portfolio.add_position(btc_position)
        portfolio.add_position(eth_position)
        
        # Calculate total value
        current_prices = {
            "BTC": Money(Decimal("55000.00"), "USD"),
            "ETH": Money(Decimal("3500.00"), "USD")
        }
        
        total_value = portfolio.calculate_total_value(current_prices)
        
        # BTC: 0.1 * 55000 = 5500
        # ETH: 1.0 * 3500 = 3500
        # Total: 9000
        assert total_value.amount == Decimal("9000.00")
        assert total_value.currency == "USD"
    
    def test_calculate_total_pnl(self):
        """Test total portfolio P&L calculation"""
        portfolio = Portfolio(
            user_id=123,
            base_currency="USD"
        )
        
        # Add position
        asset = Asset("BTC", "Bitcoin", AssetCategory.CRYPTO)
        position = Position(
            user_id=123,
            asset=asset,
            quantity=Decimal("0.1"),
            average_price=Money(Decimal("50000.00"), "USD")
        )
        portfolio.add_position(position)
        
        # Add completed trade
        trade = Trade(
            user_id=123,
            asset=asset,
            direction=TradeDirection.LONG,
            amount=Money(Decimal("1000.00"), "USD")
        )
        trade.execute(Money(Decimal("50000.00"), "USD"))
        trade.close(Money(Decimal("55000.00"), "USD"))
        portfolio.add_trade(trade)
        
        # Calculate total P&L
        current_prices = {"BTC": Money(Decimal("55000.00"), "USD")}
        total_pnl = portfolio.calculate_total_pnl(current_prices)
        
        # Position unrealized P&L: 0.1 * (55000 - 50000) = 500
        # Trade realized P&L: 100 (from previous test)
        # Total: 600
        assert total_pnl.amount == Decimal("600.00")
        assert total_pnl.currency == "USD"
    
    def test_portfolio_validation(self):
        """Test portfolio input validation"""
        # Test invalid user ID
        with pytest.raises(ValueError, match="User ID must be positive"):
            Portfolio(user_id=0, base_currency="USD")
        
        # Test empty base currency
        with pytest.raises(ValueError, match="Base currency cannot be empty"):
            Portfolio(user_id=123, base_currency="")


if __name__ == "__main__":
    # Run basic smoke tests
    print("Running Trading Domain Entity Tests...")
    
    # Test Trade creation
    asset = Asset("BTC", "Bitcoin", AssetCategory.CRYPTO)
    trade = Trade(
        user_id=123,
        asset=asset,
        direction=TradeDirection.LONG,
        amount=Money(Decimal("1000.00"), "USD")
    )
    print(f"✅ Trade: {trade.trade_id} - {trade.asset.symbol} {trade.direction.value}")
    
    # Test Position creation
    position = Position(
        user_id=123,
        asset=asset,
        quantity=Decimal("0.1"),
        average_price=Money(Decimal("50000.00"), "USD")
    )
    print(f"✅ Position: {position.position_id} - {position.quantity} {position.asset.symbol}")
    
    # Test Portfolio creation
    portfolio = Portfolio(user_id=123, base_currency="USD")
    print(f"✅ Portfolio: {portfolio.portfolio_id} - {portfolio.base_currency}")
    
    print("✅ All entity tests passed!")