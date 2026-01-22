"""Voice agent application with dependency injection.

This module contains the main application class and agent implementation,
refactored to use dependency injection for STT, LLM, and TTS components.
"""

import sys

from dotenv import load_dotenv
from livekit.agents import Agent, AgentServer, JobContext, JobProcess, cli
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


def download_files():
    """Download required model files (VAD, turn detector, etc.)."""
    print("Downloading Silero VAD model...")
    silero.VAD.load()
    print("✓ Silero VAD model downloaded")
    print(
        "\nNote: Multilingual turn detector will be downloaded automatically on first use "
        "(requires job context)"
    )
    print("\nAll models downloaded successfully!")


if __name__ == "__main__":
    # Simple CLI: check for download-files command
    if len(sys.argv) > 1 and sys.argv[1] == "download-files":
        download_files()
    else:
        # Default: start the voice assistant
        server = create_app()
        logger.info("Starting voice assistant application")
        cli.run_app(server)
