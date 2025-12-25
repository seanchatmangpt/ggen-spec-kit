#!/usr/bin/env python3
"""Comprehensive mypy strict mode error fixer."""

import re
from pathlib import Path


def fix_file_types(file_path: Path) -> bool:
    """Fix type errors in a single file."""
    content = file_path.read_text()
    original = content

    # Fix 1: Add Any import if using Any but not imported
    if ': Any' in content or '-> Any' in content or '[Any' in content:
        if 'from typing import' in content and 'Any' not in content[:content.find('import')]:
            # Add Any to existing typing import
            content = re.sub(
                r'from typing import ([^)]+?)(\n)',
                r'from typing import \1, Any\2',
                content,
                count=1
            )

    # Fix 2: Generic types without parameters
    content = re.sub(r'-> dict:', r'-> dict[str, Any]:', content)
    content = re.sub(r'-> tuple:', r'-> tuple[Any, ...]:', content)
    content = re.sub(r'-> list:', r'-> list[Any]:', content)
    content = re.sub(r': dict\)', r': dict[str, Any])', content)
    content = re.sub(r': dict,', r': dict[str, Any],', content)
    content = re.sub(r': tuple\)', r': tuple[Any, ...],', content)
    content = re.sub(r': list\)', r': list[Any])', content)

    # Fix 3: Function parameter without type
    content = re.sub(r'\(([a-z_]+),\s+([a-z_]+):', r'(\1: Any, \2:', content)

    # Fix 4: list[Any](...) -> list(...)
    content = re.sub(r'list\[Any\]\(', r'list(', content)

    # Fix 5: Cast returns that mypy complains about
    content = re.sub(
        r'return sum\(factors\) / len\(factors\)',
        r'return float(sum(factors) / len(factors))',
        content
    )
    content = re.sub(
        r'return min\(([^,]+),\s*([^)]+)\)\s*$',
        r'return float(min(\1, \2))',
        content,
        flags=re.MULTILINE
    )
    content = re.sub(
        r'return ([a-z_]+)\s*/\s*([a-z_]+)',
        r'return float(\1 / \2)',
        content
    )

    # Fix 6: Add type annotations for structure variables
    content = re.sub(
        r'(\s+)structure = \{',
        r'\1structure: dict[str, Any] = {',
        content
    )
    content = re.sub(
        r'(\s+)validation = \{',
        r'\1validation: dict[str, Any] = {',
        content
    )

    # Fix 7: dict[str, Any]() constructors
    content = re.sub(r'dict\[str, Any\]\(', r'dict(', content)

    if content != original:
        file_path.write_text(content)
        return True
    return False


def main() -> None:
    """Fix all type errors."""
    src_dir = Path('/home/user/ggen-spec-kit/src/specify_cli')

    # Files with known errors
    files_to_fix = [
        '__init__.py',
        'ops/process_mining.py',
        'hyperdimensional/prioritization.py',
        'hyperdimensional/ast_nodes.py',
    ]

    fixed_count = 0
    for file_rel in files_to_fix:
        file_path = src_dir / file_rel
        if file_path.exists():
            if fix_file_types(file_path):
                print(f"Fixed: {file_path}")
                fixed_count += 1

    print(f"\nFixed {fixed_count} files")


if __name__ == '__main__':
    main()
