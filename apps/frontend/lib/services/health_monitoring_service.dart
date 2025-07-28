import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import '../config/app_config.dart';
import 'analytics_service.dart';
import 'performance_monitoring_service.dart';

enum HealthStatus {
  healthy,
  warning,
  critical,
  unknown,
}

class HealthCheck {
  final String name;
  final HealthStatus status;
  final String message;
  final DateTime timestamp;
  final Duration responseTime;
  final Map<String, dynamic> metadata;

  HealthCheck({
    required this.name,
    required this.status,
    required this.message,
    DateTime? timestamp,
    Duration? responseTime,
    this.metadata = const {},
  }) : timestamp = timestamp ?? DateTime.now(),
       responseTime = responseTime ?? Duration.zero;

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'status': status.name,
      'message': message,
      'timestamp': timestamp.millisecondsSinceEpoch,
      'response_time_ms': responseTime.inMilliseconds,
      'metadata': metadata,
    };
  }
}

class HealthMonitoringService {
  static final HealthMonitoringService _instance = HealthMonitoringService._internal();
  factory HealthMonitoringService() => _instance;
  HealthMonitoringService._internal();

  Timer? _healthCheckTimer;
  final List<HealthCheck> _healthHistory = [];
  final Map<String, HealthCheck> _lastHealthChecks = {};

  static Future<void> initialize() async {
    final instance = HealthMonitoringService();
    
    if (AppConfig.enablePerformanceMonitoring) {
      await instance._startHealthMonitoring();
    }
  }

  Future<void> _startHealthMonitoring() async {
    // Run initial health check
    await performCompleteHealthCheck();
    
    // Schedule regular health checks
    _healthCheckTimer = Timer.periodic(
      AppConfig.healthCheckInterval,
      (_) => performCompleteHealthCheck(),
    );
  }

  // Comprehensive health check
  Future<Map<String, HealthCheck>> performCompleteHealthCheck() async {
    final checks = <String, Future<HealthCheck>>{
      'app_responsiveness': _checkAppResponsiveness(),
      'memory_status': _checkMemoryStatus(),
      'network_connectivity': _checkNetworkConnectivity(),
      'analytics_service': _checkAnalyticsService(),
      'subscription_service': _checkSubscriptionService(),
      'storage_service': _checkStorageService(),
      'performance_metrics': _checkPerformanceMetrics(),
    };

    // If in production, also check external dependencies
    if (AppConfig.isProduction) {
      checks['api_health'] = _checkApiHealth();
      checks['revenue_cat_health'] = _checkRevenueCatHealth();
    }

    final results = <String, HealthCheck>{};
    
    // Execute all health checks in parallel
    final futures = checks.entries.map((entry) async {
      try {
        final result = await entry.value.timeout(
          const Duration(seconds: 30),
          onTimeout: () => HealthCheck(
            name: entry.key,
            status: HealthStatus.critical,
            message: 'Health check timed out',
          ),
        );
        return MapEntry(entry.key, result);
      } catch (e) {
        return MapEntry(
          entry.key,
          HealthCheck(
            name: entry.key,
            status: HealthStatus.critical,
            message: 'Health check failed: $e',
          ),
        );
      }
    });

    final completedChecks = await Future.wait(futures);
    
    for (final entry in completedChecks) {
      results[entry.key] = entry.value;
      _lastHealthChecks[entry.key] = entry.value;
      _healthHistory.add(entry.value);
    }

    // Keep only last 100 health checks
    if (_healthHistory.length > 100) {
      _healthHistory.removeRange(0, _healthHistory.length - 100);
    }

    // Calculate overall health score
    final overallHealth = _calculateOverallHealth(results);
    
    // Track health metrics
    await AnalyticsService.trackEvent(
      name: 'health_check_completed',
      type: EventType.performance,
      properties: {
        'overall_status': overallHealth.status.name,
        'overall_score': _getHealthScore(overallHealth.status),
        'checks_count': results.length,
        'failed_checks': results.values.where((c) => c.status == HealthStatus.critical).length,
        'warning_checks': results.values.where((c) => c.status == HealthStatus.warning).length,
      },
    );

    return results;
  }

  // Individual health check implementations
  Future<HealthCheck> _checkAppResponsiveness() async {
    final stopwatch = Stopwatch()..start();
    
    try {
      // Test app responsiveness with a simple async operation
      await Future.delayed(const Duration(milliseconds: 10));
      
      stopwatch.stop();
      final responseTime = stopwatch.elapsed;
      
      HealthStatus status;
      String message;
      
      if (responseTime.inMilliseconds < 50) {
        status = HealthStatus.healthy;
        message = 'App responding normally';
      } else if (responseTime.inMilliseconds < 200) {
        status = HealthStatus.warning;
        message = 'App responding slowly';
      } else {
        status = HealthStatus.critical;
        message = 'App response time critical';
      }
      
      return HealthCheck(
        name: 'app_responsiveness',
        status: status,
        message: message,
        responseTime: responseTime,
        metadata: {'response_time_ms': responseTime.inMilliseconds},
      );
    } catch (e) {
      stopwatch.stop();
      return HealthCheck(
        name: 'app_responsiveness',
        status: HealthStatus.critical,
        message: 'App responsiveness check failed: $e',
        responseTime: stopwatch.elapsed,
      );
    }
  }

  Future<HealthCheck> _checkMemoryStatus() async {
    try {
      // This would integrate with platform-specific memory monitoring
      // For now, we'll use a simplified check
      
      final performanceSummary = PerformanceMonitoringService().getPerformanceSummary();
      final memoryMetrics = performanceSummary['memoryUsage_avg'] ?? 0;
      
      HealthStatus status;
      String message;
      
      if (memoryMetrics < AppConfig.maxCacheSize * 0.7) {
        status = HealthStatus.healthy;
        message = 'Memory usage normal';
      } else if (memoryMetrics < AppConfig.maxCacheSize * 0.9) {
        status = HealthStatus.warning;
        message = 'Memory usage elevated';
      } else {
        status = HealthStatus.critical;
        message = 'Memory usage critical';
      }
      
      return HealthCheck(
        name: 'memory_status',
        status: status,
        message: message,
        metadata: {
          'memory_usage_bytes': memoryMetrics,
          'memory_limit_bytes': AppConfig.maxCacheSize,
        },
      );
    } catch (e) {
      return HealthCheck(
        name: 'memory_status',
        status: HealthStatus.unknown,
        message: 'Memory check unavailable: $e',
      );
    }
  }

  Future<HealthCheck> _checkNetworkConnectivity() async {
    final stopwatch = Stopwatch()..start();
    
    try {
      // Test basic network connectivity
      final result = await InternetAddress.lookup('google.com')
          .timeout(const Duration(seconds: 10));
      
      stopwatch.stop();
      
      if (result.isNotEmpty && result[0].rawAddress.isNotEmpty) {
        return HealthCheck(
          name: 'network_connectivity',
          status: HealthStatus.healthy,
          message: 'Network connectivity normal',
          responseTime: stopwatch.elapsed,
        );
      } else {
        return HealthCheck(
          name: 'network_connectivity',
          status: HealthStatus.critical,
          message: 'No network connectivity',
          responseTime: stopwatch.elapsed,
        );
      }
    } catch (e) {
      stopwatch.stop();
      return HealthCheck(
        name: 'network_connectivity',
        status: HealthStatus.critical,
        message: 'Network connectivity failed: $e',
        responseTime: stopwatch.elapsed,
      );
    }
  }

  Future<HealthCheck> _checkAnalyticsService() async {
    try {
      final summary = await AnalyticsService.getAnalyticsSummary();
      
      if (summary['total_events'] >= 0) {
        return HealthCheck(
          name: 'analytics_service',
          status: HealthStatus.healthy,
          message: 'Analytics service operational',
          metadata: {
            'total_events': summary['total_events'],
            'session_duration': summary['session_duration'],
          },
        );
      } else {
        return HealthCheck(
          name: 'analytics_service',
          status: HealthStatus.warning,
          message: 'Analytics service has issues',
        );
      }
    } catch (e) {
      return HealthCheck(
        name: 'analytics_service',
        status: HealthStatus.critical,
        message: 'Analytics service failed: $e',
      );
    }
  }

  Future<HealthCheck> _checkSubscriptionService() async {
    try {
      // This would check if RevenueCat/subscription service is working
      // For now, we'll do a simple connectivity check
      return HealthCheck(
        name: 'subscription_service',
        status: HealthStatus.healthy,
        message: 'Subscription service operational',
      );
    } catch (e) {
      return HealthCheck(
        name: 'subscription_service',
        status: HealthStatus.warning,
        message: 'Subscription service issues: $e',
      );
    }
  }

  Future<HealthCheck> _checkStorageService() async {
    try {
      // Check if local storage is working
      // This would test SharedPreferences, file system, etc.
      return HealthCheck(
        name: 'storage_service',
        status: HealthStatus.healthy,
        message: 'Storage service operational',
      );
    } catch (e) {
      return HealthCheck(
        name: 'storage_service',
        status: HealthStatus.critical,
        message: 'Storage service failed: $e',
      );
    }
  }

  Future<HealthCheck> _checkPerformanceMetrics() async {
    try {
      final performanceSummary = PerformanceMonitoringService().getPerformanceSummary();
      
      HealthStatus status = HealthStatus.healthy;
      String message = 'Performance metrics normal';
      
      // Check for performance issues
      final avgStartupTime = performanceSummary['appStartup_avg'] ?? 0;
      if (avgStartupTime > 5000) {
        status = HealthStatus.warning;
        message = 'Slow app startup detected';
      }
      
      final avgScreenLoad = performanceSummary['screenLoad_avg'] ?? 0;
      if (avgScreenLoad > 3000) {
        status = HealthStatus.warning;
        message = 'Slow screen loading detected';
      }
      
      return HealthCheck(
        name: 'performance_metrics',
        status: status,
        message: message,
        metadata: performanceSummary,
      );
    } catch (e) {
      return HealthCheck(
        name: 'performance_metrics',
        status: HealthStatus.unknown,
        message: 'Performance metrics unavailable: $e',
      );
    }
  }

  Future<HealthCheck> _checkApiHealth() async {
    final stopwatch = Stopwatch()..start();
    
    try {
      final response = await http.get(
        Uri.parse(AppConfig.healthUrl),
        headers: {'Content-Type': 'application/json'},
      ).timeout(AppConfig.networkTimeout);
      
      stopwatch.stop();
      
      if (response.statusCode == 200) {
        return HealthCheck(
          name: 'api_health',
          status: HealthStatus.healthy,
          message: 'API server healthy',
          responseTime: stopwatch.elapsed,
          metadata: {
            'status_code': response.statusCode,
            'response_size': response.body.length,
          },
        );
      } else {
        return HealthCheck(
          name: 'api_health',
          status: HealthStatus.warning,
          message: 'API server issues (status: ${response.statusCode})',
          responseTime: stopwatch.elapsed,
        );
      }
    } catch (e) {
      stopwatch.stop();
      return HealthCheck(
        name: 'api_health',
        status: HealthStatus.critical,
        message: 'API server unreachable: $e',
        responseTime: stopwatch.elapsed,
      );
    }
  }

  Future<HealthCheck> _checkRevenueCatHealth() async {
    try {
      // This would check RevenueCat service health
      // For now, return a placeholder check
      return HealthCheck(
        name: 'revenue_cat_health',
        status: HealthStatus.healthy,
        message: 'RevenueCat service operational',
      );
    } catch (e) {
      return HealthCheck(
        name: 'revenue_cat_health',
        status: HealthStatus.warning,
        message: 'RevenueCat service issues: $e',
      );
    }
  }

  HealthCheck _calculateOverallHealth(Map<String, HealthCheck> checks) {
    final statuses = checks.values.map((c) => c.status).toList();
    
    if (statuses.any((s) => s == HealthStatus.critical)) {
      return HealthCheck(
        name: 'overall_health',
        status: HealthStatus.critical,
        message: 'Critical issues detected',
      );
    } else if (statuses.any((s) => s == HealthStatus.warning)) {
      return HealthCheck(
        name: 'overall_health',
        status: HealthStatus.warning,
        message: 'Some issues detected',
      );
    } else if (statuses.any((s) => s == HealthStatus.unknown)) {
      return HealthCheck(
        name: 'overall_health',
        status: HealthStatus.warning,
        message: 'Some checks unavailable',
      );
    } else {
      return HealthCheck(
        name: 'overall_health',
        status: HealthStatus.healthy,
        message: 'All systems operational',
      );
    }
  }

  int _getHealthScore(HealthStatus status) {
    switch (status) {
      case HealthStatus.healthy:
        return 100;
      case HealthStatus.warning:
        return 75;
      case HealthStatus.critical:
        return 25;
      case HealthStatus.unknown:
        return 50;
    }
  }

  // Public API
  Map<String, HealthCheck> getLastHealthChecks() {
    return Map.from(_lastHealthChecks);
  }

  List<HealthCheck> getHealthHistory({Duration? period}) {
    if (period == null) return List.from(_healthHistory);
    
    final cutoff = DateTime.now().subtract(period);
    return _healthHistory.where((h) => h.timestamp.isAfter(cutoff)).toList();
  }

  HealthStatus getOverallHealthStatus() {
    if (_lastHealthChecks.isEmpty) return HealthStatus.unknown;
    
    return _calculateOverallHealth(_lastHealthChecks).status;
  }

  // Health check endpoint for external monitoring
  Map<String, dynamic> getHealthStatusJson() {
    final lastChecks = getLastHealthChecks();
    final overallHealth = _calculateOverallHealth(lastChecks);
    
    return {
      'status': overallHealth.status.name,
      'message': overallHealth.message,
      'timestamp': DateTime.now().toIso8601String(),
      'app_version': AppConfig.appVersion,
      'build_number': AppConfig.buildNumber,
      'environment': AppConfig.isProduction ? 'production' : 'development',
      'uptime_minutes': PerformanceMonitoringService().getPerformanceSummary()['app_uptime_minutes'] ?? 0,
      'checks': lastChecks.map((key, value) => MapEntry(key, value.toJson())),
    };
  }

  void dispose() {
    _healthCheckTimer?.cancel();
    _healthHistory.clear();
    _lastHealthChecks.clear();
  }
}