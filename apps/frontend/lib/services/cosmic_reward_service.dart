import 'package:flutter/foundation.dart';
import '../models/simple_trade.dart';
import 'cosmic_audio_service.dart';

/// Service for calculating cosmic rewards from trading activities
/// Provides stellar shards and experience point calculations based on trade performance
class CosmicRewardService {
  /// Calculate stellar shards reward based on trade outcome and player level
  static int calculateStellarShards(SimpleTrade trade, int currentLevel) {
    // Determine trade success from profitLoss or unrealizedPnL
    final pnl = trade.profitLoss ?? trade.unrealizedPnL ?? 0.0;

    // Base reward: higher for successful trades
    int baseReward = pnl > 0 ? 15 : 3;

    // Level multiplier increases rewards as player progresses
    double levelMultiplier = 1.0 + (currentLevel * 0.2);

    // Real trades get bonus multiplier
    double realTradeMultiplier = trade.isRealTrade ? 2.0 : 1.0;

    // Apply all multipliers
    int finalReward = (baseReward * levelMultiplier * realTradeMultiplier)
        .round();

    // Ensure minimum reward
    return finalReward < 1 ? 1 : finalReward;
  }

  /// Calculate experience points based on trade outcome
  static int calculateExperience(SimpleTrade trade) {
    // Determine trade success from profitLoss or unrealizedPnL
    final pnl = trade.profitLoss ?? trade.unrealizedPnL ?? 0.0;

    // Base XP: more for successful trades
    int baseXP = pnl > 0 ? 8 : 3;

    // Real trades get bonus XP
    int realTradeBonus = trade.isRealTrade ? 5 : 0;

    return baseXP + realTradeBonus;
  }

  /// Calculate if player should level up based on current experience
  static bool shouldLevelUp(int currentExperience, int experienceGained) {
    int currentLevel = (currentExperience / 100).floor() + 1;
    int newLevel = ((currentExperience + experienceGained) / 100).floor() + 1;
    return newLevel > currentLevel;
  }

  /// Calculate new level based on total experience
  static int calculateLevel(int totalExperience) {
    return (totalExperience / 100).floor() + 1;
  }

  /// Get cosmic tier based on level
  static String getCosmicTierName(int level) {
    if (level >= 50) return "Universal Sovereign";
    if (level >= 30) return "Stellar Architect";
    if (level >= 15) return "Genesis Awakener";
    if (level >= 5) return "Cosmic Trainee";
    return "Stellar Seedling";
  }

  /// Get cosmic tier emoji based on level
  static String getCosmicTierEmoji(int level) {
    if (level >= 50) return "🌌";
    if (level >= 30) return "⭐";
    if (level >= 15) return "✨";
    if (level >= 5) return "🌟";
    return "🌱";
  }

  /// Generate cosmic success message
  static String generateSuccessMessage(
    int stellarShardsGained,
    int experienceGained,
    bool leveledUp,
    String newTierName,
  ) {
    if (leveledUp) {
      return "🎉 COSMIC EVOLUTION! Welcome to $newTierName!\n⭐ +$stellarShardsGained Stellar Shards, +$experienceGained XP";
    } else {
      return "⭐ Stellar Alignment Achieved!\n+$stellarShardsGained Stellar Shards, +$experienceGained XP";
    }
  }

  /// Generate cosmic attempt message (for unsuccessful trades)
  static String generateAttemptMessage(
    int stellarShardsGained,
    int experienceGained,
  ) {
    return "🔄 Cosmic Energy Channeled!\n+$stellarShardsGained Stellar Shards, +$experienceGained XP";
  }

  /// Trigger appropriate audio feedback based on cosmic event
  static Future<void> triggerCosmicAudio({
    required bool isSuccess,
    required bool didLevelUp,
    required bool didTierUp,
    int currentLevel = 1,
  }) async {
    try {
      if (didTierUp && currentLevel >= 10) {
        // Special cosmic celebration for major tier advancement
        await CosmicAudioService.playCosmicCelebration();
      } else if (didLevelUp) {
        // Level up fanfare
        await CosmicAudioService.playLevelUpFanfare();
      } else if (isSuccess) {
        // Success chime
        await CosmicAudioService.playSuccessChime();
      } else {
        // Attempt tone
        await CosmicAudioService.playAttemptTone();
      }
    } catch (e) {
      // Audio is enhancement only - don't let errors disrupt the experience
      if (kDebugMode) {
        print('⚠️ Cosmic audio feedback error (non-critical): $e');
      }
    }
  }
}
