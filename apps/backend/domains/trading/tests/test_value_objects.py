"""
Tests for Trading Domain Value Objects

Comprehensive test suite validating all value objects in the Trading Domain
following the same patterns established in other domains.
"""

import pytest
from decimal import Decimal
from dataclasses import FrozenInstanceError

from ..value_objects import (
    Asset, Money, RiskParameters, TradeDirection, TradeStatus, AssetCategory
)


class TestAsset:
    """Test Asset value object"""
    
    def test_create_crypto_asset(self):
        """Test creating a cryptocurrency asset"""
        asset = Asset(
            symbol="BTC",
            name="Bitcoin",
            category=AssetCategory.CRYPTO
        )
        
        assert asset.symbol == "BTC"
        assert asset.name == "Bitcoin"
        assert asset.category == AssetCategory.CRYPTO
        assert asset.is_crypto()
        assert not asset.is_forex()
    
    def test_create_forex_asset(self):
        """Test creating a forex asset"""
        asset = Asset(
            symbol="EURUSD",
            name="Euro/US Dollar",
            category=AssetCategory.FOREX
        )
        
        assert asset.symbol == "EURUSD"
        assert asset.name == "Euro/US Dollar" 
        assert asset.category == AssetCategory.FOREX
        assert asset.is_forex()
        assert not asset.is_crypto()
    
    def test_asset_validation(self):
        """Test asset input validation"""
        # Test invalid symbol
        with pytest.raises(ValueError, match="Symbol cannot be empty"):
            Asset("", "Bitcoin", AssetCategory.CRYPTO)
            
        # Test invalid name
        with pytest.raises(ValueError, match="Name cannot be empty"):
            Asset("BTC", "", AssetCategory.CRYPTO)
    
    def test_asset_immutability(self):
        """Test that asset is immutable"""
        asset = Asset("BTC", "Bitcoin", AssetCategory.CRYPTO)
        
        with pytest.raises(FrozenInstanceError):
            asset.symbol = "ETH"
    
    def test_asset_equality(self):
        """Test value equality for assets"""
        asset1 = Asset("BTC", "Bitcoin", AssetCategory.CRYPTO)
        asset2 = Asset("BTC", "Bitcoin", AssetCategory.CRYPTO)
        asset3 = Asset("ETH", "Ethereum", AssetCategory.CRYPTO)
        
        assert asset1 == asset2
        assert asset1 != asset3
        assert hash(asset1) == hash(asset2)


class TestMoney:
    """Test Money value object"""
    
    def test_create_money_from_decimal(self):
        """Test creating money from Decimal"""
        money = Money(Decimal("100.50"), "USD")
        
        assert money.amount == Decimal("100.50")
        assert money.currency == "USD"
        assert money.is_usd()
        assert not money.is_eur()
    
    def test_create_money_from_float(self):
        """Test creating money from float"""
        money = Money(100.50, "EUR")
        
        assert money.amount == Decimal("100.50")
        assert money.currency == "EUR"
        assert money.is_eur()
    
    def test_money_arithmetic(self):
        """Test money arithmetic operations"""
        money1 = Money(Decimal("100.00"), "USD")
        money2 = Money(Decimal("50.00"), "USD")
        
        # Addition
        result = money1 + money2
        assert result.amount == Decimal("150.00")
        assert result.currency == "USD"
        
        # Subtraction
        result = money1 - money2
        assert result.amount == Decimal("50.00")
        assert result.currency == "USD"
        
        # Multiplication by scalar
        result = money1 * 2
        assert result.amount == Decimal("200.00")
        assert result.currency == "USD"
    
    def test_money_currency_mismatch(self):
        """Test arithmetic with different currencies fails"""
        money_usd = Money(Decimal("100.00"), "USD")
        money_eur = Money(Decimal("50.00"), "EUR")
        
        with pytest.raises(ValueError, match="Currency mismatch"):
            money_usd + money_eur
            
        with pytest.raises(ValueError, match="Currency mismatch"):
            money_usd - money_eur
    
    def test_money_validation(self):
        """Test money validation"""
        # Test negative amount allowed
        money = Money(Decimal("-100.00"), "USD")
        assert money.amount == Decimal("-100.00")
        
        # Test empty currency
        with pytest.raises(ValueError, match="Currency cannot be empty"):
            Money(Decimal("100.00"), "")
    
    def test_money_precision(self):
        """Test money decimal precision"""
        money = Money(Decimal("100.123456"), "USD")
        rounded = money.round_to_cents()
        
        assert rounded.amount == Decimal("100.12")
        assert rounded.currency == "USD"
    
    def test_money_comparison(self):
        """Test money comparison operations"""
        money1 = Money(Decimal("100.00"), "USD")
        money2 = Money(Decimal("150.00"), "USD")
        money3 = Money(Decimal("100.00"), "USD")
        
        assert money1 < money2
        assert money2 > money1
        assert money1 == money3
        assert money1 <= money3
        assert money1 >= money3
    
    def test_money_immutability(self):
        """Test that money is immutable"""
        money = Money(Decimal("100.00"), "USD")
        
        with pytest.raises(FrozenInstanceError):
            money.amount = Decimal("200.00")


class TestRiskParameters:
    """Test RiskParameters value object"""
    
    def test_create_risk_parameters(self):
        """Test creating risk parameters"""
        risk = RiskParameters(
            stop_loss_percentage=Decimal("5.0"),
            take_profit_percentage=Decimal("10.0"),
            max_position_size=Money(Decimal("1000.00"), "USD")
        )
        
        assert risk.stop_loss_percentage == Decimal("5.0")
        assert risk.take_profit_percentage == Decimal("10.0")
        assert risk.max_position_size.amount == Decimal("1000.00")
    
    def test_risk_parameters_validation(self):
        """Test risk parameters validation"""
        # Test negative stop loss
        with pytest.raises(ValueError, match="Stop loss percentage must be positive"):
            RiskParameters(
                stop_loss_percentage=Decimal("-5.0"),
                take_profit_percentage=Decimal("10.0"),
                max_position_size=Money(Decimal("1000.00"), "USD")
            )
        
        # Test negative take profit
        with pytest.raises(ValueError, match="Take profit percentage must be positive"):
            RiskParameters(
                stop_loss_percentage=Decimal("5.0"),
                take_profit_percentage=Decimal("-10.0"),
                max_position_size=Money(Decimal("1000.00"), "USD")
            )
        
        # Test zero max position size
        with pytest.raises(ValueError, match="Max position size must be positive"):
            RiskParameters(
                stop_loss_percentage=Decimal("5.0"),
                take_profit_percentage=Decimal("10.0"),
                max_position_size=Money(Decimal("0.00"), "USD")
            )
    
    def test_calculate_stop_loss_price(self):
        """Test stop loss price calculation"""
        risk = RiskParameters(
            stop_loss_percentage=Decimal("5.0"),
            take_profit_percentage=Decimal("10.0"),
            max_position_size=Money(Decimal("1000.00"), "USD")
        )
        
        entry_price = Money(Decimal("100.00"), "USD")
        
        # Long position stop loss
        stop_loss = risk.calculate_stop_loss_price(entry_price, TradeDirection.LONG)
        assert stop_loss.amount == Decimal("95.00")
        
        # Short position stop loss
        stop_loss = risk.calculate_stop_loss_price(entry_price, TradeDirection.SHORT)
        assert stop_loss.amount == Decimal("105.00")
    
    def test_calculate_take_profit_price(self):
        """Test take profit price calculation"""
        risk = RiskParameters(
            stop_loss_percentage=Decimal("5.0"),
            take_profit_percentage=Decimal("10.0"),
            max_position_size=Money(Decimal("1000.00"), "USD")
        )
        
        entry_price = Money(Decimal("100.00"), "USD")
        
        # Long position take profit
        take_profit = risk.calculate_take_profit_price(entry_price, TradeDirection.LONG)
        assert take_profit.amount == Decimal("110.00")
        
        # Short position take profit
        take_profit = risk.calculate_take_profit_price(entry_price, TradeDirection.SHORT)
        assert take_profit.amount == Decimal("90.00")
    
    def test_risk_parameters_immutability(self):
        """Test that risk parameters are immutable"""
        risk = RiskParameters(
            stop_loss_percentage=Decimal("5.0"),
            take_profit_percentage=Decimal("10.0"),
            max_position_size=Money(Decimal("1000.00"), "USD")
        )
        
        with pytest.raises(FrozenInstanceError):
            risk.stop_loss_percentage = Decimal("10.0")


class TestEnums:
    """Test enum value objects"""
    
    def test_trade_direction_enum(self):
        """Test TradeDirection enum"""
        assert TradeDirection.LONG.value == "long"
        assert TradeDirection.SHORT.value == "short"
        
        # Test enum comparison
        assert TradeDirection.LONG != TradeDirection.SHORT
        assert TradeDirection.LONG == TradeDirection.LONG
    
    def test_trade_status_enum(self):
        """Test TradeStatus enum"""
        assert TradeStatus.PENDING.value == "pending"
        assert TradeStatus.ACTIVE.value == "active"
        assert TradeStatus.COMPLETED.value == "completed"
        assert TradeStatus.FAILED.value == "failed"
        assert TradeStatus.CANCELLED.value == "cancelled"
    
    def test_asset_category_enum(self):
        """Test AssetCategory enum"""
        assert AssetCategory.CRYPTO.value == "crypto"
        assert AssetCategory.FOREX.value == "forex"
        assert AssetCategory.COMMODITIES.value == "commodities"
        assert AssetCategory.INDICES.value == "indices"


if __name__ == "__main__":
    # Run basic smoke tests
    print("Running Trading Domain Value Objects Tests...")
    
    # Test Asset creation
    asset = Asset("BTC", "Bitcoin", AssetCategory.CRYPTO)
    print(f"✅ Asset: {asset.symbol} - {asset.name}")
    
    # Test Money creation
    money = Money(Decimal("100.50"), "USD")
    print(f"✅ Money: {money.amount} {money.currency}")
    
    # Test RiskParameters creation
    risk = RiskParameters(
        stop_loss_percentage=Decimal("5.0"),
        take_profit_percentage=Decimal("10.0"),
        max_position_size=Money(Decimal("1000.00"), "USD")
    )
    print(f"✅ RiskParameters: SL={risk.stop_loss_percentage}%, TP={risk.take_profit_percentage}%")
    
    print("✅ All value object tests passed!")