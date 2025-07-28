// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'simple_gamification.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

PlayerProgress _$PlayerProgressFromJson(Map<String, dynamic> json) =>
    PlayerProgress(
      playerId: json['playerId'] as String,
      xp: (json['xp'] as num).toInt(),
      level: (json['level'] as num).toInt(),
      tradingPoints: (json['tradingPoints'] as num).toInt(),
      practicePoints: (json['practicePoints'] as num).toInt(),
      streakDays: (json['streakDays'] as num).toInt(),
      lastActiveDate: DateTime.parse(json['lastActiveDate'] as String),
      createdAt: DateTime.parse(json['createdAt'] as String),
      achievements: (json['achievements'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
      stats: Map<String, int>.from(json['stats'] as Map),
    );

Map<String, dynamic> _$PlayerProgressToJson(PlayerProgress instance) =>
    <String, dynamic>{
      'playerId': instance.playerId,
      'xp': instance.xp,
      'level': instance.level,
      'tradingPoints': instance.tradingPoints,
      'practicePoints': instance.practicePoints,
      'streakDays': instance.streakDays,
      'lastActiveDate': instance.lastActiveDate.toIso8601String(),
      'createdAt': instance.createdAt.toIso8601String(),
      'achievements': instance.achievements,
      'stats': instance.stats,
    };

Achievement _$AchievementFromJson(Map<String, dynamic> json) => Achievement(
  id: json['id'] as String,
  name: json['name'] as String,
  description: json['description'] as String,
  type: $enumDecode(_$AchievementTypeEnumMap, json['type']),
  targetValue: (json['targetValue'] as num).toInt(),
  xpReward: (json['xpReward'] as num).toInt(),
  tradingPointsReward: (json['tradingPointsReward'] as num).toInt(),
  iconName: json['iconName'] as String,
  rarity: $enumDecode(_$AchievementRarityEnumMap, json['rarity']),
  requirements: (json['requirements'] as List<dynamic>)
      .map((e) => e as String)
      .toList(),
);

Map<String, dynamic> _$AchievementToJson(Achievement instance) =>
    <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'description': instance.description,
      'type': _$AchievementTypeEnumMap[instance.type]!,
      'targetValue': instance.targetValue,
      'xpReward': instance.xpReward,
      'tradingPointsReward': instance.tradingPointsReward,
      'iconName': instance.iconName,
      'rarity': _$AchievementRarityEnumMap[instance.rarity]!,
      'requirements': instance.requirements,
    };

const _$AchievementTypeEnumMap = {
  AchievementType.firstTrade: 'first_trade',
  AchievementType.tradeCount: 'trade_count',
  AchievementType.profitTarget: 'profit_target',
  AchievementType.streakMilestone: 'streak_milestone',
  AchievementType.levelMilestone: 'level_milestone',
  AchievementType.practiceMilestone: 'practice_milestone',
  AchievementType.realTrading: 'real_trading',
  AchievementType.specialEvent: 'special_event',
};

const _$AchievementRarityEnumMap = {
  AchievementRarity.common: 'common',
  AchievementRarity.uncommon: 'uncommon',
  AchievementRarity.rare: 'rare',
  AchievementRarity.epic: 'epic',
  AchievementRarity.legendary: 'legendary',
};

XPGainEvent _$XPGainEventFromJson(Map<String, dynamic> json) => XPGainEvent(
  eventId: json['eventId'] as String,
  playerId: json['playerId'] as String,
  source: $enumDecode(_$XPGainSourceEnumMap, json['source']),
  xpGained: (json['xpGained'] as num).toInt(),
  tradingPointsGained: (json['tradingPointsGained'] as num).toInt(),
  practicePointsGained: (json['practicePointsGained'] as num).toInt(),
  description: json['description'] as String,
  timestamp: DateTime.parse(json['timestamp'] as String),
  metadata: json['metadata'] as Map<String, dynamic>,
);

Map<String, dynamic> _$XPGainEventToJson(XPGainEvent instance) =>
    <String, dynamic>{
      'eventId': instance.eventId,
      'playerId': instance.playerId,
      'source': _$XPGainSourceEnumMap[instance.source]!,
      'xpGained': instance.xpGained,
      'tradingPointsGained': instance.tradingPointsGained,
      'practicePointsGained': instance.practicePointsGained,
      'description': instance.description,
      'timestamp': instance.timestamp.toIso8601String(),
      'metadata': instance.metadata,
    };

const _$XPGainSourceEnumMap = {
  XPGainSource.practiceTrade: 'practice_trade',
  XPGainSource.realTrade: 'real_trade',
  XPGainSource.profitableTrade: 'profitable_trade',
  XPGainSource.dailyLogin: 'daily_login',
  XPGainSource.streakBonus: 'streak_bonus',
  XPGainSource.levelUp: 'level_up',
  XPGainSource.achievement: 'achievement',
  XPGainSource.firstTimeBonus: 'first_time_bonus',
};

DailyReward _$DailyRewardFromJson(Map<String, dynamic> json) => DailyReward(
  streakDay: (json['streakDay'] as num).toInt(),
  xpReward: (json['xpReward'] as num).toInt(),
  tradingPointsReward: (json['tradingPointsReward'] as num).toInt(),
  description: json['description'] as String,
  isMilestone: json['isMilestone'] as bool,
  bonusRewards: json['bonusRewards'] as Map<String, dynamic>,
);

Map<String, dynamic> _$DailyRewardToJson(DailyReward instance) =>
    <String, dynamic>{
      'streakDay': instance.streakDay,
      'xpReward': instance.xpReward,
      'tradingPointsReward': instance.tradingPointsReward,
      'description': instance.description,
      'isMilestone': instance.isMilestone,
      'bonusRewards': instance.bonusRewards,
    };
