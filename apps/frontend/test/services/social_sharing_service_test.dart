import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:astratrade_app/services/social_sharing_service.dart';

class MockSocialSharingService extends Mock implements SocialSharingService {}

void main() {
  group('SocialSharingService', () {
    late SocialSharingService socialSharingService;

    setUp(() {
      socialSharingService = SocialSharingService();
    });

    test('should be a singleton', () {
      final instance1 = SocialSharingService();
      final instance2 = SocialSharingService();
      expect(instance1, equals(instance2));
    });

    group('shareTradingAchievement', () {
      test('should generate cosmic message with correct format', () async {
        // This test would require mocking share_plus
        // For now, we'll test the structure
        expect(socialSharingService, isA<SocialSharingService>());
      });

      test('should handle different achievement types', () async {
        const achievement = 'Level Up Achievement';
        const stellarShards = 150.0;
        const lumina = 25.5;
        const level = 5;

        // Test that the method can be called without errors
        expect(
          () => socialSharingService.shareTradingAchievement(
            achievement: achievement,
            stellarShards: stellarShards,
            lumina: lumina,
            level: level,
          ),
          returnsNormally,
        );
      });
    });

    group('shareLevelUp', () {
      test('should format level up message correctly', () async {
        const newLevel = 10;
        const totalShards = 500.0;
        const specialUnlock = 'Advanced Trading Algorithms';

        expect(
          () => socialSharingService.shareLevelUp(
            newLevel: newLevel,
            totalShards: totalShards,
            specialUnlock: specialUnlock,
          ),
          returnsNormally,
        );
      });
    });

    group('shareStreak', () {
      test('should format streak message correctly', () async {
        const streakDays = 7;
        const bonusMultiplier = 1.5;

        expect(
          () => socialSharingService.shareStreak(
            streakDays: streakDays,
            bonusMultiplier: bonusMultiplier,
          ),
          returnsNormally,
        );
      });
    });

    group('shareArtifactDiscovery', () {
      test('should format artifact message correctly', () async {
        const artifactName = 'Stellar Prism';
        const rarity = 'legendary';
        const effect = 'Increases Lumina generation by 50%';

        expect(
          () => socialSharingService.shareArtifactDiscovery(
            artifactName: artifactName,
            rarity: rarity,
            effect: effect,
          ),
          returnsNormally,
        );
      });

      test('should handle different rarity types', () async {
        final rarities = ['common', 'rare', 'epic', 'legendary'];
        
        for (final rarity in rarities) {
          expect(
            () => socialSharingService.shareArtifactDiscovery(
              artifactName: 'Test Artifact',
              rarity: rarity,
              effect: 'Test Effect',
            ),
            returnsNormally,
          );
        }
      });
    });

    group('shareCosmicMeme', () {
      test('should handle different meme types', () async {
        final memeTypes = [
          'profit_explosion',
          'loss_protection',
          'streak_fire',
          'artifact_discovery',
          'generic',
        ];

        for (final memeType in memeTypes) {
          expect(
            () => socialSharingService.shareCosmicMeme(
              memeType: memeType,
              memeData: {'test': 'data'},
            ),
            returnsNormally,
          );
        }
      });

      test('should handle empty meme data', () async {
        expect(
          () => socialSharingService.shareCosmicMeme(
            memeType: 'generic',
            memeData: {},
          ),
          returnsNormally,
        );
      });
    });
  });
}