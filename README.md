<a href="https://livekit.io/">
  <img src="./.github/assets/livekit-mark.png" alt="LiveKit logo" width="100" height="100">
</a>

# Generic Voice AI Assistant

A simple, general-purpose voice AI assistant built with [LiveKit Agents for Python](https://github.com/livekit/agents) and [LiveKit Cloud](https://cloud.livekit.io/). This assistant can answer questions, provide information, and maintain natural conversations on any topic.

## Table of Contents

- [Generic Voice AI Assistant](#generic-voice-ai-assistant)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Quick Start](#quick-start)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [Environment Setup](#environment-setup)
    - [Download Model Files](#download-model-files)
    - [Running the Assistant](#running-the-assistant)
  - [What It Does](#what-it-does)
  - [Development](#development)
    - [Project Structure](#project-structure)
    - [Testing](#testing)
    - [Code Formatting](#code-formatting)
    - [Using the Makefile](#using-the-makefile)
    - [Plan Review Command](#plan-review-command)
  - [Architecture](#architecture)
    - [Dependency Injection](#dependency-injection)
    - [Pydantic Models](#pydantic-models)
  - [Frontend \& Deployment](#frontend--deployment)
    - [Frontend Options](#frontend-options)
    - [Production Deployment](#production-deployment)
  - [Coding Agents and MCP](#coding-agents-and-mcp)
  - [License](#license)

## Overview

This repository demonstrates how to build a voice AI assistant using LiveKit Agents. The assistant uses:

- **Speech-to-Text (STT)** - AssemblyAI for voice recognition
- **Large Language Model (LLM)** - OpenAI GPT-4 for natural language understanding
- **Text-to-Speech (TTS)** - Cartesia for natural-sounding voice responses

The application is built with a clean architecture using dependency injection and Pydantic v2 models for configuration and data validation.

## Quick Start

### Prerequisites

- Python 3.11 or later
- [uv](https://docs.astral.sh/uv/) package manager
- [LiveKit Cloud](https://cloud.livekit.io/) account (free tier available)
- API keys for:
  - OpenAI (for LLM)
  - AssemblyAI (for STT)
  - Cartesia (for TTS)

### Installation

Clone the repository and install dependencies:

```bash
git clone <repository-url>
cd lk-agent-1
uv sync
```

**IMPORTANT:** This project uses `uv` for dependency management. Always use `uv run` to execute commands (e.g., `uv run python src/app.py`). Do not manually activate virtual environments - `uv run` handles this automatically.

### Environment Setup

1. Sign up for [LiveKit Cloud](https://cloud.livekit.io/)

2. Copy the example environment file:
   ```bash
   cp .env.example .env.local
   ```

3. Fill in the required keys in `.env.local`:
   - `LIVEKIT_URL`
   - `LIVEKIT_API_KEY`
   - `LIVEKIT_API_SECRET`
   - `OPENAI_API_KEY`
   - `ASSEMBLYAI_API_KEY`
   - `CARTESIA_API_KEY`

You can also use the [LiveKit CLI](https://docs.livekit.io/home/cli/cli-setup) to automatically load environment variables:

```bash
lk cloud auth
lk app env -w -d .env.local
```

### Download Model Files

Before running the assistant for the first time, download required models:

```bash
uv run python src/app.py download-files
```

This downloads:
- Silero VAD (Voice Activity Detection) model
- LiveKit multilingual turn detector model

### Running the Assistant

```bash
uv run python src/app.py
```

This starts the voice assistant with LiveKit Cloud integration, enabling:
- Natural voice conversations
- Real-time speech recognition
- Natural-sounding voice responses
- Noise cancellation and voice activity detection

## What It Does

The Generic Voice Assistant is a general-purpose AI that:

- **Answers questions** on a wide range of topics
- **Provides information** using GPT-4's knowledge base
- **Maintains natural conversations** with a friendly, helpful tone
- **Handles interruptions** gracefully with LiveKit's turn detection
- **Works with any frontend** (web, mobile, embedded, telephony)

The assistant is designed to be simple and extensible, making it easy to customize for specific use cases or add specialized capabilities.

## Development

### Project Structure

```
src/
├── app.py                    # Voice Assistant (main entry point)
├── config.py                 # Pydantic configuration models
├── factories.py              # Creates STT/LLM/TTS instances
├── session_handler.py        # Session orchestration
└── adapters/
    ├── __init__.py
    └── audio_utils.py        # Shared audio helpers

tests/
├── conftest.py               # Shared pytest fixtures
└── ...                       # Test files
```

Key components:

- **`app.py`** - Application entry point and CLI commands
- **`config.py`** - Environment-driven configuration using Pydantic v2
- **`factories.py`** - Factory functions for creating STT/LLM/TTS instances
- **`session_handler.py`** - Manages agent sessions and conversation flow
- **`adapters/audio_utils.py`** - Shared audio processing utilities

### Testing

Run all tests:

```bash
uv run pytest
```

Run specific test file:

```bash
uv run pytest tests/test_session_handler.py -v
```

Run with coverage:

```bash
uv run pytest --cov=src --cov-report=html
```

### Code Formatting

Format code with ruff:

```bash
uv run ruff format
```

Lint code:

```bash
uv run ruff check
```

Fix linting issues:

```bash
uv run ruff check --fix
```

### Using the Makefile

This project includes a Makefile for common tasks:

```bash
make help           # Show all available commands
make run            # Run the voice assistant
make test           # Run all tests
make format         # Format code
make lint           # Lint code
make download-files # Download model files
```

### Plan Review Command

Review implementation plans for quality and executability before execution:

```bash
# Review a plan file
/review_plan plan/2026-01-23-feature-name.md

# Review a multi-file plan
/review_plan plan/2026-01-23-feature-name/

# Interactive mode
/review_plan
```

The review agent analyzes plans across 5 dimensions:
1. **Accuracy** - Technical correctness and validity
2. **Consistency** - Internal consistency and conventions
3. **Clarity** - Clear, unambiguous instructions
4. **Completeness** - All necessary steps and context
5. **Executability** - Can agents execute without intervention?

Output: Review saved to `*.REVIEW.md` with executability score (0-100) and detailed recommendations.

**Note:** Reviews are advisory only. No changes are made to original plans.

## Architecture

### Dependency Injection

This codebase uses dependency injection (DI) to construct components:

1. **Configuration** - `src/config.py` (Pydantic v2 models, env-driven)
2. **Construction** - `src/factories.py` (builds STT/LLM/TTS)
3. **Wiring** - `src/app.py` (creates app + server)
4. **Runtime** - `src/session_handler.py` (manages sessions)

No custom adapters or protocols are used - components are constructed directly using LiveKit's concrete types.

### Pydantic Models

This project uses **Pydantic v2** for all data models:

- Runtime validation
- JSON serialization/deserialization
- Schema generation
- Environment variable integration
- Better IDE support

See `AGENTS.md` for detailed guidelines on when to use Pydantic vs dataclasses.

## Frontend & Deployment

### Frontend Options

Get started with pre-built frontend applications:

| Platform | Repository | Description |
|----------|-----------|-------------|
| **Web** | [`agent-starter-react`](https://github.com/livekit-examples/agent-starter-react) | React & Next.js web app |
| **iOS/macOS** | [`agent-starter-swift`](https://github.com/livekit-examples/agent-starter-swift) | Native iOS, macOS, visionOS |
| **Flutter** | [`agent-starter-flutter`](https://github.com/livekit-examples/agent-starter-flutter) | Cross-platform mobile |
| **React Native** | [`voice-assistant-react-native`](https://github.com/livekit-examples/voice-assistant-react-native) | React Native & Expo |
| **Android** | [`agent-starter-android`](https://github.com/livekit-examples/agent-starter-android) | Native Android (Kotlin) |
| **Web Embed** | [`agent-starter-embed`](https://github.com/livekit-examples/agent-starter-embed) | Embeddable widget |
| **Telephony** | [Documentation](https://docs.livekit.io/agents/start/telephony/) | Phone integration |

See the [complete frontend guide](https://docs.livekit.io/agents/start/frontend/) for advanced customization.

### Production Deployment

This project includes a production-ready `Dockerfile`. To deploy:

1. Build the Docker image:
   ```bash
   docker build --platform linux/amd64 --no-cache -t voice-assistant .
   ```

2. Deploy to LiveKit Cloud or your preferred platform

See the [deploying to production guide](https://docs.livekit.io/agents/ops/deployment/) for details.

## Coding Agents and MCP

This project works with coding agents like [Cursor](https://www.cursor.com/) and [Claude Code](https://www.anthropic.com/claude-code).

Install the [LiveKit Docs MCP server](https://docs.livekit.io/mcp) for best results:

**For Cursor:**

[![Install MCP Server](https://cursor.com/deeplink/mcp-install-light.svg)](https://cursor.com/en-US/install-mcp?name=livekit-docs&config=eyJ1cmwiOiJodHRwczovL2RvY3MubGl2ZWtpdC5pby9tY3AifQ%3D%3D)

**For Claude Code:**

```bash
claude mcp add --transport http livekit-docs https://docs.livekit.io/mcp
```

**For Codex CLI:**

```bash
codex mcp add --url https://docs.livekit.io/mcp livekit-docs
```

**For Gemini CLI:**

```bash
gemini mcp add --transport http livekit-docs https://docs.livekit.io/mcp
```

The project includes a complete [AGENTS.md](AGENTS.md) file with coding guidelines. See [https://agents.md](https://agents.md) to learn more.



## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
