import 'package:flutter/material.dart';
import 'dart:math' as math;

/// Types of particle effects available
enum ParticleEffectType {
  burst,      // Explosion-style burst
  spiral,     // Spiral outward motion
  fountain,   // Fountain upward effect
  shimmer,    // Gentle shimmer effect
  confetti,   // Confetti celebration
  starField,  // Twinkling stars
}

/// Shape of individual particles
enum ParticleShape {
  circle,
  star,
  diamond,
  heart,
  lightning,
}

/// Enhanced cosmic particle effect for trade feedback and celebrations
/// Provides multiple effect types with visual satisfaction
class CosmicParticleEffect extends StatefulWidget {
  final bool isSuccess;
  final VoidCallback? onComplete;
  final Duration duration;
  final ParticleEffectType effectType;
  final int particleCount;
  final double intensity;

  const CosmicParticleEffect({
    super.key,
    required this.isSuccess,
    this.onComplete,
    this.duration = const Duration(milliseconds: 1500),
    this.effectType = ParticleEffectType.burst,
    this.particleCount = 8,
    this.intensity = 1.0,
  });

  @override
  State<CosmicParticleEffect> createState() => _CosmicParticleEffectState();
}

class _CosmicParticleEffectState extends State<CosmicParticleEffect>
    with TickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _fadeAnimation;
  late Animation<double> _scaleAnimation;
  late Animation<double> _rotationAnimation;

  final List<EnhancedParticleData> _particles = [];
  late int _particleCount;

  @override
  void initState() {
    super.initState();

    _particleCount = widget.particleCount;
    _controller = AnimationController(duration: widget.duration, vsync: this);

    _fadeAnimation = Tween<double>(begin: 1.0, end: 0.0).animate(
      CurvedAnimation(
        parent: _controller,
        curve: const Interval(0.7, 1.0, curve: Curves.easeOut),
      ),
    );

    _scaleAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _controller,
        curve: const Interval(0.0, 0.3, curve: Curves.elasticOut),
      ),
    );

    _rotationAnimation = Tween<double>(begin: 0.0, end: 2 * math.pi).animate(
      CurvedAnimation(
        parent: _controller,
        curve: Curves.linear,
      ),
    );

    _generateParticles();
    _startAnimation();
  }

  void _generateParticles() {
    final random = math.Random();
    
    for (int i = 0; i < _particleCount; i++) {
      switch (widget.effectType) {
        case ParticleEffectType.burst:
          _generateBurstParticle(random, i);
          break;
        case ParticleEffectType.spiral:
          _generateSpiralParticle(random, i);
          break;
        case ParticleEffectType.fountain:
          _generateFountainParticle(random, i);
          break;
        case ParticleEffectType.shimmer:
          _generateShimmerParticle(random, i);
          break;
        case ParticleEffectType.confetti:
          _generateConfettiParticle(random, i);
          break;
        case ParticleEffectType.starField:
          _generateStarParticle(random, i);
          break;
      }
    }
  }

  void _generateBurstParticle(math.Random random, int index) {
    final angle = (index / _particleCount) * 2 * math.pi;
    final distance = (40.0 + random.nextDouble() * 80.0) * widget.intensity;
    final colors = widget.isSuccess 
        ? [Colors.cyan, Colors.amber, Colors.green, Colors.white]
        : [Colors.red, Colors.orange, Colors.yellow, Colors.pink];

    _particles.add(
      EnhancedParticleData(
        angle: angle,
        distance: distance,
        size: (4.0 + random.nextDouble() * 8.0) * widget.intensity,
        delay: random.nextDouble() * 0.3,
        color: colors[random.nextInt(colors.length)],
        shape: ParticleShape.values[random.nextInt(ParticleShape.values.length)],
        rotationSpeed: 0.5 + random.nextDouble() * 2.0,
      ),
    );
  }

  void _generateSpiralParticle(math.Random random, int index) {
    final baseAngle = (index / _particleCount) * 2 * math.pi;
    final spiralOffset = (index / _particleCount) * 4 * math.pi;
    
    _particles.add(
      EnhancedParticleData(
        angle: baseAngle + spiralOffset,
        distance: 20.0 + index * 5.0,
        size: 3.0 + random.nextDouble() * 4.0,
        delay: index * 0.05,
        color: widget.isSuccess ? Colors.cyan : Colors.red,
        shape: ParticleShape.star,
        rotationSpeed: 1.0 + random.nextDouble(),
      ),
    );
  }

  void _generateFountainParticle(math.Random random, int index) {
    final angle = -math.pi / 2 + (random.nextDouble() - 0.5) * math.pi / 3;
    
    _particles.add(
      EnhancedParticleData(
        angle: angle,
        distance: 50.0 + random.nextDouble() * 100.0,
        size: 2.0 + random.nextDouble() * 6.0,
        delay: random.nextDouble() * 0.2,
        color: widget.isSuccess ? Colors.gold : Colors.orange,
        shape: ParticleShape.diamond,
        rotationSpeed: 0.5 + random.nextDouble(),
        yVelocity: -2.0 - random.nextDouble() * 3.0,
        xVelocity: (random.nextDouble() - 0.5) * 2.0,
      ),
    );
  }

  void _generateShimmerParticle(math.Random random, int index) {
    final angle = random.nextDouble() * 2 * math.pi;
    final distance = 10.0 + random.nextDouble() * 30.0;
    
    _particles.add(
      EnhancedParticleData(
        angle: angle,
        distance: distance,
        size: 1.0 + random.nextDouble() * 3.0,
        delay: random.nextDouble() * 0.8,
        color: Colors.white.withOpacity(0.3 + random.nextDouble() * 0.7),
        shape: ParticleShape.circle,
        rotationSpeed: 0.1 + random.nextDouble() * 0.3,
      ),
    );
  }

  void _generateConfettiParticle(math.Random random, int index) {
    final colors = [
      Colors.red, Colors.blue, Colors.green, Colors.yellow,
      Colors.purple, Colors.orange, Colors.pink, Colors.cyan,
    ];
    
    _particles.add(
      EnhancedParticleData(
        angle: random.nextDouble() * 2 * math.pi,
        distance: 30.0 + random.nextDouble() * 80.0,
        size: 3.0 + random.nextDouble() * 5.0,
        delay: random.nextDouble() * 0.5,
        color: colors[random.nextInt(colors.length)],
        shape: random.nextBool() ? ParticleShape.diamond : ParticleShape.heart,
        rotationSpeed: 2.0 + random.nextDouble() * 4.0,
        yVelocity: random.nextDouble() * 2.0,
        xVelocity: (random.nextDouble() - 0.5) * 4.0,
      ),
    );
  }

  void _generateStarParticle(math.Random random, int index) {
    final angle = random.nextDouble() * 2 * math.pi;
    final distance = random.nextDouble() * 150.0;
    
    _particles.add(
      EnhancedParticleData(
        angle: angle,
        distance: distance,
        size: 1.0 + random.nextDouble() * 4.0,
        delay: random.nextDouble() * 1.0,
        color: Colors.white.withOpacity(0.4 + random.nextDouble() * 0.6),
        shape: ParticleShape.star,
        rotationSpeed: 0.1 + random.nextDouble() * 0.5,
        life: 0.5 + random.nextDouble() * 0.5,
      ),
    );
  }

  void _startAnimation() {
    _controller.forward().then((_) {
      if (widget.onComplete != null) {
        widget.onComplete!();
      }
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return FadeTransition(
          opacity: _fadeAnimation,
          child: Transform.scale(
            scale: _scaleAnimation.value,
            child: SizedBox(
              width: 200,
              height: 200,
              child: CustomPaint(
                painter: ParticlePainter(
                  particles: _particles,
                  progress: _controller.value,
                  isSuccess: widget.isSuccess,
                ),
              ),
            ),
          ),
        );
      },
    );
  }
}

class EnhancedParticleData {
  final double angle;
  final double distance;
  final double size;
  final double delay;
  final Color color;
  final ParticleShape shape;
  final double rotationSpeed;
  final double yVelocity;
  final double xVelocity;
  final double life;

  EnhancedParticleData({
    required this.angle,
    required this.distance,
    required this.size,
    required this.delay,
    required this.color,
    this.shape = ParticleShape.circle,
    required this.rotationSpeed,
    this.yVelocity = 0.0,
    this.xVelocity = 0.0,
    this.life = 1.0,
  });
}

// Legacy support for existing code
class ParticleData extends EnhancedParticleData {
  ParticleData({
    required double angle,
    required double distance,
    required double size,
    required double delay,
  }) : super(
          angle: angle,
          distance: distance,
          size: size,
          delay: delay,
          color: Colors.cyan,
          rotationSpeed: 1.0,
        );
}

class ParticlePainter extends CustomPainter {
  final List<ParticleData> particles;
  final double progress;
  final bool isSuccess;

  ParticlePainter({
    required this.particles,
    required this.progress,
    required this.isSuccess,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);

    // Colors based on success/failure
    final colors = isSuccess
        ? [
            const Color(0xFFFFD700), // Gold
            const Color(0xFFFFA500), // Orange
            const Color(0xFFFFFFFF), // White
          ]
        : [
            const Color(0xFF00BFFF), // Deep Sky Blue
            const Color(0xFF87CEEB), // Sky Blue
            const Color(0xFFE0E0E0), // Light Gray
          ];

    for (int i = 0; i < particles.length; i++) {
      final particle = particles[i];
      final adjustedProgress = math
          .max(0.0, progress - particle.delay)
          .clamp(0.0, 1.0);

      if (adjustedProgress <= 0.0) continue;

      // Calculate particle position
      final currentDistance = particle.distance * adjustedProgress;
      final x = center.dx + math.cos(particle.angle) * currentDistance;
      final y = center.dy + math.sin(particle.angle) * currentDistance;

      // Calculate particle opacity and size
      final opacity = (1.0 - adjustedProgress).clamp(0.0, 1.0);
      final currentSize = particle.size * (1.0 - adjustedProgress * 0.3);

      // Choose color
      final colorIndex = i % colors.length;
      final color = colors[colorIndex].withOpacity(opacity);

      // Draw particle
      final paint = Paint()
        ..color = color
        ..style = PaintingStyle.fill;

      canvas.drawCircle(Offset(x, y), currentSize, paint);

      // Add glow effect for success particles
      if (isSuccess && opacity > 0.5) {
        final glowPaint = Paint()
          ..color = colors[colorIndex].withOpacity(opacity * 0.3)
          ..style = PaintingStyle.fill;

        canvas.drawCircle(Offset(x, y), currentSize * 2, glowPaint);
      }
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}

/// Overlay widget that can be used to show particles on top of other content
class CosmicParticleOverlay extends StatefulWidget {
  final Widget child;
  final bool showParticles;
  final bool isSuccess;
  final VoidCallback? onParticlesComplete;

  const CosmicParticleOverlay({
    super.key,
    required this.child,
    this.showParticles = false,
    this.isSuccess = true,
    this.onParticlesComplete,
  });

  @override
  State<CosmicParticleOverlay> createState() => _CosmicParticleOverlayState();
}

class _CosmicParticleOverlayState extends State<CosmicParticleOverlay> {
  bool _isShowingParticles = false;

  @override
  void didUpdateWidget(CosmicParticleOverlay oldWidget) {
    super.didUpdateWidget(oldWidget);

    if (widget.showParticles && !oldWidget.showParticles) {
      _showParticles();
    }
  }

  void _showParticles() {
    setState(() {
      _isShowingParticles = true;
    });

    // Auto-hide after animation completes
    Future.delayed(const Duration(milliseconds: 1500), () {
      if (mounted) {
        setState(() {
          _isShowingParticles = false;
        });

        if (widget.onParticlesComplete != null) {
          widget.onParticlesComplete!();
        }
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        widget.child,
        if (_isShowingParticles)
          Positioned.fill(
            child: Center(
              child: CosmicParticleEffect(
                isSuccess: widget.isSuccess,
                onComplete: () {
                  setState(() {
                    _isShowingParticles = false;
                  });

                  if (widget.onParticlesComplete != null) {
                    widget.onParticlesComplete!();
                  }
                },
              ),
            ),
          ),
      ],
    );
  }
}
