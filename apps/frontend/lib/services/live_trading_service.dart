import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart';
import '../config/contract_config.dart';
import 'starknet_service.dart';
import 'extended_exchange_api_service.dart';
import 'wallet_import_service.dart';

/// Live Trading Service - Connects StarknetService with Extended Exchange
/// This service enables real trading operations with proper Starknet signatures
class LiveTradingService {
  final StarknetService _starknetService;
  final http.Client _httpClient;
  
  LiveTradingService({
    StarknetService? starknetService,
    http.Client? httpClient,
  }) : _starknetService = starknetService ?? StarknetService(useMainnet: false),
       _httpClient = httpClient ?? http.Client();

  /// Initialize both StarknetService and Extended Exchange connectivity
  Future<void> initialize() async {
    await _starknetService.initialize();
    
    // Verify Extended Exchange connectivity
    final isHealthy = await _testExtendedExchangeHealth();
    if (!isHealthy) {
      throw LiveTradingException('Extended Exchange API is not available');
    }
    
    debugPrint('✅ Live Trading Service initialized successfully');
  }

  /// Place a live trading order with full Starknet signature
  Future<LiveTradeResult> placeLiveOrder({
    required String privateKey,
    required String market,
    required String side, // 'BUY' or 'SELL'
    required String type, // 'MARKET' or 'LIMIT' 
    required String size,
    String? price,
    bool reduceOnly = false,
    bool postOnly = false,
  }) async {
    try {
      debugPrint('🚀 Placing live order: $market $side $size ${price != null ? '@$price' : 'MARKET'}');
      
      // 1. Validate wallet can sign
      if (!_starknetService.canSignTradePayload(privateKey)) {
        throw LiveTradingException('Invalid private key for signing');
      }
      
      // 2. Ensure we have Extended Exchange API key for trading
      debugPrint('🔑 Ensuring Extended Exchange API key for real trading...');
      final starknetAddress = await _deriveAddressFromPrivateKey(privateKey);
      await ExtendedExchangeApiService.generateApiKeyForTrading(starknetAddress);
      debugPrint('✅ API key ready for real trading');
      
      // 3. Create signed trading payload using StarknetService
      final signedPayload = await _starknetService.signRealTradePayload(
        privateKey: privateKey,
        market: market,
        side: side,
        type: type,
        size: size,
        price: price,
        reduceOnly: reduceOnly,
        postOnly: postOnly,
      );
      
      debugPrint('✅ Trade payload signed with Starknet ECDSA');
      
      // 4. Submit order to Extended Exchange
      final orderResponse = await _submitOrderToExtendedExchange(signedPayload);
      
      debugPrint('✅ Order submitted to Extended Exchange');
      
      return LiveTradeResult(
        success: true,
        orderId: orderResponse['data']?['orderId'],
        clientOrderId: orderResponse['data']?['clientOrderId'],
        status: orderResponse['data']?['status'] ?? 'SUBMITTED',
        market: market,
        side: side,
        size: size,
        price: price,
        message: 'Order placed successfully',
        transactionHash: orderResponse['data']?['transactionHash'],
      );
      
    } catch (e) {
      debugPrint('❌ Live order placement failed: $e');
      
      return LiveTradeResult(
        success: false,
        market: market,
        side: side,
        size: size,
        price: price,
        message: 'Order failed: ${e.toString()}',
      );
    }
  }

  /// Get account balance and trading information
  Future<LiveAccountInfo> getAccountInfo() async {
    try {
      final response = await _httpClient.get(
        Uri.parse('${ContractConfig.extendedExchangeBaseUrl}/user/balance'),
        headers: {
          'X-Api-Key': ContractConfig.extendedExchangeApiKey,
          'Content-Type': 'application/json',
          'User-Agent': 'AstraTrade-Live/1.0.0',
        },
      ).timeout(Duration(seconds: 15));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        
        return LiveAccountInfo(
          success: true,
          balance: data['data']?['balance'] ?? '0',
          equity: data['data']?['equity'] ?? '0',
          availableForTrade: data['data']?['availableForTrade'] ?? '0',
          unrealisedPnl: data['data']?['unrealisedPnl'] ?? '0',
        );
      } else {
        throw LiveTradingException('Account info request failed: ${response.statusCode}');
      }
    } catch (e) {
      return LiveAccountInfo(
        success: false,
        message: 'Failed to get account info: ${e.toString()}',
      );
    }
  }

  /// Get current positions
  Future<List<LivePosition>> getPositions() async {
    try {
      final response = await _httpClient.get(
        Uri.parse('${ContractConfig.extendedExchangeBaseUrl}/user/positions'),
        headers: {
          'X-Api-Key': ContractConfig.extendedExchangeApiKey,
          'Content-Type': 'application/json',
          'User-Agent': 'AstraTrade-Live/1.0.0',
        },
      ).timeout(Duration(seconds: 15));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final List<dynamic> positionsData = data['data'] ?? [];
        
        return positionsData.map((position) => LivePosition(
          market: position['market'] ?? '',
          side: position['side'] ?? '',
          size: position['size'] ?? '0',
          entryPrice: position['entryPrice'] ?? '0',
          markPrice: position['markPrice'] ?? '0',
          unrealisedPnl: position['unrealisedPnl'] ?? '0',
        )).toList();
      } else {
        throw LiveTradingException('Positions request failed: ${response.statusCode}');
      }
    } catch (e) {
      debugPrint('❌ Failed to get positions: $e');
      return [];
    }
  }

  /// Get available markets for trading
  Future<List<LiveMarket>> getAvailableMarkets() async {
    try {
      final response = await _httpClient.get(
        Uri.parse('${ContractConfig.extendedExchangeBaseUrl}/info/markets'),
        headers: {
          'X-Api-Key': ContractConfig.extendedExchangeApiKey,
          'Content-Type': 'application/json',
          'User-Agent': 'AstraTrade-Live/1.0.0',
        },
      ).timeout(Duration(seconds: 15));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final List<dynamic> marketsData = data['data'] ?? [];
        
        return marketsData.where((market) => market['active'] == true)
            .map((market) => LiveMarket(
              name: market['name'] ?? '',
              baseAsset: market['assetName'] ?? '',
              quoteAsset: market['collateralAssetName'] ?? 'USD',
              lastPrice: market['marketStats']?['lastPrice']?.toString() ?? '0',
              bidPrice: market['marketStats']?['bidPrice']?.toString() ?? '0',
              askPrice: market['marketStats']?['askPrice']?.toString() ?? '0',
              dailyVolume: market['marketStats']?['dailyVolume']?.toString() ?? '0',
              dailyChange: market['marketStats']?['dailyPriceChangePercentage']?.toString() ?? '0',
              minOrderSize: market['tradingConfig']?['minOrderSize']?.toString() ?? '0.001',
              isActive: market['active'] ?? false,
            )).toList();
      } else {
        throw LiveTradingException('Markets request failed: ${response.statusCode}');
      }
    } catch (e) {
      debugPrint('❌ Failed to get markets: $e');
      return [];
    }
  }

  /// Submit signed order to Extended Exchange API
  Future<Map<String, dynamic>> _submitOrderToExtendedExchange(SignedTradePayload signedPayload) async {
    final response = await _httpClient.post(
      Uri.parse('${ContractConfig.extendedExchangeBaseUrl}/orders'),
      headers: {
        'Content-Type': 'application/json',
        'X-Api-Key': ContractConfig.extendedExchangeApiKey,
        'User-Agent': 'AstraTrade-Live/1.0.0',
      },
      body: jsonEncode(signedPayload.toJson()),
    ).timeout(Duration(seconds: 20));

    debugPrint('📡 Extended Exchange response: ${response.statusCode}');
    debugPrint('📡 Response body: ${response.body}');

    if (response.statusCode == 200 || response.statusCode == 201) {
      return jsonDecode(response.body);
    } else {
      throw LiveTradingException(
        'Extended Exchange order failed: ${response.statusCode} - ${response.body}'
      );
    }
  }

  /// Test Extended Exchange API health
  Future<bool> _testExtendedExchangeHealth() async {
    try {
      final response = await _httpClient.get(
        Uri.parse('${ContractConfig.extendedExchangeBaseUrl}/info/markets'),
        headers: {
          'X-Api-Key': ContractConfig.extendedExchangeApiKey,
          'Content-Type': 'application/json',
        },
      ).timeout(Duration(seconds: 10));
      
      return response.statusCode == 200;
    } catch (e) {
      debugPrint('❌ Extended Exchange health check failed: $e');
      return false;
    }
  }

  /// Derive Starknet address from private key
  Future<String> _deriveAddressFromPrivateKey(String privateKey) async {
    try {
      // Use WalletImportService to derive address from private key
      final walletService = WalletImportService();
      final address = await walletService.deriveAddressFromPrivateKey(privateKey);
      if (address != null && address.isNotEmpty) {
        return address;
      }
      throw LiveTradingException('Unable to derive address from private key');
    } catch (e) {
      throw LiveTradingException('Failed to derive address from private key: $e');
    }
  }

  void dispose() {
    _httpClient.close();
  }
}

/// Result of a live trading operation
class LiveTradeResult {
  final bool success;
  final String? orderId;
  final String? clientOrderId;
  final String? status;
  final String market;
  final String side;
  final String size;
  final String? price;
  final String message;
  final String? transactionHash;

  LiveTradeResult({
    required this.success,
    this.orderId,
    this.clientOrderId,
    this.status,
    required this.market,
    required this.side,
    required this.size,
    this.price,
    required this.message,
    this.transactionHash,
  });

  @override
  String toString() {
    return 'LiveTradeResult(success: $success, orderId: $orderId, market: $market, side: $side, size: $size, message: $message)';
  }
}

/// Live account information
class LiveAccountInfo {
  final bool success;
  final String? balance;
  final String? equity;
  final String? availableForTrade;
  final String? unrealisedPnl;
  final String? message;

  LiveAccountInfo({
    required this.success,
    this.balance,
    this.equity,
    this.availableForTrade,
    this.unrealisedPnl,
    this.message,
  });
}

/// Live trading position
class LivePosition {
  final String market;
  final String side;
  final String size;
  final String entryPrice;
  final String markPrice;
  final String unrealisedPnl;

  LivePosition({
    required this.market,
    required this.side,
    required this.size,
    required this.entryPrice,
    required this.markPrice,
    required this.unrealisedPnl,
  });
}

/// Live market information
class LiveMarket {
  final String name;
  final String baseAsset;
  final String quoteAsset;
  final String lastPrice;
  final String bidPrice;
  final String askPrice;
  final String dailyVolume;
  final String dailyChange;
  final String minOrderSize;
  final bool isActive;

  LiveMarket({
    required this.name,
    required this.baseAsset,
    required this.quoteAsset,
    required this.lastPrice,
    required this.bidPrice,
    required this.askPrice,
    required this.dailyVolume,
    required this.dailyChange,
    required this.minOrderSize,
    required this.isActive,
  });
}

/// Exception for live trading operations
class LiveTradingException implements Exception {
  final String message;
  
  LiveTradingException(this.message);
  
  @override
  String toString() => 'LiveTradingException: $message';
}