import 'dart:convert';
import 'dart:developer';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart';
import 'package:crypto/crypto.dart';
import 'secure_storage_service.dart';

/// Production-ready service for managing Extended Exchange API keys and user accounts
class ExtendedExchangeApiService {
  static const String _baseUrl = 'http://localhost:3001/proxy/extended-exchange';
  static const String _userRegistrationEndpoint = '/api/v1/users/register';
  static const String _apiKeyValidationEndpoint = '/api/v1/users/validate';
  static const String _apiKeyStatusEndpoint = '/api/v1/users/status';
  
  static String get baseUrl => _baseUrl;
  
  /// Create a new user account with Extended Exchange and get unique API key
  static Future<String> createUserAccount(String starknetAddress) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl$_userRegistrationEndpoint'),
        headers: {
          'Content-Type': 'application/json',
          'X-App-Integration': 'astratrade',
        },
        body: jsonEncode({
          'starknet_address': starknetAddress,
          'user_type': 'individual',
          'app_integration': 'astratrade',
          'environment': kDebugMode ? 'testnet' : 'mainnet',
        }),
      );

      if (response.statusCode == 201 || response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final apiKey = data['api_key'];
        final accountId = data['account_id'];
        
        if (apiKey == null || apiKey.isEmpty) {
          throw Exception('Invalid API key received from Extended Exchange');
        }
        
        // Store API key securely with wallet address as identifier
        await SecureStorageService.instance.storeTradingCredentials(
          apiKey: apiKey,
          apiSecret: data['api_secret'] ?? '',
          passphrase: data['passphrase'],
        );
        
        // Store account metadata
        await SecureStorageService.instance.storeUserData({
          'extended_exchange_account_id': accountId,
          'starknet_address': starknetAddress,
          'api_key_created': DateTime.now().toIso8601String(),
        });
        
        debugPrint('✅ Extended Exchange account created successfully');
        return apiKey;
      } else {
        final error = jsonDecode(response.body);
        throw Exception('Extended Exchange registration failed: ${error['message'] ?? response.statusCode}');
      }
    } on http.ClientException catch (e) {
      log('❌ Network error creating Extended Exchange account: $e');
      throw Exception('Network connection failed. Please check your internet connection.');
    } catch (e) {
      log('❌ Failed to create Extended Exchange account: $e');
      throw Exception('Account creation failed: $e');
    }
  }

  /// Get stored API key for a specific wallet address
  static Future<String?> getStoredApiKey(String starknetAddress) async {
    try {
      final credentials = await SecureStorageService.instance.getTradingCredentials();
      return credentials?['api_key'];
    } catch (e) {
      log('❌ Failed to retrieve API key: $e');
      return null;
    }
  }

  /// Validate if an API key is active and working
  static Future<bool> validateApiKey(String apiKey) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl$_apiKeyValidationEndpoint'),
        headers: {
          'Authorization': 'Bearer $apiKey',
          'X-App-Integration': 'astratrade',
        },
      );

      return response.statusCode == 200;
    } catch (e) {
      log('❌ API key validation failed: $e');
      return false;
    }
  }

  /// Get API key usage statistics for a user
  static Future<Map<String, dynamic>> getApiKeyUsage(String apiKey) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl$_apiKeyStatusEndpoint'),
        headers: {
          'Authorization': 'Bearer $apiKey',
          'X-App-Integration': 'astratrade',
        },
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to get usage statistics: ${response.statusCode}');
      }
    } catch (e) {
      log('❌ Failed to get API key usage: $e');
      return {
        'requests_today': 0,
        'requests_limit': 1000,
        'last_used': DateTime.now().toIso8601String(),
        'is_active': true,
        'error': e.toString(),
      };
    }
  }

  /// Ensure user has valid API key, create if needed
  static Future<String> ensureUserApiKey(String starknetAddress) async {
    try {
      // Check if we already have a stored API key
      final existingApiKey = await getStoredApiKey(starknetAddress);
      if (existingApiKey != null) {
        // Validate existing key
        final isValid = await validateApiKey(existingApiKey);
        if (isValid) {
          debugPrint('✅ Using existing valid API key');
          return existingApiKey;
        } else {
          debugPrint('⚠️ Existing API key invalid, creating new one');
        }
      }

      // Create new API key
      debugPrint('🔄 Creating new Extended Exchange account...');
      return await createUserAccount(starknetAddress);
    } catch (e) {
      log('❌ Failed to ensure user API key: $e');
      throw Exception('Failed to setup trading account: $e');
    }
  }

  /// Generate API key specifically for real trading (with user feedback)
  /// This is called when user initiates their first real trade
  static Future<String> generateApiKeyForTrading(String starknetAddress) async {
    try {
      debugPrint('🚀 Generating API key for real trading...');
      
      // Check if we already have a valid API key
      final existingApiKey = await getStoredApiKey(starknetAddress);
      if (existingApiKey != null) {
        final isValid = await validateApiKey(existingApiKey);
        if (isValid) {
          debugPrint('✅ Using existing valid API key for trading');
          return existingApiKey;
        }
      }
      
      // Generate new API key for trading
      debugPrint('⚡ Creating new Extended Exchange account for trading...');
      final apiKey = await ensureUserApiKey(starknetAddress);
      
      debugPrint('✅ API key generated successfully for real trading');
      return apiKey;
    } catch (e) {
      log('❌ Failed to generate API key for trading: $e');
      throw TradingSetupException('Failed to setup trading account: $e');
    }
  }

  /// Clear API key for specific wallet (logout/cleanup)
  static Future<void> clearApiKey(String starknetAddress) async {
    try {
      await SecureStorageService.instance.clearKey('trading_credentials');
      debugPrint('✅ API key cleared for wallet: ${starknetAddress.substring(0, 10)}...');
    } catch (e) {
      log('❌ Failed to clear API key: $e');
    }
  }

  // ========================================
  // EXTENDED API TRADING ENDPOINTS
  // ========================================

  /// Place a perpetual order via Extended Exchange API
  static Future<Map<String, dynamic>> placePerpetualOrder({
    required String apiKey,
    required String symbol,
    required double amount,
    required String side, // 'BUY' or 'SELL'
    required String orderType, // 'MARKET' or 'LIMIT'
    double? price,
    required String starkSignature,
  }) async {
    try {
      final orderData = {
        'symbol': symbol,
        'amount': amount.toString(),
        'side': side.toUpperCase(),
        'type': orderType.toUpperCase(),
        if (price != null) 'price': price.toString(),
        'timestamp': DateTime.now().millisecondsSinceEpoch,
      };

      final response = await retryApiCall(() async {
        return await http.post(
          Uri.parse('$baseUrl/api/v1/orders/perpetual'),
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer $apiKey',
            'X-App-Integration': 'astratrade',
            'X-Stark-Signature': starkSignature,
          },
          body: jsonEncode(orderData),
        ).timeout(ExtendedExchangeConfig.requestTimeout);
      });

      if (response.statusCode == 201 || response.statusCode == 200) {
        final data = jsonDecode(response.body);
        debugPrint('✅ Order placed successfully: ${data['order_id']}');
        return data;
      } else {
        final error = jsonDecode(response.body);
        throw ExtendedExchangeException(
          'Order placement failed: ${error['message'] ?? 'Unknown error'}',
          statusCode: response.statusCode,
          errorCode: error['error_code'],
        );
      }
    } catch (e) {
      log('❌ Failed to place perpetual order: $e');
      rethrow;
    }
  }

  /// Get position for a specific symbol
  static Future<Map<String, dynamic>> getPosition({
    required String apiKey,
    required String symbol,
  }) async {
    try {
      final response = await retryApiCall(() async {
        return await http.get(
          Uri.parse('$baseUrl/api/v1/positions/$symbol'),
          headers: {
            'Authorization': 'Bearer $apiKey',
            'X-App-Integration': 'astratrade',
          },
        ).timeout(ExtendedExchangeConfig.requestTimeout);
      });

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else if (response.statusCode == 404) {
        // No position exists for this symbol
        return {
          'symbol': symbol,
          'size': 0.0,
          'unrealized_pnl': 0.0,
          'entry_price': null,
          'mark_price': null,
          'is_open': false,
        };
      } else {
        final error = jsonDecode(response.body);
        throw ExtendedExchangeException(
          'Failed to get position: ${error['message'] ?? 'Unknown error'}',
          statusCode: response.statusCode,
        );
      }
    } catch (e) {
      log('❌ Failed to get position: $e');
      rethrow;
    }
  }

  /// Get all open positions
  static Future<List<Map<String, dynamic>>> getAllPositions({
    required String apiKey,
  }) async {
    try {
      final response = await retryApiCall(() async {
        return await http.get(
          Uri.parse('$baseUrl/api/v1/positions'),
          headers: {
            'Authorization': 'Bearer $apiKey',
            'X-App-Integration': 'astratrade',
          },
        ).timeout(ExtendedExchangeConfig.requestTimeout);
      });

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return List<Map<String, dynamic>>.from(data['positions'] ?? []);
      } else {
        final error = jsonDecode(response.body);
        throw ExtendedExchangeException(
          'Failed to get positions: ${error['message'] ?? 'Unknown error'}',
          statusCode: response.statusCode,
        );
      }
    } catch (e) {
      log('❌ Failed to get positions: $e');
      return [];
    }
  }

  /// Get account balance and margin information
  static Future<Map<String, dynamic>> getAccountBalance({
    required String apiKey,
  }) async {
    try {
      final response = await retryApiCall(() async {
        return await http.get(
          Uri.parse('$baseUrl/api/v1/account/balance'),
          headers: {
            'Authorization': 'Bearer $apiKey',
            'X-App-Integration': 'astratrade',
          },
        ).timeout(ExtendedExchangeConfig.requestTimeout);
      });

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        final error = jsonDecode(response.body);
        throw ExtendedExchangeException(
          'Failed to get account balance: ${error['message'] ?? 'Unknown error'}',
          statusCode: response.statusCode,
        );
      }
    } catch (e) {
      log('❌ Failed to get account balance: $e');
      rethrow;
    }
  }

  /// Get order status and details
  static Future<Map<String, dynamic>> getOrderStatus({
    required String apiKey,
    required String orderId,
  }) async {
    try {
      final response = await retryApiCall(() async {
        return await http.get(
          Uri.parse('$baseUrl/api/v1/orders/$orderId'),
          headers: {
            'Authorization': 'Bearer $apiKey',
            'X-App-Integration': 'astratrade',
          },
        ).timeout(ExtendedExchangeConfig.requestTimeout);
      });

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        final error = jsonDecode(response.body);
        throw ExtendedExchangeException(
          'Failed to get order status: ${error['message'] ?? 'Unknown error'}',
          statusCode: response.statusCode,
        );
      }
    } catch (e) {
      log('❌ Failed to get order status: $e');
      rethrow;
    }
  }

  /// Cancel an order
  static Future<Map<String, dynamic>> cancelOrder({
    required String apiKey,
    required String orderId,
    required String starkSignature,
  }) async {
    try {
      final response = await retryApiCall(() async {
        return await http.delete(
          Uri.parse('$baseUrl/api/v1/orders/$orderId'),
          headers: {
            'Authorization': 'Bearer $apiKey',
            'X-App-Integration': 'astratrade',
            'X-Stark-Signature': starkSignature,
          },
        ).timeout(ExtendedExchangeConfig.requestTimeout);
      });

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        debugPrint('✅ Order cancelled successfully: $orderId');
        return data;
      } else {
        final error = jsonDecode(response.body);
        throw ExtendedExchangeException(
          'Order cancellation failed: ${error['message'] ?? 'Unknown error'}',
          statusCode: response.statusCode,
        );
      }
    } catch (e) {
      log('❌ Failed to cancel order: $e');
      rethrow;
    }
  }

  /// Get market data for a symbol
  static Future<Map<String, dynamic>> getMarketData({
    required String symbol,
  }) async {
    try {
      final response = await retryApiCall(() async {
        return await http.get(
          Uri.parse('$baseUrl/api/v1/market/ticker/$symbol'),
          headers: {
            'X-App-Integration': 'astratrade',
          },
        ).timeout(ExtendedExchangeConfig.requestTimeout);
      });

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        final error = jsonDecode(response.body);
        throw ExtendedExchangeException(
          'Failed to get market data: ${error['message'] ?? 'Unknown error'}',
          statusCode: response.statusCode,
        );
      }
    } catch (e) {
      log('❌ Failed to get market data: $e');
      rethrow;
    }
  }

  /// Get available trading symbols
  static Future<List<String>> getAvailableSymbols() async {
    try {
      final response = await retryApiCall(() async {
        return await http.get(
          Uri.parse('$baseUrl/api/v1/market/symbols'),
          headers: {
            'X-App-Integration': 'astratrade',
          },
        ).timeout(ExtendedExchangeConfig.requestTimeout);
      });

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return List<String>.from(data['symbols'] ?? []);
      } else {
        final error = jsonDecode(response.body);
        throw ExtendedExchangeException(
          'Failed to get symbols: ${error['message'] ?? 'Unknown error'}',
          statusCode: response.statusCode,
        );
      }
    } catch (e) {
      log('❌ Failed to get available symbols: $e');
      // Return default symbols if API fails
      return ['BTC-USD', 'ETH-USD', 'SOL-USD', 'AVAX-USD'];
    }
  }

  /// Get account status and trading limits
  static Future<Map<String, dynamic>> getAccountStatus(String apiKey) async {
    try {
      final usage = await getApiKeyUsage(apiKey);
      return {
        'is_active': usage['is_active'] ?? false,
        'daily_requests': usage['requests_today'] ?? 0,
        'daily_limit': usage['requests_limit'] ?? 1000,
        'remaining_requests': (usage['requests_limit'] ?? 1000) - (usage['requests_today'] ?? 0),
        'last_activity': usage['last_used'],
      };
    } catch (e) {
      log('❌ Failed to get account status: $e');
      return {
        'is_active': false,
        'error': e.toString(),
      };
    }
  }

  /// Generate deterministic API key for testing/demo purposes
  /// IMPORTANT: This is for TESTING ONLY - use createUserAccount for production
  @Deprecated('Use createUserAccount for production API key generation')
  static String generateDeterministicApiKey(String starknetAddress) {
    // TESTING ONLY: Use the provided test key for all testing scenarios
    // This allows testing real trading orders with the shared test account
    return const String.fromEnvironment(
      'EXTENDED_EXCHANGE_API_KEY',
      defaultValue: '', // Set via environment variable
    );
  }

  /// Check if Extended Exchange API is available
  static Future<bool> isServiceAvailable() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/health'),
      ).timeout(const Duration(seconds: 5));
      return response.statusCode == 200;
    } catch (e) {
      log('❌ Extended Exchange service unavailable: $e');
      return false;
    }
  }

  /// Retry logic for API calls
  static Future<T> retryApiCall<T>(
    Future<T> Function() apiCall, {
    int maxRetries = 3,
    Duration delay = const Duration(seconds: 1),
  }) async {
    int attempt = 0;
    while (attempt < maxRetries) {
      try {
        return await apiCall();
      } catch (e) {
        attempt++;
        if (attempt >= maxRetries) {
          throw Exception('Max retries exceeded: $e');
        }
        debugPrint('🔄 Retry attempt $attempt/$maxRetries after ${delay.inSeconds}s');
        await Future.delayed(delay * attempt);
      }
    }
    throw Exception('Retry failed');
  }
}

/// Configuration for Extended Exchange API
class ExtendedExchangeConfig {
  static const bool enableRetry = true;
  static const int maxRetries = 3;
  static const Duration requestTimeout = Duration(seconds: 30);
  static const Duration retryDelay = Duration(seconds: 1);
  
  /// Check if we're running in demo mode
  static bool get isDemoMode => kDebugMode && 
      ExtendedExchangeApiService.baseUrl.contains('testnet');
  
  /// Get appropriate API endpoint based on environment
  static String getApiEndpoint(String endpoint) {
    return '${ExtendedExchangeApiService.baseUrl}$endpoint';
  }
}

/// Exception thrown by Extended Exchange API operations
class ExtendedExchangeException implements Exception {
  final String message;
  final int? statusCode;
  final String? errorCode;
  
  ExtendedExchangeException(this.message, {this.statusCode, this.errorCode});
  
  @override
  String toString() {
    return 'ExtendedExchangeException: $message' +
           (statusCode != null ? ' (Status: $statusCode)' : '') +
           (errorCode != null ? ' (Code: $errorCode)' : '');
  }
}

/// Exception thrown during trading setup operations
class TradingSetupException implements Exception {
  final String message;
  
  TradingSetupException(this.message);
  
  @override
  String toString() => 'TradingSetupException: $message';
}