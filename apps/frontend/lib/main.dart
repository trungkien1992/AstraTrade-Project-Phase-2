import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'screens/trade_entry_screen.dart';
import 'screens/trade_result_screen.dart';
import 'screens/streak_tracker_screen.dart';
import 'screens/analytics_dashboard_screen.dart';
import 'models/simple_trade.dart';
import 'services/subscription_service.dart';
import 'services/analytics_service.dart';
import 'services/performance_monitoring_service.dart';
import 'services/health_monitoring_service.dart';
import 'config/app_config.dart';
import 'widgets/onboarding_gate.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize core services
  await SubscriptionService.initialize();
  await AnalyticsService.initialize();
  
  // Initialize monitoring services (only in production/staging)
  if (AppConfig.enablePerformanceMonitoring) {
    await PerformanceMonitoringService.initialize();
    await HealthMonitoringService.initialize();
  }
  
  runApp(
    const ProviderScope(
      child: AstraTradeApp(),
    ),
  );
}

class AstraTradeApp extends StatelessWidget {
  const AstraTradeApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AstraTrade - Cosmic DeFi Trading',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        useMaterial3: true,
        appBarTheme: AppBarTheme(
          backgroundColor: Colors.blue[600],
          foregroundColor: Colors.white,
          elevation: 0,
        ),
      ),
      home: const OnboardingGate(),
      routes: {
        '/trade-entry': (context) => const TradeEntryScreen(),
        '/streak-tracker': (context) => const StreakTrackerScreen(),
        '/analytics': (context) => const AnalyticsDashboardScreen(),
      },
      onGenerateRoute: (settings) {
        if (settings.name == '/trade-result') {
          final trade = settings.arguments as SimpleTrade;
          return MaterialPageRoute(
            builder: (context) => TradeResultScreen(trade: trade),
          );
        }
        return null;
      },
      debugShowCheckedModeBanner: false,
    );
  }
}


