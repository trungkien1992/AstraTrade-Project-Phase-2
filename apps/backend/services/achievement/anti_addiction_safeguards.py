#!/usr/bin/env python3
"""
Anti-Addiction Safeguards System

Implements responsible gamification mechanisms to prevent harmful 
achievement patterns and promote healthy trading behaviors.

Research-Based Safeguards:
- Maximum 4 achievements per hour to prevent dopamine oversaturation
- 15-minute cooling-off periods after 3+ consecutive achievements
- 60% educational achievement ratio to promote learning over performance
- Overtrading detection and intervention
- Stress monitoring with achievement suppression during high-stress periods
- Risk awareness promotion through achievement design
- Addiction pattern detection and intervention

Compliance:
- Financial trading regulations
- Responsible gambling guidelines
- User privacy protection
- Psychological safety standards
"""

import asyncio
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import redis.asyncio as redis
import numpy as np
from .dopamine_timing_engine import AchievementPriority, UserStressMetrics, TradingContextState


logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """User risk levels for addiction intervention"""
    LOW = "low"           # Healthy usage patterns
    MODERATE = "moderate" # Some concerning patterns
    HIGH = "high"         # Intervention recommended
    CRITICAL = "critical" # Immediate intervention required


class InterventionType(Enum):
    """Types of interventions for addiction prevention"""
    ACHIEVEMENT_SUPPRESSION = "achievement_suppression"
    COOLING_OFF_ENFORCEMENT = "cooling_off_enforcement"
    EDUCATIONAL_REDIRECT = "educational_redirect"
    STRESS_REDUCTION = "stress_reduction"
    OVERTRADING_WARNING = "overtrading_warning"
    BREAK_SUGGESTION = "break_suggestion"
    SUPPORT_RESOURCES = "support_resources"


@dataclass
class UserRiskMetrics:
    """Comprehensive risk assessment metrics for a user"""
    user_id: str
    
    # Achievement patterns
    hourly_achievement_rate: float = 0.0
    consecutive_achievement_count: int = 0
    educational_achievement_ratio: float = 0.0
    total_achievements_today: int = 0
    
    # Trading patterns  
    trades_per_hour: float = 0.0
    loss_streak: int = 0
    position_hold_time_avg: float = 0.0  # Average minutes
    risk_per_trade: float = 0.0  # Percentage of portfolio
    
    # Behavioral patterns
    session_duration: float = 0.0  # Hours
    break_frequency: float = 0.0   # Breaks per hour
    stress_episodes: int = 0       # High-stress periods today
    error_frequency: float = 0.0   # Errors per hour
    
    # Time patterns
    late_night_trading: bool = False  # Trading after 11 PM
    weekend_trading_hours: float = 0.0
    consecutive_days_trading: int = 0
    
    # Calculated risk scores
    addiction_risk_score: float = 0.0
    overtrading_risk_score: float = 0.0
    stress_risk_score: float = 0.0
    
    @property
    def overall_risk_level(self) -> RiskLevel:
        """Calculate overall risk level from component scores"""
        max_risk = max(
            self.addiction_risk_score,
            self.overtrading_risk_score,
            self.stress_risk_score
        )
        
        if max_risk >= 0.8:
            return RiskLevel.CRITICAL
        elif max_risk >= 0.6:
            return RiskLevel.HIGH
        elif max_risk >= 0.4:
            return RiskLevel.MODERATE
        else:
            return RiskLevel.LOW


@dataclass
class InterventionAction:
    """Specific intervention action to be taken"""
    intervention_type: InterventionType
    severity: RiskLevel
    message: str
    duration_minutes: int = 0
    metadata: Dict = field(default_factory=dict)


class AntiAddictionSafeguards:
    """
    Comprehensive anti-addiction system implementing multiple safeguards
    to prevent harmful gamification patterns in trading applications.
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.config = self._initialize_config()
        self.risk_thresholds = self._initialize_risk_thresholds()
        
    def _initialize_config(self) -> Dict:
        """Initialize anti-addiction configuration parameters"""
        return {
            # Achievement limits
            "max_achievements_per_hour": 4,
            "max_achievements_per_day": 24,
            "consecutive_achievement_limit": 3,
            "cooling_off_period_minutes": 15,
            "educational_achievement_ratio_target": 0.6,
            
            # Trading limits (for overtrading detection)
            "max_trades_per_hour_warning": 20,
            "max_trades_per_hour_critical": 30,
            "min_position_hold_time_minutes": 5,
            "max_risk_per_trade_percent": 10.0,
            
            # Session limits
            "max_session_duration_hours": 8,
            "min_break_frequency_per_hour": 1,
            "max_consecutive_trading_days": 30,
            
            # Time restrictions
            "restricted_hours_start": 23,  # 11 PM
            "restricted_hours_end": 6,     # 6 AM
            "weekend_trading_limit_hours": 4,
            
            # Stress thresholds
            "max_stress_episodes_per_day": 5,
            "max_error_frequency_per_hour": 10,
            "max_loss_streak": 5
        }
    
    def _initialize_risk_thresholds(self) -> Dict:
        """Initialize risk level thresholds for different metrics"""
        return {
            "addiction_risk": {
                "low": 0.0,
                "moderate": 0.4,
                "high": 0.6,
                "critical": 0.8
            },
            "overtrading_risk": {
                "low": 0.0,
                "moderate": 0.3,
                "high": 0.5,
                "critical": 0.7
            },
            "stress_risk": {
                "low": 0.0,
                "moderate": 0.4,
                "high": 0.6,
                "critical": 0.8
            }
        }
    
    async def assess_user_risk(self, user_id: str) -> UserRiskMetrics:
        """Comprehensive risk assessment for a user"""
        
        # Collect risk metrics
        risk_metrics = UserRiskMetrics(user_id=user_id)
        
        # Achievement pattern metrics
        await self._assess_achievement_patterns(risk_metrics)
        
        # Trading pattern metrics
        await self._assess_trading_patterns(risk_metrics)
        
        # Behavioral pattern metrics
        await self._assess_behavioral_patterns(risk_metrics)
        
        # Time pattern metrics
        await self._assess_time_patterns(risk_metrics)
        
        # Calculate composite risk scores
        self._calculate_risk_scores(risk_metrics)
        
        # Store assessment in Redis for monitoring
        await self._store_risk_assessment(risk_metrics)
        
        return risk_metrics
    
    async def _assess_achievement_patterns(self, metrics: UserRiskMetrics):
        """Assess achievement-related risk patterns"""
        user_id = metrics.user_id
        
        # Get recent achievement data
        recent_key = f"achievements:recent:{user_id}"
        current_time = time.time()
        
        # Hourly achievement rate
        hourly_achievements = await self.redis.zcount(
            recent_key, current_time - 3600, current_time
        )
        metrics.hourly_achievement_rate = float(hourly_achievements)
        
        # Daily total achievements
        daily_achievements = await self.redis.zcount(
            recent_key, current_time - 86400, current_time
        )
        metrics.total_achievements_today = daily_achievements
        
        # Consecutive achievements (last 10 minutes)
        consecutive_achievements = await self.redis.zcount(
            recent_key, current_time - 600, current_time
        )
        metrics.consecutive_achievement_count = consecutive_achievements
        
        # Educational achievement ratio
        educational_ratio = await self._get_educational_achievement_ratio(user_id)
        metrics.educational_achievement_ratio = educational_ratio
    
    async def _assess_trading_patterns(self, metrics: UserRiskMetrics):
        """Assess trading-related risk patterns"""
        user_id = metrics.user_id
        
        # Get trading activity data
        trading_key = f"trading:activity:{user_id}"
        current_time = time.time()
        
        # Trades per hour
        hourly_trades = await self.redis.zcount(
            trading_key, current_time - 3600, current_time
        )
        metrics.trades_per_hour = float(hourly_trades)
        
        # Loss streak
        loss_streak = await self._get_current_loss_streak(user_id)
        metrics.loss_streak = loss_streak
        
        # Average position hold time
        avg_hold_time = await self._get_average_hold_time(user_id)
        metrics.position_hold_time_avg = avg_hold_time
        
        # Risk per trade
        avg_risk = await self._get_average_risk_per_trade(user_id)
        metrics.risk_per_trade = avg_risk
    
    async def _assess_behavioral_patterns(self, metrics: UserRiskMetrics):
        """Assess behavioral risk patterns"""
        user_id = metrics.user_id
        
        # Session duration
        session_duration = await self._get_current_session_duration(user_id)
        metrics.session_duration = session_duration
        
        # Break frequency
        break_frequency = await self._get_break_frequency(user_id)
        metrics.break_frequency = break_frequency
        
        # Stress episodes today
        stress_episodes = await self._get_stress_episodes_count(user_id)
        metrics.stress_episodes = stress_episodes
        
        # Error frequency
        error_frequency = await self._get_error_frequency(user_id)
        metrics.error_frequency = error_frequency
    
    async def _assess_time_patterns(self, metrics: UserRiskMetrics):
        """Assess time-based risk patterns"""
        user_id = metrics.user_id
        current_hour = datetime.now().hour
        
        # Late night trading detection
        if (current_hour >= self.config["restricted_hours_start"] or 
            current_hour < self.config["restricted_hours_end"]):
            is_active = await self._is_user_currently_active(user_id)
            metrics.late_night_trading = is_active
        
        # Weekend trading hours
        weekend_hours = await self._get_weekend_trading_hours(user_id)
        metrics.weekend_trading_hours = weekend_hours
        
        # Consecutive trading days
        consecutive_days = await self._get_consecutive_trading_days(user_id)
        metrics.consecutive_days_trading = consecutive_days
    
    def _calculate_risk_scores(self, metrics: UserRiskMetrics):
        """Calculate composite risk scores from individual metrics"""
        
        # Addiction Risk Score
        addiction_factors = [
            min(metrics.hourly_achievement_rate / self.config["max_achievements_per_hour"], 1.0) * 0.3,
            min(metrics.consecutive_achievement_count / self.config["consecutive_achievement_limit"], 1.0) * 0.2,
            max(0, (self.config["educational_achievement_ratio_target"] - metrics.educational_achievement_ratio)) * 0.2,
            min(metrics.total_achievements_today / self.config["max_achievements_per_day"], 1.0) * 0.15,
            (1.0 if metrics.late_night_trading else 0.0) * 0.15
        ]
        metrics.addiction_risk_score = sum(addiction_factors)
        
        # Overtrading Risk Score
        overtrading_factors = [
            min(metrics.trades_per_hour / self.config["max_trades_per_hour_critical"], 1.0) * 0.4,
            (1.0 - min(metrics.position_hold_time_avg / self.config["min_position_hold_time_minutes"], 1.0)) * 0.2,
            min(metrics.risk_per_trade / self.config["max_risk_per_trade_percent"], 1.0) * 0.2,
            min(metrics.session_duration / self.config["max_session_duration_hours"], 1.0) * 0.1,
            min(metrics.weekend_trading_hours / self.config["weekend_trading_limit_hours"], 1.0) * 0.1
        ]
        metrics.overtrading_risk_score = sum(overtrading_factors)
        
        # Stress Risk Score  
        stress_factors = [
            min(metrics.loss_streak / self.config["max_loss_streak"], 1.0) * 0.3,
            min(metrics.stress_episodes / self.config["max_stress_episodes_per_day"], 1.0) * 0.25,
            min(metrics.error_frequency / self.config["max_error_frequency_per_hour"], 1.0) * 0.2,
            (1.0 - min(metrics.break_frequency / self.config["min_break_frequency_per_hour"], 1.0)) * 0.15,
            min(metrics.consecutive_days_trading / self.config["max_consecutive_trading_days"], 1.0) * 0.1
        ]
        metrics.stress_risk_score = sum(stress_factors)
    
    async def check_achievement_allowed(
        self, 
        user_id: str,
        achievement_priority: AchievementPriority
    ) -> Tuple[bool, Optional[InterventionAction]]:
        """
        Check if achievement notification is allowed or if intervention is needed.
        
        Returns (allowed, intervention_action)
        """
        risk_metrics = await self.assess_user_risk(user_id)
        
        # Check for critical risk - block all achievements
        if risk_metrics.overall_risk_level == RiskLevel.CRITICAL:
            intervention = InterventionAction(
                intervention_type=InterventionType.ACHIEVEMENT_SUPPRESSION,
                severity=RiskLevel.CRITICAL,
                message="Achievement notifications temporarily paused for your wellbeing. Take a break and consider our support resources.",
                duration_minutes=60,
                metadata={"risk_score": risk_metrics.addiction_risk_score}
            )
            return False, intervention
        
        # Check hourly limits
        if risk_metrics.hourly_achievement_rate >= self.config["max_achievements_per_hour"]:
            intervention = InterventionAction(
                intervention_type=InterventionType.COOLING_OFF_ENFORCEMENT,
                severity=RiskLevel.HIGH,
                message="You've reached your hourly achievement limit. Take a short break to let the excitement settle.",
                duration_minutes=15
            )
            return False, intervention
        
        # Check consecutive achievements
        if risk_metrics.consecutive_achievement_count >= self.config["consecutive_achievement_limit"]:
            intervention = InterventionAction(
                intervention_type=InterventionType.COOLING_OFF_ENFORCEMENT,
                severity=RiskLevel.MODERATE,
                message="Multiple achievements unlocked! Take a moment to reflect on your progress before continuing.",
                duration_minutes=15
            )
            return False, intervention
        
        # Check educational ratio (allow educational achievements even if over limit)
        if (achievement_priority != AchievementPriority.EDUCATIONAL and 
            risk_metrics.educational_achievement_ratio < self.config["educational_achievement_ratio_target"] * 0.5):
            
            intervention = InterventionAction(
                intervention_type=InterventionType.EDUCATIONAL_REDIRECT,
                severity=RiskLevel.MODERATE,
                message="Focus on learning! Complete some educational content to unlock more achievement opportunities.",
                duration_minutes=5,
                metadata={"suggested_content": "trading_basics"}
            )
            return False, intervention
        
        # Check for overtrading
        if risk_metrics.overtrading_risk_score > 0.6:
            intervention = InterventionAction(
                intervention_type=InterventionType.OVERTRADING_WARNING,
                severity=RiskLevel.HIGH,
                message="Your trading activity is quite intense. Consider taking a strategic pause to review your positions.",
                duration_minutes=10
            )
            # Allow achievement but log warning
            await self._log_intervention(user_id, intervention)
        
        # Check for high stress
        if risk_metrics.stress_risk_score > 0.7:
            intervention = InterventionAction(
                intervention_type=InterventionType.STRESS_REDUCTION,
                severity=RiskLevel.HIGH,
                message="You seem stressed. Take some deep breaths and consider reviewing your risk management strategy.",
                duration_minutes=5
            )
            return False, intervention
        
        # Check late night trading
        if risk_metrics.late_night_trading:
            intervention = InterventionAction(
                intervention_type=InterventionType.BREAK_SUGGESTION,
                severity=RiskLevel.MODERATE,
                message="It's getting late. Consider getting some rest for clearer thinking tomorrow.",
                duration_minutes=0
            )
            # Allow achievement but suggest break
            await self._log_intervention(user_id, intervention)
        
        return True, None
    
    async def trigger_intervention(self, user_id: str, intervention: InterventionAction):
        """Execute a specific intervention action"""
        
        # Log intervention
        await self._log_intervention(user_id, intervention)
        
        # Set intervention state in Redis
        if intervention.duration_minutes > 0:
            intervention_key = f"interventions:active:{user_id}"
            intervention_data = {
                "type": intervention.intervention_type.value,
                "severity": intervention.severity.value,
                "message": intervention.message,
                "expires_at": (datetime.now() + timedelta(minutes=intervention.duration_minutes)).timestamp(),
                "metadata": json.dumps(intervention.metadata)
            }
            
            await self.redis.hset(intervention_key, mapping=intervention_data)
            await self.redis.expire(intervention_key, intervention.duration_minutes * 60)
        
        # Send intervention message via appropriate channel
        await self._send_intervention_message(user_id, intervention)
    
    async def get_active_interventions(self, user_id: str) -> List[InterventionAction]:
        """Get currently active interventions for a user"""
        intervention_key = f"interventions:active:{user_id}"
        
        if not await self.redis.exists(intervention_key):
            return []
        
        intervention_data = await self.redis.hgetall(intervention_key)
        
        intervention = InterventionAction(
            intervention_type=InterventionType(intervention_data["type"]),
            severity=RiskLevel(intervention_data["severity"]),
            message=intervention_data["message"],
            metadata=json.loads(intervention_data.get("metadata", "{}"))
        )
        
        return [intervention]
    
    async def _get_educational_achievement_ratio(self, user_id: str) -> float:
        """Get ratio of educational to total achievements"""
        # This would query the achievements database
        # For now, return a mock value
        return 0.4  # 40% educational ratio
    
    async def _get_current_loss_streak(self, user_id: str) -> int:
        """Get current consecutive loss streak"""
        # This would query trading results
        return 2  # Mock: 2 consecutive losses
    
    async def _get_average_hold_time(self, user_id: str) -> float:
        """Get average position hold time in minutes"""
        # This would query position history
        return 15.5  # Mock: 15.5 minutes average
    
    async def _get_average_risk_per_trade(self, user_id: str) -> float:
        """Get average risk percentage per trade"""
        # This would query trading history
        return 2.5  # Mock: 2.5% risk per trade
    
    async def _get_current_session_duration(self, user_id: str) -> float:
        """Get current session duration in hours"""
        session_key = f"session:start:{user_id}"
        session_start = await self.redis.get(session_key)
        
        if session_start:
            duration_seconds = time.time() - float(session_start)
            return duration_seconds / 3600  # Convert to hours
        
        return 0.0
    
    async def _get_break_frequency(self, user_id: str) -> float:
        """Get break frequency per hour"""
        # This would analyze activity gaps
        return 0.8  # Mock: 0.8 breaks per hour
    
    async def _get_stress_episodes_count(self, user_id: str) -> int:
        """Get number of stress episodes today"""
        stress_key = f"stress_episodes:{user_id}"
        today_start = datetime.now().replace(hour=0, minute=0, second=0).timestamp()
        
        return await self.redis.zcount(stress_key, today_start, time.time())
    
    async def _get_error_frequency(self, user_id: str) -> float:
        """Get error frequency per hour"""
        error_key = f"errors:{user_id}"
        hour_ago = time.time() - 3600
        
        error_count = await self.redis.zcount(error_key, hour_ago, time.time())
        return float(error_count)
    
    async def _is_user_currently_active(self, user_id: str) -> bool:
        """Check if user is currently active"""
        activity_key = f"user_activities:{user_id}"
        recent_activity = await self.redis.zrevrange(activity_key, 0, 0, withscores=True)
        
        if recent_activity:
            last_activity_time = recent_activity[0][1]
            return (time.time() - last_activity_time) < 300  # Active in last 5 minutes
        
        return False
    
    async def _get_weekend_trading_hours(self, user_id: str) -> float:
        """Get weekend trading hours this week"""
        # This would analyze weekend activity
        return 2.5  # Mock: 2.5 hours weekend trading
    
    async def _get_consecutive_trading_days(self, user_id: str) -> int:
        """Get consecutive days of trading activity"""
        # This would analyze daily trading patterns
        return 5  # Mock: 5 consecutive trading days
    
    async def _store_risk_assessment(self, metrics: UserRiskMetrics):
        """Store risk assessment in Redis for monitoring"""
        assessment_key = f"risk_assessment:{metrics.user_id}"
        
        assessment_data = {
            "timestamp": time.time(),
            "addiction_risk_score": metrics.addiction_risk_score,
            "overtrading_risk_score": metrics.overtrading_risk_score,
            "stress_risk_score": metrics.stress_risk_score,
            "overall_risk_level": metrics.overall_risk_level.value,
            "hourly_achievement_rate": metrics.hourly_achievement_rate,
            "trades_per_hour": metrics.trades_per_hour,
            "session_duration": metrics.session_duration,
            "consecutive_days_trading": metrics.consecutive_days_trading
        }
        
        await self.redis.hset(assessment_key, mapping=assessment_data)
        await self.redis.expire(assessment_key, 86400)  # Expire after 24 hours
        
        # Store in time series for trend analysis
        assessment_history_key = f"risk_history:{metrics.user_id}"
        await self.redis.zadd(
            assessment_history_key,
            {json.dumps(assessment_data): time.time()}
        )
        
        # Keep only last 30 days of history
        cutoff_time = time.time() - (30 * 86400)
        await self.redis.zremrangebyscore(assessment_history_key, 0, cutoff_time)
    
    async def _log_intervention(self, user_id: str, intervention: InterventionAction):
        """Log intervention for monitoring and analysis"""
        logger.info(
            f"Intervention triggered for user {user_id}: "
            f"{intervention.intervention_type.value} - {intervention.severity.value}"
        )
        
        # Store intervention log
        intervention_log_key = f"interventions:log:{user_id}"
        log_entry = {
            "timestamp": time.time(),
            "type": intervention.intervention_type.value,
            "severity": intervention.severity.value,
            "message": intervention.message,
            "duration_minutes": intervention.duration_minutes,
            "metadata": json.dumps(intervention.metadata)
        }
        
        await self.redis.zadd(
            intervention_log_key,
            {json.dumps(log_entry): time.time()}
        )
        
        # Keep intervention logs for 90 days
        await self.redis.expire(intervention_log_key, 90 * 86400)
    
    async def _send_intervention_message(self, user_id: str, intervention: InterventionAction):
        """Send intervention message to user via appropriate channel"""
        # This would integrate with notification service
        # For now, just log the message
        logger.info(f"Intervention message for user {user_id}: {intervention.message}")
    
    async def generate_wellbeing_report(self, user_id: str) -> Dict:
        """Generate comprehensive wellbeing report for user"""
        risk_metrics = await self.assess_user_risk(user_id)
        active_interventions = await self.get_active_interventions(user_id)
        
        # Get risk history for trend analysis
        history_key = f"risk_history:{user_id}"
        history_data = await self.redis.zrevrange(history_key, 0, 29, withscores=True)  # Last 30 entries
        
        risk_trend = []
        for history_json, timestamp in history_data:
            history_item = json.loads(history_json)
            risk_trend.append({
                "date": datetime.fromtimestamp(timestamp).isoformat(),
                "addiction_risk": history_item["addiction_risk_score"],
                "overtrading_risk": history_item["overtrading_risk_score"],
                "stress_risk": history_item["stress_risk_score"],
                "overall_risk": history_item["overall_risk_level"]
            })
        
        return {
            "user_id": user_id,
            "assessment_timestamp": datetime.now().isoformat(),
            "current_risk_level": risk_metrics.overall_risk_level.value,
            "risk_scores": {
                "addiction": risk_metrics.addiction_risk_score,
                "overtrading": risk_metrics.overtrading_risk_score,
                "stress": risk_metrics.stress_risk_score
            },
            "key_metrics": {
                "hourly_achievement_rate": risk_metrics.hourly_achievement_rate,
                "trades_per_hour": risk_metrics.trades_per_hour,
                "session_duration_hours": risk_metrics.session_duration,
                "educational_achievement_ratio": risk_metrics.educational_achievement_ratio,
                "consecutive_trading_days": risk_metrics.consecutive_days_trading
            },
            "active_interventions": [
                {
                    "type": intervention.intervention_type.value,
                    "severity": intervention.severity.value,
                    "message": intervention.message
                }
                for intervention in active_interventions
            ],
            "risk_trend": risk_trend,
            "recommendations": self._generate_recommendations(risk_metrics),
            "support_resources": self._get_support_resources()
        }
    
    def _generate_recommendations(self, metrics: UserRiskMetrics) -> List[str]:
        """Generate personalized recommendations based on risk assessment"""
        recommendations = []
        
        if metrics.addiction_risk_score > 0.5:
            recommendations.append("Consider taking regular breaks between trading sessions")
            recommendations.append("Focus more on educational content to build sustainable skills")
        
        if metrics.overtrading_risk_score > 0.5:
            recommendations.append("Review your trading plan and stick to position size limits")
            recommendations.append("Set daily trade limits to prevent overtrading")
        
        if metrics.stress_risk_score > 0.5:
            recommendations.append("Practice stress management techniques before trading")
            recommendations.append("Consider reducing position sizes until stress levels decrease")
        
        if metrics.educational_achievement_ratio < 0.4:
            recommendations.append("Spend more time on educational content to improve your skills")
            recommendations.append("Complete trading tutorials to unlock better achievement opportunities")
        
        return recommendations
    
    def _get_support_resources(self) -> List[Dict]:
        """Get support resources for users with addiction risk"""
        return [
            {
                "title": "Responsible Trading Guidelines",
                "description": "Learn about healthy trading practices and risk management",
                "url": "/education/responsible-trading"
            },
            {
                "title": "Stress Management for Traders", 
                "description": "Techniques for managing stress and emotions while trading",
                "url": "/education/stress-management"
            },
            {
                "title": "Trading Psychology Course",
                "description": "Comprehensive course on trading psychology and mental health",
                "url": "/education/trading-psychology"
            },
            {
                "title": "Support Community",
                "description": "Connect with other traders and share experiences",
                "url": "/community/support"
            }
        ]