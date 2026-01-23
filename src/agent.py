"""McDonald's Drive-Thru Agent CLI.

This module provides the command-line interface for running the drive-thru agent
in various modes (console, dev, production).
"""

import asyncio
from uuid import uuid4

import click
from dotenv import load_dotenv
from livekit.agents import AgentServer, JobContext, JobProcess, cli
from livekit.agents.cli import AgentsConsole
from livekit.plugins import silero
from loguru import logger

from config import AppConfig
from session_handler import DriveThruSessionHandler

# Load environment variables
load_dotenv(".env.local")


def _prewarm(proc: JobProcess):
    """Module-level prewarm function for loading VAD model."""
    proc.userdata["vad"] = silero.VAD.load()


async def _handle_rtc_session(ctx: JobContext):
    """Module-level RTC session handler."""
    from livekit.agents import NOT_GIVEN, AgentSession, room_io
    from livekit.plugins import noise_cancellation
    from livekit.plugins.turn_detector.multilingual import MultilingualModel

    from factories import create_stt, create_tts

    # Initialize config and handler for this worker process
    config = AppConfig()
    handler = DriveThruSessionHandler(config)

    session_id = ctx.room.name

    logger.info(f"Starting drive-thru session for room: {session_id}")

    # Create drive-thru agent
    drive_thru_agent = await handler.create_agent(session_id)

    # Verify agent has tools registered
    logger.info(f"Agent has {len(drive_thru_agent.tools)} tools available")

    # Create voice pipeline components
    stt = create_stt(config.pipeline)
    tts = create_tts(config.pipeline)

    # Set up turn detection and VAD
    turn_detection = (
        MultilingualModel()
        if config.session.use_multilingual_turn_detector
        else NOT_GIVEN
    )
    vad = ctx.proc.userdata.get("vad") or NOT_GIVEN

    # Create AgentSession
    session = AgentSession(
        stt=stt,
        llm=drive_thru_agent.llm,
        tts=tts,
        turn_detection=turn_detection,
        vad=vad,
        preemptive_generation=config.session.preemptive_generation,
    )

    # Configure room options
    room_options = room_io.RoomOptions()
    if config.session.enable_noise_cancellation:
        room_options = room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=noise_cancellation.BVC(),
            ),
        )

    # Start the session
    await session.start(
        agent=drive_thru_agent,
        room=ctx.room,
        room_options=room_options,
    )

    logger.info("Session started, connecting to room")

    # Join the room
    await ctx.connect()

    logger.info("Connected to room successfully")

    # Greet the user
    await session.say("Welcome to McDonald's! What can I get for you today?")


@click.group()
def agent_cli():
    """McDonald's Drive-Thru Agent CLI."""
    pass


@agent_cli.command()
def console():
    """Run drive-thru agent in console mode (for testing).

    This mode allows you to interact with the agent directly in the terminal,
    which is useful for testing and debugging.
    """

    async def run_console():
        """Async console runner."""
        from livekit.agents import AgentSession, NOT_GIVEN

        from factories import create_stt, create_tts

        # Load configuration
        config = AppConfig()

        # Create session handler
        handler = DriveThruSessionHandler(config)

        # Create agent for console session
        session_id = str(uuid4())
        logger.info(f"Starting console session: {session_id}")

        drive_thru_agent = await handler.create_agent(session_id)

        # Verify agent has tools registered
        logger.info(f"Agent has {len(drive_thru_agent.tools)} tools available")

        # Create voice pipeline components
        stt = create_stt(config.pipeline)
        tts = create_tts(config.pipeline)

        # Create AgentSession with drive-thru LLM
        # Console mode doesn't support MultilingualModel (requires job context)
        turn_detection = NOT_GIVEN

        session = AgentSession(
            stt=stt,
            llm=drive_thru_agent.llm,  # Use the DriveThruLLM
            tts=tts,
            turn_detection=turn_detection,
            preemptive_generation=config.session.preemptive_generation,
        )

        # Start session with the agent
        await session.start(agent=drive_thru_agent)

        # Run console
        logger.info("Console ready. Start speaking to the agent.")
        console = AgentsConsole(session)
        await console.arun()

    # Run the async console
    asyncio.run(run_console())


@agent_cli.command()
def dev():
    """Run drive-thru agent in dev mode with LiveKit connection.

    This mode connects to LiveKit for testing with real voice interactions.
    """
    # Create server
    server = AgentServer()
    server.setup_fnc = _prewarm
    server.rtc_session()(_handle_rtc_session)

    logger.info("Starting drive-thru agent in dev mode")
    cli.run_app(server)


@agent_cli.command()
def start():
    """Run drive-thru agent in production mode.

    This is the production entry point for deployment.
    """
    # Create server
    server = AgentServer()
    server.setup_fnc = _prewarm
    server.rtc_session()(_handle_rtc_session)

    logger.info("Starting drive-thru agent in production mode")
    cli.run_app(server)


@agent_cli.command()
def download_files():
    """Download required model files (VAD, turn detector, etc.).

    Run this before your first session to download necessary models.
    """
    from livekit.plugins import silero

    click.echo("Downloading Silero VAD model...")
    silero.VAD.load()
    click.echo("✓ Silero VAD model downloaded")

    click.echo(
        "\nNote: Multilingual turn detector will be downloaded automatically on first use "
        "(requires job context)"
    )

    click.echo("\nAll models downloaded successfully!")


if __name__ == "__main__":
    agent_cli()
