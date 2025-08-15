import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'dart:math' as math;
import 'cosmic_particle_effect.dart';

/// Milestone celebration widget for special achievements
/// Creates dramatic effects for level-ups, streaks, and major wins
class MilestoneCelebration extends StatefulWidget {
  final MilestoneType milestoneType;
  final String title;
  final String subtitle;
  final String? customMessage;
  final Color primaryColor;
  final Color secondaryColor;
  final VoidCallback? onComplete;
  final Duration duration;
  final bool autoStart;

  const MilestoneCelebration({
    super.key,
    required this.milestoneType,
    required this.title,
    this.subtitle = '',
    this.customMessage,
    this.primaryColor = Colors.amber,
    this.secondaryColor = Colors.orange,
    this.onComplete,
    this.duration = const Duration(milliseconds: 3000),
    this.autoStart = true,
  });

  @override
  State<MilestoneCelebration> createState() => _MilestoneCelebrationState();
}

class _MilestoneCelebrationState extends State<MilestoneCelebration>
    with TickerProviderStateMixin {
  late AnimationController _mainController;
  late AnimationController _pulseController;
  late AnimationController _textController;
  late AnimationController _particleController;

  late Animation<double> _scaleAnimation;
  late Animation<double> _fadeAnimation;
  late Animation<double> _pulseAnimation;
  late Animation<Offset> _slideAnimation;
  late Animation<double> _rotationAnimation;

  @override
  void initState() {
    super.initState();
    _setupAnimations();
    
    if (widget.autoStart) {
      _startCelebration();
    }
  }

  void _setupAnimations() {
    _mainController = AnimationController(
      duration: widget.duration,
      vsync: this,
    );

    _pulseController = AnimationController(
      duration: const Duration(milliseconds: 500),
      vsync: this,
    );

    _textController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );

    _particleController = AnimationController(
      duration: const Duration(milliseconds: 2000),
      vsync: this,
    );

    // Main scale animation with dramatic entrance
    _scaleAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _mainController,
        curve: const Interval(0.0, 0.4, curve: Curves.elasticOut),
      ),
    );

    // Fade in/out animation
    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _mainController,
        curve: const Interval(0.0, 0.3, curve: Curves.easeInOut),
      ),
    );

    // Continuous pulse animation
    _pulseAnimation = Tween<double>(begin: 1.0, end: 1.1).animate(
      CurvedAnimation(
        parent: _pulseController,
        curve: Curves.easeInOut,
      ),
    );

    // Text slide animation
    _slideAnimation = Tween<Offset>(
      begin: const Offset(0, 0.5),
      end: Offset.zero,
    ).animate(
      CurvedAnimation(
        parent: _textController,
        curve: Curves.easeOutCubic,
      ),
    );

    // Rotation animation for dynamic elements
    _rotationAnimation = Tween<double>(begin: 0.0, end: 2 * math.pi).animate(
      CurvedAnimation(
        parent: _particleController,
        curve: Curves.linear,
      ),
    );
  }

  @override
  void dispose() {
    _mainController.dispose();
    _pulseController.dispose();
    _textController.dispose();
    _particleController.dispose();
    super.dispose();
  }

  void _startCelebration() {
    // Trigger haptic feedback
    HapticFeedback.heavyImpact();
    
    // Start main animation
    _mainController.forward();
    
    // Start pulse animation with repeat
    _pulseController.repeat(reverse: true);
    
    // Delayed text animation
    Future.delayed(const Duration(milliseconds: 200), () {
      if (mounted) {
        _textController.forward();
      }
    });
    
    // Start particle effects
    _particleController.forward();
    
    // Complete animation and cleanup
    _mainController.addStatusListener((status) {
      if (status == AnimationStatus.completed) {
        _completeCelebration();
      }
    });
  }

  void _completeCelebration() {
    widget.onComplete?.call();
  }

  @override
  Widget build(BuildContext context) {
    final screenSize = MediaQuery.of(context).size;
    
    return Positioned.fill(
      child: Material(
        color: Colors.transparent,
        child: Stack(
          alignment: Alignment.center,
          children: [
            // Background overlay
            AnimatedBuilder(
              animation: _fadeAnimation,
              builder: (context, child) {
                return Container(
                  color: Colors.black.withOpacity(_fadeAnimation.value * 0.7),
                );
              },
            ),

            // Particle effects background
            AnimatedBuilder(
              animation: _particleController,
              builder: (context, child) {
                return Positioned.fill(
                  child: CosmicParticleEffect(
                    isSuccess: true,
                    effectType: _getParticleEffect(),
                    particleCount: _getParticleCount(),
                    intensity: 1.5,
                  ),
                );
              },
            ),

            // Main celebration content
            AnimatedBuilder(
              animation: Listenable.merge([_scaleAnimation, _pulseAnimation]),
              builder: (context, child) {
                return Transform.scale(
                  scale: _scaleAnimation.value * _pulseAnimation.value,
                  child: Container(
                    constraints: BoxConstraints(
                      maxWidth: screenSize.width * 0.8,
                      maxHeight: screenSize.height * 0.6,
                    ),
                    padding: const EdgeInsets.all(32),
                    decoration: BoxDecoration(
                      gradient: RadialGradient(
                        colors: [
                          widget.primaryColor.withOpacity(0.9),
                          widget.secondaryColor.withOpacity(0.8),
                        ],
                      ),
                      borderRadius: BorderRadius.circular(24),
                      border: Border.all(
                        color: Colors.white.withOpacity(0.3),
                        width: 2,
                      ),
                      boxShadow: [
                        BoxShadow(
                          color: widget.primaryColor.withOpacity(0.5),
                          blurRadius: 20,
                          spreadRadius: 5,
                        ),
                      ],
                    ),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        // Milestone icon
                        _buildMilestoneIcon(),
                        
                        const SizedBox(height: 16),
                        
                        // Title
                        SlideTransition(
                          position: _slideAnimation,
                          child: FadeTransition(
                            opacity: _textController,
                            child: Text(
                              widget.title,
                              style: const TextStyle(
                                fontSize: 32,
                                fontWeight: FontWeight.bold,
                                color: Colors.white,
                                shadows: [
                                  Shadow(
                                    color: Colors.black26,
                                    blurRadius: 4,
                                    offset: Offset(0, 2),
                                  ),
                                ],
                              ),
                              textAlign: TextAlign.center,
                            ),
                          ),
                        ),
                        
                        if (widget.subtitle.isNotEmpty) ...[
                          const SizedBox(height: 8),
                          SlideTransition(
                            position: _slideAnimation,
                            child: FadeTransition(
                              opacity: _textController,
                              child: Text(
                                widget.subtitle,
                                style: const TextStyle(
                                  fontSize: 18,
                                  color: Colors.white70,
                                  fontWeight: FontWeight.w500,
                                ),
                                textAlign: TextAlign.center,
                              ),
                            ),
                          ),
                        ],
                        
                        if (widget.customMessage != null) ...[
                          const SizedBox(height: 16),
                          SlideTransition(
                            position: _slideAnimation,
                            child: FadeTransition(
                              opacity: _textController,
                              child: Container(
                                padding: const EdgeInsets.all(16),
                                decoration: BoxDecoration(
                                  color: Colors.white.withOpacity(0.2),
                                  borderRadius: BorderRadius.circular(12),
                                ),
                                child: Text(
                                  widget.customMessage!,
                                  style: const TextStyle(
                                    fontSize: 16,
                                    color: Colors.white,
                                    height: 1.4,
                                  ),
                                  textAlign: TextAlign.center,
                                ),
                              ),
                            ),
                          ),
                        ],
                      ],
                    ),
                  ),
                );
              },
            ),

            // Floating sparkles
            ..._buildFloatingSparkles(screenSize),
          ],
        ),
      ),
    );
  }

  Widget _buildMilestoneIcon() {
    final iconData = _getMilestoneIcon();
    
    return AnimatedBuilder(
      animation: _rotationAnimation,
      builder: (context, child) {
        return Container(
          width: 80,
          height: 80,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: Colors.white,
            boxShadow: [
              BoxShadow(
                color: widget.primaryColor.withOpacity(0.5),
                blurRadius: 15,
                spreadRadius: 2,
              ),
            ],
          ),
          child: Transform.rotate(
            angle: widget.milestoneType == MilestoneType.levelUp 
                ? _rotationAnimation.value 
                : 0.0,
            child: Icon(
              iconData,
              size: 40,
              color: widget.primaryColor,
            ),
          ),
        );
      },
    );
  }

  List<Widget> _buildFloatingSparkles(Size screenSize) {
    final sparkles = <Widget>[];
    final random = math.Random();
    
    for (int i = 0; i < 12; i++) {
      final left = random.nextDouble() * screenSize.width;
      final top = random.nextDouble() * screenSize.height;
      final delay = i * 100.0;
      
      sparkles.add(
        Positioned(
          left: left,
          top: top,
          child: AnimatedBuilder(
            animation: _particleController,
            builder: (context, child) {
              final progress = (_particleController.value + delay / 1000) % 1.0;
              final opacity = (math.sin(progress * math.pi * 2) + 1) / 2;
              
              return Opacity(
                opacity: opacity * 0.8,
                child: Icon(
                  Icons.auto_awesome,
                  size: 16 + random.nextDouble() * 8,
                  color: Colors.white,
                ),
              );
            },
          ),
        ),
      );
    }
    
    return sparkles;
  }

  IconData _getMilestoneIcon() {
    switch (widget.milestoneType) {
      case MilestoneType.levelUp:
        return Icons.emoji_events;
      case MilestoneType.winStreak:
        return Icons.local_fire_department;
      case MilestoneType.bigWin:
        return Icons.trending_up;
      case MilestoneType.firstTrade:
        return Icons.rocket_launch;
      case MilestoneType.achievement:
        return Icons.military_tech;
      case MilestoneType.milestone:
        return Icons.flag;
    }
  }

  ParticleEffectType _getParticleEffect() {
    switch (widget.milestoneType) {
      case MilestoneType.levelUp:
        return ParticleEffectType.fountain;
      case MilestoneType.winStreak:
        return ParticleEffectType.spiral;
      case MilestoneType.bigWin:
        return ParticleEffectType.burst;
      case MilestoneType.firstTrade:
        return ParticleEffectType.starField;
      case MilestoneType.achievement:
        return ParticleEffectType.confetti;
      case MilestoneType.milestone:
        return ParticleEffectType.shimmer;
    }
  }

  int _getParticleCount() {
    switch (widget.milestoneType) {
      case MilestoneType.levelUp:
        return 20;
      case MilestoneType.winStreak:
        return 15;
      case MilestoneType.bigWin:
        return 25;
      case MilestoneType.firstTrade:
        return 30;
      case MilestoneType.achievement:
        return 18;
      case MilestoneType.milestone:
        return 12;
    }
  }
}

/// Types of milestones that can be celebrated
enum MilestoneType {
  levelUp,
  winStreak,
  bigWin,
  firstTrade,
  achievement,
  milestone,
}

/// Helper widget to easily show milestone celebrations
class MilestoneOverlay extends StatefulWidget {
  final Widget child;
  final bool showCelebration;
  final MilestoneType milestoneType;
  final String title;
  final String subtitle;
  final String? customMessage;
  final VoidCallback? onComplete;

  const MilestoneOverlay({
    super.key,
    required this.child,
    this.showCelebration = false,
    this.milestoneType = MilestoneType.achievement,
    this.title = 'Congratulations!',
    this.subtitle = '',
    this.customMessage,
    this.onComplete,
  });

  @override
  State<MilestoneOverlay> createState() => _MilestoneOverlayState();
}

class _MilestoneOverlayState extends State<MilestoneOverlay> {
  bool _isShowingCelebration = false;

  @override
  void didUpdateWidget(MilestoneOverlay oldWidget) {
    super.didUpdateWidget(oldWidget);
    
    if (widget.showCelebration && !oldWidget.showCelebration) {
      _showCelebration();
    }
  }

  void _showCelebration() {
    setState(() {
      _isShowingCelebration = true;
    });
  }

  void _hideCelebration() {
    setState(() {
      _isShowingCelebration = false;
    });
    
    widget.onComplete?.call();
  }

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        widget.child,
        
        if (_isShowingCelebration)
          MilestoneCelebration(
            milestoneType: widget.milestoneType,
            title: widget.title,
            subtitle: widget.subtitle,
            customMessage: widget.customMessage,
            onComplete: _hideCelebration,
          ),
      ],
    );
  }
}

/// Utility class for creating milestone celebrations
class MilestoneUtils {
  /// Show a level up celebration
  static void showLevelUp(BuildContext context, int newLevel) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => MilestoneCelebration(
        milestoneType: MilestoneType.levelUp,
        title: 'Level Up!',
        subtitle: 'Welcome to Level $newLevel',
        customMessage: 'Your cosmic trading skills are evolving!',
        primaryColor: Colors.purple,
        secondaryColor: Colors.pink,
        onComplete: () => Navigator.of(context).pop(),
      ),
    );
  }

  /// Show a win streak celebration
  static void showWinStreak(BuildContext context, int streak) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => MilestoneCelebration(
        milestoneType: MilestoneType.winStreak,
        title: 'On Fire!',
        subtitle: '$streak Win Streak',
        customMessage: 'You\'re mastering the cosmic markets!',
        primaryColor: Colors.orange,
        secondaryColor: Colors.red,
        onComplete: () => Navigator.of(context).pop(),
      ),
    );
  }

  /// Show a big win celebration
  static void showBigWin(BuildContext context, double amount) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => MilestoneCelebration(
        milestoneType: MilestoneType.bigWin,
        title: 'Stellar Trade!',
        subtitle: '\$${amount.toStringAsFixed(2)} Profit',
        customMessage: 'The cosmic winds aligned perfectly!',
        primaryColor: Colors.green,
        secondaryColor: Colors.teal,
        onComplete: () => Navigator.of(context).pop(),
      ),
    );
  }

  /// Show first trade celebration
  static void showFirstTrade(BuildContext context) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => MilestoneCelebration(
        milestoneType: MilestoneType.firstTrade,
        title: 'First Trade!',
        subtitle: 'Welcome to the cosmic markets',
        customMessage: 'Every expert was once a beginner. Great start!',
        primaryColor: Colors.cyan,
        secondaryColor: Colors.blue,
        onComplete: () => Navigator.of(context).pop(),
      ),
    );
  }
}