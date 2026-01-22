@voice-agent @order-taking @priority-1
Feature: Multi-Item Ordering
  As a McDonald's customer
  I want to order multiple different items in one session
  So that I can get a complete meal

  Background:
    Given the McDonald's menu is loaded
    And the agent is ready to take orders

  @multi-item
  Scenario: Customer orders burger and fries
    When the customer says "I'll have a Big Mac"
    Then the agent confirms the item was added
    When the customer says "and large fries"
    Then the agent confirms the item was added
    And the order contains 2 items

  @combo-order
  Scenario: Customer orders a combo meal
    When the customer says "I'll have a Big Mac"
    And the customer says "large fries"
    And the customer says "and a Coke"
    Then the order contains 3 items
    And the order contains "Big Mac" from "Beef & Pork"
    And the order contains "Large French Fries" from "Snacks & Sides"
    And the order contains "Coca-Cola" from "Beverages"

  @mixed-quantities
  Scenario: Customer orders multiple items with different quantities
    When the customer says "Two Big Macs"
    And the customer says "three orders of fries"
    And the customer says "one apple pie"
    Then the order total count is 6 items
    And the order has 3 unique items
