# ⚙️ Configuration & Providers

`xdh` features a modular multi-provider architecture designed to interface with cloud APIs and local inference engines interchangeably.

---

## 🗂️ Configuration File

Settings are saved in `~/.xdharness/config.json`. An example configuration:

```json
{
  "current_provider": "openrouter",
  "current_theme": "tokyo_night",
  "active_tools": true,
  "show_thinking": true,
  "compaction_threshold": 0.85,
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
      "default_model": "deepseek-coder",
      "context_window": 64000
    },
    "ollama": {
      "base_url": "http://localhost:11434/v1/chat/completions",
      "api_key": "ollama",
      "default_model": "llama3:latest",
      "context_window": 32000
    }
  }
}
```

---

## 🔄 Automatic Model Failover

One of the marquee features in `xdh` is **Auto-Failover**:
- When an active provider returns HTTP status `429` (Rate Limited), `500`, `502`, or `503` (Server / Outage errors), `xdh` automatically detects configured alternative providers in your `config.json`.
- The engine logs a warning notification in the viewport:
  ```text
  ⚠️ Provider 'openrouter' returned HTTP 429. Auto-failing over to 'openai'...
  ```
- The current prompt and session state seamlessly resume on the failover provider without interrupting your flow.

---

## 🎛️ In-Session Commands

- `/provider <name>`: Switch the active provider on the fly.
- `/model <name>`: Change model name for the current provider.
- `/thinking <on|off>`: Toggle live reasoning/thought token rendering.
- `/settings`: Display active configuration properties.
