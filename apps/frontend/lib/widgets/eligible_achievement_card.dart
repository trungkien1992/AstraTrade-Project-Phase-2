import 'package:flutter/material.dart';
import '../models/nft_models.dart';

/// Widget to display an eligible achievement for NFT minting
class EligibleAchievementCard extends StatelessWidget {
  final EligibleAchievement achievement;
  final VoidCallback onMintPressed;
  final bool isMinting;

  const EligibleAchievementCard({
    super.key,
    required this.achievement,
    required this.onMintPressed,
    required this.isMinting,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                // Achievement icon
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: _getRarityColor(achievement.rarity),
                    shape: BoxShape.circle,
                  ),
                  child: Icon(
                    _getAchievementIcon(achievement.achievementType),
                    color: Colors.white,
                  ),
                ),
                const SizedBox(width: 16),
                // Achievement info
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        achievement.name,
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        achievement.description,
                        style: const TextStyle(color: Colors.grey),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            // Rarity badge
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              decoration: BoxDecoration(
                color: _getRarityColor(achievement.rarity),
                borderRadius: BorderRadius.circular(20),
              ),
              child: Text(
                achievement.rarity.toUpperCase(),
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            const SizedBox(height: 16),
            // Mint button
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: isMinting ? null : onMintPressed,
                style: ElevatedButton.styleFrom(
                  backgroundColor: _getRarityColor(achievement.rarity),
                ),
                child: isMinting
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: Colors.white,
                        ),
                      )
                    : const Text(
                        'Mint Genesis NFT',
                        style: TextStyle(color: Colors.white),
                      ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// Get color based on achievement rarity
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
