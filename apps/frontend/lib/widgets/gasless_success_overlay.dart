import 'package:flutter/material.dart';
import 'dart:math' as math;
import 'dart:ui' as ui;
import 'package:google_fonts/google_fonts.dart';

class GaslessSuccessOverlay extends StatefulWidget {
  final String symbol;
  final double amount;
  final String direction;
  final VoidCallback onComplete;

  const GaslessSuccessOverlay({
    Key? key,
    required this.symbol,
    required this.amount,
    required this.direction,
    required this.onComplete,
  }) : super(key: key);

  @override
  State<GaslessSuccessOverlay> createState() => _GaslessSuccessOverlayState();
}

class _GaslessSuccessOverlayState extends State<GaslessSuccessOverlay>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;
  late Animation<double> _opacityAnimation;
  late Animation<double> _burstAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 2500),
      vsync: this,
    );

    _scaleAnimation = TweenSequence([
      TweenSequenceItem(tween: Tween(begin: 0.5, end: 1.2), weight: 30),
      TweenSequenceItem(tween: Tween(begin: 1.2, end: 1.0), weight: 20),
    ]).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.elasticOut,
    ));

    _opacityAnimation = TweenSequence([
      TweenSequenceItem(tween: Tween(begin: 0.0, end: 1.0), weight: 20),
      TweenSequenceItem(tween: Tween(begin: 1.0, end: 1.0), weight: 60),
      TweenSequenceItem(tween: Tween(begin: 1.0, end: 0.0), weight: 20),
    ]).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.easeInOut,
    ));

    _burstAnimation = Tween(begin: 0.0, end: 1.0).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.easeOut,
    ));

    _controller.forward();
    _controller.addStatusListener((status) {
      if (status == AnimationStatus.completed) {
        widget.onComplete();
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
    final directionText = widget.direction == 'ORBITAL_ASCENT' ? 'ORBITAL ASCENT' : 'GRAVITATIONAL DESCENT';
    final directionColor = widget.direction == 'ORBITAL_ASCENT' ? Colors.green : Colors.red;

    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return BackdropFilter(
          filter: ui.ImageFilter.blur(sigmaX: 10, sigmaY: 10),
          child: Container(
            color: Colors.black.withOpacity(0.7),
            child: Center(
              child: ScaleTransition(
                scale: _scaleAnimation,
                child: FadeTransition(
                  opacity: _opacityAnimation,
                  child: Container(
                    width: 280,
                    height: 280,
                    decoration: BoxDecoration(
                      gradient: RadialGradient(
                        colors: [
                          Colors.purple.withOpacity(0.8),
                          Colors.indigo.withOpacity(0.6),
                          Colors.transparent,
                        ],
                        stops: [0.1, 0.5, 1.0],
                      ),
                      shape: BoxShape.circle,
                    ),
                    child: Stack(
                      alignment: Alignment.center,
                      children: [
                        // Stellar burst particles
                        CustomPaint(
                          size: const Size(280, 280),
                          painter: StellarBurstPainter(
                            progress: _burstAnimation.value,
                            particleCount: 20,
                          ),
                        ),
                        
                        // Main content
                        Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            // Success icon
                            Container(
                              width: 80,
                              height: 80,
                              decoration: BoxDecoration(
                                shape: BoxShape.circle,
                                gradient: LinearGradient(
                                  colors: [Colors.purple.shade400, Colors.cyan.shade400],
                                  begin: Alignment.topLeft,
                                  end: Alignment.bottomRight,
                                ),
                                boxShadow: [
                                  BoxShadow(
                                    color: Colors.purple.withOpacity(0.5),
                                    blurRadius: 20,
                                    spreadRadius: 5,
                                  ),
                                ],
                              ),
                              child: const Icon(
                                Icons.check_circle,
                                size: 50,
                                color: Colors.white,
                              ),
                            ),
                            const SizedBox(height: 20),
                            
                            // Trade secured text
                            Text(
                              'TRADE SECURED',
                              style: GoogleFonts.orbitron(
                                fontSize: 24,
                                fontWeight: FontWeight.bold,
                                color: Colors.white,
                                letterSpacing: 2,
                              ),
                            ),
                            const SizedBox(height: 8),
                            
                            // Gasless badge
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                              decoration: BoxDecoration(
                                color: Colors.green.withOpacity(0.2),
                                borderRadius: BorderRadius.circular(12),
                                border: Border.all(
                                  color: Colors.green.withOpacity(0.5),
                                  width: 1,
                                ),
                              ),
                              child: Text(
                                'GASLESS SPONSORED',
                                style: GoogleFonts.rajdhani(
                                  fontSize: 12,
                                  color: Colors.green.shade200,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                            const SizedBox(height: 12),
                            
                            // Trade details
                            Text(
                              '$directionText',
                              style: GoogleFonts.rajdhani(
                                fontSize: 16,
                                color: directionColor,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            Text(
                              '${widget.symbol} \$${widget.amount.toStringAsFixed(2)}',
                              style: GoogleFonts.rajdhani(
                                fontSize: 14,
                                color: Colors.white70,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),
        );
      },
    );
  }
}

class StellarBurstPainter extends CustomPainter {
  final double progress;
  final int particleCount;

  StellarBurstPainter({
    required this.progress,
    required this.particleCount,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final maxRadius = size.width * 0.8;

    // Draw particles radiating outward
    for (int i = 0; i < particleCount; i++) {
      final angle = (i * 2 * math.pi) / particleCount;
      final particleProgress = progress * (1.0 - (i * 0.05)); // Staggered animation
      
      if (particleProgress <= 0) continue;
      
      final radius = maxRadius * particleProgress;
      final x = center.dx + math.cos(angle) * radius;
      final y = center.dy + math.sin(angle) * radius;
      
      final particleSize = 3.0 * (1.0 - particleProgress * 0.5);
      final opacity = (1.0 - particleProgress).clamp(0.0, 1.0);
      
      final paint = Paint()
        ..color = Colors.white.withOpacity(opacity)
        ..style = PaintingStyle.fill;
      
      // Star-shaped particle
      final path = Path();
      for (int j = 0; j < 4; j++) {
        final starAngle = (j * math.pi * 2) / 4;
        final starRadius = j % 2 == 0 ? particleSize : particleSize * 0.5;
        final starX = x + math.cos(starAngle) * starRadius;
        final starY = y + math.sin(starAngle) * starRadius;
        
        if (j == 0) {
          path.moveTo(starX, starY);
        } else {
          path.lineTo(starX, starY);
        }
      }
      path.close();
      
      canvas.drawPath(path, paint);
    }
  }

  @override
  bool shouldRepaint(StellarBurstPainter oldDelegate) {
    return oldDelegate.progress != progress;
  }
}