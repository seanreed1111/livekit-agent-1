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


class SimpleMockLLM(LLM):
    """A simple mock LLM that always returns the same fixed response."""

    def __init__(
        self,
        *,
        response_text: str = "You knew the job was dangerous when you took it, Fred.",
        ttft: float = 0.1,
        chunk_size: int = 5,
    ) -> None:
        """
        Args:
            response_text: The fixed text response to always return
            ttft: Time-to-first-token delay in seconds (simulates thinking time)
            chunk_size: Number of characters per chunk when streaming
        """
        super().__init__()
        self._response_text = response_text
        self._ttft = ttft
        self._chunk_size = chunk_size

    @property
    def model(self) -> str:
        return "mock-llm"

    @property
    def provider(self) -> str:
        return "mock"

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
        return SimpleMockLLMStream(
            self,
            chat_ctx=chat_ctx,
            tools=tools or [],
            conn_options=conn_options,
            response_text=self._response_text,
            ttft=self._ttft,
            chunk_size=self._chunk_size,
        )


class SimpleMockLLMStream(LLMStream):
    """Stream implementation for SimpleMockLLM."""

    def __init__(
        self,
        llm: SimpleMockLLM,
        *,
        chat_ctx: ChatContext,
        tools: list[Tool],
        conn_options: APIConnectOptions,
        response_text: str,
        ttft: float,
        chunk_size: int,
    ) -> None:
        super().__init__(llm, chat_ctx=chat_ctx, tools=tools, conn_options=conn_options)
        self._response_text = response_text
        self._ttft = ttft
        self._chunk_size = chunk_size

    async def _run(self) -> None:
        """Generate the mock response by streaming chunks."""

        # Simulate time-to-first-token delay
        await asyncio.sleep(self._ttft)

        # Stream the response in chunks
        num_chunks = max(1, len(self._response_text) // self._chunk_size + 1)
        for i in range(num_chunks):
            chunk_text = self._response_text[i * self._chunk_size : (i + 1) * self._chunk_size]
            if chunk_text:  # Only send non-empty chunks
                self._send_chunk(delta=chunk_text)

    def _send_chunk(self, *, delta: str | None = None) -> None:
        """Send a chat chunk with the given content delta."""
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
