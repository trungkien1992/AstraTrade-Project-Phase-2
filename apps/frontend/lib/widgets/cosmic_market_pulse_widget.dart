import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'dart:math' as math;
import '../theme/cosmic_theme.dart';
import '../utils/constants.dart';

/// Cosmic-themed market pulse widget showing trading data and stellar flux
/// Abstracts traditional trading charts into cosmic energy patterns
class CosmicMarketPulseWidget extends StatefulWidget {
  final String symbol;
  final double currentPrice;
  final double priceChange;
  final double priceChangePercent;
  final bool isLoading;

  const CosmicMarketPulseWidget({
    super.key,
    this.symbol = 'ETH-USD',
    this.currentPrice = 2500.0,
    this.priceChange = 125.50,
    this.priceChangePercent = 5.02,
    this.isLoading = false,
  });

  @override
  State<CosmicMarketPulseWidget> createState() =>
      _CosmicMarketPulseWidgetState();
}

class _CosmicMarketPulseWidgetState extends State<CosmicMarketPulseWidget>
    with TickerProviderStateMixin {
  late AnimationController _pulseController;
  late AnimationController _waveController;
  late Animation<double> _pulseAnimation;
  late Animation<double> _waveAnimation;

  @override
  void initState() {
    super.initState();

    // Pulse animation for price changes
    _pulseController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );

    _pulseAnimation = Tween<double>(begin: 0.8, end: 1.2).animate(
      CurvedAnimation(parent: _pulseController, curve: Curves.easeInOut),
    );

    // Wave animation for flux visualization
    _waveController = AnimationController(
      duration: const Duration(seconds: 3),
      vsync: this,
    )..repeat();

    _waveAnimation = Tween<double>(
      begin: 0.0,
      end: 2 * math.pi,
    ).animate(_waveController);

    // Start pulse when price changes
    if (widget.priceChange != 0) {
      _pulseController.forward().then((_) {
        _pulseController.reverse();
      });
    }
  }

  @override
  void didUpdateWidget(CosmicMarketPulseWidget oldWidget) {
    super.didUpdateWidget(oldWidget);

    // Trigger pulse on price change
    if (widget.priceChange != oldWidget.priceChange &&
        widget.priceChange != 0) {
      _pulseController.forward().then((_) {
        _pulseController.reverse();
      });
    }
  }

  @override
  void dispose() {
    _pulseController.dispose();
    _waveController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final isPositive = widget.priceChange >= 0;
    final fluxColor = isPositive ? CosmicTheme.accentCyan : Color(0xFFEF4444);

    if (widget.isLoading) {
      return _buildLoadingState();
    }

    return Container(
      padding: const EdgeInsets.all(AppConstants.paddingMedium),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            CosmicTheme.cosmicDarkGray,
            CosmicTheme.cosmicGray.withOpacity(0.8),
          ],
        ),
        borderRadius: BorderRadius.circular(AppConstants.borderRadius),
        border: Border.all(color: fluxColor.withOpacity(0.3), width: 1),
        boxShadow: [
          BoxShadow(
            color: fluxColor.withOpacity(0.2),
            blurRadius: 10,
            spreadRadius: 2,
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header with symbol and stellar flux indicator
          _buildHeader(fluxColor),

          const SizedBox(height: AppConstants.paddingMedium),

          // Stellar flux visualization
          _buildStellarFluxChart(fluxColor),

          const SizedBox(height: AppConstants.paddingMedium),

          // Price data
          _buildPriceData(fluxColor, isPositive),
        ],
      ),
    );
  }

  Widget _buildLoadingState() {
    return Container(
      padding: const EdgeInsets.all(AppConstants.paddingMedium),
      decoration: BoxDecoration(
        color: CosmicTheme.cosmicDarkGray,
        borderRadius: BorderRadius.circular(AppConstants.borderRadius),
        border: Border.all(
          color: CosmicTheme.primaryPurple.withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Column(
        children: [
          Row(
            children: [
              Container(
                width: 12,
                height: 12,
                decoration: const BoxDecoration(
                  shape: BoxShape.circle,
                  color: CosmicTheme.primaryPurple,
                ),
              ),
              const SizedBox(width: 8),
              Text(
                'Scanning Stellar Flux...',
                style: GoogleFonts.orbitron(
                  fontSize: 14,
                  color: CosmicTheme.starWhite.withOpacity(0.8),
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),

          const SizedBox(height: 16),

          LinearProgressIndicator(
            backgroundColor: CosmicTheme.cosmicGray,
            valueColor: AlwaysStoppedAnimation<Color>(CosmicTheme.accentCyan),
          ),
        ],
      ),
    );
  }

  Widget _buildHeader(Color fluxColor) {
    return Row(
      children: [
        // Stellar flux indicator
        AnimatedBuilder(
          animation: _pulseAnimation,
          builder: (context, child) {
            return Transform.scale(
              scale: _pulseAnimation.value,
              child: Container(
                width: 12,
                height: 12,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: fluxColor,
                  boxShadow: [
                    BoxShadow(
                      color: fluxColor.withOpacity(0.6),
                      blurRadius: 8,
                      spreadRadius: 2,
                    ),
                  ],
                ),
              ),
            );
          },
        ),

        const SizedBox(width: 8),

        // Symbol with cosmic terminology
        Text(
          '${widget.symbol} Stellar Flux',
          style: GoogleFonts.orbitron(
            fontSize: 16,
            color: CosmicTheme.starWhite,
            fontWeight: FontWeight.w600,
          ),
        ),

        const Spacer(),

        // Flux intensity indicator
        _buildFluxIntensity(),
      ],
    );
  }

  Widget _buildFluxIntensity() {
    final intensity = (widget.priceChangePercent.abs() / 10).clamp(0.0, 1.0);

    return Row(
      children: List.generate(5, (index) {
        final isActive = index < (intensity * 5).round();
        return Container(
          width: 4,
          height: 12,
          margin: const EdgeInsets.only(left: 2),
          decoration: BoxDecoration(
            color: isActive ? CosmicTheme.accentCyan : CosmicTheme.cosmicGray,
            borderRadius: BorderRadius.circular(2),
          ),
        );
      }),
    );
  }

  Widget _buildStellarFluxChart(Color fluxColor) {
    return Container(
      height: 80,
      width: double.infinity,
      child: AnimatedBuilder(
        animation: _waveAnimation,
        builder: (context, child) {
          return CustomPaint(
            painter: StellarFluxPainter(
              wavePhase: _waveAnimation.value,
              fluxColor: fluxColor,
              intensity: widget.priceChangePercent.abs() / 10,
            ),
            size: Size.infinite,
          );
        },
      ),
    );
  }

  Widget _buildPriceData(Color fluxColor, bool isPositive) {
    return Row(
      children: [
        // Current price (abstracted as "Quantum Energy")
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Quantum Energy',
                style: GoogleFonts.rajdhani(
                  fontSize: 12,
                  color: CosmicTheme.starWhite.withOpacity(0.6),
                  fontWeight: FontWeight.w500,
                ),
              ),
              Text(
                '${widget.currentPrice.toStringAsFixed(2)} QE',
                style: GoogleFonts.orbitron(
                  fontSize: 18,
                  color: CosmicTheme.starWhite,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ),

        // Price change (abstracted as "Flux Variance")
        Column(
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            Text(
              'Flux Variance',
              style: GoogleFonts.rajdhani(
                fontSize: 12,
                color: CosmicTheme.starWhite.withOpacity(0.6),
                fontWeight: FontWeight.w500,
              ),
            ),
            Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(
                  isPositive ? Icons.trending_up : Icons.trending_down,
                  color: fluxColor,
                  size: 16,
                ),
                const SizedBox(width: 4),
                Text(
                  '${isPositive ? '+' : ''}${widget.priceChangePercent.toStringAsFixed(2)}%',
                  style: GoogleFonts.orbitron(
                    fontSize: 14,
                    color: fluxColor,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
          ],
        ),
      ],
    );
  }
}

/// Custom painter for stellar flux wave visualization
class StellarFluxPainter extends CustomPainter {
  final double wavePhase;
  final Color fluxColor;
  final double intensity;

  StellarFluxPainter({
    required this.wavePhase,
    required this.fluxColor,
    required this.intensity,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = fluxColor.withOpacity(0.6)
      ..strokeWidth = 2
      ..style = PaintingStyle.stroke;

    final fillPaint = Paint()
      ..shader = LinearGradient(
        begin: Alignment.topCenter,
        end: Alignment.bottomCenter,
        colors: [
          fluxColor.withOpacity(0.3),
          fluxColor.withOpacity(0.1),
          Colors.transparent,
        ],
      ).createShader(Rect.fromLTWH(0, 0, size.width, size.height));

    final path = Path();
    final fillPath = Path();

    // Generate wave points
    const amplitude = 20.0;
    final frequency = 2 + (intensity * 3); // More volatile = higher frequency
    final baseY = size.height * 0.5;

    for (double x = 0; x <= size.width; x += 2) {
      final normalizedX = x / size.width;
      final y =
          baseY +
          math.sin((normalizedX * frequency * 2 * math.pi) + wavePhase) *
              amplitude *
              (1 + intensity);

      if (x == 0) {
        path.moveTo(x, y);
        fillPath.moveTo(x, size.height);
        fillPath.lineTo(x, y);
      } else {
        path.lineTo(x, y);
        fillPath.lineTo(x, y);
      }
    }

    // Close fill path
    fillPath.lineTo(size.width, size.height);
    fillPath.close();

    // Draw filled area first
    canvas.drawPath(fillPath, fillPaint);

    // Draw wave line
    canvas.drawPath(path, paint);

    // Add energy particles
    _drawEnergyParticles(canvas, size);
  }

  void _drawEnergyParticles(Canvas canvas, Size size) {
    final particlePaint = Paint()
      ..color = fluxColor.withOpacity(0.8)
      ..style = PaintingStyle.fill;

    final random = math.Random(42); // Deterministic for consistency

    for (int i = 0; i < (intensity * 10).round(); i++) {
      final x = random.nextDouble() * size.width;
      final y = random.nextDouble() * size.height;
      final radius = 1 + (random.nextDouble() * 2);

      canvas.drawCircle(Offset(x, y), radius, particlePaint);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}
