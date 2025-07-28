import 'package:flutter/material.dart';
import 'package:audioplayers/audioplayers.dart';
import 'dart:async';
import '../models/planet_biome.dart';
import '../services/dynamic_biome_service.dart';

/// Enhanced Audio Service with biome-specific soundscapes and dynamic effects
class EnhancedAudioService {
  static final _instance = EnhancedAudioService._internal();
  factory EnhancedAudioService() => _instance;
  EnhancedAudioService._internal();

  final AudioPlayer _backgroundPlayer = AudioPlayer();
  final AudioPlayer _effectPlayer = AudioPlayer();
  final AudioPlayer _ambientPlayer = AudioPlayer();
  
  bool _isInitialized = false;
  bool _isEnabled = true;
  double _masterVolume = 0.7;
  double _ambientVolume = 0.4;
  double _effectVolume = 0.8;
  
  PlanetBiome? _currentBiome;
  String? _currentAmbientTrack;
  Timer? _ambientUpdateTimer;
  
  // Audio asset mapping
  final Map<PlanetBiome, BiomeAudioConfig> _biomeAudioConfigs = {
    PlanetBiome.barren: BiomeAudioConfig(
      backgroundTrack: 'audio/barren_wasteland.mp3',
      ambientSounds: [
        'audio/wind_howling.mp3',
        'audio/dust_storm.mp3',
        'audio/rocks_tumbling.mp3',
      ],
      effectSounds: {
        'tap': 'audio/dust_tap.mp3',
        'win': 'audio/desert_bloom.mp3',
        'loss': 'audio/dust_storm_intense.mp3',
        'evolution': 'audio/oasis_emerges.mp3',
      },
      baseFrequency: 60,
      harmonicScale: 'minor',
    ),
    PlanetBiome.verdant: BiomeAudioConfig(
      backgroundTrack: 'audio/verdant_gardens.mp3',
      ambientSounds: [
        'audio/birds_chirping.mp3',
        'audio/water_flowing.mp3',
        'audio/leaves_rustling.mp3',
      ],
      effectSounds: {
        'tap': 'audio/gentle_rain.mp3',
        'win': 'audio/flowers_blooming.mp3',
        'loss': 'audio/autumn_wind.mp3',
        'evolution': 'audio/forest_growth.mp3',
      },
      baseFrequency: 432,
      harmonicScale: 'major',
    ),
    PlanetBiome.volcanic: BiomeAudioConfig(
      backgroundTrack: 'audio/volcanic_forge.mp3',
      ambientSounds: [
        'audio/lava_bubbling.mp3',
        'audio/fires_crackling.mp3',
        'audio/metallic_clanging.mp3',
      ],
      effectSounds: {
        'tap': 'audio/metal_strike.mp3',
        'win': 'audio/lava_eruption.mp3',
        'loss': 'audio/steam_hiss.mp3',
        'evolution': 'audio/forge_ignition.mp3',
      },
      baseFrequency: 220,
      harmonicScale: 'diminished',
    ),
    PlanetBiome.crystalline: BiomeAudioConfig(
      backgroundTrack: 'audio/crystalline_sanctuary.mp3',
      ambientSounds: [
        'audio/crystal_harmonics.mp3',
        'audio/celestial_tones.mp3',
        'audio/glass_chimes.mp3',
      ],
      effectSounds: {
        'tap': 'audio/crystal_tone.mp3',
        'win': 'audio/harmonic_resonance.mp3',
        'loss': 'audio/crystal_fracture.mp3',
        'evolution': 'audio/ascending_scale.mp3',
      },
      baseFrequency: 528,
      harmonicScale: 'pentatonic',
    ),
    PlanetBiome.transcendent: BiomeAudioConfig(
      backgroundTrack: 'audio/transcendent_realm.mp3',
      ambientSounds: [
        'audio/cosmic_vibrations.mp3',
        'audio/ethereal_winds.mp3',
        'audio/quantum_flux.mp3',
      ],
      effectSounds: {
        'tap': 'audio/quantum_particle.mp3',
        'win': 'audio/dimensional_shift.mp3',
        'loss': 'audio/void_echo.mp3',
        'evolution': 'audio/enlightenment_chord.mp3',
      },
      baseFrequency: 852,
      harmonicScale: 'solfeggio',
    ),
  };

  /// Initialize enhanced audio system
  Future<void> initialize() async {
    if (_isInitialized) return;
    
    try {
      // Configure audio players
      await _backgroundPlayer.setReleaseMode(ReleaseMode.loop);
      await _ambientPlayer.setReleaseMode(ReleaseMode.loop);
      
      // Set initial volumes
      await _backgroundPlayer.setVolume(_masterVolume);
      await _ambientPlayer.setVolume(_ambientVolume);
      await _effectPlayer.setVolume(_effectVolume);
      
      _isInitialized = true;
    } catch (e) {
      print('Failed to initialize enhanced audio: $e');
    }
  }

  /// Set current biome and update audio accordingly
  Future<void> setBiome(PlanetBiome biome) async {
    if (!_isEnabled || !_isInitialized) return;
    
    _currentBiome = biome;
    final config = _biomeAudioConfigs[biome];
    
    if (config != null) {
      // Crossfade to new biome background
      await _crossfadeBackground(config.backgroundTrack, duration: const Duration(seconds: 2));
      
      // Start biome-specific ambient sounds
      await _startBiomeAmbient(config);
      
      // Update frequency-based effects
      await _updateFrequencyEffects(config);
    }
  }

  /// Play biome-specific background music with crossfade
  Future<void> _crossfadeBackground(String newTrack, {Duration duration = const Duration(seconds: 2)}) async {
    try {
      // Fade out current track
      await _backgroundPlayer.setVolume(0.0);
      await Future.delayed(duration ~/ 2);
      
      // Load and start new track
      await _backgroundPlayer.play(AssetSource(newTrack));
      
      // Fade in new track
      await _backgroundPlayer.setVolume(_masterVolume);
    } catch (e) {
      print('Background crossfade failed: $e');
    }
  }

  /// Start biome-specific ambient sounds
  Future<void> _startBiomeAmbient(BiomeAudioConfig config) async {
    try {
      // Stop current ambient
      await _ambientPlayer.stop();
      
      // Select random ambient sound
      final ambientSound = config.ambientSounds[
        DateTime.now().millisecondsSinceEpoch % config.ambientSounds.length
      ];
      
      _currentAmbientTrack = ambientSound;
      await _ambientPlayer.play(AssetSource(ambientSound));
    } catch (e) {
      print('Ambient sound failed: $e');
    }
  }

  /// Update frequency-based audio effects
  Future<void> _updateFrequencyEffects(BiomeAudioConfig config) async {
    // This would integrate with advanced audio processing
    // For now, we'll use the base frequency for effect timing
    final baseDelay = (60000 / config.baseFrequency).round(); // ms
    
    // Schedule periodic effect updates
    Timer.periodic(Duration(milliseconds: baseDelay), (timer) {
      if (_currentBiome == null) {
        timer.cancel();
        return;
      }
      
      // Update ambient sound modulation based on biome
      _modulateAmbientSound(config);
    });
  }

  /// Modulate ambient sound based on biome state
  void _modulateAmbientSound(BiomeAudioConfig config) {
    // Placeholder for advanced audio modulation
    // This would adjust reverb, filters, etc. based on biome state
  }

  /// Play biome-specific trading effects
  Future<void> playTradingEffect({
    required bool isWin,
    required double profit,
    required double volume,
    PlanetBiome? biome,
  }) async {
    if (!_isEnabled || !_isInitialized) return;
    
    final targetBiome = biome ?? _currentBiome;
    if (targetBiome == null) return;
    
    final config = _biomeAudioConfigs[targetBiome];
    if (config == null) return;
    
    try {
      final effectKey = isWin ? 'win' : 'loss';
      final effectFile = config.effectSounds[effectKey];
      
      if (effectFile != null) {
        // Calculate effect intensity based on profit/volume
        final intensity = (profit.abs() / 1000).clamp(0.1, 1.0);
        final effectVolume = _effectVolume * intensity;
        
        await _effectPlayer.setVolume(effectVolume);
        await _effectPlayer.play(AssetSource(effectFile));
        
        // Add harmonic overlay based on profit direction
        if (profit != 0) {
          await _playHarmonicOverlay(
            frequency: config.baseFrequency,
            intensity: intensity,
            isPositive: profit > 0,
            scale: config.harmonicScale,
          );
        }
      }
    } catch (e) {
      print('Trading effect failed: $e');
    }
  }

  /// Play biome evolution effects
  Future<void> playBiomeEvolution(PlanetBiome newBiome) async {
    if (!_isEnabled || !_isInitialized) return;
    
    final config = _biomeAudioConfigs[newBiome];
    if (config == null) return;
    
    try {
      final evolutionFile = config.effectSounds['evolution'];
      if (evolutionFile != null) {
        await _effectPlayer.setVolume(_effectVolume);
        await _effectPlayer.play(AssetSource(evolutionFile));
        
        // Play ascending scale for evolution
        await _playEvolutionScale(config.baseFrequency);
      }
    } catch (e) {
      print('Biome evolution effect failed: $e');
    }
  }

  /// Play harmonic overlay based on trading outcome
  Future<void> _playHarmonicOverlay({
    required double frequency,
    required double intensity,
    required bool isPositive,
    required String scale,
  }) async {
    // This would generate harmonic frequencies based on the scale
    // For now, we'll use a simple frequency modulation
    final harmonicFreq = isPositive ? frequency * 1.5 : frequency * 0.75;
    final duration = Duration(milliseconds: (intensity * 1000).round());
    
    // Generate and play harmonic tone
    await _generateHarmonicTone(harmonicFreq, intensity, duration);
  }

  /// Play evolution scale
  Future<void> _playEvolutionScale(double baseFrequency) async {
    const notes = [1.0, 1.125, 1.25, 1.333, 1.5, 1.667, 1.875, 2.0]; // Major scale intervals
    
    for (final interval in notes) {
      final freq = baseFrequency * interval;
      await _generateHarmonicTone(freq, 0.5, const Duration(milliseconds: 200));
      await Future.delayed(const Duration(milliseconds: 100));
    }
  }

  /// Generate harmonic tone (placeholder for actual synthesis)
  Future<void> _generateHarmonicTone(double frequency, double intensity, Duration duration) async {
    // This would integrate with actual audio synthesis
    // For now, we'll use pre-generated harmonic sounds
    final toneFile = 'audio/harmonic_${frequency.round()}.mp3';
    
    try {
      await _effectPlayer.setVolume(_effectVolume * intensity);
      await _effectPlayer.play(AssetSource(toneFile));
    } catch (e) {
      // Fallback to generic tone
      await _effectPlayer.play(AssetSource('audio/generic_tone.mp3'));
    }
  }

  /// Play particle effects
  Future<void> playParticleEffect({
    required ParticleType type,
    required double intensity,
    PlanetBiome? biome,
  }) async {
    if (!_isEnabled || !_isInitialized) return;
    
    final targetBiome = biome ?? _currentBiome;
    if (targetBiome == null) return;
    
    try {
      final particleFile = _getParticleSoundFile(type, targetBiome);
      if (particleFile != null) {
        await _effectPlayer.setVolume(_effectVolume * intensity);
        await _effectPlayer.play(AssetSource(particleFile));
      }
    } catch (e) {
      print('Particle effect failed: $e');
    }
  }

  /// Get particle sound file based on type and biome
  String? _getParticleSoundFile(ParticleType type, PlanetBiome biome) {
    final basePath = 'audio/particles/${biome.name}/';
    
    switch (type) {
      case ParticleType.spark:
        return '${basePath}spark.mp3';
      case ParticleType.growth:
        return '${basePath}growth.mp3';
      case ParticleType.win:
        return '${basePath}success.mp3';
      case ParticleType.loss:
        return '${basePath}failure.mp3';
      case ParticleType.transformation:
        return '${basePath}transform.mp3';
      case ParticleType.active:
        return '${basePath}active.mp3';
      case ParticleType.lava:
        return '${basePath}lava.mp3';
      case ParticleType.crystal:
        return '${basePath}crystal.mp3';
      case ParticleType.enlightenment:
        return '${basePath}enlightenment.mp3';
    }
  }

  /// Adjust volume levels
  Future<void> setVolume({
    double? master,
    double? ambient,
    double? effects,
  }) async {
    if (master != null) {
      _masterVolume = master.clamp(0.0, 1.0);
      await _backgroundPlayer.setVolume(_masterVolume);
    }
    
    if (ambient != null) {
      _ambientVolume = ambient.clamp(0.0, 1.0);
      await _ambientPlayer.setVolume(_ambientVolume);
    }
    
    if (effects != null) {
      _effectVolume = effects.clamp(0.0, 1.0);
    }
  }

  /// Toggle audio on/off
  Future<void> toggleAudio() async {
    _isEnabled = !_isEnabled;
    
    if (_isEnabled) {
      await initialize();
      if (_currentBiome != null) {
        await setBiome(_currentBiome!);
      }
    } else {
      await _backgroundPlayer.stop();
      await _ambientPlayer.stop();
      await _effectPlayer.stop();
    }
  }

  /// Fade out all audio
  Future<void> fadeOutAll({Duration duration = const Duration(seconds: 1)}) async {
    try {
      await _backgroundPlayer.setVolume(0.0);
      await _ambientPlayer.setVolume(0.0);
      await _effectPlayer.setVolume(0.0);
      
      await Future.delayed(duration);
      
      await _backgroundPlayer.stop();
      await _ambientPlayer.stop();
      await _effectPlayer.stop();
    } catch (e) {
      print('Fade out failed: $e');
    }
  }

  /// Get current audio state
  bool get isEnabled => _isEnabled;
  bool get isInitialized => _isInitialized;
  double get masterVolume => _masterVolume;
  double get ambientVolume => _ambientVolume;
  double get effectVolume => _effectVolume;
  PlanetBiome? get currentBiome => _currentBiome;

  /// Dispose audio service
  Future<void> dispose() async {
    await _backgroundPlayer.dispose();
    await _ambientPlayer.dispose();
    await _effectPlayer.dispose();
    _ambientUpdateTimer?.cancel();
  }
}

/// Biome audio configuration
class BiomeAudioConfig {
  final String backgroundTrack;
  final List<String> ambientSounds;
  final Map<String, String> effectSounds;
  final double baseFrequency;
  final String harmonicScale;

  BiomeAudioConfig({
    required this.backgroundTrack,
    required this.ambientSounds,
    required this.effectSounds,
    required this.baseFrequency,
    required this.harmonicScale,
  });
}

/// Audio settings model
class AudioSettings {
  final bool isEnabled;
  final double masterVolume;
  final double ambientVolume;
  final double effectVolume;
  final bool backgroundMusic;
  final bool ambientSounds;
  final bool tradingEffects;
  final bool biomeEvolution;

  AudioSettings({
    this.isEnabled = true,
    this.masterVolume = 0.7,
    this.ambientVolume = 0.4,
    this.effectVolume = 0.8,
    this.backgroundMusic = true,
    this.ambientSounds = true,
    this.tradingEffects = true,
    this.biomeEvolution = true,
  });

  AudioSettings copyWith({
    bool? isEnabled,
    double? masterVolume,
    double? ambientVolume,
    double? effectVolume,
    bool? backgroundMusic,
    bool? ambientSounds,
    bool? tradingEffects,
    bool? biomeEvolution,
  }) {
    return AudioSettings(
      isEnabled: isEnabled ?? this.isEnabled,
      masterVolume: masterVolume ?? this.masterVolume,
      ambientVolume: ambientVolume ?? this.ambientVolume,
      effectVolume: effectVolume ?? this.effectVolume,
      backgroundMusic: backgroundMusic ?? this.backgroundMusic,
      ambientSounds: ambientSounds ?? this.ambientSounds,
      tradingEffects: tradingEffects ?? this.tradingEffects,
      biomeEvolution: biomeEvolution ?? this.biomeEvolution,
    );
  }
}