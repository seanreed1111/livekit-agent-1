#!/usr/bin/env python3
"""Demo script for MockTTS audio generation.

This script demonstrates the audio generation capabilities of MockTTS by:
1. Generating different types of audio (tone, beep sequence)
2. Saving them as WAV files that can be played
3. Showing how MockTTS works in practice
"""

import asyncio

from adapters.mock_adapters import MockTTS


async def main():
    """Generate demo audio files from MockTTS."""
    print("=== MockTTS Audio Generation Demo ===\n")

    # Demo 1: Generate a simple tone
    print("1. Generating simple tone (440Hz, A4 note)...")
    tts_tone = MockTTS(audio_type="tone", sample_rate=24000)
    stream = tts_tone.synthesize("This is a test message")

    async for chunk in stream:
        frame = chunk.frame
        print(f"   Generated: {frame.samples_per_channel} samples")
        print(f"   Duration: {frame.duration:.2f} seconds")
        print(f"   Sample rate: {frame.sample_rate} Hz")
        print(f"   Channels: {frame.num_channels}")

        # Save to WAV file
        wav_bytes = frame.to_wav_bytes()
        with open("demo_tone.wav", "wb") as f:
            f.write(wav_bytes)
        print(f"   Saved to: demo_tone.wav ({len(wav_bytes)} bytes)\n")

    # Demo 2: Generate a beep sequence
    print("2. Generating beep sequence (800Hz, 2 beeps)...")
    tts_beep = MockTTS(audio_type="beep", sample_rate=24000)
    stream = tts_beep.synthesize("Beep beep!")

    async for chunk in stream:
        frame = chunk.frame
        print(f"   Generated: {frame.samples_per_channel} samples")
        print(f"   Duration: {frame.duration:.2f} seconds")
        print(f"   Sample rate: {frame.sample_rate} Hz")

        # Save to WAV file
        wav_bytes = frame.to_wav_bytes()
        with open("demo_beep.wav", "wb") as f:
            f.write(wav_bytes)
        print(f"   Saved to: demo_beep.wav ({len(wav_bytes)} bytes)\n")

    # Demo 3: Generate with simulated delay
    print("3. Generating with 0.5 second delay...")
    import time

    tts_delayed = MockTTS(audio_type="tone", simulate_delay=0.5)
    start = time.time()
    stream = tts_delayed.synthesize("Delayed audio")

    async for chunk in stream:
        elapsed = time.time() - start
        print(f"   Audio generated after {elapsed:.2f} seconds")
        print(f"   (Simulated streaming delay)\n")

    print("=== Demo Complete ===")
    print("You can play the generated WAV files:")
    print("  - demo_tone.wav: Simple 440Hz tone")
    print("  - demo_beep.wav: Sequence of 800Hz beeps")
    print("\nOn macOS, use: afplay demo_tone.wav")
    print("On Linux, use: aplay demo_tone.wav")
    print("On Windows, use: start demo_tone.wav")


if __name__ == "__main__":
    asyncio.run(main())
