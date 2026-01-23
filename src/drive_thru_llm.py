"""DriveThruLLM - Context injection wrapper for menu-aware LLM.

This module provides a stateless LLM wrapper that intercepts chat calls to inject
relevant menu context based on keywords extracted from user messages. This helps
ground the LLM in actual menu items and reduces hallucination.
"""

from typing import Any

from livekit.agents.llm import LLM, ChatContext, LLMStream

from menus.mcdonalds.models import Item
from menu_provider import MenuProvider


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
        max_context_items: int = 50,
    ) -> None:
        """Initialize wrapper.

        Args:
            wrapped_llm: The LLM to wrap (e.g., OpenAI GPT-4.1)
            menu_provider: MenuProvider for menu queries
            max_context_items: Max number of menu items to inject (default: 50)
        """
        super().__init__()
        self._wrapped_llm = wrapped_llm
        self._menu_provider = menu_provider
        self._max_context_items = max_context_items

    async def chat(
        self,
        *,
        chat_ctx: ChatContext,
        tools: list[Any] | None = None,
        **kwargs: Any,
    ) -> LLMStream:
        """Intercept chat to inject menu context.

        Flow:
        1. Extract keywords from latest user message
        2. Search for relevant menu items
        3. Inject items into chat_ctx
        4. Delegate to wrapped_llm.chat()

        Args:
            chat_ctx: The chat context
            tools: Optional list of tools for the LLM
            **kwargs: Additional arguments to pass to wrapped LLM

        Returns:
            LLMStream from wrapped LLM
        """
        # 1. Extract keywords from latest user message
        latest_message = self._get_latest_user_message(chat_ctx)
        augmented_ctx = chat_ctx

        if latest_message:
            keywords = self._extract_keywords(latest_message)

            if keywords:  # Only search if we have keywords
                # 2. Search for relevant menu items
                relevant_items = self._find_relevant_items(keywords)

                # 3. Inject into context
                if relevant_items:
                    augmented_ctx = self._inject_menu_context(chat_ctx, relevant_items)

        # 4. Delegate to wrapped LLM
        return await self._wrapped_llm.chat(
            chat_ctx=augmented_ctx, tools=tools, **kwargs
        )

    def _get_latest_user_message(self, chat_ctx: ChatContext) -> str | None:
        """Get the latest user message from chat context.

        Args:
            chat_ctx: The chat context

        Returns:
            Latest user message content, or None if no user messages exist
        """
        # Iterate in reverse to find the last user message
        for item in reversed(chat_ctx.items):
            if (
                hasattr(item, "role")
                and item.role == "user"
                and hasattr(item, "content")
            ):
                # Extract text content from the item
                # Content might be a list of content parts or a string
                content = item.content
                if isinstance(content, list):
                    # Join all text parts
                    text_parts = []
                    for part in content:
                        if hasattr(part, "text"):
                            text_parts.append(part.text)
                        elif isinstance(part, str):
                            text_parts.append(part)
                    return " ".join(text_parts)
                elif isinstance(content, str):
                    return content

        return None

    def _extract_keywords(self, message: str) -> list[str]:
        """Extract potential menu-related keywords from user message.

        Simple approach: Split on spaces, filter stopwords, lowercase.

        Args:
            message: User's message text

        Returns:
            List of keywords to search

        Examples:
            "I want a Big Mac" → ["big", "mac"]
            "Two cheeseburgers please" → ["two", "cheeseburgers", "please"]
        """
        if not message:
            return []

        # Lowercase and split
        words = message.lower().split()

        # Remove common stopwords
        stopwords = {
            "i",
            "want",
            "a",
            "an",
            "the",
            "please",
            "thanks",
            "and",
            "with",
        }
        keywords = [w for w in words if w not in stopwords]

        return keywords

    def _find_relevant_items(self, keywords: list[str]) -> list[Item]:
        """Find menu items matching keywords.

        Args:
            keywords: List of keywords to search

        Returns:
            List of relevant menu items (up to max_context_items)

        Strategy:
            - Search for each keyword
            - Deduplicate results
            - Limit to max_context_items
        """
        all_matches: list[Item] = []
        seen_items: set[str] = set()

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

    def _inject_menu_context(
        self, chat_ctx: ChatContext, items: list[Item]
    ) -> ChatContext:
        """Inject menu items into chat context.

        Strategy: Add a system message with relevant menu items.

        Args:
            chat_ctx: Original chat context
            items: Relevant menu items to inject

        Returns:
            New ChatContext with injected menu items
        """
        # Format items for injection
        items_text = self._format_items_for_context(items)

        # Create a new context and rebuild with menu context injected
        new_ctx = ChatContext()

        # Helper function to extract text from content
        def get_text_content(content: Any) -> str:
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                text_parts = []
                for part in content:
                    if hasattr(part, "text"):
                        text_parts.append(part.text)
                    elif isinstance(part, str):
                        text_parts.append(part)
                return " ".join(text_parts)
            return ""

        # Add items in order: first item, then menu context, then rest
        for i, item in enumerate(chat_ctx.items):
            if i == 0:
                # Add the first message (usually system prompt)
                new_ctx.add_message(
                    role=item.role,
                    content=get_text_content(item.content),
                )
                # After first message, inject menu context
                new_ctx.add_message(
                    role="system",
                    content=f"Relevant menu items:\n{items_text}",
                )
            else:
                # Add remaining messages
                new_ctx.add_message(
                    role=item.role,
                    content=get_text_content(item.content),
                )

        return new_ctx

    def _format_items_for_context(self, items: list[Item]) -> str:
        """Format menu items for LLM context.

        Args:
            items: List of menu items

        Returns:
            Formatted string of items

        Example:
            "- Big Mac (Beef & Pork)
             - Quarter Pounder (Beef & Pork)
             - Egg McMuffin (Breakfast)"
        """
        if not items:
            return ""

        lines = []
        for item in items:
            # Group by category for clarity
            lines.append(f"- {item.item_name} ({item.category_name})")

            # Optionally include modifiers
            if item.modifiers:
                modifier_names = [m.modifier_name for m in item.modifiers]
                lines.append(f"  Modifiers: {', '.join(modifier_names)}")

        return "\n".join(lines)
