import 'package:flutter/material.dart';
import '../models/nft_models.dart';

/// Widget to display an NFT card
class NFTCardWidget extends StatelessWidget {
  final GenesisNFT nft;
  final VoidCallback? onTap;

  const NFTCardWidget({super.key, required this.nft, this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Card(
        color: _getRarityColor(nft.rarity),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // NFT image placeholder
              Container(
                height: 120,
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(
                  _getAchievementIcon(nft.achievementType),
                  size: 48,
                  color: Colors.white,
                ),
              ),
              const SizedBox(height: 12),
              // NFT name
              Text(
                nft.metadata['name'] ?? 'Genesis NFT',
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 4),
              // Rarity badge
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: Colors.black.withOpacity(0.3),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  nft.rarity.toUpperCase(),
                  style: const TextStyle(
                    fontSize: 12,
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              const SizedBox(height: 8),
              // Achievement type
              Text(
                nft.achievementType.replaceAll('_', ' ').toUpperCase(),
                style: const TextStyle(fontSize: 12, color: Colors.white70),
              ),
            ],
          ),
        ),
      ),
    );
  }

  /// Get color based on NFT rarity
  Color _getRarityColor(String rarity) {
    switch (rarity.toLowerCase()) {
      case 'common':
        return Colors.grey.shade700;
      case 'uncommon':
        return Colors.green.shade700;
      case 'rare':
        return Colors.blue.shade700;
      case 'epic':
        return Colors.purple.shade700;
      case 'legendary':
        return Colors.orange.shade700;
      default:
        return Colors.grey.shade800;
    }
  }

  /// Get icon based on achievement type
  IconData _getAchievementIcon(String achievementType) {
    switch (achievementType) {
      case 'first_trade':
        return Icons.rocket_launch;
      case 'level_milestone':
        return Icons.trending_up;
      case 'constellation_founder':
        return Icons.group_work;
      case 'viral_legend':
        return Icons.share;
      case 'trading_master':
        return Icons.auto_graph;
      default:
        return Icons.emoji_events;
    }
  }
}
