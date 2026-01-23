<a href="https://livekit.io/">
  <img src="./.github/assets/livekit-mark.png" alt="LiveKit logo" width="100" height="100">
</a>

# McDonald's Drive-Thru Voice AI Agent

A voice AI agent system built with [LiveKit Agents for Python](https://github.com/livekit/agents) and [LiveKit Cloud](https://cloud.livekit.io/). This repository contains **two main applications**:

1. **McDonald's Drive-Thru Agent** (`src/agent.py`) - A specialized AI agent that takes drive-thru orders using McDonald's menu data
2. **Generic Voice Assistant** (`src/app.py`) - A general-purpose voice AI assistant

## Table of Contents

- [McDonald's Drive-Thru Voice AI Agent](#mcdonalds-drive-thru-voice-ai-agent)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Quick Start](#quick-start)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [Environment Setup](#environment-setup)
    - [Download Model Files](#download-model-files)
  - [McDonald's Drive-Thru Agent](#mcdonalds-drive-thru-agent)
    - [What It Does](#what-it-does)
    - [How It Works](#how-it-works)
    - [Running the Drive-Thru Agent](#running-the-drive-thru-agent)
      - [Console Mode (Testing)](#console-mode-testing)
      - [Dev Mode (LiveKit Connection)](#dev-mode-livekit-connection)
      - [Production Mode](#production-mode)
    - [Menu Data](#menu-data)
    - [Order Output](#order-output)
  - [Generic Voice Assistant](#generic-voice-assistant)
    - [What It Does](#what-it-does-1)
    - [Running the Voice Assistant](#running-the-voice-assistant)
  - [Development](#development)
    - [Project Structure](#project-structure)
    - [Testing](#testing)
    - [Code Formatting](#code-formatting)
    - [Using the Makefile](#using-the-makefile)
  - [Architecture](#architecture)
    - [Dependency Injection](#dependency-injection)
    - [Pydantic Models](#pydantic-models)
  - [Frontend \& Deployment](#frontend--deployment)
    - [Frontend Options](#frontend-options)
    - [Production Deployment](#production-deployment)
  - [Coding Agents and MCP](#coding-agents-and-mcp)
  - [License](#license)

## Overview

This repository demonstrates how to build specialized voice AI agents using LiveKit. The codebase is organized around **two distinct entry points**:

- **`src/agent.py`** - McDonald's Drive-Thru Agent (specialized ordering system)
- **`src/app.py`** - Generic Voice Assistant (general-purpose AI)

Both applications share common infrastructure (STT, TTS, LLM) but serve different purposes.

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

**IMPORTANT:** This project uses `uv` for dependency management. Always use `uv run` to execute commands (e.g., `uv run python src/agent.py`). Do not manually activate virtual environments - `uv run` handles this automatically.

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

Before running either application for the first time, download required models:

```bash
uv run python src/agent.py download-files
```

This downloads:
- Silero VAD (Voice Activity Detection) model
- LiveKit multilingual turn detector model

## McDonald's Drive-Thru Agent

### What It Does

The Drive-Thru Agent is a specialized voice AI that:

- Takes customer orders for McDonald's menu items
- Searches and validates items against a real McDonald's menu
- Handles item modifiers (add-ons, substitutions)
- Confirms each item as it's added
- Reads back the complete order
- Saves orders as JSON files for processing

### How It Works

The Drive-Thru Agent consists of several components:

1. **DriveThruAgent** (`src/drive_thru_agent.py`)
   - Orchestrates the ordering conversation
   - Defines the agent's persona and instructions
   - Manages order state via `OrderStateManager`
   - Provides tools for adding/confirming orders

2. **DriveThruLLM** (`src/drive_thru_llm.py`)
   - Wraps the base LLM (e.g., GPT-4)
   - Intercepts chat requests to inject menu context
   - Searches menu based on keywords in user messages
   - Reduces hallucination by grounding LLM in actual menu items

3. **MenuProvider** (`src/menu_provider.py`)
   - Loads McDonald's menu from JSON
   - Provides search functionality
   - Returns structured menu items (categories, modifiers)

4. **OrderStateManager** (`src/order_state_manager.py`)
   - Tracks order items during conversation
   - Saves completed orders to JSON files
   - One instance per session

### Running the Drive-Thru Agent

#### Console Mode (Testing)

Test the agent directly in your terminal:

```bash
uv run python src/agent.py console
```

This mode is perfect for:
- Quick testing and debugging
- Trying out the ordering flow
- Experimenting with menu items

#### Dev Mode (LiveKit Connection)

Run the agent with a LiveKit connection for testing with real voice:

```bash
uv run python src/agent.py dev
```

This mode:
- Connects to LiveKit Cloud
- Supports frontend applications
- Includes noise cancellation
- Enables real voice interactions

#### Production Mode

For production deployment:

```bash
uv run python src/agent.py start
```

This is the production-ready entry point used in Docker deployments.

### Menu Data

The McDonald's menu is stored as structured Pydantic models in `menus/mcdonalds/`:

- **Menu Structure** - `transformed-data/menu-structure-2026-01-21.json`
- **Pydantic Models** - `models.py`
  - `Menu` - Complete menu with categories
  - `Item` - Individual menu item with modifiers
  - `Modifier` - Item variations (e.g., "Extra Cheese", "No Pickles")

Categories include:
- Breakfast
- Beef & Pork
- Chicken & Fish
- Snacks & Sides
- Beverages
- Coffee & Tea
- Desserts
- Smoothies & Shakes

### Order Output

Completed orders are saved to the `orders/` directory as JSON files:

```json
{
  "session_id": "abc123",
  "items": [
    {
      "item_name": "Big Mac",
      "category": "Beef & Pork",
      "modifiers": ["Extra Cheese", "No Pickles"]
    }
  ],
  "timestamp": "2026-01-22T10:30:00Z"
}
```

## Generic Voice Assistant

### What It Does

The Generic Voice Assistant is a general-purpose AI that:

- Answers questions on various topics
- Provides helpful information
- Maintains a friendly, conversational tone
- Works with any topic (not menu-specific)

### Running the Voice Assistant

```bash
uv run python src/app.py
```

This runs a generic voice assistant without menu integration. Use this for:
- General Q&A applications
- Non-specialized voice interactions
- Testing the base voice pipeline

## Development

### Project Structure

```
src/
├── agent.py                  # Drive-Thru Agent CLI (main entry point)
├── app.py                    # Generic Voice Assistant
├── config.py                 # Pydantic configuration models
├── factories.py              # Creates STT/LLM/TTS instances
├── session_handler.py        # Session orchestration
├── drive_thru_agent.py       # Drive-Thru Agent implementation
├── drive_thru_llm.py         # Menu-aware LLM wrapper
├── menu_provider.py          # Menu search and loading
├── order_state_manager.py   # Order tracking
└── tools/
    └── order_tools.py        # Order management tools

menus/mcdonalds/
├── models.py                 # Pydantic menu models
├── transformed-data/         # Menu JSON files
└── raw-data/                 # Original menu data

tests/
├── conftest.py              # Shared pytest fixtures
├── test_drive_thru_agent.py # Agent tests
├── test_menu_models.py      # Menu model tests
└── ...
```

### Testing

Run all tests:

```bash
uv run pytest
```

Run specific test file:

```bash
uv run pytest tests/test_drive_thru_agent.py -v
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
make console        # Run drive-thru agent in console mode
make dev            # Run drive-thru agent in dev mode
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
3. **Wiring** - `src/agent.py` or `src/app.py` (creates app + server)
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
   docker build --platform linux/amd64 --no-cache -t drive-thru-agent .
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
