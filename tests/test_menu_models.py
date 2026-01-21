"""
Tests for McDonald's menu Pydantic models.

Tests cover:
- Modifier creation and uniqueness
- Item creation with modifiers
- Menu creation and manipulation
- JSON serialization and deserialization
- Loading from original JSON file format
"""

import json
from pathlib import Path

import pytest

from menus.mcdonalds.models import Item, Menu, Modifier


class TestModifier:
    """Tests for the Modifier model."""

    def test_modifier_creation(self):
        """Test creating a modifier with auto-generated ID."""
        modifier = Modifier(modifier_name="Egg Whites")
        assert modifier.modifier_name == "Egg Whites"
        assert modifier.modifier_id is not None
        assert len(modifier.modifier_id) > 0

    def test_modifier_ids_are_unique(self):
        """Test that each modifier gets a unique ID."""
        modifier1 = Modifier(modifier_name="Cheese")
        modifier2 = Modifier(modifier_name="Cheese")
        assert modifier1.modifier_id != modifier2.modifier_id

    def test_modifier_custom_id(self):
        """Test creating a modifier with a custom ID."""
        custom_id = "custom-123"
        modifier = Modifier(modifier_name="Bacon", modifier_id=custom_id)
        assert modifier.modifier_id == custom_id

    def test_modifier_equality(self):
        """Test that modifiers are compared by ID."""
        modifier1 = Modifier(modifier_name="Cheese", modifier_id="id1")
        modifier2 = Modifier(modifier_name="Cheese", modifier_id="id1")
        modifier3 = Modifier(modifier_name="Cheese", modifier_id="id2")

        assert modifier1 == modifier2
        assert modifier1 != modifier3

    def test_modifier_in_set(self):
        """Test that modifiers can be used in sets."""
        modifier1 = Modifier(modifier_name="Cheese", modifier_id="id1")
        modifier2 = Modifier(modifier_name="Bacon", modifier_id="id2")
        modifier3 = Modifier(modifier_name="Cheese", modifier_id="id1")

        modifier_set = {modifier1, modifier2, modifier3}
        assert len(modifier_set) == 2  # modifier1 and modifier3 are the same

    def test_modifier_json_serialization(self):
        """Test serializing a modifier to JSON."""
        modifier = Modifier(modifier_name="Egg Whites", modifier_id="test-id")
        json_str = modifier.model_dump_json()
        data = json.loads(json_str)

        assert data["modifier_name"] == "Egg Whites"
        assert data["modifier_id"] == "test-id"

    def test_modifier_json_deserialization(self):
        """Test deserializing a modifier from JSON."""
        json_str = '{"modifier_name": "Cheese", "modifier_id": "test-id"}'
        modifier = Modifier.model_validate_json(json_str)

        assert modifier.modifier_name == "Cheese"
        assert modifier.modifier_id == "test-id"


class TestItem:
    """Tests for the Item model."""

    def test_item_creation_without_modifiers(self):
        """Test creating an item without modifiers."""
        item = Item(
            category_name="Breakfast",
            item_name="Egg McMuffin",
            available_as_base=True
        )

        assert item.category_name == "Breakfast"
        assert item.item_name == "Egg McMuffin"
        assert item.available_as_base is True
        assert len(item.modifiers) == 0

    def test_item_creation_with_modifiers(self):
        """Test creating an item with modifiers."""
        modifiers = [
            Modifier(modifier_name="Egg Whites"),
            Modifier(modifier_name="Hotcakes")
        ]
        item = Item(
            category_name="Breakfast",
            item_name="Big Breakfast",
            available_as_base=True,
            modifiers=modifiers
        )

        assert len(item.modifiers) == 2
        assert item.modifiers[0].modifier_name == "Egg Whites"
        assert item.modifiers[1].modifier_name == "Hotcakes"

    def test_item_add_modifier(self):
        """Test adding a modifier to an item."""
        item = Item(
            category_name="Beef & Pork",
            item_name="Quarter Pounder",
            available_as_base=True
        )

        modifier = item.add_modifier("Cheese")
        assert len(item.modifiers) == 1
        assert modifier.modifier_name == "Cheese"
        assert modifier in item.modifiers

    def test_item_json_serialization(self):
        """Test serializing an item to JSON."""
        item = Item(
            category_name="Breakfast",
            item_name="Egg McMuffin",
            available_as_base=True,
            modifiers=[Modifier(modifier_name="Cheese", modifier_id="id1")]
        )

        json_str = item.to_json()
        data = json.loads(json_str)

        assert data["category_name"] == "Breakfast"
        assert data["item_name"] == "Egg McMuffin"
        assert data["available_as_base"] is True
        assert len(data["modifiers"]) == 1
        assert data["modifiers"][0]["modifier_name"] == "Cheese"

    def test_item_json_deserialization(self):
        """Test deserializing an item from JSON."""
        json_str = '''
        {
            "category_name": "Breakfast",
            "item_name": "Egg McMuffin",
            "available_as_base": true,
            "modifiers": [
                {"modifier_name": "Cheese", "modifier_id": "id1"}
            ]
        }
        '''
        item = Item.from_json(json_str)

        assert item.category_name == "Breakfast"
        assert item.item_name == "Egg McMuffin"
        assert item.available_as_base is True
        assert len(item.modifiers) == 1
        assert item.modifiers[0].modifier_name == "Cheese"

    def test_item_not_available_as_base(self):
        """Test creating an item that requires modifiers."""
        item = Item(
            category_name="Smoothies & Shakes",
            item_name="McFlurry",
            available_as_base=False,
            modifiers=[
                Modifier(modifier_name="M&Ms Candies"),
                Modifier(modifier_name="Oreo Cookies")
            ]
        )

        assert item.available_as_base is False
        assert len(item.modifiers) == 2


class TestMenu:
    """Tests for the Menu model."""

    def test_menu_creation_empty(self):
        """Test creating an empty menu."""
        menu = Menu()
        assert len(menu.categories) == 0
        assert menu.get_all_categories() == []

    def test_menu_add_item(self):
        """Test adding items to the menu."""
        menu = Menu()
        item1 = Item(
            category_name="Breakfast",
            item_name="Egg McMuffin",
            available_as_base=True
        )
        item2 = Item(
            category_name="Breakfast",
            item_name="Hash Brown",
            available_as_base=True
        )

        menu.add_item(item1)
        menu.add_item(item2)

        assert len(menu.categories) == 1
        assert "Breakfast" in menu.categories
        assert len(menu.get_category("Breakfast")) == 2

    def test_menu_multiple_categories(self):
        """Test menu with multiple categories."""
        menu = Menu()
        breakfast = Item(category_name="Breakfast", item_name="Egg McMuffin", available_as_base=True)
        burger = Item(category_name="Beef & Pork", item_name="Big Mac", available_as_base=True)

        menu.add_item(breakfast)
        menu.add_item(burger)

        assert len(menu.categories) == 2
        categories = menu.get_all_categories()
        assert "Breakfast" in categories
        assert "Beef & Pork" in categories

    def test_menu_get_category(self):
        """Test retrieving items from a specific category."""
        menu = Menu()
        item1 = Item(category_name="Breakfast", item_name="Item1", available_as_base=True)
        item2 = Item(category_name="Breakfast", item_name="Item2", available_as_base=True)
        menu.add_item(item1)
        menu.add_item(item2)

        breakfast_items = menu.get_category("Breakfast")
        assert len(breakfast_items) == 2
        assert breakfast_items[0].item_name == "Item1"
        assert breakfast_items[1].item_name == "Item2"

    def test_menu_get_nonexistent_category(self):
        """Test getting a category that doesn't exist."""
        menu = Menu()
        items = menu.get_category("NonExistent")
        assert items == []

    def test_menu_get_item(self):
        """Test retrieving a specific item by category and name."""
        menu = Menu()
        item = Item(category_name="Breakfast", item_name="Egg McMuffin", available_as_base=True)
        menu.add_item(item)

        retrieved = menu.get_item("Breakfast", "Egg McMuffin")
        assert retrieved is not None
        assert retrieved.item_name == "Egg McMuffin"

    def test_menu_get_nonexistent_item(self):
        """Test getting an item that doesn't exist."""
        menu = Menu()
        item = menu.get_item("Breakfast", "NonExistent")
        assert item is None

    def test_menu_json_serialization(self):
        """Test serializing a menu to JSON."""
        menu = Menu()
        item = Item(
            category_name="Breakfast",
            item_name="Egg McMuffin",
            available_as_base=True,
            modifiers=[Modifier(modifier_name="Cheese")]
        )
        menu.add_item(item)

        json_str = menu.to_json()
        data = json.loads(json_str)

        assert "categories" in data
        assert "Breakfast" in data["categories"]
        assert len(data["categories"]["Breakfast"]) == 1
        assert data["categories"]["Breakfast"][0]["item_name"] == "Egg McMuffin"

    def test_menu_json_deserialization(self):
        """Test deserializing a menu from JSON."""
        json_str = '''
        {
            "categories": {
                "Breakfast": [
                    {
                        "category_name": "Breakfast",
                        "item_name": "Egg McMuffin",
                        "available_as_base": true,
                        "modifiers": []
                    }
                ]
            }
        }
        '''
        menu = Menu.from_json(json_str)

        assert len(menu.categories) == 1
        assert "Breakfast" in menu.categories
        breakfast_items = menu.get_category("Breakfast")
        assert len(breakfast_items) == 1
        assert breakfast_items[0].item_name == "Egg McMuffin"

    def test_menu_load_from_file(self, tmp_path):
        """Test loading menu from the original JSON file format."""
        # Create a temporary JSON file with sample data
        test_data = {
            "Breakfast": {
                "Egg McMuffin": {
                    "available_as_base": True,
                    "variations": []
                },
                "Big Breakfast": {
                    "available_as_base": True,
                    "variations": ["Egg Whites", "Hotcakes"]
                }
            },
            "Beef & Pork": {
                "Big Mac": {
                    "available_as_base": True,
                    "variations": []
                },
                "Quarter Pounder": {
                    "available_as_base": True,
                    "variations": ["Cheese", "Bacon"]
                }
            }
        }

        test_file = tmp_path / "test_menu.json"
        with open(test_file, 'w') as f:
            json.dump(test_data, f)

        # Load the menu
        menu = Menu.load_from_file(test_file)

        # Verify the menu was loaded correctly
        assert len(menu.categories) == 2
        assert "Breakfast" in menu.categories
        assert "Beef & Pork" in menu.categories

        # Check Breakfast items
        breakfast = menu.get_category("Breakfast")
        assert len(breakfast) == 2

        egg_mcmuffin = menu.get_item("Breakfast", "Egg McMuffin")
        assert egg_mcmuffin is not None
        assert egg_mcmuffin.available_as_base is True
        assert len(egg_mcmuffin.modifiers) == 0

        big_breakfast = menu.get_item("Breakfast", "Big Breakfast")
        assert big_breakfast is not None
        assert len(big_breakfast.modifiers) == 2
        modifier_names = [m.modifier_name for m in big_breakfast.modifiers]
        assert "Egg Whites" in modifier_names
        assert "Hotcakes" in modifier_names

        # Check Beef & Pork items
        quarter_pounder = menu.get_item("Beef & Pork", "Quarter Pounder")
        assert quarter_pounder is not None
        assert len(quarter_pounder.modifiers) == 2

    def test_menu_save_to_file(self, tmp_path):
        """Test saving menu to a JSON file."""
        menu = Menu()
        item = Item(
            category_name="Breakfast",
            item_name="Egg McMuffin",
            available_as_base=True,
            modifiers=[Modifier(modifier_name="Cheese")]
        )
        menu.add_item(item)

        # Save to file
        output_file = tmp_path / "output_menu.json"
        menu.save_to_file(output_file)

        # Verify file was created
        assert output_file.exists()

        # Load and verify contents
        with open(output_file) as f:
            data = json.load(f)

        assert "categories" in data
        assert "Breakfast" in data["categories"]
        assert len(data["categories"]["Breakfast"]) == 1


def test_load_actual_menu_file():
    """Integration test: Load the actual McDonald's menu JSON file."""
    menu_file = Path(__file__).parent.parent / "menus" / "mcdonalds" / "transformed-data" / "menu-structure-2026-01-21.json"

    if not menu_file.exists():
        pytest.skip(f"Menu file not found: {menu_file}")

    menu = Menu.load_from_file(menu_file)

    # Verify the menu loaded successfully
    assert len(menu.categories) > 0

    # Check for expected categories
    expected_categories = ["Breakfast", "Beef & Pork", "Chicken & Fish", "Beverages", "Coffee & Tea"]
    for category in expected_categories:
        assert category in menu.get_all_categories(), f"Expected category '{category}' not found"

    # Check a specific item with variations
    big_breakfast = menu.get_item("Breakfast", "Big Breakfast (Large Biscuit)")
    if big_breakfast:
        assert big_breakfast.available_as_base is True
        assert len(big_breakfast.modifiers) > 0

    # Check an item that requires modifiers (McFlurry)
    categories = menu.get_all_categories()
    if "Smoothies & Shakes" in categories:
        mcflurry_items = [item for item in menu.get_category("Smoothies & Shakes") if "McFlurry" in item.item_name]
        if mcflurry_items:
            mcflurry = mcflurry_items[0]
            assert mcflurry.available_as_base is False
            assert len(mcflurry.modifiers) > 0


def test_round_trip_serialization(tmp_path):
    """Test that a menu can be saved and loaded without data loss."""
    # Create original menu
    original_menu = Menu()
    item = Item(
        category_name="Breakfast",
        item_name="Test Item",
        available_as_base=True,
        modifiers=[
            Modifier(modifier_name="Mod1", modifier_id="id1"),
            Modifier(modifier_name="Mod2", modifier_id="id2")
        ]
    )
    original_menu.add_item(item)

    # Save to file
    file_path = tmp_path / "test.json"
    original_menu.save_to_file(file_path)

    # Load from file
    loaded_menu = Menu.from_json(file_path.read_text())

    # Verify data integrity
    assert len(loaded_menu.categories) == len(original_menu.categories)
    loaded_item = loaded_menu.get_item("Breakfast", "Test Item")
    assert loaded_item is not None
    assert loaded_item.item_name == item.item_name
    assert len(loaded_item.modifiers) == len(item.modifiers)
    assert loaded_item.modifiers[0].modifier_id == "id1"
    assert loaded_item.modifiers[1].modifier_id == "id2"
