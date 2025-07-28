import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/nft_providers.dart';
import '../providers/auth_provider.dart';
import '../services/nft_service.dart';
import '../models/nft_models.dart';
import '../widgets/eligible_achievement_card.dart';

/// Screen to mint new Genesis NFTs
class NFTMintingScreen extends ConsumerStatefulWidget {
  const NFTMintingScreen({super.key});

  @override
  ConsumerState<NFTMintingScreen> createState() => _NFTMintingScreenState();
}

class _NFTMintingScreenState extends ConsumerState<NFTMintingScreen> {
  bool _isMinting = false;

  @override
  Widget build(BuildContext context) {
    final user = ref.watch(authProvider).value;
    
    if (user == null) {
      return const Scaffold(
        body: Center(
          child: Text('Please log in to mint NFTs'),
        ),
      );
    }

    final eligibleAchievementsAsync = ref.watch(eligibleAchievementsProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Mint Genesis NFT'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: eligibleAchievementsAsync.when(
          data: (achievements) => _buildMintingContent(context, achievements),
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (error, stack) => Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(Icons.error, size: 48, color: Colors.red),
                const SizedBox(height: 16),
                Text('Error loading achievements: $error'),
                const SizedBox(height: 16),
                ElevatedButton(
                  onPressed: () => ref.invalidate(eligibleAchievementsProvider),
                  child: const Text('Retry'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildMintingContent(BuildContext context, List<EligibleAchievement> achievements) {
    if (achievements.isEmpty) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.emoji_events_outlined, size: 64, color: Colors.grey),
            SizedBox(height: 16),
            Text(
              'No eligible achievements for NFT minting',
              style: TextStyle(fontSize: 18),
            ),
            SizedBox(height: 8),
            Text(
              'Complete more achievements to unlock Genesis NFTs',
              style: TextStyle(color: Colors.grey),
            ),
          ],
        ),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Eligible Achievements',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 16),
        const Text(
          'Select an achievement to mint your Genesis NFT',
          style: TextStyle(color: Colors.grey),
        ),
        const SizedBox(height: 24),
        Expanded(
          child: ListView.builder(
            itemCount: achievements.length,
            itemBuilder: (context, index) {
              return EligibleAchievementCard(
                achievement: achievements[index],
                onMintPressed: () => _mintNFT(achievements[index]),
                isMinting: _isMinting,
              );
            },
          ),
        ),
      ],
    );
  }

  Future<void> _mintNFT(EligibleAchievement achievement) async {
    if (_isMinting) return;

    setState(() {
      _isMinting = true;
    });

    try {
      final nftService = ref.read(nftServiceProvider);
      final nft = await nftService.mintGenesisNFT(
        achievementType: achievement.achievementType,
        milestoneData: achievement.milestoneData,
      );

      if (mounted) {
        // Show success dialog
        await showDialog(
          context: context,
          builder: (context) {
            return AlertDialog(
              title: const Text('NFT Minted!'),
              content: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Icon(Icons.auto_awesome, size: 48, color: Colors.purple),
                  const SizedBox(height: 16),
                  Text(
                    'Congratulations! You\'ve minted a ${nft.rarity} Genesis NFT.',
                    textAlign: TextAlign.center,
                  ),
                ],
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.of(context).pop(),
                  child: const Text('OK'),
                ),
              ],
            );
          },
        );

        // Refresh the eligible achievements list
        ref.invalidate(eligibleAchievementsProvider);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to mint NFT: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isMinting = false;
        });
      }
    }
  }
}