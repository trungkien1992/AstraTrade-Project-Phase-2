import 'package:flutter/foundation.dart';

/// Achievement model representing individual achievements in the research-driven system
/// 
/// Categories align with research findings:
/// - Educational: 60% of achievements - focus on learning and skill development
/// - Risk Management: 20% of achievements - safety and responsible trading
/// - Performance: 15% of achievements - skill-based milestones
/// - Social: 5% of achievements - community engagement
class Achievement {
  final String id;
  final String name;
  final String description;
  final String category; // educational, risk_management, performance, social
  final String rarity; // common, uncommon, rare, epic, legendary
  final int xpReward;
  final String cosmicTheme;
  final List<String> learningObjectives;
  final List<String> prerequisiteAchievements;
  
  // Progress tracking
  final int progressCurrent;
  final int progressTarget;
  final bool isCompleted;
  final DateTime? unlockedAt;
  final DateTime? expiresAt;
  
  // League integration
  final int leagueMultiplier;
  final String skillLevel; // novice, apprentice, practitioner, expert, master
  
  // Social features
  final bool isShareable;
  final int shareCount;
  final List<String> tags;
  
  // Display configuration
  final String iconUrl;
  final Map<String, dynamic> displayConfig;

  const Achievement({
    required this.id,
    required this.name,
    required this.description,
    required this.category,
    this.rarity = 'common',
    required this.xpReward,
    this.cosmicTheme = '',
    this.learningObjectives = const [],
    this.prerequisiteAchievements = const [],
    this.progressCurrent = 0,
    this.progressTarget = 1,
    this.isCompleted = false,
    this.unlockedAt,
    this.expiresAt,
    this.leagueMultiplier = 1,
    this.skillLevel = 'novice',
    this.isShareable = true,
    this.shareCount = 0,
    this.tags = const [],
    this.iconUrl = '',
    this.displayConfig = const {},
  });

  /// Calculate progress percentage (0.0 to 1.0)
  double get progressPercentage {
    if (progressTarget <= 0) return isCompleted ? 1.0 : 0.0;
    return (progressCurrent / progressTarget).clamp(0.0, 1.0);
  }
  
  /// Get category display name
  String get categoryDisplayName {
    switch (category) {
      case 'educational':
        return 'Education';
      case 'risk_management':
        return 'Risk Management';
      case 'performance':
        return 'Performance';
      case 'social':
        return 'Social';
      default:
        return 'Achievement';
    }
  }
  
  /// Get rarity display name
  String get rarityDisplayName {
    return rarity.split('_').map((word) => 
        word[0].toUpperCase() + word.substring(1)).join(' ');
  }
  
  /// Check if achievement is educational (research priority)
  bool get isEducational => category == 'educational';
  
  /// Check if achievement promotes safety
  bool get promotesSafety => category == 'risk_management';
  
  /// Check if achievement is recommended based on research criteria
  bool get isRecommended {
    // Educational and risk management achievements are prioritized
    if (isEducational || promotesSafety) return true;
    
    // Incomplete achievements with prerequisites met
    if (!isCompleted && prerequisiteAchievements.isEmpty) return true;
    
    return false;
  }
  
  /// Get XP reward with league scaling
  int get scaledXPReward => (xpReward * leagueMultiplier).round();

  /// Create achievement from JSON
  factory Achievement.fromJson(Map<String, dynamic> json) {
    return Achievement(
      id: json['id'] as String,
      name: json['name'] as String,
      description: json['description'] as String,
      category: json['category'] as String,
      rarity: json['rarity'] as String? ?? 'common',
      xpReward: json['xp_reward'] as int,
      cosmicTheme: json['cosmic_theme'] as String? ?? '',
      learningObjectives: List<String>.from(json['learning_objectives'] ?? []),
      prerequisiteAchievements: List<String>.from(json['prerequisite_achievements'] ?? []),
      progressCurrent: json['progress_current'] as int? ?? 0,
      progressTarget: json['progress_target'] as int? ?? 1,
      isCompleted: json['is_completed'] as bool? ?? false,
      unlockedAt: json['unlocked_at'] != null 
          ? DateTime.parse(json['unlocked_at'] as String)
          : null,
      expiresAt: json['expires_at'] != null
          ? DateTime.parse(json['expires_at'] as String)
          : null,
      leagueMultiplier: json['league_multiplier'] as int? ?? 1,
      skillLevel: json['skill_level'] as String? ?? 'novice',
      isShareable: json['is_shareable'] as bool? ?? true,
      shareCount: json['share_count'] as int? ?? 0,
      tags: List<String>.from(json['tags'] ?? []),
      iconUrl: json['icon_url'] as String? ?? '',
      displayConfig: Map<String, dynamic>.from(json['display_config'] ?? {}),
    );
  }

  /// Convert achievement to JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'category': category,
      'rarity': rarity,
      'xp_reward': xpReward,
      'cosmic_theme': cosmicTheme,
      'learning_objectives': learningObjectives,
      'prerequisite_achievements': prerequisiteAchievements,
      'progress_current': progressCurrent,
      'progress_target': progressTarget,
      'is_completed': isCompleted,
      'unlocked_at': unlockedAt?.toIso8601String(),
      'expires_at': expiresAt?.toIso8601String(),
      'league_multiplier': leagueMultiplier,
      'skill_level': skillLevel,
      'is_shareable': isShareable,
      'share_count': shareCount,
      'tags': tags,
      'icon_url': iconUrl,
      'display_config': displayConfig,
    };
  }

  /// Create a copy with updated fields
  Achievement copyWith({
    String? id,
    String? name,
    String? description,
    String? category,
    String? rarity,
    int? xpReward,
    String? cosmicTheme,
    List<String>? learningObjectives,
    List<String>? prerequisiteAchievements,
    int? progressCurrent,
    int? progressTarget,
    bool? isCompleted,
    DateTime? unlockedAt,
    DateTime? expiresAt,
    int? leagueMultiplier,
    String? skillLevel,
    bool? isShareable,
    int? shareCount,
    List<String>? tags,
    String? iconUrl,
    Map<String, dynamic>? displayConfig,
  }) {
    return Achievement(
      id: id ?? this.id,
      name: name ?? this.name,
      description: description ?? this.description,
      category: category ?? this.category,
      rarity: rarity ?? this.rarity,
      xpReward: xpReward ?? this.xpReward,
      cosmicTheme: cosmicTheme ?? this.cosmicTheme,
      learningObjectives: learningObjectives ?? this.learningObjectives,
      prerequisiteAchievements: prerequisiteAchievements ?? this.prerequisiteAchievements,
      progressCurrent: progressCurrent ?? this.progressCurrent,
      progressTarget: progressTarget ?? this.progressTarget,
      isCompleted: isCompleted ?? this.isCompleted,
      unlockedAt: unlockedAt ?? this.unlockedAt,
      expiresAt: expiresAt ?? this.expiresAt,
      leagueMultiplier: leagueMultiplier ?? this.leagueMultiplier,
      skillLevel: skillLevel ?? this.skillLevel,
      isShareable: isShareable ?? this.isShareable,
      shareCount: shareCount ?? this.shareCount,
      tags: tags ?? this.tags,
      iconUrl: iconUrl ?? this.iconUrl,
      displayConfig: displayConfig ?? this.displayConfig,
    );
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is Achievement && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;

  @override
  String toString() {
    return 'Achievement(id: $id, name: $name, category: $category, completed: $isCompleted)';
  }
}

/// Achievement category statistics for research-driven distribution
class AchievementCategoryStats {
  final String category;
  final int totalAchievements;
  final int completedAchievements;
  final double targetPercentage; // Research-driven target
  final double actualPercentage; // Current distribution
  final List<Achievement> recommendedAchievements;

  const AchievementCategoryStats({
    required this.category,
    required this.totalAchievements,
    required this.completedAchievements,
    required this.targetPercentage,
    required this.actualPercentage,
    required this.recommendedAchievements,
  });

  /// Completion percentage for this category
  double get completionPercentage {
    if (totalAchievements == 0) return 0.0;
    return completedAchievements / totalAchievements;
  }

  /// Whether category meets research target distribution
  bool get meetsTargetDistribution {
    return (actualPercentage - targetPercentage).abs() <= 0.05; // 5% tolerance
  }

  factory AchievementCategoryStats.fromJson(Map<String, dynamic> json) {
    return AchievementCategoryStats(
      category: json['category'] as String,
      totalAchievements: json['total_achievements'] as int,
      completedAchievements: json['completed_achievements'] as int,
      targetPercentage: json['target_percentage'] as double,
      actualPercentage: json['actual_percentage'] as double,
      recommendedAchievements: (json['recommended_achievements'] as List)
          .map((item) => Achievement.fromJson(item as Map<String, dynamic>))
          .toList(),
    );
  }
}

/// League progression model integrating achievements
class LeagueProgression {
  final String userId;
  final String currentLeague; // cadet, rising_star, champion, elite, galactic_master
  final String leagueStatus; // active, promotion_eligible, demotion_warning
  final int leaguePoints;
  final DateTime leagueEntryDate;
  final int daysInCurrentLeague;
  final Map<String, double> promotionProgress; // requirement -> progress %
  
  // Achievement requirements
  final int educationalAchievementsRequired;
  final int riskManagementAchievementsRequired;
  final int totalAchievementsRequired;
  final int educationalAchievementsCompleted;
  final int riskManagementAchievementsCompleted;
  final int totalAchievementsCompleted;

  const LeagueProgression({
    required this.userId,
    required this.currentLeague,
    required this.leagueStatus,
    required this.leaguePoints,
    required this.leagueEntryDate,
    required this.daysInCurrentLeague,
    required this.promotionProgress,
    required this.educationalAchievementsRequired,
    required this.riskManagementAchievementsRequired,
    required this.totalAchievementsRequired,
    required this.educationalAchievementsCompleted,
    required this.riskManagementAchievementsCompleted,
    required this.totalAchievementsCompleted,
  });

  /// Get league display name
  String get leagueDisplayName {
    switch (currentLeague) {
      case 'cadet':
        return 'Cadet League';
      case 'rising_star':
        return 'Rising Star League';
      case 'champion':
        return 'Champion League';
      case 'elite':
        return 'Elite League';
      case 'galactic_master':
        return 'Galactic Master League';
      default:
        return 'Unknown League';
    }
  }

  /// Check if ready for promotion
  bool get isPromotionEligible => leagueStatus == 'promotion_eligible';

  /// Get overall promotion progress (0.0 to 1.0)
  double get overallPromotionProgress {
    if (promotionProgress.isEmpty) return 0.0;
    return promotionProgress.values.reduce((a, b) => a + b) / promotionProgress.length;
  }

  /// Get educational achievement progress
  double get educationalProgress {
    if (educationalAchievementsRequired <= 0) return 1.0;
    return (educationalAchievementsCompleted / educationalAchievementsRequired).clamp(0.0, 1.0);
  }

  /// Get risk management achievement progress
  double get riskManagementProgress {
    if (riskManagementAchievementsRequired <= 0) return 1.0;
    return (riskManagementAchievementsCompleted / riskManagementAchievementsRequired).clamp(0.0, 1.0);
  }

  factory LeagueProgression.fromJson(Map<String, dynamic> json) {
    return LeagueProgression(
      userId: json['user_id'] as String,
      currentLeague: json['current_league'] as String,
      leagueStatus: json['league_status'] as String,
      leaguePoints: json['league_points'] as int,
      leagueEntryDate: DateTime.parse(json['league_entry_date'] as String),
      daysInCurrentLeague: json['days_in_current_league'] as int,
      promotionProgress: Map<String, double>.from(json['promotion_progress'] ?? {}),
      educationalAchievementsRequired: json['educational_achievements_required'] as int,
      riskManagementAchievementsRequired: json['risk_management_achievements_required'] as int,
      totalAchievementsRequired: json['total_achievements_required'] as int,
      educationalAchievementsCompleted: json['educational_achievements_completed'] as int,
      riskManagementAchievementsCompleted: json['risk_management_achievements_completed'] as int,
      totalAchievementsCompleted: json['total_achievements_completed'] as int,
    );
  }
}

/// Achievement notification model for real-time display
class AchievementNotification {
  final String notificationId;
  final Achievement achievement;
  final String displayPosition; // bottom_right, center_modal, etc.
  final String displayStyle; // subtle, standard, celebrate
  final int autoDismissSeconds;
  final bool soundEnabled;
  final bool animationEnabled;
  final DateTime receivedAt;
  final Map<String, dynamic> triggerData;

  const AchievementNotification({
    required this.notificationId,
    required this.achievement,
    this.displayPosition = 'bottom_right',
    this.displayStyle = 'standard',
    this.autoDismissSeconds = 5,
    this.soundEnabled = true,
    this.animationEnabled = true,
    required this.receivedAt,
    this.triggerData = const {},
  });

  /// Check if notification should celebrate (educational/safety achievements)
  bool get shouldCelebrate {
    return achievement.isEducational || 
           achievement.promotesSafety || 
           achievement.rarity == 'legendary';
  }

  /// Get celebration level based on achievement importance
  String get celebrationLevel {
    if (achievement.rarity == 'legendary') return 'celebrate';
    if (achievement.isEducational || achievement.promotesSafety) return 'celebrate';
    return displayStyle;
  }

  factory AchievementNotification.fromJson(Map<String, dynamic> json) {
    return AchievementNotification(
      notificationId: json['notification_id'] as String,
      achievement: Achievement.fromJson(json['achievement_data'] as Map<String, dynamic>),
      displayPosition: json['display_config']['position'] as String? ?? 'bottom_right',
      displayStyle: json['display_config']['style'] as String? ?? 'standard',
      autoDismissSeconds: json['display_config']['auto_dismiss_seconds'] as int? ?? 5,
      soundEnabled: json['display_config']['sound_enabled'] as bool? ?? true,
      animationEnabled: json['display_config']['animation_enabled'] as bool? ?? true,
      receivedAt: DateTime.parse(json['timestamp'] as String),
      triggerData: Map<String, dynamic>.from(json['trigger_data'] ?? {}),
    );
  }
}

/// User achievement statistics for analytics
class UserAchievementStats {
  final int totalAchievements;
  final int completedAchievements;
  final int educationalCompleted;
  final int riskManagementCompleted;
  final int performanceCompleted;
  final int socialCompleted;
  final int totalXPEarned;
  final int leaguePoints;
  final String currentLeague;
  final double educationalPercentage;
  final LeagueProgression? leagueProgression;
  final List<Achievement> recentlyCompleted;
  final List<Achievement> recommended;

  const UserAchievementStats({
    required this.totalAchievements,
    required this.completedAchievements,
    required this.educationalCompleted,
    required this.riskManagementCompleted,
    required this.performanceCompleted,
    required this.socialCompleted,
    required this.totalXPEarned,
    required this.leaguePoints,
    required this.currentLeague,
    required this.educationalPercentage,
    this.leagueProgression,
    required this.recentlyCompleted,
    required this.recommended,
  });

  /// Overall completion percentage
  double get completionPercentage {
    if (totalAchievements == 0) return 0.0;
    return completedAchievements / totalAchievements;
  }

  /// Check if user meets educational focus target (60%)
  bool get meetsEducationalTarget {
    if (completedAchievements == 0) return true; // No achievements yet
    return educationalPercentage >= 0.55; // 55% minimum (allowing some tolerance)
  }

  /// Get category breakdown
  Map<String, int> get categoryBreakdown {
    return {
      'educational': educationalCompleted,
      'risk_management': riskManagementCompleted,
      'performance': performanceCompleted,
      'social': socialCompleted,
    };
  }

  factory UserAchievementStats.fromJson(Map<String, dynamic> json) {
    return UserAchievementStats(
      totalAchievements: json['total_achievements'] as int,
      completedAchievements: json['completed_achievements'] as int,
      educationalCompleted: json['educational_completed'] as int,
      riskManagementCompleted: json['risk_management_completed'] as int,
      performanceCompleted: json['performance_completed'] as int,
      socialCompleted: json['social_completed'] as int,
      totalXPEarned: json['total_xp_earned'] as int,
      leaguePoints: json['league_points'] as int,
      currentLeague: json['current_league'] as String,
      educationalPercentage: json['educational_percentage'] as double,
      leagueProgression: json['league_progression'] != null
          ? LeagueProgression.fromJson(json['league_progression'] as Map<String, dynamic>)
          : null,
      recentlyCompleted: (json['recently_completed'] as List? ?? [])
          .map((item) => Achievement.fromJson(item as Map<String, dynamic>))
          .toList(),
      recommended: (json['recommended'] as List? ?? [])
          .map((item) => Achievement.fromJson(item as Map<String, dynamic>))
          .toList(),
    );
  }
}