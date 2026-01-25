"""Tests for configuration models.

This test suite verifies that the Pydantic configuration models correctly
load from environment variables, handle nested configuration, and use
appropriate defaults.
"""

import pytest
from pathlib import Path

from config import AppConfig, PipelineConfig, SessionConfig, AgentConfig


def test_appconfig_loads_from_env_local(tmp_path, monkeypatch):
    """Test that AppConfig loads from .env.local file.

    Critical test: Ensures configuration can be loaded from environment
    files, which is the primary configuration mechanism for production.
    """
    # Arrange: Clear any existing environment variables
    for var in ["LIVEKIT_URL", "LIVEKIT_API_KEY", "LIVEKIT_API_SECRET"]:
        monkeypatch.delenv(var, raising=False)

    # Create .env.local with valid credentials
    env_file = tmp_path / ".env.local"
    env_file.write_text("""LIVEKIT_URL=wss://test.livekit.cloud
LIVEKIT_API_KEY=test_key
LIVEKIT_API_SECRET=test_secret
""")
    monkeypatch.chdir(tmp_path)

    # Act: Initialize AppConfig
    config = AppConfig()

    # Assert: All fields populated correctly
    assert config.livekit_url == "wss://test.livekit.cloud"
    assert config.livekit_api_key == "test_key"
    assert config.livekit_api_secret == "test_secret"


def test_appconfig_nested_delimiter(tmp_path, monkeypatch):
    """Test that __ delimiter works for nested config.

    Critical test: The __ delimiter allows setting nested configuration
    via environment variables (e.g., PIPELINE__LLM_MODEL sets
    config.pipeline.llm_model).
    """
    # Arrange: Clear any existing environment variables
    for var in ["LIVEKIT_URL", "LIVEKIT_API_KEY", "LIVEKIT_API_SECRET",
                "PIPELINE__LLM_MODEL", "PIPELINE__TTS_VOICE",
                "SESSION__PREEMPTIVE_GENERATION"]:
        monkeypatch.delenv(var, raising=False)

    # Create .env with nested config
    env_file = tmp_path / ".env.local"
    env_file.write_text("""PIPELINE__LLM_MODEL=openai/gpt-4o
PIPELINE__TTS_VOICE=Nova
SESSION__PREEMPTIVE_GENERATION=false
""")
    monkeypatch.chdir(tmp_path)

    # Act: Initialize AppConfig
    config = AppConfig()

    # Assert: Nested config parsed correctly
    assert config.pipeline.llm_model == "openai/gpt-4o"
    assert config.pipeline.tts_voice == "Nova"
    assert config.session.preemptive_generation is False


def test_appconfig_uses_defaults(tmp_path, monkeypatch):
    """Test that AppConfig uses default values when env not set.

    Critical test: Ensures sensible defaults are used when environment
    variables are not provided, allowing the application to start with
    minimal configuration.
    """
    # Arrange: Clear any existing environment variables
    for var in ["LIVEKIT_URL", "LIVEKIT_API_KEY", "LIVEKIT_API_SECRET",
                "PIPELINE__LLM_MODEL", "PIPELINE__STT_MODEL", "PIPELINE__TTS_MODEL",
                "PIPELINE__TTS_VOICE", "SESSION__USE_MULTILINGUAL_TURN_DETECTOR",
                "SESSION__PREEMPTIVE_GENERATION", "SESSION__ENABLE_NOISE_CANCELLATION"]:
        monkeypatch.delenv(var, raising=False)

    # Empty .env.local (no custom config)
    env_file = tmp_path / ".env.local"
    env_file.write_text("")
    monkeypatch.chdir(tmp_path)

    # Act: Initialize AppConfig
    config = AppConfig()

    # Assert: Default values used
    assert config.pipeline.llm_model == "openai/gpt-4.1-nano"
    assert config.pipeline.stt_model == "assemblyai/universal-streaming"
    assert config.pipeline.tts_model == "inworld/inworld-tts-1"
    assert config.pipeline.tts_voice == "Ashley"
    assert config.session.use_multilingual_turn_detector is True
    assert config.session.preemptive_generation is True
    assert config.session.enable_noise_cancellation is True

    # LiveKit credentials default to None (must be provided)
    assert config.livekit_url is None
    assert config.livekit_api_key is None
    assert config.livekit_api_secret is None
