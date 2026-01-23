# Implementation Plan: Remove McDonald's Drive-Thru Code

## Objective
Remove all McDonald's drive-thru agent code from this repository, leaving only the generic voice assistant (`src/app.py`) as the main entry point.

## Overview
This is primarily a **deletion task** with targeted edits to remove drive-thru configuration from shared files. The generic voice assistant is already complete and functional - no new code required.

**Estimated Time:** 2-3 hours
**Risk Level:** Low (clean separation between drive-thru and generic code)

## Plan Updates (2026-01-23)

This plan has been updated based on review feedback to address all high-priority issues:

1. **Phase 1 (Verification Timing):** Moved test verification to Phase 8 to avoid import errors before config cleanup
2. **Phase 2 (src/tools/ cleanup):** Changed to `rm -rf src/tools/` for cleaner execution
3. **Phase 4.3 (conftest.py):** Made explicit with all 17 fixtures listed by name and line numbers (lines 12-13, 20-287)
4. **Phase 5.4 (NEW):** Added dependency cleanup step - remove `rapidfuzz` and `click` from pyproject.toml, run `uv lock`
5. **Phase 6.2 (AGENTS.md):** Specified exact lines to update (38, 153, 343, 350)
6. **Phase 8.3 (Smoke Test):** Replaced timeout-based test with proper import verification and test suite

**Executability Score Improvement:** 78/100 → Expected 85+/100 after updates

---

## Phase 1: Preparation & Safety

- [x] Create Safety Branch
```bash
git checkout -b remove-drive-thru-code
git status
```

- [x] Verify Current State
```bash
# Verify branch was created successfully
git branch --show-current
```

**Success:** On `remove-drive-thru-code` branch.

**Note:** Test verification moved to Phase 8 (after config cleanup) to avoid import errors.

---

## Phase 2: Delete Drive-Thru Source Files

- [x] Core Drive-Thru Files (delete entirely)
```bash
rm src/drive_thru_agent.py
rm src/drive_thru_llm.py
rm src/menu_provider.py
rm src/order_state_manager.py
rm src/menu_validation.py
rm src/tools/order_tools.py
rm src/agent.py
```

**Critical:** `src/agent.py` is the old drive-thru entry point. `src/app.py` becomes the new main entry point.

- [x] Menu Data (delete entire directory)
```bash
rm -rf src/menus/
```

- [x] Tools Directory (delete entirely)
```bash
# Delete entire tools directory
rm -rf src/tools/
```

**Note:** This directory only contains drive-thru specific code (`order_tools.py`).

---

## Phase 3: Delete Drive-Thru Tests

- [x] Test Files (delete entirely)
```bash
rm tests/test_drive_thru_agent.py
rm tests/test_drive_thru_llm.py
rm tests/test_drive_thru_agent_integration.py
rm tests/test_menu_models.py
rm tests/test_menu_provider.py
rm tests/test_menu_validation.py
rm tests/test_order_state.py
rm tests/test_order_tools.py
```

- [x] BDD Feature Files (delete directory)
```bash
rm -rf tests/features/
```

---

## Phase 4: Update Shared Source Files

- [x] 4.1: Update `src/config.py`

**DELETE lines 83-123:**
```python
class DriveThruConfig(BaseModel):
    """Configuration for McDonald's drive-thru agent."""
    # ... entire class (lines 83-123)
```

**DELETE lines 141-144 from `AppConfig`:**
```python
    drive_thru: DriveThruConfig = Field(
        default_factory=DriveThruConfig,
        description="Drive-thru agent configuration",
    )
```

**KEEP:** All other configs (`AgentConfig`, `PipelineConfig`, `SessionConfig`, `AppConfig`)

- [x] 4.2: Update `src/session_handler.py`

**DELETE lines 107-159:**
```python
class DriveThruSessionHandler:
    """Handles creation of drive-thru agent sessions."""
    # ... entire class (lines 107-159)
```

**KEEP:** `SessionHandler` class (lines 15-105) - this is generic and used by `app.py`

- [x] 4.3: Update `tests/conftest.py`

**DELETE imports (lines 12-13):**
```python
from menus.mcdonalds.models import Item, Menu, Modifier
from menu_provider import MenuProvider
```

**DELETE all drive-thru fixtures (lines 20-287):**

**Menu Data Fixtures (lines 20-54):**
- `test_menu_data` (lines 20-54)

**Item Fixtures (lines 62-122):**
- `sample_menu_items` (lines 62-95)
- `big_mac_with_modifiers` (lines 98-111)
- `item_without_modifiers` (lines 114-122)

**Menu Fixtures (lines 130-136):**
- `sample_menu` (lines 130-136)

**MenuProvider Fixtures (lines 144-156):**
- `test_menu_provider` (lines 144-149)
- `real_menu_provider` (lines 152-156)

**Path Fixtures (lines 164-174):**
- `real_menu_path` (lines 164-174)

**OrderStateManager Fixtures (lines 182-193):**
- `temp_output_dir` (lines 182-185)
- `order_manager` (lines 188-193)

**OrderTools Fixtures (lines 201-223):**
- `menu_provider` (lines 201-205)
- `order_state_manager` (lines 208-215)
- `order_tools` (lines 218-223)

**DriveThruLLM Fixtures (lines 231-255):**
- `mock_drive_thru_llm` (lines 231-237)
- `drive_thru_llm` (lines 240-255)

**DriveThruAgent Fixtures (lines 263-286):**
- `drive_thru_agent` (lines 263-273)
- `real_drive_thru_agent` (lines 276-286)

**Total:** 17 fixtures to delete, spanning lines 12-13 (imports) and 20-287 (fixture definitions)

**KEEP:** Only the file header docstring (lines 1-10) and generic pytest imports (lines 7-10). The file will be nearly empty after cleanup.

---

## Phase 5: Update Build & Deployment

- [x] 5.1: Update `Dockerfile`

**Line 64 - Change download command:**
```dockerfile
# OLD
RUN uv run src/agent.py download-files

# NEW
RUN uv run python src/app.py download-files
```

**Line 69 - Change entrypoint:**
```dockerfile
# OLD
CMD ["uv", "run", "src/agent.py", "start"]

# NEW
CMD ["uv", "run", "python", "src/app.py"]
```

- [x] 5.2: Replace `Makefile`

**Complete rewrite** for generic assistant:

```makefile
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
```

- [x] 5.3: Update `pyproject.toml` metadata

**Lines 6-8:**
```toml
# OLD
name = "agent-starter-python"
version = "1.0.0"
description = "Simple voice AI assistant built with LiveKit Agents for Python"

# NEW
name = "generic-voice-assistant"
version = "2.0.0"
description = "Generic voice AI assistant built with LiveKit Agents for Python"
```

- [x] 5.4: Remove drive-thru dependencies from `pyproject.toml`

**DELETE lines 18-19 (drive-thru only dependencies):**
```toml
    "rapidfuzz>=3.14.3",
    "click>=8.3.1",
```

**Reason:**
- `rapidfuzz` - Only used by `menu_provider.py` for fuzzy menu search
- `click` - Only used by `src/agent.py` CLI (being deleted)

**Update lock file:**
```bash
uv lock
```

**Verify dependencies:**
```bash
# Check remaining dependencies
uv tree
```

**Success:** Lock file updated, no unused dependencies remain.

---

## Phase 6: Update Documentation

- [x] 6.1: Update `README.md`

**Major sections to rewrite:**

1. **Title (Line 6):** "Generic Voice AI Assistant"
2. **Overview (Lines 48-55):** Remove drive-thru description, focus on generic assistant only
3. **Table of Contents (Lines 14-46):** Remove all drive-thru sections
4. **Delete entire sections:**
   - "McDonald's Drive-Thru Agent" (Lines 117-231)
   - "Menu Data" section
   - "Order Output" section
   - Drive-thru CLI modes (console/dev/start)

5. **Simplify "Quick Start":**
   - Running: `uv run python src/app.py`
   - Download models: `uv run python src/app.py download-files`
   - Remove CLI mode instructions

6. **Update "Project Structure":**
   - Remove references to drive-thru files
   - Focus on `src/app.py` as main entry point
   - Remove `menus/` directory

7. **Keep and update:**
   - Generic Voice Assistant section
   - Development section (testing, formatting)
   - Architecture section (DI, Pydantic)
   - Frontend & Deployment section

- [x] 6.2: Update `AGENTS.md`

**Line 38 - Update project structure description:**
```markdown
# OLD
All app-level code is in the `src/` directory. In general, simple agents can be constructed with a single `agent.py` file. Additional files can be added, but you must retain `agent.py` as the entrypoint (see the associated Dockerfile for how this is deployed).

# NEW
All app-level code is in the `src/` directory. In general, simple agents can be constructed with a single `app.py` file. Additional files can be added as needed for more complex implementations.
```

**Line 153 - Update example command:**
```markdown
# OLD
# Run the agent
uv run python src/agent.py dev

# NEW
# Run the agent
uv run python src/app.py
```

**Line 343 - Update wiring description:**
```markdown
# OLD
3. **Wiring**: `src/agent.py` (creates the app + server)

# NEW
3. **Wiring**: `src/app.py` (creates the app + server)
```

**Lines 350 - Update file structure example:**
```markdown
# OLD
src/
├── agent.py            # App entrypoint + wiring

# NEW
src/
├── app.py              # App entrypoint + wiring
```

**Search and clean up any remaining references:**
```bash
# Search for drive-thru references
grep -n "drive-thru\|drive_thru\|McDonald\|menu\|order" AGENTS.md
```

**Keep:** All generic best practices sections (Pydantic, testing, DI patterns, planning principles)

- [x] 6.3: Update `CHANGELOG.md`

**Add new entry at top:**
```markdown
## [2.0.0] - 2026-01-23

### BREAKING CHANGES
- Removed all McDonald's drive-thru specific code
- Simplified to generic voice assistant only
- Main entry point is now `src/app.py` (replaced `src/agent.py` CLI)

### Removed
- Drive-thru agent implementation
- Menu provider, validation, and order management
- Drive-thru specific tests and BDD scenarios
- `DriveThruConfig` and `DriveThruSessionHandler`
- CLI commands (console/dev/start modes)

### Changed
- Dockerfile entrypoint updated to use `src/app.py`
- Makefile simplified for generic assistant
- Documentation updated to reflect generic use case only
```

---

## Phase 7: Clean Up Runtime Files

- [x] Update `.gitignore`
```bash
# Add to .gitignore if not already present
echo "orders/" >> .gitignore
echo "plan/" >> .gitignore
```

- [x] Delete Runtime Directories (local only)
```bash
rm -rf orders/
rm -rf plan/completed-plans/drive-thru-llm/
```

**Note:** These are gitignored, so deletions won't affect git.

---

## Phase 8: Verification

- [x] 8.1: Code Quality Checks
```bash
# Format and lint
uv run ruff format
uv run ruff check --fix

# Search for remaining references
grep -r "drive_thru" src/ tests/ 2>/dev/null || echo "✓ No drive_thru references"
grep -r "DriveThru" src/ tests/ 2>/dev/null || echo "✓ No DriveThru references"
grep -r "mcdonalds" src/ tests/ 2>/dev/null || echo "✓ No mcdonalds references"
grep -r "menu_provider" src/ tests/ 2>/dev/null || echo "✓ No menu_provider references"
```

**Success:** No linting errors, code formatted, no drive-thru references.

- [x] 8.2: Test Suite Verification
```bash
# Run all remaining tests
uv run pytest tests/ -v
```

**Success:** All tests pass, no import errors.

- [x] 8.3: Application Smoke Test
```bash
# Download models
uv run python src/app.py download-files

# Verify app can be imported without errors
uv run python -c "from app import entrypoint; print('✓ App imports successfully')"

# Run comprehensive tests including app startup
uv run pytest tests/test_agent.py -v
```

**Success:**
- Models download successfully
- App module imports without errors
- All tests pass (verifies app initialization works)

- [x] 8.4: Docker Build Verification
```bash
# Build Docker image
docker build --platform linux/amd64 -t generic-voice-assistant .

# Verify it builds without errors
```

**Success:** Docker builds cleanly.

---

## Phase 9: Git Commit

### Review Changes
```bash
git status
git diff --stat
git diff --name-status | head -20
```

### Create Commit
```bash
git add -A
git commit -m "feat: remove drive-thru code, simplify to generic voice assistant

BREAKING CHANGE: Removed all McDonald's drive-thru specific functionality

This commit removes all drive-thru agent code and simplifies the repository
to a generic voice AI assistant only.

Changes:
- Deleted drive-thru agent, LLM wrapper, menu system, and order management
- Removed DriveThruConfig and DriveThruSessionHandler
- Deleted all drive-thru tests and BDD scenarios
- Updated documentation to reflect generic use case
- Changed main entry point from src/agent.py to src/app.py
- Simplified Makefile for generic assistant
- Updated Dockerfile for new entry point

The generic voice assistant (src/app.py) remains fully functional with all
shared infrastructure (factories, config, session handler)."
```

### Final Verification
```bash
git status
uv run pytest tests/ -v
uv run python src/app.py download-files
```

---

## Critical Files Reference

### Files to DELETE (37 files)
**Source Code (9):**
- `src/drive_thru_agent.py`
- `src/drive_thru_llm.py`
- `src/menu_provider.py`
- `src/order_state_manager.py`
- `src/menu_validation.py`
- `src/tools/order_tools.py`
- `src/agent.py` ⚠️ **Old entry point**
- `src/menus/` (entire directory)
- `src/tools/` (if empty after cleanup)

**Tests (8):**
- `tests/test_drive_thru_agent.py`
- `tests/test_drive_thru_llm.py`
- `tests/test_drive_thru_agent_integration.py`
- `tests/test_menu_models.py`
- `tests/test_menu_provider.py`
- `tests/test_menu_validation.py`
- `tests/test_order_state.py`
- `tests/test_order_tools.py`

**BDD Features:**
- `tests/features/` (entire directory)

**Runtime (local only):**
- `orders/` (generated orders)
- `plan/completed-plans/drive-thru-llm/` (planning docs)

### Files to EDIT (9 files)
1. **`src/config.py`**
   - DELETE lines 83-123: `DriveThruConfig` class
   - DELETE lines 141-144: `drive_thru` field in `AppConfig`

2. **`src/session_handler.py`**
   - DELETE lines 107-159: `DriveThruSessionHandler` class

3. **`tests/conftest.py`**
   - DELETE lines 12-13: import statements
   - DELETE lines 20-287: all 17 drive-thru fixtures
   - RESULT: Nearly empty file with just header

4. **`Dockerfile`**
   - Line 64: Change to `src/app.py download-files`
   - Line 69: Change to `CMD ["uv", "run", "python", "src/app.py"]`

5. **`Makefile`**
   - Complete rewrite for generic assistant

6. **`pyproject.toml`**
   - Lines 6-8: Update name, version, description
   - DELETE lines 18-19: Remove `rapidfuzz` and `click` dependencies
   - Run `uv lock` to update lock file

7. **`README.md`**
   - Rewrite for generic assistant only

8. **`AGENTS.md`**
   - Line 38: Update project structure description
   - Line 153: Update example command
   - Line 343: Update wiring description
   - Line 350: Update file structure example

9. **`CHANGELOG.md`**
   - Add breaking changes entry

### Files to KEEP (unchanged)
- `src/app.py` ⭐ **New main entry point**
- `src/config.py` (partial edit - keep base configs)
- `src/factories.py`
- `src/session_handler.py` (partial edit - keep `SessionHandler`)
- `src/keyword_intercept_llm.py`
- `src/mock_llm.py`
- `tests/test_agent.py`
- `tests/test_keyword_intercept.py`

---

## Verification Checklist

- [ ] All drive-thru source files deleted
- [ ] All drive-thru tests deleted
- [ ] `src/config.py` updated (DriveThruConfig removed)
- [ ] `src/session_handler.py` updated (DriveThruSessionHandler removed)
- [ ] `tests/conftest.py` cleaned (all 17 drive-thru fixtures removed)
- [ ] `Dockerfile` updated (entry point changed to app.py)
- [ ] `Makefile` rewritten for generic assistant
- [ ] `pyproject.toml` metadata updated
- [ ] `pyproject.toml` dependencies cleaned (rapidfuzz, click removed)
- [ ] `uv.lock` updated after dependency changes
- [ ] `README.md` rewritten for generic assistant
- [ ] `AGENTS.md` cleaned (lines 38, 153, 343, 350 updated)
- [ ] `CHANGELOG.md` updated with breaking changes
- [ ] Code formatted (ruff format)
- [ ] Code linted (ruff check --fix)
- [ ] No drive-thru references remain in code (grep verification)
- [ ] All tests pass
- [ ] Application imports successfully
- [ ] Models download successfully
- [ ] Docker builds successfully
- [ ] Git commit created
- [ ] Clean working tree

---

## Rollback Plan

If issues arise:
```bash
git checkout main
git branch -D remove-drive-thru-code
```

Or reset to specific commit:
```bash
git reset --hard HEAD~1
```

---

## Notes

- **Clean Separation:** The generic assistant (`app.py`) has zero dependencies on drive-thru code
- **Shared Infrastructure:** All factories, base configs, and `SessionHandler` are generic and reusable
- **No New Code:** This is purely a deletion/cleanup task - no new functionality needed
- **Safe Operation:** Changes are isolated, well-defined, and easily reversible
- **Dependency Cleanup:** Removing `rapidfuzz` and `click` reduces dependency footprint
- **Test Verification:** Moved to Phase 8 to avoid import errors before config cleanup
- **Explicit Fixture List:** All 17 conftest.py fixtures listed by name for clear execution
