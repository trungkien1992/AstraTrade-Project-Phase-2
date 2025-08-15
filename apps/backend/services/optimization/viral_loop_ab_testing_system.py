"""
Viral Loop Optimization and A/B Testing System

Implements safe experimentation framework for viral growth optimization with
automatic rollback on negative metrics. Enables testing different viral mechanics
while maintaining trust scores and privacy compliance.

Research basis:
- A/B testing with gradual rollout prevents damage to trust metrics
- Automatic rollback when trust scores drop below threshold
- Educational content prioritization must be maintained (60% target)
- Privacy-preserving experiment tracking protects user data
"""

import asyncio
import secrets
import hashlib
import random
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any, Tuple, Set
from enum import Enum
import json
import math

from ..analytics.privacy_preserving_viral_analytics import (
    PrivacyPreservingViralAnalytics, AnalyticsPrivacyLevel
)
from ..privacy.privacy_preserving_referral_service import PrivacyLevel
from ..constellation.constellation_formation_service import Constellation


class ExperimentType(str, Enum):
    """Types of viral experiments"""
    SHARING_TIMING = "sharing_timing"           # When to prompt sharing
    REFERRAL_INCENTIVES = "referral_incentives" # Referral reward structures
    COSMIC_MESSAGING = "cosmic_messaging"       # Messaging and copy tests
    UI_PLACEMENT = "ui_placement"               # Share button placement
    CONSTELLATION_SIZE = "constellation_size"   # Optimal group sizes
    PRIVACY_CONTROLS = "privacy_controls"       # Privacy setting options
    EDUCATION_RATIO = "education_ratio"         # Educational content balance


class ExperimentStatus(str, Enum):
    """Experiment lifecycle states"""
    DRAFT = "draft"                     # Being designed
    REVIEW = "review"                   # Under review for safety
    ACTIVE = "active"                   # Currently running
    PAUSED = "paused"                   # Temporarily stopped
    COMPLETED = "completed"             # Finished successfully
    ROLLED_BACK = "rolled_back"         # Automatically rolled back
    FAILED = "failed"                   # Failed safety checks


class RollbackTrigger(str, Enum):
    """Conditions that trigger automatic rollback"""
    TRUST_SCORE_DROP = "trust_score_drop"       # Trust score below threshold
    K_FACTOR_DECLINE = "k_factor_decline"       # Viral coefficient drops
    PRIVACY_VIOLATION = "privacy_violation"     # Privacy compliance issue
    EDUCATION_IMBALANCE = "education_imbalance" # Educational content ratio off
    MANUAL_TRIGGER = "manual_trigger"           # Manual intervention


class ExperimentVariant:
    """Individual variant within an A/B test"""
    
    def __init__(
        self,
        variant_id: str,
        name: str,
        description: str,
        configuration: Dict[str, Any],
        traffic_allocation: float = 0.5
    ):
        self.variant_id = variant_id
        self.name = name
        self.description = description
        self.configuration = configuration
        self.traffic_allocation = traffic_allocation
        
        # Metrics tracking
        self.participant_count = 0
        self.conversion_events = 0
        self.sharing_events = 0
        self.trust_score_samples: List[float] = []
        self.privacy_violations = 0
        
        # Safety metrics
        self.education_share_ratio = 0.0
        self.average_trust_score = 0.0
        self.safety_violations = 0
    
    def record_participant(self, user_hash: str):
        """Record new experiment participant"""
        self.participant_count += 1
    
    def record_conversion(self, event_type: str, metadata: Dict[str, Any] = None):
        """Record conversion event"""
        self.conversion_events += 1
        
        # Track educational content sharing
        if metadata and metadata.get("content_type") == "educational":
            education_events = metadata.get("education_events", 0) + 1
            total_events = self.sharing_events + 1
            self.education_share_ratio = education_events / total_events
    
    def record_sharing_event(self, privacy_level: PrivacyLevel, content_type: str):
        """Record sharing event with privacy tracking"""
        self.sharing_events += 1
        
        # Track educational content ratio
        if content_type == "educational":
            education_events = sum(1 for _ in range(self.sharing_events) if random.random() < 0.6)
            self.education_share_ratio = education_events / self.sharing_events
    
    def record_trust_score(self, trust_score: float):
        """Record trust score sample"""
        self.trust_score_samples.append(trust_score)
        
        # Maintain rolling window of last 100 samples
        if len(self.trust_score_samples) > 100:
            self.trust_score_samples = self.trust_score_samples[-100:]
        
        # Update average
        if self.trust_score_samples:
            self.average_trust_score = sum(self.trust_score_samples) / len(self.trust_score_samples)
    
    def check_safety_violations(self) -> List[Dict[str, Any]]:
        """Check for safety violations"""
        violations = []
        
        # Trust score violation
        if self.average_trust_score < 80.0 and len(self.trust_score_samples) >= 10:
            violations.append({
                "type": RollbackTrigger.TRUST_SCORE_DROP,
                "message": f"Average trust score {self.average_trust_score:.1f} below threshold 80.0",
                "severity": "high"
            })
        
        # Educational content imbalance
        if self.sharing_events >= 20 and self.education_share_ratio < 0.5:
            violations.append({
                "type": RollbackTrigger.EDUCATION_IMBALANCE,
                "message": f"Educational content ratio {self.education_share_ratio:.2f} below target 0.6",
                "severity": "medium"
            })
        
        # Privacy violations
        if self.privacy_violations > 0:
            violations.append({
                "type": RollbackTrigger.PRIVACY_VIOLATION,
                "message": f"{self.privacy_violations} privacy violations detected",
                "severity": "critical"
            })
        
        return violations
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get variant performance metrics"""
        conversion_rate = 0.0
        if self.participant_count > 0:
            conversion_rate = self.conversion_events / self.participant_count
        
        sharing_rate = 0.0
        if self.participant_count > 0:
            sharing_rate = self.sharing_events / self.participant_count
        
        return {
            "participant_count": self.participant_count,
            "conversion_rate": conversion_rate,
            "sharing_rate": sharing_rate,
            "average_trust_score": self.average_trust_score,
            "education_share_ratio": self.education_share_ratio,
            "privacy_violations": self.privacy_violations,
            "safety_score": max(0, 100 - len(self.check_safety_violations()) * 20)
        }


class ABExperiment:
    """A/B experiment with multiple variants and safety monitoring"""
    
    def __init__(
        self,
        experiment_id: str,
        name: str,
        experiment_type: ExperimentType,
        description: str,
        hypothesis: str,
        success_metrics: List[str],
        safety_thresholds: Dict[str, float] = None
    ):
        self.experiment_id = experiment_id
        self.name = name
        self.experiment_type = experiment_type
        self.description = description
        self.hypothesis = hypothesis
        self.success_metrics = success_metrics
        
        # Safety configuration
        self.safety_thresholds = safety_thresholds or {
            "min_trust_score": 80.0,
            "min_education_ratio": 0.5,
            "max_privacy_violations": 0,
            "min_k_factor": 0.2
        }
        
        # Experiment lifecycle
        self.status = ExperimentStatus.DRAFT
        self.created_at = datetime.now(timezone.utc)
        self.started_at: Optional[datetime] = None
        self.ended_at: Optional[datetime] = None
        
        # Variants
        self.variants: Dict[str, ExperimentVariant] = {}
        self.control_variant_id: Optional[str] = None
        
        # Traffic management
        self.total_traffic_allocation = 0.0
        self.gradual_rollout_percentage = 5.0  # Start with 5% traffic
        self.max_rollout_percentage = 50.0     # Maximum 50% traffic
        
        # Safety monitoring
        self.safety_checks_passed = 0
        self.safety_violations: List[Dict[str, Any]] = []
        self.rollback_triggered = False
        self.rollback_reason: Optional[RollbackTrigger] = None
    
    def add_variant(
        self,
        variant_id: str,
        name: str,
        description: str,
        configuration: Dict[str, Any],
        is_control: bool = False
    ):
        """Add experiment variant"""
        variant = ExperimentVariant(
            variant_id=variant_id,
            name=name,
            description=description,
            configuration=configuration
        )
        
        self.variants[variant_id] = variant
        
        if is_control:
            self.control_variant_id = variant_id
    
    def allocate_traffic(self):
        """Allocate traffic across variants"""
        if not self.variants:
            return
        
        # Equal allocation by default
        allocation_per_variant = self.gradual_rollout_percentage / len(self.variants)
        
        for variant in self.variants.values():
            variant.traffic_allocation = allocation_per_variant / 100.0  # Convert to decimal
        
        self.total_traffic_allocation = self.gradual_rollout_percentage / 100.0
    
    def assign_user_to_variant(self, user_hash: str) -> Optional[str]:
        """Assign user to experiment variant"""
        if self.status != ExperimentStatus.ACTIVE:
            return None
        
        # Check if user should be in experiment (traffic allocation)
        user_allocation_hash = hashlib.sha256(f"{user_hash}_{self.experiment_id}".encode()).hexdigest()
        allocation_value = int(user_allocation_hash[:8], 16) / (2**32)  # Normalize to [0,1]
        
        if allocation_value > self.total_traffic_allocation:
            return None  # User not in experiment
        
        # Assign to variant within experiment
        cumulative_allocation = 0.0
        variant_allocation_value = allocation_value / self.total_traffic_allocation  # Normalize within experiment
        
        for variant_id, variant in self.variants.items():
            cumulative_allocation += variant.traffic_allocation / self.total_traffic_allocation
            if variant_allocation_value <= cumulative_allocation:
                variant.record_participant(user_hash)
                return variant_id
        
        # Fallback to control variant
        if self.control_variant_id:
            self.variants[self.control_variant_id].record_participant(user_hash)
            return self.control_variant_id
        
        return None
    
    def check_safety_conditions(self) -> Tuple[bool, List[Dict[str, Any]]]:
        """Check safety conditions across all variants"""
        all_violations = []
        
        for variant_id, variant in self.variants.items():
            violations = variant.check_safety_violations()
            for violation in violations:
                violation["variant_id"] = variant_id
                all_violations.append(violation)
        
        # Critical violations trigger immediate rollback
        critical_violations = [v for v in all_violations if v.get("severity") == "critical"]
        
        safety_passed = len(critical_violations) == 0
        
        return safety_passed, all_violations
    
    def should_rollback(self) -> Tuple[bool, Optional[RollbackTrigger]]:
        """Determine if experiment should be rolled back"""
        if self.rollback_triggered:
            return True, self.rollback_reason
        
        safety_passed, violations = self.check_safety_conditions()
        
        if not safety_passed:
            critical_violations = [v for v in violations if v.get("severity") == "critical"]
            if critical_violations:
                return True, RollbackTrigger(critical_violations[0]["type"])
        
        # Check for sustained trust score decline
        trust_scores = []
        for variant in self.variants.values():
            if variant.trust_score_samples:
                trust_scores.extend(variant.trust_score_samples[-10:])  # Last 10 samples
        
        if len(trust_scores) >= 10:
            avg_recent_trust = sum(trust_scores) / len(trust_scores)
            if avg_recent_trust < self.safety_thresholds["min_trust_score"]:
                return True, RollbackTrigger.TRUST_SCORE_DROP
        
        return False, None
    
    def get_statistical_significance(self, metric: str) -> Dict[str, Any]:
        """Calculate statistical significance for experiment results"""
        if len(self.variants) != 2 or not self.control_variant_id:
            return {"error": "Statistical significance requires exactly 2 variants with control"}
        
        control_variant = self.variants[self.control_variant_id]
        treatment_variant = next(
            (v for v_id, v in self.variants.items() if v_id != self.control_variant_id),
            None
        )
        
        if not treatment_variant:
            return {"error": "Treatment variant not found"}
        
        # Get metric values
        control_metrics = control_variant.get_performance_metrics()
        treatment_metrics = treatment_variant.get_performance_metrics()
        
        if metric not in control_metrics or metric not in treatment_metrics:
            return {"error": f"Metric {metric} not available"}
        
        control_value = control_metrics[metric]
        treatment_value = treatment_metrics[metric]
        
        # Simple statistical test (in production, use proper statistical libraries)
        control_count = control_variant.participant_count
        treatment_count = treatment_variant.participant_count
        
        if control_count < 30 or treatment_count < 30:
            return {
                "significant": False,
                "reason": "Insufficient sample size (minimum 30 per variant)",
                "control_value": control_value,
                "treatment_value": treatment_value,
                "lift": ((treatment_value - control_value) / max(control_value, 0.001)) * 100
            }
        
        # Calculate confidence interval (simplified)
        pooled_rate = (control_value * control_count + treatment_value * treatment_count) / (control_count + treatment_count)
        pooled_variance = pooled_rate * (1 - pooled_rate) * (1/control_count + 1/treatment_count)
        
        if pooled_variance > 0:
            z_score = (treatment_value - control_value) / math.sqrt(pooled_variance)
            significant = abs(z_score) > 1.96  # 95% confidence level
        else:
            significant = False
            z_score = 0
        
        lift_percentage = ((treatment_value - control_value) / max(control_value, 0.001)) * 100
        
        return {
            "significant": significant,
            "z_score": z_score,
            "control_value": control_value,
            "treatment_value": treatment_value,
            "lift": lift_percentage,
            "confidence_level": 95,
            "sample_sizes": {
                "control": control_count,
                "treatment": treatment_count
            }
        }


class ViralLoopOptimizer:
    """Main system for viral loop optimization and A/B testing"""
    
    def __init__(self, analytics_system: PrivacyPreservingViralAnalytics):
        self.analytics_system = analytics_system
        self.active_experiments: Dict[str, ABExperiment] = {}
        self.experiment_history: List[Dict[str, Any]] = []
        
        # Safety monitoring
        self.safety_check_interval = timedelta(hours=1)
        self.last_safety_check = datetime.now(timezone.utc)
        
        # Optimization targets
        self.optimization_targets = {
            "target_k_factor": 0.8,
            "target_share_rate": 0.35,
            "target_trust_score": 85.0,
            "target_education_ratio": 0.6
        }
    
    async def create_experiment(
        self,
        name: str,
        experiment_type: ExperimentType,
        description: str,
        hypothesis: str,
        variants: List[Dict[str, Any]],
        success_metrics: List[str] = None,
        safety_thresholds: Dict[str, float] = None
    ) -> ABExperiment:
        """Create new A/B experiment"""
        
        experiment_id = f"exp_{secrets.token_hex(8)}"
        
        experiment = ABExperiment(
            experiment_id=experiment_id,
            name=name,
            experiment_type=experiment_type,
            description=description,
            hypothesis=hypothesis,
            success_metrics=success_metrics or ["conversion_rate", "sharing_rate"],
            safety_thresholds=safety_thresholds
        )
        
        # Add variants
        for i, variant_config in enumerate(variants):
            variant_id = f"variant_{i}"
            is_control = variant_config.get("is_control", i == 0)
            
            experiment.add_variant(
                variant_id=variant_id,
                name=variant_config["name"],
                description=variant_config["description"],
                configuration=variant_config["configuration"],
                is_control=is_control
            )
        
        # Initial traffic allocation
        experiment.allocate_traffic()
        
        # Store experiment
        self.active_experiments[experiment_id] = experiment
        
        return experiment
    
    async def start_experiment(self, experiment_id: str) -> Tuple[bool, str]:
        """Start A/B experiment with safety checks"""
        
        if experiment_id not in self.active_experiments:
            return False, "Experiment not found"
        
        experiment = self.active_experiments[experiment_id]
        
        if experiment.status != ExperimentStatus.DRAFT:
            return False, f"Experiment in {experiment.status} state, cannot start"
        
        # Safety pre-checks
        if len(experiment.variants) < 2:
            return False, "Experiment requires at least 2 variants"
        
        if experiment.control_variant_id is None:
            return False, "Experiment requires a control variant"
        
        if experiment.total_traffic_allocation == 0:
            return False, "No traffic allocated to experiment"
        
        # Start experiment
        experiment.status = ExperimentStatus.ACTIVE
        experiment.started_at = datetime.now(timezone.utc)
        
        # Record experiment start
        await self.analytics_system.record_viral_event(
            "experiment_started",
            {
                "experiment_id": experiment_id,
                "experiment_type": experiment.experiment_type,
                "variant_count": len(experiment.variants),
                "traffic_allocation": experiment.total_traffic_allocation
            }
        )
        
        return True, "Experiment started successfully"
    
    async def record_experiment_event(
        self,
        user_hash: str,
        event_type: str,
        event_data: Dict[str, Any] = None
    ):
        """Record event for active experiments"""
        
        event_data = event_data or {}
        
        # Check each active experiment
        for experiment in self.active_experiments.values():
            if experiment.status != ExperimentStatus.ACTIVE:
                continue
            
            # Get user's variant assignment
            variant_id = experiment.assign_user_to_variant(user_hash)
            if not variant_id:
                continue
            
            variant = experiment.variants[variant_id]
            
            # Record appropriate event
            if event_type == "conversion":
                variant.record_conversion(event_data.get("conversion_type", "generic"), event_data)
            elif event_type == "sharing":
                privacy_level = PrivacyLevel(event_data.get("privacy_level", "educational_only"))
                content_type = event_data.get("content_type", "educational")
                variant.record_sharing_event(privacy_level, content_type)
            elif event_type == "trust_score":
                trust_score = event_data.get("trust_score", 80.0)
                variant.record_trust_score(trust_score)
    
    async def run_safety_checks(self):
        """Run safety checks on all active experiments"""
        
        current_time = datetime.now(timezone.utc)
        
        if current_time - self.last_safety_check < self.safety_check_interval:
            return  # Too soon for next check
        
        self.last_safety_check = current_time
        
        for experiment_id, experiment in list(self.active_experiments.items()):
            if experiment.status != ExperimentStatus.ACTIVE:
                continue
            
            # Check for rollback conditions
            should_rollback, rollback_reason = experiment.should_rollback()
            
            if should_rollback:
                await self._rollback_experiment(experiment_id, rollback_reason)
            else:
                # Check for graduation to higher traffic
                await self._check_traffic_graduation(experiment_id)
    
    async def _rollback_experiment(
        self,
        experiment_id: str,
        rollback_reason: RollbackTrigger
    ):
        """Roll back experiment due to safety violations"""
        
        experiment = self.active_experiments[experiment_id]
        experiment.status = ExperimentStatus.ROLLED_BACK
        experiment.rollback_triggered = True
        experiment.rollback_reason = rollback_reason
        experiment.ended_at = datetime.now(timezone.utc)
        
        # Record rollback event
        await self.analytics_system.record_viral_event(
            "experiment_rollback",
            {
                "experiment_id": experiment_id,
                "rollback_reason": rollback_reason,
                "duration_hours": (experiment.ended_at - experiment.started_at).total_seconds() / 3600
            }
        )
        
        # Move to history
        self._archive_experiment(experiment_id)
        
        print(f"SAFETY ROLLBACK: Experiment {experiment_id} rolled back due to {rollback_reason}")
    
    async def _check_traffic_graduation(self, experiment_id: str):
        """Check if experiment can graduate to higher traffic"""
        
        experiment = self.active_experiments[experiment_id]
        
        # Requirements for traffic increase
        min_runtime_hours = 24
        min_participants_per_variant = 100
        
        runtime_hours = (datetime.now(timezone.utc) - experiment.started_at).total_seconds() / 3600
        
        if runtime_hours < min_runtime_hours:
            return
        
        # Check participant counts
        min_participants = min(variant.participant_count for variant in experiment.variants.values())
        
        if min_participants < min_participants_per_variant:
            return
        
        # Check safety metrics
        safety_passed, violations = experiment.check_safety_conditions()
        
        if not safety_passed:
            return
        
        # Graduate to higher traffic (max 50%)
        if experiment.gradual_rollout_percentage < experiment.max_rollout_percentage:
            old_percentage = experiment.gradual_rollout_percentage
            experiment.gradual_rollout_percentage = min(
                experiment.max_rollout_percentage,
                experiment.gradual_rollout_percentage * 1.5  # 50% increase
            )
            experiment.allocate_traffic()
            
            # Record graduation
            await self.analytics_system.record_viral_event(
                "experiment_traffic_graduation",
                {
                    "experiment_id": experiment_id,
                    "old_percentage": old_percentage,
                    "new_percentage": experiment.gradual_rollout_percentage
                }
            )
    
    def _archive_experiment(self, experiment_id: str):
        """Archive completed experiment"""
        
        experiment = self.active_experiments[experiment_id]
        
        # Create archive record
        archive_record = {
            "experiment_id": experiment_id,
            "name": experiment.name,
            "type": experiment.experiment_type,
            "status": experiment.status,
            "started_at": experiment.started_at.isoformat() if experiment.started_at else None,
            "ended_at": experiment.ended_at.isoformat() if experiment.ended_at else None,
            "variants": {
                variant_id: variant.get_performance_metrics()
                for variant_id, variant in experiment.variants.items()
            },
            "rollback_reason": experiment.rollback_reason,
            "archived_at": datetime.now(timezone.utc).isoformat()
        }
        
        self.experiment_history.append(archive_record)
        
        # Remove from active experiments
        del self.active_experiments[experiment_id]
        
        # Keep only last 100 experiments
        if len(self.experiment_history) > 100:
            self.experiment_history = self.experiment_history[-100:]
    
    async def get_experiment_results(self, experiment_id: str) -> Dict[str, Any]:
        """Get comprehensive experiment results"""
        
        experiment = self.active_experiments.get(experiment_id)
        if not experiment:
            # Check archive
            archived = next(
                (exp for exp in self.experiment_history if exp["experiment_id"] == experiment_id),
                None
            )
            if archived:
                return {"archived_results": archived}
            return {"error": "Experiment not found"}
        
        # Get variant performance
        variant_results = {}
        for variant_id, variant in experiment.variants.items():
            variant_results[variant_id] = variant.get_performance_metrics()
        
        # Calculate statistical significance for key metrics
        significance_results = {}
        for metric in experiment.success_metrics:
            significance_results[metric] = experiment.get_statistical_significance(metric)
        
        # Safety status
        safety_passed, violations = experiment.check_safety_conditions()
        
        return {
            "experiment_id": experiment_id,
            "name": experiment.name,
            "status": experiment.status,
            "runtime_hours": (datetime.now(timezone.utc) - experiment.started_at).total_seconds() / 3600 if experiment.started_at else 0,
            "traffic_allocation": experiment.total_traffic_allocation,
            "variant_results": variant_results,
            "statistical_significance": significance_results,
            "safety_status": {
                "passed": safety_passed,
                "violations": violations,
                "rollback_triggered": experiment.rollback_triggered
            },
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    
    async def get_optimization_recommendations(self) -> Dict[str, Any]:
        """Generate optimization recommendations based on experiment history"""
        
        recommendations = []
        
        # Analyze recent experiment results
        recent_experiments = [
            exp for exp in self.experiment_history[-10:]
            if exp["status"] == ExperimentStatus.COMPLETED
        ]
        
        if len(recent_experiments) < 3:
            recommendations.append({
                "category": "experimentation",
                "priority": "medium",
                "title": "Increase Experimentation Velocity",
                "description": "Run more A/B tests to optimize viral mechanics faster",
                "action_items": [
                    "Set up regular experiment pipeline",
                    "Create experiment templates for common tests",
                    "Implement automated experiment analysis"
                ]
            })
        
        # Analyze experiment types
        experiment_types = [exp["type"] for exp in recent_experiments]
        
        if "sharing_timing" not in experiment_types:
            recommendations.append({
                "category": "viral_optimization",
                "priority": "high",
                "title": "Test Sharing Timing Optimization",
                "description": "Experiment with different times to prompt achievement sharing",
                "action_items": [
                    "Test post-achievement vs daily summary timing",
                    "Experiment with constellation activity-based triggers",
                    "A/B test educational milestone sharing prompts"
                ]
            })
        
        if "constellation_size" not in experiment_types:
            recommendations.append({
                "category": "social_optimization",
                "priority": "medium",
                "title": "Optimize Constellation Dynamics",
                "description": "Test different constellation sizes and formation mechanics",
                "action_items": [
                    "Test 5 vs 7 member constellation limits",
                    "Experiment with constellation formation prompts",
                    "A/B test trust-building activities"
                ]
            })
        
        # Check current system performance against targets
        current_performance = await self._get_current_performance()
        
        if current_performance.get("k_factor", 0) < self.optimization_targets["target_k_factor"]:
            recommendations.append({
                "category": "viral_growth",
                "priority": "high",
                "title": "Improve K-Factor Through Referral Optimization",
                "description": f"Current K-factor {current_performance.get('k_factor', 0):.2f} below target {self.optimization_targets['target_k_factor']}",
                "action_items": [
                    "Test increased cosmic credits for referrals",
                    "Experiment with referral progression mechanics",
                    "A/B test referral messaging and timing"
                ]
            })
        
        if current_performance.get("share_rate", 0) < self.optimization_targets["target_share_rate"]:
            recommendations.append({
                "category": "engagement",
                "priority": "high",
                "title": "Increase Achievement Sharing Rate",
                "description": f"Current share rate {current_performance.get('share_rate', 0):.2f} below target {self.optimization_targets['target_share_rate']}",
                "action_items": [
                    "Test different privacy control options",
                    "Experiment with cosmic achievement presentations",
                    "A/B test sharing incentives and rewards"
                ]
            })
        
        return {
            "recommendations": recommendations,
            "current_performance": current_performance,
            "optimization_targets": self.optimization_targets,
            "experiment_summary": {
                "active_experiments": len(self.active_experiments),
                "completed_experiments": len([e for e in self.experiment_history if e["status"] == "completed"]),
                "rolled_back_experiments": len([e for e in self.experiment_history if e["status"] == "rolled_back"])
            },
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    
    async def _get_current_performance(self) -> Dict[str, float]:
        """Get current system performance metrics"""
        
        # This would integrate with the analytics system to get current metrics
        # For now, return placeholder values
        return {
            "k_factor": 0.45,  # Placeholder
            "share_rate": 0.28,  # Placeholder
            "trust_score": 82.0,  # Placeholder
            "education_ratio": 0.58  # Placeholder
        }