/// Trade request model for Extended Exchange API
class TradeRequest {
  final String symbol;
  final String side; // 'BUY' or 'SELL'
  final double amount;
  final String? orderType; // 'MARKET' or 'LIMIT'
  final double? limitPrice;
  final String? clientOrderId;
  final bool reduceOnly;
  final bool postOnly;

  TradeRequest({
    required this.symbol,
    required this.side,
    required this.amount,
    this.orderType = 'MARKET',
    this.limitPrice,
    this.clientOrderId,
    this.reduceOnly = false,
    this.postOnly = false,
  });

  Map<String, dynamic> toJson() => {
    'symbol': symbol,
    'side': side,
    'amount': amount,
    'order_type': orderType,
    'limit_price': limitPrice,
    'client_order_id': clientOrderId,
    'reduce_only': reduceOnly,
    'post_only': postOnly,
  };

  factory TradeRequest.fromJson(Map<String, dynamic> json) => TradeRequest(
    symbol: json['symbol'] ?? '',
    side: json['side'] ?? 'BUY',
    amount: (json['amount'] as num?)?.toDouble() ?? 0.0,
    orderType: json['order_type'],
    limitPrice: (json['limit_price'] as num?)?.toDouble(),
    clientOrderId: json['client_order_id'],
    reduceOnly: json['reduce_only'] ?? false,
    postOnly: json['post_only'] ?? false,
  );
}