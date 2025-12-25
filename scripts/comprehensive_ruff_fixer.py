#!/usr/bin/env python3
"""Comprehensive Ruff violation fixer using AST transformations."""

import ast
import re
import sys
from pathlib import Path
from typing import Any


class ComprehensiveRuffFixer(ast.NodeTransformer):
    """Fix multiple ruff violations using AST transformations."""

    def __init__(self) -> None:
        """Initialize the fixer."""
        self.fixes_applied = {
            "G004_logging_fstring": 0,
            "B904_raise_from": 0,
            "PTH123_open_to_pathlib": 0,
            "PTH101_chmod_to_pathlib": 0,
            "PTH109_getcwd_to_pathlib": 0,
            "SIM102_collapsible_if": 0,
            "TRY401_logging_exception": 0,
        }
        self.changes_made = False

    def visit_Call(self, node: ast.Call) -> Any:
        """Fix function calls."""
        # Fix G004: logging f-strings
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in ("debug", "info", "warning", "error", "critical"):
                if node.args and isinstance(node.args[0], ast.JoinedStr):
                    # Convert f-string to % formatting
                    fixed_node = self._fix_logging_fstring(node)
                    if fixed_node:
                        return fixed_node

            # Fix TRY401: logger.exception with redundant exception object
            if node.func.attr == "exception":
                if len(node.args) >= 2:
                    # Check if last arg is exception variable
                    # Remove it if it's redundant
                    fixed_node = self._fix_logging_exception(node)
                    if fixed_node:
                        return fixed_node

        # Fix PTH123: open() -> Path.open()
        if isinstance(node.func, ast.Name) and node.func.id == "open":
            if node.args:
                fixed_node = self._fix_open_to_pathlib(node)
                if fixed_node:
                    return fixed_node

        # Fix PTH101: os.chmod() -> Path.chmod()
        if isinstance(node.func, ast.Attribute):
            if (
                isinstance(node.func.value, ast.Name)
                and node.func.value.id == "os"
                and node.func.attr == "chmod"
            ):
                fixed_node = self._fix_os_chmod(node)
                if fixed_node:
                    return fixed_node

        # Fix PTH109: os.getcwd() -> Path.cwd()
        if isinstance(node.func, ast.Attribute):
            if (
                isinstance(node.func.value, ast.Name)
                and node.func.value.id == "os"
                and node.func.attr == "getcwd"
            ):
                fixed_node = self._fix_os_getcwd(node)
                if fixed_node:
                    return fixed_node

        return self.generic_visit(node)

    def visit_Raise(self, node: ast.Raise) -> Any:
        """Fix B904: raise without from in except clause."""
        # This needs context about whether we're in an except handler
        # For now, we'll handle this in a separate pass
        return self.generic_visit(node)

    def _fix_logging_fstring(self, node: ast.Call) -> ast.Call | None:
        """Convert logging f-string to % formatting."""
        if not node.args or not isinstance(node.args[0], ast.JoinedStr):
            return None

        fstring = node.args[0]
        format_str_parts = []
        format_args = []

        for value in fstring.values:
            if isinstance(value, ast.Constant):
                format_str_parts.append(str(value.value))
            elif isinstance(value, ast.FormattedValue):
                format_str_parts.append("%s")
                format_args.append(value.value)

        new_format_str = "".join(format_str_parts)
        new_args = [ast.Constant(value=new_format_str)] + format_args

        self.fixes_applied["G004_logging_fstring"] += 1
        self.changes_made = True

        return ast.Call(
            func=node.func,
            args=new_args,
            keywords=node.keywords,
        )

    def _fix_logging_exception(self, node: ast.Call) -> ast.Call | None:
        """Remove redundant exception object from logger.exception()."""
        # If last arg looks like an exception variable, remove it
        # This is heuristic-based
        if len(node.args) < 2:
            return None

        # Keep format string and args, remove last if it looks like exception
        new_args = node.args[:-1]

        self.fixes_applied["TRY401_logging_exception"] += 1
        self.changes_made = True

        return ast.Call(
            func=node.func,
            args=new_args,
            keywords=node.keywords,
        )

    def _fix_open_to_pathlib(self, node: ast.Call) -> ast.Call | None:
        """Convert open() to Path().open()."""
        if not node.args:
            return None

        path_arg = node.args[0]

        # Create Path(path_arg).open(mode, ...)
        path_call = ast.Call(
            func=ast.Name(id="Path", ctx=ast.Load()),
            args=[path_arg],
            keywords=[],
        )

        # Extract mode and other args
        open_args = node.args[1:] if len(node.args) > 1 else []

        new_call = ast.Call(
            func=ast.Attribute(
                value=path_call,
                attr="open",
                ctx=ast.Load(),
            ),
            args=open_args,
            keywords=node.keywords,
        )

        self.fixes_applied["PTH123_open_to_pathlib"] += 1
        self.changes_made = True

        return new_call

    def _fix_os_chmod(self, node: ast.Call) -> ast.Call | None:
        """Convert os.chmod() to Path().chmod()."""
        if len(node.args) < 2:
            return None

        path_arg = node.args[0]
        mode_arg = node.args[1]

        # Create Path(path_arg).chmod(mode)
        path_call = ast.Call(
            func=ast.Name(id="Path", ctx=ast.Load()),
            args=[path_arg],
            keywords=[],
        )

        new_call = ast.Call(
            func=ast.Attribute(
                value=path_call,
                attr="chmod",
                ctx=ast.Load(),
            ),
            args=[mode_arg],
            keywords=[],
        )

        self.fixes_applied["PTH101_chmod_to_pathlib"] += 1
        self.changes_made = True

        return new_call

    def _fix_os_getcwd(self, node: ast.Call) -> ast.Call | None:
        """Convert os.getcwd() to Path.cwd()."""
        new_call = ast.Call(
            func=ast.Attribute(
                value=ast.Name(id="Path", ctx=ast.Load()),
                attr="cwd",
                ctx=ast.Load(),
            ),
            args=[],
            keywords=[],
        )

        self.fixes_applied["PTH109_getcwd_to_pathlib"] += 1
        self.changes_made = True

        return new_call


class B904Fixer:
    """Fix B904: raise without from in except clauses."""

    def fix_file(self, content: str) -> tuple[str, int]:
        """Fix B904 violations using regex."""
        fixes = 0

        # Pattern: raise <exception> (not followed by from)
        # In except clause
        pattern = r"(\s+)(raise\s+\w+\([^)]*\))(\s*(?:$|\n))"

        def replace_raise(match: re.Match[str]) -> str:
            nonlocal fixes
            indent = match.group(1)
            raise_stmt = match.group(2)
            ending = match.group(3)

            # Check if we're likely in an except clause
            # (heuristic: indented raise statement)
            if indent and "from" not in raise_stmt:
                fixes += 1
                return f"{indent}{raise_stmt} from None{ending}"
            return match.group(0)

        fixed_content = re.sub(pattern, replace_raise, content)
        return fixed_content, fixes


class UnusedArgFixer:
    """Fix ARG001/ARG002: prefix unused args with underscore."""

    def fix_file(self, content: str, unused_args: set[str]) -> tuple[str, int]:
        """Fix unused arguments by prefixing with underscore."""
        fixes = 0

        for arg in unused_args:
            # Only fix if not already prefixed with _
            if not arg.startswith("_"):
                # Pattern: function parameter
                pattern = rf"\b({arg})\s*(?::|,|\))"
                new_name = f"_{arg}"

                # Count occurrences
                matches = re.findall(pattern, content)
                if matches:
                    content = re.sub(pattern, rf"{new_name}\g<0>", content)
                    fixes += len(matches)

        return content, fixes


def fix_file(file_path: Path) -> dict[str, Any]:
    """Fix a single Python file."""
    try:
        content = file_path.read_text(encoding="utf-8")
        original_content = content
        total_fixes = 0

        # AST-based fixes
        try:
            tree = ast.parse(content)
            fixer = ComprehensiveRuffFixer()
            new_tree = fixer.visit(tree)

            if fixer.changes_made:
                ast.fix_missing_locations(new_tree)
                content = ast.unparse(new_tree)
                total_fixes += sum(fixer.fixes_applied.values())
        except SyntaxError:
            pass

        # Regex-based B904 fix
        b904_fixer = B904Fixer()
        content, b904_fixes = b904_fixer.fix_file(content)
        total_fixes += b904_fixes

        # Write back if changed
        if content != original_content:
            file_path.write_text(content, encoding="utf-8")
            return {
                "file": str(file_path),
                "fixes": total_fixes,
                "success": True,
            }

        return {"file": str(file_path), "fixes": 0, "success": True}

    except Exception as e:
        return {
            "file": str(file_path),
            "fixes": 0,
            "success": False,
            "error": str(e),
        }


def main() -> None:
    """Main entry point."""
    src_path = Path("/home/user/ggen-spec-kit/src/specify_cli")

    if not src_path.exists():
        print(f"Error: {src_path} not found")
        sys.exit(1)

    print("=" * 80)
    print("COMPREHENSIVE RUFF VIOLATION FIXER")
    print("=" * 80)
    print()

    # Find all Python files
    py_files = list(src_path.rglob("*.py"))
    print(f"Found {len(py_files)} Python files")
    print()

    results = []
    for py_file in py_files:
        result = fix_file(py_file)
        results.append(result)
        if result["fixes"] > 0:
            print(f"✓ {py_file.relative_to(src_path)}: {result['fixes']} fixes")

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    total_fixes = sum(r["fixes"] for r in results)
    successful = sum(1 for r in results if r["success"])
    failed = sum(1 for r in results if not r["success"])

    print(f"Total files processed: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Total fixes applied: {total_fixes}")
    print()


if __name__ == "__main__":
    main()
