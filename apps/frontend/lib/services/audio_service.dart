import 'package:audioplayers/audioplayers.dart';
import 'package:flutter/foundation.dart';

/// Service for managing game audio and sound effects
class AudioService {
  static final AudioService _instance = AudioService._internal();
  factory AudioService() => _instance;
  AudioService._internal();

  final AudioPlayer _audioPlayer = AudioPlayer();
  final AudioPlayer _backgroundPlayer = AudioPlayer();
  bool _isEnabled = true;
  double _volume = 0.7;
  bool _backgroundMusicEnabled = true;

  /// Initialize the audio service
  Future<void> initialize() async {
    try {
      await _audioPlayer.setVolume(_volume);
      await _backgroundPlayer.setVolume(
        _volume * 0.3,
      ); // Background music quieter
      debugPrint('AudioService initialized successfully');
    } catch (e) {
      debugPrint('Failed to initialize AudioService: $e');
    }
  }

  /// Enable or disable sound effects
  void setEnabled(bool enabled) {
    _isEnabled = enabled;
  }

  /// Set volume level (0.0 to 1.0)
  void setVolume(double volume) {
    _volume = volume.clamp(0.0, 1.0);
    _audioPlayer.setVolume(_volume);
  }

  /// Play cosmic sound effect
  Future<void> playCosmicSound(String soundType) async {
    if (!_isEnabled) return;

    try {
      // Since we don't have actual audio files, we'll create different tone patterns
      // In a real implementation, you would load actual audio files
      switch (soundType) {
        case 'harvest_success':
          await _playSuccessSound();
          break;
        case 'stardust_generation':
          await _playGenerationSound();
          break;
        case 'error':
          await _playErrorSound();
          break;
        case 'level_up':
          await _playLevelUpSound();
          break;
        case 'trade_execute':
          await _playTradeSound();
          break;
        case 'forge_activate':
          await _playForgeSound();
          break;
        default:
          debugPrint('Unknown sound type: $soundType');
      }
    } catch (e) {
      debugPrint('Failed to play sound $soundType: $e');
    }
  }

  /// Play success notification sound
  Future<void> _playSuccessSound() async {
    try {
      await _audioPlayer.play(AssetSource('audio/harvest_success.wav'));
      debugPrint('🎵 Playing cosmic harvest success sound');
    } catch (e) {
      debugPrint('Failed to play success sound: $e');
      await _playTone(frequency: 800, duration: 200); // Fallback
    }
  }

  /// Play generation/crafting sound
  Future<void> _playGenerationSound() async {
    try {
      await _audioPlayer.play(AssetSource('audio/stardust_generation.wav'));
      debugPrint('🎵 Playing cosmic stardust generation sound');
    } catch (e) {
      debugPrint('Failed to play generation sound: $e');
      await _playTone(frequency: 600, duration: 300); // Fallback
    }
  }

  /// Play error notification sound
  Future<void> _playErrorSound() async {
    try {
      await _audioPlayer.play(AssetSource('audio/error.wav'));
      debugPrint('🎵 Playing cosmic error sound');
    } catch (e) {
      debugPrint('Failed to play error sound: $e');
      await _playTone(frequency: 300, duration: 400); // Fallback
    }
  }

  /// Play level up celebration sound
  Future<void> _playLevelUpSound() async {
    try {
      await _audioPlayer.play(AssetSource('audio/level_up.wav'));
      debugPrint('🎵 Playing cosmic level up fanfare');
    } catch (e) {
      debugPrint('Failed to play level up sound: $e');
      await _playTone(frequency: 1000, duration: 150); // Fallback
      await Future.delayed(const Duration(milliseconds: 100));
      await _playTone(frequency: 1200, duration: 150);
    }
  }

  /// Play trading action sound
  Future<void> _playTradeSound() async {
    try {
      await _audioPlayer.play(AssetSource('audio/trade_execute.wav'));
      debugPrint('🎵 Playing cosmic trade execution sound');
    } catch (e) {
      debugPrint('Failed to play trade sound: $e');
      await _playTone(frequency: 700, duration: 250); // Fallback
    }
  }

  /// Play forge activation sound
  Future<void> _playForgeSound() async {
    try {
      await _audioPlayer.play(AssetSource('audio/forge_activate.wav'));
      debugPrint('🎵 Playing mystical forge activation sound');
    } catch (e) {
      debugPrint('Failed to play forge sound: $e');
      await _playTone(frequency: 500, duration: 350); // Fallback
    }
  }

  /// Play a simple tone (placeholder for actual audio files)
  Future<void> _playTone({
    required double frequency,
    required int duration,
  }) async {
    // This is a placeholder implementation
    // In a real app, you would use actual audio files
    try {
      // For web/mobile platforms that support it, you could generate tones
      // For now, we'll just log the sound
      debugPrint('🔊 Playing tone: ${frequency}Hz for ${duration}ms');

      // Simulate playing time
      await Future.delayed(Duration(milliseconds: duration));
    } catch (e) {
      debugPrint('Failed to play tone: $e');
    }
  }

  /// Start background ambient music
  Future<void> startBackgroundMusic() async {
    if (!_backgroundMusicEnabled) return;

    try {
      await _backgroundPlayer.setReleaseMode(ReleaseMode.loop);
      await _backgroundPlayer.play(AssetSource('audio/background_ambient.wav'));
      debugPrint('🎵 Started cosmic background music');
    } catch (e) {
      debugPrint('Failed to start background music: $e');
    }
  }

  /// Stop background ambient music
  Future<void> stopBackgroundMusic() async {
    try {
      await _backgroundPlayer.stop();
      debugPrint('🎵 Stopped background music');
    } catch (e) {
      debugPrint('Failed to stop background music: $e');
    }
  }

  /// Enable or disable background music
  void setBackgroundMusicEnabled(bool enabled) {
    _backgroundMusicEnabled = enabled;
    if (!enabled) {
      stopBackgroundMusic();
    } else {
      startBackgroundMusic();
    }
  }

  /// Dispose of audio resources
  void dispose() {
    _audioPlayer.dispose();
    _backgroundPlayer.dispose();
  }
}

/// Cosmic sound types for the game
enum CosmicSoundType {
  harvestSuccess('harvest_success'),
  stardustGeneration('stardust_generation'),
  error('error'),
  levelUp('level_up'),
  tradeExecute('trade_execute'),
  forgeActivate('forge_activate');

  const CosmicSoundType(this.value);
  final String value;
}

/// Extension for easy access to sound playing
extension CosmicSounds on AudioService {
  Future<void> playHarvestSuccess() =>
      playCosmicSound(CosmicSoundType.harvestSuccess.value);
  Future<void> playStardustGeneration() =>
      playCosmicSound(CosmicSoundType.stardustGeneration.value);
  Future<void> playError() => playCosmicSound(CosmicSoundType.error.value);
  Future<void> playLevelUp() => playCosmicSound(CosmicSoundType.levelUp.value);
  Future<void> playTradeExecute() =>
      playCosmicSound(CosmicSoundType.tradeExecute.value);
  Future<void> playForgeActivate() =>
      playCosmicSound(CosmicSoundType.forgeActivate.value);
}
