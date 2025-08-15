import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:astratrade_app/services/cosmic_animation_service.dart';
import 'package:astratrade_app/widgets/cosmic_haptic_button.dart';

void main() {
  group('Phase 1 Integration Tests', () {
    testWidgets('Cosmic Animation Service Integration', (
      WidgetTester tester,
    ) async {
      bool animationTriggered = false;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: Builder(
              builder: (context) {
                return Center(
                  child: ElevatedButton(
                    onPressed: () {
                      CosmicAnimationService().playHarvestAnimation(
                        context: context,
                        amount: 100.0,
                        position: const Offset(100, 100),
                      );
                      animationTriggered = true;
                    },
                    child: const Text('Trigger Animation'),
                  ),
                );
              },
            ),
          ),
        ),
      );

      await tester.tap(find.text('Trigger Animation'));
      await tester.pump();

      expect(animationTriggered, isTrue);
    });

    testWidgets('Cosmic Haptic Button Integration', (
      WidgetTester tester,
    ) async {
      bool buttonPressed = false;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: Center(
              child: CosmicHapticButton(
                onPressed: () {
                  buttonPressed = true;
                },
                hapticPattern: CosmicHapticPattern.medium,
                child: const Text('Haptic Button'),
              ),
            ),
          ),
        ),
      );

      await tester.tap(find.text('Haptic Button'));
      await tester.pumpAndSettle();

      expect(buttonPressed, isTrue);
    });

    testWidgets('Multiple Animation Types', (WidgetTester tester) async {
      int animationCount = 0;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: Builder(
              builder: (context) {
                return Column(
                  children: [
                    CosmicButton(
                      text: 'Level Up',
                      animationType: 'levelup',
                      onPressed: () {
                        animationCount++;
                      },
                    ),
                    CosmicButton(
                      text: 'Trade',
                      animationType: 'trade',
                      onPressed: () {
                        animationCount++;
                      },
                    ),
                    CosmicButton(
                      text: 'Harvest',
                      animationType: 'harvest',
                      onPressed: () {
                        animationCount++;
                      },
                    ),
                  ],
                );
              },
            ),
          ),
        ),
      );

      await tester.tap(find.text('Level Up'));
      await tester.pump();

      await tester.tap(find.text('Trade'));
      await tester.pump();

      await tester.tap(find.text('Harvest'));
      await tester.pump();

      expect(animationCount, equals(3));
    });

    testWidgets('Haptic Pattern Variations', (WidgetTester tester) async {
      final patterns = [
        CosmicHapticPattern.light,
        CosmicHapticPattern.medium,
        CosmicHapticPattern.heavy,
        CosmicHapticPattern.success,
        CosmicHapticPattern.error,
        CosmicHapticPattern.levelUp,
        CosmicHapticPattern.legendary,
      ];

      for (final pattern in patterns) {
        await tester.pumpWidget(
          MaterialApp(
            home: Scaffold(
              body: Center(
                child: CosmicHapticButton(
                  onPressed: () {},
                  hapticPattern: pattern,
                  child: Text('Pattern: ${pattern.name}'),
                ),
              ),
            ),
          ),
        );

        await tester.tap(find.text('Pattern: ${pattern.name}'));
        await tester.pumpAndSettle();
      }
    });
  });
}
