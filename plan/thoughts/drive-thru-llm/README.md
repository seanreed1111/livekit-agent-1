# McDonald's Drive-Thru Agent - Implementation Plans

**Created**: 2026-01-21
**Purpose**: Ordered breakdown of main plan into testable, implementable chunks

---

## Overview

This directory contains the **complete implementation plan** for the McDonald's Drive-Thru Agent, broken down into **8 numbered plans** that must be executed in order based on dependencies.

The original monolithic plan (`mcdonalds-drive-thru-agent-plan.md`) has been analyzed for dependencies and restructured into smaller, focused plans that are:
- ✅ **Ordered by dependencies** (Plan 01 has no dependencies, Plan 08 depends on all previous)
- ✅ **Testable using BDD strategy** (each plan maps to BDD scenarios)
- ✅ **Easy for agents to implement** (clear scope, concrete tasks)
- ✅ **Independently verifiable** (each plan has success criteria)

---

## Implementation Status Checklist

**Last Updated**: 2026-01-21 (Plan 06 completed)

Track completion of all implementation plans. Check off each plan as it's completed and verified.

- [x] **Plan 01: Menu Models and Validation** ✅ COMPLETED
  - Enhanced `Item` class with `quantity` and `item_id` fields
  - Implemented `__add__()` method for combining items
  - Created pure validation functions (`fuzzy_match_item`, `validate_item_exists`, `validate_modifiers`, `validate_order_item`)
  - 67 tests passing in 0.08s
  - Files: `menus/mcdonalds/models.py`, `src/menu_validation.py`
  - Tests: `tests/test_menu_models.py`, `tests/test_menu_validation.py`

- [x] **Plan 02: MenuProvider** ✅ COMPLETED
  - Created `MenuProvider` class with read-only menu access
  - Implemented query methods: `search_items()`, `get_category()`, `get_item()`, `get_all_categories()`, etc.
  - All methods return immutable copies via `model_copy()`
  - Built lookup indices for O(1) category access
  - 28 tests passing in 0.06s
  - Files: `src/menu_provider.py`
  - Tests: `tests/test_menu_provider.py`
  - Depends on: Plan 01

- [x] **Plan 03: OrderStateManager** ✅ COMPLETED
  - Created `OrderItem` dataclass with full serialization support (to_dict/from_dict)
  - Implemented `OrderStateManager` class with all command methods (add_item, remove_item, update_item_quantity, complete_order, clear_order)
  - Implemented all query methods (get_items, get_item_by_id, get_total_count, get_order_summary, is_empty)
  - Dual persistence: incremental log (JSONL) + final JSON on completion
  - Returns immutable copies from query methods to prevent external state mutations
  - 36 tests passing in 0.04s
  - Files: `src/order_state_manager.py`
  - Tests: `tests/test_order_state.py`
  - Fixtures added to: `tests/conftest.py`
  - Depends on: Plan 01

- [x] **Plan 04: OrderTools** ✅ COMPLETED
  - Created `src/tools/order_tools.py` with factory function and three tools
  - Implemented `add_item_to_order` tool with validation integration
  - Implemented `complete_order` tool for order finalization
  - Implemented `remove_item_from_order` tool for item removal
  - 24 tests passing in 0.45s
  - Files: `src/tools/order_tools.py`, `src/tools/__init__.py`
  - Tests: `tests/test_order_tools.py`
  - Fixtures added to: `tests/conftest.py`
  - Depends on: Plans 01, 02, 03

- [x] **Plan 05: DriveThruLLM** ✅ COMPLETED
  - Created `DriveThruLLM` stateless wrapper class
  - Implemented keyword extraction from user messages
  - Implemented menu item search and context injection
  - Implemented chat() method that intercepts and injects menu context
  - 19 tests passing in 0.40s
  - Files: `src/drive_thru_llm.py`
  - Tests: `tests/test_drive_thru_llm.py`
  - Depends on: Plan 02

- [x] **Plan 06: DriveThruAgent** ✅ COMPLETED
  - Created `DriveThruAgent` orchestration class extending LiveKit Agent
  - Implemented component wiring: owns OrderStateManager, receives MenuProvider and DriveThruLLM via DI
  - Implemented comprehensive agent instructions and persona
  - Provided properties for accessing agent, order_state, llm, and tools
  - 6 unit tests passing (agent initialization, wiring, ownership)
  - 8 integration tests passing (tool integration, order workflows, error handling)
  - 14 total tests passing in 0.40s
  - Files: `src/drive_thru_agent.py`
  - Tests: `tests/test_drive_thru_agent.py`, `tests/test_drive_thru_agent_integration.py`
  - Fixtures added to: `tests/conftest.py`
  - Depends on: Plans 02, 03, 04, 05

- [x] **Plan 07: Integration and Wiring** ✅ COMPLETED (2026-01-21)
  - Added `DriveThruConfig` to `src/config.py` with menu path, output dir, fuzzy match threshold, and feature flags
  - Created `DriveThruSessionHandler` in `src/session_handler.py` for session management
  - Created `src/agent.py` as CLI entry point with commands: console, dev, start, download-files
  - Created BDD feature files (6 files total):
    - `tests/features/agent/01_basic_ordering.feature` (3 scenarios)
    - `tests/features/agent/02_multi_item_ordering.feature` (3 scenarios)
    - `tests/features/agent/03_modifiers.feature` (4 scenarios)
    - `tests/features/agent/04_order_corrections.feature` (3 scenarios)
    - `tests/features/agent/05_error_handling.feature` (4 scenarios)
    - `tests/features/agent/06_order_completion.feature` (4 scenarios)
  - Total: 21 BDD scenarios defined
  - Added dependencies: click, pytest-bdd
  - CLI tested and operational
  - Files: `src/config.py` (modified), `src/session_handler.py` (modified), `src/agent.py` (new)
  - Feature files: `tests/features/agent/*.feature` (6 files)
  - Note: BDD step definitions and test execution deferred (user preference)
  - Depends on: Plans 01-06

- [ ] **Plan 08: Accuracy Optimization**
  - Not yet started (Optional/Future Work)
  - Depends on: Plan 07

---

## Dependency Graph

```
Plan 01: Menu Models & Validation
    ↓ (provides: Item models, validation functions)
    │
    ├─→ Plan 02: MenuProvider (depends on Item models)
    │       ↓ (provides: read-only menu access)
    │       │
    │       └─→ Plan 05: DriveThruLLM (depends on MenuProvider)
    │
    └─→ Plan 03: OrderStateManager (depends on OrderItem dataclass)
            ↓ (provides: state management)
            │
            └─→ Plan 04: OrderTools (depends on Plans 01, 02, 03)
                    ↓ (provides: LLM tools)
                    │
                    └─→ Plan 06: DriveThruAgent (depends on Plans 02, 03, 04, 05)
                            ↓ (provides: complete agent)
                            │
                            └─→ Plan 07: Integration (depends on Plans 01-06)
                                    ↓ (provides: working application)
                                    │
                                    └─→ Plan 08: Optimization (depends on Plan 07)
```

---

## Implementation Plans

### Plan 01: Menu Models and Validation
**File**: `01-menu-models-and-validation.md`
**Dependencies**: None (Foundation layer)
**Complexity**: Low-Medium

**What it builds**:
- Enhanced `Item` class with `quantity` and `item_id` fields
- `__add__()` method for combining items
- Pure validation functions: `fuzzy_match_item()`, `validate_item_exists()`, `validate_modifiers()`
- `ValidationResult` dataclass

**Why first**: No dependencies, pure functions, fast to test

**Success Criteria**: 22+ unit tests pass in <1 second

---

### Plan 02: MenuProvider
**File**: `02-menu-provider.md`
**Dependencies**: Plan 01 (Menu models)
**Complexity**: Low

**What it builds**:
- `MenuProvider` class for read-only menu access
- Query methods: `search_items()`, `get_category()`, `get_item()`
- Immutable data guarantees

**Why second**: Only depends on models, provides data access for all other components

**Success Criteria**: 20+ unit tests pass in <2 seconds, returns immutable copies

---

### Plan 03: OrderStateManager
**File**: `03-order-state-manager.md`
**Dependencies**: Plan 01 (OrderItem dataclass)
**Complexity**: Medium

**What it builds**:
- `OrderStateManager` class (single source of truth for order state)
- Command methods: `add_item()`, `remove_item()`, `complete_order()`
- Query methods: `get_items()`, `get_order_summary()`
- Persistence: incremental log (JSONL) + final JSON

**Why third**: Parallel to Plan 02, only depends on dataclasses

**Success Criteria**: 30+ unit tests pass, file I/O works correctly, 95%+ coverage

---

### Plan 04: OrderTools
**File**: `04-order-tools.md`
**Dependencies**: Plans 01, 02, 03 (validation, menu, state)
**Complexity**: Medium

**What it builds**:
- `create_order_tools()` factory function
- `add_item_to_order` tool (with validation)
- `complete_order` tool
- `remove_item_from_order` tool (optional)

**Why fourth**: Coordination layer between LLM and system, needs all foundation components

**Success Criteria**: 20+ integration tests pass, validation prevents invalid state mutations

---

### Plan 05: DriveThruLLM
**File**: `05-drive-thru-llm.md`
**Dependencies**: Plan 02 (MenuProvider)
**Complexity**: Medium

**What it builds**:
- `DriveThruLLM` wrapper class (stateless)
- Menu context injection (Strategy 2)
- Keyword extraction and relevant item search

**Why fifth**: Parallel to Plan 04, only depends on MenuProvider for context

**Success Criteria**: 15+ unit tests pass, context injection works, wrapper is stateless

---

### Plan 06: DriveThruAgent
**File**: `06-drive-thru-agent.md`
**Dependencies**: Plans 02, 03, 04, 05 (all components)
**Complexity**: Medium

**What it builds**:
- `DriveThruAgent` orchestration class
- Agent instructions and persona
- Component wiring (owns OrderStateManager, receives dependencies)

**Why sixth**: Brings all components together, needs everything from previous plans

**Success Criteria**: E2E tests pass for basic scenarios, agent creates correctly

---

### Plan 07: Integration and Wiring
**File**: `07-integration-and-wiring.md`
**Dependencies**: Plans 01-06 (complete system)
**Complexity**: Medium-High

**What it builds**:
- `DriveThruConfig` in config system
- `DriveThruSessionHandler` for session management
- Console and dev mode commands
- All BDD scenarios as E2E tests (18 scenarios)

**Why seventh**: Integration requires all components working, tests verify end-to-end

**Success Criteria**: All Priority 1 BDD scenarios pass (8/8), 95%+ Priority 2 pass (17+/18)

---

### Plan 08: Accuracy Optimization
**File**: `08-accuracy-optimization.md`
**Dependencies**: Plan 07 (working system with baseline accuracy)
**Complexity**: Medium-High
**Status**: Optional/Future Work

**What it adds**:
- Strategy 3: Explicit Confirmation Loop
- Strategy 5: Semantic Search with Embeddings
- Strategy 7: Chain-of-Thought Prompting
- Strategy 10: Context Window Optimization
- A/B testing framework

**Why last**: Optimization requires baseline to measure against

**Success Criteria**: Accuracy >= 95% (or higher target), optimal strategy identified

---

## How to Use These Plans

### For Sequential Implementation

1. **Start with Plan 01**: Implement pure functions and models
   ```bash
   # Read plan
   cat plan/thoughts/01-menu-models-and-validation.md

   # Implement according to checklist
   # Run tests until all pass
   uv run pytest tests/test_menu_validation.py -v
   ```

2. **Move to Plan 02**: Only start after Plan 01 is complete
   ```bash
   cat plan/thoughts/02-menu-provider.md
   # Implement, test, verify
   ```

3. **Continue sequentially** through Plans 03-08

### For Parallel Work (Multiple Developers)

**Team A** can work on:
- Plan 01 → Plan 02 → Plan 05 (MenuProvider track)

**Team B** can work on:
- Plan 01 → Plan 03 → Plan 04 (State management track)

**Then merge** at Plan 06 (DriveThruAgent)

### For Agent Implementation

Each plan includes:
- ✅ **Clear scope**: Exactly what to build
- ✅ **Implementation checklist**: Step-by-step tasks
- ✅ **Test requirements**: What tests to write
- ✅ **Success criteria**: How to know you're done
- ✅ **BDD mapping**: Which scenarios this plan supports

Agents can implement one plan at a time, verifying completion before moving to the next.

---

## BDD Testing Strategy

All plans map to BDD scenarios defined in `../bdd-testing-strategy.md`:

| BDD Scenario | Implemented In |
|--------------|----------------|
| 1.1 (Order Big Mac) | Plans 01-07 |
| 1.2 (With quantity) | Plans 01-07 |
| 2.1 (Multiple items) | Plans 01-07 |
| 3.1 (With modifiers) | Plans 01, 04-07 |
| 4.1 (Corrections) | Plans 03, 04, 06, 07 |
| 5.1 (Invalid item) | Plans 01, 04, 07 |
| 5.2 (Ambiguous) | Plans 02, 05, 07 |
| 5.4 (STT recovery) | Plans 01, 05, 07 |
| 6.1 (Complete order) | Plans 03, 04, 07 |

All 18 scenarios are fully tested in Plan 07's E2E test suite.

---

## Architecture Principles

Each plan follows these clean architecture principles:

**✓ Single Responsibility Principle (SRP)**
- Each component has one reason to change
- Pure functions separated from stateful components

**✓ Dependency Inversion**
- Components receive dependencies via constructor
- High-level components don't depend on low-level details

**✓ Pure Functions Where Possible**
- Plan 01: All validation functions are pure
- Fast, testable, reusable

**✓ Immutability Reduces Bugs**
- Plan 02: MenuProvider returns immutable data
- Plan 03: OrderStateManager returns copies

**✓ Single Source of Truth**
- Plan 03: OrderStateManager owns ALL order state
- No distributed state

**✓ Tell, Don't Ask**
- Plan 04: Tools tell OrderStateManager what to do
- No query-and-manipulate patterns

**✓ Test Pyramid**
- Many fast unit tests (Plans 01-06)
- Some integration tests (Plans 04-06)
- Few E2E tests (Plan 07)

---

## File Structure After Implementation

```
src/
├── menu_validation.py          # Plan 01
├── menu_provider.py            # Plan 02
├── order_state_manager.py      # Plan 03
├── drive_thru_llm.py          # Plan 05
├── drive_thru_agent.py        # Plan 06
├── session_handler.py         # Plan 07
├── config.py                  # Plan 07 (modified)
├── agent.py                   # Plan 07 (modified)
└── tools/
    └── order_tools.py         # Plan 04

tests/
├── test_menu_validation.py    # Plan 01
├── test_menu_models.py        # Plan 01
├── test_menu_provider.py      # Plan 02
├── test_order_state.py        # Plan 03
├── test_order_tools.py        # Plan 04
├── test_drive_thru_llm.py     # Plan 05
├── test_drive_thru_agent.py   # Plan 06
├── test_bdd_scenarios.py      # Plan 07
└── features/
    ├── steps/
    │   └── agent_steps.py     # Plan 07
    └── agent/
        ├── 01_basic_ordering.feature       # Plan 07
        ├── 02_multi_item_ordering.feature  # Plan 07
        ├── 03_modifiers.feature            # Plan 07
        ├── 04_order_corrections.feature    # Plan 07
        ├── 05_error_handling.feature       # Plan 07
        └── 06_order_completion.feature     # Plan 07

menus/
└── mcdonalds/
    ├── models.py                           # Plan 01 (enhanced)
    └── transformed-data/
        └── menu-structure-2026-01-21.json

orders/
└── {session_id}/
    ├── incremental_log.jsonl  # Plan 03
    └── final_order.json       # Plan 03
```

---

## Testing Checklist

After implementing all plans:

### Unit Tests
- [ ] Plan 01: 22+ tests, <1 second, 100% coverage
- [ ] Plan 02: 20+ tests, <2 seconds, 95%+ coverage
- [ ] Plan 03: 30+ tests, fast in-memory, 95%+ coverage
- [ ] Plan 04: 20+ tests, 90%+ coverage
- [ ] Plan 05: 15+ tests, 90%+ coverage
- [ ] Plan 06: 6+ tests

### Integration Tests
- [ ] Plan 04: Tools + State + Validation work together
- [ ] Plan 06: Agent wiring correct

### E2E BDD Tests
- [ ] Plan 07: All Priority 1 scenarios pass (8/8)
- [ ] Plan 07: 95%+ Priority 2 scenarios pass (17+/18)

### Total Test Count
- Expected: **150+ tests** across all levels
- Test pyramid: ~100 unit, ~30 integration, ~20 E2E

---

## Success Metrics

**After Plan 07 (MVP)**:
- ✅ All components implemented
- ✅ 95%+ BDD scenarios pass
- ✅ Order files generated correctly
- ✅ Console mode works end-to-end
- ✅ ~150+ tests passing

**After Plan 08 (Optimized)**:
- ✅ Accuracy ≥ 95% (or target)
- ✅ Latency < 2 seconds per turn
- ✅ Cost reasonable
- ✅ Optimal strategies identified

---

## Next Steps

1. **Review this breakdown** with team
2. **Start with Plan 01**: Foundation layer
3. **Work sequentially** or in parallel (see above)
4. **Test thoroughly** at each step
5. **Integrate at Plan 07**
6. **Optimize at Plan 08** (if needed)

---

## Questions?

Refer to:
- **Main plan**: `mcdonalds-drive-thru-agent-plan.md` (unchanged reference)
- **BDD strategy**: `../bdd-testing-strategy.md`
- **Individual plans**: `01-*.md` through `08-*.md`
- **Project docs**: `../../AGENTS.md` and `../../README.md`

**Key Principle**: Each plan is self-contained, testable, and verifiable. Build from the bottom up (pure functions → data access → state → coordination → orchestration → integration → optimization).
