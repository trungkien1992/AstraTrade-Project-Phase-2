import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/artifact.dart';
import '../models/ascension_system.dart';
import '../models/lottery.dart';
import '../models/shield_dust.dart';
import '../models/quantum_anomaly.dart';
import '../models/leaderboard.dart';
import '../services/artifact_service.dart';
import '../services/lottery_service.dart';
import '../services/quantum_anomaly_service.dart';
import '../widgets/planet_view.dart';

/// Enhanced game state that includes all new features
class EnhancedGameState {
  // Core game state (existing)
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
  
  // New features
  final ArtifactCollection artifactCollection;
  final PlayerAscension ascensionData;
  final PlayerShieldDust shieldDustData;
  final PlayerLotteryStats lotteryStats;
  final PlayerQuantumStats quantumStats;
  final bool hasAscended;
  final Map<String, double> activeArtifactBonuses;
  final QuantumAnomalyEvent? activeAnomaly;
  final LotteryDraw? currentLottery;
  final Map<String, double> anomalyEffects;

  const EnhancedGameState({
    this.stellarShards = 50,
    this.lumina = 0,
    this.experience = 0,
    this.totalXP = 0,
    this.level = 1,
    this.planetHealth = PlanetHealth.stable,
    this.astroForgers = 1,
    this.hasGenesisIgnition = false,
    this.lastTradeMessage = "Welcome to the Enhanced Cosmic Trading Journey!",
    required this.lastActivity,
    this.cosmicNodes = const {},
    this.totalTrades = 0,
    this.winStreak = 0,
    this.winRate = 0.0,
    this.cosmicTier = CosmicTier.stellarSeedling,
    required this.artifactCollection,
    required this.ascensionData,
    required this.shieldDustData,
    required this.lotteryStats,
    required this.quantumStats,
    this.hasAscended = false,
    this.activeArtifactBonuses = const {},
    this.activeAnomaly,
    this.currentLottery,
    this.anomalyEffects = const {},
  });

  factory EnhancedGameState.initial(String playerId) {
    final now = DateTime.now();
    return EnhancedGameState(
      lastActivity: now,
      artifactCollection: ArtifactCollection.empty(playerId),
      ascensionData: PlayerAscension.newPlayer(playerId),
      shieldDustData: PlayerShieldDust.newPlayer(playerId),
      lotteryStats: PlayerLotteryStats.newPlayer(playerId),
      quantumStats: PlayerQuantumStats.newPlayer(playerId),
    );
  }

  EnhancedGameState copyWith({
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
    ArtifactCollection? artifactCollection,
    PlayerAscension? ascensionData,
    PlayerShieldDust? shieldDustData,
    PlayerLotteryStats? lotteryStats,
    PlayerQuantumStats? quantumStats,
    bool? hasAscended,
    Map<String, double>? activeArtifactBonuses,
    QuantumAnomalyEvent? activeAnomaly,
    LotteryDraw? currentLottery,
    Map<String, double>? anomalyEffects,
  }) {
    return EnhancedGameState(
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
      artifactCollection: artifactCollection ?? this.artifactCollection,
      ascensionData: ascensionData ?? this.ascensionData,
      shieldDustData: shieldDustData ?? this.shieldDustData,
      lotteryStats: lotteryStats ?? this.lotteryStats,
      quantumStats: quantumStats ?? this.quantumStats,
      hasAscended: hasAscended ?? this.hasAscended,
      activeArtifactBonuses: activeArtifactBonuses ?? this.activeArtifactBonuses,
      activeAnomaly: activeAnomaly ?? this.activeAnomaly,
      currentLottery: currentLottery ?? this.currentLottery,
      anomalyEffects: anomalyEffects ?? this.anomalyEffects,
    );
  }

  /// Calculate enhanced cosmic power including all new features
  int get enhancedCosmicPower {
    int basePower = stellarShards ~/ 10;
    int luminaPower = lumina * 50;
    int experiencePower = experience ~/ 5;
    int forgerPower = astroForgers * 25;
    int nodePower = cosmicNodes.values.fold(0, (sum, level) => sum + (level * 100));
    
    // Add artifact power
    int artifactPower = artifactCollection.artifacts.fold(0, 
        (sum, artifact) => sum + artifact.powerLevel.round() * 10);
    
    // Add ascension power
    int ascensionPower = ascensionData.totalStardust * 5;
    ascensionPower += ascensionData.ascensionLevel * 1000;
    
    // Add shield dust power
    int shieldPower = shieldDustData.totalDustGenerated ~/ 5;
    
    // Apply multipliers
    double totalPower = (basePower + luminaPower + experiencePower + 
                        forgerPower + nodePower + artifactPower + 
                        ascensionPower + shieldPower).toDouble();
    
    // Apply ascension multipliers
    totalPower *= ascensionData.globalAscensionMultiplier;
    
    // Apply artifact bonuses
    final efficiencyBonus = activeArtifactBonuses['astro_forger_multiplier'] ?? 0.0;
    totalPower *= (1.0 + efficiencyBonus);
    
    // Apply anomaly effects
    final anomalyMultiplier = anomalyEffects['all_systems_multiplier'] ?? 1.0;
    totalPower *= anomalyMultiplier;
    
    return totalPower.round();
  }

  /// Get enhanced tier display with ascension information
  String get enhancedTierDisplay {
    if (hasAscended && ascensionData.ascensionLevel > 0) {
      return '${ascensionData.currentTier.icon} ${ascensionData.currentTier.displayName} [A${ascensionData.ascensionLevel}]';
    }
    return '${cosmicTier.icon} ${cosmicTier.displayName}';
  }

  /// Calculate effective Stellar Shards generation with all bonuses
  double get effectiveStellarShardsPerHour {
    double baseRate = 10.0 + (level * 2.0);
    
    // Apply cosmic node multipliers
    baseRate *= (1.0 + (cosmicNodes['graviton'] ?? 0) * 0.15);
    baseRate *= (1.0 + (cosmicNodes['chrono'] ?? 0) * 0.1);
    
    // Apply artifact bonuses
    final artifactMultiplier = activeArtifactBonuses['astro_forger_multiplier'] ?? 0.0;
    baseRate *= (1.0 + artifactMultiplier);
    
    // Apply ascension bonuses
    final ascensionMultipliers = ascensionData.globalAscensionMultiplier;
    baseRate *= ascensionMultipliers;
    
    // Apply anomaly effects
    final anomalyMultiplier = anomalyEffects['stellar_shards_multiplier'] ?? 1.0;
    baseRate *= anomalyMultiplier;
    
    return baseRate;
  }

  /// Check if player can afford with shield dust protection
  bool canAffordWithProtection({int? stellarShardsCost, int? luminaCost}) {
    if (stellarShardsCost != null) {
      final availableProtection = shieldDustData.currentDustAmount;
      final effectiveCost = stellarShardsCost - availableProtection;
      if (stellarShards < effectiveCost) {
        return false;
      }
    }
    
    if (luminaCost != null && lumina < luminaCost) {
      return false;
    }
    
    return true;
  }

  /// Get protection status summary
  Map<String, dynamic> get protectionStatus {
    return {
      'shield_dust_available': shieldDustData.currentDustAmount,
      'max_protection': shieldDustData.maxProtectionAvailable,
      'protection_efficiency': shieldDustData.overallProtectionEfficiency,
      'recent_protections': shieldDustData.recentProtections.length,
    };
  }

  /// Get lottery participation summary
  Map<String, dynamic> get lotteryStatus {
    return {
      'tickets_purchased': lotteryStats.totalTicketsPurchased,
      'total_winnings': lotteryStats.totalWinnings,
      'win_rate': lotteryStats.winRate,
      'luck_rating': lotteryStats.luckRating,
      'current_draw_active': currentLottery?.isAcceptingTickets ?? false,
    };
  }

  /// Get anomaly participation summary
  Map<String, dynamic> get anomalyStatus {
    return {
      'anomalies_participated': quantumStats.totalAnomaliesParticipated,
      'challenges_completed': quantumStats.totalChallengesCompleted,
      'total_rewards': quantumStats.totalAnomalyRewards,
      'is_veteran': quantumStats.isAnomalyVeteran,
      'current_anomaly_active': activeAnomaly?.isActive ?? false,
    };
  }

  /// Get all active multipliers from various sources
  Map<String, double> get allActiveMultipliers {
    final multipliers = <String, double>{};
    
    // Base multipliers
    multipliers['base'] = 1.0;
    
    // Artifact multipliers
    multipliers.addAll(activeArtifactBonuses);
    
    // Ascension multipliers
    multipliers['ascension_global'] = ascensionData.globalAscensionMultiplier;
    
    // Anomaly multipliers
    multipliers.addAll(anomalyEffects);
    
    return multipliers;
  }
}

/// Enhanced game state notifier that manages all features
class EnhancedGameStateNotifier extends StateNotifier<EnhancedGameState> {
  final ArtifactService _artifactService;
  final LotteryService _lotteryService;
  final QuantumAnomalyService _anomalyService;
  final String playerId;

  EnhancedGameStateNotifier({
    required this.playerId,
    required ArtifactService artifactService,
    required LotteryService lotteryService,
    required QuantumAnomalyService anomalyService,
  }) : _artifactService = artifactService,
       _lotteryService = lotteryService,
       _anomalyService = anomalyService,
       super(EnhancedGameState.initial(playerId)) {
    _initialize();
  }

  Future<void> _initialize() async {
    // Load all player data
    final artifactCollection = await _artifactService.getPlayerCollection(playerId);
    final lotteryStats = await _lotteryService.getPlayerStats(playerId);
    final quantumStats = await _anomalyService.getPlayerStats(playerId);
    final activeAnomaly = await _anomalyService.getCurrentAnomaly();
    final currentLottery = await _lotteryService.getCurrentDraw();
    
    // Calculate artifact bonuses
    final artifactBonuses = await _artifactService.calculatePassiveBonuses(playerId);
    
    // Get anomaly effects
    final anomalyEffects = await _anomalyService.processAnomalyEffects();
    
    state = state.copyWith(
      artifactCollection: artifactCollection,
      lotteryStats: lotteryStats,
      quantumStats: quantumStats,
      activeAnomaly: activeAnomaly,
      currentLottery: currentLottery,
      activeArtifactBonuses: artifactBonuses,
      anomalyEffects: anomalyEffects,
    );
  }

  /// Perform enhanced trade with all new features
  Future<Map<String, dynamic>> performEnhancedTrade({
    required String asset,
    required String direction,
    required double amount,
    required bool isRealTrade,
  }) async {
    try {
      // Calculate bonuses from artifacts
      final bonuses = state.activeArtifactBonuses;
      final criticalChanceBonus = bonuses['critical_chance_bonus'] ?? 0.0;
      final xpMultiplier = bonuses['xp_multiplier'] ?? 0.0;
      
      // Apply anomaly effects
      final anomalyMultipliers = state.anomalyEffects;
      final stellarShardsMultiplier = anomalyMultipliers['stellar_shards_multiplier'] ?? 1.0;
      
      // Simulate trade result (integrate with existing game service)
      final baseReward = 10 + (state.level * 2);
      final enhancedReward = (baseReward * stellarShardsMultiplier * (1.0 + xpMultiplier)).round();
      
      // Check for artifact drops
      final shouldDrop = await _artifactService.shouldDropArtifact(
        playerId: playerId,
        activityType: 'trade',
        baseDropChance: 0.05,
        bonusMultipliers: {
          'real_trade': isRealTrade ? 2.0 : 1.0,
          'anomaly_boost': anomalyMultipliers['artifact_drop_chance'] ?? 1.0,
        },
      );

      TradingArtifact? newArtifact;
      if (shouldDrop) {
        newArtifact = await _artifactService.mintArtifact(
          playerId: playerId,
          eventSource: 'trade_drop',
        );
      }

      // Generate shield dust for real trades
      int shieldDustGenerated = 0;
      if (isRealTrade) {
        shieldDustGenerated = 10; // Base amount per real trade
        final updatedShieldDust = state.shieldDustData.addDust(
          ShieldDustSource.realTrade,
          shieldDustGenerated,
        );
        
        state = state.copyWith(shieldDustData: updatedShieldDust);
      }

      // Update game state
      state = state.copyWith(
        stellarShards: state.stellarShards + enhancedReward,
        totalTrades: state.totalTrades + 1,
        lastActivity: DateTime.now(),
        lastTradeMessage: _generateTradeMessage(enhancedReward, newArtifact != null),
      );

      // Refresh artifact bonuses if new artifact was minted
      if (newArtifact != null) {
        final updatedCollection = await _artifactService.getPlayerCollection(playerId);
        final updatedBonuses = await _artifactService.calculatePassiveBonuses(playerId);
        
        state = state.copyWith(
          artifactCollection: updatedCollection,
          activeArtifactBonuses: updatedBonuses,
        );
      }

      return {
        'success': true,
        'stellar_shards_gained': enhancedReward,
        'shield_dust_gained': shieldDustGenerated,
        'artifact_dropped': newArtifact,
        'bonuses_applied': bonuses,
        'anomaly_effects': anomalyMultipliers,
      };
    } catch (e) {
      debugPrint('Enhanced trade failed: $e');
      return {'success': false, 'error': e.toString()};
    }
  }

  /// Purchase lottery tickets
  Future<bool> purchaseLotteryTickets(int ticketCount) async {
    final tickets = await _lotteryService.purchaseTickets(
      playerId: playerId,
      playerName: 'Player_$playerId', // Would get actual name from user service
      ticketCount: ticketCount,
      stellarShardsBalance: state.stellarShards,
    );

    if (tickets != null) {
      final totalCost = ticketCount * LotteryConfig.ticketCost;
      final updatedStats = await _lotteryService.getPlayerStats(playerId);
      
      state = state.copyWith(
        stellarShards: state.stellarShards - totalCost,
        lotteryStats: updatedStats,
        lastActivity: DateTime.now(),
      );
      
      return true;
    }
    
    return false;
  }

  /// Equip artifact
  Future<bool> equipArtifact(String artifactId) async {
    final success = await _artifactService.equipArtifact(playerId, artifactId);
    
    if (success) {
      final updatedCollection = await _artifactService.getPlayerCollection(playerId);
      final updatedBonuses = await _artifactService.calculatePassiveBonuses(playerId);
      
      state = state.copyWith(
        artifactCollection: updatedCollection,
        activeArtifactBonuses: updatedBonuses,
      );
    }
    
    return success;
  }

  /// Join quantum anomaly challenge
  Future<bool> joinAnomalyChallenge(String challengeId) async {
    final success = await _anomalyService.joinChallenge(
      playerId: playerId,
      challengeId: challengeId,
    );
    
    if (success) {
      final updatedAnomaly = await _anomalyService.getCurrentAnomaly();
      final updatedStats = await _anomalyService.getPlayerStats(playerId);
      
      state = state.copyWith(
        activeAnomaly: updatedAnomaly,
        quantumStats: updatedStats,
      );
    }
    
    return success;
  }

  /// Refresh all dynamic data
  Future<void> refreshState() async {
    await _initialize();
  }

  String _generateTradeMessage(int reward, bool artifactDropped) {
    if (artifactDropped) {
      return "🌟 Cosmic Trade Complete! +$reward SS and a mysterious artifact emerged!";
    }
    return "✨ Trade executed! +$reward Stellar Shards harvested from the cosmos!";
  }
}

/// Providers for the enhanced game state system
final enhancedGameStateProvider = StateNotifierProvider.family<EnhancedGameStateNotifier, EnhancedGameState, String>(
  (ref, playerId) => EnhancedGameStateNotifier(
    playerId: playerId,
    artifactService: ArtifactService(),
    lotteryService: LotteryService(),
    anomalyService: QuantumAnomalyService(),
  ),
);

/// Provider for artifact-specific operations
final artifactProvider = Provider((ref) => ArtifactService());

/// Provider for lottery-specific operations
final lotteryProvider = Provider((ref) => LotteryService());

/// Provider for quantum anomaly-specific operations
final quantumAnomalyProvider = Provider((ref) => QuantumAnomalyService());

/// Provider for current active anomaly
final currentAnomalyProvider = FutureProvider((ref) async {
  final service = ref.read(quantumAnomalyProvider);
  return await service.getCurrentAnomaly();
});

/// Provider for current lottery draw
final currentLotteryProvider = FutureProvider((ref) async {
  final service = ref.read(lotteryProvider);
  return await service.getCurrentDraw();
});

/// Provider for anomaly forecast
final anomalyForecastProvider = FutureProvider((ref) async {
  final service = ref.read(quantumAnomalyProvider);
  return await service.getAnomalyForecast();
});