import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:crypto/crypto.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

// Environment configuration
class EnvironmentConfig {
  static const String appVersion = '1.0.0';
  static const String apiSecret = String.fromEnvironment(
    'API_SECRET',
    defaultValue: 'default_api_secret_key',
  );
}

// Secure storage wrapper
class SecureStorage {
  final FlutterSecureStorage _storage;

  SecureStorage(this._storage);

  Future<String?> getToken() async {
    return await _storage.read(key: 'auth_token');
  }

  Future<String?> getRefreshToken() async {
    return await _storage.read(key: 'refresh_token');
  }

  Future<void> saveTokens({
    required String accessToken,
    required String refreshToken,
  }) async {
    await _storage.write(key: 'auth_token', value: accessToken);
    await _storage.write(key: 'refresh_token', value: refreshToken);
  }

  Future<void> clearTokens() async {
    await _storage.delete(key: 'auth_token');
    await _storage.delete(key: 'refresh_token');
  }
}

// Custom exception classes
class ApiException implements Exception {
  final String message;
  final int? statusCode;

  ApiException(this.message, {this.statusCode});

  @override
  String toString() => 'ApiException: $message (Status: $statusCode)';
}

class BadRequestException extends ApiException {
  BadRequestException(String message) : super(message, statusCode: 400);
}

class UnauthorizedException extends ApiException {
  UnauthorizedException(String message) : super(message, statusCode: 401);
}

class ForbiddenException extends ApiException {
  ForbiddenException(String message) : super(message, statusCode: 403);
}

class NotFoundException extends ApiException {
  NotFoundException(String message) : super(message, statusCode: 404);
}

class RateLimitException extends ApiException {
  RateLimitException(String message) : super(message, statusCode: 429);
}

class ServerException extends ApiException {
  ServerException(String message) : super(message, statusCode: 500);
}

class NetworkException extends ApiException {
  NetworkException(String message) : super(message);
}

// Simple retry interceptor implementation
class RetryInterceptor extends Interceptor {
  final Dio dio;
  final int retries;
  final List<Duration> retryDelays;

  RetryInterceptor({
    required this.dio,
    this.retries = 3,
    this.retryDelays = const [
      Duration(seconds: 1),
      Duration(seconds: 3),
      Duration(seconds: 5),
    ],
  });

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    if (_shouldRetry(err) && err.requestOptions.extra['retryCount'] < retries) {
      final retryCount = (err.requestOptions.extra['retryCount'] ?? 0) + 1;
      err.requestOptions.extra['retryCount'] = retryCount;

      final delay = retryDelays[retryCount - 1];
      await Future.delayed(delay);

      try {
        final response = await dio.fetch(err.requestOptions);
        handler.resolve(response);
        return;
      } catch (e) {
        // Let the error pass through for the next retry
      }
    }

    handler.next(err);
  }

  bool _shouldRetry(DioException error) {
    return error.type == DioExceptionType.connectionTimeout ||
        error.type == DioExceptionType.receiveTimeout ||
        error.type == DioExceptionType.sendTimeout ||
        (error.response?.statusCode != null &&
            error.response!.statusCode! >= 500);
  }
}

class SecureApiClient {
  final Dio _dio;
  final SecureStorage _storage;
  static const int _maxRetries = 3;

  SecureApiClient({required String baseUrl, required SecureStorage storage})
    : _storage = storage,
      _dio = Dio(
        BaseOptions(
          baseUrl: baseUrl,
          connectTimeout: const Duration(seconds: 10),
          receiveTimeout: const Duration(seconds: 10),
          headers: {
            'Content-Type': 'application/json',
            'X-App-Version': EnvironmentConfig.appVersion,
            'X-Platform': defaultTargetPlatform.name,
          },
        ),
      ) {
    _setupInterceptors();
  }

  void _setupInterceptors() {
    // Auth interceptor
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          final token = await _storage.getToken();
          if (token != null) {
            options.headers['Authorization'] = 'Bearer $token';
          }

          // Add request signature for additional security
          final signature = _generateRequestSignature(
            options.method,
            options.path,
            options.data,
          );
          options.headers['X-Signature'] = signature;

          handler.next(options);
        },
        onError: (error, handler) async {
          if (error.response?.statusCode == 401) {
            // Token expired, try to refresh
            final refreshed = await _refreshToken();
            if (refreshed) {
              // Retry the request
              final options = error.requestOptions;
              final token = await _storage.getToken();
              options.headers['Authorization'] = 'Bearer $token';

              final response = await _dio.fetch(options);
              return handler.resolve(response);
            }
          }
          handler.next(error);
        },
      ),
    );

    // Retry interceptor
    _dio.interceptors.add(
      RetryInterceptor(
        dio: _dio,
        retries: _maxRetries,
        retryDelays: const [
          Duration(seconds: 1),
          Duration(seconds: 3),
          Duration(seconds: 5),
        ],
      ),
    );

    // Logging interceptor (debug only)
    if (kDebugMode) {
      _dio.interceptors.add(
        LogInterceptor(
          requestBody: true,
          responseBody: true,
          error: true,
          requestHeader: true,
          responseHeader: true,
        ),
      );
    }
  }

  String _generateRequestSignature(String method, String path, dynamic data) {
    final timestamp = DateTime.now().millisecondsSinceEpoch.toString();
    final dataString = data != null ? jsonEncode(data) : '';
    final message = '$method$path$dataString$timestamp';

    final key = utf8.encode(EnvironmentConfig.apiSecret);
    final bytes = utf8.encode(message);

    final hmacSha256 = Hmac(sha256, key);
    final digest = hmacSha256.convert(bytes);

    return '$digest:$timestamp';
  }

  Future<bool> _refreshToken() async {
    try {
      final refreshToken = await _storage.getRefreshToken();
      if (refreshToken == null) return false;

      final response = await _dio.post(
        '/auth/refresh',
        data: {'refresh_token': refreshToken},
      );

      final newToken = response.data['access_token'];
      final newRefreshToken = response.data['refresh_token'];

      await _storage.saveTokens(
        accessToken: newToken,
        refreshToken: newRefreshToken,
      );

      return true;
    } catch (e) {
      return false;
    }
  }

  // API methods with automatic error handling
  Future<T> get<T>(
    String path, {
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    try {
      final response = await _dio.get<T>(
        path,
        queryParameters: queryParameters,
        options: options,
      );
      return response.data!;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<T> post<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    try {
      final response = await _dio.post<T>(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
      );
      return response.data!;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  ApiException _handleError(DioException error) {
    if (error.response != null) {
      final statusCode = error.response!.statusCode ?? 0;
      final data = error.response!.data;

      String message = 'An error occurred';
      if (data is Map && data.containsKey('detail')) {
        message = data['detail'];
      }

      switch (statusCode) {
        case 400:
          return BadRequestException(message);
        case 401:
          return UnauthorizedException(message);
        case 403:
          return ForbiddenException(message);
        case 404:
          return NotFoundException(message);
        case 429:
          return RateLimitException(message);
        case 500:
          return ServerException(message);
        default:
          return ApiException(message, statusCode: statusCode);
      }
    } else if (error.type == DioExceptionType.connectionTimeout) {
      return NetworkException('Connection timeout');
    } else if (error.type == DioExceptionType.receiveTimeout) {
      return NetworkException('Receive timeout');
    } else {
      return NetworkException('Network error');
    }
  }
}
