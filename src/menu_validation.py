"""
Pure validation functions for menu item validation and fuzzy matching.

This module provides validation utilities for order processing with no side effects.
All functions are pure and deterministic for easy testing.
"""

from dataclasses import dataclass

from rapidfuzz import fuzz, process

from menus.mcdonalds.models import Item, Menu


@dataclass
class ValidationResult:
    """Result of a validation operation.

    Attributes:
        is_valid: Whether the validation passed
        matched_item: The matched item if validation succeeded
        confidence_score: Confidence score (0.0-100.0) for fuzzy matches
        error_message: Detailed error message if validation failed
    """

    is_valid: bool
    matched_item: Item | None = None
    confidence_score: float = 0.0
    error_message: str | None = None


def fuzzy_match_item(
    item_name: str, menu_items: list[Item], threshold: int = 85
) -> ValidationResult:
    """
    Fuzzy match an item name against menu items.

    Args:
        item_name: The item name to match (e.g., "big mac", "Big Mack")
        menu_items: List of menu items to search
        threshold: Minimum score (0-100) to accept match

    Returns:
        ValidationResult with best match if above threshold

    Examples:
        - "Big Mack" → matches "Big Mac" with high confidence
        - "chicken nuggets" → matches "Chicken McNuggets"
        - "whopper" → no match (not on menu)
    """
    if not item_name or not item_name.strip():
        return ValidationResult(
            is_valid=False, error_message="Item name cannot be empty"
        )

    if not menu_items:
        return ValidationResult(is_valid=False, error_message="Menu is empty")

    # Extract item names for matching (use lowercase for case-insensitive matching)
    item_name_mapping = {item.item_name: item for item in menu_items}
    item_names = list(item_name_mapping.keys())

    # Create lowercase mapping for case-insensitive search
    lowercase_mapping = {name.lower(): name for name in item_names}
    lowercase_names = list(lowercase_mapping.keys())

    # Use rapidfuzz to find best match (case-insensitive)
    result = process.extractOne(
        item_name.lower(), lowercase_names, scorer=fuzz.ratio, score_cutoff=threshold
    )

    if result is None:
        return ValidationResult(
            is_valid=False,
            error_message=f"No menu item found matching '{item_name}'",
        )

    matched_lowercase, score, _ = result
    # Map back to original case
    original_name = lowercase_mapping[matched_lowercase]
    matched_item = item_name_mapping[original_name]

    return ValidationResult(
        is_valid=True, matched_item=matched_item, confidence_score=float(score)
    )


def validate_item_exists(item_name: str, category: str, menu: Menu) -> ValidationResult:
    """
    Validate that an item exists in the specified category.

    First tries exact match, then falls back to fuzzy matching.

    Args:
        item_name: The item to validate
        category: The menu category
        menu: Menu data provider

    Returns:
        ValidationResult indicating if item exists
    """
    # Get items in category
    category_items = menu.get_category(category)

    if not category_items:
        return ValidationResult(
            is_valid=False, error_message=f"Category '{category}' not found in menu"
        )

    # Try exact match first (case-insensitive)
    for item in category_items:
        if item.item_name.lower() == item_name.lower():
            return ValidationResult(
                is_valid=True, matched_item=item, confidence_score=100.0
            )

    # Fall back to fuzzy matching
    return fuzzy_match_item(item_name, category_items)


def validate_modifiers(
    item: Item, requested_modifiers: list[str], fuzzy_threshold: int = 85
) -> ValidationResult:
    """
    Validate that all requested modifiers are available for the item.

    Args:
        item: The menu item
        requested_modifiers: List of modifier names requested
        fuzzy_threshold: Threshold for fuzzy matching modifier names

    Returns:
        ValidationResult indicating if all modifiers are valid

    Examples:
        - Item: Big Mac, Modifiers: ["No Pickles"] → valid
        - Item: Big Mac, Modifiers: ["Anchovies"] → invalid
    """
    if not requested_modifiers:
        # Empty modifier list is valid
        return ValidationResult(
            is_valid=True, matched_item=item, confidence_score=100.0
        )

    if not item.modifiers:
        # Item has no available modifiers
        return ValidationResult(
            is_valid=False,
            error_message=f"Item '{item.item_name}' has no modifiers available, but modifiers were requested: {requested_modifiers}",
        )

    # Build mapping of available modifiers
    available_modifier_names = [m.modifier_name for m in item.modifiers]

    invalid_modifiers = []
    for requested in requested_modifiers:
        # Try exact match first
        exact_match = any(
            m.lower() == requested.lower() for m in available_modifier_names
        )
        if exact_match:
            continue

        # Try fuzzy match
        result = process.extractOne(
            requested,
            available_modifier_names,
            scorer=fuzz.ratio,
            score_cutoff=fuzzy_threshold,
        )

        if result is None:
            invalid_modifiers.append(requested)

    if invalid_modifiers:
        return ValidationResult(
            is_valid=False,
            error_message=f"Invalid modifiers for '{item.item_name}': {invalid_modifiers}. Available modifiers: {available_modifier_names}",
        )

    return ValidationResult(is_valid=True, matched_item=item, confidence_score=100.0)


def validate_order_item(
    item_name: str,
    category: str,
    modifiers: list[str],
    menu: Menu,
    fuzzy_threshold: int = 85,
) -> ValidationResult:
    """
    Complete validation: item exists + modifiers valid.

    Convenience function that combines item existence and modifier validation.

    Args:
        item_name: The item name to validate
        category: The menu category
        modifiers: List of requested modifiers
        menu: Menu data provider
        fuzzy_threshold: Threshold for fuzzy matching

    Returns:
        ValidationResult with either success or detailed error
    """
    # First validate item exists
    item_result = validate_item_exists(item_name, category, menu)

    if not item_result.is_valid:
        return item_result

    # Then validate modifiers
    assert item_result.matched_item is not None
    return validate_modifiers(item_result.matched_item, modifiers, fuzzy_threshold)
