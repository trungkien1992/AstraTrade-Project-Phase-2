import 'dart:async';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'analytics_service.dart';
import 'ab_testing_service.dart';
import 'ab_test_analyzer_service.dart';

enum OptimizationStrategy {
  exit_intent_capture,
  progressive_disclosure,
  social_proof_injection,
  urgency_creation,
  value_reinforcement,
  friction_reduction,
}

class ConversionOptimization {
  final String optimizationId;
  final OptimizationStrategy strategy;
  final String targetStep;
  final Map<String, dynamic> parameters;
  final bool isActive;
  final double expectedLift;

  ConversionOptimization({
    required this.optimizationId,
    required this.strategy,
    required this.targetStep,
    required this.parameters,
    this.isActive = true,
    this.expectedLift = 0.0,
  });

  Map<String, dynamic> toJson() {
    return {
      'optimization_id': optimizationId,
      'strategy': strategy.name,
      'target_step': targetStep,
      'parameters': parameters,
      'is_active': isActive,
      'expected_lift': expectedLift,
    };
  }
}

class ConversionOptimizationService {
  static const String _optimizationsKey = 'active_optimizations';
  static const String _userBehaviorKey = 'user_behavior_patterns';

  static final List<ConversionOptimization> _activeOptimizations = [];
  static Timer? _optimizationTimer;

  // Initialize optimization service
  static Future<void> initialize() async {
    await _loadActiveOptimizations();
    await _startOptimizationMonitoring();
  }

  static Future<void> _loadActiveOptimizations() async {
    final prefs = await SharedPreferences.getInstance();
    final optimizationsData = prefs.getStringList(_optimizationsKey) ?? [];

    _activeOptimizations.clear();

    // Default optimizations
    _activeOptimizations.addAll([
      ConversionOptimization(
        optimizationId: 'exit_intent_paywall',
        strategy: OptimizationStrategy.exit_intent_capture,
        targetStep: 'app_exit',
        parameters: {
          'trigger_delay_ms': 500,
          'discount_percentage': 70,
          'message': 'Wait! Get 70% off before you go',
        },
        expectedLift: 15.0,
      ),
      ConversionOptimization(
        optimizationId: 'onboarding_progressive',
        strategy: OptimizationStrategy.progressive_disclosure,
        targetStep: 'onboarding_start',
        parameters: {
          'max_steps_per_screen': 2,
          'progress_visibility': true,
          'skip_option_delay_ms': 3000,
        },
        expectedLift: 12.0,
      ),
      ConversionOptimization(
        optimizationId: 'social_proof_paywall',
        strategy: OptimizationStrategy.social_proof_injection,
        targetStep: 'paywall_view',
        parameters: {
          'user_count': 50000,
          'recent_signups': 247,
          'testimonials_enabled': true,
        },
        expectedLift: 8.0,
      ),
      ConversionOptimization(
        optimizationId: 'urgency_timer',
        strategy: OptimizationStrategy.urgency_creation,
        targetStep: 'paywall_view',
        parameters: {
          'countdown_hours': 24,
          'scarcity_spots': 100,
          'flash_sale_enabled': true,
        },
        expectedLift: 22.0,
      ),
    ]);
  }

  static Future<void> _startOptimizationMonitoring() async {
    _optimizationTimer = Timer.periodic(
      const Duration(minutes: 5),
      (_) => _evaluateAndOptimize(),
    );
  }

  // Real-time optimization based on user behavior
  static Future<void> optimizeUserJourney(
    String currentStep,
    Map<String, dynamic> userContext,
  ) async {
    final applicableOptimizations = _activeOptimizations
        .where((opt) => opt.isActive && opt.targetStep == currentStep)
        .toList();

    for (final optimization in applicableOptimizations) {
      await _applyOptimization(optimization, userContext);
    }
  }

  static Future<void> _applyOptimization(
    ConversionOptimization optimization,
    Map<String, dynamic> userContext,
  ) async {
    switch (optimization.strategy) {
      case OptimizationStrategy.exit_intent_capture:
        await _handleExitIntentOptimization(optimization, userContext);
        break;
      case OptimizationStrategy.progressive_disclosure:
        await _handleProgressiveDisclosure(optimization, userContext);
        break;
      case OptimizationStrategy.social_proof_injection:
        await _handleSocialProofInjection(optimization, userContext);
        break;
      case OptimizationStrategy.urgency_creation:
        await _handleUrgencyCreation(optimization, userContext);
        break;
      case OptimizationStrategy.value_reinforcement:
        await _handleValueReinforcement(optimization, userContext);
        break;
      case OptimizationStrategy.friction_reduction:
        await _handleFrictionReduction(optimization, userContext);
        break;
    }

    // Track optimization application
    await AnalyticsService.trackEvent(
      name: 'optimization_applied',
      type: EventType.user_action,
      properties: {
        'optimization_id': optimization.optimizationId,
        'strategy': optimization.strategy.name,
        'target_step': optimization.targetStep,
        'user_context': userContext,
      },
    );
  }

  // Exit intent optimization
  static Future<void> _handleExitIntentOptimization(
    ConversionOptimization optimization,
    Map<String, dynamic> userContext,
  ) async {
    final params = optimization.parameters;

    // Check if user is about to leave without subscribing
    final hasSubscription = userContext['has_subscription'] ?? false;
    final timeSpent = userContext['time_spent_seconds'] ?? 0;

    if (!hasSubscription && timeSpent > 30) {
      // Schedule exit intent trigger
      Timer(Duration(milliseconds: params['trigger_delay_ms'] ?? 500), () {
        _triggerExitIntentOffer(params);
      });
    }
  }

  static void _triggerExitIntentOffer(Map<String, dynamic> params) {
    // This would trigger an exit intent modal in practice
    AnalyticsService.trackEvent(
      name: 'exit_intent_triggered',
      type: EventType.user_action,
      properties: params,
    );
  }

  // Progressive disclosure optimization
  static Future<void> _handleProgressiveDisclosure(
    ConversionOptimization optimization,
    Map<String, dynamic> userContext,
  ) async {
    final params = optimization.parameters;

    // Optimize onboarding flow based on user type
    final experienceLevel = userContext['experience_level'] ?? 'Beginner';

    if (experienceLevel == 'Beginner') {
      // Show simplified flow for beginners
      await AnalyticsService.trackEvent(
        name: 'progressive_disclosure_simplified',
        type: EventType.user_action,
        properties: {
          'max_steps': params['max_steps_per_screen'],
          'user_level': experienceLevel,
        },
      );
    }
  }

  // Social proof injection
  static Future<void> _handleSocialProofInjection(
    ConversionOptimization optimization,
    Map<String, dynamic> userContext,
  ) async {
    final params = optimization.parameters;

    // Add social proof elements based on context
    final socialProofData = {
      'total_users': params['user_count'],
      'recent_signups': params['recent_signups'],
      'show_testimonials': params['testimonials_enabled'],
    };

    await AnalyticsService.trackEvent(
      name: 'social_proof_displayed',
      type: EventType.user_action,
      properties: socialProofData,
    );
  }

  // Urgency creation
  static Future<void> _handleUrgencyCreation(
    ConversionOptimization optimization,
    Map<String, dynamic> userContext,
  ) async {
    final params = optimization.parameters;

    // Create urgency based on user behavior
    final sessionCount = userContext['session_count'] ?? 1;

    if (sessionCount >= 2) {
      // Show urgency for returning users
      await AnalyticsService.trackEvent(
        name: 'urgency_elements_shown',
        type: EventType.user_action,
        properties: {
          'countdown_hours': params['countdown_hours'],
          'scarcity_spots': params['scarcity_spots'],
          'user_session_count': sessionCount,
        },
      );
    }
  }

  // Value reinforcement
  static Future<void> _handleValueReinforcement(
    ConversionOptimization optimization,
    Map<String, dynamic> userContext,
  ) async {
    final params = optimization.parameters;

    // Reinforce value based on user actions
    final tradesCompleted = userContext['trades_completed'] ?? 0;

    if (tradesCompleted >= 3) {
      await AnalyticsService.trackEvent(
        name: 'value_reinforcement_triggered',
        type: EventType.user_action,
        properties: {
          'trades_completed': tradesCompleted,
          'value_message': params['message'],
        },
      );
    }
  }

  // Friction reduction
  static Future<void> _handleFrictionReduction(
    ConversionOptimization optimization,
    Map<String, dynamic> userContext,
  ) async {
    final params = optimization.parameters;

    // Reduce friction in conversion process
    await AnalyticsService.trackEvent(
      name: 'friction_reduction_applied',
      type: EventType.user_action,
      properties: params,
    );
  }

  // Evaluate and auto-optimize based on performance data
  static Future<void> _evaluateAndOptimize() async {
    final funnelData = await ABTestAnalyzerService.analyzeConversionFunnel();
    final recommendations =
        await ABTestAnalyzerService.getOptimizationRecommendations();

    // Find biggest dropoff points
    final criticalDropoffs = funnelData
        .where((step) => step.dropoffRate > 50.0)
        .toList();

    for (final dropoff in criticalDropoffs) {
      await _createDynamicOptimization(dropoff);
    }

    // Implement priority recommendations
    final priorityActions =
        recommendations['priority_actions'] as List<String>? ?? [];
    for (final action in priorityActions) {
      await _implementRecommendation(action);
    }
  }

  static Future<void> _createDynamicOptimization(
    ConversionFunnelStep dropoffStep,
  ) async {
    // Create optimization based on dropoff analysis
    final optimizationId =
        'dynamic_${dropoffStep.stepName.toLowerCase().replaceAll(' ', '_')}';

    ConversionOptimization optimization;

    if (dropoffStep.stepName.contains('Paywall')) {
      optimization = ConversionOptimization(
        optimizationId: optimizationId,
        strategy: OptimizationStrategy.urgency_creation,
        targetStep: 'paywall_view',
        parameters: {
          'urgency_level': 'high',
          'discount_offered': true,
          'countdown_enabled': true,
        },
        expectedLift: 25.0,
      );
    } else if (dropoffStep.stepName.contains('Onboarding')) {
      optimization = ConversionOptimization(
        optimizationId: optimizationId,
        strategy: OptimizationStrategy.progressive_disclosure,
        targetStep: 'onboarding_step',
        parameters: {
          'simplify_flow': true,
          'reduce_steps': true,
          'add_skip_options': true,
        },
        expectedLift: 15.0,
      );
    } else {
      optimization = ConversionOptimization(
        optimizationId: optimizationId,
        strategy: OptimizationStrategy.friction_reduction,
        targetStep: dropoffStep.stepName.toLowerCase(),
        parameters: {
          'reduce_form_fields': true,
          'add_help_text': true,
          'improve_loading': true,
        },
        expectedLift: 10.0,
      );
    }

    // Add to active optimizations if not already present
    if (!_activeOptimizations.any(
      (opt) => opt.optimizationId == optimizationId,
    )) {
      _activeOptimizations.add(optimization);

      await AnalyticsService.trackEvent(
        name: 'dynamic_optimization_created',
        type: EventType.user_action,
        properties: optimization.toJson(),
      );
    }
  }

  static Future<void> _implementRecommendation(String recommendation) async {
    await AnalyticsService.trackEvent(
      name: 'recommendation_implemented',
      type: EventType.user_action,
      properties: {
        'recommendation': recommendation,
        'implementation_time': DateTime.now().toIso8601String(),
      },
    );
  }

  // User behavior pattern analysis
  static Future<void> trackUserBehaviorPattern(
    String pattern,
    Map<String, dynamic> context,
  ) async {
    final prefs = await SharedPreferences.getInstance();
    final behaviorData = prefs.getStringList(_userBehaviorKey) ?? [];

    final behaviorEntry = {
      'pattern': pattern,
      'context': context,
      'timestamp': DateTime.now().millisecondsSinceEpoch,
    };

    behaviorData.add(behaviorEntry.toString());

    // Keep only recent behavior data
    if (behaviorData.length > 500) {
      behaviorData.removeRange(0, behaviorData.length - 500);
    }

    await prefs.setStringList(_userBehaviorKey, behaviorData);

    // Trigger real-time optimization
    await _analyzePatternAndOptimize(pattern, context);
  }

  static Future<void> _analyzePatternAndOptimize(
    String pattern,
    Map<String, dynamic> context,
  ) async {
    switch (pattern) {
      case 'hesitation_at_paywall':
        await _optimizeForPaywallHesitation(context);
        break;
      case 'rapid_onboarding_completion':
        await _optimizeForEngagedUser(context);
        break;
      case 'multiple_trade_sessions':
        await _optimizeForPowerUser(context);
        break;
      case 'price_sensitivity_signals':
        await _optimizeForPriceSensitiveUser(context);
        break;
    }
  }

  static Future<void> _optimizeForPaywallHesitation(
    Map<String, dynamic> context,
  ) async {
    // Show exit intent discount for hesitant users
    await optimizeUserJourney('paywall_view', {
      ...context,
      'hesitation_detected': true,
      'optimization_priority': 'high',
    });
  }

  static Future<void> _optimizeForEngagedUser(
    Map<String, dynamic> context,
  ) async {
    // Fast-track engaged users to premium features
    await optimizeUserJourney('onboarding_completed', {
      ...context,
      'engagement_level': 'high',
      'show_premium_preview': true,
    });
  }

  static Future<void> _optimizeForPowerUser(
    Map<String, dynamic> context,
  ) async {
    // Offer advanced features to power users
    await optimizeUserJourney('trade_completed', {
      ...context,
      'user_type': 'power_user',
      'show_advanced_features': true,
    });
  }

  static Future<void> _optimizeForPriceSensitiveUser(
    Map<String, dynamic> context,
  ) async {
    // Show value-focused messaging for price-sensitive users
    await optimizeUserJourney('paywall_view', {
      ...context,
      'price_sensitivity': 'high',
      'emphasize_value': true,
    });
  }

  // Get optimization performance report
  static Future<Map<String, dynamic>> getOptimizationReport() async {
    final funnelData = await ABTestAnalyzerService.analyzeConversionFunnel();
    final segments = await ABTestAnalyzerService.analyzeUserSegments();

    return {
      'active_optimizations': _activeOptimizations.length,
      'optimization_strategies': _activeOptimizations
          .map((opt) => opt.strategy.name)
          .toSet()
          .toList(),
      'expected_total_lift': _activeOptimizations.fold<double>(
        0.0,
        (sum, opt) => sum + opt.expectedLift,
      ),
      'funnel_health_score': _calculateFunnelHealthScore(funnelData),
      'top_performing_segments': segments
          .where((s) => s.conversionRate > 15.0)
          .map((s) => s.name)
          .toList(),
      'recommendations_count':
          (await ABTestAnalyzerService.getOptimizationRecommendations()).values
              .expand((recommendations) => recommendations as Iterable)
              .length,
    };
  }

  static double _calculateFunnelHealthScore(
    List<ConversionFunnelStep> funnelData,
  ) {
    if (funnelData.isEmpty) return 0.0;

    final avgConversionRate =
        funnelData
            .map((step) => step.conversionRate)
            .fold<double>(0.0, (sum, rate) => sum + rate) /
        funnelData.length;

    final avgDropoffRate =
        funnelData
            .map((step) => step.dropoffRate)
            .fold<double>(0.0, (sum, rate) => sum + rate) /
        funnelData.length;

    // Health score based on conversion rate and inverse of dropoff rate
    return (avgConversionRate + (100 - avgDropoffRate)) / 2;
  }

  // Cleanup
  static void dispose() {
    _optimizationTimer?.cancel();
    _activeOptimizations.clear();
  }
}
