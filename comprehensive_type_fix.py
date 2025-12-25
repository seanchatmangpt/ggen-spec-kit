#!/usr/bin/env python3
"""Comprehensive type error fixes for mypy strict mode compliance."""

import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple


def add_float_casts(content: str) -> Tuple[str, int]:
    """Add float() casts to fix no-any-return errors."""
    fixes = 0
    patterns = [
        (r'return sum\(([^)]+)\) / len\(([^)]+)\)', r'return float(sum(\1)) / len(\2)'),
        (r'return min\(([^,]+), ([\d.]+)\)([^)]*)$', r'return float(min(\1, \2))\3', re.MULTILINE),
        (r'return ([a-z_]+) \* ([a-z_]+) \* \(([^)]+)\)', r'return float(\1 * \2 * (\3))'),
        (r'return ([a-z_]+) \* ([a-z_]+)$', r'return float(\1 * \2)', re.MULTILINE),
    ]

    for pattern, replacement, *flags in patterns:
        flag = flags[0] if flags else 0
        new_content = re.sub(pattern, replacement, content, flags=flag)
        if new_content != content:
            fixes += content.count(pattern) - new_content.count(pattern) + 1
            content = new_content

    return content, fixes


def add_str_casts(content: str) -> Tuple[str, int]:
    """Add str() casts where needed."""
    fixes = 0
    patterns = [
        (r'return self\.parameters\.get\("metric", "([^"]+)"\)', r'return str(self.parameters.get("metric", "\1"))'),
    ]

    for pattern, replacement in patterns:
        new_content = re.sub(pattern, replacement, content)
        if new_content != content:
            fixes += 1
            content = new_content

    return content, fixes


def add_type_ignores_for_stubs(content: str) -> Tuple[str, int]:
    """Add type: ignore comments for missing library stubs."""
    fixes = 0
    patterns = [
        (r'(\s+import pandas as pd)$', r'\1  # type: ignore[import-untyped]', re.MULTILINE),
    ]

    for pattern, replacement, *flags in patterns:
        flag = flags[0] if flags else 0
        new_content = re.sub(pattern, replacement, content, flags=flag)
        if new_content != content:
            fixes += 1
            content = new_content

    return content, fixes


def fix_generic_types(content: str) -> Tuple[str, int]:
    """Fix generic types without parameters."""
    fixes = 0
    patterns = [
        (r'-> dict:', r'-> Dict[str, Any]:'),
        (r'-> tuple:', r'-> Tuple[Any, ...]:'),
        (r'-> list:', r'-> List[Any]:'),
        (r': dict\)', r': Dict[str, Any])'),
        (r': tuple\)', r': Tuple[Any, ...]'),
        (r': list\)', r': List[Any])'),
    ]

    for pattern, replacement in patterns:
        new_content = re.sub(pattern, replacement, content)
        if new_content != content:
            fixes += content.count(pattern.replace('\\', ''))
            content = new_content

    return content, fixes


def add_missing_return_types(content: str) -> Tuple[str, int]:
    """Add -> None to functions without return types."""
    fixes = 0

    # Find functions without return type
    pattern = r'(\n\s*def\s+\w+\([^)]*\)\s*):'
    matches = list(re.finditer(pattern, content))

    for match in reversed(matches):  # Process in reverse to maintain positions
        before_colon = content[match.start():match.end()]
        if '->' not in before_colon:
            # Simple heuristic: if function doesn't return or only returns None
            func_start = match.end()
            # Find next function or class definition
            next_def_match = re.search(r'\n(def |class )', content[func_start:])
            if next_def_match:
                func_end = func_start + next_def_match.start()
            else:
                func_end = len(content)

            func_body = content[func_start:func_end]

            # If no return statement or only "return" or "return None"
            returns = re.findall(r'\n\s+return\s*([^\n]*)', func_body)
            if not returns or all(not r.strip() or r.strip() == 'None' for r in returns):
                # Add -> None
                content = content[:match.end()-1] + ' -> None' + content[match.end()-1:]
                fixes += 1

    return content, fixes


def ensure_typing_imports(content: str) -> Tuple[str, int]:
    """Ensure necessary typing imports exist."""
    fixes = 0
    needs = []

    if 'Dict[' in content and 'from typing import' in content and 'Dict' not in content.split('from typing import')[1].split('\n')[0]:
        needs.append('Dict')
    if 'List[' in content and 'from typing import' in content and 'List' not in content.split('from typing import')[1].split('\n')[0]:
        needs.append('List')
    if 'Tuple[' in content and 'from typing import' in content and 'Tuple' not in content.split('from typing import')[1].split('\n')[0]:
        needs.append('Tuple')
    if ': Any' in content or '-> Any' in content or '[Any' in content:
        if 'from typing import' in content and 'Any' not in content.split('from typing import')[1].split('\n')[0]:
            needs.append('Any')

    if needs and 'from typing import' in content:
        # Add to existing import
        pattern = r'from typing import ([^\n]+)'
        match = re.search(pattern, content)
        if match:
            existing_imports = match.group(1)
            new_imports = existing_imports + ', ' + ', '.join(needs)
            content = re.sub(pattern, f'from typing import {new_imports}', content, count=1)
            fixes += len(needs)

    return content, fixes


def fix_file(file_path: Path) -> Dict[str, int]:
    """Fix all type errors in a file."""
    if not file_path.exists():
        return {}

    content = file_path.read_text()
    original_content = content
    stats = {}

    # Apply fixes
    content, stats['float_casts'] = add_float_casts(content)
    content, stats['str_casts'] = add_str_casts(content)
    content, stats['type_ignores'] = add_type_ignores_for_stubs(content)
    content, stats['generic_types'] = fix_generic_types(content)
    content, stats['return_types'] = add_missing_return_types(content)
    content, stats['typing_imports'] = ensure_typing_imports(content)

    if content != original_content:
        file_path.write_text(content)
        return stats
    return {}


def main() -> None:
    """Fix type errors in all files."""
    src_dir = Path('/home/user/ggen-spec-kit/src/specify_cli')

    # Get all Python files
    py_files = list(src_dir.rglob('*.py'))

    total_stats: Dict[str, int] = {}
    fixed_files = 0

    for py_file in py_files:
        stats = fix_file(py_file)
        if stats:
            fixed_files += 1
            print(f"Fixed {py_file.name}:")
            for category, count in stats.items():
                if count > 0:
                    print(f"  {category}: {count}")
                    total_stats[category] = total_stats.get(category, 0) + count

    print(f"\n=== Summary ===")
    print(f"Files modified: {fixed_files}")
    print(f"Total fixes:")
    for category, count in sorted(total_stats.items()):
        print(f"  {category}: {count}")

    # Run mypy to see remaining errors
    print("\n=== Running mypy to check remaining errors ===")
    result = subprocess.run(
        ['uv', 'run', 'mypy', 'src/specify_cli/', '--strict'],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        # Count errors
        errors = result.stderr.count('error:')
        files_with_errors = len(set(re.findall(r'src/[^:]+\.py', result.stderr)))
        print(f"Remaining errors: {errors}")
        print(f"Files with errors: {files_with_errors}")
        # Show first 20 errors
        lines = result.stderr.split('\n')
        error_lines = [l for l in lines if 'error:' in l][:20]
        print("\nFirst 20 errors:")
        for line in error_lines:
            print(line)
    else:
        print("✓ All type errors fixed!")


if __name__ == '__main__':
    main()
