"""
Dependency injection and connection management for AstraTrade microservices.
Handles database and Redis connections with proper lifecycle management.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

import redis.asyncio as redis
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool

from .config import config

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and sessions."""
    
    def __init__(self):
        self.engine: Optional[AsyncEngine] = None
        self.session_factory: Optional[async_sessionmaker] = None
    
    async def initialize(self) -> AsyncEngine:
        """Initialize database engine and session factory."""
        if self.engine:
            return self.engine
        
        db_config = config.get_database_config()
        
        # Create async engine
        self.engine = create_async_engine(
            db_config["url"],
            pool_size=db_config["pool_size"],
            max_overflow=db_config["max_overflow"],
            pool_recycle=db_config["pool_recycle"],
            pool_pre_ping=db_config["pool_pre_ping"],
            echo=db_config["echo"],
            # Use NullPool for better container management
            poolclass=NullPool if config.environment == "test" else None
        )
        
        # Create session factory
        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        logger.info(f"Database initialized for {config.service_name}")
        return self.engine
    
    async def close(self):
        """Close database engine."""
        if self.engine:
            await self.engine.dispose()
            self.engine = None
            self.session_factory = None
            logger.info(f"Database closed for {config.service_name}")
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session context manager."""
        if not self.session_factory:
            await self.initialize()
        
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()


class RedisManager:
    """Manages Redis connections and operations."""
    
    def __init__(self):
        self.client: Optional[redis.Redis] = None
        self.connection_pool: Optional[redis.ConnectionPool] = None
    
    async def initialize(self) -> redis.Redis:
        """Initialize Redis client with connection pool."""
        if self.client:
            return self.client
        
        redis_config = config.get_redis_config()
        
        # Create connection pool
        self.connection_pool = redis.ConnectionPool.from_url(
            redis_config["url"],
            max_connections=redis_config["max_connections"],
            retry_on_timeout=redis_config["retry_on_timeout"],
            health_check_interval=redis_config["health_check_interval"]
        )
        
        # Create client
        self.client = redis.Redis(
            connection_pool=self.connection_pool,
            decode_responses=True
        )
        
        # Test connection
        try:
            await self.client.ping()
            logger.info(f"Redis initialized for {config.service_name}")
        except Exception as e:
            logger.error(f"Redis connection failed for {config.service_name}: {e}")
            raise
        
        return self.client
    
    async def close(self):
        """Close Redis client and connection pool."""
        if self.client:
            await self.client.close()
            self.client = None
        
        if self.connection_pool:
            await self.connection_pool.disconnect()
            self.connection_pool = None
        
        logger.info(f"Redis closed for {config.service_name}")
    
    async def get_client(self) -> redis.Redis:
        """Get Redis client."""
        if not self.client:
            await self.initialize()
        return self.client


class EventBusManager:
    """Manages Redis Streams event bus operations."""
    
    def __init__(self, redis_manager: RedisManager):
        self.redis_manager = redis_manager
        self.consumer_tasks: list = []
    
    async def publish_event(self, stream_name: str, event_data: dict) -> str:
        """Publish event to Redis stream."""
        client = await self.redis_manager.get_client()
        
        # Add service metadata
        event_data.update({
            "producer": f"{config.service_name}@{config.get_container_id()}",
            "service_version": config.service_version,
            "published_at": str(asyncio.get_event_loop().time())
        })
        
        # Convert all values to strings for Redis
        stream_data = {k: str(v) for k, v in event_data.items()}
        
        message_id = await client.xadd(stream_name, stream_data)
        logger.debug(f"Published event to {stream_name}: {message_id}")
        
        return message_id
    
    async def create_consumer_group(self, stream_name: str, group_name: str) -> bool:
        """Create consumer group for stream."""
        client = await self.redis_manager.get_client()
        
        try:
            await client.xgroup_create(stream_name, group_name, id="0", mkstream=True)
            logger.info(f"Created consumer group {group_name} for stream {stream_name}")
            return True
        except redis.ResponseError as e:
            if "BUSYGROUP" in str(e):
                logger.debug(f"Consumer group {group_name} already exists for {stream_name}")
                return True
            else:
                logger.error(f"Failed to create consumer group {group_name}: {e}")
                return False
    
    async def consume_events(self, stream_patterns: list, group_name: str, consumer_name: str, handler_func):
        """Consume events from multiple streams."""
        client = await self.redis_manager.get_client()
        
        # Create consumer groups for all streams
        for pattern in stream_patterns:
            # For now, use pattern as stream name (could be enhanced for pattern matching)
            await self.create_consumer_group(pattern, group_name)
        
        logger.info(f"Starting event consumer {consumer_name} for group {group_name}")
        
        while True:
            try:
                # Read from multiple streams
                streams = {pattern: ">" for pattern in stream_patterns}
                messages = await client.xreadgroup(
                    group_name,
                    consumer_name,
                    streams,
                    count=10,
                    block=1000  # 1 second timeout
                )
                
                # Process messages
                for stream_name, stream_messages in messages:
                    for message_id, fields in stream_messages:
                        try:
                            await handler_func(stream_name, message_id, fields)
                            
                            # Acknowledge message
                            await client.xack(stream_name, group_name, message_id)
                            
                        except Exception as e:
                            logger.error(f"Error processing message {message_id} from {stream_name}: {e}")
                            # Could implement retry logic here
                
            except asyncio.CancelledError:
                logger.info(f"Event consumer {consumer_name} cancelled")
                break
            except Exception as e:
                logger.error(f"Event consumer {consumer_name} error: {e}")
                await asyncio.sleep(5)  # Wait before retry
    
    async def start_consumer(self, stream_patterns: list, group_name: str, handler_func):
        """Start background event consumer task."""
        consumer_name = f"{config.get_container_id()}-consumer"
        
        task = asyncio.create_task(
            self.consume_events(stream_patterns, group_name, consumer_name, handler_func)
        )
        self.consumer_tasks.append(task)
        
        logger.info(f"Started consumer task for {group_name}")
        return task
    
    async def stop_consumers(self):
        """Stop all consumer tasks."""
        for task in self.consumer_tasks:
            task.cancel()
        
        if self.consumer_tasks:
            await asyncio.gather(*self.consumer_tasks, return_exceptions=True)
        
        self.consumer_tasks.clear()
        logger.info("Stopped all event consumers")


# Global instances
database_manager = DatabaseManager()
redis_manager = RedisManager()
event_bus_manager = EventBusManager(redis_manager)


async def get_database_session():
    """FastAPI dependency for database session."""
    async with database_manager.get_session() as session:
        yield session


async def get_redis_client():
    """FastAPI dependency for Redis client."""
    return await redis_manager.get_client()


async def get_event_bus():
    """FastAPI dependency for event bus."""
    return event_bus_manager


async def initialize_dependencies():
    """Initialize all service dependencies."""
    logger.info(f"Initializing dependencies for {config.service_name}")
    
    # Initialize database
    await database_manager.initialize()
    
    # Initialize Redis
    await redis_manager.initialize()
    
    logger.info(f"Dependencies initialized for {config.service_name}")


async def cleanup_dependencies():
    """Cleanup all service dependencies."""
    logger.info(f"Cleaning up dependencies for {config.service_name}")
    
    # Stop event consumers
    await event_bus_manager.stop_consumers()
    
    # Close Redis
    await redis_manager.close()
    
    # Close database
    await database_manager.close()
    
    logger.info(f"Dependencies cleaned up for {config.service_name}")