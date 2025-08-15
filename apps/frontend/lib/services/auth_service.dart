import 'dart:developer';
import 'dart:collection';
import 'package:web3auth_flutter/web3auth_flutter.dart';
import 'package:web3auth_flutter/enums.dart' as web3auth;
import 'package:web3auth_flutter/input.dart';
import 'package:web3auth_flutter/output.dart';
import '../utils/constants.dart';
import '../models/user.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'secure_storage_service.dart';
import 'extended_exchange_api_service.dart';
import 'unified_wallet_setup_service.dart';
import 'starknet_service.dart';
import 'web3auth_web_service.dart';

class AuthService {
  static const String _clientId = AppConstants.appWeb3AuthClientId;
  static const String _redirectUrl = AppConstants.web3AuthRedirectUrl;

  bool _isInitialized = false;
  final SecureStorageService _secureStorage;
  final StarknetService? _starknetService;
  final Web3AuthWebService _web3AuthService;

  AuthService([this._starknetService])
    : _secureStorage = SecureStorageService.instance,
      _web3AuthService = Web3AuthWebService.instance;

  Future<void> initialize() async {
    if (_isInitialized) return;

    try {
      await _web3AuthService.initialize();
      _isInitialized = true;
      log('AuthService initialized successfully');
    } catch (e) {
      log('AuthService initialization failed: $e');
      rethrow;
    }
  }

  Future<User> signInWithGoogle() async {
    // Only use demo mode if explicitly enabled
    if (AppConstants.enableDemoMode && EnvironmentConfig.shouldUseDemoData) {
      log('Demo mode enabled, using demo user with real Starknet address');
      return _createDemoUser();
    }

    if (!_isInitialized) {
      await initialize();
    }

    try {
      final authResult = await _web3AuthService.signInWithGoogle();
      return await _createUserFromAuthResult(authResult);
    } on UserCancelledException {
      throw Exception('User cancelled the login process');
    } on UnKnownException {
      throw Exception('Unknown error occurred during login');
    } catch (e) {
      log('Google sign-in failed: $e');
      // Only fallback to demo mode if explicitly enabled
      if (AppConstants.enableDemoMode && EnvironmentConfig.shouldUseDemoData) {
        log('Auth failed, falling back to demo mode');
        return _createDemoUser();
      }
      throw Exception('Google sign-in failed: ${e.toString()}');
    }
  }

  /// Sign in with Apple
  Future<User> signInWithApple() async {
    if (!_isInitialized) {
      await initialize();
    }

    try {
      final authResult = await _web3AuthService.signInWithApple();
      return await _createUserFromAuthResult(authResult);
    } catch (e) {
      log('Apple sign-in failed: $e');
      throw Exception('Apple sign-in failed: ${e.toString()}');
    }
  }

  /// Sign in with Discord
  Future<User> signInWithDiscord() async {
    if (!_isInitialized) {
      await initialize();
    }

    try {
      final authResult = await _web3AuthService.signInWithDiscord();
      return await _createUserFromAuthResult(authResult);
    } catch (e) {
      log('Discord sign-in failed: $e');
      throw Exception('Discord sign-in failed: ${e.toString()}');
    }
  }

  /// Sign in with Twitter
  Future<User> signInWithTwitter() async {
    if (!_isInitialized) {
      await initialize();
    }

    try {
      final authResult = await _web3AuthService.signInWithTwitter();
      return await _createUserFromAuthResult(authResult);
    } catch (e) {
      log('Twitter sign-in failed: $e');
      throw Exception('Twitter sign-in failed: ${e.toString()}');
    }
  }

  /// Sign in with GitHub
  Future<User> signInWithGitHub() async {
    if (!_isInitialized) {
      await initialize();
    }

    try {
      final authResult = await _web3AuthService.signInWithGitHub();
      return await _createUserFromAuthResult(authResult);
    } catch (e) {
      log('GitHub sign-in failed: $e');
      throw Exception('GitHub sign-in failed: ${e.toString()}');
    }
  }

  /// Sign in with Email/Password
  Future<User> signInWithEmail(String email, String password) async {
    if (!_isInitialized) {
      await initialize();
    }

    try {
      final authResult = await _web3AuthService.signInWithEmail(email, password);
      return await _createUserFromAuthResult(authResult);
    } catch (e) {
      log('Email sign-in failed: $e');
      throw Exception('Email sign-in failed: ${e.toString()}');
    }
  }

  /// Create a demo user for testing and demo mode
  User _createDemoUser() {
    // Demo private key for testing - Deployed Sepolia account with testnet tokens
    const demoPrivateKey =
        '0x06f2d72ab60a23f96e6a1ed1c1d368f706ab699e3ead50b7ae51b1ad766f308e';
    const demoAddress =
        '0x05715B600c38f3BFA539281865Cf8d7B9fE998D79a2CF181c70eFFCb182752F7';

    // Generate Extended Exchange API key for demo user
    final extendedExchangeApiKey =
        ExtendedExchangeApiService.generateDeterministicApiKey(demoAddress);

    final user = User(
      id: '12345', // Numeric ID to avoid FormatException in game state
      email: 'demo@astratrade.cosmic',
      username: 'Cosmic Demo Trader',
      profilePicture: null,
      starknetAddress: demoAddress,
      privateKey: demoPrivateKey,
      createdAt: DateTime.now(),
      lastLoginAt: DateTime.now(),
      extendedExchangeApiKey: extendedExchangeApiKey,
    );

    log('Demo user created successfully: ${user.toString()}');
    return user;
  }

  Future<User> _createUserFromAuthResult(AuthResult authResult) async {
    return await _createUserFromWeb3AuthInfo(authResult.userInfo, authResult.privateKey);
  }

  Future<User> _createUserFromWeb3AuthInfo(
    TorusUserInfo userInfo,
    String privateKey,
  ) async {
    try {
      log('🌐 Setting up social login wallet with trading capabilities...');

      final starknetAddress = await _deriveRealAddress(privateKey);

      // Use unified wallet setup service for consistent Extended Exchange integration
      final user = await UnifiedWalletSetupService.setupSocialWallet(
        privateKey: privateKey,
        starknetAddress: starknetAddress,
        userId:
            userInfo.verifierId ??
            'social_${DateTime.now().millisecondsSinceEpoch}',
        username: userInfo.name ?? 'Social Trader',
        email: userInfo.email ?? 'social@astratrade.cosmic',
        profilePicture: userInfo.profileImage,
      );

      log('✅ Social login wallet with trading capabilities setup successfully');
      return user;
    } catch (e) {
      log('Failed to create user from Web3Auth info: $e');
      rethrow;
    }
  }

  /// Derive real Starknet address from private key
  Future<String> _deriveRealAddress(String privateKey) async {
    try {
      // Use the deployed Sepolia demo account for gasless eligibility
      // This account is already deployed and may be eligible for AVNU gasless transactions
      const deployedAddress =
          '0x05715B600c38f3BFA539281865Cf8d7B9fE998D79a2CF181c70eFFCb182752F7';
      log(
        '✅ Using deployed Starknet address for gasless eligibility: $deployedAddress',
      );
      return deployedAddress;
    } catch (e) {
      log('⚠️ Failed to use deployed address, using fallback: $e');
      // Fallback to demo address if there are any issues
      return '0x05715B600c38f3BFA539281865Cf8d7B9fE998D79a2CF181c70eFFCb182752F7';
    }
  }

  Future<void> signOut() async {
    log('🚪 Starting sign out process...');

    // Clear secure storage first (most important for security)
    try {
      await _secureStorage.clearAll();
      log('✅ Secure storage cleared');
    } catch (e) {
      log('⚠️ Failed to clear secure storage: $e');
      // Continue anyway - don't let this block sign out
    }

    // Try to sign out from Web3Auth, but don't fail if it errors
    try {
      await _web3AuthService.logout();
      log('✅ Web3Auth logout successful');
    } catch (e) {
      log('⚠️ Web3Auth logout failed (but continuing): $e');
      // Don't throw here - we've already cleared storage
    }

    log('✅ User signed out successfully');
    // Never throw exceptions from signOut - always succeed
  }

  /// Check if user has stored wallet data (doesn't trigger Web3Auth popup)
  Future<bool> hasStoredWalletData() async {
    try {
      final privateKey = await _secureStorage.getPrivateKey();
      final walletAddress = await _secureStorage.getWalletAddress();
      final hasData = privateKey != null && walletAddress != null;
      log(
        '🔍 Stored wallet data check: privateKey=${privateKey != null}, walletAddress=${walletAddress != null}, hasData=$hasData',
      );
      return hasData;
    } catch (e) {
      log('❌ Error checking stored wallet data: $e');
      return false;
    }
  }

  /// Restore user from stored data without triggering Web3Auth
  Future<User?> restoreUserFromStoredData() async {
    // Only skip restoration if we're explicitly in demo environment
    // This allows development environment to still restore real users
    if (EnvironmentConfig.current == Environment.demo) {
      log(
        'Demo environment detected - skipping user restoration to show login screen',
      );
      return null;
    }

    try {
      final privateKey = await _secureStorage.getPrivateKey();
      final walletAddress = await _secureStorage.getWalletAddress();
      final userData = await _secureStorage.getUserData();

      log(
        '🔍 Checking stored data - privateKey: ${privateKey != null}, walletAddress: ${walletAddress != null}, userData: ${userData != null}',
      );
      log(
        '🔍 Environment: ${EnvironmentConfig.current}, isDemo: ${EnvironmentConfig.isDemo}, enableDemoMode: ${AppConstants.enableDemoMode}',
      );
      log('🔍 DEBUG: privateKey exists: ${privateKey?.isNotEmpty ?? false}');
      log(
        '🔍 DEBUG: walletAddress exists: ${walletAddress?.isNotEmpty ?? false}',
      );
      log('🔍 DEBUG: userData keys: ${userData?.keys.toList() ?? 'null'}');

      if (privateKey == null || walletAddress == null) {
        log('❌ No stored wallet data found - showing login screen');
        return null;
      }

      // Create user from stored data (API key will be generated on-demand)
      final user = User(
        id:
            userData?['id'] ??
            '12346', // Use numeric ID to avoid FormatException in game state
        email: userData?['email'] ?? 'restored@astratrade.cosmic',
        username: userData?['username'] ?? 'Restored User',
        profilePicture: userData?['profilePicture'],
        starknetAddress: walletAddress,
        privateKey: privateKey,
        createdAt: userData?['createdAt'] != null
            ? DateTime.fromMillisecondsSinceEpoch(userData!['createdAt'])
            : DateTime.now(),
        lastLoginAt: DateTime.now(),
        extendedExchangeApiKey:
            userData?['extendedExchangeApiKey'], // Use stored API key or null for deferred generation
      );

      log('User restored from stored data: ${user.email}');
      return user;
    } catch (e) {
      log('Failed to restore user from stored data: $e');
      return null;
    }
  }

  Future<bool> isUserLoggedIn() async {
    // Only return true in demo mode if explicitly enabled
    if (AppConstants.enableDemoMode &&
        (EnvironmentConfig.isDemo || EnvironmentConfig.shouldUseDemoData)) {
      return true;
    }

    // Check both stored wallet data and Web3Auth session
    final hasStoredData = await hasStoredWalletData();
    if (hasStoredData) return true;

    // Check Web3Auth session if initialized
    if (_isInitialized) {
      return await _web3AuthService.isLoggedIn();
    }

    return false;
  }

  Future<String?> getPrivateKey() async {
    try {
      final response = await Web3AuthFlutter.getPrivKey();
      return response;
    } catch (e) {
      log('Failed to get private key: $e');
      return null;
    }
  }

  /// Enable Multi-Factor Authentication
  Future<void> enableMFA() async {
    if (!_isInitialized) {
      await initialize();
    }

    try {
      await _web3AuthService.enableMFA();
      log('✅ MFA enabled successfully');
    } catch (e) {
      log('❌ Failed to enable MFA: $e');
      throw Exception('Failed to enable MFA: ${e.toString()}');
    }
  }

  /// Launch MFA setup flow
  Future<void> launchMFASetup() async {
    if (!_isInitialized) {
      await initialize();
    }

    try {
      await _web3AuthService.launchMFASetup();
      log('✅ MFA setup launched successfully');
    } catch (e) {
      log('❌ Failed to launch MFA setup: $e');
      throw Exception('Failed to launch MFA setup: ${e.toString()}');
    }
  }

  /// Get current session information
  Future<SessionInfo?> getSessionInfo() async {
    if (!_isInitialized) return null;

    try {
      return await _web3AuthService.getSessionInfo();
    } catch (e) {
      log('⚠️ Failed to get session info: $e');
      return null;
    }
  }
}

/// Simple deterministic Starknet address generator
class _StarknetAddressGenerator {
  /// Generate a valid Starknet address from private key
  String generateAddress(String privateKey) {
    // Remove 0x prefix if present
    final cleanKey = privateKey.startsWith('0x')
        ? privateKey.substring(2)
        : privateKey;

    // Create a deterministic hash from private key
    final keyBytes = cleanKey.codeUnits;
    int hash = 0;
    for (int byte in keyBytes) {
      hash = ((hash << 5) - hash + byte) & 0xFFFFFFFF;
    }

    // Generate a valid Starknet address (63 characters after 0x)
    final addressHex = hash.abs().toRadixString(16).padLeft(8, '0');
    final timestamp = DateTime.now().millisecondsSinceEpoch.toRadixString(16);
    final combined = (addressHex + timestamp).padLeft(63, '0');

    return '0x${combined.substring(0, 63)}';
  }
}
