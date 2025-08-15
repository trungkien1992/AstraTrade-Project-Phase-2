from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timezone
import asyncio
import logging

from models.event_outbox import EventOutbox, OutboxStatus
from infrastructure.events.redis_event_bus import RedisEventBus
from domains.shared.events import DomainEvent

logger = logging.getLogger(__name__)

class OutboxService:
    """Service for managing the transactional outbox pattern"""
    
    def __init__(self, db_session: Session, event_bus: RedisEventBus):
        self.db_session = db_session
        self.event_bus = event_bus
        
    async def add_event(self, event: DomainEvent, priority: int = 0) -> None:
        """Add event to outbox"""
        outbox_record = EventOutbox(
            aggregate_id=event.entity_id,
            event_type=event.event_type,
            payload=event.to_dict(),
            priority=priority,
            status=OutboxStatus.PENDING,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        self.db_session.add(outbox_record)
        self.db_session.commit()
        
    async def process_pending_events(self, batch_size: int = 100) -> int:
        """Process pending events from outbox"""
        # Get pending events ordered by priority and creation time
        pending_events = self.db_session.query(EventOutbox).filter(
            and_(
                EventOutbox.status == OutboxStatus.PENDING,
                EventOutbox.priority >= 0  # Only process positive priority events
            )
        ).order_by(
            EventOutbox.priority.desc(),
            EventOutbox.created_at.asc()
        ).limit(batch_size).all()
        
        processed_count = 0
        
        for outbox_record in pending_events:
            try:
                # Deserialize event (simplified)
                event_data = outbox_record.payload
                # In a real implementation, you'd properly deserialize based on event_type
                
                # Publish event
                # For now, we'll just log that we would publish
                logger.info(f"Publishing event {outbox_record.event_type} with ID {outbox_record.id}")
                
                # Update status to published
                outbox_record.status = OutboxStatus.PUBLISHED
                outbox_record.updated_at = datetime.now(timezone.utc)
                processed_count += 1
                
            except Exception as e:
                logger.error(f"Failed to process outbox event {outbox_record.id}: {e}")
                # Update status to failed after max retries
                outbox_record.status = OutboxStatus.FAILED
                outbox_record.updated_at = datetime.now(timezone.utc)
        
        self.db_session.commit()
        return processed_count
        
    async def start_processing_loop(self, interval_seconds: int = 5):
        """Start background processing loop"""
        while True:
            try:
                processed = await self.process_pending_events()
                if processed > 0:
                    logger.info(f"Processed {processed} outbox events")
            except Exception as e:
                logger.error(f"Error in outbox processing loop: {e}")
            
            await asyncio.sleep(interval_seconds)