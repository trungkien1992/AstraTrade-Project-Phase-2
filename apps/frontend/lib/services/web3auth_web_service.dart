import 'dart:async';
import 'dart:developer';
import 'dart:collection';
import 'package:web3auth_flutter/web3auth_flutter.dart';
import 'package:web3auth_flutter/enums.dart' as web3auth;
import 'package:web3auth_flutter/input.dart';
import 'package:web3auth_flutter/output.dart';
import '../utils/constants.dart';

/// Comprehensive Web3Auth service supporting all 6 login providers
/// Supports Google, Apple, Discord, Twitter, GitHub, and Email authentication
class Web3AuthWebService {
  static Web3AuthWebService? _instance;
  static Web3AuthWebService get instance => _instance ??= Web3AuthWebService._();

  Web3AuthWebService._();

  bool _isInitialized = false;

  /// Initialize Web3Auth with v6.2.0 configuration
  Future<void> initialize() async {
    if (_isInitialized) return;

    try {
      log('🌐 Initializing Web3Auth v6.2.0...');

      await Web3AuthFlutter.init(
        Web3AuthOptions(
          clientId: AppConstants.appWeb3AuthClientId,
          network: web3auth.Network.sapphire_mainnet,
          redirectUrl: Uri.parse(AppConstants.web3AuthRedirectUrl),
          whiteLabel: WhiteLabelData(
            appName: AppConstants.appName,
            logoLight: "https://astratrade.io/logo-light.png",
            logoDark: "https://astratrade.io/logo-dark.png",
            defaultLanguage: web3auth.Language.en,
            mode: web3auth.ThemeModes.dark,
            theme: HashMap.from({
              "primary": "#7B2CBF",
              "gray": "#1a1a1a",
              "red": "#ef4444",
              "green": "#22c55e",
              "success": "#22c55e",
              "warning": "#f59e0b",
              "error": "#ef4444",
              "info": "#3b82f6",
            }),
          ),
        ),
      );

      _isInitialized = true;
      log('✅ Web3Auth v6.2.0 initialized successfully');
    } catch (e) {
      log('❌ Web3Auth initialization failed: $e');
      rethrow;
    }
  }

  /// Login with Google OAuth
  Future<AuthResult> signInWithGoogle() async {
    if (!_isInitialized) await initialize();

    try {
      log('🚀 Starting Google OAuth login...');

      await Web3AuthFlutter.login(
        LoginParams(
          loginProvider: web3auth.Provider.google,
          extraLoginOptions: ExtraLoginOptions(
            domain: AppConstants.web3AuthDomain,
            prompt: web3auth.Prompt.login,
            scope: 'openid email profile',
            response_type: 'code',
            connection: '',
          ),
        ),
      );

      return await _getAuthResult('Google');
    } catch (e) {
      log('❌ Google login failed: $e');
      throw AuthException('Google login failed: ${e.toString()}');
    }
  }

  /// Login with Apple Sign-in
  Future<AuthResult> signInWithApple() async {
    if (!_isInitialized) await initialize();

    try {
      log('🍎 Starting Apple Sign-in...');

      await Web3AuthFlutter.login(
        LoginParams(
          loginProvider: web3auth.Provider.jwt,
          extraLoginOptions: ExtraLoginOptions(
            domain: AppConstants.web3AuthDomain,
            verifierIdField: 'sub',
            connection: 'apple',
            prompt: web3auth.Prompt.login,
          ),
        ),
      );

      return await _getAuthResult('Apple');
    } catch (e) {
      log('❌ Apple login failed: $e');
      throw AuthException('Apple login failed: ${e.toString()}');
    }
  }

  /// Login with Discord
  Future<AuthResult> signInWithDiscord() async {
    if (!_isInitialized) await initialize();

    try {
      log('🎮 Starting Discord login...');

      await Web3AuthFlutter.login(
        LoginParams(
          loginProvider: web3auth.Provider.discord,
          extraLoginOptions: ExtraLoginOptions(
            domain: AppConstants.web3AuthDomain,
            prompt: web3auth.Prompt.login,
            scope: 'identify email',
          ),
        ),
      );

      return await _getAuthResult('Discord');
    } catch (e) {
      log('❌ Discord login failed: $e');
      throw AuthException('Discord login failed: ${e.toString()}');
    }
  }

  /// Login with Twitter
  Future<AuthResult> signInWithTwitter() async {
    if (!_isInitialized) await initialize();

    try {
      log('🐦 Starting Twitter login...');

      await Web3AuthFlutter.login(
        LoginParams(
          loginProvider: web3auth.Provider.twitter,
          extraLoginOptions: ExtraLoginOptions(
            domain: AppConstants.web3AuthDomain,
            prompt: web3auth.Prompt.login,
          ),
        ),
      );

      return await _getAuthResult('Twitter');
    } catch (e) {
      log('❌ Twitter login failed: $e');
      throw AuthException('Twitter login failed: ${e.toString()}');
    }
  }

  /// Login with GitHub
  Future<AuthResult> signInWithGitHub() async {
    if (!_isInitialized) await initialize();

    try {
      log('🐙 Starting GitHub login...');

      await Web3AuthFlutter.login(
        LoginParams(
          loginProvider: web3auth.Provider.github,
          extraLoginOptions: ExtraLoginOptions(
            domain: AppConstants.web3AuthDomain,
            prompt: web3auth.Prompt.login,
            scope: 'user:email',
          ),
        ),
      );

      return await _getAuthResult('GitHub');
    } catch (e) {
      log('❌ GitHub login failed: $e');
      throw AuthException('GitHub login failed: ${e.toString()}');
    }
  }

  /// Login with Email/Password
  Future<AuthResult> signInWithEmail(String email, String password) async {
    if (!_isInitialized) await initialize();

    try {
      log('📧 Starting Email/Password login...');

      await Web3AuthFlutter.login(
        LoginParams(
          loginProvider: web3auth.Provider.email_passwordless,
          extraLoginOptions: ExtraLoginOptions(
            domain: AppConstants.web3AuthDomain,
            login_hint: email,
            prompt: web3auth.Prompt.login,
          ),
        ),
      );

      return await _getAuthResult('Email');
    } catch (e) {
      log('❌ Email login failed: $e');
      throw AuthException('Email login failed: ${e.toString()}');
    }
  }

  /// Get authentication result with user info and private key
  Future<AuthResult> _getAuthResult(String provider) async {
    try {
      final privateKey = await Web3AuthFlutter.getPrivKey();
      if (privateKey.isEmpty) {
        throw Exception('Failed to retrieve private key');
      }

      final userInfo = await Web3AuthFlutter.getUserInfo();
      
      log('✅ $provider authentication successful');
      log('📋 User info: ${userInfo.email} (${userInfo.name})');
      
      return AuthResult(
        userInfo: userInfo,
        privateKey: privateKey,
        provider: provider,
      );
    } catch (e) {
      log('❌ Failed to get auth result: $e');
      rethrow;
    }
  }

  /// Enable Multi-Factor Authentication
  Future<void> enableMFA() async {
    if (!_isInitialized) {
      throw Exception('Web3Auth not initialized');
    }

    try {
      log('🔐 Enabling MFA...');
      
      // TODO: MFA APIs not available in current version
      // This would call Web3Auth MFA enable API when available
      log('⚠️ MFA enable API not yet available in current Web3Auth version');
      
    } catch (e) {
      log('❌ Failed to enable MFA: $e');
      throw AuthException('Failed to enable MFA: ${e.toString()}');
    }
  }

  /// Launch MFA setup flow
  Future<void> launchMFASetup() async {
    if (!_isInitialized) {
      throw Exception('Web3Auth not initialized');
    }

    try {
      log('⚙️ Launching MFA setup...');
      
      // TODO: MFA setup UI not available in current version
      // This would launch Web3Auth MFA setup UI when available
      log('⚠️ MFA setup UI not yet available in current Web3Auth version');
      
    } catch (e) {
      log('❌ Failed to launch MFA setup: $e');
      throw AuthException('Failed to launch MFA setup: ${e.toString()}');
    }
  }

  /// Get current session information
  Future<SessionInfo?> getSessionInfo() async {
    if (!_isInitialized) return null;

    try {
      final userInfo = await Web3AuthFlutter.getUserInfo();
      final privateKey = await Web3AuthFlutter.getPrivKey();
      
      if (privateKey.isEmpty) return null;

      return SessionInfo(
        isLoggedIn: true,
        userInfo: userInfo,
        privateKey: privateKey,
      );
    } catch (e) {
      log('⚠️ Failed to get session info: $e');
      return null;
    }
  }

  /// Logout from Web3Auth
  Future<void> logout() async {
    if (!_isInitialized) return;

    try {
      log('🚪 Logging out from Web3Auth...');
      await Web3AuthFlutter.logout();
      log('✅ Logout successful');
    } catch (e) {
      log('⚠️ Logout failed: $e');
      // Don't throw - logout should always succeed
    }
  }

  /// Check if user is logged in
  Future<bool> isLoggedIn() async {
    if (!_isInitialized) return false;

    try {
      final privateKey = await Web3AuthFlutter.getPrivKey();
      return privateKey.isNotEmpty;
    } catch (e) {
      return false;
    }
  }
}

/// Authentication result containing user info and private key
class AuthResult {
  final TorusUserInfo userInfo;
  final String privateKey;
  final String provider;

  AuthResult({
    required this.userInfo,
    required this.privateKey,
    required this.provider,
  });

  @override
  String toString() {
    return 'AuthResult(provider: $provider, email: ${userInfo.email}, name: ${userInfo.name})';
  }
}

/// Session information
class SessionInfo {
  final bool isLoggedIn;
  final TorusUserInfo userInfo;
  final String privateKey;

  SessionInfo({
    required this.isLoggedIn,
    required this.userInfo,
    required this.privateKey,
  });
}

/// Custom authentication exception
class AuthException implements Exception {
  final String message;
  
  AuthException(this.message);

  @override
  String toString() => 'AuthException: $message';
}