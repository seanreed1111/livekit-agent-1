# =============================================================================
# Generic Voice Assistant - Makefile
# =============================================================================

.PHONY: help run setup test format lint clean download-files
.DEFAULT_GOAL := help

BLUE   := \033[0;34m
GREEN  := \033[0;32m
NC     := \033[0m
BOLD   := \033[1m

help:
	@echo "$(BLUE)$(BOLD)Generic Voice Assistant$(NC)"
	@echo ""
	@echo "$(BOLD)Commands:$(NC)"
	@echo "  $(GREEN)make run$(NC)                Run voice assistant"
	@echo "  $(GREEN)make test$(NC)               Run all tests"
	@echo "  $(GREEN)make setup$(NC)              Install dependencies and download models"
	@echo "  $(GREEN)make format$(NC)             Format code with ruff"
	@echo "  $(GREEN)make lint$(NC)               Lint code with ruff"
	@echo "  $(GREEN)make clean$(NC)              Remove caches and generated files"

run:
	@echo "$(BLUE)Starting voice assistant...$(NC)"
	uv run python src/app.py

setup:
	@echo "$(BLUE)Installing dependencies...$(NC)"
	uv sync
	@echo "$(BLUE)Downloading model files...$(NC)"
	uv run python src/app.py download-files
	@echo "$(GREEN)Setup complete!$(NC)"

download-files:
	@echo "$(BLUE)Downloading model files...$(NC)"
	uv run python src/app.py download-files

test:
	@echo "$(BLUE)Running tests...$(NC)"
	uv run pytest tests/ -v

format:
	@echo "$(BLUE)Formatting code...$(NC)"
	uv run ruff format

lint:
	@echo "$(BLUE)Linting code...$(NC)"
	uv run ruff check --fix

clean:
	@echo "$(BLUE)Cleaning caches...$(NC)"
	rm -rf .pytest_cache .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
