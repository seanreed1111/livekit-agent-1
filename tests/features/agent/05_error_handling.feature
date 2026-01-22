@voice-agent @order-taking @priority-2
Feature: Error Handling and Recovery
  As a McDonald's customer
  I want the agent to handle errors gracefully
  So that I can still complete my order even with mistakes

  Background:
    Given the McDonald's menu is loaded
    And the agent is ready to take orders

  @invalid-item
  Scenario: Customer orders item not on menu
    When the customer says "I'll have a Whopper"
    Then the agent politely informs the item is not available
    And the agent suggests similar menu items
    And the order remains empty

  @ambiguous-item
  Scenario: Customer gives ambiguous item name
    When the customer says "I want a burger"
    Then the agent asks for clarification
    And the agent lists burger options

  @unclear-audio
  Scenario: Speech recognition produces unclear result
    When the customer says "mmm... uh... can I get"
    Then the agent asks the customer to repeat their order
    And the order remains unchanged

  @typo-recovery
  Scenario: Customer says item name with speech variation
    When the customer says "big mak"
    Then the agent uses fuzzy matching
    And the agent confirms "Big Mac"
    And the order contains "Big Mac"
