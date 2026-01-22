# Changelog

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
