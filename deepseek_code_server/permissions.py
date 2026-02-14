"""Permission system for tool execution."""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class PermissionLevel(Enum):
    """Permission levels for operations."""

    AUTO = "auto"  # Automatically allowed (safe operations)
    ASK = "ask"  # Requires user confirmation
    DENY = "deny"  # Blocked entirely


@dataclass
class PermissionRequest:
    """A request for permission to perform an action."""

    tool_name: str
    tool_input: dict[str, Any]
    level: PermissionLevel
    reason: str | None = None


@dataclass
class PermissionResult:
    """Result of a permission check."""

    allowed: bool
    reason: str | None = None


class PermissionManager:
    """Manages permissions for tool execution."""

    # Patterns for dangerous bash commands
    DANGEROUS_BASH_PATTERNS = [
        (r"rm\s+-rf?\s+/", "Recursive delete from root"),
        (r"rm\s+-rf?\s+~", "Recursive delete from home"),
        (r"rm\s+-rf?\s+\*", "Recursive delete with wildcard"),
        (r"sudo\s+", "Sudo command"),
        (r"chmod\s+777", "World-writable permissions"),
        (r">\s*/dev/sd", "Write to disk device"),
        (r"\|\s*sh\s*$", "Piping to shell"),
        (r"\|\s*bash\s*$", "Piping to bash"),
        (r"curl.*\|\s*(sh|bash)", "Curl piping to shell"),
        (r"wget.*\|\s*(sh|bash)", "Wget piping to shell"),
        (r":()\s*{\s*:\|:&\s*}", "Fork bomb"),
        (r"mkfs\.", "Filesystem format"),
    ]

    # Commands that are completely blocked
    BLOCKED_COMMANDS = [
        "rm -rf /",
        "rm -rf /*",
        "dd if=/dev/zero of=/dev/sda",
    ]

    def __init__(self, trust_mode: bool = False, yolo_mode: bool = False):
        """
        Initialize permission manager.

        Args:
            trust_mode: If True, auto-approve all non-blocked operations
            yolo_mode: If True, skip ALL permission prompts (like Claude Code's --dangerously-skip-permissions)
        """
        self.trust_mode = trust_mode
        self.yolo_mode = yolo_mode
        self.session_allowlist: set[str] = set()  # Patterns to auto-allow
        self.session_denylist: set[str] = set()  # Patterns to auto-deny

    def add_to_allowlist(self, pattern: str) -> None:
        """Add a pattern to the session allowlist."""
        self.session_allowlist.add(pattern)

    def add_to_denylist(self, pattern: str) -> None:
        """Add a pattern to the session denylist."""
        self.session_denylist.add(pattern)

    def _check_bash_command(self, command: str) -> tuple[PermissionLevel, str | None]:
        """Check permission level for a bash command."""
        # Check blocked commands
        cmd_lower = command.lower().strip()
        for blocked in self.BLOCKED_COMMANDS:
            if blocked in cmd_lower:
                return PermissionLevel.DENY, f"Blocked command: {blocked}"

        # Check dangerous patterns
        for pattern, reason in self.DANGEROUS_BASH_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                return PermissionLevel.DENY, f"Dangerous pattern: {reason}"

        # Check session allowlist
        for allowed in self.session_allowlist:
            if allowed.startswith("bash(") and allowed.endswith(")"):
                # Pattern like "bash(npm test:*)"
                allowed_pattern = allowed[5:-1]
                if self._matches_pattern(command, allowed_pattern):
                    return PermissionLevel.AUTO, None

        # Check session denylist
        for denied in self.session_denylist:
            if denied.startswith("bash(") and denied.endswith(")"):
                denied_pattern = denied[5:-1]
                if self._matches_pattern(command, denied_pattern):
                    return PermissionLevel.DENY, "Denied by session rule"

        # Default: ask
        return PermissionLevel.ASK, None

    def _matches_pattern(self, text: str, pattern: str) -> bool:
        """Check if text matches a simple wildcard pattern."""
        # Convert simple wildcard pattern to regex
        regex_pattern = pattern.replace("*", ".*").replace("?", ".")
        return bool(re.match(regex_pattern, text))

    def check_permission(
        self, tool_name: str, tool_input: dict[str, Any]
    ) -> PermissionRequest:
        """
        Check what permission level is needed for a tool call.

        Returns a PermissionRequest indicating the required level.
        """
        # YOLO mode: auto-approve everything except truly dangerous commands
        if self.yolo_mode:
            # Still check for blocked bash commands
            if tool_name == "bash":
                command = tool_input.get("command", "")
                level, reason = self._check_bash_command(command)
                if level == PermissionLevel.DENY:
                    return PermissionRequest(
                        tool_name=tool_name,
                        tool_input=tool_input,
                        level=level,
                        reason=reason,
                    )
            # Auto-approve everything else in YOLO mode
            return PermissionRequest(
                tool_name=tool_name,
                tool_input=tool_input,
                level=PermissionLevel.AUTO,
            )

        # Read-only operations are always safe
        if tool_name in ("read_file", "glob", "grep"):
            return PermissionRequest(
                tool_name=tool_name,
                tool_input=tool_input,
                level=PermissionLevel.AUTO,
            )

        # File modifications need permission
        if tool_name in ("write_file", "edit_file"):
            path = tool_input.get("path", "")

            # Check session lists
            for allowed in self.session_allowlist:
                if allowed.startswith("write(") and allowed.endswith(")"):
                    allowed_pattern = allowed[6:-1]
                    if self._matches_pattern(path, allowed_pattern):
                        return PermissionRequest(
                            tool_name=tool_name,
                            tool_input=tool_input,
                            level=PermissionLevel.AUTO,
                        )

            return PermissionRequest(
                tool_name=tool_name,
                tool_input=tool_input,
                level=PermissionLevel.ASK if not self.trust_mode else PermissionLevel.AUTO,
            )

        # Bash commands need careful checking
        if tool_name == "bash":
            command = tool_input.get("command", "")
            level, reason = self._check_bash_command(command)

            # Trust mode doesn't override DENY
            if level == PermissionLevel.ASK and self.trust_mode:
                level = PermissionLevel.AUTO

            return PermissionRequest(
                tool_name=tool_name,
                tool_input=tool_input,
                level=level,
                reason=reason,
            )

        # Unknown tools default to ASK
        return PermissionRequest(
            tool_name=tool_name,
            tool_input=tool_input,
            level=PermissionLevel.ASK if not self.trust_mode else PermissionLevel.AUTO,
        )

    def format_permission_prompt(self, request: PermissionRequest) -> str:
        """Format a human-readable permission prompt."""
        tool_name = request.tool_name
        tool_input = request.tool_input

        if tool_name == "bash":
            return f"Run command: {tool_input.get('command', '')}"
        elif tool_name == "write_file":
            return f"Write to file: {tool_input.get('path', '')}"
        elif tool_name == "edit_file":
            return f"Edit file: {tool_input.get('path', '')}"
        else:
            return f"{tool_name}: {tool_input}"
