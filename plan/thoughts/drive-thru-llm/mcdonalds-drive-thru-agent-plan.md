# McDonald's Drive-Thru Order Taker Agent - Implementation Plan

**Created**: 2026-01-21
**Status**: Planning Phase
**Goal**: Create a high-accuracy voice AI agent for taking McDonald's drive-thru orders

---

## Executive Summary

This plan outlines the implementation of a custom voice AI agent that acts as a McDonald's drive-thru order taker. The agent must accurately capture customer orders from the 212-item menu across 9 categories, maintain order state, and generate structured output files. The primary focus is on **maximizing accuracy** through multiple complementary strategies.

---

## 0. Clean Architecture Principles (Kent Beck + Dave Farley)

This implementation follows clean architecture principles for maintainability, testability, and continuous delivery.

### Core Principles Checklist

**✓ Single Responsibility Principle (SRP)**
- Each component has one reason to change
- DriveThruLLM: Context injection only (no state)
- OrderStateManager: State + persistence only
- MenuProvider: Read-only data access only
- menu_validation.py: Pure validation functions only

**✓ Dependency Inversion**
- Components receive dependencies via constructor (DI)
- High-level components don't depend on low-level details
- Easy to mock, easy to test, easy to swap

**✓ Pure Functions Where Possible**
- menu_validation.py: 100% pure functions
- No I/O, no side effects, fully deterministic
- Fast, testable, reusable

**✓ Immutability Reduces Bugs**
- MenuProvider returns immutable data
- Menu cannot be accidentally corrupted
- Thread-safe by design

**✓ Single Source of Truth**
- OrderStateManager is ONLY owner of order state
- All mutations flow through one place
- Easy to debug, easy to audit, easy to test

**✓ Tell, Don't Ask**
- Tools tell OrderStateManager what to do
- Don't query state, mutate it, then write back
- Reduces coupling, increases cohesion

**✓ Test Pyramid**
- Many fast unit tests (milliseconds)
- Some integration tests (seconds)
- Few E2E tests (minutes)
- Fast feedback loops enable TDD

**✓ Make Invalid States Unrepresentable**
- Use type system + schemas to prevent errors
- Function calling enforces structure
- Validation happens before state mutation

### Boundary Rules

| Component | Can Access | Cannot Access |
|-----------|-----------|---------------|
| `menu_validation.py` | Menu data (parameter) | Nothing (pure functions) |
| `MenuProvider` | Menu JSON file | Order state, LLM |
| `OrderStateManager` | Order state, file I/O | Menu data, LLM, validation logic |
| `OrderTools` | OrderStateManager, MenuProvider, menu_validation | LLM internals |
| `DriveThruLLM` | MenuProvider, wrapped LLM | Order state, validation |
| `DriveThruAgent` | Everything (orchestrator) | N/A |

**Dependency Flow** (always downward, never circular):
```
DriveThruAgent
    ├─> OrderStateManager
    ├─> MenuProvider
    ├─> OrderTools
    │       ├─> menu_validation.py
    │       ├─> OrderStateManager
    │       └─> MenuProvider
    └─> DriveThruLLM
            └─> MenuProvider
```

### Testing Strategy

**Unit Tests** (Fast, isolated, many)
- `test_menu_validation.py`: Pure functions, no mocks needed
- `test_menu_provider.py`: Test with fixture JSON
- `test_order_state.py`: In-memory state, temp file I/O
- `test_drive_thru_llm.py`: Mock wrapped LLM

**Integration Tests** (Medium speed, some mocks)
- `test_order_tools.py`: Real MenuProvider, mock OrderStateManager

**E2E Tests** (Slow, real components, few)
- `test_drive_thru_agent.py`: Full agent with judge-based evaluation
- `test_accuracy.py`: Accuracy benchmarks

**Goal**: Unit tests run in <1 second total, enabling rapid TDD cycles.

---

## 1. System Architecture

### 1.1 Core Components & Data Flow

```
Customer Voice Input
    ↓
[STT] → AssemblyAI Universal Streaming
    ↓
[AgentSession with DriveThruLLM wrapper]
    │
    ├─> DriveThruLLM.chat()
    │   ├─ Queries MenuProvider for context
    │   ├─ Injects menu context into chat_ctx
    │   └─ Delegates to Base LLM (OpenAI GPT-4.1)
    │
    ├─> Base LLM outputs function call → add_item_to_order(...)
    │
    ├─> OrderTools.add_item_to_order()
    │   ├─ Calls menu_validation.validate_item() [pure function]
    │   ├─ If valid: OrderStateManager.add_item() [state mutation]
    │   │   └─ OrderStateManager appends to incremental log
    │   └─ Returns result to LLM
    │
    └─> LLM generates response text
    ↓
[TTS] → Inworld/Cartesia
    ↓
Agent Voice Response


┌─────────────────────────────────────────────────────┐
│ Dependency Diagram (Composition, not inheritance)  │
└─────────────────────────────────────────────────────┘

VoiceAgentApp
    │
    ├─> Creates: DriveThruAgent (owns conversation)
    │        │
    │        ├─> Owns: OrderStateManager (mutable state)
    │        │
    │        ├─> Receives: MenuProvider (read-only data)
    │        │
    │        └─> Registers: OrderTools (coordination layer)
    │                  │
    │                  ├─> Uses: menu_validation.py (pure functions)
    │                  │
    │                  ├─> Calls: OrderStateManager (state mutations)
    │                  │
    │                  └─> Queries: MenuProvider (data access)
    │
    ├─> Creates: DriveThruLLM (wraps base LLM)
    │        │
    │        └─> Queries: MenuProvider (for context injection)
    │
    └─> Loads: MenuProvider (singleton, immutable)


Key Principles:
- MenuProvider: Read-only, queried by many
- OrderStateManager: Write-heavy, single owner (DriveThruAgent)
- menu_validation.py: Pure functions, no dependencies
- DriveThruLLM: Stateless wrapper, delegates to base LLM
- OrderTools: Thin coordination layer, receives dependencies
```

### 1.2 New Components to Build

Each component has a single, well-defined responsibility following the Single Responsibility Principle.

#### 1. **DriveThruLLM** (`src/drive_thru_llm.py`)
**Responsibility**: Pure LLM wrapper - context injection only
**Does**:
- Wraps a base LLM (similar to `KeywordInterceptLLM` pattern)
- Intercepts `chat()` calls to inject relevant menu context into `chat_ctx`
- Delegates to wrapped LLM
- Returns LLM stream

**Does NOT**:
- Manage order state (that's `OrderStateManager`)
- Store any state (stateless wrapper)
- Validate menu items (that's `menu_validation.py`)
- Perform searches (that's `MenuProvider`)

**Why**: Separation of concerns - LLM wrapping is orthogonal to state management

---

#### 2. **MenuProvider** (`src/menu_provider.py`)
**Responsibility**: Read-only menu data access
**Does**:
- Loads menu data from JSON using existing Pydantic models
- Provides search/query interface: `search_items(keyword)`, `get_category(name)`, `get_item(category, name)`
- Returns menu data structures (immutable)

**Does NOT**:
- Modify menu data (read-only)
- Validate orders (that's `menu_validation.py`)
- Manage order state (that's `OrderStateManager`)
- Fuzzy match (that's `menu_validation.py`)

**Why**: Single source of truth for menu data, but purely a data provider

---

#### 3. **OrderStateManager** (`src/order_state_manager.py`)
**Responsibility**: Single source of truth for order state and persistence
**Does**:
- Owns ALL order state (items, quantities, session info)
- Provides command methods: `add_item()`, `remove_item()`, `clear_order()`, `complete_order()`
- Provides query methods: `get_items()`, `get_total_count()`, `get_order_summary()`
- Handles persistence: incremental log (append after each operation), final JSON (on complete)
- Manages session lifecycle

**Does NOT**:
- Validate menu items (that's `menu_validation.py` - validation happens before calling OrderStateManager)
- Search menu (that's `MenuProvider`)
- Make decisions (it's told what to do)

**Why**: All state changes go through one place - testable, debuggable, single source of truth

---

#### 4. **menu_validation.py** (`src/menu_validation.py`)
**Responsibility**: Pure validation and matching functions
**Does**:
- Provides pure functions: `fuzzy_match_item()`, `validate_item_exists()`, `validate_modifiers()`
- Fuzzy string matching using `rapidfuzz`
- Returns validation results (success/failure with details)

**Does NOT**:
- Store state (pure functions only)
- Load menu data (receives menu data as parameter)
- Modify orders (just validates, doesn't change state)

**Why**: Pure functions are maximally testable and reusable

---

#### 5. **OrderTools** (`src/tools/order_tools.py`)
**Responsibility**: LiveKit Tool definitions for LLM function calling
**Does**:
- Defines `add_item_to_order` tool with schema (category, item_name, modifiers, quantity)
- Defines `complete_order` tool
- Thin wrappers that orchestrate: validate → add to order state → return result
- Receives `OrderStateManager` and `MenuProvider` as dependencies

**Does NOT**:
- Own state (receives OrderStateManager)
- Implement validation logic (calls menu_validation.py)

**Why**: Tools are the interface between LLM and our system - they coordinate but don't own logic

---

#### 6. **DriveThruAgent** (`src/drive_thru_agent.py`)
**Responsibility**: Agent orchestration and configuration
**Does**:
- Defines agent instructions/persona (system prompt)
- Owns `OrderStateManager` instance (via composition)
- Registers tools with agent (passing OrderStateManager as dependency)
- Coordinates conversation flow

**Does NOT**:
- Manage state directly (delegates to OrderStateManager)
- Validate items (delegates to validation layer via tools)
- Load menu (receives MenuProvider as dependency)

**Why**: Agent is the conductor - it orchestrates but delegates actual work

---

## 1.3 Component Contracts (Interfaces)

Following the Interface Segregation Principle, here are the explicit contracts for each component.

### MenuProvider Interface
```python
class MenuProvider:
    """Read-only menu data provider."""

    def __init__(self, menu_file_path: str) -> None:
        """Load menu from JSON file."""

    def search_items(self, keyword: str, category: str | None = None) -> list[Item]:
        """Search for items by keyword, optionally filtered by category."""

    def get_category(self, category_name: str) -> list[Item]:
        """Get all items in a category."""

    def get_item(self, category_name: str, item_name: str) -> Item | None:
        """Get a specific item by category and name."""

    def get_all_categories(self) -> list[str]:
        """Get list of all category names."""

    def get_menu(self) -> Menu:
        """Get the complete menu (immutable)."""
```

### OrderStateManager Interface
```python
@dataclass
class OrderItem:
    """A single item in an order."""
    item_name: str
    category: str
    modifiers: list[str]
    quantity: int
    item_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)


class OrderStateManager:
    """Single source of truth for order state and persistence."""

    def __init__(self, session_id: str, output_dir: str) -> None:
        """Initialize order state for a session."""

    def add_item(self, item_name: str, category: str, modifiers: list[str], quantity: int = 1) -> OrderItem:
        """Add item to order. Returns the created OrderItem. Appends to incremental log."""

    def remove_item(self, item_id: str) -> bool:
        """Remove item by ID. Returns True if found and removed."""

    def update_item_quantity(self, item_id: str, new_quantity: int) -> bool:
        """Update quantity for an item. Returns True if found and updated."""

    def get_items(self) -> list[OrderItem]:
        """Get all items in current order (read-only copy)."""

    def get_total_count(self) -> int:
        """Get total number of items (accounting for quantities)."""

    def get_order_summary(self) -> str:
        """Get human-readable order summary."""

    def complete_order(self) -> dict:
        """Mark order complete and generate final JSON. Returns final order dict."""

    def clear_order(self) -> None:
        """Clear all items (for cancellation/restart)."""
```

### menu_validation Module (Pure Functions)
```python
@dataclass
class ValidationResult:
    """Result of a validation operation."""
    is_valid: bool
    matched_item: Item | None = None
    confidence_score: float = 0.0
    error_message: str | None = None


def fuzzy_match_item(
    item_name: str,
    menu_items: list[Item],
    threshold: int = 85
) -> ValidationResult:
    """Fuzzy match an item name against menu items. Returns best match if above threshold."""


def validate_item_exists(
    item_name: str,
    category: str,
    menu_provider: MenuProvider
) -> ValidationResult:
    """Validate that an item exists in the specified category."""


def validate_modifiers(
    item: Item,
    requested_modifiers: list[str],
    fuzzy_threshold: int = 85
) -> ValidationResult:
    """Validate that all requested modifiers are available for the item."""


def validate_order_item(
    item_name: str,
    category: str,
    modifiers: list[str],
    menu_provider: MenuProvider,
    fuzzy_threshold: int = 85
) -> ValidationResult:
    """Complete validation: item exists + modifiers valid. Convenience function."""
```

### OrderTools (LiveKit Tool Definitions)
```python
def create_order_tools(
    order_state: OrderStateManager,
    menu_provider: MenuProvider,
    config: DriveThruConfig
) -> list[Tool]:
    """Create LiveKit Tool instances with dependencies injected.

    Returns:
        List of Tool objects that can be registered with an Agent
    """

    # Tool 1: add_item_to_order
    # Schema: {category: str, item_name: str, modifiers: list[str], quantity: int}
    # Behavior: validate → add to state → return confirmation

    # Tool 2: complete_order
    # Schema: {}
    # Behavior: complete order → return summary
```

### DriveThruLLM Interface
```python
class DriveThruLLM(LLM):
    """Stateless LLM wrapper that injects menu context."""

    def __init__(
        self,
        wrapped_llm: LLM,
        menu_provider: MenuProvider,
        config: DriveThruConfig
    ) -> None:
        """Initialize wrapper with dependencies."""

    def chat(
        self,
        *,
        chat_ctx: ChatContext,
        tools: list[Tool] | None = None,
        **kwargs
    ) -> LLMStream:
        """Intercept chat to inject menu context, then delegate to wrapped LLM."""
        # 1. Extract keywords from latest user message
        # 2. Query MenuProvider for relevant items
        # 3. Inject into chat_ctx as system message or augment existing prompt
        # 4. Delegate to wrapped_llm.chat()
```

### DriveThruAgent
```python
class DriveThruAgent(Agent):
    """Drive-thru order taking agent."""

    def __init__(
        self,
        order_state: OrderStateManager,
        menu_provider: MenuProvider,
        config: DriveThruConfig
    ) -> None:
        """Initialize agent with dependencies.

        - Sets instructions/persona
        - Registers order tools
        - Owns OrderStateManager
        """
```

**Design Principles Applied**:
1. **Dependency Injection**: Components receive dependencies via constructor, not by creating them
2. **Interface Segregation**: Each interface is minimal and focused
3. **Immutability**: MenuProvider returns immutable data; OrderStateManager is the only mutator
4. **Pure Functions**: `menu_validation.py` has no side effects, fully testable
5. **Tell, Don't Ask**: Tools tell OrderStateManager what to do, don't query and manipulate
6. **Single Source of Truth**: All order state lives in OrderStateManager

---

## 2. Accuracy-Boosting Strategies

### Priority 1: Core Strategies (Implement First)

#### Strategy 1: LLM Function Calling / Structured Output
**Approach**: Define tools/functions that the LLM can call to add items to the order.

**Implementation**:
- Create `add_item_to_order` function with parameters:
  - `category` (enum from menu categories)
  - `item_name` (string)
  - `modifiers` (list of strings)
  - `quantity` (int, default 1)
- LLM must use this function instead of free-form text
- Validates parameters against menu before accepting

**Pros**:
- Structured, parseable output
- Forces LLM to think in terms of menu structure
- Easy to validate

**Cons**:
- Requires LLM with good function calling support
- May feel less natural for complex orders

**Accuracy Impact**: HIGH (8/10) - Eliminates parsing errors

---

#### Strategy 2: Menu Context Injection
**Approach**: Dynamically inject relevant menu items into the LLM context based on customer utterance.

**Implementation**:
- When customer speaks, extract keywords (e.g., "burger", "breakfast", "coffee")
- Fetch relevant menu items from Menu model
- Include in system prompt: "Available items: [filtered list]"
- Reduces hallucination by showing exact menu item names

**Example**:
```
Customer: "I'd like a Big Mac"
→ Inject into context: "Beef & Pork items: Big Mac, McDouble, Quarter Pounder..."
```

**Pros**:
- Reduces hallucination
- Helps with exact item name matching
- Context-aware

**Cons**:
- Increases token usage
- May miss items if keyword matching fails

**Accuracy Impact**: HIGH (8/10) - Grounds LLM in actual menu

---

#### Strategy 3: Explicit Confirmation Loop
**Approach**: After each item is understood, explicitly confirm with customer.

**Implementation**:
- After LLM extracts an item, respond: "Got it, one Big Mac. Anything else?"
- Customer can correct if wrong
- Only write to order file after confirmation

**Example Flow**:
```
Customer: "Big Mac please"
Agent: "One Big Mac - is that correct?"
Customer: "Yes"
Agent: "Great! Anything else?"
[Write to order file]
```

**Pros**:
- Allows error correction
- Builds customer confidence
- Simple to implement

**Cons**:
- Slower ordering process
- May annoy customers with simple orders

**Accuracy Impact**: VERY HIGH (9/10) - Human-in-the-loop validation

---

#### Strategy 4: Fuzzy String Matching
**Approach**: Use fuzzy matching to handle pronunciation variations and STT errors.

**Implementation**:
- Use `rapidfuzz` or `fuzzywuzzy` library
- When LLM outputs an item name, fuzzy match against menu
- Accept if confidence > 85%
- Handle common variations:
  - "Big Mac" vs "big mac" vs "bigmac" vs "Big Mack"
  - "McNuggets" vs "chicken nuggets" vs "nuggets"

**Example**:
```python
from rapidfuzz import process, fuzz

def find_menu_item(utterance: str, menu_items: list[str]) -> tuple[str, float]:
    result = process.extractOne(utterance, menu_items, scorer=fuzz.ratio)
    return result[0], result[1]  # item, confidence_score
```

**Pros**:
- Handles STT errors
- Tolerates variations
- Fast and deterministic

**Cons**:
- Can match wrong items if names are similar
- Requires confidence threshold tuning

**Accuracy Impact**: MEDIUM-HIGH (7/10) - Catches STT errors

---

### Priority 2: Advanced Strategies (Implement Later for Optimization)

#### Strategy 5: Semantic Search with Embeddings
**Approach**: Use embeddings to find semantically similar menu items.

**Implementation**:
- Pre-compute embeddings for all menu items (OpenAI text-embedding-3-small)
- Store in vector DB or in-memory
- When customer speaks, embed their utterance
- Find nearest neighbors in embedding space
- Use as candidates for LLM to choose from

**Pros**:
- Handles synonyms ("cheeseburger" → "Quarter Pounder with Cheese")
- Semantic understanding
- Robust to paraphrasing

**Cons**:
- More complex implementation
- Requires embedding API calls
- May introduce latency

**Accuracy Impact**: HIGH (8/10) - Semantic understanding

---

#### Strategy 6: Two-Stage Parsing
**Approach**: Separate intent extraction from menu item selection.

**Implementation**:
1. **Stage 1**: Extract customer intent
   - "I want a burger with cheese"
   - Intent: {type: burger, modifiers: [cheese]}
2. **Stage 2**: Match intent to menu items
   - Search menu for burgers with cheese modifier
   - Return candidates: [Cheeseburger, Double Cheeseburger, Quarter Pounder with Cheese]
3. **Stage 3**: LLM selects best match or asks clarifying question

**Pros**:
- Cleaner separation of concerns
- Can optimize each stage separately
- Better debuggability

**Cons**:
- More complex
- Additional latency from multiple stages

**Accuracy Impact**: MEDIUM-HIGH (7/10) - Structured approach

---

#### Strategy 7: Chain-of-Thought Prompting
**Approach**: Ask LLM to explain its reasoning before outputting.

**Implementation**:
```
System: When a customer orders, think step-by-step:
1. What type of item are they requesting? (burger, drink, breakfast, etc.)
2. Which specific item from our menu matches best?
3. Did they mention any modifiers?
4. What quantity?
Then output the structured order.
```

**Pros**:
- Improves LLM reasoning
- More interpretable
- Can catch logic errors

**Cons**:
- Increases token usage
- May add latency
- Reasoning not always visible to customer

**Accuracy Impact**: MEDIUM (6/10) - Helps LLM think clearly

---

#### Strategy 8: Constrained Decoding
**Approach**: Use grammar-based constrained generation (if LLM supports it).

**Implementation**:
- Define grammar for valid responses
- LLM can only output strings that match the grammar
- Grammar includes exact menu item names

**Example Grammar**:
```
ORDER := <ITEM> | <ITEM> "and" <ORDER>
ITEM := <QUANTITY> <MENU_ITEM> <MODIFIERS>
MENU_ITEM := "Big Mac" | "Quarter Pounder" | ...
```

**Pros**:
- Guarantees valid output
- No hallucination possible
- Perfect accuracy for item names

**Cons**:
- Very few LLMs support this
- Complex to implement
- May be too rigid

**Accuracy Impact**: VERY HIGH (9/10) - If available

---

#### Strategy 9: Post-Processing Validation Layer
**Approach**: Validate every LLM output against menu before mutating order state.

**Implementation**: Pure function in `menu_validation.py`
```python
def validate_order_item(
    item_name: str,
    category: str,
    modifiers: list[str],
    menu_provider: MenuProvider,
    fuzzy_threshold: int = 85
) -> ValidationResult:
    """Pure function: check item exists + modifiers valid."""
    # Check item exists in menu
    # Check modifiers are valid for that item
    # Return ValidationResult with matched item or error
```

**Component Ownership**: `menu_validation.py` (pure functions)

**Pros**:
- Last line of defense
- Can auto-correct minor errors
- Prevents invalid orders

**Cons**:
- Reactive, not proactive
- May reject valid variations

**Accuracy Impact**: MEDIUM-HIGH (7/10) - Safety net

---

#### Strategy 10: Context Window Optimization
**Approach**: Only include relevant portions of menu in context.

**Implementation**:
- Detect if customer is ordering breakfast, lunch, drinks, etc.
- Only inject that category's items into prompt
- Reduces noise and token count
- Improves focus

**Example**:
```
Customer: "I want breakfast"
→ Only include Breakfast category items in context
```

**Pros**:
- Reduces token usage
- Reduces hallucination
- Faster inference

**Cons**:
- May miss cross-category orders
- Requires intent detection

**Accuracy Impact**: MEDIUM (6/10) - Helps focus

---

### Recommended Strategy Combination & Component Ownership

Each strategy is owned by a specific component, following SRP.

**Phase 1 (MVP)**:
1. **Function Calling** (Strategy 1)
   - Owner: `OrderTools` (defines tool schemas)
   - Core structure for order taking

2. **Menu Context Injection** (Strategy 2)
   - Owner: `DriveThruLLM` (injects context in chat())
   - Grounding LLM in actual menu

3. **Fuzzy String Matching** (Strategy 4)
   - Owner: `menu_validation.py` (pure function)
   - STT error handling

4. **Post-Processing Validation** (Strategy 9)
   - Owner: `OrderTools` (validates before state mutation)
   - Safety net - validate before add_item()

**Phase 2 (Optimization)**:
5. **Explicit Confirmation Loop** (Strategy 3)
   - Owner: `DriveThruAgent` (instructions/conversation flow)
   - User validation

6. **Semantic Search** (Strategy 5)
   - Owner: `MenuProvider` (add embedding-based search method)
   - Better matching via semantics

**Phase 3 (Advanced)**:
7. **Two-Stage Parsing** (Strategy 6)
   - Owner: `OrderTools` (modify tool implementation)
   - If needed for complex orders

8. **Chain-of-Thought** (Strategy 7)
   - Owner: `DriveThruAgent` (modify instructions)
   - If needed for better reasoning

**Key Insight**: Each strategy lives in exactly one component. This:
- Makes it easy to A/B test strategies (change one component)
- Enables independent testing of strategies
- Prevents strategy logic from leaking across boundaries

---

## 3. Order State Management

### 3.1 Order State Model

```python
@dataclass
class OrderItem:
    item_name: str
    category: str
    modifiers: list[str]
    quantity: int
    timestamp: datetime
    confirmed: bool = False

@dataclass
class OrderSession:
    session_id: str
    start_time: datetime
    items: list[OrderItem]
    status: Literal["in_progress", "completed", "cancelled"]
```

### 3.2 Incremental Logging

After each customer turn where an item is added:
- Append to `orders/{session_id}/incremental_log.jsonl`
- Each line is a JSON object with:
  - `timestamp`
  - `customer_utterance`
  - `item_parsed`
  - `agent_response`

### 3.3 Final Output

When customer says "done" or "that's all":
- Generate `orders/{session_id}/final_order.json`:

```json
{
  "session_id": "uuid-here",
  "timestamp": "2026-01-21T14:30:00Z",
  "items": [
    {
      "item_name": "Big Mac",
      "category": "Beef & Pork",
      "modifiers": [],
      "quantity": 1
    },
    {
      "item_name": "Medium Fries",
      "category": "Snacks & Sides",
      "modifiers": [],
      "quantity": 1
    }
  ],
  "total_items": 2,
  "order_summary": "1 Big Mac, 1 Medium Fries"
}
```

### 3.4 Menu Model Enhancements

To support order aggregation and better tracking, the `Item` class in `menus/mcdonalds/models.py` will be enhanced with the following features:

#### 3.4.1 New Fields

1. **quantity field** (`int`, default=1)
   - Tracks how many of this item are in the order
   - Default value is 1 for single items
   - Used for aggregating duplicate items

2. **item_id field** (`str`)
   - Unique identifier for each item instance
   - Auto-generated UUID to distinguish between item instances
   - Allows tracking individual items even with same name and modifiers

#### 3.4.2 Item Addition (`__add__` method)

Implements addition operator for combining items. Two items can be added if and only if:

**Conditions**:
- `item1.item_name == item2.item_name` (exact name match)
- `set(item1.modifiers) == set(item2.modifiers)` (same modifiers, order doesn't matter)

**Behavior**:
- If conditions are met: Create new item with `quantity = item1.quantity + item2.quantity`
- If conditions are not met: Raise `ValueError` with descriptive message

**Example Usage**:
```python
# Create two identical Big Macs
item1 = Item(
    category_name="Beef & Pork",
    item_name="Big Mac",
    available_as_base=True,
    quantity=1
)

item2 = Item(
    category_name="Beef & Pork",
    item_name="Big Mac",
    available_as_base=True,
    quantity=2
)

# Add them together
combined = item1 + item2  # quantity=3

# Items with different modifiers cannot be added
item3 = Item(
    category_name="Beef & Pork",
    item_name="Big Mac",
    available_as_base=True,
    quantity=1
)
item3.add_modifier("No Pickles")

# This will raise ValueError
combined = item1 + item3  # Error! Different modifiers
```

**Implementation Notes**:
- Modifier comparison uses set equality, so order doesn't matter
- The new combined item gets a new `item_id`
- Original items remain unchanged
- This enables order consolidation: "Two Big Macs" + "One Big Mac" = "Three Big Macs"

---

## 4. Agent Instructions & Persona

### 4.1 System Prompt

```
You are a friendly and efficient McDonald's drive-thru order taker. Your goal is to:

1. Greet the customer warmly
2. Listen carefully to their order
3. Use the add_item_to_order function to record each item
4. Confirm each item with the customer
5. When they're done, read back their complete order
6. Thank them and tell them the total

Guidelines:
- Be concise and natural in your responses
- If you're unsure about an item, ask for clarification
- Always confirm items before adding to the order
- Use the exact menu item names when confirming
- If a customer mentions an item not on the menu, politely inform them

Menu Structure:
- 9 categories: Breakfast, Beef & Pork, Chicken & Fish, Salads, Snacks & Sides, Desserts, Beverages, Coffee & Tea, Smoothies & Shakes
- 212 total items
- Some items have modifiers (e.g., "Quarter Pounder" with "Cheese")
```

### 4.2 Conversation Flow

```
Agent: "Welcome to McDonald's! What can I get for you today?"

Customer: "I'll have a Big Mac"

Agent: [Calls add_item_to_order(category="Beef & Pork", item_name="Big Mac", quantity=1)]
      "Got it, one Big Mac. Anything else?"

Customer: "And a medium fries"

Agent: [Calls add_item_to_order(category="Snacks & Sides", item_name="Medium Fries", quantity=1)]
      "One medium fries. Anything else?"

Customer: "No, that's all"

Agent: "Perfect! Your order is one Big Mac and one medium fries. Your total is [calculated].
       Please pull around to the first window."
       [Writes final order JSON]
```

---

## 5. Testing Strategy

### 5.1 Test Categories

1. **Single Item Orders**
   - Simple: "I want a Big Mac"
   - With quantity: "Two cheeseburgers"
   - With modifiers: "Quarter Pounder with cheese"

2. **Multi-Item Orders**
   - "Big Mac, large fries, and a Coke"
   - "Two Big Macs, one with no pickles"

3. **Complex Orders**
   - "I want a number 1 with a Coke" (if meal combos are supported)
   - Orders with substitutions
   - Orders with special requests

4. **Error Handling**
   - Invalid items: "I want a Whopper" (Burger King item)
   - Unclear requests: "I want a burger"
   - Corrections: "Actually, make that a McDouble"

5. **Accuracy Tests**
   - STT variations: "Big Mack" → "Big Mac"
   - Synonym handling: "chicken nuggets" → "Chicken McNuggets"
   - Modifier accuracy: Did modifiers get applied correctly?

### 5.2 Test Implementation

```python
@pytest.mark.asyncio
async def test_single_item_order_accuracy() -> None:
    """Test that a simple single-item order is captured accurately."""
    async with (
        _llm() as judge_llm,
        AgentSession(llm=drive_thru_llm) as session,
    ):
        await session.start(DriveThruAgent())

        # Customer orders a Big Mac
        result = await session.run(user_input="I'll have a Big Mac")

        # Verify the agent called the add_item_to_order function
        result.expect.next_event().is_function_call(
            function_name="add_item_to_order",
            arguments={
                "category": "Beef & Pork",
                "item_name": "Big Mac",
                "quantity": 1,
                "modifiers": []
            }
        )

        # Verify the agent confirmed the item
        await (
            result.expect.next_event()
            .is_message(role="assistant")
            .judge(
                judge_llm,
                intent="Confirms that one Big Mac was added to the order and asks if the customer wants anything else"
            )
        )

        # End the order
        result = await session.run(user_input="That's all")

        # Verify final order JSON was created correctly
        assert order_manager.get_final_order() == {
            "items": [
                {"item_name": "Big Mac", "category": "Beef & Pork", "modifiers": [], "quantity": 1}
            ]
        }
```

### 5.3 Accuracy Metrics

Track the following metrics:
- **Item Name Accuracy**: % of items correctly identified
- **Modifier Accuracy**: % of modifiers correctly applied
- **Quantity Accuracy**: % of quantities correctly captured
- **Order Completeness**: % of orders with all items captured
- **False Positives**: Items added that weren't ordered
- **False Negatives**: Items ordered but not added

Target: 95%+ accuracy on all metrics

---

## 6. Implementation Phases

### Phase 1: Core Infrastructure (Build from bottom up, test-first)

**Principle**: Start with components that have no dependencies (pure functions, data models), then build upward.

#### Step 1.1: Menu Models & Validation (No dependencies)
- [ ] Enhance `Item` class with `quantity` field (default=1)
- [ ] Enhance `Item` class with `item_id` field (UUID)
- [ ] Implement `__add__` method for `Item` class
- [ ] Write unit tests for `Item` enhancements
  - Test addition with same modifiers
  - Test addition failure with different modifiers
  - Test quantity field defaults

#### Step 1.2: Pure Functions (No dependencies)
- [ ] Implement `menu_validation.py` with pure functions
  - `fuzzy_match_item()`
  - `validate_item_exists()`
  - `validate_modifiers()`
  - `validate_order_item()`
- [ ] Write comprehensive unit tests for validation functions
  - Fast, deterministic, no I/O
  - Test edge cases: empty inputs, exact matches, fuzzy matches, no matches

#### Step 1.3: Read-Only Data Provider (Depends on: Item models)
- [ ] Implement `MenuProvider` class
  - Constructor loads JSON
  - `search_items()`, `get_category()`, `get_item()`
  - All methods return immutable data
- [ ] Write unit tests for MenuProvider
  - Use fixture JSON file
  - Test search, category queries, item lookups
  - Verify immutability (mutations don't affect provider)

#### Step 1.4: Stateful Order Manager (Depends on: OrderItem dataclass)
- [ ] Define `OrderItem` dataclass
- [ ] Implement `OrderStateManager` class
  - `add_item()`, `remove_item()`, `update_item_quantity()`
  - `get_items()`, `get_total_count()`, `get_order_summary()`
  - `complete_order()`, `clear_order()`
  - Incremental logging (append to JSONL after each mutation)
  - Final JSON generation
- [ ] Write unit tests for OrderStateManager
  - Test in-memory state operations (fast)
  - Test file I/O separately (use temp directory)
  - Verify incremental log appends correctly
  - Verify final JSON structure

#### Step 1.5: Verify Boundaries
- [ ] Ensure MenuProvider has no mutable state
- [ ] Ensure OrderStateManager is single source of truth
- [ ] Ensure validation functions are pure (no I/O, no side effects)
- [ ] Run all unit tests - should be fast (<1 second total)

### Phase 2: Coordination Layer (Build tools and wrappers)

**Principle**: Now that we have testable components, build the coordination layer that wires them together.

#### Step 2.1: LLM Tools (Depends on: OrderStateManager, MenuProvider, menu_validation)
- [ ] Implement `create_order_tools()` in `src/tools/order_tools.py`
  - Define `add_item_to_order` tool schema
    - Parameters: category, item_name, modifiers, quantity
    - Description optimized for LLM understanding
  - Implement tool function:
    ```python
    # 1. Validate using menu_validation.validate_order_item()
    # 2. If valid: order_state.add_item()
    # 3. Return structured confirmation
    ```
  - Define `complete_order` tool schema
  - Implement tool function: calls order_state.complete_order()
- [ ] Write integration tests for order_tools
  - Mock OrderStateManager, real MenuProvider
  - Verify validation is called before state mutation
  - Verify tool returns proper schema
  - Test invalid inputs (should not mutate state)

#### Step 2.2: LLM Wrapper (Depends on: MenuProvider)
- [ ] Implement `DriveThruLLM` wrapper
  - Constructor: receives wrapped_llm, menu_provider, config
  - `chat()` method:
    ```python
    # 1. Extract keywords from latest user message
    # 2. Query menu_provider.search_items(keyword)
    # 3. Inject relevant items into chat_ctx (augment system message)
    # 4. Delegate to wrapped_llm.chat()
    ```
  - Keep wrapper STATELESS
- [ ] Write unit tests for DriveThruLLM
  - Mock wrapped LLM
  - Verify menu context is injected into chat_ctx
  - Verify delegation to wrapped LLM
  - No state stored in wrapper

#### Step 2.3: Accuracy Strategies (Implement within existing components)
- [ ] Strategy 1: Function Calling - Already implemented in OrderTools ✓
- [ ] Strategy 2: Menu Context Injection - Implemented in DriveThruLLM
- [ ] Strategy 4: Fuzzy String Matching - Implemented in menu_validation.py
- [ ] Strategy 9: Post-Processing Validation - Implemented in OrderTools (validate before add)
- [ ] Verify all strategies are in place
- [ ] Document which component owns which strategy

### Phase 3: Agent Integration (Wire everything together)

**Principle**: Agent is the orchestrator - it owns dependencies and wires them together.

#### Step 3.1: Agent Implementation (Depends on: All components from Phase 1 & 2)
- [ ] Implement `DriveThruAgent` class
  - Constructor receives: order_state, menu_provider, config
  - Sets drive-thru specific instructions (system prompt)
  - Registers tools: `create_order_tools(order_state, menu_provider, config)`
  - Agent OWNS OrderStateManager (composition)
  - Agent RECEIVES MenuProvider (dependency injection)
- [ ] Define agent instructions/persona
  - Concise, friendly, efficient
  - Clear about when to use tools
  - Handles confirmation flow

#### Step 3.2: App-Level Wiring (Depends on: DriveThruAgent, DriveThruLLM)
- [ ] Add `DriveThruConfig` to `src/config.py`
  - menu_file_path, orders_output_dir
  - fuzzy_match_threshold, max_context_items
  - enable_confirmation_loop, enable_semantic_search
- [ ] Create `DriveThruVoiceAgentApp` (or extend `VoiceAgentApp`)
  - Instantiate MenuProvider (singleton, loaded once)
  - Wrap base LLM with DriveThruLLM (injecting MenuProvider)
  - Create OrderStateManager for each session (session_handler)
  - Create DriveThruAgent (injecting order_state and menu_provider)
  - Wire to SessionHandler
- [ ] Verify dependency flow:
  ```
  App creates MenuProvider (singleton)
     ├─> Injects into DriveThruLLM wrapper
     ├─> Injects into DriveThruAgent
     └─> Injects into OrderTools

  App creates OrderStateManager per session
     ├─> Owned by DriveThruAgent
     └─> Passed to OrderTools
  ```

#### Step 3.3: Integration Testing
- [ ] Write integration test: OrderTools + OrderStateManager + MenuProvider
  - No mocked components, real coordination
  - Verify end-to-end flow: validate → add → log
- [ ] Test console mode end-to-end
  - Use mock LLM or real LLM with simple prompts
  - Verify order state is persisted correctly
  - Verify incremental logs and final JSON

### Phase 4: Testing & Refinement (2-3 days)
- [ ] Write comprehensive test suite (20+ tests)
- [ ] Test with real voice input (console mode)
- [ ] Measure accuracy metrics
- [ ] Identify failure modes
- [ ] Iterate on prompts and validation logic

### Phase 5: Advanced Strategies (Optional, 2-3 days)
- [ ] Implement Strategy 3: Explicit Confirmation Loop
- [ ] Implement Strategy 5: Semantic Search with Embeddings
- [ ] A/B test different strategy combinations
- [ ] Optimize for latency and cost

---

## 7. File Structure

```
src/
├── drive_thru_agent.py          # Agent orchestration (owns OrderStateManager)
├── drive_thru_llm.py            # LLM wrapper (stateless context injection)
├── menu_provider.py             # Menu data provider (read-only)
├── order_state_manager.py       # Order state + persistence (single source of truth)
├── menu_validation.py           # Pure validation functions
└── tools/
    ├── __init__.py
    └── order_tools.py           # LiveKit Tool definitions (coordination layer)

tests/
├── test_menu_validation.py      # Unit tests for pure functions (fast)
├── test_menu_provider.py        # Unit tests for menu queries (fast)
├── test_order_state.py          # Unit tests for state management (fast)
├── test_drive_thru_llm.py       # Unit tests for LLM wrapper (fast, mocked LLM)
├── test_order_tools.py          # Integration tests for tools (medium)
├── test_drive_thru_agent.py     # End-to-end agent tests (slow, uses real LLM/judge)
└── test_accuracy.py             # Accuracy benchmarks (slow)

orders/
├── {session_id}/
│   ├── incremental_log.jsonl    # Per-turn logging
│   └── final_order.json         # Final order output

menus/
└── mcdonalds/
    ├── models.py                # Pydantic models (Item, Modifier, Menu)
    └── transformed-data/
        └── menu-structure-2026-01-21.json

plan/
└── mcdonalds-drive-thru-agent-plan.md  # This document


Test Pyramid (following best practices):
┌─────────────┐
│  E2E Tests  │  ← Few, slow, test full agent behavior
├─────────────┤
│ Integration │  ← Some, medium, test component interactions
├─────────────┤
│ Unit Tests  │  ← Many, fast, test isolated components
└─────────────┘

Unit tests should be:
- Fast (no I/O, no real LLM calls)
- Isolated (test one component at a time)
- Deterministic (no randomness, no flakiness)

Integration tests should:
- Use real components but mock expensive dependencies (e.g., mock LLM)
- Test interactions between 2-3 components

E2E tests should:
- Use judge-based evaluation for natural language
- Cover critical user paths
- Be fewer in number (expensive to run)
```

---

## 8. Configuration

Add to `src/config.py`:

```python
class DriveThruConfig(BaseModel):
    """Configuration for drive-thru agent."""

    menu_file_path: str = Field(
        default="menus/mcdonalds/transformed-data/menu-structure-2026-01-21.json",
        description="Path to menu JSON file"
    )

    orders_output_dir: str = Field(
        default="orders",
        description="Directory to save order files"
    )

    fuzzy_match_threshold: int = Field(
        default=85,
        description="Minimum fuzzy match score (0-100)"
    )

    enable_confirmation_loop: bool = Field(
        default=True,
        description="Require confirmation before adding items"
    )

    enable_semantic_search: bool = Field(
        default=False,
        description="Use embeddings for semantic item search"
    )

    max_context_items: int = Field(
        default=50,
        description="Maximum number of menu items to inject into context"
    )
```

---

## 9. Risks & Mitigations

### Risk 1: STT Errors
**Impact**: Customer says "Big Mac" but STT hears "Big Mack" or "big man"
**Mitigation**:
- Fuzzy string matching (Strategy 4)
- Semantic search (Strategy 5)
- Confirmation loop (Strategy 3)

### Risk 2: LLM Hallucination
**Impact**: LLM adds items not on the menu
**Mitigation**:
- Function calling with strict validation
- Menu context injection (Strategy 2)
- Post-processing validation (Strategy 9)

### Risk 3: Modifier Errors
**Impact**: Customer wants "no pickles" but modifier not captured
**Mitigation**:
- Structured modifier field in function calling
- Validation against available modifiers per item
- Explicit confirmation

### Risk 4: Latency
**Impact**: Slow response times frustrate customers
**Mitigation**:
- Use faster LLM (GPT-4.1-nano or similar)
- Optimize context injection (Strategy 10)
- Precompute embeddings if using Strategy 5
- Enable preemptive generation

### Risk 5: Multi-Item Order Complexity
**Impact**: Customer orders 5 items in one utterance, agent misses some
**Mitigation**:
- Ask customer to order one item at a time
- Use two-stage parsing (Strategy 6) if needed
- Read back full order at end for correction

---

## 10. Success Criteria

The implementation will be considered successful when:

1. **Accuracy**: ≥95% item name accuracy on test suite
2. **Modifier Accuracy**: ≥90% modifier accuracy
3. **Completeness**: ≥95% of orders captured completely
4. **Latency**: <2 seconds per turn (STT → TTS)
5. **Robustness**: Handles invalid items gracefully (100% of test cases)
6. **Output**: Correctly generates incremental logs and final JSON for 100% of orders
7. **User Experience**: Judge-based tests confirm natural, friendly interaction

---

## 11. Future Enhancements

After initial implementation, consider:

1. **Meal Combos**: Support "Number 1" style ordering
2. **Upselling**: "Would you like to make that a meal?"
3. **Menu Recommendations**: Based on time of day, weather, etc.
4. **Price Calculation**: Calculate total cost
5. **Multi-Language Support**: Spanish, etc.
6. **Voice Biometrics**: Remember repeat customers
7. **Order History**: "Same as last time"
8. **Integration**: Connect to POS system for real orders

---

## 12. Key Design Decisions

### Why Separate DriveThruLLM from OrderStateManager?
**Principle**: Single Responsibility Principle (SRP)

LLM wrapping (context injection) is orthogonal to state management. By separating:
- DriveThruLLM can be tested with mock LLM (fast unit tests)
- OrderStateManager can be tested without LLM (fast unit tests)
- Each component has one reason to change
- Components can be swapped independently (e.g., try different context injection strategies)

### Why Pure Functions for Validation?
**Principle**: Functional Core, Imperative Shell

Pure functions are maximally testable:
- No I/O, no side effects
- Deterministic outputs for same inputs
- Fast to execute (no database, no API calls)
- Easy to reason about
- Can be reused anywhere

This enables Test-Driven Development: write test first, implement function, iterate quickly.

### Why MenuProvider Returns Immutable Data?
**Principle**: Immutability Reduces Bugs

If MenuProvider returned mutable references:
- Callers could accidentally modify menu data
- Hard to track down where menu was corrupted
- Thread safety issues in concurrent sessions

By returning immutable copies:
- Menu data is protected from accidental mutation
- Single source of truth guaranteed
- Easier to reason about data flow

### Why OrderStateManager is the Only State Owner?
**Principle**: Single Source of Truth (SSOT)

All order mutations flow through one place:
- Easy to add logging/auditing
- Persistence logic centralized
- Impossible to have inconsistent state
- Debugging is straightforward: check one component
- Testing is simple: verify state before/after

Contrast with diffused state (anti-pattern):
- State scattered across DriveThruLLM, tools, agent
- Hard to debug: "Where did this item come from?"
- Hard to test: need to set up multiple components
- Brittle: changes ripple across multiple components

### Why Tools are Thin Coordination Layer?
**Principle**: Tell, Don't Ask

Tools coordinate but don't implement logic:
```python
# Good (coordination)
def add_item_to_order_tool(...):
    result = validate_order_item(...)  # Ask validation layer
    if result.is_valid:
        order_state.add_item(...)      # Tell state manager
    return confirmation

# Bad (implementation leaking into tool)
def add_item_to_order_tool(...):
    # Fuzzy matching logic here
    # Modifier validation logic here
    # File I/O logic here
    # Now tool is hard to test and has multiple responsibilities
```

### Why Function Calling?
**Principle**: Make Invalid States Unrepresentable

Function calling provides structured output that's easy to validate and parse. It forces the LLM to think in terms of discrete actions rather than free-form text, reducing ambiguity.

Schema enforcement means: "If it parses, it's valid" (or close to it).

### Why Multiple Strategies?
**Principle**: Defense in Depth

No single strategy achieves 100% accuracy. Layering multiple complementary strategies (function calling + fuzzy matching + validation) creates a robust system where failures at one level are caught by another.

### Why Confirmation Loop?
**Principle**: Human-in-the-Loop

Voice AI has inherent uncertainty (STT errors, LLM mistakes). Confirming each item catches errors before they compound. Cheaper to fix early than to remake entire order.

### Why Incremental Logging?
**Principle**: Observability & Debuggability

Provides an audit trail and debugging information. If final order is wrong, we can trace back through the conversation to see where it went wrong.

Enables data-driven improvement: analyze logs to find common error patterns.

### Why Focus on Accuracy Over Speed?
**Principle**: Correctness First, Optimization Second

Wrong orders are worse than slow orders. Once accuracy is proven, we can optimize for latency.

Premature optimization is the root of all evil. Get it working, get it right, then make it fast.

### Why Test Pyramid (Many Unit, Few E2E)?
**Principle**: Fast Feedback Loops (Continuous Delivery)

Unit tests:
- Run in milliseconds
- Give instant feedback
- Pinpoint exact failure
- Enable rapid iteration

E2E tests:
- Run in seconds/minutes
- Slow feedback
- Hard to debug failures
- Necessary but expensive

Build on solid foundation of fast unit tests, use E2E tests for critical paths only.

### Why Dependency Injection?
**Principle**: Inversion of Control (IoC)

Components receive dependencies rather than creating them:
- Easy to substitute mocks for testing
- Easy to swap implementations (e.g., different LLM, different storage)
- Explicit dependencies (no hidden coupling)
- Testable in isolation

```python
# Good (DI)
class DriveThruAgent:
    def __init__(self, order_state: OrderStateManager, menu: MenuProvider):
        self.order_state = order_state  # Injected
        self.menu = menu                # Injected

# Bad (hidden dependencies)
class DriveThruAgent:
    def __init__(self):
        self.order_state = OrderStateManager()  # Hard-coded
        self.menu = MenuProvider()              # Hard-coded
        # Now can't test with mocks, can't swap implementations
```

---

## 13. Experimentation Framework

To determine which strategies work best, implement an experimentation framework:

```python
class AccuracyExperiment:
    """Framework for testing accuracy strategies."""

    def __init__(self, test_cases: list[OrderTestCase]):
        self.test_cases = test_cases

    async def run_experiment(self, strategy_config: dict) -> ExperimentResults:
        """Run all test cases with a given strategy configuration."""
        results = []
        for test_case in self.test_cases:
            result = await self.run_single_test(test_case, strategy_config)
            results.append(result)
        return ExperimentResults(results)

    def compare_strategies(self, strategy_a: dict, strategy_b: dict) -> Comparison:
        """A/B test two strategy configurations."""
        results_a = await self.run_experiment(strategy_a)
        results_b = await self.run_experiment(strategy_b)
        return Comparison(results_a, results_b)
```

Use this to answer questions like:
- Does semantic search improve accuracy over fuzzy matching?
- What's the optimal fuzzy match threshold?
- Does chain-of-thought reduce hallucination?
- What's the latency vs accuracy tradeoff?

---

## 14. Monitoring & Observability

In production, track:
- **Per-turn metrics**: Item extraction accuracy, latency
- **Per-order metrics**: Order completeness, correction rate
- **LLM metrics**: Token usage, cost per order
- **Error rates**: Invalid items, failed validations
- **User satisfaction**: Explicit feedback, order completion rate

Use LiveKit's built-in metrics framework + custom application metrics.

---

## Conclusion

This plan provides a comprehensive roadmap for building a high-accuracy McDonald's drive-thru order taker. The key insight is that **accuracy requires multiple layered strategies**, not a single silver bullet. By combining function calling, menu context injection, fuzzy matching, and validation, we can achieve 95%+ accuracy while maintaining a natural conversational experience.

The phased approach allows for iterative development: start with core infrastructure, implement MVP accuracy strategies, test thoroughly, then optimize with advanced strategies as needed.

**Next Steps**:
1. Review and approve this plan
2. Begin Phase 1 implementation
3. Set up testing infrastructure
4. Iterate based on real-world results
