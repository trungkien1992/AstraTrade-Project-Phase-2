import 'dart:developer';
import 'package:flutter/services.dart';
import 'package:local_auth/local_auth.dart';
import 'package:local_auth/error_codes.dart' as auth_error;
import 'secure_storage_service.dart';

/// Biometric Authentication Service
/// Handles fingerprint, face ID, and other biometric authentication methods
class BiometricAuthService {
  static BiometricAuthService? _instance;
  static BiometricAuthService get instance => _instance ??= BiometricAuthService._();

  BiometricAuthService._();

  final LocalAuthentication _localAuth = LocalAuthentication();
  final SecureStorageService _secureStorage = SecureStorageService.instance;

  static const String _biometricEnabledKey = 'biometric_enabled';
  static const String _lastBiometricCheckKey = 'last_biometric_check';

  /// Check if biometric authentication is available on the device
  Future<bool> isBiometricAvailable() async {
    try {
      final bool isAvailable = await _localAuth.canCheckBiometrics;
      final bool isDeviceSupported = await _localAuth.isDeviceSupported();
      
      log('🔐 Biometric availability: $isAvailable, Device supported: $isDeviceSupported');
      return isAvailable && isDeviceSupported;
    } catch (e) {
      log('❌ Error checking biometric availability: $e');
      return false;
    }
  }

  /// Get available biometric types (fingerprint, face, iris, etc.)
  Future<List<BiometricType>> getAvailableBiometrics() async {
    try {
      if (!await isBiometricAvailable()) {
        return [];
      }

      final List<BiometricType> availableBiometrics = await _localAuth.getAvailableBiometrics();
      log('🔐 Available biometrics: $availableBiometrics');
      return availableBiometrics;
    } catch (e) {
      log('❌ Error getting available biometrics: $e');
      return [];
    }
  }

  /// Check if user has enabled biometric authentication in app settings
  Future<bool> isBiometricEnabled() async {
    try {
      final String? enabled = await _secureStorage.getValue(_biometricEnabledKey);
      return enabled == 'true';
    } catch (e) {
      log('❌ Error checking biometric enabled status: $e');
      return false;
    }
  }

  /// Enable/disable biometric authentication in app settings
  Future<void> setBiometricEnabled(bool enabled) async {
    try {
      await _secureStorage.storeValue(_biometricEnabledKey, enabled.toString());
      log('✅ Biometric authentication ${enabled ? 'enabled' : 'disabled'}');
    } catch (e) {
      log('❌ Error setting biometric enabled status: $e');
      throw BiometricException('Failed to update biometric settings');
    }
  }

  /// Perform biometric authentication
  Future<BiometricAuthResult> authenticate({
    String reason = 'Please authenticate to access your account',
    bool biometricOnly = false,
    bool stickyAuth = false,
  }) async {
    try {
      // Check if biometric authentication is available
      if (!await isBiometricAvailable()) {
        return BiometricAuthResult.unavailable('Biometric authentication not available');
      }

      // Check if user has enabled biometrics
      if (!await isBiometricEnabled()) {
        return BiometricAuthResult.disabled('Biometric authentication is disabled');
      }

      log('🔐 Starting biometric authentication...');

      final bool didAuthenticate = await _localAuth.authenticate(
        localizedReason: reason,
        options: AuthenticationOptions(
          biometricOnly: biometricOnly,
          stickyAuth: stickyAuth,
        ),
      );

      if (didAuthenticate) {
        await _updateLastBiometricCheck();
        log('✅ Biometric authentication successful');
        return BiometricAuthResult.success();
      } else {
        log('❌ Biometric authentication failed');
        return BiometricAuthResult.failed('Authentication failed');
      }
    } on PlatformException catch (e) {
      log('❌ Biometric authentication error: ${e.code} - ${e.message}');
      return _handlePlatformException(e);
    } catch (e) {
      log('❌ Unexpected biometric authentication error: $e');
      return BiometricAuthResult.error('Unexpected error: ${e.toString()}');
    }
  }

  /// Quick biometric check for app launch
  Future<bool> quickBiometricCheck() async {
    try {
      // Only perform quick check if biometrics are available and enabled
      if (!await isBiometricAvailable() || !await isBiometricEnabled()) {
        return false;
      }

      // Check if we've done a recent biometric check (within last 5 minutes)
      if (await _hasRecentBiometricCheck()) {
        log('✅ Recent biometric check found, skipping');
        return true;
      }

      final result = await authenticate(
        reason: 'Verify your identity to continue',
        biometricOnly: true,
        stickyAuth: false,
      );

      return result.isSuccess;
    } catch (e) {
      log('❌ Quick biometric check failed: $e');
      return false;
    }
  }

  /// Get biometric authentication strength description
  Future<String> getBiometricDescription() async {
    final biometrics = await getAvailableBiometrics();
    
    if (biometrics.isEmpty) {
      return 'No biometric authentication available';
    }

    final List<String> descriptions = [];
    
    for (final biometric in biometrics) {
      switch (biometric) {
        case BiometricType.face:
          descriptions.add('Face ID');
          break;
        case BiometricType.fingerprint:
          descriptions.add('Fingerprint');
          break;
        case BiometricType.iris:
          descriptions.add('Iris scan');
          break;
        case BiometricType.strong:
          descriptions.add('Strong biometric');
          break;
        case BiometricType.weak:
          descriptions.add('Basic biometric');
          break;
      }
    }

    return descriptions.isNotEmpty ? descriptions.join(', ') : 'Biometric authentication';
  }

  /// Setup biometric authentication flow
  Future<BiometricSetupResult> setupBiometric() async {
    try {
      // Check if biometrics are available
      if (!await isBiometricAvailable()) {
        return BiometricSetupResult.unavailable('Biometric authentication not available on this device');
      }

      // Get available biometrics
      final biometrics = await getAvailableBiometrics();
      if (biometrics.isEmpty) {
        return BiometricSetupResult.unavailable('No biometric methods are set up on this device');
      }

      // Test biometric authentication
      final result = await authenticate(
        reason: 'Please authenticate to enable biometric login',
        biometricOnly: true,
      );

      if (result.isSuccess) {
        await setBiometricEnabled(true);
        return BiometricSetupResult.success('Biometric authentication enabled successfully');
      } else {
        return BiometricSetupResult.failed(result.message);
      }
    } catch (e) {
      log('❌ Biometric setup failed: $e');
      return BiometricSetupResult.error('Setup failed: ${e.toString()}');
    }
  }

  /// Disable biometric authentication
  Future<void> disableBiometric() async {
    try {
      await setBiometricEnabled(false);
      await _secureStorage.clearKey(_lastBiometricCheckKey);
      log('✅ Biometric authentication disabled');
    } catch (e) {
      log('❌ Error disabling biometric authentication: $e');
      throw BiometricException('Failed to disable biometric authentication');
    }
  }

  /// Update timestamp of last successful biometric check
  Future<void> _updateLastBiometricCheck() async {
    try {
      final timestamp = DateTime.now().millisecondsSinceEpoch.toString();
      await _secureStorage.storeValue(_lastBiometricCheckKey, timestamp);
    } catch (e) {
      log('⚠️ Failed to update last biometric check: $e');
    }
  }

  /// Check if we have a recent biometric check (within 5 minutes)
  Future<bool> _hasRecentBiometricCheck() async {
    try {
      final String? timestampStr = await _secureStorage.getValue(_lastBiometricCheckKey);
      if (timestampStr == null) return false;

      final timestamp = int.tryParse(timestampStr);
      if (timestamp == null) return false;

      final lastCheck = DateTime.fromMillisecondsSinceEpoch(timestamp);
      final now = DateTime.now();
      final difference = now.difference(lastCheck);

      return difference.inMinutes < 5;
    } catch (e) {
      log('⚠️ Error checking recent biometric check: $e');
      return false;
    }
  }

  /// Handle platform-specific biometric authentication errors
  BiometricAuthResult _handlePlatformException(PlatformException e) {
    switch (e.code) {
      case auth_error.notAvailable:
        return BiometricAuthResult.unavailable('Biometric authentication is not available');
      case auth_error.notEnrolled:
        return BiometricAuthResult.unavailable('No biometrics are enrolled on this device');
      case auth_error.lockedOut:
        return BiometricAuthResult.lockedOut('Biometric authentication is temporarily locked');
      case auth_error.permanentlyLockedOut:
        return BiometricAuthResult.lockedOut('Biometric authentication is permanently locked');
      case auth_error.biometricOnlyNotSupported:
        return BiometricAuthResult.unavailable('Biometric-only authentication not supported');
      default:
        return BiometricAuthResult.error('Authentication error: ${e.message}');
    }
  }
}

/// Result of biometric authentication attempt
class BiometricAuthResult {
  final bool isSuccess;
  final bool isUnavailable;
  final bool isDisabled;
  final bool isLockedOut;
  final String message;

  BiometricAuthResult._({
    required this.isSuccess,
    required this.isUnavailable,
    required this.isDisabled,
    required this.isLockedOut,
    required this.message,
  });

  factory BiometricAuthResult.success() {
    return BiometricAuthResult._(
      isSuccess: true,
      isUnavailable: false,
      isDisabled: false,
      isLockedOut: false,
      message: 'Authentication successful',
    );
  }

  factory BiometricAuthResult.failed(String message) {
    return BiometricAuthResult._(
      isSuccess: false,
      isUnavailable: false,
      isDisabled: false,
      isLockedOut: false,
      message: message,
    );
  }

  factory BiometricAuthResult.unavailable(String message) {
    return BiometricAuthResult._(
      isSuccess: false,
      isUnavailable: true,
      isDisabled: false,
      isLockedOut: false,
      message: message,
    );
  }

  factory BiometricAuthResult.disabled(String message) {
    return BiometricAuthResult._(
      isSuccess: false,
      isUnavailable: false,
      isDisabled: true,
      isLockedOut: false,
      message: message,
    );
  }

  factory BiometricAuthResult.lockedOut(String message) {
    return BiometricAuthResult._(
      isSuccess: false,
      isUnavailable: false,
      isDisabled: false,
      isLockedOut: true,
      message: message,
    );
  }

  factory BiometricAuthResult.error(String message) {
    return BiometricAuthResult._(
      isSuccess: false,
      isUnavailable: false,
      isDisabled: false,
      isLockedOut: false,
      message: message,
    );
  }

  @override
  String toString() {
    return 'BiometricAuthResult(success: $isSuccess, message: $message)';
  }
}

/// Result of biometric setup attempt
class BiometricSetupResult {
  final bool isSuccess;
  final bool isUnavailable;
  final String message;

  BiometricSetupResult._({
    required this.isSuccess,
    required this.isUnavailable,
    required this.message,
  });

  factory BiometricSetupResult.success(String message) {
    return BiometricSetupResult._(
      isSuccess: true,
      isUnavailable: false,
      message: message,
    );
  }

  factory BiometricSetupResult.failed(String message) {
    return BiometricSetupResult._(
      isSuccess: false,
      isUnavailable: false,
      message: message,
    );
  }

  factory BiometricSetupResult.unavailable(String message) {
    return BiometricSetupResult._(
      isSuccess: false,
      isUnavailable: true,
      message: message,
    );
  }

  factory BiometricSetupResult.error(String message) {
    return BiometricSetupResult._(
      isSuccess: false,
      isUnavailable: false,
      message: message,
    );
  }

  @override
  String toString() {
    return 'BiometricSetupResult(success: $isSuccess, message: $message)';
  }
}

/// Custom biometric authentication exception
class BiometricException implements Exception {
  final String message;
  
  BiometricException(this.message);

  @override
  String toString() => 'BiometricException: $message';
}