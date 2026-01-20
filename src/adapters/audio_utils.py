"""Audio generation utilities for mock adapters.

This module provides utilities for generating synthetic audio data for testing,
including simple tones and beeps that can be used in MockTTS.
"""

import numpy as np
from livekit import rtc


def generate_tone(
    frequency: float = 440.0,
    duration: float = 0.5,
    sample_rate: int = 24000,
    num_channels: int = 1,
    amplitude: float = 0.3,
) -> rtc.AudioFrame:
    """Generate a simple sine wave tone as an AudioFrame.

    Args:
        frequency: Frequency of the tone in Hz (default: 440Hz - A4 note)
        duration: Duration of the tone in seconds
        sample_rate: Sample rate in Hz (default: 24000 - standard for TTS)
        num_channels: Number of audio channels (default: 1 - mono)
        amplitude: Amplitude of the tone, range 0.0 to 1.0 (default: 0.3)

    Returns:
        AudioFrame containing the generated tone
    """
    # Calculate number of samples
    samples_per_channel = int(sample_rate * duration)

    # Generate time array
    t = np.linspace(0, duration, samples_per_channel, endpoint=False)

    # Generate sine wave
    tone = amplitude * np.sin(2 * np.pi * frequency * t)

    # Convert to int16 format (required by LiveKit)
    # Scale to int16 range: [-32768, 32767]
    audio_int16 = (tone * 32767).astype(np.int16)

    # If stereo, duplicate the channel
    if num_channels == 2:
        audio_int16 = np.repeat(audio_int16, 2)

    # Create AudioFrame
    frame = rtc.AudioFrame.create(
        sample_rate=sample_rate,
        num_channels=num_channels,
        samples_per_channel=samples_per_channel,
    )

    # Copy audio data to frame
    # AudioFrame.data is a memoryview, convert our numpy array to bytes
    np.copyto(
        np.frombuffer(frame.data, dtype=np.int16).reshape(-1),
        audio_int16,
    )

    return frame


def generate_silence(
    duration: float = 0.5,
    sample_rate: int = 24000,
    num_channels: int = 1,
) -> rtc.AudioFrame:
    """Generate silence as an AudioFrame.

    Args:
        duration: Duration of silence in seconds
        sample_rate: Sample rate in Hz (default: 24000)
        num_channels: Number of audio channels (default: 1)

    Returns:
        AudioFrame containing silence
    """
    # Calculate number of samples
    samples_per_channel = int(sample_rate * duration)

    # Create AudioFrame (defaults to silence/zeros)
    frame = rtc.AudioFrame.create(
        sample_rate=sample_rate,
        num_channels=num_channels,
        samples_per_channel=samples_per_channel,
    )

    return frame


def generate_beep_sequence(
    num_beeps: int = 3,
    beep_duration: float = 0.1,
    gap_duration: float = 0.1,
    frequency: float = 800.0,
    sample_rate: int = 24000,
    num_channels: int = 1,
) -> rtc.AudioFrame:
    """Generate a sequence of beeps separated by silence.

    Args:
        num_beeps: Number of beeps to generate
        beep_duration: Duration of each beep in seconds
        gap_duration: Duration of gap between beeps in seconds
        frequency: Frequency of the beep in Hz
        sample_rate: Sample rate in Hz
        num_channels: Number of audio channels

    Returns:
        AudioFrame containing the beep sequence
    """
    segments = []

    for i in range(num_beeps):
        # Add beep
        beep = generate_tone(
            frequency=frequency,
            duration=beep_duration,
            sample_rate=sample_rate,
            num_channels=num_channels,
        )
        beep_data = np.frombuffer(beep.data, dtype=np.int16)
        segments.append(beep_data)

        # Add gap (except after last beep)
        if i < num_beeps - 1:
            gap = generate_silence(
                duration=gap_duration,
                sample_rate=sample_rate,
                num_channels=num_channels,
            )
            gap_data = np.frombuffer(gap.data, dtype=np.int16)
            segments.append(gap_data)

    # Concatenate all segments
    combined = np.concatenate(segments)
    samples_per_channel = len(combined) // num_channels

    # Create final AudioFrame
    frame = rtc.AudioFrame.create(
        sample_rate=sample_rate,
        num_channels=num_channels,
        samples_per_channel=samples_per_channel,
    )

    # Copy combined audio data
    np.copyto(
        np.frombuffer(frame.data, dtype=np.int16).reshape(-1),
        combined,
    )

    return frame
