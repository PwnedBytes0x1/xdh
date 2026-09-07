# 🏠 Welcome to the xdh Documentation & Wiki

`xdh` (xdharness) is an autonomous terminal agent harness and Text User Interface (TUI) engineered for developer agility, cross-platform portability, and resilient model execution.

---

## 🧭 Navigation

- **[Getting Started](Getting-Started.md)**: System prerequisites, installation methods, and initial launch.
- **[Configuration & Providers](Configuration.md)**: Setup OpenAI, OpenRouter, Anthropic, DeepSeek, Groq, Ollama, and local models.
- **[Tools & Capabilities](Tools-and-Capabilities.md)**: Deep dive into autonomous code editing, atomic diffs, web fetching, and tasks.
- **[Theming Engine](Theming.md)**: Explore the 7 built-in themes and color customization.
- **[Architecture & Internals](Architecture.md)**: Token compaction, streaming parser, and asynchronous layout engine.

---

## 🎯 Design Goals

1. **True Cross-Platform Portability**: Native feel across Android Termux, Linux distributions, macOS, and Windows PowerShell without heavy compilation or graphics drivers.
2. **Resilience via Failover**: Network partitions and provider rate limits (429 / 5xx) automatically switch to hot standby providers.
3. **Safety First**: Destructive edits create atomic backups (`~/.xdharness/backups/`) and support instantaneous `/undo`.
4. **Ergonomic UI**: Dynamic expanding input composer, context ghost-suggestions, micro-action status badges, and non-blocking smooth viewport scrolling.
