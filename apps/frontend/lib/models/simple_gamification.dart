import 'package:json_annotation/json_annotation.dart';

part 'simple_gamification.g.dart';

/// Simple gamification system for AstraTrade
/// Basic XP, levels, and achievements without cosmic themes

@JsonSerializable()
class PlayerProgress {
  final String playerId;
  final int xp;
  final int level;
  final int tradingPoints; // TP - earned from trading activities
  final int practicePoints; // PP - earned from practice trades
  final int streakDays;
  final DateTime lastActiveDate;
  final DateTime createdAt;
  final List<String> achievements;
  final Map<String, int> stats;

  const PlayerProgress({
    required this.playerId,
    required this.xp,
    required this.level,
    required this.tradingPoints,
    required this.practicePoints,
    required this.streakDays,
    required this.lastActiveDate,
    required this.createdAt,
    required this.achievements,
    required this.stats,
  });

  factory PlayerProgress.fromJson(Map<String, dynamic> json) =>
      _$PlayerProgressFromJson(json);
  Map<String, dynamic> toJson() => _$PlayerProgressToJson(this);

  /// Create initial progress for new player
  factory PlayerProgress.newPlayer(String playerId) {
    return PlayerProgress(
      playerId: playerId,
      xp: 0,
      level: 1,
      tradingPoints: 0,
      practicePoints: 0,
      streakDays: 0,
      lastActiveDate: DateTime.now(),
      createdAt: DateTime.now(),
      achievements: [],
      stats: {
        'total_trades': 0,
        'practice_trades': 0,
        'real_trades': 0,
        'profitable_trades': 0,
        'total_profit': 0,
        'best_streak': 0,
        'days_active': 1,
      },
    );
  }

  /// Calculate XP required for level
  static int xpRequiredForLevel(int level) {
    return 100 * level * level;
  }

  /// Get total XP from all sources
  int get totalXP => xp;

  /// Check if player can level up
  bool get canLevelUp => totalXP >= xpRequiredForLevel(level + 1);

  /// Get progress to next level (0.0 to 1.0)
  double get levelProgress {
    final currentLevelXP = xpRequiredForLevel(level);
    final nextLevelXP = xpRequiredForLevel(level + 1);
    final progressXP = totalXP - currentLevelXP;
    final requiredXP = nextLevelXP - currentLevelXP;
    return (progressXP / requiredXP).clamp(0.0, 1.0);
  }

  /// Get XP needed for next level
  int get xpToNextLevel {
    final nextLevelXP = xpRequiredForLevel(level + 1);
    return nextLevelXP - totalXP;
  }

  /// Check if player has active streak
  bool get hasActiveStreak {
    final now = DateTime.now();
    final lastActive = DateTime(
      lastActiveDate.year,
      lastActiveDate.month,
      lastActiveDate.day,
    );
    final today = DateTime(now.year, now.month, now.day);
    final yesterday = today.subtract(const Duration(days: 1));

    return lastActive.isAtSameMomentAs(today) ||
        lastActive.isAtSameMomentAs(yesterday);
  }

  /// Get daily reward multiplier based on streak
  double get streakMultiplier {
    if (streakDays == 0) return 1.0;
    return (1.0 + (streakDays * 0.05)).clamp(1.0, 2.0); // 5% per day, max 2x
  }

  /// Get player rank based on level
  String get rank {
    if (level >= 50) return 'Expert Trader';
    if (level >= 30) return 'Advanced Trader';
    if (level >= 20) return 'Intermediate Trader';
    if (level >= 10) return 'Experienced Trader';
    if (level >= 5) return 'Novice Trader';
    return 'Beginner Trader';
  }

  PlayerProgress copyWith({
    String? playerId,
    int? xp,
    int? level,
    int? tradingPoints,
    int? practicePoints,
    int? streakDays,
    DateTime? lastActiveDate,
    DateTime? createdAt,
    List<String>? achievements,
    Map<String, int>? stats,
  }) {
    return PlayerProgress(
      playerId: playerId ?? this.playerId,
      xp: xp ?? this.xp,
      level: level ?? this.level,
      tradingPoints: tradingPoints ?? this.tradingPoints,
      practicePoints: practicePoints ?? this.practicePoints,
      streakDays: streakDays ?? this.streakDays,
      lastActiveDate: lastActiveDate ?? this.lastActiveDate,
      createdAt: createdAt ?? this.createdAt,
      achievements: achievements ?? this.achievements,
      stats: stats ?? this.stats,
    );
  }
}

/// Achievement definition
@JsonSerializable()
class Achievement {
  final String id;
  final String name;
  final String description;
  final AchievementType type;
  final int targetValue;
  final int xpReward;
  final int tradingPointsReward;
  final String iconName;
  final AchievementRarity rarity;
  final List<String> requirements;

  const Achievement({
    required this.id,
    required this.name,
    required this.description,
    required this.type,
    required this.targetValue,
    required this.xpReward,
    required this.tradingPointsReward,
    required this.iconName,
    required this.rarity,
    required this.requirements,
  });

  factory Achievement.fromJson(Map<String, dynamic> json) =>
      _$AchievementFromJson(json);
  Map<String, dynamic> toJson() => _$AchievementToJson(this);
}

/// Types of achievements
enum AchievementType {
  @JsonValue('first_trade')
  firstTrade,
  @JsonValue('trade_count')
  tradeCount,
  @JsonValue('profit_target')
  profitTarget,
  @JsonValue('streak_milestone')
  streakMilestone,
  @JsonValue('level_milestone')
  levelMilestone,
  @JsonValue('practice_milestone')
  practiceMilestone,
  @JsonValue('real_trading')
  realTrading,
  @JsonValue('special_event')
  specialEvent,
}

/// Achievement rarity levels
enum AchievementRarity {
  @JsonValue('common')
  common,
  @JsonValue('uncommon')
  uncommon,
  @JsonValue('rare')
  rare,
  @JsonValue('epic')
  epic,
  @JsonValue('legendary')
  legendary,
}

/// XP gain event for tracking
@JsonSerializable()
class XPGainEvent {
  final String eventId;
  final String playerId;
  final XPGainSource source;
  final int xpGained;
  final int tradingPointsGained;
  final int practicePointsGained;
  final String description;
  final DateTime timestamp;
  final Map<String, dynamic> metadata;

  const XPGainEvent({
    required this.eventId,
    required this.playerId,
    required this.source,
    required this.xpGained,
    required this.tradingPointsGained,
    required this.practicePointsGained,
    required this.description,
    required this.timestamp,
    required this.metadata,
  });

  factory XPGainEvent.fromJson(Map<String, dynamic> json) =>
      _$XPGainEventFromJson(json);
  Map<String, dynamic> toJson() => _$XPGainEventToJson(this);
}

/// Sources of XP gain
enum XPGainSource {
  @JsonValue('practice_trade')
  practiceTrade,
  @JsonValue('real_trade')
  realTrade,
  @JsonValue('profitable_trade')
  profitableTrade,
  @JsonValue('daily_login')
  dailyLogin,
  @JsonValue('streak_bonus')
  streakBonus,
  @JsonValue('level_up')
  levelUp,
  @JsonValue('achievement')
  achievement,
  @JsonValue('first_time_bonus')
  firstTimeBonus,
}

/// Daily streak reward
@JsonSerializable()
class DailyReward {
  final int streakDay;
  final int xpReward;
  final int tradingPointsReward;
  final String description;
  final bool isMilestone;
  final Map<String, dynamic> bonusRewards;

  const DailyReward({
    required this.streakDay,
    required this.xpReward,
    required this.tradingPointsReward,
    required this.description,
    required this.isMilestone,
    required this.bonusRewards,
  });

  factory DailyReward.fromJson(Map<String, dynamic> json) =>
      _$DailyRewardFromJson(json);
  Map<String, dynamic> toJson() => _$DailyRewardToJson(this);

  /// Calculate daily reward based on streak
  static DailyReward calculateReward(int streakDay) {
    final baseXP = 25 + (streakDay * 5);
    final baseTP = 10 + (streakDay * 2);

    final isMilestone = streakDay % 7 == 0 || [30, 50, 100].contains(streakDay);

    return DailyReward(
      streakDay: streakDay,
      xpReward: isMilestone ? (baseXP * 2) : baseXP,
      tradingPointsReward: isMilestone ? (baseTP * 2) : baseTP,
      description: isMilestone
          ? 'Milestone Achieved! 🏆'
          : 'Daily Login Bonus ✨',
      isMilestone: isMilestone,
      bonusRewards: isMilestone
          ? {
              'title': _getMilestoneTitle(streakDay),
              'special_reward': _getSpecialReward(streakDay),
            }
          : {},
    );
  }

  static String _getMilestoneTitle(int streakDay) {
    if (streakDay >= 100) return 'Master Trader';
    if (streakDay >= 50) return 'Dedicated Trader';
    if (streakDay >= 30) return 'Committed Trader';
    if (streakDay >= 7) return 'Consistent Trader';
    return 'Active Trader';
  }

  static String _getSpecialReward(int streakDay) {
    if (streakDay >= 100) return 'Exclusive trader badge';
    if (streakDay >= 50) return 'Advanced trading tools';
    if (streakDay >= 30) return 'Premium features access';
    if (streakDay >= 7) return 'Trading bonus multiplier';
    return 'None';
  }
}
