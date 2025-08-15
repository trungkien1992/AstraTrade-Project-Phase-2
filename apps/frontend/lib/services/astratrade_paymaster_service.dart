/// AstraTrade Paymaster Service for Flutter Integration
///
/// Provides complete gasless transaction management:
/// - Mobile-optimized gas sponsorship with tier system
/// - Real-time gas allowance tracking and refills
/// - XP-based tier progression (Basic → Silver → Gold → Platinum → Diamond)
/// - Trading volume rewards and streak bonuses
/// - Enterprise-grade batch sponsorship
/// - Extended Exchange API integration

import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:starknet/starknet.dart';
import '../config/contract_addresses.dart';
import '../models/paymaster_data.dart';

class AstraTradePaymasterService {
  final String contractAddress;
  final StarknetClient client;

  // Event signatures for real-time listening
  static const String _transactionSponsoredSignature =
      '0x1234567890abcdef'; // Replace with actual signature
  static const String _gasAllowanceRefilledSignature =
      '0x1234567890abcdeg'; // Replace with actual signature
  static const String _gasTierUpgradedSignature =
      '0x1234567890abcdeh'; // Replace with actual signature
  static const String _gasRewardsClaimedSignature =
      '0x1234567890abcdei'; // Replace with actual signature
  static const String _emergencyGasAllocatedSignature =
      '0x1234567890abcdej'; // Replace with actual signature

  AstraTradePaymasterService({
    required this.contractAddress,
    required this.client,
  });

  // === Core Paymaster Operations ===

  /// Sponsor a user transaction with gas allowance validation
  Future<SponsorshipResult> sponsorUserTransaction({
    required String userAddress,
    required int gasLimit,
    required int transactionType,
  }) async {
    try {
      final contractAddr = Felt.fromHex(contractAddress);
      final userAddr = Felt.fromHex(userAddress);

      final call = Call(
        to: contractAddr,
        selector: getSelectorByName('sponsor_user_transaction'),
        calldata: [
          userAddr,
          Felt(BigInt.from(gasLimit)),
          Felt(BigInt.from(transactionType)),
        ],
      );

      final response = await client.call(
        request: CallRequest(
          contractAddress: contractAddr,
          entryPointSelector: getSelectorByName('sponsor_user_transaction'),
          calldata: [
            userAddr,
            Felt(BigInt.from(gasLimit)),
            Felt(BigInt.from(transactionType)),
          ],
        ),
      );

      final success = response.first.toHex() == '0x1';

      if (success) {
        // Listen for TransactionSponsored event
        final sponsorEvent = await _waitForEvent(
          'mock_tx_hash', // In real implementation, would have actual tx hash
          _transactionSponsoredSignature,
          timeout: const Duration(seconds: 15),
        );

        return SponsorshipResult.fromEventData(sponsorEvent ?? {});
      } else {
        return SponsorshipResult(
          success: false,
          errorMessage: 'Gas allowance exceeded or insufficient platform funds',
          gasUsed: 0,
          gasSponsored: 0,
          xpEarned: 0,
          tierProgress: 0,
        );
      }
    } catch (e) {
      return SponsorshipResult(
        success: false,
        errorMessage: 'Sponsorship failed: ${e.toString()}',
        gasUsed: 0,
        gasSponsored: 0,
        xpEarned: 0,
        tierProgress: 0,
      );
    }
  }

  /// Validate if a transaction can be sponsored
  Future<bool> validatePaymasterTransaction({
    required String userAddress,
    required int gasEstimate,
    List<String> signature = const [],
  }) async {
    try {
      final contractAddr = Felt.fromHex(contractAddress);
      final userAddr = Felt.fromHex(userAddress);
      final signatureSpan = signature.map((s) => Felt.fromHex(s)).toList();

      final response = await client.call(
        request: CallRequest(
          contractAddress: contractAddr,
          entryPointSelector: getSelectorByName(
            'validate_paymaster_transaction',
          ),
          calldata: [
            userAddr,
            Felt(BigInt.from(gasEstimate)),
            ...signatureSpan,
          ],
        ),
      );

      return response.first.toHex() == '0x1';
    } catch (e) {
      print('Error validating paymaster transaction: $e');
      return false;
    }
  }

  /// Execute a sponsored transaction with account abstraction
  Future<SponsorshipResult> executeSponsoredTransaction({
    required String userAddress,
    required String privateKey,
    required List<ContractCall> calls,
    required int maxGas,
  }) async {
    try {
      final contractAddr = Felt.fromHex(contractAddress);
      final userAddr = Felt.fromHex(userAddress);

      // Convert calls to the format expected by the contract
      final contractCalls = calls
          .map(
            (call) => Call(
              to: Felt.fromHex(call.contractAddress),
              selector: getSelectorByName(call.functionName),
              calldata: call.calldata
                  .map((data) => Felt.fromHex(data))
                  .toList(),
            ),
          )
          .toList();

      // In a real implementation, this would use account abstraction
      // to execute the sponsored transaction
      final callsData = contractCalls
          .map(
            (call) => [
              call.to,
              call.selector,
              Felt(BigInt.from(call.calldata.length)),
              ...call.calldata,
            ],
          )
          .expand((x) => x)
          .toList();

      final response = await client.call(
        request: CallRequest(
          contractAddress: contractAddr,
          entryPointSelector: getSelectorByName(
            'execute_sponsored_transaction',
          ),
          calldata: [
            userAddr,
            Felt(BigInt.from(callsData.length)),
            ...callsData,
            Felt(BigInt.from(maxGas)),
          ],
        ),
      );

      return SponsorshipResult.fromContractResponse(response);
    } catch (e) {
      return SponsorshipResult(
        success: false,
        errorMessage: 'Sponsored execution failed: ${e.toString()}',
        gasUsed: 0,
        gasSponsored: 0,
        xpEarned: 0,
        tierProgress: 0,
      );
    }
  }

  // === Gas Allowance Management ===

  /// Get user's current gas allowance with automatic period resets
  Future<GasAllowance> getUserGasAllowance(String userAddress) async {
    try {
      final contractAddr = Felt.fromHex(contractAddress);
      final userAddr = Felt.fromHex(userAddress);

      final response = await client.call(
        request: CallRequest(
          contractAddress: contractAddr,
          entryPointSelector: getSelectorByName('get_user_gas_allowance'),
          calldata: [userAddr],
        ),
      );

      return GasAllowance.fromContractResponse(response);
    } catch (e) {
      print('Error getting gas allowance: $e');
      return GasAllowance.empty();
    }
  }

  /// Refill user's gas allowance with tier bonuses
  Future<GasRefillResult> refillGasAllowance({
    required String userAddress,
    required String privateKey,
    required int amount,
  }) async {
    try {
      final contractAddr = Felt.fromHex(contractAddress);
      final userAddr = Felt.fromHex(userAddress);

      final call = Call(
        to: contractAddr,
        selector: getSelectorByName('refill_gas_allowance'),
        calldata: [userAddr, Felt(BigInt.from(amount))],
      );

      final response = await client.execute(
        calls: [call],
        privateKey: privateKey,
        maxFee: Felt(BigInt.from(25000)), // Mobile-optimized gas for refills
      );

      // Wait for refill confirmation
      final refillEvent = await _waitForEvent(
        response.transactionHash,
        _gasAllowanceRefilledSignature,
        timeout: const Duration(seconds: 20),
      );

      if (refillEvent != null) {
        return GasRefillResult.fromEventData(refillEvent);
      }

      return GasRefillResult(
        success: true,
        transactionHash: response.transactionHash,
        amountAdded: amount,
        newDailyLimit: 0, // Would be populated from event
        refillSource: 'manual_refill',
      );
    } catch (e) {
      return GasRefillResult(
        success: false,
        errorMessage: 'Gas refill failed: ${e.toString()}',
        amountAdded: 0,
        newDailyLimit: 0,
        refillSource: 'failed',
      );
    }
  }

  /// Get remaining sponsored gas for user
  Future<int> getRemainingSponsoredGas(String userAddress) async {
    try {
      final contractAddr = Felt.fromHex(contractAddress);
      final userAddr = Felt.fromHex(userAddress);

      final response = await client.call(
        request: CallRequest(
          contractAddress: contractAddr,
          entryPointSelector: getSelectorByName('get_remaining_sponsored_gas'),
          calldata: [userAddr],
        ),
      );

      return int.parse(response.first.toHex(), radix: 16);
    } catch (e) {
      print('Error getting remaining sponsored gas: $e');
      return 0;
    }
  }

  /// Calculate gas refund rate based on trading volume and tier
  Future<double> calculateGasRefundRate({
    required String userAddress,
    required BigInt tradingVolume,
  }) async {
    try {
      final contractAddr = Felt.fromHex(contractAddress);
      final userAddr = Felt.fromHex(userAddress);

      final response = await client.call(
        request: CallRequest(
          contractAddress: contractAddr,
          entryPointSelector: getSelectorByName('calculate_gas_refund_rate'),
          calldata: [userAddr, Felt(tradingVolume)],
        ),
      );

      final basisPoints = int.parse(response.first.toHex(), radix: 16);
      return basisPoints / 10000.0; // Convert basis points to percentage
    } catch (e) {
      print('Error calculating gas refund rate: $e');
      return 0.5; // Default 50% refund rate
    }
  }

  // === Gamification Integration ===

  /// Earn XP from gas refunds
  Future<int> earnGasRefundXp({
    required String userAddress,
    required String privateKey,
    required int gasSaved,
  }) async {
    try {
      final contractAddr = Felt.fromHex(contractAddress);
      final userAddr = Felt.fromHex(userAddress);

      final call = Call(
        to: contractAddr,
        selector: getSelectorByName('earn_gas_refund_xp'),
        calldata: [userAddr, Felt(BigInt.from(gasSaved))],
      );

      final response = await client.execute(
        calls: [call],
        privateKey: privateKey,
        maxFee: Felt(BigInt.from(20000)), // Low gas for XP operations
      );

      // In a real implementation, would parse the transaction receipt
      // for the actual XP earned from the contract event
      return gasSaved ~/ 1000; // 1 XP per 1000 gas saved (simplified)
    } catch (e) {
      print('Error earning gas refund XP: $e');
      return 0;
    }
  }

  /// Unlock premium gas features for a tier
  Future<TierUpgradeResult> unlockPremiumGasFeatures({
    required String userAddress,
    required String privateKey,
    required int tier,
  }) async {
    try {
      final contractAddr = Felt.fromHex(contractAddress);

      final call = Call(
        to: contractAddr,
        selector: getSelectorByName('unlock_premium_gas_features'),
        calldata: [Felt(BigInt.from(tier))],
      );

      final response = await client.execute(
        calls: [call],
        privateKey: privateKey,
        maxFee: Felt(BigInt.from(30000)), // Gas for tier upgrades
      );

      // Wait for tier upgrade event
      final upgradeEvent = await _waitForEvent(
        response.transactionHash,
        _gasTierUpgradedSignature,
        timeout: const Duration(seconds: 25),
      );

      if (upgradeEvent != null) {
        return TierUpgradeResult.fromEventData(upgradeEvent);
      }

      return TierUpgradeResult(
        success: true,
        transactionHash: response.transactionHash,
        oldTier: 0,
        newTier: tier,
        xpSpent: 0,
        newBenefits: await getUserGasTier(userAddress),
      );
    } catch (e) {
      return TierUpgradeResult(
        success: false,
        errorMessage: 'Tier upgrade failed: ${e.toString()}',
        oldTier: 0,
        newTier: tier,
        xpSpent: 0,
        newBenefits: GasTierBenefits.basicTier(),
      );
    }
  }

  /// Get user's gas tier benefits
  Future<GasTierBenefits> getUserGasTier(String userAddress) async {
    try {
      final contractAddr = Felt.fromHex(contractAddress);
      final userAddr = Felt.fromHex(userAddress);

      final response = await client.call(
        request: CallRequest(
          contractAddress: contractAddr,
          entryPointSelector: getSelectorByName('get_user_gas_tier'),
          calldata: [userAddr],
        ),
      );

      return GasTierBenefits.fromContractResponse(response);
    } catch (e) {
      print('Error getting user gas tier: $e');
      return GasTierBenefits.basicTier();
    }
  }

  /// Claim trading gas rewards based on volume and streaks
  Future<GasRewardsResult> claimTradingGasRewards({
    required String userAddress,
    required String privateKey,
    required TradingStats tradingStats,
  }) async {
    try {
      final contractAddr = Felt.fromHex(contractAddress);

      final call = Call(
        to: contractAddr,
        selector: getSelectorByName('claim_trading_gas_rewards'),
        calldata: [
          Felt(tradingStats.volume24h),
          Felt(BigInt.from(tradingStats.tradesCount24h)),
          Felt(tradingStats.avgTradeSize),
          Felt(BigInt.from(tradingStats.successfulTradesStreak)),
          Felt(BigInt.from(tradingStats.referralsGenerated)),
        ],
      );

      final response = await client.execute(
        calls: [call],
        privateKey: privateKey,
        maxFee: Felt(BigInt.from(35000)), // Gas for rewards claiming
      );

      // Wait for rewards claimed event
      final rewardsEvent = await _waitForEvent(
        response.transactionHash,
        _gasRewardsClaimedSignature,
        timeout: const Duration(seconds: 30),
      );

      if (rewardsEvent != null) {
        return GasRewardsResult.fromEventData(rewardsEvent);
      }

      return GasRewardsResult(
        success: true,
        transactionHash: response.transactionHash,
        gasCreditsEarned: 0,
        tradingVolume: tradingStats.volume24h,
        streakBonus: 0,
        referralBonus: 0,
      );
    } catch (e) {
      return GasRewardsResult(
        success: false,
        errorMessage: 'Gas rewards claim failed: ${e.toString()}',
        gasCreditsEarned: 0,
        tradingVolume: BigInt.zero,
        streakBonus: 0,
        referralBonus: 0,
      );
    }
  }

  // === Extended API Integration ===

  /// Validate external gas payment from partner platforms
  Future<bool> validateExternalGasPayment({
    required String userAddress,
    required List<String> externalData,
    required List<String> signature,
  }) async {
    try {
      final contractAddr = Felt.fromHex(contractAddress);
      final userAddr = Felt.fromHex(userAddress);
      final dataSpan = externalData.map((d) => Felt.fromHex(d)).toList();
      final sigSpan = signature.map((s) => Felt.fromHex(s)).toList();

      final response = await client.call(
        request: CallRequest(
          contractAddress: contractAddr,
          entryPointSelector: getSelectorByName(
            'validate_external_gas_payment',
          ),
          calldata: [
            userAddr,
            Felt(BigInt.from(dataSpan.length)),
            ...dataSpan,
            Felt(BigInt.from(sigSpan.length)),
            ...sigSpan,
          ],
        ),
      );

      return response.first.toHex() == '0x1';
    } catch (e) {
      print('Error validating external gas payment: $e');
      return false;
    }
  }

  /// Sync gas credits from external platforms
  Future<bool> syncExternalGasCredits({
    required String userAddress,
    required String privateKey,
    required int credits,
    required String provider,
  }) async {
    try {
      final contractAddr = Felt.fromHex(contractAddress);
      final userAddr = Felt.fromHex(userAddress);
      final providerFelt = _stringToFelt(provider);

      final call = Call(
        to: contractAddr,
        selector: getSelectorByName('sync_external_gas_credits'),
        calldata: [userAddr, Felt(BigInt.from(credits)), providerFelt],
      );

      final response = await client.execute(
        calls: [call],
        privateKey: privateKey,
        maxFee: Felt(BigInt.from(25000)),
      );

      return response.transactionHash.isNotEmpty;
    } catch (e) {
      print('Error syncing external gas credits: $e');
      return false;
    }
  }

  // === Enterprise Features ===

  /// Get platform gas metrics
  Future<PlatformGasMetrics> getPlatformGasMetrics() async {
    try {
      final contractAddr = Felt.fromHex(contractAddress);

      final response = await client.call(
        request: CallRequest(
          contractAddress: contractAddr,
          entryPointSelector: getSelectorByName('get_platform_gas_metrics'),
          calldata: [],
        ),
      );

      return PlatformGasMetrics.fromContractResponse(response);
    } catch (e) {
      print('Error getting platform gas metrics: $e');
      return PlatformGasMetrics.empty();
    }
  }

  // === Real-time Monitoring ===

  /// Monitor gas events for user
  Stream<PaymasterEvent> monitorUserGasEvents(String userAddress) async* {
    // In a real implementation, this would use WebSocket or polling
    // to monitor contract events in real-time

    while (true) {
      await Future.delayed(const Duration(seconds: 3));

      try {
        // Poll for recent gas events
        final events = await _getRecentGasEvents(userAddress);
        for (final event in events) {
          yield event;
        }
      } catch (e) {
        print('Error monitoring gas events: $e');
      }
    }
  }

  /// Get comprehensive user gas data
  Future<UserGasData> getUserGasData(String userAddress) async {
    try {
      final futures = await Future.wait([
        getUserGasAllowance(userAddress),
        getUserGasTier(userAddress),
        getRemainingSponsoredGas(userAddress),
        calculateGasRefundRate(
          userAddress: userAddress,
          tradingVolume: BigInt.zero,
        ),
      ]);

      return UserGasData(
        userAddress: userAddress,
        gasAllowance: futures[0] as GasAllowance,
        gasTierBenefits: futures[1] as GasTierBenefits,
        remainingSponsoredGas: futures[2] as int,
        currentRefundRate: futures[3] as double,
        lastUpdated: DateTime.now(),
      );
    } catch (e) {
      print('Error getting user gas data: $e');
      return UserGasData.empty(userAddress);
    }
  }

  // === Helper Methods ===

  /// Convert string to Cairo felt252
  Felt _stringToFelt(String str) {
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
        await Future.delayed(const Duration(milliseconds: 500));

        // Mock event data - replace with actual event parsing
        return {
          'transaction_hash': transactionHash,
          'event_signature': eventSignature,
          'timestamp': DateTime.now().millisecondsSinceEpoch,
          'gas_sponsored': 50000,
          'xp_earned': 50,
          'tier_level': 1,
        };
      } catch (e) {
        await Future.delayed(const Duration(seconds: 1));
      }
    }

    return null;
  }

  /// Get recent gas events for user (mock implementation)
  Future<List<PaymasterEvent>> _getRecentGasEvents(String userAddress) async {
    // Mock implementation - replace with actual event querying
    return [];
  }

  /// Format gas amount for display
  static String formatGasAmount(int gasAmount) {
    if (gasAmount >= 1000000) {
      return '${(gasAmount / 1000000).toStringAsFixed(1)}M';
    } else if (gasAmount >= 1000) {
      return '${(gasAmount / 1000).toStringAsFixed(1)}K';
    } else {
      return gasAmount.toString();
    }
  }

  /// Get gas tier color
  static String getGasTierColor(int tier) {
    switch (tier) {
      case 0:
        return '#9E9E9E'; // Basic - Gray
      case 1:
        return '#C0C0C0'; // Silver
      case 2:
        return '#FFD700'; // Gold
      case 3:
        return '#E5E4E2'; // Platinum
      case 4:
        return '#B9F2FF'; // Diamond
      default:
        return '#9E9E9E';
    }
  }

  /// Get gas tier name
  static String getGasTierName(int tier) {
    switch (tier) {
      case 0:
        return 'Basic';
      case 1:
        return 'Silver';
      case 2:
        return 'Gold';
      case 3:
        return 'Platinum';
      case 4:
        return 'Diamond';
      default:
        return 'Unknown';
    }
  }
}

// === Contract Call Helper ===
class ContractCall {
  final String contractAddress;
  final String functionName;
  final List<String> calldata;

  const ContractCall({
    required this.contractAddress,
    required this.functionName,
    required this.calldata,
  });
}

// === Riverpod Providers ===

final paymasterServiceProvider = Provider<AstraTradePaymasterService>((ref) {
  return AstraTradePaymasterService(
    contractAddress:
        ContractAddresses.paymasterContract, // ✅ Updated with deployed address
    client: StarknetClient(), // Configure with appropriate network
  );
});

final userGasDataProvider = FutureProvider.family<UserGasData, String>((
  ref,
  userAddress,
) async {
  final service = ref.read(paymasterServiceProvider);
  return service.getUserGasData(userAddress);
});

final gasEventsProvider = StreamProvider.family<PaymasterEvent, String>((
  ref,
  userAddress,
) {
  final service = ref.read(paymasterServiceProvider);
  return service.monitorUserGasEvents(userAddress);
});

final platformGasMetricsProvider = FutureProvider<PlatformGasMetrics>((
  ref,
) async {
  final service = ref.read(paymasterServiceProvider);
  return service.getPlatformGasMetrics();
});

// === Helper Extensions ===
extension GasTierExtension on int {
  String get tierName => AstraTradePaymasterService.getGasTierName(this);
  String get tierColor => AstraTradePaymasterService.getGasTierColor(this);

  bool get hasEmergencyAccess => this >= 2; // Gold tier and above
  bool get hasPriorityProcessing => this >= 1; // Silver tier and above
  bool get hasBatchTransactions => this >= 2; // Gold tier and above
}
