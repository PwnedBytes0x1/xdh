# 🚀 Getting Started with xdh

Learn how to install, configure, and launch `xdh` on your preferred system.

---

## 📋 System Requirements

- **Python**: 3.10 or higher
- **Dependencies**: `prompt_toolkit>=3.0.36`, `rich>=13.0.0`
- **Supported Environments**:
  - Android (Termux)
  - Linux (Ubuntu, Debian, Arch, Fedora, Alpine)
  - macOS (Terminal, iTerm2, Kitty, Alacritty)
  - Windows (PowerShell, Windows Terminal)

---

## 📦 Installation Guide

### Option 1: pip (PyPI / Direct)

```bash
pip install xdharness
```

Once installed, invoke directly:
```bash
xdh
# or
xdharness
```

### Option 2: Termux (Android)

```bash
# Update package repos and install python + git
pkg update && pkg install python git -y

# Clone repo
git clone https://github.com/PwnedBytes0x1/xdh.git
cd xdh
pip install -r requirements.txt
pip install -e .

# Create shortcut in PATH
ln -s $(pwd)/xdh.py $PREFIX/bin/xdh
chmod +x $PREFIX/bin/xdh
xdh
```

### Option 3: Manual Clone & Run

```bash
git clone https://github.com/PwnedBytes0x1/xdh.git
cd xdh
pip install -r requirements.txt
python3 xdh.py
```

---

## ⚙️ Initial Configuration

When launched for the first time, `xdh` automatically initializes its directory structure in `~/.xdharness`:

```text
~/.xdharness/
├── config.json          # Provider endpoints, active theme, preferences
├── prompt_history.txt   # Multi-session command history
├── sessions/            # Serialized session states
├── skills/              # Custom agent skills & system extensions
└── backups/             # Automatic pre-edit file snapshots
```

Configure your preferred LLM provider directly in `~/.xdharness/config.json` or by using `/settings` within the TUI.
