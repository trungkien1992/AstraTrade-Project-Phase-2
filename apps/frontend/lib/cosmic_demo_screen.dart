import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:audioplayers/audioplayers.dart';
import 'dart:math' as math;

/// Cosmic Trading Demo Screen
/// Shows complete cosmic enhancement experience
class CosmicDemoScreen extends StatefulWidget {
  const CosmicDemoScreen({super.key});

  @override
  State<CosmicDemoScreen> createState() => _CosmicDemoScreenState();
}

class _CosmicDemoScreenState extends State<CosmicDemoScreen>
    with TickerProviderStateMixin {
  // Game state
  int stellarShards = 50;
  int experience = 0;
  int level = 1;
  int winStreak = 0;
  int totalTrades = 0;

  // UI state
  bool isTrading = false;
  bool showParticles = false;
  bool lastTradeSuccess = false;
  String lastMessage = "Welcome to Cosmic Trading!";

  // Audio player
  final AudioPlayer _audioPlayer = AudioPlayer();

  // Animation controllers
  late AnimationController _particleController;
  late AnimationController _statsController;

  @override
  void initState() {
    super.initState();

    _particleController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );

    _statsController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );
  }

  @override
  void dispose() {
    _particleController.dispose();
    _statsController.dispose();
    _audioPlayer.dispose();
    super.dispose();
  }

  /// Execute cosmic trade with full multisensory feedback
  Future<void> _executeCosmicTrade() async {
    if (isTrading) return;

    setState(() {
      isTrading = true;
      lastMessage = "Channeling cosmic energy...";
    });

    // Simulate trade processing
    await Future.delayed(const Duration(milliseconds: 800));

    // Determine trade outcome (70% success rate)
    final random = math.Random();
    final isSuccess = random.nextDouble() < 0.7;

    // Calculate rewards
    final currentLevel = level;
    final ssGained = _calculateStellarShards(isSuccess);
    final xpGained = _calculateExperience(isSuccess);

    // Update game state
    final oldLevel = level;
    stellarShards += ssGained;
    experience += xpGained;
    totalTrades += 1;

    if (isSuccess) {
      winStreak += 1;
    } else {
      winStreak = 0;
    }

    // Calculate new level
    level = (experience ~/ 100) + 1;
    final didLevelUp = level > oldLevel;

    // Update UI state
    setState(() {
      isTrading = false;
      showParticles = true;
      lastTradeSuccess = isSuccess;

      if (didLevelUp) {
        lastMessage =
            "🎉 COSMIC EVOLUTION! Welcome to Level $level!\n⭐ +$ssGained SS, +$xpGained XP";
      } else if (isSuccess) {
        lastMessage =
            "⭐ Stellar Alignment Achieved!\n+$ssGained Stellar Shards, +$xpGained XP";
      } else {
        lastMessage =
            "🔄 Cosmic Energy Channeled!\n+$ssGained Stellar Shards, +$xpGained XP";
      }
    });

    // Trigger multisensory feedback
    await _triggerCosmicFeedback(isSuccess, didLevelUp);

    // Animate stats update
    _statsController.forward().then((_) {
      _statsController.reset();
    });

    // Hide particles after animation
    Future.delayed(const Duration(milliseconds: 1500), () {
      if (mounted) {
        setState(() {
          showParticles = false;
        });
      }
    });
  }

  /// Calculate stellar shards reward
  int _calculateStellarShards(bool isSuccess) {
    int baseReward = isSuccess ? 15 : 3;
    double levelMultiplier = 1.0 + (level * 0.2);
    return (baseReward * levelMultiplier).round();
  }

  /// Calculate experience points
  int _calculateExperience(bool isSuccess) {
    return isSuccess ? 8 : 3;
  }

  /// Trigger haptic, audio, and visual feedback
  Future<void> _triggerCosmicFeedback(bool isSuccess, bool didLevelUp) async {
    try {
      if (didLevelUp) {
        // Level up: Special celebration
        HapticFeedback.heavyImpact();
        await Future.delayed(const Duration(milliseconds: 150));
        HapticFeedback.lightImpact();
        await _audioPlayer.play(AssetSource('audio/level_up.wav'));
      } else if (isSuccess) {
        // Success: Double tap + chime
        HapticFeedback.lightImpact();
        await Future.delayed(const Duration(milliseconds: 100));
        HapticFeedback.lightImpact();
        await _audioPlayer.play(AssetSource('audio/trade_execute.wav'));
      } else {
        // Attempt: Single pulse + soft tone
        HapticFeedback.mediumImpact();
        await _audioPlayer.setVolume(0.4);
        await _audioPlayer.play(AssetSource('audio/trade_execute.wav'));
        await Future.delayed(const Duration(milliseconds: 500));
        await _audioPlayer.setVolume(0.6);
      }
    } catch (e) {
      // Audio errors don't disrupt the experience
      debugPrint('Audio feedback error: $e');
    }
  }

  /// Get cosmic tier name based on level
  String get cosmicTier {
    if (level >= 50) return "Universal Sovereign";
    if (level >= 30) return "Stellar Architect";
    if (level >= 15) return "Genesis Awakener";
    if (level >= 5) return "Cosmic Trainee";
    return "Stellar Seedling";
  }

  /// Get cosmic tier emoji
  String get cosmicTierEmoji {
    if (level >= 50) return "🌌";
    if (level >= 30) return "⭐";
    if (level >= 15) return "✨";
    if (level >= 5) return "🌟";
    return "🌱";
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('AstraTrade - Cosmic Demo'),
        backgroundColor: Colors.purple,
        foregroundColor: Colors.white,
        elevation: 0,
      ),
      body: Stack(
        children: [
          // Main content
          SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const SizedBox(height: 20),

                // Demo title
                Text(
                  '🌟 Cosmic Trading Experience',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontSize: 24,
                    color: Colors.purple.shade300,
                  ),
                  textAlign: TextAlign.center,
                ),

                const SizedBox(height: 8),

                Text(
                  'Experience how cosmic enhancements transform trading',
                  style: Theme.of(
                    context,
                  ).textTheme.bodyMedium?.copyWith(color: Colors.grey.shade400),
                  textAlign: TextAlign.center,
                ),

                const SizedBox(height: 30),

                // Cosmic Stats Bar
                _buildCosmicStatsBar(),

                const SizedBox(height: 30),

                // Trading Interface
                _buildTradingInterface(),

                const SizedBox(height: 30),

                // Last Trade Message
                _buildLastTradeMessage(),

                const SizedBox(height: 30),

                // Cosmic Progression Info
                _buildCosmicProgression(),

                const SizedBox(height: 20),
              ],
            ),
          ),

          // Particle effects overlay
          if (showParticles)
            Positioned.fill(
              child: Center(
                child: CosmicParticleEffect(
                  isSuccess: lastTradeSuccess,
                  controller: _particleController,
                ),
              ),
            ),
        ],
      ),
    );
  }

  /// Build cosmic stats display bar
  Widget _buildCosmicStatsBar() {
    return AnimatedBuilder(
      animation: _statsController,
      builder: (context, child) {
        return Transform.scale(
          scale: 1.0 + (_statsController.value * 0.1),
          child: Card(
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  _buildStatItem(
                    icon: Icons.auto_awesome,
                    value: '$stellarShards',
                    label: 'Stellar Shards',
                    color: Colors.amber,
                  ),
                  _buildDivider(),
                  _buildStatItem(
                    icon: Icons.trending_up,
                    value: 'LVL $level',
                    label: 'Cosmic Level',
                    color: Colors.cyan,
                  ),
                  _buildDivider(),
                  _buildStatItem(
                    icon: Icons.stars,
                    value: '$experience',
                    label: 'Experience',
                    color: Colors.white,
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  /// Build individual stat item
  Widget _buildStatItem({
    required IconData icon,
    required String value,
    required String label,
    required Color color,
  }) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, color: color, size: 24),
        const SizedBox(height: 8),
        Text(
          value,
          style: const TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: TextStyle(fontSize: 12, color: Colors.grey.shade400),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }

  /// Build divider between stats
  Widget _buildDivider() {
    return Container(height: 40, width: 1, color: Colors.grey.shade600);
  }

  /// Build trading interface
  Widget _buildTradingInterface() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            Text(
              '⚡ Cosmic Energy Channel',
              style: Theme.of(
                context,
              ).textTheme.titleLarge?.copyWith(color: Colors.purple.shade300),
            ),

            const SizedBox(height: 8),

            Text(
              'Execute trades and experience cosmic rewards',
              style: TextStyle(color: Colors.grey.shade400),
              textAlign: TextAlign.center,
            ),

            const SizedBox(height: 24),

            // Trade button
            SizedBox(
              width: double.infinity,
              height: 60,
              child: ElevatedButton(
                onPressed: isTrading ? null : _executeCosmicTrade,
                style: ElevatedButton.styleFrom(
                  backgroundColor: isTrading ? Colors.grey : Colors.purple,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: isTrading
                    ? const Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(
                              color: Colors.white,
                              strokeWidth: 2,
                            ),
                          ),
                          SizedBox(width: 12),
                          Text('Channeling Energy...'),
                        ],
                      )
                    : Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const Icon(Icons.flash_on),
                          const SizedBox(width: 8),
                          Text(
                            'Execute Cosmic Trade',
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
              ),
            ),

            const SizedBox(height: 16),

            // Trading stats
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                Text('Total Trades: $totalTrades'),
                Text('Win Streak: $winStreak'),
              ],
            ),
          ],
        ),
      ),
    );
  }

  /// Build last trade message display
  Widget _buildLastTradeMessage() {
    return Card(
      color: const Color(0xFF0A1A0A),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            Text(
              '📡 Cosmic Communication',
              style: Theme.of(
                context,
              ).textTheme.titleMedium?.copyWith(color: Colors.green.shade300),
            ),
            const SizedBox(height: 12),
            Text(
              lastMessage,
              style: const TextStyle(color: Colors.white, fontSize: 16),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  /// Build cosmic progression display
  Widget _buildCosmicProgression() {
    final progressToNextLevel = (experience % 100) / 100.0;
    final xpToNextLevel = 100 - (experience % 100);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(cosmicTierEmoji, style: const TextStyle(fontSize: 24)),
                const SizedBox(width: 8),
                Text(
                  cosmicTier,
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    color: Colors.purple.shade300,
                  ),
                ),
              ],
            ),

            const SizedBox(height: 16),

            Text(
              'Progress to Level ${level + 1}',
              style: TextStyle(color: Colors.grey.shade400),
            ),

            const SizedBox(height: 8),

            LinearProgressIndicator(
              value: progressToNextLevel,
              backgroundColor: Colors.grey.shade700,
              valueColor: AlwaysStoppedAnimation<Color>(Colors.purple.shade300),
            ),

            const SizedBox(height: 8),

            Text(
              '$xpToNextLevel XP to next level',
              style: TextStyle(color: Colors.grey.shade400, fontSize: 12),
            ),
          ],
        ),
      ),
    );
  }
}

/// Simple particle effect widget for cosmic feedback
class CosmicParticleEffect extends StatefulWidget {
  final bool isSuccess;
  final AnimationController controller;

  const CosmicParticleEffect({
    super.key,
    required this.isSuccess,
    required this.controller,
  });

  @override
  State<CosmicParticleEffect> createState() => _CosmicParticleEffectState();
}

class _CosmicParticleEffectState extends State<CosmicParticleEffect> {
  @override
  void initState() {
    super.initState();
    widget.controller.forward().then((_) {
      widget.controller.reset();
    });
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: widget.controller,
      builder: (context, child) {
        return CustomPaint(
          size: const Size(200, 200),
          painter: ParticlePainter(
            progress: widget.controller.value,
            isSuccess: widget.isSuccess,
          ),
        );
      },
    );
  }
}

/// Custom painter for particle effects
class ParticlePainter extends CustomPainter {
  final double progress;
  final bool isSuccess;

  ParticlePainter({required this.progress, required this.isSuccess});

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final colors = isSuccess
        ? [Colors.amber, Colors.orange, Colors.white]
        : [Colors.cyan, Colors.blue, Colors.white];

    for (int i = 0; i < 8; i++) {
      final angle = (i / 8) * 2 * math.pi;
      final distance = 60 * progress;
      final x = center.dx + math.cos(angle) * distance;
      final y = center.dy + math.sin(angle) * distance;

      final opacity = (1.0 - progress).clamp(0.0, 1.0);
      final size = (8.0 * (1.0 - progress * 0.5)).clamp(2.0, 8.0);

      final paint = Paint()
        ..color = colors[i % colors.length].withOpacity(opacity)
        ..style = PaintingStyle.fill;

      canvas.drawCircle(Offset(x, y), size, paint);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}
