import 'dart:developer';
import 'package:flutter/foundation.dart';
import '../models/simple_trade.dart';
import 'extended_exchange_api_service.dart';
import 'stark_signature_service.dart';
import 'secure_storage_service.dart';
import 'unified_wallet_setup_service.dart';

/// High-level trading service that integrates Extended Exchange API with Stark signatures
/// Provides seamless real perpetual trading while maintaining SimpleTrade compatibility
class ExtendedTradingService {
  static const List<String> _defaultSymbols = [
    'BTC-USD', 'ETH-USD', 'SOL-USD', 'AVAX-USD'
  ];
  
  /// Place a real perpetual trade via Extended Exchange API
  static Future<SimpleTrade> placePerpetualTrade({
    required double amount,
    required String direction, // 'BUY' or 'SELL'
    String? symbol,
    String? orderType, // 'MARKET' or 'LIMIT'
    double? price,
  }) async {
    try {
      debugPrint('🚀 Placing real perpetual trade: $amount $direction ${symbol ?? 'BTC-USD'}');
      
      // Get API key and ensure user is set up for trading
      final starknetAddress = await _getUserStarknetAddress();
      final apiKey = await ExtendedExchangeApiService.ensureUserApiKey(starknetAddress);
      
      // Prepare order data
      final orderData = {
        'symbol': symbol ?? 'BTC-USD',
        'amount': amount,
        'side': direction.toUpperCase(),
        'type': orderType ?? 'MARKET',
        if (price != null) 'price': price,
        'timestamp': DateTime.now().millisecondsSinceEpoch,
      };
      
      // Generate Stark signature for the order using mobile-native SDK
      final starkSignature = await UnifiedWalletSetupService.signTransactionForExtendedAPI(
        orderData: orderData,
      );
      debugPrint('✅ Using mobile-native signature generation');
      
      // Place the order via Extended API
      final orderResult = await ExtendedExchangeApiService.placePerpetualOrder(
        apiKey: apiKey,
        symbol: orderData['symbol'] as String,
        amount: orderData['amount'] as double,
        side: orderData['side'] as String,
        orderType: orderData['type'] as String,
        price: orderData['price'] as double?,
        starkSignature: starkSignature,
      );
      
      // Create SimpleTrade from Extended API response
      final trade = SimpleTrade(
        id: orderResult['order_id']?.toString() ?? DateTime.now().millisecondsSinceEpoch.toString(),
        amount: amount,
        direction: direction.toUpperCase(),
        symbol: symbol ?? 'BTC-USD',
        timestamp: DateTime.now(),
        // Extended API specific fields
        extendedOrderId: orderResult['order_id']?.toString(),
        orderStatus: _parseOrderStatus(orderResult['status']),
        fillPrice: orderResult['fill_price']?.toDouble(),
        unrealizedPnL: 0.0, // Will be updated when position is tracked
      );
      
      debugPrint('✅ Real perpetual trade placed: ${trade.id}');
      return trade;
      
    } catch (e) {
      log('❌ Failed to place perpetual trade: $e');
      
      // Return failed trade for UI consistency
      return SimpleTrade(
        id: 'failed_${DateTime.now().millisecondsSinceEpoch}',
        amount: amount,
        direction: direction.toUpperCase(),
        symbol: symbol ?? 'BTC-USD',
        timestamp: DateTime.now(),
        profitLoss: null,
        isCompleted: false,
        orderStatus: OrderStatus.failed,
      );
    }
  }
  
  /// Get position for a symbol and update trade with real P&L
  static Future<SimpleTrade> updateTradeWithPosition(SimpleTrade trade) async {
    try {
      if (trade.extendedOrderId == null) {
        // No Extended order ID, can't track position
        return trade;
      }
      
      final starknetAddress = await _getUserStarknetAddress();
      final apiKey = await ExtendedExchangeApiService.getStoredApiKey(starknetAddress);
      
      if (apiKey == null) {
        log('⚠️ No API key found for position tracking');
        return trade;
      }
      
      // Get position from Extended API
      final position = await ExtendedExchangeApiService.getPosition(
        apiKey: apiKey,
        symbol: trade.symbol,
      );
      
      // Update trade with real position data
      return trade.copyWith(
        profitLoss: position['unrealized_pnl']?.toDouble(),
        unrealizedPnL: position['unrealized_pnl']?.toDouble(),
        isCompleted: !(position['is_open'] ?? false),
        lastUpdate: DateTime.now(),
      );
      
    } catch (e) {
      log('❌ Failed to update trade with position: $e');
      return trade;
    }
  }
  
  /// Get all open positions from Extended API
  static Future<List<Map<String, dynamic>>> getAllPositions() async {
    try {
      final starknetAddress = await _getUserStarknetAddress();
      final apiKey = await ExtendedExchangeApiService.getStoredApiKey(starknetAddress);
      
      if (apiKey == null) {
        return [];
      }
      
      return await ExtendedExchangeApiService.getAllPositions(apiKey: apiKey);
    } catch (e) {
      log('❌ Failed to get all positions: $e');
      return [];
    }
  }
  
  /// Get account balance from Extended API
  static Future<Map<String, dynamic>> getAccountBalance() async {
    try {
      final starknetAddress = await _getUserStarknetAddress();
      final apiKey = await ExtendedExchangeApiService.getStoredApiKey(starknetAddress);
      
      if (apiKey == null) {
        return {
          'total_balance': 0.0,
          'available_balance': 0.0,
          'margin_used': 0.0,
          'error': 'No API key found',
        };
      }
      
      return await ExtendedExchangeApiService.getAccountBalance(apiKey: apiKey);
    } catch (e) {
      log('❌ Failed to get account balance: $e');
      return {
        'total_balance': 0.0,
        'available_balance': 0.0,
        'margin_used': 0.0,
        'error': e.toString(),
      };
    }
  }
  
  /// Cancel an order via Extended API
  static Future<bool> cancelOrder(String orderId) async {
    try {
      final starknetAddress = await _getUserStarknetAddress();
      final apiKey = await ExtendedExchangeApiService.getStoredApiKey(starknetAddress);
      
      if (apiKey == null) {
        return false;
      }
      
      // Generate signature for cancellation
      final cancelSignature = await StarkSignatureService.signAccountOperation(
        operation: 'cancel_order',
        operationData: {
          'order_id': orderId,
          'timestamp': DateTime.now().millisecondsSinceEpoch,
        },
      );
      
      final result = await ExtendedExchangeApiService.cancelOrder(
        apiKey: apiKey,
        orderId: orderId,
        starkSignature: cancelSignature,
      );
      
      return result['success'] == true;
    } catch (e) {
      log('❌ Failed to cancel order: $e');
      return false;
    }
  }
  
  /// Get real-time market data for a symbol
  static Future<Map<String, dynamic>> getMarketData(String symbol) async {
    try {
      return await ExtendedExchangeApiService.getMarketData(symbol: symbol);
    } catch (e) {
      log('❌ Failed to get market data: $e');
      return {
        'symbol': symbol,
        'price': 0.0,
        'change_24h': 0.0,
        'volume_24h': 0.0,
        'error': e.toString(),
      };
    }
  }
  
  /// Get available trading symbols from Extended API
  static Future<List<String>> getAvailableSymbols() async {
    try {
      final symbols = await ExtendedExchangeApiService.getAvailableSymbols();
      return symbols.isNotEmpty ? symbols : _defaultSymbols;
    } catch (e) {
      log('❌ Failed to get available symbols: $e');
      return _defaultSymbols;
    }
  }
  
  /// Check if Extended Exchange API is available
  static Future<bool> isServiceAvailable() async {
    try {
      return await ExtendedExchangeApiService.isServiceAvailable();
    } catch (e) {
      log('❌ Extended service check failed: $e');
      return false;
    }
  }
  
  /// Setup user for real trading (generate API key + Stark keys)
  static Future<Map<String, dynamic>> setupUserForTrading() async {
    try {
      debugPrint('🔧 Setting up user for real trading...');
      
      final starknetAddress = await _getUserStarknetAddress();
      
      // Ensure Stark keys are generated
      final starkKeys = await StarkSignatureService.ensureStarkKeys();
      
      // Generate API key for trading
      final apiKey = await ExtendedExchangeApiService.generateApiKeyForTrading(starknetAddress);
      
      // Validate the setup
      final isValidApi = await ExtendedExchangeApiService.validateApiKey(apiKey);
      final hasStarkKeys = starkKeys['private_key']?.isNotEmpty == true;
      
      debugPrint('✅ Trading setup complete');
      
      return {
        'success': isValidApi && hasStarkKeys,
        'api_key_valid': isValidApi,
        'stark_keys_generated': hasStarkKeys,
        'public_key': starkKeys['public_key']?.substring(0, 16),
      };
    } catch (e) {
      log('❌ Failed to setup user for trading: $e');
      return {
        'success': false,
        'error': e.toString(),
      };
    }
  }
  
  /// Get trading status and capabilities
  static Future<Map<String, dynamic>> getTradingStatus() async {
    try {
      final starknetAddress = await _getUserStarknetAddress();
      final apiKey = await ExtendedExchangeApiService.getStoredApiKey(starknetAddress);
      final hasStarkKeys = await StarkSignatureService.getPrivateKey() != null;
      
      final isServiceUp = await isServiceAvailable();
      final isApiValid = apiKey != null ? await ExtendedExchangeApiService.validateApiKey(apiKey) : false;
      
      return {
        'ready_for_trading': isServiceUp && isApiValid && hasStarkKeys,
        'service_available': isServiceUp,
        'api_key_valid': isApiValid,
        'stark_keys_ready': hasStarkKeys,
        'starknet_address': starknetAddress.substring(0, 16),
      };
    } catch (e) {
      log('❌ Failed to get trading status: $e');
      return {
        'ready_for_trading': false,
        'error': e.toString(),
      };
    }
  }
  
  // ========================================
  // HELPER METHODS
  // ========================================
  
  /// Get user's Starknet address (placeholder for actual wallet integration)
  static Future<String> _getUserStarknetAddress() async {
    try {
      // Try to get from secure storage first
      final storedAddress = await SecureStorageService.instance.getValue('starknet_address');
      if (storedAddress != null && storedAddress.isNotEmpty) {
        return storedAddress;
      }
      
      // Generate a mock address for testing
      // In production, this would come from Starknet.dart wallet
      const mockAddress = '0x1234567890abcdef1234567890abcdef12345678';
      await SecureStorageService.instance.storeValue('starknet_address', mockAddress);
      
      debugPrint('⚠️ Using mock Starknet address for testing');
      return mockAddress;
    } catch (e) {
      log('❌ Failed to get Starknet address: $e');
      // Fallback address
      return '0x1234567890abcdef1234567890abcdef12345678';
    }
  }
  
  /// Parse order status from Extended API response
  static OrderStatus _parseOrderStatus(String? status) {
    switch (status?.toLowerCase()) {
      case 'pending':
        return OrderStatus.pending;
      case 'filled':
        return OrderStatus.filled;
      case 'cancelled':
        return OrderStatus.cancelled;
      case 'failed':
        return OrderStatus.failed;
      case 'partial':
        return OrderStatus.partiallyFilled;
      default:
        return OrderStatus.pending;
    }
  }
}

/// Extended API configuration for trading
class ExtendedTradingConfig {
  static const double minTradeAmount = 1.0; // Minimum $1 trade
  static const double maxTradeAmount = 10000.0; // Maximum $10k trade for MVP
  static const List<String> supportedOrderTypes = ['MARKET', 'LIMIT'];
  static const Duration orderTimeout = Duration(minutes: 5);
  
  /// Get trading limits for user level
  static Map<String, double> getTradingLimits(String userLevel) {
    switch (userLevel.toLowerCase()) {
      case 'beginner':
        return {
          'max_per_trade': 50.0,
          'max_total_exposure': 200.0,
          'daily_trade_limit': 10,
        };
      case 'intermediate':
        return {
          'max_per_trade': 500.0,
          'max_total_exposure': 2000.0,
          'daily_trade_limit': 50,
        };
      case 'advanced':
        return {
          'max_per_trade': 5000.0,
          'max_total_exposure': 20000.0,
          'daily_trade_limit': 100,
        };
      default:
        return {
          'max_per_trade': 10.0,
          'max_total_exposure': 50.0,
          'daily_trade_limit': 5,
        };
    }
  }
}

/// Exception thrown by Extended Trading operations
class ExtendedTradingException implements Exception {
  final String message;
  final String? orderData;
  
  ExtendedTradingException(this.message, {this.orderData});
  
  @override
  String toString() {
    return 'ExtendedTradingException: $message${orderData != null ? ' (Order: $orderData)' : ''}';
  }
}