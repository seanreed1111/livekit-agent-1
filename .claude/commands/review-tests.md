---
description: Review existing test coverage and identify gaps
model: opus
args:
  - name: targets
    description: Optional space-separated list of modules/directories to review (e.g., "src/config.py src/factories.py" or "src/adapters")
    required: false

---

# Test Coverage Review

You are tasked with reviewing the existing test suite to identify gaps, missing test cases, and areas that need improved coverage. Your goal is to provide a comprehensive analysis that helps prioritize testing efforts.

## Command Arguments

This command accepts optional target parameters to focus the review on specific modules or directories. This is useful when:
- You've just modified specific files and want to ensure they have adequate test coverage
- You want to review a specific subsystem or component
- An agent or user wants to focus testing efforts on a particular area

**Usage Examples:**
- `/review-tests` - Review all source files (full review)
- `/review-tests src/config.py` - Review only config.py
- `/review-tests src/config.py src/factories.py` - Review multiple specific files
- `/review-tests src/adapters` - Review all files in the adapters directory
- `/review-tests src/config.py src/adapters` - Review a specific file + entire directory

**Argument Parsing:**
- Parse the command args to extract target modules/directories
- If no args provided: review ALL source files in src/ (default behavior)
- If args provided: review ONLY the specified targets
- Validate that all specified targets exist before proceeding
- If a target doesn't exist, report an error and list valid targets

## Initial Response

When this command is invoked, immediately begin the review process without waiting for additional input.

## Process Steps

### Step 1: Analyze Existing Tests and Source Code

1. **Parse target arguments** (if provided):
   - Extract targets from command args
   - Validate each target exists (file or directory)
   - If target is a directory, expand to all .py files within it
   - If no targets specified, default to reviewing all of `src/`

2. **Discover all test files**:
   - Use Bash to find all test files: `find tests -type f -name "*.py"`
   - Use Read tool to examine each test file completely
   - Identify what is being tested and coverage scope

3. **Discover source files to review**:
   - If targets specified:
     - For each target:
       - If file: add to review list
       - If directory: find all .py files in directory: `find <dir> -type f -name "*.py"`
     - Exclude `__init__.py` files unless they contain logic
   - If no targets specified:
     - Use Bash to find all source files: `find src -type f -name "*.py"`
     - Exclude `__init__.py` files unless they contain logic
   - Use Read tool to examine each source file
   - Identify critical functions, classes, and edge cases

3. **Map test coverage**:
   - For each source file, identify:
     - Which tests cover it (if any)
     - What functionality is tested
     - What functionality is NOT tested
     - What edge cases are missing
   - Calculate approximate coverage percentage per file

4. **Analyze test quality**:
   - Are tests unit tests or integration tests?
   - Do tests follow best practices?
   - Are tests properly isolated?
   - Do tests use fixtures appropriately?
   - Are edge cases covered?

### Step 2: Categorize Missing Tests

Organize missing tests into categories:

1. **By Criticality**:
   - **Critical**: Tests for core functionality that would block production deployment
   - **High**: Tests for important features that significantly impact reliability
   - **Medium**: Tests for supporting functionality that improves quality
   - **Low**: Tests for edge cases or nice-to-have coverage

2. **By Functionality**:
   - Configuration & initialization tests
   - Core business logic tests
   - Integration tests
   - Error handling tests
   - Edge case tests
   - End-to-end tests

3. **By Type**:
   - Unit tests (isolated component testing)
   - Integration tests (component interaction)
   - End-to-end tests (full system flow)
   - Property-based tests (if applicable)
   - Performance tests (if applicable)

### Step 3: Generate Review Report

1. **Create output directory**:
   - Use Bash to create: `mkdir -p plan/review-tests`
   - Generate timestamp for report filename

2. **Generate comprehensive report**:

Use the following template structure:

```markdown
# Test Coverage Review

**Review Date:** YYYY-MM-DD HH:MM:SS
**Reviewer:** Claude Code Test Review Agent
**Project:** Generic Voice AI Assistant
**Scope:** [Full Review | Targeted: <list of targets>]

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

**Overall Test Coverage:** XX% (estimated)

**Test Files:** X
**Source Files:** Y
**Files with Tests:** Z
**Files without Tests:** Y-Z

**Key Findings:**
- [High-level finding 1]
- [High-level finding 2]
- [High-level finding 3]

**Recommended Priority:**
1. [Top priority area]
2. [Second priority area]
3. [Third priority area]

---

## Current Test Coverage

### Test Suite Overview

| Test File | Lines | Tests | Source Files Covered |
|-----------|-------|-------|---------------------|
| test_*.py | XX | X | file1.py, file2.py |

### Source Coverage Overview

| Source File | LOC | Has Tests | Coverage Est. | Critical Gaps |
|-------------|-----|-----------|---------------|---------------|
| app.py | XX | ✅/❌ | XX% | [Gap summary] |

---

## Coverage Analysis by File

### [source_file_1.py]

**Location:** `src/source_file_1.py`
**Lines of Code:** XXX
**Test File:** `tests/test_file_1.py` (if exists)
**Estimated Coverage:** XX%

#### What IS Tested
- ✅ Function/class 1 (lines XX-YY)
  - Test: `test_name` (test_file.py:XX)
  - Coverage: Basic functionality
- ✅ Function/class 2 (lines XX-YY)
  - Test: `test_name` (test_file.py:XX)
  - Coverage: Happy path

#### What IS NOT Tested
- ❌ Function/class 3 (lines XX-YY)
  - Missing: All functionality
  - Criticality: High
- ⚠️ Function/class 1 edge cases:
  - Missing: Null/empty input handling
  - Missing: Error conditions
  - Missing: Boundary conditions
  - Criticality: Medium

#### Critical Functions/Classes
1. `function_name` (lines XX-YY) - [Why critical]
2. `class_name` (lines XX-YY) - [Why critical]

#### Recommended Tests
- [ ] **Critical:** Test function_name error handling
- [ ] **High:** Test class_name initialization edge cases
- [ ] **Medium:** Test integration with dependency X

---

[Repeat for each source file]

---

## Missing Tests by Criticality

### Critical (Blocks Production)
**Total:** X tests

1. **Test: Configuration Loading & Validation**
   - File: `src/config.py`
   - Function: `AppConfig.__init__`, environment loading
   - Why Critical: Incorrect configuration could cause runtime failures
   - Test Scenarios:
     - Valid .env.local file parsing
     - Missing required credentials
     - Invalid nested configuration format
     - Default value application
   - Estimated Effort: X unit tests, ~XX minutes

2. **Test: Session Lifecycle**
   - File: `src/session_handler.py`
   - Function: `SessionHandler.handle_session()`
   - Why Critical: Core application flow
   - Test Scenarios:
     - Successful session initialization
     - Connection failures
     - Component creation errors
     - Room join failures
   - Estimated Effort: X unit tests, X integration tests, ~XX minutes

[Continue with all critical tests]

### High Priority (Significant Impact)
**Total:** X tests

[Same format as Critical section]

### Medium Priority (Quality Improvement)
**Total:** X tests

[Same format]

### Low Priority (Nice to Have)
**Total:** X tests

[Same format]

---

## Missing Tests by Functionality

### Configuration & Initialization (X tests)
- [ ] **Critical:** AppConfig environment loading (config.py)
- [ ] **Critical:** PipelineConfig defaults (config.py)
- [ ] **High:** Nested configuration with `__` delimiter (config.py)
- [ ] **Medium:** Invalid configuration validation (config.py)

### Core Business Logic (X tests)
- [ ] **Critical:** Factory component creation (factories.py)
- [ ] **High:** Mock LLM selection logic (factories.py)
- [ ] **High:** Keyword interceptor wrapping (factories.py)

### Integration (X tests)
- [ ] **Critical:** Config → Factory → Component flow
- [ ] **Critical:** Factory → Session → Agent flow
- [ ] **High:** Complete application bootstrap

### Error Handling (X tests)
- [ ] **Critical:** Session creation failures (session_handler.py)
- [ ] **High:** Connection error handling (session_handler.py)
- [ ] **Medium:** Invalid input validation across components

### Edge Cases (X tests)
- [ ] **High:** Empty/null configuration values
- [ ] **Medium:** Keyword interceptor with empty text
- [ ] **Low:** Unicode/special characters in responses

### End-to-End (X tests)
- [ ] **High:** Complete voice interaction flow
- [ ] **Medium:** Multi-turn conversation
- [ ] **Low:** LiveKit room lifecycle (if testable)

---

## Missing Tests by Type

### Unit Tests (X tests)
**What:** Test individual functions/classes in isolation

**Missing:**
- [ ] config.py: X tests for AppConfig, PipelineConfig, SessionConfig
- [ ] factories.py: X tests for create_stt(), create_llm(), create_tts()
- [ ] session_handler.py: X tests for SessionHandler methods
- [ ] mock_llm.py: X tests for SimpleMockLLM, SimpleMockLLMStream
- [ ] app.py: X tests for _prewarm(), _handle_session(), create_app()

**Total Unit Tests Needed:** XX

### Integration Tests (X tests)
**What:** Test component interactions and workflows

**Missing:**
- [ ] Config → Factory integration (X scenarios)
- [ ] Factory → Session integration (X scenarios)
- [ ] Component wiring in AgentSession (X scenarios)
- [ ] Mock LLM + Keyword Interceptor integration (X scenarios)

**Total Integration Tests Needed:** XX

### End-to-End Tests (X tests)
**What:** Test complete system flows

**Missing:**
- [ ] Application startup flow (X scenarios)
- [ ] Voice interaction flow (X scenarios, if feasible)
- [ ] Error recovery flow (X scenarios)

**Total E2E Tests Needed:** XX

---

## Test Quality Assessment

### Current Test Quality

**Strengths:**
- ✅ [Strength 1 with example]
- ✅ [Strength 2 with example]

**Weaknesses:**
- ❌ [Weakness 1 with example]
- ❌ [Weakness 2 with example]

### Test Organization
- **Fixtures:** [Assessment of conftest.py usage]
- **Isolation:** [Assessment of test isolation]
- **Naming:** [Assessment of test naming conventions]
- **Documentation:** [Assessment of test docstrings]

### Best Practices Adherence
- [ ] Tests follow AAA pattern (Arrange-Act-Assert)
- [ ] Tests are isolated and independent
- [ ] Tests use meaningful names
- [ ] Fixtures are properly organized in conftest.py
- [ ] Edge cases are systematically covered
- [ ] Error scenarios are tested
- [ ] Integration tests verify component interactions

---

## Recommendations

### Immediate Actions (Before Production)
1. **Add configuration tests** - Prevents deployment with bad config
2. **Add session handler tests** - Validates core application flow
3. **Add factory tests** - Ensures components are created correctly

### Short-term Actions (Next Sprint)
4. Add integration tests for component wiring
5. Add error handling tests across all components
6. Improve test organization and documentation

### Long-term Actions (Quality Improvement)
7. Add end-to-end tests for complete workflows
8. Add property-based tests for edge case discovery
9. Set up coverage tracking and reporting

### Testing Infrastructure
- [ ] Set up pytest-cov for coverage reporting
- [ ] Add coverage thresholds to CI/CD
- [ ] Consider adding mutation testing
- [ ] Document testing standards in AGENTS.md

---

## Implementation Plan Summary

**Total Tests to Write:** XXX

**Breakdown by Priority:**
- Critical: XX tests (~XX minutes)
- High: XX tests (~XX minutes)
- Medium: XX tests (~XX minutes)
- Low: XX tests (~XX minutes)

**Breakdown by Type:**
- Unit: XX tests
- Integration: XX tests
- End-to-End: XX tests

**Recommended Phases:**

### Phase 1: Critical Tests (Required for Production)
**Goal:** Cover all production-blocking gaps
**Tests:** XX
**Files:** config.py, session_handler.py, factories.py
**Estimated Time:** XX minutes

### Phase 2: High Priority Tests (Pre-Release)
**Goal:** Cover important functionality
**Tests:** XX
**Files:** app.py, integration tests
**Estimated Time:** XX minutes

### Phase 3: Quality Improvement Tests
**Goal:** Comprehensive coverage and edge cases
**Tests:** XX
**Files:** All remaining gaps
**Estimated Time:** XX minutes

---

## Appendix: Detailed Test Specifications

### A1. Configuration Tests (config.py)

#### Test: AppConfig Environment Loading
**File:** `tests/test_config.py`
**Function Under Test:** `AppConfig.__init__()`
**Criticality:** Critical

**Test Cases:**
1. `test_appconfig_loads_from_env_local`
   - Setup: Create .env.local with valid credentials
   - Action: Initialize AppConfig
   - Assert: All fields populated correctly

2. `test_appconfig_missing_required_fields`
   - Setup: .env.local missing LIVEKIT_URL
   - Action: Initialize AppConfig
   - Assert: Raises ValidationError with helpful message

3. `test_appconfig_nested_delimiter`
   - Setup: .env with PIPELINE__LLM__MODEL=gpt-4
   - Action: Initialize AppConfig
   - Assert: config.pipeline.llm.model == "gpt-4"

[Continue with detailed specifications for each test category]

---

**Note:** This review is advisory only. No changes have been made to the codebase. All test implementations require explicit user approval.
```

3. **Write report file**:
   - Save to: `plan/review-tests/YYYY-MM-DD-HHMMSS-test-coverage-review.md`
   - If scoped review, include scope in filename: `YYYY-MM-DD-HHMMSS-test-coverage-review-config.md`
   - Include complete timestamp in filename
   - Include full analysis and specifications

4. **Present summary to user**:
   ```
   ✅ Test coverage review completed!

   Report saved to: plan/review-tests/YYYY-MM-DD-HHMMSS-test-coverage-review.md

   Current Coverage: XX%
   Files with Tests: X/Y (XX%)

   Missing Tests by Priority:
   - Critical: XX tests (production blockers)
   - High: XX tests (significant impact)
   - Medium: XX tests (quality improvement)
   - Low: XX tests (nice to have)

   Total Tests to Write: XXX

   Top 3 Priorities:
   1. [Priority 1]
   2. [Priority 2]
   3. [Priority 3]

   See the full report for detailed analysis and test specifications.

   Next steps:
   - Review the report and prioritize which tests to implement
   - To implement tests: Explicitly request "implement the critical tests" or similar
   - To implement specific tests: Reference specific test names from the report
   ```

## Important Guidelines

1. **Scope Handling**:
   - If targets specified: Validate all targets exist before proceeding
   - If target is a directory: Expand to all .py files (excluding __init__.py unless it has logic)
   - If no targets: Review all files in src/ (full review)
   - Clearly indicate scope in report and summary

2. **Thorough Analysis**:
   - Read ALL relevant source files completely (within scope)
   - Read ALL test files completely
   - Map coverage systematically
   - Identify both obvious and subtle gaps

3. **Clear Categorization**:
   - Use consistent criticality levels
   - Explain WHY each test is critical/high/medium/low
   - Group by functionality for clarity
   - Provide test type breakdown

4. **Actionable Output**:
   - Provide specific test names
   - Include test scenarios and assertions
   - Estimate effort/time when possible
   - Create clear implementation phases

5. **Non-Destructive**:
   - NEVER write tests automatically
   - NEVER modify existing code
   - Only generate review report
   - Wait for explicit user approval to implement

6. **Comprehensive**:
   - Cover unit, integration, and e2e test gaps
   - Include edge cases and error scenarios
   - Consider test quality, not just coverage
   - Provide detailed test specifications in appendix

## Example Interactions

### Example 1: Full Review

```
User: /review-tests
Assistant: I'll analyze the test coverage for all source files and identify gaps...

[Discovers all source and test files]
[Reads and analyzes each file]
[Maps coverage systematically]

Generating comprehensive test coverage review...

✅ Test coverage review completed!

Report saved to: plan/review-tests/2026-01-24-153045-test-coverage-review.md

Scope: Full Review (7 source files)
Current Coverage: 15%
Files with Tests: 2/7 (29%)

Missing Tests by Priority:
- Critical: 24 tests (production blockers)
- High: 18 tests (significant impact)
- Medium: 12 tests (quality improvement)
- Low: 8 tests (nice to have)

Total Tests to Write: 62

Top 3 Priorities:
1. Configuration loading & validation (config.py) - 8 critical tests
2. Session lifecycle & error handling (session_handler.py) - 6 critical tests
3. Factory component creation (factories.py) - 5 critical tests

See the full report for detailed analysis and test specifications.

Next steps:
- Review the report and prioritize which tests to implement
- To implement tests: Explicitly request "implement the critical tests" or similar
- To implement specific tests: Reference specific test names from the report
```

### Example 2: Targeted Review

```
User: /review-tests src/config.py src/factories.py
Assistant: I'll analyze test coverage for the specified modules and identify gaps...

Targets: src/config.py, src/factories.py

[Validates targets exist]
[Discovers relevant test files]
[Reads and analyzes targeted files]
[Maps coverage systematically]

Generating targeted test coverage review...

✅ Test coverage review completed!

Report saved to: plan/review-tests/2026-01-24-153045-test-coverage-review-config-factories.md

Scope: Targeted Review (2 files: config.py, factories.py)
Current Coverage: 10%
Files with Tests: 0/2 (0%)

Missing Tests by Priority:
- Critical: 13 tests (production blockers)
- High: 9 tests (significant impact)
- Medium: 6 tests (quality improvement)
- Low: 3 tests (nice to have)

Total Tests to Write: 31

Top 3 Priorities:
1. AppConfig environment loading (config.py) - 5 critical tests
2. Factory STT/LLM/TTS creation (factories.py) - 5 critical tests
3. Configuration validation (config.py) - 3 critical tests

See the full report for detailed analysis and test specifications.

Next steps:
- Review the report and prioritize which tests to implement
- To implement tests: Explicitly request "implement the critical tests" or similar
- To implement specific tests: Reference specific test names from the report

User: implement the critical tests from config.py
Assistant: [Proceeds to implement the 5 critical configuration tests]
```

### Example 3: Directory Review

```
User: /review-tests src/adapters
Assistant: I'll analyze test coverage for all modules in src/adapters/ and identify gaps...

Target directory: src/adapters/
Found files: audio_utils.py

[Validates directory exists]
[Discovers all .py files in directory]
[Reads and analyzes each file]
[Maps coverage systematically]

Generating targeted test coverage review...

✅ Test coverage review completed!

Report saved to: plan/review-tests/2026-01-24-153045-test-coverage-review-adapters.md

Scope: Targeted Review (1 file in adapters/)
Current Coverage: 0%
Files with Tests: 0/1 (0%)

Missing Tests by Priority:
- Critical: 0 tests
- High: 3 tests (significant impact)
- Medium: 2 tests (quality improvement)
- Low: 1 test (nice to have)

Total Tests to Write: 6

Top Priority:
1. Audio utility functions (audio_utils.py) - 3 high priority tests

See the full report for detailed analysis and test specifications.
```

## Notes

- This command focuses on analysis and planning, not implementation
- The generated report serves as a roadmap for testing efforts
- Users maintain control over which tests to implement and when
- Test specifications in the appendix provide clear implementation guidance
