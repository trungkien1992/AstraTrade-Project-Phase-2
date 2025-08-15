import 'package:flutter/foundation.dart';
import '../models/simple_gamification.dart';
import '../services/simple_gamification_service.dart';

/// Provider for simple gamification system
/// Manages XP, levels, achievements without cosmic themes
class SimpleGamificationProvider extends ChangeNotifier {
  final SimpleGamificationService _service = SimpleGamificationService();

  PlayerProgress? _currentProgress;
  List<Achievement> _achievements = [];
  List<XPGainEvent> _recentEvents = [];
  bool _isLoading = false;
  String? _error;

  // Getters
  PlayerProgress? get currentProgress => _currentProgress;
  List<Achievement> get achievements => _achievements;
  List<XPGainEvent> get recentEvents => _recentEvents;
  bool get isLoading => _isLoading;
  String? get error => _error;

  /// Get achievements earned by player
  List<Achievement> get earnedAchievements {
    if (_currentProgress == null) return [];
    return _achievements
        .where((a) => _currentProgress!.achievements.contains(a.id))
        .toList();
  }

  /// Get achievements available to earn
  List<Achievement> get availableAchievements {
    if (_currentProgress == null) return [];
    return _achievements
        .where((a) => !_currentProgress!.achievements.contains(a.id))
        .toList();
  }

  /// Get achievement progress map
  Map<String, double> get achievementProgress {
    return _service.getAchievementProgress();
  }

  /// Initialize gamification for player
  Future<void> initializePlayer(String playerId) async {
    try {
      _setLoading(true);
      _error = null;

      _currentProgress = await _service.initializePlayer(playerId);
      _achievements = _service.allAchievements;
      _recentEvents = _service.recentEvents;

      // Award daily login bonus if applicable
      final dailyBonus = await _service.awardDailyLogin(playerId);
      if (dailyBonus != null) {
        _recentEvents = _service.recentEvents;
        _currentProgress = _service.currentProgress;
      }

      debugPrint('🎮 Gamification provider initialized for $playerId');
    } catch (e) {
      _error = 'Failed to initialize gamification: $e';
      debugPrint('❌ Gamification initialization error: $e');
    } finally {
      _setLoading(false);
    }
  }

  /// Award XP for practice trade
  Future<void> awardPracticeTradeXP({
    required String playerId,
    required bool isProfitable,
    required double amount,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      final event = await _service.awardPracticeTradeXP(
        playerId: playerId,
        isProfitable: isProfitable,
        amount: amount,
        metadata: metadata,
      );

      _currentProgress = _service.currentProgress;
      _recentEvents = _service.recentEvents;

      notifyListeners();
      debugPrint('🎯 Practice XP awarded: ${event.xpGained}XP');
    } catch (e) {
      _error = 'Failed to award practice XP: $e';
      debugPrint('❌ Practice XP error: $e');
      notifyListeners();
    }
  }

  /// Award XP for real trade
  Future<void> awardRealTradeXP({
    required String playerId,
    required bool isProfitable,
    required double amount,
    required double profit,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      final event = await _service.awardRealTradeXP(
        playerId: playerId,
        isProfitable: isProfitable,
        amount: amount,
        profit: profit,
        metadata: metadata,
      );

      _currentProgress = _service.currentProgress;
      _recentEvents = _service.recentEvents;

      notifyListeners();
      debugPrint('💰 Real trade XP awarded: ${event.xpGained}XP');
    } catch (e) {
      _error = 'Failed to award real trade XP: $e';
      debugPrint('❌ Real trade XP error: $e');
      notifyListeners();
    }
  }

  /// Award daily login bonus
  Future<bool> awardDailyLoginBonus(String playerId) async {
    try {
      final event = await _service.awardDailyLogin(playerId);

      if (event != null) {
        _currentProgress = _service.currentProgress;
        _recentEvents = _service.recentEvents;
        notifyListeners();

        debugPrint('📅 Daily bonus awarded: ${event.xpGained}XP');
        return true;
      }

      return false; // Already claimed today
    } catch (e) {
      _error = 'Failed to award daily bonus: $e';
      debugPrint('❌ Daily bonus error: $e');
      notifyListeners();
      return false;
    }
  }

  /// Get rank display info
  Map<String, dynamic> getRankInfo() {
    if (_currentProgress == null) {
      return {
        'rank': 'Beginner Trader',
        'level': 1,
        'progress': 0.0,
        'xp_to_next': 100,
      };
    }

    return {
      'rank': _currentProgress!.rank,
      'level': _currentProgress!.level,
      'progress': _currentProgress!.levelProgress,
      'xp_to_next': _currentProgress!.xpToNextLevel,
      'total_xp': _currentProgress!.totalXP,
    };
  }

  /// Get trading stats summary
  Map<String, dynamic> getTradingStats() {
    if (_currentProgress == null) {
      return {
        'total_trades': 0,
        'practice_trades': 0,
        'real_trades': 0,
        'profitable_trades': 0,
        'total_profit': 0,
        'success_rate': 0.0,
        'streak_days': 0,
        'best_streak': 0,
      };
    }

    final stats = _currentProgress!.stats;
    final totalTrades = stats['total_trades']!;
    final profitableTrades = stats['profitable_trades']!;
    final successRate = totalTrades > 0
        ? (profitableTrades / totalTrades)
        : 0.0;

    return {
      'total_trades': totalTrades,
      'practice_trades': stats['practice_trades']!,
      'real_trades': stats['real_trades']!,
      'profitable_trades': profitableTrades,
      'total_profit': stats['total_profit']!,
      'success_rate': successRate,
      'streak_days': _currentProgress!.streakDays,
      'best_streak': stats['best_streak']!,
      'trading_points': _currentProgress!.tradingPoints,
      'practice_points': _currentProgress!.practicePoints,
    };
  }

  /// Get recent achievements (last 5)
  List<Achievement> getRecentAchievements() {
    return _recentEvents
        .where((e) => e.source == XPGainSource.achievement)
        .take(5)
        .map((e) {
          final achievementId = e.metadata['achievement_id'] as String;
          return _achievements.firstWhere((a) => a.id == achievementId);
        })
        .toList();
  }

  /// Get achievements close to completion (>75% progress)
  List<Achievement> getAlmostCompleteAchievements() {
    final progress = achievementProgress;
    return availableAchievements
        .where((a) => (progress[a.id] ?? 0.0) > 0.75)
        .toList();
  }

  /// Set loading state
  void _setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }

  /// Clear error
  void clearError() {
    _error = null;
    notifyListeners();
  }

  /// Refresh data
  Future<void> refresh() async {
    if (_currentProgress != null) {
      await initializePlayer(_currentProgress!.playerId);
    }
  }
}
