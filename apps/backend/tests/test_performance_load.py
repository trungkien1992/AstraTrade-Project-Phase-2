import pytest
import asyncio
import time
import statistics
import random
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock, AsyncMock, patch
import redis
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
import psutil
import gc

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.competition.competition_service import CompetitionService
from services.competition.scoring import TournamentScoringEngine
from services.competition.leaderboard import LeaderboardManager
from services.competition.websocket_manager import TournamentWebSocketManager
from services.competition.ai_traders import AITradingEngine
from domains.shared.events import DomainEvent

# Performance test configuration
PERFORMANCE_CONFIG = {
    'redis_operations': 1000,
    'concurrent_users': 100,
    'websocket_connections': 500,
    'ai_trading_cycles': 50,
    'leaderboard_updates': 200,
    'message_throughput': 1000,
}

class PerformanceTimer:
    """Context manager for timing operations"""
    
    def __init__(self, name: str):
        self.name = name
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, *args):
        self.end_time = time.perf_counter()
    
    @property
    def duration(self) -> float:
        return self.end_time - self.start_time if self.end_time else 0

class MemoryMonitor:
    """Memory usage monitoring"""
    
    def __init__(self):
        self.initial_memory = None
        self.peak_memory = None
        self.final_memory = None
    
    def start(self):
        gc.collect()  # Force garbage collection
        self.initial_memory = psutil.Process().memory_info().rss
        self.peak_memory = self.initial_memory
    
    def update(self):
        current_memory = psutil.Process().memory_info().rss
        if current_memory > self.peak_memory:
            self.peak_memory = current_memory
    
    def stop(self):
        gc.collect()
        self.final_memory = psutil.Process().memory_info().rss
    
    def get_stats(self) -> Dict[str, float]:
        return {
            'initial_mb': self.initial_memory / 1024 / 1024,
            'peak_mb': self.peak_memory / 1024 / 1024,
            'final_mb': self.final_memory / 1024 / 1024,
            'increase_mb': (self.final_memory - self.initial_memory) / 1024 / 1024
        }

@pytest.fixture
def redis_client():
    """Mock Redis client optimized for performance testing"""
    mock_redis = Mock(spec=redis.Redis)
    mock_redis.ping.return_value = True
    
    # Fast mock responses
    mock_redis.hset.return_value = True
    mock_redis.hgetall.return_value = {
        'total_trades': '10',
        'winning_trades': '6',
        'total_profit': '500.0',
        'total_volume': '10000.0',
        'initial_capital': '100000.0'
    }
    mock_redis.zadd.return_value = 1
    mock_redis.zrevrange.return_value = [("user_1", 100.0), ("user_2", 90.0)]
    mock_redis.zscore.return_value = 95.0
    mock_redis.zrevrank.return_value = 1
    mock_redis.zcard.return_value = 100
    mock_redis.publish.return_value = 1
    mock_redis.lpush.return_value = 1
    mock_redis.ltrim.return_value = True
    mock_redis.llen.return_value = 50
    mock_redis.exists.return_value = True
    
    return mock_redis

@pytest.fixture
def competition_service(redis_client):
    """Competition service for performance testing"""
    with patch('services.competition.competition_service.Redis', return_value=redis_client):
        service = CompetitionService()
        service.redis_client = redis_client
        return service

class TestRedisPerformance:
    """Test Redis operation performance"""
    
    @pytest.mark.asyncio
    async def test_redis_leaderboard_operations_performance(self, redis_client):
        """Test Redis leaderboard operations under load"""
        leaderboard_manager = LeaderboardManager(redis_client)
        tournament_id = "performance_test"
        
        operations_count = PERFORMANCE_CONFIG['redis_operations']
        latencies = []
        
        memory_monitor = MemoryMonitor()
        memory_monitor.start()
        
        with PerformanceTimer("redis_leaderboard_operations") as timer:
            for i in range(operations_count):
                start = time.perf_counter()
                
                # Simulate leaderboard update
                await leaderboard_manager.update_score(tournament_id, f"user_{i}", random.uniform(0, 1000))
                
                end = time.perf_counter()
                latencies.append(end - start)
                
                if i % 100 == 0:
                    memory_monitor.update()
        
        memory_monitor.stop()
        
        # Performance assertions
        assert timer.duration < 10.0, f"Redis operations took too long: {timer.duration:.2f}s"
        
        avg_latency = statistics.mean(latencies)
        p95_latency = statistics.quantiles(latencies, n=20)[18]  # 95th percentile
        
        assert avg_latency < 0.01, f"Average Redis latency too high: {avg_latency:.4f}s"
        assert p95_latency < 0.05, f"P95 Redis latency too high: {p95_latency:.4f}s"
        
        memory_stats = memory_monitor.get_stats()
        assert memory_stats['increase_mb'] < 100, f"Memory usage increased too much: {memory_stats['increase_mb']:.2f}MB"
        
        print(f"Redis Performance Stats:")
        print(f"  Operations: {operations_count}")
        print(f"  Total time: {timer.duration:.2f}s")
        print(f"  Ops/sec: {operations_count / timer.duration:.2f}")
        print(f"  Avg latency: {avg_latency:.4f}s")
        print(f"  P95 latency: {p95_latency:.4f}s")
        print(f"  Memory increase: {memory_stats['increase_mb']:.2f}MB")
    
    @pytest.mark.asyncio
    async def test_concurrent_redis_operations(self, redis_client):
        """Test concurrent Redis operations performance"""
        leaderboard_manager = LeaderboardManager(redis_client)
        tournament_id = "concurrent_test"
        
        concurrent_users = PERFORMANCE_CONFIG['concurrent_users']
        operations_per_user = 10
        
        async def user_operations(user_id: int):
            latencies = []
            for i in range(operations_per_user):
                start = time.perf_counter()
                await leaderboard_manager.update_score(tournament_id, f"user_{user_id}", random.uniform(0, 1000))
                end = time.perf_counter()
                latencies.append(end - start)
            return latencies
        
        with PerformanceTimer("concurrent_redis_operations") as timer:
            # Run concurrent user operations
            tasks = [user_operations(i) for i in range(concurrent_users)]
            results = await asyncio.gather(*tasks)
        
        # Analyze results
        all_latencies = [latency for user_latencies in results for latency in user_latencies]
        avg_latency = statistics.mean(all_latencies)
        max_latency = max(all_latencies)
        
        total_operations = concurrent_users * operations_per_user
        ops_per_second = total_operations / timer.duration
        
        assert timer.duration < 20.0, f"Concurrent operations took too long: {timer.duration:.2f}s"
        assert avg_latency < 0.05, f"Average concurrent latency too high: {avg_latency:.4f}s"
        assert ops_per_second > 50, f"Concurrent throughput too low: {ops_per_second:.2f} ops/sec"
        
        print(f"Concurrent Redis Performance Stats:")
        print(f"  Concurrent users: {concurrent_users}")
        print(f"  Total operations: {total_operations}")
        print(f"  Total time: {timer.duration:.2f}s")
        print(f"  Ops/sec: {ops_per_second:.2f}")
        print(f"  Avg latency: {avg_latency:.4f}s")
        print(f"  Max latency: {max_latency:.4f}s")

class TestScoringEnginePerformance:
    """Test scoring engine performance"""
    
    @pytest.mark.asyncio
    async def test_scoring_calculation_performance(self, redis_client):
        """Test scoring engine calculation performance"""
        scoring_engine = TournamentScoringEngine(redis_client)
        tournament_id = "scoring_perf_test"
        
        calculations_count = 500
        latencies = []
        
        # Pre-populate some user stats
        for i in range(10):
            stats_key = f"tournament:{tournament_id}:stats:user_{i}"
            redis_client.hgetall.return_value = {
                'total_trades': str(random.randint(5, 50)),
                'winning_trades': str(random.randint(2, 30)),
                'total_profit': str(random.uniform(-1000, 2000)),
                'total_volume': str(random.uniform(5000, 50000)),
                'initial_capital': '100000.0'
            }
        
        with PerformanceTimer("scoring_calculations") as timer:
            for i in range(calculations_count):
                start = time.perf_counter()
                
                components = await scoring_engine.calculate_score_components(f"user_{i % 10}", tournament_id)
                final_score = scoring_engine.calculate_composite_score(components)
                
                end = time.perf_counter()
                latencies.append(end - start)
        
        avg_latency = statistics.mean(latencies)
        p95_latency = statistics.quantiles(latencies, n=20)[18]
        calculations_per_second = calculations_count / timer.duration
        
        assert timer.duration < 5.0, f"Scoring calculations took too long: {timer.duration:.2f}s"
        assert avg_latency < 0.01, f"Average scoring latency too high: {avg_latency:.4f}s"
        assert calculations_per_second > 100, f"Scoring throughput too low: {calculations_per_second:.2f} calc/sec"
        
        print(f"Scoring Engine Performance Stats:")
        print(f"  Calculations: {calculations_count}")
        print(f"  Total time: {timer.duration:.2f}s")
        print(f"  Calc/sec: {calculations_per_second:.2f}")
        print(f"  Avg latency: {avg_latency:.4f}s")
        print(f"  P95 latency: {p95_latency:.4f}s")

class TestAITradingPerformance:
    """Test AI trading engine performance"""
    
    @pytest.mark.asyncio
    async def test_ai_trading_cycle_performance(self, competition_service):
        """Test AI trading cycle performance"""
        ai_engine = competition_service.ai_engine
        tournament_id = "ai_perf_test"
        
        # Initialize AI states
        ai_engine.initialize_ai_states(tournament_id)
        
        cycles_count = PERFORMANCE_CONFIG['ai_trading_cycles']
        cycle_times = []
        total_trades = 0
        
        memory_monitor = MemoryMonitor()
        memory_monitor.start()
        
        with PerformanceTimer("ai_trading_cycles") as timer:
            for cycle in range(cycles_count):
                cycle_start = time.perf_counter()
                
                result = await ai_engine.run_ai_trading_cycle(tournament_id)
                total_trades += result['trades_generated']
                
                cycle_end = time.perf_counter()
                cycle_times.append(cycle_end - cycle_start)
                
                memory_monitor.update()
        
        memory_monitor.stop()
        
        avg_cycle_time = statistics.mean(cycle_times)
        max_cycle_time = max(cycle_times)
        trades_per_cycle = total_trades / cycles_count
        
        assert timer.duration < 30.0, f"AI trading cycles took too long: {timer.duration:.2f}s"
        assert avg_cycle_time < 0.5, f"Average cycle time too high: {avg_cycle_time:.4f}s"
        assert max_cycle_time < 2.0, f"Max cycle time too high: {max_cycle_time:.4f}s"
        
        memory_stats = memory_monitor.get_stats()
        assert memory_stats['increase_mb'] < 50, f"AI trading memory increase too high: {memory_stats['increase_mb']:.2f}MB"
        
        print(f"AI Trading Performance Stats:")
        print(f"  Cycles: {cycles_count}")
        print(f"  Total time: {timer.duration:.2f}s")
        print(f"  Total trades: {total_trades}")
        print(f"  Avg cycle time: {avg_cycle_time:.4f}s")
        print(f"  Max cycle time: {max_cycle_time:.4f}s")
        print(f"  Trades per cycle: {trades_per_cycle:.2f}")
        print(f"  Memory increase: {memory_stats['increase_mb']:.2f}MB")
    
    @pytest.mark.asyncio
    async def test_concurrent_ai_trade_generation(self, competition_service):
        """Test concurrent AI trade generation performance"""
        ai_engine = competition_service.ai_engine
        tournament_id = "concurrent_ai_test"
        
        ai_engine.initialize_ai_states(tournament_id)
        traders = ai_engine.get_active_ai_traders()[:20]  # Use first 20 AI traders
        
        market_conditions = {
            'hour': 14,
            'volatility': 0.04,
            'trend_strength': 0.7,
            'trend_direction': 'UP'
        }
        
        iterations = 10
        
        with PerformanceTimer("concurrent_ai_generation") as timer:
            for iteration in range(iterations):
                # Generate trades for all AI traders concurrently
                tasks = [
                    ai_engine.generate_ai_trade(trader, market_conditions)
                    for trader in traders
                ]
                
                trades = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Count successful trade generations
                successful_trades = sum(1 for trade in trades if trade is not None and not isinstance(trade, Exception))
        
        total_attempts = len(traders) * iterations
        generation_rate = total_attempts / timer.duration
        
        assert timer.duration < 10.0, f"Concurrent AI generation took too long: {timer.duration:.2f}s"
        assert generation_rate > 50, f"AI generation rate too low: {generation_rate:.2f} attempts/sec"
        
        print(f"Concurrent AI Generation Performance Stats:")
        print(f"  AI traders: {len(traders)}")
        print(f"  Iterations: {iterations}")
        print(f"  Total attempts: {total_attempts}")
        print(f"  Total time: {timer.duration:.2f}s")
        print(f"  Generation rate: {generation_rate:.2f} attempts/sec")

class TestWebSocketPerformance:
    """Test WebSocket performance"""
    
    @pytest.mark.asyncio
    async def test_websocket_connection_scaling(self):
        """Test WebSocket connection scaling performance"""
        mock_redis = Mock()
        mock_redis.ping.return_value = True
        mock_redis.zrevrange.return_value = []
        mock_redis.hgetall.return_value = {}
        
        # Mock pubsub
        mock_pubsub = Mock()
        mock_pubsub.subscribe = AsyncMock()
        mock_pubsub.listen = AsyncMock(return_value=AsyncGenerator([]))
        mock_redis.pubsub.return_value = mock_pubsub
        
        websocket_manager = TournamentWebSocketManager(mock_redis)
        tournament_id = "websocket_perf_test"
        
        connection_count = PERFORMANCE_CONFIG['websocket_connections']
        connection_times = []
        
        async def create_mock_websocket():
            """Create a mock WebSocket connection"""
            ws = Mock()
            ws.accept = AsyncMock()
            ws.send_json = AsyncMock()
            ws.client = Mock()
            ws.client.host = f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}"
            ws.headers = {"user-agent": "perf-test"}
            return ws
        
        memory_monitor = MemoryMonitor()
        memory_monitor.start()
        
        # Test connection creation performance
        with PerformanceTimer("websocket_connections") as timer:
            websockets_list = []
            
            for i in range(connection_count):
                conn_start = time.perf_counter()
                
                ws = await create_mock_websocket()
                connection = await websocket_manager.connect(ws, tournament_id, f"user_{i}")
                websockets_list.append((ws, connection))
                
                conn_end = time.perf_counter()
                connection_times.append(conn_end - conn_start)
                
                if i % 100 == 0:
                    memory_monitor.update()
        
        memory_monitor.stop()
        
        avg_connection_time = statistics.mean(connection_times)
        max_connection_time = max(connection_times)
        connections_per_second = connection_count / timer.duration
        
        assert timer.duration < 30.0, f"WebSocket connections took too long: {timer.duration:.2f}s"
        assert avg_connection_time < 0.1, f"Average connection time too high: {avg_connection_time:.4f}s"
        assert connections_per_second > 20, f"Connection rate too low: {connections_per_second:.2f} conn/sec"
        
        memory_stats = memory_monitor.get_stats()
        assert memory_stats['increase_mb'] < 200, f"WebSocket memory increase too high: {memory_stats['increase_mb']:.2f}MB"
        
        # Test message broadcasting performance
        message_count = PERFORMANCE_CONFIG['message_throughput']
        
        with PerformanceTimer("message_broadcasting") as broadcast_timer:
            for i in range(message_count):
                message = {
                    'type': 'performance_test',
                    'data': {'message_id': i, 'timestamp': time.time()}
                }
                await websocket_manager.broadcast_to_tournament(tournament_id, message)
        
        messages_per_second = message_count / broadcast_timer.duration
        total_message_deliveries = connection_count * message_count
        deliveries_per_second = total_message_deliveries / broadcast_timer.duration
        
        assert broadcast_timer.duration < 20.0, f"Message broadcasting took too long: {broadcast_timer.duration:.2f}s"
        assert messages_per_second > 50, f"Message broadcast rate too low: {messages_per_second:.2f} msg/sec"
        
        print(f"WebSocket Performance Stats:")
        print(f"  Connections: {connection_count}")
        print(f"  Connection time: {timer.duration:.2f}s")
        print(f"  Conn/sec: {connections_per_second:.2f}")
        print(f"  Avg conn time: {avg_connection_time:.4f}s")
        print(f"  Max conn time: {max_connection_time:.4f}s")
        print(f"  Memory increase: {memory_stats['increase_mb']:.2f}MB")
        print(f"  Messages broadcast: {message_count}")
        print(f"  Broadcast time: {broadcast_timer.duration:.2f}s")
        print(f"  Msg/sec: {messages_per_second:.2f}")
        print(f"  Total deliveries/sec: {deliveries_per_second:.2f}")
        
        # Cleanup
        await websocket_manager.shutdown()

async def AsyncGenerator(items):
    """Helper for async iteration in mocks"""
    for item in items:
        yield item

class TestIntegratedSystemPerformance:
    """Test integrated system performance"""
    
    @pytest.mark.asyncio
    async def test_full_tournament_simulation(self, competition_service):
        """Test full tournament simulation performance"""
        tournament_id = "full_simulation_test"
        
        # Initialize tournament
        await competition_service.initialize_daily_tournament()
        await competition_service.initialize_ai_traders(tournament_id)
        
        # Simulation parameters
        simulation_duration = 30  # seconds
        user_count = 50
        trades_per_user = 10
        
        memory_monitor = MemoryMonitor()
        memory_monitor.start()
        
        async def simulate_user_trading(user_id: str):
            """Simulate a user's trading activity"""
            trade_count = 0
            
            for _ in range(trades_per_user):
                # Create trade event
                trade_event = DomainEvent(
                    event_type="trade_executed",
                    domain="trading",
                    entity_id=f"trade_{user_id}_{trade_count}",
                    data={
                        'user_id': user_id,
                        'symbol': random.choice(['BTC-USD', 'ETH-USD', 'AAPL', 'TSLA']),
                        'side': random.choice(['BUY', 'SELL']),
                        'amount': random.uniform(100, 5000),
                        'profit': random.uniform(-200, 300),
                        'profit_percentage': random.uniform(-5, 8),
                        'volume': random.uniform(100, 5000),
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    }
                )
                
                await competition_service.process_trade_event(trade_event)
                trade_count += 1
                
                # Small delay to simulate realistic trading
                await asyncio.sleep(random.uniform(0.1, 0.5))
        
        with PerformanceTimer("full_tournament_simulation") as timer:
            # Start user trading simulations
            user_tasks = [simulate_user_trading(f"user_{i}") for i in range(user_count)]
            
            # Start AI trading cycles
            ai_cycles = 0
            ai_task_active = True
            
            async def ai_trading_loop():
                nonlocal ai_cycles, ai_task_active
                while ai_task_active:
                    await competition_service.ai_engine.run_ai_trading_cycle(tournament_id)
                    ai_cycles += 1
                    await asyncio.sleep(1)  # 1-second AI cycles for testing
            
            ai_task = asyncio.create_task(ai_trading_loop())
            
            # Wait for user simulations to complete or timeout
            try:
                await asyncio.wait_for(asyncio.gather(*user_tasks), timeout=simulation_duration)
            except asyncio.TimeoutError:
                pass
            
            ai_task_active = False
            await ai_task
        
        memory_monitor.stop()
        
        # Get final statistics
        tournament_stats = await competition_service.get_tournament_statistics(tournament_id)
        leaderboard = await competition_service.get_tournament_leaderboard(tournament_id, 0, 20)
        
        total_operations = user_count * trades_per_user + ai_cycles
        operations_per_second = total_operations / timer.duration
        
        memory_stats = memory_monitor.get_stats()
        
        # Performance assertions
        assert timer.duration <= simulation_duration + 5, f"Simulation exceeded expected duration"
        assert operations_per_second > 10, f"System throughput too low: {operations_per_second:.2f} ops/sec"
        assert memory_stats['increase_mb'] < 500, f"Memory increase too high: {memory_stats['increase_mb']:.2f}MB"
        
        print(f"Full Tournament Simulation Performance Stats:")
        print(f"  Duration: {timer.duration:.2f}s")
        print(f"  Users: {user_count}")
        print(f"  User trades: {user_count * trades_per_user}")
        print(f"  AI cycles: {ai_cycles}")
        print(f"  Total operations: {total_operations}")
        print(f"  Ops/sec: {operations_per_second:.2f}")
        print(f"  Memory increase: {memory_stats['increase_mb']:.2f}MB")
        print(f"  Final participants: {tournament_stats['total_participants']}")
        print(f"  Human players: {tournament_stats['human_players']}")
        print(f"  AI players: {tournament_stats['ai_players']}")
        print(f"  Leaderboard entries: {len(leaderboard)}")

class TestMemoryLeakDetection:
    """Test for memory leaks in long-running operations"""
    
    @pytest.mark.asyncio
    async def test_memory_stability_over_time(self, competition_service):
        """Test memory stability during extended operation"""
        tournament_id = "memory_stability_test"
        
        # Initialize tournament
        await competition_service.initialize_daily_tournament()
        await competition_service.initialize_ai_traders(tournament_id)
        
        memory_samples = []
        operation_count = 200
        
        # Take initial memory sample
        gc.collect()
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        for i in range(operation_count):
            # Perform various operations
            if i % 4 == 0:
                # AI trading cycle
                await competition_service.ai_engine.run_ai_trading_cycle(tournament_id)
            elif i % 4 == 1:
                # User trade simulation
                trade_event = DomainEvent(
                    event_type="trade_executed",
                    domain="trading", 
                    entity_id=f"memory_test_{i}",
                    data={
                        'user_id': f'user_{i % 10}',
                        'symbol': 'BTC-USD',
                        'profit': random.uniform(-50, 100),
                        'volume': 1000.0
                    }
                )
                await competition_service.process_trade_event(trade_event)
            elif i % 4 == 2:
                # Leaderboard query
                await competition_service.get_tournament_leaderboard(tournament_id, 0, 20)
            else:
                # Tournament stats
                await competition_service.get_tournament_statistics(tournament_id)
            
            # Sample memory every 20 operations
            if i % 20 == 0:
                current_memory = psutil.Process().memory_info().rss / 1024 / 1024
                memory_samples.append(current_memory)
        
        # Final memory check
        gc.collect()
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        # Analyze memory trend
        if len(memory_samples) >= 3:
            # Check if memory is consistently growing (potential leak)
            increases = [memory_samples[i+1] - memory_samples[i] for i in range(len(memory_samples)-1)]
            avg_increase = statistics.mean(increases)
            
            # Memory should not consistently increase
            assert avg_increase < 5.0, f"Potential memory leak detected: avg increase {avg_increase:.2f}MB per sample"
        
        total_increase = final_memory - initial_memory
        assert total_increase < 100, f"Total memory increase too high: {total_increase:.2f}MB"
        
        print(f"Memory Stability Test Stats:")
        print(f"  Operations: {operation_count}")
        print(f"  Initial memory: {initial_memory:.2f}MB")
        print(f"  Final memory: {final_memory:.2f}MB")
        print(f"  Total increase: {total_increase:.2f}MB")
        print(f"  Memory samples: {len(memory_samples)}")

class TestStressConditions:
    """Test system behavior under stress conditions"""
    
    @pytest.mark.asyncio
    async def test_high_concurrent_load(self, competition_service):
        """Test system under high concurrent load"""
        tournament_id = "stress_test"
        
        # Initialize tournament
        await competition_service.initialize_daily_tournament()
        
        # High concurrency parameters
        concurrent_operations = 200
        operations_per_task = 5
        
        async def stress_task(task_id: int):
            """Individual stress testing task"""
            results = []
            
            for op in range(operations_per_task):
                start_time = time.perf_counter()
                
                try:
                    # Mix of different operations
                    if op % 3 == 0:
                        # Trade processing
                        trade_event = DomainEvent(
                            event_type="trade_executed",
                            domain="trading",
                            entity_id=f"stress_{task_id}_{op}",
                            data={
                                'user_id': f'stress_user_{task_id}',
                                'symbol': random.choice(['BTC-USD', 'ETH-USD', 'AAPL']),
                                'profit': random.uniform(-100, 200),
                                'volume': random.uniform(500, 2000)
                            }
                        )
                        await competition_service.process_trade_event(trade_event)
                    
                    elif op % 3 == 1:
                        # Leaderboard operations
                        await competition_service.get_tournament_leaderboard(tournament_id, 0, 10)
                    
                    else:
                        # Statistics query
                        await competition_service.get_tournament_statistics(tournament_id)
                    
                    end_time = time.perf_counter()
                    results.append(('success', end_time - start_time))
                    
                except Exception as e:
                    end_time = time.perf_counter()
                    results.append(('error', end_time - start_time, str(e)))
            
            return results
        
        with PerformanceTimer("stress_test") as timer:
            # Launch all concurrent tasks
            tasks = [stress_task(i) for i in range(concurrent_operations)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Analyze results
        total_operations = 0
        successful_operations = 0
        failed_operations = 0
        all_latencies = []
        errors = []
        
        for task_result in results:
            if isinstance(task_result, Exception):
                failed_operations += operations_per_task
                errors.append(str(task_result))
            else:
                for op_result in task_result:
                    total_operations += 1
                    if op_result[0] == 'success':
                        successful_operations += 1
                        all_latencies.append(op_result[1])
                    else:
                        failed_operations += 1
                        errors.append(op_result[2])
        
        success_rate = successful_operations / total_operations if total_operations > 0 else 0
        avg_latency = statistics.mean(all_latencies) if all_latencies else 0
        operations_per_second = total_operations / timer.duration
        
        # Stress test assertions
        assert timer.duration < 60.0, f"Stress test took too long: {timer.duration:.2f}s"
        assert success_rate > 0.95, f"Success rate too low under stress: {success_rate:.2%}"
        assert avg_latency < 1.0, f"Average latency too high under stress: {avg_latency:.4f}s"
        assert operations_per_second > 50, f"Throughput too low under stress: {operations_per_second:.2f} ops/sec"
        
        print(f"Stress Test Results:")
        print(f"  Concurrent tasks: {concurrent_operations}")
        print(f"  Total operations: {total_operations}")
        print(f"  Successful: {successful_operations}")
        print(f"  Failed: {failed_operations}")
        print(f"  Success rate: {success_rate:.2%}")
        print(f"  Total time: {timer.duration:.2f}s")
        print(f"  Ops/sec: {operations_per_second:.2f}")
        print(f"  Avg latency: {avg_latency:.4f}s")
        print(f"  Unique errors: {len(set(errors))}")

if __name__ == "__main__":
    # Run performance tests with custom markers
    pytest.main([
        __file__, 
        "-v", 
        "-s",  # Show print statements
        "--tb=short",  # Shorter tracebacks
        "--timeout=300"  # 5 minute timeout for performance tests
    ])