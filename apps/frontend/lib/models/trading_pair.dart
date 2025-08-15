/// Trading Pair Model for AstraTrade Exchange V2
///
/// Represents a trading pair (e.g., BTC/USD, ETH/USD) with:
/// - Market information (prices, symbols)
/// - Trading parameters (leverage limits, margins)
/// - Volume and activity data
/// - Mobile-optimized display formatting

import 'dart:convert';

class TradingPair {
  final int pairId;
  final String name;
  final String baseAsset;
  final String quoteAsset;
  final BigInt currentPrice;
  final int maxLeverage;
  final int maintenanceMargin; // In basis points (e.g., 500 = 5%)
  final BigInt fundingRate;
  final bool isActive;
  final BigInt dailyVolume;

  const TradingPair({
    required this.pairId,
    required this.name,
    required this.baseAsset,
    required this.quoteAsset,
    required this.currentPrice,
    required this.maxLeverage,
    required this.maintenanceMargin,
    required this.fundingRate,
    required this.isActive,
    required this.dailyVolume,
  });

  /// Create TradingPair from contract response
  factory TradingPair.fromContractResponse(List<String> response) {
    return TradingPair(
      pairId: int.parse(response[0]),
      name: _feltToString(response[1]),
      baseAsset: _feltToString(response[2]),
      quoteAsset: _feltToString(response[3]),
      currentPrice: BigInt.parse(response[4]),
      maxLeverage: int.parse(response[5]),
      maintenanceMargin: int.parse(response[6]),
      fundingRate: BigInt.parse(response[7]),
      isActive: response[8] == '1',
      dailyVolume: BigInt.parse(response[9]),
    );
  }

  /// Create TradingPair from JSON
  factory TradingPair.fromJson(Map<String, dynamic> json) {
    return TradingPair(
      pairId: json['pairId'] as int,
      name: json['name'] as String,
      baseAsset: json['baseAsset'] as String,
      quoteAsset: json['quoteAsset'] as String,
      currentPrice: BigInt.parse(json['currentPrice'] as String),
      maxLeverage: json['maxLeverage'] as int,
      maintenanceMargin: json['maintenanceMargin'] as int,
      fundingRate: BigInt.parse(json['fundingRate'] as String),
      isActive: json['isActive'] as bool,
      dailyVolume: BigInt.parse(json['dailyVolume'] as String),
    );
  }

  /// Convert to JSON
  Map<String, dynamic> toJson() {
    return {
      'pairId': pairId,
      'name': name,
      'baseAsset': baseAsset,
      'quoteAsset': quoteAsset,
      'currentPrice': currentPrice.toString(),
      'maxLeverage': maxLeverage,
      'maintenanceMargin': maintenanceMargin,
      'fundingRate': fundingRate.toString(),
      'isActive': isActive,
      'dailyVolume': dailyVolume.toString(),
    };
  }

  /// Get formatted current price
  String getFormattedPrice({int decimals = 18, int displayDecimals = 2}) {
    final divisor = BigInt.from(10).pow(decimals);
    final price = currentPrice.toDouble() / divisor.toDouble();
    return '\$${price.toStringAsFixed(displayDecimals)}';
  }

  /// Get price with appropriate decimal places based on value
  String getSmartFormattedPrice({int decimals = 18}) {
    final divisor = BigInt.from(10).pow(decimals);
    final price = currentPrice.toDouble() / divisor.toDouble();

    if (price >= 1000) {
      return '\$${price.toStringAsFixed(0)}';
    } else if (price >= 100) {
      return '\$${price.toStringAsFixed(1)}';
    } else if (price >= 1) {
      return '\$${price.toStringAsFixed(2)}';
    } else if (price >= 0.01) {
      return '\$${price.toStringAsFixed(4)}';
    } else {
      return '\$${price.toStringAsFixed(6)}';
    }
  }

  /// Get formatted daily volume
  String getFormattedDailyVolume({int decimals = 18}) {
    final divisor = BigInt.from(10).pow(decimals);
    final volume = dailyVolume.toDouble() / divisor.toDouble();

    if (volume >= 1000000) {
      return '\$${(volume / 1000000).toStringAsFixed(1)}M';
    } else if (volume >= 1000) {
      return '\$${(volume / 1000).toStringAsFixed(1)}K';
    } else {
      return '\$${volume.toStringAsFixed(0)}';
    }
  }

  /// Get formatted funding rate as percentage
  String getFormattedFundingRate({int decimals = 18}) {
    final divisor = BigInt.from(10).pow(decimals);
    final rate = fundingRate.toDouble() / divisor.toDouble();
    final percentage = rate * 100;

    final sign = percentage >= 0 ? '+' : '';
    return '$sign${percentage.toStringAsFixed(4)}%';
  }

  /// Get maintenance margin as percentage
  String get maintenanceMarginPercentage {
    final percentage = maintenanceMargin / 100.0;
    return '${percentage.toStringAsFixed(1)}%';
  }

  /// Calculate liquidation price for a position
  BigInt calculateLiquidationPrice({
    required BigInt entryPrice,
    required bool isLong,
    required int leverage,
  }) {
    final marginFactor = (10000 - maintenanceMargin) * 100;
    final leverageFactor = marginFactor ~/ leverage;

    if (isLong) {
      final priceReduction =
          (entryPrice * BigInt.from(leverageFactor)) ~/ BigInt.from(1000000);
      return entryPrice - priceReduction;
    } else {
      final priceIncrease =
          (entryPrice * BigInt.from(leverageFactor)) ~/ BigInt.from(1000000);
      return entryPrice + priceIncrease;
    }
  }

  /// Get asset icon path
  String get assetIconPath {
    switch (baseAsset.toUpperCase()) {
      case 'BTC':
        return 'assets/icons/btc.png';
      case 'ETH':
        return 'assets/icons/eth.png';
      case 'SOL':
        return 'assets/icons/sol.png';
      case 'AVAX':
        return 'assets/icons/avax.png';
      case 'MATIC':
        return 'assets/icons/matic.png';
      default:
        return 'assets/icons/default_crypto.png';
    }
  }

  /// Get asset color for UI theming
  String get assetColor {
    switch (baseAsset.toUpperCase()) {
      case 'BTC':
        return '#F7931A'; // Bitcoin orange
      case 'ETH':
        return '#627EEA'; // Ethereum blue
      case 'SOL':
        return '#9945FF'; // Solana purple
      case 'AVAX':
        return '#E84142'; // Avalanche red
      case 'MATIC':
        return '#8247E5'; // Polygon purple
      default:
        return '#6C757D'; // Default gray
    }
  }

  /// Get market category
  MarketCategory get category {
    switch (baseAsset.toUpperCase()) {
      case 'BTC':
      case 'ETH':
        return MarketCategory.major;
      case 'SOL':
      case 'AVAX':
      case 'MATIC':
        return MarketCategory.altcoin;
      default:
        return MarketCategory.other;
    }
  }

  /// Get risk level based on maintenance margin and max leverage
  RiskLevel get riskLevel {
    if (maxLeverage <= 10 && maintenanceMargin >= 1000) {
      return RiskLevel.low;
    } else if (maxLeverage <= 25 && maintenanceMargin >= 500) {
      return RiskLevel.medium;
    } else if (maxLeverage <= 50) {
      return RiskLevel.high;
    } else {
      return RiskLevel.extreme;
    }
  }

  /// Check if pair supports given leverage
  bool supportsLeverage(int leverage) {
    return leverage > 0 && leverage <= maxLeverage;
  }

  /// Get minimum position size (based on current price)
  BigInt getMinimumPositionSize({int decimals = 18}) {
    // Minimum $10 position
    final minUsdValue = BigInt.from(10) * BigInt.from(10).pow(decimals);
    return minUsdValue ~/
        currentPrice *
        currentPrice; // Round to price precision
  }

  /// Copy with updated values
  TradingPair copyWith({
    int? pairId,
    String? name,
    String? baseAsset,
    String? quoteAsset,
    BigInt? currentPrice,
    int? maxLeverage,
    int? maintenanceMargin,
    BigInt? fundingRate,
    bool? isActive,
    BigInt? dailyVolume,
  }) {
    return TradingPair(
      pairId: pairId ?? this.pairId,
      name: name ?? this.name,
      baseAsset: baseAsset ?? this.baseAsset,
      quoteAsset: quoteAsset ?? this.quoteAsset,
      currentPrice: currentPrice ?? this.currentPrice,
      maxLeverage: maxLeverage ?? this.maxLeverage,
      maintenanceMargin: maintenanceMargin ?? this.maintenanceMargin,
      fundingRate: fundingRate ?? this.fundingRate,
      isActive: isActive ?? this.isActive,
      dailyVolume: dailyVolume ?? this.dailyVolume,
    );
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;

    return other is TradingPair &&
        other.pairId == pairId &&
        other.name == name &&
        other.baseAsset == baseAsset &&
        other.quoteAsset == quoteAsset &&
        other.currentPrice == currentPrice &&
        other.maxLeverage == maxLeverage &&
        other.maintenanceMargin == maintenanceMargin &&
        other.fundingRate == fundingRate &&
        other.isActive == isActive &&
        other.dailyVolume == dailyVolume;
  }

  @override
  int get hashCode {
    return Object.hash(
      pairId,
      name,
      baseAsset,
      quoteAsset,
      currentPrice,
      maxLeverage,
      maintenanceMargin,
      fundingRate,
      isActive,
      dailyVolume,
    );
  }

  @override
  String toString() {
    return 'TradingPair(id: $pairId, name: $name, price: ${getFormattedPrice()}, maxLeverage: ${maxLeverage}x, active: $isActive)';
  }

  /// Helper method to convert felt252 to string
  static String _feltToString(String felt) {
    // Convert felt252 hex to string
    // This is a simplified conversion - in reality, you'd need proper felt252 to ASCII conversion
    if (felt.startsWith('0x')) {
      final hex = felt.substring(2);
      final bytes = <int>[];
      for (int i = 0; i < hex.length; i += 2) {
        final hexByte = hex.substring(i, i + 2);
        final byte = int.parse(hexByte, radix: 16);
        if (byte != 0) bytes.add(byte);
      }
      return String.fromCharCodes(bytes);
    }
    return felt;
  }
}

/// Market category enum
enum MarketCategory {
  major, // BTC, ETH
  altcoin, // Other major cryptocurrencies
  defi, // DeFi tokens
  other, // Everything else
}

/// Risk level enum
enum RiskLevel {
  low, // Conservative leverage and margins
  medium, // Moderate risk
  high, // High leverage/risk
  extreme, // Maximum risk
}

/// Extensions for better display
extension MarketCategoryExtension on MarketCategory {
  String get displayName {
    switch (this) {
      case MarketCategory.major:
        return 'Major';
      case MarketCategory.altcoin:
        return 'Altcoin';
      case MarketCategory.defi:
        return 'DeFi';
      case MarketCategory.other:
        return 'Other';
    }
  }

  String get colorHex {
    switch (this) {
      case MarketCategory.major:
        return '#00C851'; // Green
      case MarketCategory.altcoin:
        return '#33B5E5'; // Blue
      case MarketCategory.defi:
        return '#FF8800'; // Orange
      case MarketCategory.other:
        return '#6C757D'; // Gray
    }
  }
}

extension RiskLevelExtension on RiskLevel {
  String get displayName {
    switch (this) {
      case RiskLevel.low:
        return 'Low Risk';
      case RiskLevel.medium:
        return 'Medium Risk';
      case RiskLevel.high:
        return 'High Risk';
      case RiskLevel.extreme:
        return 'Extreme Risk';
    }
  }

  String get colorHex {
    switch (this) {
      case RiskLevel.low:
        return '#00C851'; // Green
      case RiskLevel.medium:
        return '#FFBB33'; // Yellow
      case RiskLevel.high:
        return '#FF8800'; // Orange
      case RiskLevel.extreme:
        return '#FF4444'; // Red
    }
  }

  String get description {
    switch (this) {
      case RiskLevel.low:
        return 'Conservative leverage with high margin requirements';
      case RiskLevel.medium:
        return 'Moderate leverage suitable for experienced traders';
      case RiskLevel.high:
        return 'High leverage requiring careful risk management';
      case RiskLevel.extreme:
        return 'Maximum leverage - only for expert traders';
    }
  }
}
