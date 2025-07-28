import 'dart:convert';
import 'package:http/http.dart' as http;

class BackendApiException implements Exception {
  final String message;
  BackendApiException(this.message);
  @override
  String toString() => 'BackendApiException: $message';
}

class BackendUser {
  final int id;
  final String username;
  final int xp;
  final int level;
  BackendUser({required this.id, required this.username, required this.xp, required this.level});
  factory BackendUser.fromJson(Map<String, dynamic> json) => BackendUser(
    id: json['id'],
    username: json['username'],
    xp: json['xp'],
    level: json['level'],
  );
}

class BackendLoginResponse {
  final int userId;
  final String username;
  final String token;
  BackendLoginResponse({required this.userId, required this.username, required this.token});
  factory BackendLoginResponse.fromJson(Map<String, dynamic> json) => BackendLoginResponse(
    userId: json['user_id'],
    username: json['username'],
    token: json['token'],
  );
}

class BackendTradeResult {
  final String outcome;
  final double profitPercentage;
  final String message;
  final int xpGained;
  BackendTradeResult({required this.outcome, required this.profitPercentage, required this.message, required this.xpGained});
  factory BackendTradeResult.fromJson(Map<String, dynamic> json) => BackendTradeResult(
    outcome: json['outcome'],
    profitPercentage: (json['profit_percentage'] as num).toDouble(),
    message: json['message'],
    xpGained: json['xp_gained'],
  );
}

class BackendLeaderboardEntry {
  final int userId;
  final String username;
  final int xp;
  final int level;
  BackendLeaderboardEntry({required this.userId, required this.username, required this.xp, required this.level});
  factory BackendLeaderboardEntry.fromJson(Map<String, dynamic> json) => BackendLeaderboardEntry(
    userId: json['user_id'],
    username: json['username'],
    xp: json['xp'],
    level: json['level'],
  );
}

class AstraTradeBackendClient {
  static const String baseUrl = 'http://localhost:8002';
  final http.Client _httpClient;
  AstraTradeBackendClient({http.Client? httpClient}) : _httpClient = httpClient ?? http.Client();

  Future<BackendUser> register(String username, String password) async {
    final uri = Uri.parse('$baseUrl/register');
    final response = await _httpClient.post(uri,
      headers: {'Content-Type': 'application/json'},
      body: json.encode({'username': username, 'password': password}),
    );
    if (response.statusCode == 200) {
      return BackendUser.fromJson(json.decode(response.body));
    } else {
      throw BackendApiException(response.body);
    }
  }

  Future<BackendLoginResponse> login(String username, String password) async {
    final uri = Uri.parse('$baseUrl/login');
    final response = await _httpClient.post(uri,
      headers: {'Content-Type': 'application/json'},
      body: json.encode({'username': username, 'password': password}),
    );
    if (response.statusCode == 200) {
      return BackendLoginResponse.fromJson(json.decode(response.body));
    } else {
      throw BackendApiException(response.body);
    }
  }

  Future<List<BackendUser>> getUsers() async {
    final uri = Uri.parse('$baseUrl/users');
    final response = await _httpClient.get(uri);
    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body);
      return data.map((e) => BackendUser.fromJson(e)).toList();
    } else {
      throw BackendApiException(response.body);
    }
  }

  Future<BackendTradeResult> placeTrade({required int userId, required String asset, required String direction, required double amount}) async {
    final uri = Uri.parse('$baseUrl/trade');
    final response = await _httpClient.post(uri,
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'user_id': userId,
        'asset': asset,
        'direction': direction,
        'amount': amount,
      }),
    );
    if (response.statusCode == 200) {
      return BackendTradeResult.fromJson(json.decode(response.body));
    } else {
      throw BackendApiException(response.body);
    }
  }

  Future<List<BackendLeaderboardEntry>> getLeaderboard() async {
    final uri = Uri.parse('$baseUrl/leaderboard');
    final response = await _httpClient.get(uri);
    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body);
      return data.map((e) => BackendLeaderboardEntry.fromJson(e)).toList();
    } else {
      throw BackendApiException(response.body);
    }
  }

  Future<void> addXp(int userId, int amount) async {
    final uri = Uri.parse('$baseUrl/xp/add');
    final response = await _httpClient.post(uri,
      headers: {'Content-Type': 'application/json'},
      body: json.encode({'user_id': userId, 'amount': amount}),
    );
    if (response.statusCode != 200) {
      throw BackendApiException(response.body);
    }
  }

  void dispose() {
    _httpClient.close();
  }
} 