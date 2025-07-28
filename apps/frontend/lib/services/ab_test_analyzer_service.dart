import 'dart:math';
import 'package:shared_preferences/shared_preferences.dart';
import 'ab_testing_service.dart';
import 'analytics_service.dart';

class ABTestResult {
  final String testName;
  final String variant;
  final int participants;
  final int conversions;
  final double conversionRate;
  final double confidenceLevel;
  final bool isStatisticallySignificant;
  final Map<String, dynamic> metadata;

  ABTestResult({
    required this.testName,
    required this.variant,
    required this.participants,
    required this.conversions,
    required this.conversionRate,
    required this.confidenceLevel,
    required this.isStatisticallySignificant,
    this.metadata = const {},
  });

  Map<String, dynamic> toJson() {
    return {
      'test_name': testName,
      'variant': variant,
      'participants': participants,
      'conversions': conversions,
      'conversion_rate': conversionRate,
      'confidence_level': confidenceLevel,
      'is_statistically_significant': isStatisticallySignificant,
      'metadata': metadata,
    };
  }
}

class ConversionFunnelStep {
  final String stepName;
  final int visitors;
  final int conversions;
  final double conversionRate;
  final double dropoffRate;

  ConversionFunnelStep({
    required this.stepName,
    required this.visitors,
    required this.conversions,
    required this.conversionRate,
    required this.dropoffRate,
  });

  Map<String, dynamic> toJson() {
    return {
      'step_name': stepName,
      'visitors': visitors,
      'conversions': conversions,
      'conversion_rate': conversionRate,
      'dropoff_rate': dropoffRate,
    };
  }
}

class UserSegment {
  final String segmentId;
  final String name;
  final Map<String, dynamic> criteria;
  final int userCount;
  final double conversionRate;
  final double averageRevenue;

  UserSegment({
    required this.segmentId,
    required this.name,
    required this.criteria,
    required this.userCount,
    required this.conversionRate,
    required this.averageRevenue,
  });

  Map<String, dynamic> toJson() {
    return {
      'segment_id': segmentId,
      'name': name,
      'criteria': criteria,
      'user_count': userCount,
      'conversion_rate': conversionRate,
      'average_revenue': averageRevenue,
    };
  }
}

class ABTestAnalyzerService {
  static const String _testResultsPrefix = 'ab_results_';
  static const String _funnelDataKey = 'conversion_funnel_data';
  static const String _segmentDataKey = 'user_segment_data';

  // Analyze A/B test performance
  static Future<List<ABTestResult>> analyzeABTestResults() async {
    final results = <ABTestResult>[];
    
    // Analyze paywall presentation test
    final paywallResults = await _analyzePaywallTest();
    results.addAll(paywallResults);
    
    // Analyze onboarding flow test
    final onboardingResults = await _analyzeOnboardingTest();
    results.addAll(onboardingResults);
    
    // Analyze rating prompt test
    final ratingResults = await _analyzeRatingTest();
    results.addAll(ratingResults);
    
    return results;
  }

  static Future<List<ABTestResult>> _analyzePaywallTest() async {
    final testData = await ABTestingService.getTestResults('paywall_presentation');
    final results = <ABTestResult>[];
    
    final variantData = testData['results'] as Map<String, dynamic>? ?? {};
    
    for (final entry in variantData.entries) {
      final variant = entry.key;
      final data = entry.value as Map<String, int>;
      
      final participants = data.values.fold(0, (sum, count) => sum + count);
      final conversions = data['purchase'] ?? 0;
      final conversionRate = participants > 0 ? (conversions / participants) * 100 : 0.0;
      
      // Calculate statistical significance (simplified Z-test)
      final confidenceLevel = _calculateConfidenceLevel(participants, conversions);
      final isSignificant = confidenceLevel >= 95.0;
      
      results.add(ABTestResult(
        testName: 'paywall_presentation',
        variant: variant,
        participants: participants,
        conversions: conversions,
        conversionRate: conversionRate,
        confidenceLevel: confidenceLevel,
        isStatisticallySignificant: isSignificant,
        metadata: {
          'dismissals': data['dismissal'] ?? 0,
          'views': data['view'] ?? 0,
          'test_duration_days': _calculateTestDuration(),
        },
      ));
    }
    
    return results;
  }

  static Future<List<ABTestResult>> _analyzeOnboardingTest() async {
    final testData = await ABTestingService.getTestResults('onboarding_flow');
    final results = <ABTestResult>[];
    
    final variantData = testData['results'] as Map<String, dynamic>? ?? {};
    
    for (final entry in variantData.entries) {
      final variant = entry.key;
      final data = entry.value as Map<String, int>;
      
      final participants = data.values.fold(0, (sum, count) => sum + count);
      final conversions = data['completion'] ?? 0;
      final conversionRate = participants > 0 ? (conversions / participants) * 100 : 0.0;
      
      final confidenceLevel = _calculateConfidenceLevel(participants, conversions);
      final isSignificant = confidenceLevel >= 95.0;
      
      results.add(ABTestResult(
        testName: 'onboarding_flow',
        variant: variant,
        participants: participants,
        conversions: conversions,
        conversionRate: conversionRate,
        confidenceLevel: confidenceLevel,
        isStatisticallySignificant: isSignificant,
        metadata: {
          'dropoffs': data['dropoff'] ?? 0,
          'avg_completion_time': _calculateAvgCompletionTime(variant),
        },
      ));
    }
    
    return results;
  }

  static Future<List<ABTestResult>> _analyzeRatingTest() async {
    final testData = await ABTestingService.getTestResults('rating_prompt_timing');
    final results = <ABTestResult>[];
    
    final variantData = testData['results'] as Map<String, dynamic>? ?? {};
    
    for (final entry in variantData.entries) {
      final variant = entry.key;
      final data = entry.value as Map<String, int>;
      
      final participants = data.values.fold(0, (sum, count) => sum + count);
      final conversions = data['rating_submitted'] ?? 0;
      final conversionRate = participants > 0 ? (conversions / participants) * 100 : 0.0;
      
      final confidenceLevel = _calculateConfidenceLevel(participants, conversions);
      final isSignificant = confidenceLevel >= 95.0;
      
      results.add(ABTestResult(
        testName: 'rating_prompt_timing',
        variant: variant,
        participants: participants,
        conversions: conversions,
        conversionRate: conversionRate,
        confidenceLevel: confidenceLevel,
        isStatisticallySignificant: isSignificant,
        metadata: {
          'avg_rating': _calculateAvgRating(variant),
          'store_visits': data['store_visit'] ?? 0,
        },
      ));
    }
    
    return results;
  }

  // Analyze conversion funnel
  static Future<List<ConversionFunnelStep>> analyzeConversionFunnel() async {
    final events = await AnalyticsService.getEvents();
    
    // Define funnel steps
    final steps = [
      'app_opened',
      'onboarding_completed',
      'first_trade_attempted',
      'paywall_shown',
      'subscription_purchased',
    ];
    
    final funnelData = <ConversionFunnelStep>[];
    int previousStepVisitors = 0;
    
    for (int i = 0; i < steps.length; i++) {
      final stepName = steps[i];
      final stepEvents = events.where((e) => e.name == stepName).toList();
      final visitors = stepEvents.length;
      
      final conversions = i < steps.length - 1 
          ? events.where((e) => e.name == steps[i + 1]).length 
          : visitors;
      
      final conversionRate = visitors > 0 ? (conversions / visitors) * 100 : 0.0;
      final dropoffRate = i > 0 && previousStepVisitors > 0 
          ? ((previousStepVisitors - visitors) / previousStepVisitors) * 100 
          : 0.0;
      
      funnelData.add(ConversionFunnelStep(
        stepName: _formatStepName(stepName),
        visitors: visitors,
        conversions: conversions,
        conversionRate: conversionRate,
        dropoffRate: dropoffRate,
      ));
      
      previousStepVisitors = visitors;
    }
    
    return funnelData;
  }

  // User segmentation analysis
  static Future<List<UserSegment>> analyzeUserSegments() async {
    final events = await AnalyticsService.getEvents();
    final segments = <UserSegment>[];
    
    // Segment 1: High-value prospects
    final highValueUsers = events.where((e) => 
        e.name == 'onboarding_completed' && 
        (e.properties['experience_level'] == 'Advanced' ||
         (e.properties['practice_amount'] ?? 0) >= 500)).toList();
    
    final highValueConversions = events.where((e) => 
        e.name == 'subscription_purchased' &&
        highValueUsers.any((u) => u.userId == e.userId)).length;
    
    segments.add(UserSegment(
      segmentId: 'high_value_prospects',
      name: 'High-Value Prospects',
      criteria: {
        'experience_level': 'Advanced',
        'practice_amount': '>=500',
        'goals': 'contains_professional',
      },
      userCount: highValueUsers.length,
      conversionRate: highValueUsers.isNotEmpty 
          ? (highValueConversions / highValueUsers.length) * 100 
          : 0.0,
      averageRevenue: 9.99, // Monthly subscription
    ));
    
    // Segment 2: Casual learners
    final casualUsers = events.where((e) => 
        e.name == 'onboarding_completed' && 
        e.properties['experience_level'] == 'Beginner' &&
        (e.properties['practice_amount'] ?? 0) < 500).toList();
    
    final casualConversions = events.where((e) => 
        e.name == 'subscription_purchased' &&
        casualUsers.any((u) => u.userId == e.userId)).length;
    
    segments.add(UserSegment(
      segmentId: 'casual_learners',
      name: 'Casual Learners',
      criteria: {
        'experience_level': 'Beginner',
        'practice_amount': '<500',
        'goals': 'learning_focused',
      },
      userCount: casualUsers.length,
      conversionRate: casualUsers.isNotEmpty 
          ? (casualConversions / casualUsers.length) * 100 
          : 0.0,
      averageRevenue: 2.99, // Discount price
    ));
    
    // Segment 3: Power users
    final powerUsers = events.where((e) => 
        e.name == 'trade_completed' &&
        e.properties['total_trades'] >= 20).toList();
    
    final powerUserConversions = events.where((e) => 
        e.name == 'subscription_purchased' &&
        powerUsers.any((u) => u.userId == e.userId)).length;
    
    segments.add(UserSegment(
      segmentId: 'power_users',
      name: 'Power Users',
      criteria: {
        'total_trades': '>=20',
        'current_streak': '>=5',
        'win_rate': '>60',
      },
      userCount: powerUsers.length,
      conversionRate: powerUsers.isNotEmpty 
          ? (powerUserConversions / powerUsers.length) * 100 
          : 0.0,
      averageRevenue: 9.99,
    ));
    
    return segments;
  }

  // Get optimization recommendations
  static Future<Map<String, dynamic>> getOptimizationRecommendations() async {
    final abResults = await analyzeABTestResults();
    final funnelData = await analyzeConversionFunnel();
    final segments = await analyzeUserSegments();
    
    final recommendations = <String, dynamic>{
      'ab_test_recommendations': _generateABTestRecommendations(abResults),
      'funnel_optimizations': _generateFunnelOptimizations(funnelData),
      'segment_strategies': _generateSegmentStrategies(segments),
      'priority_actions': _generatePriorityActions(abResults, funnelData, segments),
    };
    
    return recommendations;
  }

  // Helper methods
  static double _calculateConfidenceLevel(int participants, int conversions) {
    if (participants == 0) return 0.0;
    
    final p = conversions / participants;
    final standardError = sqrt((p * (1 - p)) / participants);
    final zScore = (p - 0.5).abs() / standardError;
    
    // Simplified confidence calculation
    if (zScore >= 1.96) return 95.0;
    if (zScore >= 1.645) return 90.0;
    if (zScore >= 1.282) return 80.0;
    return 0.0;
  }

  static int _calculateTestDuration() {
    // Calculate days since test started (simplified)
    return 7; // Assume 1 week for now
  }

  static double _calculateAvgCompletionTime(String variant) {
    // Would calculate from actual timing data
    return variant == 'control' ? 180.0 : 120.0; // seconds
  }

  static double _calculateAvgRating(String variant) {
    // Would calculate from actual rating data
    return variant == 'control' ? 4.2 : 4.5;
  }

  static String _formatStepName(String stepName) {
    return stepName.split('_').map((word) => 
        word[0].toUpperCase() + word.substring(1)).join(' ');
  }

  static List<String> _generateABTestRecommendations(List<ABTestResult> results) {
    final recommendations = <String>[];
    
    // Find best performing variants
    final paywallResults = results.where((r) => r.testName == 'paywall_presentation').toList();
    if (paywallResults.isNotEmpty) {
      final bestPaywall = paywallResults.reduce((a, b) => 
          a.conversionRate > b.conversionRate ? a : b);
      
      if (bestPaywall.isStatisticallySignificant) {
        recommendations.add('Switch all users to ${bestPaywall.variant} paywall variant '
            '(${bestPaywall.conversionRate.toStringAsFixed(1)}% conversion rate)');
      } else {
        recommendations.add('Continue paywall A/B test - need more data for statistical significance');
      }
    }
    
    // Check for underperforming variants
    final lowPerformers = results.where((r) => r.conversionRate < 5.0).toList();
    for (final result in lowPerformers) {
      recommendations.add('Consider discontinuing ${result.variant} variant '
          'for ${result.testName} (low ${result.conversionRate.toStringAsFixed(1)}% conversion)');
    }
    
    return recommendations;
  }

  static List<String> _generateFunnelOptimizations(List<ConversionFunnelStep> funnel) {
    final optimizations = <String>[];
    
    // Find biggest dropoff points
    final biggestDropoffs = funnel.where((step) => step.dropoffRate > 50.0).toList();
    for (final step in biggestDropoffs) {
      optimizations.add('Optimize ${step.stepName} - ${step.dropoffRate.toStringAsFixed(1)}% dropoff rate');
    }
    
    // Check overall funnel health
    final finalStep = funnel.isNotEmpty ? funnel.last : null;
    if (finalStep != null && finalStep.conversionRate < 10.0) {
      optimizations.add('Overall conversion rate is low (${finalStep.conversionRate.toStringAsFixed(1)}%) - '
          'consider revising entire funnel');
    }
    
    return optimizations;
  }

  static List<String> _generateSegmentStrategies(List<UserSegment> segments) {
    final strategies = <String>[];
    
    for (final segment in segments) {
      if (segment.conversionRate > 20.0) {
        strategies.add('${segment.name}: High-converting segment - '
            'increase targeting and expand reach');
      } else if (segment.conversionRate < 5.0) {
        strategies.add('${segment.name}: Low-converting segment - '
            'test different messaging or offers');
      } else {
        strategies.add('${segment.name}: Moderate performance - '
            'A/B test improvements to messaging and timing');
      }
    }
    
    return strategies;
  }

  static List<String> _generatePriorityActions(
    List<ABTestResult> abResults, 
    List<ConversionFunnelStep> funnel, 
    List<UserSegment> segments
  ) {
    final actions = <String>[];
    
    // Priority 1: Address critical funnel issues
    final criticalDropoffs = funnel.where((step) => step.dropoffRate > 70.0).toList();
    if (criticalDropoffs.isNotEmpty) {
      actions.add('URGENT: Fix critical dropoff at ${criticalDropoffs.first.stepName}');
    }
    
    // Priority 2: Implement winning A/B tests
    final significantWinners = abResults.where((r) => 
        r.isStatisticallySignificant && r.conversionRate > 15.0).toList();
    if (significantWinners.isNotEmpty) {
      actions.add('HIGH: Implement winning variant ${significantWinners.first.variant}');
    }
    
    // Priority 3: Focus on high-value segments
    final highValueSegments = segments.where((s) => 
        s.averageRevenue > 5.0 && s.conversionRate > 10.0).toList();
    if (highValueSegments.isNotEmpty) {
      actions.add('MEDIUM: Optimize targeting for ${highValueSegments.first.name}');
    }
    
    return actions;
  }
}