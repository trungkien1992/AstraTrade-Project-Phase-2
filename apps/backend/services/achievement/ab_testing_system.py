#!/usr/bin/env python3
"""
A/B Testing Infrastructure for Achievement System

Implements safe, statistical A/B testing for achievement timing, display,
and user experience optimization with real-time monitoring and automatic
rollback capabilities to prevent user harm.

Key Features:
- Gradual rollout system (5% → 15% → 30% → 50% → 100%)
- Real-time metrics collection and statistical analysis
- Automatic rollback on negative performance indicators
- Cohort-based testing (new users vs experienced traders)
- Multi-variant testing (A/B/C/D tests)
- Statistical significance validation
- Safe experimentation guardrails
"""

import asyncio
import time
import json
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Set, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import redis.asyncio as redis
import numpy as np
from scipy import stats


logger = logging.getLogger(__name__)


class ExperimentStatus(Enum):
    """Status of A/B testing experiments"""
    DRAFT = "draft"                    # Experiment configured but not started
    RAMPING = "ramping"               # Gradual rollout in progress  
    RUNNING = "running"               # Full rollout active
    PAUSED = "paused"                 # Temporarily paused
    COMPLETED = "completed"           # Experiment completed successfully
    STOPPED = "stopped"               # Manually stopped
    ROLLED_BACK = "rolled_back"       # Automatically rolled back due to negative metrics


class ExperimentType(Enum):
    """Types of experiments for achievement system"""
    TIMING_OPTIMIZATION = "timing_optimization"     # Test different delay intervals
    DISPLAY_POSITION = "display_position"           # Test notification positions
    DISPLAY_STYLE = "display_style"                 # Test visual styles
    INTERRUPTION_LEVEL = "interruption_level"       # Test interruption tolerance
    ACHIEVEMENT_FREQUENCY = "achievement_frequency"  # Test frequency limits
    CONTEXTUAL_RULES = "contextual_rules"           # Test context-sensitive rules


class MetricType(Enum):
    """Types of metrics tracked in experiments"""
    # Primary metrics (key success indicators)
    ACHIEVEMENT_ENGAGEMENT_RATE = "achievement_engagement_rate"
    TIME_TO_ACKNOWLEDGMENT_MS = "time_to_acknowledgment_ms"
    USER_SATISFACTION_SCORE = "user_satisfaction_score"
    LEARNING_PROGRESSION_RATE = "learning_progression_rate"
    
    # Secondary metrics (supporting indicators)
    SESSION_DURATION_MINUTES = "session_duration_minutes"
    TRADING_FREQUENCY = "trading_frequency"
    ERROR_RATE = "error_rate"
    FEATURE_ADOPTION_RATE = "feature_adoption_rate"
    
    # Safety metrics (guardrail indicators)
    STRESS_LEVEL_INCREASE = "stress_level_increase"
    OVERTRADING_INCIDENTS = "overtrading_incidents"
    USER_COMPLAINTS = "user_complaints"
    ACHIEVEMENT_DISMISSAL_RATE = "achievement_dismissal_rate"


@dataclass
class ExperimentVariant:
    """Configuration for an experiment variant"""
    variant_id: str
    name: str
    description: str
    config: Dict[str, Any]
    expected_impact: str
    traffic_percentage: float = 0.0  # Current traffic allocation


@dataclass
class ExperimentConfig:
    """Complete experiment configuration"""
    experiment_id: str
    name: str
    description: str
    experiment_type: ExperimentType
    variants: List[ExperimentVariant]
    
    # Rollout configuration
    ramp_up_schedule: List[Tuple[float, timedelta]]  # (percentage, duration)
    max_duration_days: int = 30
    
    # Statistical configuration
    minimum_sample_size: int = 1000
    statistical_power: float = 0.8
    significance_level: float = 0.05
    minimum_effect_size: float = 0.05  # 5% minimum detectable effect
    
    # Safety configuration
    primary_metrics: List[MetricType]
    safety_metrics: List[MetricType]
    rollback_thresholds: Dict[MetricType, float]
    
    # Targeting
    target_user_cohorts: List[str] = field(default_factory=lambda: ["all"])
    exclude_user_segments: List[str] = field(default_factory=list)
    
    # Metadata
    owner: str = "achievement_team"
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: ExperimentStatus = ExperimentStatus.DRAFT


@dataclass
class ExperimentMetrics:
    """Collected metrics for an experiment"""
    experiment_id: str
    variant_id: str
    user_id: str
    timestamp: datetime
    metrics: Dict[MetricType, float]
    user_cohort: str
    session_id: str


@dataclass
class StatisticalResult:
    """Results of statistical significance testing"""
    metric_type: MetricType
    control_mean: float
    variant_mean: float
    effect_size: float
    p_value: float
    confidence_interval: Tuple[float, float]
    is_significant: bool
    power: float
    sample_size_control: int
    sample_size_variant: int


class ExperimentManager:
    """
    Manages A/B testing experiments for achievement system optimization.
    
    Provides safe experimentation with gradual rollout, real-time monitoring,
    and automatic rollback to protect user experience.
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        
        # Keys for Redis storage
        self.experiments_key = "ab_experiments"
        self.assignments_key = "ab_assignments"
        self.metrics_key = "ab_metrics"
        
        # Configuration
        self.config = self._initialize_config()
        self.predefined_experiments = self._initialize_experiments()
        
        # Monitoring
        self.monitoring_interval_seconds = 300  # 5 minutes
        
    def _initialize_config(self) -> Dict:
        """Initialize A/B testing system configuration"""
        return {
            "hash_seed": "astratrade_ab_2024",  # For consistent user assignment
            "ramp_up_intervals": [0.05, 0.15, 0.30, 0.50, 1.0],  # 5%, 15%, 30%, 50%, 100%
            "ramp_up_durations": [2, 3, 5, 7, -1],  # Days for each ramp, -1 = indefinite
            "min_users_per_variant": 100,
            "safety_check_interval_minutes": 15,
            "automatic_rollback_enabled": True,
            "statistical_analysis_interval_hours": 6,
            "cohort_definitions": {
                "new_users": "user_age_days < 7",
                "experienced_traders": "user_age_days >= 30 AND trades_count >= 100", 
                "high_engagement": "daily_session_duration_avg > 60",
                "low_engagement": "daily_session_duration_avg < 30"
            }
        }
    
    def _initialize_experiments(self) -> Dict[str, ExperimentConfig]:
        """Initialize predefined experiments for achievement system"""
        
        experiments = {}
        
        # Timing Optimization Experiment
        experiments["timing_optimization_v1"] = ExperimentConfig(
            experiment_id="timing_optimization_v1",
            name="Achievement Timing Optimization",
            description="Test optimal delay intervals for achievement notifications",
            experiment_type=ExperimentType.TIMING_OPTIMIZATION,
            variants=[
                ExperimentVariant(
                    variant_id="control",
                    name="Current (60s base)",
                    description="Current timing with 60s base interval",
                    config={"base_interval": 60, "jitter": 0.3}
                ),
                ExperimentVariant(
                    variant_id="shorter",
                    name="Shorter (30s base)",
                    description="Shorter intervals with 30s base",
                    config={"base_interval": 30, "jitter": 0.3}
                ),
                ExperimentVariant(
                    variant_id="longer",
                    name="Longer (90s base)",
                    description="Longer intervals with 90s base", 
                    config={"base_interval": 90, "jitter": 0.3}
                ),
                ExperimentVariant(
                    variant_id="variable",
                    name="Variable (45-75s)",
                    description="Variable timing based on context",
                    config={"base_interval": 60, "jitter": 0.5, "context_adaptive": True}
                )
            ],
            ramp_up_schedule=[
                (0.05, timedelta(days=2)),
                (0.15, timedelta(days=3)),
                (0.30, timedelta(days=5)),
                (0.50, timedelta(days=7)),
                (1.0, timedelta(days=-1))
            ],
            minimum_sample_size=1000,
            primary_metrics=[
                MetricType.ACHIEVEMENT_ENGAGEMENT_RATE,
                MetricType.TIME_TO_ACKNOWLEDGMENT_MS,
                MetricType.USER_SATISFACTION_SCORE
            ],
            safety_metrics=[
                MetricType.STRESS_LEVEL_INCREASE,
                MetricType.ACHIEVEMENT_DISMISSAL_RATE,
                MetricType.USER_COMPLAINTS
            ],
            rollback_thresholds={
                MetricType.ACHIEVEMENT_ENGAGEMENT_RATE: -0.10,  # 10% decrease
                MetricType.STRESS_LEVEL_INCREASE: 0.15,          # 15% increase
                MetricType.USER_COMPLAINTS: 0.05                # 5% increase
            }
        )
        
        # Display Position Experiment
        experiments["display_position_v1"] = ExperimentConfig(
            experiment_id="display_position_v1", 
            name="Achievement Display Position",
            description="Test optimal positions for achievement notifications",
            experiment_type=ExperimentType.DISPLAY_POSITION,
            variants=[
                ExperimentVariant(
                    variant_id="bottom_right",
                    name="Bottom Right (Control)",
                    description="Current bottom-right position",
                    config={"position": "bottom_right", "offset": {"x": 20, "y": 20}}
                ),
                ExperimentVariant(
                    variant_id="bottom_left", 
                    name="Bottom Left",
                    description="Bottom-left position for left-handed users",
                    config={"position": "bottom_left", "offset": {"x": 20, "y": 20}}
                ),
                ExperimentVariant(
                    variant_id="sidebar",
                    name="Sidebar",
                    description="Dedicated sidebar for achievements",
                    config={"position": "sidebar", "width": 300}
                )
            ],
            ramp_up_schedule=[
                (0.05, timedelta(days=1)),
                (0.15, timedelta(days=2)), 
                (0.30, timedelta(days=3)),
                (0.50, timedelta(days=5)),
                (1.0, timedelta(days=-1))
            ],
            minimum_sample_size=500,
            primary_metrics=[
                MetricType.ACHIEVEMENT_ENGAGEMENT_RATE,
                MetricType.TIME_TO_ACKNOWLEDGMENT_MS
            ],
            safety_metrics=[
                MetricType.ERROR_RATE,
                MetricType.ACHIEVEMENT_DISMISSAL_RATE
            ],
            rollback_thresholds={
                MetricType.ACHIEVEMENT_ENGAGEMENT_RATE: -0.08,
                MetricType.ERROR_RATE: 0.10
            }
        )
        
        return experiments
    
    async def create_experiment(self, config: ExperimentConfig) -> bool:
        """Create a new experiment"""
        
        # Validate experiment configuration
        validation_result = await self._validate_experiment_config(config)
        if not validation_result["valid"]:
            logger.error(f"Invalid experiment config: {validation_result['errors']}")
            return False
        
        # Store experiment configuration
        experiment_key = f"{self.experiments_key}:{config.experiment_id}"
        config_data = {
            "config": json.dumps(self._serialize_experiment_config(config)),
            "status": config.status.value,
            "created_at": time.time(),
            "updated_at": time.time()
        }
        
        await self.redis.hset(experiment_key, mapping=config_data)
        
        logger.info(f"Created experiment: {config.experiment_id}")
        return True
    
    async def start_experiment(self, experiment_id: str) -> bool:
        """Start an experiment with gradual ramp-up"""
        
        experiment = await self.get_experiment(experiment_id)
        if not experiment:
            logger.error(f"Experiment not found: {experiment_id}")
            return False
        
        if experiment.status != ExperimentStatus.DRAFT:
            logger.error(f"Cannot start experiment in status: {experiment.status}")
            return False
        
        # Update experiment status
        experiment.status = ExperimentStatus.RAMPING
        experiment.start_time = datetime.now()
        
        # Start with first ramp percentage
        if experiment.ramp_up_schedule:
            first_ramp = experiment.ramp_up_schedule[0]
            experiment.variants[0].traffic_percentage = first_ramp[0] * 100
        
        await self._update_experiment(experiment)
        
        # Schedule ramp-up progression
        await self._schedule_ramp_progression(experiment)
        
        # Start safety monitoring
        await self._start_safety_monitoring(experiment)
        
        logger.info(f"Started experiment: {experiment_id}")
        return True
    
    async def get_user_variant(
        self,
        experiment_id: str,
        user_id: str,
        user_cohort: str = "all"
    ) -> Optional[ExperimentVariant]:
        """Get the variant assigned to a specific user"""
        
        experiment = await self.get_experiment(experiment_id)
        if not experiment or experiment.status not in [ExperimentStatus.RAMPING, ExperimentStatus.RUNNING]:
            return None
        
        # Check if user is in target cohort
        if user_cohort not in experiment.target_user_cohorts and "all" not in experiment.target_user_cohorts:
            return None
        
        # Check if user is excluded
        if user_cohort in experiment.exclude_user_segments:
            return None
        
        # Check existing assignment
        assignment_key = f"{self.assignments_key}:{experiment_id}:{user_id}"
        existing_assignment = await self.redis.get(assignment_key)
        
        if existing_assignment:
            variant_id = existing_assignment
            return next((v for v in experiment.variants if v.variant_id == variant_id), None)
        
        # Calculate hash-based assignment for consistency
        hash_input = f"{self.config['hash_seed']}:{experiment_id}:{user_id}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        assignment_percentile = (hash_value % 10000) / 100  # 0-99.99
        
        # Get current traffic allocation
        current_traffic = await self._get_current_traffic_allocation(experiment)
        
        # Assign variant based on traffic allocation
        cumulative_percentage = 0
        for variant in experiment.variants:
            variant_traffic = current_traffic.get(variant.variant_id, 0)
            cumulative_percentage += variant_traffic
            
            if assignment_percentile < cumulative_percentage:
                # Store assignment
                await self.redis.set(
                    assignment_key,
                    variant.variant_id,
                    ex=86400 * experiment.max_duration_days
                )
                return variant
        
        # No variant assigned (user outside experiment traffic)
        return None
    
    async def record_metrics(
        self,
        experiment_id: str,
        user_id: str,
        metrics_data: Dict[MetricType, float],
        user_cohort: str = "all",
        session_id: str = None
    ):
        """Record metrics for experiment analysis"""
        
        variant = await self.get_user_variant(experiment_id, user_id, user_cohort)
        if not variant:
            return  # User not in experiment
        
        # Create metrics record
        metrics = ExperimentMetrics(
            experiment_id=experiment_id,
            variant_id=variant.variant_id,
            user_id=user_id,
            timestamp=datetime.now(),
            metrics=metrics_data,
            user_cohort=user_cohort,
            session_id=session_id or f"session_{int(time.time())}"
        )
        
        # Store metrics in time series
        metrics_key = f"{self.metrics_key}:{experiment_id}:{variant.variant_id}"
        metrics_value = {
            "user_id": user_id,
            "timestamp": metrics.timestamp.timestamp(),
            "metrics": {k.value: v for k, v in metrics_data.items()},
            "cohort": user_cohort,
            "session_id": metrics.session_id
        }
        
        await self.redis.zadd(
            metrics_key,
            {json.dumps(metrics_value): metrics.timestamp.timestamp()}
        )
        
        # Set expiration (keep metrics for analysis period)
        retention_seconds = 90 * 86400  # 90 days
        await self.redis.expire(metrics_key, retention_seconds)
    
    async def analyze_experiment(self, experiment_id: str) -> Dict[str, Any]:
        """Analyze experiment results with statistical testing"""
        
        experiment = await self.get_experiment(experiment_id)
        if not experiment:
            return {"error": "Experiment not found"}
        
        # Get metrics for all variants
        variant_metrics = {}
        for variant in experiment.variants:
            metrics_key = f"{self.metrics_key}:{experiment_id}:{variant.variant_id}"
            raw_metrics = await self.redis.zrange(metrics_key, 0, -1)
            
            parsed_metrics = []
            for metric_json in raw_metrics:
                metric_data = json.loads(metric_json)
                parsed_metrics.append(metric_data)
            
            variant_metrics[variant.variant_id] = parsed_metrics
        
        # Perform statistical analysis
        results = {}
        control_variant = experiment.variants[0]  # First variant is control
        
        for variant in experiment.variants[1:]:  # Compare against control
            variant_results = {}
            
            for metric_type in experiment.primary_metrics:
                stat_result = await self._calculate_statistical_significance(
                    control_variant.variant_id,
                    variant.variant_id,
                    metric_type,
                    variant_metrics
                )
                
                variant_results[metric_type.value] = {
                    "control_mean": stat_result.control_mean,
                    "variant_mean": stat_result.variant_mean,
                    "effect_size": stat_result.effect_size,
                    "p_value": stat_result.p_value,
                    "confidence_interval": stat_result.confidence_interval,
                    "is_significant": stat_result.is_significant,
                    "statistical_power": stat_result.power,
                    "sample_sizes": {
                        "control": stat_result.sample_size_control,
                        "variant": stat_result.sample_size_variant
                    }
                }
            
            results[variant.variant_id] = variant_results
        
        # Check if experiment has reached statistical significance
        has_winner = any(
            any(metric_data["is_significant"] for metric_data in variant_data.values())
            for variant_data in results.values()
        )
        
        # Calculate overall experiment health
        experiment_health = await self._calculate_experiment_health(experiment_id, variant_metrics)
        
        return {
            "experiment_id": experiment_id,
            "status": experiment.status.value,
            "start_time": experiment.start_time.isoformat() if experiment.start_time else None,
            "duration_days": (datetime.now() - experiment.start_time).days if experiment.start_time else 0,
            "has_statistical_winner": has_winner,
            "variant_results": results,
            "experiment_health": experiment_health,
            "recommendations": self._generate_recommendations(experiment, results, experiment_health)
        }
    
    async def _calculate_statistical_significance(
        self,
        control_variant_id: str,
        test_variant_id: str,
        metric_type: MetricType,
        variant_metrics: Dict[str, List[Dict]]
    ) -> StatisticalResult:
        """Calculate statistical significance between control and test variant"""
        
        # Extract metric values for control and test groups
        control_values = []
        test_values = []
        
        for metric_data in variant_metrics.get(control_variant_id, []):
            if metric_type.value in metric_data["metrics"]:
                control_values.append(metric_data["metrics"][metric_type.value])
        
        for metric_data in variant_metrics.get(test_variant_id, []):
            if metric_type.value in metric_data["metrics"]:
                test_values.append(metric_data["metrics"][metric_type.value])
        
        if len(control_values) < 30 or len(test_values) < 30:
            # Insufficient sample size
            return StatisticalResult(
                metric_type=metric_type,
                control_mean=np.mean(control_values) if control_values else 0,
                variant_mean=np.mean(test_values) if test_values else 0,
                effect_size=0,
                p_value=1.0,
                confidence_interval=(0, 0),
                is_significant=False,
                power=0,
                sample_size_control=len(control_values),
                sample_size_variant=len(test_values)
            )
        
        # Calculate means
        control_mean = np.mean(control_values)
        test_mean = np.mean(test_values)
        
        # Perform t-test
        t_stat, p_value = stats.ttest_ind(control_values, test_values)
        
        # Calculate effect size (Cohen's d)
        pooled_std = np.sqrt(((len(control_values) - 1) * np.var(control_values) + 
                             (len(test_values) - 1) * np.var(test_values)) / 
                            (len(control_values) + len(test_values) - 2))
        effect_size = (test_mean - control_mean) / pooled_std if pooled_std > 0 else 0
        
        # Calculate confidence interval
        se_diff = np.sqrt(np.var(control_values) / len(control_values) + 
                         np.var(test_values) / len(test_values))
        df = len(control_values) + len(test_values) - 2
        t_critical = stats.t.ppf(0.975, df)  # 95% confidence interval
        
        diff = test_mean - control_mean
        margin_of_error = t_critical * se_diff
        confidence_interval = (diff - margin_of_error, diff + margin_of_error)
        
        # Determine statistical significance
        is_significant = p_value < 0.05 and abs(effect_size) >= 0.2  # Medium effect size
        
        # Calculate statistical power (approximation)
        power = self._calculate_power(len(control_values), len(test_values), effect_size)
        
        return StatisticalResult(
            metric_type=metric_type,
            control_mean=control_mean,
            variant_mean=test_mean,
            effect_size=effect_size,
            p_value=p_value,
            confidence_interval=confidence_interval,
            is_significant=is_significant,
            power=power,
            sample_size_control=len(control_values),
            sample_size_variant=len(test_values)
        )
    
    def _calculate_power(self, n1: int, n2: int, effect_size: float) -> float:
        """Calculate statistical power (simplified approximation)"""
        # Simplified power calculation for equal variances
        n_harmonic = 2 / (1/n1 + 1/n2)
        ncp = effect_size * np.sqrt(n_harmonic / 2)  # Non-centrality parameter
        
        # Approximate power using normal distribution
        z_alpha = stats.norm.ppf(0.975)  # Two-tailed test, alpha = 0.05
        power = 1 - stats.norm.cdf(z_alpha - ncp) + stats.norm.cdf(-z_alpha - ncp)
        
        return max(0, min(1, power))
    
    async def _check_safety_thresholds(self, experiment_id: str) -> Dict[str, Any]:
        """Check safety thresholds and determine if rollback is needed"""
        
        experiment = await self.get_experiment(experiment_id)
        if not experiment:
            return {"rollback_needed": False}
        
        rollback_needed = False
        violations = []
        
        # Get recent metrics for safety analysis
        safety_window_hours = 24
        cutoff_time = time.time() - (safety_window_hours * 3600)
        
        for variant in experiment.variants:
            if variant.variant_id == "control":
                continue  # Skip control group for safety checks
            
            metrics_key = f"{self.metrics_key}:{experiment_id}:{variant.variant_id}"
            recent_metrics = await self.redis.zrangebyscore(
                metrics_key, cutoff_time, time.time()
            )
            
            if not recent_metrics:
                continue
            
            # Analyze safety metrics
            for metric_type, threshold in experiment.rollback_thresholds.items():
                metric_values = []
                
                for metric_json in recent_metrics:
                    metric_data = json.loads(metric_json)
                    if metric_type.value in metric_data["metrics"]:
                        metric_values.append(metric_data["metrics"][metric_type.value])
                
                if metric_values:
                    avg_value = np.mean(metric_values)
                    
                    # Check if threshold is violated
                    if (threshold > 0 and avg_value > threshold) or (threshold < 0 and avg_value < threshold):
                        violations.append({
                            "variant_id": variant.variant_id,
                            "metric": metric_type.value,
                            "current_value": avg_value,
                            "threshold": threshold,
                            "violation_magnitude": abs(avg_value - threshold)
                        })
                        rollback_needed = True
        
        return {
            "rollback_needed": rollback_needed,
            "violations": violations,
            "check_timestamp": datetime.now().isoformat()
        }
    
    async def rollback_experiment(self, experiment_id: str, reason: str = "Safety violation"):
        """Rollback experiment to control group"""
        
        experiment = await self.get_experiment(experiment_id)
        if not experiment:
            return False
        
        # Update experiment status
        experiment.status = ExperimentStatus.ROLLED_BACK
        experiment.end_time = datetime.now()
        
        await self._update_experiment(experiment)
        
        # Clear all non-control variant assignments
        # This effectively assigns all users to control group
        assignment_pattern = f"{self.assignments_key}:{experiment_id}:*"
        async for key in self.redis.scan_iter(match=assignment_pattern):
            await self.redis.delete(key)
        
        # Log rollback
        rollback_log = {
            "experiment_id": experiment_id,
            "timestamp": time.time(),
            "reason": reason,
            "previous_status": ExperimentStatus.RUNNING.value
        }
        
        rollback_key = f"ab_rollbacks:{experiment_id}"
        await self.redis.lpush(rollback_key, json.dumps(rollback_log))
        await self.redis.expire(rollback_key, 86400 * 90)  # Keep for 90 days
        
        logger.warning(f"Rolled back experiment {experiment_id}: {reason}")
        return True
    
    # Helper methods for experiment management
    async def get_experiment(self, experiment_id: str) -> Optional[ExperimentConfig]:
        """Get experiment configuration"""
        experiment_key = f"{self.experiments_key}:{experiment_id}"
        experiment_data = await self.redis.hgetall(experiment_key)
        
        if not experiment_data:
            return None
        
        config_json = experiment_data.get("config")
        if config_json:
            return self._deserialize_experiment_config(json.loads(config_json))
        
        return None
    
    def _serialize_experiment_config(self, config: ExperimentConfig) -> Dict:
        """Serialize experiment config for storage"""
        return {
            "experiment_id": config.experiment_id,
            "name": config.name,
            "description": config.description,
            "experiment_type": config.experiment_type.value,
            "variants": [
                {
                    "variant_id": v.variant_id,
                    "name": v.name,
                    "description": v.description,
                    "config": v.config,
                    "expected_impact": v.expected_impact,
                    "traffic_percentage": v.traffic_percentage
                }
                for v in config.variants
            ],
            "ramp_up_schedule": [(p, d.total_seconds()) for p, d in config.ramp_up_schedule],
            "max_duration_days": config.max_duration_days,
            "minimum_sample_size": config.minimum_sample_size,
            "statistical_power": config.statistical_power,
            "significance_level": config.significance_level,
            "minimum_effect_size": config.minimum_effect_size,
            "primary_metrics": [m.value for m in config.primary_metrics],
            "safety_metrics": [m.value for m in config.safety_metrics],
            "rollback_thresholds": {k.value: v for k, v in config.rollback_thresholds.items()},
            "target_user_cohorts": config.target_user_cohorts,
            "exclude_user_segments": config.exclude_user_segments,
            "owner": config.owner,
            "start_time": config.start_time.isoformat() if config.start_time else None,
            "end_time": config.end_time.isoformat() if config.end_time else None,
            "status": config.status.value
        }
    
    def _deserialize_experiment_config(self, data: Dict) -> ExperimentConfig:
        """Deserialize experiment config from storage"""
        # Implementation would convert stored dict back to ExperimentConfig object
        # (Truncated for brevity)
        pass
    
    # Additional helper methods would go here...
    # _validate_experiment_config, _update_experiment, _get_current_traffic_allocation, etc.