import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'widgets/game_stats_bar.dart';
import 'providers/game_state_provider.dart';

/// Simple test app to verify GameStatsBar widget works
class TestGameStatsApp extends ConsumerWidget {
  const TestGameStatsApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return MaterialApp(
      title: 'GameStats Test',
      theme: ThemeData(primarySwatch: Colors.blue),
      home: const TestGameStatsScreen(),
    );
  }
}

class TestGameStatsScreen extends ConsumerWidget {
  const TestGameStatsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(title: const Text('GameStatsBar Test')),
      body: const Column(
        children: [
          SizedBox(height: 20),
          GameStatsBar(),
          SizedBox(height: 20),
          Text('GameStatsBar appears above this text'),
        ],
      ),
    );
  }
}

void main() {
  runApp(const ProviderScope(child: TestGameStatsApp()));
}
