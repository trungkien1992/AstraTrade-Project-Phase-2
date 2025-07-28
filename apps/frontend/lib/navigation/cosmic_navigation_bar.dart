import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'dart:math' as math;

import 'cosmic_navigation_controller.dart';
import '../core/haptic_feedback.dart';

/// Custom cosmic-themed bottom navigation bar
class CosmicNavigationBar extends ConsumerStatefulWidget {
  const CosmicNavigationBar({super.key});

  @override
  ConsumerState<CosmicNavigationBar> createState() => _CosmicNavigationBarState();
}

class _CosmicNavigationBarState extends ConsumerState<CosmicNavigationBar>
    with TickerProviderStateMixin {
  late AnimationController _pulseController;
  late AnimationController _glowController;
  late Animation<double> _pulseAnimation;
  late Animation<double> _glowAnimation;

  @override
  void initState() {
    super.initState();
    
    _pulseController = AnimationController(
      duration: const Duration(milliseconds: 2000),
      vsync: this,
    )..repeat(reverse: true);
    
    _glowController = AnimationController(
      duration: const Duration(milliseconds: 3000),
      vsync: this,
    )..repeat();

    _pulseAnimation = Tween<double>(
      begin: 0.8,
      end: 1.2,
    ).animate(CurvedAnimation(
      parent: _pulseController,
      curve: Curves.easeInOut,
    ));

    _glowAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _glowController,
      curve: Curves.easeInOut,
    ));
  }

  @override
  void dispose() {
    _pulseController.dispose();
    _glowController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final navigationState = ref.watch(cosmicNavigationProvider);
    final currentDestination = navigationState.currentDestination;
    
    if (!navigationState.showNavigationBar) {
      return const SizedBox.shrink();
    }

    return Container(
      height: 88,
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [
            const Color(0xFF0A0A0F).withOpacity(0.95),
            const Color(0xFF1A1A2E).withOpacity(0.98),
          ],
        ),
        border: const Border(
          top: BorderSide(
            color: Color(0xFF7B2CBF),
            width: 0.5,
          ),
        ),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF7B2CBF).withOpacity(0.1),
            blurRadius: 20,
            spreadRadius: 0,
            offset: const Offset(0, -5),
          ),
        ],
      ),
      child: SafeArea(
        top: false,
        child: AnimatedBuilder(
          animation: Listenable.merge([_pulseAnimation, _glowAnimation]),
          builder: (context, child) {
            return Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: CosmicDestination.values.map((destination) {
                  final isActive = destination == currentDestination;
                  return _buildNavigationItem(
                    destination: destination,
                    isActive: isActive,
                    onTap: () {
                      CosmicHapticFeedback.selectionClick();
                      ref.read(cosmicNavigationProvider.notifier).navigateTo(destination);
                    },
                  );
                }).toList(),
              ),
            );
          },
        ),
      ),
    );
  }

  Widget _buildNavigationItem({
    required CosmicDestination destination,
    required bool isActive,
    required VoidCallback onTap,
  }) {
    return Expanded(
      child: Tooltip(
        message: destination.tooltip,
        child: GestureDetector(
          onTap: onTap,
          child: Container(
            padding: const EdgeInsets.symmetric(vertical: 7),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                // Icon with cosmic effects
                Container(
                  height: 32,
                  width: 32,
                  child: Stack(
                    alignment: Alignment.center,
                    children: [
                      // Glow effect for active item
                      if (isActive) ...[
                        Positioned.fill(
                          child: Container(
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              gradient: RadialGradient(
                                colors: [
                                  const Color(0xFF7B2CBF).withOpacity(
                                    0.6 * _glowAnimation.value,
                                  ),
                                  const Color(0xFF7B2CBF).withOpacity(
                                    0.2 * _glowAnimation.value,
                                  ),
                                  Colors.transparent,
                                ],
                                stops: const [0.3, 0.7, 1.0],
                              ),
                            ),
                          ),
                        ),
                        // Pulsing outer ring
                        Transform.scale(
                          scale: _pulseAnimation.value,
                          child: Container(
                            width: 28,
                            height: 28,
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              border: Border.all(
                                color: const Color(0xFF7B2CBF).withOpacity(0.4),
                                width: 1,
                              ),
                            ),
                          ),
                        ),
                      ],
                      
                      // Main icon
                      AnimatedContainer(
                        duration: const Duration(milliseconds: 200),
                        child: Icon(
                          isActive ? destination.activeIcon : destination.icon,
                          size: 22,
                          color: isActive 
                              ? const Color(0xFF7B2CBF)
                              : Colors.grey.shade400,
                        ),
                      ),
                    ],
                  ),
                ),
                
                const SizedBox(height: 6),
                
                // Label
                AnimatedDefaultTextStyle(
                  duration: const Duration(milliseconds: 200),
                  style: GoogleFonts.rajdhani(
                    fontSize: 11,
                    fontWeight: isActive ? FontWeight.bold : FontWeight.w500,
                    color: isActive 
                        ? const Color(0xFF7B2CBF)
                        : Colors.grey.shade500,
                  ),
                  child: Text(
                    destination.label,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                
                // Active indicator
                AnimatedContainer(
                  duration: const Duration(milliseconds: 200),
                  height: 2,
                  width: isActive ? 24 : 0,
                  margin: const EdgeInsets.only(top: 2),
                  decoration: BoxDecoration(
                    color: const Color(0xFF7B2CBF),
                    borderRadius: BorderRadius.circular(1),
                    boxShadow: isActive ? [
                      BoxShadow(
                        color: const Color(0xFF7B2CBF).withOpacity(0.5),
                        blurRadius: 4,
                        spreadRadius: 0,
                      ),
                    ] : null,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

/// Floating navigation button for special actions
class CosmicFloatingNavigationButton extends ConsumerStatefulWidget {
  final VoidCallback? onPressed;
  final IconData icon;
  final String label;
  final bool isVisible;

  const CosmicFloatingNavigationButton({
    super.key,
    this.onPressed,
    this.icon = Icons.add,
    this.label = 'Quick Action',
    this.isVisible = true,
  });

  @override
  ConsumerState<CosmicFloatingNavigationButton> createState() => 
      _CosmicFloatingNavigationButtonState();
}

class _CosmicFloatingNavigationButtonState 
    extends ConsumerState<CosmicFloatingNavigationButton>
    with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _scaleAnimation;
  late Animation<double> _rotationAnimation;

  @override
  void initState() {
    super.initState();
    
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    )..repeat();

    _scaleAnimation = Tween<double>(
      begin: 1.0,
      end: 1.1,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeInOut,
    ));

    _rotationAnimation = Tween<double>(
      begin: 0.0,
      end: 2 * math.pi,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.linear,
    ));
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (!widget.isVisible) {
      return const SizedBox.shrink();
    }

    return AnimatedBuilder(
      animation: _animationController,
      builder: (context, child) {
        return Transform.scale(
          scale: _scaleAnimation.value,
          child: FloatingActionButton(
            onPressed: () {
              CosmicHapticFeedback.mediumImpact();
              widget.onPressed?.call();
            },
            backgroundColor: const Color(0xFF7B2CBF),
            elevation: 8,
            child: Transform.rotate(
              angle: _rotationAnimation.value * 0.1, // Subtle rotation
              child: Icon(
                widget.icon,
                color: Colors.white,
                size: 28,
              ),
            ),
          ),
        );
      },
    );
  }
}