import 'package:flutter/foundation.dart';
import 'dart:math' as math;

/// Daily cosmic challenges service for enhanced engagement
/// Provides rotating daily objectives with cosmic rewards
class CosmicChallengeService {
  static final _instance = CosmicChallengeService._internal();
  factory CosmicChallengeService() => _instance;
  CosmicChallengeService._internal();

  // Challenge state
  static DateTime? _lastChallengeDate;
  static List<CosmicChallenge> _dailyChallenges = [];
  static Map<String, int> _challengeProgress = {};

  /// Get today's cosmic challenges
  static List<CosmicChallenge> getTodaysChallenges() {
    final today = DateTime.now();
    final todayKey = '${today.year}-${today.month}-${today.day}';

    // Generate new challenges if needed
    if (_lastChallengeDate == null ||
        _lastChallengeDate!.day != today.day ||
        _dailyChallenges.isEmpty) {
      _generateDailyChallenges(today);
      _lastChallengeDate = today;
    }

    return _dailyChallenges;
  }

  /// Generate daily challenges based on date seed
  static void _generateDailyChallenges(DateTime date) {
    final random = math.Random(date.day + date.month * 31);
    final allChallenges = _getAllPossibleChallenges();

    // Select 3 random challenges for the day
    _dailyChallenges = [];
    final shuffled = List<CosmicChallenge>.from(allChallenges)..shuffle(random);
    _dailyChallenges = shuffled.take(3).toList();

    // Reset progress for new day
    _challengeProgress.clear();
    for (final challenge in _dailyChallenges) {
      _challengeProgress[challenge.id] = 0;
    }

    if (kDebugMode) {
      print('🌟 Generated daily cosmic challenges: ${_dailyChallenges.length}');
    }
  }

  /// Get all possible challenge templates
  static List<CosmicChallenge> _getAllPossibleChallenges() {
    return [
      // Trading frequency challenges
      CosmicChallenge(
        id: 'execute_5_trades',
        title: 'Cosmic Energy Flow',
        description: 'Execute 5 trades today',
        icon: '⚡',
        targetValue: 5,
        rewardStellarShards: 50,
        rewardExperience: 25,
        type: ChallengeType.tradingFrequency,
      ),

      CosmicChallenge(
        id: 'execute_10_trades',
        title: 'Energy Master',
        description: 'Execute 10 trades today',
        icon: '🌟',
        targetValue: 10,
        rewardStellarShards: 120,
        rewardExperience: 60,
        type: ChallengeType.tradingFrequency,
      ),

      // Success challenges
      CosmicChallenge(
        id: 'win_3_trades',
        title: 'Stellar Alignment',
        description: 'Win 3 successful trades',
        icon: '✨',
        targetValue: 3,
        rewardStellarShards: 75,
        rewardExperience: 40,
        type: ChallengeType.tradingSuccess,
      ),

      CosmicChallenge(
        id: 'win_streak_5',
        title: 'Cosmic Harmony',
        description: 'Achieve a 5-trade win streak',
        icon: '🌊',
        targetValue: 5,
        rewardStellarShards: 150,
        rewardExperience: 80,
        type: ChallengeType.winStreak,
      ),

      // Power-up challenges
      CosmicChallenge(
        id: 'use_3_powerups',
        title: 'Power Channeler',
        description: 'Use 3 different power-ups',
        icon: '🔮',
        targetValue: 3,
        rewardStellarShards: 60,
        rewardExperience: 30,
        type: ChallengeType.powerUpUsage,
      ),

      // Stellar shards challenges
      CosmicChallenge(
        id: 'earn_100_ss',
        title: 'Stellar Collector',
        description: 'Earn 100 Stellar Shards',
        icon: '💎',
        targetValue: 100,
        rewardStellarShards: 80,
        rewardExperience: 50,
        type: ChallengeType.stellarShardsEarned,
      ),

      CosmicChallenge(
        id: 'spend_50_ss',
        title: 'Cosmic Investor',
        description: 'Spend 50 Stellar Shards on power-ups',
        icon: '💰',
        targetValue: 50,
        rewardStellarShards: 75,
        rewardExperience: 35,
        type: ChallengeType.stellarShardsSpent,
      ),

      // Exploration challenges
      CosmicChallenge(
        id: 'try_3_symbols',
        title: 'Cosmic Explorer',
        description: 'Trade 3 different symbols',
        icon: '🚀',
        targetValue: 3,
        rewardStellarShards: 65,
        rewardExperience: 45,
        type: ChallengeType.symbolDiversity,
      ),

      // Persistence challenges
      CosmicChallenge(
        id: 'trade_after_loss',
        title: 'Cosmic Resilience',
        description: 'Execute a trade after a loss',
        icon: '🛡️',
        targetValue: 1,
        rewardStellarShards: 40,
        rewardExperience: 25,
        type: ChallengeType.resilience,
      ),
    ];
  }

  /// Update challenge progress
  static void updateChallengeProgress({
    required String challengeType,
    int value = 1,
    Map<String, dynamic>? data,
  }) {
    final challenges = getTodaysChallenges();

    for (final challenge in challenges) {
      bool shouldUpdate = false;

      switch (challenge.type) {
        case ChallengeType.tradingFrequency:
          if (challengeType == 'trade_executed') shouldUpdate = true;
          break;
        case ChallengeType.tradingSuccess:
          if (challengeType == 'trade_success') shouldUpdate = true;
          break;
        case ChallengeType.winStreak:
          if (challengeType == 'win_streak' && data != null) {
            _challengeProgress[challenge.id] = data['streak'] ?? 0;
            continue;
          }
          break;
        case ChallengeType.powerUpUsage:
          if (challengeType == 'powerup_used') shouldUpdate = true;
          break;
        case ChallengeType.stellarShardsEarned:
          if (challengeType == 'stellar_shards_earned') {
            _challengeProgress[challenge.id] =
                (_challengeProgress[challenge.id] ?? 0) + value;
            continue;
          }
          break;
        case ChallengeType.stellarShardsSpent:
          if (challengeType == 'stellar_shards_spent') {
            _challengeProgress[challenge.id] =
                (_challengeProgress[challenge.id] ?? 0) + value;
            continue;
          }
          break;
        case ChallengeType.symbolDiversity:
          if (challengeType == 'symbol_traded' && data != null) {
            // Track unique symbols
            final symbols = Set<String>.from(data['tradedSymbols'] ?? []);
            _challengeProgress[challenge.id] = symbols.length;
            continue;
          }
          break;
        case ChallengeType.resilience:
          if (challengeType == 'trade_after_loss') shouldUpdate = true;
          break;
      }

      if (shouldUpdate) {
        _challengeProgress[challenge.id] =
            (_challengeProgress[challenge.id] ?? 0) + value;
      }
    }

    if (kDebugMode) {
      print('🎯 Challenge progress updated: $challengeType');
    }
  }

  /// Get challenge progress
  static int getChallengeProgress(String challengeId) {
    return _challengeProgress[challengeId] ?? 0;
  }

  /// Check if challenge is completed
  static bool isChallengeCompleted(CosmicChallenge challenge) {
    final progress = getChallengeProgress(challenge.id);
    return progress >= challenge.targetValue;
  }

  /// Get completed challenges
  static List<CosmicChallenge> getCompletedChallenges() {
    return getTodaysChallenges()
        .where((challenge) => isChallengeCompleted(challenge))
        .toList();
  }

  /// Get incomplete challenges
  static List<CosmicChallenge> getIncompleteChallenges() {
    return getTodaysChallenges()
        .where((challenge) => !isChallengeCompleted(challenge))
        .toList();
  }

  /// Get challenge completion percentage
  static double getChallengeCompletionRate() {
    final challenges = getTodaysChallenges();
    if (challenges.isEmpty) return 0.0;

    final completed = getCompletedChallenges().length;
    return completed / challenges.length;
  }

  /// Get total potential rewards for today
  static ChallengeRewards getTotalPotentialRewards() {
    final challenges = getTodaysChallenges();
    int totalSS = 0;
    int totalXP = 0;

    for (final challenge in challenges) {
      totalSS += challenge.rewardStellarShards;
      totalXP += challenge.rewardExperience;
    }

    return ChallengeRewards(stellarShards: totalSS, experience: totalXP);
  }

  /// Claim rewards for completed challenges
  static ChallengeRewards claimCompletedRewards() {
    final completed = getCompletedChallenges();
    int totalSS = 0;
    int totalXP = 0;

    for (final challenge in completed) {
      totalSS += challenge.rewardStellarShards;
      totalXP += challenge.rewardExperience;
    }

    if (kDebugMode) {
      print('🎁 Claimed challenge rewards: ${totalSS}SS, ${totalXP}XP');
    }

    return ChallengeRewards(stellarShards: totalSS, experience: totalXP);
  }
}

/// Cosmic challenge data model
class CosmicChallenge {
  final String id;
  final String title;
  final String description;
  final String icon;
  final int targetValue;
  final int rewardStellarShards;
  final int rewardExperience;
  final ChallengeType type;

  const CosmicChallenge({
    required this.id,
    required this.title,
    required this.description,
    required this.icon,
    required this.targetValue,
    required this.rewardStellarShards,
    required this.rewardExperience,
    required this.type,
  });
}

/// Challenge type enumeration
enum ChallengeType {
  tradingFrequency,
  tradingSuccess,
  winStreak,
  powerUpUsage,
  stellarShardsEarned,
  stellarShardsSpent,
  symbolDiversity,
  resilience,
}

/// Challenge rewards data model
class ChallengeRewards {
  final int stellarShards;
  final int experience;

  const ChallengeRewards({
    required this.stellarShards,
    required this.experience,
  });
}
