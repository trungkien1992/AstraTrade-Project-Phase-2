import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';

import 'cosmic_navigation_controller.dart';
import 'cosmic_navigation_bar.dart';
import 'cosmic_page_transitions.dart';
import '../screens/main_hub_screen.dart';
// TODO: Create missing screens
// import '../screens/cosmic_forge_screen.dart';
// import '../screens/planet_status_screen.dart';
// import '../screens/constellation_screen.dart';
// import '../services/cosmic_flow_service.dart';
import '../providers/game_state_provider.dart';

/// Main navigation shell that manages all cosmic destinations
class CosmicNavigationShell extends ConsumerStatefulWidget {
  const CosmicNavigationShell({super.key});

  @override
  ConsumerState<CosmicNavigationShell> createState() =>
      _CosmicNavigationShellState();
}

class _CosmicNavigationShellState extends ConsumerState<CosmicNavigationShell> {
  @override
  void initState() {
    super.initState();
    print('🚀 CosmicNavigationShell - initState called');
  }

  @override
  Widget build(BuildContext context) {
    print('🚀 CosmicNavigationShell - build called');
    final navigationState = ref.watch(cosmicNavigationProvider);
    final currentDestination = navigationState.currentDestination;
    print(
      '🚀 CosmicNavigationShell - Navigation state loaded: $currentDestination',
    );

    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (didPop, result) {
        if (!didPop) {
          final handled = ref
              .read(cosmicNavigationProvider.notifier)
              .handleBackNavigation();

          if (!handled) {
            // If navigation couldn't handle it, allow system back
            Navigator.of(context).pop();
          }
        }
      },
      child: Scaffold(
        backgroundColor: const Color(0xFF0A0A0F),
        body: Stack(
          children: [
            // Cosmic background gradient
            Container(
              decoration: const BoxDecoration(
                gradient: RadialGradient(
                  center: Alignment.topRight,
                  radius: 2.0,
                  colors: [Color(0xFF1A1A2E), Color(0xFF0A0A0F)],
                ),
              ),
            ),

            // Main content with nested navigation
            IndexedStack(
              index: currentDestination.index,
              children: CosmicDestination.values.map((destination) {
                return Navigator(
                  key: navigationState.navigatorKeys[destination],
                  onGenerateRoute: (settings) =>
                      _generateRoute(destination, settings),
                  onGenerateInitialRoutes: (navigator, initialRoute) {
                    return [
                      _generateRoute(
                        destination,
                        RouteSettings(name: initialRoute),
                      ),
                    ];
                  },
                );
              }).toList(),
            ),
          ],
        ),

        // Bottom navigation bar
        bottomNavigationBar: const CosmicNavigationBar(),

        // Floating action button for quick actions
        floatingActionButton: _buildFloatingActionButton(currentDestination),
        floatingActionButtonLocation: FloatingActionButtonLocation.centerDocked,
      ),
    );
  }

  /// Generate routes for each destination navigator
  Route<dynamic> _generateRoute(
    CosmicDestination destination,
    RouteSettings settings,
  ) {
    Widget page;

    switch (destination) {
      case CosmicDestination.hub:
        page = const MainHubScreen();
        break;
      case CosmicDestination.forge:
        page = const MainHubScreen(); // TODO: Replace with CosmicForgeScreen
        break;
      case CosmicDestination.planet:
        page = const MainHubScreen(); // TODO: Replace with PlanetStatusScreen
        break;
      case CosmicDestination.constellations:
        page = const MainHubScreen(); // TODO: Replace with ConstellationScreen
        break;
    }

    // Use different transitions based on destination
    switch (destination) {
      case CosmicDestination.hub:
        return CosmicPageTransitions.quantumFade(
          page: page,
          settings: settings,
        );
      case CosmicDestination.forge:
        return CosmicPageTransitions.stellarBurst(
          page: page,
          settings: settings,
          burstColor: Colors.orange,
        );
      case CosmicDestination.planet:
        return CosmicPageTransitions.orbitalRotation(
          page: page,
          settings: settings,
        );
      case CosmicDestination.constellations:
        return CosmicPageTransitions.stellarSlide(
          page: page,
          settings: settings,
          beginOffset: const Offset(0.0, 1.0),
        );
    }
  }

  /// Build floating action button based on current destination
  Widget? _buildFloatingActionButton(CosmicDestination destination) {
    switch (destination) {
      case CosmicDestination.hub:
        return CosmicFloatingNavigationButton(
          icon: Icons.flash_on,
          label: 'Quick Trade',
          onPressed: () {
            // Quick trade action
            _handleQuickAction('quick_trade');
          },
        );
      case CosmicDestination.forge:
        return CosmicFloatingNavigationButton(
          icon: Icons.auto_awesome,
          label: 'Auto Forge',
          onPressed: () {
            // Auto forge action
            _handleQuickAction('auto_forge');
          },
        );
      case CosmicDestination.planet:
        return CosmicFloatingNavigationButton(
          icon: Icons.timeline,
          label: 'Evolution',
          onPressed: () {
            // Planet evolution action
            _handleQuickAction('planet_evolution');
          },
        );
      case CosmicDestination.constellations:
        return CosmicFloatingNavigationButton(
          icon: Icons.group_add,
          label: 'Join',
          onPressed: () {
            // Join constellation action
            _handleQuickAction('join_constellation');
          },
        );
    }
  }

  /// Handle quick actions from floating button
  void _handleQuickAction(String action) {
    final currentNavigatorKey = ref
        .read(cosmicNavigationProvider.notifier)
        .getCurrentNavigatorContext();

    if (currentNavigatorKey == null) return;

    switch (action) {
      case 'quick_trade':
        // Navigate to trading screen or show quick trade dialog
        _showQuickTradeDialog();
        break;
      case 'auto_forge':
        // Navigate to auto forge or show forge dialog
        _showAutoForgeDialog();
        break;
      case 'planet_evolution':
        // Navigate to evolution screen or show evolution dialog
        _showEvolutionDialog();
        break;
      case 'join_constellation':
        // Navigate to constellation join or show join dialog
        _showJoinConstellationDialog();
        break;
    }
  }

  /// Perform quick trade operation
  Future<void> _showQuickTradeDialog() async {
    // Show loading state
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            const CircularProgressIndicator(
              valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
              strokeWidth: 2,
            ),
            const SizedBox(width: 16),
            Text(
              'Executing Quick Trade...',
              style: GoogleFonts.orbitron(
                color: Colors.white,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
        backgroundColor: const Color(0xFF7B2CBF),
        duration: const Duration(seconds: 2),
      ),
    );

    try {
      // Perform the actual trade using the game state provider
      await ref.read(gameStateProvider.notifier).performQuickTrade();

      // Show success message
      if (mounted) {
        final gameState = ref.read(gameStateProvider);
        ScaffoldMessenger.of(context).clearSnackBars();
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '🚀 Quick Trade Complete!',
                  style: GoogleFonts.orbitron(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 14,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  gameState.lastTradeMessage,
                  style: GoogleFonts.rajdhani(
                    color: Colors.white.withOpacity(0.9),
                    fontSize: 12,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Stellar Shards: ${gameState.stellarShards} | Lumina: ${gameState.lumina}',
                  style: GoogleFonts.rajdhani(
                    color: Colors.white.withOpacity(0.8),
                    fontSize: 11,
                  ),
                ),
              ],
            ),
            backgroundColor: Colors.green.shade700,
            duration: const Duration(seconds: 4),
          ),
        );
      }
    } catch (e) {
      // Show error message
      if (mounted) {
        ScaffoldMessenger.of(context).clearSnackBars();
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Row(
              children: [
                const Icon(Icons.error, color: Colors.white),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'Trade failed: ${e.toString()}',
                    style: GoogleFonts.rajdhani(color: Colors.white),
                  ),
                ),
              ],
            ),
            backgroundColor: Colors.red.shade700,
            duration: const Duration(seconds: 3),
          ),
        );
      }
    }
  }

  /// Show auto forge dialog
  void _showAutoForgeDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: const Color(0xFF1A1A2E),
        title: const Text('Auto Forge', style: TextStyle(color: Colors.white)),
        content: const Text(
          'Auto forge feature coming soon!',
          style: TextStyle(color: Colors.grey),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text(
              'Close',
              style: TextStyle(color: Color(0xFF7B2CBF)),
            ),
          ),
        ],
      ),
    );
  }

  /// Show evolution dialog
  void _showEvolutionDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: const Color(0xFF1A1A2E),
        title: const Text(
          'Planet Evolution',
          style: TextStyle(color: Colors.white),
        ),
        content: const Text(
          'Evolution acceleration feature coming soon!',
          style: TextStyle(color: Colors.grey),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text(
              'Close',
              style: TextStyle(color: Color(0xFF7B2CBF)),
            ),
          ),
        ],
      ),
    );
  }

  /// Show join constellation dialog
  void _showJoinConstellationDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: const Color(0xFF1A1A2E),
        title: const Text(
          'Join Constellation',
          style: TextStyle(color: Colors.white),
        ),
        content: const Text(
          'Constellation joining feature coming soon!',
          style: TextStyle(color: Colors.grey),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text(
              'Close',
              style: TextStyle(color: Color(0xFF7B2CBF)),
            ),
          ),
        ],
      ),
    );
  }
}
