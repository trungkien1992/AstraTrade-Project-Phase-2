import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/onboarding_data.dart';

class OnboardingState {
  final String? experienceLevel;
  final double? practiceAmount;
  final List<String> goals;
  final bool? hasNotificationPermission;
  final bool isCompleted;

  const OnboardingState({
    this.experienceLevel,
    this.practiceAmount,
    this.goals = const [],
    this.hasNotificationPermission,
    this.isCompleted = false,
  });

  OnboardingState copyWith({
    String? experienceLevel,
    double? practiceAmount,
    List<String>? goals,
    bool? hasNotificationPermission,
    bool? isCompleted,
  }) {
    return OnboardingState(
      experienceLevel: experienceLevel ?? this.experienceLevel,
      practiceAmount: practiceAmount ?? this.practiceAmount,
      goals: goals ?? this.goals,
      hasNotificationPermission: hasNotificationPermission ?? this.hasNotificationPermission,
      isCompleted: isCompleted ?? this.isCompleted,
    );
  }

  bool get canProceed {
    return experienceLevel != null && 
           practiceAmount != null && 
           goals.isNotEmpty;
  }

  OnboardingData toOnboardingData() {
    return OnboardingData(
      experienceLevel: experienceLevel!,
      practiceAmount: practiceAmount!,
      goals: goals,
      hasNotificationPermission: hasNotificationPermission ?? false,
      completedAt: DateTime.now(),
    );
  }
}

class OnboardingNotifier extends StateNotifier<OnboardingState> {
  OnboardingNotifier() : super(const OnboardingState()) {
    _loadSavedData();
  }

  Future<void> _loadSavedData() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final onboardingJson = prefs.getString('onboarding_data');
      
      // For demo purposes, always start with fresh onboarding
      // Comment this out in production and uncomment the code below
      await prefs.remove('onboarding_data');
      
      /* Production code:
      if (onboardingJson != null) {
        // User has completed onboarding before
        state = state.copyWith(isCompleted: true);
      }
      */
    } catch (e) {
      // Handle error silently
    }
  }

  void setExperienceLevel(String level) {
    state = state.copyWith(experienceLevel: level);
  }

  void setPracticeAmount(double amount) {
    state = state.copyWith(practiceAmount: amount);
  }

  void setGoals(List<String> goals) {
    state = state.copyWith(goals: goals);
  }

  void setNotificationPermission(bool granted) {
    state = state.copyWith(hasNotificationPermission: granted);
  }

  Future<void> completeOnboarding() async {
    if (!state.canProceed) return;

    try {
      final onboardingData = state.toOnboardingData();
      final prefs = await SharedPreferences.getInstance();
      
      // Save onboarding data
      await prefs.setString('onboarding_data', 
          onboardingData.toJson().toString());
      
      state = state.copyWith(isCompleted: true);
    } catch (e) {
      // Handle error
      throw Exception('Failed to save onboarding data');
    }
  }

  void resetOnboarding() {
    state = const OnboardingState();
  }

  bool shouldShowPaywallEarly() {
    // Show paywall early for high-value users
    if (state.experienceLevel == 'Advanced') return true;
    if ((state.practiceAmount ?? 0) >= 500) return true;
    if (state.goals.any((goal) => 
        goal.contains('professional') || 
        goal.contains('career') ||
        goal.contains('income'))) return true;
    
    return false;
  }
}

final onboardingProvider = StateNotifierProvider<OnboardingNotifier, OnboardingState>((ref) {
  return OnboardingNotifier();
});