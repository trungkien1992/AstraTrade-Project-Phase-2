import 'package:json_annotation/json_annotation.dart';

part 'tournament_models.g.dart';

@JsonSerializable()
class LeaderboardEntry {
  final int rank;
  @JsonKey(name: 'user_id')
  final String userId;
  final String username;
  final double score;
  @JsonKey(name: 'is_ai', defaultValue: false)
  final bool isAi;
  final String? avatar;
  final String? league;
  @JsonKey(name: 'change_direction')
  final String? changeDirection;
  @JsonKey(name: 'change_amount')
  final int? changeAmount;

  LeaderboardEntry({
    required this.rank,
    required this.userId,
    required this.username,
    required this.score,
    required this.isAi,
    this.avatar,
    this.league,
    this.changeDirection,
    this.changeAmount,
  });

  factory LeaderboardEntry.fromJson(Map<String, dynamic> json) =>
      _$LeaderboardEntryFromJson(json);

  Map<String, dynamic> toJson() => _$LeaderboardEntryToJson(this);
}

@JsonSerializable()
class TournamentMetadata {
  @JsonKey(name: 'tournament_id')
  final String tournamentId;
  final String status;
  @JsonKey(name: 'start_time')
  final String startTime;
  @JsonKey(name: 'end_time')
  final String endTime;
  @JsonKey(name: 'total_participants')
  final int totalParticipants;
  @JsonKey(name: 'total_trades')
  final int totalTrades;
  @JsonKey(name: 'prize_pool')
  final double? prizePool;
  @JsonKey(name: 'entry_fee')
  final double? entryFee;

  TournamentMetadata({
    required this.tournamentId,
    required this.status,
    required this.startTime,
    required this.endTime,
    required this.totalParticipants,
    required this.totalTrades,
    this.prizePool,
    this.entryFee,
  });

  factory TournamentMetadata.fromJson(Map<String, dynamic> json) =>
      _$TournamentMetadataFromJson(json);

  Map<String, dynamic> toJson() => _$TournamentMetadataToJson(this);
}

@JsonSerializable()
class UserTournamentStats {
  @JsonKey(name: 'user_id')
  final String userId;
  @JsonKey(name: 'total_trades')
  final int totalTrades;
  @JsonKey(name: 'winning_trades')
  final int winningTrades;
  @JsonKey(name: 'total_profit')
  final double totalProfit;
  @JsonKey(name: 'total_volume')
  final double totalVolume;
  @JsonKey(name: 'win_rate')
  final double winRate;
  @JsonKey(name: 'portfolio_value')
  final double portfolioValue;
  final int? rank;
  final double? percentile;

  UserTournamentStats({
    required this.userId,
    required this.totalTrades,
    required this.winningTrades,
    required this.totalProfit,
    required this.totalVolume,
    required this.winRate,
    required this.portfolioValue,
    this.rank,
    this.percentile,
  });

  factory UserTournamentStats.fromJson(Map<String, dynamic> json) =>
      _$UserTournamentStatsFromJson(json);

  Map<String, dynamic> toJson() => _$UserTournamentStatsToJson(this);
}

@JsonSerializable()
class LiveTrade {
  @JsonKey(name: 'trade_id')
  final String tradeId;
  @JsonKey(name: 'user_id')
  final String userId;
  final String username;
  final String symbol;
  final String side;
  final double amount;
  final double? price;
  final double? profit;
  @JsonKey(name: 'profit_percentage')
  final double? profitPercentage;
  @JsonKey(name: 'is_ai', defaultValue: false)
  final bool isAi;
  @JsonKey(name: 'ai_strategy')
  final String? aiStrategy;
  final String timestamp;

  LiveTrade({
    required this.tradeId,
    required this.userId,
    required this.username,
    required this.symbol,
    required this.side,
    required this.amount,
    this.price,
    this.profit,
    this.profitPercentage,
    required this.isAi,
    this.aiStrategy,
    required this.timestamp,
  });

  factory LiveTrade.fromJson(Map<String, dynamic> json) =>
      _$LiveTradeFromJson(json);

  Map<String, dynamic> toJson() => _$LiveTradeToJson(this);
}

@JsonSerializable()
class Achievement {
  @JsonKey(name: 'achievement_id')
  final String achievementId;
  @JsonKey(name: 'user_id')
  final String userId;
  final String username;
  final String title;
  final String description;
  final String icon;
  final int points;
  final String rarity;
  final String category;
  @JsonKey(name: 'unlocked_at')
  final String unlockedAt;

  Achievement({
    required this.achievementId,
    required this.userId,
    required this.username,
    required this.title,
    required this.description,
    required this.icon,
    required this.points,
    required this.rarity,
    required this.category,
    required this.unlockedAt,
  });

  factory Achievement.fromJson(Map<String, dynamic> json) =>
      _$AchievementFromJson(json);

  Map<String, dynamic> toJson() => _$AchievementToJson(this);
}

@JsonSerializable()
class AITraderInfo {
  final String id;
  final String name;
  final String title;
  final String strategy;
  final String backstory;
  @JsonKey(name: 'risk_profile')
  final Map<String, double> riskProfile;
  @JsonKey(name: 'personality_traits')
  final Map<String, double> personalityTraits;
  @JsonKey(name: 'preferred_symbols')
  final List<String> preferredSymbols;
  @JsonKey(name: 'trading_hours')
  final List<int> tradingHours;
  @JsonKey(name: 'current_state')
  final Map<String, dynamic> currentState;
  @JsonKey(name: 'performance_stats')
  final Map<String, dynamic>? performanceStats;

  AITraderInfo({
    required this.id,
    required this.name,
    required this.title,
    required this.strategy,
    required this.backstory,
    required this.riskProfile,
    required this.personalityTraits,
    required this.preferredSymbols,
    required this.tradingHours,
    required this.currentState,
    this.performanceStats,
  });

  factory AITraderInfo.fromJson(Map<String, dynamic> json) =>
      _$AITraderInfoFromJson(json);

  Map<String, dynamic> toJson() => _$AITraderInfoToJson(this);
}

@JsonSerializable()
class TournamentEvent {
  @JsonKey(name: 'event_id')
  final String eventId;
  @JsonKey(name: 'event_type')
  final String eventType;
  final String title;
  final String description;
  @JsonKey(name: 'duration_minutes')
  final int? durationMinutes;
  final double? multiplier;
  @JsonKey(name: 'affects_leaderboard')
  final bool affectsLeaderboard;
  @JsonKey(name: 'started_at')
  final String startedAt;
  @JsonKey(name: 'ends_at')
  final String? endsAt;

  TournamentEvent({
    required this.eventId,
    required this.eventType,
    required this.title,
    required this.description,
    this.durationMinutes,
    this.multiplier,
    required this.affectsLeaderboard,
    required this.startedAt,
    this.endsAt,
  });

  factory TournamentEvent.fromJson(Map<String, dynamic> json) =>
      _$TournamentEventFromJson(json);

  Map<String, dynamic> toJson() => _$TournamentEventToJson(this);
}

@JsonSerializable()
class InitialStateData {
  @JsonKey(name: 'tournament_id')
  final String tournamentId;
  final List<LeaderboardEntry> leaderboard;
  @JsonKey(name: 'user_rank')
  final int? userRank;
  @JsonKey(name: 'user_score')
  final double? userScore;
  @JsonKey(name: 'user_stats')
  final UserTournamentStats? userStats;
  @JsonKey(name: 'active_connections')
  final int activeConnections;
  @JsonKey(name: 'tournament_meta')
  final TournamentMetadata tournamentMeta;
  @JsonKey(name: 'server_time')
  final double serverTime;
  @JsonKey(name: 'ai_traders_count')
  final int aiTradersCount;
  @JsonKey(name: 'recent_trades', defaultValue: <LiveTrade>[])
  final List<LiveTrade> recentTrades;

  InitialStateData({
    required this.tournamentId,
    required this.leaderboard,
    this.userRank,
    this.userScore,
    this.userStats,
    required this.activeConnections,
    required this.tournamentMeta,
    required this.serverTime,
    required this.aiTradersCount,
    required this.recentTrades,
  });

  factory InitialStateData.fromJson(Map<String, dynamic> json) =>
      _$InitialStateDataFromJson(json);

  Map<String, dynamic> toJson() => _$InitialStateDataToJson(this);
}

@JsonSerializable()
class LeaderboardUpdateData {
  @JsonKey(name: 'user_id')
  final String userId;
  final String username;
  @JsonKey(name: 'old_rank')
  final int? oldRank;
  @JsonKey(name: 'new_rank')
  final int newRank;
  @JsonKey(name: 'old_score')
  final double? oldScore;
  @JsonKey(name: 'new_score')
  final double newScore;
  @JsonKey(name: 'rank_change', defaultValue: 0)
  final int rankChange;
  @JsonKey(name: 'score_change', defaultValue: 0.0)
  final double scoreChange;
  @JsonKey(name: 'is_ai', defaultValue: false)
  final bool isAi;

  LeaderboardUpdateData({
    required this.userId,
    required this.username,
    this.oldRank,
    required this.newRank,
    this.oldScore,
    required this.newScore,
    required this.rankChange,
    required this.scoreChange,
    required this.isAi,
  });

  factory LeaderboardUpdateData.fromJson(Map<String, dynamic> json) =>
      _$LeaderboardUpdateDataFromJson(json);

  Map<String, dynamic> toJson() => _$LeaderboardUpdateDataToJson(this);
}

@JsonSerializable()
class NearbyCompetitorsData {
  final List<LeaderboardEntry> competitors;
  @JsonKey(name: 'user_rank')
  final int userRank;
  final int radius;
  @JsonKey(name: 'total_participants')
  final int totalParticipants;

  NearbyCompetitorsData({
    required this.competitors,
    required this.userRank,
    required this.radius,
    required this.totalParticipants,
  });

  factory NearbyCompetitorsData.fromJson(Map<String, dynamic> json) =>
      _$NearbyCompetitorsDataFromJson(json);

  Map<String, dynamic> toJson() => _$NearbyCompetitorsDataToJson(this);
}

@JsonSerializable()
class AuthenticationData {
  @JsonKey(name: 'user_id')
  final String userId;
  final String? username;
  final bool authenticated;
  final List<String> permissions;

  AuthenticationData({
    required this.userId,
    this.username,
    required this.authenticated,
    required this.permissions,
  });

  factory AuthenticationData.fromJson(Map<String, dynamic> json) =>
      _$AuthenticationDataFromJson(json);

  Map<String, dynamic> toJson() => _$AuthenticationDataToJson(this);
}

@JsonSerializable()
class ErrorData {
  @JsonKey(name: 'error_code')
  final String errorCode;
  @JsonKey(name: 'error_message')
  final String errorMessage;
  final Map<String, dynamic>? details;
  @JsonKey(name: 'retry_after')
  final int? retryAfter;

  ErrorData({
    required this.errorCode,
    required this.errorMessage,
    this.details,
    this.retryAfter,
  });

  factory ErrorData.fromJson(Map<String, dynamic> json) =>
      _$ErrorDataFromJson(json);

  Map<String, dynamic> toJson() => _$ErrorDataToJson(this);
}

@JsonSerializable()
class ConnectionStats {
  @JsonKey(name: 'total_connections')
  final int totalConnections;
  @JsonKey(name: 'peak_concurrent')
  final int peakConcurrent;
  @JsonKey(name: 'messages_sent')
  final int messagesSent;
  @JsonKey(name: 'messages_received')
  final int messagesReceived;
  final int reconnections;
  @JsonKey(name: 'current_connections')
  final int currentConnections;
  @JsonKey(name: 'active_tournaments')
  final int activeTournaments;
  @JsonKey(name: 'tournament_breakdown')
  final Map<String, int> tournamentBreakdown;

  ConnectionStats({
    required this.totalConnections,
    required this.peakConcurrent,
    required this.messagesSent,
    required this.messagesReceived,
    required this.reconnections,
    required this.currentConnections,
    required this.activeTournaments,
    required this.tournamentBreakdown,
  });

  factory ConnectionStats.fromJson(Map<String, dynamic> json) =>
      _$ConnectionStatsFromJson(json);

  Map<String, dynamic> toJson() => _$ConnectionStatsToJson(this);
}

// Utility classes for UI state management
class TournamentUIState {
  final List<LeaderboardEntry> leaderboard;
  final List<LiveTrade> recentTrades;
  final List<Achievement> recentAchievements;
  final TournamentEvent? activeEvent;
  final UserTournamentStats? userStats;
  final int? userRank;
  final double? userScore;
  final bool isConnected;
  final String? errorMessage;
  final DateTime lastUpdate;

  TournamentUIState({
    this.leaderboard = const [],
    this.recentTrades = const [],
    this.recentAchievements = const [],
    this.activeEvent,
    this.userStats,
    this.userRank,
    this.userScore,
    this.isConnected = false,
    this.errorMessage,
    DateTime? lastUpdate,
  }) : lastUpdate = lastUpdate ?? DateTime.now();

  TournamentUIState copyWith({
    List<LeaderboardEntry>? leaderboard,
    List<LiveTrade>? recentTrades,
    List<Achievement>? recentAchievements,
    TournamentEvent? activeEvent,
    UserTournamentStats? userStats,
    int? userRank,
    double? userScore,
    bool? isConnected,
    String? errorMessage,
    DateTime? lastUpdate,
  }) {
    return TournamentUIState(
      leaderboard: leaderboard ?? this.leaderboard,
      recentTrades: recentTrades ?? this.recentTrades,
      recentAchievements: recentAchievements ?? this.recentAchievements,
      activeEvent: activeEvent ?? this.activeEvent,
      userStats: userStats ?? this.userStats,
      userRank: userRank ?? this.userRank,
      userScore: userScore ?? this.userScore,
      isConnected: isConnected ?? this.isConnected,
      errorMessage: errorMessage,
      lastUpdate: lastUpdate ?? DateTime.now(),
    );
  }
}

// Tournament notification types
enum TournamentNotificationType {
  leaderboardChange,
  achievementUnlocked,
  tournamentEvent,
  aiTradeAlert,
  competitorNearby,
  personalBest,
}

class TournamentNotification {
  final TournamentNotificationType type;
  final String title;
  final String message;
  final String? imageUrl;
  final Map<String, dynamic>? data;
  final DateTime timestamp;
  final Duration? displayDuration;

  TournamentNotification({
    required this.type,
    required this.title,
    required this.message,
    this.imageUrl,
    this.data,
    DateTime? timestamp,
    this.displayDuration,
  }) : timestamp = timestamp ?? DateTime.now();
}

// WebSocket message types enum
enum WebSocketMessageType {
  initialState,
  leaderboardUpdate,
  liveTrade,
  achievementUnlocked,
  tournamentEvent,
  heartbeat,
  nearbyCompetitors,
  aiTraderInfo,
  detailedLeaderboard,
  authenticationSuccess,
  error,
  getNearbyCompetitors,
  getAITraderInfo,
  getDetailedLeaderboard,
  authenticate,
  heartbeatResponse,
}