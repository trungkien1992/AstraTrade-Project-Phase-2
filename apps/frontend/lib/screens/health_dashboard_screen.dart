import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/health_monitoring_service.dart';
import '../services/performance_monitoring_service.dart';
import '../config/app_config.dart';

class HealthDashboardScreen extends ConsumerStatefulWidget {
  const HealthDashboardScreen({super.key});

  @override
  ConsumerState<HealthDashboardScreen> createState() => _HealthDashboardScreenState();
}

class _HealthDashboardScreenState extends ConsumerState<HealthDashboardScreen> {
  Map<String, HealthCheck>? _healthChecks;
  Map<String, dynamic>? _performanceSummary;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadHealthData();
  }

  Future<void> _loadHealthData() async {
    setState(() => _isLoading = true);
    
    try {
      final healthChecks = await HealthMonitoringService().performCompleteHealthCheck();
      final performanceSummary = PerformanceMonitoringService().getPerformanceSummary();
      
      setState(() {
        _healthChecks = healthChecks;
        _performanceSummary = performanceSummary;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading health data: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('System Health'),
        backgroundColor: Colors.blue[600],
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadHealthData,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _loadHealthData,
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildOverallStatus(),
                    const SizedBox(height: 24),
                    _buildHealthChecks(),
                    const SizedBox(height: 24),
                    _buildPerformanceMetrics(),
                    const SizedBox(height: 24),
                    _buildSystemInfo(),
                  ],
                ),
              ),
            ),
    );
  }

  Widget _buildOverallStatus() {
    if (_healthChecks == null) return const SizedBox();

    final overallStatus = HealthMonitoringService().getOverallHealthStatus();
    
    Color statusColor;
    IconData statusIcon;
    String statusText;
    
    switch (overallStatus) {
      case HealthStatus.healthy:
        statusColor = Colors.green;
        statusIcon = Icons.check_circle;
        statusText = 'All Systems Operational';
        break;
      case HealthStatus.warning:
        statusColor = Colors.orange;
        statusIcon = Icons.warning;
        statusText = 'Some Issues Detected';
        break;
      case HealthStatus.critical:
        statusColor = Colors.red;
        statusIcon = Icons.error;
        statusText = 'Critical Issues Found';
        break;
      case HealthStatus.unknown:
        statusColor = Colors.grey;
        statusIcon = Icons.help;
        statusText = 'Status Unknown';
        break;
    }

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Row(
          children: [
            Icon(statusIcon, size: 48, color: statusColor),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    statusText,
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: statusColor,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Last checked: ${DateTime.now().toString().substring(0, 19)}',
                    style: const TextStyle(color: Colors.grey),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'App Version: ${AppConfig.appVersion} (${AppConfig.buildNumber})',
                    style: const TextStyle(color: Colors.grey, fontSize: 12),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHealthChecks() {
    if (_healthChecks == null) return const SizedBox();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Health Checks',
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 16),
        ...(_healthChecks!.entries.map((entry) => _buildHealthCheckCard(entry.value))),
      ],
    );
  }

  Widget _buildHealthCheckCard(HealthCheck check) {
    Color statusColor;
    IconData statusIcon;
    
    switch (check.status) {
      case HealthStatus.healthy:
        statusColor = Colors.green;
        statusIcon = Icons.check_circle;
        break;
      case HealthStatus.warning:
        statusColor = Colors.orange;
        statusIcon = Icons.warning;
        break;
      case HealthStatus.critical:
        statusColor = Colors.red;
        statusIcon = Icons.error;
        break;
      case HealthStatus.unknown:
        statusColor = Colors.grey;
        statusIcon = Icons.help;
        break;
    }

    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: Icon(statusIcon, color: statusColor),
        title: Text(
          _formatCheckName(check.name),
          style: const TextStyle(fontWeight: FontWeight.w600),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(check.message),
            if (check.responseTime.inMilliseconds > 0)
              Text(
                'Response time: ${check.responseTime.inMilliseconds}ms',
                style: const TextStyle(fontSize: 12, color: Colors.grey),
              ),
          ],
        ),
        trailing: Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: statusColor.withOpacity(0.1),
            borderRadius: BorderRadius.circular(4),
          ),
          child: Text(
            check.status.name.toUpperCase(),
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.bold,
              color: statusColor,
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildPerformanceMetrics() {
    if (_performanceSummary == null) return const SizedBox();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Performance Metrics',
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
              children: [
                _buildMetricRow('App Uptime', '${_performanceSummary!['app_uptime_minutes']} minutes'),
                _buildMetricRow('Total Metrics', '${_performanceSummary!['total_metrics']}'),
                if (_performanceSummary!['appStartup_avg'] != null)
                  _buildMetricRow('Avg Startup Time', '${_performanceSummary!['appStartup_avg'].toStringAsFixed(0)}ms'),
                if (_performanceSummary!['screenLoad_avg'] != null)
                  _buildMetricRow('Avg Screen Load', '${_performanceSummary!['screenLoad_avg'].toStringAsFixed(0)}ms'),
                if (_performanceSummary!['networkRequest_avg'] != null)
                  _buildMetricRow('Avg Network Request', '${_performanceSummary!['networkRequest_avg'].toStringAsFixed(0)}ms'),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildMetricRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(fontWeight: FontWeight.w500)),
          Text(value, style: const TextStyle(color: Colors.grey)),
        ],
      ),
    );
  }

  Widget _buildSystemInfo() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'System Information',
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
              children: [
                _buildInfoRow('Environment', AppConfig.isProduction ? 'Production' : 'Development'),
                _buildInfoRow('App Version', AppConfig.appVersion),
                _buildInfoRow('Build Number', AppConfig.buildNumber),
                _buildInfoRow('Beta Version', AppConfig.isBetaVersion ? 'Yes' : 'No'),
                _buildInfoRow('Analytics Enabled', AppConfig.enableAnalytics ? 'Yes' : 'No'),
                _buildInfoRow('Performance Monitoring', AppConfig.enablePerformanceMonitoring ? 'Yes' : 'No'),
                _buildInfoRow('A/B Testing', AppConfig.enableABTesting ? 'Yes' : 'No'),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(fontWeight: FontWeight.w500)),
          Text(value, style: const TextStyle(color: Colors.grey)),
        ],
      ),
    );
  }

  String _formatCheckName(String name) {
    return name
        .split('_')
        .map((word) => word[0].toUpperCase() + word.substring(1))
        .join(' ');
  }
}