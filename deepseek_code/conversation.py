"""Conversation history management."""

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class ConversationHistory:
    """Manages conversation message history."""

    messages: list[dict[str, Any]] = field(default_factory=list)
    system_prompt: str = ""
    max_messages: int = 100  # Soft limit before compaction suggestion

    def add_user_message(self, content: str) -> None:
        """Add a user message."""
        self.messages.append({"role": "user", "content": content})

    def add_assistant_message(self, message: dict[str, Any]) -> None:
        """Add an assistant message (may include tool_calls)."""
        self.messages.append(message)

    def add_tool_result(self, tool_call_id: str, result: str) -> None:
        """Add a tool result message."""
        self.messages.append({
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": result,
        })

    def add_tool_results(self, results: list[dict[str, Any]]) -> None:
        """Add multiple tool results."""
        for result in results:
            self.messages.append(result)

    def get_messages_for_api(self) -> list[dict[str, Any]]:
        """Get messages formatted for API call."""
        return self.messages.copy()

    def get_full_context(self) -> list[dict[str, Any]]:
        """Get full context including system prompt."""
        result = []
        if self.system_prompt:
            result.append({"role": "system", "content": self.system_prompt})
        result.extend(self.messages)
        return result

    def clear(self) -> None:
        """Clear conversation history."""
        self.messages = []

    def needs_compaction(self) -> bool:
        """Check if conversation is getting long."""
        return len(self.messages) > self.max_messages

    @property
    def message_count(self) -> int:
        """Get number of messages."""
        return len(self.messages)


class ConversationStore:
    """Persists conversations to disk."""

    def __init__(self, storage_dir: str | None = None):
        if storage_dir:
            self.storage_dir = Path(storage_dir)
        else:
            self.storage_dir = Path.home() / ".deepseek-code" / "history"

        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save(self, history: ConversationHistory, session_id: str | None = None) -> str:
        """
        Save conversation history.

        Args:
            history: ConversationHistory to save
            session_id: Optional session ID (generates timestamp if not provided)

        Returns:
            Session ID used for saving
        """
        if session_id is None:
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        file_path = self.storage_dir / f"{session_id}.json"

        data = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "system_prompt": history.system_prompt,
            "messages": history.messages,
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return session_id

    def load(self, session_id: str) -> ConversationHistory | None:
        """
        Load conversation history.

        Args:
            session_id: Session ID to load

        Returns:
            ConversationHistory or None if not found
        """
        file_path = self.storage_dir / f"{session_id}.json"

        if not file_path.exists():
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            history = ConversationHistory(
                messages=data.get("messages", []),
                system_prompt=data.get("system_prompt", ""),
            )
            return history

        except (json.JSONDecodeError, KeyError):
            return None

    def list_sessions(self, limit: int = 20) -> list[dict[str, str]]:
        """
        List recent sessions.

        Returns:
            List of session info dicts with 'id' and 'timestamp'
        """
        sessions = []

        for file_path in sorted(self.storage_dir.glob("*.json"), reverse=True)[:limit]:
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
                sessions.append({
                    "id": file_path.stem,
                    "timestamp": data.get("timestamp", "unknown"),
                })
            except Exception:
                continue

        return sessions

    def delete(self, session_id: str) -> bool:
        """Delete a session."""
        file_path = self.storage_dir / f"{session_id}.json"
        if file_path.exists():
            file_path.unlink()
            return True
        return False


def compact_conversation(
    history: ConversationHistory,
    client: Any,  # DeepSeekClient
    keep_recent: int = 10,
) -> ConversationHistory:
    """
    Compact a conversation by summarizing older messages.

    Args:
        history: Original conversation history
        client: DeepSeek client for summarization
        keep_recent: Number of recent messages to keep intact

    Returns:
        New ConversationHistory with compacted messages
    """
    if len(history.messages) <= keep_recent:
        return history

    # Split messages
    old_messages = history.messages[:-keep_recent]
    recent_messages = history.messages[-keep_recent:]

    # Create summary prompt
    summary_prompt = """Summarize this conversation concisely, preserving:
- The original task/goal
- Key findings and decisions made
- Important file paths and changes
- Current state of the work
- What still needs to be done

Format as a brief summary paragraph."""

    # Build messages for summary
    summary_messages = [
        {"role": "system", "content": summary_prompt},
        {"role": "user", "content": json.dumps(old_messages, indent=2)},
    ]

    # Get summary
    response = client.chat(summary_messages, tools=None, max_tokens=1000)

    # Build new history
    new_history = ConversationHistory(system_prompt=history.system_prompt)

    # Add summary as context
    if response.content:
        new_history.add_user_message(
            f"[Previous conversation summary]\n{response.content}\n\n[Continuing conversation...]"
        )

    # Add recent messages
    new_history.messages.extend(recent_messages)

    return new_history
