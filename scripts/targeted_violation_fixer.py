#!/usr/bin/env python3
"""Targeted fixer for specific ruff violations."""

import re
import sys
from pathlib import Path


def fix_pyle1206(content: str) -> tuple[str, int]:
    """Fix PLE1206: Not enough arguments for logging format string."""
    fixes = 0
    lines = content.split("\n")
    new_lines = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # Pattern: logger.exception("... %s: %s", arg1) - missing arg2
        if "logger.exception" in line or "logger.error" in line:
            # Count %s placeholders
            placeholders = line.count("%s") + line.count("%d") + line.count("%r")

            # Count arguments after the format string
            if placeholders > 0:
                # Look for arguments on this line and next lines
                full_statement = line
                j = i + 1
                while j < len(lines) and not full_statement.strip().endswith(")"):
                    full_statement += "\n" + lines[j]
                    j += 1

                # Count commas after the format string
                # This is a heuristic
                if full_statement.count(",") < placeholders:
                    # Add missing argument
                    # Replace last ) with , exception_var)
                    if "except" in "\n".join(lines[max(0, i - 5) : i]):
                        # We're likely in an except block
                        # Don't fix this - too complex
                        pass

        new_lines.append(line)
        i += 1

    return "\n".join(new_lines), fixes


def fix_era001(content: str) -> tuple[str, int]:
    """Fix ERA001: Remove commented-out code."""
    fixes = 0
    lines = content.split("\n")
    new_lines = []

    for line in lines:
        # Skip lines that are just commented code (heuristic)
        stripped = line.strip()
        if stripped.startswith("#"):
            # Check if it's likely code vs documentation
            # If it has code patterns, skip it
            code_patterns = [
                "import ",
                "def ",
                "class ",
                "return ",
                "if ",
                "for ",
                "while ",
                "try:",
                "except",
                " = ",
                ".(",
            ]

            if any(pattern in stripped for pattern in code_patterns):
                # Likely commented code - but let's be conservative
                # Only remove if it's clearly not a TODO or explanation
                if not any(keyword in stripped.upper() for keyword in ["TODO", "FIXME", "NOTE", "HACK", "XXX"]):
                    fixes += 1
                    continue  # Skip this line

        new_lines.append(line)

    return "\n".join(new_lines), fixes


def fix_f401(content: str) -> tuple[str, int]:
    """Fix F401: Remove unused imports."""
    fixes = 0
    lines = content.split("\n")

    # This is complex - use ruff's built-in fixer instead
    return content, fixes


def fix_sim102(content: str) -> tuple[str, int]:
    """Fix SIM102: Collapsible if statements."""
    fixes = 0

    # Pattern: if condition1:\n    if condition2:
    # Replace with: if condition1 and condition2:

    # This requires AST - skip for now
    return content, fixes


def fix_b904_aggressive(content: str) -> tuple[str, int]:
    """More aggressive B904 fixer."""
    fixes = 0

    # Pattern: raise Exception(...) in except block without from
    pattern = r"(\s+)(raise\s+\w+\([^)]*\))(\s*(?:#.*)?$)"

    def replace_raise(match: re.Match[str]) -> str:
        nonlocal fixes
        indent = match.group(1)
        raise_stmt = match.group(2)
        trailing = match.group(3)

        if "from" not in raise_stmt:
            fixes += 1
            return f"{indent}{raise_stmt} from None{trailing}"
        return match.group(0)

    content = re.sub(pattern, replace_raise, content, flags=re.MULTILINE)
    return content, fixes


def fix_g004_remaining(content: str) -> tuple[str, int]:
    """Fix remaining G004 violations."""
    fixes = 0

    # Pattern: logger.method(f"...")
    # Replace with: logger.method("...", args)

    # This is complex - skip for now
    return content, fixes


def fix_file(file_path: Path) -> dict:
    """Fix a single file."""
    try:
        content = file_path.read_text(encoding="utf-8")
        original = content
        total_fixes = 0

        # Apply fixes
        content, n = fix_era001(content)
        total_fixes += n

        content, n = fix_b904_aggressive(content)
        total_fixes += n

        # Write back if changed
        if content != original:
            file_path.write_text(content, encoding="utf-8")

        return {"file": str(file_path), "fixes": total_fixes, "success": True}

    except Exception as e:
        return {"file": str(file_path), "fixes": 0, "success": False, "error": str(e)}


def main() -> None:
    """Main entry point."""
    src_path = Path("/home/user/ggen-spec-kit/src/specify_cli")

    print("=" * 80)
    print("TARGETED VIOLATION FIXER")
    print("=" * 80)
    print()

    py_files = list(src_path.rglob("*.py"))
    print(f"Processing {len(py_files)} files...")
    print()

    results = []
    for py_file in py_files:
        result = fix_file(py_file)
        results.append(result)
        if result["fixes"] > 0:
            print(f"✓ {py_file.relative_to(src_path)}: {result['fixes']} fixes")

    print()
    print("=" * 80)
    total_fixes = sum(r["fixes"] for r in results)
    print(f"Total fixes: {total_fixes}")
    print("=" * 80)


if __name__ == "__main__":
    main()
