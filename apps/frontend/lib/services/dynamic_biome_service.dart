import 'package:flutter/material.dart';
import 'dart:async';
import 'dart:math' as math;
import '../models/planet_biome.dart';
import '../models/quantum_core.dart';
import '../services/haptic_service.dart';
import '../services/enhanced_audio_service.dart';

/// Enhanced Dynamic Biome Service
/// Provides real-time biome evolution based on trading performance and user behavior
class DynamicBiomeService {
  static final _instance = DynamicBiomeService._internal();
  factory DynamicBiomeService() => _instance;
  DynamicBiomeService._internal();

  final StreamController<BiomeEvolutionEvent> _evolutionController = 
      StreamController<BiomeEvolutionEvent>.broadcast();
  Stream<BiomeEvolutionEvent> get evolutionStream => _evolutionController.stream;

  final StreamController<BiomeVisualUpdate> _visualController = 
      StreamController<BiomeVisualUpdate>.broadcast();
  Stream<BiomeVisualUpdate> get visualStream => _visualController.stream;

  Timer? _evolutionTimer;
  Timer? _visualUpdateTimer;
  Timer? _tradingSyncTimer;

  PlanetBiomeData? _currentBiome;
  PlanetCultivationData? _cultivationData;
  BiomeVisualState? _visualState;
  
  // Enhanced biome evolution parameters
  double _evolutionProgress = 0.0;
  double _cultivationEnergy = 0.0;
  double _tradingMomentum = 0.0;
  double _visualIntensity = 0.5;
  int _consecutiveWins = 0;
  int _consecutiveLosses = 0;
  
  // Dynamic visual elements
  final Map<String, dynamic> _visualElements = {};
  final List<BiomeParticle> _activeParticles = [];
  final List<BiomeEffect> _activeEffects = [];

  /// Initialize dynamic biome system
  Future<void> initializeDynamicBiome({
    required PlanetBiomeData initialBiome,
    required PlanetCultivationData cultivationData,
  }) async {
    try {
      _currentBiome = initialBiome;
      _cultivationData = cultivationData;
      _visualState = _createInitialVisualState(initialBiome.biome);
      
      // Start evolution monitoring
      _startEvolutionMonitoring();
      _startVisualUpdates();
      _startTradingSync();
      
      // Emit initial state
      _emitBiomeEvolution(BiomeEvolutionType.initialized);
      
    } catch (e) {
      throw Exception('Failed to initialize dynamic biome: $e');
    }
  }

  /// Update biome based on trading performance
  Future<void> updateFromTradingPerformance({
    required double pnl,
    required double volume,
    required bool isWin,
    required String symbol,
    required Duration tradeDuration,
  }) async {
    try {
      // Calculate trading impact on biome
      final tradingImpact = _calculateTradingImpact(pnl, volume, tradeDuration);
      
      // Update momentum-based evolution
      if (isWin) {
        _consecutiveWins++;
        _consecutiveLosses = 0;
        _tradingMomentum = (_tradingMomentum + tradingImpact).clamp(0.0, 1.0);
        _cultivationEnergy += tradingImpact * 0.5;
      } else {
        _consecutiveLosses++;
        _consecutiveWins = 0;
        _tradingMomentum = (_tradingMomentum - tradingImpact * 0.3).clamp(0.0, 1.0);
        _cultivationEnergy += tradingImpact * 0.2; // Still some energy from learning
      }

      // Trigger biome-specific reactions
      await _triggerBiomeReaction(isWin, tradingImpact, symbol);
      
      // Update visual effects
      await _updateVisualEffectsFromTrading(isWin, tradingImpact);
      
      // Check for biome evolution
      await _checkBiomeEvolution();
      
      // Emit trading update
      _emitTradingUpdate(pnl, isWin, tradingImpact);
      
    } catch (e) {
      print('Failed to update biome from trading: $e');
    }
  }

  /// Enhanced biome evolution with dynamic thresholds
  Future<void> _checkBiomeEvolution() async {
    if (_currentBiome == null || _cultivationData == null) return;

    final currentBiome = _currentBiome!.biome;
    final nextBiome = currentBiome.nextBiome;
    
    if (nextBiome == null) return; // Already at max level

    // Calculate dynamic evolution criteria
    final evolutionCriteria = _calculateEvolutionCriteria(currentBiome, nextBiome);
    
    // Check if criteria are met
    if (_meetsEvolutionCriteria(evolutionCriteria)) {
      await _evolveBiome(nextBiome, evolutionCriteria);
    } else {
      // Update evolution progress
      _evolutionProgress = _calculateEvolutionProgress(evolutionCriteria);
      _emitEvolutionProgress();
    }
  }

  /// Calculate dynamic evolution criteria
  EvolutionCriteria _calculateEvolutionCriteria(PlanetBiome current, PlanetBiome next) {
    final baseThreshold = next.xpThreshold;
    
    return EvolutionCriteria(
      xpRequired: baseThreshold,
      cultivationRequired: baseThreshold * 0.3,
      tradingVolumeRequired: baseThreshold * 0.5,
      streakRequired: (baseThreshold / 100).floor(),
      biomeSpecificTasks: _getBiomeSpecificTasks(current, next),
      visualMaturity: _visualIntensity,
      communityEngagement: _calculateCommunityEngagement(),
    );
  }

  /// Get biome-specific evolution tasks
  List<BiomeTask> _getBiomeSpecificTasks(PlanetBiome current, PlanetBiome next) {
    switch (current) {
      case PlanetBiome.barren:
        return [
          BiomeTask('First Harvest', 'Generate 100 Stellar Shards', 100, 0),
          BiomeTask('Initial Trade', 'Complete your first real trade', 1, 0),
        ];
      case PlanetBiome.verdant:
        return [
          BiomeTask('Garden Growth', 'Achieve 7-day trading streak', 7, 0),
          BiomeTask('Flora Expansion', 'Generate 1000 Stellar Shards', 1000, 0),
        ];
      case PlanetBiome.volcanic:
        return [
          BiomeTask('Forge Mastery', 'Achieve 15-day trading streak', 15, 0),
          BiomeTask('Lava Flow', 'Complete 50 profitable trades', 50, 0),
        ];
      case PlanetBiome.crystalline:
        return [
          BiomeTask('Crystal Harmony', 'Achieve 30-day trading streak', 30, 0),
          BiomeTask('Perfect Trade', 'Execute a trade with 10%+ profit', 1, 0),
        ];
      case PlanetBiome.transcendent:
        return []; // Max level
    }
  }

  /// Check if evolution criteria are met
  bool _meetsEvolutionCriteria(EvolutionCriteria criteria) {
    return _cultivationEnergy >= criteria.cultivationRequired &&
           _consecutiveWins >= criteria.streakRequired &&
           _visualIntensity >= 0.8 &&
           criteria.biomeSpecificTasks.every((task) => task.current >= task.required);
  }

  /// Calculate evolution progress percentage
  double _calculateEvolutionProgress(EvolutionCriteria criteria) {
    double progress = 0.0;
    
    progress += (_cultivationEnergy / criteria.cultivationRequired) * 0.3;
    progress += (_consecutiveWins / criteria.streakRequired) * 0.2;
    progress += _visualIntensity * 0.2;
    progress += (criteria.biomeSpecificTasks.fold(0.0, (sum, task) => 
        sum + (task.current / task.required)) / criteria.biomeSpecificTasks.length) * 0.3;
    
    return progress.clamp(0.0, 1.0);
  }

  /// Evolve to next biome with enhanced effects
  Future<void> _evolveBiome(PlanetBiome newBiome, EvolutionCriteria criteria) async {
    try {
      final oldBiome = _currentBiome!.biome;
      
      // Create evolution event
      final evolutionEvent = BiomeEvolutionEvent(
        oldBiome: oldBiome,
        newBiome: newBiome,
        evolutionType: BiomeEvolutionType.evolved,
        progress: 1.0,
        timestamp: DateTime.now(),
        metadata: {'criteria': criteria},
      );
      
      // Trigger dramatic visual transformation
      await _triggerEvolutionTransformation(oldBiome, newBiome);
      
      // Update biome state
      _currentBiome = PlanetBiomeData(
        biome: newBiome,
        evolutionProgress: 0.0,
        unlockedAt: DateTime.now(),
        isActive: true,
      );
      
      _cultivationData = _cultivationData!.copyWith(
        biome: newBiome,
        cultivationLevel: 0.0,
      );
      
      _visualState = _createEvolvedVisualState(newBiome);
      
      // Reset progress trackers
      _evolutionProgress = 0.0;
      _consecutiveWins = 0;
      _consecutiveLosses = 0;
      
      // Emit evolution event
      _evolutionController.add(evolutionEvent);
      
      // Play evolution effects
      await HapticService.triggerEvolutionFeedback();
      await EnhancedAudioService().playBiomeEvolution(newBiome);
      
    } catch (e) {
      print('Biome evolution failed: $e');
    }
  }

  /// Calculate trading impact on biome
  double _calculateTradingImpact(double pnl, double volume, Duration duration) {
    final pnlImpact = (pnl.abs() / 100).clamp(0.0, 1.0);
    final volumeImpact = (volume / 1000).clamp(0.0, 1.0);
    const durationImpact = 1.0; // Base impact
    
    return (pnlImpact * 0.4 + volumeImpact * 0.3 + durationImpact * 0.3);
  }

  /// Trigger biome-specific reactions to trading
  Future<void> _triggerBiomeReaction(bool isWin, double impact, String symbol) async {
    final reaction = BiomeReaction(
      biome: _currentBiome!.biome,
      isWin: isWin,
      impact: impact,
      symbol: symbol,
      timestamp: DateTime.now(),
    );
    
    switch (_currentBiome!.biome) {
      case PlanetBiome.barren:
        await _triggerBarrenReaction(reaction);
        break;
      case PlanetBiome.verdant:
        await _triggerVerdantReaction(reaction);
        break;
      case PlanetBiome.volcanic:
        await _triggerVolcanicReaction(reaction);
        break;
      case PlanetBiome.crystalline:
        await _triggerCrystallineReaction(reaction);
        break;
      case PlanetBiome.transcendent:
        await _triggerTranscendentReaction(reaction);
        break;
    }
  }

  /// Barren biome reactions
  Future<void> _triggerBarrenReaction(BiomeReaction reaction) async {
    if (reaction.isWin) {
      // First sparks of life
      _visualElements['seedlings'] = (_visualElements['seedlings'] ?? 0) + reaction.impact * 10;
      _activeParticles.add(BiomeParticle.spark(
        intensity: reaction.impact,
        color: Colors.orange,
      ));
    } else {
      // Dust storms
      _activeEffects.add(BiomeEffect.dustStorm(
        intensity: reaction.impact * 0.5,
        duration: Duration(seconds: (reaction.impact * 5).round()),
      ));
    }
  }

  /// Verdant biome reactions
  Future<void> _triggerVerdantReaction(BiomeReaction reaction) async {
    if (reaction.isWin) {
      // Plant growth
      _visualElements['flora_density'] = (_visualElements['flora_density'] ?? 0.5) + reaction.impact * 0.1;
      _activeParticles.add(BiomeParticle.growth(
        intensity: reaction.impact,
        color: Colors.green,
      ));
    } else {
      // Seasonal changes
      _activeEffects.add(BiomeEffect.seasonalShift(
        intensity: reaction.impact * 0.3,
        duration: Duration(seconds: (reaction.impact * 3).round()),
      ));
    }
  }

  /// Volcanic biome reactions
  Future<void> _triggerVolcanicReaction(BiomeReaction reaction) async {
    if (reaction.isWin) {
      // Lava flows
      _visualElements['lava_intensity'] = (_visualElements['lava_intensity'] ?? 0.3) + reaction.impact * 0.2;
      _activeParticles.add(BiomeParticle.lava(
        intensity: reaction.impact,
        color: Colors.red,
      ));
    } else {
      // Ash clouds
      _activeEffects.add(BiomeEffect.ashCloud(
        intensity: reaction.impact * 0.4,
        duration: Duration(seconds: (reaction.impact * 4).round()),
      ));
    }
  }

  /// Crystalline biome reactions
  Future<void> _triggerCrystallineReaction(BiomeReaction reaction) async {
    if (reaction.isWin) {
      // Crystal growth
      _visualElements['crystal_growth'] = (_visualElements['crystal_growth'] ?? 0.4) + reaction.impact * 0.15;
      _activeParticles.add(BiomeParticle.crystal(
        intensity: reaction.impact,
        color: Colors.cyan,
      ));
    } else {
      // Crystal resonance
      _activeEffects.add(BiomeEffect.crystalResonance(
        intensity: reaction.impact * 0.2,
        duration: Duration(seconds: (reaction.impact * 6).round()),
      ));
    }
  }

  /// Transcendent biome reactions
  Future<void> _triggerTranscendentReaction(BiomeReaction reaction) async {
    if (reaction.isWin) {
      // Cosmic enlightenment
      _visualElements['enlightenment'] = (_visualElements['enlightenment'] ?? 0.6) + reaction.impact * 0.1;
      _activeParticles.add(BiomeParticle.enlightenment(
        intensity: reaction.impact,
        color: Colors.purple,
      ));
    } else {
      // Dimensional shift
      _activeEffects.add(BiomeEffect.dimensionalShift(
        intensity: reaction.impact * 0.1,
        duration: Duration(seconds: (reaction.impact * 8).round()),
      ));
    }
  }

  /// Create initial visual state for biome
  BiomeVisualState _createInitialVisualState(PlanetBiome biome) {
    switch (biome) {
      case PlanetBiome.barren:
        return BiomeVisualState.barren();
      case PlanetBiome.verdant:
        return BiomeVisualState.verdant();
      case PlanetBiome.volcanic:
        return BiomeVisualState.volcanic();
      case PlanetBiome.crystalline:
        return BiomeVisualState.crystalline();
      case PlanetBiome.transcendent:
        return BiomeVisualState.transcendent();
    }
  }

  /// Create evolved visual state
  BiomeVisualState _createEvolvedVisualState(PlanetBiome biome) {
    return _createInitialVisualState(biome).copyWith(
      evolutionLevel: 1.0,
      particleDensity: 2.0,
      effectIntensity: 1.5,
    );
  }

  /// Start evolution monitoring
  void _startEvolutionMonitoring() {
    _evolutionTimer = Timer.periodic(const Duration(minutes: 1), (timer) {
      _checkBiomeEvolution();
    });
  }

  /// Start visual updates
  void _startVisualUpdates() {
    _visualUpdateTimer = Timer.periodic(const Duration(seconds: 2), (timer) {
      _updateVisualEffects();
    });
  }

  /// Start trading sync
  void _startTradingSync() {
    _tradingSyncTimer = Timer.periodic(const Duration(seconds: 30), (timer) {
      _syncWithTradingData();
    });
  }

  /// Update visual effects
  Future<void> _updateVisualEffects() async {
    if (_visualState == null) return;
    
    // Update particle positions and effects
    _updateParticles();
    _updateEffects();
    
    // Emit visual update
    _visualController.add(BiomeVisualUpdate(
      biome: _currentBiome!.biome,
      visualState: _visualState!,
      particles: List.from(_activeParticles),
      effects: List.from(_activeEffects),
      timestamp: DateTime.now(),
    ));
  }

  /// Update particles
  void _updateParticles() {
    _activeParticles.removeWhere((particle) => 
      DateTime.now().difference(particle.createdAt).inSeconds > particle.lifespan);
    
    // Add new particles based on activity
    if (_tradingMomentum > 0.7) {
      _activeParticles.add(BiomeParticle.active(
        intensity: _tradingMomentum,
        color: _getBiomeColor(_currentBiome!.biome),
      ));
    }
  }

  /// Update effects
  void _updateEffects() {
    _activeEffects.removeWhere((effect) => 
      DateTime.now().difference(effect.startTime).inSeconds > effect.duration.inSeconds);
  }

  /// Sync with trading data
  void _syncWithTradingData() {
    // Update momentum decay
    _tradingMomentum *= 0.95; // Gradual decay
    _visualIntensity = (_visualIntensity + _tradingMomentum * 0.1).clamp(0.0, 1.0);
  }

  /// Update visual effects from trading
  Future<void> _updateVisualEffectsFromTrading(bool isWin, double impact) async {
    _visualIntensity = (_visualIntensity + impact * 0.2).clamp(0.0, 1.0);
    
    // Add trading-specific particles
    _activeParticles.add(BiomeParticle.trading(
      isWin: isWin,
      intensity: impact,
      color: isWin ? Colors.green : Colors.red,
    ));
  }

  /// Trigger evolution transformation
  Future<void> _triggerEvolutionTransformation(PlanetBiome old, PlanetBiome newBiome) async {
    // Create dramatic transformation effects
    final transformation = BiomeTransformation(
      oldBiome: old,
      newBiome: newBiome,
      duration: const Duration(seconds: 5),
      intensity: 1.0,
    );
    
    // Emit transformation events
    for (int i = 0; i < 50; i++) {
      await Future.delayed(const Duration(milliseconds: 100));
      _visualController.add(BiomeVisualUpdate(
        biome: newBiome,
        visualState: _visualState!,
        particles: _generateTransformationParticles(old, newBiome, i / 50),
        effects: [BiomeEffect.evolution(intensity: i / 50)],
        timestamp: DateTime.now(),
      ));
    }
  }

  /// Generate transformation particles
  List<BiomeParticle> _generateTransformationParticles(PlanetBiome old, PlanetBiome newBiome, double progress) {
    return List.generate(20, (index) {
      return BiomeParticle.transformation(
        fromColor: _getBiomeColor(old),
        toColor: _getBiomeColor(newBiome),
        progress: progress,
        randomOffset: index * 0.1,
      );
    });
  }

  /// Get biome color
  Color _getBiomeColor(PlanetBiome biome) {
    switch (biome) {
      case PlanetBiome.barren:
        return Colors.brown;
      case PlanetBiome.verdant:
        return Colors.green;
      case PlanetBiome.volcanic:
        return Colors.red;
      case PlanetBiome.crystalline:
        return Colors.cyan;
      case PlanetBiome.transcendent:
        return Colors.purple;
    }
  }

  /// Calculate community engagement
  double _calculateCommunityEngagement() {
    // Placeholder for community engagement calculation
    return 0.5;
  }

  /// Emit biome evolution event
  void _emitBiomeEvolution(BiomeEvolutionType type) {
    _evolutionController.add(BiomeEvolutionEvent(
      oldBiome: _currentBiome?.biome,
      newBiome: _currentBiome?.biome,
      evolutionType: type,
      progress: _evolutionProgress,
      timestamp: DateTime.now(),
    ));
  }

  /// Emit evolution progress
  void _emitEvolutionProgress() {
    _evolutionController.add(BiomeEvolutionEvent(
      oldBiome: _currentBiome?.biome,
      newBiome: _currentBiome?.biome?.nextBiome,
      evolutionType: BiomeEvolutionType.progress,
      progress: _evolutionProgress,
      timestamp: DateTime.now(),
    ));
  }

  /// Emit trading update
  void _emitTradingUpdate(double pnl, bool isWin, double impact) {
    _evolutionController.add(BiomeEvolutionEvent(
      oldBiome: _currentBiome?.biome,
      newBiome: _currentBiome?.biome,
      evolutionType: BiomeEvolutionType.tradingUpdate,
      progress: impact,
      timestamp: DateTime.now(),
      metadata: {
        'pnl': pnl,
        'isWin': isWin,
        'impact': impact,
      },
    ));
  }

  /// Dispose service
  void dispose() {
    _evolutionTimer?.cancel();
    _visualUpdateTimer?.cancel();
    _tradingSyncTimer?.cancel();
    _evolutionController.close();
    _visualController.close();
  }

  /// Getters
  PlanetBiomeData? get currentBiome => _currentBiome;
  PlanetCultivationData? get cultivationData => _cultivationData;
  BiomeVisualState? get visualState => _visualState;
  double get evolutionProgress => _evolutionProgress;
  double get tradingMomentum => _tradingMomentum;
  List<BiomeParticle> get activeParticles => List.unmodifiable(_activeParticles);
  List<BiomeEffect> get activeEffects => List.unmodifiable(_activeEffects);
}

/// Biome evolution event types
enum BiomeEvolutionType {
  initialized,
  progress,
  evolved,
  tradingUpdate,
}

/// Biome evolution event
class BiomeEvolutionEvent {
  final PlanetBiome? oldBiome;
  final PlanetBiome? newBiome;
  final BiomeEvolutionType evolutionType;
  final double progress;
  final DateTime timestamp;
  final Map<String, dynamic>? metadata;

  BiomeEvolutionEvent({
    this.oldBiome,
    this.newBiome,
    required this.evolutionType,
    required this.progress,
    required this.timestamp,
    this.metadata,
  });
}

/// Biome visual state
class BiomeVisualState {
  final PlanetBiome biome;
  final double evolutionLevel;
  final double particleDensity;
  final double effectIntensity;
  final Color primaryColor;
  final Color secondaryColor;
  final List<Color> gradientColors;
  final Map<String, double> elementLevels;

  BiomeVisualState({
    required this.biome,
    this.evolutionLevel = 0.0,
    this.particleDensity = 1.0,
    this.effectIntensity = 1.0,
    required this.primaryColor,
    required this.secondaryColor,
    required this.gradientColors,
    this.elementLevels = const {},
  });

  factory BiomeVisualState.barren() => BiomeVisualState(
    biome: PlanetBiome.barren,
    primaryColor: Colors.brown,
    secondaryColor: Colors.orange,
    gradientColors: [Colors.brown.shade800, Colors.orange.shade900],
    elementLevels: {'dust': 0.8, 'rock': 0.6, 'void': 0.9},
  );

  factory BiomeVisualState.verdant() => BiomeVisualState(
    biome: PlanetBiome.verdant,
    primaryColor: Colors.green,
    secondaryColor: Colors.lightGreen,
    gradientColors: [Colors.green.shade800, Colors.lightGreen.shade600],
    elementLevels: {'flora': 0.7, 'water': 0.6, 'life': 0.8},
  );

  factory BiomeVisualState.volcanic() => BiomeVisualState(
    biome: PlanetBiome.volcanic,
    primaryColor: Colors.red,
    secondaryColor: Colors.orange,
    gradientColors: [Colors.red.shade900, Colors.orange.shade800],
    elementLevels: {'lava': 0.8, 'heat': 0.9, 'forge': 0.7},
  );

  factory BiomeVisualState.crystalline() => BiomeVisualState(
    biome: PlanetBiome.crystalline,
    primaryColor: Colors.cyan,
    secondaryColor: Colors.blue,
    gradientColors: [Colors.cyan.shade800, Colors.blue.shade600],
    elementLevels: {'crystal': 0.9, 'light': 0.8, 'harmony': 0.7},
  );

  factory BiomeVisualState.transcendent() => BiomeVisualState(
    biome: PlanetBiome.transcendent,
    primaryColor: Colors.purple,
    secondaryColor: Colors.indigo,
    gradientColors: [Colors.purple.shade800, Colors.indigo.shade600],
    elementLevels: {'cosmic': 0.9, 'energy': 0.8, 'wisdom': 0.7},
  );

  BiomeVisualState copyWith({
    double? evolutionLevel,
    double? particleDensity,
    double? effectIntensity,
    Color? primaryColor,
    Color? secondaryColor,
    List<Color>? gradientColors,
    Map<String, double>? elementLevels,
  }) {
    return BiomeVisualState(
      biome: biome,
      evolutionLevel: evolutionLevel ?? this.evolutionLevel,
      particleDensity: particleDensity ?? this.particleDensity,
      effectIntensity: effectIntensity ?? this.effectIntensity,
      primaryColor: primaryColor ?? this.primaryColor,
      secondaryColor: secondaryColor ?? this.secondaryColor,
      gradientColors: gradientColors ?? this.gradientColors,
      elementLevels: elementLevels ?? this.elementLevels,
    );
  }
}

/// Biome visual update
class BiomeVisualUpdate {
  final PlanetBiome biome;
  final BiomeVisualState visualState;
  final List<BiomeParticle> particles;
  final List<BiomeEffect> effects;
  final DateTime timestamp;

  BiomeVisualUpdate({
    required this.biome,
    required this.visualState,
    required this.particles,
    required this.effects,
    required this.timestamp,
  });
}

/// Biome particle system
class BiomeParticle {
  final Offset position;
  final double intensity;
  final Color color;
  final DateTime createdAt;
  final int lifespan;
  final ParticleType type;

  BiomeParticle({
    required this.position,
    required this.intensity,
    required this.color,
    required this.createdAt,
    required this.lifespan,
    required this.type,
  });

  factory BiomeParticle.spark({
    required double intensity,
    required Color color,
  }) => BiomeParticle(
    position: Offset(
      math.Random().nextDouble() * 100,
      math.Random().nextDouble() * 100,
    ),
    intensity: intensity,
    color: color,
    createdAt: DateTime.now(),
    lifespan: 3,
    type: ParticleType.spark,
  );

  factory BiomeParticle.growth({
    required double intensity,
    required Color color,
  }) => BiomeParticle(
    position: Offset(
      math.Random().nextDouble() * 100,
      math.Random().nextDouble() * 100,
    ),
    intensity: intensity,
    color: color,
    createdAt: DateTime.now(),
    lifespan: 5,
    type: ParticleType.growth,
  );

  factory BiomeParticle.trading({
    required bool isWin,
    required double intensity,
    required Color color,
  }) => BiomeParticle(
    position: Offset(
      math.Random().nextDouble() * 100,
      math.Random().nextDouble() * 100,
    ),
    intensity: intensity,
    color: color,
    createdAt: DateTime.now(),
    lifespan: isWin ? 4 : 2,
    type: isWin ? ParticleType.win : ParticleType.loss,
  );

  factory BiomeParticle.transformation({
    required Color fromColor,
    required Color toColor,
    required double progress,
    required double randomOffset,
  }) => BiomeParticle(
    position: Offset(
      math.Random().nextDouble() * 100 + randomOffset * 10,
      math.Random().nextDouble() * 100 + randomOffset * 10,
    ),
    intensity: 1.0,
    color: Color.lerp(fromColor, toColor, progress)!,
    createdAt: DateTime.now(),
    lifespan: 2,
    type: ParticleType.transformation,
  );

  factory BiomeParticle.active({
    required double intensity,
    required Color color,
  }) => BiomeParticle(
    position: Offset(
      math.Random().nextDouble() * 100,
      math.Random().nextDouble() * 100,
    ),
    intensity: intensity,
    color: color,
    createdAt: DateTime.now(),
    lifespan: 2,
    type: ParticleType.active,
  );

  factory BiomeParticle.lava({
    required double intensity,
    required Color color,
  }) => BiomeParticle(
    position: Offset(
      math.Random().nextDouble() * 100,
      math.Random().nextDouble() * 100,
    ),
    intensity: intensity,
    color: color,
    createdAt: DateTime.now(),
    lifespan: 4,
    type: ParticleType.lava,
  );

  factory BiomeParticle.crystal({
    required double intensity,
    required Color color,
  }) => BiomeParticle(
    position: Offset(
      math.Random().nextDouble() * 100,
      math.Random().nextDouble() * 100,
    ),
    intensity: intensity,
    color: color,
    createdAt: DateTime.now(),
    lifespan: 6,
    type: ParticleType.crystal,
  );

  factory BiomeParticle.enlightenment({
    required double intensity,
    required Color color,
  }) => BiomeParticle(
    position: Offset(
      math.Random().nextDouble() * 100,
      math.Random().nextDouble() * 100,
    ),
    intensity: intensity,
    color: color,
    createdAt: DateTime.now(),
    lifespan: 8,
    type: ParticleType.enlightenment,
  );
}

/// Biome effects
class BiomeEffect {
  final EffectType type;
  final double intensity;
  final Duration duration;
  final DateTime startTime;
  final Color color;

  BiomeEffect({
    required this.type,
    required this.intensity,
    required this.duration,
    required this.startTime,
    required this.color,
  });

  factory BiomeEffect.dustStorm({
    required double intensity,
    required Duration duration,
  }) => BiomeEffect(
    type: EffectType.dustStorm,
    intensity: intensity,
    duration: duration,
    startTime: DateTime.now(),
    color: Colors.brown,
  );

  factory BiomeEffect.seasonalShift({
    required double intensity,
    required Duration duration,
  }) => BiomeEffect(
    type: EffectType.seasonalShift,
    intensity: intensity,
    duration: duration,
    startTime: DateTime.now(),
    color: Colors.green,
  );

  factory BiomeEffect.ashCloud({
    required double intensity,
    required Duration duration,
  }) => BiomeEffect(
    type: EffectType.ashCloud,
    intensity: intensity,
    duration: duration,
    startTime: DateTime.now(),
    color: Colors.grey,
  );

  factory BiomeEffect.crystalResonance({
    required double intensity,
    required Duration duration,
  }) => BiomeEffect(
    type: EffectType.crystalResonance,
    intensity: intensity,
    duration: duration,
    startTime: DateTime.now(),
    color: Colors.cyan,
  );

  factory BiomeEffect.dimensionalShift({
    required double intensity,
    required Duration duration,
  }) => BiomeEffect(
    type: EffectType.dimensionalShift,
    intensity: intensity,
    duration: duration,
    startTime: DateTime.now(),
    color: Colors.purple,
  );

  factory BiomeEffect.evolution({
    required double intensity,
  }) => BiomeEffect(
    type: EffectType.evolution,
    intensity: intensity,
    duration: const Duration(seconds: 5),
    startTime: DateTime.now(),
    color: Colors.white,
  );
}

/// Evolution criteria
class EvolutionCriteria {
  final double xpRequired;
  final double cultivationRequired;
  final double tradingVolumeRequired;
  final int streakRequired;
  final List<BiomeTask> biomeSpecificTasks;
  final double visualMaturity;
  final double communityEngagement;

  EvolutionCriteria({
    required this.xpRequired,
    required this.cultivationRequired,
    required this.tradingVolumeRequired,
    required this.streakRequired,
    required this.biomeSpecificTasks,
    required this.visualMaturity,
    required this.communityEngagement,
  });
}

/// Biome task
class BiomeTask {
  final String name;
  final String description;
  final double required;
  double current;

  BiomeTask(this.name, this.description, this.required, this.current);

  double get progress => (current / required).clamp(0.0, 1.0);
}

/// Biome reaction
class BiomeReaction {
  final PlanetBiome biome;
  final bool isWin;
  final double impact;
  final String symbol;
  final DateTime timestamp;

  BiomeReaction({
    required this.biome,
    required this.isWin,
    required this.impact,
    required this.symbol,
    required this.timestamp,
  });
}

/// Biome transformation
class BiomeTransformation {
  final PlanetBiome oldBiome;
  final PlanetBiome newBiome;
  final Duration duration;
  final double intensity;

  BiomeTransformation({
    required this.oldBiome,
    required this.newBiome,
    required this.duration,
    required this.intensity,
  });
}

/// Particle types
enum ParticleType {
  spark,
  growth,
  win,
  loss,
  transformation,
  active,
  lava,
  crystal,
  enlightenment,
}

/// Effect types
enum EffectType {
  dustStorm,
  seasonalShift,
  ashCloud,
  crystalResonance,
  dimensionalShift,
  evolution,
}