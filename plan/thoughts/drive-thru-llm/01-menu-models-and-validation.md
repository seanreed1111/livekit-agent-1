# Plan 01: Menu Models and Validation (Foundation Layer)

**Created**: 2026-01-21
**Status**: Ready for Implementation
**Dependencies**: None (Foundation layer)
**Estimated Complexity**: Low-Medium

---

## Overview

This is the **foundation layer** of the McDonald's Drive-Thru Agent. It implements pure functions and data models with **zero external dependencies**. Everything in this plan is:
- Fast to test (no I/O, no API calls)
- Deterministic (no randomness)
- Pure (no side effects)
- Easy to reason about

**Success Criteria**: All unit tests pass in <1 second total.

---

## Components to Build

### 1. Enhanced Menu Models

**File**: `menus/mcdonalds/models.py` (existing, needs enhancements)

**Current State**: Already has `Item`, `Modifier`, and `Menu` classes

**Enhancements Needed**:

#### 1.1 Add `quantity` field to `Item`
```python
quantity: int = Field(default=1, description="Number of this item")
```

#### 1.2 Add `item_id` field to `Item`
```python
item_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier")
```

#### 1.3 Implement `__add__` method for `Item`
- **Purpose**: Allow combining identical items (e.g., 2 Big Macs + 1 Big Mac = 3 Big Macs)
- **Rules**:
  - Can only add items with same `item_name`
  - Can only add items with same modifiers (set equality, order doesn't matter)
  - Result has `quantity = item1.quantity + item2.quantity`
  - Result gets new `item_id`
- **Error Handling**: Raise `ValueError` if items don't match

**Example**:
```python
item1 = Item(category_name="Beef & Pork", item_name="Big Mac", quantity=1)
item2 = Item(category_name="Beef & Pork", item_name="Big Mac", quantity=2)
combined = item1 + item2  # quantity=3

# With modifiers - must match
item3 = Item(category_name="Beef & Pork", item_name="Big Mac", quantity=1)
item3.add_modifier("No Pickles")
combined = item1 + item3  # ValueError! Different modifiers
```

---

### 2. Pure Validation Functions

**File**: `src/menu_validation.py` (new)

**Purpose**: Pure functions for menu item validation and fuzzy matching

**Dependencies**:
- `rapidfuzz` library (for fuzzy string matching)
- Menu models (for type hints)

#### 2.1 Data Classes

```python
@dataclass
class ValidationResult:
    """Result of a validation operation."""
    is_valid: bool
    matched_item: Item | None = None
    confidence_score: float = 0.0
    error_message: str | None = None
```

#### 2.2 Functions to Implement

##### `fuzzy_match_item()`
```python
def fuzzy_match_item(
    item_name: str,
    menu_items: list[Item],
    threshold: int = 85
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
```

**Implementation Notes**:
- Use `rapidfuzz.process.extractOne()` with `fuzz.ratio` scorer
- Return best match only if score >= threshold
- Case-insensitive matching
- Handle empty inputs gracefully

##### `validate_item_exists()`
```python
def validate_item_exists(
    item_name: str,
    category: str,
    menu_provider: MenuProvider
) -> ValidationResult:
    """
    Validate that an item exists in the specified category.

    First tries exact match, then falls back to fuzzy matching.

    Args:
        item_name: The item to validate
        category: The menu category
        menu_provider: Menu data provider

    Returns:
        ValidationResult indicating if item exists
    """
```

**Implementation Notes**:
- First try exact match (case-insensitive)
- If no exact match, try fuzzy match
- Return detailed error message if not found

##### `validate_modifiers()`
```python
def validate_modifiers(
    item: Item,
    requested_modifiers: list[str],
    fuzzy_threshold: int = 85
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
```

**Implementation Notes**:
- Use fuzzy matching for modifier names too
- Return list of invalid modifiers in error message
- Handle "No X" style modifiers (removal)

##### `validate_order_item()` (Convenience Function)
```python
def validate_order_item(
    item_name: str,
    category: str,
    modifiers: list[str],
    menu_provider: MenuProvider,
    fuzzy_threshold: int = 85
) -> ValidationResult:
    """
    Complete validation: item exists + modifiers valid.

    Convenience function that combines item existence and modifier validation.

    Returns:
        ValidationResult with either success or detailed error
    """
```

---

## Testing Strategy

### Unit Tests for Menu Models

**File**: `tests/test_menu_models.py` (enhance existing)

**New Tests**:

1. **Test `quantity` field default**
   ```python
   def test_item_quantity_defaults_to_one():
       item = Item(category_name="Beef & Pork", item_name="Big Mac")
       assert item.quantity == 1
   ```

2. **Test `item_id` generation**
   ```python
   def test_item_id_is_unique():
       item1 = Item(category_name="Beef & Pork", item_name="Big Mac")
       item2 = Item(category_name="Beef & Pork", item_name="Big Mac")
       assert item1.item_id != item2.item_id
   ```

3. **Test `__add__` with same items**
   ```python
   def test_add_identical_items():
       item1 = Item(category_name="Beef & Pork", item_name="Big Mac", quantity=1)
       item2 = Item(category_name="Beef & Pork", item_name="Big Mac", quantity=2)
       combined = item1 + item2
       assert combined.quantity == 3
       assert combined.item_name == "Big Mac"
   ```

4. **Test `__add__` with different modifiers fails**
   ```python
   def test_add_items_with_different_modifiers_raises_error():
       item1 = Item(category_name="Beef & Pork", item_name="Big Mac")
       item2 = Item(category_name="Beef & Pork", item_name="Big Mac")
       item2.add_modifier("No Pickles")

       with pytest.raises(ValueError):
           combined = item1 + item2
   ```

5. **Test `__add__` with same modifiers (different order)**
   ```python
   def test_add_items_with_same_modifiers_different_order():
       item1 = Item(category_name="Beef & Pork", item_name="Big Mac")
       item1.add_modifier("No Pickles")
       item1.add_modifier("Extra Sauce")

       item2 = Item(category_name="Beef & Pork", item_name="Big Mac")
       item2.add_modifier("Extra Sauce")
       item2.add_modifier("No Pickles")

       combined = item1 + item2
       assert combined.quantity == 2
   ```

### Unit Tests for Validation Functions

**File**: `tests/test_menu_validation.py` (new)

**Tests** (aim for 20+ tests, fast execution):

#### Fuzzy Matching Tests

1. `test_fuzzy_match_exact_match()` - "Big Mac" → "Big Mac" (100% confidence)
2. `test_fuzzy_match_case_insensitive()` - "big mac" → "Big Mac"
3. `test_fuzzy_match_typo()` - "Big Mack" → "Big Mac"
4. `test_fuzzy_match_synonym()` - "chicken nuggets" → "Chicken McNuggets"
5. `test_fuzzy_match_no_match()` - "whopper" → None
6. `test_fuzzy_match_below_threshold()` - "pizza" → None (no valid match)
7. `test_fuzzy_match_empty_input()` - "" → error
8. `test_fuzzy_match_empty_menu()` - any input with empty menu → None

#### Item Validation Tests

9. `test_validate_item_exists_exact_match()`
10. `test_validate_item_exists_fuzzy_match()`
11. `test_validate_item_not_in_category()`
12. `test_validate_item_wrong_category()`
13. `test_validate_item_invalid_name()`

#### Modifier Validation Tests

14. `test_validate_modifiers_all_valid()`
15. `test_validate_modifiers_one_invalid()`
16. `test_validate_modifiers_empty_list()` - should be valid
17. `test_validate_modifiers_fuzzy_match()` - "no pickles" → "No Pickles"
18. `test_validate_modifiers_no_modifiers_available()` - item has no modifiers

#### Combined Validation Tests

19. `test_validate_order_item_success()`
20. `test_validate_order_item_invalid_item()`
21. `test_validate_order_item_invalid_modifier()`
22. `test_validate_order_item_both_invalid()`

**Test Data Setup**:
```python
@pytest.fixture
def sample_menu_items():
    """Create a small test menu."""
    return [
        Item(category_name="Beef & Pork", item_name="Big Mac"),
        Item(category_name="Beef & Pork", item_name="Quarter Pounder"),
        Item(category_name="Chicken & Fish", item_name="Chicken McNuggets"),
    ]

@pytest.fixture
def big_mac_with_modifiers():
    """Create a Big Mac with available modifiers."""
    item = Item(category_name="Beef & Pork", item_name="Big Mac")
    item.add_modifier("No Pickles")
    item.add_modifier("Extra Sauce")
    item.add_modifier("No Onions")
    return item
```

---

## BDD Scenarios (Behavior Testing)

While this layer is primarily tested with unit tests, some behaviors map to BDD scenarios:

### Related BDD Scenarios:
- **Scenario 5.1** (Invalid menu item) - depends on `validate_item_exists()`
- **Scenario 5.3** (Invalid modifier) - depends on `validate_modifiers()`
- **Scenario 5.4** (STT error recovery) - depends on `fuzzy_match_item()`

**BDD Step Definitions** (to be implemented in later phases):
```python
@then("the agent informs the customer the item is not available")
def step_impl(context):
    # Internally uses validate_item_exists()
    pass

@then("the agent confirms 'Big Mac' using fuzzy matching")
def step_impl(context):
    # Internally uses fuzzy_match_item()
    pass
```

---

## Implementation Checklist

### Phase 1: Menu Model Enhancements
- [ ] Add `quantity: int = 1` field to `Item` class
- [ ] Add `item_id: str = uuid4()` field to `Item` class
- [ ] Implement `__add__()` method on `Item` class
- [ ] Write unit tests for `quantity` field
- [ ] Write unit tests for `item_id` uniqueness
- [ ] Write unit tests for `__add__()` success cases
- [ ] Write unit tests for `__add__()` error cases
- [ ] Run tests: `uv run pytest tests/test_menu_models.py -v`
- [ ] Verify all tests pass in <1 second

### Phase 2: Validation Functions
- [ ] Create `src/menu_validation.py`
- [ ] Define `ValidationResult` dataclass
- [ ] Implement `fuzzy_match_item()` function
- [ ] Implement `validate_item_exists()` function
- [ ] Implement `validate_modifiers()` function
- [ ] Implement `validate_order_item()` function
- [ ] Add type hints to all functions
- [ ] Add docstrings to all functions

### Phase 3: Validation Tests
- [ ] Create `tests/test_menu_validation.py`
- [ ] Write fuzzy matching tests (8 tests)
- [ ] Write item validation tests (5 tests)
- [ ] Write modifier validation tests (5 tests)
- [ ] Write combined validation tests (4 tests)
- [ ] Add test fixtures for menu items
- [ ] Run tests: `uv run pytest tests/test_menu_validation.py -v`
- [ ] Verify all tests pass in <1 second
- [ ] Check code coverage: `uv run pytest --cov=src.menu_validation`
- [ ] Aim for 100% coverage on pure functions

### Phase 4: Edge Cases and Refinement
- [ ] Test with empty inputs
- [ ] Test with special characters in item names
- [ ] Test with very long item names
- [ ] Test with unicode characters
- [ ] Optimize fuzzy matching threshold if needed
- [ ] Document any edge cases found

### Phase 5: Integration Prep
- [ ] Verify all type hints are correct
- [ ] Verify all docstrings are complete
- [ ] Run formatter: `uv run ruff format src/menu_validation.py`
- [ ] Run linter: `uv run ruff check src/menu_validation.py`
- [ ] Commit changes with clear message

---

## Success Criteria

✅ **All unit tests pass** (22+ tests)
✅ **Tests run in <1 second** (pure functions, no I/O)
✅ **100% code coverage** on validation functions
✅ **No external dependencies** (except rapidfuzz and menu models)
✅ **Type hints complete** (passes mypy --strict)
✅ **Docstrings complete** (all public functions documented)
✅ **Fuzzy matching works** for common typos and variations
✅ **Clear error messages** for validation failures

---

## Dependencies for Next Plans

**This plan provides**:
- ✅ Enhanced `Item` model with `quantity` and `item_id`
- ✅ `__add__()` method for combining items
- ✅ `ValidationResult` dataclass
- ✅ Pure validation functions
- ✅ Foundation for all order taking logic

**Next plans can now use**:
- `fuzzy_match_item()` for STT error handling
- `validate_item_exists()` for menu validation
- `validate_modifiers()` for customization validation
- `validate_order_item()` for complete order validation

---

## Notes

- This layer has **zero side effects** - all functions are pure
- This layer is **fast to test** - no I/O, no API calls
- This layer is **easy to debug** - deterministic behavior
- This layer is **reusable** - functions can be used anywhere
- This layer enables **TDD** - write test first, implement, iterate quickly

**Key Principle**: Build a solid foundation before adding complexity. Pure functions are the most reliable building blocks.
