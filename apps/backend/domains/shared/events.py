"""
Domain Event System

Enhanced event system for Redis Streams integration and microservices.
Enables loose coupling between domains through event-driven architecture.

As defined in ADR-002 and ADR-007, this supports the Infrastructure Bridge Strategy
with production-ready event handling, tracing, and cross-domain communication.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Any, Dict, List, Protocol, Optional
from uuid import uuid4
import os


@dataclass
class DomainEvent(ABC):
    """
    Enhanced base class for all domain events.
    
    Supports Redis Streams integration, distributed tracing, and microservices
    deployment while maintaining backward compatibility with existing domains.
    
    New fields for production readiness:
    - correlation_id: Links events across service boundaries
    - causation_id: Tracks event causation chains  
    - producer: Identifies the service that generated the event
    - domain: Domain name for event routing and filtering
    - entity_id: ID of the aggregate that generated the event
    """
    # Core event fields (existing - backward compatible)
    event_id: str = field(default_factory=lambda: str(uuid4()))
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    event_version: int = field(default=1)
    
    # New production fields for microservices and tracing
    correlation_id: Optional[str] = field(default=None)
    causation_id: Optional[str] = field(default=None)
    producer: str = field(default_factory=lambda: f"astra-backend@{os.getenv('APP_VERSION', '1.0.0')}")
    domain: str = field(default="unknown")
    entity_id: str = field(default="")
    
    # Idempotency support
    idempotency_key: Optional[str] = field(default=None)
    
    # Data payload for domain-specific information
    data: Dict[str, Any] = field(default_factory=dict)
    
    @property
    @abstractmethod
    def event_type(self) -> str:
        """Return the event type identifier in format 'Domain.EventName'."""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for Redis Streams serialization."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "domain": self.domain,
            "entity_id": self.entity_id,
            "occurred_at": self.occurred_at.isoformat(),
            "event_version": str(self.event_version),
            "correlation_id": self.correlation_id or "",
            "causation_id": self.causation_id or "",
            "producer": self.producer,
            "data": str(self.data) if self.data else ""
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DomainEvent':
        """Create event from Redis Streams data (for deserialization)."""
        # This will be implemented by concrete event classes
        raise NotImplementedError("Subclasses must implement from_dict")
    
    def get_stream_name(self) -> str:
        """Generate Redis Stream name following convention: astra.{domain}.{event}.v{version}"""
        event_name = self.event_type.split('.')[-1].lower()
        return f"astra.{self.domain.lower()}.{event_name}.v{self.event_version}"


class EventBus(Protocol):
    """
    Enhanced event bus interface for Redis Streams integration.
    
    Supports Redis Streams consumer groups, idempotency tracking,
    and production-ready event processing with correlation tracing.
    """
    
    async def emit(self, event: DomainEvent) -> None:
        """Emit a domain event to Redis Streams."""
        ...
    
    async def emit_with_correlation(self, event: DomainEvent, correlation_id: str, causation_id: Optional[str] = None) -> None:
        """Emit event with explicit correlation and causation tracking."""
        ...
    
    async def subscribe(self, stream_pattern: str, consumer_group: str, handler: callable) -> None:
        """Subscribe to Redis Streams with consumer group."""
        ...
    
    async def subscribe_to_domain(self, domain: str, consumer_group: str, handler: callable) -> None:
        """Subscribe to all events from a specific domain."""
        ...
    
    async def unsubscribe(self, stream_pattern: str, consumer_group: str) -> None:
        """Remove consumer group from Redis Streams."""
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


# Redis Streams Integration Support
class RedisStreamsEventBus:
    """
    Redis Streams implementation of EventBus interface.
    
    This will be implemented in the infrastructure layer with
    Redis client configuration and connection management.
    """
    pass


# Event Adapter for Legacy Events
class LegacyEventAdapter:
    """
    Adapter to convert legacy domain events to the new enhanced schema.
    
    Preserves existing domain implementations during migration to Redis Streams.
    """
    
    @staticmethod
    def adapt_simple_event(event_type: str, entity_id: str, data: Dict[str, Any], 
                          domain: str, correlation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Adapt simple event format to enhanced DomainEvent structure.
        
        Used for domains that emit events via _emit_event() method pattern.
        """
        return {
            "event_id": str(uuid4()),
            "event_type": f"{domain}.{event_type}",
            "domain": domain,
            "entity_id": entity_id,
            "occurred_at": datetime.now(timezone.utc).isoformat(),
            "event_version": 1,
            "correlation_id": correlation_id or "",
            "causation_id": "",
            "producer": f"astra-backend@{os.getenv('APP_VERSION', '1.0.0')}",
            "data": str(data) if data else ""
        }
    
    @staticmethod
    def adapt_gamification_event(legacy_event) -> Dict[str, Any]:
        """
        Adapt Gamification domain's separate DomainEvent class to enhanced schema.
        """
        return {
            "event_id": str(uuid4()),
            "event_type": f"Gamification.{legacy_event.event_type}",
            "domain": "gamification",
            "entity_id": legacy_event.entity_id,
            "occurred_at": legacy_event.occurred_at.isoformat() if hasattr(legacy_event, 'occurred_at') else datetime.now(timezone.utc).isoformat(),
            "event_version": 1,
            "correlation_id": "",
            "causation_id": "",
            "producer": f"astra-backend@{os.getenv('APP_VERSION', '1.0.0')}",
            "data": str(legacy_event.data) if hasattr(legacy_event, 'data') else ""
        }