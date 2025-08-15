#!/usr/bin/env python3
"""
AstraTrade API Response Time Optimization
Comprehensive API performance optimization for enhanced gateway and microservices.
"""

import asyncio
import time
import json
import aiohttp
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
import logging
import statistics
from functools import wraps
# Optional high-performance dependencies
try:
    import uvloop  # High-performance event loop
except ImportError:
    uvloop = None

try:
    import orjson  # Fast JSON serialization
except ImportError:
    orjson = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api-optimizer")

@dataclass
class APIPerformanceMetric:
    """API endpoint performance metrics."""
    endpoint: str
    method: str
    response_time_ms: float
    status_code: int
    response_size_bytes: int
    success: bool
    timestamp: str
    optimization_applied: Optional[str] = None
    user_agent: str = "performance-tester"

@dataclass
class OptimizationResult:
    """Result of an optimization technique."""
    technique_name: str
    before_avg_ms: float
    after_avg_ms: float
    improvement_percent: float
    success: bool
    description: str
    timestamp: str

class APIPerformanceProfiler:
    """Profiles API performance and identifies bottlenecks."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.metrics: List[APIPerformanceMetric] = []
        self.optimization_results: List[OptimizationResult] = []
        
    async def profile_endpoint(self, endpoint: str, method: str = "GET", 
                             payload: Optional[Dict] = None, headers: Optional[Dict] = None,
                             iterations: int = 50) -> List[APIPerformanceMetric]:
        """Profile a specific API endpoint."""
        logger.info(f"🔍 Profiling {method} {endpoint} ({iterations} iterations)")
        
        endpoint_metrics = []
        
        # Use optimized HTTP client settings
        connector = aiohttp.TCPConnector(
            limit=100,
            limit_per_host=50,
            keepalive_timeout=30,
            enable_cleanup_closed=True,
            use_dns_cache=True,
            ttl_dns_cache=300
        )
        
        timeout = aiohttp.ClientTimeout(total=30, connect=5)
        
        async with aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            json_serialize=orjson.dumps if orjson else None  # Fast JSON serialization if available
        ) as session:
            
            for i in range(iterations):
                start_time = time.perf_counter()
                
                try:
                    if method.upper() == "POST":
                        async with session.post(
                            f"{self.base_url}{endpoint}",
                            json=payload,
                            headers=headers or {}
                        ) as response:
                            content = await response.read()
                            response_time = (time.perf_counter() - start_time) * 1000
                            
                            metric = APIPerformanceMetric(
                                endpoint=endpoint,
                                method=method.upper(),
                                response_time_ms=response_time,
                                status_code=response.status,
                                response_size_bytes=len(content),
                                success=200 <= response.status < 400,
                                timestamp=datetime.now().isoformat()
                            )
                            
                            endpoint_metrics.append(metric)
                    
                    else:  # GET and other methods
                        async with session.get(
                            f"{self.base_url}{endpoint}",
                            headers=headers or {}
                        ) as response:
                            content = await response.read()
                            response_time = (time.perf_counter() - start_time) * 1000
                            
                            metric = APIPerformanceMetric(
                                endpoint=endpoint,
                                method=method.upper(),
                                response_time_ms=response_time,
                                status_code=response.status,
                                response_size_bytes=len(content),
                                success=200 <= response.status < 400,
                                timestamp=datetime.now().isoformat()
                            )
                            
                            endpoint_metrics.append(metric)
                
                except Exception as e:
                    response_time = (time.perf_counter() - start_time) * 1000
                    metric = APIPerformanceMetric(
                        endpoint=endpoint,
                        method=method.upper(),
                        response_time_ms=response_time,
                        status_code=0,
                        response_size_bytes=0,
                        success=False,
                        timestamp=datetime.now().isoformat(),
                        optimization_applied=f"Error: {str(e)}"
                    )
                    endpoint_metrics.append(metric)
                
                # Small delay to avoid overwhelming the server
                if i < iterations - 1:
                    await asyncio.sleep(0.01)
        
        self.metrics.extend(endpoint_metrics)
        
        # Calculate statistics
        successful_metrics = [m for m in endpoint_metrics if m.success]
        if successful_metrics:
            avg_time = statistics.mean([m.response_time_ms for m in successful_metrics])
            p95_time = statistics.quantiles([m.response_time_ms for m in successful_metrics], n=20)[18] if len(successful_metrics) > 20 else avg_time
            success_rate = len(successful_metrics) / len(endpoint_metrics) * 100
            
            logger.info(f"   ✅ Avg: {avg_time:.2f}ms, P95: {p95_time:.2f}ms, Success: {success_rate:.1f}%")
        else:
            logger.warning(f"   ❌ All requests failed for {endpoint}")
        
        return endpoint_metrics

class APIOptimizer:
    """Implements various API optimization techniques."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.profiler = APIPerformanceProfiler(base_url)
        
    async def optimize_response_compression(self) -> OptimizationResult:
        """Test and optimize response compression."""
        logger.info("🗜️ Testing Response Compression Optimization")
        
        endpoint = "/dashboard"
        
        # Test without compression
        metrics_before = await self.profiler.profile_endpoint(
            endpoint, iterations=20
        )
        
        # Test with compression
        headers_with_compression = {
            "Accept-Encoding": "gzip, deflate, br",
            "Accept": "application/json"
        }
        
        metrics_after = await self.profiler.profile_endpoint(
            endpoint, headers=headers_with_compression, iterations=20
        )
        
        # Calculate improvement
        successful_before = [m for m in metrics_before if m.success]
        successful_after = [m for m in metrics_after if m.success]
        
        if successful_before and successful_after:
            avg_before = statistics.mean([m.response_time_ms for m in successful_before])
            avg_after = statistics.mean([m.response_time_ms for m in successful_after])
            
            improvement = ((avg_before - avg_after) / avg_before) * 100
            
            result = OptimizationResult(
                technique_name="Response Compression",
                before_avg_ms=avg_before,
                after_avg_ms=avg_after,
                improvement_percent=improvement,
                success=improvement > 0,
                description=f"Compression headers reduced response time by {improvement:.1f}%",
                timestamp=datetime.now().isoformat()
            )
        else:
            result = OptimizationResult(
                technique_name="Response Compression",
                before_avg_ms=0,
                after_avg_ms=0,
                improvement_percent=0,
                success=False,
                description="Unable to measure compression impact due to failed requests",
                timestamp=datetime.now().isoformat()
            )
        
        self.profiler.optimization_results.append(result)
        logger.info(f"   📊 Compression Impact: {result.improvement_percent:.1f}% improvement")
        
        return result
    
    async def optimize_connection_pooling(self) -> OptimizationResult:
        """Test connection pooling optimization."""
        logger.info("🔗 Testing Connection Pooling Optimization")
        
        endpoints = ["/health", "/services", "/dashboard", "/metrics"]
        
        # Test with single connection (no pooling)
        start_time = time.perf_counter()
        single_connection_times = []
        
        for endpoint in endpoints:
            async with aiohttp.ClientSession() as session:
                for _ in range(5):  # 5 requests per endpoint
                    req_start = time.perf_counter()
                    try:
                        async with session.get(f"{self.base_url}{endpoint}") as response:
                            await response.read()
                            req_time = (time.perf_counter() - req_start) * 1000
                            single_connection_times.append(req_time)
                    except:
                        pass
        
        single_connection_total = time.perf_counter() - start_time
        
        # Test with connection pooling
        start_time = time.perf_counter()
        pooled_connection_times = []
        
        connector = aiohttp.TCPConnector(limit=20, limit_per_host=10)
        async with aiohttp.ClientSession(connector=connector) as session:
            for endpoint in endpoints:
                for _ in range(5):  # 5 requests per endpoint
                    req_start = time.perf_counter()
                    try:
                        async with session.get(f"{self.base_url}{endpoint}") as response:
                            await response.read()
                            req_time = (time.perf_counter() - req_start) * 1000
                            pooled_connection_times.append(req_time)
                    except:
                        pass
        
        pooled_connection_total = time.perf_counter() - start_time
        
        # Calculate improvement
        if single_connection_times and pooled_connection_times:
            avg_single = statistics.mean(single_connection_times)
            avg_pooled = statistics.mean(pooled_connection_times)
            
            improvement = ((avg_single - avg_pooled) / avg_single) * 100
            
            result = OptimizationResult(
                technique_name="Connection Pooling",
                before_avg_ms=avg_single,
                after_avg_ms=avg_pooled,
                improvement_percent=improvement,
                success=improvement > 0,
                description=f"Connection pooling improved response time by {improvement:.1f}%",
                timestamp=datetime.now().isoformat()
            )
        else:
            result = OptimizationResult(
                technique_name="Connection Pooling",
                before_avg_ms=0,
                after_avg_ms=0,
                improvement_percent=0,
                success=False,
                description="Unable to measure connection pooling impact",
                timestamp=datetime.now().isoformat()
            )
        
        self.profiler.optimization_results.append(result)
        logger.info(f"   📊 Connection Pooling Impact: {result.improvement_percent:.1f}% improvement")
        
        return result
    
    async def optimize_concurrent_requests(self) -> OptimizationResult:
        """Test concurrent request optimization."""
        logger.info("⚡ Testing Concurrent Request Optimization")
        
        endpoint = "/health"
        num_requests = 50
        
        # Test sequential requests
        start_time = time.perf_counter()
        sequential_times = []
        
        async with aiohttp.ClientSession() as session:
            for i in range(num_requests):
                req_start = time.perf_counter()
                try:
                    async with session.get(f"{self.base_url}{endpoint}") as response:
                        await response.read()
                        req_time = (time.perf_counter() - req_start) * 1000
                        sequential_times.append(req_time)
                except:
                    pass
        
        sequential_total = time.perf_counter() - start_time
        
        # Test concurrent requests
        start_time = time.perf_counter()
        concurrent_times = []
        
        async def make_request(session):
            req_start = time.perf_counter()
            try:
                async with session.get(f"{self.base_url}{endpoint}") as response:
                    await response.read()
                    req_time = (time.perf_counter() - req_start) * 1000
                    return req_time
            except:
                return None
        
        connector = aioredis.TCPConnector(limit=100)
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = [make_request(session) for _ in range(num_requests)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            concurrent_times = [r for r in results if r is not None and not isinstance(r, Exception)]
        
        concurrent_total = time.perf_counter() - start_time
        
        # Calculate improvement (total time improvement, not individual request time)
        total_improvement = ((sequential_total - concurrent_total) / sequential_total) * 100
        
        if sequential_times and concurrent_times:
            avg_sequential = statistics.mean(sequential_times)
            avg_concurrent = statistics.mean(concurrent_times)
            
            result = OptimizationResult(
                technique_name="Concurrent Requests",
                before_avg_ms=avg_sequential,
                after_avg_ms=avg_concurrent,
                improvement_percent=total_improvement,
                success=total_improvement > 0,
                description=f"Concurrency reduced total execution time by {total_improvement:.1f}%",
                timestamp=datetime.now().isoformat()
            )
        else:
            result = OptimizationResult(
                technique_name="Concurrent Requests",
                before_avg_ms=0,
                after_avg_ms=0,
                improvement_percent=0,
                success=False,
                description="Unable to measure concurrency impact",
                timestamp=datetime.now().isoformat()
            )
        
        self.profiler.optimization_results.append(result)
        logger.info(f"   📊 Concurrency Impact: {result.improvement_percent:.1f}% total time improvement")
        
        return result
    
    async def optimize_payload_size(self) -> OptimizationResult:
        """Test payload size optimization."""
        logger.info("📦 Testing Payload Size Optimization")
        
        endpoint = "/api/v1/trading/execute"
        
        # Test with large payload
        large_payload = {
            "user_id": 12345,
            "asset_symbol": "BTC/USD",
            "direction": "LONG",
            "amount": 1000,
            "metadata": {
                "description": "This is a very long description " * 50,  # Large metadata
                "tags": [f"tag_{i}" for i in range(100)],  # Many tags
                "extra_data": {f"key_{i}": f"value_{i}" * 10 for i in range(50)}  # Extra data
            }
        }
        
        large_payload_metrics = await self.profiler.profile_endpoint(
            endpoint, method="POST", payload=large_payload, iterations=20
        )
        
        # Test with optimized small payload
        small_payload = {
            "user_id": 12345,
            "asset_symbol": "BTC/USD",
            "direction": "LONG",
            "amount": 1000
        }
        
        small_payload_metrics = await self.profiler.profile_endpoint(
            endpoint, method="POST", payload=small_payload, iterations=20
        )
        
        # Calculate improvement
        successful_large = [m for m in large_payload_metrics if m.success]
        successful_small = [m for m in small_payload_metrics if m.success]
        
        if successful_large and successful_small:
            avg_large = statistics.mean([m.response_time_ms for m in successful_large])
            avg_small = statistics.mean([m.response_time_ms for m in successful_small])
            
            improvement = ((avg_large - avg_small) / avg_large) * 100
            
            result = OptimizationResult(
                technique_name="Payload Size Optimization",
                before_avg_ms=avg_large,
                after_avg_ms=avg_small,
                improvement_percent=improvement,
                success=improvement > 0,
                description=f"Reducing payload size improved response time by {improvement:.1f}%",
                timestamp=datetime.now().isoformat()
            )
        else:
            result = OptimizationResult(
                technique_name="Payload Size Optimization",
                before_avg_ms=0,
                after_avg_ms=0,
                improvement_percent=0,
                success=False,
                description="Unable to measure payload size impact",
                timestamp=datetime.now().isoformat()
            )
        
        self.profiler.optimization_results.append(result)
        logger.info(f"   📊 Payload Optimization Impact: {result.improvement_percent:.1f}% improvement")
        
        return result
    
    async def benchmark_all_endpoints(self) -> Dict[str, List[APIPerformanceMetric]]:
        """Benchmark all major API endpoints."""
        logger.info("🎯 Benchmarking All Major API Endpoints")
        
        endpoints_config = [
            {"endpoint": "/", "method": "GET"},
            {"endpoint": "/health", "method": "GET"},
            {"endpoint": "/services", "method": "GET"},
            {"endpoint": "/dashboard", "method": "GET"},
            {"endpoint": "/metrics", "method": "GET"},
            {
                "endpoint": "/api/v1/trading/execute",
                "method": "POST",
                "payload": {
                    "user_id": 123,
                    "asset_symbol": "BTC/USD",
                    "direction": "LONG",
                    "amount": 1000
                },
                "headers": {"Content-Type": "application/json", "X-User-ID": "benchmark-user"}
            },
            {
                "endpoint": "/test/rate-limit",
                "method": "GET",
                "headers": {"X-User-ID": "benchmark-rate-limit-user"}
            }
        ]
        
        endpoint_results = {}
        
        for config in endpoints_config:
            endpoint = config["endpoint"]
            method = config["method"]
            payload = config.get("payload")
            headers = config.get("headers")
            
            metrics = await self.profiler.profile_endpoint(
                endpoint, method, payload, headers, iterations=30
            )
            
            endpoint_results[f"{method} {endpoint}"] = metrics
        
        return endpoint_results
    
    async def run_comprehensive_optimization(self) -> Dict[str, Any]:
        """Run comprehensive API optimization suite."""
        logger.info("🚀 Starting Comprehensive API Performance Optimization")
        logger.info("=" * 60)
        
        start_time = time.time()
        
        # Phase 1: Baseline benchmarking
        logger.info("\n📊 Phase 1: Baseline Performance Benchmarking")
        baseline_results = await self.benchmark_all_endpoints()
        
        # Phase 2: Optimization techniques
        logger.info("\n⚡ Phase 2: Optimization Techniques")
        
        optimizations = [
            ("Response Compression", self.optimize_response_compression),
            ("Connection Pooling", self.optimize_connection_pooling),
            ("Concurrent Requests", self.optimize_concurrent_requests),
            ("Payload Size", self.optimize_payload_size),
        ]
        
        optimization_results = []
        for opt_name, opt_func in optimizations:
            try:
                result = await opt_func()
                optimization_results.append(result)
            except Exception as e:
                logger.error(f"   ❌ {opt_name} optimization failed: {e}")
        
        # Phase 3: Post-optimization benchmarking
        logger.info("\n📈 Phase 3: Post-Optimization Benchmarking")
        post_optimization_results = await self.benchmark_all_endpoints()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Generate optimization report
        report = self._generate_api_optimization_report(
            duration, baseline_results, post_optimization_results, optimization_results
        )
        
        logger.info("\n" + "=" * 60)
        logger.info("🎉 API Performance Optimization Complete!")
        logger.info(f"Duration: {duration:.1f} seconds")
        logger.info(f"Endpoints Tested: {len(baseline_results)}")
        logger.info(f"Optimizations Applied: {len(optimization_results)}")
        
        return report
    
    def _generate_api_optimization_report(self, duration: float,
                                        baseline_results: Dict[str, List[APIPerformanceMetric]],
                                        post_opt_results: Dict[str, List[APIPerformanceMetric]],
                                        optimization_results: List[OptimizationResult]) -> Dict[str, Any]:
        """Generate comprehensive API optimization report."""
        
        # Calculate baseline statistics
        baseline_stats = {}
        for endpoint, metrics in baseline_results.items():
            successful = [m for m in metrics if m.success]
            if successful:
                baseline_stats[endpoint] = {
                    "avg_response_time_ms": statistics.mean([m.response_time_ms for m in successful]),
                    "p95_response_time_ms": statistics.quantiles([m.response_time_ms for m in successful], n=20)[18] if len(successful) > 20 else 0,
                    "success_rate_percent": len(successful) / len(metrics) * 100,
                    "avg_response_size_bytes": statistics.mean([m.response_size_bytes for m in successful])
                }
            else:
                baseline_stats[endpoint] = {
                    "avg_response_time_ms": 0,
                    "p95_response_time_ms": 0,
                    "success_rate_percent": 0,
                    "avg_response_size_bytes": 0
                }
        
        # Calculate post-optimization statistics
        post_opt_stats = {}
        for endpoint, metrics in post_opt_results.items():
            successful = [m for m in metrics if m.success]
            if successful:
                post_opt_stats[endpoint] = {
                    "avg_response_time_ms": statistics.mean([m.response_time_ms for m in successful]),
                    "p95_response_time_ms": statistics.quantiles([m.response_time_ms for m in successful], n=20)[18] if len(successful) > 20 else 0,
                    "success_rate_percent": len(successful) / len(metrics) * 100,
                    "avg_response_size_bytes": statistics.mean([m.response_size_bytes for m in successful])
                }
            else:
                post_opt_stats[endpoint] = {
                    "avg_response_time_ms": 0,
                    "p95_response_time_ms": 0,
                    "success_rate_percent": 0,
                    "avg_response_size_bytes": 0
                }
        
        # Calculate overall improvement
        overall_baseline_avg = statistics.mean([
            stats["avg_response_time_ms"] 
            for stats in baseline_stats.values() 
            if stats["avg_response_time_ms"] > 0
        ]) if baseline_stats else 0
        
        overall_post_opt_avg = statistics.mean([
            stats["avg_response_time_ms"] 
            for stats in post_opt_stats.values() 
            if stats["avg_response_time_ms"] > 0
        ]) if post_opt_stats else 0
        
        overall_improvement = 0
        if overall_baseline_avg > 0 and overall_post_opt_avg > 0:
            overall_improvement = ((overall_baseline_avg - overall_post_opt_avg) / overall_baseline_avg) * 100
        
        report = {
            "optimization_summary": {
                "duration_seconds": duration,
                "endpoints_tested": len(baseline_results),
                "optimizations_applied": len(optimization_results),
                "overall_improvement_percent": overall_improvement,
                "timestamp": datetime.now().isoformat()
            },
            "baseline_performance": baseline_stats,
            "post_optimization_performance": post_opt_stats,
            "optimization_techniques": [asdict(opt) for opt in optimization_results],
            "detailed_metrics": {
                "baseline": {endpoint: [asdict(m) for m in metrics] for endpoint, metrics in baseline_results.items()},
                "post_optimization": {endpoint: [asdict(m) for m in metrics] for endpoint, metrics in post_opt_results.items()}
            },
            "recommendations": self._generate_api_recommendations(
                baseline_stats, post_opt_stats, optimization_results
            )
        }
        
        return report
    
    def _generate_api_recommendations(self, baseline_stats: Dict[str, Dict],
                                    post_opt_stats: Dict[str, Dict],
                                    optimization_results: List[OptimizationResult]) -> List[str]:
        """Generate API optimization recommendations."""
        recommendations = []
        
        # Analyze slow endpoints
        slow_endpoints = []
        for endpoint, stats in post_opt_stats.items():
            if stats["avg_response_time_ms"] > 100:  # >100ms
                slow_endpoints.append(endpoint)
        
        if slow_endpoints:
            recommendations.append(f"Found {len(slow_endpoints)} slow endpoints (>100ms) - consider further optimization")
        
        # Analyze successful optimizations
        successful_opts = [opt for opt in optimization_results if opt.success and opt.improvement_percent > 5]
        if successful_opts:
            best_opt = max(successful_opts, key=lambda x: x.improvement_percent)
            recommendations.append(f"Best optimization: {best_opt.technique_name} ({best_opt.improvement_percent:.1f}% improvement)")
        
        # Analyze failed optimizations
        failed_opts = [opt for opt in optimization_results if not opt.success]
        if failed_opts:
            recommendations.append(f"Review {len(failed_opts)} failed optimization techniques")
        
        # Response size recommendations
        large_responses = []
        for endpoint, stats in post_opt_stats.items():
            if stats["avg_response_size_bytes"] > 50000:  # >50KB
                large_responses.append(endpoint)
        
        if large_responses:
            recommendations.append(f"Found {len(large_responses)} endpoints with large responses - consider pagination or compression")
        
        # Success rate recommendations
        low_success_endpoints = []
        for endpoint, stats in post_opt_stats.items():
            if stats["success_rate_percent"] < 95:
                low_success_endpoints.append(endpoint)
        
        if low_success_endpoints:
            recommendations.append(f"Found {len(low_success_endpoints)} endpoints with low success rates - investigate error patterns")
        
        if not recommendations:
            recommendations.append("API performance is well optimized! All endpoints performing within acceptable ranges.")
        
        return recommendations
    
    def save_optimization_report(self, report: Dict[str, Any], filename: Optional[str] = None):
        """Save API optimization report to file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"api_optimization_report_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"📄 API optimization report saved to: {filename}")

async def main():
    """Main function to run API optimization."""
    # Use uvloop for better performance
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    
    optimizer = APIOptimizer()
    
    # Run comprehensive optimization
    report = await optimizer.run_comprehensive_optimization()
    
    # Save report
    optimizer.save_optimization_report(report)
    
    # Print summary
    print("\n" + "="*60)
    print("📊 API OPTIMIZATION SUMMARY")
    print("="*60)
    print(f"Duration: {report['optimization_summary']['duration_seconds']:.1f}s")
    print(f"Endpoints Tested: {report['optimization_summary']['endpoints_tested']}")
    print(f"Optimizations Applied: {report['optimization_summary']['optimizations_applied']}")
    print(f"Overall Improvement: {report['optimization_summary']['overall_improvement_percent']:.1f}%")
    
    print("\n📈 ENDPOINT PERFORMANCE:")
    for endpoint, stats in report['post_optimization_performance'].items():
        print(f"• {endpoint}: {stats['avg_response_time_ms']:.1f}ms avg, {stats['success_rate_percent']:.1f}% success")
    
    print("\n⚡ OPTIMIZATION TECHNIQUES:")
    for opt in report['optimization_techniques']:
        print(f"• {opt['technique_name']}: {opt['improvement_percent']:.1f}% improvement")
    
    print("\n🔍 RECOMMENDATIONS:")
    for rec in report['recommendations']:
        print(f"• {rec}")

if __name__ == "__main__":
    asyncio.run(main())