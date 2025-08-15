import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/nft_models.dart';
import '../services/nft_service.dart';

/// Provider for NFT service
final nftServiceProvider = Provider<NFTService>((ref) {
  return NFTService();
});

/// Provider for user's NFT collection
final userNFTCollectionProvider = FutureProvider.family<NFTCollection, int>((
  ref,
  userId,
) async {
  final nftService = ref.read(nftServiceProvider);
  return await nftService.getUserNFTCollection(userId);
});

/// Provider for eligible achievements for NFT minting
final eligibleAchievementsProvider = FutureProvider<List<EligibleAchievement>>((
  ref,
) async {
  final nftService = ref.read(nftServiceProvider);
  return await nftService.getEligibleAchievements();
});

/// Provider for NFT marketplace listings
final nftMarketplaceProvider =
    FutureProvider.family<List<NFTMarketplaceItem>, Map<String, dynamic>>((
      ref,
      filters,
    ) async {
      final nftService = ref.read(nftServiceProvider);

      return await nftService.getMarketplaceListings(
        rarity: filters['rarity'] as String?,
        achievementType: filters['achievementType'] as String?,
        minPrice: filters['minPrice'] as double?,
        maxPrice: filters['maxPrice'] as double?,
        currency: filters['currency'] as String? ?? 'stellar_shards',
        sortBy: filters['sortBy'] as String? ?? 'listed_at',
        sortOrder: filters['sortOrder'] as String? ?? 'desc',
        limit: filters['limit'] as int? ?? 20,
      );
    });

/// Provider for global NFT statistics
final globalNFTStatsProvider = FutureProvider<Map<String, dynamic>>((
  ref,
) async {
  final nftService = ref.read(nftServiceProvider);
  return await nftService.getGlobalNFTStats();
});
