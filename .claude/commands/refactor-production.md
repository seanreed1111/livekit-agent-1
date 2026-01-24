---
description: Review code with Dave Farley & Kent Beck principles and suggest production-ready refactoring
model: opus
args:
  - name: targets
    description: Optional space-separated list of modules/files to refactor (e.g., "src/config.py src/factories.py")
    required: false

---

# Production Refactoring with Farley-Beck Principles

You are tasked with reviewing code using the architectural insights of Dave Farley and Kent Beck, then suggesting refactoring suitable for a production software system. This command follows a rigorous, test-driven approach to ensure refactoring maintains system reliability.

## Core Refactoring Principles

### Dave Farley's Principles
- **Continuous Delivery**: Changes must be small, incremental, and reversible
- **Evidence-based**: Use automated tests to validate changes
- **Automation-first**: Ensure refactoring can be verified automatically
- **Quality focus**: Improve design while maintaining or improving quality metrics

### Kent Beck's Principles
- **"Make the change easy, then make the easy change"**: Preparatory refactoring first
- **Tidying**: Small refactorings (minutes to hours), not multi-day rewrites
- **Separate concerns**: Separate structural changes from behavioral changes
- **Test-Driven**: Red-Green-Refactor cycle ensures safety
- **Simple design**: Grow design organically, one decision at a time
- **YAGNI**: Don't add features or abstractions for hypothetical futures

### Combined Approach
1. **Preparatory refactoring** to make the structure easier to work with
2. **Small, incremental steps** that can each be verified independently
3. **Test coverage first** - never refactor without tests
4. **Continuous integration** - each step should leave code in working state
5. **Evidence-based validation** - use tests to prove correctness

## Command Arguments

This command accepts optional target parameters to focus refactoring on specific modules or files:

**Usage Examples:**
- `/refactor-production` - Review all source files (full review)
- `/refactor-production src/config.py` - Review only config.py
- `/refactor-production src/config.py src/factories.py` - Review multiple files
- `/refactor-production src/adapters` - Review all files in adapters directory

**Argument Parsing:**
- If no args provided: review ALL source files in src/ (default behavior)
- If args provided: review ONLY the specified targets
- Validate that all specified targets exist before proceeding

## Initial Response

When this command is invoked, immediately begin the refactoring analysis process without waiting for additional input.

## Process Overview

This command follows a structured, test-driven workflow:

1. **Research refactoring patterns** from Farley & Beck
2. **Analyze codebase** for refactoring opportunities
3. **Create detailed refactoring plan** (plan/future-plans/plan_name.md)
4. **Review plan** with sub-agent (plan/future-plans/plan_name-SUBAGENT-FEEDBACK.md)
5. **Incorporate feedback** (plan/future-plans/plan_name-AFTER_FEEDBACK.md)
6. **Review test coverage** with /review-tests command
7. **Write missing tests** if needed (with user approval)
8. **Execute refactoring** (with explicit user approval)

## Detailed Process Steps

### Step 1: Research Refactoring Patterns

Before analyzing the codebase, research the latest refactoring patterns from Dave Farley and Kent Beck:

1. **Use WebSearch to research**:
   - Search for "Dave Farley modern software engineering refactoring patterns 2026"
   - Search for "Kent Beck Tidy First preparatory refactoring patterns 2026"
   - Search for specific patterns relevant to the codebase language/framework

2. **Extract key patterns**:
   - Document refactoring techniques from research
   - Identify patterns applicable to this codebase
   - Note specific examples or case studies

3. **Create research summary**:
   - Save findings to `plan/future-plans/refactoring-research-YYYY-MM-DD.md`
   - Include sources and citations
   - Highlight patterns most relevant to this project

### Step 2: Analyze Codebase

1. **Parse target arguments** (if provided):
   - Extract targets from command args
   - Validate each target exists (file or directory)
   - If target is directory, expand to all .py files
   - If no targets, analyze all of `src/`

2. **Code quality analysis**:
   - Use Read tool to examine all relevant source files
   - Identify code smells:
     - Long functions/methods (>50 lines)
     - Deep nesting (>3 levels)
     - Duplicated code
     - Large classes (God objects)
     - Feature envy (methods using other classes' data extensively)
     - Primitive obsession (not using domain types)
     - Long parameter lists (>3-4 parameters)
     - Switch statements / complex conditionals
     - Comments that explain "why" code is confusing (smell indicator)

3. **Architectural analysis**:
   - Identify separation of concerns violations
   - Look for tight coupling
   - Find missing abstractions
   - Identify overly-complex abstractions
   - Check dependency directions (do they point toward stability?)

4. **Pattern analysis**:
   - Identify existing patterns in the codebase
   - Look for pattern inconsistencies
   - Find missing patterns that would help

5. **Test coverage consideration**:
   - Note which code has tests
   - Identify critical code without tests
   - Consider testability of current structure

### Step 3: Create Detailed Refactoring Plan (First Output)

Create a comprehensive, step-by-step refactoring plan that a sub-agent could follow without further context.

**Plan Structure:**

```markdown
# Refactoring Plan: [Descriptive Name]

**Date:** YYYY-MM-DD
**Scope:** [Full codebase | Specific files: ...]
**Principles:** Dave Farley's Continuous Delivery + Kent Beck's Preparatory Refactoring

---

## Executive Summary

**Goal:** [What we're trying to achieve]

**Approach:** [High-level strategy]

**Estimated Effort:** [X hours/days - be realistic]

**Risk Level:** [Low/Medium/High]

**Key Benefits:**
- [Benefit 1]
- [Benefit 2]

---

## Research Summary

[Include key findings from Step 1 research]

**Applicable Patterns:**
1. [Pattern name] - [Why relevant]
2. [Pattern name] - [Why relevant]

**Sources:**
- [Source 1 with URL]
- [Source 2 with URL]

---

## Current State Analysis

### Code Smells Identified

#### [File: src/example.py]

1. **Long Method: `function_name()` (lines X-Y)**
   - Current: XX lines
   - Issue: Does too many things
   - Beck principle violated: Simple design
   - Impact: Hard to test, hard to understand

2. **Duplicated Code**
   - Locations: [file1:lines, file2:lines]
   - Issue: Same logic in multiple places
   - Farley principle violated: Single source of truth
   - Impact: Bugs require multiple fixes

[Continue for each smell]

### Architectural Issues

1. **Tight Coupling: [Component A] → [Component B]**
   - Issue: Component A directly instantiates Component B
   - Impact: Hard to test, hard to change
   - Target: Dependency injection pattern

[Continue for each issue]

### Missing Patterns

1. **No Factory Pattern for [Component]**
   - Issue: Construction logic scattered
   - Benefit: Centralized, testable construction
   - Beck principle: Separate concerns

---

## Refactoring Strategy

**Approach:** Preparatory Refactoring ("Make the change easy")

We will NOT immediately fix all issues. Instead:
1. First, make small tidyings to improve structure
2. Each tidying is independently valuable
3. Each tidying leaves code in working state
4. Tests pass after each tidying

**Phases:**
- Phase 1: Preparatory tidyings (make change easy)
- Phase 2: Structural improvements (the easy change)
- Phase 3: Pattern application (if still needed)
- Phase 4: Validation & cleanup

---

## Refactoring Phases

### Phase 1: Preparatory Tidyings

**Goal:** Make the codebase easier to refactor

**Duration:** [X hours]

**Prerequisites:** None

**Steps:**

1. **Extract Magic Numbers** (30 minutes)
   - File: `src/example.py`
   - Lines: XX-YY
   - Action: Replace hardcoded values with named constants
   - Example:
     ```python
     # Before
     if len(items) > 5:

     # After
     MAX_ITEMS = 5
     if len(items) > MAX_ITEMS:
     ```
   - Tests affected: [test file(s)]
   - Verification: `uv run pytest tests/test_example.py`

2. **Rename Variables for Clarity** (20 minutes)
   - File: `src/example.py`
   - Variables: `x` → `user_count`, `tmp` → `sanitized_input`
   - Rationale: Self-documenting code
   - Verification: `uv run pytest`

[Continue with each tidying - be specific]

**Success Criteria:**
- [ ] All magic numbers extracted to constants
- [ ] All variables have meaningful names
- [ ] All tests pass: `uv run pytest`
- [ ] Code coverage unchanged or improved

**Rollback Plan:** Git revert to commit before Phase 1

---

### Phase 2: Structural Improvements

**Goal:** [Specific structural goal]

**Duration:** [X hours]

**Prerequisites:** Phase 1 complete

**Steps:**

1. **Extract Long Method: `process_data()` → Multiple Methods** (45 minutes)
   - File: `src/example.py`
   - Current: Lines XX-YY (80 lines)
   - Target: Extract into:
     - `validate_input()` (lines XX-YY)
     - `transform_data()` (lines XX-YY)
     - `save_results()` (lines XX-YY)
   - Detailed steps:
     a. Run existing tests to establish baseline
     b. Extract `validate_input()` method
     c. Run tests (must pass)
     d. Extract `transform_data()` method
     e. Run tests (must pass)
     f. Extract `save_results()` method
     g. Run tests (must pass)
     h. Update `process_data()` to call extracted methods
     i. Run full test suite
   - Tests affected: `tests/test_example.py::test_process_data`
   - New tests needed:
     - `test_validate_input_with_valid_data`
     - `test_validate_input_with_invalid_data`
     - `test_transform_data`
     - `test_save_results`

[Continue with each structural change - extreme detail]

**Success Criteria:**
- [ ] All long methods (>50 lines) extracted
- [ ] Each new method has unit tests
- [ ] Integration tests still pass
- [ ] Code coverage >= previous level

**Rollback Plan:** Git revert to commit after Phase 1

---

### Phase 3: Pattern Application

[Similar detailed structure]

---

### Phase 4: Validation & Cleanup

[Similar detailed structure]

---

## Dependency Graph

```
Phase 1 (Preparatory)
    ↓
Phase 2 (Structural)
    ↓
Phase 3 (Patterns)
    ↓
Phase 4 (Validation)
```

**Parallelization:** None - must be sequential due to dependencies

---

## Testing Strategy

### Pre-Refactoring Tests

**Existing Coverage:**
- [Summary from codebase analysis]

**Gaps Identified:**
- [Critical functions without tests]
- [Edge cases not covered]

**Required Before Refactoring:**
- [ ] Test coverage for `function_x()`
- [ ] Integration test for `component_y`
- [ ] Edge case tests for error handling

### During Refactoring

**Per-Phase Testing:**
- After each tidying: Run affected tests
- After each phase: Run full test suite
- No phase proceeds if tests fail

**Test Additions:**
- Phase 2: [X new unit tests for extracted methods]
- Phase 3: [Y new integration tests]

### Post-Refactoring Validation

- [ ] All existing tests pass
- [ ] All new tests pass
- [ ] Code coverage >= baseline
- [ ] Performance tests pass (if applicable)
- [ ] Manual smoke test of key features

---

## Risk Assessment

### High Risk Areas

1. **[Component/Function Name]**
   - Risk: [What could go wrong]
   - Mitigation: [How we'll prevent it]
   - Rollback: [How to undo if needed]

### Mitigation Strategies

1. **Comprehensive Testing**
   - Write tests BEFORE refactoring
   - Run tests AFTER each change
   - Never commit failing tests

2. **Small Steps**
   - Each commit is independently valuable
   - Each commit leaves code working
   - Easy to rollback any step

3. **Continuous Validation**
   - Tests run locally before commit
   - CI/CD runs full suite
   - Monitor for regressions

---

## Success Criteria

### Code Quality Metrics

- [ ] Cyclomatic complexity reduced by X%
- [ ] Average method length < 30 lines
- [ ] No methods > 50 lines
- [ ] No duplicated code blocks
- [ ] All code smells addressed

### Test Metrics

- [ ] Code coverage >= [X%]
- [ ] All critical paths tested
- [ ] All edge cases tested
- [ ] Test execution time < [X seconds]

### Production Readiness

- [ ] All tests passing
- [ ] No breaking changes to public APIs
- [ ] Documentation updated
- [ ] AGENTS.md updated with new patterns
- [ ] Ready for code review
- [ ] Ready for deployment

---

## Implementation Notes

### Tools Required

- `uv run pytest` - Test execution
- `uv run ruff check` - Linting
- `uv run ruff format` - Code formatting
- Git - Version control

### Developer Guidelines

1. **Make each change small** - Kent Beck's "tidyings" principle
2. **Test after each change** - Continuous validation
3. **Commit frequently** - Easy rollback points
4. **Never break main** - All commits should pass tests
5. **Document decisions** - Update AGENTS.md with patterns

### Common Pitfalls to Avoid

1. **Don't refactor without tests** - Write tests first
2. **Don't make multiple changes at once** - One tidying at a time
3. **Don't skip verification** - Run tests after each change
4. **Don't over-engineer** - YAGNI principle
5. **Don't create hypothetical abstractions** - Wait for actual need

---

## Appendix: Detailed Code Examples

### Example 1: Extract Method Refactoring

**Before:**
```python
def process_user_data(data):
    # Validation (lines 1-15)
    if not data:
        raise ValueError("Data required")
    if 'email' not in data:
        raise ValueError("Email required")
    # ... more validation

    # Transformation (lines 16-40)
    user = User()
    user.email = data['email'].lower().strip()
    # ... more transformation

    # Persistence (lines 41-55)
    db.save(user)
    cache.set(user.id, user)
    # ... more persistence

    return user
```

**After:**
```python
def process_user_data(data):
    """Process and save user data using SRP."""
    validated = _validate_user_data(data)
    user = _transform_to_user(validated)
    _persist_user(user)
    return user

def _validate_user_data(data):
    """Validate user data structure and contents."""
    if not data:
        raise ValueError("Data required")
    if 'email' not in data:
        raise ValueError("Email required")
    return data

def _transform_to_user(data):
    """Transform validated data into User model."""
    user = User()
    user.email = data['email'].lower().strip()
    return user

def _persist_user(user):
    """Save user to database and cache."""
    db.save(user)
    cache.set(user.id, user)
```

**Benefits:**
- Each function has single responsibility
- Each function is testable in isolation
- Clear separation of concerns
- Self-documenting code structure

---

**Plan Version:** 1.0
**Last Updated:** [YYYY-MM-DD]
**Status:** Draft - Awaiting Review
```

**File Path:** `plan/future-plans/refactoring-[scope]-YYYY-MM-DD.md`

Where `[scope]` is:
- `full` if analyzing entire codebase
- `[filename]` if targeting specific file(s)
- `[directory]` if targeting specific directory

### Step 4: Spawn Review Sub-Agent (Collect Feedback)

After creating the initial plan, spawn a specialized review agent to check for correctness, completeness, and inconsistencies.

1. **Read the plan file completely**:
   ```bash
   Read plan/future-plans/refactoring-[scope]-YYYY-MM-DD.md
   ```

2. **Spawn review agent using Task tool**:
   - Use subagent_type: "general-purpose"
   - Use model: "opus" for strong analytical reasoning
   - Provide detailed review prompt:

   ```
   You are a specialized refactoring plan review agent. Your task is to review this refactoring plan for correctness, completeness, consistency, and safety.

   ## Review Guidelines

   1. **Farley-Beck Principles Adherence**
      - Does plan follow "make change easy, then make easy change"?
      - Are changes small and incremental?
      - Is each step independently valuable?
      - Is continuous validation emphasized?

   2. **Technical Correctness**
      - Are refactoring techniques sound?
      - Are file paths and line numbers realistic?
      - Do code examples follow Python best practices?
      - Are the proposed patterns appropriate?

   3. **Completeness**
      - Are all steps detailed enough to execute?
      - Are prerequisites clearly stated?
      - Are success criteria measurable?
      - Are rollback plans adequate?

   4. **Safety & Risk Management**
      - Is testing strategy comprehensive?
      - Are high-risk areas identified?
      - Are mitigation strategies adequate?
      - Is rollback plan clear?

   5. **Consistency**
      - Is terminology consistent throughout?
      - Do phases follow logical progression?
      - Are dependencies correctly identified?
      - Is formatting consistent?

   ## Output Format

   Provide structured feedback as markdown:

   ```markdown
   # Refactoring Plan Review Feedback

   **Review Date:** YYYY-MM-DD
   **Reviewer:** Claude Sub-Agent
   **Plan:** [plan name]

   ---

   ## Overall Assessment

   **Quality Score:** [X/10]
   **Readiness:** [Ready to Execute | Needs Minor Changes | Needs Major Revision]

   **Summary:** [2-3 sentences on overall quality]

   ---

   ## Strengths

   1. [Specific strength with reference to plan section]
   2. [Another strength]

   ---

   ## Issues Found

   ### Critical Issues (Must Fix)

   1. **[Issue Title]**
      - Location: [Section/Phase reference]
      - Problem: [What's wrong]
      - Impact: [Why this matters]
      - Suggestion: [How to fix]

   ### Major Issues (Should Fix)

   [Same structure]

   ### Minor Issues (Nice to Fix)

   [Same structure]

   ---

   ## Specific Recommendations

   ### Testing Strategy
   - [Recommendation 1]
   - [Recommendation 2]

   ### Refactoring Steps
   - [Recommendation 1]
   - [Recommendation 2]

   ### Risk Management
   - [Recommendation 1]
   - [Recommendation 2]

   ---

   ## Principle Adherence Check

   **Dave Farley Principles:**
   - [ ] Small, incremental changes
   - [ ] Continuous validation through tests
   - [ ] Evidence-based approach
   - [ ] Automation emphasis

   **Kent Beck Principles:**
   - [ ] Preparatory refactoring first
   - [ ] Tidyings (small steps)
   - [ ] Separate structural from behavioral
   - [ ] TDD approach
   - [ ] Simple design / YAGNI

   **Issues with Principles:**
   - [Any violations or concerns]

   ---

   ## Completeness Check

   - [ ] All phases have detailed steps
   - [ ] Each step has verification method
   - [ ] Success criteria are measurable
   - [ ] Rollback plans exist
   - [ ] Prerequisites clearly stated
   - [ ] Code examples are complete
   - [ ] Testing strategy is comprehensive

   **Missing Elements:**
   - [Anything that should be added]

   ---

   ## Final Recommendation

   [Clear statement: "Ready to proceed" OR "Revise plan before proceeding" with rationale]
   ```

   ## Plan to Review

   [INSERT PLAN CONTENT HERE]
   ```

3. **Wait for review completion**:
   - Do NOT run in background
   - Wait for sub-agent to complete analysis

4. **Save feedback**:
   - Write feedback to: `plan/future-plans/refactoring-[scope]-YYYY-MM-DD-SUBAGENT-FEEDBACK.md`

### Step 5: Incorporate Feedback (Second Output)

1. **Read both files**:
   - Original plan: `plan/future-plans/refactoring-[scope]-YYYY-MM-DD.md`
   - Feedback: `plan/future-plans/refactoring-[scope]-YYYY-MM-DD-SUBAGENT-FEEDBACK.md`

2. **Analyze feedback**:
   - Identify critical and major issues
   - Understand all recommendations
   - Determine which feedback to incorporate

3. **Create improved plan**:
   - Start with original plan content
   - Address all critical issues
   - Address major issues where appropriate
   - Consider minor issues
   - Add "Revision History" section documenting changes
   - Ensure plan is still detailed enough for sub-agent execution

4. **Add revision tracking**:
   ```markdown
   ## Revision History

   ### Version 2.0 - YYYY-MM-DD (Post-Review)

   **Changes Made:**
   1. [Critical issue fixed: description]
   2. [Major issue addressed: description]
   3. [Improvement added: description]

   **Feedback Incorporated:**
   - [Reference to feedback item 1]
   - [Reference to feedback item 2]

   **Feedback Not Incorporated:**
   - [Item X: Reason why not incorporated]

   **Reviewer Comments Addressed:** [X/Y items]
   ```

5. **Save improved plan**:
   - File: `plan/future-plans/refactoring-[scope]-YYYY-MM-DD-AFTER_FEEDBACK.md`
   - This is now the authoritative refactoring plan

### Step 6: Review Test Coverage

After finalizing the refactoring plan, review existing test coverage to ensure the refactoring can be performed safely.

1. **Invoke /review-tests command**:
   - If refactoring specific files: `/review-tests [target files]`
   - If refactoring entire codebase: `/review-tests`
   - This command will generate a comprehensive test coverage report

2. **Wait for test review completion**:
   - Review agent will analyze existing tests
   - Report will identify gaps and missing coverage
   - Report saved to: `plan/review-tests/YYYY-MM-DD-HHMMSS-test-coverage-review[-scope].md`

3. **Analyze test coverage report**:
   - Read the generated report completely
   - Identify critical gaps related to refactoring targets
   - Note missing unit tests, integration tests, edge cases
   - Calculate coverage percentage for refactoring targets

4. **Determine test sufficiency**:

   **Sufficient test coverage criteria:**
   - All code being refactored has unit tests
   - Critical paths have integration tests
   - Edge cases are covered
   - Test coverage >= 80% for target code
   - Tests are reliable (not flaky)

   **Insufficient test coverage indicators:**
   - Target code has no tests
   - Coverage < 60% for target code
   - Missing critical edge case tests
   - Missing integration tests
   - Existing tests are flaky or unreliable

### Step 7: Handle Insufficient Test Coverage

If test coverage is insufficient, STOP and get user approval before proceeding.

1. **Create test gaps summary**:
   ```markdown
   ## Test Coverage Analysis for Refactoring

   **Refactoring Target:** [scope]
   **Current Coverage:** [X%]
   **Required Coverage:** 80%+

   **Assessment:** INSUFFICIENT - Refactoring without adequate tests is unsafe

   ### Critical Gaps

   The following tests are REQUIRED before refactoring can proceed safely:

   1. **[Module/Function]** (Priority: Critical)
      - Missing: [specific test scenarios]
      - Risk: [what could break without these tests]
      - Estimated effort: [X unit tests]

   2. **[Module/Function]** (Priority: Critical)
      - Missing: [specific test scenarios]
      - Risk: [what could break]
      - Estimated effort: [X tests]

   [Continue for all critical gaps]

   ### Recommended Test Suite

   **Unit Tests:** [X tests needed]
   - [test_file_1.py]: [X tests]
   - [test_file_2.py]: [Y tests]

   **Integration Tests:** [Y tests needed]
   - [test_integration.py]: [Z tests]

   **Total Estimated Effort:** [XX tests, approximately X hours]
   ```

2. **Present to user with AskUserQuestion**:
   ```
   ⚠️  INSUFFICIENT TEST COVERAGE DETECTED

   The refactoring plan targets code with insufficient test coverage.

   Current coverage: [X%]
   Required coverage: 80%+

   Critical gaps identified:
   - [Gap 1]
   - [Gap 2]
   - [Gap 3]

   Dave Farley and Kent Beck both emphasize: NEVER refactor without tests.

   Required tests before refactoring:
   - [X] unit tests
   - [Y] integration tests
   - Estimated effort: [Z hours]

   See detailed analysis in: [path to test gaps summary]

   Would you like me to:
   1. Write the required tests first (TDD approach - RECOMMENDED)
   2. Proceed with refactoring anyway (RISKY - not recommended)
   3. Cancel refactoring until tests are manually written
   ```

3. **Use AskUserQuestion tool**:
   ```json
   {
     "questions": [
       {
         "question": "Test coverage is insufficient for safe refactoring. How would you like to proceed?",
         "header": "Tests needed",
         "multiSelect": false,
         "options": [
           {
             "label": "Write tests first (Recommended)",
             "description": "Follow TDD approach: write missing tests before refactoring. This is the safest option and aligns with Farley-Beck principles."
           },
           {
             "label": "Review gaps and decide",
             "description": "I'll review the test gap analysis and decide which tests to write manually before proceeding."
           },
           {
             "label": "Skip tests (Not recommended)",
             "description": "Proceed with refactoring without additional tests. This is risky and NOT recommended by Farley or Beck."
           }
         ]
       }
     ]
   }
   ```

4. **Handle user response**:

   **If "Write tests first" selected**:
   - Proceed to Step 8 (Write Missing Tests)

   **If "Review gaps and decide" selected**:
   - Present detailed test gap analysis
   - STOP and wait for explicit instruction
   - Do NOT proceed with refactoring

   **If "Skip tests" selected**:
   - Issue strong warning about risks
   - Ask for explicit confirmation: "I understand the risks and want to proceed without tests"
   - Document in refactoring plan that tests were skipped
   - Add explicit rollback checkpoint before starting
   - If confirmed, proceed to Step 9

### Step 8: Write Missing Tests (TDD Approach)

If user approves writing tests first, spawn a specialized test-writing agent.

1. **Create test specification document**:
   - Combine refactoring plan + test coverage report
   - Extract specific test requirements
   - Prioritize critical tests
   - Create detailed test specifications

2. **Spawn test-writing agent using Task tool**:
   - Use subagent_type: "general-purpose" with writing-tests skill
   - Provide comprehensive test requirements
   - Include context from refactoring plan
   - Reference existing tests for style/patterns

   ```
   You are a test-writing agent following TDD principles. Write comprehensive tests for code that will be refactored.

   ## Context

   We are preparing to refactor the following code:
   [Scope from refactoring plan]

   Test coverage analysis shows these critical gaps:
   [Gaps from test review]

   ## Requirements

   Write tests following these principles:
   1. **Test behavior, not implementation** - Tests should verify what code does, not how
   2. **Use real dependencies** - Avoid excessive mocking (Testing Trophy model)
   3. **Follow AAA pattern** - Arrange, Act, Assert
   4. **One assertion per concept** - Tests can have multiple assertions if testing one behavior
   5. **Fixtures in conftest.py** - All reusable fixtures go in tests/conftest.py
   6. **Clear naming** - test_function_name_scenario_expected_result

   ## Test Specifications

   [Detailed specifications from test gap analysis]

   ### Unit Tests Required

   1. **test_config.py**
      - test_appconfig_loads_from_env_local
        - Setup: Create .env.local with valid credentials
        - Action: Initialize AppConfig
        - Assert: All fields populated correctly
      [etc.]

   ### Integration Tests Required

   [Detailed specifications]

   ## Success Criteria

   - [ ] All specified tests written
   - [ ] All tests pass
   - [ ] Code coverage for target code >= 80%
   - [ ] Tests are reliable (run multiple times)
   - [ ] Fixtures properly organized in conftest.py
   - [ ] Tests follow existing project patterns

   ## Existing Test Patterns

   [Examples from existing test files]
   ```

3. **Wait for test-writing completion**:
   - Agent will write all specified tests
   - Agent will run tests to verify they pass
   - Agent will report coverage metrics

4. **Verify test quality**:
   - Read generated test files
   - Run test suite: `uv run pytest -v`
   - Check coverage: `uv run pytest --cov=src --cov-report=term`
   - Ensure coverage >= 80% for refactoring targets

5. **If tests insufficient**:
   - Identify remaining gaps
   - Ask user if more tests needed
   - Iterate until coverage adequate

6. **If tests adequate**:
   - Commit tests: `git add tests/ && git commit -m "test: Add tests for upcoming refactoring"`
   - Proceed to Step 9

### Step 9: Get Explicit User Approval for Refactoring

Before executing the refactoring, get explicit user approval.

1. **Create refactoring summary**:
   ```markdown
   ## Refactoring Summary

   **Plan:** plan/future-plans/refactoring-[scope]-YYYY-MM-DD-AFTER_FEEDBACK.md
   **Test Coverage:** [X%] (was [Y%])
   **Test Suite:** [X tests added, Y existing]
   **Scope:** [Files/modules to be refactored]

   ### Changes Overview

   **Phase 1: Preparatory Tidyings**
   - [X tidyings]
   - [Duration estimate]
   - [Files affected]

   **Phase 2: Structural Improvements**
   - [Y refactorings]
   - [Duration estimate]
   - [Files affected]

   **Phase 3: Pattern Application**
   - [Z patterns]
   - [Duration estimate]
   - [Files affected]

   ### Safety Measures

   - ✅ Comprehensive test coverage (≥80%)
   - ✅ Small, incremental steps
   - ✅ Tests run after each change
   - ✅ Clear rollback plan
   - ✅ Follows Farley-Beck principles

   ### Risks

   - [Risk 1 + mitigation]
   - [Risk 2 + mitigation]

   ### Estimated Duration

   [X hours/days] - based on plan estimates
   ```

2. **Present to user**:
   ```
   ✅ READY TO BEGIN REFACTORING

   All prerequisites complete:
   - ✅ Research conducted
   - ✅ Refactoring plan created
   - ✅ Plan reviewed and revised
   - ✅ Test coverage verified/improved ([X%])
   - ✅ Safety measures in place

   Plan: plan/future-plans/refactoring-[scope]-YYYY-MM-DD-AFTER_FEEDBACK.md

   Scope: [description]
   Estimated effort: [X hours]
   Risk level: [Low/Medium/High]

   The refactoring will:
   - [Benefit 1]
   - [Benefit 2]
   - [Benefit 3]

   See full summary above for details.

   May I proceed with executing the refactoring plan?
   ```

3. **Use AskUserQuestion tool**:
   ```json
   {
     "questions": [
       {
         "question": "All prerequisites complete. May I proceed with the refactoring?",
         "header": "Start refactoring?",
         "multiSelect": false,
         "options": [
           {
             "label": "Yes, proceed (Recommended)",
             "description": "Execute the refactoring plan following all Farley-Beck principles with comprehensive test coverage."
           },
           {
             "label": "Review plan first",
             "description": "Let me review the plan and summary before deciding."
           },
           {
             "label": "Make changes to plan",
             "description": "I want to modify the plan before execution."
           },
           {
             "label": "Cancel refactoring",
             "description": "Do not proceed with refactoring at this time."
           }
         ]
       }
     ]
   }
   ```

4. **Handle user response**:

   **If "Yes, proceed" selected**:
   - Proceed to Step 10 (Execute Refactoring)

   **If "Review plan first" selected**:
   - Present plan location
   - STOP and wait for user to review
   - After review, ask again for approval

   **If "Make changes to plan" selected**:
   - Ask what changes are needed
   - Update plan accordingly
   - Re-run review if major changes
   - Ask again for approval

   **If "Cancel refactoring" selected**:
   - Save all work done so far
   - Provide summary of artifacts created
   - Exit gracefully

### Step 10: Execute Refactoring Plan

With explicit user approval, execute the refactoring plan.

1. **Create execution tracking**:
   - Create file: `plan/future-plans/refactoring-[scope]-YYYY-MM-DD-EXECUTION.md`
   - Log each phase/step as executed
   - Record test results
   - Note any deviations from plan

2. **Execute Phase 1**:
   - Follow plan steps exactly
   - After EACH tidying:
     - Run affected tests
     - Verify tests pass
     - If tests fail: STOP, rollback, analyze
   - After phase complete:
     - Run full test suite: `uv run pytest`
     - Run linter: `uv run ruff check`
     - Format code: `uv run ruff format`
     - Git commit: `git add . && git commit -m "refactor: Phase 1 - Preparatory tidyings"`

3. **Execute Phase 2**:
   - [Same process as Phase 1]
   - More granular commits encouraged
   - Test after each structural change

4. **Execute Phase 3**:
   - [Same process]

5. **Execute Phase 4** (Validation & Cleanup):
   - Run complete test suite
   - Verify all success criteria met
   - Update documentation (AGENTS.md if patterns changed)
   - Final lint and format
   - Final commit

6. **Update execution log**:
   ```markdown
   # Refactoring Execution Log

   **Plan:** refactoring-[scope]-YYYY-MM-DD-AFTER_FEEDBACK.md
   **Started:** YYYY-MM-DD HH:MM:SS
   **Completed:** YYYY-MM-DD HH:MM:SS
   **Duration:** [X hours]

   ## Phase 1: Preparatory Tidyings

   ✅ Completed: YYYY-MM-DD HH:MM:SS

   **Steps Executed:**
   1. ✅ Extract Magic Numbers (25 mins)
      - Tests: PASSED
      - Commit: abc1234
   2. ✅ Rename Variables (18 mins)
      - Tests: PASSED
      - Commit: def5678

   **Phase Results:**
   - All tests passed: ✅
   - Code coverage: [X%]
   - Issues encountered: None
   - Deviations from plan: None

   ## Phase 2: Structural Improvements

   [Same format]

   ## Final Results

   **Success Criteria:**
   - ✅ All tests passing
   - ✅ Code coverage >= [X%]
   - ✅ Cyclomatic complexity reduced
   - ✅ Code smells addressed
   - ✅ Documentation updated

   **Metrics:**
   - Tests added: [X]
   - Tests passing: [Y/Y]
   - Coverage before: [X%]
   - Coverage after: [Y%]
   - Commits created: [Z]

   **Artifacts Created:**
   - Refactoring plan (3 versions)
   - Test coverage review
   - Execution log
   - [X] new test files
   - [Y] refactored source files
   ```

### Step 11: Final Report

Present completion summary to user:

```
✅ REFACTORING COMPLETE

Scope: [scope description]
Duration: [X hours] ([Y hours estimated])
Phases: 4/4 completed

Results:
- ✅ All [X] tests passing
- ✅ Code coverage: [Y%] (was [Z%])
- ✅ [N] code smells eliminated
- ✅ [M] commits created
- ✅ Ready for production

Artifacts created:
1. plan/future-plans/refactoring-research-YYYY-MM-DD.md
2. plan/future-plans/refactoring-[scope]-YYYY-MM-DD.md (original)
3. plan/future-plans/refactoring-[scope]-YYYY-MM-DD-SUBAGENT-FEEDBACK.md
4. plan/future-plans/refactoring-[scope]-YYYY-MM-DD-AFTER_FEEDBACK.md (final plan)
5. plan/review-tests/YYYY-MM-DD-HHMMSS-test-coverage-review.md
6. plan/future-plans/refactoring-[scope]-YYYY-MM-DD-EXECUTION.md (execution log)

Files modified:
- [List of source files]
- [List of test files]

Commits:
- [commit hash]: refactor: Phase 1 - Preparatory tidyings
- [commit hash]: refactor: Phase 2 - Structural improvements
- [etc.]

Next steps:
- Review changes: git log
- Run full test suite: uv run pytest
- Create PR if ready: /commit-push-pr
- Update AGENTS.md with new patterns learned
```

## Important Guidelines

### 1. Principle Adherence

**Dave Farley:**
- Small, incremental changes only
- Every change must be validated by tests
- Evidence-based decisions
- Continuous integration (tests always pass)
- Focus on production quality

**Kent Beck:**
- "Make the change easy, then make the easy change"
- Tidyings are small (minutes to hours)
- Separate structural from behavioral changes
- TDD: write tests before refactoring
- YAGNI: no hypothetical abstractions
- Simple design: grow organically

### 2. Safety First

- **NEVER refactor without tests**
- **NEVER make large changes**
- **NEVER skip verification steps**
- **NEVER continue if tests fail**
- **ALWAYS have a rollback plan**

### 3. User Control

- **ALWAYS get explicit approval before:**
  - Writing tests (if coverage insufficient)
  - Executing refactoring plan
  - Making changes to user's code

- **ALWAYS stop and ask if:**
  - Plan is ambiguous
  - Tests are failing
  - Unexpected issues arise
  - Risk level increases

### 4. Documentation

- Research findings with sources
- Detailed, executable plans
- Comprehensive test coverage reports
- Execution logs with results
- All artifacts saved to plan/future-plans/

### 5. Test-Driven

- Tests BEFORE refactoring (TDD)
- Tests AFTER each change (verification)
- Comprehensive coverage (≥80%)
- All tests in conftest.py fixtures
- Follow project test patterns

## Common Refactoring Patterns (from Research)

### Kent Beck's Tidyings (from "Tidy First?")

1. **Guard clauses** - Early returns for error conditions
2. **Dead code elimination** - Remove unused code
3. **Normalize symmetries** - Make similar code look similar
4. **Explicit parameters** - Replace magic values with parameters
5. **Chunk statements** - Group related lines
6. **Extract helper** - Pull out helper functions
7. **One pile** - Gather scattered logic
8. **Explaining constants** - Named constants instead of literals
9. **Explaining variables** - Intermediate variables with names
10. **Inline method** - Remove unnecessary indirection

### Dave Farley's Patterns (from Modern Software Engineering)

1. **Modularity** - Strong cohesion, loose coupling
2. **Separation of concerns** - Each module one responsibility
3. **Information hiding** - Encapsulate implementation details
4. **Testability** - Design for automated testing
5. **Deployability** - Small, incremental, reversible changes

## Example Interaction Flow

```
User: /refactor-production src/config.py
Assistant: I'll review src/config.py with Farley-Beck principles and create a production-ready refactoring plan...

[Step 1: Research]
Searching for latest Farley-Beck refactoring patterns...
✅ Research complete. Saved to: plan/future-plans/refactoring-research-2026-01-24.md

[Step 2: Analyze Codebase]
Reading src/config.py...
Analyzing code quality...
Identified:
- 3 code smells
- 2 architectural issues
- 1 missing pattern

[Step 3: Create Initial Plan]
Creating detailed refactoring plan...
✅ Plan created: plan/future-plans/refactoring-config-2026-01-24.md

[Step 4: Spawn Review Agent]
Spawning sub-agent to review plan for correctness...
[Agent reviews plan]
✅ Feedback saved: plan/future-plans/refactoring-config-2026-01-24-SUBAGENT-FEEDBACK.md

[Step 5: Incorporate Feedback]
Analyzing feedback...
Addressing 2 critical issues, 3 major issues...
✅ Improved plan saved: plan/future-plans/refactoring-config-2026-01-24-AFTER_FEEDBACK.md

[Step 6: Review Test Coverage]
Running /review-tests src/config.py...
✅ Test coverage review: plan/review-tests/2026-01-24-120000-test-coverage-review-config.md

Test Coverage Analysis:
- Current coverage: 15%
- Required coverage: 80%+
- Gap: 13 critical tests missing

[Step 7: Handle Insufficient Coverage]
⚠️  INSUFFICIENT TEST COVERAGE DETECTED

The refactoring targets code with inadequate test coverage.

Current coverage: 15%
Required coverage: 80%+

Critical gaps:
- AppConfig initialization (5 tests)
- Environment loading (4 tests)
- Validation logic (4 tests)

Required tests: 13 unit tests (~2 hours)

Would you like me to:
1. Write tests first (TDD - RECOMMENDED)
2. Review gaps and decide
3. Skip tests (NOT recommended)

User: Write tests first

Assistant: [Step 8: Write Missing Tests]
Spawning test-writing agent...
[Agent writes comprehensive tests]
✅ Tests written: tests/test_config.py (13 new tests)

Running tests...
```
uv run pytest tests/test_config.py -v
========================= 13 passed in 2.3s =========================
```

Code coverage for src/config.py: 85% ✅

Committing tests...
```
git add tests/test_config.py
git commit -m "test: Add comprehensive tests for config.py before refactoring"
```

[Step 9: Get Explicit Approval]
✅ READY TO BEGIN REFACTORING

All prerequisites complete:
- ✅ Research conducted
- ✅ Refactoring plan created
- ✅ Plan reviewed and revised
- ✅ Test coverage improved (85%)
- ✅ Safety measures in place

Plan: plan/future-plans/refactoring-config-2026-01-24-AFTER_FEEDBACK.md

Scope: src/config.py
Estimated effort: 3 hours
Risk level: Low

Benefits:
- Eliminate code smells
- Improve testability
- Better separation of concerns

May I proceed?

User: Yes, proceed

Assistant: [Step 10: Execute Refactoring]
Starting execution...

Phase 1: Preparatory Tidyings
  ✓ Extract magic numbers (config.py:45-48)
    Tests: PASSED
  ✓ Rename unclear variables (config.py:52-60)
    Tests: PASSED
  ✓ Add explaining constants (config.py:75-80)
    Tests: PASSED
  ✅ Phase 1 complete
  ```
  git commit -m "refactor: Phase 1 - Preparatory tidyings"
  ```

Phase 2: Structural Improvements
  ✓ Extract validation method (config.py:100-125)
    Tests: PASSED (including 3 new tests)
  ✓ Extract factory method (config.py:140-165)
    Tests: PASSED
  ✅ Phase 2 complete
  ```
  git commit -m "refactor: Phase 2 - Structural improvements"
  ```

Phase 3: Pattern Application
  ✓ Apply Builder pattern for complex config
    Tests: PASSED
  ✅ Phase 3 complete
  ```
  git commit -m "refactor: Phase 3 - Apply Builder pattern"
  ```

Phase 4: Validation & Cleanup
  ✓ Full test suite: 24/24 passed ✅
  ✓ Code coverage: 92% ✅
  ✓ Linting: No issues ✅
  ✓ Documentation updated ✅
  ✅ Phase 4 complete
  ```
  git commit -m "refactor: Phase 4 - Final validation and cleanup"
  ```

[Step 11: Final Report]
✅ REFACTORING COMPLETE

Scope: src/config.py
Duration: 2.8 hours (3 hours estimated)
Phases: 4/4 completed

Results:
- ✅ All 24 tests passing
- ✅ Code coverage: 92% (was 15%)
- ✅ 5 code smells eliminated
- ✅ 4 commits created
- ✅ Ready for production

Artifacts created:
1. plan/future-plans/refactoring-research-2026-01-24.md
2. plan/future-plans/refactoring-config-2026-01-24.md
3. plan/future-plans/refactoring-config-2026-01-24-SUBAGENT-FEEDBACK.md
4. plan/future-plans/refactoring-config-2026-01-24-AFTER_FEEDBACK.md
5. plan/review-tests/2026-01-24-120000-test-coverage-review-config.md
6. plan/future-plans/refactoring-config-2026-01-24-EXECUTION.md

Files modified:
- src/config.py
- tests/test_config.py (13 new tests)

Next steps:
- Review changes: git log -p
- Run full test suite: uv run pytest
- Create PR: /commit-push-pr
```

---

**Note:** This is a production-quality refactoring command that prioritizes safety, testing, and user control while applying industry-leading principles from Dave Farley and Kent Beck.
