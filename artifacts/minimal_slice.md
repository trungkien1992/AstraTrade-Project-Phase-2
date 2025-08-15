# Phase 1: Game Stats Bar - Minimal Slice

## Scope
**Minimal viable addition** of game statistics display to existing TradeEntryScreen:

### Core Components
1. **Game Stats Widget**: Compact horizontal bar showing:
   - Stellar Shards count with icon
   - Current XP / Level display  
   - Cosmic tier indicator (optional)

2. **Integration Points**:
   - Add to TradeEntryScreen above existing content
   - Connect to existing GameStateProvider
   - Style with existing CosmicTheme
   - Minimal animation on stat changes

### Implementation Strategy
1. **Create GameStatsBar widget** - Reusable component
2. **Extract stats display logic** from MainHubScreen  
3. **Add feature flag** for easy enable/disable
4. **Integrate with existing providers** - no new dependencies

## Flag/Toggles
```dart
// Feature flag for game stats display
final gameStatsEnabledProvider = StateProvider<bool>((ref) => true);

// Usage in TradeEntryScreen
final showGameStats = ref.watch(gameStatsEnabledProvider);
if (showGameStats) {
  // Show stats bar
}
```

## Rollout Plan
1. **Development**: Implement GameStatsBar widget with feature flag
2. **Testing**: Enable flag in development environment
3. **Validation**: Test iOS simulator performance and UX
4. **Production**: Keep flag disabled until validation complete
5. **Gradual Enable**: Enable for testing users first

## Observability
```dart
// Track game stats interactions
AnalyticsService.trackEvent('game_stats_displayed', {
  'stellar_shards': gameState.stellarShards,
  'level': gameState.level,
  'screen': 'trade_entry',
});

// Monitor performance impact
PerformanceMonitoringService.trackRenderTime('trade_entry_with_stats');

// Track feature flag usage
AnalyticsService.trackEvent('feature_flag_enabled', {
  'flag_name': 'game_stats_bar',
  'screen': 'trade_entry',
});
```

## Rollback
**Instant rollback capabilities**:
1. **Feature Flag**: Set `gameStatsEnabledProvider` to `false`
2. **Hot Restart**: Flutter hot restart removes stats immediately  
3. **Code Rollback**: Isolated widget can be removed without breaking existing functionality
4. **Database**: No database changes - purely UI enhancement
5. **Dependencies**: Uses existing GameStateProvider - no new dependencies to break

## Success Metrics
- **Performance**: No increase in render time >100ms
- **Functionality**: All existing trading features work unchanged
- **Visual**: Stats display correctly with cosmic theme
- **iOS Compatibility**: Smooth operation in iOS simulator
- **User Experience**: Stats enhance rather than distract from trading flow

## Technical Implementation
```dart
class GameStatsBar extends ConsumerWidget {
  const GameStatsBar({super.key});
  
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final gameState = ref.watch(gameStateProvider);
    
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(/* cosmic theme */),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        children: [
          _buildStatItem(Icons.auto_awesome, '${gameState.stellarShards}', 'Shards'),
          _buildStatItem(Icons.trending_up, 'LVL ${gameState.level}', 'Level'),
          _buildStatItem(Icons.stars, '${gameState.experience} XP', 'Experience'),
        ],
      ),
    );
  }
}
```