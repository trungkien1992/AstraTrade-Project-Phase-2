// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'leaderboard.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

LeaderboardEntry _$LeaderboardEntryFromJson(Map<String, dynamic> json) =>
    LeaderboardEntry(
      userId: json['userId'] as String,
      username: json['username'] as String,
      avatarUrl: json['avatarUrl'] as String,
      rank: (json['rank'] as num).toInt(),
      stellarShards: (json['stellarShards'] as num).toInt(),
      lumina: (json['lumina'] as num).toInt(),
      level: (json['level'] as num).toInt(),
      totalXP: (json['totalXP'] as num).toInt(),
      cosmicTier: json['cosmicTier'] as String,
      isVerifiedLuminaWeaver: json['isVerifiedLuminaWeaver'] as bool? ?? false,
      isCurrentUser: json['isCurrentUser'] as bool? ?? false,
      planetIcon: json['planetIcon'] as String,
      winStreak: (json['winStreak'] as num?)?.toInt() ?? 0,
      totalTrades: (json['totalTrades'] as num?)?.toInt() ?? 0,
      winRate: (json['winRate'] as num?)?.toDouble() ?? 0.0,
      lastActive: DateTime.parse(json['lastActive'] as String),
    );

Map<String, dynamic> _$LeaderboardEntryToJson(LeaderboardEntry instance) =>
    <String, dynamic>{
      'userId': instance.userId,
      'username': instance.username,
      'avatarUrl': instance.avatarUrl,
      'rank': instance.rank,
      'stellarShards': instance.stellarShards,
      'lumina': instance.lumina,
      'level': instance.level,
      'totalXP': instance.totalXP,
      'cosmicTier': instance.cosmicTier,
      'isVerifiedLuminaWeaver': instance.isVerifiedLuminaWeaver,
      'isCurrentUser': instance.isCurrentUser,
      'planetIcon': instance.planetIcon,
      'winStreak': instance.winStreak,
      'totalTrades': instance.totalTrades,
      'winRate': instance.winRate,
      'lastActive': instance.lastActive.toIso8601String(),
    };
