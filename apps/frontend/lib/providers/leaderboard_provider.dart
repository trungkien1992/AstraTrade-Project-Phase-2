import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/leaderboard.dart';
import '../services/leaderboard_service.dart';

/// State class for leaderboard data
class LeaderboardState {
  final List<LeaderboardEntry> entries;
  final bool isLoading;
  final String? error;
  final LeaderboardType currentType;
  final Map<String, dynamic>? stats;
  final DateTime? lastUpdated;

  const LeaderboardState({
    this.entries = const [],
    this.isLoading = false,
    this.error,
    this.currentType = LeaderboardType.stellarShards,
    this.stats,
    this.lastUpdated,
  });

  LeaderboardState copyWith({
    List<LeaderboardEntry>? entries,
    bool? isLoading,
    String? error,
    LeaderboardType? currentType,
    Map<String, dynamic>? stats,
    DateTime? lastUpdated,
  }) {
    return LeaderboardState(
      entries: entries ?? this.entries,
      isLoading: isLoading ?? this.isLoading,
      error: error,
      currentType: currentType ?? this.currentType,
      stats: stats ?? this.stats,
      lastUpdated: lastUpdated ?? this.lastUpdated,
    );
  }

  /// Get current user's entry from the leaderboard
  LeaderboardEntry? get currentUserEntry {
    try {
      return entries.firstWhere((entry) => entry.isCurrentUser);
    } catch (e) {
      return null;
    }
  }

  /// Get top 3 players
  List<LeaderboardEntry> get topThree {
    return entries.take(3).toList();
  }

  /// Check if current user is in top 10
  bool get isUserInTopTen {
    final userEntry = currentUserEntry;
    return userEntry != null && userEntry.rank <= 10;
  }

  /// Get total number of pro traders
  int get proTraderCount {
    return entries.where((entry) => entry.isVerifiedLuminaWeaver).length;
  }
}

/// Notifier for managing leaderboard state
final leaderboardServiceProvider = Provider((ref) => LeaderboardService());

class LeaderboardNotifier extends StateNotifier<LeaderboardState> {
  final LeaderboardService _leaderboardService;

  LeaderboardNotifier(this._leaderboardService)
    : super(const LeaderboardState());

  /// Load leaderboard data for the specified type
  Future<void> loadLeaderboard(LeaderboardType type) async {
    if (state.isLoading) return; // Prevent multiple simultaneous loads

    state = state.copyWith(isLoading: true, error: null, currentType: type);

    try {
      final entries = await _leaderboardService.getLeaderboardData(type);
      final stats = await _leaderboardService.getLeaderboardStats(type);

      state = state.copyWith(
        entries: entries,
        isLoading: false,
        stats: stats,
        lastUpdated: DateTime.now(),
      );

      debugPrint(
        'Loaded ${entries.length} leaderboard entries for ${type.name}',
      );
    } catch (e, stackTrace) {
      debugPrint('Error loading leaderboard: $e');
      debugPrint('Stack trace: $stackTrace');

      state = state.copyWith(
        isLoading: false,
        error: 'Failed to load leaderboard: ${e.toString()}',
      );
    }
  }

  /// Refresh current leaderboard
  Future<void> refresh() async {
    await loadLeaderboard(state.currentType);
  }

  /// Switch to different leaderboard type
  Future<void> switchLeaderboardType(LeaderboardType type) async {
    if (state.currentType != type) {
      await loadLeaderboard(type);
    }
  }

  /// Update current user's position (call after trade completion)
  void updateCurrentUserStats({
    required int stellarShards,
    required int lumina,
    required int totalXP,
    required int winStreak,
    required int totalTrades,
    required double winRate,
  }) {
    // Update the service cache
    _leaderboardService.updateCurrentUserStats(
      stellarShards: stellarShards,
      lumina: lumina,
      totalXP: totalXP,
      winStreak: winStreak,
      totalTrades: totalTrades,
      winRate: winRate,
    );

    // If we have current leaderboard data, update the current user's entry
    if (state.entries.isNotEmpty) {
      final updatedEntries = state.entries.map((entry) {
        if (entry.isCurrentUser) {
          final level = XPCalculator.calculateLevel(totalXP);
          final cosmicTier = CosmicTier.fromXP(totalXP);

          return entry.copyWith(
            stellarShards: stellarShards,
            lumina: lumina,
            level: level,
            totalXP: totalXP,
            cosmicTier: cosmicTier.displayName,
            winStreak: winStreak,
            totalTrades: totalTrades,
            winRate: winRate,
            lastActive: DateTime.now(),
          );
        }
        return entry;
      }).toList();

      // Re-sort based on current leaderboard type
      _sortEntries(updatedEntries, state.currentType);

      // Reassign ranks
      for (int i = 0; i < updatedEntries.length; i++) {
        updatedEntries[i] = updatedEntries[i].copyWith(rank: i + 1);
      }

      state = state.copyWith(
        entries: updatedEntries,
        lastUpdated: DateTime.now(),
      );
    }
  }

  /// Sort entries based on leaderboard type
  void _sortEntries(List<LeaderboardEntry> entries, LeaderboardType type) {
    switch (type) {
      case LeaderboardType.stellarShards:
        entries.sort((a, b) => b.stellarShards.compareTo(a.stellarShards));
        break;
      case LeaderboardType.lumina:
        entries.sort((a, b) => b.lumina.compareTo(a.lumina));
        break;
      case LeaderboardType.level:
        entries.sort((a, b) {
          final levelComparison = b.level.compareTo(a.level);
          if (levelComparison != 0) return levelComparison;
          return b.totalXP.compareTo(a.totalXP);
        });
        break;
      case LeaderboardType.winStreak:
        entries.sort((a, b) {
          final streakComparison = b.winStreak.compareTo(a.winStreak);
          if (streakComparison != 0) return streakComparison;
          return b.winRate.compareTo(a.winRate);
        });
        break;
    }
  }

  /// Get current user's ranking info
  LeaderboardEntry? getCurrentUserRanking() {
    return state.currentUserEntry;
  }

  /// Get top players (limit to specified count)
  List<LeaderboardEntry> getTopPlayers([int limit = 10]) {
    return state.entries.take(limit).toList();
  }

  /// Get players around current user
  List<LeaderboardEntry> getPlayersAroundUser([int range = 3]) {
    final currentUser = state.currentUserEntry;
    if (currentUser == null) return [];

    final startIndex = (currentUser.rank - 1 - range).clamp(
      0,
      state.entries.length,
    );
    final endIndex = (currentUser.rank + range).clamp(0, state.entries.length);

    return state.entries.sublist(startIndex, endIndex);
  }

  /// Clear error state
  void clearError() {
    if (state.error != null) {
      state = state.copyWith(error: null);
    }
  }

  @override
  void dispose() {
    _leaderboardService.dispose();
    super.dispose();
  }
}

/// Provider for leaderboard state
final leaderboardProvider =
    StateNotifierProvider<LeaderboardNotifier, LeaderboardState>(
      (ref) => LeaderboardNotifier(ref.watch(leaderboardServiceProvider)),
    );

/// Provider for current leaderboard type
final currentLeaderboardTypeProvider = StateProvider<LeaderboardType>(
  (ref) => LeaderboardType.stellarShards,
);

/// Provider for leaderboard statistics
final leaderboardStatsProvider = Provider<Map<String, dynamic>?>((ref) {
  final state = ref.watch(leaderboardProvider);
  return state.stats;
});

/// Provider for current user's leaderboard position
final currentUserRankingProvider = Provider<LeaderboardEntry?>((ref) {
  final state = ref.watch(leaderboardProvider);
  return state.currentUserEntry;
});

/// Provider for top 3 players
final topThreePlayersProvider = Provider<List<LeaderboardEntry>>((ref) {
  final state = ref.watch(leaderboardProvider);
  return state.topThree;
});

/// Provider that auto-refreshes leaderboard data periodically
final autoRefreshLeaderboardProvider = StreamProvider<LeaderboardState>((ref) {
  final notifier = ref.watch(leaderboardProvider.notifier);

  return Stream.periodic(
    const Duration(minutes: 2), // Refresh every 2 minutes
    (_) => notifier.refresh(),
  ).asyncMap((_) async {
    await Future.delayed(const Duration(milliseconds: 100)); // Small delay
    return ref.read(leaderboardProvider);
  });
});
