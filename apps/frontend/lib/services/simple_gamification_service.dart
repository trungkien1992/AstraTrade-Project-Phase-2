import 'dart:developer';
import 'dart:convert';
import 'dart:math' as math;
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/simple_gamification.dart';
import '../models/user.dart';

/// Simple Gamification Service - Basic XP, levels, achievements
/// No cosmic themes - straightforward progression system
class SimpleGamificationService {
  static const String _storageKey = 'player_progress';
  static const String _achievementsKey = 'player_achievements';
  static const String _eventsKey = 'xp_events';
  
  PlayerProgress? _currentProgress;
  final List<Achievement> _allAchievements = [];
  final List<XPGainEvent> _recentEvents = [];
  
  /// Get current player progress
  PlayerProgress? get currentProgress => _currentProgress;
  
  /// Get all available achievements
  List<Achievement> get allAchievements => List.unmodifiable(_allAchievements);
  
  /// Get recent XP events
  List<XPGainEvent> get recentEvents => List.unmodifiable(_recentEvents);

  /// Initialize gamification system for player
  Future<PlayerProgress> initializePlayer(String playerId) async {
    try {
      // Try to load existing progress
      final existingProgress = await _loadPlayerProgress(playerId);
      if (existingProgress != null) {
        _currentProgress = existingProgress;
        await _loadRecentEvents();
        return existingProgress;
      }
      
      // Create new player progress
      final newProgress = PlayerProgress.newPlayer(playerId);
      _currentProgress = newProgress;
      
      await _savePlayerProgress(newProgress);
      await _initializeAchievements();
      
      debugPrint('🎮 Initialized simple gamification for player: $playerId');
      return newProgress;
      
    } catch (e) {
      log('Error initializing gamification: $e');
      throw GamificationException('Failed to initialize gamification system');
    }
  }

  /// Award XP from practice trading
  Future<XPGainEvent> awardPracticeTradeXP({
    required String playerId,
    required bool isProfitable,
    required double amount,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      final baseXP = 10;
      final profitBonus = isProfitable ? 15 : 0;
      final amountBonus = (amount / 10).round().clamp(0, 50);
      final totalXP = baseXP + profitBonus + amountBonus;
      
      final event = XPGainEvent(
        eventId: 'practice_${DateTime.now().millisecondsSinceEpoch}',
        playerId: playerId,
        source: XPGainSource.practiceTrade,
        xpGained: totalXP,
        tradingPointsGained: 0,
        practicePointsGained: 5 + (isProfitable ? 5 : 0),
        description: isProfitable ? 'Profitable Practice Trade! 📈' : 'Practice Trade Complete 📊',
        timestamp: DateTime.now(),
        metadata: {
          'trade_amount': amount,
          'profitable': isProfitable,
          'trading_mode': 'practice',
          ...?metadata,
        },
      );
      
      await _applyXPGain(event);
      await _checkAchievements();
      
      debugPrint('🎯 Practice trade XP awarded: ${totalXP}XP');
      return event;
      
    } catch (e) {
      log('Error awarding practice XP: $e');
      throw GamificationException('Failed to award practice XP');
    }
  }

  /// Award XP from real trading
  Future<XPGainEvent> awardRealTradeXP({
    required String playerId,
    required bool isProfitable,
    required double amount,
    required double profit,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      final baseXP = 50; // Real trades worth more
      final profitBonus = isProfitable ? 100 : 0;
      final amountBonus = (amount / 5).round().clamp(0, 200);
      final profitBonus2 = (profit.abs() * 10).round().clamp(0, 500);
      final totalXP = baseXP + profitBonus + amountBonus + profitBonus2;
      
      final event = XPGainEvent(
        eventId: 'real_${DateTime.now().millisecondsSinceEpoch}',
        playerId: playerId,
        source: isProfitable ? XPGainSource.profitableTrade : XPGainSource.realTrade,
        xpGained: totalXP,
        tradingPointsGained: 25 + (isProfitable ? 75 : 0),
        practicePointsGained: 0,
        description: isProfitable ? 'Profitable Real Trade! 🚀' : 'Real Trade Complete 💼',
        timestamp: DateTime.now(),
        metadata: {
          'trade_amount': amount,
          'profit': profit,
          'profitable': isProfitable,
          'trading_mode': 'real',
          ...?metadata,
        },
      );
      
      await _applyXPGain(event);
      await _checkAchievements();
      
      debugPrint('💰 Real trade XP awarded: ${totalXP}XP, ${event.tradingPointsGained}TP');
      return event;
      
    } catch (e) {
      log('Error awarding real trade XP: $e');
      throw GamificationException('Failed to award real trade XP');
    }
  }

  /// Award daily login bonus
  Future<XPGainEvent?> awardDailyLogin(String playerId) async {
    try {
      if (_currentProgress == null) return null;
      
      final now = DateTime.now();
      final today = DateTime(now.year, now.month, now.day);
      final lastActive = DateTime(
        _currentProgress!.lastActiveDate.year,
        _currentProgress!.lastActiveDate.month,
        _currentProgress!.lastActiveDate.day,
      );
      
      // Check if already claimed today
      if (lastActive.isAtSameMomentAs(today)) {
        return null; // Already claimed today
      }
      
      // Calculate new streak
      final yesterday = today.subtract(const Duration(days: 1));
      final newStreak = lastActive.isAtSameMomentAs(yesterday) 
          ? _currentProgress!.streakDays + 1 
          : 1; // Reset if gap
      
      final dailyReward = DailyReward.calculateReward(newStreak);
      
      final event = XPGainEvent(
        eventId: 'daily_${DateTime.now().millisecondsSinceEpoch}',
        playerId: playerId,
        source: newStreak > 1 ? XPGainSource.streakBonus : XPGainSource.dailyLogin,
        xpGained: dailyReward.xpReward,
        tradingPointsGained: dailyReward.tradingPointsReward,
        practicePointsGained: 0,
        description: dailyReward.description,
        timestamp: DateTime.now(),
        metadata: {
          'streak_day': newStreak,
          'is_milestone': dailyReward.isMilestone,
          'bonus_rewards': dailyReward.bonusRewards,
        },
      );
      
      // Update streak and last active date
      _currentProgress = _currentProgress!.copyWith(
        streakDays: newStreak,
        lastActiveDate: now,
        stats: {
          ..._currentProgress!.stats,
          'days_active': _currentProgress!.stats['days_active']! + 1,
          'best_streak': math.max(_currentProgress!.stats['best_streak']!, newStreak),
        },
      );
      
      await _applyXPGain(event);
      await _checkAchievements();
      
      debugPrint('📅 Daily login bonus: ${dailyReward.xpReward}XP (streak: $newStreak)');
      return event;
      
    } catch (e) {
      log('Error awarding daily login: $e');
      return null;
    }
  }

  /// Check and award achievements
  Future<List<Achievement>> _checkAchievements() async {
    try {
      if (_currentProgress == null) return [];
      
      final newAchievements = <Achievement>[];
      final stats = _currentProgress!.stats;
      
      for (final achievement in _allAchievements) {
        // Skip if already earned
        if (_currentProgress!.achievements.contains(achievement.id)) continue;
        
        bool earned = false;
        
        switch (achievement.type) {
          case AchievementType.firstTrade:
            earned = stats['total_trades']! >= 1;
            break;
          case AchievementType.tradeCount:
            earned = stats['total_trades']! >= achievement.targetValue;
            break;
          case AchievementType.profitTarget:
            earned = stats['total_profit']! >= achievement.targetValue;
            break;
          case AchievementType.streakMilestone:
            earned = _currentProgress!.streakDays >= achievement.targetValue;
            break;
          case AchievementType.levelMilestone:
            earned = _currentProgress!.level >= achievement.targetValue;
            break;
          case AchievementType.practiceMilestone:
            earned = stats['practice_trades']! >= achievement.targetValue;
            break;
          case AchievementType.realTrading:
            earned = stats['real_trades']! >= achievement.targetValue;
            break;
          case AchievementType.specialEvent:
            // Handle special events separately
            break;
        }
        
        if (earned) {
          newAchievements.add(achievement);
          await _awardAchievement(achievement);
        }
      }
      
      return newAchievements;
      
    } catch (e) {
      log('Error checking achievements: $e');
      return [];
    }
  }

  /// Award achievement to player
  Future<void> _awardAchievement(Achievement achievement) async {
    try {
      if (_currentProgress == null) return;
      
      // Add achievement to player's list
      final updatedAchievements = [..._currentProgress!.achievements, achievement.id];
      
      // Award XP and TP
      final achievementEvent = XPGainEvent(
        eventId: 'achievement_${DateTime.now().millisecondsSinceEpoch}',
        playerId: _currentProgress!.playerId,
        source: XPGainSource.achievement,
        xpGained: achievement.xpReward,
        tradingPointsGained: achievement.tradingPointsReward,
        practicePointsGained: 0,
        description: 'Achievement Unlocked: ${achievement.name} 🏆',
        timestamp: DateTime.now(),
        metadata: {
          'achievement_id': achievement.id,
          'achievement_name': achievement.name,
          'rarity': achievement.rarity.name,
        },
      );
      
      _currentProgress = _currentProgress!.copyWith(achievements: updatedAchievements);
      await _applyXPGain(achievementEvent);
      
      debugPrint('🏆 Achievement unlocked: ${achievement.name} (+${achievement.xpReward}XP)');
      
    } catch (e) {
      log('Error awarding achievement: $e');
    }
  }

  /// Apply XP gain and handle level ups
  Future<void> _applyXPGain(XPGainEvent event) async {
    try {
      if (_currentProgress == null) return;
      
      final oldLevel = _currentProgress!.level;
      final newXP = _currentProgress!.xp + event.xpGained;
      final newTP = _currentProgress!.tradingPoints + event.tradingPointsGained;
      final newPP = _currentProgress!.practicePoints + event.practicePointsGained;
      
      // Calculate new level
      int newLevel = oldLevel;
      while (newXP >= PlayerProgress.xpRequiredForLevel(newLevel + 1)) {
        newLevel++;
      }
      
      // Update stats based on event type
      final updatedStats = Map<String, int>.from(_currentProgress!.stats);
      switch (event.source) {
        case XPGainSource.practiceTrade:
          updatedStats['practice_trades'] = updatedStats['practice_trades']! + 1;
          updatedStats['total_trades'] = updatedStats['total_trades']! + 1;
          if (event.metadata['profitable'] == true) {
            updatedStats['profitable_trades'] = updatedStats['profitable_trades']! + 1;
          }
          break;
        case XPGainSource.realTrade:
        case XPGainSource.profitableTrade:
          updatedStats['real_trades'] = updatedStats['real_trades']! + 1;
          updatedStats['total_trades'] = updatedStats['total_trades']! + 1;
          if (event.metadata['profitable'] == true) {
            updatedStats['profitable_trades'] = updatedStats['profitable_trades']! + 1;
            final profit = (event.metadata['profit'] as double? ?? 0.0).round();
            updatedStats['total_profit'] = updatedStats['total_profit']! + profit;
          }
          break;
        default:
          break;
      }
      
      _currentProgress = _currentProgress!.copyWith(
        xp: newXP,
        level: newLevel,
        tradingPoints: newTP,
        practicePoints: newPP,
        stats: updatedStats,
      );
      
      // Add event to recent events
      _recentEvents.insert(0, event);
      if (_recentEvents.length > 50) {
        _recentEvents.removeRange(50, _recentEvents.length);
      }
      
      await _savePlayerProgress(_currentProgress!);
      await _saveRecentEvents();
      
      // Handle level up
      if (newLevel > oldLevel) {
        await _handleLevelUp(oldLevel, newLevel);
      }
      
    } catch (e) {
      log('Error applying XP gain: $e');
    }
  }

  /// Handle level up rewards and notifications
  Future<void> _handleLevelUp(int oldLevel, int newLevel) async {
    try {
      for (int level = oldLevel + 1; level <= newLevel; level++) {
        final levelUpEvent = XPGainEvent(
          eventId: 'levelup_${DateTime.now().millisecondsSinceEpoch}_$level',
          playerId: _currentProgress!.playerId,
          source: XPGainSource.levelUp,
          xpGained: 0,
          tradingPointsGained: level * 10, // TP reward for leveling up
          practicePointsGained: 0,
          description: 'Level Up! Welcome to Level $level 🎉',
          timestamp: DateTime.now(),
          metadata: {
            'old_level': oldLevel,
            'new_level': level,
            'tp_reward': level * 10,
          },
        );
        
        _recentEvents.insert(0, levelUpEvent);
        
        debugPrint('⬆️ Level up! $oldLevel → $level (+${level * 10}TP)');
      }
      
      await _saveRecentEvents();
      
    } catch (e) {
      log('Error handling level up: $e');
    }
  }

  /// Get player's achievement progress
  Map<String, double> getAchievementProgress() {
    if (_currentProgress == null) return {};
    
    final progress = <String, double>{};
    final stats = _currentProgress!.stats;
    
    for (final achievement in _allAchievements) {
      if (_currentProgress!.achievements.contains(achievement.id)) {
        progress[achievement.id] = 1.0; // Completed
        continue;
      }
      
      double currentProgress = 0.0;
      
      switch (achievement.type) {
        case AchievementType.firstTrade:
        case AchievementType.tradeCount:
          currentProgress = (stats['total_trades']! / achievement.targetValue).clamp(0.0, 1.0);
          break;
        case AchievementType.profitTarget:
          currentProgress = (stats['total_profit']! / achievement.targetValue).clamp(0.0, 1.0);
          break;
        case AchievementType.streakMilestone:
          currentProgress = (_currentProgress!.streakDays / achievement.targetValue).clamp(0.0, 1.0);
          break;
        case AchievementType.levelMilestone:
          currentProgress = (_currentProgress!.level / achievement.targetValue).clamp(0.0, 1.0);
          break;
        case AchievementType.practiceMilestone:
          currentProgress = (stats['practice_trades']! / achievement.targetValue).clamp(0.0, 1.0);
          break;
        case AchievementType.realTrading:
          currentProgress = (stats['real_trades']! / achievement.targetValue).clamp(0.0, 1.0);
          break;
        case AchievementType.specialEvent:
          currentProgress = 0.0;
          break;
      }
      
      progress[achievement.id] = currentProgress;
    }
    
    return progress;
  }

  /// Load player progress from storage
  Future<PlayerProgress?> _loadPlayerProgress(String playerId) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final data = prefs.getString('${_storageKey}_$playerId');
      if (data == null) return null;
      
      final json = jsonDecode(data) as Map<String, dynamic>;
      return PlayerProgress.fromJson(json);
      
    } catch (e) {
      log('Error loading player progress: $e');
      return null;
    }
  }

  /// Save player progress to storage
  Future<void> _savePlayerProgress(PlayerProgress progress) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final data = jsonEncode(progress.toJson());
      await prefs.setString('${_storageKey}_${progress.playerId}', data);
      
    } catch (e) {
      log('Error saving player progress: $e');
    }
  }

  /// Load recent events from storage
  Future<void> _loadRecentEvents() async {
    try {
      if (_currentProgress == null) return;
      
      final prefs = await SharedPreferences.getInstance();
      final data = prefs.getString('${_eventsKey}_${_currentProgress!.playerId}');
      if (data == null) return;
      
      final jsonList = jsonDecode(data) as List<dynamic>;
      _recentEvents.clear();
      _recentEvents.addAll(
        jsonList.map((json) => XPGainEvent.fromJson(json as Map<String, dynamic>))
      );
      
    } catch (e) {
      log('Error loading recent events: $e');
    }
  }

  /// Save recent events to storage
  Future<void> _saveRecentEvents() async {
    try {
      if (_currentProgress == null) return;
      
      final prefs = await SharedPreferences.getInstance();
      final data = jsonEncode(_recentEvents.map((e) => e.toJson()).toList());
      await prefs.setString('${_eventsKey}_${_currentProgress!.playerId}', data);
      
    } catch (e) {
      log('Error saving recent events: $e');
    }
  }

  /// Initialize default achievements
  Future<void> _initializeAchievements() async {
    _allAchievements.clear();
    _allAchievements.addAll([
      // Trading Achievements
      Achievement(
        id: 'first_trade',
        name: 'First Trade',
        description: 'Complete your first trade',
        type: AchievementType.firstTrade,
        targetValue: 1,
        xpReward: 50,
        tradingPointsReward: 25,
        iconName: 'first_trade',
        rarity: AchievementRarity.common,
        requirements: [],
      ),
      Achievement(
        id: 'trade_10',
        name: 'Getting Started',
        description: 'Complete 10 trades',
        type: AchievementType.tradeCount,
        targetValue: 10,
        xpReward: 100,
        tradingPointsReward: 50,
        iconName: 'trade_10',
        rarity: AchievementRarity.common,
        requirements: [],
      ),
      Achievement(
        id: 'trade_100',
        name: 'Experienced Trader',
        description: 'Complete 100 trades',
        type: AchievementType.tradeCount,
        targetValue: 100,
        xpReward: 500,
        tradingPointsReward: 250,
        iconName: 'trade_100',
        rarity: AchievementRarity.uncommon,
        requirements: [],
      ),
      Achievement(
        id: 'trade_1000',
        name: 'Master Trader',
        description: 'Complete 1000 trades',
        type: AchievementType.tradeCount,
        targetValue: 1000,
        xpReward: 2000,
        tradingPointsReward: 1000,
        iconName: 'trade_1000',
        rarity: AchievementRarity.rare,
        requirements: [],
      ),
      
      // Level Achievements
      Achievement(
        id: 'level_10',
        name: 'Rising Star',
        description: 'Reach level 10',
        type: AchievementType.levelMilestone,
        targetValue: 10,
        xpReward: 200,
        tradingPointsReward: 100,
        iconName: 'level_10',
        rarity: AchievementRarity.common,
        requirements: [],
      ),
      Achievement(
        id: 'level_25',
        name: 'Skilled Trader',
        description: 'Reach level 25',
        type: AchievementType.levelMilestone,
        targetValue: 25,
        xpReward: 750,
        tradingPointsReward: 375,
        iconName: 'level_25',
        rarity: AchievementRarity.uncommon,
        requirements: [],
      ),
      Achievement(
        id: 'level_50',
        name: 'Expert Trader',
        description: 'Reach level 50',
        type: AchievementType.levelMilestone,
        targetValue: 50,
        xpReward: 2500,
        tradingPointsReward: 1250,
        iconName: 'level_50',
        rarity: AchievementRarity.epic,
        requirements: [],
      ),
      
      // Streak Achievements
      Achievement(
        id: 'streak_7',
        name: 'Weekly Warrior',
        description: 'Login for 7 consecutive days',
        type: AchievementType.streakMilestone,
        targetValue: 7,
        xpReward: 300,
        tradingPointsReward: 150,
        iconName: 'streak_7',
        rarity: AchievementRarity.common,
        requirements: [],
      ),
      Achievement(
        id: 'streak_30',
        name: 'Monthly Master',
        description: 'Login for 30 consecutive days',
        type: AchievementType.streakMilestone,
        targetValue: 30,
        xpReward: 1500,
        tradingPointsReward: 750,
        iconName: 'streak_30',
        rarity: AchievementRarity.rare,
        requirements: [],
      ),
      Achievement(
        id: 'streak_100',
        name: 'Dedication Legend',
        description: 'Login for 100 consecutive days',
        type: AchievementType.streakMilestone,
        targetValue: 100,
        xpReward: 5000,
        tradingPointsReward: 2500,
        iconName: 'streak_100',
        rarity: AchievementRarity.legendary,
        requirements: [],
      ),
      
      // Practice Achievements
      Achievement(
        id: 'practice_50',
        name: 'Practice Makes Perfect',
        description: 'Complete 50 practice trades',
        type: AchievementType.practiceMilestone,
        targetValue: 50,
        xpReward: 250,
        tradingPointsReward: 125,
        iconName: 'practice_50',
        rarity: AchievementRarity.common,
        requirements: [],
      ),
      
      // Real Trading Achievements
      Achievement(
        id: 'real_trade_1',
        name: 'Real Deal',
        description: 'Complete your first real trade',
        type: AchievementType.realTrading,
        targetValue: 1,
        xpReward: 500,
        tradingPointsReward: 250,
        iconName: 'real_trade_1',
        rarity: AchievementRarity.uncommon,
        requirements: [],
      ),
      Achievement(
        id: 'real_trade_10',
        name: 'Real Trader',
        description: 'Complete 10 real trades',
        type: AchievementType.realTrading,
        targetValue: 10,
        xpReward: 1000,
        tradingPointsReward: 500,
        iconName: 'real_trade_10',
        rarity: AchievementRarity.rare,
        requirements: [],
      ),
      
      // Profit Achievements
      Achievement(
        id: 'profit_100',
        name: 'First Profit',
        description: 'Earn \$100 total profit',
        type: AchievementType.profitTarget,
        targetValue: 100,
        xpReward: 750,
        tradingPointsReward: 375,
        iconName: 'profit_100',
        rarity: AchievementRarity.uncommon,
        requirements: [],
      ),
      Achievement(
        id: 'profit_1000',
        name: 'Profit Master',
        description: 'Earn \$1000 total profit',
        type: AchievementType.profitTarget,
        targetValue: 1000,
        xpReward: 3000,
        tradingPointsReward: 1500,
        iconName: 'profit_1000',
        rarity: AchievementRarity.epic,
        requirements: [],
      ),
    ]);
  }
}

/// Exception for gamification operations
class GamificationException implements Exception {
  final String message;
  
  GamificationException(this.message);
  
  @override
  String toString() => 'GamificationException: $message';
}