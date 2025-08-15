import 'package:flutter/material.dart';
import 'package:share_plus/share_plus.dart';
import '../models/simple_gamification.dart';
import '../models/simple_trade.dart';
import '../services/mobile_haptic_service.dart';
import '../services/mobile_notification_service.dart';

/// Simple social service for sharing achievements and trading progress
/// Integrates with simple gamification system (non-cosmic theme)
class SimpleSocialService {
  static final SimpleSocialService _instance = SimpleSocialService._internal();
  factory SimpleSocialService() => _instance;
  SimpleSocialService._internal();

  final _hapticService = MobileHapticService();
  final _notificationService = MobileNotificationService();

  /// Share achievement unlock with friends
  Future<void> shareAchievement({
    required Achievement achievement,
    required int currentLevel,
    required int totalXP,
    Widget? customWidget,
  }) async {
    await _hapticService.initialize();

    final message = _generateAchievementMessage(
      achievement: achievement,
      currentLevel: currentLevel,
      totalXP: totalXP,
    );

    await _hapticService.success();

    await Share.share(message, subject: 'AstraTrade Achievement Unlocked! 🏆');

    // Show success feedback
    await _notificationService.showTradingAlert(
      title: '🚀 Achievement Shared!',
      message:
          'Your ${achievement.name} achievement has been shared with friends',
      color: Colors.green,
    );
  }

  /// Share level up progress
  Future<void> shareLevelUp({
    required int newLevel,
    required int totalXP,
    required int xpToNext,
    Widget? levelUpWidget,
  }) async {
    await _hapticService.initialize();

    final message =
        '''
🎯 Level Up in AstraTrade! 🎯

🔥 Level: $newLevel
⭐ Total XP: $totalXP
📈 Next Level: ${xpToNext} XP to go

Master the art of trading with gamified learning!
#AstraTrade #TradingSkills #LevelUp #Finance
''';

    await _hapticService.levelUp(newLevel: newLevel);

    await Share.share(message, subject: 'Level $newLevel Achieved! 🚀');
  }

  /// Share trading streak achievement
  Future<void> shareStreak({
    required int streakDays,
    required double successRate,
    required int totalTrades,
    Widget? streakWidget,
  }) async {
    await _hapticService.initialize();

    final message =
        '''
🔥 $streakDays-Day Trading Streak! 🔥

📊 Success Rate: ${(successRate * 100).toStringAsFixed(1)}%
📈 Total Trades: $totalTrades
🎯 Consistency pays off!

Join me on AstraTrade - gamified trading education!
#AstraTrade #TradingStreak #FinanceEducation
''';

    await _hapticService.dailyStreak(
      streakDays: streakDays,
      isMilestone: streakDays % 7 == 0,
    );

    await Share.share(
      message,
      subject: '$streakDays-Day Streak Achievement! 🔥',
    );
  }

  /// Share successful trade with performance stats
  Future<void> shareTradeSuccess({
    required SimpleTrade trade,
    required double profitPercentage,
    required int currentLevel,
  }) async {
    await _hapticService.initialize();

    final message =
        '''
📈 Successful Trade on AstraTrade! 📈

💰 ${trade.symbol}: ${trade.direction} 
📊 Profit: +${profitPercentage.toStringAsFixed(1)}%
🎯 Level: $currentLevel

Learning trading through gamification!
#AstraTrade #TradingSuccess #FinanceEducation
''';

    await _hapticService.tradeCompleted(
      trade: trade,
      isProfit: (trade.profitLoss ?? 0) > 0,
    );

    await Share.share(message, subject: 'Trading Success! 💰');
  }

  /// Create friend challenge for trading competition
  Future<void> createFriendChallenge({
    required String challengeType,
    required int targetValue,
    required Duration duration,
  }) async {
    await _hapticService.initialize();

    final message = _generateChallengeMessage(
      challengeType: challengeType,
      targetValue: targetValue,
      duration: duration,
    );

    await _hapticService.mediumTap();

    await Share.share(message, subject: 'AstraTrade Challenge! 🎯');

    // Show confirmation
    await _notificationService.showTradingAlert(
      title: '⚡ Challenge Created!',
      message: 'Your $challengeType challenge has been shared with friends',
      color: Colors.blue,
    );
  }

  /// Share leaderboard position
  Future<void> shareLeaderboardPosition({
    required int rank,
    required int totalXP,
    required String rankTitle,
  }) async {
    await _hapticService.initialize();

    final message =
        '''
🏆 Leaderboard Update! 🏆

📍 Rank: #$rank
👑 Title: $rankTitle  
⭐ Total XP: $totalXP

Climbing the ranks in AstraTrade!
#AstraTrade #Leaderboard #TradingSkills
''';

    await _hapticService.success();

    await Share.share(message, subject: 'Leaderboard Rank #$rank! 🏆');
  }

  /// Generate achievement sharing message
  String _generateAchievementMessage({
    required Achievement achievement,
    required int currentLevel,
    required int totalXP,
  }) {
    final rarityEmoji = _getRarityEmoji(achievement.rarity);

    return '''
$rarityEmoji ${achievement.name} Unlocked! $rarityEmoji

🎯 ${achievement.description}
🔥 Level: $currentLevel
⭐ Total XP: $totalXP
🏆 XP Reward: +${achievement.xpReward}

${_getAchievementTypeMessage(achievement.type)}
#AstraTrade #Achievement #TradingSkills
''';
  }

  /// Generate friend challenge message
  String _generateChallengeMessage({
    required String challengeType,
    required int targetValue,
    required Duration duration,
  }) {
    final durationText = duration.inDays > 0
        ? '${duration.inDays} days'
        : '${duration.inHours} hours';

    return '''
🎯 AstraTrade Challenge! 🎯

Challenge: $challengeType
Target: $targetValue
Duration: $durationText

Think you can beat me? 
Download AstraTrade and let's compete!
#AstraTrade #Challenge #TradingSkills
''';
  }

  /// Get emoji for achievement rarity
  String _getRarityEmoji(AchievementRarity rarity) {
    switch (rarity) {
      case AchievementRarity.common:
        return '🥉';
      case AchievementRarity.uncommon:
        return '🥈';
      case AchievementRarity.rare:
        return '🥇';
      case AchievementRarity.epic:
        return '💎';
      case AchievementRarity.legendary:
        return '👑';
    }
  }

  /// Get contextual message for achievement type
  String _getAchievementTypeMessage(AchievementType type) {
    switch (type) {
      case AchievementType.firstTrade:
        return 'First step into the world of trading!';
      case AchievementType.tradeCount:
        return 'Experience comes with practice!';
      case AchievementType.profitTarget:
        return 'Consistency in trading pays off!';
      case AchievementType.streakMilestone:
        return 'Daily practice makes perfect!';
      case AchievementType.levelMilestone:
        return 'Growing stronger as a trader!';
      case AchievementType.practiceMilestone:
        return 'Practice makes perfect!';
      case AchievementType.realTrading:
        return 'Real trading experience!';
      case AchievementType.specialEvent:
        return 'Special event achievement!';
    }
  }

  /// Get current social sharing settings
  Map<String, dynamic> getSettings() {
    return {
      'enabled': true,
      'achievements_sharing': true,
      'level_sharing': true,
      'streak_sharing': true,
      'challenge_creation': true,
      'leaderboard_sharing': true,
    };
  }

  /// Set social sharing preferences
  Future<void> setSettings(Map<String, dynamic> settings) async {
    // Implementation would store preferences
    // For now, just provide haptic feedback
    await _hapticService.lightTap();
  }
}
