# xdh (xdharness)

> Autonomous Terminal Agent Harness & TUI. Cross-platform support for Android Termux, Linux, macOS, and Windows.

## Overview

`xdh` is a high-performance terminal UI and harness for AI agents featuring:
- **3-Segment Layout**: Real-time context header bar, conversational viewport, and dynamic composer.
- **Multi-Provider & Fallback Support**: Compatible with OpenAI, Anthropic, OpenRouter, DeepSeek, Groq, Ollama, LM Studio, and more with auto-failover on rate limits (429/5xx).
- **Built-in Agent Tools**: File inspection/editing with unified diffs, terminal execution, web search & fetch, background task manager, directory trees, and scratchpad memo.
- **Rich Theming**: Built-in themes including Tokyo Night, Dracula, Catppuccin, Monokai, Nord, Cyberpunk, and Gruvbox.
- **Mobile / Termux Optimized**: Touch & keybinding friendly scrolling, ghost autocomplete suggestions, micro-action badges, and minimal resource footprint.

## Installation

```bash
git clone https://github.com/PwnedBytes0x1/xdh.git
cd xdh
pip install -r requirements.txt
chmod +x xdh.py
```

Optional symlink or wrapper:
```bash
ln -s $(pwd)/xdh.py $PREFIX/bin/xdh  # on Termux
# or
ln -s $(pwd)/xdh.py /usr/local/bin/xdh  # on Linux/macOS
```

## Quick Start

Run the harness:
```bash
python3 xdh.py
```

Or check version:
```bash
python3 xdh.py --version
```

## Commands

- `/settings`: Interactive configuration & preferences
- `/provider`: Switch active AI provider (`/provider <name>`)
- `/model`: Switch model (`/model <name>`)
- `/theme`: Switch color palette (`/theme <name>`)
- `/tools`: Toggle autonomous tool calling (`/tools on|off`)
- `/diff`: Review proposed edits and diffs across files
- `/apply`: Apply proposed unified diffs
- `/tasks`: Monitor background tasks (`/tasks list|logs|kill`)
- `/git`: Git status, diff, or commit
- `/search`: Web search query
- `/fetch`: Web page or API reader
- `/help`: Show full list of commands

## License

MIT License.
