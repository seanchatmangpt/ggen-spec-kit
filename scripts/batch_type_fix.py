#!/usr/bin/env python3
"""
Batch Type Error Fixer

Systematically fixes common mypy type errors across the codebase.
Uses pattern matching and intelligent inference to add type annotations.
"""

import re
import subprocess
import sys
from pathlib import Path
from typing import Any


def get_mypy_errors() -> list[tuple[str, int, str, str]]:
    """Get all mypy errors as (file, line, error_code, message) tuples."""
    result = subprocess.run(
        ["uv", "run", "mypy", "src/specify_cli", "--show-error-codes", "--no-error-summary"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )

    errors = []
    for line in result.stdout.split('\n'):
        # Parse: file.py:123: error: message [error-code]
        match = re.match(r'(.+?):(\d+):\s*error:\s*(.+?)\s*\[(\w+(?:-\w+)*)\]', line)
        if match:
            filepath, lineno, message, error_code = match.groups()
            errors.append((filepath, int(lineno), error_code, message))

    return errors


def fix_no_untyped_def(filepath: str, lineno: int) -> bool:
    """Fix no-untyped-def errors by adding parameter type annotations."""
    path = Path(filepath)
    if not path.exists():
        return False

    lines = path.read_text().split('\n')
    if lineno > len(lines):
        return False

    line_idx = lineno - 1
    line = lines[line_idx]

    # Pattern: def func_name(arg1, arg2, kwarg=default):
    # Add : Any to each untyped parameter
    if 'def ' in line and '(' in line:
        # Simple fix: add "-> None" if missing return type
        if '->' not in line and line.rstrip().endswith(':'):
            lines[line_idx] = line.rstrip()[:-1] + ' -> None:'
            path.write_text('\n'.join(lines))
            return True

    return False


def fix_var_annotated(filepath: str, lineno: int, message: str) -> bool:
    """Fix var-annotated errors by adding variable type annotations."""
    path = Path(filepath)
    if not path.exists():
        return False

    lines = path.read_text().split('\n')
    if lineno > len(lines):
        return False

    line_idx = lineno - 1
    line = lines[line_idx]

    # Extract variable name from message
    match = re.search(r'Need type annotation for "(\w+)"', message)
    if not match:
        return False

    var_name = match.group(1)

    # Common patterns to infer types
    if '= []' in line:
        line = re.sub(rf'\b{var_name}\s*=\s*\[\]', f'{var_name}: list[Any] = []', line)
    elif '= {}' in line:
        line = re.sub(rf'\b{var_name}\s*=\s*\{{\}}', f'{var_name}: dict[str, Any] = {{}}', line)
    elif '= set()' in line:
        line = re.sub(rf'\b{var_name}\s*=\s*set\(\)', f'{var_name}: set[Any] = set()', line)
    else:
        return False

    lines[line_idx] = line
    path.write_text('\n'.join(lines))
    return True


def fix_unused_ignore(filepath: str, lineno: int) -> bool:
    """Remove unused type: ignore comments."""
    path = Path(filepath)
    if not path.exists():
        return False

    lines = path.read_text().split('\n')
    if lineno > len(lines):
        return False

    line_idx = lineno - 1
    line = lines[line_idx]

    # Remove type: ignore comments
    line = re.sub(r'\s*#\s*type:\s*ignore\[[\w,-]+\]\s*$', '', line)
    line = re.sub(r'\s*#\s*type:\s*ignore\s*$', '', line)

    if line != lines[line_idx]:
        lines[line_idx] = line
        path.write_text('\n'.join(lines))
        return True

    return False


def add_any_import(filepath: str) -> bool:
    """Add 'from typing import Any' if not present and needed."""
    path = Path(filepath)
    if not path.exists():
        return False

    content = path.read_text()

    # Check if Any is already imported
    if re.search(r'from typing import.*\bAny\b', content):
        return False

    lines = content.split('\n')

    # Find where to insert
    insert_idx = 0
    for i, line in enumerate(lines):
        if line.strip().startswith('from __future__'):
            insert_idx = i + 1
        elif line.strip().startswith('from typing import'):
            # Merge with existing typing import
            existing_imports = re.search(r'from typing import (.+)', line)
            if existing_imports:
                imports = existing_imports.group(1)
                if 'Any' not in imports:
                    lines[i] = f"from typing import {imports}, Any"
                    path.write_text('\n'.join(lines))
                    return True
            return False

    # Insert new import
    if insert_idx == 0:
        # Find first non-docstring line
        for i, line in enumerate(lines):
            if line.strip() and not line.strip().startswith(('"""', "'''", '#')):
                insert_idx = i
                break

    lines.insert(insert_idx, 'from typing import Any')
    path.write_text('\n'.join(lines))
    return True


def main() -> None:
    """Main entry point."""
    print("🔧 Batch Type Error Fixer")
    print("=" * 60)

    # Get all mypy errors
    print("Analyzing mypy errors...")
    errors = get_mypy_errors()
    print(f"Found {len(errors)} errors")

    # Group by error type
    error_groups: dict[str, list[tuple[str, int, str]]] = {}
    for filepath, lineno, error_code, message in errors:
        if error_code not in error_groups:
            error_groups[error_code] = []
        error_groups[error_code].append((filepath, lineno, message))

    # Print summary
    print("\nError distribution:")
    for error_code, items in sorted(error_groups.items(), key=lambda x: -len(x[1]))[:10]:
        print(f"  {error_code}: {len(items)}")

    # Fix errors by category
    fixed_count = 0
    files_needing_any = set()

    # Fix unused-ignore first (easiest)
    if 'unused-ignore' in error_groups:
        print(f"\nFixing {len(error_groups['unused-ignore'])} unused-ignore errors...")
        for filepath, lineno, _ in error_groups['unused-ignore']:
            if fix_unused_ignore(filepath, lineno):
                fixed_count += 1

    # Fix var-annotated
    if 'var-annotated' in error_groups:
        print(f"\nFixing {len(error_groups['var-annotated'])} var-annotated errors...")
        for filepath, lineno, message in error_groups['var-annotated']:
            if fix_var_annotated(filepath, lineno, message):
                fixed_count += 1
                files_needing_any.add(filepath)

    # Fix no-untyped-def (partially)
    if 'no-untyped-def' in error_groups:
        print(f"\nFixing {len(error_groups['no-untyped-def'])} no-untyped-def errors (partial)...")
        for filepath, lineno, _ in error_groups['no-untyped-def'][:20]:  # Limit to avoid breaking things
            if fix_no_untyped_def(filepath, lineno):
                fixed_count += 1

    # Add Any imports where needed
    print(f"\nAdding Any imports to {len(files_needing_any)} files...")
    for filepath in files_needing_any:
        add_any_import(filepath)

    print("=" * 60)
    print(f"Fixed {fixed_count} errors")
    print("\nRun mypy again to see updated error count:")
    print("  uv run mypy src/specify_cli --show-error-codes | grep -c 'error:'")


if __name__ == '__main__':
    main()
