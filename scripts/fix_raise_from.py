#!/usr/bin/env python3
"""
Fix B904: raise-without-from-inside-except

Automatically adds 'from e' or 'from None' to raise statements in except blocks.
"""

import ast
import sys
from pathlib import Path
from typing import List, Tuple


class RaiseFromFixer(ast.NodeTransformer):
    """Add 'from' clause to raise statements in except handlers."""

    def __init__(self):
        self.fixes: List[Tuple[int, str]] = []
        self.in_except_handler = False
        self.current_exception_name = None

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> ast.ExceptHandler:
        """Visit except handlers and track exception name."""
        old_in_except = self.in_except_handler
        old_exc_name = self.current_exception_name

        self.in_except_handler = True
        self.current_exception_name = node.name

        self.generic_visit(node)

        self.in_except_handler = old_in_except
        self.current_exception_name = old_exc_name

        return node

    def visit_Raise(self, node: ast.Raise) -> ast.Raise:
        """Fix raise statements without 'from' in except handlers."""
        if self.in_except_handler and node.exc and not node.cause:
            # Add 'from' clause
            if self.current_exception_name:
                # Use the caught exception: raise NewError(...) from e
                node.cause = ast.Name(id=self.current_exception_name, ctx=ast.Load())
            else:
                # Use 'from None' to suppress context
                node.cause = ast.Constant(value=None)

            self.fixes.append((node.lineno, f"Added 'from' clause"))

        return node


def fix_file_regex(file_path: Path) -> int:
    """Fix raise-without-from using regex (simpler for this case)."""
    content = file_path.read_text()
    lines = content.split('\n')
    changes = 0

    in_except = False
    except_indent = 0
    exception_var = None

    for i, line in enumerate(lines):
        stripped = line.lstrip()
        indent = len(line) - len(stripped)

        # Track except blocks
        if stripped.startswith('except ') and ' as ' in stripped:
            in_except = True
            except_indent = indent
            # Extract exception variable name
            parts = stripped.split(' as ')
            if len(parts) > 1:
                exception_var = parts[1].rstrip(':').strip()

        elif stripped.startswith('except'):
            in_except = True
            except_indent = indent
            exception_var = None

        # End of except block (dedent or new except/finally)
        elif in_except and (
            indent <= except_indent
            and stripped
            and not stripped.startswith(('#', '"', "'"))
        ):
            if not stripped.startswith('raise'):
                in_except = False
                exception_var = None

        # Fix raise statements in except blocks
        if in_except and stripped.startswith('raise ') and ' from ' not in line:
            # Don't fix bare 'raise'
            if stripped != 'raise':
                if exception_var:
                    lines[i] = line.replace('raise ', f'raise ', 1)
                    # Add ' from {exception_var}' before any comments
                    if '#' in lines[i]:
                        comment_pos = lines[i].index('#')
                        lines[i] = (
                            lines[i][:comment_pos].rstrip()
                            + f' from {exception_var}  '
                            + lines[i][comment_pos:]
                        )
                    else:
                        lines[i] = lines[i].rstrip() + f' from {exception_var}'
                else:
                    # Add 'from None' to suppress chaining
                    if '#' in lines[i]:
                        comment_pos = lines[i].index('#')
                        lines[i] = (
                            lines[i][:comment_pos].rstrip()
                            + ' from None  '
                            + lines[i][comment_pos:]
                        )
                    else:
                        lines[i] = lines[i].rstrip() + ' from None'

                changes += 1

    if changes > 0:
        file_path.write_text('\n'.join(lines))

    return changes


def main():
    """Fix all raise-without-from violations."""
    src_dir = Path('/home/user/ggen-spec-kit/src/specify_cli')

    print("Fixing B904: raise-without-from-inside-except")
    print("=" * 60)

    total_fixes = 0
    files_fixed = 0

    for py_file in src_dir.rglob('*.py'):
        if '__pycache__' in str(py_file):
            continue

        fixes = fix_file_regex(py_file)
        if fixes > 0:
            print(f"✓ {py_file.relative_to(src_dir)}: {fixes} fixes")
            total_fixes += fixes
            files_fixed += 1

    print(f"\nTotal: {total_fixes} fixes in {files_fixed} files")


if __name__ == '__main__':
    main()
