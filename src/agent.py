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
from protocols import LLMProtocol, STTProtocol, TTSProtocol
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

    # To add tools, use the @function_tool decorator.
    # Here's an example that adds a simple weather tool.
    # You also have to add `from livekit.agents import function_tool, RunContext` to the top of this file
    # @function_tool
    # async def lookup_weather(self, context: RunContext, location: str):
    #     """Use this tool to look up current weather information in the given location.
    #
    #     If the location is not supported by the weather service, the tool will indicate this. You must tell the user the location's weather is unavailable.
    #
    #     Args:
    #         location: The location to look up weather information for (e.g. city name)
    #     """
    #
    #     logger.info(f"Looking up weather for {location}")
    #
    #     return "sunny with a temperature of 70 degrees."


class VoiceAgentApp:
    """Voice agent application with dependency injection.

    This class encapsulates the voice agent application and uses dependency injection
    to provide STT, LLM, and TTS components, enabling testability and flexibility.
    """

    def __init__(
        self,
        stt: STTProtocol | None = None,
        llm: LLMProtocol | None = None,
        tts: TTSProtocol | None = None,
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

        logger.info(
            "VoiceAgentApp initialized with adapter type: {}",
            self.config.pipeline.adapter_type,
        )

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
