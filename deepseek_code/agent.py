"""Core agent loop implementation."""

from dataclasses import dataclass
from typing import Any, Callable

from .llm import DeepSeekClient, LLMResponse, ToolCall
from .tools.base import ToolRegistry, ToolResult, create_default_registry
from .permissions import PermissionManager, PermissionLevel, PermissionRequest
from .conversation import ConversationHistory
from .context import ProjectContext, build_system_prompt
from . import ui


@dataclass
class AgentConfig:
    """Configuration for the agent."""

    max_turns: int = 50
    trust_mode: bool = False
    verbose: bool = False


class Agent:
    """Main agent that orchestrates the LLM and tools."""

    def __init__(
        self,
        client: DeepSeekClient,
        context: ProjectContext,
        config: AgentConfig | None = None,
        registry: ToolRegistry | None = None,
    ):
        self.client = client
        self.context = context
        self.config = config or AgentConfig()
        self.registry = registry or create_default_registry()
        self.permissions = PermissionManager(trust_mode=self.config.trust_mode)

        # Build system prompt
        self.system_prompt = build_system_prompt(context)

        # Initialize conversation
        self.history = ConversationHistory(system_prompt=self.system_prompt)

    def _get_permission(self, request: PermissionRequest) -> bool:
        """
        Check permission for a tool call, prompting user if needed.

        Returns True if allowed, False if denied.
        """
        if request.level == PermissionLevel.AUTO:
            return True

        if request.level == PermissionLevel.DENY:
            if request.reason:
                ui.print_error(f"Blocked: {request.reason}")
            else:
                ui.print_error("This operation is blocked for safety.")
            return False

        # ASK level - prompt user
        prompt = self.permissions.format_permission_prompt(request)
        choice = ui.ask_permission(prompt)

        if choice == "y":
            return True
        elif choice == "always":
            # Add to session allowlist
            tool_name = request.tool_name
            if tool_name == "bash":
                cmd = request.tool_input.get("command", "")
                # Extract command prefix for allowlist
                cmd_prefix = cmd.split()[0] if cmd else ""
                if cmd_prefix:
                    self.permissions.add_to_allowlist(f"bash({cmd_prefix}*)")
                    ui.print_info(f"Added 'bash({cmd_prefix}*)' to session allowlist")
            elif tool_name in ("write_file", "edit_file"):
                path = request.tool_input.get("path", "")
                self.permissions.add_to_allowlist(f"write({path})")
                ui.print_info(f"Added 'write({path})' to session allowlist")
            return True
        else:
            return False

    def _execute_tool(self, tool_call: ToolCall) -> str:
        """Execute a single tool call and return the result."""
        tool = self.registry.get(tool_call.name)

        if not tool:
            return f"Error: Unknown tool '{tool_call.name}'"

        # Check permissions
        perm_request = self.permissions.check_permission(
            tool_call.name, tool_call.arguments
        )

        if not self._get_permission(perm_request):
            return "Permission denied by user."

        # Execute the tool
        try:
            result = tool.execute(**tool_call.arguments)
            return str(result)
        except Exception as e:
            return f"Error executing tool: {e}"

    def _process_tool_calls(self, tool_calls: list[ToolCall]) -> list[dict[str, Any]]:
        """Process all tool calls and return results."""
        results = []

        for tc in tool_calls:
            # Show tool call
            ui.print_tool_call(tc.name, tc.arguments)

            # Execute
            result = self._execute_tool(tc)

            # Show result (truncated)
            success = not result.startswith("Error")
            ui.print_tool_result(result, success=success)

            # Format for API
            results.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })

        return results

    def run_turn(self, user_message: str | None = None) -> str | None:
        """
        Run a single agent turn.

        Args:
            user_message: Optional user message to add before the turn

        Returns:
            Final text response from assistant, or None if still processing
        """
        # Add user message if provided
        if user_message:
            self.history.add_user_message(user_message)

        # Get tool schemas
        tool_schemas = self.registry.get_schemas()

        # Build messages for API
        messages = self.history.get_full_context()

        # Call LLM
        with ui.print_thinking():
            response = self.client.chat(messages, tools=tool_schemas)

        # Add assistant message to history
        assistant_msg = self.client.format_assistant_message(response)
        self.history.add_assistant_message(assistant_msg)

        # Check if done (no tool calls)
        if not response.has_tool_calls:
            if response.content:
                ui.print_assistant_message(response.content)
            return response.content

        # Process tool calls
        tool_results = self._process_tool_calls(response.tool_calls)
        self.history.add_tool_results(tool_results)

        # Continue processing (tool results added, ready for next turn)
        return None

    def run(self, task: str) -> str:
        """
        Run the agent loop until task is complete.

        Args:
            task: The task/prompt to execute

        Returns:
            Final response from the agent
        """
        # Add initial task
        self.history.add_user_message(task)

        for turn in range(self.config.max_turns):
            # Run a turn (don't add message, already added)
            result = self.run_turn(user_message=None)

            if result is not None:
                # Agent is done
                return result

        # Max turns reached
        ui.print_warning(f"Reached maximum turns ({self.config.max_turns})")
        return "Task incomplete - maximum turns reached."

    def chat(self, message: str) -> str:
        """
        Send a chat message and get response (for interactive mode).

        This runs the full agent loop for a single user message.
        """
        for turn in range(self.config.max_turns):
            if turn == 0:
                result = self.run_turn(user_message=message)
            else:
                result = self.run_turn(user_message=None)

            if result is not None:
                return result

        ui.print_warning(f"Reached maximum turns ({self.config.max_turns})")
        return "Response incomplete - maximum turns reached."

    def reset(self) -> None:
        """Reset conversation history."""
        self.history = ConversationHistory(system_prompt=self.system_prompt)


def create_agent(
    api_key: str | None = None,
    model: str | None = None,
    working_dir: str = ".",
    trust_mode: bool = False,
    max_turns: int = 50,
) -> Agent:
    """
    Create an agent with default configuration.

    Args:
        api_key: DeepSeek API key (or use DEEPSEEK_API_KEY env var)
        model: Model to use (default: deepseek-chat)
        working_dir: Working directory
        trust_mode: Auto-approve safe operations
        max_turns: Maximum turns per task

    Returns:
        Configured Agent instance
    """
    from .context import get_project_context

    client = DeepSeekClient(api_key=api_key, model=model)
    context = get_project_context(working_dir)
    config = AgentConfig(max_turns=max_turns, trust_mode=trust_mode)

    return Agent(client=client, context=context, config=config)
