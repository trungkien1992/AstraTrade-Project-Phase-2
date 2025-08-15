import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/nft_providers.dart';
import '../providers/auth_provider.dart';
import '../models/nft_models.dart';
import '../widgets/nft_card_widget.dart';
import '../widgets/nft_collection_stats_widget.dart';

/// Screen to display user's NFT collection
class NFTCollectionScreen extends ConsumerWidget {
  const NFTCollectionScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final user = ref.watch(authProvider).value;

    if (user == null) {
      return const Scaffold(
        body: Center(child: Text('Please log in to view your NFT collection')),
      );
    }

    final collectionAsync = ref.watch(userNFTCollectionProvider(user.id));

    return Scaffold(
      appBar: AppBar(
        title: const Text('My NFT Collection'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => ref.invalidate(userNFTCollectionProvider(user.id)),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          ref.invalidate(userNFTCollectionProvider(user.id));
        },
        child: collectionAsync.when(
          data: (collection) => _buildCollectionContent(context, collection),
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (error, stack) => Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(Icons.error, size: 48, color: Colors.red),
                const SizedBox(height: 16),
                Text('Error loading collection: $error'),
                const SizedBox(height: 16),
                ElevatedButton(
                  onPressed: () =>
                      ref.invalidate(userNFTCollectionProvider(user.id)),
                  child: const Text('Retry'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildCollectionContent(
    BuildContext context,
    NFTCollection collection,
  ) {
    if (collection.totalNfts == 0) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.collections_outlined, size: 64, color: Colors.grey),
            SizedBox(height: 16),
            Text(
              'No NFTs in your collection yet',
              style: TextStyle(fontSize: 18),
            ),
            SizedBox(height: 8),
            Text(
              'Complete achievements to mint Genesis NFTs',
              style: TextStyle(color: Colors.grey),
            ),
          ],
        ),
      );
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Collection stats
          NFTCollectionStatsWidget(collection: collection),

          const SizedBox(height: 24),

          // Featured NFT
          if (collection.featuredNft != null) ...[
            const Text(
              'Featured NFT',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            NFTCardWidget(nft: collection.featuredNft!),
            const SizedBox(height: 24),
          ],

          // Recent NFTs
          const Text(
            'Recent NFTs',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 12),
          GridView.builder(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: 2,
              crossAxisSpacing: 12,
              mainAxisSpacing: 12,
              childAspectRatio: 0.8,
            ),
            itemCount: collection.recentNfts.length,
            itemBuilder: (context, index) {
              return NFTCardWidget(nft: collection.recentNfts[index]);
            },
          ),
        ],
      ),
    );
  }
}
