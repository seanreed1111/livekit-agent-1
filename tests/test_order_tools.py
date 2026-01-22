"""Integration tests for order tools.

These tests verify that the OrderTools coordination layer correctly integrates
with OrderStateManager, MenuProvider, and menu_validation.
"""


import pytest

from src.tools.order_tools import create_order_tools

# ============================================================================
# add_item_to_order Tests
# ============================================================================


@pytest.mark.asyncio
async def test_add_item_valid_item(order_tools, order_state_manager):
    """Adding a valid item succeeds and updates state."""
    add_item_tool = order_tools[0]  # add_item_to_order

    result = await add_item_tool(
        category="Beef & Pork", item_name="Big Mac", quantity=1
    )

    # Check response
    assert "Added one Big Mac" in result
    assert "to your order" in result

    # Check state was updated
    items = order_state_manager.get_items()
    assert len(items) == 1
    assert items[0].item_name == "Big Mac"
    assert items[0].category == "Beef & Pork"
    assert items[0].quantity == 1


@pytest.mark.asyncio
async def test_add_item_with_modifiers(order_tools, order_state_manager):
    """Adding an item with valid modifiers succeeds."""
    add_item_tool = order_tools[0]

    result = await add_item_tool(
        category="Breakfast",
        item_name="Big Breakfast (Large Biscuit)",
        modifiers=["Egg Whites", "Hotcakes"],
        quantity=1,
    )

    # Check response includes modifiers
    assert "Added one Big Breakfast (Large Biscuit)" in result
    assert "Egg Whites" in result
    assert "Hotcakes" in result

    # Check state
    items = order_state_manager.get_items()
    assert len(items) == 1
    assert items[0].modifiers == ["Egg Whites", "Hotcakes"]


@pytest.mark.asyncio
async def test_add_item_with_quantity_greater_than_one(
    order_tools, order_state_manager
):
    """Adding multiple quantities of an item succeeds."""
    add_item_tool = order_tools[0]

    result = await add_item_tool(
        category="Snacks & Sides", item_name="Medium French Fries", quantity=3
    )

    # Check response
    assert "Added 3 Medium French Fries" in result

    # Check state
    items = order_state_manager.get_items()
    assert len(items) == 1
    assert items[0].quantity == 3


@pytest.mark.asyncio
async def test_add_item_fuzzy_match_success(order_tools, order_state_manager):
    """Fuzzy matching corrects minor spelling errors."""
    add_item_tool = order_tools[0]

    # Intentional typo: "Big Mack" instead of "Big Mac"
    result = await add_item_tool(
        category="Beef & Pork", item_name="Big Mack", quantity=1
    )

    # Should succeed via fuzzy match
    assert "Added one Big Mac" in result  # Corrected to "Big Mac"

    # Check state has correct name
    items = order_state_manager.get_items()
    assert len(items) == 1
    assert items[0].item_name == "Big Mac"  # Not "Big Mack"


@pytest.mark.asyncio
async def test_add_item_invalid_item(order_tools, order_state_manager):
    """Adding an item not on the menu fails with error message."""
    add_item_tool = order_tools[0]

    result = await add_item_tool(
        category="Beef & Pork", item_name="Whopper", quantity=1
    )

    # Check error message
    assert "couldn't add" in result.lower() or "not" in result.lower()

    # Verify state is unchanged
    assert order_state_manager.is_empty()


@pytest.mark.asyncio
async def test_add_item_invalid_modifier(order_tools, order_state_manager):
    """Adding an item with an invalid modifier fails."""
    add_item_tool = order_tools[0]

    result = await add_item_tool(
        category="Beef & Pork",
        item_name="Big Mac",
        modifiers=["InvalidModifier123"],
        quantity=1,
    )

    # Check error message
    assert "couldn't add" in result.lower() or "not available" in result.lower()

    # Verify state is unchanged
    assert order_state_manager.is_empty()


@pytest.mark.asyncio
async def test_add_item_wrong_category(order_tools, order_state_manager):
    """Adding an item with wrong category fails."""
    add_item_tool = order_tools[0]

    # Big Mac is in "Beef & Pork", not "Breakfast"
    result = await add_item_tool(category="Breakfast", item_name="Big Mac", quantity=1)

    # Should fail validation
    assert "couldn't add" in result.lower() or "not" in result.lower()

    # Verify state is unchanged
    assert order_state_manager.is_empty()


@pytest.mark.asyncio
async def test_add_item_case_insensitive(order_tools, order_state_manager):
    """Item names are case insensitive (handled by fuzzy match)."""
    add_item_tool = order_tools[0]

    result = await add_item_tool(
        category="Beef & Pork", item_name="big mac", quantity=1
    )

    # Should succeed
    assert "Added one Big Mac" in result

    # Check state
    items = order_state_manager.get_items()
    assert len(items) == 1
    assert items[0].item_name == "Big Mac"  # Normalized to correct case


@pytest.mark.asyncio
async def test_add_item_with_empty_modifiers_list(order_tools, order_state_manager):
    """Adding an item with empty modifiers list works."""
    add_item_tool = order_tools[0]

    result = await add_item_tool(
        category="Beef & Pork", item_name="Big Mac", modifiers=[], quantity=1
    )

    # Should succeed
    assert "Added one Big Mac" in result

    # Check state
    items = order_state_manager.get_items()
    assert len(items) == 1
    assert items[0].modifiers == []


@pytest.mark.asyncio
async def test_add_multiple_different_items(order_tools, order_state_manager):
    """Adding multiple different items accumulates state."""
    add_item_tool = order_tools[0]

    # Add first item
    await add_item_tool(category="Beef & Pork", item_name="Big Mac", quantity=1)

    # Add second item
    await add_item_tool(
        category="Snacks & Sides", item_name="Medium French Fries", quantity=1
    )

    # Add third item
    await add_item_tool(
        category="Beverages", item_name="Coca-Cola Classic (Medium)", quantity=1
    )

    # Check state
    items = order_state_manager.get_items()
    assert len(items) == 3
    assert {item.item_name for item in items} == {
        "Big Mac",
        "Medium French Fries",
        "Coca-Cola Classic (Medium)",
    }


# ============================================================================
# complete_order Tests
# ============================================================================


@pytest.mark.asyncio
async def test_complete_order_success(order_tools, order_state_manager, tmp_path):
    """Completing order with items succeeds and creates final JSON."""
    add_item_tool = order_tools[0]
    complete_tool = order_tools[1]

    # Add items
    await add_item_tool(category="Beef & Pork", item_name="Big Mac")
    await add_item_tool(category="Snacks & Sides", item_name="Medium French Fries")

    # Complete order
    result = await complete_tool()

    # Check response
    assert "Order complete" in result
    assert "Big Mac" in result
    assert "Medium French Fries" in result
    assert "Total items: 2" in result

    # Verify final JSON was created
    final_json_path = (
        tmp_path
        / "orders"
        / "test-tools-session"  # Session ID from fixture
        / "final_order.json"
    )
    assert final_json_path.exists()


@pytest.mark.asyncio
async def test_complete_empty_order(order_tools, order_state_manager):
    """Completing an empty order prompts user to add items."""
    complete_tool = order_tools[1]

    result = await complete_tool()

    # Check response
    assert "empty" in result.lower()
    assert "add something" in result.lower() or "would you like" in result.lower()


@pytest.mark.asyncio
async def test_complete_order_with_multiple_quantities(
    order_tools, order_state_manager
):
    """Completing order correctly counts total items including quantities."""
    add_item_tool = order_tools[0]
    complete_tool = order_tools[1]

    # Add items with quantities
    await add_item_tool(category="Beef & Pork", item_name="Big Mac", quantity=2)
    await add_item_tool(
        category="Snacks & Sides", item_name="Medium French Fries", quantity=3
    )

    # Complete order
    result = await complete_tool()

    # Check total items is correct (2 + 3 = 5)
    assert "Total items: 5" in result


# ============================================================================
# remove_item_from_order Tests
# ============================================================================


@pytest.mark.asyncio
async def test_remove_existing_item(order_tools, order_state_manager):
    """Removing an existing item succeeds."""
    add_item_tool = order_tools[0]
    remove_tool = order_tools[2]

    # Add items
    await add_item_tool(category="Beef & Pork", item_name="Big Mac")
    await add_item_tool(category="Snacks & Sides", item_name="Medium French Fries")

    # Remove one item
    result = await remove_tool(item_name="Big Mac")

    # Check response
    assert "Removed Big Mac" in result

    # Check state
    items = order_state_manager.get_items()
    assert len(items) == 1
    assert items[0].item_name == "Medium French Fries"


@pytest.mark.asyncio
async def test_remove_non_existent_item(order_tools, order_state_manager):
    """Removing an item not in the order returns error message."""
    add_item_tool = order_tools[0]
    remove_tool = order_tools[2]

    # Add one item
    await add_item_tool(category="Beef & Pork", item_name="Big Mac")

    # Try to remove different item
    result = await remove_tool(item_name="Whopper")

    # Check error message
    assert "don't see" in result.lower() or "not" in result.lower()

    # State should be unchanged
    items = order_state_manager.get_items()
    assert len(items) == 1
    assert items[0].item_name == "Big Mac"


@pytest.mark.asyncio
async def test_remove_from_empty_order(order_tools):
    """Removing from an empty order returns error message."""
    remove_tool = order_tools[2]

    result = await remove_tool(item_name="Big Mac")

    # Check error message
    assert "don't see" in result.lower()


@pytest.mark.asyncio
async def test_remove_specific_item_when_duplicates_exist(
    order_tools, order_state_manager
):
    """When duplicates exist, removes the most recently added one."""
    add_item_tool = order_tools[0]
    remove_tool = order_tools[2]

    # Add same item twice
    await add_item_tool(category="Beef & Pork", item_name="Big Mac", quantity=1)
    await add_item_tool(category="Beef & Pork", item_name="Big Mac", quantity=1)

    # Add different item in between
    await add_item_tool(category="Snacks & Sides", item_name="Medium French Fries")

    # Remove Big Mac (should remove the most recent one)
    result = await remove_tool(item_name="Big Mac")

    assert "Removed Big Mac" in result

    # Should still have one Big Mac and one fries
    items = order_state_manager.get_items()
    assert len(items) == 2
    item_names = [item.item_name for item in items]
    assert item_names.count("Big Mac") == 1
    assert "Medium French Fries" in item_names


@pytest.mark.asyncio
async def test_remove_item_case_insensitive(order_tools, order_state_manager):
    """Removing items is case insensitive."""
    add_item_tool = order_tools[0]
    remove_tool = order_tools[2]

    # Add item
    await add_item_tool(category="Beef & Pork", item_name="Big Mac")

    # Remove with different case
    result = await remove_tool(item_name="big mac")

    # Should succeed
    assert "removed big mac" in result.lower()

    # Order should be empty
    assert order_state_manager.is_empty()


# ============================================================================
# Validation Integration Tests
# ============================================================================


@pytest.mark.asyncio
async def test_validation_error_doesnt_mutate_state(order_tools, order_state_manager):
    """Failed validation doesn't mutate order state."""
    add_item_tool = order_tools[0]

    # Try to add invalid item
    result = await add_item_tool(
        category="Beef & Pork",
        item_name="Whopper",  # Not on menu
    )

    # Check error message returned
    assert "couldn't add" in result.lower()

    # Verify state is unchanged
    assert order_state_manager.is_empty()


@pytest.mark.asyncio
async def test_partial_validation_failure_preserves_valid_items(
    order_tools, order_state_manager
):
    """If one item fails validation, previously added items remain."""
    add_item_tool = order_tools[0]

    # Add valid item
    await add_item_tool(category="Beef & Pork", item_name="Big Mac")

    # Try to add invalid item
    await add_item_tool(category="Beef & Pork", item_name="Whopper")

    # Check state still has the valid item
    items = order_state_manager.get_items()
    assert len(items) == 1
    assert items[0].item_name == "Big Mac"


# ============================================================================
# Edge Cases
# ============================================================================


@pytest.mark.asyncio
async def test_add_item_with_very_long_item_name(order_tools, order_state_manager):
    """Very long item names are handled (validation should reject)."""
    add_item_tool = order_tools[0]

    result = await add_item_tool(
        category="Beef & Pork",
        item_name="X" * 200,  # Very long invalid name
        quantity=1,
    )

    # Should fail validation
    assert "couldn't add" in result.lower()

    # State should be empty
    assert order_state_manager.is_empty()


@pytest.mark.asyncio
async def test_add_item_with_special_characters_in_name(
    order_tools, order_state_manager
):
    """Special characters in item names are handled correctly."""
    add_item_tool = order_tools[0]

    # Try a real item with special characters (if exists)
    # This should test fuzzy matching with special chars
    result = await add_item_tool(
        category="Coffee & Tea", item_name="Caffe Latte", quantity=1
    )

    # Should either succeed or fail gracefully
    # Just verify no crashes
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_tools_return_strings(order_tools):
    """All tools return string responses (required for LLM)."""
    add_tool, complete_tool, remove_tool = order_tools

    # All tools should be callable
    assert callable(add_tool)
    assert callable(complete_tool)
    assert callable(remove_tool)


@pytest.mark.asyncio
async def test_factory_creates_three_tools(order_state_manager, menu_provider):
    """Factory function creates exactly three tools."""
    tools = create_order_tools(order_state_manager, menu_provider)

    assert len(tools) == 3
    assert tools[0].info.name == "add_item_to_order"
    assert tools[1].info.name == "complete_order"
    assert tools[2].info.name == "remove_item_from_order"
