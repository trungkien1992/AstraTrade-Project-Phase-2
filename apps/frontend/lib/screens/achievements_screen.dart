import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/simple_gamification_provider.dart';
import '../models/simple_gamification.dart';

/// Simple achievements and progress screen
/// No cosmic themes - clean, straightforward design
class AchievementsScreen extends StatelessWidget {
  const AchievementsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Achievements & Progress'),
        backgroundColor: Colors.blue[800],
        foregroundColor: Colors.white,
      ),
      body: Consumer<SimpleGamificationProvider>(
        builder: (context, gamification, child) {
          if (gamification.isLoading) {
            return const Center(child: CircularProgressIndicator());
          }

          if (gamification.error != null) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.error, color: Colors.red[400], size: 64),
                  const SizedBox(height: 16),
                  Text(
                    'Error loading achievements',
                    style: Theme.of(context).textTheme.headlineSmall,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    gamification.error!,
                    style: Theme.of(context).textTheme.bodyMedium,
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: () {
                      gamification.clearError();
                      gamification.refresh();
                    },
                    child: const Text('Retry'),
                  ),
                ],
              ),
            );
          }

          final progress = gamification.currentProgress;
          if (progress == null) {
            return const Center(
              child: Text('No progress data available'),
            );
          }

          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildProgressOverview(context, gamification),
                const SizedBox(height: 24),
                _buildQuickStats(context, gamification),
                const SizedBox(height: 24),
                _buildAchievementsSection(context, gamification),
                const SizedBox(height: 24),
                _buildRecentActivity(context, gamification),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildProgressOverview(BuildContext context, SimpleGamificationProvider gamification) {
    final rankInfo = gamification.getRankInfo();
    
    return Card(
      elevation: 4,
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.stars, color: Colors.amber[600], size: 32),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        rankInfo['rank'],
                        style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        'Level ${rankInfo['level']}',
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          color: Colors.blue[600],
                        ),
                      ),
                    ],
                  ),
                ),
                Text(
                  '${rankInfo['total_xp']} XP',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: Colors.blue[800],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Progress to Level ${rankInfo['level'] + 1}',
                      style: Theme.of(context).textTheme.bodyMedium,
                    ),
                    Text(
                      '${rankInfo['xp_to_next']} XP needed',
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                LinearProgressIndicator(
                  value: rankInfo['progress'],
                  backgroundColor: Colors.grey[300],
                  valueColor: AlwaysStoppedAnimation<Color>(Colors.blue[600]!),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildQuickStats(BuildContext context, SimpleGamificationProvider gamification) {
    final stats = gamification.getTradingStats();
    
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Trading Statistics',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: _buildStatItem(
                    context,
                    'Total Trades',
                    stats['total_trades'].toString(),
                    Icons.trending_up,
                    Colors.blue,
                  ),
                ),
                Expanded(
                  child: _buildStatItem(
                    context,
                    'Success Rate',
                    '${(stats['success_rate'] * 100).toStringAsFixed(1)}%',
                    Icons.target,
                    Colors.green,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: _buildStatItem(
                    context,
                    'Current Streak',
                    '${stats['streak_days']} days',
                    Icons.local_fire_department,
                    Colors.orange,
                  ),
                ),
                Expanded(
                  child: _buildStatItem(
                    context,
                    'Trading Points',
                    stats['trading_points'].toString(),
                    Icons.stars,
                    Colors.purple,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatItem(BuildContext context, String label, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(height: 4),
          Text(
            value,
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          Text(
            label,
            style: Theme.of(context).textTheme.bodySmall,
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildAchievementsSection(BuildContext context, SimpleGamificationProvider gamification) {
    final earnedAchievements = gamification.earnedAchievements;
    final availableAchievements = gamification.availableAchievements;
    final progress = gamification.achievementProgress;
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Achievements',
          style: Theme.of(context).textTheme.titleLarge?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          '${earnedAchievements.length} of ${gamification.achievements.length} earned',
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
            color: Colors.grey[600],
          ),
        ),
        const SizedBox(height: 16),
        
        // Earned Achievements
        if (earnedAchievements.isNotEmpty) ...[
          Text(
            'Earned Achievements',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.bold,
              color: Colors.green[700],
            ),
          ),
          const SizedBox(height: 8),
          ...earnedAchievements.map((achievement) => _buildAchievementCard(
            context, achievement, true, 1.0,
          )),
          const SizedBox(height: 16),
        ],
        
        // Available Achievements
        if (availableAchievements.isNotEmpty) ...[
          Text(
            'Available Achievements',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          ...availableAchievements.map((achievement) => _buildAchievementCard(
            context, achievement, false, progress[achievement.id] ?? 0.0,
          )),
        ],
      ],
    );
  }

  Widget _buildAchievementCard(BuildContext context, Achievement achievement, bool isEarned, double progress) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      elevation: isEarned ? 3 : 1,
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(12),
          border: isEarned 
              ? Border.all(color: Colors.green[400]!, width: 2)
              : null,
        ),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: isEarned ? Colors.green[100] : Colors.grey[200],
                ),
                child: Icon(
                  isEarned ? Icons.check_circle : _getAchievementIcon(achievement.type),
                  color: isEarned ? Colors.green[600] : Colors.grey[600],
                  size: 28,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            achievement.name,
                            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.bold,
                              color: isEarned ? Colors.green[700] : null,
                            ),
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                          decoration: BoxDecoration(
                            color: _getRarityColor(achievement.rarity).withOpacity(0.2),
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Text(
                            achievement.rarity.name.toUpperCase(),
                            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: _getRarityColor(achievement.rarity),
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(
                      achievement.description,
                      style: Theme.of(context).textTheme.bodyMedium,
                    ),
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        Icon(Icons.stars, size: 16, color: Colors.amber[600]),
                        const SizedBox(width: 4),
                        Text(
                          '${achievement.xpReward} XP',
                          style: Theme.of(context).textTheme.bodySmall,
                        ),
                        const SizedBox(width: 16),
                        Icon(Icons.emoji_events, size: 16, color: Colors.purple[600]),
                        const SizedBox(width: 4),
                        Text(
                          '${achievement.tradingPointsReward} TP',
                          style: Theme.of(context).textTheme.bodySmall,
                        ),
                      ],
                    ),
                    if (!isEarned && progress > 0) ...[
                      const SizedBox(height: 8),
                      LinearProgressIndicator(
                        value: progress,
                        backgroundColor: Colors.grey[300],
                        valueColor: AlwaysStoppedAnimation<Color>(Colors.blue[600]!),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        '${(progress * 100).toStringAsFixed(0)}% complete',
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: Colors.grey[600],
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildRecentActivity(BuildContext context, SimpleGamificationProvider gamification) {
    final recentEvents = gamification.recentEvents.take(10).toList();
    
    if (recentEvents.isEmpty) {
      return const SizedBox();
    }
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Recent Activity',
          style: Theme.of(context).textTheme.titleLarge?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 16),
        ...recentEvents.map((event) => _buildActivityItem(context, event)),
      ],
    );
  }

  Widget _buildActivityItem(BuildContext context, XPGainEvent event) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: _getSourceColor(event.source).withOpacity(0.2),
          child: Icon(
            _getSourceIcon(event.source),
            color: _getSourceColor(event.source),
          ),
        ),
        title: Text(event.description),
        subtitle: Text(_formatTimestamp(event.timestamp)),
        trailing: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            if (event.xpGained > 0)
              Text(
                '+${event.xpGained} XP',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Colors.blue[600],
                  fontWeight: FontWeight.bold,
                ),
              ),
            if (event.tradingPointsGained > 0)
              Text(
                '+${event.tradingPointsGained} TP',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Colors.purple[600],
                  fontWeight: FontWeight.bold,
                ),
              ),
          ],
        ),
      ),
    );
  }

  IconData _getAchievementIcon(AchievementType type) {
    switch (type) {
      case AchievementType.firstTrade:
        return Icons.play_arrow;
      case AchievementType.tradeCount:
        return Icons.trending_up;
      case AchievementType.profitTarget:
        return Icons.attach_money;
      case AchievementType.streakMilestone:
        return Icons.local_fire_department;
      case AchievementType.levelMilestone:
        return Icons.stars;
      case AchievementType.practiceMilestone:
        return Icons.school;
      case AchievementType.realTrading:
        return Icons.account_balance;
      case AchievementType.specialEvent:
        return Icons.celebration;
    }
  }

  Color _getRarityColor(AchievementRarity rarity) {
    switch (rarity) {
      case AchievementRarity.common:
        return Colors.grey[600]!;
      case AchievementRarity.uncommon:
        return Colors.green[600]!;
      case AchievementRarity.rare:
        return Colors.blue[600]!;
      case AchievementRarity.epic:
        return Colors.purple[600]!;
      case AchievementRarity.legendary:
        return Colors.orange[600]!;
    }
  }

  IconData _getSourceIcon(XPGainSource source) {
    switch (source) {
      case XPGainSource.practiceTrade:
        return Icons.school;
      case XPGainSource.realTrade:
        return Icons.account_balance;
      case XPGainSource.profitableTrade:
        return Icons.trending_up;
      case XPGainSource.dailyLogin:
        return Icons.calendar_today;
      case XPGainSource.streakBonus:
        return Icons.local_fire_department;
      case XPGainSource.levelUp:
        return Icons.keyboard_arrow_up;
      case XPGainSource.achievement:
        return Icons.emoji_events;
      case XPGainSource.firstTimeBonus:
        return Icons.star;
    }
  }

  Color _getSourceColor(XPGainSource source) {
    switch (source) {
      case XPGainSource.practiceTrade:
        return Colors.blue[600]!;
      case XPGainSource.realTrade:
        return Colors.green[600]!;
      case XPGainSource.profitableTrade:
        return Colors.green[700]!;
      case XPGainSource.dailyLogin:
        return Colors.orange[600]!;
      case XPGainSource.streakBonus:
        return Colors.red[600]!;
      case XPGainSource.levelUp:
        return Colors.purple[600]!;
      case XPGainSource.achievement:
        return Colors.amber[600]!;
      case XPGainSource.firstTimeBonus:
        return Colors.pink[600]!;
    }
  }

  String _formatTimestamp(DateTime timestamp) {
    final now = DateTime.now();
    final difference = now.difference(timestamp);
    
    if (difference.inMinutes < 1) {
      return 'Just now';
    } else if (difference.inHours < 1) {
      return '${difference.inMinutes}m ago';
    } else if (difference.inDays < 1) {
      return '${difference.inHours}h ago';
    } else if (difference.inDays < 7) {
      return '${difference.inDays}d ago';
    } else {
      return '${timestamp.day}/${timestamp.month}/${timestamp.year}';
    }
  }
}