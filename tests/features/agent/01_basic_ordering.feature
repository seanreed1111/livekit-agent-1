@voice-agent @order-taking @priority-1
Feature: Basic Single-Item Ordering
  As a McDonald's customer
  I want to order a single menu item
  So that I can quickly get my food

  Background:
    Given the McDonald's menu is loaded
    And the agent is ready to take orders

  @smoke
  Scenario: Customer orders a Big Mac
    When the customer says "I'll have a Big Mac"
    Then the agent confirms the item was added
    And the order contains 1 item
    And the order contains "Big Mac" from "Beef & Pork"

  @quantities
  Scenario: Customer orders multiple Big Macs
    When the customer says "Two Big Macs please"
    Then the agent confirms the item was added
    And the order contains 1 line item with quantity 2

  @simple-order
  Scenario: Complete basic order
    When the customer says "I'll have a Big Mac"
    Then the agent confirms the item was added
    When the customer says "that's all"
    Then the order is completed
    And a final order file is created
    And the final order contains 1 item
