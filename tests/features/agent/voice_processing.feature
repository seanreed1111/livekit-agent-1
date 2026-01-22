Feature: Voice Processing and Turn Detection
  As a user
  I want natural voice interaction with proper turn-taking
  So that conversations feel responsive and human-like

  Background:
    Given the agent is connected to the room
    And the voice processing pipeline is initialized
    And the agent is ready to receive audio input

  Scenario: Agent detects end of user's question
    When the user speaks a complete question
    And the user stops speaking for the turn boundary duration
    Then the agent should detect the end of turn
    And the agent should begin generating a response
    And the agent should not wait unnecessarily long

  Scenario: Agent waits for user to finish during mid-sentence pause
    When the user starts speaking
    And the user pauses briefly mid-sentence
    And the pause is shorter than the turn boundary threshold
    Then the agent should continue waiting for more speech
    And the agent should not interrupt the user
    And the agent should not begin responding prematurely

  Scenario: Agent handles user interruption gracefully
    Given the agent is currently speaking
    When the user begins speaking
    Then the agent should detect the interruption
    And the agent should stop its current response
    And the agent should listen to the user's new input

  Scenario: Agent processes clear speech accurately
    When the user speaks clearly and at normal volume
    Then the speech-to-text should transcribe accurately
    And the agent should understand the user's intent
    And the agent should respond appropriately to the transcribed input

  Scenario: Agent handles background noise with cancellation
    Given background noise is present in the audio
    When the user speaks clearly over the noise
    Then the noise cancellation should filter the background noise
    And the speech-to-text should accurately transcribe the user's speech
    And the agent should respond based on the clean transcription
    And the background noise should not significantly impact accuracy

  Scenario: Agent maintains voice consistency in responses
    When the agent generates multiple responses
    Then all text-to-speech output should use the same voice
    And the voice should maintain consistent personality characteristics
    And the audio quality should be clear and natural

  Scenario: Agent uses preemptive generation for responsiveness
    When the user is speaking
    And the turn detector identifies likely end-of-turn
    Then the agent should begin preparing a response
    And the response should be ready when the user finishes
    And the latency between user speech and agent response should be minimized

  Scenario: Agent handles silence appropriately
    Given the user has not spoken for an extended period
    And no turn has been detected
    Then the agent should continue waiting patiently
    And the agent should not generate unsolicited responses
    And the agent should remain ready for user input

  Scenario: Agent processes multilingual turn detection
    Given the turn detector supports multiple languages
    When the user speaks in a supported language
    Then the agent should correctly detect turn boundaries
    And the turn detection should work regardless of language
    And the agent should respond appropriately
