import 'package:flutter/material.dart';
import 'dart:math' as math;
import '../models/achievement_models.dart';
import '../providers/achievement_provider.dart';
import '../widgets/achievement_progress_card.dart';
import '../widgets/achievement_category_filter.dart';
import '../services/enhanced_haptic_service.dart';

/// Achievement Gallery Screen showcasing research-driven achievement categories
/// 
/// Features:
/// - 60% Educational, 20% Risk Management, 15% Performance, 5% Social distribution
/// - Progressive skill-level filtering and recommendations
/// - League-based achievement scaling visualization  
/// - Search and category filtering
/// - Achievement sharing and social features
/// - Progress tracking with visual indicators
class AchievementsGalleryScreen extends StatefulWidget {
  const AchievementsGalleryScreen({Key? key}) : super(key: key);

  @override
  State<AchievementsGalleryScreen> createState() => _AchievementsGalleryScreenState();
}

class _AchievementsGalleryScreenState extends State<AchievementsGalleryScreen>
    with TickerProviderStateMixin {
  
  late TabController _tabController;
  late AnimationController _headerAnimationController;
  late AnimationController _statsAnimationController;
  
  String _selectedCategory = 'all';
  String _searchQuery = '';
  String _sortBy = 'category';
  bool _showCompletedOnly = false;
  bool _showRecommendedOnly = false;
  
  final TextEditingController _searchController = TextEditingController();
  final ScrollController _scrollController = ScrollController();

  @override
  void initState() {
    super.initState();
    
    _tabController = TabController(length: 5, vsync: this);
    
    _headerAnimationController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );
    
    _statsAnimationController = AnimationController(
      duration: const Duration(milliseconds: 1200),
      vsync: this,
    );
    
    _headerAnimationController.forward();
    _statsAnimationController.forward();
    
    _tabController.addListener(() {
      if (_tabController.indexIsChanging) {
        _onCategoryChanged(_tabController.index);
      }
    });
  }
  
  void _onCategoryChanged(int index) {
    final categories = ['all', 'educational', 'risk_management', 'performance', 'social'];
    setState(() {
      _selectedCategory = categories[index];
    });
    
    // Haptic feedback for tab changes
    EnhancedHapticService().playSelectionHaptic();
  }

  @override
  void dispose() {
    _tabController.dispose();
    _headerAnimationController.dispose();
    _statsAnimationController.dispose();
    _searchController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0A0F),
      body: CustomScrollView(
        controller: _scrollController,
        slivers: [
          _buildCosmicAppBar(),
          _buildStatsOverview(),
          _buildCategoryTabs(),
          _buildFiltersRow(),
          _buildAchievementsGrid(),
        ],
      ),
      floatingActionButton: _buildRecommendationsFAB(),
    );
  }
  
  Widget _buildCosmicAppBar() {
    return SliverAppBar(
      expandedHeight: 200,
      floating: false,
      pinned: true,
      backgroundColor: const Color(0xFF0A0A0F),
      flexibleSpace: FlexibleSpaceBar(
        background: AnimatedBuilder(
          animation: _headerAnimationController,
          builder: (context, child) {
            return Container(
              decoration: const BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [
                    Color(0xFF1A1A2E),
                    Color(0xFF16213E),
                    Color(0xFF0A0A0F),
                  ],
                ),
              ),
              child: Stack(
                children: [
                  // Animated stars background
                  _buildAnimatedStars(),
                  
                  // Header content
                  Positioned(
                    left: 20,
                    right: 20,
                    bottom: 30,
                    child: FadeTransition(
                      opacity: _headerAnimationController,
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'Galactic Achievements',
                            style: TextStyle(
                              fontSize: 28,
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                            ),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            'Your Journey Through the Cosmic Trading Academy',
                            style: TextStyle(
                              fontSize: 16,
                              color: Colors.white.withOpacity(0.7),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            );
          },
        ),
        title: const Text(
          'Achievements',
          style: TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
          ),
        ),
      ),
    );
  }
  
  Widget _buildAnimatedStars() {
    return AnimatedBuilder(
      animation: _headerAnimationController,
      builder: (context, child) {
        return CustomPaint(
          painter: StarFieldPainter(_headerAnimationController.value),
          size: Size.infinite,
        );
      },
    );
  }
  
  Widget _buildStatsOverview() {
    return SliverToBoxAdapter(
      child: Container(
        margin: const EdgeInsets.all(20),
        child: AnimatedBuilder(
          animation: _statsAnimationController,
          builder: (context, child) {
            return Consumer<AchievementProvider>(
              builder: (context, achievementProvider, child) {
                final stats = achievementProvider.getUserStats();
                
                return SlideTransition(
                  position: Tween<Offset>(
                    begin: const Offset(0, 0.5),
                    end: Offset.zero,
                  ).animate(_statsAnimationController),
                  child: FadeTransition(
                    opacity: _statsAnimationController,
                    child: _buildStatsCards(stats),
                  ),
                );
              },
            );
          },
        ),
      ),
    );
  }
  
  Widget _buildStatsCards(Map<String, dynamic> stats) {
    return Row(
      children: [
        Expanded(
          child: _buildStatCard(
            'Total Unlocked',
            '${stats['completed']}/${stats['total']}',
            Icons.emoji_events,
            const Color(0xFF4CAF50),
            stats['completed'] / stats['total'],
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildStatCard(
            'Education Focus',
            '${stats['educational_percentage']}%',
            Icons.school,
            const Color(0xFF2196F3),
            stats['educational_percentage'] / 100,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildStatCard(
            'League Points',
            '${stats['league_points']}',
            Icons.star,
            const Color(0xFFFF9800),
            stats['league_progress'],
          ),
        ),
      ],
    );
  }
  
  Widget _buildStatCard(
    String title,
    String value,
    IconData icon,
    Color color,
    double progress,
  ) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            color.withOpacity(0.2),
            color.withOpacity(0.1),
          ],
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: color.withOpacity(0.3),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, color: color, size: 20),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  title,
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.white.withOpacity(0.7),
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            value,
            style: const TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 8),
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: progress.clamp(0.0, 1.0),
              backgroundColor: Colors.white.withOpacity(0.1),
              valueColor: AlwaysStoppedAnimation<Color>(color),
              minHeight: 4,
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildCategoryTabs() {
    return SliverToBoxAdapter(
      child: Container(
        margin: const EdgeInsets.symmetric(horizontal: 20),
        child: TabBar(
          controller: _tabController,
          isScrollable: true,
          indicator: BoxDecoration(
            borderRadius: BorderRadius.circular(25),
            gradient: const LinearGradient(
              colors: [Color(0xFF667eea), Color(0xFF764ba2)],
            ),
          ),
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white60,
          labelStyle: const TextStyle(
            fontWeight: FontWeight.w600,
            fontSize: 14,
          ),
          tabs: [
            _buildCategoryTab('All', Icons.apps, 'all'),
            _buildCategoryTab('Education', Icons.school, 'educational'),
            _buildCategoryTab('Safety', Icons.security, 'risk_management'), 
            _buildCategoryTab('Performance', Icons.trending_up, 'performance'),
            _buildCategoryTab('Social', Icons.people, 'social'),
          ],
        ),
      ),
    );
  }
  
  Tab _buildCategoryTab(String label, IconData icon, String category) {
    return Tab(
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 16),
            const SizedBox(width: 6),
            Text(label),
          ],
        ),
      ),
    );
  }
  
  Widget _buildFiltersRow() {
    return SliverToBoxAdapter(
      child: Container(
        margin: const EdgeInsets.all(20),
        child: Column(
          children: [
            // Search bar
            Container(
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: Colors.white.withOpacity(0.2),
                ),
              ),
              child: TextField(
                controller: _searchController,
                style: const TextStyle(color: Colors.white),
                decoration: InputDecoration(
                  hintText: 'Search achievements...',
                  hintStyle: TextStyle(color: Colors.white.withOpacity(0.5)),
                  prefixIcon: Icon(
                    Icons.search,
                    color: Colors.white.withOpacity(0.5),
                  ),
                  border: InputBorder.none,
                  contentPadding: const EdgeInsets.all(16),
                ),
                onChanged: (value) {
                  setState(() {
                    _searchQuery = value;
                  });
                },
              ),
            ),
            
            const SizedBox(height: 12),
            
            // Filter chips
            Wrap(
              spacing: 8,
              children: [
                _buildFilterChip(
                  'Completed Only',
                  _showCompletedOnly,
                  (value) => setState(() => _showCompletedOnly = value),
                ),
                _buildFilterChip(
                  'Recommended',
                  _showRecommendedOnly,
                  (value) => setState(() => _showRecommendedOnly = value),
                ),
                _buildSortDropdown(),
              ],
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildFilterChip(String label, bool selected, ValueChanged<bool> onChanged) {
    return FilterChip(
      label: Text(label),
      selected: selected,
      onSelected: onChanged,
      backgroundColor: Colors.white.withOpacity(0.1),
      selectedColor: const Color(0xFF667eea),
      labelStyle: TextStyle(
        color: selected ? Colors.white : Colors.white70,
        fontWeight: selected ? FontWeight.w600 : FontWeight.normal,
      ),
      checkmarkColor: Colors.white,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(20),
        side: BorderSide(
          color: selected ? const Color(0xFF667eea) : Colors.white.withOpacity(0.2),
        ),
      ),
    );
  }
  
  Widget _buildSortDropdown() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.white.withOpacity(0.2)),
      ),
      child: DropdownButton<String>(
        value: _sortBy,
        underline: const SizedBox(),
        dropdownColor: const Color(0xFF1A1A2E),
        style: const TextStyle(color: Colors.white, fontSize: 14),
        icon: const Icon(Icons.arrow_drop_down, color: Colors.white70),
        items: const [
          DropdownMenuItem(value: 'category', child: Text('By Category')),
          DropdownMenuItem(value: 'rarity', child: Text('By Rarity')),
          DropdownMenuItem(value: 'progress', child: Text('By Progress')),
          DropdownMenuItem(value: 'recent', child: Text('Recently Added')),
        ],
        onChanged: (value) {
          if (value != null) {
            setState(() {
              _sortBy = value;
            });
          }
        },
      ),
    );
  }
  
  Widget _buildAchievementsGrid() {
    return Consumer<AchievementProvider>(
      builder: (context, achievementProvider, child) {
        final achievements = _getFilteredAchievements(achievementProvider);
        
        if (achievements.isEmpty) {
          return _buildEmptyState();
        }
        
        return SliverPadding(
          padding: const EdgeInsets.all(20),
          sliver: SliverGrid(
            gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: 2,
              childAspectRatio: 0.85,
              crossAxisSpacing: 12,
              mainAxisSpacing: 12,
            ),
            delegate: SliverChildBuilderDelegate(
              (context, index) {
                final achievement = achievements[index];
                return AchievementProgressCard(
                  achievement: achievement,
                  onTap: () => _showAchievementDetails(achievement),
                );
              },
              childCount: achievements.length,
            ),
          ),
        );
      },
    );
  }
  
  List<Achievement> _getFilteredAchievements(AchievementProvider provider) {
    var achievements = provider.getAllAchievements();
    
    // Apply category filter
    if (_selectedCategory != 'all') {
      achievements = achievements
          .where((a) => a.category == _selectedCategory)
          .toList();
    }
    
    // Apply search filter
    if (_searchQuery.isNotEmpty) {
      achievements = achievements
          .where((a) => 
              a.name.toLowerCase().contains(_searchQuery.toLowerCase()) ||
              a.description.toLowerCase().contains(_searchQuery.toLowerCase()))
          .toList();
    }
    
    // Apply completion filter
    if (_showCompletedOnly) {
      achievements = achievements.where((a) => a.isCompleted).toList();
    }
    
    // Apply recommended filter
    if (_showRecommendedOnly) {
      final recommended = provider.getRecommendedAchievements();
      achievements = achievements
          .where((a) => recommended.contains(a.id))
          .toList();
    }
    
    // Apply sorting
    _sortAchievements(achievements);
    
    return achievements;
  }
  
  void _sortAchievements(List<Achievement> achievements) {
    switch (_sortBy) {
      case 'category':
        achievements.sort((a, b) {
          final categoryOrder = ['educational', 'risk_management', 'performance', 'social'];
          final aIndex = categoryOrder.indexOf(a.category);
          final bIndex = categoryOrder.indexOf(b.category);
          if (aIndex != bIndex) return aIndex.compareTo(bIndex);
          return a.name.compareTo(b.name);
        });
        break;
      case 'rarity':
        achievements.sort((a, b) {
          final rarityOrder = ['legendary', 'epic', 'rare', 'uncommon', 'common'];
          final aIndex = rarityOrder.indexOf(a.rarity);
          final bIndex = rarityOrder.indexOf(b.rarity);
          return aIndex.compareTo(bIndex);
        });
        break;
      case 'progress':
        achievements.sort((a, b) {
          final aProgress = a.progressCurrent / math.max(a.progressTarget, 1);
          final bProgress = b.progressCurrent / math.max(b.progressTarget, 1);
          return bProgress.compareTo(aProgress);
        });
        break;
      case 'recent':
        achievements.sort((a, b) => b.unlockedAt?.compareTo(a.unlockedAt ?? DateTime(2000)) ?? 0);
        break;
    }
  }
  
  Widget _buildEmptyState() {
    return SliverToBoxAdapter(
      child: Container(
        padding: const EdgeInsets.all(40),
        child: Column(
          children: [
            Icon(
              Icons.search_off,
              size: 64,
              color: Colors.white.withOpacity(0.3),
            ),
            const SizedBox(height: 16),
            Text(
              'No achievements found',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w600,
                color: Colors.white.withOpacity(0.7),
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Try adjusting your filters or search terms',
              style: TextStyle(
                color: Colors.white.withOpacity(0.5),
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildRecommendationsFAB() {
    return Consumer<AchievementProvider>(
      builder: (context, provider, child) {
        final recommendedCount = provider.getRecommendedAchievements().length;
        
        if (recommendedCount == 0) return const SizedBox.shrink();
        
        return FloatingActionButton.extended(
          onPressed: () {
            setState(() {
              _showRecommendedOnly = true;
              _selectedCategory = 'all';
              _tabController.animateTo(0);
            });
          },
          backgroundColor: const Color(0xFF667eea),
          label: Text(
            'View $recommendedCount Recommended',
            style: const TextStyle(
              fontWeight: FontWeight.w600,
              color: Colors.white,
            ),
          ),
          icon: const Icon(Icons.recommend, color: Colors.white),
        );
      },
    );
  }
  
  void _showAchievementDetails(Achievement achievement) {
    showDialog(
      context: context,
      builder: (context) => AchievementDetailsModal(achievement: achievement),
    );
  }
}

/// Custom painter for animated star field background
class StarFieldPainter extends CustomPainter {
  final double animationValue;
  
  StarFieldPainter(this.animationValue);
  
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.white.withOpacity(0.6)
      ..strokeWidth = 1;
    
    final random = math.Random(42); // Fixed seed for consistent stars
    
    for (int i = 0; i < 50; i++) {
      final x = random.nextDouble() * size.width;
      final y = random.nextDouble() * size.height;
      final twinkle = (math.sin(animationValue * 2 * math.pi + i) + 1) / 2;
      
      paint.color = Colors.white.withOpacity(0.3 + twinkle * 0.4);
      canvas.drawCircle(Offset(x, y), 1 + twinkle, paint);
    }
  }
  
  @override
  bool shouldRepaint(StarFieldPainter oldDelegate) {
    return oldDelegate.animationValue != animationValue;
  }
}

// Modal for showing detailed achievement information
class AchievementDetailsModal extends StatelessWidget {
  final Achievement achievement;
  
  const AchievementDetailsModal({
    Key? key,
    required this.achievement,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Dialog(
      backgroundColor: Colors.transparent,
      child: Container(
        constraints: const BoxConstraints(maxWidth: 400),
        padding: const EdgeInsets.all(24),
        decoration: BoxDecoration(
          gradient: const LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Color(0xFF1A1A2E),
              Color(0xFF16213E),
            ],
          ),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: Colors.white.withOpacity(0.2)),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Achievement icon and title
            Row(
              children: [
                Container(
                  width: 56,
                  height: 56,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: _getCategoryColor(achievement.category),
                  ),
                  child: const Icon(
                    Icons.emoji_events,
                    color: Colors.white,
                    size: 28,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        achievement.name,
                        style: const TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                      Text(
                        achievement.category.replaceAll('_', ' ').toUpperCase(),
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                          color: _getCategoryColor(achievement.category),
                          letterSpacing: 1,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            
            const SizedBox(height: 20),
            
            // Description
            Text(
              achievement.description,
              style: TextStyle(
                fontSize: 16,
                color: Colors.white.withOpacity(0.8),
                height: 1.4,
              ),
            ),
            
            if (achievement.cosmicTheme.isNotEmpty) ...[
              const SizedBox(height: 16),
              Text(
                achievement.cosmicTheme,
                style: TextStyle(
                  fontSize: 14,
                  fontStyle: FontStyle.italic,
                  color: Colors.white.withOpacity(0.6),
                ),
              ),
            ],
            
            const SizedBox(height: 24),
            
            // Action buttons
            Row(
              children: [
                if (!achievement.isCompleted) ...[
                  Expanded(
                    child: ElevatedButton(
                      onPressed: () {
                        // Navigate to relevant learning content
                        Navigator.of(context).pop();
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: _getCategoryColor(achievement.category),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                        padding: const EdgeInsets.symmetric(vertical: 12),
                      ),
                      child: const Text(
                        'Start Learning',
                        style: TextStyle(
                          fontWeight: FontWeight.w600,
                          color: Colors.white,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                ],
                Expanded(
                  child: OutlinedButton(
                    onPressed: () => Navigator.of(context).pop(),
                    style: OutlinedButton.styleFrom(
                      side: BorderSide(color: Colors.white.withOpacity(0.3)),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                      padding: const EdgeInsets.symmetric(vertical: 12),
                    ),
                    child: const Text(
                      'Close',
                      style: TextStyle(
                        fontWeight: FontWeight.w600,
                        color: Colors.white70,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
  
  Color _getCategoryColor(String category) {
    switch (category) {
      case 'educational':
        return const Color(0xFF4CAF50);
      case 'risk_management':
        return const Color(0xFF2196F3);
      case 'performance':
        return const Color(0xFFFF9800);
      case 'social':
        return const Color(0xFF9C27B0);
      default:
        return const Color(0xFF607D8B);
    }
  }
}

import 'package:provider/provider.dart';