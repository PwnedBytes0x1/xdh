# 🛠️ Tools & Capabilities

`xdh` ships with a comprehensive set of autonomous tools exposed to LLM function-calling mechanisms.

---

## 🧰 Available Agent Tools

| Tool Name | Scope | Description |
| :--- | :--- | :--- |
| `bash_run` | Shell / System | Runs commands via `/bin/sh` or system shell with timeout safeguards and output truncation. |
| `read_file` | Filesystem | Reads full or windowed line segments of files with encoding fallbacks. |
| `write_file` | Filesystem | Atomically writes contents to disk, automatically creating parent directories and snapshots in `~/.xdharness/backups/`. |
| `edit_file` | Codebase | Performs targeted block replacement using exact or fuzzy diff matching. |
| `diff_files` | Codebase | Generates unified diff representations for inspection before applying changes. |
| `web_search` | Internet | Performs duckduckgo search queries and returns summarized abstracts. |
| `web_fetch` | Network | Fetches HTML or JSON payloads from URLs and parses clean markdown text. |
| `bg_task` | Background | Launches long-running processes asynchronously with log capture. |
| `tree_view` | Project | Generates an intelligent recursive directory tree filtered by `.gitignore`. |

---

## 🛡️ Atomic Backups & The Undo Command

Before modifying any existing file on your machine, `xdh` automatically makes a timestamped copy:

```text
~/.xdharness/backups/
└── src_core_app.py.20260907_120000.bak
```

If a change does not meet your expectations, simply run:
```bash
/undo
```
The agent harness will immediately restore the latest backup snapshot.

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
