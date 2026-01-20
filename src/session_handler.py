"""Session handler for voice agent interactions.

This module contains the SessionHandler class that manages agent sessions
with dependency-injected STT, LLM, and TTS components.
"""

from livekit.agents import Agent, AgentSession, JobContext, room_io
from livekit.plugins import noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from loguru import logger

from config import SessionConfig
from protocols import LLMProtocol, STTProtocol, TTSProtocol


class SessionHandler:
    """Handles agent sessions with dependency-injected voice pipeline components.

    This class encapsulates the session handling logic and receives STT, LLM, and TTS
    components through constructor injection, enabling testability and flexibility.
    """

    def __init__(
        self,
        stt: STTProtocol,
        llm: LLMProtocol,
        tts: TTSProtocol,
        agent: Agent,
        session_config: SessionConfig,
    ):
        """Initialize the session handler.

        Args:
            stt: Speech-to-text adapter
            llm: Large language model adapter
            tts: Text-to-speech adapter
            agent: The agent instance to use for sessions
            session_config: Configuration for session management
        """
        self.stt = stt
        self.llm = llm
        self.tts = tts
        self.agent = agent
        self.session_config = session_config
        logger.info("SessionHandler initialized")

    def _unwrap_adapter(self, adapter):
        """Unwrap LiveKit adapters to get the underlying inference object.

        LiveKit adapters wrap the actual inference objects, but AgentSession
        expects the unwrapped objects. This method extracts the underlying
        object from LiveKit adapters while leaving mock adapters as-is.

        Args:
            adapter: An adapter object (LiveKit or mock)

        Returns:
            The underlying object for LiveKit adapters, or the adapter itself for mocks
        """
        # LiveKit adapters store the underlying object in _stt, _llm, or _tts
        # We check __dict__ directly to avoid triggering __getattr__ on mock adapters
        for attr in ("_stt", "_llm", "_tts"):
            if attr in adapter.__dict__:
                underlying = adapter.__dict__[attr]
                if underlying is not None:
                    return underlying
        # Mock adapters don't have underlying objects, return as-is
        return adapter

    async def handle_session(self, ctx: JobContext) -> None:
        """Handle an RTC session.

        Args:
            ctx: Job context containing room and connection information
        """
        # Logging setup
        ctx.log_context_fields = {
            "room": ctx.room.name,
        }

        logger.info(f"Starting session for room: {ctx.room.name}")

        # Unwrap adapters to get actual objects for AgentSession
        # LiveKit adapters wrap inference objects, but AgentSession needs the unwrapped versions
        stt = self._unwrap_adapter(self.stt)
        llm = self._unwrap_adapter(self.llm)
        tts = self._unwrap_adapter(self.tts)

        logger.debug(
            f"Using STT: {type(stt).__name__}, LLM: {type(llm).__name__}, TTS: {type(tts).__name__}"
        )

        # Set up the voice AI pipeline with injected components
        session = AgentSession(
            stt=stt,
            llm=llm,
            tts=tts,
            turn_detection=(
                MultilingualModel()
                if self.session_config.use_multilingual_turn_detector
                else None
            ),
            vad=ctx.proc.userdata.get("vad"),
            preemptive_generation=self.session_config.preemptive_generation,
        )

        # Configure room options
        room_options = room_io.RoomOptions()
        if self.session_config.enable_noise_cancellation:
            room_options = room_io.RoomOptions(
                audio_input=room_io.AudioInputOptions(
                    noise_cancellation=noise_cancellation.BVC(),
                ),
            )

        # Start the session
        await session.start(
            agent=self.agent,
            room=ctx.room,
            room_options=room_options,
        )

        logger.info("Session started, connecting to room")

        # Join the room and connect to the user
        await ctx.connect()

        logger.info("Connected to room successfully")
