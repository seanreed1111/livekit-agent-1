"""Tests for MockTTS audio generation.

These tests verify that MockTTS correctly generates audio data in the format
expected by LiveKit Agents.
"""

import pytest

from adapters.mock_adapters import MockTTS


@pytest.mark.asyncio
async def test_mock_tts_generates_tone():
    """Test that MockTTS generates a tone with correct properties."""
    tts = MockTTS(audio_type="tone", sample_rate=24000, num_channels=1)

    # Synthesize some text
    stream = tts.synthesize("Hello world")

    # Collect all audio chunks
    chunks = []
    async for chunk in stream:
        chunks.append(chunk)

    # Verify we got at least one chunk
    assert len(chunks) > 0

    # Check first chunk properties
    first_chunk = chunks[0]
    assert first_chunk.delta_text == "Hello world"
    assert first_chunk.is_final is True
    assert first_chunk.request_id is not None

    # Check audio frame properties
    frame = first_chunk.frame
    assert frame.sample_rate == 24000
    assert frame.num_channels == 1
    assert frame.samples_per_channel > 0
    assert len(frame.data) > 0


@pytest.mark.asyncio
async def test_mock_tts_generates_beep():
    """Test that MockTTS generates a beep sequence."""
    tts = MockTTS(audio_type="beep", sample_rate=24000, num_channels=1)

    # Synthesize some text
    stream = tts.synthesize("Testing beep")

    # Collect all audio chunks
    chunks = []
    async for chunk in stream:
        chunks.append(chunk)

    # Verify we got audio
    assert len(chunks) > 0

    # Check audio frame
    frame = chunks[0].frame
    assert frame.sample_rate == 24000
    assert frame.num_channels == 1
    assert frame.samples_per_channel > 0


@pytest.mark.asyncio
async def test_mock_tts_different_sample_rates():
    """Test that MockTTS works with different sample rates."""
    for sample_rate in [16000, 24000, 48000]:
        tts = MockTTS(sample_rate=sample_rate)
        stream = tts.synthesize("Test")

        chunks = []
        async for chunk in stream:
            chunks.append(chunk)

        assert len(chunks) > 0
        assert chunks[0].frame.sample_rate == sample_rate


@pytest.mark.asyncio
async def test_mock_tts_stereo():
    """Test that MockTTS can generate stereo audio."""
    tts = MockTTS(num_channels=2)
    stream = tts.synthesize("Stereo test")

    chunks = []
    async for chunk in stream:
        chunks.append(chunk)

    assert len(chunks) > 0
    assert chunks[0].frame.num_channels == 2


@pytest.mark.asyncio
async def test_mock_tts_simulated_delay():
    """Test that MockTTS respects simulated delay."""
    import time

    tts = MockTTS(simulate_delay=0.1)
    stream = tts.synthesize("Delayed audio")

    start_time = time.time()
    chunks = []
    async for chunk in stream:
        chunks.append(chunk)
    elapsed = time.time() - start_time

    # Should have taken at least the simulated delay
    assert elapsed >= 0.1
    assert len(chunks) > 0


@pytest.mark.asyncio
async def test_mock_tts_call_count():
    """Test that MockTTS tracks the number of synthesize calls."""
    tts = MockTTS()

    assert tts._call_count == 0

    stream1 = tts.synthesize("First")
    async for _ in stream1:
        pass

    assert tts._call_count == 1

    stream2 = tts.synthesize("Second")
    async for _ in stream2:
        pass

    assert tts._call_count == 2


@pytest.mark.asyncio
async def test_mock_tts_context_manager():
    """Test that MockTTS works as an async context manager."""
    async with MockTTS() as tts:
        stream = tts.synthesize("Context test")
        chunks = []
        async for chunk in stream:
            chunks.append(chunk)

        assert len(chunks) > 0
