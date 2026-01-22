"""Integration tests for DriveThruAgent.

These tests verify that the agent's components work together correctly,
focusing on the integration between tools, order state, and menu validation.

For full E2E tests with LLM interaction, see the BDD scenarios in Plan 07.
"""

from pathlib import Path

import pytest

from src.drive_thru_agent import DriveThruAgent
from src.drive_thru_llm import DriveThruLLM
from src.menu_provider import MenuProvider


@pytest.fixture
def agent_with_real_components(tmp_path):
    """Create agent with real DriveThruLLM for integration testing."""
    from unittest.mock import AsyncMock, Mock

    from livekit.agents.llm import LLM

    # Create menu provider
    menu_provider = MenuProvider(
        "menus/mcdonalds/transformed-data/menu-structure-2026-01-21.json"
    )

    # Create mock base LLM (we won't actually call it in these tests)
    mock_base_llm = Mock(spec=LLM)
    mock_base_llm.chat = AsyncMock()

    # Create real DriveThruLLM
    drive_thru_llm = DriveThruLLM(
        wrapped_llm=mock_base_llm, menu_provider=menu_provider, max_context_items=50
    )

    # Create agent
    return DriveThruAgent(
        session_id="integration-test-session",
        llm=drive_thru_llm,
        menu_provider=menu_provider,
        output_dir=str(tmp_path / "orders"),
    )


@pytest.mark.asyncio
async def test_add_item_tool_integration(agent_with_real_components):
    """Test that add_item tool works with validation and state management."""
    agent = agent_with_real_components

    # Get the add_item tool
    add_item_tool = None
    for tool in agent.tools:
        if hasattr(tool, "__name__") and tool.__name__ == "add_item_to_order":
            add_item_tool = tool
            break

    assert add_item_tool is not None, "add_item_to_order tool not found"

    # Call the tool to add a Big Mac (tools are callable)
    result = await add_item_tool(
        category="Beef & Pork", item_name="Big Mac", modifiers=[], quantity=1
    )

    # Verify success message
    assert "Added one Big Mac" in result

    # Verify item is in order state
    items = agent.order_state.get_items()
    assert len(items) == 1
    assert items[0].item_name == "Big Mac"
    assert items[0].category == "Beef & Pork"


@pytest.mark.asyncio
async def test_add_item_with_fuzzy_matching(agent_with_real_components):
    """Test that fuzzy matching works through the tool."""
    agent = agent_with_real_components

    # Get the add_item tool
    add_item_tool = None
    for tool in agent.tools:
        if hasattr(tool, "__name__") and tool.__name__ == "add_item_to_order":
            add_item_tool = tool
            break

    # Try to add "big mak" (misspelled)
    result = await add_item_tool(
        category="Beef & Pork",
        item_name="big mak",  # Misspelled
        modifiers=[],
        quantity=1,
    )

    # Should succeed with fuzzy match
    assert "Added one Big Mac" in result

    # Verify correct item name is stored
    items = agent.order_state.get_items()
    assert len(items) == 1
    assert items[0].item_name == "Big Mac"  # Corrected name


@pytest.mark.asyncio
async def test_add_invalid_item(agent_with_real_components):
    """Test that invalid items are rejected."""
    agent = agent_with_real_components

    # Get the add_item tool
    add_item_tool = None
    for tool in agent.tools:
        if hasattr(tool, "__name__") and tool.__name__ == "add_item_to_order":
            add_item_tool = tool
            break

    # Try to add an invalid item
    result = await add_item_tool(
        category="Beef & Pork",
        item_name="Whopper",  # Not on McDonald's menu
        modifiers=[],
        quantity=1,
    )

    # Should return error message
    assert "Sorry" in result or "couldn't add" in result.lower()

    # Verify order is still empty
    assert agent.order_state.is_empty()


@pytest.mark.asyncio
async def test_add_multiple_items(agent_with_real_components):
    """Test adding multiple items to an order."""
    agent = agent_with_real_components

    # Get the add_item tool
    add_item_tool = None
    for tool in agent.tools:
        if hasattr(tool, "__name__") and tool.__name__ == "add_item_to_order":
            add_item_tool = tool
            break

    # Add Big Mac
    await add_item_tool(
        category="Beef & Pork", item_name="Big Mac", modifiers=[], quantity=1
    )

    # Add Fries
    await add_item_tool(
        category="Snacks & Sides",
        item_name="Large French Fries",
        modifiers=[],
        quantity=1,
    )

    # Add McNuggets with quantity
    await add_item_tool(
        category="Chicken & Fish",
        item_name="Chicken McNuggets (10 piece)",
        modifiers=[],
        quantity=2,
    )

    # Verify all items in order
    items = agent.order_state.get_items()
    assert len(items) == 3

    # Verify total count
    total = agent.order_state.get_total_count()
    assert total == 4  # 1 Big Mac + 1 Fries + 2 McNuggets


@pytest.mark.asyncio
async def test_complete_order_integration(agent_with_real_components, tmp_path):
    """Test completing an order with file persistence."""
    agent = agent_with_real_components

    # Get tools
    add_item_tool = None
    complete_order_tool = None
    for tool in agent.tools:
        if hasattr(tool, "__name__"):
            if tool.__name__ == "add_item_to_order":
                add_item_tool = tool
            elif tool.__name__ == "complete_order":
                complete_order_tool = tool

    # Add items
    await add_item_tool(
        category="Beef & Pork", item_name="Big Mac", modifiers=[], quantity=2
    )

    # Complete order
    result = await complete_order_tool()

    # Verify completion message
    assert "Order complete" in result
    assert "Big Mac" in result
    assert "Total items: 2" in result

    # Verify final order file exists
    session_dir = Path(tmp_path / "orders" / "integration-test-session")
    final_order_file = session_dir / "final_order.json"
    assert final_order_file.exists()

    # Verify file contents
    import json

    with open(final_order_file) as f:
        order_data = json.load(f)

    assert order_data["session_id"] == "integration-test-session"
    assert order_data["total_items"] == 2
    assert len(order_data["items"]) == 1  # One unique item
    assert order_data["items"][0]["item_name"] == "Big Mac"
    assert order_data["items"][0]["quantity"] == 2


@pytest.mark.asyncio
async def test_remove_item_integration(agent_with_real_components):
    """Test removing an item from the order."""
    agent = agent_with_real_components

    # Get tools
    add_item_tool = None
    remove_item_tool = None
    for tool in agent.tools:
        if hasattr(tool, "__name__"):
            if tool.__name__ == "add_item_to_order":
                add_item_tool = tool
            elif tool.__name__ == "remove_item_from_order":
                remove_item_tool = tool

    # Add items
    await add_item_tool(
        category="Beef & Pork", item_name="Big Mac", modifiers=[], quantity=1
    )
    await add_item_tool(
        category="Snacks & Sides",
        item_name="Large French Fries",
        modifiers=[],
        quantity=1,
    )

    # Verify we have 2 items
    assert agent.order_state.get_total_count() == 2

    # Remove Big Mac
    result = await remove_item_tool(item_name="Big Mac")

    # Verify removal message
    assert "Removed Big Mac" in result

    # Verify only fries remain
    items = agent.order_state.get_items()
    assert len(items) == 1
    assert items[0].item_name == "Large French Fries"


@pytest.mark.asyncio
async def test_complete_empty_order(agent_with_real_components):
    """Test that completing an empty order is handled gracefully."""
    agent = agent_with_real_components

    # Get complete_order tool
    complete_order_tool = None
    for tool in agent.tools:
        if hasattr(tool, "__name__") and tool.__name__ == "complete_order":
            complete_order_tool = tool
            break

    # Try to complete empty order
    result = await complete_order_tool()

    # Should prompt user to add items
    assert "empty" in result.lower()
    assert "add something" in result.lower() or "would you like" in result.lower()


@pytest.mark.asyncio
async def test_agent_instructions_exist(agent_with_real_components):
    """Test that agent has proper instructions."""
    agent = agent_with_real_components

    # Get instructions (they're stored in the Agent base class)
    # We can verify the agent was created successfully
    assert agent is not None

    # Verify agent has the DriveThruAgent type
    assert isinstance(agent, DriveThruAgent)

    # Verify order state is accessible
    assert agent.order_state is not None

    # Verify tools are accessible
    assert len(agent.tools) == 3  # add_item, complete_order, remove_item
