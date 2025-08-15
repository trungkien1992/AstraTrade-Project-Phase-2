import 'package:audioplayers/audioplayers.dart';
import 'package:flutter/foundation.dart';

/// Cosmic audio feedback service for trading activities
/// Provides satisfying audio cues for different cosmic events
class CosmicAudioService {
  static final _instance = CosmicAudioService._internal();
  factory CosmicAudioService() => _instance;
  CosmicAudioService._internal();

  final AudioPlayer _effectPlayer = AudioPlayer();

  bool _isInitialized = false;
  bool _isEnabled = true;
  double _volume = 0.6;

  /// Initialize the audio service
  static Future<void> initialize() async {
    final instance = CosmicAudioService();
    if (instance._isInitialized) return;

    try {
      await instance._effectPlayer.setVolume(instance._volume);
      instance._isInitialized = true;

      if (kDebugMode) {
        print('🎵 CosmicAudioService initialized successfully');
      }
    } catch (e) {
      if (kDebugMode) {
        print('⚠️ CosmicAudioService initialization failed: $e');
      }
      instance._isEnabled = false;
    }
  }

  /// Play success chime for profitable trades
  static Future<void> playSuccessChime() async {
    final instance = CosmicAudioService();
    if (!instance._isEnabled || !instance._isInitialized) return;

    try {
      // Use existing trade_execute.wav for success sound
      await instance._effectPlayer.play(AssetSource('audio/trade_execute.wav'));

      if (kDebugMode) {
        print('🎵 Playing cosmic success chime');
      }
    } catch (e) {
      if (kDebugMode) {
        print('⚠️ Failed to play success chime: $e');
      }
    }
  }

  /// Play attempt tone for trading attempts
  static Future<void> playAttemptTone() async {
    final instance = CosmicAudioService();
    if (!instance._isEnabled || !instance._isInitialized) return;

    try {
      // Use a softer version or different timing for attempts
      await instance._effectPlayer.stop(); // Stop any current sound
      await instance._effectPlayer.setVolume(instance._volume * 0.7); // Softer
      await instance._effectPlayer.play(AssetSource('audio/trade_execute.wav'));

      // Reset volume after playing
      Future.delayed(const Duration(milliseconds: 500), () {
        instance._effectPlayer.setVolume(instance._volume);
      });

      if (kDebugMode) {
        print('🎵 Playing cosmic attempt tone');
      }
    } catch (e) {
      if (kDebugMode) {
        print('⚠️ Failed to play attempt tone: $e');
      }
    }
  }

  /// Play level up fanfare
  static Future<void> playLevelUpFanfare() async {
    final instance = CosmicAudioService();
    if (!instance._isEnabled || !instance._isInitialized) return;

    try {
      // Use existing level_up.wav for level up sound
      await instance._effectPlayer.play(AssetSource('audio/level_up.wav'));

      if (kDebugMode) {
        print('🎵 Playing cosmic level up fanfare');
      }
    } catch (e) {
      if (kDebugMode) {
        print('⚠️ Failed to play level up fanfare: $e');
      }
    }
  }

  /// Play error sound for failed operations
  static Future<void> playErrorTone() async {
    final instance = CosmicAudioService();
    if (!instance._isEnabled || !instance._isInitialized) return;

    try {
      // Use existing error.wav for error sound
      await instance._effectPlayer.play(AssetSource('audio/error.wav'));

      if (kDebugMode) {
        print('🎵 Playing cosmic error tone');
      }
    } catch (e) {
      if (kDebugMode) {
        print('⚠️ Failed to play error tone: $e');
      }
    }
  }

  /// Play cosmic celebration for big wins or special events
  static Future<void> playCosmicCelebration() async {
    final instance = CosmicAudioService();
    if (!instance._isEnabled || !instance._isInitialized) return;

    try {
      // Enhanced level up sound for special celebrations
      await instance._effectPlayer.setVolume(instance._volume * 1.2); // Louder
      await instance._effectPlayer.play(AssetSource('audio/level_up.wav'));

      // Reset volume after playing
      Future.delayed(const Duration(milliseconds: 1000), () {
        instance._effectPlayer.setVolume(instance._volume);
      });

      if (kDebugMode) {
        print('🎵 Playing cosmic celebration');
      }
    } catch (e) {
      if (kDebugMode) {
        print('⚠️ Failed to play cosmic celebration: $e');
      }
    }
  }

  /// Enable or disable audio effects
  static void setEnabled(bool enabled) {
    final instance = CosmicAudioService();
    instance._isEnabled = enabled;

    if (kDebugMode) {
      print('🎵 Cosmic audio ${enabled ? 'enabled' : 'disabled'}');
    }
  }

  /// Set master volume (0.0 to 1.0)
  static void setVolume(double volume) {
    final instance = CosmicAudioService();
    instance._volume = volume.clamp(0.0, 1.0);
    instance._effectPlayer.setVolume(instance._volume);

    if (kDebugMode) {
      print('🎵 Cosmic audio volume set to ${instance._volume}');
    }
  }

  /// Get current enabled state
  static bool get isEnabled {
    return CosmicAudioService()._isEnabled;
  }

  /// Get current volume level
  static double get volume {
    return CosmicAudioService()._volume;
  }

  /// Dispose resources
  static Future<void> dispose() async {
    final instance = CosmicAudioService();
    try {
      await instance._effectPlayer.stop();
      await instance._effectPlayer.dispose();

      if (kDebugMode) {
        print('🎵 CosmicAudioService disposed');
      }
    } catch (e) {
      if (kDebugMode) {
        print('⚠️ Error disposing CosmicAudioService: $e');
      }
    }
  }
}
