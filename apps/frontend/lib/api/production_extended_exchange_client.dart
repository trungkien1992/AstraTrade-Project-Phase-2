import 'dart:convert';
import 'dart:typed_data';
import 'package:http/http.dart' as http;
import 'package:crypto/crypto.dart';

/// Production Extended Exchange API Client
/// LIVE TRADING integration with real authentication
class ProductionExtendedExchangeClient {
  static const String baseUrl =
      'https://starknet.sepolia.extended.exchange/api/v1';
  static const Duration timeout = Duration(seconds: 30);

  final String _apiKey;
  final String _apiSecret;
  final http.Client _client;

  ProductionExtendedExchangeClient({
    required String apiKey,
    required String apiSecret,
    http.Client? client,
  }) : _apiKey = apiKey,
       _apiSecret = apiSecret,
       _client = client ?? http.Client();

  /// Generate HMAC signature for authenticated requests
  String _generateSignature(
    String timestamp,
    String method,
    String path,
    String body,
  ) {
    final message = timestamp + method.toUpperCase() + path + body;
    final key = utf8.encode(_apiSecret);
    final messageBytes = utf8.encode(message);
    final hmac = Hmac(sha256, key);
    final digest = hmac.convert(messageBytes);
    return digest.toString();
  }

  /// Build authenticated headers
  Map<String, String> _buildHeaders(String method, String path, String body) {
    final timestamp = (DateTime.now().millisecondsSinceEpoch / 1000)
        .toStringAsFixed(0);
    final signature = _generateSignature(timestamp, method, path, body);

    return {
      'X-Api-Key': _apiKey,
      'X-Timestamp': timestamp,
      'X-Signature': signature,
      'Content-Type': 'application/json',
      'User-Agent': 'AstraTrade-Production/1.0.0',
    };
  }

  /// Execute real trading order
  Future<LiveTradeResult> executeLiveTrade({
    required String symbol,
    required String side, // 'BUY' or 'SELL'
    required double amount,
    String orderType = 'MARKET',
    double? limitPrice,
  }) async {
    final orderData = {
      'market': symbol,
      'side': side,
      'type': orderType,
      'size': amount.toString(),
      if (limitPrice != null) 'price': limitPrice.toString(),
      'time_in_force': 'IOC', // Immediate or Cancel
      'client_order_id': 'astratrade_${DateTime.now().millisecondsSinceEpoch}',
    };

    final body = jsonEncode(orderData);
    final headers = _buildHeaders('POST', '/orders', body);

    try {
      final response = await _client
          .post(Uri.parse('$baseUrl/orders'), headers: headers, body: body)
          .timeout(timeout);

      final responseData = jsonDecode(response.body);

      return LiveTradeResult(
        success: response.statusCode == 200 || response.statusCode == 201,
        orderId: responseData['id']?.toString(),
        status: responseData['status']?.toString() ?? 'UNKNOWN',
        executedAmount:
            double.tryParse(responseData['filled_size']?.toString() ?? '0') ??
            0,
        executedPrice:
            double.tryParse(
              responseData['average_fill_price']?.toString() ?? '0',
            ) ??
            0,
        timestamp: DateTime.now(),
        rawResponse: responseData,
      );
    } catch (e) {
      return LiveTradeResult(
        success: false,
        error: 'Trading execution failed: ${e.toString()}',
        timestamp: DateTime.now(),
      );
    }
  }

  /// Get live market data
  Future<MarketData> getLiveMarketData(String symbol) async {
    try {
      final response = await _client
          .get(
            Uri.parse('$baseUrl/markets/$symbol/ticker'),
            headers: {'User-Agent': 'AstraTrade-Production/1.0.0'},
          )
          .timeout(timeout);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return MarketData.fromJson(data);
      }

      throw Exception('Failed to fetch market data: ${response.statusCode}');
    } catch (e) {
      throw Exception('Market data request failed: ${e.toString()}');
    }
  }

  /// Get account balance and positions
  Future<AccountInfo> getAccountInfo() async {
    final headers = _buildHeaders('GET', '/user/account', '');

    try {
      final response = await _client
          .get(Uri.parse('$baseUrl/user/account'), headers: headers)
          .timeout(timeout);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return AccountInfo.fromJson(data);
      }

      throw Exception('Failed to fetch account info: ${response.statusCode}');
    } catch (e) {
      throw Exception('Account info request failed: ${e.toString()}');
    }
  }

  void dispose() {
    _client.close();
  }
}

/// Live trading result
class LiveTradeResult {
  final bool success;
  final String? orderId;
  final String? status;
  final double executedAmount;
  final double executedPrice;
  final DateTime timestamp;
  final String? error;
  final Map<String, dynamic>? rawResponse;

  LiveTradeResult({
    required this.success,
    this.orderId,
    this.status,
    this.executedAmount = 0.0,
    this.executedPrice = 0.0,
    required this.timestamp,
    this.error,
    this.rawResponse,
  });

  Map<String, dynamic> toJson() => {
    'success': success,
    'order_id': orderId,
    'status': status,
    'executed_amount': executedAmount,
    'executed_price': executedPrice,
    'timestamp': timestamp.toIso8601String(),
    'error': error,
    'raw_response': rawResponse,
  };
}

/// Market data model
class MarketData {
  final String symbol;
  final double lastPrice;
  final double bidPrice;
  final double askPrice;
  final double volume24h;
  final double priceChange24h;

  MarketData({
    required this.symbol,
    required this.lastPrice,
    required this.bidPrice,
    required this.askPrice,
    required this.volume24h,
    required this.priceChange24h,
  });

  factory MarketData.fromJson(Map<String, dynamic> json) => MarketData(
    symbol: json['market'] ?? '',
    lastPrice: double.tryParse(json['last']?.toString() ?? '0') ?? 0,
    bidPrice: double.tryParse(json['bid']?.toString() ?? '0') ?? 0,
    askPrice: double.tryParse(json['ask']?.toString() ?? '0') ?? 0,
    volume24h: double.tryParse(json['volume_24h']?.toString() ?? '0') ?? 0,
    priceChange24h: double.tryParse(json['change_24h']?.toString() ?? '0') ?? 0,
  );
}

/// Account information model
class AccountInfo {
  final String accountId;
  final Map<String, double> balances;
  final List<Position> positions;

  AccountInfo({
    required this.accountId,
    required this.balances,
    required this.positions,
  });

  factory AccountInfo.fromJson(Map<String, dynamic> json) => AccountInfo(
    accountId: json['id']?.toString() ?? '',
    balances:
        (json['balances'] as Map<String, dynamic>?)?.map(
          (key, value) => MapEntry(key, double.tryParse(value.toString()) ?? 0),
        ) ??
        {},
    positions:
        (json['positions'] as List?)
            ?.map((p) => Position.fromJson(p))
            .toList() ??
        [],
  );
}

/// Trading position model
class Position {
  final String market;
  final double size;
  final double entryPrice;
  final double unrealizedPnl;

  Position({
    required this.market,
    required this.size,
    required this.entryPrice,
    required this.unrealizedPnl,
  });

  factory Position.fromJson(Map<String, dynamic> json) => Position(
    market: json['market'] ?? '',
    size: double.tryParse(json['size']?.toString() ?? '0') ?? 0,
    entryPrice: double.tryParse(json['entry_price']?.toString() ?? '0') ?? 0,
    unrealizedPnl:
        double.tryParse(json['unrealized_pnl']?.toString() ?? '0') ?? 0,
  );
}
