import 'dart:convert';
import 'dart:developer';
import 'package:crypto/crypto.dart';
import 'package:flutter/foundation.dart';

/// Extended Exchange HMAC Authentication Service
/// Implements HMAC-SHA256 signature generation for secure API authentication
class ExtendedExchangeHmacService {
  static const int _timestampToleranceSeconds = 300; // 5 minutes
  static const String _userAgent = 'AstraTrade/1.0.0';

  /// Generate HMAC-SHA256 signature for Extended Exchange API request
  ///
  /// Signature format: HMAC-SHA256(timestamp + method + path + body, apiSecret)
  static String generateSignature({
    required String apiSecret,
    required String method,
    required String path,
    required String body,
    int? timestamp,
  }) {
    try {
      // Use provided timestamp or generate current UTC timestamp
      final ts =
          timestamp ?? DateTime.now().toUtc().millisecondsSinceEpoch ~/ 1000;

      // Create the signature string: timestamp + method + path + body
      final signatureString = '$ts${method.toUpperCase()}$path$body';

      debugPrint('🔐 Generating HMAC signature');
      debugPrint('   Method: ${method.toUpperCase()}');
      debugPrint('   Path: $path');
      debugPrint('   Body length: ${body.length}');
      debugPrint('   Timestamp: $ts');

      // Generate HMAC-SHA256 signature
      final key = utf8.encode(apiSecret);
      final messageBytes = utf8.encode(signatureString);
      final hmac = Hmac(sha256, key);
      final digest = hmac.convert(messageBytes);

      final signature = digest.toString();
      debugPrint(
        '✅ HMAC signature generated: ${signature.substring(0, 16)}...',
      );

      return signature;
    } catch (e) {
      log('❌ Failed to generate HMAC signature: $e');
      throw HmacAuthenticationException('Signature generation failed: $e');
    }
  }

  /// Generate authentication headers for Extended Exchange API request
  static Map<String, String> generateAuthHeaders({
    required String apiKey,
    required String apiSecret,
    required String method,
    required String path,
    required String body,
    Map<String, String>? additionalHeaders,
  }) {
    try {
      final timestamp = DateTime.now().toUtc().millisecondsSinceEpoch ~/ 1000;

      final signature = generateSignature(
        apiSecret: apiSecret,
        method: method,
        path: path,
        body: body,
        timestamp: timestamp,
      );

      final headers = {
        'X-Api-Key': apiKey,
        'X-Timestamp': timestamp.toString(),
        'X-Signature': signature,
        'Content-Type': 'application/json',
        'User-Agent': _userAgent,
        ...?additionalHeaders,
      };

      debugPrint('🔑 Generated auth headers');
      debugPrint('   API Key: ${apiKey.substring(0, 8)}...');
      debugPrint('   Timestamp: $timestamp');
      debugPrint('   Headers count: ${headers.length}');

      return headers;
    } catch (e) {
      log('❌ Failed to generate auth headers: $e');
      throw HmacAuthenticationException('Auth headers generation failed: $e');
    }
  }

  /// Validate HMAC signature (for testing and verification)
  static bool validateSignature({
    required String apiSecret,
    required String method,
    required String path,
    required String body,
    required String providedSignature,
    required int timestamp,
  }) {
    try {
      // Check timestamp is within tolerance
      final now = DateTime.now().toUtc().millisecondsSinceEpoch ~/ 1000;
      final timeDiff = (now - timestamp).abs();

      if (timeDiff > _timestampToleranceSeconds) {
        debugPrint(
          '❌ Timestamp validation failed: ${timeDiff}s > ${_timestampToleranceSeconds}s',
        );
        return false;
      }

      // Generate expected signature
      final expectedSignature = generateSignature(
        apiSecret: apiSecret,
        method: method,
        path: path,
        body: body,
        timestamp: timestamp,
      );

      // Compare signatures using secure comparison
      final isValid = _secureCompare(expectedSignature, providedSignature);

      debugPrint(
        isValid
            ? '✅ Signature validation passed'
            : '❌ Signature validation failed',
      );

      return isValid;
    } catch (e) {
      log('❌ Signature validation error: $e');
      return false;
    }
  }

  /// Normalize request path for signature generation
  static String normalizePath(String path) {
    // Remove base URL if present
    if (path.startsWith('http')) {
      final uri = Uri.parse(path);
      return uri.path + (uri.query.isNotEmpty ? '?${uri.query}' : '');
    }

    // Ensure path starts with /
    if (!path.startsWith('/')) {
      path = '/$path';
    }

    return path;
  }

  /// Normalize request body for signature generation
  static String normalizeBody(dynamic body) {
    if (body == null) return '';

    if (body is String) {
      return body;
    }

    if (body is Map || body is List) {
      return jsonEncode(body);
    }

    return body.toString();
  }

  /// Create request payload for signing
  static HmacRequestPayload createRequestPayload({
    required String method,
    required String path,
    dynamic body,
    Map<String, String>? queryParams,
  }) {
    try {
      // Normalize components
      final normalizedPath = normalizePath(path);
      final normalizedBody = normalizeBody(body);
      final upperMethod = method.toUpperCase();

      // Add query parameters to path if provided
      String fullPath = normalizedPath;
      if (queryParams != null && queryParams.isNotEmpty) {
        final queryString = queryParams.entries
            .map(
              (e) =>
                  '${Uri.encodeQueryComponent(e.key)}=${Uri.encodeQueryComponent(e.value)}',
            )
            .join('&');

        final separator = fullPath.contains('?') ? '&' : '?';
        fullPath = '$fullPath$separator$queryString';
      }

      return HmacRequestPayload(
        method: upperMethod,
        path: fullPath,
        body: normalizedBody,
        timestamp: DateTime.now().toUtc().millisecondsSinceEpoch ~/ 1000,
      );
    } catch (e) {
      log('❌ Failed to create request payload: $e');
      throw HmacAuthenticationException('Request payload creation failed: $e');
    }
  }

  /// Secure string comparison to prevent timing attacks
  static bool _secureCompare(String a, String b) {
    if (a.length != b.length) return false;

    int result = 0;
    for (int i = 0; i < a.length; i++) {
      result |= a.codeUnitAt(i) ^ b.codeUnitAt(i);
    }

    return result == 0;
  }

  /// Test HMAC service with known values
  static Future<bool> testHmacService() async {
    debugPrint('🧪 Testing HMAC service...');

    try {
      // Test signature generation
      const testApiSecret = 'test_secret_key_123';
      const testMethod = 'POST';
      const testPath = '/api/v1/orders';
      const testBody = '{"symbol":"BTC-USD","side":"BUY","amount":"0.1"}';
      const testTimestamp =
          1640995200; // Known timestamp for consistent testing

      final signature = generateSignature(
        apiSecret: testApiSecret,
        method: testMethod,
        path: testPath,
        body: testBody,
        timestamp: testTimestamp,
      );

      debugPrint(
        '✅ Test signature generated: ${signature.substring(0, 16)}...',
      );

      // Test signature validation
      final isValid = validateSignature(
        apiSecret: testApiSecret,
        method: testMethod,
        path: testPath,
        body: testBody,
        providedSignature: signature,
        timestamp: testTimestamp,
      );

      if (!isValid) {
        debugPrint('❌ Signature validation test failed');
        return false;
      }

      // Test auth headers generation
      final headers = generateAuthHeaders(
        apiKey: 'test_api_key_123',
        apiSecret: testApiSecret,
        method: testMethod,
        path: testPath,
        body: testBody,
      );

      if (!headers.containsKey('X-Api-Key') ||
          !headers.containsKey('X-Timestamp') ||
          !headers.containsKey('X-Signature')) {
        debugPrint('❌ Auth headers test failed');
        return false;
      }

      // Test request payload creation
      final payload = createRequestPayload(
        method: testMethod,
        path: testPath,
        body: jsonDecode(testBody),
        queryParams: {'test': 'value'},
      );

      if (payload.method != testMethod.toUpperCase()) {
        debugPrint('❌ Request payload test failed');
        return false;
      }

      debugPrint('✅ All HMAC service tests passed');
      return true;
    } catch (e) {
      log('❌ HMAC service test failed: $e');
      return false;
    }
  }
}

/// HMAC request payload data structure
class HmacRequestPayload {
  final String method;
  final String path;
  final String body;
  final int timestamp;

  HmacRequestPayload({
    required this.method,
    required this.path,
    required this.body,
    required this.timestamp,
  });

  /// Get the signature string for this payload
  String getSignatureString() {
    return '$timestamp$method$path$body';
  }

  @override
  String toString() {
    return 'HmacRequestPayload(method: $method, path: $path, bodyLength: ${body.length}, timestamp: $timestamp)';
  }
}

/// Exception thrown during HMAC authentication operations
class HmacAuthenticationException implements Exception {
  final String message;
  final String? errorCode;

  HmacAuthenticationException(this.message, {this.errorCode});

  @override
  String toString() {
    return 'HmacAuthenticationException: $message${errorCode != null ? ' (Code: $errorCode)' : ''}';
  }
}
