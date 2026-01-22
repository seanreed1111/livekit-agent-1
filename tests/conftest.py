"""Shared pytest fixtures for all test modules.

This module contains common fixtures used across multiple test files,
including menu data, menu instances, and test items.
"""

import json
from pathlib import Path

import pytest

from menus.mcdonalds.models import Item, Menu, Modifier
from src.menu_provider import MenuProvider

# ============================================================================
# Menu Data Fixtures
# ============================================================================


@pytest.fixture
def test_menu_data() -> dict:
    """Create minimal test menu data in the original format.

    The original format has categories as top-level keys, with items nested under each category.
    Each item has 'available_as_base' and 'variations' fields.
    """
    return {
        "Breakfast": {
            "Egg McMuffin": {
                "available_as_base": True,
                "variations": ["No Cheese"],
            },
            "Hash Browns": {
                "available_as_base": True,
                "variations": [],
            },
        },
        "Beef & Pork": {
            "Big Mac": {
                "available_as_base": True,
                "variations": ["No Pickles", "Extra Cheese"],
            },
            "Quarter Pounder": {
                "available_as_base": True,
                "variations": [],
            },
        },
        "Chicken & Fish": {
            "McChicken": {
                "available_as_base": True,
                "variations": [],
            }
        },
    }


# ============================================================================
# Item Fixtures
# ============================================================================


@pytest.fixture
def sample_menu_items():
    """Create a small test menu with various items."""
    return [
        Item(
            category_name="Beef & Pork",
            item_name="Big Mac",
            available_as_base=True,
            modifiers=[
                Modifier(modifier_name="No Pickles"),
                Modifier(modifier_name="Extra Sauce"),
                Modifier(modifier_name="No Onions"),
            ],
        ),
        Item(
            category_name="Beef & Pork",
            item_name="Quarter Pounder",
            available_as_base=True,
            modifiers=[
                Modifier(modifier_name="Cheese"),
                Modifier(modifier_name="Bacon"),
            ],
        ),
        Item(
            category_name="Chicken & Fish",
            item_name="Chicken McNuggets",
            available_as_base=True,
            modifiers=[
                Modifier(modifier_name="6 Piece"),
                Modifier(modifier_name="10 Piece"),
                Modifier(modifier_name="20 Piece"),
            ],
        ),
    ]


@pytest.fixture
def big_mac_with_modifiers():
    """Create a Big Mac with available modifiers."""
    item = Item(
        category_name="Beef & Pork",
        item_name="Big Mac",
        available_as_base=True,
        modifiers=[
            Modifier(modifier_name="No Pickles"),
            Modifier(modifier_name="Extra Sauce"),
            Modifier(modifier_name="No Onions"),
        ],
    )
    return item


@pytest.fixture
def item_without_modifiers():
    """Create an item with no available modifiers."""
    return Item(
        category_name="Beverages",
        item_name="Coca-Cola",
        available_as_base=True,
        modifiers=[],
    )


# ============================================================================
# Menu Fixtures
# ============================================================================


@pytest.fixture
def sample_menu(sample_menu_items):
    """Create a test menu with items in categories."""
    menu = Menu()
    for item in sample_menu_items:
        menu.add_item(item)
    return menu


# ============================================================================
# MenuProvider Fixtures
# ============================================================================


@pytest.fixture
def test_menu_provider(tmp_path, test_menu_data) -> MenuProvider:
    """Create MenuProvider with small test menu."""
    menu_file = tmp_path / "test_menu.json"
    menu_file.write_text(json.dumps(test_menu_data))
    return MenuProvider(str(menu_file))


@pytest.fixture
def real_menu_provider() -> MenuProvider:
    """Create MenuProvider with real menu file."""
    menu_path = "menus/mcdonalds/transformed-data/menu-structure-2026-01-21.json"
    return MenuProvider(menu_path)


# ============================================================================
# Path Fixtures
# ============================================================================


@pytest.fixture
def real_menu_path() -> Path:
    """Get the path to the real McDonald's menu JSON file."""
    return (
        Path(__file__).parent.parent
        / "menus"
        / "mcdonalds"
        / "transformed-data"
        / "menu-structure-2026-01-21.json"
    )


# ============================================================================
# OrderStateManager Fixtures
# ============================================================================


@pytest.fixture
def temp_output_dir(tmp_path):
    """Create temporary output directory for order tests."""
    return str(tmp_path / "orders")


@pytest.fixture
def order_manager(temp_output_dir):
    """Create OrderStateManager with temp directory."""
    from src.order_state_manager import OrderStateManager

    return OrderStateManager(session_id="test-session-123", output_dir=temp_output_dir)


# ============================================================================
# OrderTools Fixtures
# ============================================================================


@pytest.fixture
def menu_provider() -> MenuProvider:
    """Create MenuProvider with real menu for order tools tests."""
    menu_path = "menus/mcdonalds/transformed-data/menu-structure-2026-01-21.json"
    return MenuProvider(menu_path)


@pytest.fixture
def order_state_manager(tmp_path):
    """Create OrderStateManager with temp directory for order tools tests."""
    from src.order_state_manager import OrderStateManager

    return OrderStateManager(
        session_id="test-tools-session", output_dir=str(tmp_path / "orders")
    )


@pytest.fixture
def order_tools(order_state_manager, menu_provider):
    """Create order tools with real dependencies for integration tests."""
    from src.tools.order_tools import create_order_tools

    return create_order_tools(order_state_manager, menu_provider)
