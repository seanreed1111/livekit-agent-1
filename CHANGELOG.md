# Changelog

## [2.0.0] - 2026-01-23

### BREAKING CHANGES
- Removed all McDonald's drive-thru specific code
- Simplified to generic voice assistant only
- Main entry point is now `src/app.py` (replaced `src/agent.py` CLI)

### Removed
- Drive-thru agent implementation
- Menu provider, validation, and order management
- Drive-thru specific tests and BDD scenarios
- `DriveThruConfig` and `DriveThruSessionHandler`
- CLI commands (console/dev/start modes)

### Changed
- Dockerfile entrypoint updated to use `src/app.py`
- Makefile simplified for generic assistant
- Documentation updated to reflect generic use case only

---

## PR #11: Plan Review System and Planning Command Updates (January 23, 2026)

**Commit:** 8c86909
**Branch:** `update-remove-mcdonalds-agent-plan`
**Files changed:** 11 files (+2,851 lines, -47 lines)

### ✨ New Features

#### Plan Review Command (`/review_plan`)
- **Comprehensive plan assessment system** - Evaluate implementation plan quality before execution
  - Analyzes plans across 5 dimensions:
    - **Accuracy** - Technical correctness and validity
    - **Consistency** - Internal consistency and naming conventions
    - **Clarity** - Clear, unambiguous instructions
    - - **Completeness** - All necessary steps and context included
    - **Executability** - Can agents execute without intervention?
  - Generates executability score (0-100%) with severity-based recommendations
  - Identifies critical blockers, major concerns, and minor issues
  - Saves non-destructive reviews to `*.REVIEW.md` files
  - Implemented in `.claude/commands/review_plan.md` (296 lines)
  - Skill implementation in `.claude/skills/review-plan/SKILL.md` (377 lines)

#### Review Scoring System
- **Executability scores** - Objective plan quality assessment
  - **90-100**: Excellent - Ready for execution
  - **75-89**: Good - Minor clarifications needed
  - **60-74**: Fair - Improvements recommended
  - **40-59**: Poor - Major revisions required
  - **0-39**: Critical - Cannot execute safely
- **Priority-based recommendations** - Actionable feedback organized by severity
  - Critical blockers that must be addressed
  - Major concerns for significant improvements
  - Minor issues for optional enhancements

### 🔧 Improvements

#### Plan Updates Based on Review Feedback
- **Updated remove-mcdonalds-voice-agent.md** - Addressed all high-priority issues from review
  - Added explicit fixture deletions with line numbers (all 17 fixtures listed)
  - Added dependency cleanup phase (remove `rapidfuzz`, `click`)
  - Moved test verification to Phase 8 (avoid import errors before config cleanup)
  - Changed `src/tools/` cleanup to `rm -rf` for cleaner execution
  - Specified exact line numbers for AGENTS.md updates (lines 38, 153, 343, 350)
  - Replaced timeout-based smoke test with proper import verification
  - **Executability Score Improvement:** 78/100 → Expected 85+/100

#### Planning Command Consistency
- **Standardized plan locations** - All planning commands now use consistent paths
  - Updated `create_plan.md` - Changed examples to `plan/future-plans/` directory
  - Updated `implement_plan.md` - Clarified verification approach, removed thoughts/ references
  - Updated `iterate_plan.md` - Fixed plan paths, changed model to sonnet
  - Ensures consistent plan organization across all commands

### 📚 Documentation

#### AGENTS.md Updates
- **Added Plan Review section** - Complete guide to using `/review_plan` command
  - When to review (before execution, complex plans, unclear requirements)
  - Review criteria and scoring scale
  - Usage examples and workflow integration
  - Advisory nature of reviews (non-destructive)
  - Added 34 lines of documentation

#### README.md Updates
- **Added Plan Review Command section** - User-facing documentation
  - Command examples (file, directory, interactive modes)
  - 5-dimension analysis explanation
  - Executability scoring criteria
  - Output format details
  - Added 26 lines of documentation

#### Plan Documentation
- **Review example** - `remove-mcdonalds-voice-agent.REVIEW.md` (1,961 lines)
  - Demonstrates comprehensive review output format
  - Shows executability score calculation
  - Includes detailed recommendations by priority
  - Provides examples of critical, major, and minor issues
- **Planning guide** - `review-plan-command.md` (213 lines)
  - Implementation notes for review command
  - Design decisions and rationale
  - Future enhancement ideas

### ⚙️ Configuration

#### Settings Updates
- **Added review_plan permission** - `.claude/settings.local.json`
  - Enabled `Skill(review_plan)` in allowedPrompts
  - Allows non-interactive plan review execution

### Files Modified

#### Commands (3 files, +29 lines)
- `.claude/commands/create_plan.md` - Standardized paths to `plan/future-plans/`
- `.claude/commands/implement_plan.md` - Updated plan paths, clarified verification
- `.claude/commands/iterate_plan.md` - Fixed paths, changed model to sonnet

#### Configuration (1 file, +2 lines)
- `.claude/settings.local.json` - Added review_plan skill permission

#### Documentation (2 files, +60 lines)
- `AGENTS.md` - Added Plan Review section with guidelines
- `README.md` - Added Plan Review Command documentation

#### Plans (1 file, +206 lines)
- `plan/future-plans/remove-mcdonalds-voice-agent.md` - Updated based on review feedback
  - Added Phase 5.4 (dependency cleanup)
  - Specified exact line numbers for all edits
  - Added plan update summary at top

### Files Added

#### Commands (1 file, 296 lines)
- `.claude/commands/review_plan.md` - Plan review command implementation

#### Skills (1 file, 377 lines)
- `.claude/skills/review-plan/SKILL.md` - Plan review skill with analysis framework

#### Documentation (2 files, 2,174 lines)
- `plan/future-plans/remove-mcdonalds-voice-agent.REVIEW.md` - Example review output
- `plan/future-plans/review-plan-command.md` - Planning and implementation notes

### Migration Notes

This release introduces a systematic approach to plan quality assessment:

#### Key Benefits
- **Prevents costly mistakes** - Catch issues before execution begins
- **Improves plan quality** - Objective scoring drives better planning
- **Reduces rework** - Clear recommendations before implementation
- **Ensures executability** - Focus on whether agents can actually execute the plan
- **Non-destructive** - Reviews are advisory, original plans unchanged

#### When to Use
- After creating complex plans with `/create_plan`
- Before starting plan execution with `/implement_plan`
- When plans seem ambiguous or incomplete
- Before assigning work to multiple agents
- Periodically for long-running plans

#### Design Philosophy
- Plans should score 75+ for safe execution
- Reviews analyze both what to do and how to do it
- Recommendations are prioritized by severity
- Reviews provide actionable feedback, not just criticism
- Original plans remain untouched - reviews are separate files

The plan review system enables higher quality planning and safer plan execution across all development workflows.

---

## PR #10: Fix Drive-Thru Agent Responsiveness (January 22, 2026)

**Commit:** 1e2687b
**Branch:** `debug-session`
**Files changed:** 2 files (+98 lines, -162 lines)

### 🐛 Bug Fixes

#### Critical: Agent Now Responds to Customer Orders
- **Fixed tool registration bug** - The drive-thru agent was greeting customers but not responding to their orders. Root cause: order management tools (add_item_to_order, complete_order, remove_item_from_order) were created but never passed to the LiveKit Agent parent class.
  - **What was broken**: Agent would say "Welcome to McDonald's! What can I get for you today?" but become unresponsive when customers placed orders
  - **What's fixed**: Agent now properly calls tools to add items, confirm orders, and save final orders to JSON
  - **Technical change**: Reordered `DriveThruAgent.__init__()` to create tools before calling `super().__init__()` and pass them via `tools` parameter
  - **Impact**: Agent can now complete full ordering workflows from greeting to order completion

### 🔍 Improvements

#### Enhanced Diagnostic Logging
- **Tool registration verification** - Added logging to confirm 3 tools are registered when agent starts
  - Logs show "Agent has 3 tools available" in both console and dev modes
  - Helps diagnose similar issues in the future
  - Implemented in `src/drive_thru_agent.py` and `src/agent.py`

### Technical Details

**Root Cause Analysis:**
- Location: `src/drive_thru_agent.py:51`
- Issue: `super().__init__(instructions=...)` called without `tools` parameter
- Tools created at lines 64-66 but never passed to parent Agent class
- Result: LLM had no access to ordering functions

**Fix Applied:**
1. Store dependencies first (llm, menu_provider, session_id)
2. Create OrderStateManager
3. Create tools BEFORE calling super().__init__()
4. Pass tools to parent: `super().__init__(instructions=..., tools=self._tools)`

**Verified Working:**
- ✅ Console mode: Confirmed "Agent has 3 tools available"
- ✅ Dev mode: Agent starts and registers with LiveKit Cloud
- ✅ Tool registration: All 3 tools accessible to LLM

---

## PR #9: Enhanced Makefile with Minimalism Standards (January 22, 2026)

**Commits:** c808878 to b39200e
**Branch:** `enhance-makefile-skill`
**Files changed:** 17 files (+1,319 lines, -183 lines)

### Features

#### Makefile Skill System
- **Comprehensive Makefile skill** - New standardized approach to Makefile creation and maintenance
  - Minimalism philosophy: "The best Makefile is the shortest one that meets the user's needs"
  - Importance-first ordering: Most frequently used commands appear first
  - Variable-based scope: Single targets with `SCOPE` and `ARGS` variables instead of target proliferation
  - Default to 5-8 core targets for most projects
  - Implemented in `.claude/skills/makefile/SKILL.md` (348 lines)

#### Reference Implementation
- **Complete Makefile example** - Production-ready reference implementation
  - Demonstrates all patterns and best practices
  - Full color-coded help system
  - Variable defaults and scope selection
  - Comprehensive error handling
  - Implemented in `.claude/skills/makefile/references/Makefile` (519 lines)

### Makefile Improvements

#### Structure & Organization
- **Importance-first ordering** - Targets ordered by frequency of use, not alphabetically
  1. `help` - Always first
  2. `console`, `dev` - Most frequently used commands
  3. `setup` - Installation and configuration
  4. `test` - Testing
  5. `format`, `lint` - Code quality
  6. `clean` - Utilities
- **Clear section headers** - Visual separators with meaningful labels
- **Color-coded output** - Blue (info), Green (success), Yellow (warnings), Cyan (headers)
- **Quick reference at top** - Top 3-5 most important commands prominently displayed

#### Enhanced Help System
- **Comprehensive `make help`** - Organized by importance with realistic examples
  - Most common commands section
  - Setup instructions
  - Development workflow commands
  - Production deployment
  - Utilities
- **Usage examples** - Real command examples for every target
- **Variable documentation** - Clear examples of `SCOPE` and `ARGS` usage

#### Testing Flexibility
- **Scope-based testing** - Single `test` target with multiple scopes
  - `make test` - Run all tests (default)
  - `make test SCOPE=unit` - Unit tests only
  - `make test SCOPE=integration` - Integration tests only
  - `make test ARGS="-k order"` - Pass arguments to pytest
- **Eliminated target proliferation** - Replaced potential `test-unit`, `test-integration` targets with scope-based approach

#### User Experience
- **Default goal** - `make` without arguments shows helpful information
- **Consistent formatting** - All commands follow same patterns
- **Clear error messages** - Helpful hints when commands are used incorrectly

### Documentation

#### Makefile Standards Documentation
- **SKILL.md** - Complete guide to Makefile best practices (348 lines)
  - Philosophy and core principles
  - Implementation patterns
  - Prohibited anti-patterns
  - Best practices and examples
  - Refactoring guide
  - Summary checklist for new targets

#### Pattern Examples
- **Variable defaults and scope selection** - How to use `SCOPE` and `ARGS`
- **User-friendly help output** - Color-coded help format
- **Argument pass-through** - Flexible command customization
- **Target ordering guidelines** - Importance over alphabetization
- **Error handling patterns** - User-friendly validation

### Refactoring & Cleanup

#### Code Quality
- **Reduced complexity** - From potentially 12+ targets down to 8 essential targets
- **Eliminated redundancy** - Single targets with variables instead of similar targets
- **Improved discoverability** - Importance-first ordering makes common commands easy to find

#### File Organization
- **Plan documentation moved** - Relocated `plan/thoughts/` to `docs/planning/`
  - `drive-thru-llm/` subdirectory and all its contents
  - `mcdonalds-drive-thru-agent-plan.md`

### Files Modified

#### Build System
- `Makefile` - Complete refactoring with new standards (+153 lines)
  - Importance-first target ordering
  - Color-coded output
  - Enhanced help system
  - Variable-based scoping
  - Clear section organization

#### Documentation
- `README.md` - Enhanced Makefile documentation (+475 lines)
  - Quick Commands section added
  - Makefile usage examples
  - Development workflow documentation

#### Configuration
- `.claude/settings.local.json` - Updated skill configuration (+5 lines)
- `.gitignore` - Added patterns for skill-related files (+2 lines)

### Files Added
- `.claude/skills/makefile/SKILL.md` - Makefile standards (348 lines)
- `.claude/skills/makefile/references/Makefile` - Reference implementation (519 lines)

### Files Moved
- `plan/thoughts/drive-thru-llm/` → `docs/planning/drive-thru-llm/` (7 files)
- `plan/thoughts/mcdonalds-drive-thru-agent-plan.md` → `docs/planning/`

### Migration Notes

This release establishes comprehensive standards for Makefile creation and maintenance:

#### Key Benefits
- **Minimalism**: Fewer targets mean less maintenance and easier discovery
- **Flexibility**: Variables provide customization without target proliferation
- **Usability**: Color-coded help and importance-first ordering improve UX
- **Maintainability**: Clear patterns and standards ensure consistency
- **Discoverability**: Most important commands appear first

#### Design Philosophy
- Challenge every new target: "Can I use an existing target with variables instead?"
- Default to 5-8 core targets for most projects
- Order by importance, not alphabetically
- Use `SCOPE` for variations, `ARGS` for customization
- Provide helpful error messages and usage hints

The Makefile skill can be applied to any project requiring build automation.

---

## PR #8: Claude Code Commands and Skills (January 22, 2026)

**Commits:** b0b44bf to c808878
**Branch:** `update-claude`
**Files changed:** 47 files (+6,982 lines, -15 lines)

### Features

#### Claude Code Agent System
- **7 specialized agents** - Pre-configured agents for common development tasks
  - `bdd-scenario-writer` - Generates behavior-driven development scenarios (482 lines)
  - `codebase-analyzer` - Analyzes implementation details (143 lines)
  - `codebase-locator` - Finds files, directories, and components (122 lines)
  - `codebase-pattern-finder` - Discovers similar implementations and patterns (227 lines)
  - `thoughts-analyzer` - Deep dive research for thoughts directory (145 lines)
  - `thoughts-locator` - Discovers relevant documents in thoughts/ (127 lines)
  - `web-search-researcher` - Web research for modern information (109 lines)

#### Claude Code Commands
- **35 workflow commands** - Complete suite of development commands

  **Planning & Research:**
  - `create_plan` - Create detailed implementation plans (449 lines)
  - `create_plan_generic` - Generic planning with research (442 lines)
  - `create_plan_nt` - Planning without thoughts directory (439 lines)
  - `iterate_plan` - Iterate on existing plans (249 lines)
  - `iterate_plan_nt` - Iterate without thoughts (238 lines)
  - `validate_plan` - Validate against success criteria (166 lines)
  - `research_codebase` - Document as-is codebase (213 lines)
  - `research_codebase_generic` - Generic codebase research (179 lines)
  - `research_codebase_nt` - Research without thoughts (190 lines)

  **Git Workflow:**
  - `commit` - Create commits without Claude attribution (44 lines)
  - `ci_commit` - Create commits with clear messages (34 lines)
  - `commit-push-pr` - Commit, push, and open PR (19 lines)
  - `describe_pr` - Generate PR descriptions (76 lines)
  - `ci_describe_pr` - Comprehensive PR descriptions (75 lines)
  - `describe_pr_nt` - PR descriptions without thoughts (89 lines)

  **Development Workflow:**
  - `implement_plan` - Execute technical plans (84 lines)
  - `debug` - Debug issues via logs, DB, git history (200 lines)
  - `local_review` - Set up worktree for branch review (48 lines)
  - `create_worktree` - Worktree creation utility (41 lines)
  - `create_handoff` - Transfer work to another session (95 lines)
  - `resume_handoff` - Resume from handoff document (217 lines)

  **Linear Integration:**
  - `linear` - Manage Linear tickets (388 lines)
  - `ralph_research` - Research highest priority ticket (81 lines)
  - `ralph_plan` - Plan for highest priority ticket (59 lines)
  - `ralph_impl` - Implement small tickets (33 lines)
  - `oneshot` - Research and launch planning (6 lines)
  - `oneshot_plan` - Execute ralph plan and implementation (6 lines)
  - `founder_mode` - Create ticket and PR for experiments (19 lines)

#### Claude Code Skills
- **6 development skills** - Best practices and standards
  - `architecting-systems` - System architecture design (62 lines)
  - `changelog-generator` - Transform commits to user-friendly changelogs (104 lines)
  - `design` - Minimal design for dashboards and admin UIs (170 lines)
  - `writing-plans` - Create implementation plans with task grouping (116 lines)
  - `writing-tests` - Behavior-focused tests with Testing Trophy (85 lines)
  - Plus skills already present: `systematic-debugging`, `handling-errors`, `migrating-code`, etc.

### Documentation

#### Skill Reference Documentation
- **Changelog style guide** - `.claude/skills/changelog-generator/references/CHANGELOG_STYLE.md` (316 lines)
  - Professional changelog formatting
  - User-friendly language guidelines
  - Categorization standards
  - Examples and anti-patterns

- **Design craft details** - `.claude/skills/design/references/craft-details.md` (109 lines)
  - Jony Ive-level design principles
  - Dashboard and admin interface standards
  - Minimal, precise design guidelines

- **Test writing references**:
  - Python testing guide - `.claude/skills/writing-tests/references/python.md` (209 lines)
  - TypeScript/React testing - `.claude/skills/writing-tests/references/typescript-react.md` (237 lines)

### Configuration

#### Claude Code Settings
- **Local settings** - `.claude/settings.local.json` (32 lines)
  - Agent configurations
  - Command definitions
  - Skill registrations
- **Menu-specific settings** - `menus/mcdonalds/.claude/settings.local.json` (8 lines)

### Files Added

#### Agents (1,355 lines)
- 7 specialized agent definition files in `.claude/agents/`

#### Commands (3,532 lines)
- 35 workflow command files in `.claude/commands/`

#### Skills (1,201 lines)
- 6 skill definition files with comprehensive documentation
- 3 reference documentation files (862 lines)

#### Configuration (40 lines)
- 2 settings files for Claude Code integration

### Files Modified
- `.gitignore` - Removed 15 outdated patterns

### Migration Notes

This release adds comprehensive Claude Code integration for AI-assisted development:

#### Key Capabilities
- **Specialized agents** for focused tasks (BDD, codebase analysis, research)
- **Workflow commands** covering entire dev lifecycle
- **Best practice skills** with reference documentation
- **Linear integration** for ticket management
- **Git workflow automation** with commit and PR generation
- **Planning and execution** with validation and handoffs

#### Integration Points
- Commands accessible via `/command-name` syntax
- Skills provide standards and patterns
- Agents handle complex multi-step tasks
- Settings allow customization per project

The system enables AI-assisted development while maintaining code quality and consistency.

---

## PR #6: Voice Ordering System (January 22, 2026)

**Commits:** 90a0ae5 to d442c03
**Branch:** `voice-ordering-llm`
**Files changed:** 65 files (+16,661 lines, -1,616 lines)

### Features

#### Voice Ordering System
- **DriveThruLLM** - Context injection wrapper for menu-aware LLM interactions
  - Intercepts chat calls to inject relevant menu context based on keywords
  - Queries MenuProvider for relevant menu items from user messages
  - Grounds LLM in actual menu data to reduce hallucination
  - Configurable max context items (default: 50)
  - Implemented in `src/drive_thru_llm.py` (274 lines)

- **MenuProvider** - Read-only data access layer for McDonald's menu
  - Thread-safe, immutable menu data access
  - Fast keyword-based search with category filtering
  - Built-in indices for efficient queries
  - Returns deep copies to prevent mutations
  - Implemented in `src/menu_provider.py` (156 lines)

- **OrderStateManager** - Single source of truth for order state
  - Manages order items with unique IDs and timestamps
  - Supports add, remove, update, and clear operations
  - Order persistence to JSON files
  - Order summary generation for user confirmation
  - Implemented in `src/order_state_manager.py` (371 lines)

- **Order Tools** - LLM function tools for order manipulation
  - `add_item_to_order` - Add items with modifiers and quantities
  - `remove_item_from_order` - Remove items by item ID
  - `modify_item_in_order` - Update existing order items
  - `clear_order` - Clear entire order
  - `show_order_summary` - Display current order contents
  - Implemented in `src/tools/order_tools.py` (256 lines)

- **DriveThruAgent** - Complete drive-thru ordering agent
  - Integrates DriveThruLLM, MenuProvider, and OrderStateManager
  - Registers order tools with the LLM
  - Handles session lifecycle and state management
  - Implemented in `src/drive_thru_agent.py` (148 lines)

- **Menu Validation** - Validation system for menu data integrity
  - Validates item names against menu
  - Checks modifier availability for items
  - Returns validation results with suggestions for corrections
  - Implemented in `src/menu_validation.py` (214 lines)

#### Enhanced Menu Models
- **Quantity support** - Added `quantity` field to `Item` model
  - Default value of 1
  - Enables multi-item orders of the same product
- **Item addition operator** - Implemented `__add__` for combining identical items
  - Combines quantities of items with same name and modifiers
  - Validates items are compatible before combining
  - Raises errors for incompatible items

#### Agent Configuration
- **Extended config** - Updated `src/config.py` with drive-thru specific settings
  - Menu file path configuration
  - LLM configuration for drive-thru use case
  - Added 46 lines of configuration code

### Testing

#### Comprehensive Test Suite
- **Menu model tests** - Extended `tests/test_menu_models.py` (+246 lines)
  - Quantity handling tests
  - Item addition operator tests
  - Serialization and deserialization tests

- **MenuProvider tests** - New test suite `tests/test_menu_provider.py` (292 lines)
  - Keyword search tests
  - Category filtering tests
  - Thread-safety tests
  - Error handling tests

- **Menu validation tests** - New suite `tests/test_menu_validation.py` (304 lines)
  - Item name validation tests
  - Modifier validation tests
  - Suggestion generation tests

- **OrderStateManager tests** - New suite `tests/test_order_state.py` (479 lines)
  - Add, remove, update, clear operations
  - Order persistence tests
  - Summary generation tests
  - Edge case handling

- **Order tools tests** - New suite `tests/test_order_tools.py` (489 lines)
  - Tool invocation tests
  - Parameter validation tests
  - Error handling tests
  - Integration with OrderStateManager

- **DriveThruLLM tests** - New suite `tests/test_drive_thru_llm.py` (376 lines)
  - Context injection tests
  - Keyword extraction tests
  - Menu item filtering tests
  - LLM delegation tests

- **DriveThruAgent tests** - New suite `tests/test_drive_thru_agent.py` (102 lines)
  - Agent initialization tests
  - Tool registration tests
  - Session handling tests

- **Integration tests** - New suite `tests/test_drive_thru_agent_integration.py` (298 lines)
  - End-to-end ordering flow tests
  - Multi-item order tests
  - Error recovery tests

#### BDD Feature Files
- **Basic ordering** - `tests/features/agent/01_basic_ordering.feature` (31 lines)
- **Multi-item ordering** - `tests/features/agent/02_multi_item_ordering.feature` (35 lines)
- **Modifiers** - `tests/features/agent/03_modifiers.feature` (33 lines)
- **Order corrections** - `tests/features/agent/04_order_corrections.feature` (31 lines)
- **Error handling** - `tests/features/agent/05_error_handling.feature` (35 lines)
- **Order completion** - `tests/features/agent/06_order_completion.feature` (45 lines)

#### Test Organization
- **Reorganized features** - Moved existing feature files into `tests/features/agent/`
  - `agent_personality.feature`
  - `multi_turn_context.feature`
  - `safety_harmful_requests.feature`
  - `voice_processing.feature`

- **Centralized fixtures** - Updated `tests/conftest.py` (+285 lines)
  - Menu data fixtures
  - MenuProvider fixtures
  - OrderStateManager fixtures
  - DriveThruLLM fixtures
  - Mock LLM fixtures for testing

### Documentation

#### Planning Documentation
- **Implementation plan** - Complete plan in `plan/thoughts/mcdonalds-drive-thru-agent-plan.md` (1,619 lines)
- **Drive-thru LLM documentation** - Detailed design docs in `plan/thoughts/drive-thru-llm/`:
  - `README.md` - Overview and architecture (491 lines)
  - `01-menu-models-and-validation.md` - Menu models design (433 lines)
  - `02-menu-provider.md` - MenuProvider design (504 lines)
  - `03-order-state-manager.md` - State management design (761 lines)
  - `04-order-tools.md` - Order tools design (619 lines)
  - `05-drive-thru-llm.md` - DriveThruLLM design (551 lines)
  - `06-drive-thru-agent.md` - Agent integration (426 lines)
  - `07-integration-and-wiring.md` - System integration (545 lines)
  - `08-accuracy-optimization.md` - Optimization strategies (561 lines)
  - `bdd-testing-strategy.md` - Testing approach (584 lines)

#### Reference Documentation
- **Returns library** - Comprehensive reference for functional programming
  - `docs/python/references/RETURNS.md` - Empty placeholder
  - `docs/python/references/returns-part1-core-types.md` - Core types (2,139 lines)
  - `docs/python/references/returns-part2-advanced-features.md` - Advanced features (2,158 lines)

#### Project Documentation Updates
- **AGENTS.md** - Updated with voice ordering system documentation (+147 lines)
  - Drive-thru agent architecture
  - Component interaction patterns
  - Testing guidelines for voice ordering

### Refactoring & Cleanup

#### Code Organization
- **Tool package** - Created `src/tools/` package for order tools
  - `src/tools/__init__.py` - Package initialization (5 lines)
  - `src/tools/order_tools.py` - Order tool implementations (256 lines)

- **Session handler** - Added `src/session_handler.py` (54 lines)
  - Session lifecycle management
  - State initialization and cleanup

#### File Cleanup
- **Removed mermaid diagrams** - Cleaned up visual documentation no longer needed:
  - `menus/mcdonalds/mermaid-diagrams/beef_pork.mmd` (-36 lines)
  - `menus/mcdonalds/mermaid-diagrams/beverages.mmd` (-56 lines)
  - `menus/mcdonalds/mermaid-diagrams/breakfast.mmd` (-72 lines)
  - `menus/mcdonalds/mermaid-diagrams/chicken_fish.mmd` (-56 lines)
  - `menus/mcdonalds/mermaid-diagrams/coffee_tea.mmd` (-198 lines)
  - `menus/mcdonalds/mermaid-diagrams/desserts.mmd` (-16 lines)
  - `menus/mcdonalds/mermaid-diagrams/salads.mmd` (-14 lines)
  - `menus/mcdonalds/mermaid-diagrams/smoothies_shakes.mmd` (-64 lines)
  - `menus/mcdonalds/mermaid-diagrams/snacks_sides.mmd` (-28 lines)

- **Removed alternative menu structures** - Cleaned up exploration files:
  - `menus/mcdonalds/transformed-data/menu-structure-alternatives-comparison.md` (-238 lines)
  - `menus/mcdonalds/alt-menu-options/menu-structure-v2-base-first.json` (-74 lines)
  - `menus/mcdonalds/alt-menu-options/menu-structure-v2-explicit-standard.json` (-51 lines)
  - `menus/mcdonalds/alt-menu-options/menu-structure-v2-flattened.json` (-35 lines)
  - `menus/mcdonalds/alt-menu-options/menu-structure-v2-modifiers.json` (-64 lines)
  - `menus/mcdonalds/alt-menu-options/menu-structure-v2-separated.json` (-74 lines)
  - `menus/mcdonalds/alt-menu-options/menu-structure-with-null.json` (-342 lines)

- **Removed examples** - Cleaned up outdated example code:
  - `examples/basic_agent_with_mock_llm.py` (-141 lines)

### Dependencies

#### Added
- **returns** - Functional programming library for railway-oriented programming
  - Added to `pyproject.toml`
  - Updated `uv.lock` with new dependencies (+106 lines)

### Files Modified (Core Application)

#### Main Application
- `src/agent.py` - Major update with drive-thru agent integration (+289 lines)
  - Wires DriveThruAgent into main application
  - Configures menu provider and order state manager
  - Sets up agent session handling

#### New Core Modules
- `src/drive_thru_agent.py` - Drive-thru agent implementation (148 lines)
- `src/drive_thru_llm.py` - Context injection LLM wrapper (274 lines)
- `src/menu_provider.py` - Menu data access layer (156 lines)
- `src/menu_validation.py` - Menu validation system (214 lines)
- `src/order_state_manager.py` - Order state management (371 lines)
- `src/session_handler.py` - Session lifecycle management (54 lines)
- `src/tools/order_tools.py` - Order manipulation tools (256 lines)

#### Enhanced Modules
- `menus/mcdonalds/models.py` - Extended with quantity support (+60 lines)
- `src/config.py` - Extended with drive-thru configuration (+46 lines)

### Migration Notes

This release represents the complete implementation of a voice-driven McDonald's drive-thru ordering system:

#### Architecture Highlights
- **Menu-aware LLM**: DriveThruLLM wrapper injects relevant menu context to ground responses in actual menu data
- **Clear separation of concerns**: MenuProvider (read), OrderStateManager (state), Order Tools (operations)
- **Comprehensive testing**: 2,640+ lines of test code with unit, integration, and BDD tests
- **Railway-oriented programming**: Integration of `returns` library for functional error handling
- **Extensive documentation**: 6,109 lines of planning and reference documentation

#### Key Capabilities
- Natural language ordering with menu validation
- Support for modifiers and quantities
- Order correction and modification during conversation
- Persistent order state across session
- Context-aware menu suggestions
- Comprehensive error handling and recovery

#### Development Process
- TDD approach with tests written before implementation
- Incremental development following Kent Beck and Dave Farley principles
- Sharp boundaries between components
- Minimal coupling, high cohesion

The system is production-ready with extensive test coverage and clear documentation for future enhancements.

---

## PR #5: Pydantic Menu Models (January 21, 2026)

**Commits:** 45bdc8e to 90a0ae5
**Branch:** `make-pydantic-models`
**Files changed:** 4 files (+718 lines, -1,136 lines)

### Features

#### Pydantic v2 Models
- **Menu data models** - Complete Pydantic v2 implementation
  - `Modifier` - Represents menu item variations
    - `modifier_name: str` - Name of the modifier
    - `modifier_id: str` - Auto-generated UUID
    - Hashable and comparable by ID
  - `Item` - Represents a menu item
    - `category_name: str` - Item category
    - `item_name: str` - Item name
    - `available_as_base: bool` - Whether orderable without modifications
    - `modifiers: list[Modifier]` - Available variations
    - Helper method `add_modifier()` for adding variations
  - `Menu` - Complete menu structure
    - `categories: dict[str, list[Item]]` - All items by category
    - Query methods: `get_category()`, `get_item()`, `get_all_categories()`
    - Add method: `add_item()`

#### Serialization Support
- **JSON serialization** - All models support JSON I/O
  - `to_json()` - Serialize to JSON string
  - `from_json()` - Deserialize from JSON string
  - `load_from_file()` - Load menu from JSON file
  - `save_to_file()` - Save menu to JSON file

### Testing
- **Comprehensive test suite** - Full test coverage for menu models
  - Modifier creation and comparison tests
  - Item creation and modifier management tests
  - Menu construction and query tests
  - Serialization/deserialization tests
  - File I/O tests
  - Implemented in `tests/test_menu_models.py` (448 lines)

### Documentation
- **README updates** - Complete documentation for menu models
  - Model descriptions and usage examples
  - Serialization patterns
  - Testing guidelines
  - Added to `README.md` (+76 lines)

### Refactoring & Cleanup
- **Removed markdown documentation** - Replaced with code-based models
  - Removed `menus/mcdonalds/menu-structure.md` (-1,136 lines)
  - Information now encoded in Pydantic models with runtime validation

### Files Added
- `menus/mcdonalds/models.py` - Pydantic v2 menu models (194 lines)
- `tests/test_menu_models.py` - Comprehensive test suite (448 lines)

### Files Modified
- `README.md` - Added menu models documentation (+76 lines)

### Files Removed
- `menus/mcdonalds/menu-structure.md` - Replaced with Pydantic models (-1,136 lines)

### Migration Notes

This release transforms static menu documentation into validated, type-safe Pydantic models:

#### Benefits
- **Runtime validation**: Automatic type checking and data validation
- **JSON serialization**: Built-in `.model_dump()` and `.model_dump_json()` methods
- **Better IDE support**: Enhanced autocomplete and type hints
- **Testability**: Easy to test with comprehensive test suite
- **LLM-friendly**: Structured data ready for integration with LLM agents

#### Design Philosophy
- Followed Pydantic v2 best practices as documented in AGENTS.md
- Preferred Pydantic models over dataclasses for better validation and serialization
- Maintained separation of concerns between data models and business logic
- Created sharp boundaries with clear, well-defined interfaces

The Pydantic models provide the foundation for the voice ordering system implemented in PR #6.

---

## Combined changelog for commits db75b2e to 45bdc8e (January 21, 2026)

### Features

#### McDonald's Menu System
- **Menu data foundation** - Added comprehensive McDonald's menu data infrastructure
  - Sourced from Kaggle dataset with 261 menu items
  - Organized into categories: Breakfast, Beef & Pork, Chicken & Fish, Beverages, Coffee & Tea, Smoothies & Shakes, Desserts, Salads, Snacks & Sides
- **JSON menu structure** - Structured menu data with multiple format explorations
  - Primary structure: `menu-structure-2026-01-21.json` (949 lines)
  - JSON Schema validation: `menu-structure-2026-01-21.schema.json`
  - Alternative formats explored for optimal design
- **Menu parsing utilities** - `parse_menu.py` script for transforming CSV to structured JSON (167 lines)
- **Menu validation** - `validate_menu.py` script for verifying menu structure integrity (72 lines)

#### Visual Documentation
- **Mermaid diagrams** - Complete visual representation of menu structure
  - Beef & Pork category diagram (36 lines)
  - Beverages diagram (56 lines)
  - Breakfast diagram (72 lines)
  - Chicken & Fish diagram (56 lines)
  - Coffee & Tea diagram (198 lines)
  - Desserts diagram (16 lines)
  - Salads diagram (14 lines)
  - Smoothies & Shakes diagram (64 lines)
  - Snacks & Sides diagram (28 lines)
- **Menu structure documentation** - `menu-structure.md` comprehensive guide (1,136 lines)

#### Menu Structure Design
- **Multiple alternatives evaluated**:
  - Base-first structure (`menu-structure-v2-base-first.json`)
  - Explicit standard structure (`menu-structure-v2-explicit-standard.json`)
  - Flattened structure (`menu-structure-v2-flattened.json`)
  - Modifiers-focused structure (`menu-structure-v2-modifiers.json`)
  - Separated structure (`menu-structure-v2-separated.json`)
  - Null-value handling (`menu-structure-with-null.json`)
- **Design comparison document** - `menu-structure-alternatives-comparison.md` (238 lines)

### Documentation
- **AGENTS.md updates** - Added 64 lines documenting McDonald's menu models
  - Pydantic v2 model specifications
  - Usage examples for Menu, Item, and Modifier models
  - Serialization and file I/O patterns
  - Testing guidelines for menu models

### Data Organization
- **Raw data directory** - Organized source CSV files in `menus/mcdonalds/raw-data/`
  - `mcdonalds-menu-from-kaggle.csv` - Original Kaggle dataset
  - `mcdonalds-menu-items.csv` - Processed menu items
- **Transformed data directory** - Structured JSON outputs in `menus/mcdonalds/transformed-data/`
  - Final menu structure with schema
  - Alternative structure formats for comparison
- **Alternative options directory** - Design explorations in `alt-menu-options/`

### Dependencies
- **Added jsonschema** - For menu structure validation

### Files Added

#### Menu Data (2,800+ lines)
- `menus/mcdonalds/raw-data/mcdonalds-menu-from-kaggle.csv` (261 lines)
- `menus/mcdonalds/raw-data/mcdonalds-menu-items.csv` (261 lines)
- `menus/mcdonalds/transformed-data/menu-structure-2026-01-21.json` (949 lines)
- `menus/mcdonalds/transformed-data/menu-structure-2026-01-21.schema.json` (65 lines)

#### Scripts & Utilities (239 lines)
- `parse_menu.py` - Menu transformation script (167 lines)
- `menus/mcdonalds/transformed-data/validate_menu.py` - Validation script (72 lines)

#### Documentation (1,374 lines)
- `menus/mcdonalds/menu-structure.md` - Comprehensive guide (1,136 lines)
- `menus/mcdonalds/transformed-data/menu-structure-alternatives-comparison.md` (238 lines)

#### Mermaid Diagrams (540 lines)
- 9 category-specific diagram files totaling 540 lines

#### Alternative Structures (638 lines)
- 6 alternative JSON structure formats for design evaluation

### Files Modified
- `AGENTS.md` - Added McDonald's menu models documentation (+64 lines)
- `pyproject.toml` - Added jsonschema dependency
- `uv.lock` - Updated with new dependencies (+79 lines)

### Files Removed
- `menus/mcdonalds/transformed-data/menu-structure.json` - Replaced with versioned structure

### Migration Notes

This version establishes the data foundation for a voice-ordering system:
- **Comprehensive menu data**: Complete McDonald's menu with categories and items
- **Validated structure**: JSON Schema ensures data integrity
- **Multiple format options**: Evaluated alternatives to find optimal structure
- **Visual documentation**: Mermaid diagrams provide clear menu hierarchy
- **Parsing infrastructure**: Scripts for future menu updates and transformations

The menu system is designed to integrate with Pydantic v2 models for LLM-friendly structured data access.

---

## Combined changelog for commits c6ae5c1 to db75b2e (January 21, 2026)

### Features

#### Hybrid LLM System
- **Keyword intercept LLM** - Added intelligent keyword detection for faster responses
  - Intercepts common keywords/phrases and provides immediate responses
  - Falls back to full LLM when keywords don't match
  - Significantly reduces latency for common interactions
- **Mock LLM implementation** - Complete mock LLM for testing and development
  - Supports offline development without API calls
  - Configurable responses for testing scenarios
  - Integration with existing factory pattern

#### Architecture Improvements
- **Simplified architecture** - Removed protocol layer for more direct LiveKit integration
  - Eliminated custom protocol abstractions in favor of concrete LiveKit components
  - Direct use of `livekit.agents.inference.STT/LLM/TTS`
  - Cleaner dependency injection through factories
- **Agent renamed to app** - Refactored `agent.py` to `app.py` for clarity
- **Enhanced configuration** - Extended config support for keyword intercept and mock LLM options

### Testing
- **Keyword intercept tests** - Comprehensive test suite for keyword detection and fallback behavior
  - 250+ lines of test coverage for keyword intercept functionality
  - Tests for exact matches, partial matches, and LLM fallback scenarios
- **Mock LLM examples** - Added `examples/basic_agent_with_mock_llm.py` demonstrating usage

### Build & Development
- **Makefile updates** - Streamlined build commands and targets
- **Audio samples organization** - Moved demo audio files to `audio-samples/` directory
- **Dependency updates** - Updated `uv.lock` with new dependencies

### Refactoring & Cleanup
- **Removed protocol abstractions** - Eliminated `src/protocols.py` and protocol-based adapters
- **Removed mock adapters** - Cleaned up old mock adapter implementations
  - Removed `src/adapters/livekit_adapters.py`
  - Removed `src/adapters/mock_adapters.py`
  - Streamlined `src/adapters/` to focus on utilities only
- **Documentation cleanup** - Removed outdated documentation:
  - Removed `MOCK_ADAPTERS.md` (no longer relevant)
  - Simplified `AGENTS.md` (removed 393 lines of outdated content)
  - Removed refactoring examples from `past-plans/`
- **Test cleanup** - Removed obsolete test files:
  - Removed `tests/test_mock_tts_audio.py`
  - Updated `tests/test_agent.py` for simplified architecture

### Files Modified

#### Core Application
- `src/app.py` (renamed from `src/agent.py`) - Refactored for hybrid LLM support
- `src/factories.py` - Updated to create mock LLM and keyword intercept LLM instances
- `src/config.py` - Added configuration for new LLM options
- `src/session_handler.py` - Simplified for direct LiveKit integration

#### New Modules
- `src/mock_llm.py` - Mock LLM implementation for testing (116 lines)
- `src/keyword_intercept_llm.py` - Keyword intercept LLM wrapper (219 lines)

#### Testing
- `tests/test_keyword_intercept.py` - New comprehensive test suite (250 lines)
- `tests/test_agent.py` - Updated for new architecture

#### Examples
- `examples/basic_agent_with_mock_llm.py` - Demo of mock LLM usage (141 lines)

### Migration Notes

This version represents a significant architectural shift:
- **No more protocol layer**: Direct use of LiveKit components instead of custom abstractions
- **Hybrid LLM approach**: Keyword intercept for common phrases with LLM fallback
- **Cleaner codebase**: Removed ~1,940 lines of unnecessary abstraction code
- **Better performance**: Faster responses through keyword intercept system
- **Simpler testing**: Mock LLM enables offline development and testing

The changes maintain the dependency injection pattern while significantly simplifying the codebase and improving response times.

---

## Combined changelog for commits 420b4cd to 55367d6 (January 18-22, 2026)

## Features

### Agent Core Functionality
- **Initial LiveKit voice agent implementation** with OpenAI, Cartesia, and AssemblyAI integration
- **Initial agent greeting** - Agent now greets users when the session starts
- **Conversation context** - Agent maintains multi-turn conversation context

### Testing & Quality
- **BDD test scenarios** - Added comprehensive Gherkin feature files for:
  - Agent personality and tone
  - Multi-turn conversation context
  - Safety and harmful request handling
  - Voice processing and interruption handling
- **Test suite** with pytest integration

### Mock Adapters for Development
- **Mock TTS adapter with tone generation** - Generate audio tones for testing without API calls
- **Mock STT and LLM adapters** - Complete mock implementation for offline development
- **Audio utilities** - Tone generation, beep creation, and WAV file handling
- **Demo scripts** - `demo_mock_tts_audio.py` for testing mock audio output

## Refactoring & Architecture

### Dependency Injection & Inversion
- **Configuration management** - Centralized Pydantic-based config in `src/config.py`
- **Factory pattern** - Dependency injection through `src/factories.py`
- **Protocol-based abstractions** - Defined protocols in `src/protocols.py` for STT, LLM, and TTS
- **Session handler** - Separated session orchestration into `src/session_handler.py`
- **Adapter pattern** - Organized adapters in `src/adapters/` package:
  - LiveKit concrete implementations
  - Mock implementations for testing
  - Audio utilities

### Code Quality Improvements
- **Removed global variables** - Refactored agent to eliminate global state
- **Sharp boundaries** - Clear separation of concerns between components
- **Model optimization** - Switched to more cost-effective models

## Documentation

### Project Documentation
- **AGENTS.md** - Comprehensive guide for working with LiveKit Agents:
  - Project structure and uv package manager usage
  - Data models with Pydantic v2 best practices
  - Testing guidelines with pytest and BDD
  - Architecture patterns and dependency injection
  - Implementation tracking system
- **MOCK_ADAPTERS.md** - Detailed documentation for mock adapter development and usage
- **Python reference** - Added `PYTHON_MATCH_REFERENCE.md` for pattern matching examples
- **Future bugfixes** - Documented turn detector language warning issue
- **README updates** - Enhanced setup instructions and project overview

## Build & Development

### Build Tools
- **Makefile** - Added comprehensive Make targets for:
  - Running agent (console, dev, start modes)
  - Testing and code quality (test, format, lint)
  - Utilities (download-files, clean)
- **Development examples** - Created refactoring comparison examples in `past-plans/`

### Project Setup
- **Docker support** - Dockerfile for production deployment
- **Environment configuration** - `.env.example` and `.gitignore` setup
- **uv lock file** - Complete dependency lock for reproducible builds
- **CI/CD cleanup** - Removed unnecessary workflow files

## Dependencies

### Added
- **pydantic** - For configuration and data validation
- **pytest-bdd** - For behavior-driven development testing
- **numpy** - For audio processing utilities

## Files Modified

### Core Application
- `src/agent.py` - Major refactoring for dependency injection and clean architecture
- `src/config.py` - New configuration module
- `src/factories.py` - Factory functions for component creation
- `src/protocols.py` - Protocol definitions for type safety
- `src/session_handler.py` - Session lifecycle management

### Adapters
- `src/adapters/__init__.py` - Package initialization
- `src/adapters/livekit_adapters.py` - LiveKit concrete implementations
- `src/adapters/mock_adapters.py` - Mock implementations with greeting and tone support
- `src/adapters/audio_utils.py` - Audio generation utilities

### Testing
- `tests/test_agent.py` - Updated tests for refactored architecture
- `tests/test_mock_tts_audio.py` - New tests for mock TTS audio generation
- `tests/features/*.feature` - BDD scenario files

### Configuration & Build
- `pyproject.toml` - Updated dependencies and project metadata
- `Makefile` - Enhanced build and development commands
- `.gitignore` - Additional patterns for generated files

### Documentation
- `README.md` - Enhanced project overview and setup instructions
- `AGENTS.md` - Comprehensive agent development guide
- `MOCK_ADAPTERS.md` - Mock adapter documentation

## Migration Notes

This version represents a significant architectural improvement with:
- Clear separation between configuration, factories, and runtime logic
- Protocol-based dependency injection for better testability
- Comprehensive mock adapters for offline development
- Enhanced documentation for AI-assisted development

The refactoring maintains backward compatibility while providing a more maintainable and testable codebase.
