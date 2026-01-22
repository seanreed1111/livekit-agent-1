"""MenuProvider - Read-only data access layer for McDonald's menu.

This module provides the MenuProvider class, which loads and queries
the McDonald's menu data in a thread-safe, immutable manner.
"""

from pathlib import Path

from menus.mcdonalds.models import Item, Menu


class MenuProvider:
    """Read-only menu data provider.

    Loads the McDonald's menu from JSON and provides query methods.
    All methods return immutable data (copies, not references).

    Thread-safe: Can be shared across multiple agents/sessions.
    """

    def __init__(self, menu_file_path: str) -> None:
        """Load menu from JSON file.

        Args:
            menu_file_path: Path to menu JSON file

        Raises:
            FileNotFoundError: If menu file doesn't exist
            ValueError: If menu JSON is invalid
        """
        # Validate file exists
        if not Path(menu_file_path).exists():
            raise FileNotFoundError(f"Menu file not found: {menu_file_path}")

        # Load menu using Pydantic model
        try:
            self._menu = Menu.load_from_file(menu_file_path)
        except Exception as e:
            raise ValueError(f"Invalid menu JSON: {e}") from e

        # Build lookup indices for fast queries
        self._build_indices()

    def search_items(self, keyword: str, category: str | None = None) -> list[Item]:
        """Search for items by keyword, optionally filtered by category.

        Args:
            keyword: Search term (case-insensitive)
            category: Optional category to filter by

        Returns:
            List of matching items (copies, not references)

        Examples:
            - search_items("mac") → [Big Mac, Egg McMuffin, ...]
            - search_items("burger", category="Beef & Pork") → [burgers only]
            - search_items("coffee", category="Coffee & Tea") → [coffee items]
        """
        keyword_lower = keyword.lower()
        results = []

        # Get items to search
        if category:
            items_to_search = self.get_category(category)
        else:
            items_to_search = self._get_all_items()

        # Search item names (case-insensitive substring match)
        for item in items_to_search:
            if keyword_lower in item.item_name.lower():
                # Return copy, not reference
                results.append(item.model_copy())

        return results

    def get_category(self, category_name: str) -> list[Item]:
        """Get all items in a category.

        Args:
            category_name: Name of category (e.g., "Breakfast")

        Returns:
            List of items in category (empty list if category not found)

        Examples:
            - get_category("Breakfast") → [Egg McMuffin, Hash Browns, ...]
            - get_category("Invalid") → []
        """
        # Use index for O(1) lookup
        items = self._category_index.get(category_name, [])

        # Return copies, not references
        return [item.model_copy() for item in items]

    def get_item(self, category_name: str, item_name: str) -> Item | None:
        """Get a specific item by category and name.

        Args:
            category_name: Category the item is in
            item_name: Name of the item (case-insensitive)

        Returns:
            Item if found, None otherwise

        Examples:
            - get_item("Beef & Pork", "Big Mac") → Item(...)
            - get_item("Breakfast", "Big Mac") → None (wrong category)
        """
        items = self.get_category(category_name)

        for item in items:
            if item.item_name.lower() == item_name.lower():
                return item.model_copy()  # Return copy

        return None

    def get_all_categories(self) -> list[str]:
        """Get list of all category names.

        Returns:
            List of category names

        Example:
            → ["Breakfast", "Beef & Pork", "Chicken & Fish", ...]
        """
        return list(self._category_index.keys())

    def get_menu(self) -> Menu:
        """Get the complete menu.

        Returns:
            Complete Menu object (immutable copy)
        """
        return self._menu.model_copy(deep=True)

    def get_items_count(self) -> int:
        """Get total number of items across all categories."""
        return sum(len(items) for items in self._category_index.values())

    def category_exists(self, category_name: str) -> bool:
        """Check if a category exists."""
        return category_name in self._category_index

    def _build_indices(self) -> None:
        """Build lookup indices for fast queries (called once on init)."""
        self._category_index: dict[str, list[Item]] = {}

        for category_name, items in self._menu.categories.items():
            self._category_index[category_name] = items

    def _get_all_items(self) -> list[Item]:
        """Get all items across all categories."""
        all_items = []
        for items in self._category_index.values():
            all_items.extend(items)
        return all_items
