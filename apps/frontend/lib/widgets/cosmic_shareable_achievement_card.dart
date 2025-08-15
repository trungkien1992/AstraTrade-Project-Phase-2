import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:share_plus/share_plus.dart';
import 'package:path_provider/path_provider.dart';
import 'dart:ui' as ui;
import 'dart:typed_data';
import 'dart:math' as math;
import 'dart:io';

import '../services/social_sharing_service.dart';
import '../widgets/cosmic_particle_effect.dart';

/// Privacy-preserving shareable achievement card with cosmic theming
/// Transforms trading achievements into space exploration narratives
/// Enables viral sharing without exposing financial data
class CosmicShareableAchievementCard extends StatefulWidget {
  final Map<String, dynamic> cosmicAchievement;
  final String cosmicCallsign;
  final String? constellationName;
  final VoidCallback? onShare;
  final bool showShareButton;
  final bool enableParticleEffects;

  const CosmicShareableAchievementCard({
    super.key,
    required this.cosmicAchievement,
    required this.cosmicCallsign,
    this.constellationName,
    this.onShare,
    this.showShareButton = true,
    this.enableParticleEffects = true,
  });

  @override
  State<CosmicShareableAchievementCard> createState() => _CosmicShareableAchievementCardState();
}

class _CosmicShareableAchievementCardState extends State<CosmicShareableAchievementCard>
    with TickerProviderStateMixin {
  late AnimationController _glowController;
  late AnimationController _particleController;
  late Animation<double> _glowAnimation;
  late Animation<double> _scaleAnimation;
  
  bool _isSharing = false;
  bool _showParticles = false;

  @override
  void initState() {
    super.initState();
    
    _glowController = AnimationController(
      duration: const Duration(seconds: 2),
      vsync: this,
    );
    
    _particleController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );
    
    _glowAnimation = Tween<double>(
      begin: 0.3,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _glowController,
      curve: Curves.easeInOut,
    ));
    
    _scaleAnimation = Tween<double>(
      begin: 1.0,
      end: 1.05,
    ).animate(CurvedAnimation(
      parent: _glowController,
      curve: Curves.easeInOut,
    ));
    
    _glowController.repeat(reverse: true);
    
    // Trigger initial particle effect for high-tier achievements
    if (widget.enableParticleEffects && _isHighTierAchievement()) {
      Future.delayed(const Duration(milliseconds: 500), () {
        if (mounted) {
          setState(() {
            _showParticles = true;
          });
          _particleController.forward();
        }
      });
    }
  }

  @override
  void dispose() {
    _glowController.dispose();
    _particleController.dispose();
    super.dispose();
  }

  bool _isHighTierAchievement() {
    final category = widget.cosmicAchievement['category'] as String? ?? '';
    return category.contains('command_mastery') || category.contains('academy_training');
  }

  Color _getCategoryColor() {
    final visualTheme = widget.cosmicAchievement['visual_theme'] as Map<String, dynamic>? ?? {};
    final colorHex = visualTheme['primary_color'] as String? ?? '#4A90E2';
    
    // Convert hex to Color
    final hex = colorHex.replaceAll('#', '');
    return Color(int.parse('FF$hex', radix: 16));
  }

  Color _getSecondaryColor() {
    final visualTheme = widget.cosmicAchievement['visual_theme'] as Map<String, dynamic>? ?? {};
    final colorHex = visualTheme['secondary_color'] as String? ?? '#7ED321';
    
    final hex = colorHex.replaceAll('#', '');
    return Color(int.parse('FF$hex', radix: 16));
  }

  String _getIconName() {
    final visualTheme = widget.cosmicAchievement['visual_theme'] as Map<String, dynamic>? ?? {};
    return visualTheme['icon'] as String? ?? 'stellar_compass';
  }

  Widget _buildCosmicIcon() {
    final iconName = _getIconName();
    final primaryColor = _getCategoryColor();
    
    // Map cosmic icon names to actual icons
    IconData iconData;
    switch (iconName) {
      case 'academy_badge':
        iconData = Icons.school_outlined;
        break;
      case 'stellar_compass':
        iconData = Icons.explore_outlined;
        break;
      case 'constellation_link':
        iconData = Icons.hub_outlined;
        break;
      case 'shield_emblem':
        iconData = Icons.shield_outlined;
        break;
      case 'flame_trail':
        iconData = Icons.local_fire_department_outlined;
        break;
      case 'navigation_compass':
        iconData = Icons.navigation_outlined;
        break;
      case 'command_insignia':
        iconData = Icons.stars_outlined;
        break;
      case 'diplomatic_seal':
        iconData = Icons.handshake_outlined;
        break;
      case 'explorer_badge':
        iconData = Icons.rocket_launch_outlined;
        break;
      case 'supreme_insignia':
        iconData = Icons.workspace_premium_outlined;
        break;
      default:
        iconData = Icons.military_tech_outlined;
    }
    
    return Container(
      width: 60,
      height: 60,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        gradient: RadialGradient(
          colors: [
            primaryColor.withOpacity(0.8),
            primaryColor.withOpacity(0.3),
          ],
        ),
        boxShadow: [
          BoxShadow(
            color: primaryColor.withOpacity(0.4),
            blurRadius: 20,
            spreadRadius: 5,
          ),
        ],
      ),
      child: Icon(
        iconData,
        size: 32,
        color: Colors.white,
      ),
    );
  }

  Widget _buildCosmicBackground() {
    final primaryColor = _getCategoryColor();
    final secondaryColor = _getSecondaryColor();
    
    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(20),
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            primaryColor.withOpacity(0.1),
            secondaryColor.withOpacity(0.05),
            Colors.black.withOpacity(0.8),
          ],
          stops: const [0.0, 0.5, 1.0],
        ),
      ),
      child: Stack(
        children: [
          // Animated starfield background
          _buildStarField(),
          // Cosmic grid overlay
          _buildCosmicGrid(),
        ],
      ),
    );
  }

  Widget _buildStarField() {
    return AnimatedBuilder(
      animation: _glowController,
      builder: (context, child) {
        return CustomPaint(
          painter: StarFieldPainter(
            animationValue: _glowAnimation.value,
            primaryColor: _getCategoryColor(),
          ),
          size: Size.infinite,
        );
      },
    );
  }

  Widget _buildCosmicGrid() {
    return AnimatedBuilder(
      animation: _glowController,
      builder: (context, child) {
        return CustomPaint(
          painter: CosmicGridPainter(
            animationValue: _glowAnimation.value,
            primaryColor: _getCategoryColor().withOpacity(0.1),
          ),
          size: Size.infinite,
        );
      },
    );
  }

  Widget _buildAchievementContent() {
    final title = widget.cosmicAchievement['title'] as String? ?? 'Cosmic Achievement';
    final description = widget.cosmicAchievement['description'] as String? ?? '';
    final abstractedMetrics = widget.cosmicAchievement['abstracted_metrics'] as Map<String, dynamic>? ?? {};
    
    return Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header with icon and title
          Row(
            children: [
              _buildCosmicIcon(),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Commander ${widget.cosmicCallsign}',
                      style: TextStyle(
                        fontSize: 14,
                        color: _getCategoryColor(),
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 16),
          
          // Description
          Text(
            description,
            style: const TextStyle(
              fontSize: 14,
              color: Colors.white70,
              height: 1.4,
            ),
          ),
          
          const SizedBox(height: 16),
          
          // Abstracted metrics (safe for sharing)
          if (abstractedMetrics.isNotEmpty) ...[
            _buildMetricsSection(abstractedMetrics),
            const SizedBox(height: 16),
          ],
          
          // Constellation context
          if (widget.constellationName != null) ...[
            _buildConstellationBadge(),
            const SizedBox(height: 16),
          ],
          
          // Cosmic timestamp
          _buildCosmicTimestamp(),
        ],
      ),
    );
  }

  Widget _buildMetricsSection(Map<String, dynamic> metrics) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(12),
        color: Colors.black.withOpacity(0.3),
        border: Border.all(
          color: _getCategoryColor().withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Mission Details',
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.bold,
              color: _getCategoryColor(),
            ),
          ),
          const SizedBox(height: 8),
          ...metrics.entries.map((entry) => Padding(
            padding: const EdgeInsets.symmetric(vertical: 2),
            child: Row(
              children: [
                Container(
                  width: 4,
                  height: 4,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: _getSecondaryColor(),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    entry.value.toString(),
                    style: const TextStyle(
                      fontSize: 12,
                      color: Colors.white70,
                    ),
                  ),
                ),
              ],
            ),
          )).toList(),
        ],
      ),
    );
  }

  Widget _buildConstellationBadge() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(20),
        gradient: LinearGradient(
          colors: [
            _getCategoryColor().withOpacity(0.3),
            _getSecondaryColor().withOpacity(0.3),
          ],
        ),
        border: Border.all(
          color: _getCategoryColor().withOpacity(0.5),
          width: 1,
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            Icons.hub_outlined,
            size: 16,
            color: _getCategoryColor(),
          ),
          const SizedBox(width: 6),
          Text(
            '${widget.constellationName} Constellation',
            style: TextStyle(
              fontSize: 12,
              color: _getCategoryColor(),
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCosmicTimestamp() {
    final now = DateTime.now();
    final stardate = 'Stardate ${now.year}.${now.month.toString().padLeft(2, '0')}.${now.day.toString().padLeft(2, '0')}';
    
    return Row(
      children: [
        Icon(
          Icons.access_time,
          size: 14,
          color: Colors.white54,
        ),
        const SizedBox(width: 6),
        Text(
          stardate,
          style: const TextStyle(
            fontSize: 12,
            color: Colors.white54,
            fontStyle: FontStyle.italic,
          ),
        ),
      ],
    );
  }

  Widget _buildShareButton() {
    if (!widget.showShareButton) return const SizedBox.shrink();
    
    return Positioned(
      top: 16,
      right: 16,
      child: AnimatedScale(
        scale: _isSharing ? 0.9 : 1.0,
        duration: const Duration(milliseconds: 200),
        child: Container(
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            gradient: RadialGradient(
              colors: [
                _getCategoryColor().withOpacity(0.8),
                _getCategoryColor().withOpacity(0.4),
              ],
            ),
            boxShadow: [
              BoxShadow(
                color: _getCategoryColor().withOpacity(0.3),
                blurRadius: 10,
                spreadRadius: 2,
              ),
            ],
          ),
          child: IconButton(
            onPressed: _isSharing ? null : _handleShare,
            icon: Icon(
              _isSharing ? Icons.hourglass_empty : Icons.share,
              color: Colors.white,
              size: 20,
            ),
          ),
        ),
      ),
    );
  }

  Future<void> _handleShare() async {
    if (_isSharing) return;
    
    setState(() {
      _isSharing = true;
    });
    
    try {
      // Haptic feedback
      HapticFeedback.lightImpact();
      
      // Trigger particle effect
      if (widget.enableParticleEffects) {
        setState(() {
          _showParticles = true;
        });
        _particleController.reset();
        _particleController.forward();
      }
      
      // Generate shareable content
      final shareText = _generateShareText();
      
      // Capture widget as image for sharing
      final imageFile = await _captureWidgetAsImage();
      
      if (imageFile != null) {
        await Share.shareXFiles(
          [XFile(imageFile.path)],
          text: shareText,
          subject: 'Cosmic Achievement Unlocked! 🚀',
        );
      } else {
        await Share.share(
          shareText,
          subject: 'Cosmic Achievement Unlocked! 🚀',
        );
      }
      
      // Trigger callback
      widget.onShare?.call();
      
    } catch (e) {
      // Handle sharing error
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Unable to share achievement: ${e.toString()}'),
          backgroundColor: Colors.red,
        ),
      );
    } finally {
      if (mounted) {
        setState(() {
          _isSharing = false;
        });
      }
    }
  }

  String _generateShareText() {
    final title = widget.cosmicAchievement['title'] as String? ?? 'Cosmic Achievement';
    final category = widget.cosmicAchievement['category'] as String? ?? 'exploration';
    
    final shareTemplates = {
      'academy_training': '🎓 Just graduated from the Galactic Trading Academy! $title achieved. Ready to explore the cosmos? #CosmicTrading #LearningJourney',
      'stellar_navigation': '🛡️ Mastered the art of safe space navigation! $title unlocked. Join the academy: [INVITE_CODE] #SafeTrading #CosmicAcademy',
      'fleet_operations': '🚀 Advanced fleet coordination achieved! $title complete. Building a stronger galactic community. #FleetCommand #CosmicStrategy',
      'diplomatic_relations': '🤝 Forged new alliances across the galaxy! $title earned. Unity makes us stronger. #CosmicDiplomacy #Community',
      'exploration_missions': '🌌 Discovered new frontiers in space trading! $title accomplished. Adventure awaits! #CosmicExploration #Discovery',
      'command_mastery': '⭐ Achieved supreme command excellence! $title mastered. Leading the way to the stars. #CommandMastery #EliteTrader',
    };
    
    return shareTemplates[category] ?? 
           '🚀 $title achieved in the Galactic Trading Arena! Join the cosmic journey: [INVITE_CODE] #CosmicTrading #Academy';
  }

  Future<XFile?> _captureWidgetAsImage() async {
    try {
      final RenderRepaintBoundary boundary = context.findRenderObject() as RenderRepaintBoundary;
      final ui.Image image = await boundary.toImage(pixelRatio: 3.0);
      final ByteData? byteData = await image.toByteData(format: ui.ImageByteFormat.png);
      
      if (byteData != null) {
        final Uint8List pngBytes = byteData.buffer.asUint8List();
        
        // Save to temporary file
        final tempDir = await getTemporaryDirectory();
        final file = File('${tempDir.path}/cosmic_achievement_${DateTime.now().millisecondsSinceEpoch}.png');
        await file.writeAsBytes(pngBytes);
        
        return XFile(file.path);
      }
    } catch (e) {
      print('Error capturing widget as image: $e');
    }
    
    return null;
  }

  @override
  Widget build(BuildContext context) {
    return RepaintBoundary(
      child: AnimatedBuilder(
        animation: _scaleAnimation,
        builder: (context, child) {
          return Transform.scale(
            scale: _scaleAnimation.value,
            child: Container(
              width: double.infinity,
              margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: Stack(
                children: [
                  // Background with cosmic effects
                  ClipRRect(
                    borderRadius: BorderRadius.circular(20),
                    child: _buildCosmicBackground(),
                  ),
                  
                  // Main content
                  ClipRRect(
                    borderRadius: BorderRadius.circular(20),
                    child: _buildAchievementContent(),
                  ),
                  
                  // Share button
                  _buildShareButton(),
                  
                  // Particle effects overlay
                  if (_showParticles && widget.enableParticleEffects)
                    Positioned.fill(
                      child: CosmicParticleEffect(
                        isSuccess: true,
                        effectType: _getParticleEffectType(),
                        particleCount: 12,
                        intensity: 1.0,
                        onComplete: () {
                          if (mounted) {
                            setState(() {
                              _showParticles = false;
                            });
                          }
                        },
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

  ParticleEffectType _getParticleEffectType() {
    final celebrationType = widget.cosmicAchievement['celebration_type'] as String? ?? 'stellar_sparkles';
    
    switch (celebrationType) {
      case 'supernova_explosion':
        return ParticleEffectType.burst;
      case 'constellation_formation':
        return ParticleEffectType.spiral;
      case 'knowledge_aurora':
        return ParticleEffectType.shimmer;
      default:
        return ParticleEffectType.starField;
    }
  }
}

/// Custom painter for animated starfield background
class StarFieldPainter extends CustomPainter {
  final double animationValue;
  final Color primaryColor;
  
  StarFieldPainter({
    required this.animationValue,
    required this.primaryColor,
  });
  
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..style = PaintingStyle.fill;
    
    final random = math.Random(42); // Fixed seed for consistent star positions
    
    for (int i = 0; i < 50; i++) {
      final x = random.nextDouble() * size.width;
      final y = random.nextDouble() * size.height;
      final starSize = random.nextDouble() * 2 + 0.5;
      final opacity = (math.sin(animationValue * math.pi * 2 + i) * 0.3 + 0.7).clamp(0.0, 1.0);
      
      paint.color = primaryColor.withOpacity(opacity * 0.6);
      canvas.drawCircle(Offset(x, y), starSize, paint);
    }
  }
  
  @override
  bool shouldRepaint(StarFieldPainter oldDelegate) {
    return oldDelegate.animationValue != animationValue;
  }
}

/// Custom painter for cosmic grid overlay
class CosmicGridPainter extends CustomPainter {
  final double animationValue;
  final Color primaryColor;
  
  CosmicGridPainter({
    required this.animationValue,
    required this.primaryColor,
  });
  
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 0.5
      ..color = primaryColor.withOpacity(animationValue * 0.3);
    
    const gridSize = 40.0;
    
    // Draw vertical lines
    for (double x = 0; x <= size.width; x += gridSize) {
      canvas.drawLine(
        Offset(x, 0),
        Offset(x, size.height),
        paint,
      );
    }
    
    // Draw horizontal lines
    for (double y = 0; y <= size.height; y += gridSize) {
      canvas.drawLine(
        Offset(0, y),
        Offset(size.width, y),
        paint,
      );
    }
  }
  
  @override
  bool shouldRepaint(CosmicGridPainter oldDelegate) {
    return oldDelegate.animationValue != animationValue;
  }
}