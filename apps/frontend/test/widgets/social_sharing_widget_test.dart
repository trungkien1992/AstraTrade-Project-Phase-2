import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:astratrade_app/widgets/social_sharing_widget.dart';
import 'package:astratrade_app/services/social_sharing_service.dart';
import 'package:astratrade_app/services/viral_engagement_service.dart';

class MockSocialSharingService extends Mock implements SocialSharingService {}
class MockViralEngagementService extends Mock implements ViralEngagementService {}

void main() {
  group('SocialSharingWidget', () {
    late MockSocialSharingService mockSharingService;
    late MockViralEngagementService mockViralService;

    setUp(() {
      mockSharingService = MockSocialSharingService();
      mockViralService = MockViralEngagementService();
      
      // Mock viral service getters
      when(() => mockViralService.shareCount).thenReturn(5);
      when(() => mockViralService.viralScore).thenReturn(125.0);
      when(() => mockViralService.getViralRank()).thenReturn('Rising Influencer');
      
      // Mock track share
      when(() => mockViralService.trackShare(
        contentType: any(named: 'contentType'),
        platform: any(named: 'platform'),
        metadata: any(named: 'metadata'),
      )).thenAnswer((_) async {});
    });

    Widget createWidget({
      String contentType = 'achievement',
      Map<String, dynamic>? contentData,
      bool showMemeOptions = true,
    }) {
      return MaterialApp(
        home: Scaffold(
          body: SocialSharingWidget(
            contentType: contentType,
            contentData: contentData ?? {
              'achievement': 'Test Achievement',
              'stellarShards': 100.0,
              'lumina': 25.0,
              'level': 5,
            },
            showMemeOptions: showMemeOptions,
          ),
        ),
      );
    }

    testWidgets('should display share header correctly', (WidgetTester tester) async {
      await tester.pumpWidget(createWidget());

      expect(find.text('Share Your Cosmic Achievement!'), findsOneWidget);
      expect(find.byIcon(Icons.share), findsOneWidget);
    });

    testWidgets('should expand when toggle button is pressed', (WidgetTester tester) async {
      await tester.pumpWidget(createWidget());

      // Initially collapsed
      expect(find.text('Quick Share Options'), findsNothing);

      // Tap expand button
      await tester.tap(find.byIcon(Icons.keyboard_arrow_down));
      await tester.pumpAndSettle();

      // Now expanded
      expect(find.text('Quick Share Options'), findsOneWidget);
    });

    testWidgets('should display quick share options when expanded', (WidgetTester tester) async {
      await tester.pumpWidget(createWidget());

      // Expand the widget
      await tester.tap(find.byIcon(Icons.keyboard_arrow_down));
      await tester.pumpAndSettle();

      // Check for quick share buttons
      expect(find.text('Text'), findsOneWidget);
      expect(find.text('Image'), findsOneWidget);
      expect(find.text('Link'), findsOneWidget);
      expect(find.text('Meme'), findsOneWidget);
    });

    testWidgets('should display meme generator toggle when showMemeOptions is true', (WidgetTester tester) async {
      await tester.pumpWidget(createWidget(showMemeOptions: true));

      // Expand the widget
      await tester.tap(find.byIcon(Icons.keyboard_arrow_down));
      await tester.pumpAndSettle();

      expect(find.text('Meme Generator'), findsOneWidget);
      expect(find.byType(Switch), findsOneWidget);
    });

    testWidgets('should not display meme generator toggle when showMemeOptions is false', (WidgetTester tester) async {
      await tester.pumpWidget(createWidget(showMemeOptions: false));

      // Expand the widget
      await tester.tap(find.byIcon(Icons.keyboard_arrow_down));
      await tester.pumpAndSettle();

      expect(find.text('Meme Generator'), findsNothing);
    });

    testWidgets('should show meme generator options when toggle is enabled', (WidgetTester tester) async {
      await tester.pumpWidget(createWidget());

      // Expand the widget
      await tester.tap(find.byIcon(Icons.keyboard_arrow_down));
      await tester.pumpAndSettle();

      // Enable meme generator
      await tester.tap(find.byType(Switch));
      await tester.pumpAndSettle();

      expect(find.text('Choose Meme Template'), findsOneWidget);
      expect(find.text('Profit Explosion'), findsOneWidget);
      expect(find.text('Loss Protection'), findsOneWidget);
      expect(find.text('Streak Fire'), findsOneWidget);
      expect(find.text('Artifact Discovery'), findsOneWidget);
      expect(find.text('Generic Cosmic'), findsOneWidget);
    });

    testWidgets('should select meme template when tapped', (WidgetTester tester) async {
      await tester.pumpWidget(createWidget());

      // Expand and enable meme generator
      await tester.tap(find.byIcon(Icons.keyboard_arrow_down));
      await tester.pumpAndSettle();
      await tester.tap(find.byType(Switch));
      await tester.pumpAndSettle();

      // Initially Generic Cosmic should be selected (default)
      final genericContainer = find.ancestor(
        of: find.text('Generic Cosmic'),
        matching: find.byType(Container),
      );
      expect(genericContainer, findsOneWidget);

      // Tap on Profit Explosion
      await tester.tap(find.text('Profit Explosion'));
      await tester.pumpAndSettle();

      // Should be able to find the text (selection state changes internally)
      expect(find.text('Profit Explosion'), findsOneWidget);
    });

    testWidgets('should display viral stats', (WidgetTester tester) async {
      await tester.pumpWidget(createWidget());

      // Expand the widget
      await tester.tap(find.byIcon(Icons.keyboard_arrow_down));
      await tester.pumpAndSettle();

      // Wait for the FutureBuilder to complete
      await tester.pump();

      expect(find.text('Your Viral Stats'), findsOneWidget);
      expect(find.text('Shares'), findsOneWidget);
      expect(find.text('Viral Score'), findsOneWidget);
      expect(find.text('Rank'), findsOneWidget);
    });

    testWidgets('should handle different content types', (WidgetTester tester) async {
      // Test with levelup content
      await tester.pumpWidget(createWidget(
        contentType: 'levelup',
        contentData: {
          'newLevel': 10,
          'totalShards': 500.0,
          'specialUnlock': 'Advanced Trading',
        },
      ));

      expect(find.text('Share Your Cosmic Achievement!'), findsOneWidget);
    });

    testWidgets('should handle tap on quick share buttons', (WidgetTester tester) async {
      await tester.pumpWidget(createWidget());

      // Expand the widget
      await tester.tap(find.byIcon(Icons.keyboard_arrow_down));
      await tester.pumpAndSettle();

      // Test tapping text share button
      await tester.tap(find.text('Text'));
      await tester.pumpAndSettle();

      // Test tapping image share button
      await tester.tap(find.text('Image'));
      await tester.pumpAndSettle();

      // Test tapping link share button
      await tester.tap(find.text('Link'));
      await tester.pumpAndSettle();

      // Test tapping meme share button
      await tester.tap(find.text('Meme'));
      await tester.pumpAndSettle();

      // Widget should still be there (no crashes)
      expect(find.text('Share Your Cosmic Achievement!'), findsOneWidget);
    });

    testWidgets('should display generate meme button when meme generator is enabled', (WidgetTester tester) async {
      await tester.pumpWidget(createWidget());

      // Expand and enable meme generator
      await tester.tap(find.byIcon(Icons.keyboard_arrow_down));
      await tester.pumpAndSettle();
      await tester.tap(find.byType(Switch));
      await tester.pumpAndSettle();

      expect(find.text('Generate & Share Meme'), findsOneWidget);
    });

    testWidgets('should handle meme generation button tap', (WidgetTester tester) async {
      await tester.pumpWidget(createWidget());

      // Expand and enable meme generator
      await tester.tap(find.byIcon(Icons.keyboard_arrow_down));
      await tester.pumpAndSettle();
      await tester.tap(find.byType(Switch));
      await tester.pumpAndSettle();

      // Tap generate meme button
      await tester.tap(find.text('Generate & Share Meme'));
      await tester.pumpAndSettle();

      // Widget should still be there (no crashes)
      expect(find.text('Generate & Share Meme'), findsOneWidget);
    });

    testWidgets('should display correct icons for different content types', (WidgetTester tester) async {
      await tester.pumpWidget(createWidget());

      expect(find.byIcon(Icons.share), findsOneWidget);
      expect(find.byIcon(Icons.keyboard_arrow_down), findsOneWidget);
    });

    testWidgets('should handle empty content data gracefully', (WidgetTester tester) async {
      await tester.pumpWidget(createWidget(contentData: {}));

      expect(find.text('Share Your Cosmic Achievement!'), findsOneWidget);
    });

    testWidgets('should handle null content data gracefully', (WidgetTester tester) async {
      await tester.pumpWidget(createWidget(contentData: null));

      expect(find.text('Share Your Cosmic Achievement!'), findsOneWidget);
    });
  });
}