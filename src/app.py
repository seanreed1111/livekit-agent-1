"""Voice agent application with dependency injection.

This module contains the main application class and agent implementation,
refactored to use dependency injection for STT, LLM, and TTS components.
"""

from dotenv import load_dotenv
from livekit.agents import Agent, AgentServer, JobContext, JobProcess, cli
from livekit.plugins import silero
from loguru import logger

from config import AppConfig, PipelineConfig
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


def _prewarm(proc: JobProcess):
    """Module-level prewarm function for loading VAD model."""
    proc.userdata["vad"] = silero.VAD.load()


async def _handle_session(ctx: JobContext):
    """Module-level session handler."""
    # Initialize config and handler for this worker process
    config = AppConfig()

    # Create components
    stt = create_stt(config.pipeline)
    llm = create_llm(config.pipeline)
    tts = create_tts(config.pipeline)

    # Create agent
    agent = Assistant(instructions=config.agent.instructions)

    # Create session handler with injected dependencies
    session_handler = SessionHandler(
        stt=stt,
        llm=llm,
        tts=tts,
        agent=agent,
        session_config=config.session,
    )

    await session_handler.handle_session(ctx)


def create_app(config: AppConfig | None = None) -> AgentServer:
    """Create and configure the voice agent application.

    Args:
        config: Application configuration. If None, loads from environment.

    Returns:
        Configured AgentServer instance ready to run.
    """
    # Set up server
    server = AgentServer()
    server.setup_fnc = _prewarm
    server.rtc_session()(_handle_session)

    logger.info("Voice agent application initialized")

    return server


if __name__ == "__main__":
    config = AppConfig(
        pipeline=PipelineConfig(
            llm_model="mock",
            enable_keyword_intercept=True,
        )
    )
    server = create_app(config=config)
    logger.info("Starting voice agent application")
    cli.run_app(server)
