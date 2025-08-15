import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/simple_trade.dart';
import '../services/simple_trading_service.dart';
import '../providers/trading_provider.dart';
import '../providers/game_state_provider.dart';
import '../providers/tutorial_provider.dart';
import '../services/rating_service.dart';
import '../services/analytics_service.dart';
import '../services/cosmic_reward_service.dart';
import '../services/cosmic_audio_service.dart';
import '../widgets/cosmic_particle_effect.dart';
import '../widgets/tutorial_overlay_widget.dart';
import '../widgets/milestone_celebration.dart';
import '../utils/responsive_helper.dart';
import 'dart:math' as math;

class TradeResultScreen extends ConsumerStatefulWidget {
  final SimpleTrade trade;

  const TradeResultScreen({super.key, required this.trade});

  @override
  ConsumerState<TradeResultScreen> createState() => _TradeResultScreenState();
}

class _TradeResultScreenState extends ConsumerState<TradeResultScreen>
    with TickerProviderStateMixin {
  late AnimationController _animationController;
  late AnimationController _cosmicController;
  late Animation<double> _scaleAnimation;
  late Animation<double> _cosmicFadeAnimation;

  SimpleTrade? _completedTrade;
  bool _isProcessing = true;

  // Cosmic rewards state
  int _stellarShardsGained = 0;
  int _experienceGained = 0;
  bool _didLevelUp = false;
  bool _showCosmicRewards = false;
  String _cosmicMessage = "";
  int _oldLevel = 1;
  int _newLevel = 1;

  // Tutorial keys for targeting UI elements
  final GlobalKey _resultsKey = GlobalKey();
  final GlobalKey _rewardsKey = GlobalKey();
  final GlobalKey _progressKey = GlobalKey();

  @override
  void initState() {
    super.initState();

    _animationController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );

    _cosmicController = AnimationController(
      duration: const Duration(milliseconds: 1200),
      vsync: this,
    );

    _scaleAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.elasticOut),
    );

    _cosmicFadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _cosmicController, curve: Curves.easeInOut),
    );

    _processTrade();
  }

  @override
  void dispose() {
    _animationController.dispose();
    _cosmicController.dispose();
    super.dispose();
  }

  void _processTrade() async {
    // Simulate processing time
    await Future.delayed(const Duration(seconds: 2));

    final completedTrade = SimpleTradingService.completeTrade(widget.trade);

    // 🌟 CALCULATE COSMIC REWARDS
    await _calculateCosmicRewards(completedTrade);

    // Track completed trade
    await AnalyticsService.trackTradeCompleted(
      symbol: completedTrade.symbol,
      direction: completedTrade.direction,
      amount: completedTrade.amount,
      profitLoss: completedTrade.profitLoss!,
      profitLossPercentage: completedTrade.profitLossPercentage,
      isProfit: completedTrade.profitLoss! > 0,
    );

    // Update in provider
    ref.read(tradingProvider.notifier).updateTrade(completedTrade);

    setState(() {
      _completedTrade = completedTrade;
      _isProcessing = false;
    });

    // Start trade result animation
    _animationController.forward();

    // Show cosmic rewards after trade result is visible
    Future.delayed(const Duration(milliseconds: 1200), () {
      if (mounted) {
        setState(() {
          _showCosmicRewards = true;
        });
        _cosmicController.forward();

        // Trigger cosmic celebration effects
        _triggerCosmicCelebration();

        // Check if user needs results tutorial
        final tutorialNotifier = ref.read(tutorialProvider.notifier);
        if (tutorialNotifier.shouldShowResultsTutorial()) {
          Future.delayed(const Duration(milliseconds: 1000), () {
            if (mounted) {
              tutorialNotifier.startTutorial('results');
            }
          });
        }
      }
    });
  }

  /// Calculate cosmic rewards for the completed trade
  Future<void> _calculateCosmicRewards(SimpleTrade trade) async {
    try {
      // Get current game state
      final gameState = ref.read(gameStateProvider);
      _oldLevel = gameState.level;

      // Calculate cosmic rewards
      _stellarShardsGained = CosmicRewardService.calculateStellarShards(
        trade,
        gameState.level,
      );
      _experienceGained = CosmicRewardService.calculateExperience(trade);

      final pnl = trade.profitLoss ?? trade.unrealizedPnL ?? 0.0;
      final isSuccess = pnl > 0;

      // Add cosmic rewards to game state
      ref
          .read(gameStateProvider.notifier)
          .addCosmicRewards(
            stellarShards: _stellarShardsGained,
            experience: _experienceGained,
            isSuccess: isSuccess,
          );

      // Check for level up
      final newGameState = ref.read(gameStateProvider);
      _newLevel = newGameState.level;
      _didLevelUp = _newLevel > _oldLevel;

      // Generate cosmic message
      if (_didLevelUp) {
        _cosmicMessage =
            "🎉 COSMIC EVOLUTION! Welcome to Level $_newLevel!\n⭐ +$_stellarShardsGained SS, +$_experienceGained XP";
      } else if (isSuccess) {
        _cosmicMessage =
            "⭐ Stellar Alignment Achieved!\n+$_stellarShardsGained Stellar Shards, +$_experienceGained XP";
      } else {
        _cosmicMessage =
            "🔄 Cosmic Energy Channeled!\n+$_stellarShardsGained Stellar Shards, +$_experienceGained XP";
      }
    } catch (e) {
      debugPrint('⚠️ Cosmic rewards calculation error: $e');
      // Fallback values
      _stellarShardsGained = 5;
      _experienceGained = 2;
      _cosmicMessage =
          "🌟 Cosmic Energy Received!\n+$_stellarShardsGained Stellar Shards, +$_experienceGained XP";
    }
  }

  /// Trigger cosmic celebration effects
  void _triggerCosmicCelebration() async {
    try {
      final pnl = _completedTrade?.profitLoss ?? 0.0;
      
      if (_didLevelUp) {
        // Level up celebration with milestone overlay
        HapticFeedback.heavyImpact();
        await Future.delayed(const Duration(milliseconds: 200));
        HapticFeedback.lightImpact();
        await CosmicAudioService.playLevelUpFanfare();
        
        // Show milestone celebration after a brief delay
        Future.delayed(const Duration(milliseconds: 1500), () {
          if (mounted) {
            MilestoneUtils.showLevelUp(context, _newLevel);
          }
        });
      } else if (pnl > 100) {
        // Big win celebration for profits over $100
        HapticFeedback.heavyImpact();
        await CosmicAudioService.playSuccessChime();
        
        Future.delayed(const Duration(milliseconds: 1000), () {
          if (mounted) {
            MilestoneUtils.showBigWin(context, pnl);
          }
        });
      } else if (pnl > 0) {
        // Regular success celebration
        HapticFeedback.lightImpact();
        await Future.delayed(const Duration(milliseconds: 100));
        HapticFeedback.lightImpact();
        await CosmicAudioService.playSuccessChime();
      } else {
        // Participation reward
        HapticFeedback.mediumImpact();
        await CosmicAudioService.playAttemptTone();
      }

      // Check for win streak milestone
      final tradingState = ref.read(tradingProvider);
      final winStreak = tradingState.progress.currentStreak;
      if (pnl > 0 && winStreak > 0 && winStreak % 5 == 0) {
        // Celebrate win streaks of 5, 10, 15, etc.
        Future.delayed(const Duration(milliseconds: 2000), () {
          if (mounted) {
            MilestoneUtils.showWinStreak(context, winStreak);
          }
        });
      }

      // Check for first trade milestone
      if (tradingState.progress.totalTrades == 1) {
        Future.delayed(const Duration(milliseconds: 2500), () {
          if (mounted) {
            MilestoneUtils.showFirstTrade(context);
          }
        });
      }
    } catch (e) {
      debugPrint('⚠️ Cosmic celebration error: $e');
    }
  }

  /// Build cosmic rewards celebration section
  Widget _buildCosmicRewardsSection() {
    return FadeTransition(
      opacity: _cosmicFadeAnimation,
      child: Stack(
        children: [
          Card(
            key: _rewardsKey,
            elevation: 12,
            color: _didLevelUp
                ? Colors.purple.shade900
                : Colors.indigo.shade900,
            child: Container(
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(12),
                gradient: LinearGradient(
                  colors: _didLevelUp
                      ? [Colors.purple.shade800, Colors.pink.shade800]
                      : [Colors.indigo.shade800, Colors.blue.shade800],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                border: Border.all(
                  color: _didLevelUp ? Colors.amber : Colors.cyan,
                  width: 2,
                ),
              ),
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  children: [
                    // Cosmic header
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(
                          _didLevelUp ? Icons.auto_awesome : Icons.stars,
                          color: _didLevelUp ? Colors.amber : Colors.cyan,
                          size: 32,
                        ),
                        const SizedBox(width: 12),
                        Text(
                          _didLevelUp ? 'COSMIC EVOLUTION!' : 'COSMIC REWARDS',
                          style: TextStyle(
                            fontSize: _didLevelUp ? 20 : 18,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                            letterSpacing: 1.2,
                          ),
                        ),
                      ],
                    ),

                    const SizedBox(height: 16),

                    // Cosmic message
                    Text(
                      _cosmicMessage,
                      style: const TextStyle(
                        fontSize: 16,
                        color: Colors.white,
                        height: 1.4,
                      ),
                      textAlign: TextAlign.center,
                    ),

                    const SizedBox(height: 20),

                    // Rewards display
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                      children: [
                        _buildRewardItem(
                          icon: Icons.auto_awesome,
                          value: '+$_stellarShardsGained',
                          label: 'Stellar Shards',
                          color: Colors.amber,
                        ),
                        _buildRewardDivider(),
                        _buildRewardItem(
                          icon: Icons.trending_up,
                          value: '+$_experienceGained',
                          label: 'Experience',
                          color: Colors.cyan,
                        ),
                        if (_didLevelUp) ...[
                          _buildRewardDivider(),
                          _buildRewardItem(
                            icon: Icons.military_tech,
                            value: '$_newLevel',
                            label: 'New Level',
                            color: Colors.amber,
                          ),
                        ],
                      ],
                    ),

                    // Level progress (if not leveled up)
                    if (!_didLevelUp) ...[
                      const SizedBox(height: 16),
                      _buildLevelProgress(),
                    ],
                  ],
                ),
              ),
            ),
          ),

          // Particle effects overlay
          if (_didLevelUp)
            Positioned.fill(
              child: IgnorePointer(
                child: CosmicParticleEffect(isSuccess: true, onComplete: () {}),
              ),
            ),
        ],
      ),
    );
  }

  /// Build individual reward item
  Widget _buildRewardItem({
    required IconData icon,
    required String value,
    required String label,
    required Color color,
  }) {
    return Column(
      children: [
        Icon(icon, color: color, size: 24),
        const SizedBox(height: 8),
        Text(
          value,
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: const TextStyle(fontSize: 12, color: Colors.white70),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }

  /// Build reward divider
  Widget _buildRewardDivider() {
    return Container(height: 50, width: 1, color: Colors.white30);
  }

  /// Build level progress display
  Widget _buildLevelProgress() {
    final gameState = ref.watch(gameStateProvider);
    final progressToNextLevel = (gameState.experience % 100) / 100.0;
    final xpToNextLevel = 100 - (gameState.experience % 100);

    return Column(
      children: [
        Text(
          'Progress to Level ${gameState.level + 1}',
          style: const TextStyle(color: Colors.white70, fontSize: 14),
        ),
        const SizedBox(height: 8),
        LinearProgressIndicator(
          value: progressToNextLevel,
          backgroundColor: Colors.white30,
          valueColor: const AlwaysStoppedAnimation<Color>(Colors.cyan),
        ),
        const SizedBox(height: 4),
        Text(
          '$xpToNextLevel XP to next level',
          style: const TextStyle(color: Colors.white60, fontSize: 12),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return TutorialWrapper(
      tutorialId: 'results',
      steps: TutorialContent.getResultsSteps(
        resultsKey: _resultsKey,
        rewardsKey: _rewardsKey,
        progressKey: _progressKey,
      ),
      child: ResponsiveScaffold(
      appBar: AppBar(
        title: const Text('Trade Result'),
        backgroundColor: Colors.blue[600],
        foregroundColor: Colors.white,
        automaticallyImplyLeading: false,
      ),
      body: ResponsiveBuilder(
        builder: (context, deviceType) {
          final isMobile = ResponsiveHelper.isMobile(context);
          
          return Column(
          children: [
            SizedBox(height: isMobile ? 40 : 60),

            if (_isProcessing) ...[
              const CircularProgressIndicator(),
              const SizedBox(height: 20),
              const Text(
                'Processing your trade...',
                style: TextStyle(fontSize: 18),
              ),
              const SizedBox(height: 10),
              Text(
                '${widget.trade.direction} \$${widget.trade.amount.toInt()} ${widget.trade.symbol}',
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ] else if (_completedTrade != null) ...[
              ScaleTransition(
                scale: _scaleAnimation,
                child: Card(
                  key: _resultsKey,
                  elevation: 8,
                  child: Padding(
                    padding: const EdgeInsets.all(24.0),
                    child: Column(
                      children: [
                        Icon(
                          _completedTrade!.profitLossPercentage > 0
                              ? Icons.trending_up
                              : Icons.trending_down,
                          size: 64,
                          color: _completedTrade!.profitLossPercentage > 0
                              ? Colors.green
                              : Colors.red,
                        ),
                        const SizedBox(height: 16),

                        Text(
                          SimpleTradingService.getTradeMessage(
                            _completedTrade!,
                          ),
                          style: const TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                          ),
                          textAlign: TextAlign.center,
                        ),

                        const SizedBox(height: 20),

                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceAround,
                          children: [
                            Column(
                              children: [
                                const Text(
                                  'Trade Amount',
                                  style: TextStyle(
                                    fontSize: 14,
                                    color: Colors.grey,
                                  ),
                                ),
                                Text(
                                  '\$${_completedTrade!.amount.toInt()}',
                                  style: const TextStyle(
                                    fontSize: 18,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ],
                            ),
                            Column(
                              children: [
                                const Text(
                                  'Profit/Loss',
                                  style: TextStyle(
                                    fontSize: 14,
                                    color: Colors.grey,
                                  ),
                                ),
                                Text(
                                  '\$${_completedTrade!.profitLoss!.toStringAsFixed(2)}',
                                  style: TextStyle(
                                    fontSize: 18,
                                    fontWeight: FontWeight.bold,
                                    color: _completedTrade!.profitLoss! > 0
                                        ? Colors.green
                                        : Colors.red,
                                  ),
                                ),
                              ],
                            ),
                            Column(
                              children: [
                                const Text(
                                  'Return',
                                  style: TextStyle(
                                    fontSize: 14,
                                    color: Colors.grey,
                                  ),
                                ),
                                Text(
                                  '${_completedTrade!.profitLossPercentage > 0 ? '+' : ''}${_completedTrade!.profitLossPercentage.toStringAsFixed(1)}%',
                                  style: TextStyle(
                                    fontSize: 18,
                                    fontWeight: FontWeight.bold,
                                    color:
                                        _completedTrade!.profitLossPercentage >
                                            0
                                        ? Colors.green
                                        : Colors.red,
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
              ),

              // 🌟 COSMIC REWARDS SECTION
              if (_showCosmicRewards) ...[
                const SizedBox(height: 20),
                _buildCosmicRewardsSection(),
              ],
            ],

            const Spacer(),

            if (!_isProcessing) ...[
              SizedBox(
                width: double.infinity,
                height: 56,
                child: ElevatedButton.icon(
                  key: _progressKey,
                  onPressed: _handleViewProgress,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.purple[600],
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  icon: const Icon(Icons.insights),
                  label: const Text(
                    'View Cosmic Progress',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                ),
              ),

              const SizedBox(height: 12),

              SizedBox(
                width: double.infinity,
                height: 56,
                child: OutlinedButton.icon(
                  onPressed: _handleTradeAgain,
                  style: OutlinedButton.styleFrom(
                    side: BorderSide(color: Colors.purple[400]!),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  icon: const Icon(Icons.flash_on),
                  label: Text(
                    'Channel More Energy',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: Colors.purple[400],
                    ),
                  ),
                ),
              ),
            ],

            const SizedBox(height: 20),
          ],
        );
        },
      ),
      ), // Close TutorialWrapper
    );
  }

  void _handleViewProgress() {
    // Mark results tutorial as completed if this is the first time viewing results
    final tutorialNotifier = ref.read(tutorialProvider.notifier);
    if (tutorialNotifier.shouldShowResultsTutorial()) {
      tutorialNotifier.completeResultsTutorial();
    }

    _checkForRatingPrompt(() {
      Navigator.pushNamed(context, '/streak-tracker');
    });
  }

  void _handleTradeAgain() {
    _checkForRatingPrompt(() {
      Navigator.pushNamed(context, '/trade-entry');
    });
  }

  void _checkForRatingPrompt(VoidCallback onContinue) async {
    final tradingState = ref.read(tradingProvider);
    final progress = tradingState.progress;

    final shouldShow = await RatingService.shouldShowRatingPrompt(
      totalTrades: progress.totalTrades,
      currentStreak: progress.currentStreak,
      hasSubscription: progress.hasSubscription,
    );

    if (shouldShow && mounted) {
      await RatingService.markRatingPromptShown();

      final ratingResult = await RatingService.showRatingDialog(context);

      if (ratingResult == true && mounted) {
        // User interacted with rating prompt
        onContinue();
      } else if (mounted) {
        // User dismissed or skipped rating
        onContinue();
      }
    } else {
      onContinue();
    }
  }
}
