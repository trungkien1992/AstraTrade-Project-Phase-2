import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/xp_system.dart';
import '../services/xp_service.dart';
import '../services/trading_stats_service.dart';
import 'leaderboard_provider.dart';

/// Provider for XP Service instance
final xpServiceProvider = Provider<XPService>((ref) {
  return XPService();
});

/// Provider for Trading Stats Service instance
final tradingStatsServiceProvider = Provider<TradingStatsService>((ref) {
  return TradingStatsService();
});

/// Provider for current player XP data
final playerXPProvider =
    StateNotifierProvider<PlayerXPNotifier, AsyncValue<PlayerXP?>>((ref) {
      final xpService = ref.watch(xpServiceProvider);
      return PlayerXPNotifier(xpService, ref);
    });

/// Provider for recent XP events
final recentXPEventsProvider = Provider<List<XPGainEvent>>((ref) {
  final xpService = ref.watch(xpServiceProvider);
  return xpService.getRecentEvents();
});

/// Provider for idle generation rate
final idleGenerationRateProvider = Provider<double>((ref) {
  final xpService = ref.watch(xpServiceProvider);
  return xpService.calculateIdleGeneration();
});

/// State notifier for player XP management
class PlayerXPNotifier extends StateNotifier<AsyncValue<PlayerXP?>> {
  final XPService _xpService;
  final Ref _ref;
  late final TradingStatsService _tradingStatsService;

  PlayerXPNotifier(this._xpService, this._ref)
    : super(const AsyncValue.loading()) {
    _tradingStatsService = _ref.read(tradingStatsServiceProvider);
  }

  /// Update leaderboard when XP changes
  void _updateLeaderboard(String playerId, PlayerXP playerXP) async {
    try {
      // Check if leaderboard provider is available
      final leaderboardNotifier = _ref.read(leaderboardProvider.notifier);

      // Get current trading statistics
      final tradingStats = await _tradingStatsService.getCurrentStats();

      // Update leaderboard with new stats
      leaderboardNotifier.updateCurrentUserStats(
        stellarShards: playerXP.stellarShards.round(),
        lumina: playerXP.lumina.round(),
        totalXP: playerXP.totalXP.round(),
        winStreak: tradingStats.winStreak,
        totalTrades: tradingStats.totalTrades,
        winRate: tradingStats.winRate,
      );
    } catch (e) {
      // Leaderboard provider might not be available yet, ignore error
    }
  }

  /// Initialize XP system for player
  Future<void> initializePlayer(String playerId) async {
    try {
      state = const AsyncValue.loading();
      final playerXP = await _xpService.initializePlayer(playerId);
      state = AsyncValue.data(playerXP);
    } catch (e, stackTrace) {
      state = AsyncValue.error(e, stackTrace);
    }
  }

  /// Generate Stellar Shards from orbital forging
  Future<XPGainEvent?> orbitalForge({
    required String playerId,
    double baseAmount = 5.0,
    bool isCriticalForge = false,
  }) async {
    try {
      final event = await _xpService.generateStellarShards(
        playerId: playerId,
        baseAmount: baseAmount,
        isCriticalForge: isCriticalForge,
      );

      // Update state with new XP data
      final updatedXP = _xpService.currentPlayerXP;
      if (updatedXP != null) {
        state = AsyncValue.data(updatedXP);
        _updateLeaderboard(playerId, updatedXP);
      }

      return event;
    } catch (e) {
      // Don't update state on error, just return null
      return null;
    }
  }

  /// Process mock trade rewards
  Future<XPGainEvent?> processMockTrade({
    required String playerId,
    required double tradeAmount,
    required bool wasSuccessful,
    String? symbol,
  }) async {
    try {
      // Record trade statistics
      await _tradingStatsService.recordTradeResult(
        wasSuccessful: wasSuccessful,
        amount: tradeAmount,
        symbol: symbol,
      );

      final event = await _xpService.generateStellarShardsFromMockTrade(
        playerId: playerId,
        tradeAmount: tradeAmount,
        wasSuccessful: wasSuccessful,
      );

      final updatedXP = _xpService.currentPlayerXP;
      if (updatedXP != null) {
        state = AsyncValue.data(updatedXP);
        _updateLeaderboard(playerId, updatedXP);
      }

      return event;
    } catch (e) {
      return null;
    }
  }

  /// Process real trade Lumina harvest
  Future<XPGainEvent?> harvestLumina({
    required String playerId,
    required double tradeAmount,
    required bool wasSuccessful,
    required String transactionHash,
    String? symbol,
  }) async {
    try {
      // Record trade statistics for real trades
      await _tradingStatsService.recordTradeResult(
        wasSuccessful: wasSuccessful,
        amount: tradeAmount,
        symbol: symbol,
      );

      final event = await _xpService.harvestLumina(
        playerId: playerId,
        tradeAmount: tradeAmount,
        wasSuccessful: wasSuccessful,
        transactionHash: transactionHash,
      );

      final updatedXP = _xpService.currentPlayerXP;
      if (updatedXP != null) {
        state = AsyncValue.data(updatedXP);
        _updateLeaderboard(playerId, updatedXP);
      }

      return event;
    } catch (e) {
      return null;
    }
  }

  /// Process daily login rewards
  Future<XPGainEvent?> processDailyLogin(String playerId) async {
    try {
      final event = await _xpService.processDailyLogin(playerId: playerId);

      final updatedXP = _xpService.currentPlayerXP;
      if (updatedXP != null) {
        state = AsyncValue.data(updatedXP);
        _updateLeaderboard(playerId, updatedXP);
      }

      return event;
    } catch (e) {
      return null;
    }
  }

  /// Upgrade cosmic genesis node
  Future<bool> upgradeCosmicNode({
    required String playerId,
    required String nodeId,
  }) async {
    try {
      final success = await _xpService.upgradeCosmicGenesisNode(
        playerId: playerId,
        nodeId: nodeId,
      );

      if (success) {
        final updatedXP = _xpService.currentPlayerXP;
        if (updatedXP != null) {
          state = AsyncValue.data(updatedXP);
        }
      }

      return success;
    } catch (e) {
      return false;
    }
  }

  /// Process idle time rewards
  Future<double> processIdleTime(Duration idleTime) async {
    try {
      final generatedShards = await _xpService.processIdleTime(idleTime);

      final updatedXP = _xpService.currentPlayerXP;
      if (updatedXP != null) {
        state = AsyncValue.data(updatedXP);
      }

      return generatedShards;
    } catch (e) {
      return 0.0;
    }
  }

  /// Refresh current XP data
  void refresh() {
    final currentXP = _xpService.currentPlayerXP;
    if (currentXP != null) {
      state = AsyncValue.data(currentXP);
    }
  }
}

/// Provider for Stellar Shards balance
final stellarShardsProvider = Provider<double>((ref) {
  final xpState = ref.watch(playerXPProvider);
  return xpState.when(
    data: (xp) => xp?.stellarShards ?? 0.0,
    loading: () => 0.0,
    error: (_, __) => 0.0,
  );
});

/// Provider for Lumina balance
final luminaProvider = Provider<double>((ref) {
  final xpState = ref.watch(playerXPProvider);
  return xpState.when(
    data: (xp) => xp?.lumina ?? 0.0,
    loading: () => 0.0,
    error: (_, __) => 0.0,
  );
});

/// Provider for player level
final playerLevelProvider = Provider<int>((ref) {
  final xpState = ref.watch(playerXPProvider);
  return xpState.when(
    data: (xp) => xp?.level ?? 1,
    loading: () => 1,
    error: (_, __) => 1,
  );
});

/// Provider for level progress (0.0 to 1.0)
final levelProgressProvider = Provider<double>((ref) {
  final xpState = ref.watch(playerXPProvider);
  return xpState.when(
    data: (xp) => xp?.levelProgress ?? 0.0,
    loading: () => 0.0,
    error: (_, __) => 0.0,
  );
});

/// Provider for streak information
final streakInfoProvider = Provider<Map<String, dynamic>>((ref) {
  final xpState = ref.watch(playerXPProvider);
  return xpState.when(
    data: (xp) => {
      'days': xp?.consecutiveDays ?? 0,
      'multiplier': xp?.streakMultiplier ?? 1.0,
      'hasActiveStreak': xp?.hasActiveStreak ?? false,
    },
    loading: () => {'days': 0, 'multiplier': 1.0, 'hasActiveStreak': false},
    error: (_, __) => {'days': 0, 'multiplier': 1.0, 'hasActiveStreak': false},
  );
});

/// Provider for can level up status
final canLevelUpProvider = Provider<bool>((ref) {
  final xpState = ref.watch(playerXPProvider);
  return xpState.when(
    data: (xp) => xp?.canLevelUp ?? false,
    loading: () => false,
    error: (_, __) => false,
  );
});

/// Provider for total XP
final totalXPProvider = Provider<double>((ref) {
  final xpState = ref.watch(playerXPProvider);
  return xpState.when(
    data: (xp) => xp?.totalXP ?? 0.0,
    loading: () => 0.0,
    error: (_, __) => 0.0,
  );
});

/// Provider for current trading statistics
final currentTradingStatsProvider = FutureProvider<TradingStats>((ref) async {
  final tradingStatsService = ref.watch(tradingStatsServiceProvider);
  return await tradingStatsService.getCurrentStats();
});

/// Provider for win streak count
final winStreakProvider = FutureProvider<int>((ref) async {
  final tradingStatsService = ref.watch(tradingStatsServiceProvider);
  return await tradingStatsService.getWinStreak();
});

/// Provider for total trades count
final totalTradesCountProvider = FutureProvider<int>((ref) async {
  final tradingStatsService = ref.watch(tradingStatsServiceProvider);
  return await tradingStatsService.getTotalTrades();
});

/// Provider for win rate percentage
final winRatePercentageProvider = FutureProvider<double>((ref) async {
  final tradingStatsService = ref.watch(tradingStatsServiceProvider);
  return await tradingStatsService.getWinRate();
});

/// Provider for trading history
final tradingHistoryProvider = FutureProvider<List<TradeRecord>>((ref) async {
  final tradingStatsService = ref.watch(tradingStatsServiceProvider);
  return await tradingStatsService.getTradingHistory();
});
