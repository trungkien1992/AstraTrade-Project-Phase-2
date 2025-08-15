"""
Redis Streams Event Bus Implementation

Production-ready Redis Streams integration for the enhanced event system.
Supports consumer groups, idempotency, and distributed tracing.
"""

import asyncio
import json
import os
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Callable
from uuid import uuid4

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("Warning: redis library not available. Install with: pip install redis")


class RedisStreamsEventBus:
    """
    Redis Streams implementation of the EventBus protocol.
    
    Features:
    - Producer/Consumer pattern with consumer groups
    - Idempotency tracking with Redis Sorted Sets
    - Stream naming convention: astra.{domain}.{event}.v{version}
    - Correlation and causation tracking
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379", 
                 max_connections: int = 10):
        self.redis_url = redis_url
        self.max_connections = max_connections
        self._redis_pool = None
        self._consumers = {}  # Track active consumers
        
    async def _get_redis_client(self):
        """Get Redis client with connection pooling."""
        if not REDIS_AVAILABLE:
            raise RuntimeError("Redis library not available")
            
        if self._redis_pool is None:
            self._redis_pool = redis.ConnectionPool.from_url(
                self.redis_url,
                max_connections=self.max_connections,
                decode_responses=True
            )
        
        return redis.Redis(connection_pool=self._redis_pool)
    
    async def emit(self, event_dict: Dict[str, Any]) -> str:
        """
        Emit a domain event to Redis Streams.
        
        Args:
            event_dict: Enhanced event dictionary with all required fields
            
        Returns:
            str: Redis Stream message ID
        """
        client = await self._get_redis_client()
        
        # Generate stream name from event
        stream_name = self._get_stream_name(event_dict)
        
        # Ensure all values are strings (Redis requirement)
        stream_data = {k: str(v) for k, v in event_dict.items()}
        
        try:
            # Add to Redis Stream with automatic ID generation
            message_id = await client.xadd(stream_name, stream_data)
            
            # Track for idempotency (store event_id in sorted set with timestamp)
            idempotency_key = f"processed_events:{event_dict['domain']}"
            timestamp = datetime.now(timezone.utc).timestamp()
            await client.zadd(idempotency_key, {event_dict['event_id']: timestamp})
            
            # Set expiration on idempotency tracking (7 days)
            await client.expire(idempotency_key, 604800)
            
            return message_id
            
        except Exception as e:
            print(f"Error emitting event to Redis: {e}")
            raise
    
    async def emit_with_correlation(self, event_dict: Dict[str, Any], 
                                  correlation_id: str, 
                                  causation_id: Optional[str] = None) -> str:
        """
        Emit event with explicit correlation and causation tracking.
        
        Updates event dictionary with correlation metadata before emission.
        """
        event_dict['correlation_id'] = correlation_id
        if causation_id:
            event_dict['causation_id'] = causation_id
        
        return await self.emit(event_dict)
    
    async def subscribe(self, stream_pattern: str, consumer_group: str, 
                       handler: Callable, consumer_name: str = None) -> None:
        """
        Subscribe to Redis Streams with consumer group.
        
        Args:
            stream_pattern: Stream name or pattern (e.g., "astra.trading.*")
            consumer_group: Consumer group name
            handler: Async function to handle events
            consumer_name: Optional consumer name (auto-generated if None)
        """
        if consumer_name is None:
            consumer_name = f"consumer_{uuid4().hex[:8]}"
        
        client = await self._get_redis_client()
        
        # Create consumer group if it doesn't exist
        try:
            await client.xgroup_create(stream_pattern, consumer_group, 
                                     id='0', mkstream=True)
        except redis.ResponseError as e:
            if "BUSYGROUP" not in str(e):
                raise
        
        # Start consumer loop
        consumer_key = f"{stream_pattern}:{consumer_group}:{consumer_name}"
        self._consumers[consumer_key] = {
            'stream': stream_pattern,
            'group': consumer_group,
            'name': consumer_name,
            'handler': handler,
            'active': True
        }
        
        # Launch consumer in background
        asyncio.create_task(self._consume_loop(client, stream_pattern, 
                                             consumer_group, consumer_name, handler))
    
    async def subscribe_to_domain(self, domain: str, consumer_group: str, 
                                handler: Callable) -> None:
        """Subscribe to all events from a specific domain."""
        stream_pattern = f"astra.{domain.lower()}.*"
        await self.subscribe(stream_pattern, consumer_group, handler)
    
    async def _consume_loop(self, client, stream_pattern: str, 
                          consumer_group: str, consumer_name: str, 
                          handler: Callable) -> None:
        """
        Main consumer loop for processing Redis Streams messages.
        
        Handles message acknowledgment and error recovery.
        """
        while True:
            try:
                # Read messages from consumer group
                messages = await client.xreadgroup(
                    consumer_group, 
                    consumer_name,
                    {stream_pattern: '>'},
                    count=10,
                    block=1000  # Block for 1 second
                )
                
                for stream, msgs in messages:
                    for msg_id, fields in msgs:
                        try:
                            # Check idempotency
                            if await self._is_processed(client, fields):
                                await client.xack(stream, consumer_group, msg_id)
                                continue
                            
                            # Convert fields back to proper event structure
                            event_data = self._deserialize_event(fields)
                            
                            # Call handler
                            await handler(event_data)
                            
                            # Acknowledge successful processing
                            await client.xack(stream, consumer_group, msg_id)
                            
                            # Mark as processed for idempotency
                            await self._mark_processed(client, fields)
                            
                        except Exception as e:
                            print(f"Error processing message {msg_id}: {e}")
                            # Don't ack on error - message will be retried
            
            except Exception as e:
                print(f"Consumer loop error: {e}")
                await asyncio.sleep(5)  # Back off on errors
    
    async def _is_processed(self, client, fields: Dict[str, str]) -> bool:
        """Check if event was already processed (idempotency)."""
        event_id = fields.get('event_id')
        domain = fields.get('domain')
        
        if not event_id or not domain:
            return False
        
        idempotency_key = f"processed_events:{domain}"
        score = await client.zscore(idempotency_key, event_id)
        return score is not None
    
    async def _mark_processed(self, client, fields: Dict[str, str]) -> None:
        """Mark event as processed for idempotency tracking."""
        event_id = fields.get('event_id')
        domain = fields.get('domain')
        
        if event_id and domain:
            idempotency_key = f"processed_events:{domain}"
            timestamp = datetime.now(timezone.utc).timestamp()
            await client.zadd(idempotency_key, {event_id: timestamp})
    
    def _get_stream_name(self, event_dict: Dict[str, Any]) -> str:
        """Generate Redis Stream name from event data."""
        domain = event_dict.get('domain', 'unknown').lower()
        event_type = event_dict.get('event_type', 'Unknown.Event')
        event_name = event_type.split('.')[-1].lower()
        version = event_dict.get('event_version', 1)
        
        return f"astra.{domain}.{event_name}.v{version}"
    
    def _deserialize_event(self, fields: Dict[str, str]) -> Dict[str, Any]:
        """Convert Redis Stream fields back to event structure."""
        event_data = dict(fields)
        
        # Convert string fields back to appropriate types
        if 'event_version' in event_data:
            event_data['event_version'] = int(event_data['event_version'])
        
        # Parse data field as JSON if present
        if 'data' in event_data and event_data['data']:
            try:
                event_data['data'] = json.loads(event_data['data'])
            except json.JSONDecodeError:
                # Keep as string if not valid JSON
                pass
        
        return event_data
    
    async def unsubscribe(self, stream_pattern: str, consumer_group: str) -> None:
        """Remove consumer group from Redis Streams."""
        client = await self._get_redis_client()
        
        # Remove consumer group
        try:
            await client.xgroup_destroy(stream_pattern, consumer_group)
        except redis.ResponseError:
            pass  # Group might not exist
        
        # Stop consumer loops
        for key, consumer in list(self._consumers.items()):
            if (consumer['stream'] == stream_pattern and 
                consumer['group'] == consumer_group):
                consumer['active'] = False
                del self._consumers[key]
    
    async def close(self):
        """Close Redis connections and cleanup resources."""
        if self._redis_pool:
            await self._redis_pool.disconnect()
        
        # Stop all consumers
        for consumer in self._consumers.values():
            consumer['active'] = False
        
        self._consumers.clear()


# Utility functions for creating Redis-compatible events
def create_redis_event(event_type: str, domain: str, entity_id: str,
                      data: Dict[str, Any] = None, 
                      correlation_id: str = None,
                      causation_id: str = None) -> Dict[str, Any]:
    """
    Create Redis Streams compatible event dictionary.
    
    Convenience function for creating events that can be sent to Redis.
    """
    if '.' not in event_type:
        event_type = f"{domain.title()}.{event_type}"
    
    return {
        "event_id": str(uuid4()),
        "event_type": event_type,
        "domain": domain.lower(),
        "entity_id": str(entity_id),
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "event_version": 1,
        "correlation_id": correlation_id or "",
        "causation_id": causation_id or "",
        "producer": f"astra-backend@{os.getenv('APP_VERSION', '1.0.0')}",
        "data": json.dumps(data) if data else ""
    }


# Example usage and testing
async def test_redis_streams():
    """Test Redis Streams event bus functionality."""
    if not REDIS_AVAILABLE:
        print("❌ Redis not available for testing")
        return
    
    print("🚀 Testing Redis Streams Event Bus")
    
    # Create event bus
    event_bus = RedisStreamsEventBus()
    
    # Create test event
    test_event = create_redis_event(
        event_type="TestEvent",
        domain="testing",
        entity_id="test_123",
        data={"message": "Hello Redis Streams!"},
        correlation_id="test_correlation"
    )
    
    try:
        # Emit event
        message_id = await event_bus.emit(test_event)
        print(f"✅ Event emitted with ID: {message_id}")
        
        # Test handler
        async def test_handler(event_data):
            print(f"📨 Received event: {event_data['event_type']}")
            print(f"   Data: {event_data.get('data', 'No data')}")
        
        # Subscribe to events
        await event_bus.subscribe("astra.testing.*", "test_group", test_handler)
        
        # Wait a bit for processing
        await asyncio.sleep(2)
        
        print("✅ Redis Streams test completed")
        
    except Exception as e:
        print(f"❌ Redis Streams test failed: {e}")
    
    finally:
        await event_bus.close()


if __name__ == "__main__":
    asyncio.run(test_redis_streams())