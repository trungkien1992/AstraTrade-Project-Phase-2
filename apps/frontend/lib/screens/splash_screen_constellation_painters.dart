import 'package:flutter/material.dart';
import 'dart:math' as math;

/// Milky Way painter for cosmic background
class MilkyWayPainter extends CustomPainter {
  final double animationValue;
  final double glowIntensity;
  
  MilkyWayPainter({
    required this.animationValue,
    required this.glowIntensity,
  });

  @override
  void paint(Canvas canvas, Size size) {
    // Create Milky Way band effect
    final center = Offset(size.width / 2, size.height / 2);
    
    // Main galactic band
    final bandPaint = Paint()
      ..shader = LinearGradient(
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
        colors: [
          const Color(0xFF7B2CBF).withOpacity(0.3 * glowIntensity),
          const Color(0xFF06B6D4).withOpacity(0.2 * glowIntensity),
          const Color(0xFF1A1A2E).withOpacity(0.1 * glowIntensity),
        ],
        stops: const [0.0, 0.5, 1.0],
      ).createShader(Rect.fromLTWH(0, 0, size.width, size.height))
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 40);
    
    // Draw curved band
    final path = Path();
    path.moveTo(0, size.height * 0.3);
    path.quadraticBezierTo(
      size.width * 0.5, 
      size.height * 0.2 + math.sin(animationValue * 2 * math.pi) * 10,
      size.width, 
      size.height * 0.4
    );
    path.lineTo(size.width, size.height * 0.5);
    path.quadraticBezierTo(
      size.width * 0.5, 
      size.height * 0.6 + math.sin(animationValue * 2 * math.pi) * 10,
      0, 
      size.height * 0.7
    );
    path.close();
    
    canvas.drawPath(path, bandPaint);
  }

  @override
  bool shouldRepaint(MilkyWayPainter oldDelegate) {
    return oldDelegate.animationValue != animationValue || 
           oldDelegate.glowIntensity != glowIntensity;
  }
}

/// Constellation starfield painter
class ConstellationStarFieldPainter extends CustomPainter {
  final double animationValue;
  static final List<ConstellationStar> _stars = _generateConstellationStars();
  
  ConstellationStarFieldPainter({required this.animationValue});
  
  static List<ConstellationStar> _generateConstellationStars() {
    final random = math.Random(123);
    return List.generate(200, (i) {
      final isInConstellation = i % 7 == 0; // Every 7th star is brighter
      return ConstellationStar(
        position: Offset(random.nextDouble(), random.nextDouble()),
        size: isInConstellation ? 2.0 + random.nextDouble() * 1.5 : 0.5 + random.nextDouble() * 1.0,
        twinklePhase: i.toDouble(),
        brightness: isInConstellation ? 0.8 + random.nextDouble() * 0.2 : 0.3 + random.nextDouble() * 0.5,
        color: isInConstellation 
            ? const Color(0xFFFFD700) 
            : const Color(0xFFFFFFFF),
      );
    });
  }

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..style = PaintingStyle.fill;
    
    for (final star in _stars) {
      final position = Offset(
        star.position.dx * size.width,
        star.position.dy * size.height,
      );
      
      final twinkle = star.brightness * 
        (0.3 + 0.7 * math.sin(animationValue * 3 * math.pi + star.twinklePhase));
      
      paint.color = star.color.withOpacity(twinkle * 0.8);
      canvas.drawCircle(position, star.size, paint);
      
      // Add subtle glow for brighter stars
      if (star.color == const Color(0xFFFFD700)) {
        final glowPaint = Paint()
          ..color = star.color.withOpacity(twinkle * 0.3)
          ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 4);
        
        canvas.drawCircle(position, star.size * 2, glowPaint);
      }
    }
  }

  @override
  bool shouldRepaint(ConstellationStarFieldPainter oldDelegate) {
    return oldDelegate.animationValue != animationValue;
  }
}

/// Constellation star data
class ConstellationStar {
  final Offset position;
  final double size;
  final double twinklePhase;
  final double brightness;
  final Color color;
  
  const ConstellationStar({
    required this.position,
    required this.size,
    required this.twinklePhase,
    required this.brightness,
    required this.color,
  });
}