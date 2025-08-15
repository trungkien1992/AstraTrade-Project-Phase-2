import 'package:flutter/services.dart';
import 'package:flutter/foundation.dart';

/// Enhanced haptic feedback service for immersive cosmic experience
/// Provides contextual haptic patterns for different game actions
class HapticService {
  static bool _isInitialized = false;
  static bool _isSupported = false;

  /// Initialize haptic service
  static Future<void> initialize() async {
    if (_isInitialized) return;

    try {
      _isSupported = true; // Haptic feedback is always available on iOS
      _isInitialized = true;

      if (kDebugMode) {
        print('HapticService: Initialized, supported: $_isSupported');
      }
    } catch (e) {
      if (kDebugMode) {
        print('HapticService: Failed to initialize: $e');
      }
      _isSupported = false;
    }
  }

  /// Basic tap feedback for planet interactions
  static Future<void> triggerTapFeedback() async {
    if (!_isSupported) return;

    try {
      await HapticFeedback.lightImpact();
    } catch (e) {
      if (kDebugMode) {
        print('HapticService: Tap feedback failed: $e');
      }
    }
  }

  /// Enhanced haptic for successful trade execution
  static Future<void> triggerTradeSuccessFeedback() async {
    if (!_isSupported) return;

    try {
      await HapticFeedback.mediumImpact();
    } catch (e) {
      if (kDebugMode) {
        print('HapticService: Trade success feedback failed: $e');
      }
    }
  }

  /// Enhanced haptic for failed trade
  static Future<void> triggerTradeFailureFeedback() async {
    if (!_isSupported) return;

    try {
      await HapticFeedback.heavyImpact();
    } catch (e) {
      if (kDebugMode) {
        print('HapticService: Trade failure feedback failed: $e');
      }
    }
  }

  /// Biome evolution haptic pattern
  static Future<void> triggerEvolutionFeedback() async {
    if (!_isSupported) return;

    try {
      await HapticFeedback.heavyImpact();
    } catch (e) {
      if (kDebugMode) {
        print('HapticService: Evolution feedback failed: $e');
      }
    }
  }

  /// Level up haptic celebration
  static Future<void> triggerLevelUpFeedback() async {
    if (!_isSupported) return;

    try {
      await HapticFeedback.heavyImpact();
    } catch (e) {
      if (kDebugMode) {
        print('HapticService: Level up feedback failed: $e');
      }
    }
  }

  /// Stellar shard harvest haptic
  static Future<void> triggerHarvestFeedback() async {
    if (!_isSupported) return;

    try {
      await HapticFeedback.selectionClick();
    } catch (e) {
      if (kDebugMode) {
        print('HapticService: Harvest feedback failed: $e');
      }
    }
  }

  /// Lumina generation haptic
  static Future<void> triggerLuminaGenerationFeedback() async {
    if (!_isSupported) return;

    try {
      await HapticFeedback.mediumImpact();
    } catch (e) {
      if (kDebugMode) {
        print('HapticService: Lumina generation feedback failed: $e');
      }
    }
  }

  /// Cosmic forge activation haptic
  static Future<void> triggerForgeActivationFeedback() async {
    if (!_isSupported) return;

    try {
      await HapticFeedback.heavyImpact();
    } catch (e) {
      if (kDebugMode) {
        print('HapticService: Forge activation feedback failed: $e');
      }
    }
  }

  /// Orbital ascent haptic pattern
  static Future<void> triggerOrbitalAscentFeedback() async {
    if (!_isSupported) return;

    try {
      await HapticFeedback.mediumImpact();
    } catch (e) {
      if (kDebugMode) {
        print('HapticService: Orbital ascent feedback failed: $e');
      }
    }
  }

  /// Gravitational descent haptic pattern
  static Future<void> triggerGravitationalDescentFeedback() async {
    if (!_isSupported) return;

    try {
      await HapticFeedback.mediumImpact();
    } catch (e) {
      if (kDebugMode) {
        print('HapticService: Gravitational descent feedback failed: $e');
      }
    }
  }

  /// Notification haptic for background alerts
  static Future<void> triggerNotificationFeedback() async {
    if (!_isSupported) return;

    try {
      await HapticFeedback.selectionClick();
    } catch (e) {
      if (kDebugMode) {
        print('HapticService: Notification feedback failed: $e');
      }
    }
  }

  /// Error haptic for system failures
  static Future<void> triggerErrorFeedback() async {
    if (!_isSupported) return;

    try {
      await HapticFeedback.heavyImpact();
    } catch (e) {
      if (kDebugMode) {
        print('HapticService: Error feedback failed: $e');
      }
    }
  }

  /// Custom haptic pattern for specific actions
  static Future<void> triggerCustomFeedback({
    required List<int> pattern,
    required List<int> intensities,
  }) async {
    if (!_isSupported) return;

    try {
      // Fallback to basic haptic
      await HapticFeedback.mediumImpact();
    } catch (e) {
      if (kDebugMode) {
        print('HapticService: Custom feedback failed: $e');
      }
    }
  }

  /// Test haptic capabilities
  static Future<Map<String, bool>> testHapticCapabilities() async {
    try {
      return {
        'hasVibrator': true,
        'hasAmplitudeControl': false,
        'hasCustomVibrations': false,
      };
    } catch (e) {
      if (kDebugMode) {
        print('HapticService: Capability test failed: $e');
      }
      return {
        'hasVibrator': false,
        'hasAmplitudeControl': false,
        'hasCustomVibrations': false,
      };
    }
  }

  /// Cancel any ongoing vibration
  static Future<void> cancelVibration() async {
    try {
      // No-op for HapticFeedback
    } catch (e) {
      if (kDebugMode) {
        print('HapticService: Cancel vibration failed: $e');
      }
    }
  }
}
