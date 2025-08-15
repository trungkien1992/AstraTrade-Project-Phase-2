/// Vault Data Models for AstraTrade
///
/// Complete data models for vault operations:
/// - User vault state with real-time health monitoring
/// - Deposit/withdrawal results with gamification
/// - Asset configurations and pricing
/// - Risk assessment and liquidation protection

import 'dart:convert';

// === Core User Vault Data ===

class UserVaultData {
  final String userAddress;
  final BigInt totalCollateralValue;
  final BigInt healthFactor;
  final BigInt ethBalance;
  final BigInt btcBalance;
  final BigInt usdcBalance;
  final VaultBenefits benefits;
  final DateTime lastUpdated;
  final int totalXpEarned;
  final int depositStreak;
  final int unlockedTiers;

  const UserVaultData({
    required this.userAddress,
    required this.totalCollateralValue,
    required this.healthFactor,
    required this.ethBalance,
    required this.btcBalance,
    required this.usdcBalance,
    required this.benefits,
    required this.lastUpdated,
    this.totalXpEarned = 0,
    this.depositStreak = 0,
    this.unlockedTiers = 0,
  });

  /// Create empty vault data for new user
  factory UserVaultData.empty(String userAddress) {
    return UserVaultData(
      userAddress: userAddress,
      totalCollateralValue: BigInt.zero,
      healthFactor: BigInt.zero,
      ethBalance: BigInt.zero,
      btcBalance: BigInt.zero,
      usdcBalance: BigInt.zero,
      benefits: VaultBenefits.defaultBenefits(),
      lastUpdated: DateTime.now(),
    );
  }

  /// Create from contract response
  factory UserVaultData.fromContractResponse(
    String userAddress,
    List<String> response,
  ) {
    return UserVaultData(
      userAddress: userAddress,
      totalCollateralValue: BigInt.parse(response[0]),
      healthFactor: BigInt.parse(response[1]),
      ethBalance: BigInt.parse(response[2]),
      btcBalance: BigInt.parse(response[3]),
      usdcBalance: BigInt.parse(response[4]),
      benefits: VaultBenefits.fromContractResponse(response.sublist(5, 9)),
      lastUpdated: DateTime.now(),
      totalXpEarned: int.parse(response[9]),
      depositStreak: int.parse(response[10]),
      unlockedTiers: int.parse(response[11]),
    );
  }

  /// Convert to JSON
  Map<String, dynamic> toJson() {
    return {
      'userAddress': userAddress,
      'totalCollateralValue': totalCollateralValue.toString(),
      'healthFactor': healthFactor.toString(),
      'ethBalance': ethBalance.toString(),
      'btcBalance': btcBalance.toString(),
      'usdcBalance': usdcBalance.toString(),
      'benefits': benefits.toJson(),
      'lastUpdated': lastUpdated.toIso8601String(),
      'totalXpEarned': totalXpEarned,
      'depositStreak': depositStreak,
      'unlockedTiers': unlockedTiers,
    };
  }

  /// Create from JSON
  factory UserVaultData.fromJson(Map<String, dynamic> json) {
    return UserVaultData(
      userAddress: json['userAddress'] as String,
      totalCollateralValue: BigInt.parse(
        json['totalCollateralValue'] as String,
      ),
      healthFactor: BigInt.parse(json['healthFactor'] as String),
      ethBalance: BigInt.parse(json['ethBalance'] as String),
      btcBalance: BigInt.parse(json['btcBalance'] as String),
      usdcBalance: BigInt.parse(json['usdcBalance'] as String),
      benefits: VaultBenefits.fromJson(
        json['benefits'] as Map<String, dynamic>,
      ),
      lastUpdated: DateTime.parse(json['lastUpdated'] as String),
      totalXpEarned: json['totalXpEarned'] as int? ?? 0,
      depositStreak: json['depositStreak'] as int? ?? 0,
      unlockedTiers: json['unlockedTiers'] as int? ?? 0,
    );
  }

  /// Get formatted collateral value
  String getFormattedCollateralValue({int decimals = 18}) {
    final divisor = BigInt.from(10).pow(decimals);
    final value = totalCollateralValue.toDouble() / divisor.toDouble();

    if (value >= 1000000) {
      return '\$${(value / 1000000).toStringAsFixed(2)}M';
    } else if (value >= 1000) {
      return '\$${(value / 1000).toStringAsFixed(2)}K';
    } else {
      return '\$${value.toStringAsFixed(2)}';
    }
  }

  /// Get formatted health factor as percentage
  String getFormattedHealthFactor({int decimals = 18}) {
    if (healthFactor == BigInt.zero) return '0%';

    final divisor = BigInt.from(10).pow(decimals);
    final percentage = (healthFactor.toDouble() / divisor.toDouble()) * 100;
    return '${percentage.toStringAsFixed(1)}%';
  }

  /// Get risk level assessment
  RiskLevel get riskLevel {
    if (healthFactor == BigInt.zero) return RiskLevel.liquidation;

    final divisor = BigInt.from(10).pow(18);
    final ratio = healthFactor.toDouble() / divisor.toDouble();

    if (ratio >= 1.5) return RiskLevel.safe;
    if (ratio >= 1.25) return RiskLevel.low;
    if (ratio >= 1.1) return RiskLevel.medium;
    if (ratio >= 1.0) return RiskLevel.high;
    return RiskLevel.liquidation;
  }

  /// Get user level from XP
  int get userLevel {
    if (totalXpEarned >= 40000) return 20;
    if (totalXpEarned >= 22500) return 15;
    if (totalXpEarned >= 10000) return 10;
    if (totalXpEarned >= 2500) return 5;
    if (totalXpEarned >= 400) return 2;
    return 1;
  }

  /// Check if tier is unlocked
  bool isTierUnlocked(int tier) {
    return (unlockedTiers & (1 << tier)) != 0;
  }

  /// Get asset balance by symbol
  BigInt getAssetBalance(String asset) {
    switch (asset.toUpperCase()) {
      case 'ETH':
        return ethBalance;
      case 'BTC':
        return btcBalance;
      case 'USDC':
        return usdcBalance;
      default:
        return BigInt.zero;
    }
  }

  /// Copy with updated values
  UserVaultData copyWith({
    String? userAddress,
    BigInt? totalCollateralValue,
    BigInt? healthFactor,
    BigInt? ethBalance,
    BigInt? btcBalance,
    BigInt? usdcBalance,
    VaultBenefits? benefits,
    DateTime? lastUpdated,
    int? totalXpEarned,
    int? depositStreak,
    int? unlockedTiers,
  }) {
    return UserVaultData(
      userAddress: userAddress ?? this.userAddress,
      totalCollateralValue: totalCollateralValue ?? this.totalCollateralValue,
      healthFactor: healthFactor ?? this.healthFactor,
      ethBalance: ethBalance ?? this.ethBalance,
      btcBalance: btcBalance ?? this.btcBalance,
      usdcBalance: usdcBalance ?? this.usdcBalance,
      benefits: benefits ?? this.benefits,
      lastUpdated: lastUpdated ?? this.lastUpdated,
      totalXpEarned: totalXpEarned ?? this.totalXpEarned,
      depositStreak: depositStreak ?? this.depositStreak,
      unlockedTiers: unlockedTiers ?? this.unlockedTiers,
    );
  }

  @override
  String toString() {
    return 'UserVaultData(address: $userAddress, collateral: ${getFormattedCollateralValue()}, health: ${getFormattedHealthFactor()}, level: $userLevel)';
  }
}

// === Vault Benefits ===

class VaultBenefits {
  final int yieldMultiplier; // In basis points (11000 = 110% = 10% bonus)
  final int reducedLiquidationFee; // In basis points (250 = 2.5%)
  final bool priorityAssetAccess;
  final int maxLeverageBonus; // Additional leverage points

  const VaultBenefits({
    required this.yieldMultiplier,
    required this.reducedLiquidationFee,
    required this.priorityAssetAccess,
    required this.maxLeverageBonus,
  });

  /// Default benefits for new users
  factory VaultBenefits.defaultBenefits() {
    return const VaultBenefits(
      yieldMultiplier: 10000, // 100% = no bonus
      reducedLiquidationFee: 500, // 5% full fee
      priorityAssetAccess: false,
      maxLeverageBonus: 0,
    );
  }

  /// Create from contract response
  factory VaultBenefits.fromContractResponse(List<String> response) {
    return VaultBenefits(
      yieldMultiplier: int.parse(response[0]),
      reducedLiquidationFee: int.parse(response[1]),
      priorityAssetAccess: response[2] == '1',
      maxLeverageBonus: int.parse(response[3]),
    );
  }

  /// Convert to JSON
  Map<String, dynamic> toJson() {
    return {
      'yieldMultiplier': yieldMultiplier,
      'reducedLiquidationFee': reducedLiquidationFee,
      'priorityAssetAccess': priorityAssetAccess,
      'maxLeverageBonus': maxLeverageBonus,
    };
  }

  /// Create from JSON
  factory VaultBenefits.fromJson(Map<String, dynamic> json) {
    return VaultBenefits(
      yieldMultiplier: json['yieldMultiplier'] as int,
      reducedLiquidationFee: json['reducedLiquidationFee'] as int,
      priorityAssetAccess: json['priorityAssetAccess'] as bool,
      maxLeverageBonus: json['maxLeverageBonus'] as int,
    );
  }

  /// Get yield bonus percentage
  double get yieldBonusPercentage {
    return (yieldMultiplier - 10000) / 100.0;
  }

  /// Get liquidation fee percentage
  double get liquidationFeePercentage {
    return reducedLiquidationFee / 100.0;
  }

  @override
  String toString() {
    return 'VaultBenefits(yield: +${yieldBonusPercentage.toStringAsFixed(1)}%, liquidation: ${liquidationFeePercentage.toStringAsFixed(1)}%, leverage: +$maxLeverageBonus)';
  }
}

// === Operation Result Classes ===

class DepositResult {
  final bool success;
  final String? transactionHash;
  final String? errorMessage;
  final BigInt newCollateralValue;
  final int xpEarned;
  final BigInt newHealthFactor;
  final BigInt gasUsed;

  const DepositResult({
    required this.success,
    this.transactionHash,
    this.errorMessage,
    required this.newCollateralValue,
    required this.xpEarned,
    required this.newHealthFactor,
    required this.gasUsed,
  });

  /// Create from contract event data
  factory DepositResult.fromEventData(Map<String, dynamic> eventData) {
    return DepositResult(
      success: true,
      transactionHash: eventData['transaction_hash'],
      newCollateralValue: BigInt.parse(eventData['new_total_value'] ?? '0'),
      xpEarned: int.parse(eventData['xp_earned'] ?? '0'),
      newHealthFactor: BigInt.parse(eventData['health_factor'] ?? '0'),
      gasUsed: BigInt.parse(eventData['gas_used'] ?? '50000'),
    );
  }

  /// Get formatted gas used
  String get formattedGasUsed {
    if (gasUsed >= BigInt.from(1000)) {
      return '${(gasUsed.toDouble() / 1000).toStringAsFixed(1)}K';
    }
    return gasUsed.toString();
  }

  @override
  String toString() {
    return success
        ? 'Deposit successful: +$xpEarned XP, Gas: $formattedGasUsed'
        : 'Deposit failed: $errorMessage';
  }
}

class WithdrawalResult {
  final bool success;
  final String? transactionHash;
  final String? errorMessage;
  final BigInt remainingCollateralValue;
  final BigInt newHealthFactor;
  final BigInt gasUsed;

  const WithdrawalResult({
    required this.success,
    this.transactionHash,
    this.errorMessage,
    required this.remainingCollateralValue,
    required this.newHealthFactor,
    required this.gasUsed,
  });

  /// Create from contract event data
  factory WithdrawalResult.fromEventData(Map<String, dynamic> eventData) {
    return WithdrawalResult(
      success: true,
      transactionHash: eventData['transaction_hash'],
      remainingCollateralValue: BigInt.parse(
        eventData['remaining_value'] ?? '0',
      ),
      newHealthFactor: BigInt.parse(eventData['health_factor'] ?? '0'),
      gasUsed: BigInt.parse(eventData['gas_used'] ?? '45000'),
    );
  }

  @override
  String toString() {
    return success
        ? 'Withdrawal successful'
        : 'Withdrawal failed: $errorMessage';
  }
}

class YieldClaimResult {
  final bool success;
  final String? transactionHash;
  final String? errorMessage;
  final BigInt totalYield;
  final int xpBonus;
  final int streakBonus;

  const YieldClaimResult({
    required this.success,
    this.transactionHash,
    this.errorMessage,
    required this.totalYield,
    required this.xpBonus,
    required this.streakBonus,
  });

  /// Create from contract event data
  factory YieldClaimResult.fromEventData(Map<String, dynamic> eventData) {
    return YieldClaimResult(
      success: true,
      transactionHash: eventData['transaction_hash'],
      totalYield: BigInt.parse(eventData['total_yield'] ?? '0'),
      xpBonus: int.parse(eventData['xp_bonus'] ?? '0'),
      streakBonus: int.parse(eventData['streak_bonus'] ?? '0'),
    );
  }

  /// Get formatted yield amount
  String getFormattedYield({int decimals = 18}) {
    final divisor = BigInt.from(10).pow(decimals);
    final value = totalYield.toDouble() / divisor.toDouble();
    return value.toStringAsFixed(6);
  }

  @override
  String toString() {
    return success
        ? 'Yield claimed: ${getFormattedYield()} ETH, +$xpBonus XP, ${streakBonus}% streak bonus'
        : 'Yield claim failed: $errorMessage';
  }
}

class TierUnlockResult {
  final bool success;
  final String? transactionHash;
  final String? errorMessage;
  final int tier;
  final int xpCost;
  final List<String> assetsUnlocked;

  const TierUnlockResult({
    required this.success,
    this.transactionHash,
    this.errorMessage,
    required this.tier,
    required this.xpCost,
    required this.assetsUnlocked,
  });

  /// Create from contract event data
  factory TierUnlockResult.fromEventData(Map<String, dynamic> eventData) {
    return TierUnlockResult(
      success: true,
      transactionHash: eventData['transaction_hash'],
      tier: int.parse(eventData['tier'] ?? '0'),
      xpCost: int.parse(eventData['xp_cost'] ?? '0'),
      assetsUnlocked: List<String>.from(eventData['assets_unlocked'] ?? []),
    );
  }

  @override
  String toString() {
    return success
        ? 'Tier $tier unlocked: ${assetsUnlocked.join(', ')} for $xpCost XP'
        : 'Tier unlock failed: $errorMessage';
  }
}

// === Asset Configuration ===

class AssetConfig {
  final String symbol;
  final String oracle;
  final int collateralFactor; // In basis points (8000 = 80%)
  final int minUserLevel; // Required user level
  final bool isActive;
  final BigInt totalDeposits;
  final int yieldRate; // Annual yield in basis points

  const AssetConfig({
    required this.symbol,
    required this.oracle,
    required this.collateralFactor,
    required this.minUserLevel,
    required this.isActive,
    required this.totalDeposits,
    required this.yieldRate,
  });

  /// Create from contract response
  factory AssetConfig.fromContractResponse(
    String symbol,
    List<String> response,
  ) {
    return AssetConfig(
      symbol: symbol,
      oracle: response[0],
      collateralFactor: int.parse(response[1]),
      minUserLevel: int.parse(response[2]),
      isActive: response[3] == '1',
      totalDeposits: BigInt.parse(response[4]),
      yieldRate: int.parse(response[5]),
    );
  }

  /// Get collateral factor as percentage
  double get collateralFactorPercentage {
    return collateralFactor / 100.0;
  }

  /// Get annual yield as percentage
  double get annualYieldPercentage {
    return yieldRate / 100.0;
  }

  /// Get asset tier based on min user level
  int get tier {
    if (minUserLevel <= 1) return 0; // Basic assets (ETH, BTC, USDC)
    if (minUserLevel <= 5) return 1; // Tier 1 assets
    if (minUserLevel <= 10) return 2; // Tier 2 assets
    if (minUserLevel <= 15) return 3; // Tier 3 assets
    return 4; // Tier 4 experimental assets
  }

  @override
  String toString() {
    return 'AssetConfig($symbol: ${collateralFactorPercentage.toStringAsFixed(0)}% LTV, ${annualYieldPercentage.toStringAsFixed(1)}% APY, Level $minUserLevel+)';
  }
}

// === Vault Events ===

abstract class VaultEvent {
  final String userAddress;
  final DateTime timestamp;
  final String transactionHash;

  const VaultEvent({
    required this.userAddress,
    required this.timestamp,
    required this.transactionHash,
  });
}

class CollateralDepositedEvent extends VaultEvent {
  final String asset;
  final BigInt amount;
  final BigInt newTotalValue;
  final int xpEarned;
  final BigInt healthFactor;

  const CollateralDepositedEvent({
    required super.userAddress,
    required super.timestamp,
    required super.transactionHash,
    required this.asset,
    required this.amount,
    required this.newTotalValue,
    required this.xpEarned,
    required this.healthFactor,
  });

  @override
  String toString() {
    return 'Deposited ${amount.toString()} $asset (+$xpEarned XP)';
  }
}

class YieldClaimedEvent extends VaultEvent {
  final BigInt totalYield;
  final int xpBonus;
  final int streakBonus;

  const YieldClaimedEvent({
    required super.userAddress,
    required super.timestamp,
    required super.transactionHash,
    required this.totalYield,
    required this.xpBonus,
    required this.streakBonus,
  });

  @override
  String toString() {
    return 'Claimed ${totalYield.toString()} yield (+$xpBonus XP, ${streakBonus}% bonus)';
  }
}

class HealthFactorUpdatedEvent extends VaultEvent {
  final BigInt oldHealthFactor;
  final BigInt newHealthFactor;
  final int riskLevel;

  const HealthFactorUpdatedEvent({
    required super.userAddress,
    required super.timestamp,
    required super.transactionHash,
    required this.oldHealthFactor,
    required this.newHealthFactor,
    required this.riskLevel,
  });

  @override
  String toString() {
    final riskNames = ['Safe', 'Warning', 'Danger', 'Liquidation'];
    return 'Health factor updated: ${riskNames[riskLevel]}';
  }
}

// === Risk Level Enum ===
enum RiskLevel {
  safe, // > 150% health factor
  low, // 125-150% health factor
  medium, // 110-125% health factor
  high, // 100-110% health factor
  liquidation, // < 100% health factor
}

extension RiskLevelExtension on RiskLevel {
  String get displayName {
    switch (this) {
      case RiskLevel.safe:
        return 'Safe';
      case RiskLevel.low:
        return 'Low Risk';
      case RiskLevel.medium:
        return 'Medium Risk';
      case RiskLevel.high:
        return 'High Risk';
      case RiskLevel.liquidation:
        return 'Liquidation Risk';
    }
  }

  String get colorHex {
    switch (this) {
      case RiskLevel.safe:
        return '#00C851'; // Green
      case RiskLevel.low:
        return '#2BBBAD'; // Teal
      case RiskLevel.medium:
        return '#FFBB33'; // Yellow
      case RiskLevel.high:
        return '#FF8800'; // Orange
      case RiskLevel.liquidation:
        return '#FF4444'; // Red
    }
  }

  String get description {
    switch (this) {
      case RiskLevel.safe:
        return 'Position is safe from liquidation';
      case RiskLevel.low:
        return 'Low risk of liquidation';
      case RiskLevel.medium:
        return 'Monitor position closely';
      case RiskLevel.high:
        return 'High risk - consider adding collateral';
      case RiskLevel.liquidation:
        return 'Position may be liquidated';
    }
  }
}
