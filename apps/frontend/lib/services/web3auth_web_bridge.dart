import 'dart:async';
import 'dart:convert';
import 'dart:developer';
import 'dart:js_interop';
import 'dart:js_interop_unsafe';
import 'package:web/web.dart' as web;
import 'package:web3auth_flutter/output.dart';
import 'package:web3auth_flutter/web3auth_flutter.dart';

import 'package:flutter/foundation.dart' show kIsWeb;
import '../utils/constants.dart';

/// Web3Auth JavaScript bridge for Flutter web platform
/// Interfaces with Web3Auth Modal SDK loaded via HTML script tags
class Web3AuthWebBridge {
  static Web3AuthWebBridge? _instance;
  static Web3AuthWebBridge get instance => _instance ??= Web3AuthWebBridge._();

  Web3AuthWebBridge._();

  bool _isInitialized = false;

  /// Check if running on web platform with Web3Auth SDK available
  bool get isSupported {
    if (!kIsWeb) return false;
    return _checkWeb3AuthSDK();
  }

  /// Initialize Web3Auth on web platform
  Future<void> initialize() async {
    if (_isInitialized) return;

    if (!isSupported) {
      throw Exception('Web3Auth SDK not available on this platform');
    }

    try {
      log('🌐 Initializing Web3Auth for web platform');

      final config = _createWeb3AuthConfig();
      await _initializeWeb3Auth(config);

      _isInitialized = true;
      log('✅ Web3Auth web bridge initialized successfully');
    } catch (e) {
      log('💥 Web3Auth web initialization failed: $e');
      rethrow;
    }
  }

  /// Login with Google provider
  Future<Map<String, dynamic>> loginWithGoogle() async {
    if (!_isInitialized) {
      await initialize();
    }

    try {
      log('🚀 Starting Google authentication via Web3Auth web...');

      // Call Web3Auth login with Google provider
      final result = await _loginWithProvider('google');

      if (result == null) {
        throw Exception('Login failed - no result returned');
      }

      log('✅ Google authentication successful');
      return result;
    } catch (e) {
      log('💥 Google login failed: $e');
      rethrow;
    }
  }

  /// Login with Apple provider
  Future<Map<String, dynamic>> loginWithApple() async {
    if (!_isInitialized) {
      await initialize();
    }

    try {
      log('🍎 Starting Apple authentication via Web3Auth web...');
      final result = await _loginWithProvider('apple');

      if (result == null) {
        throw Exception('Apple login failed - no result returned');
      }

      log('✅ Apple authentication successful');
      return result;
    } catch (e) {
      log('💥 Apple login failed: $e');
      rethrow;
    }
  }

  /// Login with Discord provider
  Future<Map<String, dynamic>> loginWithDiscord() async {
    if (!_isInitialized) {
      await initialize();
    }

    try {
      log('🎮 Starting Discord authentication via Web3Auth web...');
      final result = await _loginWithProvider('discord');

      if (result == null) {
        throw Exception('Discord login failed - no result returned');
      }

      log('✅ Discord authentication successful');
      return result;
    } catch (e) {
      log('💥 Discord login failed: $e');
      rethrow;
    }
  }

  /// Login with Twitter provider
  Future<Map<String, dynamic>> loginWithTwitter() async {
    if (!_isInitialized) {
      await initialize();
    }

    try {
      log('🐦 Starting Twitter authentication via Web3Auth web...');
      final result = await _loginWithProvider('twitter');

      if (result == null) {
        throw Exception('Twitter login failed - no result returned');
      }

      log('✅ Twitter authentication successful');
      return result;
    } catch (e) {
      log('💥 Twitter login failed: $e');
      rethrow;
    }
  }

  /// Login with GitHub provider
  Future<Map<String, dynamic>> loginWithGitHub() async {
    if (!_isInitialized) {
      await initialize();
    }

    try {
      log('🐙 Starting GitHub authentication via Web3Auth web...');
      final result = await _loginWithProvider('github');

      if (result == null) {
        throw Exception('GitHub login failed - no result returned');
      }

      log('✅ GitHub authentication successful');
      return result;
    } catch (e) {
      log('💥 GitHub login failed: $e');
      rethrow;
    }
  }

  /// Login with Email provider
  Future<Map<String, dynamic>> loginWithEmail(String email, String password) async {
    if (!_isInitialized) {
      await initialize();
    }

    try {
      log('📧 Starting Email authentication via Web3Auth web...');
      final result = await _loginWithProvider('email', extraParams: {
        'login_hint': email,
        'password': password,
      });

      if (result == null) {
        throw Exception('Email login failed - no result returned');
      }

      log('✅ Email authentication successful');
      return result;
    } catch (e) {
      log('💥 Email login failed: $e');
      rethrow;
    }
  }

  /// Get user information
  Future<Map<String, dynamic>?> getUserInfo() async {
    if (!_isInitialized) return null;

    try {
      final userInfo = await _getUserInfo();
      return userInfo;
    } catch (e) {
      log('⚠️  Failed to get user info: $e');
      return null;
    }
  }

  /// Get private key
  Future<String?> getPrivateKey() async {
    if (!_isInitialized) return null;

    try {
      final privateKey = await _getPrivateKey();
      return privateKey;
    } catch (e) {
      log('⚠️  Failed to get private key: $e');
      return null;
    }
  }

  /// Logout
  Future<void> logout() async {
    if (!_isInitialized) return;

    try {
      await _logout();
      log('✅ Logged out successfully');
    } catch (e) {
      log('⚠️  Logout failed: $e');
    }
  }

  /// Check if Web3Auth SDK is loaded
  bool _checkWeb3AuthSDK() {
    try {
      // Check if Web3Auth SDK is loaded in the browser
      return web.window.hasProperty('initWeb3Auth'.toJS).toDart;
    } catch (e) {
      return false;
    }
  }

  /// Create Web3Auth configuration
  Map<String, dynamic> _createWeb3AuthConfig() {
    return {
      'clientId': AppConstants.appWeb3AuthClientId,
      'web3AuthNetwork': 'sapphire_mainnet',
      'chainConfig': {
        'chainNamespace': 'other',
        'chainId': 'starknet:SN_SEPOLIA',
        'rpcTarget': 'https://starknet-sepolia.public.blastapi.io/rpc/v0_7',
        'displayName': 'Starknet Sepolia',
        'blockExplorer': 'https://sepolia.voyager.online',
        'ticker': 'ETH',
        'tickerName': 'Ethereum',
      },
      'uiConfig': {
        'appName': AppConstants.appName,
        'mode': 'dark',
        'logoLight': 'https://web3auth.io/docs/contents/logo-light.png',
        'logoDark': 'https://web3auth.io/docs/contents/logo-dark.png',
        'defaultLanguage': 'en',
        'theme': {'primary': '#7B2CBF'},
      },
    };
  }

  /// Initialize Web3Auth instance
  Future<void> _initializeWeb3Auth(Map<String, dynamic> config) async {
    try {
      log('🌐 Calling JavaScript initWeb3Auth...');

      // Call the JavaScript function we defined in index.html
      final result = await _callJavaScriptFunction('initWeb3Auth', [config]);

      if (result != true) {
        throw Exception('Web3Auth initialization returned false');
      }

      log('✅ Web3Auth web bridge initialized successfully');
    } catch (e) {
      log('💥 Web3Auth initialization error: $e');
      rethrow;
    }
  }

  /// Login with specified provider
  Future<Map<String, dynamic>?> _loginWithProvider(
    String provider, {
    Map<String, dynamic>? extraParams,
  }) async {
    try {
      log('🌐 Starting Web3Auth $provider login...');

      // Determine the JavaScript function name based on provider
      String functionName;
      List<dynamic> params = [];

      switch (provider.toLowerCase()) {
        case 'google':
          functionName = 'loginWithGoogle';
          break;
        case 'apple':
          functionName = 'loginWithApple';
          break;
        case 'discord':
          functionName = 'loginWithDiscord';
          break;
        case 'twitter':
          functionName = 'loginWithTwitter';
          break;
        case 'github':
          functionName = 'loginWithGitHub';
          break;
        case 'email':
          functionName = 'loginWithEmail';
          if (extraParams != null) {
            params = [extraParams];
          }
          break;
        default:
          functionName = 'loginWithProvider';
          params = [provider, extraParams ?? {}];
      }

      // Call the JavaScript function to show the Web3Auth popup
      final result = await _callJavaScriptFunction(functionName, params);

      if (result != true) {
        throw UserCancelledException('$provider login failed or was cancelled');
      }

      // Return a basic success indicator - user info will be fetched separately
      return {'success': true, 'provider': provider};
    } catch (e) {
      log('💥 Provider login error: $e');
      rethrow;
    }
  }

  /// Get user information from Web3Auth
  Future<Map<String, dynamic>?> _getUserInfo() async {
    try {
      log('📋 Getting user info from Web3Auth...');

      // Call the JavaScript function to get user info
      final userInfo = await _callJavaScriptFunction('getWeb3AuthUserInfo', []);

      if (userInfo is Map) {
        return Map<String, dynamic>.from(userInfo as Map);
      }

      return userInfo as Map<String, dynamic>?;
    } catch (e) {
      log('💥 Get user info error: $e');
      rethrow;
    }
  }

  /// Get private key from Web3Auth
  Future<String?> _getPrivateKey() async {
    try {
      log('🔑 Getting private key from Web3Auth...');

      // Call the JavaScript function to get private key
      final privateKey = await _callJavaScriptFunction(
        'getWeb3AuthPrivateKey',
        [],
      );

      return privateKey as String?;
    } catch (e) {
      log('💥 Get private key error: $e');
      rethrow;
    }
  }

  /// Logout from Web3Auth
  Future<void> _logout() async {
    try {
      log('🌐 Logging out from Web3Auth...');

      // Call the JavaScript function to logout
      await _callJavaScriptFunction('logoutWeb3Auth', []);
    } catch (e) {
      log('💥 Logout error: $e');
      rethrow;
    }
  }

  /// Call a JavaScript function using dart:js_interop
  Future<dynamic> _callJavaScriptFunction(
    String functionName,
    List<dynamic> args,
  ) async {
    try {
      log('🌐 Attempting to call JavaScript function: $functionName');

      // Convert the function name to a JSString and check if it exists
      final funcName = functionName.toJS;
      if (!web.window.hasProperty(funcName).toDart) {
        throw Exception('JavaScript function $functionName not found');
      }

      // Get the function and call it
      final function = web.window.getProperty(funcName);

      // Convert arguments to JavaScript objects
      final jsArgs = args.map((arg) {
        if (arg is Map) {
          return arg.jsify();
        }
        return arg?.toJS ?? null;
      }).toList();

      // Call the function and await the result
      final result = await (function as JSFunction)
          .callAsFunction(web.window, jsArgs.toJS)
          .toDart;

      log('✅ JavaScript function $functionName completed successfully');
      return result;
    } catch (e) {
      log('💥 JavaScript function call failed: $e');
      rethrow;
    }
  }
}
