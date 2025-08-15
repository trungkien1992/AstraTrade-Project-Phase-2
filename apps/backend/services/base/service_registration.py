"""
Service Registration Module for AstraTrade Microservices

This module provides functionality for microservices to register themselves
with the service discovery system and maintain heartbeats.
"""

import asyncio
import os
import socket
import time
from typing import Dict, Any, Optional
import logging
from contextlib import asynccontextmanager

# Import service discovery components
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from service_discovery import ServiceRegistry, ServiceInstance, ServiceClient

logger = logging.getLogger("service-registration")


class MicroserviceRegistration:
    """Handles service registration for microservices."""
    
    def __init__(
        self,
        service_name: str,
        service_port: int,
        service_version: str = "1.0.0",
        redis_url: str = None,
        metadata: Dict[str, Any] = None
    ):
        self.service_name = service_name
        self.service_port = service_port
        self.service_version = service_version
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379")
        self.metadata = metadata or {}
        
        self.registry = None
        self.service_client = None
        self.instance_id = f"{service_name}-{int(time.time())}"
        self.host = self._get_host()
        
        # Add default metadata
        self.metadata.update({
            "service_type": "microservice",
            "started_at": time.time(),
            "python_version": sys.version,
            "environment": os.getenv("ENVIRONMENT", "development")
        })
    
    def _get_host(self) -> str:
        """Get the host IP address."""
        try:
            # Try to get container hostname first
            hostname = os.getenv("HOSTNAME", socket.gethostname())
            
            # In Docker environment, use container name
            if os.path.exists("/.dockerenv"):
                return hostname
            
            # For local development, use localhost
            return "localhost"
        
        except Exception:
            return "localhost"
    
    async def start(self) -> bool:
        """Start service registration."""
        try:
            logger.info(f"🚀 Starting service registration for {self.service_name}")
            
            # Initialize service registry
            self.registry = ServiceRegistry(self.redis_url)
            await self.registry.start()
            
            # Create service instance
            service_instance = ServiceInstance(
                service_name=self.service_name,
                instance_id=self.instance_id,
                host=self.host,
                port=self.service_port,
                version=self.service_version,
                metadata=self.metadata
            )
            
            # Create service client for registration and heartbeat
            self.service_client = ServiceClient(self.registry, service_instance)
            success = await self.service_client.start()
            
            if success:
                logger.info(
                    f"✅ Service {self.service_name} registered successfully at "
                    f"{self.host}:{self.service_port} (ID: {self.instance_id})"
                )
                return True
            else:
                logger.error(f"❌ Failed to register service {self.service_name}")
                return False
        
        except Exception as e:
            logger.error(f"❌ Service registration error: {e}")
            return False
    
    async def stop(self) -> None:
        """Stop service registration."""
        try:
            logger.info(f"🔄 Stopping service registration for {self.service_name}")
            
            if self.service_client:
                await self.service_client.stop()
                logger.info(f"✅ Service {self.service_name} deregistered")
            
            if self.registry:
                await self.registry.stop()
                logger.info("✅ Service registry connection closed")
        
        except Exception as e:
            logger.error(f"❌ Service deregistration error: {e}")
    
    async def update_metadata(self, metadata: Dict[str, Any]) -> bool:
        """Update service metadata."""
        try:
            if self.service_client:
                self.metadata.update(metadata)
                self.service_client.service.metadata = self.metadata
                logger.info(f"✅ Updated metadata for {self.service_name}")
                return True
            return False
        
        except Exception as e:
            logger.error(f"❌ Metadata update error: {e}")
            return False
    
    @property
    def is_registered(self) -> bool:
        """Check if service is registered."""
        return self.service_client is not None and self.registry is not None


@asynccontextmanager
async def register_microservice(
    service_name: str,
    service_port: int,
    service_version: str = "1.0.0",
    metadata: Dict[str, Any] = None
):
    """Context manager for microservice registration."""
    registration = MicroserviceRegistration(
        service_name=service_name,
        service_port=service_port,
        service_version=service_version,
        metadata=metadata
    )
    
    try:
        # Start registration
        success = await registration.start()
        if not success:
            logger.warning(f"⚠️ Failed to register {service_name}, continuing without service discovery")
        
        yield registration
    
    finally:
        # Cleanup
        await registration.stop()


# FastAPI integration
def create_service_lifespan(
    service_name: str,
    service_port: int,
    service_version: str = "1.0.0",
    metadata: Dict[str, Any] = None
):
    """Create FastAPI lifespan context manager with service registration."""
    
    @asynccontextmanager
    async def lifespan(app):
        # Startup
        logger.info(f"🚀 Starting {service_name} microservice")
        
        async with register_microservice(
            service_name=service_name,
            service_port=service_port,
            service_version=service_version,
            metadata=metadata
        ) as registration:
            
            # Store registration in app state for use in endpoints
            app.state.service_registration = registration
            
            logger.info(f"✅ {service_name} microservice ready")
            
            yield
        
        # Shutdown
        logger.info(f"👋 {service_name} microservice shutdown complete")
    
    return lifespan


# Health check enhancement for services
def create_enhanced_health_check(additional_checks: Dict[str, callable] = None):
    """Create enhanced health check with service discovery integration."""
    
    async def health_check_endpoint(request):
        """Enhanced health check endpoint."""
        from fastapi import Request
        from fastapi.responses import JSONResponse
        
        health_status = {
            "status": "healthy",
            "timestamp": time.time(),
            "service_name": getattr(request.app.state, 'service_name', 'unknown'),
            "checks": {}
        }
        
        overall_healthy = True
        
        # Check service registration
        if hasattr(request.app.state, 'service_registration'):
            registration = request.app.state.service_registration
            health_status["checks"]["service_registration"] = {
                "healthy": registration.is_registered,
                "instance_id": registration.instance_id if registration.is_registered else None
            }
            
            if not registration.is_registered:
                overall_healthy = False
        
        # Run additional health checks
        if additional_checks:
            for check_name, check_func in additional_checks.items():
                try:
                    result = await check_func() if asyncio.iscoroutinefunction(check_func) else check_func()
                    health_status["checks"][check_name] = {
                        "healthy": True,
                        "result": result
                    }
                except Exception as e:
                    health_status["checks"][check_name] = {
                        "healthy": False,
                        "error": str(e)
                    }
                    overall_healthy = False
        
        # Set overall status
        health_status["status"] = "healthy" if overall_healthy else "unhealthy"
        
        status_code = 200 if overall_healthy else 503
        return JSONResponse(content=health_status, status_code=status_code)
    
    return health_check_endpoint


# Environment-based configuration
def get_service_config() -> Dict[str, Any]:
    """Get service configuration from environment variables."""
    return {
        "service_name": os.getenv("SERVICE_NAME", "unknown"),
        "service_port": int(os.getenv("SERVICE_PORT", "8000")),
        "service_version": os.getenv("SERVICE_VERSION", "1.0.0"),
        "redis_url": os.getenv("REDIS_URL", "redis://localhost:6379"),
        "log_level": os.getenv("LOG_LEVEL", "INFO"),
        "environment": os.getenv("ENVIRONMENT", "development")
    }


# Example usage
async def example_microservice():
    """Example of how to use service registration."""
    config = get_service_config()
    
    async with register_microservice(
        service_name=config["service_name"],
        service_port=config["service_port"],
        service_version=config["service_version"],
        metadata={
            "domain": "example",
            "capabilities": ["health_check", "metrics"]
        }
    ) as registration:
        
        logger.info("Service registered, running application...")
        
        # Simulate application running
        for i in range(10):
            await asyncio.sleep(1)
            
            # Update metadata periodically
            if i == 5:
                await registration.update_metadata({
                    "requests_handled": 100,
                    "uptime_seconds": i
                })
        
        logger.info("Application stopping...")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run example
    asyncio.run(example_microservice())