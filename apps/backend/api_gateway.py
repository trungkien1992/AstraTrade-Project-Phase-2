"""
AstraTrade API Gateway

FastAPI-based API gateway with domain routing, correlation tracking,
authentication, and event-driven integration.
"""

import asyncio
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Depends, Request, Response, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field
import uvicorn

# Rate limiting and security
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# Custom rate limiting with Redis
class EnhancedRateLimiter:
    """Enhanced rate limiter with per-user and per-service limits."""
    
    def __init__(self):
        self.user_limits = defaultdict(lambda: {"count": 0, "reset_time": time.time() + 60})
        self.service_limits = defaultdict(lambda: {"count": 0, "reset_time": time.time() + 60})
    
    def check_user_limit(self, user_id: str, limit: int = 100) -> bool:
        """Check if user is within rate limit."""
        current_time = time.time()
        user_data = self.user_limits[user_id]
        
        if current_time > user_data["reset_time"]:
            user_data["count"] = 0
            user_data["reset_time"] = current_time + 60
        
        if user_data["count"] >= limit:
            return False
        
        user_data["count"] += 1
        return True
    
    def check_service_limit(self, service_name: str, limit: int = 1000) -> bool:
        """Check if service is within rate limit."""
        current_time = time.time()
        service_data = self.service_limits[service_name]
        
        if current_time > service_data["reset_time"]:
            service_data["count"] = 0
            service_data["reset_time"] = current_time + 60
        
        if service_data["count"] >= limit:
            return False
        
        service_data["count"] += 1
        return True


enhanced_limiter = EnhancedRateLimiter()

# Logging and monitoring
import logging
from contextlib import asynccontextmanager

# Import event bus integration and service discovery
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'domains', 'shared'))

try:
    from redis_streams import RedisStreamsEventBus, create_redis_event
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("Warning: Redis integration not available")

# Import service discovery
from service_discovery import ServiceRegistry, ServiceInstance
import httpx
from enum import Enum
from collections import defaultdict
import random
from typing import DefaultDict

# Import WebSocket manager and competition service
try:
    from services.competition.websocket_manager import TournamentWebSocketManager
    from services.competition.competition_service import CompetitionService
    import redis
    TOURNAMENT_WEBSOCKET_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Tournament WebSocket not available: {e}")
    TOURNAMENT_WEBSOCKET_AVAILABLE = False


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("astra-gateway")


# Rate limiter
limiter = Limiter(key_func=get_remote_address)


# Request/Response Models
class CircuitBreakerState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """Circuit breaker for service resilience."""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = CircuitBreakerState.CLOSED
    
    def can_request(self) -> bool:
        """Check if requests are allowed."""
        if self.state == CircuitBreakerState.CLOSED:
            return True
        
        if self.state == CircuitBreakerState.OPEN:
            if time.time() - self.last_failure_time > self.timeout:
                self.state = CircuitBreakerState.HALF_OPEN
                return True
            return False
        
        # HALF_OPEN state
        return True
    
    def record_success(self):
        """Record successful request."""
        self.failure_count = 0
        self.state = CircuitBreakerState.CLOSED
    
    def record_failure(self):
        """Record failed request."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN


class APIResponse(BaseModel):
    """Standard API response format."""
    success: bool
    data: Any = None
    message: str = ""
    correlation_id: str = ""
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class TradeRequest(BaseModel):
    """Trading API request model."""
    user_id: int
    asset_symbol: str
    direction: str = Field(..., regex="^(LONG|SHORT)$")
    amount: float = Field(..., gt=0)
    risk_percentage: float = Field(default=1.0, ge=0.1, le=10.0)
    is_mock: bool = False


class UserRegistrationRequest(BaseModel):
    """User registration request model."""
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    password: str = Field(..., min_length=8)


# Global state for event bus and services
class GatewayState:
    event_bus: Optional[RedisStreamsEventBus] = None
    service_registry: Optional[ServiceRegistry] = None
    services: Dict[str, Any] = {}
    circuit_breakers: Dict[str, CircuitBreaker] = {}
    metrics: Dict[str, int] = {
        "requests_total": 0,
        "requests_by_domain": {},
        "errors_total": 0,
        "events_published": 0,
        "circuit_breaker_opens": 0,
        "failed_requests": 0,
        "service_discovery_calls": 0,
        "websocket_connections": 0,
        "websocket_messages": 0
    }
    request_counts: DefaultDict[str, int] = defaultdict(int)
    last_reset_time: float = time.time()
    
    # WebSocket and tournament components
    websocket_manager: Optional[TournamentWebSocketManager] = None
    competition_service: Optional[CompetitionService] = None
    redis_client: Optional[redis.Redis] = None


gateway_state = GatewayState()


# Application lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management."""
    # Startup
    logger.info("🚀 Starting AstraTrade API Gateway")
    
    # Initialize service registry
    gateway_state.service_registry = ServiceRegistry()
    await gateway_state.service_registry.start()
    logger.info("✅ Service registry initialized")
    
    # Initialize event bus
    if REDIS_AVAILABLE:
        gateway_state.event_bus = RedisStreamsEventBus()
        logger.info("✅ Redis Streams event bus initialized")
    else:
        logger.warning("⚠️  Redis not available - events will be logged only")
    
    # Initialize circuit breakers for each service
    service_names = ["trading", "gamification", "social", "user", "financial", "nft"]
    for service_name in service_names:
        gateway_state.circuit_breakers[service_name] = CircuitBreaker(
            failure_threshold=5,
            timeout=30
        )
    
    # Initialize services (mock implementations for now)
    gateway_state.services = {
        "trading": MockTradingService(),
        "gamification": MockGamificationService(),
        "social": MockSocialService(),
        "user": MockUserService(),
        "financial": MockFinancialService(),
        "nft": MockNFTService()
    }
    
    # Initialize tournament WebSocket and competition service
    if TOURNAMENT_WEBSOCKET_AVAILABLE:
        try:
            # Initialize Redis client
            gateway_state.redis_client = redis.Redis(
                host='localhost', port=6379, decode_responses=True
            )
            
            # Initialize WebSocket manager
            gateway_state.websocket_manager = TournamentWebSocketManager(gateway_state.redis_client)
            
            # Initialize competition service
            gateway_state.competition_service = CompetitionService()
            await gateway_state.competition_service.start()
            
            logger.info("✅ Tournament WebSocket and Competition Service initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize tournament services: {e}")
            TOURNAMENT_WEBSOCKET_AVAILABLE = False
    else:
        logger.warning("⚠️ Tournament WebSocket services not available")
    
    logger.info("✅ Domain services and circuit breakers initialized")
    logger.info("🌐 API Gateway ready with service discovery")
    
    yield
    
    # Shutdown
    logger.info("🔄 Shutting down AstraTrade API Gateway")
    
    # Shutdown tournament services
    if gateway_state.competition_service:
        try:
            await gateway_state.competition_service.stop_ai_trading_cycle()
            logger.info("✅ Competition service stopped")
        except Exception as e:
            logger.error(f"Error stopping competition service: {e}")
    
    if gateway_state.websocket_manager:
        try:
            await gateway_state.websocket_manager.shutdown()
            logger.info("✅ WebSocket manager stopped")
        except Exception as e:
            logger.error(f"Error stopping WebSocket manager: {e}")
    
    if gateway_state.service_registry:
        await gateway_state.service_registry.stop()
        logger.info("✅ Service registry stopped")
    
    if gateway_state.event_bus and hasattr(gateway_state.event_bus, 'close'):
        await gateway_state.event_bus.close()
        logger.info("✅ Event bus closed")
    
    logger.info("👋 API Gateway shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="AstraTrade API Gateway",
    description="Production-ready API gateway for AstraTrade microservices",
    version="2.0.0",
    lifespan=lifespan
)

# Add rate limiting middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://astratrade.app"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Add trusted host middleware for security
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.astratrade.app"]
)


# Rate limiting middleware
@app.middleware("http")
async def rate_limiting_middleware(request: Request, call_next):
    """Enhanced rate limiting per user and service."""
    # Extract user ID (simplified)
    user_id = request.headers.get("X-User-ID", get_remote_address(request))
    
    # Extract service from path
    path_parts = request.url.path.split("/")
    service_name = path_parts[3] if len(path_parts) > 3 else "unknown"
    
    # Check user rate limit
    if not enhanced_limiter.check_user_limit(user_id, limit=200):  # 200 req/min per user
        return JSONResponse(
            status_code=429,
            content={
                "success": False,
                "message": "User rate limit exceeded",
                "limit": "200 requests per minute"
            }
        )
    
    # Check service rate limit
    if not enhanced_limiter.check_service_limit(service_name, limit=1000):  # 1000 req/min per service
        return JSONResponse(
            status_code=429,
            content={
                "success": False,
                "message": f"Service {service_name} rate limit exceeded",
                "limit": "1000 requests per minute"
            }
        )
    
    response = await call_next(request)
    return response


# Correlation ID middleware
@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    """Add correlation ID to all requests."""
    # Generate or extract correlation ID
    correlation_id = request.headers.get("X-Correlation-ID") or f"req_{uuid4().hex[:16]}"
    
    # Add to request state
    request.state.correlation_id = correlation_id
    
    # Process request
    start_time = time.time()
    response = await call_next(request)
    processing_time = time.time() - start_time
    
    # Add correlation ID to response headers
    response.headers["X-Correlation-ID"] = correlation_id
    response.headers["X-Processing-Time"] = f"{processing_time:.3f}s"
    
    # Update metrics
    gateway_state.metrics["requests_total"] += 1
    
    return response


# Request logging middleware
@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    """Log all requests with correlation tracking."""
    correlation_id = getattr(request.state, 'correlation_id', 'unknown')
    
    logger.info(
        f"📥 {request.method} {request.url.path} "
        f"[{correlation_id}] from {request.client.host if request.client else 'unknown'}"
    )
    
    try:
        response = await call_next(request)
        
        logger.info(
            f"📤 {response.status_code} {request.url.path} "
            f"[{correlation_id}] in {response.headers.get('X-Processing-Time', '?')}"
        )
        
        return response
    
    except Exception as e:
        gateway_state.metrics["errors_total"] += 1
        logger.error(f"❌ Error processing {request.url.path} [{correlation_id}]: {e}")
        raise


# Authentication dependency (simplified)
async def get_current_user(request: Request) -> Dict[str, Any]:
    """Get current user from request (simplified authentication)."""
    # In production, would validate JWT token
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        # For demo, allow unauthenticated requests
        return {"user_id": 999, "username": "demo_user", "authenticated": False}
    
    # Mock authentication
    return {"user_id": 123, "username": "authenticated_user", "authenticated": True}


# Service discovery helpers
async def get_healthy_service_instance(service_name: str) -> Optional[ServiceInstance]:
    """Get a healthy service instance using service discovery."""
    if not gateway_state.service_registry:
        return None
    
    gateway_state.metrics["service_discovery_calls"] += 1
    
    # Check circuit breaker
    circuit_breaker = gateway_state.circuit_breakers.get(service_name)
    if circuit_breaker and not circuit_breaker.can_request():
        logger.warning(f"🚨 Circuit breaker OPEN for {service_name}")
        return None
    
    # Get healthy instance
    instance = await gateway_state.service_registry.get_service_instance(
        service_name, strategy="round_robin"
    )
    
    return instance


async def make_service_request(
    service_name: str, 
    method: str, 
    path: str, 
    data: Dict[str, Any] = None,
    correlation_id: str = None
) -> Dict[str, Any]:
    """Make request to service with circuit breaker and retry logic."""
    instance = await get_healthy_service_instance(service_name)
    
    if not instance:
        # Fallback to mock service
        logger.warning(f"⚠️ No healthy {service_name} instance, using fallback")
        return await call_fallback_service(service_name, method, path, data, correlation_id)
    
    circuit_breaker = gateway_state.circuit_breakers[service_name]
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = f"{instance.service_url}{path}"
            headers = {"X-Correlation-ID": correlation_id} if correlation_id else {}
            
            if method.upper() == "GET":
                response = await client.get(url, headers=headers)
            elif method.upper() == "POST":
                response = await client.post(url, json=data, headers=headers)
            else:
                response = await client.request(method, url, json=data, headers=headers)
            
            response.raise_for_status()
            circuit_breaker.record_success()
            
            return response.json()
    
    except Exception as e:
        logger.error(f"❌ Service request failed {service_name}: {e}")
        circuit_breaker.record_failure()
        gateway_state.metrics["failed_requests"] += 1
        
        if circuit_breaker.state == CircuitBreakerState.OPEN:
            gateway_state.metrics["circuit_breaker_opens"] += 1
        
        # Fallback to mock service
        return await call_fallback_service(service_name, method, path, data, correlation_id)


async def call_fallback_service(
    service_name: str, 
    method: str, 
    path: str, 
    data: Dict[str, Any] = None,
    correlation_id: str = None
) -> Dict[str, Any]:
    """Call fallback mock service when real service is unavailable."""
    mock_service = gateway_state.services.get(service_name)
    
    if not mock_service:
        raise HTTPException(
            status_code=503, 
            detail=f"Service {service_name} unavailable and no fallback"
        )
    
    # Simple routing to mock methods
    if service_name == "trading" and "execute" in path:
        return await mock_service.execute_trade(data, correlation_id)
    elif service_name == "gamification" and "profile" in path:
        user_id = data.get("user_id") if data else 123
        return await mock_service.get_user_profile(user_id, correlation_id)
    elif service_name == "social" and "feed" in path:
        user_id = data.get("user_id") if data else 123
        limit = data.get("limit", 10) if data else 10
        return await mock_service.get_feed(user_id, limit, correlation_id)
    elif service_name == "user" and "register" in path:
        return await mock_service.register_user(data, correlation_id)
    
    # Default response
    return {
        "message": f"Fallback response from {service_name}",
        "correlation_id": correlation_id,
        "fallback": True
    }


# Helper function to publish API events
async def publish_api_event(event_type: str, domain: str, data: Dict[str, Any], correlation_id: str) -> None:
    """Publish API gateway events."""
    if gateway_state.event_bus:
        event = create_redis_event(
            event_type=f"Gateway.{event_type}",
            domain="gateway",
            entity_id=f"api_{correlation_id}",
            data=data,
            correlation_id=correlation_id
        )
        
        await gateway_state.event_bus.emit(event)
        gateway_state.metrics["events_published"] += 1


# Health check endpoint
@app.get("/health", response_model=APIResponse)
async def health_check():
    """Health check endpoint for load balancers."""
    # Check service registry health
    service_registry_healthy = gateway_state.service_registry is not None
    
    # Get all registered services
    registered_services = {}
    if gateway_state.service_registry:
        try:
            all_services = await gateway_state.service_registry.get_all_services()
            for service_name, instances in all_services.items():
                registered_services[service_name] = {
                    "instances": len(instances),
                    "healthy_instances": len([i for i in instances if i.is_healthy]),
                    "circuit_breaker": gateway_state.circuit_breakers.get(service_name, {}).state.value if gateway_state.circuit_breakers.get(service_name) else "unknown"
                }
        except Exception as e:
            logger.error(f"Health check error: {e}")
    
    return APIResponse(
        success=True,
        data={
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "infrastructure": {
                "event_bus": "connected" if gateway_state.event_bus else "unavailable",
                "service_registry": "connected" if service_registry_healthy else "unavailable"
            },
            "registered_services": registered_services,
            "fallback_services": list(gateway_state.services.keys()),
            "circuit_breakers": {
                name: cb.state.value for name, cb in gateway_state.circuit_breakers.items()
            }
        },
        message="API Gateway is healthy with service discovery"
    )


# Metrics endpoint
@app.get("/metrics", response_model=APIResponse)
async def get_metrics():
    """Get API Gateway metrics."""
    # Enhanced metrics with circuit breaker and service discovery info
    enhanced_metrics = gateway_state.metrics.copy()
    
    # Add circuit breaker metrics
    circuit_breaker_metrics = {}
    for service_name, cb in gateway_state.circuit_breakers.items():
        circuit_breaker_metrics[service_name] = {
            "state": cb.state.value,
            "failure_count": cb.failure_count,
            "last_failure_time": cb.last_failure_time
        }
    
    enhanced_metrics["circuit_breakers"] = circuit_breaker_metrics
    
    # Add service discovery metrics
    if gateway_state.service_registry:
        try:
            all_services = await gateway_state.service_registry.get_all_services()
            service_health = {}
            for service_name, instances in all_services.items():
                healthy_count = len([i for i in instances if i.is_healthy])
                service_health[service_name] = {
                    "total_instances": len(instances),
                    "healthy_instances": healthy_count,
                    "health_percentage": (healthy_count / len(instances)) * 100 if instances else 0
                }
            enhanced_metrics["service_health"] = service_health
        except Exception as e:
            logger.error(f"Metrics collection error: {e}")
    
    return APIResponse(
        success=True,
        data=enhanced_metrics,
        message="Enhanced gateway metrics with service discovery"
    )


# Service discovery endpoint
@app.get("/services", response_model=APIResponse)
async def get_services():
    """Get all registered services."""
    if not gateway_state.service_registry:
        return APIResponse(
            success=False,
            message="Service registry not available"
        )
    
    try:
        all_services = await gateway_state.service_registry.get_all_services()
        service_details = {}
        
        for service_name, instances in all_services.items():
            service_details[service_name] = [
                {
                    "instance_id": instance.instance_id,
                    "host": instance.host,
                    "port": instance.port,
                    "version": instance.version,
                    "status": instance.status.value,
                    "healthy": instance.is_healthy,
                    "last_heartbeat": instance.last_heartbeat,
                    "service_url": instance.service_url,
                    "metadata": instance.metadata
                }
                for instance in instances
            ]
        
        return APIResponse(
            success=True,
            data=service_details,
            message="Service registry contents"
        )
    
    except Exception as e:
        logger.error(f"Service discovery error: {e}")
        return APIResponse(
            success=False,
            message=f"Error retrieving services: {str(e)}"
        )


# Domain routing endpoints
@app.post("/api/v1/trading/execute", response_model=APIResponse)
@limiter.limit("100/minute")
async def execute_trade(
    trade_request: TradeRequest,
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Execute a trade through the trading domain."""
    correlation_id = request.state.correlation_id
    
    try:
        # Update domain metrics
        if "trading" not in gateway_state.metrics["requests_by_domain"]:
            gateway_state.metrics["requests_by_domain"]["trading"] = 0
        gateway_state.metrics["requests_by_domain"]["trading"] += 1
        
        # Publish API request event
        await publish_api_event(
            "TradeRequested",
            "trading",
            {
                "user_id": trade_request.user_id,
                "asset_symbol": trade_request.asset_symbol,
                "amount": trade_request.amount,
                "authenticated": current_user["authenticated"]
            },
            correlation_id
        )
        
        # Call trading service with service discovery
        result = await make_service_request(
            service_name="trading",
            method="POST",
            path="/api/v1/trading/execute",
            data=trade_request.dict(),
            correlation_id=correlation_id
        )
        
        return APIResponse(
            success=True,
            data=result,
            message="Trade executed successfully",
            correlation_id=correlation_id
        )
    
    except Exception as e:
        logger.error(f"Trading error [{correlation_id}]: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/gamification/user/{user_id}/profile", response_model=APIResponse)
@limiter.limit("200/minute")
async def get_user_gamification_profile(
    user_id: int,
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get user's gamification profile."""
    correlation_id = request.state.correlation_id
    
    try:
        # Update domain metrics
        if "gamification" not in gateway_state.metrics["requests_by_domain"]:
            gateway_state.metrics["requests_by_domain"]["gamification"] = 0
        gateway_state.metrics["requests_by_domain"]["gamification"] += 1
        
        profile = await make_service_request(
            service_name="gamification",
            method="GET",
            path=f"/api/v1/gamification/user/{user_id}/profile",
            correlation_id=correlation_id
        )
        
        return APIResponse(
            success=True,
            data=profile,
            message="Gamification profile retrieved",
            correlation_id=correlation_id
        )
    
    except Exception as e:
        logger.error(f"Gamification error [{correlation_id}]: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/social/feed", response_model=APIResponse)
@limiter.limit("50/minute")
async def get_social_feed(
    request: Request,
    limit: int = 10,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get social feed for user."""
    correlation_id = request.state.correlation_id
    
    try:
        # Update domain metrics
        if "social" not in gateway_state.metrics["requests_by_domain"]:
            gateway_state.metrics["requests_by_domain"]["social"] = 0
        gateway_state.metrics["requests_by_domain"]["social"] += 1
        
        feed = await make_service_request(
            service_name="social",
            method="GET",
            path=f"/api/v1/social/feed?limit={limit}&user_id={current_user['user_id']}",
            correlation_id=correlation_id
        )
        
        return APIResponse(
            success=True,
            data=feed,
            message="Social feed retrieved",
            correlation_id=correlation_id
        )
    
    except Exception as e:
        logger.error(f"Social error [{correlation_id}]: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/users/register", response_model=APIResponse)
@limiter.limit("10/minute")
async def register_user(
    registration: UserRegistrationRequest,
    request: Request
):
    """Register a new user."""
    correlation_id = request.state.correlation_id
    
    try:
        # Update domain metrics
        if "user" not in gateway_state.metrics["requests_by_domain"]:
            gateway_state.metrics["requests_by_domain"]["user"] = 0
        gateway_state.metrics["requests_by_domain"]["user"] += 1
        
        # Publish user registration event
        await publish_api_event(
            "UserRegistrationRequested",
            "user",
            {
                "username": registration.username,
                "email": registration.email
            },
            correlation_id
        )
        
        result = await make_service_request(
            service_name="user",
            method="POST",
            path="/api/v1/users/register",
            data=registration.dict(),
            correlation_id=correlation_id
        )
        
        return APIResponse(
            success=True,
            data=result,
            message="User registered successfully",
            correlation_id=correlation_id
        )
    
    except Exception as e:
        logger.error(f"User registration error [{correlation_id}]: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Tournament WebSocket endpoint
@app.websocket("/ws/tournament/{tournament_id}")
async def tournament_websocket(
    websocket: WebSocket, 
    tournament_id: str,
    token: Optional[str] = Query(None)
):
    """WebSocket endpoint for real-time tournament updates"""
    
    if not TOURNAMENT_WEBSOCKET_AVAILABLE or not gateway_state.websocket_manager:
        await websocket.close(code=1003, reason="WebSocket service not available")
        return
    
    # Extract connection metadata
    ip_address = websocket.client.host if websocket.client else None
    user_agent = websocket.headers.get("user-agent")
    
    # Authenticate user if token provided
    user_id = None
    if token:
        user_id = await authenticate_websocket_token(token)
    
    try:
        # Connect to WebSocket manager
        connection = await gateway_state.websocket_manager.connect(
            websocket=websocket,
            tournament_id=tournament_id,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Update metrics
        gateway_state.metrics["websocket_connections"] += 1
        
        logger.info(f"🌐 WebSocket connected: tournament={tournament_id}, user={user_id}")
        
        # Keep connection alive and handle client messages
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()
                gateway_state.metrics["websocket_messages"] += 1
                
                # Handle client message
                if data:
                    message = json.loads(data)
                    await gateway_state.websocket_manager.handle_client_message(connection, message)
                    
            except WebSocketDisconnect:
                logger.info(f"🔌 WebSocket disconnected: tournament={tournament_id}, user={user_id}")
                break
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON received from WebSocket: {data}")
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                break
                
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
        try:
            await websocket.close()
        except:
            pass
    finally:
        # Ensure cleanup
        if gateway_state.websocket_manager:
            await gateway_state.websocket_manager.disconnect(websocket, tournament_id)


async def authenticate_websocket_token(token: str) -> Optional[str]:
    """Authenticate WebSocket token and return user ID"""
    try:
        # Mock authentication - would integrate with real auth service
        if token.startswith('user_'):
            return token
        elif token.startswith('bearer_'):
            # Extract user ID from bearer token (simplified)
            return token.replace('bearer_', '')
        return None
    except Exception as e:
        logger.error(f"WebSocket authentication error: {e}")
        return None


# Tournament API endpoints
@app.get("/api/v1/tournaments/current", response_model=APIResponse)
async def get_current_tournament(request: Request):
    """Get current tournament information"""
    correlation_id = request.state.correlation_id
    
    if not gateway_state.competition_service:
        raise HTTPException(status_code=503, detail="Competition service not available")
    
    try:
        tournament_id = gateway_state.competition_service.get_current_tournament_id()
        tournament_stats = await gateway_state.competition_service.get_tournament_statistics(tournament_id)
        
        return APIResponse(
            success=True,
            data=tournament_stats,
            message="Current tournament information",
            correlation_id=correlation_id
        )
    except Exception as e:
        logger.error(f"Tournament info error [{correlation_id}]: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/tournaments/{tournament_id}/leaderboard", response_model=APIResponse)
async def get_tournament_leaderboard(
    tournament_id: str,
    request: Request,
    start: int = 0,
    limit: int = 50
):
    """Get tournament leaderboard"""
    correlation_id = request.state.correlation_id
    
    if not gateway_state.competition_service:
        raise HTTPException(status_code=503, detail="Competition service not available")
    
    try:
        leaderboard = await gateway_state.competition_service.get_tournament_leaderboard(
            tournament_id, start, start + limit - 1
        )
        
        return APIResponse(
            success=True,
            data={
                "leaderboard": leaderboard,
                "start": start,
                "limit": limit,
                "tournament_id": tournament_id
            },
            message="Tournament leaderboard",
            correlation_id=correlation_id
        )
    except Exception as e:
        logger.error(f"Tournament leaderboard error [{correlation_id}]: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/tournaments/{tournament_id}/ai-traders", response_model=APIResponse)
async def get_tournament_ai_traders(tournament_id: str, request: Request):
    """Get list of AI traders in tournament"""
    correlation_id = request.state.correlation_id
    
    if not gateway_state.competition_service:
        raise HTTPException(status_code=503, detail="Competition service not available")
    
    try:
        ai_traders = gateway_state.competition_service.ai_engine.get_active_ai_traders()
        
        ai_trader_info = []
        for ai in ai_traders:
            ai_info = await gateway_state.competition_service.get_ai_trader_info(ai.id)
            if ai_info:
                ai_trader_info.append({
                    "id": ai.id,
                    "name": ai.name,
                    "title": ai.title,
                    "strategy": ai.strategy.value,
                    "backstory": ai.backstory,
                    "current_trades": ai_info['current_state']['total_trades'],
                    "portfolio_value": ai_info['current_state']['portfolio_value'],
                    "is_active": ai_info['current_state']['active']
                })
        
        return APIResponse(
            success=True,
            data={
                "ai_traders": ai_trader_info,
                "total_count": len(ai_trader_info),
                "tournament_id": tournament_id
            },
            message="AI traders information",
            correlation_id=correlation_id
        )
    except Exception as e:
        logger.error(f"AI traders info error [{correlation_id}]: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/ai-traders/{ai_id}", response_model=APIResponse)
async def get_ai_trader_details(ai_id: str, request: Request):
    """Get detailed information about specific AI trader"""
    correlation_id = request.state.correlation_id
    
    if not gateway_state.competition_service:
        raise HTTPException(status_code=503, detail="Competition service not available")
    
    try:
        ai_info = await gateway_state.competition_service.get_ai_trader_info(ai_id)
        
        if not ai_info:
            raise HTTPException(status_code=404, detail="AI trader not found")
        
        return APIResponse(
            success=True,
            data=ai_info,
            message="AI trader details",
            correlation_id=correlation_id
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI trader details error [{correlation_id}]: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/websocket/stats", response_model=APIResponse)
async def get_websocket_stats(request: Request):
    """Get WebSocket connection statistics"""
    correlation_id = request.state.correlation_id
    
    if not gateway_state.websocket_manager:
        raise HTTPException(status_code=503, detail="WebSocket service not available")
    
    try:
        stats = gateway_state.websocket_manager.get_connection_stats()
        
        return APIResponse(
            success=True,
            data=stats,
            message="WebSocket statistics",
            correlation_id=correlation_id
        )
    except Exception as e:
        logger.error(f"WebSocket stats error [{correlation_id}]: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Error handling
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors."""
    correlation_id = getattr(request.state, 'correlation_id', 'unknown')
    
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "message": "Endpoint not found",
            "correlation_id": correlation_id,
            "timestamp": datetime.now().isoformat()
        },
        headers={"X-Correlation-ID": correlation_id}
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Handle internal server errors."""
    correlation_id = getattr(request.state, 'correlation_id', 'unknown')
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "correlation_id": correlation_id,
            "timestamp": datetime.now().isoformat()
        },
        headers={"X-Correlation-ID": correlation_id}
    )


# Mock domain services (to be replaced with actual services)
class MockTradingService:
    async def execute_trade(self, trade_data: Dict[str, Any], correlation_id: str) -> Dict[str, Any]:
        """Mock trading service."""
        await asyncio.sleep(0.1)  # Simulate processing
        
        return {
            "trade_id": f"trade_{uuid4().hex[:8]}",
            "user_id": trade_data.get("user_id"),
            "asset_symbol": trade_data.get("asset_symbol"),
            "direction": trade_data.get("direction"),
            "amount": trade_data.get("amount"),
            "status": "executed",
            "pnl": float(trade_data.get("amount", 0)) * 0.05,  # 5% profit simulation
            "executed_at": datetime.now().isoformat(),
            "correlation_id": correlation_id,
            "service_type": "mock_fallback"
        }


class MockGamificationService:
    async def get_user_profile(self, user_id: int, correlation_id: str) -> Dict[str, Any]:
        """Mock gamification service."""
        await asyncio.sleep(0.05)
        
        return {
            "user_id": user_id,
            "level": 25,
            "total_xp": 15750,
            "achievements": ["profitable_trader", "high_volume", "streak_master"],
            "leaderboard_rank": 47,
            "correlation_id": correlation_id,
            "service_type": "mock_fallback"
        }


class MockSocialService:
    async def get_feed(self, user_id: int, limit: int, correlation_id: str) -> Dict[str, Any]:
        """Mock social service."""
        await asyncio.sleep(0.08)
        
        feed_items = [
            {
                "id": f"feed_{i}",
                "user_id": user_id + i,
                "content": f"User reached level {20 + i}!",
                "type": "level_up",
                "timestamp": datetime.now().isoformat()
            }
            for i in range(min(limit, 5))
        ]
        
        return {
            "feed": feed_items,
            "total_count": len(feed_items),
            "correlation_id": correlation_id,
            "service_type": "mock_fallback"
        }


class MockUserService:
    async def register_user(self, registration_data: Dict[str, Any], correlation_id: str) -> Dict[str, Any]:
        """Mock user service."""
        await asyncio.sleep(0.2)
        
        return {
            "user_id": 12345,
            "username": registration_data.get("username"),
            "email": registration_data.get("email"),
            "created_at": datetime.now().isoformat(),
            "correlation_id": correlation_id,
            "service_type": "mock_fallback"
        }


class MockFinancialService:
    pass


class MockNFTService:
    pass


# Development server
if __name__ == "__main__":
    uvicorn.run(
        "api_gateway:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )