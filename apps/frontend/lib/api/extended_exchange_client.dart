import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart';

/// Extended Exchange API Client for live trading operations on Starknet Sepolia
/// Handles order placement and trading operations with proper authentication
class ExtendedExchangeClient {
  // Proxy configuration for local development
  static const String baseUrl = 'http://localhost:3001/proxy/extended-exchange/api/v1';
  static const String signingDomain = 'starknet.sepolia.extended.exchange';
  static const Duration defaultTimeout = Duration(seconds: 15);
  
  // Real API Key for live trading
  static const String realApiKey = String.fromEnvironment(
    'EXTENDED_EXCHANGE_API_KEY',
    defaultValue: '', // Set via environment variable
  );

  final http.Client _httpClient;
  final String _apiKey;
  final String _userAgent;

  ExtendedExchangeClient({
    required String apiKey,
    http.Client? httpClient,
    String userAgent = 'AstraTrade-Flutter/1.0.0',
  })  : _apiKey = apiKey,
        _httpClient = httpClient ?? http.Client(),
        _userAgent = userAgent;

  /// Place a real trading order with signed payload
  /// 
  /// This method sends a properly authenticated order request to Extended Exchange
  /// with both API key and Stark signature authentication.
  Future<ExtendedOrderResponse> placeOrder({
    required String market,
    required String side, // 'BUY' or 'SELL'
    required String type, // 'MARKET' or 'LIMIT'
    required String size, // Order size as string
    required String? price, // Price for limit orders
    required Map<String, dynamic> starkSignature, // Stark signature data
    String? clientOrderId,
    bool reduceOnly = false,
    bool postOnly = false,
  }) async {
    final uri = Uri.parse('$baseUrl/orders');
    
    final orderPayload = {
      'market': market,
      'side': side,
      'type': type,
      'size': size,
      if (price != null) 'price': price,
      if (clientOrderId != null) 'clientOrderId': clientOrderId,
      'reduceOnly': reduceOnly,
      'postOnly': postOnly,
      // Stark signature fields (these will be added by signing process)
      'signature': starkSignature,
    };

    try {
      final response = await _httpClient
          .post(
            uri,
            headers: {
              'Content-Type': 'application/json',
              'X-Api-Key': _apiKey,
              'User-Agent': _userAgent,
            },
            body: json.encode(orderPayload),
          )
          .timeout(defaultTimeout);

      if (response.statusCode == 201 || response.statusCode == 200) {
        final Map<String, dynamic> responseData = json.decode(response.body);
        return ExtendedOrderResponse.fromJson(responseData);
      } else {
        throw ExtendedExchangeException(
          'Order placement failed',
          statusCode: response.statusCode,
          details: response.body,
        );
      }
    } catch (e) {
      if (e is ExtendedExchangeException) rethrow;
      throw ExtendedExchangeException(
        'Network error during order placement: ${e.toString()}',
      );
    }
  }

  /// Get account balance information
  Future<ExtendedBalanceResponse> getBalance() async {
    final uri = Uri.parse('$baseUrl/user/balance');
    
    try {
      final response = await _httpClient
          .get(
            uri,
            headers: {
              'X-Api-Key': _apiKey,
              'User-Agent': _userAgent,
            },
          )
          .timeout(defaultTimeout);

      if (response.statusCode == 200) {
        final Map<String, dynamic> responseData = json.decode(response.body);
        return ExtendedBalanceResponse.fromJson(responseData);
      } else {
        throw ExtendedExchangeException(
          'Balance retrieval failed',
          statusCode: response.statusCode,
          details: response.body,
        );
      }
    } catch (e) {
      if (e is ExtendedExchangeException) rethrow;
      throw ExtendedExchangeException(
        'Network error during balance retrieval: ${e.toString()}',
      );
    }
  }

  /// Get current positions
  Future<List<ExtendedPosition>> getPositions() async {
    final uri = Uri.parse('$baseUrl/user/positions');
    
    try {
      final response = await _httpClient
          .get(
            uri,
            headers: {
              'X-Api-Key': _apiKey,
              'User-Agent': _userAgent,
            },
          )
          .timeout(defaultTimeout);

      if (response.statusCode == 200) {
        final Map<String, dynamic> responseData = json.decode(response.body);
        final List<dynamic> positionsData = responseData['data'] ?? [];
        return positionsData
            .map((position) => ExtendedPosition.fromJson(position))
            .toList();
      } else {
        throw ExtendedExchangeException(
          'Positions retrieval failed',
          statusCode: response.statusCode,
          details: response.body,
        );
      }
    } catch (e) {
      if (e is ExtendedExchangeException) rethrow;
      throw ExtendedExchangeException(
        'Network error during positions retrieval: ${e.toString()}',
      );
    }
  }

  /// Get market information for a specific trading pair
  Future<ExtendedMarket> getMarket(String marketName) async {
    final uri = Uri.parse('$baseUrl/info/markets?market=$marketName');
    
    try {
      final response = await _httpClient
          .get(
            uri,
            headers: {
              'X-Api-Key': _apiKey,
              'User-Agent': _userAgent,
              'Content-Type': 'application/json',
            },
          )
          .timeout(defaultTimeout);

      if (response.statusCode == 200) {
        final Map<String, dynamic> responseData = json.decode(response.body);
        if (responseData['status'] == 'OK' && responseData['data'] != null) {
          final List<dynamic> marketsData = responseData['data'];
          if (marketsData.isNotEmpty) {
            return ExtendedMarket.fromJson(marketsData.first);
          } else {
            throw ExtendedExchangeException('Market $marketName not found');
          }
        } else {
          throw ExtendedExchangeException('Invalid response format');
        }
      } else {
        throw ExtendedExchangeException(
          'Market retrieval failed',
          statusCode: response.statusCode,
          details: response.body,
        );
      }
    } catch (e) {
      if (e is ExtendedExchangeException) rethrow;
      throw ExtendedExchangeException(
        'Network error during market retrieval: ${e.toString()}',
      );
    }
  }

  /// Get all available markets with real-time data
  Future<List<ExtendedMarket>> getAllMarkets() async {
    final uri = Uri.parse('$baseUrl/info/markets');
    
    try {
      final response = await _httpClient
          .get(
            uri,
            headers: {
              'X-Api-Key': _apiKey,
              'User-Agent': _userAgent,
              'Content-Type': 'application/json',
            },
          )
          .timeout(defaultTimeout);

      if (response.statusCode == 200) {
        final Map<String, dynamic> responseData = json.decode(response.body);
        if (responseData['status'] == 'OK' && responseData['data'] != null) {
          final List<dynamic> marketsData = responseData['data'];
          return marketsData
              .map((marketData) => ExtendedMarket.fromJson(marketData))
              .toList();
        } else {
          throw ExtendedExchangeException('Invalid response format');
        }
      } else {
        throw ExtendedExchangeException(
          'Markets retrieval failed',
          statusCode: response.statusCode,
          details: response.body,
        );
      }
    } catch (e) {
      if (e is ExtendedExchangeException) rethrow;
      throw ExtendedExchangeException(
        'Network error during markets retrieval: ${e.toString()}',
      );
    }
  }

  /// Health check for Extended Exchange API
  Future<bool> healthCheck() async {
    try {
      final uri = Uri.parse('$baseUrl/info/markets');
      final response = await _httpClient
          .get(
            uri,
            headers: {
              'X-Api-Key': _apiKey,
              'User-Agent': _userAgent,
            },
          )
          .timeout(const Duration(seconds: 5));
      return response.statusCode == 200;
    } catch (e) {
      debugPrint('Extended Exchange health check failed: $e');
      return false;
    }
  }

  /// Get order book for a specific market
  Future<ExtendedOrderBook> getOrderBook(String marketName) async {
    final uri = Uri.parse('$baseUrl/orderbook?market=$marketName');
    try {
      final response = await _httpClient
          .get(
            uri,
            headers: {
              'X-Api-Key': _apiKey,
              'User-Agent': _userAgent,
            },
          )
          .timeout(defaultTimeout);
      if (response.statusCode == 200) {
        final Map<String, dynamic> responseData = json.decode(response.body);
        return ExtendedOrderBook.fromJson(responseData['data']);
      } else {
        throw ExtendedExchangeException(
          'Order book retrieval failed',
          statusCode: response.statusCode,
          details: response.body,
        );
      }
    } catch (e) {
      if (e is ExtendedExchangeException) rethrow;
      throw ExtendedExchangeException(
        'Network error during order book retrieval:  [${e.toString()}]');
    }
  }

  void dispose() {
    _httpClient.close();
  }
} // <-- This closes the ExtendedExchangeClient class

// --- Model and Exception Classes ---

class ExtendedOrderResponse {
  final String status;
  final ExtendedOrderData? data;
  final ExtendedError? error;

  ExtendedOrderResponse({
    required this.status,
    this.data,
    this.error,
  });

  factory ExtendedOrderResponse.fromJson(Map<String, dynamic> json) {
    return ExtendedOrderResponse(
      status: json['status'] ?? '',
      data: json['data'] != null ? ExtendedOrderData.fromJson(json['data']) : null,
      error: json['error'] != null ? ExtendedError.fromJson(json['error']) : null,
    );
  }

  bool get isSuccess => status == 'OK' && error == null;
}

class ExtendedOrderData {
  final String orderId;
  final String clientOrderId;
  final String market;
  final String side;
  final String type;
  final String size;
  final String? price;
  final String status;
  final DateTime createdAt;
  final String? transactionHash;

  ExtendedOrderData({
    required this.orderId,
    required this.clientOrderId,
    required this.market,
    required this.side,
    required this.type,
    required this.size,
    this.price,
    required this.status,
    required this.createdAt,
    this.transactionHash,
  });

  factory ExtendedOrderData.fromJson(Map<String, dynamic> json) {
    return ExtendedOrderData(
      orderId: json['orderId'] ?? '',
      clientOrderId: json['clientOrderId'] ?? '',
      market: json['market'] ?? '',
      side: json['side'] ?? '',
      type: json['type'] ?? '',
      size: json['size'] ?? '',
      price: json['price'],
      status: json['status'] ?? '',
      createdAt: DateTime.fromMillisecondsSinceEpoch(
        (json['createdAt'] ?? 0) * 1000,
      ),
      transactionHash: json['transactionHash'] as String?,
    );
  }
}

class ExtendedBalanceResponse {
  final String status;
  final ExtendedBalanceData? data;
  final ExtendedError? error;

  ExtendedBalanceResponse({
    required this.status,
    this.data,
    this.error,
  });

  factory ExtendedBalanceResponse.fromJson(Map<String, dynamic> json) {
    return ExtendedBalanceResponse(
      status: json['status'] ?? '',
      data: json['data'] != null ? ExtendedBalanceData.fromJson(json['data']) : null,
      error: json['error'] != null ? ExtendedError.fromJson(json['error']) : null,
    );
  }

  bool get isSuccess => status == 'OK' && error == null;
}

class ExtendedBalanceData {
  final String collateralName;
  final String balance;
  final String equity;
  final String availableForTrade;
  final String unrealisedPnl;

  ExtendedBalanceData({
    required this.collateralName,
    required this.balance,
    required this.equity,
    required this.availableForTrade,
    required this.unrealisedPnl,
  });

  factory ExtendedBalanceData.fromJson(Map<String, dynamic> json) {
    return ExtendedBalanceData(
      collateralName: json['collateralName'] ?? '',
      balance: json['balance'] ?? '0',
      equity: json['equity'] ?? '0',
      availableForTrade: json['availableForTrade'] ?? '0',
      unrealisedPnl: json['unrealisedPnl'] ?? '0',
    );
  }
}

class ExtendedPosition {
  final String market;
  final String side;
  final String size;
  final String entryPrice;
  final String markPrice;
  final String unrealisedPnl;

  ExtendedPosition({
    required this.market,
    required this.side,
    required this.size,
    required this.entryPrice,
    required this.markPrice,
    required this.unrealisedPnl,
  });

  factory ExtendedPosition.fromJson(Map<String, dynamic> json) {
    return ExtendedPosition(
      market: json['market'] ?? '',
      side: json['side'] ?? '',
      size: json['size'] ?? '0',
      entryPrice: json['entryPrice'] ?? '0',
      markPrice: json['markPrice'] ?? '0',
      unrealisedPnl: json['unrealisedPnl'] ?? '0',
    );
  }
}

class ExtendedMarket {
  final String name;
  final String baseAsset;
  final String quoteAsset;
  final String tickSize;
  final String stepSize;
  final String minOrderSize;
  final bool isActive;
  final String status;
  final ExtendedMarketStats marketStats;
  final ExtendedTradingConfig tradingConfig;

  ExtendedMarket({
    required this.name,
    required this.baseAsset,
    required this.quoteAsset,
    required this.tickSize,
    required this.stepSize,
    required this.minOrderSize,
    required this.isActive,
    required this.status,
    required this.marketStats,
    required this.tradingConfig,
  });

  factory ExtendedMarket.fromJson(Map<String, dynamic> json) {
    final tradingConfig = json['tradingConfig'] ?? {};
    
    return ExtendedMarket(
      name: json['name'] ?? '',
      baseAsset: json['assetName'] ?? '',
      quoteAsset: json['collateralAssetName'] ?? 'USD',
      tickSize: tradingConfig['minPriceChange']?.toString() ?? '0.01',
      stepSize: tradingConfig['minOrderSizeChange']?.toString() ?? '0.001',
      minOrderSize: tradingConfig['minOrderSize']?.toString() ?? '1',
      isActive: json['active'] ?? false,
      status: json['status'] ?? '',
      marketStats: ExtendedMarketStats.fromJson(json['marketStats'] ?? {}),
      tradingConfig: ExtendedTradingConfig.fromJson(tradingConfig),
    );
  }
}

class ExtendedMarketStats {
  final String lastPrice;
  final String markPrice;
  final String askPrice;
  final String bidPrice;
  final String dailyVolume;
  final String dailyPriceChange;
  final String dailyPriceChangePercentage;
  final String dailyHigh;
  final String dailyLow;
  final String openInterest;

  ExtendedMarketStats({
    required this.lastPrice,
    required this.markPrice,
    required this.askPrice,
    required this.bidPrice,
    required this.dailyVolume,
    required this.dailyPriceChange,
    required this.dailyPriceChangePercentage,
    required this.dailyHigh,
    required this.dailyLow,
    required this.openInterest,
  });

  factory ExtendedMarketStats.fromJson(Map<String, dynamic> json) {
    return ExtendedMarketStats(
      lastPrice: json['lastPrice']?.toString() ?? '0',
      markPrice: json['markPrice']?.toString() ?? '0',
      askPrice: json['askPrice']?.toString() ?? '0',
      bidPrice: json['bidPrice']?.toString() ?? '0',
      dailyVolume: json['dailyVolume']?.toString() ?? '0',
      dailyPriceChange: json['dailyPriceChange']?.toString() ?? '0',
      dailyPriceChangePercentage: json['dailyPriceChangePercentage']?.toString() ?? '0',
      dailyHigh: json['dailyHigh']?.toString() ?? '0',
      dailyLow: json['dailyLow']?.toString() ?? '0',
      openInterest: json['openInterest']?.toString() ?? '0',
    );
  }
}

class ExtendedTradingConfig {
  final String minOrderSize;
  final String minOrderSizeChange;
  final String minPriceChange;
  final String maxLeverage;

  ExtendedTradingConfig({
    required this.minOrderSize,
    required this.minOrderSizeChange,
    required this.minPriceChange,
    required this.maxLeverage,
  });

  factory ExtendedTradingConfig.fromJson(Map<String, dynamic> json) {
    return ExtendedTradingConfig(
      minOrderSize: json['minOrderSize']?.toString() ?? '1',
      minOrderSizeChange: json['minOrderSizeChange']?.toString() ?? '0.001',
      minPriceChange: json['minPriceChange']?.toString() ?? '0.01',
      maxLeverage: json['maxLeverage']?.toString() ?? '1.00',
    );
  }
}

class ExtendedOrderBook {
  final List<OrderBookEntry> bids;
  final List<OrderBookEntry> asks;

  ExtendedOrderBook({required this.bids, required this.asks});

  factory ExtendedOrderBook.fromJson(Map<String, dynamic> json) {
    return ExtendedOrderBook(
      bids: (json['bids'] as List<dynamic>? ?? [])
          .map((e) => OrderBookEntry.fromJson(e))
          .toList(),
      asks: (json['asks'] as List<dynamic>? ?? [])
          .map((e) => OrderBookEntry.fromJson(e))
          .toList(),
    );
  }
}

class OrderBookEntry {
  final String price;
  final String size;

  OrderBookEntry({required this.price, required this.size});

  factory OrderBookEntry.fromJson(Map<String, dynamic> json) {
    return OrderBookEntry(
      price: json['price'] ?? '0',
      size: json['size'] ?? '0',
    );
  }
}

class ExtendedError {
  final int code;
  final String message;

  ExtendedError({
    required this.code,
    required this.message,
  });

  factory ExtendedError.fromJson(Map<String, dynamic> json) {
    return ExtendedError(
      code: json['code'] ?? 0,
      message: json['message'] ?? '',
    );
  }
}

class ExtendedExchangeException implements Exception {
  final String message;
  final int? statusCode;
  final String? details;

  ExtendedExchangeException(
    this.message, {
    this.statusCode,
    this.details,
  });

  @override
  String toString() {
    return 'ExtendedExchangeException: $message${statusCode != null ? ' (Status: $statusCode)' : ''}${details != null ? ' - $details' : ''}';
  }
}