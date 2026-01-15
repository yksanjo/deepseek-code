"""CLI entry point for DeepSeek Code."""

import os
import sys
from typing import Optional

import typer
from dotenv import load_dotenv
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
from rich.console import Console

from . import __version__
from .agent import Agent, AgentConfig
from .context import get_project_context
from .llm import DeepSeekClient
from . import ui


# Load environment variables from .env file
load_dotenv()

app = typer.Typer(
    name="deepseek-code",
    help="AI coding assistant powered by DeepSeek-V3",
    add_completion=False,
)

console = Console()


def get_prompt_session() -> PromptSession:
    """Create a prompt session with history and multiline support."""
    history_dir = os.path.expanduser("~/.deepseek-code")
    os.makedirs(history_dir, exist_ok=True)
    history_file = os.path.join(history_dir, "prompt_history")

    bindings = KeyBindings()

    @bindings.add("enter")
    def _(event):
        event.current_buffer.validate_and_handle()

    @bindings.add("c-j")
    def _(event):
        event.current_buffer.insert_text("\n")

    return PromptSession(
        history=FileHistory(history_file),
        key_bindings=bindings,
        multiline=True,
    )


def interactive_loop(agent: Agent) -> None:
    """Run the interactive REPL loop."""
    session = get_prompt_session()

    while True:
        try:
            # Get user input
            user_input = session.prompt("\n> ").strip()

            if not user_input:
                continue

            # Handle special commands
            if user_input.lower() in ("quit", "exit", "q"):
                ui.print_goodbye()
                break

            if user_input.lower() == "clear":
                agent.reset()
                console.print("[info]Conversation cleared.[/info]")
                continue

            if user_input.lower() == "help":
                print_help(agent)
                continue

            # Toggle YOLO mode
            if user_input.lower() in ("/yolo", "yolo"):
                agent.permissions.yolo_mode = not agent.permissions.yolo_mode
                agent.config.yolo_mode = agent.permissions.yolo_mode
                if agent.permissions.yolo_mode:
                    console.print("[bold red]⚠️  YOLO MODE ENABLED ⚠️[/bold red]")
                    console.print("[yellow]All permission prompts will be skipped![/yellow]")
                else:
                    console.print("[green]YOLO mode disabled.[/green]")
                    console.print("[dim]Permission prompts are now active.[/dim]")
                continue

            # Toggle trust mode
            if user_input.lower() in ("/trust", "trust"):
                agent.permissions.trust_mode = not agent.permissions.trust_mode
                agent.config.trust_mode = agent.permissions.trust_mode
                if agent.permissions.trust_mode:
                    console.print("[cyan]Trust mode enabled.[/cyan]")
                else:
                    console.print("[dim]Trust mode disabled.[/dim]")
                continue

            # Show current mode status
            if user_input.lower() in ("/status", "status"):
                print_status(agent)
                continue

            # Process the message
            agent.chat(user_input)

        except KeyboardInterrupt:
            console.print("\n[dim]Use 'quit' to exit[/dim]")
            continue

        except EOFError:
            ui.print_goodbye()
            break


def print_help(agent: Agent) -> None:
    """Print help information."""
    yolo_status = "[red]ON[/red]" if agent.permissions.yolo_mode else "[dim]off[/dim]"
    trust_status = "[cyan]ON[/cyan]" if agent.permissions.trust_mode else "[dim]off[/dim]"

    console.print(f"""
[bold]Commands:[/bold]
  quit, exit, q  - Exit the program
  clear          - Clear conversation history
  help           - Show this help message

[bold]Mode Commands:[/bold]
  /yolo          - Toggle YOLO mode (currently {yolo_status})
  /trust         - Toggle trust mode (currently {trust_status})
  /status        - Show current mode status

[bold]Tips:[/bold]
  - Ctrl+J inserts a newline (for multiline input)
  - Ask the AI to read files before editing them
  - Use 'always' when prompted to auto-approve similar operations
  - Create a DEEPSEEK.md file in your project root for project-specific context
""")


def print_status(agent: Agent) -> None:
    """Print current mode status."""
    console.print("\n[bold]Current Status:[/bold]")

    if agent.permissions.yolo_mode:
        console.print("  YOLO Mode:  [bold red]ON[/bold red] (all prompts skipped)")
    else:
        console.print("  YOLO Mode:  [dim]off[/dim]")

    if agent.permissions.trust_mode:
        console.print("  Trust Mode: [cyan]ON[/cyan] (safe ops auto-approved)")
    else:
        console.print("  Trust Mode: [dim]off[/dim]")

    console.print(f"  Model:      [blue]{agent.client.model}[/blue]")
    console.print()


def create_and_run_agent(
    task: Optional[str],
    model: str,
    trust: bool,
    yolo: bool,
    max_turns: int,
    verbose: bool,
    no_context: bool,
) -> None:
    """Create an agent and run it with the given task or in interactive mode."""
    # Check for API key
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        console.print(
            "[error]Error: DEEPSEEK_API_KEY environment variable not set.[/error]\n"
            "Get your API key from: https://platform.deepseek.com/\n"
            "Then set it: export DEEPSEEK_API_KEY=your_key_here"
        )
        raise typer.Exit(1)

    # Get project context
    context = get_project_context(".")
    context_loaded = context.deepseek_md is not None

    if no_context:
        context.deepseek_md = None
        context_loaded = False

    # Print welcome
    ui.print_welcome(__version__, context.working_dir, context_loaded, yolo_mode=yolo)

    # Create agent
    try:
        client = DeepSeekClient(api_key=api_key, model=model)
        config = AgentConfig(
            max_turns=max_turns,
            trust_mode=trust,
            yolo_mode=yolo,
            verbose=verbose,
        )
        agent = Agent(client=client, context=context, config=config)

    except Exception as e:
        console.print(f"[error]Failed to initialize: {e}[/error]")
        raise typer.Exit(1)

    # Run task or interactive mode
    if task:
        # Single task mode
        try:
            agent.run(task)
        except KeyboardInterrupt:
            console.print("\n[warning]Interrupted[/warning]")
            raise typer.Exit(130)
    else:
        # Interactive mode
        interactive_loop(agent)


@app.command()
def run(
    task: Optional[str] = typer.Argument(
        None,
        help="Task to execute (if not provided, starts interactive mode)",
    ),
    model: str = typer.Option(
        "deepseek-chat",
        "--model", "-m",
        help="Model to use (deepseek-chat, deepseek-coder)",
    ),
    trust: bool = typer.Option(
        False,
        "--trust", "-t",
        help="Trust mode: auto-approve safe operations",
    ),
    yolo: bool = typer.Option(
        False,
        "--dangerously-skip-permissions", "--yolo",
        help="YOLO mode: skip ALL permission prompts (use with caution!)",
    ),
    max_turns: int = typer.Option(
        50,
        "--max-turns",
        help="Maximum turns per task",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose", "-v",
        help="Verbose output",
    ),
    no_context: bool = typer.Option(
        False,
        "--no-context",
        help="Don't load DEEPSEEK.md context",
    ),
) -> None:
    """
    Run DeepSeek Code with a task or in interactive mode.

    Examples:
        deepseek-code run
        deepseek-code run "Fix the bug in auth.py"
        deepseek-code run --trust "Run the tests"
        deepseek-code run --yolo "Refactor the entire codebase"
    """
    create_and_run_agent(task, model, trust, yolo, max_turns, verbose, no_context)


@app.command()
def init() -> None:
    """Initialize a DEEPSEEK.md file in the current directory."""
    deepseek_md_path = "DEEPSEEK.md"

    if os.path.exists(deepseek_md_path):
        console.print(f"[warning]{deepseek_md_path} already exists[/warning]")
        raise typer.Exit(1)

    template = """# DEEPSEEK.md

## Project Overview
Describe your project here.

## Key Commands
- `make test`: Run tests
- `make lint`: Run linting
- `npm run dev`: Start development server

## Architecture
- `src/`: Source code
- `tests/`: Test files
- `docs/`: Documentation

## Conventions
- List your coding conventions here
- Style guides, patterns to follow

## Known Issues
- Document any known issues or gotchas
"""

    with open(deepseek_md_path, "w") as f:
        f.write(template)

    console.print(f"[success]Created {deepseek_md_path}[/success]")
    console.print("Edit this file to add project-specific context for the AI.")


@app.command()
def history(
    limit: int = typer.Option(20, "--limit", "-n", help="Number of sessions to show"),
) -> None:
    """Show recent conversation history."""
    from .conversation import ConversationStore

    store = ConversationStore()
    sessions = store.list_sessions(limit=limit)

    if not sessions:
        console.print("[dim]No conversation history found.[/dim]")
        return

    console.print("[bold]Recent sessions:[/bold]\n")
    for session in sessions:
        console.print(f"  {session['id']}  {session['timestamp']}")


@app.command()
def version() -> None:
    """Show version information."""
    console.print(f"DeepSeek Code v{__version__}")


def main():
    """Main entry point - defaults to interactive mode if no args."""
    # If no arguments provided, default to 'run' command
    if len(sys.argv) == 1:
        sys.argv.append("run")
    app()


if __name__ == "__main__":
    main()
