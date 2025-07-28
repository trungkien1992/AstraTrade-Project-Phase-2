import 'package:flutter/material.dart';
import 'dart:math' as math;

/// Custom page transitions for cosmic navigation
class CosmicPageTransitions {
  /// Stellar slide transition with cosmic effects
  static PageRouteBuilder stellarSlide({
    required Widget page,
    required RouteSettings settings,
    Duration duration = const Duration(milliseconds: 400),
    Curve curve = Curves.easeInOutCubic,
    Offset beginOffset = const Offset(1.0, 0.0),
  }) {
    return PageRouteBuilder(
      settings: settings,
      pageBuilder: (context, animation, secondaryAnimation) => page,
      transitionDuration: duration,
      reverseTransitionDuration: duration,
      transitionsBuilder: (context, animation, secondaryAnimation, child) {
        return SlideTransition(
          position: Tween<Offset>(
            begin: beginOffset,
            end: Offset.zero,
          ).animate(CurvedAnimation(
            parent: animation,
            curve: curve,
          )),
          child: FadeTransition(
            opacity: Tween<double>(
              begin: 0.0,
              end: 1.0,
            ).animate(CurvedAnimation(
              parent: animation,
              curve: Interval(0.0, 0.8, curve: curve),
            )),
            child: child,
          ),
        );
      },
    );
  }

  /// Cosmic scale transition with particle effects
  static PageRouteBuilder cosmicScale({
    required Widget page,
    required RouteSettings settings,
    Duration duration = const Duration(milliseconds: 350),
    Curve curve = Curves.easeInOutBack,
    Alignment alignment = Alignment.center,
  }) {
    return PageRouteBuilder(
      settings: settings,
      pageBuilder: (context, animation, secondaryAnimation) => page,
      transitionDuration: duration,
      reverseTransitionDuration: duration,
      transitionsBuilder: (context, animation, secondaryAnimation, child) {
        return ScaleTransition(
          alignment: alignment,
          scale: Tween<double>(
            begin: 0.8,
            end: 1.0,
          ).animate(CurvedAnimation(
            parent: animation,
            curve: curve,
          )),
          child: FadeTransition(
            opacity: Tween<double>(
              begin: 0.0,
              end: 1.0,
            ).animate(CurvedAnimation(
              parent: animation,
              curve: Interval(0.2, 1.0, curve: Curves.easeInOut),
            )),
            child: child,
          ),
        );
      },
    );
  }

  /// Quantum fade transition
  static PageRouteBuilder quantumFade({
    required Widget page,
    required RouteSettings settings,
    Duration duration = const Duration(milliseconds: 300),
    Curve curve = Curves.easeInOut,
  }) {
    return PageRouteBuilder(
      settings: settings,
      pageBuilder: (context, animation, secondaryAnimation) => page,
      transitionDuration: duration,
      reverseTransitionDuration: duration,
      transitionsBuilder: (context, animation, secondaryAnimation, child) {
        return FadeTransition(
          opacity: Tween<double>(
            begin: 0.0,
            end: 1.0,
          ).animate(CurvedAnimation(
            parent: animation,
            curve: curve,
          )),
          child: child,
        );
      },
    );
  }

  /// Orbital rotation transition
  static PageRouteBuilder orbitalRotation({
    required Widget page,
    required RouteSettings settings,
    Duration duration = const Duration(milliseconds: 600),
    Curve curve = Curves.easeInOutCubic,
    bool clockwise = true,
  }) {
    return PageRouteBuilder(
      settings: settings,
      pageBuilder: (context, animation, secondaryAnimation) => page,
      transitionDuration: duration,
      reverseTransitionDuration: duration,
      transitionsBuilder: (context, animation, secondaryAnimation, child) {
        return AnimatedBuilder(
          animation: animation,
          builder: (context, child) {
            final rotationValue = clockwise 
                ? animation.value * math.pi * 0.5
                : -animation.value * math.pi * 0.5;
            
            return Transform(
              alignment: Alignment.center,
              transform: Matrix4.identity()
                ..setEntry(3, 2, 0.001) // Perspective
                ..rotateY(rotationValue),
              child: Opacity(
                opacity: Curves.easeInOut.transform(animation.value),
                child: child,
              ),
            );
          },
          child: child,
        );
      },
    );
  }

  /// Stellar burst transition - for special navigation events
  static PageRouteBuilder stellarBurst({
    required Widget page,
    required RouteSettings settings,
    Duration duration = const Duration(milliseconds: 500),
    Curve curve = Curves.elasticOut,
    Color burstColor = const Color(0xFF7B2CBF),
  }) {
    return PageRouteBuilder(
      settings: settings,
      pageBuilder: (context, animation, secondaryAnimation) => page,
      transitionDuration: duration,
      reverseTransitionDuration: duration,
      transitionsBuilder: (context, animation, secondaryAnimation, child) {
        return Stack(
          children: [
            // Burst effect background
            AnimatedBuilder(
              animation: animation,
              builder: (context, child) {
                return Container(
                  decoration: BoxDecoration(
                    gradient: RadialGradient(
                      center: Alignment.center,
                      radius: animation.value * 2.0,
                      colors: [
                        burstColor.withOpacity(0.3 * (1 - animation.value)),
                        burstColor.withOpacity(0.1 * (1 - animation.value)),
                        Colors.transparent,
                      ],
                      stops: const [0.0, 0.7, 1.0],
                    ),
                  ),
                );
              },
            ),
            
            // Main page content
            ScaleTransition(
              scale: Tween<double>(
                begin: 0.3,
                end: 1.0,
              ).animate(CurvedAnimation(
                parent: animation,
                curve: curve,
              )),
              child: FadeTransition(
                opacity: Tween<double>(
                  begin: 0.0,
                  end: 1.0,
                ).animate(CurvedAnimation(
                  parent: animation,
                  curve: Interval(0.3, 1.0, curve: Curves.easeInOut),
                )),
                child: child,
              ),
            ),
          ],
        );
      },
    );
  }

  /// Navigation stack transitions based on destination
  static Widget buildStackTransition({
    required Widget child,
    required Animation<double> animation,
    required Animation<double> secondaryAnimation,
    required String? previousRoute,
    required String currentRoute,
  }) {
    // Determine transition based on route hierarchy
    final isForward = _isForwardNavigation(previousRoute, currentRoute);
    
    if (isForward) {
      return SlideTransition(
        position: Tween<Offset>(
          begin: const Offset(1.0, 0.0),
          end: Offset.zero,
        ).animate(CurvedAnimation(
          parent: animation,
          curve: Curves.easeInOutCubic,
        )),
        child: child,
      );
    } else {
      return SlideTransition(
        position: Tween<Offset>(
          begin: const Offset(-0.3, 0.0),
          end: Offset.zero,
        ).animate(CurvedAnimation(
          parent: animation,
          curve: Curves.easeInOutCubic,
        )),
        child: child,
      );
    }
  }

  /// Determine if navigation is forward or backward
  static bool _isForwardNavigation(String? from, String to) {
    const navigationHierarchy = [
      '/hub',
      '/forge',
      '/planet',
      '/constellations',
    ];
    
    if (from == null) return true;
    
    final fromIndex = navigationHierarchy.indexOf(from);
    final toIndex = navigationHierarchy.indexOf(to);
    
    if (fromIndex == -1 || toIndex == -1) return true;
    
    return toIndex > fromIndex;
  }
}

/// Custom transition delegate for nested navigation
class CosmicTransitionDelegate extends TransitionDelegate<void> {
  @override
  Iterable<RouteTransitionRecord> resolve({
    required List<RouteTransitionRecord> newPageRouteHistory,
    required Map<RouteTransitionRecord?, RouteTransitionRecord> locationToExitingPageRoute,
    required Map<RouteTransitionRecord?, List<RouteTransitionRecord>> pageRouteToPagelessRoutes,
  }) {
    final results = <RouteTransitionRecord>[];
    
    for (final pageRoute in newPageRouteHistory) {
      if (pageRoute.isWaitingForEnteringDecision) {
        pageRoute.markForAdd();
      }
      results.add(pageRoute);
    }
    
    for (final exitingPageRoute in locationToExitingPageRoute.values) {
      if (exitingPageRoute.isWaitingForExitingDecision) {
        exitingPageRoute.markForRemove();
        final pagelessRoutes = pageRouteToPagelessRoutes[exitingPageRoute];
        if (pagelessRoutes != null) {
          for (final pagelessRoute in pagelessRoutes) {
            pagelessRoute.markForRemove();
          }
        }
      }
      results.add(exitingPageRoute);
    }
    
    return results;
  }
}

/// Animation curves for cosmic transitions
class CosmicCurves {
  static const Curve stellarEase = Curves.easeInOutCubic;
  static const Curve quantumBounce = Curves.elasticOut;
  static const Curve cosmicPulse = Curves.easeInOutSine;
  static const Curve orbitalMotion = Curves.easeInOutQuart;
  
  /// Custom curve for stellar navigation
  static const Curve stellarNavigation = Cubic(0.25, 0.1, 0.25, 1.0);
  
  /// Custom curve for planet interactions
  static const Curve planetInteraction = Cubic(0.4, 0.0, 0.2, 1.0);
}