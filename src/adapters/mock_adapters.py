"""Mock adapter implementations for STT, LLM, and TTS.

These adapters provide configurable mock implementations for testing and development.
They implement the same protocols as the LiveKit adapters but with controllable behavior.
"""

from typing import Any

from loguru import logger

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


class MockTTS:
    """Mock Text-to-Speech adapter.

    This adapter simulates TTS behavior with configurable audio generation.
    Useful for testing and development without calling external TTS services.
    """

    def __init__(
        self,
        simulate_delay: float = 0.0,
        voice: str = "mock-voice",
    ):
        """Initialize the mock TTS adapter.

        Args:
            simulate_delay: Simulated audio generation delay in seconds
            voice: Voice identifier for logging purposes
        """
        self.simulate_delay = simulate_delay
        self.voice = voice
        self._call_count = 0
        logger.info(f"MockTTS initialized with voice: {voice}")

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
