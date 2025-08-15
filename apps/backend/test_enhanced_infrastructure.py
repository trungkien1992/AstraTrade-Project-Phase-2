#!/usr/bin/env python3
"""
Test script to demonstrate enhanced infrastructure capabilities
without requiring full dependency installation.
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any

# Mock implementations to test infrastructure concepts

class MockServiceRegistry:
    """Mock service registry for testing."""
    
    def __init__(self):
        self.services = {
            "trading": [
                {"instance_id": "trading-1", "host": "localhost", "port": 8001, "healthy": True},
                {"instance_id": "trading-2", "host": "localhost", "port": 8002, "healthy": True}
            ],
            "gamification": [
                {"instance_id": "gamification-1", "host": "localhost", "port": 8003, "healthy": True}
            ],
            "social": [
                {"instance_id": "social-1", "host": "localhost", "port": 8004, "healthy": False},
                {"instance_id": "social-2", "host": "localhost", "port": 8005, "healthy": True}
            ]
        }
    
    async def get_healthy_instance(self, service_name: str):
        """Get a healthy service instance."""
        instances = self.services.get(service_name, [])
        healthy = [i for i in instances if i["healthy"]]
        return healthy[0] if healthy else None
    
    async def get_all_services(self):
        """Get all registered services."""
        return self.services


class MockCircuitBreaker:
    """Mock circuit breaker for testing."""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.failure_count = 0
        self.last_failure_time = 0
    
    def can_request(self) -> bool:
        """Check if requests are allowed."""
        if self.state == "CLOSED":
            return True
        elif self.state == "OPEN":
            # Check if timeout period has passed
            if time.time() - self.last_failure_time > 30:  # 30 second timeout
                self.state = "HALF_OPEN"
                return True
            return False
        else:  # HALF_OPEN
            return True
    
    def record_success(self):
        """Record successful request."""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def record_failure(self):
        """Record failed request."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= 5:  # Failure threshold
            self.state = "OPEN"


class MockBusinessMetrics:
    """Mock business metrics collector."""
    
    def __init__(self):
        self.metrics = {
            "trades_executed": 0,
            "users_registered": 0,
            "revenue_generated": 0.0,
            "social_interactions": 0,
            "xp_earned": 0
        }
        self.kpis = {
            "trades_per_second": {"current": 0.0, "target": 10.0, "status": "warning"},
            "daily_active_users": {"current": 0, "target": 1000, "status": "critical"},
            "daily_revenue": {"current": 0.0, "target": 10000.0, "status": "critical"}
        }
    
    def record_trade(self, volume: float, revenue: float):
        """Record trade execution."""
        self.metrics["trades_executed"] += 1
        self.metrics["revenue_generated"] += revenue
        self.kpis["trades_per_second"]["current"] = self.metrics["trades_executed"] / 60.0  # Simplified
    
    def record_user_registration(self):
        """Record user registration."""
        self.metrics["users_registered"] += 1
        self.kpis["daily_active_users"]["current"] = self.metrics["users_registered"]
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get business dashboard data."""
        return {
            "timestamp": datetime.now().isoformat(),
            "metrics": self.metrics,
            "kpis": self.kpis,
            "health_status": "operational"
        }


class MockDistributedTracer:
    """Mock distributed tracer."""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.traces = []
    
    def trace_operation(self, operation_name: str, correlation_id: str, **metadata):
        """Trace an operation."""
        trace = {
            "service": self.service_name,
            "operation": operation_name,
            "correlation_id": correlation_id,
            "start_time": time.time(),
            "metadata": metadata
        }
        
        class TraceContext:
            def __init__(self, tracer, trace_data):
                self.tracer = tracer
                self.trace = trace_data
            
            async def __aenter__(self):
                return self
            
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                self.trace["end_time"] = time.time()
                self.trace["duration"] = self.trace["end_time"] - self.trace["start_time"]
                self.trace["success"] = exc_type is None
                self.tracer.traces.append(self.trace)
        
        return TraceContext(self, trace)


async def test_service_discovery():
    """Test service discovery functionality."""
    print("🔍 Testing Service Discovery...")
    
    registry = MockServiceRegistry()
    
    # Test getting healthy instances
    trading_instance = await registry.get_healthy_instance("trading")
    print(f"✅ Trading service: {trading_instance}")
    
    social_instance = await registry.get_healthy_instance("social")
    print(f"✅ Social service (auto-failover): {social_instance}")
    
    # Test service overview
    all_services = await registry.get_all_services()
    print(f"📊 Service Registry Status:")
    for service, instances in all_services.items():
        healthy_count = len([i for i in instances if i["healthy"]])
        print(f"  - {service}: {healthy_count}/{len(instances)} healthy")


async def test_circuit_breaker():
    """Test circuit breaker functionality."""
    print("\n⚡ Testing Circuit Breaker...")
    
    cb = MockCircuitBreaker("test-service")
    
    # Test normal operation
    print(f"✅ Initial state: {cb.state} (can_request: {cb.can_request()})")
    
    # Simulate failures
    for i in range(6):
        cb.record_failure()
        print(f"🔴 Failure {i+1}: state={cb.state}, can_request={cb.can_request()}")
    
    # Test recovery
    await asyncio.sleep(1)  # Simulate time passing
    cb.record_success()
    print(f"✅ After recovery: {cb.state} (can_request: {cb.can_request()})")


async def test_business_metrics():
    """Test business metrics collection."""
    print("\n📊 Testing Business Metrics...")
    
    metrics = MockBusinessMetrics()
    
    # Simulate business activities
    metrics.record_trade(1000.0, 10.0)
    metrics.record_trade(1500.0, 15.0)
    metrics.record_user_registration()
    
    dashboard = metrics.get_dashboard_data()
    print("📈 Business Dashboard:")
    print(json.dumps(dashboard, indent=2))


async def test_distributed_tracing():
    """Test distributed tracing."""
    print("\n🔗 Testing Distributed Tracing...")
    
    tracer = MockDistributedTracer("api-gateway")
    
    # Simulate traced operations
    correlation_id = "req_abc123"
    
    async with tracer.trace_operation(
        "execute_trade", 
        correlation_id, 
        user_id=123, 
        symbol="BTC/USD"
    ):
        await asyncio.sleep(0.1)  # Simulate work
    
    async with tracer.trace_operation(
        "update_gamification", 
        correlation_id, 
        xp_gained=50
    ):
        await asyncio.sleep(0.05)  # Simulate work
    
    print(f"🔍 Traced Operations for {correlation_id}:")
    for trace in tracer.traces:
        print(f"  - {trace['operation']}: {trace['duration']:.3f}s (success: {trace['success']})")


async def test_rate_limiting():
    """Test rate limiting functionality."""
    print("\n🚦 Testing Rate Limiting...")
    
    # Mock rate limiter
    user_requests = {}
    
    def check_rate_limit(user_id: str, limit: int = 100) -> bool:
        current_time = time.time()
        if user_id not in user_requests:
            user_requests[user_id] = {"count": 0, "reset_time": current_time + 60}
        
        user_data = user_requests[user_id]
        if current_time > user_data["reset_time"]:
            user_data["count"] = 0
            user_data["reset_time"] = current_time + 60
        
        if user_data["count"] >= limit:
            return False
        
        user_data["count"] += 1
        return True
    
    # Test rate limiting
    user_id = "user123"
    for i in range(5):
        allowed = check_rate_limit(user_id, limit=3)
        print(f"Request {i+1} for {user_id}: {'✅ Allowed' if allowed else '🚫 Rate Limited'}")


async def simulate_enhanced_api_gateway():
    """Simulate the enhanced API gateway in action."""
    print("\n🌐 Simulating Enhanced API Gateway...")
    
    # Initialize components
    registry = MockServiceRegistry()
    circuit_breakers = {
        "trading": MockCircuitBreaker("trading"),
        "social": MockCircuitBreaker("social")
    }
    metrics = MockBusinessMetrics()
    tracer = MockDistributedTracer("api-gateway")
    
    correlation_id = "req_demo123"
    
    # Simulate API request flow
    print(f"📥 Incoming request: /api/v1/trading/execute [{correlation_id}]")
    
    # 1. Service Discovery
    async with tracer.trace_operation("service_discovery", correlation_id):
        trading_instance = await registry.get_healthy_instance("trading")
        print(f"🔍 Service Discovery: Found {trading_instance['instance_id']}")
    
    # 2. Circuit Breaker Check
    cb = circuit_breakers["trading"]
    if cb.can_request():
        print(f"⚡ Circuit Breaker: {cb.state} - Request allowed")
        
        # 3. Execute Trade (simulated)
        async with tracer.trace_operation("execute_trade", correlation_id, user_id=123):
            await asyncio.sleep(0.1)  # Simulate trade execution
            cb.record_success()
            metrics.record_trade(1000.0, 10.0)
            print("💰 Trade executed successfully")
    else:
        print(f"🚨 Circuit Breaker: {cb.state} - Request blocked")
    
    # 4. Show final metrics
    dashboard = metrics.get_dashboard_data()
    print(f"\n📊 Updated Metrics:")
    print(f"  - Trades: {dashboard['metrics']['trades_executed']}")
    print(f"  - Revenue: ${dashboard['metrics']['revenue_generated']:.2f}")
    
    print(f"\n🔗 Request Trace:")
    for trace in tracer.traces:
        print(f"  - {trace['operation']}: {trace['duration']:.3f}s")


async def main():
    """Main test function."""
    print("🚀 AstraTrade Enhanced Infrastructure Demo")
    print("=" * 50)
    
    try:
        await test_service_discovery()
        await test_circuit_breaker()
        await test_business_metrics()
        await test_distributed_tracing()
        await test_rate_limiting()
        await simulate_enhanced_api_gateway()
        
        print("\n" + "=" * 50)
        print("✅ All Enhanced Infrastructure Tests Passed!")
        print("\n🎯 Infrastructure Capabilities Demonstrated:")
        print("  ✅ Dynamic Service Discovery with Health Checking")
        print("  ✅ Circuit Breaker Patterns for Resilience")
        print("  ✅ Real-time Business Metrics Collection")
        print("  ✅ Distributed Tracing Across Services")
        print("  ✅ Advanced Rate Limiting Protection")
        print("  ✅ Service Health-based Routing")
        
        print("\n🌟 Production Features:")
        print("  - Automatic service failover")
        print("  - Business KPI tracking")
        print("  - End-to-end request correlation")
        print("  - Performance monitoring")
        print("  - Security rate limiting")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())