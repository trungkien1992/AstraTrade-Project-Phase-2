import 'dart:math';
import '../models/simple_trade.dart';

class SimpleTradingService {
  static const List<String> _symbols = [
    'AAPL', 'TSLA', 'AMZN', 'GOOGL', 'MSFT', 'NVDA', 'META', 'NFLX'
  ];

  static const List<double> _amounts = [50, 100, 250, 500, 1000];

  /// Simulates a trade outcome with realistic market behavior
  /// Returns profit/loss percentage between -15% and +15%
  static double simulateTradeOutcome() {
    final random = Random();
    
    // 55% chance of profit (slightly bullish bias)
    final isProfit = random.nextDouble() > 0.45;
    
    if (isProfit) {
      // Profit: 0.1% to 15%
      return random.nextDouble() * 14.9 + 0.1;
    } else {
      // Loss: -0.1% to -15%
      return -(random.nextDouble() * 14.9 + 0.1);
    }
  }

  /// Creates a new trade with random parameters
  static SimpleTrade createRandomTrade() {
    final random = Random();
    
    return SimpleTrade(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      amount: _amounts[random.nextInt(_amounts.length)],
      direction: random.nextBool() ? 'BUY' : 'SELL',
      symbol: _symbols[random.nextInt(_symbols.length)],
      timestamp: DateTime.now(),
    );
  }

  /// Creates a trade with user-specified parameters
  static SimpleTrade createTrade({
    required double amount,
    required String direction,
    String? symbol,
  }) {
    final random = Random();
    
    return SimpleTrade(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      amount: amount,
      direction: direction.toUpperCase(),
      symbol: symbol ?? _symbols[random.nextInt(_symbols.length)],
      timestamp: DateTime.now(),
    );
  }

  /// Completes a trade by adding profit/loss
  static SimpleTrade completeTrade(SimpleTrade trade) {
    final outcomePercentage = simulateTradeOutcome();
    final profitLoss = trade.amount * (outcomePercentage / 100);
    
    return trade.copyWith(
      profitLoss: profitLoss,
      isCompleted: true,
    );
  }

  /// Simulates 24-hour delayed trade completion
  static Future<SimpleTrade> completeTradeDelayed(SimpleTrade trade) async {
    // In MVP, we'll complete immediately for better UX
    // In production, this would wait 24 hours
    await Future.delayed(const Duration(seconds: 2));
    return completeTrade(trade);
  }

  /// Gets realistic market message based on outcome
  static String getTradeMessage(SimpleTrade trade) {
    if (!trade.isCompleted || trade.profitLoss == null) {
      return 'Trade pending...';
    }

    final percentage = trade.profitLossPercentage;
    final isProfit = percentage > 0;
    final symbol = trade.symbol;
    
    if (isProfit) {
      if (percentage > 10) {
        return '🚀 Excellent trade on $symbol! +${percentage.toStringAsFixed(1)}%';
      } else if (percentage > 5) {
        return '📈 Great trade on $symbol! +${percentage.toStringAsFixed(1)}%';
      } else {
        return '✅ Nice trade on $symbol! +${percentage.toStringAsFixed(1)}%';
      }
    } else {
      if (percentage < -10) {
        return '📉 Tough break on $symbol. ${percentage.toStringAsFixed(1)}%';
      } else if (percentage < -5) {
        return '⚠️ Small loss on $symbol. ${percentage.toStringAsFixed(1)}%';
      } else {
        return '🔻 Minor loss on $symbol. ${percentage.toStringAsFixed(1)}%';
      }
    }
  }

  /// Gets available trading symbols
  static List<String> getAvailableSymbols() => List.from(_symbols);

  /// Gets available trade amounts
  static List<double> getAvailableAmounts() => List.from(_amounts);
}