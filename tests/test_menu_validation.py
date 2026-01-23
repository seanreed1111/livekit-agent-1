"""
Unit tests for menu validation functions.

Tests cover:
- Fuzzy matching with various inputs
- Item existence validation
- Modifier validation
- Combined validation
"""

import pytest

from menu_validation import (
    ValidationResult,
    fuzzy_match_item,
    validate_item_exists,
    validate_modifiers,
    validate_order_item,
)

# Fuzzy Matching Tests


class TestFuzzyMatchItem:
    """Tests for fuzzy_match_item() function."""

    def test_fuzzy_match_exact_match(self, sample_menu_items):
        """Test exact match returns 100% confidence."""
        result = fuzzy_match_item("Big Mac", sample_menu_items)

        assert result.is_valid is True
        assert result.matched_item is not None
        assert result.matched_item.item_name == "Big Mac"
        assert result.confidence_score == 100.0

    def test_fuzzy_match_case_insensitive(self, sample_menu_items):
        """Test case-insensitive matching."""
        result = fuzzy_match_item("big mac", sample_menu_items)

        assert result.is_valid is True
        assert result.matched_item is not None
        assert result.matched_item.item_name == "Big Mac"

    def test_fuzzy_match_typo(self, sample_menu_items):
        """Test matching with typo."""
        result = fuzzy_match_item("Big Mack", sample_menu_items)

        assert result.is_valid is True
        assert result.matched_item is not None
        assert result.matched_item.item_name == "Big Mac"
        assert result.confidence_score >= 85.0

    def test_fuzzy_match_synonym(self, sample_menu_items):
        """Test matching with common synonym."""
        result = fuzzy_match_item("chicken nuggets", sample_menu_items)

        assert result.is_valid is True
        assert result.matched_item is not None
        assert result.matched_item.item_name == "Chicken McNuggets"

    def test_fuzzy_match_no_match(self, sample_menu_items):
        """Test item not on menu returns no match."""
        result = fuzzy_match_item("whopper", sample_menu_items)

        assert result.is_valid is False
        assert result.matched_item is None
        assert "No menu item found" in result.error_message

    def test_fuzzy_match_below_threshold(self, sample_menu_items):
        """Test item below threshold returns no match."""
        result = fuzzy_match_item("pizza", sample_menu_items, threshold=90)

        assert result.is_valid is False
        assert result.matched_item is None

    def test_fuzzy_match_empty_input(self, sample_menu_items):
        """Test empty input returns error."""
        result = fuzzy_match_item("", sample_menu_items)

        assert result.is_valid is False
        assert result.error_message == "Item name cannot be empty"

    def test_fuzzy_match_empty_menu(self):
        """Test empty menu returns error."""
        result = fuzzy_match_item("Big Mac", [])

        assert result.is_valid is False
        assert result.error_message == "Menu is empty"

    def test_fuzzy_match_whitespace_input(self, sample_menu_items):
        """Test whitespace-only input is treated as empty."""
        result = fuzzy_match_item("   ", sample_menu_items)

        assert result.is_valid is False
        assert "empty" in result.error_message.lower()


# Item Validation Tests


class TestValidateItemExists:
    """Tests for validate_item_exists() function."""

    def test_validate_item_exists_exact_match(self, sample_menu):
        """Test exact match in category."""
        result = validate_item_exists("Big Mac", "Beef & Pork", sample_menu)

        assert result.is_valid is True
        assert result.matched_item is not None
        assert result.matched_item.item_name == "Big Mac"
        assert result.confidence_score == 100.0

    def test_validate_item_exists_fuzzy_match(self, sample_menu):
        """Test fuzzy match in category."""
        result = validate_item_exists("Big Mack", "Beef & Pork", sample_menu)

        assert result.is_valid is True
        assert result.matched_item is not None
        assert result.matched_item.item_name == "Big Mac"

    def test_validate_item_not_in_category(self, sample_menu):
        """Test item exists but in wrong category."""
        result = validate_item_exists("Big Mac", "Chicken & Fish", sample_menu)

        assert result.is_valid is False
        assert result.matched_item is None

    def test_validate_item_wrong_category(self, sample_menu):
        """Test invalid category name."""
        result = validate_item_exists("Big Mac", "Invalid Category", sample_menu)

        assert result.is_valid is False
        assert "not found in menu" in result.error_message

    def test_validate_item_invalid_name(self, sample_menu):
        """Test item name not on menu."""
        result = validate_item_exists("Whopper", "Beef & Pork", sample_menu)

        assert result.is_valid is False
        assert result.matched_item is None

    def test_validate_item_case_insensitive(self, sample_menu):
        """Test case-insensitive exact matching."""
        result = validate_item_exists("big mac", "Beef & Pork", sample_menu)

        assert result.is_valid is True
        assert result.matched_item.item_name == "Big Mac"


# Modifier Validation Tests


class TestValidateModifiers:
    """Tests for validate_modifiers() function."""

    def test_validate_modifiers_all_valid(self, big_mac_with_modifiers):
        """Test all requested modifiers are valid."""
        result = validate_modifiers(
            big_mac_with_modifiers, ["No Pickles", "Extra Sauce"]
        )

        assert result.is_valid is True
        assert result.matched_item is not None

    def test_validate_modifiers_one_invalid(self, big_mac_with_modifiers):
        """Test one invalid modifier fails validation."""
        result = validate_modifiers(big_mac_with_modifiers, ["No Pickles", "Anchovies"])

        assert result.is_valid is False
        assert "Anchovies" in result.error_message
        assert "Invalid modifiers" in result.error_message

    def test_validate_modifiers_empty_list(self, big_mac_with_modifiers):
        """Test empty modifier list is valid."""
        result = validate_modifiers(big_mac_with_modifiers, [])

        assert result.is_valid is True
        assert result.confidence_score == 100.0

    def test_validate_modifiers_fuzzy_match(self, big_mac_with_modifiers):
        """Test fuzzy matching for modifier names."""
        result = validate_modifiers(big_mac_with_modifiers, ["no pickles"])

        assert result.is_valid is True

    def test_validate_modifiers_no_modifiers_available(self, item_without_modifiers):
        """Test item with no available modifiers."""
        result = validate_modifiers(item_without_modifiers, ["Extra Ice"])

        assert result.is_valid is False
        assert "no modifiers available" in result.error_message

    def test_validate_modifiers_multiple_invalid(self, big_mac_with_modifiers):
        """Test multiple invalid modifiers."""
        result = validate_modifiers(
            big_mac_with_modifiers, ["Anchovies", "Pineapple", "No Pickles"]
        )

        assert result.is_valid is False
        assert "Anchovies" in result.error_message
        assert "Pineapple" in result.error_message

    def test_validate_modifiers_all_invalid(self, big_mac_with_modifiers):
        """Test all modifiers invalid."""
        result = validate_modifiers(big_mac_with_modifiers, ["Anchovies", "Pineapple"])

        assert result.is_valid is False
        assert len(result.error_message) > 0


# Combined Validation Tests


class TestValidateOrderItem:
    """Tests for validate_order_item() convenience function."""

    def test_validate_order_item_success(self, sample_menu):
        """Test successful validation of item with modifiers."""
        result = validate_order_item(
            "Big Mac", "Beef & Pork", ["No Pickles"], sample_menu
        )

        assert result.is_valid is True
        assert result.matched_item is not None
        assert result.matched_item.item_name == "Big Mac"

    def test_validate_order_item_invalid_item(self, sample_menu):
        """Test validation fails for invalid item."""
        result = validate_order_item("Whopper", "Beef & Pork", [], sample_menu)

        assert result.is_valid is False
        assert result.matched_item is None

    def test_validate_order_item_invalid_modifier(self, sample_menu):
        """Test validation fails for invalid modifier."""
        result = validate_order_item(
            "Big Mac", "Beef & Pork", ["Anchovies"], sample_menu
        )

        assert result.is_valid is False
        assert "Anchovies" in result.error_message

    def test_validate_order_item_both_invalid(self, sample_menu):
        """Test validation fails when both item and modifiers invalid."""
        result = validate_order_item(
            "Whopper", "Beef & Pork", ["Anchovies"], sample_menu
        )

        assert result.is_valid is False
        # Should fail on item validation first
        assert result.matched_item is None

    def test_validate_order_item_no_modifiers(self, sample_menu):
        """Test validation with no modifiers requested."""
        result = validate_order_item("Big Mac", "Beef & Pork", [], sample_menu)

        assert result.is_valid is True
        assert result.matched_item.item_name == "Big Mac"

    def test_validate_order_item_fuzzy_item_match(self, sample_menu):
        """Test validation with fuzzy item matching."""
        result = validate_order_item(
            "Big Mack", "Beef & Pork", ["No Pickles"], sample_menu
        )

        assert result.is_valid is True
        assert result.matched_item.item_name == "Big Mac"


# Edge Cases and Integration Tests


class TestValidationEdgeCases:
    """Tests for edge cases and integration scenarios."""

    def test_validation_result_dataclass(self):
        """Test ValidationResult can be created."""
        result = ValidationResult(
            is_valid=True,
            matched_item=None,
            confidence_score=95.5,
            error_message=None,
        )

        assert result.is_valid is True
        assert result.confidence_score == 95.5

    def test_validation_result_defaults(self):
        """Test ValidationResult default values."""
        result = ValidationResult(is_valid=False)

        assert result.matched_item is None
        assert result.confidence_score == 0.0
        assert result.error_message is None

    def test_fuzzy_threshold_customization(self, sample_menu_items):
        """Test custom fuzzy threshold."""
        # Lower threshold should match more loosely
        result_low = fuzzy_match_item("mac", sample_menu_items, threshold=60)
        assert result_low.is_valid is True

        # Higher threshold should be stricter
        result_high = fuzzy_match_item("mac", sample_menu_items, threshold=95)
        assert result_high.is_valid is False
