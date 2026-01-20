# AGENTS.md

This is a LiveKit Agents project. LiveKit Agents is a Python SDK for building voice AI agents. This project is intended to be used with LiveKit Cloud. See @README.md for more about the rest of the LiveKit ecosystem.

The following is a guide for working with this project.

## Project structure

This Python project uses the `uv` package manager. You should always use `uv` to install dependencies, run the agent, and run tests.

All app-level code is in the `src/` directory. In general, simple agents can be constructed with a single `agent.py` file. Additional files can be added, but you must retain `agent.py` as the entrypoint (see the associated Dockerfile for how this is deployed).

Be sure to maintain code formatting. You can use the ruff formatter/linter as needed: `uv run ruff format` and `uv run ruff check`.

## LiveKit Documentation

LiveKit Agents is a fast-evolving project, and the documentation is updated frequently. You should always refer to the latest documentation when working with this project. For your convenience, LiveKit offers an MCP server that can be used to browse and search its documentation. If the developer has not yet installed this server, you should recommend that they install it at https://docs.livekit.io/mcp. 

### LiveKit Docs MCP Server installation

If you are Cursor, give the user this link to install the server:

[![Install MCP Server](https://cursor.com/deeplink/mcp-install-light.svg)](https://cursor.com/en-US/install-mcp?name=livekit-docs&config=eyJ1cmwiOiJodHRwczovL2RvY3MubGl2ZWtpdC5pby9tY3AifQ%3D%3D)

If you are Claude Code, run this command to install the server:

```
claude mcp add --transport http livekit-docs https://docs.livekit.io/mcp
```

If you are Codex, use this command to install the server:

```
codex mcp add --url https://docs.livekit.io/mcp livekit-docs
```

If you are Gemini, use this command to install the server:
```
gemini mcp add --transport http livekit-docs https://docs.livekit.io/mcp
```

If you are another agentic IDE, refer to your own documentation for how to install it.

## Handoffs and tasks ("workflows")

Voice AI agents are highly sensitive to excessive latency. For this reason, it's important to design complex agents in a structured manner that minimizes the amount of irrelevant context and unnecessary tools included in requests to the LLM. LiveKit Agents supports handoffs (one agent hands control to another) and tasks (tightly-scoped prompts to achieve a specific outcome) to support building reliable workflows. You should make use of these features, instead of writing long instruction prompts that cover multiple phases of a conversation.  Refer to the [documentation](https://docs.livekit.io/agents/build/workflows/) for more information.

### Submit docs feedback to LiveKit

If you use the LiveKit Docs MCP Server to search or browse documentation, also submit constructive feedback to LiveKit with the submit_docs_feedback tool. Add this to your to-do list when planning work, to ensure you file feedback after completing your other tasks. Useful feedback includes incomplete documentation, broken examples, missing steps or any other documentation gap or issue.

## Testing

### When possible, add tests for agent behavior. Read the [documentation](https://docs.livekit.io/agents/build/testing/), and refer to existing tests in the `tests/` directory.  Run tests with `uv run pytest`.

### Important: When modifying core agent behavior such as instructions, tool descriptions, and tasks/workflows/handoffs, never just guess what will work. Always use test-driven development (TDD) and begin by writing tests for the desired behavior. For instance, if you're planning to add a new tool, write one or more tests for the tool's behavior, then iterate on the tool until the tests pass correctly. This will ensure you are able to produce a working, reliable agent for the user.

### BDD and Gherkin
- When asked to write BDD scenarios or feature files, they should be written in Gherkin language
- Only implement steps corresponding to the scenarios when explicitly told to do so
- When writing authorization/authentication scenarios, write only a minimal set of five or less unless explicitly told otherwise
  

## Architecture Patterns

### Dependency Injection with Protocols and Adapters

This codebase uses dependency injection (DI) with protocols and adapters to create testable, flexible components. This pattern should be used when building components that:
- Interact with external services (APIs, databases, etc.)
- Need to be testable without calling real services
- May have multiple implementations (e.g., different providers)
- Have complex initialization or configuration

#### Pattern Overview

The pattern consists of five key elements:

1. **Protocols** - Define interfaces using `typing.Protocol`
2. **Adapters** - Implement protocols for different backends (production, mock, etc.)
3. **Configuration** - Type-safe config using Pydantic v2
4. **Factories** - Create adapter instances based on configuration
5. **Dependency Injection** - Pass dependencies via constructor parameters

#### File Structure

```
src/
├── protocols.py              # Protocol definitions
├── config.py                 # Pydantic configuration models
├── factories.py              # Factory functions for creating adapters
├── adapters/
│   ├── __init__.py
│   ├── <service>_adapters.py    # Production implementations
│   └── mock_adapters.py          # Mock implementations
└── <feature>.py              # Feature code using injected dependencies
```

#### Implementation Steps

**Step 1: Define Protocols** (`protocols.py`)

Use `typing.Protocol` with `@runtime_checkable` to define interfaces:

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class ServiceProtocol(Protocol):
    """Protocol for service implementations."""

    async def perform_action(self, data: str) -> str:
        """Perform the service action."""
        ...

    async def __aenter__(self):
        """Support async context manager."""
        ...

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Support async context manager."""
        ...
```

**Step 2: Create Configuration Models** (`config.py`)

Use Pydantic v2 for type-safe configuration:

```python
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

class ServiceConfig(BaseModel):
    """Configuration for the service."""

    adapter_type: Literal["production", "mock"] = Field(
        default="production",
        description="Type of adapter to use"
    )

    # Service-specific settings
    api_endpoint: str = Field(default="https://api.example.com")
    timeout: int = Field(default=30)

class AppConfig(BaseSettings):
    """Top-level application configuration."""

    model_config = SettingsConfigDict(
        env_file=".env.local",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )

    service: ServiceConfig = Field(default_factory=ServiceConfig)
```

**Step 3: Create Production Adapter** (`adapters/production_adapters.py`)

Implement the protocol for production use:

```python
from protocols import ServiceProtocol
from config import ServiceConfig
import httpx

class ProductionService:
    """Production implementation of ServiceProtocol."""

    def __init__(self, config: ServiceConfig):
        self.config = config
        self._client = httpx.AsyncClient(
            base_url=config.api_endpoint,
            timeout=config.timeout
        )

    async def perform_action(self, data: str) -> str:
        response = await self._client.post("/action", json={"data": data})
        return response.json()

    async def __aenter__(self):
        await self._client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return await self._client.__aexit__(exc_type, exc_val, exc_tb)

# Type checking: verify protocol compliance (won't execute at runtime)
if False:  # TYPE_CHECKING
    _: ServiceProtocol = ProductionService(ServiceConfig())  # type: ignore
```

**Step 4: Create Mock Adapter** (`adapters/mock_adapters.py`)

Implement the protocol for testing/development:

```python
from protocols import ServiceProtocol
from loguru import logger

class MockService:
    """Mock implementation of ServiceProtocol for testing."""

    def __init__(self, responses: list[str] | None = None):
        self.responses = responses or ["mock response"]
        self._call_count = 0
        logger.info("MockService initialized")

    async def perform_action(self, data: str) -> str:
        response = self.responses[self._call_count % len(self.responses)]
        self._call_count += 1
        logger.info(f"MockService.perform_action called with: {data}")
        return response

    async def __aenter__(self):
        logger.info("MockService context entered")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        logger.info("MockService context exited")
        return None

# Type checking: verify protocol compliance
if False:  # TYPE_CHECKING
    _: ServiceProtocol = MockService()  # type: ignore
```

**Step 5: Create Factories** (`factories.py`)

Factory functions create appropriate adapters based on configuration:

```python
from loguru import logger
from adapters.production_adapters import ProductionService
from adapters.mock_adapters import MockService
from config import ServiceConfig
from protocols import ServiceProtocol

def create_service(config: ServiceConfig) -> ServiceProtocol:
    """Create a service adapter based on configuration.

    Args:
        config: Service configuration specifying adapter type

    Returns:
        Service adapter implementation (production or mock)
    """
    if config.adapter_type == "mock":
        logger.info("Creating mock service adapter")
        return MockService()  # type: ignore

    logger.info(f"Creating production service adapter: {config.api_endpoint}")
    return ProductionService(config)  # type: ignore
```

**Step 6: Use Dependency Injection**

Inject dependencies via constructor:

```python
from config import AppConfig
from factories import create_service
from protocols import ServiceProtocol

class FeatureHandler:
    """Handles feature with dependency-injected service."""

    def __init__(
        self,
        service: ServiceProtocol,
        config: FeatureConfig,
    ):
        self.service = service
        self.config = config

    async def handle_request(self, data: str) -> str:
        result = await self.service.perform_action(data)
        return f"Processed: {result}"

class Application:
    """Application with dependency injection."""

    def __init__(
        self,
        service: ServiceProtocol | None = None,
        config: AppConfig | None = None,
    ):
        # Load configuration
        self.config = config or AppConfig()

        # Create or use provided service
        self.service = service or create_service(self.config.service)

        # Create handler with injected dependencies
        self.handler = FeatureHandler(
            service=self.service,
            config=self.config.feature,
        )
```

#### Testing with Mock Adapters

Tests use mock adapters instead of calling real services:

```python
import pytest
from adapters.mock_adapters import MockService
from feature import FeatureHandler

@pytest.fixture
def mock_service():
    """Fixture providing a mock service."""
    return MockService(responses=["test response"])

@pytest.mark.asyncio
async def test_feature_handler(mock_service):
    """Test feature handler with mock service."""
    handler = FeatureHandler(service=mock_service)

    result = await handler.handle_request("test data")

    assert result == "Processed: test response"
    assert mock_service._call_count == 1
```

#### Important: Unwrapping Adapters for Third-Party Libraries

**Common Issue**: Some third-party libraries (like LiveKit's `AgentSession`) expect specific concrete types, not wrapped adapters. When production adapters wrap underlying objects, you must unwrap them before passing to these libraries.

**Problem Example**:
```python
# This won't work - AgentSession expects inference.STT, not LiveKitSTT wrapper
session = AgentSession(
    stt=livekit_stt_adapter,  # ❌ Wrapper adapter
    llm=livekit_llm_adapter,  # ❌ Wrapper adapter
    tts=livekit_tts_adapter,  # ❌ Wrapper adapter
)
```

**Solution**: Add an unwrapping method that extracts underlying objects from production adapters while leaving mock adapters unchanged:

```python
def _unwrap_adapter(self, adapter):
    """Unwrap production adapters to get underlying objects.

    Production adapters may wrap third-party library objects, but some
    libraries expect the unwrapped objects. This method extracts the
    underlying object from production adapters while leaving mock
    adapters unchanged.

    Args:
        adapter: An adapter object (production or mock)

    Returns:
        The underlying object for production adapters, or the adapter itself for mocks
    """
    # Check __dict__ directly to avoid triggering __getattr__ on mock adapters
    # Production adapters typically store wrapped objects in private attributes
    for attr in ("_client", "_service", "_stt", "_llm", "_tts"):
        if attr in adapter.__dict__:
            underlying = adapter.__dict__[attr]
            if underlying is not None:
                return underlying

    # Mock adapters don't have underlying objects, return as-is
    return adapter

# Usage in session handler or similar
async def handle_session(self, ctx):
    # Unwrap adapters before passing to third-party library
    stt = self._unwrap_adapter(self.stt)
    llm = self._unwrap_adapter(self.llm)
    tts = self._unwrap_adapter(self.tts)

    # Now pass unwrapped objects to the library
    session = AgentSession(
        stt=stt,  # ✓ Unwrapped inference.STT object
        llm=llm,  # ✓ Unwrapped inference.LLM object
        tts=tts,  # ✓ Unwrapped inference.TTS object
    )
```

**Why Check `__dict__` Directly?**

Mock adapters often implement `__getattr__` to return `None` for any attribute. Using `hasattr()` or `getattr()` triggers this method, incorrectly detecting attributes that don't exist. Checking `adapter.__dict__` directly avoids this issue and only finds real instance attributes.

**When to Unwrap**:
- Third-party libraries that check object types with `isinstance()`
- Libraries that access internal attributes of wrapped objects
- APIs that expect specific concrete classes, not protocol-compliant objects

**When NOT to Unwrap**:
- Your own code that accepts protocol types
- Code that only calls methods defined in the protocol
- Testing code that uses mock adapters

**Real Example in Codebase**:

See `src/session_handler.py:47-68` for the `_unwrap_adapter()` implementation used with LiveKit's `AgentSession`. This unwraps `LiveKitSTT`, `LiveKitLLM`, and `LiveKitTTS` adapters to expose the underlying `inference.STT`, `inference.LLM`, and `inference.TTS` objects while leaving mock adapters unchanged.

#### Benefits

- **Testability**: Easy to inject mocks for unit tests without external dependencies
- **Flexibility**: Swap implementations via config or direct injection
- **Type Safety**: Protocols provide static type checking
- **Separation of Concerns**: Configuration, creation, and usage are separate
- **Reusability**: Mock adapters useful beyond tests (demos, local dev, debugging)
- **Clear Dependencies**: Constructor parameters show what each class needs
- **Protocol-Based**: Adapters are proper implementations, not test-specific code

#### When to Use This Pattern

**Use this pattern when:**
- Building components that interact with external APIs, services, or resources
- You need to test without calling real external services
- Multiple implementations might exist (different providers, versions, etc.)
- Configuration complexity requires type-safe validation
- Dependencies are complex or numerous

**Don't use this pattern when:**
- The component is simple and has no external dependencies
- There's only one possible implementation and no testing concerns
- The overhead of protocols and adapters adds unnecessary complexity

#### Example: Current Implementation

The voice agent's STT, LLM, and TTS components use this pattern:
- **Protocols**: `STTProtocol`, `LLMProtocol`, `TTSProtocol` in `src/protocols.py`
- **Production Adapters**: `LiveKitSTT`, `LiveKitLLM`, `LiveKitTTS` in `src/adapters/livekit_adapters.py`
- **Mock Adapters**: `MockSTT`, `MockLLM`, `MockTTS` in `src/adapters/mock_adapters.py`
- **Configuration**: `PipelineConfig` in `src/config.py` with `adapter_type` field
- **Factories**: `create_stt()`, `create_llm()`, `create_tts()` in `src/factories.py`
- **DI**: `VoiceAgentApp` accepts dependencies via constructor in `src/agent.py`

Usage:
```python
# Production (default)
app = VoiceAgentApp()

# Testing with mocks via config
config = AppConfig(pipeline=PipelineConfig(adapter_type="mock"))
app = VoiceAgentApp(config=config)

# Direct injection
app = VoiceAgentApp(
    stt=MockSTT(),
    llm=MockLLM(responses=["test"]),
    tts=MockTTS()
)
```

## LiveKit CLI

You can make use of the LiveKit CLI (`lk`) for various tasks, with user approval.


