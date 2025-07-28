// This is a basic Flutter widget test.
//
// To perform an interaction with a widget in your test, use the WidgetTester
// utility in the flutter_test package. For example, you can send tap and scroll
// gestures. You can also use WidgetTester to find child widgets in the widget
// tree, read text, and verify that the values of widget properties are correct.

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:astratrade_app/main.dart';

void main() {
  testWidgets('AstraTrade app initialization test', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const ProviderScope(child: AstraTradeApp()));

    // Verify that the app initializes without crashing
    expect(find.byType(MaterialApp), findsOneWidget);
    
    // Verify basic splash screen elements are present initially
    expect(find.text('AstraTrade'), findsOneWidget);
    expect(find.text('Advanced Trading Platform'), findsOneWidget);
    expect(find.byType(CircularProgressIndicator), findsOneWidget);
    
    // Verify app doesn't crash during initialization
    await tester.pump();
    expect(find.byType(MaterialApp), findsOneWidget);
    
    // Wait for splash timer to complete to avoid pending timer error
    await tester.pump(const Duration(seconds: 4));
  });
}
