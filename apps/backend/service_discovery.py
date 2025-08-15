"""
AstraTrade Service Discovery System

Manages service registration, health checks, and load balancing
for microservices deployment in the Infrastructure Bridge Strategy.
"""

import asyncio
import json
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import logging

# Redis for service registry
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("Warning: Redis not available for service discovery")

logger = logging.getLogger("service-discovery")


class ServiceStatus(Enum):
    """Service health status."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    STARTING = "starting"
    STOPPING = "stopping"
    UNKNOWN = "unknown"


@dataclass
class ServiceInstance:
    """Represents a service instance in the registry."""
    service_name: str
    instance_id: str
    host: str
    port: int
    version: str
    status: ServiceStatus = ServiceStatus.STARTING
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_heartbeat: float = field(default_factory=time.time)
    health_check_url: str = ""
    
    def __post_init__(self):
        if not self.health_check_url:
            self.health_check_url = f"http://{self.host}:{self.port}/health"
    
    @property
    def is_healthy(self) -> bool:
        """Check if service instance is healthy."""
        return (
            self.status == ServiceStatus.HEALTHY and
            time.time() - self.last_heartbeat < 30  # 30-second timeout
        )
    
    @property
    def service_url(self) -> str:
        """Get service base URL."""
        return f"http://{self.host}:{self.port}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Redis storage."""
        return {
            "service_name": self.service_name,
            "instance_id": self.instance_id,
            "host": self.host,
            "port": self.port,
            "version": self.version,
            "status": self.status.value,
            "metadata": json.dumps(self.metadata),
            "last_heartbeat": self.last_heartbeat,
            "health_check_url": self.health_check_url
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ServiceInstance':
        """Create instance from dictionary."""
        return cls(
            service_name=data["service_name"],
            instance_id=data["instance_id"],
            host=data["host"],
            port=int(data["port"]),
            version=data["version"],
            status=ServiceStatus(data["status"]),
            metadata=json.loads(data.get("metadata", "{}")),
            last_heartbeat=float(data["last_heartbeat"]),
            health_check_url=data["health_check_url"]
        )


class ServiceRegistry:
    """
    Redis-based service registry for microservices discovery.
    
    Features:
    - Service registration and deregistration
    - Health check monitoring
    - Load balancing with multiple strategies
    - Service metadata management
    - Automatic cleanup of stale services
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self._redis = None
        self._services: Dict[str, Dict[str, ServiceInstance]] = {}
        self._health_check_interval = 10  # seconds
        self._cleanup_interval = 30  # seconds
        self._running = False
    
    async def start(self) -> None:
        """Start the service registry."""
        if not REDIS_AVAILABLE:
            logger.warning("Redis not available - using in-memory registry")
            self._running = True
            return
        
        try:
            self._redis = redis.from_url(self.redis_url, decode_responses=True)
            await self._redis.ping()
            logger.info("✅ Service registry connected to Redis")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            logger.info("🔄 Falling back to in-memory registry")
            self._redis = None
        
        self._running = True
        
        # Start background tasks
        asyncio.create_task(self._health_check_loop())
        asyncio.create_task(self._cleanup_loop())
        
        logger.info("🚀 Service registry started")
    
    async def stop(self) -> None:
        """Stop the service registry."""
        self._running = False
        
        if self._redis:
            await self._redis.close()
        
        logger.info("🔄 Service registry stopped")
    
    async def register_service(self, service: ServiceInstance) -> bool:
        """Register a service instance."""
        try:
            # Update local cache
            if service.service_name not in self._services:
                self._services[service.service_name] = {}
            
            self._services[service.service_name][service.instance_id] = service
            
            # Store in Redis if available
            if self._redis:
                key = f"service:{service.service_name}:{service.instance_id}"
                await self._redis.hset(key, mapping=service.to_dict())
                await self._redis.expire(key, 60)  # Auto-expire in 60 seconds
                
                # Add to service list
                await self._redis.sadd(f"services:{service.service_name}", service.instance_id)
                await self._redis.expire(f"services:{service.service_name}", 60)
            
            logger.info(f"✅ Registered {service.service_name}:{service.instance_id} at {service.service_url}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to register service {service.service_name}: {e}")
            return False
    
    async def deregister_service(self, service_name: str, instance_id: str) -> bool:
        """Deregister a service instance."""
        try:
            # Remove from local cache
            if service_name in self._services and instance_id in self._services[service_name]:
                del self._services[service_name][instance_id]
                
                if not self._services[service_name]:
                    del self._services[service_name]
            
            # Remove from Redis if available
            if self._redis:
                key = f"service:{service_name}:{instance_id}"
                await self._redis.delete(key)
                await self._redis.srem(f"services:{service_name}", instance_id)
            
            logger.info(f"✅ Deregistered {service_name}:{instance_id}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to deregister service {service_name}: {e}")
            return False
    
    async def heartbeat(self, service_name: str, instance_id: str) -> bool:
        """Update service heartbeat."""
        try:
            # Update local cache
            if (service_name in self._services and 
                instance_id in self._services[service_name]):
                
                service = self._services[service_name][instance_id]
                service.last_heartbeat = time.time()
                service.status = ServiceStatus.HEALTHY
                
                # Update Redis
                if self._redis:
                    key = f"service:{service_name}:{instance_id}"
                    await self._redis.hset(key, mapping={
                        "last_heartbeat": service.last_heartbeat,
                        "status": service.status.value
                    })
                    await self._redis.expire(key, 60)
                
                return True
        
        except Exception as e:
            logger.error(f"❌ Heartbeat failed for {service_name}:{instance_id}: {e}")
        
        return False
    
    async def get_service_instances(self, service_name: str) -> List[ServiceInstance]:
        """Get all healthy instances of a service."""
        instances = []
        
        try:
            # Check local cache first
            if service_name in self._services:
                for instance in self._services[service_name].values():
                    if instance.is_healthy:
                        instances.append(instance)
            
            # If Redis available, also check Redis for any missed instances
            if self._redis:
                instance_ids = await self._redis.smembers(f"services:{service_name}")
                
                for instance_id in instance_ids:
                    if instance_id not in [i.instance_id for i in instances]:
                        key = f"service:{service_name}:{instance_id}"
                        data = await self._redis.hgetall(key)
                        
                        if data:
                            instance = ServiceInstance.from_dict(data)
                            if instance.is_healthy:
                                instances.append(instance)
                                # Update local cache
                                if service_name not in self._services:
                                    self._services[service_name] = {}
                                self._services[service_name][instance_id] = instance
        
        except Exception as e:
            logger.error(f"❌ Failed to get service instances for {service_name}: {e}")
        
        return instances
    
    async def get_service_instance(self, service_name: str, strategy: str = "round_robin") -> Optional[ServiceInstance]:
        """Get a single service instance using load balancing strategy."""
        instances = await self.get_service_instances(service_name)
        
        if not instances:
            return None
        
        if strategy == "round_robin":
            # Simple round-robin (would implement proper state tracking in production)
            return instances[hash(service_name) % len(instances)]
        
        elif strategy == "random":
            import random
            return random.choice(instances)
        
        elif strategy == "least_connections":
            # Would track connection counts in production
            return min(instances, key=lambda x: x.metadata.get("connections", 0))
        
        else:
            return instances[0]  # Default to first available
    
    async def get_all_services(self) -> Dict[str, List[ServiceInstance]]:
        """Get all services and their instances."""
        all_services = {}
        
        # Get from local cache
        for service_name in self._services:
            instances = await self.get_service_instances(service_name)
            if instances:
                all_services[service_name] = instances
        
        # Also check Redis for any services not in local cache
        if self._redis:
            try:
                keys = await self._redis.keys("services:*")
                for key in keys:
                    service_name = key.split(":", 1)[1]
                    if service_name not in all_services:
                        instances = await self.get_service_instances(service_name)
                        if instances:
                            all_services[service_name] = instances
            except Exception as e:
                logger.error(f"❌ Failed to get all services from Redis: {e}")
        
        return all_services
    
    async def _health_check_loop(self) -> None:
        """Background health check loop."""
        while self._running:
            try:
                await asyncio.sleep(self._health_check_interval)
                await self._perform_health_checks()
            except Exception as e:
                logger.error(f"❌ Health check loop error: {e}")
    
    async def _cleanup_loop(self) -> None:
        """Background cleanup loop for stale services."""
        while self._running:
            try:
                await asyncio.sleep(self._cleanup_interval)
                await self._cleanup_stale_services()
            except Exception as e:
                logger.error(f"❌ Cleanup loop error: {e}")
    
    async def _perform_health_checks(self) -> None:
        """Perform health checks on all registered services."""
        current_time = time.time()
        
        for service_name, instances in self._services.items():
            for instance_id, instance in list(instances.items()):
                # Check if heartbeat is stale
                if current_time - instance.last_heartbeat > 30:
                    logger.warning(f"⚠️  Stale heartbeat for {service_name}:{instance_id}")
                    instance.status = ServiceStatus.UNHEALTHY
                
                # Could also perform HTTP health checks here
                # await self._http_health_check(instance)
    
    async def _cleanup_stale_services(self) -> None:
        """Remove stale service instances."""
        current_time = time.time()
        
        for service_name, instances in list(self._services.items()):
            for instance_id, instance in list(instances.items()):
                if current_time - instance.last_heartbeat > 60:  # 1 minute timeout
                    logger.info(f"🧹 Cleaning up stale service {service_name}:{instance_id}")
                    await self.deregister_service(service_name, instance_id)


# Service discovery client for services to register themselves
class ServiceClient:
    """Client for services to register and maintain heartbeat."""
    
    def __init__(self, registry: ServiceRegistry, service: ServiceInstance):
        self.registry = registry
        self.service = service
        self._heartbeat_task = None
    
    async def start(self) -> bool:
        """Start the service client."""
        # Register service
        success = await self.registry.register_service(self.service)
        
        if success:
            # Start heartbeat
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            logger.info(f"🚀 Service client started for {self.service.service_name}")
        
        return success
    
    async def stop(self) -> None:
        """Stop the service client."""
        # Stop heartbeat
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
        
        # Deregister service
        await self.registry.deregister_service(
            self.service.service_name, 
            self.service.instance_id
        )
        
        logger.info(f"🔄 Service client stopped for {self.service.service_name}")
    
    async def _heartbeat_loop(self) -> None:
        """Send periodic heartbeats."""
        while True:
            try:
                await asyncio.sleep(5)  # Heartbeat every 5 seconds
                await self.registry.heartbeat(
                    self.service.service_name,
                    self.service.instance_id
                )
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Heartbeat error: {e}")


# Example usage and testing
async def test_service_discovery():
    """Test service discovery system."""
    print("🔧 Testing Service Discovery System")
    print("=" * 50)
    
    # Create registry
    registry = ServiceRegistry()
    await registry.start()
    
    try:
        # Register some services
        trading_service = ServiceInstance(
            service_name="trading",
            instance_id="trading-001",
            host="localhost",
            port=8001,
            version="1.0.0",
            metadata={"domain": "trading", "replicas": 2}
        )
        
        gamification_service = ServiceInstance(
            service_name="gamification",
            instance_id="gamification-001", 
            host="localhost",
            port=8002,
            version="1.0.0",
            metadata={"domain": "gamification", "replicas": 1}
        )
        
        # Register services
        await registry.register_service(trading_service)
        await registry.register_service(gamification_service)
        
        # Create service clients
        trading_client = ServiceClient(registry, trading_service)
        await trading_client.start()
        
        print("✅ Services registered and heartbeat started")
        
        # Test service discovery
        trading_instances = await registry.get_service_instances("trading")
        print(f"📊 Found {len(trading_instances)} trading instances")
        
        # Test load balancing
        instance = await registry.get_service_instance("trading", "round_robin")
        if instance:
            print(f"🎯 Selected instance: {instance.service_url}")
        
        # Test service listing
        all_services = await registry.get_all_services()
        print(f"📋 Total services: {len(all_services)}")
        
        for service_name, instances in all_services.items():
            print(f"   • {service_name}: {len(instances)} instances")
            for instance in instances:
                print(f"     - {instance.instance_id} at {instance.service_url}")
        
        print("✅ Service discovery test completed")
        
        # Cleanup
        await trading_client.stop()
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        await registry.stop()


if __name__ == "__main__":
    asyncio.run(test_service_discovery())