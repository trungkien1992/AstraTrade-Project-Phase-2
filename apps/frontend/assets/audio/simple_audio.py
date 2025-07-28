#!/usr/bin/env python3
"""
Simple cosmic audio generator for AstraTrade
Generates basic but effective space-themed sounds
"""

import numpy as np
import wave

def save_wav(filename, signal, sample_rate=44100):
    """Save signal as WAV file"""
    signal = np.clip(signal, -1, 1)
    signal_int = (signal * 32767).astype(np.int16)
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(signal_int.tobytes())

def generate_simple_tone(freq, duration, amplitude=0.5):
    """Generate a simple tone with fade in/out"""
    sample_rate = 44100
    frames = int(duration * sample_rate)
    t = np.linspace(0, duration, frames)
    
    # Generate tone
    signal = amplitude * np.sin(2 * np.pi * freq * t)
    
    # Add fade in/out
    fade_frames = min(frames // 10, 2205)  # 0.05s fade or 10% of duration
    signal[:fade_frames] *= np.linspace(0, 1, fade_frames)
    signal[-fade_frames:] *= np.linspace(1, 0, fade_frames)
    
    return signal

print("🎵 Generating simple cosmic audio files...")

# Harvest success - ascending chime
freqs = [523, 659, 784, 1047]  # C major chord
signal = np.array([])
for freq in freqs:
    tone = generate_simple_tone(freq, 0.3, 0.4)
    signal = np.concatenate([signal, tone])
save_wav('harvest_success.wav', signal)
print("✅ harvest_success.wav")

# Stardust generation - gentle hum
signal = generate_simple_tone(220, 2.0, 0.2)
save_wav('stardust_generation.wav', signal)
print("✅ stardust_generation.wav")

# Error - harsh beep
signal = generate_simple_tone(150, 0.5, 0.6)
save_wav('error.wav', signal)
print("✅ error.wav")

# Level up - ascending scale
freqs = [261, 329, 392, 523, 659]  # C major scale
signal = np.array([])
for freq in freqs:
    tone = generate_simple_tone(freq, 0.2, 0.5)
    signal = np.concatenate([signal, tone])
save_wav('level_up.wav', signal)
print("✅ level_up.wav")

# Trade execute - crisp beep
signal = generate_simple_tone(1000, 0.2, 0.6)
save_wav('trade_execute.wav', signal)
print("✅ trade_execute.wav")

# Forge activate - deep mysterious tone
signal = generate_simple_tone(65, 2.0, 0.4)
save_wav('forge_activate.wav', signal)
print("✅ forge_activate.wav")

# Background ambient - gentle drone
sample_rate = 44100
duration = 10.0  # 10 second loop
frames = int(duration * sample_rate)
t = np.linspace(0, duration, frames)

# Multiple frequency layers
signal = (0.1 * np.sin(2 * np.pi * 55 * t) +    # Low A
          0.05 * np.sin(2 * np.pi * 82.5 * t) +  # Low E
          0.03 * np.sin(2 * np.pi * 110 * t))    # A above

# Add gentle modulation
modulation = 1 + 0.1 * np.sin(2 * np.pi * 0.5 * t)
signal *= modulation

# Smooth loop
fade_frames = sample_rate // 2  # 0.5 second fade
signal[:fade_frames] *= np.linspace(0, 1, fade_frames)
signal[-fade_frames:] *= np.linspace(1, 0, fade_frames)

save_wav('background_ambient.wav', signal)
print("✅ background_ambient.wav")

# Cosmic Energy Channeling - mysterious harmonic sound
freqs = [220, 330, 440]  # Harmonic frequencies
signal = np.array([])
for freq in freqs:
    tone = generate_simple_tone(freq, 1.5, 0.3)
    signal = np.concatenate([signal, tone])
save_wav('cosmic_energy_channeling.wav', signal)
print("✅ cosmic_energy_channeling.wav")

# Quantum Tap Strong - sharp high tap
signal = generate_simple_tone(880, 0.1, 0.8)
save_wav('quantum_tap_strong.wav', signal)
print("✅ quantum_tap_strong.wav")

# Quantum Tap Light - gentle tap
signal = generate_simple_tone(440, 0.1, 0.4)
save_wav('quantum_tap_light.wav', signal)
print("✅ quantum_tap_light.wav")

# Astro Forger Upgrade - triumphant chord
freqs = [523, 659, 784]  # C major chord
signal = np.array([])
for freq in freqs:
    tone = generate_simple_tone(freq, 1.0, 0.4)
    if len(signal) == 0:
        signal = tone
    else:
        # Overlap the notes for chord effect
        min_len = min(len(signal), len(tone))
        signal[:min_len] += tone[:min_len]
        if len(tone) > len(signal):
            signal = np.concatenate([signal, tone[min_len:]])
save_wav('astro_forger_upgrade.wav', signal)
print("✅ astro_forger_upgrade.wav")

# Quantum Core Evolution - ascending magical scale
freqs = [261, 329, 392, 523]  # C major ascending
signal = np.array([])
for freq in freqs:
    tone = generate_simple_tone(freq, 0.8, 0.3)
    signal = np.concatenate([signal, tone])
save_wav('quantum_core_evolution.wav', signal)
print("✅ quantum_core_evolution.wav")

print("🎉 All audio files generated successfully!")