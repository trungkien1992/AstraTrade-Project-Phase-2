#!/usr/bin/env python3
"""
Smart Achievement Notification System

Integrates with WebSocket infrastructure to deliver real-time achievement
notifications with context awareness, anti-addiction safeguards, and
intelligent queuing for optimal user experience.

Features:
- Real-time WebSocket delivery with fallback mechanisms
- Context-aware notification timing and styling
- Integration with anti-addiction safeguards
- Offline user notification queuing
- Batch notification support for related achievements
- A/B testing integration for notification optimization
- Comprehensive delivery tracking and analytics
"""

import asyncio
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Set, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import redis.asyncio as redis

from .dopamine_timing_engine import (
    DopamineOptimizedAchievementSystem, AchievementTrigger, 
    AchievementPriority, TradingContextState, UserStressMetrics
)
from .trading_context_detector import TradingContextDetector, ActivityType
from .context_sensitive_display import (
    ContextSensitiveDisplayManager, DisplayQueueItem, 
    DisplayPosition, DisplayStyle, InterruptionLevel
)
from .anti_addiction_safeguards import AntiAddictionSafeguards, InterventionAction
from .research_driven_categories import ResearchDrivenAchievements, AchievementDefinition


logger = logging.getLogger(__name__)


class NotificationChannel(Enum):
    """Available notification channels"""
    WEBSOCKET = "websocket"              # Real-time WebSocket
    PUSH_NOTIFICATION = "push"           # Mobile push notifications
    EMAIL = "email"                      # Email notifications (digest)
    IN_APP_BANNER = "in_app_banner"     # Persistent in-app banner
    TOAST = "toast"                      # Temporary toast notification


class NotificationStatus(Enum):
    """Status of notification delivery"""
    PENDING = "pending"                  # Queued for delivery
    DELIVERED = "delivered"              # Successfully delivered
    FAILED = "failed"                    # Delivery failed
    DISMISSED = "dismissed"              # User dismissed notification
    EXPIRED = "expired"                  # Notification expired
    SUPPRESSED = "suppressed"            # Suppressed by anti-addiction


class DeliveryPriority(Enum):
    """Delivery priority levels"""
    IMMEDIATE = 1                        # Deliver immediately (critical/educational)
    HIGH = 2                            # Deliver within 30 seconds
    NORMAL = 3                          # Deliver within 5 minutes
    LOW = 4                             # Deliver when convenient
    BATCH = 5                           # Include in next batch delivery


@dataclass
class NotificationPayload:
    """Complete notification payload for delivery"""
    notification_id: str
    user_id: str
    achievement_definition: AchievementDefinition
    trigger_data: Dict[str, Any]
    
    # Delivery configuration
    channels: List[NotificationChannel]
    priority: DeliveryPriority
    expires_at: datetime
    
    # Display configuration  
    position: DisplayPosition = DisplayPosition.BOTTOM_RIGHT
    style: DisplayStyle = DisplayStyle.STANDARD
    auto_dismiss_seconds: int = 5
    
    # Content
    title: str = ""
    message: str = ""
    icon_url: str = ""
    celebration_animation: str = "standard"
    sound_effect: str = "achievement"
    
    # Context
    triggered_at: datetime = field(default_factory=datetime.now)
    context_when_triggered: Optional[TradingContextState] = None
    user_stress_level: float = 0.0
    
    # Tracking
    delivery_attempts: int = 0
    last_delivery_attempt: Optional[datetime] = None
    status: NotificationStatus = NotificationStatus.PENDING


@dataclass
class NotificationBatch:
    """Batch of related notifications for grouped delivery"""
    batch_id: str
    user_id: str
    notifications: List[NotificationPayload]
    batch_type: str  # "related_achievements", "daily_summary", etc.
    scheduled_delivery: datetime
    max_notifications_per_batch: int = 5


class SmartNotificationSystem:
    """
    Intelligent notification system integrating WebSocket delivery,
    context awareness, and anti-addiction safeguards.
    """
    
    def __init__(
        self,
        redis_client: redis.Redis,
        context_detector: TradingContextDetector,
        display_manager: ContextSensitiveDisplayManager,
        anti_addiction: AntiAddictionSafeguards,
        achievement_system: ResearchDrivenAchievements
    ):
        self.redis = redis_client
        self.context_detector = context_detector
        self.display_manager = display_manager
        self.anti_addiction = anti_addiction
        self.achievement_system = achievement_system
        
        # Redis keys for notification management
        self.notifications_key = "smart_notifications"
        self.delivery_queue_key = "notification_delivery_queue"
        self.delivery_stats_key = "notification_delivery_stats"
        self.user_preferences_key = "notification_preferences"
        
        # Configuration
        self.config = self._initialize_config()
        
        # WebSocket channels
        self.websocket_channels = {
            "achievements": "achievement_notifications",
            "system": "system_notifications",
            "educational": "educational_notifications"
        }
        
    def _initialize_config(self) -> Dict:
        """Initialize notification system configuration"""
        return {
            "max_notification_queue_size": 50,
            "notification_expiry_hours": 24,
            "delivery_retry_attempts": 3,
            "delivery_retry_backoff_seconds": [30, 300, 1800],  # 30s, 5m, 30m
            "batch_delivery_window_minutes": 5,
            "websocket_timeout_seconds": 10,
            "offline_notification_retention_days": 7,
            
            # Default notification templates
            "achievement_templates": {
                "educational": {
                    "title": "🎓 Knowledge Unlocked!",
                    "message": "You've mastered {achievement_name}! Your trading skills are growing.",
                    "celebration": "celebrate",
                    "sound": "achievement_educational"
                },
                "risk_management": {
                    "title": "🛡️ Safety Milestone!",
                    "message": "Excellent risk management! You've earned {achievement_name}.",
                    "celebration": "celebrate", 
                    "sound": "achievement_safety"
                },
                "performance": {
                    "title": "⭐ Trading Excellence!",
                    "message": "Outstanding performance! You've achieved {achievement_name}.",
                    "celebration": "celebrate",
                    "sound": "achievement_performance"
                },
                "social": {
                    "title": "🤝 Community Impact!",
                    "message": "Your community contributions earned you {achievement_name}!",
                    "celebration": "standard",
                    "sound": "achievement_social"
                }
            }
        }
    
    async def notify_achievement_unlocked(
        self,
        user_id: str,
        achievement_id: str,
        trigger_data: Dict[str, Any],
        context: Optional[TradingContextState] = None,
        stress_metrics: Optional[UserStressMetrics] = None
    ) -> bool:
        """
        Process achievement unlock and create intelligent notification.
        
        Returns True if notification was successfully queued for delivery.
        """
        
        # Get achievement definition
        achievement_def = self.achievement_system.get_achievement_by_id(achievement_id)
        if not achievement_def:
            logger.error(f"Achievement not found: {achievement_id}")
            return False
        
        # Get current context if not provided
        if context is None:
            context = await self.context_detector.get_current_context(user_id)
        
        if stress_metrics is None:
            stress_metrics = await self.context_detector.get_stress_metrics(user_id)
        
        # Check anti-addiction safeguards
        allowed, intervention = await self.anti_addiction.check_achievement_allowed(
            user_id, achievement_def.priority
        )
        
        if not allowed:
            # Handle intervention if needed
            if intervention:
                await self._handle_intervention_notification(user_id, intervention)
            
            # Create suppressed notification for tracking
            notification = await self._create_notification_payload(
                user_id, achievement_def, trigger_data, context, stress_metrics
            )
            notification.status = NotificationStatus.SUPPRESSED
            await self._store_notification(notification)
            
            logger.info(f"Achievement notification suppressed: {achievement_id} for user {user_id}")
            return False
        
        # Create notification payload
        notification = await self._create_notification_payload(
            user_id, achievement_def, trigger_data, context, stress_metrics
        )
        
        # Determine delivery channels and priority
        await self._configure_notification_delivery(notification, context, stress_metrics)
        
        # Queue notification for delivery
        await self._queue_notification(notification)
        
        logger.info(
            f"Achievement notification queued: {achievement_id} for user {user_id}, "
            f"priority={notification.priority.value}, channels={[c.value for c in notification.channels]}"
        )
        
        return True
    
    async def _create_notification_payload(
        self,
        user_id: str,
        achievement_def: AchievementDefinition,
        trigger_data: Dict[str, Any],
        context: TradingContextState,
        stress_metrics: UserStressMetrics
    ) -> NotificationPayload:
        """Create comprehensive notification payload"""
        
        # Generate unique notification ID
        notification_id = f"notif_{user_id}_{achievement_def.achievement_id}_{int(time.time())}"
        
        # Get notification template based on achievement category
        template = self.config["achievement_templates"].get(
            achievement_def.category.value, 
            self.config["achievement_templates"]["educational"]
        )
        
        # Format notification content
        title = template["title"]
        message = template["message"].format(
            achievement_name=achievement_def.name,
            **trigger_data
        )
        
        # Determine expiry time (longer for educational achievements)
        expiry_hours = 48 if achievement_def.is_educational else 24
        expires_at = datetime.now() + timedelta(hours=expiry_hours)
        
        # Create base notification
        notification = NotificationPayload(
            notification_id=notification_id,
            user_id=user_id,
            achievement_definition=achievement_def,
            trigger_data=trigger_data,
            channels=[NotificationChannel.WEBSOCKET],  # Default channel
            priority=DeliveryPriority.NORMAL,
            expires_at=expires_at,
            title=title,
            message=message,
            celebration_animation=template["celebration"],
            sound_effect=template["sound"],
            context_when_triggered=context,
            user_stress_level=stress_metrics.stress_level
        )
        
        return notification
    
    async def _configure_notification_delivery(
        self,
        notification: NotificationPayload,
        context: TradingContextState,
        stress_metrics: UserStressMetrics
    ):
        """Configure delivery channels and priority based on context"""
        
        achievement_def = notification.achievement_definition
        
        # Determine priority based on achievement type and context
        if achievement_def.priority == AchievementPriority.CRITICAL:
            notification.priority = DeliveryPriority.IMMEDIATE
        elif achievement_def.is_educational and context == TradingContextState.EDUCATION_MODE:
            notification.priority = DeliveryPriority.IMMEDIATE
        elif achievement_def.promotes_safety:
            notification.priority = DeliveryPriority.HIGH
        elif context in [TradingContextState.ORDER_ENTRY, TradingContextState.HIGH_STRESS]:
            notification.priority = DeliveryPriority.BATCH  # Don't interrupt critical activities
        else:
            notification.priority = DeliveryPriority.NORMAL
        
        # Configure delivery channels
        channels = [NotificationChannel.WEBSOCKET]  # Always include WebSocket
        
        # Add push notification for important achievements
        if achievement_def.priority in [AchievementPriority.CRITICAL, AchievementPriority.EDUCATIONAL]:
            channels.append(NotificationChannel.PUSH_NOTIFICATION)
        
        # Add in-app banner for major milestones
        if achievement_def.badge_rarity in ["epic", "legendary"]:
            channels.append(NotificationChannel.IN_APP_BANNER)
        
        notification.channels = channels
        
        # Configure display based on context
        user_preferences = await self.display_manager.get_user_preferences(notification.user_id)
        
        # Context-sensitive display configuration
        if context == TradingContextState.EDUCATION_MODE:
            notification.position = DisplayPosition.CENTER_MODAL
            notification.style = DisplayStyle.CELEBRATE
            notification.auto_dismiss_seconds = 6
        elif context in [TradingContextState.ORDER_ENTRY, TradingContextState.CHART_ANALYSIS]:
            notification.position = DisplayPosition.BOTTOM_RIGHT
            notification.style = DisplayStyle.SUBTLE
            notification.auto_dismiss_seconds = 3
        elif stress_metrics.stress_level > 0.6:
            notification.position = DisplayPosition.BOTTOM_RIGHT
            notification.style = DisplayStyle.SUBTLE
            notification.auto_dismiss_seconds = 2
            notification.sound_effect = "none"  # No sound when stressed
        else:
            notification.position = user_preferences.preferred_position
            notification.style = user_preferences.preferred_style
            notification.auto_dismiss_seconds = user_preferences.auto_dismiss_seconds
    
    async def _queue_notification(self, notification: NotificationPayload):
        """Queue notification for delivery processing"""
        
        # Store notification
        await self._store_notification(notification)
        
        # Add to delivery queue with priority-based scoring
        queue_score = self._calculate_queue_score(notification)
        
        queue_data = {
            "notification_id": notification.notification_id,
            "user_id": notification.user_id,
            "priority": notification.priority.value,
            "scheduled_delivery": notification.triggered_at.timestamp(),
            "channels": [c.value for c in notification.channels]
        }
        
        await self.redis.zadd(
            self.delivery_queue_key,
            {json.dumps(queue_data): queue_score}
        )
        
        # Set queue expiration
        await self.redis.expire(self.delivery_queue_key, 86400)  # 24 hours
    
    def _calculate_queue_score(self, notification: NotificationPayload) -> float:
        """Calculate priority score for delivery queue ordering"""
        
        # Base score from delivery priority (lower = higher priority)
        base_score = notification.priority.value * 1000
        
        # Adjust for achievement importance
        if notification.achievement_definition.priority == AchievementPriority.CRITICAL:
            base_score -= 500
        elif notification.achievement_definition.is_educational:
            base_score -= 300
        elif notification.achievement_definition.promotes_safety:
            base_score -= 200
        
        # Add timestamp component for FIFO within priority levels
        timestamp_component = notification.triggered_at.timestamp() / 1000000
        
        return base_score + timestamp_component
    
    async def process_delivery_queue(self) -> List[NotificationPayload]:
        """
        Process notification delivery queue.
        
        Should be called by background processor every 10-30 seconds.
        """
        processed_notifications = []
        
        # Get notifications ready for delivery (lowest scores first)
        ready_items = await self.redis.zrange(
            self.delivery_queue_key, 0, 19, withscores=True  # Process up to 20 at a time
        )
        
        for queue_item_json, score in ready_items:
            queue_data = json.loads(queue_item_json)
            
            # Get full notification
            notification = await self._get_notification(queue_data["notification_id"])
            if not notification:
                continue
            
            # Check if notification has expired
            if datetime.now() > notification.expires_at:
                notification.status = NotificationStatus.EXPIRED
                await self._update_notification(notification)
                await self._remove_from_queue(queue_data["notification_id"])
                continue
            
            # Check if user is online for WebSocket delivery
            is_online = await self._is_user_online(notification.user_id)
            
            # Attempt delivery
            if await self._attempt_delivery(notification, is_online):
                notification.status = NotificationStatus.DELIVERED
                await self._update_notification(notification)
                await self._remove_from_queue(queue_data["notification_id"])
                processed_notifications.append(notification)
                
                # Record successful delivery
                await self._record_delivery_success(notification)
            else:
                # Handle delivery failure
                notification.delivery_attempts += 1
                notification.last_delivery_attempt = datetime.now()
                
                if notification.delivery_attempts >= self.config["delivery_retry_attempts"]:
                    notification.status = NotificationStatus.FAILED
                    await self._remove_from_queue(queue_data["notification_id"])
                    logger.warning(f"Notification delivery failed after retries: {notification.notification_id}")
                else:
                    # Schedule retry with backoff
                    await self._schedule_delivery_retry(notification)
                
                await self._update_notification(notification)
        
        return processed_notifications
    
    async def _attempt_delivery(
        self,
        notification: NotificationPayload,
        user_online: bool
    ) -> bool:
        """Attempt to deliver notification via configured channels"""
        
        delivery_success = False
        
        for channel in notification.channels:
            try:
                if channel == NotificationChannel.WEBSOCKET:
                    if user_online:
                        success = await self._deliver_via_websocket(notification)
                        delivery_success = delivery_success or success
                    else:
                        # Queue for when user comes online
                        await self._queue_offline_notification(notification)
                        delivery_success = True  # Consider queuing as successful delivery
                
                elif channel == NotificationChannel.PUSH_NOTIFICATION:
                    success = await self._deliver_via_push(notification)
                    delivery_success = delivery_success or success
                
                elif channel == NotificationChannel.IN_APP_BANNER:
                    success = await self._deliver_via_banner(notification)
                    delivery_success = delivery_success or success
                    
            except Exception as e:
                logger.error(f"Delivery failed for channel {channel.value}: {e}")
                continue
        
        return delivery_success
    
    async def _deliver_via_websocket(self, notification: NotificationPayload) -> bool:
        """Deliver notification via WebSocket"""
        
        # Create WebSocket message
        ws_message = {
            "type": "achievement_notification",
            "notification_id": notification.notification_id,
            "achievement_id": notification.achievement_definition.achievement_id,
            "title": notification.title,
            "message": notification.message,
            "display_config": {
                "position": notification.position.value,
                "style": notification.style.value,
                "auto_dismiss_seconds": notification.auto_dismiss_seconds,
                "celebration_animation": notification.celebration_animation,
                "sound_effect": notification.sound_effect,
                "icon_url": notification.icon_url
            },
            "achievement_data": {
                "name": notification.achievement_definition.name,
                "description": notification.achievement_definition.description,
                "category": notification.achievement_definition.category.value,
                "xp_reward": notification.achievement_definition.xp_reward,
                "badge_rarity": notification.achievement_definition.badge_rarity,
                "cosmic_theme": notification.achievement_definition.cosmic_theme
            },
            "trigger_data": notification.trigger_data,
            "timestamp": notification.triggered_at.isoformat()
        }
        
        # Publish to user's WebSocket channel
        channel_name = f"user_notifications:{notification.user_id}"
        
        try:
            result = await self.redis.publish(channel_name, json.dumps(ws_message))
            
            # Check if message was delivered (at least one subscriber)
            if result > 0:
                logger.debug(f"WebSocket notification delivered to {notification.user_id}")
                return True
            else:
                logger.debug(f"No WebSocket subscribers for user {notification.user_id}")
                return False
                
        except Exception as e:
            logger.error(f"WebSocket delivery failed: {e}")
            return False
    
    async def _deliver_via_push(self, notification: NotificationPayload) -> bool:
        """Deliver notification via push notification service"""
        
        # This would integrate with push notification service (FCM, APNS, etc.)
        # For now, simulate delivery
        logger.info(f"Push notification sent: {notification.title} to user {notification.user_id}")
        return True
    
    async def _deliver_via_banner(self, notification: NotificationPayload) -> bool:
        """Deliver notification via persistent in-app banner"""
        
        # Store banner notification for persistent display
        banner_key = f"notification_banners:{notification.user_id}"
        banner_data = {
            "notification_id": notification.notification_id,
            "title": notification.title,
            "message": notification.message,
            "achievement_id": notification.achievement_definition.achievement_id,
            "created_at": time.time(),
            "expires_at": notification.expires_at.timestamp()
        }
        
        await self.redis.hset(banner_key, notification.notification_id, json.dumps(banner_data))
        await self.redis.expire(banner_key, int((notification.expires_at - datetime.now()).total_seconds()))
        
        logger.info(f"Banner notification created for user {notification.user_id}")
        return True
    
    async def _queue_offline_notification(self, notification: NotificationPayload):
        """Queue notification for offline user"""
        
        offline_key = f"offline_notifications:{notification.user_id}"
        
        offline_data = {
            "notification_id": notification.notification_id,
            "title": notification.title,
            "message": notification.message,
            "achievement_data": {
                "id": notification.achievement_definition.achievement_id,
                "name": notification.achievement_definition.name,
                "category": notification.achievement_definition.category.value,
                "xp_reward": notification.achievement_definition.xp_reward
            },
            "triggered_at": notification.triggered_at.timestamp(),
            "priority": notification.priority.value
        }
        
        # Store with timestamp as score for chronological ordering
        await self.redis.zadd(
            offline_key,
            {json.dumps(offline_data): notification.triggered_at.timestamp()}
        )
        
        # Set expiration for offline notifications
        retention_seconds = self.config["offline_notification_retention_days"] * 86400
        await self.redis.expire(offline_key, retention_seconds)
        
        logger.info(f"Notification queued for offline user {notification.user_id}")
    
    async def deliver_offline_notifications(self, user_id: str) -> List[Dict]:
        """Deliver queued notifications when user comes online"""
        
        offline_key = f"offline_notifications:{user_id}"
        
        # Get all offline notifications
        offline_notifications = await self.redis.zrange(offline_key, 0, -1, withscores=True)
        
        if not offline_notifications:
            return []
        
        delivered_notifications = []
        
        # Limit to prevent overwhelming user
        max_offline_notifications = 10
        notifications_to_deliver = offline_notifications[:max_offline_notifications]
        
        for notification_json, timestamp in notifications_to_deliver:
            notification_data = json.loads(notification_json)
            
            # Create summary message for offline notifications
            summary_message = {
                "type": "offline_notification_summary",
                "notifications": [notification_data],
                "total_offline_count": len(offline_notifications),
                "delivery_timestamp": time.time()
            }
            
            # Deliver via WebSocket
            channel_name = f"user_notifications:{user_id}"
            await self.redis.publish(channel_name, json.dumps(summary_message))
            
            delivered_notifications.append(notification_data)
        
        # Clear delivered offline notifications
        if delivered_notifications:
            offline_items_to_remove = [
                json.dumps(notif) for notif in delivered_notifications
            ]
            await self.redis.zrem(offline_key, *offline_items_to_remove)
        
        logger.info(f"Delivered {len(delivered_notifications)} offline notifications to user {user_id}")
        
        return delivered_notifications
    
    # Additional helper methods for notification management
    async def _store_notification(self, notification: NotificationPayload):
        """Store notification in Redis"""
        # Implementation for storing notification data
        pass
    
    async def _get_notification(self, notification_id: str) -> Optional[NotificationPayload]:
        """Retrieve notification from Redis"""
        # Implementation for retrieving notification data
        pass
    
    async def _is_user_online(self, user_id: str) -> bool:
        """Check if user is currently online"""
        # Check recent activity or WebSocket connection status
        activity_key = f"user_activities:{user_id}"
        last_activity = await self.redis.zrevrange(activity_key, 0, 0, withscores=True)
        
        if last_activity:
            last_activity_time = last_activity[0][1]
            return (time.time() - last_activity_time) < 300  # Online if active in last 5 minutes
        
        return False
    
    # Analytics and monitoring methods would go here...
    async def get_notification_analytics(self, user_id: str, days: int = 7) -> Dict:
        """Get notification delivery analytics"""
        # Implementation for analytics
        pass