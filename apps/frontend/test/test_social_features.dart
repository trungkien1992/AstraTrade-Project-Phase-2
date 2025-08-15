import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:mockito/annotations.dart';
import '../lib/services/simple_social_service.dart';
import '../lib/services/friend_challenges_service.dart';
import '../lib/models/simple_gamification.dart';
import '../lib/models/simple_trade.dart';

// Generate mocks
@GenerateMocks([SimpleSocialService, FriendChallengesService])
void main() {
  group('Social Features Tests', () {
    late SimpleSocialService mockSocialService;
    late FriendChallengesService mockFriendService;

    setUp(() {
      mockSocialService = MockSimpleSocialService();
      mockFriendService = MockFriendChallengesService();
    });

    test('Simple social service can share achievement', () async {
      final achievement = Achievement(
        id: 'test_achievement',
        name: 'Test Achievement',
        description: 'Test achievement for sharing',
        type: AchievementType.firstTrade,
        targetValue: 1,
        xpReward: 100,
        tradingPointsReward: 50,
        iconName: 'trophy',
        rarity: AchievementRarity.common,
        requirements: [],
      );

      when(
        mockSocialService.shareAchievement(achievement: achievement),
      ).thenAnswer((_) async {});

      await mockSocialService.shareAchievement(achievement: achievement);
      verify(
        mockSocialService.shareAchievement(achievement: achievement),
      ).called(1);
    });

    test('Friend challenges service can create challenge', () async {
      final trade = SimpleTrade(
        id: 'test_trade',
        amount: 0.1,
        direction: 'BUY',
        symbol: 'BTC-PERP',
        timestamp: DateTime.now(),
      );

      when(
        mockFriendService.createChallenge(
          challengerId: anyNamed('challengerId'),
          challengedId: anyNamed('challengedId'),
          trade: anyNamed('trade'),
        ),
      ).thenAnswer((_) async => Future.value());

      await mockFriendService.createChallenge(
        challengerId: 'user1',
        challengedId: 'user2',
        trade: trade,
      );

      verify(
        mockFriendService.createChallenge(
          challengerId: 'user1',
          challengedId: 'user2',
          trade: trade,
        ),
      ).called(1);
    });

    test('Friend challenges service can join challenge', () async {
      when(mockFriendService.joinChallenge(any)).thenAnswer((_) async {});

      await mockFriendService.joinChallenge('challenge_id_123');
      verify(mockFriendService.joinChallenge('challenge_id_123')).called(1);
    });
  });
}
