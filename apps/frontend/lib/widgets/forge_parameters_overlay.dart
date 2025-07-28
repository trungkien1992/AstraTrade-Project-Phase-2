import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'dart:math' as math;

class ForgeParametersOverlay extends StatefulWidget {
  final Offset position;
  final String symbol;
  final String action;
  final int amount;
  final double tradeAmount;
  final double riskLevel;
  final VoidCallback? onConfirm;
  final VoidCallback? onCancel;
  final VoidCallback? onAdjust;

  const ForgeParametersOverlay({
    Key? key,
    required this.position,
    required this.symbol,
    required this.action,
    required this.amount,
    this.tradeAmount = 100.0,
    this.riskLevel = 0.5,
    this.onConfirm,
    this.onCancel,
    this.onAdjust,
  }) : super(key: key);

  @override
  State<ForgeParametersOverlay> createState() => _ForgeParametersOverlayState();
}

class _ForgeParametersOverlayState extends State<ForgeParametersOverlay>
    with TickerProviderStateMixin {
  late AnimationController _animationController;
  late AnimationController _pulseController;
  late Animation<double> _scaleAnimation;
  late Animation<double> _fadeAnimation;
  late Animation<double> _pulseAnimation;

  @override
  void initState() {
    super.initState();
    
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );
    
    _pulseController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    )..repeat(reverse: true);
    
    _scaleAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.elasticOut,
    ));
    
    _fadeAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeOut,
    ));
    
    _pulseAnimation = Tween<double>(
      begin: 0.8,
      end: 1.2,
    ).animate(CurvedAnimation(
      parent: _pulseController,
      curve: Curves.easeInOut,
    ));
    
    _animationController.forward();
  }

  @override
  void dispose() {
    _animationController.dispose();
    _pulseController.dispose();
    super.dispose();
  }

  void _hide() {
    _animationController.reverse().then((_) {
      widget.onCancel?.call();
    });
  }

  void _confirm() {
    widget.onConfirm?.call();
  }

  String _getCosmicSymbolName() {
    switch (widget.symbol) {
      case 'BTCUSD':
        return 'Prime Star';
      case 'ETHUSD':
        return 'Ether Nexus';
      case 'SOLUSD':
        return 'Solar Flare';
      default:
        return 'Cosmic Energy';
    }
  }

  IconData _getCosmicIcon() {
    switch (widget.symbol) {
      case 'BTCUSD':
        return Icons.public;
      case 'ETHUSD':
        return Icons.blur_on;
      case 'SOLUSD':
        return Icons.flare;
      default:
        return Icons.auto_awesome;
    }
  }

  Color _getActionColor() {
    switch (widget.action.toUpperCase()) {
      case 'BUY':
        return Colors.green;
      case 'SELL':
        return Colors.red;
      case 'FORGE':
        return Colors.purple;
      default:
        return Colors.blue;
    }
  }

  String _getActionText() {
    switch (widget.action.toUpperCase()) {
      case 'BUY':
        return 'CHANNEL';
      case 'SELL':
        return 'RELEASE';
      case 'FORGE':
        return 'FORGE';
      default:
        return widget.action.toUpperCase();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Positioned(
      left: widget.position.dx - 120,
      top: widget.position.dy - 100,
      child: AnimatedBuilder(
        animation: _animationController,
        builder: (context, child) {
          return Transform.scale(
            scale: _scaleAnimation.value,
            child: Opacity(
              opacity: _fadeAnimation.value,
              child: _buildOverlayContent(),
            ),
          );
        },
      ),
    );
  }

  Widget _buildOverlayContent() {
    return Container(
      width: 240,
      constraints: const BoxConstraints(maxWidth: 260),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            Colors.black.withOpacity(0.95),
            Colors.grey.shade900.withOpacity(0.95),
          ],
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: _getActionColor().withOpacity(0.8),
          width: 2,
        ),
        boxShadow: [
          BoxShadow(
            color: _getActionColor().withOpacity(0.4),
            blurRadius: 20,
            spreadRadius: 3,
          ),
          BoxShadow(
            color: Colors.black.withOpacity(0.8),
            blurRadius: 15,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Header
          _buildHeader(),
          
          // Divider
          Container(
            height: 1,
            margin: const EdgeInsets.symmetric(horizontal: 16),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [
                  Colors.transparent,
                  _getActionColor().withOpacity(0.5),
                  Colors.transparent,
                ],
              ),
            ),
          ),
          
          // Parameters
          _buildParameters(),
          
          // Action buttons
          _buildActionButtons(),
        ],
      ),
    );
  }

  Widget _buildHeader() {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          // Action with icon
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              AnimatedBuilder(
                animation: _pulseAnimation,
                builder: (context, child) {
                  return Transform.scale(
                    scale: _pulseAnimation.value,
                    child: Icon(
                      _getCosmicIcon(),
                      color: _getActionColor(),
                      size: 24,
                    ),
                  );
                },
              ),
              const SizedBox(width: 12),
              Text(
                _getActionText(),
                style: GoogleFonts.orbitron(
                  color: _getActionColor(),
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1.2,
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 8),
          
          // Cosmic symbol name
          Text(
            _getCosmicSymbolName(),
            style: GoogleFonts.orbitron(
              color: Colors.cyan.shade300,
              fontSize: 14,
              fontWeight: FontWeight.w600,
            ),
          ),
          
          const SizedBox(height: 4),
          
          // Real symbol
          Text(
            widget.symbol,
            style: GoogleFonts.rajdhani(
              color: Colors.grey.shade400,
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildParameters() {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          // Trade Amount parameter
          _buildParameterRow(
            'Trade Amount',
            '\$${widget.tradeAmount.toStringAsFixed(2)}',
            Icons.attach_money,
            Colors.green.shade400,
          ),
          
          const SizedBox(height: 12),
          
          // Stellar Shards reward
          _buildParameterRow(
            'SS Reward',
            '${widget.amount} TT',
            Icons.account_balance_wallet,
            Colors.purple.shade400,
          ),
          
          const SizedBox(height: 12),
          
          // Risk Level parameter
          _buildParameterRow(
            'Risk Level',
            _getRiskLevelText(widget.riskLevel),
            Icons.security,
            _getRiskLevelColor(widget.riskLevel),
          ),
          
          const SizedBox(height: 12),
          
          // Action type parameter
          _buildParameterRow(
            'Action',
            widget.action.toUpperCase(),
            widget.action.toUpperCase() == 'BUY' 
                ? Icons.trending_up 
                : widget.action.toUpperCase() == 'SELL'
                    ? Icons.trending_down
                    : Icons.auto_awesome,
            _getActionColor(),
          ),
          
          const SizedBox(height: 12),
          
          // AI confidence indicator
          _buildParameterRow(
            'AI Confidence',
            '${85 + math.Random().nextInt(10)}%',
            Icons.psychology,
            Colors.cyan.shade400,
          ),
        ],
      ),
    );
  }

  Widget _buildParameterRow(String label, String value, IconData icon, Color color) {
    return Row(
      children: [
        Icon(
          icon,
          color: color,
          size: 16,
        ),
        const SizedBox(width: 8),
        Expanded(
          child: Text(
            label,
            style: GoogleFonts.rajdhani(
              color: Colors.grey.shade300,
              fontSize: 12,
              fontWeight: FontWeight.w500,
            ),
          ),
        ),
        Text(
          value,
          style: GoogleFonts.orbitron(
            color: color,
            fontSize: 12,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }

  Widget _buildActionButtons() {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          // Top row: Cancel and Adjust
          Row(
            children: [
              // Cancel button
              Expanded(
                child: ElevatedButton(
                  onPressed: _hide,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.grey.shade700,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 10),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                  child: Text(
                    'Cancel',
                    style: GoogleFonts.rajdhani(
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ),
              
              const SizedBox(width: 8),
              
              // Adjust button
              Expanded(
                child: ElevatedButton(
                  onPressed: _adjust,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.blue.shade600,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 10),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        Icons.tune,
                        size: 12,
                      ),
                      const SizedBox(width: 4),
                      Text(
                        'Adjust',
                        style: GoogleFonts.rajdhani(
                          fontSize: 11,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 12),
          
          // Bottom row: Execute button (full width)
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: _confirm,
              style: ElevatedButton.styleFrom(
                backgroundColor: _getActionColor(),
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 14),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
                elevation: 4,
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.rocket_launch,
                    size: 16,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    'Execute Trade',
                    style: GoogleFonts.rajdhani(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  /// Get risk level display text
  String _getRiskLevelText(double riskLevel) {
    if (riskLevel <= 0.3) return 'Conservative';
    if (riskLevel <= 0.7) return 'Moderate';
    return 'Aggressive';
  }

  /// Get risk level color for UI display
  Color _getRiskLevelColor(double riskLevel) {
    if (riskLevel <= 0.3) return Colors.green.shade400;
    if (riskLevel <= 0.7) return Colors.orange.shade400;
    return Colors.red.shade400;
  }

  /// Handle adjust button press
  void _adjust() {
    _animationController.reverse().then((_) {
      widget.onAdjust?.call();
    });
  }
}

// Helper class for managing forge parameter overlays
class ForgeParameterManager {
  static OverlayEntry? _currentOverlay;
  
  static void showForgeParameters({
    required BuildContext context,
    required Offset position,
    required String symbol,
    required String action,
    required int amount,
    double tradeAmount = 100.0,
    double riskLevel = 0.5,
    VoidCallback? onConfirm,
    VoidCallback? onCancel,
    VoidCallback? onAdjust,
  }) {
    hideForgeParameters();
    
    _currentOverlay = OverlayEntry(
      builder: (context) => ForgeParametersOverlay(
        position: position,
        symbol: symbol,
        action: action,
        amount: amount,
        tradeAmount: tradeAmount,
        riskLevel: riskLevel,
        onConfirm: () {
          hideForgeParameters();
          onConfirm?.call();
        },
        onCancel: () {
          hideForgeParameters();
          onCancel?.call();
        },
        onAdjust: () {
          hideForgeParameters();
          onAdjust?.call();
        },
      ),
    );
    
    Overlay.of(context).insert(_currentOverlay!);
  }
  
  static void hideForgeParameters() {
    _currentOverlay?.remove();
    _currentOverlay = null;
  }
}