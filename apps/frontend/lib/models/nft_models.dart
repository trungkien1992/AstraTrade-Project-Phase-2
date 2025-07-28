import 'package:json_annotation/json_annotation.dart';

part 'nft_models.g.dart';

/// Genesis NFT model
@JsonSerializable()
class GenesisNFT {
  final String nftId;
  final int tokenId;
  final String achievementType;
  final String rarity;
  final int pointsEarned;
  final Map<String, dynamic> metadata;
  final String? mintingTransaction;
  final String mintingStatus;
  final DateTime createdAt;

  GenesisNFT({
    required this.nftId,
    required this.tokenId,
    required this.achievementType,
    required this.rarity,
    required this.pointsEarned,
    required this.metadata,
    this.mintingTransaction,
    required this.mintingStatus,
    required this.createdAt,
  });

  factory GenesisNFT.fromJson(Map<String, dynamic> json) => _$GenesisNFTFromJson(json);
  Map<String, dynamic> toJson() => _$GenesisNFTToJson(this);
}

/// NFT Collection model
@JsonSerializable()
class NFTCollection {
  final int userId;
  final int totalNfts;
  final int uniqueAchievements;
  final double totalRarityScore;
  final GenesisNFT? featuredNft;
  final List<GenesisNFT> recentNfts;
  final Map<String, double> collectionValue;

  NFTCollection({
    required this.userId,
    required this.totalNfts,
    required this.uniqueAchievements,
    required this.totalRarityScore,
    this.featuredNft,
    required this.recentNfts,
    required this.collectionValue,
  });

  factory NFTCollection.fromJson(Map<String, dynamic> json) => _$NFTCollectionFromJson(json);
  Map<String, dynamic> toJson() => _$NFTCollectionToJson(this);
}

/// NFT Marketplace Item model
@JsonSerializable()
class NFTMarketplaceItem {
  final String nftId;
  final int tokenId;
  final String ownerAddress;
  final String ownerUsername;
  final double price;
  final String currency;
  final String rarity;
  final String achievementType;
  final Map<String, dynamic> metadata;
  final DateTime listedAt;
  final bool isFeatured;

  NFTMarketplaceItem({
    required this.nftId,
    required this.tokenId,
    required this.ownerAddress,
    required this.ownerUsername,
    required this.price,
    required this.currency,
    required this.rarity,
    required this.achievementType,
    required this.metadata,
    required this.listedAt,
    required this.isFeatured,
  });

  factory NFTMarketplaceItem.fromJson(Map<String, dynamic> json) => _$NFTMarketplaceItemFromJson(json);
  Map<String, dynamic> toJson() => _$NFTMarketplaceItemToJson(this);
}

/// Eligible Achievement model
@JsonSerializable()
class EligibleAchievement {
  final String achievementType;
  final String name;
  final String description;
  final String rarity;
  final bool requirementsMet;
  final Map<String, dynamic> milestoneData;

  EligibleAchievement({
    required this.achievementType,
    required this.name,
    required this.description,
    required this.rarity,
    required this.requirementsMet,
    required this.milestoneData,
  });

  factory EligibleAchievement.fromJson(Map<String, dynamic> json) => _$EligibleAchievementFromJson(json);
  Map<String, dynamic> toJson() => _$EligibleAchievementToJson(this);
}