import 'dart:convert';
import 'dart:developer';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart';
import 'package:astratrade_app/services/secure_storage_service.dart';
import 'package:astratrade_app/services/extended_exchange_onboarding_service.dart';
import 'package:astratrade_app/services/extended_exchange_signature_service.dart';
import 'package:astratrade_app/services/extended_exchange_hmac_service.dart';
import 'package:astratrade_app/middleware/extended_exchange_auth_middleware.dart';
import 'package:astratrade_app/models/extended_exchange_onboarding_models.dart';

/// Production-ready service for managing Extended Exchange API keys and user accounts
class ExtendedExchangeApiService {
  static const String _baseUrl =
      'http://localhost:3001/proxy/extended-exchange';

  static String get baseUrl => _baseUrl;

  /// Save user's Extended Exchange API key
  static Future<void> saveUserApiKey(
    String apiKey, {
    String? apiSecret,
    String? passphrase,
  }) async {
    try {
      // Store API key securely
      await SecureStorageService.instance.storeTradingCredentials(
        apiKey: apiKey,
        apiSecret: apiSecret ?? '',
        passphrase: passphrase,
      );

      debugPrint('✅ Extended Exchange API key saved successfully');
    } catch (e) {
      log('❌ Failed to save Extended Exchange API key: $e');
      throw Exception('Failed to save API key: $e');
    }
  }

  /// Get stored API key
  static Future<String?> getStoredApiKey() async {
    try {
      final credentials = await SecureStorageService.instance
          .getTradingCredentials();
      return credentials?['api_key'];
    } catch (e) {
      log('❌ Failed to retrieve API key: $e');
      return null;
    }
  }

  /// Validate if an API key is active and working by making a real API call
  static Future<bool> validateApiKey(String apiKey) async {
    try {
      // Make a simple authenticated request to verify the API key
      final response = await http.get(
        Uri.parse('$baseUrl/api/v1/account/balance'), // Using a real endpoint
        headers: {
          'Authorization': 'Bearer $apiKey',
          'X-App-Integration': 'astratrade',
        },
      );

      // If we get a 200 or 403 (valid key but no permission), the key is valid
      // If we get 401, the key is invalid
      return response.statusCode == 200 || response.statusCode == 403;
    } catch (e) {
      log('❌ API key validation failed: $e');
      return false;
    }
  }

  /// Get API key usage statistics (placeholder - would need Extended Exchange to provide this)
  static Future<Map<String, dynamic>> getApiKeyUsage(String apiKey) async {
    try {
      // For now, we'll return mock data since Extended Exchange doesn't provide this endpoint
      // In a real implementation, you would call the actual Extended Exchange endpoint
      return {
        'requests_today': 0,
        'requests_limit': 1000,
        'last_used': DateTime.now().toIso8601String(),
        'is_active': true,
      };
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

  /// Ensure user has valid API key, prompt for entry if needed
  static Future<String> ensureUserApiKey() async {
    try {
      // Check if we already have a stored API key
      final existingApiKey = await getStoredApiKey();
      if (existingApiKey != null) {
        // Validate existing key
        final isValid = await validateApiKey(existingApiKey);
        if (isValid) {
          debugPrint('✅ Using existing valid API key');
          return existingApiKey;
        } else {
          debugPrint('⚠️ Existing API key invalid, please enter a new one');
          throw Exception('Invalid API key stored. Please enter a new one.');
        }
      }

      // If no API key is stored, throw an exception to prompt user entry
      throw Exception(
        'No API key found. Please enter your Extended Exchange API key.',
      );
    } catch (e) {
      log('❌ Failed to ensure user API key: $e');
      throw Exception('API key setup required: $e');
    }
  }

  /// Prompt user to enter API key for real trading
  static Future<String> promptForApiKey() async {
    try {
      debugPrint('🚀 Please enter your Extended Exchange API key...');
      // This would be implemented in the UI layer to prompt the user
      // For now, we'll throw an exception to indicate user action is needed
      throw Exception('User API key entry required');
    } catch (e) {
      log('❌ Failed to prompt for API key: $e');
      throw Exception('Failed to setup trading account: ${e.toString()}');
    }
  }

  /// Clear API key (logout/cleanup)
  static Future<void> clearApiKey() async {
    try {
      await SecureStorageService.instance.clearKey('trading_credentials');
      debugPrint('✅ Extended Exchange API key cleared');
    } catch (e) {
      log('❌ Failed to clear API key: $e');
    }
  }

  // ========================================
  // ENHANCED ONBOARDING INTEGRATION
  // ========================================

  /// Create a full Extended Exchange account with onboarding
  /// This integrates with the bounty submission onboarding flow
  static Future<OnboardedAccount> createUserAccount({
    required String l1PrivateKey,
    required String l1Address,
    String? referralCode,
  }) async {
    try {
      debugPrint(
        '🚀 Creating Extended Exchange account with full onboarding...',
      );

      // Use the new onboarding service to create the account
      final onboardedAccount =
          await ExtendedExchangeOnboardingService.onboardAccount(
            l1PrivateKey: l1PrivateKey,
            l1Address: l1Address,
            referralCode: referralCode,
          );

      // Store the API key securely
      if (onboardedAccount.tradingApiKey != null) {
        await saveUserApiKey(onboardedAccount.tradingApiKey!);
        debugPrint('✅ Trading API key saved securely');
      }

      // Store the L2 credentials securely
      await _storeL2Credentials(onboardedAccount);

      debugPrint('✅ Extended Exchange account created successfully');
      debugPrint('   Vault ID: ${onboardedAccount.l2Vault}');
      debugPrint('   Account ID: ${onboardedAccount.account.id}');

      return onboardedAccount;
    } catch (e) {
      log('❌ Failed to create user account: $e');
      if (e is OnboardingException) {
        rethrow;
      } else {
        throw TradingSetupException('Account creation failed: $e');
      }
    }
  }

  /// Store L2 credentials securely
  static Future<void> _storeL2Credentials(OnboardedAccount account) async {
    try {
      final l2Data = {
        'l2_private_key': account.l2PrivateKey,
        'l2_public_key': account.l2PublicKey,
        'l2_vault_id': account.l2Vault.toString(),
        'account_id': account.account.id.toString(),
        'account_index': account.account.accountIndex.toString(),
      };

      await SecureStorageService.instance.storeExtendedExchangeCredentials(
        l2Data,
      );
      debugPrint('✅ L2 credentials stored securely');
    } catch (e) {
      log('❌ Failed to store L2 credentials: $e');
      throw TradingSetupException('Failed to store L2 credentials: $e');
    }
  }

  /// Get stored L2 credentials
  static Future<Map<String, String>?> getL2Credentials() async {
    try {
      return await SecureStorageService.instance
          .getExtendedExchangeCredentials();
    } catch (e) {
      log('❌ Failed to retrieve L2 credentials: $e');
      return null;
    }
  }

  /// Generate order signature for trading
  static Map<String, dynamic> generateOrderSignature({
    required String privateKey,
    required String market,
    required String side,
    required String quantity,
    required String price,
    required int vaultId,
    required int nonce,
    required int expiry,
  }) {
    try {
      return ExtendedExchangeSignatureService.generateOrderSignature(
        privateKey: privateKey,
        market: market,
        side: side,
        quantity: quantity,
        price: price,
        vaultId: vaultId,
        nonce: nonce,
        expiry: expiry,
      );
    } catch (e) {
      log('❌ Failed to generate order signature: $e');
      throw TradingSetupException('Signature generation failed: $e');
    }
  }

  /// Get supported trading markets
  static List<String> getSupportedMarkets() {
    return ExtendedExchangeSignatureService.getSupportedMarkets();
  }

  /// Test the complete onboarding flow
  static Future<bool> testOnboardingFlow() async {
    try {
      debugPrint('🧪 Testing Extended Exchange onboarding flow...');
      final result = await ExtendedExchangeOnboardingService.testOnboarding();
      if (result) {
        debugPrint('✅ Onboarding flow test passed');
      } else {
        debugPrint('❌ Onboarding flow test failed');
      }
      return result;
    } catch (e) {
      log('❌ Onboarding flow test error: $e');
      return false;
    }
  }

  // ========================================
  // HMAC AUTHENTICATION INTEGRATION
  // ========================================

  /// Setup HMAC authentication credentials
  static Future<void> setupHmacAuthentication({
    required String apiKey,
    required String apiSecret,
    String environment = 'sepolia',
  }) async {
    try {
      debugPrint('🔐 Setting up HMAC authentication...');

      // Store HMAC credentials securely
      await SecureStorageService.instance.storeHmacCredentials(
        apiKey: apiKey,
        apiSecret: apiSecret,
        environment: environment,
      );

      // Also store in legacy format for backward compatibility
      await SecureStorageService.instance.storeTradingCredentials(
        apiKey: apiKey,
        apiSecret: apiSecret,
      );

      debugPrint('✅ HMAC authentication setup completed');
      debugPrint('   Environment: $environment');
      debugPrint('   API Key: ${apiKey.substring(0, 8)}...');
    } catch (e) {
      log('❌ Failed to setup HMAC authentication: $e');
      throw TradingSetupException('HMAC authentication setup failed: $e');
    }
  }

  /// Validate HMAC authentication setup
  static Future<bool> validateHmacSetup() async {
    try {
      debugPrint('🧪 Validating HMAC setup...');

      // Check if credentials are stored
      final hasCredentials = await SecureStorageService.instance
          .validateHmacCredentials();
      if (!hasCredentials) {
        debugPrint('❌ No HMAC credentials found');
        return false;
      }

      // Test HMAC service
      final hmacTest = await ExtendedExchangeHmacService.testHmacService();
      if (!hmacTest) {
        debugPrint('❌ HMAC service test failed');
        return false;
      }

      // Test authentication middleware
      final middlewareTest =
          await ExtendedExchangeAuthMiddleware.testMiddleware();
      if (!middlewareTest) {
        debugPrint('❌ Authentication middleware test failed');
        return false;
      }

      // Test credential validation
      final credentialValidation =
          await ExtendedExchangeAuthMiddleware.validateCredentials();

      debugPrint('✅ HMAC setup validation completed');
      debugPrint('   Credentials stored: $hasCredentials');
      debugPrint('   HMAC service: $hmacTest');
      debugPrint('   Middleware: $middlewareTest');
      debugPrint('   API validation: $credentialValidation');

      return hasCredentials && hmacTest && middlewareTest;
    } catch (e) {
      log('❌ HMAC setup validation failed: $e');
      return false;
    }
  }

  /// Get current HMAC authentication status
  static Future<Map<String, dynamic>> getHmacStatus() async {
    try {
      final credentials = await SecureStorageService.instance
          .getHmacCredentials();
      final hasCredentials = credentials != null;

      return {
        'hmac_enabled': hasCredentials,
        'environment': credentials?['environment'] ?? 'unknown',
        'api_key_prefix': hasCredentials
            ? (credentials!['api_key'] as String).substring(0, 8)
            : null,
        'timestamp': credentials?['timestamp'],
        'status': hasCredentials ? 'configured' : 'not_configured',
      };
    } catch (e) {
      log('❌ Failed to get HMAC status: $e');
      return {'hmac_enabled': false, 'status': 'error', 'error': e.toString()};
    }
  }

  // ========================================
  // EXTENDED API TRADING ENDPOINTS
  // ========================================

  /// Place a perpetual order via Extended Exchange API with HMAC authentication
  static Future<Map<String, dynamic>> placePerpetualOrder({
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
        'stark_signature': starkSignature,
      };

      debugPrint('🔄 Placing perpetual order with HMAC auth...');
      debugPrint('   Symbol: $symbol');
      debugPrint('   Side: ${side.toUpperCase()}');
      debugPrint('   Amount: $amount');
      debugPrint('   Type: ${orderType.toUpperCase()}');

      final response = await retryApiCall(() async {
        return await ExtendedExchangeAuthMiddleware.post(
          '$baseUrl/api/v1/orders/perpetual',
          headers: {
            'X-App-Integration': 'astratrade',
            'X-Stark-Signature': starkSignature,
          },
          body: orderData,
          timeout: ExtendedExchangeConfig.requestTimeout,
        );
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

  /// Get position for a specific symbol with HMAC authentication
  static Future<Map<String, dynamic>> getPosition({
    required String symbol,
  }) async {
    try {
      debugPrint('📊 Getting position for $symbol with HMAC auth...');

      final response = await retryApiCall(() async {
        return await ExtendedExchangeAuthMiddleware.get(
          '$baseUrl/api/v1/positions/$symbol',
          headers: {'X-App-Integration': 'astratrade'},
          timeout: ExtendedExchangeConfig.requestTimeout,
        );
      });

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        debugPrint('✅ Position retrieved for $symbol');
        return data;
      } else if (response.statusCode == 404) {
        // No position exists for this symbol
        debugPrint('ℹ️ No position found for $symbol');
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
        return await http
            .get(
              Uri.parse('$baseUrl/api/v1/positions'),
              headers: {
                'Authorization': 'Bearer $apiKey',
                'X-App-Integration': 'astratrade',
              },
            )
            .timeout(ExtendedExchangeConfig.requestTimeout);
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
        return await http
            .get(
              Uri.parse('$baseUrl/api/v1/account/balance'),
              headers: {
                'Authorization': 'Bearer $apiKey',
                'X-App-Integration': 'astratrade',
              },
            )
            .timeout(ExtendedExchangeConfig.requestTimeout);
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
        return await http
            .get(
              Uri.parse('$baseUrl/api/v1/orders/$orderId'),
              headers: {
                'Authorization': 'Bearer $apiKey',
                'X-App-Integration': 'astratrade',
              },
            )
            .timeout(ExtendedExchangeConfig.requestTimeout);
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
        return await http
            .delete(
              Uri.parse('$baseUrl/api/v1/orders/$orderId'),
              headers: {
                'Authorization': 'Bearer $apiKey',
                'X-App-Integration': 'astratrade',
                'X-Stark-Signature': starkSignature,
              },
            )
            .timeout(ExtendedExchangeConfig.requestTimeout);
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
        return await http
            .get(
              Uri.parse('$baseUrl/api/v1/market/ticker/$symbol'),
              headers: {'X-App-Integration': 'astratrade'},
            )
            .timeout(ExtendedExchangeConfig.requestTimeout);
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
        return await http
            .get(
              Uri.parse('$baseUrl/api/v1/market/symbols'),
              headers: {'X-App-Integration': 'astratrade'},
            )
            .timeout(ExtendedExchangeConfig.requestTimeout);
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
        'remaining_requests':
            (usage['requests_limit'] ?? 1000) - (usage['requests_today'] ?? 0),
        'last_activity': usage['last_used'],
      };
    } catch (e) {
      log('❌ Failed to get account status: $e');
      return {'is_active': false, 'error': e.toString()};
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
      final response = await http
          .get(Uri.parse('$baseUrl/health'))
          .timeout(const Duration(seconds: 5));
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
        debugPrint(
          '🔄 Retry attempt $attempt/$maxRetries after ${delay.inSeconds}s',
        );
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
  static bool get isDemoMode =>
      kDebugMode && ExtendedExchangeApiService.baseUrl.contains('testnet');

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
    return 'ExtendedExchangeException: ${message.toString()}' +
        (statusCode != null ? ' (Status: ${statusCode.toString()})' : '') +
        (errorCode != null ? ' (Code: ${errorCode.toString()})' : '');
  }
}

/// Exception thrown during trading setup operations
class TradingSetupException implements Exception {
  final String message;

  TradingSetupException(this.message);

  @override
  String toString() => 'TradingSetupException: ${message.toString()}';
}
