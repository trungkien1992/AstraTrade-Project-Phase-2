import 'dart:async';
import 'package:flutter/foundation.dart';
import 'extended_exchange_websocket_service.dart';
import 'price_aggregation_service.dart';
import 'market_data_cache_service.dart';
import 'market_data_monitor_service.dart';
import 'extended_exchange_chart_service.dart';
import 'extended_exchange_api_service.dart';
import '../data/extended_exchange_trading_pairs.dart';

/// Extended Exchange Integration Service
///
/// Unified service that orchestrates all trading pairs integration components:
/// - WebSocket real-time data feeds
/// - Price aggregation and caching
/// - Data quality monitoring
/// - Chart data services
/// - HMAC authentication
///
/// Provides a single entry point for all 65+ trading pairs functionality
class ExtendedExchangeIntegrationService {
  // Core services
  late final ExtendedExchangeWebSocketService _webSocketService;
  late final PriceAggregationService _aggregationService;
  late final MarketDataCacheService _cacheService;
  late final MarketDataMonitorService _monitorService;
  late final ExtendedExchangeChartService _chartService;
  late final ExtendedExchangeApiService _apiService;

  // Service state
  bool _isInitialized = false;
  bool _isStarted = false;
  final Completer<void> _initCompleter = Completer<void>();

  // Stream controllers for unified API
  final StreamController<ServiceStatus> _statusController =
      StreamController<ServiceStatus>.broadcast();
  final StreamController<Map<String, AggregatedPriceData>> _pricesController =
      StreamController<Map<String, AggregatedPriceData>>.broadcast();
  final StreamController<IntegrationMetrics> _metricsController =
      StreamController<IntegrationMetrics>.broadcast();

  // Metrics tracking
  DateTime? _startTime;
  int _totalSymbolsTracked = 0;
  Timer? _metricsTimer;

  /// Service status stream
  Stream<ServiceStatus> get statusStream => _statusController.stream;

  /// All price updates stream
  Stream<Map<String, AggregatedPriceData>> get allPricesStream =>
      _pricesController.stream;

  /// Integration metrics stream
  Stream<IntegrationMetrics> get metricsStream => _metricsController.stream;

  /// Current service status
  ServiceStatus get currentStatus => _getCurrentStatus();

  /// All supported trading pairs
  List<ExtendedExchangeTradingPair> get supportedTradingPairs =>
      ExtendedExchangeTradingPairs.allTradingPairs;

  /// Popular trading pairs for quick access
  List<ExtendedExchangeTradingPair> get popularTradingPairs =>
      ExtendedExchangeTradingPairs.getPopularTradingPairs();

  /// Initialize the integration service
  Future<void> initialize() async {
    if (_isInitialized) return;

    try {
      debugPrint('🚀 Initializing Extended Exchange Integration Service');

      // Initialize cache service first
      _cacheService = marketDataCacheService;
      await _cacheService.initialize();

      // Initialize API service
      _apiService = ExtendedExchangeApiService();

      // Initialize WebSocket service
      _webSocketService = ExtendedExchangeWebSocketService();

      // Initialize price aggregation service
      _aggregationService = PriceAggregationService(
        webSocketService: _webSocketService,
        cacheService: _cacheService,
        apiService: _apiService,
      );

      // Initialize monitoring service
      _monitorService = MarketDataMonitorService(
        webSocketService: _webSocketService,
        aggregationService: _aggregationService,
        cacheService: _cacheService,
      );

      // Initialize chart service with all dependencies
      _chartService = ExtendedExchangeChartService(
        webSocketService: _webSocketService,
        aggregationService: _aggregationService,
        cacheService: _cacheService,
      );

      // Initialize services in order
      await _aggregationService.initialize();

      _isInitialized = true;
      _initCompleter.complete();

      debugPrint('✅ Extended Exchange Integration Service initialized');
      debugPrint(
        '   Total trading pairs supported: ${supportedTradingPairs.length}',
      );
      debugPrint('   Popular pairs available: ${popularTradingPairs.length}');
    } catch (e) {
      debugPrint(
        '💥 Failed to initialize Extended Exchange Integration Service: $e',
      );
      _initCompleter.completeError(e);
      rethrow;
    }
  }

  /// Start all services
  Future<void> start() async {
    await _ensureInitialized();

    if (_isStarted) return;

    try {
      debugPrint('🎬 Starting Extended Exchange Integration Service');
      _startTime = DateTime.now();

      // Start WebSocket connection
      await _webSocketService.connect();

      // Start monitoring
      _monitorService.startMonitoring();

      // Start metrics collection
      _startMetricsCollection();

      // Set up stream forwarding
      _setupStreamForwarding();

      _isStarted = true;
      _totalSymbolsTracked = supportedTradingPairs.length;

      // Emit initial status
      _statusController.add(_getCurrentStatus());

      debugPrint('✅ Extended Exchange Integration Service started');
      debugPrint('   Tracking $_totalSymbolsTracked trading pairs');
    } catch (e) {
      debugPrint(
        '💥 Failed to start Extended Exchange Integration Service: $e',
      );
      _statusController.add(
        ServiceStatus(
          isRunning: false,
          isHealthy: false,
          error: e.toString(),
          connectedSymbols: 0,
          totalSymbols: supportedTradingPairs.length,
          uptime: Duration.zero,
        ),
      );
      rethrow;
    }
  }

  /// Stop all services
  Future<void> stop() async {
    if (!_isStarted) return;

    debugPrint('⏹️ Stopping Extended Exchange Integration Service');

    // Stop metrics collection
    _metricsTimer?.cancel();
    _metricsTimer = null;

    // Stop monitoring
    _monitorService.stopMonitoring();

    // Disconnect WebSocket
    _webSocketService.disconnect();

    _isStarted = false;

    // Emit final status
    _statusController.add(_getCurrentStatus());

    debugPrint('✅ Extended Exchange Integration Service stopped');
  }

  /// Get price data for a specific symbol
  AggregatedPriceData? getPriceData(String symbol) {
    if (!_isStarted) return null;
    return _aggregationService.getPriceData(symbol);
  }

  /// Get price stream for a specific symbol
  Stream<AggregatedPriceData> getPriceStream(String symbol) {
    if (!_isStarted) {
      return Stream.empty();
    }
    return _aggregationService.getPriceStream(symbol);
  }

  /// Get candlestick data for charts
  Future<List<dynamic>> getCandlestickData({
    required String symbol,
    String interval = '5m',
    int limit = 100,
  }) async {
    await _ensureInitialized();
    return await _chartService.getCandlestickData(
      symbol: symbol,
      interval: interval,
      limit: limit,
    );
  }

  /// Get current market ticker data
  Future<Map<String, dynamic>?> getTickerData(String symbol) async {
    await _ensureInitialized();
    return await _chartService.getTickerData(symbol);
  }

  /// Get trading pairs by category
  List<ExtendedExchangeTradingPair> getTradingPairsByCategory(
    TradingPairCategory category,
  ) {
    return ExtendedExchangeTradingPairs.getTradingPairsByCategory(category);
  }

  /// Search trading pairs
  List<ExtendedExchangeTradingPair> searchTradingPairs(String query) {
    return ExtendedExchangeTradingPairs.searchTradingPairs(query);
  }

  /// Get top gainers
  List<AggregatedPriceData> getTopGainers({int limit = 10}) {
    if (!_isStarted) return [];
    return _aggregationService.getTopGainers(limit: limit);
  }

  /// Get top losers
  List<AggregatedPriceData> getTopLosers({int limit = 10}) {
    if (!_isStarted) return [];
    return _aggregationService.getTopLosers(limit: limit);
  }

  /// Get most active by volume
  List<AggregatedPriceData> getMostActiveByVolume({int limit = 10}) {
    if (!_isStarted) return [];
    return _aggregationService.getMostActiveByVolume(limit: limit);
  }

  /// Force refresh data for a symbol
  Future<void> refreshSymbolData(String symbol) async {
    if (!_isStarted) return;
    await _aggregationService.refreshSymbolData(symbol);
  }

  /// Bulk refresh multiple symbols
  Future<void> bulkRefreshSymbols(List<String> symbols) async {
    if (!_isStarted) return;
    await _aggregationService.bulkRefreshSymbols(symbols);
  }

  /// Get health report
  HealthReport get currentHealthReport => _monitorService.currentHealthReport;

  /// Get quality report
  QualityReport get currentQualityReport =>
      _monitorService.currentQualityReport;

  /// Get performance metrics
  PerformanceMetrics get currentPerformanceMetrics =>
      _monitorService.currentPerformanceMetrics;

  /// Get cache statistics
  Map<String, dynamic> get cacheStats => _cacheService.cacheStats;

  /// Clear cache
  Future<void> clearCache() async {
    await _cacheService.clearAll();
  }

  /// Reset all metrics
  void resetMetrics() {
    _monitorService.resetMetrics();
  }

  /// Get comprehensive service statistics
  Map<String, dynamic> get serviceStatistics {
    final wsStats = _webSocketService.connectionStats;
    final aggStats = _aggregationService.currentStatistics;
    final cacheStats = _cacheService.cacheStats;
    final healthReport = _monitorService.currentHealthReport;
    final qualityReport = _monitorService.currentQualityReport;
    final perfMetrics = _monitorService.currentPerformanceMetrics;

    return {
      'service': {
        'is_running': _isStarted,
        'is_healthy': healthReport.isHealthy,
        'uptime_seconds': _startTime != null
            ? DateTime.now().difference(_startTime!).inSeconds
            : 0,
        'total_symbols': _totalSymbolsTracked,
      },
      'websocket': wsStats,
      'aggregation': aggStats,
      'cache': cacheStats,
      'health': {
        'overall_healthy': healthReport.isHealthy,
        'websocket_healthy': healthReport.webSocketHealthy,
        'aggregation_healthy': healthReport.aggregationHealthy,
        'cache_healthy': healthReport.cacheHealthy,
        'uptime_percent': healthReport.uptimePercent,
        'consecutive_errors': healthReport.consecutiveErrors,
      },
      'quality': {
        'quality_score': qualityReport.qualityScore,
        'is_quality_good': qualityReport.isQualityGood,
        'healthy_symbols': qualityReport.healthySymbols,
        'stale_symbols': qualityReport.staleSymbols,
        'anomalous_symbols': qualityReport.anomalousSymbols,
        'data_completeness': qualityReport.dataCompleteness,
      },
      'performance': {
        'average_latency_ms': perfMetrics.averageLatency,
        'min_latency_ms': perfMetrics.minLatency,
        'max_latency_ms': perfMetrics.maxLatency,
        'throughput_per_min': perfMetrics.throughput,
        'memory_usage_mb': perfMetrics.memoryUsage,
        'cache_hit_ratio': perfMetrics.cacheHitRatio,
        'active_connections': perfMetrics.activeConnections,
      },
    };
  }

  /// Ensure service is initialized
  Future<void> _ensureInitialized() async {
    if (!_isInitialized) {
      await _initCompleter.future;
    }
  }

  /// Get current service status
  ServiceStatus _getCurrentStatus() {
    return ServiceStatus(
      isRunning: _isStarted,
      isHealthy: _isStarted
          ? _monitorService.currentHealthReport.isHealthy
          : false,
      error: null,
      connectedSymbols: _isStarted
          ? _aggregationService.currentStatistics['total_symbols'] ?? 0
          : 0,
      totalSymbols: supportedTradingPairs.length,
      uptime: _startTime != null
          ? DateTime.now().difference(_startTime!)
          : Duration.zero,
    );
  }

  /// Set up stream forwarding from internal services
  void _setupStreamForwarding() {
    // Forward aggregated prices
    _aggregationService.allPricesStream.listen(
      (prices) => _pricesController.add(prices),
      onError: (error) => debugPrint('💥 Error forwarding prices: $error'),
    );

    // Forward status updates based on health reports
    _monitorService.healthStream.listen(
      (healthReport) => _statusController.add(_getCurrentStatus()),
      onError: (error) => debugPrint('💥 Error forwarding status: $error'),
    );
  }

  /// Start metrics collection
  void _startMetricsCollection() {
    _metricsTimer = Timer.periodic(Duration(seconds: 30), (timer) {
      final metrics = IntegrationMetrics(
        timestamp: DateTime.now(),
        totalSymbols: _totalSymbolsTracked,
        activeSymbols:
            _aggregationService.currentStatistics['total_symbols'] ?? 0,
        websocketConnected: _webSocketService.currentState.isConnected,
        cacheHitRatio: _cacheService.hitRatio,
        averageLatency:
            _monitorService.currentPerformanceMetrics.averageLatency,
        memoryUsage: _monitorService.currentPerformanceMetrics.memoryUsage,
        uptime: _startTime != null
            ? DateTime.now().difference(_startTime!)
            : Duration.zero,
      );

      _metricsController.add(metrics);
    });
  }

  /// Dispose the integration service
  void dispose() {
    debugPrint('🧹 Disposing Extended Exchange Integration Service');

    stop();

    _metricsTimer?.cancel();
    _monitorService.dispose();
    _aggregationService.dispose();
    _webSocketService.dispose();

    _statusController.close();
    _pricesController.close();
    _metricsController.close();

    _isInitialized = false;
    _isStarted = false;
  }
}

/// Service status information
class ServiceStatus {
  final bool isRunning;
  final bool isHealthy;
  final String? error;
  final int connectedSymbols;
  final int totalSymbols;
  final Duration uptime;

  ServiceStatus({
    required this.isRunning,
    required this.isHealthy,
    this.error,
    required this.connectedSymbols,
    required this.totalSymbols,
    required this.uptime,
  });

  double get connectionPercentage =>
      totalSymbols > 0 ? (connectedSymbols / totalSymbols) * 100 : 0.0;
}

/// Integration metrics
class IntegrationMetrics {
  final DateTime timestamp;
  final int totalSymbols;
  final int activeSymbols;
  final bool websocketConnected;
  final double cacheHitRatio;
  final double averageLatency;
  final double memoryUsage;
  final Duration uptime;

  IntegrationMetrics({
    required this.timestamp,
    required this.totalSymbols,
    required this.activeSymbols,
    required this.websocketConnected,
    required this.cacheHitRatio,
    required this.averageLatency,
    required this.memoryUsage,
    required this.uptime,
  });
}

/// Singleton instance for global access
final extendedExchangeIntegrationService = ExtendedExchangeIntegrationService();
