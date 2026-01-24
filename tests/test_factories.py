"""Tests for factory functions.

This test suite verifies that factory functions correctly create voice
pipeline components (STT, LLM, TTS) from configuration, including handling
of mock LLM and keyword interceptor wrapping.
"""

import pytest
from unittest.mock import patch, MagicMock
from livekit.agents import inference

from config import PipelineConfig
from factories import create_llm, create_stt, create_tts
from keyword_intercept_llm import KeywordInterceptLLM
from mock_llm import SimpleMockLLM


def test_create_llm_normal_model():
    """Test create_llm with normal model returns inference.LLM.

    Critical test: Ensures that standard OpenAI models are correctly
    instantiated as LiveKit inference.LLM instances.
    """
    # Arrange
    config = PipelineConfig(llm_model="openai/gpt-4.1-nano")

    # Act: Mock inference.LLM to avoid needing API keys
    with patch('factories.inference.LLM') as MockLLM:
        mock_llm_instance = MagicMock()
        MockLLM.return_value = mock_llm_instance

        llm = create_llm(config)

        # Assert
        MockLLM.assert_called_once_with(model="openai/gpt-4.1-nano")
        assert llm is mock_llm_instance


def test_create_llm_mock_model():
    """Test create_llm with 'mock' returns SimpleMockLLM.

    Critical test: Ensures the "mock" model selection creates a mock LLM
    for testing and development without API calls.
    """
    # Arrange
    config = PipelineConfig(llm_model="mock")

    # Act
    llm = create_llm(config)

    # Assert
    assert isinstance(llm, SimpleMockLLM)
    assert not isinstance(llm, KeywordInterceptLLM)


def test_create_llm_with_keyword_interceptor():
    """Test create_llm wraps with KeywordInterceptLLM when enabled.

    Critical test: Ensures the keyword interceptor wrapper is applied
    when enable_keyword_intercept is True, regardless of base LLM type.
    """
    # Arrange: Mock LLM with keyword interceptor enabled
    config = PipelineConfig(
        llm_model="mock",
        enable_keyword_intercept=True,
        intercept_keywords=["test", "example"],
        intercept_response="Intercepted response"
    )

    # Act
    llm = create_llm(config)

    # Assert: Should be wrapped in KeywordInterceptLLM
    assert isinstance(llm, KeywordInterceptLLM)
    assert llm._keywords == ["test", "example"]
    assert llm._response_text == "Intercepted response"

    # The wrapped LLM should be SimpleMockLLM
    assert isinstance(llm._wrapped_llm, SimpleMockLLM)


def test_create_llm_keyword_interceptor_with_real_llm():
    """Test keyword interceptor can wrap real LLM.

    Critical test: Ensures keyword interceptor works with real inference.LLM,
    not just mock LLM.
    """
    # Arrange: Real LLM with keyword interceptor enabled
    config = PipelineConfig(
        llm_model="openai/gpt-4.1-nano",
        enable_keyword_intercept=True,
        intercept_keywords=["fruit"],
        intercept_response="I don't like fruit"
    )

    # Act: Mock inference.LLM to avoid needing API keys
    with patch('factories.inference.LLM') as MockLLM:
        mock_llm_instance = MagicMock()
        MockLLM.return_value = mock_llm_instance

        llm = create_llm(config)

        # Assert: Should be wrapped in KeywordInterceptLLM
        assert isinstance(llm, KeywordInterceptLLM)
        assert llm._keywords == ["fruit"]

        # The wrapped LLM should be the mock instance
        assert llm._wrapped_llm is mock_llm_instance


def test_create_stt_with_config():
    """Test create_stt creates STT with correct model and language.

    Critical test: Ensures STT component is created with configuration
    parameters for speech recognition.
    """
    # Arrange
    config = PipelineConfig(
        stt_model="assemblyai/universal-streaming",
        stt_language="en"
    )

    # Act: Mock inference.STT to avoid needing API keys
    with patch('factories.inference.STT') as MockSTT:
        mock_stt_instance = MagicMock()
        MockSTT.return_value = mock_stt_instance

        stt = create_stt(config)

        # Assert
        MockSTT.assert_called_once_with(
            model="assemblyai/universal-streaming",
            language="en"
        )
        assert stt is mock_stt_instance


def test_create_tts_with_config():
    """Test create_tts creates TTS with correct model and voice.

    Critical test: Ensures TTS component is created with configuration
    parameters for speech synthesis.
    """
    # Arrange
    config = PipelineConfig(
        tts_model="inworld/inworld-tts-1",
        tts_voice="Ashley"
    )

    # Act: Mock inference.TTS to avoid needing API keys
    with patch('factories.inference.TTS') as MockTTS:
        mock_tts_instance = MagicMock()
        MockTTS.return_value = mock_tts_instance

        tts = create_tts(config)

        # Assert
        MockTTS.assert_called_once_with(
            model="inworld/inworld-tts-1",
            voice="Ashley"
        )
        assert tts is mock_tts_instance
