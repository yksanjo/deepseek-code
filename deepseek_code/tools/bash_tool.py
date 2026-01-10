"""Bash command execution tool."""

import subprocess
import shlex
from typing import Any

from .base import Tool, ToolResult


class BashTool(Tool):
    """Execute bash commands."""

    name = "bash"
    description = (
        "Execute a bash command in the shell. Use for running scripts, "
        "git commands, package managers, build tools, etc."
    )
    permission_level = "ask"  # Most commands need permission

    parameters = {
        "command": {
            "type": "string",
            "description": "The bash command to execute",
            "required": True,
        },
        "timeout": {
            "type": "integer",
            "description": "Timeout in seconds (default: 120)",
            "required": False,
        },
    }

    # Patterns that indicate very dangerous commands
    BLOCKED_PATTERNS = [
        "rm -rf /",
        "rm -rf /*",
        ":(){ :|:& };:",  # Fork bomb
        "> /dev/sda",
        "dd if=/dev/zero of=/dev/",
        "mkfs.",
    ]

    # Patterns that require extra caution
    DANGEROUS_PATTERNS = [
        r"rm\s+-rf?",
        r"sudo\s+",
        r"chmod\s+777",
        r">\s*/dev/",
        r"\|\s*sh",
        r"\|\s*bash",
        r"curl.*\|.*sh",
        r"wget.*\|.*sh",
        r"mv\s+/",
        r"cp\s+.*\s+/",
    ]

    def is_blocked(self, command: str) -> bool:
        """Check if command is completely blocked."""
        cmd_lower = command.lower()
        return any(pattern in cmd_lower for pattern in self.BLOCKED_PATTERNS)

    def is_dangerous(self, command: str) -> bool:
        """Check if command matches dangerous patterns."""
        import re

        return any(re.search(pattern, command) for pattern in self.DANGEROUS_PATTERNS)

    def execute(self, command: str, timeout: int = 120) -> ToolResult:
        # Check for blocked commands
        if self.is_blocked(command):
            return ToolResult(
                success=False,
                output="",
                error="This command is blocked for safety reasons.",
            )

        try:
            # Run the command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=None,  # Use current working directory
                env=None,  # Inherit environment
            )

            # Combine stdout and stderr
            output_parts = []
            if result.stdout:
                output_parts.append(result.stdout)
            if result.stderr:
                output_parts.append(result.stderr)

            output = "\n".join(output_parts).strip()

            # Truncate very long output
            max_len = 50000
            if len(output) > max_len:
                output = output[:max_len] + f"\n... (output truncated, {len(output)} total chars)"

            if result.returncode == 0:
                return ToolResult(
                    success=True,
                    output=f"$ {command}\n{output}" if output else f"$ {command}\n(no output)",
                )
            else:
                return ToolResult(
                    success=False,
                    output=f"$ {command}\n{output}",
                    error=f"Command exited with code {result.returncode}",
                )

        except subprocess.TimeoutExpired:
            return ToolResult(
                success=False,
                output="",
                error=f"Command timed out after {timeout} seconds",
            )
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))
