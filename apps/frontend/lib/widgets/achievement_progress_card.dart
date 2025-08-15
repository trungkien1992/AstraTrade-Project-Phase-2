import 'package:flutter/material.dart';
import 'dart:math' as math;
import '../models/achievement_models.dart';
import '../services/enhanced_haptic_service.dart';

/// Achievement Progress Card displaying individual achievement with research-driven design
/// 
/// Features:
/// - Category-specific color coding and icons
/// - Progress visualization for multi-step achievements
/// - League-based XP scaling display
/// - Completion status with celebration animations
/// - Educational achievement prioritization
/// - Social sharing integration
class AchievementProgressCard extends StatefulWidget {
  final Achievement achievement;
  final VoidCallback? onTap;
  final VoidCallback? onShare;
  final bool showLeagueBonus;
  final bool isRecommended;
  
  const AchievementProgressCard({
    Key? key,
    required this.achievement,
    this.onTap,
    this.onShare,
    this.showLeagueBonus = false,
    this.isRecommended = false,
  }) : super(key: key);

  @override
  State<AchievementProgressCard> createState() => _AchievementProgressCardState();
}

class _AchievementProgressCardState extends State<AchievementProgressCard>
    with TickerProviderStateMixin {
  
  late AnimationController _hoverController;
  late AnimationController _progressController;
  late AnimationController _recommendedController;
  
  late Animation<double> _scaleAnimation;
  late Animation<double> _progressAnimation;
  late Animation<double> _glowAnimation;
  
  bool _isHovered = false;

  @override
  void initState() {
    super.initState();
    
    _hoverController = AnimationController(
      duration: const Duration(milliseconds: 200),
      vsync: this,
    );
    
    _progressController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );
    
    _recommendedController = AnimationController(
      duration: const Duration(milliseconds: 2000),
      vsync: this,
    );
    
    _scaleAnimation = Tween<double>(
      begin: 1.0,
      end: 1.05,
    ).animate(CurvedAnimation(
      parent: _hoverController,
      curve: Curves.easeInOut,
    ));
    
    _progressAnimation = Tween<double>(
      begin: 0.0,
      end: widget.achievement.progressCurrent / math.max(widget.achievement.progressTarget, 1),
    ).animate(CurvedAnimation(
      parent: _progressController,
      curve: Curves.easeOutCubic,
    ));
    
    _glowAnimation = Tween<double>(
      begin: 0.3,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _recommendedController,
      curve: Curves.easeInOut,
    ));
    
    // Start progress animation
    Future.delayed(Duration(milliseconds: math.Random().nextInt(500)), () {
      if (mounted) _progressController.forward();
    });
    
    // Start recommended glow animation
    if (widget.isRecommended) {
      _recommendedController.repeat(reverse: true);
    }
  }

  @override
  void dispose() {
    _hoverController.dispose();
    _progressController.dispose();
    _recommendedController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () {
        EnhancedHapticService().playSelectionHaptic();
        widget.onTap?.call();
      },
      onTapDown: (_) => _setHovered(true),
      onTapUp: (_) => _setHovered(false),
      onTapCancel: () => _setHovered(false),
      child: MouseRegion(
        onEnter: (_) => _setHovered(true),
        onExit: (_) => _setHovered(false),
        child: AnimatedBuilder(
          animation: Listenable.merge([
            _scaleAnimation,
            _glowAnimation,
          ]),
          builder: (context, child) {
            return Transform.scale(
              scale: _scaleAnimation.value,
              child: Container(
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(16),
                  boxShadow: [
                    if (widget.isRecommended)
                      BoxShadow(
                        color: _getCategoryColor().withOpacity(_glowAnimation.value * 0.4),
                        blurRadius: 12,
                        spreadRadius: 2,
                      ),
                    BoxShadow(
                      color: Colors.black.withOpacity(0.3),
                      blurRadius: 8,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: _buildCardContent(),
              ),
            );
          },
        ),
      ),
    );
  }
  
  void _setHovered(bool hovered) {
    if (_isHovered != hovered) {
      setState(() => _isHovered = hovered);
      if (hovered) {
        _hoverController.forward();
      } else {
        _hoverController.reverse();
      }
    }
  }
  
  Widget _buildCardContent() {
    return Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            _getCardBackgroundColor(),
            _getCardBackgroundColor().withOpacity(0.8),
          ],
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: widget.isRecommended 
              ? _getCategoryColor().withOpacity(0.6)
              : Colors.white.withOpacity(0.1),
          width: widget.isRecommended ? 2 : 1,
        ),
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(16),
        child: Stack(
          children: [
            // Background pattern
            _buildBackgroundPattern(),
            
            // Main content
            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Header with icon and status
                  _buildCardHeader(),
                  
                  const SizedBox(height: 12),
                  
                  // Title and description
                  _buildTitleAndDescription(),
                  
                  const Spacer(),
                  
                  // Progress section
                  if (!widget.achievement.isCompleted && widget.achievement.progressTarget > 0)
                    _buildProgressSection(),
                  
                  // Rewards section
                  _buildRewardsSection(),
                ],
              ),
            ),
            
            // Completion overlay
            if (widget.achievement.isCompleted)
              _buildCompletionOverlay(),
            
            // Recommended badge
            if (widget.isRecommended)
              _buildRecommendedBadge(),
          ],
        ),
      ),
    );
  }
  
  Widget _buildBackgroundPattern() {
    return Positioned.fill(
      child: CustomPaint(
        painter: CategoryPatternPainter(
          widget.achievement.category,
          _getCategoryColor().withOpacity(0.05),
        ),
      ),
    );
  }
  
  Widget _buildCardHeader() {
    return Row(
      children: [
        // Category icon
        Container(
          width: 36,
          height: 36,
          decoration: BoxDecoration(
            color: _getCategoryColor().withOpacity(0.2),
            borderRadius: BorderRadius.circular(8),
            border: Border.all(
              color: _getCategoryColor().withOpacity(0.4),
            ),
          ),
          child: Icon(
            _getCategoryIcon(),
            color: _getCategoryColor(),
            size: 20,
          ),
        ),
        
        const Spacer(),
        
        // Rarity indicator
        _buildRarityIndicator(),
        
        const SizedBox(width: 8),
        
        // More actions button
        _buildMoreActionsButton(),
      ],
    );
  }
  
  Widget _buildRarityIndicator() {
    final rarityColor = _getRarityColor();
    final rarityIcons = _getRarityIcons();
    
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: rarityIcons.map((icon) => Icon(
        icon,
        size: 12,
        color: rarityColor,
      )).toList(),
    );
  }
  
  Widget _buildMoreActionsButton() {
    return GestureDetector(
      onTap: _showMoreActions,
      child: Container(
        width: 24,
        height: 24,
        decoration: BoxDecoration(
          color: Colors.white.withOpacity(0.1),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Icon(
          Icons.more_vert,
          size: 16,
          color: Colors.white.withOpacity(0.7),
        ),
      ),
    );
  }
  
  Widget _buildTitleAndDescription() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Category label
        Text(
          _getCategoryLabel(),
          style: TextStyle(
            fontSize: 10,
            fontWeight: FontWeight.w600,
            color: _getCategoryColor(),
            letterSpacing: 0.8,
          ),
        ),
        
        const SizedBox(height: 4),
        
        // Achievement name
        Text(
          widget.achievement.name,
          style: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: Colors.white,
            height: 1.2,
          ),
          maxLines: 2,
          overflow: TextOverflow.ellipsis,
        ),
        
        const SizedBox(height: 6),
        
        // Description
        Text(
          widget.achievement.description,
          style: TextStyle(
            fontSize: 12,
            color: Colors.white.withOpacity(0.7),
            height: 1.3,
          ),
          maxLines: 3,
          overflow: TextOverflow.ellipsis,
        ),
      ],
    );
  }
  
  Widget _buildProgressSection() {
    return Column(
      children: [
        const SizedBox(height: 12),
        
        // Progress bar with animation
        AnimatedBuilder(
          animation: _progressAnimation,
          builder: (context, child) {
            return Column(
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Progress',
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w600,
                        color: Colors.white.withOpacity(0.6),
                      ),
                    ),
                    Text(
                      '${widget.achievement.progressCurrent}/${widget.achievement.progressTarget}',
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w600,
                        color: Colors.white.withOpacity(0.8),
                      ),
                    ),
                  ],
                ),
                
                const SizedBox(height: 4),
                
                ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: LinearProgressIndicator(
                    value: _progressAnimation.value,
                    backgroundColor: Colors.white.withOpacity(0.1),
                    valueColor: AlwaysStoppedAnimation<Color>(
                      _getCategoryColor().withOpacity(0.8),
                    ),
                    minHeight: 6,
                  ),
                ),
              ],
            );
          },
        ),
      ],
    );
  }
  
  Widget _buildRewardsSection() {
    return Container(
      margin: const EdgeInsets.only(top: 12),
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.05),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: Colors.white.withOpacity(0.1),
        ),
      ),
      child: Row(
        children: [
          // XP reward
          Icon(
            Icons.star,
            size: 14,
            color: Colors.amber.withOpacity(0.8),
          ),
          const SizedBox(width: 4),
          Text(
            '+${widget.achievement.xpReward} XP',
            style: TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.w600,
              color: Colors.white.withOpacity(0.8),
            ),
          ),
          
          if (widget.showLeagueBonus) ...[
            const SizedBox(width: 8),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
              decoration: BoxDecoration(
                color: const Color(0xFF667eea).withOpacity(0.2),
                borderRadius: BorderRadius.circular(4),
              ),
              child: Text(
                '×1.5 League',
                style: TextStyle(
                  fontSize: 9,
                  fontWeight: FontWeight.w600,
                  color: const Color(0xFF667eea),
                ),
              ),
            ),
          ],
          
          const Spacer(),
          
          // Share button for completed achievements
          if (widget.achievement.isCompleted && widget.onShare != null)
            GestureDetector(
              onTap: widget.onShare,
              child: Icon(
                Icons.share,
                size: 16,
                color: Colors.white.withOpacity(0.6),
              ),
            ),
        ],
      ),
    );
  }
  
  Widget _buildCompletionOverlay() {
    return Positioned.fill(
      child: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topRight,
            end: Alignment.bottomLeft,
            colors: [
              _getCategoryColor().withOpacity(0.1),
              Colors.transparent,
            ],
          ),
          borderRadius: BorderRadius.circular(16),
        ),
        child: const Align(
          alignment: Alignment.topRight,
          child: Padding(
            padding: EdgeInsets.all(12),
            child: Icon(
              Icons.check_circle,
              color: Colors.green,
              size: 24,
            ),
          ),
        ),
      ),
    );
  }
  
  Widget _buildRecommendedBadge() {
    return Positioned(
      top: -8,
      right: -8,
      child: AnimatedBuilder(
        animation: _glowAnimation,
        builder: (context, child) {
          return Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [
                  const Color(0xFF667eea).withOpacity(_glowAnimation.value),
                  const Color(0xFF764ba2).withOpacity(_glowAnimation.value),
                ],
              ),
              borderRadius: BorderRadius.circular(12),
              boxShadow: [
                BoxShadow(
                  color: const Color(0xFF667eea).withOpacity(_glowAnimation.value * 0.3),
                  blurRadius: 8,
                  spreadRadius: 1,
                ),
              ],
            ),
            child: const Text(
              'RECOMMENDED',
              style: TextStyle(
                fontSize: 8,
                fontWeight: FontWeight.bold,
                color: Colors.white,
                letterSpacing: 0.5,
              ),
            ),
          );
        },
      ),
    );
  }
  
  Color _getCategoryColor() {
    switch (widget.achievement.category) {
      case 'educational':
        return const Color(0xFF4CAF50); // Green for learning
      case 'risk_management':
        return const Color(0xFF2196F3); // Blue for safety
      case 'performance':
        return const Color(0xFFFF9800); // Orange for performance
      case 'social':
        return const Color(0xFF9C27B0); // Purple for community
      default:
        return const Color(0xFF607D8B); // Blue-grey default
    }
  }
  
  Color _getCardBackgroundColor() {
    if (widget.achievement.isCompleted) {
      return _getCategoryColor().withOpacity(0.15);
    }
    return const Color(0xFF1A1A2E).withOpacity(0.8);
  }
  
  IconData _getCategoryIcon() {
    switch (widget.achievement.category) {
      case 'educational':
        return Icons.school;
      case 'risk_management':
        return Icons.security;
      case 'performance':
        return Icons.trending_up;
      case 'social':
        return Icons.people;
      default:
        return Icons.emoji_events;
    }
  }
  
  String _getCategoryLabel() {
    switch (widget.achievement.category) {
      case 'educational':
        return 'EDUCATION';
      case 'risk_management':
        return 'RISK MANAGEMENT';
      case 'performance':
        return 'PERFORMANCE';
      case 'social':
        return 'SOCIAL';
      default:
        return 'ACHIEVEMENT';
    }
  }
  
  Color _getRarityColor() {
    switch (widget.achievement.rarity) {
      case 'legendary':
        return const Color(0xFFFFD700); // Gold
      case 'epic':
        return const Color(0xFF9C27B0); // Purple
      case 'rare':
        return const Color(0xFF2196F3); // Blue
      case 'uncommon':
        return const Color(0xFF4CAF50); // Green
      default:
        return const Color(0xFF9E9E9E); // Grey
    }
  }
  
  List<IconData> _getRarityIcons() {
    switch (widget.achievement.rarity) {
      case 'legendary':
        return [Icons.star, Icons.star, Icons.star, Icons.star, Icons.star];
      case 'epic':
        return [Icons.star, Icons.star, Icons.star, Icons.star];
      case 'rare':
        return [Icons.star, Icons.star, Icons.star];
      case 'uncommon':
        return [Icons.star, Icons.star];
      default:
        return [Icons.star];
    }
  }
  
  void _showMoreActions() {
    showModalBottomSheet(
      context: context,
      backgroundColor: const Color(0xFF1A1A2E),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => Container(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Icons.info_outline, color: Colors.white70),
              title: const Text(
                'View Details',
                style: TextStyle(color: Colors.white),
              ),
              onTap: () {
                Navigator.pop(context);
                widget.onTap?.call();
              },
            ),
            
            if (widget.achievement.isCompleted) ...[
              ListTile(
                leading: const Icon(Icons.share, color: Colors.white70),
                title: const Text(
                  'Share Achievement',
                  style: TextStyle(color: Colors.white),
                ),
                onTap: () {
                  Navigator.pop(context);
                  widget.onShare?.call();
                },
              ),
            ] else ...[
              ListTile(
                leading: const Icon(Icons.school, color: Colors.white70),
                title: const Text(
                  'View Learning Path',
                  style: TextStyle(color: Colors.white),
                ),
                onTap: () {
                  Navigator.pop(context);
                  // Navigate to learning content
                },
              ),
            ],
            
            ListTile(
              leading: const Icon(Icons.bookmark_border, color: Colors.white70),
              title: const Text(
                'Add to Favorites',
                style: TextStyle(color: Colors.white),
              ),
              onTap: () {
                Navigator.pop(context);
                // Add to favorites
              },
            ),
          ],
        ),
      ),
    );
  }
}

/// Custom painter for category-specific background patterns
class CategoryPatternPainter extends CustomPainter {
  final String category;
  final Color color;
  
  CategoryPatternPainter(this.category, this.color);
  
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..strokeWidth = 1
      ..style = PaintingStyle.stroke;
    
    switch (category) {
      case 'educational':
        _drawEducationPattern(canvas, size, paint);
        break;
      case 'risk_management':
        _drawSafetyPattern(canvas, size, paint);
        break;
      case 'performance':
        _drawPerformancePattern(canvas, size, paint);
        break;
      case 'social':
        _drawSocialPattern(canvas, size, paint);
        break;
    }
  }
  
  void _drawEducationPattern(Canvas canvas, Size size, Paint paint) {
    // Draw book/learning icons pattern
    for (int i = 0; i < 3; i++) {
      for (int j = 0; j < 4; j++) {
        final x = (i + 0.5) * size.width / 3;
        final y = (j + 0.5) * size.height / 4;
        
        // Draw simple book outline
        final rect = Rect.fromCenter(
          center: Offset(x, y),
          width: 8,
          height: 6,
        );
        canvas.drawRect(rect, paint);
      }
    }
  }
  
  void _drawSafetyPattern(Canvas canvas, Size size, Paint paint) {
    // Draw shield pattern
    for (int i = 0; i < 2; i++) {
      for (int j = 0; j < 3; j++) {
        final x = (i + 0.5) * size.width / 2;
        final y = (j + 0.5) * size.height / 3;
        
        final path = Path()
          ..moveTo(x, y - 5)
          ..lineTo(x - 4, y - 2)
          ..lineTo(x - 4, y + 2)
          ..lineTo(x, y + 5)
          ..lineTo(x + 4, y + 2)
          ..lineTo(x + 4, y - 2)
          ..close();
        
        canvas.drawPath(path, paint);
      }
    }
  }
  
  void _drawPerformancePattern(Canvas canvas, Size size, Paint paint) {
    // Draw upward trending arrows
    for (int i = 0; i < 4; i++) {
      for (int j = 0; j < 3; j++) {
        final x = (i + 0.5) * size.width / 4;
        final y = (j + 0.5) * size.height / 3;
        
        final path = Path()
          ..moveTo(x - 3, y + 2)
          ..lineTo(x, y - 2)
          ..lineTo(x + 3, y + 2)
          ..moveTo(x - 1, y)
          ..lineTo(x + 1, y);
        
        canvas.drawPath(path, paint);
      }
    }
  }
  
  void _drawSocialPattern(Canvas canvas, Size size, Paint paint) {
    // Draw connected circles (people network)
    for (int i = 0; i < 3; i++) {
      for (int j = 0; j < 4; j++) {
        final x = (i + 0.5) * size.width / 3;
        final y = (j + 0.5) * size.height / 4;
        
        canvas.drawCircle(Offset(x, y), 3, paint);
        
        // Draw connections to adjacent circles
        if (i < 2) {
          canvas.drawLine(
            Offset(x + 3, y),
            Offset(x + size.width / 3 - 3, y),
            paint,
          );
        }
      }
    }
  }
  
  @override
  bool shouldRepaint(CategoryPatternPainter oldDelegate) {
    return oldDelegate.category != category || oldDelegate.color != color;
  }
}