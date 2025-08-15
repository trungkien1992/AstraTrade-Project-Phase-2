#!/usr/bin/env python3
"""
Simplified Enhanced API Gateway for Testing Deployment
Focuses on core enhanced features without problematic dependencies.
"""

import asyncio
import time
import json
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import uuid4

# Use only core dependencies that should work
try:
    from fastapi import FastAPI, HTTPException, Request, Response
    from fastapi.responses import JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    print("❌ FastAPI not available")

# Try Redis connection
try:
    import redis
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    redis_client.ping()
    REDIS_AVAILABLE = True
    print("✅ Redis connection successful")
except:
    REDIS_AVAILABLE = False
    print("⚠️ Redis not available - using mock service registry")

from collections import defaultdict
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("simple-gateway")

class CircuitBreakerState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class MockServiceRegistry:
    """Simplified service registry for testing."""
    
    def __init__(self):
        self.services = {
            "trading": {"host": "localhost", "port": 8001, "healthy": True},
            "gamification": {"host": "localhost", "port": 8002, "healthy": True},
            "social": {"host": "localhost", "port": 8003, "healthy": True},
            "user": {"host": "localhost", "port": 8004, "healthy": True},
        }
    
    async def get_service(self, service_name: str):
        return self.services.get(service_name)
    
    async def register_service(self, service_name: str, host: str, port: int):
        self.services[service_name] = {"host": host, "port": port, "healthy": True}
        logger.info(f"✅ Registered service: {service_name} at {host}:{port}")

class MockCircuitBreaker:
    """Simplified circuit breaker for testing."""
    
    def __init__(self):
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        
    def can_request(self) -> bool:
        return self.state != CircuitBreakerState.OPEN
    
    def record_success(self):
        self.failure_count = 0
        self.state = CircuitBreakerState.CLOSED
    
    def record_failure(self):
        self.failure_count += 1
        if self.failure_count >= 3:  # Lower threshold for testing
            self.state = CircuitBreakerState.OPEN

class MockBusinessMetrics:
    """Simplified business metrics for testing."""
    
    def __init__(self):
        self.metrics = {
            "requests_total": 0,
            "trades_executed": 0,
            "users_active": 0,
            "revenue_generated": 0.0
        }
        self.start_time = time.time()
    
    def record_request(self):
        self.metrics["requests_total"] += 1
    
    def record_trade(self, amount: float):
        self.metrics["trades_executed"] += 1
        self.metrics["revenue_generated"] += amount * 0.001  # 0.1% fee
    
    def get_dashboard_data(self):
        uptime = time.time() - self.start_time
        return {
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": round(uptime, 2),
            "metrics": self.metrics,
            "kpis": {
                "requests_per_second": round(self.metrics["requests_total"] / max(uptime, 1), 2),
                "revenue_per_trade": round(self.metrics["revenue_generated"] / max(self.metrics["trades_executed"], 1), 4)
            },
            "status": "operational"
        }

class MockRateLimiter:
    """Simplified rate limiter for testing."""
    
    def __init__(self):
        self.requests = defaultdict(list)
    
    def check_limit(self, user_id: str, limit: int = 100) -> bool:
        now = time.time()
        # Clean old requests (older than 60 seconds)
        self.requests[user_id] = [req_time for req_time in self.requests[user_id] if now - req_time < 60]
        
        if len(self.requests[user_id]) >= limit:
            return False
        
        self.requests[user_id].append(now)
        return True

# Global state
if not FASTAPI_AVAILABLE:
    print("❌ Cannot start gateway - FastAPI not available")
    exit(1)

app = FastAPI(
    title="AstraTrade Enhanced API Gateway (Simplified)",
    description="Testing deployment of enhanced infrastructure features",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
service_registry = MockServiceRegistry()
circuit_breakers = {
    "trading": MockCircuitBreaker(),
    "gamification": MockCircuitBreaker(),
    "social": MockCircuitBreaker(),
    "user": MockCircuitBreaker()
}
business_metrics = MockBusinessMetrics()
rate_limiter = MockRateLimiter()

# Middleware for request tracking
@app.middleware("http")
async def request_tracking_middleware(request: Request, call_next):
    start_time = time.time()
    correlation_id = request.headers.get("X-Correlation-ID", f"req_{uuid4().hex[:12]}")
    
    # Rate limiting check
    user_id = request.headers.get("X-User-ID", request.client.host if request.client else "unknown")
    if not rate_limiter.check_limit(user_id, limit=50):  # Lower limit for testing
        return JSONResponse(
            status_code=429,
            content={
                "success": False,
                "message": "Rate limit exceeded",
                "correlation_id": correlation_id
            }
        )
    
    # Record request
    business_metrics.record_request()
    
    # Process request
    response = await call_next(request)
    
    # Add headers
    response.headers["X-Correlation-ID"] = correlation_id
    response.headers["X-Processing-Time"] = f"{time.time() - start_time:.3f}s"
    
    processing_time = time.time() - start_time
    logger.info(f"📥 {request.method} {request.url.path} [{correlation_id}] - {response.status_code} - {processing_time:.3f}s")
    
    return response

# Health check endpoint
@app.get("/health")
async def health_check():
    """Enhanced health check with service discovery."""
    redis_status = "connected" if REDIS_AVAILABLE else "unavailable"
    
    services_status = {}
    for service_name, cb in circuit_breakers.items():
        services_status[service_name] = {
            "circuit_breaker": cb.state.value,
            "failure_count": cb.failure_count
        }
    
    return {
        "success": True,
        "timestamp": datetime.now().isoformat(),
        "status": "healthy",
        "infrastructure": {
            "redis": redis_status,
            "service_registry": "operational"
        },
        "services": services_status,
        "message": "Enhanced API Gateway operational"
    }

# Service discovery endpoint
@app.get("/services")
async def get_services():
    """Get all registered services."""
    return {
        "success": True,
        "timestamp": datetime.now().isoformat(),
        "services": service_registry.services,
        "message": "Service registry contents"
    }

# Business dashboard endpoint
@app.get("/dashboard")
async def get_dashboard():
    """Get business metrics dashboard."""
    return {
        "success": True,
        "data": business_metrics.get_dashboard_data(),
        "message": "Business metrics dashboard"
    }

# Metrics endpoint
@app.get("/metrics")
async def get_metrics():
    """Get infrastructure metrics."""
    circuit_breaker_status = {name: cb.state.value for name, cb in circuit_breakers.items()}
    
    return {
        "success": True,
        "timestamp": datetime.now().isoformat(),
        "metrics": business_metrics.metrics,
        "circuit_breakers": circuit_breaker_status,
        "rate_limiting": {
            "active_users": len(rate_limiter.requests),
            "total_tracked_requests": sum(len(reqs) for reqs in rate_limiter.requests.values())
        },
        "message": "Enhanced infrastructure metrics"
    }

# Mock trading endpoint
@app.post("/api/v1/trading/execute")
async def execute_trade(request: Request):
    """Mock trading execution with enhanced features."""
    correlation_id = request.headers.get("X-Correlation-ID", "unknown")
    
    # Check circuit breaker
    cb = circuit_breakers["trading"]
    if not cb.can_request():
        logger.warning(f"🚨 Circuit breaker OPEN for trading service [{correlation_id}]")
        return JSONResponse(
            status_code=503,
            content={
                "success": False,
                "message": "Trading service temporarily unavailable",
                "correlation_id": correlation_id,
                "circuit_breaker_state": cb.state.value
            }
        )
    
    try:
        # Simulate trade execution
        await asyncio.sleep(0.1)  # Simulate processing time
        
        # Record success
        cb.record_success()
        business_metrics.record_trade(1000.0)  # Mock $1000 trade
        
        trade_id = f"trade_{uuid4().hex[:8]}"
        
        logger.info(f"💰 Trade executed: {trade_id} [{correlation_id}]")
        
        return {
            "success": True,
            "data": {
                "trade_id": trade_id,
                "status": "executed",
                "amount": 1000.0,
                "fee": 1.0,
                "executed_at": datetime.now().isoformat(),
                "service_type": "enhanced_gateway"
            },
            "correlation_id": correlation_id,
            "message": "Trade executed successfully with enhanced features"
        }
    
    except Exception as e:
        cb.record_failure()
        logger.error(f"❌ Trade execution failed [{correlation_id}]: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Test circuit breaker endpoint
@app.post("/test/circuit-breaker/{service_name}")
async def test_circuit_breaker(service_name: str):
    """Test circuit breaker functionality."""
    if service_name not in circuit_breakers:
        raise HTTPException(status_code=404, detail="Service not found")
    
    cb = circuit_breakers[service_name]
    
    # Simulate failures to trigger circuit breaker
    for i in range(4):
        cb.record_failure()
    
    return {
        "success": True,
        "message": f"Circuit breaker for {service_name} triggered",
        "state": cb.state.value,
        "failure_count": cb.failure_count
    }

# Test rate limiting endpoint
@app.get("/test/rate-limit")
async def test_rate_limit(request: Request):
    """Test rate limiting functionality."""
    user_id = request.headers.get("X-User-ID", "test-user")
    
    # Make 60 requests quickly to test rate limiting
    results = []
    for i in range(60):
        allowed = rate_limiter.check_limit(user_id, limit=10)  # Low limit for testing
        results.append({"request": i+1, "allowed": allowed})
        if not allowed:
            break
    
    return {
        "success": True,
        "user_id": user_id,
        "test_results": results,
        "message": "Rate limiting test completed"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with enhanced gateway information."""
    return {
        "success": True,
        "message": "🚀 AstraTrade Enhanced API Gateway (Simplified)",
        "version": "1.0.0",
        "features": [
            "Service Discovery",
            "Circuit Breakers",
            "Rate Limiting", 
            "Business Metrics",
            "Request Correlation",
            "Health Monitoring"
        ],
        "endpoints": {
            "health": "/health",
            "services": "/services",
            "dashboard": "/dashboard",
            "metrics": "/metrics",
            "trading": "/api/v1/trading/execute"
        },
        "timestamp": datetime.now().isoformat()
    }

# Admin endpoint to reset circuit breakers
@app.post("/admin/circuit-breaker/reset/{service}")
async def reset_circuit_breaker(service: str):
    """Reset circuit breaker for a specific service."""
    if service not in circuit_breakers:
        raise HTTPException(status_code=404, detail=f"Service '{service}' not found")
    
    circuit_breakers[service].record_success()  # This resets failure count and closes circuit
    
    return {
        "success": True,
        "message": f"Circuit breaker reset for {service}",
        "service": service,
        "new_state": circuit_breakers[service].state.value,
        "failure_count": circuit_breakers[service].failure_count,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("🚀 Starting AstraTrade Enhanced API Gateway (Simplified)")
    print("✅ Service Discovery: Mock registry operational")
    print("✅ Circuit Breakers: 4 services protected")
    print("✅ Rate Limiting: Per-user protection active")
    print("✅ Business Metrics: Real-time collection enabled")
    print("✅ Request Correlation: Full tracing operational")
    print(f"✅ Redis: {'Connected' if REDIS_AVAILABLE else 'Mock mode'}")
    print("🌐 Starting server on http://localhost:8000")
    
    uvicorn.run(
        "simple_gateway:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )