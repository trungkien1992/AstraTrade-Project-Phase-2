import 'package:flutter_test/flutter_test.dart';
import 'lib/services/simple_gamification_service.dart';
import 'lib/services/gamification_integration.dart';
import 'lib/models/simple_gamification.dart';
import 'lib/models/simple_trade.dart';

/// Test for simple gamification system
/// Validates XP, achievements, and progression
void main() {
  group('Simple Gamification System Tests', () {
    
    test('Gamification Service Creation', () {
      final service = SimpleGamificationService();
      expect(service, isNotNull);
    });
    
    test('Player Progress Model', () {
      final testDate = DateTime.parse('2025-01-01T00:00:00.000Z');
      final progress = PlayerProgress(
        playerId: 'test_player',
        xp: 150,
        level: 2,
        tradingPoints: 50,
        practicePoints: 25,
        streakDays: 3,
        lastActiveDate: testDate,
        createdAt: testDate,
        achievements: ['first_trade'],
        stats: {
          'total_trades': 5,
          'practice_trades': 3,
          'real_trades': 2,
          'profitable_trades': 3,
          'total_profit': 150,
          'best_streak': 3,
          'days_active': 3,
        },
      );
      
      expect(progress.playerId, 'test_player');
      expect(progress.xp, 150);
      expect(progress.level, 2);
      expect(progress.rank, 'Beginner Trader');
      expect(progress.streakMultiplier, 1.15); // 1.0 + (3 * 0.05)
    });
    
    test('XP Level Calculations', () {
      // Test XP requirements for levels
      expect(PlayerProgress.xpRequiredForLevel(1), 100);
      expect(PlayerProgress.xpRequiredForLevel(2), 400);
      expect(PlayerProgress.xpRequiredForLevel(3), 900);
      expect(PlayerProgress.xpRequiredForLevel(5), 2500);
    });
    
    test('Achievement Types Available', () {
      expect(AchievementType.values, hasLength(8));
      expect(AchievementType.firstTrade, isNotNull);
      expect(AchievementType.tradeCount, isNotNull);
      expect(AchievementType.profitTarget, isNotNull);
      expect(AchievementType.streakMilestone, isNotNull);
      expect(AchievementType.levelMilestone, isNotNull);
      expect(AchievementType.practiceMilestone, isNotNull);
      expect(AchievementType.realTrading, isNotNull);
      expect(AchievementType.specialEvent, isNotNull);
    });
    
    test('Achievement Rarity Levels', () {
      expect(AchievementRarity.values, hasLength(5));
      expect(AchievementRarity.common, isNotNull);
      expect(AchievementRarity.uncommon, isNotNull);
      expect(AchievementRarity.rare, isNotNull);
      expect(AchievementRarity.epic, isNotNull);
      expect(AchievementRarity.legendary, isNotNull);
    });
    
    test('XP Gain Sources', () {
      expect(XPGainSource.values, hasLength(8));
      expect(XPGainSource.practiceTrade, isNotNull);
      expect(XPGainSource.realTrade, isNotNull);
      expect(XPGainSource.profitableTrade, isNotNull);
      expect(XPGainSource.dailyLogin, isNotNull);
      expect(XPGainSource.streakBonus, isNotNull);
      expect(XPGainSource.levelUp, isNotNull);
      expect(XPGainSource.achievement, isNotNull);
      expect(XPGainSource.firstTimeBonus, isNotNull);
    });
    
    test('Daily Reward Calculation', () {
      // Test basic daily reward
      final basicReward = DailyReward.calculateReward(3);
      expect(basicReward.streakDay, 3);
      expect(basicReward.xpReward, 40); // 25 + (3 * 5)
      expect(basicReward.tradingPointsReward, 16); // 10 + (3 * 2)
      expect(basicReward.isMilestone, false);
      
      // Test milestone reward (7 days)
      final milestoneReward = DailyReward.calculateReward(7);
      expect(milestoneReward.streakDay, 7);
      expect(milestoneReward.xpReward, 120); // (25 + 35) * 2
      expect(milestoneReward.tradingPointsReward, 48); // (10 + 14) * 2
      expect(milestoneReward.isMilestone, true);
      expect(milestoneReward.description, 'Milestone Achieved! 🏆');
    });
    
    test('Player Progress Level Calculations', () {
      final progress = PlayerProgress(
        playerId: 'test',
        xp: 450, // Between level 2 (400 XP) and level 3 (900 XP)
        level: 2,
        tradingPoints: 0,
        practicePoints: 0,
        streakDays: 0,
        lastActiveDate: DateTime.now(),
        createdAt: DateTime.now(),
        achievements: [],
        stats: {},
      );
      
      expect(progress.canLevelUp, false); // 450 < 900
      expect(progress.xpToNextLevel, 450); // 900 - 450
      expect(progress.levelProgress, 0.1); // (450-400)/(900-400) = 50/500 = 0.1
    });
    
    test('Rank Progression', () {
      final ranks = [
        (1, 'Beginner Trader'),
        (5, 'Novice Trader'),
        (10, 'Experienced Trader'),
        (20, 'Intermediate Trader'),
        (30, 'Advanced Trader'),
        (50, 'Expert Trader'),
      ];
      
      for (final (level, expectedRank) in ranks) {
        final progress = PlayerProgress(
          playerId: 'test',
          xp: 0,
          level: level,
          tradingPoints: 0,
          practicePoints: 0,
          streakDays: 0,
          lastActiveDate: DateTime.now(),
          createdAt: DateTime.now(),
          achievements: [],
          stats: {},
        );
        
        expect(progress.rank, expectedRank);
      }
    });
    
    test('Gamification Integration Helper', () {
      // Test that the integration helper exists and has required methods
      expect(GamificationIntegration.service, isNotNull);
      expect(GamificationIntegration.awardTradeXP, isNotNull);
      expect(GamificationIntegration.awardDailyLoginBonus, isNotNull);
      expect(GamificationIntegration.initializeNewPlayer, isNotNull);
    });
    
    test('Service Dependencies and Imports', () {
      // This test passes if the file compiles without import errors
      expect(true, true);
    });
    
  });
  
  group('Gamification Integration Compliance', () {
    
    test('Simple, non-cosmic theme approach', () {
      // ✅ Simple gamification without cosmic themes
      final testDate = DateTime.parse('2025-01-01T00:00:00.000Z');
      final progress = PlayerProgress(
        playerId: 'test',
        xp: 100,
        level: 1,
        tradingPoints: 25,
        practicePoints: 15,
        streakDays: 1,
        lastActiveDate: testDate,
        createdAt: testDate,
        achievements: [],
        stats: {},
      );
      
      expect(progress.rank.contains('Trader'), true);
      expect(progress.rank.contains('Cosmic'), false);
      expect(progress.rank.contains('Stellar'), false);
    });
    
    test('Basic XP and level system', () {
      // ✅ Basic XP progression system
      final newPlayer = PlayerProgress.newPlayer('test');
      expect(newPlayer.xp, 0);
      expect(newPlayer.level, 1);
      expect(newPlayer.tradingPoints, 0);
      expect(newPlayer.practicePoints, 0);
    });
    
    test('Achievement system available', () {
      // ✅ Achievement system for milestones
      const achievement = Achievement(
        id: 'test',
        name: 'Test Achievement',
        description: 'Test description',
        type: AchievementType.firstTrade,
        targetValue: 1,
        xpReward: 50,
        tradingPointsReward: 25,
        iconName: 'test',
        rarity: AchievementRarity.common,
        requirements: [],
      );
      
      expect(achievement.name, 'Test Achievement');
      expect(achievement.xpReward, 50);
      expect(achievement.rarity, AchievementRarity.common);
    });
    
    test('Daily streak system', () {
      // ✅ Daily login and streak rewards
      final testDate = DateTime.parse('2025-01-01T00:00:00.000Z');
      final progress = PlayerProgress(
        playerId: 'test',
        xp: 0,
        level: 1,
        tradingPoints: 0,
        practicePoints: 0,
        streakDays: 5,
        lastActiveDate: testDate,
        createdAt: testDate,
        achievements: [],
        stats: {},
      );
      
      expect(progress.streakDays, 5);
      expect(progress.streakMultiplier, 1.25); // 1.0 + (5 * 0.05)
    });
    
    test('Trading integration hooks', () {
      // ✅ Integration with trading system for XP rewards
      expect(GamificationIntegration.awardTradeXP, isNotNull);
      expect(GamificationIntegration.awardDailyLoginBonus, isNotNull);
    });
    
  });
}