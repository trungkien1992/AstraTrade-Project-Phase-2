import 'package:flutter/material.dart';
import 'dart:math' as math;

/// Custom widget that recreates the official Starknet logo
class StarknetLogo extends StatelessWidget {
  final double size;
  final Color? backgroundColor;

  const StarknetLogo({super.key, this.size = 24, this.backgroundColor});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        color: backgroundColor ?? const Color(0xFF2D1B3D), // Starknet dark blue
        shape: BoxShape.circle,
      ),
      child: CustomPaint(
        painter: _StarknetLogoPainter(),
        size: Size(size, size),
      ),
    );
  }
}

class _StarknetLogoPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width / 2;

    // Create the main flowing shape (white with pink gradient)
    final path = Path();

    // Start from the left side, create a flowing S-like curve
    final startX = radius * 0.3;
    final startY = radius * 0.8;

    path.moveTo(startX, startY);

    // Create the flowing curve using quadratic bezier curves
    path.quadraticBezierTo(
      radius * 0.6,
      radius * 0.2, // Control point
      radius * 1.4,
      radius * 0.6, // End point
    );

    path.quadraticBezierTo(
      radius * 1.7,
      radius * 0.8, // Control point
      radius * 1.8,
      radius * 1.2, // End point (extends beyond circle)
    );

    // Create the inner curve
    path.quadraticBezierTo(
      radius * 1.6,
      radius * 1.0, // Control point
      radius * 1.2,
      radius * 1.1, // End point
    );

    path.quadraticBezierTo(
      radius * 0.8,
      radius * 1.2, // Control point
      radius * 0.5,
      radius * 0.9, // End point
    );

    path.close();

    // Create gradient paint for the main shape
    final gradient = LinearGradient(
      begin: Alignment.topLeft,
      end: Alignment.bottomRight,
      colors: [
        Colors.white,
        const Color(0xFFFF9999), // Light pink
        const Color(0xFFFF7777), // Medium pink
      ],
    );

    final paint = Paint()
      ..shader = gradient.createShader(
        Rect.fromCircle(center: center, radius: radius),
      )
      ..style = PaintingStyle.fill;

    canvas.save();
    canvas.clipRRect(
      RRect.fromRectAndRadius(
        Rect.fromCircle(center: center, radius: radius),
        Radius.circular(radius),
      ),
    );

    canvas.drawPath(path, paint);

    // Add the star in the upper left
    _drawStar(
      canvas,
      Offset(radius * 0.6, radius * 0.4),
      radius * 0.15,
      Colors.white,
    );

    // Add the small circle in the lower right
    final circlePaint = Paint()
      ..color = const Color(0xFFFF7777)
      ..style = PaintingStyle.fill;

    canvas.drawCircle(
      Offset(radius * 1.4, radius * 1.4),
      radius * 0.12,
      circlePaint,
    );

    canvas.restore();
  }

  void _drawStar(Canvas canvas, Offset center, double radius, Color color) {
    final paint = Paint()
      ..color = color
      ..style = PaintingStyle.fill;

    final path = Path();
    const points = 4;

    for (int i = 0; i < points * 2; i++) {
      final angle = (i * math.pi) / points;
      final r = i.isEven ? radius : radius * 0.4;
      final x = center.dx + math.cos(angle) * r;
      final y = center.dy + math.sin(angle) * r;

      if (i == 0) {
        path.moveTo(x, y);
      } else {
        path.lineTo(x, y);
      }
    }

    path.close();
    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
