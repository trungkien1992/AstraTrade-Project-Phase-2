/// User Progression Model for AstraTrade Exchange V2
/// 
/// Represents the gamification state of a user including:
/// - XP and level progression
/// - Achievement tracking
/// - Trading statistics
/// - Streak information

import 'dart:convert';

class UserProgression {
  final String userAddress;
  final BigInt totalXp;
  final int currentLevel;
  final int streakDays;
  final DateTime lastActivityTimestamp;
  final BigInt achievementMask;
  final BigInt practiceBalance;
  final int totalTrades;
  final int profitableTrades;
  final int maxLeverageAllowed;
  final bool isKycVerified;

  const UserProgression({
    required this.userAddress,
    required this.totalXp,
    required this.currentLevel,
    required this.streakDays,
    required this.lastActivityTimestamp,
    required this.achievementMask,
    required this.practiceBalance,
    required this.totalTrades,
    required this.profitableTrades,
    required this.maxLeverageAllowed,
    required this.isKycVerified,
  });

  /// Create UserProgression from contract response
  factory UserProgression.fromContractResponse(List<String> response) {
    return UserProgression(
      userAddress: response[0],
      totalXp: BigInt.parse(response[1]),
      currentLevel: int.parse(response[2]),
      streakDays: int.parse(response[3]),
      lastActivityTimestamp: DateTime.fromMillisecondsSinceEpoch(
        int.parse(response[4]) * 1000
      ),
      achievementMask: BigInt.parse(response[5]),
      practiceBalance: BigInt.parse(response[6]),
      totalTrades: int.parse(response[7]),
      profitableTrades: int.parse(response[8]),
      maxLeverageAllowed: int.parse(response[9]),
      isKycVerified: response[10] == '1',
    );
  }

  /// Create UserProgression from JSON
  factory UserProgression.fromJson(Map<String, dynamic> json) {
    return UserProgression(
      userAddress: json['userAddress'] as String,
      totalXp: BigInt.parse(json['totalXp'] as String),
      currentLevel: json['currentLevel'] as int,
      streakDays: json['streakDays'] as int,
      lastActivityTimestamp: DateTime.parse(json['lastActivityTimestamp'] as String),
      achievementMask: BigInt.parse(json['achievementMask'] as String),
      practiceBalance: BigInt.parse(json['practiceBalance'] as String),
      totalTrades: json['totalTrades'] as int,
      profitableTrades: json['profitableTrades'] as int,
      maxLeverageAllowed: json['maxLeverageAllowed'] as int,
      isKycVerified: json['isKycVerified'] as bool,
    );
  }

  /// Convert to JSON
  Map<String, dynamic> toJson() {
    return {
      'userAddress': userAddress,
      'totalXp': totalXp.toString(),
      'currentLevel': currentLevel,
      'streakDays': streakDays,
      'lastActivityTimestamp': lastActivityTimestamp.toIso8601String(),
      'achievementMask': achievementMask.toString(),
      'practiceBalance': practiceBalance.toString(),
      'totalTrades': totalTrades,
      'profitableTrades': profitableTrades,
      'maxLeverageAllowed': maxLeverageAllowed,
      'isKycVerified': isKycVerified,
    };
  }

  /// Get XP required for next level
  int get xpForNextLevel {
    final nextLevel = currentLevel + 1;
    final requiredXp = nextLevel * nextLevel * 100; // Level formula: sqrt(XP/100) + 1
    return requiredXp;
  }

  /// Get XP progress to next level (0.0 to 1.0)
  double get levelProgress {
    final currentLevelXp = currentLevel * currentLevel * 100;
    final nextLevelXp = xpForNextLevel;
    final progressXp = totalXp.toInt() - currentLevelXp;
    final totalNeededXp = nextLevelXp - currentLevelXp;
    
    if (totalNeededXp <= 0) return 1.0;
    return (progressXp / totalNeededXp).clamp(0.0, 1.0);
  }

  /// Get profit percentage
  double get profitPercentage {
    if (totalTrades == 0) return 0.0;
    return (profitableTrades / totalTrades) * 100.0;
  }

  /// Check if user has specific achievement
  bool hasAchievement(int achievementId) {
    final bitPosition = achievementId - 1;
    final mask = BigInt.one << bitPosition;
    return (achievementMask & mask) != BigInt.zero;
  }

  /// Get list of unlocked achievements
  List<Achievement> get unlockedAchievements {
    List<Achievement> achievements = [];
    
    // Check each achievement bit
    for (int i = 0; i < 32; i++) {
      if (hasAchievement(i + 1)) {
        achievements.add(Achievement.fromId(i + 1));
      }
    }
    
    return achievements;
  }

  /// Get practice balance in readable format
  String get practiceBalanceFormatted {
    final balance = practiceBalance / BigInt.from(10).pow(18); // Assume 18 decimals
    return balance.toString();
  }

  /// Get trading experience level
  TradingExperience get tradingExperience {
    if (totalTrades < 10) return TradingExperience.beginner;
    if (totalTrades < 50) return TradingExperience.intermediate;
    if (totalTrades < 100) return TradingExperience.advanced;
    return TradingExperience.expert;
  }

  /// Copy with updated values
  UserProgression copyWith({
    String? userAddress,
    BigInt? totalXp,
    int? currentLevel,
    int? streakDays,
    DateTime? lastActivityTimestamp,
    BigInt? achievementMask,
    BigInt? practiceBalance,
    int? totalTrades,
    int? profitableTrades,
    int? maxLeverageAllowed,
    bool? isKycVerified,
  }) {
    return UserProgression(
      userAddress: userAddress ?? this.userAddress,
      totalXp: totalXp ?? this.totalXp,
      currentLevel: currentLevel ?? this.currentLevel,
      streakDays: streakDays ?? this.streakDays,
      lastActivityTimestamp: lastActivityTimestamp ?? this.lastActivityTimestamp,
      achievementMask: achievementMask ?? this.achievementMask,
      practiceBalance: practiceBalance ?? this.practiceBalance,
      totalTrades: totalTrades ?? this.totalTrades,
      profitableTrades: profitableTrades ?? this.profitableTrades,
      maxLeverageAllowed: maxLeverageAllowed ?? this.maxLeverageAllowed,
      isKycVerified: isKycVerified ?? this.isKycVerified,
    );
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    
    return other is UserProgression &&
        other.userAddress == userAddress &&
        other.totalXp == totalXp &&
        other.currentLevel == currentLevel &&
        other.streakDays == streakDays &&
        other.lastActivityTimestamp == lastActivityTimestamp &&
        other.achievementMask == achievementMask &&
        other.practiceBalance == practiceBalance &&
        other.totalTrades == totalTrades &&
        other.profitableTrades == profitableTrades &&
        other.maxLeverageAllowed == maxLeverageAllowed &&
        other.isKycVerified == isKycVerified;
  }

  @override
  int get hashCode {
    return Object.hash(
      userAddress,
      totalXp,
      currentLevel,
      streakDays,
      lastActivityTimestamp,
      achievementMask,
      practiceBalance,
      totalTrades,
      profitableTrades,
      maxLeverageAllowed,
      isKycVerified,
    );
  }

  @override
  String toString() {
    return 'UserProgression(userAddress: $userAddress, currentLevel: $currentLevel, totalXp: $totalXp, streakDays: $streakDays, totalTrades: $totalTrades)';
  }
}

/// Achievement data class
class Achievement {
  final int id;
  final String name;
  final String description;
  final int xpReward;
  final AchievementRarity rarity;

  const Achievement({
    required this.id,
    required this.name,
    required this.description,
    required this.xpReward,
    required this.rarity,
  });

  /// Create achievement from ID
  factory Achievement.fromId(int id) {
    switch (id) {
      case 1:
        return const Achievement(
          id: 1,
          name: 'First Trade',
          description: 'Complete your first trade',
          xpReward: 100,
          rarity: AchievementRarity.common,
        );
      case 2:
        return const Achievement(
          id: 2,
          name: 'Trader Novice',
          description: 'Complete 10 trades',
          xpReward: 250,
          rarity: AchievementRarity.common,
        );
      case 3:
        return const Achievement(
          id: 3,
          name: 'Trader Expert',
          description: 'Complete 100 trades',
          xpReward: 500,
          rarity: AchievementRarity.rare,
        );
      case 4:
        return const Achievement(
          id: 4,
          name: 'Week Warrior',
          description: 'Maintain a 7-day trading streak',
          xpReward: 300,
          rarity: AchievementRarity.uncommon,
        );
      case 5:
        return const Achievement(
          id: 5,
          name: 'Profit Master',
          description: 'Achieve 70%+ profit rate with 10+ trades',
          xpReward: 750,
          rarity: AchievementRarity.legendary,
        );
      default:
        return Achievement(
          id: id,
          name: 'Unknown Achievement',
          description: 'Mystery achievement',
          xpReward: 0,
          rarity: AchievementRarity.common,
        );
    }
  }

  /// Convert to JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'xpReward': xpReward,
      'rarity': rarity.name,
    };
  }

  /// Create from JSON  
  factory Achievement.fromJson(Map<String, dynamic> json) {
    return Achievement(
      id: json['id'] as int,
      name: json['name'] as String,
      description: json['description'] as String,
      xpReward: json['xpReward'] as int,
      rarity: AchievementRarity.values.firstWhere(
        (r) => r.name == json['rarity'],
        orElse: () => AchievementRarity.common,
      ),
    );
  }
}

/// Achievement rarity levels
enum AchievementRarity {
  common,
  uncommon,
  rare,
  epic,
  legendary,
}

/// Trading experience levels
enum TradingExperience {
  beginner,
  intermediate,
  advanced,
  expert,
}

/// Extension for better display of trading experience
extension TradingExperienceExtension on TradingExperience {
  String get displayName {
    switch (this) {
      case TradingExperience.beginner:
        return 'Beginner';
      case TradingExperience.intermediate:
        return 'Intermediate';
      case TradingExperience.advanced:
        return 'Advanced';
      case TradingExperience.expert:
        return 'Expert';
    }
  }

  String get description {
    switch (this) {
      case TradingExperience.beginner:
        return 'Learning the basics';
      case TradingExperience.intermediate:
        return 'Building experience';
      case TradingExperience.advanced:
        return 'Skilled trader';
      case TradingExperience.expert:
        return 'Master trader';
    }
  }
}