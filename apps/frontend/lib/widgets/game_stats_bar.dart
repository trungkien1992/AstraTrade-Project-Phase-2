import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import '../providers/game_state_provider.dart';
import '../theme/cosmic_theme.dart';
import '../utils/constants.dart';
import '../services/analytics_service.dart';

/// Feature flag for game stats display
final gameStatsEnabledProvider = StateProvider<bool>((ref) => true);

/// Compact game statistics bar for displaying player progression
/// Designed to integrate seamlessly with existing trading interface
class GameStatsBar extends ConsumerWidget {
  const GameStatsBar({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final gameState = ref.watch(gameStateProvider);
    final isEnabled = ref.watch(gameStatsEnabledProvider);

    if (!isEnabled) return const SizedBox.shrink();

    // Track stats display
    AnalyticsService.trackEvent(
      name: 'game_stats_displayed',
      type: EventType.user_action,
      properties: {
        'stellar_shards': gameState.stellarShards,
        'level': gameState.level,
        'screen': 'trade_entry',
      },
    );

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            CosmicTheme.accentCyan.withOpacity(0.1),
            CosmicTheme.cosmicGold.withOpacity(0.1),
          ],
          begin: Alignment.centerLeft,
          end: Alignment.centerRight,
        ),
        borderRadius: BorderRadius.circular(AppConstants.defaultBorderRadius),
        border: Border.all(
          color: CosmicTheme.accentCyan.withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        children: [
          _buildStatItem(
            icon: Icons.auto_awesome,
            value: '${gameState.stellarShards}',
            label: 'Stellar Shards',
            color: CosmicTheme.cosmicGold,
          ),
          _buildDivider(),
          _buildStatItem(
            icon: Icons.trending_up,
            value: 'LVL ${gameState.level}',
            label: 'Cosmic Level',
            color: CosmicTheme.accentCyan,
          ),
          _buildDivider(),
          _buildStatItem(
            icon: Icons.stars,
            value: '${gameState.experience}',
            label: 'Experience',
            color: CosmicTheme.starWhite,
          ),
        ],
      ),
    );
  }

  Widget _buildStatItem({
    required IconData icon,
    required String value,
    required String label,
    required Color color,
  }) {
    return Expanded(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(icon, color: color, size: 16),
              const SizedBox(width: 4),
              Text(
                value,
                style: GoogleFonts.orbitron(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                  color: CosmicTheme.starWhite,
                ),
              ),
            ],
          ),
          const SizedBox(height: 2),
          Text(
            label,
            style: GoogleFonts.rajdhani(
              fontSize: 10,
              color: CosmicTheme.starWhite.withOpacity(0.7),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDivider() {
    return Container(
      height: 30,
      width: 1,
      color: CosmicTheme.accentCyan.withOpacity(0.3),
    );
  }
}
