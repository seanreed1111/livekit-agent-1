# BDD Testing Strategy for McDonald's Drive-Thru Agent

**Created**: 2026-01-21
**Purpose**: Define minimal set of behavior-driven scenarios for testing the drive-thru agent's behavior, not its implementation

---

## Overview

This document outlines a minimal but comprehensive set of BDD scenarios using Gherkin syntax to validate the McDonald's Drive-Thru Agent's behavior from a customer perspective. These scenarios test **what the system does**, not **how it does it**.

### Testing Principles

1. **Behavior-Focused**: Test observable customer interactions, not internal implementation
2. **Black-Box**: Treat the agent as a black box - input (voice) → output (response + order file)
3. **User Perspective**: Write scenarios from the customer's point of view
4. **End-to-End**: Each scenario covers a complete customer journey
5. **Implementation-Agnostic**: Scenarios should remain valid even if internal architecture changes

---

## Feature File Organization

```
tests/features/agent/
├── 01_basic_ordering.feature          # Simple, single-item orders
├── 02_multi_item_ordering.feature     # Multiple items in one order
├── 03_modifiers.feature               # Items with customizations
├── 04_order_corrections.feature       # Fixing mistakes
├── 05_error_handling.feature          # Invalid items and edge cases
└── 06_order_completion.feature        # Finishing and confirming orders
```

---

## 1. Basic Ordering (`01_basic_ordering.feature`)

**Purpose**: Verify the agent can handle simple, straightforward orders

### Scenarios

#### Scenario 1.1: Order a single menu item
```gherkin
Feature: Basic Single-Item Ordering
  As a customer
  I want to order a single item
  So that I can get my food quickly

  Scenario: Customer orders a Big Mac
    Given the agent greets the customer
    When the customer says "I'll have a Big Mac"
    Then the agent confirms "one Big Mac"
    And the agent asks if the customer wants anything else
    When the customer says "that's all"
    Then the agent reads back the complete order
    And the order file contains 1 item
    And the order file shows "Big Mac" in category "Beef & Pork"
```

#### Scenario 1.2: Order with explicit quantity
```gherkin
  Scenario: Customer orders multiple quantities of same item
    Given the agent greets the customer
    When the customer says "Two Big Macs please"
    Then the agent confirms "two Big Macs"
    And the agent asks if the customer wants anything else
    When the customer says "no thanks"
    Then the order file contains 1 line item with quantity 2
```

#### Scenario 1.3: Order from breakfast menu
```gherkin
  Scenario: Customer orders a breakfast item
    Given the agent greets the customer
    When the customer says "I'd like an Egg McMuffin"
    Then the agent confirms the item
    And the order file shows the item in category "Breakfast"
```

---

## 2. Multi-Item Ordering (`02_multi_item_ordering.feature`)

**Purpose**: Verify the agent can handle orders with multiple different items

### Scenarios

#### Scenario 2.1: Order multiple items sequentially
```gherkin
Feature: Multi-Item Ordering
  As a customer
  I want to order several different items
  So that I can get everything I need

  Scenario: Customer orders items one at a time
    Given the agent greets the customer
    When the customer says "I'll have a Big Mac"
    Then the agent confirms "one Big Mac"
    When the customer says "and a medium fries"
    Then the agent confirms "one medium fries"
    When the customer says "and a Coke"
    Then the agent confirms the Coke
    When the customer says "that's it"
    Then the order file contains 3 items
    And the order includes "Big Mac", "Medium Fries", and a beverage
```

#### Scenario 2.2: Order multiple items in one utterance
```gherkin
  Scenario: Customer lists multiple items at once
    Given the agent greets the customer
    When the customer says "I want a Big Mac, large fries, and a Sprite"
    Then the agent confirms all three items
    And the order file contains 3 items
```

#### Scenario 2.3: Mix of quantities and items
```gherkin
  Scenario: Customer orders mix of single and multiple items
    Given the agent greets the customer
    When the customer says "Two Big Macs and one large fries"
    Then the agent confirms "two Big Macs and one large fries"
    And the order file contains 2 line items
    And one line item has quantity 2
    And one line item has quantity 1
```

---

## 3. Modifiers and Customizations (`03_modifiers.feature`)

**Purpose**: Verify the agent correctly captures item customizations

### Scenarios

#### Scenario 3.1: Item with modifier
```gherkin
Feature: Order Customization
  As a customer
  I want to customize my items
  So that I get exactly what I want

  Scenario: Customer adds cheese to Quarter Pounder
    Given the agent greets the customer
    When the customer says "Quarter Pounder with cheese"
    Then the agent confirms the item with the modifier
    And the order file shows "Quarter Pounder" with modifier "Cheese"
```

#### Scenario 3.2: Item with removal modifier
```gherkin
  Scenario: Customer requests no pickles
    Given the agent greets the customer
    When the customer says "Big Mac with no pickles"
    Then the agent confirms "Big Mac, no pickles"
    And the order file shows the "no pickles" modifier
```

#### Scenario 3.3: Multiple modifiers on one item
```gkerkin
  Scenario: Customer requests multiple customizations
    Given the agent greets the customer
    When the customer says "Big Mac with no pickles and extra sauce"
    Then the agent confirms both modifiers
    And the order file shows both "no pickles" and "extra sauce" modifiers
```

#### Scenario 3.4: Different modifiers on same item type
```gherkin
  Scenario: Customer orders two Big Macs with different customizations
    Given the agent greets the customer
    When the customer says "Two Big Macs, one with no pickles"
    Then the agent confirms one regular Big Mac and one without pickles
    And the order file contains 2 separate line items for Big Mac
    And one line item has "no pickles" modifier
    And one line item has no modifiers
```

---

## 4. Order Corrections (`04_order_corrections.feature`)

**Purpose**: Verify the agent can handle customer corrections and changes

### Scenarios

#### Scenario 4.1: Correct item before confirming
```gherkin
Feature: Order Corrections
  As a customer
  I want to correct mistakes in my order
  So that I get what I actually want

  Scenario: Customer corrects item immediately
    Given the agent greets the customer
    When the customer says "I want a Big Mac"
    And the customer says "actually, make that a McDouble"
    Then the agent acknowledges the correction
    And the order file contains "McDouble"
    And the order file does not contain "Big Mac"
```

#### Scenario 4.2: Change quantity
```gherkin
  Scenario: Customer changes quantity of an item
    Given the agent greets the customer
    When the customer says "Two Big Macs"
    And the customer says "actually make that three Big Macs"
    Then the agent confirms "three Big Macs"
    And the order file shows quantity 3 for Big Mac
```

#### Scenario 4.3: Remove item from order
```gherkin
  Scenario: Customer removes an item
    Given the agent has confirmed "Big Mac" and "fries"
    When the customer says "actually, skip the fries"
    Then the agent acknowledges the removal
    And the order file contains only "Big Mac"
    And the order file does not contain "fries"
```

---

## 5. Error Handling (`05_error_handling.feature`)

**Purpose**: Verify the agent handles invalid requests gracefully

### Scenarios

#### Scenario 5.1: Invalid menu item
```gherkin
Feature: Error Handling
  As a customer
  I want to be informed when I request something unavailable
  So that I can make a valid choice

  Scenario: Customer requests item not on menu
    Given the agent greets the customer
    When the customer says "I want a Whopper"
    Then the agent politely informs the customer the item is not available
    And the agent suggests looking at the menu
    And the order file remains empty
```

#### Scenario 5.2: Ambiguous request
```gherkin
  Scenario: Customer makes unclear request
    Given the agent greets the customer
    When the customer says "I want a burger"
    Then the agent asks for clarification
    And the agent may suggest specific burger options
    And the order file remains empty until clarified
```

#### Scenario 5.3: Invalid modifier
```gherkin
  Scenario: Customer requests unavailable customization
    Given the agent greets the customer
    When the customer says "Big Mac with anchovies"
    Then the agent informs the customer that modifier is not available
    And the agent may suggest valid modifiers
    And no item is added to the order
```

#### Scenario 5.4: STT error recovery
```gherkin
  Scenario: Customer's words are misheard but corrected
    Given the agent greets the customer
    When the customer says something that sounds like "Big Mack"
    Then the agent confirms "Big Mac" using fuzzy matching
    And the order file contains "Big Mac" (correct spelling)
```

---

## 6. Order Completion (`06_order_completion.feature`)

**Purpose**: Verify the agent properly finalizes orders

### Scenarios

#### Scenario 6.1: Complete a simple order
```gherkin
Feature: Order Completion
  As a customer
  I want my order to be finalized correctly
  So that I receive what I ordered

  Scenario: Customer completes order
    Given the agent has confirmed "Big Mac" and "fries"
    When the customer says "that's all"
    Then the agent reads back the complete order
    And the agent thanks the customer
    And a final order JSON file is created
    And the JSON file contains all items
    And the JSON file has correct quantities
```

#### Scenario 6.2: Cancel entire order
```gherkin
  Scenario: Customer cancels order
    Given the agent has confirmed "Big Mac" and "fries"
    When the customer says "actually, cancel that"
    Then the agent acknowledges the cancellation
    And the order file is empty or marked as cancelled
```

#### Scenario 6.3: Final confirmation and correction
```gherkin
  Scenario: Customer corrects during final readback
    Given the agent has confirmed "Big Mac", "fries", and "Coke"
    When the agent reads back the order
    And the customer says "no, I wanted a Sprite not a Coke"
    Then the agent corrects the order
    And the final order file shows "Sprite"
    And the final order file does not contain "Coke"
```

---

## Minimal Test Coverage Matrix

### Priority 1: Core Behaviors (Must Have)
| Feature | Scenarios | Coverage |
|---------|-----------|----------|
| Basic Ordering | 1.1, 1.2 | Single item, quantities |
| Multi-Item | 2.1 | Sequential ordering |
| Modifiers | 3.1 | Basic customization |
| Error Handling | 5.1, 5.2 | Invalid items, ambiguity |
| Completion | 6.1 | Finalize order |

**Total**: ~8 scenarios for smoke testing

### Priority 2: Extended Coverage (Should Have)
| Feature | Additional Scenarios | Coverage |
|---------|---------------------|----------|
| Basic Ordering | 1.3 | Category coverage (breakfast) |
| Multi-Item | 2.2, 2.3 | Bulk ordering, mixed quantities |
| Modifiers | 3.2, 3.3, 3.4 | Removals, multiple mods, variations |
| Corrections | 4.1, 4.2, 4.3 | All correction types |
| Error Handling | 5.3, 5.4 | Invalid mods, STT recovery |
| Completion | 6.2, 6.3 | Cancellation, final corrections |

**Total**: ~18 scenarios for comprehensive testing

### Priority 3: Edge Cases (Nice to Have)
- Ordering from multiple categories
- Very large orders (10+ items)
- Rapid corrections (multiple changes)
- Silence handling (customer doesn't respond)
- Interruptions (customer talks over agent)

---

## Test Data Requirements

### Menu Items to Cover
- **Breakfast**: Egg McMuffin, Hash Browns
- **Beef & Pork**: Big Mac, Quarter Pounder, McDouble
- **Chicken & Fish**: Chicken McNuggets, Filet-O-Fish
- **Snacks & Sides**: Fries (Small, Medium, Large), Apple Slices
- **Beverages**: Coke, Sprite, Water
- **Coffee & Tea**: Coffee (various sizes)
- **Desserts**: Apple Pie, McFlurry
- **Smoothies & Shakes**: Chocolate Shake

### Modifiers to Test
- Additions: "with cheese", "extra sauce", "add bacon"
- Removals: "no pickles", "no onions", "no ice"
- Substitutions: "egg whites instead of regular eggs"

### Invalid Items (for error testing)
- Whopper (Burger King)
- Baconator (Wendy's)
- "Pizza" (not on menu)

---

## Implementation Guidelines

### Given/When/Then Structure

**Given**: Set up the initial state
- Agent state (greeted, mid-order, etc.)
- Existing order contents
- Session context

**When**: The action/input
- Customer utterance (what they say)
- Should be realistic voice input

**Then**: Expected outcomes
- Agent response (tone, content)
- Order state (what's in the order file)
- File system state (what files exist)

### Assertion Types

#### Agent Response Assertions (Behavioral)
```gherkin
Then the agent confirms "one Big Mac"
Then the agent asks if the customer wants anything else
Then the agent politely informs the customer
Then the agent reads back the complete order
```

#### Order State Assertions (Observable)
```gherkin
Then the order file contains 3 items
Then the order file shows "Big Mac" in category "Beef & Pork"
Then one line item has quantity 2
Then the order file does not contain "fries"
```

#### Avoid Implementation Assertions (Internal)
```gherkin
# ❌ Don't do this (implementation detail)
Then the OrderStateManager.add_item was called
Then the fuzzy_match_item function returned 0.95
Then the DriveThruLLM injected menu context

# ✓ Do this instead (observable behavior)
Then the order file contains "Big Mac"
Then the agent confirms the item
Then the order is recorded correctly
```

---

## BDD Test Execution

### Step Definition Categories

1. **Setup Steps** (Given)
   - `Given the agent greets the customer`
   - `Given the agent has confirmed "Big Mac" and "fries"`
   - `Given the customer is mid-order`

2. **Action Steps** (When)
   - `When the customer says "{utterance}"`
   - `When the customer says "that's all"`
   - `When the agent reads back the order`

3. **Verification Steps** (Then)
   - `Then the agent confirms "{item}"`
   - `Then the order file contains {n} items`
   - `Then the order file shows "{item}" in category "{category}"`
   - `Then the JSON file has correct quantities`

### Judge-Based Assertions

For natural language responses, use LLM judge:

```python
@then('the agent confirms "one Big Mac"')
def verify_agent_confirmation(context):
    # Use judge to verify intent, not exact wording
    await result.expect.next_event().is_message(role="assistant").judge(
        judge_llm,
        intent="Confirms that one Big Mac was added and asks if customer wants more"
    )
```

### File System Assertions

For order files, use direct JSON comparison:

```python
@then('the order file contains {n:d} items')
def verify_order_count(context, n):
    order = load_order_json(context.session_id)
    assert len(order['items']) == n
```

---

## Continuous Testing Strategy

### Test Pyramid for BDD Scenarios

```
        /\
       /  \      E2E BDD Scenarios (~18 scenarios)
      /____\     Full voice pipeline, judge-based
     /      \
    /        \   Integration Tests (~30 tests)
   /__________\  Component interactions, mocked LLM
  /            \
 /              \ Unit Tests (~100+ tests)
/________________\ Pure functions, data models
```

### When to Run

- **On every commit**: Priority 1 scenarios (smoke tests)
- **On PR**: Priority 1 + Priority 2 scenarios
- **Nightly**: Full suite including edge cases
- **Before release**: Full suite + manual exploratory testing

### Success Criteria

- **All Priority 1 scenarios pass**: Required for merge
- **95%+ Priority 2 pass rate**: Required for release
- **Zero regressions**: New features don't break existing scenarios

---

## Example: Complete Feature File

Here's what a complete feature file would look like:

```gherkin
# tests/features/agent/01_basic_ordering.feature

@voice-agent @order-taking @priority-1
Feature: Basic Single-Item Ordering
  As a McDonald's customer
  I want to order a single menu item
  So that I can quickly get my food

  Background:
    Given the McDonald's menu is loaded
    And the agent is ready to take orders

  @smoke
  Scenario: Order a Big Mac
    Given the agent greets the customer
    When the customer says "I'll have a Big Mac"
    Then the agent confirms "one Big Mac"
    And the agent asks if the customer wants anything else
    When the customer says "that's all"
    Then the agent reads back the complete order
    And a final order JSON file is created
    And the order file contains 1 item
    And the order file shows "Big Mac" in category "Beef & Pork"
    And the item has quantity 1
    And the item has no modifiers

  @quantities
  Scenario: Order multiple Big Macs
    Given the agent greets the customer
    When the customer says "Two Big Macs please"
    Then the agent confirms "two Big Macs"
    And the agent asks if the customer wants anything else
    When the customer says "no thanks"
    Then the order file contains 1 line item
    And the line item has quantity 2

  @breakfast
  Scenario: Order breakfast item
    Given the agent greets the customer
    When the customer says "I'd like an Egg McMuffin"
    Then the agent confirms "one Egg McMuffin"
    When the customer says "that's it"
    Then the order file shows "Egg McMuffin" in category "Breakfast"
```

---

## Key Takeaways

1. **Test Behavior, Not Implementation**: Focus on what customers experience
2. **Minimal but Comprehensive**: 18 scenarios cover all critical paths
3. **Priority-Based**: Start with 8 smoke tests, expand to 18 for full coverage
4. **Implementation-Agnostic**: Tests survive architecture refactoring
5. **Realistic**: Use natural customer language, not technical terms
6. **Observable**: Assert on files, responses, and end-user visible state
7. **Maintainable**: Clear structure, reusable steps, good organization

---

## Next Steps

1. **Review this strategy** with the team
2. **Write actual feature files** following the examples above
3. **Implement step definitions** for Given/When/Then steps
4. **Set up test data** (menu JSON, invalid items)
5. **Configure test runner** (pytest-bdd or behave)
6. **Run Priority 1** scenarios to validate approach
7. **Iterate** based on real test results
8. **Expand** to Priority 2 and Priority 3 as needed

This BDD testing strategy ensures the McDonald's Drive-Thru Agent behaves correctly from a customer perspective, regardless of internal implementation details.
