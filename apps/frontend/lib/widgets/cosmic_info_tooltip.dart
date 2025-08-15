import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../theme/cosmic_theme.dart';
import '../utils/constants.dart';

/// Cosmic-themed tooltip widget for displaying helpful information
/// Provides contextual guidance with stellar aesthetics
class CosmicInfoTooltip extends StatefulWidget {
  final String title;
  final String message;
  final Widget child;
  final CosmicTooltipType type;
  final bool showOnTap;

  const CosmicInfoTooltip({
    super.key,
    required this.title,
    required this.message,
    required this.child,
    this.type = CosmicTooltipType.info,
    this.showOnTap = false,
  });

  @override
  State<CosmicInfoTooltip> createState() => _CosmicInfoTooltipState();
}

class _CosmicInfoTooltipState extends State<CosmicInfoTooltip>
    with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _scaleAnimation;
  late Animation<double> _opacityAnimation;

  OverlayEntry? _overlayEntry;
  bool _isShowing = false;

  @override
  void initState() {
    super.initState();

    _animationController = AnimationController(
      duration: CosmicAnimations.fast,
      vsync: this,
    );

    _scaleAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.elasticOut),
    );

    _opacityAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _hideTooltip();
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (widget.showOnTap) {
      return GestureDetector(onTap: _toggleTooltip, child: widget.child);
    }

    return MouseRegion(
      onEnter: (_) => _showTooltip(),
      onExit: (_) => _hideTooltip(),
      child: GestureDetector(onLongPress: _showTooltip, child: widget.child),
    );
  }

  void _toggleTooltip() {
    if (_isShowing) {
      _hideTooltip();
    } else {
      _showTooltip();
    }
  }

  void _showTooltip() {
    if (_isShowing) return;

    _isShowing = true;
    _overlayEntry = _createOverlayEntry();
    Overlay.of(context).insert(_overlayEntry!);
    _animationController.forward();
  }

  void _hideTooltip() {
    if (!_isShowing) return;

    _isShowing = false;
    _animationController.reverse().then((_) {
      _overlayEntry?.remove();
      _overlayEntry = null;
    });
  }

  OverlayEntry _createOverlayEntry() {
    final renderBox = context.findRenderObject() as RenderBox;
    final size = renderBox.size;
    final offset = renderBox.localToGlobal(Offset.zero);

    return OverlayEntry(
      builder: (context) => Positioned(
        left: offset.dx - 50, // Center approximately
        top: offset.dy + size.height + 8,
        child: AnimatedBuilder(
          animation: _animationController,
          builder: (context, child) {
            return Transform.scale(
              scale: _scaleAnimation.value,
              child: Opacity(
                opacity: _opacityAnimation.value,
                child: Material(
                  color: Colors.transparent,
                  child: _buildTooltipContent(),
                ),
              ),
            );
          },
        ),
      ),
    );
  }

  Widget _buildTooltipContent() {
    final colors = _getTypeColors();

    return Container(
      constraints: const BoxConstraints(maxWidth: 280),
      padding: const EdgeInsets.all(AppConstants.paddingMedium),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            colors.backgroundColor,
            colors.backgroundColor.withOpacity(0.9),
          ],
        ),
        borderRadius: BorderRadius.circular(AppConstants.defaultBorderRadius),
        border: Border.all(color: colors.borderColor, width: 1),
        boxShadow: [
          BoxShadow(
            color: colors.shadowColor,
            blurRadius: 15,
            spreadRadius: 3,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          // Header with icon and title
          Row(
            children: [
              Icon(_getTypeIcon(), color: colors.iconColor, size: 18),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  widget.title,
                  style: GoogleFonts.orbitron(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    color: colors.titleColor,
                  ),
                ),
              ),
            ],
          ),

          const SizedBox(height: 8),

          // Message content
          Text(
            widget.message,
            style: GoogleFonts.rajdhani(
              fontSize: 13,
              color: colors.textColor,
              height: 1.4,
            ),
          ),

          // Decorative element
          const SizedBox(height: 8),
          Container(
            height: 2,
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [
                  colors.accentColor,
                  colors.accentColor.withOpacity(0.3),
                  Colors.transparent,
                ],
              ),
              borderRadius: BorderRadius.circular(1),
            ),
          ),
        ],
      ),
    );
  }

  TooltipColors _getTypeColors() {
    switch (widget.type) {
      case CosmicTooltipType.info:
        return TooltipColors(
          backgroundColor: CosmicTheme.cosmicDarkGray,
          borderColor: CosmicTheme.accentCyan,
          shadowColor: CosmicTheme.accentCyan.withOpacity(0.3),
          iconColor: CosmicTheme.accentCyan,
          titleColor: CosmicTheme.starWhite,
          textColor: CosmicTheme.starWhite.withOpacity(0.9),
          accentColor: CosmicTheme.accentCyan,
        );

      case CosmicTooltipType.warning:
        return TooltipColors(
          backgroundColor: CosmicTheme.cosmicDarkGray,
          borderColor: CosmicTheme.cosmicGold,
          shadowColor: CosmicTheme.cosmicGold.withOpacity(0.3),
          iconColor: CosmicTheme.cosmicGold,
          titleColor: CosmicTheme.starWhite,
          textColor: CosmicTheme.starWhite.withOpacity(0.9),
          accentColor: CosmicTheme.cosmicGold,
        );

      case CosmicTooltipType.success:
        return TooltipColors(
          backgroundColor: CosmicTheme.cosmicDarkGray,
          borderColor: const Color(0xFF10B981),
          shadowColor: const Color(0xFF10B981).withOpacity(0.3),
          iconColor: const Color(0xFF10B981),
          titleColor: CosmicTheme.starWhite,
          textColor: CosmicTheme.starWhite.withOpacity(0.9),
          accentColor: const Color(0xFF10B981),
        );

      case CosmicTooltipType.error:
        return TooltipColors(
          backgroundColor: CosmicTheme.cosmicDarkGray,
          borderColor: const Color(0xFFEF4444),
          shadowColor: const Color(0xFFEF4444).withOpacity(0.3),
          iconColor: const Color(0xFFEF4444),
          titleColor: CosmicTheme.starWhite,
          textColor: CosmicTheme.starWhite.withOpacity(0.9),
          accentColor: const Color(0xFFEF4444),
        );

      case CosmicTooltipType.cosmic:
        return TooltipColors(
          backgroundColor: CosmicTheme.cosmicDarkGray,
          borderColor: CosmicTheme.primaryPurple,
          shadowColor: CosmicTheme.primaryPurple.withOpacity(0.3),
          iconColor: CosmicTheme.primaryPurple,
          titleColor: CosmicTheme.starWhite,
          textColor: CosmicTheme.starWhite.withOpacity(0.9),
          accentColor: CosmicTheme.primaryPurple,
        );
    }
  }

  IconData _getTypeIcon() {
    switch (widget.type) {
      case CosmicTooltipType.info:
        return Icons.info_outline;
      case CosmicTooltipType.warning:
        return Icons.warning_amber_outlined;
      case CosmicTooltipType.success:
        return Icons.check_circle_outline;
      case CosmicTooltipType.error:
        return Icons.error_outline;
      case CosmicTooltipType.cosmic:
        return Icons.auto_awesome;
    }
  }
}

/// Types of cosmic tooltips with different visual styles
enum CosmicTooltipType { info, warning, success, error, cosmic }

/// Color scheme for different tooltip types
class TooltipColors {
  final Color backgroundColor;
  final Color borderColor;
  final Color shadowColor;
  final Color iconColor;
  final Color titleColor;
  final Color textColor;
  final Color accentColor;

  TooltipColors({
    required this.backgroundColor,
    required this.borderColor,
    required this.shadowColor,
    required this.iconColor,
    required this.titleColor,
    required this.textColor,
    required this.accentColor,
  });
}

/// Convenience widget for quick cosmic info tooltips
class QuickCosmicTooltip extends StatelessWidget {
  final String message;
  final Widget child;
  final CosmicTooltipType type;

  const QuickCosmicTooltip({
    super.key,
    required this.message,
    required this.child,
    this.type = CosmicTooltipType.info,
  });

  @override
  Widget build(BuildContext context) {
    return CosmicInfoTooltip(
      title: _getDefaultTitle(),
      message: message,
      type: type,
      child: child,
    );
  }

  String _getDefaultTitle() {
    switch (type) {
      case CosmicTooltipType.info:
        return 'Cosmic Intel';
      case CosmicTooltipType.warning:
        return 'Stellar Warning';
      case CosmicTooltipType.success:
        return 'Quantum Success';
      case CosmicTooltipType.error:
        return 'System Alert';
      case CosmicTooltipType.cosmic:
        return 'Cosmic Wisdom';
    }
  }
}

/// Helper for creating trading-specific cosmic tooltips
class TradingCosmicTooltip extends StatelessWidget {
  final String title;
  final String description;
  final Widget child;
  final bool showOnTap;

  const TradingCosmicTooltip({
    super.key,
    required this.title,
    required this.description,
    required this.child,
    this.showOnTap = false,
  });

  @override
  Widget build(BuildContext context) {
    return CosmicInfoTooltip(
      title: title,
      message: description,
      type: CosmicTooltipType.cosmic,
      showOnTap: showOnTap,
      child: child,
    );
  }
}
