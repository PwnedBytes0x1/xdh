# 🏗️ Architecture & Internals

An in-depth guide into how `xdh` manages concurrent streams, asynchronous TUI rendering, multi-agent swarms, Model Context Protocol (MCP) clients, token budgets, and tool execution.

---

## 🧩 Core Subsystems

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                           XDHApp (TUI Layer)                            │
│   ┌─────────────────┬───────────────────┬───────────────┬───────────┐   │
│   │   Header Bar    │ History Viewport  │ Composer Area │  Drawer   │   │
│   └─────────────────┴───────────────────┴───────────────┴───────────┘   │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ UI Events / Debounced 30 FPS Render
┌────────────────────────────────────▼────────────────────────────────────┐
│                         XDHarness (Agent Core)                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │ Token Compactor & System Prompt Injection                       │   │
│   ├─────────────────────────────────────────────────────────────────┤   │
│   │ SSE Streaming Decoder & Delta Tool Call Accumulator             │   │
│   ├─────────────────────────────────────────────────────────────────┤   │
│   │ Multi-Provider Circuit Breaker & 5-Stage Exponential Retry      │   │
│   ├─────────────────────────────────────────────────────────────────┤   │
│   │ Mid-Run User Guidance & ESC Interrupt Interceptor               │   │
│   └─────────────────────────────────────────────────────────────────┘   │
└──────────────────┬─────────────────────────────────┬────────────────────┘
                   │ Tool Execution                  │ Subagent Swarms
┌──────────────────▼───────────────┐ ┌───────────────▼────────────────────┐
│      Built-in Tool Subsystem     │ │   Multi-Agent Thread Pool (Swarms) │
│  [bash] [read/write/replace]     │ │  [tester]   [reviewer]  [planner]  │
│  [git]  [checkpoint] [search]   │ │  Isolated context & parallel queue │
└──────────────────┬───────────────┘ └────────────────────────────────────┘
                   │ External RPC
┌──────────────────▼──────────────────────────────────────────────────────┐
│                    MCP Client (stdio JSON-RPC 2.0)                      │
│   Non-blocking discovery, stdio pipes, schema mapping to tool specs     │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## ⚡ High-Frequency Non-Blocking Rendering (30 FPS Debouncer)

To maintain ultra-smooth UI responsiveness during high-bandwidth token streaming:
- **Rate-Limited Redraws**: Instead of redrawing the entire terminal on every single SSE token or micro-delta, `xdh` utilizes a 30 FPS timestamp throttler (`_last_redraw_time` at ~0.033s intervals).
- **Thread-Safe Invalidation**: Background agent threads call `app.invalidate()` within the debounced window, eliminating terminal flickering and freeing CPU cycles for model processing.
- **Thread-Local Console Caches**: High-frequency Rich rendering objects reuse thread-local consoles, drastically mitigating memory allocation overhead.

---

## 🤖 Multi-Agent Parallel Swarms

When invoking `spawn_agents`:
- Each agent runs in its own distinct background worker thread (`threading.Thread`).
- Subagents receive custom system prompts, authorized tool subsets, and private conversation histories.
- The supervisor coordinates tasks asynchronously and collects structured JSON summaries, surfacing live status indicators in the sidecar drawer panel.

---

## 🔌 Model Context Protocol (MCP) Client Architecture

`xdh` integrates a native, lightweight JSON-RPC 2.0 client:
- **Transport**: Standard I/O (`stdin`/`stdout`/`stderr`) pipes connected to spawned server subprocesses.
- **Lifecycle**: Initializes handshake via `initialize` and `notifications/initialized`, interrogates tools via `tools/list`, and dynamically binds tool execution to `tools/call`.
- **Fault-Isolation**: Server timeouts or pipe closures are caught gracefully, preventing tool crashes from destabilizing the agent harness.

---

## 🧠 Context Management & Compaction

Long-running conversations automatically respect model context boundaries:
- `count_context_tokens()` tracks approximate token usage against `context_window`.
- When consumption crosses `compaction_threshold` (default `85%`), the compaction pipeline automatically summarizes earlier conversation turns while preserving critical system instructions, recent tool outputs, and user requests.
