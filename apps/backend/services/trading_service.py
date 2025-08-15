from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from uuid import uuid4

from domains.trading.entities import Trade
from domains.trading.value_objects import TradeStatus, TradeDirection, Asset, Money
from domains.shared.events import DomainEvent
from services.outbox_service import OutboxService
from models.event_outbox import EventOutbox, OutboxStatus

class TradeExecutedEvent(DomainEvent):
    """Event emitted when a trade is executed"""
    
    def __init__(self, trade_id: str, user_id: int, asset: str, direction: str, 
                 amount: float, entry_price: float, executed_at: str):
        super().__init__(
            event_id=str(uuid4()),
            event_type="TradeExecuted",
            domain="trading",
            entity_id=trade_id,
            data={
                "trade_id": trade_id,
                "user_id": user_id,
                "asset": asset,
                "direction": direction,
                "amount": amount,
                "entry_price": entry_price,
                "executed_at": executed_at
            }
        )

class TradingService:
    """Service for managing trading operations with outbox pattern"""
    
    def __init__(self, outbox_service: OutboxService):
        self.outbox_service = outbox_service
        
    async def execute_trade(self, trade: Trade, entry_price: Money, exchange_order_id: str) -> None:
        """Execute a trade and publish events through outbox"""
        try:
            # Execute the trade
            trade.execute(entry_price, exchange_order_id)
            
            # Get pending events from trade
            pending_events = trade.get_pending_events()
            
            # Add events to outbox
            for event_info in pending_events:
                if event_info["event_type"] == "TradeExecuted":
                    event_data = event_info["event_data"]
                    event = TradeExecutedEvent(
                        trade_id=event_data["trade_id"],
                        user_id=event_data["user_id"],
                        asset=event_data["asset"],
                        direction=event_data["direction"],
                        amount=event_data["amount"],
                        entry_price=event_data["entry_price"],
                        executed_at=event_data["executed_at"]
                    )
                    await self.outbox_service.add_event(event)
                    
        except Exception as e:
            # Handle trade execution failure
            trade.fail(str(e))
            # Add failure event to outbox
            pending_events = trade.get_pending_events()
            for event_info in pending_events:
                if event_info["event_type"] == "TradeFailed":
                    # Implementation for TradeFailedEvent would go here
                    pass
            raise