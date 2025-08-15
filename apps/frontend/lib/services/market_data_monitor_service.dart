import 'dart:async';
import 'dart:math';
import 'package:flutter/foundation.dart';
import 'extended_exchange_websocket_service.dart';
import 'price_aggregation_service.dart';
import 'market_data_cache_service.dart';
import '../data/extended_exchange_trading_pairs.dart';

/// Market Data Quality Monitor Service
///
/// Provides comprehensive monitoring for:
/// - Data quality validation
/// - Connection health monitoring
/// - Performance metrics tracking
/// - Automatic reconnection management
/// - Alert system for anomalies
class MarketDataMonitorService {
  static const int _healthCheckIntervalMs = 30 * 1000; // 30 seconds
  static const int _qualityCheckIntervalMs = 60 * 1000; // 60 seconds
  static const int _metricsUpdateIntervalMs = 5 * 1000; // 5 seconds

  // Thresholds for quality checks
  static const double _maxPriceDeviationPercent = 20.0; // 20% price deviation
  static const int _maxDataAgeMs = 60 * 1000; // 60 seconds max data age
  static const double _minConnectionUptimePercent =
      95.0; // 95% uptime requirement
  static const int _maxConsecutiveErrors = 5; // Maximum consecutive errors

  // Services to monitor
  final ExtendedExchangeWebSocketService _webSocketService;
  final PriceAggregationService _aggregationService;
  final MarketDataCacheService _cacheService;

  // Monitoring state
  bool _isMonitoring = false;
  Timer? _healthTimer;
  Timer? _qualityTimer;
  Timer? _metricsTimer;

  // Health metrics
  DateTime? _monitoringStartTime;
  int _totalHealthChecks = 0;
  int _failedHealthChecks = 0;
  int _consecutiveErrors = 0;
  DateTime? _lastHealthCheck;

  // Quality metrics
  final Map<String, QualityMetrics> _symbolQuality = {};
  final List<DataAnomalyReport> _anomalies = [];
  int _totalQualityChecks = 0;
  int _failedQualityChecks = 0;

  // Performance metrics
  final List<double> _latencyHistory = [];
  final Map<String, int> _updateCounts = {};
  DateTime? _lastMetricsReset;

  // Stream controllers for monitoring events
  final StreamController<HealthReport> _healthController =
      StreamController<HealthReport>.broadcast();
  final StreamController<QualityReport> _qualityController =
      StreamController<QualityReport>.broadcast();
  final StreamController<DataAnomalyReport> _anomalyController =
      StreamController<DataAnomalyReport>.broadcast();
  final StreamController<PerformanceMetrics> _metricsController =
      StreamController<PerformanceMetrics>.broadcast();

  MarketDataMonitorService({
    required ExtendedExchangeWebSocketService webSocketService,
    required PriceAggregationService aggregationService,
    required MarketDataCacheService cacheService,
  }) : _webSocketService = webSocketService,
       _aggregationService = aggregationService,
       _cacheService = cacheService;

  /// Health monitoring stream
  Stream<HealthReport> get healthStream => _healthController.stream;

  /// Quality monitoring stream
  Stream<QualityReport> get qualityStream => _qualityController.stream;

  /// Anomaly detection stream
  Stream<DataAnomalyReport> get anomalyStream => _anomalyController.stream;

  /// Performance metrics stream
  Stream<PerformanceMetrics> get metricsStream => _metricsController.stream;

  /// Start monitoring services
  void startMonitoring() {
    if (_isMonitoring) return;

    debugPrint('🔍 Starting Market Data Monitor Service');
    _isMonitoring = true;
    _monitoringStartTime = DateTime.now();
    _lastMetricsReset = DateTime.now();

    // Start health check timer
    _healthTimer = Timer.periodic(
      Duration(milliseconds: _healthCheckIntervalMs),
      (_) => _performHealthCheck(),
    );

    // Start quality check timer
    _qualityTimer = Timer.periodic(
      Duration(milliseconds: _qualityCheckIntervalMs),
      (_) => _performQualityCheck(),
    );

    // Start metrics update timer
    _metricsTimer = Timer.periodic(
      Duration(milliseconds: _metricsUpdateIntervalMs),
      (_) => _updateMetrics(),
    );

    debugPrint('✅ Market Data Monitor Service started');
  }

  /// Stop monitoring services
  void stopMonitoring() {
    if (!_isMonitoring) return;

    debugPrint('⏹️ Stopping Market Data Monitor Service');
    _isMonitoring = false;

    _healthTimer?.cancel();
    _qualityTimer?.cancel();
    _metricsTimer?.cancel();

    _healthTimer = null;
    _qualityTimer = null;
    _metricsTimer = null;

    debugPrint('✅ Market Data Monitor Service stopped');
  }

  /// Get current health report
  HealthReport get currentHealthReport => _generateHealthReport();

  /// Get current quality report
  QualityReport get currentQualityReport => _generateQualityReport();

  /// Get current performance metrics
  PerformanceMetrics get currentPerformanceMetrics =>
      _generatePerformanceMetrics();

  /// Get recent anomalies
  List<DataAnomalyReport> get recentAnomalies => _anomalies
      .where(
        (anomaly) => DateTime.now().difference(anomaly.timestamp).inHours < 24,
      )
      .toList();

  /// Force health check
  Future<HealthReport> performHealthCheck() async {
    return await _performHealthCheck();
  }

  /// Force quality check
  Future<QualityReport> performQualityCheck() async {
    return await _performQualityCheck();
  }

  /// Reset metrics
  void resetMetrics() {
    _latencyHistory.clear();
    _updateCounts.clear();
    _anomalies.clear();
    _symbolQuality.clear();
    _lastMetricsReset = DateTime.now();
    _totalHealthChecks = 0;
    _failedHealthChecks = 0;
    _totalQualityChecks = 0;
    _failedQualityChecks = 0;
    _consecutiveErrors = 0;

    debugPrint('🔄 Monitor metrics reset');
  }

  /// Perform health check on all services
  Future<HealthReport> _performHealthCheck() async {
    try {
      _totalHealthChecks++;
      _lastHealthCheck = DateTime.now();

      // Check WebSocket connection
      final wsState = _webSocketService.currentState;
      final wsHealthy = wsState.isConnected;
      final wsStats = _webSocketService.connectionStats;

      // Check aggregation service
      final aggStats = _aggregationService.currentStatistics;
      final aggHealthy =
          aggStats['total_symbols'] > 0 && aggStats['last_update'] != null;

      // Check cache service
      final cacheStats = _cacheService.cacheStats;
      final cacheHealthy =
          cacheStats['hit_ratio'] >= 0.0 &&
          cacheStats['memory_cache_size'] >= 0;

      // Overall health assessment
      final overallHealthy = wsHealthy && aggHealthy && cacheHealthy;

      if (!overallHealthy) {
        _failedHealthChecks++;
        _consecutiveErrors++;
      } else {
        _consecutiveErrors = 0;
      }

      // Check if automatic reconnection is needed
      if (_consecutiveErrors >= _maxConsecutiveErrors && wsState.hasError) {
        debugPrint('🚨 Too many consecutive errors, triggering reconnection');
        unawaited(_webSocketService.connect());
      }

      final report = HealthReport(
        timestamp: _lastHealthCheck!,
        isHealthy: overallHealthy,
        webSocketHealthy: wsHealthy,
        aggregationHealthy: aggHealthy,
        cacheHealthy: cacheHealthy,
        connectionState: wsState,
        uptime: _monitoringStartTime != null
            ? DateTime.now().difference(_monitoringStartTime!).inSeconds
            : 0,
        uptimePercent: _calculateUptimePercent(),
        consecutiveErrors: _consecutiveErrors,
        details: {
          'websocket_stats': wsStats,
          'aggregation_stats': aggStats,
          'cache_stats': cacheStats,
        },
      );

      _healthController.add(report);
      return report;
    } catch (e) {
      debugPrint('💥 Error in health check: $e');
      _failedHealthChecks++;
      _consecutiveErrors++;

      final errorReport = HealthReport(
        timestamp: DateTime.now(),
        isHealthy: false,
        webSocketHealthy: false,
        aggregationHealthy: false,
        cacheHealthy: false,
        connectionState: WebSocketConnectionState.error,
        uptime: 0,
        uptimePercent: 0.0,
        consecutiveErrors: _consecutiveErrors,
        details: {'error': e.toString()},
      );

      _healthController.add(errorReport);
      return errorReport;
    }
  }

  /// Perform quality check on data
  Future<QualityReport> _performQualityCheck() async {
    try {
      _totalQualityChecks++;
      final now = DateTime.now();

      int healthySymbols = 0;
      int staleSymbols = 0;
      int anomalousSymbols = 0;
      final List<String> issues = [];

      // Check all active trading pairs
      final allSymbols = ExtendedExchangeTradingPairs.getAllSymbols();

      for (final symbol in allSymbols) {
        final priceData = _aggregationService.getPriceData(symbol);

        if (priceData == null) {
          staleSymbols++;
          issues.add('No data for $symbol');
          continue;
        }

        // Check data freshness
        final dataAge = now.difference(priceData.lastUpdate).inMilliseconds;
        if (dataAge > _maxDataAgeMs) {
          staleSymbols++;
          issues.add('Stale data for $symbol (${dataAge}ms old)');
          continue;
        }

        // Check for price anomalies
        if (_detectPriceAnomaly(symbol, priceData)) {
          anomalousSymbols++;
          continue;
        }

        healthySymbols++;

        // Update quality metrics for symbol
        _updateSymbolQuality(symbol, priceData, now);
      }

      final qualityScore = healthySymbols / allSymbols.length * 100;
      final isQualityGood = qualityScore >= 80.0; // 80% threshold

      if (!isQualityGood) {
        _failedQualityChecks++;
      }

      final report = QualityReport(
        timestamp: now,
        qualityScore: qualityScore,
        isQualityGood: isQualityGood,
        totalSymbols: allSymbols.length,
        healthySymbols: healthySymbols,
        staleSymbols: staleSymbols,
        anomalousSymbols: anomalousSymbols,
        issues: issues,
        averageLatency: _calculateAverageLatency(),
        dataCompleteness: healthySymbols / allSymbols.length,
      );

      _qualityController.add(report);
      return report;
    } catch (e) {
      debugPrint('💥 Error in quality check: $e');
      _failedQualityChecks++;

      final errorReport = QualityReport(
        timestamp: DateTime.now(),
        qualityScore: 0.0,
        isQualityGood: false,
        totalSymbols: 0,
        healthySymbols: 0,
        staleSymbols: 0,
        anomalousSymbols: 0,
        issues: ['Quality check error: $e'],
        averageLatency: 0.0,
        dataCompleteness: 0.0,
      );

      _qualityController.add(errorReport);
      return errorReport;
    }
  }

  /// Detect price anomalies
  bool _detectPriceAnomaly(String symbol, AggregatedPriceData priceData) {
    // Get price history for trend analysis
    final priceHistory = _aggregationService.getPriceHistory(symbol, limit: 10);

    if (priceHistory.length < 5) return false; // Need enough history

    // Calculate recent average price
    final recentPrices = priceHistory.takeLast(5).map((p) => p.price).toList();
    final avgPrice = recentPrices.reduce((a, b) => a + b) / recentPrices.length;

    // Check for significant deviation
    final currentPrice = priceData.price;
    final deviationPercent = ((currentPrice - avgPrice).abs() / avgPrice) * 100;

    if (deviationPercent > _maxPriceDeviationPercent) {
      final anomaly = DataAnomalyReport(
        timestamp: DateTime.now(),
        symbol: symbol,
        anomalyType: AnomalyType.priceDeviation,
        severity: deviationPercent > 50.0
            ? AnomalySeverity.critical
            : AnomalySeverity.warning,
        description:
            'Price deviation of ${deviationPercent.toStringAsFixed(1)}% detected',
        currentValue: currentPrice,
        expectedValue: avgPrice,
        details: {
          'deviation_percent': deviationPercent,
          'current_price': currentPrice,
          'average_price': avgPrice,
          'history_points': recentPrices.length,
        },
      );

      _anomalies.add(anomaly);
      _anomalyController.add(anomaly);

      // Limit anomaly history
      if (_anomalies.length > 1000) {
        _anomalies.removeAt(0);
      }

      return true;
    }

    return false;
  }

  /// Update quality metrics for a symbol
  void _updateSymbolQuality(
    String symbol,
    AggregatedPriceData priceData,
    DateTime now,
  ) {
    if (!_symbolQuality.containsKey(symbol)) {
      _symbolQuality[symbol] = QualityMetrics(symbol: symbol);
    }

    final metrics = _symbolQuality[symbol]!;
    metrics.updateCount++;
    metrics.lastUpdate = now;

    // Calculate data freshness score
    final dataAge = now.difference(priceData.lastUpdate).inMilliseconds;
    metrics.freshnessScore = max(0.0, 100.0 - (dataAge / _maxDataAgeMs * 100));

    // Calculate reliability score based on update frequency
    metrics.reliabilityScore = min(100.0, (metrics.updateCount / 10.0) * 100);

    // Overall quality score
    metrics.qualityScore =
        (metrics.freshnessScore + metrics.reliabilityScore) / 2;
  }

  /// Update performance metrics
  void _updateMetrics() {
    if (!_isMonitoring) return;

    try {
      // Collect latency data from WebSocket service
      final wsStats = _webSocketService.connectionStats;
      final lastMessageTime = wsStats['last_message_time'] as String?;

      if (lastMessageTime != null) {
        final messageTime = DateTime.parse(lastMessageTime);
        final latency = DateTime.now()
            .difference(messageTime)
            .inMilliseconds
            .toDouble();

        _latencyHistory.add(latency);

        // Keep only recent latency data
        if (_latencyHistory.length > 100) {
          _latencyHistory.removeAt(0);
        }
      }

      final metrics = _generatePerformanceMetrics();
      _metricsController.add(metrics);
    } catch (e) {
      debugPrint('💥 Error updating metrics: $e');
    }
  }

  /// Generate health report
  HealthReport _generateHealthReport() {
    final now = DateTime.now();
    final wsState = _webSocketService.currentState;

    return HealthReport(
      timestamp: now,
      isHealthy:
          wsState.isConnected && _consecutiveErrors < _maxConsecutiveErrors,
      webSocketHealthy: wsState.isConnected,
      aggregationHealthy:
          _aggregationService.currentStatistics['total_symbols'] > 0,
      cacheHealthy: _cacheService.cacheStats['hit_ratio'] >= 0.0,
      connectionState: wsState,
      uptime: _monitoringStartTime != null
          ? now.difference(_monitoringStartTime!).inSeconds
          : 0,
      uptimePercent: _calculateUptimePercent(),
      consecutiveErrors: _consecutiveErrors,
      details: {},
    );
  }

  /// Generate quality report
  QualityReport _generateQualityReport() {
    final healthyCount = _symbolQuality.values
        .where((m) => m.qualityScore >= 80.0)
        .length;
    final totalSymbols = ExtendedExchangeTradingPairs.getAllSymbols().length;

    return QualityReport(
      timestamp: DateTime.now(),
      qualityScore: healthyCount / max(1, totalSymbols) * 100,
      isQualityGood: healthyCount / max(1, totalSymbols) >= 0.8,
      totalSymbols: totalSymbols,
      healthySymbols: healthyCount,
      staleSymbols: 0,
      anomalousSymbols: _anomalies.length,
      issues: [],
      averageLatency: _calculateAverageLatency(),
      dataCompleteness: healthyCount / max(1, totalSymbols),
    );
  }

  /// Generate performance metrics
  PerformanceMetrics _generatePerformanceMetrics() {
    return PerformanceMetrics(
      timestamp: DateTime.now(),
      averageLatency: _calculateAverageLatency(),
      minLatency: _latencyHistory.isNotEmpty
          ? _latencyHistory.reduce(min)
          : 0.0,
      maxLatency: _latencyHistory.isNotEmpty
          ? _latencyHistory.reduce(max)
          : 0.0,
      throughput: _calculateThroughput(),
      memoryUsage: _cacheService.cacheStats['memory_usage_mb'] ?? 0.0,
      cacheHitRatio: _cacheService.hitRatio,
      activeConnections: _webSocketService.currentState.isConnected ? 1 : 0,
    );
  }

  /// Calculate uptime percentage
  double _calculateUptimePercent() {
    if (_totalHealthChecks == 0) return 100.0;
    final successfulChecks = _totalHealthChecks - _failedHealthChecks;
    return (successfulChecks / _totalHealthChecks) * 100;
  }

  /// Calculate average latency
  double _calculateAverageLatency() {
    if (_latencyHistory.isEmpty) return 0.0;
    return _latencyHistory.reduce((a, b) => a + b) / _latencyHistory.length;
  }

  /// Calculate throughput (updates per minute)
  double _calculateThroughput() {
    if (_lastMetricsReset == null) return 0.0;

    final totalUpdates = _updateCounts.values.fold(
      0,
      (sum, count) => sum + count,
    );
    final elapsedMinutes = DateTime.now()
        .difference(_lastMetricsReset!)
        .inMinutes;

    return elapsedMinutes > 0 ? totalUpdates / elapsedMinutes : 0.0;
  }

  /// Dispose monitor service
  void dispose() {
    debugPrint('🧹 Disposing Market Data Monitor Service');

    stopMonitoring();

    _healthController.close();
    _qualityController.close();
    _anomalyController.close();
    _metricsController.close();
  }
}

/// Health report for service monitoring
class HealthReport {
  final DateTime timestamp;
  final bool isHealthy;
  final bool webSocketHealthy;
  final bool aggregationHealthy;
  final bool cacheHealthy;
  final WebSocketConnectionState connectionState;
  final int uptime;
  final double uptimePercent;
  final int consecutiveErrors;
  final Map<String, dynamic> details;

  HealthReport({
    required this.timestamp,
    required this.isHealthy,
    required this.webSocketHealthy,
    required this.aggregationHealthy,
    required this.cacheHealthy,
    required this.connectionState,
    required this.uptime,
    required this.uptimePercent,
    required this.consecutiveErrors,
    required this.details,
  });
}

/// Quality report for data monitoring
class QualityReport {
  final DateTime timestamp;
  final double qualityScore;
  final bool isQualityGood;
  final int totalSymbols;
  final int healthySymbols;
  final int staleSymbols;
  final int anomalousSymbols;
  final List<String> issues;
  final double averageLatency;
  final double dataCompleteness;

  QualityReport({
    required this.timestamp,
    required this.qualityScore,
    required this.isQualityGood,
    required this.totalSymbols,
    required this.healthySymbols,
    required this.staleSymbols,
    required this.anomalousSymbols,
    required this.issues,
    required this.averageLatency,
    required this.dataCompleteness,
  });
}

/// Data anomaly report
class DataAnomalyReport {
  final DateTime timestamp;
  final String symbol;
  final AnomalyType anomalyType;
  final AnomalySeverity severity;
  final String description;
  final double currentValue;
  final double expectedValue;
  final Map<String, dynamic> details;

  DataAnomalyReport({
    required this.timestamp,
    required this.symbol,
    required this.anomalyType,
    required this.severity,
    required this.description,
    required this.currentValue,
    required this.expectedValue,
    required this.details,
  });
}

/// Performance metrics
class PerformanceMetrics {
  final DateTime timestamp;
  final double averageLatency;
  final double minLatency;
  final double maxLatency;
  final double throughput;
  final double memoryUsage;
  final double cacheHitRatio;
  final int activeConnections;

  PerformanceMetrics({
    required this.timestamp,
    required this.averageLatency,
    required this.minLatency,
    required this.maxLatency,
    required this.throughput,
    required this.memoryUsage,
    required this.cacheHitRatio,
    required this.activeConnections,
  });
}

/// Quality metrics per symbol
class QualityMetrics {
  final String symbol;
  int updateCount = 0;
  DateTime? lastUpdate;
  double freshnessScore = 0.0;
  double reliabilityScore = 0.0;
  double qualityScore = 0.0;

  QualityMetrics({required this.symbol});
}

/// Types of data anomalies
enum AnomalyType {
  priceDeviation,
  volumeSpike,
  dataGap,
  latencySpike,
  connectionDrop,
}

/// Severity levels for anomalies
enum AnomalySeverity { info, warning, error, critical }

/// Helper extension for unawaited futures
extension FutureExtension on Future {
  void get unawaited => {};
}
