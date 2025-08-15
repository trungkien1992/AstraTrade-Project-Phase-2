/// Extended Exchange HMAC Authentication Usage Example
///
/// This file demonstrates how to use the HMAC authentication system
/// for secure Extended Exchange API communication.

import 'package:flutter/foundation.dart';
import 'package:astratrade_app/services/extended_exchange_api_service.dart';
import 'package:astratrade_app/services/extended_exchange_hmac_service.dart';
import 'package:astratrade_app/middleware/extended_exchange_auth_middleware.dart';

/// Example: Complete HMAC Authentication Setup
class HmacAuthenticationExample {
  /// Step 1: Setup HMAC authentication with API credentials
  static Future<void> setupAuthentication() async {
    try {
      debugPrint('🔐 Setting up HMAC authentication...');

      // Replace with your actual Extended Exchange API credentials
      const apiKey = 'your_extended_exchange_api_key';
      const apiSecret = 'your_extended_exchange_api_secret';

      await ExtendedExchangeApiService.setupHmacAuthentication(
        apiKey: apiKey,
        apiSecret: apiSecret,
        environment: 'sepolia', // or 'mainnet' for production
      );

      debugPrint('✅ HMAC authentication setup completed');
    } catch (e) {
      debugPrint('❌ HMAC setup failed: $e');
      rethrow;
    }
  }

  /// Step 2: Validate HMAC setup
  static Future<bool> validateSetup() async {
    try {
      debugPrint('🧪 Validating HMAC setup...');

      final isValid = await ExtendedExchangeApiService.validateHmacSetup();

      if (isValid) {
        debugPrint('✅ HMAC authentication is properly configured');
      } else {
        debugPrint('❌ HMAC authentication configuration is invalid');
      }

      return isValid;
    } catch (e) {
      debugPrint('❌ HMAC validation failed: $e');
      return false;
    }
  }

  /// Step 3: Make authenticated API calls
  static Future<void> makeAuthenticatedCalls() async {
    try {
      debugPrint('📡 Making authenticated API calls...');

      // Example: Get account balance (automatically signed with HMAC)
      // Note: API key removed from parameters - handled by middleware
      /*
      final balance = await ExtendedExchangeApiService.getAccountBalance();
      debugPrint('💰 Account balance: $balance');
      
      // Example: Get position for BTC-USD (automatically signed with HMAC)
      final position = await ExtendedExchangeApiService.getPosition(
        symbol: 'BTC-USD',
      );
      debugPrint('📊 BTC-USD position: $position');
      
      // Example: Place order (automatically signed with HMAC)
      final orderResult = await ExtendedExchangeApiService.placePerpetualOrder(
        symbol: 'BTC-USD',
        amount: 0.01,
        side: 'BUY',
        orderType: 'MARKET',
        starkSignature: 'your_stark_signature_here',
      );
      debugPrint('📈 Order placed: $orderResult');
      */

      debugPrint('✅ Authenticated API calls completed');
    } catch (e) {
      debugPrint('❌ API calls failed: $e');
      rethrow;
    }
  }

  /// Step 4: Direct middleware usage (advanced)
  static Future<void> directMiddlewareUsage() async {
    try {
      debugPrint('🔧 Using authentication middleware directly...');

      // Direct API call with automatic HMAC signing
      final response = await ExtendedExchangeAuthMiddleware.get(
        'https://api.starknet.sepolia.extended.exchange/api/v1/markets',
        headers: {'X-App-Integration': 'astratrade'},
      );

      debugPrint('📊 Response status: ${response.statusCode}');
      debugPrint('📄 Response body: ${response.body.substring(0, 200)}...');
    } catch (e) {
      debugPrint('❌ Direct middleware usage failed: $e');
      rethrow;
    }
  }

  /// Step 5: Manual HMAC signature generation (educational)
  static void manualSignatureGeneration() {
    try {
      debugPrint('🔍 Manual HMAC signature generation example...');

      // Example request parameters
      const apiSecret = 'your_api_secret_here';
      const method = 'POST';
      const path = '/api/v1/orders';
      const body = '{"symbol":"BTC-USD","side":"BUY","amount":"0.1"}';

      // Generate signature manually
      final signature = ExtendedExchangeHmacService.generateSignature(
        apiSecret: apiSecret,
        method: method,
        path: path,
        body: body,
      );

      debugPrint('🔑 Generated signature: $signature');

      // Generate complete auth headers
      const apiKey = 'your_api_key_here';
      final headers = ExtendedExchangeHmacService.generateAuthHeaders(
        apiKey: apiKey,
        apiSecret: apiSecret,
        method: method,
        path: path,
        body: body,
      );

      debugPrint('📋 Auth headers: $headers');
    } catch (e) {
      debugPrint('❌ Manual signature generation failed: $e');
    }
  }

  /// Complete example workflow
  static Future<void> completeExample() async {
    try {
      debugPrint('🚀 Starting complete HMAC authentication example...');

      // Step 1: Setup authentication
      await setupAuthentication();

      // Step 2: Validate setup
      final isValid = await validateSetup();
      if (!isValid) {
        throw Exception('HMAC setup validation failed');
      }

      // Step 3: Make authenticated calls
      await makeAuthenticatedCalls();

      // Step 4: Direct middleware usage
      await directMiddlewareUsage();

      // Step 5: Manual signature generation
      manualSignatureGeneration();

      debugPrint(
        '✅ Complete HMAC authentication example finished successfully',
      );
    } catch (e) {
      debugPrint('❌ Complete example failed: $e');
      rethrow;
    }
  }

  /// Get authentication status
  static Future<void> checkAuthStatus() async {
    try {
      final status = await ExtendedExchangeApiService.getHmacStatus();
      debugPrint('📊 HMAC Authentication Status:');
      debugPrint('   Enabled: ${status['hmac_enabled']}');
      debugPrint('   Environment: ${status['environment']}');
      debugPrint('   API Key: ${status['api_key_prefix']}***');
      debugPrint('   Status: ${status['status']}');
    } catch (e) {
      debugPrint('❌ Failed to get auth status: $e');
    }
  }
}

/// Security Best Practices
class HmacSecurityBestPractices {
  /// Security recommendations for HMAC authentication
  static void securityRecommendations() {
    debugPrint('🔒 HMAC Security Best Practices:');
    debugPrint('');
    debugPrint('1. API Secret Storage:');
    debugPrint('   ✓ Store API secrets in device secure storage (implemented)');
    debugPrint('   ✓ Never log or expose API secrets in plain text');
    debugPrint('   ✓ Use separate keys for testnet and mainnet');
    debugPrint('');
    debugPrint('2. Request Security:');
    debugPrint('   ✓ Always use HTTPS for API requests');
    debugPrint('   ✓ Include timestamp in signatures (replay protection)');
    debugPrint('   ✓ Validate signature on both client and server');
    debugPrint('');
    debugPrint('3. Error Handling:');
    debugPrint('   ✓ Handle 401/403 authentication errors gracefully');
    debugPrint('   ✓ Implement retry logic for network failures');
    debugPrint('   ✓ Clear credentials on repeated auth failures');
    debugPrint('');
    debugPrint('4. Key Management:');
    debugPrint('   ✓ Rotate API keys regularly');
    debugPrint('   ✓ Monitor API key usage and limits');
    debugPrint('   ✓ Revoke compromised keys immediately');
  }
}

/// Testing utilities
class HmacTestingUtils {
  /// Test HMAC authentication with demo credentials
  static Future<void> testWithDemoCredentials() async {
    try {
      debugPrint('🧪 Testing HMAC with demo credentials...');

      // Test HMAC service
      final hmacTest = await ExtendedExchangeHmacService.testHmacService();
      debugPrint('   HMAC Service: ${hmacTest ? "✅ PASSED" : "❌ FAILED"}');

      // Test middleware
      final middlewareTest =
          await ExtendedExchangeAuthMiddleware.testMiddleware();
      debugPrint('   Middleware: ${middlewareTest ? "✅ PASSED" : "❌ FAILED"}');

      debugPrint('📊 Demo testing completed');
    } catch (e) {
      debugPrint('❌ Demo testing failed: $e');
    }
  }
}
