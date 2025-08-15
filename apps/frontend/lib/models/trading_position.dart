/// Trading Position Model for AstraTrade Exchange V2
///
/// Represents a perpetuals trading position with:
/// - Position details (leverage, collateral, prices)
/// - Real-time P&L calculation
/// - Liquidation monitoring
/// - Mobile-optimized display data

import 'dart:convert';

class TradingPosition {
  final int positionId;
  final String userAddress;
  final int pairId;
  final bool isLong;
  final int leverage;
  final BigInt collateral;
  final BigInt entryPrice;
  final BigInt liquidationPrice;
  final BigInt fundingRateAccumulated;
  final bool isActive;
  final DateTime createdTimestamp;
  final DateTime lastUpdatedTimestamp;

  const TradingPosition({
    required this.positionId,
    required this.userAddress,
    required this.pairId,
    required this.isLong,
    required this.leverage,
    required this.collateral,
    required this.entryPrice,
    required this.liquidationPrice,
    required this.fundingRateAccumulated,
    required this.isActive,
    required this.createdTimestamp,
    required this.lastUpdatedTimestamp,
  });

  /// Create TradingPosition from contract data
  factory TradingPosition.fromContractData(List<String> data) {
    return TradingPosition(
      positionId: int.parse(data[0]),
      userAddress: data[1],
      pairId: int.parse(data[2]),
      isLong: data[3] == '1',
      leverage: int.parse(data[4]),
      collateral: BigInt.parse(data[5]),
      entryPrice: BigInt.parse(data[6]),
      liquidationPrice: BigInt.parse(data[7]),
      fundingRateAccumulated: BigInt.parse(data[8]),
      isActive: data[9] == '1',
      createdTimestamp: DateTime.fromMillisecondsSinceEpoch(
        int.parse(data[10]) * 1000,
      ),
      lastUpdatedTimestamp: DateTime.fromMillisecondsSinceEpoch(
        int.parse(data[11]) * 1000,
      ),
    );
  }

  /// Create TradingPosition from JSON
  factory TradingPosition.fromJson(Map<String, dynamic> json) {
    return TradingPosition(
      positionId: json['positionId'] as int,
      userAddress: json['userAddress'] as String,
      pairId: json['pairId'] as int,
      isLong: json['isLong'] as bool,
      leverage: json['leverage'] as int,
      collateral: BigInt.parse(json['collateral'] as String),
      entryPrice: BigInt.parse(json['entryPrice'] as String),
      liquidationPrice: BigInt.parse(json['liquidationPrice'] as String),
      fundingRateAccumulated: BigInt.parse(
        json['fundingRateAccumulated'] as String,
      ),
      isActive: json['isActive'] as bool,
      createdTimestamp: DateTime.parse(json['createdTimestamp'] as String),
      lastUpdatedTimestamp: DateTime.parse(
        json['lastUpdatedTimestamp'] as String,
      ),
    );
  }

  /// Convert to JSON
  Map<String, dynamic> toJson() {
    return {
      'positionId': positionId,
      'userAddress': userAddress,
      'pairId': pairId,
      'isLong': isLong,
      'leverage': leverage,
      'collateral': collateral.toString(),
      'entryPrice': entryPrice.toString(),
      'liquidationPrice': liquidationPrice.toString(),
      'fundingRateAccumulated': fundingRateAccumulated.toString(),
      'isActive': isActive,
      'createdTimestamp': createdTimestamp.toIso8601String(),
      'lastUpdatedTimestamp': lastUpdatedTimestamp.toIso8601String(),
    };
  }

  /// Calculate position size (collateral * leverage)
  BigInt get positionSize {
    return collateral * BigInt.from(leverage);
  }

  /// Calculate unrealized P&L based on current price
  PositionPnL calculatePnL(BigInt currentPrice) {
    final sizeBigInt = positionSize;

    BigInt pnlAmount;
    bool isProfit;

    if (isLong) {
      if (currentPrice > entryPrice) {
        final priceDiff = currentPrice - entryPrice;
        pnlAmount = (sizeBigInt * priceDiff) ~/ entryPrice;
        isProfit = true;
      } else {
        final priceDiff = entryPrice - currentPrice;
        pnlAmount = (sizeBigInt * priceDiff) ~/ entryPrice;
        isProfit = false;
      }
    } else {
      if (currentPrice < entryPrice) {
        final priceDiff = entryPrice - currentPrice;
        pnlAmount = (sizeBigInt * priceDiff) ~/ entryPrice;
        isProfit = true;
      } else {
        final priceDiff = currentPrice - entryPrice;
        pnlAmount = (sizeBigInt * priceDiff) ~/ entryPrice;
        isProfit = false;
      }
    }

    return PositionPnL(
      amount: pnlAmount,
      isProfit: isProfit,
      percentage: _calculatePnLPercentage(pnlAmount, isProfit),
    );
  }

  /// Calculate P&L percentage
  double _calculatePnLPercentage(BigInt pnlAmount, bool isProfit) {
    if (collateral == BigInt.zero) return 0.0;

    final percentage = (pnlAmount.toDouble() / collateral.toDouble()) * 100.0;
    return isProfit ? percentage : -percentage;
  }

  /// Check if position is near liquidation (within 10%)
  bool isNearLiquidation(BigInt currentPrice) {
    if (!isActive) return false;

    final threshold = BigInt.from(10); // 10% threshold
    BigInt distanceToLiquidation;

    if (isLong) {
      if (currentPrice <= liquidationPrice) return true;
      distanceToLiquidation = currentPrice - liquidationPrice;
    } else {
      if (currentPrice >= liquidationPrice) return true;
      distanceToLiquidation = liquidationPrice - currentPrice;
    }

    final thresholdDistance = (currentPrice * threshold) ~/ BigInt.from(100);
    return distanceToLiquidation <= thresholdDistance;
  }

  /// Get position direction as string
  String get directionText => isLong ? 'LONG' : 'SHORT';

  /// Get position status
  PositionStatus get status {
    if (!isActive) return PositionStatus.closed;
    return PositionStatus.active;
  }

  /// Get formatted entry price
  String getFormattedEntryPrice({int decimals = 18}) {
    final divisor = BigInt.from(10).pow(decimals);
    final price = entryPrice.toDouble() / divisor.toDouble();
    return price.toStringAsFixed(2);
  }

  /// Get formatted liquidation price
  String getFormattedLiquidationPrice({int decimals = 18}) {
    final divisor = BigInt.from(10).pow(decimals);
    final price = liquidationPrice.toDouble() / divisor.toDouble();
    return price.toStringAsFixed(2);
  }

  /// Get formatted collateral amount
  String getFormattedCollateral({int decimals = 18}) {
    final divisor = BigInt.from(10).pow(decimals);
    final amount = collateral.toDouble() / divisor.toDouble();
    return amount.toStringAsFixed(4);
  }

  /// Get formatted position size
  String getFormattedPositionSize({int decimals = 18}) {
    final divisor = BigInt.from(10).pow(decimals);
    final size = positionSize.toDouble() / divisor.toDouble();
    return size.toStringAsFixed(2);
  }

  /// Get time since position was opened
  Duration get timeOpen {
    return DateTime.now().difference(createdTimestamp);
  }

  /// Get formatted time open
  String get formattedTimeOpen {
    final duration = timeOpen;
    if (duration.inDays > 0) {
      return '${duration.inDays}d ${duration.inHours % 24}h';
    } else if (duration.inHours > 0) {
      return '${duration.inHours}h ${duration.inMinutes % 60}m';
    } else {
      return '${duration.inMinutes}m';
    }
  }

  /// Copy with updated values
  TradingPosition copyWith({
    int? positionId,
    String? userAddress,
    int? pairId,
    bool? isLong,
    int? leverage,
    BigInt? collateral,
    BigInt? entryPrice,
    BigInt? liquidationPrice,
    BigInt? fundingRateAccumulated,
    bool? isActive,
    DateTime? createdTimestamp,
    DateTime? lastUpdatedTimestamp,
  }) {
    return TradingPosition(
      positionId: positionId ?? this.positionId,
      userAddress: userAddress ?? this.userAddress,
      pairId: pairId ?? this.pairId,
      isLong: isLong ?? this.isLong,
      leverage: leverage ?? this.leverage,
      collateral: collateral ?? this.collateral,
      entryPrice: entryPrice ?? this.entryPrice,
      liquidationPrice: liquidationPrice ?? this.liquidationPrice,
      fundingRateAccumulated:
          fundingRateAccumulated ?? this.fundingRateAccumulated,
      isActive: isActive ?? this.isActive,
      createdTimestamp: createdTimestamp ?? this.createdTimestamp,
      lastUpdatedTimestamp: lastUpdatedTimestamp ?? this.lastUpdatedTimestamp,
    );
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;

    return other is TradingPosition &&
        other.positionId == positionId &&
        other.userAddress == userAddress &&
        other.pairId == pairId &&
        other.isLong == isLong &&
        other.leverage == leverage &&
        other.collateral == collateral &&
        other.entryPrice == entryPrice &&
        other.liquidationPrice == liquidationPrice &&
        other.fundingRateAccumulated == fundingRateAccumulated &&
        other.isActive == isActive &&
        other.createdTimestamp == createdTimestamp &&
        other.lastUpdatedTimestamp == lastUpdatedTimestamp;
  }

  @override
  int get hashCode {
    return Object.hash(
      positionId,
      userAddress,
      pairId,
      isLong,
      leverage,
      collateral,
      entryPrice,
      liquidationPrice,
      fundingRateAccumulated,
      isActive,
      createdTimestamp,
      lastUpdatedTimestamp,
    );
  }

  @override
  String toString() {
    return 'TradingPosition(id: $positionId, pair: $pairId, ${directionText} ${leverage}x, collateral: ${getFormattedCollateral()}, active: $isActive)';
  }
}

/// P&L calculation result
class PositionPnL {
  final BigInt amount;
  final bool isProfit;
  final double percentage;

  const PositionPnL({
    required this.amount,
    required this.isProfit,
    required this.percentage,
  });

  /// Get formatted P&L amount
  String getFormattedAmount({int decimals = 18}) {
    final divisor = BigInt.from(10).pow(decimals);
    final value = amount.toDouble() / divisor.toDouble();
    final sign = isProfit ? '+' : '-';
    return '$sign\$${value.abs().toStringAsFixed(2)}';
  }

  /// Get formatted P&L percentage
  String get formattedPercentage {
    final sign = isProfit ? '+' : '';
    return '$sign${percentage.toStringAsFixed(2)}%';
  }

  /// Get P&L color (green for profit, red for loss)
  String get colorHex => isProfit ? '#00C851' : '#FF4444';

  @override
  String toString() {
    return 'PositionPnL(${getFormattedAmount()}, ${formattedPercentage})';
  }
}

/// Position status enum
enum PositionStatus { active, closed, liquidated }

/// Extension for better display of position status
extension PositionStatusExtension on PositionStatus {
  String get displayName {
    switch (this) {
      case PositionStatus.active:
        return 'Active';
      case PositionStatus.closed:
        return 'Closed';
      case PositionStatus.liquidated:
        return 'Liquidated';
    }
  }

  String get colorHex {
    switch (this) {
      case PositionStatus.active:
        return '#00C851'; // Green
      case PositionStatus.closed:
        return '#6C757D'; // Gray
      case PositionStatus.liquidated:
        return '#FF4444'; // Red
    }
  }
}
