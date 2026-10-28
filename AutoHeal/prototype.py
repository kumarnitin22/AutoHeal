#!/usr/bin/env python3
"""
AutoHeal - Universal AI-IDE Syntax Healer & Config Transpiler
Hackathon Track: AI & Developer Tools
Zero external dependencies (uses standard Python library only).
"""

import os
import sys
import ast
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Enable UTF-8 encoding on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


class Colors:
    """Terminal styling ANSI codes."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    GRAY = "\033[90m"

    @classmethod
    def disable(cls):
        cls.RESET = cls.BOLD = cls.GREEN = cls.YELLOW = ""
        cls.RED = cls.CYAN = cls.BLUE = cls.MAGENTA = cls.GRAY = ""


if not sys.stdout.isatty():
    Colors.disable()


def print_banner():
    banner = r"""
====================================================================
   _         _        _   _            _ 
  /_\  _   _| |_ ___ | | | | ___  __ _| |
 //_\\| | | | __/ _ \| |_| |/ _ \/ _` | |
/  _  \ |_| | || (_) |  _  |  __/ (_| | |
\_/ \_/\__,_|\__\___/|_| |_|\___|\__,_|_|
  AI Code Syntax Healer & Multi-Editor Rule Transpiler
===================================================================="""
    print(f"{Colors.CYAN}{Colors.BOLD}{banner.strip()}{Colors.RESET}\n")


class CodeSyntaxHealer:
    """Detects and repairs truncated Python code from interrupted AI sessions."""
    
    OPEN_TO_CLOSE: Dict[str, str] = {'(': ')', '[': ']', '{': '}'}
    CLOSE_TO_OPEN: Dict[str, str] = {')': '(', ']': '[', '}': '{'}
    BLOCK_PREFIXES = (
        'def ', 'async def ', 'class ', 'if ', 'elif ', 'else:', 'else',
        'for ', 'async for ', 'while ', 'try:', 'try', 'except ', 'except:',
        'finally:', 'finally', 'with ', 'async with '
    )

    @classmethod
    def test_syntax(cls, code: str) -> Tuple[bool, Optional[str]]:
        try:
            ast.parse(code)
            return True, None
        except SyntaxError as err:
            return False, f"Line {err.lineno}: {err.msg}"
        except Exception as err:
            return False, str(err)

    @classmethod
    def heal(cls, code: str) -> Tuple[bool, str, List[str]]:
        is_valid, _ = cls.test_syntax(code)
        if is_valid:
            return True, code, ["Code syntax is already valid"]

        actions: List[str] = []
        repaired = code.rstrip()

        # Step 1: Delimiter stack tracking (LIFO balancing)
        stack: List[str] = []
        for char in repaired:
            if char in cls.OPEN_TO_CLOSE:
                stack.append(char)
            elif char in cls.CLOSE_TO_OPEN:
                matching_open = cls.CLOSE_TO_OPEN[char]
                if stack and stack[-1] == matching_open:
                    stack.pop()

        if stack:
            closing_chars = [cls.OPEN_TO_CLOSE[op] for op in reversed(stack)]
            closing_str = "".join(closing_chars)
            repaired += closing_str
            actions.append(f"Balanced unclosed delimiters -> appended '{closing_str}'")

        is_valid, err_msg = cls.test_syntax(repaired)
        if is_valid:
            return True, repaired + "\n", actions

        # Step 2: Handle block header missing colon
        lines = repaired.splitlines()
        last_line = lines[-1] if lines else ""
        if not repaired.endswith(':'):
            if any(last_line.strip().startswith(p) for p in cls.BLOCK_PREFIXES) or (err_msg and "expected ':'" in err_msg):
                repaired += ":"
                actions.append("Appended missing ':' to block header")

        # Step 3: Handle dangling colon (unimplemented body)
        if repaired.endswith(':'):
            colon_line = repaired.splitlines()[-1] if repaired.splitlines() else ""
            indent_count = len(colon_line) - len(colon_line.lstrip())
            pass_indent = " " * (indent_count + 4) if indent_count > 0 else "    "
            repaired += f"\n{pass_indent}pass"
            actions.append(f"Appended newline with '{pass_indent.strip() or '    '}pass'")

        final_code = repaired if repaired.endswith("\n") else repaired + "\n"
        is_valid, final_err = cls.test_syntax(final_code)
        if is_valid:
            return True, final_code, actions

        return False, final_code, [f"Unresolved SyntaxError ({final_err})"]


class RuleTranspiler:
    """Maps custom instructions across AI editor formats."""

    @classmethod
    def transpile(cls, target_dir: str, target_format: str = "windsurf") -> Tuple[bool, str]:
        dir_path = Path(target_dir).resolve()
        cursor_file = dir_path / ".cursorrules"
        windsurf_file = dir_path / ".windsurfrules"

        if target_format.lower() == "windsurf":
            if not cursor_file.exists():
                return False, "'.cursorrules' not found (skipped rule conversion)."
            content = cursor_file.read_text(encoding="utf-8")
            header = (
                "# ==============================================================================\n"
                "# Windsurf Custom Rules (.windsurfrules)\n"
                "# Auto-transpiled from .cursorrules by AutoHeal\n"
                "# ==============================================================================\n\n"
            )
            windsurf_file.write_text(header + content.strip() + "\n", encoding="utf-8")
            return True, "Transpiled '.cursorrules' -> '.windsurfrules' successfully."

        return False, f"Unsupported target format: '{target_format}'"


def run_autoheal(target_dir: str, target_rules: str = "windsurf") -> bool:
    print_banner()
    path = Path(target_dir).resolve()

    if not path.exists() or not path.is_dir():
        print(f"{Colors.RED}[ERROR] Target directory not found: {path}{Colors.RESET}")
        return False

    print(f"{Colors.BLUE}[INFO]{Colors.RESET} Scanning directory : {Colors.BOLD}{path}{Colors.RESET}")
    print(f"{Colors.BLUE}[INFO]{Colors.RESET} Target IDE rules   : {Colors.BOLD}{target_rules}{Colors.RESET}\n" + "-" * 65)

    py_files = [
        p for p in path.rglob("*.py")
        if not any(x in p.parts for x in [".venv", "venv", "__pycache__", ".git", "build", "dist"])
    ]
    print(f"{Colors.CYAN}[SCAN]{Colors.RESET} Discovered {len(py_files)} Python file(s).\n")

    healed_count = 0
    valid_count = 0
    failed_count = 0

    for file_path in py_files:
        code = file_path.read_text(encoding="utf-8")
        is_valid, _ = CodeSyntaxHealer.test_syntax(code)

        if is_valid:
            print(f"{Colors.GREEN}[OK]{Colors.RESET}     {file_path.name} - Valid syntax")
            valid_count += 1
            continue

        healed, fixed_code, actions = CodeSyntaxHealer.heal(code)
        if healed:
            file_path.write_text(fixed_code, encoding="utf-8")
            print(f"{Colors.GREEN}{Colors.BOLD}[HEALED]{Colors.RESET} {file_path.name}")
            for action in actions:
                print(f"         |-- {Colors.GRAY}{action}{Colors.RESET}")
            healed_count += 1
        else:
            print(f"{Colors.RED}[FAIL]{Colors.RESET}   {file_path.name} - Unresolved syntax errors")
            failed_count += 1

    print("-" * 65)
    rule_ok, rule_msg = RuleTranspiler.transpile(str(path), target_rules)
    color = Colors.GREEN if rule_ok else Colors.YELLOW
    print(f"{Colors.MAGENTA}[RULE]{Colors.RESET}   {color}{rule_msg}{Colors.RESET}")

    print("=" * 65)
    print(f"{Colors.BOLD}Execution Summary:{Colors.RESET}")
    print(f"  * Total Files Scanned : {len(py_files)}")
    print(f"  * Already Valid       : {valid_count}")
    print(f"  * Auto-Repaired       : {Colors.GREEN}{healed_count}{Colors.RESET}")
    print(f"  * Unresolved Errors   : {Colors.RED if failed_count else Colors.GRAY}{failed_count}{Colors.RESET}")
    print("=" * 65)

    if failed_count == 0:
        print(f"{Colors.GREEN}{Colors.BOLD}[SUCCESS] Project is fully healed and ready to run in {target_rules.capitalize()}!{Colors.RESET}\n")
        return True
    return False


def main():
    parser = argparse.ArgumentParser(
        prog="AutoHeal",
        description="AutoHeal: AI Syntax Repair & Multi-Editor Rule Transpiler CLI."
    )
    parser.add_argument("--dir", default=".", help="Target project directory (default: current directory)")
    parser.add_argument("--to", default="windsurf", choices=["windsurf"], help="Target AI editor (default: windsurf)")
    args = parser.parse_args()

    success = run_autoheal(args.dir, args.to)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()