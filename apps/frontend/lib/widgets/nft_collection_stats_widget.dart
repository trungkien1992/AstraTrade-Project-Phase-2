import 'package:flutter/material.dart';
import '../models/nft_models.dart';

/// Widget to display NFT collection statistics
class NFTCollectionStatsWidget extends StatelessWidget {
  final NFTCollection collection;

  const NFTCollectionStatsWidget({super.key, required this.collection});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            const Text(
              'Collection Stats',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildStatItem('Total NFTs', collection.totalNfts.toString()),
                _buildStatItem('Unique Achievements', collection.uniqueAchievements.toString()),
                _buildStatItem('Rarity Score', collection.totalRarityScore.toStringAsFixed(1)),
              ],
            ),
            const SizedBox(height: 16),
            const Divider(),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildValueItem(
                  'Stellar Shards', 
                  collection.collectionValue['stellar_shards']?.toStringAsFixed(0) ?? '0'
                ),
                _buildValueItem(
                  'Lumina', 
                  collection.collectionValue['lumina']?.toStringAsFixed(0) ?? '0'
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatItem(String label, String value) {
    return Column(
      children: [
        Text(
          value,
          style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: const TextStyle(color: Colors.grey),
        ),
      ],
    );
  }

  Widget _buildValueItem(String label, String value) {
    return Column(
      children: [
        Text(
          value,
          style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: const TextStyle(color: Colors.grey, fontSize: 12),
        ),
      ],
    );
  }
}