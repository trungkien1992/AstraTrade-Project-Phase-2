#!/usr/bin/env python3
"""
Dopamine-Optimized Achievement Timing Engine

Based on neuroscience research and trading psychology studies, this engine 
implements variable reward schedules, context-sensitive timing, and 
anti-addiction safeguards for achievement notifications.

Key Research Findings Applied:
- Variable reward schedules (70% predictable + 30% surprise)
- Base intervals: 45-90 seconds with ±30% jitter
- Stress detection: 2x multipliers during high-stress periods  
- Cooling-off periods: 15 minutes after 3+ consecutive achievements
- Context awareness: 5-second delays during high-concentration tasks
"""

import asyncio
import random
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import redis.asyncio as redis
import numpy as np


class AchievementPriority(Enum):
    """Achievement priority levels based on research findings"""
    CRITICAL = 1        # Safety/risk management achievements
    EDUCATIONAL = 2     # Learning-focused achievements  
    PERFORMANCE = 3     # Trading performance milestones
    SOCIAL = 4          # Social sharing/community achievements


class TradingContextState(Enum):
    """Trading context states for timing adjustments"""
    IDLE = "idle"                    # No active trading
    ORDER_ENTRY = "order_entry"     # Placing/modifying orders
    CHART_ANALYSIS = "chart_analysis"  # Analyzing charts/indicators
    POSITION_MANAGEMENT = "position_management"  # Managing open positions
    EDUCATION_MODE = "education_mode"    # Learning/reading content
    HIGH_STRESS = "high_stress"      # High volatility/rapid trading


@dataclass
class UserStressMetrics:
    """User stress indicators for timing adjustments"""
    click_frequency: float = 0.0      # Clicks per minute
    error_rate: float = 0.0           # Order errors/cancellations
    session_intensity: float = 0.0    # Trading volume intensity
    time_since_loss: Optional[float] = None  # Minutes since last loss
    market_volatility: float = 0.0    # Current market volatility index
    
    @property
    def stress_level(self) -> float:
        """Calculate normalized stress level (0.0 - 1.0)"""
        # Weighted stress calculation based on research
        stress_components = [
            min(self.click_frequency / 60.0, 1.0) * 0.3,  # Max 60 clicks/min
            min(self.error_rate, 1.0) * 0.2,              # Max 100% error rate
            min(self.session_intensity / 10.0, 1.0) * 0.2, # Normalized intensity
            (0.5 if self.time_since_loss and self.time_since_loss < 5 else 0.0) * 0.15,
            min(self.market_volatility / 0.05, 1.0) * 0.15  # Max 5% volatility
        ]
        return min(sum(stress_components), 1.0)


@dataclass
class AchievementTrigger:
    """Achievement trigger with timing and context data"""
    achievement_id: str
    user_id: str
    priority: AchievementPriority
    data: Dict
    triggered_at: datetime
    scheduled_display_at: Optional[datetime] = None
    context_when_triggered: Optional[TradingContextState] = None
    stress_level_when_triggered: float = 0.0


class VariableTimingEngine:
    """
    Core timing engine implementing dopamine-optimized achievement scheduling.
    
    Research-based parameters:
    - Educational achievements: 45s ± 30%
    - Performance achievements: 60s ± 30% 
    - Social achievements: 90s ± 30%
    - Stress multiplier: 2.0x during high stress
    - Cooling-off period: 15 minutes after 3+ achievements
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        
        # Research-validated base intervals (seconds)
        self.base_intervals = {
            AchievementPriority.CRITICAL: 30,      # Immediate for safety
            AchievementPriority.EDUCATIONAL: 45,   # Optimal for learning
            AchievementPriority.PERFORMANCE: 60,   # Prevents gaming system
            AchievementPriority.SOCIAL: 90         # Lowest dopamine impact
        }
        
        # Timing configuration based on research
        self.jitter_factor = 0.3           # ±30% variation for unpredictability
        self.stress_multiplier = 2.0       # Double delays under stress
        self.surprise_achievement_rate = 0.3  # 30% surprise achievements
        self.max_hourly_achievements = 4   # Anti-addiction limit
        self.cooling_off_period = 900      # 15 minutes in seconds
        
        # Context-sensitive delays
        self.context_delays = {
            TradingContextState.IDLE: 0,
            TradingContextState.ORDER_ENTRY: 5,      # 5s delay during order entry
            TradingContextState.CHART_ANALYSIS: 3,   # 3s delay during analysis
            TradingContextState.POSITION_MANAGEMENT: 1,  # Minimal delay
            TradingContextState.EDUCATION_MODE: 0,   # Immediate for learning
            TradingContextState.HIGH_STRESS: 10      # Extended delay under stress
        }
    
    async def calculate_display_timing(
        self, 
        achievement_trigger: AchievementTrigger,
        current_context: TradingContextState,
        stress_metrics: UserStressMetrics
    ) -> datetime:
        """
        Calculate optimal display timing for achievement based on context and stress.
        
        Returns the scheduled display time for the achievement.
        """
        # Check if user is in cooling-off period
        if await self._is_in_cooling_off_period(achievement_trigger.user_id):
            return await self._schedule_after_cooling_off(achievement_trigger.user_id)
        
        # Get base interval for achievement priority
        base_interval = self.base_intervals[achievement_trigger.priority]
        
        # Apply jitter for variable reward schedule (±30%)
        jitter = random.uniform(-self.jitter_factor, self.jitter_factor)
        interval_with_jitter = base_interval * (1 + jitter)
        
        # Apply stress multiplier
        if stress_metrics.stress_level > 0.5:  # High stress threshold
            interval_with_jitter *= self.stress_multiplier
        
        # Add context-sensitive delay
        context_delay = self.context_delays.get(current_context, 0)
        total_delay = max(5, interval_with_jitter + context_delay)  # Minimum 5s
        
        # Check for surprise achievement (immediate display for positive reinforcement)
        if self._is_surprise_achievement(achievement_trigger):
            total_delay = min(total_delay, 3)  # Max 3s delay for surprises
        
        scheduled_time = achievement_trigger.triggered_at + timedelta(seconds=total_delay)
        
        # Update trigger with calculated timing
        achievement_trigger.scheduled_display_at = scheduled_time
        achievement_trigger.stress_level_when_triggered = stress_metrics.stress_level
        
        return scheduled_time
    
    def _is_surprise_achievement(self, trigger: AchievementTrigger) -> bool:
        """Determine if achievement should be treated as surprise (immediate)"""
        # 30% of achievements are surprises for dopamine optimization
        random.seed(hash(f"{trigger.user_id}_{trigger.achievement_id}_{trigger.triggered_at}"))
        return random.random() < self.surprise_achievement_rate
    
    async def _is_in_cooling_off_period(self, user_id: str) -> bool:
        """Check if user is in cooling-off period after consecutive achievements"""
        recent_key = f"achievements:recent:{user_id}"
        recent_count = await self.redis.zcount(
            recent_key,
            int(time.time() - 3600),  # Last hour
            int(time.time())
        )
        
        if recent_count >= self.max_hourly_achievements:
            return True
        
        # Check for consecutive achievements (3+ in 10 minutes triggers cooling-off)
        consecutive_count = await self.redis.zcount(
            recent_key,
            int(time.time() - 600),  # Last 10 minutes
            int(time.time())
        )
        
        return consecutive_count >= 3
    
    async def _schedule_after_cooling_off(self, user_id: str) -> datetime:
        """Schedule achievement after cooling-off period ends"""
        last_achievement_key = f"achievements:last:{user_id}"
        last_achievement_time = await self.redis.get(last_achievement_key)
        
        if last_achievement_time:
            last_time = datetime.fromtimestamp(float(last_achievement_time))
            cooling_off_end = last_time + timedelta(seconds=self.cooling_off_period)
            
            # Add random delay after cooling-off to avoid predictable patterns
            random_delay = random.uniform(0, 300)  # 0-5 minutes
            return cooling_off_end + timedelta(seconds=random_delay)
        
        # Fallback: schedule in cooling-off period from now
        return datetime.now() + timedelta(seconds=self.cooling_off_period)
    
    async def record_achievement_display(self, user_id: str, achievement_id: str):
        """Record achievement display for anti-addiction tracking"""
        current_time = time.time()
        
        # Update recent achievements set
        recent_key = f"achievements:recent:{user_id}"
        await self.redis.zadd(recent_key, {achievement_id: current_time})
        await self.redis.expire(recent_key, 3600)  # Expire after 1 hour
        
        # Update last achievement time
        last_key = f"achievements:last:{user_id}"
        await self.redis.set(last_key, current_time, ex=3600)
    
    async def get_timing_stats(self, user_id: str) -> Dict:
        """Get timing statistics for monitoring and optimization"""
        recent_key = f"achievements:recent:{user_id}"
        
        # Count achievements in different time windows
        current_time = time.time()
        hourly_count = await self.redis.zcount(recent_key, current_time - 3600, current_time)
        last_10_min_count = await self.redis.zcount(recent_key, current_time - 600, current_time)
        
        # Get last achievement time
        last_key = f"achievements:last:{user_id}"
        last_achievement = await self.redis.get(last_key)
        last_achievement_time = float(last_achievement) if last_achievement else None
        
        return {
            "hourly_achievement_count": hourly_count,
            "last_10_min_count": last_10_min_count,
            "is_in_cooling_off": await self._is_in_cooling_off_period(user_id),
            "last_achievement_timestamp": last_achievement_time,
            "time_until_cooling_off_ends": None if not await self._is_in_cooling_off_period(user_id) 
                                          else (await self._schedule_after_cooling_off(user_id) - datetime.now()).total_seconds()
        }


class AchievementQueue:
    """
    Priority-based achievement queue with timing enforcement.
    
    Manages delayed display of achievements based on calculated timing
    and maintains proper ordering based on priority and scheduled time.
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.queue_key = "achievement_display_queue"
        self.processing_lock = "achievement_queue_lock"
    
    async def enqueue_achievement(self, trigger: AchievementTrigger):
        """Add achievement to display queue with scheduled timing"""
        if not trigger.scheduled_display_at:
            raise ValueError("Achievement trigger must have scheduled_display_at set")
        
        queue_item = {
            "achievement_id": trigger.achievement_id,
            "user_id": trigger.user_id,
            "priority": trigger.priority.value,
            "data": trigger.data,
            "triggered_at": trigger.triggered_at.isoformat(),
            "scheduled_display_at": trigger.scheduled_display_at.isoformat(),
            "context": trigger.context_when_triggered.value if trigger.context_when_triggered else None,
            "stress_level": trigger.stress_level_when_triggered
        }
        
        # Use scheduled display time as score for Redis sorted set
        score = trigger.scheduled_display_at.timestamp()
        
        await self.redis.zadd(
            self.queue_key,
            {json.dumps(queue_item): score}
        )
    
    async def get_ready_achievements(self, current_time: Optional[datetime] = None) -> List[AchievementTrigger]:
        """Get all achievements ready for display"""
        if current_time is None:
            current_time = datetime.now()
        
        # Get achievements with scheduled time <= current time
        raw_items = await self.redis.zrangebyscore(
            self.queue_key,
            0,
            current_time.timestamp(),
            withscores=True
        )
        
        ready_achievements = []
        for item_json, _ in raw_items:
            item_data = json.loads(item_json)
            
            trigger = AchievementTrigger(
                achievement_id=item_data["achievement_id"],
                user_id=item_data["user_id"],
                priority=AchievementPriority(item_data["priority"]),
                data=item_data["data"],
                triggered_at=datetime.fromisoformat(item_data["triggered_at"]),
                scheduled_display_at=datetime.fromisoformat(item_data["scheduled_display_at"]),
                context_when_triggered=TradingContextState(item_data["context"]) if item_data["context"] else None,
                stress_level_when_triggered=item_data["stress_level"]
            )
            
            ready_achievements.append(trigger)
        
        # Sort by priority (lower number = higher priority)
        ready_achievements.sort(key=lambda x: x.priority.value)
        
        return ready_achievements
    
    async def remove_processed_achievements(self, achievements: List[AchievementTrigger]):
        """Remove achievements from queue after processing"""
        items_to_remove = []
        
        for trigger in achievements:
            queue_item = {
                "achievement_id": trigger.achievement_id,
                "user_id": trigger.user_id,
                "priority": trigger.priority.value,
                "data": trigger.data,
                "triggered_at": trigger.triggered_at.isoformat(),
                "scheduled_display_at": trigger.scheduled_display_at.isoformat(),
                "context": trigger.context_when_triggered.value if trigger.context_when_triggered else None,
                "stress_level": trigger.stress_level_when_triggered
            }
            items_to_remove.append(json.dumps(queue_item))
        
        if items_to_remove:
            await self.redis.zrem(self.queue_key, *items_to_remove)
    
    async def get_queue_size(self) -> int:
        """Get current queue size"""
        return await self.redis.zcard(self.queue_key)
    
    async def get_user_queued_count(self, user_id: str) -> int:
        """Get number of achievements queued for specific user"""
        all_items = await self.redis.zrange(self.queue_key, 0, -1)
        
        user_count = 0
        for item_json in all_items:
            item_data = json.loads(item_json)
            if item_data["user_id"] == user_id:
                user_count += 1
        
        return user_count
    
    async def clear_user_queue(self, user_id: str):
        """Clear all queued achievements for a specific user"""
        all_items = await self.redis.zrange(self.queue_key, 0, -1)
        
        items_to_remove = []
        for item_json in all_items:
            item_data = json.loads(item_json)
            if item_data["user_id"] == user_id:
                items_to_remove.append(item_json)
        
        if items_to_remove:
            await self.redis.zrem(self.queue_key, *items_to_remove)


class DopamineOptimizedAchievementSystem:
    """
    Main achievement system integrating timing engine and queue management.
    
    This system implements research-based dopamine optimization for
    achievement notifications in trading environments.
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.timing_engine = VariableTimingEngine(redis_client)
        self.queue = AchievementQueue(redis_client)
        
    async def trigger_achievement(
        self,
        achievement_id: str,
        user_id: str,
        achievement_data: Dict,
        priority: AchievementPriority,
        current_context: TradingContextState,
        stress_metrics: UserStressMetrics
    ) -> bool:
        """
        Trigger an achievement with dopamine-optimized timing.
        
        Returns True if achievement was successfully queued for display.
        """
        trigger = AchievementTrigger(
            achievement_id=achievement_id,
            user_id=user_id,
            priority=priority,
            data=achievement_data,
            triggered_at=datetime.now(),
            context_when_triggered=current_context
        )
        
        # Calculate optimal display timing
        scheduled_time = await self.timing_engine.calculate_display_timing(
            trigger, current_context, stress_metrics
        )
        
        # Enqueue for later display
        await self.queue.enqueue_achievement(trigger)
        
        return True
    
    async def process_ready_achievements(self) -> List[AchievementTrigger]:
        """
        Process achievements that are ready for display.
        
        Should be called by background processor every 5-10 seconds.
        """
        ready_achievements = await self.queue.get_ready_achievements()
        
        if ready_achievements:
            # Record display for anti-addiction tracking
            for trigger in ready_achievements:
                await self.timing_engine.record_achievement_display(
                    trigger.user_id,
                    trigger.achievement_id
                )
            
            # Remove from queue
            await self.queue.remove_processed_achievements(ready_achievements)
        
        return ready_achievements
    
    async def get_user_status(self, user_id: str) -> Dict:
        """Get comprehensive status for user's achievement system"""
        timing_stats = await self.timing_engine.get_timing_stats(user_id)
        queued_count = await self.queue.get_user_queued_count(user_id)
        
        return {
            **timing_stats,
            "queued_achievements": queued_count,
            "system_status": "operational"
        }