#!/usr/bin/env python3
"""
Generate royalty-free cosmic/space-themed audio files for AstraTrade
Uses procedural generation to create unique space sounds
"""

import numpy as np
import wave
import struct
import math

def generate_tone(frequency, duration, sample_rate=44100, amplitude=0.5):
    """Generate a pure tone"""
    frames = int(duration * sample_rate)
    return amplitude * np.sin(2 * np.pi * frequency * np.linspace(0, duration, frames))

def generate_chord(frequencies, duration, sample_rate=44100, amplitude=0.3):
    """Generate a chord from multiple frequencies"""
    frames = int(duration * sample_rate)
    t = np.linspace(0, duration, frames)
    signal = np.zeros(frames)
    
    for freq in frequencies:
        signal += amplitude * np.sin(2 * np.pi * freq * t)
    
    return signal / len(frequencies)

def add_envelope(signal, attack=0.1, decay=0.1, sustain=0.7, release=0.2):
    """Add ADSR envelope to signal"""
    length = len(signal)
    envelope = np.ones(length)
    
    # Attack
    attack_frames = int(attack * length)
    envelope[:attack_frames] = np.linspace(0, 1, attack_frames)
    
    # Decay
    decay_frames = int(decay * length)
    decay_start = attack_frames
    decay_end = decay_start + decay_frames
    envelope[decay_start:decay_end] = np.linspace(1, sustain, decay_frames)
    
    # Release
    release_frames = int(release * length)
    release_start = length - release_frames
    envelope[release_start:] = np.linspace(envelope[release_start], 0, release_frames)
    
    return signal * envelope

def add_reverb(signal, delay=0.1, decay=0.3, sample_rate=44100):
    """Add simple reverb effect"""
    delay_samples = int(delay * sample_rate)
    reverb_signal = np.concatenate([np.zeros(delay_samples), signal * decay])
    
    # Pad original signal to match reverb length
    padded_signal = np.concatenate([signal, np.zeros(delay_samples)])
    
    # Mix original and reverb
    min_length = min(len(padded_signal), len(reverb_signal))
    return (padded_signal[:min_length] + reverb_signal[:min_length]) / 2

def save_wav(filename, signal, sample_rate=44100):
    """Save signal as WAV file"""
    # Normalize to 16-bit range
    signal = np.clip(signal, -1, 1)
    signal_int = (signal * 32767).astype(np.int16)
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(signal_int.tobytes())

def generate_harvest_success():
    """Generate success sound - ascending cosmic chime"""
    # Ascending pentatonic scale for success
    frequencies = [523, 659, 784, 1047, 1319]  # C5, E5, G5, C6, E6
    duration = 1.5
    
    signal = np.array([])
    for i, freq in enumerate(frequencies):
        tone_duration = 0.3 - (i * 0.05)  # Shorter notes as we ascend
        tone = generate_tone(freq, tone_duration)
        tone = add_envelope(tone, attack=0.05, release=0.3)
        signal = np.concatenate([signal, tone])
    
    # Add cosmic reverb
    signal = add_reverb(signal, delay=0.15, decay=0.4)
    
    save_wav('harvest_success.wav', signal)
    print("✅ Generated harvest_success.wav")

def generate_stardust_generation():
    """Generate gentle ambient tone for idle generation"""
    # Soft, low-frequency hum with harmonics
    base_freq = 110  # A2
    harmonics = [base_freq, base_freq * 1.5, base_freq * 2, base_freq * 3]
    
    duration = 2.0
    signal = generate_chord(harmonics, duration, amplitude=0.2)
    
    # Add gentle modulation
    t = np.linspace(0, duration, len(signal))
    modulation = 1 + 0.1 * np.sin(2 * np.pi * 0.5 * t)  # 0.5 Hz modulation
    signal *= modulation
    
    signal = add_envelope(signal, attack=0.5, decay=0.2, sustain=0.6, release=0.3)
    signal = add_reverb(signal, delay=0.2, decay=0.3)
    
    save_wav('stardust_generation.wav', signal)
    print("✅ Generated stardust_generation.wav")

def generate_error():
    """Generate error sound - descending dissonant chord"""
    # Dissonant descending frequencies
    frequencies = [440, 415, 392, 370]  # Slightly detuned descending
    duration = 0.8
    
    signal = np.array([])
    for freq in frequencies:
        tone = generate_tone(freq, 0.2)
        tone = add_envelope(tone, attack=0.02, release=0.15)
        signal = np.concatenate([signal, tone])
    
    # Add slight distortion for harshness
    signal = np.tanh(signal * 2) * 0.5
    
    save_wav('error.wav', signal)
    print("✅ Generated error.wav")

def generate_level_up():
    """Generate triumphant level up sound"""
    # Major triad arpeggios
    frequencies = [261, 329, 392, 523, 659, 784, 1047]  # C major scale
    duration = 2.0
    
    signal = np.array([])
    for i, freq in enumerate(frequencies):
        tone = generate_tone(freq, 0.25)
        tone = add_envelope(tone, attack=0.05, release=0.2)
        signal = np.concatenate([signal, tone])
    
    # Add sparkle with high frequency harmonics
    sparkle = generate_tone(2093, 0.5, amplitude=0.1)  # High C
    sparkle = add_envelope(sparkle, attack=0.1, release=0.4)
    
    # Pad to match length and add sparkle
    min_length = min(len(signal), len(sparkle))
    if min_length > 0:
        signal[:min_length] = signal[:min_length] + sparkle[:min_length]
    signal = add_reverb(signal, delay=0.1, decay=0.5)
    
    save_wav('level_up.wav', signal)
    print("✅ Generated level_up.wav")

def generate_trade_execute():
    """Generate crisp trade execution sound"""
    # Quick, authoritative beep
    frequencies = [1000, 1200]  # High, clear tones
    
    signal = np.array([])
    for freq in frequencies:
        tone = generate_tone(freq, 0.15)
        tone = add_envelope(tone, attack=0.01, release=0.1)
        signal = np.concatenate([signal, tone])
    
    save_wav('trade_execute.wav', signal)
    print("✅ Generated trade_execute.wav")

def generate_forge_activate():
    """Generate mysterious forge activation sound"""
    # Deep, mystical bass tone with harmonics
    base_freq = 65  # C2
    duration = 3.0
    sample_rate = 44100
    
    # Generate each harmonic separately to avoid length issues
    frames = int(duration * sample_rate)
    signal = np.zeros(frames)
    
    harmonics = [base_freq, base_freq * 1.618, base_freq * 2.414]  # Golden ratio harmonics
    for freq in harmonics:
        tone = generate_tone(freq, duration, amplitude=0.1)
        if len(tone) == len(signal):
            signal += tone
    
    # Add mysterious wobble
    t = np.linspace(0, duration, len(signal))
    wobble = 1 + 0.2 * np.sin(2 * np.pi * 0.3 * t) * np.sin(2 * np.pi * 0.7 * t)
    signal *= wobble
    
    signal = add_envelope(signal, attack=0.8, decay=0.3, sustain=0.8, release=0.9)
    signal = add_reverb(signal, delay=0.3, decay=0.6)
    
    save_wav('forge_activate.wav', signal)
    print("✅ Generated forge_activate.wav")

def generate_background_ambient():
    """Generate ambient space background music"""
    duration = 30.0  # 30 seconds loop
    sample_rate = 44100
    
    # Multiple layers of ambient sound
    # Layer 1: Deep space drone
    drone_freq = 55  # A1
    drone = generate_tone(drone_freq, duration, amplitude=0.1)
    
    # Layer 2: Floating harmonics
    harmonics = [82.5, 110, 165, 220]  # Fifths and octaves
    harmonic_signal = np.zeros(int(duration * sample_rate))
    
    for i, freq in enumerate(harmonics):
        # Stagger the harmonics
        start_time = i * (duration / len(harmonics))
        tone_duration = duration - start_time
        
        if tone_duration > 0:
            tone = generate_tone(freq, tone_duration, amplitude=0.05)
            tone = add_envelope(tone, attack=0.3, decay=0.1, sustain=0.8, release=0.3)
            
            start_sample = int(start_time * sample_rate)
            end_sample = start_sample + len(tone)
            
            if end_sample <= len(harmonic_signal):
                harmonic_signal[start_sample:end_sample] += tone
    
    # Layer 3: Subtle cosmic wind
    wind_freq = 200
    wind = generate_tone(wind_freq, duration, amplitude=0.03)
    # Add random modulation for wind effect
    t = np.linspace(0, duration, len(wind))
    wind_modulation = 1 + 0.5 * np.sin(2 * np.pi * 0.1 * t) * np.sin(2 * np.pi * 0.13 * t)
    wind *= wind_modulation
    
    # Combine all layers
    signal = drone + harmonic_signal + wind
    signal = add_reverb(signal, delay=0.5, decay=0.4)
    
    # Ensure smooth loop
    fade_length = int(0.5 * sample_rate)  # 0.5 second fade
    signal[:fade_length] *= np.linspace(0, 1, fade_length)
    signal[-fade_length:] *= np.linspace(1, 0, fade_length)
    
    save_wav('background_ambient.wav', signal)
    print("✅ Generated background_ambient.wav (30s loop)")

def main():
    """Generate all audio files"""
    print("🎵 Generating royalty-free cosmic audio files for AstraTrade...")
    print("=" * 60)
    
    try:
        generate_harvest_success()
        generate_stardust_generation()
        generate_error()
        generate_level_up()
        generate_trade_execute()
        generate_forge_activate()
        generate_background_ambient()
        
        print("=" * 60)
        print("🎉 All audio files generated successfully!")
        print("📁 Files saved in current directory:")
        print("   - harvest_success.wav")
        print("   - stardust_generation.wav") 
        print("   - error.wav")
        print("   - level_up.wav")
        print("   - trade_execute.wav")
        print("   - forge_activate.wav")
        print("   - background_ambient.wav")
        print("")
        print("🚀 Ready for AstraTrade deployment!")
        
    except Exception as e:
        print(f"❌ Error generating audio: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())