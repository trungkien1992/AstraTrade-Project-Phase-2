/// Model for user's default trade parameters
class DefaultTradeParameters {
  final double tradeAmount;           // Default trade amount in USD
  final String preferredSymbol;       // Preferred trading symbol
  final double riskLevel;             // Risk level (0.1 to 1.0)
  final bool enableAutoForge;         // Auto-execute forge when parameters are good
  final double maxSlippage;           // Maximum acceptable slippage %
  final Duration confirmationDelay;   // Delay before auto-execution (if enabled)

  const DefaultTradeParameters({
    this.tradeAmount = 100.0,
    this.preferredSymbol = 'BTCUSD',
    this.riskLevel = 0.5,
    this.enableAutoForge = false,
    this.maxSlippage = 2.0,
    this.confirmationDelay = const Duration(seconds: 3),
  });

  DefaultTradeParameters copyWith({
    double? tradeAmount,
    String? preferredSymbol,
    double? riskLevel,
    bool? enableAutoForge,
    double? maxSlippage,
    Duration? confirmationDelay,
  }) {
    return DefaultTradeParameters(
      tradeAmount: tradeAmount ?? this.tradeAmount,
      preferredSymbol: preferredSymbol ?? this.preferredSymbol,
      riskLevel: riskLevel ?? this.riskLevel,
      enableAutoForge: enableAutoForge ?? this.enableAutoForge,
      maxSlippage: maxSlippage ?? this.maxSlippage,
      confirmationDelay: confirmationDelay ?? this.confirmationDelay,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'tradeAmount': tradeAmount,
      'preferredSymbol': preferredSymbol,
      'riskLevel': riskLevel,
      'enableAutoForge': enableAutoForge,
      'maxSlippage': maxSlippage,
      'confirmationDelayMs': confirmationDelay.inMilliseconds,
    };
  }

  factory DefaultTradeParameters.fromJson(Map<String, dynamic> json) {
    return DefaultTradeParameters(
      tradeAmount: (json['tradeAmount'] as num?)?.toDouble() ?? 100.0,
      preferredSymbol: json['preferredSymbol'] as String? ?? 'BTCUSD',
      riskLevel: (json['riskLevel'] as num?)?.toDouble() ?? 0.5,
      enableAutoForge: json['enableAutoForge'] as bool? ?? false,
      maxSlippage: (json['maxSlippage'] as num?)?.toDouble() ?? 2.0,
      confirmationDelay: Duration(
        milliseconds: json['confirmationDelayMs'] as int? ?? 3000,
      ),
    );
  }

  /// Get risk level as display text
  String get riskLevelText {
    if (riskLevel <= 0.3) return 'Conservative';
    if (riskLevel <= 0.7) return 'Moderate';
    return 'Aggressive';
  }

  /// Get risk level color for UI display
  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is DefaultTradeParameters &&
        other.tradeAmount == tradeAmount &&
        other.preferredSymbol == preferredSymbol &&
        other.riskLevel == riskLevel &&
        other.enableAutoForge == enableAutoForge &&
        other.maxSlippage == maxSlippage &&
        other.confirmationDelay == confirmationDelay;
  }

  @override
  int get hashCode {
    return Object.hash(
      tradeAmount,
      preferredSymbol,
      riskLevel,
      enableAutoForge,
      maxSlippage,
      confirmationDelay,
    );
  }

  @override
  String toString() {
    return 'DefaultTradeParameters('
        'amount: \$${tradeAmount.toStringAsFixed(2)}, '
        'symbol: $preferredSymbol, '
        'risk: $riskLevelText, '
        'autoForge: $enableAutoForge'
        ')';
  }
}