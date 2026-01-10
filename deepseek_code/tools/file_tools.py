"""File operation tools: read, write, edit."""

import os
from pathlib import Path

from .base import Tool, ToolResult


class ReadFileTool(Tool):
    """Read the contents of a file."""

    name = "read_file"
    description = "Read the contents of a file at the specified path."
    permission_level = "auto"  # Safe - read-only operation

    parameters = {
        "path": {
            "type": "string",
            "description": "The path to the file to read",
            "required": True,
        },
        "limit": {
            "type": "integer",
            "description": "Maximum number of lines to read (default: all)",
            "required": False,
        },
        "offset": {
            "type": "integer",
            "description": "Line number to start reading from (1-indexed, default: 1)",
            "required": False,
        },
    }

    def execute(self, path: str, limit: int | None = None, offset: int = 1) -> ToolResult:
        try:
            # Expand user path and resolve
            file_path = Path(path).expanduser().resolve()

            if not file_path.exists():
                return ToolResult(success=False, output="", error=f"File not found: {path}")

            if not file_path.is_file():
                return ToolResult(success=False, output="", error=f"Not a file: {path}")

            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()

            # Apply offset (convert to 0-indexed)
            start_idx = max(0, offset - 1)
            lines = lines[start_idx:]

            # Apply limit
            if limit and limit > 0:
                lines = lines[:limit]

            # Format with line numbers
            content_lines = []
            for i, line in enumerate(lines, start=start_idx + 1):
                content_lines.append(f"{i:6d}\t{line.rstrip()}")

            content = "\n".join(content_lines)

            return ToolResult(
                success=True,
                output=f"Contents of {path}:\n{content}" if content else f"{path} is empty",
            )

        except PermissionError:
            return ToolResult(success=False, output="", error=f"Permission denied: {path}")
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))


class WriteFileTool(Tool):
    """Write content to a file (create or overwrite)."""

    name = "write_file"
    description = "Write content to a file. Creates the file if it doesn't exist, overwrites if it does."
    permission_level = "ask"  # Needs permission - modifies filesystem

    parameters = {
        "path": {
            "type": "string",
            "description": "The path to the file to write",
            "required": True,
        },
        "content": {
            "type": "string",
            "description": "The content to write to the file",
            "required": True,
        },
    }

    def execute(self, path: str, content: str) -> ToolResult:
        try:
            file_path = Path(path).expanduser().resolve()

            # Create parent directories if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write the file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            return ToolResult(
                success=True,
                output=f"Successfully wrote {len(content)} characters to {path}",
            )

        except PermissionError:
            return ToolResult(success=False, output="", error=f"Permission denied: {path}")
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))


class EditFileTool(Tool):
    """Make surgical edits to a file using string replacement."""

    name = "edit_file"
    description = (
        "Make a precise edit to a file by replacing a unique string with a new string. "
        "The old_str must be unique in the file (appear exactly once)."
    )
    permission_level = "ask"  # Needs permission - modifies filesystem

    parameters = {
        "path": {
            "type": "string",
            "description": "The path to the file to edit",
            "required": True,
        },
        "old_str": {
            "type": "string",
            "description": "The exact string to find and replace (must be unique in the file)",
            "required": True,
        },
        "new_str": {
            "type": "string",
            "description": "The string to replace old_str with",
            "required": True,
        },
    }

    def execute(self, path: str, old_str: str, new_str: str) -> ToolResult:
        try:
            file_path = Path(path).expanduser().resolve()

            if not file_path.exists():
                return ToolResult(success=False, output="", error=f"File not found: {path}")

            if not file_path.is_file():
                return ToolResult(success=False, output="", error=f"Not a file: {path}")

            # Read current content
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Check uniqueness
            count = content.count(old_str)
            if count == 0:
                return ToolResult(
                    success=False,
                    output="",
                    error=f"String not found in file. Make sure old_str exactly matches the file content including whitespace.",
                )
            if count > 1:
                return ToolResult(
                    success=False,
                    output="",
                    error=f"String found {count} times. old_str must be unique. Include more surrounding context to make it unique.",
                )

            # Perform replacement
            new_content = content.replace(old_str, new_str)

            # Write back
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            # Show what changed
            lines_changed = old_str.count("\n") + 1
            return ToolResult(
                success=True,
                output=f"Successfully edited {path} ({lines_changed} line(s) affected)",
            )

        except PermissionError:
            return ToolResult(success=False, output="", error=f"Permission denied: {path}")
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))
