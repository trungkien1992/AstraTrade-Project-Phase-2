import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';

/// Service for tracking trading statistics like win streaks, total trades, and win rates
class TradingStatsService {
  static const String _winStreakKey = 'trading_win_streak';
  static const String _totalTradesKey = 'trading_total_trades';
  static const String _totalWinsKey = 'trading_total_wins';
  static const String _lastTradeResultKey = 'trading_last_result';
  static const String _tradingHistoryKey = 'trading_history';

  /// Get current win streak
  Future<int> getWinStreak() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getInt(_winStreakKey) ?? 0;
  }

  /// Get total trades count
  Future<int> getTotalTrades() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getInt(_totalTradesKey) ?? 0;
  }

  /// Get total wins count
  Future<int> getTotalWins() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getInt(_totalWinsKey) ?? 0;
  }

  /// Calculate win rate as percentage (0.0 to 1.0)
  Future<double> getWinRate() async {
    final totalTrades = await getTotalTrades();
    final totalWins = await getTotalWins();

    if (totalTrades == 0) return 0.0;
    return totalWins / totalTrades;
  }

  /// Record a trade result and update statistics
  Future<TradingStats> recordTradeResult({
    required bool wasSuccessful,
    required double amount,
    String? symbol,
  }) async {
    final prefs = await SharedPreferences.getInstance();

    // Update total trades
    final totalTrades = await getTotalTrades();
    await prefs.setInt(_totalTradesKey, totalTrades + 1);

    // Update total wins if successful
    if (wasSuccessful) {
      final totalWins = await getTotalWins();
      await prefs.setInt(_totalWinsKey, totalWins + 1);
    }

    // Update win streak
    final currentStreak = await getWinStreak();
    int newStreak;
    if (wasSuccessful) {
      newStreak = currentStreak + 1;
    } else {
      newStreak = 0; // Reset streak on loss
    }
    await prefs.setInt(_winStreakKey, newStreak);

    // Store last trade result
    await prefs.setBool(_lastTradeResultKey, wasSuccessful);

    // Add to trading history (keep last 100 trades)
    await _addToTradingHistory(wasSuccessful, amount, symbol);

    return TradingStats(
      winStreak: newStreak,
      totalTrades: totalTrades + 1,
      totalWins: wasSuccessful ? await getTotalWins() : await getTotalWins(),
      winRate: await getWinRate(),
    );
  }

  /// Get current trading statistics
  Future<TradingStats> getCurrentStats() async {
    return TradingStats(
      winStreak: await getWinStreak(),
      totalTrades: await getTotalTrades(),
      totalWins: await getTotalWins(),
      winRate: await getWinRate(),
    );
  }

  /// Add trade to history (internal method)
  Future<void> _addToTradingHistory(
    bool wasSuccessful,
    double amount,
    String? symbol,
  ) async {
    final prefs = await SharedPreferences.getInstance();
    final historyJson = prefs.getString(_tradingHistoryKey) ?? '[]';
    final List<dynamic> history = json.decode(historyJson);

    // Add new trade
    history.add({
      'success': wasSuccessful,
      'amount': amount,
      'symbol': symbol,
      'timestamp': DateTime.now().millisecondsSinceEpoch,
    });

    // Keep only last 100 trades
    if (history.length > 100) {
      history.removeRange(0, history.length - 100);
    }

    await prefs.setString(_tradingHistoryKey, json.encode(history));
  }

  /// Get trading history
  Future<List<TradeRecord>> getTradingHistory() async {
    final prefs = await SharedPreferences.getInstance();
    final historyJson = prefs.getString(_tradingHistoryKey) ?? '[]';
    final List<dynamic> history = json.decode(historyJson);

    return history
        .map((item) => TradeRecord.fromJson(item))
        .toList()
        .reversed
        .toList();
  }

  /// Reset all trading statistics (for testing or fresh start)
  Future<void> resetStats() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_winStreakKey);
    await prefs.remove(_totalTradesKey);
    await prefs.remove(_totalWinsKey);
    await prefs.remove(_lastTradeResultKey);
    await prefs.remove(_tradingHistoryKey);
  }
}

/// Model for trading statistics
class TradingStats {
  final int winStreak;
  final int totalTrades;
  final int totalWins;
  final double winRate;

  TradingStats({
    required this.winStreak,
    required this.totalTrades,
    required this.totalWins,
    required this.winRate,
  });

  int get totalLosses => totalTrades - totalWins;

  @override
  String toString() {
    return 'TradingStats(streak: $winStreak, trades: $totalTrades, wins: $totalWins, rate: ${(winRate * 100).toStringAsFixed(1)}%)';
  }
}

/// Model for individual trade record
class TradeRecord {
  final bool wasSuccessful;
  final double amount;
  final String? symbol;
  final DateTime timestamp;

  TradeRecord({
    required this.wasSuccessful,
    required this.amount,
    this.symbol,
    required this.timestamp,
  });

  factory TradeRecord.fromJson(Map<String, dynamic> json) {
    return TradeRecord(
      wasSuccessful: json['success'] ?? false,
      amount: (json['amount'] ?? 0.0).toDouble(),
      symbol: json['symbol'],
      timestamp: DateTime.fromMillisecondsSinceEpoch(json['timestamp'] ?? 0),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'success': wasSuccessful,
      'amount': amount,
      'symbol': symbol,
      'timestamp': timestamp.millisecondsSinceEpoch,
    };
  }
}
