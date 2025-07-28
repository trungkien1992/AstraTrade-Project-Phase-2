// Reusable pulsating button widget for AstraTrade UI

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'cosmic_haptic_button.dart';

class PulsatingButton extends StatefulWidget {
  final String text;
  final VoidCallback? onPressed;
  final Color? color;
  final bool isLoading;
  
  const PulsatingButton({
    super.key,
    required this.text,
    required this.onPressed,
    this.color,
    this.isLoading = false,
  });

  @override
  State<PulsatingButton> createState() => _PulsatingButtonState();
}

class _PulsatingButtonState extends State<PulsatingButton>
    with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _scaleAnimation;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(seconds: 1),
      vsync: this,
    );
    _scaleAnimation = Tween<double>(
      begin: 1.0,
      end: 1.05,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeInOut,
    ));

    _animationController.repeat(reverse: true);
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _scaleAnimation,
      builder: (context, child) {
        return Transform.scale(
          scale: _scaleAnimation.value,
          child: CosmicHapticButton(
            onPressed: widget.isLoading ? null : () {
              HapticFeedback.mediumImpact();
              widget.onPressed?.call();
            },
            hapticPattern: CosmicHapticPattern.medium,
            primaryColor: widget.color ?? Theme.of(context).primaryColor,
            padding: const EdgeInsets.symmetric(
              horizontal: 32,
              vertical: 16,
            ),
            enabled: !widget.isLoading,
            child: widget.isLoading
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                    ),
                  )
                : Text(
                    widget.text,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
          ),
        );
      },
    );
  }
}