import 'dart:async';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/simple_trade.dart';
import '../models/simple_gamification.dart';

/// Mobile-native notification service for trading app
/// Focused on practical trading alerts and achievement notifications
class MobileNotificationService {
  static final _instance = MobileNotificationService._internal();
  factory MobileNotificationService() => _instance;
  MobileNotificationService._internal();
  
  static const String _channelId = 'astratrade_notifications';
  static const String _channelName = 'AstraTrade';
  static const String _channelDescription = 'Trading alerts and progress notifications';
  
  final FlutterLocalNotificationsPlugin _localNotifications = 
      FlutterLocalNotificationsPlugin();
  
  bool _isInitialized = false;
  bool _notificationsEnabled = true;
  
  /// Initialize notification service
  Future<bool> initialize() async {
    if (_isInitialized) return true;
    
    try {
      await _requestPermissions();
      await _initializeLocalNotifications();
      await _loadSettings();
      
      _isInitialized = true;
      debugPrint('📱 Mobile notification service initialized');
      return true;
      
    } catch (e) {
      debugPrint('❌ Failed to initialize notifications: $e');
      return false;
    }
  }

  /// Request notification permissions
  Future<void> _requestPermissions() async {
    if (Platform.isIOS) {
      final status = await Permission.notification.request();
      debugPrint('📱 iOS notification permission: ${status.name}');
    } else if (Platform.isAndroid) {
      final status = await Permission.notification.request();
      debugPrint('📱 Android notification permission: ${status.name}');
    }
  }

  /// Initialize local notifications
  Future<void> _initializeLocalNotifications() async {
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
    
    // Create notification channel for Android
    if (Platform.isAndroid) {
      await _createNotificationChannel();
    }
  }

  /// Create Android notification channel
  Future<void> _createNotificationChannel() async {
    final androidChannel = AndroidNotificationChannel(
      _channelId,
      _channelName,
      description: _channelDescription,
      importance: Importance.high,
      enableVibration: true,
      vibrationPattern: Int64List.fromList([0, 250, 250, 250]),
    );
    
    await _localNotifications
        .resolvePlatformSpecificImplementation<
            AndroidFlutterLocalNotificationsPlugin>()
        ?.createNotificationChannel(androidChannel);
  }

  /// Load notification settings
  Future<void> _loadSettings() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      _notificationsEnabled = prefs.getBool('notifications_enabled') ?? true;
    } catch (e) {
      debugPrint('⚠️ Failed to load notification settings: $e');
    }
  }

  /// Save notification settings
  Future<void> _saveSettings() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setBool('notifications_enabled', _notificationsEnabled);
    } catch (e) {
      debugPrint('⚠️ Failed to save notification settings: $e');
    }
  }

  /// Handle notification tap
  void _onNotificationTapped(NotificationResponse response) {
    debugPrint('📱 Notification tapped: ${response.payload}');
    
    // Handle different notification types based on payload
    final payload = response.payload;
    if (payload != null) {
      if (payload.startsWith('trade:')) {
        // Navigate to trading screen
      } else if (payload.startsWith('achievement:')) {
        // Navigate to achievements screen
      } else if (payload.startsWith('daily:')) {
        // Navigate to main screen for daily bonus
      }
    }
  }

  /// Show trade completion notification
  Future<void> showTradeNotification({
    required SimpleTrade trade,
    required bool isProfit,
  }) async {
    if (!_isInitialized || !_notificationsEnabled) return;
    
    try {
      final title = isProfit 
          ? '🎉 Profitable Trade!'
          : '📊 Trade Completed';
      
      final profit = trade.profitLoss ?? 0.0;
      final body = isProfit
          ? 'Great job! You made \$${profit.toStringAsFixed(2)} on ${trade.symbol}'
          : 'Trade completed for ${trade.symbol}. P&L: \$${profit.toStringAsFixed(2)}';
      
      await _localNotifications.show(
        _generateNotificationId(),
        title,
        body,
        NotificationDetails(
          android: AndroidNotificationDetails(
            _channelId,
            _channelName,
            channelDescription: _channelDescription,
            importance: Importance.high,
            priority: Priority.high,
            icon: '@mipmap/ic_launcher',
            color: isProfit ? Colors.green : Colors.blue,
            vibrationPattern: isProfit 
                ? Int64List.fromList([0, 100, 100, 100]) // Celebration pattern
                : Int64List.fromList([0, 200]), // Simple pattern
          ),
          iOS: DarwinNotificationDetails(
            presentAlert: true,
            presentBadge: true,
            presentSound: true,
            sound: isProfit ? 'success.aiff' : 'default.aiff',
          ),
        ),
        payload: 'trade:${trade.id}',
      );
      
      debugPrint('📱 Trade notification sent: ${trade.id}');
      
    } catch (e) {
      debugPrint('❌ Failed to show trade notification: $e');
    }
  }

  /// Show achievement unlock notification
  Future<void> showAchievementNotification({
    required Achievement achievement,
    required int xpGained,
  }) async {
    if (!_isInitialized || !_notificationsEnabled) return;
    
    try {
      final title = '🏆 Achievement Unlocked!';
      final body = '${achievement.name}\n+${xpGained} XP earned';
      
      await _localNotifications.show(
        _generateNotificationId(),
        title,
        body,
        NotificationDetails(
          android: AndroidNotificationDetails(
            _channelId,
            _channelName,
            channelDescription: _channelDescription,
            importance: Importance.high,
            priority: Priority.high,
            icon: '@mipmap/ic_launcher',
            color: _getAchievementColor(achievement.rarity),
            vibrationPattern: _getAchievementVibration(achievement.rarity),
            styleInformation: BigTextStyleInformation(
              body,
              contentTitle: title,
              summaryText: achievement.description,
            ),
          ),
          iOS: const DarwinNotificationDetails(
            presentAlert: true,
            presentBadge: true,
            presentSound: true,
            sound: 'achievement.aiff',
          ),
        ),
        payload: 'achievement:${achievement.id}',
      );
      
      debugPrint('📱 Achievement notification sent: ${achievement.id}');
      
    } catch (e) {
      debugPrint('❌ Failed to show achievement notification: $e');
    }
  }

  /// Show level up notification
  Future<void> showLevelUpNotification({
    required int oldLevel,
    required int newLevel,
    required String rank,
  }) async {
    if (!_isInitialized || !_notificationsEnabled) return;
    
    try {
      final title = '⬆️ Level Up!';
      final body = 'Congratulations! You reached Level $newLevel\nRank: $rank';
      
      await _localNotifications.show(
        _generateNotificationId(),
        title,
        body,
        NotificationDetails(
          android: AndroidNotificationDetails(
            _channelId,
            _channelName,
            channelDescription: _channelDescription,
            importance: Importance.max,
            priority: Priority.max,
            icon: '@mipmap/ic_launcher',
            color: Colors.purple,
            vibrationPattern: Int64List.fromList([0, 100, 50, 100, 50, 200]), // Level up celebration
            styleInformation: BigTextStyleInformation(
              body,
              contentTitle: title,
              summaryText: 'Keep trading to unlock more features!',
            ),
          ),
          iOS: const DarwinNotificationDetails(
            presentAlert: true,
            presentBadge: true,
            presentSound: true,
            sound: 'levelup.aiff',
          ),
        ),
        payload: 'levelup:$newLevel',
      );
      
      debugPrint('📱 Level up notification sent: $oldLevel → $newLevel');
      
    } catch (e) {
      debugPrint('❌ Failed to show level up notification: $e');
    }
  }

  /// Show daily streak notification
  Future<void> showDailyStreakNotification({
    required int streakDays,
    required int xpReward,
    required bool isMilestone,
  }) async {
    if (!_isInitialized || !_notificationsEnabled) return;
    
    try {
      final title = isMilestone 
          ? '🔥 Streak Milestone!'
          : '📅 Daily Bonus';
      
      final body = isMilestone
          ? 'Amazing! $streakDays day streak achieved!\n+${xpReward} XP bonus'
          : 'Day $streakDays login streak\n+${xpReward} XP earned';
      
      await _localNotifications.show(
        _generateNotificationId(),
        title,
        body,
        NotificationDetails(
          android: AndroidNotificationDetails(
            _channelId,
            _channelName,
            channelDescription: _channelDescription,
            importance: isMilestone ? Importance.high : Importance.defaultImportance,
            priority: isMilestone ? Priority.high : Priority.defaultPriority,
            icon: '@mipmap/ic_launcher',
            color: isMilestone ? Colors.orange : Colors.blue,
            vibrationPattern: isMilestone
                ? Int64List.fromList([0, 150, 100, 150, 100, 300])
                : Int64List.fromList([0, 100]),
          ),
          iOS: DarwinNotificationDetails(
            presentAlert: true,
            presentBadge: true,
            presentSound: true,
            sound: isMilestone ? 'milestone.aiff' : 'default.aiff',
          ),
        ),
        payload: 'daily:$streakDays',
      );
      
      debugPrint('📱 Daily streak notification sent: $streakDays days');
      
    } catch (e) {
      debugPrint('❌ Failed to show daily streak notification: $e');
    }
  }

  /// Show trading alert notification
  Future<void> showTradingAlert({
    required String title,
    required String message,
    String? symbol,
    Color? color,
  }) async {
    if (!_isInitialized || !_notificationsEnabled) return;
    
    try {
      await _localNotifications.show(
        _generateNotificationId(),
        title,
        message,
        NotificationDetails(
          android: AndroidNotificationDetails(
            _channelId,
            _channelName,
            channelDescription: _channelDescription,
            importance: Importance.high,
            priority: Priority.high,
            icon: '@mipmap/ic_launcher',
            color: color ?? Colors.blue,
            vibrationPattern: Int64List.fromList([0, 200, 100, 200]),
          ),
          iOS: const DarwinNotificationDetails(
            presentAlert: true,
            presentBadge: true,
            presentSound: true,
          ),
        ),
        payload: 'alert:${symbol ?? 'general'}',
      );
      
      debugPrint('📱 Trading alert sent: $title');
      
    } catch (e) {
      debugPrint('❌ Failed to show trading alert: $e');
    }
  }

  /// Schedule daily reminder notification
  Future<void> scheduleDailyReminder({
    required int hour,
    required int minute,
  }) async {
    if (!_isInitialized || !_notificationsEnabled) return;
    
    try {
      // Cancel existing daily reminder
      await _localNotifications.cancel(9999);
      
      // Schedule new daily reminder
      await _localNotifications.periodicallyShow(
        9999,
        '📈 Ready to Trade?',
        'Don\'t forget to check your portfolio and make some trades today!',
        RepeatInterval.daily,
        const NotificationDetails(
          android: AndroidNotificationDetails(
            _channelId,
            _channelName,
            channelDescription: _channelDescription,
            importance: Importance.defaultImportance,
            priority: Priority.defaultPriority,
            icon: '@mipmap/ic_launcher',
          ),
          iOS: DarwinNotificationDetails(
            presentAlert: true,
            presentBadge: true,
            presentSound: true,
          ),
        ),
        payload: 'daily_reminder',
      );
      
      debugPrint('📱 Daily reminder scheduled for $hour:$minute');
      
    } catch (e) {
      debugPrint('❌ Failed to schedule daily reminder: $e');
    }
  }

  /// Enable/disable notifications
  Future<void> setNotificationsEnabled(bool enabled) async {
    _notificationsEnabled = enabled;
    await _saveSettings();
    
    if (!enabled) {
      await cancelAllNotifications();
    }
    
    debugPrint('📱 Notifications ${enabled ? 'enabled' : 'disabled'}');
  }

  /// Cancel all notifications
  Future<void> cancelAllNotifications() async {
    await _localNotifications.cancelAll();
    debugPrint('📱 All notifications cancelled');
  }

  /// Get notification settings
  Map<String, dynamic> getSettings() {
    return {
      'enabled': _notificationsEnabled,
      'initialized': _isInitialized,
    };
  }

  /// Generate unique notification ID
  int _generateNotificationId() {
    return DateTime.now().millisecondsSinceEpoch.remainder(100000);
  }

  /// Get achievement color based on rarity
  Color _getAchievementColor(AchievementRarity rarity) {
    switch (rarity) {
      case AchievementRarity.common:
        return Colors.grey;
      case AchievementRarity.uncommon:
        return Colors.green;
      case AchievementRarity.rare:
        return Colors.blue;
      case AchievementRarity.epic:
        return Colors.purple;
      case AchievementRarity.legendary:
        return Colors.orange;
    }
  }

  /// Get achievement vibration pattern based on rarity
  Int64List _getAchievementVibration(AchievementRarity rarity) {
    switch (rarity) {
      case AchievementRarity.common:
        return Int64List.fromList([0, 100]);
      case AchievementRarity.uncommon:
        return Int64List.fromList([0, 100, 50, 100]);
      case AchievementRarity.rare:
        return Int64List.fromList([0, 150, 100, 150]);
      case AchievementRarity.epic:
        return Int64List.fromList([0, 200, 100, 200, 100, 200]);
      case AchievementRarity.legendary:
        return Int64List.fromList([0, 300, 150, 300, 150, 300, 150, 500]);
    }
  }
}