import 'package:flutter/foundation.dart' show kIsWeb;

/// Platform detection utilities for cross-platform compatibility
class PlatformUtils {
  /// Check if running on web platform
  static bool get isWeb => kIsWeb;

  /// Check if running on mobile platform (iOS/Android)
  static bool get isMobile => !kIsWeb;

  /// Check if Web3Auth Flutter plugin should be used
  /// Returns true for mobile platforms where the plugin works
  static bool get useWeb3AuthFlutterPlugin => isMobile;

  /// Check if Web3Auth JavaScript bridge should be used
  /// Returns true for web platform where JavaScript SDK is available
  static bool get useWeb3AuthWebBridge => isWeb;

  /// Get platform description for logging
  static String get platformDescription {
    if (isWeb) return 'Web Platform';
    return 'Mobile Platform';
  }

  /// Check if platform supports native Web3Auth plugin
  static bool get supportsNativeWeb3Auth => isMobile;

  /// Check if platform requires JavaScript interop for Web3Auth
  static bool get requiresJavaScriptInterop => isWeb;
}
