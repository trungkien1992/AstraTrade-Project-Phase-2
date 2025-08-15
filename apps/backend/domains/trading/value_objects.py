"""
Trading Domain Value Objects

Value objects for the Trading Domain as defined in PHASE1_DOMAIN_STRUCTURE.md.
These immutable objects represent domain concepts without identity.

Value Objects implemented:
- Asset: Trading instrument with symbol, name, and category
- Money: Monetary amount with currency (using Decimal for precision)
- RiskParameters: Risk management settings (stop loss, take profit, position sizing)
- TradeDirection: LONG or SHORT positions
- TradeStatus: Lifecycle states for trades
- AssetCategory: Classification of trading instruments

Architecture follows DDD patterns with:
- Immutability (frozen dataclasses)
- Value equality (not identity)
- Domain validation in constructors
- Rich behavior methods
- Type safety
"""

from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Union
import re


class TradeDirection(Enum):
    """Direction of a trade - long (buy) or short (sell)."""
    LONG = "long"
    SHORT = "short"


class TradeStatus(Enum):
    """Lifecycle status of a trade."""
    PENDING = "pending"      # Trade created but not executed
    ACTIVE = "active"        # Trade executed and open
    PARTIALLY_FILLED = "partially_filled"  # Trade partially executed
    FILLED = "filled"        # Trade fully executed
    COMPLETED = "completed"  # Trade closed with profit/loss
    FAILED = "failed"        # Trade execution failed
    CANCELLED = "cancelled"  # Trade cancelled before execution


class AssetCategory(Enum):
    """Category classification for trading assets."""
    CRYPTO = "crypto"
    FOREX = "forex"
    COMMODITIES = "commodities"
    INDICES = "indices"
    STOCKS = "stocks"


@dataclass(frozen=True)
class Asset:
    """
    Asset value object representing a tradeable instrument.
    
    Immutable representation of financial instruments with validation
    for symbol format and business rules.
    
    Invariants:
    - Symbol must be uppercase alphanumeric (e.g., BTCUSD, EURUSD)
    - Name cannot be empty
    - Category must be valid AssetCategory
    """
    symbol: str
    name: str
    category: AssetCategory
    
    def __post_init__(self):
        # Validate symbol format
        if not self.symbol:
            raise ValueError("Asset symbol cannot be empty")
        
        # Convert to uppercase and validate format
        symbol_upper = self.symbol.upper()
        if not re.match(r'^[A-Z0-9]+$', symbol_upper):
            raise ValueError(f"Asset symbol '{self.symbol}' must contain only uppercase letters and numbers")
        
        # Use object.__setattr__ because class is frozen
        object.__setattr__(self, 'symbol', symbol_upper)
        
        # Validate name
        if not self.name or not self.name.strip():
            raise ValueError("Asset name cannot be empty")
        
        # Validate category
        if not isinstance(self.category, AssetCategory):
            raise ValueError("Category must be a valid AssetCategory")
    
    def is_crypto(self) -> bool:
        """Check if this is a cryptocurrency asset."""
        return self.category == AssetCategory.CRYPTO
    
    def is_forex(self) -> bool:
        """Check if this is a forex pair."""
        return self.category == AssetCategory.FOREX
    
    def get_base_quote(self) -> tuple[str, str]:
        """
        Extract base and quote currencies from symbol.
        Works for common patterns like BTCUSD, EURUSD.
        """
        if self.category == AssetCategory.CRYPTO:
            # Common crypto patterns: BTCUSD, ETHUSD, etc.
            if self.symbol.endswith('USD'):
                return self.symbol[:-3], 'USD'
            elif self.symbol.endswith('USDT'):
                return self.symbol[:-4], 'USDT'
        elif self.category == AssetCategory.FOREX:
            # Forex pairs are typically 6 characters: EURUSD, GBPJPY
            if len(self.symbol) == 6:
                return self.symbol[:3], self.symbol[3:]
        
        # Default: assume USD as quote currency
        return self.symbol, 'USD'


@dataclass(frozen=True) 
class Money:
    """
    Money value object representing monetary amounts with currency.
    
    Uses Decimal for precise financial calculations to avoid floating-point
    precision issues critical in financial applications.
    
    Invariants:
    - Amount uses Decimal for precision
    - Currency must be valid 3-character code
    - Supports arithmetic operations with same currency
    - Rounds to appropriate decimal places for currency
    """
    amount: Decimal
    currency: str
    
    def __post_init__(self):
        # Validate currency format
        if not self.currency:
            raise ValueError("Currency cannot be empty")
        
        currency_upper = self.currency.upper()
        if not re.match(r'^[A-Z]{3}$', currency_upper):
            raise ValueError(f"Currency '{self.currency}' must be 3 uppercase letters")
        
        object.__setattr__(self, 'currency', currency_upper)
        
        # Ensure amount is Decimal
        if not isinstance(self.amount, Decimal):
            object.__setattr__(self, 'amount', Decimal(str(self.amount)))
        
        # Round to appropriate decimal places
        decimal_places = self._get_decimal_places()
        rounded_amount = self.amount.quantize(
            Decimal(10) ** -decimal_places, 
            rounding=ROUND_HALF_UP
        )
        object.__setattr__(self, 'amount', rounded_amount)
    
    def _get_decimal_places(self) -> int:
        """Get standard decimal places for currency."""
        # Most fiat currencies use 2 decimal places
        # Cryptocurrencies often use more precision
        crypto_currencies = {'BTC', 'ETH', 'ADA', 'SOL', 'MATIC', 'LINK'}
        
        if self.currency in crypto_currencies:
            return 8  # Crypto precision
        else:
            return 2  # Fiat currency precision
    
    def add(self, other: 'Money') -> 'Money':
        """Add two Money values (same currency only)."""
        self._validate_currency_match(other)
        return Money(self.amount + other.amount, self.currency)
    
    def subtract(self, other: 'Money') -> 'Money':
        """Subtract two Money values (same currency only)."""
        self._validate_currency_match(other)
        return Money(self.amount - other.amount, self.currency)
    
    def multiply(self, factor: Union[Decimal, float, int]) -> 'Money':
        """Multiply Money by a numeric factor."""
        if not isinstance(factor, Decimal):
            factor = Decimal(str(factor))
        return Money(self.amount * factor, self.currency)
    
    def divide(self, divisor: Union[Decimal, float, int]) -> 'Money':
        """Divide Money by a numeric divisor."""
        if not isinstance(divisor, Decimal):
            divisor = Decimal(str(divisor))
        if divisor == Decimal('0'):
            raise ValueError("Cannot divide by zero")
        return Money(self.amount / divisor, self.currency)
    
    def is_positive(self) -> bool:
        """Check if amount is positive."""
        return self.amount > Decimal('0')
    
    def is_negative(self) -> bool:
        """Check if amount is negative."""
        return self.amount < Decimal('0')
    
    def is_zero(self) -> bool:
        """Check if amount is zero."""
        return self.amount == Decimal('0')
    
    def abs(self) -> 'Money':
        """Return absolute value."""
        return Money(abs(self.amount), self.currency)
    
    def _validate_currency_match(self, other: 'Money') -> None:
        """Validate that currencies match for arithmetic operations."""
        if self.currency != other.currency:
            raise ValueError(f"Cannot operate on different currencies: {self.currency} vs {other.currency}")
    
    def __str__(self) -> str:
        """String representation for display."""
        return f"{self.amount} {self.currency}"
    
    def __lt__(self, other: 'Money') -> bool:
        self._validate_currency_match(other)
        return self.amount < other.amount
    
    def __le__(self, other: 'Money') -> bool:
        self._validate_currency_match(other)
        return self.amount <= other.amount
    
    def __gt__(self, other: 'Money') -> bool:
        self._validate_currency_match(other)
        return self.amount > other.amount
    
    def __ge__(self, other: 'Money') -> bool:
        self._validate_currency_match(other)
        return self.amount >= other.amount


@dataclass(frozen=True)
class RiskParameters:
    """
    Risk management parameters for trading positions.
    
    Defines risk controls including position sizing, stop loss, and take profit
    levels as percentages of account balance or position value.
    
    Invariants:
    - All percentages must be between 0 and 100
    - Stop loss must be positive (loss percentage)
    - Take profit must be positive (profit percentage)
    - Max position percentage must not exceed 100% of account
    """
    max_position_pct: Decimal      # Max % of account balance per position
    stop_loss_pct: Decimal         # Stop loss % from entry price
    take_profit_pct: Decimal       # Take profit % from entry price
    max_daily_loss_pct: Optional[Decimal] = None  # Max daily loss % of account
    max_drawdown_pct: Optional[Decimal] = None    # Max account drawdown %
    
    def __post_init__(self):
        # Validate percentages are in valid range
        self._validate_percentage(self.max_position_pct, "max_position_pct")
        self._validate_percentage(self.stop_loss_pct, "stop_loss_pct")
        self._validate_percentage(self.take_profit_pct, "take_profit_pct")
        
        if self.max_daily_loss_pct is not None:
            self._validate_percentage(self.max_daily_loss_pct, "max_daily_loss_pct")
        
        if self.max_drawdown_pct is not None:
            self._validate_percentage(self.max_drawdown_pct, "max_drawdown_pct")
        
        # Business rule validations
        if self.max_position_pct > Decimal('100'):
            raise ValueError("Max position percentage cannot exceed 100%")
        
        if self.stop_loss_pct <= Decimal('0'):
            raise ValueError("Stop loss percentage must be positive")
        
        if self.take_profit_pct <= Decimal('0'):
            raise ValueError("Take profit percentage must be positive")
    
    def _validate_percentage(self, value: Decimal, field_name: str) -> None:
        """Validate that a value is a valid percentage."""
        if not isinstance(value, Decimal):
            raise ValueError(f"{field_name} must be a Decimal")
        
        if value < Decimal('0'):
            raise ValueError(f"{field_name} cannot be negative")
        
        if value > Decimal('1000'):  # Allow up to 1000% for some edge cases
            raise ValueError(f"{field_name} cannot exceed 1000%")
    
    def calculate_position_size(self, account_balance: Money, entry_price: Money) -> Money:
        """
        Calculate position size based on risk parameters.
        
        Uses the max position percentage to determine how much of the account
        balance should be allocated to this position.
        """
        max_allocation = account_balance.multiply(self.max_position_pct / Decimal('100'))
        position_quantity = max_allocation.divide(entry_price.amount)
        return Money(position_quantity.amount, account_balance.currency)
    
    def calculate_stop_loss_price(self, entry_price: Money, direction: TradeDirection) -> Money:
        """Calculate stop loss price based on entry price and direction."""
        stop_loss_multiplier = self.stop_loss_pct / Decimal('100')
        
        if direction == TradeDirection.LONG:
            # For long positions, stop loss is below entry price
            stop_price = entry_price.amount * (Decimal('1') - stop_loss_multiplier)
        else:
            # For short positions, stop loss is above entry price
            stop_price = entry_price.amount * (Decimal('1') + stop_loss_multiplier)
        
        return Money(stop_price, entry_price.currency)
    
    def calculate_take_profit_price(self, entry_price: Money, direction: TradeDirection) -> Money:
        """Calculate take profit price based on entry price and direction."""
        take_profit_multiplier = self.take_profit_pct / Decimal('100')
        
        if direction == TradeDirection.LONG:
            # For long positions, take profit is above entry price
            profit_price = entry_price.amount * (Decimal('1') + take_profit_multiplier)
        else:
            # For short positions, take profit is below entry price
            profit_price = entry_price.amount * (Decimal('1') - take_profit_multiplier)
        
        return Money(profit_price, entry_price.currency)
    
    def calculate_risk_reward_ratio(self) -> Decimal:
        """Calculate risk-to-reward ratio."""
        return self.take_profit_pct / self.stop_loss_pct
    
    def is_conservative(self) -> bool:
        """Check if risk parameters are conservative."""
        return (
            self.max_position_pct <= Decimal('5') and  # Max 5% per position
            self.stop_loss_pct <= Decimal('2') and     # Max 2% stop loss
            self.calculate_risk_reward_ratio() >= Decimal('2')  # At least 1:2 risk/reward
        )
    
    def is_aggressive(self) -> bool:
        """Check if risk parameters are aggressive."""
        return (
            self.max_position_pct >= Decimal('20') or  # 20%+ per position
            self.stop_loss_pct >= Decimal('10') or     # 10%+ stop loss
            self.calculate_risk_reward_ratio() < Decimal('1')  # Less than 1:1 risk/reward
        )