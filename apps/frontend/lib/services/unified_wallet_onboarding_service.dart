import 'dart:developer';
import 'dart:math' as math;
import 'package:bip39/bip39.dart' as bip39;
import '../models/user.dart';
import 'secure_storage_service.dart';
import 'mobile_starknet_service.dart';
import 'wallet_import_service.dart';
import 'unified_wallet_setup_service.dart';

/// Unified Wallet Onboarding Service
/// Provides a complete wallet creation and recovery experience
/// Integrates all wallet types: fresh, import, recovery, social
class UnifiedWalletOnboardingService {
  static final MobileStarknetService _mobileStarknetService = MobileStarknetService();
  static final SecureStorageService _secureStorage = SecureStorageService.instance;
  static final WalletImportService _walletImportService = WalletImportService();

  /// Onboard with fresh wallet creation
  /// Generates new private key, mnemonic, and sets up complete trading wallet
  static Future<WalletOnboardingResult> onboardWithFreshWallet({
    required String username,
    required String email,
    String? profilePicture,
    bool generateMnemonic = true,
  }) async {
    try {
      log('🆕 Starting fresh wallet onboarding...');
      
      // Generate new wallet credentials
      final credentials = await _generateWalletCredentials(generateMnemonic);
      
      // Setup wallet with trading capabilities
      final user = await UnifiedWalletSetupService.setupWalletWithTrading(
        privateKey: credentials.privateKey,
        starknetAddress: credentials.address,
        userId: _generateUserId(),
        username: username,
        email: email,
        profilePicture: profilePicture,
      );

      // Store recovery data securely
      if (credentials.mnemonic != null) {
        await _storeMnemonicSecurely(credentials.mnemonic!);
      }

      log('✅ Fresh wallet onboarding completed successfully');
      return WalletOnboardingResult.success(
        user: user,
        mnemonic: credentials.mnemonic,
        onboardingType: OnboardingType.fresh,
      );
    } catch (e) {
      log('❌ Fresh wallet onboarding failed: $e');
      return WalletOnboardingResult.error('Failed to create fresh wallet: ${e.toString()}');
    }
  }

  /// Onboard with private key import
  /// Imports existing wallet from private key and sets up trading capabilities
  static Future<WalletOnboardingResult> onboardWithPrivateKey({
    required String privateKey,
    required String username,
    required String email,
    String? profilePicture,
  }) async {
    try {
      log('🔑 Starting private key import onboarding...');
      
      // Validate and derive address from private key
      final address = await _walletImportService.deriveAddressFromPrivateKey(privateKey);
      if (address == null) {
        throw Exception('Invalid private key');
      }

      // Setup wallet with trading capabilities
      final user = await UnifiedWalletSetupService.setupWalletWithTrading(
        privateKey: privateKey,
        starknetAddress: address,
        userId: _generateUserId(),
        username: username,
        email: email,
        profilePicture: profilePicture,
      );

      log('✅ Private key import onboarding completed successfully');
      return WalletOnboardingResult.success(
        user: user,
        onboardingType: OnboardingType.privateKey,
      );
    } catch (e) {
      log('❌ Private key import onboarding failed: $e');
      return WalletOnboardingResult.error('Failed to import private key: ${e.toString()}');
    }
  }

  /// Onboard with mnemonic recovery
  /// Recovers wallet from mnemonic phrase and sets up trading capabilities
  static Future<WalletOnboardingResult> onboardWithMnemonic({
    required String mnemonic,
    required String username,
    required String email,
    String? profilePicture,
    int accountIndex = 0,
  }) async {
    try {
      log('🔤 Starting mnemonic recovery onboarding...');
      
      // Validate mnemonic
      if (!bip39.validateMnemonic(mnemonic)) {
        throw Exception('Invalid mnemonic phrase');
      }

      // Derive private key from mnemonic
      final privateKey = await _derivePrivateKeyFromMnemonic(mnemonic, accountIndex);
      
      // Derive address from private key
      final address = await _walletImportService.deriveAddressFromPrivateKey(privateKey);
      if (address == null) {
        throw Exception('Failed to derive address from mnemonic');
      }

      // Setup wallet with trading capabilities
      final user = await UnifiedWalletSetupService.setupWalletWithTrading(
        privateKey: privateKey,
        starknetAddress: address,
        userId: _generateUserId(),
        username: username,
        email: email,
        profilePicture: profilePicture,
      );

      // Store mnemonic securely for future recovery
      await _storeMnemonicSecurely(mnemonic);

      log('✅ Mnemonic recovery onboarding completed successfully');
      return WalletOnboardingResult.success(
        user: user,
        mnemonic: mnemonic,
        onboardingType: OnboardingType.mnemonic,
      );
    } catch (e) {
      log('❌ Mnemonic recovery onboarding failed: $e');
      return WalletOnboardingResult.error('Failed to recover from mnemonic: ${e.toString()}');
    }
  }

  /// Onboard with social login (Web3Auth)
  /// Uses existing social login credentials to setup trading wallet
  static Future<WalletOnboardingResult> onboardWithSocial({
    required String privateKey,
    required String starknetAddress,
    required String userId,
    required String username,
    required String email,
    String? profilePicture,
    required String provider,
  }) async {
    try {
      log('🌐 Starting social login onboarding with $provider...');
      
      // Setup wallet with trading capabilities (no mnemonic for social)
      final user = await UnifiedWalletSetupService.setupWalletWithTrading(
        privateKey: privateKey,
        starknetAddress: starknetAddress,
        userId: userId,
        username: username,
        email: email,
        profilePicture: profilePicture,
      );

      log('✅ Social login onboarding completed successfully');
      return WalletOnboardingResult.success(
        user: user,
        onboardingType: OnboardingType.social,
        socialProvider: provider,
      );
    } catch (e) {
      log('❌ Social login onboarding failed: $e');
      return WalletOnboardingResult.error('Failed social onboarding: ${e.toString()}');
    }
  }

  /// Get wallet recovery options for existing user
  static Future<WalletRecoveryInfo> getRecoveryInfo() async {
    try {
      // Check if user has stored mnemonic
      final mnemonic = await _retrieveMnemonicSecurely();
      
      // Check if user has stored private key
      final privateKey = await _secureStorage.getPrivateKey();
      
      // Check if user has social login data
      final userData = await _secureStorage.getUserData();
      final hasSocialLogin = userData?['socialProvider'] != null;

      return WalletRecoveryInfo(
        hasMnemonic: mnemonic != null,
        hasPrivateKey: privateKey != null,
        hasSocialLogin: hasSocialLogin,
        socialProvider: userData?['socialProvider'],
      );
    } catch (e) {
      log('❌ Failed to get recovery info: $e');
      return WalletRecoveryInfo(
        hasMnemonic: false,
        hasPrivateKey: false,
        hasSocialLogin: false,
      );
    }
  }

  /// Export wallet data for backup
  static Future<WalletExportData?> exportWalletData() async {
    try {
      final privateKey = await _secureStorage.getPrivateKey();
      final address = await _secureStorage.getWalletAddress();
      final mnemonic = await _retrieveMnemonicSecurely();
      
      if (privateKey == null || address == null) {
        return null;
      }

      return WalletExportData(
        privateKey: privateKey,
        address: address,
        mnemonic: mnemonic,
        exportedAt: DateTime.now(),
      );
    } catch (e) {
      log('❌ Failed to export wallet data: $e');
      return null;
    }
  }

  /// Generate new wallet credentials (private key, address, optional mnemonic)
  static Future<WalletCredentials> _generateWalletCredentials(bool generateMnemonic) async {
    final random = math.Random.secure();
    String privateKey;
    String? mnemonic;

    if (generateMnemonic) {
      // Generate mnemonic and derive private key
      mnemonic = bip39.generateMnemonic();
      privateKey = await _derivePrivateKeyFromMnemonic(mnemonic, 0);
    } else {
      // Generate random private key
      final bytes = List<int>.generate(32, (_) => random.nextInt(256));
      privateKey = '0x${bytes.map((b) => b.toRadixString(16).padLeft(2, '0')).join()}';
    }

    // Derive address from private key
    final address = await _walletImportService.deriveAddressFromPrivateKey(privateKey);
    if (address == null) {
      throw Exception('Failed to derive address from generated private key');
    }

    return WalletCredentials(
      privateKey: privateKey,
      address: address,
      mnemonic: mnemonic,
    );
  }

  /// Derive private key from mnemonic phrase
  static Future<String> _derivePrivateKeyFromMnemonic(String mnemonic, int accountIndex) async {
    try {
      // Convert mnemonic to seed
      final seed = bip39.mnemonicToSeed(mnemonic);
      
      // For simplicity, we'll use a deterministic approach
      // In production, you'd want to use proper BIP44 derivation
      final seedHex = seed.map((b) => b.toRadixString(16).padLeft(2, '0')).join();
      final accountBytes = seedHex.substring(0, 64); // First 32 bytes
      
      return '0x$accountBytes';
    } catch (e) {
      log('❌ Failed to derive private key from mnemonic: $e');
      rethrow;
    }
  }

  /// Store mnemonic phrase securely
  static Future<void> _storeMnemonicSecurely(String mnemonic) async {
    try {
      await _secureStorage.storeValue('wallet_mnemonic', mnemonic);
      log('✅ Mnemonic stored securely');
    } catch (e) {
      log('❌ Failed to store mnemonic: $e');
      rethrow;
    }
  }

  /// Retrieve mnemonic phrase securely
  static Future<String?> _retrieveMnemonicSecurely() async {
    try {
      return await _secureStorage.getValue('wallet_mnemonic');
    } catch (e) {
      log('⚠️ Failed to retrieve mnemonic: $e');
      return null;
    }
  }

  /// Generate unique user ID
  static String _generateUserId() {
    final timestamp = DateTime.now().millisecondsSinceEpoch;
    final random = math.Random().nextInt(9999);
    return 'user_${timestamp}_$random';
  }
}

/// Wallet onboarding result
class WalletOnboardingResult {
  final bool isSuccess;
  final User? user;
  final String? mnemonic;
  final String? error;
  final OnboardingType? onboardingType;
  final String? socialProvider;

  WalletOnboardingResult._({
    required this.isSuccess,
    this.user,
    this.mnemonic,
    this.error,
    this.onboardingType,
    this.socialProvider,
  });

  factory WalletOnboardingResult.success({
    required User user,
    String? mnemonic,
    required OnboardingType onboardingType,
    String? socialProvider,
  }) {
    return WalletOnboardingResult._(
      isSuccess: true,
      user: user,
      mnemonic: mnemonic,
      onboardingType: onboardingType,
      socialProvider: socialProvider,
    );
  }

  factory WalletOnboardingResult.error(String error) {
    return WalletOnboardingResult._(
      isSuccess: false,
      error: error,
    );
  }

  @override
  String toString() {
    if (isSuccess) {
      return 'WalletOnboardingResult(success: user=${user?.email}, type=$onboardingType)';
    } else {
      return 'WalletOnboardingResult(error: $error)';
    }
  }
}

/// Types of wallet onboarding
enum OnboardingType {
  fresh,
  privateKey,
  mnemonic,
  social,
}

/// Wallet credentials generated during creation
class WalletCredentials {
  final String privateKey;
  final String address;
  final String? mnemonic;

  WalletCredentials({
    required this.privateKey,
    required this.address,
    this.mnemonic,
  });
}

/// Wallet recovery information
class WalletRecoveryInfo {
  final bool hasMnemonic;
  final bool hasPrivateKey;
  final bool hasSocialLogin;
  final String? socialProvider;

  WalletRecoveryInfo({
    required this.hasMnemonic,
    required this.hasPrivateKey,
    required this.hasSocialLogin,
    this.socialProvider,
  });

  bool get hasAnyRecoveryMethod => hasMnemonic || hasPrivateKey || hasSocialLogin;
}

/// Wallet export data for backup
class WalletExportData {
  final String privateKey;
  final String address;
  final String? mnemonic;
  final DateTime exportedAt;

  WalletExportData({
    required this.privateKey,
    required this.address,
    this.mnemonic,
    required this.exportedAt,
  });
}

/// Custom wallet onboarding exception
class WalletOnboardingException implements Exception {
  final String message;
  
  WalletOnboardingException(this.message);

  @override
  String toString() => 'WalletOnboardingException: $message';
}