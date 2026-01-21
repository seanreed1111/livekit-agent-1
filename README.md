<a href="https://livekit.io/">
  <img src="./.github/assets/livekit-mark.png" alt="LiveKit logo" width="100" height="100">
</a>

# LiveKit Agents Starter - Python

A complete starter project for building voice AI apps with [LiveKit Agents for Python](https://github.com/livekit/agents) and [LiveKit Cloud](https://cloud.livekit.io/).

The starter project includes:

- A simple voice AI assistant, ready for extension and customization
- A voice AI pipeline with [models](https://docs.livekit.io/agents/models) from OpenAI, Cartesia, and AssemblyAI served through LiveKit Cloud
  - Easily integrate your preferred [LLM](https://docs.livekit.io/agents/models/llm/), [STT](https://docs.livekit.io/agents/models/stt/), and [TTS](https://docs.livekit.io/agents/models/tts/) instead, or swap to a realtime model like the [OpenAI Realtime API](https://docs.livekit.io/agents/models/realtime/openai)
- Eval suite based on the LiveKit Agents [testing & evaluation framework](https://docs.livekit.io/agents/build/testing/)
- [LiveKit Turn Detector](https://docs.livekit.io/agents/build/turns/turn-detector/) for contextually-aware speaker detection, with multilingual support
- [Background voice cancellation](https://docs.livekit.io/home/cloud/noise-cancellation/)
- Integrated [metrics and logging](https://docs.livekit.io/agents/build/metrics/)
- A Dockerfile ready for [production deployment](https://docs.livekit.io/agents/ops/deployment/)

This starter app is compatible with any [custom web/mobile frontend](https://docs.livekit.io/agents/start/frontend/) or [SIP-based telephony](https://docs.livekit.io/agents/start/telephony/).

## Coding agents and MCP

This project is designed to work with coding agents like [Cursor](https://www.cursor.com/) and [Claude Code](https://www.anthropic.com/claude-code). 

To get the most out of these tools, install the [LiveKit Docs MCP server](https://docs.livekit.io/mcp).

For Cursor, use this link:

[![Install MCP Server](https://cursor.com/deeplink/mcp-install-light.svg)](https://cursor.com/en-US/install-mcp?name=livekit-docs&config=eyJ1cmwiOiJodHRwczovL2RvY3MubGl2ZWtpdC5pby9tY3AifQ%3D%3D)

For Claude Code, run this command:

```
claude mcp add --transport http livekit-docs https://docs.livekit.io/mcp
```

For Codex CLI, use this command to install the server:
```
codex mcp add --url https://docs.livekit.io/mcp livekit-docs
```

For Gemini CLI, use this command to install the server:
```
gemini mcp add --transport http livekit-docs https://docs.livekit.io/mcp
```

The project includes a complete [AGENTS.md](AGENTS.md) file for these assistants. You can modify this file  your needs. To learn more about this file, see [https://agents.md](https://agents.md).

## Dev Setup

Clone the repository and install dependencies:

```console
cd agent-starter-python
uv sync
```

**Important:** This project uses `uv` for dependency management. Always use `uv run` to execute commands (e.g., `uv run python src/agent.py`). Do not manually activate the virtual environment - `uv run` handles this automatically. If your IDE or shell auto-activates `.venv`, you can safely ignore it and continue using `uv run` for all commands.

Sign up for [LiveKit Cloud](https://cloud.livekit.io/) then set up the environment by copying `.env.example` to `.env.local` and filling in the required keys:

- `LIVEKIT_URL`
- `LIVEKIT_API_KEY`
- `LIVEKIT_API_SECRET`

You can load the LiveKit environment automatically using the [LiveKit CLI](https://docs.livekit.io/home/cli/cli-setup):

```bash
lk cloud auth
lk app env -w -d .env.local
```

## Run the agent

Before your first run, you must download certain models such as [Silero VAD](https://docs.livekit.io/agents/build/turns/vad/) and the [LiveKit turn detector](https://docs.livekit.io/agents/build/turns/turn-detector/):

```console
uv run python src/agent.py download-files
```

Next, run this command to speak to your agent directly in your terminal:

```console
uv run python src/agent.py console
```

To run the agent for use with a frontend or telephony, use the `dev` command:

```console
uv run python src/agent.py dev
```

In production, use the `start` command:

```console
uv run python src/agent.py start
```

## Makefile

This project includes a `Makefile` for convenient development workflows.

### Quick Commands

```bash
# See all available commands
make help

# Run the agent (requires API keys configured for the chosen models)
make console        # Console mode
make dev            # Dev mode
make start          # Production mode

# Development
make test           # Run all tests
make format         # Format code with ruff
make lint           # Lint code with ruff

# Utilities
make download-files # Download required model files
make clean          # Remove generated files
```

## Frontend & Telephony

Get started quickly with our pre-built frontend starter apps, or add telephony support:

| Platform | Link | Description |
|----------|----------|-------------|
| **Web** | [`livekit-examples/agent-starter-react`](https://github.com/livekit-examples/agent-starter-react) | Web voice AI assistant with React & Next.js |
| **iOS/macOS** | [`livekit-examples/agent-starter-swift`](https://github.com/livekit-examples/agent-starter-swift) | Native iOS, macOS, and visionOS voice AI assistant |
| **Flutter** | [`livekit-examples/agent-starter-flutter`](https://github.com/livekit-examples/agent-starter-flutter) | Cross-platform voice AI assistant app |
| **React Native** | [`livekit-examples/voice-assistant-react-native`](https://github.com/livekit-examples/voice-assistant-react-native) | Native mobile app with React Native & Expo |
| **Android** | [`livekit-examples/agent-starter-android`](https://github.com/livekit-examples/agent-starter-android) | Native Android app with Kotlin & Jetpack Compose |
| **Web Embed** | [`livekit-examples/agent-starter-embed`](https://github.com/livekit-examples/agent-starter-embed) | Voice AI widget for any website |
| **Telephony** | [📚 Documentation](https://docs.livekit.io/agents/start/telephony/) | Add inbound or outbound calling to your agent |

For advanced customization, see the [complete frontend guide](https://docs.livekit.io/agents/start/frontend/).

## Tests and evals

This project includes a complete suite of evals, based on the LiveKit Agents [testing & evaluation framework](https://docs.livekit.io/agents/build/testing/). To run them:

```console
make test
# or
uv run pytest
```



## McDonald's Menu Models

This project includes Pydantic v2 models for representing McDonald's menu data, designed to provide structured menu information to the LLM agent.

### Models

The menu system consists of three main models located in `menus/mcdonalds/models.py`:

- **Modifier**: Represents a menu item variation/modifier
  - `modifier_name: str` - Name of the modifier (e.g., "Egg Whites", "Cheese")
  - `modifier_id: str` - Auto-generated UUID for each modifier

- **Item**: Represents a menu item
  - `category_name: str` - Category (e.g., "Breakfast", "Beef & Pork")
  - `item_name: str` - Item name (e.g., "Big Mac")
  - `available_as_base: bool` - Whether item can be ordered without modifications
  - `modifiers: list[Modifier]` - Available variations for this item

- **Menu**: Complete menu structure
  - `categories: dict[str, list[Item]]` - All items organized by category
  - Helper methods for accessing and manipulating menu items

### Usage

```python
from menus.mcdonalds.models import Menu

# Load the menu from the JSON file
menu = Menu.load_from_file("menus/mcdonalds/transformed-data/menu-structure-2026-01-21.json")

# Access items by category
breakfast_items = menu.get_category("Breakfast")

# Get a specific item
big_mac = menu.get_item("Beef & Pork", "Big Mac")

# Add new items
from menus.mcdonalds.models import Item
new_item = Item(
    category_name="Breakfast",
    item_name="New Item",
    available_as_base=True
)
new_item.add_modifier("Extra Cheese")
menu.add_item(new_item)

# Save modified menu
menu.save_to_file("updated_menu.json")
```

### Serialization

All models support JSON serialization and deserialization:

```python
# Serialize individual items or modifiers
json_str = item.to_json()
item = Item.from_json(json_str)

# Serialize entire menu
json_str = menu.to_json()
menu = Menu.from_json(json_str)

# Save/Load from files
menu.save_to_file("output.json")
menu = Menu.load_from_file("menu-structure-2026-01-21.json")
```

### Testing

Run the menu model tests:

```console
uv run python -m pytest tests/test_menu_models.py -v
```

## Deploying to production

This project is production-ready and includes a working `Dockerfile`. To deploy it to LiveKit Cloud or another environment, see the [deploying to production](https://docs.livekit.io/agents/ops/deployment/) guide.



## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
