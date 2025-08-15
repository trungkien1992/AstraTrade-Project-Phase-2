import 'dart:async';
import 'dart:convert';
import 'dart:math';
import 'package:flutter/foundation.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:web_socket_channel/status.dart' as status;
import '../data/extended_exchange_trading_pairs.dart';
import 'extended_exchange_hmac_service.dart';

/// Extended Exchange WebSocket Service for Real-Time Price Feeds
///
/// Provides real-time price updates for all 65+ trading pairs with:
/// - <100ms latency target
/// - Automatic reconnection with exponential backoff
/// - Connection health monitoring
/// - HMAC authentication integration
class ExtendedExchangeWebSocketService {
  static const String _websocketUrl =
      'wss://starknet.sepolia.extended.exchange/stream.extended.exchange/v1';
  static const int _maxReconnectAttempts = 10;
  static const int _maxReconnectDelay = 30000; // 30 seconds
  static const int _pingInterval = 30000; // 30 seconds
  static const int _connectionTimeout = 10000; // 10 seconds

  WebSocketChannel? _channel;
  StreamSubscription? _subscription;
  Timer? _reconnectTimer;
  Timer? _pingTimer;
  Timer? _timeoutTimer;

  int _reconnectAttempts = 0;
  bool _isConnecting = false;
  bool _isManualDisconnect = false;
  DateTime? _lastMessageTime;
  DateTime? _connectionStartTime;

  final Map<String, StreamController<Map<String, dynamic>>> _priceControllers =
      {};
  final StreamController<WebSocketConnectionState> _connectionController =
      StreamController<WebSocketConnectionState>.broadcast();
  final StreamController<Map<String, dynamic>> _allPricesController =
      StreamController<Map<String, dynamic>>.broadcast();

  /// Connection state stream
  Stream<WebSocketConnectionState> get connectionState =>
      _connectionController.stream;

  /// All price updates stream
  Stream<Map<String, dynamic>> get allPriceUpdates =>
      _allPricesController.stream;

  /// Current connection status
  WebSocketConnectionState get currentState => _getCurrentState();

  /// Statistics for monitoring
  Map<String, dynamic> get connectionStats => {
    'reconnect_attempts': _reconnectAttempts,
    'is_connected': _channel != null,
    'last_message_time': _lastMessageTime?.toIso8601String(),
    'connection_start_time': _connectionStartTime?.toIso8601String(),
    'uptime_seconds': _connectionStartTime != null
        ? DateTime.now().difference(_connectionStartTime!).inSeconds
        : 0,
  };

  /// Connect to Extended Exchange WebSocket
  Future<void> connect() async {
    if (_isConnecting) {
      debugPrint('🔄 WebSocket connection already in progress');
      return;
    }

    if (_channel != null) {
      debugPrint('✅ WebSocket already connected');
      return;
    }

    _isConnecting = true;
    _isManualDisconnect = false;
    _connectionStartTime = DateTime.now();

    try {
      debugPrint('🚀 Connecting to Extended Exchange WebSocket...');
      _connectionController.add(WebSocketConnectionState.connecting);

      // Create WebSocket connection with timeout
      _timeoutTimer = Timer(Duration(milliseconds: _connectionTimeout), () {
        debugPrint('⏰ WebSocket connection timeout');
        _handleConnectionFailure(Exception('Connection timeout'));
      });

      _channel = WebSocketChannel.connect(
        Uri.parse(_websocketUrl),
        protocols: ['extended-exchange-v1'],
      );

      _timeoutTimer?.cancel();
      _timeoutTimer = null;

      debugPrint('✅ WebSocket connected successfully');
      _connectionController.add(WebSocketConnectionState.connected);

      _isConnecting = false;
      _reconnectAttempts = 0;
      _lastMessageTime = DateTime.now();

      // Listen to incoming messages
      _subscription = _channel!.stream.listen(
        _handleMessage,
        onError: _handleError,
        onDone: _handleDisconnection,
      );

      // Send authentication and subscription
      await _authenticate();
      await _subscribeToAllPairs();

      // Start ping timer
      _startPingTimer();
    } catch (e) {
      debugPrint('💥 WebSocket connection failed: $e');
      _handleConnectionFailure(e);
    }
  }

  /// Disconnect from WebSocket
  void disconnect() {
    debugPrint('🔌 Manually disconnecting WebSocket');
    _isManualDisconnect = true;
    _cleanup();
    _connectionController.add(WebSocketConnectionState.disconnected);
  }

  /// Get price stream for specific trading pair
  Stream<Map<String, dynamic>> getPriceStream(String symbol) {
    if (!_priceControllers.containsKey(symbol)) {
      _priceControllers[symbol] =
          StreamController<Map<String, dynamic>>.broadcast();
    }
    return _priceControllers[symbol]!.stream;
  }

  /// Subscribe to multiple trading pairs
  Future<void> subscribeToSymbols(List<String> symbols) async {
    if (_channel == null) {
      debugPrint('⚠️ Cannot subscribe: WebSocket not connected');
      return;
    }

    final subscription = {
      'action': 'subscribe',
      'channel': 'ticker',
      'symbols': symbols,
      'timestamp': DateTime.now().millisecondsSinceEpoch,
    };

    debugPrint(
      '📡 Subscribing to ${symbols.length} symbols: ${symbols.take(5).join(', ')}${symbols.length > 5 ? '...' : ''}',
    );
    _channel!.sink.add(json.encode(subscription));
  }

  /// Send authentication message
  Future<void> _authenticate() async {
    try {
      final timestamp = DateTime.now().millisecondsSinceEpoch ~/ 1000;

      // Generate HMAC signature for WebSocket authentication
      final signatureString = ExtendedExchangeHmacService.generateSignature(
        method: 'GET',
        path: '/stream',
        body: '',
        timestamp: timestamp,
        apiSecret: 'websocket_secret', // Would be from secure storage
      );

      final authMessage = {
        'action': 'auth',
        'api_key': 'websocket_api_key', // Would be from secure storage
        'timestamp': timestamp,
        'signature': signatureString,
      };

      debugPrint('🔐 Sending WebSocket authentication');
      _channel!.sink.add(json.encode(authMessage));
    } catch (e) {
      debugPrint('💥 Authentication error: $e');
      // Continue without authentication for now
    }
  }

  /// Subscribe to all 65+ trading pairs
  Future<void> _subscribeToAllPairs() async {
    final allSymbols = ExtendedExchangeTradingPairs.getAllSymbols();

    // Subscribe in batches to avoid overwhelming the server
    const batchSize = 20;
    for (int i = 0; i < allSymbols.length; i += batchSize) {
      final batch = allSymbols.skip(i).take(batchSize).toList();
      await subscribeToSymbols(batch);

      // Small delay between batches
      if (i + batchSize < allSymbols.length) {
        await Future.delayed(Duration(milliseconds: 100));
      }
    }

    debugPrint('✅ Subscribed to all ${allSymbols.length} trading pairs');
  }

  /// Handle incoming WebSocket messages
  void _handleMessage(dynamic rawMessage) {
    try {
      _lastMessageTime = DateTime.now();

      final message =
          json.decode(rawMessage.toString()) as Map<String, dynamic>;
      final messageType = message['type'] ?? message['channel'];

      switch (messageType) {
        case 'ticker':
        case 'price_update':
          _handlePriceUpdate(message);
          break;

        case 'auth_response':
          _handleAuthResponse(message);
          break;

        case 'subscription_response':
          _handleSubscriptionResponse(message);
          break;

        case 'ping':
          _handlePing(message);
          break;

        case 'error':
          _handleServerError(message);
          break;

        default:
          debugPrint('📨 Unknown message type: $messageType');
          debugPrint(
            '   Message: ${message.toString().substring(0, min(200, message.toString().length))}',
          );
      }
    } catch (e) {
      debugPrint('💥 Error processing message: $e');
      debugPrint(
        '   Raw message: ${rawMessage.toString().substring(0, min(200, rawMessage.toString().length))}',
      );
    }
  }

  /// Handle price update messages
  void _handlePriceUpdate(Map<String, dynamic> message) {
    final symbol = message['symbol'] as String?;
    final data = message['data'] as Map<String, dynamic>?;

    if (symbol == null || data == null) {
      debugPrint('⚠️ Invalid price update: missing symbol or data');
      return;
    }

    // Normalize price data
    final normalizedData = {
      'symbol': symbol,
      'price': _parseDouble(data['price'] ?? data['last_price']),
      'change_24h': _parseDouble(data['change_24h'] ?? data['daily_change']),
      'change_percent_24h': _parseDouble(
        data['change_percent_24h'] ?? data['daily_change_percent'],
      ),
      'volume_24h': _parseDouble(data['volume_24h'] ?? data['daily_volume']),
      'high_24h': _parseDouble(data['high_24h'] ?? data['daily_high']),
      'low_24h': _parseDouble(data['low_24h'] ?? data['daily_low']),
      'bid': _parseDouble(data['bid']),
      'ask': _parseDouble(data['ask']),
      'timestamp': DateTime.now().millisecondsSinceEpoch,
      'source': 'websocket',
    };

    // Send to symbol-specific stream
    if (_priceControllers.containsKey(symbol)) {
      _priceControllers[symbol]!.add(normalizedData);
    }

    // Send to all prices stream
    _allPricesController.add(normalizedData);

    if (kDebugMode && Random().nextInt(100) < 5) {
      // Log 5% of messages
      final price = normalizedData['price'];
      final priceStr = price is double
          ? price.toStringAsFixed(4)
          : price.toString();
      debugPrint('📈 Price update: $symbol = \$$priceStr');
    }
  }

  /// Handle authentication response
  void _handleAuthResponse(Map<String, dynamic> message) {
    final success = message['success'] ?? false;
    if (success) {
      debugPrint('✅ WebSocket authentication successful');
    } else {
      debugPrint('❌ WebSocket authentication failed: ${message['error']}');
    }
  }

  /// Handle subscription response
  void _handleSubscriptionResponse(Map<String, dynamic> message) {
    final success = message['success'] ?? false;
    final symbols = message['symbols'] as List?;

    if (success) {
      debugPrint(
        '✅ Subscription successful for ${symbols?.length ?? 0} symbols',
      );
    } else {
      debugPrint('❌ Subscription failed: ${message['error']}');
    }
  }

  /// Handle ping messages
  void _handlePing(Map<String, dynamic> message) {
    // Respond with pong
    final pongMessage = {
      'type': 'pong',
      'timestamp': DateTime.now().millisecondsSinceEpoch,
    };
    _channel?.sink.add(json.encode(pongMessage));
  }

  /// Handle server errors
  void _handleServerError(Map<String, dynamic> message) {
    final error = message['error'] ?? 'Unknown server error';
    debugPrint('🚨 Server error: $error');
  }

  /// Handle WebSocket errors
  void _handleError(dynamic error) {
    debugPrint('💥 WebSocket error: $error');
    _connectionController.add(WebSocketConnectionState.error);
    _scheduleReconnection();
  }

  /// Handle WebSocket disconnection
  void _handleDisconnection() {
    debugPrint('🔌 WebSocket disconnected');
    _connectionController.add(WebSocketConnectionState.disconnected);

    if (!_isManualDisconnect) {
      _scheduleReconnection();
    }
  }

  /// Handle connection failures
  void _handleConnectionFailure(dynamic error) {
    _isConnecting = false;
    _timeoutTimer?.cancel();
    _timeoutTimer = null;

    debugPrint('💥 Connection failure: $error');
    _connectionController.add(WebSocketConnectionState.error);
    _scheduleReconnection();
  }

  /// Schedule automatic reconnection with exponential backoff
  void _scheduleReconnection() {
    if (_isManualDisconnect || _reconnectAttempts >= _maxReconnectAttempts) {
      if (_reconnectAttempts >= _maxReconnectAttempts) {
        debugPrint('🚫 Max reconnection attempts reached');
        _connectionController.add(WebSocketConnectionState.failed);
      }
      return;
    }

    _cleanup();

    _reconnectAttempts++;
    final delay = min(
      _maxReconnectDelay,
      1000 * pow(2, _reconnectAttempts - 1).toInt(),
    );

    debugPrint(
      '🔄 Scheduling reconnection attempt $_reconnectAttempts in ${delay}ms',
    );
    _connectionController.add(WebSocketConnectionState.reconnecting);

    _reconnectTimer = Timer(Duration(milliseconds: delay), () {
      debugPrint(
        '🔄 Attempting reconnection $_reconnectAttempts/$_maxReconnectAttempts',
      );
      connect();
    });
  }

  /// Start ping timer for connection health
  void _startPingTimer() {
    _pingTimer?.cancel();
    _pingTimer = Timer.periodic(Duration(milliseconds: _pingInterval), (timer) {
      if (_channel != null) {
        final pingMessage = {
          'type': 'ping',
          'timestamp': DateTime.now().millisecondsSinceEpoch,
        };
        _channel!.sink.add(json.encode(pingMessage));
      }
    });
  }

  /// Get current connection state
  WebSocketConnectionState _getCurrentState() {
    if (_isConnecting) return WebSocketConnectionState.connecting;
    if (_channel != null) return WebSocketConnectionState.connected;
    if (_reconnectAttempts > 0 && _reconnectAttempts < _maxReconnectAttempts) {
      return WebSocketConnectionState.reconnecting;
    }
    if (_reconnectAttempts >= _maxReconnectAttempts) {
      return WebSocketConnectionState.failed;
    }
    return WebSocketConnectionState.disconnected;
  }

  /// Parse double value safely
  double? _parseDouble(dynamic value) {
    if (value == null) return null;
    if (value is double) return value;
    if (value is int) return value.toDouble();
    if (value is String) return double.tryParse(value);
    return null;
  }

  /// Clean up resources
  void _cleanup() {
    _subscription?.cancel();
    _subscription = null;

    _channel?.sink.close(status.normalClosure);
    _channel = null;

    _reconnectTimer?.cancel();
    _reconnectTimer = null;

    _pingTimer?.cancel();
    _pingTimer = null;

    _timeoutTimer?.cancel();
    _timeoutTimer = null;
  }

  /// Dispose all resources
  void dispose() {
    debugPrint('🧹 Disposing WebSocket service');
    _isManualDisconnect = true;
    _cleanup();

    // Close all stream controllers
    for (final controller in _priceControllers.values) {
      controller.close();
    }
    _priceControllers.clear();

    _connectionController.close();
    _allPricesController.close();
  }
}

/// WebSocket connection states
enum WebSocketConnectionState {
  disconnected,
  connecting,
  connected,
  reconnecting,
  error,
  failed,
}

/// Extension for connection state display
extension WebSocketConnectionStateExtension on WebSocketConnectionState {
  String get displayName {
    switch (this) {
      case WebSocketConnectionState.disconnected:
        return 'Disconnected';
      case WebSocketConnectionState.connecting:
        return 'Connecting';
      case WebSocketConnectionState.connected:
        return 'Connected';
      case WebSocketConnectionState.reconnecting:
        return 'Reconnecting';
      case WebSocketConnectionState.error:
        return 'Error';
      case WebSocketConnectionState.failed:
        return 'Failed';
    }
  }

  bool get isConnected => this == WebSocketConnectionState.connected;
  bool get isConnecting => this == WebSocketConnectionState.connecting;
  bool get hasError =>
      this == WebSocketConnectionState.error ||
      this == WebSocketConnectionState.failed;
}
