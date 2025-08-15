"""
Trading Domain Entities

Core business entities for the Trading Domain as defined in PHASE1_DOMAIN_STRUCTURE.md.
These entities encapsulate the essential business concepts and invariants.

Domain Entities implemented:
- Trade: Individual trading operations with lifecycle management
- Portfolio: User's collection of positions and overall financial state  
- Position: Specific asset holdings with real-time P&L calculation

Architecture follows DDD patterns with:
- Immutable creation after construction
- Business rule enforcement
- Domain event emission
- Rich domain behavior (not anemic models)
"""

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from uuid import uuid4

from .value_objects import Asset, Money, RiskParameters, TradeDirection, TradeStatus


class Trade:
    """
    Trade entity representing a single trading operation.
    
    Encapsulates the complete lifecycle of a trade from creation to settlement,
    including entry/exit prices, P&L calculation, and associated metadata.
    
    Invariants:
    - Trade ID is immutable once set
    - User ID must be valid
    - Amount must be positive
    - Status transitions follow valid business rules
    - Entry price must be set for active trades
    """
    
    def __init__(
        self,
        user_id: int,
        asset: Asset,
        direction: TradeDirection,
        amount: Money,
        entry_price: Optional[Money] = None,
        trade_id: Optional[str] = None,
        created_at: Optional[datetime] = None
    ):
        self._trade_id = trade_id or str(uuid4())
        self._user_id = self._validate_user_id(user_id)
        self._asset = asset
        self._direction = direction
        self._amount = self._validate_amount(amount)
        self._entry_price = entry_price
        self._exit_price: Optional[Money] = None
        self._status = TradeStatus.PENDING
        self._created_at = created_at or datetime.now(timezone.utc)
        self._closed_at: Optional[datetime] = None
        self._error_message: Optional[str] = None
        self._exchange_order_id: Optional[str] = None
        
        # For partial fills
        self._filled_amount: Money = Money(Decimal('0'), amount.currency)
        self._average_fill_price: Optional[Money] = None
        
        # For idempotency
        self._idempotency_key: Optional[str] = None
        
        # Domain events (would be implemented with proper event system)
        self._domain_events: List[Dict[str, Any]] = []
    
    @property
    def trade_id(self) -> str:
        return self._trade_id
    
    @property
    def user_id(self) -> int:
        return self._user_id
    
    @property 
    def asset(self) -> Asset:
        return self._asset
    
    @property
    def direction(self) -> TradeDirection:
        return self._direction
    
    @property
    def amount(self) -> Money:
        return self._amount
        
    @property
    def entry_price(self) -> Optional[Money]:
        return self._entry_price
        
    @property
    def exit_price(self) -> Optional[Money]:
        return self._exit_price
        
    @property
    def status(self) -> TradeStatus:
        return self._status
        
    @property
    def created_at(self) -> datetime:
        return self._created_at
        
    @property
    def closed_at(self) -> Optional[datetime]:
        return self._closed_at
        
    @property
    def exchange_order_id(self) -> Optional[str]:
        return self._exchange_order_id
    
    def execute(self, entry_price: Money, exchange_order_id: str) -> None:
        """Execute the trade with given entry price and exchange order ID."""
        if self._status != TradeStatus.PENDING:
            raise ValueError(f"Cannot execute trade with status {self._status}")
        
        self._entry_price = entry_price
        self._exchange_order_id = exchange_order_id
        self._status = TradeStatus.ACTIVE
        
        self._add_domain_event("TradeExecuted", {
            "trade_id": self._trade_id,
            "user_id": self._user_id,
            "asset": self._asset.symbol,
            "direction": self._direction.value,
            "amount": float(self._amount.amount),
            "entry_price": float(entry_price.amount),
            "executed_at": datetime.now(timezone.utc).isoformat()
        })
    
    def partially_fill(self, fill_amount: Money, fill_price: Money) -> None:
        """Handle partial fill of a trade."""
        if self._status not in [TradeStatus.PENDING, TradeStatus.PARTIALLY_FILLED]:
            raise ValueError(f"Cannot partially fill trade with status {self._status}")
            
        # Validate currency match
        if fill_amount.currency != self._amount.currency:
            raise ValueError("Fill amount currency must match trade amount currency")
            
        # Update filled amount
        self._filled_amount = self._filled_amount.add(fill_amount)
        
        # Update average fill price
        if self._average_fill_price is None:
            self._average_fill_price = fill_price
        else:
            # Calculate weighted average
            total_value = (self._filled_amount.subtract(fill_amount).amount * self._average_fill_price.amount) + \
                          (fill_amount.amount * fill_price.amount)
            avg_price = total_value / self._filled_amount.amount
            self._average_fill_price = Money(avg_price, fill_price.currency)
        
        # Update status
        if self._filled_amount.amount >= self._amount.amount:
            self._status = TradeStatus.FILLED
        else:
            self._status = TradeStatus.PARTIALLY_FILLED
            
        self._add_domain_event("TradePartiallyFilled", {
            "trade_id": self._trade_id,
            "user_id": self._user_id,
            "fill_amount": float(fill_amount.amount),
            "fill_price": float(fill_price.amount),
            "total_filled": float(self._filled_amount.amount),
            "average_fill_price": float(self._average_fill_price.amount),
            "status": self._status.value,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    def close(self, exit_price: Money) -> Money:
        """Close the trade and calculate final P&L."""
        if self._status != TradeStatus.ACTIVE:
            raise ValueError(f"Cannot close trade with status {self._status}")
        
        if not self._entry_price:
            raise ValueError("Cannot close trade without entry price")
        
        self._exit_price = exit_price
        self._status = TradeStatus.COMPLETED
        self._closed_at = datetime.now(timezone.utc)
        
        pnl = self.calculate_pnl(exit_price)
        
        self._add_domain_event("TradeClosed", {
            "trade_id": self._trade_id,
            "user_id": self._user_id,
            "pnl": float(pnl.amount),
            "closed_at": self._closed_at.isoformat()
        })
        
        return pnl
    
    def fail(self, error_message: str) -> None:
        """Mark trade as failed with error message."""
        self._status = TradeStatus.FAILED
        self._error_message = error_message
        self._closed_at = datetime.now(timezone.utc)
        
        self._add_domain_event("TradeFailed", {
            "trade_id": self._trade_id,
            "user_id": self._user_id,
            "error": error_message,
            "failed_at": self._closed_at.isoformat()
        })
    
    def calculate_pnl(self, current_price: Money) -> Money:
        """Calculate current profit/loss for the trade."""
        if not self._entry_price:
            return Money(Decimal('0'), self._amount.currency)
        
        price_diff = current_price.amount - self._entry_price.amount
        
        # For short positions, invert the P&L calculation
        if self._direction == TradeDirection.SHORT:
            price_diff = -price_diff
        
        # P&L = position_size * price_difference 
        pnl_amount = self._amount.amount * price_diff / self._entry_price.amount
        
        return Money(pnl_amount, self._amount.currency)
    
    def calculate_pnl_percentage(self, current_price: Money) -> Decimal:
        """Calculate P&L as percentage of initial investment."""
        if not self._entry_price:
            return Decimal('0')
        
        pnl = self.calculate_pnl(current_price)
        return (pnl.amount / self._amount.amount) * Decimal('100')
    
    def is_profitable(self, current_price: Money) -> bool:
        """Check if trade is currently profitable."""
        return self.calculate_pnl(current_price).amount > Decimal('0')
    
    def _validate_user_id(self, user_id: int) -> int:
        if user_id <= 0:
            raise ValueError("User ID must be positive")
        return user_id
    
    def _validate_amount(self, amount: Money) -> Money:
        if amount.amount <= Decimal('0'):
            raise ValueError("Trade amount must be positive")
        return amount
    
    def _add_domain_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Add domain event for eventual publication through outbox."""
        # Instead of storing events in memory, we'll mark that events need to be created
        # The actual event creation will happen in the service layer with outbox pattern
        event_info = {
            "event_type": event_type,
            "event_data": event_data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Store in a way that can be picked up by the service layer
        if not hasattr(self, '_pending_events'):
            self._pending_events = []
        self._pending_events.append(event_info)
    
    def get_pending_events(self) -> List[Dict[str, Any]]:
        """Get pending events and clear the list."""
        events = getattr(self, '_pending_events', []).copy()
        if hasattr(self, '_pending_events'):
            self._pending_events.clear()
        return events


class Position:
    """
    Position entity representing holdings in a specific asset.
    
    Aggregates multiple trades for the same asset and provides
    real-time P&L calculation and risk metrics.
    
    Invariants:
    - Asset is immutable once set
    - Quantity reflects net position across all trades
    - Average entry price is weighted by trade sizes
    - Unrealized P&L is calculated using current market price
    """
    
    def __init__(self, asset: Asset, trades: Optional[List[Trade]] = None):
        self._asset = asset
        self._trades: List[Trade] = trades or []
        
        # Calculated properties
        self._quantity = self._calculate_net_quantity()
        self._average_entry_price = self._calculate_average_entry_price()
        self._total_invested = self._calculate_total_invested()
        
    @property
    def asset(self) -> Asset:
        return self._asset
    
    @property
    def quantity(self) -> Decimal:
        return self._quantity
    
    @property
    def average_entry_price(self) -> Optional[Money]:
        return self._average_entry_price
    
    @property
    def total_invested(self) -> Money:
        return self._total_invested
    
    @property
    def trades(self) -> List[Trade]:
        return self._trades.copy()
    
    def add_trade(self, trade: Trade) -> None:
        """Add a trade to this position."""
        if trade.asset != self._asset:
            raise ValueError(f"Trade asset {trade.asset.symbol} doesn't match position asset {self._asset.symbol}")
        
        self._trades.append(trade)
        self._recalculate()
    
    def calculate_unrealized_pnl(self, current_price: Money) -> Money:
        """Calculate unrealized P&L based on current market price."""
        if not self._average_entry_price or self._quantity == Decimal('0'):
            return Money(Decimal('0'), current_price.currency)
        
        price_diff = current_price.amount - self._average_entry_price.amount
        unrealized_pnl = self._quantity * price_diff
        
        return Money(unrealized_pnl, current_price.currency)
    
    def calculate_realized_pnl(self) -> Money:
        """Calculate realized P&L from closed trades."""
        if not self._trades:
            return Money(Decimal('0'), 'USD')  # Default currency
        
        total_realized = Decimal('0')
        currency = self._trades[0].amount.currency
        
        for trade in self._trades:
            if trade.status == TradeStatus.COMPLETED and trade.exit_price:
                pnl = trade.calculate_pnl(trade.exit_price)
                total_realized += pnl.amount
        
        return Money(total_realized, currency)
    
    def calculate_total_pnl(self, current_price: Money) -> Money:
        """Calculate total P&L (realized + unrealized)."""
        realized = self.calculate_realized_pnl()
        unrealized = self.calculate_unrealized_pnl(current_price)
        
        total_amount = realized.amount + unrealized.amount
        return Money(total_amount, current_price.currency)
    
    def is_long(self) -> bool:
        """Check if this is a long position."""
        return self._quantity > Decimal('0')
    
    def is_short(self) -> bool:
        """Check if this is a short position."""
        return self._quantity < Decimal('0')
    
    def is_flat(self) -> bool:
        """Check if position is flat (no quantity)."""
        return self._quantity == Decimal('0')
    
    def _calculate_net_quantity(self) -> Decimal:
        """Calculate net quantity across all trades."""
        net_quantity = Decimal('0')
        
        for trade in self._trades:
            if trade.status in [TradeStatus.ACTIVE, TradeStatus.FILLED, TradeStatus.COMPLETED]:
                quantity_delta = trade.amount.amount / (trade.entry_price.amount if trade.entry_price else Decimal('1'))
                
                if trade.direction == TradeDirection.LONG:
                    net_quantity += quantity_delta
                else:  # SHORT
                    net_quantity -= quantity_delta
        
        return net_quantity
    
    def _calculate_average_entry_price(self) -> Optional[Money]:
        """Calculate weighted average entry price."""
        if not self._trades or self._quantity == Decimal('0'):
            return None
        
        total_value = Decimal('0')
        total_quantity = Decimal('0')
        currency = None
        
        for trade in self._trades:
            if trade.status in [TradeStatus.ACTIVE, TradeStatus.FILLED, TradeStatus.COMPLETED] and trade.entry_price:
                # Use filled amount for partially filled trades, full amount for others
                amount = trade._filled_amount if trade.status == TradeStatus.PARTIALLY_FILLED else trade.amount
                quantity = amount.amount / trade.entry_price.amount
                value = quantity * trade.entry_price.amount
                
                total_value += value
                total_quantity += quantity
                currency = trade.entry_price.currency
        
        if total_quantity == Decimal('0') or not currency:
            return None
        
        avg_price = total_value / total_quantity
        return Money(avg_price, currency)
    
    def _calculate_total_invested(self) -> Money:
        """Calculate total amount invested in this position."""
        if not self._trades:
            return Money(Decimal('0'), 'USD')
        
        total_invested = Decimal('0')
        currency = self._trades[0].amount.currency
        
        for trade in self._trades:
            if trade.status in [TradeStatus.ACTIVE, TradeStatus.FILLED, TradeStatus.COMPLETED]:
                # Use filled amount for partially filled trades, full amount for others
                amount = trade._filled_amount if trade.status == TradeStatus.PARTIALLY_FILLED else trade.amount
                total_invested += amount.amount
        
        return Money(total_invested, currency)
    
    def _recalculate(self) -> None:
        """Recalculate all derived values."""
        self._quantity = self._calculate_net_quantity()
        self._average_entry_price = self._calculate_average_entry_price()
        self._total_invested = self._calculate_total_invested()


class Portfolio:
    """
    Portfolio entity representing a user's complete trading portfolio.
    
    Aggregates all positions and provides portfolio-level metrics including
    total value, available balance, total P&L, and risk assessment.
    
    Invariants:
    - User ID is immutable
    - Positions are keyed by asset symbol
    - Total value includes both positions and available cash
    - P&L calculations are real-time based on current prices
    """
    
    def __init__(self, user_id: int, available_balance: Money, positions: Optional[Dict[str, Position]] = None):
        self._user_id = self._validate_user_id(user_id)
        self._available_balance = available_balance
        self._positions: Dict[str, Position] = positions or {}
        self._last_updated = datetime.now(timezone.utc)
    
    @property
    def user_id(self) -> int:
        return self._user_id
    
    @property
    def available_balance(self) -> Money:
        return self._available_balance
    
    @property
    def positions(self) -> Dict[str, Position]:
        return self._positions.copy()
    
    @property
    def last_updated(self) -> datetime:
        return self._last_updated
    
    def add_position(self, position: Position) -> None:
        """Add a position to the portfolio."""
        self._positions[position.asset.symbol] = position
        self._last_updated = datetime.now(timezone.utc)
    
    def get_position(self, asset_symbol: str) -> Optional[Position]:
        """Get position for specific asset."""
        return self._positions.get(asset_symbol)
    
    def update_available_balance(self, new_balance: Money) -> None:
        """Update available cash balance."""
        if new_balance.amount < Decimal('0'):
            raise ValueError("Available balance cannot be negative")
        
        self._available_balance = new_balance
        self._last_updated = datetime.now(timezone.utc)
    
    def calculate_total_value(self, current_prices: Dict[str, Money]) -> Money:
        """Calculate total portfolio value including positions and cash."""
        total_value = self._available_balance.amount
        currency = self._available_balance.currency
        
        for symbol, position in self._positions.items():
            if symbol in current_prices and not position.is_flat():
                current_price = current_prices[symbol]
                position_value = position.calculate_total_pnl(current_price).amount + position.total_invested.amount
                total_value += position_value
        
        return Money(total_value, currency)
    
    def calculate_total_pnl(self, current_prices: Dict[str, Money]) -> Money:
        """Calculate total profit/loss across all positions."""
        total_pnl = Decimal('0')
        currency = self._available_balance.currency
        
        for symbol, position in self._positions.items():
            if symbol in current_prices:
                current_price = current_prices[symbol]
                position_pnl = position.calculate_total_pnl(current_price)
                total_pnl += position_pnl.amount
        
        return Money(total_pnl, currency)
    
    def calculate_unrealized_pnl(self, current_prices: Dict[str, Money]) -> Money:
        """Calculate total unrealized P&L across all positions."""
        total_unrealized = Decimal('0')
        currency = self._available_balance.currency
        
        for symbol, position in self._positions.items():
            if symbol in current_prices:
                current_price = current_prices[symbol]
                position_unrealized = position.calculate_unrealized_pnl(current_price)
                total_unrealized += position_unrealized.amount
        
        return Money(total_unrealized, currency)
    
    def calculate_portfolio_risk(self, current_prices: Dict[str, Money]) -> Dict[str, Any]:
        """Calculate portfolio risk metrics."""
        total_value = self.calculate_total_value(current_prices)
        
        if total_value.amount == Decimal('0'):
            return {
                "total_exposure": Decimal('0'),
                "largest_position_pct": Decimal('0'),
                "number_of_positions": 0,
                "cash_percentage": Decimal('100')
            }
        
        largest_position = Decimal('0')
        total_position_value = Decimal('0')
        active_positions = 0
        
        for symbol, position in self._positions.items():
            if not position.is_flat() and symbol in current_prices:
                current_price = current_prices[symbol]
                position_value = abs(position.quantity) * current_price.amount
                total_position_value += position_value
                
                position_pct = (position_value / total_value.amount) * Decimal('100')
                largest_position = max(largest_position, position_pct)
                active_positions += 1
        
        cash_percentage = (self._available_balance.amount / total_value.amount) * Decimal('100')
        
        return {
            "total_exposure": (total_position_value / total_value.amount) * Decimal('100'),
            "largest_position_pct": largest_position,
            "number_of_positions": active_positions,
            "cash_percentage": cash_percentage
        }
    
    def get_active_positions(self) -> List[Position]:
        """Get all positions with non-zero quantity."""
        return [pos for pos in self._positions.values() if not pos.is_flat()]
    
    def _validate_user_id(self, user_id: int) -> int:
        if user_id <= 0:
            raise ValueError("User ID must be positive")
        return user_id