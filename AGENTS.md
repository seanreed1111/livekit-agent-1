# AGENTS.md

This is a LiveKit Agents project. LiveKit Agents is a Python SDK for building voice AI agents. This project is intended to be used with LiveKit Cloud. See @README.md for more about the rest of the LiveKit ecosystem.

The following is a guide for working with this project.

## Project structure

This Python project uses the `uv` package manager. You should **always** use `uv` for all Python operations - installing dependencies, running scripts, running tests, and executing any Python commands.

All app-level code is in the `src/` directory. In general, simple agents can be constructed with a single `agent.py` file. Additional files can be added, but you must retain `agent.py` as the entrypoint (see the associated Dockerfile for how this is deployed).

Be sure to maintain code formatting. You can use the ruff formatter/linter as needed: `uv run ruff format` and `uv run ruff check`.

## Package Management with `uv`

**IMPORTANT:** This project uses `uv` as its package manager. You must **always** use `uv` commands instead of `pip` or bare `python` commands.

### Running Python Scripts

**Always use `uv run python` instead of just `python`:**

```bash
# ✓ Correct
uv run python script.py
uv run python -m module

# ✗ Wrong
python script.py
python3 script.py
```

The `uv run` prefix ensures the script runs in the correct virtual environment with all dependencies available. **Do not manually activate virtual environments** - `uv run` handles this automatically.

### Adding Dependencies

Use `uv add` to install new packages:

```bash
# Add a regular dependency
uv add package-name

# Add a dev dependency (for testing, linting, etc.)
uv add --dev package-name

# Add with version constraints
uv add "package-name>=1.0.0"
```

### Running Tests and Commands

Always prefix commands with `uv run`:

```bash
# Run tests
uv run pytest

# Run specific test file
uv run pytest tests/test_agent.py

# Run linting and formatting
uv run ruff check
uv run ruff format

# Run the agent
uv run python src/agent.py dev
```

### Syncing Dependencies

After pulling changes that modify `pyproject.toml`, sync dependencies:

```bash
uv sync
```

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

### Dependency Injection with Config + Factories (no custom adapters)

This codebase uses dependency injection (DI) while **constructing concrete LiveKit
components directly** (no `Protocol`/adapter/mocks layer).

The responsibilities are:

1. **Configuration**: `src/config.py` (Pydantic v2 models, env-driven)
2. **Construction**: `src/factories.py` (builds `livekit.agents.inference.STT/LLM/TTS`)
3. **Wiring**: `src/agent.py` (creates the app + server)
4. **Runtime behavior**: `src/session_handler.py` (creates `AgentSession` and runs it)

#### Current file structure

```
src/
├── agent.py            # App entrypoint + wiring
├── config.py           # Pydantic configuration models
├── factories.py        # Creates inference STT/LLM/TTS from config
├── session_handler.py  # Session orchestration (AgentSession)
└── adapters/
    ├── __init__.py
    └── audio_utils.py  # Shared audio helpers only
```

## LiveKit CLI

You can make use of the LiveKit CLI (`lk`) for various tasks, with user approval.


