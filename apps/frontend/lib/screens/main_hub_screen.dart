import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'dart:math' as math;
import 'dart:async';

import '../providers/auth_provider.dart';
import '../providers/game_state_provider.dart';
import '../models/user.dart';
// import '../widgets/planet_view.dart';
import '../widgets/pulsating_button.dart';
import '../widgets/notification_widget.dart';
import '../widgets/cosmic_market_pulse_widget.dart';
import '../widgets/cosmic_info_tooltip.dart';
import '../widgets/cosmic_challenges_widget.dart';
// import '../widgets/forge_parameters_overlay.dart';
// import '../widgets/lumina_resource_widget.dart'; // File not found - commented out
import '../widgets/starknet_wallet_widget.dart';
import '../utils/constants.dart';
// import 'planet_status_screen.dart';
import '../api/rag_api_client.dart';
import '../services/game_service.dart';
import '../services/cosmic_challenge_service.dart';
// import '../services/dynamic_biome_service.dart';
// import '../services/enhanced_audio_service.dart';
import '../services/starknet_service.dart';
// import '../services/enhanced_haptic_service.dart';
import '../services/haptic_service.dart';
import '../services/secure_storage_service.dart';
// import '../models/planet_biome.dart';
// import 'leaderboard_screen.dart';
// import 'cosmic_forge_screen.dart';
// import 'orbital_forging_screen.dart';
// import 'cosmic_genesis_screen.dart';
// import 'constellation_management_screen.dart';
import 'trading_screen.dart';
import '../api/extended_exchange_client.dart'; // Added import for ExtendedExchangeClient
import '../config/secrets.dart';

final apiKeyProvider = StateProvider<String>((ref) => extendedExchangeApiKey);

final extendedExchangeClientProvider = Provider<ExtendedExchangeClient>((ref) {
  final apiKey = ref.watch(apiKeyProvider);
  return ExtendedExchangeClient(apiKey: apiKey);
});

class ApiKeyProvider with ChangeNotifier {
  String _apiKey;
  ApiKeyProvider(this._apiKey);
  String get apiKey => _apiKey;
  set apiKey(String key) {
    _apiKey = key;
    notifyListeners();
  }
}

class MainHubScreen extends ConsumerStatefulWidget {
  const MainHubScreen({super.key});

  @override
  ConsumerState<MainHubScreen> createState() => _MainHubScreenState();
}

class _MainHubScreenState extends ConsumerState<MainHubScreen> {
  // final List<ForgeParticleEffect> _particleEffects = [];
  late final GameService _gameService;
  final Map<String, dynamic> _visualElements = {};

  // Enhanced services
  // late final DynamicBiomeService _dynamicBiomeService;
  // late final EnhancedAudioService _audioService;
  // late final EnhancedHapticService _hapticService;
  StreamSubscription? _biomeSubscription;
  StreamSubscription? _visualSubscription;

  // Pro Mode configuration
  bool _isConfiguringProMode = false;
  // PlanetBiome? _currentBiome;
  double _evolutionProgress = 0.0;

  @override
  void initState() {
    super.initState();
    _gameService = ref.read(gameServiceProvider);
    // _dynamicBiomeService = DynamicBiomeService();
    // _audioService = EnhancedAudioService();
    // _hapticService = EnhancedHapticService();
    // _initializeEnhancedServices();
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authProvider);
    final user = authState.value;
    final gameState = ref.watch(gameStateProvider);
    final isTrading = ref.watch(isQuickTradingProvider);

    return Scaffold(
      backgroundColor: const Color(0xFF0A0A0A),
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.logout, color: Colors.white),
          onPressed: () async {
            // Sign out user to return to login screen
            ref.read(authProvider.notifier).signOut();
          },
          tooltip: 'Sign Out',
        ),
        title: LayoutBuilder(
          builder: (context, constraints) {
            // Dynamic font scaling for title overflow fix (#1)
            double fontSize = 20.0;
            if (constraints.maxWidth < 300) {
              fontSize = 16.0;
            } else if (constraints.maxWidth < 350) {
              fontSize = 18.0;
            }

            return Text(
              '${AppConstants.appName} Hub',
              style: GoogleFonts.orbitron(
                fontWeight: FontWeight.bold,
                letterSpacing: 1.5,
                fontSize: fontSize,
              ),
              overflow: TextOverflow.fade,
              softWrap: false,
            );
          },
        ),
        backgroundColor: Colors.transparent,
        elevation: 0,
        actions: [
          const NotificationWidget(),
          const SizedBox(width: 8),
          const SizedBox(width: 8),
        ],
      ),
      body: user == null
          ? const Center(child: CircularProgressIndicator())
          : Stack(
              children: [
                SingleChildScrollView(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    children: [
                      // RAG Connection Status Banner
                      _buildRagStatusBanner(),

                      // Starknet Wallet Widget (moved up for visibility)
                      _buildSimpleWalletWidget(user),

                      // User Controls (Logout)
                      // _buildUserControls(),

                      // 🌌 COSMIC COMMAND CENTER
                      _buildCosmicCommandCenter(gameState),

                      // Game Stats Header
                      // _buildGameStatsHeader(gameState),
                      const SizedBox(height: 24),

                      // Cosmic Market Pulse - Primary trading pairs
                      // _buildCosmicMarketPulseSection(),
                      const SizedBox(height: 24),

                      // Main Planet Display
                      // _buildPlanetSection(gameState),
                      const SizedBox(height: 24),

                      // Pro Mode Toggle Section
                      _buildProModeToggle(),
                      const SizedBox(height: 16),

                      // Core Game Actions
                      _buildCoreGameActions(gameState, isTrading),
                      const SizedBox(height: 24),

                      // Game Progress Section
                      _buildGameProgressSection(gameState),
                      const SizedBox(height: 24),

                      // Cosmic Genesis Grid (if unlocked)
                      // if (gameState.hasGenesisIgnition)
                      //   _buildCosmicGenesisGrid(gameState),
                    ],
                  ),
                ),

                // Particle effects overlay
                // ..._particleEffects,
              ],
            ),
    );
  }

  /// Cosmic Market Pulse section with abstract trading visualization
  // Widget _buildCosmicMarketPulseSection() {
  //   return Column(
  //     crossAxisAlignment: CrossAxisAlignment.start,
  //     children: [
  //       Row(
  //         children: [
  //           Icon(
  //             Icons.auto_awesome,
  //             color: Colors.cyan.shade400,
  //             size: 20,
  //           ),
  //           const SizedBox(width: 8),
  //           Text(
  //             'Cosmic Market Pulse',
  //             style: GoogleFonts.orbitron(
  //               fontSize: 18,
  //               fontWeight: FontWeight.bold,
  //               color: Colors.white,
  //             ),
  //           ),
  //           const Spacer(),
  //           GestureDetector(
  //             onTap: () => _navigateToTrading(),
  //             child: Container(
  //               padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
  //               decoration: BoxDecoration(
  //                 color: Colors.cyan.withOpacity(0.2),
  //                 borderRadius: BorderRadius.circular(12),
  //                 border: Border.all(color: Colors.cyan.withOpacity(0.5)),
  //               ),
  //               child: Row(
  //                 mainAxisSize: MainAxisSize.min,
  //                 children: [
  //                   Text(
  //                     'Full Charts',
  //                     style: GoogleFonts.rajdhani(
  //                       color: Colors.cyan,
  //                       fontSize: 12,
  //                       fontWeight: FontWeight.w600,
  //                     ),
  //                   ),
  //                   const SizedBox(width: 4),
  //                   Icon(
  //                     Icons.open_in_new,
  //                     color: Colors.cyan,
  //                     size: 14,
  //                   ),
  //                 ],
  //               ),
  //             ),
  //           ),
  //         ],
  //       ),
  //       const SizedBox(height: 16),

  //       // Primary cosmic trading pairs
  //       SizedBox(
  //         height: 180,
  //         child: ListView(
  //           scrollDirection: Axis.horizontal,
  //           children: [
  //             // Prime Star (Bitcoin)
  //             SizedBox(
  //               width: 280,
  //               child: CosmicMarketPulseWidget(
  //                 symbol: 'BTCUSD',
  //                 height: 180,
  //                 isCompact: true,
  //               ),
  //             ),
  //             const SizedBox(width: 16),

  //             // Ether Nexus (Ethereum)
  //             SizedBox(
  //               width: 280,
  //               child: CosmicMarketPulseWidget(
  //                 symbol: 'ETHUSD',
  //                 height: 180,
  //                 isCompact: true,
  //               ),
  //             ),
  //             const SizedBox(width: 16),

  //             // Solar Flare (Solana)
  //             SizedBox(
  //               width: 280,
  //               child: CosmicMarketPulseWidget(
  //                 symbol: 'SOLUSD',
  //                 height: 180,
  //                 isCompact: true,
  //               ),
  //             ),
  //           ],
  //         ),
  //       ),

  //       const SizedBox(height: 12),

  //       // Cosmic market summary
  //       Container(
  //         padding: const EdgeInsets.all(16),
  //         decoration: BoxDecoration(
  //           gradient: LinearGradient(
  //             colors: [
  //               Colors.deepPurple.shade900.withOpacity(0.3),
  //               Colors.indigo.shade900.withOpacity(0.3),
  //             ],
  //             begin: Alignment.topLeft,
  //             end: Alignment.bottomRight,
  //           ),
  //           borderRadius: BorderRadius.circular(12),
  //           border: Border.all(
  //             color: Colors.purple.withOpacity(0.3),
  //             width: 1,
  //           ),
  //         ),
  //         child: Row(
  //           mainAxisAlignment: MainAxisAlignment.spaceEvenly,
  //           children: [
  //             _buildCosmicMarketStat('Stellar Flows', '6', Icons.trending_up, Colors.cyan),
  //             _buildCosmicMarketStat('Energy Volume', '2.4B', Icons.bolt, Colors.purple),
  //             _buildCosmicMarketStat('Active Pairs', '6', Icons.auto_awesome, Colors.orange),
  //             _buildCosmicMarketStat('Sync Rate', '99.8%', Icons.sync, Colors.green),
  //           ],
  //         ),
  //       ),
  //     ],
  //   );
  // }

  // Widget _buildCosmicMarketStat(String label, String value, IconData icon, Color color) {
  //   return Column(
  //     children: [
  //       Icon(icon, color: color, size: 16),
  //       const SizedBox(height: 4),
  //       Text(
  //         value,
  //         style: GoogleFonts.orbitron(
  //           color: color,
  //           fontSize: 14,
  //           fontWeight: FontWeight.bold,
  //         ),
  //       ),
  //       Row(
  //         mainAxisSize: MainAxisSize.min,
  //         children: [
  //           Text(
  //             label,
  //             style: GoogleFonts.rajdhani(
  //               color: Colors.grey.shade400,
  //               fontSize: 10,
  //             ),
  //             textAlign: TextAlign.center,
  //           ),
  //           const SizedBox(width: 4),
  //           CosmicInfoTooltip(
  //             title: label,
  //             description: _getCosmicTermDescription(label),
  //             icon: icon,
  //             child: const CosmicInfoIcon(size: 12),
  //           ),
  //         ],
  //       ),
  //     ],
  //   );
  // }

  String _getCosmicTermDescription(String term) {
    switch (term) {
      case 'Stellar Flows':
        return 'Represents the current market momentum. A rising flow indicates strong buying pressure, while falling flows suggest selling pressure.';
      case 'Energy Volume':
        return 'Total trading volume across all cosmic pairs, measured in stellar energy units. Higher volume indicates more active trading.';
      case 'Active Pairs':
        return 'Number of trading pairs currently available for cosmic energy channeling. Each pair represents a unique trading opportunity.';
      case 'Sync Rate':
        return 'How well the cosmic trading system is synchronized with galactic market data. Higher sync rates ensure more accurate trading.';
      default:
        return 'A cosmic trading metric that influences your overall trading performance.';
    }
  }

  /// Game stats header showing TT, CP, XP and cosmic tier
  // Widget _buildGameStatsHeader(GameState gameState) {
  //   return Container(
  //     padding: const EdgeInsets.all(16),
  //     decoration: BoxDecoration(
  //       gradient: LinearGradient(
  //         colors: [
  //           Colors.purple.shade800.withOpacity(0.9),
  //           Colors.blue.shade800.withOpacity(0.9),
  //         ],
  //         begin: Alignment.topLeft,
  //         end: Alignment.bottomRight,
  //       ),
  //       borderRadius: BorderRadius.circular(16),
  //       border: Border.all(
  //         color: _getPlanetHealthColor(gameState.planetHealth).withOpacity(0.3),
  //         width: 2,
  //       ),
  //     ),
  //     child: Column(
  //       children: [
  //         // Cosmic Tier
  //         Text(
  //           gameState.cosmicTier.displayName,
  //           style: GoogleFonts.orbitron(
  //             fontSize: 18,
  //             fontWeight: FontWeight.bold,
  //             color: Colors.white,
  //           ),
  //         ),
  //         const SizedBox(height: 16),

  //         // Stats Row
  //         Row(
  //           mainAxisAlignment: MainAxisAlignment.spaceEvenly,
  //           children: [
  //             _buildStatColumn('Trade Tokens', '${gameState.stellarShards}', 'TT', Colors.cyan),
  //             _buildStatColumn('Cosmic Power', '${gameState.cosmicPower}', 'CP', Colors.purple),
  //             _buildStatColumn('Experience', '${gameState.experience}', 'XP', Colors.orange),
  //             // Enhanced Lumina display (always visible with locked/unlocked state)
  //             // CompactLuminaDisplay(
  //             //   luminaAmount: gameState.lumina,
  //             //   hasGenesisIgnition: gameState.hasGenesisIgnition,
  //             //   onTap: () => _showLuminaInfo(context, gameState),
  //             // ),
  //           ],
  //         ),
  //       ],
  //     ),
  //   );}

  /// Build Cosmic Command Center section
  Widget _buildCosmicCommandCenter(GameState gameState) {
    return Card(
      elevation: 12,
      color: Colors.deepPurple.shade900,
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16),
          gradient: LinearGradient(
            colors: [
              Colors.deepPurple.shade800,
              Colors.indigo.shade800,
              Colors.purple.shade900,
            ],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          border: Border.all(color: Colors.cyan.withOpacity(0.3), width: 2),
        ),
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            children: [
              // Command Center Header
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: Colors.cyan.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: Colors.cyan.withOpacity(0.5)),
                    ),
                    child: const Icon(
                      Icons.dashboard,
                      color: Colors.cyan,
                      size: 28,
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Cosmic Command Center',
                          style: GoogleFonts.orbitron(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'Level ${gameState.level} ${_getCosmicTierName(gameState.level)}',
                          style: GoogleFonts.rajdhani(
                            fontSize: 14,
                            color: Colors.cyan.shade300,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),
                  ),
                  _buildCosmicTierBadge(gameState.level),
                ],
              ),

              const SizedBox(height: 20),

              // Cosmic Stats Grid
              _buildCosmicStatsGrid(gameState),

              const SizedBox(height: 20),

              // Daily Challenges Section
              CosmicChallengesWidget(
                isExpanded: false,
                onRewardsClaimed: (rewards) {
                  // Handle challenge rewards in main hub
                  _showRewardsNotification(rewards);
                },
              ),

              const SizedBox(height: 16),

              // Quick Actions Row
              _buildQuickActionsRow(),
            ],
          ),
        ),
      ),
    );
  }

  /// Build cosmic stats grid
  Widget _buildCosmicStatsGrid(GameState gameState) {
    return Row(
      children: [
        Expanded(
          child: _buildStatCard(
            icon: Icons.auto_awesome,
            value: '${gameState.stellarShards}',
            label: 'Stellar Shards',
            color: Colors.amber,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildStatCard(
            icon: Icons.trending_up,
            value: '${gameState.experience}',
            label: 'Experience',
            color: Colors.cyan,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildStatCard(
            icon: Icons.local_fire_department,
            value: '${gameState.winStreak}',
            label: 'Win Streak',
            color: Colors.orange,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildStatCard(
            icon: Icons.analytics,
            value: '${gameState.totalTrades}',
            label: 'Total Trades',
            color: Colors.green,
          ),
        ),
      ],
    );
  }

  /// Build individual stat card
  Widget _buildStatCard({
    required IconData icon,
    required String value,
    required String label,
    required Color color,
  }) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
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
            style: const TextStyle(fontSize: 10, color: Colors.white70),
            textAlign: TextAlign.center,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }

  /// Build cosmic tier badge
  Widget _buildCosmicTierBadge(int level) {
    final tierInfo = _getCosmicTierInfo(level);

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: tierInfo['color'].withOpacity(0.2),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: tierInfo['color'].withOpacity(0.5)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(tierInfo['emoji'], style: const TextStyle(fontSize: 16)),
          const SizedBox(width: 4),
          Text(
            'LVL $level',
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.bold,
              color: tierInfo['color'],
            ),
          ),
        ],
      ),
    );
  }

  /// Build quick actions row
  Widget _buildQuickActionsRow() {
    return Row(
      children: [
        Expanded(
          child: _buildQuickActionButton(
            icon: Icons.flash_on,
            label: 'Quick Trade',
            color: Colors.purple,
            onTap: () => _navigateToTrading(),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildQuickActionButton(
            icon: Icons.insights,
            label: 'Analytics',
            color: Colors.indigo,
            onTap: () => Navigator.pushNamed(context, '/analytics'),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildQuickActionButton(
            icon: Icons.timeline,
            label: 'Streak',
            color: Colors.orange,
            onTap: () => Navigator.pushNamed(context, '/streak-tracker'),
          ),
        ),
      ],
    );
  }

  /// Build quick action button
  Widget _buildQuickActionButton({
    required IconData icon,
    required String label,
    required Color color,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: color.withOpacity(0.2),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: color.withOpacity(0.5)),
        ),
        child: Column(
          children: [
            Icon(icon, color: color, size: 24),
            const SizedBox(height: 4),
            Text(
              label,
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// Get cosmic tier name
  String _getCosmicTierName(int level) {
    if (level >= 50) return "Universal Sovereign";
    if (level >= 30) return "Stellar Architect";
    if (level >= 15) return "Genesis Awakener";
    if (level >= 5) return "Cosmic Trainee";
    return "Stellar Seedling";
  }

  /// Get cosmic tier info
  Map<String, dynamic> _getCosmicTierInfo(int level) {
    if (level >= 50) return {'emoji': '🌌', 'color': Colors.purple};
    if (level >= 30) return {'emoji': '⭐', 'color': Colors.amber};
    if (level >= 15) return {'emoji': '✨', 'color': Colors.cyan};
    if (level >= 5) return {'emoji': '🌟', 'color': Colors.orange};
    return {'emoji': '🌱', 'color': Colors.green};
  }

  /// Show rewards notification
  void _showRewardsNotification(ChallengeRewards rewards) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            const Icon(Icons.celebration, color: Colors.amber),
            const SizedBox(width: 8),
            Expanded(
              child: Text(
                '🎉 Challenge rewards: +${rewards.stellarShards} SS, +${rewards.experience} XP',
                style: const TextStyle(color: Colors.white),
              ),
            ),
          ],
        ),
        backgroundColor: Colors.green.shade700,
        duration: const Duration(seconds: 3),
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
      ),
    );
  }

  Widget _buildStatColumn(
    String label,
    String value,
    String suffix,
    Color color,
  ) {
    return Column(
      children: [
        Text(
          value,
          style: GoogleFonts.orbitron(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        Text(
          suffix,
          style: GoogleFonts.rajdhani(
            fontSize: 12,
            color: color.withOpacity(0.8),
            fontWeight: FontWeight.w600,
          ),
        ),
        Text(
          label,
          style: GoogleFonts.rajdhani(
            fontSize: 10,
            color: Colors.grey.shade400,
          ),
        ),
      ],
    );
  }

  /// Main planet display with tap-to-forge functionality
  // Widget _buildPlanetSection(GameState gameState) {
  //   return Column(
  //     children: [
  //       // Last trade message
  //       Container(
  //         padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
  //         decoration: BoxDecoration(
  //           color: Colors.black.withOpacity(0.5),
  //           borderRadius: BorderRadius.circular(20),
  //           border: Border.all(
  //             color: _getPlanetHealthColor(gameState.planetHealth).withOpacity(0.3),
  //           ),
  //         ),
  //         child: Text(
  //           gameState.lastTradeMessage,
  //           style: GoogleFonts.rajdhani(
  //             fontSize: 14,
  //             color: Colors.white,
  //             fontStyle: FontStyle.italic,
  //           ),
  //           textAlign: TextAlign.center,
  //         ),
  //       ),
  //       const SizedBox(height: 16),

  //       // Planet view
  //       // PlanetView(
  //       //   health: gameState.planetHealth,
  //       //   size: 250,
  //       //   showQuantumCore: gameState.hasGenesisIgnition,
  //       //   onTap: () => _executeBlindTapForge(gameState),
  //       //   onLongPressStart: (details) => _showForgeParameters(details, gameState),
  //       //   onLongPressEnd: (details) => {}, // Let overlay persist until user chooses action
  //       //   onLongPressCancel: () => ForgeParameterManager.hideForgeParameters(),
  //       // ),

  //       const SizedBox(height: 16),

  //       // Planet interaction info
  //       // _buildPlanetInteractionInfo(),

  //       const SizedBox(height: 8),

  //       // Planet health indicator
  //       // _buildPlanetHealthIndicator(gameState.planetHealth),

  //       const SizedBox(height: 16),

  //       // Enhanced Lumina status section
  //       // _buildLuminaStatusSection(gameState),
  //     ],
  //   );
  // }

  // Widget _buildPlanetHealthIndicator(PlanetHealth health) {
  //   String status;
  //   Color color;
  //   IconData icon;

  //   switch (health) {
  //     case PlanetHealth.flourishing:
  //       status = "Flourishing";
  //       color = Colors.green;
  //       icon = Icons.eco;
  //       break;
  //     case PlanetHealth.stable:
  //       status = "Stable";
  //       color = Colors.blue;
  //       icon = Icons.balance;
  //       break;
  //     case PlanetHealth.decaying:
  //       status = "Needs Attention";
  //       color = Colors.orange;
  //       icon = Icons.warning;
  //       break;
  //   }

  //   return Container(
  //     padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
  //     decoration: BoxDecoration(
  //       color: color.withOpacity(0.2),
  //       borderRadius: BorderRadius.circular(16),
  //       border: Border.all(color: color, width: 1),
  //     ),
  //     child: Row(
  //       mainAxisSize: MainAxisSize.min,
  //       children: [
  //         Icon(icon, size: 16, color: color),
  //         const SizedBox(width: 6),
  //         Text(
  //           'Planet: $status',
  //           style: GoogleFonts.rajdhani(
  //             fontSize: 12,
  //             color: color,
  //             fontWeight: FontWeight.w600,
  //           ),
  //         ),
  //       ],
  //     ),
  //   );
  // }

  /// Quick Trade section with pulsating button
  Widget _buildCoreGameActions(GameState gameState, bool isTrading) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            Colors.purple.shade900.withOpacity(0.7),
            Colors.indigo.shade900.withOpacity(0.7),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.purple.withOpacity(0.3), width: 2),
      ),
      child: Column(
        children: [
          Text(
            'Cosmic Forge',
            style: GoogleFonts.orbitron(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            _gameService.isProModeEnabled
                ? '⚡ Execute GASLESS trades with AVNU Paymaster\n🌐 Sepolia Testnet • Zero Gas Fees'
                : 'Channel cosmic energies through strategic trading',
            style: GoogleFonts.rajdhani(
              fontSize: 14,
              color: Colors.grey.shade300,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 20),

          // Core Game Actions Grid (2x2)
          Column(
            children: [
              // Top Row
              Row(
                children: [
                  // Quick Trade Button
                  Expanded(
                    child: SizedBox(
                      height: 80,
                      child: Container(
                        decoration: BoxDecoration(
                          borderRadius: BorderRadius.circular(12),
                          gradient: LinearGradient(
                            colors: [
                              (_gameService.isProModeEnabled
                                  ? Colors.green.shade600
                                  : Colors.purple.shade600),
                              (_gameService.isProModeEnabled
                                  ? Colors.green.shade800
                                  : Colors.purple.shade800),
                            ],
                            begin: Alignment.topCenter,
                            end: Alignment.bottomCenter,
                          ),
                        ),
                        child: ElevatedButton(
                          onPressed: isTrading ? null : () => _performTrade(),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.transparent,
                            foregroundColor: Colors.white,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                            padding: const EdgeInsets.all(12),
                            elevation: 0,
                          ),
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Text(
                                isTrading
                                    ? 'Channeling Energy...'
                                    : _gameService.isProModeEnabled
                                    ? '💎 QUICK TRADE'
                                    : '🌟 QUICK TRADE',
                                style: GoogleFonts.orbitron(
                                  color: Colors.white,
                                  fontSize: 12,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                'One-tap trades with smart defaults',
                                style: GoogleFonts.rajdhani(
                                  color: Colors.white.withOpacity(0.8),
                                  fontSize: 10,
                                  fontWeight: FontWeight.w500,
                                ),
                                textAlign: TextAlign.center,
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ),

                  const SizedBox(width: 12),

                  // Cosmic Forge Button
                  Expanded(
                    child: SizedBox(
                      height: 80,
                      child: ElevatedButton(
                        onPressed: () {}, // _navigateToCosmicForge(),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.indigo.shade600,
                          foregroundColor: Colors.white,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                          padding: const EdgeInsets.all(12),
                        ),
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const Icon(Icons.auto_awesome, size: 18),
                            const SizedBox(height: 4),
                            Text(
                              'COSMIC FORGE',
                              style: GoogleFonts.orbitron(
                                fontSize: 12,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            const SizedBox(height: 2),
                            Text(
                              'Advanced controls for custom trades',
                              style: GoogleFonts.rajdhani(
                                color: Colors.white.withOpacity(0.8),
                                fontSize: 10,
                                fontWeight: FontWeight.w500,
                              ),
                              textAlign: TextAlign.center,
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 12),

              // Bottom Row
              Row(
                children: [
                  // Orbital Forging Button
                  Expanded(
                    child: SizedBox(
                      height: 60,
                      child: ElevatedButton(
                        onPressed: () {}, // _navigateToOrbitalForging(),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.cyan.shade600,
                          foregroundColor: Colors.white,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                        ),
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const Icon(Icons.public, size: 20),
                            const SizedBox(height: 4),
                            Text(
                              'PLANET',
                              style: GoogleFonts.orbitron(
                                fontSize: 12,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),

                  const SizedBox(width: 12),

                  // Cosmic Genesis Grid Button (Pro Trader only)
                  Expanded(
                    child: SizedBox(
                      height: 60,
                      child: ElevatedButton(
                        onPressed:
                            () {}, // gameState.hasGenesisIgnition ? () => _navigateToCosmicGenesis() : null,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors
                              .grey
                              .shade700, // gameState.hasGenesisIgnition ? Colors.purple.shade600 : Colors.grey.shade700,
                          foregroundColor: Colors.white,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                        ),
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(
                              Icons
                                  .lock, // gameState.hasGenesisIgnition ? Icons.grid_view : Icons.lock,
                              size: 20,
                            ),
                            const SizedBox(height: 4),
                            Text(
                              'LOCKED', // gameState.hasGenesisIgnition ? 'GENESIS GRID' : 'LOCKED',
                              style: GoogleFonts.orbitron(
                                fontSize: 12,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),

          const SizedBox(height: 16),

          // Trading stats
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              _buildTradeStatItem('Total Trades', '${gameState.totalTrades}'),
              _buildTradeStatItem('Win Streak', '${gameState.winStreak}'),
              // if (gameState.hasGenesisIgnition)
              //   _buildTradeStatItem('Genesis Active', '✨'),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildTradeStatItem(String label, String value) {
    return Column(
      children: [
        Text(
          value,
          style: GoogleFonts.orbitron(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
        Text(
          label,
          style: GoogleFonts.rajdhani(
            fontSize: 10,
            color: Colors.grey.shade400,
          ),
        ),
      ],
    );
  }

  /// Game progress section showing upgrades and achievements
  Widget _buildGameProgressSection(GameState gameState) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Cosmic Expansion',
          style: GoogleFonts.orbitron(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
        const SizedBox(height: 16),

        // Astro-Forgers section
        Card(
          color: Colors.grey.shade900,
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Astro-Forgers: ${gameState.astroForgers}',
                      style: GoogleFonts.orbitron(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                    ElevatedButton(
                      onPressed:
                          gameState.canAfford(
                            stellarShardsCost: _calculateAstroForgerCost(
                              gameState,
                            ),
                          )
                          ? () => _purchaseAstroForger()
                          : null,
                      child: Text(
                        'Buy (${_calculateAstroForgerCost(gameState)} TT)',
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  'Automated stellar shard generation',
                  style: GoogleFonts.rajdhani(
                    fontSize: 12,
                    color: Colors.grey.shade400,
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  /// Cosmic Genesis Grid for Pro Traders
  // Widget _buildCosmicGenesisGrid(GameState gameState) {
  //   return Column(
  //     crossAxisAlignment: CrossAxisAlignment.start,
  //     children: [
  //       Text(
  //         'Cosmic Genesis Grid',
  //         style: GoogleFonts.orbitron(
  //           fontSize: 18,
  //           fontWeight: FontWeight.bold,
  //           color: Colors.white,
  //         ),
  //       ),
  //       const SizedBox(height: 16),

  //       Card(
  //         color: Colors.grey.shade900,
  //         child: Padding(
  //           padding: const EdgeInsets.all(16),
  //           child: Column(
  //             children: [
  //               Text(
  //                 'Infuse Lumina to activate cosmic nodes',
  //                 style: GoogleFonts.rajdhani(
  //                   fontSize: 14,
  //                   color: Colors.grey.shade300,
  //                 ),
  //               ),
  //               const SizedBox(height: 16),

  //               // Sample nodes grid
  //               GridView.count(
  //                 shrinkWrap: true,
  //                 physics: const NeverScrollableScrollPhysics(),
  //                 crossAxisCount: 3,
  //                 mainAxisSpacing: 8,
  //                 crossAxisSpacing: 8,
  //                 children: [
  //                   _buildCosmicNode('Graviton\nAmplifier', 'graviton_amplifier', gameState),
  //                   _buildCosmicNode('Chrono\nAccelerator', 'chrono_accelerator', gameState),
  //                   _buildCosmicNode('Bio-Synthesis\nNexus', 'bio_synthesis_nexus', gameState),
  //                 ],
  //               ),
  //             ],
  //           ),
  //         ),
  //       ),
  //     ],
  //   );
  // }

  // Widget _buildCosmicNode(String name, String nodeType, GameState gameState) {
  //   final currentLevel = gameState.cosmicNodes[nodeType] ?? 0;
  //   final upgradeCost = _calculateNodeUpgradeCost(nodeType, currentLevel);
  //   final canAfford = gameState.canAfford(luminaCost: upgradeCost);

  //   return GestureDetector(
  //     onTap: canAfford ? () => _upgradeCosmicNode(nodeType) : null,
  //     child: Container(
  //       padding: const EdgeInsets.all(8),
  //       decoration: BoxDecoration(
  //         color: currentLevel > 0
  //             ? Colors.purple.shade800.withOpacity(0.5)
  //             : Colors.grey.shade800.withOpacity(0.3),
  //         borderRadius: BorderRadius.circular(8),
  //         border: Border.all(
  //           color: currentLevel > 0 ? Colors.purple : Colors.grey,
  //           width: 1,
  //         ),
  //       ),
  //       child: Column(
  //         mainAxisAlignment: MainAxisAlignment.center,
  //         children: [
  //           Text(
  //             name,
  //             style: GoogleFonts.rajdhani(
  //               fontSize: 10,
  //               color: Colors.white,
  //               fontWeight: FontWeight.w600,
  //             ),
  //             textAlign: TextAlign.center,
  //           ),
  //           const SizedBox(height: 4),
  //           Text(
  //             'Lv. $currentLevel',
  //             style: GoogleFonts.orbitron(
  //               fontSize: 12,
  //               color: currentLevel > 0 ? Colors.purple.shade300 : Colors.grey,
  //               fontWeight: FontWeight.bold,
  //             ),
  //           ),
  //           if (canAfford) ...[
  //             const SizedBox(height: 2),
  //             Text(
  //               '$upgradeCost LM',
  //               style: GoogleFonts.rajdhani(
  //                 fontSize: 8,
  //                 color: Colors.yellow.shade300,
  //               ),
  //             ),
  //           ],
  //         ],
  //       ),
  //     ),
  //   );
  // }

  // Action methods for game interactions

  /// Perform trading operation with enhanced biome integration
  Future<void> _performTrade() async {
    ref.read(isQuickTradingProvider.notifier).state = true;

    try {
      if (_gameService.isProModeEnabled) {
        // Pro Mode: Execute real trade with biome integration
        final result = await _performRealTrade();

        // Update biome based on trading performance
        // if (result != null) {
        //   await _dynamicBiomeService.updateFromTradingPerformance(
        //     pnl: result.pnl,
        //     volume: result.volume,
        //     isWin: result.isWin,
        //     symbol: result.symbol,
        //     tradeDuration: result.duration,
        //   );

        //   // Enhanced audio feedback
        //   await _audioService.playTradingEffect(
        //     isWin: result.isWin,
        //     profit: result.pnl,
        //     volume: result.volume,
        //     biome: _getCurrentBiomeFromGameState(),
        //   );

        //   // Enhanced haptic feedback
        //   await _hapticService.triggerTradingFeedback(
        //     isWin: result.isWin,
        //     profit: result.pnl,
        //     biome: _getCurrentBiomeFromGameState(),
        //     volume: result.volume,
        //   );
        // }
      } else {
        // Simulation Mode with enhanced effects
        await ref.read(gameStateProvider.notifier).performQuickTrade();

        // Simulate biome reaction for demo
        // await _dynamicBiomeService.updateFromTradingPerformance(
        //   pnl: (math.Random().nextDouble() * 100 - 50),
        //   volume: 100.0,
        //   isWin: math.Random().nextBool(),
        //   symbol: 'BTCUSD',
        //   tradeDuration: const Duration(seconds: 5),
        // );
      }

      // Show enhanced success feedback
      if (mounted) {
        final mode = _gameService.isProModeEnabled ? 'REAL' : 'SIMULATION';
        final gameState = ref.read(gameStateProvider);

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Row(
              children: [
                const Icon(Icons.auto_awesome, color: Colors.white),
                const SizedBox(width: 8),
                Expanded(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '🚀 $mode Trade Complete!',
                        style: GoogleFonts.orbitron(
                          fontSize: 14,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                      // Text(
                      //   'Planet biome: ${_currentBiome?.name ?? 'barren'}',
                      //   style: GoogleFonts.rajdhani(
                      //     fontSize: 11,
                      //     color: Colors.white.withOpacity(0.8),
                      //   ),
                      // ),
                    ],
                  ),
                ),
              ],
            ),
            backgroundColor: _gameService.isProModeEnabled
                ? Colors.green.shade600
                : Colors.purple.shade600,
            duration: const Duration(seconds: 3),
            behavior: SnackBarBehavior.floating,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
          ),
        );
      }
    } catch (e) {
      // Show cosmic-themed error feedback with biome context
      if (mounted) {
        String errorTitle;
        String errorMessage;
        Color backgroundColor;
        IconData errorIcon;

        if (e.toString().contains('RAG') || e.toString().contains('Network')) {
          errorTitle = '✨ Cosmic Network Fluctuation';
          errorMessage =
              'Switching to simulation mode for continuous trading experience.';
          backgroundColor = Colors.purple.shade600;
          errorIcon = Icons.auto_awesome;
        } else if (e.toString().contains('Pro Mode') ||
            e.toString().contains('Extended')) {
          errorTitle = '🔮 Pro Mode Adjustment';
          errorMessage =
              'Temporarily using simulation mode. Pro Mode will reconnect automatically.';
          backgroundColor = Colors.blue.shade600;
          errorIcon = Icons.sync;
        } else {
          errorTitle = '⚡ Cosmic Interference';
          errorMessage = 'Trading systems adapting. Your progress is safe.';
          backgroundColor = Colors.indigo.shade600;
          errorIcon = Icons.auto_fix_high;
        }

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Row(
              children: [
                Icon(errorIcon, color: Colors.white, size: 20),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        errorTitle,
                        style: GoogleFonts.orbitron(
                          fontSize: 14,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        errorMessage,
                        style: GoogleFonts.rajdhani(
                          fontSize: 12,
                          color: Colors.white.withOpacity(0.9),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            backgroundColor: backgroundColor,
            duration: const Duration(seconds: 3),
            behavior: SnackBarBehavior.floating,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
          ),
        );
      }
    } finally {
      if (mounted) {
        ref.read(isQuickTradingProvider.notifier).state = false;
      }
    }
  }

  /// Get current biome from game state
  // PlanetBiome _getCurrentBiomeFromGameState() {
  //   final gameState = ref.read(gameStateProvider);
  //   return _currentBiome ?? PlanetBiome.barren;
  // }

  /// Perform real trade using Extended Exchange API
  Future<dynamic> _performRealTrade() async {
    try {
      // Get user's Starknet address for API key generation
      final authState = ref.read(authProvider);
      final user = authState.value;
      if (user == null) {
        throw Exception('User not authenticated');
      }

      final result = await _gameService.performRealTrade(
        starknetAddress: user.starknetAddress,
      );

      // Update game state with real trade results
      ref.read(gameStateProvider.notifier).updateFromRealTrade(result);

      return result;
    } catch (e) {
      // Let the calling method handle the error display
      rethrow;
    }
  }

  /// Perform manual stellar forge (planet tap)
  // Future<void> _performManualForge(GameState gameState) async {
  //   await ref.read(gameStateProvider.notifier).performManualForge();

  //   // Add particle effect at tap location
  //   if (mounted) {
  //     late final ForgeParticleEffect particleEffect;
  //     particleEffect = ForgeParticleEffect(
  //       position: const Offset(200, 200), // Center of planet
  //       color: _getPlanetHealthColor(gameState.planetHealth),
  //       onComplete: () {
  //         if (mounted) {
  //           setState(() {
  //             _particleEffects.removeWhere((effect) => effect == particleEffect);
  //           });
  //         }
  //       },
  //     );

  //     setState(() {
  //       _particleEffects.add(particleEffect);
  //     });
  //   }
  // }

  /// Purchase additional Astro-Forger
  void _purchaseAstroForger() {
    ref.read(gameStateProvider.notifier).purchaseAstroForger();

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          'New Astro-Forger acquired! Stellar Shard generation increased.',
          style: GoogleFonts.rajdhani(fontSize: 14),
        ),
        backgroundColor: Colors.cyan.shade600,
        duration: const Duration(seconds: 2),
      ),
    );
  }

  /// Upgrade a Cosmic Genesis Node
  void _upgradeCosmicNode(String nodeType) {
    ref.read(gameStateProvider.notifier).upgradeCosmicNode(nodeType);

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          'Cosmic Node upgraded! Your planet grows stronger.',
          style: GoogleFonts.rajdhani(fontSize: 14),
        ),
        backgroundColor: Colors.purple.shade600,
        duration: const Duration(seconds: 2),
      ),
    );
  }

  // Helper methods

  /// Get color based on planet health
  // Color _getPlanetHealthColor(PlanetHealth health) {
  //   switch (health) {
  //     case PlanetHealth.flourishing:
  //       return Colors.green;
  //     case PlanetHealth.stable:
  //       return Colors.blue;
  //     case PlanetHealth.decaying:
  //       return Colors.orange;
  //   }
  // }

  /// Calculate cost for next Astro-Forger
  int _calculateAstroForgerCost(GameState gameState) {
    return 100 + (gameState.astroForgers * 50);
  }

  /// Calculate cost for upgrading a Cosmic Node
  int _calculateNodeUpgradeCost(String nodeType, int currentLevel) {
    return 10 + (currentLevel * 15);
  }

  /// Navigate to the Leaderboard Screen
  // void _showLeaderboards(BuildContext context) {
  //   Navigator.of(context).push(
  //     MaterialPageRoute(
  //       builder: (context) => const LeaderboardScreen(),
  //     ),
  //   );
  // }

  // void _showConstellations(BuildContext context) {
  //   Navigator.of(context).push(
  //     MaterialPageRoute(
  //       builder: (context) => const ConstellationManagementScreen(),
  //     ),
  //   );
  // }

  /// Navigate to the Cosmic Forge Trading Screen
  // void _navigateToCosmicForge() {
  //   Navigator.of(context).push(
  //     MaterialPageRoute(
  //       builder: (context) => const CosmicForgeScreen(),
  //     ),
  //   );
  // }

  // void _navigateToOrbitalForging() {
  //   Navigator.of(context).push(
  //     MaterialPageRoute(
  //       builder: (context) => const OrbitalForgingScreen(),
  //     ),
  //   );
  // }

  // void _navigateToCosmicGenesis() {
  //   Navigator.of(context).push(
  //     MaterialPageRoute(
  //       builder: (context) => const CosmicGenesisScreen(),
  //     ),
  //   );
  // }

  void _navigateToTrading() {
    Navigator.of(
      context,
    ).push(MaterialPageRoute(builder: (context) => const TradingScreen()));
  }

  /// Initialize enhanced services
  // Future<void> _initializeEnhancedServices() async {
  //   try {
  //     // Initialize audio service
  //     await _audioService.initialize();

  //     // Initialize haptic service
  //     await _hapticService.initialize();

  //     // Initialize dynamic biome service
  //     final gameState = ref.read(gameStateProvider);
  //     if (gameState != null) {
  //       await _dynamicBiomeService.initializeDynamicBiome(
  //         initialBiome: PlanetBiomeData(
  //           biome: PlanetBiome.barren,
  //           evolutionProgress: 0.0,
  //           unlockedAt: DateTime.now(),
  //           isActive: true,
  //         ),
  //         cultivationData: PlanetCultivationData(
  //           biome: PlanetBiome.barren,
  //           cultivationLevel: 0.0,
  //           resourceGeneration: const {},
  //           unlockedFeatures: const [],
  //           lastCultivationTime: DateTime.now(),
  //         ),
  //       );

  //       // Set up biome evolution listeners
  //       _biomeSubscription = _dynamicBiomeService.evolutionStream.listen((event) {
  //         _handleBiomeEvolutionEvent(event);
  //       });

  //       _visualSubscription = _dynamicBiomeService.visualStream.listen((update) {
  //         _handleVisualUpdate(update);
  //       });

  //       // Set initial biome audio
  //       await _audioService.setBiome(PlanetBiome.barren);
  //     }
  //   } catch (e) {
  //     print('Failed to initialize enhanced services: $e');
  //   }
  // }

  /// Handle biome evolution events
  // void _handleBiomeEvolutionEvent(BiomeEvolutionEvent event) {
  //   setState(() {
  //     _currentBiome = event.newBiome;
  //     _evolutionProgress = event.progress;
  //   });

  //   // Update audio for new biome
  //   if (event.newBiome != null) {
  //     _audioService.setBiome(event.newBiome!);
  //   }
  // }

  /// Handle visual updates from biome system
  // void _handleVisualUpdate(BiomeVisualUpdate update) {
  //   // Update planet view with new visual state
  //   // This would trigger planet widget updates
  //   setState(() {
  //     // Update visual state variables
  //   });
  // }

  /// Build RAG connection status banner
  Widget _buildRagStatusBanner() {
    return FutureBuilder<bool>(
      future: _checkRagConnection(),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const SizedBox.shrink(); // Don't show while checking
        }

        final isConnected = snapshot.data ?? false;
        if (isConnected) {
          return const SizedBox.shrink(); // Don't show banner when connected
        }

        return Container(
          margin: const EdgeInsets.only(bottom: 16),
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [
                Colors.purple.shade600.withOpacity(0.9),
                Colors.blue.shade600.withOpacity(0.9),
              ],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Colors.purple.shade400.withOpacity(0.6)),
          ),
          child: Row(
            children: [
              Icon(Icons.auto_awesome, color: Colors.purple.shade200, size: 18),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '⚡ Cosmic Demo Mode Active',
                      style: GoogleFonts.orbitron(
                        fontSize: 14,
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      '⚡ Gasless Trading • AVNU Paymaster • Sepolia Testnet',
                      style: GoogleFonts.rajdhani(
                        fontSize: 11,
                        color: Colors.purple.shade100,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              ),
              // Temporary test button for View Progress fix validation
              Container(
                height: 32,
                child: ElevatedButton(
                  onPressed: () {}, // _testViewProgressFix,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.green.shade600,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 4,
                    ),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(6),
                    ),
                  ),
                  child: Text(
                    '🧪 Test Fix',
                    style: GoogleFonts.rajdhani(
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  /// Check RAG connection status (temporarily disabled for main hub loading)
  Future<bool> _checkRagConnection() async {
    try {
      // Temporarily return false to prevent blocking main hub loading
      // TODO: Re-enable when RAG backend is available
      return false;
    } catch (e) {
      return false;
    }
  }

  /// Build Pro Mode toggle section
  Widget _buildProModeToggle() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: _gameService.isProModeEnabled
              ? [
                  Colors.green.shade800.withOpacity(0.9),
                  Colors.green.shade700.withOpacity(0.9),
                ]
              : [
                  Colors.grey.shade800.withOpacity(0.9),
                  Colors.grey.shade700.withOpacity(0.9),
                ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: _gameService.isProModeEnabled
              ? Colors.green.withOpacity(0.5)
              : Colors.grey.withOpacity(0.3),
          width: 2,
        ),
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    _gameService.isProModeEnabled
                        ? 'PRO MODE ACTIVE'
                        : 'SIMULATION MODE',
                    style: GoogleFonts.orbitron(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: _gameService.isProModeEnabled
                          ? Colors.green.shade200
                          : Colors.white,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    _gameService.isProModeEnabled
                        ? 'Real funds & live markets'
                        : 'Safe practice environment',
                    style: GoogleFonts.rajdhani(
                      fontSize: 12,
                      color: Colors.grey.shade300,
                    ),
                  ),
                ],
              ),
              Switch.adaptive(
                value: _gameService.isProModeEnabled,
                onChanged: (value) => _toggleProMode(value),
                activeColor: Colors.green.shade400,
                inactiveThumbColor: Colors.grey.shade400,
              ),
            ],
          ),

          // Pro Mode status indicators
          if (_gameService.isProModeEnabled) ...[
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: Colors.green.shade900.withOpacity(0.5),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                children: [
                  Icon(Icons.security, color: Colors.green.shade300, size: 16),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Connected to Extended Exchange testnet',
                      style: GoogleFonts.rajdhani(
                        fontSize: 11,
                        color: Colors.green.shade200,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }

  /// Toggle Pro Mode on/off
  void _toggleProMode(bool enabled) {
    if (enabled) {
      _showProModeConfigDialog();
    } else {
      setState(() {
        _gameService.disableProMode();
      });

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            '🌟 Switched to Simulation Mode - Safe practice environment',
            style: GoogleFonts.rajdhani(fontSize: 14),
          ),
          backgroundColor: Colors.purple.shade600,
          duration: const Duration(seconds: 2),
        ),
      );
    }
  }

  /// Show Pro Mode configuration dialog
  void _showProModeConfigDialog() {
    final apiKeyController = TextEditingController();
    final privateKeyController = TextEditingController();

    // Demo credentials for testing
    apiKeyController.text = const String.fromEnvironment(
      'DEMO_API_KEY',
      defaultValue: 'demo_api_key_testnet',
    );
    privateKeyController.text = const String.fromEnvironment(
      'DEMO_PRIVATE_KEY',
      defaultValue: 'demo_private_key_for_testing_only',
    );

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: Colors.grey.shade900,
        title: Text(
          '💎 Enable Pro Mode',
          style: GoogleFonts.orbitron(
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Enter your Extended Exchange credentials to enable real trading:',
                style: GoogleFonts.rajdhani(color: Colors.grey.shade300),
              ),
              const SizedBox(height: 16),

              // API Key input
              Text(
                'API Key:',
                style: GoogleFonts.rajdhani(
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
              const SizedBox(height: 8),
              TextField(
                controller: apiKeyController,
                style: GoogleFonts.rajdhani(color: Colors.white),
                decoration: InputDecoration(
                  hintText: 'Your Extended Exchange API key',
                  hintStyle: GoogleFonts.rajdhani(color: Colors.grey.shade500),
                  border: OutlineInputBorder(
                    borderSide: BorderSide(color: Colors.grey.shade600),
                  ),
                  enabledBorder: OutlineInputBorder(
                    borderSide: BorderSide(color: Colors.grey.shade600),
                  ),
                ),
              ),
              const SizedBox(height: 16),

              // Private Key input
              Text(
                'Private Key:',
                style: GoogleFonts.rajdhani(
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
              const SizedBox(height: 8),
              TextField(
                controller: privateKeyController,
                obscureText: true,
                style: GoogleFonts.rajdhani(color: Colors.white),
                decoration: InputDecoration(
                  hintText: 'Your Starknet private key',
                  hintStyle: GoogleFonts.rajdhani(color: Colors.grey.shade500),
                  border: OutlineInputBorder(
                    borderSide: BorderSide(color: Colors.grey.shade600),
                  ),
                  enabledBorder: OutlineInputBorder(
                    borderSide: BorderSide(color: Colors.grey.shade600),
                  ),
                ),
              ),
              const SizedBox(height: 16),

              // Warning notice
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.orange.shade900.withOpacity(0.3),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.orange.shade600),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(
                          Icons.warning,
                          color: Colors.orange.shade400,
                          size: 16,
                        ),
                        const SizedBox(width: 8),
                        Text(
                          'TESTNET ONLY',
                          style: GoogleFonts.orbitron(
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                            color: Colors.orange.shade400,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'This connects to Extended Exchange testnet with demo funds. Real funds are not at risk.',
                      style: GoogleFonts.rajdhani(
                        fontSize: 11,
                        color: Colors.orange.shade200,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: Text(
              'Cancel',
              style: GoogleFonts.rajdhani(color: Colors.grey),
            ),
          ),
          ElevatedButton(
            onPressed: () {
              final apiKey = apiKeyController.text.trim();
              final privateKey = privateKeyController.text.trim();

              if (apiKey.isNotEmpty && privateKey.isNotEmpty) {
                Navigator.of(context).pop();
                _enableProMode(apiKey, privateKey);
              } else {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text(
                      'Please enter both API key and private key',
                      style: GoogleFonts.rajdhani(),
                    ),
                    backgroundColor: Colors.red.shade600,
                  ),
                );
              }
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.green.shade600,
            ),
            child: Text(
              'Enable Pro Mode',
              style: GoogleFonts.rajdhani(color: Colors.white),
            ),
          ),
        ],
      ),
    );
  }

  /// Enable Pro Mode with provided credentials
  void _enableProMode(String apiKey, String privateKey) async {
    try {
      setState(() {
        _isConfiguringProMode = true;
      });

      // Enable Pro Mode in game service
      _gameService.enableProMode(apiKey: apiKey, privateKey: privateKey);

      // Test connectivity
      final isConnected = await _gameService.checkExtendedExchangeHealth();

      if (mounted) {
        setState(() {
          _isConfiguringProMode = false;
        });

        if (isConnected) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(
                '💎 Pro Mode ACTIVATED! Connected to Extended Exchange testnet',
                style: GoogleFonts.rajdhani(fontSize: 14),
              ),
              backgroundColor: Colors.green.shade600,
              duration: const Duration(seconds: 3),
            ),
          );
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(
                '⚠️ Pro Mode enabled but Extended Exchange unreachable. Check network.',
                style: GoogleFonts.rajdhani(fontSize: 14),
              ),
              backgroundColor: Colors.orange.shade600,
              duration: const Duration(seconds: 3),
            ),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isConfiguringProMode = false;
        });

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'Failed to enable Pro Mode: ${e.toString()}',
              style: GoogleFonts.rajdhani(fontSize: 14),
            ),
            backgroundColor: Colors.red.shade600,
            duration: const Duration(seconds: 3),
          ),
        );
      }
    }
  }

  /// Build simple wallet widget
  Widget _buildSimpleWalletWidget(User? user) {
    // Show placeholder if no user data
    if (user == null) {
      return Container(
        margin: const EdgeInsets.symmetric(vertical: 8),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [
              Colors.grey.shade800.withOpacity(0.3),
              Colors.grey.shade700.withOpacity(0.3),
            ],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.grey.withOpacity(0.3)),
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: Colors.grey.withOpacity(0.2),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(
                Icons.account_balance_wallet,
                color: Colors.grey,
                size: 24,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Wallet Loading...',
                    style: GoogleFonts.orbitron(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                      color: Colors.grey,
                    ),
                  ),
                  Text(
                    'Please wait...',
                    style: GoogleFonts.rajdhani(
                      fontSize: 16,
                      color: Colors.grey.shade400,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      );
    }

    // Ensure we have a valid starknet address
    if (user.starknetAddress.isEmpty) {
      return Container(
        margin: const EdgeInsets.symmetric(vertical: 8),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [
              Colors.orange.shade800.withOpacity(0.3),
              Colors.red.shade800.withOpacity(0.3),
            ],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.orange.withOpacity(0.3)),
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: Colors.orange.withOpacity(0.2),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(Icons.warning, color: Colors.orange, size: 24),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Wallet Setup Required',
                    style: GoogleFonts.orbitron(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                      color: Colors.orange,
                    ),
                  ),
                  Text(
                    'No Starknet address found',
                    style: GoogleFonts.rajdhani(
                      fontSize: 16,
                      color: Colors.orange.shade300,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      );
    }

    final displayAddress =
        '${user.starknetAddress.substring(0, 6)}...${user.starknetAddress.substring(user.starknetAddress.length - 4)}';

    return Container(
      margin: const EdgeInsets.symmetric(vertical: 8),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            Colors.blue.shade800.withOpacity(0.3),
            Colors.purple.shade800.withOpacity(0.3),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.cyan.withOpacity(0.3)),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Colors.cyan.withOpacity(0.2),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(
              Icons.account_balance_wallet,
              color: Colors.cyan,
              size: 24,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Starknet Wallet',
                  style: GoogleFonts.orbitron(
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                    color: Colors.cyan,
                  ),
                ),
                Text(
                  displayAddress,
                  style: GoogleFonts.rajdhani(
                    fontSize: 16,
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
          IconButton(
            icon: const Icon(Icons.copy, color: Colors.grey, size: 18),
            onPressed: () {
              Clipboard.setData(ClipboardData(text: user.starknetAddress));
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Starknet address copied to clipboard'),
                ),
              );
            },
            tooltip: 'Copy Address',
          ),
        ],
      ),
    );
  }
}
