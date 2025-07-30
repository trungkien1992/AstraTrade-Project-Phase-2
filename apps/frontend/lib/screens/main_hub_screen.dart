import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'dart:math' as math;
import 'dart:async';

import '../providers/auth_provider.dart';
import '../providers/game_state_provider.dart';
import '../models/user.dart';
import '../widgets/planet_view.dart';
import '../widgets/pulsating_button.dart';
import '../widgets/notification_widget.dart';
import '../widgets/cosmic_market_pulse_widget.dart';
import '../widgets/cosmic_info_tooltip.dart';
import '../widgets/forge_parameters_overlay.dart';
import '../widgets/lumina_resource_widget.dart';
import '../widgets/starknet_wallet_widget.dart';
import '../utils/constants.dart';
import 'planet_status_screen.dart';
import '../api/rag_api_client.dart';
import '../services/game_service.dart';
import '../services/dynamic_biome_service.dart';
import '../services/enhanced_audio_service.dart';
import '../services/starknet_service.dart';
import '../services/enhanced_haptic_service.dart';
import '../services/haptic_service.dart';
import '../services/secure_storage_service.dart';
import '../models/planet_biome.dart';
import 'leaderboard_screen.dart';
import 'cosmic_forge_screen.dart';
import 'orbital_forging_screen.dart';
import 'cosmic_genesis_screen.dart';
import 'constellation_management_screen.dart';
import 'trading_screen.dart';
import '../api/extended_exchange_client.dart'; // Added import for ExtendedExchangeClient
import '../config/secrets.dart';

final apiKeyProvider = StateProvider<String>((ref) => EXTENDED_EXCHANGE_API_KEY);

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
  final List<ForgeParticleEffect> _particleEffects = [];
  late final GameService _gameService;
  final Map<String, dynamic> _visualElements = {};
  
  // Enhanced services
  late final DynamicBiomeService _dynamicBiomeService;
  late final EnhancedAudioService _audioService;
  late final EnhancedHapticService _hapticService;
  StreamSubscription? _biomeSubscription;
  StreamSubscription? _visualSubscription;
  
  // Pro Mode configuration
  bool _isConfiguringProMode = false;
  PlanetBiome? _currentBiome;
  double _evolutionProgress = 0.0;

  @override
  void initState() {
    super.initState();
    _gameService = ref.read(gameServiceProvider);
    _dynamicBiomeService = DynamicBiomeService();
    _audioService = EnhancedAudioService();
    _hapticService = EnhancedHapticService();
    _initializeEnhancedServices();
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
                      _buildUserControls(),
                      
                      // Game Stats Header
                      _buildGameStatsHeader(gameState),
                      const SizedBox(height: 24),

                      // Cosmic Market Pulse - Primary trading pairs
                      _buildCosmicMarketPulseSection(),
                      const SizedBox(height: 24),

                      // Main Planet Display
                      _buildPlanetSection(gameState),
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
                      if (gameState.hasGenesisIgnition)
                        _buildCosmicGenesisGrid(gameState),
                    ],
                  ),
                ),
                
                // Particle effects overlay
                ..._particleEffects,
              ],
            ),
    );
  }

  /// Cosmic Market Pulse section with abstract trading visualization
  Widget _buildCosmicMarketPulseSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(
              Icons.auto_awesome,
              color: Colors.cyan.shade400,
              size: 20,
            ),
            const SizedBox(width: 8),
            Text(
              'Cosmic Market Pulse',
              style: GoogleFonts.orbitron(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
            const Spacer(),
            GestureDetector(
              onTap: () => _navigateToTrading(),
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: Colors.cyan.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.cyan.withOpacity(0.5)),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      'Full Charts',
                      style: GoogleFonts.rajdhani(
                        color: Colors.cyan,
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(width: 4),
                    Icon(
                      Icons.open_in_new,
                      color: Colors.cyan,
                      size: 14,
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        
        // Primary cosmic trading pairs
        SizedBox(
          height: 180,
          child: ListView(
            scrollDirection: Axis.horizontal,
            children: [
              // Prime Star (Bitcoin)
              SizedBox(
                width: 280,
                child: CosmicMarketPulseWidget(
                  symbol: 'BTCUSD',
                  height: 180,
                  isCompact: true,
                ),
              ),
              const SizedBox(width: 16),
              
              // Ether Nexus (Ethereum)
              SizedBox(
                width: 280,
                child: CosmicMarketPulseWidget(
                  symbol: 'ETHUSD',
                  height: 180,
                  isCompact: true,
                ),
              ),
              const SizedBox(width: 16),
              
              // Solar Flare (Solana)
              SizedBox(
                width: 280,
                child: CosmicMarketPulseWidget(
                  symbol: 'SOLUSD',
                  height: 180,
                  isCompact: true,
                ),
              ),
            ],
          ),
        ),
        
        const SizedBox(height: 12),
        
        // Cosmic market summary
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [
                Colors.deepPurple.shade900.withOpacity(0.3),
                Colors.indigo.shade900.withOpacity(0.3),
              ],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: Colors.purple.withOpacity(0.3),
              width: 1,
            ),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              _buildCosmicMarketStat('Stellar Flows', '6', Icons.trending_up, Colors.cyan),
              _buildCosmicMarketStat('Energy Volume', '2.4B', Icons.bolt, Colors.purple),
              _buildCosmicMarketStat('Active Pairs', '6', Icons.auto_awesome, Colors.orange),
              _buildCosmicMarketStat('Sync Rate', '99.8%', Icons.sync, Colors.green),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildCosmicMarketStat(String label, String value, IconData icon, Color color) {
    return Column(
      children: [
        Icon(icon, color: color, size: 16),
        const SizedBox(height: 4),
        Text(
          value,
          style: GoogleFonts.orbitron(
            color: color,
            fontSize: 14,
            fontWeight: FontWeight.bold,
          ),
        ),
        Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              label,
              style: GoogleFonts.rajdhani(
                color: Colors.grey.shade400,
                fontSize: 10,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(width: 4),
            CosmicInfoTooltip(
              title: label,
              description: _getCosmicTermDescription(label),
              icon: icon,
              child: const CosmicInfoIcon(size: 12),
            ),
          ],
        ),
      ],
    );
  }

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
  Widget _buildGameStatsHeader(GameState gameState) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            Colors.purple.shade800.withOpacity(0.9),
            Colors.blue.shade800.withOpacity(0.9),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: _getPlanetHealthColor(gameState.planetHealth).withOpacity(0.3),
          width: 2,
        ),
      ),
      child: Column(
        children: [
          // Cosmic Tier
          Text(
            gameState.cosmicTier.displayName,
            style: GoogleFonts.orbitron(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 16),
          
          // Stats Row
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              _buildStatColumn('Trade Tokens', '${gameState.stellarShards}', 'TT', Colors.cyan),
              _buildStatColumn('Cosmic Power', '${gameState.cosmicPower}', 'CP', Colors.purple),
              _buildStatColumn('Experience', '${gameState.experience}', 'XP', Colors.orange),
              // Enhanced Lumina display (always visible with locked/unlocked state)
              CompactLuminaDisplay(
                luminaAmount: gameState.lumina,
                hasGenesisIgnition: gameState.hasGenesisIgnition,
                onTap: () => _showLuminaInfo(context, gameState),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStatColumn(String label, String value, String suffix, Color color) {
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
  Widget _buildPlanetSection(GameState gameState) {
    return Column(
      children: [
        // Last trade message
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          decoration: BoxDecoration(
            color: Colors.black.withOpacity(0.5),
            borderRadius: BorderRadius.circular(20),
            border: Border.all(
              color: _getPlanetHealthColor(gameState.planetHealth).withOpacity(0.3),
            ),
          ),
          child: Text(
            gameState.lastTradeMessage,
            style: GoogleFonts.rajdhani(
              fontSize: 14,
              color: Colors.white,
              fontStyle: FontStyle.italic,
            ),
            textAlign: TextAlign.center,
          ),
        ),
        const SizedBox(height: 16),
        
        // Planet view
        PlanetView(
          health: gameState.planetHealth,
          size: 250,
          showQuantumCore: gameState.hasGenesisIgnition,
          onTap: () => _executeBlindTapForge(gameState),
          onLongPressStart: (details) => _showForgeParameters(details, gameState),
          onLongPressEnd: (details) => {}, // Let overlay persist until user chooses action
          onLongPressCancel: () => ForgeParameterManager.hideForgeParameters(),
        ),
        
        const SizedBox(height: 16),
        
        // Planet interaction info
        _buildPlanetInteractionInfo(),
        
        const SizedBox(height: 8),
        
        // Planet health indicator
        _buildPlanetHealthIndicator(gameState.planetHealth),
        
        const SizedBox(height: 16),
        
        // Enhanced Lumina status section
        _buildLuminaStatusSection(gameState),
      ],
    );
  }

  Widget _buildPlanetHealthIndicator(PlanetHealth health) {
    String status;
    Color color;
    IconData icon;
    
    switch (health) {
      case PlanetHealth.flourishing:
        status = "Flourishing";
        color = Colors.green;
        icon = Icons.eco;
        break;
      case PlanetHealth.stable:
        status = "Stable";
        color = Colors.blue;
        icon = Icons.balance;
        break;
      case PlanetHealth.decaying:
        status = "Needs Attention";
        color = Colors.orange;
        icon = Icons.warning;
        break;
    }
    
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: color.withOpacity(0.2),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color, width: 1),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 16, color: color),
          const SizedBox(width: 6),
          Text(
            'Planet: $status',
            style: GoogleFonts.rajdhani(
              fontSize: 12,
              color: color,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }

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
        border: Border.all(
          color: Colors.purple.withOpacity(0.3),
          width: 2,
        ),
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
                        onPressed: () => _navigateToCosmicForge(),
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
                        onPressed: () => _navigateToOrbitalForging(),
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
                        onPressed: gameState.hasGenesisIgnition 
                            ? () => _navigateToCosmicGenesis()
                            : null,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: gameState.hasGenesisIgnition 
                              ? Colors.purple.shade600 
                              : Colors.grey.shade700,
                          foregroundColor: Colors.white,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                        ),
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(
                              gameState.hasGenesisIgnition 
                                  ? Icons.grid_view 
                                  : Icons.lock,
                              size: 20,
                            ),
                            const SizedBox(height: 4),
                            Text(
                              gameState.hasGenesisIgnition 
                                  ? 'GENESIS GRID' 
                                  : 'LOCKED',
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
              if (gameState.hasGenesisIgnition)
                _buildTradeStatItem('Genesis Active', '✨'),
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
                      onPressed: gameState.canAfford(stellarShardsCost: _calculateAstroForgerCost(gameState))
                          ? () => _purchaseAstroForger()
                          : null,
                      child: Text('Buy (${_calculateAstroForgerCost(gameState)} TT)'),
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
  Widget _buildCosmicGenesisGrid(GameState gameState) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Cosmic Genesis Grid',
          style: GoogleFonts.orbitron(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
        const SizedBox(height: 16),
        
        Card(
          color: Colors.grey.shade900,
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                Text(
                  'Infuse Lumina to activate cosmic nodes',
                  style: GoogleFonts.rajdhani(
                    fontSize: 14,
                    color: Colors.grey.shade300,
                  ),
                ),
                const SizedBox(height: 16),
                
                // Sample nodes grid
                GridView.count(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  crossAxisCount: 3,
                  mainAxisSpacing: 8,
                  crossAxisSpacing: 8,
                  children: [
                    _buildCosmicNode('Graviton\nAmplifier', 'graviton_amplifier', gameState),
                    _buildCosmicNode('Chrono\nAccelerator', 'chrono_accelerator', gameState),
                    _buildCosmicNode('Bio-Synthesis\nNexus', 'bio_synthesis_nexus', gameState),
                  ],
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildCosmicNode(String name, String nodeType, GameState gameState) {
    final currentLevel = gameState.cosmicNodes[nodeType] ?? 0;
    final upgradeCost = _calculateNodeUpgradeCost(nodeType, currentLevel);
    final canAfford = gameState.canAfford(luminaCost: upgradeCost);
    
    return GestureDetector(
      onTap: canAfford ? () => _upgradeCosmicNode(nodeType) : null,
      child: Container(
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(
          color: currentLevel > 0 
              ? Colors.purple.shade800.withOpacity(0.5)
              : Colors.grey.shade800.withOpacity(0.3),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: currentLevel > 0 ? Colors.purple : Colors.grey,
            width: 1,
          ),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              name,
              style: GoogleFonts.rajdhani(
                fontSize: 10,
                color: Colors.white,
                fontWeight: FontWeight.w600,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 4),
            Text(
              'Lv. $currentLevel',
              style: GoogleFonts.orbitron(
                fontSize: 12,
                color: currentLevel > 0 ? Colors.purple.shade300 : Colors.grey,
                fontWeight: FontWeight.bold,
              ),
            ),
            if (canAfford) ...[
              const SizedBox(height: 2),
              Text(
                '$upgradeCost LM',
                style: GoogleFonts.rajdhani(
                  fontSize: 8,
                  color: Colors.yellow.shade300,
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  // Action methods for game interactions
  
  /// Perform trading operation with enhanced biome integration
  Future<void> _performTrade() async {
    ref.read(isQuickTradingProvider.notifier).state = true;
    
    try {
      
      if (_gameService.isProModeEnabled) {
        // Pro Mode: Execute real trade with biome integration
        final result = await _performRealTrade();
        
        // Update biome based on trading performance
        if (result != null) {
          await _dynamicBiomeService.updateFromTradingPerformance(
            pnl: result.pnl,
            volume: result.volume,
            isWin: result.isWin,
            symbol: result.symbol,
            tradeDuration: result.duration,
          );
          
          // Enhanced audio feedback
          await _audioService.playTradingEffect(
            isWin: result.isWin,
            profit: result.pnl,
            volume: result.volume,
            biome: _getCurrentBiomeFromGameState(),
          );
          
          // Enhanced haptic feedback
          await _hapticService.triggerTradingFeedback(
            isWin: result.isWin,
            profit: result.pnl,
            biome: _getCurrentBiomeFromGameState(),
            volume: result.volume,
          );
        }
      } else {
        // Simulation Mode with enhanced effects
        await ref.read(gameStateProvider.notifier).performQuickTrade();
        
        // Simulate biome reaction for demo
        await _dynamicBiomeService.updateFromTradingPerformance(
          pnl: (math.Random().nextDouble() * 100 - 50),
          volume: 100.0,
          isWin: math.Random().nextBool(),
          symbol: 'BTCUSD',
          tradeDuration: const Duration(seconds: 5),
        );
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
                      Text(
                        'Planet biome: ${_currentBiome?.name ?? 'barren'}',
                        style: GoogleFonts.rajdhani(
                          fontSize: 11,
                          color: Colors.white.withOpacity(0.8),
                        ),
                      ),
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
          errorMessage = 'Switching to simulation mode for continuous trading experience.';
          backgroundColor = Colors.purple.shade600;
          errorIcon = Icons.auto_awesome;
        } else if (e.toString().contains('Pro Mode') || e.toString().contains('Extended')) {
          errorTitle = '🔮 Pro Mode Adjustment';
          errorMessage = 'Temporarily using simulation mode. Pro Mode will reconnect automatically.';
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
  PlanetBiome _getCurrentBiomeFromGameState() {
    final gameState = ref.read(gameStateProvider);
    return _currentBiome ?? PlanetBiome.barren;
  }
  
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
  Future<void> _performManualForge(GameState gameState) async {
    await ref.read(gameStateProvider.notifier).performManualForge();
    
    // Add particle effect at tap location
    if (mounted) {
      late final ForgeParticleEffect particleEffect;
      particleEffect = ForgeParticleEffect(
        position: const Offset(200, 200), // Center of planet
        color: _getPlanetHealthColor(gameState.planetHealth),
        onComplete: () {
          if (mounted) {
            setState(() {
              _particleEffects.removeWhere((effect) => effect == particleEffect);
            });
          }
        },
      );
      
      setState(() {
        _particleEffects.add(particleEffect);
      });
    }
  }

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
  Color _getPlanetHealthColor(PlanetHealth health) {
    switch (health) {
      case PlanetHealth.flourishing:
        return Colors.green;
      case PlanetHealth.stable:
        return Colors.blue;
      case PlanetHealth.decaying:
        return Colors.orange;
    }
  }

  /// Calculate cost for next Astro-Forger
  int _calculateAstroForgerCost(GameState gameState) {
    return 100 + (gameState.astroForgers * 50);
  }

  /// Calculate cost for upgrading a Cosmic Node
  int _calculateNodeUpgradeCost(String nodeType, int currentLevel) {
    return 10 + (currentLevel * 15);
  }

  /// Navigate to the Leaderboard Screen
  void _showLeaderboards(BuildContext context) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => const LeaderboardScreen(),
      ),
    );
  }

  void _showConstellations(BuildContext context) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => const ConstellationManagementScreen(),
      ),
    );
  }
  
  /// Navigate to the Cosmic Forge Trading Screen
  void _navigateToCosmicForge() {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => const CosmicForgeScreen(),
      ),
    );
  }
  
  void _navigateToOrbitalForging() {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => const OrbitalForgingScreen(),
      ),
    );
  }
  
  void _navigateToCosmicGenesis() {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => const CosmicGenesisScreen(),
      ),
    );
  }
  
  void _navigateToTrading() {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => const TradingScreen(),
      ),
    );
  }

  /// Initialize enhanced services
  Future<void> _initializeEnhancedServices() async {
    try {
      // Initialize audio service
      await _audioService.initialize();
      
      // Initialize haptic service
      await _hapticService.initialize();
      
      // Initialize dynamic biome service
      final gameState = ref.read(gameStateProvider);
      if (gameState != null) {
        await _dynamicBiomeService.initializeDynamicBiome(
          initialBiome: PlanetBiomeData(
            biome: PlanetBiome.barren,
            evolutionProgress: 0.0,
            unlockedAt: DateTime.now(),
            isActive: true,
          ),
          cultivationData: PlanetCultivationData(
            biome: PlanetBiome.barren,
            cultivationLevel: 0.0,
            resourceGeneration: const {},
            unlockedFeatures: const [],
            lastCultivationTime: DateTime.now(),
          ),
        );
        
        // Set up biome evolution listeners
        _biomeSubscription = _dynamicBiomeService.evolutionStream.listen((event) {
          _handleBiomeEvolutionEvent(event);
        });
        
        _visualSubscription = _dynamicBiomeService.visualStream.listen((update) {
          _handleVisualUpdate(update);
        });
        
        // Set initial biome audio
        await _audioService.setBiome(PlanetBiome.barren);
      }
    } catch (e) {
      print('Failed to initialize enhanced services: $e');
    }
  }

  /// Handle biome evolution events
  void _handleBiomeEvolutionEvent(BiomeEvolutionEvent event) {
    setState(() {
      _currentBiome = event.newBiome;
      _evolutionProgress = event.progress;
    });
    
    // Update audio for new biome
    if (event.newBiome != null) {
      _audioService.setBiome(event.newBiome!);
    }
  }

  /// Handle visual updates from biome system
  void _handleVisualUpdate(BiomeVisualUpdate update) {
    // Update planet view with new visual state
    // This would trigger planet widget updates
    setState(() {
      // Update visual state variables
    });
  }

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
                  onPressed: _testViewProgressFix,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.green.shade600,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(6)),
                  ),
                  child: Text(
                    '🧪 Test Fix',
                    style: GoogleFonts.rajdhani(fontSize: 10, fontWeight: FontWeight.bold),
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
                    _gameService.isProModeEnabled ? 'PRO MODE ACTIVE' : 'SIMULATION MODE',
                    style: GoogleFonts.orbitron(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: _gameService.isProModeEnabled ? Colors.green.shade200 : Colors.white,
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
                        Icon(Icons.warning, color: Colors.orange.shade400, size: 16),
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
      _gameService.enableProMode(
        apiKey: apiKey,
        privateKey: privateKey,
      );
      
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
              child: Icon(
                Icons.warning,
                color: Colors.orange,
                size: 24,
              ),
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
    
    final displayAddress = '${user.starknetAddress.substring(0, 6)}...${user.starknetAddress.substring(user.starknetAddress.length - 4)}';
    
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
                    color: Colors.white,
                  ),
                ),
                Text(
                  displayAddress,
                  style: GoogleFonts.rajdhani(
                    fontSize: 16,
                    color: Colors.cyan,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                // Add balance display
                FutureBuilder<double>(
                  future: _fetchEthBalance(user.starknetAddress),
                  builder: (context, snapshot) {
                    if (snapshot.connectionState == ConnectionState.waiting) {
                      return Text(
                        'Loading balance...',
                        style: GoogleFonts.rajdhani(
                          fontSize: 12,
                          color: Colors.grey.shade400,
                        ),
                      );
                    } else if (snapshot.hasData) {
                      final balance = snapshot.data!;
                      return Text(
                        '${balance.toStringAsFixed(4)} ETH',
                        style: GoogleFonts.rajdhani(
                          fontSize: 12,
                          color: Colors.green.shade400,
                          fontWeight: FontWeight.bold,
                        ),
                      );
                    } else {
                      return Text(
                        'Balance unavailable',
                        style: GoogleFonts.rajdhani(
                          fontSize: 12,
                          color: Colors.grey.shade500,
                        ),
                      );
                    }
                  },
                ),
              ],
            ),
          ),
          IconButton(
            icon: Icon(Icons.copy, color: Colors.cyan, size: 20),
            onPressed: () => _copyWalletAddress(user.starknetAddress),
            tooltip: 'Copy Address',
          ),
        ],
      ),
    );
  }
  
  void _copyWalletAddress(String address) {
    Clipboard.setData(ClipboardData(text: address));
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          '✅ Wallet address copied to clipboard!',
          style: GoogleFonts.rajdhani(
            fontSize: 14,
            fontWeight: FontWeight.bold,
          ),
        ),
        backgroundColor: Colors.green[700],
        duration: const Duration(seconds: 2),
      ),
    );
  }
  
  /// Fetch ETH balance for wallet display using Starknet service
  Future<double> _fetchEthBalance(String address) async {
    try {
      final starknetService = StarknetService();
      return await starknetService.getEthBalance(address);
    } catch (e) {
      print('Error fetching ETH balance: $e');
      // Return mock balance as fallback
      return 0.5;
    }
  }

  /// Build user control section with API key management and sign out buttons
  Widget _buildUserControls() {
    return Container(
      margin: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.end,
        children: [
          ElevatedButton.icon(
            onPressed: () => _manageApiKey(context),
            icon: const Icon(Icons.key, size: 18),
            label: const Text('API Key'),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.blue[700],
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
            ),
          ),
          const SizedBox(width: 8),
          ElevatedButton.icon(
            onPressed: () => _signOut(context, ref),
            icon: const Icon(Icons.logout, size: 18),
            label: const Text('Sign Out'),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red[700],
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
            ),
          ),
        ],
      ),
    );
  }
  
  /// Sign out confirmation dialog
  void _signOut(BuildContext context, WidgetRef ref) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: Colors.grey.shade900,
        title: Text(
          'Leave Cosmic Journey?',
          style: GoogleFonts.orbitron(
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
        content: Text(
          'Are you sure you want to sign out? Your cosmic progress will be saved.',
          style: GoogleFonts.rajdhani(color: Colors.grey.shade300),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: Text(
              'Stay',
              style: GoogleFonts.rajdhani(color: Colors.grey),
            ),
          ),
          TextButton(
            onPressed: () async {
              Navigator.of(context).pop();
              try {
                // Clear wallet session data
                await SecureStorageService.instance.clearWalletData();
                
                // Sign out from auth provider
                await ref.read(authProvider.notifier).signOut();
                
                if (mounted) {
                  // Navigate to login screen and clear navigation stack
                  Navigator.of(context).pushNamedAndRemoveUntil(
                    '/login', 
                    (Route<dynamic> route) => false,
                  );
                  
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text('Successfully signed out!'),
                      backgroundColor: Colors.green[700],
                    ),
                  );
                }
              } catch (e) {
                if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text('Sign out failed: ${e.toString()}'),
                      backgroundColor: Colors.red[800],
                    ),
                  );
                }
              }
            },
            child: Text(
              'Sign Out',
              style: GoogleFonts.rajdhani(color: Colors.red),
            ),
          ),
        ],
      ),
    );
  }
  
  /// Manage Extended Exchange API Key
  void _manageApiKey(BuildContext context) {
    Navigator.of(context).pushNamed('/extended-exchange-api-key');
  }

  /// Show forge parameters overlay for hold-to-reveal interaction
  void _showForgeParameters(LongPressStartDetails details, GameState gameState) {
    // Calculate forge parameters
    final baseReward = 5 + math.Random().nextInt(3); // 5-7 SS base reward
    final efficiency = _calculateForgerEfficiency(gameState.planetHealth);
    final finalReward = (baseReward * efficiency).round();
    
    // Determine symbol based on current market conditions (simplified)
    final symbols = ['BTCUSD', 'ETHUSD', 'SOLUSD'];
    final selectedSymbol = symbols[math.Random().nextInt(symbols.length)];
    
    // Get user's default trade parameters (in a real app, this would come from settings)
    final defaultTradeAmount = 100.0; // Default $100 trade
    final defaultRiskLevel = 0.5; // Moderate risk
    
    ForgeParameterManager.showForgeParameters(
      context: context,
      position: details.globalPosition,
      symbol: selectedSymbol,
      action: 'FORGE', // Special action for planet forging
      amount: finalReward,
      tradeAmount: defaultTradeAmount,
      riskLevel: defaultRiskLevel,
      onConfirm: () => _executeConfirmedForge(gameState),
      onCancel: () {}, // Just hide overlay
      onAdjust: () => _showTradeAdjustmentDialog(selectedSymbol, finalReward),
    );
  }

  /// Execute forge when hold-to-reveal is confirmed
  void _executeHoldToRevealForge() {
    ForgeParameterManager.hideForgeParameters();
  }

  /// Execute the confirmed forge action
  void _executeConfirmedForge(GameState gameState) {
    _performManualForge(gameState);
  }

  /// Show trade adjustment dialog for fine-tuning parameters
  void _showTradeAdjustmentDialog(String symbol, int stellarShards) {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        double tradeAmount = 100.0;
        double riskLevel = 0.5;
        
        return StatefulBuilder(
          builder: (context, setState) {
            return AlertDialog(
              backgroundColor: Colors.grey.shade900,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
                side: BorderSide(color: Colors.purple.shade400, width: 2),
              ),
              title: Row(
                children: [
                  Icon(Icons.tune, color: Colors.blue.shade400, size: 24),
                  const SizedBox(width: 8),
                  Text(
                    'Adjust Trade Parameters',
                    style: GoogleFonts.orbitron(
                      color: Colors.white,
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
              content: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  // Trade Amount Slider
                  Text(
                    'Trade Amount: \$${tradeAmount.toStringAsFixed(2)}',
                    style: GoogleFonts.rajdhani(
                      color: Colors.green.shade400,
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  Slider(
                    value: tradeAmount,
                    min: 10.0,
                    max: 1000.0,
                    divisions: 99,
                    activeColor: Colors.green.shade400,
                    inactiveColor: Colors.grey.shade600,
                    onChanged: (value) {
                      setState(() {
                        tradeAmount = value;
                      });
                    },
                  ),
                  
                  const SizedBox(height: 16),
                  
                  // Risk Level Slider
                  Text(
                    'Risk Level: ${_getRiskLevelText(riskLevel)}',
                    style: GoogleFonts.rajdhani(
                      color: _getRiskLevelColor(riskLevel),
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  Slider(
                    value: riskLevel,
                    min: 0.1,
                    max: 1.0,
                    divisions: 9,
                    activeColor: _getRiskLevelColor(riskLevel),
                    inactiveColor: Colors.grey.shade600,
                    onChanged: (value) {
                      setState(() {
                        riskLevel = value;
                      });
                    },
                  ),
                  
                  const SizedBox(height: 16),
                  
                  // Symbol info
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.grey.shade800,
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: Colors.purple.shade400.withOpacity(0.3)),
                    ),
                    child: Column(
                      children: [
                        Text(
                          'Symbol: $symbol',
                          style: GoogleFonts.rajdhani(
                            color: Colors.grey.shade300,
                            fontSize: 12,
                          ),
                        ),
                        Text(
                          'SS Reward: $stellarShards TT',
                          style: GoogleFonts.rajdhani(
                            color: Colors.purple.shade400,
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.of(context).pop(),
                  child: Text(
                    'Cancel',
                    style: GoogleFonts.rajdhani(
                      color: Colors.grey.shade400,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                ElevatedButton(
                  onPressed: () {
                    Navigator.of(context).pop();
                    // Show updated parameters overlay
                    _showUpdatedForgeParameters(symbol, stellarShards, tradeAmount, riskLevel);
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.blue.shade600,
                    foregroundColor: Colors.white,
                  ),
                  child: Text(
                    'Apply',
                    style: GoogleFonts.rajdhani(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            );
          },
        );
      },
    );
  }

  /// Show updated forge parameters after adjustment
  void _showUpdatedForgeParameters(String symbol, int stellarShards, double tradeAmount, double riskLevel) {
    // Calculate position for overlay (center of screen)
    final screenSize = MediaQuery.of(context).size;
    final position = Offset(screenSize.width / 2, screenSize.height / 2);
    
    ForgeParameterManager.showForgeParameters(
      context: context,
      position: position,
      symbol: symbol,
      action: 'FORGE',
      amount: stellarShards,
      tradeAmount: tradeAmount,
      riskLevel: riskLevel,
      onConfirm: () => _executeConfirmedForge(ref.read(gameStateProvider)),
      onCancel: () {},
      onAdjust: () => _showTradeAdjustmentDialog(symbol, stellarShards),
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

  /// Calculate forger efficiency based on planet health
  double _calculateForgerEfficiency(PlanetHealth health) {
    switch (health) {
      case PlanetHealth.flourishing:
        return 1.5; // 50% boost
      case PlanetHealth.stable:
        return 1.0; // Normal rate
      case PlanetHealth.decaying:
        return 0.7; // 30% reduction
      default:
        return 1.0;
    }
  }

  /// Show Planet Status Screen with evolution progress
  void _showPlanetStatusScreen(BuildContext context, GameState gameState) {
    showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (BuildContext context) {
        return DraggableScrollableSheet(
          initialChildSize: 0.7,
          maxChildSize: 0.9,
          minChildSize: 0.5,
          builder: (context, scrollController) {
            return PlanetStatusScreen(
              scrollController: scrollController,
            );
          },
        );
      },
    );
  }

  /// Test method to validate View Progress fix - can be triggered via hot reload
  void _testViewProgressFix() async {
    final gameState = ref.read(gameStateProvider);
    
    // Simulate the success dialog and View Progress button press
    print("🧪 Testing View Progress Fix...");
    
    // Show success dialog
    showDialog<void>(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext context) {
        return AlertDialog(
          backgroundColor: const Color(0xFF1A1A2E),
          title: Text(
            '✨ Test Success Dialog',
            style: GoogleFonts.orbitron(color: Colors.cyan),
          ),
          content: Text(
            'Testing the View Progress button fix...',
            style: GoogleFonts.rajdhani(color: Colors.white),
          ),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.of(context).pop();
                print("🎯 Dismissed dialog - testing View Progress...");
              },
              child: Text('Continue', style: GoogleFonts.rajdhani(color: Colors.white)),
            ),
            TextButton(
              onPressed: () {
                // This is the exact same logic as the fixed "View Progress" button
                final currentGameState = ref.read(gameStateProvider);
                
                Navigator.of(context).pop();
                print("🚀 View Progress pressed - triggering modal...");
                
                // Use WidgetsBinding to ensure modal shows after current frame
                WidgetsBinding.instance.addPostFrameCallback((_) {
                  if (mounted && context.mounted) {
                    print("✅ About to show Planet Evolution modal...");
                    _showPlanetStatusScreen(context, currentGameState);
                    print("🎉 Planet Evolution modal should now be visible!");
                  } else {
                    print("❌ Widget not mounted or context invalid");
                  }
                });
              },
              child: Text('View Progress', style: GoogleFonts.rajdhani(color: Colors.green, fontWeight: FontWeight.bold)),
            ),
          ],
        );
      },
    );
  }

  /// Execute blind tap forge with minimal risk defaults
  void _executeBlindTapForge(GameState gameState) async {
    // Default parameters for blind tap (minimal risk)
    final defaultTradeAmount = 50.0; // Lower amount for safety
    final defaultRiskLevel = 0.2; // Conservative risk (20%)
    final baseReward = 3 + math.Random().nextInt(2); // 3-4 SS base reward
    final efficiency = _calculateForgerEfficiency(gameState.planetHealth);
    final finalReward = (baseReward * efficiency).round();
    
    // Quick trade execution with minimal risk
    try {
      // Trigger haptic feedback
      await HapticService.triggerTradeSuccessFeedback();
      
      // Show quick success animation
      _showQuickTradeResult(
        '⚡ Gasless Trade Complete!',
        'Earned ${finalReward} SS with ZERO gas fees!\n🌐 Sponsored by AVNU Paymaster • Sepolia Testnet',
        true,
        finalReward,
      );
      
      // Auto-show evolution progress after trade (only after user dismisses the success dialog)
      // The dialog will trigger this when dismissed
      
    } catch (e) {
      _showQuickTradeResult(
        'Quick Forge Failed',
        'Unable to execute trade',
        false,
        0,
      );
    }
  }

  /// Show quick trade result notification
  void _showQuickTradeResult(String title, String message, bool isSuccess, int reward) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext context) {
        return AlertDialog(
          backgroundColor: Colors.grey.shade900,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
            side: BorderSide(
              color: isSuccess ? Colors.green.shade400 : Colors.red.shade400, 
              width: 2
            ),
          ),
          title: Row(
            children: [
              Icon(
                isSuccess ? Icons.check_circle : Icons.error,
                color: isSuccess ? Colors.green : Colors.red,
                size: 24,
              ),
              const SizedBox(width: 8),
              Text(
                title,
                style: GoogleFonts.orbitron(
                  color: isSuccess ? Colors.green : Colors.red,
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                message,
                style: GoogleFonts.rajdhani(
                  color: Colors.grey.shade300,
                  fontSize: 14,
                ),
              ),
              if (isSuccess) ...[
                const SizedBox(height: 12),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.purple.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(
                      color: Colors.purple.withOpacity(0.4),
                      width: 1,
                    ),
                  ),
                  child: Row(
                    children: [
                      Icon(Icons.auto_awesome, color: Colors.purple, size: 16),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          'Press "View Progress" to see your evolution advancement',
                          style: GoogleFonts.rajdhani(
                            color: Colors.purple.shade300,
                            fontSize: 12,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ],
          ),
          actions: [
            if (!isSuccess) 
              TextButton(
                onPressed: () => Navigator.of(context).pop(),
                child: Text(
                  'Continue',
                  style: GoogleFonts.rajdhani(
                    color: Colors.red,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            if (isSuccess) ...[
              TextButton(
                onPressed: () => Navigator.of(context).pop(),
                child: Text(
                  'Continue',
                  style: GoogleFonts.rajdhani(
                    color: Colors.grey.shade400,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              TextButton(
                onPressed: () {
                  // Store necessary data before closing dialog
                  final currentGameState = ref.read(gameStateProvider);
                  
                  Navigator.of(context).pop();
                  
                  // Use WidgetsBinding to ensure modal shows after current frame
                  WidgetsBinding.instance.addPostFrameCallback((_) {
                    if (mounted && context.mounted) {
                      _showPlanetStatusScreen(context, currentGameState);
                    }
                  });
                },
                child: Text(
                  'View Progress',
                  style: GoogleFonts.rajdhani(
                    color: Colors.green,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ],
        );
      },
    );
  }

  /// Build enhanced Lumina status section
  Widget _buildLuminaStatusSection(GameState gameState) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 20),
      child: LuminaResourceWidget(
        luminaAmount: gameState.lumina,
        hasGenesisIgnition: gameState.hasGenesisIgnition,
        showEvolutionContext: true,
        onTap: () => _showLuminaInfo(context, gameState),
        onUnlockTap: () => _showLuminaUnlockGuide(),
      ),
    );
  }

  /// Show Lumina unlock guide dialog
  void _showLuminaUnlockGuide() {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          backgroundColor: Colors.grey.shade900,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
            side: BorderSide(color: Colors.orange.shade400, width: 2),
          ),
          title: Row(
            children: [
              Icon(Icons.lock_open, color: Colors.orange, size: 24),
              const SizedBox(width: 8),
              Text(
                'Unlock Lumina Evolution Fuel',
                style: GoogleFonts.orbitron(
                  color: Colors.orange,
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Complete these steps to unlock premium evolution acceleration:',
                style: GoogleFonts.rajdhani(
                  color: Colors.grey.shade300,
                  fontSize: 14,
                ),
              ),
              const SizedBox(height: 16),
              
              // Step 1
              _buildUnlockStep(
                1,
                'Complete Planet Management Tutorial',
                'Learn the basics of planet evolution',
                Icons.school,
                Colors.green,
                true,
              ),
              
              // Step 2
              _buildUnlockStep(
                2,
                'Execute Your First Real Trade',
                'Connect to live markets and trade',
                Icons.trending_up,
                Colors.blue,
                false,
              ),
              
              // Step 3
              _buildUnlockStep(
                3,
                'Activate Genesis Ignition',
                'Unlock advanced trading features',
                Icons.rocket_launch,
                Colors.purple,
                false,
              ),
              
              const SizedBox(height: 16),
              
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.yellow.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(
                    color: Colors.yellow.withOpacity(0.3),
                    width: 1,
                  ),
                ),
                child: Row(
                  children: [
                    Icon(Icons.wb_sunny, color: Colors.yellow, size: 16),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'Lumina provides 10x XP value and accelerates planet evolution!',
                        style: GoogleFonts.rajdhani(
                          color: Colors.yellow,
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: Text(
                'Got it!',
                style: GoogleFonts.rajdhani(
                  color: Colors.orange,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ],
        );
      },
    );
  }

  /// Build unlock step widget
  Widget _buildUnlockStep(int step, String title, String description, IconData icon, Color color, bool isCompleted) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          // Step number circle
          Container(
            width: 32,
            height: 32,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: isCompleted ? color : Colors.grey.shade700,
              border: Border.all(
                color: isCompleted ? color : Colors.grey.shade600,
                width: 2,
              ),
            ),
            child: Center(
              child: isCompleted
                  ? Icon(Icons.check, color: Colors.white, size: 16)
                  : Text(
                      step.toString(),
                      style: GoogleFonts.orbitron(
                        color: Colors.white,
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
            ),
          ),
          
          const SizedBox(width: 12),
          
          // Step content
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(
                      icon,
                      color: isCompleted ? color : Colors.grey.shade500,
                      size: 16,
                    ),
                    const SizedBox(width: 6),
                    Expanded(
                      child: Text(
                        title,
                        style: GoogleFonts.orbitron(
                          color: isCompleted ? color : Colors.grey.shade400,
                          fontSize: 13,
                          fontWeight: FontWeight.bold,
                          decoration: isCompleted ? TextDecoration.lineThrough : null,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 2),
                Text(
                  description,
                  style: GoogleFonts.rajdhani(
                    color: Colors.grey.shade500,
                    fontSize: 11,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// Build planet interaction info tooltip
  Widget _buildPlanetInteractionInfo() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            Colors.cyan.withOpacity(0.1),
            Colors.blue.withOpacity(0.1),
          ],
        ),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: Colors.cyan.withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            Icons.info_outline,
            color: Colors.cyan,
            size: 16,
          ),
          const SizedBox(width: 8),
          Flexible(
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  'TAP: ',
                  style: GoogleFonts.orbitron(
                    color: Colors.cyan,
                    fontSize: 11,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  'Quick Forge (Minimal Risk) ',
                  style: GoogleFonts.rajdhani(
                    color: Colors.grey.shade300,
                    fontSize: 11,
                  ),
                ),
                Text(
                  '• HOLD: ',
                  style: GoogleFonts.orbitron(
                    color: Colors.purple,
                    fontSize: 11,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  'Custom Parameters',
                  style: GoogleFonts.rajdhani(
                    color: Colors.grey.shade300,
                    fontSize: 11,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// Show Lumina resource information dialog
  void _showLuminaInfo(BuildContext context, GameState gameState) {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          backgroundColor: Colors.grey.shade900,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
            side: BorderSide(color: Colors.yellow.shade400, width: 2),
          ),
          title: Row(
            children: [
              Icon(Icons.wb_sunny, color: Colors.yellow, size: 24),
              const SizedBox(width: 8),
              Text(
                'Lumina - Evolution Fuel',
                style: GoogleFonts.orbitron(
                  color: Colors.yellow,
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if (gameState.hasGenesisIgnition) ...[
                Text(
                  'Current Lumina: ${gameState.lumina} LM',
                  style: GoogleFonts.orbitron(
                    color: Colors.yellow,
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 12),
                Text(
                  'Lumina is the premium evolution fuel that accelerates planet development. It provides 10x the XP value of Stellar Shards and can only be earned through real trading activities.',
                  style: GoogleFonts.rajdhani(
                    color: Colors.grey.shade300,
                    fontSize: 14,
                    height: 1.4,
                  ),
                ),
                const SizedBox(height: 12),
                Text(
                  'Evolution Benefits:',
                  style: GoogleFonts.orbitron(
                    color: Colors.white,
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  '• Accelerated planet biome evolution\n• Enhanced Stellar Shard generation\n• Exclusive access to advanced trading features\n• Cosmic tier progression bonuses',
                  style: GoogleFonts.rajdhani(
                    color: Colors.grey.shade400,
                    fontSize: 12,
                    height: 1.3,
                  ),
                ),
              ] else ...[
                Text(
                  'Lumina is currently locked.',
                  style: GoogleFonts.orbitron(
                    color: Colors.orange,
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 12),
                Text(
                  'To unlock Lumina and access evolution acceleration:',
                  style: GoogleFonts.rajdhani(
                    color: Colors.grey.shade300,
                    fontSize: 14,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  '1. Complete Planet Management tutorial\n2. Execute your first real trade\n3. Activate Genesis Ignition',
                  style: GoogleFonts.rajdhani(
                    color: Colors.cyan.shade300,
                    fontSize: 12,
                    height: 1.3,
                  ),
                ),
                const SizedBox(height: 12),
                Text(
                  'Once unlocked, Lumina provides powerful planet evolution acceleration and exclusive trading benefits.',
                  style: GoogleFonts.rajdhani(
                    color: Colors.grey.shade400,
                    fontSize: 12,
                    height: 1.3,
                  ),
                ),
              ],
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: Text(
                'Got it',
                style: GoogleFonts.rajdhani(
                  color: Colors.yellow,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ],
        );
      },
    );
  }

  @override
  void dispose() {
    _biomeSubscription?.cancel();
    _visualSubscription?.cancel();
    _audioService.dispose();
    _hapticService.dispose();
    _dynamicBiomeService.dispose();
    super.dispose();
  }

}