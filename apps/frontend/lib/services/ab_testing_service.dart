import 'dart:math';
import 'package:shared_preferences/shared_preferences.dart';

enum ABTestVariant {
  control,
  variant_a,
  variant_b,
}

class ABTestConfig {
  final String testName;
  final Map<ABTestVariant, double> weights;
  final bool isActive;
  final DateTime? endDate;

  const ABTestConfig({
    required this.testName,
    required this.weights,
    this.isActive = true,
    this.endDate,
  });
}

class ABTestingService {
  static const String _userVariantPrefix = 'ab_test_';
  static const String _testResultPrefix = 'ab_result_';
  
  static final Map<String, ABTestConfig> _activeTests = {
    'paywall_presentation': ABTestConfig(
      testName: 'paywall_presentation',
      weights: {
        ABTestVariant.control: 0.4,
        ABTestVariant.variant_a: 0.3,
        ABTestVariant.variant_b: 0.3,
      },
    ),
    'onboarding_flow': ABTestConfig(
      testName: 'onboarding_flow',
      weights: {
        ABTestVariant.control: 0.5,
        ABTestVariant.variant_a: 0.5,
      },
    ),
    'rating_prompt_timing': ABTestConfig(
      testName: 'rating_prompt_timing',
      weights: {
        ABTestVariant.control: 0.6,
        ABTestVariant.variant_a: 0.4,
      },
    ),
  };

  static Future<ABTestVariant> getVariant(String testName) async {
    final prefs = await SharedPreferences.getInstance();
    final savedVariant = prefs.getString('$_userVariantPrefix$testName');
    
    if (savedVariant != null) {
      return ABTestVariant.values.firstWhere(
        (v) => v.name == savedVariant,
        orElse: () => ABTestVariant.control,
      );
    }

    // Assign new variant based on weights
    final config = _activeTests[testName];
    if (config == null || !config.isActive) {
      return ABTestVariant.control;
    }

    final variant = _assignVariant(config.weights);
    await prefs.setString('$_userVariantPrefix$testName', variant.name);
    
    return variant;
  }

  static ABTestVariant _assignVariant(Map<ABTestVariant, double> weights) {
    final random = Random();
    final randomValue = random.nextDouble();
    
    double cumulativeWeight = 0.0;
    for (final entry in weights.entries) {
      cumulativeWeight += entry.value;
      if (randomValue <= cumulativeWeight) {
        return entry.key;
      }
    }
    
    return ABTestVariant.control;
  }

  static Future<void> trackConversion(String testName, String eventName, Map<String, dynamic>? properties) async {
    final variant = await getVariant(testName);
    final prefs = await SharedPreferences.getInstance();
    
    final conversionData = {
      'test_name': testName,
      'variant': variant.name,
      'event': eventName,
      'timestamp': DateTime.now().millisecondsSinceEpoch,
      'properties': properties ?? {},
    };
    
    // Store conversion data for analytics
    final existingData = prefs.getStringList('$_testResultPrefix$testName') ?? [];
    existingData.add(_encodeConversionData(conversionData));
    await prefs.setStringList('$_testResultPrefix$testName', existingData);
  }

  static String _encodeConversionData(Map<String, dynamic> data) {
    // Simple encoding for local storage
    return '${data['variant']}|${data['event']}|${data['timestamp']}';
  }

  static Future<Map<String, dynamic>> getTestResults(String testName) async {
    final prefs = await SharedPreferences.getInstance();
    final data = prefs.getStringList('$_testResultPrefix$testName') ?? [];
    
    final results = <String, Map<String, int>>{};
    
    for (final entry in data) {
      final parts = entry.split('|');
      if (parts.length >= 3) {
        final variant = parts[0];
        final event = parts[1];
        
        results[variant] ??= {};
        results[variant]![event] = (results[variant]![event] ?? 0) + 1;
      }
    }
    
    return {
      'test_name': testName,
      'results': results,
      'total_participants': data.length,
    };
  }

  static Future<bool> isInVariant(String testName, ABTestVariant variant) async {
    final userVariant = await getVariant(testName);
    return userVariant == variant;
  }

  // Paywall-specific A/B test helpers
  static Future<PaywallVariant> getPaywallVariant() async {
    final variant = await getVariant('paywall_presentation');
    switch (variant) {
      case ABTestVariant.control:
        return PaywallVariant.standard;
      case ABTestVariant.variant_a:
        return PaywallVariant.discount_first;
      case ABTestVariant.variant_b:
        return PaywallVariant.social_proof;
    }
  }

  // Onboarding A/B test helpers
  static Future<OnboardingVariant> getOnboardingVariant() async {
    final variant = await getVariant('onboarding_flow');
    switch (variant) {
      case ABTestVariant.control:
        return OnboardingVariant.standard;
      case ABTestVariant.variant_a:
        return OnboardingVariant.simplified;
      default:
        return OnboardingVariant.standard;
    }
  }

  // Rating prompt A/B test helpers
  static Future<RatingPromptVariant> getRatingPromptVariant() async {
    final variant = await getVariant('rating_prompt_timing');
    switch (variant) {
      case ABTestVariant.control:
        return RatingPromptVariant.standard;
      case ABTestVariant.variant_a:
        return RatingPromptVariant.early_prompt;
      default:
        return RatingPromptVariant.standard;
    }
  }
}

enum PaywallVariant {
  standard,
  discount_first,
  social_proof,
}

enum OnboardingVariant {
  standard,
  simplified,
}

enum RatingPromptVariant {
  standard,
  early_prompt,
}