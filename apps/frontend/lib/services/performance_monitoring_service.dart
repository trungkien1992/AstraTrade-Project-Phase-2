import 'dart:async';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:flutter/widgets.dart';
import '../config/app_config.dart';
import 'analytics_service.dart';

enum PerformanceMetricType {
  appStartup,
  screenLoad,
  networkRequest,
  memoryUsage,
  frameRendering,
  batteryUsage,
  diskUsage,
}

class PerformanceMetric {
  final String name;
  final PerformanceMetricType type;
  final double value;
  final String unit;
  final DateTime timestamp;
  final Map<String, dynamic> metadata;

  PerformanceMetric({
    required this.name,
    required this.type,
    required this.value,
    required this.unit,
    DateTime? timestamp,
    this.metadata = const {},
  }) : timestamp = timestamp ?? DateTime.now();

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'type': type.name,
      'value': value,
      'unit': unit,
      'timestamp': timestamp.millisecondsSinceEpoch,
      'metadata': metadata,
    };
  }
}

class PerformanceMonitoringService {
  static final PerformanceMonitoringService _instance = PerformanceMonitoringService._internal();
  factory PerformanceMonitoringService() => _instance;
  PerformanceMonitoringService._internal();

  final List<PerformanceMetric> _metrics = [];
  Timer? _memoryMonitoringTimer;
  Timer? _healthCheckTimer;
  DateTime? _appStartTime;
  DateTime? _lastFrameTime;
  int _frameCount = 0;
  int _droppedFrames = 0;

  // App lifecycle tracking
  static Future<void> initialize() async {
    final instance = PerformanceMonitoringService();
    instance._appStartTime = DateTime.now();
    
    if (AppConfig.enablePerformanceMonitoring) {
      await instance._startMonitoring();
      instance._trackAppStartup();
    }
  }

  Future<void> _startMonitoring() async {
    // Start memory monitoring
    _memoryMonitoringTimer = Timer.periodic(
      const Duration(minutes: 1),
      (_) => _trackMemoryUsage(),
    );

    // Start health check monitoring
    _healthCheckTimer = Timer.periodic(
      AppConfig.healthCheckInterval,
      (_) => _performHealthCheck(),
    );

    // Start frame rendering monitoring in debug mode
    if (kDebugMode) {
      _startFrameMonitoring();
    }
  }

  void _trackAppStartup() {
    if (_appStartTime != null) {
      final startupTime = DateTime.now().difference(_appStartTime!).inMilliseconds;
      trackMetric(PerformanceMetric(
        name: 'app_startup_time',
        type: PerformanceMetricType.appStartup,
        value: startupTime.toDouble(),
        unit: 'milliseconds',
        metadata: {
          'platform': Platform.operatingSystem,
          'is_cold_start': true,
        },
      ));
    }
  }

  // Screen loading performance
  static Future<T> trackScreenLoad<T>(
    String screenName,
    Future<T> Function() operation,
  ) async {
    final stopwatch = Stopwatch()..start();
    
    try {
      final result = await operation();
      
      stopwatch.stop();
      PerformanceMonitoringService().trackMetric(PerformanceMetric(
        name: 'screen_load_time',
        type: PerformanceMetricType.screenLoad,
        value: stopwatch.elapsedMilliseconds.toDouble(),
        unit: 'milliseconds',
        metadata: {
          'screen_name': screenName,
          'success': true,
        },
      ));
      
      return result;
    } catch (error) {
      stopwatch.stop();
      PerformanceMonitoringService().trackMetric(PerformanceMetric(
        name: 'screen_load_time',
        type: PerformanceMetricType.screenLoad,
        value: stopwatch.elapsedMilliseconds.toDouble(),
        unit: 'milliseconds',
        metadata: {
          'screen_name': screenName,
          'success': false,
          'error': error.toString(),
        },
      ));
      
      rethrow;
    }
  }

  // Network request performance
  static Future<T> trackNetworkRequest<T>(
    String endpoint,
    Future<T> Function() request,
  ) async {
    final stopwatch = Stopwatch()..start();
    
    try {
      final result = await request();
      
      stopwatch.stop();
      PerformanceMonitoringService().trackMetric(PerformanceMetric(
        name: 'network_request_time',
        type: PerformanceMetricType.networkRequest,
        value: stopwatch.elapsedMilliseconds.toDouble(),
        unit: 'milliseconds',
        metadata: {
          'endpoint': endpoint,
          'success': true,
          'method': 'GET', // Could be enhanced to track actual method
        },
      ));
      
      return result;
    } catch (error) {
      stopwatch.stop();
      PerformanceMonitoringService().trackMetric(PerformanceMetric(
        name: 'network_request_time',
        type: PerformanceMetricType.networkRequest,
        value: stopwatch.elapsedMilliseconds.toDouble(),
        unit: 'milliseconds',
        metadata: {
          'endpoint': endpoint,
          'success': false,
          'error': error.toString(),
        },
      ));
      
      rethrow;
    }
  }

  // Memory usage tracking
  Future<void> _trackMemoryUsage() async {
    try {
      // Get memory info from platform
      final MethodChannel channel = MethodChannel('com.astratrade.app/performance');
      final memoryInfo = await channel.invokeMethod('getMemoryInfo');
      
      trackMetric(PerformanceMetric(
        name: 'memory_usage',
        type: PerformanceMetricType.memoryUsage,
        value: (memoryInfo['usedMemory'] ?? 0).toDouble(),
        unit: 'bytes',
        metadata: {
          'total_memory': memoryInfo['totalMemory'] ?? 0,
          'available_memory': memoryInfo['availableMemory'] ?? 0,
          'memory_pressure': _calculateMemoryPressure(memoryInfo),
        },
      ));
    } catch (e) {
      // Fallback for platforms that don't support memory monitoring
      if (kDebugMode) {
        print('Memory monitoring not available: $e');
      }
    }
  }

  String _calculateMemoryPressure(Map<dynamic, dynamic> memoryInfo) {
    final used = memoryInfo['usedMemory'] ?? 0;
    final total = memoryInfo['totalMemory'] ?? 1;
    final percentage = (used / total) * 100;
    
    if (percentage > 90) return 'critical';
    if (percentage > 75) return 'high';
    if (percentage > 50) return 'moderate';
    return 'low';
  }

  // Frame rendering monitoring
  void _startFrameMonitoring() {
    // This would typically integrate with Flutter's frame callback
    // For production, consider using Flutter's PerformanceOverlay
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _trackFrameRendering();
    });
  }

  void _trackFrameRendering() {
    final now = DateTime.now();
    
    if (_lastFrameTime != null) {
      final frameDuration = now.difference(_lastFrameTime!).inMicroseconds;
      final targetFrameDuration = 16666; // 60 FPS = 16.67ms per frame
      
      if (frameDuration > targetFrameDuration * 1.5) {
        _droppedFrames++;
      }
      
      _frameCount++;
      
      // Report frame metrics every 60 frames
      if (_frameCount % 60 == 0) {
        trackMetric(PerformanceMetric(
          name: 'frame_rendering_performance',
          type: PerformanceMetricType.frameRendering,
          value: _droppedFrames.toDouble(),
          unit: 'dropped_frames_per_60',
          metadata: {
            'total_frames': _frameCount,
            'avg_frame_time': frameDuration.toDouble(),
            'target_frame_time': targetFrameDuration.toDouble(),
          },
        ));
        
        _droppedFrames = 0; // Reset counter
      }
    }
    
    _lastFrameTime = now;
    
    // Schedule next frame monitoring
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _trackFrameRendering();
    });
  }

  // Health check monitoring
  Future<void> _performHealthCheck() async {
    final healthMetrics = <String, dynamic>{};
    
    // Check app responsiveness
    final responseTime = await _measureAppResponseTime();
    healthMetrics['response_time_ms'] = responseTime;
    
    // Check memory status
    healthMetrics['memory_pressure'] = await _getCurrentMemoryPressure();
    
    // Check analytics service health
    healthMetrics['analytics_healthy'] = await _checkAnalyticsHealth();
    
    // Report overall health score
    final healthScore = _calculateHealthScore(healthMetrics);
    
    trackMetric(PerformanceMetric(
      name: 'app_health_score',
      type: PerformanceMetricType.appStartup,
      value: healthScore,
      unit: 'score_0_to_100',
      metadata: healthMetrics,
    ));
  }

  Future<double> _measureAppResponseTime() async {
    final stopwatch = Stopwatch()..start();
    
    // Simulate a quick operation to measure responsiveness
    await Future.delayed(const Duration(milliseconds: 1));
    
    stopwatch.stop();
    return stopwatch.elapsedMilliseconds.toDouble();
  }

  Future<String> _getCurrentMemoryPressure() async {
    try {
      final MethodChannel channel = MethodChannel('com.astratrade.app/performance');
      final memoryInfo = await channel.invokeMethod('getMemoryInfo');
      return _calculateMemoryPressure(memoryInfo);
    } catch (e) {
      return 'unknown';
    }
  }

  Future<bool> _checkAnalyticsHealth() async {
    try {
      // Try to get analytics summary as a health check
      await AnalyticsService.getAnalyticsSummary();
      return true;
    } catch (e) {
      return false;
    }
  }

  double _calculateHealthScore(Map<String, dynamic> metrics) {
    double score = 100.0;
    
    // Deduct for slow response time
    final responseTime = metrics['response_time_ms'] ?? 0;
    if (responseTime > 100) score -= 20;
    else if (responseTime > 50) score -= 10;
    
    // Deduct for memory pressure
    final memoryPressure = metrics['memory_pressure'] ?? 'low';
    switch (memoryPressure) {
      case 'critical':
        score -= 40;
        break;
      case 'high':
        score -= 20;
        break;
      case 'moderate':
        score -= 10;
        break;
    }
    
    // Deduct for analytics issues
    if (!(metrics['analytics_healthy'] ?? true)) {
      score -= 15;
    }
    
    return score.clamp(0.0, 100.0);
  }

  // Public API for tracking custom metrics
  void trackMetric(PerformanceMetric metric) {
    _metrics.add(metric);
    
    // Also send to analytics service
    AnalyticsService.trackPerformanceMetric(
      metric: metric.name,
      value: metric.value,
      unit: metric.unit,
    );
    
    // Keep only recent metrics to prevent memory bloat
    if (_metrics.length > 1000) {
      _metrics.removeRange(0, _metrics.length - 1000);
    }
    
    // Log critical performance issues
    if (_isCriticalMetric(metric)) {
      _handleCriticalPerformanceIssue(metric);
    }
  }

  bool _isCriticalMetric(PerformanceMetric metric) {
    switch (metric.type) {
      case PerformanceMetricType.appStartup:
        return metric.value > 5000; // > 5 seconds
      case PerformanceMetricType.screenLoad:
        return metric.value > 3000; // > 3 seconds
      case PerformanceMetricType.networkRequest:
        return metric.value > 10000; // > 10 seconds
      case PerformanceMetricType.memoryUsage:
        return metric.metadata['memory_pressure'] == 'critical';
      case PerformanceMetricType.frameRendering:
        return metric.value > 10; // > 10 dropped frames per 60
      default:
        return false;
    }
  }

  void _handleCriticalPerformanceIssue(PerformanceMetric metric) {
    if (kDebugMode) {
      print('🚨 Critical Performance Issue: ${metric.name} = ${metric.value} ${metric.unit}');
    }
    
    // Track as error for analytics
    AnalyticsService.trackError(
      error: 'Critical Performance Issue',
      context: 'performance_monitoring',
      stackTrace: 'Metric: ${metric.name}, Value: ${metric.value} ${metric.unit}',
    );
  }

  // Get performance summary
  Map<String, dynamic> getPerformanceSummary() {
    final now = DateTime.now();
    final last24Hours = now.subtract(const Duration(hours: 24));
    
    final recentMetrics = _metrics
        .where((m) => m.timestamp.isAfter(last24Hours))
        .toList();
    
    final metricsByType = <PerformanceMetricType, List<PerformanceMetric>>{};
    for (final metric in recentMetrics) {
      metricsByType[metric.type] ??= [];
      metricsByType[metric.type]!.add(metric);
    }
    
    final summary = <String, dynamic>{
      'total_metrics': recentMetrics.length,
      'collection_period': '24_hours',
      'app_uptime_minutes': _appStartTime != null 
          ? now.difference(_appStartTime!).inMinutes 
          : 0,
    };
    
    // Calculate averages for each metric type
    for (final entry in metricsByType.entries) {
      final metrics = entry.value;
      final avgValue = metrics.map((m) => m.value).reduce((a, b) => a + b) / metrics.length;
      final maxValue = metrics.map((m) => m.value).reduce((a, b) => a > b ? a : b);
      
      summary['${entry.key.name}_avg'] = avgValue;
      summary['${entry.key.name}_max'] = maxValue;
      summary['${entry.key.name}_count'] = metrics.length;
    }
    
    return summary;
  }

  // Cleanup
  void dispose() {
    _memoryMonitoringTimer?.cancel();
    _healthCheckTimer?.cancel();
    _metrics.clear();
  }
}