# Changelog

Combined changelog for commits 420b4cd to 55367d6 (January 18-22, 2026)

## Features

### Agent Core Functionality
- **Initial LiveKit voice agent implementation** with OpenAI, Cartesia, and AssemblyAI integration
- **Initial agent greeting** - Agent now greets users when the session starts
- **Conversation context** - Agent maintains multi-turn conversation context

### Testing & Quality
- **BDD test scenarios** - Added comprehensive Gherkin feature files for:
  - Agent personality and tone
  - Multi-turn conversation context
  - Safety and harmful request handling
  - Voice processing and interruption handling
- **Test suite** with pytest integration

### Mock Adapters for Development
- **Mock TTS adapter with tone generation** - Generate audio tones for testing without API calls
- **Mock STT and LLM adapters** - Complete mock implementation for offline development
- **Audio utilities** - Tone generation, beep creation, and WAV file handling
- **Demo scripts** - `demo_mock_tts_audio.py` for testing mock audio output

## Refactoring & Architecture

### Dependency Injection & Inversion
- **Configuration management** - Centralized Pydantic-based config in `src/config.py`
- **Factory pattern** - Dependency injection through `src/factories.py`
- **Protocol-based abstractions** - Defined protocols in `src/protocols.py` for STT, LLM, and TTS
- **Session handler** - Separated session orchestration into `src/session_handler.py`
- **Adapter pattern** - Organized adapters in `src/adapters/` package:
  - LiveKit concrete implementations
  - Mock implementations for testing
  - Audio utilities

### Code Quality Improvements
- **Removed global variables** - Refactored agent to eliminate global state
- **Sharp boundaries** - Clear separation of concerns between components
- **Model optimization** - Switched to more cost-effective models

## Documentation

### Project Documentation
- **AGENTS.md** - Comprehensive guide for working with LiveKit Agents:
  - Project structure and uv package manager usage
  - Data models with Pydantic v2 best practices
  - Testing guidelines with pytest and BDD
  - Architecture patterns and dependency injection
  - Implementation tracking system
- **MOCK_ADAPTERS.md** - Detailed documentation for mock adapter development and usage
- **Python reference** - Added `PYTHON_MATCH_REFERENCE.md` for pattern matching examples
- **Future bugfixes** - Documented turn detector language warning issue
- **README updates** - Enhanced setup instructions and project overview

## Build & Development

### Build Tools
- **Makefile** - Added comprehensive Make targets for:
  - Running agent (console, dev, start modes)
  - Testing and code quality (test, format, lint)
  - Utilities (download-files, clean)
- **Development examples** - Created refactoring comparison examples in `past-plans/`

### Project Setup
- **Docker support** - Dockerfile for production deployment
- **Environment configuration** - `.env.example` and `.gitignore` setup
- **uv lock file** - Complete dependency lock for reproducible builds
- **CI/CD cleanup** - Removed unnecessary workflow files

## Dependencies

### Added
- **pydantic** - For configuration and data validation
- **pytest-bdd** - For behavior-driven development testing
- **numpy** - For audio processing utilities

## Files Modified

### Core Application
- `src/agent.py` - Major refactoring for dependency injection and clean architecture
- `src/config.py` - New configuration module
- `src/factories.py` - Factory functions for component creation
- `src/protocols.py` - Protocol definitions for type safety
- `src/session_handler.py` - Session lifecycle management

### Adapters
- `src/adapters/__init__.py` - Package initialization
- `src/adapters/livekit_adapters.py` - LiveKit concrete implementations
- `src/adapters/mock_adapters.py` - Mock implementations with greeting and tone support
- `src/adapters/audio_utils.py` - Audio generation utilities

### Testing
- `tests/test_agent.py` - Updated tests for refactored architecture
- `tests/test_mock_tts_audio.py` - New tests for mock TTS audio generation
- `tests/features/*.feature` - BDD scenario files

### Configuration & Build
- `pyproject.toml` - Updated dependencies and project metadata
- `Makefile` - Enhanced build and development commands
- `.gitignore` - Additional patterns for generated files

### Documentation
- `README.md` - Enhanced project overview and setup instructions
- `AGENTS.md` - Comprehensive agent development guide
- `MOCK_ADAPTERS.md` - Mock adapter documentation

## Migration Notes

This version represents a significant architectural improvement with:
- Clear separation between configuration, factories, and runtime logic
- Protocol-based dependency injection for better testability
- Comprehensive mock adapters for offline development
- Enhanced documentation for AI-assisted development

The refactoring maintains backward compatibility while providing a more maintainable and testable codebase.
