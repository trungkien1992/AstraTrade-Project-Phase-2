import 'dart:async';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:flutter_background_service/flutter_background_service.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:permission_handler/permission_handler.dart';
// import 'package:timezone/timezone.dart' as tz; // Commented out for iOS simulator testing
// import 'haptic_service.dart'; // Commented out due to unused import warning

/// Enhanced notification service for cosmic catalyst features
/// Provides local notifications and background processing for demo
class EnhancedNotificationService {
  static final _instance = EnhancedNotificationService._internal();
  factory EnhancedNotificationService() => _instance;
  EnhancedNotificationService._internal();
  
  static const String _channelId = 'cosmic_catalyst_notifications';
  static const String _channelName = 'Cosmic Catalyst';
  static const String _channelDescription = 'Notifications for cosmic trading activities';
  
  final FlutterLocalNotificationsPlugin _localNotifications = 
      FlutterLocalNotificationsPlugin();
  
  bool _isInitialized = false;
  String? _demoToken;
  
  /// Initialize notification service
  Future<bool> initialize() async {
    if (_isInitialized) return true;
    
    try {
      await _requestPermissions();
      await _initializeLocalNotifications();
      await _initializeDemoTokens();
      await _initializeBackgroundService();
      
      _isInitialized = true;
      
      if (kDebugMode) {
        print('EnhancedNotificationService: Initialized successfully');
      }
      
      return true;
    } catch (e) {
      if (kDebugMode) {
        print('EnhancedNotificationService: Failed to initialize: $e');
      }
      return false;
    }
  }
  
  /// Request necessary permissions
  Future<void> _requestPermissions() async {
    // Request notification permissions
    if (Platform.isAndroid) {
      await Permission.notification.request();
    }
    
    // Request Firebase messaging permissions - Commented out for iOS simulator testing
    // await _firebaseMessaging.requestPermission(
    //   alert: true,
    //   announcement: false,
    //   badge: true,
    //   carPlay: false,
    //   criticalAlert: false,
    //   provisional: false,
    //   sound: true,
    // );
  }
  
  /// Initialize local notifications
  Future<void> _initializeLocalNotifications() async {
    // Android initialization
    const AndroidInitializationSettings initializationSettingsAndroid =
        AndroidInitializationSettings('@mipmap/ic_launcher');
    
    // iOS initialization
    const DarwinInitializationSettings initializationSettingsIOS =
        DarwinInitializationSettings(
      requestAlertPermission: true,
      requestBadgePermission: true,
      requestSoundPermission: true,
    );
    
    const InitializationSettings initializationSettings = InitializationSettings(
      android: initializationSettingsAndroid,
      iOS: initializationSettingsIOS,
    );
    
    await _localNotifications.initialize(
      initializationSettings,
      onDidReceiveNotificationResponse: _onNotificationTapped,
    );
    
    // Create notification channel for Android
    if (Platform.isAndroid) {
      await _createNotificationChannel();
    }
  }
  
  /// Create Android notification channel
  Future<void> _createNotificationChannel() async {
    final AndroidNotificationChannel channel = AndroidNotificationChannel(
      _channelId,
      _channelName,
      description: _channelDescription,
      importance: Importance.high,
      enableVibration: true,
      enableLights: true,
      ledColor: const Color(0xFF9C27B0), // Purple cosmic color
      vibrationPattern: Int64List.fromList([0, 250, 250, 250]),
    );
    
    await _localNotifications
        .resolvePlatformSpecificImplementation<AndroidFlutterLocalNotificationsPlugin>()
        ?.createNotificationChannel(channel);
  }
  
  /// Initialize Firebase messaging - Commented out for iOS simulator testing
  // Future<void> _initializeFirebaseMessaging() async {
  //   // Get FCM token
  //   _fcmToken = await _firebaseMessaging.getToken();
  //   
  //   if (kDebugMode) {
  //     print('FCM Token: $_fcmToken');
  //   }
  //   
  //   // Handle background messages
  //   FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);
  //   
  //   // Handle foreground messages
  //   FirebaseMessaging.onMessage.listen(_handleForegroundMessage);
  //   
  //   // Handle notification taps when app is in background
  //   FirebaseMessaging.onMessageOpenedApp.listen(_handleNotificationTap);
  //   
  //   // Handle notification taps when app is terminated
  //   FirebaseMessaging.instance.getInitialMessage().then((RemoteMessage? message) {
  //     if (message != null) {
  //       _handleNotificationTap(message);
  //     }
  //   });
  //   
  //   // Listen for token refreshes
  //   FirebaseMessaging.instance.onTokenRefresh.listen((String token) {
  //     _fcmToken = token;
  //     _sendTokenToServer(token);
  //   });
  //   
  //   // Send initial token to server
  //   if (_fcmToken != null) {
  //     _sendTokenToServer(_fcmToken!);
  //   }
  // }

  /// Initialize demo tokens for local testing
  Future<void> _initializeDemoTokens() async {
    // Demo implementation for iOS simulator testing
    _demoToken = 'demo_token_${DateTime.now().millisecondsSinceEpoch}';
    
    if (kDebugMode) {
      print('Demo Notification Token: $_demoToken');
    }
    
    // Send demo token to server
    if (_demoToken != null) {
      _sendTokenToServer(_demoToken!);
    }
  }
  
  /// Initialize background service for idle processing
  Future<void> _initializeBackgroundService() async {
    final service = FlutterBackgroundService();
    await service.configure(
      androidConfiguration: AndroidConfiguration(
        onStart: _backgroundServiceStart,
        autoStart: true,
        isForegroundMode: false,
        notificationChannelId: _channelId,
        initialNotificationTitle: 'Cosmic Catalyst',
        initialNotificationContent: 'Generating stellar energy...',
        foregroundServiceNotificationId: 888,
      ),
      iosConfiguration: IosConfiguration(
        autoStart: true,
        onForeground: _backgroundServiceStart,
        onBackground: _backgroundServiceStart,
      ),
    );
  }
  
  /// Background service entry point
  static Future<bool> _backgroundServiceStart(ServiceInstance service) async {
    // Initialize background processing
    Timer.periodic(const Duration(minutes: 5), (timer) async {
      await _processBackgroundIdleGeneration();
      await _checkStreakReminders();
      await _processQuantumAnomalies();
    });
    return true;
  }
  
  /// Process idle generation in background
  static Future<void> _processBackgroundIdleGeneration() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final lastProcessTime = prefs.getInt('last_idle_process') ?? 0;
      final currentTime = DateTime.now().millisecondsSinceEpoch;
      
      if (currentTime - lastProcessTime > 300000) { // 5 minutes
        // Calculate idle generation
        final stellarShardsGenerated = _calculateIdleGeneration();
        
        // Update stored values
        final currentSS = prefs.getDouble('stellar_shards') ?? 0.0;
        await prefs.setDouble('stellar_shards', currentSS + stellarShardsGenerated);
        await prefs.setInt('last_idle_process', currentTime);
        
        // Show notification if significant generation
        if (stellarShardsGenerated > 10) {
          await _showIdleGenerationNotification(stellarShardsGenerated);
        }
      }
    } catch (e) {
      if (kDebugMode) {
        print('Background idle generation failed: $e');
      }
    }
  }
  
  /// Calculate idle generation based on user's astro-forgers
  static double _calculateIdleGeneration() {
    // Simplified calculation - in real app, this would be based on user's upgrades
    return 1.0; // Base rate per 5 minutes
  }
  
  /// Show idle generation notification
  static Future<void> _showIdleGenerationNotification(double amount) async {
    final localNotifications = FlutterLocalNotificationsPlugin();
    
    const AndroidNotificationDetails androidDetails = AndroidNotificationDetails(
      _channelId,
      _channelName,
      channelDescription: _channelDescription,
      importance: Importance.low,
      priority: Priority.low,
      icon: '@mipmap/ic_launcher',
      color: Color(0xFF9C27B0),
    );
    
    const NotificationDetails platformDetails = NotificationDetails(
      android: androidDetails,
      iOS: DarwinNotificationDetails(
        presentAlert: true,
        presentBadge: true,
        presentSound: false,
      ),
    );
    
    await localNotifications.show(
      1,
      'Stellar Shards Generated! ⭐',
      'Your Astro-Forgers generated ${amount.toStringAsFixed(1)} Stellar Shards',
      platformDetails,
      payload: 'idle_generation',
    );
  }
  
  /// Check and send streak reminders
  static Future<void> _checkStreakReminders() async {
    final prefs = await SharedPreferences.getInstance();
    final lastLoginTime = prefs.getInt('last_login_time') ?? 0;
    final currentTime = DateTime.now().millisecondsSinceEpoch;
    
    // Check if 20 hours have passed since last login
    if (currentTime - lastLoginTime > 72000000) { // 20 hours
      await _showStreakReminderNotification();
    }
  }
  
  /// Show streak reminder notification
  static Future<void> _showStreakReminderNotification() async {
    final localNotifications = FlutterLocalNotificationsPlugin();
    
    final AndroidNotificationDetails androidDetails = AndroidNotificationDetails(
      _channelId,
      _channelName,
      channelDescription: _channelDescription,
      importance: Importance.high,
      priority: Priority.high,
      icon: '@mipmap/ic_launcher',
      color: const Color(0xFF9C27B0),
      enableVibration: true,
      vibrationPattern: Int64List.fromList([0, 250, 250, 250]),
    );
    
    final NotificationDetails platformDetails = NotificationDetails(
      android: androidDetails,
      iOS: const DarwinNotificationDetails(
        presentAlert: true,
        presentBadge: true,
        presentSound: true,
      ),
    );
    
    await localNotifications.show(
      2,
      'Maintain Your Cosmic Streak! 🔥',
      'Your stellar energy is waiting. Login to maintain your streak bonus!',
      platformDetails,
      payload: 'streak_reminder',
    );
  }
  
  /// Process quantum anomalies (time-limited events)
  static Future<void> _processQuantumAnomalies() async {
    // Check for active quantum anomalies
    final prefs = await SharedPreferences.getInstance();
    final anomalyEndTime = prefs.getInt('quantum_anomaly_end') ?? 0;
    final currentTime = DateTime.now().millisecondsSinceEpoch;
    
    if (anomalyEndTime > currentTime) {
      final remainingMinutes = (anomalyEndTime - currentTime) ~/ 60000;
      
      if (remainingMinutes <= 5) {
        await _showQuantumAnomalyEndingNotification(remainingMinutes);
      }
    }
  }
  
  /// Show quantum anomaly ending notification
  static Future<void> _showQuantumAnomalyEndingNotification(int remainingMinutes) async {
    final localNotifications = FlutterLocalNotificationsPlugin();
    
    final AndroidNotificationDetails androidDetails = AndroidNotificationDetails(
      _channelId,
      _channelName,
      channelDescription: _channelDescription,
      importance: Importance.high,
      priority: Priority.high,
      icon: '@mipmap/ic_launcher',
      color: const Color(0xFF9C27B0),
      enableVibration: true,
      vibrationPattern: Int64List.fromList([0, 500, 200, 500]),
    );
    
    final NotificationDetails platformDetails = NotificationDetails(
      android: androidDetails,
      iOS: const DarwinNotificationDetails(
        presentAlert: true,
        presentBadge: true,
        presentSound: true,
      ),
    );
    
    await localNotifications.show(
      3,
      'Quantum Anomaly Ending! ⚡',
      'Only $remainingMinutes minutes left! Harvest maximum Lumina now!',
      platformDetails,
      payload: 'quantum_anomaly_ending',
    );
  }
  
  /// Handle Firebase background messages - Commented out for iOS simulator testing
  // static Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  //   if (kDebugMode) {
  //     print('Background message received: ${message.messageId}');
  //   }
  //   
  //   // Trigger haptic feedback
  //   await HapticService.triggerNotificationFeedback();
  // }

  // Placeholder for Firebase background message handler removed for iOS simulator testing
  
  /// Handle foreground messages - Commented out for iOS simulator testing
  // Future<void> _handleForegroundMessage(RemoteMessage message) async {
  //   if (kDebugMode) {
  //     print('Foreground message received: ${message.messageId}');
  //   }
  //   
  //   // Show local notification for foreground message
  //   await _showLocalNotification(
  //     title: message.notification?.title ?? 'Cosmic Catalyst',
  //     body: message.notification?.body ?? 'New cosmic event!',
  //     payload: message.data['type'] ?? 'general',
  //   );
  //   
  //   // Trigger haptic feedback
  //   await HapticService.triggerNotificationFeedback();
  // }

  // Placeholder for handling foreground messages removed for iOS simulator testing
  
  /// Handle notification taps - Commented out for iOS simulator testing
  // Future<void> _handleNotificationTap(RemoteMessage message) async {
  //   if (kDebugMode) {
  //     print('Notification tapped: ${message.messageId}');
  //   }
  //   
  //   // Navigate to appropriate screen based on notification type
  //   final notificationType = message.data['type'] ?? 'general';
  //   await _navigateToScreen(notificationType);
  // }

  // Placeholder for handling notification taps removed for iOS simulator testing
  
  /// Handle local notification taps
  Future<void> _onNotificationTapped(NotificationResponse response) async {
    if (kDebugMode) {
      print('Local notification tapped: ${response.payload}');
    }
    
    await _navigateToScreen(response.payload ?? 'general');
  }
  
  /// Navigate to appropriate screen
  Future<void> _navigateToScreen(String type) async {
    // This would be implemented with your navigation system
    switch (type) {
      case 'idle_generation':
        // Navigate to main hub
        break;
      case 'streak_reminder':
        // Navigate to daily rewards
        break;
      case 'quantum_anomaly_ending':
        // Navigate to quantum anomaly screen
        break;
      case 'trade_complete':
        // Navigate to trade history
        break;
      default:
        // Navigate to main screen
        break;
    }
  }
  
  // _showLocalNotification method removed as it was unused after Firebase removal
  
  /// Send FCM token to server
  Future<void> _sendTokenToServer(String token) async {
    // Implement API call to send token to your backend
    if (kDebugMode) {
      print('Sending FCM token to server: $token');
    }
  }
  
  /// Schedule streak reminder
  Future<void> scheduleStreakReminder() async {
    // Simplified to use show instead of zonedSchedule for iOS simulator testing
    await _localNotifications.show(
      100,
      'Maintain Your Cosmic Streak! 🔥',
      'Your stellar energy is waiting. Login to maintain your streak bonus!',
      const NotificationDetails(
        android: AndroidNotificationDetails(
          _channelId,
          _channelName,
          channelDescription: _channelDescription,
          importance: Importance.high,
          priority: Priority.high,
          icon: '@mipmap/ic_launcher',
          color: Color(0xFF9C27B0),
        ),
        iOS: DarwinNotificationDetails(
          presentAlert: true,
          presentBadge: true,
          presentSound: true,
        ),
      ),
    );
  }
  
  /// Schedule quantum anomaly notification
  Future<void> scheduleQuantumAnomalyNotification(DateTime endTime) async {
    // Simplified to use show instead of zonedSchedule for iOS simulator testing
    await _localNotifications.show(
      101,
      'Quantum Anomaly Ending! ⚡',
      'Only 5 minutes left! Harvest maximum Lumina now!',
      NotificationDetails(
        android: AndroidNotificationDetails(
          _channelId,
          _channelName,
          channelDescription: _channelDescription,
          importance: Importance.high,
          priority: Priority.high,
          icon: '@mipmap/ic_launcher',
          color: const Color(0xFF9C27B0),
          enableVibration: true,
          vibrationPattern: Int64List.fromList([0, 500, 200, 500]),
        ),
        iOS: const DarwinNotificationDetails(
          presentAlert: true,
          presentBadge: true,
          presentSound: true,
        ),
      ),
    );
  }
  
  /// Cancel all notifications
  Future<void> cancelAllNotifications() async {
    await _localNotifications.cancelAll();
  }
  
  /// Cancel specific notification
  Future<void> cancelNotification(int id) async {
    await _localNotifications.cancel(id);
  }
  
  /// Get demo token
  String? get demoToken => _demoToken;
  
  /// Check if service is initialized
  bool get isInitialized => _isInitialized;
}