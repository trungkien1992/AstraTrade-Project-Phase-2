import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import '../models/leaderboard.dart';
import '../models/prestige.dart';
import '../providers/leaderboard_provider.dart';
import '../providers/auth_provider.dart';
import '../services/prestige_service.dart';
import '../widgets/pulsating_button.dart';
import '../core/haptic_feedback.dart' as core_haptic;

class LeaderboardScreen extends ConsumerStatefulWidget {
  const LeaderboardScreen({super.key});

  @override
  ConsumerState<LeaderboardScreen> createState() => _LeaderboardScreenState();
}

class _LeaderboardScreenState extends ConsumerState<LeaderboardScreen>
    with TickerProviderStateMixin {
  late TabController _tabController;
  late TabController _prestigeTabController;
  
  final PrestigeService _prestigeService = PrestigeService();
  
  List<PrestigeLeaderboardEntry> _prestigeLeaderboard = [];
  List<PrestigeLeaderboardEntry> _verificationLeaderboard = [];
  List<SpotlightCandidate> _spotlightCandidates = [];
  bool _isLoadingPrestige = false;
  String? _prestigeError;
  
  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 6, vsync: this); // Expanded to 6 tabs
    _prestigeTabController = TabController(length: 3, vsync: this);
    
    // Load initial leaderboard data
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(leaderboardProvider.notifier).loadLeaderboard(LeaderboardType.stellarShards);
      _loadPrestigeData();
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    _prestigeTabController.dispose();
    _prestigeService.dispose();
    super.dispose();
  }

  /// Load prestige data from API
  Future<void> _loadPrestigeData() async {
    setState(() {
      _isLoadingPrestige = true;
      _prestigeError = null;
    });

    try {
      final authState = ref.read(authProvider);
      final user = authState.whenData((user) => user).value;
      final token = user?.id; // Use user ID as token for now

      final results = await Future.wait([
        _prestigeService.getPrestigeLeaderboard(token: token),
        _prestigeService.getVerificationLeaderboard(token: token),
        _prestigeService.getSpotlightCandidates(token: token),
      ]);

      setState(() {
        _prestigeLeaderboard = results[0] as List<PrestigeLeaderboardEntry>;
        _verificationLeaderboard = results[1] as List<PrestigeLeaderboardEntry>;
        _spotlightCandidates = results[2] as List<SpotlightCandidate>;
        _isLoadingPrestige = false;
      });
    } catch (e) {
      setState(() {
        _prestigeError = e.toString();
        _isLoadingPrestige = false;
      });
    }
  }

  /// Vote for spotlight candidate
  Future<void> _voteForSpotlight(String candidateUserId) async {
    try {
      core_haptic.HapticFeedback.triggerHaptic(core_haptic.HapticType.selection);
      
      final authState = ref.read(authProvider);
      final user = authState.whenData((user) => user).value;
      final token = user?.id; // Use user ID as token for now

      if (token == null) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Please log in to vote')),
        );
        return;
      }

      await _prestigeService.voteForSpotlight(
        token: token,
        candidateUserId: candidateUserId,
      );

      // Refresh spotlight candidates
      final updatedCandidates = await _prestigeService.getSpotlightCandidates(token: token);
      setState(() {
        _spotlightCandidates = updatedCandidates;
      });

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Vote cast successfully! ⭐'),
          backgroundColor: Colors.green,
        ),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Failed to vote: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final leaderboardState = ref.watch(leaderboardProvider);
    
    return Scaffold(
      backgroundColor: const Color(0xFF0A0A0A),
      appBar: AppBar(
        title: Text(
          'Cosmic Leaderboards',
          style: GoogleFonts.orbitron(
            fontWeight: FontWeight.bold,
            letterSpacing: 1.5,
            color: Colors.white,
          ),
        ),
        backgroundColor: Colors.transparent,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => ref.read(leaderboardProvider.notifier).refresh(),
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          onTap: _onTabChanged,
          isScrollable: true,
          tabs: const [
            Tab(text: 'Stellar Shards', icon: Icon(Icons.stars)),
            Tab(text: 'Lumina Flow', icon: Icon(Icons.auto_awesome)),
            Tab(text: 'Levels', icon: Icon(Icons.trending_up)),
            Tab(text: 'Win Streaks', icon: Icon(Icons.local_fire_department)),
            Tab(text: 'Prestige', icon: Icon(Icons.verified)),
            Tab(text: 'Spotlight', icon: Icon(Icons.star)),
          ],
          labelStyle: GoogleFonts.orbitron(fontSize: 11, fontWeight: FontWeight.w600),
          unselectedLabelStyle: GoogleFonts.orbitron(fontSize: 10),
        ),
      ),
      body: Column(
        children: [
          // Current User Quick Stats
          _buildCurrentUserStats(leaderboardState),
          
          // Leaderboard Content
          Expanded(
            child: TabBarView(
              controller: _tabController,
              children: [
                _buildLeaderboardList(leaderboardState, LeaderboardType.stellarShards),
                _buildLeaderboardList(leaderboardState, LeaderboardType.lumina),
                _buildLeaderboardList(leaderboardState, LeaderboardType.level),
                _buildLeaderboardList(leaderboardState, LeaderboardType.winStreak),
                _buildPrestigeSection(),
                _buildSpotlightSection(),
              ],
            ),
          ),
        ],
      ),
    );
  }

  void _onTabChanged(int index) {
    final types = [
      LeaderboardType.stellarShards,
      LeaderboardType.lumina,
      LeaderboardType.level,
      LeaderboardType.winStreak,
    ];
    
    // Only handle standard leaderboard types (first 4 tabs)
    if (index < types.length) {
      ref.read(leaderboardProvider.notifier).switchLeaderboardType(types[index]);
    } else if (index == 4 || index == 5) {
      // Prestige or Spotlight tabs - refresh prestige data
      _loadPrestigeData();
    }
    
    core_haptic.HapticFeedback.triggerHaptic(core_haptic.HapticType.selection);
  }

  Widget _buildCurrentUserStats(LeaderboardState state) {
    final currentUser = state.currentUserEntry;
    
    if (currentUser == null) {
      return Container(
        margin: const EdgeInsets.all(16),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [Colors.purple.shade900, Colors.blue.shade900],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: Colors.cyan.shade300, width: 1),
        ),
        child: const Center(
          child: Text(
            'Loading your cosmic status...',
            style: TextStyle(color: Colors.white70),
          ),
        ),
      );
    }

    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            Colors.purple.shade900.withOpacity(0.8),
            Colors.blue.shade900.withOpacity(0.8),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: currentUser.isVerifiedLuminaWeaver 
              ? Colors.yellow.shade300 
              : Colors.cyan.shade300,
          width: 2,
        ),
        boxShadow: [
          BoxShadow(
            color: (currentUser.isVerifiedLuminaWeaver 
                ? Colors.yellow.shade300 
                : Colors.cyan.shade300).withOpacity(0.3),
            blurRadius: 8,
            spreadRadius: 1,
          ),
        ],
      ),
      child: Column(
        children: [
          Row(
            children: [
              // Planet Icon
              Container(
                width: 50,
                height: 50,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: LinearGradient(
                    colors: [Colors.blue.shade400, Colors.purple.shade400],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                ),
                child: Center(
                  child: Text(
                    currentUser.planetIcon,
                    style: const TextStyle(fontSize: 24),
                  ),
                ),
              ),
              const SizedBox(width: 16),
              
              // User Info
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Text(
                          currentUser.username,
                          style: GoogleFonts.orbitron(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),
                        if (currentUser.isVerifiedLuminaWeaver) ...[
                          const SizedBox(width: 8),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                            decoration: BoxDecoration(
                              gradient: LinearGradient(
                                colors: [Colors.yellow.shade400, Colors.orange.shade400],
                              ),
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Text(
                              'Lumina Weaver',
                              style: GoogleFonts.orbitron(
                                fontSize: 10,
                                fontWeight: FontWeight.bold,
                                color: Colors.black,
                              ),
                            ),
                          ),
                        ],
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(
                      currentUser.cosmicTier,
                      style: GoogleFonts.orbitron(
                        fontSize: 14,
                        color: Colors.cyan.shade300,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              ),
              
              // Rank
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                decoration: BoxDecoration(
                  color: Colors.black.withOpacity(0.5),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: Colors.white.withOpacity(0.3)),
                ),
                child: Column(
                  children: [
                    Text(
                      '#${currentUser.rank}',
                      style: GoogleFonts.orbitron(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                    Text(
                      'RANK',
                      style: GoogleFonts.orbitron(
                        fontSize: 10,
                        color: Colors.white70,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 16),
          
          // Stats Row
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildStatItem('SS', currentUser.stellarShards.toString(), Colors.blue),
              _buildStatItem('LM', currentUser.lumina.toString(), Colors.yellow),
              _buildStatItem('LVL', currentUser.level.toString(), Colors.green),
              _buildStatItem('XP', currentUser.totalXP.toString(), Colors.purple),
              _buildStatItem('Streak', currentUser.winStreak.toString(), Colors.orange),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStatItem(String label, String value, Color color) {
    return Column(
      children: [
        Text(
          value,
          style: GoogleFonts.orbitron(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        Text(
          label,
          style: GoogleFonts.orbitron(
            fontSize: 10,
            color: Colors.white70,
          ),
        ),
      ],
    );
  }

  Widget _buildLeaderboardList(LeaderboardState state, LeaderboardType type) {
    if (state.isLoading) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(color: Colors.cyan),
            SizedBox(height: 16),
            Text(
              'Loading cosmic rankings...',
              style: TextStyle(color: Colors.white70),
            ),
          ],
        ),
      );
    }

    if (state.error != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline, color: Colors.red, size: 48),
            const SizedBox(height: 16),
            Text(
              'Failed to load leaderboard',
              style: GoogleFonts.orbitron(color: Colors.white, fontSize: 16),
            ),
            const SizedBox(height: 8),
            Text(
              state.error!,
              style: const TextStyle(color: Colors.red, fontSize: 12),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            PulsatingButton(
              text: 'Retry',
              onPressed: () => ref.read(leaderboardProvider.notifier).refresh(),
            ),
          ],
        ),
      );
    }

    if (state.entries.isEmpty) {
      return const Center(
        child: Text(
          'No cosmic traders found',
          style: TextStyle(color: Colors.white70, fontSize: 16),
        ),
      );
    }

    // Filter entries for Lumina leaderboard (Pro Traders only)
    final filteredEntries = type == LeaderboardType.lumina
        ? state.entries.where((entry) => entry.isVerifiedLuminaWeaver).toList()
        : state.entries;

    return ListView.builder(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      itemCount: filteredEntries.length,
      itemBuilder: (context, index) {
        final entry = filteredEntries[index];
        return _buildLeaderboardEntry(entry, type, index);
      },
    );
  }

  Widget _buildLeaderboardEntry(LeaderboardEntry entry, LeaderboardType type, int listIndex) {
    final isCurrentUser = entry.isCurrentUser;
    final isTopThree = entry.rank <= 3;
    
    // Colors for top 3
    Color? rankColor;
    if (entry.rank == 1) {
      rankColor = Colors.yellow.shade400;
    } else if (entry.rank == 2) {
      rankColor = Colors.grey.shade300;
    } else if (entry.rank == 3) {
      rankColor = Colors.orange.shade400;
    }

    return Container(
      margin: const EdgeInsets.symmetric(vertical: 4),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: isCurrentUser
              ? [Colors.purple.shade800.withOpacity(0.8), Colors.blue.shade800.withOpacity(0.8)]
              : isTopThree
                  ? [Colors.yellow.shade900.withOpacity(0.3), Colors.orange.shade900.withOpacity(0.3)]
                  : [Colors.grey.shade900.withOpacity(0.3), Colors.grey.shade800.withOpacity(0.3)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: isCurrentUser
              ? Colors.cyan.shade300
              : isTopThree
                  ? rankColor ?? Colors.white.withOpacity(0.2)
                  : Colors.white.withOpacity(0.1),
          width: isCurrentUser ? 2 : 1,
        ),
      ),
      child: Row(
        children: [
          // Rank
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: isTopThree ? (rankColor ?? Colors.white.withOpacity(0.2)) : Colors.white.withOpacity(0.1),
            ),
            child: Center(
              child: Text(
                '#${entry.rank}',
                style: GoogleFonts.orbitron(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                  color: isTopThree ? Colors.black : Colors.white,
                ),
              ),
            ),
          ),
          
          const SizedBox(width: 16),
          
          // Planet Icon
          Text(
            entry.planetIcon,
            style: const TextStyle(fontSize: 24),
          ),
          
          const SizedBox(width: 12),
          
          // User Info
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text(
                      entry.username,
                      style: GoogleFonts.orbitron(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: isCurrentUser ? Colors.cyan.shade300 : Colors.white,
                      ),
                    ),
                    if (entry.isVerifiedLuminaWeaver) ...[
                      const SizedBox(width: 8),
                      Icon(
                        Icons.verified,
                        size: 16,
                        color: Colors.yellow.shade400,
                      ),
                    ],
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  'Level ${entry.level} • ${entry.cosmicTier}',
                  style: GoogleFonts.orbitron(
                    fontSize: 12,
                    color: Colors.white70,
                  ),
                ),
              ],
            ),
          ),
          
          // Primary Stat (based on leaderboard type)
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              color: Colors.black.withOpacity(0.3),
              borderRadius: BorderRadius.circular(16),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  _getPrimaryStatValue(entry, type),
                  style: GoogleFonts.orbitron(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: _getPrimaryStatColor(type),
                  ),
                ),
                Text(
                  _getPrimaryStatLabel(type),
                  style: GoogleFonts.orbitron(
                    fontSize: 10,
                    color: Colors.white70,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  String _getPrimaryStatValue(LeaderboardEntry entry, LeaderboardType type) {
    switch (type) {
      case LeaderboardType.stellarShards:
        return _formatNumber(entry.stellarShards);
      case LeaderboardType.lumina:
        return _formatNumber(entry.lumina);
      case LeaderboardType.level:
        return entry.level.toString();
      case LeaderboardType.winStreak:
        return entry.winStreak.toString();
    }
  }

  String _getPrimaryStatLabel(LeaderboardType type) {
    switch (type) {
      case LeaderboardType.stellarShards:
        return 'SS';
      case LeaderboardType.lumina:
        return 'LM';
      case LeaderboardType.level:
        return 'LVL';
      case LeaderboardType.winStreak:
        return 'STREAK';
    }
  }

  Color _getPrimaryStatColor(LeaderboardType type) {
    switch (type) {
      case LeaderboardType.stellarShards:
        return Colors.blue.shade300;
      case LeaderboardType.lumina:
        return Colors.yellow.shade300;
      case LeaderboardType.level:
        return Colors.green.shade300;
      case LeaderboardType.winStreak:
        return Colors.orange.shade300;
    }
  }

  String _formatNumber(int number) {
    if (number >= 1000000) {
      return '${(number / 1000000).toStringAsFixed(1)}M';
    } else if (number >= 1000) {
      return '${(number / 1000).toStringAsFixed(1)}K';
    } else {
      return number.toString();
    }
  }

  /// Build prestige section with dual leaderboards
  Widget _buildPrestigeSection() {
    return Column(
      children: [
        // Prestige Sub-tabs
        Container(
          decoration: BoxDecoration(
            color: Colors.black.withOpacity(0.3),
            border: Border(
              bottom: BorderSide(color: Colors.white.withOpacity(0.1)),
            ),
          ),
          child: TabBar(
            controller: _prestigeTabController,
            tabs: const [
              Tab(text: 'Influence', icon: Icon(Icons.trending_up, size: 16)),
              Tab(text: 'Verified', icon: Icon(Icons.verified, size: 16)),
              Tab(text: 'Stats', icon: Icon(Icons.analytics, size: 16)),
            ],
            labelStyle: GoogleFonts.orbitron(fontSize: 10, fontWeight: FontWeight.w600),
            unselectedLabelStyle: GoogleFonts.orbitron(fontSize: 9),
            indicatorColor: Colors.purple.shade300,
          ),
        ),
        
        // Prestige Content
        Expanded(
          child: TabBarView(
            controller: _prestigeTabController,
            children: [
              _buildPrestigeLeaderboard(),
              _buildVerificationLeaderboard(),
              _buildPrestigeStats(),
            ],
          ),
        ),
      ],
    );
  }

  /// Build prestige leaderboard (influence-based)
  Widget _buildPrestigeLeaderboard() {
    if (_isLoadingPrestige) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(color: Colors.purple),
            SizedBox(height: 16),
            Text(
              'Loading cosmic influencers...',
              style: TextStyle(color: Colors.white70),
            ),
          ],
        ),
      );
    }

    if (_prestigeError != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline, color: Colors.red, size: 48),
            const SizedBox(height: 16),
            Text(
              'Failed to load prestige data',
              style: GoogleFonts.orbitron(color: Colors.white, fontSize: 16),
            ),
            const SizedBox(height: 8),
            Text(
              _prestigeError!,
              style: const TextStyle(color: Colors.red, fontSize: 12),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            PulsatingButton(
              text: 'Retry',
              onPressed: _loadPrestigeData,
            ),
          ],
        ),
      );
    }

    if (_prestigeLeaderboard.isEmpty) {
      return const Center(
        child: Text(
          'No prestige rankings available',
          style: TextStyle(color: Colors.white70, fontSize: 16),
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      itemCount: _prestigeLeaderboard.length,
      itemBuilder: (context, index) {
        final entry = _prestigeLeaderboard[index];
        return _buildPrestigeEntry(entry, index);
      },
    );
  }

  /// Build verification leaderboard (verified users only)
  Widget _buildVerificationLeaderboard() {
    if (_isLoadingPrestige) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(color: Colors.yellow),
            SizedBox(height: 16),
            Text(
              'Loading verified elite...',
              style: TextStyle(color: Colors.white70),
            ),
          ],
        ),
      );
    }

    if (_verificationLeaderboard.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.verified, color: Colors.yellow.shade300, size: 64),
            const SizedBox(height: 16),
            Text(
              'Elite Verified Traders',
              style: GoogleFonts.orbitron(
                color: Colors.white,
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              'Only the most prestigious cosmic traders earn verification',
              style: TextStyle(color: Colors.white70, fontSize: 14),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      itemCount: _verificationLeaderboard.length,
      itemBuilder: (context, index) {
        final entry = _verificationLeaderboard[index];
        return _buildVerifiedEntry(entry, index);
      },
    );
  }

  /// Build prestige statistics
  Widget _buildPrestigeStats() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Prestige System Overview',
            style: GoogleFonts.orbitron(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 20),
          
          _buildStatCard(
            'Total Verified Users',
            '${_verificationLeaderboard.length}',
            Icons.verified,
            Colors.yellow.shade300,
          ),
          
          const SizedBox(height: 12),
          
          _buildStatCard(
            'Active Influencers',
            '${_prestigeLeaderboard.where((e) => e.prestige.influenceScore > 100).length}',
            Icons.trending_up,
            Colors.purple.shade300,
          ),
          
          const SizedBox(height: 12),
          
          _buildStatCard(
            'Spotlight Candidates',
            '${_spotlightCandidates.length}',
            Icons.star,
            Colors.orange.shade300,
          ),
          
          const SizedBox(height: 24),
          
          Text(
            'Verification Tiers',
            style: GoogleFonts.orbitron(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          
          const SizedBox(height: 12),
          
          _buildVerificationTierInfo(),
        ],
      ),
    );
  }

  /// Build spotlight section
  Widget _buildSpotlightSection() {
    if (_isLoadingPrestige) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(color: Colors.orange),
            SizedBox(height: 16),
            Text(
              'Loading spotlight candidates...',
              style: TextStyle(color: Colors.white70),
            ),
          ],
        ),
      );
    }

    if (_spotlightCandidates.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.star, color: Colors.orange.shade300, size: 64),
            const SizedBox(height: 16),
            Text(
              'Cosmic Spotlight',
              style: GoogleFonts.orbitron(
                color: Colors.white,
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              'Vote for outstanding achievements to feature them in the spotlight',
              style: TextStyle(color: Colors.white70, fontSize: 14),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      itemCount: _spotlightCandidates.length,
      itemBuilder: (context, index) {
        final candidate = _spotlightCandidates[index];
        return _buildSpotlightCandidate(candidate);
      },
    );
  }

  /// Build prestige leaderboard entry
  Widget _buildPrestigeEntry(PrestigeLeaderboardEntry entry, int listIndex) {
    final isCurrentUser = entry.isCurrentUser;
    final isTopThree = entry.rank <= 3;
    
    Color? rankColor;
    if (entry.rank == 1) {
      rankColor = Colors.purple.shade300;
    } else if (entry.rank == 2) {
      rankColor = Colors.blue.shade300;
    } else if (entry.rank == 3) {
      rankColor = Colors.green.shade300;
    }

    return Container(
      margin: const EdgeInsets.symmetric(vertical: 4),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: isCurrentUser
              ? [Colors.purple.shade800.withOpacity(0.8), Colors.blue.shade800.withOpacity(0.8)]
              : isTopThree
                  ? [Colors.purple.shade900.withOpacity(0.4), Colors.blue.shade900.withOpacity(0.4)]
                  : [Colors.grey.shade900.withOpacity(0.3), Colors.grey.shade800.withOpacity(0.3)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: isCurrentUser
              ? Colors.purple.shade300
              : entry.isVerified
                  ? Colors.yellow.shade300
                  : Colors.white.withOpacity(0.1),
          width: entry.isVerified ? 2 : 1,
        ),
      ),
      child: Row(
        children: [
          // Rank
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: isTopThree ? (rankColor ?? Colors.white.withOpacity(0.2)) : Colors.white.withOpacity(0.1),
            ),
            child: Center(
              child: Text(
                '#${entry.rank}',
                style: GoogleFonts.orbitron(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                  color: isTopThree ? Colors.black : Colors.white,
                ),
              ),
            ),
          ),
          
          const SizedBox(width: 16),
          
          // Planet Icon with Aura
          Container(
            padding: const EdgeInsets.all(2),
            decoration: entry.isVerified
                ? BoxDecoration(
                    shape: BoxShape.circle,
                    border: Border.all(
                      color: Color(int.parse('0xFF${entry.auraColor.substring(1)}')),
                      width: 2,
                    ),
                  )
                : null,
            child: Text(
              entry.planetIcon,
              style: const TextStyle(fontSize: 24),
            ),
          ),
          
          const SizedBox(width: 12),
          
          // User Info
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text(
                      entry.customTitle ?? entry.username,
                      style: GoogleFonts.orbitron(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: isCurrentUser ? Colors.purple.shade300 : Colors.white,
                      ),
                    ),
                    if (entry.isVerified) ...[
                      const SizedBox(width: 8),
                      Icon(
                        Icons.verified,
                        size: 16,
                        color: Color(int.parse('0xFF${entry.prestige.verificationTierColor.substring(1)}')),
                      ),
                    ],
                  ],
                ),
                if (entry.customTitle != null) ...[
                  const SizedBox(height: 2),
                  Text(
                    entry.username,
                    style: GoogleFonts.orbitron(
                      fontSize: 12,
                      color: Colors.white60,
                    ),
                  ),
                ],
                const SizedBox(height: 4),
                Row(
                  children: [
                    Text(
                      'Level ${entry.level} • ${entry.prestige.influenceLevel}',
                      style: GoogleFonts.orbitron(
                        fontSize: 12,
                        color: Colors.white70,
                      ),
                    ),
                    if (entry.badgeCount > 0) ...[
                      const SizedBox(width: 8),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: Colors.orange.shade300,
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Text(
                          '${entry.badgeCount} 🏆',
                          style: GoogleFonts.orbitron(
                            fontSize: 10,
                            fontWeight: FontWeight.bold,
                            color: Colors.black,
                          ),
                        ),
                      ),
                    ],
                  ],
                ),
              ],
            ),
          ),
          
          // Influence Score
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              color: Colors.black.withOpacity(0.3),
              borderRadius: BorderRadius.circular(16),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  entry.primaryDisplayValue,
                  style: GoogleFonts.orbitron(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.purple.shade300,
                  ),
                ),
                Text(
                  'INFLUENCE',
                  style: GoogleFonts.orbitron(
                    fontSize: 10,
                    color: Colors.white70,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// Build verified leaderboard entry
  Widget _buildVerifiedEntry(PrestigeLeaderboardEntry entry, int listIndex) {
    return Container(
      margin: const EdgeInsets.symmetric(vertical: 4),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            Color(int.parse('0xFF${entry.prestige.verificationTierColor.substring(1)}')).withOpacity(0.2),
            Colors.black.withOpacity(0.8),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: Color(int.parse('0xFF${entry.prestige.verificationTierColor.substring(1)}')),
          width: 2,
        ),
      ),
      child: Row(
        children: [
          // Verification Badge
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: Color(int.parse('0xFF${entry.prestige.verificationTierColor.substring(1)}')),
            ),
            child: Center(
              child: Icon(
                Icons.verified,
                color: Colors.black,
                size: 20,
              ),
            ),
          ),
          
          const SizedBox(width: 16),
          
          // User Info
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  entry.customTitle ?? entry.username,
                  style: GoogleFonts.orbitron(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                if (entry.customTitle != null) ...[
                  const SizedBox(height: 2),
                  Text(
                    entry.username,
                    style: GoogleFonts.orbitron(
                      fontSize: 12,
                      color: Colors.white60,
                    ),
                  ),
                ],
                const SizedBox(height: 4),
                Text(
                  '${entry.verificationTierName} Tier • Level ${entry.level}',
                  style: GoogleFonts.orbitron(
                    fontSize: 12,
                    color: Colors.white70,
                  ),
                ),
              ],
            ),
          ),
          
          // Spotlight Count
          if (entry.prestige.spotlightCount > 0)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              decoration: BoxDecoration(
                color: Colors.orange.shade300,
                borderRadius: BorderRadius.circular(16),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Icon(Icons.star, size: 16, color: Colors.black),
                  const SizedBox(width: 4),
                  Text(
                    '${entry.prestige.spotlightCount}',
                    style: GoogleFonts.orbitron(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                      color: Colors.black,
                    ),
                  ),
                ],
              ),
            ),
        ],
      ),
    );
  }

  /// Build spotlight candidate card
  Widget _buildSpotlightCandidate(SpotlightCandidate candidate) {
    return Container(
      margin: const EdgeInsets.symmetric(vertical: 8),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: candidate.isCurrentlySpotlighted
              ? [Colors.orange.shade800.withOpacity(0.8), Colors.red.shade800.withOpacity(0.8)]
              : [Colors.grey.shade900.withOpacity(0.8), Colors.grey.shade800.withOpacity(0.8)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: candidate.isCurrentlySpotlighted
              ? Colors.orange.shade300
              : Colors.white.withOpacity(0.2),
          width: candidate.isCurrentlySpotlighted ? 3 : 1,
        ),
      ),
      child: Column(
        children: [
          // Header
          Container(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                // Avatar with verification
                Container(
                  padding: const EdgeInsets.all(2),
                  decoration: candidate.prestige.isVerified
                      ? BoxDecoration(
                          shape: BoxShape.circle,
                          border: Border.all(
                            color: Color(int.parse('0xFF${candidate.prestige.auraColor.substring(1)}')),
                            width: 2,
                          ),
                        )
                      : null,
                  child: Text(
                    candidate.planetIcon,
                    style: const TextStyle(fontSize: 32),
                  ),
                ),
                
                const SizedBox(width: 16),
                
                // User info
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Text(
                            candidate.username,
                            style: GoogleFonts.orbitron(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                            ),
                          ),
                          if (candidate.prestige.isVerified) ...[
                            const SizedBox(width: 8),
                            Icon(
                              Icons.verified,
                              size: 18,
                              color: Color(int.parse('0xFF${candidate.prestige.verificationTierColor.substring(1)}')),
                            ),
                          ],
                          if (candidate.isCurrentlySpotlighted) ...[
                            const SizedBox(width: 8),
                            Icon(
                              Icons.star,
                              size: 18,
                              color: Colors.orange.shade300,
                            ),
                          ],
                        ],
                      ),
                      const SizedBox(height: 4),
                      Text(
                        candidate.prestige.influenceLevel,
                        style: GoogleFonts.orbitron(
                          fontSize: 12,
                          color: Colors.white70,
                        ),
                      ),
                    ],
                  ),
                ),
                
                // Vote count
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  decoration: BoxDecoration(
                    color: Colors.orange.shade300,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.star, size: 16, color: Colors.black),
                      const SizedBox(width: 4),
                      Text(
                        '${candidate.spotlightVotes}',
                        style: GoogleFonts.orbitron(
                          fontSize: 14,
                          fontWeight: FontWeight.bold,
                          color: Colors.black,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          
          // Achievement
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.black.withOpacity(0.3),
              borderRadius: const BorderRadius.only(
                bottomLeft: Radius.circular(16),
                bottomRight: Radius.circular(16),
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  candidate.achievementTitle,
                  style: GoogleFonts.orbitron(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.orange.shade300,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  candidate.achievementDescription,
                  style: const TextStyle(
                    fontSize: 14,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 12),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      candidate.timeSinceAchievement,
                      style: GoogleFonts.orbitron(
                        fontSize: 12,
                        color: Colors.white60,
                      ),
                    ),
                    if (candidate.canReceiveVotes)
                      PulsatingButton(
                        text: 'Vote ⭐',
                        onPressed: () => _voteForSpotlight(candidate.userId),
                        color: Colors.orange.shade300,
                      ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// Build stat card for prestige stats
  Widget _buildStatCard(String title, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [color.withOpacity(0.2), Colors.black.withOpacity(0.8)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.5)),
      ),
      child: Row(
        children: [
          Icon(icon, color: color, size: 32),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  value,
                  style: GoogleFonts.orbitron(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                Text(
                  title,
                  style: GoogleFonts.orbitron(
                    fontSize: 12,
                    color: Colors.white70,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// Build verification tier information
  Widget _buildVerificationTierInfo() {
    final tiers = [
      {'name': 'Bronze', 'color': '#CD7F32', 'desc': 'Active community member'},
      {'name': 'Silver', 'color': '#C0C0C0', 'desc': 'Consistent high performer'},
      {'name': 'Gold', 'color': '#FFD700', 'desc': 'Elite cosmic trader'},
    ];

    return Column(
      children: tiers.map((tier) {
        return Container(
          margin: const EdgeInsets.symmetric(vertical: 4),
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Color(int.parse('0xFF${tier['color']!.substring(1)}')).withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
            border: Border.all(
              color: Color(int.parse('0xFF${tier['color']!.substring(1)}')).withOpacity(0.3),
            ),
          ),
          child: Row(
            children: [
              Icon(
                Icons.verified,
                color: Color(int.parse('0xFF${tier['color']!.substring(1)}')),
                size: 20,
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '${tier['name']} Tier',
                      style: GoogleFonts.orbitron(
                        fontSize: 14,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                    Text(
                      tier['desc']!,
                      style: const TextStyle(
                        fontSize: 12,
                        color: Colors.white70,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        );
      }).toList(),
    );
  }
}