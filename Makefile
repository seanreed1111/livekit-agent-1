.PHONY: help test format lint check mock-console mock-dev console dev start download-files clean

# Default target
help:
	@echo "Available targets:"
	@echo "  make test           - Run all tests with pytest"
	@echo "  make format         - Format code with ruff"
	@echo "  make lint           - Lint code with ruff"
	@echo "  make check          - Run linting and tests"
	@echo ""
	@echo "Mock adapter targets (use MockSTT, MockLLM, MockTTS):"
	@echo "  make mock-console   - Run agent in console mode with mock adapters"
	@echo "  make mock-dev       - Run agent in dev mode with mock adapters"
	@echo ""
	@echo "Production targets (use LiveKit adapters):"
	@echo "  make console        - Run agent in console mode"
	@echo "  make dev            - Run agent in dev mode"
	@echo "  make start          - Run agent in production mode"
	@echo ""
	@echo "Utilities:"
	@echo "  make download-files - Download required model files (VAD, turn detector)"
	@echo "  make clean          - Remove generated files and cache"

# Testing
test:
	uv run python -m pytest tests/ -v

# Code formatting and linting
format:
	uv run ruff format

lint:
	uv run ruff check

check: lint test

# Mock adapter targets - uses MockSTT, MockLLM, MockTTS
mock-console:
	@echo "Running agent in console mode with MOCK adapters..."
	@echo "(Using MockSTT, MockLLM, MockTTS - no external API calls)"
	PIPELINE__ADAPTER_TYPE=mock uv run python src/agent.py console

mock-dev:
	@echo "Running agent in dev mode with MOCK adapters..."
	@echo "(Using MockSTT, MockLLM, MockTTS - no external API calls)"
	PIPELINE__ADAPTER_TYPE=mock uv run python src/agent.py dev

# Production targets - uses LiveKit adapters (requires API keys)
console:
	uv run python src/agent.py console

dev:
	uv run python src/agent.py dev

start:
	uv run python src/agent.py start

# Download required model files
download-files:
	uv run python src/agent.py download-files

# Clean generated files
clean:
	rm -rf .pytest_cache
	rm -rf __pycache__
	rm -rf src/__pycache__
	rm -rf src/**/__pycache__
	rm -rf tests/__pycache__
	rm -rf .ruff_cache
	rm -f demo_tone.wav demo_beep.wav
	@echo "Cleaned generated files and caches"
