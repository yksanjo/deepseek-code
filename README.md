# deepseek-code

An open-source CLI coding assistant powered by DeepSeek. Build your own
Claude Code workflow for roughly 1/100th the API cost.

```bash
pip install -e .
export DEEPSEEK_API_KEY=sk-...
deepseek-code
```

[![License](https://img.shields.io/github/license/yksanjo/deepseek-code)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](pyproject.toml)
![Status](https://img.shields.io/badge/status-beta-orange)

---

## What it is

A terminal coding assistant that talks to the DeepSeek API (V3 / V4
chat) and runs an agent loop with file, search, and bash tools. The
architecture mirrors Claude Code: an agent that turns LLM tool calls
into local file edits, shell commands, and codebase searches, gated
by a permission system.

It is intentionally a thin, hackable CLI — a starting point you can
fork and extend, not a SaaS product.

## Why

- **Cost.** DeepSeek pricing is roughly 1–2% of frontier model
  pricing per token. For an agent loop that burns tokens on tool
  calls and context, that's the difference between "$1 per session"
  and "$0.01 per session." See `BENCHMARKS.md` for back-of-envelope
  comparisons.
- **Self-hostable.** Bring your own key. No backend.
- **Hackable.** ~1,800 lines of Python across 8 modules. Add a new
  tool by dropping a file into `deepseek_code/tools/`.

## Honest limitations

- **Quality gap vs frontier models.** DeepSeek V3-class models are
  excellent for the price, but on complex multi-file refactors they
  trail Claude Sonnet / GPT-4.1. The 100× cost gap is real and so is
  the quality gap. Pick deliberately.
- **Beta.** Not safe for unattended use on production code. Permission
  prompts default to "ask for every action."
- **Tooling surface is small.** File read/write/edit, search, and
  bash. No MCP support yet, no IDE integration.

## Install

Requires Python 3.10+.

```bash
git clone https://github.com/yksanjo/deepseek-code.git
cd deepseek-code
pip install -e .
```

Set your API key (get one at https://platform.deepseek.com):

```bash
export DEEPSEEK_API_KEY=sk-...
# Or put it in a .env file in your project directory.
```

## Use

```bash
# Start an interactive session in the current directory
deepseek-code

# One-shot prompt mode
deepseek-code "explain the agent loop in deepseek_code/agent.py"

# Skip permission prompts (use cautiously — the equivalent of
# Claude Code's --dangerously-skip-permissions)
deepseek-code --yolo
```

In an interactive session:
- Type a request and press Enter.
- The agent will propose tool calls (read file, edit file, run bash,
  etc.); you confirm or deny each one unless you've enabled trust.
- `Ctrl-D` exits.

## Architecture

```
deepseek_code/
├── cli.py          # Typer entry point, interactive REPL
├── agent.py        # Agent loop: LLM → tool calls → results → LLM
├── llm.py          # DeepSeek API client (OpenAI-compatible)
├── conversation.py # Message history, system prompt assembly
├── context.py      # Project context (cwd, language, files)
├── permissions.py  # Per-tool-call user prompts
├── ui.py           # Rich-based terminal UI
└── tools/
    ├── base.py
    ├── file_tools.py    # read / write / edit / list
    ├── search_tools.py  # grep / glob
    └── bash_tool.py     # shell execution
```

## Extending

Add a new tool by subclassing `Tool` in `tools/base.py`, registering
it in `tools/__init__.py`'s `create_default_registry()`, and giving
it a JSON schema for arguments. The agent will pick it up
automatically on the next run.

## Cost comparison

See `BENCHMARKS.md` for detailed pricing math. Headline numbers
(subject to provider changes):

| Tool | API pricing (per 1M tokens) |
|---|---|
| DeepSeek (this) | ~$0.14 in / $0.28 out |
| Claude Sonnet | ~$3 in / $15 out |
| Claude Opus | ~$15 in / $75 out |

For a typical 50-turn coding session, this lands at roughly $0.01 vs
$1.25 for Claude. Whether the quality trade-off is right for you
depends on the task.

## Contributing

PRs welcome. See `CONTRIBUTING.md` for the workflow. Tests live in
`tests/`; run with `pytest`.

## License

MIT. See `LICENSE`.

## Disclosures

This project was developed with assistance from AI coding tools. The
agent architecture is consciously modeled after Anthropic's Claude
Code; this is not an Anthropic product.
