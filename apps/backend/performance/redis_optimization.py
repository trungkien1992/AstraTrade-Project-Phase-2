#!/usr/bin/env python3
"""
AstraTrade Redis Performance Optimization
Comprehensive Redis performance tuning for event bus and caching systems.
"""

import asyncio
import time
import json
import redis
import redis.asyncio as aioredis
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import logging
import psutil
import statistics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("redis-optimizer")

@dataclass
class RedisPerformanceMetric:
    """Redis operation performance metrics."""
    operation_name: str
    operation_type: str  # 'read', 'write', 'stream', 'pubsub'
    execution_time_ms: float
    data_size_bytes: int
    success: bool
    timestamp: str
    optimization_applied: Optional[str] = None

@dataclass
class RedisMemoryMetrics:
    """Redis memory usage metrics."""
    used_memory_mb: float
    used_memory_peak_mb: float
    used_memory_rss_mb: float
    memory_fragmentation_ratio: float
    expired_keys: int
    evicted_keys: int
    keyspace_hits: int
    keyspace_misses: int
    hit_rate_percent: float
    timestamp: str

@dataclass
class RedisStreamMetrics:
    """Redis Streams specific metrics."""
    stream_name: str
    length: int
    consumer_groups: int
    pending_messages: int
    last_generated_id: str
    memory_usage_bytes: int
    throughput_msgs_per_sec: float
    timestamp: str

class RedisOptimizer:
    """Redis performance optimization and monitoring."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_client = None
        self.async_redis_client = None
        self.performance_metrics: List[RedisPerformanceMetric] = []
        self.memory_metrics: List[RedisMemoryMetrics] = []
        self.stream_metrics: List[RedisStreamMetrics] = []
        
    async def initialize(self):
        """Initialize Redis connections with optimized settings."""
        logger.info("🔧 Initializing optimized Redis connections...")
        
        # Sync Redis client with optimized settings
        # Create connection pool with optimized settings
        pool = redis.ConnectionPool.from_url(
            self.redis_url,
            max_connections=50,
            retry_on_timeout=True,
            socket_keepalive=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            health_check_interval=30
        )
        self.redis_client = redis.Redis(
            connection_pool=pool,
            decode_responses=True
        )
        
        # Async Redis client
        self.async_redis_client = aioredis.Redis.from_url(
            self.redis_url,
            decode_responses=True,
            max_connections=50
        )
        
        # Test connections
        await self._test_connections()
        logger.info("✅ Redis connections initialized with optimizations")
    
    async def _test_connections(self):
        """Test Redis connections."""
        try:
            # Test sync connection
            self.redis_client.ping()
            
            # Test async connection
            await self.async_redis_client.ping()
            
            logger.info("✅ Redis connection tests passed")
        except Exception as e:
            logger.error(f"❌ Redis connection test failed: {e}")
            raise
    
    async def benchmark_redis_operations(self) -> List[RedisPerformanceMetric]:
        """Benchmark various Redis operations."""
        logger.info("🏃‍♂️ Benchmarking Redis operations...")
        
        benchmarks = [
            ("String SET", self._benchmark_string_set),
            ("String GET", self._benchmark_string_get),
            ("Hash Operations", self._benchmark_hash_operations),
            ("List Operations", self._benchmark_list_operations),
            ("Set Operations", self._benchmark_set_operations),
            ("Sorted Set Operations", self._benchmark_sorted_set_operations),
            ("Stream Operations", self._benchmark_stream_operations),
            ("Pipeline Operations", self._benchmark_pipeline_operations),
        ]
        
        benchmark_results = []
        
        for benchmark_name, benchmark_func in benchmarks:
            logger.info(f"   Running: {benchmark_name}")
            try:
                metrics = await benchmark_func()
                benchmark_results.extend(metrics)
            except Exception as e:
                logger.error(f"   ❌ {benchmark_name} failed: {e}")
        
        return benchmark_results
    
    async def _benchmark_string_set(self) -> List[RedisPerformanceMetric]:
        """Benchmark string SET operations."""
        metrics = []
        
        # Single SET operations
        for i in range(100):
            start_time = time.time()
            key = f"benchmark:string:{i}"
            value = f"test_value_{i}" * 10  # ~100 bytes
            
            try:
                await self.async_redis_client.set(key, value, ex=300)  # 5min expiry
                execution_time = (time.time() - start_time) * 1000
                
                metrics.append(RedisPerformanceMetric(
                    operation_name=f"String SET {i}",
                    operation_type="write",
                    execution_time_ms=execution_time,
                    data_size_bytes=len(value.encode()),
                    success=True,
                    timestamp=datetime.now().isoformat()
                ))
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                metrics.append(RedisPerformanceMetric(
                    operation_name=f"String SET {i}",
                    operation_type="write",
                    execution_time_ms=execution_time,
                    data_size_bytes=len(value.encode()),
                    success=False,
                    timestamp=datetime.now().isoformat(),
                    optimization_applied=f"Error: {str(e)}"
                ))
        
        return metrics
    
    async def _benchmark_string_get(self) -> List[RedisPerformanceMetric]:
        """Benchmark string GET operations."""
        metrics = []
        
        # GET operations on previously set keys
        for i in range(100):
            start_time = time.time()
            key = f"benchmark:string:{i}"
            
            try:
                value = await self.async_redis_client.get(key)
                execution_time = (time.time() - start_time) * 1000
                data_size = len(value.encode()) if value else 0
                
                metrics.append(RedisPerformanceMetric(
                    operation_name=f"String GET {i}",
                    operation_type="read",
                    execution_time_ms=execution_time,
                    data_size_bytes=data_size,
                    success=value is not None,
                    timestamp=datetime.now().isoformat()
                ))
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                metrics.append(RedisPerformanceMetric(
                    operation_name=f"String GET {i}",
                    operation_type="read",
                    execution_time_ms=execution_time,
                    data_size_bytes=0,
                    success=False,
                    timestamp=datetime.now().isoformat(),
                    optimization_applied=f"Error: {str(e)}"
                ))
        
        return metrics
    
    async def _benchmark_hash_operations(self) -> List[RedisPerformanceMetric]:
        """Benchmark hash operations."""
        metrics = []
        hash_key = "benchmark:hash:user_profile"
        
        # HSET operations
        for i in range(50):
            start_time = time.time()
            field = f"field_{i}"
            value = f"value_{i}" * 5
            
            try:
                await self.async_redis_client.hset(hash_key, field, value)
                execution_time = (time.time() - start_time) * 1000
                
                metrics.append(RedisPerformanceMetric(
                    operation_name=f"Hash HSET {i}",
                    operation_type="write",
                    execution_time_ms=execution_time,
                    data_size_bytes=len(value.encode()),
                    success=True,
                    timestamp=datetime.now().isoformat()
                ))
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                metrics.append(RedisPerformanceMetric(
                    operation_name=f"Hash HSET {i}",
                    operation_type="write",
                    execution_time_ms=execution_time,
                    data_size_bytes=len(value.encode()),
                    success=False,
                    timestamp=datetime.now().isoformat(),
                    optimization_applied=f"Error: {str(e)}"
                ))
        
        # HGETALL operation
        start_time = time.time()
        try:
            all_data = await self.async_redis_client.hgetall(hash_key)
            execution_time = (time.time() - start_time) * 1000
            data_size = sum(len(str(k).encode()) + len(str(v).encode()) for k, v in all_data.items())
            
            metrics.append(RedisPerformanceMetric(
                operation_name="Hash HGETALL",
                operation_type="read",
                execution_time_ms=execution_time,
                data_size_bytes=data_size,
                success=True,
                timestamp=datetime.now().isoformat()
            ))
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            metrics.append(RedisPerformanceMetric(
                operation_name="Hash HGETALL",
                operation_type="read",
                execution_time_ms=execution_time,
                data_size_bytes=0,
                success=False,
                timestamp=datetime.now().isoformat(),
                optimization_applied=f"Error: {str(e)}"
            ))
        
        return metrics
    
    async def _benchmark_list_operations(self) -> List[RedisPerformanceMetric]:
        """Benchmark list operations."""
        metrics = []
        list_key = "benchmark:list:recent_trades"
        
        # LPUSH operations
        for i in range(100):
            start_time = time.time()
            value = json.dumps({
                "trade_id": f"trade_{i}",
                "user_id": 123,
                "amount": 1000 + i,
                "timestamp": datetime.now().isoformat()
            })
            
            try:
                await self.async_redis_client.lpush(list_key, value)
                execution_time = (time.time() - start_time) * 1000
                
                metrics.append(RedisPerformanceMetric(
                    operation_name=f"List LPUSH {i}",
                    operation_type="write",
                    execution_time_ms=execution_time,
                    data_size_bytes=len(value.encode()),
                    success=True,
                    timestamp=datetime.now().isoformat()
                ))
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                metrics.append(RedisPerformanceMetric(
                    operation_name=f"List LPUSH {i}",
                    operation_type="write",
                    execution_time_ms=execution_time,
                    data_size_bytes=len(value.encode()),
                    success=False,
                    timestamp=datetime.now().isoformat(),
                    optimization_applied=f"Error: {str(e)}"
                ))
        
        # LRANGE operation
        start_time = time.time()
        try:
            recent_trades = await self.async_redis_client.lrange(list_key, 0, 19)  # Get 20 most recent
            execution_time = (time.time() - start_time) * 1000
            data_size = sum(len(trade.encode()) for trade in recent_trades)
            
            metrics.append(RedisPerformanceMetric(
                operation_name="List LRANGE (0, 19)",
                operation_type="read",
                execution_time_ms=execution_time,
                data_size_bytes=data_size,
                success=True,
                timestamp=datetime.now().isoformat()
            ))
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            metrics.append(RedisPerformanceMetric(
                operation_name="List LRANGE (0, 19)",
                operation_type="read",
                execution_time_ms=execution_time,
                data_size_bytes=0,
                success=False,
                timestamp=datetime.now().isoformat(),
                optimization_applied=f"Error: {str(e)}"
            ))
        
        return metrics
    
    async def _benchmark_set_operations(self) -> List[RedisPerformanceMetric]:
        """Benchmark set operations."""
        metrics = []
        set_key = "benchmark:set:active_users"
        
        # SADD operations
        for i in range(100):
            start_time = time.time()
            member = f"user_{i}"
            
            try:
                await self.async_redis_client.sadd(set_key, member)
                execution_time = (time.time() - start_time) * 1000
                
                metrics.append(RedisPerformanceMetric(
                    operation_name=f"Set SADD {i}",
                    operation_type="write",
                    execution_time_ms=execution_time,
                    data_size_bytes=len(member.encode()),
                    success=True,
                    timestamp=datetime.now().isoformat()
                ))
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                metrics.append(RedisPerformanceMetric(
                    operation_name=f"Set SADD {i}",
                    operation_type="write",
                    execution_time_ms=execution_time,
                    data_size_bytes=len(member.encode()),
                    success=False,
                    timestamp=datetime.now().isoformat(),
                    optimization_applied=f"Error: {str(e)}"
                ))
        
        return metrics
    
    async def _benchmark_sorted_set_operations(self) -> List[RedisPerformanceMetric]:
        """Benchmark sorted set operations (leaderboards)."""
        metrics = []
        zset_key = "benchmark:zset:leaderboard"
        
        # ZADD operations
        for i in range(100):
            start_time = time.time()
            member = f"user_{i}"
            score = 1000 + i * 10
            
            try:
                await self.async_redis_client.zadd(zset_key, {member: score})
                execution_time = (time.time() - start_time) * 1000
                
                metrics.append(RedisPerformanceMetric(
                    operation_name=f"ZSet ZADD {i}",
                    operation_type="write",
                    execution_time_ms=execution_time,
                    data_size_bytes=len(member.encode()) + 8,  # member + score
                    success=True,
                    timestamp=datetime.now().isoformat()
                ))
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                metrics.append(RedisPerformanceMetric(
                    operation_name=f"ZSet ZADD {i}",
                    operation_type="write",
                    execution_time_ms=execution_time,
                    data_size_bytes=len(member.encode()) + 8,
                    success=False,
                    timestamp=datetime.now().isoformat(),
                    optimization_applied=f"Error: {str(e)}"
                ))
        
        # ZREVRANGE operation (leaderboard)
        start_time = time.time()
        try:
            top_users = await self.async_redis_client.zrevrange(zset_key, 0, 9, withscores=True)
            execution_time = (time.time() - start_time) * 1000
            data_size = sum(len(str(user).encode()) + 8 for user, score in top_users)
            
            metrics.append(RedisPerformanceMetric(
                operation_name="ZSet ZREVRANGE (top 10)",
                operation_type="read",
                execution_time_ms=execution_time,
                data_size_bytes=data_size,
                success=True,
                timestamp=datetime.now().isoformat()
            ))
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            metrics.append(RedisPerformanceMetric(
                operation_name="ZSet ZREVRANGE (top 10)",
                operation_type="read",
                execution_time_ms=execution_time,
                data_size_bytes=0,
                success=False,
                timestamp=datetime.now().isoformat(),
                optimization_applied=f"Error: {str(e)}"
            ))
        
        return metrics
    
    async def _benchmark_stream_operations(self) -> List[RedisPerformanceMetric]:
        """Benchmark Redis Streams operations."""
        metrics = []
        stream_key = "benchmark:stream:events"
        
        # XADD operations
        for i in range(50):
            start_time = time.time()
            event_data = {
                "event_type": "trade_executed",
                "user_id": str(123 + i),
                "trade_id": f"trade_{i}",
                "amount": str(1000 + i),
                "timestamp": datetime.now().isoformat()
            }
            
            try:
                message_id = await self.async_redis_client.xadd(stream_key, event_data)
                execution_time = (time.time() - start_time) * 1000
                data_size = sum(len(k.encode()) + len(v.encode()) for k, v in event_data.items())
                
                metrics.append(RedisPerformanceMetric(
                    operation_name=f"Stream XADD {i}",
                    operation_type="stream",
                    execution_time_ms=execution_time,
                    data_size_bytes=data_size,
                    success=True,
                    timestamp=datetime.now().isoformat()
                ))
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                data_size = sum(len(k.encode()) + len(v.encode()) for k, v in event_data.items())
                metrics.append(RedisPerformanceMetric(
                    operation_name=f"Stream XADD {i}",
                    operation_type="stream",
                    execution_time_ms=execution_time,
                    data_size_bytes=data_size,
                    success=False,
                    timestamp=datetime.now().isoformat(),
                    optimization_applied=f"Error: {str(e)}"
                ))
        
        # XREAD operation
        start_time = time.time()
        try:
            messages = await self.async_redis_client.xread({stream_key: "0"}, count=10)
            execution_time = (time.time() - start_time) * 1000
            
            data_size = 0
            if messages:
                for stream, msgs in messages:
                    for msg_id, fields in msgs:
                        data_size += sum(len(k.encode()) + len(v.encode()) for k, v in fields.items())
            
            metrics.append(RedisPerformanceMetric(
                operation_name="Stream XREAD (10 messages)",
                operation_type="stream",
                execution_time_ms=execution_time,
                data_size_bytes=data_size,
                success=True,
                timestamp=datetime.now().isoformat()
            ))
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            metrics.append(RedisPerformanceMetric(
                operation_name="Stream XREAD (10 messages)",
                operation_type="stream",
                execution_time_ms=execution_time,
                data_size_bytes=0,
                success=False,
                timestamp=datetime.now().isoformat(),
                optimization_applied=f"Error: {str(e)}"
            ))
        
        return metrics
    
    async def _benchmark_pipeline_operations(self) -> List[RedisPerformanceMetric]:
        """Benchmark pipeline operations."""
        metrics = []
        
        # Pipeline with multiple operations
        start_time = time.time()
        try:
            pipe = self.async_redis_client.pipeline()
            
            # Add 100 operations to pipeline
            for i in range(100):
                pipe.set(f"pipeline:key:{i}", f"value_{i}", ex=300)
            
            # Execute pipeline
            results = await pipe.execute()
            execution_time = (time.time() - start_time) * 1000
            
            successful_ops = sum(1 for result in results if result)
            data_size = sum(len(f"value_{i}".encode()) for i in range(100))
            
            metrics.append(RedisPerformanceMetric(
                operation_name="Pipeline (100 SET operations)",
                operation_type="write",
                execution_time_ms=execution_time,
                data_size_bytes=data_size,
                success=successful_ops == 100,
                timestamp=datetime.now().isoformat(),
                optimization_applied=f"Batched {successful_ops}/100 operations"
            ))
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            metrics.append(RedisPerformanceMetric(
                operation_name="Pipeline (100 SET operations)",
                operation_type="write",
                execution_time_ms=execution_time,
                data_size_bytes=0,
                success=False,
                timestamp=datetime.now().isoformat(),
                optimization_applied=f"Error: {str(e)}"
            ))
        
        return metrics
    
    async def collect_memory_metrics(self) -> RedisMemoryMetrics:
        """Collect Redis memory usage metrics."""
        try:
            info = await self.async_redis_client.info("memory")
            stats = await self.async_redis_client.info("stats")
            
            used_memory_mb = info.get('used_memory', 0) / (1024 * 1024)
            used_memory_peak_mb = info.get('used_memory_peak', 0) / (1024 * 1024)
            used_memory_rss_mb = info.get('used_memory_rss', 0) / (1024 * 1024)
            
            fragmentation_ratio = info.get('mem_fragmentation_ratio', 1.0)
            
            keyspace_hits = stats.get('keyspace_hits', 0)
            keyspace_misses = stats.get('keyspace_misses', 0)
            total_requests = keyspace_hits + keyspace_misses
            hit_rate = (keyspace_hits / total_requests * 100) if total_requests > 0 else 0
            
            metrics = RedisMemoryMetrics(
                used_memory_mb=used_memory_mb,
                used_memory_peak_mb=used_memory_peak_mb,
                used_memory_rss_mb=used_memory_rss_mb,
                memory_fragmentation_ratio=fragmentation_ratio,
                expired_keys=stats.get('expired_keys', 0),
                evicted_keys=stats.get('evicted_keys', 0),
                keyspace_hits=keyspace_hits,
                keyspace_misses=keyspace_misses,
                hit_rate_percent=hit_rate,
                timestamp=datetime.now().isoformat()
            )
            
            self.memory_metrics.append(metrics)
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to collect memory metrics: {e}")
            return RedisMemoryMetrics(0, 0, 0, 1.0, 0, 0, 0, 0, 0, datetime.now().isoformat())
    
    async def analyze_event_bus_streams(self) -> List[RedisStreamMetrics]:
        """Analyze Redis Streams used for event bus."""
        logger.info("📊 Analyzing event bus streams...")
        
        stream_patterns = [
            "astra.trading.*",
            "astra.gamification.*", 
            "astra.social.*",
            "astra.financial.*",
            "astra.nft.*",
            "astra.user.*"
        ]
        
        stream_metrics = []
        
        try:
            # Get all streams
            all_keys = await self.async_redis_client.keys("astra.*")
            streams = [key for key in all_keys if "stream" in key.lower() or "astra." in key]
            
            for stream_name in streams:
                try:
                    # Get stream info
                    stream_info = await self.async_redis_client.xinfo_stream(stream_name)
                    
                    # Get consumer groups
                    try:
                        groups = await self.async_redis_client.xinfo_groups(stream_name)
                        consumer_groups = len(groups)
                        
                        # Calculate pending messages across all groups
                        pending_messages = 0
                        for group in groups:
                            pending_messages += group.get('pending', 0)
                    except:
                        consumer_groups = 0
                        pending_messages = 0
                    
                    # Get memory usage
                    try:
                        memory_usage = await self.async_redis_client.memory_usage(stream_name)
                    except:
                        memory_usage = 0
                    
                    metrics = RedisStreamMetrics(
                        stream_name=stream_name,
                        length=stream_info.get('length', 0),
                        consumer_groups=consumer_groups,
                        pending_messages=pending_messages,
                        last_generated_id=stream_info.get('last-generated-id', '0-0'),
                        memory_usage_bytes=memory_usage,
                        throughput_msgs_per_sec=0.0,  # Would need time-based calculation
                        timestamp=datetime.now().isoformat()
                    )
                    
                    stream_metrics.append(metrics)
                    
                except Exception as e:
                    logger.warning(f"Failed to analyze stream {stream_name}: {e}")
        
        except Exception as e:
            logger.error(f"Failed to analyze streams: {e}")
        
        self.stream_metrics.extend(stream_metrics)
        return stream_metrics
    
    async def optimize_redis_configuration(self) -> Dict[str, Any]:
        """Apply Redis configuration optimizations."""
        logger.info("⚙️ Applying Redis configuration optimizations...")
        
        optimizations = []
        
        try:
            # Memory optimization settings
            config_commands = [
                ("maxmemory-policy", "allkeys-lru"),  # LRU eviction for all keys
                ("timeout", "300"),  # Client idle timeout
                ("tcp-keepalive", "60"),  # TCP keepalive
                ("save", "900 1 300 10 60 10000"),  # Optimized save intervals
            ]
            
            for setting, value in config_commands:
                try:
                    await self.async_redis_client.config_set(setting, value)
                    optimizations.append(f"{setting} = {value}")
                    logger.info(f"   ✅ Applied: {setting} = {value}")
                except Exception as e:
                    logger.warning(f"   ⚠️ Failed to set {setting}: {e}")
            
            # Get current configuration
            config = await self.async_redis_client.config_get("*")
            
            return {
                "optimizations_applied": optimizations,
                "current_config": dict(config),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to optimize Redis configuration: {e}")
            return {
                "optimizations_applied": [],
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def run_comprehensive_optimization(self) -> Dict[str, Any]:
        """Run comprehensive Redis optimization suite."""
        logger.info("🚀 Starting Comprehensive Redis Optimization")
        logger.info("=" * 60)
        
        start_time = time.time()
        
        # Initialize connections
        await self.initialize()
        
        # Phase 1: Configuration optimization
        logger.info("\n⚙️ Phase 1: Configuration Optimization")
        config_results = await self.optimize_redis_configuration()
        
        # Phase 2: Performance benchmarking
        logger.info("\n🏃‍♂️ Phase 2: Performance Benchmarking")
        benchmark_results = await self.benchmark_redis_operations()
        
        # Phase 3: Memory analysis
        logger.info("\n📊 Phase 3: Memory Analysis")
        memory_metrics = await self.collect_memory_metrics()
        
        # Phase 4: Event bus analysis
        logger.info("\n🌊 Phase 4: Event Bus Stream Analysis")
        stream_metrics = await self.analyze_event_bus_streams()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Generate optimization report
        report = self._generate_optimization_report(
            duration, config_results, benchmark_results, memory_metrics, stream_metrics
        )
        
        logger.info("\n" + "=" * 60)
        logger.info("🎉 Redis Optimization Complete!")
        logger.info(f"Duration: {duration:.1f} seconds")
        logger.info(f"Operations Benchmarked: {len(benchmark_results)}")
        logger.info(f"Streams Analyzed: {len(stream_metrics)}")
        
        return report
    
    def _generate_optimization_report(self, duration: float, config_results: Dict[str, Any],
                                    benchmark_results: List[RedisPerformanceMetric],
                                    memory_metrics: RedisMemoryMetrics,
                                    stream_metrics: List[RedisStreamMetrics]) -> Dict[str, Any]:
        """Generate comprehensive Redis optimization report."""
        
        # Analyze benchmark results
        successful_ops = [m for m in benchmark_results if m.success]
        failed_ops = [m for m in benchmark_results if not m.success]
        
        if successful_ops:
            avg_response_time = statistics.mean([m.execution_time_ms for m in successful_ops])
            p95_response_time = statistics.quantiles([m.execution_time_ms for m in successful_ops], n=20)[18] if len(successful_ops) > 20 else 0
        else:
            avg_response_time = 0
            p95_response_time = 0
        
        # Group operations by type
        operation_types = {}
        for metric in successful_ops:
            op_type = metric.operation_type
            if op_type not in operation_types:
                operation_types[op_type] = []
            operation_types[op_type].append(metric.execution_time_ms)
        
        type_averages = {
            op_type: statistics.mean(times) 
            for op_type, times in operation_types.items()
        }
        
        report = {
            "optimization_summary": {
                "duration_seconds": duration,
                "config_optimizations_applied": len(config_results.get("optimizations_applied", [])),
                "operations_benchmarked": len(benchmark_results),
                "successful_operations": len(successful_ops),
                "failed_operations": len(failed_ops),
                "streams_analyzed": len(stream_metrics),
                "timestamp": datetime.now().isoformat()
            },
            "performance_metrics": {
                "avg_response_time_ms": avg_response_time,
                "p95_response_time_ms": p95_response_time,
                "success_rate_percent": (len(successful_ops) / len(benchmark_results) * 100) if benchmark_results else 0,
                "operation_type_averages": type_averages
            },
            "memory_metrics": asdict(memory_metrics),
            "stream_metrics": [asdict(sm) for sm in stream_metrics],
            "configuration": config_results,
            "benchmark_details": [asdict(bm) for bm in benchmark_results],
            "recommendations": self._generate_redis_recommendations(
                benchmark_results, memory_metrics, stream_metrics
            )
        }
        
        return report
    
    def _generate_redis_recommendations(self, benchmark_results: List[RedisPerformanceMetric],
                                      memory_metrics: RedisMemoryMetrics,
                                      stream_metrics: List[RedisStreamMetrics]) -> List[str]:
        """Generate Redis optimization recommendations."""
        recommendations = []
        
        # Analyze response times
        successful_ops = [m for m in benchmark_results if m.success]
        if successful_ops:
            avg_time = statistics.mean([m.execution_time_ms for m in successful_ops])
            
            if avg_time > 5.0:  # >5ms average
                recommendations.append("High average response time - consider Redis clustering or optimization")
            
            slow_ops = [m for m in successful_ops if m.execution_time_ms > 10.0]
            if slow_ops:
                recommendations.append(f"Found {len(slow_ops)} slow operations (>10ms) - investigate specific operations")
        
        # Analyze memory usage
        if memory_metrics.memory_fragmentation_ratio > 1.5:
            recommendations.append("High memory fragmentation - consider Redis restart or MEMORY PURGE")
        
        if memory_metrics.hit_rate_percent < 90:
            recommendations.append(f"Low cache hit rate ({memory_metrics.hit_rate_percent:.1f}%) - review caching strategy")
        
        if memory_metrics.evicted_keys > 0:
            recommendations.append("Key evictions detected - consider increasing maxmemory or optimizing data retention")
        
        # Analyze streams
        total_pending = sum(sm.pending_messages for sm in stream_metrics)
        if total_pending > 1000:
            recommendations.append(f"High pending messages in streams ({total_pending}) - check consumer performance")
        
        large_streams = [sm for sm in stream_metrics if sm.length > 10000]
        if large_streams:
            recommendations.append(f"Found {len(large_streams)} large streams - consider XTRIM for memory optimization")
        
        # Operation-specific recommendations
        failed_ops = [m for m in benchmark_results if not m.success]
        if failed_ops:
            recommendations.append(f"Found {len(failed_ops)} failed operations - investigate error patterns")
        
        if not recommendations:
            recommendations.append("Redis performance is optimized! All metrics within acceptable ranges.")
        
        return recommendations
    
    def save_optimization_report(self, report: Dict[str, Any], filename: Optional[str] = None):
        """Save Redis optimization report to file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"redis_optimization_report_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"📄 Redis optimization report saved to: {filename}")
    
    async def cleanup(self):
        """Clean up Redis connections."""
        if self.async_redis_client:
            await self.async_redis_client.close()
        if self.redis_client:
            self.redis_client.close()
        logger.info("🧹 Redis connections cleaned up")

async def main():
    """Main function to run Redis optimization."""
    optimizer = RedisOptimizer()
    
    try:
        # Run comprehensive optimization
        report = await optimizer.run_comprehensive_optimization()
        
        # Save report
        optimizer.save_optimization_report(report)
        
        # Print summary
        print("\n" + "="*60)
        print("📊 REDIS OPTIMIZATION SUMMARY")
        print("="*60)
        print(f"Duration: {report['optimization_summary']['duration_seconds']:.1f}s")
        print(f"Operations Benchmarked: {report['optimization_summary']['operations_benchmarked']}")
        print(f"Success Rate: {report['performance_metrics']['success_rate_percent']:.1f}%")
        print(f"Avg Response Time: {report['performance_metrics']['avg_response_time_ms']:.2f}ms")
        print(f"Cache Hit Rate: {report['memory_metrics']['hit_rate_percent']:.1f}%")
        print(f"Memory Usage: {report['memory_metrics']['used_memory_mb']:.1f}MB")
        print(f"Streams Analyzed: {report['optimization_summary']['streams_analyzed']}")
        
        print("\n🔍 RECOMMENDATIONS:")
        for rec in report['recommendations']:
            print(f"• {rec}")
    
    finally:
        await optimizer.cleanup()

if __name__ == "__main__":
    asyncio.run(main())