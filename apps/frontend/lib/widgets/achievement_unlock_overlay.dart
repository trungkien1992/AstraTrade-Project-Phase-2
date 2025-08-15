import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'dart:math' as math;
import '../models/achievement_models.dart';
import '../services/enhanced_audio_service.dart';
import '../services/enhanced_haptic_service.dart';

/// Research-driven achievement unlock overlay with context-sensitive display
/// 
/// Features:
/// - Dopamine-optimized animations based on neuroscience research
/// - Context-aware positioning (bottom-right, subtle, etc.)
/// - Anti-addiction compliant (no gambling-like mechanics)
/// - Educational achievement prioritization with celebration
/// - Cosmic theming with particle effects
class AchievementUnlockOverlay extends StatefulWidget {
  final Achievement achievement;
  final String displayPosition;
  final String displayStyle;
  final int autoDismissSeconds;
  final bool soundEnabled;
  final bool animationEnabled;
  final VoidCallback? onDismiss;
  final VoidCallback? onTap;
  
  const AchievementUnlockOverlay({
    Key? key,
    required this.achievement,
    this.displayPosition = 'bottom_right',
    this.displayStyle = 'standard',
    this.autoDismissSeconds = 5,
    this.soundEnabled = true,
    this.animationEnabled = true,
    this.onDismiss,
    this.onTap,
  }) : super(key: key);

  @override
  State<AchievementUnlockOverlay> createState() => _AchievementUnlockOverlayState();
}

class _AchievementUnlockOverlayState extends State<AchievementUnlockOverlay>
    with TickerProviderStateMixin {
  
  late AnimationController _slideController;
  late AnimationController _pulseController;
  late AnimationController _particleController;
  late AnimationController _shimmerController;
  
  late Animation<Offset> _slideAnimation;
  late Animation<double> _pulseAnimation;
  late Animation<double> _opacityAnimation;
  late Animation<double> _scaleAnimation;
  late Animation<double> _shimmerAnimation;
  
  bool _isVisible = false;

  @override
  void initState() {
    super.initState();
    _initializeAnimations();
    _showAchievement();
    
    // Auto-dismiss timer
    if (widget.autoDismissSeconds > 0) {
      Future.delayed(Duration(seconds: widget.autoDismissSeconds), () {
        if (mounted) {
          _hideAchievement();
        }
      });
    }
  }
  
  void _initializeAnimations() {
    // Main slide-in animation
    _slideController = AnimationController(
      duration: const Duration(milliseconds: 600),
      vsync: this,
    );
    
    // Pulse animation for attention
    _pulseController = AnimationController(
      duration: const Duration(milliseconds: 1200),
      vsync: this,
    );
    
    // Particle effect controller
    _particleController = AnimationController(
      duration: const Duration(milliseconds: 2000),
      vsync: this,
    );
    
    // Shimmer effect for rare achievements
    _shimmerController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );
    
    // Configure slide animation based on position
    final slideOffset = _getSlideOffset();
    _slideAnimation = Tween<Offset>(
      begin: slideOffset,
      end: Offset.zero,
    ).animate(CurvedAnimation(
      parent: _slideController,
      curve: Curves.easeOutBack,
    ));
    
    // Pulse animation for subtle attention
    _pulseAnimation = Tween<double>(
      begin: 1.0,
      end: 1.05,
    ).animate(CurvedAnimation(
      parent: _pulseController,
      curve: Curves.easeInOut,
    ));
    
    // Opacity animation for fade effects
    _opacityAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _slideController,
      curve: const Interval(0.0, 0.7),
    ));
    
    // Scale animation for celebration
    _scaleAnimation = Tween<double>(
      begin: 0.8,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _slideController,
      curve: Curves.elasticOut,
    ));
    
    // Shimmer animation for legendary achievements
    _shimmerAnimation = Tween<double>(
      begin: -1.0,
      end: 2.0,
    ).animate(_shimmerController);
  }
  
  Offset _getSlideOffset() {
    switch (widget.displayPosition) {
      case 'bottom_right':
        return const Offset(1.0, 0.0);
      case 'bottom_left':
        return const Offset(-1.0, 0.0);
      case 'top_right':
        return const Offset(1.0, 0.0);
      case 'center_modal':
        return const Offset(0.0, 1.0);
      default:
        return const Offset(1.0, 0.0);
    }
  }
  
  Future<void> _showAchievement() async {
    if (!widget.animationEnabled) {
      setState(() => _isVisible = true);
      return;
    }
    
    setState(() => _isVisible = true);
    
    // Play sound effect based on achievement category
    if (widget.soundEnabled) {
      await _playAchievementSound();
    }
    
    // Play haptic feedback
    await _playHapticFeedback();
    
    // Start animations based on display style
    if (widget.displayStyle == 'celebrate') {
      await _playCelebrationSequence();
    } else if (widget.displayStyle == 'standard') {
      await _playStandardSequence();
    } else {
      await _playSubtleSequence();
    }
  }
  
  Future<void> _playAchievementSound() async {
    final audioService = EnhancedAudioService();
    
    String soundFile = 'achievement_standard.wav';
    
    // Category-specific sounds based on research-driven categories
    switch (widget.achievement.category) {
      case 'educational':
        soundFile = 'achievement_educational.wav';
        break;
      case 'risk_management':
        soundFile = 'achievement_safety.wav';
        break;
      case 'performance':
        soundFile = 'achievement_performance.wav';
        break;
      case 'social':
        soundFile = 'achievement_social.wav';
        break;
    }
    
    // Volume based on rarity (subtle for common, louder for rare)
    double volume = widget.achievement.rarity == 'legendary' ? 0.8 : 0.6;
    if (widget.displayStyle == 'subtle') volume *= 0.5;
    
    await audioService.playAchievementSound(soundFile, volume: volume);
  }
  
  Future<void> _playHapticFeedback() async {
    final hapticService = EnhancedHapticService();
    
    // Haptic intensity based on achievement importance
    if (widget.achievement.category == 'educational' || 
        widget.achievement.category == 'risk_management') {
      await hapticService.playSuccessHaptic(intensity: 'medium');
    } else if (widget.achievement.rarity == 'legendary') {
      await hapticService.playSuccessHaptic(intensity: 'heavy');
    } else {
      await hapticService.playSuccessHaptic(intensity: 'light');
    }
  }
  
  Future<void> _playCelebrationSequence() async {
    // Full celebration sequence for educational/safety achievements
    _slideController.forward();
    
    await Future.delayed(const Duration(milliseconds: 300));
    
    // Start particle effects for legendary achievements
    if (widget.achievement.rarity == 'legendary') {
      _particleController.forward();
      _shimmerController.repeat();
    }
    
    // Pulse animation for attention
    _pulseController.repeat(reverse: true);
    
    await Future.delayed(const Duration(milliseconds: 800));
    
    // Stop pulse after initial celebration
    await Future.delayed(const Duration(milliseconds: 2000));
    _pulseController.stop();
    _shimmerController.stop();
  }
  
  Future<void> _playStandardSequence() async {
    _slideController.forward();
    
    await Future.delayed(const Duration(milliseconds: 400));
    
    if (widget.achievement.rarity != 'common') {
      _pulseController.repeat(reverse: true);
      
      await Future.delayed(const Duration(milliseconds: 1500));
      _pulseController.stop();
    }
  }
  
  Future<void> _playSubtleSequence() async {
    // Minimal animation for subtle display during trading
    _slideController.forward();
  }
  
  Future<void> _hideAchievement() async {
    if (!mounted) return;
    
    _pulseController.stop();
    _shimmerController.stop();
    
    await _slideController.reverse();
    
    if (mounted) {
      widget.onDismiss?.call();
    }
  }
  
  @override
  void dispose() {
    _slideController.dispose();
    _pulseController.dispose();
    _particleController.dispose();
    _shimmerController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (!_isVisible) return const SizedBox.shrink();
    
    return Positioned(
      ...._getPositionParameters(context),
      child: SlideTransition(
        position: _slideAnimation,
        child: AnimatedBuilder(
          animation: Listenable.merge([
            _pulseController,
            _scaleAnimation,
            _opacityAnimation,
          ]),
          builder: (context, child) {
            return Transform.scale(
              scale: _scaleAnimation.value * _pulseAnimation.value,
              child: Opacity(
                opacity: _opacityAnimation.value,
                child: _buildAchievementCard(),
              ),
            );
          },
        ),
      ),
    );
  }
  
  Map<String, double> _getPositionParameters(BuildContext context) {
    const margin = 20.0;
    
    switch (widget.displayPosition) {
      case 'bottom_right':
        return {
          'bottom': margin,
          'right': margin,
        };
      case 'bottom_left':
        return {
          'bottom': margin,
          'left': margin,
        };
      case 'top_right':
        return {
          'top': margin + MediaQuery.of(context).padding.top,
          'right': margin,
        };
      case 'center_modal':
        return {
          'top': MediaQuery.of(context).size.height * 0.3,
          'left': margin,
          'right': margin,
        };
      default:
        return {
          'bottom': margin,
          'right': margin,
        };
    }
  }
  
  Widget _buildAchievementCard() {
    return GestureDetector(
      onTap: () {
        widget.onTap?.call();
        _hideAchievement();
      },
      child: Container(
        constraints: const BoxConstraints(
          maxWidth: 350,
          minWidth: 280,
        ),
        child: Stack(
          clipBehavior: Clip.none,
          children: [
            // Background card
            _buildCardBackground(),
            
            // Shimmer effect for legendary achievements
            if (widget.achievement.rarity == 'legendary')
              _buildShimmerEffect(),
            
            // Particle effects for celebration
            if (widget.displayStyle == 'celebrate' && widget.achievement.rarity == 'legendary')
              _buildParticleEffects(),
            
            // Content
            _buildCardContent(),
            
            // Close button
            _buildCloseButton(),
          ],
        ),
      ),
    );
  }
  
  Widget _buildCardBackground() {
    final isSubtle = widget.displayStyle == 'subtle';
    final cardColor = _getCardColor();
    
    return Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            cardColor.withOpacity(isSubtle ? 0.85 : 0.95),
            cardColor.withOpacity(isSubtle ? 0.75 : 0.90),
          ],
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: _getBorderColor(),
          width: widget.achievement.rarity == 'legendary' ? 2 : 1,
        ),
        boxShadow: [
          BoxShadow(
            color: cardColor.withOpacity(0.3),
            blurRadius: isSubtle ? 8 : 16,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(16),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
          child: Container(
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.1),
            ),
          ),
        ),
      ),
    );
  }
  
  Color _getCardColor() {
    // Category-based colors aligned with research-driven categories
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
  
  Color _getBorderColor() {
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
  
  Widget _buildShimmerEffect() {
    return AnimatedBuilder(
      animation: _shimmerAnimation,
      builder: (context, child) {
        return Container(
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(16),
            gradient: LinearGradient(
              begin: Alignment(-1.0 + _shimmerAnimation.value * 2, -1.0),
              end: Alignment(-1.0 + _shimmerAnimation.value * 2 + 0.5, -1.0),
              colors: const [
                Colors.transparent,
                Colors.white24,
                Colors.transparent,
              ],
            ),
          ),
        );
      },
    );
  }
  
  Widget _buildParticleEffects() {
    return AnimatedBuilder(
      animation: _particleController,
      builder: (context, child) {
        return CustomPaint(
          painter: ParticleEffectsPainter(_particleController.value),
          size: const Size(350, 150),
        );
      },
    );
  }
  
  Widget _buildCardContent() {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            children: [
              // Achievement icon
              _buildAchievementIcon(),
              const SizedBox(width: 12),
              
              // Title and category
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      _getCategoryTitle(),
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                        color: Colors.white.withOpacity(0.8),
                        letterSpacing: 0.8,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      widget.achievement.name,
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                  ],
                ),
              ),
              
              // XP reward
              _buildXPReward(),
            ],
          ),
          
          const SizedBox(height: 8),
          
          // Description
          Text(
            widget.achievement.description,
            style: TextStyle(
              fontSize: 14,
              color: Colors.white.withOpacity(0.9),
              height: 1.3,
            ),
          ),
          
          if (widget.achievement.cosmicTheme.isNotEmpty) ...[
            const SizedBox(height: 8),
            Text(
              widget.achievement.cosmicTheme,
              style: TextStyle(
                fontSize: 12,
                fontStyle: FontStyle.italic,
                color: Colors.white.withOpacity(0.7),
              ),
            ),
          ],
          
          // Progress indicator for multi-step achievements
          if (widget.achievement.progressCurrent > 0) ...[
            const SizedBox(height: 12),
            _buildProgressIndicator(),
          ],
        ],
      ),
    );
  }
  
  String _getCategoryTitle() {
    switch (widget.achievement.category) {
      case 'educational':
        return '🎓 KNOWLEDGE UNLOCKED';
      case 'risk_management':
        return '🛡️ SAFETY MILESTONE';
      case 'performance':
        return '⭐ TRADING EXCELLENCE';
      case 'social':
        return '🤝 COMMUNITY IMPACT';
      default:
        return '🏆 ACHIEVEMENT UNLOCKED';
    }
  }
  
  Widget _buildAchievementIcon() {
    String iconPath = 'assets/icons/achievement_default.png';
    
    // Category-specific icons
    switch (widget.achievement.category) {
      case 'educational':
        iconPath = 'assets/icons/achievement_education.png';
        break;
      case 'risk_management':
        iconPath = 'assets/icons/achievement_safety.png';
        break;
      case 'performance':
        iconPath = 'assets/icons/achievement_performance.png';
        break;
      case 'social':
        iconPath = 'assets/icons/achievement_social.png';
        break;
    }
    
    return Container(
      width: 48,
      height: 48,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        border: Border.all(
          color: _getBorderColor(),
          width: 2,
        ),
        boxShadow: [
          BoxShadow(
            color: _getBorderColor().withOpacity(0.3),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: ClipOval(
        child: Image.asset(
          iconPath,
          width: 44,
          height: 44,
          fit: BoxFit.cover,
          errorBuilder: (context, error, stackTrace) {
            // Fallback icon
            return Container(
              color: _getCardColor(),
              child: const Icon(
                Icons.emoji_events,
                color: Colors.white,
                size: 24,
              ),
            );
          },
        ),
      ),
    );
  }
  
  Widget _buildXPReward() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.2),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Icon(
            Icons.star,
            size: 16,
            color: Colors.amber,
          ),
          const SizedBox(width: 4),
          Text(
            '+${widget.achievement.xpReward} XP',
            style: const TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildProgressIndicator() {
    final progress = widget.achievement.progressCurrent / widget.achievement.progressTarget;
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Progress',
              style: TextStyle(
                fontSize: 12,
                color: Colors.white.withOpacity(0.7),
              ),
            ),
            Text(
              '${widget.achievement.progressCurrent}/${widget.achievement.progressTarget}',
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w600,
                color: Colors.white.withOpacity(0.9),
              ),
            ),
          ],
        ),
        const SizedBox(height: 4),
        ClipRRect(
          borderRadius: BorderRadius.circular(8),
          child: LinearProgressIndicator(
            value: progress,
            backgroundColor: Colors.white.withOpacity(0.2),
            valueColor: AlwaysStoppedAnimation<Color>(
              _getBorderColor().withOpacity(0.8),
            ),
            minHeight: 6,
          ),
        ),
      ],
    );
  }
  
  Widget _buildCloseButton() {
    return Positioned(
      top: 8,
      right: 8,
      child: GestureDetector(
        onTap: _hideAchievement,
        child: Container(
          width: 24,
          height: 24,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: Colors.black.withOpacity(0.3),
          ),
          child: const Icon(
            Icons.close,
            size: 16,
            color: Colors.white70,
          ),
        ),
      ),
    );
  }
}

/// Custom painter for particle effects on legendary achievements
class ParticleEffectsPainter extends CustomPainter {
  final double animationValue;
  
  ParticleEffectsPainter(this.animationValue);
  
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.amber.withOpacity(0.6)
      ..blendMode = BlendMode.screen;
    
    final random = math.Random(42); // Fixed seed for consistent particles
    
    for (int i = 0; i < 20; i++) {
      final x = random.nextDouble() * size.width;
      final y = random.nextDouble() * size.height;
      
      final particleProgress = (animationValue + random.nextDouble()) % 1.0;
      final opacity = 1.0 - particleProgress;
      final particleSize = 2 + (random.nextDouble() * 3);
      
      if (opacity > 0) {
        paint.color = Colors.amber.withOpacity(opacity * 0.6);
        canvas.drawCircle(
          Offset(x, y - (particleProgress * 50)),
          particleSize,
          paint,
        );
      }
    }
  }
  
  @override
  bool shouldRepaint(ParticleEffectsPainter oldDelegate) {
    return oldDelegate.animationValue != animationValue;
  }
}

import 'dart:ui';