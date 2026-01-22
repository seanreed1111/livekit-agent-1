# =============================================================================
# McDonald's Drive-Thru Agent - Makefile
# =============================================================================
# Quick Reference:
#   make console       - Run drive-thru agent in console mode (testing)
#   make dev           - Run drive-thru agent with LiveKit (voice testing)
#   make test          - Run all tests
#   make setup         - Install dependencies and download models
# =============================================================================

.PHONY: help console dev start setup test format lint clean
.DEFAULT_GOAL := help

# -----------------------------------------------------------------------------
# Colors
# -----------------------------------------------------------------------------
BLUE   := \033[0;34m
GREEN  := \033[0;32m
YELLOW := \033[0;33m
CYAN   := \033[0;36m
BOLD   := \033[1m
NC     := \033[0m

# -----------------------------------------------------------------------------
# Default Variables
# -----------------------------------------------------------------------------
ARGS   ?=
SCOPE  ?= all

# =============================================================================
# HELP
# =============================================================================
help:
	@echo "$(CYAN)$(BOLD)McDonald's Drive-Thru Agent$(NC)"
	@echo ""
	@echo "$(BOLD)Most Common Commands:$(NC)"
	@echo "  $(GREEN)make console$(NC)              Test agent in terminal (no voice)"
	@echo "  $(GREEN)make dev$(NC)                  Run agent with LiveKit (voice enabled)"
	@echo "  $(GREEN)make test$(NC)                 Run all tests"
	@echo ""
	@echo "$(BOLD)Setup:$(NC)"
	@echo "  $(GREEN)make setup$(NC)                Install dependencies and download models"
	@echo ""
	@echo "$(BOLD)Development:$(NC)"
	@echo "  $(GREEN)make format$(NC)               Format code with ruff"
	@echo "  $(GREEN)make lint$(NC)                 Lint code with ruff"
	@echo "  $(GREEN)make test SCOPE=unit$(NC)      Run unit tests only"
	@echo "  $(GREEN)make test SCOPE=integration$(NC) Run integration tests only"
	@echo "  $(GREEN)make test ARGS=\"-k order\"$(NC) Run tests matching 'order'"
	@echo ""
	@echo "$(BOLD)Production:$(NC)"
	@echo "  $(GREEN)make start$(NC)                Run agent in production mode"
	@echo ""
	@echo "$(BOLD)Utilities:$(NC)"
	@echo "  $(GREEN)make clean$(NC)                Remove caches and generated files"

# =============================================================================
# RUN - Drive-Thru Agent Execution
# =============================================================================

console:  ## Run drive-thru agent in console mode (text-only, for testing)
	@echo "$(BLUE)Starting drive-thru agent in console mode...$(NC)"
	uv run python src/agent.py console
	@echo "$(GREEN)Agent session complete$(NC)"

dev:  ## Run drive-thru agent in dev mode (LiveKit connection, voice enabled)
	@echo "$(BLUE)Starting drive-thru agent in dev mode...$(NC)"
	uv run python src/agent.py dev

start:  ## Run drive-thru agent in production mode
	@echo "$(BLUE)Starting drive-thru agent in production mode...$(NC)"
	uv run python src/agent.py start

# =============================================================================
# SETUP - Dependencies and Models
# =============================================================================

setup:  ## Install dependencies and download required models
	@echo "$(BLUE)Installing dependencies...$(NC)"
	uv sync
	@echo "$(GREEN)Dependencies installed$(NC)"
	@echo "$(BLUE)Downloading model files (VAD, turn detector)...$(NC)"
	uv run python src/agent.py download-files
	@echo "$(GREEN)Setup complete!$(NC)"

# =============================================================================
# TEST - Run Tests
# =============================================================================

test:  ## Run tests (use SCOPE=unit|integration|all, ARGS for pytest flags)
	@echo "$(BLUE)Running tests (SCOPE=$(SCOPE))...$(NC)"
	@case "$(SCOPE)" in \
		unit) \
			uv run pytest tests/ -m "not integration" -v $(ARGS) ;; \
		integration) \
			uv run pytest tests/ -m integration -v $(ARGS) ;; \
		all) \
			uv run pytest tests/ -v $(ARGS) ;; \
		*) \
			echo "$(YELLOW)Unknown SCOPE: $(SCOPE)$(NC)"; \
			echo "Usage: make test SCOPE=[unit|integration|all] [ARGS=\"pytest-flags\"]"; \
			exit 1 ;; \
	esac
	@echo "$(GREEN)Tests complete$(NC)"

# =============================================================================
# CODE QUALITY - Formatting and Linting
# =============================================================================

format:  ## Format code with ruff
	@echo "$(BLUE)Formatting code...$(NC)"
	uv run ruff format
	@echo "$(GREEN)Code formatted$(NC)"

lint:  ## Lint and fix code with ruff
	@echo "$(BLUE)Linting code...$(NC)"
	uv run ruff check --fix
	@echo "$(GREEN)Linting complete$(NC)"

# =============================================================================
# UTILITIES
# =============================================================================

clean:  ## Remove caches and generated files
	@echo "$(BLUE)Cleaning caches and generated files...$(NC)"
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)Clean complete$(NC)"
