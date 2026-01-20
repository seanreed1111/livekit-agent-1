# Mock Adapters Guide

This project includes mock implementations of STT, LLM, and TTS components for testing and development without external API calls.

## Quick Start

Use the provided Makefile targets to run the agent with mock adapters:

```bash
# Run agent in console mode with mock adapters
make mock-console

# Run agent in dev mode with mock adapters
make mock-dev
```

## What Are Mock Adapters?

Mock adapters are lightweight implementations that simulate the behavior of production voice pipeline components:

- **MockSTT** - Simulates speech-to-text without calling external services
- **MockLLM** - Returns pre-configured responses without calling LLM APIs
- **MockTTS** - Generates synthetic audio (tones/beeps) without calling TTS services

### Benefits

- ✅ **No API keys required** - Test without LiveKit Cloud credentials
- ✅ **No external dependencies** - Work offline or without network
- ✅ **Fast development** - Instant responses, no API latency
- ✅ **Deterministic testing** - Predictable behavior for automated tests
- ✅ **Cost-free** - No API usage charges during development

## Using Mock Adapters

### Option 1: Makefile (Recommended)

```bash
# See all available targets
make help

# Run with mock adapters
make mock-console  # Console mode
make mock-dev      # Dev mode

# Run tests
make test

# Code quality
make format
make lint
```

### Option 2: Environment Variable

Set the `PIPELINE__ADAPTER_TYPE` environment variable:

```bash
# Unix/Linux/macOS
PIPELINE__ADAPTER_TYPE=mock uv run python src/agent.py console

# Windows (PowerShell)
$env:PIPELINE__ADAPTER_TYPE="mock"
uv run python src/agent.py console
```

### Option 3: Programmatic Configuration

```python
from agent import VoiceAgentApp
from config import AppConfig, PipelineConfig

# Configure to use mock adapters
config = AppConfig(
    pipeline=PipelineConfig(adapter_type="mock")
)

# Create app with mock adapters
app = VoiceAgentApp(config=config)
app.run()
```

### Option 4: Direct Injection

```python
from agent import VoiceAgentApp
from adapters.mock_adapters import MockSTT, MockLLM, MockTTS

# Create mock adapters with custom settings
stt = MockSTT()
llm = MockLLM(responses=["Custom response 1", "Custom response 2"])
tts = MockTTS(audio_type="beep", sample_rate=24000)

# Inject into app
app = VoiceAgentApp(stt=stt, llm=llm, tts=tts)
```

## Mock Adapter Configuration

### MockSTT

```python
from adapters.mock_adapters import MockSTT

stt = MockSTT(
    transcriptions=["Hello", "How are you?"],  # Custom transcriptions
    simulate_delay=0.1,                         # Simulated latency
)
```

### MockLLM

```python
from adapters.mock_adapters import MockLLM

llm = MockLLM(
    responses=[
        "I understand. How can I help?",
        "That's interesting.",
        "I can assist with that.",
    ],
    simulate_delay=0.2,  # Simulated response time
)
```

### MockTTS

```python
from adapters.mock_adapters import MockTTS

tts = MockTTS(
    audio_type="tone",      # "tone" or "beep"
    sample_rate=24000,      # Audio sample rate (Hz)
    num_channels=1,         # 1 (mono) or 2 (stereo)
    simulate_delay=0.1,     # Simulated synthesis delay
    voice="mock-voice",     # Voice identifier (for logging)
)
```

## Audio Generation

MockTTS generates real audio data using synthetic tones:

- **Tone mode** (`audio_type="tone"`): Simple sine wave at 440Hz
- **Beep mode** (`audio_type="beep"`): Sequence of short beeps at 800Hz

The audio is generated in the correct format for LiveKit:
- Format: 16-bit signed PCM (int16)
- Sample rate: 24,000 Hz (default, configurable)
- Channels: 1 (mono, configurable)

### Demo Script

Run the audio generation demo:

```bash
uv run python demo_mock_tts_audio.py
```

This creates two WAV files you can play:
- `demo_tone.wav` - A 440Hz tone
- `demo_beep.wav` - Sequence of beeps

Play them:
```bash
# macOS
afplay demo_tone.wav

# Linux
aplay demo_tone.wav

# Windows
start demo_tone.wav
```

## Testing

Mock adapters are extensively tested:

```bash
# Run all tests
make test

# Run specific test file
uv run python -m pytest tests/test_mock_tts_audio.py -v
```

Test files:
- `tests/test_agent.py` - Basic agent and adapter instantiation tests
- `tests/test_mock_tts_audio.py` - MockTTS audio generation tests

## Architecture

The mock adapters follow the same protocol-based architecture as production adapters:

```
┌─────────────────────────────────────────────────┐
│                  VoiceAgentApp                  │
│  (Dependency Injection via Constructor)         │
└──────────┬──────────────┬──────────────┬────────┘
           │              │              │
    ┌──────▼──────┐┌──────▼──────┐┌─────▼──────┐
    │STTProtocol  ││LLMProtocol  ││TTSProtocol │
    └──────┬──────┘└──────┬──────┘└─────┬──────┘
           │              │              │
    ┌──────▼──────┐┌──────▼──────┐┌─────▼──────┐
    │  MockSTT    ││  MockLLM    ││  MockTTS   │
    │     or      ││     or      ││    or      │
    │ LiveKitSTT  ││ LiveKitLLM  ││LiveKitTTS  │
    └─────────────┘└─────────────┘└────────────┘
```

**Key Files:**
- `src/protocols.py` - Protocol definitions
- `src/adapters/mock_adapters.py` - Mock implementations
- `src/adapters/livekit_adapters.py` - Production implementations
- `src/adapters/audio_utils.py` - Audio generation utilities
- `src/factories.py` - Factory functions for creating adapters
- `src/config.py` - Configuration models

## Switching Between Mock and Production

Change the `adapter_type` configuration:

```python
# Mock adapters (no API keys needed)
config = AppConfig(
    pipeline=PipelineConfig(adapter_type="mock")
)

# Production adapters (requires LiveKit Cloud credentials)
config = AppConfig(
    pipeline=PipelineConfig(adapter_type="livekit")
)
```

Or use environment variables:
```bash
# Mock
PIPELINE__ADAPTER_TYPE=mock uv run python src/agent.py console

# Production
PIPELINE__ADAPTER_TYPE=livekit uv run python src/agent.py console
```

## Limitations

Mock adapters are designed for testing and development, not production:

- **MockSTT**: Doesn't actually transcribe audio
- **MockLLM**: Returns pre-configured responses, doesn't understand context
- **MockTTS**: Generates synthetic tones, not natural speech

For production deployment, use the LiveKit adapters with proper API credentials.

## Further Reading

- [AGENTS.md](AGENTS.md) - Complete project guide
- [README.md](README.md) - Project overview
- [LiveKit Agents Documentation](https://docs.livekit.io/agents/)
