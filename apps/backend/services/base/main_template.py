"""
Base FastAPI application template for AstraTrade microservices.
Provides common setup and configuration for all services.
"""

import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from .config import config
from .health import router as health_router, setup_health_checker
from .metrics import track_http_requests, metrics_endpoint, metrics_collector
from .dependencies import (
    initialize_dependencies, 
    cleanup_dependencies, 
    database_manager, 
    redis_manager
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    logger.info(f"Starting {config.service_name} service...")
    
    try:
        # Initialize dependencies
        await initialize_dependencies()
        
        # Setup health checker with dependencies
        setup_health_checker(
            db_engine=database_manager.engine,
            redis_client=redis_manager.client
        )
        
        logger.info(f"{config.service_name} service started successfully")
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to start {config.service_name}: {e}")
        raise
    
    finally:
        logger.info(f"Shutting down {config.service_name} service...")
        
        try:
            # Cleanup dependencies
            await cleanup_dependencies()
            logger.info(f"{config.service_name} service stopped successfully")
        except Exception as e:
            logger.error(f"Error during {config.service_name} shutdown: {e}")


def create_app(title: str = None, description: str = None, version: str = None) -> FastAPI:
    """Create FastAPI application with common configuration."""
    
    app_title = title or f"AstraTrade {config.service_name.title()} Service"
    app_description = description or f"Microservice for {config.service_name} domain operations"
    app_version = version or config.service_version
    
    # Create FastAPI app
    app = FastAPI(
        title=app_title,
        description=app_description,
        version=app_version,
        lifespan=lifespan,
        debug=config.debug
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add trusted host middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"] if config.debug else ["localhost", "127.0.0.1", config.service_host]
    )
    
    # Add metrics middleware
    if config.metrics_enabled:
        app.middleware("http")(track_http_requests())
    
    # Add health endpoints
    app.include_router(health_router, tags=["Health"])
    
    # Add metrics endpoint
    if config.metrics_enabled:
        app.get("/metrics", include_in_schema=False)(metrics_endpoint)
    
    # Add global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "service": config.service_name,
                "path": str(request.url.path)
            }
        )
    
    # Add correlation ID middleware
    @app.middleware("http")
    async def correlation_id_middleware(request: Request, call_next):
        # Get or generate correlation ID
        correlation_id = request.headers.get("X-Correlation-ID")
        if not correlation_id:
            import uuid
            correlation_id = f"{config.service_name}-{uuid.uuid4().hex[:16]}"
        
        # Store in request state
        request.state.correlation_id = correlation_id
        
        # Process request
        response = await call_next(request)
        
        # Add correlation ID to response
        response.headers["X-Correlation-ID"] = correlation_id
        
        return response
    
    # Add service info endpoint
    @app.get("/info", tags=["Service"])
    async def service_info():
        """Get service information."""
        return {
            "service": config.service_name,
            "version": config.service_version,
            "environment": config.environment,
            "container_id": config.get_container_id(),
            "debug": config.debug
        }
    
    logger.info(f"Created FastAPI app for {config.service_name}")
    return app


# Service registration utilities
async def register_with_api_gateway():
    """Register service with API Gateway service discovery."""
    try:
        from ..base.dependencies import redis_manager
        
        # Get Redis client for service registry
        client = await redis_manager.get_client()
        
        # Create service registration data
        service_data = {
            "service_name": config.service_name,
            "instance_id": config.get_container_id(),
            "host": config.service_host,
            "port": str(config.service_port),
            "version": config.service_version,
            "health_check_url": f"http://{config.service_host}:{config.service_port}/health",
            "status": "healthy",
            "metadata": f'{{"domain": "{config.service_name}", "container_id": "{config.get_container_id()}"}}'
        }
        
        # Register in Redis
        service_key = f"service:{config.service_name}:{config.get_container_id()}"
        await client.hset(service_key, mapping=service_data)
        await client.expire(service_key, 60)  # Auto-expire in 60 seconds
        
        # Add to service list
        await client.sadd(f"services:{config.service_name}", config.get_container_id())
        await client.expire(f"services:{config.service_name}", 60)
        
        logger.info(f"Registered {config.service_name} with service discovery")
        
    except Exception as e:
        logger.error(f"Failed to register {config.service_name} with service discovery: {e}")


async def start_heartbeat():
    """Start heartbeat task for service discovery."""
    async def heartbeat_loop():
        while True:
            try:
                await register_with_api_gateway()
                await asyncio.sleep(30)  # Send heartbeat every 30 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Heartbeat error for {config.service_name}: {e}")
                await asyncio.sleep(5)  # Retry after 5 seconds on error
    
    # Start heartbeat task
    heartbeat_task = asyncio.create_task(heartbeat_loop())
    logger.info(f"Started heartbeat for {config.service_name}")
    
    return heartbeat_task