import 'dart:async';
import 'dart:math' as math;
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import '../models/simple_gamification.dart';
import '../models/simple_trade.dart';
import '../api/astratrade_backend_client.dart';
import '../services/mobile_haptic_service.dart';
import '../services/mobile_notification_service.dart';

/// Challenge types for friend competitions
enum ChallengeType {
  dailyTrades,     // Complete X trades in a day
  weeklyProfit,    // Achieve X% profit in a week
  streakChallenge, // Maintain X day streak
  xpRace,          // First to reach X XP
  accuracyTest,    // Achieve X% success rate
}

/// Friend challenge data model
class FriendChallenge {
  final String id;
  final String creatorId;
  final String creatorName;
  final ChallengeType type;
  final String title;
  final String description;
  final int targetValue;
  final DateTime startTime;
  final DateTime endTime;
  final List<ChallengeParticipant> participants;
  final ChallengeStatus status;
  final String? winnerId;
  final DateTime createdAt;

  const FriendChallenge({
    required this.id,
    required this.creatorId,
    required this.creatorName,
    required this.type,
    required this.title,
    required this.description,
    required this.targetValue,
    required this.startTime,
    required this.endTime,
    required this.participants,
    required this.status,
    this.winnerId,
    required this.createdAt,
  });
}

/// Challenge participant data
class ChallengeParticipant {
  final String userId;
  final String username;
  final int currentProgress;
  final bool hasCompleted;
  final DateTime joinedAt;
  final DateTime? completedAt;

  const ChallengeParticipant({
    required this.userId,
    required this.username,
    required this.currentProgress,
    required this.hasCompleted,
    required this.joinedAt,
    this.completedAt,
  });
}

/// Challenge status
enum ChallengeStatus {
  pending,    // Waiting for participants
  active,     // Currently running
  completed,  // Finished
  cancelled,  // Cancelled by creator
}

/// Service for managing friend challenges and competitions
class FriendChallengesService {
  static final FriendChallengesService _instance = FriendChallengesService._internal();
  factory FriendChallengesService() => _instance;
  FriendChallengesService._internal();

  final _backendClient = AstraTradeBackendClient();
  final _hapticService = MobileHapticService();
  final _notificationService = MobileNotificationService();
  
  final _challengesController = StreamController<List<FriendChallenge>>.broadcast();
  Stream<List<FriendChallenge>> get challengesStream => _challengesController.stream;

  List<FriendChallenge> _activeChallenges = [];
  Timer? _updateTimer;

  /// Initialize the service
  Future<void> initialize() async {
    await _hapticService.initialize();
    await _notificationService.initialize();
    
    // Start periodic updates
    _updateTimer = Timer.periodic(const Duration(minutes: 5), (timer) {
      _refreshChallenges();
    });
    
    await _refreshChallenges();
  }

  /// Create a new friend challenge
  Future<FriendChallenge> createChallenge({
    required ChallengeType type,
    required String title,
    required String description,
    required int targetValue,
    required Duration duration,
  }) async {
    await _hapticService.mediumTap();
    
    // Generate challenge data
    final challenge = FriendChallenge(
      id: _generateChallengeId(),
      creatorId: 'current_user', // Would get from auth service
      creatorName: 'You',
      type: type,
      title: title,
      description: description,
      targetValue: targetValue,
      startTime: DateTime.now(),
      endTime: DateTime.now().add(duration),
      participants: [],
      status: ChallengeStatus.pending,
      createdAt: DateTime.now(),
    );

    // Add to local list
    _activeChallenges.add(challenge);
    _challengesController.add(List.from(_activeChallenges));

    // Show success feedback
    await _notificationService.showTradingAlert(
      title: '🎯 Challenge Created!',
      message: 'Your $title challenge is ready to share',
      color: Colors.blue,
    );

    await _hapticService.success();
    return challenge;
  }

  /// Join an existing challenge
  Future<void> joinChallenge(String challengeId) async {
    await _hapticService.lightTap();
    
    final challengeIndex = _activeChallenges.indexWhere((c) => c.id == challengeId);
    if (challengeIndex == -1) return;

    // Simulate joining (in real app, would call backend)
    await _notificationService.showTradingAlert(
      title: '⚡ Challenge Joined!',
      message: 'You are now competing in this challenge',
      color: Colors.green,
    );

    await _hapticService.success();
  }

  /// Update challenge progress based on trading activity
  Future<void> updateChallengeProgress({
    required SimpleTrade trade,
    required int currentXP,
    required int currentLevel,
    required int streakDays,
  }) async {
    for (final challenge in _activeChallenges) {
      if (challenge.status != ChallengeStatus.active) continue;

      bool progressMade = false;
      int newProgress = 0;

      switch (challenge.type) {
        case ChallengeType.dailyTrades:
          // Count trades completed today
          final today = DateTime.now();
          if (trade.timestamp.day == today.day) {
            newProgress = 1; // Would accumulate in real implementation
            progressMade = true;
          }
          break;

        case ChallengeType.weeklyProfit:
          // Track profit percentage
          if (trade.profitLoss != null && trade.profitLoss! > 0) {
            newProgress = (trade.profitLoss! * 100).round();
            progressMade = true;
          }
          break;

        case ChallengeType.streakChallenge:
          newProgress = streakDays;
          progressMade = streakDays >= challenge.targetValue;
          break;

        case ChallengeType.xpRace:
          newProgress = currentXP;
          progressMade = currentXP >= challenge.targetValue;
          break;

        case ChallengeType.accuracyTest:
          // Would calculate from trading stats
          progressMade = false;
          break;
      }

      if (progressMade) {
        await _notificationService.showTradingAlert(
          title: '🏆 Challenge Progress!',
          message: 'You made progress in "${challenge.title}"',
          color: Colors.orange,
        );
        
        await _hapticService.achievementUnlocked(rarity: AchievementRarity.common);
      }
    }
  }

  /// Get active challenges for current user
  Future<List<FriendChallenge>> getActiveChallenges() async {
    return _activeChallenges.where((c) => 
      c.status == ChallengeStatus.active || c.status == ChallengeStatus.pending
    ).toList();
  }

  /// Get completed challenges
  Future<List<FriendChallenge>> getCompletedChallenges() async {
    return _activeChallenges.where((c) => 
      c.status == ChallengeStatus.completed
    ).toList();
  }

  /// Generate challenge templates for quick creation
  List<Map<String, dynamic>> getChallengeTemplates() {
    return [
      {
        'type': ChallengeType.dailyTrades,
        'title': '5 Trades Today',
        'description': 'Complete 5 successful trades in a single day',
        'targetValue': 5,
        'duration': const Duration(days: 1),
        'icon': '📈',
      },
      {
        'type': ChallengeType.weeklyProfit,
        'title': '10% Weekly Profit',
        'description': 'Achieve 10% profit in your trading portfolio this week',
        'targetValue': 10,
        'duration': const Duration(days: 7),
        'icon': '💰',
      },
      {
        'type': ChallengeType.streakChallenge,
        'title': '7-Day Streak',
        'description': 'Maintain a 7-day trading streak',
        'targetValue': 7,
        'duration': const Duration(days: 14),
        'icon': '🔥',
      },
      {
        'type': ChallengeType.xpRace,
        'title': 'XP Race to 1000',
        'description': 'First to reach 1000 XP wins',
        'targetValue': 1000,
        'duration': const Duration(days: 30),
        'icon': '⭐',
      },
      {
        'type': ChallengeType.accuracyTest,
        'title': '80% Accuracy',
        'description': 'Achieve 80% trading accuracy over 10 trades',
        'targetValue': 80,
        'duration': const Duration(days: 7),
        'icon': '🎯',
      },
    ];
  }

  /// Refresh challenges from backend
  Future<void> _refreshChallenges() async {
    try {
      // In real implementation, would fetch from backend
      // For now, simulate some active challenges
      if (_activeChallenges.isEmpty) {
        _activeChallenges = _generateSampleChallenges();
        _challengesController.add(List.from(_activeChallenges));
      }
    } catch (e) {
      debugPrint('Error refreshing challenges: $e');
    }
  }

  /// Generate sample challenges for demo
  List<FriendChallenge> _generateSampleChallenges() {
    final random = math.Random();
    return [
      FriendChallenge(
        id: 'challenge_1',
        creatorId: 'friend_1',
        creatorName: 'Alex',
        type: ChallengeType.dailyTrades,
        title: '5 Trades Challenge',
        description: 'Complete 5 trades today',
        targetValue: 5,
        startTime: DateTime.now().subtract(const Duration(hours: 2)),
        endTime: DateTime.now().add(const Duration(hours: 22)),
        participants: [
          ChallengeParticipant(
            userId: 'friend_1',
            username: 'Alex',
            currentProgress: 3,
            hasCompleted: false,
            joinedAt: DateTime.now().subtract(const Duration(hours: 2)),
          ),
        ],
        status: ChallengeStatus.active,
        createdAt: DateTime.now().subtract(const Duration(hours: 2)),
      ),
      FriendChallenge(
        id: 'challenge_2',
        creatorId: 'friend_2',
        creatorName: 'Sarah',
        type: ChallengeType.xpRace,
        title: 'XP Race to 500',
        description: 'First to reach 500 XP',
        targetValue: 500,
        startTime: DateTime.now().subtract(const Duration(days: 1)),
        endTime: DateTime.now().add(const Duration(days: 6)),
        participants: [
          ChallengeParticipant(
            userId: 'friend_2',
            username: 'Sarah',
            currentProgress: 420,
            hasCompleted: false,
            joinedAt: DateTime.now().subtract(const Duration(days: 1)),
          ),
        ],
        status: ChallengeStatus.active,
        createdAt: DateTime.now().subtract(const Duration(days: 1)),
      ),
    ];
  }

  /// Generate unique challenge ID
  String _generateChallengeId() {
    final timestamp = DateTime.now().millisecondsSinceEpoch;
    final random = math.Random().nextInt(9999);
    return 'challenge_${timestamp}_$random';
  }

  /// Dispose of the service
  void dispose() {
    _updateTimer?.cancel();
    _challengesController.close();
  }
}