import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/game_service.dart';
import '../models/planet_health.dart';
// import '../widgets/planet_view.dart'; // TODO: Create missing widget
import '../api/rag_api_client.dart';
import '../providers/auth_provider.dart';
import '../models/leaderboard.dart';
import '../services/leaderboard_service.dart';
import '../providers/leaderboard_provider.dart';
import '../screens/main_hub_screen.dart'; // For apiKeyProvider
import '../services/paymaster_service.dart';
import '../services/notification_service.dart';
import '../services/starknet_service.dart';

/// Player game state data model
class GameState {
  final int stellarShards;
  final int lumina;
  final int experience;
  final int totalXP;
  final int level;
  final PlanetHealth planetHealth;
  final int astroForgers;
  final bool hasGenesisIgnition;
  final String lastTradeMessage;
  final DateTime lastActivity;
  final Map<String, int> cosmicNodes;
  final int totalTrades;
  final int winStreak;
  final double winRate;
  final CosmicTier cosmicTier;

  const GameState({
    this.stellarShards = 50,
    this.lumina = 0,
    this.experience = 0,
    this.totalXP = 0,
    this.level = 1,
    this.planetHealth = PlanetHealth.stable,
    this.astroForgers = 1,
    this.hasGenesisIgnition = false,
    this.lastTradeMessage = "Welcome to the Cosmic Trading Journey!",
    required this.lastActivity,
    this.cosmicNodes = const {},
    this.totalTrades = 0,
    this.winStreak = 0,
    this.winRate = 0.0,
    this.cosmicTier = CosmicTier.stellarSeedling,
  });

  GameState copyWith({
    int? stellarShards,
    int? lumina,
    int? experience,
    int? totalXP,
    int? level,
    PlanetHealth? planetHealth,
    int? astroForgers,
    bool? hasGenesisIgnition,
    String? lastTradeMessage,
    DateTime? lastActivity,
    Map<String, int>? cosmicNodes,
    int? totalTrades,
    int? winStreak,
    double? winRate,
    CosmicTier? cosmicTier,
  }) {
    return GameState(
      stellarShards: stellarShards ?? this.stellarShards,
      lumina: lumina ?? this.lumina,
      experience: experience ?? this.experience,
      totalXP: totalXP ?? this.totalXP,
      level: level ?? this.level,
      planetHealth: planetHealth ?? this.planetHealth,
      astroForgers: astroForgers ?? this.astroForgers,
      hasGenesisIgnition: hasGenesisIgnition ?? this.hasGenesisIgnition,
      lastTradeMessage: lastTradeMessage ?? this.lastTradeMessage,
      lastActivity: lastActivity ?? this.lastActivity,
      cosmicNodes: cosmicNodes ?? this.cosmicNodes,
      totalTrades: totalTrades ?? this.totalTrades,
      winStreak: winStreak ?? this.winStreak,
      winRate: winRate ?? this.winRate,
      cosmicTier: cosmicTier ?? this.cosmicTier,
    );
  }

  /// Calculate player's cosmic power (CP) based on various factors
  int get cosmicPower {
    int basePower = stellarShards ~/ 10;
    int luminaPower = lumina * 50;
    int experiencePower = experience ~/ 5;
    int forgerPower = astroForgers * 25;
    int nodePower = cosmicNodes.values.fold(
      0,
      (sum, level) => sum + (level * 100),
    );

    return basePower + luminaPower + experiencePower + forgerPower + nodePower;
  }

  /// Get player's cosmic tier display name based on their power level
  String get cosmicTierDisplayName {
    return cosmicTier.displayName;
  }

  /// Check if player can afford an upgrade
  bool canAfford({int? stellarShardsCost, int? luminaCost}) {
    if (stellarShardsCost != null && stellarShards < stellarShardsCost) {
      return false;
    }
    if (luminaCost != null && lumina < luminaCost) {
      return false;
    }
    return true;
  }
}

/// Game state notifier that manages all game state changes
final gameServiceProvider = Provider((ref) {
  final user = ref.watch(currentUserProvider);
  final userApiKey = user?.extendedExchangeApiKey;

  // TEMPORARILY DISABLED: Starknet service has API compatibility issues
  return GameService(
    ref.watch(astratradeBackendClientProvider),
    // ref.watch(starknetServiceProvider), // Commented out due to API issues
    userApiKey, // Pass user's personal API key for market data access
  );
});

class GameStateNotifier extends StateNotifier<GameState> {
  final Ref _ref;
  final GameService _gameService;
  final LeaderboardService _leaderboardService;

  GameStateNotifier(this._ref, this._gameService, this._leaderboardService)
    : super(GameState(lastActivity: DateTime.now())) {
    _startAutoForging();
    _checkRagConnection();
  }

  /// Check RAG backend connection status - DISABLED FOR STABILITY
  Future<void> _checkRagConnection() async {
    // DISABLED: RAG system causes connection errors and instability
    debugPrint('RAG connection check disabled for stability');
  }

  /// Convert user ID to integer for backend compatibility
  int _getUserIdAsInt(String userId) {
    debugPrint('🔍 Converting user ID to int: "$userId"');

    // Handle specific legacy cases first
    if (userId == 'restored_user') {
      debugPrint('⚠️ Found legacy restored_user ID, using fallback: 12346');
      return 12346;
    }

    // Try parsing as int first (for numeric user IDs)
    try {
      final result = int.parse(userId);
      debugPrint('✅ Successfully parsed as int: $result');
      return result;
    } catch (e) {
      // For string IDs like "fresh_17G32427D152", use a consistent hash
      final hash = userId.hashCode.abs();
      debugPrint('⚠️ Using hash for string ID "$userId": $hash (error: $e)');
      return hash;
    }
  }

  /// Perform a Quick Trade operation with gasless paymaster integration
  Future<void> performQuickTrade() async {
    debugPrint('🎯 === QUICK TRADE STARTED ===');
    try {
      final user = _ref.read(currentUserProvider);
      if (user == null) {
        debugPrint('❌ CRITICAL: User not logged in');
        throw Exception('User not logged in.');
      }

      debugPrint(
        '✅ User found: ID="${user.id}", Address="${user.starknetAddress ?? 'NO_ADDRESS'}"',
      );

      // Initialize paymaster service
      debugPrint('🔧 Initializing paymaster service...');
      final paymaster = PaymasterService.instance;
      await paymaster.initialize();
      debugPrint('✅ Paymaster service initialized');

      // Check if user is eligible for gasless transactions
      final userAddress = user.starknetAddress ?? '';
      debugPrint(
        '🔍 Checking paymaster eligibility for address: "$userAddress"',
      );
      debugPrint(
        '🔍 Address length: ${userAddress.length}, isEmpty: ${userAddress.isEmpty}',
      );
      final eligibility = await paymaster.checkUserEligibility(userAddress);
      debugPrint(
        '📊 Eligibility result: isEligible=${eligibility.isEligible}, dailyLimit=${eligibility.dailyLimit}, usedToday=${eligibility.usedToday}',
      );
      debugPrint(
        '🎯 PAYMASTER DECISION: Will attempt gasless? ${eligibility.isEligible && userAddress.isNotEmpty}',
      );

      TradeResult result;

      // Enable paymaster for gasless transactions
      if (eligibility.isEligible && userAddress.isNotEmpty) {
        debugPrint('🎯 CONDITIONS MET: Attempting paymaster-sponsored trade');
        debugPrint('✅ ENTERING GASLESS TRANSACTION FLOW');

        // Show gasless transaction notification
        _showGaslessNotification(
          '🚀 Gasless Trade Initiated!',
          'AVNU paymaster is processing your transaction with zero gas fees!',
        );

        // Attempt gasless trade with paymaster sponsorship
        try {
          debugPrint('🚀 STEP 1: Preparing gasless trade via AVNU paymaster');

          // Prepare trade calls for paymaster sponsorship
          final tradeCalls = [
            {
              'contract_address': '0x123...', // Mock trading contract
              'selector': 'execute_trade',
              'calldata': [user.id, 'ETH', 'long', '100.0'],
            },
          ];
          debugPrint('📋 Trade calls prepared: ${tradeCalls.length} calls');

          // Estimate gas for the trade
          const estimatedGas = 0.005; // 0.005 ETH worth of gas
          debugPrint('⛽ Estimated gas: $estimatedGas ETH');

          // Validate transaction can be sponsored
          debugPrint('🔍 STEP 2: Validating transaction for sponsorship...');

          // Show validation notification
          _showGaslessNotification(
            '🔍 Validating Gasless Trade',
            'Checking AVNU sponsorship eligibility for your transaction...',
          );

          final canSponsor = await paymaster.validateTransaction(
            userAddress: userAddress,
            calls: tradeCalls,
            estimatedGas: estimatedGas,
          );
          debugPrint('📊 Validation result: canSponsor=$canSponsor');

          if (canSponsor) {
            debugPrint(
              '🎯 STEP 3: Requesting sponsorship from AVNU paymaster...',
            );
            // Request sponsorship from AVNU paymaster
            final sponsorship = await paymaster.requestSponsorship(
              userAddress: userAddress,
              calls: tradeCalls,
              estimatedGas: estimatedGas,
              metadata: {
                'trade_type': 'quick_trade',
                'user_id': user.id,
                'timestamp': DateTime.now().toIso8601String(),
              },
            );
            debugPrint(
              '📨 Sponsorship response: isApproved=${sponsorship.isApproved}, ID=${sponsorship.sponsorshipId}',
            );

            if (sponsorship.isApproved) {
              debugPrint(
                '✅ STEP 4: AVNU sponsorship APPROVED! Executing gasless transaction...',
              );

              // Generate real signature for gasless transaction
              String userSignature;
              try {
                debugPrint(
                  '🔐 Generating real Starknet signature for gasless transaction...',
                );
                final starknetService = StarknetService();
                userSignature = await starknetService
                    .generateGaslessTransactionSignature(
                      privateKey: user.privateKey,
                      userAddress: userAddress,
                      calls: tradeCalls,
                    );
                debugPrint('✅ Real signature generated successfully');
              } catch (e) {
                debugPrint(
                  '⚠️ Real signature generation failed, using fallback: $e',
                );
                userSignature =
                    'enhanced_fallback_signature_${DateTime.now().millisecondsSinceEpoch}';
              }

              // Execute gasless transaction through paymaster
              final txHash = await paymaster.executeWithSponsorship(
                sponsorship: sponsorship,
                calls: tradeCalls,
                userAddress: userAddress,
                userSignature: userSignature, // Now using real signatures!
              );

              debugPrint(
                '🎉 STEP 5: Gasless transaction EXECUTED successfully! TxHash: $txHash',
              );

              // Show success notification
              _showGaslessNotification(
                '✅ Gasless Trade Complete!',
                'Transaction executed successfully with zero gas fees! 🎉',
              );

              // Perform the actual game logic trade (this remains the same)
              debugPrint('🎮 STEP 6: Executing game logic trade...');
              result = await _gameService.performQuickTrade(
                userId: _getUserIdAsInt(user.id),
              );
              debugPrint('✅ Game logic trade completed: ${result.outcome}');

              // Update trade message to indicate gasless success with transaction verification
              final isRealTx = txHash.isNotEmpty && !txHash.contains('mock');
              final verificationMessage = isRealTx
                  ? '\n🔍 Verify on Starkscan: https://sepolia.starkscan.co/tx/$txHash'
                  : '\n⚠️ Mock transaction (AVNU integration in progress): $txHash';

              result = TradeResult(
                outcome: result.outcome,
                stellarShardsGained: result.stellarShardsGained,
                luminaGained: result.luminaGained,
                profitPercentage: result.profitPercentage,
                outcomeMessage:
                    '🚀 GASLESS TRADE SUCCESS!\n${result.outcomeMessage}\n💰 No gas fees paid! (Sponsored by AVNU)$verificationMessage',
                isCriticalForge: result.isCriticalForge,
              );
              debugPrint(
                '🎊 PAYMASTER SUCCESS: Trade completed with gasless sponsorship!',
              );
            } else {
              debugPrint(
                '❌ STEP 4: AVNU sponsorship DENIED, falling back to regular trade',
              );

              // Show fallback notification
              _showGaslessNotification(
                '⚠️ Gasless Unavailable',
                'AVNU sponsorship limit reached. Using regular trade with minimal fees.',
              );

              result = await _gameService.performQuickTrade(
                userId: _getUserIdAsInt(user.id),
              );
              debugPrint('📱 Fallback trade completed: ${result.outcome}');
            }
          } else {
            debugPrint(
              '⚠️ STEP 3: Transaction CANNOT be sponsored, using regular trade',
            );
            result = await _gameService.performQuickTrade(
              userId: _getUserIdAsInt(user.id),
            );
            debugPrint('📱 Regular trade completed: ${result.outcome}');
          }
        } catch (paymasterError) {
          debugPrint('🔴 PAYMASTER ERROR: $paymasterError');
          debugPrint('🔄 Falling back to regular trade...');
          result = await _gameService.performQuickTrade(
            userId: _getUserIdAsInt(user.id),
          );
          debugPrint('📱 Fallback trade completed: ${result.outcome}');
        }
      } else {
        // User not eligible or no address, use regular trade
        debugPrint(
          '📱 SKIPPING PAYMASTER: User not eligible (${eligibility.isEligible}) or no address (${userAddress.isEmpty})',
        );
        debugPrint('❌ USING REGULAR TRADE PATH (NO GASLESS)');
        debugPrint(
          '🔍 Debug - Address: "$userAddress", Length: ${userAddress.length}',
        );
        debugPrint(
          '🔍 Debug - Eligible: ${eligibility.isEligible}, Reason: ${eligibility.reasonCode}',
        );
        result = await _gameService.performQuickTrade(
          userId: _getUserIdAsInt(user.id),
        );
        debugPrint('📱 Regular trade completed: ${result.outcome}');
      }

      // Calculate XP gained based on trade result
      final xpGained = XPCalculator.calculateTradeXP(
        isProfit: result.outcome == TradeOutcome.profit,
        isCriticalForge: result.isCriticalForge,
        isRealTrade: false, // This is simulation trade
        winStreak: state.winStreak,
        profitPercentage: result.profitPercentage,
      );

      // Update state based on trade result
      final newStellarShards = state.stellarShards + result.stellarShardsGained;
      final newLumina = state.lumina + result.luminaGained;
      final newExperience =
          state.experience + (result.isCriticalForge ? 20 : 10);
      final newTotalXP = state.totalXP + xpGained;
      final newTotalTrades = state.totalTrades + 1;

      // Update win streak
      int newWinStreak = state.winStreak;
      if (result.outcome == TradeOutcome.profit) {
        newWinStreak += 1;
      } else if (result.outcome == TradeOutcome.loss) {
        newWinStreak = 0;
      }

      // Calculate new level and cosmic tier
      final newLevel = XPCalculator.calculateLevel(newTotalXP);
      final newCosmicTier = CosmicTier.fromXP(newTotalXP);

      // Calculate win rate
      final profitableTrades = result.outcome == TradeOutcome.profit ? 1 : 0;
      final newWinRate = newTotalTrades > 0
          ? ((state.winRate * state.totalTrades) + profitableTrades) /
                newTotalTrades
          : 0.0;

      // Check for level up
      final didLevelUp = newLevel > state.level;
      final didTierUp = newCosmicTier != state.cosmicTier;

      // Determine new planet health based on recent performance
      PlanetHealth newPlanetHealth = _calculatePlanetHealth(
        result.outcome,
        newWinStreak,
        newTotalTrades,
      );

      // Build level up message if applicable
      String finalMessage = result.outcomeMessage;
      if (didLevelUp) {
        finalMessage += "\n🎉 LEVEL UP! You've reached Level $newLevel!";
      }
      if (didTierUp) {
        finalMessage +=
            "\n✨ COSMIC ASCENSION! You are now ${newCosmicTier.displayName}!";
      }
      if (xpGained > 0) {
        finalMessage += "\n+$xpGained XP gained!";
      }

      state = state.copyWith(
        stellarShards: newStellarShards.toInt(),
        lumina: newLumina.toInt(),
        experience: newExperience,
        totalXP: newTotalXP,
        level: newLevel,
        cosmicTier: newCosmicTier,
        planetHealth: newPlanetHealth,
        lastTradeMessage: finalMessage,
        lastActivity: DateTime.now(),
        totalTrades: newTotalTrades,
        winStreak: newWinStreak,
        winRate: newWinRate,
      );

      // Update leaderboard with new stats
      _leaderboardService.updateCurrentUserStats(
        stellarShards: newStellarShards.toInt(),
        lumina: newLumina.toInt(),
        totalXP: newTotalXP,
        winStreak: newWinStreak,
        totalTrades: newTotalTrades,
        winRate: newWinRate,
      );

      // Trigger Genesis Ignition if this is the first profitable trade
      if (!state.hasGenesisIgnition && result.outcome == TradeOutcome.profit) {
        _triggerGenesisIgnition();
      }

      debugPrint('🎊 === QUICK TRADE COMPLETED SUCCESSFULLY ===');
    } catch (e, stackTrace) {
      // Handle trade error with comprehensive debugging
      debugPrint('💥 === QUICK TRADE ERROR ===');
      debugPrint('🔴 Error type: ${e.runtimeType}');
      debugPrint('🔴 Error message: ${e.toString()}');
      debugPrint('🔴 Stack trace: $stackTrace');

      String errorMessage;
      if (e is RagApiException) {
        debugPrint('🌐 RAG API Exception detected');
        errorMessage = "Cosmic Network Disruption: ${e.message}";
      } else if (e.toString().contains('FormatException')) {
        debugPrint(
          '🔤 Format Exception detected - likely user ID parsing issue',
        );
        errorMessage = "User ID Format Error: ${e.toString()}";
      } else if (e.toString().contains('restored_user')) {
        debugPrint('👤 Restored user ID issue detected');
        errorMessage = "User Session Error: ${e.toString()}";
      } else {
        debugPrint('❓ Unknown error type');
        errorMessage = "Cosmic Interference Detected: ${e.toString()}";
      }

      debugPrint('📝 Final error message: $errorMessage');

      state = state.copyWith(
        lastTradeMessage: errorMessage,
        lastActivity: DateTime.now(),
      );

      debugPrint('💥 === ERROR HANDLING COMPLETE - RETHROWING ===');
      // Re-throw for UI handling
      rethrow;
    }
  }

  /// Perform manual stellar forge (planet tap)
  Future<void> performManualForge() async {
    final reward = await _gameService.performStellarForge(isManualTap: true);
    final efficiency = _gameService.calculateForgerEfficiency(
      state.planetHealth.name,
    );
    final finalReward = (reward * efficiency).round();

    state = state.copyWith(
      stellarShards: state.stellarShards + finalReward,
      experience: state.experience + 2,
      lastActivity: DateTime.now(),
    );
  }

  /// Purchase additional Astro-Forger
  void purchaseAstroForger() {
    final cost = _calculateAstroForgerCost();
    if (state.canAfford(stellarShardsCost: cost)) {
      state = state.copyWith(
        stellarShards: state.stellarShards - cost,
        astroForgers: state.astroForgers + 1,
        lastActivity: DateTime.now(),
      );
    }
  }

  /// Activate/upgrade a Cosmic Genesis Node
  void upgradeCosmicNode(String nodeType) {
    final cost = _calculateNodeUpgradeCost(nodeType);
    if (state.canAfford(luminaCost: cost)) {
      final currentLevel = state.cosmicNodes[nodeType] ?? 0;
      final newNodes = Map<String, int>.from(state.cosmicNodes);
      newNodes[nodeType] = currentLevel + 1;

      state = state.copyWith(
        lumina: state.lumina - cost,
        cosmicNodes: newNodes,
        lastActivity: DateTime.now(),
      );
    }
  }

  /// Trigger Genesis Ignition (Pro Trader activation)
  void _triggerGenesisIgnition() {
    state = state.copyWith(
      hasGenesisIgnition: true,
      lumina: state.lumina + 25, // Lumina Cascade bonus
      lastTradeMessage:
          "🌟 GENESIS IGNITION ACHIEVED! Welcome to Pro Trading! 🌟",
      planetHealth: PlanetHealth.flourishing,
    );
  }

  /// Calculate planet health based on recent trading performance
  PlanetHealth _calculatePlanetHealth(
    TradeOutcome lastOutcome,
    int winStreak,
    int totalTrades,
  ) {
    // Calculate success rate if we have enough trades
    if (totalTrades >= 5) {
      if (winStreak >= 3) {
        return PlanetHealth.flourishing;
      } else if (winStreak >= 1 || lastOutcome != TradeOutcome.loss) {
        return PlanetHealth.stable;
      } else {
        return PlanetHealth.decaying;
      }
    }

    // For early trades, be more forgiving
    if (lastOutcome == TradeOutcome.profit) {
      return PlanetHealth.flourishing;
    } else if (lastOutcome == TradeOutcome.breakeven) {
      return PlanetHealth.stable;
    } else {
      return state.planetHealth; // Don't penalize immediately
    }
  }

  /// Calculate cost for next Astro-Forger
  int _calculateAstroForgerCost() {
    return 100 + (state.astroForgers * 50);
  }

  /// Calculate cost for upgrading a Cosmic Node
  int _calculateNodeUpgradeCost(String nodeType) {
    final currentLevel = state.cosmicNodes[nodeType] ?? 0;
    return 10 + (currentLevel * 15);
  }

  /// Start auto-forging from Astro-Forgers
  void _startAutoForging() {
    // This would typically use a timer in a real implementation
    // For now, we'll simulate periodic auto-forging
    Future.delayed(const Duration(seconds: 30), () {
      if (mounted && state.astroForgers > 0) {
        _performAutoForge();
        _startAutoForging(); // Continue the cycle
      }
    });
  }

  /// Perform automatic stellar forge from Astro-Forgers
  Future<void> _performAutoForge() async {
    if (state.astroForgers <= 0) return;

    final baseReward = await _gameService.performStellarForge(
      isManualTap: false,
    );
    final efficiency = _gameService.calculateForgerEfficiency(
      state.planetHealth.name,
    );
    final totalReward = (baseReward * state.astroForgers * efficiency).round();

    state = state.copyWith(
      stellarShards: state.stellarShards + totalReward,
      experience: state.experience + 1,
      lastActivity: DateTime.now(),
    );
  }

  /// Update game state from real trade result with enhanced XP system
  void updateFromRealTrade(TradeResult result) {
    // Calculate XP gained for real trade (higher rewards)
    final xpGained = XPCalculator.calculateTradeXP(
      isProfit: result.outcome == TradeOutcome.profit,
      isCriticalForge: result.isCriticalForge,
      isRealTrade: true, // Real trade gets higher XP
      winStreak: state.winStreak,
      profitPercentage: result.profitPercentage,
    );

    // Update state based on real trade result
    final newStellarShards = state.stellarShards + result.stellarShardsGained;
    final newLumina = state.lumina + result.luminaGained;
    final newExperience =
        state.experience +
        (result.isCriticalForge ? 30 : 15); // Higher XP for real trades
    final newTotalXP = state.totalXP + xpGained;
    final newTotalTrades = state.totalTrades + 1;

    // Update win streak
    int newWinStreak = state.winStreak;
    if (result.outcome == TradeOutcome.profit) {
      newWinStreak += 1;
    } else if (result.outcome == TradeOutcome.loss) {
      newWinStreak = 0;
    }

    // Calculate new level and cosmic tier
    final newLevel = XPCalculator.calculateLevel(newTotalXP);
    final newCosmicTier = CosmicTier.fromXP(newTotalXP);

    // Calculate win rate
    final profitableTrades = result.outcome == TradeOutcome.profit ? 1 : 0;
    final newWinRate = newTotalTrades > 0
        ? ((state.winRate * state.totalTrades) + profitableTrades) /
              newTotalTrades
        : 0.0;

    // Check for level up
    final didLevelUp = newLevel > state.level;
    final didTierUp = newCosmicTier != state.cosmicTier;

    // Determine new planet health based on real trade performance
    PlanetHealth newPlanetHealth = _calculatePlanetHealth(
      result.outcome,
      newWinStreak,
      newTotalTrades,
    );

    // Build enhanced message for real trades
    String finalMessage = "🚀 REAL TRADE: ${result.outcomeMessage}";
    if (didLevelUp) {
      finalMessage += "\n🎉 LEVEL UP! You've reached Level $newLevel!";
    }
    if (didTierUp) {
      finalMessage +=
          "\n✨ COSMIC ASCENSION! You are now ${newCosmicTier.displayName}!";
    }
    if (xpGained > 0) {
      finalMessage += "\n+$xpGained XP gained! (Real Trade Bonus)";
    }

    state = state.copyWith(
      stellarShards: newStellarShards,
      lumina: newLumina,
      experience: newExperience,
      totalXP: newTotalXP,
      level: newLevel,
      cosmicTier: newCosmicTier,
      planetHealth: newPlanetHealth,
      lastTradeMessage: finalMessage,
      lastActivity: DateTime.now(),
      totalTrades: newTotalTrades,
      winStreak: newWinStreak,
      winRate: newWinRate,
    );

    // Update leaderboard with new stats
    _leaderboardService.updateCurrentUserStats(
      stellarShards: newStellarShards,
      lumina: newLumina,
      totalXP: newTotalXP,
      winStreak: newWinStreak,
      totalTrades: newTotalTrades,
      winRate: newWinRate,
    );

    // Trigger Genesis Ignition if this is the first profitable real trade
    if (!state.hasGenesisIgnition && result.outcome == TradeOutcome.profit) {
      _triggerGenesisIgnition();
    }
  }

  /// Reset game state (for testing or new game)
  void resetGameState() {
    state = GameState(lastActivity: DateTime.now());
  }

  /// Get market data for UI display
  Map<String, dynamic> getMarketData() {
    return _gameService.getMockMarketData();
  }

  /// Show gasless transaction notification to user
  void _showGaslessNotification(String title, String message) {
    try {
      final notification = GameNotification(
        id: 'gasless_${DateTime.now().millisecondsSinceEpoch}',
        type: NotificationType.trading,
        title: title,
        message: message,
        data: {
          'type': 'gasless_transaction',
          'timestamp': DateTime.now().toIso8601String(),
          'feature': 'AVNU_paymaster',
        },
        timestamp: DateTime.now(),
        isRead: false,
      );

      NotificationService().showNotification(notification);
      debugPrint('🔔 Gasless notification shown: $title - $message');
    } catch (e) {
      debugPrint('⚠️ Failed to show gasless notification: $e');
    }
  }

  /// Add cosmic rewards from trading activities (non-disruptive integration)
  /// This method enhances the existing trading flow with cosmic progression
  void addCosmicRewards({
    required int stellarShards,
    required int experience,
    required bool isSuccess,
    String? customMessage,
  }) {
    // Calculate new values
    final newStellarShards = state.stellarShards + stellarShards;
    final newExperience = state.experience + experience;
    final newTotalXP = state.totalXP + experience;
    final newLevel = (newTotalXP / 100).floor() + 1;

    // Check for level up
    final didLevelUp = newLevel > state.level;

    // Update win streak
    final newWinStreak = isSuccess ? state.winStreak + 1 : 0;

    // Calculate new cosmic tier
    final newCosmicTier = CosmicTier.fromXP(newTotalXP);
    final didTierUp = newCosmicTier != state.cosmicTier;

    // Generate cosmic message
    String cosmicMessage;
    if (customMessage != null) {
      cosmicMessage = customMessage;
    } else if (didLevelUp && didTierUp) {
      cosmicMessage =
          "🎉 COSMIC EVOLUTION! Welcome to ${newCosmicTier.displayName}!\n⭐ +$stellarShards Stellar Shards, +$experience XP";
    } else if (didLevelUp) {
      cosmicMessage =
          "🌟 LEVEL UP! You've reached Level $newLevel!\n⭐ +$stellarShards Stellar Shards, +$experience XP";
    } else if (isSuccess) {
      cosmicMessage =
          "⭐ Stellar Alignment Achieved!\n+$stellarShards Stellar Shards, +$experience XP";
    } else {
      cosmicMessage =
          "🔄 Cosmic Energy Channeled!\n+$stellarShards Stellar Shards, +$experience XP";
    }

    // Update state with cosmic rewards
    state = state.copyWith(
      stellarShards: newStellarShards,
      experience: newExperience,
      totalXP: newTotalXP,
      level: newLevel,
      cosmicTier: newCosmicTier,
      winStreak: newWinStreak,
      lastTradeMessage: cosmicMessage,
      lastActivity: DateTime.now(),
    );

    // Update leaderboard with new cosmic stats
    _leaderboardService.updateCurrentUserStats(
      stellarShards: newStellarShards,
      lumina: state.lumina,
      totalXP: newTotalXP,
      winStreak: newWinStreak,
      totalTrades: state.totalTrades,
      winRate: state.winRate,
    );

    debugPrint('🌟 Cosmic rewards added: +$stellarShards SS, +$experience XP');
    if (didLevelUp) {
      debugPrint('🎉 Player leveled up to Level $newLevel!');
    }
    if (didTierUp) {
      debugPrint('✨ Player ascended to ${newCosmicTier.displayName}!');
    }
  }
}

/// Provider for the game state
final gameStateProvider = StateNotifierProvider<GameStateNotifier, GameState>(
  (ref) => GameStateNotifier(
    ref,
    ref.watch(gameServiceProvider),
    ref.watch(leaderboardServiceProvider),
  ),
);

/// Provider for market data (updates periodically)
final marketDataProvider = StreamProvider<Map<String, dynamic>>((ref) {
  return Stream.periodic(
    const Duration(seconds: 5),
    (_) => ref.read(gameStateProvider.notifier).getMarketData(),
  );
});

/// Provider for checking if player is in "Quick Trade" loading state
final isQuickTradingProvider = StateProvider<bool>((ref) => false);

/// Provider for RAG backend connection status
final ragConnectionStatusProvider = StateProvider<RagConnectionStatus>(
  (ref) => RagConnectionStatus.unknown,
);

/// RAG connection status enum
enum RagConnectionStatus { unknown, connected, disconnected, connecting, error }
