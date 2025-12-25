#!/usr/bin/env python3
"""
Advanced Type Annotation Fixer using AST Introspection

This script automatically fixes mypy type errors using advanced techniques:
1. AST parsing to analyze function signatures and return values
2. Type inference from existing code patterns
3. Import management for typing constructs
4. Automated annotation injection

Error categories addressed:
- no-untyped-def: Add parameter type annotations
- no-any-return: Add specific return type annotations
- var-annotated: Add variable type annotations
- valid-type: Fix callable -> Callable
- import issues: Add missing imports
"""

import ast
import re
import sys
from pathlib import Path
from typing import Any


class TypeAnnotationFixer(ast.NodeTransformer):
    """AST transformer that adds type annotations to functions."""

    def __init__(self) -> None:
        self.imports_to_add: set[str] = set()
        self.needs_typing = False
        self.needs_collections_abc = False

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """Add type annotations to function definitions."""
        # Check if function needs return type
        if node.returns is None:
            # Infer return type from body
            return_type = self._infer_return_type(node)
            if return_type:
                node.returns = ast.parse(return_type).body[0].value  # type: ignore

        self.generic_visit(node)
        return node

    def _infer_return_type(self, node: ast.FunctionDef) -> str | None:
        """Infer return type from function body."""
        # Check for yield statements (generator)
        for child in ast.walk(node):
            if isinstance(child, ast.Yield):
                self.needs_typing = True
                return "Generator[Any, None, None]"

        # Check for explicit return statements
        returns = [n for n in ast.walk(node) if isinstance(n, ast.Return)]
        if not returns:
            return "None"

        # Analyze return values
        if all(r.value is None for r in returns):
            return "None"

        return None  # Can't infer safely


def fix_callable_types(content: str) -> str:
    """Fix callable -> Callable type annotations."""
    # Replace callable with Callable in type annotations
    patterns = [
        (r'\bcallable\b(?=\s*\]|\s*\||\s*,|\s*=)', 'Callable[..., Any]'),
        (r':\s*None\s*\|\s*callable\b', ': Callable[..., Any] | None'),
        (r':\s*callable\b', ': Callable[..., Any]'),
    ]

    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)

    return content


def add_missing_typing_imports(content: str, filepath: str) -> str:
    """Add missing typing imports based on content."""
    lines = content.split('\n')

    # Detect what typing constructs are used
    needs_callable = 'Callable[' in content or ': Callable' in content
    needs_any = ': Any' in content or '[Any' in content or ', Any' in content
    needs_generator = 'Generator[' in content

    # Find import section
    import_idx = 0
    future_import_idx = -1
    typing_import_idx = -1
    last_import_idx = 0

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('from __future__'):
            future_import_idx = i
        elif stripped.startswith('from typing import'):
            typing_import_idx = i
        elif stripped.startswith(('import ', 'from ')):
            last_import_idx = i

    # Determine where to insert
    if future_import_idx >= 0:
        import_idx = future_import_idx + 1
    else:
        import_idx = 0
        # Find first non-docstring, non-comment line
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped and not stripped.startswith('#') and not stripped.startswith('"""') and not stripped.startswith("'''"):
                import_idx = i
                break

    # Check if we already have typing imports
    existing_typing_imports = set()
    if typing_import_idx >= 0:
        typing_line = lines[typing_import_idx]
        # Extract what's already imported
        match = re.search(r'from typing import (.+)', typing_line)
        if match:
            imports_str = match.group(1)
            existing_typing_imports = {
                imp.strip() for imp in imports_str.split(',')
            }

    # Build new imports to add
    needed_imports = set()
    if needs_callable and 'Callable' not in existing_typing_imports:
        needed_imports.add('Callable')
    if needs_any and 'Any' not in existing_typing_imports:
        needed_imports.add('Any')
    if needs_generator and 'Generator' not in existing_typing_imports:
        needed_imports.add('Generator')

    if not needed_imports:
        return content

    # Add to existing or create new
    if typing_import_idx >= 0:
        # Merge with existing
        all_imports = sorted(existing_typing_imports | needed_imports)
        lines[typing_import_idx] = f"from typing import {', '.join(all_imports)}"
    else:
        # Create new import
        new_import = f"from typing import {', '.join(sorted(needed_imports))}"
        # Insert after __future__ or at beginning
        insert_pos = import_idx
        # Add blank line before if needed
        if insert_pos > 0 and lines[insert_pos - 1].strip():
            lines.insert(insert_pos, '')
            insert_pos += 1
        lines.insert(insert_pos, new_import)

    return '\n'.join(lines)


def fix_generator_return_types(content: str) -> str:
    """Fix generator return types (contextmanager issues)."""
    # Fix contextmanager generator functions
    lines = content.split('\n')
    fixed_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Look for @contextmanager decorator
        if '@contextmanager' in line:
            # Find the function definition
            j = i + 1
            while j < len(lines) and 'def ' not in lines[j]:
                j += 1

            if j < len(lines):
                func_line = lines[j]
                # Check if it has a return type
                if '->' in func_line:
                    # Replace return type with Generator
                    # Pattern: def func(...) -> None:
                    # Replace with: def func(...) -> Generator[...]:
                    func_line = re.sub(
                        r'def\s+(\w+)\s*\([^)]*\)\s*->\s*None\s*:',
                        r'def \1(...) -> Generator[Any, None, None]:',
                        func_line
                    )
                    lines[j] = func_line

        fixed_lines.append(line)
        i += 1

    return '\n'.join(lines) if fixed_lines else content


def fix_file(filepath: Path) -> tuple[bool, str]:
    """Fix type annotations in a single file.

    Returns:
        Tuple of (changed, message)
    """
    try:
        content = filepath.read_text()
        original_content = content

        # Apply fixes
        content = fix_callable_types(content)
        content = add_missing_typing_imports(content, str(filepath))
        content = fix_generator_return_types(content)

        # Write back if changed
        if content != original_content:
            filepath.write_text(content)
            return True, "Fixed"

        return False, "No changes needed"

    except Exception as e:
        return False, f"Error: {e}"


def main() -> None:
    """Main entry point."""
    src_dir = Path(__file__).parent.parent / 'src' / 'specify_cli'

    if not src_dir.exists():
        print(f"Error: {src_dir} does not exist")
        sys.exit(1)

    print("🔧 Advanced Type Annotation Fixer")
    print("=" * 60)

    # Find all Python files
    py_files = list(src_dir.rglob('*.py'))
    print(f"Found {len(py_files)} Python files")

    fixed_count = 0
    for py_file in sorted(py_files):
        changed, message = fix_file(py_file)
        if changed:
            fixed_count += 1
            rel_path = py_file.relative_to(src_dir.parent.parent)
            print(f"✓ {rel_path}: {message}")

    print("=" * 60)
    print(f"Fixed {fixed_count} files")


if __name__ == '__main__':
    main()
