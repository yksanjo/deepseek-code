"""Rich terminal UI components."""

import json
from typing import Any

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.syntax import Syntax
from rich.theme import Theme
from rich.text import Text
from rich.live import Live
from rich.spinner import Spinner


# Custom theme
THEME = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "red bold",
    "success": "green",
    "tool": "blue",
    "path": "magenta",
})

console = Console(theme=THEME)


def print_welcome(version: str, working_dir: str, context_loaded: bool = False) -> None:
    """Print welcome message."""
    console.print(f"\n[bold cyan]DeepSeek Code[/bold cyan] v{version}")
    console.print(f"Working directory: [path]{working_dir}[/path]")
    if context_loaded:
        console.print("[success]Loaded context from DEEPSEEK.md[/success]")
    console.print()


def print_assistant_message(content: str) -> None:
    """Print assistant's text response with markdown rendering."""
    if content:
        md = Markdown(content)
        console.print(md)
        console.print()


def print_tool_call(tool_name: str, tool_input: dict[str, Any]) -> None:
    """Print a tool call being made."""
    icon = get_tool_icon(tool_name)

    if tool_name == "bash":
        cmd = tool_input.get("command", "")
        console.print(f"{icon} [tool]bash[/tool]: {cmd}")
    elif tool_name == "read_file":
        path = tool_input.get("path", "")
        console.print(f"{icon} [tool]read_file[/tool]: [path]{path}[/path]")
    elif tool_name == "write_file":
        path = tool_input.get("path", "")
        console.print(f"{icon} [tool]write_file[/tool]: [path]{path}[/path]")
    elif tool_name == "edit_file":
        path = tool_input.get("path", "")
        old_preview = tool_input.get("old_str", "")[:50]
        console.print(f"{icon} [tool]edit_file[/tool]: [path]{path}[/path]")
        if old_preview:
            console.print(f"   old: \"{old_preview}...\"")
    elif tool_name == "glob":
        pattern = tool_input.get("pattern", "")
        console.print(f"{icon} [tool]glob[/tool]: {pattern}")
    elif tool_name == "grep":
        pattern = tool_input.get("pattern", "")
        path = tool_input.get("path", ".")
        console.print(f"{icon} [tool]grep[/tool]: '{pattern}' in [path]{path}[/path]")
    else:
        console.print(f"{icon} [tool]{tool_name}[/tool]: {json.dumps(tool_input)}")


def get_tool_icon(tool_name: str) -> str:
    """Get icon for a tool."""
    icons = {
        "read_file": "[cyan]>[/cyan]",
        "write_file": "[yellow]>[/yellow]",
        "edit_file": "[yellow]>[/yellow]",
        "bash": "[green]$[/green]",
        "glob": "[blue]>[/blue]",
        "grep": "[blue]>[/blue]",
    }
    return icons.get(tool_name, "[white]>[/white]")


def print_tool_result(result: str, success: bool = True, truncate: int = 500) -> None:
    """Print tool execution result."""
    if not result:
        return

    # Truncate for display
    display = result
    if len(result) > truncate:
        display = result[:truncate] + f"\n... ({len(result)} chars total)"

    if success:
        # Indent the output
        lines = display.split("\n")
        for line in lines:
            console.print(f"   {line}", highlight=False)
    else:
        console.print(f"   [error]{display}[/error]")


def print_error(message: str) -> None:
    """Print an error message."""
    console.print(f"[error]Error: {message}[/error]")


def print_success(message: str) -> None:
    """Print a success message."""
    console.print(f"[success]{message}[/success]")


def print_warning(message: str) -> None:
    """Print a warning message."""
    console.print(f"[warning]{message}[/warning]")


def print_info(message: str) -> None:
    """Print an info message."""
    console.print(f"[info]{message}[/info]")


def ask_permission(prompt: str, options: list[str] = None) -> str:
    """
    Ask user for permission.

    Args:
        prompt: The permission prompt to show
        options: List of options (default: y/n/always)

    Returns:
        User's choice as a string
    """
    if options is None:
        options = ["y", "n", "always"]

    options_str = "/".join(options)
    console.print(f"\n[warning]Permission required:[/warning] {prompt}")

    while True:
        choice = Prompt.ask(f"Allow? [{options_str}]", default="n").lower().strip()

        # Handle common inputs
        if choice in ("y", "yes"):
            return "y"
        elif choice in ("n", "no"):
            return "n"
        elif choice in ("a", "always"):
            return "always"
        elif choice in options:
            return choice
        else:
            console.print(f"Please enter one of: {options_str}")


def get_user_input(prompt: str = "> ") -> str:
    """Get input from user with nice prompt."""
    try:
        return Prompt.ask(f"[bold cyan]{prompt}[/bold cyan]")
    except (EOFError, KeyboardInterrupt):
        return ""


def print_thinking() -> Live:
    """Show a thinking spinner. Returns Live context to be used with 'with'."""
    return Live(
        Spinner("dots", text="Thinking...", style="cyan"),
        console=console,
        transient=True,
    )


def print_token_usage(prompt_tokens: int, completion_tokens: int, total_tokens: int) -> None:
    """Print token usage information."""
    console.print(
        f"\n[dim]Tokens: {prompt_tokens} prompt + {completion_tokens} completion = {total_tokens} total[/dim]"
    )


def print_goodbye() -> None:
    """Print goodbye message."""
    console.print("\n[cyan]Goodbye![/cyan]\n")
