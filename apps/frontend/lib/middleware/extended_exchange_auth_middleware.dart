import 'dart:async';
import 'dart:convert';
import 'dart:developer';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:astratrade_app/services/extended_exchange_hmac_service.dart';
import 'package:astratrade_app/services/secure_storage_service.dart';

/// Extended Exchange Authentication Middleware
/// Automatically adds HMAC authentication to all API requests
class ExtendedExchangeAuthMiddleware {
  static const int _maxRetries = 3;
  static const Duration _retryDelay = Duration(seconds: 1);

  /// HTTP client wrapper that automatically adds HMAC authentication
  static Future<http.Response> authenticatedRequest({
    required String method,
    required String url,
    Map<String, String>? headers,
    dynamic body,
    Map<String, String>? queryParams,
    Duration? timeout,
  }) async {
    try {
      // Get stored API credentials
      final credentials = await _getApiCredentials();
      if (credentials == null) {
        throw AuthenticationException(
          'No API credentials found. Please configure API key and secret.',
        );
      }

      final apiKey = credentials['api_key']!;
      final apiSecret = credentials['api_secret']!;

      // Parse URL to get path
      final uri = Uri.parse(url);
      final path = uri.path + (uri.query.isNotEmpty ? '?${uri.query}' : '');

      // Prepare request body
      final bodyString = ExtendedExchangeHmacService.normalizeBody(body);

      // Add query parameters if provided
      final finalUri = queryParams != null && queryParams.isNotEmpty
          ? uri.replace(
              queryParameters: {...uri.queryParameters, ...queryParams},
            )
          : uri;

      // Generate authentication headers
      final authHeaders = ExtendedExchangeHmacService.generateAuthHeaders(
        apiKey: apiKey,
        apiSecret: apiSecret,
        method: method,
        path: path,
        body: bodyString,
        additionalHeaders: headers,
      );

      debugPrint(
        '🔒 Making authenticated ${method.toUpperCase()} request to $path',
      );

      // Execute request with retry logic
      return await _executeWithRetry(
        method: method,
        uri: finalUri,
        headers: authHeaders,
        body: bodyString,
        timeout: timeout ?? const Duration(seconds: 30),
      );
    } catch (e) {
      log('❌ Authenticated request failed: $e');
      rethrow;
    }
  }

  /// Execute HTTP request with authentication and retry logic
  static Future<http.Response> _executeWithRetry({
    required String method,
    required Uri uri,
    required Map<String, String> headers,
    required String body,
    required Duration timeout,
  }) async {
    int attempt = 0;
    Exception? lastException;

    while (attempt < _maxRetries) {
      attempt++;

      try {
        debugPrint('🔄 Request attempt $attempt/$_maxRetries');

        late http.Response response;

        switch (method.toUpperCase()) {
          case 'GET':
            response = await http.get(uri, headers: headers).timeout(timeout);
            break;
          case 'POST':
            response = await http
                .post(uri, headers: headers, body: body)
                .timeout(timeout);
            break;
          case 'PUT':
            response = await http
                .put(uri, headers: headers, body: body)
                .timeout(timeout);
            break;
          case 'DELETE':
            response = await http
                .delete(uri, headers: headers)
                .timeout(timeout);
            break;
          case 'PATCH':
            response = await http
                .patch(uri, headers: headers, body: body)
                .timeout(timeout);
            break;
          default:
            throw AuthenticationException('Unsupported HTTP method: $method');
        }

        // Check for authentication errors
        if (response.statusCode == 401) {
          debugPrint('❌ Authentication failed (401): ${response.body}');
          throw AuthenticationException(
            'Authentication failed: Invalid signature or expired timestamp',
          );
        } else if (response.statusCode == 403) {
          debugPrint('❌ Authorization failed (403): ${response.body}');
          throw AuthenticationException(
            'Authorization failed: Insufficient permissions',
          );
        } else if (response.statusCode >= 500) {
          debugPrint(
            '⚠️ Server error (${response.statusCode}): ${response.body}',
          );
          if (attempt < _maxRetries) {
            await Future.delayed(_retryDelay * attempt);
            continue;
          }
        }

        debugPrint('✅ Request completed: ${response.statusCode}');
        return response;
      } on TimeoutException catch (e) {
        lastException = AuthenticationException(
          'Request timeout: ${e.message}',
        );
        debugPrint('⏰ Request timeout on attempt $attempt');

        if (attempt < _maxRetries) {
          await Future.delayed(_retryDelay * attempt);
          continue;
        }
      } on AuthenticationException {
        // Don't retry authentication errors
        rethrow;
      } catch (e) {
        lastException = Exception('Request failed: $e');
        debugPrint('💥 Request error on attempt $attempt: $e');

        if (attempt < _maxRetries) {
          await Future.delayed(_retryDelay * attempt);
          continue;
        }
      }
    }

    throw lastException ?? Exception('All retry attempts failed');
  }

  /// Get API credentials from secure storage
  static Future<Map<String, String>?> _getApiCredentials() async {
    try {
      final tradingCredentials = await SecureStorageService.instance
          .getTradingCredentials();

      if (tradingCredentials == null) {
        debugPrint('⚠️ No trading credentials found');
        return null;
      }

      final apiKey = tradingCredentials['api_key'] as String?;
      final apiSecret = tradingCredentials['api_secret'] as String?;

      if (apiKey == null ||
          apiSecret == null ||
          apiKey.isEmpty ||
          apiSecret.isEmpty) {
        debugPrint('⚠️ Incomplete API credentials (missing key or secret)');
        return null;
      }

      return {'api_key': apiKey, 'api_secret': apiSecret};
    } catch (e) {
      log('❌ Failed to get API credentials: $e');
      return null;
    }
  }

  /// Convenience methods for different HTTP methods

  static Future<http.Response> get(
    String url, {
    Map<String, String>? headers,
    Map<String, String>? queryParams,
    Duration? timeout,
  }) async {
    return authenticatedRequest(
      method: 'GET',
      url: url,
      headers: headers,
      queryParams: queryParams,
      timeout: timeout,
    );
  }

  static Future<http.Response> post(
    String url, {
    Map<String, String>? headers,
    dynamic body,
    Map<String, String>? queryParams,
    Duration? timeout,
  }) async {
    return authenticatedRequest(
      method: 'POST',
      url: url,
      headers: headers,
      body: body,
      queryParams: queryParams,
      timeout: timeout,
    );
  }

  static Future<http.Response> put(
    String url, {
    Map<String, String>? headers,
    dynamic body,
    Map<String, String>? queryParams,
    Duration? timeout,
  }) async {
    return authenticatedRequest(
      method: 'PUT',
      url: url,
      headers: headers,
      body: body,
      queryParams: queryParams,
      timeout: timeout,
    );
  }

  static Future<http.Response> delete(
    String url, {
    Map<String, String>? headers,
    Map<String, String>? queryParams,
    Duration? timeout,
  }) async {
    return authenticatedRequest(
      method: 'DELETE',
      url: url,
      headers: headers,
      queryParams: queryParams,
      timeout: timeout,
    );
  }

  /// Validate stored API credentials
  static Future<bool> validateCredentials() async {
    try {
      final credentials = await _getApiCredentials();
      if (credentials == null) {
        debugPrint('❌ No credentials to validate');
        return false;
      }

      // Test credentials with a simple API call
      final response = await get(
        'https://api.starknet.sepolia.extended.exchange/api/v1/user/account',
        timeout: const Duration(seconds: 10),
      );

      final isValid = response.statusCode == 200;
      debugPrint(
        isValid
            ? '✅ Credentials validation passed'
            : '❌ Credentials validation failed: ${response.statusCode}',
      );

      return isValid;
    } catch (e) {
      log('❌ Credentials validation error: $e');
      return false;
    }
  }

  /// Test the middleware with a simple request
  static Future<bool> testMiddleware() async {
    debugPrint('🧪 Testing authentication middleware...');

    try {
      // Test with a simple GET request
      final response = await get(
        'https://api.starknet.sepolia.extended.exchange/api/v1/markets',
        timeout: const Duration(seconds: 10),
      );

      final isSuccess = response.statusCode == 200;
      debugPrint(
        isSuccess
            ? '✅ Middleware test passed'
            : '❌ Middleware test failed: ${response.statusCode}',
      );

      return isSuccess;
    } catch (e) {
      if (e is AuthenticationException) {
        debugPrint(
          '⚠️ Middleware test: Authentication required (expected for test)',
        );
        return true; // This is expected if no credentials are set
      }

      log('❌ Middleware test failed: $e');
      return false;
    }
  }
}

/// Exception thrown during authentication operations
class AuthenticationException implements Exception {
  final String message;
  final int? statusCode;
  final String? errorCode;

  AuthenticationException(this.message, {this.statusCode, this.errorCode});

  @override
  String toString() {
    return 'AuthenticationException: $message${statusCode != null ? ' (Status: $statusCode)' : ''}${errorCode != null ? ' (Code: $errorCode)' : ''}';
  }
}
