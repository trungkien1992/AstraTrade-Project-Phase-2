"""
AstraTrade Business Metrics Collection System

Comprehensive business metrics collection for monitoring KPIs,
user activity, revenue, and operational metrics across all domains.
"""

import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import json
import asyncio
import logging
from collections import defaultdict, deque
import threading

logger = logging.getLogger("business-metrics")


class MetricType(Enum):
    """Types of business metrics."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class Domain(Enum):
    """Business domains."""
    TRADING = "trading"
    GAMIFICATION = "gamification"
    SOCIAL = "social"
    USER = "user"
    FINANCIAL = "financial"
    NFT = "nft"
    GATEWAY = "gateway"


@dataclass
class MetricPoint:
    """A single metric data point."""
    name: str
    value: float
    metric_type: MetricType
    domain: Domain
    timestamp: float = field(default_factory=time.time)
    labels: Dict[str, str] = field(default_factory=dict)
    correlation_id: Optional[str] = None


@dataclass
class BusinessKPI:
    """Business Key Performance Indicator."""
    name: str
    current_value: float
    target_value: float
    threshold_warning: float
    threshold_critical: float
    description: str
    unit: str
    last_updated: float = field(default_factory=time.time)


class BusinessMetricsCollector:
    """
    Comprehensive business metrics collector for AstraTrade.
    
    Collects and aggregates business metrics across all domains:
    - Trading metrics (trades/second, volume, PnL)
    - User activity (registrations, logins, engagement)
    - Revenue metrics (subscription, trading fees, NFT sales)
    - Gamification metrics (XP earned, achievements unlocked)
    - Social metrics (interactions, clan activity)
    """
    
    def __init__(self):
        self.metrics: Dict[str, List[MetricPoint]] = defaultdict(list)
        self.kpis: Dict[str, BusinessKPI] = {}
        self.counters: Dict[str, float] = defaultdict(float)
        self.gauges: Dict[str, float] = defaultdict(float)
        self.timers: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.lock = threading.Lock()
        
        # Business aggregations
        self.trading_stats = {
            "total_trades": 0,
            "total_volume": 0.0,
            "total_revenue": 0.0,
            "active_users": set(),
            "trades_per_second": deque(maxlen=60),  # Last 60 seconds
        }
        
        self.user_stats = {
            "total_registrations": 0,
            "daily_active_users": set(),
            "monthly_active_users": set(),
            "user_retention": {},
        }
        
        self.revenue_stats = {
            "trading_fees": 0.0,
            "subscription_revenue": 0.0,
            "nft_marketplace_revenue": 0.0,
            "total_revenue": 0.0,
        }
        
        self.gamification_stats = {
            "total_xp_earned": 0,
            "achievements_unlocked": 0,
            "level_ups": 0,
            "leaderboard_updates": 0,
        }
        
        self.social_stats = {
            "social_interactions": 0,
            "clan_activities": 0,
            "feed_entries": 0,
            "viral_content_shares": 0,
        }
        
        # Initialize KPIs
        self._initialize_kpis()
        
        # Start background aggregation
        self._running = True
        try:
            asyncio.create_task(self._aggregation_loop())
        except RuntimeError:
            # If no event loop is running, skip background task
            pass
    
    def _initialize_kpis(self):
        """Initialize business KPIs with targets and thresholds."""
        self.kpis = {
            # Trading KPIs
            "trades_per_second": BusinessKPI(
                name="Trades Per Second",
                current_value=0.0,
                target_value=10.0,
                threshold_warning=5.0,
                threshold_critical=2.0,
                description="Average trades executed per second",
                unit="trades/sec"
            ),
            "daily_trading_volume": BusinessKPI(
                name="Daily Trading Volume",
                current_value=0.0,
                target_value=1000000.0,  # $1M daily
                threshold_warning=500000.0,
                threshold_critical=100000.0,
                description="Total trading volume in USD per day",
                unit="USD"
            ),
            
            # User KPIs
            "daily_active_users": BusinessKPI(
                name="Daily Active Users",
                current_value=0.0,
                target_value=1000.0,
                threshold_warning=500.0,
                threshold_critical=100.0,
                description="Number of unique active users per day",
                unit="users"
            ),
            "user_registration_rate": BusinessKPI(
                name="User Registration Rate",
                current_value=0.0,
                target_value=50.0,  # 50 new users per day
                threshold_warning=25.0,
                threshold_critical=10.0,
                description="New user registrations per day",
                unit="registrations/day"
            ),
            
            # Revenue KPIs
            "daily_revenue": BusinessKPI(
                name="Daily Revenue",
                current_value=0.0,
                target_value=10000.0,  # $10K daily
                threshold_warning=5000.0,
                threshold_critical=1000.0,
                description="Total revenue generated per day",
                unit="USD"
            ),
            "revenue_per_user": BusinessKPI(
                name="Revenue Per User",
                current_value=0.0,
                target_value=100.0,  # $100 per user
                threshold_warning=50.0,
                threshold_critical=10.0,
                description="Average revenue per active user",
                unit="USD/user"
            ),
            
            # Engagement KPIs
            "user_engagement_score": BusinessKPI(
                name="User Engagement Score",
                current_value=0.0,
                target_value=8.0,  # Out of 10
                threshold_warning=6.0,
                threshold_critical=4.0,
                description="Average user engagement score (0-10)",
                unit="score"
            ),
            "social_interaction_rate": BusinessKPI(
                name="Social Interaction Rate",
                current_value=0.0,
                target_value=5.0,  # 5 interactions per user per day
                threshold_warning=3.0,
                threshold_critical=1.0,
                description="Social interactions per active user per day",
                unit="interactions/user/day"
            ),
        }
    
    def record_trade_executed(
        self, 
        user_id: str, 
        symbol: str, 
        volume: float, 
        revenue: float,
        correlation_id: str = None
    ):
        """Record trade execution metrics."""
        with self.lock:
            self.trading_stats["total_trades"] += 1
            self.trading_stats["total_volume"] += volume
            self.trading_stats["total_revenue"] += revenue
            self.trading_stats["active_users"].add(user_id)
            
            # Record trading fee revenue
            self.revenue_stats["trading_fees"] += revenue
            self.revenue_stats["total_revenue"] += revenue
        
        # Record individual metrics
        self.record_metric("trade_executed", 1, MetricType.COUNTER, Domain.TRADING, {
            "symbol": symbol,
            "user_id": user_id
        }, correlation_id)
        
        self.record_metric("trading_volume", volume, MetricType.COUNTER, Domain.TRADING, {
            "symbol": symbol
        }, correlation_id)
        
        logger.info(f"Trade executed: {symbol} ${volume:.2f} for user {user_id}")
    
    def record_user_registration(self, user_id: str, correlation_id: str = None):
        """Record user registration metrics."""
        with self.lock:
            self.user_stats["total_registrations"] += 1
            self.user_stats["daily_active_users"].add(user_id)
            self.user_stats["monthly_active_users"].add(user_id)
        
        self.record_metric("user_registered", 1, MetricType.COUNTER, Domain.USER, {
            "user_id": user_id
        }, correlation_id)
        
        logger.info(f"User registered: {user_id}")
    
    def record_user_activity(self, user_id: str, activity_type: str, correlation_id: str = None):
        """Record user activity metrics."""
        with self.lock:
            self.user_stats["daily_active_users"].add(user_id)
            self.user_stats["monthly_active_users"].add(user_id)
        
        self.record_metric("user_activity", 1, MetricType.COUNTER, Domain.USER, {
            "user_id": user_id,
            "activity_type": activity_type
        }, correlation_id)
    
    def record_xp_gained(self, user_id: str, xp_amount: int, source: str, correlation_id: str = None):
        """Record gamification XP metrics."""
        with self.lock:
            self.gamification_stats["total_xp_earned"] += xp_amount
        
        self.record_metric("xp_gained", xp_amount, MetricType.COUNTER, Domain.GAMIFICATION, {
            "user_id": user_id,
            "source": source
        }, correlation_id)
    
    def record_achievement_unlocked(self, user_id: str, achievement_type: str, correlation_id: str = None):
        """Record achievement unlock metrics."""
        with self.lock:
            self.gamification_stats["achievements_unlocked"] += 1
        
        self.record_metric("achievement_unlocked", 1, MetricType.COUNTER, Domain.GAMIFICATION, {
            "user_id": user_id,
            "achievement_type": achievement_type
        }, correlation_id)
    
    def record_social_interaction(
        self, 
        user_id: str, 
        interaction_type: str, 
        target_user_id: str = None,
        correlation_id: str = None
    ):
        """Record social interaction metrics."""
        with self.lock:
            self.social_stats["social_interactions"] += 1
        
        labels = {
            "user_id": user_id,
            "interaction_type": interaction_type
        }
        
        if target_user_id:
            labels["target_user_id"] = target_user_id
        
        self.record_metric("social_interaction", 1, MetricType.COUNTER, Domain.SOCIAL, labels, correlation_id)
    
    def record_nft_sale(self, user_id: str, nft_id: str, sale_price: float, marketplace_fee: float, correlation_id: str = None):
        """Record NFT marketplace metrics."""
        with self.lock:
            self.revenue_stats["nft_marketplace_revenue"] += marketplace_fee
            self.revenue_stats["total_revenue"] += marketplace_fee
        
        self.record_metric("nft_sale", sale_price, MetricType.COUNTER, Domain.NFT, {
            "user_id": user_id,
            "nft_id": nft_id
        }, correlation_id)
        
        self.record_metric("marketplace_revenue", marketplace_fee, MetricType.COUNTER, Domain.NFT, {
            "nft_id": nft_id
        }, correlation_id)
    
    def record_subscription_payment(self, user_id: str, plan_type: str, amount: float, correlation_id: str = None):
        """Record subscription revenue metrics."""
        with self.lock:
            self.revenue_stats["subscription_revenue"] += amount
            self.revenue_stats["total_revenue"] += amount
        
        self.record_metric("subscription_payment", amount, MetricType.COUNTER, Domain.FINANCIAL, {
            "user_id": user_id,
            "plan_type": plan_type
        }, correlation_id)
    
    def record_api_request(self, endpoint: str, method: str, status_code: int, duration: float, correlation_id: str = None):
        """Record API gateway metrics."""
        self.record_metric("api_request", 1, MetricType.COUNTER, Domain.GATEWAY, {
            "endpoint": endpoint,
            "method": method,
            "status_code": str(status_code)
        }, correlation_id)
        
        self.record_metric("api_request_duration", duration, MetricType.HISTOGRAM, Domain.GATEWAY, {
            "endpoint": endpoint,
            "method": method
        }, correlation_id)
    
    def record_metric(
        self, 
        name: str, 
        value: float, 
        metric_type: MetricType, 
        domain: Domain,
        labels: Dict[str, str] = None,
        correlation_id: str = None
    ):
        """Record a generic metric."""
        metric = MetricPoint(
            name=name,
            value=value,
            metric_type=metric_type,
            domain=domain,
            labels=labels or {},
            correlation_id=correlation_id
        )
        
        with self.lock:
            self.metrics[name].append(metric)
            
            # Update aggregations
            if metric_type == MetricType.COUNTER:
                self.counters[name] += value
            elif metric_type == MetricType.GAUGE:
                self.gauges[name] = value
            elif metric_type == MetricType.TIMER:
                self.timers[name].append(value)
    
    async def _aggregation_loop(self):
        """Background loop for metric aggregation and KPI calculation."""
        while self._running:
            try:
                await asyncio.sleep(10)  # Aggregate every 10 seconds
                await self._calculate_kpis()
            except Exception as e:
                logger.error(f"Error in metrics aggregation: {e}")
    
    async def _calculate_kpis(self):
        """Calculate business KPIs from raw metrics."""
        current_time = time.time()
        
        with self.lock:
            # Calculate trades per second
            if len(self.trading_stats["trades_per_second"]) > 0:
                trades_per_second = sum(self.trading_stats["trades_per_second"]) / len(self.trading_stats["trades_per_second"])
            else:
                trades_per_second = 0.0
            
            self.kpis["trades_per_second"].current_value = trades_per_second
            self.kpis["trades_per_second"].last_updated = current_time
            
            # Calculate daily active users
            daily_active_users = len(self.user_stats["daily_active_users"])
            self.kpis["daily_active_users"].current_value = daily_active_users
            self.kpis["daily_active_users"].last_updated = current_time
            
            # Calculate daily revenue
            daily_revenue = self.revenue_stats["total_revenue"]
            self.kpis["daily_revenue"].current_value = daily_revenue
            self.kpis["daily_revenue"].last_updated = current_time
            
            # Calculate revenue per user
            if daily_active_users > 0:
                revenue_per_user = daily_revenue / daily_active_users
            else:
                revenue_per_user = 0.0
            
            self.kpis["revenue_per_user"].current_value = revenue_per_user
            self.kpis["revenue_per_user"].last_updated = current_time
            
            # Calculate engagement score (simplified)
            total_interactions = (
                self.social_stats["social_interactions"] +
                self.gamification_stats["achievements_unlocked"] +
                self.trading_stats["total_trades"]
            )
            
            if daily_active_users > 0:
                engagement_score = min(10.0, (total_interactions / daily_active_users) * 2)
            else:
                engagement_score = 0.0
            
            self.kpis["user_engagement_score"].current_value = engagement_score
            self.kpis["user_engagement_score"].last_updated = current_time
    
    def get_business_summary(self) -> Dict[str, Any]:
        """Get comprehensive business metrics summary."""
        with self.lock:
            # Handle set serialization properly
            trading_stats_copy = self.trading_stats.copy()
            trading_stats_copy["active_users"] = len(trading_stats_copy["active_users"])
            trading_stats_copy["trades_per_second"] = list(trading_stats_copy["trades_per_second"])
            
            return {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "kpis": {
                    name: {
                        "current": kpi.current_value,
                        "target": kpi.target_value,
                        "status": self._get_kpi_status(kpi),
                        "description": kpi.description,
                        "unit": kpi.unit,
                        "last_updated": kpi.last_updated
                    }
                    for name, kpi in self.kpis.items()
                },
                "domain_stats": {
                    "trading": trading_stats_copy,
                    "user": {k: len(v) if isinstance(v, set) else v for k, v in self.user_stats.items()},
                    "revenue": self.revenue_stats.copy(),
                    "gamification": self.gamification_stats.copy(),
                    "social": self.social_stats.copy()
                },
                "metric_counts": {
                    name: len(metrics) for name, metrics in self.metrics.items()
                }
            }
    
    def _get_kpi_status(self, kpi: BusinessKPI) -> str:
        """Determine KPI status based on thresholds."""
        if kpi.current_value >= kpi.target_value:
            return "excellent"
        elif kpi.current_value >= kpi.threshold_warning:
            return "good"
        elif kpi.current_value >= kpi.threshold_critical:
            return "warning"
        else:
            return "critical"
    
    def get_prometheus_metrics(self) -> str:
        """Export metrics in Prometheus format."""
        lines = []
        
        with self.lock:
            # Export counters
            for name, value in self.counters.items():
                lines.append(f"astra_{name}_total {value}")
            
            # Export gauges
            for name, value in self.gauges.items():
                lines.append(f"astra_{name} {value}")
            
            # Export KPIs
            for name, kpi in self.kpis.items():
                lines.append(f"astra_kpi_{name} {kpi.current_value}")
                lines.append(f"astra_kpi_{name}_target {kpi.target_value}")
        
        return "\n".join(lines)
    
    def reset_daily_stats(self):
        """Reset daily statistics (call at midnight)."""
        with self.lock:
            self.user_stats["daily_active_users"].clear()
            # Keep monthly stats and cumulative counters
    
    def stop(self):
        """Stop the metrics collector."""
        self._running = False


# Global instance
business_metrics = BusinessMetricsCollector()


# Convenience functions for easy integration
def record_trade(user_id: str, symbol: str, volume: float, revenue: float, correlation_id: str = None):
    """Convenience function to record trade metrics."""
    business_metrics.record_trade_executed(user_id, symbol, volume, revenue, correlation_id)


def record_user_signup(user_id: str, correlation_id: str = None):
    """Convenience function to record user registration."""
    business_metrics.record_user_registration(user_id, correlation_id)


def record_achievement(user_id: str, achievement_type: str, correlation_id: str = None):
    """Convenience function to record achievement unlock."""
    business_metrics.record_achievement_unlocked(user_id, achievement_type, correlation_id)


def get_business_dashboard() -> Dict[str, Any]:
    """Get business dashboard data."""
    return business_metrics.get_business_summary()


if __name__ == "__main__":
    # Example usage
    import asyncio
    
    async def test_metrics():
        # Simulate some business activity
        business_metrics.record_trade_executed("user123", "BTC/USD", 1000.0, 10.0)
        business_metrics.record_user_registration("user124")
        business_metrics.record_xp_gained("user123", 50, "trading")
        business_metrics.record_achievement_unlocked("user123", "profitable_trader")
        business_metrics.record_social_interaction("user123", "like", "user124")
        
        await asyncio.sleep(1)
        
        # Get summary
        summary = business_metrics.get_business_summary()
        print(json.dumps(summary, indent=2))
    
    asyncio.run(test_metrics())