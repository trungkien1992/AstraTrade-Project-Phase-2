import 'dart:async';
import 'dart:convert';
import 'dart:math';
import 'package:flutter/foundation.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:shared_preferences/shared_preferences.dart';

class NotificationService {
  static final NotificationService _instance = NotificationService._internal();
  factory NotificationService() => _instance;
  NotificationService._internal();

  final FlutterLocalNotificationsPlugin _localNotifications = FlutterLocalNotificationsPlugin();
  final StreamController<GameNotification> _notificationController = StreamController<GameNotification>.broadcast();
  
  Timer? _mockEventTimer;
  bool _isInitialized = false;
  List<GameNotification> _notificationHistory = [];
  
  // Stream for listening to notifications
  Stream<GameNotification> get notificationStream => _notificationController.stream;
  
  // Get notification history
  List<GameNotification> get notificationHistory => List.unmodifiable(_notificationHistory);

  Future<void> initialize() async {
    if (_isInitialized) return;
    
    // Initialize local notifications
    const androidSettings = AndroidInitializationSettings('@mipmap/ic_launcher');
    const iosSettings = DarwinInitializationSettings(
      requestAlertPermission: true,
      requestBadgePermission: true,
      requestSoundPermission: true,
    );
    
    const initSettings = InitializationSettings(
      android: androidSettings,
      iOS: iosSettings,
    );
    
    await _localNotifications.initialize(
      initSettings,
      onDidReceiveNotificationResponse: _onNotificationTapped,
    );
    
    // Load notification history
    await _loadNotificationHistory();
    
    // Start mock real-time events for development
    _startMockEventTimer();
    
    _isInitialized = true;
  }

  void _onNotificationTapped(NotificationResponse response) {
    // Handle notification tap
    final payload = response.payload;
    if (payload != null) {
      try {
        final data = json.decode(payload);
        final notification = GameNotification.fromJson(data);
        _notificationController.add(notification);
      } catch (e) {
        debugPrint('Error parsing notification payload: $e');
      }
    }
  }

  // Show local notification
  Future<void> showNotification(GameNotification notification) async {
    if (!_isInitialized) await initialize();
    
    const androidDetails = AndroidNotificationDetails(
      'astratrade_game',
      'AstraTrade Game',
      channelDescription: 'Game events and updates',
      importance: Importance.high,
      priority: Priority.high,
      icon: '@mipmap/ic_launcher',
    );
    
    const iosDetails = DarwinNotificationDetails(
      presentAlert: true,
      presentBadge: true,
      presentSound: true,
    );
    
    const details = NotificationDetails(
      android: androidDetails,
      iOS: iosDetails,
    );

    await _localNotifications.show(
      notification.id.hashCode,
      notification.title,
      notification.message,
      details,
      payload: json.encode(notification.toJson()),
    );

    // Add to stream and history
    _notificationController.add(notification);
    _addToHistory(notification);
  }

  // Add notification to history and save
  void _addToHistory(GameNotification notification) {
    _notificationHistory.insert(0, notification);
    
    // Keep only last 100 notifications
    if (_notificationHistory.length > 100) {
      _notificationHistory = _notificationHistory.take(100).toList();
    }
    
    _saveNotificationHistory();
  }

  // Save notification history to local storage
  Future<void> _saveNotificationHistory() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final historyJson = _notificationHistory.map((n) => n.toJson()).toList();
      await prefs.setString('notification_history', json.encode(historyJson));
    } catch (e) {
      debugPrint('Error saving notification history: $e');
    }
  }

  // Load notification history from local storage
  Future<void> _loadNotificationHistory() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final historyString = prefs.getString('notification_history');
      
      if (historyString != null) {
        final historyJson = json.decode(historyString) as List;
        _notificationHistory = historyJson
            .map((json) => GameNotification.fromJson(json))
            .toList();
      }
    } catch (e) {
      debugPrint('Error loading notification history: $e');
      _notificationHistory = [];
    }
  }

  // Clear all notifications
  Future<void> clearAllNotifications() async {
    await _localNotifications.cancelAll();
    _notificationHistory.clear();
    await _saveNotificationHistory();
  }

  // Mark notification as read
  void markAsRead(String notificationId) {
    final index = _notificationHistory.indexWhere((n) => n.id == notificationId);
    if (index != -1) {
      _notificationHistory[index] = _notificationHistory[index].copyWith(isRead: true);
      _saveNotificationHistory();
    }
  }

  // Get unread count
  int get unreadCount => _notificationHistory.where((n) => !n.isRead).length;

  // Start mock timer for development (simulates real-time events)
  void _startMockEventTimer() {
    _mockEventTimer?.cancel();
    _mockEventTimer = Timer.periodic(const Duration(minutes: 2), (timer) {
      _generateMockNotification();
    });
  }

  // Generate mock notifications for development
  void _generateMockNotification() {
    final random = Random();
    final mockEvents = [
      {
        'type': NotificationType.constellation,
        'title': 'Constellation Battle Started!',
        'message': 'Stellar Pioneers vs Cosmic Guardians - Trading Duel is now active!',
        'data': {'battle_id': 'battle_${random.nextInt(1000)}'}
      },
      {
        'type': NotificationType.achievement,
        'title': 'Achievement Unlocked!',
        'message': 'You\'ve earned a Rare Genesis NFT for reaching Level 25!',
        'data': {'achievement': 'level_milestone', 'level': 25}
      },
      {
        'type': NotificationType.viral,
        'title': 'Your Meme is Going Viral!',
        'message': 'Your "Diamond Hands" meme has 500+ shares! 🚀',
        'data': {'meme_id': 'meme_${random.nextInt(1000)}', 'shares': 500}
      },
      {
        'type': NotificationType.trading,
        'title': 'Trading Opportunity!',
        'message': 'ETH/USDT is showing strong momentum - perfect for your strategy!',
        'data': {'pair': 'ETH/USDT', 'trend': 'bullish'}
      },
      {
        'type': NotificationType.social,
        'title': 'New Constellation Member!',
        'message': 'CosmicTrader has joined your constellation. Welcome them!',
        'data': {'username': 'CosmicTrader'}
      },
      {
        'type': NotificationType.marketplace,
        'title': 'NFT Sale Completed!',
        'message': 'Your Legendary Genesis NFT sold for 5,000 Stellar Shards!',
        'data': {'nft_id': 'genesis_legendary_123', 'price': 5000}
      },
    ];

    final event = mockEvents[random.nextInt(mockEvents.length)];
    final notification = GameNotification(
      id: 'mock_${DateTime.now().millisecondsSinceEpoch}',
      type: event['type'] as NotificationType,
      title: event['title'] as String,
      message: event['message'] as String,
      data: event['data'] as Map<String, dynamic>,
      timestamp: DateTime.now(),
      isRead: false,
    );

    showNotification(notification);
  }

  // Real-time event handlers (would be called by actual game events)
  
  void onConstellationBattleStarted(String battleId, String challengerName, String defenderName) {
    final notification = GameNotification(
      id: 'battle_start_$battleId',
      type: NotificationType.constellation,
      title: 'Constellation Battle Started!',
      message: '$challengerName is challenging $defenderName to battle!',
      data: {'battle_id': battleId, 'challenger': challengerName, 'defender': defenderName},
      timestamp: DateTime.now(),
      isRead: false,
    );
    
    showNotification(notification);
  }

  void onAchievementUnlocked(String achievementType, Map<String, dynamic> details) {
    final notification = GameNotification(
      id: 'achievement_${DateTime.now().millisecondsSinceEpoch}',
      type: NotificationType.achievement,
      title: 'Achievement Unlocked!',
      message: 'You\'ve earned a new Genesis NFT: ${achievementType.replaceAll('_', ' ').toUpperCase()}!',
      data: {'achievement': achievementType, ...details},
      timestamp: DateTime.now(),
      isRead: false,
    );
    
    showNotification(notification);
  }

  void onViralContentMilestone(String contentId, int milestone, String contentType) {
    final notification = GameNotification(
      id: 'viral_$contentId',
      type: NotificationType.viral,
      title: 'Content Going Viral! 🔥',
      message: 'Your $contentType reached $milestone interactions!',
      data: {'content_id': contentId, 'milestone': milestone, 'type': contentType},
      timestamp: DateTime.now(),
      isRead: false,
    );
    
    showNotification(notification);
  }

  void onTradingAlert(String symbol, String alertType, Map<String, dynamic> data) {
    final notification = GameNotification(
      id: 'trade_alert_${DateTime.now().millisecondsSinceEpoch}',
      type: NotificationType.trading,
      title: 'Trading Alert: $symbol',
      message: 'Price alert triggered for $symbol - $alertType signal detected!',
      data: {'symbol': symbol, 'alert_type': alertType, ...data},
      timestamp: DateTime.now(),
      isRead: false,
    );
    
    showNotification(notification);
  }

  void onSocialEvent(String eventType, String message, Map<String, dynamic> data) {
    final notification = GameNotification(
      id: 'social_${DateTime.now().millisecondsSinceEpoch}',
      type: NotificationType.social,
      title: 'Social Update',
      message: message,
      data: {'event_type': eventType, ...data},
      timestamp: DateTime.now(),
      isRead: false,
    );
    
    showNotification(notification);
  }

  void onMarketplaceEvent(String eventType, String itemName, double price) {
    final notification = GameNotification(
      id: 'marketplace_${DateTime.now().millisecondsSinceEpoch}',
      type: NotificationType.marketplace,
      title: 'Marketplace Update',
      message: eventType == 'sale' 
          ? 'Your $itemName sold for ${price.toStringAsFixed(0)} Stellar Shards!'
          : 'New $itemName listed for ${price.toStringAsFixed(0)} Stellar Shards!',
      data: {'event_type': eventType, 'item': itemName, 'price': price},
      timestamp: DateTime.now(),
      isRead: false,
    );
    
    showNotification(notification);
  }

  // Stop mock events and dispose
  void dispose() {
    _mockEventTimer?.cancel();
    _notificationController.close();
  }
}

// Notification data model
class GameNotification {
  final String id;
  final NotificationType type;
  final String title;
  final String message;
  final Map<String, dynamic> data;
  final DateTime timestamp;
  final bool isRead;

  const GameNotification({
    required this.id,
    required this.type,
    required this.title,
    required this.message,
    required this.data,
    required this.timestamp,
    this.isRead = false,
  });

  GameNotification copyWith({
    String? id,
    NotificationType? type,
    String? title,
    String? message,
    Map<String, dynamic>? data,
    DateTime? timestamp,
    bool? isRead,
  }) {
    return GameNotification(
      id: id ?? this.id,
      type: type ?? this.type,
      title: title ?? this.title,
      message: message ?? this.message,
      data: data ?? this.data,
      timestamp: timestamp ?? this.timestamp,
      isRead: isRead ?? this.isRead,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'type': type.name,
      'title': title,
      'message': message,
      'data': data,
      'timestamp': timestamp.toIso8601String(),
      'isRead': isRead,
    };
  }

  factory GameNotification.fromJson(Map<String, dynamic> json) {
    return GameNotification(
      id: json['id'],
      type: NotificationType.values.firstWhere(
        (e) => e.name == json['type'],
        orElse: () => NotificationType.general,
      ),
      title: json['title'],
      message: json['message'],
      data: Map<String, dynamic>.from(json['data'] ?? {}),
      timestamp: DateTime.parse(json['timestamp']),
      isRead: json['isRead'] ?? false,
    );
  }

  String get timeAgo {
    final now = DateTime.now();
    final difference = now.difference(timestamp);

    if (difference.inDays > 0) {
      return '${difference.inDays}d ago';
    } else if (difference.inHours > 0) {
      return '${difference.inHours}h ago';
    } else if (difference.inMinutes > 0) {
      return '${difference.inMinutes}m ago';
    } else {
      return 'Just now';
    }
  }

  String get typeIcon {
    switch (type) {
      case NotificationType.constellation:
        return '⭐';
      case NotificationType.achievement:
        return '🏆';
      case NotificationType.viral:
        return '🔥';
      case NotificationType.trading:
        return '📈';
      case NotificationType.social:
        return '👥';
      case NotificationType.marketplace:
        return '🛒';
      case NotificationType.general:
        return '📢';
    }
  }
}

enum NotificationType {
  constellation,
  achievement,
  viral,
  trading,
  social,
  marketplace,
  general,
}