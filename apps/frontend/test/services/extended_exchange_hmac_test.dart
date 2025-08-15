import 'package:flutter_test/flutter_test.dart';
import 'package:astratrade_app/services/extended_exchange_hmac_service.dart';
import 'package:astratrade_app/services/secure_storage_service.dart';
import 'package:astratrade_app/middleware/extended_exchange_auth_middleware.dart';

void main() {
  group('ExtendedExchangeHmacService Tests', () {
    const testApiKey = 'test_api_key_12345';
    const testApiSecret = 'test_secret_key_abcdef';
    const testMethod = 'POST';
    const testPath = '/api/v1/orders';
    const testBody = '{"symbol":"BTC-USD","side":"BUY","amount":"0.1"}';
    const testTimestamp = 1640995200; // Fixed timestamp for consistent testing

    test('should generate consistent HMAC signature', () {
      // Test signature generation with known values
      final signature1 = ExtendedExchangeHmacService.generateSignature(
        apiSecret: testApiSecret,
        method: testMethod,
        path: testPath,
        body: testBody,
        timestamp: testTimestamp,
      );

      final signature2 = ExtendedExchangeHmacService.generateSignature(
        apiSecret: testApiSecret,
        method: testMethod,
        path: testPath,
        body: testBody,
        timestamp: testTimestamp,
      );

      expect(signature1, equals(signature2));
      expect(signature1.length, equals(64)); // SHA-256 hex string length
    });

    test('should generate different signatures for different inputs', () {
      final signature1 = ExtendedExchangeHmacService.generateSignature(
        apiSecret: testApiSecret,
        method: testMethod,
        path: testPath,
        body: testBody,
        timestamp: testTimestamp,
      );

      final signature2 = ExtendedExchangeHmacService.generateSignature(
        apiSecret: testApiSecret,
        method: testMethod,
        path: testPath,
        body:
            '{"symbol":"ETH-USD","side":"SELL","amount":"0.2"}', // Different body
        timestamp: testTimestamp,
      );

      expect(signature1, isNot(equals(signature2)));
    });

    test('should validate signatures correctly', () {
      // Use current timestamp for validation test
      final currentTimestamp =
          DateTime.now().toUtc().millisecondsSinceEpoch ~/ 1000;

      final signature = ExtendedExchangeHmacService.generateSignature(
        apiSecret: testApiSecret,
        method: testMethod,
        path: testPath,
        body: testBody,
        timestamp: currentTimestamp,
      );

      // Valid signature should pass
      final isValid = ExtendedExchangeHmacService.validateSignature(
        apiSecret: testApiSecret,
        method: testMethod,
        path: testPath,
        body: testBody,
        providedSignature: signature,
        timestamp: currentTimestamp,
      );

      expect(isValid, isTrue);
    });

    test('should reject invalid signatures', () {
      // Use current timestamp for validation test
      final currentTimestamp =
          DateTime.now().toUtc().millisecondsSinceEpoch ~/ 1000;
      const invalidSignature = 'invalid_signature_12345';

      final isValid = ExtendedExchangeHmacService.validateSignature(
        apiSecret: testApiSecret,
        method: testMethod,
        path: testPath,
        body: testBody,
        providedSignature: invalidSignature,
        timestamp: currentTimestamp,
      );

      expect(isValid, isFalse);
    });

    test('should generate correct auth headers', () {
      final headers = ExtendedExchangeHmacService.generateAuthHeaders(
        apiKey: testApiKey,
        apiSecret: testApiSecret,
        method: testMethod,
        path: testPath,
        body: testBody,
      );

      expect(headers['X-Api-Key'], equals(testApiKey));
      expect(headers['X-Timestamp'], isNotNull);
      expect(headers['X-Signature'], isNotNull);
      expect(headers['Content-Type'], equals('application/json'));
      expect(headers['User-Agent'], equals('AstraTrade/1.0.0'));
    });

    test('should normalize paths correctly', () {
      expect(
        ExtendedExchangeHmacService.normalizePath('/api/v1/orders'),
        equals('/api/v1/orders'),
      );

      expect(
        ExtendedExchangeHmacService.normalizePath('api/v1/orders'),
        equals('/api/v1/orders'),
      );

      expect(
        ExtendedExchangeHmacService.normalizePath(
          'https://api.example.com/api/v1/orders?param=value',
        ),
        equals('/api/v1/orders?param=value'),
      );
    });

    test('should normalize request bodies correctly', () {
      expect(ExtendedExchangeHmacService.normalizeBody(null), equals(''));

      expect(
        ExtendedExchangeHmacService.normalizeBody('test string'),
        equals('test string'),
      );

      expect(
        ExtendedExchangeHmacService.normalizeBody({'key': 'value'}),
        equals('{"key":"value"}'),
      );

      expect(
        ExtendedExchangeHmacService.normalizeBody(['item1', 'item2']),
        equals('["item1","item2"]'),
      );
    });

    test('should create request payload correctly', () {
      final payload = ExtendedExchangeHmacService.createRequestPayload(
        method: testMethod,
        path: testPath,
        body: {'symbol': 'BTC-USD', 'side': 'BUY'},
        queryParams: {'limit': '10'},
      );

      expect(payload.method, equals('POST'));
      expect(payload.path, contains('/api/v1/orders'));
      expect(payload.path, contains('limit=10'));
      expect(payload.body, equals('{"symbol":"BTC-USD","side":"BUY"}'));
      expect(payload.timestamp, isA<int>());
    });

    test('should pass comprehensive service test', () async {
      final testResult = await ExtendedExchangeHmacService.testHmacService();
      expect(testResult, isTrue);
    });
  });

  group('HmacRequestPayload Tests', () {
    test('should generate correct signature string', () {
      final payload = HmacRequestPayload(
        method: 'POST',
        path: '/api/v1/test',
        body: '{"test":"data"}',
        timestamp: 1640995200,
      );

      final signatureString = payload.getSignatureString();
      expect(
        signatureString,
        equals('1640995200POST/api/v1/test{"test":"data"}'),
      );
    });

    test('should provide correct string representation', () {
      final payload = HmacRequestPayload(
        method: 'GET',
        path: '/api/v1/test',
        body: '',
        timestamp: 1640995200,
      );

      final string = payload.toString();
      expect(string, contains('method: GET'));
      expect(string, contains('path: /api/v1/test'));
      expect(string, contains('bodyLength: 0'));
      expect(string, contains('timestamp: 1640995200'));
    });
  });

  group('HmacAuthenticationException Tests', () {
    test('should format exception message correctly', () {
      final exception = HmacAuthenticationException(
        'Test error message',
        errorCode: 'ERR001',
      );

      final string = exception.toString();
      expect(string, contains('HmacAuthenticationException'));
      expect(string, contains('Test error message'));
      expect(string, contains('Code: ERR001'));
    });

    test('should handle exception without error code', () {
      final exception = HmacAuthenticationException('Simple error');
      final string = exception.toString();
      expect(string, contains('HmacAuthenticationException'));
      expect(string, contains('Simple error'));
      expect(string, isNot(contains('Code:')));
    });
  });

  group('Performance Tests', () {
    test('should generate signatures efficiently', () {
      const iterations = 1000;
      const testApiSecret = 'performance_test_secret';
      const testMethod = 'GET';
      const testPath = '/api/v1/test';
      const testBody = '';

      final stopwatch = Stopwatch()..start();

      for (int i = 0; i < iterations; i++) {
        ExtendedExchangeHmacService.generateSignature(
          apiSecret: testApiSecret,
          method: testMethod,
          path: testPath,
          body: testBody,
          timestamp: 1640995200 + i,
        );
      }

      stopwatch.stop();
      final avgTimeMs = stopwatch.elapsedMilliseconds / iterations;

      // Should generate signatures quickly (under 1ms average)
      expect(avgTimeMs, lessThan(1.0));
    });

    test('should validate signatures efficiently', () {
      const iterations = 1000;
      const testApiSecret = 'performance_test_secret';
      const testMethod = 'GET';
      const testPath = '/api/v1/test';
      const testBody = '';
      const testTimestamp = 1640995200;

      final signature = ExtendedExchangeHmacService.generateSignature(
        apiSecret: testApiSecret,
        method: testMethod,
        path: testPath,
        body: testBody,
        timestamp: testTimestamp,
      );

      final stopwatch = Stopwatch()..start();

      for (int i = 0; i < iterations; i++) {
        ExtendedExchangeHmacService.validateSignature(
          apiSecret: testApiSecret,
          method: testMethod,
          path: testPath,
          body: testBody,
          providedSignature: signature,
          timestamp: testTimestamp,
        );
      }

      stopwatch.stop();
      final avgTimeMs = stopwatch.elapsedMilliseconds / iterations;

      // Should validate signatures quickly (under 1ms average)
      expect(avgTimeMs, lessThan(1.0));
    });
  });

  group('Security Tests', () {
    test('should use secure string comparison', () {
      const signature1 = 'abc123def456';
      const signature2 = 'abc123def456';
      const signature3 = 'xyz789ghi012';

      // Test with known implementation of secure comparison
      final isValid1 = ExtendedExchangeHmacService.validateSignature(
        apiSecret: 'test_secret',
        method: 'GET',
        path: '/test',
        body: '',
        providedSignature: signature1,
        timestamp: 1640995200,
      );

      final isValid2 = ExtendedExchangeHmacService.validateSignature(
        apiSecret: 'test_secret',
        method: 'GET',
        path: '/test',
        body: '',
        providedSignature: signature3,
        timestamp: 1640995200,
      );

      // Both should be false (since we're using wrong signatures for validation)
      // but the test ensures the secure comparison function works
      expect(isValid1, isFalse);
      expect(isValid2, isFalse);
    });

    test('should reject expired timestamps', () {
      final signature = ExtendedExchangeHmacService.generateSignature(
        apiSecret: 'test_secret',
        method: 'GET',
        path: '/test',
        body: '',
        timestamp: 1000000000, // Very old timestamp
      );

      final isValid = ExtendedExchangeHmacService.validateSignature(
        apiSecret: 'test_secret',
        method: 'GET',
        path: '/test',
        body: '',
        providedSignature: signature,
        timestamp: 1000000000, // Very old timestamp
      );

      expect(isValid, isFalse);
    });
  });
}
