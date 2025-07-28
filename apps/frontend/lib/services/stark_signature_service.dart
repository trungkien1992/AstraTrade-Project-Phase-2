import 'dart:convert';
import 'dart:developer';
import 'dart:math' as math;
import 'package:crypto/crypto.dart';
import 'package:flutter/foundation.dart';
import 'secure_storage_service.dart';

/// Service for generating Stark signatures required by Extended Exchange API
/// Handles transaction signing for order placement and trading operations
class StarkSignatureService {
  static const String _privateKeyStorageKey = 'stark_private_key';
  static const String _publicKeyStorageKey = 'stark_public_key';
  
  /// Generate a new Stark key pair for the user
  static Future<Map<String, String>> generateStarkKeyPair() async {
    try {
      // Generate a secure random private key (256 bits)
      final random = math.Random.secure();
      final privateKeyBytes = List<int>.generate(32, (i) => random.nextInt(256));
      final privateKeyHex = privateKeyBytes.map((b) => b.toRadixString(16).padLeft(2, '0')).join();
      
      // For MVP, we'll use a simplified public key derivation
      // In production, this would use proper Stark curve arithmetic
      final publicKeyHash = sha256.convert(utf8.encode(privateKeyHex));
      final publicKeyHex = publicKeyHash.toString();
      
      // Store the key pair securely
      await SecureStorageService.instance.storeValue(_privateKeyStorageKey, privateKeyHex);
      await SecureStorageService.instance.storeValue(_publicKeyStorageKey, publicKeyHex);
      
      debugPrint('✅ Stark key pair generated and stored securely');
      
      return {
        'private_key': privateKeyHex,
        'public_key': publicKeyHex,
      };
    } catch (e) {
      log('❌ Failed to generate Stark key pair: $e');
      throw StarkSignatureException('Failed to generate signing keys: $e');
    }
  }
  
  /// Get stored Stark private key
  static Future<String?> getPrivateKey() async {
    try {
      return await SecureStorageService.instance.getValue(_privateKeyStorageKey);
    } catch (e) {
      log('❌ Failed to retrieve private key: $e');
      return null;
    }
  }
  
  /// Get stored Stark public key
  static Future<String?> getPublicKey() async {
    try {
      return await SecureStorageService.instance.getValue(_publicKeyStorageKey);
    } catch (e) {
      log('❌ Failed to retrieve public key: $e');
      return null;
    }
  }
  
  /// Ensure user has Stark keys, generate if needed
  static Future<Map<String, String>> ensureStarkKeys() async {
    try {
      final privateKey = await getPrivateKey();
      final publicKey = await getPublicKey();
      
      if (privateKey != null && publicKey != null) {
        debugPrint('✅ Using existing Stark keys');
        return {
          'private_key': privateKey,
          'public_key': publicKey,
        };
      }
      
      debugPrint('🔄 Generating new Stark keys...');
      return await generateStarkKeyPair();
    } catch (e) {
      log('❌ Failed to ensure Stark keys: $e');
      throw StarkSignatureException('Failed to setup signing keys: $e');
    }
  }
  
  /// Sign trading order data for Extended API
  static Future<String> signTradingOrder(Map<String, dynamic> orderData) async {
    try {
      final keys = await ensureStarkKeys();
      final privateKey = keys['private_key']!;
      
      // Normalize order data for consistent signing
      final normalizedData = _normalizeOrderData(orderData);
      
      // Create signature payload
      final payload = jsonEncode(normalizedData);
      final payloadBytes = utf8.encode(payload);
      
      // Generate signature using HMAC-SHA256 with private key
      // In production, this would use proper Stark signature algorithm
      final hmac = Hmac(sha256, utf8.encode(privateKey));
      final digest = hmac.convert(payloadBytes);
      
      final signature = digest.toString();
      
      debugPrint('✅ Order signature generated successfully');
      return signature;
    } catch (e) {
      log('❌ Failed to sign trading order: $e');
      throw StarkSignatureException('Failed to sign order: $e');
    }
  }
  
  /// Sign account operations (cancellations, withdrawals)
  static Future<String> signAccountOperation({
    required String operation,
    required Map<String, dynamic> operationData,
  }) async {
    try {
      final keys = await ensureStarkKeys();
      final privateKey = keys['private_key']!;
      
      // Create operation payload
      final payload = {
        'operation': operation,
        'data': operationData,
        'timestamp': DateTime.now().millisecondsSinceEpoch,
      };
      
      final payloadJson = jsonEncode(payload);
      final payloadBytes = utf8.encode(payloadJson);
      
      // Generate signature
      final hmac = Hmac(sha256, utf8.encode(privateKey));
      final digest = hmac.convert(payloadBytes);
      
      final signature = digest.toString();
      
      debugPrint('✅ Account operation signature generated: $operation');
      return signature;
    } catch (e) {
      log('❌ Failed to sign account operation: $e');
      throw StarkSignatureException('Failed to sign operation: $e');
    }
  }
  
  /// Validate a signature against data
  static Future<bool> validateSignature({
    required String signature,
    required Map<String, dynamic> data,
  }) async {
    try {
      final keys = await ensureStarkKeys();
      final privateKey = keys['private_key']!;
      
      // Recreate the signature and compare
      final normalizedData = _normalizeOrderData(data);
      final payload = jsonEncode(normalizedData);
      final payloadBytes = utf8.encode(payload);
      
      final hmac = Hmac(sha256, utf8.encode(privateKey));
      final digest = hmac.convert(payloadBytes);
      
      final expectedSignature = digest.toString();
      
      return signature == expectedSignature;
    } catch (e) {
      log('❌ Failed to validate signature: $e');
      return false;
    }
  }
  
  /// Generate deterministic signature for testing
  /// IMPORTANT: This is for TESTING ONLY
  @Deprecated('Use signTradingOrder for production signatures')
  static String generateTestSignature(Map<String, dynamic> orderData) {
    try {
      // Use deterministic test private key
      const testPrivateKey = String.fromEnvironment(
      'TEST_STARK_PRIVATE_KEY',
      defaultValue: 'test_stark_private_key_for_development_only',
    );
      
      final normalizedData = _normalizeOrderData(orderData);
      final payload = jsonEncode(normalizedData);
      final payloadBytes = utf8.encode(payload);
      
      final hmac = Hmac(sha256, utf8.encode(testPrivateKey));
      final digest = hmac.convert(payloadBytes);
      
      debugPrint('⚠️ Using TEST signature - not for production');
      return digest.toString();
    } catch (e) {
      log('❌ Failed to generate test signature: $e');
      return 'test_signature_fallback';
    }
  }
  
  /// Clear stored Stark keys (logout/reset)
  static Future<void> clearStarkKeys() async {
    try {
      await SecureStorageService.instance.clearKey(_privateKeyStorageKey);
      await SecureStorageService.instance.clearKey(_publicKeyStorageKey);
      debugPrint('✅ Stark keys cleared');
    } catch (e) {
      log('❌ Failed to clear Stark keys: $e');
    }
  }
  
  /// Normalize order data for consistent signature generation
  static Map<String, dynamic> _normalizeOrderData(Map<String, dynamic> orderData) {
    final normalized = Map<String, dynamic>.from(orderData);
    
    // Sort keys for consistent ordering
    final sortedKeys = normalized.keys.toList()..sort();
    final sortedData = <String, dynamic>{};
    
    for (final key in sortedKeys) {
      final value = normalized[key];
      if (value != null) {
        // Normalize numeric values to strings for consistency
        if (value is num) {
          sortedData[key] = value.toString();
        } else {
          sortedData[key] = value;
        }
      }
    }
    
    return sortedData;
  }
  
  /// Get signature info for debugging
  static Future<Map<String, dynamic>> getSignatureInfo() async {
    try {
      final publicKey = await getPublicKey();
      final hasPrivateKey = await getPrivateKey() != null;
      
      return {
        'has_keys': hasPrivateKey,
        'public_key': publicKey?.substring(0, 16) ?? null,
        'algorithm': 'HMAC-SHA256', // Simplified for MVP
        'key_length': hasPrivateKey ? 256 : 0,
      };
    } catch (e) {
      log('❌ Failed to get signature info: $e');
      return {
        'has_keys': false,
        'error': e.toString(),
      };
    }
  }
}

/// Configuration for Stark signature generation
class StarkSignatureConfig {
  static const bool enableTestMode = kDebugMode;
  static const int keyLength = 256; // bits
  static const String algorithm = 'HMAC-SHA256'; // Simplified for MVP
  
  /// Check if we're in test mode
  static bool get isTestMode => enableTestMode;
  
  /// Get signature requirements for Extended API
  static Map<String, dynamic> get requirements => {
    'algorithm': algorithm,
    'key_length': keyLength,
    'format': 'hex',
    'required_fields': ['symbol', 'amount', 'side', 'type', 'timestamp'],
  };
}

/// Exception thrown by Stark signature operations
class StarkSignatureException implements Exception {
  final String message;
  
  StarkSignatureException(this.message);
  
  @override
  String toString() => 'StarkSignatureException: $message';
}