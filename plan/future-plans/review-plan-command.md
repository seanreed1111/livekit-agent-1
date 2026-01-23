# Implementation Plan: Review Plan Command

> **Status:** DRAFT
> **Created:** 2026-01-23

## Table of Contents

- [Overview](#overview)
- [Current State Analysis](#current-state-analysis)
- [Desired End State](#desired-end-state)
- [What We're NOT Doing](#what-were-not-doing)
- [Implementation Approach](#implementation-approach)
- [Dependencies](#dependencies)
- [Phase 1: Command Structure Setup](#phase-1-command-structure-setup)
- [Phase 2: Review Agent Implementation](#phase-2-review-agent-implementation)
- [Phase 3: Review Output Generation](#phase-3-review-output-generation)
- [Phase 4: Testing and Documentation](#phase-4-testing-and-documentation)
- [Testing Strategy](#testing-strategy)
- [References](#references)

## Overview

Create a `review_plan` command that analyzes existing implementation plans for quality, completeness, and executability. The command will spawn a specialized subagent to:

1. Read and parse existing implementation plans
2. Analyze plans for accuracy, inconsistencies, clarity, completeness, and potential bugs
3. Rate the probability that agents can successfully execute the plan without ambiguity
4. Generate a detailed review document with findings, suggestions, and pain points
5. Save the review as a markdown file in the same directory as the original plan
6. **Never** implement improvements without explicit user permission

This complements the existing `create_plan` command by providing quality assurance and validation before execution.

## Current State Analysis

### Existing Infrastructure

We have a `create_plan` command at `.claude/commands/create_plan.md` that:
- Uses opus model with 10k thinking tokens
- Spawns specialized research agents (codebase-locator, codebase-analyzer, etc.)
- Creates detailed implementation plans in `plan/` directory
- Follows a structured template with phases, dependencies, and success criteria
- Supports both single-file and multi-file (directory) plan formats

### Key Discoveries

1. **Command Structure** (`.claude/commands/create_plan.md`):
   - Uses frontmatter for configuration (model, description, thinking settings)
   - Implements an interactive, iterative process
   - Heavy use of Task tool to spawn specialized agents
   - Saves plans to `plan/YYYY-MM-DD-<feature-name>.md` or `plan/YYYY-MM-DD-<feature-name>/`

2. **Plan Format** (from existing plans):
   - Structured with table of contents, overview, phases
   - Each phase has: Overview, Context, Dependencies, Changes Required, Success Criteria
   - Success criteria split into Automated vs Manual verification
   - Clear dependency graphs showing execution order and parallelization

3. **Available Agent Types** (from Task tool):
   - `codebase-analyzer` - Analyzes implementation details
   - `codebase-pattern-finder` - Finds similar implementations
   - `thoughts-analyzer` - Deep dive on research topics
   - `general-purpose` - Multi-step complex tasks

### What's Missing

No command currently exists to:
- Review and validate existing plans before execution
- Assess plan quality, completeness, and executability
- Identify potential blockers or ambiguities
- Provide structured feedback on plan improvements

## Desired End State

A `/review_plan` command that works as follows:

### User Invocation

```bash
# Review a specific plan file
/review_plan plan/2026-01-23-feature-name.md

# Review a multi-file plan (directory)
/review_plan plan/2026-01-23-feature-name/

# Interactive mode (prompts for plan path)
/review_plan
```

### Review Process

1. **Plan Loading**: Reads the specified plan file(s) completely
2. **Agent Spawning**: Creates a specialized review agent with clear context
3. **Analysis**: Agent analyzes plan across multiple dimensions:
   - **Accuracy**: Technical correctness, correct file paths, valid code patterns
   - **Consistency**: Internal consistency across phases, naming conventions
   - **Clarity**: Clear instructions, unambiguous language, well-defined success criteria
   - **Completeness**: All necessary steps included, no missing context
   - **Executability**: Can agents execute this without human intervention?
   - **Dependencies**: Dependency graph is correct and complete
   - **Testing**: Adequate test coverage and verification steps
4. **Scoring**: Provides an executability probability (0-100%)
5. **Report Generation**: Creates a review markdown file with:
   - Executive summary with executability score
   - Detailed findings by category
   - Specific line/section references to issues
   - Actionable suggestions for improvement
   - Identified pain points and blockers

### Output Location

Review saved to same directory as original plan:
- Single-file plan: `plan/future-plans/YYYY-MM-DD-feature-name.md` → `plan/future-plans/YYYY-MM-DD-feature-name.REVIEW.md`
- Multi-file plan: `plan/future-plans/YYYY-MM-DD-feature-name/README.md` → `plan/future-plans/YYYY-MM-DD-feature-name/REVIEW.md`

### Success Criteria

**Automated Verification:**
- [ ] Command file exists at `.claude/commands/review_plan.md`
- [ ] Command can be invoked with `/review_plan`
- [ ] Command accepts file path parameter
- [ ] Review markdown is generated in correct location
- [ ] No linting errors: `uv run ruff check`
- [ ] Code formatting is correct: `uv run ruff format --check`

**Manual Verification:**
- [ ] Review agent provides accurate, helpful feedback
- [ ] Executability scores are reasonable and justified
- [ ] Suggestions are actionable and specific
- [ ] Review format is readable and well-structured
- [ ] Agent does NOT attempt to implement changes without permission
- [ ] Works with both single-file and multi-file plans

## What We're NOT Doing

**Out of Scope:**
- Automatic implementation of suggested improvements
- Integration with version control for plan tracking
- Historical analysis of past plan reviews
- Plan comparison or diff functionality
- Integration with issue trackers or project management tools
- Real-time collaboration features
- Plan versioning or rollback mechanisms
- Automated plan rewriting
- Plan execution (that's handled by separate execution commands)
- Integration with CI/CD pipelines

**Explicit Non-Goals:**
- The review agent should **never** edit the original plan file
- The review agent should **never** implement suggested changes without explicit user approval
- This command is purely analytical/advisory

## Implementation Approach

### High-Level Strategy

1. **Command Configuration**: Create a markdown command file with frontmatter similar to `create_plan`
2. **Review Agent**: Use Task tool with a specialized prompt to spawn a review subagent
3. **Analysis Framework**: Define clear criteria for evaluating plans across multiple dimensions
4. **Scoring System**: Implement a rubric for executability probability
5. **Output Template**: Define a structured markdown template for review reports
6. **Non-Destructive**: Ensure no modifications to original plan files

### Key Design Decisions

**Decision 1: Use Opus Model**
- **Rationale**: Complex analytical task requires strong reasoning
- **Trade-off**: Higher cost vs better quality reviews

**Decision 2: Single Specialized Agent**
- **Rationale**: Plan review is a cohesive task that benefits from single context
- **Alternative Considered**: Multiple agents for different review dimensions
- **Why Rejected**: Risk of inconsistent feedback, harder to generate unified report

**Decision 3: Separate Review File**
- **Rationale**: Preserves original plan, allows version control of reviews
- **Alternative Considered**: Inline comments in original plan
- **Why Rejected**: Would modify original plan, violates non-destructive requirement

**Decision 4: Naming Convention: `*.REVIEW.md`**
- **Rationale**: Clear distinction from original plans, easy to identify
- **Alternative Considered**: `*-review.md` suffix
- **Why Chosen**: More prominent, matches common convention for review artifacts

## Dependencies

**Execution Order:**

1. Phase 1 (Command Structure Setup) - no dependencies
2. Phase 2 (Review Agent Implementation) - depends on Phase 1
3. Phase 3 (Review Output Generation) - depends on Phase 2
4. Phase 4 (Testing and Documentation) - depends on Phase 3

**Dependency Graph:**

```
Phase 1 (Command Structure)
  └─> Phase 2 (Review Agent)
        └─> Phase 3 (Output Generation)
              └─> Phase 4 (Testing)
```

**Parallelization:**
- All phases must run sequentially
- No parallelization opportunities (each phase builds on previous)

---

## Phase 1: Command Structure Setup

### Overview

Create the command file structure and basic invocation logic. This establishes the entry point for the `/review_plan` command.

### Context

Before starting, read these files:
- `.claude/commands/create_plan.md` - Understand command structure and patterns
- `.claude/skills/writing-plans/SKILL.md` - Understand skill delegation pattern
- `plan/future-plans/remove-mcdonalds-voice-agent.md` - Example plan format

### Dependencies

**Depends on:** None
**Required by:** Phase 2, Phase 3, Phase 4

### Changes Required

#### 1.1: Create Command File

**File:** `.claude/commands/review_plan.md`

**Changes:**
Create a new command file with frontmatter configuration:

```markdown
---
description: Review implementation plans for quality, completeness, and executability
model: opus
thinking:
  type: enabled
  budget_tokens: 10000
---

# Plan Review

You are tasked with reviewing implementation plans to assess their quality, completeness, and executability. Your goal is to provide constructive feedback that helps improve plans before execution.

## Initial Response

When this command is invoked:

1. **Check if a plan path was provided**:
   - If a file path or directory path was provided as a parameter, immediately proceed to load it
   - If no parameter provided, ask the user for the plan location

2. **If no parameters provided**, respond with:
```
I'll help you review an implementation plan. Please provide the path to the plan:

1. Single-file plan: `plan/YYYY-MM-DD-feature-name.md`
2. Multi-file plan directory: `plan/YYYY-MM-DD-feature-name/`

Example: `/review_plan plan/2026-01-23-user-auth.md`
```

Then wait for the user's input.

## Process Steps

### Step 1: Plan Loading

1. **Identify plan type**:
   - Check if path is a directory (multi-file plan) or single file
   - For directories, start with `README.md` as the main plan file

2. **Read plan completely**:
   - Use Read tool to load the entire plan file(s)
   - For multi-file plans, read ALL phase files in the directory
   - NEVER use limit/offset - read complete files

3. **Verify plan structure**:
   - Confirm it follows expected plan template
   - Identify plan phases, dependencies, success criteria
   - Note any non-standard structure

### Step 2: Spawn Review Agent

1. **Create detailed review prompt**:
   - Include the complete plan content in the prompt
   - Provide clear review criteria (see Review Criteria below)
   - Specify output format requirements
   - Emphasize non-destructive nature (no modifications to original plan)

2. **Spawn agent using Task tool**:
   - Use subagent_type: "general-purpose"
   - Provide model: "opus" for strong analytical reasoning
   - Include complete plan content in prompt
   - Request structured review output

3. **Wait for agent completion**:
   - Agent will analyze plan across all dimensions
   - Agent will generate structured review with score
   - Agent will return review content

### Step 3: Save Review Report

1. **Determine output path**:
   - Single-file plan: `<original-path-without-ext>.REVIEW.md`
   - Multi-file plan: `<directory>/REVIEW.md`

2. **Write review file**:
   - Use Write tool to save review markdown
   - Preserve original plan files (no modifications)

3. **Present results**:
   ```
   ✅ Plan review completed!

   Original plan: plan/2026-01-23-feature-name.md
   Review saved to: plan/2026-01-23-feature-name.REVIEW.md

   Executability Score: 75/100

   Key findings:
   - [Brief summary of 2-3 main issues]

   See the full review for detailed analysis and suggestions.
   ```

## Review Criteria

The review agent should evaluate plans across these dimensions:

### 1. Accuracy (20 points)
- Technical correctness of proposed changes
- Valid file paths and code references
- Correct understanding of existing codebase
- Accurate dependency identification

### 2. Consistency (15 points)
- Internal consistency across phases
- Consistent naming conventions
- Consistent patterns and approaches
- Aligned with existing codebase conventions

### 3. Clarity (20 points)
- Clear, unambiguous instructions
- Well-defined success criteria
- Explicit rather than implicit requirements
- Minimal room for interpretation

### 4. Completeness (25 points)
- All necessary steps included
- No missing context or prerequisites
- Edge cases considered
- Migration/rollback strategies included
- Testing strategy comprehensive

### 5. Executability (20 points)
- Can agents execute without human intervention?
- Dependencies properly ordered
- Success criteria are verifiable
- Context loading is adequate
- No open questions or unresolved decisions

**Total: 100 points**

### Executability Probability Scale

- **90-100**: Excellent - Ready for execution
- **75-89**: Good - Minor clarifications needed
- **60-74**: Fair - Significant improvements recommended
- **40-59**: Poor - Major revisions required
- **0-39**: Critical - Cannot execute without major rework

## Review Report Template

The agent should generate a report following this structure:

```markdown
# Plan Review: [Plan Name]

**Review Date:** YYYY-MM-DD
**Reviewer:** Claude Code Review Agent
**Plan Location:** `path/to/plan.md`

---

## Executive Summary

**Executability Score:** XX/100 - [Excellent/Good/Fair/Poor/Critical]

**Overall Assessment:**
[2-3 paragraph summary of plan quality, readiness for execution, and major concerns]

**Recommendation:**
- [ ] Ready for execution
- [ ] Ready with minor clarifications
- [ ] Requires improvements before execution
- [ ] Requires major revisions

---

## Detailed Analysis

### 1. Accuracy (XX/20)

**Score Breakdown:**
- Technical correctness: X/5
- File path validity: X/5
- Codebase understanding: X/5
- Dependency accuracy: X/5

**Findings:**
- ✅ Strength: [Specific example with line reference]
- ⚠️ Issue: [Specific problem with line reference]
- ❌ Critical: [Blocking issue with line reference]

**Suggestions:**
1. [Actionable suggestion]
2. [Actionable suggestion]

### 2. Consistency (XX/15)

[Same structure as above]

### 3. Clarity (XX/20)

[Same structure as above]

### 4. Completeness (XX/25)

[Same structure as above]

### 5. Executability (XX/20)

[Same structure as above]

---

## Identified Pain Points

### Critical Blockers
1. [Issue that prevents execution - with section reference]
2. [Another blocker]

### Major Concerns
1. [Issue that will cause problems - with section reference]
2. [Another concern]

### Minor Issues
1. [Small improvement opportunity - with section reference]
2. [Another minor issue]

---

## Specific Recommendations

### High Priority
1. **[Recommendation Title]**
   - Location: [Section/Phase reference]
   - Issue: [What's wrong]
   - Suggestion: [How to fix it]
   - Impact: [Why this matters]

### Medium Priority
[Same structure]

### Low Priority
[Same structure]

---

## Phase-by-Phase Analysis

### Phase 1: [Phase Name]
- **Score:** XX/25
- **Readiness:** [Ready/Needs Work/Blocked]
- **Key Issues:**
  - [Issue 1 with line reference]
  - [Issue 2 with line reference]
- **Dependencies:** [Properly defined? Any issues?]
- **Success Criteria:** [Clear and verifiable? Any gaps?]

### Phase 2: [Phase Name]
[Same structure]

---

## Testing Strategy Assessment

**Coverage:** [Excellent/Good/Fair/Poor]

**Unit Testing:**
- [Assessment of unit test plan]

**Integration Testing:**
- [Assessment of integration test plan]

**Manual Testing:**
- [Assessment of manual test steps]

**Gaps:**
- [Missing test scenarios]
- [Inadequate coverage areas]

---

## Dependency Graph Validation

**Graph Correctness:** [Valid/Has Issues]

**Analysis:**
- Execution order is: [clear/unclear/incorrect]
- Parallelization opportunities are: [well-identified/missing/incorrect]
- Blocking dependencies are: [properly documented/unclear/missing]

**Issues:**
- [Circular dependencies if any]
- [Missing dependencies]
- [Incorrect dependency ordering]

---

## Summary of Changes Needed

**Before execution, address:**

1. **Critical (Must Fix):**
   - [ ] [Critical change 1]
   - [ ] [Critical change 2]

2. **Important (Should Fix):**
   - [ ] [Important change 1]
   - [ ] [Important change 2]

3. **Optional (Nice to Have):**
   - [ ] [Optional improvement 1]
   - [ ] [Optional improvement 2]

---

## Reviewer Notes

[Any additional context, observations, or considerations for the plan author]

---

**Note:** This review is advisory only. No changes have been made to the original plan. All suggestions require explicit approval before implementation.
```

## Important Guidelines

1. **Non-Destructive**:
   - NEVER modify the original plan file
   - NEVER implement suggested changes without explicit permission
   - Review is purely analytical

2. **Thorough**:
   - Read the entire plan completely
   - Reference specific sections and line numbers
   - Provide concrete examples

3. **Constructive**:
   - Focus on helping improve the plan
   - Explain WHY issues matter
   - Provide actionable suggestions

4. **Objective**:
   - Use the scoring rubric consistently
   - Be honest about issues
   - Don't inflate scores

5. **Clear**:
   - Make recommendations unambiguous
   - Prioritize issues (Critical/Major/Minor)
   - Provide specific line/section references

## Example Interaction Flow

```
User: /review_plan plan/2026-01-23-user-auth.md
Assistant: Let me review that plan for you...

[Reads plan completely]

I'm spawning a review agent to analyze this plan across all quality dimensions...

[Spawns agent, waits for completion]

✅ Plan review completed!

Original plan: plan/2026-01-23-user-auth.md
Review saved to: plan/2026-01-23-user-auth.REVIEW.md

Executability Score: 75/100 - Good

Key findings:
- Missing error handling strategy in Phase 2
- Success criteria for Phase 3 are not fully automated
- Dependency graph is clear and correct

See the full review for detailed analysis and suggestions.
```
```

**Rationale:**
- Uses opus model for strong analytical reasoning
- Includes 10k thinking tokens for complex analysis
- Defines clear review criteria and scoring rubric
- Provides structured template for consistent reviews
- Emphasizes non-destructive nature throughout

#### 1.2: Create Optional Skill File

**File:** `.claude/skills/review-plan/SKILL.md`

**Changes:**
Create a skill wrapper that delegates to the command:

```markdown
---
name: review-plan
description: Review implementation plans for quality and executability
---

# Review Plan

## When to Use

Invoke this skill when you need to:
- Review an implementation plan before execution
- Assess plan quality, completeness, and clarity
- Identify potential blockers or ambiguities in plans
- Get structured feedback on plan improvements
- Validate that a plan is ready for agent execution

## What Happens

This skill **delegates to the /review_plan command**, which provides:
- Comprehensive analysis across 5 quality dimensions
- Executability probability score (0-100%)
- Detailed findings with specific section references
- Prioritized recommendations for improvements
- Phase-by-phase analysis
- Testing strategy assessment
- Review saved to `*.REVIEW.md` file

The command will:
1. Load the specified plan file(s) completely
2. Spawn a specialized review agent with opus model
3. Analyze plan for accuracy, consistency, clarity, completeness, executability
4. Generate structured review report with scoring
5. Save review to same directory as original plan
6. **Never** modify the original plan file

## Invocation

To use this skill:

```bash
# Review a specific plan file
/review-plan plan/2026-01-23-feature-name.md

# Review a multi-file plan (directory)
/review-plan plan/2026-01-23-feature-name/

# Interactive mode (prompts for plan path)
/review-plan
```

## Output Location

Review saved to:
- Single-file plan: `plan/YYYY-MM-DD-feature-name.REVIEW.md`
- Multi-file plan: `plan/YYYY-MM-DD-feature-name/REVIEW.md`

## Review Criteria

Plans are evaluated on:
1. **Accuracy** (20 pts) - Technical correctness, valid paths, correct understanding
2. **Consistency** (15 pts) - Internal consistency, naming conventions, patterns
3. **Clarity** (20 pts) - Unambiguous instructions, clear success criteria
4. **Completeness** (25 pts) - All steps included, no missing context, edge cases
5. **Executability** (20 pts) - Can agents execute without human intervention?

## Quick Examples

```bash
# Review a plan before execution
/review-plan plan/2026-01-23-add-authentication.md

# Review a complex multi-file plan
/review-plan plan/2026-01-23-database-migration/

# Interactive review
/review-plan
```

The agent will provide detailed analysis and save a review report.
```

**Rationale:**
- Provides user-friendly entry point via skill invocation
- Follows same pattern as `writing-plans` skill
- Clearly documents what the review process does

### Success Criteria

#### Automated Verification:
- [ ] Command file exists: `ls .claude/commands/review_plan.md`
- [ ] Skill file exists: `ls .claude/skills/review-plan/SKILL.md`
- [ ] No markdown linting errors in command file
- [ ] No markdown linting errors in skill file

#### Manual Verification:
- [ ] Command can be invoked with `/review_plan`
- [ ] Skill can be invoked with `/review-plan`
- [ ] Help text is clear and helpful
- [ ] Template structure matches example plans

---

## Phase 2: Review Agent Implementation

### Overview

Implement the core review agent logic that analyzes plans and generates structured feedback. This is the heart of the review functionality.

### Context

Before starting, read these files:
- `.claude/commands/review_plan.md` - Command structure from Phase 1
- `plan/future-plans/remove-mcdonalds-voice-agent.md` - Example plan to use for testing
- Existing TASK.md documentation for Task tool usage patterns

### Dependencies

**Depends on:** Phase 1
**Required by:** Phase 3, Phase 4

### Changes Required

#### 2.1: Review Agent Prompt Engineering

**File:** `.claude/commands/review_plan.md` (update Step 2)

**Changes:**
Enhance the "Spawn Review Agent" section with a detailed prompt template:

```markdown
### Step 2: Spawn Review Agent

**Create detailed review prompt:**

Use the following prompt template when spawning the review agent:

"""
You are a specialized plan review agent. Your task is to analyze the following implementation plan for quality, completeness, and executability.

## Review Guidelines

1. **Be Thorough**: Read the entire plan carefully
2. **Be Specific**: Reference exact sections, phases, and lines
3. **Be Constructive**: Explain WHY issues matter and HOW to fix them
4. **Be Objective**: Use the scoring rubric consistently
5. **Be Clear**: Prioritize issues as Critical/Major/Minor

## Scoring Rubric

Evaluate across 5 dimensions (100 points total):

### 1. Accuracy (20 points)
- Technical correctness: 5 pts
- File path validity: 5 pts
- Codebase understanding: 5 pts
- Dependency accuracy: 5 pts

### 2. Consistency (15 points)
- Internal consistency: 5 pts
- Naming conventions: 5 pts
- Pattern adherence: 5 pts

### 3. Clarity (20 points)
- Instruction clarity: 7 pts
- Success criteria clarity: 7 pts
- Minimal ambiguity: 6 pts

### 4. Completeness (25 points)
- All steps present: 8 pts
- Context adequate: 6 pts
- Edge cases covered: 6 pts
- Testing comprehensive: 5 pts

### 5. Executability (20 points)
- Agent-executable: 8 pts
- Dependencies ordered: 6 pts
- Success criteria verifiable: 6 pts

## Plan to Review

{PLAN_CONTENT}

## Your Task

1. Analyze the plan using the rubric above
2. Calculate scores for each dimension
3. Calculate total executability score (0-100)
4. Identify critical blockers, major concerns, and minor issues
5. Provide specific, actionable recommendations
6. Generate a review report following the template structure

## Output Format

Return a complete review report in markdown format following the template provided in the command documentation. Include:
- Executive summary with overall score
- Detailed analysis for each dimension
- Identified pain points (Critical/Major/Minor)
- Specific recommendations (High/Medium/Low priority)
- Phase-by-phase analysis
- Testing strategy assessment
- Dependency graph validation
- Summary checklist of changes needed

**IMPORTANT:** Do NOT modify the original plan. This is a review only. All suggestions require explicit user approval before implementation.
"""

**Spawn agent:**

```python
# Pseudocode for agent spawning logic
review_agent = Task(
    subagent_type="general-purpose",
    model="opus",
    description="Review implementation plan",
    prompt=review_prompt_with_plan_content,
    run_in_background=False  # Wait for completion
)
```

**Wait for completion and extract review report from agent response.**
```

**Rationale:**
- Provides clear, detailed instructions to the review agent
- Explicitly defines the scoring rubric
- Sets expectations for output format
- Emphasizes non-destructive nature

#### 2.2: Plan Loading Logic

**File:** `.claude/commands/review_plan.md` (enhance Step 1)

**Changes:**
Add detailed logic for handling both single-file and multi-file plans:

```markdown
### Step 1: Plan Loading (Enhanced)

#### 1.1: Determine Plan Type

```python
# Pseudocode for plan type detection
if path.is_dir():
    plan_type = "multi-file"
    main_plan_path = path / "README.md"
    phase_files = sorted(path.glob("*.md"))
elif path.suffix == ".md":
    plan_type = "single-file"
    main_plan_path = path
else:
    error("Invalid plan path. Must be a .md file or directory.")
```

#### 1.2: Load Plan Content

**For Single-File Plans:**
```python
# Read the entire plan file
plan_content = Read(file_path=main_plan_path)
```

**For Multi-File Plans:**
```python
# Read README.md first (main plan)
readme_content = Read(file_path=main_plan_path)

# Read all phase files
phase_contents = []
for phase_file in phase_files:
    if phase_file.name != "README.md":
        content = Read(file_path=phase_file)
        phase_contents.append({
            "file": phase_file.name,
            "content": content
        })

# Combine into single plan content for review
plan_content = f"""
# Main Plan (README.md)
{readme_content}

{chr(10).join([f"# {p['file']}{chr(10)}{p['content']}" for p in phase_contents])}
"""
```

#### 1.3: Validate Plan Structure

Check that the plan contains expected sections:
- Table of Contents (for well-structured plans)
- Overview or Summary
- Phases or Steps
- Success Criteria

If critical sections are missing, note this in the review.
```

**Rationale:**
- Handles both plan formats correctly
- Combines multi-file plans into single context for review agent
- Validates basic plan structure before review

### Success Criteria

#### Automated Verification:
- [ ] Review agent prompt template is complete
- [ ] Plan loading logic handles single-file plans
- [ ] Plan loading logic handles multi-file plans
- [ ] Error handling for invalid paths

#### Manual Verification:
- [ ] Review agent receives complete plan content
- [ ] Scoring rubric is clear and comprehensive
- [ ] Multi-file plans are properly combined
- [ ] Agent instructions are unambiguous

---

## Phase 3: Review Output Generation

### Overview

Implement the logic to save review reports and present results to users. Ensures reviews are properly persisted and users receive actionable feedback.

### Context

Before starting, read these files:
- `.claude/commands/review_plan.md` - Command implementation
- Review report template from Phase 2

### Dependencies

**Depends on:** Phase 1, Phase 2
**Required by:** Phase 4

### Changes Required

#### 3.1: Output Path Determination

**File:** `.claude/commands/review_plan.md` (add to Step 3)

**Changes:**
Add logic for determining review output location:

```markdown
### Step 3: Save Review Report (Enhanced)

#### 3.1: Determine Output Path

```python
# Pseudocode for output path determination
if plan_type == "single-file":
    # Original: plan/2026-01-23-feature.md
    # Review: plan/2026-01-23-feature.REVIEW.md
    review_path = plan_path.parent / f"{plan_path.stem}.REVIEW.md"

elif plan_type == "multi-file":
    # Original: plan/2026-01-23-feature/README.md
    # Review: plan/2026-01-23-feature/REVIEW.md
    review_path = plan_path.parent / "REVIEW.md"

# Ensure parent directory exists
review_path.parent.mkdir(parents=True, exist_ok=True)
```

#### 3.2: Write Review File

```python
# Use Write tool to save review
Write(
    file_path=str(review_path),
    content=review_report
)
```

#### 3.3: Present Results to User

Generate a summary message:

```
✅ Plan review completed!

Original plan: {original_plan_path}
Review saved to: {review_path}

Executability Score: {score}/100 - {rating}

Key findings:
- {finding_1}
- {finding_2}
- {finding_3}

{recommendation_summary}

See the full review for detailed analysis and suggestions.
```

Extract key information from review report:
- Overall score and rating
- Top 3 most critical findings
- Overall recommendation (Ready/Needs Work/Major Revisions)
```

**Rationale:**
- Clear naming convention (*.REVIEW.md) for review files
- Places review in same directory as original plan for easy access
- Provides helpful summary without requiring user to open review file

#### 3.2: Review Report Template Validation

**File:** `.claude/commands/review_plan.md`

**Changes:**
Add a validation step to ensure generated reviews follow the template:

```markdown
#### 3.4: Validate Review Report Structure

Before saving, verify the review report contains:
- [ ] Executive Summary with score
- [ ] Detailed Analysis section (all 5 dimensions)
- [ ] Identified Pain Points section
- [ ] Specific Recommendations section
- [ ] Phase-by-Phase Analysis section
- [ ] Testing Strategy Assessment section
- [ ] Dependency Graph Validation section
- [ ] Summary of Changes Needed section

If any section is missing, this indicates an issue with the review agent's output. Log a warning and proceed with saving, but note the incomplete sections in the user-facing summary.
```

**Rationale:**
- Ensures consistent review output quality
- Catches potential issues with review agent
- Maintains template compliance

### Success Criteria

#### Automated Verification:
- [ ] Output path logic handles single-file plans correctly
- [ ] Output path logic handles multi-file plans correctly
- [ ] Review files are written to correct locations
- [ ] Review report structure validation works

#### Manual Verification:
- [ ] Review files are created in expected locations
- [ ] Review reports are well-formatted and readable
- [ ] User summary accurately reflects review content
- [ ] No modifications to original plan files

---

## Phase 4: Testing and Documentation

### Overview

Create comprehensive tests for the review command and update documentation. Ensures the command works reliably and users understand how to use it.

### Context

Before starting, read these files:
- `.claude/commands/review_plan.md` - Completed command implementation
- `.claude/skills/review-plan/SKILL.md` - Skill wrapper
- Existing test patterns in `tests/` directory

### Dependencies

**Depends on:** Phase 1, Phase 2, Phase 3
**Required by:** None (final phase)

### Changes Required

#### 4.1: Create Test Plan

**File:** `plan/future-plans/review-plan-command.md` (this document)

**Changes:**
Add to Testing Strategy section (see below).

#### 4.2: Manual Testing Checklist

**Manual tests to perform:**

1. **Single-File Plan Review:**
   ```bash
   /review_plan plan/future-plans/remove-mcdonalds-voice-agent.md
   ```
   - Verify review agent spawns
   - Verify review is generated
   - Verify output saved to `remove-mcdonalds-voice-agent.REVIEW.md`
   - Verify original plan unchanged

2. **Multi-File Plan Review (if available):**
   ```bash
   /review_plan plan/YYYY-MM-DD-feature-name/
   ```
   - Verify all phase files are loaded
   - Verify review combines all phases
   - Verify output saved to `REVIEW.md` in directory

3. **Interactive Mode:**
   ```bash
   /review_plan
   ```
   - Verify prompt for plan path appears
   - Enter path manually
   - Verify review completes

4. **Invalid Path Handling:**
   ```bash
   /review_plan nonexistent/path.md
   ```
   - Verify helpful error message
   - Verify no crash

5. **Review Quality:**
   - Check that scores are reasonable
   - Check that findings reference specific sections
   - Check that suggestions are actionable
   - Check that priority levels make sense

#### 4.3: Update Documentation

**File:** `README.md`

**Changes:**
Add a new section under "Development" or "Commands":

```markdown
### Plan Review Command

Review implementation plans for quality and executability before execution:

```bash
# Review a plan file
/review_plan plan/2026-01-23-feature-name.md

# Review a multi-file plan
/review_plan plan/2026-01-23-feature-name/

# Interactive mode
/review_plan
```

The review agent analyzes plans across 5 dimensions:
1. **Accuracy** - Technical correctness and validity
2. **Consistency** - Internal consistency and conventions
3. **Clarity** - Clear, unambiguous instructions
4. **Completeness** - All necessary steps and context
5. **Executability** - Can agents execute without intervention?

Output: Review saved to `*.REVIEW.md` with executability score (0-100) and detailed recommendations.

**Note:** Reviews are advisory only. No changes are made to original plans.
```

**File:** `AGENTS.md`

**Changes:**
Add under "Planning Principles" or create new "Plan Review" section:

```markdown
## Plan Review

Before executing implementation plans, use the `/review_plan` command to assess quality and executability:

```bash
/review_plan plan/YYYY-MM-DD-feature-name.md
```

The review process:
1. Analyzes plans for accuracy, consistency, clarity, completeness, executability
2. Provides executability score (0-100%)
3. Identifies critical blockers, major concerns, minor issues
4. Generates actionable recommendations with priorities
5. Saves review to `*.REVIEW.md` file

**Important:** Reviews are non-destructive. No changes are made to original plans without explicit approval.

### When to Review

- After creating a complex plan with `/create_plan`
- Before starting plan execution with `/implement_plan`
- When a plan seems ambiguous or incomplete
- Before assigning work to multiple agents
- Periodically for long-running plans

### Review Criteria

Plans should score 75+ for safe execution:
- **90-100**: Excellent - Ready for execution
- **75-89**: Good - Minor clarifications needed
- **60-74**: Fair - Improvements recommended
- **40-59**: Poor - Major revisions required
- **0-39**: Critical - Cannot execute safely
```

#### 4.4: Create Example Review

**File:** `plan/future-plans/remove-mcdonalds-voice-agent.EXAMPLE-REVIEW.md`

**Changes:**
Create a sample review output to demonstrate format and content. This serves as:
- Documentation of expected output
- Reference for users
- Validation that template is comprehensive

Use the existing `remove-mcdonalds-voice-agent.md` plan as the subject, and create a realistic review showing:
- All sections populated
- Reasonable scores
- Specific findings with references
- Actionable suggestions

### Success Criteria

#### Automated Verification:
- [ ] No markdown linting errors in documentation
- [ ] Links in documentation are valid
- [ ] Example review file is properly formatted

#### Manual Verification:
- [ ] Manual testing checklist completed
- [ ] All test scenarios pass
- [ ] Documentation is clear and helpful
- [ ] Example review is realistic and comprehensive
- [ ] Command works reliably across different plan types
- [ ] Review quality is high (scores are reasonable, suggestions are actionable)

---

## Testing Strategy

### Manual Testing

Since this is a command/agent-based feature, testing will primarily be manual:

#### Test Cases

1. **TC-1: Single-File Plan Review**
   - **Setup**: Have a single-file plan available
   - **Action**: Run `/review_plan plan/file.md`
   - **Expected**: Review generated, saved to `file.REVIEW.md`, original unchanged
   - **Validation**: Check review quality, score reasonableness, specific references

2. **TC-2: Multi-File Plan Review**
   - **Setup**: Have a multi-file plan directory
   - **Action**: Run `/review_plan plan/directory/`
   - **Expected**: All files loaded, review generated, saved to `directory/REVIEW.md`
   - **Validation**: Check that all phases were analyzed

3. **TC-3: Interactive Mode**
   - **Setup**: None
   - **Action**: Run `/review_plan` without parameters
   - **Expected**: Prompt for plan path appears, accepts input
   - **Validation**: Review completes after providing path

4. **TC-4: Invalid Path**
   - **Setup**: None
   - **Action**: Run `/review_plan invalid/path.md`
   - **Expected**: Helpful error message, no crash
   - **Validation**: Error is clear and actionable

5. **TC-5: Review Quality - Accuracy**
   - **Setup**: Create a plan with intentional errors (wrong file paths, incorrect code)
   - **Action**: Run review
   - **Expected**: Review identifies inaccuracies, scores accuracy dimension low
   - **Validation**: Findings are specific and correct

6. **TC-6: Review Quality - Completeness**
   - **Setup**: Create a plan missing success criteria or context
   - **Action**: Run review
   - **Expected**: Review identifies missing elements, scores completeness low
   - **Validation**: Suggestions include what's missing

7. **TC-7: Review Quality - Executability**
   - **Setup**: Create a plan with ambiguous instructions or open questions
   - **Action**: Run review
   - **Expected**: Review identifies ambiguities, scores executability low
   - **Validation**: Highlights specific ambiguities

8. **TC-8: Non-Destructive**
   - **Setup**: Have a plan file, note its timestamp and hash
   - **Action**: Run review
   - **Expected**: Original plan file unchanged (timestamp, hash, content identical)
   - **Validation**: `diff` shows no changes, timestamps match

9. **TC-9: Skill Invocation**
   - **Setup**: None
   - **Action**: Run `/review-plan plan/file.md` (using skill name)
   - **Expected**: Same as command invocation, delegates to `/review_plan`
   - **Validation**: Review completes successfully

10. **TC-10: Output Location**
    - **Setup**: Plans in various locations
    - **Action**: Review plans, check output paths
    - **Expected**: Reviews always in same directory as plans, correct naming
    - **Validation**: File paths match expected pattern

### Integration Testing

**Manual integration tests:**

1. **End-to-End Workflow:**
   ```bash
   # Create a plan
   /create_plan Add feature X

   # Review the plan
   /review_plan plan/YYYY-MM-DD-feature-x.md

   # Verify review identifies real issues
   ```

2. **Iterative Improvement:**
   ```bash
   # Review a plan
   /review_plan plan/file.md

   # Make manual improvements based on review

   # Review again
   /review_plan plan/file.md

   # Verify score improves
   ```

### Edge Cases

1. **Very Large Plans (>1000 lines):**
   - Verify agent can handle without context overflow
   - Verify review quality remains high

2. **Plans with Non-Standard Structure:**
   - Verify agent adapts to different formats
   - Verify agent notes structural issues

3. **Plans with External References:**
   - Verify agent handles links to other files
   - Verify agent notes when referenced files should be checked

4. **Multiple Reviews of Same Plan:**
   - Verify subsequent reviews overwrite previous reviews
   - Verify no conflicts or duplicates

### Performance Considerations

- Review should complete within 2-3 minutes for typical plans (<500 lines)
- Review should complete within 5 minutes for large plans (<1000 lines)
- Agent should not timeout or require excessive retries

## Performance Considerations

### Token Usage

- **Plan Loading**: Large plans (>1000 lines) will consume significant tokens
- **Review Agent**: Opus model with 10k thinking tokens is expensive but necessary
- **Total Cost**: Expect ~$0.50-2.00 per review depending on plan size

### Optimization Strategies

1. **Prompt Efficiency**: Review prompt should be concise yet comprehensive
2. **Selective Loading**: For very large plans, consider summarization (future enhancement)
3. **Caching**: Consider caching unchanged plans (future enhancement)

### Acceptable Performance

- Single-file review: 2-3 minutes
- Multi-file review: 3-5 minutes
- Very large plans (>1000 lines): Up to 5 minutes

## Migration Notes

Not applicable - this is a new feature with no migration concerns.

## References

- Related command: `.claude/commands/create_plan.md`
- Example plan: `plan/future-plans/remove-mcdonalds-voice-agent.md`
- Task tool documentation: (available via tool descriptions)
- Planning principles: `AGENTS.md` (Planning Principles section)

## Appendix: Review Scoring Rubric (Detailed)

### 1. Accuracy (20 points total)

#### Technical Correctness (5 points)
- 5: All technical details are correct and feasible
- 4: Minor technical inaccuracies that don't affect execution
- 3: Some technical errors that may cause issues
- 2: Significant technical problems
- 1: Major technical errors throughout
- 0: Fundamentally flawed technical approach

#### File Path Validity (5 points)
- 5: All file paths are valid and follow conventions
- 4: Most paths valid, minor naming issues
- 3: Some invalid paths or incorrect locations
- 2: Many invalid paths
- 1: Most paths invalid or incorrect
- 0: No valid file path references

#### Codebase Understanding (5 points)
- 5: Demonstrates deep understanding of existing code
- 4: Good understanding with minor gaps
- 3: Basic understanding, some misconceptions
- 2: Limited understanding, significant gaps
- 1: Poor understanding of codebase
- 0: No apparent understanding of existing code

#### Dependency Accuracy (5 points)
- 5: All dependencies correctly identified and specified
- 4: Most dependencies correct, minor omissions
- 3: Some dependency errors or omissions
- 2: Many dependencies missing or incorrect
- 1: Critical dependencies missing
- 0: No dependency analysis or all incorrect

### 2. Consistency (15 points total)

#### Internal Consistency (5 points)
- 5: Perfect consistency across all phases
- 4: Minor inconsistencies that don't affect execution
- 3: Some inconsistencies that may cause confusion
- 2: Significant inconsistencies
- 1: Major contradictions in the plan
- 0: Plan is internally contradictory

#### Naming Conventions (5 points)
- 5: All names follow consistent, clear conventions
- 4: Mostly consistent with minor variations
- 3: Some inconsistent naming
- 2: Inconsistent naming throughout
- 1: No apparent naming convention
- 0: Chaotic, confusing naming

#### Pattern Adherence (5 points)
- 5: Follows all established codebase patterns
- 4: Mostly follows patterns with minor deviations
- 3: Some pattern violations
- 2: Frequently deviates from patterns
- 1: Ignores established patterns
- 0: No consideration of existing patterns

### 3. Clarity (20 points total)

#### Instruction Clarity (7 points)
- 7: All instructions are crystal clear and unambiguous
- 5-6: Mostly clear with minor ambiguities
- 3-4: Some unclear or ambiguous instructions
- 1-2: Many unclear instructions
- 0: Instructions are unclear or missing

#### Success Criteria Clarity (7 points)
- 7: Success criteria are specific, measurable, achievable
- 5-6: Mostly clear criteria with minor gaps
- 3-4: Some vague or unmeasurable criteria
- 1-2: Criteria are unclear or too generic
- 0: No clear success criteria

#### Minimal Ambiguity (6 points)
- 6: No ambiguous statements, all explicit
- 4-5: Minor ambiguities that don't affect execution
- 2-3: Some ambiguities requiring clarification
- 1: Significant ambiguity throughout
- 0: Highly ambiguous, unclear intent

### 4. Completeness (25 points total)

#### All Steps Present (8 points)
- 8: Every necessary step is included
- 6-7: Minor steps missing but not critical
- 4-5: Some important steps missing
- 2-3: Many steps missing
- 0-1: Critical steps missing

#### Context Adequate (6 points)
- 6: All necessary context provided
- 4-5: Mostly adequate context
- 2-3: Missing some important context
- 1: Insufficient context
- 0: Little to no context

#### Edge Cases Covered (6 points)
- 6: All edge cases identified and handled
- 4-5: Most edge cases covered
- 2-3: Some edge cases missing
- 1: Few edge cases considered
- 0: No edge case handling

#### Testing Comprehensive (5 points)
- 5: Comprehensive test coverage
- 4: Good test coverage with minor gaps
- 3: Basic test coverage
- 2: Minimal testing
- 1: Inadequate testing
- 0: No testing strategy

### 5. Executability (20 points total)

#### Agent-Executable (8 points)
- 8: Agents can execute without human intervention
- 6-7: Minor clarifications may be needed
- 4-5: Some human intervention required
- 2-3: Significant human intervention needed
- 0-1: Cannot be executed by agents

#### Dependencies Ordered (6 points)
- 6: Perfect dependency ordering and graph
- 4-5: Mostly correct with minor issues
- 2-3: Some dependency issues
- 1: Dependency ordering is problematic
- 0: No clear dependency structure

#### Success Criteria Verifiable (6 points)
- 6: All criteria can be automatically verified
- 4-5: Most criteria verifiable, some manual
- 2-3: Many criteria require manual verification
- 1: Criteria are not easily verifiable
- 0: No verifiable criteria

## Appendix: Common Plan Issues Reference

### Critical Issues (Score < 40)

1. **Missing Prerequisites**: Plan assumes tools/libraries/configs exist that don't
2. **Invalid File Paths**: References non-existent directories or files
3. **Circular Dependencies**: Phase A depends on B, B depends on A
4. **No Success Criteria**: No way to verify if implementation worked
5. **Open Questions**: Unresolved decisions marked as "TBD" or "TODO"
6. **Incorrect Technical Approach**: Proposed solution won't work

### Major Issues (Score 40-74)

1. **Ambiguous Instructions**: Steps that could be interpreted multiple ways
2. **Missing Context**: Doesn't specify which files to read before starting
3. **Incomplete Dependencies**: Some dependencies listed but not all
4. **Weak Success Criteria**: Criteria are too vague or not measurable
5. **Missing Edge Cases**: Common failure scenarios not addressed
6. **Inconsistent Naming**: Variables/functions named differently across phases
7. **No Testing Strategy**: Tests mentioned but no concrete plan

### Minor Issues (Score 75-89)

1. **Missing Minor Edge Cases**: Rare scenarios not covered
2. **Could Be Clearer**: Instructions are correct but could be more explicit
3. **Success Criteria Could Be More Specific**: Criteria are present but somewhat vague
4. **Minor Inconsistencies**: Small variations in terminology or style
5. **Documentation Could Be Better**: More examples would help
6. **Context Could Be More Complete**: Could list a few more files to read

## Appendix: Review Report Examples

### Example 1: Excellent Plan (Score: 92/100)

```markdown
# Plan Review: Add User Authentication

**Review Date:** 2026-01-23
**Reviewer:** Claude Code Review Agent
**Plan Location:** `plan/2026-01-23-user-auth.md`

---

## Executive Summary

**Executability Score:** 92/100 - Excellent

**Overall Assessment:**
This is a well-structured, thorough implementation plan that demonstrates strong understanding of the codebase and follows best practices. The plan clearly defines phases, dependencies, and success criteria. Technical approach is sound with appropriate use of existing patterns. Minor improvements would make it even stronger.

**Recommendation:**
- [x] Ready for execution
- [ ] Ready with minor clarifications
- [ ] Requires improvements before execution
- [ ] Requires major revisions

---

## Detailed Analysis

### 1. Accuracy (18/20)

**Score Breakdown:**
- Technical correctness: 5/5 ✅
- File path validity: 5/5 ✅
- Codebase understanding: 4/5 ⚠️
- Dependency accuracy: 4/5 ⚠️

**Findings:**
- ✅ Technical approach is solid and uses established JWT pattern
- ✅ All file paths reference existing locations
- ⚠️ Minor: Could verify that `src/config.py` exports the expected config class
- ⚠️ Minor: Phase 2 mentions dependency on `bcrypt` but doesn't specify version

**Suggestions:**
1. Verify `src/config.py` structure before Phase 1
2. Add specific version requirement for `bcrypt` (e.g., `^4.0.0`)

[... rest of example review ...]
```

### Example 2: Poor Plan (Score: 45/100)

```markdown
# Plan Review: Refactor Database Layer

**Review Date:** 2026-01-23
**Reviewer:** Claude Code Review Agent
**Plan Location:** `plan/2026-01-23-db-refactor.md`

---

## Executive Summary

**Executability Score:** 45/100 - Poor

**Overall Assessment:**
This plan requires significant revision before execution. While it identifies the need for refactoring, it lacks crucial details including specific file changes, clear success criteria, and proper dependency management. The technical approach is mentioned but not explained. Multiple critical blockers prevent agent execution.

**Recommendation:**
- [ ] Ready for execution
- [ ] Ready with minor clarifications
- [ ] Requires improvements before execution
- [x] Requires major revisions

---

## Detailed Analysis

### 1. Accuracy (8/20)

**Score Breakdown:**
- Technical correctness: 2/5 ❌
- File path validity: 2/5 ❌
- Codebase understanding: 2/5 ❌
- Dependency accuracy: 2/5 ❌

**Findings:**
- ❌ Critical: Technical approach not clearly defined
- ❌ Critical: File paths are generic (e.g., "update database files")
- ❌ Major: Doesn't demonstrate understanding of current database structure
- ❌ Major: Dependencies listed as "various modules" without specifics

**Suggestions:**
1. Research existing database layer implementation thoroughly
2. Specify exact files that need changes
3. Explain technical approach in detail (ORM? Raw SQL? Migration strategy?)
4. List specific module dependencies

[... rest of example review showing critical issues ...]
```

---

## Implementation Checklist

- [ ] Phase 1: Command Structure Setup
  - [ ] Create `.claude/commands/review_plan.md`
  - [ ] Create `.claude/skills/review-plan/SKILL.md`
  - [ ] Test command invocation
  - [ ] Test skill invocation
- [ ] Phase 2: Review Agent Implementation
  - [ ] Enhance review agent prompt
  - [ ] Implement plan loading logic
  - [ ] Test with single-file plan
  - [ ] Test with multi-file plan
- [ ] Phase 3: Review Output Generation
  - [ ] Implement output path logic
  - [ ] Add review report validation
  - [ ] Test output file creation
  - [ ] Test user summary generation
- [ ] Phase 4: Testing and Documentation
  - [ ] Complete manual testing checklist
  - [ ] Update `README.md`
  - [ ] Update `AGENTS.md`
  - [ ] Create example review
  - [ ] Verify all documentation links

---

**Total Estimated Effort:** 4-6 hours
**Complexity:** Medium
**Risk Level:** Low (new feature, no modifications to existing code)
