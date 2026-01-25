"""Tests for session handler.

This test suite verifies that SessionHandler correctly manages agent sessions,
including dependency injection, session configuration, and lifecycle management.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from livekit.agents import Agent, JobContext

from config import SessionConfig
from session_handler import SessionHandler


def test_session_handler_stores_dependencies():
    """Test SessionHandler stores all injected dependencies.

    Critical test: Ensures dependency injection works correctly and all
    components are stored for later use in handle_session.
    """
    # Arrange: Create mock dependencies
    mock_stt = MagicMock()
    mock_llm = MagicMock()
    mock_tts = MagicMock()
    mock_agent = MagicMock(spec=Agent)
    config = SessionConfig()

    # Act: Create SessionHandler
    handler = SessionHandler(
        stt=mock_stt,
        llm=mock_llm,
        tts=mock_tts,
        agent=mock_agent,
        session_config=config
    )

    # Assert: All dependencies stored
    assert handler.stt is mock_stt
    assert handler.llm is mock_llm
    assert handler.tts is mock_tts
    assert handler.agent is mock_agent
    assert handler.session_config is config


@pytest.mark.asyncio
async def test_session_handler_creates_agent_session():
    """Test handle_session creates AgentSession with correct components.

    Critical test: Ensures the core session creation logic uses injected
    components and configuration correctly.
    """
    # Arrange: Create handler with mock dependencies
    mock_stt = MagicMock()
    mock_llm = MagicMock()
    mock_tts = MagicMock()
    mock_agent = MagicMock(spec=Agent)
    config = SessionConfig(
        use_multilingual_turn_detector=True,
        preemptive_generation=True
    )

    handler = SessionHandler(
        stt=mock_stt,
        llm=mock_llm,
        tts=mock_tts,
        agent=mock_agent,
        session_config=config
    )

    # Create mock context
    mock_ctx = MagicMock(spec=JobContext)
    mock_ctx.room = MagicMock()
    mock_ctx.room.name = "test-room"
    mock_ctx.proc = MagicMock()
    mock_ctx.proc.userdata = {}
    mock_ctx.connect = AsyncMock()

    # Mock AgentSession and MultilingualModel
    with patch('session_handler.AgentSession') as MockAgentSession, \
         patch('session_handler.MultilingualModel') as MockMultilingualModel:
        mock_session = AsyncMock()
        MockAgentSession.return_value = mock_session
        mock_turn_detector = MagicMock()
        MockMultilingualModel.return_value = mock_turn_detector

        # Act: Handle session
        await handler.handle_session(mock_ctx)

        # Assert: AgentSession created with correct parameters
        MockAgentSession.assert_called_once()
        call_kwargs = MockAgentSession.call_args.kwargs

        assert call_kwargs['stt'] is mock_stt
        assert call_kwargs['llm'] is mock_llm
        assert call_kwargs['tts'] is mock_tts
        assert call_kwargs['preemptive_generation'] is True

        # Assert: Session started with agent and room
        mock_session.start.assert_called_once()
        start_kwargs = mock_session.start.call_args.kwargs
        assert start_kwargs['agent'] is mock_agent
        assert start_kwargs['room'] is mock_ctx.room


@pytest.mark.asyncio
async def test_session_handler_connects_to_room():
    """Test handle_session connects to room.

    Critical test: Ensures the session handler properly connects to the
    LiveKit room after session initialization.
    """
    # Arrange: Create handler
    mock_agent = MagicMock(spec=Agent)
    config = SessionConfig()
    handler = SessionHandler(
        stt=MagicMock(),
        llm=MagicMock(),
        tts=MagicMock(),
        agent=mock_agent,
        session_config=config
    )

    # Create mock context with spy on connect()
    mock_ctx = MagicMock(spec=JobContext)
    mock_ctx.room = MagicMock()
    mock_ctx.room.name = "test-room"
    mock_ctx.proc = MagicMock()
    mock_ctx.proc.userdata = {}
    mock_ctx.connect = AsyncMock()

    # Mock AgentSession and MultilingualModel
    with patch('session_handler.AgentSession') as MockAgentSession, \
         patch('session_handler.MultilingualModel') as MockMultilingualModel:
        mock_session = AsyncMock()
        MockAgentSession.return_value = mock_session
        MockMultilingualModel.return_value = MagicMock()

        # Act
        await handler.handle_session(mock_ctx)

        # Assert: connect() was called
        mock_ctx.connect.assert_called_once()


@pytest.mark.asyncio
async def test_session_handler_sends_greeting():
    """Test handle_session sends initial greeting.

    Critical test: Ensures users receive a greeting when joining, which is
    essential for good UX in voice assistants.
    """
    # Arrange: Create handler
    mock_agent = MagicMock(spec=Agent)
    config = SessionConfig()
    handler = SessionHandler(
        stt=MagicMock(),
        llm=MagicMock(),
        tts=MagicMock(),
        agent=mock_agent,
        session_config=config
    )

    # Create mock context
    mock_ctx = MagicMock(spec=JobContext)
    mock_ctx.room = MagicMock()
    mock_ctx.room.name = "test-room"
    mock_ctx.proc = MagicMock()
    mock_ctx.proc.userdata = {}
    mock_ctx.connect = AsyncMock()

    # Mock AgentSession and MultilingualModel
    with patch('session_handler.AgentSession') as MockAgentSession, \
         patch('session_handler.MultilingualModel') as MockMultilingualModel:
        mock_session = AsyncMock()
        MockAgentSession.return_value = mock_session
        MockMultilingualModel.return_value = MagicMock()

        # Act
        await handler.handle_session(mock_ctx)

        # Assert: Greeting sent
        mock_session.say.assert_called_once_with("Hello! How can I help you today?")
