import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/simple_gamification_provider.dart';
import '../services/mobile_haptic_service.dart';
import '../models/simple_gamification.dart';

/// Mobile-optimized progress widget showing XP, level, and achievements
/// Designed for quick glance information with haptic feedback
class MobileProgressWidget extends StatefulWidget {
  final bool showAchievements;
  final VoidCallback? onTap;

  const MobileProgressWidget({
    super.key,
    this.showAchievements = true,
    this.onTap,
  });

  @override
  State<MobileProgressWidget> createState() => _MobileProgressWidgetState();
}

class _MobileProgressWidgetState extends State<MobileProgressWidget>
    with TickerProviderStateMixin {
  final _hapticService = MobileHapticService();

  late AnimationController _progressController;
  late AnimationController _achievementController;
  late Animation<double> _progressAnimation;
  late Animation<double> _achievementAnimation;

  @override
  void initState() {
    super.initState();

    _progressController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );

    _achievementController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );

    _progressAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _progressController, curve: Curves.easeOutCubic),
    );

    _achievementAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _achievementController, curve: Curves.elasticOut),
    );

    _hapticService.initialize();
    _progressController.forward();
  }

  @override
  void dispose() {
    _progressController.dispose();
    _achievementController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<SimpleGamificationProvider>(
      builder: (context, gamification, child) {
        if (gamification.isLoading) {
          return _buildLoadingWidget();
        }

        if (gamification.currentProgress == null) {
          return _buildEmptyWidget();
        }

        return GestureDetector(
          onTap: () async {
            await _hapticService.mediumTap();
            widget.onTap?.call();
          },
          child: Card(
            elevation: 6,
            margin: const EdgeInsets.all(12),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(16),
            ),
            child: Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(16),
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [Colors.blue[50]!, Colors.purple[50]!],
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildHeader(gamification),
                  const SizedBox(height: 16),
                  _buildProgressBar(gamification),
                  const SizedBox(height: 16),
                  _buildStats(gamification),
                  // if (widget.showAchievements) ...[
                  //   const SizedBox(height: 16),
                  //   _buildRecentAchievements(gamification),
                  // ],
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildLoadingWidget() {
    return Card(
      elevation: 4,
      margin: const EdgeInsets.all(12),
      child: Container(
        height: 120,
        child: const Center(child: CircularProgressIndicator()),
      ),
    );
  }

  Widget _buildEmptyWidget() {
    return Card(
      elevation: 4,
      margin: const EdgeInsets.all(12),
      child: Container(
        height: 120,
        padding: const EdgeInsets.all(16),
        child: const Center(
          child: Text(
            'Progress data not available',
            style: TextStyle(color: Colors.grey),
          ),
        ),
      ),
    );
  }

  Widget _buildHeader(SimpleGamificationProvider gamification) {
    final rankInfo = gamification.getRankInfo();

    return Row(
      children: [
        Container(
          width: 48,
          height: 48,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            gradient: LinearGradient(
              colors: [Colors.blue[400]!, Colors.purple[400]!],
            ),
          ),
          child: Center(
            child: Text(
              rankInfo['level'].toString(),
              style: const TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
                fontSize: 18,
              ),
            ),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                rankInfo['rank'],
                style: Theme.of(
                  context,
                ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
              ),
              Text(
                'Level ${rankInfo['level']}',
                style: Theme.of(
                  context,
                ).textTheme.bodyMedium?.copyWith(color: Colors.blue[600]),
              ),
            ],
          ),
        ),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: Colors.amber[100],
            borderRadius: BorderRadius.circular(12),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(Icons.stars, size: 16, color: Colors.amber[700]),
              const SizedBox(width: 4),
              Text(
                '${rankInfo['total_xp']} XP',
                style: TextStyle(
                  color: Colors.amber[700],
                  fontWeight: FontWeight.bold,
                  fontSize: 12,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildProgressBar(SimpleGamificationProvider gamification) {
    final rankInfo = gamification.getRankInfo();
    final progress = rankInfo['progress'] as double;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Progress to Level ${rankInfo['level'] + 1}',
              style: Theme.of(
                context,
              ).textTheme.bodyMedium?.copyWith(fontWeight: FontWeight.w500),
            ),
            Text(
              '${rankInfo['xp_to_next']} XP needed',
              style: Theme.of(
                context,
              ).textTheme.bodySmall?.copyWith(color: Colors.grey[600]),
            ),
          ],
        ),
        const SizedBox(height: 8),
        AnimatedBuilder(
          animation: _progressAnimation,
          builder: (context, child) {
            return ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: Container(
                height: 8,
                decoration: BoxDecoration(
                  color: Colors.grey[300],
                  borderRadius: BorderRadius.circular(8),
                ),
                child: FractionallySizedBox(
                  alignment: Alignment.centerLeft,
                  widthFactor: progress * _progressAnimation.value,
                  child: Container(
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(8),
                      gradient: LinearGradient(
                        colors: [Colors.blue[400]!, Colors.purple[400]!],
                      ),
                    ),
                  ),
                ),
              ),
            );
          },
        ),
        const SizedBox(height: 4),
        Text(
          '${(progress * 100).toStringAsFixed(1)}% complete',
          style: Theme.of(
            context,
          ).textTheme.bodySmall?.copyWith(color: Colors.grey[600]),
        ),
      ],
    );
  }

  Widget _buildStats(SimpleGamificationProvider gamification) {
    final stats = gamification.getTradingStats();

    return Row(
      children: [
        Expanded(
          child: _buildStatItem(
            'Trades',
            stats['total_trades'].toString(),
            Icons.trending_up,
            Colors.blue,
          ),
        ),
        Expanded(
          child: _buildStatItem(
            'Success',
            '${(stats['success_rate'] * 100).toStringAsFixed(0)}%',
            Icons.target,
            Colors.green,
          ),
        ),
        Expanded(
          child: _buildStatItem(
            'Streak',
            '${stats['streak_days']}d',
            Icons.local_fire_department,
            Colors.orange,
          ),
        ),
        Expanded(
          child: _buildStatItem(
            'Points',
            stats['trading_points'].toString(),
            Icons.stars,
            Colors.purple,
          ),
        ),
      ],
    );
  }

  Widget _buildStatItem(
    String label,
    String value,
    IconData icon,
    Color color,
  ) {
    return GestureDetector(
      onTap: () async {
        await _hapticService.lightTap();
      },
      child: Container(
        padding: const EdgeInsets.all(8),
        margin: const EdgeInsets.symmetric(horizontal: 2),
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: color.withOpacity(0.3)),
        ),
        child: Column(
          children: [
            Icon(icon, color: color, size: 16),
            const SizedBox(height: 2),
            Text(
              value,
              style: TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 14,
                color: color,
              ),
            ),
            Text(
              label,
              style: TextStyle(fontSize: 10, color: Colors.grey[600]),
            ),
          ],
        ),
      ),
    );
  }

  // Widget _buildRecentAchievements(SimpleGamificationProvider gamification) {
  //   final recentAchievements = gamification.getRecentAchievements();
  //   final almostComplete = gamification.getAlmostCompleteAchievements();

  //   if (recentAchievements.isEmpty && almostComplete.isEmpty) {
  //     return const SizedBox();
  //   }

  //   return Column(
  //     crossAxisAlignment: CrossAxisAlignment.start,
  //     children: [
  //       Text(
  //         'Achievements',
  //         style: Theme.of(context).textTheme.titleSmall?.copyWith(
  //           fontWeight: FontWeight.bold,
  //         ),
  //       ),
  //       const SizedBox(height: 8),

  //       // Recent achievements
  //       if (recentAchievements.isNotEmpty) ...[
  //         ...recentAchievements.take(2).map((achievement) =>
  //           _buildAchievementChip(achievement, true)
  //         ),
  //       ],

  //       // Almost complete achievements
  //       if (almostComplete.isNotEmpty) ...[
  //         ...almostComplete.take(1).map((achievement) =>
  //           _buildAchievementChip(achievement, false)
  //         ),
  //       ],
  //     ],
  //   );
  // }

  // Widget _buildAchievementChip(Achievement achievement, bool isCompleted) {
  //   return GestureDetector(
  //     onTap: () async {
  //       await _hapticService.lightTap();
  //       if (isCompleted) {
  //         _achievementController.forward().then((_) {
  //           _achievementController.reverse();
  //         });
  //       }
  //     },
  //     child: Container(
  //       margin: const EdgeInsets.only(bottom: 4),
  //       padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
  //       decoration: BoxDecoration(
  //         color: isCompleted ? Colors.green[100] : Colors.grey[200],
  //         borderRadius: BorderRadius.circular(12),
  //         border: Border.all(
  //           color: isCompleted ? Colors.green[300]! : Colors.grey[400]!,
  //         ),
  //       ),
  //       child: Row(
  //         mainAxisSize: MainAxisSize.min,
  //         children: [
  //           Icon(
  //             isCompleted ? Icons.check_circle : Icons.hourglass_empty,
  //             size: 16,
  //             color: isCompleted ? Colors.green[600] : Colors.grey[600],
  //           ),
  //           const SizedBox(width: 4),
  //           Flexible(
  //             child: Text(
  //               achievement.name,
  //               style: TextStyle(
  //                 fontSize: 12,
  //                 fontWeight: FontWeight.w500,
  //                 color: isCompleted ? Colors.green[700] : Colors.grey[700],
  //               ),
  //               overflow: TextOverflow.ellipsis,
  //             ),
  //           ),
  //           if (!isCompleted) ...[
  //             const SizedBox(width: 4),
  //             Text(
  //               '75%+',
  //               style: TextStyle(
  //                 fontSize: 10,
  //                 color: Colors.grey[600],
  //               ),
  //             ),
  //           ],
  //         ],
  //       ),
  //     ),
  //   );
  // }
}
