// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'nft_models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

GenesisNFT _$GenesisNFTFromJson(Map<String, dynamic> json) => GenesisNFT(
  nftId: json['nftId'] as String,
  tokenId: (json['tokenId'] as num).toInt(),
  achievementType: json['achievementType'] as String,
  rarity: json['rarity'] as String,
  pointsEarned: (json['pointsEarned'] as num).toInt(),
  metadata: json['metadata'] as Map<String, dynamic>,
  mintingTransaction: json['mintingTransaction'] as String?,
  mintingStatus: json['mintingStatus'] as String,
  createdAt: DateTime.parse(json['createdAt'] as String),
);

Map<String, dynamic> _$GenesisNFTToJson(GenesisNFT instance) =>
    <String, dynamic>{
      'nftId': instance.nftId,
      'tokenId': instance.tokenId,
      'achievementType': instance.achievementType,
      'rarity': instance.rarity,
      'pointsEarned': instance.pointsEarned,
      'metadata': instance.metadata,
      'mintingTransaction': instance.mintingTransaction,
      'mintingStatus': instance.mintingStatus,
      'createdAt': instance.createdAt.toIso8601String(),
    };

NFTCollection _$NFTCollectionFromJson(Map<String, dynamic> json) =>
    NFTCollection(
      userId: (json['userId'] as num).toInt(),
      totalNfts: (json['totalNfts'] as num).toInt(),
      uniqueAchievements: (json['uniqueAchievements'] as num).toInt(),
      totalRarityScore: (json['totalRarityScore'] as num).toDouble(),
      featuredNft: json['featuredNft'] == null
          ? null
          : GenesisNFT.fromJson(json['featuredNft'] as Map<String, dynamic>),
      recentNfts: (json['recentNfts'] as List<dynamic>)
          .map((e) => GenesisNFT.fromJson(e as Map<String, dynamic>))
          .toList(),
      collectionValue: (json['collectionValue'] as Map<String, dynamic>).map(
        (k, e) => MapEntry(k, (e as num).toDouble()),
      ),
    );

Map<String, dynamic> _$NFTCollectionToJson(NFTCollection instance) =>
    <String, dynamic>{
      'userId': instance.userId,
      'totalNfts': instance.totalNfts,
      'uniqueAchievements': instance.uniqueAchievements,
      'totalRarityScore': instance.totalRarityScore,
      'featuredNft': instance.featuredNft,
      'recentNfts': instance.recentNfts,
      'collectionValue': instance.collectionValue,
    };

NFTMarketplaceItem _$NFTMarketplaceItemFromJson(Map<String, dynamic> json) =>
    NFTMarketplaceItem(
      nftId: json['nftId'] as String,
      tokenId: (json['tokenId'] as num).toInt(),
      ownerAddress: json['ownerAddress'] as String,
      ownerUsername: json['ownerUsername'] as String,
      price: (json['price'] as num).toDouble(),
      currency: json['currency'] as String,
      rarity: json['rarity'] as String,
      achievementType: json['achievementType'] as String,
      metadata: json['metadata'] as Map<String, dynamic>,
      listedAt: DateTime.parse(json['listedAt'] as String),
      isFeatured: json['isFeatured'] as bool,
    );

Map<String, dynamic> _$NFTMarketplaceItemToJson(NFTMarketplaceItem instance) =>
    <String, dynamic>{
      'nftId': instance.nftId,
      'tokenId': instance.tokenId,
      'ownerAddress': instance.ownerAddress,
      'ownerUsername': instance.ownerUsername,
      'price': instance.price,
      'currency': instance.currency,
      'rarity': instance.rarity,
      'achievementType': instance.achievementType,
      'metadata': instance.metadata,
      'listedAt': instance.listedAt.toIso8601String(),
      'isFeatured': instance.isFeatured,
    };

EligibleAchievement _$EligibleAchievementFromJson(Map<String, dynamic> json) =>
    EligibleAchievement(
      achievementType: json['achievementType'] as String,
      name: json['name'] as String,
      description: json['description'] as String,
      rarity: json['rarity'] as String,
      requirementsMet: json['requirementsMet'] as bool,
      milestoneData: json['milestoneData'] as Map<String, dynamic>,
    );

Map<String, dynamic> _$EligibleAchievementToJson(
  EligibleAchievement instance,
) => <String, dynamic>{
  'achievementType': instance.achievementType,
  'name': instance.name,
  'description': instance.description,
  'rarity': instance.rarity,
  'requirementsMet': instance.requirementsMet,
  'milestoneData': instance.milestoneData,
};
