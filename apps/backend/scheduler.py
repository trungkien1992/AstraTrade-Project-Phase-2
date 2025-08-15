#!/usr/bin/env python3
"""
AI Trading Scheduler
Runs AI trading cycles every 30 seconds for tournament competitions
"""

import asyncio
import logging
import os
import signal
import sys
import time
import json
from datetime import datetime, timezone
from typing import Dict, Any
import aiohttp
import redis.asyncio as redis

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/ai-scheduler.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class AITradingScheduler:
    """AI Trading Scheduler for tournament competitions"""
    
    def __init__(self):
        self.running = False
        self.redis_client = None
        self.cycle_interval = int(os.getenv('AI_CYCLE_INTERVAL', '30'))
        self.competition_service_url = os.getenv('COMPETITION_SERVICE_URL', 'http://competition-service:8001')
        self.max_consecutive_failures = 5
        self.consecutive_failures = 0
        
        # Statistics
        self.stats = {
            'cycles_completed': 0,
            'total_trades_generated': 0,
            'start_time': None,
            'last_cycle_time': None,
            'failures': 0
        }
    
    async def initialize(self):
        """Initialize Redis connection and other resources"""
        try:
            # Initialize Redis connection
            redis_host = os.getenv('REDIS_HOST', 'localhost')
            redis_port = int(os.getenv('REDIS_PORT', '6379'))
            redis_password = os.getenv('REDIS_PASSWORD', 'astratrade_redis_2024')
            
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                password=redis_password,
                decode_responses=True
            )
            
            # Test Redis connection
            await self.redis_client.ping()
            logger.info(f"Connected to Redis at {redis_host}:{redis_port}")
            
            # Test competition service connection
            await self.health_check_competition_service()
            logger.info(f"Competition service is healthy at {self.competition_service_url}")
            
            self.stats['start_time'] = datetime.now(timezone.utc)
            logger.info("AI Trading Scheduler initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI Trading Scheduler: {e}")
            raise
    
    async def health_check_competition_service(self):
        """Check if competition service is healthy"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.competition_service_url}/health",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status != 200:
                        raise Exception(f"Competition service health check failed: {response.status}")
                    return await response.json()
        except Exception as e:
            logger.error(f"Competition service health check failed: {e}")
            raise
    
    async def execute_ai_trading_cycle(self) -> Dict[str, Any]:
        """Execute a single AI trading cycle"""
        try:
            cycle_start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.competition_service_url}/api/internal/ai-trading-cycle",
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status != 200:
                        raise Exception(f"AI trading cycle failed: HTTP {response.status}")
                    
                    result = await response.json()
                    cycle_duration = time.time() - cycle_start_time
                    
                    # Update statistics
                    self.stats['cycles_completed'] += 1
                    self.stats['last_cycle_time'] = datetime.now(timezone.utc)
                    trades_generated = result.get('trades_generated', 0)
                    self.stats['total_trades_generated'] += trades_generated
                    self.consecutive_failures = 0
                    
                    logger.info(
                        f"AI cycle {self.stats['cycles_completed']} completed: "
                        f"{trades_generated} trades generated in {cycle_duration:.2f}s"
                    )
                    
                    return result
                    
        except Exception as e:
            self.consecutive_failures += 1
            self.stats['failures'] += 1
            logger.error(f"AI trading cycle failed (attempt {self.consecutive_failures}): {e}")
            
            # Check if we should stop due to consecutive failures
            if self.consecutive_failures >= self.max_consecutive_failures:
                logger.critical(f"Too many consecutive failures ({self.consecutive_failures}), stopping scheduler")
                await self.stop()
            
            raise e
    
    async def log_statistics(self):
        """Log scheduler statistics"""
        if self.stats['start_time']:
            uptime = datetime.now(timezone.utc) - self.stats['start_time']
            cycles_per_hour = (self.stats['cycles_completed'] / uptime.total_seconds()) * 3600 if uptime.total_seconds() > 0 else 0
            avg_trades_per_cycle = self.stats['total_trades_generated'] / max(self.stats['cycles_completed'], 1)
            
            logger.info(
                f"Scheduler Stats - Uptime: {uptime}, "
                f"Cycles: {self.stats['cycles_completed']}, "
                f"Rate: {cycles_per_hour:.2f}/hour, "
                f"Total Trades: {self.stats['total_trades_generated']}, "
                f"Avg Trades/Cycle: {avg_trades_per_cycle:.2f}, "
                f"Failures: {self.stats['failures']}"
            )
            
            # Store stats in Redis for monitoring
            try:
                stats_key = "ai_scheduler:stats"
                stats_data = {
                    **self.stats,
                    'start_time': self.stats['start_time'].isoformat(),
                    'last_cycle_time': self.stats['last_cycle_time'].isoformat() if self.stats['last_cycle_time'] else None,
                    'uptime_seconds': uptime.total_seconds(),
                    'cycles_per_hour': cycles_per_hour,
                    'avg_trades_per_cycle': avg_trades_per_cycle
                }
                await self.redis_client.hset(stats_key, mapping={k: json.dumps(v) for k, v in stats_data.items()})
                await self.redis_client.expire(stats_key, 3600)  # Expire in 1 hour
                
            except Exception as e:
                logger.warning(f"Failed to store stats in Redis: {e}")
    
    async def monitor_system_health(self):
        """Monitor system health and log warnings"""
        try:
            # Check Redis connection
            await self.redis_client.ping()
            
            # Check competition service
            await self.health_check_competition_service()
            
            # Check consecutive failures
            if self.consecutive_failures > 2:
                logger.warning(f"System health warning: {self.consecutive_failures} consecutive failures")
            
            logger.debug("System health check passed")
            
        except Exception as e:
            logger.warning(f"System health check failed: {e}")
    
    async def run(self):
        """Main scheduler loop"""
        self.running = True
        logger.info(f"Starting AI Trading Scheduler (cycle interval: {self.cycle_interval}s)")
        
        stats_log_interval = 120  # Log stats every 2 minutes
        health_check_interval = 600  # Health check every 10 minutes
        last_stats_log = 0
        last_health_check = 0
        
        try:
            while self.running:
                cycle_start = time.time()
                
                try:
                    # Execute AI trading cycle
                    await self.execute_ai_trading_cycle()
                    
                except Exception as e:
                    logger.error(f"AI trading cycle execution failed: {e}")
                    if not self.running:  # Stop was called due to too many failures
                        break
                
                current_time = time.time()
                
                # Periodic statistics logging
                if current_time - last_stats_log >= stats_log_interval:
                    await self.log_statistics()
                    last_stats_log = current_time
                
                # Periodic health checks
                if current_time - last_health_check >= health_check_interval:
                    await self.monitor_system_health()
                    last_health_check = current_time
                
                # Calculate sleep time to maintain consistent interval
                cycle_duration = time.time() - cycle_start
                sleep_time = max(0, self.cycle_interval - cycle_duration)
                
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                else:
                    logger.warning(f"AI cycle took longer than interval: {cycle_duration:.2f}s > {self.cycle_interval}s")
                
        except asyncio.CancelledError:
            logger.info("AI Trading Scheduler cancelled")
        except Exception as e:
            logger.critical(f"AI Trading Scheduler crashed: {e}")
            raise
        finally:
            await self.cleanup()
    
    async def stop(self):
        """Stop the scheduler gracefully"""
        logger.info("Stopping AI Trading Scheduler...")
        self.running = False
    
    async def cleanup(self):
        """Clean up resources"""
        try:
            # Log final statistics
            await self.log_statistics()
            
            # Close Redis connection
            if self.redis_client:
                await self.redis_client.close()
                logger.info("Redis connection closed")
            
            logger.info("AI Trading Scheduler stopped")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

# Global scheduler instance
scheduler = None

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    if scheduler:
        asyncio.create_task(scheduler.stop())

async def main():
    """Main entry point"""
    global scheduler
    
    try:
        # Set up signal handlers
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        
        # Create and initialize scheduler
        scheduler = AITradingScheduler()
        await scheduler.initialize()
        
        # Run scheduler
        await scheduler.run()
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.critical(f"AI Trading Scheduler failed to start: {e}")
        sys.exit(1)
    finally:
        if scheduler:
            await scheduler.cleanup()

if __name__ == "__main__":
    # Run the scheduler
    asyncio.run(main())