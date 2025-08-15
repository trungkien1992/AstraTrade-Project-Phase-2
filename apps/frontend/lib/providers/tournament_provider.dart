import 'dart:async';
import 'package:flutter/foundation.dart';
import '../services/tournament_websocket_service.dart';
import '../models/tournament_models.dart';

class TournamentProvider extends ChangeNotifier {
  final TournamentWebSocketService _webSocketService = TournamentWebSocketService();
  
  // State
  TournamentUIState _state = TournamentUIState();
  final List<TournamentNotification> _notifications = [];
  StreamSubscription<List<LeaderboardEntry>>? _leaderboardSubscription;
  StreamSubscription<LiveTrade>? _liveTradesSubscription;
  StreamSubscription<Achievement>? _achievementsSubscription;
  StreamSubscription<TournamentEvent>? _tournamentEventsSubscription;
  StreamSubscription<AITraderInfo>? _aiTraderInfoSubscription;
  StreamSubscription<WebSocketConnectionState>? _connectionStateSubscription;
  StreamSubscription<LeaderboardUpdateData>? _leaderboardUpdatesSubscription;
  StreamSubscription<NearbyCompetitorsData>? _nearbyCompetitorsSubscription;
  StreamSubscription<String>? _errorSubscription;
  
  // Private state
  final Map<String, AITraderInfo> _aiTraders = {};
  String? _currentTournamentId;
  Timer? _notificationCleanupTimer;
  
  // Getters
  TournamentUIState get state => _state;
  List<TournamentNotification> get notifications => List.unmodifiable(_notifications);
  WebSocketConnectionState get connectionState => _webSocketService.connectionState;
  bool get isConnected => _webSocketService.isConnected;
  String? get currentTournamentId => _currentTournamentId;
  Map<String, dynamic> get connectionStats => _webSocketService.getConnectionStats();
  Map<String, AITraderInfo> get aiTraders => Map.unmodifiable(_aiTraders);
  
  TournamentProvider() {
    _setupSubscriptions();
    _startNotificationCleanup();
  }
  
  void _setupSubscriptions() {
    // Leaderboard updates
    _leaderboardSubscription = _webSocketService.leaderboardStream.listen(
      (leaderboard) {
        _updateState((state) => state.copyWith(
          leaderboard: leaderboard,
          isConnected: true,
        ));
      },
    );
    
    // Live trades
    _liveTradesSubscription = _webSocketService.liveTradesStream.listen(
      (trade) {
        final updatedTrades = [trade, ..._state.recentTrades.take(49)].toList();
        _updateState((state) => state.copyWith(recentTrades: updatedTrades));
        
        // Create notification for significant trades
        if (_shouldNotifyForTrade(trade)) {
          _addNotification(TournamentNotification(
            type: TournamentNotificationType.aiTradeAlert,
            title: '${trade.isAi ? '🤖' : '👤'} ${trade.username}',
            message: '${trade.side} ${trade.symbol} for \$${trade.amount.toStringAsFixed(2)}',
            data: {'trade': trade.toJson()},
            displayDuration: Duration(seconds: 5),
          ));
        }
      },
    );
    
    // Achievements
    _achievementsSubscription = _webSocketService.achievementsStream.listen(
      (achievement) {
        final updatedAchievements = [achievement, ..._state.recentAchievements.take(9)].toList();
        _updateState((state) => state.copyWith(recentAchievements: updatedAchievements));
        
        _addNotification(TournamentNotification(
          type: TournamentNotificationType.achievementUnlocked,
          title: '🏆 Achievement Unlocked!',
          message: '${achievement.username}: ${achievement.title}',
          data: {'achievement': achievement.toJson()},
          displayDuration: Duration(seconds: 8),
        ));
      },
    );
    
    // Tournament events
    _tournamentEventsSubscription = _webSocketService.tournamentEventsStream.listen(
      (event) {
        _updateState((state) => state.copyWith(activeEvent: event));
        
        _addNotification(TournamentNotification(
          type: TournamentNotificationType.tournamentEvent,
          title: '🎯 ${event.title}',
          message: event.description,
          data: {'event': event.toJson()},
          displayDuration: Duration(seconds: 10),
        ));
      },
    );
    
    // AI Trader info
    _aiTraderInfoSubscription = _webSocketService.aiTraderInfoStream.listen(
      (aiInfo) {
        _aiTraders[aiInfo.id] = aiInfo;
        notifyListeners();
      },
    );
    
    // Connection state changes
    _connectionStateSubscription = _webSocketService.connectionStateStream.listen(
      (connectionState) {
        final isConnected = connectionState == WebSocketConnectionState.connected ||
                           connectionState == WebSocketConnectionState.authenticated;
        
        _updateState((state) => state.copyWith(
          isConnected: isConnected,
          errorMessage: isConnected ? null : state.errorMessage,
        ));
        
        if (isConnected && _state.errorMessage == null) {
          _addNotification(TournamentNotification(
            type: TournamentNotificationType.tournamentEvent,
            title: '🌐 Connected',
            message: 'Tournament updates are now live',
            displayDuration: Duration(seconds: 3),
          ));
        }
      },
    );
    
    // Leaderboard position updates
    _leaderboardUpdatesSubscription = _webSocketService.leaderboardUpdatesStream.listen(
      (update) {
        _handleLeaderboardUpdate(update);
      },
    );
    
    // Nearby competitors
    _nearbyCompetitorsSubscription = _webSocketService.nearbyCompetitorsStream.listen(
      (competitors) {
        // Update leaderboard with nearby competitors data
        _updateState((state) => state.copyWith(
          leaderboard: competitors.competitors,
        ));
        
        // Check for competitors very close to user
        final closeCompetitors = competitors.competitors
            .where((c) => !c.isAi && c.userId != _getCurrentUserId())
            .where((c) => (c.rank - competitors.userRank).abs() <= 2)
            .toList();
            
        if (closeCompetitors.isNotEmpty && closeCompetitors.length <= 2) {
          _addNotification(TournamentNotification(
            type: TournamentNotificationType.competitorNearby,
            title: '👀 Close Competition',
            message: 'You\'re neck and neck with ${closeCompetitors.first.username}!',
            displayDuration: Duration(seconds: 6),
          ));
        }
      },
    );
    
    // Error handling
    _errorSubscription = _webSocketService.errorStream.listen(
      (error) {
        _updateState((state) => state.copyWith(
          errorMessage: error,
          isConnected: false,
        ));
        
        _addNotification(TournamentNotification(
          type: TournamentNotificationType.tournamentEvent,
          title: '⚠️ Connection Issue',
          message: error,
          displayDuration: Duration(seconds: 8),
        ));
      },
    );
  }
  
  void _updateState(TournamentUIState Function(TournamentUIState) updater) {
    _state = updater(_state);
    notifyListeners();
  }
  
  void _handleLeaderboardUpdate(LeaderboardUpdateData update) {
    // Update the leaderboard entry if it exists
    final updatedLeaderboard = _state.leaderboard.map((entry) {
      if (entry.userId == update.userId) {
        return LeaderboardEntry(
          rank: update.newRank,
          userId: entry.userId,
          username: entry.username,
          score: update.newScore,
          isAi: entry.isAi,
          avatar: entry.avatar,
          league: entry.league,
          changeDirection: update.rankChange > 0 ? 'up' : 
                          update.rankChange < 0 ? 'down' : 'same',
          changeAmount: update.rankChange.abs(),
        );
      }
      return entry;
    }).toList();
    
    // Sort by rank
    updatedLeaderboard.sort((a, b) => a.rank.compareTo(b.rank));
    
    _updateState((state) => state.copyWith(leaderboard: updatedLeaderboard));
    
    // Update user's rank and score if this update is for the current user
    final currentUserId = _getCurrentUserId();
    if (currentUserId != null && update.userId == currentUserId) {
      _updateState((state) => state.copyWith(
        userRank: update.newRank,
        userScore: update.newScore,
      ));
      
      // Notify for significant rank changes
      if (update.rankChange.abs() >= 3) {
        final direction = update.rankChange > 0 ? 'climbed' : 'dropped';
        _addNotification(TournamentNotification(
          type: TournamentNotificationType.leaderboardChange,
          title: '📈 Rank Update',
          message: 'You $direction ${update.rankChange.abs()} positions to #${update.newRank}',
          displayDuration: Duration(seconds: 7),
        ));
      }
    }
    
    // Notify for top 10 changes
    if (update.newRank <= 10 && !update.isAi) {
      _addNotification(TournamentNotification(
        type: TournamentNotificationType.leaderboardChange,
        title: '👑 Top 10 Update',
        message: '${update.username} is now #${update.newRank}',
        displayDuration: Duration(seconds: 4),
      ));
    }
  }
  
  void _addNotification(TournamentNotification notification) {
    _notifications.insert(0, notification);
    
    // Limit notifications to prevent memory issues
    if (_notifications.length > 50) {
      _notifications.removeRange(50, _notifications.length);
    }
    
    notifyListeners();
  }
  
  bool _shouldNotifyForTrade(LiveTrade trade) {
    // Only notify for significant trades or AI trades from famous traders
    if (trade.amount >= 10000) return true; // Large trades
    if (trade.isAi && _isNotableAITrader(trade.userId)) return true;
    if (trade.profitPercentage != null && trade.profitPercentage!.abs() >= 15) return true; // Big wins/losses
    
    return false;
  }
  
  bool _isNotableAITrader(String userId) {
    final notableAIs = [
      'ai:captain_vega',
      'ai:admiral_nexus', 
      'ai:plasma_phoenix',
      'ai:quantum_flash'
    ];
    return notableAIs.contains(userId);
  }
  
  String? _getCurrentUserId() {
    // This would be retrieved from authentication service
    // For now, return null
    return null;
  }
  
  void _startNotificationCleanup() {
    _notificationCleanupTimer = Timer.periodic(Duration(minutes: 1), (_) {
      final now = DateTime.now();
      _notifications.removeWhere((notification) {
        final age = now.difference(notification.timestamp);
        return age.inMinutes > 10; // Remove notifications older than 10 minutes
      });
    });
  }
  
  // Public methods
  Future<void> connectToTournament(String tournamentId, {String? authToken}) async {
    _currentTournamentId = tournamentId;
    
    // Clear previous state
    _state = TournamentUIState();
    _notifications.clear();
    _aiTraders.clear();
    
    await _webSocketService.connectToTournament(tournamentId, authToken: authToken);
  }
  
  void disconnect() {
    _webSocketService.disconnect();
    _currentTournamentId = null;
    _updateState((state) => state.copyWith(isConnected: false));
  }
  
  void requestNearbyCompetitors({int radius = 5}) {
    _webSocketService.requestNearbyCompetitors(radius: radius);
  }
  
  void requestAITraderInfo(String aiId) {
    _webSocketService.requestAITraderInfo(aiId);
  }
  
  void requestDetailedLeaderboard({int start = 0, int limit = 50}) {
    _webSocketService.requestDetailedLeaderboard(start: start, limit: limit);
  }
  
  void authenticate(String token) {
    _webSocketService.authenticate(token);
  }
  
  void dismissNotification(int index) {
    if (index >= 0 && index < _notifications.length) {
      _notifications.removeAt(index);
      notifyListeners();
    }
  }
  
  void clearAllNotifications() {
    _notifications.clear();
    notifyListeners();
  }
  
  List<TournamentNotification> getNotificationsByType(TournamentNotificationType type) {
    return _notifications.where((n) => n.type == type).toList();
  }
  
  AITraderInfo? getAITrader(String aiId) {
    return _aiTraders[aiId];
  }
  
  List<LeaderboardEntry> getTopAITraders({int count = 5}) {
    return _state.leaderboard
        .where((entry) => entry.isAi)
        .take(count)
        .toList();
  }
  
  List<LeaderboardEntry> getTopHumanTraders({int count = 5}) {
    return _state.leaderboard
        .where((entry) => !entry.isAi)
        .take(count)
        .toList();
  }
  
  // Get user's position in leaderboard
  LeaderboardEntry? getUserLeaderboardEntry() {
    final currentUserId = _getCurrentUserId();
    if (currentUserId == null) return null;
    
    return _state.leaderboard.firstWhere(
      (entry) => entry.userId == currentUserId,
      orElse: () => LeaderboardEntry(
        rank: 0,
        userId: currentUserId,
        username: 'You',
        score: 0.0,
        isAi: false,
      ),
    );
  }
  
  // Statistics
  Map<String, dynamic> getTournamentStatistics() {
    final totalParticipants = _state.leaderboard.length;
    final aiCount = _state.leaderboard.where((e) => e.isAi).length;
    final humanCount = totalParticipants - aiCount;
    
    return {
      'total_participants': totalParticipants,
      'human_participants': humanCount,
      'ai_participants': aiCount,
      'total_trades': _state.recentTrades.length,
      'achievements_unlocked': _state.recentAchievements.length,
      'connection_duration': _webSocketService.connectionDuration?.inMinutes ?? 0,
      'messages_received': _webSocketService.messagesReceived,
      'messages_sent': _webSocketService.messagesSent,
      'last_update': _state.lastUpdate.toIso8601String(),
    };
  }
  
  // Testing and debugging methods
  void simulateConnectionLoss() {
    if (kDebugMode) {
      _webSocketService.simulateConnectionLoss();
    }
  }
  
  void forceReconnect() {
    if (kDebugMode) {
      _webSocketService.forceReconnect();
    }
  }
  
  void resetReconnectAttempts() {
    _webSocketService.resetReconnectAttempts();
  }
  
  @override
  void dispose() {
    _webSocketService.dispose();
    
    _leaderboardSubscription?.cancel();
    _liveTradesSubscription?.cancel();
    _achievementsSubscription?.cancel();
    _tournamentEventsSubscription?.cancel();
    _aiTraderInfoSubscription?.cancel();
    _connectionStateSubscription?.cancel();
    _leaderboardUpdatesSubscription?.cancel();
    _nearbyCompetitorsSubscription?.cancel();
    _errorSubscription?.cancel();
    _notificationCleanupTimer?.cancel();
    
    super.dispose();
  }
}