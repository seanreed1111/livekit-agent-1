"""Session handler for voice agent interactions.

This module contains the SessionHandler class that manages agent sessions
with dependency-injected STT, LLM, and TTS components.
"""

from livekit.agents import NOT_GIVEN, Agent, AgentSession, JobContext, room_io
from livekit.plugins import noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from loguru import logger

from config import SessionConfig


class SessionHandler:
    """Handles agent sessions with dependency-injected voice pipeline components.

    This class encapsulates the session handling logic and receives STT, LLM, and TTS
    components through constructor injection, enabling testability and flexibility.
    """

    def __init__(
        self,
        stt,
        llm,
        tts,
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

        logger.debug(
            f"Using STT: {type(self.stt).__name__}, LLM: {type(self.llm).__name__}, TTS: {type(self.tts).__name__}"
        )

        # Set up the voice AI pipeline with injected components
        turn_detection = (
            MultilingualModel()
            if self.session_config.use_multilingual_turn_detector
            else NOT_GIVEN
        )
        vad = ctx.proc.userdata.get("vad") or NOT_GIVEN

        session = AgentSession(
            stt=self.stt,
            llm=self.llm,
            tts=self.tts,
            turn_detection=turn_detection,
            vad=vad,
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

        # Greet the user when they join
        await session.say("Hello! How can I help you today?")
