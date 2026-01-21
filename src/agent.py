"""Voice agent application with dependency injection.

This module contains the main application class and agent implementation,
refactored to use dependency injection for STT, LLM, and TTS components.
"""

from dotenv import load_dotenv
from livekit.agents import Agent, AgentServer, JobProcess, cli
from livekit.plugins import silero
from loguru import logger

from config import AppConfig
from factories import create_llm, create_stt, create_tts
from session_handler import SessionHandler

load_dotenv(".env.local")


class Assistant(Agent):
    """The voice AI assistant agent."""

    def __init__(self, instructions: str | None = None) -> None:
        """Initialize the assistant.

        Args:
            instructions: System instructions for the agent. If None, uses default instructions.
        """
        default_instructions = """You are a helpful voice AI assistant. The user is interacting with you via voice, even if you perceive the conversation as text.
You eagerly assist users with their questions by providing information from your extensive knowledge.
Your responses are concise, to the point, and without any complex formatting or punctuation including emojis, asterisks, or other symbols.
You are curious, friendly, and have a sense of humor."""

        super().__init__(
            instructions=instructions or default_instructions,
        )


class VoiceAgentApp:
    """Voice agent application with dependency injection.

    This class encapsulates the voice agent application and uses dependency injection
    to provide STT, LLM, and TTS components, enabling testability and flexibility.
    """

    def __init__(
        self,
        stt=None,
        llm=None,
        tts=None,
        config: AppConfig | None = None,
    ):
        """Initialize the voice agent application.

        Args:
            stt: Speech-to-text adapter. If None, creates from config.
            llm: Large language model adapter. If None, creates from config.
            tts: Text-to-speech adapter. If None, creates from config.
            config: Application configuration. If None, loads from environment.
        """
        # Load configuration
        self.config = config or AppConfig()

        # Create or use provided adapters
        self.stt = stt or create_stt(self.config.pipeline)
        self.llm = llm or create_llm(self.config.pipeline)
        self.tts = tts or create_tts(self.config.pipeline)

        # Create agent
        self.agent = Assistant(instructions=self.config.agent.instructions)

        # Create session handler with injected dependencies
        self.session_handler = SessionHandler(
            stt=self.stt,
            llm=self.llm,
            tts=self.tts,
            agent=self.agent,
            session_config=self.config.session,
        )

        # Set up server
        self.server = AgentServer()
        self._setup_server()

        logger.info("VoiceAgentApp initialized")

    def _setup_server(self):
        """Configure the server with prewarm and session handler."""
        self.server.setup_fnc = self._prewarm
        self.server.rtc_session()(self.session_handler.handle_session)

    @staticmethod
    def _prewarm(proc: JobProcess):
        """Prewarm function for loading VAD model."""
        proc.userdata["vad"] = silero.VAD.load()

    def run(self):
        """Run the application."""
        logger.info("Starting voice agent application")
        cli.run_app(self.server)


if __name__ == "__main__":
    app = VoiceAgentApp()
    app.run()
