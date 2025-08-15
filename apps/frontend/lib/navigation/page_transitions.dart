import 'package:flutter/material.dart';

/// Custom page route transitions for smooth navigation
class CustomPageTransitions {
  /// Slide transition from right to left
  static PageRouteBuilder slideFromRight({
    required Widget child,
    Duration duration = const Duration(milliseconds: 300),
  }) {
    return PageRouteBuilder(
      pageBuilder: (context, animation, secondaryAnimation) => child,
      transitionDuration: duration,
      reverseTransitionDuration: duration,
      transitionsBuilder: (context, animation, secondaryAnimation, child) {
        const begin = Offset(1.0, 0.0);
        const end = Offset.zero;
        const curve = Curves.easeInOutCubic;

        var tween = Tween(begin: begin, end: end).chain(
          CurveTween(curve: curve),
        );

        return SlideTransition(
          position: animation.drive(tween),
          child: child,
        );
      },
    );
  }

  /// Slide transition from bottom to top
  static PageRouteBuilder slideFromBottom({
    required Widget child,
    Duration duration = const Duration(milliseconds: 300),
  }) {
    return PageRouteBuilder(
      pageBuilder: (context, animation, secondaryAnimation) => child,
      transitionDuration: duration,
      reverseTransitionDuration: duration,
      transitionsBuilder: (context, animation, secondaryAnimation, child) {
        const begin = Offset(0.0, 1.0);
        const end = Offset.zero;
        const curve = Curves.easeInOutCubic;

        var tween = Tween(begin: begin, end: end).chain(
          CurveTween(curve: curve),
        );

        return SlideTransition(
          position: animation.drive(tween),
          child: child,
        );
      },
    );
  }

  /// Fade transition with scale
  static PageRouteBuilder fadeWithScale({
    required Widget child,
    Duration duration = const Duration(milliseconds: 400),
  }) {
    return PageRouteBuilder(
      pageBuilder: (context, animation, secondaryAnimation) => child,
      transitionDuration: duration,
      reverseTransitionDuration: duration,
      transitionsBuilder: (context, animation, secondaryAnimation, child) {
        const curve = Curves.easeInOutCubic;

        var fadeAnimation = Tween(begin: 0.0, end: 1.0).animate(
          CurvedAnimation(parent: animation, curve: curve),
        );

        var scaleAnimation = Tween(begin: 0.95, end: 1.0).animate(
          CurvedAnimation(parent: animation, curve: curve),
        );

        return FadeTransition(
          opacity: fadeAnimation,
          child: ScaleTransition(
            scale: scaleAnimation,
            child: child,
          ),
        );
      },
    );
  }

  /// Cosmic-themed transition with rotation and scale
  static PageRouteBuilder cosmicTransition({
    required Widget child,
    Duration duration = const Duration(milliseconds: 600),
  }) {
    return PageRouteBuilder(
      pageBuilder: (context, animation, secondaryAnimation) => child,
      transitionDuration: duration,
      reverseTransitionDuration: duration,
      transitionsBuilder: (context, animation, secondaryAnimation, child) {
        const curve = Curves.elasticOut;

        var fadeAnimation = Tween(begin: 0.0, end: 1.0).animate(
          CurvedAnimation(
            parent: animation,
            curve: const Interval(0.0, 0.8, curve: Curves.easeInOut),
          ),
        );

        var scaleAnimation = Tween(begin: 0.5, end: 1.0).animate(
          CurvedAnimation(parent: animation, curve: curve),
        );

        var rotationAnimation = Tween(begin: 0.1, end: 0.0).animate(
          CurvedAnimation(parent: animation, curve: curve),
        );

        return FadeTransition(
          opacity: fadeAnimation,
          child: Transform.scale(
            scale: scaleAnimation.value,
            child: Transform.rotate(
              angle: rotationAnimation.value,
              child: child,
            ),
          ),
        );
      },
    );
  }

  /// Hero-style transition for trade results
  static PageRouteBuilder heroTransition({
    required Widget child,
    Duration duration = const Duration(milliseconds: 500),
  }) {
    return PageRouteBuilder(
      pageBuilder: (context, animation, secondaryAnimation) => child,
      transitionDuration: duration,
      reverseTransitionDuration: duration,
      transitionsBuilder: (context, animation, secondaryAnimation, child) {
        const curve = Curves.easeInOutQuart;

        var slideAnimation = Tween(
          begin: const Offset(0.0, 0.3),
          end: Offset.zero,
        ).animate(CurvedAnimation(parent: animation, curve: curve));

        var fadeAnimation = Tween(begin: 0.0, end: 1.0).animate(
          CurvedAnimation(parent: animation, curve: curve),
        );

        var scaleAnimation = Tween(begin: 0.9, end: 1.0).animate(
          CurvedAnimation(parent: animation, curve: curve),
        );

        return SlideTransition(
          position: slideAnimation,
          child: FadeTransition(
            opacity: fadeAnimation,
            child: ScaleTransition(
              scale: scaleAnimation,
              child: child,
            ),
          ),
        );
      },
    );
  }

  /// Shimmer reveal transition for tutorials
  static PageRouteBuilder shimmerReveal({
    required Widget child,
    Duration duration = const Duration(milliseconds: 800),
  }) {
    return PageRouteBuilder(
      pageBuilder: (context, animation, secondaryAnimation) => child,
      transitionDuration: duration,
      reverseTransitionDuration: duration,
      transitionsBuilder: (context, animation, secondaryAnimation, child) {
        return AnimatedBuilder(
          animation: animation,
          builder: (context, child) {
            return ShaderMask(
              shaderCallback: (Rect bounds) {
                return LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [
                    Colors.transparent,
                    Colors.white.withOpacity(animation.value),
                    Colors.transparent,
                  ],
                  stops: [
                    0.0,
                    animation.value,
                    1.0,
                  ],
                ).createShader(bounds);
              },
              child: child,
            );
          },
          child: child,
        );
      },
    );
  }
}

/// Extension methods for easier navigation with custom transitions
extension NavigationExtensions on NavigatorState {
  /// Navigate with slide from right transition
  Future<T?> pushSlideFromRight<T extends Object?>(Widget child) {
    return push<T>(CustomPageTransitions.slideFromRight(child: child));
  }

  /// Navigate with slide from bottom transition
  Future<T?> pushSlideFromBottom<T extends Object?>(Widget child) {
    return push<T>(CustomPageTransitions.slideFromBottom(child: child));
  }

  /// Navigate with fade and scale transition
  Future<T?> pushFadeWithScale<T extends Object?>(Widget child) {
    return push<T>(CustomPageTransitions.fadeWithScale(child: child));
  }

  /// Navigate with cosmic transition
  Future<T?> pushCosmicTransition<T extends Object?>(Widget child) {
    return push<T>(CustomPageTransitions.cosmicTransition(child: child));
  }

  /// Navigate with hero transition
  Future<T?> pushHeroTransition<T extends Object?>(Widget child) {
    return push<T>(CustomPageTransitions.heroTransition(child: child));
  }

  /// Replace current route with slide transition
  Future<T?> pushReplacementSlide<T extends Object?, TO extends Object?>(
    Widget child,
  ) {
    return pushReplacement<T, TO>(
      CustomPageTransitions.slideFromRight(child: child),
    );
  }

  /// Replace current route with cosmic transition
  Future<T?> pushReplacementCosmic<T extends Object?, TO extends Object?>(
    Widget child,
  ) {
    return pushReplacement<T, TO>(
      CustomPageTransitions.cosmicTransition(child: child),
    );
  }
}

/// Utility class for consistent transition durations and curves
class TransitionConfig {
  static const Duration fast = Duration(milliseconds: 200);
  static const Duration normal = Duration(milliseconds: 300);
  static const Duration slow = Duration(milliseconds: 500);
  static const Duration cosmic = Duration(milliseconds: 600);

  static const Curve easeInOutCubic = Curves.easeInOutCubic;
  static const Curve elasticOut = Curves.elasticOut;
  static const Curve bounceOut = Curves.bounceOut;
  static const Curve fastLinearToSlowEaseIn = Curves.fastLinearToSlowEaseIn;
}

/// Pre-built page route builders for common navigation scenarios
class RouteBuilders {
  /// Route for onboarding screens
  static PageRouteBuilder onboardingRoute(Widget child) {
    return CustomPageTransitions.slideFromRight(
      child: child,
      duration: TransitionConfig.normal,
    );
  }

  /// Route for trading screens
  static PageRouteBuilder tradingRoute(Widget child) {
    return CustomPageTransitions.cosmicTransition(
      child: child,
      duration: TransitionConfig.cosmic,
    );
  }

  /// Route for result screens
  static PageRouteBuilder resultRoute(Widget child) {
    return CustomPageTransitions.heroTransition(
      child: child,
      duration: TransitionConfig.slow,
    );
  }

  /// Route for modal screens
  static PageRouteBuilder modalRoute(Widget child) {
    return CustomPageTransitions.slideFromBottom(
      child: child,
      duration: TransitionConfig.normal,
    );
  }
}