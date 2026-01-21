.PHONY: help test format lint check console dev start download-files clean

# Default target
help:
	@echo "Available targets:"
	@echo "  make test           - Run all tests with pytest"
	@echo "  make format         - Format code with ruff"
	@echo "  make lint           - Lint code with ruff"
	@echo "  make check          - Run linting and tests"
	@echo ""
	@echo "Run targets:"
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

# Run targets (requires API keys configured for the chosen models)
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
