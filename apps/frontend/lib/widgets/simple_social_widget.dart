import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/simple_social_service.dart';
import '../services/friend_challenges_service.dart';
import '../services/mobile_haptic_service.dart';
import '../providers/simple_gamification_provider.dart';
import '../models/simple_gamification.dart';

/// Simple social widget for sharing achievements and creating challenges
/// Integrates with simple gamification system (non-cosmic theme)
class SimpleSocialWidget extends StatefulWidget {
  final bool showChallenges;
  final VoidCallback? onChallengeCreated;

  const SimpleSocialWidget({
    super.key,
    this.showChallenges = true,
    this.onChallengeCreated,
  });

  @override
  State<SimpleSocialWidget> createState() => _SimpleSocialWidgetState();
}

class _SimpleSocialWidgetState extends State<SimpleSocialWidget>
    with TickerProviderStateMixin {
  final _socialService = SimpleSocialService();
  final _challengesService = FriendChallengesService();
  final _hapticService = MobileHapticService();

  late TabController _tabController;
  bool _isLoading = false;
  List<FriendChallenge> _activeChallenges = [];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _initializeServices();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _initializeServices() async {
    await _challengesService.initialize();
    await _loadChallenges();
  }

  Future<void> _loadChallenges() async {
    setState(() => _isLoading = true);
    try {
      final challenges = await _challengesService.getActiveChallenges();
      setState(() {
        _activeChallenges = challenges;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 6,
      margin: const EdgeInsets.all(16),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16),
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [Colors.blue[50]!, Colors.green[50]!],
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildHeader(),
            const SizedBox(height: 16),
            _buildTabBar(),
            const SizedBox(height: 16),
            SizedBox(
              height: 300,
              child: TabBarView(
                controller: _tabController,
                children: [
                  _buildSharingTab(),
                  _buildChallengesTab(),
                  _buildLeaderboardTab(),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: Colors.blue[100],
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(Icons.share, color: Colors.blue[700], size: 24),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Social Features',
                style: Theme.of(
                  context,
                ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
              ),
              Text(
                'Share achievements and challenge friends',
                style: Theme.of(
                  context,
                ).textTheme.bodyMedium?.copyWith(color: Colors.grey[600]),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildTabBar() {
    return TabBar(
      controller: _tabController,
      tabs: const [
        Tab(icon: Icon(Icons.share), text: 'Share'),
        Tab(icon: Icon(Icons.emoji_events), text: 'Challenges'),
        Tab(icon: Icon(Icons.leaderboard), text: 'Friends'),
      ],
    );
  }

  Widget _buildSharingTab() {
    return Consumer<SimpleGamificationProvider>(
      builder: (context, gamification, child) {
        final recentAchievements = gamification.getRecentAchievements();
        final rankInfo = gamification.getRankInfo();

        return SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Share Your Progress',
                style: Theme.of(
                  context,
                ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 12),

              // Share level progress
              _buildShareButton(
                title: 'Share Level Progress',
                subtitle:
                    'Level ${rankInfo['level']} • ${rankInfo['total_xp']} XP',
                icon: Icons.trending_up,
                color: Colors.blue,
                onTap: () => _shareLevelProgress(gamification),
              ),

              // Share recent achievements
              if (recentAchievements.isNotEmpty) ...{
                const SizedBox(height: 8),
                Text(
                  'Recent Achievements',
                  style: Theme.of(
                    context,
                  ).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                ...recentAchievements
                    .take(3)
                    .map(
                      (achievement) => _buildShareButton(
                        title: 'Share "${achievement.name}"',
                        subtitle: achievement.description,
                        icon: Icons.military_tech,
                        color: Colors.amber,
                        onTap: () =>
                            _shareAchievement(achievement, gamification),
                      ),
                    ),
              },

              // Share trading stats
              const SizedBox(height: 8),
              _buildShareButton(
                title: 'Share Trading Stats',
                subtitle: 'Your performance summary',
                icon: Icons.analytics,
                color: Colors.green,
                onTap: () => _shareTradingStats(gamification),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildChallengesTab() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Friend Challenges',
              style: Theme.of(
                context,
              ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
            ),
            ElevatedButton.icon(
              onPressed: _showCreateChallengeDialog,
              icon: const Icon(Icons.add, size: 16),
              label: const Text('Create'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blue,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(
                  horizontal: 12,
                  vertical: 8,
                ),
                minimumSize: const Size(0, 32),
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),

        Expanded(
          child: _isLoading
              ? const Center(child: CircularProgressIndicator())
              : _activeChallenges.isEmpty
              ? _buildEmptyChallenges()
              : ListView.builder(
                  itemCount: _activeChallenges.length,
                  itemBuilder: (context, index) {
                    return _buildChallengeCard(_activeChallenges[index]);
                  },
                ),
        ),
      ],
    );
  }

  Widget _buildLeaderboardTab() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Friends Leaderboard',
          style: Theme.of(
            context,
          ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 12),

        Expanded(
          child: ListView.builder(
            itemCount: 5, // Sample friends
            itemBuilder: (context, index) {
              return _buildFriendLeaderboardItem(index);
            },
          ),
        ),
      ],
    );
  }

  Widget _buildShareButton({
    required String title,
    required String subtitle,
    required IconData icon,
    required Color color,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: () async {
        await _hapticService.lightTap();
        onTap();
      },
      child: Container(
        margin: const EdgeInsets.only(bottom: 8),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Colors.white.withOpacity(0.8),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: color.withOpacity(0.3)),
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                borderRadius: BorderRadius.circular(6),
              ),
              child: Icon(icon, color: color, size: 20),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: const TextStyle(
                      fontWeight: FontWeight.w500,
                      fontSize: 14,
                    ),
                  ),
                  Text(
                    subtitle,
                    style: TextStyle(color: Colors.grey[600], fontSize: 12),
                  ),
                ],
              ),
            ),
            Icon(Icons.share, color: Colors.grey[400], size: 16),
          ],
        ),
      ),
    );
  }

  Widget _buildEmptyChallenges() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.emoji_events, size: 48, color: Colors.grey[400]),
          const SizedBox(height: 8),
          Text(
            'No Active Challenges',
            style: TextStyle(color: Colors.grey[600]),
          ),
          const SizedBox(height: 4),
          Text(
            'Create a challenge to compete with friends!',
            style: TextStyle(color: Colors.grey[500], fontSize: 12),
          ),
        ],
      ),
    );
  }

  Widget _buildChallengeCard(FriendChallenge challenge) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Text(
                  challenge.title,
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
                const Spacer(),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 6,
                    vertical: 2,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.blue[100],
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Text(
                    challenge.status.name.toUpperCase(),
                    style: TextStyle(
                      color: Colors.blue[700],
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 4),
            Text(
              challenge.description,
              style: TextStyle(color: Colors.grey[600], fontSize: 12),
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Icon(Icons.person, size: 14, color: Colors.grey[500]),
                const SizedBox(width: 4),
                Text(
                  'By ${challenge.creatorName}',
                  style: TextStyle(color: Colors.grey[500], fontSize: 12),
                ),
                const Spacer(),
                ElevatedButton(
                  onPressed: () => _joinChallenge(challenge),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.green,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(
                      horizontal: 12,
                      vertical: 4,
                    ),
                    minimumSize: const Size(0, 28),
                  ),
                  child: const Text('Join', style: TextStyle(fontSize: 12)),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFriendLeaderboardItem(int index) {
    final sampleFriends = [
      {'name': 'Alex', 'level': 12, 'xp': 2400},
      {'name': 'Sarah', 'level': 10, 'xp': 1950},
      {'name': 'Mike', 'level': 8, 'xp': 1200},
      {'name': 'Emma', 'level': 7, 'xp': 980},
      {'name': 'You', 'level': 6, 'xp': 850},
    ];

    final friend = sampleFriends[index];
    final isCurrentUser = friend['name'] == 'You';

    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: isCurrentUser ? Colors.blue[50] : Colors.white.withOpacity(0.8),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: isCurrentUser ? Colors.blue[300]! : Colors.grey[300]!,
        ),
      ),
      child: Row(
        children: [
          Container(
            width: 24,
            height: 24,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: isCurrentUser ? Colors.blue : Colors.grey,
            ),
            child: Center(
              child: Text(
                '${index + 1}',
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 12,
                ),
              ),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  friend['name'] as String,
                  style: TextStyle(
                    fontWeight: isCurrentUser
                        ? FontWeight.bold
                        : FontWeight.w500,
                  ),
                ),
                Text(
                  'Level ${friend['level']} • ${friend['xp']} XP',
                  style: TextStyle(color: Colors.grey[600], fontSize: 12),
                ),
              ],
            ),
          ),
          if (!isCurrentUser)
            IconButton(
              onPressed: () => _challengeFriend(friend['name'] as String),
              icon: Icon(Icons.sports, color: Colors.blue[600], size: 20),
              padding: EdgeInsets.zero,
              constraints: const BoxConstraints(minWidth: 32, minHeight: 32),
            ),
        ],
      ),
    );
  }

  // Action methods
  Future<void> _shareLevelProgress(
    SimpleGamificationProvider gamification,
  ) async {
    final rankInfo = gamification.getRankInfo();
    await _socialService.shareLevelUp(
      newLevel: rankInfo['level'],
      totalXP: rankInfo['total_xp'],
      xpToNext: rankInfo['xp_to_next'],
    );
  }

  Future<void> _shareAchievement(
    Achievement achievement,
    SimpleGamificationProvider gamification,
  ) async {
    final rankInfo = gamification.getRankInfo();
    await _socialService.shareAchievement(
      achievement: achievement,
      currentLevel: rankInfo['level'],
      totalXP: rankInfo['total_xp'],
    );
  }

  Future<void> _shareTradingStats(
    SimpleGamificationProvider gamification,
  ) async {
    final stats = gamification.getTradingStats();
    await _socialService.shareStreak(
      streakDays: stats['streak_days'],
      successRate: stats['success_rate'],
      totalTrades: stats['total_trades'],
    );
  }

  Future<void> _showCreateChallengeDialog() async {
    await _hapticService.mediumTap();

    final templates = _challengesService.getChallengeTemplates();

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Create Challenge'),
        content: SizedBox(
          width: double.maxFinite,
          child: ListView.builder(
            shrinkWrap: true,
            itemCount: templates.length,
            itemBuilder: (context, index) {
              final template = templates[index];
              return ListTile(
                leading: Text(
                  template['icon'],
                  style: const TextStyle(fontSize: 20),
                ),
                title: Text(template['title']),
                subtitle: Text(template['description']),
                onTap: () async {
                  Navigator.pop(context);
                  await _createChallenge(template);
                },
              );
            },
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
        ],
      ),
    );
  }

  Future<void> _createChallenge(Map<String, dynamic> template) async {
    final challenge = await _challengesService.createChallenge(
      type: template['type'],
      title: template['title'],
      description: template['description'],
      targetValue: template['targetValue'],
      duration: template['duration'],
    );

    await _socialService.createFriendChallenge(
      challengeType: template['title'],
      targetValue: template['targetValue'],
      duration: template['duration'],
    );

    await _loadChallenges();
    widget.onChallengeCreated?.call();
  }

  Future<void> _joinChallenge(FriendChallenge challenge) async {
    await _challengesService.joinChallenge(challenge.id);
    await _loadChallenges();
  }

  Future<void> _challengeFriend(String friendName) async {
    await _hapticService.lightTap();

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Challenge sent to $friendName!'),
        backgroundColor: Colors.green,
        duration: const Duration(seconds: 2),
      ),
    );
  }
}
