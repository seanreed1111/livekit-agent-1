"""Configuration models for the voice agent application.

Uses Pydantic v2 for type-safe configuration with environment variable support.
"""

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AgentConfig(BaseModel):
    """Configuration for the agent's behavior and personality."""

    instructions: str = Field(
        default="""You are a helpful voice AI assistant. The user is interacting with you via voice, even if you perceive the conversation as text.
You eagerly assist users with their questions by providing information from your extensive knowledge.
Your responses are concise, to the point, and without any complex formatting or punctuation including emojis, asterisks, or other symbols.
You are curious, friendly, and have a sense of humor.""",
        description="System instructions that define the agent's personality and behavior",
    )


class PipelineConfig(BaseModel):
    """Configuration for the voice pipeline components (STT, LLM, TTS)."""

    # STT configuration
    stt_model: str = Field(
        default="assemblyai/universal-streaming",
        description="Speech-to-text model identifier",
    )
    stt_language: str = Field(
        default="en",
        description="Language code for speech recognition",
    )

    # LLM configuration
    llm_model: str = Field(
        default="openai/gpt-4.1-nano",
        description="Large language model identifier",
    )

    # TTS configuration
    tts_model: str = Field(
        default="inworld/inworld-tts-1",
        description="Text-to-speech model identifier",
    )
    tts_voice: str = Field(
        default="Ashley",
        description="Voice identifier for text-to-speech",
    )

    # Keyword interception configuration
    enable_keyword_intercept: bool = Field(
        default=False,
        description="Enable keyword interception for LLM responses",
    )
    intercept_keywords: list[str] = Field(
        default_factory=lambda: ["cherries", "cherry", "banana", "apple", "fruit"],
        description="Keywords that trigger interception",
    )
    intercept_response: str = Field(
        default="I don't like fruit",
        description="Response to return when keywords are detected",
    )


class SessionConfig(BaseModel):
    """Configuration for session management and turn detection."""

    use_multilingual_turn_detector: bool = Field(
        default=True,
        description="Whether to use the multilingual turn detector",
    )
    preemptive_generation: bool = Field(
        default=True,
        description="Allow LLM to generate response while waiting for end of turn",
    )
    enable_noise_cancellation: bool = Field(
        default=True,
        description="Enable background voice cancellation",
    )


class DriveThruConfig(BaseModel):
    """Configuration for McDonald's drive-thru agent."""

    # Menu configuration
    menu_file_path: str = Field(
        default="menus/mcdonalds/transformed-data/menu-structure-2026-01-21.json",
        description="Path to menu JSON file",
    )

    # Order output
    orders_output_dir: str = Field(
        default="orders",
        description="Directory to save order files",
    )

    # Accuracy strategies
    fuzzy_match_threshold: int = Field(
        default=85,
        description="Minimum fuzzy match score (0-100) for item names",
        ge=0,
        le=100,
    )

    max_context_items: int = Field(
        default=50,
        description="Maximum number of menu items to inject into LLM context",
        ge=10,
        le=100,
    )

    # Feature flags
    enable_confirmation_loop: bool = Field(
        default=True,
        description="Require confirmation before adding items",
    )

    enable_semantic_search: bool = Field(
        default=False,
        description="Use embeddings for semantic item search (future)",
    )


class AppConfig(BaseSettings):
    """Top-level application configuration.

    This can be loaded from environment variables or .env files.
    """

    model_config = SettingsConfigDict(
        env_file=".env.local",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )

    agent: AgentConfig = Field(default_factory=AgentConfig)
    pipeline: PipelineConfig = Field(default_factory=PipelineConfig)
    session: SessionConfig = Field(default_factory=SessionConfig)
    drive_thru: DriveThruConfig = Field(
        default_factory=DriveThruConfig,
        description="Drive-thru agent configuration",
    )

    # LiveKit connection settings (from environment)
    livekit_url: str | None = Field(default=None, alias="LIVEKIT_URL")
    livekit_api_key: str | None = Field(default=None, alias="LIVEKIT_API_KEY")
    livekit_api_secret: str | None = Field(default=None, alias="LIVEKIT_API_SECRET")
