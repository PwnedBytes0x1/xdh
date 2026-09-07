# 🛠️ Tools & Capabilities

`xdh` ships with a comprehensive set of 24 built-in autonomous tools exposed to LLM function-calling mechanisms, alongside dynamic tools discovered via MCP servers and user plugins.

---

## 🧰 Available Built-in Agent Tools

| Tool Name | Scope | Description |
| :--- | :--- | :--- |
| `bash` | System | Executes shell commands in workspace with non-blocking timeout handling and truncation. |
| `read_file` | Filesystem | Reads full files or specific line ranges (`start_line`, `end_line`) with smart encoding detection. |
| `write_file` | Filesystem | Writes or overwrites files on disk with automatic parent directory creation and backup snapshots. |
| `find_by_name` | Filesystem | Searches for files and directories matching glob patterns, filtered by `.xdhignore` / `.gitignore`. |
| `replace_file_content` | Codebase | Performs surgical line replacements matching exact target content chunks. |
| `list_dir` | Filesystem | Lists directory entries with file sizes, types, and recursive directory counts. |
| `grep_search` | Codebase | Fast regex and literal pattern matching across project files (accelerated by `ripgrep` when available). |
| `file_info` | Filesystem | Retrieves file metadata including size, permissions, line count, and last modification timestamp. |
| `code_outline` | Codebase | Generates structural symbols (classes, methods, functions) using Python AST or multi-language regex. |
| `manage_todos` | Workflow | Adds, marks completed, or lists current agent workflow action items and TODOs. |
| `git_status` | Version Control | Inspects repository status, staged/unstaged changes, and untracked files. |
| `git_diff` | Version Control | Generates unified git diffs for staged or unstaged workspace modifications. |
| `git_commit` | Version Control | Stages modified files and creates git commits with specified commit messages. |
| `manage_checkpoint` | Version Control | Creates named workspace snapshots and restores previous checkpoints instantly (`create`, `restore`, `list`). |
| `fetch_url` | Network | Fetches web pages or APIs over HTTP/HTTPS, extracting plain text / markdown payloads. |
| `search_web` | Internet | Performs live web searches via DuckDuckGo and aggregates contextual result snippets. |
| `bg_command` | Background | Launches persistent background tasks (`start`, `status`, `logs`, `kill`) without blocking execution. |
| `create_skill` | Extensibility | Persists reusable agent instructions and behavioral protocols to `~/.xdharness/skills/<name>.md`. |
| `call_skill` | Extensibility | Reads and executes defined skills, injecting domain-specific prompts directly into context. |
| `create_agent` | Multi-Agent | Defines custom specialized subagent profiles with custom system prompts and authorized toolsets. |
| `spawn_agents` | Multi-Agent | Spawns multiple subagents concurrently in parallel threads to solve cooperative sub-tasks. |
| `manage_plugins` | Extensibility | Manages dynamic plugins (`list`, `install`, `delete`, `info`) from local directories or GitHub repositories. |
| `manage_mcp` | MCP | Manages Model Context Protocol servers (`list`, `add`, `remove`, `ping`, `tools`) over stdio JSON-RPC 2.0. |
| `ask_question` | Interactive | Solicits interactive user feedback or picks from options during autonomous agent runs. |

---

## 🤖 Multi-Agent Orchestration & Swarms

`xdh` enables agents to coordinate subagents for parallel execution:
- **`create_agent`**: Create specialized subagent definitions (e.g. `tester`, `reviewer`, `researcher`, `security_auditor`).
- **`spawn_agents`**: Run multiple agents in parallel background threads. Each agent operates with its own isolated message context and reports results back to the primary supervisor agent.
- **Drawer Status**: Press `F2` or `Ctrl+B` to open the sidecar drawer and monitor running subagent swarms live.

---

## 🔌 Model Context Protocol (MCP) Integration

`xdh` features a zero-dependency stdio JSON-RPC 2.0 client compliant with Anthropic's Model Context Protocol (MCP):
- Configure MCP servers in `~/.xdharness/mcp.json` or dynamically via `/mcp add <name> <command> [args...]`.
- Tools exposed by external MCP servers are automatically registered into the LLM function tool registry.
- Inspect MCP tools with `/mcp tools` or `/mcp ping <name>`.

---

## 🛡️ Atomic Backups, Checkpoints & Undo

### Micro-Edit Backups
Before modifying any existing file on disk, `xdh` automatically writes a backup snapshot to:
```text
~/.xdharness/backups/
└── src_core_app.py.20260907_120000.bak
```
If an edit went wrong, revert it instantly:
```bash
/undo
```

### Full Workspace Checkpoints
For large refactors across multiple files:
```bash
/checkpoint create pre_refactor
# Perform work...
/checkpoint restore pre_refactor
```

---

## ⚡ Staged Diff Workflow

When the agent proposes code refactoring:
1. View pending changes:
   ```bash
   /diff
   ```
2. Confirm and apply:
   ```bash
   /apply
   ```
