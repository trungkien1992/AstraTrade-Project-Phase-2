import 'dart:convert';

/// Wallet Balance Model
/// Represents the balance information for a wallet
class WalletBalance {
  final String address;
  final double ethBalance;
  final double stellarShards; // Game currency
  final double lumina; // Game currency
  final DateTime lastUpdated;
  final Map<String, double> tokenBalances; // Token symbol -> balance
  final double? usdValue; // Total USD value (optional)

  WalletBalance({
    required this.address,
    required this.ethBalance,
    required this.stellarShards,
    required this.lumina,
    required this.lastUpdated,
    this.tokenBalances = const {},
    this.usdValue,
  });

  /// Create a copy with updated values
  WalletBalance copyWith({
    String? address,
    double? ethBalance,
    double? stellarShards,
    double? lumina,
    DateTime? lastUpdated,
    Map<String, double>? tokenBalances,
    double? usdValue,
  }) {
    return WalletBalance(
      address: address ?? this.address,
      ethBalance: ethBalance ?? this.ethBalance,
      stellarShards: stellarShards ?? this.stellarShards,
      lumina: lumina ?? this.lumina,
      lastUpdated: lastUpdated ?? this.lastUpdated,
      tokenBalances: tokenBalances ?? this.tokenBalances,
      usdValue: usdValue ?? this.usdValue,
    );
  }

  /// Convert to JSON for storage
  String toJson() {
    return jsonEncode({
      'address': address,
      'ethBalance': ethBalance,
      'stellarShards': stellarShards,
      'lumina': lumina,
      'lastUpdated': lastUpdated.millisecondsSinceEpoch,
      'tokenBalances': tokenBalances,
      'usdValue': usdValue,
    });
  }

  /// Create from JSON
  factory WalletBalance.fromJson(String jsonStr) {
    final json = jsonDecode(jsonStr) as Map<String, dynamic>;
    return WalletBalance(
      address: json['address'] as String,
      ethBalance: (json['ethBalance'] as num).toDouble(),
      stellarShards: (json['stellarShards'] as num).toDouble(),
      lumina: (json['lumina'] as num).toDouble(),
      lastUpdated: DateTime.fromMillisecondsSinceEpoch(json['lastUpdated'] as int),
      tokenBalances: Map<String, double>.from(
        (json['tokenBalances'] as Map<String, dynamic>? ?? {})
          .map((key, value) => MapEntry(key, (value as num).toDouble())),
      ),
      usdValue: (json['usdValue'] as num?)?.toDouble(),
    );
  }

  /// Create empty balance
  factory WalletBalance.empty(String address) {
    return WalletBalance(
      address: address,
      ethBalance: 0.0,
      stellarShards: 100.0, // Welcome bonus
      lumina: 0.0,
      lastUpdated: DateTime.now(),
      tokenBalances: {},
      usdValue: 0.0,
    );
  }

  /// Get total portfolio value in ETH
  double getTotalETHValue() {
    double total = ethBalance;
    
    // Add token values (would need price conversion in production)
    for (final balance in tokenBalances.values) {
      total += balance * 0.001; // Mock conversion rate
    }
    
    return total;
  }

  /// Get formatted ETH balance
  String getFormattedETHBalance({int decimals = 4}) {
    return '${ethBalance.toStringAsFixed(decimals)} ETH';
  }

  /// Get formatted Stellar Shards balance
  String getFormattedStellarShards() {
    if (stellarShards >= 1000000) {
      return '${(stellarShards / 1000000).toStringAsFixed(1)}M';
    } else if (stellarShards >= 1000) {
      return '${(stellarShards / 1000).toStringAsFixed(1)}K';
    } else {
      return stellarShards.toStringAsFixed(0);
    }
  }

  /// Get formatted Lumina balance
  String getFormattedLumina() {
    if (lumina >= 1000000) {
      return '${(lumina / 1000000).toStringAsFixed(1)}M';
    } else if (lumina >= 1000) {
      return '${(lumina / 1000).toStringAsFixed(1)}K';
    } else {
      return lumina.toStringAsFixed(0);
    }
  }

  /// Get formatted USD value
  String getFormattedUSDValue() {
    if (usdValue == null) return '--';
    
    if (usdValue! >= 1000000) {
      return '\$${(usdValue! / 1000000).toStringAsFixed(2)}M';
    } else if (usdValue! >= 1000) {
      return '\$${(usdValue! / 1000).toStringAsFixed(2)}K';
    } else {
      return '\$${usdValue!.toStringAsFixed(2)}';
    }
  }

  /// Get token balance by symbol
  double getTokenBalance(String symbol) {
    return tokenBalances[symbol] ?? 0.0;
  }

  /// Check if wallet has sufficient ETH balance
  bool hasSufficientETH(double requiredAmount) {
    return ethBalance >= requiredAmount;
  }

  /// Check if wallet has sufficient token balance
  bool hasSufficientToken(String symbol, double requiredAmount) {
    final balance = getTokenBalance(symbol);
    return balance >= requiredAmount;
  }

  /// Check if wallet has sufficient Stellar Shards
  bool hasSufficientStellarShards(double requiredAmount) {
    return stellarShards >= requiredAmount;
  }

  /// Check if wallet has sufficient Lumina
  bool hasSufficientLumina(double requiredAmount) {
    return lumina >= requiredAmount;
  }

  /// Check if balance data is recent
  bool isRecent({Duration maxAge = const Duration(minutes: 5)}) {
    return DateTime.now().difference(lastUpdated) <= maxAge;
  }

  /// Get all non-zero token balances
  Map<String, double> getNonZeroTokenBalances() {
    return Map.fromEntries(
      tokenBalances.entries.where((entry) => entry.value > 0),
    );
  }

  /// Get balance change percentage (requires previous balance)
  double? getBalanceChangePercentage(WalletBalance previousBalance) {
    if (previousBalance.ethBalance == 0) return null;
    
    final change = ethBalance - previousBalance.ethBalance;
    return (change / previousBalance.ethBalance) * 100;
  }

  @override
  String toString() {
    return 'WalletBalance(address: ${address.substring(0, 10)}..., '
           'ETH: ${ethBalance.toStringAsFixed(4)}, '
           'Shards: ${stellarShards.toStringAsFixed(0)}, '
           'Lumina: ${lumina.toStringAsFixed(0)})';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is WalletBalance &&
        other.address == address &&
        other.ethBalance == ethBalance &&
        other.stellarShards == stellarShards &&
        other.lumina == lumina;
  }

  @override
  int get hashCode {
    return Object.hash(address, ethBalance, stellarShards, lumina);
  }
}

/// Balance Change Model
/// Represents a change in wallet balance over time
class BalanceChange {
  final DateTime timestamp;
  final double previousETH;
  final double currentETH;
  final double previousShards;
  final double currentShards;
  final double previousLumina;
  final double currentLumina;
  final String? reason; // Transaction hash or reason for change

  BalanceChange({
    required this.timestamp,
    required this.previousETH,
    required this.currentETH,
    required this.previousShards,
    required this.currentShards,
    required this.previousLumina,
    required this.currentLumina,
    this.reason,
  });

  /// Get ETH balance change
  double get ethChange => currentETH - previousETH;

  /// Get Stellar Shards change
  double get shardsChange => currentShards - previousShards;

  /// Get Lumina change
  double get luminaChange => currentLumina - previousLumina;

  /// Check if this was a positive change
  bool get isPositive => ethChange > 0 || shardsChange > 0 || luminaChange > 0;

  /// Check if this was a negative change
  bool get isNegative => ethChange < 0 || shardsChange < 0 || luminaChange < 0;

  /// Get formatted change string
  String getFormattedChange() {
    final changes = <String>[];
    
    if (ethChange != 0) {
      final sign = ethChange > 0 ? '+' : '';
      changes.add('$sign${ethChange.toStringAsFixed(4)} ETH');
    }
    
    if (shardsChange != 0) {
      final sign = shardsChange > 0 ? '+' : '';
      changes.add('$sign${shardsChange.toStringAsFixed(0)} Shards');
    }
    
    if (luminaChange != 0) {
      final sign = luminaChange > 0 ? '+' : '';
      changes.add('$sign${luminaChange.toStringAsFixed(0)} Lumina');
    }
    
    return changes.join(', ');
  }

  @override
  String toString() {
    return 'BalanceChange(${getFormattedChange()}, reason: $reason)';
  }
}