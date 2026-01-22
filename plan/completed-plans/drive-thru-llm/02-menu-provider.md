# Plan 02: MenuProvider (Read-Only Data Access)

**Created**: 2026-01-21
**Status**: Ready for Implementation
**Dependencies**: Plan 01 (Menu models must have `Item`, `Modifier`, `Menu` classes)
**Estimated Complexity**: Low

---

## Overview

The `MenuProvider` is a **read-only data access layer** that loads the McDonald's menu from JSON and provides search/query interfaces. It follows the **Single Responsibility Principle** - it only provides menu data, never modifies it.

**Key Principles**:
- 📖 **Read-only**: Never modifies menu data
- 🔒 **Immutable returns**: Returns copies, not mutable references
- 🎯 **Single source of truth**: Loads menu once, shares with all components
- ⚡ **Fast queries**: Optimized for lookup operations

---

## Component Design

### File Structure

**File**: `src/menu_provider.py` (new)

**Dependencies**:
- `menus/mcdonalds/models.py` (Menu, Item, Modifier Pydantic models)
- `menus/mcdonalds/transformed-data/menu-structure-2026-01-21.json`

---

## Interface Contract

```python
class MenuProvider:
    """Read-only menu data provider.

    Loads the McDonald's menu from JSON and provides query methods.
    All methods return immutable data (copies, not references).

    Thread-safe: Can be shared across multiple agents/sessions.
    """

    def __init__(self, menu_file_path: str) -> None:
        """
        Load menu from JSON file.

        Args:
            menu_file_path: Path to menu JSON file

        Raises:
            FileNotFoundError: If menu file doesn't exist
            ValueError: If menu JSON is invalid
        """

    def search_items(
        self,
        keyword: str,
        category: str | None = None
    ) -> list[Item]:
        """
        Search for items by keyword, optionally filtered by category.

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

    def get_category(self, category_name: str) -> list[Item]:
        """
        Get all items in a category.

        Args:
            category_name: Name of category (e.g., "Breakfast")

        Returns:
            List of items in category (empty list if category not found)

        Examples:
            - get_category("Breakfast") → [Egg McMuffin, Hash Browns, ...]
            - get_category("Invalid") → []
        """

    def get_item(
        self,
        category_name: str,
        item_name: str
    ) -> Item | None:
        """
        Get a specific item by category and name.

        Args:
            category_name: Category the item is in
            item_name: Name of the item (case-insensitive)

        Returns:
            Item if found, None otherwise

        Examples:
            - get_item("Beef & Pork", "Big Mac") → Item(...)
            - get_item("Breakfast", "Big Mac") → None (wrong category)
        """

    def get_all_categories(self) -> list[str]:
        """
        Get list of all category names.

        Returns:
            List of category names

        Example:
            → ["Breakfast", "Beef & Pork", "Chicken & Fish", ...]
        """

    def get_menu(self) -> Menu:
        """
        Get the complete menu.

        Returns:
            Complete Menu object (immutable copy)
        """

    def get_items_count(self) -> int:
        """Get total number of items across all categories."""

    def category_exists(self, category_name: str) -> bool:
        """Check if a category exists."""
```

---

## Implementation Details

### 1. Constructor

**Responsibility**: Load and validate menu data

```python
def __init__(self, menu_file_path: str) -> None:
    """Load menu from JSON file."""
    # 1. Validate file exists
    if not Path(menu_file_path).exists():
        raise FileNotFoundError(f"Menu file not found: {menu_file_path}")

    # 2. Load menu using Pydantic model
    self._menu = Menu.load_from_file(menu_file_path)

    # 3. Build lookup indices for fast queries (optional optimization)
    self._build_indices()
```

**Private State**:
- `self._menu: Menu` - The loaded menu (private, immutable)
- `self._category_index: dict[str, list[Item]]` - Category name → items
- `self._item_index: dict[str, Item]` - Item name → item (for fast lookup)

### 2. Search Methods

#### `search_items()`

**Implementation**:
```python
def search_items(self, keyword: str, category: str | None = None) -> list[Item]:
    """Search for items by keyword."""
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
```

#### `get_category()`

**Implementation**:
```python
def get_category(self, category_name: str) -> list[Item]:
    """Get all items in a category."""
    # Use index for O(1) lookup
    items = self._category_index.get(category_name, [])

    # Return copies, not references
    return [item.model_copy() for item in items]
```

#### `get_item()`

**Implementation**:
```python
def get_item(self, category_name: str, item_name: str) -> Item | None:
    """Get a specific item."""
    items = self.get_category(category_name)

    for item in items:
        if item.item_name.lower() == item_name.lower():
            return item.model_copy()  # Return copy

    return None
```

### 3. Helper Methods

```python
def _build_indices(self) -> None:
    """Build lookup indices for fast queries (called once on init)."""
    self._category_index = {}

    for category_name, items in self._menu.categories.items():
        self._category_index[category_name] = items

def _get_all_items(self) -> list[Item]:
    """Get all items across all categories."""
    all_items = []
    for items in self._category_index.values():
        all_items.extend(items)
    return all_items
```

---

## Testing Strategy

### Unit Tests

**File**: `tests/test_menu_provider.py` (new)

**Test Fixture**:
```python
@pytest.fixture
def menu_provider():
    """Create MenuProvider with real menu file."""
    menu_path = "menus/mcdonalds/transformed-data/menu-structure-2026-01-21.json"
    return MenuProvider(menu_path)

@pytest.fixture
def test_menu_provider(tmp_path):
    """Create MenuProvider with small test menu."""
    # Create minimal test menu JSON
    test_menu = {
        "categories": {
            "Breakfast": [
                {
                    "category_name": "Breakfast",
                    "item_name": "Egg McMuffin",
                    "available_as_base": True,
                    "modifiers": []
                }
            ],
            "Beef & Pork": [
                {
                    "category_name": "Beef & Pork",
                    "item_name": "Big Mac",
                    "available_as_base": True,
                    "modifiers": [
                        {"modifier_name": "No Pickles", "modifier_id": "abc"}
                    ]
                }
            ]
        }
    }

    menu_file = tmp_path / "test_menu.json"
    menu_file.write_text(json.dumps(test_menu))
    return MenuProvider(str(menu_file))
```

**Test Cases** (aim for 15+ tests):

#### Construction Tests
1. `test_menu_provider_loads_successfully()` - Constructor works with valid file
2. `test_menu_provider_file_not_found()` - Raises FileNotFoundError for missing file
3. `test_menu_provider_invalid_json()` - Raises ValueError for bad JSON

#### Search Tests
4. `test_search_items_finds_exact_match()` - "Big Mac" finds Big Mac
5. `test_search_items_case_insensitive()` - "big mac" finds Big Mac
6. `test_search_items_partial_match()` - "mac" finds Big Mac, Egg McMuffin
7. `test_search_items_with_category_filter()` - Search within category only
8. `test_search_items_no_matches()` - Returns empty list for "whopper"
9. `test_search_items_empty_keyword()` - Returns all items or empty list

#### Category Tests
10. `test_get_category_valid()` - Get Breakfast category
11. `test_get_category_invalid()` - Returns empty list for invalid category
12. `test_get_category_case_sensitive()` - Category names are case-sensitive
13. `test_get_all_categories()` - Returns all category names

#### Item Lookup Tests
14. `test_get_item_exists()` - Get Big Mac from Beef & Pork
15. `test_get_item_wrong_category()` - Returns None for Big Mac in Breakfast
16. `test_get_item_not_found()` - Returns None for invalid item
17. `test_get_item_case_insensitive()` - "big mac" finds "Big Mac"

#### Immutability Tests
18. `test_returns_copies_not_references()` - Modifying returned item doesn't affect menu
```python
def test_returns_copies_not_references(menu_provider):
    """Verify MenuProvider returns copies, not mutable references."""
    item1 = menu_provider.get_item("Beef & Pork", "Big Mac")
    item2 = menu_provider.get_item("Beef & Pork", "Big Mac")

    # Modify item1
    item1.quantity = 999

    # item2 should be unaffected
    assert item2.quantity == 1  # Default

    # Re-fetch should also be unaffected
    item3 = menu_provider.get_item("Beef & Pork", "Big Mac")
    assert item3.quantity == 1
```

#### Count and Utility Tests
19. `test_get_items_count()` - Total items = 212 (for real menu)
20. `test_category_exists()` - Returns True/False correctly

---

## BDD Scenarios

While MenuProvider is tested primarily with unit tests, it supports these BDD scenarios:

**Related BDD Scenarios**:
- **Scenario 1.1** (Order a Big Mac) - uses `get_item()`
- **Scenario 1.3** (Order breakfast) - uses `get_category()`
- **Scenario 5.1** (Invalid menu item) - uses `get_item()` returning None
- **Scenario 5.2** (Ambiguous request) - uses `search_items()` for suggestions

**Example BDD Step** (implemented in later phases):
```python
@given("the McDonald's menu is loaded")
def step_impl(context):
    context.menu_provider = MenuProvider(
        "menus/mcdonalds/transformed-data/menu-structure-2026-01-21.json"
    )
```

---

## Implementation Checklist

### Phase 1: Basic Structure
- [ ] Create `src/menu_provider.py`
- [ ] Define `MenuProvider` class skeleton
- [ ] Implement `__init__()` with file loading
- [ ] Add error handling for file not found
- [ ] Add error handling for invalid JSON
- [ ] Test constructor with valid menu file
- [ ] Test constructor with invalid inputs

### Phase 2: Query Methods
- [ ] Implement `get_all_categories()`
- [ ] Implement `get_category()`
- [ ] Implement `get_item()`
- [ ] Implement `search_items()` (basic)
- [ ] Implement `get_menu()`
- [ ] Test each method individually

### Phase 3: Optimization
- [ ] Implement `_build_indices()` for fast lookups
- [ ] Add `get_items_count()` method
- [ ] Add `category_exists()` method
- [ ] Optimize `search_items()` with indices
- [ ] Test performance with full menu (212 items)

### Phase 4: Immutability
- [ ] Ensure all methods return copies via `model_copy()`
- [ ] Write immutability tests
- [ ] Verify no mutable references escape
- [ ] Document immutability guarantees

### Phase 5: Testing
- [ ] Create `tests/test_menu_provider.py`
- [ ] Write construction tests (3 tests)
- [ ] Write search tests (6 tests)
- [ ] Write category tests (4 tests)
- [ ] Write item lookup tests (4 tests)
- [ ] Write immutability tests (1 test)
- [ ] Write utility tests (2 tests)
- [ ] Run tests: `uv run pytest tests/test_menu_provider.py -v`
- [ ] Verify tests complete in <2 seconds

### Phase 6: Code Quality
- [ ] Add type hints to all methods
- [ ] Add docstrings to all public methods
- [ ] Run formatter: `uv run ruff format src/menu_provider.py`
- [ ] Run linter: `uv run ruff check src/menu_provider.py`
- [ ] Check coverage: `uv run pytest --cov=src.menu_provider`

### Phase 7: Integration Prep
- [ ] Test with real menu file (212 items, 9 categories)
- [ ] Verify all 9 categories load correctly
- [ ] Verify search works across all items
- [ ] Document any performance considerations
- [ ] Commit changes

---

## Success Criteria

✅ **All unit tests pass** (20+ tests)
✅ **Tests run in <2 seconds** (fast file I/O)
✅ **Loads real menu correctly** (212 items, 9 categories)
✅ **Returns immutable data** (copies, not references)
✅ **Fast queries** (O(1) category lookup, O(n) search)
✅ **Type hints complete** (passes mypy --strict)
✅ **Docstrings complete** (all public methods documented)
✅ **Thread-safe** (read-only, no mutable state)

---

## Dependencies for Next Plans

**This plan provides**:
- ✅ `MenuProvider` class for read-only menu access
- ✅ Fast query methods: `get_item()`, `get_category()`, `search_items()`
- ✅ Immutable data guarantees
- ✅ Single source of truth for menu data

**Next plans can now use**:
- `MenuProvider` for menu queries in validation
- `MenuProvider` for context injection in DriveThruLLM
- `MenuProvider` for tool implementations
- `MenuProvider` as singleton in agent app

---

## Design Notes

### Why Read-Only?

Making MenuProvider read-only provides several benefits:
1. **Thread-safe**: Can be shared across sessions without locks
2. **No corruption**: Menu cannot be accidentally modified
3. **Single source of truth**: Menu data is guaranteed consistent
4. **Testable**: Predictable behavior, no hidden state changes

### Why Return Copies?

Returning copies (via `model_copy()`) prevents:
- Callers modifying internal menu data
- Reference aliasing bugs
- Unexpected mutations affecting other components

Trade-off: Slight memory overhead, but worth it for safety.

### Why Build Indices?

Pre-building indices on construction gives us:
- O(1) category lookups instead of O(n)
- Faster queries overall
- One-time cost at startup, benefits for all queries

For a 212-item menu, this is negligible overhead with significant benefit.

---

## Example Usage

```python
# Initialize (typically done once at app startup)
menu_provider = MenuProvider(
    "menus/mcdonalds/transformed-data/menu-structure-2026-01-21.json"
)

# Query for an item
big_mac = menu_provider.get_item("Beef & Pork", "Big Mac")
if big_mac:
    print(f"Found: {big_mac.item_name}")

# Search for items
mac_items = menu_provider.search_items("mac")
print(f"Found {len(mac_items)} items with 'mac': {[i.item_name for i in mac_items]}")

# Get a category
breakfast_items = menu_provider.get_category("Breakfast")
print(f"Breakfast has {len(breakfast_items)} items")

# Get all categories
categories = menu_provider.get_all_categories()
print(f"Menu has {len(categories)} categories: {categories}")
```

**Key Principle**: MenuProvider is a pure data access layer. It loads, queries, and returns menu data. Nothing more, nothing less.
