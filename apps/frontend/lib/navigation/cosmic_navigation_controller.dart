import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Navigation destinations for the cosmic bottom navigation
enum CosmicDestination {
  hub(
    label: 'Hub',
    icon: Icons.public,
    activeIcon: Icons.public,
    tooltip: 'Main Hub - Planet & Trading Center',
  ),
  forge(
    label: 'Forge',
    icon: Icons.auto_fix_high,
    activeIcon: Icons.auto_fix_high,
    tooltip: 'Cosmic Forge - Create & Enhance',
  ),
  planet(
    label: 'Planet',
    icon: Icons.language,
    activeIcon: Icons.language,
    tooltip: 'Planet Management - Evolution & Status',
  ),
  constellations(
    label: 'Stars',
    icon: Icons.star_border,
    activeIcon: Icons.star,
    tooltip: 'Constellations - Social & Achievements',
  );

  const CosmicDestination({
    required this.label,
    required this.icon,
    required this.activeIcon,
    required this.tooltip,
  });

  final String label;
  final IconData icon;
  final IconData activeIcon;
  final String tooltip;
}

/// Navigation state for the cosmic app
class CosmicNavigationState {
  final CosmicDestination currentDestination;
  final Map<CosmicDestination, GlobalKey<NavigatorState>> navigatorKeys;
  final bool showNavigationBar;

  const CosmicNavigationState({
    required this.currentDestination,
    required this.navigatorKeys,
    this.showNavigationBar = true,
  });

  CosmicNavigationState copyWith({
    CosmicDestination? currentDestination,
    Map<CosmicDestination, GlobalKey<NavigatorState>>? navigatorKeys,
    bool? showNavigationBar,
  }) {
    return CosmicNavigationState(
      currentDestination: currentDestination ?? this.currentDestination,
      navigatorKeys: navigatorKeys ?? this.navigatorKeys,
      showNavigationBar: showNavigationBar ?? this.showNavigationBar,
    );
  }
}

/// Navigation controller for managing cosmic app navigation
class CosmicNavigationController extends StateNotifier<CosmicNavigationState> {
  CosmicNavigationController()
    : super(
        CosmicNavigationState(
          currentDestination: CosmicDestination.hub,
          navigatorKeys: {
            for (final destination in CosmicDestination.values)
              destination: GlobalKey<NavigatorState>(),
          },
        ),
      );

  /// Navigate to a specific destination
  void navigateTo(CosmicDestination destination) {
    if (state.currentDestination == destination) {
      // If already on the destination, pop to root
      final navigatorKey = state.navigatorKeys[destination];
      if (navigatorKey?.currentState?.canPop() ?? false) {
        navigatorKey!.currentState!.popUntil((route) => route.isFirst);
      }
      return;
    }

    state = state.copyWith(currentDestination: destination);
  }

  /// Get the navigator key for a destination
  GlobalKey<NavigatorState>? getNavigatorKey(CosmicDestination destination) {
    return state.navigatorKeys[destination];
  }

  /// Show or hide the bottom navigation bar
  void setNavigationBarVisibility(bool visible) {
    state = state.copyWith(showNavigationBar: visible);
  }

  /// Handle back navigation
  bool handleBackNavigation() {
    final currentKey = state.navigatorKeys[state.currentDestination];
    if (currentKey?.currentState?.canPop() ?? false) {
      currentKey!.currentState!.pop();
      return true;
    }

    // If we're not on hub and can't pop, go to hub
    if (state.currentDestination != CosmicDestination.hub) {
      navigateTo(CosmicDestination.hub);
      return true;
    }

    return false;
  }

  /// Get the current navigator context
  BuildContext? getCurrentNavigatorContext() {
    return state.navigatorKeys[state.currentDestination]?.currentContext;
  }
}

/// Provider for the cosmic navigation controller
final cosmicNavigationProvider =
    StateNotifierProvider<CosmicNavigationController, CosmicNavigationState>(
      (ref) => CosmicNavigationController(),
    );

/// Provider for the current destination
final currentDestinationProvider = Provider<CosmicDestination>((ref) {
  return ref.watch(cosmicNavigationProvider).currentDestination;
});

/// Provider for navigation bar visibility
final navigationBarVisibilityProvider = Provider<bool>((ref) {
  return ref.watch(cosmicNavigationProvider).showNavigationBar;
});
