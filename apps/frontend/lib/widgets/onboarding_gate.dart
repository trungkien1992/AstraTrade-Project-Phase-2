import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/onboarding_provider.dart';
import '../screens/trade_entry_screen.dart';
import '../onboarding/experience_level_screen.dart';

class OnboardingGate extends ConsumerWidget {
  const OnboardingGate({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final onboardingState = ref.watch(onboardingProvider);
    
    // Show onboarding flow first for complete user experience
    if (!onboardingState.isCompleted) {
      return const ExperienceLevelScreen();
    }
    
    // Show main app after onboarding is completed
    return const TradeEntryScreen();
  }
}