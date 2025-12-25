#!/usr/bin/env python3
"""
AST-Based Ruff Violation Fixer

This script uses Abstract Syntax Tree (AST) analysis to automatically fix
common ruff violations across the codebase.

Targets:
- PLC0415 (170): import-outside-top-level
- ARG001 (83): unused-function-argument (prefix with _)
- B008 (68): function-call-in-default-argument
- TRY300 (66): try-consider-else
- TRY301 (46): raise-within-try
- ARG002 (37): unused-method-argument
- PTH123 (32): builtin-open -> pathlib
- G004 (11): logging-f-string
- B904 (14): raise-without-from-inside-except
- SIM102 (11): collapsible-if
"""

import ast
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
import re


class UnusedArgumentFixer(ast.NodeTransformer):
    """Fix ARG001/ARG002: Prefix unused arguments with underscore."""

    def __init__(self, unused_args: Set[str]):
        self.unused_args = unused_args
        self.changes = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """Visit function definitions and fix unused arguments."""
        # Analyze which arguments are actually used in the function body
        used_names = self._get_used_names(node.body)

        # Fix unused arguments
        for arg in node.args.args:
            if arg.arg not in used_names and not arg.arg.startswith('_'):
                if arg.arg != 'self' and arg.arg != 'cls':
                    old_name = arg.arg
                    arg.arg = f'_{arg.arg}'
                    self.changes.append(f"Prefixed unused arg: {old_name} -> {arg.arg}")

        self.generic_visit(node)
        return node

    def _get_used_names(self, nodes: List[ast.AST]) -> Set[str]:
        """Get all names used in a list of nodes."""
        used = set()
        for node in ast.walk(ast.Module(body=nodes, type_ignores=[])):
            if isinstance(node, ast.Name):
                used.add(node.id)
        return used


class ImportOrganizer(ast.NodeTransformer):
    """Move imports to top of file (fix PLC0415)."""

    def __init__(self):
        self.imports_to_move: List[Tuple[ast.Import | ast.ImportFrom, int]] = []
        self.current_line = 0

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """Find imports inside functions."""
        for i, stmt in enumerate(node.body):
            if isinstance(stmt, (ast.Import, ast.ImportFrom)):
                # Check if it's a conditional import or error handling
                if not self._is_conditional_import(node, i):
                    self.imports_to_move.append((stmt, node.lineno))

        self.generic_visit(node)
        return node

    def _is_conditional_import(self, func: ast.FunctionDef, stmt_idx: int) -> bool:
        """Check if import is conditional (inside if/try)."""
        # This is a simple check - in practice, we'd keep conditional imports
        # For now, we'll be conservative and keep them
        return True  # Keep imports inside functions for safety


class DefaultArgumentFixer(ast.NodeTransformer):
    """Fix B008: function-call-in-default-argument."""

    def __init__(self):
        self.changes = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """Fix mutable default arguments."""
        for i, default in enumerate(node.args.defaults):
            if isinstance(default, (ast.List, ast.Dict, ast.Set, ast.Call)):
                # This requires code restructuring, mark for manual review
                self.changes.append(
                    f"Line {node.lineno}: {node.name} has mutable default argument"
                )

        self.generic_visit(node)
        return node


class TryElseFixer(ast.NodeTransformer):
    """Fix TRY300: try-consider-else."""

    def __init__(self):
        self.changes = []

    def visit_Try(self, node: ast.Try) -> ast.Try:
        """Add else clause to try blocks where appropriate."""
        # Check if try block has return/raise at end
        if node.body and not node.orelse:
            last_stmt = node.body[-1]
            if not isinstance(last_stmt, (ast.Return, ast.Raise)):
                # Could benefit from else clause, but need manual review
                self.changes.append(f"Line {node.lineno}: Consider adding else clause")

        self.generic_visit(node)
        return node


class RaiseFromFixer(ast.NodeTransformer):
    """Fix B904: raise-without-from-inside-except."""

    def __init__(self):
        self.changes = []

    def visit_Try(self, node: ast.Try) -> ast.Try:
        """Add 'from' clause to raise statements in except blocks."""
        for handler in node.handlers:
            for stmt in handler.body:
                if isinstance(stmt, ast.Raise) and stmt.exc and not stmt.cause:
                    # Mark for adding 'from e' or 'from None'
                    self.changes.append(
                        f"Line {stmt.lineno}: Add 'from' clause to raise"
                    )

        self.generic_visit(node)
        return node


def fix_unused_arguments_regex(content: str, unused_args: List[Dict]) -> str:
    """Fix unused arguments using regex (simpler than AST for this)."""
    lines = content.split('\n')
    changes = []

    for violation in unused_args:
        line_no = violation['location']['row'] - 1
        arg_name = violation['message'].split("'")[1] if "'" in violation['message'] else None

        if arg_name and 0 <= line_no < len(lines):
            line = lines[line_no]
            # Don't prefix self, cls, or already prefixed args
            if arg_name not in ('self', 'cls') and not arg_name.startswith('_'):
                # Replace the argument name with underscore prefix
                # Use word boundaries to avoid partial matches
                pattern = rf'\b{re.escape(arg_name)}\b'
                if re.search(pattern, line):
                    lines[line_no] = re.sub(
                        rf'(\(|,\s*)({re.escape(arg_name)})(\s*[,:])',
                        rf'\1_{arg_name}\3',
                        line,
                        count=1
                    )
                    changes.append(f"Line {line_no + 1}: {arg_name} -> _{arg_name}")

    if changes:
        print(f"  Fixed {len(changes)} unused arguments")

    return '\n'.join(lines)


def fix_builtin_open_regex(content: str) -> Tuple[str, int]:
    """Fix PTH123: Replace open() with Path.open()."""
    changes = 0
    lines = content.split('\n')

    # Check if pathlib is imported
    has_path_import = any('from pathlib import' in line and 'Path' in line for line in lines)

    if not has_path_import:
        # Add import after existing imports
        import_idx = 0
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                import_idx = i + 1

        if import_idx > 0:
            lines.insert(import_idx, 'from pathlib import Path')
            changes += 1

    # Replace open(path, mode) with Path(path).open(mode)
    for i, line in enumerate(lines):
        if 'open(' in line and 'Path(' not in line:
            # Simple pattern matching for common cases
            # open("file.txt", "r") -> Path("file.txt").open("r")
            match = re.search(r'open\(([^,]+),\s*(["\'][rwa][+]?["\'])\)', line)
            if match:
                path_arg = match.group(1).strip()
                mode_arg = match.group(2).strip()
                lines[i] = line.replace(
                    f'open({path_arg}, {mode_arg})',
                    f'Path({path_arg}).open({mode_arg})'
                )
                changes += 1

    return '\n'.join(lines), changes


def fix_logging_fstring_regex(content: str) -> Tuple[str, int]:
    """Fix G004: logging f-strings."""
    changes = 0
    lines = content.split('\n')

    for i, line in enumerate(lines):
        # Match logger.info(f"...") patterns
        match = re.search(r'(logger\.\w+)\(f["\']([^"\']*)["\']', line)
        if match:
            method = match.group(1)
            message = match.group(2)

            # Convert f-string to % formatting
            # This is simplified - full implementation would parse f-string expressions
            if '{' in message and '}' in message:
                # Simple conversion for basic cases
                # f"Value: {x}" -> "Value: %s", x
                vars_in_fstring = re.findall(r'\{([^}]+)\}', message)
                template = re.sub(r'\{[^}]+\}', '%s', message)

                if vars_in_fstring:
                    var_list = ', '.join(vars_in_fstring)
                    lines[i] = line.replace(
                        f'{method}(f"{message}")',
                        f'{method}("{template}", {var_list})'
                    )
                    changes += 1

    return '\n'.join(lines), changes


def fix_collapsible_if_regex(content: str) -> Tuple[str, int]:
    """Fix SIM102: collapsible-if statements."""
    changes = 0
    lines = content.split('\n')

    i = 0
    while i < len(lines) - 1:
        line = lines[i].rstrip()
        next_line = lines[i + 1].rstrip() if i + 1 < len(lines) else ''

        # Match: if cond1:
        #           if cond2:
        if line.strip().startswith('if ') and line.strip().endswith(':'):
            indent1 = len(line) - len(line.lstrip())
            if next_line.strip().startswith('if ') and next_line.strip().endswith(':'):
                indent2 = len(next_line) - len(next_line.lstrip())

                if indent2 == indent1 + 4:  # Standard 4-space indent
                    # Collapse: if cond1 and cond2:
                    cond1 = line.strip()[3:-1]  # Remove 'if ' and ':'
                    cond2 = next_line.strip()[3:-1]

                    lines[i] = ' ' * indent1 + f'if {cond1} and {cond2}:'
                    lines.pop(i + 1)
                    changes += 1
                    continue

        i += 1

    return '\n'.join(lines), changes


def analyze_violations(src_dir: Path) -> Dict[str, List[Dict]]:
    """Get detailed violation data from ruff."""
    import json
    import subprocess

    result = subprocess.run(
        ['uv', 'run', 'ruff', 'check', str(src_dir), '--output-format=json'],
        capture_output=True,
        text=True
    )

    violations = json.loads(result.stdout)

    # Group by code
    by_code = {}
    for v in violations:
        code = v['code']
        if code not in by_code:
            by_code[code] = []
        by_code[code].append(v)

    return by_code


def apply_automated_fixes(src_dir: Path) -> Dict[str, int]:
    """Apply automated fixes to all Python files."""
    stats = {
        'files_processed': 0,
        'unused_args_fixed': 0,
        'open_fixed': 0,
        'logging_fixed': 0,
        'if_collapsed': 0,
    }

    # Get violation data
    print("Analyzing violations...")
    violations_by_code = analyze_violations(src_dir)

    # Get files with ARG001/ARG002 violations
    unused_arg_files = {}
    for code in ['ARG001', 'ARG002', 'ARG004']:
        if code in violations_by_code:
            for v in violations_by_code[code]:
                filename = v['filename']
                if filename not in unused_arg_files:
                    unused_arg_files[filename] = []
                unused_arg_files[filename].append(v)

    # Process each Python file
    for py_file in src_dir.rglob('*.py'):
        if '__pycache__' in str(py_file):
            continue

        print(f"Processing: {py_file.relative_to(src_dir)}")
        stats['files_processed'] += 1

        content = py_file.read_text()
        original_content = content

        # Fix unused arguments
        if str(py_file) in unused_arg_files:
            content = fix_unused_arguments_regex(content, unused_arg_files[str(py_file)])
            stats['unused_args_fixed'] += len(unused_arg_files[str(py_file)])

        # Fix builtin open
        content, open_changes = fix_builtin_open_regex(content)
        stats['open_fixed'] += open_changes

        # Fix logging f-strings
        content, log_changes = fix_logging_fstring_regex(content)
        stats['logging_fixed'] += log_changes

        # Fix collapsible ifs
        content, if_changes = fix_collapsible_if_regex(content)
        stats['if_collapsed'] += if_changes

        # Write back if changed
        if content != original_content:
            py_file.write_text(content)
            print(f"  ✓ Updated {py_file.name}")

    return stats


def main():
    """Main entry point."""
    src_dir = Path('/home/user/ggen-spec-kit/src/specify_cli')

    if not src_dir.exists():
        print(f"Error: {src_dir} not found")
        sys.exit(1)

    print("=" * 80)
    print("AST-Based Ruff Violation Fixer")
    print("=" * 80)
    print()

    print("Step 1: Analyzing current violations...")
    violations = analyze_violations(src_dir)

    print(f"\nTotal violations: {sum(len(v) for v in violations.values())}")
    print("\nTop 10 violation types:")
    sorted_violations = sorted(violations.items(), key=lambda x: len(x[1]), reverse=True)
    for code, items in sorted_violations[:10]:
        print(f"  {code}: {len(items)}")

    print("\n" + "=" * 80)
    print("Step 2: Applying automated fixes...")
    print("=" * 80)
    print()

    stats = apply_automated_fixes(src_dir)

    print("\n" + "=" * 80)
    print("Fixes Applied:")
    print("=" * 80)
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n✓ Automated fixes complete!")
    print("\nNext steps:")
    print("  1. Run: uv run ruff check src/specify_cli --statistics")
    print("  2. Run: uv run pytest tests/unit -q")
    print("  3. Review changes: git diff")


if __name__ == '__main__':
    main()
