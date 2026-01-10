"""Context management for project-specific configuration."""

import os
import subprocess
from pathlib import Path
from dataclasses import dataclass


@dataclass
class ProjectContext:
    """Context information about the current project."""

    working_dir: str
    deepseek_md: str | None = None
    git_branch: str | None = None
    git_repo: bool = False


def find_project_root(start_path: str = ".") -> Path:
    """
    Find the project root by looking for common indicators.

    Looks for (in order):
    1. .git directory
    2. DEEPSEEK.md file
    3. pyproject.toml
    4. package.json
    5. Cargo.toml
    """
    current = Path(start_path).resolve()

    indicators = [".git", "DEEPSEEK.md", "pyproject.toml", "package.json", "Cargo.toml"]

    while current != current.parent:
        for indicator in indicators:
            if (current / indicator).exists():
                return current
        current = current.parent

    # Fallback to start path
    return Path(start_path).resolve()


def load_deepseek_md(project_root: Path) -> str | None:
    """Load DEEPSEEK.md content if it exists."""
    md_path = project_root / "DEEPSEEK.md"

    if md_path.exists():
        try:
            with open(md_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            return None

    return None


def get_git_branch(project_root: Path) -> str | None:
    """Get the current git branch name."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def is_git_repo(project_root: Path) -> bool:
    """Check if the directory is a git repository."""
    return (project_root / ".git").exists()


def get_project_context(working_dir: str = ".") -> ProjectContext:
    """
    Get full project context.

    Args:
        working_dir: Starting directory (default: current directory)

    Returns:
        ProjectContext with all gathered information
    """
    project_root = find_project_root(working_dir)

    return ProjectContext(
        working_dir=str(project_root),
        deepseek_md=load_deepseek_md(project_root),
        git_branch=get_git_branch(project_root),
        git_repo=is_git_repo(project_root),
    )


def build_system_prompt(context: ProjectContext, tools_description: str = "") -> str:
    """
    Build the system prompt with context.

    Args:
        context: Project context
        tools_description: Optional description of available tools

    Returns:
        Complete system prompt
    """
    parts = []

    # Base instructions
    parts.append("""You are DeepSeek Code, an AI coding assistant that helps with software development tasks.

You have access to tools that let you read files, write files, edit files, run commands, and search the codebase.

## Guidelines

### Before making changes:
1. Understand the task fully before acting
2. Read relevant files to understand context
3. Plan your approach

### When editing code:
1. Use edit_file for small changes (preferred) - it's more precise
2. Use write_file only for new files or complete rewrites
3. Run tests after changes when possible
4. If tests fail, analyze the error and iterate

### General principles:
- Be concise but thorough
- Explain your reasoning briefly
- Ask for clarification if the task is ambiguous
- If you're stuck, say so instead of guessing
- Don't make unnecessary changes to files
- Preserve existing code style and conventions""")

    # Add working directory
    parts.append(f"\n## Working Directory\n{context.working_dir}")

    # Add git info
    if context.git_repo:
        branch_info = f" (branch: {context.git_branch})" if context.git_branch else ""
        parts.append(f"\n## Git Repository\nThis is a git repository{branch_info}.")

    # Add DEEPSEEK.md content
    if context.deepseek_md:
        parts.append(f"\n## Project Context (from DEEPSEEK.md)\n\n{context.deepseek_md}")

    return "\n".join(parts)
