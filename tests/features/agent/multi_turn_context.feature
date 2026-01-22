Feature: Conversation Context Management
  As a user
  I want the agent to remember conversation context
  So that I can have natural multi-turn conversations

  Background:
    Given the agent is connected to the room
    And the agent is ready to receive user input

  Scenario: User asks follow-up question about same topic
    Given the user has asked "What's the weather like?"
    And the agent has responded to the weather question
    When the user says "What about tomorrow?"
    Then the agent should understand the context refers to weather
    And the agent should respond to the follow-up appropriately
    And the agent should not ask for clarification about the topic

  Scenario: User changes topic mid-conversation
    Given an ongoing conversation about weather
    And the agent has provided weather information
    When the user says "Tell me a joke"
    Then the agent should adapt to the new topic
    And the agent should not confuse the topics
    And the agent should respond with a joke

  Scenario: User refers to previous statement with pronouns
    Given the user has said "I have a dog"
    And the agent has acknowledged the user's dog
    When the user says "What should I feed it?"
    Then the agent should understand "it" refers to the dog
    And the agent should provide relevant advice about dog food
    And the agent should maintain context consistency

  Scenario: User continues complex multi-turn conversation
    Given the user has asked "What's 5 plus 3?"
    And the agent has answered "8"
    When the user says "Now multiply that by 2"
    Then the agent should remember the previous answer was 8
    And the agent should respond with "16"
    And the agent should maintain the calculation context

  Scenario: User returns to previous topic after digression
    Given the user has discussed topic A
    And the user has then discussed topic B
    When the user says "Going back to what we were talking about before"
    Then the agent should attempt to recall topic A
    And the agent should acknowledge the context switch
    And the agent should resume the previous topic appropriately
