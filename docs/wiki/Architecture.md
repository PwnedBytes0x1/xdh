# 🏗️ Architecture & Internals

An in-depth guide into how `xdh` manages concurrent streams, asynchronous TUI rendering, token budgets, and tool execution.

---

## 🧩 Core Subsystems

```text
┌─────────────────────────────────────────────────────────────┐
│                       XDHApp (TUI Layer)                    │
│   ┌─────────────────┬───────────────────┬───────────────┐   │
│   │   Header Bar    │ History Viewport  │ Composer VSplit│  │
│   └─────────────────┴───────────────────┴───────────────┘   │
└──────────────────────────────┬──────────────────────────────┘
                               │ UI Events / Async Worker Thread
┌──────────────────────────────▼──────────────────────────────┐
│                    XDHarness (Agent Core)                   │
│   ┌─────────────────────────────────────────────────────┐   │
│   │ Token Compactor & System Prompt Injection            │   │
│   ├─────────────────────────────────────────────────────┤   │
│   │ SSE Streaming Decoder & Delta Tool Accumulator      │   │
│   ├─────────────────────────────────────────────────────┤   │
│   │ Provider Failover Circuit Breaker                   │   │
│   └─────────────────────────────────────────────────────┘   │
└──────────────────────────────┬──────────────────────────────┘
                               │ Tool Dispatch
┌──────────────────────────────▼──────────────────────────────┐
│                   Tool Dispatch Subsystem                   │
│  [bash_run]  [file_io]  [diff_engine]  [web_search/fetch]   │
└─────────────────────────────────────────────────────────────┘
```

---

## ⚡ Non-Blocking UI & Threading Model

To ensure responsiveness when streaming long responses or executing subprocesses:
- **Main Thread**: Runs the `prompt_toolkit.application.Application` event loop handling user input, cursor positioning, and keybindings.
- **Worker Thread**: Agent turns run asynchronously on a dedicated background worker (`run_agent_thread`), parsing Server-Sent Events (SSE) and emitting token chunks without freezing UI frames.
- **Micro-Action Badges**: As tools run, status badges dynamically update the prompt area with informative glyphs.

---

## 🧠 Context Management & Compaction

Long-running conversations automatically respect model context boundaries:
- `count_context_tokens()` tracks approximate token usage against `context_window`.
- When consumption crosses `compaction_threshold` (default `85%`), the compaction pipeline automatically summarizes earlier conversation turns while preserving critical system instructions and recent context.
