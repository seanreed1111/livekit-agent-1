"""Tests for MenuProvider - Read-only menu data access layer."""

import json

import pytest

from src.menu_provider import MenuProvider


# ============================================================================
# Construction Tests
# ============================================================================


def test_menu_provider_loads_successfully(test_menu_provider):
    """Constructor works with valid file."""
    assert test_menu_provider is not None
    assert test_menu_provider.get_items_count() == 5


def test_menu_provider_file_not_found():
    """Raises FileNotFoundError for missing file."""
    with pytest.raises(FileNotFoundError) as exc_info:
        MenuProvider("nonexistent/path/to/menu.json")
    assert "Menu file not found" in str(exc_info.value)


def test_menu_provider_invalid_json(tmp_path):
    """Raises ValueError for bad JSON."""
    bad_json_file = tmp_path / "bad_menu.json"
    bad_json_file.write_text("{invalid json}")

    with pytest.raises(ValueError) as exc_info:
        MenuProvider(str(bad_json_file))
    assert "Invalid menu JSON" in str(exc_info.value)


# ============================================================================
# Search Tests
# ============================================================================


def test_search_items_finds_exact_match(test_menu_provider):
    """'Big Mac' finds Big Mac."""
    results = test_menu_provider.search_items("Big Mac")
    assert len(results) == 1
    assert results[0].item_name == "Big Mac"
    assert results[0].category_name == "Beef & Pork"


def test_search_items_case_insensitive(test_menu_provider):
    """'big mac' finds Big Mac (case-insensitive)."""
    results = test_menu_provider.search_items("big mac")
    assert len(results) == 1
    assert results[0].item_name == "Big Mac"


def test_search_items_partial_match(test_menu_provider):
    """'Mc' finds Egg McMuffin and McChicken."""
    results = test_menu_provider.search_items("Mc")
    assert len(results) == 2
    item_names = {item.item_name for item in results}
    assert "Egg McMuffin" in item_names
    assert "McChicken" in item_names


def test_search_items_with_category_filter(test_menu_provider):
    """Search within category only."""
    # Without filter, "Pounder" would find Quarter Pounder
    results_all = test_menu_provider.search_items("Pounder")
    assert len(results_all) == 1

    # With category filter
    results_filtered = test_menu_provider.search_items(
        "Pounder", category="Beef & Pork"
    )
    assert len(results_filtered) == 1
    assert results_filtered[0].item_name == "Quarter Pounder"

    # Wrong category should return empty
    results_wrong = test_menu_provider.search_items("Pounder", category="Breakfast")
    assert len(results_wrong) == 0


def test_search_items_no_matches(test_menu_provider):
    """Returns empty list for 'whopper' (not on menu)."""
    results = test_menu_provider.search_items("whopper")
    assert results == []


def test_search_items_empty_keyword(test_menu_provider):
    """Empty keyword returns empty list or all items (implementation choice)."""
    results = test_menu_provider.search_items("")
    # Either behavior is acceptable:
    # - Empty list (no match)
    # - All items (everything matches empty string)
    assert isinstance(results, list)


# ============================================================================
# Category Tests
# ============================================================================


def test_get_category_valid(test_menu_provider):
    """Get Breakfast category."""
    breakfast = test_menu_provider.get_category("Breakfast")
    assert len(breakfast) == 2
    item_names = {item.item_name for item in breakfast}
    assert "Egg McMuffin" in item_names
    assert "Hash Browns" in item_names


def test_get_category_invalid(test_menu_provider):
    """Returns empty list for invalid category."""
    results = test_menu_provider.get_category("InvalidCategory")
    assert results == []


def test_get_category_case_sensitive(test_menu_provider):
    """Category names are case-sensitive."""
    # Correct case
    breakfast = test_menu_provider.get_category("Breakfast")
    assert len(breakfast) == 2

    # Wrong case
    lowercase = test_menu_provider.get_category("breakfast")
    assert len(lowercase) == 0


def test_get_all_categories(test_menu_provider):
    """Returns all category names."""
    categories = test_menu_provider.get_all_categories()
    assert len(categories) == 3
    assert "Breakfast" in categories
    assert "Beef & Pork" in categories
    assert "Chicken & Fish" in categories


# ============================================================================
# Item Lookup Tests
# ============================================================================


def test_get_item_exists(test_menu_provider):
    """Get Big Mac from Beef & Pork."""
    item = test_menu_provider.get_item("Beef & Pork", "Big Mac")
    assert item is not None
    assert item.item_name == "Big Mac"
    assert item.category_name == "Beef & Pork"
    assert len(item.modifiers) == 2


def test_get_item_wrong_category(test_menu_provider):
    """Returns None for Big Mac in Breakfast (wrong category)."""
    item = test_menu_provider.get_item("Breakfast", "Big Mac")
    assert item is None


def test_get_item_not_found(test_menu_provider):
    """Returns None for invalid item."""
    item = test_menu_provider.get_item("Beef & Pork", "Whopper")
    assert item is None


def test_get_item_case_insensitive(test_menu_provider):
    """'big mac' finds 'Big Mac' (case-insensitive)."""
    item = test_menu_provider.get_item("Beef & Pork", "big mac")
    assert item is not None
    assert item.item_name == "Big Mac"


# ============================================================================
# Immutability Tests
# ============================================================================


def test_returns_copies_not_references(test_menu_provider):
    """Verify MenuProvider returns copies, not mutable references."""
    # Get the same item twice
    item1 = test_menu_provider.get_item("Beef & Pork", "Big Mac")
    item2 = test_menu_provider.get_item("Beef & Pork", "Big Mac")

    # Modify item1
    assert item1 is not None
    item1.quantity = 999

    # item2 should be unaffected
    assert item2 is not None
    assert item2.quantity == 1  # Default

    # Re-fetch should also be unaffected
    item3 = test_menu_provider.get_item("Beef & Pork", "Big Mac")
    assert item3 is not None
    assert item3.quantity == 1


def test_search_returns_copies(test_menu_provider):
    """search_items() returns copies, not references."""
    results1 = test_menu_provider.search_items("Big Mac")
    results2 = test_menu_provider.search_items("Big Mac")

    # Modify first result
    results1[0].quantity = 42

    # Second result should be unaffected
    assert results2[0].quantity == 1


def test_get_category_returns_copies(test_menu_provider):
    """get_category() returns copies, not references."""
    items1 = test_menu_provider.get_category("Breakfast")
    items2 = test_menu_provider.get_category("Breakfast")

    # Modify first result
    items1[0].quantity = 100

    # Second result should be unaffected
    assert items2[0].quantity == 1


# ============================================================================
# Count and Utility Tests
# ============================================================================


def test_get_items_count(test_menu_provider):
    """Total items = 5 for test menu."""
    count = test_menu_provider.get_items_count()
    assert count == 5


def test_get_items_count_real_menu(real_menu_provider):
    """Total items for real menu (should be 212)."""
    count = real_menu_provider.get_items_count()
    # Verify it's a reasonable number (menu might change slightly)
    assert count >= 200
    assert count <= 250


def test_category_exists(test_menu_provider):
    """Returns True/False correctly for category existence."""
    assert test_menu_provider.category_exists("Breakfast") is True
    assert test_menu_provider.category_exists("Beef & Pork") is True
    assert test_menu_provider.category_exists("InvalidCategory") is False


def test_get_menu_returns_copy(test_menu_provider):
    """get_menu() returns a deep copy."""
    menu1 = test_menu_provider.get_menu()
    menu2 = test_menu_provider.get_menu()

    # Modify menu1
    menu1.categories["Breakfast"][0].quantity = 999

    # menu2 should be unaffected
    assert menu2.categories["Breakfast"][0].quantity == 1


# ============================================================================
# Real Menu Tests
# ============================================================================


def test_real_menu_loads_correctly(real_menu_provider):
    """Loads real menu correctly."""
    categories = real_menu_provider.get_all_categories()
    assert len(categories) >= 9  # Should have at least 9 categories


def test_real_menu_search_big_mac(real_menu_provider):
    """Can find Big Mac in real menu."""
    results = real_menu_provider.search_items("Big Mac")
    assert len(results) >= 1
    assert any(item.item_name == "Big Mac" for item in results)


def test_real_menu_get_breakfast_category(real_menu_provider):
    """Can get Breakfast category from real menu."""
    breakfast = real_menu_provider.get_category("Breakfast")
    assert len(breakfast) > 0
    assert all(item.category_name == "Breakfast" for item in breakfast)


def test_real_menu_all_items_have_category(real_menu_provider):
    """All items in real menu have valid category names."""
    categories = real_menu_provider.get_all_categories()

    for category in categories:
        items = real_menu_provider.get_category(category)
        for item in items:
            assert item.category_name == category
