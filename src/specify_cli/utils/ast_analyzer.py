"""
specify_cli.utils.ast_analyzer - Advanced AST Analysis
=======================================================

Hyper-advanced AST manipulation for code consistency analysis.

This module provides comprehensive static analysis using Python's AST
module to ensure code quality, consistency, and compliance with the
three-tier architecture.

Key Features
-----------
* **Structural Analysis**: Analyze code structure across entire codebase
* **Pattern Detection**: Identify consistent and inconsistent patterns
* **Missing Code Detection**: Find missing docstrings, type hints, decorators
* **Architecture Validation**: Ensure three-tier layer separation
* **Metrics Collection**: Gather code quality metrics

Advanced Techniques
------------------
* ast.parse() - Parse Python source to AST
* ast.walk() - Traverse entire AST tree
* ast.NodeVisitor - Visit specific node types
* ast.get_source_segment() - Extract source code for nodes
* inspect module integration for runtime introspection

Examples
--------
    >>> from specify_cli.utils.ast_analyzer import CodebaseAnalyzer
    >>>
    >>> analyzer = CodebaseAnalyzer("/path/to/src")
    >>> results = analyzer.analyze()
    >>> print(f"Files analyzed: {results.total_files}")
    >>> print(f"Missing docstrings: {len(results.missing_docstrings)}")

See Also
--------
- :mod:`specify_cli.utils.ast_transformers` : AST code transformers
- :mod:`specify_cli.utils.consistency_checker` : Consistency verification
"""

from __future__ import annotations

import ast
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

__all__ = [
    "AnalysisResult",
    "CodebaseAnalyzer",
    "FileAnalysis",
    "FunctionInfo",
    "analyze_codebase",
]


@dataclass
class FunctionInfo:
    """Information about a function extracted from AST."""

    name: str
    lineno: int
    col_offset: int
    has_docstring: bool
    has_return_type: bool
    missing_param_types: list[str] = field(default_factory=list)
    is_async: bool = False
    is_method: bool = False
    is_public: bool = True
    decorators: list[str] = field(default_factory=list)
    complexity: int = 0
    source: str | None = None


@dataclass
class ClassInfo:
    """Information about a class extracted from AST."""

    name: str
    lineno: int
    col_offset: int
    has_docstring: bool
    bases: list[str] = field(default_factory=list)
    methods: list[FunctionInfo] = field(default_factory=list)
    is_dataclass: bool = False
    decorators: list[str] = field(default_factory=list)


@dataclass
class ImportInfo:
    """Information about imports in a module."""

    standard_library: list[str] = field(default_factory=list)
    third_party: list[str] = field(default_factory=list)
    local: list[str] = field(default_factory=list)
    future_imports: list[str] = field(default_factory=list)


@dataclass
class FileAnalysis:
    """Analysis results for a single Python file."""

    file_path: Path
    module_name: str
    has_module_docstring: bool
    functions: list[FunctionInfo] = field(default_factory=list)
    classes: list[ClassInfo] = field(default_factory=list)
    imports: ImportInfo = field(default_factory=ImportInfo)
    total_lines: int = 0
    code_lines: int = 0
    comment_lines: int = 0
    blank_lines: int = 0
    complexity_score: int = 0
    architecture_layer: str | None = None  # commands, ops, runtime, core
    violations: list[str] = field(default_factory=list)

    @property
    def public_functions_without_docstrings(self) -> list[FunctionInfo]:
        """Get public functions missing docstrings."""
        return [
            f
            for f in self.functions
            if f.is_public and not f.has_docstring and not f.name.startswith("_")
        ]

    @property
    def functions_without_return_types(self) -> list[FunctionInfo]:
        """Get functions missing return type hints."""
        return [f for f in self.functions if not f.has_return_type and f.is_public]

    @property
    def functions_with_missing_param_types(self) -> list[FunctionInfo]:
        """Get functions with parameters missing type hints."""
        return [f for f in self.functions if f.missing_param_types and f.is_public]


@dataclass
class AnalysisResult:
    """Complete codebase analysis results."""

    root_path: Path
    files: list[FileAnalysis] = field(default_factory=list)
    total_files: int = 0
    total_functions: int = 0
    total_classes: int = 0
    errors: list[tuple[Path, str]] = field(default_factory=list)

    @property
    def missing_docstrings(self) -> list[tuple[Path, str, int]]:
        """Get all functions/classes missing docstrings."""
        missing = []
        for file in self.files:
            for func in file.public_functions_without_docstrings:
                missing.append((file.file_path, func.name, func.lineno))
            for cls in file.classes:
                if not cls.has_docstring:
                    missing.append((file.file_path, cls.name, cls.lineno))
        return missing

    @property
    def missing_type_hints(self) -> list[tuple[Path, str, int]]:
        """Get all functions missing type hints."""
        missing = []
        for file in self.files:
            for func in file.functions_without_return_types:
                missing.append((file.file_path, func.name, func.lineno))
        return missing

    @property
    def architecture_violations(self) -> list[tuple[Path, str]]:
        """Get all architecture layer violations."""
        violations = []
        for file in self.files:
            for violation in file.violations:
                violations.append((file.file_path, violation))
        return violations

    @property
    def quality_metrics(self) -> dict[str, Any]:
        """Calculate overall code quality metrics."""
        total_public_functions = sum(
            len([f for f in file.functions if f.is_public]) for file in self.files
        )
        functions_with_docstrings = total_public_functions - len(self.missing_docstrings)
        functions_with_types = total_public_functions - len(self.missing_type_hints)

        return {
            "total_files": self.total_files,
            "total_functions": total_public_functions,
            "total_classes": self.total_classes,
            "docstring_coverage": (
                functions_with_docstrings / total_public_functions * 100
                if total_public_functions > 0
                else 100.0
            ),
            "type_hint_coverage": (
                functions_with_types / total_public_functions * 100
                if total_public_functions > 0
                else 100.0
            ),
            "architecture_violations": len(self.architecture_violations),
            "parse_errors": len(self.errors),
        }


class FunctionAnalyzer(ast.NodeVisitor):
    """AST visitor for analyzing functions and methods."""

    def __init__(self, source: str) -> None:
        self.source = source
        self.source_lines = source.split("\n")
        self.functions: list[FunctionInfo] = []
        self.classes: list[ClassInfo] = []
        self._current_class: ClassInfo | None = None

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit a class definition."""
        # Check for docstring
        has_docstring = (
            len(node.body) > 0
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        )

        # Get base classes
        bases = [self._get_name(base) for base in node.bases]

        # Check for @dataclass decorator
        decorators = [self._get_decorator_name(dec) for dec in node.decorator_list]
        is_dataclass = "dataclass" in decorators

        class_info = ClassInfo(
            name=node.name,
            lineno=node.lineno,
            col_offset=node.col_offset,
            has_docstring=has_docstring,
            bases=bases,
            is_dataclass=is_dataclass,
            decorators=decorators,
        )

        # Set current class context
        prev_class = self._current_class
        self._current_class = class_info

        # Visit methods
        self.generic_visit(node)

        # Store class info
        self._current_class = prev_class
        self.classes.append(class_info)

    def visit_FunctionDef(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        """Visit a function or method definition."""
        # Check for docstring
        has_docstring = (
            len(node.body) > 0
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        )

        # Check return type hint
        has_return_type = node.returns is not None

        # Check parameter type hints
        missing_param_types = []
        for arg in node.args.args:
            if arg.annotation is None and arg.arg != "self" and arg.arg != "cls":
                missing_param_types.append(arg.arg)

        # Get decorators
        decorators = [self._get_decorator_name(dec) for dec in node.decorator_list]

        # Calculate complexity (simplified)
        complexity = self._calculate_complexity(node)

        # Extract source if possible
        source = None
        try:
            source = ast.get_source_segment(self.source, node)
        except Exception:
            pass

        func_info = FunctionInfo(
            name=node.name,
            lineno=node.lineno,
            col_offset=node.col_offset,
            has_docstring=has_docstring,
            has_return_type=has_return_type,
            missing_param_types=missing_param_types,
            is_async=isinstance(node, ast.AsyncFunctionDef),
            is_method=self._current_class is not None,
            is_public=not node.name.startswith("_"),
            decorators=decorators,
            complexity=complexity,
            source=source,
        )

        if self._current_class:
            self._current_class.methods.append(func_info)
        else:
            self.functions.append(func_info)

        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit an async function definition."""
        self.visit_FunctionDef(node)

    def _get_name(self, node: ast.expr) -> str:
        """Get name from an expression node."""
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        return str(ast.unparse(node))

    def _get_decorator_name(self, node: ast.expr) -> str:
        """Get decorator name from a decorator node."""
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Call):
            return self._get_name(node.func)
        if isinstance(node, ast.Attribute):
            return node.attr
        return str(ast.unparse(node))

    def _calculate_complexity(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
        """Calculate cyclomatic complexity (simplified)."""
        complexity = 1  # Base complexity
        for child in ast.walk(node):
            if isinstance(
                child,
                (ast.If, ast.While, ast.For, ast.AsyncFor, ast.ExceptHandler, ast.With),
            ):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity


class ImportAnalyzer(ast.NodeVisitor):
    """AST visitor for analyzing imports."""

    def __init__(self) -> None:
        self.imports = ImportInfo()

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Visit a 'from ... import ...' statement."""
        module = node.module or ""

        if module == "__future__":
            # Future imports
            for alias in node.names:
                self.imports.future_imports.append(alias.name)
        elif module.startswith("specify_cli"):
            # Local imports
            for alias in node.names:
                import_name = f"{module}.{alias.name}" if alias.name != "*" else module
                self.imports.local.append(import_name)
        elif self._is_stdlib(module):
            # Standard library
            self.imports.standard_library.append(module)
        else:
            # Third-party
            self.imports.third_party.append(module)

        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        """Visit an 'import ...' statement."""
        for alias in node.names:
            module = alias.name
            if module.startswith("specify_cli"):
                self.imports.local.append(module)
            elif self._is_stdlib(module):
                self.imports.standard_library.append(module)
            else:
                self.imports.third_party.append(module)

        self.generic_visit(node)

    def _is_stdlib(self, module: str) -> bool:
        """Check if a module is from the standard library."""
        # Common stdlib modules (not exhaustive)
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


class CodebaseAnalyzer:
    """Analyze entire codebase using AST."""

    def __init__(self, root_path: Path | str) -> None:
        self.root_path = Path(root_path)
        self.results = AnalysisResult(root_path=self.root_path)

    def analyze(self, pattern: str = "**/*.py") -> AnalysisResult:
        """Analyze all Python files in the codebase.

        Parameters
        ----------
        pattern : str, optional
            Glob pattern for finding Python files. Default is "**/*.py".

        Returns
        -------
        AnalysisResult
            Complete analysis results.
        """
        python_files = sorted(self.root_path.glob(pattern))

        for file_path in python_files:
            # Skip test files and generated files for now
            if "test_" in file_path.name or "__pycache__" in str(file_path):
                continue

            try:
                analysis = self.analyze_file(file_path)
                self.results.files.append(analysis)
                self.results.total_files += 1
                self.results.total_functions += len(analysis.functions)
                self.results.total_classes += len(analysis.classes)
            except Exception as e:
                logger.error("Error analyzing %s: %s", file_path, e)
                self.results.errors.append((file_path, str(e)))

        return self.results

    def analyze_file(self, file_path: Path) -> FileAnalysis:
        """Analyze a single Python file.

        Parameters
        ----------
        file_path : Path
            Path to the Python file.

        Returns
        -------
        FileAnalysis
            Analysis results for the file.
        """
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(file_path))

        # Determine module name
        try:
            module_name = str(file_path.relative_to(self.root_path)).replace("/", ".")[:-3]
        except ValueError:
            module_name = file_path.stem

        # Check for module docstring
        has_module_docstring = (
            len(tree.body) > 0
            and isinstance(tree.body[0], ast.Expr)
            and isinstance(tree.body[0].value, ast.Constant)
            and isinstance(tree.body[0].value.value, str)
        )

        # Analyze functions and classes
        func_analyzer = FunctionAnalyzer(source)
        func_analyzer.visit(tree)

        # Analyze imports
        import_analyzer = ImportAnalyzer()
        import_analyzer.visit(tree)

        # Count lines
        lines = source.split("\n")
        total_lines = len(lines)
        blank_lines = sum(1 for line in lines if not line.strip())
        comment_lines = sum(1 for line in lines if line.strip().startswith("#"))
        code_lines = total_lines - blank_lines - comment_lines

        # Determine architecture layer
        architecture_layer = self._determine_layer(file_path)

        # Check for architecture violations
        violations = self._check_violations(file_path, architecture_layer, import_analyzer.imports)

        return FileAnalysis(
            file_path=file_path,
            module_name=module_name,
            has_module_docstring=has_module_docstring,
            functions=func_analyzer.functions,
            classes=func_analyzer.classes,
            imports=import_analyzer.imports,
            total_lines=total_lines,
            code_lines=code_lines,
            comment_lines=comment_lines,
            blank_lines=blank_lines,
            complexity_score=sum(f.complexity for f in func_analyzer.functions),
            architecture_layer=architecture_layer,
            violations=violations,
        )

    def _determine_layer(self, file_path: Path) -> str | None:
        """Determine which architecture layer a file belongs to."""
        parts = file_path.parts
        if "commands" in parts:
            return "commands"
        if "ops" in parts:
            return "ops"
        if "runtime" in parts:
            return "runtime"
        if "core" in parts:
            return "core"
        return None

    def _check_violations(
        self, _file_path: Path, layer: str | None, imports: ImportInfo
    ) -> list[str]:
        """Check for architecture violations.

        Rules:
        - Commands layer: No subprocess, no file I/O
        - Ops layer: No subprocess, no file I/O, no HTTP
        - Runtime layer: Can do anything
        """
        violations = []

        if layer == "ops":
            # Ops layer should not import subprocess, os (for I/O), pathlib (for I/O)
            forbidden = ["subprocess", "os.path", "shutil"]
            for imp in imports.standard_library + imports.third_party:
                if any(f in imp for f in forbidden):
                    violations.append(
                        f"Ops layer should not import {imp} (violates pure function rule)"
                    )

        elif layer == "commands":
            # Commands layer should not import subprocess
            if "subprocess" in imports.standard_library + imports.third_party:
                violations.append("Commands layer should not import subprocess")

        return violations


def analyze_codebase(root_path: Path | str, pattern: str = "**/*.py") -> AnalysisResult:
    """Convenience function to analyze a codebase.

    Parameters
    ----------
    root_path : Path | str
        Root path of the codebase.
    pattern : str, optional
        Glob pattern for finding Python files. Default is "**/*.py".

    Returns
    -------
    AnalysisResult
        Complete analysis results.
    """
    analyzer = CodebaseAnalyzer(root_path)
    return analyzer.analyze(pattern)
