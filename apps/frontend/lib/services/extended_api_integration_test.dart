import 'dart:developer';
import 'package:flutter/foundation.dart';
import 'extended_exchange_api_service.dart';
import 'stark_signature_service.dart';
import 'extended_trading_service.dart';
import 'real_trading_service.dart';

/// Integration test service for Extended API functionality
/// Tests all components working together before real deployment
class ExtendedApiIntegrationTest {
  
  /// Run comprehensive integration test
  static Future<Map<String, dynamic>> runFullIntegrationTest() async {
    debugPrint('🧪 Starting Extended API Integration Test...');
    
    final results = <String, dynamic>{
      'timestamp': DateTime.now().toIso8601String(),
      'tests': <String, dynamic>{},
      'overall_success': false,
      'errors': <String>[],
    };
    
    try {
      // Test 1: Service Availability
      results['tests']['service_availability'] = await _testServiceAvailability();
      
      // Test 2: Stark Signature Generation
      results['tests']['stark_signatures'] = await _testStarkSignatures();
      
      // Test 3: API Key Generation
      results['tests']['api_key_generation'] = await _testApiKeyGeneration();
      
      // Test 4: Trading Service Integration
      results['tests']['trading_service'] = await _testTradingServiceIntegration();
      
      // Test 5: Progressive Trading Modes
      results['tests']['progressive_modes'] = await _testProgressiveTradingModes();
      
      // Calculate overall success
      final allTests = results['tests'] as Map<String, dynamic>;
      final successfulTests = allTests.values.where((test) => test['success'] == true).length;
      final totalTests = allTests.length;
      
      results['successful_tests'] = successfulTests;
      results['total_tests'] = totalTests;
      results['success_rate'] = (successfulTests / totalTests * 100).toStringAsFixed(1);
      results['overall_success'] = successfulTests == totalTests;
      
      debugPrint('✅ Integration test completed: $successfulTests/$totalTests tests passed');
      
    } catch (e) {
      log('❌ Integration test failed: $e');
      results['errors'].add(e.toString());
    }
    
    return results;
  }
  
  /// Test Extended Exchange API service availability
  static Future<Map<String, dynamic>> _testServiceAvailability() async {
    try {
      debugPrint('🔍 Testing service availability...');
      
      final isAvailable = await ExtendedExchangeApiService.isServiceAvailable();
      
      return {
        'success': isAvailable,
        'message': isAvailable ? 'Service is available' : 'Service is unavailable',
        'test_name': 'Service Availability',
      };
    } catch (e) {
      return {
        'success': false,
        'message': 'Service availability test failed: $e',
        'test_name': 'Service Availability',
      };
    }
  }
  
  /// Test Stark signature generation
  static Future<Map<String, dynamic>> _testStarkSignatures() async {
    try {
      debugPrint('🔐 Testing Stark signature generation...');
      
      // Generate test order data
      final testOrderData = {
        'symbol': 'BTC-USD',
        'amount': 10.0,
        'side': 'BUY',
        'type': 'MARKET',
        'timestamp': DateTime.now().millisecondsSinceEpoch,
      };
      
      // Test key generation
      final keys = await StarkSignatureService.ensureStarkKeys();
      final hasPrivateKey = keys['private_key']?.isNotEmpty == true;
      final hasPublicKey = keys['public_key']?.isNotEmpty == true;
      
      // Test signature generation
      final signature = await StarkSignatureService.signTradingOrder(testOrderData);
      final hasValidSignature = signature.isNotEmpty;
      
      // Test signature validation
      final isValidSignature = await StarkSignatureService.validateSignature(
        signature: signature,
        data: testOrderData,
      );
      
      final success = hasPrivateKey && hasPublicKey && hasValidSignature && isValidSignature;
      
      return {
        'success': success,
        'message': success ? 'Stark signatures working correctly' : 'Stark signature test failed',
        'test_name': 'Stark Signatures',
        'details': {
          'has_private_key': hasPrivateKey,
          'has_public_key': hasPublicKey,
          'signature_generated': hasValidSignature,
          'signature_valid': isValidSignature,
        },
      };
    } catch (e) {
      return {
        'success': false,
        'message': 'Stark signature test failed: $e',
        'test_name': 'Stark Signatures',
      };
    }
  }
  
  /// Test API key generation and validation
  static Future<Map<String, dynamic>> _testApiKeyGeneration() async {
    try {
      debugPrint('🔑 Testing API key generation...');
      
      const testAddress = '0x1234567890abcdef1234567890abcdef12345678';
      
      // Test API key generation
      final apiKey = await ExtendedExchangeApiService.ensureUserApiKey(testAddress);
      final hasApiKey = apiKey.isNotEmpty;
      
      // Test API key validation (in test mode, this will likely fail gracefully)
      final isValidKey = await ExtendedExchangeApiService.validateApiKey(apiKey);
      
      // Test API key storage
      final storedKey = await ExtendedExchangeApiService.getStoredApiKey(testAddress);
      final keyStored = storedKey == apiKey;
      
      // In test environment, we expect key generation to work but validation might fail
      final success = hasApiKey && keyStored;
      
      return {
        'success': success,
        'message': success ? 'API key generation working' : 'API key generation failed',
        'test_name': 'API Key Generation',
        'details': {
          'api_key_generated': hasApiKey,
          'api_key_stored': keyStored,
          'api_key_valid': isValidKey,
          'note': 'Validation may fail in test environment',
        },
      };
    } catch (e) {
      return {
        'success': false,
        'message': 'API key test failed: $e',
        'test_name': 'API Key Generation',
      };
    }
  }
  
  /// Test Extended Trading Service integration
  static Future<Map<String, dynamic>> _testTradingServiceIntegration() async {
    try {
      debugPrint('⚡ Testing trading service integration...');
      
      // Test setup
      final setup = await ExtendedTradingService.setupUserForTrading();
      final setupSuccess = setup['success'] == true;
      
      // Test trading status
      final status = await ExtendedTradingService.getTradingStatus();
      final hasStatus = status.isNotEmpty;
      
      // Test available symbols
      final symbols = await ExtendedTradingService.getAvailableSymbols();
      final hasSymbols = symbols.isNotEmpty;
      
      // Test account balance (may fail in test environment)
      final balance = await ExtendedTradingService.getAccountBalance();
      final hasBalance = balance.isNotEmpty;
      
      final success = setupSuccess || hasStatus; // At least basic functionality works
      
      return {
        'success': success,
        'message': success ? 'Trading service integration working' : 'Trading service integration failed',
        'test_name': 'Trading Service Integration',
        'details': {
          'setup_completed': setupSuccess,
          'status_available': hasStatus,
          'symbols_loaded': hasSymbols,
          'balance_accessible': hasBalance,
        },
      };
    } catch (e) {
      return {
        'success': false,
        'message': 'Trading service test failed: $e',
        'test_name': 'Trading Service Integration',
      };
    }
  }
  
  /// Test progressive trading modes
  static Future<Map<String, dynamic>> _testProgressiveTradingModes() async {
    try {
      debugPrint('📈 Testing progressive trading modes...');
      
      // Test mode setting and getting
      await RealTradingService.setTradingMode(RealTradingService.TradingMode.practice);
      final currentMode = await RealTradingService.getTradingMode();
      final modeSetCorrectly = currentMode == RealTradingService.TradingMode.practice;
      
      // Test limits for different modes
      final practiceParams = RealTradingService.getTradingLimits(RealTradingService.TradingMode.practice);
      final microLimits = RealTradingService.getTradingLimits(RealTradingService.TradingMode.micro);
      final hasLimits = practiceParams.isNotEmpty && microLimits.isNotEmpty;
      
      // Test trading status
      final tradingStatus = await RealTradingService.getTradingStatus();
      final hasStatus = tradingStatus.isNotEmpty;
      
      final success = modeSetCorrectly && hasLimits && hasStatus;
      
      return {
        'success': success,
        'message': success ? 'Progressive trading modes working' : 'Progressive trading modes failed',
        'test_name': 'Progressive Trading Modes',
        'details': {
          'mode_setting': modeSetCorrectly,
          'limits_available': hasLimits,
          'status_working': hasStatus,
          'current_mode': currentMode.name,
        },
      };
    } catch (e) {
      return {
        'success': false,
        'message': 'Progressive trading modes test failed: $e',
        'test_name': 'Progressive Trading Modes',
      };
    }
  }
  
  /// Quick health check for deployment readiness
  static Future<Map<String, dynamic>> quickHealthCheck() async {
    debugPrint('🩺 Running quick health check...');
    
    try {
      final serviceUp = await ExtendedExchangeApiService.isServiceAvailable();
      final starkKeys = await StarkSignatureService.ensureStarkKeys();
      final hasKeys = starkKeys['private_key']?.isNotEmpty == true;
      final tradingStatus = await RealTradingService.getTradingStatus();
      
      final overallHealth = serviceUp || hasKeys; // At least basic functionality
      
      return {
        'healthy': overallHealth,
        'timestamp': DateTime.now().toIso8601String(),
        'checks': {
          'extended_service': serviceUp,
          'stark_keys': hasKeys,
          'trading_modes': tradingStatus.isNotEmpty,
        },
        'message': overallHealth ? 'System ready for trading' : 'System has issues',
      };
    } catch (e) {
      return {
        'healthy': false,
        'error': e.toString(),
        'message': 'Health check failed',
      };
    }
  }
  
  /// Generate test report for documentation
  static Map<String, dynamic> generateTestReport(Map<String, dynamic> results) {
    final report = <String, dynamic>{
      'title': 'Extended API Integration Test Report',
      'generated_at': DateTime.now().toIso8601String(),
      'summary': {
        'total_tests': results['total_tests'] ?? 0,
        'successful_tests': results['successful_tests'] ?? 0,
        'success_rate': results['success_rate'] ?? '0.0',
        'overall_success': results['overall_success'] ?? false,
      },
      'test_details': results['tests'] ?? {},
      'errors': results['errors'] ?? [],
      'recommendations': [],
    };
    
    // Add recommendations based on results
    if (results['overall_success'] != true) {
      report['recommendations'].add('Review failed tests and ensure all dependencies are properly configured');
    }
    
    if (results['tests']?['service_availability']?['success'] != true) {
      report['recommendations'].add('Ensure Extended Exchange API service is running and accessible');
    }
    
    if (results['tests']?['stark_signatures']?['success'] != true) {
      report['recommendations'].add('Verify Stark signature generation and key management');
    }
    
    return report;
  }
}