#!/usr/bin/env python3
"""
AstraTrade Performance Load Testing Framework
Comprehensive load testing for all microservices and infrastructure components.
"""

import asyncio
import aiohttp
import time
import json
import statistics
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import psutil
import redis
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("load-tester")

@dataclass
class LoadTestResult:
    """Result of a load test scenario."""
    scenario_name: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    p95_response_time: float
    p99_response_time: float
    requests_per_second: float
    error_rate: float
    start_time: str
    end_time: str
    duration_seconds: float
    errors: List[str]

@dataclass
class SystemMetrics:
    """System resource metrics during load test."""
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    redis_memory_mb: float
    active_connections: int
    timestamp: str

class LoadTestScenario:
    """Individual load test scenario configuration."""
    
    def __init__(self, name: str, endpoint: str, method: str = "GET", 
                 payload: Optional[Dict] = None, headers: Optional[Dict] = None,
                 concurrent_users: int = 10, requests_per_user: int = 100,
                 ramp_up_seconds: int = 5):
        self.name = name
        self.endpoint = endpoint
        self.method = method
        self.payload = payload or {}
        self.headers = headers or {}
        self.concurrent_users = concurrent_users
        self.requests_per_user = requests_per_user
        self.ramp_up_seconds = ramp_up_seconds

class AstraTradeLoadTester:
    """Comprehensive load testing framework for AstraTrade infrastructure."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.redis_client = None
        self.system_metrics: List[SystemMetrics] = []
        self.test_results: List[LoadTestResult] = []
        
        # Initialize Redis connection for monitoring
        try:
            self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
            self.redis_client.ping()
            logger.info("✅ Redis connection established for monitoring")
        except Exception as e:
            logger.warning(f"⚠️ Redis monitoring unavailable: {e}")
    
    async def execute_request(self, session: aiohttp.ClientSession, scenario: LoadTestScenario) -> Dict[str, Any]:
        """Execute a single HTTP request and measure performance."""
        start_time = time.time()
        
        try:
            if scenario.method.upper() == "POST":
                async with session.post(
                    f"{self.base_url}{scenario.endpoint}",
                    json=scenario.payload,
                    headers=scenario.headers
                ) as response:
                    response_time = time.time() - start_time
                    content = await response.text()
                    return {
                        "success": True,
                        "status_code": response.status,
                        "response_time": response_time,
                        "content_length": len(content),
                        "error": None
                    }
            else:
                async with session.get(
                    f"{self.base_url}{scenario.endpoint}",
                    headers=scenario.headers
                ) as response:
                    response_time = time.time() - start_time
                    content = await response.text()
                    return {
                        "success": True,
                        "status_code": response.status,
                        "response_time": response_time,
                        "content_length": len(content),
                        "error": None
                    }
        
        except Exception as e:
            response_time = time.time() - start_time
            return {
                "success": False,
                "status_code": 0,
                "response_time": response_time,
                "content_length": 0,
                "error": str(e)
            }
    
    async def user_simulation(self, session: aiohttp.ClientSession, scenario: LoadTestScenario, user_id: int) -> List[Dict[str, Any]]:
        """Simulate a single user making multiple requests."""
        results = []
        
        # Stagger user start times for ramp-up
        delay = (scenario.ramp_up_seconds / scenario.concurrent_users) * user_id
        await asyncio.sleep(delay)
        
        for request_num in range(scenario.requests_per_user):
            result = await self.execute_request(session, scenario)
            result["user_id"] = user_id
            result["request_num"] = request_num
            results.append(result)
            
            # Small delay between requests to simulate realistic usage
            await asyncio.sleep(0.01)
        
        return results
    
    def collect_system_metrics(self) -> SystemMetrics:
        """Collect current system resource metrics."""
        try:
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            
            redis_memory_mb = 0
            active_connections = 0
            if self.redis_client:
                try:
                    redis_info = self.redis_client.info()
                    redis_memory_mb = redis_info.get('used_memory', 0) / (1024 * 1024)
                    active_connections = redis_info.get('connected_clients', 0)
                except:
                    pass
            
            return SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_mb=memory.used / (1024 * 1024),
                redis_memory_mb=redis_memory_mb,
                active_connections=active_connections,
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            logger.warning(f"Failed to collect system metrics: {e}")
            return SystemMetrics(0, 0, 0, 0, 0, datetime.now().isoformat())
    
    async def run_scenario(self, scenario: LoadTestScenario) -> LoadTestResult:
        """Execute a complete load test scenario."""
        logger.info(f"🚀 Starting load test: {scenario.name}")
        logger.info(f"   Concurrent Users: {scenario.concurrent_users}")
        logger.info(f"   Requests per User: {scenario.requests_per_user}")
        logger.info(f"   Total Requests: {scenario.concurrent_users * scenario.requests_per_user}")
        
        start_time = time.time()
        start_timestamp = datetime.now().isoformat()
        
        # Start system metrics collection
        metrics_task = asyncio.create_task(self.monitor_system_metrics())
        
        # Create HTTP session with connection pooling
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=50)
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            # Create tasks for all users
            user_tasks = []
            for user_id in range(scenario.concurrent_users):
                task = self.user_simulation(session, scenario, user_id)
                user_tasks.append(task)
            
            # Execute all user simulations concurrently
            user_results = await asyncio.gather(*user_tasks, return_exceptions=True)
        
        # Stop metrics collection
        metrics_task.cancel()
        
        end_time = time.time()
        end_timestamp = datetime.now().isoformat()
        duration = end_time - start_time
        
        # Aggregate results
        all_results = []
        errors = []
        
        for user_result in user_results:
            if isinstance(user_result, Exception):
                errors.append(f"User simulation failed: {user_result}")
            else:
                all_results.extend(user_result)
        
        # Calculate statistics
        successful_requests = sum(1 for r in all_results if r["success"])
        failed_requests = len(all_results) - successful_requests
        
        response_times = [r["response_time"] for r in all_results if r["success"]]
        
        avg_response_time = statistics.mean(response_times) if response_times else 0
        p95_response_time = statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else 0
        p99_response_time = statistics.quantiles(response_times, n=100)[98] if len(response_times) > 100 else 0
        
        requests_per_second = len(all_results) / duration if duration > 0 else 0
        error_rate = (failed_requests / len(all_results)) * 100 if all_results else 0
        
        # Collect errors
        for result in all_results:
            if not result["success"] and result["error"]:
                errors.append(f"HTTP {result['status_code']}: {result['error']}")
        
        result = LoadTestResult(
            scenario_name=scenario.name,
            total_requests=len(all_results),
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            avg_response_time=avg_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            requests_per_second=requests_per_second,
            error_rate=error_rate,
            start_time=start_timestamp,
            end_time=end_timestamp,
            duration_seconds=duration,
            errors=list(set(errors))  # Remove duplicates
        )
        
        self.test_results.append(result)
        
        logger.info(f"✅ Completed: {scenario.name}")
        logger.info(f"   Total Requests: {result.total_requests}")
        logger.info(f"   Success Rate: {((result.successful_requests / result.total_requests) * 100):.1f}%")
        logger.info(f"   Avg Response Time: {result.avg_response_time:.3f}s")
        logger.info(f"   P95 Response Time: {result.p95_response_time:.3f}s")
        logger.info(f"   Requests/Second: {result.requests_per_second:.1f}")
        
        return result
    
    async def monitor_system_metrics(self):
        """Continuously monitor system metrics during load tests."""
        try:
            while True:
                metrics = self.collect_system_metrics()
                self.system_metrics.append(metrics)
                await asyncio.sleep(1)  # Collect metrics every second
        except asyncio.CancelledError:
            pass
    
    def get_predefined_scenarios(self) -> List[LoadTestScenario]:
        """Get predefined load test scenarios for AstraTrade."""
        return [
            # Basic connectivity tests
            LoadTestScenario(
                name="Gateway Health Check",
                endpoint="/health",
                concurrent_users=50,
                requests_per_user=20,
                ramp_up_seconds=5
            ),
            
            LoadTestScenario(
                name="Service Discovery Load",
                endpoint="/services",
                concurrent_users=25,
                requests_per_user=40,
                ramp_up_seconds=3
            ),
            
            # Business metrics dashboard
            LoadTestScenario(
                name="Business Dashboard Load",
                endpoint="/dashboard",
                concurrent_users=30,
                requests_per_user=30,
                ramp_up_seconds=5
            ),
            
            # Trading simulation
            LoadTestScenario(
                name="Trading Execution Load",
                endpoint="/api/v1/trading/execute",
                method="POST",
                payload={
                    "user_id": 12345,
                    "asset_symbol": "BTC/USD",
                    "direction": "LONG",
                    "amount": 1000
                },
                headers={"Content-Type": "application/json", "X-User-ID": "load-test-user"},
                concurrent_users=20,
                requests_per_user=50,
                ramp_up_seconds=10
            ),
            
            # High-concurrency stress test
            LoadTestScenario(
                name="High Concurrency Stress Test",
                endpoint="/health",
                concurrent_users=100,
                requests_per_user=100,
                ramp_up_seconds=15
            ),
            
            # Rate limiting validation
            LoadTestScenario(
                name="Rate Limiting Validation",
                endpoint="/test/rate-limit",
                headers={"X-User-ID": "rate-limit-test-user"},
                concurrent_users=5,
                requests_per_user=200,
                ramp_up_seconds=2
            )
        ]
    
    async def run_comprehensive_load_test(self) -> Dict[str, Any]:
        """Run all predefined load test scenarios."""
        logger.info("🧪 Starting Comprehensive AstraTrade Load Test Suite")
        logger.info("=" * 60)
        
        test_start_time = time.time()
        scenarios = self.get_predefined_scenarios()
        
        # Run each scenario
        for i, scenario in enumerate(scenarios, 1):
            logger.info(f"\n📊 Scenario {i}/{len(scenarios)}: {scenario.name}")
            await self.run_scenario(scenario)
            
            # Brief pause between scenarios
            if i < len(scenarios):
                logger.info("⏳ Cooling down for 5 seconds...")
                await asyncio.sleep(5)
        
        test_end_time = time.time()
        total_duration = test_end_time - test_start_time
        
        # Generate comprehensive report
        report = self.generate_load_test_report(total_duration)
        
        logger.info("\n" + "=" * 60)
        logger.info("🎉 Comprehensive Load Test Complete!")
        logger.info(f"Total Duration: {total_duration:.1f} seconds")
        logger.info(f"Scenarios Executed: {len(self.test_results)}")
        
        return report
    
    def generate_load_test_report(self, total_duration: float) -> Dict[str, Any]:
        """Generate comprehensive load test report."""
        total_requests = sum(r.total_requests for r in self.test_results)
        total_successful = sum(r.successful_requests for r in self.test_results)
        total_failed = sum(r.failed_requests for r in self.test_results)
        
        overall_success_rate = (total_successful / total_requests) * 100 if total_requests > 0 else 0
        overall_rps = total_requests / total_duration if total_duration > 0 else 0
        
        # Calculate system resource averages
        avg_cpu = statistics.mean([m.cpu_percent for m in self.system_metrics]) if self.system_metrics else 0
        avg_memory = statistics.mean([m.memory_percent for m in self.system_metrics]) if self.system_metrics else 0
        max_redis_memory = max([m.redis_memory_mb for m in self.system_metrics]) if self.system_metrics else 0
        
        report = {
            "summary": {
                "total_duration_seconds": total_duration,
                "total_requests": total_requests,
                "successful_requests": total_successful,
                "failed_requests": total_failed,
                "overall_success_rate": overall_success_rate,
                "overall_requests_per_second": overall_rps,
                "scenarios_executed": len(self.test_results)
            },
            "performance_metrics": {
                "avg_cpu_percent": avg_cpu,
                "avg_memory_percent": avg_memory,
                "max_redis_memory_mb": max_redis_memory,
                "metrics_collected": len(self.system_metrics)
            },
            "scenario_results": [asdict(result) for result in self.test_results],
            "system_metrics": [asdict(metric) for metric in self.system_metrics[-10:]],  # Last 10 samples
            "recommendations": self.generate_recommendations()
        }
        
        return report
    
    def generate_recommendations(self) -> List[str]:
        """Generate performance optimization recommendations based on test results."""
        recommendations = []
        
        # Analyze response times
        avg_response_times = [r.avg_response_time for r in self.test_results]
        p95_response_times = [r.p95_response_time for r in self.test_results]
        
        if any(rt > 0.1 for rt in avg_response_times):  # >100ms
            recommendations.append("Consider API response time optimization - some endpoints exceed 100ms")
        
        if any(rt > 0.2 for rt in p95_response_times):  # >200ms P95
            recommendations.append("P95 response times exceed 200ms - investigate slow queries and optimize")
        
        # Analyze error rates
        high_error_scenarios = [r for r in self.test_results if r.error_rate > 5.0]
        if high_error_scenarios:
            recommendations.append(f"High error rates detected in {len(high_error_scenarios)} scenarios - investigate failure patterns")
        
        # Analyze system resources
        if self.system_metrics:
            avg_cpu = statistics.mean([m.cpu_percent for m in self.system_metrics])
            avg_memory = statistics.mean([m.memory_percent for m in self.system_metrics])
            
            if avg_cpu > 80:
                recommendations.append("High CPU utilization detected - consider horizontal scaling")
            
            if avg_memory > 80:
                recommendations.append("High memory usage detected - optimize memory consumption")
        
        # Analyze throughput
        rps_values = [r.requests_per_second for r in self.test_results]
        max_rps = max(rps_values) if rps_values else 0
        
        if max_rps < 100:
            recommendations.append("Low throughput detected - consider connection pooling and async optimization")
        
        if not recommendations:
            recommendations.append("Performance looks good! System is handling load effectively.")
        
        return recommendations
    
    def save_report(self, report: Dict[str, Any], filename: Optional[str] = None):
        """Save load test report to file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"load_test_report_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"📄 Load test report saved to: {filename}")

async def main():
    """Main function to run load tests."""
    tester = AstraTradeLoadTester()
    
    # Run comprehensive load test
    report = await tester.run_comprehensive_load_test()
    
    # Save report
    tester.save_report(report)
    
    # Print summary
    print("\n" + "="*60)
    print("📊 LOAD TEST SUMMARY")
    print("="*60)
    print(f"Total Requests: {report['summary']['total_requests']}")
    print(f"Success Rate: {report['summary']['overall_success_rate']:.1f}%")
    print(f"Overall RPS: {report['summary']['overall_requests_per_second']:.1f}")
    print(f"Duration: {report['summary']['total_duration_seconds']:.1f}s")
    print(f"Avg CPU: {report['performance_metrics']['avg_cpu_percent']:.1f}%")
    print(f"Avg Memory: {report['performance_metrics']['avg_memory_percent']:.1f}%")
    
    print("\n🔍 RECOMMENDATIONS:")
    for rec in report['recommendations']:
        print(f"• {rec}")

if __name__ == "__main__":
    asyncio.run(main())