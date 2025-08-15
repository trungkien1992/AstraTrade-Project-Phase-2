"""
Economic Stability Engine

Automatically balances the virtual economy to maintain target inflation rate,
currency velocity, and supply ratios. Implements economic theory principles
to create a self-regulating financial ecosystem.

Research basis:
- Target 2.5% annual inflation rate for healthy growth
- Currency velocity of 2.5x monthly circulation prevents stagnation
- 60/40 earned/purchased currency ratio maintains ethical balance
- Automatic adjustments prevent economic manipulation
"""

import asyncio
import math
from datetime import datetime, timezone, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Tuple, Optional
from enum import Enum
import json

from .ethical_currency_system import CurrencyTransaction, TransactionType


class EconomicIndicator(str, Enum):
    """Economic health indicators"""
    INFLATION_RATE = "inflation_rate"
    CURRENCY_VELOCITY = "currency_velocity"  
    SUPPLY_RATIO = "supply_ratio"
    TRANSACTION_VOLUME = "transaction_volume"
    USER_ENGAGEMENT = "user_engagement"


class EconomicTrend(str, Enum):
    """Economic trend directions"""
    RISING = "rising"
    FALLING = "falling"
    STABLE = "stable"
    VOLATILE = "volatile"


class EconomicAlert(str, Enum):
    """Alert levels for economic conditions"""
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class EconomicMetric:
    """Individual economic metric with historical tracking"""
    
    def __init__(self, name: str, target_value: Decimal, tolerance: Decimal):
        self.name = name
        self.target_value = target_value
        self.tolerance = tolerance
        self.current_value = Decimal('0')
        self.history: List[Tuple[datetime, Decimal]] = []
        self.trend = EconomicTrend.STABLE
        self.alert_level = EconomicAlert.NORMAL
    
    def update_value(self, new_value: Decimal):
        """Update metric value and calculate trend"""
        timestamp = datetime.now(timezone.utc)
        
        # Store historical data
        self.history.append((timestamp, new_value))
        
        # Keep only last 30 days of history
        cutoff_date = timestamp - timedelta(days=30)
        self.history = [(ts, val) for ts, val in self.history if ts > cutoff_date]
        
        # Calculate trend
        old_value = self.current_value
        self.current_value = new_value
        
        if len(self.history) >= 3:
            self.trend = self._calculate_trend()
        
        # Update alert level
        self.alert_level = self._calculate_alert_level()
    
    def _calculate_trend(self) -> EconomicTrend:
        """Calculate trend based on recent history"""
        if len(self.history) < 3:
            return EconomicTrend.STABLE
        
        # Get last 7 values
        recent_values = [val for _, val in self.history[-7:]]
        
        # Calculate average change
        changes = []
        for i in range(1, len(recent_values)):
            change = (recent_values[i] - recent_values[i-1]) / recent_values[i-1]
            changes.append(change)
        
        if not changes:
            return EconomicTrend.STABLE
        
        avg_change = sum(changes) / len(changes)
        change_variance = sum((c - avg_change) ** 2 for c in changes) / len(changes)
        
        # Determine trend
        if change_variance > Decimal('0.1'):  # High variance
            return EconomicTrend.VOLATILE
        elif avg_change > Decimal('0.02'):    # 2% average increase
            return EconomicTrend.RISING
        elif avg_change < Decimal('-0.02'):   # 2% average decrease
            return EconomicTrend.FALLING
        else:
            return EconomicTrend.STABLE
    
    def _calculate_alert_level(self) -> EconomicAlert:
        """Calculate alert level based on deviation from target"""
        deviation = abs(self.current_value - self.target_value) / self.target_value
        
        if deviation <= self.tolerance:
            return EconomicAlert.NORMAL
        elif deviation <= self.tolerance * 2:
            return EconomicAlert.WARNING
        elif deviation <= self.tolerance * 4:
            return EconomicAlert.CRITICAL
        else:
            return EconomicAlert.EMERGENCY
    
    def get_deviation_percentage(self) -> Decimal:
        """Get percentage deviation from target"""
        if self.target_value == 0:
            return Decimal('0')
        return ((self.current_value - self.target_value) / self.target_value) * 100


class EconomicStabilityEngine:
    """Main engine for economic stability and automatic balancing"""
    
    def __init__(self):
        # Economic targets based on research
        self.metrics = {
            EconomicIndicator.INFLATION_RATE: EconomicMetric(
                "Annual Inflation Rate", 
                Decimal('2.5'),    # 2.5% target
                Decimal('0.5')     # ±0.5% tolerance
            ),
            EconomicIndicator.CURRENCY_VELOCITY: EconomicMetric(
                "Monthly Currency Velocity",
                Decimal('2.5'),    # 2.5x circulation target
                Decimal('0.5')     # ±0.5x tolerance
            ),
            EconomicIndicator.SUPPLY_RATIO: EconomicMetric(
                "Earned Currency Ratio",
                Decimal('60.0'),   # 60% earned vs 40% purchased
                Decimal('5.0')     # ±5% tolerance
            ),
            EconomicIndicator.TRANSACTION_VOLUME: EconomicMetric(
                "Daily Transaction Volume",
                Decimal('1000'),   # 1000 transactions/day target
                Decimal('200')     # ±200 transactions tolerance
            ),
        }
        
        # Adjustment parameters
        self.max_adjustment_per_cycle = Decimal('0.1')  # Max 10% adjustment
        self.adjustment_sensitivity = Decimal('0.5')     # Sensitivity factor
        self.emergency_adjustment_multiplier = Decimal('2.0')
        
        # Current multipliers
        self.faucet_rate_multiplier = Decimal('1.0')
        self.sink_rate_multiplier = Decimal('1.0')
        
        # Historical adjustments
        self.adjustment_history: List[Dict] = []
    
    def update_economic_data(
        self,
        transaction_history: List[CurrencyTransaction],
        total_cosmic_credits: Decimal,
        total_star_tokens: Decimal,
        active_users: int
    ):
        """Update all economic metrics with latest data"""
        
        # Calculate inflation rate
        inflation_rate = self._calculate_inflation_rate(transaction_history)
        self.metrics[EconomicIndicator.INFLATION_RATE].update_value(inflation_rate)
        
        # Calculate currency velocity
        velocity = self._calculate_currency_velocity(transaction_history, total_cosmic_credits + total_star_tokens)
        self.metrics[EconomicIndicator.CURRENCY_VELOCITY].update_value(velocity)
        
        # Calculate supply ratio
        total_supply = total_cosmic_credits + total_star_tokens
        if total_supply > 0:
            earned_ratio = (total_cosmic_credits / total_supply) * 100
        else:
            earned_ratio = Decimal('60')  # Default target
        self.metrics[EconomicIndicator.SUPPLY_RATIO].update_value(earned_ratio)
        
        # Calculate transaction volume
        daily_transactions = self._calculate_daily_transaction_volume(transaction_history)
        self.metrics[EconomicIndicator.TRANSACTION_VOLUME].update_value(daily_transactions)
    
    def _calculate_inflation_rate(self, transactions: List[CurrencyTransaction]) -> Decimal:
        """Calculate annual inflation rate from recent transactions"""
        now = datetime.now(timezone.utc)
        thirty_days_ago = now - timedelta(days=30)
        
        # Get transactions from last 30 days
        recent_transactions = [
            tx for tx in transactions 
            if tx.timestamp > thirty_days_ago
        ]
        
        # Calculate net currency creation (faucets - sinks)
        faucet_amount = sum(
            tx.amount for tx in recent_transactions 
            if tx.transaction_type in [TransactionType.EARNED_REWARD, TransactionType.PURCHASE]
        )
        
        sink_amount = sum(
            tx.amount for tx in recent_transactions
            if tx.transaction_type.name.startswith('SINK_')
        )
        
        net_creation = faucet_amount - sink_amount
        
        # Estimate current supply from transactions
        total_supply = sum(tx.amount for tx in transactions if tx.transaction_type == TransactionType.EARNED_REWARD)
        
        if total_supply > 0 and net_creation > 0:
            # Annualize the 30-day rate
            monthly_rate = (net_creation / total_supply) * 100
            annual_rate = monthly_rate * 12
            return min(annual_rate, Decimal('50'))  # Cap at 50% for sanity
        
        return Decimal('0')
    
    def _calculate_currency_velocity(self, transactions: List[CurrencyTransaction], total_supply: Decimal) -> Decimal:
        """Calculate monthly currency velocity"""
        now = datetime.now(timezone.utc)
        thirty_days_ago = now - timedelta(days=30)
        
        # Get spending transactions from last 30 days
        recent_spending = [
            tx for tx in transactions 
            if tx.timestamp > thirty_days_ago and tx.transaction_type.name.startswith('SINK_')
        ]
        
        total_spent = sum(tx.amount for tx in recent_spending)
        
        if total_supply > 0:
            velocity = total_spent / total_supply
            return velocity
        
        return Decimal('0')
    
    def _calculate_daily_transaction_volume(self, transactions: List[CurrencyTransaction]) -> Decimal:
        """Calculate average daily transaction count"""
        now = datetime.now(timezone.utc)
        seven_days_ago = now - timedelta(days=7)
        
        recent_transactions = [
            tx for tx in transactions 
            if tx.timestamp > seven_days_ago
        ]
        
        return Decimal(len(recent_transactions)) / Decimal('7')
    
    def calculate_optimal_adjustments(self) -> Dict[str, Decimal]:
        """
        Calculate optimal faucet and sink adjustments based on current economic health.
        
        TODO(human): Implement this method to analyze economic metrics and return
        adjustment recommendations. Should return dict with 'faucet_adjustment' and 
        'sink_adjustment' keys containing values between 0.9-1.1 for gradual changes.
        
        Consider:
        - If inflation is above target (2.5%), reduce faucets and increase sinks
        - If velocity is below target (2.5x), incentivize spending by reducing sink costs
        - If supply ratio is off (target 60% earned), adjust accordingly
        - Use economic principles for balanced adjustments
        
        Args:
            None (uses self.metrics for current economic state)
            
        Returns:
            Dict with 'faucet_adjustment' and 'sink_adjustment' decimal values
        """
        
        # TODO(human): Implement optimal adjustment calculation
        # This is where you'll implement the economic balancing logic
        
        # Placeholder return - replace with your implementation
        return {
            'faucet_adjustment': Decimal('1.0'),
            'sink_adjustment': Decimal('1.0')
        }
    
    def apply_adjustments(self, adjustments: Dict[str, Decimal]) -> Dict[str, Any]:
        """Apply calculated adjustments to the economic system"""
        
        old_faucet = self.faucet_rate_multiplier
        old_sink = self.sink_rate_multiplier
        
        # Apply adjustments with bounds checking
        faucet_adjustment = adjustments.get('faucet_adjustment', Decimal('1.0'))
        sink_adjustment = adjustments.get('sink_adjustment', Decimal('1.0'))
        
        self.faucet_rate_multiplier *= faucet_adjustment
        self.sink_rate_multiplier *= sink_adjustment
        
        # Enforce bounds (0.5x to 2.0x)
        self.faucet_rate_multiplier = max(
            Decimal('0.5'), 
            min(Decimal('2.0'), self.faucet_rate_multiplier)
        )
        self.sink_rate_multiplier = max(
            Decimal('0.5'), 
            min(Decimal('2.0'), self.sink_rate_multiplier)
        )
        
        # Record adjustment
        adjustment_record = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'old_faucet_multiplier': str(old_faucet),
            'new_faucet_multiplier': str(self.faucet_rate_multiplier),
            'old_sink_multiplier': str(old_sink),
            'new_sink_multiplier': str(self.sink_rate_multiplier),
            'faucet_change': str((self.faucet_rate_multiplier - old_faucet) / old_faucet * 100),
            'sink_change': str((self.sink_rate_multiplier - old_sink) / old_sink * 100),
            'reason': self._generate_adjustment_reason()
        }
        
        self.adjustment_history.append(adjustment_record)
        
        # Keep only last 100 adjustments
        if len(self.adjustment_history) > 100:
            self.adjustment_history = self.adjustment_history[-100:]
        
        return adjustment_record
    
    def _generate_adjustment_reason(self) -> str:
        """Generate human-readable reason for economic adjustments"""
        reasons = []
        
        for indicator, metric in self.metrics.items():
            if metric.alert_level in [EconomicAlert.WARNING, EconomicAlert.CRITICAL]:
                deviation = metric.get_deviation_percentage()
                if deviation > 0:
                    reasons.append(f"{indicator.replace('_', ' ')} {deviation:.1f}% above target")
                else:
                    reasons.append(f"{indicator.replace('_', ' ')} {abs(deviation):.1f}% below target")
        
        if not reasons:
            return "Routine economic balancing"
        
        return "; ".join(reasons)
    
    def get_economic_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive economic health report"""
        
        # Overall health score (0-100)
        health_scores = []
        for metric in self.metrics.values():
            if metric.alert_level == EconomicAlert.NORMAL:
                health_scores.append(100)
            elif metric.alert_level == EconomicAlert.WARNING:
                health_scores.append(75)
            elif metric.alert_level == EconomicAlert.CRITICAL:
                health_scores.append(50)
            else:  # EMERGENCY
                health_scores.append(25)
        
        overall_health = sum(health_scores) / len(health_scores) if health_scores else 0
        
        # Metric details
        metric_details = {}
        for indicator, metric in self.metrics.items():
            metric_details[indicator] = {
                'current_value': str(metric.current_value),
                'target_value': str(metric.target_value),
                'deviation_percentage': str(metric.get_deviation_percentage()),
                'trend': metric.trend,
                'alert_level': metric.alert_level,
                'tolerance': str(metric.tolerance)
            }
        
        # Recent adjustments
        recent_adjustments = self.adjustment_history[-5:] if self.adjustment_history else []
        
        return {
            'overall_health_score': overall_health,
            'health_status': self._determine_overall_status(overall_health),
            'metrics': metric_details,
            'current_multipliers': {
                'faucet_rate_multiplier': str(self.faucet_rate_multiplier),
                'sink_rate_multiplier': str(self.sink_rate_multiplier)
            },
            'recent_adjustments': recent_adjustments,
            'recommendations': self._generate_recommendations(),
            'generated_at': datetime.now(timezone.utc).isoformat()
        }
    
    def _determine_overall_status(self, health_score: float) -> str:
        """Determine overall economic status"""
        if health_score >= 90:
            return "Excellent"
        elif health_score >= 75:
            return "Good"
        elif health_score >= 60:
            return "Fair"
        elif health_score >= 40:
            return "Poor"
        else:
            return "Critical"
    
    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations based on current metrics"""
        recommendations = []
        
        inflation_metric = self.metrics[EconomicIndicator.INFLATION_RATE]
        velocity_metric = self.metrics[EconomicIndicator.CURRENCY_VELOCITY]
        supply_metric = self.metrics[EconomicIndicator.SUPPLY_RATIO]
        
        # Inflation recommendations
        if inflation_metric.alert_level in [EconomicAlert.WARNING, EconomicAlert.CRITICAL]:
            if inflation_metric.current_value > inflation_metric.target_value:
                recommendations.append("High inflation detected: Consider reducing earning rewards and increasing spending incentives")
            else:
                recommendations.append("Low inflation/deflation detected: Consider increasing earning rewards")
        
        # Velocity recommendations
        if velocity_metric.alert_level in [EconomicAlert.WARNING, EconomicAlert.CRITICAL]:
            if velocity_metric.current_value < velocity_metric.target_value:
                recommendations.append("Low currency velocity: Implement spending incentives and limited-time offers")
            else:
                recommendations.append("High currency velocity: Monitor for speculation and add currency sinks")
        
        # Supply ratio recommendations
        if supply_metric.alert_level in [EconomicAlert.WARNING, EconomicAlert.CRITICAL]:
            if supply_metric.current_value < supply_metric.target_value:
                recommendations.append("Too much purchased currency: Increase earning opportunities")
            else:
                recommendations.append("Too little purchased currency: Enhance premium value propositions")
        
        # General recommendations
        if not recommendations:
            recommendations.append("Economy is stable: Continue monitoring and maintain current parameters")
        
        return recommendations
    
    def simulate_adjustment_impact(
        self, 
        proposed_adjustments: Dict[str, Decimal],
        simulation_days: int = 30
    ) -> Dict[str, Any]:
        """Simulate the impact of proposed adjustments"""
        
        # This is a simplified simulation - in production would use more sophisticated modeling
        current_inflation = self.metrics[EconomicIndicator.INFLATION_RATE].current_value
        current_velocity = self.metrics[EconomicIndicator.CURRENCY_VELOCITY].current_value
        
        faucet_adj = proposed_adjustments.get('faucet_adjustment', Decimal('1.0'))
        sink_adj = proposed_adjustments.get('sink_adjustment', Decimal('1.0'))
        
        # Estimate impact on inflation (simplified)
        # Increased faucets = more inflation, increased sinks = less inflation
        inflation_impact = (faucet_adj - 1) * 2 - (sink_adj - 1) * 1.5
        projected_inflation = current_inflation + inflation_impact
        
        # Estimate impact on velocity (simplified)
        # Reduced sink costs = higher velocity
        velocity_impact = -(sink_adj - 1) * 0.5
        projected_velocity = current_velocity + velocity_impact
        
        return {
            'projected_inflation_rate': str(projected_inflation),
            'inflation_change': str(inflation_impact),
            'projected_velocity': str(projected_velocity),
            'velocity_change': str(velocity_impact),
            'simulation_period_days': simulation_days,
            'confidence_level': 'Medium',  # This would be calculated based on model accuracy
            'warnings': self._generate_simulation_warnings(projected_inflation, projected_velocity)
        }
    
    def _generate_simulation_warnings(self, projected_inflation: Decimal, projected_velocity: Decimal) -> List[str]:
        """Generate warnings for simulation results"""
        warnings = []
        
        if projected_inflation > Decimal('5.0'):
            warnings.append("High inflation risk: Projected rate exceeds safe bounds")
        elif projected_inflation < Decimal('0'):
            warnings.append("Deflation risk: Negative inflation projected")
        
        if projected_velocity > Decimal('5.0'):
            warnings.append("Speculation risk: Very high velocity projected")
        elif projected_velocity < Decimal('1.0'):
            warnings.append("Stagnation risk: Very low velocity projected")
        
        return warnings