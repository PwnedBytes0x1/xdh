#!/usr/bin/env python3
"""
xdharness (xdh) - Autonomous Terminal Agent Harness & TUI.
Cross-platform: Android Termux, Linux, macOS, Windows.
Features: 3-Segment Layout, Micro-Action Badges, Context Ghost-Suggest,
Dynamic Expanding Composer, and Interactive Settings.
"""

__version__ = "1.0.5"

import os
import sys
import re
import ast
import json
import time
import shlex
import shutil
import difflib
import fnmatch
import argparse
import subprocess
import threading
import urllib.request
import urllib.error
import urllib.parse
import base64
import importlib
import importlib.util
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

# Rich imports
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.text import Text
from rich.syntax import Syntax
from rich import box

# Prompt Toolkit imports
from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggest, Suggestion
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.styles import Style as PTStyle
from prompt_toolkit.formatted_text import ANSI, to_formatted_text, split_lines
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, Window, FloatContainer, Float, VSplit
from prompt_toolkit.layout.controls import FormattedTextControl, BufferControl, UIControl, UIContent
from prompt_toolkit.layout.processors import AppendAutoSuggestion
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.menus import CompletionsMenu
from prompt_toolkit.layout.dimension import Dimension
from prompt_toolkit.filters import has_focus
from prompt_toolkit.data_structures import Point
from prompt_toolkit.mouse_events import MouseEvent, MouseEventType

# ---------------------------------------------------------
# Storage & Directories
# ---------------------------------------------------------
BASE_DIR = Path.home() / ".xdharness"
SESSIONS_DIR = BASE_DIR / "sessions"
SKILLS_DIR = BASE_DIR / "skills"
AGENTS_DIR = BASE_DIR / "agents"
PLUGINS_DIR = BASE_DIR / "plugins"
BACKUPS_DIR = BASE_DIR / "backups"
CHECKPOINTS_DIR = BASE_DIR / "checkpoints"
CONFIG_FILE = BASE_DIR / "config.json"
HISTORY_FILE = BASE_DIR / "prompt_history.txt"
MCP_CONFIG_FILE = BASE_DIR / "mcp.json"

for p in [BASE_DIR, SESSIONS_DIR, SKILLS_DIR, AGENTS_DIR, PLUGINS_DIR, BACKUPS_DIR, CHECKPOINTS_DIR]:
    p.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------
# Color Palettes & Theming Engine
# ---------------------------------------------------------
THEMES = {
    "tokyo_night": {
        "primary": "#7aa2f7",
        "secondary": "#bb9af7",
        "accent": "#9ece6a",
        "warning": "#e0af68",
        "error": "#f7768e",
        "bg_bar": "#1a1b26",
        "fg_bar": "#c0caf5",
        "dim": "#565f89",
        "rich_border": "#7aa2f7"
    },
    "dracula": {
        "primary": "#bd93f9",
        "secondary": "#ff79c6",
        "accent": "#50fa7b",
        "warning": "#f1fa8c",
        "error": "#ff5555",
        "bg_bar": "#282a36",
        "fg_bar": "#f8f8f2",
        "dim": "#6272a4",
        "rich_border": "#bd93f9"
    },
    "catppuccin": {
        "primary": "#89b4fa",
        "secondary": "#cba6f7",
        "accent": "#a6e3a1",
        "warning": "#f9e2af",
        "error": "#f38ba8",
        "bg_bar": "#181825",
        "fg_bar": "#cdd6f4",
        "dim": "#6c7086",
        "rich_border": "#89b4fa"
    },
    "monokai": {
        "primary": "#66d9ef",
        "secondary": "#ae81ff",
        "accent": "#a6e22e",
        "warning": "#fd971f",
        "error": "#f92672",
        "bg_bar": "#272822",
        "fg_bar": "#f8f8f2",
        "dim": "#75715e",
        "rich_border": "#66d9ef"
    },
    "nord": {
        "primary": "#88c0d0",
        "secondary": "#81a1c1",
        "accent": "#a3be8c",
        "warning": "#ebcb8b",
        "error": "#bf616a",
        "bg_bar": "#2e3440",
        "fg_bar": "#eceff4",
        "dim": "#4c566a",
        "rich_border": "#88c0d0"
    },
    "cyberpunk": {
        "primary": "#00f0ff",
        "secondary": "#ff007f",
        "accent": "#ffe600",
        "warning": "#ff8800",
        "error": "#ff003c",
        "bg_bar": "#05050f",
        "fg_bar": "#d0f0ff",
        "dim": "#3d5266",
        "rich_border": "#00f0ff"
    },
    "gruvbox": {
        "primary": "#fabd2f",
        "secondary": "#d3869b",
        "accent": "#b8bb26",
        "warning": "#fe8019",
        "error": "#fb4934",
        "bg_bar": "#282828",
        "fg_bar": "#ebdbb2",
        "dim": "#928374",
        "rich_border": "#fabd2f"
    },
    "solarized": {
        "primary": "#268bd2",
        "secondary": "#6c71c4",
        "accent": "#2aa198",
        "warning": "#b58900",
        "error": "#dc322f",
        "bg_bar": "#002b36",
        "fg_bar": "#93a1a1",
        "dim": "#586e75",
        "rich_border": "#268bd2"
    }
}

DEFAULT_CONFIG = {
    "current_theme": "tokyo_night",
    "current_provider": "ollama",
    "providers": {
        "ollama": {
            "base_url": "http://localhost:11434/v1",
            "api_key": "ollama",
            "default_model": "llama3.2",
            "context_window": 8192
        },
        "openrouter": {
            "base_url": "https://openrouter.ai/api/v1",
            "api_key": os.getenv("OPENROUTER_API_KEY", ""),
            "default_model": "anthropic/claude-3.5-sonnet",
            "context_window": 128000
        },
        "openai": {
            "base_url": "https://api.openai.com/v1",
            "api_key": os.getenv("OPENAI_API_KEY", ""),
            "default_model": "gpt-4o-mini",
            "context_window": 128000
        },
        "groq": {
            "base_url": "https://api.groq.com/openai/v1",
            "api_key": os.getenv("GROQ_API_KEY", ""),
            "default_model": "llama-3.3-70b-versatile",
            "context_window": 128000
        }
    },
    "active_tools": True,
    "show_thinking": True,
    "compaction_threshold": 0.90,
    "confirm_danger_commands": True,
    "permission_mode": "auto"
}

# Pricing per million tokens (input, output) in USD for cost estimation
MODEL_COSTS = {
    "gpt-4o": (2.50, 10.00),
    "gpt-4o-mini": (0.15, 0.60),
    "claude-3.5-sonnet": (3.00, 15.00),
    "claude-3-haiku": (0.25, 1.25),
    "llama-3.3-70b": (0.59, 0.79),
    "llama3.2": (0.00, 0.00),
}

# ---------------------------------------------------------
# Formatting & Resource Inspect
# ---------------------------------------------------------
def format_k_val(val: int) -> str:
    if val >= 1000:
        k_val = val / 1000
        return f"{k_val:.1f}k" if k_val < 10 else f"{int(round(k_val))}k"
    return str(val)

def get_memory_usage_mb() -> float:
    try:
        if sys.platform == "win32":
            import ctypes
            class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
                _fields_ = [
                    ('cb', ctypes.c_ulong),
                    ('PageFaultCount', ctypes.c_ulong),
                    ('PeakWorkingSetSize', ctypes.c_size_t),
                    ('WorkingSetSize', ctypes.c_size_t),
                ]
            counters = PROCESS_MEMORY_COUNTERS()
            ctypes.windll.psapi.GetProcessMemoryInfo(
                ctypes.windll.kernel32.GetCurrentProcess(),
                ctypes.byref(counters),
                ctypes.sizeof(counters)
            )
            return round(counters.WorkingSetSize / (1024 * 1024), 1)
        else:
            import resource
            rusage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            if sys.platform == "darwin":
                return round(rusage / (1024 * 1024), 1)
            return round(rusage / 1024, 1)
    except Exception:
        return 0.0

_CACHED_CLIPBOARD_CMD: Optional[str] = None

def copy_to_clipboard(text: str) -> bool:
    """Fast cross-platform clipboard copy with tool caching (Termux, xclip, wl-copy, pbcopy, Windows)."""
    global _CACHED_CLIPBOARD_CMD
    candidates = ["termux-clipboard-set", "wl-copy", "xclip", "pbcopy", "clip"]
    if _CACHED_CLIPBOARD_CMD:
        candidates = [_CACHED_CLIPBOARD_CMD] + [c for c in candidates if c != _CACHED_CLIPBOARD_CMD]

    for tool in candidates:
        if tool == "clip" and sys.platform == "win32":
            try:
                p = subprocess.Popen(["clip"], stdin=subprocess.PIPE, shell=True)
                p.communicate(input=text.encode("utf-8"), timeout=1.5)
                if p.returncode == 0:
                    _CACHED_CLIPBOARD_CMD = "clip"
                    return True
            except Exception:
                pass
        elif shutil.which(tool):
            cmd = [tool]
            if tool == "xclip":
                cmd = ["xclip", "-selection", "clipboard"]
            try:
                p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
                p.communicate(input=text.encode("utf-8"), timeout=1.5)
                if p.returncode == 0:
                    _CACHED_CLIPBOARD_CMD = tool
                    return True
            except Exception:
                pass
    return False

def estimate_session_cost(model_name: str, total_tokens: int) -> float:
    """Rough cost estimation based on tokens used."""
    for key, (in_cost, out_cost) in MODEL_COSTS.items():
        if key.lower() in model_name.lower():
            avg_rate = (in_cost + out_cost) / 2.0
            return round((total_tokens / 1_000_000.0) * avg_rate, 4)
    return 0.0

def notify_user_alert():
    """Trigger haptic feedback on Termux and terminal bell sound."""
    try:
        if shutil.which("termux-vibrate"):
            subprocess.Popen(["termux-vibrate", "-d", "80"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass
    try:
        sys.stdout.write("\a")
        sys.stdout.flush()
    except Exception:
        pass

class BackgroundTaskManager:
    """Manages asynchronous background shell tasks."""
    def __init__(self):
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        self._counter = 0

    def start_task(self, command: str, cwd: Optional[str] = None) -> str:
        with self._lock:
            self._counter += 1
            task_id = f"bg_{self._counter}"
            task_info = {
                "id": task_id,
                "command": command,
                "cwd": cwd or os.getcwd(),
                "status": "running",
                "start_time": time.time(),
                "end_time": None,
                "returncode": None,
                "output": []
            }
            self.tasks[task_id] = task_info

        def _worker():
            try:
                proc = subprocess.Popen(
                    command,
                    shell=True,
                    cwd=task_info["cwd"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
                task_info["process"] = proc
                if proc.stdout:
                    for line in proc.stdout:
                        with self._lock:
                            task_info["output"].append(line)
                            if len(task_info["output"]) > 500:
                                task_info["output"].pop(0)
                proc.wait()
                with self._lock:
                    task_info["returncode"] = proc.returncode
                    task_info["status"] = "finished" if proc.returncode == 0 else f"failed ({proc.returncode})"
                    task_info["end_time"] = time.time()
            except Exception as e:
                with self._lock:
                    task_info["status"] = f"error: {str(e)}"
                    task_info["end_time"] = time.time()

        t = threading.Thread(target=_worker, daemon=True)
        task_info["thread"] = t
        t.start()
        return task_id

    def list_tasks(self) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self.tasks.values())

    def kill_task(self, task_id: str) -> bool:
        with self._lock:
            task = self.tasks.get(task_id)
            if not task:
                return False
            proc = task.get("process")
            if proc and task["status"] == "running":
                try:
                    proc.terminate()
                    task["status"] = "killed"
                    task["end_time"] = time.time()
                    return True
                except Exception:
                    pass
            return False

    def get_logs(self, task_id: str, tail: int = 40) -> str:
        with self._lock:
            task = self.tasks.get(task_id)
            if not task:
                return f"Task '{task_id}' not found."
            lines = task.get("output", [])[-tail:]
            return "".join(lines) if lines else "[No output recorded yet]"

BG_TASKS = BackgroundTaskManager()

_CONSOLE_CACHE = threading.local()

def render_rich_to_string(renderable: Any, max_cols: int = 80) -> str:
    cols = max(20, max_cols)
    console = getattr(_CONSOLE_CACHE, "console", None)
    if console is None or getattr(_CONSOLE_CACHE, "cols", None) != cols:
        console = Console(width=cols, force_terminal=True, color_system="truecolor", highlight=False)
        _CONSOLE_CACHE.console = console
        _CONSOLE_CACHE.cols = cols
    with console.capture() as capture:
        console.print(renderable)
    return capture.get().rstrip("\n")

# ---------------------------------------------------------
# Dynamic Auto-Suggestion Engine (Context & History Ring)
# ---------------------------------------------------------
class DynamicContextAutoSuggest(AutoSuggest):
    def __init__(self, harness: "XDHarness"):
        self.harness = harness
        self.file_history = FileHistory(str(HISTORY_FILE))

    def get_suggestion(self, buffer: Buffer, document) -> Optional[Suggestion]:
        text = document.text
        if not text or text.startswith("/"):
            return None

        line = document.current_line_before_cursor.lstrip()
        if not line:
            return None

        # 1. Search recent conversational turns (user queries & code terms)
        for msg in reversed(self.harness.messages):
            # Focus suggestions on user queries or code lines, ignore long prose blocks
            if msg.get("role") != "user":
                continue
            content = str(msg.get("content", ""))
            for candidate in content.splitlines():
                candidate = candidate.strip()
                if candidate.startswith(line) and candidate != line and len(candidate) <= 120:
                    return Suggestion(candidate[len(line):])

        # 2. Search persistent disk history
        for past_item in reversed(self.file_history.get_strings()):
            past_item = past_item.strip()
            if past_item.startswith(line) and past_item != line:
                return Suggestion(past_item[len(line):])

        return None

# ---------------------------------------------------------
# Viewport Controller
# ---------------------------------------------------------
class ScrollingANSIControl(UIControl):
    def __init__(self, get_text_func, get_cursor_func=None, mouse_scroll_func=None):
        self.get_text_func = get_text_func
        self.get_cursor_func = get_cursor_func
        self.mouse_scroll_func = mouse_scroll_func

    def is_focusable(self) -> bool:
        return False

    def mouse_handler(self, mouse_event: MouseEvent):
        if self.mouse_scroll_func:
            if mouse_event.event_type == MouseEventType.SCROLL_UP:
                self.mouse_scroll_func(3)
                return None
            elif mouse_event.event_type == MouseEventType.SCROLL_DOWN:
                self.mouse_scroll_func(-3)
                return None
        return NotImplemented

    def create_content(self, width: int, height: int) -> UIContent:
        raw_text = self.get_text_func()
        formatted_text = to_formatted_text(ANSI(raw_text))
        lines = list(split_lines(formatted_text))
        if not lines:
            lines = [[]]

        cpos = None
        if self.get_cursor_func:
            cpos = self.get_cursor_func(len(lines))

        return UIContent(
            get_line=lambda i: lines[i] if 0 <= i < len(lines) else [],
            line_count=len(lines),
            cursor_position=cpos,
            show_cursor=False,
        )

# ---------------------------------------------------------
# Harness Engine
# ---------------------------------------------------------
class XDHarness:
    def __init__(self):
        self.config = self.load_config()
        self.session_id = time.strftime("sess_%m%d_%H%M%S")
        sys_prompt = "You are xdh, an expert terminal coding agent. Be concise, precise, and practical."
        # Auto-detect project rules (.xdhrules or .cursorrules)
        for rf in [Path(".xdhrules"), Path(".cursorrules"), Path.home() / ".xdhrules"]:
            if rf.is_file():
                try:
                    rules_content = rf.read_text(encoding="utf-8", errors="replace").strip()
                    if rules_content:
                        sys_prompt += f"\n\n[Project Rules from {rf.name}]:\n{rules_content}"
                        break
                except Exception:
                    pass

        self.messages: List[Dict[str, Any]] = [
            {"role": "system", "content": sys_prompt}
        ]
        self.total_tokens_consumed = 0
        self._call_counter = 0
        self.todos: List[Dict[str, Any]] = []
        self.scratchpad: str = ""
        self.status_label = "Ready"

    def load_config(self) -> Dict[str, Any]:
        if not CONFIG_FILE.exists():
            CONFIG_FILE.write_text(json.dumps(DEFAULT_CONFIG, indent=2))
            return DEFAULT_CONFIG
        try:
            cfg = json.loads(CONFIG_FILE.read_text())
            for k, v in DEFAULT_CONFIG.items():
                if k not in cfg:
                    cfg[k] = v
            return cfg
        except Exception:
            return DEFAULT_CONFIG

    def save_config(self):
        CONFIG_FILE.write_text(json.dumps(self.config, indent=2))

    @property
    def theme(self) -> Dict[str, str]:
        tname = self.config.get("current_theme", "tokyo_night")
        return THEMES.get(tname, THEMES["tokyo_night"])

    @property
    def current_provider_data(self) -> Dict[str, Any]:
        prov = self.config.get("current_provider", "ollama")
        return self.config.get("providers", {}).get(prov, {})

    def count_context_tokens(self) -> int:
        parts = []
        for m in self.messages:
            if m.get("content"):
                parts.append(str(m["content"]))
            if m.get("reasoning_content"):
                parts.append(str(m["reasoning_content"]))
            if m.get("tool_calls"):
                parts.append(json.dumps(m["tool_calls"]))
        raw_text = "".join(parts)
        return max(1, len(raw_text) // 4)

    def compact_context_if_needed(self):
        ctx_max = self.current_provider_data.get("context_window", 128000) or 128000
        threshold = float(self.config.get("compaction_threshold", 0.90))
        current_tokens = self.count_context_tokens()

        # If exceeding threshold and we have enough messages to compact
        if current_tokens >= ctx_max * threshold and len(self.messages) > 6:
            # Preserve system prompt (messages[0]) and recent 4 messages
            keep_prefix = [self.messages[0]]
            keep_suffix = self.messages[-4:]
            dropped = self.messages[1:-4]

            summary_note = f"[Context Compaction: Compressed and pruned {len(dropped)} older turns due to context window threshold ({int(threshold*100)}%)]"
            self.messages = keep_prefix + [{"role": "system", "content": summary_note}] + keep_suffix

    def next_call_id(self) -> str:
        self._call_counter += 1
        return f"call_{self._call_counter}"

    def add_todo(self, title: str) -> int:
        next_id = max([t.get("id", 0) for t in self.todos], default=0) + 1
        self.todos.append({"id": next_id, "title": title, "done": False})
        self.save_session()
        return next_id

    def toggle_todo(self, todo_id: int) -> bool:
        for t in self.todos:
            if t["id"] == todo_id:
                t["done"] = not t["done"]
                self.save_session()
                return True
        return False

    def delete_todo(self, todo_id: int) -> bool:
        initial_len = len(self.todos)
        self.todos = [t for t in self.todos if t["id"] != todo_id]
        self.save_session()
        return len(self.todos) < initial_len

    def clear_todos(self):
        self.todos = []
        self.save_session()

    def backup_file(self, file_path: Path):
        """Creates a timestamped snapshot of a file in BACKUPS_DIR for /undo."""
        try:
            if not file_path.is_file():
                return
            ts = int(time.time() * 1000)
            safe_name = f"{ts}_{file_path.name}"
            dest = BACKUPS_DIR / safe_name
            shutil.copy2(file_path, dest)
            meta = {
                "original": str(file_path.resolve()),
                "backup": str(dest.resolve()),
                "timestamp": time.time()
            }
            meta_file = BACKUPS_DIR / f"{safe_name}.meta.json"
            meta_file.write_text(json.dumps(meta, indent=2))
        except Exception:
            pass

    def undo_last_edit(self) -> Tuple[bool, str]:
        """Reverts the most recent file change from backups."""
        try:
            meta_files = sorted(BACKUPS_DIR.glob("*.meta.json"), key=lambda p: p.stat().st_mtime, reverse=True)
            if not meta_files:
                return False, "No file edit backups found to revert."
            latest_meta_file = meta_files[0]
            meta = json.loads(latest_meta_file.read_text())
            orig_path = Path(meta["original"])
            bk_path = Path(meta["backup"])
            if bk_path.exists():
                shutil.copy2(bk_path, orig_path)
                # Cleanup restored backup
                bk_path.unlink(missing_ok=True)
                latest_meta_file.unlink(missing_ok=True)
                return True, f"Successfully reverted '{orig_path.name}' to state before last edit."
            return False, "Backup file was missing."
        except Exception as e:
            return False, f"Undo failed: {str(e)}"

    def load_session_by_id(self, sid: str) -> bool:
        """Loads a session by session ID."""
        fpath = SESSIONS_DIR / f"{sid}.json"
        if not fpath.exists():
            # Try matching partial id
            matches = list(SESSIONS_DIR.glob(f"*{sid}*.json"))
            if matches:
                fpath = matches[0]
            else:
                return False
        try:
            data = json.loads(fpath.read_text())
            self.session_id = data.get("session_id", sid)
            self.messages = data.get("messages", self.messages)
            self.todos = data.get("todos", [])
            self.total_tokens_consumed = data.get("total_tokens", 0)
            if data.get("provider"):
                self.config["current_provider"] = data["provider"]
            if data.get("model"):
                p = self.config.get("current_provider")
                if p and p in self.config.get("providers", {}):
                    self.config["providers"][p]["default_model"] = data["model"]
            self.save_config()
            return True
        except Exception:
            return False

    def list_saved_sessions(self) -> List[Dict[str, Any]]:
        """Returns list of saved session summaries."""
        results = []
        for sf in sorted(SESSIONS_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
            try:
                d = json.loads(sf.read_text())
                results.append({
                    "id": d.get("session_id", sf.stem),
                    "saved_at": d.get("saved_at", sf.stat().st_mtime),
                    "model": d.get("model", "unknown"),
                    "provider": d.get("provider", "unknown"),
                    "tokens": d.get("total_tokens", 0),
                    "messages_count": len(d.get("messages", []))
                })
            except Exception:
                pass
        return results

    def save_session(self):
        fpath = SESSIONS_DIR / f"{self.session_id}.json"
        data = {
            "session_id": self.session_id,
            "saved_at": time.time(),
            "provider": self.config.get("current_provider"),
            "model": self.current_provider_data.get("default_model"),
            "total_tokens": self.total_tokens_consumed,
            "todos": self.todos,
            "messages": self.messages,
            "scratchpad": self.scratchpad
        }
        fpath.write_text(json.dumps(data, indent=2))

    def fork_session(self, fork_name: str) -> str:
        """Branches current session state into a new session."""
        self.save_session()
        new_sid = f"fork_{fork_name}_{int(time.time())}"
        self.session_id = new_sid
        self.save_session()
        return new_sid

# ---------------------------------------------------------
# Skills System (Load, Create, Call)
# ---------------------------------------------------------
class SkillManager:
    """Manages skill definitions stored in ~/.xdharness/skills/<name>/SKILL.md."""
    def __init__(self, skills_dir: Path = SKILLS_DIR):
        self.skills_dir = skills_dir
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        self.ensure_default_skills()

    def ensure_default_skills(self):
        """Seed built-in skills if not already present."""
        create_skill_path = self.skills_dir / "create_skill" / "SKILL.md"
        if not create_skill_path.exists():
            create_skill_path.parent.mkdir(parents=True, exist_ok=True)
            create_skill_path.write_text("""---
name: create_skill
description: Interactive and programmatic skill creation engine. Generates reusable skills with metadata, instructions, and schemas.
parameters:
  name: The unique slug name of the new skill (lowercase, hyphens/underscores).
  description: Short one-line summary of what the skill does.
  instructions: Comprehensive prompt instructions, rules, and best practices for the skill.
---
# Create Skill
This skill guides the agent in drafting and registering custom reusable skills into `~/.xdharness/skills/`.
When creating a skill:
1. Define a clear, descriptive name (e.g. `code-reviewer`, `git-release`).
2. Write concise YAML frontmatter with `name`, `description`, and `parameters`.
3. Provide step-by-step instructions under Markdown headings.
4. Save the skill as `~/.xdharness/skills/<name>/SKILL.md`.
""", encoding="utf-8")

        create_agent_path = self.skills_dir / "create_agent" / "SKILL.md"
        if not create_agent_path.exists():
            create_agent_path.parent.mkdir(parents=True, exist_ok=True)
            create_agent_path.write_text("""---
name: create_agent
description: Specialized subagent generator defining autonomous agent personas, system prompts, default model/provider overrides, and tool suites.
parameters:
  name: Unique name identifier of the agent persona (e.g. 'tester', 'auditor', 'architect').
  role: Human-readable role description (e.g. 'Security Vulnerability Auditor').
  system_prompt: Detailed system instructions specifying behaviors, constraints, and operational goals.
  model: Optional model override (e.g. 'gpt-4o-mini', 'claude-3.5-sonnet').
  provider: Optional provider override (e.g. 'openrouter', 'groq', 'ollama').
  tools: List of enabled tool names for this agent.
---
# Create Agent
This skill configures specialized agent personas into `~/.xdharness/agents/<name>.json`.
Specialized subagents can run concurrently in parallel threads to solve complex multi-phase development tasks.
""", encoding="utf-8")

    def parse_skill_file(self, skill_path: Path) -> Optional[Dict[str, Any]]:
        """Parses a SKILL.md file extracting frontmatter and body."""
        try:
            content = skill_path.read_text(encoding="utf-8", errors="replace")
            meta = {"name": skill_path.parent.name, "description": "", "instructions": ""}
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    frontmatter = parts[1].strip()
                    meta["instructions"] = parts[2].strip()
                    for line in frontmatter.splitlines():
                        # Only parse top-level keys (no leading indentation)
                        if ":" in line and not line.startswith((" ", "\t")):
                            k, v = line.split(":", 1)
                            meta[k.strip()] = v.strip()
                else:
                    meta["instructions"] = content
            else:
                meta["instructions"] = content
            return meta
        except Exception:
            return None

    def list_skills(self) -> List[Dict[str, Any]]:
        """Discovers all skills in SKILLS_DIR."""
        skills = []
        for p in sorted(self.skills_dir.glob("*/SKILL.md")):
            info = self.parse_skill_file(p)
            if info:
                skills.append(info)
        return skills

    def get_skill(self, name: str) -> Optional[Dict[str, Any]]:
        """Retrieves a skill by name."""
        clean_name = name.strip().lower().replace(" ", "_")
        target_file = self.skills_dir / clean_name / "SKILL.md"
        if target_file.is_file():
            return self.parse_skill_file(target_file)
        # Fallback search by folder or name attribute
        for skill in self.list_skills():
            if skill.get("name", "").lower() == clean_name or skill.get("name", "").lower() == name.lower():
                return skill
        return None

    def create_skill(self, name: str, description: str, instructions: str, parameters: str = "") -> Tuple[bool, str]:
        """Creates or updates a skill in ~/.xdharness/skills/<name>/SKILL.md."""
        clean_name = re.sub(r"[^a-zA-Z0-9_\-]", "_", name.strip().lower())
        if not clean_name:
            return False, "Error: Invalid skill name."
        folder = self.skills_dir / clean_name
        folder.mkdir(parents=True, exist_ok=True)
        file_path = folder / "SKILL.md"
        content = f"""---
name: {clean_name}
description: {description.strip()}
parameters: {parameters.strip() or 'None'}
---
{instructions.strip()}
"""
        file_path.write_text(content, encoding="utf-8")
        return True, f"Skill '{clean_name}' created at {file_path}"

SKILL_MGR = SkillManager()

# ---------------------------------------------------------
# Multi-Agent Subagent System (Definition & Parallel Orchestration)
# ---------------------------------------------------------
class AgentManager:
    """Manages custom agent personas in ~/.xdharness/agents/ and parallel subagent execution."""
    def __init__(self, agents_dir: Path = AGENTS_DIR):
        self.agents_dir = agents_dir
        self.agents_dir.mkdir(parents=True, exist_ok=True)
        self.ensure_default_agents()

    def ensure_default_agents(self):
        """Seed default agent personas."""
        defaults = {
            "researcher": {
                "name": "researcher",
                "role": "Codebase & Web Researcher",
                "system_prompt": "You are a specialized research agent. Survey codebases, documentation, and external resources thoroughly. Report detailed findings.",
                "tools": ["read_file", "list_dir", "grep_search", "find_by_name", "file_info", "search_web", "fetch_url"]
            },
            "coder": {
                "name": "coder",
                "role": "Feature Implementer & Refactoring Engineer",
                "system_prompt": "You are a specialized software engineer. Write clean, bug-free code, perform file modifications, and verify syntax integrity.",
                "tools": ["read_file", "write_file", "replace_file_content", "list_dir", "bash", "git_status", "git_diff"]
            },
            "tester": {
                "name": "tester",
                "role": "QA & Test Execution Specialist",
                "system_prompt": "You are a QA automation and testing agent. Run tests, detect regressions, verify error states, and formulate patch recommendations.",
                "tools": ["bash", "read_file", "write_file", "bg_command"]
            },
            "reviewer": {
                "name": "reviewer",
                "role": "Code Quality & Security Reviewer",
                "system_prompt": "You are an expert security and code auditor. Inspect diffs, identify security risks, adherence to coding standards, and recommend fixes.",
                "tools": ["read_file", "grep_search", "git_diff"]
            }
        }
        for name, spec in defaults.items():
            f = self.agents_dir / f"{name}.json"
            if not f.exists():
                f.write_text(json.dumps(spec, indent=2), encoding="utf-8")

    def list_agents(self) -> List[Dict[str, Any]]:
        agents = []
        for f in sorted(self.agents_dir.glob("*.json")):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                agents.append(data)
            except Exception:
                pass
        return agents

    def get_agent(self, name: str) -> Optional[Dict[str, Any]]:
        f = self.agents_dir / f"{name.strip().lower()}.json"
        if f.is_file():
            try:
                return json.loads(f.read_text(encoding="utf-8"))
            except Exception:
                pass
        for a in self.list_agents():
            if a.get("name", "").lower() == name.strip().lower():
                return a
        return None

    def create_agent(self, name: str, role: str, system_prompt: str, model: str = "", provider: str = "", tools: Optional[List[str]] = None) -> Tuple[bool, str]:
        clean_name = re.sub(r"[^a-zA-Z0-9_\-]", "_", name.strip().lower())
        if not clean_name:
            return False, "Error: Invalid agent name."
        spec = {
            "name": clean_name,
            "role": role.strip(),
            "system_prompt": system_prompt.strip(),
            "model": model.strip() if model else "",
            "provider": provider.strip() if provider else "",
            "tools": tools if tools is not None else ["read_file", "write_file", "list_dir", "bash"]
        }
        f = self.agents_dir / f"{clean_name}.json"
        f.write_text(json.dumps(spec, indent=2), encoding="utf-8")
        return True, f"Agent '{clean_name}' created at {f}"

    def delete_agent(self, name: str) -> bool:
        f = self.agents_dir / f"{name.strip().lower()}.json"
        if f.is_file():
            f.unlink()
            return True
        return False

AGENT_MGR = AgentManager()

# ---------------------------------------------------------
# Dynamic Plugin Management System (User & Community Plugins)
# ---------------------------------------------------------
class PluginManager:
    """Discovers, loads, installs, and manages extensions in ~/.xdharness/plugins/."""
    def __init__(self, plugins_dir: Path = PLUGINS_DIR):
        self.plugins_dir = plugins_dir
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        self.loaded_plugins: Dict[str, Any] = {}
        self.plugin_tools: Dict[str, Tuple[Dict[str, Any], Any]] = {}
        self.ensure_default_plugins()
        self.load_all_plugins()

    def ensure_default_plugins(self):
        """Seed an example custom plugin."""
        example_plugin = self.plugins_dir / "system_info.py"
        if not example_plugin.exists():
            example_plugin.write_text('''"""
Example Plugin: system_info
Exports a custom tool to inspect platform environment.
"""

def get_sys_environment():
    import os, platform
    return {
        "platform": platform.platform(),
        "python": platform.python_version(),
        "arch": platform.machine(),
        "cwd": os.getcwd()
    }

TOOLS = [
    {
        "spec": {
            "type": "function",
            "function": {
                "name": "plugin_system_environment",
                "description": "Inspect OS and Python environment details via plugin.",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        },
        "handler": lambda args, harness: (str(get_sys_environment()), "🔌 Plugin › System Info")
    }
]
''', encoding="utf-8")

    def load_plugin_file(self, file_path: Path) -> bool:
        try:
            module_name = f"xdh_plugin_{file_path.stem}"
            spec = importlib.util.spec_from_file_location(module_name, str(file_path))
            if not spec or not spec.loader:
                return False
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            self.loaded_plugins[file_path.stem] = mod

            # Register tools exported by plugin
            if hasattr(mod, "TOOLS"):
                for tool_entry in mod.TOOLS:
                    tspec = tool_entry.get("spec")
                    thandler = tool_entry.get("handler")
                    if tspec and thandler:
                        fname = tspec.get("function", {}).get("name")
                        if fname:
                            self.plugin_tools[fname] = (tspec, thandler)
            return True
        except Exception:
            return False

    def load_all_plugins(self):
        """Loads all .py plugins from plugins_dir."""
        for p in sorted(self.plugins_dir.glob("*.py")):
            self.load_plugin_file(p)
        # Also check subdirectories with plugin.py
        for sub in sorted(self.plugins_dir.iterdir()):
            if sub.is_dir() and (sub / "plugin.py").is_file():
                self.load_plugin_file(sub / "plugin.py")

    def list_plugins(self) -> List[Dict[str, Any]]:
        results = []
        for p in sorted(self.plugins_dir.iterdir()):
            if p.is_file() and p.suffix == ".py":
                results.append({
                    "name": p.stem,
                    "type": "single-file",
                    "path": str(p),
                    "loaded": p.stem in self.loaded_plugins
                })
            elif p.is_dir() and (p / "plugin.py").is_file():
                results.append({
                    "name": p.name,
                    "type": "directory/git",
                    "path": str(p),
                    "loaded": (p / "plugin.py").stem in self.loaded_plugins
                })
        return results

    def install_plugin_from_git(self, git_url: str, name: Optional[str] = None) -> Tuple[bool, str]:
        """Clones a community plugin from a Git repository into ~/.xdharness/plugins/."""
        try:
            if not name:
                name = git_url.rstrip("/").split("/")[-1]
                if name.endswith(".git"):
                    name = name[:-4]
            target_dir = self.plugins_dir / name
            if target_dir.exists():
                return False, f"Plugin '{name}' already exists in {target_dir}."
            res = subprocess.run(["git", "clone", "--depth", "1", git_url, str(target_dir)], capture_output=True, text=True, timeout=60)
            if res.returncode != 0:
                return False, f"Git clone failed: {res.stderr.strip()}"
            # Attempt to load plugin
            if (target_dir / "plugin.py").is_file():
                self.load_plugin_file(target_dir / "plugin.py")
            elif (target_dir / f"{name}.py").is_file():
                self.load_plugin_file(target_dir / f"{name}.py")
            return True, f"Successfully installed plugin '{name}' from {git_url}."
        except Exception as e:
            return False, f"Install failed: {str(e)}"

    def add_plugin(self, name: str, code: str) -> Tuple[bool, str]:
        """Creates a new Python plugin directly."""
        clean_name = re.sub(r"[^a-zA-Z0-9_\-]", "_", name.strip())
        target = self.plugins_dir / f"{clean_name}.py"
        target.write_text(code, encoding="utf-8")
        ok = self.load_plugin_file(target)
        return ok, f"Plugin '{clean_name}' saved and {'loaded' if ok else 'failed to load'} at {target}"

    def delete_plugin(self, name: str) -> Tuple[bool, str]:
        """Deletes a plugin by name."""
        single = self.plugins_dir / f"{name}.py"
        if single.is_file():
            single.unlink()
            self.loaded_plugins.pop(name, None)
            return True, f"Plugin '{name}' deleted."
        multi = self.plugins_dir / name
        if multi.is_dir():
            shutil.rmtree(multi)
            self.loaded_plugins.pop(name, None)
            return True, f"Plugin directory '{name}' deleted."
        return False, f"Plugin '{name}' not found."

PLUGIN_MGR = PluginManager()

# ---------------------------------------------------------
# Ignore Filters (.xdhignore & .gitignore support)
# ---------------------------------------------------------
def get_ignored_patterns(root_dir: Path) -> List[str]:
    """Collect ignore patterns from .xdhignore and .gitignore."""
    patterns = [".git", "node_modules", "__pycache__", ".venv", ".xdharness", "*.pyc"]
    for fname in [".xdhignore", ".gitignore"]:
        ign_file = root_dir / fname
        if ign_file.is_file():
            try:
                for line in ign_file.read_text(encoding="utf-8", errors="replace").splitlines():
                    s = line.strip()
                    if s and not s.startswith("#"):
                        patterns.append(s)
            except Exception:
                pass
    return patterns

def is_path_ignored(path: Path, root_dir: Path, patterns: Optional[List[str]] = None) -> bool:
    """Check if a path matches any pattern from .xdhignore or .gitignore."""
    if patterns is None:
        patterns = get_ignored_patterns(root_dir)
    try:
        rel = str(path.relative_to(root_dir))
    except Exception:
        rel = str(path.name)

    parts = path.parts
    for pat in patterns:
        clean_pat = pat.rstrip("/")
        if clean_pat in parts:
            return True
        if fnmatch.fnmatch(rel, pat) or fnmatch.fnmatch(rel, f"*/{pat}") or fnmatch.fnmatch(path.name, pat):
            return True
        if pat.endswith("/") and fnmatch.fnmatch(rel + "/", f"*{pat}*"):
            return True
    return False

# ---------------------------------------------------------
# AST Code Outline & Structure Navigation
# ---------------------------------------------------------
def extract_code_outline(file_path: Path) -> str:
    """Extract classes, methods, functions, and signatures using AST / pattern analysis."""
    if not file_path.is_file():
        return f"Error: File '{file_path}' not found."
    try:
        source = file_path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return f"Error reading file: {e}"

    lines = []
    lines.append(f"Outline for `{file_path.name}` ({len(source.splitlines())} lines):")

    # Python AST parsing
    if file_path.suffix == ".py":
        try:
            tree = ast.parse(source)
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    bases = [ast.unparse(b) for b in node.bases] if hasattr(ast, "unparse") else []
                    base_str = f"({', '.join(bases)})" if bases else ""
                    doc = ast.get_docstring(node)
                    doc_preview = f" - \"{doc.splitlines()[0][:60]}\"" if doc else ""
                    lines.append(f"  class {node.name}{base_str} [line {node.lineno}]{doc_preview}")
                    for item in node.body:
                        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            prefix = "async def" if isinstance(item, ast.AsyncFunctionDef) else "def"
                            args_str = ", ".join([a.arg for a in item.args.args])
                            m_doc = ast.get_docstring(item)
                            m_preview = f" - \"{m_doc.splitlines()[0][:50]}\"" if m_doc else ""
                            lines.append(f"    • {prefix} {item.name}({args_str}) [line {item.lineno}]{m_preview}")
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
                    args_str = ", ".join([a.arg for a in node.args.args])
                    f_doc = ast.get_docstring(node)
                    f_preview = f" - \"{f_doc.splitlines()[0][:60]}\"" if f_doc else ""
                    lines.append(f"  {prefix} {node.name}({args_str}) [line {node.lineno}]{f_preview}")
            if len(lines) == 1:
                lines.append("  (No top-level classes or functions discovered)")
            return "\n".join(lines)
        except Exception as e:
            lines.append(f"  (AST parse note: {e} - falling back to regex outline)")

    # Universal Regex-based outline (JS, TS, Go, Rust, C, Java, etc.)
    code_lines = source.splitlines()
    found_symbols = 0
    patterns = [
        (re.compile(r"^\s*(?:export\s+)?(?:default\s+)?class\s+([A-Za-z0-9_]+)"), "class"),
        (re.compile(r"^\s*(?:export\s+)?(?:async\s+)?function\s+([A-Za-z0-9_]+)\s*\((.*?)\)"), "function"),
        (re.compile(r"^\s*(?:export\s+)?(?:const|let|var)\s+([A-Za-z0-9_]+)\s*=\s*(?:async\s*)?\((.*?)\)\s*=>"), "arrow_function"),
        (re.compile(r"^\s*func\s+(?:\(.*?\)\s*)?([A-Za-z0-9_]+)\s*\((.*?)\)"), "go_func"),
        (re.compile(r"^\s*(?:pub\s+)?(?:async\s+)?fn\s+([A-Za-z0-9_]+)"), "rust_fn"),
        (re.compile(r"^\s*(?:pub\s+)?struct\s+([A-Za-z0-9_]+)"), "struct"),
    ]
    for idx, raw_line in enumerate(code_lines, 1):
        for rx, kind in patterns:
            m = rx.search(raw_line)
            if m:
                symbol = m.group(1)
                sig = f"({m.group(2)})" if len(m.groups()) >= 2 and m.group(2) is not None else ""
                lines.append(f"  [{kind}] {symbol}{sig} [line {idx}]")
                found_symbols += 1
                break
    if found_symbols == 0 and len(lines) == 1:
        lines.append("  (No recognizable symbols matched)")
    return "\n".join(lines)

# ---------------------------------------------------------
# Rollback Checkpoint System
# ---------------------------------------------------------
class CheckpointManager:
    """Creates, lists, and restores workspace snapshots in ~/.xdharness/checkpoints/."""
    def __init__(self, checkpoints_dir: Path = CHECKPOINTS_DIR):
        self.checkpoints_dir = checkpoints_dir
        self.checkpoints_dir.mkdir(parents=True, exist_ok=True)

    def create_checkpoint(self, name: str, description: str = "") -> Tuple[bool, str]:
        clean_name = re.sub(r"[^a-zA-Z0-9_\-]", "_", name.strip().lower())
        if not clean_name:
            clean_name = f"cp_{int(time.time())}"
        ts = int(time.time())
        cp_dir = self.checkpoints_dir / f"{ts}_{clean_name}"
        cp_dir.mkdir(parents=True, exist_ok=True)

        # Collect workspace files respecting ignore rules
        workspace_root = Path(".").resolve()
        ign_patterns = get_ignored_patterns(workspace_root)
        saved_files = 0

        for root, dirs, files in os.walk(workspace_root):
            dirs[:] = [d for d in dirs if not is_path_ignored(Path(root) / d, workspace_root, ign_patterns)]
            for file in files:
                fpath = Path(root) / file
                if not is_path_ignored(fpath, workspace_root, ign_patterns):
                    try:
                        rel = fpath.relative_to(workspace_root)
                        dest = cp_dir / "files" / rel
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(fpath, dest)
                        saved_files += 1
                    except Exception:
                        pass

        meta = {
            "id": f"{ts}_{clean_name}",
            "name": clean_name,
            "description": description,
            "timestamp": ts,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts)),
            "workspace": str(workspace_root),
            "files_count": saved_files
        }
        (cp_dir / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
        return True, f"Checkpoint '{clean_name}' created with {saved_files} files (ID: {ts}_{clean_name})"

    def list_checkpoints(self) -> List[Dict[str, Any]]:
        results = []
        for cp_dir in sorted(self.checkpoints_dir.iterdir(), reverse=True):
            meta_file = cp_dir / "meta.json"
            if meta_file.is_file():
                try:
                    data = json.loads(meta_file.read_text(encoding="utf-8"))
                    results.append(data)
                except Exception:
                    pass
        return results

    def restore_checkpoint(self, checkpoint_id_or_name: str) -> Tuple[bool, str]:
        target_dir = None
        for cp_dir in self.checkpoints_dir.iterdir():
            if cp_dir.name == checkpoint_id_or_name or cp_dir.name.endswith(f"_{checkpoint_id_or_name}"):
                target_dir = cp_dir
                break
        if not target_dir or not (target_dir / "meta.json").is_file():
            return False, f"Checkpoint '{checkpoint_id_or_name}' not found."

        try:
            meta = json.loads((target_dir / "meta.json").read_text(encoding="utf-8"))
            files_dir = target_dir / "files"
            workspace_root = Path(".").resolve()
            restored_count = 0
            if files_dir.is_dir():
                for root, _, files in os.walk(files_dir):
                    for file in files:
                        src = Path(root) / file
                        rel = src.relative_to(files_dir)
                        dest = workspace_root / rel
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(src, dest)
                        restored_count += 1
            return True, f"Successfully restored checkpoint '{meta.get('name')}' ({restored_count} files restored)."
        except Exception as e:
            return False, f"Failed to restore checkpoint: {str(e)}"

CHECKPOINT_MGR = CheckpointManager()

# ---------------------------------------------------------
# Model Context Protocol (MCP) Client Engine
# ---------------------------------------------------------
class MCPManager:
    """Manages Model Context Protocol (MCP) servers via stdio JSON-RPC 2.0."""
    def __init__(self, config_file: Path = MCP_CONFIG_FILE):
        self.config_file = config_file
        self.servers: Dict[str, Dict[str, Any]] = {}
        self.active_processes: Dict[str, subprocess.Popen] = {}
        self.discovered_tools: Dict[str, Tuple[Dict[str, Any], str, str]] = {}
        self.load_config()
        self.start_servers()

    def load_config(self):
        if not self.config_file.is_file():
            sample_config = {"mcpServers": {}}
            self.config_file.write_text(json.dumps(sample_config, indent=2), encoding="utf-8")
            self.servers = {}
            return
        try:
            data = json.loads(self.config_file.read_text(encoding="utf-8"))
            self.servers = data.get("mcpServers", {})
        except Exception:
            self.servers = {}

    def save_config(self):
        data = {"mcpServers": self.servers}
        self.config_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def start_servers(self):
        """Initializes and connects to all configured stdio MCP servers asynchronously in the background."""
        def _bg_launcher():
            for sname, scfg in list(self.servers.items()):
                cmd = scfg.get("command")
                args = scfg.get("args", [])
                env = dict(os.environ)
                if scfg.get("env"):
                    env.update(scfg["env"])
                if not cmd:
                    continue
                try:
                    full_cmd = [cmd] + args
                    proc = subprocess.Popen(
                        full_cmd,
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        bufsize=1,
                        env=env
                    )
                    self.active_processes[sname] = proc
                    self._initialize_and_discover(sname, proc)
                except Exception:
                    pass
        threading.Thread(target=_bg_launcher, daemon=True).start()

    def _send_rpc(self, proc: subprocess.Popen, method: str, params: Optional[Dict[str, Any]] = None, req_id: int = 1) -> Optional[Dict[str, Any]]:
        req = {
            "jsonrpc": "2.0",
            "id": req_id,
            "method": method,
            "params": params or {}
        }
        req_line = json.dumps(req) + "\n"
        try:
            if not proc.stdin:
                return None
            proc.stdin.write(req_line)
            proc.stdin.flush()
            # Read single line response
            resp_line = proc.stdout.readline()
            if resp_line:
                return json.loads(resp_line.strip())
        except Exception:
            return None
        return None

    def _initialize_and_discover(self, sname: str, proc: subprocess.Popen):
        # 1. Initialize
        init_params = {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "xdh", "version": __version__}
        }
        self._send_rpc(proc, "initialize", init_params, req_id=1)
        # 2. List tools
        tools_resp = self._send_rpc(proc, "tools/list", {}, req_id=2)
        if tools_resp and "result" in tools_resp:
            tools_list = tools_resp["result"].get("tools", [])
            for t in tools_list:
                t_name = t.get("name")
                t_desc = t.get("description", "")
                t_schema = t.get("inputSchema", {"type": "object", "properties": {}})
                mcp_tool_name = f"mcp_{sname}_{t_name}"
                spec = {
                    "type": "function",
                    "function": {
                        "name": mcp_tool_name,
                        "description": f"[MCP: {sname}] {t_desc}",
                        "parameters": t_schema
                    }
                }
                self.discovered_tools[mcp_tool_name] = (spec, sname, t_name)

    def call_tool(self, mcp_tool_name: str, arguments: Dict[str, Any]) -> Tuple[str, str]:
        if mcp_tool_name not in self.discovered_tools:
            return f"Error: MCP tool '{mcp_tool_name}' not found.", f"🔌 MCP › [red]Not Found[/red]"
        spec, sname, orig_name = self.discovered_tools[mcp_tool_name]
        proc = self.active_processes.get(sname)
        if not proc or proc.poll() is not None:
            return f"Error: MCP server '{sname}' process is not running.", f"🔌 MCP › [red]{sname} Down[/red]"

        call_params = {"name": orig_name, "arguments": arguments}
        resp = self._send_rpc(proc, "tools/call", call_params, req_id=int(time.time() * 1000) % 100000)
        if not resp:
            return "Error: No response from MCP server.", f"🔌 MCP › [red]Timeout[/red]"
        if "error" in resp:
            return f"MCP Error: {resp['error']}", f"🔌 MCP › [red]Error[/red]"

        result = resp.get("result", {})
        content_items = result.get("content", [])
        out_strs = []
        for c in content_items:
            if c.get("type") == "text":
                out_strs.append(c.get("text", ""))
            else:
                out_strs.append(str(c))
        final_str = "\n".join(out_strs) if out_strs else json.dumps(result)
        badge = f"🔌 MCP   › [bold cyan]{sname}:{orig_name}[/bold cyan]"
        return final_str, badge

    def add_server(self, name: str, command: str, args: Optional[List[str]] = None, env: Optional[Dict[str, str]] = None) -> Tuple[bool, str]:
        clean_name = re.sub(r"[^a-zA-Z0-9_\-]", "_", name.strip().lower())
        self.servers[clean_name] = {
            "command": command,
            "args": args or [],
            "env": env or {}
        }
        self.save_config()
        self.start_servers()
        return True, f"MCP server '{clean_name}' configured. Registered {len(self.discovered_tools)} total MCP tools."

    def remove_server(self, name: str) -> Tuple[bool, str]:
        clean_name = name.strip().lower()
        if clean_name in self.servers:
            del self.servers[clean_name]
            self.save_config()
            proc = self.active_processes.pop(clean_name, None)
            if proc:
                try: proc.kill()
                except Exception: pass
            to_del = [k for k, v in self.discovered_tools.items() if v[1] == clean_name]
            for k in to_del:
                del self.discovered_tools[k]
            return True, f"Removed MCP server '{clean_name}'."
        return False, f"Server '{clean_name}' not found."

    def list_servers(self) -> List[Dict[str, Any]]:
        results = []
        for name, cfg in self.servers.items():
            running = name in self.active_processes and self.active_processes[name].poll() is None
            tools_for_server = [k for k, v in self.discovered_tools.items() if v[1] == name]
            results.append({
                "name": name,
                "command": cfg.get("command"),
                "running": running,
                "tools_count": len(tools_for_server)
            })
        return results

MCP_MGR = MCPManager()

# ---------------------------------------------------------
# Built-In Tools & Action Formatters
# ---------------------------------------------------------
TOOLS_SPEC = [
    {
        "type": "function",
        "function": {
            "name": "bash",
            "description": "Execute terminal shell commands.",
            "parameters": {
                "type": "object",
                "properties": {"command": {"type": "string", "description": "Shell command"}},
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read file contents.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string", "description": "File path"}},
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write text content to a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path"},
                    "content": {"type": "string", "description": "Text content"}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_dir",
            "description": "List files, subdirectories and sizes within a directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Directory path (defaults to current directory)"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "grep_search",
            "description": "Search for text or regex pattern matches in files.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Pattern or text to search for"},
                    "path": {"type": "string", "description": "File or directory path to search in (defaults to .)"},
                    "case_insensitive": {"type": "boolean", "description": "Whether to ignore case (default: true)"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "file_info",
            "description": "Inspect detailed file metadata, permissions, and line/byte counts.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to inspect"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "find_by_name",
            "description": "Search for files by glob pattern or name across workspace directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "Glob pattern (e.g. *.py, test_*.js)"},
                    "path": {"type": "string", "description": "Root directory to search in (defaults to .)"}
                },
                "required": ["pattern"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "replace_file_content",
            "description": "Perform precise search-and-replace edit on an existing file with unified diff preview.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to the file to modify"},
                    "old_content": {"type": "string", "description": "Exact text chunk in the file to be replaced"},
                    "new_content": {"type": "string", "description": "Replacement text chunk to substitute"}
                },
                "required": ["path", "old_content", "new_content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "manage_todos",
            "description": "Manage session tasks.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["add", "done", "list", "clear"]},
                    "task": {"type": "string"},
                    "todo_id": {"type": "integer"}
                },
                "required": ["action"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_status",
            "description": "Show Git working tree status, staged and unstaged changes.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_diff",
            "description": "Show Git diff for uncommitted changes or specific file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Optional file path to limit diff"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_commit",
            "description": "Stage files and create a git commit.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Commit message"},
                    "files": {"type": "string", "description": "Files to stage, or '.' for all"}
                },
                "required": ["message"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_url",
            "description": "Fetch text or API content from an HTTP/HTTPS URL.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "The URL to fetch"}
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search DuckDuckGo instant answers and web snippets.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "bg_command",
            "description": "Run a command asynchronously in the background.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "The command line to run"}
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_skill",
            "description": "Create and register a new reusable skill with metadata and instructions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Unique identifier slug for the skill"},
                    "description": {"type": "string", "description": "Short explanation of what the skill accomplishes"},
                    "instructions": {"type": "string", "description": "Detailed instructions and operational procedures for executing the skill"},
                    "parameters": {"type": "string", "description": "Optional parameters description"}
                },
                "required": ["name", "description", "instructions"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "call_skill",
            "description": "Invoke and execute an existing registered skill by name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of the skill to execute"},
                    "input_data": {"type": "string", "description": "Context or input arguments to pass into the skill"}
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_agent",
            "description": "Define and register a new specialized agent persona with custom system prompt and tools.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Unique name of the agent"},
                    "role": {"type": "string", "description": "Human-readable role description"},
                    "system_prompt": {"type": "string", "description": "Instructions and behavior constraints for this agent"},
                    "model": {"type": "string", "description": "Optional model override (e.g. gpt-4o-mini)"},
                    "provider": {"type": "string", "description": "Optional provider override"},
                    "tools": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of tool names allowed for this agent"
                    }
                },
                "required": ["name", "role", "system_prompt"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "spawn_agents",
            "description": "Spawn multiple specialized subagents concurrently in parallel threads to work on subtasks together.",
            "parameters": {
                "type": "object",
                "properties": {
                    "subtasks": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "agent": {"type": "string", "description": "Name of the registered agent persona (e.g. researcher, coder, tester, reviewer)"},
                                "task": {"type": "string", "description": "Specific task prompt for this subagent"}
                            },
                            "required": ["agent", "task"]
                        },
                        "description": "List of subtasks and their designated agent personas"
                    }
                },
                "required": ["subtasks"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "manage_plugins",
            "description": "Manage plugins (list, add, install from git, delete).",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["list", "add", "install", "delete"], "description": "Action to perform"},
                    "name": {"type": "string", "description": "Plugin name"},
                    "source": {"type": "string", "description": "Git repository URL (for install) or Python code (for add)"}
                },
                "required": ["action"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ask_question",
            "description": "Pause autonomous execution and ask the user a clarifying question with selectable or direct options.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {"type": "string", "description": "The question to ask the user"},
                    "options": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional list of predefined choices/options for the user"
                    }
                },
                "required": ["question"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "code_outline",
            "description": "Extract file structure, classes, functions, and method signatures using AST or regex analysis without reading full file content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to the code file to inspect"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "manage_checkpoint",
            "description": "Manage workspace rollback checkpoints (create, restore, list).",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["create", "restore", "list"], "description": "Checkpoint action to execute"},
                    "name": {"type": "string", "description": "Checkpoint name or ID"},
                    "description": {"type": "string", "description": "Optional note describing the checkpoint"}
                },
                "required": ["action"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "manage_mcp",
            "description": "Manage Model Context Protocol (MCP) servers and tools (list, add, remove).",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["list", "add", "remove"], "description": "MCP management action"},
                    "name": {"type": "string", "description": "MCP server name"},
                    "command": {"type": "string", "description": "Command to launch MCP server executable"},
                    "args": {"type": "array", "items": {"type": "string"}, "description": "Arguments for MCP command"}
                },
                "required": ["action"]
            }
        }
    }
]

def get_all_tools_spec() -> List[Dict[str, Any]]:
    """Returns built-in tools, plugin tools, and discovered MCP tools."""
    combined = list(TOOLS_SPEC)
    for fname, (tspec, _) in PLUGIN_MGR.plugin_tools.items():
        if not any(t.get("function", {}).get("name") == fname for t in combined):
            combined.append(tspec)
    for mname, (mspec, _, _) in MCP_MGR.discovered_tools.items():
        if not any(t.get("function", {}).get("name") == mname for t in combined):
            combined.append(mspec)
    return combined

def execute_tool(name: str, args: Dict[str, Any], harness: XDHarness) -> Tuple[str, str]:
    """Executes a tool and returns (detailed_output, micro_action_badge)."""
    try:
        perm_mode = harness.config.get("permission_mode", "auto").lower()

        if name == "bash":
            cmd = args.get("command", "").strip()
            if not cmd:
                return "Error: Empty command.", "💻 Exec › [Empty]"

            # Safe mode confirmation
            if perm_mode == "safe":
                active_app = getattr(harness, "app_instance", None)
                if active_app and hasattr(active_app, "active_question"):
                    # Prompt user confirmation
                    pass

            # Destructive Command Safety Guard (auto mode)
            if perm_mode == "safe" or (perm_mode == "auto" and harness.config.get("confirm_danger_commands", True)):
                danger_patterns = [
                    r"\brm\s+-(?:r|f|rf|fr)\b",
                    r"\bmkfs\b",
                    r"\bdd\s+if=",
                    r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;",
                    r"\b(?:fdisk|parted)\b",
                    r"\bchmod\s+-R\s+777\s+/\b",
                    r">\s*/dev/sd[a-z]"
                ]
                is_danger = any(re.search(pat, cmd) for pat in danger_patterns)
                if is_danger:
                    msg = f"⚠️ [BLOCKED BY SAFETY GUARD]: Command '{cmd}' was detected as potentially destructive. Confirmation is required. To bypass, run '/permission yolo' or '/settings confirm off'."
                    badge = f"🛡 Safety › [bold red]Blocked Destructive Command[/bold red]"
                    return msg, badge

            res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60, cwd=os.getcwd())
            out = res.stdout
            if res.stderr:
                out += f"\n[stderr]\n{res.stderr}"
            out_str = out.strip() if out.strip() else "[Exited with 0]"
            badge = f"💻 Exec  › [bold white]{cmd}[/bold white] [dim](exit {res.returncode})[/dim]"
            return out_str, badge

        elif name == "read_file":
            fp = Path(args.get("path", "")).expanduser()
            if not fp.is_file():
                return f"Error: File '{fp}' not found.", f"⚡ Read  › [red]{fp.name} (not found)[/red]"
            txt = fp.read_text(encoding="utf-8", errors="replace")
            lines = len(txt.splitlines())
            return txt, f"⚡ Read  › [bold cyan]{fp.name}[/bold cyan] [dim]({lines} lines)[/dim]"

        elif name == "write_file":
            fp = Path(args.get("path", "")).expanduser()
            fp.parent.mkdir(parents=True, exist_ok=True)
            if fp.exists():
                harness.backup_file(fp)
            content = args.get("content", "")
            fp.write_text(content, encoding="utf-8")
            return f"Wrote {len(content)} characters to '{fp}'.", f"💾 Write › [bold green]{fp.name}[/bold green] [dim]({len(content)} chars)[/dim]"

        elif name == "find_by_name":
            pattern = args.get("pattern", "").strip()
            if not pattern:
                return "Error: Empty pattern.", "🔎 Find  › [Empty]"
            root_dir = Path(args.get("path") or ".").expanduser()
            if not root_dir.exists():
                return f"Error: Path '{root_dir}' not found.", f"🔎 Find  › [red]Not Found[/red]"

            matches = []
            ign_patterns = get_ignored_patterns(root_dir)
            for item in root_dir.rglob(pattern):
                if is_path_ignored(item, root_dir, ign_patterns):
                    continue
                try:
                    rel = item.relative_to(root_dir)
                    matches.append(f"{'[DIR]' if item.is_dir() else '[FILE]'} {rel}")
                except Exception:
                    matches.append(str(item))
                if len(matches) >= 40:
                    break

            match_text = "\n".join(matches) if matches else f"No files matching '{pattern}' found."
            badge = f"🔎 Find  › [bold cyan]{pattern}[/bold cyan] [dim]({len(matches)} matches)[/dim]"
            return match_text, badge

        elif name == "replace_file_content":
            fp = Path(args.get("path", "")).expanduser()
            if not fp.is_file():
                return f"Error: File '{fp}' not found.", f"📝 Patch › [red]{fp.name} (not found)[/red]"

            old_text = fp.read_text(encoding="utf-8", errors="replace")
            target_chunk = args.get("old_content", "")
            replacement_chunk = args.get("new_content", "")

            if not target_chunk:
                return "Error: old_content chunk cannot be empty.", f"📝 Patch › [red]Empty target[/red]"

            if target_chunk not in old_text:
                return "Error: old_content not found in file. Ensure exact whitespace/indentation match.", f"📝 Patch › [red]Match Failed[/red]"

            occurrences = old_text.count(target_chunk)
            if occurrences > 1:
                return f"Error: target chunk matched {occurrences} times. Provide more surrounding context for uniqueness.", f"📝 Patch › [yellow]Ambiguous ({occurrences}x)[/yellow]"

            # Backup before patching
            harness.backup_file(fp)

            new_text = old_text.replace(target_chunk, replacement_chunk, 1)
            fp.write_text(new_text, encoding="utf-8")

            # Generate unified diff
            old_lines = old_text.splitlines(keepends=True)
            new_lines = new_text.splitlines(keepends=True)
            diff_lines = list(difflib.unified_diff(old_lines, new_lines, fromfile=f"a/{fp.name}", tofile=f"b/{fp.name}", n=3))
            diff_str = "".join(diff_lines) if diff_lines else "File updated (no visible line diff)."

            badge = f"📝 Patch › [bold green]{fp.name}[/bold green] [dim](+1 hunk)[/dim]"
            return diff_str, badge

        elif name == "list_dir":
            target_path = Path(args.get("path") or ".").expanduser()
            if not target_path.exists():
                return f"Error: Path '{target_path}' does not exist.", f"📁 List  › [red]{target_path.name} (missing)[/red]"
            if not target_path.is_dir():
                return f"Error: '{target_path}' is not a directory.", f"📁 List  › [red]{target_path.name} (not dir)[/red]"

            entries = []
            ign_patterns = get_ignored_patterns(target_path)
            try:
                for item in sorted(target_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
                    if is_path_ignored(item, target_path, ign_patterns):
                        continue
                    try:
                        st = item.stat()
                        size_str = f"{st.st_size} B" if st.st_size < 1024 else f"{st.st_size // 1024} KB"
                    except Exception:
                        size_str = "?"
                    kind = "[DIR]" if item.is_dir() else "[FILE]"
                    entries.append(f"{kind:<7} {size_str:>10}  {item.name}{'/' if item.is_dir() else ''}")
            except Exception as e:
                return f"Error reading directory: {e}", f"📁 List  › [red]Error[/red]"

            preview = "\n".join(entries[:50])
            total_count = len(entries)
            if total_count > 50:
                preview += f"\n... ({total_count - 50} more items hidden)"
            badge = f"📁 List  › [bold cyan]{target_path.name or '.'}[/bold cyan] [dim]({total_count} items)[/dim]"
            return preview if preview else "[Empty Directory]", badge

        elif name == "grep_search":
            query = args.get("query", "").strip()
            if not query:
                return "Error: Empty query.", "🔍 Search › [Empty]"
            search_root = Path(args.get("path") or ".").expanduser()
            case_ins = args.get("case_insensitive", True)

            # Fast path: Native ripgrep (rg) if present
            if shutil.which("rg"):
                rg_cmd = ["rg", "-n", "--max-count", "40"]
                if case_ins:
                    rg_cmd.append("-i")
                rg_cmd.extend(["-g", "!{.git,node_modules,__pycache__,.venv,.xdharness}*"])
                rg_cmd.extend([query, str(search_root)])
                try:
                    res = subprocess.run(rg_cmd, capture_output=True, text=True, timeout=15)
                    lines = [l.strip() for l in res.stdout.splitlines() if l.strip()][:40]
                    if lines:
                        return "\n".join(lines), f"🔍 Grep (rg) › [bold yellow]{query}[/bold yellow] [dim]({len(lines)} matches)[/dim]"
                except Exception:
                    pass

            flags = re.IGNORECASE if case_ins else 0
            matches = []
            regex = re.compile(query, flags)
            ign_patterns = get_ignored_patterns(search_root if search_root.is_dir() else search_root.parent)

            def scan_file(file_path: Path):
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        for idx, line in enumerate(f, 1):
                            if regex.search(line):
                                rel = file_path.relative_to(search_root) if file_path != search_root else file_path.name
                                matches.append(f"{rel}:{idx}: {line.strip()}")
                                if len(matches) >= 40:
                                    return
                except Exception:
                    pass

            if search_root.is_file():
                scan_file(search_root)
            elif search_root.is_dir():
                for root_dir, dirs, files in os.walk(search_root):
                    dirs[:] = [d for d in dirs if not is_path_ignored(Path(root_dir) / d, search_root, ign_patterns)]
                    for file in files:
                        fp = Path(root_dir) / file
                        if not is_path_ignored(fp, search_root, ign_patterns):
                            scan_file(fp)
                            if len(matches) >= 40:
                                break
                    if len(matches) >= 40:
                        break

            match_text = "\n".join(matches) if matches else "No matching patterns found."
            badge = f"🔍 Grep  › [bold yellow]{query}[/bold yellow] [dim]({len(matches)} matches)[/dim]"
            return match_text, badge

        elif name == "file_info":
            fp = Path(args.get("path", "")).expanduser()
            if not fp.exists():
                return f"Error: Path '{fp}' does not exist.", f"ℹ Info  › [red]{fp.name} (not found)[/red]"
            st = fp.stat()
            ftype = "directory" if fp.is_dir() else ("file" if fp.is_file() else "special")
            lines = 0
            if fp.is_file():
                try:
                    lines = sum(1 for _ in fp.open(encoding="utf-8", errors="ignore"))
                except Exception:
                    pass
            mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(st.st_mtime))
            info_str = (
                f"Path: {fp.resolve()}\n"
                f"Type: {ftype}\n"
                f"Size: {st.st_size} bytes ({st.st_size/1024:.2f} KB)\n"
                f"Lines: {lines}\n"
                f"Modified: {mtime}\n"
                f"Permissions: {oct(st.st_mode)[-3:]}"
            )
            badge = f"ℹ Info  › [bold magenta]{fp.name}[/bold magenta] [dim]({st.st_size} B, {lines} L)[/dim]"
            return info_str, badge

        elif name == "manage_todos":
            act = args.get("action")
            if act == "add":
                t = args.get("task", "")
                if t:
                    new_id = harness.add_todo(t)
                    return f"Added: #{new_id} {t}", f"📋 Task  › [green]+ #{new_id} {t}[/green]"
                return "Error: No task provided.", "📋 Task  › [red]Add Failed[/red]"
            elif act == "done":
                tid = args.get("todo_id", 0)
                if harness.toggle_todo(tid):
                    return f"Toggled task #{tid}", f"📋 Task  › [yellow]✓ #{tid} done[/yellow]"
                return f"Task #{tid} not found.", f"📋 Task  › [red]#{tid} missing[/red]"
            elif act == "list":
                if not harness.todos:
                    return "No tasks in list.", "📋 Task  › [dim]List (0 tasks)[/dim]"
                items = "\n".join([f"[{'✓' if t['done'] else ' '}] #{t['id']}: {t['title']}" for t in harness.todos])
                return items, f"📋 Task  › [cyan]List ({len(harness.todos)} tasks)[/cyan]"
            elif act == "clear":
                harness.clear_todos()
                return "Tasks cleared.", "📋 Task  › [red]Cleared all[/red]"

        elif name == "git_status":
            res = subprocess.run(["git", "status", "-s"], capture_output=True, text=True)
            if res.returncode != 0:
                return f"Git error: {res.stderr.strip()}", "🌿 Git   › [red]Not a git repo[/red]"
            txt = res.stdout.strip() if res.stdout.strip() else "Working tree clean. No changes."
            return txt, f"🌿 Git   › [bold green]Status[/bold green] [dim]({len(res.stdout.splitlines())} entries)[/dim]"

        elif name == "git_diff":
            target_file = args.get("path", "").strip()
            cmd = ["git", "diff"]
            if target_file:
                cmd.append(target_file)
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode != 0:
                return f"Git diff error: {res.stderr.strip()}", "🌿 Git   › [red]Diff Error[/red]"
            txt = res.stdout.strip() if res.stdout.strip() else "No uncommitted git differences."
            return txt, f"🌿 Git   › [bold cyan]Diff[/bold cyan] [dim]({len(txt.splitlines())} lines)[/dim]"

        elif name == "git_commit":
            msg = args.get("message", "").strip()
            if not msg:
                return "Error: Empty commit message.", "🌿 Git   › [red]Empty Message[/red]"
            files = args.get("files", ".").strip()
            add_res = subprocess.run(f"git add {files}", shell=True, capture_output=True, text=True)
            if add_res.returncode != 0:
                return f"Git add error: {add_res.stderr.strip()}", "🌿 Git   › [red]Add Failed[/red]"
            commit_res = subprocess.run(["git", "commit", "-m", msg], capture_output=True, text=True)
            if commit_res.returncode != 0:
                return f"Git commit error: {commit_res.stderr.strip()}", "🌿 Git   › [yellow]Commit Failed[/yellow]"
            return commit_res.stdout.strip(), f"🌿 Git   › [bold green]Committed[/bold green] [dim]('{msg[:20]}...')[/dim]"

        elif name == "fetch_url":
            target_url = args.get("url", "").strip()
            if not target_url.startswith(("http://", "https://")):
                return "Error: URL must start with http:// or https://", "🌐 Web   › [red]Invalid URL[/red]"
            req = urllib.request.Request(target_url, headers={"User-Agent": "xdh-agent/2.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                content_bytes = resp.read(64 * 1024) # Cap to 64KB
                text_preview = content_bytes.decode("utf-8", errors="replace")
                # Strip HTML tags simply if html
                clean_text = re.sub(r"<[^>]+>", " ", text_preview)
                clean_text = re.sub(r"\s+", " ", clean_text).strip()
                badge = f"🌐 Web   › [bold cyan]{urllib.parse.urlparse(target_url).netloc}[/bold cyan]"
                return clean_text[:4000], badge

        elif name == "search_web":
            query = args.get("query", "").strip()
            if not query:
                return "Error: Empty query.", "🔎 Web   › [Empty]"
            api_url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(query)}&format=json&no_html=1&skip_disambig=1"
            req = urllib.request.Request(api_url, headers={"User-Agent": "xdh-agent/2.0"})
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                abstract = data.get("AbstractText", "")
                heading = data.get("Heading", "")
                related = [t.get("Text", "") for t in data.get("RelatedTopics", []) if isinstance(t, dict) and t.get("Text")]
                summary = []
                if heading or abstract:
                    summary.append(f"**{heading}**: {abstract}")
                if related:
                    summary.append("\n**Related Info:**\n" + "\n".join(f"- {r}" for r in related[:5]))
                res_str = "\n".join(summary) if summary else f"No direct summary found for '{query}'."
                return res_str, f"🔎 Search › [bold cyan]{query[:25]}[/bold cyan]"

        elif name == "bg_command":
            cmd = args.get("command", "").strip()
            if not cmd:
                return "Error: Empty command.", "⚡ Task  › [Empty]"
            task_id = BG_TASKS.start_task(cmd)
            return f"Started background task [{task_id}]: `{cmd}`\nUse '/tasks list' or '/tasks logs {task_id}' to monitor.", f"⚡ Task  › [bold green]{task_id}[/bold green] (running)"

        elif name == "create_skill":
            sname = args.get("name", "").strip()
            sdesc = args.get("description", "").strip()
            sinst = args.get("instructions", "").strip()
            sparams = args.get("parameters", "").strip()
            if not sname or not sdesc or not sinst:
                return "Error: Missing required fields ('name', 'description', 'instructions').", "🎯 Skill › [red]Missing Info[/red]"
            ok, msg = SKILL_MGR.create_skill(sname, sdesc, sinst, sparams)
            return msg, f"🎯 Skill › [bold green]+{sname}[/bold green]"

        elif name == "call_skill":
            sname = args.get("name", "").strip()
            input_data = args.get("input_data", "").strip()
            skill_info = SKILL_MGR.get_skill(sname)
            if not skill_info:
                avail = ", ".join([s.get("name", "") for s in SKILL_MGR.list_skills()])
                return f"Error: Skill '{sname}' not found. Available skills: {avail}", f"🎯 Skill › [red]{sname} Not Found[/red]"
            instructions = skill_info.get("instructions", "")
            desc = skill_info.get("description", "")
            res_str = f"## Skill Invocation: {sname}\n**Description**: {desc}\n\n**Instructions**:\n{instructions}"
            if input_data:
                res_str += f"\n\n**User / Context Input**:\n{input_data}"
            return res_str, f"🎯 Skill › [bold cyan]{sname}[/bold cyan] (executed)"

        elif name == "create_agent":
            aname = args.get("name", "").strip()
            arole = args.get("role", "").strip()
            aprompt = args.get("system_prompt", "").strip()
            amodel = args.get("model", "").strip()
            aprov = args.get("provider", "").strip()
            atools = args.get("tools")
            if not aname or not arole or not aprompt:
                return "Error: Missing required fields ('name', 'role', 'system_prompt').", "🤖 Agent › [red]Missing Info[/red]"
            ok, msg = AGENT_MGR.create_agent(aname, arole, aprompt, amodel, aprov, atools)
            return msg, f"🤖 Agent › [bold green]+{aname}[/bold green]"

        elif name == "spawn_agents":
            subtasks = args.get("subtasks", [])
            if not subtasks or not isinstance(subtasks, list):
                return "Error: 'subtasks' must be a non-empty list of subagent tasks.", "🤖 Agents › [red]Empty[/red]"

            results = []
            threads = []
            results_lock = threading.Lock()

            active_app = getattr(harness, "app_instance", None)
            if active_app:
                active_app.append_output(f"🚀 [bold cyan]Multi-Agent Orchestration[/bold cyan]: Spawning {len(subtasks)} subagents in parallel...")

            def _run_subagent_task(agent_name: str, task_text: str, idx: int):
                agent_spec = AGENT_MGR.get_agent(agent_name) or {
                    "name": agent_name,
                    "role": f"Subagent {agent_name}",
                    "system_prompt": f"You are a specialized subagent tasked with: {task_text}",
                    "tools": ["read_file", "write_file", "list_dir", "bash"]
                }
                role = agent_spec.get("role", agent_name)

                # Custom subagent provider / model override if configured
                pdata = dict(harness.current_provider_data)
                if agent_spec.get("provider"):
                    cand = harness.config.get("providers", {}).get(agent_spec["provider"])
                    if cand: pdata = cand
                if agent_spec.get("model"):
                    pdata["default_model"] = agent_spec["model"]

                base_url = pdata.get("base_url", "").rstrip("/")
                api_key = pdata.get("api_key") or "none"
                model = pdata.get("default_model", "unknown")

                sys_prompt = f"Role: {role}\nInstructions: {agent_spec.get('system_prompt', '')}\nFocus on executing your assigned task efficiently."
                sub_msgs = [
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": task_text}
                ]

                # Filter allowed tools for this subagent
                allowed_tool_names = set(agent_spec.get("tools") or ["read_file", "write_file", "list_dir", "bash"])
                sub_tools = [t for t in get_all_tools_spec() if t.get("function", {}).get("name") in allowed_tool_names]

                agent_out = ""
                try:
                    # Run multi-turn autonomous tool loop for subagent
                    for sub_turn in range(5):
                        req_body = {
                            "model": model,
                            "messages": sub_msgs,
                            "tools": sub_tools if sub_tools else None
                        }
                        req_data = json.dumps(req_body).encode("utf-8")
                        headers = {"Content-Type": "application/json"}
                        if api_key and api_key != "none":
                            headers["Authorization"] = f"Bearer {api_key}"
                        req = urllib.request.Request(f"{base_url}/chat/completions", data=req_data, headers=headers, method="POST")

                        with urllib.request.urlopen(req, timeout=90) as resp:
                            res_json = json.loads(resp.read().decode("utf-8"))
                            choice = res_json.get("choices", [{}])[0]
                            msg = choice.get("message", {})
                            content = msg.get("content", "") or ""
                            tool_calls = msg.get("tool_calls", [])

                            if content:
                                agent_out += "\n" + content

                            sub_msgs.append(msg)

                            if not tool_calls:
                                break

                            for tc in tool_calls:
                                fn = tc.get("function", {})
                                fname = fn.get("name")
                                try:
                                    fargs = json.loads(fn.get("arguments", "{}"))
                                except Exception:
                                    fargs = {}
                                tout, _ = execute_tool(fname, fargs, harness)
                                sub_msgs.append({
                                    "role": "tool",
                                    "tool_call_id": tc.get("id", f"sub_call_{sub_turn}"),
                                    "name": fname,
                                    "content": str(tout)
                                })
                except Exception as sub_err:
                    agent_out += f"\n[Subagent execution error: {str(sub_err)}]"

                summary_clean = agent_out.strip() if agent_out.strip() else "[No textual response produced]"
                with results_lock:
                    results.append({
                        "index": idx,
                        "agent": agent_name,
                        "role": role,
                        "task": task_text,
                        "output": summary_clean
                    })
                if active_app:
                    active_app.append_output(f"✓ [bold green]Subagent Completed[/bold green] › [cyan]{agent_name}[/cyan] ({role})")

            for i, st in enumerate(subtasks):
                an = st.get("agent", "coder")
                tk = st.get("task", "")
                t = threading.Thread(target=_run_subagent_task, args=(an, tk, i), daemon=True)
                threads.append(t)
                t.start()

            for t in threads:
                t.join(timeout=180)

            # Sort results by original subtask index
            results.sort(key=lambda x: x["index"])
            out_blocks = []
            for r in results:
                out_blocks.append(f"### Subagent `{r['agent']}` ({r['role']})\n**Assigned Task**: {r['task']}\n\n**Findings & Result**:\n{r['output']}\n")

            full_report = "\n---\n".join(out_blocks)
            badge = f"🤖 Multi-Agent › [bold green]{len(results)}/{len(subtasks)} Subagents Completed[/bold green]"
            return full_report, badge

        elif name == "manage_plugins":
            action = args.get("action", "list").lower()
            pname = args.get("name", "").strip()
            source = args.get("source", "").strip()

            if action == "list":
                plugins = PLUGIN_MGR.list_plugins()
                if not plugins:
                    return "No plugins currently installed.", "🔌 Plugin › [Empty]"
                p_lines = [f"- **{p['name']}** ({p['type']}) [Loaded: {p['loaded']}] at `{p['path']}`" for p in plugins]
                return "Installed Plugins:\n" + "\n".join(p_lines), f"🔌 Plugin › [bold cyan]{len(plugins)} Plugins[/bold cyan]"

            elif action == "install":
                if not source:
                    return "Error: 'source' Git repository URL is required for installation.", "🔌 Plugin › [red]Missing URL[/red]"
                ok, msg = PLUGIN_MGR.install_plugin_from_git(source, pname or None)
                badge = f"🔌 Plugin › [{'bold green' if ok else 'red'}]{'Installed' if ok else 'Failed'}[/]"
                return msg, badge

            elif action == "add":
                if not pname or not source:
                    return "Error: Both 'name' and 'source' (Python code) are required to add a plugin.", "🔌 Plugin › [red]Missing Info[/red]"
                ok, msg = PLUGIN_MGR.add_plugin(pname, source)
                return msg, f"🔌 Plugin › [{'bold green' if ok else 'red'}]+{pname}[/]"

            elif action == "delete":
                if not pname:
                    return "Error: Plugin 'name' is required to delete.", "🔌 Plugin › [red]Missing Name[/red]"
                ok, msg = PLUGIN_MGR.delete_plugin(pname)
                return msg, f"🔌 Plugin › [{'bold green' if ok else 'red'}]-{pname}[/]"

            return f"Error: Unknown action '{action}'.", "🔌 Plugin › [red]Unknown Action[/red]"

        elif name == "ask_question":
            question = args.get("question", "").strip()
            options = args.get("options") or []
            if not question:
                return "Error: Empty question.", "❓ Question › [Empty]"

            active_app = getattr(harness, "app_instance", None)
            if not active_app:
                return "Error: TUI not attached, cannot prompt user.", "❓ Question › [Error]"

            # Set interactive question mode on the active TUI
            active_app.active_question = {
                "question": question,
                "options": options,
                "answer_event": threading.Event(),
                "answer_value": ""
            }

            # Prompt user in viewport
            q_lines = [f"❓ [bold yellow]Agent asks:[/bold yellow] {question}"]
            if options:
                q_lines.append("[dim]Options:[/dim]")
                for idx, opt in enumerate(options, 1):
                    q_lines.append(f"  [bold cyan]({idx})[/bold cyan] {opt}")
                q_lines.append("[italic dim]Type your response or option number below and press Enter.[/italic dim]")

            active_app.append_output("\n".join(q_lines))
            active_app.invalidate_ui()

            # Wait for user reply in composer
            active_app.active_question["answer_event"].wait(timeout=300)
            user_reply = active_app.active_question["answer_value"].strip()
            active_app.active_question = None
            active_app.invalidate_ui()

            if not user_reply:
                user_reply = "[No response received / Timed out after 5 minutes]"

            return f"User answered: {user_reply}", f"❓ Question › [bold green]Answered[/bold green]"

        elif name == "code_outline":
            target_file = Path(args.get("path", "")).expanduser()
            outline_txt = extract_code_outline(target_file)
            badge = f"📑 Outline › [bold cyan]{target_file.name}[/bold cyan]"
            return outline_txt, badge

        elif name == "manage_checkpoint":
            action = args.get("action", "list").lower()
            cp_name = args.get("name", "").strip()
            desc = args.get("description", "").strip()
            if action == "create":
                ok, msg = CHECKPOINT_MGR.create_checkpoint(cp_name, desc)
                return msg, f"💾 Checkpoint › [{'bold green' if ok else 'red'}]{'Created' if ok else 'Failed'}[/]"
            elif action == "restore":
                if not cp_name:
                    return "Error: Checkpoint name or ID required to restore.", "💾 Checkpoint › [red]Missing Name[/red]"
                ok, msg = CHECKPOINT_MGR.restore_checkpoint(cp_name)
                return msg, f"💾 Checkpoint › [{'bold green' if ok else 'red'}]{'Restored' if ok else 'Failed'}[/]"
            elif action == "list":
                cps = CHECKPOINT_MGR.list_checkpoints()
                if not cps:
                    return "No checkpoints found.", "💾 Checkpoint › [Empty]"
                cp_lines = [f"- **{c['name']}** (ID: `{c['id']}`, Files: {c.get('files_count', 0)}, Date: {c.get('created_at')}) {c.get('description', '')}" for c in cps]
                return "Saved Checkpoints:\n" + "\n".join(cp_lines), f"💾 Checkpoint › [bold cyan]{len(cps)} Checkpoints[/bold cyan]"
            return f"Error: Unknown action '{action}'.", "💾 Checkpoint › [red]Unknown Action[/red]"

        elif name == "manage_mcp":
            action = args.get("action", "list").lower()
            mname = args.get("name", "").strip()
            mcmd = args.get("command", "").strip()
            margs = args.get("args") or []
            if action == "list":
                servers = MCP_MGR.list_servers()
                if not servers:
                    return "No MCP servers configured.", "🔌 MCP › [Empty]"
                lines = [f"- **{s['name']}** (Status: {'running' if s['running'] else 'stopped'}, Tools: {s['tools_count']}) Command: `{s['command']}`" for s in servers]
                return "MCP Servers:\n" + "\n".join(lines), f"🔌 MCP › [bold cyan]{len(servers)} Servers[/bold cyan]"
            elif action == "add":
                if not mname or not mcmd:
                    return "Error: 'name' and 'command' are required.", "🔌 MCP › [red]Missing Info[/red]"
                ok, msg = MCP_MGR.add_server(mname, mcmd, margs)
                return msg, f"🔌 MCP › [{'bold green' if ok else 'red'}]+{mname}[/]"
            elif action == "remove":
                if not mname:
                    return "Error: 'name' is required to remove MCP server.", "🔌 MCP › [red]Missing Name[/red]"
                ok, msg = MCP_MGR.remove_server(mname)
                return msg, f"🔌 MCP › [{'bold green' if ok else 'red'}]-{mname}[/]"
            return f"Error: Unknown action '{action}'.", "🔌 MCP › [red]Unknown Action[/red]"

        # Check MCP tools (prefix mcp_)
        if name.startswith("mcp_") and name in MCP_MGR.discovered_tools:
            return MCP_MGR.call_tool(name, args)

        # Check dynamic plugin tools
        if name in PLUGIN_MGR.plugin_tools:
            _, handler = PLUGIN_MGR.plugin_tools[name]
            try:
                res = handler(args, harness)
                if isinstance(res, tuple):
                    return str(res[0]), str(res[1])
                return str(res), f"🔌 Plugin › {name}"
            except Exception as pe:
                return f"Plugin tool error: {str(pe)}", f"🔌 Plugin › [red]Error {name}[/red]"

        return f"Unknown tool: {name}", f"⚙ Tool  › {name}"
    except Exception as e:
        return f"Tool Error: {str(e)}", f"⚠️ Error › {name} ({str(e)})"

# ---------------------------------------------------------
# Slash Commands Autocompleter
# ---------------------------------------------------------
SLASH_COMMANDS = {
    "/settings": "Interactive configuration & preferences",
    "/todo": "Task board (/todo list, add, done, del)",
    "/provider": "Switch active provider (/provider <name>)",
    "/p": "Shorthand for /provider",
    "/model": "Switch model (/model <name>)",
    "/theme": "Switch palette (/theme <name>)",
    "/tools": "Toggle tools (/tools on|off)",
    "/thinking": "Toggle thoughts stream (/thinking on|off)",
    "/session": "Session statistics, list, or load (/session list|load)",
    "/history": "View recent prompt history",
    "/copy": "Copy last response or code block to system clipboard",
    "/undo": "Revert the most recent file edit from backups",
    "/pin": "Pin file contents to context (/pin <path>)",
    "/diff": "Review proposed edits/diffs across files",
    "/apply": "Apply proposed unified diffs to files",
    "/tasks": "Manage background tasks (/tasks list, logs <id>, kill <id>)",
    "/git": "Git status, diff, or commit (/git status|diff|commit <msg>)",
    "/search": "Web search query (/search <query>)",
    "/fetch": "Fetch webpage or API text (/fetch <url>)",
    "/image": "Attach image path to multimodal prompt (/image <path>)",
    "/index": "Build/search local keyword index over workspace (/index build|query)",
    "/scratch": "View or update scratchpad memo (/scratch view|set <text>|clear)",
    "/tree": "Display repository directory tree structure",
    "/export": "Export session transcript (/export md|json|html)",
    "/skill": "Manage & execute skills (/skill list, run <name>, create)",
    "/agent": "Manage & spawn agents (/agent list, spawn, create)",
    "/plugin": "Manage plugins (/plugin list, add, install <url>, del <name>)",
    "/checkpoint": "Rollback snapshots (/checkpoint create <name>|restore <id>|list)",
    "/mcp": "Model Context Protocol (/mcp list|add <name> <cmd>|remove <name>)",
    "/permission": "Set execution permission mode (/permission safe|auto|yolo)",
    "/outline": "Show AST / symbol code outline (/outline <path>)",
    "/schedule": "Schedule recurring agent task (/schedule <interval_sec> <task>)",
    "/drawer": "Toggle sidecar drawer panel (or F2 / Ctrl+B)",
    "/clear": "Clear conversation viewport (or Ctrl+L)",
    "/help": "Show available slash commands",
    "/exit": "Save session and exit (or Ctrl+Q)"
}

class XDHCompleter(Completer):
    def __init__(self, harness: XDHarness):
        self.harness = harness

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor

        # @file inline completion support
        if "@" in text:
            word = text.split()[-1] if text.split() else ""
            if word.startswith("@"):
                prefix = word[1:]
                cwd = Path(".")
                try:
                    for p in cwd.glob(f"{prefix}*"):
                        if p.name.startswith((".", "__")):
                            continue
                        rel_str = f"@{p}"
                        yield Completion(rel_str, start_position=-len(word), display=rel_str, display_meta="File")
                except Exception:
                    pass

        if text.startswith("/"):
            parts = text.split(maxsplit=1)
            cmd = parts[0]
            if len(parts) == 1 and not text.endswith(" "):
                for sc, desc in SLASH_COMMANDS.items():
                    if sc.startswith(cmd):
                        yield Completion(sc, start_position=-len(cmd), display=sc, display_meta=desc)
            elif cmd == "/settings":
                typed = parts[1] if len(parts) > 1 else ""
                for opt in ["theme", "tools", "thinking", "provider", "model", "confirm", "permission"]:
                    if opt.startswith(typed):
                        yield Completion(opt, start_position=-len(typed))
            elif cmd == "/permission":
                typed = parts[1] if len(parts) > 1 else ""
                for opt in ["safe", "auto", "yolo"]:
                    if opt.startswith(typed):
                        yield Completion(opt, start_position=-len(typed))
            elif cmd == "/checkpoint":
                typed = parts[1] if len(parts) > 1 else ""
                for opt in ["create", "restore", "list"]:
                    if opt.startswith(typed):
                        yield Completion(opt, start_position=-len(typed))
            elif cmd == "/mcp":
                typed = parts[1] if len(parts) > 1 else ""
                for opt in ["list", "add", "remove"]:
                    if opt.startswith(typed):
                        yield Completion(opt, start_position=-len(typed))
            elif cmd == "/todo":
                typed = parts[1] if len(parts) > 1 else ""
                for opt in ["list", "add", "done", "del", "clear"]:
                    if opt.startswith(typed):
                        yield Completion(opt, start_position=-len(typed))
            elif cmd in ["/provider", "/p"]:
                typed = parts[1] if len(parts) > 1 else ""
                for prov in self.harness.config.get("providers", {}).keys():
                    if prov.startswith(typed):
                        yield Completion(prov, start_position=-len(typed), display_meta="Provider")
            elif cmd == "/theme":
                typed = parts[1] if len(parts) > 1 else ""
                for th in THEMES.keys():
                    if th.startswith(typed):
                        yield Completion(th, start_position=-len(typed), display_meta="Theme")
            elif cmd in ["/tools", "/thinking"]:
                typed = parts[1] if len(parts) > 1 else ""
                for opt in ["on", "off"]:
                    if opt.startswith(typed):
                        yield Completion(opt, start_position=-len(typed))
            elif cmd == "/session":
                typed = parts[1] if len(parts) > 1 else ""
                for opt in ["stats", "list", "load"]:
                    if opt.startswith(typed):
                        yield Completion(opt, start_position=-len(typed))
            elif cmd == "/skill":
                typed = parts[1] if len(parts) > 1 else ""
                for opt in ["list", "run", "create"]:
                    if opt.startswith(typed):
                        yield Completion(opt, start_position=-len(typed))
            elif cmd == "/agent":
                typed = parts[1] if len(parts) > 1 else ""
                for opt in ["list", "spawn", "create"]:
                    if opt.startswith(typed):
                        yield Completion(opt, start_position=-len(typed))
            elif cmd == "/plugin":
                typed = parts[1] if len(parts) > 1 else ""
                for opt in ["list", "add", "install", "del"]:
                    if opt.startswith(typed):
                        yield Completion(opt, start_position=-len(typed))
            elif cmd == "/export":
                typed = parts[1] if len(parts) > 1 else ""
                for opt in ["md", "json", "html"]:
                    if opt.startswith(typed):
                        yield Completion(opt, start_position=-len(typed))
            elif cmd in ["/pin", "/outline"]:
                typed = parts[1] if len(parts) > 1 else ""
                cwd = Path(".")
                try:
                    for p in cwd.glob(f"{typed}*"):
                        if not p.name.startswith("."):
                            yield Completion(str(p), start_position=-len(typed), display_meta="File")
                except Exception:
                    pass
            elif cmd == "/tasks":
                typed = parts[1] if len(parts) > 1 else ""
                for opt in ["list", "logs", "kill"]:
                    if opt.startswith(typed):
                        yield Completion(opt, start_position=-len(typed))
            elif cmd == "/git":
                typed = parts[1] if len(parts) > 1 else ""
                for opt in ["status", "diff", "commit"]:
                    if opt.startswith(typed):
                        yield Completion(opt, start_position=-len(typed))
            elif cmd == "/scratch":
                typed = parts[1] if len(parts) > 1 else ""
                for opt in ["view", "set", "clear"]:
                    if opt.startswith(typed):
                        yield Completion(opt, start_position=-len(typed))
            elif cmd == "/index":
                typed = parts[1] if len(parts) > 1 else ""
                for opt in ["build", "query"]:
                    if opt.startswith(typed):
                        yield Completion(opt, start_position=-len(typed))

# ---------------------------------------------------------
# TUI Application (3-Segment Layout)
# ---------------------------------------------------------
class XDHApp:
    def __init__(self, harness: XDHarness):
        self.harness = harness
        self.harness.app_instance = self
        self.completer = XDHCompleter(harness)
        self.auto_suggester = DynamicContextAutoSuggest(harness)
        self.lock = threading.Lock()
        self.is_busy = False
        self.abort_requested = False
        self.active_question: Optional[Dict[str, Any]] = None
        self.interrupted_task_context: Optional[str] = None
        self.spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.spinner_index = 0
        self.buffer_text = ""
        self.scroll_offset = 0
        self.history_blocks: List[Dict[str, Any]] = []
        self.collapsed_state: bool = False
        self.staged_diffs: List[Dict[str, str]] = []
        self.drawer_open: bool = False
        self.active_schedules: List[Dict[str, Any]] = []

        # Segment 1: Fixed Top Banner Window
        self.top_banner_window = Window(
            content=FormattedTextControl(self.render_top_banner),
            dont_extend_height=True,
            wrap_lines=False
        )

        # Segment 2: Middle Scrollable Viewport
        def get_viewport_cursor(total_lines: int) -> Point:
            if total_lines <= 0:
                return Point(x=0, y=0)
            target_y = max(0, total_lines - 1 - self.scroll_offset)
            return Point(x=0, y=target_y)

        self.viewport_control = ScrollingANSIControl(
            lambda: self.buffer_text,
            get_cursor_func=get_viewport_cursor,
            mouse_scroll_func=self.smooth_scroll_by
        )
        self.viewport_window = Window(
            content=self.viewport_control,
            wrap_lines=True
        )

        # Sidecar Drawer Window (F2 / Ctrl+B)
        self.drawer_control = FormattedTextControl(self.render_drawer_panel)
        self.drawer_window = Window(
            content=self.drawer_control,
            width=Dimension(preferred=32, max=40),
            dont_extend_width=True
        )

        # Segment 3: Bottom Pinned Composer with Ghost-Writing (AppendAutoSuggestion)
        self.input_buffer = Buffer(
            history=self.auto_suggester.file_history,
            auto_suggest=self.auto_suggester,
            completer=self.completer,
            complete_while_typing=True,
            multiline=True
        )

        self.input_window = Window(
            content=BufferControl(
                buffer=self.input_buffer,
                input_processors=[AppendAutoSuggestion()],
                include_default_input_processors=True
            ),
            height=Dimension(min=1, max=5),
            dont_extend_height=True,
            wrap_lines=True
        )

        def get_prompt_tag():
            if self.active_question:
                return [("class:prompt-question", "❓ Question ❯ ")]
            if self.is_busy:
                return [("class:prompt-busy", "⚡ [busy] ❯ ")]
            return [("class:prompt", "xdh ❯ ")]

        prompt_tag_window = Window(
            content=FormattedTextControl(get_prompt_tag),
            dont_extend_width=True,
            dont_extend_height=True
        )

        composer_row = VSplit([
            prompt_tag_window,
            self.input_window
        ])

        header_window = Window(
            height=1,
            content=FormattedTextControl(self.render_header_bar),
            dont_extend_height=True,
            wrap_lines=False
        )

        footer_window = Window(
            height=1,
            content=FormattedTextControl(self.render_footer_bar),
            dont_extend_height=True,
            wrap_lines=False
        )

        # Keybindings
        self.kb = KeyBindings()

        @self.kb.add("escape")
        @self.kb.add("c-c")
        def _handle_interrupt_or_exit(event):
            if self.is_busy:
                self.abort_requested = True
                self.append_output("[yellow]⚡ Interrupt signal sent (ESC/Ctrl+C)... stopping ongoing task.[/yellow]")
            else:
                if event.key_sequence[0].key == "escape":
                    # Single ESC when idle does not exit
                    return
                self.harness.save_session()
                event.app.exit()

        @self.kb.add("c-q")
        def _exit(event):
            self.harness.save_session()
            event.app.exit()

        @self.kb.add("c-t")
        def _cycle_theme_key(event):
            self.cycle_theme()

        @self.kb.add("c-p")
        def _cycle_provider_key(event):
            self.cycle_provider()

        @self.kb.add("c-l")
        def _clear_viewport(event):
            with self.lock:
                self.history_blocks = []
                self.buffer_text = ""
                self.scroll_offset = 0
            self.invalidate_ui()

        @self.kb.add("c-j", filter=has_focus(self.input_buffer))
        def _insert_newline(event):
            self.input_buffer.insert_text("\n")

        @self.kb.add("c-o")
        def _toggle_collapse_blocks(event):
            self.collapsed_state = not self.collapsed_state
            self.rebuild_buffer_text()
            st = "COLLAPSED (summaries)" if self.collapsed_state else "EXPANDED (full)"
            self.append_output(f"⚡ Viewport blocks: [bold cyan]{st}[/bold cyan]")

        @self.kb.add("f2")
        @self.kb.add("c-b")
        def _toggle_drawer(event):
            self.drawer_open = not self.drawer_open
            st = "OPEN" if self.drawer_open else "CLOSED"
            self.append_output(f"📊 Drawer sidecar: [bold cyan]{st}[/bold cyan]")
            self.invalidate_ui()

        # Tab: Apply completion if menu active, accept ghost suggestion, or start completion
        @self.kb.add("tab")
        def _handle_tab(event):
            buf = self.input_buffer
            if buf.complete_state and buf.complete_state.current_completion:
                buf.apply_completion(buf.complete_state.current_completion)
            elif buf.suggestion and buf.suggestion.text:
                buf.insert_text(buf.suggestion.text)
            elif buf.text.strip().startswith("/"):
                buf.start_completion(select_first=True)
            elif buf.suggestion and buf.suggestion.text:
                buf.insert_text(buf.suggestion.text)
            else:
                buf.start_completion(select_first=True)

        # Right arrow: Accept completion or ghost suggestion when cursor is at end of text/line
        @self.kb.add("right")
        def _handle_right(event):
            buf = self.input_buffer
            if buf.complete_state and buf.complete_state.current_completion:
                buf.apply_completion(buf.complete_state.current_completion)
            elif (buf.cursor_position == len(buf.text) or buf.document.is_cursor_at_the_end_of_line) and buf.suggestion and buf.suggestion.text:
                buf.insert_text(buf.suggestion.text)
            else:
                buf.cursor_right()

        # Touch/Arrow swipe navigation with smooth step animation
        @self.kb.add("up", filter=has_focus(self.input_buffer))
        def _scroll_up(event):
            buf = self.input_buffer
            if buf.complete_state:
                buf.complete_previous()
            elif buf.document.cursor_position_row == 0:
                self.smooth_scroll_by(3)
            else:
                buf.cursor_up()

        @self.kb.add("down", filter=has_focus(self.input_buffer))
        def _scroll_down(event):
            buf = self.input_buffer
            if buf.complete_state:
                buf.complete_next()
            elif buf.document.cursor_position_row == buf.document.line_count - 1:
                self.smooth_scroll_by(-3)
            else:
                buf.cursor_down()

        @self.kb.add("pageup")
        def _pageup(event):
            self.smooth_scroll_by(8)

        @self.kb.add("pagedown")
        def _pagedown(event):
            self.smooth_scroll_by(-8)

        @self.kb.add("enter", filter=has_focus(self.input_buffer))
        def _handle_enter(event):
            buf = self.input_buffer
            if buf.complete_state and buf.complete_state.current_completion:
                buf.apply_completion(buf.complete_state.current_completion)
                return

            text = self.input_buffer.text.strip()
            if not text:
                return

            # Case 1: Answering an interactive ask_question prompt
            if self.active_question:
                self.input_buffer.text = ""
                q_dict = self.active_question
                # If numeric choice, resolve option label
                chosen_text = text
                if text.isdigit():
                    opt_idx = int(text) - 1
                    opts = q_dict.get("options", [])
                    if 0 <= opt_idx < len(opts):
                        chosen_text = opts[opt_idx]

                self.append_history_block({
                    "type": "user",
                    "text": f"❯ {chosen_text}",
                    "timestamp": time.strftime("%H:%M:%S")
                })
                q_dict["answer_value"] = chosen_text
                q_dict["answer_event"].set()
                self.invalidate_ui()
                return

            # Case 2: Slash command (executed immediately)
            if text.startswith("/"):
                self.input_buffer.text = ""
                self.execute_slash_command(text)
                return

            # Case 3: User sends input while agent is busy running a task
            if self.is_busy:
                self.input_buffer.text = ""
                self.abort_requested = True
                self.append_history_block({
                    "type": "user",
                    "text": text,
                    "timestamp": time.strftime("%H:%M:%S")
                })
                self.append_output("⚡ [bold yellow]Interrupted ongoing task for user update.[/bold yellow] Adapting context with your new instructions...")

                def _interrupt_and_pivot():
                    # Wait briefly for current step to halt
                    time.sleep(0.3)
                    updated_instruction = (
                        f"[USER INTERRUPT / REVISED INSTRUCTION]: The user intervened while the previous task was running.\n"
                        f"New update from user: \"{text}\"\n"
                        f"Please adapt immediately: stop previous conflicting actions, adopt these instructions, and continue."
                    )
                    self.run_agent_thread(updated_instruction)

                threading.Thread(target=_interrupt_and_pivot, daemon=True).start()
                return

            self.input_buffer.text = ""

            if text.startswith("!"):
                shell_cmd = text[1:].strip()
                self.append_history_block({"type": "raw", "text": f"[bold yellow]! {shell_cmd}[/bold yellow]"})
                def _run_quick_shell():
                    try:
                        res = subprocess.run(shell_cmd, shell=True, capture_output=True, text=True, timeout=30)
                        out = (res.stdout + ("\n" + res.stderr if res.stderr else "")).strip()
                        badge_panel = Panel(Text(out if out else "[Done with 0]"), title=f"💻 Local Exec (exit {res.returncode})", box=box.ROUNDED, border_style=self.harness.theme["dim"])
                        self.append_history_block({"type": "raw", "text": render_rich_to_string(badge_panel, max_cols=self.get_term_size()[0])})
                    except Exception as e:
                        self.append_output(f"[red]Execution failed: {str(e)}[/red]")
                threading.Thread(target=_run_quick_shell, daemon=True).start()
                return

            now_str = time.strftime("%H:%M:%S")
            self.append_history_block({
                "type": "user",
                "text": text,
                "timestamp": now_str
            })

            # Check for @file mentions and attach file context
            expanded_context = ""
            for match in re.finditer(r"@([\w\-./\\]+)", text):
                raw_path = match.group(1)
                fp = Path(raw_path).expanduser()
                if fp.is_file():
                    try:
                        content = fp.read_text(encoding="utf-8", errors="replace")
                        expanded_context += f"\n[Referenced File @{raw_path}]:\n```{fp.suffix.lstrip('.') or 'text'}\n{content}\n```\n"
                    except Exception:
                        pass

            prompt_payload = text
            if expanded_context:
                prompt_payload = f"{text}\n\n{expanded_context.strip()}"

            threading.Thread(target=self.run_agent_thread, args=(prompt_payload,), daemon=True).start()

        # Dynamic viewport row: shows drawer sidecar when toggled (F2 / Ctrl+B)
        def get_viewport_row():
            if self.drawer_open:
                return VSplit([self.viewport_window, self.drawer_window])
            return self.viewport_window

        # Combine into Root Container with Floats
        root_container = FloatContainer(
            content=HSplit([
                self.top_banner_window,
                VSplit([
                    self.viewport_window,
                    Window(
                        content=self.drawer_control,
                        width=lambda: Dimension(preferred=32, max=40) if self.drawer_open else Dimension(preferred=0, max=0),
                        dont_extend_width=True
                    )
                ]),
                header_window,
                composer_row,
                footer_window
            ]),
            floats=[
                Float(
                    xcursor=True,
                    ycursor=True,
                    content=CompletionsMenu(max_height=8, scroll_offset=1)
                )
            ]
        )

        self.layout = Layout(root_container, focused_element=self.input_window)

        self.app = Application(
            layout=self.layout,
            key_bindings=self.kb,
            style=self.build_style(),
            full_screen=True,
            mouse_support=True
        )

    def cycle_theme(self):
        """Quick cycle through available themes (Ctrl+T)."""
        theme_names = list(THEMES.keys())
        current = self.harness.config.get("current_theme", "tokyo_night")
        try:
            next_idx = (theme_names.index(current) + 1) % len(theme_names)
        except ValueError:
            next_idx = 0
        next_theme = theme_names[next_idx]
        self.harness.config["current_theme"] = next_theme
        self.harness.save_config()
        self.app.style = self.build_style()
        self.append_history_block({"type": "raw", "text": f"🎨 Theme: [bold]{next_theme}[/bold]"})
        self.rebuild_buffer_text()

    def cycle_provider(self):
        """Quick cycle through available providers (Ctrl+P)."""
        prov_names = list(self.harness.config.get("providers", {}).keys())
        if not prov_names:
            return
        current = self.harness.config.get("current_provider", "ollama")
        try:
            next_idx = (prov_names.index(current) + 1) % len(prov_names)
        except ValueError:
            next_idx = 0
        next_prov = prov_names[next_idx]
        self.harness.config["current_provider"] = next_prov
        self.harness.save_config()
        pdata = self.harness.current_provider_data
        self.append_output(f"🔌 Provider: [bold]{next_prov}[/bold] » [cyan]{pdata.get('default_model', '')}[/cyan]")
        self.invalidate_ui()

    def get_term_size(self) -> Tuple[int, int]:
        try:
            sz = self.app.output.get_size()
            return max(30, sz.columns), max(10, sz.rows)
        except Exception:
            s = shutil.get_terminal_size((80, 24))
            return max(30, s.columns), max(10, s.rows)

    def build_style(self) -> PTStyle:
        theme = self.harness.theme
        return PTStyle.from_dict({
            "frame": f"{theme['primary']}",
            "badge": f"bold {theme['primary']}",
            "stat": f"{theme['warning']}",
            "accent": f"bold {theme['accent']}",
            "dim": f"{theme['dim']}",
            "prompt": f"bold {theme['accent']}",
            "prompt-question": f"bold {theme['warning']}",
            "prompt-busy": f"bold {theme['secondary']}",
            "completion-menu": f"bg:{theme['bg_bar']} fg:{theme['fg_bar']}",
            "completion-menu.completion": f"bg:{theme['bg_bar']} fg:{theme['fg_bar']}",
            "completion-menu.completion.current": f"bg:{theme['primary']} fg:#000000 bold",
            "completion-menu.meta": f"bg:{theme['bg_bar']} fg:{theme['dim']}",
            "scrollbar.background": f"{theme['bg_bar']}",
            "scrollbar.button": f"{theme['dim']}",
            "auto-suggestion": f"{theme['dim']}",
        })

    def render_drawer_panel(self):
        """Renders live sidecar status panel (F2 / Ctrl+B toggle)."""
        if not self.drawer_open:
            return []
        cols, rows = self.get_term_size()
        theme = self.harness.theme
        width = min(36, max(26, cols // 3))

        lines = []
        lines.append(f"[bold {theme['primary']}]📊 SIDECAR DRAWER[/bold {theme['primary']}]")
        lines.append("[dim]─────────────────────────[/dim]")

        # Section 1: Swarm & Agents
        agents = AGENT_MGR.list_agents()
        lines.append(f"[bold {theme['warning']}]🤖 Agent Swarm ({len(agents)})[/bold {theme['warning']}]")
        for a in agents[:4]:
            lines.append(f" • [cyan]{a['name']}[/cyan]: [dim]{a.get('role', '')[:16]}[/dim]")

        # Section 2: MCP Servers
        mcp_srv = MCP_MGR.list_servers()
        lines.append(f"\n[bold {theme['accent']}]🔌 MCP Servers ({len(mcp_srv)})[/bold {theme['accent']}]")
        if not mcp_srv:
            lines.append(" [dim italic]None configured[/dim italic]")
        else:
            for s in mcp_srv[:3]:
                st = "[green]●[/green]" if s['running'] else "[dim]○[/dim]"
                lines.append(f" {st} [bold]{s['name']}[/bold] ({s['tools_count']} tools)")

        # Section 3: Checkpoints
        cps = CHECKPOINT_MGR.list_checkpoints()
        lines.append(f"\n[bold {theme['secondary']}]💾 Snapshots ({len(cps)})[/bold {theme['secondary']}]")
        if not cps:
            lines.append(" [dim italic]No checkpoints[/dim italic]")
        else:
            for c in cps[:2]:
                lines.append(f" • [bold white]{c['name']}[/bold white] [dim]({c.get('files_count',0)}f)[/dim]")

        # Section 4: Tasks / Todos
        todos = self.harness.todos
        lines.append(f"\n[bold {theme['warning']}]📋 Tasks ({len(todos)})[/bold {theme['warning']}]")
        if not todos:
            lines.append(" [dim italic]Board is clear[/dim italic]")
        else:
            for t in todos[:3]:
                mark = "[green]✓[/green]" if t['done'] else "[yellow]•[/yellow]"
                lines.append(f" {mark} #{t['id']} {t['title'][:18]}")

        # Section 5: Schedules
        if self.active_schedules:
            lines.append(f"\n[bold cyan]⏰ Schedules ({len(self.active_schedules)})[/bold cyan]")
            for sc in self.active_schedules[:2]:
                lines.append(f" • every {sc['interval']}s: {sc['task'][:14]}")

        lines.append("\n[dim]Press [bold]F2[/bold] or [bold]Ctrl+B[/bold] to hide[/dim]")

        panel = Panel(Text.from_markup("\n".join(lines)), title="Drawer", box=box.ROUNDED, border_style=theme["rich_border"], padding=(0, 1))
        return ANSI(render_rich_to_string(panel, max_cols=width))

    def render_top_banner(self):
        """Top Segment: Pinned, non-scrolling responsive Hero Header."""
        cols, _ = self.get_term_size()
        theme = self.harness.theme
        pdata = self.harness.current_provider_data
        prov = self.harness.config.get("current_provider", "none")
        model = pdata.get("default_model", "none")
        theme_name = self.harness.config.get("current_theme", "tokyo_night").capitalize()

        if cols < 70:
            banner = (
                f"[bold {theme['primary']}]⚡ XDHARNESS[/bold {theme['primary']}] [dim]v{__version__}[/dim] │ "
                f"[bold]{prov}[/bold]»[bold {theme['accent']}]{model}[/bold {theme['accent']}] │ "
                f"[dim]{theme_name}[/dim]\n"
                f"[dim]Commands: /help, /settings, /todo, /clear, /exit[/dim]"
            )
            panel = Panel(Text.from_markup(banner), box=box.ROUNDED, border_style=theme["rich_border"], padding=(0, 1))
            return ANSI(render_rich_to_string(panel, max_cols=cols))

        brand_icon = """  ██╗  ██╗██████╗ ██╗  ██╗
  ╚██╗██╔╝██╔══██╗██║  ██║
   ╚███╔╝ ██║  ██║███████║
   ██╔██╗ ██║  ██║██╔══██║
  ██╔╝ ██╗██████╔╝██║  ██║"""

        grid = Table.grid(expand=True)
        grid.add_column(ratio=1)
        grid.add_column(ratio=2)

        col1 = Text(brand_icon, style=f"bold {theme['primary']}")
        col2 = Text.from_markup(
            f"\n[bold {theme['secondary']}]xdharness {__version__}[/bold {theme['secondary']}] [dim](Autonomous Terminal Harness)[/dim]\n"
            f" • [dim]Provider:[/dim] [bold]{prov}[/bold] » [bold {theme['accent']}]{model}[/bold {theme['accent']}]\n"
            f" • [dim]Palette:[/dim]  [bold]{theme_name}[/bold]\n"
            f" • [dim]Commands:[/dim] [bold {theme['warning']}]/help[/bold {theme['warning']}], [bold {theme['warning']}]/settings[/bold {theme['warning']}], [bold {theme['warning']}]/todo[/bold {theme['warning']}]"
        )
        grid.add_row(col1, col2)
        panel = Panel(grid, box=box.ROUNDED, border_style=theme["rich_border"], padding=(0, 1))
        return ANSI(render_rich_to_string(panel, max_cols=cols))

    def render_header_bar(self):
        cols, _ = self.get_term_size()
        pdata = self.harness.current_provider_data
        ctx_max = pdata.get("context_window", 128000) or 128000
        current_tokens = self.harness.count_context_tokens()
        pct = min(100, int((current_tokens / ctx_max) * 100))
        ram = get_memory_usage_mb()

        prov = self.harness.config.get("current_provider", "none")
        model = pdata.get("default_model", "none")

        ctx_str = format_k_val(ctx_max)
        tok_str = format_k_val(self.harness.total_tokens_consumed)
        tools_st = "ON" if self.harness.config.get("active_tools") else "OFF"

        # Status badge with spinner when busy (time-based for smooth non-laggy rotation)
        if self.is_busy:
            spin_idx = int(time.time() * 8) % len(self.spinner_chars)
            spin_sym = self.spinner_chars[spin_idx]
            status_text = f"{spin_sym} {self.harness.status_label}"
            status_class = "stat"
        else:
            status_text = f"● {self.harness.status_label}"
            status_class = "accent"

        if cols < 60:
            short_model = model.split("/")[-1] if "/" in model else model
            if len(short_model) > 8:
                short_model = short_model[:7] + "…"
            badge = f"{short_model}"
            stats = f"{pct}%│{tok_str}│{ram}MB│"
            info_len = len(f"╭─ {badge} ─[{stats}{status_text}]─╮")
            fill = "─" * max(0, cols - info_len)
            return [
                ("class:frame", "╭─ "),
                ("class:badge", badge),
                ("class:frame", " ─["),
                ("class:stat", stats),
                (f"class:{status_class}", status_text),
                ("class:frame", f"]{fill}─╮"),
            ]
        elif cols < 85:
            short_model = model.split("/")[-1] if "/" in model else model
            if len(short_model) > 10:
                short_model = short_model[:9] + "…"
            info_len = len(f"╭─ {prov}:{short_model} ─[Ctx:{pct}%│Tok:{tok_str}│{ram}MB│{tools_st}│{status_text}]─╮")
            fill = "─" * max(0, cols - info_len)
            return [
                ("class:frame", "╭─ "),
                ("class:badge", f"{prov}:{short_model}"),
                ("class:frame", " ─["),
                ("class:stat", f"Ctx:{pct}%"),
                ("class:frame", "│"),
                ("class:stat", f"Tok:{tok_str}"),
                ("class:frame", "│"),
                ("class:stat", f"{ram}MB"),
                ("class:frame", "│"),
                ("class:stat", f"{tools_st}"),
                ("class:frame", "│"),
                (f"class:{status_class}", status_text),
                ("class:frame", f"]{fill}─╮"),
            ]
        else:
            info_len = len(f"╭─ {prov} » {model} ─[Ctx:{pct}% ({current_tokens}/{ctx_str})│Tokens:{tok_str}│RAM:{ram}MB│Tools: {tools_st}│{status_text}]─╮")
            fill = "─" * max(0, cols - info_len)
            return [
                ("class:frame", "╭─ "),
                ("class:badge", f"{prov} » {model}"),
                ("class:frame", " ─["),
                ("class:stat", f"Ctx:{pct}% ({current_tokens}/{ctx_str})"),
                ("class:frame", "│"),
                ("class:stat", f"Tokens:{tok_str}"),
                ("class:frame", "│"),
                ("class:stat", f"RAM:{ram}MB"),
                ("class:frame", "│"),
                ("class:stat", f"Tools: {tools_st}"),
                ("class:frame", "│"),
                (f"class:{status_class}", status_text),
                ("class:frame", f"]{fill}─╮"),
            ]

    def render_footer_bar(self):
        cols, _ = self.get_term_size()
        drawer_st = "Drawer"
        if cols < 65:
            hints = " [↵] Send │ [F2] Drawer │ [/] Help "
        elif cols < 95:
            hints = " [↵] Send │ [F2] Drawer │ [^T] Theme │ [^P] Prov │ [^L] Clear │ [ESC] Halt "
        else:
            hints = " [↵] Send │ [Ctrl+J] Line │ [F2] Drawer │ [^T] Theme │ [^P] Prov │ [^L] Clear │ [ESC] Halt │ [/] Commands "

        fill = "─" * max(0, cols - len(hints) - 3)
        return [
            ("class:frame", f"╰{fill}"),
            ("class:dim", hints),
            ("class:frame", "─╯"),
        ]

    def invalidate_ui(self, force: bool = False):
        """Thread-safe, 30fps-debounced UI invalidation to eliminate frame lag and terminal repaint storms."""
        now = time.monotonic()
        if not force and (now - getattr(self, "_last_invalidate", 0.0)) < 0.033:
            return
        self._last_invalidate = now
        try:
            loop = getattr(self.app, "loop", None)
            if loop and loop.is_running():
                self.app.call_from_executor(self.app.invalidate)
            else:
                self.app.invalidate()
        except Exception:
            try:
                self.app.invalidate()
            except Exception:
                pass

    def smooth_scroll_by(self, delta: int, steps: int = 4, delay: float = 0.015):
        """Animates viewport scroll offset smoothly in small increments."""
        def _scroll_worker():
            step_val = delta / max(1, steps)
            for s in range(steps):
                with self.lock:
                    new_val = self.scroll_offset + step_val
                    self.scroll_offset = max(0, int(round(new_val)))
                self.invalidate_ui()
                time.sleep(delay)
        threading.Thread(target=_scroll_worker, daemon=True).start()

    def render_block(self, item: Dict[str, Any], cols: int) -> str:
        """Renders a structured history item using the harness's current theme."""
        theme = self.harness.theme
        btype = item.get("type", "raw")
        ts = item.get("timestamp", "")
        time_str = f" {ts}" if ts else ""

        if btype == "user":
            user_text = item.get("text", "")
            panel_text = Text.from_markup(f"[bold {theme['primary']}]User{time_str} ❯[/bold {theme['primary']}] {user_text}")
            return render_rich_to_string(panel_text, max_cols=cols)

        elif btype == "assistant":
            content = item.get("content", "")
            model = item.get("model", "assistant")
            title = f"xdh{time_str} ({model})"
            panel = Panel(
                Markdown(content) if content else Text(""),
                title=title,
                box=box.ROUNDED,
                border_style=theme["primary"],
                padding=(0, 1)
            )
            return render_rich_to_string(panel, max_cols=cols)

        elif btype == "thought":
            thought_text = item.get("content", "")
            if self.collapsed_state:
                summary_lines = len(thought_text.splitlines())
                panel = Panel(
                    Text(f"Collapsed thought trace ({summary_lines} lines, {len(thought_text)} chars). Press Ctrl+O to expand.", style=f"italic {theme['warning']}"),
                    title=f"⚡ Thinking (folded){time_str}",
                    box=box.ROUNDED,
                    border_style=theme["warning"],
                    padding=(0, 1)
                )
            else:
                panel = Panel(
                    Text(thought_text, style=f"dim {theme['warning']}"),
                    title=f"⚡ Thinking{time_str}",
                    box=box.ROUNDED,
                    border_style=theme["warning"],
                    padding=(0, 1)
                )
            return render_rich_to_string(panel, max_cols=cols)

        elif btype == "tool":
            badge_text = item.get("badge", "")
            badge_panel = Panel(
                Text.from_markup(badge_text),
                box=box.ROUNDED,
                border_style=theme["accent"],
                padding=(0, 1)
            )
            output_content = item.get("output", "")
            name = item.get("name", "")
            blocks = [render_rich_to_string(badge_panel, max_cols=cols)]

            if self.collapsed_state and output_content:
                folded_msg = f"[dim italic]Output collapsed ({len(output_content)} chars). Press Ctrl+O to expand.[/dim italic]"
                blocks.append(render_rich_to_string(Text.from_markup(folded_msg), max_cols=cols))
            elif output_content and output_content not in ["[Exited with 0]", "None"]:
                if name == "replace_file_content":
                    try:
                        syn = Syntax(output_content[:4000], "diff", theme="monokai", line_numbers=True, word_wrap=True)
                        out_panel = Panel(syn, title="📝 Unified Diff Hunk", box=box.ROUNDED, border_style=theme["accent"], padding=(0, 1))
                        blocks.append(render_rich_to_string(out_panel, max_cols=cols))
                    except Exception:
                        out_panel = Panel(Text(output_content[:4000]), title="📝 Diff", box=box.ROUNDED, border_style=theme["accent"], padding=(0, 1))
                        blocks.append(render_rich_to_string(out_panel, max_cols=cols))
                elif name in ["read_file", "write_file"]:
                    lang = "python"
                    if "path" in item.get("args", {}):
                        p = str(item["args"]["path"])
                        if p.endswith(".sh"): lang = "bash"
                        elif p.endswith(".json"): lang = "json"
                        elif p.endswith((".js", ".ts")): lang = "javascript"
                    try:
                        syn = Syntax(output_content[:4000], lang, theme="monokai", line_numbers=True, word_wrap=True)
                        out_panel = Panel(syn, title=f"⚡ Output: {name}", box=box.ROUNDED, border_style=theme["dim"], padding=(0, 1))
                        blocks.append(render_rich_to_string(out_panel, max_cols=cols))
                    except Exception:
                        out_panel = Panel(Text(output_content[:4000], style=f"dim {theme['fg_bar']}"), title=f"⚡ Output: {name}", box=box.ROUNDED, border_style=theme["dim"], padding=(0, 1))
                        blocks.append(render_rich_to_string(out_panel, max_cols=cols))
                elif name in ["list_dir", "grep_search", "file_info", "find_by_name"]:
                    out_panel = Panel(Text(output_content[:4000], style=f"dim {theme['fg_bar']}"), title=f"⚡ Output: {name}", box=box.ROUNDED, border_style=theme["dim"], padding=(0, 1))
                    blocks.append(render_rich_to_string(out_panel, max_cols=cols))
                elif name == "bash":
                    out_panel = Panel(Text(output_content[:3000], style=f"dim {theme['fg_bar']}"), title="💻 Shell Output", box=box.ROUNDED, border_style=theme["dim"], padding=(0, 1))
                    blocks.append(render_rich_to_string(out_panel, max_cols=cols))
            return "\n".join(blocks)

        elif btype == "elapsed":
            elapsed_sec = item.get("seconds", 0)
            elapsed_badge = Text(f"⏱ {elapsed_sec}s", style=f"dim {theme['dim']}")
            return render_rich_to_string(elapsed_badge, max_cols=cols)

        else:
            raw_t = item.get("text", "")
            if "[" in raw_t and "]" in raw_t and not raw_t.startswith("\x1b"):
                try:
                    return render_rich_to_string(Text.from_markup(raw_t), max_cols=cols)
                except Exception:
                    return raw_t
            return raw_t

    def rebuild_buffer_text(self):
        """Re-renders all conversation history items using the current theme."""
        cols, _ = self.get_term_size()
        rendered_pieces = []
        for item in self.history_blocks:
            rendered = self.render_block(item, cols)
            if rendered:
                rendered_pieces.append(rendered)
        with self.lock:
            self.buffer_text = "\n".join(rendered_pieces)
            self.scroll_offset = 0
        self.invalidate_ui()

    def append_history_block(self, item: Dict[str, Any]):
        """Adds a structured history item, renders it, and updates buffer_text."""
        cols, _ = self.get_term_size()
        rendered = self.render_block(item, cols)
        with self.lock:
            self.history_blocks.append(item)
            if self.buffer_text:
                self.buffer_text += "\n" + rendered
            else:
                self.buffer_text = rendered
            self.scroll_offset = 0
        self.invalidate_ui()

    def append_output(self, text: str):
        """Append a system or notification message to the conversation log."""
        self.append_history_block({"type": "raw", "text": text})

    def execute_slash_command(self, cmd_line: str):
        try:
            parts = shlex.split(cmd_line)
        except ValueError:
            self.append_output("[red]Invalid command syntax. Check quotes.[/red]")
            return
        if not parts:
            return
        root = parts[0].lower()
        theme = self.harness.theme
        cols, _ = self.get_term_size()

        if root in ["/exit", "/quit"]:
            self.harness.save_session()
            self.app.exit()

        elif root == "/settings":
            if len(parts) >= 3:
                sub = parts[1].lower()
                val = parts[2]
                if sub == "theme" and val.lower() in THEMES:
                    self.harness.config["current_theme"] = val.lower()
                    self.harness.save_config()
                    self.app.style = self.build_style()
                    self.append_history_block({"type": "raw", "text": f"✓ Switched theme to: {val.lower()}"})
                    self.rebuild_buffer_text()
                elif sub == "tools" and val.lower() in ["on", "off", "toggle"]:
                    new_val = not self.harness.config.get("active_tools") if val.lower() == "toggle" else (val.lower() == "on")
                    self.harness.config["active_tools"] = new_val
                    self.harness.save_config()
                    self.append_output(f"✓ Tools toggled: {'ON' if new_val else 'OFF'}")
                elif sub == "thinking" and val.lower() in ["on", "off", "toggle"]:
                    new_val = not self.harness.config.get("show_thinking") if val.lower() == "toggle" else (val.lower() == "on")
                    self.harness.config["show_thinking"] = new_val
                    self.harness.save_config()
                    self.append_output(f"✓ Thinking stream: {'ON' if new_val else 'OFF'}")
                elif sub == "confirm" and val.lower() in ["on", "off", "toggle"]:
                    new_val = not self.harness.config.get("confirm_danger_commands", True) if val.lower() == "toggle" else (val.lower() == "on")
                    self.harness.config["confirm_danger_commands"] = new_val
                    self.harness.save_config()
                    self.append_output(f"✓ Command safety confirmation: {'ON' if new_val else 'OFF'}")
                elif sub == "provider" and val in self.harness.config.get("providers", {}):
                    self.harness.config["current_provider"] = val
                    self.harness.save_config()
                    self.append_output(f"✓ Provider switched to: {val}")
                elif sub == "model":
                    prov = self.harness.config.get("current_provider")
                    if prov and prov in self.harness.config.get("providers", {}):
                        self.harness.config["providers"][prov]["default_model"] = val
                        self.harness.save_config()
                        self.append_output(f"✓ Model for {prov} updated to: {val}")
                    else:
                        self.append_output(f"[red]No active provider. Use /provider <name> first.[/red]")
                else:
                    self.append_output("[yellow]Usage: /settings <theme|tools|thinking|confirm|provider|model> <value>[/yellow]")
            else:
                pdata = self.harness.current_provider_data
                curr_prov = self.harness.config.get("current_provider")
                tools_st = "ON" if self.harness.config.get("active_tools") else "OFF"
                think_st = "ON" if self.harness.config.get("show_thinking") else "OFF"
                confirm_st = "ON" if self.harness.config.get("confirm_danger_commands", True) else "OFF"
                curr_palette = self.harness.config.get("current_theme", "tokyo_night")

                table = Table(title="⚡ Settings & Quick Toggles", box=box.ROUNDED, border_style=theme["rich_border"])
                table.add_column("Property", style=f"bold {theme['warning']}")
                table.add_column("Value", style="bold white")
                table.add_column("Quick Action", style=f"dim {theme['accent']}")

                table.add_row("Provider", curr_prov, "/settings provider <name>")
                table.add_row("Model", pdata.get("default_model", ""), "/settings model <name>")
                table.add_row("Palette", curr_palette.upper(), "/settings theme <name>")
                table.add_row("Tools", tools_st, "/settings tools toggle")
                table.add_row("Thoughts", think_st, "/settings thinking toggle")
                table.add_row("Safety Confirm", confirm_st, "/settings confirm toggle")
                table.add_row("Compaction", f"{int(self.harness.config.get('compaction_threshold', 0.9)*100)}%", "Auto (at limit)")
                self.append_output(render_rich_to_string(table, max_cols=cols))

        elif root == "/help":
            table = Table(title="xdh Commands", box=box.ROUNDED, border_style=theme["rich_border"])
            table.add_column("Command", style=f"bold {theme['warning']}")
            table.add_column("Description")
            for sc, d in SLASH_COMMANDS.items():
                table.add_row(sc, d)
            self.append_output(render_rich_to_string(table, max_cols=cols))

        elif root == "/clear":
            with self.lock:
                self.buffer_text = ""
                self.scroll_offset = 0
            self.invalidate_ui()

        elif root == "/todo":
            if len(parts) == 1 or (len(parts) >= 2 and parts[1] == "list"):
                table = Table(title="📋 Task Board", box=box.ROUNDED, border_style=theme["rich_border"])
                table.add_column("#", style=f"bold {theme['warning']}", width=4)
                table.add_column("State", width=8)
                table.add_column("Task Item")

                if not self.harness.todos:
                    self.append_output("[dim italic]No tasks saved.[/dim italic]")
                else:
                    for t in self.harness.todos:
                        st = f"[{theme['accent']}]DONE[/{theme['accent']}]" if t["done"] else f"[{theme['warning']}]TODO[/{theme['warning']}]"
                        table.add_row(str(t["id"]), Text.from_markup(st), t["title"])
                    self.append_output(render_rich_to_string(table, max_cols=cols))
            elif len(parts) >= 3 and parts[1] == "add":
                task_str = " ".join(parts[2:])
                new_id = self.harness.add_todo(task_str)
                self.append_output(f"✓ Added task #{new_id}: {task_str}")
            elif len(parts) >= 3 and parts[1] == "done":
                if parts[2].isdigit() and self.harness.toggle_todo(int(parts[2])):
                    self.append_output(f"✓ Updated task #{parts[2]}")
                else:
                    self.append_output(f"Task #{parts[2]} not found.")
            elif len(parts) >= 3 and parts[1] == "del":
                if parts[2].isdigit() and self.harness.delete_todo(int(parts[2])):
                    self.append_output(f"✓ Deleted task #{parts[2]}")
                else:
                    self.append_output(f"Task #{parts[2]} not found.")
            elif len(parts) >= 2 and parts[1] == "clear":
                self.harness.clear_todos()
                self.append_output("✓ Cleared all tasks.")

        elif root in ["/tools", "/thinking"]:
            opt = parts[1].lower() if len(parts) > 1 else "toggle"
            field = "active_tools" if root == "/tools" else "show_thinking"
            cur = self.harness.config.get(field, True)
            new_val = not cur if opt == "toggle" else (opt == "on")
            self.harness.config[field] = new_val
            self.harness.save_config()
            self.append_output(f"✓ {root[1:].capitalize()} switched {'ON' if new_val else 'OFF'}.")

        elif root in ["/provider", "/p"] and len(parts) > 1:
            target = parts[1]
            if target in self.harness.config.get("providers", {}):
                self.harness.config["current_provider"] = target
                self.harness.save_config()
                self.append_output(f"✓ Switched to provider: {target}")
            else:
                self.append_output(f"Unknown provider '{target}'. Available: {', '.join(self.harness.config.get('providers', {}).keys())}")

        elif root == "/theme" and len(parts) > 1:
            target = parts[1].lower()
            if target in THEMES:
                self.harness.config["current_theme"] = target
                self.harness.save_config()
                self.app.style = self.build_style()
                self.append_history_block({"type": "raw", "text": f"✓ Switched theme to: {target}"})
                self.rebuild_buffer_text()
            else:
                self.append_output(f"Unknown theme. Available: {', '.join(THEMES.keys())}")

        elif root == "/model" and len(parts) > 1:
            prov = self.harness.config.get("current_provider")
            if prov and prov in self.harness.config.get("providers", {}):
                self.harness.config["providers"][prov]["default_model"] = parts[1]
                self.harness.save_config()
                self.append_output(f"✓ Default model for {prov} updated to '{parts[1]}'.")
            else:
                self.append_output(f"[red]No active provider. Use /provider <name> first.[/red]")

        elif root == "/copy":
            # Extract last code snippet or assistant response
            copied_text = ""
            for item in reversed(self.history_blocks):
                if item.get("type") == "assistant" and item.get("content"):
                    c = str(item["content"])
                    if "```" in c:
                        parts = c.split("```")
                        if len(parts) >= 3:
                            copied_text = parts[1].split("\n", 1)[-1].strip()
                    if not copied_text:
                        copied_text = c
                    break
            if not copied_text:
                self.append_output("[yellow]No assistant response available to copy.[/yellow]")
            else:
                ok = copy_to_clipboard(copied_text)
                if ok:
                    self.append_output(f"✓ Copied {len(copied_text)} characters to system clipboard.")
                else:
                    self.append_output(f"[yellow]Clipboard utility not found. Text ready ({len(copied_text)} chars).[/yellow]")

        elif root == "/undo":
            ok, msg = self.harness.undo_last_edit()
            if ok:
                self.append_output(f"✓ [green]{msg}[/green]")
            else:
                self.append_output(f"⚠️ [yellow]{msg}[/yellow]")

        elif root == "/pin":
            if len(parts) < 2:
                self.append_output("[yellow]Usage: /pin <path/to/file>[/yellow]")
            else:
                fp = Path(parts[1]).expanduser()
                if not fp.is_file():
                    self.append_output(f"[red]File '{fp}' not found.[/red]")
                else:
                    content = fp.read_text(encoding="utf-8", errors="replace")
                    snippet = f"[Pinned Context: {fp.name}]\n```{fp.suffix.lstrip('.') or 'text'}\n{content}\n```"
                    self.harness.messages.append({"role": "system", "content": snippet})
                    self.append_output(f"✓ Pinned [bold cyan]{fp.name}[/bold cyan] ({len(content.splitlines())} lines) to conversation context.")

        elif root == "/tree":
            target = Path(parts[1] if len(parts) > 1 else ".").expanduser()
            if not target.is_dir():
                self.append_output(f"[red]'{target}' is not a directory.[/red]")
            else:
                lines = [f"[bold cyan]{target.resolve().name}/[/bold cyan]"]
                count = 0
                for root_dir, dirs, files in os.walk(target):
                    dirs[:] = [d for d in dirs if d not in [".git", "node_modules", "__pycache__", ".venv", ".xdharness"]]
                    depth = len(Path(root_dir).relative_to(target).parts)
                    indent = "  " * depth
                    if depth > 0:
                        lines.append(f"{indent}📁 {Path(root_dir).name}/")
                    for f in sorted(files):
                        if count >= 60:
                            break
                        lines.append(f"{indent}  📄 {f}")
                        count += 1
                    if count >= 60:
                        lines.append(f"{indent}  ... (tree truncated)")
                        break
                tree_panel = Panel("\n".join(lines), title=f"🌳 Directory Tree: {target.name}", box=box.ROUNDED, border_style=theme["accent"])
                self.append_output(render_rich_to_string(tree_panel, max_cols=cols))

        elif root == "/export":
            fmt = parts[1].lower() if len(parts) > 1 else "md"
            ts = time.strftime("%Y%m%d_%H%M%S")
            export_path = BASE_DIR / f"export_{self.harness.session_id}_{ts}.{fmt}"
            try:
                if fmt == "json":
                    export_path.write_text(json.dumps(self.history_blocks, indent=2))
                elif fmt == "html":
                    html_content = f"<html><head><title>xdh Export {self.harness.session_id}</title></head><body style='background:#111;color:#eee;font-family:monospace;'><pre>{self.buffer_text}</pre></body></html>"
                    export_path.write_text(html_content, encoding="utf-8")
                else: # md
                    md_lines = [f"# xdh Session Export: {self.harness.session_id}\n"]
                    for it in self.history_blocks:
                        tp = it.get("type")
                        if tp == "user":
                            md_lines.append(f"\n### User ({it.get('timestamp')})\n{it.get('text')}\n")
                        elif tp == "assistant":
                            md_lines.append(f"\n### Assistant ({it.get('timestamp')})\n{it.get('content')}\n")
                        elif tp == "tool":
                            md_lines.append(f"\n> **Tool: {it.get('name')}**\n```\n{it.get('output')}\n```\n")
                    export_path.write_text("\n".join(md_lines), encoding="utf-8")
                self.append_output(f"✓ Exported transcript to: [bold cyan]{export_path}[/bold cyan]")
            except Exception as e:
                self.append_output(f"[red]Export failed: {str(e)}[/red]")

        elif root == "/session":
            sub = parts[1].lower() if len(parts) > 1 else "stats"
            if sub == "list":
                sessions = self.harness.list_saved_sessions()
                table = Table(title="🗂 Saved Sessions", box=box.ROUNDED, border_style=theme["rich_border"])
                table.add_column("Session ID", style=f"bold {theme['primary']}")
                table.add_column("Model")
                table.add_column("Messages", justify="right")
                table.add_column("Tokens", justify="right")
                table.add_column("Saved Date")
                for s in sessions[:12]:
                    d_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(s["saved_at"]))
                    table.add_row(s["id"], s["model"], str(s["messages_count"]), format_k_val(s["tokens"]), d_str)
                self.append_output(render_rich_to_string(table, max_cols=cols))
            elif sub == "load" and len(parts) >= 3:
                target_id = parts[2]
                if self.harness.load_session_by_id(target_id):
                    # Reconstruct history_blocks from restored messages
                    new_blocks = []
                    for m in self.harness.messages:
                        role = m.get("role")
                        content = m.get("content")
                        if role == "user":
                            new_blocks.append({"type": "user", "text": content or "", "timestamp": ""})
                        elif role == "assistant":
                            if m.get("reasoning_content") and self.harness.config.get("show_thinking"):
                                new_blocks.append({"type": "thought", "content": m["reasoning_content"], "timestamp": ""})
                            if content:
                                new_blocks.append({"type": "assistant", "content": content, "model": self.harness.current_provider_data.get("default_model", "assistant"), "timestamp": ""})
                        elif role == "tool":
                            new_blocks.append({"type": "tool", "name": m.get("name", "tool"), "badge": f"⚡ Tool › {m.get('name')}", "output": str(content), "args": {}, "timestamp": ""})
                    self.history_blocks = new_blocks
                    self.rebuild_buffer_text()
                    self.append_output(f"✓ Loaded session [bold green]{self.harness.session_id}[/bold green]. Context & buffer restored.")
            elif sub == "fork" and len(parts) >= 3:
                fork_tag = parts[2]
                new_sid = self.harness.fork_session(fork_tag)
                self.append_output(f"✓ Forked session into branch [bold green]{new_sid}[/bold green]. Continuing on new branch.")
            else:
                pdata = self.harness.current_provider_data
                ctx_max = pdata.get("context_window", 128000) or 128000
                current_tokens = self.harness.count_context_tokens()
                pct = min(100, int((current_tokens / ctx_max) * 100))
                ram = get_memory_usage_mb()
                curr_model = pdata.get("default_model", "none")
                cost_est = estimate_session_cost(curr_model, self.harness.total_tokens_consumed)

                table = Table(title="📊 Session Analytics", box=box.ROUNDED, border_style=theme["rich_border"])
                table.add_column("Metric", style=f"bold {theme['warning']}")
                table.add_column("Value", style="bold white")

                table.add_row("Session ID", self.harness.session_id)
                table.add_row("Active Provider", self.harness.config.get("current_provider", "none"))
                table.add_row("Active Model", curr_model)
                table.add_row("Total Messages", str(len(self.harness.messages)))
                table.add_row("Context Utilization", f"{current_tokens:,} / {ctx_max:,} tokens ({pct}%)")
                table.add_row("Total Tokens Consumed", f"{self.harness.total_tokens_consumed:,}")
                table.add_row("Estimated Cost", f"${cost_est:.4f} USD")
                table.add_row("Active Tasks (TODOs)", f"{len(self.harness.todos)} items")
                table.add_row("Process RSS Memory", f"{ram} MB")
                self.append_output(render_rich_to_string(table, max_cols=cols))

        elif root == "/history":
            past_prompts = self.auto_suggester.file_history.get_strings()
            recent = past_prompts[-15:] if past_prompts else []
            if not recent:
                self.append_output("[dim italic]No previous prompt history found.[/dim italic]")
            else:
                table = Table(title="📜 Recent Prompt History", box=box.ROUNDED, border_style=theme["rich_border"])
                table.add_column("#", style=f"bold {theme['warning']}", width=4)
                table.add_column("Prompt Text")
                for idx, prompt in enumerate(reversed(recent), 1):
                    clean_p = prompt.strip().replace("\n", " ")
                    if len(clean_p) > cols - 15:
                        clean_p = clean_p[:cols - 18] + "..."
                    table.add_row(str(idx), clean_p)
                self.append_output(render_rich_to_string(table, max_cols=cols))

        elif root == "/diff":
            # Scan recent assistant code blocks proposing patches or staged diffs
            if not self.staged_diffs:
                # Try finding diffs in the last assistant message
                for it in reversed(self.history_blocks):
                    if it.get("type") == "assistant" and "```diff" in it.get("content", ""):
                        for chunk in it["content"].split("```diff"):
                            if "```" in chunk:
                                diff_body = chunk.split("```")[0].strip()
                                self.staged_diffs.append({"diff": diff_body, "applied": False})
            if not self.staged_diffs:
                self.append_output("[yellow]No staged or pending diffs found. Use /apply after an edit suggestion.[/yellow]")
            else:
                for idx, sd in enumerate(self.staged_diffs, 1):
                    syn = Syntax(sd["diff"][:3000], "diff", theme="monokai", line_numbers=True)
                    st = "APPLIED" if sd.get("applied") else "PENDING (/apply)"
                    dp = Panel(syn, title=f"Proposed Diff #{idx} [{st}]", box=box.ROUNDED, border_style=theme["accent"])
                    self.append_output(render_rich_to_string(dp, max_cols=cols))

        elif root == "/apply":
            if not self.staged_diffs:
                self.append_output("[yellow]No pending diffs in queue. Run /diff to inspect.[/yellow]")
            else:
                applied_count = 0
                for sd in self.staged_diffs:
                    if not sd.get("applied"):
                        sd["applied"] = True
                        applied_count += 1
                self.append_output(f"✓ Marked {applied_count} diff hunks as applied.")

        elif root == "/tasks":
            sub = parts[1].lower() if len(parts) > 1 else "list"
            if sub == "list":
                tasks = BG_TASKS.list_tasks()
                if not tasks:
                    self.append_output("[dim italic]No active or recent background tasks.[/dim italic]")
                else:
                    table = Table(title="⚡ Background Tasks", box=box.ROUNDED, border_style=theme["rich_border"])
                    table.add_column("Task ID", style=f"bold {theme['primary']}")
                    table.add_column("Status")
                    table.add_column("Command")
                    for tk in tasks:
                        st = f"[green]running[/green]" if tk["status"] == "running" else f"[dim]{tk['status']}[/dim]"
                        table.add_row(tk["id"], Text.from_markup(st), tk["command"][:40])
                    self.append_output(render_rich_to_string(table, max_cols=cols))
            elif sub == "logs" and len(parts) >= 3:
                tid = parts[2]
                logs = BG_TASKS.get_logs(tid)
                lp = Panel(Text(logs), title=f"📋 Task Logs: {tid}", box=box.ROUNDED, border_style=theme["accent"])
                self.append_output(render_rich_to_string(lp, max_cols=cols))
            elif sub == "kill" and len(parts) >= 3:
                tid = parts[2]
                if BG_TASKS.kill_task(tid):
                    self.append_output(f"✓ Terminated task [bold red]{tid}[/bold red].")
                else:
                    self.append_output(f"Task '{tid}' not found or not running.")
            else:
                self.append_output("[yellow]Usage: /tasks <list|logs <id>|kill <id>>[/yellow]")

        elif root == "/git":
            sub = parts[1].lower() if len(parts) > 1 else "status"
            if sub == "status":
                out, _ = execute_tool("git_status", {}, self.harness)
                p = Panel(Text(out), title="🌿 Git Status", box=box.ROUNDED, border_style=theme["accent"])
                self.append_output(render_rich_to_string(p, max_cols=cols))
            elif sub == "diff":
                file_arg = parts[2] if len(parts) > 2 else ""
                out, _ = execute_tool("git_diff", {"path": file_arg}, self.harness)
                syn = Syntax(out[:4000], "diff", theme="monokai", line_numbers=True) if out else Text("Clean")
                p = Panel(syn, title=f"🌿 Git Diff {file_arg}", box=box.ROUNDED, border_style=theme["accent"])
                self.append_output(render_rich_to_string(p, max_cols=cols))
            elif sub == "commit" and len(parts) >= 3:
                commit_msg = " ".join(parts[2:])
                out, _ = execute_tool("git_commit", {"message": commit_msg, "files": "."}, self.harness)
                self.append_output(f"✓ {out}")
            else:
                self.append_output("[yellow]Usage: /git <status|diff [file]|commit <msg>>[/yellow]")

        elif root == "/search" and len(parts) > 1:
            q = " ".join(parts[1:])
            out, badge = execute_tool("search_web", {"query": q}, self.harness)
            sp = Panel(Markdown(out), title=f"🔎 Search: {q}", box=box.ROUNDED, border_style=theme["accent"])
            self.append_output(render_rich_to_string(sp, max_cols=cols))

        elif root == "/fetch" and len(parts) > 1:
            u = parts[1]
            out, badge = execute_tool("fetch_url", {"url": u}, self.harness)
            fp = Panel(Text(out), title=f"🌐 Fetch: {u}", box=box.ROUNDED, border_style=theme["accent"])
            self.append_output(render_rich_to_string(fp, max_cols=cols))

        elif root == "/image" and len(parts) > 1:
            img_path = Path(parts[1]).expanduser()
            if not img_path.is_file():
                self.append_output(f"[red]Image file '{img_path}' not found.[/red]")
            else:
                try:
                    img_bytes = img_path.read_bytes()
                    b64_str = base64.b64encode(img_bytes).decode("ascii")
                    mime = "image/png" if img_path.suffix.lower() == ".png" else "image/jpeg"
                    user_prompt = " ".join(parts[2:]) if len(parts) > 2 else f"Analyze this image: {img_path.name}"
                    img_msg = {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_prompt},
                            {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64_str}"}}
                        ]
                    }
                    self.harness.messages.append(img_msg)
                    self.append_history_block({
                        "type": "user",
                        "text": f"🖼 [Attached Image: {img_path.name}] {user_prompt}",
                        "timestamp": time.strftime("%H:%M:%S")
                    })
                    threading.Thread(target=self.run_agent_thread, args=(user_prompt,), daemon=True).start()
                except Exception as e:
                    self.append_output(f"[red]Failed to attach image: {str(e)}[/red]")

        elif root == "/index":
            sub = parts[1].lower() if len(parts) > 1 else "build"
            if sub == "build":
                # Build quick in-memory file index
                found = 0
                index_path = BASE_DIR / "workspace_index.json"
                idx_data = {}
                for root_dir, dirs, files in os.walk("."):
                    dirs[:] = [d for d in dirs if d not in [".git", "node_modules", "__pycache__", ".venv", ".xdharness"]]
                    for f in files:
                        p = Path(root_dir) / f
                        if p.suffix in [".py", ".js", ".ts", ".go", ".rs", ".md", ".json", ".sh", ".c", ".cpp"]:
                            try:
                                txt = p.read_text(encoding="utf-8", errors="ignore")[:5000]
                                idx_data[str(p)] = txt
                                found += 1
                            except Exception:
                                pass
                index_path.write_text(json.dumps(idx_data))
                self.append_output(f"✓ Built index with [bold cyan]{found}[/bold cyan] workspace files.")
            elif sub == "query" and len(parts) >= 3:
                keyword = parts[2].lower()
                index_path = BASE_DIR / "workspace_index.json"
                if not index_path.exists():
                    self.append_output("[yellow]Index not found. Run '/index build' first.[/yellow]")
                else:
                    idx_data = json.loads(index_path.read_text())
                    matches = [fn for fn, content in idx_data.items() if keyword in content.lower() or keyword in fn.lower()]
                    self.append_output(f"🔍 Index matches for '{keyword}':\n" + "\n".join(f"- {m}" for m in matches[:15]))

        elif root == "/scratch":
            sub = parts[1].lower() if len(parts) > 1 else "view"
            if sub == "view":
                sp_text = self.harness.scratchpad or "[Scratchpad empty. Use /scratch set <notes> to store snippets]"
                sp_panel = Panel(Text(sp_text), title="📝 Scratchpad Memo", box=box.ROUNDED, border_style=theme["accent"])
                self.append_output(render_rich_to_string(sp_panel, max_cols=cols))
            elif sub == "set" and len(parts) >= 3:
                self.harness.scratchpad = " ".join(parts[2:])
                self.harness.save_session()
                self.append_output("✓ Updated scratchpad note.")
            elif sub == "clear":
                self.harness.scratchpad = ""
                self.harness.save_session()
                self.append_output("✓ Cleared scratchpad.")

        elif root == "/skill":
            sub = parts[1].lower() if len(parts) > 1 else "list"
            if sub == "list":
                skills = SKILL_MGR.list_skills()
                if not skills:
                    self.append_output("[dim italic]No skills registered.[/dim italic]")
                else:
                    table = Table(title="🎯 Registered Skills", box=box.ROUNDED, border_style=theme["rich_border"])
                    table.add_column("Skill Name", style=f"bold {theme['primary']}")
                    table.add_column("Description")
                    for s in skills:
                        table.add_row(s.get("name", ""), s.get("description", ""))
                    self.append_output(render_rich_to_string(table, max_cols=cols))
            elif sub == "run" and len(parts) >= 3:
                sname = parts[2]
                sinput = " ".join(parts[3:]) if len(parts) > 3 else ""
                out, badge = execute_tool("call_skill", {"name": sname, "input_data": sinput}, self.harness)
                sp = Panel(Markdown(out), title=f"🎯 Skill Execution: {sname}", box=box.ROUNDED, border_style=theme["accent"])
                self.append_output(render_rich_to_string(sp, max_cols=cols))
            elif sub == "create":
                self.append_output("💡 [bold cyan]Create Skill[/bold cyan]: Ask the agent directly, e.g. `create a skill named 'deploy' to push and release` or use `/skill create <name> <description>`")
            else:
                self.append_output("[yellow]Usage: /skill <list|run <name> [input]|create>[/yellow]")

        elif root == "/agent":
            sub = parts[1].lower() if len(parts) > 1 else "list"
            if sub == "list":
                agents = AGENT_MGR.list_agents()
                if not agents:
                    self.append_output("[dim italic]No agents registered.[/dim italic]")
                else:
                    table = Table(title="🤖 Specialized Agents", box=box.ROUNDED, border_style=theme["rich_border"])
                    table.add_column("Agent", style=f"bold {theme['primary']}")
                    table.add_column("Role", style=f"bold {theme['warning']}")
                    table.add_column("Tools", style=f"dim {theme['accent']}")
                    table.add_column("Model Override")
                    for a in agents:
                        t_str = ", ".join(a.get("tools", []))[:30]
                        table.add_row(a.get("name", ""), a.get("role", ""), t_str, a.get("model") or "default")
                    self.append_output(render_rich_to_string(table, max_cols=cols))
            elif sub == "spawn" and len(parts) >= 3:
                task_prompt = " ".join(parts[2:])
                self.run_agent_thread(f"Spawn multiple specialized agents in parallel to solve: {task_prompt}")
            elif sub == "create":
                self.append_output("💡 [bold cyan]Create Agent[/bold cyan]: Ask the agent directly: `create an agent named 'auditor' with role 'Smart Contract Auditor' and tools read_file, grep_search`")
            else:
                self.append_output("[yellow]Usage: /agent <list|spawn <task>|create>[/yellow]")

        elif root == "/plugin":
            sub = parts[1].lower() if len(parts) > 1 else "list"
            if sub == "list":
                out, _ = execute_tool("manage_plugins", {"action": "list"}, self.harness)
                p = Panel(Markdown(out), title="🔌 Extensions & Plugins", box=box.ROUNDED, border_style=theme["accent"])
                self.append_output(render_rich_to_string(p, max_cols=cols))
            elif sub == "install" and len(parts) >= 3:
                git_url = parts[2]
                out, _ = execute_tool("manage_plugins", {"action": "install", "source": git_url}, self.harness)
                self.append_output(out)
            elif sub in ["del", "delete"] and len(parts) >= 3:
                pname = parts[2]
                out, _ = execute_tool("manage_plugins", {"action": "delete", "name": pname}, self.harness)
                self.append_output(out)
            elif sub == "add":
                self.append_output("💡 [bold cyan]Add Plugin[/bold cyan]: Ask the agent: `create a plugin called my_tool with a tool to fetch crypto prices`")
            else:
                self.append_output("[yellow]Usage: /plugin <list|install <git_url>|del <name>|add>[/yellow]")

        elif root == "/permission":
            if len(parts) > 1:
                mode = parts[1].lower()
                if mode in ["safe", "auto", "yolo"]:
                    self.harness.config["permission_mode"] = mode
                    self.harness.save_config()
                    self.append_output(f"✓ Execution permission mode set to: [bold cyan]{mode.upper()}[/bold cyan]")
                else:
                    self.append_output("[yellow]Usage: /permission <safe|auto|yolo>[/yellow]")
            else:
                curr = self.harness.config.get("permission_mode", "auto").upper()
                self.append_output(f"Current permission mode: [bold cyan]{curr}[/bold cyan]\nModes: safe (confirm all mutations), auto (guard destructive commands), yolo (unconstrained)")

        elif root == "/checkpoint":
            sub = parts[1].lower() if len(parts) > 1 else "list"
            if sub == "list":
                out, _ = execute_tool("manage_checkpoint", {"action": "list"}, self.harness)
                p = Panel(Markdown(out), title="💾 Workspace Checkpoints", box=box.ROUNDED, border_style=theme["accent"])
                self.append_output(render_rich_to_string(p, max_cols=cols))
            elif sub == "create":
                cp_name = parts[2] if len(parts) > 2 else f"cp_{int(time.time())}"
                desc = " ".join(parts[3:]) if len(parts) > 3 else ""
                out, _ = execute_tool("manage_checkpoint", {"action": "create", "name": cp_name, "description": desc}, self.harness)
                self.append_output(f"✓ {out}")
            elif sub == "restore" and len(parts) >= 3:
                target_cp = parts[2]
                out, _ = execute_tool("manage_checkpoint", {"action": "restore", "name": target_cp}, self.harness)
                self.append_output(f"✓ {out}")
            else:
                self.append_output("[yellow]Usage: /checkpoint <list|create [name]|restore <id>>[/yellow]")

        elif root == "/mcp":
            sub = parts[1].lower() if len(parts) > 1 else "list"
            if sub == "list":
                out, _ = execute_tool("manage_mcp", {"action": "list"}, self.harness)
                p = Panel(Markdown(out), title="🔌 Model Context Protocol (MCP)", box=box.ROUNDED, border_style=theme["accent"])
                self.append_output(render_rich_to_string(p, max_cols=cols))
            elif sub == "add" and len(parts) >= 4:
                mname = parts[2]
                mcmd = parts[3]
                margs = parts[4:] if len(parts) > 4 else []
                out, _ = execute_tool("manage_mcp", {"action": "add", "name": mname, "command": mcmd, "args": margs}, self.harness)
                self.append_output(f"✓ {out}")
            elif sub in ["remove", "del"] and len(parts) >= 3:
                mname = parts[2]
                out, _ = execute_tool("manage_mcp", {"action": "remove", "name": mname}, self.harness)
                self.append_output(f"✓ {out}")
            else:
                self.append_output("[yellow]Usage: /mcp <list|add <name> <command> [args...]|remove <name>>[/yellow]")

        elif root == "/outline":
            target_path = Path(parts[1] if len(parts) > 1 else ".").expanduser()
            if not target_path.is_file():
                self.append_output(f"[yellow]Usage: /outline <path/to/code_file>[/yellow]")
            else:
                out, badge = execute_tool("code_outline", {"path": str(target_path)}, self.harness)
                p = Panel(Text(out), title=f"📑 Code Outline: {target_path.name}", box=box.ROUNDED, border_style=theme["accent"])
                self.append_output(render_rich_to_string(p, max_cols=cols))

        elif root == "/schedule":
            if len(parts) >= 3 and parts[1].isdigit():
                interval = int(parts[1])
                task_text = " ".join(parts[2:])
                sched_id = len(self.active_schedules) + 1
                sched_entry = {"id": sched_id, "interval": interval, "task": task_text, "running": True}
                self.active_schedules.append(sched_entry)

                def _scheduled_worker(sc):
                    while sc.get("running"):
                        time.sleep(sc["interval"])
                        if not sc.get("running"):
                            break
                        self.append_output(f"⏰ [bold cyan]Scheduled Trigger (#{sc['id']})[/bold cyan]: {sc['task']}")
                        self.run_agent_thread(f"[SCHEDULED AUTONOMOUS TASK]: {sc['task']}")

                threading.Thread(target=_scheduled_worker, args=(sched_entry,), daemon=True).start()
                self.append_output(f"✓ Scheduled task #{sched_id} every {interval}s: \"{task_text}\"")
            else:
                if self.active_schedules:
                    lines = [f"#{s['id']}: every {s['interval']}s › {s['task']}" for s in self.active_schedules]
                    self.append_output("Active Schedules:\n" + "\n".join(lines))
                else:
                    self.append_output("[yellow]Usage: /schedule <interval_sec> <task prompt>[/yellow]")

        elif root == "/drawer":
            self.drawer_open = not self.drawer_open
            st = "OPEN" if self.drawer_open else "CLOSED"
            self.append_output(f"📊 Drawer sidecar: [bold cyan]{st}[/bold cyan] (toggle with F2 or Ctrl+B)")

        self.invalidate_ui()

    def run_agent_thread(self, user_input: str):
        self.is_busy = True
        self.abort_requested = False
        start_time = time.time()
        self.harness.status_label = "Thinking"
        self.invalidate_ui()
        theme = self.harness.theme

        try:
            self.harness.messages.append({"role": "user", "content": user_input})
            self.harness.compact_context_if_needed()
            tools = TOOLS_SPEC if self.harness.config.get("active_tools") else None

            turn = 0
            while True:
                turn += 1
                if self.abort_requested:
                    self.append_history_block({"type": "raw", "text": "[yellow]⚡ Generation halted by user.[/yellow]"})
                    break

                stream_gen = self.harness_stream_call(self.harness.messages, tools=tools)

                accumulated_thought = ""
                accumulated_content = ""
                final_tools = None

                with self.lock:
                    checkpoint_len = len(self.buffer_text)

                last_ui_update = 0.0
                turn_timestamp = time.strftime("%H:%M:%S")

                for token_type, chunk, tool_calls in stream_gen:
                    if self.abort_requested:
                        break

                    if token_type == "thought":
                        accumulated_thought += chunk
                    elif token_type == "content":
                        accumulated_content += chunk
                    elif token_type == "done":
                        final_tools = tool_calls

                    now = time.time()
                    is_final = (token_type == "done")
                    if (now - last_ui_update >= 0.05) or is_final:
                        last_ui_update = now
                        cols, _ = self.get_term_size()

                        # Live stream blocks preview
                        render_blocks = []
                        if accumulated_thought and self.harness.config.get("show_thinking"):
                            thought_panel = Panel(
                                Text(accumulated_thought, style=f"dim {theme['warning']}"),
                                title=f"⚡ Thinking {turn_timestamp}",
                                box=box.ROUNDED,
                                border_style=theme["warning"],
                                padding=(0, 1)
                            )
                            render_blocks.append(render_rich_to_string(thought_panel, max_cols=cols))

                        if accumulated_content:
                            curr_model = self.harness.current_provider_data.get("default_model", "assistant")
                            content_panel = Panel(
                                Markdown(accumulated_content),
                                title=f"xdh {turn_timestamp} ({curr_model})",
                                box=box.ROUNDED,
                                border_style=theme["primary"],
                                padding=(0, 1)
                            )
                            render_blocks.append(render_rich_to_string(content_panel, max_cols=cols))

                        if render_blocks:
                            combined = "\n".join(render_blocks)
                            with self.lock:
                                base = self.buffer_text[:checkpoint_len]
                                sep = "\n" if (base and combined) else ""
                                self.buffer_text = base + sep + combined
                                self.scroll_offset = 0
                            self.invalidate_ui()

                if self.abort_requested:
                    self.append_history_block({"type": "raw", "text": "[yellow]⚡ Turn cancelled by user.[/yellow]"})
                    break

                # Permanently store finalized thinking and content in history_blocks
                curr_model = self.harness.current_provider_data.get("default_model", "assistant")
                if accumulated_thought and self.harness.config.get("show_thinking"):
                    self.history_blocks.append({
                        "type": "thought",
                        "content": accumulated_thought,
                        "timestamp": turn_timestamp
                    })
                if accumulated_content:
                    self.history_blocks.append({
                        "type": "assistant",
                        "content": accumulated_content,
                        "model": curr_model,
                        "timestamp": turn_timestamp
                    })

                assistant_record: Dict[str, Any] = {
                    "role": "assistant",
                    "content": accumulated_content if accumulated_content else None
                }
                if accumulated_thought:
                    assistant_record["reasoning_content"] = accumulated_thought
                if final_tools:
                    for tc in final_tools:
                        if not tc.get("id"):
                            tc["id"] = self.harness.next_call_id()
                    assistant_record["tool_calls"] = final_tools

                self.harness.messages.append(assistant_record)

                if not final_tools or self.abort_requested:
                    break

                for tc in final_tools:
                    if self.abort_requested:
                        break

                    fn = tc.get("function", {})
                    name = fn.get("name")
                    call_id = tc.get("id")
                    try:
                        args = json.loads(fn.get("arguments", "{}"))
                    except Exception:
                        args = {}

                    self.harness.status_label = f"Tool: {name}"
                    self.invalidate_ui()

                    output, micro_badge = execute_tool(name, args, self.harness)
                    tool_timestamp = time.strftime("%H:%M:%S")

                    self.append_history_block({
                        "type": "tool",
                        "name": name,
                        "badge": micro_badge,
                        "output": str(output),
                        "args": args,
                        "timestamp": tool_timestamp
                    })

                    self.harness.messages.append({
                        "role": "tool",
                        "tool_call_id": call_id,
                        "name": name,
                        "content": str(output)
                    })

                self.harness.compact_context_if_needed()

            elapsed = round(time.time() - start_time, 2)
            if not self.abort_requested:
                self.append_history_block({
                    "type": "elapsed",
                    "seconds": elapsed
                })

            self.harness.save_session()
        except Exception as e:
            self.append_output(f"\n[bold red]Execution Error:[/bold red] {str(e)}")
        finally:
            notify_user_alert()
            self.harness.status_label = "Ready"
            self.is_busy = False
            self.abort_requested = False
            self.invalidate_ui()

    def harness_stream_call(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None):
        max_retries = 5
        base_retry_delay = 5  # Increases by 5s on each retry (5s, 10s, 15s, 20s, 25s)

        for attempt in range(1, max_retries + 1):
            if self.abort_requested:
                yield ("done", "", None)
                return

            pdata = self.harness.current_provider_data
            base_url = pdata.get("base_url", "").rstrip("/")
            api_key = pdata.get("api_key") or "none"
            model = pdata.get("default_model", "unknown")

            url = f"{base_url}/chat/completions"
            headers = {"Content-Type": "application/json"}
            if api_key and api_key != "none":
                headers["Authorization"] = f"Bearer {api_key}"

            payload: Dict[str, Any] = {
                "model": model,
                "messages": messages,
                "stream": True,
                "stream_options": {"include_usage": True}
            }
            if tools and self.harness.config.get("active_tools", True):
                payload["tools"] = tools

            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")

            try:
                with urllib.request.urlopen(req, timeout=120) as resp:
                    tool_calls_map: Dict[int, Dict[str, Any]] = {}
                    inside_think_tag = False
                    stream_usage_tokens = 0

                    for raw_line in resp:
                        if self.abort_requested:
                            break
                        line = raw_line.decode("utf-8").strip()
                        if not line or not line.startswith("data: "):
                            continue
                        data_str = line[6:].strip()
                        if data_str == "[DONE]":
                            break

                        try:
                            chunk = json.loads(data_str)
                        except Exception:
                            continue

                        usage = chunk.get("usage")
                        if usage and "total_tokens" in usage:
                            stream_usage_tokens = usage["total_tokens"]

                        choices = chunk.get("choices", [])
                        if not choices:
                            continue

                        delta = choices[0].get("delta", {})

                        reasoning_chunk = delta.get("reasoning_content") or delta.get("reasoning") or delta.get("thinking")
                        if reasoning_chunk:
                            yield ("thought", reasoning_chunk, None)

                        delta_tools = delta.get("tool_calls")
                        if delta_tools:
                            for dt in delta_tools:
                                idx = dt.get("index", 0)
                                if idx not in tool_calls_map:
                                    tool_calls_map[idx] = {"id": dt.get("id", ""), "type": "function", "function": {"name": "", "arguments": ""}}
                                if dt.get("id"):
                                    tool_calls_map[idx]["id"] = dt["id"]
                                fn = dt.get("function", {})
                                if fn.get("name"):
                                    tool_calls_map[idx]["function"]["name"] += fn["name"]
                                if fn.get("arguments"):
                                    tool_calls_map[idx]["function"]["arguments"] += fn["arguments"]

                        content_chunk = delta.get("content", "")
                        if content_chunk:
                            while content_chunk:
                                if inside_think_tag:
                                    if "</think>" in content_chunk:
                                        parts = content_chunk.split("</think>", 1)
                                        if parts[0]:
                                            yield ("thought", parts[0], None)
                                        content_chunk = parts[1] if len(parts) > 1 else ""
                                        inside_think_tag = False
                                    else:
                                        yield ("thought", content_chunk, None)
                                        content_chunk = ""
                                else:
                                    if "<think>" in content_chunk:
                                        parts = content_chunk.split("<think>", 1)
                                        if parts[0]:
                                            yield ("content", parts[0], None)
                                        content_chunk = parts[1] if len(parts) > 1 else ""
                                        inside_think_tag = True
                                    else:
                                        yield ("content", content_chunk, None)
                                        content_chunk = ""

                    if stream_usage_tokens > 0:
                        self.harness.total_tokens_consumed += stream_usage_tokens

                    final_tools = list(tool_calls_map.values()) if tool_calls_map else None
                    yield ("done", "", final_tools)
                    return

            except urllib.error.HTTPError as e:
                err = e.read().decode("utf-8", errors="replace")
                curr_prov = self.harness.config.get("current_provider")
                all_provs = [p for p in self.harness.config.get("providers", {}).keys() if p != curr_prov]

                # If server rate limit / overloaded (429/5xx), try failover if alternative provider exists
                if (e.code in [429, 500, 502, 503]) and all_provs:
                    backup = all_provs[0]
                    self.append_output(f"\n[yellow]⚠️ Provider '{curr_prov}' HTTP {e.code}. Failover to '{backup}'...[/yellow]")
                    self.harness.config["current_provider"] = backup
                    self.harness.save_config()
                    yield from self.harness_stream_call(messages, tools=tools)
                    return

                # Retry connection errors / server errors up to 5 times
                if attempt < max_retries and e.code in [429, 500, 502, 503, 504]:
                    delay = attempt * base_retry_delay
                    self.append_output(f"\n[yellow]⚠️ HTTP {e.code} error. Retrying attempt {attempt}/{max_retries} in {delay}s...[/yellow]")
                    time.sleep(delay)
                    continue
                else:
                    self.append_output(f"\n[API Error {e.code}]: {err}")
                    yield ("done", "", None)
                    return

            except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as net_err:
                if attempt < max_retries:
                    delay = attempt * base_retry_delay
                    self.append_output(f"\n[yellow]⚠️ Connection failed ({str(net_err)}). Retrying attempt {attempt}/{max_retries} in {delay}s...[/yellow]")
                    time.sleep(delay)
                    continue
                else:
                    self.append_output(f"\n[Network Failure]: Connection failed after {max_retries} attempts: {str(net_err)}")
                    yield ("done", "", None)
                    return

            except Exception as ex:
                self.append_output(f"\n[Unexpected Error]: {str(ex)}")
                yield ("done", "", None)
                return

# ---------------------------------------------------------
# Headless Execution Mode
# ---------------------------------------------------------
def run_headless(harness: XDHarness, prompt: str, pipe_mode: bool = False):
    """Executes prompt headlessly to stdout without launching prompt_toolkit TUI."""
    harness.messages.append({"role": "user", "content": prompt})
    harness.compact_context_if_needed()
    tools = get_all_tools_spec() if harness.config.get("active_tools") else None

    # Lightweight streaming generator
    pdata = harness.current_provider_data
    base_url = pdata.get("base_url", "").rstrip("/")
    api_key = pdata.get("api_key") or "none"
    model = pdata.get("default_model", "unknown")

    turn = 0
    while True:
        turn += 1
        payload = {
            "model": model,
            "messages": harness.messages,
            "stream": True,
            "stream_options": {"include_usage": True}
        }
        if tools and harness.config.get("active_tools", True):
            payload["tools"] = tools

        req_data = json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if api_key and api_key != "none":
            headers["Authorization"] = f"Bearer {api_key}"

        req = urllib.request.Request(f"{base_url}/chat/completions", data=req_data, headers=headers, method="POST")

        accumulated_content = ""
        accumulated_thought = ""
        tool_calls_map: Dict[int, Dict[str, Any]] = {}
        inside_think = False

        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                for raw_line in resp:
                    line = raw_line.decode("utf-8").strip()
                    if not line or not line.startswith("data: "):
                        continue
                    data_str = line[6:].strip()
                    if data_str == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data_str)
                    except Exception:
                        continue
                    choices = chunk.get("choices", [])
                    if not choices:
                        continue
                    delta = choices[0].get("delta", {})

                    thought_chunk = delta.get("reasoning_content") or delta.get("reasoning")
                    if thought_chunk:
                        accumulated_thought += thought_chunk
                        if not pipe_mode and harness.config.get("show_thinking"):
                            sys.stderr.write(f"\033[90m{thought_chunk}\033[0m")
                            sys.stderr.flush()

                    delta_tools = delta.get("tool_calls")
                    if delta_tools:
                        for dt in delta_tools:
                            idx = dt.get("index", 0)
                            if idx not in tool_calls_map:
                                tool_calls_map[idx] = {"id": dt.get("id", ""), "type": "function", "function": {"name": "", "arguments": ""}}
                            if dt.get("id"):
                                tool_calls_map[idx]["id"] = dt["id"]
                            fn = dt.get("function", {})
                            if fn.get("name"):
                                tool_calls_map[idx]["function"]["name"] += fn["name"]
                            if fn.get("arguments"):
                                tool_calls_map[idx]["function"]["arguments"] += fn["arguments"]

                    content_chunk = delta.get("content", "")
                    if content_chunk:
                        while content_chunk:
                            if inside_think:
                                if "</think>" in content_chunk:
                                    p, content_chunk = content_chunk.split("</think>", 1)
                                    inside_think = False
                                else:
                                    content_chunk = ""
                            else:
                                if "<think>" in content_chunk:
                                    p, content_chunk = content_chunk.split("<think>", 1)
                                    if p:
                                        sys.stdout.write(p)
                                        sys.stdout.flush()
                                        accumulated_content += p
                                    inside_think = True
                                else:
                                    sys.stdout.write(content_chunk)
                                    sys.stdout.flush()
                                    accumulated_content += content_chunk
                                    content_chunk = ""

        except Exception as e:
            sys.stderr.write(f"\n[Error: {e}]\n")
            break

        assistant_record = {
            "role": "assistant",
            "content": accumulated_content if accumulated_content else None
        }
        if accumulated_thought:
            assistant_record["reasoning_content"] = accumulated_thought
        final_tools = list(tool_calls_map.values()) if tool_calls_map else None
        if final_tools:
            for tc in final_tools:
                if not tc.get("id"):
                    tc["id"] = harness.next_call_id()
            assistant_record["tool_calls"] = final_tools

        harness.messages.append(assistant_record)

        if not final_tools:
            sys.stdout.write("\n")
            sys.stdout.flush()
            break

        for tc in final_tools:
            fn = tc.get("function", {})
            fname = fn.get("name")
            call_id = tc.get("id")
            try:
                fargs = json.loads(fn.get("arguments", "{}"))
            except Exception:
                fargs = {}

            if not pipe_mode:
                sys.stderr.write(f"\n⚡ \033[1;36mTool: {fname}\033[0m {json.dumps(fargs)[:60]}\n")
                sys.stderr.flush()

            tout, _ = execute_tool(fname, fargs, harness)
            harness.messages.append({
                "role": "tool",
                "tool_call_id": call_id,
                "name": fname,
                "content": str(tout)
            })

    harness.save_session()

# ---------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description=f"xdh (xdharness) v{__version__} - Autonomous Terminal Agent Harness")
    parser.add_argument("-v", "--version", action="version", version=f"xdh {__version__}")
    parser.add_argument("-p", "--prompt", type=str, default="", help="Run prompt non-interactively (headless mode)")
    parser.add_argument("--pipe", action="store_true", help="Pipe mode: read stdin, write clean LLM answer to stdout")
    parser.add_argument("--safe", action="store_true", help="Safe permission mode (prompts before file/system modifications)")
    parser.add_argument("--yolo", action="store_true", help="YOLO mode (unconstrained autonomous tool execution)")
    parser.add_argument("--provider", type=str, default="", help="Override active provider (ollama, openrouter, openai, groq)")
    parser.add_argument("--model", type=str, default="", help="Override default model")

    args, unknown = parser.parse_known_args()

    harness = XDHarness()

    # Apply overrides
    if args.safe:
        harness.config["permission_mode"] = "safe"
    elif args.yolo:
        harness.config["permission_mode"] = "yolo"

    if args.provider and args.provider in harness.config.get("providers", {}):
        harness.config["current_provider"] = args.provider
    if args.model:
        curr_p = harness.config.get("current_provider")
        if curr_p and curr_p in harness.config.get("providers", {}):
            harness.config["providers"][curr_p]["default_model"] = args.model

    # Check for piped stdin or -p/--prompt
    piped_stdin = ""
    if not sys.stdin.isatty():
        try:
            piped_stdin = sys.stdin.read().strip()
        except Exception:
            pass

    prompt_to_run = args.prompt
    if piped_stdin:
        if prompt_to_run:
            prompt_to_run = f"{prompt_to_run}\n\n[Piped Standard Input]:\n{piped_stdin}"
        else:
            prompt_to_run = piped_stdin

    if prompt_to_run or args.pipe:
        run_headless(harness, prompt_to_run, pipe_mode=args.pipe)
        return

    # Full TUI interactive mode
    app = XDHApp(harness)
    app.app.run()

if __name__ == "__main__":
    main()
