"""Mock adapter implementations for STT, LLM, and TTS.

These adapters provide configurable mock implementations for testing and development.
They implement the same protocols as the LiveKit adapters but with controllable behavior.
"""

import asyncio
import uuid
from collections.abc import AsyncIterator
from typing import Any

from livekit.agents.tts import ChunkedStream, SynthesizedAudio
from loguru import logger

from adapters.audio_utils import generate_beep_sequence, generate_tone
from protocols import LLMProtocol, STTProtocol, TTSProtocol


class MockSTT:
    """Mock Speech-to-Text adapter.

    This adapter simulates STT behavior with configurable responses.
    Useful for testing and development without calling external services.
    """

    def __init__(
        self,
        transcriptions: list[str] | None = None,
        simulate_delay: float = 0.0,
    ):
        """Initialize the mock STT adapter.

        Args:
            transcriptions: List of transcriptions to return in sequence.
                           If None, returns empty transcriptions.
            simulate_delay: Simulated processing delay in seconds
        """
        self.transcriptions = transcriptions or []
        self.simulate_delay = simulate_delay
        self._call_count = 0
        logger.info("MockSTT initialized")

    def __getattr__(self, name: str) -> Any:
        """Handle attribute access for compatibility with LiveKit's STT interface."""
        logger.debug(f"MockSTT attribute accessed: {name}")
        return None

    async def __aenter__(self):
        """Support async context manager protocol."""
        logger.info("MockSTT context entered")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Support async context manager protocol."""
        logger.info("MockSTT context exited")
        return None


class MockLLM:
    """Mock Large Language Model adapter.

    This adapter simulates LLM behavior with configurable responses.
    Useful for testing and development without calling external LLM APIs.
    """

    def __init__(
        self,
        responses: list[str] | None = None,
        simulate_delay: float = 0.0,
    ):
        """Initialize the mock LLM adapter.

        Args:
            responses: List of responses to return in sequence.
                      If None, returns generic responses.
            simulate_delay: Simulated processing delay in seconds
        """
        self.responses = responses or [
            "I understand. How can I help you with that?",
            "That's interesting. Tell me more.",
            "I can assist with that.",
        ]
        self.simulate_delay = simulate_delay
        self._call_count = 0
        logger.info("MockLLM initialized with {} responses", len(self.responses))

    def __getattr__(self, name: str) -> Any:
        """Handle attribute access for compatibility with LiveKit's LLM interface."""
        logger.debug(f"MockLLM attribute accessed: {name}")
        return None

    async def __aenter__(self):
        """Support async context manager protocol."""
        logger.info("MockLLM context entered")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Support async context manager protocol."""
        logger.info("MockLLM context exited")
        return None


class MockChunkedStream:
    """Mock implementation of TTS ChunkedStream.

    This class simulates the behavior of a TTS ChunkedStream by yielding
    pre-generated audio data.
    """

    def __init__(
        self,
        text: str,
        audio_frame,
        simulate_delay: float = 0.0,
    ):
        """Initialize the mock chunked stream.

        Args:
            text: The input text being synthesized
            audio_frame: The audio frame to yield
            simulate_delay: Simulated streaming delay in seconds
        """
        self.input_text = text
        self._audio_frame = audio_frame
        self._simulate_delay = simulate_delay
        self._request_id = str(uuid.uuid4())
        self._done = False

    async def __aiter__(self) -> AsyncIterator[SynthesizedAudio]:
        """Async iterator that yields synthesized audio chunks."""
        if self._simulate_delay > 0:
            await asyncio.sleep(self._simulate_delay)

        # Yield a single audio chunk
        yield SynthesizedAudio(
            frame=self._audio_frame,
            request_id=self._request_id,
            is_final=True,
            segment_id="0",
            delta_text=self.input_text,
        )

        self._done = True

    async def aclose(self):
        """Close the stream."""
        self._done = True

    async def collect(self):
        """Collect all chunks into a single result."""
        chunks = []
        async for chunk in self:
            chunks.append(chunk)
        return chunks


class MockTTS:
    """Mock Text-to-Speech adapter.

    This adapter simulates TTS behavior with configurable audio generation.
    Useful for testing and development without calling external TTS services.
    """

    def __init__(
        self,
        simulate_delay: float = 0.0,
        voice: str = "mock-voice",
        sample_rate: int = 24000,
        num_channels: int = 1,
        audio_type: str = "tone",
    ):
        """Initialize the mock TTS adapter.

        Args:
            simulate_delay: Simulated audio generation delay in seconds
            voice: Voice identifier for logging purposes
            sample_rate: Audio sample rate in Hz (default: 24000)
            num_channels: Number of audio channels (default: 1 - mono)
            audio_type: Type of audio to generate: "tone", "beep", or "silence"
                       (default: "tone")
        """
        self.simulate_delay = simulate_delay
        self.voice = voice
        self.sample_rate = sample_rate
        self.num_channels = num_channels
        self.audio_type = audio_type
        self._call_count = 0
        logger.info(
            f"MockTTS initialized with voice: {voice}, "
            f"sample_rate: {sample_rate}Hz, audio_type: {audio_type}"
        )

    def synthesize(self, text: str) -> ChunkedStream:
        """Synthesize text to speech.

        Args:
            text: The text to synthesize

        Returns:
            ChunkedStream that yields synthesized audio
        """
        self._call_count += 1
        logger.info(f"MockTTS.synthesize called (count: {self._call_count}): {text}")

        # Generate audio based on configured type
        if self.audio_type == "beep":
            audio_frame = generate_beep_sequence(
                num_beeps=2,
                beep_duration=0.15,
                gap_duration=0.1,
                frequency=800.0,
                sample_rate=self.sample_rate,
                num_channels=self.num_channels,
            )
        else:
            # Default to simple tone
            # Duration roughly proportional to text length (0.05 seconds per character)
            duration = max(0.3, min(len(text) * 0.05, 3.0))
            audio_frame = generate_tone(
                frequency=440.0,
                duration=duration,
                sample_rate=self.sample_rate,
                num_channels=self.num_channels,
                amplitude=0.3,
            )

        # Return a mock chunked stream
        return MockChunkedStream(  # type: ignore
            text=text,
            audio_frame=audio_frame,
            simulate_delay=self.simulate_delay,
        )

    def __getattr__(self, name: str) -> Any:
        """Handle attribute access for compatibility with LiveKit's TTS interface."""
        logger.debug(f"MockTTS attribute accessed: {name}")
        return None

    async def __aenter__(self):
        """Support async context manager protocol."""
        logger.info("MockTTS context entered")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Support async context manager protocol."""
        logger.info("MockTTS context exited")
        return None


# Type checking: ensure mock adapters satisfy protocols
# Note: These type assertions verify protocol compliance at type-check time
if False:  # TYPE_CHECKING
    _: STTProtocol = MockSTT()  # type: ignore
    _: LLMProtocol = MockLLM()  # type: ignore
    _: TTSProtocol = MockTTS()  # type: ignore
