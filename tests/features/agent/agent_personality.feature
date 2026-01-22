Feature: Friendly Agent Greetings
  As a user
  I want the agent to greet me warmly
  So that I feel welcomed to the conversation

  Background:
    Given the agent is connected to the room
    And the agent is ready to receive user input

  Scenario: User initiates conversation with hello
    When the user says "Hello"
    Then the agent should respond with a friendly greeting
    And the agent should optionally offer assistance
    And the agent's tone should be warm and welcoming

  Scenario: User initiates conversation with a question
    When the user says "Can you help me?"
    Then the agent should respond warmly
    And the agent should acknowledge the request for help
    And the agent should express willingness to assist

  Scenario: User greets agent in the morning
    When the user says "Good morning"
    Then the agent should respond appropriately to the time of day
    And the agent should sound friendly
    And the agent should engage naturally

  Scenario: User initiates with casual greeting
    When the user says "Hey there"
    Then the agent should match the casual tone
    And the agent should respond in a friendly manner
    And the agent should not be overly formal

  Scenario: Agent maintains friendly personality throughout conversation
    Given the user has greeted the agent
    And the agent has responded warmly
    When the user asks multiple questions in sequence
    Then the agent should maintain a consistent friendly tone
    And the agent should remain helpful and approachable
    And the agent should occasionally use appropriate humor

  Scenario: Agent stays concise for voice interaction
    When the user asks "What can you do?"
    Then the agent should provide a concise response
    And the agent should avoid lengthy explanations
    And the agent's response should be suitable for voice output
    And the agent should not use complex formatting
