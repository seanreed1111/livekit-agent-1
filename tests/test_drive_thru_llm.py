"""Tests for DriveThruLLM context injection wrapper.

This module tests the DriveThruLLM class, which wraps an LLM and injects
relevant menu context based on keywords extracted from user messages.
"""

from unittest.mock import AsyncMock, Mock

import pytest
from livekit.agents.llm import ChatContext

# Import will work once we create the module
# from drive_thru_llm import DriveThruLLM


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def mock_wrapped_llm():
    """Create a mock LLM that implements the chat interface."""
    llm = Mock()
    # Create an async mock for the chat method
    llm.chat = AsyncMock()
    # Mock the return value to be an LLMStream-like object
    mock_stream = Mock()
    llm.chat.return_value = mock_stream
    return llm


@pytest.fixture
def drive_thru_llm(mock_wrapped_llm, test_menu_provider):
    """Create DriveThruLLM with mock LLM and test menu."""
    from drive_thru_llm import DriveThruLLM

    return DriveThruLLM(
        wrapped_llm=mock_wrapped_llm,
        menu_provider=test_menu_provider,
        max_context_items=20,
    )


@pytest.fixture
def drive_thru_llm_real_menu(mock_wrapped_llm, real_menu_provider):
    """Create DriveThruLLM with mock LLM and real menu."""
    from drive_thru_llm import DriveThruLLM

    return DriveThruLLM(
        wrapped_llm=mock_wrapped_llm,
        menu_provider=real_menu_provider,
        max_context_items=50,
    )


# ============================================================================
# Keyword Extraction Tests
# ============================================================================


def test_extract_keywords_simple(drive_thru_llm):
    """Test extracting keywords from simple message."""
    message = "I want a Big Mac"
    keywords = drive_thru_llm._extract_keywords(message)

    # Should remove stopwords and lowercase
    assert "big" in keywords
    assert "mac" in keywords
    assert "i" not in keywords
    assert "want" not in keywords
    assert "a" not in keywords


def test_extract_keywords_removes_stopwords(drive_thru_llm):
    """Test that common stopwords are filtered out."""
    message = "I want the big mac please and thanks"
    keywords = drive_thru_llm._extract_keywords(message)

    # Stopwords should be removed
    stopwords = ["i", "want", "the", "please", "and", "thanks", "a", "an"]
    for stopword in stopwords:
        assert stopword not in keywords

    # Content words should remain
    assert "big" in keywords
    assert "mac" in keywords


def test_extract_keywords_lowercase(drive_thru_llm):
    """Test that keywords are lowercased."""
    message = "BIG MAC"
    keywords = drive_thru_llm._extract_keywords(message)

    assert "big" in keywords
    assert "mac" in keywords
    assert "BIG" not in keywords
    assert "MAC" not in keywords


def test_extract_keywords_empty_message(drive_thru_llm):
    """Test extracting keywords from empty message."""
    message = ""
    keywords = drive_thru_llm._extract_keywords(message)

    assert keywords == []


# ============================================================================
# Menu Search Tests
# ============================================================================


def test_find_relevant_items_single_keyword(drive_thru_llm_real_menu):
    """Test finding items with a single keyword."""
    keywords = ["mac"]
    items = drive_thru_llm_real_menu._find_relevant_items(keywords)

    # Should find items containing "mac"
    assert len(items) > 0
    item_names = [item.item_name for item in items]

    # Should include Big Mac and Egg McMuffin
    assert any("Big Mac" in name for name in item_names)


def test_find_relevant_items_multiple_keywords(drive_thru_llm_real_menu):
    """Test finding items with multiple keywords."""
    keywords = ["big", "mac"]
    items = drive_thru_llm_real_menu._find_relevant_items(keywords)

    # Should find items matching either keyword
    assert len(items) > 0


def test_find_relevant_items_no_matches(drive_thru_llm):
    """Test finding items when no matches exist."""
    keywords = ["nonexistent", "items"]
    items = drive_thru_llm._find_relevant_items(keywords)

    # Should return empty list when no matches
    assert items == []


def test_find_relevant_items_respects_max_limit(drive_thru_llm_real_menu):
    """Test that max_context_items limit is respected."""
    # Use a keyword that matches many items
    keywords = ["mc"]  # Should match many McDonald's items
    items = drive_thru_llm_real_menu._find_relevant_items(keywords)

    # Should not exceed max_context_items
    assert len(items) <= drive_thru_llm_real_menu._max_context_items


# ============================================================================
# Context Injection Tests
# ============================================================================


@pytest.mark.asyncio
async def test_chat_injects_menu_context(drive_thru_llm_real_menu, mock_wrapped_llm):
    """Test that menu context is injected into chat."""
    # Create chat context with user message
    chat_ctx = ChatContext()
    chat_ctx.add_message(role="system", content="You are a drive-thru agent")
    chat_ctx.add_message(role="user", content="I want a Big Mac")

    # Call chat
    await drive_thru_llm_real_menu.chat(chat_ctx=chat_ctx)

    # Verify wrapped LLM was called
    mock_wrapped_llm.chat.assert_called_once()

    # Get the augmented context passed to wrapped LLM
    call_args = mock_wrapped_llm.chat.call_args
    augmented_ctx = call_args.kwargs["chat_ctx"]

    # Verify menu context was injected
    assert len(augmented_ctx.items) > len(chat_ctx.items)

    # Check that menu items were included
    # The menu message should be the second message (after system prompt)
    menu_item = augmented_ctx.items[1]
    assert menu_item.role == "system"

    # Extract content text using text_content property if available
    if hasattr(menu_item, "text_content"):
        content_text = menu_item.text_content
    else:
        content_text = ""
        if isinstance(menu_item.content, list):
            for part in menu_item.content:
                if hasattr(part, "text"):
                    content_text += part.text
                elif isinstance(part, str):
                    content_text += part
        elif isinstance(menu_item.content, str):
            content_text = menu_item.content

    # Check for menu content
    assert "Big Mac" in content_text or "menu" in content_text.lower()


@pytest.mark.asyncio
async def test_chat_delegates_to_wrapped_llm(drive_thru_llm, mock_wrapped_llm):
    """Test that chat properly delegates to wrapped LLM."""
    chat_ctx = ChatContext()
    chat_ctx.add_message(role="system", content="System prompt")
    chat_ctx.add_message(role="user", content="Hello")

    # Call chat
    result = await drive_thru_llm.chat(chat_ctx=chat_ctx)

    # Verify wrapped LLM was called
    mock_wrapped_llm.chat.assert_called_once()

    # Verify result is returned
    assert result is not None


@pytest.mark.asyncio
async def test_chat_preserves_tools_parameter(drive_thru_llm, mock_wrapped_llm):
    """Test that tools parameter is passed through to wrapped LLM."""
    chat_ctx = ChatContext()
    chat_ctx.add_message(role="system", content="System")
    chat_ctx.add_message(role="user", content="Test")

    # Mock tools
    mock_tools = [Mock(), Mock()]

    # Call chat with tools
    await drive_thru_llm.chat(chat_ctx=chat_ctx, tools=mock_tools)

    # Verify tools were passed to wrapped LLM
    call_args = mock_wrapped_llm.chat.call_args
    assert call_args.kwargs["tools"] == mock_tools


@pytest.mark.asyncio
async def test_chat_no_context_injection_if_no_keywords(
    drive_thru_llm, mock_wrapped_llm
):
    """Test that no context is injected when no keywords are extracted."""
    # Create message with only stopwords
    chat_ctx = ChatContext()
    chat_ctx.add_message(role="system", content="System")
    chat_ctx.add_message(role="user", content="I want a the")

    # Call chat
    await drive_thru_llm.chat(chat_ctx=chat_ctx)

    # Get augmented context
    call_args = mock_wrapped_llm.chat.call_args
    augmented_ctx = call_args.kwargs["chat_ctx"]

    # Should not inject menu context when no keywords
    # Context should have same number of items
    assert len(augmented_ctx.items) == len(chat_ctx.items)


# ============================================================================
# Integration Tests
# ============================================================================


@pytest.mark.asyncio
async def test_full_flow_with_real_menu(drive_thru_llm_real_menu, mock_wrapped_llm):
    """Test complete flow with real menu data."""
    chat_ctx = ChatContext()
    chat_ctx.add_message(role="system", content="You are a McDonald's agent")
    chat_ctx.add_message(
        role="user", content="I want two Big Macs with no pickles please"
    )

    # Call chat
    await drive_thru_llm_real_menu.chat(chat_ctx=chat_ctx)

    # Verify wrapped LLM was called
    assert mock_wrapped_llm.chat.called

    # Get augmented context
    call_args = mock_wrapped_llm.chat.call_args
    augmented_ctx = call_args.kwargs["chat_ctx"]

    # Verify context was augmented
    assert len(augmented_ctx.items) >= len(chat_ctx.items)


@pytest.mark.asyncio
async def test_handles_empty_user_message(drive_thru_llm, mock_wrapped_llm):
    """Test handling of empty or missing user messages."""
    # Chat context with only system message
    chat_ctx = ChatContext()
    chat_ctx.add_message(role="system", content="System")

    # Call chat
    await drive_thru_llm.chat(chat_ctx=chat_ctx)

    # Should still delegate to wrapped LLM without errors
    assert mock_wrapped_llm.chat.called


@pytest.mark.asyncio
async def test_stateless_multiple_calls(drive_thru_llm_real_menu, mock_wrapped_llm):
    """Test that wrapper is stateless - multiple calls don't interfere."""
    ctx1 = ChatContext()
    ctx1.add_message(role="system", content="System")
    ctx1.add_message(role="user", content="I want a Big Mac")

    ctx2 = ChatContext()
    ctx2.add_message(role="system", content="System")
    ctx2.add_message(role="user", content="I want fries")

    # Make two calls
    await drive_thru_llm_real_menu.chat(chat_ctx=ctx1)
    await drive_thru_llm_real_menu.chat(chat_ctx=ctx2)

    # Both should work independently (no shared state)
    assert mock_wrapped_llm.chat.call_count == 2

    # Verify each call got different context
    first_call_ctx = mock_wrapped_llm.chat.call_args_list[0].kwargs["chat_ctx"]
    second_call_ctx = mock_wrapped_llm.chat.call_args_list[1].kwargs["chat_ctx"]

    # Contexts should be different
    assert first_call_ctx is not second_call_ctx


# ============================================================================
# Helper Method Tests
# ============================================================================


def test_format_items_for_context(drive_thru_llm_real_menu):
    """Test formatting items for LLM context."""
    # Get some real items
    items = drive_thru_llm_real_menu._menu_provider.search_items("Big Mac")

    # Format them
    formatted = drive_thru_llm_real_menu._format_items_for_context(items)

    # Should include item names and categories
    assert "Big Mac" in formatted
    assert isinstance(formatted, str)
    assert len(formatted) > 0


def test_format_items_for_context_empty_list(drive_thru_llm):
    """Test formatting empty list of items."""
    formatted = drive_thru_llm._format_items_for_context([])

    # Should return empty string or minimal content
    assert isinstance(formatted, str)


def test_get_latest_user_message(drive_thru_llm):
    """Test extracting the latest user message from context."""
    chat_ctx = ChatContext()
    chat_ctx.add_message(role="system", content="System")
    chat_ctx.add_message(role="user", content="First message")
    chat_ctx.add_message(role="assistant", content="Response")
    chat_ctx.add_message(role="user", content="Second message")

    # Should get the last user message
    latest = drive_thru_llm._get_latest_user_message(chat_ctx)
    assert latest == "Second message"


def test_get_latest_user_message_no_user_messages(drive_thru_llm):
    """Test getting user message when there are none."""
    chat_ctx = ChatContext()
    chat_ctx.add_message(role="system", content="System")
    chat_ctx.add_message(role="assistant", content="Assistant only")

    latest = drive_thru_llm._get_latest_user_message(chat_ctx)
    assert latest is None or latest == ""
