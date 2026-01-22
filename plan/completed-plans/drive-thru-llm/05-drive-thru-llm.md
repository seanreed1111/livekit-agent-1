# Plan 05: DriveThruLLM (Context Injection Wrapper)

**Created**: 2026-01-21
**Status**: Ready for Implementation
**Dependencies**: Plan 02 (MenuProvider)
**Estimated Complexity**: Medium

---

## Overview

`DriveThruLLM` is a **stateless LLM wrapper** that intercepts chat calls to inject relevant menu context. This implements **Strategy 2: Menu Context Injection** from the main plan, helping ground the LLM in actual menu items and reducing hallucination.

**Key Principles**:
- 🎯 **Stateless Wrapper**: No state stored, just intercepts and delegates
- 📝 **Context Injection**: Dynamically adds menu items to chat context
- 🔄 **Delegation**: Wraps another LLM, delegates actual inference
- ⚡ **Keyword-Based**: Extracts keywords from user input to find relevant items

---

## Component Design

### File Structure

**File**: `src/drive_thru_llm.py` (new)

**Dependencies**:
- `livekit.agents.llm` (LLM, ChatContext, ChatMessage, LLMStream)
- `src/menu_provider.py` (MenuProvider)

**Pattern**: Similar to `KeywordInterceptLLM` from LiveKit examples

---

## Interface Contract

```python
from livekit.agents.llm import LLM, ChatContext, LLMStream

class DriveThruLLM(LLM):
    """Stateless LLM wrapper that injects menu context.

    Intercepts chat() calls to:
    1. Extract keywords from latest user message
    2. Query MenuProvider for relevant menu items
    3. Inject items into chat context
    4. Delegate to wrapped LLM

    This helps ground the LLM in actual menu items and reduces hallucination.
    """

    def __init__(
        self,
        wrapped_llm: LLM,
        menu_provider: MenuProvider,
        max_context_items: int = 50
    ) -> None:
        """
        Initialize wrapper.

        Args:
            wrapped_llm: The LLM to wrap (e.g., OpenAI GPT-4.1)
            menu_provider: MenuProvider for menu queries
            max_context_items: Max number of menu items to inject
        """

    def chat(
        self,
        *,
        chat_ctx: ChatContext,
        tools: list[Tool] | None = None,
        **kwargs
    ) -> LLMStream:
        """
        Intercept chat to inject menu context.

        Flow:
        1. Extract keywords from latest user message
        2. Search for relevant menu items
        3. Inject items into chat_ctx
        4. Delegate to wrapped_llm.chat()

        Returns:
            LLMStream from wrapped LLM
        """
```

---

## Implementation Details

### 1. Constructor

```python
def __init__(
    self,
    wrapped_llm: LLM,
    menu_provider: MenuProvider,
    max_context_items: int = 50
) -> None:
    """Initialize wrapper."""
    super().__init__()  # Initialize LLM base class
    self._wrapped_llm = wrapped_llm
    self._menu_provider = menu_provider
    self._max_context_items = max_context_items
```

### 2. Chat Method

```python
def chat(
    self,
    *,
    chat_ctx: ChatContext,
    tools: list[Tool] | None = None,
    **kwargs
) -> LLMStream:
    """Intercept chat to inject menu context."""

    # 1. Extract keywords from latest user message
    latest_message = self._get_latest_user_message(chat_ctx)
    if latest_message:
        keywords = self._extract_keywords(latest_message)

        # 2. Search for relevant menu items
        relevant_items = self._find_relevant_items(keywords)

        # 3. Inject into context
        if relevant_items:
            augmented_ctx = self._inject_menu_context(chat_ctx, relevant_items)
        else:
            augmented_ctx = chat_ctx
    else:
        augmented_ctx = chat_ctx

    # 4. Delegate to wrapped LLM
    return self._wrapped_llm.chat(
        chat_ctx=augmented_ctx,
        tools=tools,
        **kwargs
    )
```

### 3. Helper Methods

#### Extract Keywords

```python
def _extract_keywords(self, message: str) -> list[str]:
    """
    Extract potential menu-related keywords from user message.

    Simple approach: Split on spaces, filter stopwords, lowercase.

    Args:
        message: User's message text

    Returns:
        List of keywords to search

    Examples:
        "I want a Big Mac" → ["big", "mac"]
        "Two cheeseburgers please" → ["two", "cheeseburgers", "please"]
    """
    # Lowercase and split
    words = message.lower().split()

    # Remove common stopwords
    stopwords = {"i", "want", "a", "an", "the", "please", "thanks", "and", "with"}
    keywords = [w for w in words if w not in stopwords]

    return keywords
```

#### Find Relevant Items

```python
def _find_relevant_items(self, keywords: list[str]) -> list[Item]:
    """
    Find menu items matching keywords.

    Args:
        keywords: List of keywords to search

    Returns:
        List of relevant menu items (up to max_context_items)

    Strategy:
        - Search for each keyword
        - Deduplicate results
        - Limit to max_context_items
    """
    all_matches = []
    seen_items = set()

    for keyword in keywords:
        matches = self._menu_provider.search_items(keyword)
        for item in matches:
            if item.item_name not in seen_items:
                all_matches.append(item)
                seen_items.add(item.item_name)

            if len(all_matches) >= self._max_context_items:
                break

        if len(all_matches) >= self._max_context_items:
            break

    return all_matches
```

#### Inject Context

```python
def _inject_menu_context(
    self,
    chat_ctx: ChatContext,
    items: list[Item]
) -> ChatContext:
    """
    Inject menu items into chat context.

    Strategy: Add a system message with relevant menu items.

    Args:
        chat_ctx: Original chat context
        items: Relevant menu items to inject

    Returns:
        New ChatContext with injected menu items
    """
    # Format items for injection
    items_text = self._format_items_for_context(items)

    # Create system message with menu context
    menu_message = ChatMessage(
        role="system",
        content=f"Relevant menu items:\n{items_text}"
    )

    # Create new context with injected message
    # (Insert after system prompt but before conversation)
    new_messages = [chat_ctx.messages[0], menu_message] + chat_ctx.messages[1:]

    return ChatContext(messages=new_messages)
```

#### Format Items

```python
def _format_items_for_context(self, items: list[Item]) -> str:
    """
    Format menu items for LLM context.

    Args:
        items: List of menu items

    Returns:
        Formatted string of items

    Example:
        "- Big Mac (Beef & Pork)
         - Quarter Pounder (Beef & Pork)
         - Egg McMuffin (Breakfast)"
    """
    lines = []
    for item in items:
        # Group by category for clarity
        lines.append(f"- {item.item_name} ({item.category})")

        # Optionally include modifiers
        if item.modifiers:
            modifier_names = [m.modifier_name for m in item.modifiers]
            lines.append(f"  Modifiers: {', '.join(modifier_names)}")

    return "\n".join(lines)
```

---

## Testing Strategy

### Unit Tests

**File**: `tests/test_drive_thru_llm.py` (new)

**Test Strategy**: Mock wrapped LLM, real MenuProvider

```python
import pytest
from unittest.mock import Mock, AsyncMock
from livekit.agents.llm import ChatContext, ChatMessage, LLMStream

@pytest.fixture
def menu_provider():
    """Real MenuProvider."""
    return MenuProvider("menus/mcdonalds/transformed-data/menu-structure-2026-01-21.json")

@pytest.fixture
def mock_wrapped_llm():
    """Mock the wrapped LLM."""
    llm = Mock(spec=LLM)
    llm.chat = AsyncMock(return_value=Mock(spec=LLMStream))
    return llm

@pytest.fixture
def drive_thru_llm(mock_wrapped_llm, menu_provider):
    """Create DriveThruLLM with mock."""
    return DriveThruLLM(
        wrapped_llm=mock_wrapped_llm,
        menu_provider=menu_provider,
        max_context_items=20
    )
```

**Test Cases** (aim for 15+ tests):

#### Keyword Extraction Tests

1. `test_extract_keywords_simple()` - "I want a Big Mac" → ["big", "mac"]
2. `test_extract_keywords_removes_stopwords()`
3. `test_extract_keywords_lowercase()`
4. `test_extract_keywords_empty_message()`

#### Menu Search Tests

5. `test_find_relevant_items_single_keyword()` - "mac" finds Big Mac, Egg McMuffin
6. `test_find_relevant_items_multiple_keywords()` - "big mac" is more specific
7. `test_find_relevant_items_no_matches()`
8. `test_find_relevant_items_respects_max_limit()`

#### Context Injection Tests

9. `test_chat_injects_menu_context()`
```python
@pytest.mark.asyncio
async def test_chat_injects_menu_context(drive_thru_llm, mock_wrapped_llm):
    """Verify menu context is injected into chat."""
    # Create chat context with user message
    chat_ctx = ChatContext(messages=[
        ChatMessage(role="system", content="You are a drive-thru agent"),
        ChatMessage(role="user", content="I want a Big Mac")
    ])

    # Call chat
    await drive_thru_llm.chat(chat_ctx=chat_ctx)

    # Verify wrapped LLM was called
    mock_wrapped_llm.chat.assert_called_once()

    # Get the augmented context passed to wrapped LLM
    call_args = mock_wrapped_llm.chat.call_args
    augmented_ctx = call_args.kwargs["chat_ctx"]

    # Verify menu context was injected
    assert len(augmented_ctx.messages) > len(chat_ctx.messages)

    # Check that menu items were included
    menu_message = augmented_ctx.messages[1]
    assert "Big Mac" in menu_message.content
    assert "Beef & Pork" in menu_message.content
```

10. `test_chat_delegates_to_wrapped_llm()`
11. `test_chat_preserves_tools_parameter()`
12. `test_chat_no_context_injection_if_no_keywords()`

#### Integration Tests

13. `test_full_flow_with_real_menu()`
14. `test_handles_empty_user_message()`
15. `test_stateless_multiple_calls()`
```python
@pytest.mark.asyncio
async def test_stateless_multiple_calls(drive_thru_llm, mock_wrapped_llm):
    """Verify wrapper is stateless - multiple calls don't interfere."""
    ctx1 = ChatContext(messages=[
        ChatMessage(role="system", content="System"),
        ChatMessage(role="user", content="I want a Big Mac")
    ])

    ctx2 = ChatContext(messages=[
        ChatMessage(role="system", content="System"),
        ChatMessage(role="user", content="I want fries")
    ])

    # Make two calls
    await drive_thru_llm.chat(chat_ctx=ctx1)
    await drive_thru_llm.chat(chat_ctx=ctx2)

    # Both should work independently (no shared state)
    assert mock_wrapped_llm.chat.call_count == 2
```

---

## BDD Scenarios

DriveThruLLM supports all scenarios by providing menu context:

**Related BDD Scenarios**:
- **All scenarios** benefit from menu context injection
- **Scenario 1.1** (Order Big Mac) - "Big Mac" triggers injection of Beef & Pork items
- **Scenario 5.2** (Ambiguous request) - "burger" triggers all burger items
- **Scenario 5.4** (STT error recovery) - Context helps LLM understand "Big Mack"

---

## Implementation Checklist

### Phase 1: Basic Structure
- [ ] Create `src/drive_thru_llm.py`
- [ ] Define `DriveThruLLM` class extending `LLM`
- [ ] Implement `__init__()` with dependency injection
- [ ] Add type hints and docstrings

### Phase 2: Helper Methods
- [ ] Implement `_extract_keywords()`
- [ ] Implement `_find_relevant_items()`
- [ ] Implement `_format_items_for_context()`
- [ ] Implement `_inject_menu_context()`
- [ ] Test each method individually

### Phase 3: Chat Method
- [ ] Implement `chat()` method
- [ ] Wire together keyword extraction → search → injection → delegation
- [ ] Handle edge cases (no keywords, no matches, empty messages)

### Phase 4: Testing
- [ ] Create `tests/test_drive_thru_llm.py`
- [ ] Write keyword extraction tests (4 tests)
- [ ] Write menu search tests (4 tests)
- [ ] Write context injection tests (4 tests)
- [ ] Write integration tests (3 tests)
- [ ] Run tests: `uv run pytest tests/test_drive_thru_llm.py -v`

### Phase 5: Optimization
- [ ] Consider caching frequent searches (optional)
- [ ] Optimize keyword extraction (use NLP library if needed)
- [ ] Tune max_context_items parameter
- [ ] Measure token usage impact

### Phase 6: Code Quality
- [ ] Add type hints to all methods
- [ ] Add docstrings to all methods
- [ ] Run formatter: `uv run ruff format src/drive_thru_llm.py`
- [ ] Run linter: `uv run ruff check src/drive_thru_llm.py`
- [ ] Check coverage: `uv run pytest --cov=src.drive_thru_llm`

---

## Success Criteria

✅ **All unit tests pass** (15+ tests)
✅ **Wrapper is stateless** (no instance variables except config)
✅ **Context injection works** (menu items appear in augmented context)
✅ **Delegates correctly** (wrapped LLM is called with augmented context)
✅ **Type hints complete** (passes mypy --strict)
✅ **Docstrings complete** (all public methods documented)
✅ **90%+ code coverage**

---

## Dependencies for Next Plans

**This plan provides**:
- ✅ `DriveThruLLM` wrapper class
- ✅ Menu context injection (Strategy 2)
- ✅ Stateless LLM wrapper pattern
- ✅ Keyword-based search for relevant items

**Next plans can now use**:
- DriveThruLLM in agent definition
- Wrapped LLM for improved accuracy

---

## Design Notes

### Why Stateless?

Stateless wrapper means:
- No instance state to corrupt
- Thread-safe (could be shared, though not needed)
- Predictable behavior
- Easy to test

### Why Keyword Extraction?

Simple keyword extraction is:
- Fast (no extra API calls)
- Good enough for this use case
- Easily understood and debugged

Could upgrade to NLP later if needed.

### Why System Message for Injection?

Injecting as system message:
- Clearly separates menu context from conversation
- LLM treats it as reference material
- Doesn't pollute conversation history

Alternative: Augment existing system prompt (more complex).

### Token Usage Impact

Injecting 20-50 menu items adds ~500-1000 tokens per request.

Trade-off:
- **Cost**: Slightly higher (more input tokens)
- **Benefit**: Better accuracy, less hallucination

Worth it for accuracy-critical application.

---

## Example Usage

```python
# Create wrapped LLM
base_llm = openai.LLM(model="gpt-4.1")

# Create menu provider (singleton)
menu_provider = MenuProvider("menus/mcdonalds/menu.json")

# Wrap LLM
drive_thru_llm = DriveThruLLM(
    wrapped_llm=base_llm,
    menu_provider=menu_provider,
    max_context_items=30
)

# Use in agent
agent = Agent(
    llm=drive_thru_llm,  # Use wrapped LLM
    instructions="...",
    tools=tools
)
```

**Flow**:
1. User: "I want a Big Mac"
2. DriveThruLLM extracts keywords: ["big", "mac"]
3. Searches menu: finds Big Mac, Egg McMuffin, etc.
4. Injects context: "Relevant items: Big Mac (Beef & Pork), ..."
5. Delegates to base LLM with augmented context
6. LLM sees menu items and makes better decision

**Key Principle**: Context injection grounds the LLM in reality (the actual menu), reducing hallucination.
