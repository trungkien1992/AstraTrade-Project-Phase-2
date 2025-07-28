import 'package:flutter/foundation.dart';
import 'mobile_starknet_service.dart';

/// Simplified Unified Wallet Setup Service - Mobile Native
/// Focuses only on the core functionality needed for testing
class UnifiedWalletSetupService {
  static final MobileStarknetService _mobileStarknetService = MobileStarknetService();

  /// Initialize mobile Starknet service
  static Future<void> initializeMobileService({bool useMainnet = false}) async {
    try {
      await _mobileStarknetService.initialize(useMainnet: useMainnet);
      debugPrint('✅ Mobile Starknet service initialized');
    } catch (e) {
      debugPrint('❌ Failed to initialize mobile service: $e');
      throw Exception('Failed to initialize mobile Starknet service: $e');
    }
  }

  /// Create fresh wallet using mobile-native Starknet.dart SDK
  static Future<void> createFreshWallet({
    required String username,
    required String email,
  }) async {
    try {
      debugPrint('🆕 Creating fresh wallet with mobile-native SDK...');
      
      await initializeMobileService();
      
      final walletData = await _mobileStarknetService.createWallet(
        enableBiometric: true,
      );
      
      debugPrint('✅ Fresh wallet created successfully');
      debugPrint('   Address: ${walletData.address}');
    } catch (e) {
      debugPrint('❌ Failed to create fresh wallet with mobile service: $e');
      rethrow;
    }
  }

  /// Get stored wallet data using mobile-native service
  static Future<MobileWalletData?> getStoredWallet() async {
    try {
      await initializeMobileService();
      return await _mobileStarknetService.getStoredWallet();
    } catch (e) {
      debugPrint('❌ Failed to get stored wallet with mobile service: $e');
      return null;
    }
  }
}