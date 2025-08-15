import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/trading_provider.dart';
import '../onboarding/paywall.dart';
import '../services/analytics_service.dart';

class StreakTrackerScreen extends ConsumerWidget {
  const StreakTrackerScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final tradingState = ref.watch(tradingProvider);
    final progress = tradingState.progress;

    // Track screen view
    AnalyticsService.trackScreenView(
      'streak_tracker_screen',
      properties: {
        'current_streak': progress.currentStreak,
        'total_trades': progress.totalTrades,
        'win_rate': progress.winRate,
      },
    );

    return Scaffold(
      appBar: AppBar(
        title: const Text('Your Progress'),
        backgroundColor: Colors.blue[600],
        foregroundColor: Colors.white,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pop(context),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.analytics),
            onPressed: () async {
              await AnalyticsService.trackUserAction(
                'analytics_dashboard_opened',
                properties: {'source': 'streak_tracker_screen'},
              );
              Navigator.pushNamed(context, '/analytics');
            },
            tooltip: 'Analytics Dashboard',
          ),
        ],
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            children: [
              // Current Streak Card
              Card(
                elevation: 4,
                child: Padding(
                  padding: const EdgeInsets.all(20.0),
                  child: Column(
                    children: [
                      Icon(
                        Icons.local_fire_department,
                        size: 48,
                        color: progress.currentStreak > 0
                            ? Colors.orange
                            : Colors.grey,
                      ),
                      const SizedBox(height: 12),
                      Text(
                        '${progress.currentStreak}',
                        style: const TextStyle(
                          fontSize: 36,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        'Day${progress.currentStreak == 1 ? '' : 's'} Streak',
                        style: const TextStyle(
                          fontSize: 18,
                          color: Colors.grey,
                        ),
                      ),
                      if (progress.currentStreak > 0) ...[
                        const SizedBox(height: 8),
                        Text(
                          progress.isStreakActive
                              ? 'Keep it going!'
                              : 'Trade today to continue!',
                          style: TextStyle(
                            fontSize: 14,
                            color: progress.isStreakActive
                                ? Colors.green
                                : Colors.orange,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 20),

              // Stats Grid
              GridView.count(
                shrinkWrap: true,
                crossAxisCount: 2,
                childAspectRatio: 1.5,
                crossAxisSpacing: 12,
                mainAxisSpacing: 12,
                children: [
                  _buildStatCard(
                    'Total Trades',
                    '${progress.totalTrades}',
                    Icons.trending_up,
                    Colors.blue,
                  ),
                  _buildStatCard(
                    'Win Rate',
                    '${progress.winRate.toStringAsFixed(1)}%',
                    Icons.track_changes,
                    Colors.green,
                  ),
                  _buildStatCard(
                    'Best Streak',
                    '${progress.longestStreak}',
                    Icons.emoji_events,
                    Colors.amber,
                  ),
                  _buildStatCard(
                    'Avg Return',
                    '${progress.averageProfit > 0 ? '+' : ''}${progress.averageProfit.toStringAsFixed(1)}%',
                    Icons.analytics,
                    progress.averageProfit > 0 ? Colors.green : Colors.red,
                  ),
                ],
              ),

              const SizedBox(height: 20),

              // Subscription Status
              if (!progress.hasSubscription) ...[
                Card(
                  color: Colors.amber[50],
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      children: [
                        Icon(Icons.lock, size: 32, color: Colors.amber[700]),
                        const SizedBox(height: 8),
                        const Text(
                          'Unlock Unlimited Trading',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 4),
                        const Text(
                          'You have limited trades remaining',
                          style: TextStyle(fontSize: 14, color: Colors.grey),
                        ),
                        const SizedBox(height: 12),
                        SizedBox(
                          width: double.infinity,
                          child: ElevatedButton(
                            onPressed: () {
                              // TODO: Show paywall
                              _showPaywall(context);
                            },
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.amber[700],
                              foregroundColor: Colors.white,
                            ),
                            child: const Text('Upgrade Now'),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ],

              const SizedBox(height: 32),

              // Navigation Buttons
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton(
                      onPressed: () {
                        Navigator.pushReplacementNamed(context, '/trade-entry');
                      },
                      style: OutlinedButton.styleFrom(
                        side: BorderSide(color: Colors.blue[600]!),
                        padding: const EdgeInsets.symmetric(vertical: 16),
                      ),
                      child: Text(
                        'New Trade',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: Colors.blue[600],
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: ElevatedButton(
                      onPressed: () {
                        // TODO: Show trade history
                        _showTradeHistory(context, ref);
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.blue[600],
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 16),
                      ),
                      child: const Text(
                        'Trade History',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ),
                ],
              ),

              const SizedBox(
                height: 40,
              ), // Increased padding for better button visibility
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatCard(
    String title,
    String value,
    IconData icon,
    Color color,
  ) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 24, color: color),
            const SizedBox(height: 8),
            Text(
              value,
              style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            Text(
              title,
              style: const TextStyle(fontSize: 12, color: Colors.grey),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  void _showPaywall(BuildContext context) {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const PaywallScreen()),
    );
  }

  void _showTradeHistory(BuildContext context, WidgetRef ref) {
    final trades = ref.read(tradingProvider).trades;

    showModalBottomSheet(
      context: context,
      builder: (context) => Container(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            const Text(
              'Recent Trades',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            Expanded(
              child: trades.isEmpty
                  ? const Center(child: Text('No trades yet'))
                  : ListView.builder(
                      itemCount: trades.length,
                      itemBuilder: (context, index) {
                        final trade = trades[index];
                        return ListTile(
                          leading: Icon(
                            trade.direction == 'BUY'
                                ? Icons.trending_up
                                : Icons.trending_down,
                            color: trade.direction == 'BUY'
                                ? Colors.green
                                : Colors.red,
                          ),
                          title: Text('${trade.direction} ${trade.symbol}'),
                          subtitle: Text('\$${trade.amount.toInt()}'),
                          trailing: trade.isCompleted
                              ? Text(
                                  '${trade.profitLossPercentage > 0 ? '+' : ''}${trade.profitLossPercentage.toStringAsFixed(1)}%',
                                  style: TextStyle(
                                    color: trade.profitLossPercentage > 0
                                        ? Colors.green
                                        : Colors.red,
                                    fontWeight: FontWeight.bold,
                                  ),
                                )
                              : const Text('Pending'),
                        );
                      },
                    ),
            ),
          ],
        ),
      ),
    );
  }
}
