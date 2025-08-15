import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'dart:math';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:web_socket_channel/io.dart';
import 'package:flutter/foundation.dart';
import '../models/tournament_models.dart';

enum WebSocketConnectionState {
  disconnected,
  connecting,
  connected,
  authenticated,
  reconnecting,
  error
}

class TournamentWebSocketService {
  static const String _wsBaseUrl = kDebugMode 
    ? 'ws://localhost:8000' 
    : 'wss://api.astratrade.com';
    
  WebSocketChannel? _channel;
  Timer? _reconnectTimer;
  Timer? _heartbeatTimer;
  Timer? _connectionTimeoutTimer;
  
  // Connection state
  WebSocketConnectionState _connectionState = WebSocketConnectionState.disconnected;
  String? _currentTournamentId;
  String? _authToken;
  int _reconnectAttempts = 0;
  static const int _maxReconnectAttempts = 10;
  static const int _heartbeatIntervalSeconds = 30;
  static const int _connectionTimeoutSeconds = 10;
  
  // Stream controllers
  final StreamController<List<LeaderboardEntry>> _leaderboardController = 
      StreamController<List<LeaderboardEntry>>.broadcast();
  final StreamController<LiveTrade> _liveTradesController = 
      StreamController<LiveTrade>.broadcast();
  final StreamController<Achievement> _achievementsController = 
      StreamController<Achievement>.broadcast();
  final StreamController<TournamentEvent> _tournamentEventsController = 
      StreamController<TournamentEvent>.broadcast();
  final StreamController<AITraderInfo> _aiTraderInfoController = 
      StreamController<AITraderInfo>.broadcast();
  final StreamController<WebSocketConnectionState> _connectionStateController = 
      StreamController<WebSocketConnectionState>.broadcast();
  final StreamController<LeaderboardUpdateData> _leaderboardUpdatesController = 
      StreamController<LeaderboardUpdateData>.broadcast();
  final StreamController<NearbyCompetitorsData> _nearbyCompetitorsController = 
      StreamController<NearbyCompetitorsData>.broadcast();
  final StreamController<String> _errorController = 
      StreamController<String>.broadcast();
  
  // Statistics
  int _messagesReceived = 0;
  int _messagesSent = 0;
  DateTime? _lastHeartbeat;
  DateTime? _connectionStartTime;
  
  // Public streams
  Stream<List<LeaderboardEntry>> get leaderboardStream => _leaderboardController.stream;
  Stream<LiveTrade> get liveTradesStream => _liveTradesController.stream;
  Stream<Achievement> get achievementsStream => _achievementsController.stream;
  Stream<TournamentEvent> get tournamentEventsStream => _tournamentEventsController.stream;
  Stream<AITraderInfo> get aiTraderInfoStream => _aiTraderInfoController.stream;
  Stream<WebSocketConnectionState> get connectionStateStream => _connectionStateController.stream;
  Stream<LeaderboardUpdateData> get leaderboardUpdatesStream => _leaderboardUpdatesController.stream;
  Stream<NearbyCompetitorsData> get nearbyCompetitorsStream => _nearbyCompetitorsController.stream;
  Stream<String> get errorStream => _errorController.stream;
  
  // Getters
  WebSocketConnectionState get connectionState => _connectionState;
  String? get currentTournamentId => _currentTournamentId;
  bool get isConnected => _connectionState == WebSocketConnectionState.connected || 
                         _connectionState == WebSocketConnectionState.authenticated;
  int get messagesReceived => _messagesReceived;
  int get messagesSent => _messagesSent;
  DateTime? get lastHeartbeat => _lastHeartbeat;
  Duration? get connectionDuration => _connectionStartTime != null 
      ? DateTime.now().difference(_connectionStartTime!) 
      : null;
  
  Future<void> connectToTournament(String tournamentId, {String? authToken}) async {
    if (_connectionState == WebSocketConnectionState.connecting) {
      debugPrint('🟡 Already connecting to WebSocket');
      return;
    }
    
    _currentTournamentId = tournamentId;
    _authToken = authToken;
    _connectionStartTime = DateTime.now();
    
    await _connect();
  }
  
  Future<void> _connect() async {
    if (_currentTournamentId == null) return;
    
    try {
      _setConnectionState(WebSocketConnectionState.connecting);
      
      // Build WebSocket URL with optional auth
      final uriBuilder = Uri.parse('$_wsBaseUrl/ws/tournament/$_currentTournamentId');
      final uri = _authToken != null 
          ? uriBuilder.replace(queryParameters: {'token': _authToken!})
          : uriBuilder;
      
      debugPrint('🚀 Connecting to WebSocket: ${uri.toString()}');
      
      // Set connection timeout
      _connectionTimeoutTimer?.cancel();
      _connectionTimeoutTimer = Timer(Duration(seconds: _connectionTimeoutSeconds), () {
        if (_connectionState == WebSocketConnectionState.connecting) {
          debugPrint('⏰ WebSocket connection timeout');
          _handleConnectionError('Connection timeout');
        }
      });
      
      // Create WebSocket connection
      _channel = IOWebSocketChannel.connect(uri, 
        headers: {
          'User-Agent': 'AstraTrade Mobile App',
        },
      );
      
      // Listen to WebSocket messages
      _channel!.stream.listen(
        _handleMessage,
        onError: _handleError,
        onDone: _handleDisconnect,
        cancelOnError: false,
      );
      
      // Start heartbeat timer
      _startHeartbeat();
      
      debugPrint('✅ WebSocket connection established');
      
    } catch (e) {
      debugPrint('❌ WebSocket connection error: $e');
      _handleConnectionError(e.toString());
    }
  }
  
  void _setConnectionState(WebSocketConnectionState state) {
    if (_connectionState != state) {
      _connectionState = state;
      _connectionStateController.add(state);
      debugPrint('🔄 WebSocket state changed: ${state.toString()}');
    }
  }
  
  void _handleMessage(dynamic message) {
    try {
      _messagesReceived++;
      final data = json.decode(message.toString());
      final messageType = data['type'] as String;
      
      debugPrint('📥 WebSocket message: $messageType');
      
      switch (messageType) {
        case 'initial_state':
          _handleInitialState(data['data']);
          _setConnectionState(WebSocketConnectionState.connected);
          _connectionTimeoutTimer?.cancel();
          _reconnectAttempts = 0; // Reset on successful connection
          break;
          
        case 'leaderboard_update':
          _handleLeaderboardUpdate(data['data']);
          break;
          
        case 'live_trade':
          _handleLiveTrade(data['data']);
          break;
          
        case 'achievement_unlocked':
          _handleAchievement(data['data']);
          break;
          
        case 'tournament_event':
          _handleTournamentEvent(data['data']);
          break;
          
        case 'heartbeat':
          _handleHeartbeat(data['data']);
          break;
          
        case 'nearby_competitors':
          _handleNearbyCompetitors(data['data']);
          break;
          
        case 'ai_trader_info':
          _handleAITraderInfo(data['data']);
          break;
          
        case 'detailed_leaderboard':
          _handleDetailedLeaderboard(data['data']);
          break;
          
        case 'authentication_success':
          _handleAuthenticationSuccess(data['data']);
          break;
          
        case 'error':
          _handleErrorMessage(data['data']);
          break;
          
        default:
          debugPrint('🟡 Unknown WebSocket message type: $messageType');
      }
    } catch (e) {
      debugPrint('❌ Error parsing WebSocket message: $e');
      debugPrint('Raw message: $message');
    }
  }
  
  void _handleInitialState(Map<String, dynamic> data) {
    try {
      // Parse and emit initial leaderboard
      if (data['leaderboard'] != null) {
        final leaderboard = (data['leaderboard'] as List)
          .map((entry) => LeaderboardEntry.fromJson(entry))
          .toList();
        _leaderboardController.add(leaderboard);
      }
      
      // Handle recent trades if available
      if (data['recent_trades'] != null) {
        final recentTrades = (data['recent_trades'] as List)
          .map((trade) => LiveTrade.fromJson(trade))
          .toList();
        for (final trade in recentTrades) {
          _liveTradesController.add(trade);
        }
      }
      
      debugPrint('📊 Initial state loaded: ${data['leaderboard']?.length ?? 0} leaderboard entries');
      
    } catch (e) {
      debugPrint('❌ Error handling initial state: $e');
    }
  }
  
  void _handleLeaderboardUpdate(Map<String, dynamic> data) {
    try {
      final update = LeaderboardUpdateData.fromJson(data);
      _leaderboardUpdatesController.add(update);
      
      debugPrint('📊 Leaderboard update: ${update.username} -> Rank ${update.newRank} (Score: ${update.newScore})');
      
    } catch (e) {
      debugPrint('❌ Error handling leaderboard update: $e');
    }
  }
  
  void _handleLiveTrade(Map<String, dynamic> data) {
    try {
      final trade = LiveTrade.fromJson(data);
      _liveTradesController.add(trade);
      
      debugPrint('💹 Live trade: ${trade.username} ${trade.side} ${trade.symbol} \$${trade.amount}');
      
    } catch (e) {
      debugPrint('❌ Error handling live trade: $e');
    }
  }
  
  void _handleAchievement(Map<String, dynamic> data) {
    try {
      final achievement = Achievement.fromJson(data);
      _achievementsController.add(achievement);
      
      debugPrint('🏆 Achievement unlocked: ${achievement.title} by ${achievement.username}');
      
    } catch (e) {
      debugPrint('❌ Error handling achievement: $e');
    }
  }
  
  void _handleTournamentEvent(Map<String, dynamic> data) {
    try {
      final event = TournamentEvent.fromJson(data);
      _tournamentEventsController.add(event);
      
      debugPrint('🎯 Tournament event: ${event.title}');
      
    } catch (e) {
      debugPrint('❌ Error handling tournament event: $e');
    }
  }
  
  void _handleHeartbeat(Map<String, dynamic> data) {
    _lastHeartbeat = DateTime.now();
    
    // Send heartbeat response
    _sendMessage({
      'type': 'heartbeat_response',
      'data': {
        'received_at': DateTime.now().millisecondsSinceEpoch / 1000,
        'client_time': DateTime.now().millisecondsSinceEpoch / 1000,
      }
    });
  }
  
  void _handleNearbyCompetitors(Map<String, dynamic> data) {
    try {
      final competitors = NearbyCompetitorsData.fromJson(data);
      _nearbyCompetitorsController.add(competitors);
      
      debugPrint('👥 Nearby competitors: ${competitors.competitors.length} users');
      
    } catch (e) {
      debugPrint('❌ Error handling nearby competitors: $e');
    }
  }
  
  void _handleAITraderInfo(Map<String, dynamic> data) {
    try {
      final aiInfo = AITraderInfo.fromJson(data);
      _aiTraderInfoController.add(aiInfo);
      
      debugPrint('🤖 AI trader info: ${aiInfo.name} (${aiInfo.strategy})');
      
    } catch (e) {
      debugPrint('❌ Error handling AI trader info: $e');
    }
  }
  
  void _handleDetailedLeaderboard(Map<String, dynamic> data) {
    try {
      if (data['leaderboard'] != null) {
        final leaderboard = (data['leaderboard'] as List)
          .map((entry) => LeaderboardEntry.fromJson(entry))
          .toList();
        _leaderboardController.add(leaderboard);
      }
      
      debugPrint('📊 Detailed leaderboard: ${data['total_participants']} participants');
      
    } catch (e) {
      debugPrint('❌ Error handling detailed leaderboard: $e');
    }
  }
  
  void _handleAuthenticationSuccess(Map<String, dynamic> data) {
    _setConnectionState(WebSocketConnectionState.authenticated);
    debugPrint('🔐 WebSocket authentication successful');
  }
  
  void _handleErrorMessage(Map<String, dynamic> data) {
    final errorMessage = data['error_message'] ?? 'Unknown error';
    _errorController.add(errorMessage);
    debugPrint('❌ WebSocket error: $errorMessage');
  }
  
  void _handleError(error) {
    debugPrint('❌ WebSocket error: $error');
    _handleConnectionError(error.toString());
  }
  
  void _handleDisconnect() {
    debugPrint('🔌 WebSocket disconnected');
    _setConnectionState(WebSocketConnectionState.disconnected);
    _scheduleReconnect();
  }
  
  void _handleConnectionError(String error) {
    _setConnectionState(WebSocketConnectionState.error);
    _errorController.add(error);
    _connectionTimeoutTimer?.cancel();
    _scheduleReconnect();
  }
  
  void _scheduleReconnect() {
    if (_reconnectTimer?.isActive ?? false) return;
    if (_reconnectAttempts >= _maxReconnectAttempts) {
      debugPrint('🛑 Max reconnection attempts reached');
      _errorController.add('Failed to reconnect after $_maxReconnectAttempts attempts');
      return;
    }
    
    _reconnectAttempts++;
    final delay = _calculateReconnectDelay(_reconnectAttempts);
    
    debugPrint('🔄 Scheduling reconnection attempt $_reconnectAttempts in ${delay.inSeconds}s');
    _setConnectionState(WebSocketConnectionState.reconnecting);
    
    _reconnectTimer = Timer(delay, () {
      if (_currentTournamentId != null) {
        _connect();
      }
    });
  }
  
  Duration _calculateReconnectDelay(int attempt) {
    // Exponential backoff with jitter: base delay of 2^attempt seconds + random jitter
    final baseDelay = pow(2, min(attempt, 6)).toInt(); // Cap at 64 seconds
    final jitter = Random().nextInt(1000); // 0-1000ms jitter
    return Duration(seconds: baseDelay, milliseconds: jitter);
  }
  
  void _startHeartbeat() {
    _heartbeatTimer?.cancel();
    _heartbeatTimer = Timer.periodic(
      Duration(seconds: _heartbeatIntervalSeconds),
      (_) => _checkConnection(),
    );
  }
  
  void _checkConnection() {
    if (_lastHeartbeat != null) {
      final timeSinceLastHeartbeat = DateTime.now().difference(_lastHeartbeat!);
      if (timeSinceLastHeartbeat.inSeconds > _heartbeatIntervalSeconds * 2) {
        debugPrint('💔 Heartbeat timeout - connection may be stale');
        _handleConnectionError('Heartbeat timeout');
        return;
      }
    }
    
    // Connection is healthy, no action needed
  }
  
  void _sendMessage(Map<String, dynamic> message) {
    if (_channel != null && isConnected) {
      try {
        _channel!.sink.add(json.encode(message));
        _messagesSent++;
        debugPrint('📤 Sent message: ${message['type']}');
      } catch (e) {
        debugPrint('❌ Error sending message: $e');
        _handleConnectionError(e.toString());
      }
    } else {
      debugPrint('⚠️ Cannot send message - WebSocket not connected');
    }
  }
  
  // Public message sending methods
  void requestNearbyCompetitors({int radius = 5}) {
    _sendMessage({
      'type': 'get_nearby_competitors',
      'data': {'radius': radius}
    });
  }
  
  void requestAITraderInfo(String aiId) {
    _sendMessage({
      'type': 'get_ai_trader_info',
      'data': {'ai_id': aiId}
    });
  }
  
  void requestDetailedLeaderboard({int start = 0, int limit = 50}) {
    _sendMessage({
      'type': 'get_detailed_leaderboard',
      'data': {
        'start': start,
        'limit': limit
      }
    });
  }
  
  void authenticate(String token) {
    _authToken = token;
    _sendMessage({
      'type': 'authenticate',
      'data': {'token': token}
    });
  }
  
  void disconnect() {
    debugPrint('🔌 Manually disconnecting WebSocket');
    
    _reconnectTimer?.cancel();
    _heartbeatTimer?.cancel();
    _connectionTimeoutTimer?.cancel();
    
    if (_channel != null) {
      _channel!.sink.close();
      _channel = null;
    }
    
    _setConnectionState(WebSocketConnectionState.disconnected);
    _currentTournamentId = null;
    _authToken = null;
    _reconnectAttempts = 0;
    _connectionStartTime = null;
  }
  
  Map<String, dynamic> getConnectionStats() {
    return {
      'connection_state': _connectionState.toString(),
      'tournament_id': _currentTournamentId,
      'messages_received': _messagesReceived,
      'messages_sent': _messagesSent,
      'reconnect_attempts': _reconnectAttempts,
      'last_heartbeat': _lastHeartbeat?.toIso8601String(),
      'connection_duration': connectionDuration?.inSeconds,
      'is_authenticated': _connectionState == WebSocketConnectionState.authenticated,
    };
  }
  
  void dispose() {
    debugPrint('🗑️ Disposing TournamentWebSocketService');
    
    disconnect();
    
    _leaderboardController.close();
    _liveTradesController.close();
    _achievementsController.close();
    _tournamentEventsController.close();
    _aiTraderInfoController.close();
    _connectionStateController.close();
    _leaderboardUpdatesController.close();
    _nearbyCompetitorsController.close();
    _errorController.close();
  }
  
  // Utility methods for testing and debugging
  void simulateConnectionLoss() {
    if (kDebugMode) {
      debugPrint('🧪 Simulating connection loss for testing');
      _handleDisconnect();
    }
  }
  
  void forceReconnect() {
    if (kDebugMode) {
      debugPrint('🔄 Force reconnecting for testing');
      _reconnectAttempts = 0;
      disconnect();
      if (_currentTournamentId != null) {
        connectToTournament(_currentTournamentId!, authToken: _authToken);
      }
    }
  }
  
  void resetReconnectAttempts() {
    _reconnectAttempts = 0;
    debugPrint('🔄 Reset reconnection attempts');
  }
}