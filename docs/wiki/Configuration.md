# ⚙️ Configuration & Providers

`xdh` features a modular multi-provider architecture designed to interface with cloud APIs and local inference engines interchangeably, coupled with granular permission controls and Model Context Protocol (MCP) server support.

---

## 🗂️ Main Configuration File (`~/.xdharness/config.json`)

```json
{
  "current_provider": "openrouter",
  "current_theme": "tokyo_night",
  "active_tools": true,
  "show_thinking": true,
  "permission_mode": "auto",
  "compaction_threshold": 0.85,
  "drawer_open": false,
  "providers": {
    "openrouter": {
      "base_url": "https://openrouter.ai/api/v1/chat/completions",
      "api_key": "sk-or-...",
      "default_model": "anthropic/claude-3.5-sonnet",
      "context_window": 200000
    },
    "openai": {
      "base_url": "https://api.openai.com/v1/chat/completions",
      "api_key": "sk-...",
      "default_model": "gpt-4o",
      "context_window": 128000
    },
    "deepseek": {
      "base_url": "https://api.deepseek.com/chat/completions",
      "api_key": "sk-...",
      "default_model": "deepseek-chat",
      "context_window": 64000
    },
    "ollama": {
      "base_url": "http://localhost:11434/v1/chat/completions",
      "api_key": "ollama",
      "default_model": "llama3.1:latest",
      "context_window": 32000
    }
  }
}
```

---

## 🛡️ Permission Modes

`xdh` provides three distinct safety execution profiles:

1. **`safe`**: Strictest profile. Prompts user for explicit confirmation before executing bash commands, editing files, or calling tools that mutate the environment.
2. **`auto`** *(Default)*: Pragmatic autonomy. Automatically runs read operations, Git queries, and safe tools, but prompts or warns on destructive actions (e.g. `rm -rf`, raw system modification).
3. **`yolo`**: Maximum velocity. Executes all tools and bash commands immediately without interactive prompts.

Switch permission mode at launch or in-session:
```bash
xdh --safe      # Launch in safe mode
xdh --yolo      # Launch in yolo mode
# Inside TUI:
/permission safe
/permission auto
/permission yolo
```

---

## 🔌 MCP Configuration (`~/.xdharness/mcp.json`)

Define Model Context Protocol stdio servers:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/data/data/com.termux/files/home"]
    },
    "sqlite": {
      "command": "uvx",
      "args": ["mcp-server-sqlite", "--db-path", "app.db"]
    }
  }
}
```

Or configure via slash commands:
```bash
/mcp add fetch uvx mcp-server-fetch
/mcp list
/mcp ping fetch
/mcp remove fetch
```

---

## 🔄 Automatic Model Failover & Resilience

- **5-Stage Connection Retry**: When an endpoint suffers transient connection failures or timeouts, `xdh` automatically retries up to 5 times with increasing delays (+5s per retry: 5s, 10s, 15s, 20s, 25s).
- **Auto-Failover Circuit**: When an active provider returns HTTP status `429` (Rate Limit) or `5xx` (Server Error), `xdh` automatically detects configured alternative providers and seamlessly transitions the session without losing context.

---

## 💻 Headless & Pipe CLI Flags

`xdh` supports direct pipeline chaining in shell scripts:

```bash
# Non-interactive one-shot prompt
xdh -p "Review this git diff and write a summary"

# Pipe stdin directly into xdh
git diff | xdh -p "Write conventional commit message" --pipe

# Override provider or model on the fly
xdh -p "Explain AST parsing" --provider openai --model gpt-4o --yolo
```
