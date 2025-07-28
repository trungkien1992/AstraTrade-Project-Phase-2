import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../api/secure_api_client.dart';

// Environment configuration - placeholder
class EnvironmentConfig {
  static const String apiBaseUrl = 'https://api.astratrade.com';
  static const String wsBaseUrl = 'wss://api.astratrade.com';
  static const bool isDemo = false; // Disable demo mode for real services
  static const bool shouldUseDemoData = false; // Use real Starknet services
}

// Placeholder classes for missing types
class AuthState {
  final String? token;
  final bool isAuthenticated;
  
  const AuthState({this.token, this.isAuthenticated = false});
}

class AuthNotifier extends StateNotifier<AuthState> {
  final Dio dio;
  final FlutterSecureStorage storage;
  
  AuthNotifier({required this.dio, required this.storage}) 
    : super(const AuthState());
  
  Future<void> login(String username, String password) async {
    // Placeholder login implementation
  }
  
  Future<void> logout() async {
    state = const AuthState();
  }
}

class TradingState {
  final List<dynamic> positions;
  final bool isLoading;
  
  const TradingState({this.positions = const [], this.isLoading = false});
}

class TradingNotifier extends StateNotifier<TradingState> {
  final Dio dio;
  final AuthState authState;
  
  TradingNotifier({required this.dio, required this.authState}) 
    : super(const TradingState());
}

class LeaderboardEntry {
  final String id;
  final String name;
  final double score;
  
  LeaderboardEntry({required this.id, required this.name, required this.score});
  
  factory LeaderboardEntry.fromJson(Map<String, dynamic> json) {
    return LeaderboardEntry(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      score: (json['score'] ?? 0).toDouble(),
    );
  }
}

class GameUpdate {
  final String type;
  final Map<String, dynamic> data;
  
  GameUpdate({required this.type, required this.data});
  
  factory GameUpdate.fromJson(Map<String, dynamic> json) {
    return GameUpdate(
      type: json['type'] ?? '',
      data: json['data'] ?? {},
    );
  }
}

// Simple interceptors
class AuthInterceptor extends Interceptor {
  final Ref ref;
  
  AuthInterceptor(this.ref);
  
  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    // Add auth token if available
    handler.next(options);
  }
}

class LoggingInterceptor extends Interceptor {
  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    print('Request: ${options.method} ${options.path}');
    handler.next(options);
  }
  
  @override
  void onResponse(Response response, ResponseInterceptorHandler handler) {
    print('Response: ${response.statusCode}');
    handler.next(response);
  }
  
  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    print('Error: ${err.message}');
    handler.next(err);
  }
}

// Core service providers
final dioProvider = Provider<Dio>((ref) {
  final dio = Dio(BaseOptions(
    baseUrl: EnvironmentConfig.apiBaseUrl,
    connectTimeout: const Duration(seconds: 10),
    receiveTimeout: const Duration(seconds: 10),
  ));
  
  dio.interceptors.add(AuthInterceptor(ref));
  dio.interceptors.add(LoggingInterceptor());
  
  return dio;
});

final secureStorageProvider = Provider<FlutterSecureStorage>((ref) {
  return const FlutterSecureStorage(
    aOptions: AndroidOptions(
      encryptedSharedPreferences: true,
    ),
    iOptions: IOSOptions(),
  );
});

final secureApiClientProvider = Provider<SecureApiClient>((ref) {
  final storage = SecureStorage(ref.watch(secureStorageProvider));
  return SecureApiClient(
    baseUrl: EnvironmentConfig.apiBaseUrl,
    storage: storage,
  );
});

// Feature providers
final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier(
    dio: ref.watch(dioProvider),
    storage: ref.watch(secureStorageProvider),
  );
});

final tradingProvider = StateNotifierProvider<TradingNotifier, TradingState>((ref) {
  return TradingNotifier(
    dio: ref.watch(dioProvider),
    authState: ref.watch(authProvider),
  );
});

final leaderboardProvider = FutureProvider.autoDispose<List<LeaderboardEntry>>((ref) async {
  final dio = ref.watch(dioProvider);
  final response = await dio.get('/api/leaderboard');
  return (response.data as List)
      .map((json) => LeaderboardEntry.fromJson(json))
      .toList();
});

// WebSocket provider for real-time updates
final webSocketProvider = StreamProvider.autoDispose<GameUpdate>((ref) async* {
  final authState = ref.watch(authProvider);
  if (authState.token == null) return;
  
  final channel = WebSocketChannel.connect(
    Uri.parse('${EnvironmentConfig.wsBaseUrl}/ws?token=${authState.token}'),
  );
  
  ref.onDispose(() => channel.sink.close());
  
  await for (final message in channel.stream) {
    yield GameUpdate.fromJson(jsonDecode(message));
  }
});