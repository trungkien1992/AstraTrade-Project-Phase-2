import 'package:flutter/material.dart';
import 'dart:math' as math;

/// Tutorial overlay widget that creates a spotlight effect on specific UI elements
/// Provides step-by-step guidance for new users
class TutorialOverlayWidget extends StatefulWidget {
  final Widget child;
  final List<TutorialStep> steps;
  final VoidCallback? onTutorialComplete;
  final bool showTutorial;

  const TutorialOverlayWidget({
    super.key,
    required this.child,
    required this.steps,
    this.onTutorialComplete,
    this.showTutorial = false,
  });

  @override
  State<TutorialOverlayWidget> createState() => _TutorialOverlayWidgetState();
}

class _TutorialOverlayWidgetState extends State<TutorialOverlayWidget>
    with TickerProviderStateMixin {
  late AnimationController _animationController;
  late AnimationController _pulseController;
  late Animation<double> _fadeAnimation;
  late Animation<double> _scaleAnimation;
  late Animation<double> _pulseAnimation;

  int _currentStepIndex = 0;
  OverlayEntry? _overlayEntry;
  GlobalKey _targetKey = GlobalKey();

  @override
  void initState() {
    super.initState();
    _setupAnimations();
  }

  void _setupAnimations() {
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );

    _pulseController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );

    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.easeInOut),
    );

    _scaleAnimation = Tween<double>(begin: 0.8, end: 1.0).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.elasticOut),
    );

    _pulseAnimation = Tween<double>(begin: 1.0, end: 1.2).animate(
      CurvedAnimation(parent: _pulseController, curve: Curves.easeInOut),
    );

    _pulseController.repeat(reverse: true);
  }

  @override
  void didUpdateWidget(TutorialOverlayWidget oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.showTutorial && !oldWidget.showTutorial) {
      _showTutorial();
    } else if (!widget.showTutorial && oldWidget.showTutorial) {
      _hideTutorial();
    }
  }

  @override
  void dispose() {
    _animationController.dispose();
    _pulseController.dispose();
    _hideTutorial();
    super.dispose();
  }

  void _showTutorial() {
    if (widget.steps.isEmpty) return;

    _currentStepIndex = 0;
    _createOverlay();
    _animationController.forward();
  }

  void _hideTutorial() {
    _animationController.reverse().then((_) {
      _removeOverlay();
    });
  }

  void _createOverlay() {
    _removeOverlay();
    
    _overlayEntry = OverlayEntry(
      builder: (context) => _buildOverlay(),
    );

    Overlay.of(context).insert(_overlayEntry!);
  }

  void _removeOverlay() {
    _overlayEntry?.remove();
    _overlayEntry = null;
  }

  Widget _buildOverlay() {
    final step = widget.steps[_currentStepIndex];
    
    return AnimatedBuilder(
      animation: _animationController,
      builder: (context, child) {
        return Opacity(
          opacity: _fadeAnimation.value,
          child: Material(
            color: Colors.transparent,
            child: Stack(
              children: [
                // Dark overlay with spotlight cutout
                CustomPaint(
                  size: MediaQuery.of(context).size,
                  painter: SpotlightPainter(
                    targetRect: _getTargetRect(step),
                    spotlightRadius: step.spotlightRadius,
                  ),
                ),
                
                // Tutorial content card
                Positioned(
                  left: step.tooltipPosition.dx,
                  top: step.tooltipPosition.dy,
                  child: Transform.scale(
                    scale: _scaleAnimation.value,
                    child: _buildTutorialCard(step),
                  ),
                ),

                // Pulsing indicator on target
                if (_getTargetRect(step) != Rect.zero)
                  Positioned(
                    left: _getTargetRect(step).center.dx - 20,
                    top: _getTargetRect(step).center.dy - 20,
                    child: AnimatedBuilder(
                      animation: _pulseAnimation,
                      child: Container(
                        width: 40,
                        height: 40,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          border: Border.all(
                            color: Colors.cyan,
                            width: 2,
                          ),
                        ),
                      ),
                      builder: (context, child) {
                        return Transform.scale(
                          scale: _pulseAnimation.value,
                          child: child,
                        );
                      },
                    ),
                  ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildTutorialCard(TutorialStep step) {
    return Container(
      constraints: const BoxConstraints(maxWidth: 280),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [Colors.indigo.shade800, Colors.purple.shade800],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.cyan.withOpacity(0.5)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.3),
            blurRadius: 20,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header with step indicator
          Row(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: Colors.cyan.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.cyan.withOpacity(0.5)),
                ),
                child: Text(
                  'Step ${_currentStepIndex + 1}/${widget.steps.length}',
                  style: const TextStyle(
                    color: Colors.cyan,
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              const Spacer(),
              IconButton(
                onPressed: _skipTutorial,
                icon: const Icon(Icons.close, color: Colors.white70, size: 20),
                constraints: const BoxConstraints(minWidth: 32, minHeight: 32),
                padding: EdgeInsets.zero,
              ),
            ],
          ),

          const SizedBox(height: 12),

          // Title
          Text(
            step.title,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),

          const SizedBox(height: 8),

          // Description
          Text(
            step.description,
            style: const TextStyle(
              color: Colors.white70,
              fontSize: 14,
              height: 1.4,
            ),
          ),

          const SizedBox(height: 16),

          // Action buttons
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              if (_currentStepIndex > 0)
                TextButton(
                  onPressed: _previousStep,
                  child: const Text(
                    'Back',
                    style: TextStyle(color: Colors.white70),
                  ),
                ),
              const Spacer(),
              ElevatedButton(
                onPressed: _nextStep,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.cyan,
                  foregroundColor: Colors.black,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(20),
                  ),
                ),
                child: Text(
                  _currentStepIndex == widget.steps.length - 1 ? 'Finish' : 'Next',
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Rect _getTargetRect(TutorialStep step) {
    if (step.targetKey?.currentContext == null) return Rect.zero;
    
    final RenderBox renderBox = 
        step.targetKey!.currentContext!.findRenderObject() as RenderBox;
    final position = renderBox.localToGlobal(Offset.zero);
    final size = renderBox.size;
    
    return Rect.fromLTWH(position.dx, position.dy, size.width, size.height);
  }

  void _nextStep() {
    if (_currentStepIndex < widget.steps.length - 1) {
      setState(() {
        _currentStepIndex++;
      });
      _createOverlay();
    } else {
      _completeTutorial();
    }
  }

  void _previousStep() {
    if (_currentStepIndex > 0) {
      setState(() {
        _currentStepIndex--;
      });
      _createOverlay();
    }
  }

  void _skipTutorial() {
    _completeTutorial();
  }

  void _completeTutorial() {
    _hideTutorial();
    widget.onTutorialComplete?.call();
  }

  @override
  Widget build(BuildContext context) {
    return widget.child;
  }
}

/// Custom painter for creating the spotlight effect
class SpotlightPainter extends CustomPainter {
  final Rect targetRect;
  final double spotlightRadius;

  SpotlightPainter({
    required this.targetRect,
    this.spotlightRadius = 80,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.black.withOpacity(0.8)
      ..style = PaintingStyle.fill;

    // Create a path that covers the entire screen
    final outerPath = Path()
      ..addRect(Rect.fromLTWH(0, 0, size.width, size.height));

    // Create spotlight circle around target
    if (targetRect != Rect.zero) {
      final center = targetRect.center;
      final radius = math.max(targetRect.width, targetRect.height) / 2 + spotlightRadius;
      
      final innerPath = Path()
        ..addOval(Rect.fromCircle(center: center, radius: radius));

      // Subtract the spotlight area from the overlay
      final combinedPath = Path.combine(
        PathOperation.difference,
        outerPath,
        innerPath,
      );

      canvas.drawPath(combinedPath, paint);
    } else {
      canvas.drawPath(outerPath, paint);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}

/// Data model for tutorial steps
class TutorialStep {
  final String title;
  final String description;
  final GlobalKey? targetKey;
  final Offset tooltipPosition;
  final double spotlightRadius;

  const TutorialStep({
    required this.title,
    required this.description,
    this.targetKey,
    required this.tooltipPosition,
    this.spotlightRadius = 80,
  });
}