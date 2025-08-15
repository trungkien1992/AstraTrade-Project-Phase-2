#!/usr/bin/env python3
"""
Context-Sensitive Achievement Display System

Manages achievement display timing and positioning based on user context,
flow state analysis, and interruption preferences to optimize the trading
experience while maintaining engagement through achievement notifications.

Key Features:
- Flow state protection during high-concentration activities
- Peripheral positioning to minimize trading interface disruption
- Queue-based display management with intelligent batching
- User-customizable interruption levels and preferences
- Context-aware animation and sound selection
- A/B testing infrastructure for display optimization
"""

import asyncio
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import redis.asyncio as redis

from .dopamine_timing_engine import (
    AchievementTrigger, AchievementPriority, TradingContextState
)
from .trading_context_detector import TradingContextDetector
from .anti_addiction_safeguards import AntiAddictionSafeguards, InterventionAction


logger = logging.getLogger(__name__)


class DisplayPosition(Enum):
    """Achievement notification display positions"""
    BOTTOM_RIGHT = "bottom_right"      # Default: peripheral, non-intrusive
    BOTTOM_LEFT = "bottom_left"        # Alternative peripheral position
    TOP_RIGHT = "top_right"            # Higher visibility
    CENTER_MODAL = "center_modal"      # Maximum attention (critical only)
    SIDEBAR = "sidebar"                # Dedicated achievement area
    INLINE_FEED = "inline_feed"        # Within activity feed
    DISABLED = "disabled"              # No visual display


class DisplayStyle(Enum):
    """Achievement notification display styles"""
    SUBTLE = "subtle"                  # Minimal animation, low opacity
    STANDARD = "standard"              # Normal animation and styling
    CELEBRATE = "celebrate"            # Enhanced animation for major achievements
    PROFESSIONAL = "professional"     # Clean, business-appropriate styling
    COSMIC = "cosmic"                  # Themed styling matching app design


class InterruptionLevel(Enum):
    """User-configurable interruption tolerance levels"""
    NEVER = 0                         # Queue all achievements, never interrupt
    MINIMAL = 1                       # Only critical achievements interrupt
    LOW = 2                           # Educational + critical achievements
    MEDIUM = 3                        # Most achievements, respect high-concentration
    HIGH = 4                          # All achievements, minimal delays
    IMMEDIATE = 5                     # All achievements immediately (testing only)


@dataclass
class UserDisplayPreferences:
    """User's display preferences and settings"""
    user_id: str
    interruption_level: InterruptionLevel = InterruptionLevel.MEDIUM
    preferred_position: DisplayPosition = DisplayPosition.BOTTOM_RIGHT
    preferred_style: DisplayStyle = DisplayStyle.STANDARD
    sound_enabled: bool = True
    animation_enabled: bool = True
    show_progress_bars: bool = True
    batch_similar_achievements: bool = True
    auto_dismiss_seconds: int = 4
    max_simultaneous_displays: int = 3
    quiet_hours_enabled: bool = False
    quiet_hours_start: int = 22  # 10 PM
    quiet_hours_end: int = 8     # 8 AM


@dataclass
class DisplayQueueItem:
    """Item in the achievement display queue"""
    trigger: AchievementTrigger
    scheduled_display_time: datetime
    display_preferences: UserDisplayPreferences
    context_when_queued: TradingContextState
    priority_boost: float = 0.0  # Additional priority from context
    retry_count: int = 0
    
    @property
    def effective_priority(self) -> float:
        """Calculate effective priority including context boost"""
        base_priority = self.trigger.priority.value
        return base_priority + self.priority_boost


@dataclass
class DisplayMetrics:
    """Metrics for display optimization and A/B testing"""
    user_id: str
    achievement_id: str
    display_timestamp: datetime
    position: DisplayPosition
    style: DisplayStyle
    context_when_displayed: TradingContextState
    interruption_level: InterruptionLevel
    time_to_acknowledgment_ms: Optional[int] = None
    user_dismissed_early: bool = False
    caused_trading_interruption: bool = False
    engagement_score: float = 0.0  # 0-1 based on user interaction


class ContextSensitiveDisplayManager:
    """
    Manages context-aware achievement display with flow state protection.
    
    Integrates with trading context detection and user preferences to
    deliver achievement notifications at optimal times and positions.
    """
    
    def __init__(
        self,
        redis_client: redis.Redis,
        context_detector: TradingContextDetector,
        anti_addiction: AntiAddictionSafeguards
    ):
        self.redis = redis_client
        self.context_detector = context_detector
        self.anti_addiction = anti_addiction
        
        # Display queue management
        self.display_queue_key = "achievement_display_queue"
        self.active_displays_key = "active_achievement_displays"
        
        # Configuration
        self.config = self._initialize_config()
        self.context_display_rules = self._initialize_context_rules()
        
        # A/B testing variants
        self.ab_test_variants = self._initialize_ab_variants()
    
    def _initialize_config(self) -> Dict:
        """Initialize display system configuration"""
        return {
            "max_queue_size_per_user": 10,
            "max_display_retry_attempts": 3,
            "display_timeout_seconds": 30,
            "batch_display_window_seconds": 5,
            "context_check_interval_seconds": 10,
            "metrics_retention_days": 30,
            
            # Position-specific settings
            "bottom_right_offset": {"x": 20, "y": 20},
            "animation_duration_ms": 300,
            "fade_in_duration_ms": 200,
            "celebration_duration_ms": 1000,
            
            # Flow state protection
            "high_concentration_delay_seconds": 5,
            "order_entry_suppress_duration_seconds": 10,
            "stress_suppression_threshold": 0.7,
        }
    
    def _initialize_context_rules(self) -> Dict[TradingContextState, Dict]:
        """Initialize context-specific display rules"""
        return {
            TradingContextState.IDLE: {
                "allow_immediate": True,
                "preferred_position": DisplayPosition.BOTTOM_RIGHT,
                "preferred_style": DisplayStyle.STANDARD,
                "sound_allowed": True,
                "animation_intensity": 1.0
            },
            TradingContextState.EDUCATION_MODE: {
                "allow_immediate": True,
                "preferred_position": DisplayPosition.INLINE_FEED,
                "preferred_style": DisplayStyle.CELEBRATE,
                "sound_allowed": True,
                "animation_intensity": 1.2
            },
            TradingContextState.POSITION_MANAGEMENT: {
                "allow_immediate": True,
                "preferred_position": DisplayPosition.BOTTOM_RIGHT,
                "preferred_style": DisplayStyle.SUBTLE,
                "sound_allowed": False,
                "animation_intensity": 0.8
            },
            TradingContextState.CHART_ANALYSIS: {
                "allow_immediate": False,
                "delay_seconds": 3,
                "preferred_position": DisplayPosition.BOTTOM_LEFT,
                "preferred_style": DisplayStyle.SUBTLE,
                "sound_allowed": False,
                "animation_intensity": 0.5
            },
            TradingContextState.ORDER_ENTRY: {
                "allow_immediate": False,
                "delay_seconds": 5,
                "queue_only": True,
                "preferred_position": DisplayPosition.SIDEBAR,
                "preferred_style": DisplayStyle.SUBTLE,
                "sound_allowed": False,
                "animation_intensity": 0.3
            },
            TradingContextState.HIGH_STRESS: {
                "allow_immediate": False,
                "suppress_non_critical": True,
                "delay_seconds": 10,
                "preferred_position": DisplayPosition.DISABLED,
                "preferred_style": DisplayStyle.SUBTLE,
                "sound_allowed": False,
                "animation_intensity": 0.0
            }
        }
    
    def _initialize_ab_variants(self) -> Dict:
        """Initialize A/B testing variants for display optimization"""
        return {
            "position_test": {
                "variant_a": DisplayPosition.BOTTOM_RIGHT,
                "variant_b": DisplayPosition.BOTTOM_LEFT,
                "variant_c": DisplayPosition.SIDEBAR
            },
            "timing_test": {
                "variant_a": {"base_delay": 3, "jitter": 0.2},
                "variant_b": {"base_delay": 5, "jitter": 0.3},
                "variant_c": {"base_delay": 2, "jitter": 0.1}
            },
            "style_test": {
                "variant_a": DisplayStyle.SUBTLE,
                "variant_b": DisplayStyle.STANDARD,
                "variant_c": DisplayStyle.CELEBRATE
            }
        }
    
    async def queue_achievement_display(
        self,
        trigger: AchievementTrigger,
        user_preferences: Optional[UserDisplayPreferences] = None
    ) -> bool:
        """
        Queue achievement for context-sensitive display.
        
        Returns True if successfully queued, False if rejected by anti-addiction.
        """
        
        # Get user preferences
        if not user_preferences:
            user_preferences = await self.get_user_preferences(trigger.user_id)
        
        # Check anti-addiction safeguards
        allowed, intervention = await self.anti_addiction.check_achievement_allowed(
            trigger.user_id, trigger.priority
        )
        
        if not allowed:
            if intervention:
                # Handle intervention (this might queue a different message)
                await self._handle_intervention(trigger.user_id, intervention)
            return False
        
        # Get current context
        current_context = await self.context_detector.get_current_context(trigger.user_id)
        
        # Calculate display timing based on context and preferences
        display_time = await self._calculate_display_timing(
            trigger, current_context, user_preferences
        )
        
        # Create queue item
        queue_item = DisplayQueueItem(
            trigger=trigger,
            scheduled_display_time=display_time,
            display_preferences=user_preferences,
            context_when_queued=current_context,
            priority_boost=self._calculate_context_priority_boost(current_context, trigger.priority)
        )
        
        # Add to display queue
        await self._add_to_display_queue(queue_item)
        
        logger.info(
            f"Achievement queued for display: user={trigger.user_id}, "
            f"achievement={trigger.achievement_id}, "
            f"context={current_context.value}, "
            f"display_time={display_time}"
        )
        
        return True
    
    async def process_display_queue(self) -> List[DisplayQueueItem]:
        """
        Process display queue and return items ready for display.
        
        This should be called by a background processor every few seconds.
        """
        current_time = datetime.now()
        ready_items = []
        
        # Get all users with queued items
        user_queues = await self._get_all_user_queues()
        
        for user_id, queue_items in user_queues.items():
            # Sort by effective priority and scheduled time
            queue_items.sort(key=lambda x: (x.effective_priority, x.scheduled_display_time))
            
            user_ready_items = []
            
            for item in queue_items:
                # Check if item is ready for display
                if item.scheduled_display_time <= current_time:
                    
                    # Re-check context (user state might have changed)
                    current_context = await self.context_detector.get_current_context(user_id)
                    
                    # Check if display is allowed in current context
                    if await self._is_display_allowed(item, current_context):
                        
                        # Check display capacity (max simultaneous displays)
                        active_count = await self._get_active_display_count(user_id)
                        if active_count < item.display_preferences.max_simultaneous_displays:
                            user_ready_items.append(item)
                        
                    else:
                        # Re-queue with updated timing
                        await self._requeue_item(item, current_context)
            
            # Batch similar achievements if enabled
            if user_ready_items and queue_items[0].display_preferences.batch_similar_achievements:
                user_ready_items = await self._batch_similar_achievements(user_ready_items)
            
            ready_items.extend(user_ready_items)
        
        # Remove processed items from queue
        for item in ready_items:
            await self._remove_from_display_queue(item)
        
        # Mark items as actively displaying
        for item in ready_items:
            await self._mark_as_displaying(item)
        
        return ready_items
    
    async def display_achievement(
        self,
        queue_item: DisplayQueueItem,
        variant_override: Optional[Dict] = None
    ) -> DisplayMetrics:
        """
        Display achievement notification with context-appropriate styling.
        
        Returns display metrics for A/B testing and optimization.
        """
        
        trigger = queue_item.trigger
        preferences = queue_item.display_preferences
        
        # Apply A/B test variant if specified
        display_position = preferences.preferred_position
        display_style = preferences.preferred_style
        
        if variant_override:
            display_position = variant_override.get("position", display_position)
            display_style = variant_override.get("style", display_style)
        
        # Get current context for final display decisions
        current_context = await self.context_detector.get_current_context(trigger.user_id)
        context_rules = self.context_display_rules.get(current_context, {})
        
        # Override position/style based on context if needed
        if context_rules.get("preferred_position"):
            display_position = context_rules["preferred_position"]
        if context_rules.get("preferred_style"):
            display_style = context_rules["preferred_style"]
        
        # Create display message
        display_message = await self._create_display_message(
            trigger, display_position, display_style, context_rules
        )
        
        # Send display message via WebSocket or appropriate channel
        await self._send_display_message(trigger.user_id, display_message)
        
        # Create and store display metrics
        metrics = DisplayMetrics(
            user_id=trigger.user_id,
            achievement_id=trigger.achievement_id,
            display_timestamp=datetime.now(),
            position=display_position,
            style=display_style,
            context_when_displayed=current_context,
            interruption_level=preferences.interruption_level
        )
        
        await self._store_display_metrics(metrics)
        
        # Schedule auto-dismiss if enabled
        if preferences.auto_dismiss_seconds > 0:
            await self._schedule_auto_dismiss(trigger.user_id, trigger.achievement_id, preferences.auto_dismiss_seconds)
        
        logger.info(
            f"Achievement displayed: user={trigger.user_id}, "
            f"achievement={trigger.achievement_id}, "
            f"position={display_position.value}, "
            f"style={display_style.value}, "
            f"context={current_context.value}"
        )
        
        return metrics
    
    async def _calculate_display_timing(
        self,
        trigger: AchievementTrigger,
        context: TradingContextState,
        preferences: UserDisplayPreferences
    ) -> datetime:
        """Calculate optimal display timing based on context and preferences"""
        
        base_time = trigger.triggered_at
        context_rules = self.context_display_rules.get(context, {})
        
        # Check if immediate display is allowed
        if (context_rules.get("allow_immediate", False) and 
            preferences.interruption_level >= InterruptionLevel.MEDIUM):
            return base_time
        
        # Apply context-specific delay
        context_delay = context_rules.get("delay_seconds", 0)
        
        # Apply user preference adjustments
        preference_multiplier = {
            InterruptionLevel.NEVER: 999999,  # Effectively never
            InterruptionLevel.MINIMAL: 5.0,
            InterruptionLevel.LOW: 3.0,
            InterruptionLevel.MEDIUM: 1.5,
            InterruptionLevel.HIGH: 0.5,
            InterruptionLevel.IMMEDIATE: 0.1
        }
        
        total_delay = context_delay * preference_multiplier[preferences.interruption_level]
        
        # Check quiet hours
        if preferences.quiet_hours_enabled:
            current_hour = datetime.now().hour
            if (current_hour >= preferences.quiet_hours_start or 
                current_hour < preferences.quiet_hours_end):
                # Delay until quiet hours end
                tomorrow = datetime.now().replace(hour=preferences.quiet_hours_end, minute=0, second=0)
                if current_hour >= preferences.quiet_hours_start:
                    tomorrow += timedelta(days=1)
                return tomorrow
        
        return base_time + timedelta(seconds=total_delay)
    
    def _calculate_context_priority_boost(
        self,
        context: TradingContextState,
        priority: AchievementPriority
    ) -> float:
        """Calculate priority boost based on context and achievement type"""
        
        # Educational achievements get boost in education mode
        if (context == TradingContextState.EDUCATION_MODE and 
            priority == AchievementPriority.EDUCATIONAL):
            return -0.5  # Higher priority (lower number)
        
        # Critical achievements always get boost
        if priority == AchievementPriority.CRITICAL:
            return -1.0
        
        # Lower priority during high concentration contexts
        if context in [TradingContextState.ORDER_ENTRY, TradingContextState.HIGH_STRESS]:
            return 0.5
        
        return 0.0
    
    async def _is_display_allowed(
        self,
        queue_item: DisplayQueueItem,
        current_context: TradingContextState
    ) -> bool:
        """Check if display is allowed in current context"""
        
        context_rules = self.context_display_rules.get(current_context, {})
        
        # Check if context suppresses non-critical achievements
        if (context_rules.get("suppress_non_critical", False) and
            queue_item.trigger.priority != AchievementPriority.CRITICAL):
            return False
        
        # Check if context requires queue-only
        if (context_rules.get("queue_only", False) and
            queue_item.display_preferences.interruption_level < InterruptionLevel.HIGH):
            return False
        
        # Check user stress level
        stress_metrics = await self.context_detector.get_stress_metrics(queue_item.trigger.user_id)
        if stress_metrics.stress_level > self.config["stress_suppression_threshold"]:
            return queue_item.trigger.priority == AchievementPriority.CRITICAL
        
        return True
    
    async def _create_display_message(
        self,
        trigger: AchievementTrigger,
        position: DisplayPosition,
        style: DisplayStyle,
        context_rules: Dict
    ) -> Dict:
        """Create display message with appropriate formatting"""
        
        return {
            "type": "achievement_display",
            "achievement_id": trigger.achievement_id,
            "user_id": trigger.user_id,
            "data": trigger.data,
            "display_config": {
                "position": position.value,
                "style": style.value,
                "animation_enabled": context_rules.get("animation_intensity", 1.0) > 0.5,
                "animation_intensity": context_rules.get("animation_intensity", 1.0),
                "sound_enabled": context_rules.get("sound_allowed", True),
                "auto_dismiss_ms": 4000  # Default 4 seconds
            },
            "timestamp": datetime.now().isoformat()
        }
    
    async def _send_display_message(self, user_id: str, message: Dict):
        """Send display message to user via WebSocket or other channel"""
        
        # Publish to Redis for WebSocket manager to pick up
        channel = f"achievement_display:{user_id}"
        await self.redis.publish(channel, json.dumps(message))
        
        logger.debug(f"Display message sent to channel {channel}")
    
    async def _batch_similar_achievements(
        self,
        items: List[DisplayQueueItem]
    ) -> List[DisplayQueueItem]:
        """Batch similar achievements for grouped display"""
        
        if len(items) <= 1:
            return items
        
        # Group by achievement type/category
        batches = {}
        unbatched = []
        
        for item in items:
            achievement_category = item.trigger.data.get("category", "unknown")
            
            # Only batch if achievements are within batching window
            if achievement_category in batches:
                time_diff = abs(
                    (item.scheduled_display_time - batches[achievement_category][-1].scheduled_display_time).total_seconds()
                )
                if time_diff <= self.config["batch_display_window_seconds"]:
                    batches[achievement_category].append(item)
                else:
                    unbatched.append(item)
            else:
                batches[achievement_category] = [item]
        
        # Create batched items
        batched_items = []
        for category, category_items in batches.items():
            if len(category_items) > 1:
                # Create batch display item
                primary_item = category_items[0]  # Use first item as primary
                primary_item.trigger.data["batched_achievements"] = [
                    {"id": item.trigger.achievement_id, "data": item.trigger.data}
                    for item in category_items[1:]
                ]
                batched_items.append(primary_item)
            else:
                batched_items.extend(category_items)
        
        batched_items.extend(unbatched)
        return batched_items
    
    async def get_user_preferences(self, user_id: str) -> UserDisplayPreferences:
        """Get user's display preferences"""
        
        prefs_key = f"display_preferences:{user_id}"
        stored_prefs = await self.redis.hgetall(prefs_key)
        
        if stored_prefs:
            return UserDisplayPreferences(
                user_id=user_id,
                interruption_level=InterruptionLevel(int(stored_prefs.get("interruption_level", InterruptionLevel.MEDIUM.value))),
                preferred_position=DisplayPosition(stored_prefs.get("preferred_position", DisplayPosition.BOTTOM_RIGHT.value)),
                preferred_style=DisplayStyle(stored_prefs.get("preferred_style", DisplayStyle.STANDARD.value)),
                sound_enabled=stored_prefs.get("sound_enabled", "true").lower() == "true",
                animation_enabled=stored_prefs.get("animation_enabled", "true").lower() == "true",
                show_progress_bars=stored_prefs.get("show_progress_bars", "true").lower() == "true",
                batch_similar_achievements=stored_prefs.get("batch_similar_achievements", "true").lower() == "true",
                auto_dismiss_seconds=int(stored_prefs.get("auto_dismiss_seconds", "4")),
                max_simultaneous_displays=int(stored_prefs.get("max_simultaneous_displays", "3")),
                quiet_hours_enabled=stored_prefs.get("quiet_hours_enabled", "false").lower() == "true",
                quiet_hours_start=int(stored_prefs.get("quiet_hours_start", "22")),
                quiet_hours_end=int(stored_prefs.get("quiet_hours_end", "8"))
            )
        else:
            # Return default preferences
            return UserDisplayPreferences(user_id=user_id)
    
    async def update_user_preferences(self, preferences: UserDisplayPreferences):
        """Update user's display preferences"""
        
        prefs_key = f"display_preferences:{preferences.user_id}"
        prefs_data = {
            "interruption_level": str(preferences.interruption_level.value),
            "preferred_position": preferences.preferred_position.value,
            "preferred_style": preferences.preferred_style.value,
            "sound_enabled": str(preferences.sound_enabled).lower(),
            "animation_enabled": str(preferences.animation_enabled).lower(),
            "show_progress_bars": str(preferences.show_progress_bars).lower(),
            "batch_similar_achievements": str(preferences.batch_similar_achievements).lower(),
            "auto_dismiss_seconds": str(preferences.auto_dismiss_seconds),
            "max_simultaneous_displays": str(preferences.max_simultaneous_displays),
            "quiet_hours_enabled": str(preferences.quiet_hours_enabled).lower(),
            "quiet_hours_start": str(preferences.quiet_hours_start),
            "quiet_hours_end": str(preferences.quiet_hours_end)
        }
        
        await self.redis.hset(prefs_key, mapping=prefs_data)
        await self.redis.expire(prefs_key, 86400 * 365)  # Expire after 1 year
    
    async def _store_display_metrics(self, metrics: DisplayMetrics):
        """Store display metrics for optimization analysis"""
        
        metrics_key = f"display_metrics:{metrics.user_id}"
        metrics_data = {
            "timestamp": metrics.display_timestamp.timestamp(),
            "achievement_id": metrics.achievement_id,
            "position": metrics.position.value,
            "style": metrics.style.value,
            "context": metrics.context_when_displayed.value,
            "interruption_level": metrics.interruption_level.value,
            "engagement_score": metrics.engagement_score
        }
        
        # Store in time series
        await self.redis.zadd(
            metrics_key,
            {json.dumps(metrics_data): metrics.display_timestamp.timestamp()}
        )
        
        # Keep metrics for retention period
        retention_seconds = self.config["metrics_retention_days"] * 86400
        await self.redis.expire(metrics_key, retention_seconds)
        
        # Clean old metrics
        cutoff_time = time.time() - retention_seconds
        await self.redis.zremrangebyscore(metrics_key, 0, cutoff_time)
    
    async def get_display_analytics(self, user_id: str, days: int = 7) -> Dict:
        """Get display analytics for optimization"""
        
        metrics_key = f"display_metrics:{user_id}"
        start_time = time.time() - (days * 86400)
        
        raw_metrics = await self.redis.zrangebyscore(
            metrics_key, start_time, time.time(), withscores=True
        )
        
        if not raw_metrics:
            return {"message": "No display metrics available"}
        
        metrics_list = []
        for metrics_json, timestamp in raw_metrics:
            metrics_data = json.loads(metrics_json)
            metrics_data["timestamp"] = datetime.fromtimestamp(timestamp)
            metrics_list.append(metrics_data)
        
        # Calculate analytics
        total_displays = len(metrics_list)
        avg_engagement = sum(m.get("engagement_score", 0) for m in metrics_list) / total_displays
        
        # Group by position
        position_stats = {}
        for metric in metrics_list:
            pos = metric["position"]
            if pos not in position_stats:
                position_stats[pos] = {"count": 0, "engagement": 0}
            position_stats[pos]["count"] += 1
            position_stats[pos]["engagement"] += metric.get("engagement_score", 0)
        
        # Calculate averages
        for pos_data in position_stats.values():
            if pos_data["count"] > 0:
                pos_data["avg_engagement"] = pos_data["engagement"] / pos_data["count"]
        
        return {
            "period_days": days,
            "total_displays": total_displays,
            "average_engagement": avg_engagement,
            "position_performance": position_stats,
            "context_breakdown": self._analyze_context_performance(metrics_list)
        }
    
    def _analyze_context_performance(self, metrics_list: List[Dict]) -> Dict:
        """Analyze performance by context"""
        
        context_stats = {}
        for metric in metrics_list:
            ctx = metric["context"]
            if ctx not in context_stats:
                context_stats[ctx] = {"count": 0, "engagement": 0}
            context_stats[ctx]["count"] += 1
            context_stats[ctx]["engagement"] += metric.get("engagement_score", 0)
        
        # Calculate averages
        for ctx_data in context_stats.values():
            if ctx_data["count"] > 0:
                ctx_data["avg_engagement"] = ctx_data["engagement"] / ctx_data["count"]
        
        return context_stats
    
    # Additional helper methods for queue management would go here
    # (Truncated for length - would include _add_to_display_queue, 
    # _remove_from_display_queue, _get_all_user_queues, etc.)
    
    async def _add_to_display_queue(self, item: DisplayQueueItem):
        """Add item to display queue"""
        # Implementation would use Redis sorted set with timestamp as score
        pass
    
    async def _remove_from_display_queue(self, item: DisplayQueueItem):
        """Remove item from display queue"""
        # Implementation would remove from Redis sorted set
        pass