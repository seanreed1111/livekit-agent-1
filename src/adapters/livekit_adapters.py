"""LiveKit adapter implementations for STT, LLM, and TTS.

These adapters wrap LiveKit Inference components and implement the protocol interfaces,
allowing them to be used in the voice pipeline with dependency injection.
"""

from livekit.agents import inference

from config import PipelineConfig
from protocols import LLMProtocol, STTProtocol, TTSProtocol


class LiveKitSTT:
    """LiveKit adapter for Speech-to-Text.

    This adapter wraps livekit.agents.inference.STT and implements STTProtocol.
    """

    def __init__(self, config: PipelineConfig):
        """Initialize the LiveKit STT adapter.

        Args:
            config: Pipeline configuration containing STT model and language settings
        """
        self._stt = inference.STT(
            model=config.stt_model,
            language=config.stt_language,
        )

    def __getattr__(self, name: str):
        """Delegate all attribute access to the underlying STT instance."""
        return getattr(self._stt, name)

    async def __aenter__(self):
        """Support async context manager protocol."""
        await self._stt.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Support async context manager protocol."""
        return await self._stt.__aexit__(exc_type, exc_val, exc_tb)


class LiveKitLLM:
    """LiveKit adapter for Large Language Models.

    This adapter wraps livekit.agents.inference.LLM and implements LLMProtocol.
    """

    def __init__(self, config: PipelineConfig):
        """Initialize the LiveKit LLM adapter.

        Args:
            config: Pipeline configuration containing LLM model settings
        """
        self._llm = inference.LLM(model=config.llm_model)

    def __getattr__(self, name: str):
        """Delegate all attribute access to the underlying LLM instance."""
        return getattr(self._llm, name)

    async def __aenter__(self):
        """Support async context manager protocol."""
        await self._llm.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Support async context manager protocol."""
        return await self._llm.__aexit__(exc_type, exc_val, exc_tb)


class LiveKitTTS:
    """LiveKit adapter for Text-to-Speech.

    This adapter wraps livekit.agents.inference.TTS and implements TTSProtocol.
    """

    def __init__(self, config: PipelineConfig):
        """Initialize the LiveKit TTS adapter.

        Args:
            config: Pipeline configuration containing TTS model and voice settings
        """
        self._tts = inference.TTS(
            model=config.tts_model,
            voice=config.tts_voice,
        )

    def __getattr__(self, name: str):
        """Delegate all attribute access to the underlying TTS instance."""
        return getattr(self._tts, name)

    async def __aenter__(self):
        """Support async context manager protocol."""
        await self._tts.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Support async context manager protocol."""
        return await self._tts.__aexit__(exc_type, exc_val, exc_tb)


# Type checking: ensure adapters satisfy protocols
# Note: These type assertions verify protocol compliance at type-check time
# but are not executed at runtime to avoid requiring API keys during import
if False:  # TYPE_CHECKING
    _: STTProtocol = LiveKitSTT(PipelineConfig())  # type: ignore
    _: LLMProtocol = LiveKitLLM(PipelineConfig())  # type: ignore
    _: TTSProtocol = LiveKitTTS(PipelineConfig())  # type: ignore
