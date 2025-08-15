class UserProgress {
  final int currentStreak;
  final int longestStreak;
  final int totalTrades;
  final int profitableTrades;
  final double totalProfitLoss;
  final DateTime? lastTradeDate;
  final bool hasSubscription;

  const UserProgress({
    this.currentStreak = 0,
    this.longestStreak = 0,
    this.totalTrades = 0,
    this.profitableTrades = 0,
    this.totalProfitLoss = 0.0,
    this.lastTradeDate,
    this.hasSubscription = false,
  });

  double get winRate {
    if (totalTrades == 0) return 0.0;
    return (profitableTrades / totalTrades) * 100;
  }

  double get averageProfit {
    if (totalTrades == 0) return 0.0;
    return totalProfitLoss / totalTrades;
  }

  bool get isStreakActive {
    if (lastTradeDate == null) return false;
    final now = DateTime.now();
    final difference = now.difference(lastTradeDate!);
    return difference.inHours < 24;
  }

  UserProgress copyWith({
    int? currentStreak,
    int? longestStreak,
    int? totalTrades,
    int? profitableTrades,
    double? totalProfitLoss,
    DateTime? lastTradeDate,
    bool? hasSubscription,
  }) {
    return UserProgress(
      currentStreak: currentStreak ?? this.currentStreak,
      longestStreak: longestStreak ?? this.longestStreak,
      totalTrades: totalTrades ?? this.totalTrades,
      profitableTrades: profitableTrades ?? this.profitableTrades,
      totalProfitLoss: totalProfitLoss ?? this.totalProfitLoss,
      lastTradeDate: lastTradeDate ?? this.lastTradeDate,
      hasSubscription: hasSubscription ?? this.hasSubscription,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'currentStreak': currentStreak,
      'longestStreak': longestStreak,
      'totalTrades': totalTrades,
      'profitableTrades': profitableTrades,
      'totalProfitLoss': totalProfitLoss,
      'lastTradeDate': lastTradeDate?.toIso8601String(),
      'hasSubscription': hasSubscription,
    };
  }

  factory UserProgress.fromJson(Map<String, dynamic> json) {
    return UserProgress(
      currentStreak: json['currentStreak'] ?? 0,
      longestStreak: json['longestStreak'] ?? 0,
      totalTrades: json['totalTrades'] ?? 0,
      profitableTrades: json['profitableTrades'] ?? 0,
      totalProfitLoss: (json['totalProfitLoss'] ?? 0.0).toDouble(),
      lastTradeDate: json['lastTradeDate'] != null
          ? DateTime.parse(json['lastTradeDate'])
          : null,
      hasSubscription: json['hasSubscription'] ?? false,
    );
  }
}
