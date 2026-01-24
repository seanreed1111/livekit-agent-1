# Test Coverage Review

**Review Date:** 2026-01-24 16:50:19
**Reviewer:** Claude Code Test Review Agent
**Project:** Generic Voice AI Assistant
**Scope:** Full Review (6 source files)

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Current Test Coverage](#current-test-coverage)
3. [Coverage Analysis by File](#coverage-analysis-by-file)
4. [Missing Tests by Criticality](#missing-tests-by-criticality)
5. [Missing Tests by Functionality](#missing-tests-by-functionality)
6. [Missing Tests by Type](#missing-tests-by-type)
7. [Test Quality Assessment](#test-quality-assessment)
8. [Recommendations](#recommendations)
9. [Implementation Plan Summary](#implementation-plan-summary)
10. [Appendix: Detailed Test Specifications](#appendix-detailed-test-specifications)

---

## Executive Summary

**Overall Test Coverage:** ~25% (estimated)

**Test Files:** 3 (conftest.py, test_agent.py, test_keyword_intercept.py)
**Source Files:** 6 (excluding __init__.py)
**Files with Tests:** 2/6 (33%)
**Files without Tests:** 4/6 (67%)

**Key Findings:**
- Excellent coverage for `keyword_intercept_llm.py` (15 tests covering all major scenarios)
- Behavioral agent tests exist using LiveKit's evaluation framework (3 tests)
- **No tests for configuration** (`config.py`) - critical gap for production
- **No tests for factories** (`factories.py`) - critical gap for component creation
- **No tests for session handler** (`session_handler.py`) - critical gap for core flow
- **No tests for mock LLM** (`mock_llm.py`) - medium gap for testing infrastructure
- **No tests for app.py** - core application bootstrap untested

**Recommended Priority:**
1. Configuration loading & validation (`config.py`) - 6 critical tests
2. Factory component creation (`factories.py`) - 5 critical tests
3. Session handler lifecycle (`session_handler.py`) - 4 critical tests

---

## Current Test Coverage

### Test Suite Overview

| Test File | Lines | Tests | Source Files Covered |
|-----------|-------|-------|---------------------|
| tests/conftest.py | 3 | 0 (fixtures only) | None - provides fixtures |
| tests/test_agent.py | 118 | 3 | app.py (Assistant class only) |
| tests/test_keyword_intercept.py | 251 | 15 | keyword_intercept_llm.py, mock_llm.py |

### Source Coverage Overview

| Source File | LOC | Has Tests | Coverage Est. | Critical Gaps |
|-------------|-----|-----------|---------------|---------------|
| config.py | 104 | ❌ | 0% | All models untested |
| factories.py | 59 | ❌ | 0% | All factories untested |
| session_handler.py | 105 | ❌ | 0% | Core session flow untested |
| app.py | 110 | ⚠️ Partial | 15% | Only Assistant class, no bootstrap |
| mock_llm.py | 119 | ⚠️ Indirect | 40% | Used in keyword tests, not directly |
| keyword_intercept_llm.py | 224 | ✅ | 85% | Minor edge cases |

---

## Coverage Analysis by File

### config.py

**Location:** `src/config.py`
**Lines of Code:** 104
**Test File:** None
**Estimated Coverage:** 0%

#### What IS Tested
- ❌ Nothing is directly tested

#### What IS NOT Tested
- ❌ `AgentConfig` (lines 10-19)
  - Missing: Default instructions validation
  - Missing: Custom instructions handling
  - Criticality: Medium
- ❌ `PipelineConfig` (lines 22-63)
  - Missing: All STT, LLM, TTS config fields
  - Missing: Keyword intercept configuration
  - Missing: Default value validation
  - Criticality: High
- ❌ `SessionConfig` (lines 66-80)
  - Missing: Turn detector configuration
  - Missing: Noise cancellation configuration
  - Criticality: Medium
- ❌ `AppConfig` (lines 83-103)
  - Missing: Environment file loading
  - Missing: Nested config with `__` delimiter
  - Missing: LiveKit credential loading
  - Missing: Validation of required fields
  - Criticality: **Critical**

#### Critical Functions/Classes
1. `AppConfig` (lines 83-103) - Core app configuration from environment
2. `PipelineConfig` (lines 22-63) - Voice pipeline component configuration

#### Recommended Tests
- [ ] **Critical:** Test AppConfig loads from .env.local
- [ ] **Critical:** Test AppConfig with missing required fields
- [ ] **Critical:** Test nested configuration with `__` delimiter
- [ ] **High:** Test PipelineConfig defaults
- [ ] **High:** Test keyword intercept config defaults
- [ ] **Medium:** Test SessionConfig defaults

---

### factories.py

**Location:** `src/factories.py`
**Lines of Code:** 59
**Test File:** None
**Estimated Coverage:** 0%

#### What IS Tested
- ❌ Nothing is directly tested

#### What IS NOT Tested
- ❌ `create_stt()` (lines 20-25)
  - Missing: STT creation with config
  - Missing: Model/language parameter passing
  - Criticality: High
- ❌ `create_llm()` (lines 28-50)
  - Missing: Normal LLM creation
  - Missing: Mock LLM selection (`model="mock"`)
  - Missing: Keyword interceptor wrapping
  - Criticality: **Critical**
- ❌ `create_tts()` (lines 53-58)
  - Missing: TTS creation with config
  - Missing: Voice parameter passing
  - Criticality: High

#### Critical Functions/Classes
1. `create_llm()` (lines 28-50) - Complex logic with mock/real LLM and keyword interceptor
2. `create_stt()` (lines 20-25) - STT component creation
3. `create_tts()` (lines 53-58) - TTS component creation

#### Recommended Tests
- [ ] **Critical:** Test create_llm with normal model
- [ ] **Critical:** Test create_llm with "mock" model
- [ ] **Critical:** Test create_llm with keyword interceptor enabled
- [ ] **High:** Test create_stt with config
- [ ] **High:** Test create_tts with config

---

### session_handler.py

**Location:** `src/session_handler.py`
**Lines of Code:** 105
**Test File:** None
**Estimated Coverage:** 0%

#### What IS Tested
- ❌ Nothing is directly tested

#### What IS NOT Tested
- ❌ `SessionHandler.__init__()` (lines 22-44)
  - Missing: Initialization with injected dependencies
  - Missing: Logging verification
  - Criticality: High
- ❌ `SessionHandler.handle_session()` (lines 46-104)
  - Missing: Turn detection configuration
  - Missing: Noise cancellation setup
  - Missing: AgentSession creation
  - Missing: Room connection
  - Missing: Initial greeting
  - Criticality: **Critical**

#### Critical Functions/Classes
1. `SessionHandler.handle_session()` (lines 46-104) - Core session lifecycle
2. `SessionHandler.__init__()` (lines 22-44) - Dependency injection point

#### Recommended Tests
- [ ] **Critical:** Test SessionHandler initialization
- [ ] **Critical:** Test handle_session creates AgentSession correctly
- [ ] **High:** Test turn detector selection (multilingual vs not)
- [ ] **High:** Test noise cancellation configuration
- [ ] **Medium:** Test initial greeting is sent

---

### app.py

**Location:** `src/app.py`
**Lines of Code:** 110
**Test File:** tests/test_agent.py (partial)
**Estimated Coverage:** 15%

#### What IS Tested
- ✅ `Assistant` class (lines 21-37)
  - Test: `test_offers_assistance` (test_agent.py:19)
  - Coverage: Agent greets user friendly
  - Test: `test_grounding` (test_agent.py:51)
  - Coverage: Agent refuses unknown info
  - Test: `test_refuses_harmful_request` (test_agent.py:93)
  - Coverage: Agent refuses harmful requests

#### What IS NOT Tested
- ❌ `_prewarm()` (lines 40-42)
  - Missing: VAD model loading
  - Criticality: Medium
- ❌ `_handle_session()` (lines 45-67)
  - Missing: Config loading
  - Missing: Component creation
  - Missing: SessionHandler creation
  - Criticality: High
- ❌ `create_app()` (lines 70-86)
  - Missing: AgentServer creation
  - Missing: Setup function registration
  - Missing: Session handler registration
  - Criticality: High
- ❌ `download_files()` (lines 89-98)
  - Missing: Model download functionality
  - Criticality: Low
- ❌ CLI entry point (lines 101-109)
  - Missing: Command-line argument handling
  - Criticality: Low

#### Critical Functions/Classes
1. `_handle_session()` (lines 45-67) - Main session entry point
2. `create_app()` (lines 70-86) - Application factory
3. `Assistant` (lines 21-37) - Agent class (partially tested)

#### Recommended Tests
- [ ] **High:** Test create_app returns configured AgentServer
- [ ] **High:** Test _handle_session creates components correctly
- [ ] **Medium:** Test _prewarm loads VAD
- [ ] **Medium:** Test Assistant with custom instructions
- [ ] **Low:** Test download_files executes

---

### mock_llm.py

**Location:** `src/mock_llm.py`
**Lines of Code:** 119
**Test File:** Used indirectly in test_keyword_intercept.py
**Estimated Coverage:** 40% (indirect)

#### What IS Tested
- ⚠️ `SimpleMockLLM` (lines 23-70)
  - Indirectly tested via keyword intercept tests
  - No direct unit tests

#### What IS NOT Tested
- ❌ `SimpleMockLLM.__init__()` (lines 26-42)
  - Missing: Custom response_text
  - Missing: Custom ttft parameter
  - Missing: Custom chunk_size parameter
  - Criticality: Medium
- ❌ `SimpleMockLLMStream._run()` (lines 92-105)
  - Missing: Streaming behavior
  - Missing: Chunk size handling
  - Missing: TTFT delay verification
  - Criticality: Medium

#### Critical Functions/Classes
1. `SimpleMockLLM` (lines 23-70) - Mock LLM for testing
2. `SimpleMockLLMStream` (lines 73-118) - Stream implementation

#### Recommended Tests
- [ ] **Medium:** Test SimpleMockLLM with custom response
- [ ] **Medium:** Test SimpleMockLLM with custom ttft
- [ ] **Medium:** Test SimpleMockLLM chunking behavior
- [ ] **Low:** Test model/provider properties

---

### keyword_intercept_llm.py

**Location:** `src/keyword_intercept_llm.py`
**Lines of Code:** 224
**Test File:** tests/test_keyword_intercept.py
**Estimated Coverage:** 85%

#### What IS Tested
- ✅ Keyword interception (15 tests)
  - Test: `test_intercepts_cherries_keyword`
  - Test: `test_intercepts_cherry_keyword`
  - Test: `test_intercepts_banana_keyword`
  - Test: `test_intercepts_apple_keyword`
  - Test: `test_intercepts_fruit_keyword`
  - Test: `test_case_insensitive_matching`
  - Test: `test_delegates_non_keyword_input`
  - Test: `test_all_default_keywords`
  - Test: `test_keyword_in_sentence`
  - Test: `test_custom_keywords_and_response`
  - Test: `test_no_more_events_after_interception`

#### What IS NOT Tested
- ⚠️ `_get_latest_user_message()` (lines 77-106)
  - Missing: Content as list of parts
  - Missing: Empty conversation history
  - Criticality: Medium
- ⚠️ Edge cases
  - Missing: Empty keyword list
  - Missing: Empty input text
  - Criticality: Low

#### Critical Functions/Classes
1. `KeywordInterceptLLM.chat()` (lines 124-169) - Well tested
2. `_get_latest_user_message()` (lines 77-106) - Needs edge case tests
3. `_contains_keyword()` (lines 108-122) - Well tested

#### Recommended Tests
- [ ] **Medium:** Test with content as list of parts
- [ ] **Low:** Test with empty keyword list
- [ ] **Low:** Test with empty conversation history

---

## Missing Tests by Criticality

### Critical (Blocks Production)
**Total:** 10 tests

1. **Test: AppConfig Environment Loading**
   - File: `src/config.py`
   - Function: `AppConfig.__init__()`, environment loading
   - Why Critical: Incorrect configuration causes runtime failures
   - Test Scenarios:
     - Valid .env.local file parsing
     - Missing required credentials
     - Nested config with `__` delimiter
   - Estimated Effort: 3 unit tests

2. **Test: Factory LLM Creation with Variants**
   - File: `src/factories.py`
   - Function: `create_llm()`
   - Why Critical: Wrong LLM type breaks core functionality
   - Test Scenarios:
     - Normal model creates inference.LLM
     - "mock" model creates SimpleMockLLM
     - Keyword intercept wraps LLM correctly
   - Estimated Effort: 3 unit tests

3. **Test: Session Handler Core Flow**
   - File: `src/session_handler.py`
   - Function: `SessionHandler.handle_session()`
   - Why Critical: Core application flow
   - Test Scenarios:
     - Successful session initialization
     - AgentSession created with correct components
     - Room connection established
     - Initial greeting sent
   - Estimated Effort: 4 unit tests

### High Priority (Significant Impact)
**Total:** 9 tests

1. **Test: Factory STT/TTS Creation**
   - File: `src/factories.py`
   - Functions: `create_stt()`, `create_tts()`
   - Why High: Component creation failures break pipeline
   - Test Scenarios:
     - STT created with correct model/language
     - TTS created with correct model/voice
   - Estimated Effort: 2 unit tests

2. **Test: Application Bootstrap**
   - File: `src/app.py`
   - Function: `create_app()`
   - Why High: Application initialization failure
   - Test Scenarios:
     - Returns configured AgentServer
     - Setup function registered
     - Session handler registered
   - Estimated Effort: 3 unit tests

3. **Test: SessionHandler Initialization**
   - File: `src/session_handler.py`
   - Function: `SessionHandler.__init__()`
   - Why High: Dependency injection point
   - Test Scenarios:
     - Stores all injected dependencies
     - Logs initialization
   - Estimated Effort: 2 unit tests

4. **Test: Session Configuration Options**
   - File: `src/session_handler.py`
   - Function: `SessionHandler.handle_session()`
   - Why High: Turn detection and noise cancellation
   - Test Scenarios:
     - Multilingual turn detector enabled/disabled
     - Noise cancellation enabled/disabled
   - Estimated Effort: 2 unit tests

### Medium Priority (Quality Improvement)
**Total:** 8 tests

1. **Test: PipelineConfig Defaults**
   - File: `src/config.py`
   - Class: `PipelineConfig`
   - Test Scenarios: All default values correct
   - Estimated Effort: 1 unit test

2. **Test: SessionConfig Defaults**
   - File: `src/config.py`
   - Class: `SessionConfig`
   - Test Scenarios: All default values correct
   - Estimated Effort: 1 unit test

3. **Test: Mock LLM Customization**
   - File: `src/mock_llm.py`
   - Class: `SimpleMockLLM`
   - Test Scenarios:
     - Custom response text
     - Custom TTFT delay
     - Custom chunk size
   - Estimated Effort: 3 unit tests

4. **Test: Assistant Custom Instructions**
   - File: `src/app.py`
   - Class: `Assistant`
   - Test Scenarios: Custom instructions passed correctly
   - Estimated Effort: 1 unit test

5. **Test: Keyword Intercept Edge Cases**
   - File: `src/keyword_intercept_llm.py`
   - Function: `_get_latest_user_message()`
   - Test Scenarios:
     - Content as list of parts
     - Empty conversation
   - Estimated Effort: 2 unit tests

### Low Priority (Nice to Have)
**Total:** 4 tests

1. **Test: Download Files Command**
   - File: `src/app.py`
   - Function: `download_files()`
   - Estimated Effort: 1 unit test

2. **Test: CLI Entry Point**
   - File: `src/app.py`
   - Test Scenarios: Command line argument handling
   - Estimated Effort: 1 integration test

3. **Test: Empty Keyword List**
   - File: `src/keyword_intercept_llm.py`
   - Estimated Effort: 1 unit test

4. **Test: Mock LLM Properties**
   - File: `src/mock_llm.py`
   - Test Scenarios: model/provider properties
   - Estimated Effort: 1 unit test

---

## Missing Tests by Functionality

### Configuration & Initialization (6 tests)
- [ ] **Critical:** AppConfig environment loading (config.py)
- [ ] **Critical:** AppConfig with missing required fields (config.py)
- [ ] **Critical:** Nested configuration with `__` delimiter (config.py)
- [ ] **Medium:** PipelineConfig defaults (config.py)
- [ ] **Medium:** SessionConfig defaults (config.py)
- [ ] **Medium:** AgentConfig defaults (config.py)

### Core Business Logic (8 tests)
- [ ] **Critical:** Factory LLM creation - normal model (factories.py)
- [ ] **Critical:** Factory LLM creation - mock model (factories.py)
- [ ] **Critical:** Factory LLM creation - with keyword interceptor (factories.py)
- [ ] **High:** Factory STT creation (factories.py)
- [ ] **High:** Factory TTS creation (factories.py)
- [ ] **High:** Application bootstrap - create_app() (app.py)
- [ ] **Medium:** Assistant with custom instructions (app.py)
- [ ] **Medium:** Mock LLM customization (mock_llm.py)

### Integration (4 tests)
- [ ] **Critical:** Config → Factory → Component flow
- [ ] **Critical:** SessionHandler with all injected dependencies
- [ ] **High:** Complete application bootstrap
- [ ] **Medium:** _handle_session component wiring

### Error Handling (3 tests)
- [ ] **Critical:** Missing required config values
- [ ] **High:** Invalid config format
- [ ] **Medium:** Empty keyword list handling

### Edge Cases (4 tests)
- [ ] **Medium:** Empty/null configuration values
- [ ] **Medium:** Content as list of parts in keyword intercept
- [ ] **Low:** Empty conversation history
- [ ] **Low:** Unicode/special characters in keywords

### End-to-End (2 tests)
- [ ] **High:** Session lifecycle from start to greeting
- [ ] **Low:** CLI command handling

---

## Missing Tests by Type

### Unit Tests (23 tests)
**What:** Test individual functions/classes in isolation

**Missing:**
- [ ] config.py: 6 tests for AppConfig, PipelineConfig, SessionConfig, AgentConfig
- [ ] factories.py: 5 tests for create_stt(), create_llm(), create_tts()
- [ ] session_handler.py: 4 tests for SessionHandler.__init__(), config options
- [ ] mock_llm.py: 4 tests for SimpleMockLLM customization and properties
- [ ] app.py: 3 tests for create_app(), Assistant, _prewarm()
- [ ] keyword_intercept_llm.py: 1 test for edge cases

**Total Unit Tests Needed:** 23

### Integration Tests (5 tests)
**What:** Test component interactions and workflows

**Missing:**
- [ ] Config → Factory integration (1 scenario)
- [ ] Factory → SessionHandler integration (1 scenario)
- [ ] _handle_session full flow (1 scenario)
- [ ] Application bootstrap flow (1 scenario)
- [ ] Session lifecycle (1 scenario)

**Total Integration Tests Needed:** 5

### End-to-End Tests (3 tests)
**What:** Test complete system flows

**Missing:**
- [ ] Application startup flow (1 scenario)
- [ ] Voice interaction flow (1 scenario - may need mocking)
- [ ] CLI command handling (1 scenario)

**Total E2E Tests Needed:** 3

---

## Test Quality Assessment

### Current Test Quality

**Strengths:**
- ✅ Keyword intercept tests are comprehensive (15 tests covering all major cases)
- ✅ Agent behavioral tests use LiveKit's evaluation framework with LLM-as-judge
- ✅ Tests use async/await correctly with pytest.mark.asyncio
- ✅ Tests verify specific behaviors rather than just checking for no errors
- ✅ Tests use meaningful assertions with custom messages

**Weaknesses:**
- ❌ conftest.py is empty - no shared fixtures defined
- ❌ No tests for configuration loading (critical for production)
- ❌ No tests for factory functions (core component creation)
- ❌ No tests for session handler (core application flow)
- ❌ Mock LLM only tested indirectly through keyword intercept tests
- ❌ No integration tests between components

### Test Organization
- **Fixtures:** conftest.py exists but is empty - need to add shared fixtures
- **Isolation:** Tests appear isolated but some share SimpleMockLLM setup
- **Naming:** Test names are descriptive and follow convention
- **Documentation:** Test docstrings explain purpose well

### Best Practices Adherence
- [x] Tests follow AAA pattern (Arrange-Act-Assert)
- [x] Tests are isolated and independent
- [x] Tests use meaningful names
- [ ] Fixtures are properly organized in conftest.py (needs work)
- [ ] Edge cases are systematically covered (partially)
- [ ] Error scenarios are tested (missing)
- [ ] Integration tests verify component interactions (missing)

---

## Recommendations

### Immediate Actions (Before Production)
1. **Add configuration tests** (6 tests)
   - Prevents deployment with bad config
   - Catches environment loading issues
   - Validates nested config parsing

2. **Add factory tests** (5 tests)
   - Ensures components are created correctly
   - Tests mock LLM selection logic
   - Validates keyword interceptor wrapping

3. **Add session handler tests** (4 tests)
   - Validates core application flow
   - Tests dependency injection
   - Verifies session lifecycle

### Short-term Actions (Next Sprint)
4. Add integration tests for component wiring (5 tests)
5. Add error handling tests across all components (3 tests)
6. Improve test organization with shared fixtures in conftest.py
7. Add mock LLM direct unit tests (4 tests)

### Long-term Actions (Quality Improvement)
8. Add end-to-end tests for complete workflows (3 tests)
9. Set up pytest-cov for coverage reporting
10. Add coverage thresholds to CI/CD
11. Document testing standards in AGENTS.md

### Testing Infrastructure
- [ ] Add shared fixtures to conftest.py for common test setup
- [ ] Set up pytest-cov for coverage reporting
- [ ] Add coverage thresholds to CI/CD (target: 80%)
- [ ] Consider adding mutation testing for critical paths

---

## Implementation Plan Summary

**Total Tests to Write:** 31

**Breakdown by Priority:**
- Critical: 10 tests
- High: 9 tests
- Medium: 8 tests
- Low: 4 tests

**Breakdown by Type:**
- Unit: 23 tests
- Integration: 5 tests
- End-to-End: 3 tests

**Recommended Phases:**

### Phase 1: Critical Tests (Required for Production)
**Goal:** Cover all production-blocking gaps
**Tests:** 10
**Files:** config.py, factories.py, session_handler.py

| Test | File | Priority |
|------|------|----------|
| test_appconfig_loads_from_env | config.py | Critical |
| test_appconfig_missing_required | config.py | Critical |
| test_appconfig_nested_delimiter | config.py | Critical |
| test_create_llm_normal_model | factories.py | Critical |
| test_create_llm_mock_model | factories.py | Critical |
| test_create_llm_with_interceptor | factories.py | Critical |
| test_session_handler_init | session_handler.py | Critical |
| test_session_handler_creates_session | session_handler.py | Critical |
| test_session_handler_connects | session_handler.py | Critical |
| test_session_handler_greets | session_handler.py | Critical |

### Phase 2: High Priority Tests (Pre-Release)
**Goal:** Cover important functionality
**Tests:** 9
**Files:** factories.py, app.py, session_handler.py

| Test | File | Priority |
|------|------|----------|
| test_create_stt_with_config | factories.py | High |
| test_create_tts_with_config | factories.py | High |
| test_create_app_returns_server | app.py | High |
| test_create_app_registers_setup | app.py | High |
| test_create_app_registers_session | app.py | High |
| test_session_handler_turn_detector | session_handler.py | High |
| test_session_handler_noise_cancel | session_handler.py | High |
| test_handle_session_creates_components | app.py | High |
| test_integration_config_to_factory | integration | High |

### Phase 3: Quality Improvement Tests
**Goal:** Comprehensive coverage and edge cases
**Tests:** 12
**Files:** All remaining gaps

| Test | File | Priority |
|------|------|----------|
| test_pipeline_config_defaults | config.py | Medium |
| test_session_config_defaults | config.py | Medium |
| test_agent_config_defaults | config.py | Medium |
| test_mock_llm_custom_response | mock_llm.py | Medium |
| test_mock_llm_custom_ttft | mock_llm.py | Medium |
| test_mock_llm_chunking | mock_llm.py | Medium |
| test_assistant_custom_instructions | app.py | Medium |
| test_keyword_content_list | keyword_intercept_llm.py | Medium |
| test_keyword_empty_history | keyword_intercept_llm.py | Low |
| test_download_files | app.py | Low |
| test_empty_keyword_list | keyword_intercept_llm.py | Low |
| test_mock_llm_properties | mock_llm.py | Low |

---

## Appendix: Detailed Test Specifications

### A1. Configuration Tests (config.py)

#### Test: AppConfig Environment Loading
**File:** `tests/test_config.py`
**Function Under Test:** `AppConfig()`
**Criticality:** Critical

**Test Cases:**

1. `test_appconfig_loads_from_env_local`
   ```python
   def test_appconfig_loads_from_env_local(tmp_path, monkeypatch):
       """Test that AppConfig loads from .env.local file."""
       # Setup: Create .env.local with valid credentials
       env_file = tmp_path / ".env.local"
       env_file.write_text("""
       LIVEKIT_URL=wss://test.livekit.cloud
       LIVEKIT_API_KEY=test_key
       LIVEKIT_API_SECRET=test_secret
       """)
       monkeypatch.chdir(tmp_path)

       # Action: Initialize AppConfig
       config = AppConfig()

       # Assert: All fields populated correctly
       assert config.livekit_url == "wss://test.livekit.cloud"
       assert config.livekit_api_key == "test_key"
       assert config.livekit_api_secret == "test_secret"
   ```

2. `test_appconfig_nested_delimiter`
   ```python
   def test_appconfig_nested_delimiter(tmp_path, monkeypatch):
       """Test that __ delimiter works for nested config."""
       # Setup: Create .env with nested config
       env_file = tmp_path / ".env.local"
       env_file.write_text("""
       PIPELINE__LLM_MODEL=gpt-4o
       PIPELINE__TTS_VOICE=Nova
       SESSION__PREEMPTIVE_GENERATION=false
       """)
       monkeypatch.chdir(tmp_path)

       # Action: Initialize AppConfig
       config = AppConfig()

       # Assert: Nested config parsed correctly
       assert config.pipeline.llm_model == "gpt-4o"
       assert config.pipeline.tts_voice == "Nova"
       assert config.session.preemptive_generation is False
   ```

3. `test_appconfig_uses_defaults`
   ```python
   def test_appconfig_uses_defaults(tmp_path, monkeypatch):
       """Test that AppConfig uses default values when env not set."""
       # Setup: Empty .env.local
       env_file = tmp_path / ".env.local"
       env_file.write_text("")
       monkeypatch.chdir(tmp_path)

       # Action: Initialize AppConfig
       config = AppConfig()

       # Assert: Default values used
       assert config.pipeline.llm_model == "openai/gpt-4.1-nano"
       assert config.pipeline.stt_model == "assemblyai/universal-streaming"
       assert config.session.use_multilingual_turn_detector is True
   ```

### A2. Factory Tests (factories.py)

#### Test: LLM Factory with Variants
**File:** `tests/test_factories.py`
**Function Under Test:** `create_llm()`
**Criticality:** Critical

**Test Cases:**

1. `test_create_llm_normal_model`
   ```python
   def test_create_llm_normal_model():
       """Test create_llm with normal model returns inference.LLM."""
       config = PipelineConfig(llm_model="openai/gpt-4.1-nano")

       llm = create_llm(config)

       assert isinstance(llm, inference.LLM)
   ```

2. `test_create_llm_mock_model`
   ```python
   def test_create_llm_mock_model():
       """Test create_llm with 'mock' returns SimpleMockLLM."""
       config = PipelineConfig(llm_model="mock")

       llm = create_llm(config)

       assert isinstance(llm, SimpleMockLLM)
   ```

3. `test_create_llm_with_keyword_interceptor`
   ```python
   def test_create_llm_with_keyword_interceptor():
       """Test create_llm wraps with KeywordInterceptLLM when enabled."""
       config = PipelineConfig(
           llm_model="mock",
           enable_keyword_intercept=True,
           intercept_keywords=["test"],
           intercept_response="intercepted"
       )

       llm = create_llm(config)

       assert isinstance(llm, KeywordInterceptLLM)
   ```

### A3. Session Handler Tests (session_handler.py)

#### Test: SessionHandler Initialization
**File:** `tests/test_session_handler.py`
**Function Under Test:** `SessionHandler.__init__()`
**Criticality:** Critical

**Test Cases:**

1. `test_session_handler_stores_dependencies`
   ```python
   def test_session_handler_stores_dependencies():
       """Test SessionHandler stores all injected dependencies."""
       mock_stt = MagicMock()
       mock_llm = MagicMock()
       mock_tts = MagicMock()
       mock_agent = MagicMock(spec=Agent)
       config = SessionConfig()

       handler = SessionHandler(
           stt=mock_stt,
           llm=mock_llm,
           tts=mock_tts,
           agent=mock_agent,
           session_config=config
       )

       assert handler.stt is mock_stt
       assert handler.llm is mock_llm
       assert handler.tts is mock_tts
       assert handler.agent is mock_agent
       assert handler.session_config is config
   ```

---

**Note:** This review is advisory only. No changes have been made to the codebase. All test implementations require explicit user approval.
