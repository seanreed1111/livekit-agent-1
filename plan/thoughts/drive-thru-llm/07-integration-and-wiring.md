# Plan 07: Integration and Application Wiring

**Created**: 2026-01-21
**Status**: Ready for Implementation
**Dependencies**: Plans 01-06 (All components complete)
**Estimated Complexity**: Medium-High

---

## Overview

This plan covers **app-level wiring** and **end-to-end integration**. It brings together all components into a working drive-thru agent application, adds configuration, and implements comprehensive E2E testing against all BDD scenarios.

**Key Objectives**:
- 🔌 Wire all components into the main application
- ⚙️ Add configuration for drive-thru agent
- 🧪 Implement all Priority 1 & 2 BDD scenarios as E2E tests
- 🚀 Enable console and dev modes for testing
- ✅ Verify 95%+ accuracy on test suite

---

## 1. Configuration

### Add DriveThruConfig

**File**: `src/config.py` (modify existing)

```python
from pydantic import BaseModel, Field

class DriveThruConfig(BaseModel):
    """Configuration for McDonald's drive-thru agent."""

    # Menu configuration
    menu_file_path: str = Field(
        default="menus/mcdonalds/transformed-data/menu-structure-2026-01-21.json",
        description="Path to menu JSON file"
    )

    # Order output
    orders_output_dir: str = Field(
        default="orders",
        description="Directory to save order files"
    )

    # Accuracy strategies
    fuzzy_match_threshold: int = Field(
        default=85,
        description="Minimum fuzzy match score (0-100) for item names",
        ge=0,
        le=100
    )

    max_context_items: int = Field(
        default=50,
        description="Maximum number of menu items to inject into LLM context",
        ge=10,
        le=100
    )

    # Feature flags
    enable_confirmation_loop: bool = Field(
        default=True,
        description="Require confirmation before adding items"
    )

    enable_semantic_search: bool = Field(
        default=False,
        description="Use embeddings for semantic item search (future)"
    )


class Config(BaseModel):
    """Root configuration (extend existing)."""
    # ... existing fields ...

    # Add drive-thru config
    drive_thru: DriveThruConfig = Field(
        default_factory=DriveThruConfig,
        description="Drive-thru agent configuration"
    )
```

---

## 2. Application Wiring

### Session Handler

**File**: `src/session_handler.py` (modify or create new)

```python
from uuid import uuid4
from livekit.agents import Session
from src.drive_thru_agent import DriveThruAgent
from src.drive_thru_llm import DriveThruLLM
from src.menu_provider import MenuProvider
from src.config import Config

class DriveThruSessionHandler:
    """Handles creation of drive-thru agent sessions."""

    def __init__(self, config: Config):
        """Initialize session handler with config."""
        self.config = config

        # Create shared MenuProvider (singleton - loaded once)
        self.menu_provider = MenuProvider(
            config.drive_thru.menu_file_path
        )

    async def create_agent(self, session_id: str) -> DriveThruAgent:
        """Create a new DriveThruAgent for a session."""

        # Create base LLM (from config)
        from src.factories import create_llm
        base_llm = create_llm(self.config)

        # Wrap with DriveThruLLM
        drive_thru_llm = DriveThruLLM(
            wrapped_llm=base_llm,
            menu_provider=self.menu_provider,
            max_context_items=self.config.drive_thru.max_context_items
        )

        # Create DriveThruAgent
        agent = DriveThruAgent(
            session_id=session_id,
            llm=drive_thru_llm,
            menu_provider=self.menu_provider,
            output_dir=self.config.drive_thru.orders_output_dir
        )

        return agent
```

### Main Application

**File**: `src/agent.py` (modify existing)

Add drive-thru mode option:

```python
import click
from src.session_handler import DriveThruSessionHandler

@click.group()
def cli():
    """McDonald's Drive-Thru Agent CLI."""
    pass

@cli.command()
def console():
    """Run drive-thru agent in console mode (for testing)."""
    # Load config
    config = load_config()

    # Create session handler
    handler = DriveThruSessionHandler(config)

    # Create agent
    session_id = str(uuid4())
    agent = await handler.create_agent(session_id)

    # Run console session
    async with Console(agent.agent) as console:
        await console.run()

@cli.command()
def dev():
    """Run drive-thru agent in dev mode."""
    # Similar to console but with LiveKit connection
    config = load_config()
    handler = DriveThruSessionHandler(config)

    # Create app
    app = DriveThruApp(handler, config)
    app.run()

# ... existing commands ...

if __name__ == "__main__":
    cli()
```

---

## 3. BDD Test Implementation

### Feature Files

**Directory**: `tests/features/agent/`

Create actual Gherkin feature files based on `plan/bdd-testing-strategy.md`:

**File**: `tests/features/agent/01_basic_ordering.feature`

```gherkin
@voice-agent @order-taking @priority-1
Feature: Basic Single-Item Ordering
  As a McDonald's customer
  I want to order a single menu item
  So that I can quickly get my food

  Background:
    Given the McDonald's menu is loaded
    And the agent is ready to take orders

  @smoke
  Scenario: Customer orders a Big Mac
    Given the agent greets the customer
    When the customer says "I'll have a Big Mac"
    Then the agent confirms "one Big Mac"
    And the agent asks if the customer wants anything else
    When the customer says "that's all"
    Then the agent reads back the complete order
    And a final order JSON file is created
    And the order file contains 1 item
    And the order file shows "Big Mac" in category "Beef & Pork"
    And the item has quantity 1

  @quantities
  Scenario: Customer orders multiple Big Macs
    Given the agent greets the customer
    When the customer says "Two Big Macs please"
    Then the agent confirms "two Big Macs"
    When the customer says "no thanks"
    Then the order file contains 1 line item
    And the line item has quantity 2
```

**(Similar files for 02-06 features)**

### Step Definitions

**File**: `tests/features/steps/agent_steps.py`

```python
import pytest
from behave import given, when, then
from livekit.agents.testing import AgentSession
import json
from pathlib import Path

# Setup steps

@given("the McDonald's menu is loaded")
def step_menu_loaded(context):
    """Load menu provider."""
    from src.menu_provider import MenuProvider
    context.menu_provider = MenuProvider(
        "menus/mcdonalds/transformed-data/menu-structure-2026-01-21.json"
    )

@given("the agent is ready to take orders")
async def step_agent_ready(context):
    """Create and start agent."""
    from src.drive_thru_agent import DriveThruAgent
    from src.drive_thru_llm import DriveThruLLM
    from livekit.plugins import openai

    # Create components
    base_llm = openai.LLM(model="gpt-4o-mini")
    drive_thru_llm = DriveThruLLM(base_llm, context.menu_provider)

    session_id = f"test-{uuid4()}"
    agent = DriveThruAgent(
        session_id=session_id,
        llm=drive_thru_llm,
        menu_provider=context.menu_provider,
        output_dir="test_orders"
    )

    # Store for later steps
    context.agent = agent
    context.session_id = session_id

    # Start session
    context.session = AgentSession(llm=drive_thru_llm)
    await context.session.start(agent.agent)

@given("the agent greets the customer")
async def step_agent_greets(context):
    """Agent sends greeting."""
    # Wait for initial greeting
    result = await context.session.wait_for_message()
    # Store result for verification if needed
    context.last_result = result

# Action steps

@when('the customer says "{utterance}"')
async def step_customer_says(context, utterance):
    """Customer speaks."""
    context.last_result = await context.session.run(user_input=utterance)

# Verification steps

@then('the agent confirms "{text}"')
async def step_agent_confirms(context, text):
    """Verify agent confirmed something."""
    from livekit.plugins import openai
    judge_llm = openai.LLM(model="gpt-4o")

    await (
        context.last_result.expect.next_event()
        .is_message(role="assistant")
        .judge(
            judge_llm,
            intent=f"Confirms {text} was added to the order"
        )
    )

@then("the agent asks if the customer wants anything else")
async def step_agent_asks_more(context):
    """Verify agent asks for more items."""
    # Use judge to verify intent
    from livekit.plugins import openai
    judge_llm = openai.LLM(model="gpt-4o")

    await (
        context.last_result.expect.next_event()
        .is_message(role="assistant")
        .judge(
            judge_llm,
            intent="Asks if customer wants anything else or is done ordering"
        )
    )

@then("a final order JSON file is created")
def step_final_json_created(context):
    """Verify final order JSON exists."""
    order_path = Path("test_orders") / context.session_id / "final_order.json"
    assert order_path.exists(), f"Final order JSON not found at {order_path}"

@then("the order file contains {n:d} item")
@then("the order file contains {n:d} items")
def step_order_contains_items(context, n):
    """Verify number of items."""
    order_path = Path("test_orders") / context.session_id / "final_order.json"
    with open(order_path) as f:
        order_data = json.load(f)

    assert len(order_data["items"]) == n

@then('the order file shows "{item_name}" in category "{category}"')
def step_order_shows_item_in_category(context, item_name, category):
    """Verify specific item in order."""
    order_path = Path("test_orders") / context.session_id / "final_order.json"
    with open(order_path) as f:
        order_data = json.load(f)

    # Find item
    item = next(
        (i for i in order_data["items"] if i["item_name"] == item_name),
        None
    )

    assert item is not None, f"{item_name} not found in order"
    assert item["category"] == category

@then("the item has quantity {quantity:d}")
@then("the line item has quantity {quantity:d}")
def step_item_has_quantity(context, quantity):
    """Verify item quantity."""
    order_path = Path("test_orders") / context.session_id / "final_order.json"
    with open(order_path) as f:
        order_data = json.load(f)

    # Check first item (or last added item)
    assert order_data["items"][0]["quantity"] == quantity
```

### Test Runner

**File**: `tests/test_bdd_scenarios.py`

```python
"""Run BDD scenarios using pytest-bdd."""
import pytest
from pytest_bdd import scenarios

# Load all feature files
scenarios('features/agent/01_basic_ordering.feature')
scenarios('features/agent/02_multi_item_ordering.feature')
scenarios('features/agent/03_modifiers.feature')
scenarios('features/agent/04_order_corrections.feature')
scenarios('features/agent/05_error_handling.feature')
scenarios('features/agent/06_order_completion.feature')

# Step definitions are auto-discovered from features/steps/
```

---

## 4. Testing Strategy

### Test Levels

1. **Unit Tests** (Plans 01-06) - Fast, isolated, comprehensive
   - Already implemented in previous plans
   - ~100+ tests across all components

2. **Integration Tests** (Plans 04-06) - Component interactions
   - Tools + State + Validation
   - Agent wiring

3. **E2E BDD Tests** (This plan) - Full conversation flows
   - All Priority 1 scenarios (8 scenarios)
   - All Priority 2 scenarios (18 total scenarios)

### Running Tests

```bash
# Run all tests
uv run pytest

# Run unit tests only (fast)
uv run pytest tests/test_*.py -v

# Run BDD scenarios only
uv run pytest tests/test_bdd_scenarios.py -v

# Run specific feature
uv run pytest tests/test_bdd_scenarios.py -k "basic_ordering"

# Run with coverage
uv run pytest --cov=src --cov-report=html
```

---

## Implementation Checklist

### Phase 1: Configuration
- [ ] Add `DriveThruConfig` to `src/config.py`
- [ ] Add drive_thru field to root Config
- [ ] Test config loading

### Phase 2: Session Handler
- [ ] Create `DriveThruSessionHandler`
- [ ] Implement `create_agent()` method
- [ ] Create singleton MenuProvider
- [ ] Test session creation

### Phase 3: App Wiring
- [ ] Modify `src/agent.py` to support drive-thru mode
- [ ] Add console command for drive-thru
- [ ] Add dev command for drive-thru
- [ ] Test console mode manually

### Phase 4: BDD Feature Files
- [ ] Create `tests/features/agent/` directory
- [ ] Write 01_basic_ordering.feature (3 scenarios)
- [ ] Write 02_multi_item_ordering.feature (3 scenarios)
- [ ] Write 03_modifiers.feature (4 scenarios)
- [ ] Write 04_order_corrections.feature (3 scenarios)
- [ ] Write 05_error_handling.feature (4 scenarios)
- [ ] Write 06_order_completion.feature (3 scenarios)

### Phase 5: Step Definitions
- [ ] Create `tests/features/steps/` directory
- [ ] Implement Given steps (setup)
- [ ] Implement When steps (actions)
- [ ] Implement Then steps (assertions)
- [ ] Use judge-based assertions for natural language
- [ ] Use direct assertions for file/state checks

### Phase 6: Test Execution
- [ ] Install pytest-bdd: `uv add --dev pytest-bdd`
- [ ] Create `tests/test_bdd_scenarios.py`
- [ ] Run Priority 1 scenarios (8 scenarios)
- [ ] Fix any failures
- [ ] Run Priority 2 scenarios (18 total)
- [ ] Measure accuracy: target 95%+ pass rate

### Phase 7: Accuracy Measurement
- [ ] Track metrics: item accuracy, modifier accuracy, order completeness
- [ ] Identify failure patterns
- [ ] Iterate on prompts/validation if needed
- [ ] Document accuracy results

### Phase 8: Integration Testing
- [ ] Test console mode end-to-end
- [ ] Test dev mode end-to-end
- [ ] Verify file outputs (incremental log + final JSON)
- [ ] Test with various order complexities

---

## Success Criteria

✅ **All components wire together** correctly
✅ **Configuration works** (can load drive-thru config)
✅ **Console mode works** (can test locally)
✅ **All Priority 1 BDD scenarios pass** (8/8)
✅ **95%+ Priority 2 scenarios pass** (17+/18)
✅ **Order files generated correctly** (incremental log + final JSON)
✅ **Accuracy targets met** (95%+ item accuracy)
✅ **No regressions** (all unit tests still pass)

---

## Dependencies for Next Plan

**This plan provides**:
- ✅ Complete working application
- ✅ BDD test suite for validation
- ✅ Baseline accuracy measurement
- ✅ Configuration system

**Next plan (Plan 08) can now**:
- Optimize accuracy strategies
- A/B test different approaches
- Add advanced features

---

## Design Notes

### Why Singleton MenuProvider?

MenuProvider is loaded once at app startup:
- Saves memory (only one copy of 212-item menu)
- Saves time (no repeated file I/O)
- Thread-safe (read-only)
- Shared across all sessions

### Why Session-Specific OrderStateManager?

Each conversation gets its own OrderStateManager:
- Isolated state (no cross-contamination)
- Easy cleanup (one session = one directory)
- Testable (each test gets fresh state)

### BDD as Acceptance Tests

BDD scenarios serve as:
- Acceptance criteria (defines "done")
- Regression tests (prevents breakage)
- Documentation (shows how system works)
- Communication tool (between devs and stakeholders)

**Key Principle**: Integration brings components to life. A well-integrated system is greater than the sum of its parts.
