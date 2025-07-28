import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'dart:math' as math;

import '../utils/constants.dart';
// import 'splash_screen_constellation_painters.dart'; // TODO: Use if needed

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen>
    with SingleTickerProviderStateMixin {
  late AnimationController _masterController;
  
  late Animation<double> _fadeAnimation;
  late Animation<double> _scaleAnimation;
  late Animation<double> _particleAnimation;
  late Animation<double> _galaxyAnimation;
  late Animation<double> _glowAnimation;

  @override
  void initState() {
    super.initState();
    
    // Single master controller for all animations (performance optimization)
    _masterController = AnimationController(
      duration: const Duration(seconds: 4),
      vsync: this,
    );
    
    // Staggered animations using intervals
    _fadeAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _masterController,
      curve: const Interval(0.0, 0.25, curve: Curves.easeInOut),
    ));
    
    _scaleAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _masterController,
      curve: const Interval(0.075, 0.5, curve: Curves.elasticOut),
    ));
    
    _particleAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _masterController,
      curve: const Interval(0.2, 1.0, curve: Curves.linear),
    ));
    
    _galaxyAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _masterController,
      curve: Curves.linear,
    ));
    
    _glowAnimation = Tween<double>(
      begin: 0.6,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _masterController,
      curve: const Interval(0.3, 1.0, curve: Curves.easeInOut),
    ));

    // Start master animation
    _masterController.forward();

    // Navigate to home after 4 seconds
    Future.delayed(const Duration(seconds: 4), () {
      if (mounted) {
        // Navigate to main hub screen
        Navigator.of(context).pushReplacementNamed('/main_hub');
      }
    });
  }

  @override
  void dispose() {
    _masterController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0A0A),
      body: AnimatedBuilder(
        animation: _masterController,
        builder: (context, child) {
          return Stack(
            children: [
              // Enhanced layered cosmic background
              _buildEnhancedCosmicBackground(),
              
              // Main content
              Center(
                child: FadeTransition(
                  opacity: _fadeAnimation,
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      // Big Dipper Constellation Icon - DRAMATICALLY MOVED UP
                      Transform.translate(
                        offset: Offset(0, -80), // Move constellation WAY UP
                        child: RepaintBoundary(
                          child: Transform.scale(
                            scale: _scaleAnimation.value,
                            child: BigDipperConstellation(
                              size: 180.0,
                              animationValue: _scaleAnimation.value,
                              glowIntensity: _glowAnimation.value,
                            ),
                          ),
                        ),
                      ),
                      
                      SizedBox(height: 40 * _fadeAnimation.value),
                      
                      // Enhanced App Name with arc layout and glow
                      _buildEnhancedAppTitle(),
                      
                      const SizedBox(height: 12),
                      
                      // Enhanced tagline with glow
                      _buildEnhancedTagline(),
                      
                      const SizedBox(height: 60),
                      
                      // Stylized galaxy loader
                      RepaintBoundary(
                        child: _buildGalaxyLoader(),
                      ),
                      
                      const SizedBox(height: 20),
                      
                      // Enhanced loading text
                      _buildEnhancedLoadingText(),
                    ],
                  ),
                ),
              ),
              
              // Optimized floating particles
              RepaintBoundary(
                child: _buildOptimizedFloatingParticles(),
              ),
            ],
          );
        },
      ),
    );
  }
  
  Widget _buildEnhancedCosmicBackground() {
    return Stack(
      children: [
        // Layer 1: Deep space background (slowest parallax)
        Transform.translate(
          offset: Offset(_particleAnimation.value * -20, _particleAnimation.value * -10),
          child: Container(
            width: double.infinity,
            height: double.infinity,
            decoration: const BoxDecoration(
              gradient: RadialGradient(
                center: Alignment(-0.3, -0.5),
                radius: 2.5,
                colors: [
                  Color(0xFF1A1A2E),
                  Color(0xFF0F0F23),
                  Color(0xFF0A0A0F),
                  Color(0xFF000000),
                ],
                stops: [0.0, 0.3, 0.7, 1.0],
              ),
            ),
          ),
        ),
        
        // Layer 2: Nebulae effects (medium parallax)
        Transform.translate(
          offset: Offset(_particleAnimation.value * -50, _particleAnimation.value * -25),
          child: CustomPaint(
            painter: NebulaEffectsPainter(
              animationValue: _particleAnimation.value,
              glowIntensity: _glowAnimation.value,
            ),
            size: Size.infinite,
          ),
        ),
        
        // Layer 3: Enhanced starfield (fastest parallax)
        Transform.translate(
          offset: Offset(_particleAnimation.value * -80, _particleAnimation.value * -40),
          child: CustomPaint(
            painter: EnhancedStarFieldPainter(
              animationValue: _particleAnimation.value,
            ),
            size: Size.infinite,
          ),
        ),
      ],
    );
  }
  
  Widget _buildGalaxyLoader() {
    return SizedBox(
      width: 60,
      height: 60,
      child: CustomPaint(
        painter: GalaxyLoaderPainter(
          rotationValue: _galaxyAnimation.value,
          pulseValue: _glowAnimation.value,
        ),
      ),
    );
  }
  
  Widget _buildOptimizedFloatingParticles() {
    return CustomPaint(
      painter: OptimizedFloatingParticlesPainter(
        animationValue: _particleAnimation.value,
        screenSize: MediaQuery.of(context).size,
      ),
      size: Size.infinite,
    );
  }
  
  Widget _buildEnhancedAppTitle() {
    return ShaderMask(
      shaderCallback: (bounds) => const LinearGradient(
        colors: [
          Color(0xFF7B2CBF),
          Color(0xFF06B6D4),
          Color(0xFFFFD700),
        ],
      ).createShader(bounds),
      child: Text(
        AppConstants.appName,
        style: GoogleFonts.orbitron(
          fontSize: 38,
          fontWeight: FontWeight.w900,
          color: Colors.white,
          letterSpacing: 4,
        ),
      ),
    );
  }
  
  Widget _buildEnhancedTagline() {
    return Text(
      AppConstants.cosmicSubtitle,
      style: GoogleFonts.rajdhani(
        fontSize: 20,
        color: const Color(0xFF06B6D4),
        letterSpacing: 2,
        fontWeight: FontWeight.w600,
        shadows: [
          Shadow(
            color: const Color(0xFF06B6D4).withOpacity(0.8),
            blurRadius: 10,
          ),
        ],
      ),
      textAlign: TextAlign.center,
    );
  }
  
  Widget _buildEnhancedLoadingText() {
    return Text(
      AppConstants.cosmicLoadingMessage,
      style: GoogleFonts.roboto(
        fontSize: 15,
        color: Colors.white70,
        letterSpacing: 1,
        shadows: [
          Shadow(
            color: Colors.white.withOpacity(0.5),
            blurRadius: 5,
          ),
        ],
      ),
    );
  }
}

/// Enhanced starfield painter with better performance
class EnhancedStarFieldPainter extends CustomPainter {
  final double animationValue;
  static final List<ConstellationStarData> _stars = _generateStars();
  
  EnhancedStarFieldPainter({required this.animationValue});

  static List<ConstellationStarData> _generateStars() {
    final random = math.Random(123);
    return List.generate(120, (i) => ConstellationStarData(
      position: Offset(random.nextDouble(), random.nextDouble()),
      size: 0.8 + random.nextDouble() * 3.0,
      brightness: 0.2 + random.nextDouble() * 0.8,
    ));
  }

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..style = PaintingStyle.fill;
    
    for (int i = 0; i < _stars.length; i++) {
      final star = _stars[i];
      final position = Offset(
        star.position.dx * size.width,
        star.position.dy * size.height,
      );
      
      final twinkle = star.brightness * 
        (0.5 + 0.5 * math.sin(animationValue * 2 * math.pi + i.toDouble()));
      
      paint.color = Colors.white.withOpacity((twinkle * 0.7).clamp(0.0, 1.0));
      canvas.drawCircle(position, star.size, paint);
    }
  }

  @override
  bool shouldRepaint(EnhancedStarFieldPainter oldDelegate) {
    return oldDelegate.animationValue != animationValue;
  }
}

/// Data class for star properties
class ConstellationStarData {
  final Offset position;
  final double size;
  final double brightness;
  
  const ConstellationStarData({
    required this.position,
    required this.size,
    required this.brightness,
  });
}

/// Nebula effects painter for atmospheric depth
class NebulaEffectsPainter extends CustomPainter {
  final double animationValue;
  final double glowIntensity;
  
  NebulaEffectsPainter({
    required this.animationValue,
    required this.glowIntensity,
  });

  @override
  void paint(Canvas canvas, Size size) {
    // Draw multiple nebula blobs for atmospheric depth
    
    // Nebula blob 1 - Purple
    _drawNebulaBlob(
      canvas,
      Offset(size.width * 0.2, size.height * 0.3),
      size.width * 0.4,
      const Color(0xFF7B2CBF).withOpacity(0.15 * glowIntensity),
      animationValue * 0.5,
    );
    
    // Nebula blob 2 - Cyan
    _drawNebulaBlob(
      canvas,
      Offset(size.width * 0.7, size.height * 0.6),
      size.width * 0.35,
      const Color(0xFF06B6D4).withOpacity(0.12 * glowIntensity),
      animationValue * 0.3,
    );
    
    // Nebula blob 3 - Deep purple
    _drawNebulaBlob(
      canvas,
      Offset(size.width * 0.4, size.height * 0.8),
      size.width * 0.3,
      const Color(0xFF3B82F6).withOpacity(0.1 * glowIntensity),
      animationValue * 0.7,
    );
  }
  
  void _drawNebulaBlob(Canvas canvas, Offset center, double radius, Color color, double animationOffset) {
    final paint = Paint()
      ..color = color
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 80)
      ..style = PaintingStyle.fill;
    
    // Animate nebula position slightly
    final animatedCenter = center + Offset(
      math.sin(animationOffset * 2 * math.pi) * 20,
      math.cos(animationOffset * 2 * math.pi) * 15,
    );
    
    canvas.drawCircle(animatedCenter, radius, paint);
  }

  @override
  bool shouldRepaint(NebulaEffectsPainter oldDelegate) {
    return oldDelegate.animationValue != animationValue || 
           oldDelegate.glowIntensity != glowIntensity;
  }
}

/// Optimized floating particles painter
class OptimizedFloatingParticlesPainter extends CustomPainter {
  final double animationValue;
  final Size screenSize;
  static final List<FloatingParticle> _particles = _generateParticles();
  
  OptimizedFloatingParticlesPainter({
    required this.animationValue,
    required this.screenSize,
  });
  
  static List<FloatingParticle> _generateParticles() {
    final random = math.Random(42);
    return List.generate(20, (i) => FloatingParticle(
      initialX: random.nextDouble(),
      initialY: random.nextDouble(),
      size: 1.5 + random.nextDouble() * 3.5,
      colorIndex: i % 3,
      speed: 0.3 + random.nextDouble() * 0.7,
    ));
  }

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..style = PaintingStyle.fill;
    
    for (final particle in _particles) {
      final x = particle.initialX * size.width;
      final y = (particle.initialY * size.height - (animationValue * particle.speed * 300)) % size.height;
      final opacity = ((1.0 - (animationValue * 0.7)) * 0.8).clamp(0.0, 1.0);
      
      if (opacity <= 0) continue;
      
      final color = [
        const Color(0xFF7B2CBF),
        const Color(0xFF06B6D4),
        const Color(0xFFFFD700),
      ][particle.colorIndex];
      
      paint.color = color.withOpacity(opacity);
      canvas.drawCircle(Offset(x, y), particle.size, paint);
    }
  }

  @override
  bool shouldRepaint(OptimizedFloatingParticlesPainter oldDelegate) {
    return oldDelegate.animationValue != animationValue;
  }
}

/// Data class for floating particles
class FloatingParticle {
  final double initialX;
  final double initialY;
  final double size;
  final int colorIndex;
  final double speed;
  
  const FloatingParticle({
    required this.initialX,
    required this.initialY,
    required this.size,
    required this.colorIndex,
    required this.speed,
  });
}

/// Galaxy loader painter with geometric design
class GalaxyLoaderPainter extends CustomPainter {
  final double rotationValue;
  final double pulseValue;
  
  GalaxyLoaderPainter({
    required this.rotationValue,
    required this.pulseValue,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width * 0.4;
    
    // Draw spiral galaxy arms
    _drawSpiralArms(canvas, center, radius);
    
    // Draw pulsing core
    _drawPulsingCore(canvas, center, radius * 0.3);
  }
  
  void _drawSpiralArms(Canvas canvas, Offset center, double radius) {
    final paint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.0
      ..strokeCap = StrokeCap.round;
    
    // Draw 3 spiral arms
    for (int arm = 0; arm < 3; arm++) {
      final armOffset = (arm * 2 * math.pi / 3) + (rotationValue * 2 * math.pi);
      final path = Path();
      
      bool isFirstPoint = true;
      for (double t = 0; t < 4 * math.pi; t += 0.1) {
        final r = radius * (0.1 + 0.9 * t / (4 * math.pi));
        final angle = armOffset + t;
        final x = center.dx + r * math.cos(angle);
        final y = center.dy + r * math.sin(angle);
        
        if (isFirstPoint) {
          path.moveTo(x, y);
          isFirstPoint = false;
        } else {
          path.lineTo(x, y);
        }
      }
      
      // Gradient color for spiral arms
      paint.color = const Color(0xFF06B6D4).withOpacity(0.6);
      canvas.drawPath(path, paint);
    }
  }
  
  void _drawPulsingCore(Canvas canvas, Offset center, double coreRadius) {
    // Alternate between cyan and gold based on pulse
    final coreColor = Color.lerp(
      const Color(0xFF06B6D4), // Cyan
      const Color(0xFFFFD700), // Gold
      pulseValue,
    )!;
    
    // Outer glow
    final glowPaint = Paint()
      ..color = coreColor.withOpacity(0.3 * pulseValue)
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 15)
      ..style = PaintingStyle.fill;
    
    canvas.drawCircle(center, coreRadius * 2, glowPaint);
    
    // Core gradient
    final corePaint = Paint()
      ..shader = RadialGradient(
        colors: [
          Colors.white,
          coreColor,
          coreColor.withOpacity(0.8),
        ],
        stops: const [0.0, 0.6, 1.0],
      ).createShader(Rect.fromCircle(center: center, radius: coreRadius));
    
    canvas.drawCircle(center, coreRadius * (0.8 + 0.2 * pulseValue), corePaint);
  }

  @override
  bool shouldRepaint(GalaxyLoaderPainter oldDelegate) {
    return oldDelegate.rotationValue != rotationValue || 
           oldDelegate.pulseValue != pulseValue;
  }
}

/// Big Dipper constellation widget
class BigDipperConstellation extends StatelessWidget {
  final double size;
  final double animationValue;
  final double glowIntensity;
  
  const BigDipperConstellation({
    super.key,
    required this.size,
    required this.animationValue,
    required this.glowIntensity,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: size,
      height: size,
      child: CustomPaint(
        painter: BigDipperPainter(
          animationValue: animationValue,
          glowIntensity: glowIntensity,
        ),
      ),
    );
  }
}

/// Custom painter for the Big Dipper constellation
class BigDipperPainter extends CustomPainter {
  final double animationValue;
  final double glowIntensity;
  static final List<ConstellationStarData> _bigDipperStars = _generateBigDipperStars();
  
  BigDipperPainter({
    required this.animationValue,
    required this.glowIntensity,
  });
  
  static List<ConstellationStarData> _generateBigDipperStars() {
    // Big Dipper constellation coordinates (normalized 0-1) - MOVED UP SIGNIFICANTLY
    return [
      // Handle stars (4 stars forming the dipper bowl) - ALL MOVED UP
      ConstellationStarData(
        position: const Offset(0.2, 0.15), // WAS 0.3
        size: 12.0,
        brightness: 1.0,
      ),
      ConstellationStarData(
        position: const Offset(0.35, 0.1), // WAS 0.25
        size: 10.0,
        brightness: 0.9,
      ),
      ConstellationStarData(
        position: const Offset(0.5, 0.2), // WAS 0.35
        size: 11.0,
        brightness: 0.95,
      ),
      ConstellationStarData(
        position: const Offset(0.65, 0.15), // WAS 0.3
        size: 9.0,
        brightness: 0.85,
      ),
      // Handle stars (3 stars forming the dipper handle) - ALL MOVED UP
      ConstellationStarData(
        position: const Offset(0.75, 0.3), // WAS 0.45
        size: 10.0,
        brightness: 0.9,
      ),
      ConstellationStarData(
        position: const Offset(0.85, 0.45), // WAS 0.6
        size: 8.0,
        brightness: 0.8,
      ),
      ConstellationStarData(
        position: const Offset(0.95, 0.6), // WAS 0.75
        size: 7.0,
        brightness: 0.75,
      ),
    ];
  }

  @override
  void paint(Canvas canvas, Size size) {
    // Draw cosmic nebula background
    _drawCosmicNebula(canvas, size);
    
    // Draw constellation connections
    _drawConstellationLines(canvas, size);
    
    // Draw Big Dipper stars with staggered reveal
    _drawConstellationStars(canvas, size);
    
    // Draw trading symbols overlay
    _drawTradingSymbols(canvas, size);
  }
  
  void _drawCosmicNebula(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    
    // Deep space nebula background
    final nebulaPaint = Paint()
      ..shader = RadialGradient(
        center: const Alignment(-0.2, -0.3),
        radius: 1.8,
        colors: [
          const Color(0xFF1A1A2E).withOpacity(0.9),
          const Color(0xFF16213E).withOpacity(0.7),
          const Color(0xFF0F3460).withOpacity(0.5),
          const Color(0xFF0A0A0A).withOpacity(0.3),
        ],
        stops: const [0.0, 0.4, 0.7, 1.0],
      ).createShader(Rect.fromCircle(center: center, radius: size.width * 0.8))
      ..style = PaintingStyle.fill;
    
    canvas.drawCircle(center, size.width * 0.5, nebulaPaint);
    
    // Aurora-like effect
    final auroraPaint = Paint()
      ..shader = LinearGradient(
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
        colors: [
          const Color(0xFF06B6D4).withOpacity(0.2 * glowIntensity),
          const Color(0xFF7B2CBF).withOpacity(0.15 * glowIntensity),
          const Color(0xFFFFD700).withOpacity(0.1 * glowIntensity),
        ],
      ).createShader(Rect.fromLTWH(0, 0, size.width, size.height));
    
    canvas.drawRect(Rect.fromLTWH(0, 0, size.width, size.height), auroraPaint);
  }
  
  void _drawConstellationLines(Canvas canvas, Size size) {
    if (animationValue < 0.2) return;
    
    final linePaint = Paint()
      ..color = const Color(0xFF06B6D4).withOpacity(0.4 * (animationValue - 0.2) / 0.8)
      ..strokeWidth = 1.5
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;
    
    // Connect Big Dipper stars in sequence
    final path = Path();
    bool isFirst = true;
    
    for (int i = 0; i < _bigDipperStars.length; i++) {
      final star = _bigDipperStars[i];
      final position = Offset(star.position.dx * size.width, star.position.dy * size.height);
      
      if (isFirst) {
        path.moveTo(position.dx, position.dy);
        isFirst = false;
      } else {
        path.lineTo(position.dx, position.dy);
      }
    }
    
    canvas.drawPath(path, linePaint);
  }
  
  void _drawConstellationStars(Canvas canvas, Size size) {
    for (int i = 0; i < _bigDipperStars.length; i++) {
      final starReveal = ((animationValue - (i * 0.1)) / 0.9).clamp(0.0, 1.0);
      if (starReveal <= 0) continue;
      
      final star = _bigDipperStars[i];
      final position = Offset(star.position.dx * size.width, star.position.dy * size.height);
      
      // Star glow
      final glowPaint = Paint()
        ..color = const Color(0xFFFFD700).withOpacity(0.6 * glowIntensity * starReveal)
        ..maskFilter = MaskFilter.blur(BlurStyle.normal, star.size * 1.5)
        ..style = PaintingStyle.fill;
      
      canvas.drawCircle(position, star.size * 1.5, glowPaint);
      
      // Star core
      final starPaint = Paint()
        ..color = Colors.white.withOpacity(starReveal)
        ..style = PaintingStyle.fill;
      
      canvas.drawCircle(position, star.size * 0.7 * starReveal, starPaint);
      
      // Star inner core
      final innerPaint = Paint()
        ..color = const Color(0xFFFFD700).withOpacity(starReveal)
        ..style = PaintingStyle.fill;
      
      canvas.drawCircle(position, star.size * 0.3 * starReveal, innerPaint);
    }
  }
  
  void _drawTradingSymbols(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    
    // Trading constellation overlay
    final textPainter = TextPainter(
      text: TextSpan(
        text: '↗',
        style: TextStyle(
          color: const Color(0xFF06B6D4).withOpacity(0.8 * animationValue),
          fontSize: size.width * 0.12,
          fontWeight: FontWeight.bold,
          shadows: [
            Shadow(
              color: const Color(0xFF06B6D4).withOpacity(glowIntensity * 0.5),
              blurRadius: 8,
            ),
          ],
        ),
      ),
      textDirection: TextDirection.ltr,
    );
    
    textPainter.layout();
    textPainter.paint(
      canvas,
      Offset(
        center.dx - textPainter.width / 2,
        center.dy - textPainter.height / 2,
      ),
    );
  }

  @override
  bool shouldRepaint(BigDipperPainter oldDelegate) {
    return oldDelegate.animationValue != animationValue || 
           oldDelegate.glowIntensity != glowIntensity;
  }
}

