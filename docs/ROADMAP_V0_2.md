# Roadmap — v0.2

**Goal:** close the three biggest UX gaps versus Claude Code while keeping the cost story intact.

## Status

- v0.1 — shipped (18 ⭐, 1 contributor, 1 merged PR)
- v0.2 — planning (this doc)

## v0.2 scope

Ordered by leverage. Each item is one or more focused PRs.

### 1. Real README (replaces scaffold) — DONE in this branch

The previous README was a generic project scaffold. Replaced with real positioning, install in three lines, model-swap table, and a comparison matrix.

**Why first:** every visitor to the repo loses confidence on a generic README. This is a one-day fix that compounds across every future visit.

### 2. `/load <path>` — file context command

Closes the largest UX gap vs Claude Code's `@file` behavior. Users want to say "look at `auth/session.py`" without describing it.

Surface:
```
> /load auth/session.py
loaded auth/session.py (143 lines, 3.2KB)

> /load src/**/*.py
loaded 14 files (892 lines, 28KB)

> /unload
cleared loaded context
```

Implementation: load files into a dedicated section of the conversation history, separate from agent tool-use. Lead: @antenore.

### 3. Tab completion for file paths

Pairs naturally with `/load`. Use prompt-toolkit's path completer; gate it on `/load `, `/cat `, etc.

Lead: @antenore.

### 4. `--model` flag

The LLM client already supports `DEEPSEEK_BASE_URL` and `DEEPSEEK_MODEL` env vars. Add a `--model deepseek|qwen|kimi|together|ollama` shorthand that sets both at once. Document in README.

```bash
dsc --model qwen "fix this bug"
```

### 5. MCP tool support

The differentiator. `mcp-discovery` already has 14k indexed servers. Wire them in:

- New `--mcp <name>` flag → fetches server metadata, runs install, registers as tools
- Or `/mcp install filesystem` inside a session
- MCP tools appear in the same tool registry as built-in `bash`/`file`/`search`

Architecture sketch:

```
deepseek-code agent
    └── ToolRegistry
        ├── bash           (built-in)
        ├── file_*         (built-in)
        ├── search_*       (built-in)
        └── MCP adapter    (NEW)
            └── reads from mcp-discovery API
            └── proxies tool calls to MCP server stdio
```

### 6. `/cost` command + status line

Surfaces the "1/100th cost" thesis viscerally. Status line shows model + tokens + cumulative $. `/cost` shows session breakdown.

Reinforces the brand on every screenshot.

## Out of scope for v0.2

- Multi-agent orchestration
- Auto-commit / auto-PR
- Web UI
- Plugin API (deferred to v0.3)

## Launch plan

When v0.2 ships:
- Show HN: "DeepSeek-Code v0.2 — open-source Claude Code with 14k MCP tools, $0.14 per session"
- X thread: cost graph + status line gif
- r/LocalLLaMA: emphasize Ollama support
- DEV.to long-form: model swap walkthrough

## Timeline

3 weeks of part-time work. README + `--model` + `/cost` + status line in week 1. `/load` + tab completion in week 2 (Antenore). MCP support in week 3.
