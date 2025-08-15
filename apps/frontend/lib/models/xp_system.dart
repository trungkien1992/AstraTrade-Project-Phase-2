import 'package:json_annotation/json_annotation.dart';

part 'xp_system.g.dart';

/// Core XP and progression system for AstraTrade
/// Implements dual currency system: Stellar Shards (SS) and Lumina (LM)

@JsonSerializable()
class PlayerXP {
  final String playerId;
  final double stellarShards; // SS - Generated from mock trades and tapping
  final double lumina; // LM - Harvested from real trades only
  final int level;
  final double xpToNextLevel;
  final int consecutiveDays; // Streak tracking
  final DateTime lastActiveDate;
  final DateTime createdAt;
  final DateTime? lastLuminaHarvest;
  final Map<String, dynamic> cosmicGenesisGrid; // Lumina investment nodes

  const PlayerXP({
    required this.playerId,
    required this.stellarShards,
    required this.lumina,
    required this.level,
    required this.xpToNextLevel,
    required this.consecutiveDays,
    required this.lastActiveDate,
    required this.createdAt,
    this.lastLuminaHarvest,
    required this.cosmicGenesisGrid,
  });

  factory PlayerXP.fromJson(Map<String, dynamic> json) =>
      _$PlayerXPFromJson(json);
  Map<String, dynamic> toJson() => _$PlayerXPToJson(this);

  /// Create initial XP state for new player
  factory PlayerXP.newPlayer(String playerId) {
    return PlayerXP(
      playerId: playerId,
      stellarShards: 0.0,
      lumina: 0.0,
      level: 1,
      xpToNextLevel: 100.0,
      consecutiveDays: 0,
      lastActiveDate: DateTime.now(),
      createdAt: DateTime.now(),
      cosmicGenesisGrid: initializeCosmicGrid(),
    );
  }

  /// Initialize the Cosmic Genesis Grid with empty nodes
  static Map<String, dynamic> initializeCosmicGrid() {
    return {
      'graviton_amplifier': {
        'level': 0,
        'max_level': 10,
        'cost_multiplier': 1.5,
      },
      'chrono_accelerator': {
        'level': 0,
        'max_level': 10,
        'cost_multiplier': 1.3,
      },
      'bio_synthesis_nexus': {
        'level': 0,
        'max_level': 10,
        'cost_multiplier': 1.4,
      },
      'quantum_resonator': {
        'level': 0,
        'max_level': 10,
        'cost_multiplier': 1.6,
      },
      'stellar_flux_harmonizer': {
        'level': 0,
        'max_level': 10,
        'cost_multiplier': 1.7,
      },
    };
  }

  /// Calculate XP required for specific level
  static double xpRequiredForLevel(int level) {
    // Exponential growth with cosmic scaling
    return 100.0 * (level * level * 1.2);
  }

  /// Calculate total XP from Stellar Shards and Lumina
  double get totalXP => stellarShards + (lumina * 10.0); // Lumina worth 10x SS

  /// Check if player can level up
  bool get canLevelUp => totalXP >= xpRequiredForLevel(level + 1);

  /// Get current level based on total XP
  int get calculatedLevel {
    int currentLevel = 1;
    while (totalXP >= xpRequiredForLevel(currentLevel + 1)) {
      currentLevel++;
    }
    return currentLevel;
  }

  /// Get progress to next level (0.0 to 1.0)
  double get levelProgress {
    final currentLevelXP = xpRequiredForLevel(level);
    final nextLevelXP = xpRequiredForLevel(level + 1);
    final progressXP = totalXP - currentLevelXP;
    final requiredXP = nextLevelXP - currentLevelXP;
    return (progressXP / requiredXP).clamp(0.0, 1.0);
  }

  /// Calculate Stellar Shards per hour from idle generation
  double get stellarShardsPerHour {
    double baseRate = 10.0 + (level * 2.0);

    // Apply Cosmic Genesis Grid multipliers
    final gravitonLevel =
        cosmicGenesisGrid['graviton_amplifier']?['level'] ?? 0;
    final chronoLevel = cosmicGenesisGrid['chrono_accelerator']?['level'] ?? 0;
    final bioLevel = cosmicGenesisGrid['bio_synthesis_nexus']?['level'] ?? 0;

    // Each node provides multiplicative bonus
    baseRate *= (1.0 + (gravitonLevel * 0.15)); // 15% per level
    baseRate *= (1.0 + (chronoLevel * 0.1)); // 10% per level
    baseRate *= (1.0 + (bioLevel * 0.12)); // 12% per level

    return baseRate;
  }

  /// Check if player has active streak
  bool get hasActiveStreak {
    final now = DateTime.now();
    final lastActive = DateTime(
      lastActiveDate.year,
      lastActiveDate.month,
      lastActiveDate.day,
    );
    final today = DateTime(now.year, now.month, now.day);
    final yesterday = today.subtract(const Duration(days: 1));

    return lastActive.isAtSameMomentAs(today) ||
        lastActive.isAtSameMomentAs(yesterday);
  }

  /// Get daily reward multiplier based on streak
  double get streakMultiplier {
    if (consecutiveDays == 0) return 1.0;

    // Exponential rewards for consistency
    final baseMultiplier = 1.0 + (consecutiveDays * 0.05); // 5% per day
    final milestoneBonus = (consecutiveDays ~/ 7) * 0.1; // 10% per week

    return (baseMultiplier + milestoneBonus).clamp(1.0, 3.0); // Cap at 3x
  }

  PlayerXP copyWith({
    String? playerId,
    double? stellarShards,
    double? lumina,
    int? level,
    double? xpToNextLevel,
    int? consecutiveDays,
    DateTime? lastActiveDate,
    DateTime? createdAt,
    DateTime? lastLuminaHarvest,
    Map<String, dynamic>? cosmicGenesisGrid,
  }) {
    return PlayerXP(
      playerId: playerId ?? this.playerId,
      stellarShards: stellarShards ?? this.stellarShards,
      lumina: lumina ?? this.lumina,
      level: level ?? this.level,
      xpToNextLevel: xpToNextLevel ?? this.xpToNextLevel,
      consecutiveDays: consecutiveDays ?? this.consecutiveDays,
      lastActiveDate: lastActiveDate ?? this.lastActiveDate,
      createdAt: createdAt ?? this.createdAt,
      lastLuminaHarvest: lastLuminaHarvest ?? this.lastLuminaHarvest,
      cosmicGenesisGrid: cosmicGenesisGrid ?? this.cosmicGenesisGrid,
    );
  }
}

/// Represents a single XP gain event
@JsonSerializable()
class XPGainEvent {
  final String eventId;
  final String playerId;
  final XPGainType type;
  final double stellarShardsGained;
  final double luminaGained;
  final String description;
  final DateTime timestamp;
  final Map<String, dynamic> metadata;

  const XPGainEvent({
    required this.eventId,
    required this.playerId,
    required this.type,
    required this.stellarShardsGained,
    required this.luminaGained,
    required this.description,
    required this.timestamp,
    required this.metadata,
  });

  factory XPGainEvent.fromJson(Map<String, dynamic> json) =>
      _$XPGainEventFromJson(json);
  Map<String, dynamic> toJson() => _$XPGainEventToJson(this);

  /// Get total XP value of this event
  double get totalXPValue => stellarShardsGained + (luminaGained * 10.0);
}

/// Types of XP gain events
enum XPGainType {
  @JsonValue('orbital_forging')
  orbitalForging, // Idle tapping
  @JsonValue('mock_trade')
  mockTrade, // Practice trading
  @JsonValue('quantum_harvest')
  quantumHarvest, // Real trade
  @JsonValue('daily_reward')
  dailyReward, // Streak bonus
  @JsonValue('level_up')
  levelUp, // Level milestone
  @JsonValue('genesis_activation')
  genesisActivation, // Node upgrade
  @JsonValue('special_event')
  specialEvent, // Limited events
}

/// Cosmic Genesis Grid Node - Lumina investment system
@JsonSerializable()
class CosmicGenesisNode {
  final String nodeId;
  final String name;
  final String description;
  final CosmicNodeType type;
  final int currentLevel;
  final int maxLevel;
  final double baseLuminaCost;
  final double costMultiplier;
  final List<CosmicNodeEffect> effects;
  final bool isUnlocked;
  final DateTime? lastUpgraded;

  const CosmicGenesisNode({
    required this.nodeId,
    required this.name,
    required this.description,
    required this.type,
    required this.currentLevel,
    required this.maxLevel,
    required this.baseLuminaCost,
    required this.costMultiplier,
    required this.effects,
    required this.isUnlocked,
    this.lastUpgraded,
  });

  factory CosmicGenesisNode.fromJson(Map<String, dynamic> json) =>
      _$CosmicGenesisNodeFromJson(json);
  Map<String, dynamic> toJson() => _$CosmicGenesisNodeToJson(this);

  /// Calculate Lumina cost for next level
  double get nextLevelCost {
    if (currentLevel >= maxLevel) return double.infinity;
    return baseLuminaCost * (costMultiplier * currentLevel);
  }

  /// Check if node can be upgraded
  bool canUpgrade(double availableLumina) {
    return currentLevel < maxLevel && availableLumina >= nextLevelCost;
  }

  /// Get current effect strength
  double get currentEffectStrength {
    return currentLevel * 0.1; // 10% per level base
  }
}

/// Types of Cosmic Genesis Nodes
enum CosmicNodeType {
  @JsonValue('graviton_amplifier')
  gravitonAmplifier,
  @JsonValue('chrono_accelerator')
  chronoAccelerator,
  @JsonValue('bio_synthesis_nexus')
  bioSynthesisNexus,
  @JsonValue('quantum_resonator')
  quantumResonator,
  @JsonValue('stellar_flux_harmonizer')
  stellarFluxHarmonizer,
}

/// Effects provided by Cosmic Genesis Nodes
@JsonSerializable()
class CosmicNodeEffect {
  final String effectType;
  final double multiplier;
  final String target;
  final String description;

  const CosmicNodeEffect({
    required this.effectType,
    required this.multiplier,
    required this.target,
    required this.description,
  });

  factory CosmicNodeEffect.fromJson(Map<String, dynamic> json) =>
      _$CosmicNodeEffectFromJson(json);
  Map<String, dynamic> toJson() => _$CosmicNodeEffectToJson(this);
}

/// Daily streak and rewards system
@JsonSerializable()
class DailyStreakReward {
  final int streakDay;
  final double stellarShardsReward;
  final double luminaReward;
  final String description;
  final bool isMilestone;
  final Map<String, dynamic> specialRewards;

  const DailyStreakReward({
    required this.streakDay,
    required this.stellarShardsReward,
    required this.luminaReward,
    required this.description,
    required this.isMilestone,
    required this.specialRewards,
  });

  factory DailyStreakReward.fromJson(Map<String, dynamic> json) =>
      _$DailyStreakRewardFromJson(json);
  Map<String, dynamic> toJson() => _$DailyStreakRewardToJson(this);

  /// Calculate reward multiplier based on streak
  static DailyStreakReward calculateReward(int streakDay) {
    final baseShards = 50.0 + (streakDay * 5.0);
    final baseLumina = streakDay >= 7
        ? 1.0
        : 0.0; // Only milestone days give Lumina

    final isMilestone = streakDay % 7 == 0 || streakDay % 30 == 0;

    return DailyStreakReward(
      streakDay: streakDay,
      stellarShardsReward: baseShards * (isMilestone ? 2.0 : 1.0),
      luminaReward: baseLumina * (streakDay ~/ 7),
      description: isMilestone
          ? 'Cosmic Milestone Achieved! 🌟'
          : 'Daily Stellar Convergence ✨',
      isMilestone: isMilestone,
      specialRewards: isMilestone
          ? {
              'title': streakDay >= 30 ? 'Cosmic Devotee' : 'Stellar Devotee',
              'planet_effect': 'enhanced_glow_${streakDay ~/ 7}',
            }
          : {},
    );
  }
}
