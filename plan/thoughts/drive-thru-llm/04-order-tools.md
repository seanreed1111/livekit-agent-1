# Plan 04: OrderTools (LLM Tool Definitions)

**Created**: 2026-01-21
**Status**: Ready for Implementation
**Dependencies**: Plans 01-03 (OrderStateManager, MenuProvider, menu_validation)
**Estimated Complexity**: Medium

---

## Overview

`OrderTools` is the **coordination layer** between the LLM and our order taking system. It defines LiveKit Tools that the LLM can call via function calling, orchestrating validation → state mutation flow.

**Key Principles**:
- 🎯 **Thin Coordination Layer**: Tools coordinate, don't implement logic
- ✅ **Validate Before Mutate**: Always validate using menu_validation before calling OrderStateManager
- 📞 **Function Calling Interface**: Structured schemas for LLM to call
- 🔄 **Dependency Injection**: Receives OrderStateManager and MenuProvider

---

## Component Design

### File Structure

**File**: `src/tools/order_tools.py` (new)

**Dependencies**:
- `src/order_state_manager.py` (OrderStateManager)
- `src/menu_provider.py` (MenuProvider)
- `src/menu_validation.py` (validation functions)
- `livekit.plugins.openai` (Tool, FunctionContext)

---

## Tools to Implement

### Tool 1: `add_item_to_order`

**Purpose**: Add a menu item to the customer's order

**Schema**:
```python
{
    "type": "function",
    "function": {
        "name": "add_item_to_order",
        "description": "Add a menu item to the customer's order. Always validate the item exists on the menu before adding.",
        "parameters": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "The menu category (e.g., 'Beef & Pork', 'Breakfast', 'Beverages')",
                    "enum": [
                        "Breakfast",
                        "Beef & Pork",
                        "Chicken & Fish",
                        "Salads",
                        "Snacks & Sides",
                        "Desserts",
                        "Beverages",
                        "Coffee & Tea",
                        "Smoothies & Shakes"
                    ]
                },
                "item_name": {
                    "type": "string",
                    "description": "The exact name of the menu item (e.g., 'Big Mac', 'Egg McMuffin')"
                },
                "modifiers": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of modifiers or customizations (e.g., ['No Pickles', 'Extra Sauce'])",
                    "default": []
                },
                "quantity": {
                    "type": "integer",
                    "description": "Number of this item to add",
                    "default": 1,
                    "minimum": 1
                }
            },
            "required": ["category", "item_name"]
        }
    }
}
```

**Implementation Flow**:
```python
async def add_item_to_order(
    ctx: FunctionContext,
    category: str,
    item_name: str,
    modifiers: list[str] | None = None,
    quantity: int = 1
) -> str:
    """Add item to order with validation."""

    # 1. Validate item exists and modifiers are valid
    validation_result = validate_order_item(
        item_name=item_name,
        category=category,
        modifiers=modifiers or [],
        menu_provider=menu_provider,
        fuzzy_threshold=85
    )

    # 2. If invalid, return error message
    if not validation_result.is_valid:
        return f"Sorry, I couldn't add that item: {validation_result.error_message}"

    # 3. If valid, use matched item (might be fuzzy matched)
    matched_item = validation_result.matched_item
    order_state_manager.add_item(
        item_name=matched_item.item_name,  # Use exact match
        category=category,
        modifiers=modifiers or [],
        quantity=quantity
    )

    # 4. Return confirmation
    modifier_text = ""
    if modifiers:
        modifier_text = f" with {', '.join(modifiers)}"

    if quantity > 1:
        return f"Added {quantity} {matched_item.item_name}{modifier_text} to your order."
    else:
        return f"Added one {matched_item.item_name}{modifier_text} to your order."
```

---

### Tool 2: `complete_order`

**Purpose**: Finalize the order and generate output files

**Schema**:
```python
{
    "type": "function",
    "function": {
        "name": "complete_order",
        "description": "Complete the order and generate the final order summary. Call this when the customer says they're done ordering.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}
```

**Implementation Flow**:
```python
async def complete_order(ctx: FunctionContext) -> str:
    """Complete the order."""

    # 1. Check if order is empty
    if order_state_manager.is_empty():
        return "Your order is empty. Would you like to add something?"

    # 2. Complete order (writes final JSON)
    final_order = order_state_manager.complete_order()

    # 3. Return summary
    summary = final_order["order_summary"]
    total_items = final_order["total_items"]

    return f"Order complete! You ordered: {summary}. Total items: {total_items}. Thank you!"
```

---

### Tool 3: `remove_item_from_order` (Optional)

**Purpose**: Remove an item from the order

**Schema**:
```python
{
    "type": "function",
    "function": {
        "name": "remove_item_from_order",
        "description": "Remove an item from the order. Useful when customer wants to cancel an item.",
        "parameters": {
            "type": "object",
            "properties": {
                "item_name": {
                    "type": "string",
                    "description": "Name of the item to remove (e.g., 'Big Mac')"
                }
            },
            "required": ["item_name"]
        }
    }
}
```

**Implementation**:
```python
async def remove_item_from_order(ctx: FunctionContext, item_name: str) -> str:
    """Remove item from order."""

    # Find item by name (use latest item with that name)
    items = order_state_manager.get_items()
    item_to_remove = None

    for item in reversed(items):  # Start from end (most recent)
        if item.item_name.lower() == item_name.lower():
            item_to_remove = item
            break

    if item_to_remove is None:
        return f"I don't see '{item_name}' in your order."

    # Remove item
    success = order_state_manager.remove_item(item_to_remove.item_id)

    if success:
        return f"Removed {item_name} from your order."
    else:
        return f"Couldn't remove {item_name}. Please try again."
```

---

## Factory Function

**Purpose**: Create all tools with dependencies injected

```python
from livekit.plugins.openai import Tool

def create_order_tools(
    order_state: OrderStateManager,
    menu_provider: MenuProvider,
) -> list[Tool]:
    """
    Create LiveKit Tool instances with dependencies injected.

    Args:
        order_state: OrderStateManager instance for this session
        menu_provider: MenuProvider instance (shared singleton)

    Returns:
        List of Tool objects that can be registered with an Agent

    Example:
        tools = create_order_tools(order_state_manager, menu_provider)
        agent = Agent(tools=tools, ...)
    """

    # Closure to capture dependencies
    async def _add_item_to_order(
        ctx: FunctionContext,
        category: str,
        item_name: str,
        modifiers: list[str] | None = None,
        quantity: int = 1
    ) -> str:
        # Implementation here (access order_state and menu_provider from closure)
        ...

    async def _complete_order(ctx: FunctionContext) -> str:
        # Implementation here
        ...

    async def _remove_item_from_order(ctx: FunctionContext, item_name: str) -> str:
        # Implementation here
        ...

    # Create Tool instances
    return [
        Tool(
            name="add_item_to_order",
            description="Add a menu item to the customer's order",
            function=_add_item_to_order,
            # Schema defined separately or inferred from function signature
        ),
        Tool(
            name="complete_order",
            description="Complete the order",
            function=_complete_order,
        ),
        Tool(
            name="remove_item_from_order",
            description="Remove an item from the order",
            function=_remove_item_from_order,
        ),
    ]
```

---

## Testing Strategy

### Integration Tests

**File**: `tests/test_order_tools.py` (new)

**Test Setup**:
```python
import pytest
from unittest.mock import Mock, AsyncMock
from livekit.plugins.openai import FunctionContext

@pytest.fixture
def menu_provider():
    """Real MenuProvider with test menu."""
    return MenuProvider("menus/mcdonalds/transformed-data/menu-structure-2026-01-21.json")

@pytest.fixture
def order_state_manager(tmp_path):
    """OrderStateManager with temp directory."""
    return OrderStateManager(
        session_id="test-session",
        output_dir=str(tmp_path / "orders")
    )

@pytest.fixture
def order_tools(order_state_manager, menu_provider):
    """Create tools with real dependencies."""
    return create_order_tools(order_state_manager, menu_provider)

@pytest.fixture
def mock_ctx():
    """Mock FunctionContext."""
    return Mock(spec=FunctionContext)
```

**Test Cases** (aim for 20+ tests):

#### `add_item_to_order` Tests

1. **Valid item addition**
```python
@pytest.mark.asyncio
async def test_add_item_valid_item(order_tools, order_state_manager, mock_ctx):
    """Adding a valid item succeeds."""
    add_item_tool = order_tools[0]  # add_item_to_order

    result = await add_item_tool.function(
        mock_ctx,
        category="Beef & Pork",
        item_name="Big Mac",
        quantity=1
    )

    # Check response
    assert "Added one Big Mac" in result

    # Check state was updated
    items = order_state_manager.get_items()
    assert len(items) == 1
    assert items[0].item_name == "Big Mac"
```

2. **Valid item with modifiers**
3. **Valid item with quantity > 1**
4. **Fuzzy match success** (e.g., "Big Mack" → "Big Mac")
5. **Invalid item** (e.g., "Whopper")
6. **Invalid modifier**
7. **Wrong category**
8. **Case insensitive item name**

#### `complete_order` Tests

9. **Complete order with items**
```python
@pytest.mark.asyncio
async def test_complete_order_success(order_tools, order_state_manager, mock_ctx):
    """Completing order with items succeeds."""
    add_item_tool = order_tools[0]
    complete_tool = order_tools[1]

    # Add items
    await add_item_tool.function(mock_ctx, "Beef & Pork", "Big Mac")
    await add_item_tool.function(mock_ctx, "Snacks & Sides", "Medium Fries")

    # Complete
    result = await complete_tool.function(mock_ctx)

    assert "Order complete" in result
    assert "Big Mac" in result
    assert "Medium Fries" in result
```

10. **Complete empty order**
11. **Verify final JSON is created**

#### `remove_item_from_order` Tests

12. **Remove existing item**
13. **Remove non-existent item**
14. **Remove from empty order**
15. **Remove specific item when duplicates exist**

#### Edge Cases

16. **Add item with empty modifiers list**
17. **Add item with quantity = 0** (should fail validation)
18. **Add item with very long name**
19. **Concurrent tool calls** (if applicable)

#### Validation Integration

20. **Validation errors are handled gracefully**
```python
@pytest.mark.asyncio
async def test_validation_error_doesnt_mutate_state(order_tools, order_state_manager, mock_ctx):
    """Failed validation doesn't mutate order state."""
    add_item_tool = order_tools[0]

    # Try to add invalid item
    result = await add_item_tool.function(
        mock_ctx,
        category="Beef & Pork",
        item_name="Whopper"  # Invalid
    )

    # Check error message returned
    assert "couldn't add" in result.lower() or "not available" in result.lower()

    # Verify state is unchanged
    assert order_state_manager.is_empty()
```

---

## BDD Scenarios

OrderTools directly supports these BDD scenarios:

**Related BDD Scenarios**:
- **Scenario 1.1** (Order Big Mac) - uses `add_item_to_order` tool
- **Scenario 1.2** (Multiple quantities) - uses `quantity` parameter
- **Scenario 2.1** (Multiple items) - calls `add_item_to_order` multiple times
- **Scenario 3.1** (With modifiers) - uses `modifiers` parameter
- **Scenario 4.1** (Corrections) - uses `remove_item_from_order`
- **Scenario 5.1** (Invalid item) - validation fails, error returned
- **Scenario 6.1** (Complete order) - uses `complete_order` tool

**BDD Step Verification**:
```python
@then("the agent calls the add_item_to_order function")
def step_impl(context):
    # Verify function call was made
    result.expect.next_event().is_function_call(
        function_name="add_item_to_order",
        arguments={
            "category": "Beef & Pork",
            "item_name": "Big Mac",
            "quantity": 1,
            "modifiers": []
        }
    )
```

---

## Implementation Checklist

### Phase 1: Tool Implementation
- [ ] Create `src/tools/` directory
- [ ] Create `src/tools/__init__.py`
- [ ] Create `src/tools/order_tools.py`
- [ ] Define tool schemas (JSON schema or function signatures)
- [ ] Implement `_add_item_to_order()` function
- [ ] Implement `_complete_order()` function
- [ ] Implement `_remove_item_from_order()` function (optional)

### Phase 2: Factory Function
- [ ] Implement `create_order_tools()` factory
- [ ] Use closure to inject dependencies
- [ ] Return list of Tool instances
- [ ] Add type hints and docstrings

### Phase 3: Validation Integration
- [ ] Import validation functions from `menu_validation.py`
- [ ] Call `validate_order_item()` in `_add_item_to_order()`
- [ ] Handle validation errors gracefully
- [ ] Return helpful error messages to LLM

### Phase 4: Testing
- [ ] Create `tests/test_order_tools.py`
- [ ] Write fixtures for tools, state, and menu provider
- [ ] Write add_item tests (8 tests)
- [ ] Write complete_order tests (3 tests)
- [ ] Write remove_item tests (4 tests)
- [ ] Write edge case tests (3 tests)
- [ ] Write validation integration tests (2 tests)
- [ ] Run tests: `uv run pytest tests/test_order_tools.py -v`

### Phase 5: Code Quality
- [ ] Add type hints to all functions
- [ ] Add docstrings to all functions
- [ ] Run formatter: `uv run ruff format src/tools/`
- [ ] Run linter: `uv run ruff check src/tools/`
- [ ] Check coverage: `uv run pytest --cov=src.tools`
- [ ] Aim for 90%+ coverage

### Phase 6: Integration
- [ ] Test tools with mock LLM
- [ ] Verify tool schemas are LLM-friendly
- [ ] Test error message clarity
- [ ] Document tool usage for agent
- [ ] Commit changes

---

## Success Criteria

✅ **All integration tests pass** (20+ tests)
✅ **Tools work with real dependencies** (OrderStateManager, MenuProvider)
✅ **Validation integrated correctly** (invalid items don't mutate state)
✅ **Error messages are helpful** (LLM can understand and relay to user)
✅ **Type hints complete** (passes mypy --strict)
✅ **Docstrings complete** (all public functions documented)
✅ **90%+ code coverage**

---

## Dependencies for Next Plans

**This plan provides**:
- ✅ `create_order_tools()` factory function
- ✅ `add_item_to_order` tool (with validation)
- ✅ `complete_order` tool
- ✅ `remove_item_from_order` tool (optional)
- ✅ Coordination layer between LLM and state management

**Next plans can now use**:
- Tools in agent definition
- Tools for E2E testing
- Tool schemas for LLM prompting

---

## Design Notes

### Why Thin Coordination Layer?

Tools should orchestrate, not implement:
- **Validation logic** lives in `menu_validation.py` (pure functions)
- **State mutations** live in `OrderStateManager` (state owner)
- **Tools** just coordinate: validate → mutate → return result

This keeps tools simple and testable.

### Why Dependency Injection via Closure?

Using closure to capture dependencies:
```python
def create_order_tools(order_state, menu_provider):
    async def _add_item(...):
        # Can access order_state and menu_provider
        ...
    return [Tool(function=_add_item, ...)]
```

Benefits:
- Tools have access to dependencies
- Dependencies can be different per session
- Easy to test with mocks or real instances

### Why Validate Before Mutate?

**Never mutate state unless validation passes.**

This prevents:
- Invalid items in order
- Corrupted state from bad inputs
- Need for rollback logic

Validation is cheap; state corruption is expensive.

### Why Return String Responses?

Tools return strings that the LLM can use to formulate responses:
- "Added one Big Mac to your order."
- "Sorry, I couldn't add that item: Whopper is not on the menu."

This gives LLM context to generate natural responses while maintaining structure.

---

## Example Usage

```python
# Create tools for a session
order_state = OrderStateManager(session_id="abc-123")
menu_provider = MenuProvider("menus/mcdonalds/menu.json")

tools = create_order_tools(order_state, menu_provider)

# Agent uses tools
agent = Agent(
    instructions="You are a drive-thru order taker...",
    tools=tools,
    ...
)

# LLM calls tool
result = await add_item_to_order_tool(
    ctx=...,
    category="Beef & Pork",
    item_name="Big Mac",
    quantity=2
)
# Returns: "Added 2 Big Mac to your order."

# State is updated
assert order_state.get_total_count() == 2
```

**Key Principle**: Tools are the bridge between unstructured LLM output and structured system operations. They validate, coordinate, and provide feedback.
