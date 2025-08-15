import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../widgets/tutorial_overlay_widget.dart';

/// Tutorial state management provider
/// Tracks user's tutorial progress and manages tutorial flow
class TutorialState {
  final bool hasCompletedOnboarding;
  final bool hasCompletedTradingTutorial;
  final bool hasCompletedResultsTutorial;
  final bool isShowingTutorial;
  final String? currentTutorialId;
  final Set<String> completedTutorials;

  const TutorialState({
    this.hasCompletedOnboarding = false,
    this.hasCompletedTradingTutorial = false,
    this.hasCompletedResultsTutorial = false,
    this.isShowingTutorial = false,
    this.currentTutorialId,
    this.completedTutorials = const {},
  });

  TutorialState copyWith({
    bool? hasCompletedOnboarding,
    bool? hasCompletedTradingTutorial,
    bool? hasCompletedResultsTutorial,
    bool? isShowingTutorial,
    String? currentTutorialId,
    Set<String>? completedTutorials,
  }) {
    return TutorialState(
      hasCompletedOnboarding: hasCompletedOnboarding ?? this.hasCompletedOnboarding,
      hasCompletedTradingTutorial: hasCompletedTradingTutorial ?? this.hasCompletedTradingTutorial,
      hasCompletedResultsTutorial: hasCompletedResultsTutorial ?? this.hasCompletedResultsTutorial,
      isShowingTutorial: isShowingTutorial ?? this.isShowingTutorial,
      currentTutorialId: currentTutorialId,
      completedTutorials: completedTutorials ?? this.completedTutorials,
    );
  }
}

class TutorialNotifier extends StateNotifier<TutorialState> {
  TutorialNotifier() : super(const TutorialState()) {
    _loadTutorialState();
  }

  static const String _onboardingKey = 'tutorial_onboarding_completed';
  static const String _tradingKey = 'tutorial_trading_completed';
  static const String _resultsKey = 'tutorial_results_completed';
  static const String _completedTutorialsKey = 'tutorial_completed_list';

  /// Load tutorial state from persistent storage
  Future<void> _loadTutorialState() async {
    final prefs = await SharedPreferences.getInstance();
    
    final completedTutorialsList = prefs.getStringList(_completedTutorialsKey) ?? [];
    
    state = state.copyWith(
      hasCompletedOnboarding: prefs.getBool(_onboardingKey) ?? false,
      hasCompletedTradingTutorial: prefs.getBool(_tradingKey) ?? false,
      hasCompletedResultsTutorial: prefs.getBool(_resultsKey) ?? false,
      completedTutorials: Set<String>.from(completedTutorialsList),
    );
  }

  /// Save tutorial state to persistent storage
  Future<void> _saveTutorialState() async {
    final prefs = await SharedPreferences.getInstance();
    
    await prefs.setBool(_onboardingKey, state.hasCompletedOnboarding);
    await prefs.setBool(_tradingKey, state.hasCompletedTradingTutorial);
    await prefs.setBool(_resultsKey, state.hasCompletedResultsTutorial);
    await prefs.setStringList(_completedTutorialsKey, state.completedTutorials.toList());
  }

  /// Check if user needs to see onboarding tutorial
  bool shouldShowOnboardingTutorial() {
    return !state.hasCompletedOnboarding;
  }

  /// Check if user needs to see trading tutorial
  bool shouldShowTradingTutorial() {
    return state.hasCompletedOnboarding && !state.hasCompletedTradingTutorial;
  }

  /// Check if user needs to see results tutorial
  bool shouldShowResultsTutorial() {
    return state.hasCompletedTradingTutorial && !state.hasCompletedResultsTutorial;
  }

  /// Check if a specific tutorial has been completed
  bool hasCompletedTutorial(String tutorialId) {
    return state.completedTutorials.contains(tutorialId);
  }

  /// Start showing a tutorial
  void startTutorial(String tutorialId) {
    state = state.copyWith(
      isShowingTutorial: true,
      currentTutorialId: tutorialId,
    );
  }

  /// Mark onboarding tutorial as completed
  Future<void> completeOnboardingTutorial() async {
    state = state.copyWith(
      hasCompletedOnboarding: true,
      isShowingTutorial: false,
      currentTutorialId: null,
      completedTutorials: {...state.completedTutorials, 'onboarding'},
    );
    await _saveTutorialState();
  }

  /// Mark trading tutorial as completed
  Future<void> completeTradingTutorial() async {
    state = state.copyWith(
      hasCompletedTradingTutorial: true,
      isShowingTutorial: false,
      currentTutorialId: null,
      completedTutorials: {...state.completedTutorials, 'trading'},
    );
    await _saveTutorialState();
  }

  /// Mark results tutorial as completed
  Future<void> completeResultsTutorial() async {
    state = state.copyWith(
      hasCompletedResultsTutorial: true,
      isShowingTutorial: false,
      currentTutorialId: null,
      completedTutorials: {...state.completedTutorials, 'results'},
    );
    await _saveTutorialState();
  }

  /// Mark any tutorial as completed
  Future<void> completeTutorial(String tutorialId) async {
    state = state.copyWith(
      isShowingTutorial: false,
      currentTutorialId: null,
      completedTutorials: {...state.completedTutorials, tutorialId},
    );
    await _saveTutorialState();
  }

  /// Stop current tutorial
  void stopTutorial() {
    state = state.copyWith(
      isShowingTutorial: false,
      currentTutorialId: null,
    );
  }

  /// Reset all tutorial progress (for testing or user preference)
  Future<void> resetAllTutorials() async {
    state = const TutorialState();
    
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_onboardingKey);
    await prefs.remove(_tradingKey);
    await prefs.remove(_resultsKey);
    await prefs.remove(_completedTutorialsKey);
  }
}

/// Provider for tutorial state management
final tutorialProvider = StateNotifierProvider<TutorialNotifier, TutorialState>((ref) {
  return TutorialNotifier();
});

/// Tutorial content definitions for different features
class TutorialContent {
  /// Onboarding tutorial steps
  static List<TutorialStep> getOnboardingSteps() {
    return [
      const TutorialStep(
        title: "Welcome to AstraTrade!",
        description: "Let's get you started with a quick tour of our cosmic trading simulator.",
        tooltipPosition: Offset(20, 100),
      ),
      const TutorialStep(
        title: "Choose Your Experience",
        description: "Select your trading experience level to get personalized lessons and challenges.",
        tooltipPosition: Offset(20, 200),
      ),
      const TutorialStep(
        title: "Set Practice Amount",
        description: "Choose how much virtual money you want to practice with. Don't worry, it's not real!",
        tooltipPosition: Offset(20, 300),
      ),
      const TutorialStep(
        title: "Define Your Goals",
        description: "Tell us what you want to achieve so we can customize your learning journey.",
        tooltipPosition: Offset(20, 400),
      ),
    ];
  }

  /// Trading screen tutorial steps
  static List<TutorialStep> getTradingSteps({
    GlobalKey? amountKey,
    GlobalKey? directionKey,
    GlobalKey? symbolKey,
    GlobalKey? tradeButtonKey,
  }) {
    return [
      TutorialStep(
        title: "Choose Trade Amount",
        description: "Select how much you want to trade with. Start small while you're learning!",
        targetKey: amountKey,
        tooltipPosition: const Offset(20, 100),
      ),
      TutorialStep(
        title: "Pick Direction",
        description: "Choose BUY if you think the price will go up, or SELL if you think it will go down.",
        targetKey: directionKey,
        tooltipPosition: const Offset(20, 200),
      ),
      TutorialStep(
        title: "Select Trading Pair",
        description: "Choose which cryptocurrency pair you want to trade. Each has different risk levels.",
        targetKey: symbolKey,
        tooltipPosition: const Offset(20, 300),
      ),
      TutorialStep(
        title: "Execute Your Trade",
        description: "Ready to trade? Tap this button to place your order and see what happens!",
        targetKey: tradeButtonKey,
        tooltipPosition: const Offset(20, 500),
      ),
    ];
  }

  /// Trade results tutorial steps
  static List<TutorialStep> getResultsSteps({
    GlobalKey? resultsKey,
    GlobalKey? rewardsKey,
    GlobalKey? progressKey,
  }) {
    return [
      TutorialStep(
        title: "Your Trade Results",
        description: "Here's how your trade performed. Green means profit, red means loss - it's all part of learning!",
        targetKey: resultsKey,
        tooltipPosition: const Offset(20, 200),
      ),
      TutorialStep(
        title: "Cosmic Rewards",
        description: "Even losses earn you Stellar Shards and XP! Every trade is a learning opportunity.",
        targetKey: rewardsKey,
        tooltipPosition: const Offset(20, 400),
      ),
      TutorialStep(
        title: "Track Your Progress",
        description: "Watch your skills grow over time. Level up by completing trades and challenges!",
        targetKey: progressKey,
        tooltipPosition: const Offset(20, 600),
      ),
    ];
  }

  /// Quick tips for advanced features
  static List<TutorialStep> getAdvancedTips() {
    return [
      const TutorialStep(
        title: "Cosmic Power-Ups",
        description: "Use Stellar Shards to buy power-ups that enhance your trades and boost rewards.",
        tooltipPosition: Offset(20, 300),
      ),
      const TutorialStep(
        title: "Daily Challenges",
        description: "Complete daily challenges to earn extra rewards and accelerate your progress.",
        tooltipPosition: Offset(20, 150),
      ),
      const TutorialStep(
        title: "Leaderboard",
        description: "Compete with other traders and climb the cosmic leaderboard to unlock exclusive rewards.",
        tooltipPosition: Offset(20, 450),
      ),
    ];
  }
}

/// Helper widget to easily add tutorials to any screen
class TutorialWrapper extends ConsumerWidget {
  final Widget child;
  final String tutorialId;
  final List<TutorialStep> steps;

  const TutorialWrapper({
    super.key,
    required this.child,
    required this.tutorialId,
    required this.steps,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final tutorialState = ref.watch(tutorialProvider);
    final tutorialNotifier = ref.read(tutorialProvider.notifier);

    return TutorialOverlayWidget(
      showTutorial: tutorialState.isShowingTutorial && 
                   tutorialState.currentTutorialId == tutorialId,
      steps: steps,
      onTutorialComplete: () {
        tutorialNotifier.completeTutorial(tutorialId);
      },
      child: child,
    );
  }
}