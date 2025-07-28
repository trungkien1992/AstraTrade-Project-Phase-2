import 'package:flutter_test/flutter_test.dart';
import 'package:astratrade_app/models/nft_models.dart';

void main() {
  group('NFT Models Tests', () {
    test('GenesisNFT model creation', () {
      final nft = GenesisNFT(
        nftId: 'genesis_first_trade_abc123',
        tokenId: 1,
        achievementType: 'first_trade',
        rarity: 'common',
        pointsEarned: 100,
        metadata: {
          'name': 'Genesis First Trade',
          'description': 'First trade achievement NFT',
        },
        mintingTransaction: '0x1234567890abcdef',
        mintingStatus: 'minted',
        createdAt: DateTime.now(),
      );

      expect(nft.nftId, 'genesis_first_trade_abc123');
      expect(nft.tokenId, 1);
      expect(nft.achievementType, 'first_trade');
      expect(nft.rarity, 'common');
      expect(nft.pointsEarned, 100);
      expect(nft.mintingStatus, 'minted');
    });

    test('NFTCollection model creation', () {
      final nft = GenesisNFT(
        nftId: 'genesis_first_trade_abc123',
        tokenId: 1,
        achievementType: 'first_trade',
        rarity: 'common',
        pointsEarned: 100,
        metadata: {
          'name': 'Genesis First Trade',
          'description': 'First trade achievement NFT',
        },
        mintingTransaction: '0x1234567890abcdef',
        mintingStatus: 'minted',
        createdAt: DateTime.now(),
      );

      final collection = NFTCollection(
        userId: 123,
        totalNfts: 5,
        uniqueAchievements: 3,
        totalRarityScore: 15.5,
        featuredNft: nft,
        recentNfts: [nft],
        collectionValue: {
          'stellar_shards': 5000.0,
          'lumina': 500.0,
        },
      );

      expect(collection.userId, 123);
      expect(collection.totalNfts, 5);
      expect(collection.uniqueAchievements, 3);
      expect(collection.totalRarityScore, 15.5);
      expect(collection.featuredNft, nft);
      expect(collection.recentNfts.length, 1);
      expect(collection.collectionValue['stellar_shards'], 5000.0);
    });

    test('NFTMarketplaceItem model creation', () {
      final item = NFTMarketplaceItem(
        nftId: 'genesis_first_trade_abc123',
        tokenId: 1,
        ownerAddress: '0x1234567890abcdef',
        ownerUsername: 'Trader123',
        price: 1000.0,
        currency: 'stellar_shards',
        rarity: 'rare',
        achievementType: 'first_trade',
        metadata: {
          'name': 'Genesis First Trade',
        },
        listedAt: DateTime.now(),
        isFeatured: true,
      );

      expect(item.nftId, 'genesis_first_trade_abc123');
      expect(item.tokenId, 1);
      expect(item.ownerUsername, 'Trader123');
      expect(item.price, 1000.0);
      expect(item.currency, 'stellar_shards');
      expect(item.rarity, 'rare');
      expect(item.isFeatured, true);
    });

    test('EligibleAchievement model creation', () {
      final achievement = EligibleAchievement(
        achievementType: 'level_milestone',
        name: 'Stellar Ascension',
        description: 'Reached level 25',
        rarity: 'rare',
        requirementsMet: true,
        milestoneData: {
          'level_achieved': 25,
        },
      );

      expect(achievement.achievementType, 'level_milestone');
      expect(achievement.name, 'Stellar Ascension');
      expect(achievement.description, 'Reached level 25');
      expect(achievement.rarity, 'rare');
      expect(achievement.requirementsMet, true);
      expect(achievement.milestoneData['level_achieved'], 25);
    });
  });
}