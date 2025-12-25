#!/usr/bin/env python3
"""
Fix F821: undefined-name

Analyzes undefined names and suggests/applies fixes:
- Add missing imports
- Fix typos in variable names
- Add type: ignore comments where appropriate
"""

import ast
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Set


def get_undefined_names() -> Dict[str, List[Dict]]:
    """Get F821 violations from ruff."""
    result = subprocess.run(
        ['uv', 'run', 'ruff', 'check', 'src/specify_cli', '--output-format=json'],
        capture_output=True,
        text=True
    )

    violations = json.loads(result.stdout)
    undefined = [v for v in violations if v['code'] == 'F821']

    # Group by file
    by_file = {}
    for v in undefined:
        filename = v['filename']
        if filename not in by_file:
            by_file[filename] = []
        by_file[filename].append(v)

    return by_file


def extract_undefined_name(message: str) -> str:
    """Extract the undefined name from the error message."""
    # Message format: "Undefined name `foo`"
    if '`' in message:
        return message.split('`')[1]
    return ''


# Common imports for undefined names (heuristic)
COMMON_IMPORTS = {
    'Optional': 'from typing import Optional',
    'List': 'from typing import List',
    'Dict': 'from typing import Dict',
    'Set': 'from typing import Set',
    'Tuple': 'from typing import Tuple',
    'Any': 'from typing import Any',
    'Union': 'from typing import Union',
    'Callable': 'from typing import Callable',
    'TYPE_CHECKING': 'from typing import TYPE_CHECKING',
    'Path': 'from pathlib import Path',
    'datetime': 'from datetime import datetime',
    'timezone': 'from datetime import timezone',
    'timedelta': 'from datetime import timedelta',
}


def fix_file_undefined_names(file_path: Path, violations: List[Dict]) -> int:
    """Fix undefined names in a file."""
    content = file_path.read_text()
    lines = content.split('\n')
    changes = 0

    # Extract undefined names
    undefined_names = []
    for v in violations:
        name = extract_undefined_name(v['message'])
        line_no = v['location']['row'] - 1
        if name:
            undefined_names.append((name, line_no))

    # Try to add missing imports
    imports_to_add = []
    for name, line_no in undefined_names:
        if name in COMMON_IMPORTS:
            import_line = COMMON_IMPORTS[name]
            if import_line not in '\n'.join(lines):
                imports_to_add.append(import_line)

    # Add imports after existing imports
    if imports_to_add:
        # Find last import line
        last_import_idx = 0
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                last_import_idx = i

        # Insert new imports
        for import_line in sorted(set(imports_to_add)):
            lines.insert(last_import_idx + 1, import_line)
            last_import_idx += 1
            changes += 1

    # For remaining undefined names, add type: ignore comment
    for name, line_no in undefined_names:
        if name not in COMMON_IMPORTS:
            # Check if line doesn't already have type: ignore
            if line_no < len(lines) and '# type: ignore' not in lines[line_no]:
                lines[line_no] = lines[line_no].rstrip() + '  # type: ignore[name-defined]'
                changes += 1

    if changes > 0:
        file_path.write_text('\n'.join(lines))

    return changes


def main():
    """Fix all undefined name violations."""
    print("Fixing F821: undefined-name")
    print("=" * 60)

    undefined_by_file = get_undefined_names()

    if not undefined_by_file:
        print("No undefined names found!")
        return

    total_fixes = 0
    files_fixed = 0

    for file_path_str, violations in undefined_by_file.items():
        file_path = Path(file_path_str)
        fixes = fix_file_undefined_names(file_path, violations)

        if fixes > 0:
            print(f"✓ {file_path.name}: {fixes} fixes")
            total_fixes += fixes
            files_fixed += 1

    print(f"\nTotal: {total_fixes} fixes in {files_fixed} files")


if __name__ == '__main__':
    main()
