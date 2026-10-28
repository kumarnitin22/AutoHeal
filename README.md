# AutoHeal 🛠️
> **Universal AI-IDE Syntax Recovery Engine & Config Transpiler**  
> *Track: AI & Developer Tools*

AutoHeal resolves vendor lock-in and token-exhaustion syntax corruption across AI-assisted development environments (Cursor, Windsurf, VS Code). When an LLM model terminates generation abruptly due to token quotas, AutoHeal detects truncated syntax trees, balances delimiters in LIFO order, caps incomplete block declarations, and transpiles editor prompt rules seamlessly.

---

## ⚡ The Problem
1. **Mid-Generation Syntax Halts:** Abrupt API token exhaustion leaves unclosed brackets (`{`, `[`, `(`) and dangling colons (`:`), causing immediate compiler failure.
2. **Editor Context Lock-In:** Custom instructions like `.cursorrules` are ignored when switching to alternative editors like Windsurf (`.windsurfrules`).

---

## 🚀 Key Features
- **Zero External Dependencies:** Built entirely with standard library modules (`ast`, `sys`, `os`, `pathlib`, `argparse`).
- **LIFO Bracket Resolution:** Reconstructs closing delimiters for deeply nested dictionaries, arrays, and tuple parameters.
- **Indentation-Aware Block Healing:** Closes empty control structures (`def`, `if`, `for`) with contextually indented `pass` tokens.
- **Config Transpilation:** Translates `.cursorrules` directly into compliant `.windsurfrules`.

---

## 📦 Project Structure
```text
AutoHeal/
├── prototype.py           # Core AST repair engine and CLI
├── demo_test/             # Sample truncated files for reproduction
│   ├── broken_delimiters.py
│   ├── broken_colon.py
│   └── .cursorrules
└── README.md
