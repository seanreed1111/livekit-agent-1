# Plan 06: DriveThruAgent (Agent Orchestration)

**Created**: 2026-01-21
**Status**: Ready for Implementation
**Dependencies**: Plans 01-05 (All components)
**Estimated Complexity**: Medium

---

## Overview

`DriveThruAgent` is the **orchestrator** that brings together all components to create the complete drive-thru order taking agent. It defines the agent's persona, registers tools, and coordinates the conversation flow.

**Key Principles**:
- 🎯 **Orchestration**: Wires components together, doesn't implement logic
- 📝 **Owns State**: Owns OrderStateManager instance (composition)
- 🔧 **Receives Dependencies**: Gets MenuProvider, DriveThruLLM via DI
- 💬 **Defines Persona**: Sets instructions and conversation style

---

## Component Design

### File Structure

**File**: `src/drive_thru_agent.py` (new)

**Dependencies**:
- `livekit.agents` (Agent, Session)
- `src/order_state_manager.py` (OrderStateManager)
- `src/menu_provider.py` (MenuProvider)
- `src/drive_thru_llm.py` (DriveThruLLM)
- `src/tools/order_tools.py` (create_order_tools)

---

## Implementation

### DriveThruAgent Class

```python
from livekit.agents import Agent
from livekit.agents.llm import ChatContext, ChatMessage

class DriveThruAgent:
    """McDonald's drive-thru order taking agent.

    Orchestrates:
    - OrderStateManager (owns instance per session)
    - Tools (created with dependencies)
    - DriveThruLLM (wrapped LLM with context injection)
    - Instructions/persona
    """

    def __init__(
        self,
        session_id: str,
        llm: DriveThruLLM,
        menu_provider: MenuProvider,
        output_dir: str = "orders"
    ) -> None:
        """
        Initialize drive-thru agent.

        Args:
            session_id: Unique session ID
            llm: DriveThruLLM (wrapped LLM)
            menu_provider: MenuProvider for menu access
            output_dir: Directory for order files
        """
        # Create OrderStateManager for this session (agent owns it)
        self._order_state = OrderStateManager(
            session_id=session_id,
            output_dir=output_dir
        )

        # Store dependencies
        self._llm = llm
        self._menu_provider = menu_provider
        self._session_id = session_id

        # Create tools with dependencies injected
        self._tools = create_order_tools(
            order_state=self._order_state,
            menu_provider=self._menu_provider
        )

        # Create LiveKit Agent
        self._agent = Agent(
            llm=self._llm,
            tools=self._tools,
            instructions=self._get_instructions()
        )

    def _get_instructions(self) -> str:
        """Get agent instructions/persona."""
        return """You are a friendly and efficient McDonald's drive-thru order taker.

Your responsibilities:
1. Greet customers warmly when they arrive
2. Listen carefully to their order
3. Use the add_item_to_order function to record each item
4. Confirm each item after adding it
5. When customer is done, use complete_order function
6. Read back the complete order
7. Thank the customer

Guidelines:
- Be concise and natural - avoid overly formal language
- If unsure about an item, ask for clarification
- Always confirm items before adding to order
- Use exact menu item names when confirming
- If customer mentions an item not on the menu, politely inform them
- Be helpful with suggestions if they seem uncertain

Menu Categories:
- Breakfast: Morning items like Egg McMuffin, Hash Browns
- Beef & Pork: Big Mac, Quarter Pounder, burgers
- Chicken & Fish: McNuggets, Filet-O-Fish
- Snacks & Sides: Fries, Apple Slices
- Beverages: Soft drinks
- Coffee & Tea: Hot and iced coffee
- Desserts: Apple Pie, McFlurry
- Smoothies & Shakes

Remember: You have access to the complete menu via your tools. Use them!
"""

    @property
    def agent(self) -> Agent:
        """Get the LiveKit Agent instance."""
        return self._agent

    @property
    def order_state(self) -> OrderStateManager:
        """Get the order state manager (for testing)."""
        return self._order_state

    async def close(self) -> None:
        """Clean up resources."""
        # Could add cleanup logic here if needed
        pass
```

---

## Agent Instructions Design

### Persona Elements

**Tone**: Friendly, efficient, professional
**Style**: Conversational, concise, natural
**Behavior**: Confirming, helpful, patient

### Key Instructions

1. **Greeting**: "Welcome to McDonald's! What can I get for you today?"

2. **Active Listening**: Process customer requests carefully

3. **Tool Usage**: Always use `add_item_to_order` function for adding items

4. **Confirmation**: Confirm each item: "Got it, one Big Mac"

5. **Clarification**: If uncertain: "Just to clarify, did you want..."

6. **Completion**: When done: "Your order is [summary]. [Total] items."

7. **Error Handling**: "I'm sorry, we don't have [item]. Can I suggest [alternative]?"

---

## Testing Strategy

### Unit Tests

**File**: `tests/test_drive_thru_agent.py` (new)

**Test Focus**: Agent initialization and wiring

```python
import pytest
from unittest.mock import Mock

@pytest.fixture
def menu_provider():
    """Real menu provider."""
    return MenuProvider("menus/mcdonalds/transformed-data/menu-structure-2026-01-21.json")

@pytest.fixture
def mock_llm():
    """Mock DriveThruLLM."""
    return Mock(spec=DriveThruLLM)

@pytest.fixture
def drive_thru_agent(mock_llm, menu_provider, tmp_path):
    """Create DriveThruAgent."""
    return DriveThruAgent(
        session_id="test-session",
        llm=mock_llm,
        menu_provider=menu_provider,
        output_dir=str(tmp_path / "orders")
    )
```

**Test Cases**:

1. `test_agent_initialization()` - Agent creates correctly
2. `test_agent_creates_order_state()` - OrderStateManager is created
3. `test_agent_creates_tools()` - Tools are created and registered
4. `test_agent_has_instructions()` - Instructions are set
5. `test_agent_owns_order_state()` - Can access order_state property
6. `test_agent_session_directory_created()` - Session dir exists

### Integration Tests (E2E)

**File**: `tests/test_drive_thru_agent_e2e.py` (new)

**Test Focus**: Complete conversation flows using BDD scenarios

Use LiveKit's testing framework with judge-based evaluation:

```python
@pytest.mark.asyncio
async def test_scenario_1_1_order_big_mac() -> None:
    """
    BDD Scenario 1.1: Customer orders a Big Mac

    Given the agent greets the customer
    When the customer says "I'll have a Big Mac"
    Then the agent confirms "one Big Mac"
    And the agent asks if the customer wants anything else
    When the customer says "that's all"
    Then the agent reads back the complete order
    And the order file contains 1 item
    And the order file shows "Big Mac" in category "Beef & Pork"
    """
    # Create real agent
    menu_provider = MenuProvider("menus/mcdonalds/menu.json")
    base_llm = openai.LLM(model="gpt-4o-mini")
    drive_thru_llm = DriveThruLLM(base_llm, menu_provider)
    agent = DriveThruAgent("test-123", drive_thru_llm, menu_provider)

    # Create judge LLM
    judge_llm = openai.LLM(model="gpt-4o")

    # Run test session
    async with AgentSession(llm=drive_thru_llm) as session:
        await session.start(agent.agent)

        # Customer orders
        result = await session.run(user_input="I'll have a Big Mac")

        # Verify function call
        result.expect.next_event().is_function_call(
            function_name="add_item_to_order",
            arguments={
                "category": "Beef & Pork",
                "item_name": "Big Mac",
                "quantity": 1,
                "modifiers": []
            }
        )

        # Verify confirmation
        await (
            result.expect.next_event()
            .is_message(role="assistant")
            .judge(
                judge_llm,
                intent="Confirms one Big Mac was added and asks if customer wants anything else"
            )
        )

        # End order
        result = await session.run(user_input="that's all")

        # Verify completion
        result.expect.next_event().is_function_call(
            function_name="complete_order"
        )

        # Verify order file
        final_order = agent.order_state.complete_order()
        assert len(final_order["items"]) == 1
        assert final_order["items"][0]["item_name"] == "Big Mac"
        assert final_order["items"][0]["category"] == "Beef & Pork"
```

---

## BDD Scenarios

DriveThruAgent is tested against ALL BDD scenarios from the testing strategy:

**Priority 1** (Must implement):
- Scenario 1.1: Order a Big Mac
- Scenario 1.2: Order with quantity
- Scenario 2.1: Multiple items sequentially
- Scenario 3.1: Item with modifier
- Scenario 5.1: Invalid menu item
- Scenario 5.2: Ambiguous request
- Scenario 6.1: Complete order

**Priority 2** (Should implement):
- All remaining scenarios from bdd-testing-strategy.md

---

## Implementation Checklist

### Phase 1: Basic Structure
- [ ] Create `src/drive_thru_agent.py`
- [ ] Define `DriveThruAgent` class
- [ ] Implement `__init__()` with dependency injection
- [ ] Implement `_get_instructions()` method
- [ ] Add properties: `agent`, `order_state`

### Phase 2: Instructions
- [ ] Write comprehensive agent instructions
- [ ] Define persona and tone
- [ ] Include menu category overview
- [ ] Add tool usage guidelines
- [ ] Add error handling guidelines

### Phase 3: Wiring
- [ ] Create OrderStateManager in constructor
- [ ] Create tools with `create_order_tools()`
- [ ] Create LiveKit Agent with llm, tools, instructions
- [ ] Test that all components wire together

### Phase 4: Unit Tests
- [ ] Create `tests/test_drive_thru_agent.py`
- [ ] Write initialization tests (6 tests)
- [ ] Test dependency wiring
- [ ] Run tests: `uv run pytest tests/test_drive_thru_agent.py -v`

### Phase 5: E2E Tests
- [ ] Create `tests/test_drive_thru_agent_e2e.py`
- [ ] Implement BDD Scenario 1.1 (Big Mac order)
- [ ] Implement BDD Scenario 1.2 (with quantity)
- [ ] Implement BDD Scenario 2.1 (multiple items)
- [ ] Implement BDD Scenario 5.1 (invalid item)
- [ ] Run E2E tests: `uv run pytest tests/test_drive_thru_agent_e2e.py -v`

### Phase 6: Code Quality
- [ ] Add type hints
- [ ] Add docstrings
- [ ] Run formatter: `uv run ruff format src/drive_thru_agent.py`
- [ ] Run linter: `uv run ruff check src/drive_thru_agent.py`

---

## Success Criteria

✅ **Agent initializes correctly** with all dependencies
✅ **Tools are registered** and accessible to LLM
✅ **Instructions are clear** and comprehensive
✅ **E2E tests pass** for Priority 1 BDD scenarios
✅ **Order state is managed** correctly through full conversation
✅ **Type hints complete**
✅ **Docstrings complete**

---

## Dependencies for Next Plans

**This plan provides**:
- ✅ Complete `DriveThruAgent` class
- ✅ Agent orchestration and wiring
- ✅ Comprehensive instructions/persona
- ✅ E2E test framework

**Next plan can now**:
- Wire agent into application
- Test full system integration
- Deploy to production

---

## Design Notes

### Why Agent Owns OrderStateManager?

Agent is responsible for the conversation session, so it owns the session state:
- Creates OrderStateManager for its session
- Passes it to tools
- Can access it for testing/debugging

### Why Dependency Injection?

Agent receives llm and menu_provider instead of creating them:
- Easier to test (can inject mocks)
- Flexible (can use different LLMs)
- Decoupled (agent doesn't know about LLM creation)

### Instructions Design Philosophy

Instructions are:
- **Clear**: Unambiguous about what to do
- **Concise**: Not overwhelming
- **Action-oriented**: Tell agent what to do, not what to think
- **Tool-focused**: Emphasize using functions

**Example Usage**

```python
# App-level setup
menu_provider = MenuProvider("menus/mcdonalds/menu.json")
base_llm = openai.LLM(model="gpt-4o")
drive_thru_llm = DriveThruLLM(base_llm, menu_provider)

# Create agent for session
agent = DriveThruAgent(
    session_id=str(uuid.uuid4()),
    llm=drive_thru_llm,
    menu_provider=menu_provider,
    output_dir="orders"
)

# Use agent in session
async with Session() as session:
    await session.start(agent.agent)
```

**Key Principle**: Agent is the conductor - it orchestrates all components but delegates actual work to specialized components.
