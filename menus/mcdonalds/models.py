"""
Pydantic v2 models for McDonald's menu data.

This module provides models for representing menu items, modifiers, and the complete menu structure.
All models support JSON serialization and deserialization.
"""

from pathlib import Path
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class Modifier(BaseModel):
    """A modifier or variation for a menu item.

    Attributes:
        modifier_name: The name of the modifier (e.g., "Egg Whites", "Cheese")
        modifier_id: A unique identifier for this modifier (auto-generated UUID)
    """
    modifier_name: str
    modifier_id: str = Field(default_factory=lambda: str(uuid4()))

    def __hash__(self) -> int:
        """Allow Modifiers to be used in sets based on their ID."""
        return hash(self.modifier_id)

    def __eq__(self, other: object) -> bool:
        """Compare Modifiers by their ID."""
        if not isinstance(other, Modifier):
            return False
        return self.modifier_id == other.modifier_id


class Item(BaseModel):
    """A menu item with its category and available modifiers.

    Attributes:
        category_name: The category this item belongs to (e.g., "Breakfast", "Beef & Pork")
        item_name: The name of the item (e.g., "Big Mac")
        available_as_base: Whether the item can be ordered without modifications
        modifiers: List of available modifiers/variations for this item
    """
    category_name: str
    item_name: str
    available_as_base: bool
    modifiers: list[Modifier] = Field(default_factory=list)

    def add_modifier(self, modifier_name: str) -> "Modifier":
        """Add a new modifier to this item.

        Args:
            modifier_name: The name of the modifier to add

        Returns:
            The created Modifier instance
        """
        modifier = Modifier(modifier_name=modifier_name)
        self.modifiers.append(modifier)
        return modifier

    def to_json(self) -> str:
        """Serialize this item to JSON string."""
        return self.model_dump_json(indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "Item":
        """Deserialize an item from JSON string.

        Args:
            json_str: JSON string representation of an Item

        Returns:
            Item instance
        """
        return cls.model_validate_json(json_str)


class Menu(BaseModel):
    """Complete menu containing all items organized by category.

    Attributes:
        categories: Dictionary mapping category names to lists of items
    """
    categories: dict[str, list[Item]] = Field(default_factory=dict)

    def add_item(self, item: Item) -> None:
        """Add an item to the menu under its category.

        Args:
            item: The item to add
        """
        if item.category_name not in self.categories:
            self.categories[item.category_name] = []
        self.categories[item.category_name].append(item)

    def get_category(self, category_name: str) -> list[Item]:
        """Get all items in a specific category.

        Args:
            category_name: The name of the category

        Returns:
            List of items in that category, or empty list if category doesn't exist
        """
        return self.categories.get(category_name, [])

    def get_all_categories(self) -> list[str]:
        """Get list of all category names.

        Returns:
            List of category names
        """
        return list(self.categories.keys())

    def get_item(self, category_name: str, item_name: str) -> Item | None:
        """Get a specific item by category and name.

        Args:
            category_name: The category to search in
            item_name: The name of the item

        Returns:
            The item if found, None otherwise
        """
        for item in self.get_category(category_name):
            if item.item_name == item_name:
                return item
        return None

    def to_json(self) -> str:
        """Serialize this menu to JSON string."""
        return self.model_dump_json(indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "Menu":
        """Deserialize a menu from JSON string.

        Args:
            json_str: JSON string representation of a Menu

        Returns:
            Menu instance
        """
        return cls.model_validate_json(json_str)

    @classmethod
    def load_from_file(cls, file_path: str | Path) -> "Menu":
        """Load menu from the original JSON file format.

        The original format has categories as top-level keys, with items nested under each category.
        Each item has 'available_as_base' and 'variations' fields.

        Args:
            file_path: Path to the JSON file

        Returns:
            Menu instance populated with all items and modifiers
        """
        import json

        path = Path(file_path)
        with path.open('r') as f:
            data: dict[str, dict[str, Any]] = json.load(f)

        menu = cls()

        for category_name, items_dict in data.items():
            for item_name, item_data in items_dict.items():
                item = Item(
                    category_name=category_name,
                    item_name=item_name,
                    available_as_base=item_data['available_as_base'],
                    modifiers=[
                        Modifier(modifier_name=variation)
                        for variation in item_data.get('variations', [])
                    ]
                )
                menu.add_item(item)

        return menu

    def save_to_file(self, file_path: str | Path) -> None:
        """Save menu to a JSON file in the Pydantic model format.

        Args:
            file_path: Path where the JSON file should be saved
        """
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open('w') as f:
            f.write(self.to_json())
