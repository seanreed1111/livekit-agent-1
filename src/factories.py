"""Factory functions for creating voice pipeline components.

This project previously used protocols/adapters/mocks for STT/LLM/TTS. After
removing that layer, these factories still provide separation of concerns:
- `config.py` owns configuration
- `factories.py` owns object construction
- `agent.py` wires the app together

The returned objects are concrete LiveKit Inference implementations.
"""

from livekit.agents import inference
from loguru import logger

from config import PipelineConfig
from mock_llm import SimpleMockLLM


def create_stt(config: PipelineConfig) -> inference.STT:
    """Create an STT component from configuration."""
    logger.info(
        f"Creating STT with model: {config.stt_model}, lang: {config.stt_language}"
    )
    return inference.STT(model=config.stt_model, language=config.stt_language)


def create_llm(config: PipelineConfig) -> inference.LLM | SimpleMockLLM:
    """Create an LLM component from configuration."""
    logger.info(f"Creating LLM with model: {config.llm_model}")
    match config.llm_model:
        case "mock":
            return SimpleMockLLM()
        case _:
            return inference.LLM(model=config.llm_model)


def create_tts(config: PipelineConfig) -> inference.TTS:
    """Create a TTS component from configuration."""
    logger.info(
        f"Creating TTS with model: {config.tts_model}, voice: {config.tts_voice}"
    )
    return inference.TTS(model=config.tts_model, voice=config.tts_voice)
