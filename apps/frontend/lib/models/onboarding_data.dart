class OnboardingData {
  final String experienceLevel;
  final double practiceAmount;
  final List<String> goals;
  final bool hasNotificationPermission;
  final DateTime completedAt;

  const OnboardingData({
    required this.experienceLevel,
    required this.practiceAmount,
    required this.goals,
    this.hasNotificationPermission = false,
    required this.completedAt,
  });

  OnboardingData copyWith({
    String? experienceLevel,
    double? practiceAmount,
    List<String>? goals,
    bool? hasNotificationPermission,
    DateTime? completedAt,
  }) {
    return OnboardingData(
      experienceLevel: experienceLevel ?? this.experienceLevel,
      practiceAmount: practiceAmount ?? this.practiceAmount,
      goals: goals ?? this.goals,
      hasNotificationPermission:
          hasNotificationPermission ?? this.hasNotificationPermission,
      completedAt: completedAt ?? this.completedAt,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'experienceLevel': experienceLevel,
      'practiceAmount': practiceAmount,
      'goals': goals,
      'hasNotificationPermission': hasNotificationPermission,
      'completedAt': completedAt.toIso8601String(),
    };
  }

  factory OnboardingData.fromJson(Map<String, dynamic> json) {
    return OnboardingData(
      experienceLevel: json['experienceLevel'] ?? '',
      practiceAmount: (json['practiceAmount'] ?? 0.0).toDouble(),
      goals: List<String>.from(json['goals'] ?? []),
      hasNotificationPermission: json['hasNotificationPermission'] ?? false,
      completedAt: DateTime.parse(json['completedAt']),
    );
  }

  bool get isHighValueUser {
    // Users with advanced experience or high practice amounts are more likely to convert
    return experienceLevel == 'Advanced' || practiceAmount >= 500;
  }

  bool get hasAmbiguousGoals {
    // Users with career/income goals are higher intent
    return goals.any(
      (goal) =>
          goal.contains('career') ||
          goal.contains('income') ||
          goal.contains('professional'),
    );
  }
}
