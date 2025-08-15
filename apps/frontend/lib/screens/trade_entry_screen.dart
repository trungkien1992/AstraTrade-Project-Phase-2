import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'dart:math' as math;
import '../models/simple_trade.dart';
import '../services/real_trading_service.dart';
import '../providers/trading_provider.dart';
import '../providers/game_state_provider.dart';
import '../providers/tutorial_provider.dart';
import '../services/exit_intent_service.dart';
import '../services/analytics_service.dart';
import '../services/cosmic_reward_service.dart';
import '../services/cosmic_audio_service.dart';
import '../services/cosmic_challenge_service.dart';
import '../onboarding/paywall.dart';
import '../widgets/game_stats_bar.dart';
import '../widgets/cosmic_particle_effect.dart';
import '../widgets/cosmic_challenges_widget.dart';
import '../widgets/tutorial_overlay_widget.dart';
import '../widgets/interactive_card.dart';
import '../navigation/page_transitions.dart';
import '../utils/responsive_helper.dart';
import '../utils/performance_optimizer.dart';
import 'trade_result_screen.dart';

class TradeEntryScreen extends ConsumerStatefulWidget {
  const TradeEntryScreen({super.key});

  @override
  ConsumerState<TradeEntryScreen> createState() => _TradeEntryScreenState();
}

class _TradeEntryScreenState extends ConsumerState<TradeEntryScreen> {
  double _selectedAmount = 100;
  String _selectedDirection = 'BUY';
  String _selectedSymbol = 'ETH-USD';
  bool _isLoading = false;

  // Cosmic integration state
  bool _showParticles = false;
  bool _lastTradeSuccess = false;

  // Cosmic power-ups state
  bool _energyBoostActive = false;
  bool _cosmicInsightActive = false;
  bool _shieldProtectionActive = false;
  bool _showPowerUpSelector = false;

  // Cosmic challenges state
  bool _showChallenges = false;
  Set<String> _tradedSymbols = {};

  // Tutorial keys for targeting UI elements
  final GlobalKey _amountKey = GlobalKey();
  final GlobalKey _directionKey = GlobalKey();
  final GlobalKey _symbolKey = GlobalKey();
  final GlobalKey _tradeButtonKey = GlobalKey();

  @override
  void initState() {
    super.initState();
    // Schedule analytics tracking and tutorial check for next frame
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final tradingState = ref.read(tradingProvider);
      AnalyticsService.trackScreenView(
        'trade_entry_screen',
        properties: {
          'free_trades_remaining': tradingState.freeTrades,
          'has_subscription': tradingState.progress.hasSubscription,
          'total_trades': tradingState.progress.totalTrades,
        },
      );

      // Check if user needs trading tutorial
      final tutorialNotifier = ref.read(tutorialProvider.notifier);
      if (tutorialNotifier.shouldShowTradingTutorial()) {
        // Delay tutorial to let UI settle
        Future.delayed(const Duration(milliseconds: 500), () {
          if (mounted) {
            tutorialNotifier.startTutorial('trading');
          }
        });
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final tradingState = ref.watch(tradingProvider);
    final tutorialState = ref.watch(tutorialProvider);

    return TutorialWrapper(
      tutorialId: 'trading',
      steps: TutorialContent.getTradingSteps(
        amountKey: _amountKey,
        directionKey: _directionKey,
        symbolKey: _symbolKey,
        tradeButtonKey: _tradeButtonKey,
      ),
      child: ResponsiveScaffold(
      appBar: AppBar(
        title: const Text('Place Trade'),
        backgroundColor: Colors.blue[600],
        foregroundColor: Colors.white,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () {
            // If this is the main screen, exit or show confirmation
            Navigator.pushReplacementNamed(context, '/streak-tracker');
          },
        ),
      ),
      body: CosmicParticleOverlay(
        showParticles: _showParticles,
        isSuccess: _lastTradeSuccess,
        onParticlesComplete: () {
          setState(() {
            _showParticles = false;
          });
        },
        child: ResponsiveBuilder(
          builder: (context, deviceType) {
            final responsivePadding = ResponsiveHelper.getResponsivePadding(context);
            final isMobile = ResponsiveHelper.isMobile(context);
            
            return Padding(
              padding: responsivePadding,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  SizedBox(height: isMobile ? 20 : 32),

              // Game Stats Bar (Phase 1: Gamification Integration)
              const GameStatsBar().optimizeRepaints(),

              const SizedBox(height: 16),

              // 🏆 COSMIC CHALLENGES SECTION
              CosmicChallengesWidget(
                isExpanded: _showChallenges,
                onToggle: () {
                  setState(() {
                    _showChallenges = !_showChallenges;
                  });
                },
                onRewardsClaimed: (rewards) {
                  // Add challenge rewards to game state
                  ref
                      .read(gameStateProvider.notifier)
                      .addCosmicRewards(
                        stellarShards: rewards.stellarShards,
                        experience: rewards.experience,
                        isSuccess: true,
                        customMessage:
                            "🏆 Daily Challenge Rewards Claimed!\n+${rewards.stellarShards} SS, +${rewards.experience} XP",
                      );
                },
              ).optimizeRepaints(),

              const SizedBox(height: 16),

              // Amount Selection
              InteractiveCard(
                key: _amountKey,
                child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Trade Amount',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 12),
                      Wrap(
                        spacing: 8,
                        children: RealTradingService.getAvailableAmounts()
                            .map(
                              (amount) => ChoiceChip(
                                label: Text('\$${amount.toInt()}'),
                                selected: _selectedAmount == amount,
                                onSelected: (selected) {
                                  if (selected) {
                                    setState(() {
                                      _selectedAmount = amount;
                                    });
                                  }
                                },
                              ),
                            )
                            .toList(),
                      ),
                    ],
                ),
              ),

              const SizedBox(height: 16),

              // Direction Selection
              InteractiveCard(
                key: _directionKey,
                child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Direction',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 12),
                      Row(
                        children: [
                          Expanded(
                            child: ChoiceChip(
                              label: const Text('BUY'),
                              selected: _selectedDirection == 'BUY',
                              selectedColor: Colors.green[200],
                              onSelected: (selected) {
                                if (selected) {
                                  setState(() {
                                    _selectedDirection = 'BUY';
                                  });
                                }
                              },
                            ),
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: ChoiceChip(
                              label: const Text('SELL'),
                              selected: _selectedDirection == 'SELL',
                              selectedColor: Colors.red[200],
                              onSelected: (selected) {
                                if (selected) {
                                  setState(() {
                                    _selectedDirection = 'SELL';
                                  });
                                }
                              },
                            ),
                          ),
                        ],
                      ),
                    ],
                ),
              ),

              const SizedBox(height: 16),

              // Symbol Selection
              InteractiveCard(
                key: _symbolKey,
                child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Token Pair',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 12),
                      DropdownButtonFormField<String>(
                        value: _selectedSymbol,
                        decoration: const InputDecoration(
                          border: OutlineInputBorder(),
                        ),
                        items: RealTradingService.getAvailableSymbols()
                            .map(
                              (symbol) => DropdownMenuItem(
                                value: symbol,
                                child: Text(symbol),
                              ),
                            )
                            .toList(),
                        onChanged: (value) {
                          if (value != null) {
                            setState(() {
                              _selectedSymbol = value;
                            });
                          }
                        },
                      ),
                    ],
                ),
              ),

              const SizedBox(height: 20),

              // 🌟 COSMIC POWER-UP SECTION
              _buildCosmicPowerUpSection(),

              const Spacer(),

              // Trade Button
              SizedBox(
                width: double.infinity,
                height: isMobile ? 56 : 64,
                child: AnimatedInteractiveButton(
                  key: _tradeButtonKey,
                  onPressed: _isLoading ? null : _placeTrade,
                  backgroundColor: Colors.blue[600],
                  foregroundColor: Colors.white,
                  isLoading: _isLoading,
                  icon: _selectedDirection == 'BUY' ? Icons.trending_up : Icons.trending_down,
                  child: Text(
                    '${_selectedDirection} \$${_selectedAmount.toInt()} ${_selectedSymbol}',
                    style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                ),
              ),

                  const SizedBox(height: 20),
                ],
              ),
            );
          },
        ),
      ),
      ), // Close TutorialWrapper
    );
  }

  /// Build cosmic power-up selection section
  Widget _buildCosmicPowerUpSection() {
    final gameState = ref.watch(gameStateProvider);

    return Card(
      elevation: 4,
      color: Colors.indigo.shade900,
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(12),
          gradient: LinearGradient(
            colors: [Colors.indigo.shade800, Colors.purple.shade800],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          border: Border.all(color: Colors.cyan.withOpacity(0.5)),
        ),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              Row(
                children: [
                  const Icon(Icons.auto_awesome, color: Colors.cyan, size: 24),
                  const SizedBox(width: 8),
                  const Text(
                    'Cosmic Energy Boosts',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                  const Spacer(),
                  Text(
                    '${gameState.stellarShards} SS',
                    style: const TextStyle(
                      fontSize: 14,
                      color: Colors.amber,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 12),

              // Power-up options
              Row(
                children: [
                  Expanded(
                    child: _buildPowerUpOption(
                      icon: Icons.flash_on,
                      title: 'Energy Boost',
                      description: '+50% SS reward',
                      cost: 20,
                      isActive: _energyBoostActive,
                      canAfford: gameState.stellarShards >= 20,
                      onTap: () => _togglePowerUp('energy'),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: _buildPowerUpOption(
                      icon: Icons.visibility,
                      title: 'Cosmic Insight',
                      description: 'Market trend hint',
                      cost: 15,
                      isActive: _cosmicInsightActive,
                      canAfford: gameState.stellarShards >= 15,
                      onTap: () => _togglePowerUp('insight'),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: _buildPowerUpOption(
                      icon: Icons.shield,
                      title: 'Shield',
                      description: 'Reduce loss impact',
                      cost: 25,
                      isActive: _shieldProtectionActive,
                      canAfford: gameState.stellarShards >= 25,
                      onTap: () => _togglePowerUp('shield'),
                    ),
                  ),
                ],
              ),

              // Active power-ups indicator
              if (_energyBoostActive ||
                  _cosmicInsightActive ||
                  _shieldProtectionActive) ...[
                const SizedBox(height: 12),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 8,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.green.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.green.withOpacity(0.5)),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.power, color: Colors.green, size: 16),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          'Cosmic energies are aligned for your next trade!',
                          style: TextStyle(
                            color: Colors.green.shade300,
                            fontSize: 12,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  /// Build individual power-up option
  Widget _buildPowerUpOption({
    required IconData icon,
    required String title,
    required String description,
    required int cost,
    required bool isActive,
    required bool canAfford,
    required VoidCallback onTap,
  }) {
    final isEnabled = canAfford && !isActive;

    return GestureDetector(
      onTap: isEnabled ? onTap : null,
      child: Container(
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(
          color: isActive
              ? Colors.green.withOpacity(0.3)
              : isEnabled
              ? Colors.white.withOpacity(0.1)
              : Colors.grey.withOpacity(0.1),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: isActive
                ? Colors.green
                : isEnabled
                ? Colors.cyan.withOpacity(0.5)
                : Colors.grey.withOpacity(0.3),
          ),
        ),
        child: Column(
          children: [
            Icon(
              icon,
              color: isActive
                  ? Colors.green
                  : isEnabled
                  ? Colors.cyan
                  : Colors.grey,
              size: 20,
            ),
            const SizedBox(height: 4),
            Text(
              title,
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.bold,
                color: isActive
                    ? Colors.green
                    : isEnabled
                    ? Colors.white
                    : Colors.grey,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 2),
            Text(
              description,
              style: TextStyle(
                fontSize: 9,
                color: isActive
                    ? Colors.green.shade300
                    : isEnabled
                    ? Colors.white70
                    : Colors.grey,
              ),
              textAlign: TextAlign.center,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
            const SizedBox(height: 2),
            Text(
              '$cost SS',
              style: TextStyle(
                fontSize: 10,
                color: Colors.amber.withOpacity(isEnabled ? 1.0 : 0.5),
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// Toggle power-up activation
  void _togglePowerUp(String type) async {
    final gameState = ref.read(gameStateProvider);

    switch (type) {
      case 'energy':
        if (!_energyBoostActive && gameState.stellarShards >= 20) {
          setState(() {
            _energyBoostActive = true;
          });
          // Deduct stellar shards
          ref
              .read(gameStateProvider.notifier)
              .addCosmicRewards(
                stellarShards: -20,
                experience: 0,
                isSuccess: true,
                customMessage:
                    "⚡ Energy Boost Activated! Next trade rewards +50%",
              );
          // Track power-up usage for challenges
          CosmicChallengeService.updateChallengeProgress(
            challengeType: 'powerup_used',
          );
          CosmicChallengeService.updateChallengeProgress(
            challengeType: 'stellar_shards_spent',
            value: 20,
          );
          HapticFeedback.lightImpact();
        }
        break;
      case 'insight':
        if (!_cosmicInsightActive && gameState.stellarShards >= 15) {
          setState(() {
            _cosmicInsightActive = true;
          });
          // Deduct stellar shards and show market insight
          ref
              .read(gameStateProvider.notifier)
              .addCosmicRewards(
                stellarShards: -15,
                experience: 0,
                isSuccess: true,
                customMessage:
                    "🔮 Cosmic Insight Activated! Market trends revealed",
              );
          // Track power-up usage for challenges
          CosmicChallengeService.updateChallengeProgress(
            challengeType: 'powerup_used',
          );
          CosmicChallengeService.updateChallengeProgress(
            challengeType: 'stellar_shards_spent',
            value: 15,
          );
          _showCosmicInsight();
          HapticFeedback.lightImpact();
        }
        break;
      case 'shield':
        if (!_shieldProtectionActive && gameState.stellarShards >= 25) {
          setState(() {
            _shieldProtectionActive = true;
          });
          // Deduct stellar shards
          ref
              .read(gameStateProvider.notifier)
              .addCosmicRewards(
                stellarShards: -25,
                experience: 0,
                isSuccess: true,
                customMessage:
                    "🛡️ Shield Protection Activated! Loss impact reduced",
              );
          // Track power-up usage for challenges
          CosmicChallengeService.updateChallengeProgress(
            challengeType: 'powerup_used',
          );
          CosmicChallengeService.updateChallengeProgress(
            challengeType: 'stellar_shards_spent',
            value: 25,
          );
          HapticFeedback.lightImpact();
        }
        break;
    }
  }

  /// Show cosmic market insight
  void _showCosmicInsight() {
    final insights = [
      '🌟 The cosmic winds favor ${'BUY' == _selectedDirection ? 'upward' : 'downward'} movement',
      '✨ Stellar alignments suggest ${_selectedSymbol.split('-')[0]} energy is strong',
      '🔮 The cosmic oracle sees favorable conditions ahead',
      '⭐ Universal forces align with your trading intention',
    ];

    final randomInsight =
        insights[DateTime.now().millisecond % insights.length];

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            const Icon(Icons.auto_awesome, color: Colors.amber),
            const SizedBox(width: 8),
            Expanded(
              child: Text(
                randomInsight,
                style: const TextStyle(color: Colors.white),
              ),
            ),
          ],
        ),
        backgroundColor: Colors.indigo.shade800,
        duration: const Duration(seconds: 4),
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
      ),
    );
  }

  void _placeTrade() async {
    final tradingState = ref.read(tradingProvider);

    // Track trade attempt
    await AnalyticsService.trackUserAction(
      'trade_attempted',
      properties: {
        'symbol': _selectedSymbol,
        'direction': _selectedDirection,
        'amount': _selectedAmount,
        'free_trades_remaining': tradingState.freeTrades,
        'has_subscription': tradingState.progress.hasSubscription,
      },
    );

    // Check if user can trade
    if (!ref.read(tradingProvider.notifier).canTrade()) {
      // Show exit intent dialog first
      final exitIntentResult = await ExitIntentService.showExitIntentDialog(
        context,
      );

      if (exitIntentResult != true) {
        // If user didn't accept exit intent offer, show regular paywall
        final paywallResult = await Navigator.push<bool>(
          context,
          MaterialPageRoute(
            builder: (context) =>
                const PaywallScreen(trigger: 'trade_limit_reached'),
          ),
        );

        if (paywallResult != true) {
          return; // User didn't subscribe
        }
      }

      // User has now subscribed, continue with trade
    }

    setState(() {
      _isLoading = true;
    });

    try {
      // 🚀 EXECUTE REAL END-TO-END TRADE
      debugPrint('🎯 Starting REAL END-TO-END TRADE execution');
      debugPrint('   Amount: \$${_selectedAmount}');
      debugPrint('   Direction: $_selectedDirection');
      debugPrint('   Symbol: $_selectedSymbol');

      final trade = await RealTradingService.executeRealTrade(
        amount: _selectedAmount,
        direction: _selectedDirection,
        symbol: _selectedSymbol,
      );

      debugPrint(
        '✅ REAL TRADE COMPLETED: ${trade.isRealTrade ? 'SUCCESS' : 'FALLBACK'}',
      );

      // Track successful trade start
      await AnalyticsService.trackTradeStarted(
        symbol: _selectedSymbol,
        direction: _selectedDirection,
        amount: _selectedAmount,
      );

      // Add trade to provider
      ref.read(tradingProvider.notifier).addTrade(trade);

      // 🌟 ADD COSMIC REWARDS (non-disruptive integration)
      await _addCosmicRewards(trade);

      // Mark trading tutorial as completed if this is the first trade
      final tutorialNotifier = ref.read(tutorialProvider.notifier);
      if (tutorialNotifier.shouldShowTradingTutorial()) {
        await tutorialNotifier.completeTradingTutorial();
      }

      // Navigate to result screen with custom transition
      if (mounted) {
        Navigator.of(context).pushReplacementCosmic(
          TradeResultScreen(trade: trade),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error placing trade: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  /// Update cosmic challenge progress based on trade results
  void _updateChallengeProgress(SimpleTrade trade, bool isSuccess) {
    try {
      // Track symbol diversity
      _tradedSymbols.add(trade.symbol);

      // Update various challenge types
      CosmicChallengeService.updateChallengeProgress(
        challengeType: 'trade_executed',
      );

      if (isSuccess) {
        CosmicChallengeService.updateChallengeProgress(
          challengeType: 'trade_success',
        );
      }

      // Update win streak
      final gameState = ref.read(gameStateProvider);
      CosmicChallengeService.updateChallengeProgress(
        challengeType: 'win_streak',
        data: {'streak': gameState.winStreak},
      );

      // Update stellar shards earned
      final pnl = trade.profitLoss ?? trade.unrealizedPnL ?? 0.0;
      if (pnl > 0) {
        final ssEarned = CosmicRewardService.calculateStellarShards(
          trade,
          gameState.level,
        );
        CosmicChallengeService.updateChallengeProgress(
          challengeType: 'stellar_shards_earned',
          value: ssEarned,
        );
      }

      // Update symbol diversity
      CosmicChallengeService.updateChallengeProgress(
        challengeType: 'symbol_traded',
        data: {'tradedSymbols': _tradedSymbols.toList()},
      );

      debugPrint('🎯 Challenge progress updated for trade');
    } catch (e) {
      debugPrint('⚠️ Challenge tracking error (non-critical): $e');
    }
  }

  /// Consume active power-ups after trade execution
  void _consumePowerUps() {
    setState(() {
      _energyBoostActive = false;
      _cosmicInsightActive = false;
      _shieldProtectionActive = false;
    });
    debugPrint('🌟 All cosmic power-ups consumed');
  }

  /// Add cosmic rewards and feedback for completed trades
  /// This enhances the trading experience without disrupting existing functionality
  Future<void> _addCosmicRewards(SimpleTrade trade) async {
    try {
      // Get current game state
      final gameState = ref.read(gameStateProvider);

      // Calculate base cosmic rewards
      int stellarShardsGained = CosmicRewardService.calculateStellarShards(
        trade,
        gameState.level,
      );
      int experienceGained = CosmicRewardService.calculateExperience(trade);
      final pnl = trade.profitLoss ?? trade.unrealizedPnL ?? 0.0;
      bool isSuccess = pnl > 0;

      // 🌟 APPLY COSMIC POWER-UP BONUSES
      if (_energyBoostActive) {
        stellarShardsGained = (stellarShardsGained * 1.5).round();
        debugPrint('⚡ Energy Boost applied: +50% Stellar Shards');
      }

      if (_shieldProtectionActive && !isSuccess && pnl < 0) {
        // Shield reduces loss impact - convert some losses to small gains
        debugPrint('🛡️ Shield Protection activated: Loss impact reduced');
        // For demonstration, shield gives small consolation rewards
        stellarShardsGained = math.max(stellarShardsGained, 8);
        experienceGained = math.max(experienceGained, 4);
      }

      // Check for level up before adding rewards
      final currentLevel = gameState.level;

      // Add cosmic rewards to game state
      ref
          .read(gameStateProvider.notifier)
          .addCosmicRewards(
            stellarShards: stellarShardsGained,
            experience: experienceGained,
            isSuccess: isSuccess,
          );

      // Check if player leveled up
      final newGameState = ref.read(gameStateProvider);
      final didLevelUp = newGameState.level > currentLevel;

      // 🌟 CONSUME POWER-UPS AFTER USE
      _consumePowerUps();

      // 🎯 UPDATE COSMIC CHALLENGES
      _updateChallengeProgress(trade, isSuccess);

      // Update particle effect state
      setState(() {
        _lastTradeSuccess = isSuccess;
        _showParticles = true;
      });

      // Add multisensory feedback (haptic + audio)
      if (didLevelUp) {
        // Level up: Special celebration
        HapticFeedback.heavyImpact();
        await Future.delayed(const Duration(milliseconds: 150));
        HapticFeedback.lightImpact();
        await CosmicAudioService.playLevelUpFanfare();
      } else if (isSuccess) {
        // Success: Light double-tap + success chime
        HapticFeedback.lightImpact();
        await Future.delayed(const Duration(milliseconds: 100));
        HapticFeedback.lightImpact();
        await CosmicAudioService.playSuccessChime();
      } else {
        // Attempt: Single medium impact + soft tone
        HapticFeedback.mediumImpact();
        await CosmicAudioService.playAttemptTone();
      }

      debugPrint(
        '🌟 Cosmic rewards added: +$stellarShardsGained SS, +$experienceGained XP',
      );
    } catch (e) {
      // Cosmic rewards are enhancement only - don't let errors disrupt trading
      debugPrint('⚠️ Cosmic rewards error (non-critical): $e');
    }
  }
}
