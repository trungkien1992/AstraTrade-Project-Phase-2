import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

/// Enhanced card widget with micro-interactions
/// Provides subtle animations and feedback for better user experience
class InteractiveCard extends StatefulWidget {
  final Widget child;
  final VoidCallback? onTap;
  final VoidCallback? onLongPress;
  final Color? backgroundColor;
  final EdgeInsets? padding;
  final BorderRadius? borderRadius;
  final double elevation;
  final bool isSelected;
  final Duration animationDuration;
  final double hoverScale;
  final double pressScale;
  final bool enableHapticFeedback;
  final Color? borderColor;
  final double borderWidth;

  const InteractiveCard({
    super.key,
    required this.child,
    this.onTap,
    this.onLongPress,
    this.backgroundColor,
    this.padding = const EdgeInsets.all(16.0),
    this.borderRadius,
    this.elevation = 2.0,
    this.isSelected = false,
    this.animationDuration = const Duration(milliseconds: 200),
    this.hoverScale = 1.02,
    this.pressScale = 0.98,
    this.enableHapticFeedback = true,
    this.borderColor,
    this.borderWidth = 1.0,
  });

  @override
  State<InteractiveCard> createState() => _InteractiveCardState();
}

class _InteractiveCardState extends State<InteractiveCard>
    with TickerProviderStateMixin {
  late AnimationController _scaleController;
  late AnimationController _elevationController;
  late AnimationController _colorController;

  late Animation<double> _scaleAnimation;
  late Animation<double> _elevationAnimation;
  late Animation<Color?> _colorAnimation;

  bool _isPressed = false;
  bool _isHovered = false;

  @override
  void initState() {
    super.initState();

    _scaleController = AnimationController(
      duration: widget.animationDuration,
      vsync: this,
    );

    _elevationController = AnimationController(
      duration: widget.animationDuration,
      vsync: this,
    );

    _colorController = AnimationController(
      duration: widget.animationDuration,
      vsync: this,
    );

    _scaleAnimation = Tween<double>(
      begin: 1.0,
      end: widget.hoverScale,
    ).animate(CurvedAnimation(
      parent: _scaleController,
      curve: Curves.easeInOutCubic,
    ));

    _elevationAnimation = Tween<double>(
      begin: widget.elevation,
      end: widget.elevation + 4.0,
    ).animate(CurvedAnimation(
      parent: _elevationController,
      curve: Curves.easeInOutCubic,
    ));

    _colorAnimation = ColorTween(
      begin: widget.backgroundColor ?? Colors.white,
      end: (widget.backgroundColor ?? Colors.white).withOpacity(0.9),
    ).animate(CurvedAnimation(
      parent: _colorController,
      curve: Curves.easeInOutCubic,
    ));
  }

  @override
  void dispose() {
    _scaleController.dispose();
    _elevationController.dispose();
    _colorController.dispose();
    super.dispose();
  }

  void _onTapDown(TapDownDetails details) {
    setState(() {
      _isPressed = true;
    });

    _scaleController.animateTo(widget.pressScale / widget.hoverScale);
    _colorController.forward();

    if (widget.enableHapticFeedback) {
      HapticFeedback.lightImpact();
    }
  }

  void _onTapUp(TapUpDetails details) {
    _resetAnimations();
  }

  void _onTapCancel() {
    _resetAnimations();
  }

  void _resetAnimations() {
    setState(() {
      _isPressed = false;
    });

    if (_isHovered) {
      _scaleController.animateTo(1.0);
    } else {
      _scaleController.reverse();
    }
    
    _colorController.reverse();
  }

  void _onHoverEnter(PointerEnterEvent event) {
    setState(() {
      _isHovered = true;
    });

    _scaleController.forward();
    _elevationController.forward();
  }

  void _onHoverExit(PointerExitEvent event) {
    setState(() {
      _isHovered = false;
    });

    if (!_isPressed) {
      _scaleController.reverse();
    }
    _elevationController.reverse();
  }

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      onEnter: _onHoverEnter,
      onExit: _onHoverExit,
      child: GestureDetector(
        onTap: widget.onTap,
        onLongPress: widget.onLongPress,
        onTapDown: _onTapDown,
        onTapUp: _onTapUp,
        onTapCancel: _onTapCancel,
        child: AnimatedBuilder(
          animation: Listenable.merge([
            _scaleAnimation,
            _elevationAnimation,
            _colorAnimation,
          ]),
          builder: (context, child) {
            return Transform.scale(
              scale: _scaleAnimation.value,
              child: Card(
                elevation: _elevationAnimation.value,
                color: _colorAnimation.value,
                shape: RoundedRectangleBorder(
                  borderRadius: widget.borderRadius ?? BorderRadius.circular(12),
                  side: BorderSide(
                    color: widget.isSelected
                        ? (widget.borderColor ?? Theme.of(context).primaryColor)
                        : (widget.borderColor ?? Colors.transparent),
                    width: widget.isSelected ? widget.borderWidth * 2 : widget.borderWidth,
                  ),
                ),
                child: Container(
                  padding: widget.padding,
                  child: widget.child,
                ),
              ),
            );
          },
        ),
      ),
    );
  }
}

/// Animated button with micro-interactions
class AnimatedInteractiveButton extends StatefulWidget {
  final Widget child;
  final VoidCallback? onPressed;
  final Color? backgroundColor;
  final Color? foregroundColor;
  final EdgeInsets padding;
  final BorderRadius? borderRadius;
  final Duration animationDuration;
  final double pressScale;
  final bool enableHapticFeedback;
  final bool isLoading;
  final IconData? icon;

  const AnimatedInteractiveButton({
    super.key,
    required this.child,
    this.onPressed,
    this.backgroundColor,
    this.foregroundColor,
    this.padding = const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
    this.borderRadius,
    this.animationDuration = const Duration(milliseconds: 150),
    this.pressScale = 0.95,
    this.enableHapticFeedback = true,
    this.isLoading = false,
    this.icon,
  });

  @override
  State<AnimatedInteractiveButton> createState() => _AnimatedInteractiveButtonState();
}

class _AnimatedInteractiveButtonState extends State<AnimatedInteractiveButton>
    with TickerProviderStateMixin {
  late AnimationController _scaleController;
  late AnimationController _rippleController;
  late AnimationController _loadingController;

  late Animation<double> _scaleAnimation;
  late Animation<double> _rippleAnimation;

  bool _isPressed = false;

  @override
  void initState() {
    super.initState();

    _scaleController = AnimationController(
      duration: widget.animationDuration,
      vsync: this,
    );

    _rippleController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );

    _loadingController = AnimationController(
      duration: const Duration(milliseconds: 1000),
      vsync: this,
    );

    _scaleAnimation = Tween<double>(
      begin: 1.0,
      end: widget.pressScale,
    ).animate(CurvedAnimation(
      parent: _scaleController,
      curve: Curves.easeInOutCubic,
    ));

    _rippleAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _rippleController,
      curve: Curves.easeOut,
    ));

    if (widget.isLoading) {
      _loadingController.repeat();
    }
  }

  @override
  void didUpdateWidget(AnimatedInteractiveButton oldWidget) {
    super.didUpdateWidget(oldWidget);
    
    if (widget.isLoading != oldWidget.isLoading) {
      if (widget.isLoading) {
        _loadingController.repeat();
      } else {
        _loadingController.stop();
      }
    }
  }

  @override
  void dispose() {
    _scaleController.dispose();
    _rippleController.dispose();
    _loadingController.dispose();
    super.dispose();
  }

  void _onTapDown(TapDownDetails details) {
    setState(() {
      _isPressed = true;
    });

    _scaleController.forward();
    _rippleController.reset();
    _rippleController.forward();

    if (widget.enableHapticFeedback) {
      HapticFeedback.mediumImpact();
    }
  }

  void _onTapUp(TapUpDetails details) {
    _resetAnimation();
  }

  void _onTapCancel() {
    _resetAnimation();
  }

  void _resetAnimation() {
    setState(() {
      _isPressed = false;
    });

    _scaleController.reverse();
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTapDown: widget.onPressed != null && !widget.isLoading ? _onTapDown : null,
      onTapUp: widget.onPressed != null && !widget.isLoading ? _onTapUp : null,
      onTapCancel: widget.onPressed != null && !widget.isLoading ? _onTapCancel : null,
      onTap: widget.onPressed != null && !widget.isLoading ? widget.onPressed : null,
      child: AnimatedBuilder(
        animation: _scaleAnimation,
        builder: (context, child) {
          return Transform.scale(
            scale: _scaleAnimation.value,
            child: Container(
              padding: widget.padding,
              decoration: BoxDecoration(
                color: widget.backgroundColor ?? Theme.of(context).primaryColor,
                borderRadius: widget.borderRadius ?? BorderRadius.circular(8),
                boxShadow: [
                  BoxShadow(
                    color: (widget.backgroundColor ?? Theme.of(context).primaryColor)
                        .withOpacity(0.3),
                    blurRadius: _isPressed ? 4 : 8,
                    offset: Offset(0, _isPressed ? 2 : 4),
                  ),
                ],
              ),
              child: Stack(
                alignment: Alignment.center,
                children: [
                  // Ripple effect
                  AnimatedBuilder(
                    animation: _rippleAnimation,
                    builder: (context, child) {
                      return Container(
                        decoration: BoxDecoration(
                          borderRadius: widget.borderRadius ?? BorderRadius.circular(8),
                          color: Colors.white.withOpacity(
                            (1 - _rippleAnimation.value) * 0.3,
                          ),
                        ),
                      );
                    },
                  ),
                  
                  // Button content
                  AnimatedSwitcher(
                    duration: const Duration(milliseconds: 200),
                    child: widget.isLoading
                        ? RotationTransition(
                            turns: _loadingController,
                            child: Icon(
                              Icons.refresh,
                              color: widget.foregroundColor ?? Colors.white,
                            ),
                          )
                        : Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              if (widget.icon != null) ...[
                                Icon(
                                  widget.icon,
                                  color: widget.foregroundColor ?? Colors.white,
                                  size: 18,
                                ),
                                const SizedBox(width: 8),
                              ],
                              DefaultTextStyle(
                                style: TextStyle(
                                  color: widget.foregroundColor ?? Colors.white,
                                  fontWeight: FontWeight.bold,
                                ),
                                child: widget.child,
                              ),
                            ],
                          ),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}

/// Utility class for consistent micro-interaction values
class InteractionConfig {
  static const Duration fast = Duration(milliseconds: 100);
  static const Duration normal = Duration(milliseconds: 200);
  static const Duration slow = Duration(milliseconds: 300);

  static const double defaultHoverScale = 1.02;
  static const double defaultPressScale = 0.98;
  static const double buttonPressScale = 0.95;

  static const Curve defaultCurve = Curves.easeInOutCubic;
  static const Curve bounceCurve = Curves.elasticOut;
  static const Curve smoothCurve = Curves.easeInOutQuart;
}