import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'dart:math' as math;
import '../theme/cosmic_theme.dart';
import '../utils/constants.dart';

/// Interactive 3D-styled planet widget for the main hub
/// Represents the user's cosmic trading ecosystem
class PlanetView extends StatefulWidget {
  final double size;
  final VoidCallback? onTap;
  final double evolutionProgress;
  final String biomeType;

  const PlanetView({
    super.key,
    this.size = 200.0,
    this.onTap,
    this.evolutionProgress = 0.5,
    this.biomeType = 'verdant',
  });

  @override
  State<PlanetView> createState() => _PlanetViewState();
}

class _PlanetViewState extends State<PlanetView> with TickerProviderStateMixin {
  late AnimationController _rotationController;
  late AnimationController _pulseController;
  late Animation<double> _pulseAnimation;

  @override
  void initState() {
    super.initState();

    // Slow rotation animation
    _rotationController = AnimationController(
      duration: const Duration(seconds: 20),
      vsync: this,
    )..repeat();

    // Pulse animation for energy
    _pulseController = AnimationController(
      duration: const Duration(seconds: 2),
      vsync: this,
    );

    _pulseAnimation = Tween<double>(begin: 0.95, end: 1.05).animate(
      CurvedAnimation(parent: _pulseController, curve: Curves.easeInOut),
    );

    _pulseController.repeat(reverse: true);
  }

  @override
  void dispose() {
    _rotationController.dispose();
    _pulseController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: widget.onTap,
      child: AnimatedBuilder(
        animation: Listenable.merge([_rotationController, _pulseAnimation]),
        builder: (context, child) {
          return Transform.scale(
            scale: _pulseAnimation.value,
            child: Transform.rotate(
              angle: _rotationController.value * 2 * math.pi,
              child: Container(
                width: widget.size,
                height: widget.size,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: _getPlanetGradient(),
                  boxShadow: [
                    BoxShadow(
                      color: CosmicTheme.primaryPurple.withOpacity(0.4),
                      blurRadius: 20,
                      spreadRadius: 5,
                    ),
                    BoxShadow(
                      color: CosmicTheme.accentCyan.withOpacity(0.2),
                      blurRadius: 40,
                      spreadRadius: 10,
                    ),
                  ],
                ),
                child: Stack(
                  children: [
                    // Planet surface details
                    _buildPlanetSurface(),

                    // Energy core
                    _buildEnergyCore(),

                    // Orbital rings
                    _buildOrbitalRings(),

                    // Evolution progress indicator
                    _buildEvolutionIndicator(),
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  /// Planet gradient based on biome type and evolution
  Gradient _getPlanetGradient() {
    switch (widget.biomeType) {
      case 'volcanic':
        return const RadialGradient(
          colors: [
            Color(0xFFEF4444), // Red core
            Color(0xFF991B1B), // Dark red
            Color(0xFF451A03), // Deep brown
          ],
        );
      case 'crystalline':
        return const RadialGradient(
          colors: [
            Color(0xFF06B6D4), // Cyan core
            Color(0xFF0891B2), // Blue
            Color(0xFF164E63), // Deep blue
          ],
        );
      case 'verdant':
      default:
        return RadialGradient(
          colors: [
            CosmicTheme.cosmicGold.withOpacity(0.8), // Golden core
            CosmicTheme.primaryPurple, // Purple middle
            CosmicTheme.deepPurple, // Deep purple edge
          ],
        );
    }
  }

  /// Planet surface with texture-like details
  Widget _buildPlanetSurface() {
    return Positioned.fill(
      child: ClipOval(
        child: Stack(
          children: [
            // Surface continents
            Positioned(
              top: widget.size * 0.2,
              left: widget.size * 0.1,
              child: Container(
                width: widget.size * 0.3,
                height: widget.size * 0.4,
                decoration: BoxDecoration(
                  color: CosmicTheme.starWhite.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(20),
                ),
              ),
            ),

            // Ocean areas
            Positioned(
              bottom: widget.size * 0.1,
              right: widget.size * 0.15,
              child: Container(
                width: widget.size * 0.4,
                height: widget.size * 0.3,
                decoration: BoxDecoration(
                  color: CosmicTheme.accentCyan.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(15),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// Central energy core that pulses
  Widget _buildEnergyCore() {
    return Center(
      child: Container(
        width: widget.size * 0.3,
        height: widget.size * 0.3,
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          gradient: RadialGradient(
            colors: [
              CosmicTheme.cosmicGold.withOpacity(0.8),
              CosmicTheme.accentCyan.withOpacity(0.6),
              Colors.transparent,
            ],
          ),
        ),
      ),
    );
  }

  /// Orbital rings around the planet
  Widget _buildOrbitalRings() {
    return Stack(
      children: [
        // Inner ring
        Center(
          child: Transform.rotate(
            angle: _rotationController.value * 4 * math.pi,
            child: Container(
              width: widget.size * 1.3,
              height: widget.size * 0.1,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(100),
                gradient: LinearGradient(
                  colors: [
                    Colors.transparent,
                    CosmicTheme.accentCyan.withOpacity(0.3),
                    Colors.transparent,
                  ],
                ),
              ),
            ),
          ),
        ),

        // Outer ring
        Center(
          child: Transform.rotate(
            angle: -_rotationController.value * 2 * math.pi,
            child: Container(
              width: widget.size * 1.6,
              height: widget.size * 0.05,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(100),
                gradient: LinearGradient(
                  colors: [
                    Colors.transparent,
                    CosmicTheme.primaryPurple.withOpacity(0.2),
                    Colors.transparent,
                  ],
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }

  /// Evolution progress indicator
  Widget _buildEvolutionIndicator() {
    return Positioned(
      bottom: 10,
      left: 0,
      right: 0,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Progress bar
          Container(
            width: widget.size * 0.8,
            height: 4,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(2),
              color: CosmicTheme.cosmicGray,
            ),
            child: FractionallySizedBox(
              alignment: Alignment.centerLeft,
              widthFactor: widget.evolutionProgress,
              child: Container(
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(2),
                  gradient: CosmicTheme.goldGradient,
                ),
              ),
            ),
          ),

          const SizedBox(height: 4),

          // Evolution percentage
          Text(
            '${(widget.evolutionProgress * 100).toInt()}% Evolved',
            style: GoogleFonts.rajdhani(
              fontSize: 10,
              color: CosmicTheme.starWhite.withOpacity(0.8),
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }
}

/// Simplified planet view for smaller spaces
class MiniPlanetView extends StatelessWidget {
  final double size;
  final String biomeType;

  const MiniPlanetView({
    super.key,
    this.size = 60.0,
    this.biomeType = 'verdant',
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        gradient: RadialGradient(
          colors: [
            CosmicTheme.cosmicGold.withOpacity(0.8),
            CosmicTheme.primaryPurple,
            CosmicTheme.deepPurple,
          ],
        ),
        boxShadow: [
          BoxShadow(
            color: CosmicTheme.primaryPurple.withOpacity(0.3),
            blurRadius: 8,
            spreadRadius: 2,
          ),
        ],
      ),
      child: Center(
        child: Container(
          width: size * 0.4,
          height: size * 0.4,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: CosmicTheme.cosmicGold.withOpacity(0.6),
          ),
        ),
      ),
    );
  }
}
