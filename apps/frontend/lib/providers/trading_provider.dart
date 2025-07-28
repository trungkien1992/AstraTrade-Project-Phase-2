import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/simple_trade.dart';
import '../models/user_progress.dart';

class TradingState {
  final List<SimpleTrade> trades;
  final UserProgress progress;
  final int freeTrades;

  TradingState({
    this.trades = const [],
    this.progress = const UserProgress(),
    this.freeTrades = 3,
  });

  TradingState copyWith({
    List<SimpleTrade>? trades,
    UserProgress? progress,
    int? freeTrades,
  }) {
    return TradingState(
      trades: trades ?? this.trades,
      progress: progress ?? this.progress,
      freeTrades: freeTrades ?? this.freeTrades,
    );
  }
}

class TradingNotifier extends StateNotifier<TradingState> {
  TradingNotifier() : super(TradingState());

  void addTrade(SimpleTrade trade) {
    state = state.copyWith(
      trades: [...state.trades, trade],
      freeTrades: state.freeTrades > 0 ? state.freeTrades - 1 : 0,
    );
  }

  void updateTrade(SimpleTrade updatedTrade) {
    final trades = state.trades.map((trade) {
      return trade.id == updatedTrade.id ? updatedTrade : trade;
    }).toList();

    // Update progress if trade is completed
    UserProgress updatedProgress = state.progress;
    if (updatedTrade.isCompleted && updatedTrade.profitLoss != null) {
      updatedProgress = _updateProgress(state.progress, updatedTrade);
    }

    state = state.copyWith(
      trades: trades,
      progress: updatedProgress,
    );
  }

  UserProgress _updateProgress(UserProgress current, SimpleTrade completedTrade) {
    final now = DateTime.now();
    final lastTradeWasToday = current.lastTradeDate != null &&
        current.lastTradeDate!.day == now.day &&
        current.lastTradeDate!.month == now.month &&
        current.lastTradeDate!.year == now.year;

    final lastTradeWasYesterday = current.lastTradeDate != null &&
        now.difference(current.lastTradeDate!).inDays == 1;

    int newCurrentStreak = current.currentStreak;
    if (!lastTradeWasToday) {
      if (lastTradeWasYesterday || current.currentStreak == 0) {
        newCurrentStreak = current.currentStreak + 1;
      } else {
        newCurrentStreak = 1; // Reset streak if gap > 1 day
      }
    }

    final newLongestStreak = newCurrentStreak > current.longestStreak
        ? newCurrentStreak
        : current.longestStreak;

    final isProfit = completedTrade.profitLoss! > 0;
    final newProfitableTrades = isProfit
        ? current.profitableTrades + 1
        : current.profitableTrades;

    return current.copyWith(
      currentStreak: newCurrentStreak,
      longestStreak: newLongestStreak,
      totalTrades: current.totalTrades + 1,
      profitableTrades: newProfitableTrades,
      totalProfitLoss: current.totalProfitLoss + completedTrade.profitLoss!,
      lastTradeDate: now,
    );
  }

  bool canTrade() {
    return state.freeTrades > 0 || state.progress.hasSubscription;
  }

  void upgradeToSubscription() {
    state = state.copyWith(
      progress: state.progress.copyWith(hasSubscription: true),
    );
  }

  void updateSubscription(bool hasSubscription) {
    state = state.copyWith(
      progress: state.progress.copyWith(hasSubscription: hasSubscription),
    );
  }

  bool shouldShowRatingPrompt() {
    final progress = state.progress;
    return progress.totalTrades >= 5 && 
           progress.currentStreak >= 3 &&
           progress.winRate > 50.0;
  }

  void resetProgress() {
    state = TradingState();
  }
}

final tradingProvider = StateNotifierProvider<TradingNotifier, TradingState>((ref) {
  return TradingNotifier();
});