#!/usr/bin/env python3
"""
AstraTrade Database Performance Optimization
Comprehensive database query optimization and connection pooling enhancements.
"""

import asyncio
import time
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import logging
from sqlalchemy import create_engine, text, MetaData, Table
from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import asyncpg
import psutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("db-optimizer")

@dataclass
class QueryPerformanceMetric:
    """Performance metrics for a database query."""
    query_name: str
    query: str
    execution_time_ms: float
    rows_returned: int
    rows_examined: Optional[int]
    index_used: bool
    timestamp: str
    optimization_applied: Optional[str] = None

@dataclass
class ConnectionPoolMetrics:
    """Connection pool performance metrics."""
    pool_size: int
    checked_out: int
    overflow: int
    checked_in: int
    total_connections: int
    average_checkout_time_ms: float
    timestamp: str

class DatabaseOptimizer:
    """Database performance optimization and monitoring."""
    
    def __init__(self, database_url: str = "postgresql+asyncpg://postgres:password@localhost/astradb"):
        self.database_url = database_url
        self.sync_url = database_url.replace("+asyncpg", "")
        self.async_engine = None
        self.sync_engine = None
        self.async_session_factory = None
        self.metrics: List[QueryPerformanceMetric] = []
        self.pool_metrics: List[ConnectionPoolMetrics] = []
        
    async def initialize(self):
        """Initialize database connections with optimized settings."""
        logger.info("🔧 Initializing optimized database connections...")
        
        # Async engine with optimized connection pool
        self.async_engine = create_async_engine(
            self.database_url,
            # Connection pool settings
            pool_size=20,           # Base pool size
            max_overflow=30,        # Additional connections when needed
            pool_pre_ping=True,     # Validate connections
            pool_recycle=3600,      # Recycle connections every hour
            # Query optimization settings
            echo=False,             # Disable query logging for performance
            future=True,
            # Connection-specific optimizations
            connect_args={
                "command_timeout": 10,
                "server_settings": {
                    "application_name": "astra_optimized",
                    "jit": "off",  # Disable JIT for consistent performance
                }
            }
        )
        
        # Sync engine for analysis queries
        self.sync_engine = create_engine(
            self.sync_url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            poolclass=QueuePool,
            echo=False
        )
        
        self.async_session_factory = sessionmaker(
            self.async_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        logger.info("✅ Database connections initialized with optimizations")
    
    async def analyze_query_performance(self, query_name: str, query: str, 
                                      params: Optional[Dict] = None) -> QueryPerformanceMetric:
        """Analyze performance of a specific query."""
        if not self.async_engine:
            await self.initialize()
        
        start_time = time.time()
        rows_returned = 0
        index_used = False
        
        try:
            async with self.async_engine.begin() as conn:
                # Execute EXPLAIN ANALYZE for detailed performance info
                explain_query = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}"
                
                if params:
                    explain_result = await conn.execute(text(explain_query), params)
                    actual_result = await conn.execute(text(query), params)
                else:
                    explain_result = await conn.execute(text(explain_query))
                    actual_result = await conn.execute(text(query))
                
                # Process results
                explain_data = explain_result.fetchone()[0]
                actual_rows = actual_result.fetchall()
                rows_returned = len(actual_rows)
                
                # Analyze execution plan
                plan = explain_data[0]["Plan"]
                index_used = self._check_index_usage(plan)
                
        except Exception as e:
            logger.error(f"Query analysis failed for {query_name}: {e}")
            execution_time_ms = (time.time() - start_time) * 1000
            return QueryPerformanceMetric(
                query_name=query_name,
                query=query,
                execution_time_ms=execution_time_ms,
                rows_returned=0,
                rows_examined=None,
                index_used=False,
                timestamp=datetime.now().isoformat(),
                optimization_applied="ERROR: Analysis failed"
            )
        
        execution_time_ms = (time.time() - start_time) * 1000
        
        metric = QueryPerformanceMetric(
            query_name=query_name,
            query=query,
            execution_time_ms=execution_time_ms,
            rows_returned=rows_returned,
            rows_examined=None,  # Would need additional analysis
            index_used=index_used,
            timestamp=datetime.now().isoformat()
        )
        
        self.metrics.append(metric)
        return metric
    
    def _check_index_usage(self, plan: Dict) -> bool:
        """Check if query execution plan uses indexes efficiently."""
        node_type = plan.get("Node Type", "")
        
        # Index scan types indicate good index usage
        efficient_scans = [
            "Index Scan", "Index Only Scan", "Bitmap Index Scan"
        ]
        
        if node_type in efficient_scans:
            return True
        
        # Check child plans recursively
        if "Plans" in plan:
            for child_plan in plan["Plans"]:
                if self._check_index_usage(child_plan):
                    return True
        
        return False
    
    async def optimize_common_queries(self) -> List[QueryPerformanceMetric]:
        """Optimize common AstraTrade queries."""
        logger.info("🔍 Analyzing and optimizing common queries...")
        
        common_queries = [
            {
                "name": "User Authentication Lookup",
                "query": "SELECT id, email, username, password_hash FROM users WHERE email = :email LIMIT 1",
                "params": {"email": "test@example.com"}
            },
            {
                "name": "Recent Trades by User",
                "query": "SELECT * FROM trades WHERE user_id = :user_id ORDER BY created_at DESC LIMIT 20",
                "params": {"user_id": 123}
            },
            {
                "name": "Leaderboard Top Users",
                "query": "SELECT u.username, g.total_xp FROM users u JOIN gamification_profiles g ON u.id = g.user_id ORDER BY g.total_xp DESC LIMIT 50",
                "params": None
            },
            {
                "name": "Active Trading Positions",
                "query": "SELECT * FROM positions WHERE user_id = :user_id AND status = 'ACTIVE'",
                "params": {"user_id": 123}
            },
            {
                "name": "Social Feed Recent Posts",
                "query": "SELECT p.*, u.username FROM posts p JOIN users u ON p.user_id = u.id WHERE p.created_at > NOW() - INTERVAL '24 hours' ORDER BY p.created_at DESC LIMIT 100",
                "params": None
            }
        ]
        
        optimized_metrics = []
        
        for query_config in common_queries:
            logger.info(f"   Analyzing: {query_config['name']}")
            
            # Analyze current performance
            metric = await self.analyze_query_performance(
                query_config["name"],
                query_config["query"],
                query_config["params"]
            )
            
            # Apply optimizations if needed
            optimization = await self._suggest_query_optimization(metric)
            if optimization:
                metric.optimization_applied = optimization
                logger.info(f"   💡 Optimization suggested: {optimization}")
            
            optimized_metrics.append(metric)
        
        return optimized_metrics
    
    async def _suggest_query_optimization(self, metric: QueryPerformanceMetric) -> Optional[str]:
        """Suggest optimizations for slow queries."""
        suggestions = []
        
        # Check for slow queries
        if metric.execution_time_ms > 100:  # >100ms
            suggestions.append("Consider adding appropriate indexes")
        
        # Check for missing index usage
        if not metric.index_used and metric.rows_returned > 10:
            suggestions.append("Query not using indexes - review WHERE clauses")
        
        # Check for large result sets
        if metric.rows_returned > 1000:
            suggestions.append("Large result set - consider pagination")
        
        return "; ".join(suggestions) if suggestions else None
    
    async def create_performance_indexes(self) -> List[str]:
        """Create indexes for common query patterns."""
        logger.info("📚 Creating performance indexes...")
        
        indexes_to_create = [
            # User table optimizations
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email ON users(email)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_username ON users(username)",
            
            # Trades table optimizations
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_trades_user_id_created_at ON trades(user_id, created_at DESC)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_trades_asset_symbol_created_at ON trades(asset_symbol, created_at DESC)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_trades_status_created_at ON trades(status, created_at DESC)",
            
            # Positions table optimizations
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_positions_user_id_status ON positions(user_id, status)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_positions_asset_symbol_status ON positions(asset_symbol, status)",
            
            # Gamification optimizations
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_gamification_profiles_total_xp ON gamification_profiles(total_xp DESC)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_achievements_user_id_unlocked_at ON achievements(user_id, unlocked_at DESC)",
            
            # Social features optimizations
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_posts_created_at ON posts(created_at DESC)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_posts_user_id_created_at ON posts(user_id, created_at DESC)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_social_interactions_user_id_created_at ON social_interactions(user_id, created_at DESC)",
            
            # Event bus optimizations
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_events_correlation_id ON events(correlation_id)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_events_event_type_created_at ON events(event_type, created_at DESC)"
        ]
        
        created_indexes = []
        
        try:
            async with self.async_engine.begin() as conn:
                for index_sql in indexes_to_create:
                    try:
                        await conn.execute(text(index_sql))
                        index_name = index_sql.split("idx_")[1].split(" ")[0]
                        created_indexes.append(f"idx_{index_name}")
                        logger.info(f"   ✅ Created index: idx_{index_name}")
                    except Exception as e:
                        logger.warning(f"   ⚠️ Index creation failed: {e}")
        
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
        
        return created_indexes
    
    async def monitor_connection_pool(self) -> ConnectionPoolMetrics:
        """Monitor connection pool performance."""
        if not self.async_engine:
            await self.initialize()
        
        pool = self.async_engine.pool
        
        metrics = ConnectionPoolMetrics(
            pool_size=pool.size(),
            checked_out=pool.checkedout(),
            overflow=pool.overflow(),
            checked_in=pool.checkedin(),
            total_connections=pool.checkedout() + pool.checkedin(),
            average_checkout_time_ms=0.0,  # Would need tracking over time
            timestamp=datetime.now().isoformat()
        )
        
        self.pool_metrics.append(metrics)
        return metrics
    
    async def optimize_connection_settings(self) -> Dict[str, Any]:
        """Optimize PostgreSQL connection settings."""
        logger.info("⚙️ Optimizing database connection settings...")
        
        optimization_queries = [
            # Connection and memory settings
            "SET shared_buffers = '256MB'",
            "SET effective_cache_size = '1GB'",
            "SET work_mem = '32MB'",
            "SET maintenance_work_mem = '128MB'",
            
            # Query optimization settings
            "SET random_page_cost = 1.1",  # SSD optimization
            "SET seq_page_cost = 1.0",
            "SET effective_io_concurrency = 200",  # SSD optimization
            
            # Checkpoint and WAL settings
            "SET checkpoint_completion_target = 0.9",
            "SET wal_buffers = '16MB'",
            
            # Logging and monitoring
            "SET log_min_duration_statement = 1000",  # Log queries > 1s
            "SET log_checkpoints = on",
            "SET log_connections = on",
            "SET log_disconnections = on"
        ]
        
        applied_settings = []
        
        try:
            async with self.async_engine.begin() as conn:
                for setting_sql in optimization_queries:
                    try:
                        await conn.execute(text(setting_sql))
                        applied_settings.append(setting_sql.split("SET ")[1])
                        logger.info(f"   ✅ Applied: {setting_sql}")
                    except Exception as e:
                        logger.warning(f"   ⚠️ Setting failed: {e}")
        
        except Exception as e:
            logger.error(f"Failed to apply settings: {e}")
        
        return {
            "applied_settings": applied_settings,
            "timestamp": datetime.now().isoformat()
        }
    
    async def run_comprehensive_optimization(self) -> Dict[str, Any]:
        """Run comprehensive database optimization suite."""
        logger.info("🚀 Starting Comprehensive Database Optimization")
        logger.info("=" * 60)
        
        start_time = time.time()
        
        # Initialize optimized connections
        await self.initialize()
        
        # Phase 1: Create performance indexes
        logger.info("\n📚 Phase 1: Creating Performance Indexes")
        created_indexes = await self.create_performance_indexes()
        
        # Phase 2: Optimize connection settings
        logger.info("\n⚙️ Phase 2: Optimizing Connection Settings")
        connection_settings = await self.optimize_connection_settings()
        
        # Phase 3: Analyze query performance
        logger.info("\n🔍 Phase 3: Analyzing Query Performance")
        query_metrics = await self.optimize_common_queries()
        
        # Phase 4: Monitor connection pool
        logger.info("\n📊 Phase 4: Monitoring Connection Pool")
        pool_metrics = await self.monitor_connection_pool()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Generate optimization report
        report = {
            "optimization_summary": {
                "duration_seconds": duration,
                "indexes_created": len(created_indexes),
                "settings_applied": len(connection_settings.get("applied_settings", [])),
                "queries_analyzed": len(query_metrics),
                "timestamp": datetime.now().isoformat()
            },
            "performance_indexes": created_indexes,
            "connection_settings": connection_settings,
            "query_performance": [asdict(metric) for metric in query_metrics],
            "connection_pool_metrics": asdict(pool_metrics),
            "recommendations": self._generate_optimization_recommendations(query_metrics)
        }
        
        logger.info("\n" + "=" * 60)
        logger.info("🎉 Database Optimization Complete!")
        logger.info(f"Duration: {duration:.1f} seconds")
        logger.info(f"Indexes Created: {len(created_indexes)}")
        logger.info(f"Queries Analyzed: {len(query_metrics)}")
        
        return report
    
    def _generate_optimization_recommendations(self, metrics: List[QueryPerformanceMetric]) -> List[str]:
        """Generate database optimization recommendations."""
        recommendations = []
        
        # Analyze slow queries
        slow_queries = [m for m in metrics if m.execution_time_ms > 100]
        if slow_queries:
            recommendations.append(f"Found {len(slow_queries)} slow queries (>100ms) - review and optimize")
        
        # Analyze index usage
        queries_without_indexes = [m for m in metrics if not m.index_used and m.rows_returned > 1]
        if queries_without_indexes:
            recommendations.append(f"{len(queries_without_indexes)} queries not using indexes efficiently")
        
        # Connection pool recommendations
        if self.pool_metrics:
            latest_pool = self.pool_metrics[-1]
            utilization = (latest_pool.checked_out / latest_pool.pool_size) * 100
            
            if utilization > 80:
                recommendations.append("High connection pool utilization - consider increasing pool size")
            elif utilization < 20:
                recommendations.append("Low connection pool utilization - consider reducing pool size")
        
        # Performance recommendations
        avg_response_time = sum(m.execution_time_ms for m in metrics) / len(metrics) if metrics else 0
        if avg_response_time > 50:
            recommendations.append("Average query time > 50ms - review query optimization strategies")
        
        if not recommendations:
            recommendations.append("Database performance is optimized! All metrics within acceptable ranges.")
        
        return recommendations
    
    def save_optimization_report(self, report: Dict[str, Any], filename: Optional[str] = None):
        """Save optimization report to file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"db_optimization_report_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"📄 Database optimization report saved to: {filename}")
    
    async def cleanup(self):
        """Clean up database connections."""
        if self.async_engine:
            await self.async_engine.dispose()
        if self.sync_engine:
            self.sync_engine.dispose()
        logger.info("🧹 Database connections cleaned up")

async def main():
    """Main function to run database optimization."""
    optimizer = DatabaseOptimizer()
    
    try:
        # Run comprehensive optimization
        report = await optimizer.run_comprehensive_optimization()
        
        # Save report
        optimizer.save_optimization_report(report)
        
        # Print summary
        print("\n" + "="*60)
        print("📊 DATABASE OPTIMIZATION SUMMARY")
        print("="*60)
        print(f"Duration: {report['optimization_summary']['duration_seconds']:.1f}s")
        print(f"Indexes Created: {report['optimization_summary']['indexes_created']}")
        print(f"Settings Applied: {report['optimization_summary']['settings_applied']}")
        print(f"Queries Analyzed: {report['optimization_summary']['queries_analyzed']}")
        
        print("\n🔍 RECOMMENDATIONS:")
        for rec in report['recommendations']:
            print(f"• {rec}")
        
        print("\n📈 QUERY PERFORMANCE:")
        for query in report['query_performance']:
            print(f"• {query['query_name']}: {query['execution_time_ms']:.1f}ms")
    
    finally:
        await optimizer.cleanup()

if __name__ == "__main__":
    asyncio.run(main())