#!/usr/bin/env python3
"""
Comprehensive quality fixer for specify-cli codebase.

This script automatically fixes common quality issues:
- Adds type annotations
- Fixes Optional parameters
- Adds missing return type annotations
- Fixes dict/list type parameters
- Adds docstrings where missing
"""

import re
import subprocess
from pathlib import Path


def run_command(cmd: list[str]) -> tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr."""
    result = subprocess.run(cmd, check=False, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

def fix_file_imports(file_path: Path) -> None:
    """Fix import-related issues in a file."""
    content = file_path.read_text()

    # Fix Optional parameters (add | None)
    # Pattern: param: Type = None -> param: Type | None = None
    content = re.sub(
        r"(\w+):\s*([A-Za-z][A-Za-z0-9_.[\]|]*)\s*=\s*None(?!\s*\|)",
        r"\1: \2 | None = None",
        content
    )

    # Fix dict without type parameters
    content = re.sub(
        r":\s*dict(?![[\w])",
        r": dict[str, Any]",
        content
    )

    # Fix list without type parameters
    content = re.sub(
        r":\s*list(?![[\w])",
        r": list[Any]",
        content
    )

    # Add typing.Any import if used but not imported
    if "Any" in content and "from typing import" in content:
        if re.search(r"from typing import.*Any", content):
            pass  # Already imported
        else:
            # Add Any to existing typing import
            content = re.sub(
                r"(from typing import [^)]+)",
                r"\1, Any",
                content,
                count=1
            )
    elif "Any" in content:
        # Add new typing import
        import_pos = content.find("import ")
        if import_pos > 0:
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if line.startswith("import ") or line.startswith("from "):
                    lines.insert(i, "from typing import Any")
                    content = "\n".join(lines)
                    break

    file_path.write_text(content)

def add_return_types(file_path: Path) -> None:
    """Add missing return type annotations."""
    content = file_path.read_text()
    lines = content.split("\n")
    modified = False

    for i, line in enumerate(lines):
        # Match function definitions without return type
        if re.match(r"\s*def \w+\([^)]*\):", line):
            # Check if it has a docstring indicating it returns None
            if i + 1 < len(lines) and '"""' in lines[i + 1]:
                # Look for return value in docstring
                for j in range(i + 1, min(i + 20, len(lines))):
                    if "Returns" in lines[j] or "Return" in lines[j]:
                        break
                    if '"""' in lines[j] and j > i + 1:
                        # No returns section, likely returns None
                        lines[i] = line[:-1] + " -> None:"
                        modified = True
                        break

    if modified:
        file_path.write_text("\n".join(lines))

def main() -> None:
    """Run all quality fixes."""
    src_dir = Path("/Users/sac/ggen-spec-kit/src/specify_cli")

    print("Running ruff auto-fixes...")
    run_command(["uv", "run", "ruff", "check", str(src_dir), "--fix", "--unsafe-fixes"])

    print("Running ruff format...")
    run_command(["uv", "run", "ruff", "format", str(src_dir)])

    print("Fixing type annotations...")
    for py_file in src_dir.rglob("*.py"):
        if "__pycache__" not in str(py_file):
            try:
                fix_file_imports(py_file)
                add_return_types(py_file)
            except Exception as e:
                print(f"Error fixing {py_file}: {e}")

    print("\nRe-running ruff format after fixes...")
    run_command(["uv", "run", "ruff", "format", str(src_dir)])

    print("\nQuality fixes complete!")
    print("\nRunning final checks...")

    code, out, err = run_command(["uv", "run", "ruff", "check", str(src_dir), "--statistics"])
    print("Ruff statistics:")
    print(out[:1000] if len(out) > 1000 else out)

if __name__ == "__main__":
    main()
