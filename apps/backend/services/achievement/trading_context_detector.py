#!/usr/bin/env python3
"""
Trading Context Detection System

Analyzes user behavior patterns to determine current trading context,
enabling achievement timing optimization that preserves flow states
and enhances user concentration during critical trading activities.

Context States Detected:
- Order Entry: User is placing/modifying orders (high concentration)  
- Chart Analysis: User is analyzing charts/indicators (medium concentration)
- Position Management: User is managing existing positions (low concentration)
- Education Mode: User is learning/reading content (achievement-friendly)
- High Stress: User is under stress from losses/volatility (delay achievements)
- Idle: No active trading (achievement-friendly)
"""

import asyncio
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import redis.asyncio as redis
import numpy as np
from .dopamine_timing_engine import TradingContextState, UserStressMetrics


@dataclass
class UserActivity:
    """Individual user activity event for context analysis"""
    user_id: str
    activity_type: str
    timestamp: datetime
    metadata: Dict = field(default_factory=dict)


@dataclass
class ContextAnalysisWindow:
    """Time window for analyzing user context"""
    start_time: datetime
    end_time: datetime
    activities: List[UserActivity] = field(default_factory=list)
    
    @property
    def duration_seconds(self) -> float:
        return (self.end_time - self.start_time).total_seconds()


class ActivityType(Enum):
    """Types of user activities tracked for context detection"""
    # Trading Activities
    ORDER_PLACED = "order_placed"
    ORDER_MODIFIED = "order_modified"
    ORDER_CANCELLED = "order_cancelled"
    POSITION_OPENED = "position_opened"
    POSITION_CLOSED = "position_closed"
    STOP_LOSS_SET = "stop_loss_set"
    TAKE_PROFIT_SET = "take_profit_set"
    
    # Analysis Activities
    CHART_OPENED = "chart_opened"
    INDICATOR_ADDED = "indicator_added"
    TIMEFRAME_CHANGED = "timeframe_changed"
    SYMBOL_SWITCHED = "symbol_switched"
    WATCHLIST_VIEWED = "watchlist_viewed"
    
    # Educational Activities
    TUTORIAL_STARTED = "tutorial_started"
    TUTORIAL_COMPLETED = "tutorial_completed"
    ARTICLE_READ = "article_read"
    VIDEO_WATCHED = "video_watched"
    FAQ_ACCESSED = "faq_accessed"
    
    # System Activities
    LOGIN = "login"
    LOGOUT = "logout"
    PAGE_VIEW = "page_view"
    CLICK = "click"
    SCROLL = "scroll"
    ERROR_OCCURRED = "error_occurred"
    
    # Tournament Activities
    TOURNAMENT_JOINED = "tournament_joined"
    LEADERBOARD_VIEWED = "leaderboard_viewed"
    AI_TRADER_INFO_VIEWED = "ai_trader_info_viewed"


class TradingContextDetector:
    """
    Analyzes user behavior patterns to determine current trading context.
    
    Uses sliding window analysis of user activities to classify current
    state and predict optimal timing for achievement notifications.
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.analysis_window = 60  # 60 seconds lookback window
        self.activity_weights = self._initialize_activity_weights()
        self.context_thresholds = self._initialize_context_thresholds()
        
    def _initialize_activity_weights(self) -> Dict[ActivityType, Dict[str, float]]:
        """Initialize activity weights for different context states"""
        return {
            # Order-related activities indicate ORDER_ENTRY context
            ActivityType.ORDER_PLACED: {
                "order_entry": 0.8,
                "stress": 0.6,
                "concentration": 0.9
            },
            ActivityType.ORDER_MODIFIED: {
                "order_entry": 0.7,
                "stress": 0.4,
                "concentration": 0.8
            },
            ActivityType.ORDER_CANCELLED: {
                "order_entry": 0.6,
                "stress": 0.7,  # Cancellations often indicate stress
                "concentration": 0.7
            },
            
            # Chart activities indicate CHART_ANALYSIS context
            ActivityType.CHART_OPENED: {
                "chart_analysis": 0.6,
                "concentration": 0.7
            },
            ActivityType.INDICATOR_ADDED: {
                "chart_analysis": 0.8,
                "concentration": 0.8
            },
            ActivityType.TIMEFRAME_CHANGED: {
                "chart_analysis": 0.7,
                "concentration": 0.6
            },
            ActivityType.SYMBOL_SWITCHED: {
                "chart_analysis": 0.5,
                "concentration": 0.5
            },
            
            # Position management activities
            ActivityType.POSITION_OPENED: {
                "position_management": 0.8,
                "stress": 0.5,
                "concentration": 0.6
            },
            ActivityType.POSITION_CLOSED: {
                "position_management": 0.9,
                "stress": 0.4,  # Closing can reduce stress
                "concentration": 0.5
            },
            ActivityType.STOP_LOSS_SET: {
                "position_management": 0.7,
                "stress": -0.3,  # Setting stop loss reduces stress
                "concentration": 0.6
            },
            
            # Educational activities indicate EDUCATION_MODE
            ActivityType.TUTORIAL_STARTED: {
                "education_mode": 0.9,
                "achievement_friendly": 0.8,
                "concentration": 0.7
            },
            ActivityType.ARTICLE_READ: {
                "education_mode": 0.8,
                "achievement_friendly": 0.9,
                "concentration": 0.6
            },
            ActivityType.VIDEO_WATCHED: {
                "education_mode": 0.7,
                "achievement_friendly": 0.7,
                "concentration": 0.8
            },
            
            # Error activities indicate stress
            ActivityType.ERROR_OCCURRED: {
                "stress": 0.8,
                "concentration": -0.3  # Errors break concentration
            },
            
            # Tournament activities
            ActivityType.TOURNAMENT_JOINED: {
                "engagement": 0.8,
                "achievement_friendly": 0.6
            },
            ActivityType.LEADERBOARD_VIEWED: {
                "engagement": 0.6,
                "achievement_friendly": 0.5
            },
            
            # General system activities (low impact)
            ActivityType.PAGE_VIEW: {
                "engagement": 0.2
            },
            ActivityType.CLICK: {
                "engagement": 0.1,
                "concentration": 0.1
            }
        }
    
    def _initialize_context_thresholds(self) -> Dict[str, float]:
        """Initialize thresholds for context state determination"""
        return {
            "order_entry_threshold": 0.6,      # 60% order entry activity
            "chart_analysis_threshold": 0.5,   # 50% chart analysis activity
            "position_management_threshold": 0.4,  # 40% position management
            "education_mode_threshold": 0.5,   # 50% educational activity
            "high_stress_threshold": 0.6,      # 60% stress indicators
            "high_concentration_threshold": 0.7,  # 70% concentration activity
            "idle_threshold": 0.2              # Below 20% activity = idle
        }
    
    async def record_activity(
        self,
        user_id: str,
        activity_type: ActivityType,
        metadata: Optional[Dict] = None
    ):
        """Record user activity for context analysis"""
        activity = UserActivity(
            user_id=user_id,
            activity_type=activity_type.value,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        
        # Store in Redis with expiration
        activity_key = f"user_activities:{user_id}"
        activity_data = {
            "type": activity.activity_type,
            "timestamp": activity.timestamp.timestamp(),
            "metadata": json.dumps(activity.metadata)
        }
        
        # Use sorted set with timestamp as score for efficient range queries
        await self.redis.zadd(
            activity_key,
            {json.dumps(activity_data): activity.timestamp.timestamp()}
        )
        
        # Expire old activities after 1 hour
        await self.redis.expire(activity_key, 3600)
        
        # Clean up activities older than analysis window
        cutoff_time = time.time() - (self.analysis_window * 2)  # Keep 2x window for analysis
        await self.redis.zremrangebyscore(activity_key, 0, cutoff_time)
    
    async def get_current_context(self, user_id: str) -> TradingContextState:
        """Determine current trading context based on recent activities"""
        activities = await self._get_recent_activities(user_id, self.analysis_window)
        
        if not activities:
            return TradingContextState.IDLE
        
        # Calculate context scores
        context_scores = self._calculate_context_scores(activities)
        
        # Determine context based on highest score and thresholds
        return self._classify_context(context_scores)
    
    async def get_stress_metrics(self, user_id: str) -> UserStressMetrics:
        """Calculate current stress metrics for the user"""
        activities = await self._get_recent_activities(user_id, 300)  # 5-minute window
        
        if not activities:
            return UserStressMetrics()
        
        # Calculate stress indicators
        click_frequency = self._calculate_click_frequency(activities)
        error_rate = self._calculate_error_rate(activities)
        session_intensity = await self._calculate_session_intensity(user_id)
        time_since_loss = await self._get_time_since_last_loss(user_id)
        market_volatility = await self._get_market_volatility()
        
        return UserStressMetrics(
            click_frequency=click_frequency,
            error_rate=error_rate,
            session_intensity=session_intensity,
            time_since_loss=time_since_loss,
            market_volatility=market_volatility
        )
    
    async def _get_recent_activities(
        self, 
        user_id: str, 
        window_seconds: int
    ) -> List[UserActivity]:
        """Get user activities within the specified time window"""
        activity_key = f"user_activities:{user_id}"
        cutoff_time = time.time() - window_seconds
        
        # Get activities from Redis sorted set
        raw_activities = await self.redis.zrangebyscore(
            activity_key,
            cutoff_time,
            time.time(),
            withscores=True
        )
        
        activities = []
        for activity_json, timestamp in raw_activities:
            activity_data = json.loads(activity_json)
            
            activity = UserActivity(
                user_id=user_id,
                activity_type=activity_data["type"],
                timestamp=datetime.fromtimestamp(timestamp),
                metadata=json.loads(activity_data["metadata"])
            )
            activities.append(activity)
        
        return activities
    
    def _calculate_context_scores(self, activities: List[UserActivity]) -> Dict[str, float]:
        """Calculate weighted scores for different context states"""
        scores = {
            "order_entry": 0.0,
            "chart_analysis": 0.0,
            "position_management": 0.0,
            "education_mode": 0.0,
            "stress": 0.0,
            "concentration": 0.0,
            "engagement": 0.0,
            "achievement_friendly": 0.0
        }
        
        if not activities:
            return scores
        
        # Calculate time-weighted scores (recent activities have higher weight)
        now = time.time()
        total_weight = 0.0
        
        for activity in activities:
            try:
                activity_type = ActivityType(activity.activity_type)
                weights = self.activity_weights.get(activity_type, {})
                
                # Time decay: recent activities weighted higher
                time_diff = now - activity.timestamp.timestamp()
                time_weight = max(0.1, 1.0 - (time_diff / self.analysis_window))
                
                # Apply weights to scores
                for score_type, weight in weights.items():
                    if score_type in scores:
                        scores[score_type] += weight * time_weight
                        total_weight += time_weight
                        
            except ValueError:
                # Skip unknown activity types
                continue
        
        # Normalize scores by total weight
        if total_weight > 0:
            for score_type in scores:
                scores[score_type] /= total_weight
        
        return scores
    
    def _classify_context(self, context_scores: Dict[str, float]) -> TradingContextState:
        """Classify trading context based on calculated scores"""
        thresholds = self.context_thresholds
        
        # Check for high stress first (overrides other contexts)
        if context_scores["stress"] >= thresholds["high_stress_threshold"]:
            return TradingContextState.HIGH_STRESS
        
        # Check for order entry (high priority context)
        if context_scores["order_entry"] >= thresholds["order_entry_threshold"]:
            return TradingContextState.ORDER_ENTRY
        
        # Check for chart analysis
        if context_scores["chart_analysis"] >= thresholds["chart_analysis_threshold"]:
            return TradingContextState.CHART_ANALYSIS
        
        # Check for position management
        if context_scores["position_management"] >= thresholds["position_management_threshold"]:
            return TradingContextState.POSITION_MANAGEMENT
        
        # Check for education mode
        if context_scores["education_mode"] >= thresholds["education_mode_threshold"]:
            return TradingContextState.EDUCATION_MODE
        
        # Check for idle state
        total_activity = sum(context_scores[key] for key in ["order_entry", "chart_analysis", "position_management", "engagement"])
        if total_activity < thresholds["idle_threshold"]:
            return TradingContextState.IDLE
        
        # Default to idle if no clear context
        return TradingContextState.IDLE
    
    def _calculate_click_frequency(self, activities: List[UserActivity]) -> float:
        """Calculate clicks per minute from activities"""
        if not activities:
            return 0.0
        
        click_count = sum(1 for activity in activities if activity.activity_type == ActivityType.CLICK.value)
        time_span = (max(activity.timestamp for activity in activities) - 
                    min(activity.timestamp for activity in activities)).total_seconds()
        
        if time_span == 0:
            return 0.0
        
        return (click_count / time_span) * 60  # Convert to clicks per minute
    
    def _calculate_error_rate(self, activities: List[UserActivity]) -> float:
        """Calculate error rate from activities"""
        if not activities:
            return 0.0
        
        error_count = sum(1 for activity in activities if activity.activity_type == ActivityType.ERROR_OCCURRED.value)
        total_activities = len(activities)
        
        return error_count / total_activities if total_activities > 0 else 0.0
    
    async def _calculate_session_intensity(self, user_id: str) -> float:
        """Calculate trading session intensity (normalized 0-1)"""
        # Get trading activities in last 30 minutes
        trading_activities = await self._get_recent_activities(user_id, 1800)
        
        trading_types = {
            ActivityType.ORDER_PLACED.value,
            ActivityType.ORDER_MODIFIED.value,
            ActivityType.POSITION_OPENED.value,
            ActivityType.POSITION_CLOSED.value
        }
        
        trading_count = sum(1 for activity in trading_activities 
                           if activity.activity_type in trading_types)
        
        # Normalize: 0-10 trades in 30 minutes = 0.0-1.0 intensity
        return min(trading_count / 10.0, 1.0)
    
    async def _get_time_since_last_loss(self, user_id: str) -> Optional[float]:
        """Get time in minutes since last losing trade"""
        # This would integrate with trading service to get recent trade results
        # For now, return None (not implemented)
        # TODO: Integrate with trading service
        return None
    
    async def _get_market_volatility(self) -> float:
        """Get current market volatility index"""
        # This would integrate with market data service
        # For now, return moderate volatility
        # TODO: Integrate with market data service
        return 0.02  # 2% volatility
    
    async def get_context_history(self, user_id: str, hours: int = 1) -> List[Dict]:
        """Get historical context states for analysis"""
        activities = await self._get_recent_activities(user_id, hours * 3600)
        
        # Group activities into 5-minute windows
        window_size = 300  # 5 minutes
        windows = {}
        
        for activity in activities:
            window_start = int(activity.timestamp.timestamp() // window_size) * window_size
            if window_start not in windows:
                windows[window_start] = []
            windows[window_start].append(activity)
        
        # Analyze each window
        context_history = []
        for window_start, window_activities in sorted(windows.items()):
            context_scores = self._calculate_context_scores(window_activities)
            context_state = self._classify_context(context_scores)
            
            context_history.append({
                "window_start": datetime.fromtimestamp(window_start),
                "context": context_state.value,
                "scores": context_scores,
                "activity_count": len(window_activities)
            })
        
        return context_history
    
    async def get_achievement_friendly_score(self, user_id: str) -> float:
        """Get current achievement-friendliness score (0-1)"""
        activities = await self._get_recent_activities(user_id, self.analysis_window)
        context_scores = self._calculate_context_scores(activities)
        current_context = self._classify_context(context_scores)
        
        # Context-based achievement friendliness
        context_friendliness = {
            TradingContextState.EDUCATION_MODE: 0.9,
            TradingContextState.IDLE: 0.8,
            TradingContextState.POSITION_MANAGEMENT: 0.6,
            TradingContextState.CHART_ANALYSIS: 0.3,
            TradingContextState.ORDER_ENTRY: 0.1,
            TradingContextState.HIGH_STRESS: 0.0
        }
        
        base_score = context_friendliness.get(current_context, 0.5)
        
        # Adjust based on achievement_friendly score from activities
        activity_bonus = context_scores.get("achievement_friendly", 0.0) * 0.3
        
        return min(base_score + activity_bonus, 1.0)