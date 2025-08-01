"""
Domain Event System

Abstract base classes and interfaces for the domain event system.
Enables loose coupling between domains through event-driven architecture.

As defined in ADR-002, this prepares for Phase 2 event-driven extensions
while providing the foundation for domain event handling in Phase 1.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Any, Dict, List, Protocol
from uuid import uuid4


@dataclass
class DomainEvent(ABC):
    """
    Base class for all domain events.
    
    Domain events represent something important that happened in the domain
    and enable loose coupling between bounded contexts.
    """
    event_id: str = field(default_factory=lambda: str(uuid4()))
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    event_version: int = field(default=1)
    
    @property
    @abstractmethod
    def event_type(self) -> str:
        """Return the event type identifier."""
        pass


class EventBus(Protocol):
    """
    Event bus interface for publishing and subscribing to domain events.
    
    This interface will be implemented in the infrastructure layer with
    the actual event bus technology (Redis Streams, NATS, etc.)
    """
    
    async def emit(self, event: DomainEvent) -> None:
        """Emit a domain event to all subscribers."""
        ...
    
    async def subscribe(self, event_type: str, handler: callable) -> None:
        """Subscribe to a specific event type."""
        ...
    
    async def unsubscribe(self, event_type: str, handler: callable) -> None:
        """Unsubscribe from a specific event type."""
        ...


class EventHandler(Protocol):
    """Interface for domain event handlers."""
    
    async def handle(self, event: DomainEvent) -> None:
        """Handle a domain event."""
        ...


@dataclass
class EventStore:
    """
    Simple in-memory event store for Phase 1.
    
    This will be replaced with a proper event store implementation
    in Phase 2 for event sourcing and audit trails.
    """
    _events: List[DomainEvent] = field(default_factory=list)
    
    def append(self, event: DomainEvent) -> None:
        """Append an event to the store."""
        self._events.append(event)
    
    def get_events(self, event_type: str = None) -> List[DomainEvent]:
        """Get events, optionally filtered by type."""
        if event_type:
            return [e for e in self._events if e.event_type == event_type]
        return self._events.copy()
    
    def get_events_for_aggregate(self, aggregate_id: str) -> List[DomainEvent]:
        """Get events for a specific aggregate (if event has aggregate_id)."""
        return [
            e for e in self._events 
            if hasattr(e, 'aggregate_id') and e.aggregate_id == aggregate_id
        ]