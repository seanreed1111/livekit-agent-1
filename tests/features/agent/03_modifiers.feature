@voice-agent @order-taking @priority-1
Feature: Item Modifiers and Customization
  As a McDonald's customer
  I want to customize my order with modifiers
  So that I can get exactly what I want

  Background:
    Given the McDonald's menu is loaded
    And the agent is ready to take orders

  @modifiers
  Scenario: Customer orders burger with no pickles
    When the customer says "Big Mac with no pickles"
    Then the agent confirms the item was added
    And the order contains "Big Mac" with modifier "No Pickles"

  @multiple-modifiers
  Scenario: Customer orders with multiple modifiers
    When the customer says "Big Mac with no pickles, extra sauce, and add bacon"
    Then the agent confirms the item was added
    And the order contains "Big Mac" with 3 modifiers

  @modifier-validation
  Scenario: Customer requests invalid modifier
    When the customer says "Big Mac with pineapple"
    Then the agent politely informs that the modifier is not available
    And the agent asks if they want the item without that modifier

  @breakfast-modifiers
  Scenario: Customer customizes breakfast item
    When the customer says "Egg McMuffin with no cheese and egg whites"
    Then the agent confirms the item was added
    And the order contains "Egg McMuffin" with modifiers "No Cheese" and "Egg Whites"
