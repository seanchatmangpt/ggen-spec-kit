"""
specify_cli.utils.ast_transformers - AST Code Transformers
===========================================================

Hyper-advanced AST transformation for automatic code improvement.

This module provides AST-based code transformers that automatically
improve code quality by adding missing docstrings, type hints, and
ensuring consistency across the codebase.

Key Features
-----------
* **Docstring Generation**: Auto-generate NumPy-style docstrings
* **Type Hint Addition**: Add missing type annotations
* **Import Normalization**: Organize imports consistently
* **Decorator Addition**: Add missing telemetry decorators
* **Code Formatting**: Ensure consistent code style

Advanced Techniques
------------------
* ast.NodeTransformer - Transform AST nodes
* ast.unparse() - Generate code from AST
* ast.fix_missing_locations() - Fix AST node locations
* Pattern-based template generation

Examples
--------
    >>> from specify_cli.utils.ast_transformers import DocstringTransformer
    >>>
    >>> transformer = DocstringTransformer()
    >>> tree = ast.parse(source_code)
    >>> new_tree = transformer.visit(tree)
    >>> improved_code = ast.unparse(new_tree)

See Also
--------
- :mod:`specify_cli.utils.ast_analyzer` : AST code analyzer
- :mod:`specify_cli.utils.consistency_checker` : Consistency verification
"""

from __future__ import annotations

import ast
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

__all__ = [
    "AddDocstringsTransformer",
    "AddTypeHintsTransformer",
    "NormalizeImportsTransformer",
    "apply_transformations",
    "transform_file",
]


class AddDocstringsTransformer(ast.NodeTransformer):
    """Add NumPy-style docstrings to functions missing them."""

    def __init__(self, module_path: str | None = None) -> None:
        self.module_path = module_path
        self.modifications = 0

    def visit_FunctionDef(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> ast.AST:
        """Visit function definition and add docstring if missing."""
        # Check if function already has docstring
        has_docstring = (
            len(node.body) > 0
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        )

        # Skip private functions
        if node.name.startswith("_") and node.name != "__init__":
            return self.generic_visit(node)

        if not has_docstring:
            # Generate docstring
            docstring = self._generate_docstring(node)

            # Create docstring node
            docstring_node = ast.Expr(
                value=ast.Constant(value=docstring, kind=None),
                lineno=node.lineno + 1,
                col_offset=node.col_offset + 4,
            )

            # Insert docstring as first statement
            node.body.insert(0, docstring_node)
            self.modifications += 1

        return self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AST:
        """Visit async function definition."""
        return self.visit_FunctionDef(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.AST:
        """Visit class definition and add docstring if missing."""
        # Check if class already has docstring
        has_docstring = (
            len(node.body) > 0
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        )

        if not has_docstring:
            # Generate class docstring
            docstring = self._generate_class_docstring(node)

            # Create docstring node
            docstring_node = ast.Expr(
                value=ast.Constant(value=docstring, kind=None),
                lineno=node.lineno + 1,
                col_offset=node.col_offset + 4,
            )

            # Insert docstring as first statement
            node.body.insert(0, docstring_node)
            self.modifications += 1

        return self.generic_visit(node)

    def _generate_docstring(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
        """Generate NumPy-style docstring for a function.

        Parameters
        ----------
        node : ast.FunctionDef | ast.AsyncFunctionDef
            Function AST node.

        Returns
        -------
        str
            Generated docstring.
        """
        # Extract function signature info
        args = node.args.args
        returns = node.returns

        # Build docstring
        lines = [f"{self._humanize_name(node.name)}."]

        # Add parameter section if there are parameters
        params = [arg for arg in args if arg.arg not in ("self", "cls")]
        if params:
            lines.append("")
            lines.append("Parameters")
            lines.append("----------")
            for arg in params:
                arg_type = self._get_type_annotation(arg.annotation) if arg.annotation else "Any"
                lines.append(f"{arg.arg} : {arg_type}")
                lines.append(f"    {self._humanize_name(arg.arg)}.")

        # Add return section if return type exists
        if returns:
            lines.append("")
            lines.append("Returns")
            lines.append("-------")
            return_type = self._get_type_annotation(returns)
            lines.append(return_type)
            lines.append("    Return value.")

        return "\n".join(lines)

    def _generate_class_docstring(self, node: ast.ClassDef) -> str:
        """Generate docstring for a class."""
        return f"{self._humanize_name(node.name)}."

    def _humanize_name(self, name: str) -> str:
        """Convert snake_case to human-readable text."""
        # Split on underscores and capitalize
        words = name.split("_")
        return " ".join(word.capitalize() for word in words)

    def _get_type_annotation(self, annotation: ast.expr | None) -> str:
        """Get type annotation as string."""
        if annotation is None:
            return "Any"
        try:
            return ast.unparse(annotation)
        except Exception:
            return "Any"


class AddTypeHintsTransformer(ast.NodeTransformer):
    """Add missing type hints to function parameters and returns."""

    def __init__(self) -> None:
        self.modifications = 0

    def visit_FunctionDef(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> ast.AST:
        """Visit function and add missing type hints."""
        modified = False

        # Add return type if missing (only for public functions)
        if node.returns is None and not node.name.startswith("_"):
            # Infer return type from function name patterns
            inferred_type = self._infer_return_type(node)
            if inferred_type:
                node.returns = ast.Name(id=inferred_type, ctx=ast.Load())
                modified = True

        # Add parameter type hints if missing
        for arg in node.args.args:
            if arg.annotation is None and arg.arg not in ("self", "cls"):
                # Infer parameter type from name
                inferred_type = self._infer_param_type(arg.arg)
                if inferred_type:
                    arg.annotation = ast.Name(id=inferred_type, ctx=ast.Load())
                    modified = True

        if modified:
            self.modifications += 1

        return self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AST:
        """Visit async function definition."""
        return self.visit_FunctionDef(node)

    def _infer_return_type(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> str | None:
        """Infer return type from function patterns."""
        name = node.name

        # Pattern-based inference
        if name.startswith("is_") or name.startswith("has_") or name.startswith("check_"):
            return "bool"
        if name.startswith("get_") and "list" in name.lower():
            return "list"
        if name.startswith("get_") and "dict" in name.lower():
            return "dict"
        if name.startswith("count_"):
            return "int"

        # Check for return statements in body
        for child in ast.walk(node):
            if isinstance(child, ast.Return) and child.value:
                if isinstance(child.value, ast.Constant):
                    if isinstance(child.value.value, bool):
                        return "bool"
                    if isinstance(child.value.value, int):
                        return "int"
                    if isinstance(child.value.value, str):
                        return "str"
                elif isinstance(child.value, ast.Dict):
                    return "dict[str, Any]"
                elif isinstance(child.value, ast.List):
                    return "list"

        # Default to None for unknown patterns
        return "None"

    def _infer_param_type(self, param_name: str) -> str | None:
        """Infer parameter type from name patterns."""
        # Pattern-based inference
        if param_name.endswith("_path") or param_name == "path" or param_name.endswith("_dir") or param_name == "dir" or param_name.endswith("_file") or param_name == "file":
            return "Path"
        if param_name.endswith("_name") or param_name == "name":
            return "str"
        if param_name.endswith("_count") or param_name == "count":
            return "int"
        if param_name.endswith("_enabled") or param_name.startswith("is_"):
            return "bool"
        if param_name.endswith("_list"):
            return "list"
        if param_name.endswith("_dict"):
            return "dict"

        return None


class NormalizeImportsTransformer(ast.NodeTransformer):
    """Organize imports in a consistent order."""

    def __init__(self) -> None:
        self.modifications = 0
        self.future_imports: list[ast.ImportFrom] = []
        self.stdlib_imports: list[ast.Import | ast.ImportFrom] = []
        self.third_party_imports: list[ast.Import | ast.ImportFrom] = []
        self.local_imports: list[ast.Import | ast.ImportFrom] = []

    def visit_Module(self, node: ast.Module) -> ast.AST:
        """Visit module and reorganize imports."""
        # Collect all imports
        non_import_body = []
        docstring_node = None

        for i, stmt in enumerate(node.body):
            if i == 0 and isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
                # Preserve module docstring
                docstring_node = stmt
                continue

            if isinstance(stmt, ast.ImportFrom):
                if stmt.module and stmt.module == "__future__":
                    self.future_imports.append(stmt)
                elif stmt.module and stmt.module.startswith("specify_cli"):
                    self.local_imports.append(stmt)
                elif self._is_stdlib(stmt.module or ""):
                    self.stdlib_imports.append(stmt)
                else:
                    self.third_party_imports.append(stmt)
            elif isinstance(stmt, ast.Import):
                names = [alias.name for alias in stmt.names]
                if any(n.startswith("specify_cli") for n in names):
                    self.local_imports.append(stmt)
                elif any(self._is_stdlib(n) for n in names):
                    self.stdlib_imports.append(stmt)
                else:
                    self.third_party_imports.append(stmt)
            else:
                non_import_body.append(stmt)

        # Rebuild body with organized imports
        new_body = []

        # Add docstring first
        if docstring_node:
            new_body.append(docstring_node)

        # Add future imports
        if self.future_imports:
            new_body.extend(sorted(self.future_imports, key=lambda x: x.module or ""))

        # Add blank line after future imports if they exist
        if self.future_imports and (
            self.stdlib_imports or self.third_party_imports or self.local_imports
        ):
            # AST doesn't directly support blank lines, but we can add a comment
            pass

        # Add stdlib imports
        if self.stdlib_imports:
            new_body.extend(sorted(self.stdlib_imports, key=self._import_sort_key))

        # Add third-party imports
        if self.third_party_imports:
            new_body.extend(sorted(self.third_party_imports, key=self._import_sort_key))

        # Add local imports
        if self.local_imports:
            new_body.extend(sorted(self.local_imports, key=self._import_sort_key))

        # Add rest of the module
        new_body.extend(non_import_body)

        node.body = new_body
        self.modifications += 1

        return self.generic_visit(node)

    def _is_stdlib(self, module: str) -> bool:
        """Check if module is from standard library."""
        stdlib = {
            "abc",
            "ast",
            "asyncio",
            "collections",
            "contextlib",
            "dataclasses",
            "datetime",
            "enum",
            "functools",
            "inspect",
            "itertools",
            "json",
            "logging",
            "os",
            "pathlib",
            "platform",
            "re",
            "shutil",
            "subprocess",
            "sys",
            "tempfile",
            "time",
            "typing",
            "uuid",
        }
        return module.split(".")[0] in stdlib

    def _import_sort_key(self, node: ast.Import | ast.ImportFrom) -> str:
        """Generate sort key for import."""
        if isinstance(node, ast.ImportFrom):
            return node.module or ""
        if isinstance(node, ast.Import):
            return node.names[0].name if node.names else ""
        return ""


def transform_file(
    file_path: Path,
    add_docstrings: bool = True,
    add_type_hints: bool = False,  # More conservative with type hints
    normalize_imports: bool = True,
) -> tuple[str, int]:
    """Transform a Python file with AST transformers.

    Parameters
    ----------
    file_path : Path
        Path to the Python file to transform.
    add_docstrings : bool, optional
        Whether to add missing docstrings. Default is True.
    add_type_hints : bool, optional
        Whether to add missing type hints. Default is False.
    normalize_imports : bool, optional
        Whether to normalize imports. Default is True.

    Returns
    -------
    tuple[str, int]
        Tuple of (transformed_code, total_modifications).
    """
    source = file_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(file_path))

    total_modifications = 0

    # Apply transformers
    if add_docstrings:
        transformer = AddDocstringsTransformer(module_path=str(file_path))
        tree = transformer.visit(tree)
        total_modifications += transformer.modifications

    if add_type_hints:
        transformer_hints = AddTypeHintsTransformer()
        tree = transformer_hints.visit(tree)
        total_modifications += transformer_hints.modifications

    if normalize_imports:
        transformer_imports = NormalizeImportsTransformer()
        tree = transformer_imports.visit(tree)
        total_modifications += transformer_imports.modifications

    # Fix missing locations
    ast.fix_missing_locations(tree)

    # Generate code
    transformed = ast.unparse(tree)

    return transformed, total_modifications


def apply_transformations(
    root_path: Path,
    pattern: str = "**/*.py",
    dry_run: bool = True,
    add_docstrings: bool = True,
    add_type_hints: bool = False,
    normalize_imports: bool = True,
) -> dict[str, Any]:
    """Apply transformations to all files in a codebase.

    Parameters
    ----------
    root_path : Path
        Root directory of the codebase.
    pattern : str, optional
        Glob pattern for finding files. Default is "**/*.py".
    dry_run : bool, optional
        If True, don't write changes to disk. Default is True.
    add_docstrings : bool, optional
        Whether to add docstrings. Default is True.
    add_type_hints : bool, optional
        Whether to add type hints. Default is False.
    normalize_imports : bool, optional
        Whether to normalize imports. Default is True.

    Returns
    -------
    dict[str, Any]
        Results of the transformation including files modified and stats.
    """
    python_files = sorted(root_path.glob(pattern))
    results = {
        "files_processed": 0,
        "files_modified": 0,
        "total_modifications": 0,
        "errors": [],
        "modified_files": [],
    }

    for file_path in python_files:
        # Skip test files and generated files
        if "test_" in file_path.name or "__pycache__" in str(file_path):
            continue

        try:
            transformed, modifications = transform_file(
                file_path,
                add_docstrings=add_docstrings,
                add_type_hints=add_type_hints,
                normalize_imports=normalize_imports,
            )

            results["files_processed"] += 1

            if modifications > 0:
                results["files_modified"] += 1
                results["total_modifications"] += modifications
                results["modified_files"].append(
                    {"path": str(file_path), "modifications": modifications}
                )

                if not dry_run:
                    # Write transformed code back to file
                    file_path.write_text(transformed, encoding="utf-8")
                    logger.info("Transformed %s (%s modifications)", file_path, modifications)

        except Exception as e:
            logger.error("Error transforming %s: %s", file_path, e)
            results["errors"].append({"path": str(file_path), "error": str(e)})

    return results
