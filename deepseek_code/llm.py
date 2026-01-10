"""DeepSeek API client using OpenAI-compatible interface."""

import os
from dataclasses import dataclass, field
from typing import Any

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageToolCall
from pydantic import BaseModel


@dataclass
class ToolCall:
    """Represents a tool call from the LLM."""

    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class LLMResponse:
    """Response from the LLM."""

    content: str | None
    tool_calls: list[ToolCall] = field(default_factory=list)
    finish_reason: str = "stop"
    usage: dict[str, int] = field(default_factory=dict)

    @property
    def has_tool_calls(self) -> bool:
        return len(self.tool_calls) > 0


class DeepSeekClient:
    """Client for DeepSeek API using OpenAI SDK."""

    DEFAULT_MODEL = "deepseek-chat"
    DEFAULT_BASE_URL = "https://api.deepseek.com"

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
    ):
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError(
                "DeepSeek API key required. Set DEEPSEEK_API_KEY environment variable "
                "or pass api_key parameter."
            )

        self.model = model or os.environ.get("DEEPSEEK_MODEL", self.DEFAULT_MODEL)
        self.base_url = base_url or os.environ.get("DEEPSEEK_BASE_URL", self.DEFAULT_BASE_URL)

        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        self.total_tokens_used = 0

    def _parse_tool_calls(
        self, tool_calls: list[ChatCompletionMessageToolCall] | None
    ) -> list[ToolCall]:
        """Parse OpenAI tool calls into our ToolCall format."""
        if not tool_calls:
            return []

        import json

        result = []
        for tc in tool_calls:
            try:
                args = json.loads(tc.function.arguments)
            except json.JSONDecodeError:
                args = {"raw": tc.function.arguments}

            result.append(
                ToolCall(
                    id=tc.id,
                    name=tc.function.name,
                    arguments=args,
                )
            )
        return result

    def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.0,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        """Send a chat request to DeepSeek.

        Args:
            messages: List of message dicts with 'role' and 'content'
            tools: Optional list of tool definitions in OpenAI format
            temperature: Sampling temperature (0.0 = deterministic)
            max_tokens: Maximum tokens in response

        Returns:
            LLMResponse with content and/or tool calls
        """
        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        response = self.client.chat.completions.create(**kwargs)

        # Track usage
        if response.usage:
            self.total_tokens_used += response.usage.total_tokens
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }
        else:
            usage = {}

        choice = response.choices[0]
        message = choice.message

        return LLMResponse(
            content=message.content,
            tool_calls=self._parse_tool_calls(message.tool_calls),
            finish_reason=choice.finish_reason or "stop",
            usage=usage,
        )

    def format_tool_result(self, tool_call_id: str, result: str) -> dict[str, Any]:
        """Format a tool result message for the conversation."""
        return {
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": result,
        }

    def format_assistant_message(self, response: LLMResponse) -> dict[str, Any]:
        """Format an assistant response for the conversation history."""
        message: dict[str, Any] = {"role": "assistant"}

        if response.content:
            message["content"] = response.content

        if response.tool_calls:
            message["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.name,
                        "arguments": __import__("json").dumps(tc.arguments),
                    },
                }
                for tc in response.tool_calls
            ]

        return message


# Convenience function to create a client
def get_client(**kwargs) -> DeepSeekClient:
    """Create a DeepSeek client with optional overrides."""
    return DeepSeekClient(**kwargs)
