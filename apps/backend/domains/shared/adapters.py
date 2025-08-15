"""
Domain Event Adapters

Adapter patterns for migrating existing domain events to enhanced schema.
Maintains backward compatibility while enabling Redis Streams integration.
"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional, Union
from uuid import uuid4
import os
import json

from .events import DomainEvent as EnhancedDomainEvent
from .validation import validate_event_schema, EventValidationError


class DomainEventAdapter:
    """
    Base adapter for converting legacy domain events to enhanced schema.
    
    Preserves existing domain implementations while adding Redis Streams compatibility.
    """
    
    @staticmethod
    def create_enhanced_event(
        event_type: str,
        domain: str, 
        entity_id: str,
        data: Dict[str, Any] = None,
        correlation_id: Optional[str] = None,
        causation_id: Optional[str] = None,
        occurred_at: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Create enhanced event structure from basic parameters.
        
        Used by domains to generate Redis Streams compatible events.
        """
        if occurred_at is None:
            occurred_at = datetime.now(timezone.utc)
        
        # Ensure event_type follows Domain.EventName format
        if '.' not in event_type:
            event_type = f"{domain.title()}.{event_type}"
        
        enhanced_event = {
            "event_id": str(uuid4()),
            "event_type": event_type,
            "domain": domain.lower(),
            "entity_id": str(entity_id),
            "occurred_at": occurred_at.isoformat(),
            "event_version": 1,
            "correlation_id": correlation_id or "",
            "causation_id": causation_id or "",
            "producer": f"astra-backend@{os.getenv('APP_VERSION', '1.0.0')}",
            "data": json.dumps(data) if data else ""
        }
        
        # Validate the created event
        try:
            validate_event_schema(enhanced_event)
            return enhanced_event
        except EventValidationError as e:
            # Log validation error but return event anyway for compatibility
            print(f"Warning: Event validation failed for {event_type}: {e}")
            return enhanced_event


class GamificationEventAdapter(DomainEventAdapter):
    """
    Adapter for Gamification domain's separate DomainEvent class.
    
    Converts the existing gamification/events.py DomainEvent format
    to the enhanced shared schema while preserving functionality.
    """
    
    @staticmethod 
    def adapt_legacy_event(legacy_event) -> Dict[str, Any]:
        """
        Convert Gamification domain's DomainEvent to enhanced schema.
        
        Args:
            legacy_event: Instance of gamification.events.DomainEvent
            
        Returns:
            Dict[str, Any]: Enhanced event structure for Redis Streams
        """
        # Extract data from legacy event
        event_type = getattr(legacy_event, 'event_type', 'UnknownEvent')
        entity_id = getattr(legacy_event, 'entity_id', '')
        data = getattr(legacy_event, 'data', {})
        occurred_at = getattr(legacy_event, 'occurred_at', None)
        
        if occurred_at is None:
            occurred_at = datetime.now(timezone.utc)
        elif hasattr(occurred_at, 'replace'):
            # Ensure timezone aware
            if occurred_at.tzinfo is None:
                occurred_at = occurred_at.replace(tzinfo=timezone.utc)
        
        return GamificationEventAdapter.create_enhanced_event(
            event_type=event_type,
            domain="gamification",
            entity_id=entity_id,
            data=data,
            occurred_at=occurred_at
        )
    
    @staticmethod
    def create_gamification_event(
        event_type: str,
        entity_id: str,
        data: Dict[str, Any] = None,
        correlation_id: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create enhanced gamification event with domain-specific optimizations.
        
        Common gamification events:
        - XPGained, LevelUp, AchievementUnlocked, StreakUpdated
        """
        # Add user_id to entity_id if provided for better event routing
        if user_id is not None and not entity_id:
            entity_id = f"user_{user_id}"
        
        # Add common gamification context to data
        enhanced_data = data or {}
        if user_id is not None:
            enhanced_data['user_id'] = user_id
        
        return GamificationEventAdapter.create_enhanced_event(
            event_type=event_type,
            domain="gamification", 
            entity_id=entity_id,
            data=enhanced_data,
            correlation_id=correlation_id
        )


class SimpleEventAdapter(DomainEventAdapter):
    """
    Adapter for domains using the _emit_event() pattern.
    
    Used by Financial, NFT, and User domains that emit events
    with simple event_type and data parameters.
    """
    
    @staticmethod
    def adapt_simple_event(
        event_type: str,
        entity_id: str, 
        data: Dict[str, Any],
        domain: str,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Adapt domains that use _emit_event(event_type, data) pattern.
        
        Preserves the simple event emission pattern while adding
        enhanced fields for Redis Streams integration.
        """
        return SimpleEventAdapter.create_enhanced_event(
            event_type=event_type,
            domain=domain,
            entity_id=entity_id,
            data=data,
            correlation_id=correlation_id
        )


class TradingEventAdapter(DomainEventAdapter):
    """
    Adapter for Trading domain's enhanced DomainEvent classes.
    
    Trading domain already uses enhanced events but may need
    field mapping for Redis Streams compatibility.
    """
    
    @staticmethod
    def adapt_trading_event(trading_event: EnhancedDomainEvent) -> Dict[str, Any]:
        """
        Convert Trading domain DomainEvent to Redis Streams format.
        
        Trading events already follow enhanced schema, so mainly
        need serialization and stream name generation.
        """
        return {
            "event_id": trading_event.event_id,
            "event_type": trading_event.event_type,
            "domain": "trading",
            "entity_id": getattr(trading_event, 'trade_id', trading_event.entity_id),
            "occurred_at": trading_event.occurred_at.isoformat(),
            "event_version": trading_event.event_version,
            "correlation_id": getattr(trading_event, 'correlation_id', ''),
            "causation_id": getattr(trading_event, 'causation_id', ''),
            "producer": trading_event.producer,
            "data": json.dumps(trading_event.data) if trading_event.data else ""
        }


class SocialEventAdapter(DomainEventAdapter):
    """
    Adapter for Social domain's DomainEvent classes.
    
    Social domain already uses shared DomainEvent base class,
    so mainly needs Redis Streams serialization.
    """
    
    @staticmethod
    def adapt_social_event(social_event: EnhancedDomainEvent) -> Dict[str, Any]:
        """Convert Social domain DomainEvent to Redis Streams format."""
        return {
            "event_id": social_event.event_id,
            "event_type": social_event.event_type,
            "domain": "social",
            "entity_id": social_event.entity_id,
            "occurred_at": social_event.occurred_at.isoformat(),
            "event_version": social_event.event_version,
            "correlation_id": getattr(social_event, 'correlation_id', ''),
            "causation_id": getattr(social_event, 'causation_id', ''),
            "producer": social_event.producer,
            "data": json.dumps(social_event.data) if social_event.data else ""
        }


# Adapter Registry for domain-specific routing
class AdapterRegistry:
    """
    Registry mapping domains to their appropriate adapters.
    
    Enables automatic adapter selection based on domain name.
    """
    
    ADAPTERS = {
        'trading': TradingEventAdapter,
        'gamification': GamificationEventAdapter,
        'social': SocialEventAdapter,
        'user': SimpleEventAdapter,
        'financial': SimpleEventAdapter,
        'nft': SimpleEventAdapter
    }
    
    @classmethod
    def get_adapter(cls, domain: str):
        """Get appropriate adapter for domain."""
        return cls.ADAPTERS.get(domain.lower(), SimpleEventAdapter)
    
    @classmethod
    def adapt_event_for_streams(cls, domain: str, event_data: Union[Dict, Any]) -> Dict[str, Any]:
        """
        Automatically adapt any domain event for Redis Streams.
        
        Args:
            domain: Domain name (trading, gamification, etc.)
            event_data: Event data in any format
            
        Returns:
            Dict[str, Any]: Redis Streams compatible event
        """
        adapter = cls.get_adapter(domain)
        
        # Handle different event formats
        if isinstance(event_data, dict):
            # Already in dict format, validate and enhance
            if 'event_type' in event_data:
                return adapter.create_enhanced_event(
                    event_type=event_data['event_type'],
                    domain=domain,
                    entity_id=event_data.get('entity_id', ''),
                    data=event_data.get('data', {}),
                    correlation_id=event_data.get('correlation_id')
                )
        
        # Handle domain-specific event objects
        if domain == 'gamification':
            return GamificationEventAdapter.adapt_legacy_event(event_data)
        elif domain == 'trading' and hasattr(event_data, 'event_type'):
            return TradingEventAdapter.adapt_trading_event(event_data)
        elif domain == 'social' and hasattr(event_data, 'event_type'):
            return SocialEventAdapter.adapt_social_event(event_data)
        
        # Fallback to simple adapter
        return SimpleEventAdapter.create_enhanced_event(
            event_type="UnknownEvent",
            domain=domain,
            entity_id="unknown",
            data={"raw_event": str(event_data)}
        )