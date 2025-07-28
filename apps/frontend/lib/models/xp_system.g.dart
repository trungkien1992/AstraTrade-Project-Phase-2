// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'xp_system.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

PlayerXP _$PlayerXPFromJson(Map<String, dynamic> json) => PlayerXP(
  playerId: json['playerId'] as String,
  stellarShards: (json['stellarShards'] as num).toDouble(),
  lumina: (json['lumina'] as num).toDouble(),
  level: (json['level'] as num).toInt(),
  xpToNextLevel: (json['xpToNextLevel'] as num).toDouble(),
  consecutiveDays: (json['consecutiveDays'] as num).toInt(),
  lastActiveDate: DateTime.parse(json['lastActiveDate'] as String),
  createdAt: DateTime.parse(json['createdAt'] as String),
  lastLuminaHarvest: json['lastLuminaHarvest'] == null
      ? null
      : DateTime.parse(json['lastLuminaHarvest'] as String),
  cosmicGenesisGrid: json['cosmicGenesisGrid'] as Map<String, dynamic>,
);

Map<String, dynamic> _$PlayerXPToJson(PlayerXP instance) => <String, dynamic>{
  'playerId': instance.playerId,
  'stellarShards': instance.stellarShards,
  'lumina': instance.lumina,
  'level': instance.level,
  'xpToNextLevel': instance.xpToNextLevel,
  'consecutiveDays': instance.consecutiveDays,
  'lastActiveDate': instance.lastActiveDate.toIso8601String(),
  'createdAt': instance.createdAt.toIso8601String(),
  'lastLuminaHarvest': instance.lastLuminaHarvest?.toIso8601String(),
  'cosmicGenesisGrid': instance.cosmicGenesisGrid,
};

XPGainEvent _$XPGainEventFromJson(Map<String, dynamic> json) => XPGainEvent(
  eventId: json['eventId'] as String,
  playerId: json['playerId'] as String,
  type: $enumDecode(_$XPGainTypeEnumMap, json['type']),
  stellarShardsGained: (json['stellarShardsGained'] as num).toDouble(),
  luminaGained: (json['luminaGained'] as num).toDouble(),
  description: json['description'] as String,
  timestamp: DateTime.parse(json['timestamp'] as String),
  metadata: json['metadata'] as Map<String, dynamic>,
);

Map<String, dynamic> _$XPGainEventToJson(XPGainEvent instance) =>
    <String, dynamic>{
      'eventId': instance.eventId,
      'playerId': instance.playerId,
      'type': _$XPGainTypeEnumMap[instance.type]!,
      'stellarShardsGained': instance.stellarShardsGained,
      'luminaGained': instance.luminaGained,
      'description': instance.description,
      'timestamp': instance.timestamp.toIso8601String(),
      'metadata': instance.metadata,
    };

const _$XPGainTypeEnumMap = {
  XPGainType.orbitalForging: 'orbital_forging',
  XPGainType.mockTrade: 'mock_trade',
  XPGainType.quantumHarvest: 'quantum_harvest',
  XPGainType.dailyReward: 'daily_reward',
  XPGainType.levelUp: 'level_up',
  XPGainType.genesisActivation: 'genesis_activation',
  XPGainType.specialEvent: 'special_event',
};

CosmicGenesisNode _$CosmicGenesisNodeFromJson(Map<String, dynamic> json) =>
    CosmicGenesisNode(
      nodeId: json['nodeId'] as String,
      name: json['name'] as String,
      description: json['description'] as String,
      type: $enumDecode(_$CosmicNodeTypeEnumMap, json['type']),
      currentLevel: (json['currentLevel'] as num).toInt(),
      maxLevel: (json['maxLevel'] as num).toInt(),
      baseLuminaCost: (json['baseLuminaCost'] as num).toDouble(),
      costMultiplier: (json['costMultiplier'] as num).toDouble(),
      effects: (json['effects'] as List<dynamic>)
          .map((e) => CosmicNodeEffect.fromJson(e as Map<String, dynamic>))
          .toList(),
      isUnlocked: json['isUnlocked'] as bool,
      lastUpgraded: json['lastUpgraded'] == null
          ? null
          : DateTime.parse(json['lastUpgraded'] as String),
    );

Map<String, dynamic> _$CosmicGenesisNodeToJson(CosmicGenesisNode instance) =>
    <String, dynamic>{
      'nodeId': instance.nodeId,
      'name': instance.name,
      'description': instance.description,
      'type': _$CosmicNodeTypeEnumMap[instance.type]!,
      'currentLevel': instance.currentLevel,
      'maxLevel': instance.maxLevel,
      'baseLuminaCost': instance.baseLuminaCost,
      'costMultiplier': instance.costMultiplier,
      'effects': instance.effects,
      'isUnlocked': instance.isUnlocked,
      'lastUpgraded': instance.lastUpgraded?.toIso8601String(),
    };

const _$CosmicNodeTypeEnumMap = {
  CosmicNodeType.gravitonAmplifier: 'graviton_amplifier',
  CosmicNodeType.chronoAccelerator: 'chrono_accelerator',
  CosmicNodeType.bioSynthesisNexus: 'bio_synthesis_nexus',
  CosmicNodeType.quantumResonator: 'quantum_resonator',
  CosmicNodeType.stellarFluxHarmonizer: 'stellar_flux_harmonizer',
};

CosmicNodeEffect _$CosmicNodeEffectFromJson(Map<String, dynamic> json) =>
    CosmicNodeEffect(
      effectType: json['effectType'] as String,
      multiplier: (json['multiplier'] as num).toDouble(),
      target: json['target'] as String,
      description: json['description'] as String,
    );

Map<String, dynamic> _$CosmicNodeEffectToJson(CosmicNodeEffect instance) =>
    <String, dynamic>{
      'effectType': instance.effectType,
      'multiplier': instance.multiplier,
      'target': instance.target,
      'description': instance.description,
    };

DailyStreakReward _$DailyStreakRewardFromJson(Map<String, dynamic> json) =>
    DailyStreakReward(
      streakDay: (json['streakDay'] as num).toInt(),
      stellarShardsReward: (json['stellarShardsReward'] as num).toDouble(),
      luminaReward: (json['luminaReward'] as num).toDouble(),
      description: json['description'] as String,
      isMilestone: json['isMilestone'] as bool,
      specialRewards: json['specialRewards'] as Map<String, dynamic>,
    );

Map<String, dynamic> _$DailyStreakRewardToJson(DailyStreakReward instance) =>
    <String, dynamic>{
      'streakDay': instance.streakDay,
      'stellarShardsReward': instance.stellarShardsReward,
      'luminaReward': instance.luminaReward,
      'description': instance.description,
      'isMilestone': instance.isMilestone,
      'specialRewards': instance.specialRewards,
    };
