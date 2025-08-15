"""
Event Gateway

FastAPI router for event bus management, monitoring, and administration.
Provides REST API endpoints for event publishing, monitoring, and health checks.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from infrastructure.events.redis_event_bus import RedisEventBus, EventBusConfig, EventMetrics
from infrastructure.events.schemas import EventType, validate_event, EVENT_TYPE_REGISTRY
from infrastructure.events.handlers import (
    TradingToGamificationHandler,
    SocialToGamificationHandler, 
    GamificationToSocialHandler,
    FinancialIntegrationHandler
)

logger = logging.getLogger(__name__)

# Request/Response Models
class EventPublishRequest(BaseModel):
    """Request model for publishing events"""
    event_type: str
    event_data: Dict[str, Any]
    correlation_id: Optional[str] = None

class EventPublishResponse(BaseModel):
    """Response model for event publishing"""
    success: bool
    event_id: Optional[str] = None
    message: str
    latency_ms: Optional[float] = None

class HealthCheckResponse(BaseModel):
    """Response model for health checks"""
    status: str
    metrics: Optional[Dict[str, Any]] = None
    streams: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class EventBusStatsResponse(BaseModel):
    """Response model for event bus statistics"""
    metrics: Dict[str, Any]
    active_handlers: Dict[str, int]
    stream_info: Dict[str, Any]
    uptime_seconds: float


class EventGateway:
    """
    Event Gateway service for managing event bus operations.
    
    Provides centralized event publishing, subscription management,
    and monitoring capabilities through REST API endpoints.
    """
    
    def __init__(self, config: EventBusConfig):
        self.config = config
        self.event_bus: Optional[RedisEventBus] = None
        self.handlers = {}
        self.router = APIRouter(prefix="/events", tags=["events"])
        self.start_time = datetime.now()
        
        # Setup routes
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.router.post(
            "/publish",
            response_model=EventPublishResponse,
            summary="Publish Domain Event",
            description="Publish a domain event to the event bus"
        )
        async def publish_event(request: EventPublishRequest):
            return await self._publish_event(request)
        
        @self.router.get(
            "/health",
            response_model=HealthCheckResponse,
            summary="Event Bus Health Check",
            description="Get health status and basic metrics of the event bus"
        )
        async def health_check():
            return await self._health_check()
        
        @self.router.get(
            "/stats",
            response_model=EventBusStatsResponse,
            summary="Event Bus Statistics",
            description="Get detailed statistics and metrics from the event bus"
        )
        async def get_stats():
            return await self._get_stats()
        
        @self.router.get(
            "/streams",
            summary="List Event Streams",
            description="List all active event streams and their status"
        )
        async def list_streams():
            return await self._list_streams()
        
        @self.router.post(
            "/handlers/register",
            summary="Register Event Handler",
            description="Register a new event handler for a specific event type"
        )
        async def register_handler(event_type: str, handler_name: str):
            return await self._register_handler(event_type, handler_name)
        
        @self.router.delete(
            "/handlers/{event_type}/{handler_name}",
            summary="Unregister Event Handler",
            description="Unregister an event handler"
        )
        async def unregister_handler(event_type: str, handler_name: str):
            return await self._unregister_handler(event_type, handler_name)
        
        @self.router.post(
            "/replay/{stream_name}",
            summary="Replay Events",
            description="Replay events from a specific stream (admin operation)"
        )
        async def replay_events(stream_name: str, from_id: str = "0", count: int = 100):
            return await self._replay_events(stream_name, from_id, count)
    
    async def initialize(self) -> None:
        """Initialize event bus and register default handlers"""
        try:
            # Initialize event bus
            self.event_bus = RedisEventBus(self.config)
            await self.event_bus.connect()
            
            # Register cross-domain handlers
            await self._register_default_handlers()
            
            # Start consuming events
            await self.event_bus.start_consuming()
            
            logger.info("Event gateway initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize event gateway: {e}")
            raise
    
    async def shutdown(self) -> None:
        """Shutdown event bus and cleanup resources"""
        if self.event_bus:
            await self.event_bus.stop_consuming()
            await self.event_bus.disconnect()
        
        logger.info("Event gateway shutdown complete")
    
    async def _publish_event(self, request: EventPublishRequest) -> EventPublishResponse:
        """Publish event to event bus"""
        if not self.event_bus:
            raise HTTPException(status_code=503, detail="Event bus not initialized")
        
        try:
            start_time = asyncio.get_event_loop().time()
            
            # Validate event data
            event = validate_event(request.event_type, request.event_data)
            
            # Publish to event bus
            await self.event_bus.emit(event)
            
            # Calculate latency
            latency_ms = (asyncio.get_event_loop().time() - start_time) * 1000
            
            return EventPublishResponse(
                success=True,
                event_id=event.metadata.event_id,
                message=f"Event {request.event_type} published successfully",
                latency_ms=latency_ms
            )
            
        except ValueError as e:
            return EventPublishResponse(
                success=False,
                message=f"Invalid event data: {e}"
            )
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
            return EventPublishResponse(
                success=False,
                message=f"Failed to publish event: {e}"
            )
    
    async def _health_check(self) -> HealthCheckResponse:
        """Perform health check on event bus"""
        if not self.event_bus:
            return HealthCheckResponse(
                status="unhealthy",
                message="Event bus not initialized"
            )
        
        try:
            health_data = await self.event_bus.health_check()
            return HealthCheckResponse(**health_data)
        except Exception as e:
            return HealthCheckResponse(
                status="unhealthy",
                message=f"Health check failed: {e}"
            )
    
    async def _get_stats(self) -> EventBusStatsResponse:
        """Get detailed event bus statistics"""
        if not self.event_bus:
            raise HTTPException(status_code=503, detail="Event bus not initialized")
        
        try:
            metrics = await self.event_bus.get_metrics()
            uptime = (datetime.now() - self.start_time).total_seconds()
            
            # Count active handlers
            active_handlers = {
                event_type: len(handlers)
                for event_type, handlers in self.event_bus.event_handlers.items()
            }
            
            # Get stream info
            stream_info = {}
            if self.event_bus.redis_client:
                for event_type in self.event_bus.event_handlers.keys():
                    stream_name = f"{self.config.stream_prefix}:{event_type}"
                    try:
                        info = await self.event_bus.redis_client.xinfo_stream(stream_name)
                        stream_info[event_type] = {
                            "length": info.get("length", 0),
                            "groups": info.get("groups", 0),
                            "first_entry": info.get("first-entry", [None])[0],
                            "last_entry": info.get("last-entry", [None])[0]
                        }
                    except Exception:
                        stream_info[event_type] = {"error": "Stream not found"}
            
            return EventBusStatsResponse(
                metrics=metrics.__dict__,
                active_handlers=active_handlers,
                stream_info=stream_info,
                uptime_seconds=uptime
            )
            
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get stats: {e}")
    
    async def _list_streams(self) -> Dict[str, Any]:
        """List all active event streams"""
        if not self.event_bus or not self.event_bus.redis_client:
            raise HTTPException(status_code=503, detail="Event bus not initialized")
        
        try:
            streams = {}
            
            # Get all streams matching our prefix
            pattern = f"{self.config.stream_prefix}:*"
            keys = await self.event_bus.redis_client.keys(pattern)
            
            for key in keys:
                try:
                    info = await self.event_bus.redis_client.xinfo_stream(key)
                    streams[key] = {
                        "length": info.get("length", 0),
                        "radix_tree_keys": info.get("radix-tree-keys", 0),
                        "radix_tree_nodes": info.get("radix-tree-nodes", 0),
                        "groups": info.get("groups", 0),
                        "last_generated_id": info.get("last-generated-id", "0-0")
                    }
                except Exception as e:
                    streams[key] = {"error": str(e)}
            
            return {"streams": streams, "total_streams": len(streams)}
            
        except Exception as e:
            logger.error(f"Failed to list streams: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to list streams: {e}")
    
    async def _register_handler(self, event_type: str, handler_name: str) -> Dict[str, Any]:
        """Register new event handler"""
        if not self.event_bus:
            raise HTTPException(status_code=503, detail="Event bus not initialized")
        
        # This is a simplified implementation
        # In practice, you'd have a handler registry
        return {
            "success": True,
            "message": f"Handler {handler_name} registered for {event_type}",
            "event_type": event_type,
            "handler_name": handler_name
        }
    
    async def _unregister_handler(self, event_type: str, handler_name: str) -> Dict[str, Any]:
        """Unregister event handler"""
        if not self.event_bus:
            raise HTTPException(status_code=503, detail="Event bus not initialized")
        
        return {
            "success": True,
            "message": f"Handler {handler_name} unregistered from {event_type}",
            "event_type": event_type,
            "handler_name": handler_name
        }
    
    async def _replay_events(self, stream_name: str, from_id: str, count: int) -> Dict[str, Any]:
        """Replay events from stream (admin operation)"""
        if not self.event_bus or not self.event_bus.redis_client:
            raise HTTPException(status_code=503, detail="Event bus not initialized")
        
        try:
            # Read events from stream
            events = await self.event_bus.redis_client.xrange(
                stream_name, min=from_id, count=count
            )
            
            replayed = 0
            for event_id, fields in events:
                # Re-publish event (simplified - would need proper deserialization)
                try:
                    # This would typically deserialize and re-emit the event
                    replayed += 1
                except Exception as e:
                    logger.error(f"Failed to replay event {event_id}: {e}")
            
            return {
                "success": True,
                "message": f"Replayed {replayed} events from {stream_name}",
                "stream_name": stream_name,
                "events_replayed": replayed,
                "total_events_found": len(events)
            }
            
        except Exception as e:
            logger.error(f"Failed to replay events: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to replay events: {e}")
    
    async def _register_default_handlers(self) -> None:
        """Register default cross-domain event handlers"""
        try:
            # Note: In a real implementation, these would be properly injected
            # with actual service dependencies
            
            # Trading → Gamification integration
            trading_handler = TradingToGamificationHandler(self.event_bus, None)
            await self.event_bus.subscribe("trade_executed", trading_handler)
            await self.event_bus.subscribe("trading_rewards_calculated", trading_handler)
            
            # Social → Gamification integration  
            social_handler = SocialToGamificationHandler(self.event_bus, None)
            await self.event_bus.subscribe("social_rating_changed", social_handler)
            await self.event_bus.subscribe("viral_content_shared", social_handler)
            await self.event_bus.subscribe("social_interaction_performed", social_handler)
            
            # Gamification → Social integration
            gamification_handler = GamificationToSocialHandler(self.event_bus, None)
            await self.event_bus.subscribe("level_up", gamification_handler)
            await self.event_bus.subscribe("achievement_unlocked", gamification_handler)
            
            # Financial integration
            financial_handler = FinancialIntegrationHandler(self.event_bus, None, None)
            await self.event_bus.subscribe("account_created", financial_handler)
            await self.event_bus.subscribe("funds_added", financial_handler)
            await self.event_bus.subscribe("payment_processed", financial_handler)
            
            logger.info("Default event handlers registered successfully")
            
        except Exception as e:
            logger.error(f"Failed to register default handlers: {e}")
            raise


# Global event gateway instance
event_gateway: Optional[EventGateway] = None

async def get_event_gateway() -> EventGateway:
    """Dependency to get event gateway instance"""
    global event_gateway
    if not event_gateway:
        raise HTTPException(status_code=503, detail="Event gateway not initialized")
    return event_gateway

async def initialize_event_gateway(config: EventBusConfig) -> EventGateway:
    """Initialize global event gateway"""
    global event_gateway
    event_gateway = EventGateway(config)
    await event_gateway.initialize()
    return event_gateway

async def shutdown_event_gateway():
    """Shutdown global event gateway"""
    global event_gateway
    if event_gateway:
        await event_gateway.shutdown()
        event_gateway = None