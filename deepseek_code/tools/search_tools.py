"""Search tools: glob and grep."""

import fnmatch
import os
import re
from pathlib import Path

from .base import Tool, ToolResult


class GlobTool(Tool):
    """Find files matching a pattern."""

    name = "glob"
    description = (
        "Find files matching a glob pattern. "
        "Supports ** for recursive matching (e.g., '**/*.py' finds all Python files)."
    )
    permission_level = "auto"  # Safe - read-only operation

    parameters = {
        "pattern": {
            "type": "string",
            "description": "Glob pattern to match (e.g., '**/*.py', 'src/**/*.ts')",
            "required": True,
        },
        "path": {
            "type": "string",
            "description": "Base directory to search in (default: current directory)",
            "required": False,
        },
        "limit": {
            "type": "integer",
            "description": "Maximum number of results to return (default: 100)",
            "required": False,
        },
    }

    # Directories to skip
    SKIP_DIRS = {
        ".git",
        "node_modules",
        "__pycache__",
        ".venv",
        "venv",
        ".env",
        "dist",
        "build",
        ".next",
        ".cache",
        "target",  # Rust
    }

    def execute(
        self, pattern: str, path: str = ".", limit: int = 100
    ) -> ToolResult:
        try:
            base_path = Path(path).expanduser().resolve()

            if not base_path.exists():
                return ToolResult(
                    success=False, output="", error=f"Path not found: {path}"
                )

            matches = []

            # Use pathlib's glob for pattern matching
            for match in base_path.glob(pattern):
                # Skip directories we don't care about
                parts = match.parts
                if any(skip in parts for skip in self.SKIP_DIRS):
                    continue

                # Only include files
                if match.is_file():
                    try:
                        rel_path = match.relative_to(base_path)
                        matches.append(str(rel_path))
                    except ValueError:
                        matches.append(str(match))

                if len(matches) >= limit:
                    break

            # Sort by modification time (most recent first)
            def get_mtime(p: str) -> float:
                try:
                    return (base_path / p).stat().st_mtime
                except:
                    return 0

            matches.sort(key=get_mtime, reverse=True)

            if not matches:
                return ToolResult(
                    success=True,
                    output=f"No files found matching '{pattern}' in {path}",
                )

            result = f"Found {len(matches)} file(s) matching '{pattern}':\n"
            result += "\n".join(f"  {m}" for m in matches)

            if len(matches) >= limit:
                result += f"\n  ... (limited to {limit} results)"

            return ToolResult(success=True, output=result)

        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))


class GrepTool(Tool):
    """Search for patterns in file contents."""

    name = "grep"
    description = (
        "Search for a regex pattern in files. "
        "Returns matching lines with file paths and line numbers."
    )
    permission_level = "auto"  # Safe - read-only operation

    parameters = {
        "pattern": {
            "type": "string",
            "description": "Regex pattern to search for",
            "required": True,
        },
        "path": {
            "type": "string",
            "description": "File or directory to search in (default: current directory)",
            "required": False,
        },
        "include": {
            "type": "string",
            "description": "Glob pattern for files to include (e.g., '*.py', default: '*')",
            "required": False,
        },
        "ignore_case": {
            "type": "boolean",
            "description": "Case-insensitive search (default: false)",
            "required": False,
        },
        "limit": {
            "type": "integer",
            "description": "Maximum number of matches to return (default: 50)",
            "required": False,
        },
    }

    # Directories to skip
    SKIP_DIRS = {
        ".git",
        "node_modules",
        "__pycache__",
        ".venv",
        "venv",
        ".env",
        "dist",
        "build",
        ".next",
        ".cache",
        "target",
    }

    # Binary file extensions to skip
    BINARY_EXTENSIONS = {
        ".png", ".jpg", ".jpeg", ".gif", ".ico", ".webp",
        ".pdf", ".doc", ".docx", ".xls", ".xlsx",
        ".zip", ".tar", ".gz", ".rar", ".7z",
        ".exe", ".dll", ".so", ".dylib",
        ".pyc", ".pyo", ".class",
        ".woff", ".woff2", ".ttf", ".eot",
        ".mp3", ".mp4", ".wav", ".avi", ".mov",
    }

    def execute(
        self,
        pattern: str,
        path: str = ".",
        include: str = "*",
        ignore_case: bool = False,
        limit: int = 50,
    ) -> ToolResult:
        try:
            base_path = Path(path).expanduser().resolve()

            if not base_path.exists():
                return ToolResult(
                    success=False, output="", error=f"Path not found: {path}"
                )

            # Compile regex
            flags = re.IGNORECASE if ignore_case else 0
            try:
                regex = re.compile(pattern, flags)
            except re.error as e:
                return ToolResult(
                    success=False, output="", error=f"Invalid regex pattern: {e}"
                )

            matches = []

            # Get files to search
            if base_path.is_file():
                files_to_search = [base_path]
            else:
                # Use glob to find files
                files_to_search = list(base_path.glob(f"**/{include}"))

            for file_path in files_to_search:
                if not file_path.is_file():
                    continue

                # Skip directories we don't care about
                if any(skip in file_path.parts for skip in self.SKIP_DIRS):
                    continue

                # Skip binary files
                if file_path.suffix.lower() in self.BINARY_EXTENSIONS:
                    continue

                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        for line_num, line in enumerate(f, 1):
                            if regex.search(line):
                                try:
                                    rel_path = file_path.relative_to(base_path)
                                except ValueError:
                                    rel_path = file_path

                                matches.append({
                                    "file": str(rel_path),
                                    "line": line_num,
                                    "content": line.rstrip()[:200],  # Truncate long lines
                                })

                                if len(matches) >= limit:
                                    break

                except (IOError, UnicodeDecodeError):
                    continue

                if len(matches) >= limit:
                    break

            if not matches:
                return ToolResult(
                    success=True,
                    output=f"No matches found for '{pattern}' in {path}",
                )

            result = f"Found {len(matches)} match(es) for '{pattern}':\n\n"
            for m in matches:
                result += f"{m['file']}:{m['line']}: {m['content']}\n"

            if len(matches) >= limit:
                result += f"\n... (limited to {limit} results)"

            return ToolResult(success=True, output=result)

        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))
