"""Keyword-intercepting LLM wrapper.

This module provides a wrapper LLM that intercepts user input containing
specific keywords and returns a fixed response instead of calling the
underlying LLM. For non-keyword input, it delegates to the wrapped LLM.
"""

from __future__ import annotations

import asyncio
from typing import Any

from livekit.agents.llm import (
    LLM,
    ChatChunk,
    ChatContext,
    ChoiceDelta,
    LLMStream,
    Tool,
    ToolChoice,
)
from livekit.agents.types import (
    DEFAULT_API_CONNECT_OPTIONS,
    NOT_GIVEN,
    APIConnectOptions,
    NotGivenOr,
)
from loguru import logger


class KeywordInterceptLLM(LLM):
    """LLM wrapper that intercepts input containing specific keywords.

    This wrapper checks user input for specified keywords. When a keyword
    is detected, it returns a fixed response instead of calling the wrapped
    LLM. For all other input, it delegates to the wrapped LLM.
    """

    def __init__(
        self,
        wrapped_llm: LLM,
        keywords: list[str] | None = None,
        response_text: str = "I don't like fruit",
    ) -> None:
        """Initialize the keyword-intercepting LLM wrapper.

        Args:
            wrapped_llm: The actual LLM to delegate to when keywords are not detected
            keywords: List of keywords to intercept (case-insensitive).
                     Defaults to fruit-related keywords.
            response_text: Text to return when keywords are detected.
                          Defaults to "I don't like fruit".
        """
        super().__init__()
        self._wrapped_llm = wrapped_llm
        self._keywords = keywords or ["cherries", "cherry", "banana", "apple", "fruit"]
        self._response_text = response_text

        # Convert keywords to lowercase for case-insensitive matching
        self._keywords_lower = [kw.lower() for kw in self._keywords]

        logger.info(
            f"KeywordInterceptLLM initialized with keywords: {self._keywords}, "
            f"response: '{self._response_text}'"
        )

    @property
    def model(self) -> str:
        """Return the wrapped LLM's model identifier."""
        return self._wrapped_llm.model

    @property
    def provider(self) -> str:
        """Return the wrapped LLM's provider identifier."""
        return self._wrapped_llm.provider

    def _get_latest_user_message(self, chat_ctx: ChatContext) -> str:
        """Extract the most recent user message from chat context.

        Args:
            chat_ctx: The chat context containing the conversation history

        Returns:
            The content of the most recent user message, or empty string if none found
        """
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
        return ""

    def _contains_keyword(self, text: str) -> bool:
        """Check if text contains any of the intercepted keywords.

        Args:
            text: The text to check for keywords

        Returns:
            True if any keyword is found (case-insensitive), False otherwise
        """
        text_lower = text.lower()
        for keyword in self._keywords_lower:
            if keyword in text_lower:
                logger.debug(f"Keyword '{keyword}' detected in user input")
                return True
        return False

    def chat(
        self,
        *,
        chat_ctx: ChatContext,
        tools: list[Tool] | None = None,
        conn_options: APIConnectOptions = DEFAULT_API_CONNECT_OPTIONS,
        parallel_tool_calls: NotGivenOr[bool] = NOT_GIVEN,
        tool_choice: NotGivenOr[ToolChoice] = NOT_GIVEN,
        extra_kwargs: NotGivenOr[dict[str, Any]] = NOT_GIVEN,
    ) -> LLMStream:
        """Create a chat stream, intercepting keywords if present.

        Args:
            chat_ctx: The chat context
            tools: Available tools for the LLM
            conn_options: API connection options
            parallel_tool_calls: Whether to allow parallel tool calls
            tool_choice: Tool choice configuration
            extra_kwargs: Additional keyword arguments

        Returns:
            LLMStream that either returns fixed response or delegates to wrapped LLM
        """
        # Extract latest user message
        user_message = self._get_latest_user_message(chat_ctx)

        # Check for keywords
        if self._contains_keyword(user_message):
            logger.info("Keyword detected - returning fixed response")
            return KeywordInterceptStream(
                self,
                chat_ctx=chat_ctx,
                tools=tools or [],
                conn_options=conn_options,
                response_text=self._response_text,
            )
        else:
            logger.debug("No keywords detected - delegating to wrapped LLM")
            return self._wrapped_llm.chat(
                chat_ctx=chat_ctx,
                tools=tools,
                conn_options=conn_options,
                parallel_tool_calls=parallel_tool_calls,
                tool_choice=tool_choice,
                extra_kwargs=extra_kwargs,
            )


class KeywordInterceptStream(LLMStream):
    """Stream implementation for keyword-intercepted responses."""

    def __init__(
        self,
        llm: KeywordInterceptLLM,
        *,
        chat_ctx: ChatContext,
        tools: list[Tool],
        conn_options: APIConnectOptions,
        response_text: str,
    ) -> None:
        """Initialize the keyword intercept stream.

        Args:
            llm: The parent KeywordInterceptLLM instance
            chat_ctx: The chat context
            tools: Available tools
            conn_options: API connection options
            response_text: The fixed response text to stream
        """
        super().__init__(llm, chat_ctx=chat_ctx, tools=tools, conn_options=conn_options)
        self._response_text = response_text

    async def _run(self) -> None:
        """Generate the fixed response by streaming it.

        This simulates a realistic LLM response with a small delay for
        time-to-first-token and then streams the complete response.
        """
        # Simulate a small time-to-first-token delay
        await asyncio.sleep(0.05)

        # Stream the complete response in one chunk
        self._send_chunk(delta=self._response_text)

    def _send_chunk(self, *, delta: str | None = None) -> None:
        """Send a chat chunk with the given content delta.

        Args:
            delta: The text content to send in this chunk
        """
        self._event_ch.send_nowait(
            ChatChunk(
                id=str(id(self)),
                delta=ChoiceDelta(
                    role="assistant",
                    content=delta,
                    tool_calls=[],
                ),
            )
        )
