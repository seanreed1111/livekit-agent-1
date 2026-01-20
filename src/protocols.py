"""Protocol definitions for voice pipeline components.

These protocols define the interfaces that STT, LLM, and TTS implementations must follow,
enabling dependency injection and allowing different adapters (LiveKit, mock, etc.).
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class STTProtocol(Protocol):
    """Protocol for Speech-to-Text implementations.

    This protocol defines the interface that all STT adapters must implement
    to be compatible with the voice pipeline.
    """

    # STT implementations in LiveKit Agents are typically used as context managers
    # and passed directly to AgentSession. The actual interface is internal to LiveKit,
    # so we define a minimal protocol that allows type checking while maintaining
    # compatibility with livekit.agents.inference.STT


@runtime_checkable
class LLMProtocol(Protocol):
    """Protocol for Large Language Model implementations.

    This protocol defines the interface that all LLM adapters must implement
    to be compatible with the voice pipeline.
    """

    # LLM implementations in LiveKit Agents are typically used as context managers
    # and passed directly to AgentSession. The actual interface is internal to LiveKit,
    # so we define a minimal protocol that allows type checking while maintaining
    # compatibility with livekit.agents.inference.LLM


@runtime_checkable
class TTSProtocol(Protocol):
    """Protocol for Text-to-Speech implementations.

    This protocol defines the interface that all TTS adapters must implement
    to be compatible with the voice pipeline.
    """

    # TTS implementations in LiveKit Agents are typically used as context managers
    # and passed directly to AgentSession. The actual interface is internal to LiveKit,
    # so we define a minimal protocol that allows type checking while maintaining
    # compatibility with livekit.agents.inference.TTS
