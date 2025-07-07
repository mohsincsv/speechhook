#!/usr/bin/env python3
"""
SpeechHook - Lean speech onset detection for voice agents
One class, one job: detect when user starts speaking during TTS playback
"""

import numpy as np
from typing import Optional
from scipy.fft import rfft
from collections import deque


class SpeechHook:
    """
    Detects speech onset in real-time audio streams.
    Optimized for Twilio media streams (8kHz mu-law) but supports PCM16.
    """
    
    def __init__(self, sample_rate: int = 8000, encoding: str = 'mulaw'):
        self.sample_rate = sample_rate
        self.encoding = encoding
        self.frame_size = int(sample_rate * 0.02)  # 20ms frames
        
        # Detection parameters
        self.onset_frames = 3  # Frames needed to confirm speech
        self.enter_threshold = 0.15  # Threshold above noise floor
        self.exit_threshold = 0.05   # Threshold to end speech
        
        # State
        self.is_speaking = False
        self.consecutive_speech = 0
        self.noise_history = deque(maxlen=50)  # 1 second of history
        self.prev_spectrum = None
        self.last_sample = 0.0
        
        # Mu-law decode table (precomputed for speed)
        self._mulaw_table = self._build_mulaw_table()
    
    def _build_mulaw_table(self) -> np.ndarray:
        """Precompute mu-law decode table"""
        table = np.zeros(256, dtype=np.float32)
        for i in range(256):
            ulaw = (~i) & 0xFF
            sign = -1 if (ulaw & 0x80) else 1
            magnitude = ((ulaw & 0x0F) << 3) + 0x84
            magnitude <<= (ulaw & 0x70) >> 4
            pcm16 = sign * (magnitude - 0x84)
            table[i] = pcm16 / 32768.0
        return table
    
    def _decode_audio(self, buffer: bytes) -> np.ndarray:
        """Decode audio buffer to float samples"""
        if self.encoding == 'mulaw':
            return self._mulaw_table[np.frombuffer(buffer, dtype=np.uint8)]
        elif self.encoding == 'pcm16':
            samples = np.frombuffer(buffer, dtype=np.int16)
            return samples.astype(np.float32) / 32768.0
        else:
            raise ValueError(f"Unsupported encoding: {self.encoding}")
    
    def _preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        """Apply pre-emphasis and windowing"""
        # Pre-emphasis filter: y[n] = x[n] - 0.95 * x[n-1]
        if len(frame) > 0:
            frame[0] -= 0.95 * self.last_sample
            for i in range(1, len(frame)):
                frame[i] -= 0.95 * frame[i-1]
            self.last_sample = frame[-1]
        
        # Hann window
        if len(frame) > 0:
            window = 0.5 * (1 - np.cos(2 * np.pi * np.arange(len(frame)) / (len(frame) - 1)))
            frame *= window
        
        return frame
    
    def _extract_features(self, frame: np.ndarray) -> float:
        """Extract speech activity score from audio frame"""
        if len(frame) < 16:  # Too short
            return 0.0
        
        # Compute power spectrum
        spectrum = np.abs(rfft(frame)) ** 2
        total_energy = np.sum(spectrum)
        
        if total_energy < 1e-10:  # Silence
            return 0.0
        
        # Feature 1: Speech band energy ratio (300-3400 Hz)
        freqs = np.fft.rfftfreq(len(frame), 1/self.sample_rate)
        speech_mask = (freqs >= 300) & (freqs <= 3400)
        speech_energy = np.sum(spectrum[speech_mask])
        energy_ratio = speech_energy / total_energy
        
        # Feature 2: Spectral flux (onset detection)
        flux = 0.0
        if self.prev_spectrum is not None:
            diff = spectrum - self.prev_spectrum
            flux = np.sum(diff[diff > 0])
        self.prev_spectrum = spectrum
        flux_norm = flux / (flux + 1.0)
        
        # Feature 3: Zero crossing rate
        zero_crossings = np.sum(np.diff(np.sign(frame)) != 0)
        zcr = zero_crossings / len(frame)
        
        # Combine features
        score = 0.6 * energy_ratio + 0.3 * flux_norm + 0.1 * min(1.0, zcr * 10)
        
        return score
    
    def process_audio(self, audio_buffer: bytes) -> bool:
        """
        Process audio buffer and detect speech onset.
        
        Args:
            audio_buffer: Raw audio data (mu-law bytes or PCM16)
            
        Returns:
            bool: True if speech onset detected, False otherwise
        """
        # Decode audio
        samples = self._decode_audio(audio_buffer)
        
        # Only process if we have enough samples for a frame
        if len(samples) < self.frame_size:
            return False
        
        # Take first frame (ignore extra samples)
        frame = samples[:self.frame_size]
        
        # Preprocess
        frame = self._preprocess_frame(frame.copy())
        
        # Extract features
        score = self._extract_features(frame)
        
        # Update noise floor (only with non-zero scores)
        if score > 0:
            self.noise_history.append(score)
        
        # Need some history before we can detect
        if len(self.noise_history) < 10:
            return False
        
        # Calculate adaptive threshold
        noise_floor = np.median(self.noise_history)
        
        # State machine logic
        if not self.is_speaking:
            # Check for speech start
            if score > noise_floor + self.enter_threshold:
                self.consecutive_speech += 1
                if self.consecutive_speech >= self.onset_frames:
                    self.is_speaking = True
                    return True  # Speech onset detected!
            else:
                self.consecutive_speech = 0
        else:
            # Check for speech end
            if score < noise_floor + self.exit_threshold:
                self.is_speaking = False
                self.consecutive_speech = 0
        
        return False
    
    def reset(self):
        """Reset detector state"""
        self.is_speaking = False
        self.consecutive_speech = 0
        self.noise_history.clear()
        self.prev_spectrum = None
        self.last_sample = 0.0


# Convenience functions for common audio formats
def create_telephony_hook() -> SpeechHook:
    """Create SpeechHook for telephony audio (8kHz mu-law)
    Works with: Twilio, Vonage, AWS Connect, any SIP provider"""
    return SpeechHook(sample_rate=8000, encoding='mulaw')


def create_hd_hook(sample_rate: int = 16000) -> SpeechHook:
    """Create SpeechHook for high-definition audio (PCM16)
    Works with: WebRTC, local microphones, high-quality streams"""
    return SpeechHook(sample_rate=sample_rate, encoding='pcm16')


def create_broadcast_hook() -> SpeechHook:
    """Create SpeechHook for broadcast quality (22kHz PCM16)
    Works with: Radio streams, podcast processing, media files"""
    return SpeechHook(sample_rate=22050, encoding='pcm16')
