import 'package:flutter_test/flutter_test.dart';
import 'package:astratrade_app/services/nft_service.dart';
import 'package:mocktail/mocktail.dart';
import 'dart:io';
import 'package:http/http.dart' as http;

class MockHttpClient extends Mock implements http.Client {}

void main() {
  group('NFT Service Tests', () {
    late NFTService nftService;
    late MockHttpClient mockHttpClient;

    setUp(() {
      mockHttpClient = MockHttpClient();
      nftService = NFTService();
    });

    test('NFTService is a singleton', () {
      final service1 = NFTService();
      final service2 = NFTService();
      expect(identical(service1, service2), true);
    });

    test('Can create NFTService instance', () {
      expect(nftService, isNotNull);
    });
  });
}