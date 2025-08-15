import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
// import '../models/planet_biome.dart';

/// Enhanced Haptic Service with biome-specific feedback patterns
class EnhancedHapticService {
  static final _instance = EnhancedHapticService._internal();
  factory EnhancedHapticService() => _instance;
  EnhancedHapticService._internal();

  bool _isEnabled = true;
  bool _isInitialized = false;
  double _intensityMultiplier = 1.0;

  // Biome-specific haptic patterns
  // final Map<PlanetBiome, BiomeHapticConfig> _biomeConfigs = {
  //   PlanetBiome.barren: BiomeHapticConfig(
  //     tapPattern: HapticPattern(
  //       intensities: [0, 30, 0, 20],
  //       durations: [0, 50, 30, 40],
  //       sharpness: 0.8,
  //       texture: 'rough',
  //     ),
  //     winPattern: HapticPattern(
  //       intensities: [0, 40, 0, 60, 0, 80],
  //       durations: [0, 100, 50, 150, 50, 200],
  //       sharpness: 0.9,
  //       texture: 'gritty',
  //     ),
  //     lossPattern: HapticPattern(
  //       intensities: [0, 20, 0, 15, 0, 10],
  //       durations: [0, 200, 100, 150, 100, 100],
  //       sharpness: 0.7,
  //       texture: 'soft',
  //     ),
  //     evolutionPattern: HapticPattern(
  //       intensities: [0, 30, 0, 50, 0, 70, 0, 90],
  //       durations: [0, 200, 100, 300, 100, 400, 100, 500],
  //       sharpness: 1.0,
  //       texture: 'building',
  //     ),
  //   ),
  //   PlanetBiome.verdant: BiomeHapticConfig(
  //     tapPattern: HapticPattern(
  //       intensities: [0, 25, 0, 35],
  //       durations: [0, 60, 40, 80],
  //       sharpness: 0.4,
  //       texture: 'soft',
  //     ),
  //     winPattern: HapticPattern(
  //       intensities: [0, 30, 0, 45, 0, 60],
  //       durations: [0, 150, 75, 200, 75, 250],
  //       sharpness: 0.5,
  //       texture: 'gentle',
  //     ),
  //     lossPattern: HapticPattern(
  //       intensities: [0, 20, 0, 15],
  //       durations: [0, 300, 150, 200],
  //       sharpness: 0.3,
  //       texture: 'soft',
  //     ),
  //     evolutionPattern: HapticPattern(
  //       intensities: [0, 25, 0, 40, 0, 55, 0, 70],
  //       durations: [0, 300, 150, 400, 150, 500, 150, 600],
  //       sharpness: 0.6,
  //       texture: 'growing',
  //     ),
  //   ),
  //   PlanetBiome.volcanic: BiomeHapticConfig(
  //     tapPattern: HapticPattern(
  //       intensities: [0, 50, 0, 40],
  //       durations: [0, 40, 20, 60],
  //       sharpness: 0.9,
  //       texture: 'sharp',
  //     ),
  //     winPattern: HapticPattern(
  //       intensities: [0, 60, 0, 80, 0, 100],
  //       durations: [0, 80, 40, 120, 40, 160],
  //       sharpness: 1.0,
  //       texture: 'intense',
  //     ),
  //     lossPattern: HapticPattern(
  //       intensities: [0, 30, 0, 25, 0, 20],
  //       durations: [0, 150, 75, 100, 75, 50],
  //       sharpness: 0.8,
  //       texture: 'fading',
  //     ),
  //     evolutionPattern: HapticPattern(
  //       intensities: [0, 40, 0, 70, 0, 90, 0, 120],
  //       durations: [0, 100, 50, 200, 50, 300, 50, 400],
  //       sharpness: 0.95,
  //       texture: 'forging',
  //     ),
  //   ),
  //   PlanetBiome.crystalline: BiomeHapticConfig(
  //     tapPattern: HapticPattern(
  //       intensities: [0, 35, 0, 45],
  //       durations: [0, 45, 25, 55],
  //       sharpness: 0.7,
  //       texture: 'clear',
  //     ),
  //     winPattern: HapticPattern(
  //       intensities: [0, 50, 0, 65, 0, 80],
  //       durations: [0, 120, 60, 180, 60, 240],
  //       sharpness: 0.8,
  //       texture: 'crystalline',
  //     ),
  //     lossPattern: HapticPattern(
  //       intensities: [0, 25, 0, 20],
  //       durations: [0, 250, 125, 180],
  //       sharpness: 0.6,
  //       texture: 'fracture',
  //     ),
  //     evolutionPattern: HapticPattern(
  //       intensities: [0, 45, 0, 65, 0, 85, 0, 105],
  //       durations: [0, 200, 100, 300, 100, 400, 100, 500],
  //       sharpness: 0.85,
  //       texture: 'resonance',
  //     ),
  //   ),
  //   PlanetBiome.transcendent: BiomeHapticConfig(
  //     tapPattern: HapticPattern(
  //       intensities: [0, 40, 0, 60],
  //       durations: [0, 50, 30, 70],
  //       sharpness: 0.6,
  //       texture: 'ethereal',
  //     ),
  //     winPattern: HapticPattern(
  //       intensities: [0, 70, 0, 90, 0, 110],
  //       durations: [0, 200, 100, 300, 100, 400],
  //       sharpness: 0.7,
  //       texture: 'cosmic',
  //     ),
  //     lossPattern: HapticPattern(
  //       intensities: [0, 30, 0, 25],
  //       durations: [0, 400, 200, 300],
  //       sharpness: 0.5,
  //       texture: 'void',
  //     ),
  //     evolutionPattern: HapticPattern(
  //       intensities: [0, 60, 0, 90, 0, 120, 0, 150],
  //       durations: [0, 300, 150, 500, 150, 700, 150, 900],
  //       sharpness: 0.75,
  //       texture: 'ascension',
  //     ),
  //   ),
  // };

  /// Initialize haptic service
  Future<void> initialize() async {
    try {
      _isInitialized = true;
    } catch (e) {
      print('Haptic initialization failed: $e');
    }
  }

  /// Trigger biome-specific tap feedback
  // Future<void> triggerBiomeTap(PlanetBiome biome, {double intensity = 1.0}) async {
  //   if (!_isEnabled || !_isInitialized) return;

  //   final config = _biomeConfigs[biome];
  //   if (config == null) return;

  //   await _triggerPattern(config.tapPattern, intensity: intensity);
  // }

  /// Trigger biome-specific win feedback
  // Future<void> triggerBiomeWin(PlanetBiome biome, {double intensity = 1.0}) async {
  //   if (!_isEnabled || !_isInitialized) return;

  //   final config = _biomeConfigs[biome];
  //   if (config == null) return;

  //   await _triggerPattern(config.winPattern, intensity: intensity);
  // }

  /// Trigger biome-specific loss feedback
  // Future<void> triggerBiomeLoss(PlanetBiome biome, {double intensity = 1.0}) async {
  //   if (!_isEnabled || !_isInitialized) return;

  //   final config = _biomeConfigs[biome];
  //   if (config == null) return;

  //   await _triggerPattern(config.lossPattern, intensity: intensity);
  // }

  /// Trigger biome evolution feedback
  // Future<void> triggerBiomeEvolution(PlanetBiome newBiome) async {
  //   if (!_isEnabled || !_isInitialized) return;

  //   final config = _biomeConfigs[newBiome];
  //   if (config == null) return;

  //   await _triggerPattern(config.evolutionPattern, intensity: 1.5);
  // }

  /// Trigger custom haptic pattern
  Future<void> triggerCustomPattern(
    HapticPattern pattern, {
    double intensity = 1.0,
  }) async {
    if (!_isEnabled || !_isInitialized) return;

    await _triggerPattern(pattern, intensity: intensity);
  }

  /// Trigger advanced trading feedback
  // Future<void> triggerTradingFeedback({
  //   required bool isWin,
  //   required double profit,
  //   required PlanetBiome biome,
  //   required double volume,
  // }) async {
  //   if (!_isEnabled || !_isInitialized) return;

  //   final impact = (profit.abs() / 1000).clamp(0.1, 1.0);
  //   final adjustedIntensity = impact * _intensityMultiplier;

  //   if (isWin) {
  //     await triggerBiomeWin(biome, intensity: adjustedIntensity);
  //   } else {
  //     await triggerBiomeLoss(biome, intensity: adjustedIntensity);
  //   }

  //   // Add volume-based haptic pulse
  //   await _triggerVolumePulse(volume, adjustedIntensity);
  // }

  /// Trigger particle effect feedback
  // Future<void> triggerParticleEffect({
  //   required ParticleType type,
  //   required double intensity,
  //   PlanetBiome? biome,
  // }) async {
  //   if (!_isEnabled || !_isInitialized) return;

  //   final pattern = _getParticlePattern(type, biome);
  //   if (pattern != null) {
  //     await _triggerPattern(pattern, intensity: intensity);
  //   }
  // }

  /// Trigger streak feedback
  // Future<void> triggerStreakFeedback(int streakDays, PlanetBiome biome) async {
  //   if (!_isEnabled || !_isInitialized) return;

  //   final streakIntensity = (streakDays / 30).clamp(0.1, 2.0);

  //   final streakPattern = HapticPattern(
  //     intensities: List.generate(
  //       streakDays.clamp(3, 8),
  //       (index) => 0 + (index + 1) * 15,
  //     ),
  //     durations: List.generate(
  //       streakDays.clamp(3, 8),
  //       (index) => 50 + index * 25,
  //     ),
  //     sharpness: 0.8,
  //     texture: 'building',
  //   );

  //   await _triggerPattern(streakPattern, intensity: streakIntensity);
  // }

  /// Trigger NFT discovery feedback
  // Future<void> triggerNFTDiscovery(String rarity, PlanetBiome biome) async {
  //   if (!_isEnabled || !_isInitialized) return;

  //   final rarityMultiplier = _getRarityMultiplier(rarity);

  //   final nftPattern = HapticPattern(
  //     intensities: [0, 80, 0, 100, 0, 120],
  //     durations: [0, 100, 50, 150, 50, 200],
  //     sharpness: 1.0,
  //     texture: 'treasure',
  //   );

  //   await _triggerPattern(nftPattern, intensity: rarityMultiplier);
  // }

  /// Trigger quantum anomaly feedback
  // Future<void> triggerQuantumAnomaly(QuantumAnomalyType type, PlanetBiome biome) async {
  //   if (!_isEnabled || !_isInitialized) return;

  //   final anomalyPattern = _getAnomalyPattern(type, biome);
  //   if (anomalyPattern != null) {
  //     await _triggerPattern(anomalyPattern, intensity: 1.2);
  //   }
  // }

  /// Trigger immersive ambient feedback
  // Future<void> triggerAmbientFeedback(PlanetBiome biome, {double intensity = 0.3}) async {
  //   if (!_isEnabled || !_isInitialized) return;

  //   final ambientPattern = _getAmbientPattern(biome);
  //   if (ambientPattern != null) {
  //     await _triggerPattern(ambientPattern, intensity: intensity);
  //   }
  // }

  /// Private method to trigger actual haptic pattern
  Future<void> _triggerPattern(
    HapticPattern pattern, {
    double intensity = 1.0,
  }) async {
    try {
      final adjustedIntensities = pattern.intensities
          .map(
            (i) => (i * intensity * _intensityMultiplier).round().clamp(0, 255),
          )
          .toList();

      final adjustedDurations = pattern.durations
          .map((d) => (d * intensity).round().clamp(1, 1000))
          .toList();

      await HapticFeedback.vibrate();

      // For iOS, use custom haptic patterns
      if (pattern.intensities.length > 1) {
        await _triggerCustomPattern(adjustedIntensities, adjustedDurations);
      } else {
        await _triggerSimplePattern(adjustedIntensities.first);
      }
    } catch (e) {
      print('Haptic trigger failed: $e');
    }
  }

  /// Trigger custom haptic pattern
  Future<void> _triggerCustomPattern(
    List<int> intensities,
    List<int> durations,
  ) async {
    // This would use platform-specific haptic APIs
    // For now, we'll use a sequence of vibrations
    for (int i = 0; i < intensities.length; i++) {
      if (i > 0) {
        await Future.delayed(Duration(milliseconds: durations[i]));
      }
      if (intensities[i] > 0) {
        await _triggerSimplePattern(intensities[i]);
      }
    }
  }

  /// Trigger simple haptic pattern
  Future<void> _triggerSimplePattern(int intensity) async {
    try {
      // Use platform-specific haptic feedback
      if (intensity > 150) {
        await HapticFeedback.heavyImpact();
      } else if (intensity > 100) {
        await HapticFeedback.mediumImpact();
      } else if (intensity > 50) {
        await HapticFeedback.lightImpact();
      } else {
        await HapticFeedback.selectionClick();
      }
    } catch (e) {
      print('Simple haptic failed: $e');
    }
  }

  /// Trigger volume-based pulse
  Future<void> _triggerVolumePulse(double volume, double intensity) async {
    final pulseIntensity = (volume * intensity * 100).round().clamp(0, 255);
    await _triggerSimplePattern(pulseIntensity);
  }

  /// Get particle pattern
  // HapticPattern? _getParticlePattern(ParticleType type, PlanetBiome? biome) {
  //   if (biome == null) return null;

  //   final basePattern = _biomeConfigs[biome]?.tapPattern;
  //   if (basePattern == null) return null;

  //   return switch (type) {
  //     ParticleType.spark => basePattern.copyWith(
  //       intensities: basePattern.intensities.map((i) => (i * 1.5).round()).toList(),
  //       texture: 'sparkle',
  //     ),
  //     ParticleType.growth => basePattern.copyWith(
  //       intensities: basePattern.intensities.map((i) => (i * 0.8).round()).toList(),
  //       texture: 'organic',
  //     ),
  //     _ => basePattern,
  //   };
  // }

  /// Get anomaly pattern
  // HapticPattern? _getAnomalyPattern(QuantumAnomalyType type, PlanetBiome biome) {
  //   final baseConfig = _biomeConfigs[biome];
  //   if (baseConfig == null) return null;

  //   return switch (type) {
  //     QuantumAnomalyType.stellarStorm => HapticPattern(
  //       intensities: [0, 60, 0, 80, 0, 100],
  //       durations: [0, 50, 25, 75, 25, 100],
  //       sharpness: 0.9,
  //       texture: 'storm',
  //     ),
  //     QuantumAnomalyType.voidRift => HapticPattern(
  //       intensities: [0, 40, 0, 30, 0, 20, 0, 10],
  //       durations: [0, 100, 50, 80, 50, 60, 50, 40],
  //       sharpness: 0.7,
  //       texture: 'void',
  //     ),
  //     QuantumAnomalyType.temporalFlux => HapticPattern(
  //       intensities: [0, 50, 0, 45, 0, 40, 0, 35],
  //       durations: [0, 30, 15, 25, 15, 20, 15, 15],
  //       sharpness: 0.6,
  //       texture: 'flux',
  //     ),
  //     QuantumAnomalyType.cosmicResonance => HapticPattern(
  //       intensities: [0, 70, 0, 90, 0, 110],
  //       durations: [0, 150, 75, 200, 75, 250],
  //       sharpness: 0.8,
  //       texture: 'resonance',
  //     ),
  //   };
  // }

  /// Get ambient pattern
  // HapticPattern? _getAmbientPattern(PlanetBiome biome) {
  //   final baseConfig = _biomeConfigs[biome];
  //   if (baseConfig == null) return null;

  //   return baseConfig.tapPattern.copyWith(
  //     intensities: baseConfig.tapPattern.intensities.map((i) => (i * 0.3).round()).toList(),
  //     texture: 'ambient',
  //   );
  // }

  /// Get rarity multiplier
  double _getRarityMultiplier(String rarity) {
    return switch (rarity.toLowerCase()) {
      'legendary' => 2.0,
      'epic' => 1.5,
      'rare' => 1.2,
      _ => 1.0,
    };
  }

  /// Set intensity multiplier
  void setIntensityMultiplier(double multiplier) {
    _intensityMultiplier = multiplier.clamp(0.1, 3.0);
  }

  /// Toggle haptic feedback
  void toggleHaptics() {
    _isEnabled = !_isEnabled;
  }

  /// Get current settings
  bool get isEnabled => _isEnabled;
  bool get isInitialized => _isInitialized;
  double get intensityMultiplier => _intensityMultiplier;

  /// Dispose service
  void dispose() {
    // No disposal needed for haptic feedback
  }
}

/// Haptic pattern configuration
class HapticPattern {
  final List<int> intensities;
  final List<int> durations;
  final double sharpness;
  final String texture;

  HapticPattern({
    required this.intensities,
    required this.durations,
    this.sharpness = 0.5,
    this.texture = 'default',
  });

  HapticPattern copyWith({
    List<int>? intensities,
    List<int>? durations,
    double? sharpness,
    String? texture,
  }) {
    return HapticPattern(
      intensities: intensities ?? this.intensities,
      durations: durations ?? this.durations,
      sharpness: sharpness ?? this.sharpness,
      texture: texture ?? this.texture,
    );
  }
}

/// Biome haptic configuration
class BiomeHapticConfig {
  final HapticPattern tapPattern;
  final HapticPattern winPattern;
  final HapticPattern lossPattern;
  final HapticPattern evolutionPattern;

  BiomeHapticConfig({
    required this.tapPattern,
    required this.winPattern,
    required this.lossPattern,
    required this.evolutionPattern,
  });
}

/// Particle types for haptic feedback
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

/// Quantum anomaly types
enum QuantumAnomalyType {
  stellarStorm,
  voidRift,
  temporalFlux,
  cosmicResonance,
}
