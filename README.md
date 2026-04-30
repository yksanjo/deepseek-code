# 🐟 deepseek-code

> Open-source AI coding assistant CLI — your own Claude Code, ~1/100th the cost.

```bash
pip install deepseek-code
export DEEPSEEK_API_KEY=...
dsc
```

That's it. You're coding with an autonomous agent.

[![PyPI](https://img.shields.io/pypi/v/deepseek-code)](https://pypi.org/project/deepseek-code/)
[![License](https://img.shields.io/github/license/yksanjo/deepseek-code)](LICENSE)
[![Stars](https://img.shields.io/github/stars/yksanjo/deepseek-code?style=social)](https://github.com/yksanjo/deepseek-code)

---

## Why

Claude Code is great. It also costs $20–$200/mo and locks you to one provider.

**`deepseek-code` is the same idea, open-source, model-agnostic, and runs against any OpenAI-compatible endpoint** — DeepSeek, Qwen, Kimi, Together, Ollama, your own self-hosted model.

Typical session cost on DeepSeek-V3: **~$0.14**.

## Features

- 🛠️ **Full tool use** — bash, file read/write, glob, grep
- 🔐 **Permission prompts** — every dangerous action asks first (or `--yolo` to skip)
- 💬 **Multi-turn conversation** — keeps context across the session
- 🌍 **Multi-language UX** — English + Chinese READMEs and prompts
- 🔄 **Provider-agnostic** — swap models with one env var
- ⌨️ **Real terminal UX** — multiline input (Ctrl+J), history, syntax highlighting

## Install

```bash
pip install deepseek-code
```

Or from source:

```bash
git clone https://github.com/yksanjo/deepseek-code
cd deepseek-code
pip install -e .
```

## Configure

```bash
export DEEPSEEK_API_KEY=your_key_here
```

## Use

```bash
dsc                              # interactive REPL in current directory
dsc "fix the failing test"       # one-shot mode
dsc --yolo "refactor utils.py"   # skip permission prompts (use with care)
```

## Switch models

Anything OpenAI-compatible works. Set two env vars:

| Provider | `DEEPSEEK_BASE_URL` | `DEEPSEEK_MODEL` |
|---|---|---|
| DeepSeek (default) | `https://api.deepseek.com` | `deepseek-chat` |
| Qwen (Alibaba) | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-coder-plus` |
| Kimi (Moonshot) | `https://api.moonshot.cn/v1` | `moonshot-v1-32k` |
| Together AI | `https://api.together.xyz/v1` | `deepseek-ai/DeepSeek-V3` |
| Ollama (local) | `http://localhost:11434/v1` | `qwen2.5-coder:32b` |

Reuse `DEEPSEEK_API_KEY` for all of them (or set whatever the provider expects).

## How it compares

| | deepseek-code | Claude Code | Cursor | Aider |
|---|---|---|---|---|
| Cost / session | ~$0.14 | $20–$200 / mo | $20 / mo | varies |
| Open source | ✅ | ❌ | ❌ | ✅ |
| Model swap | ✅ any OpenAI-compat | ❌ | partial | ✅ |
| Terminal-native | ✅ | ✅ | ❌ | ✅ |
| MCP tools | 🚧 v0.2 | ✅ | ❌ | ❌ |

## Roadmap

See [`docs/ROADMAP.md`](docs/ROADMAP.md) for the full v0.2 plan. Highlights:

- `/load <path>` for explicit file context
- Tab completion for file paths
- `--model` flag (no env vars needed)
- MCP tool support via [`mcp-discovery`](https://github.com/yksanjo/mcp-discovery) — bring 14k MCP servers into your terminal
- `/cost` command — track cumulative session cost in real time
- Status line — model, tokens, $ used

## Contributing

PRs welcome. See [`CONTRIBUTING.md`](CONTRIBUTING.md). Small, focused PRs preferred.

Active contributors: [@antenore](https://github.com/antenore)

## License

MIT.
