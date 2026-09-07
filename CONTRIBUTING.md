# Contributing to xdh (xdharness)

Thank you for your interest in contributing to `xdh`! We welcome bug reports, feature suggestions, architecture improvements, and pull requests.

---

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). Please report any violations or concerns to **pwnedbytes@gmail.com**.

---

## How Can I Contribute?

### 🐛 Reporting Bugs

- Search the [GitHub Issues](https://github.com/PwnedBytes0x1/xdh/issues) to ensure the issue hasn't already been reported.
- Open an issue with a clear title and description.
- Include:
  - `xdh` version (`xdh --version`)
  - Python version (`python3 --version`)
  - OS / Environment (e.g. Android Termux, Ubuntu, macOS, Windows PowerShell)
  - Active theme and provider
  - Steps to reproduce and full tracebacks or terminal logs.

### 💡 Requesting Features

- Open a feature request on [GitHub Issues](https://github.com/PwnedBytes0x1/xdh/issues).
- Detail the problem, use-case, and why this enhances `xdh`.
- Discuss UI impacts (e.g. keybindings, micro-badges, or viewport layout).

---

## 🛠️ Local Development Setup

1. **Fork and Clone**:
   ```bash
   git clone https://github.com/your-username/xdh.git
   cd xdh
   ```

2. **Create a Virtual Environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install in Editable Mode**:
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

4. **Verify Syntax & Smoke Test**:
   ```bash
   python3 -m py_compile xdh.py
   python3 xdh.py --version
   ```

---

## 📝 Pull Request Guidelines

1. **Branch Naming**: Use clear prefixes like `feature/`, `fix/`, or `docs/`.
2. **Code Style**:
   - Keep the codebase lightweight and maintain cross-platform compatibility (Android Termux must always work smoothly without binary dependencies).
   - Preserve comments, error-handling fallbacks, and user feedback strings.
3. **Commit Messages**: Follow standard conventional commit formats (e.g., `feat: ...`, `fix: ...`, `docs: ...`).
4. **Testing**: Smoke-test changes directly in the TUI across both desktop and mobile/Termux screen dimensions.

---

## 📄 License

By contributing to `xdh`, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).
