# Plan 03: OrderStateManager (State & Persistence)

**Created**: 2026-01-21
**Status**: Ready for Implementation
**Dependencies**: Plan 01 (OrderItem dataclass)
**Estimated Complexity**: Medium

---

## Overview

The `OrderStateManager` is the **single source of truth** for all order state. Every order mutation (add, remove, update) flows through this component. It handles both in-memory state and persistence (incremental logs + final JSON).

**Key Principles**:
- 🎯 **Single Source of Truth**: ALL order state lives here
- 📝 **Tell, Don't Ask**: Components tell it what to do, don't query and manipulate
- 💾 **Dual Persistence**: Incremental log (append-only) + final JSON (on complete)
- 🔒 **Encapsulation**: Private state, public command/query methods
- ⚡ **Fast Testing**: In-memory operations are fast; file I/O tested separately

---

## Component Design

### File Structure

**File**: `src/order_state_manager.py` (new)

**Dependencies**:
- Standard library: `dataclasses`, `datetime`, `json`, `pathlib`, `uuid`
- No external dependencies (lightweight, fast)

---

## Data Model

### OrderItem Dataclass

```python
from dataclasses import dataclass, field
from datetime import datetime
import uuid

@dataclass
class OrderItem:
    """A single item in an order.

    Represents one line item with all its details.
    Immutable after creation (use update methods on OrderStateManager).
    """

    item_name: str
    category: str
    modifiers: list[str] = field(default_factory=list)
    quantity: int = 1
    item_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "item_id": self.item_id,
            "item_name": self.item_name,
            "category": self.category,
            "modifiers": self.modifiers,
            "quantity": self.quantity,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "OrderItem":
        """Create OrderItem from dictionary."""
        return cls(
            item_id=data["item_id"],
            item_name=data["item_name"],
            category=data["category"],
            modifiers=data.get("modifiers", []),
            quantity=data.get("quantity", 1),
            timestamp=datetime.fromisoformat(data["timestamp"]),
        )
```

---

## Interface Contract

```python
class OrderStateManager:
    """Single source of truth for order state and persistence.

    Manages:
    - In-memory order state (list of OrderItem)
    - Incremental logging (append after each mutation)
    - Final JSON output (on order completion)
    - Session lifecycle

    Thread-safety: NOT thread-safe. Each agent session gets its own instance.
    """

    def __init__(self, session_id: str, output_dir: str = "orders") -> None:
        """
        Initialize order state for a session.

        Args:
            session_id: Unique session identifier (UUID)
            output_dir: Directory to save order files

        Creates:
            - {output_dir}/{session_id}/ directory
            - incremental_log.jsonl file (empty initially)
        """

    # Command Methods (mutations)

    def add_item(
        self,
        item_name: str,
        category: str,
        modifiers: list[str] | None = None,
        quantity: int = 1
    ) -> OrderItem:
        """
        Add item to order.

        Args:
            item_name: Name of the menu item
            category: Menu category
            modifiers: List of modifier names (default: empty list)
            quantity: Number of items (default: 1)

        Returns:
            The created OrderItem

        Side effects:
            - Appends item to in-memory order
            - Appends to incremental log file
        """

    def remove_item(self, item_id: str) -> bool:
        """
        Remove item by ID.

        Args:
            item_id: The UUID of the item to remove

        Returns:
            True if found and removed, False otherwise

        Side effects:
            - Removes item from in-memory order
            - Appends removal event to incremental log
        """

    def update_item_quantity(self, item_id: str, new_quantity: int) -> bool:
        """
        Update quantity for an item.

        Args:
            item_id: The UUID of the item
            new_quantity: New quantity (must be > 0)

        Returns:
            True if found and updated, False otherwise

        Side effects:
            - Updates item quantity in-memory
            - Appends update event to incremental log
        """

    def complete_order(self) -> dict:
        """
        Mark order complete and generate final JSON.

        Returns:
            Final order dictionary

        Side effects:
            - Writes final_order.json file
            - Appends completion event to incremental log
        """

    def clear_order(self) -> None:
        """
        Clear all items (for cancellation/restart).

        Side effects:
            - Clears in-memory order
            - Appends clear event to incremental log
        """

    # Query Methods (read-only)

    def get_items(self) -> list[OrderItem]:
        """
        Get all items in current order (read-only copy).

        Returns:
            List of OrderItem (copies, not references)
        """

    def get_item_by_id(self, item_id: str) -> OrderItem | None:
        """Get a specific item by its ID."""

    def get_total_count(self) -> int:
        """
        Get total number of items (accounting for quantities).

        Example: If order has 2x Big Mac (quantity=2) and 1x Fries (quantity=1),
        returns 3.
        """

    def get_order_summary(self) -> str:
        """
        Get human-readable order summary.

        Returns:
            String like "2 Big Mac, 1 Medium Fries, 1 Coke"
        """

    def is_empty(self) -> bool:
        """Check if order has no items."""

    # Private Methods (implementation details)

    def _append_to_log(self, event: dict) -> None:
        """Append event to incremental log file."""

    def _ensure_session_directory(self) -> None:
        """Create session directory if it doesn't exist."""
```

---

## Implementation Details

### 1. Constructor

```python
def __init__(self, session_id: str, output_dir: str = "orders") -> None:
    """Initialize order state for a session."""
    self._session_id = session_id
    self._output_dir = Path(output_dir)
    self._session_dir = self._output_dir / session_id

    # In-memory state
    self._items: list[OrderItem] = []
    self._start_time = datetime.now()
    self._status = "in_progress"  # or "completed", "cancelled"

    # File paths
    self._incremental_log_path = self._session_dir / "incremental_log.jsonl"
    self._final_order_path = self._session_dir / "final_order.json"

    # Create session directory and empty log file
    self._ensure_session_directory()
```

### 2. Command Methods

#### `add_item()`

```python
def add_item(
    self,
    item_name: str,
    category: str,
    modifiers: list[str] | None = None,
    quantity: int = 1
) -> OrderItem:
    """Add item to order."""
    # Create OrderItem
    item = OrderItem(
        item_name=item_name,
        category=category,
        modifiers=modifiers or [],
        quantity=quantity,
    )

    # Add to in-memory state
    self._items.append(item)

    # Log event
    self._append_to_log({
        "event": "add_item",
        "timestamp": datetime.now().isoformat(),
        "item": item.to_dict(),
    })

    return item
```

#### `remove_item()`

```python
def remove_item(self, item_id: str) -> bool:
    """Remove item by ID."""
    # Find item
    item_to_remove = None
    for item in self._items:
        if item.item_id == item_id:
            item_to_remove = item
            break

    if item_to_remove is None:
        return False

    # Remove from in-memory state
    self._items.remove(item_to_remove)

    # Log event
    self._append_to_log({
        "event": "remove_item",
        "timestamp": datetime.now().isoformat(),
        "item_id": item_id,
        "item_name": item_to_remove.item_name,
    })

    return True
```

#### `complete_order()`

```python
def complete_order(self) -> dict:
    """Mark order complete and generate final JSON."""
    self._status = "completed"

    # Build final order dict
    final_order = {
        "session_id": self._session_id,
        "start_time": self._start_time.isoformat(),
        "completion_time": datetime.now().isoformat(),
        "status": self._status,
        "items": [item.to_dict() for item in self._items],
        "total_items": self.get_total_count(),
        "order_summary": self.get_order_summary(),
    }

    # Write final JSON
    with open(self._final_order_path, "w") as f:
        json.dump(final_order, f, indent=2)

    # Log completion event
    self._append_to_log({
        "event": "complete_order",
        "timestamp": datetime.now().isoformat(),
        "total_items": self.get_total_count(),
    })

    return final_order
```

### 3. Query Methods

#### `get_items()`

```python
def get_items(self) -> list[OrderItem]:
    """Get all items (read-only copy)."""
    # Return copy to prevent external mutations
    return [
        OrderItem(
            item_id=item.item_id,
            item_name=item.item_name,
            category=item.category,
            modifiers=item.modifiers.copy(),  # Copy modifiers list
            quantity=item.quantity,
            timestamp=item.timestamp,
        )
        for item in self._items
    ]
```

#### `get_order_summary()`

```python
def get_order_summary(self) -> str:
    """Get human-readable order summary."""
    if not self._items:
        return "No items"

    # Group items for display
    summary_parts = []
    for item in self._items:
        if item.quantity > 1:
            summary_parts.append(f"{item.quantity} {item.item_name}")
        else:
            summary_parts.append(f"1 {item.item_name}")

    return ", ".join(summary_parts)
```

### 4. Private Methods

#### `_append_to_log()`

```python
def _append_to_log(self, event: dict) -> None:
    """Append event to incremental log file (JSONL format)."""
    with open(self._incremental_log_path, "a") as f:
        f.write(json.dumps(event) + "\n")
```

#### `_ensure_session_directory()`

```python
def _ensure_session_directory(self) -> None:
    """Create session directory if it doesn't exist."""
    self._session_dir.mkdir(parents=True, exist_ok=True)

    # Create empty log file if it doesn't exist
    if not self._incremental_log_path.exists():
        self._incremental_log_path.touch()
```

---

## Testing Strategy

### Unit Tests

**File**: `tests/test_order_state.py` (new)

**Test Organization**:
- In-memory tests (fast, no file I/O)
- File I/O tests (use temp directory)
- Edge case tests

**Test Fixtures**:
```python
import tempfile
import pytest
from pathlib import Path

@pytest.fixture
def temp_output_dir(tmp_path):
    """Create temporary output directory for tests."""
    return str(tmp_path / "orders")

@pytest.fixture
def order_manager(temp_output_dir):
    """Create OrderStateManager with temp directory."""
    return OrderStateManager(
        session_id="test-session-123",
        output_dir=temp_output_dir
    )
```

**Test Cases** (aim for 25+ tests):

#### Construction Tests
1. `test_order_manager_creates_session_directory()`
2. `test_order_manager_creates_empty_log_file()`
3. `test_order_manager_starts_with_empty_order()`

#### Add Item Tests
4. `test_add_item_single_item()`
5. `test_add_item_with_modifiers()`
6. `test_add_item_with_quantity()`
7. `test_add_item_returns_order_item()`
8. `test_add_item_assigns_unique_id()`
9. `test_add_item_appends_to_log()`

#### Remove Item Tests
10. `test_remove_item_by_id_success()`
11. `test_remove_item_by_id_not_found()`
12. `test_remove_item_appends_to_log()`

#### Update Item Tests
13. `test_update_item_quantity_success()`
14. `test_update_item_quantity_not_found()`
15. `test_update_item_quantity_invalid_value()` (quantity <= 0)

#### Query Tests
16. `test_get_items_returns_copies()`
```python
def test_get_items_returns_copies(order_manager):
    """Verify get_items() returns copies, not references."""
    order_manager.add_item("Big Mac", "Beef & Pork")

    items1 = order_manager.get_items()
    items2 = order_manager.get_items()

    # Modify first item
    items1[0].quantity = 999

    # Second call should be unaffected
    assert items2[0].quantity == 1
```

17. `test_get_total_count_single_item()`
18. `test_get_total_count_multiple_quantities()`
```python
def test_get_total_count_multiple_quantities(order_manager):
    """Total count sums quantities."""
    order_manager.add_item("Big Mac", "Beef & Pork", quantity=2)
    order_manager.add_item("Fries", "Snacks & Sides", quantity=1)

    assert order_manager.get_total_count() == 3
```

19. `test_get_order_summary_format()`
20. `test_is_empty_true_and_false()`

#### Complete Order Tests
21. `test_complete_order_writes_final_json()`
```python
def test_complete_order_writes_final_json(order_manager, temp_output_dir):
    """Verify final JSON is written on completion."""
    order_manager.add_item("Big Mac", "Beef & Pork")
    order_manager.add_item("Fries", "Snacks & Sides")

    final_order = order_manager.complete_order()

    # Check return value
    assert final_order["total_items"] == 2
    assert len(final_order["items"]) == 2

    # Check file was created
    final_path = Path(temp_output_dir) / "test-session-123" / "final_order.json"
    assert final_path.exists()

    # Check file contents
    with open(final_path) as f:
        saved_order = json.load(f)
    assert saved_order == final_order
```

22. `test_complete_order_includes_session_info()`
23. `test_complete_order_includes_summary()`

#### Clear Order Tests
24. `test_clear_order_removes_all_items()`
25. `test_clear_order_logs_event()`

#### Incremental Log Tests
26. `test_incremental_log_format_is_jsonl()`
```python
def test_incremental_log_format_is_jsonl(order_manager, temp_output_dir):
    """Verify incremental log is valid JSONL."""
    order_manager.add_item("Big Mac", "Beef & Pork")
    order_manager.add_item("Fries", "Snacks & Sides")
    order_manager.remove_item(order_manager.get_items()[0].item_id)

    log_path = Path(temp_output_dir) / "test-session-123" / "incremental_log.jsonl"

    # Read log
    with open(log_path) as f:
        lines = f.readlines()

    # Should have 3 events: add, add, remove
    assert len(lines) == 3

    # Each line should be valid JSON
    for line in lines:
        event = json.loads(line)
        assert "event" in event
        assert "timestamp" in event
```

27. `test_incremental_log_contains_all_events()`

#### Edge Cases
28. `test_add_item_empty_modifiers_list()`
29. `test_remove_item_from_empty_order()`
30. `test_complete_order_empty_order()`

---

## BDD Scenarios

OrderStateManager supports all BDD scenarios through its state management:

**Related BDD Scenarios**:
- **All scenarios in 01-06** depend on OrderStateManager for state
- **Scenario 1.1** (Order Big Mac) - uses `add_item()`
- **Scenario 2.1** (Multiple items) - uses `add_item()` multiple times
- **Scenario 4.1** (Corrections) - uses `remove_item()` and `add_item()`
- **Scenario 4.3** (Remove item) - uses `remove_item()`
- **Scenario 6.1** (Complete order) - uses `complete_order()`
- **Scenario 6.2** (Cancel order) - uses `clear_order()`

**BDD Step Example**:
```python
@then("the order file contains {n:d} items")
def step_impl(context, n):
    # Load final order JSON
    order_data = load_final_order(context.session_id)
    assert len(order_data["items"]) == n

@then('the order file shows "Big Mac" in category "Beef & Pork"')
def step_impl(context):
    order_data = load_final_order(context.session_id)
    big_mac = next(
        (item for item in order_data["items"] if item["item_name"] == "Big Mac"),
        None
    )
    assert big_mac is not None
    assert big_mac["category"] == "Beef & Pork"
```

---

## Implementation Checklist

### Phase 1: Data Model
- [ ] Create `src/order_state_manager.py`
- [ ] Define `OrderItem` dataclass
- [ ] Implement `OrderItem.to_dict()`
- [ ] Implement `OrderItem.from_dict()`
- [ ] Write tests for OrderItem serialization

### Phase 2: OrderStateManager Skeleton
- [ ] Define `OrderStateManager` class
- [ ] Implement `__init__()` with directory creation
- [ ] Implement `_ensure_session_directory()`
- [ ] Test constructor creates directories correctly

### Phase 3: Command Methods
- [ ] Implement `add_item()`
- [ ] Implement `remove_item()`
- [ ] Implement `update_item_quantity()`
- [ ] Implement `clear_order()`
- [ ] Implement `complete_order()`
- [ ] Test each method individually

### Phase 4: Query Methods
- [ ] Implement `get_items()` (with copy logic)
- [ ] Implement `get_item_by_id()`
- [ ] Implement `get_total_count()`
- [ ] Implement `get_order_summary()`
- [ ] Implement `is_empty()`
- [ ] Test each method individually

### Phase 5: Persistence
- [ ] Implement `_append_to_log()`
- [ ] Wire logging into all command methods
- [ ] Test incremental log format (JSONL)
- [ ] Test final JSON generation
- [ ] Verify log events are correct

### Phase 6: Testing
- [ ] Create `tests/test_order_state.py`
- [ ] Write construction tests (3 tests)
- [ ] Write add item tests (6 tests)
- [ ] Write remove/update tests (5 tests)
- [ ] Write query tests (5 tests)
- [ ] Write complete order tests (3 tests)
- [ ] Write clear order tests (2 tests)
- [ ] Write incremental log tests (2 tests)
- [ ] Write edge case tests (3 tests)
- [ ] Run tests: `uv run pytest tests/test_order_state.py -v`

### Phase 7: Code Quality
- [ ] Add type hints to all methods
- [ ] Add docstrings to all public methods
- [ ] Run formatter: `uv run ruff format src/order_state_manager.py`
- [ ] Run linter: `uv run ruff check src/order_state_manager.py`
- [ ] Check coverage: `uv run pytest --cov=src.order_state_manager`
- [ ] Aim for 95%+ coverage

### Phase 8: Integration Prep
- [ ] Test with realistic session flows
- [ ] Verify incremental log is useful for debugging
- [ ] Verify final JSON has all required fields
- [ ] Document file formats
- [ ] Commit changes

---

## Success Criteria

✅ **All unit tests pass** (30+ tests)
✅ **Fast in-memory tests** (<1 second for non-I/O tests)
✅ **File I/O works correctly** (incremental log + final JSON)
✅ **Returns copies, not references** (encapsulation)
✅ **Single source of truth** (all state in one place)
✅ **Type hints complete** (passes mypy --strict)
✅ **Docstrings complete** (all public methods documented)
✅ **95%+ code coverage**

---

## Dependencies for Next Plans

**This plan provides**:
- ✅ `OrderStateManager` class for state management
- ✅ `OrderItem` dataclass for representing order items
- ✅ Command methods: `add_item()`, `remove_item()`, `update_item_quantity()`, `complete_order()`
- ✅ Query methods: `get_items()`, `get_total_count()`, `get_order_summary()`
- ✅ Persistence: incremental log + final JSON

**Next plans can now use**:
- OrderStateManager for storing order state
- Command methods for tools to mutate state
- Query methods for reading current order
- Session directory structure for file output

---

## Design Notes

### Why Single Source of Truth?

Having all state in OrderStateManager prevents:
- **Inconsistency**: No risk of state being out of sync across components
- **Debugging nightmares**: Always know where to look for state
- **Testing complexity**: Only one component to mock/verify

### Why Command/Query Separation?

Commands (add, remove, update) mutate state and have side effects.
Queries (get_items, get_total_count) are read-only and have no side effects.

This makes the API clear: "Is this going to change something?"

### Why Incremental Logging?

Provides a complete audit trail of the conversation:
- Debug failures: "What did the agent do?"
- Analyze patterns: "What errors are common?"
- Replay sessions: "Re-create the conversation"

### Why Return Copies?

Prevents external code from mutating internal state:
```python
items = order_manager.get_items()
items[0].quantity = 999  # Doesn't affect internal state
```

Trade-off: Small performance cost for big safety win.

---

## Example Usage

```python
# Create manager for a session
order_manager = OrderStateManager(
    session_id="550e8400-e29b-41d4-a716-446655440000",
    output_dir="orders"
)

# Add items
item1 = order_manager.add_item("Big Mac", "Beef & Pork", quantity=2)
item2 = order_manager.add_item("Fries", "Snacks & Sides", modifiers=["No Salt"])

# Query state
print(order_manager.get_order_summary())  # "2 Big Mac, 1 Fries"
print(order_manager.get_total_count())     # 3

# Modify order
order_manager.remove_item(item2.item_id)

# Complete
final_order = order_manager.complete_order()
# Writes: orders/550e8400.../final_order.json
```

**Key Principle**: OrderStateManager owns ALL order state. Other components ask it to make changes; they never manipulate state directly.
