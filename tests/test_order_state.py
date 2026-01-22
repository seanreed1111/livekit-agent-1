"""Tests for OrderStateManager and OrderItem.

This test module covers:
- OrderItem serialization/deserialization
- OrderStateManager construction
- Command methods (add, remove, update, clear, complete)
- Query methods (get_items, get_total_count, get_order_summary, etc.)
- File I/O (incremental log, final JSON)
- Edge cases
"""

import json
from datetime import datetime
from pathlib import Path

from src.order_state_manager import OrderItem

# ============================================================================
# OrderItem Tests
# ============================================================================


def test_order_item_to_dict():
    """Test OrderItem serialization to dictionary."""
    item = OrderItem(
        item_name="Big Mac",
        category="Beef & Pork",
        modifiers=["No Pickles", "Extra Sauce"],
        quantity=2,
    )

    result = item.to_dict()

    assert result["item_name"] == "Big Mac"
    assert result["category"] == "Beef & Pork"
    assert result["modifiers"] == ["No Pickles", "Extra Sauce"]
    assert result["quantity"] == 2
    assert "item_id" in result
    assert "timestamp" in result


def test_order_item_from_dict():
    """Test OrderItem deserialization from dictionary."""
    data = {
        "item_id": "test-id-123",
        "item_name": "Quarter Pounder",
        "category": "Beef & Pork",
        "modifiers": ["Cheese"],
        "quantity": 1,
        "timestamp": "2026-01-21T10:30:00",
    }

    item = OrderItem.from_dict(data)

    assert item.item_id == "test-id-123"
    assert item.item_name == "Quarter Pounder"
    assert item.category == "Beef & Pork"
    assert item.modifiers == ["Cheese"]
    assert item.quantity == 1
    assert isinstance(item.timestamp, datetime)


def test_order_item_roundtrip():
    """Test OrderItem serialization roundtrip (to_dict -> from_dict)."""
    original = OrderItem(
        item_name="McChicken",
        category="Chicken & Fish",
        modifiers=[],
        quantity=3,
    )

    # Serialize and deserialize
    data = original.to_dict()
    restored = OrderItem.from_dict(data)

    assert restored.item_name == original.item_name
    assert restored.category == original.category
    assert restored.modifiers == original.modifiers
    assert restored.quantity == original.quantity


# ============================================================================
# Construction Tests
# ============================================================================


def test_order_manager_creates_session_directory(order_manager, temp_output_dir):
    """Test that OrderStateManager creates session directory on init."""
    session_dir = Path(temp_output_dir) / "test-session-123"
    assert session_dir.exists()
    assert session_dir.is_dir()


def test_order_manager_creates_empty_log_file(order_manager, temp_output_dir):
    """Test that OrderStateManager creates empty incremental log file."""
    log_file = Path(temp_output_dir) / "test-session-123" / "incremental_log.jsonl"
    assert log_file.exists()
    assert log_file.read_text() == ""


def test_order_manager_starts_with_empty_order(order_manager):
    """Test that OrderStateManager initializes with no items."""
    assert order_manager.is_empty()
    assert order_manager.get_total_count() == 0
    assert order_manager.get_items() == []


# ============================================================================
# Add Item Tests
# ============================================================================


def test_add_item_single_item(order_manager):
    """Test adding a single item to order."""
    item = order_manager.add_item("Big Mac", "Beef & Pork")

    assert item.item_name == "Big Mac"
    assert item.category == "Beef & Pork"
    assert order_manager.get_total_count() == 1
    assert not order_manager.is_empty()


def test_add_item_with_modifiers(order_manager):
    """Test adding item with modifiers."""
    item = order_manager.add_item(
        "Big Mac", "Beef & Pork", modifiers=["No Pickles", "Extra Sauce"]
    )

    assert item.modifiers == ["No Pickles", "Extra Sauce"]
    items = order_manager.get_items()
    assert items[0].modifiers == ["No Pickles", "Extra Sauce"]


def test_add_item_with_quantity(order_manager):
    """Test adding item with quantity > 1."""
    item = order_manager.add_item("Fries", "Snacks & Sides", quantity=3)

    assert item.quantity == 3
    assert order_manager.get_total_count() == 3


def test_add_item_returns_order_item(order_manager):
    """Test that add_item returns OrderItem instance."""
    item = order_manager.add_item("Big Mac", "Beef & Pork")

    assert isinstance(item, OrderItem)
    assert hasattr(item, "item_id")
    assert hasattr(item, "timestamp")


def test_add_item_assigns_unique_id(order_manager):
    """Test that each item gets a unique ID."""
    item1 = order_manager.add_item("Big Mac", "Beef & Pork")
    item2 = order_manager.add_item("Big Mac", "Beef & Pork")

    assert item1.item_id != item2.item_id


def test_add_item_appends_to_log(order_manager, temp_output_dir):
    """Test that add_item appends event to incremental log."""
    order_manager.add_item("Big Mac", "Beef & Pork")

    log_file = Path(temp_output_dir) / "test-session-123" / "incremental_log.jsonl"
    with open(log_file) as f:
        lines = f.readlines()

    assert len(lines) == 1
    event = json.loads(lines[0])
    assert event["event"] == "add_item"
    assert event["item"]["item_name"] == "Big Mac"


# ============================================================================
# Remove Item Tests
# ============================================================================


def test_remove_item_by_id_success(order_manager):
    """Test removing item by ID when it exists."""
    item = order_manager.add_item("Big Mac", "Beef & Pork")
    item_id = item.item_id

    result = order_manager.remove_item(item_id)

    assert result is True
    assert order_manager.is_empty()
    assert order_manager.get_total_count() == 0


def test_remove_item_by_id_not_found(order_manager):
    """Test removing item by ID when it doesn't exist."""
    result = order_manager.remove_item("non-existent-id")

    assert result is False


def test_remove_item_appends_to_log(order_manager, temp_output_dir):
    """Test that remove_item appends event to incremental log."""
    item = order_manager.add_item("Big Mac", "Beef & Pork")
    order_manager.remove_item(item.item_id)

    log_file = Path(temp_output_dir) / "test-session-123" / "incremental_log.jsonl"
    with open(log_file) as f:
        lines = f.readlines()

    assert len(lines) == 2  # add + remove
    remove_event = json.loads(lines[1])
    assert remove_event["event"] == "remove_item"
    assert remove_event["item_id"] == item.item_id


# ============================================================================
# Update Item Quantity Tests
# ============================================================================


def test_update_item_quantity_success(order_manager):
    """Test updating item quantity when item exists."""
    item = order_manager.add_item("Big Mac", "Beef & Pork", quantity=1)

    result = order_manager.update_item_quantity(item.item_id, 3)

    assert result is True
    updated_item = order_manager.get_item_by_id(item.item_id)
    assert updated_item.quantity == 3
    assert order_manager.get_total_count() == 3


def test_update_item_quantity_not_found(order_manager):
    """Test updating quantity for non-existent item."""
    result = order_manager.update_item_quantity("non-existent-id", 5)

    assert result is False


def test_update_item_quantity_invalid_value(order_manager):
    """Test updating quantity to invalid value (0 or negative)."""
    item = order_manager.add_item("Big Mac", "Beef & Pork", quantity=2)

    result_zero = order_manager.update_item_quantity(item.item_id, 0)
    result_negative = order_manager.update_item_quantity(item.item_id, -1)

    assert result_zero is False
    assert result_negative is False
    # Original quantity should be unchanged
    assert order_manager.get_item_by_id(item.item_id).quantity == 2


# ============================================================================
# Query Method Tests
# ============================================================================


def test_get_items_returns_copies(order_manager):
    """Verify get_items() returns copies, not references."""
    order_manager.add_item("Big Mac", "Beef & Pork")

    items1 = order_manager.get_items()
    items2 = order_manager.get_items()

    # Modify first item
    items1[0].quantity = 999

    # Second call should be unaffected
    assert items2[0].quantity == 1


def test_get_total_count_single_item(order_manager):
    """Test total count with single item."""
    order_manager.add_item("Big Mac", "Beef & Pork", quantity=1)

    assert order_manager.get_total_count() == 1


def test_get_total_count_multiple_quantities(order_manager):
    """Total count sums quantities."""
    order_manager.add_item("Big Mac", "Beef & Pork", quantity=2)
    order_manager.add_item("Fries", "Snacks & Sides", quantity=1)

    assert order_manager.get_total_count() == 3


def test_get_order_summary_format(order_manager):
    """Test order summary format."""
    order_manager.add_item("Big Mac", "Beef & Pork", quantity=2)
    order_manager.add_item("Fries", "Snacks & Sides", quantity=1)

    summary = order_manager.get_order_summary()

    assert summary == "2 Big Mac, 1 Fries"


def test_is_empty_true_and_false(order_manager):
    """Test is_empty() returns correct values."""
    assert order_manager.is_empty() is True

    order_manager.add_item("Big Mac", "Beef & Pork")
    assert order_manager.is_empty() is False


def test_get_item_by_id_found(order_manager):
    """Test get_item_by_id when item exists."""
    item = order_manager.add_item("Big Mac", "Beef & Pork")

    found_item = order_manager.get_item_by_id(item.item_id)

    assert found_item is not None
    assert found_item.item_name == "Big Mac"
    assert found_item.item_id == item.item_id


def test_get_item_by_id_not_found(order_manager):
    """Test get_item_by_id when item doesn't exist."""
    result = order_manager.get_item_by_id("non-existent-id")

    assert result is None


# ============================================================================
# Complete Order Tests
# ============================================================================


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


def test_complete_order_includes_session_info(order_manager):
    """Test that complete_order includes session metadata."""
    order_manager.add_item("Big Mac", "Beef & Pork")

    final_order = order_manager.complete_order()

    assert final_order["session_id"] == "test-session-123"
    assert "start_time" in final_order
    assert "completion_time" in final_order
    assert final_order["status"] == "completed"


def test_complete_order_includes_summary(order_manager):
    """Test that complete_order includes order summary."""
    order_manager.add_item("Big Mac", "Beef & Pork", quantity=2)
    order_manager.add_item("Fries", "Snacks & Sides")

    final_order = order_manager.complete_order()

    assert final_order["order_summary"] == "2 Big Mac, 1 Fries"
    assert final_order["total_items"] == 3


# ============================================================================
# Clear Order Tests
# ============================================================================


def test_clear_order_removes_all_items(order_manager):
    """Test that clear_order removes all items."""
    order_manager.add_item("Big Mac", "Beef & Pork")
    order_manager.add_item("Fries", "Snacks & Sides")

    order_manager.clear_order()

    assert order_manager.is_empty()
    assert order_manager.get_total_count() == 0


def test_clear_order_logs_event(order_manager, temp_output_dir):
    """Test that clear_order appends event to log."""
    order_manager.add_item("Big Mac", "Beef & Pork")
    order_manager.clear_order()

    log_file = Path(temp_output_dir) / "test-session-123" / "incremental_log.jsonl"
    with open(log_file) as f:
        lines = f.readlines()

    assert len(lines) == 2  # add + clear
    clear_event = json.loads(lines[1])
    assert clear_event["event"] == "clear_order"


# ============================================================================
# Incremental Log Tests
# ============================================================================


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


def test_incremental_log_contains_all_events(order_manager, temp_output_dir):
    """Test that all events are logged in order."""
    order_manager.add_item("Big Mac", "Beef & Pork")
    item = order_manager.add_item("Fries", "Snacks & Sides", quantity=1)
    order_manager.update_item_quantity(item.item_id, 2)
    order_manager.complete_order()

    log_path = Path(temp_output_dir) / "test-session-123" / "incremental_log.jsonl"

    with open(log_path) as f:
        lines = f.readlines()

    events = [json.loads(line) for line in lines]
    event_types = [e["event"] for e in events]

    assert event_types == ["add_item", "add_item", "update_quantity", "complete_order"]


# ============================================================================
# Edge Case Tests
# ============================================================================


def test_add_item_empty_modifiers_list(order_manager):
    """Test adding item with None modifiers (should default to empty list)."""
    item = order_manager.add_item("Big Mac", "Beef & Pork", modifiers=None)

    assert item.modifiers == []


def test_remove_item_from_empty_order(order_manager):
    """Test removing item from empty order."""
    result = order_manager.remove_item("some-id")

    assert result is False


def test_complete_order_empty_order(order_manager, temp_output_dir):
    """Test completing an empty order."""
    final_order = order_manager.complete_order()

    assert final_order["total_items"] == 0
    assert final_order["items"] == []
    assert final_order["order_summary"] == "No items"

    # Check file was still created
    final_path = Path(temp_output_dir) / "test-session-123" / "final_order.json"
    assert final_path.exists()


def test_get_order_summary_empty_order(order_manager):
    """Test order summary for empty order."""
    summary = order_manager.get_order_summary()

    assert summary == "No items"
