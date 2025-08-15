import 'dart:async';
import 'dart:convert';
import 'dart:collection';
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:hive_flutter/hive_flutter.dart';
import '../data/extended_exchange_trading_pairs.dart';

/// Market Data Cache Service
///
/// Provides intelligent caching for real-time price data with:
/// - In-memory cache with TTL management
/// - Persistent storage for offline access
/// - Memory optimization for 65+ trading pairs
/// - Cache invalidation strategies
class MarketDataCacheService {
  static const String _cacheBoxName = 'market_data_cache';
  static const String _metadataBoxName = 'cache_metadata';
  static const String _prefsKey = 'market_cache_stats';

  // Cache TTL settings
  static const int _priceDataTtlMs = 5 * 60 * 1000; // 5 minutes for price data
  static const int _marketStatsTtlMs =
      60 * 60 * 1000; // 1 hour for market stats
  static const int _historicalDataTtlMs =
      24 * 60 * 60 * 1000; // 24 hours for historical data

  // Memory management
  static const int _maxMemoryCacheSize = 1000; // Maximum items in memory
  static const int _cleanupThresholdSize = 1200; // Trigger cleanup at this size

  // In-memory cache with LRU eviction
  final LinkedHashMap<String, CachedData> _memoryCache =
      LinkedHashMap<String, CachedData>();

  // Hive boxes for persistent storage
  Box<String>? _cacheBox;
  Box<String>? _metadataBox;

  // Cache statistics
  int _hitCount = 0;
  int _missCount = 0;
  int _writeCount = 0;

  // Initialization state
  bool _isInitialized = false;
  final Completer<void> _initCompleter = Completer<void>();

  /// Initialize the cache service
  Future<void> initialize() async {
    if (_isInitialized) return;

    try {
      debugPrint('🚀 Initializing Market Data Cache Service');

      // Initialize Hive if not already done
      if (!Hive.isAdapterRegistered(0)) {
        await Hive.initFlutter();
      }

      // Open cache boxes
      _cacheBox = await Hive.openBox<String>(_cacheBoxName);
      _metadataBox = await Hive.openBox<String>(_metadataBoxName);

      // Load existing cache statistics
      await _loadCacheStats();

      // Perform initial cleanup
      await _performCleanup();

      _isInitialized = true;
      _initCompleter.complete();

      debugPrint('✅ Market Data Cache initialized successfully');
      debugPrint('   Memory cache size: ${_memoryCache.length}');
      debugPrint('   Persistent cache size: ${_cacheBox?.length ?? 0}');
    } catch (e) {
      debugPrint('💥 Failed to initialize cache service: $e');
      _initCompleter.completeError(e);
      rethrow;
    }
  }

  /// Ensure cache is initialized
  Future<void> _ensureInitialized() async {
    if (!_isInitialized) {
      await _initCompleter.future;
    }
  }

  /// Cache price data for a trading pair
  Future<void> cachePriceData(
    String symbol,
    Map<String, dynamic> priceData,
  ) async {
    await _ensureInitialized();

    try {
      final cacheKey = 'price_$symbol';
      final cachedData = CachedData(
        key: cacheKey,
        data: priceData,
        timestamp: DateTime.now().millisecondsSinceEpoch,
        ttlMs: _priceDataTtlMs,
        dataType: CacheDataType.priceData,
      );

      // Store in memory cache
      _memoryCache[cacheKey] = cachedData;
      _moveToFront(cacheKey);

      // Store in persistent cache
      await _cacheBox?.put(cacheKey, json.encode(cachedData.toMap()));

      _writeCount++;

      // Trigger cleanup if needed
      if (_memoryCache.length > _cleanupThresholdSize) {
        unawaited(_performMemoryCleanup());
      }
    } catch (e) {
      debugPrint('💥 Error caching price data for $symbol: $e');
    }
  }

  /// Get cached price data for a trading pair
  Future<Map<String, dynamic>?> getCachedPriceData(String symbol) async {
    await _ensureInitialized();

    final cacheKey = 'price_$symbol';

    // Check memory cache first
    final memoryCached = _memoryCache[cacheKey];
    if (memoryCached != null && !memoryCached.isExpired) {
      _moveToFront(cacheKey);
      _hitCount++;
      return memoryCached.data;
    }

    // Check persistent cache
    try {
      final persistentData = _cacheBox?.get(cacheKey);
      if (persistentData != null) {
        final cachedData = CachedData.fromMap(json.decode(persistentData));

        if (!cachedData.isExpired) {
          // Move to memory cache for faster access
          _memoryCache[cacheKey] = cachedData;
          _moveToFront(cacheKey);
          _hitCount++;
          return cachedData.data;
        } else {
          // Remove expired data
          await _cacheBox?.delete(cacheKey);
        }
      }
    } catch (e) {
      debugPrint('💥 Error reading cached price data for $symbol: $e');
    }

    _missCount++;
    return null;
  }

  /// Cache market statistics
  Future<void> cacheMarketStats(
    String symbol,
    Map<String, dynamic> marketStats,
  ) async {
    await _ensureInitialized();

    try {
      final cacheKey = 'stats_$symbol';
      final cachedData = CachedData(
        key: cacheKey,
        data: marketStats,
        timestamp: DateTime.now().millisecondsSinceEpoch,
        ttlMs: _marketStatsTtlMs,
        dataType: CacheDataType.marketStats,
      );

      _memoryCache[cacheKey] = cachedData;
      _moveToFront(cacheKey);

      await _cacheBox?.put(cacheKey, json.encode(cachedData.toMap()));
      _writeCount++;
    } catch (e) {
      debugPrint('💥 Error caching market stats for $symbol: $e');
    }
  }

  /// Get cached market statistics
  Future<Map<String, dynamic>?> getCachedMarketStats(String symbol) async {
    await _ensureInitialized();

    final cacheKey = 'stats_$symbol';
    return await _getCachedData(cacheKey);
  }

  /// Cache historical price data
  Future<void> cacheHistoricalData(
    String symbol,
    String interval,
    List<Map<String, dynamic>> historicalData,
  ) async {
    await _ensureInitialized();

    try {
      final cacheKey = 'historical_${symbol}_$interval';
      final cachedData = CachedData(
        key: cacheKey,
        data: {'data': historicalData, 'count': historicalData.length},
        timestamp: DateTime.now().millisecondsSinceEpoch,
        ttlMs: _historicalDataTtlMs,
        dataType: CacheDataType.historicalData,
      );

      // Historical data is typically larger, store directly in persistent cache
      await _cacheBox?.put(cacheKey, json.encode(cachedData.toMap()));
      _writeCount++;
    } catch (e) {
      debugPrint('💥 Error caching historical data for $symbol: $e');
    }
  }

  /// Get cached historical data
  Future<List<Map<String, dynamic>>?> getCachedHistoricalData(
    String symbol,
    String interval,
  ) async {
    await _ensureInitialized();

    final cacheKey = 'historical_${symbol}_$interval';

    try {
      final persistentData = _cacheBox?.get(cacheKey);
      if (persistentData != null) {
        final cachedData = CachedData.fromMap(json.decode(persistentData));

        if (!cachedData.isExpired) {
          _hitCount++;
          final data = cachedData.data['data'] as List?;
          return data?.cast<Map<String, dynamic>>();
        } else {
          await _cacheBox?.delete(cacheKey);
        }
      }
    } catch (e) {
      debugPrint('💥 Error reading cached historical data for $symbol: $e');
    }

    _missCount++;
    return null;
  }

  /// Cache multiple price updates in batch
  Future<void> batchCachePriceData(
    Map<String, Map<String, dynamic>> priceUpdates,
  ) async {
    await _ensureInitialized();

    final futures = <Future<void>>[];

    for (final entry in priceUpdates.entries) {
      futures.add(cachePriceData(entry.key, entry.value));
    }

    await Future.wait(futures);
    debugPrint('✅ Batch cached ${priceUpdates.length} price updates');
  }

  /// Get cache hit ratio
  double get hitRatio {
    final totalRequests = _hitCount + _missCount;
    return totalRequests > 0 ? _hitCount / totalRequests : 0.0;
  }

  /// Get cache statistics
  Map<String, dynamic> get cacheStats => {
    'hit_count': _hitCount,
    'miss_count': _missCount,
    'write_count': _writeCount,
    'hit_ratio': hitRatio,
    'memory_cache_size': _memoryCache.length,
    'persistent_cache_size': _cacheBox?.length ?? 0,
    'memory_usage_mb': _estimateMemoryUsage() / (1024 * 1024),
  };

  /// Clear expired entries from cache
  Future<void> clearExpiredEntries() async {
    await _ensureInitialized();

    int memoryCleared = 0;
    int persistentCleared = 0;

    // Clear expired memory cache entries
    final expiredMemoryKeys = <String>[];
    for (final entry in _memoryCache.entries) {
      if (entry.value.isExpired) {
        expiredMemoryKeys.add(entry.key);
      }
    }

    for (final key in expiredMemoryKeys) {
      _memoryCache.remove(key);
      memoryCleared++;
    }

    // Clear expired persistent cache entries
    try {
      final allKeys = _cacheBox?.keys.toList() ?? [];
      final expiredKeys = <dynamic>[];

      for (final key in allKeys) {
        try {
          final data = _cacheBox?.get(key);
          if (data != null) {
            final cachedData = CachedData.fromMap(json.decode(data));
            if (cachedData.isExpired) {
              expiredKeys.add(key);
            }
          }
        } catch (e) {
          // If we can't parse the data, consider it expired
          expiredKeys.add(key);
        }
      }

      for (final key in expiredKeys) {
        await _cacheBox?.delete(key);
        persistentCleared++;
      }
    } catch (e) {
      debugPrint('💥 Error clearing expired persistent cache: $e');
    }

    debugPrint('🧹 Cache cleanup completed:');
    debugPrint('   Memory entries cleared: $memoryCleared');
    debugPrint('   Persistent entries cleared: $persistentCleared');
  }

  /// Clear all cached data
  Future<void> clearAll() async {
    await _ensureInitialized();

    _memoryCache.clear();
    await _cacheBox?.clear();
    await _metadataBox?.clear();

    _hitCount = 0;
    _missCount = 0;
    _writeCount = 0;

    await _saveCacheStats();
    debugPrint('🧹 All cache data cleared');
  }

  /// Preload cache with popular trading pairs
  Future<void> preloadPopularPairs() async {
    await _ensureInitialized();

    final popularPairs = ExtendedExchangeTradingPairs.getPopularTradingPairs();
    debugPrint('🔥 Preloading cache for ${popularPairs.length} popular pairs');

    // This would typically fetch from API and cache
    // For now, we'll just ensure cache keys are ready
    for (final pair in popularPairs) {
      final cacheKey = 'price_${pair.symbol}';
      // Prepare cache slot
      final placeholder = CachedData(
        key: cacheKey,
        data: {'symbol': pair.symbol, 'placeholder': true},
        timestamp: DateTime.now().millisecondsSinceEpoch,
        ttlMs: 1000, // Short TTL for placeholder
        dataType: CacheDataType.priceData,
      );

      _memoryCache[cacheKey] = placeholder;
    }
  }

  /// Get generic cached data
  Future<Map<String, dynamic>?> _getCachedData(String cacheKey) async {
    // Check memory cache first
    final memoryCached = _memoryCache[cacheKey];
    if (memoryCached != null && !memoryCached.isExpired) {
      _moveToFront(cacheKey);
      _hitCount++;
      return memoryCached.data;
    }

    // Check persistent cache
    try {
      final persistentData = _cacheBox?.get(cacheKey);
      if (persistentData != null) {
        final cachedData = CachedData.fromMap(json.decode(persistentData));

        if (!cachedData.isExpired) {
          _memoryCache[cacheKey] = cachedData;
          _moveToFront(cacheKey);
          _hitCount++;
          return cachedData.data;
        } else {
          await _cacheBox?.delete(cacheKey);
        }
      }
    } catch (e) {
      debugPrint('💥 Error reading cached data for $cacheKey: $e');
    }

    _missCount++;
    return null;
  }

  /// Move cache entry to front (LRU)
  void _moveToFront(String key) {
    final value = _memoryCache.remove(key);
    if (value != null) {
      _memoryCache[key] = value;
    }
  }

  /// Perform memory cache cleanup (LRU eviction)
  Future<void> _performMemoryCleanup() async {
    if (_memoryCache.length <= _maxMemoryCacheSize) return;

    final entriesToRemove = _memoryCache.length - _maxMemoryCacheSize;
    final keysToRemove = _memoryCache.keys.take(entriesToRemove).toList();

    for (final key in keysToRemove) {
      _memoryCache.remove(key);
    }

    debugPrint('🧹 Memory cache cleanup: removed $entriesToRemove entries');
  }

  /// Perform comprehensive cleanup
  Future<void> _performCleanup() async {
    await clearExpiredEntries();
    await _performMemoryCleanup();
  }

  /// Load cache statistics from preferences
  Future<void> _loadCacheStats() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final statsJson = prefs.getString(_prefsKey);

      if (statsJson != null) {
        final stats = json.decode(statsJson) as Map<String, dynamic>;
        _hitCount = stats['hit_count'] ?? 0;
        _missCount = stats['miss_count'] ?? 0;
        _writeCount = stats['write_count'] ?? 0;
      }
    } catch (e) {
      debugPrint('💥 Error loading cache stats: $e');
    }
  }

  /// Save cache statistics to preferences
  Future<void> _saveCacheStats() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final stats = {
        'hit_count': _hitCount,
        'miss_count': _missCount,
        'write_count': _writeCount,
        'last_save': DateTime.now().toIso8601String(),
      };

      await prefs.setString(_prefsKey, json.encode(stats));
    } catch (e) {
      debugPrint('💥 Error saving cache stats: $e');
    }
  }

  /// Estimate memory usage of cache
  int _estimateMemoryUsage() {
    int totalSize = 0;

    for (final entry in _memoryCache.values) {
      totalSize += json.encode(entry.toMap()).length * 2; // Rough estimate
    }

    return totalSize;
  }

  /// Dispose cache service
  Future<void> dispose() async {
    debugPrint('🧹 Disposing Market Data Cache Service');

    await _saveCacheStats();
    await _cacheBox?.close();
    await _metadataBox?.close();

    _memoryCache.clear();
    _isInitialized = false;
  }
}

/// Cached data wrapper
class CachedData {
  final String key;
  final Map<String, dynamic> data;
  final int timestamp;
  final int ttlMs;
  final CacheDataType dataType;

  CachedData({
    required this.key,
    required this.data,
    required this.timestamp,
    required this.ttlMs,
    required this.dataType,
  });

  /// Check if data is expired
  bool get isExpired {
    final now = DateTime.now().millisecondsSinceEpoch;
    return now > timestamp + ttlMs;
  }

  /// Get age in seconds
  int get ageSeconds {
    final now = DateTime.now().millisecondsSinceEpoch;
    return (now - timestamp) ~/ 1000;
  }

  /// Convert to map for serialization
  Map<String, dynamic> toMap() => {
    'key': key,
    'data': data,
    'timestamp': timestamp,
    'ttl_ms': ttlMs,
    'data_type': dataType.name,
  };

  /// Create from map
  factory CachedData.fromMap(Map<String, dynamic> map) {
    return CachedData(
      key: map['key'],
      data: Map<String, dynamic>.from(map['data']),
      timestamp: map['timestamp'],
      ttlMs: map['ttl_ms'],
      dataType: CacheDataType.values.firstWhere(
        (type) => type.name == map['data_type'],
        orElse: () => CacheDataType.priceData,
      ),
    );
  }
}

/// Cache data types
enum CacheDataType { priceData, marketStats, historicalData }

/// Singleton instance for global access
final marketDataCacheService = MarketDataCacheService();

/// Helper extension for unawaited futures
extension FutureExtension on Future {
  void get unawaited => {};
}
