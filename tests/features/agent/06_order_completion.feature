@voice-agent @order-taking @priority-1
Feature: Order Completion and Confirmation
  As a McDonald's customer
  I want to finalize and confirm my order
  So that I know my order is correct before paying

  Background:
    Given the McDonald's menu is loaded
    And the agent is ready to take orders

  @complete-order
  Scenario: Customer completes a simple order
    Given the customer has ordered "Big Mac"
    And the customer has ordered "Large French Fries"
    When the customer says "that's all"
    Then the agent reads back the complete order
    And the agent asks for confirmation
    When the customer says "yes"
    Then the order is marked as complete
    And a final order file is created

  @empty-order-prevention
  Scenario: Agent prevents completing empty order
    When the customer says "that's it"
    Then the agent informs the order is empty
    And the agent asks what they would like to order
    And no order file is created

  @order-summary
  Scenario: Customer requests order summary before completing
    Given the customer has ordered "Big Mac"
    And the customer has ordered "Large French Fries"
    And the customer has ordered "Coca-Cola"
    When the customer says "what did I order?"
    Then the agent reads back all items
    And the agent confirms the total count

  @complete-with-modifications
  Scenario: Complete order with modifications
    Given the customer has ordered "Big Mac" with "No Pickles"
    And the customer has ordered "Large French Fries"
    When the customer says "that's all"
    Then the order summary includes the Big Mac modification
    And a final order file is created
    And the file contains the modifier "No Pickles"
