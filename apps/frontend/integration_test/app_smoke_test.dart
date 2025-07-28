import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:astratrade_app/main.dart';
import 'package:flutter/material.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('App launches and shows splash screen', (WidgetTester tester) async {
    await tester.pumpWidget(const ProviderScope(child: TradingPracticeApp()));

    // Verify splash screen elements
    expect(find.text('AstraTrade'), findsOneWidget);
    expect(find.text('Advanced Trading Platform'), findsOneWidget);
    expect(find.byType(CircularProgressIndicator), findsOneWidget);

    // Wait for splash to complete
    await tester.pump(const Duration(seconds: 4));

    // After splash, main UI should be present
    expect(find.byType(MaterialApp), findsOneWidget);
    // You can add more checks for main UI widgets here
  });
} 