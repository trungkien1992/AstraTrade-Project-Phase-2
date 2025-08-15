/// Trade result model for Extended Exchange API responses
class TradeResult {
  final bool success;
  final String tradeId;
  final String symbol;
  final String side;
  final double requestedAmount;
  final double executedAmount;
  final double executedPrice;
  final String status;
  final DateTime timestamp;
  final bool isLive;
  final Map<String, dynamic>? exchangeResponse;
  final String? error;

  TradeResult({
    required this.success,
    required this.tradeId,
    required this.symbol,
    required this.side,
    required this.requestedAmount,
    required this.executedAmount,
    required this.executedPrice,
    required this.status,
    required this.timestamp,
    this.isLive = false,
    this.exchangeResponse,
    this.error,
  });

  /// Calculate profit/loss if this is a completed trade
  double get profitLoss {
    if (!success || executedAmount == 0) return 0.0;

    // Simplified P&L calculation for demo
    // In production, this would use entry/exit prices
    final marketMovement = 0.5; // Simulated 0.5% market movement
    return side == 'BUY'
        ? (executedAmount * executedPrice * marketMovement / 100)
        : -(executedAmount * executedPrice * marketMovement / 100);
  }

  /// Get return percentage
  double get returnPercentage {
    if (!success || executedAmount == 0) return 0.0;
    final tradeValue = executedAmount * executedPrice;
    return tradeValue > 0 ? (profitLoss / tradeValue) * 100 : 0.0;
  }

  Map<String, dynamic> toJson() => {
    'success': success,
    'trade_id': tradeId,
    'symbol': symbol,
    'side': side,
    'requested_amount': requestedAmount,
    'executed_amount': executedAmount,
    'executed_price': executedPrice,
    'status': status,
    'timestamp': timestamp.toIso8601String(),
    'is_live': isLive,
    'exchange_response': exchangeResponse,
    'error': error,
    'profit_loss': profitLoss,
    'return_percentage': returnPercentage,
  };

  factory TradeResult.fromJson(Map<String, dynamic> json) => TradeResult(
    success: json['success'] ?? false,
    tradeId: json['trade_id'] ?? '',
    symbol: json['symbol'] ?? '',
    side: json['side'] ?? 'BUY',
    requestedAmount: (json['requested_amount'] as num?)?.toDouble() ?? 0.0,
    executedAmount: (json['executed_amount'] as num?)?.toDouble() ?? 0.0,
    executedPrice: (json['executed_price'] as num?)?.toDouble() ?? 0.0,
    status: json['status'] ?? 'UNKNOWN',
    timestamp: DateTime.tryParse(json['timestamp'] ?? '') ?? DateTime.now(),
    isLive: json['is_live'] ?? false,
    exchangeResponse: json['exchange_response'],
    error: json['error'],
  );

  /// Create a successful demo trade result
  factory TradeResult.demo({
    required String symbol,
    required String side,
    required double amount,
  }) {
    final price = _getDemoPrice(symbol);
    return TradeResult(
      success: true,
      tradeId: 'demo_${DateTime.now().millisecondsSinceEpoch}',
      symbol: symbol,
      side: side,
      requestedAmount: amount,
      executedAmount: amount,
      executedPrice: price,
      status: 'FILLED',
      timestamp: DateTime.now(),
      isLive: false,
    );
  }

  /// Get demo price for symbol
  static double _getDemoPrice(String symbol) {
    final prices = {
      'ETH-USD': 3250.50,
      'BTC-USD': 67800.25,
      'STRK-USD': 1.85,
      'USDC-USD': 1.00,
    };
    return prices[symbol] ?? 1.0;
  }
}
