"""
Health check implementation for AstraTrade microservices.
Provides comprehensive dependency health monitoring.
"""

import asyncio
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncEngine
import redis.asyncio as redis

from .config import config


router = APIRouter()


class HealthChecker:
    """Centralized health checking for service dependencies."""
    
    def __init__(self, db_engine: Optional[AsyncEngine] = None, redis_client: Optional[redis.Redis] = None):
        self.db_engine = db_engine
        self.redis_client = redis_client
        self.startup_time = time.time()
    
    async def check_database(self) -> Dict[str, Any]:
        """Check database connectivity and performance."""
        if not self.db_engine:
            return {"status": "not_configured", "message": "Database not configured"}
        
        try:
            start_time = time.time()
            
            # Simple connectivity test
            async with self.db_engine.connect() as connection:
                result = await connection.execute("SELECT 1")
                await result.fetchone()
            
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            return {
                "status": "healthy",
                "response_time_ms": round(response_time, 2),
                "pool_size": self.db_engine.pool.size() if hasattr(self.db_engine, 'pool') else "unknown",
                "checked_out": self.db_engine.pool.checkedout() if hasattr(self.db_engine, 'pool') else "unknown"
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    async def check_redis(self) -> Dict[str, Any]:
        """Check Redis connectivity and performance."""
        if not self.redis_client:
            return {"status": "not_configured", "message": "Redis not configured"}
        
        try:
            start_time = time.time()
            
            # Test basic connectivity
            await self.redis_client.ping()
            
            # Test set/get operation
            test_key = f"health_check_{config.service_name}_{int(time.time())}"
            await self.redis_client.set(test_key, "ok", ex=60)  # Expire in 60 seconds
            result = await self.redis_client.get(test_key)
            await self.redis_client.delete(test_key)
            
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            # Get Redis info
            info = await self.redis_client.info("memory")
            
            return {
                "status": "healthy",
                "response_time_ms": round(response_time, 2),
                "test_result": result.decode() if result else None,
                "memory_used_mb": round(info.get("used_memory", 0) / 1024 / 1024, 2),
                "connected_clients": info.get("connected_clients", "unknown")
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    async def check_service_discovery(self) -> Dict[str, Any]:
        """Check service discovery connectivity."""
        try:
            # Test connection to service registry (Redis-based)
            registry_client = redis.from_url(config.service_registry_url)
            
            start_time = time.time()
            await registry_client.ping()
            response_time = (time.time() - start_time) * 1000
            
            # Check if service is registered
            service_key = f"service:{config.service_name}:{config.get_container_id()}"
            is_registered = await registry_client.exists(service_key)
            
            await registry_client.close()
            
            return {
                "status": "healthy",
                "response_time_ms": round(response_time, 2),
                "service_registered": bool(is_registered),
                "registry_url": config.service_registry_url
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    async def get_comprehensive_health(self) -> Dict[str, Any]:
        """Get comprehensive health status for all dependencies."""
        uptime = time.time() - self.startup_time
        
        # Run all health checks concurrently
        db_health, redis_health, registry_health = await asyncio.gather(
            self.check_database(),
            self.check_redis(),
            self.check_service_discovery(),
            return_exceptions=True
        )
        
        # Handle any exceptions from health checks
        if isinstance(db_health, Exception):
            db_health = {"status": "error", "error": str(db_health)}
        if isinstance(redis_health, Exception):
            redis_health = {"status": "error", "error": str(redis_health)}
        if isinstance(registry_health, Exception):
            registry_health = {"status": "error", "error": str(registry_health)}
        
        # Determine overall status
        all_dependencies = [db_health, redis_health, registry_health]
        unhealthy_deps = [dep for dep in all_dependencies if dep.get("status") != "healthy"]
        
        overall_status = "healthy" if not unhealthy_deps else "unhealthy"
        
        return {
            "status": overall_status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": config.service_name,
            "version": config.service_version,
            "uptime_seconds": round(uptime, 2),
            "container_id": config.get_container_id(),
            "dependencies": {
                "database": db_health,
                "redis": redis_health,
                "service_discovery": registry_health
            },
            "environment": config.environment,
            "debug": config.debug
        }


# Global health checker instance
health_checker = HealthChecker()


@router.get("/health")
async def health_check():
    """Basic health check endpoint."""
    health_status = await health_checker.get_comprehensive_health()
    
    # Return 503 if unhealthy
    if health_status["status"] != "healthy":
        raise HTTPException(status_code=503, detail=health_status)
    
    return health_status


@router.get("/health/live")
async def liveness_check():
    """Kubernetes liveness probe - basic service availability."""
    return {
        "status": "alive",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": config.service_name,
        "uptime_seconds": round(time.time() - health_checker.startup_time, 2)
    }


@router.get("/health/ready")
async def readiness_check():
    """Kubernetes readiness probe - service ready to accept traffic."""
    health_status = await health_checker.get_comprehensive_health()
    
    # Check if critical dependencies are healthy
    dependencies = health_status.get("dependencies", {})
    critical_deps = ["database", "redis"]  # Service discovery is non-critical
    
    for dep_name in critical_deps:
        dep_status = dependencies.get(dep_name, {})
        if dep_status.get("status") != "healthy":
            raise HTTPException(
                status_code=503, 
                detail={
                    "status": "not_ready",
                    "reason": f"{dep_name} dependency unhealthy",
                    "dependency_status": dep_status
                }
            )
    
    return {
        "status": "ready",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": config.service_name,
        "critical_dependencies": {dep: dependencies[dep] for dep in critical_deps}
    }


def setup_health_checker(db_engine: AsyncEngine = None, redis_client: redis.Redis = None):
    """Initialize health checker with service dependencies."""
    global health_checker
    health_checker.db_engine = db_engine
    health_checker.redis_client = redis_client