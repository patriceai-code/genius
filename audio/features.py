"""
Acoustic Feature Extraction
Calculates physical sound attributes:
- Dominant spectral peak (Hz)
- Chirp pulse duration (ms)
- Periodic cadence interval (seconds)
"""

import numpy as np
from scipy import signal
from typing import Dict, Any, Tuple


def calculate_peak_frequency(samples: np.ndarray, sample_rate: int) -> float:
    """Finds the strongest frequency component in the audio signal using FFT."""
    if len(samples) == 0:
        return 0.0

    # Apply Hann window to reduce spectral leakage
    windowed = samples * np.hanning(len(samples))
    fft_magnitudes = np.abs(np.fft.rfft(windowed))
    frequencies = np.fft.rfftfreq(len(samples), d=1.0 / sample_rate)

    # Ignore frequencies below 400Hz (sub-bass/rumble)
    valid_indices = frequencies >= 400.0
    if not np.any(valid_indices):
        return 0.0

    peak_idx = np.argmax(fft_magnitudes[valid_indices])
    peak_freq = frequencies[valid_indices][peak_idx]
    return float(round(peak_freq, 1))


def calculate_pulse_duration(samples: np.ndarray, sample_rate: int, threshold_ratio: float = 0.20) -> float:
    """
    Measures the continuous pulse width in milliseconds using the Hilbert amplitude envelope
    to avoid oscillation zero-crossing dropouts.
    """
    if len(samples) == 0:
        return 0.0

    analytic_signal = signal.hilbert(samples)
    envelope = np.abs(analytic_signal)
    max_amp = np.max(envelope)
    if max_amp < 1e-4:
        return 0.0

    threshold = max_amp * threshold_ratio
    above_threshold = envelope > threshold

    active_indices = np.where(above_threshold)[0]
    if len(active_indices) == 0:
        return 0.0

    # Split into pulses by silence gap > 50ms
    gap_samples = int(sample_rate * 0.05)
    diffs = np.diff(active_indices)
    split_points = np.where(diffs > gap_samples)[0]

    if len(split_points) > 0:
        first_pulse_indices = active_indices[:split_points[0] + 1]
    else:
        first_pulse_indices = active_indices

    # Duration from first active index to last active index in first pulse
    duration_samples = first_pulse_indices[-1] - first_pulse_indices[0] + 1
    duration_ms = (duration_samples / sample_rate) * 1000.0
    return float(round(duration_ms, 1))


def calculate_cadence_interval(samples: np.ndarray, sample_rate: int) -> float:
    """
    Detects repeated sound pulses and computes the time interval (seconds)
    between successive pulse peaks.
    """
    if len(samples) < sample_rate * 0.5:
        return 0.0

    # Envelope detection using Hilbert transform or moving RMS
    analytic_signal = signal.hilbert(samples)
    amplitude_envelope = np.abs(analytic_signal)

    # Smooth the envelope
    kernel_size = int(sample_rate * 0.02)  # 20ms smoothing
    if kernel_size > 1:
        smoothed = np.convolve(amplitude_envelope, np.ones(kernel_size) / kernel_size, mode="same")
    else:
        smoothed = amplitude_envelope

    # Find peaks separated by at least 0.2s
    min_distance = int(sample_rate * 0.2)
    height_threshold = np.max(smoothed) * 0.3
    
    peaks, _ = signal.find_peaks(smoothed, distance=min_distance, height=height_threshold)

    if len(peaks) >= 2:
        intervals = np.diff(peaks) / sample_rate
        avg_interval = np.median(intervals)
        return float(round(avg_interval, 2))

    return 0.0


def extract_features_from_pcm(samples: np.ndarray, sample_rate: int = 16000) -> Dict[str, float]:
    """Extracts the complete acoustic feature triplet: (interval_s, peak_freq_hz, duration_ms)."""
    # Normalize
    max_val = np.max(np.abs(samples))
    if max_val > 0:
        samples = samples / max_val

    freq = calculate_peak_frequency(samples, sample_rate)
    duration = calculate_pulse_duration(samples, sample_rate)
    interval = calculate_cadence_interval(samples, sample_rate)

    return {
        "interval_s": interval,
        "peak_frequency_hz": freq,
        "pulse_duration_ms": duration,
    }
