"""Factory functions for creating voice pipeline component adapters.

These factories create the appropriate adapter implementations (LiveKit or mock)
based on configuration, enabling easy swapping between production and test implementations.
"""

from loguru import logger

from adapters.livekit_adapters import LiveKitLLM, LiveKitSTT, LiveKitTTS
from adapters.mock_adapters import MockLLM, MockSTT, MockTTS
from config import PipelineConfig
from protocols import LLMProtocol, STTProtocol, TTSProtocol


def create_stt(config: PipelineConfig) -> STTProtocol:
    """Create an STT adapter based on configuration.

    Args:
        config: Pipeline configuration specifying adapter type and settings

    Returns:
        STT adapter implementation (LiveKit or mock)
    """
    if config.adapter_type == "mock":
        logger.info("Creating mock STT adapter")
        return MockSTT()  # type: ignore

    logger.info(f"Creating LiveKit STT adapter with model: {config.stt_model}")
    return LiveKitSTT(config)  # type: ignore


def create_llm(config: PipelineConfig) -> LLMProtocol:
    """Create an LLM adapter based on configuration.

    Args:
        config: Pipeline configuration specifying adapter type and settings

    Returns:
        LLM adapter implementation (LiveKit or mock)
    """
    if config.adapter_type == "mock":
        logger.info("Creating mock LLM adapter")
        return MockLLM()  # type: ignore

    logger.info(f"Creating LiveKit LLM adapter with model: {config.llm_model}")
    return LiveKitLLM(config)  # type: ignore


def create_tts(config: PipelineConfig) -> TTSProtocol:
    """Create a TTS adapter based on configuration.

    Args:
        config: Pipeline configuration specifying adapter type and settings

    Returns:
        TTS adapter implementation (LiveKit or mock)
    """
    if config.adapter_type == "mock":
        logger.info("Creating mock TTS adapter")
        return MockTTS()  # type: ignore

    logger.info(
        f"Creating LiveKit TTS adapter with model: {config.tts_model}, voice: {config.tts_voice}"
    )
    return LiveKitTTS(config)  # type: ignore
