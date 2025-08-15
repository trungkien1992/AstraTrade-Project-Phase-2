import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/audio_service.dart';

/// Provider for AudioService instance
final audioServiceProvider = Provider<AudioService>((ref) {
  return AudioService();
});

/// Provider for audio enabled state
final audioEnabledProvider = StateProvider<bool>((ref) => true);

/// Provider for audio volume
final audioVolumeProvider = StateProvider<double>((ref) => 0.7);

/// Provider that manages audio settings
final audioSettingsProvider = Provider<AudioSettings>((ref) {
  final isEnabled = ref.watch(audioEnabledProvider);
  final volume = ref.watch(audioVolumeProvider);

  return AudioSettings(isEnabled: isEnabled, volume: volume);
});

/// Audio settings model
class AudioSettings {
  final bool isEnabled;
  final double volume;

  AudioSettings({required this.isEnabled, required this.volume});

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is AudioSettings &&
          runtimeType == other.runtimeType &&
          isEnabled == other.isEnabled &&
          volume == other.volume;

  @override
  int get hashCode => isEnabled.hashCode ^ volume.hashCode;
}

/// Notifier for managing audio state
class AudioNotifier extends StateNotifier<AudioSettings> {
  final AudioService _audioService;

  AudioNotifier(this._audioService)
    : super(AudioSettings(isEnabled: true, volume: 0.7)) {
    _audioService.initialize();
  }

  /// Toggle audio on/off
  void toggleAudio() {
    final newState = AudioSettings(
      isEnabled: !state.isEnabled,
      volume: state.volume,
    );
    state = newState;
    _audioService.setEnabled(newState.isEnabled);
  }

  /// Set audio volume
  void setVolume(double volume) {
    final newState = AudioSettings(
      isEnabled: state.isEnabled,
      volume: volume.clamp(0.0, 1.0),
    );
    state = newState;
    _audioService.setVolume(newState.volume);
  }

  /// Play cosmic sound with current settings
  Future<void> playSound(String soundType) async {
    if (state.isEnabled) {
      await _audioService.playCosmicSound(soundType);
    }
  }
}

/// Provider for audio notifier
final audioNotifierProvider =
    StateNotifierProvider<AudioNotifier, AudioSettings>((ref) {
      final audioService = ref.watch(audioServiceProvider);
      return AudioNotifier(audioService);
    });
