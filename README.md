# DeepSeek Code

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![DeepSeek](https://img.shields.io/badge/Powered%20by-DeepSeek--V3-green.svg)](https://www.deepseek.com/)

**An open-source AI coding assistant CLI powered by DeepSeek-V3** - Build your own "Claude Code" with DeepSeek's API.

**开源 AI 编程助手命令行工具，由 DeepSeek-V3 驱动** - 使用 DeepSeek API 打造属于你自己的 "Claude Code"。

<p align="center">
  <img src="https://img.shields.io/badge/2100+-lines%20of%20Python-blue" alt="Lines of Code">
  <img src="https://img.shields.io/badge/6-tools-orange" alt="Tools">
  <img src="https://img.shields.io/badge/100%25-local%20first-green" alt="Local First">
</p>

```
  ____                 ____            _
 |  _ \  ___  ___ _ __/ ___|  ___  ___| | __
 | | | |/ _ \/ _ \ '_ \___ \ / _ \/ _ \ |/ /
 | |_| |  __/  __/ |_) |__) |  __/  __/   <
 |____/ \___|\___| .__/____/ \___|\___|_|\_\
   ____          |_|  _
  / ___|___   __| | ___
 | |   / _ \ / _` |/ _ \
 | |__| (_) | (_| |  __/
  \____\___/ \__,_|\___|
```

---

## 为什么选择 DeepSeek Code? | Why DeepSeek Code?

<details>
<summary>🇨🇳 中文</summary>

- **性价比高**: DeepSeek-V3 提供 GPT-4 级别的性能，成本仅为其一小部分
- **开放架构**: 完全了解 AI 编程代理的工作原理，没有黑盒
- **可扩展**: 添加自定义工具、修改代理循环、自由定制一切
- **注重隐私**: 代码留在本地，只有提示词发送到 API

### 主要功能

| 功能 | 描述 |
|------|------|
| **交互式 REPL** | 实时与 AI 讨论你的代码 |
| **文件操作** | 读取、写入、精准编辑文件 |
| **Shell 命令** | 运行 bash 命令，带安全检查 |
| **代码搜索** | 用 glob 查找文件，用 grep 搜索内容 |
| **项目上下文** | 自动加载 `DEEPSEEK.md` 获取项目知识 |
| **权限系统** | 危险操作前请求许可 |
| **YOLO 模式** | 使用 `--yolo` 跳过所有提示（类似 Claude Code） |
| **对话历史** | 跨会话保存 |

</details>

<details open>
<summary>🇺🇸 English</summary>

- **Cost-effective**: DeepSeek-V3 offers GPT-4 level performance at a fraction of the cost
- **Open architecture**: Understand exactly how AI coding agents work - no black box
- **Extensible**: Add your own tools, modify the agent loop, customize everything
- **Privacy-focused**: Your code stays on your machine, only prompts go to the API

## Features

| Feature | Description |
|---------|-------------|
| **Interactive REPL** | Chat with AI about your code in real-time |
| **File Operations** | Read, write, and surgically edit files |
| **Shell Commands** | Run bash commands with safety checks |
| **Code Search** | Find files with glob, search content with grep |
| **Project Context** | Auto-loads `DEEPSEEK.md` for project-specific knowledge |
| **Permission System** | Asks before dangerous operations |
| **YOLO Mode** | Skip all prompts with `--yolo` (like Claude Code) |
| **Conversation History** | Persists across sessions |

</details>

## Installation

### Option 1: Install from GitHub (Recommended)

```bash
# Clone and install in one go
git clone https://github.com/yksanjo/deepseek-code.git
cd deepseek-code
pip install -e .
```

### Option 2: Quick Install (One-liner)

```bash
pip install git+https://github.com/yksanjo/deepseek-code.git
```

### Setup API Key

1. Get your API key from [DeepSeek Platform](https://platform.deepseek.com/)
2. Add credits to your account (DeepSeek-V3 is very affordable!)
3. Set the environment variable:

```bash
# Add to your shell profile (~/.bashrc, ~/.zshrc, etc.)
export DEEPSEEK_API_KEY=your_key_here

# Or create a .env file in your project
echo "DEEPSEEK_API_KEY=your_key_here" > .env
```

### Launch

```bash
# Start interactive mode
deepseek-code

# Or use the short alias
dsc
```

You should see:
```
  ____                 ____            _
 |  _ \  ___  ___ _ __/ ___|  ___  ___| | __
 | | | |/ _ \/ _ \ '_ \___ \ / _ \/ _ \ |/ /
 | |_| |  __/  __/ |_) |__) |  __/  __/   <
 |____/ \___|\___| .__/____/ \___|\___|_|\_\
   ____          |_|  _
  / ___|___   __| | ___
 | |   / _ \ / _` |/ _ \
 | |__| (_) | (_| |  __/
  \____\___/ \__,_|\___|

                    v0.1.0

  Directory: /your/project
  Type help for commands, quit to exit

──────────────────────────────────────────────────

>
```

## Usage

### Interactive Mode

```bash
deepseek-code
```

```
DeepSeek Code v0.1.0
Working directory: /path/to/your/project

> Fix the type error in utils.py

> Reading utils.py...
> edit_file: utils.py
   old: "def process(data):"
   new: "def process(data: dict) -> list:"

Permission required: Edit file: utils.py
Allow? [y/n/always]: y

Fixed type annotation in utils.py

> quit
```

### Single Task Mode

```bash
deepseek-code run "Add docstrings to all functions in main.py"
```

### CLI Commands

```bash
deepseek-code              # Start interactive mode (default)
deepseek-code run "task"   # Run a single task
deepseek-code init         # Create DEEPSEEK.md template
deepseek-code history      # Show conversation history
deepseek-code version      # Show version
```

### Options

```bash
deepseek-code run --help

Options:
  -m, --model TEXT                Model to use (deepseek-chat, deepseek-coder)
  -t, --trust                     Trust mode: auto-approve safe operations
  --yolo, --dangerously-skip-permissions
                                  YOLO mode: skip ALL permission prompts
  --max-turns INTEGER             Maximum turns per task (default: 50)
  -v, --verbose                   Verbose output
  --no-context                    Don't load DEEPSEEK.md context
```

## Permission Controls

DeepSeek Code has a flexible permission system similar to Claude Code. Choose your level of automation:

### Default Mode (Recommended for beginners)
```bash
deepseek-code
```
- **Read operations**: Auto-approved (reading files, searching)
- **Write operations**: Asks for permission each time
- **Shell commands**: Asks for permission, blocks dangerous commands
- **Option to "always" approve**: Type `a` or `always` when prompted to auto-approve similar operations

### Trust Mode (`--trust` / `-t`)
```bash
deepseek-code run --trust "your task"
```
- Auto-approves **safe** write operations and shell commands
- Still asks for potentially dangerous operations
- Good for: Routine tasks in trusted projects

### YOLO Mode (`--yolo` / `--dangerously-skip-permissions`)
```bash
# Full flag (like Claude Code)
deepseek-code run --dangerously-skip-permissions "your task"

# Short alias
deepseek-code run --yolo "refactor entire codebase"
```
- **Skips ALL permission prompts** - maximum speed
- Still blocks truly dangerous commands (`rm -rf /`, `sudo`, fork bombs)
- Shows warning banner when enabled:
  ```
  ⚠️  YOLO MODE ENABLED ⚠️
  All permission prompts will be skipped!
  (Dangerous operations like rm -rf / are still blocked)
  ```
- Good for: Experienced users, trusted environments, rapid iteration

### Permission Levels Summary

| Mode | Flag | File Writes | Shell Commands | Dangerous Commands |
|------|------|-------------|----------------|-------------------|
| Default | (none) | Ask | Ask | Blocked |
| Trust | `--trust` | Auto | Auto (safe) | Blocked |
| YOLO | `--yolo` | Auto | Auto | Blocked |

### Blocked Commands (Always)

These are blocked in ALL modes for safety:
- `rm -rf /` and similar destructive commands
- `sudo` commands
- Fork bombs
- Direct disk writes (`dd if=/dev/zero of=/dev/sda`)
- Piping untrusted content to shell (`curl ... | bash`)

## Tools

DeepSeek Code comes with 6 built-in tools:

| Tool | Description | Permission |
|------|-------------|------------|
| `read_file` | Read file contents with line numbers | Auto |
| `write_file` | Create or overwrite files | Ask |
| `edit_file` | Surgical string replacement (like sed) | Ask |
| `bash` | Run shell commands | Ask (dangerous blocked) |
| `glob` | Find files by pattern (`**/*.py`) | Auto |
| `grep` | Search file contents with regex | Auto |

## Project Context

Create a `DEEPSEEK.md` file in your project root to give the AI project-specific knowledge:

```bash
deepseek-code init
```

```markdown
# DEEPSEEK.md

## Project Overview
FastAPI backend for user authentication.

## Key Commands
- `make test`: Run all tests
- `make lint`: Run linting

## Architecture
- `src/api/`: API routes
- `src/models/`: Database models

## Conventions
- Use type hints everywhere
- Write tests for new features
```

## Architecture

```
deepseek_code/
├── cli.py             # Typer CLI entry point
├── agent.py           # Core agent loop (the magic happens here)
├── llm.py             # DeepSeek API client (OpenAI-compatible)
├── tools/             # Tool implementations
│   ├── base.py        # Tool base class & registry
│   ├── file_tools.py  # read, write, edit
│   ├── search_tools.py # glob, grep
│   └── bash_tool.py   # Shell commands
├── permissions.py     # Safety checks
├── context.py         # DEEPSEEK.md loading
├── conversation.py    # History management
└── ui.py              # Rich terminal UI
```

## How It Works

The core is a simple **agent loop**:

```python
while not done:
    response = llm.chat(messages, tools)

    if response.has_tool_calls:
        for tool_call in response.tool_calls:
            result = execute_tool(tool_call)
            messages.append(result)
    else:
        done = True
```

1. **Send messages** to DeepSeek with available tools
2. **Execute tool calls** if the AI requests them
3. **Feed results back** to the AI
4. **Repeat** until the AI responds without tool calls

This is the same pattern used by Claude Code, GPT-4 agents, and other AI coding assistants.

## Extending

### Add a New Tool

```python
from deepseek_code.tools.base import Tool, ToolResult

class MyTool(Tool):
    name = "my_tool"
    description = "Does something useful"
    permission_level = "ask"  # or "auto" for safe operations

    parameters = {
        "input": {
            "type": "string",
            "description": "The input to process",
            "required": True,
        }
    }

    def execute(self, input: str) -> ToolResult:
        # Your logic here
        return ToolResult(success=True, output="Done!")
```

Register it in `tools/base.py`:

```python
def create_default_registry():
    registry = ToolRegistry()
    # ... existing tools ...
    registry.register(MyTool())
    return registry
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black deepseek_code/
ruff check deepseek_code/
```

## Comparison with Other Tools

| Feature | DeepSeek Code | Claude Code | Cursor | GitHub Copilot |
|---------|--------------|-------------|--------|----------------|
| Open Source | Yes | No | No | No |
| Self-hostable | Yes | No | No | No |
| Cost | ~$0.14/M tokens | ~$15/M tokens | $20/mo | $10/mo |
| Customizable | Fully | No | Limited | No |
| Local LLM support | Planned | No | No | No |

## Roadmap

- [ ] Streaming responses
- [ ] Sub-agent support for complex tasks
- [ ] Local LLM support (Ollama, llama.cpp)
- [ ] VS Code extension
- [ ] Multi-file editing
- [ ] Git integration tools

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- Inspired by [Claude Code](https://claude.ai/code) architecture
- Powered by [DeepSeek-V3](https://www.deepseek.com/)
- Built with [Typer](https://typer.tiangolo.com/) and [Rich](https://rich.readthedocs.io/)

---

<p align="center">
  <b>Star this repo if you find it useful!</b>
</p>
