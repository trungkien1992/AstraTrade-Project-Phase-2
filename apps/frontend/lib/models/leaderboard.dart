import 'dart:math' as math;
import 'package:json_annotation/json_annotation.dart';

part 'leaderboard.g.dart';

/// Represents a player's entry on the leaderboard
@JsonSerializable()
class LeaderboardEntry {
  final String userId;
  final String username;
  final String avatarUrl;
  final int rank;
  final int stellarShards;
  final int lumina;
  final int level;
  final int totalXP;
  final String cosmicTier;
  final bool isVerifiedLuminaWeaver;
  final bool isCurrentUser;
  final String planetIcon;
  final int winStreak;
  final int totalTrades;
  final double winRate;
  final DateTime lastActive;

  const LeaderboardEntry({
    required this.userId,
    required this.username,
    required this.avatarUrl,
    required this.rank,
    required this.stellarShards,
    required this.lumina,
    required this.level,
    required this.totalXP,
    required this.cosmicTier,
    this.isVerifiedLuminaWeaver = false,
    this.isCurrentUser = false,
    required this.planetIcon,
    this.winStreak = 0,
    this.totalTrades = 0,
    this.winRate = 0.0,
    required this.lastActive,
  });

  factory LeaderboardEntry.fromJson(Map<String, dynamic> json) =>
      _$LeaderboardEntryFromJson(json);

  Map<String, dynamic> toJson() => _$LeaderboardEntryToJson(this);

  LeaderboardEntry copyWith({
    String? userId,
    String? username,
    String? avatarUrl,
    int? rank,
    int? stellarShards,
    int? lumina,
    int? level,
    int? totalXP,
    String? cosmicTier,
    bool? isVerifiedLuminaWeaver,
    bool? isCurrentUser,
    String? planetIcon,
    int? winStreak,
    int? totalTrades,
    double? winRate,
    DateTime? lastActive,
  }) {
    return LeaderboardEntry(
      userId: userId ?? this.userId,
      username: username ?? this.username,
      avatarUrl: avatarUrl ?? this.avatarUrl,
      rank: rank ?? this.rank,
      stellarShards: stellarShards ?? this.stellarShards,
      lumina: lumina ?? this.lumina,
      level: level ?? this.level,
      totalXP: totalXP ?? this.totalXP,
      cosmicTier: cosmicTier ?? this.cosmicTier,
      isVerifiedLuminaWeaver: isVerifiedLuminaWeaver ?? this.isVerifiedLuminaWeaver,
      isCurrentUser: isCurrentUser ?? this.isCurrentUser,
      planetIcon: planetIcon ?? this.planetIcon,
      winStreak: winStreak ?? this.winStreak,
      totalTrades: totalTrades ?? this.totalTrades,
      winRate: winRate ?? this.winRate,
      lastActive: lastActive ?? this.lastActive,
    );
  }
}

/// Enum for different leaderboard types
enum LeaderboardType {
  stellarShards,  // Trade Token Leaderboard (SS)
  lumina,         // Lumina Flow Leaderboard (LM) - Pro Traders only
  level,          // Level-based ranking
  winStreak,      // Current win streak
}

/// Represents the cosmic tier progression system
enum CosmicTier {
  stellarSeedling('Stellar Seedling', 0, '🌱'),
  cosmicGardener('Cosmic Gardener', 100, '🌿'),
  nebulaNavigator('Nebula Navigator', 500, '🌌'),
  stellarStrategist('Stellar Strategist', 2000, '⭐'),
  galaxyGrandmaster('Galaxy Grandmaster', 5000, '🌟'),
  universalSovereign('Universal Sovereign', 10000, '👑');

  const CosmicTier(this.displayName, this.requiredXP, this.icon);

  final String displayName;
  final int requiredXP;
  final String icon;

  /// Get cosmic tier based on total XP
  static CosmicTier fromXP(int totalXP) {
    final tiers = CosmicTier.values.reversed.toList();
    for (final tier in tiers) {
      if (totalXP >= tier.requiredXP) {
        return tier;
      }
    }
    return CosmicTier.stellarSeedling;
  }

  /// Get progress to next tier (0.0 to 1.0)
  double getProgressToNext(int currentXP) {
    final currentIndex = CosmicTier.values.indexOf(this);
    if (currentIndex == CosmicTier.values.length - 1) {
      return 1.0; // Max tier reached
    }
    
    final nextTier = CosmicTier.values[currentIndex + 1];
    final progressRange = nextTier.requiredXP - requiredXP;
    final currentProgress = currentXP - requiredXP;
    
    return (currentProgress / progressRange).clamp(0.0, 1.0);
  }

  /// Get XP needed to reach next tier
  int getXPToNext(int currentXP) {
    final currentIndex = CosmicTier.values.indexOf(this);
    if (currentIndex == CosmicTier.values.length - 1) {
      return 0; // Max tier reached
    }
    
    final nextTier = CosmicTier.values[currentIndex + 1];
    return (nextTier.requiredXP - currentXP).clamp(0, nextTier.requiredXP);
  }
}

/// XP calculation utilities
class XPCalculator {
  // Base XP rewards
  static const int baseTradeXP = 10;
  static const int baseCriticalForgeXP = 25;
  static const int realTradeXPMultiplier = 2;
  
  // Streak bonuses
  static const Map<int, double> streakMultipliers = {
    0: 1.0,   // No streak
    3: 1.2,   // 3-win streak: +20%
    5: 1.5,   // 5-win streak: +50%
    10: 2.0,  // 10-win streak: +100%
    15: 2.5,  // 15-win streak: +150%
    20: 3.0,  // 20-win streak: +200%
  };

  /// Calculate XP for a trade based on outcome and streak
  static int calculateTradeXP({
    required bool isProfit,
    required bool isCriticalForge,
    required bool isRealTrade,
    required int winStreak,
    required double profitPercentage,
  }) {
    if (!isProfit) return 2; // Small consolation XP for losses
    
    // Base XP calculation
    int baseXP = isCriticalForge ? baseCriticalForgeXP : baseTradeXP;
    
    // Real trade multiplier
    if (isRealTrade) {
      baseXP = (baseXP * realTradeXPMultiplier).round();
    }
    
    // Profit percentage bonus (up to 50% bonus for high profits)
    double profitBonus = 1.0 + (profitPercentage.abs() / 100 * 0.5).clamp(0.0, 0.5);
    baseXP = (baseXP * profitBonus).round();
    
    // Streak multiplier
    double streakMultiplier = _getStreakMultiplier(winStreak);
    baseXP = (baseXP * streakMultiplier).round();
    
    return baseXP;
  }

  /// Calculate level from total XP using exponential growth
  static int calculateLevel(int totalXP) {
    if (totalXP < 100) return 1;
    
    // Level formula: level = floor(sqrt(totalXP / 50)) + 1
    // This creates a smooth progression where higher levels require more XP
    return (math.sqrt(totalXP / 50).floor() + 1).clamp(1, 100);
  }

  /// Calculate XP required for a specific level
  static int getXPForLevel(int level) {
    if (level <= 1) return 0;
    return ((level - 1) * (level - 1) * 50).round();
  }

  /// Calculate XP needed to reach next level
  static int getXPToNextLevel(int currentXP) {
    int currentLevel = calculateLevel(currentXP);
    int nextLevelXP = getXPForLevel(currentLevel + 1);
    return nextLevelXP - currentXP;
  }

  /// Get streak multiplier for current win streak
  static double _getStreakMultiplier(int winStreak) {
    // Find the highest applicable streak bonus
    double multiplier = 1.0;
    for (final entry in streakMultipliers.entries) {
      if (winStreak >= entry.key) {
        multiplier = entry.value;
      }
    }
    return multiplier;
  }
}

