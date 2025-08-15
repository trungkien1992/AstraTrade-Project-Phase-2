import 'package:flutter/services.dart' as flutter_services;

/// Cosmic haptic feedback system
class CosmicHapticFeedback {
  /// Light impact feedback
  static Future<void> lightImpact() async {
    await flutter_services.HapticFeedback.lightImpact();
  }

  /// Medium impact feedback
  static Future<void> mediumImpact() async {
    await flutter_services.HapticFeedback.mediumImpact();
  }

  /// Heavy impact feedback
  static Future<void> heavyImpact() async {
    await flutter_services.HapticFeedback.heavyImpact();
  }

  /// Selection click feedback
  static Future<void> selectionClick() async {
    await flutter_services.HapticFeedback.selectionClick();
  }

  /// Error feedback (medium impact)
  static Future<void> error() async {
    await flutter_services.HapticFeedback.mediumImpact();
  }

  /// Success feedback (light impact)
  static Future<void> success() async {
    await flutter_services.HapticFeedback.lightImpact();
  }

  /// Notification feedback (selection click)
  static Future<void> notification() async {
    await flutter_services.HapticFeedback.selectionClick();
  }
}

/// Legacy haptic feedback types
enum HapticType { selection, light, medium, heavy, success, error }

/// Legacy haptic feedback class for backwards compatibility
class HapticFeedback {
  static Future<void> triggerHaptic(HapticType type) async {
    switch (type) {
      case HapticType.selection:
        await flutter_services.HapticFeedback.selectionClick();
        break;
      case HapticType.light:
        await flutter_services.HapticFeedback.lightImpact();
        break;
      case HapticType.medium:
        await flutter_services.HapticFeedback.mediumImpact();
        break;
      case HapticType.heavy:
        await flutter_services.HapticFeedback.heavyImpact();
        break;
      case HapticType.success:
        await CosmicHapticFeedback.success();
        break;
      case HapticType.error:
        await CosmicHapticFeedback.error();
        break;
    }
  }
}
