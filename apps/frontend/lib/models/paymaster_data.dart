/// Paymaster Data Models for AstraTrade
/// 
/// Complete data models for gasless transaction management:
/// - Gas allowance tracking with tier-based limits
/// - XP-based tier progression system
/// - Trading rewards and streak bonuses
/// - Platform metrics and enterprise features

import 'dart:convert';

// === Core Gas Allowance Data ===

class GasAllowance {
  final int dailyLimit;
  final int weeklyLimit;
  final int monthlyLimit;
  final int usedToday;
  final int usedThisWeek;
  final int usedThisMonth;
  final DateTime lastResetDay;
  final DateTime lastResetWeek;
  final DateTime lastResetMonth;
  final double priorityBoost; // Multiplier for priority processing

  const GasAllowance({
    required this.dailyLimit,
    required this.weeklyLimit,
    required this.monthlyLimit,
    required this.usedToday,
    required this.usedThisWeek,
    required this.usedThisMonth,
    required this.lastResetDay,
    required this.lastResetWeek,
    required this.lastResetMonth,
    this.priorityBoost = 1.0,
  });

  /// Create empty gas allowance
  factory GasAllowance.empty() {
    final now = DateTime.now();
    return GasAllowance(
      dailyLimit: 0,
      weeklyLimit: 0,
      monthlyLimit: 0,
      usedToday: 0,
      usedThisWeek: 0,
      usedThisMonth: 0,
      lastResetDay: now,
      lastResetWeek: now,
      lastResetMonth: now,
    );
  }

  /// Create from contract response
  factory GasAllowance.fromContractResponse(List<String> response) {
    return GasAllowance(
      dailyLimit: int.parse(response[0]),
      weeklyLimit: int.parse(response[1]),
      monthlyLimit: int.parse(response[2]),
      usedToday: int.parse(response[3]),
      usedThisWeek: int.parse(response[4]),
      usedThisMonth: int.parse(response[5]),
      lastResetDay: DateTime.fromMillisecondsSinceEpoch(int.parse(response[6]) * 1000),
      lastResetWeek: DateTime.fromMillisecondsSinceEpoch(int.parse(response[7]) * 1000),
      lastResetMonth: DateTime.fromMillisecondsSinceEpoch(int.parse(response[8]) * 1000),
      priorityBoost: int.parse(response[9]) / 10000.0,
    );
  }

  /// Convert to JSON
  Map<String, dynamic> toJson() {
    return {
      'dailyLimit': dailyLimit,
      'weeklyLimit': weeklyLimit,
      'monthlyLimit': monthlyLimit,
      'usedToday': usedToday,
      'usedThisWeek': usedThisWeek,
      'usedThisMonth': usedThisMonth,
      'lastResetDay': lastResetDay.toIso8601String(),
      'lastResetWeek': lastResetWeek.toIso8601String(),
      'lastResetMonth': lastResetMonth.toIso8601String(),
      'priorityBoost': priorityBoost,
    };
  }

  /// Create from JSON
  factory GasAllowance.fromJson(Map<String, dynamic> json) {
    return GasAllowance(
      dailyLimit: json['dailyLimit'] as int,
      weeklyLimit: json['weeklyLimit'] as int,
      monthlyLimit: json['monthlyLimit'] as int,
      usedToday: json['usedToday'] as int,
      usedThisWeek: json['usedThisWeek'] as int,
      usedThisMonth: json['usedThisMonth'] as int,
      lastResetDay: DateTime.parse(json['lastResetDay'] as String),
      lastResetWeek: DateTime.parse(json['lastResetWeek'] as String),
      lastResetMonth: DateTime.parse(json['lastResetMonth'] as String),
      priorityBoost: json['priorityBoost'] as double? ?? 1.0,
    );
  }

  /// Get remaining daily gas
  int get remainingDaily => dailyLimit - usedToday;

  /// Get remaining weekly gas
  int get remainingWeekly => weeklyLimit - usedThisWeek;

  /// Get remaining monthly gas
  int get remainingMonthly => monthlyLimit - usedThisMonth;

  /// Get daily usage percentage
  double get dailyUsagePercentage {
    if (dailyLimit == 0) return 0.0;
    return (usedToday / dailyLimit).clamp(0.0, 1.0);
  }

  /// Get weekly usage percentage
  double get weeklyUsagePercentage {
    if (weeklyLimit == 0) return 0.0;
    return (usedThisWeek / weeklyLimit).clamp(0.0, 1.0);
  }

  /// Get monthly usage percentage
  double get monthlyUsagePercentage {
    if (monthlyLimit == 0) return 0.0;
    return (usedThisMonth / monthlyLimit).clamp(0.0, 1.0);
  }

  /// Format gas amount for display
  String formatGasAmount(int amount) {
    if (amount >= 1000000) {
      return '${(amount / 1000000).toStringAsFixed(1)}M';
    } else if (amount >= 1000) {
      return '${(amount / 1000).toStringAsFixed(1)}K';
    } else {
      return amount.toString();
    }
  }

  /// Get formatted daily remaining
  String get formattedDailyRemaining => formatGasAmount(remainingDaily);

  /// Get formatted weekly remaining
  String get formattedWeeklyRemaining => formatGasAmount(remainingWeekly);

  /// Get formatted monthly remaining
  String get formattedMonthlyRemaining => formatGasAmount(remainingMonthly);

  /// Check if user can sponsor a transaction
  bool canSponsorTransaction(int gasAmount) {
    return remainingDaily >= gasAmount && 
           remainingWeekly >= gasAmount && 
           remainingMonthly >= gasAmount;
  }

  @override
  String toString() {
    return 'GasAllowance(daily: ${formatGasAmount(remainingDaily)}/${formatGasAmount(dailyLimit)}, priority: ${(priorityBoost * 100).toStringAsFixed(0)}%)';
  }
}

// === Gas Tier Benefits ===

class GasTierBenefits {
  final String tierName;
  final int dailyGasAllowance;
  final int weeklyGasAllowance;
  final int monthlyGasAllowance;
  final bool priorityProcessing;
  final int batchTransactionLimit;
  final bool emergencyGasAccess;
  final double referralBonusRate; // Percentage (e.g., 0.05 = 5%)

  const GasTierBenefits({
    required this.tierName,
    required this.dailyGasAllowance,
    required this.weeklyGasAllowance,
    required this.monthlyGasAllowance,
    required this.priorityProcessing,
    required this.batchTransactionLimit,
    required this.emergencyGasAccess,
    required this.referralBonusRate,
  });

  /// Basic tier benefits
  factory GasTierBenefits.basicTier() {
    return const GasTierBenefits(
      tierName: 'Basic',
      dailyGasAllowance: 100000,   // 100k gas/day
      weeklyGasAllowance: 500000,  // 500k gas/week
      monthlyGasAllowance: 2000000, // 2M gas/month
      priorityProcessing: false,
      batchTransactionLimit: 1,
      emergencyGasAccess: false,
      referralBonusRate: 0.05, // 5%
    );
  }

  /// Create from contract response
  factory GasTierBenefits.fromContractResponse(List<String> response) {
    return GasTierBenefits(
      tierName: _feltToString(response[0]),
      dailyGasAllowance: int.parse(response[1]),
      weeklyGasAllowance: int.parse(response[2]),
      monthlyGasAllowance: int.parse(response[3]),
      priorityProcessing: response[4] == '1',
      batchTransactionLimit: int.parse(response[5]),
      emergencyGasAccess: response[6] == '1',
      referralBonusRate: int.parse(response[7]) / 10000.0,
    );
  }

  /// Convert to JSON
  Map<String, dynamic> toJson() {
    return {
      'tierName': tierName,
      'dailyGasAllowance': dailyGasAllowance,
      'weeklyGasAllowance': weeklyGasAllowance,
      'monthlyGasAllowance': monthlyGasAllowance,
      'priorityProcessing': priorityProcessing,
      'batchTransactionLimit': batchTransactionLimit,
      'emergencyGasAccess': emergencyGasAccess,
      'referralBonusRate': referralBonusRate,
    };
  }

  /// Create from JSON
  factory GasTierBenefits.fromJson(Map<String, dynamic> json) {
    return GasTierBenefits(
      tierName: json['tierName'] as String,
      dailyGasAllowance: json['dailyGasAllowance'] as int,
      weeklyGasAllowance: json['weeklyGasAllowance'] as int,
      monthlyGasAllowance: json['monthlyGasAllowance'] as int,
      priorityProcessing: json['priorityProcessing'] as bool,
      batchTransactionLimit: json['batchTransactionLimit'] as int,
      emergencyGasAccess: json['emergencyGasAccess'] as bool,
      referralBonusRate: json['referralBonusRate'] as double,
    );
  }

  /// Get tier level from name
  int get tierLevel {
    switch (tierName.toLowerCase()) {
      case 'basic': return 0;
      case 'silver': return 1;
      case 'gold': return 2;
      case 'platinum': return 3;
      case 'diamond': return 4;
      default: return 0;
    }
  }

  /// Get tier color
  String get tierColor {
    switch (tierLevel) {
      case 0: return '#9E9E9E'; // Basic - Gray
      case 1: return '#C0C0C0'; // Silver
      case 2: return '#FFD700'; // Gold
      case 3: return '#E5E4E2'; // Platinum
      case 4: return '#B9F2FF'; // Diamond
      default: return '#9E9E9E';
    }
  }

  /// Get formatted referral bonus
  String get formattedReferralBonus {
    return '${(referralBonusRate * 100).toStringAsFixed(1)}%';
  }

  @override
  String toString() {
    return 'GasTierBenefits($tierName: ${(dailyGasAllowance / 1000).toStringAsFixed(0)}K/day, priority: $priorityProcessing, referral: $formattedReferralBonus)';
  }

  /// Helper method to convert felt252 to string
  static String _feltToString(String felt) {
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

// === User Gas Data ===

class UserGasData {
  final String userAddress;
  final GasAllowance gasAllowance;
  final GasTierBenefits gasTierBenefits;
  final int remainingSponsoredGas;
  final double currentRefundRate;
  final DateTime lastUpdated;
  final int totalGasSponsored;
  final int totalGasSaved;
  final int totalXpFromGas;
  final int consecutiveDaysActive;

  const UserGasData({
    required this.userAddress,
    required this.gasAllowance,
    required this.gasTierBenefits,
    required this.remainingSponsoredGas,
    required this.currentRefundRate,
    required this.lastUpdated,
    this.totalGasSponsored = 0,
    this.totalGasSaved = 0,
    this.totalXpFromGas = 0,
    this.consecutiveDaysActive = 0,
  });

  /// Create empty user gas data
  factory UserGasData.empty(String userAddress) {
    return UserGasData(
      userAddress: userAddress,
      gasAllowance: GasAllowance.empty(),
      gasTierBenefits: GasTierBenefits.basicTier(),
      remainingSponsoredGas: 0,
      currentRefundRate: 0.5,
      lastUpdated: DateTime.now(),
    );
  }

  /// Convert to JSON
  Map<String, dynamic> toJson() {
    return {
      'userAddress': userAddress,
      'gasAllowance': gasAllowance.toJson(),
      'gasTierBenefits': gasTierBenefits.toJson(),
      'remainingSponsoredGas': remainingSponsoredGas,
      'currentRefundRate': currentRefundRate,
      'lastUpdated': lastUpdated.toIso8601String(),
      'totalGasSponsored': totalGasSponsored,
      'totalGasSaved': totalGasSaved,
      'totalXpFromGas': totalXpFromGas,
      'consecutiveDaysActive': consecutiveDaysActive,
    };
  }

  /// Create from JSON
  factory UserGasData.fromJson(Map<String, dynamic> json) {
    return UserGasData(
      userAddress: json['userAddress'] as String,
      gasAllowance: GasAllowance.fromJson(json['gasAllowance'] as Map<String, dynamic>),
      gasTierBenefits: GasTierBenefits.fromJson(json['gasTierBenefits'] as Map<String, dynamic>),
      remainingSponsoredGas: json['remainingSponsoredGas'] as int,
      currentRefundRate: json['currentRefundRate'] as double,
      lastUpdated: DateTime.parse(json['lastUpdated'] as String),
      totalGasSponsored: json['totalGasSponsored'] as int? ?? 0,
      totalGasSaved: json['totalGasSaved'] as int? ?? 0,
      totalXpFromGas: json['totalXpFromGas'] as int? ?? 0,
      consecutiveDaysActive: json['consecutiveDaysActive'] as int? ?? 0,
    );
  }

  /// Get formatted current refund rate
  String get formattedRefundRate {
    return '${(currentRefundRate * 100).toStringAsFixed(1)}%';
  }

  /// Get formatted total gas sponsored
  String get formattedTotalGasSponsored {
    return gasAllowance.formatGasAmount(totalGasSponsored);
  }

  /// Get formatted total gas saved
  String get formattedTotalGasSaved {
    return gasAllowance.formatGasAmount(totalGasSaved);
  }

  /// Copy with updated values
  UserGasData copyWith({
    String? userAddress,
    GasAllowance? gasAllowance,
    GasTierBenefits? gasTierBenefits,
    int? remainingSponsoredGas,
    double? currentRefundRate,
    DateTime? lastUpdated,
    int? totalGasSponsored,
    int? totalGasSaved,
    int? totalXpFromGas,
    int? consecutiveDaysActive,
  }) {
    return UserGasData(
      userAddress: userAddress ?? this.userAddress,
      gasAllowance: gasAllowance ?? this.gasAllowance,
      gasTierBenefits: gasTierBenefits ?? this.gasTierBenefits,
      remainingSponsoredGas: remainingSponsoredGas ?? this.remainingSponsoredGas,
      currentRefundRate: currentRefundRate ?? this.currentRefundRate,
      lastUpdated: lastUpdated ?? this.lastUpdated,
      totalGasSponsored: totalGasSponsored ?? this.totalGasSponsored,
      totalGasSaved: totalGasSaved ?? this.totalGasSaved,
      totalXpFromGas: totalXpFromGas ?? this.totalXpFromGas,
      consecutiveDaysActive: consecutiveDaysActive ?? this.consecutiveDaysActive,
    );
  }

  @override
  String toString() {
    return 'UserGasData(${gasTierBenefits.tierName}: ${gasAllowance.formattedDailyRemaining} remaining, ${formattedRefundRate} refund)';
  }
}

// === Operation Result Classes ===

class SponsorshipResult {
  final bool success;
  final String? transactionHash;
  final String? errorMessage;
  final int gasUsed;
  final int gasSponsored;
  final int xpEarned;
  final int tierProgress; // Progress towards next tier (0-10000 basis points)

  const SponsorshipResult({
    required this.success,
    this.transactionHash,
    this.errorMessage,
    required this.gasUsed,
    required this.gasSponsored,
    required this.xpEarned,
    required this.tierProgress,
  });

  /// Create from contract event data
  factory SponsorshipResult.fromEventData(Map<String, dynamic> eventData) {
    return SponsorshipResult(
      success: true,
      transactionHash: eventData['transaction_hash'],
      gasUsed: int.parse(eventData['gas_used']?.toString() ?? '0'),
      gasSponsored: int.parse(eventData['gas_sponsored']?.toString() ?? '0'),
      xpEarned: int.parse(eventData['xp_earned']?.toString() ?? '0'),
      tierProgress: int.parse(eventData['tier_progress']?.toString() ?? '0'),
    );
  }

  /// Create from contract response
  factory SponsorshipResult.fromContractResponse(List<String> response) {
    return SponsorshipResult(
      success: response[0] == '1',
      transactionHash: response[1] != '0' ? response[1] : null,
      gasUsed: int.parse(response[2]),
      gasSponsored: int.parse(response[3]),
      xpEarned: int.parse(response[4]),
      tierProgress: int.parse(response[5]),
      errorMessage: response[0] == '0' ? 'Sponsorship failed' : null,
    );
  }

  /// Get tier progress percentage
  double get tierProgressPercentage {
    return tierProgress / 100.0; // Convert basis points to percentage
  }

  @override
  String toString() {
    return success
        ? 'Sponsored ${gasSponsored} gas, earned ${xpEarned} XP'
        : 'Sponsorship failed: $errorMessage';
  }
}

class GasRefillResult {
  final bool success;
  final String? transactionHash;
  final String? errorMessage;
  final int amountAdded;
  final int newDailyLimit;
  final String refillSource;

  const GasRefillResult({
    required this.success,
    this.transactionHash,
    this.errorMessage,
    required this.amountAdded,
    required this.newDailyLimit,
    required this.refillSource,
  });

  /// Create from contract event data
  factory GasRefillResult.fromEventData(Map<String, dynamic> eventData) {
    return GasRefillResult(
      success: true,
      transactionHash: eventData['transaction_hash'],
      amountAdded: int.parse(eventData['amount_added']?.toString() ?? '0'),
      newDailyLimit: int.parse(eventData['new_daily_limit']?.toString() ?? '0'),
      refillSource: eventData['refill_source']?.toString() ?? 'unknown',
    );
  }

  @override
  String toString() {
    return success
        ? 'Added ${amountAdded} gas from $refillSource'
        : 'Refill failed: $errorMessage';
  }
}

class TierUpgradeResult {
  final bool success;
  final String? transactionHash;
  final String? errorMessage;
  final int oldTier;
  final int newTier;
  final int xpSpent;
  final GasTierBenefits newBenefits;

  const TierUpgradeResult({
    required this.success,
    this.transactionHash,
    this.errorMessage,
    required this.oldTier,
    required this.newTier,
    required this.xpSpent,
    required this.newBenefits,
  });

  /// Create from contract event data
  factory TierUpgradeResult.fromEventData(Map<String, dynamic> eventData) {
    return TierUpgradeResult(
      success: true,
      transactionHash: eventData['transaction_hash'],
      oldTier: int.parse(eventData['old_tier']?.toString() ?? '0'),
      newTier: int.parse(eventData['new_tier']?.toString() ?? '0'),
      xpSpent: int.parse(eventData['xp_spent']?.toString() ?? '0'),
      newBenefits: GasTierBenefits.basicTier(), // Would be parsed from event
    );
  }

  @override
  String toString() {
    return success
        ? 'Upgraded from tier $oldTier to tier $newTier for $xpSpent XP'
        : 'Upgrade failed: $errorMessage';
  }
}

class GasRewardsResult {
  final bool success;
  final String? transactionHash;
  final String? errorMessage;
  final int gasCreditsEarned;
  final BigInt tradingVolume;
  final int streakBonus;
  final int referralBonus;

  const GasRewardsResult({
    required this.success,
    this.transactionHash,
    this.errorMessage,
    required this.gasCreditsEarned,
    required this.tradingVolume,
    required this.streakBonus,
    required this.referralBonus,
  });

  /// Create from contract event data
  factory GasRewardsResult.fromEventData(Map<String, dynamic> eventData) {
    return GasRewardsResult(
      success: true,
      transactionHash: eventData['transaction_hash'],
      gasCreditsEarned: int.parse(eventData['gas_credits_earned']?.toString() ?? '0'),
      tradingVolume: BigInt.parse(eventData['trading_volume']?.toString() ?? '0'),
      streakBonus: int.parse(eventData['streak_bonus']?.toString() ?? '0'),
      referralBonus: int.parse(eventData['referral_bonus']?.toString() ?? '0'),
    );
  }

  /// Get formatted trading volume
  String getFormattedTradingVolume({int decimals = 18}) {
    final divisor = BigInt.from(10).pow(decimals);
    final volume = tradingVolume.toDouble() / divisor.toDouble();
    
    if (volume >= 1000) {
      return '${(volume / 1000).toStringAsFixed(1)}K ETH';
    } else {
      return '${volume.toStringAsFixed(2)} ETH';
    }
  }

  @override
  String toString() {
    return success
        ? 'Earned ${gasCreditsEarned} gas credits from ${getFormattedTradingVolume()} volume'
        : 'Rewards claim failed: $errorMessage';
  }
}

// === Trading Stats ===

class TradingStats {
  final BigInt volume24h;
  final int tradesCount24h;
  final BigInt avgTradeSize;
  final int successfulTradesStreak;
  final int referralsGenerated;

  const TradingStats({
    required this.volume24h,
    required this.tradesCount24h,
    required this.avgTradeSize,
    required this.successfulTradesStreak,
    required this.referralsGenerated,
  });

  /// Create empty trading stats
  factory TradingStats.empty() {
    return const TradingStats(
      volume24h: BigInt.zero,
      tradesCount24h: 0,
      avgTradeSize: BigInt.zero,
      successfulTradesStreak: 0,
      referralsGenerated: 0,
    );
  }

  /// Convert to JSON
  Map<String, dynamic> toJson() {
    return {
      'volume24h': volume24h.toString(),
      'tradesCount24h': tradesCount24h,
      'avgTradeSize': avgTradeSize.toString(),
      'successfulTradesStreak': successfulTradesStreak,
      'referralsGenerated': referralsGenerated,
    };
  }

  /// Create from JSON
  factory TradingStats.fromJson(Map<String, dynamic> json) {
    return TradingStats(
      volume24h: BigInt.parse(json['volume24h'] as String),
      tradesCount24h: json['tradesCount24h'] as int,
      avgTradeSize: BigInt.parse(json['avgTradeSize'] as String),
      successfulTradesStreak: json['successfulTradesStreak'] as int,
      referralsGenerated: json['referralsGenerated'] as int,
    );
  }
}

// === Platform Gas Metrics ===

class PlatformGasMetrics {
  final int totalGasSponsoredToday;
  final int totalUsersSponsoredToday;
  final int averageGasPerTransaction;
  final BigInt totalRevenueFromGas;
  final double gasEfficiencyRatio;

  const PlatformGasMetrics({
    required this.totalGasSponsoredToday,
    required this.totalUsersSponsoredToday,
    required this.averageGasPerTransaction,
    required this.totalRevenueFromGas,
    required this.gasEfficiencyRatio,
  });

  /// Create empty platform metrics
  factory PlatformGasMetrics.empty() {
    return const PlatformGasMetrics(
      totalGasSponsoredToday: 0,
      totalUsersSponsoredToday: 0,
      averageGasPerTransaction: 0,
      totalRevenueFromGas: BigInt.zero,
      gasEfficiencyRatio: 0.85,
    );
  }

  /// Create from contract response
  factory PlatformGasMetrics.fromContractResponse(List<String> response) {
    return PlatformGasMetrics(
      totalGasSponsoredToday: int.parse(response[0]),
      totalUsersSponsoredToday: int.parse(response[1]),
      averageGasPerTransaction: int.parse(response[2]),
      totalRevenueFromGas: BigInt.parse(response[3]),
      gasEfficiencyRatio: int.parse(response[4]) / 10000.0,
    );
  }

  /// Get formatted total gas sponsored
  String get formattedTotalGasSponsored {
    if (totalGasSponsoredToday >= 1000000) {
      return '${(totalGasSponsoredToday / 1000000).toStringAsFixed(1)}M';
    } else if (totalGasSponsoredToday >= 1000) {
      return '${(totalGasSponsoredToday / 1000).toStringAsFixed(1)}K';
    } else {
      return totalGasSponsoredToday.toString();
    }
  }

  /// Get formatted efficiency ratio
  String get formattedEfficiencyRatio {
    return '${(gasEfficiencyRatio * 100).toStringAsFixed(1)}%';
  }

  @override
  String toString() {
    return 'PlatformGasMetrics($formattedTotalGasSponsored gas, $totalUsersSponsoredToday users, $formattedEfficiencyRatio efficiency)';
  }
}

// === Paymaster Events ===

abstract class PaymasterEvent {
  final String userAddress;
  final DateTime timestamp;
  final String transactionHash;

  const PaymasterEvent({
    required this.userAddress,
    required this.timestamp,
    required this.transactionHash,
  });
}

class TransactionSponsoredEvent extends PaymasterEvent {
  final int gasSponsored;
  final int transactionType;
  final int xpEarned;
  final int remainingAllowance;
  final int tierLevel;

  const TransactionSponsoredEvent({
    required super.userAddress,
    required super.timestamp,
    required super.transactionHash,
    required this.gasSponsored,
    required this.transactionType,
    required this.xpEarned,
    required this.remainingAllowance,
    required this.tierLevel,
  });

  @override
  String toString() {
    return 'Sponsored ${gasSponsored} gas (+${xpEarned} XP)';
  }
}

class GasTierUpgradedEvent extends PaymasterEvent {
  final int oldTier;
  final int newTier;
  final GasTierBenefits newBenefits;
  final int xpSpent;

  const GasTierUpgradedEvent({
    required super.userAddress,
    required super.timestamp,
    required super.transactionHash,
    required this.oldTier,
    required this.newTier,
    required this.newBenefits,
    required this.xpSpent,
  });

  @override
  String toString() {
    return 'Upgraded to ${newBenefits.tierName} tier (${xpSpent} XP)';
  }
}

class GasRewardsClaimedEvent extends PaymasterEvent {
  final int gasCreditsEarned;
  final BigInt tradingVolume;
  final int streakBonus;
  final int referralBonus;

  const GasRewardsClaimedEvent({
    required super.userAddress,
    required super.timestamp,
    required super.transactionHash,
    required this.gasCreditsEarned,
    required this.tradingVolume,
    required this.streakBonus,
    required this.referralBonus,
  });

  @override
  String toString() {
    return 'Claimed ${gasCreditsEarned} gas credits (${streakBonus}% streak bonus)';
  }
}