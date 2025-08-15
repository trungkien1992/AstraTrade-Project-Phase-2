import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../onboarding/paywall.dart';

class ExitIntentService {
  static const String _exitIntentShownKey = 'exit_intent_shown';
  static const String _lastExitIntentKey = 'last_exit_intent';
  static const int _cooldownMinutes = 60;

  static Future<bool> shouldShowExitIntent() async {
    final prefs = await SharedPreferences.getInstance();
    final hasShown = prefs.getBool(_exitIntentShownKey) ?? false;
    final lastShown = prefs.getInt(_lastExitIntentKey) ?? 0;

    if (!hasShown) return true;

    final now = DateTime.now().millisecondsSinceEpoch;
    final cooldownPassed = (now - lastShown) > (_cooldownMinutes * 60 * 1000);

    return cooldownPassed;
  }

  static Future<void> markExitIntentShown() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_exitIntentShownKey, true);
    await prefs.setInt(
      _lastExitIntentKey,
      DateTime.now().millisecondsSinceEpoch,
    );
  }

  static Future<bool?> showExitIntentDialog(BuildContext context) async {
    final shouldShow = await shouldShowExitIntent();

    if (!shouldShow) return null;

    await markExitIntentShown();

    return showDialog<bool>(
      context: context,
      barrierDismissible: false,
      builder: (context) => const ExitIntentDiscountDialog(),
    );
  }

  static void setupExitIntentDetection(
    BuildContext context,
    VoidCallback onTrigger,
  ) {
    // This would typically be triggered by app lifecycle events
    // For now, we can trigger it manually or on specific actions

    // Example: Trigger when user tries to go back from certain screens
    Navigator.of(context).canPop() ? onTrigger() : null;
  }
}
