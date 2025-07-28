import 'dart:async';
import 'dart:math' as math;
import 'package:flutter/foundation.dart';
import '../models/leaderboard.dart';
import '../api/astratrade_backend_client.dart';

/// Service for managing leaderboard data and rankings
class LeaderboardService {
  static final LeaderboardService _instance = LeaderboardService._internal();
  factory LeaderboardService() => _instance;
  LeaderboardService._internal();

  final _backendClient = AstraTradeBackendClient();

  /// Get leaderboard data for the specified type
  Future<List<LeaderboardEntry>> getLeaderboardData(LeaderboardType type) async {
    // Only one type supported in backend for now
    final backendEntries = await _backendClient.getLeaderboard();
    // Map backend entries to app model
    return backendEntries.map((e) => LeaderboardEntry(
      userId: e.userId.toString(),
      username: e.username,
      avatarUrl: '', // Extend if backend supports
      rank: 0, // Will be set after sorting
      stellarShards: e.xp, // Map XP to shards for now
      lumina: 0, // Extend if backend supports
      level: e.level,
      totalXP: e.xp,
      cosmicTier: '', // Extend if needed
      isVerifiedLuminaWeaver: false,
      isCurrentUser: false, // Set in provider/UI
      planetIcon: '',
      winStreak: 0,
      totalTrades: 0,
      winRate: 0.0,
      lastActive: DateTime.now(),
    )).toList();
  }

  /// Get current user's ranking for a specific leaderboard type
  Future<LeaderboardEntry?> getCurrentUserRanking(LeaderboardType type) async {
    final leaderboard = await getLeaderboardData(type);
    return leaderboard.firstWhere(
      (entry) => entry.isCurrentUser,
      orElse: () => throw StateError('Current user not found in leaderboard'),
    );
  }

  /// Get top players for the specified type (limit results)
  Future<List<LeaderboardEntry>> getTopPlayers(LeaderboardType type, {int limit = 10}) async {
    final leaderboard = await getLeaderboardData(type);
    return leaderboard.take(limit).toList();
  }

  /// Get players around current user's rank
  Future<List<LeaderboardEntry>> getPlayersAroundUser(LeaderboardType type, {int range = 5}) async {
    final leaderboard = await getLeaderboardData(type);
    final currentUser = leaderboard.firstWhere((entry) => entry.isCurrentUser);
    
    final startIndex = math.max(0, currentUser.rank - 1 - range);
    final endIndex = math.min(leaderboard.length, currentUser.rank + range);
    
    return leaderboard.sublist(startIndex, endIndex);
  }

  /// Update current user's stats (for real-time updates)
  void updateCurrentUserStats({
    required int stellarShards,
    required int lumina,
    required int totalXP,
    required int winStreak,
    required int totalTrades,
    required double winRate,
  }) {
    // In a real app, this would update the backend
    // For now, we'll just invalidate the cache
    _invalidateCache();
    
    debugPrint('Updated current user stats: SS=$stellarShards, LM=$lumina, XP=$totalXP');
  }

  /// Invalidate cached data to force refresh
  void _invalidateCache() {
    // No cache to invalidate as data is fetched directly from backend
  }

  /// Check if cache is still valid
  bool _isCacheValid() {
    // No cache to check
    return true;
  }

  /// Generate Stellar Shards leaderboard (Trade Token Leaderboard)
  List<LeaderboardEntry> _getStellarShardsLeaderboard() {
    // This method is no longer needed as data is fetched directly from backend
    return [];
  }

  /// Generate Lumina leaderboard (Pro Traders only)
  List<LeaderboardEntry> _getLuminaLeaderboard() {
    // This method is no longer needed as data is fetched directly from backend
    return [];
  }

  /// Generate level-based leaderboard
  List<LeaderboardEntry> _getLevelLeaderboard() {
    // This method is no longer needed as data is fetched directly from backend
    return [];
  }

  /// Generate win streak leaderboard
  List<LeaderboardEntry> _getWinStreakLeaderboard() {
    // This method is no longer needed as data is fetched directly from backend
    return [];
  }

  /// Generate mock user data for leaderboard
  List<LeaderboardEntry> _generateMockUsers() {
    // This method is no longer needed as data is fetched directly from backend
    return [];
  }

  /// Simulate real-time leaderboard updates (for demo purposes)
  Stream<List<LeaderboardEntry>> getLeaderboardStream(LeaderboardType type) {
    return Stream.periodic(
      Duration(seconds: 30), // Update every 30 seconds
      (_) => getLeaderboardData(type),
    ).asyncMap((future) => future);
  }

  /// Get leaderboard statistics
  Future<Map<String, dynamic>> getLeaderboardStats(LeaderboardType type) async {
    final leaderboard = await getLeaderboardData(type);
    
    int totalPlayers = leaderboard.length;
    int proTraders = leaderboard.where((e) => false).length; // No LuminaWeaver field in LeaderboardEntry
    
    double avgLevel = leaderboard.map((e) => e.level).reduce((a, b) => a + b) / totalPlayers;
    int totalStellarShards = leaderboard.map((e) => e.stellarShards).reduce((a, b) => a + b);
    int totalLumina = leaderboard.map((e) => 0).reduce((a, b) => a + b); // Lumina is 0 in backend
    
    return {
      'totalPlayers': totalPlayers,
      'proTraders': proTraders,
      'averageLevel': avgLevel.round(),
      'totalStellarShards': totalStellarShards,
      'totalLumina': totalLumina,
      'topPlayerSS': leaderboard.first.stellarShards,
      'topPlayerLumina': 0, // Lumina is 0 in backend
    };
  }

  /// Clean up resources
  void dispose() {
    // No resources to dispose
  }
}