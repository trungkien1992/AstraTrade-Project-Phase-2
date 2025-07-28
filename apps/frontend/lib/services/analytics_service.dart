import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter/foundation.dart';

enum EventType {
  screen_view,
  user_action,
  conversion,
  error,
  performance,
}

class AnalyticsEvent {
  final String name;
  final EventType type;
  final Map<String, dynamic> properties;
  final DateTime timestamp;
  final String? userId;
  final String? sessionId;

  AnalyticsEvent({
    required this.name,
    required this.type,
    required this.properties,
    DateTime? timestamp,
    this.userId,
    this.sessionId,
  }) : timestamp = timestamp ?? DateTime.now();

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'type': type.name,
      'properties': properties,
      'timestamp': timestamp.millisecondsSinceEpoch,
      'user_id': userId,
      'session_id': sessionId,
    };
  }

  factory AnalyticsEvent.fromJson(Map<String, dynamic> json) {
    return AnalyticsEvent(
      name: json['name'],
      type: EventType.values.firstWhere((e) => e.name == json['type']),
      properties: Map<String, dynamic>.from(json['properties']),
      timestamp: DateTime.fromMillisecondsSinceEpoch(json['timestamp']),
      userId: json['user_id'],
      sessionId: json['session_id'],
    );
  }
}

class AnalyticsService {
  static const String _eventsKey = 'analytics_events';
  static const String _sessionKey = 'current_session_id';
  static const String _userKey = 'analytics_user_id';
  static const String _sessionStartKey = 'session_start_time';
  
  static String? _currentSessionId;
  static String? _currentUserId;
  static DateTime? _sessionStartTime;

  static Future<void> initialize() async {
    final prefs = await SharedPreferences.getInstance();
    
    // Generate or retrieve user ID
    _currentUserId = prefs.getString(_userKey);
    if (_currentUserId == null) {
      _currentUserId = _generateUniqueId();
      await prefs.setString(_userKey, _currentUserId!);
    }

    // Start new session
    await _startNewSession();
    
    // Track app open
    await trackEvent(
      name: 'app_opened',
      type: EventType.user_action,
      properties: {
        'app_version': '1.0.0',
        'platform': defaultTargetPlatform.name,
      },
    );
  }

  static Future<void> _startNewSession() async {
    final prefs = await SharedPreferences.getInstance();
    _currentSessionId = _generateUniqueId();
    _sessionStartTime = DateTime.now();
    
    await prefs.setString(_sessionKey, _currentSessionId!);
    await prefs.setInt(_sessionStartKey, _sessionStartTime!.millisecondsSinceEpoch);
  }

  static String _generateUniqueId() {
    return DateTime.now().millisecondsSinceEpoch.toString() + 
           (1000 + (DateTime.now().microsecond % 9000)).toString();
  }

  static Future<void> trackEvent({
    required String name,
    required EventType type,
    Map<String, dynamic>? properties,
  }) async {
    final event = AnalyticsEvent(
      name: name,
      type: type,
      properties: properties ?? {},
      userId: _currentUserId,
      sessionId: _currentSessionId,
    );

    await _storeEvent(event);
    
    if (kDebugMode) {
      print('📊 Analytics: ${event.name} - ${event.properties}');
    }
  }

  static Future<void> _storeEvent(AnalyticsEvent event) async {
    final prefs = await SharedPreferences.getInstance();
    final existingEvents = prefs.getStringList(_eventsKey) ?? [];
    
    existingEvents.add(jsonEncode(event.toJson()));
    
    // Keep only last 1000 events to manage storage
    if (existingEvents.length > 1000) {
      existingEvents.removeRange(0, existingEvents.length - 1000);
    }
    
    await prefs.setStringList(_eventsKey, existingEvents);
  }

  // Screen tracking
  static Future<void> trackScreenView(String screenName, {Map<String, dynamic>? properties}) async {
    await trackEvent(
      name: 'screen_view',
      type: EventType.screen_view,
      properties: {
        'screen_name': screenName,
        ...?properties,
      },
    );
  }

  // User actions
  static Future<void> trackUserAction(String action, {Map<String, dynamic>? properties}) async {
    await trackEvent(
      name: action,
      type: EventType.user_action,
      properties: properties,
    );
  }

  // Trading specific events
  static Future<void> trackTradeStarted({
    required String symbol,
    required String direction,
    required double amount,
  }) async {
    await trackEvent(
      name: 'trade_started',
      type: EventType.user_action,
      properties: {
        'symbol': symbol,
        'direction': direction,
        'amount': amount,
      },
    );
  }

  static Future<void> trackTradeCompleted({
    required String symbol,
    required String direction,
    required double amount,
    required double profitLoss,
    required double profitLossPercentage,
    required bool isProfit,
  }) async {
    await trackEvent(
      name: 'trade_completed',
      type: EventType.conversion,
      properties: {
        'symbol': symbol,
        'direction': direction,
        'amount': amount,
        'profit_loss': profitLoss,
        'profit_loss_percentage': profitLossPercentage,
        'is_profit': isProfit,
        'result': isProfit ? 'profit' : 'loss',
      },
    );
  }

  // Paywall events
  static Future<void> trackPaywallShown({
    required String trigger,
    required String variant,
  }) async {
    await trackEvent(
      name: 'paywall_shown',
      type: EventType.user_action,
      properties: {
        'trigger': trigger,
        'variant': variant,
      },
    );
  }

  static Future<void> trackPaywallConversion({
    required String variant,
    required String plan,
    required double price,
  }) async {
    await trackEvent(
      name: 'subscription_purchased',
      type: EventType.conversion,
      properties: {
        'variant': variant,
        'plan': plan,
        'price': price,
        'conversion_type': 'subscription',
      },
    );
  }

  static Future<void> trackPaywallDismissed({
    required String variant,
    required String reason,
  }) async {
    await trackEvent(
      name: 'paywall_dismissed',
      type: EventType.user_action,
      properties: {
        'variant': variant,
        'reason': reason,
      },
    );
  }

  // Onboarding events
  static Future<void> trackOnboardingStep({
    required String step,
    required int stepNumber,
    Map<String, dynamic>? stepData,
  }) async {
    await trackEvent(
      name: 'onboarding_step',
      type: EventType.user_action,
      properties: {
        'step': step,
        'step_number': stepNumber,
        ...?stepData,
      },
    );
  }

  static Future<void> trackOnboardingCompleted({
    required String experienceLevel,
    required double practiceAmount,
    required List<String> goals,
    required bool notificationsEnabled,
  }) async {
    await trackEvent(
      name: 'onboarding_completed',
      type: EventType.conversion,
      properties: {
        'experience_level': experienceLevel,
        'practice_amount': practiceAmount,
        'goals': goals,
        'notifications_enabled': notificationsEnabled,
        'conversion_type': 'onboarding',
      },
    );
  }

  // Rating events
  static Future<void> trackRatingPromptShown({
    required int totalTrades,
    required int currentStreak,
    required String trigger,
  }) async {
    await trackEvent(
      name: 'rating_prompt_shown',
      type: EventType.user_action,
      properties: {
        'total_trades': totalTrades,
        'current_streak': currentStreak,
        'trigger': trigger,
      },
    );
  }

  static Future<void> trackRatingSubmitted({
    required int rating,
    required bool wentToStore,
  }) async {
    await trackEvent(
      name: 'rating_submitted',
      type: EventType.conversion,
      properties: {
        'rating': rating,
        'went_to_store': wentToStore,
        'conversion_type': 'rating',
      },
    );
  }

  // Performance tracking
  static Future<void> trackPerformanceMetric({
    required String metric,
    required double value,
    String? unit,
  }) async {
    await trackEvent(
      name: 'performance_metric',
      type: EventType.performance,
      properties: {
        'metric': metric,
        'value': value,
        'unit': unit,
      },
    );
  }

  // Error tracking
  static Future<void> trackError({
    required String error,
    required String context,
    String? stackTrace,
  }) async {
    await trackEvent(
      name: 'error_occurred',
      type: EventType.error,
      properties: {
        'error': error,
        'context': context,
        'stack_trace': stackTrace,
      },
    );
  }

  // Data retrieval for dashboard
  static Future<List<AnalyticsEvent>> getEvents({
    EventType? type,
    DateTime? startDate,
    DateTime? endDate,
    int? limit,
  }) async {
    final prefs = await SharedPreferences.getInstance();
    final eventStrings = prefs.getStringList(_eventsKey) ?? [];
    
    List<AnalyticsEvent> events = [];
    
    for (final eventString in eventStrings) {
      try {
        final event = AnalyticsEvent.fromJson(jsonDecode(eventString));
        
        // Apply filters
        if (type != null && event.type != type) continue;
        if (startDate != null && event.timestamp.isBefore(startDate)) continue;
        if (endDate != null && event.timestamp.isAfter(endDate)) continue;
        
        events.add(event);
      } catch (e) {
        // Skip invalid events
        continue;
      }
    }
    
    // Sort by timestamp (newest first)
    events.sort((a, b) => b.timestamp.compareTo(a.timestamp));
    
    // Apply limit
    if (limit != null && events.length > limit) {
      events = events.take(limit).toList();
    }
    
    return events;
  }

  static Future<Map<String, dynamic>> getAnalyticsSummary() async {
    final events = await getEvents();
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    final week = today.subtract(const Duration(days: 7));
    
    final todaysEvents = events.where((e) => e.timestamp.isAfter(today)).length;
    final weeksEvents = events.where((e) => e.timestamp.isAfter(week)).length;
    
    final conversions = events.where((e) => e.type == EventType.conversion).length;
    final screenViews = events.where((e) => e.type == EventType.screen_view).length;
    final errors = events.where((e) => e.type == EventType.error).length;
    
    return {
      'total_events': events.length,
      'todays_events': todaysEvents,
      'weeks_events': weeksEvents,
      'conversions': conversions,
      'screen_views': screenViews,
      'errors': errors,
      'session_id': _currentSessionId,
      'user_id': _currentUserId,
      'session_duration': _sessionStartTime != null 
          ? DateTime.now().difference(_sessionStartTime!).inMinutes 
          : 0,
    };
  }

  static Future<void> endSession() async {
    if (_sessionStartTime != null) {
      final sessionDuration = DateTime.now().difference(_sessionStartTime!);
      
      await trackEvent(
        name: 'session_ended',
        type: EventType.user_action,
        properties: {
          'session_duration_minutes': sessionDuration.inMinutes,
          'session_duration_seconds': sessionDuration.inSeconds,
        },
      );
    }
  }
}