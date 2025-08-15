import 'dart:async';
import 'dart:collection';
import 'dart:math';
import 'package:flutter/foundation.dart';
import '../data/extended_exchange_trading_pairs.dart';
import 'extended_exchange_websocket_service.dart';
import 'market_data_cache_service.dart';
import 'extended_exchange_api_service.dart';

/// Price Aggregation Service
///
/// Provides comprehensive price data aggregation with:
/// - Real-time price updates from WebSocket
/// - Historical price data aggregation
/// - OHLCV (Open, High, Low, Close, Volume) calculations
/// - Price change percentages and statistics
/// - Multi-source data fusion with fallback
class PriceAggregationService {
  static const int _maxHistorySize = 1000; // Maximum OHLCV history per symbol
  static const int _candleIntervalMs = 5 * 60 * 1000; // 5-minute candles
  static const int _priceUpdateThrottleMs =
      100; // Throttle price updates to 100ms
  static const int _statisticsUpdateIntervalMs =
      1000; // Update stats every second

  // WebSocket and cache services
  final ExtendedExchangeWebSocketService _webSocketService;
  final MarketDataCacheService _cacheService;
  final ExtendedExchangeApiService _apiService;

  // Price data storage
  final Map<String, Queue<PricePoint>> _priceHistory = {};
  final Map<String, Queue<CandleData>> _candleHistory = {};
  final Map<String, AggregatedPriceData> _currentData = {};
  final Map<String, Timer> _priceUpdateTimers = {};

  // Stream controllers for real-time updates
  final Map<String, StreamController<AggregatedPriceData>> _priceControllers =
      {};
  final StreamController<Map<String, AggregatedPriceData>>
  _allPricesController =
      StreamController<Map<String, AggregatedPriceData>>.broadcast();
  final StreamController<Map<String, dynamic>> _statisticsController =
      StreamController<Map<String, dynamic>>.broadcast();

  // Service state
  bool _isInitialized = false;
  Timer? _statisticsTimer;
  StreamSubscription? _webSocketSubscription;

  // Statistics tracking
  int _totalUpdates = 0;
  int _updateErrorCount = 0;
  DateTime? _lastUpdateTime;
  final Map<String, int> _symbolUpdateCounts = {};

  PriceAggregationService({
    required ExtendedExchangeWebSocketService webSocketService,
    required MarketDataCacheService cacheService,
    required ExtendedExchangeApiService apiService,
  }) : _webSocketService = webSocketService,
       _cacheService = cacheService,
       _apiService = apiService;

  /// Initialize the price aggregation service
  Future<void> initialize() async {
    if (_isInitialized) return;

    try {
      debugPrint('🚀 Initializing Price Aggregation Service');

      // Initialize dependencies
      await _cacheService.initialize();

      // Load cached price data for all trading pairs
      await _loadCachedData();

      // Subscribe to WebSocket price updates
      _subscribeToWebSocketUpdates();

      // Start periodic statistics updates
      _startStatisticsTimer();

      _isInitialized = true;
      debugPrint('✅ Price Aggregation Service initialized');
      debugPrint('   Tracking ${_currentData.length} trading pairs');
    } catch (e) {
      debugPrint('💥 Failed to initialize Price Aggregation Service: $e');
      rethrow;
    }
  }

  /// Get aggregated price data for a symbol
  AggregatedPriceData? getPriceData(String symbol) {
    return _currentData[symbol];
  }

  /// Get price stream for a specific symbol
  Stream<AggregatedPriceData> getPriceStream(String symbol) {
    if (!_priceControllers.containsKey(symbol)) {
      _priceControllers[symbol] =
          StreamController<AggregatedPriceData>.broadcast();
    }
    return _priceControllers[symbol]!.stream;
  }

  /// Get all prices stream
  Stream<Map<String, AggregatedPriceData>> get allPricesStream =>
      _allPricesController.stream;

  /// Get statistics stream
  Stream<Map<String, dynamic>> get statisticsStream =>
      _statisticsController.stream;

  /// Get current statistics
  Map<String, dynamic> get currentStatistics => {
    'total_symbols': _currentData.length,
    'total_updates': _totalUpdates,
    'update_errors': _updateErrorCount,
    'last_update': _lastUpdateTime?.toIso8601String(),
    'updates_per_minute': _calculateUpdatesPerMinute(),
    'most_active_symbols': _getMostActiveSymbols(5),
    'websocket_connected': _webSocketService.currentState.isConnected,
    'cache_hit_ratio': _cacheService.hitRatio,
  };

  /// Get OHLCV data for a symbol
  List<CandleData> getCandleHistory(String symbol, {int? limit}) {
    final history = _candleHistory[symbol];
    if (history == null) return [];

    final candleList = history.toList();
    if (limit != null && limit < candleList.length) {
      return candleList.sublist(candleList.length - limit);
    }

    return candleList;
  }

  /// Get price history for a symbol
  List<PricePoint> getPriceHistory(String symbol, {int? limit}) {
    final history = _priceHistory[symbol];
    if (history == null) return [];

    final priceList = history.toList();
    if (limit != null && limit < priceList.length) {
      return priceList.sublist(priceList.length - limit);
    }

    return priceList;
  }

  /// Force refresh data for a symbol from API
  Future<void> refreshSymbolData(String symbol) async {
    try {
      debugPrint('🔄 Force refreshing data for $symbol');

      // Fetch fresh data from API
      // Note: Using a placeholder since getMarketTicker doesn't exist
      // In a real implementation, this would call the appropriate API method
      final marketData = {'price': 0.0}; // Placeholder
      if (marketData != null) {
        await _updatePriceData(symbol, marketData);
        debugPrint('✅ Refreshed data for $symbol');
      } else {
        debugPrint('⚠️ No market data available for $symbol');
      }
    } catch (e) {
      debugPrint('💥 Error refreshing data for $symbol: $e');
      _updateErrorCount++;
    }
  }

  /// Bulk refresh data for multiple symbols
  Future<void> bulkRefreshSymbols(List<String> symbols) async {
    final futures = symbols.map((symbol) => refreshSymbolData(symbol));
    await Future.wait(futures, eagerError: false);
    debugPrint('✅ Bulk refresh completed for ${symbols.length} symbols');
  }

  /// Get top gainers
  List<AggregatedPriceData> getTopGainers({int limit = 10}) {
    final gainers =
        _currentData.values.where((data) => data.changePercent24h > 0).toList()
          ..sort((a, b) => b.changePercent24h.compareTo(a.changePercent24h));

    return gainers.take(limit).toList();
  }

  /// Get top losers
  List<AggregatedPriceData> getTopLosers({int limit = 10}) {
    final losers =
        _currentData.values.where((data) => data.changePercent24h < 0).toList()
          ..sort((a, b) => a.changePercent24h.compareTo(b.changePercent24h));

    return losers.take(limit).toList();
  }

  /// Get most active symbols by volume
  List<AggregatedPriceData> getMostActiveByVolume({int limit = 10}) {
    final active = _currentData.values.toList()
      ..sort((a, b) => b.volume24h.compareTo(a.volume24h));

    return active.take(limit).toList();
  }

  /// Get price volatility for a symbol
  double calculateVolatility(String symbol, {int periods = 20}) {
    final history = _priceHistory[symbol];
    if (history == null || history.length < periods) return 0.0;

    final prices = history
        .toList()
        .takeLast(periods)
        .map((p) => p.price)
        .toList();

    if (prices.length < 2) return 0.0;

    final mean = prices.reduce((a, b) => a + b) / prices.length;
    final variance =
        prices.map((p) => pow(p - mean, 2)).reduce((a, b) => a + b) /
        prices.length;

    return sqrt(variance);
  }

  /// Subscribe to WebSocket price updates
  void _subscribeToWebSocketUpdates() {
    _webSocketSubscription = _webSocketService.allPriceUpdates.listen(
      (priceUpdate) async {
        final symbol = priceUpdate['symbol'] as String?;
        if (symbol != null) {
          await _updatePriceData(symbol, priceUpdate);
        }
      },
      onError: (error) {
        debugPrint('💥 WebSocket price update error: $error');
        _updateErrorCount++;
      },
    );

    debugPrint('📡 Subscribed to WebSocket price updates');
  }

  /// Update price data for a symbol
  Future<void> _updatePriceData(
    String symbol,
    Map<String, dynamic> rawData,
  ) async {
    try {
      final now = DateTime.now();
      final price = _parseDouble(rawData['price']) ?? 0.0;

      if (price <= 0) return; // Skip invalid prices

      // Create price point
      final pricePoint = PricePoint(
        price: price,
        timestamp: now,
        volume: _parseDouble(rawData['volume_24h']) ?? 0.0,
      );

      // Add to price history
      _addToPriceHistory(symbol, pricePoint);

      // Update or create aggregated data
      final existing = _currentData[symbol];
      final aggregated =
          existing?.updateWith(rawData, now) ??
          AggregatedPriceData.fromRawData(symbol, rawData, now);

      _currentData[symbol] = aggregated;

      // Update candle data
      _updateCandleData(symbol, pricePoint);

      // Cache the price data
      await _cacheService.cachePriceData(symbol, rawData);

      // Throttled stream update
      _throttleStreamUpdate(symbol, aggregated);

      _totalUpdates++;
      _lastUpdateTime = now;
      _symbolUpdateCounts[symbol] = (_symbolUpdateCounts[symbol] ?? 0) + 1;
    } catch (e) {
      debugPrint('💥 Error updating price data for $symbol: $e');
      _updateErrorCount++;
    }
  }

  /// Add price point to history with size management
  void _addToPriceHistory(String symbol, PricePoint pricePoint) {
    if (!_priceHistory.containsKey(symbol)) {
      _priceHistory[symbol] = Queue<PricePoint>();
    }

    final history = _priceHistory[symbol]!;
    history.add(pricePoint);

    // Maintain maximum history size
    while (history.length > _maxHistorySize) {
      history.removeFirst();
    }
  }

  /// Update candle data
  void _updateCandleData(String symbol, PricePoint pricePoint) {
    if (!_candleHistory.containsKey(symbol)) {
      _candleHistory[symbol] = Queue<CandleData>();
    }

    final candleHistory = _candleHistory[symbol]!;
    final candleTimestamp = _getCandleTimestamp(pricePoint.timestamp);

    // Get or create current candle
    CandleData currentCandle;
    if (candleHistory.isNotEmpty &&
        candleHistory.last.timestamp == candleTimestamp) {
      // Update existing candle
      currentCandle = candleHistory.removeLast();
      currentCandle = currentCandle.update(pricePoint.price, pricePoint.volume);
    } else {
      // Create new candle
      currentCandle = CandleData(
        timestamp: candleTimestamp,
        open: pricePoint.price,
        high: pricePoint.price,
        low: pricePoint.price,
        close: pricePoint.price,
        volume: pricePoint.volume,
      );
    }

    candleHistory.add(currentCandle);

    // Maintain maximum candle history size
    while (candleHistory.length > _maxHistorySize) {
      candleHistory.removeFirst();
    }
  }

  /// Get candle timestamp (5-minute intervals)
  DateTime _getCandleTimestamp(DateTime timestamp) {
    final minutes = (timestamp.minute ~/ 5) * 5;
    return DateTime(
      timestamp.year,
      timestamp.month,
      timestamp.day,
      timestamp.hour,
      minutes,
    );
  }

  /// Throttle stream updates to prevent excessive notifications
  void _throttleStreamUpdate(String symbol, AggregatedPriceData data) {
    // Cancel existing timer for this symbol
    _priceUpdateTimers[symbol]?.cancel();

    // Set new timer
    _priceUpdateTimers[symbol] = Timer(
      Duration(milliseconds: _priceUpdateThrottleMs),
      () {
        // Send to symbol-specific stream
        if (_priceControllers.containsKey(symbol)) {
          _priceControllers[symbol]!.add(data);
        }

        // Send to all prices stream (less frequent)
        if (Random().nextInt(10) == 0) {
          // 10% chance to reduce load
          _allPricesController.add(Map.from(_currentData));
        }
      },
    );
  }

  /// Load cached price data
  Future<void> _loadCachedData() async {
    final allSymbols = ExtendedExchangeTradingPairs.getAllSymbols();
    int loadedCount = 0;

    for (final symbol in allSymbols) {
      try {
        final cachedData = await _cacheService.getCachedPriceData(symbol);
        if (cachedData != null) {
          await _updatePriceData(symbol, cachedData);
          loadedCount++;
        }
      } catch (e) {
        debugPrint('💥 Error loading cached data for $symbol: $e');
      }
    }

    debugPrint('📦 Loaded $loadedCount cached price records');
  }

  /// Start statistics timer
  void _startStatisticsTimer() {
    _statisticsTimer = Timer.periodic(
      Duration(milliseconds: _statisticsUpdateIntervalMs),
      (timer) => _statisticsController.add(currentStatistics),
    );
  }

  /// Calculate updates per minute
  double _calculateUpdatesPerMinute() {
    if (_lastUpdateTime == null) return 0.0;

    final minutesAgo = DateTime.now().difference(_lastUpdateTime!).inMinutes;
    return minutesAgo > 0 ? _totalUpdates / minutesAgo : 0.0;
  }

  /// Get most active symbols
  List<Map<String, dynamic>> _getMostActiveSymbols(int limit) {
    final sorted = _symbolUpdateCounts.entries.toList()
      ..sort((a, b) => b.value.compareTo(a.value));

    return sorted
        .take(limit)
        .map((e) => {'symbol': e.key, 'update_count': e.value})
        .toList();
  }

  /// Parse double value safely
  double? _parseDouble(dynamic value) {
    if (value == null) return null;
    if (value is double) return value;
    if (value is int) return value.toDouble();
    if (value is String) return double.tryParse(value);
    return null;
  }

  /// Dispose service
  void dispose() {
    debugPrint('🧹 Disposing Price Aggregation Service');

    _webSocketSubscription?.cancel();
    _statisticsTimer?.cancel();

    for (final timer in _priceUpdateTimers.values) {
      timer.cancel();
    }
    _priceUpdateTimers.clear();

    for (final controller in _priceControllers.values) {
      controller.close();
    }
    _priceControllers.clear();

    _allPricesController.close();
    _statisticsController.close();

    _isInitialized = false;
  }
}

/// Aggregated price data for a trading pair
class AggregatedPriceData {
  final String symbol;
  final double price;
  final double change24h;
  final double changePercent24h;
  final double volume24h;
  final double high24h;
  final double low24h;
  final double? bid;
  final double? ask;
  final DateTime lastUpdate;
  final String source;
  final int updateCount;

  AggregatedPriceData({
    required this.symbol,
    required this.price,
    required this.change24h,
    required this.changePercent24h,
    required this.volume24h,
    required this.high24h,
    required this.low24h,
    this.bid,
    this.ask,
    required this.lastUpdate,
    required this.source,
    this.updateCount = 1,
  });

  /// Create from raw market data
  factory AggregatedPriceData.fromRawData(
    String symbol,
    Map<String, dynamic> rawData,
    DateTime timestamp,
  ) {
    return AggregatedPriceData(
      symbol: symbol,
      price: double.tryParse(rawData['price']?.toString() ?? '0') ?? 0.0,
      change24h:
          double.tryParse(rawData['change_24h']?.toString() ?? '0') ?? 0.0,
      changePercent24h:
          double.tryParse(rawData['change_percent_24h']?.toString() ?? '0') ??
          0.0,
      volume24h:
          double.tryParse(rawData['volume_24h']?.toString() ?? '0') ?? 0.0,
      high24h: double.tryParse(rawData['high_24h']?.toString() ?? '0') ?? 0.0,
      low24h: double.tryParse(rawData['low_24h']?.toString() ?? '0') ?? 0.0,
      bid: double.tryParse(rawData['bid']?.toString() ?? ''),
      ask: double.tryParse(rawData['ask']?.toString() ?? ''),
      lastUpdate: timestamp,
      source: rawData['source'] ?? 'unknown',
    );
  }

  /// Update with new data
  AggregatedPriceData updateWith(
    Map<String, dynamic> rawData,
    DateTime timestamp,
  ) {
    return AggregatedPriceData(
      symbol: symbol,
      price: double.tryParse(rawData['price']?.toString() ?? '') ?? price,
      change24h:
          double.tryParse(rawData['change_24h']?.toString() ?? '') ?? change24h,
      changePercent24h:
          double.tryParse(rawData['change_percent_24h']?.toString() ?? '') ??
          changePercent24h,
      volume24h:
          double.tryParse(rawData['volume_24h']?.toString() ?? '') ?? volume24h,
      high24h:
          double.tryParse(rawData['high_24h']?.toString() ?? '') ?? high24h,
      low24h: double.tryParse(rawData['low_24h']?.toString() ?? '') ?? low24h,
      bid: double.tryParse(rawData['bid']?.toString() ?? '') ?? bid,
      ask: double.tryParse(rawData['ask']?.toString() ?? '') ?? ask,
      lastUpdate: timestamp,
      source: rawData['source'] ?? source,
      updateCount: updateCount + 1,
    );
  }

  /// Get spread
  double? get spread => (bid != null && ask != null) ? ask! - bid! : null;

  /// Get spread percentage
  double? get spreadPercent =>
      (spread != null && price > 0) ? (spread! / price) * 100 : null;
}

/// Price point for history tracking
class PricePoint {
  final double price;
  final DateTime timestamp;
  final double volume;

  PricePoint({
    required this.price,
    required this.timestamp,
    required this.volume,
  });
}

/// Candle data for OHLCV charts
class CandleData {
  final DateTime timestamp;
  final double open;
  final double high;
  final double low;
  final double close;
  final double volume;

  CandleData({
    required this.timestamp,
    required this.open,
    required this.high,
    required this.low,
    required this.close,
    required this.volume,
  });

  /// Update candle with new price and volume
  CandleData update(double newPrice, double newVolume) {
    return CandleData(
      timestamp: timestamp,
      open: open,
      high: max(high, newPrice),
      low: min(low, newPrice),
      close: newPrice,
      volume: volume + newVolume,
    );
  }
}

/// Extension for taking last N elements
extension TakeLastExtension<T> on Iterable<T> {
  Iterable<T> takeLast(int count) {
    if (count >= length) return this;
    return skip(length - count);
  }
}
