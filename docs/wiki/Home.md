# 🏠 Welcome to the xdh Documentation & Wiki

`xdh` (xdharness) is an autonomous terminal agent harness and Text User Interface (TUI) engineered for developer agility, cross-platform portability, high-frequency execution, and resilient model orchestration.

---

## 🧭 Navigation

- **[Getting Started](Getting-Started.md)**: System prerequisites, installation methods, Termux quickstart, CLI options, and initial launch.
- **[Configuration & Providers](Configuration.md)**: Setup OpenAI, OpenRouter, Anthropic, DeepSeek, Groq, Ollama, local models, MCP servers, and permission modes (`safe`, `auto`, `yolo`).
- **[Tools & Capabilities](Tools-and-Capabilities.md)**: Deep dive into all 24 autonomous built-in tools including Skills, Multi-Agent Swarms, AST Outlines, MCP integration, Git, and Checkpoint rollbacks.
- **[Theming Engine](Theming.md)**: Explore the 8 curated color palettes, custom theme definition, and dynamic cycling.
- **[Architecture & Internals](Architecture.md)**: MCP client JSON-RPC 2.0 specs, multi-agent parallel threading, 30 FPS debounced rendering, token compactor, and streaming SSE parser.

---

## 🎯 Design Goals & Core Tenets

1. **True Cross-Platform Portability**: Native feel across Android Termux, Linux distributions, macOS, and Windows PowerShell without heavy compilation or graphics drivers.
2. **Zero-Friction Autonomy**: Unconstrained tool calling rounds with automatic loop guardrails, dynamic task scheduling, and background thread monitoring.
3. **Resilience via Failover**: Network partitions and provider rate limits (`429` / `5xx`) automatically switch across hot standby providers with 5-stage exponential retry backoff.
4. **Safety & Permission Controls**: Choose between `--safe` (interactive confirmation on state changes), `--auto` (guard destructive operations), or `--yolo` (unrestricted velocity), paired with automatic workspace snapshots (`manage_checkpoint` and `~/.xdharness/backups/`).
5. **Multi-Agent Orchestration**: Spin up dedicated, cooperative subagents running concurrently on distinct threads with independent task contexts and message aggregation.
6. **Model Context Protocol (MCP)**: First-class native JSON-RPC 2.0 client connecting to external MCP servers over stdio without external packages.
7. **Ergonomic TUI & Headless Pipe**: 3-segment responsive UI with dynamic expanding composer, sidecar drawer (`F2`/`Ctrl+B`), context ghost suggestions, and headless pipe support (`xdh -p "..."`).
