@voice-agent @order-taking @priority-1
Feature: Order Corrections and Changes
  As a McDonald's customer
  I want to modify my order before finalizing
  So that I can correct mistakes

  Background:
    Given the McDonald's menu is loaded
    And the agent is ready to take orders
    And the customer has ordered "Big Mac"
    And the customer has ordered "Large French Fries"

  @remove-item
  Scenario: Customer removes an item from order
    When the customer says "actually, remove the fries"
    Then the agent confirms the item was removed
    And the order contains only 1 item
    And the order contains "Big Mac"

  @change-quantity
  Scenario: Customer changes item quantity
    When the customer says "make that two Big Macs instead"
    Then the agent confirms the quantity was updated
    And the order contains "Big Mac" with quantity 2

  @replace-item
  Scenario: Customer replaces an item
    When the customer says "change the Big Mac to a Quarter Pounder"
    Then the agent confirms the change
    And the order does not contain "Big Mac"
    And the order contains "Quarter Pounder"
