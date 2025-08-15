/// Order status enum for Extended API integration
enum OrderStatus { pending, filled, partiallyFilled, cancelled, failed }

class SimpleTrade {
  final String id;
  final double amount;
  final String direction; // 'BUY' or 'SELL'
  final String symbol; // 'BTC-USD', 'ETH-USD', etc.
  final DateTime timestamp;
  final double? profitLoss;
  final bool isCompleted;

  // Extended API fields for real trading
  final String? extendedOrderId;
  final OrderStatus? orderStatus;
  final double? fillPrice;
  final double? unrealizedPnL;
  final DateTime? lastUpdate;

  SimpleTrade({
    required this.id,
    required this.amount,
    required this.direction,
    required this.symbol,
    required this.timestamp,
    this.profitLoss,
    this.isCompleted = false,
    // Extended API fields
    this.extendedOrderId,
    this.orderStatus,
    this.fillPrice,
    this.unrealizedPnL,
    this.lastUpdate,
  });

  SimpleTrade copyWith({
    double? profitLoss,
    bool? isCompleted,
    String? extendedOrderId,
    OrderStatus? orderStatus,
    double? fillPrice,
    double? unrealizedPnL,
    DateTime? lastUpdate,
  }) {
    return SimpleTrade(
      id: id,
      amount: amount,
      direction: direction,
      symbol: symbol,
      timestamp: timestamp,
      profitLoss: profitLoss ?? this.profitLoss,
      isCompleted: isCompleted ?? this.isCompleted,
      // Extended API fields
      extendedOrderId: extendedOrderId ?? this.extendedOrderId,
      orderStatus: orderStatus ?? this.orderStatus,
      fillPrice: fillPrice ?? this.fillPrice,
      unrealizedPnL: unrealizedPnL ?? this.unrealizedPnL,
      lastUpdate: lastUpdate ?? this.lastUpdate,
    );
  }

  double get profitLossPercentage {
    if (profitLoss == null || amount == 0) return 0.0;
    return (profitLoss! / amount) * 100;
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'amount': amount,
      'direction': direction,
      'symbol': symbol,
      'timestamp': timestamp.toIso8601String(),
      'profitLoss': profitLoss,
      'isCompleted': isCompleted,
      // Extended API fields
      'extendedOrderId': extendedOrderId,
      'orderStatus': orderStatus?.name,
      'fillPrice': fillPrice,
      'unrealizedPnL': unrealizedPnL,
      'lastUpdate': lastUpdate?.toIso8601String(),
    };
  }

  factory SimpleTrade.fromJson(Map<String, dynamic> json) {
    return SimpleTrade(
      id: json['id'],
      amount: json['amount'].toDouble(),
      direction: json['direction'],
      symbol: json['symbol'],
      timestamp: DateTime.parse(json['timestamp']),
      profitLoss: json['profitLoss']?.toDouble(),
      isCompleted: json['isCompleted'] ?? false,
      // Extended API fields
      extendedOrderId: json['extendedOrderId'],
      orderStatus: json['orderStatus'] != null
          ? OrderStatus.values.firstWhere(
              (e) => e.name == json['orderStatus'],
              orElse: () => OrderStatus.pending,
            )
          : null,
      fillPrice: json['fillPrice']?.toDouble(),
      unrealizedPnL: json['unrealizedPnL']?.toDouble(),
      lastUpdate: json['lastUpdate'] != null
          ? DateTime.parse(json['lastUpdate'])
          : null,
    );
  }

  /// Check if this is a real Extended API trade
  bool get isRealTrade => extendedOrderId != null;

  /// Get current P&L (prioritize unrealized over realized)
  double? get currentPnL => unrealizedPnL ?? profitLoss;

  /// Get trading status display string
  String get statusDisplay {
    if (orderStatus != null) {
      switch (orderStatus!) {
        case OrderStatus.pending:
          return 'Pending';
        case OrderStatus.filled:
          return 'Filled';
        case OrderStatus.partiallyFilled:
          return 'Partially Filled';
        case OrderStatus.cancelled:
          return 'Cancelled';
        case OrderStatus.failed:
          return 'Failed';
      }
    }
    return isCompleted ? 'Completed' : 'Processing';
  }
}
