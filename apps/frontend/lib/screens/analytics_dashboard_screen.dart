import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/analytics_service.dart';
import '../services/ab_testing_service.dart';
import 'health_dashboard_screen.dart';

class AnalyticsDashboardScreen extends ConsumerStatefulWidget {
  const AnalyticsDashboardScreen({super.key});

  @override
  ConsumerState<AnalyticsDashboardScreen> createState() => _AnalyticsDashboardScreenState();
}

class _AnalyticsDashboardScreenState extends ConsumerState<AnalyticsDashboardScreen> {
  Map<String, dynamic>? _analyticsSummary;
  List<AnalyticsEvent>? _recentEvents;
  Map<String, dynamic>? _abTestResults;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadAnalyticsData();
  }

  Future<void> _loadAnalyticsData() async {
    setState(() => _isLoading = true);
    
    try {
      final summary = await AnalyticsService.getAnalyticsSummary();
      final events = await AnalyticsService.getEvents(limit: 50);
      final paywallResults = await ABTestingService.getTestResults('paywall_presentation');
      
      setState(() {
        _analyticsSummary = summary;
        _recentEvents = events;
        _abTestResults = paywallResults;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading analytics: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Analytics Dashboard'),
        backgroundColor: Colors.blue[600],
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.health_and_safety),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const HealthDashboardScreen()),
              );
            },
            tooltip: 'System Health',
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadAnalyticsData,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _loadAnalyticsData,
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildOverviewCards(),
                    const SizedBox(height: 24),
                    _buildABTestResults(),
                    const SizedBox(height: 24),
                    _buildRecentEvents(),
                    const SizedBox(height: 24),
                    _buildEventTypeBreakdown(),
                  ],
                ),
              ),
            ),
    );
  }

  Widget _buildOverviewCards() {
    if (_analyticsSummary == null) return const SizedBox();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Overview',
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 16),
        GridView.count(
          crossAxisCount: 2,
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          childAspectRatio: 1.5,
          crossAxisSpacing: 16,
          mainAxisSpacing: 16,
          children: [
            _buildMetricCard(
              'Total Events',
              _analyticsSummary!['total_events'].toString(),
              Icons.analytics,
              Colors.blue,
            ),
            _buildMetricCard(
              'Today\'s Events',
              _analyticsSummary!['todays_events'].toString(),
              Icons.today,
              Colors.green,
            ),
            _buildMetricCard(
              'Conversions',
              _analyticsSummary!['conversions'].toString(),
              Icons.trending_up,
              Colors.orange,
            ),
            _buildMetricCard(
              'Errors',
              _analyticsSummary!['errors'].toString(),
              Icons.error_outline,
              Colors.red,
            ),
          ],
        ),
        const SizedBox(height: 16),
        _buildSessionInfo(),
      ],
    );
  }

  Widget _buildMetricCard(String title, String value, IconData icon, Color color) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 32, color: color),
            const SizedBox(height: 8),
            Text(
              value,
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
            Text(
              title,
              style: const TextStyle(
                fontSize: 12,
                color: Colors.grey,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSessionInfo() {
    if (_analyticsSummary == null) return const SizedBox();

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Current Session',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                const Icon(Icons.timer, size: 16, color: Colors.grey),
                const SizedBox(width: 8),
                Text('Duration: ${_analyticsSummary!['session_duration']} minutes'),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                const Icon(Icons.fingerprint, size: 16, color: Colors.grey),
                const SizedBox(width: 8),
                Text('Session ID: ${_analyticsSummary!['session_id']?.substring(0, 8)}...'),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildABTestResults() {
    if (_abTestResults == null) return const SizedBox();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'A/B Test Results',
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 16),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Paywall Presentation Test',
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 12),
                Text('Total Participants: ${_abTestResults!['total_participants']}'),
                const SizedBox(height: 16),
                ..._buildVariantResults(),
              ],
            ),
          ),
        ),
      ],
    );
  }

  List<Widget> _buildVariantResults() {
    final results = _abTestResults!['results'] as Map<String, dynamic>;
    final widgets = <Widget>[];

    for (final entry in results.entries) {
      final variant = entry.key;
      final data = entry.value as Map<String, dynamic>;
      
      widgets.add(
        Container(
          margin: const EdgeInsets.only(bottom: 8),
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Colors.grey[50],
            borderRadius: BorderRadius.circular(8),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Variant: $variant',
                style: const TextStyle(fontWeight: FontWeight.w600),
              ),
              const SizedBox(height: 4),
              ...data.entries.map((e) => Text('${e.key}: ${e.value}')),
            ],
          ),
        ),
      );
    }

    return widgets;
  }

  Widget _buildRecentEvents() {
    if (_recentEvents == null || _recentEvents!.isEmpty) {
      return const Card(
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Text('No recent events'),
        ),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Recent Events',
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 16),
        Card(
          child: Column(
            children: [
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.grey[50],
                  borderRadius: const BorderRadius.only(
                    topLeft: Radius.circular(12),
                    topRight: Radius.circular(12),
                  ),
                ),
                child: const Row(
                  children: [
                    Expanded(flex: 2, child: Text('Event', style: TextStyle(fontWeight: FontWeight.bold))),
                    Expanded(flex: 1, child: Text('Type', style: TextStyle(fontWeight: FontWeight.bold))),
                    Expanded(flex: 2, child: Text('Time', style: TextStyle(fontWeight: FontWeight.bold))),
                  ],
                ),
              ),
              ListView.separated(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: _recentEvents!.take(10).length,
                separatorBuilder: (context, index) => const Divider(height: 1),
                itemBuilder: (context, index) {
                  final event = _recentEvents![index];
                  return ListTile(
                    dense: true,
                    title: Row(
                      children: [
                        Expanded(flex: 2, child: Text(event.name, style: const TextStyle(fontSize: 12))),
                        Expanded(flex: 1, child: _buildEventTypeChip(event.type)),
                        Expanded(flex: 2, child: Text(_formatTime(event.timestamp), style: const TextStyle(fontSize: 12))),
                      ],
                    ),
                    subtitle: event.properties.isNotEmpty
                        ? Text(
                            event.properties.entries.take(2).map((e) => '${e.key}: ${e.value}').join(', '),
                            style: const TextStyle(fontSize: 10, color: Colors.grey),
                          )
                        : null,
                  );
                },
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildEventTypeChip(EventType type) {
    Color color;
    switch (type) {
      case EventType.conversion:
        color = Colors.green;
        break;
      case EventType.error:
        color = Colors.red;
        break;
      case EventType.user_action:
        color = Colors.blue;
        break;
      case EventType.screen_view:
        color = Colors.purple;
        break;
      case EventType.performance:
        color = Colors.orange;
        break;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(
        type.name,
        style: TextStyle(
          fontSize: 10,
          color: color,
          fontWeight: FontWeight.w500,
        ),
      ),
    );
  }

  Widget _buildEventTypeBreakdown() {
    if (_recentEvents == null) return const SizedBox();

    final typeCount = <EventType, int>{};
    for (final event in _recentEvents!) {
      typeCount[event.type] = (typeCount[event.type] ?? 0) + 1;
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Event Type Breakdown',
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 16),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: typeCount.entries.map((entry) {
                final percentage = (_recentEvents!.length > 0) 
                    ? (entry.value / _recentEvents!.length * 100)
                    : 0.0;
                
                return Container(
                  margin: const EdgeInsets.only(bottom: 12),
                  child: Row(
                    children: [
                      _buildEventTypeChip(entry.key),
                      const SizedBox(width: 12),
                      Expanded(
                        child: LinearProgressIndicator(
                          value: percentage / 100,
                          backgroundColor: Colors.grey[200],
                          valueColor: AlwaysStoppedAnimation(_getTypeColor(entry.key)),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Text('${entry.value} (${percentage.toStringAsFixed(1)}%)'),
                    ],
                  ),
                );
              }).toList(),
            ),
          ),
        ),
      ],
    );
  }

  Color _getTypeColor(EventType type) {
    switch (type) {
      case EventType.conversion:
        return Colors.green;
      case EventType.error:
        return Colors.red;
      case EventType.user_action:
        return Colors.blue;
      case EventType.screen_view:
        return Colors.purple;
      case EventType.performance:
        return Colors.orange;
    }
  }

  String _formatTime(DateTime time) {
    final now = DateTime.now();
    final difference = now.difference(time);
    
    if (difference.inDays > 0) {
      return '${difference.inDays}d ago';
    } else if (difference.inHours > 0) {
      return '${difference.inHours}h ago';
    } else if (difference.inMinutes > 0) {
      return '${difference.inMinutes}m ago';
    } else {
      return 'Just now';
    }
  }
}