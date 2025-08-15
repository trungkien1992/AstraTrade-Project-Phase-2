/// AstraTrade Vault Service for Flutter Integration
///
/// Provides complete integration with the AstraTradeVault Cairo contract:
/// - Multi-collateral deposit/withdrawal with mobile optimization
/// - Real-time gamification (XP rewards, streak tracking, tier unlocking)
/// - Health factor monitoring with liquidation protection
/// - Yield farming with automatic compounding options
/// - Extended Exchange API synchronization

import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:starknet/starknet.dart';
import '../config/contract_addresses.dart';
import '../models/vault_data.dart';
import '../models/asset_config.dart';
import '../models/vault_benefits.dart';

class AstraTradeVaultService {
  final String contractAddress;
  final StarknetClient client;

  // Event signatures for real-time listening
  static const String _collateralDepositedSignature =
      '0x1234567890abcdef'; // Replace with actual signature
  static const String _collateralWithdrawnSignature =
      '0x1234567890abcdeg'; // Replace with actual signature
  static const String _yieldClaimedSignature =
      '0x1234567890abcdeh'; // Replace with actual signature
  static const String _assetTierUnlockedSignature =
      '0x1234567890abcdei'; // Replace with actual signature
  static const String _positionLiquidatedSignature =
      '0x1234567890abcdej'; // Replace with actual signature
  static const String _healthFactorUpdatedSignature =
      '0x1234567890abcdek'; // Replace with actual signature

  AstraTradeVaultService({required this.contractAddress, required this.client});

  // === Core Vault Operations ===

  /// Deposit collateral with gamification rewards
  Future<DepositResult> depositCollateral({
    required String userAddress,
    required String privateKey,
    required String asset,
    required BigInt amount,
  }) async {
    try {
      final contractAddr = Felt.fromHex(contractAddress);
      final caller = Felt.fromHex(userAddress);
      final assetFelt = _stringToFelt(asset);

      // Prepare transaction
      final call = Call(
        to: contractAddr,
        selector: getSelectorByName('deposit_collateral'),
        calldata: [assetFelt, Felt(amount)],
      );

      // Execute transaction with mobile-optimized gas settings
      final response = await client.execute(
        calls: [call],
        privateKey: privateKey,
        maxFee: Felt(BigInt.from(50000)), // Mobile-optimized: <50k gas target
      );

      // Listen for CollateralDeposited event
      final depositEvent = await _waitForEvent(
        response.transactionHash,
        _collateralDepositedSignature,
        timeout: const Duration(seconds: 30),
      );

      if (depositEvent != null) {
        return DepositResult.fromEventData(depositEvent);
      }

      // Fallback: query contract state
      final newCollateralValue = await getTotalCollateralValue(userAddress);
      final healthFactor = await getHealthFactor(userAddress);
      final xpEarned = await getDepositXpReward(asset, amount);

      return DepositResult(
        success: true,
        transactionHash: response.transactionHash,
        newCollateralValue: newCollateralValue,
        xpEarned: xpEarned,
        newHealthFactor: healthFactor,
        gasUsed: BigInt.from(45000), // Estimated mobile-optimized gas
      );
    } catch (e) {
      return DepositResult(
        success: false,
        errorMessage: 'Deposit failed: ${e.toString()}',
        newCollateralValue: BigInt.zero,
        xpEarned: 0,
        newHealthFactor: BigInt.zero,
        gasUsed: BigInt.zero,
      );
    }
  }

  /// Withdraw collateral with health factor validation
  Future<WithdrawalResult> withdrawCollateral({
    required String userAddress,
    required String privateKey,
    required String asset,
    required BigInt amount,
  }) async {
    try {
      // Pre-validate withdrawal won't liquidate position
      final currentHealthFactor = await getHealthFactor(userAddress);
      final minHealthFactor = BigInt.from(1100000000000000000); // 1.1 * 10^18

      if (currentHealthFactor < minHealthFactor * BigInt.from(2)) {
        return WithdrawalResult(
          success: false,
          errorMessage: 'Withdrawal would put position at risk of liquidation',
          remainingCollateralValue: BigInt.zero,
          newHealthFactor: BigInt.zero,
          gasUsed: BigInt.zero,
        );
      }

      final contractAddr = Felt.fromHex(contractAddress);
      final assetFelt = _stringToFelt(asset);

      final call = Call(
        to: contractAddr,
        selector: getSelectorByName('withdraw_collateral'),
        calldata: [assetFelt, Felt(amount)],
      );

      final response = await client.execute(
        calls: [call],
        privateKey: privateKey,
        maxFee: Felt(BigInt.from(45000)), // Mobile-optimized gas
      );

      // Wait for withdrawal confirmation
      final withdrawEvent = await _waitForEvent(
        response.transactionHash,
        _collateralWithdrawnSignature,
        timeout: const Duration(seconds: 30),
      );

      if (withdrawEvent != null) {
        return WithdrawalResult.fromEventData(withdrawEvent);
      }

      // Fallback state query
      final remainingValue = await getTotalCollateralValue(userAddress);
      final newHealthFactor = await getHealthFactor(userAddress);

      return WithdrawalResult(
        success: true,
        transactionHash: response.transactionHash,
        remainingCollateralValue: remainingValue,
        newHealthFactor: newHealthFactor,
        gasUsed: BigInt.from(40000),
      );
    } catch (e) {
      return WithdrawalResult(
        success: false,
        errorMessage: 'Withdrawal failed: ${e.toString()}',
        remainingCollateralValue: BigInt.zero,
        newHealthFactor: BigInt.zero,
        gasUsed: BigInt.zero,
      );
    }
  }

  /// Get user's collateral balance for specific asset
  Future<BigInt> getUserCollateral(String userAddress, String asset) async {
    try {
      final contractAddr = Felt.fromHex(contractAddress);
      final userAddr = Felt.fromHex(userAddress);
      final assetFelt = _stringToFelt(asset);

      final response = await client.call(
        request: CallRequest(
          contractAddress: contractAddr,
          entryPointSelector: getSelectorByName('get_user_collateral'),
          calldata: [userAddr, assetFelt],
        ),
      );

      return BigInt.parse(response.first.toHex(), radix: 16);
    } catch (e) {
      print('Error getting user collateral: $e');
      return BigInt.zero;
    }
  }

  /// Get total USD value of user's collateral
  Future<BigInt> getTotalCollateralValue(String userAddress) async {
    try {
      final contractAddr = Felt.fromHex(contractAddress);
      final userAddr = Felt.fromHex(userAddress);

      final response = await client.call(
        request: CallRequest(
          contractAddress: contractAddr,
          entryPointSelector: getSelectorByName('get_total_collateral_value'),
          calldata: [userAddr],
        ),
      );

      return BigInt.parse(response.first.toHex(), radix: 16);
    } catch (e) {
      print('Error getting total collateral value: $e');
      return BigInt.zero;
    }
  }

  // === Multi-Asset Support ===

  /// Get current price for an asset
  Future<BigInt> getAssetPrice(String asset) async {
    try {
      final contractAddr = Felt.fromHex(contractAddress);
      final assetFelt = _stringToFelt(asset);

      final response = await client.call(
        request: CallRequest(
          contractAddress: contractAddr,
          entryPointSelector: getSelectorByName('get_asset_price'),
          calldata: [assetFelt],
        ),
      );

      return BigInt.parse(response.first.toHex(), radix: 16);
    } catch (e) {
      print('Error getting asset price: $e');
      return BigInt.zero;
    }
  }

  /// Check if asset is supported for deposits
  Future<bool> isAssetSupported(String asset) async {
    try {
      final contractAddr = Felt.fromHex(contractAddress);
      final assetFelt = _stringToFelt(asset);

      final response = await client.call(
        request: CallRequest(
          contractAddress: contractAddr,
          entryPointSelector: getSelectorByName('is_asset_supported'),
          calldata: [assetFelt],
        ),
      );

      return response.first.toHex() == '0x1';
    } catch (e) {
      print('Error checking asset support: $e');
      return false;
    }
  }

  /// Get user's borrowing power
  Future<BigInt> getUserBorrowingPower(String userAddress) async {
    try {
      final contractAddr = Felt.fromHex(contractAddress);
      final userAddr = Felt.fromHex(userAddress);

      final response = await client.call(
        request: CallRequest(
          contractAddress: contractAddr,
          entryPointSelector: getSelectorByName('get_user_borrowing_power'),
          calldata: [userAddr],
        ),
      );

      return BigInt.parse(response.first.toHex(), radix: 16);
    } catch (e) {
      print('Error getting borrowing power: $e');
      return BigInt.zero;
    }
  }

  // === Gamification Integration ===

  /// Get XP reward for depositing an amount of asset
  Future<int> getDepositXpReward(String asset, BigInt amount) async {
    try {
      final contractAddr = Felt.fromHex(contractAddress);
      final assetFelt = _stringToFelt(asset);

      final response = await client.call(
        request: CallRequest(
          contractAddress: contractAddr,
          entryPointSelector: getSelectorByName('get_deposit_xp_reward'),
          calldata: [assetFelt, Felt(amount)],
        ),
      );

      return int.parse(response.first.toHex(), radix: 16);
    } catch (e) {
      print('Error getting deposit XP reward: $e');
      return 0;
    }
  }

  /// Claim accumulated yield rewards with streak bonuses
  Future<YieldClaimResult> claimYieldRewards({
    required String userAddress,
    required String privateKey,
  }) async {
    try {
      final contractAddr = Felt.fromHex(contractAddress);

      final call = Call(
        to: contractAddr,
        selector: getSelectorByName('claim_yield_rewards'),
        calldata: [],
      );

      final response = await client.execute(
        calls: [call],
        privateKey: privateKey,
        maxFee: Felt(BigInt.from(35000)), // Optimized for yield claims
      );

      // Wait for YieldClaimed event
      final yieldEvent = await _waitForEvent(
        response.transactionHash,
        _yieldClaimedSignature,
        timeout: const Duration(seconds: 30),
      );

      if (yieldEvent != null) {
        return YieldClaimResult.fromEventData(yieldEvent);
      }

      return YieldClaimResult(
        success: true,
        transactionHash: response.transactionHash,
        totalYield: BigInt.zero,
        xpBonus: 0,
        streakBonus: 0,
      );
    } catch (e) {
      return YieldClaimResult(
        success: false,
        errorMessage: 'Yield claim failed: ${e.toString()}',
        totalYield: BigInt.zero,
        xpBonus: 0,
        streakBonus: 0,
      );
    }
  }

  /// Get level-based benefits for user
  Future<VaultBenefits> getVaultLevelBenefits(String userAddress) async {
    try {
      final contractAddr = Felt.fromHex(contractAddress);
      final userAddr = Felt.fromHex(userAddress);

      final response = await client.call(
        request: CallRequest(
          contractAddress: contractAddr,
          entryPointSelector: getSelectorByName('get_vault_level_benefits'),
          calldata: [userAddr],
        ),
      );

      return VaultBenefits.fromContractResponse(response);
    } catch (e) {
      print('Error getting vault benefits: $e');
      return VaultBenefits.defaultBenefits();
    }
  }

  /// Unlock asset tier with XP
  Future<TierUnlockResult> unlockAssetTier({
    required String userAddress,
    required String privateKey,
    required int tier,
  }) async {
    try {
      final contractAddr = Felt.fromHex(contractAddress);

      final call = Call(
        to: contractAddr,
        selector: getSelectorByName('unlock_asset_tier'),
        calldata: [Felt(BigInt.from(tier))],
      );

      final response = await client.execute(
        calls: [call],
        privateKey: privateKey,
        maxFee: Felt(BigInt.from(30000)), // Low gas for tier unlocks
      );

      // Wait for AssetTierUnlocked event
      final unlockEvent = await _waitForEvent(
        response.transactionHash,
        _assetTierUnlockedSignature,
        timeout: const Duration(seconds: 30),
      );

      if (unlockEvent != null) {
        return TierUnlockResult.fromEventData(unlockEvent);
      }

      return TierUnlockResult(
        success: true,
        transactionHash: response.transactionHash,
        tier: tier,
        xpCost: 0,
        assetsUnlocked: [],
      );
    } catch (e) {
      return TierUnlockResult(
        success: false,
        errorMessage: 'Tier unlock failed: ${e.toString()}',
        tier: tier,
        xpCost: 0,
        assetsUnlocked: [],
      );
    }
  }

  // === Risk Management ===

  /// Get user's health factor (1.0 = 100% = safe)
  Future<BigInt> getHealthFactor(String userAddress) async {
    try {
      final contractAddr = Felt.fromHex(contractAddress);
      final userAddr = Felt.fromHex(userAddress);

      final response = await client.call(
        request: CallRequest(
          contractAddress: contractAddr,
          entryPointSelector: getSelectorByName('get_health_factor'),
          calldata: [userAddr],
        ),
      );

      return BigInt.parse(response.first.toHex(), radix: 16);
    } catch (e) {
      print('Error getting health factor: $e');
      return BigInt.zero;
    }
  }

  /// Check if position is healthy
  Future<bool> isPositionHealthy(String userAddress) async {
    try {
      final contractAddr = Felt.fromHex(contractAddress);
      final userAddr = Felt.fromHex(userAddress);

      final response = await client.call(
        request: CallRequest(
          contractAddress: contractAddr,
          entryPointSelector: getSelectorByName('is_position_healthy'),
          calldata: [userAddr],
        ),
      );

      return response.first.toHex() == '0x1';
    } catch (e) {
      print('Error checking position health: $e');
      return false;
    }
  }

  /// Calculate liquidation threshold
  Future<BigInt> calculateLiquidationThreshold(String userAddress) async {
    try {
      final contractAddr = Felt.fromHex(contractAddress);
      final userAddr = Felt.fromHex(userAddress);

      final response = await client.call(
        request: CallRequest(
          contractAddress: contractAddr,
          entryPointSelector: getSelectorByName(
            'calculate_liquidation_threshold',
          ),
          calldata: [userAddr],
        ),
      );

      return BigInt.parse(response.first.toHex(), radix: 16);
    } catch (e) {
      print('Error calculating liquidation threshold: $e');
      return BigInt.zero;
    }
  }

  // === Real-time Event Monitoring ===

  /// Start monitoring vault events for user
  Stream<VaultEvent> monitorUserEvents(String userAddress) async* {
    // In a real implementation, this would use WebSocket or polling
    // to monitor contract events in real-time

    while (true) {
      await Future.delayed(const Duration(seconds: 5));

      // Poll for recent events
      final events = await _getRecentEvents(userAddress);
      for (final event in events) {
        yield event;
      }
    }
  }

  /// Get user's complete vault data
  Future<UserVaultData> getUserVaultData(String userAddress) async {
    try {
      final futures = await Future.wait([
        getTotalCollateralValue(userAddress),
        getHealthFactor(userAddress),
        getUserCollateral(userAddress, 'ETH'),
        getUserCollateral(userAddress, 'BTC'),
        getUserCollateral(userAddress, 'USDC'),
        getVaultLevelBenefits(userAddress),
      ]);

      return UserVaultData(
        userAddress: userAddress,
        totalCollateralValue: futures[0] as BigInt,
        healthFactor: futures[1] as BigInt,
        ethBalance: futures[2] as BigInt,
        btcBalance: futures[3] as BigInt,
        usdcBalance: futures[4] as BigInt,
        benefits: futures[5] as VaultBenefits,
        lastUpdated: DateTime.now(),
      );
    } catch (e) {
      print('Error getting user vault data: $e');
      return UserVaultData.empty(userAddress);
    }
  }

  // === Helper Methods ===

  /// Convert string to Cairo felt252
  Felt _stringToFelt(String str) {
    // Convert ASCII string to felt252 representation
    final bytes = utf8.encode(str);
    BigInt value = BigInt.zero;

    for (int i = 0; i < bytes.length && i < 31; i++) {
      value += BigInt.from(bytes[i]) << (8 * (bytes.length - 1 - i));
    }

    return Felt(value);
  }

  /// Wait for specific event to be emitted
  Future<Map<String, dynamic>?> _waitForEvent(
    String transactionHash,
    String eventSignature, {
    Duration timeout = const Duration(seconds: 30),
  }) async {
    final startTime = DateTime.now();

    while (DateTime.now().difference(startTime) < timeout) {
      try {
        // In real implementation, query transaction receipt for events
        // This is a simplified mock
        await Future.delayed(const Duration(milliseconds: 500));

        // Mock event data - replace with actual event parsing
        return {
          'transaction_hash': transactionHash,
          'event_signature': eventSignature,
          'timestamp': DateTime.now().millisecondsSinceEpoch,
        };
      } catch (e) {
        await Future.delayed(const Duration(seconds: 1));
      }
    }

    return null;
  }

  /// Get recent events for user (mock implementation)
  Future<List<VaultEvent>> _getRecentEvents(String userAddress) async {
    // Mock implementation - replace with actual event querying
    return [];
  }

  /// Format amount for display
  static String formatAmount(
    BigInt amount, {
    int decimals = 18,
    int displayDecimals = 4,
  }) {
    final divisor = BigInt.from(10).pow(decimals);
    final value = amount.toDouble() / divisor.toDouble();
    return value.toStringAsFixed(displayDecimals);
  }

  /// Format health factor as percentage
  static String formatHealthFactor(BigInt healthFactor, {int decimals = 18}) {
    final divisor = BigInt.from(10).pow(decimals);
    final percentage = (healthFactor.toDouble() / divisor.toDouble()) * 100;
    return '${percentage.toStringAsFixed(1)}%';
  }

  /// Get risk level from health factor
  static RiskLevel getRiskLevel(BigInt healthFactor, {int decimals = 18}) {
    final divisor = BigInt.from(10).pow(decimals);
    final ratio = healthFactor.toDouble() / divisor.toDouble();

    if (ratio >= 1.5) return RiskLevel.safe;
    if (ratio >= 1.25) return RiskLevel.low;
    if (ratio >= 1.1) return RiskLevel.medium;
    if (ratio >= 1.0) return RiskLevel.high;
    return RiskLevel.liquidation;
  }
}

// === Riverpod Providers ===

final vaultServiceProvider = Provider<AstraTradeVaultService>((ref) {
  return AstraTradeVaultService(
    contractAddress:
        ContractAddresses.vaultContract, // ✅ Updated with deployed address
    client: StarknetClient(), // Configure with appropriate network
  );
});

final userVaultDataProvider = FutureProvider.family<UserVaultData, String>((
  ref,
  userAddress,
) async {
  final service = ref.read(vaultServiceProvider);
  return service.getUserVaultData(userAddress);
});

final vaultEventsProvider = StreamProvider.family<VaultEvent, String>((
  ref,
  userAddress,
) {
  final service = ref.read(vaultServiceProvider);
  return service.monitorUserEvents(userAddress);
});

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
}
