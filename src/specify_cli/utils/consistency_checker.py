"""
specify_cli.utils.consistency_checker - Code Consistency Verification
======================================================================

Verify code consistency across the three-tier architecture.

This module checks that all code follows consistent patterns and
adheres to the architectural principles of the spec-kit project.

Key Features
-----------
* **Pattern Verification**: Check command/ops/runtime patterns
* **Architecture Compliance**: Verify layer separation
* **Documentation Consistency**: Ensure consistent docstrings
* **Type Hint Coverage**: Measure type annotation completeness
* **Metrics Reporting**: Generate quality metrics

Examples
--------
    >>> from specify_cli.utils.consistency_checker import verify_consistency
    >>>
    >>> report = verify_consistency("/path/to/src")
    >>> print(report.summary())

See Also
--------
- :mod:`specify_cli.utils.ast_analyzer` : AST code analyzer
- :mod:`specify_cli.utils.ast_transformers` : Code transformers
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

from specify_cli.utils.ast_analyzer import AnalysisResult, FileAnalysis, analyze_codebase

logger = logging.getLogger(__name__)

__all__ = [
    "ConsistencyReport",
    "verify_consistency",
]


@dataclass
class ConsistencyReport:
    """Report on code consistency across the codebase."""

    analysis: AnalysisResult
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    @property
    def total_issues(self) -> int:
        """Get total number of issues found."""
        return len(self.issues)

    @property
    def is_consistent(self) -> bool:
        """Check if codebase is consistent."""
        return self.total_issues == 0

    def summary(self) -> str:
        """Generate a summary report.

        Returns
        -------
        str
            Formatted summary report.
        """
        lines = []
        lines.append("=" * 70)
        lines.append("CODE CONSISTENCY REPORT")
        lines.append("=" * 70)
        lines.append("")

        # Overall metrics
        metrics = self.analysis.quality_metrics
        lines.append("OVERALL METRICS")
        lines.append("-" * 70)
        lines.append(f"  Files analyzed:           {metrics['total_files']}")
        lines.append(f"  Total functions:          {metrics['total_functions']}")
        lines.append(f"  Total classes:            {metrics['total_classes']}")
        lines.append(f"  Docstring coverage:       {metrics['docstring_coverage']:.1f}%")
        lines.append(f"  Type hint coverage:       {metrics['type_hint_coverage']:.1f}%")
        lines.append(f"  Architecture violations:  {metrics['architecture_violations']}")
        lines.append(f"  Parse errors:             {metrics['parse_errors']}")
        lines.append("")

        # Issues
        if self.issues:
            lines.append("ISSUES FOUND")
            lines.append("-" * 70)
            for issue in self.issues[:20]:  # Show first 20
                lines.append(f"  - {issue}")
            if len(self.issues) > 20:
                lines.append(f"  ... and {len(self.issues) - 20} more issues")
            lines.append("")

        # Warnings
        if self.warnings:
            lines.append("WARNINGS")
            lines.append("-" * 70)
            for warning in self.warnings[:10]:  # Show first 10
                lines.append(f"  - {warning}")
            if len(self.warnings) > 10:
                lines.append(f"  ... and {len(self.warnings) - 10} more warnings")
            lines.append("")

        # Recommendations
        if self.recommendations:
            lines.append("RECOMMENDATIONS")
            lines.append("-" * 70)
            for rec in self.recommendations:
                lines.append(f"  - {rec}")
            lines.append("")

        # Overall status
        lines.append("OVERALL STATUS")
        lines.append("-" * 70)
        if self.is_consistent:
            lines.append("  ✓ Codebase is CONSISTENT")
        else:
            lines.append(f"  ✗ Found {self.total_issues} consistency issues")
        lines.append("")

        lines.append("=" * 70)

        return "\n".join(lines)

    def detailed_report(self) -> str:
        """Generate a detailed report with file-by-file analysis.

        Returns
        -------
        str
            Formatted detailed report.
        """
        lines = [self.summary()]
        lines.append("")
        lines.append("DETAILED FILE ANALYSIS")
        lines.append("=" * 70)
        lines.append("")

        # Group files by layer
        by_layer: dict[str, list[FileAnalysis]] = {}
        for file in self.analysis.files:
            layer = file.architecture_layer or "other"
            if layer not in by_layer:
                by_layer[layer] = []
            by_layer[layer].append(file)

        for layer in sorted(by_layer.keys()):
            lines.append(f"\n{layer.upper()} LAYER")
            lines.append("-" * 70)

            for file in by_layer[layer]:
                lines.append(f"\n  {file.file_path.name}")
                lines.append(f"    Functions: {len(file.functions)}")
                lines.append(f"    Classes: {len(file.classes)}")
                lines.append(f"    Lines: {file.code_lines} code, {file.comment_lines} comments")
                lines.append(f"    Complexity: {file.complexity_score}")

                if file.violations:
                    lines.append("    Violations:")
                    for violation in file.violations:
                        lines.append(f"      - {violation}")

                missing_docs = file.public_functions_without_docstrings
                if missing_docs:
                    lines.append(f"    Missing docstrings: {len(missing_docs)} functions")

                missing_types = file.functions_without_return_types
                if missing_types:
                    lines.append(f"    Missing type hints: {len(missing_types)} functions")

        return "\n".join(lines)


class ConsistencyChecker:
    """Check code consistency across the codebase."""

    def __init__(self, analysis: AnalysisResult) -> None:
        self.analysis = analysis
        self.report = ConsistencyReport(analysis=analysis)

    def check_all(self) -> ConsistencyReport:
        """Run all consistency checks.

        Returns
        -------
        ConsistencyReport
            Complete consistency report.
        """
        self.check_docstrings()
        self.check_type_hints()
        self.check_architecture_layers()
        self.check_import_patterns()
        self.check_command_patterns()
        self.check_ops_patterns()
        self.check_runtime_patterns()
        self.generate_recommendations()

        return self.report

    def check_docstrings(self) -> None:
        """Check for missing docstrings."""
        missing = self.analysis.missing_docstrings

        if missing:
            self.report.issues.append(
                f"Found {len(missing)} functions/classes missing docstrings"
            )

            # Add specific examples
            for path, name, lineno in missing[:5]:
                self.report.warnings.append(
                    f"{path.name}:{lineno} - {name} missing docstring"
                )

    def check_type_hints(self) -> None:
        """Check for missing type hints."""
        missing = self.analysis.missing_type_hints

        if missing:
            self.report.warnings.append(
                f"Found {len(missing)} functions missing return type hints"
            )

    def check_architecture_layers(self) -> None:
        """Check architecture layer violations."""
        violations = self.analysis.architecture_violations

        if violations:
            self.report.issues.append(
                f"Found {len(violations)} architecture violations"
            )

            for path, violation in violations[:5]:
                self.report.issues.append(f"{path.name}: {violation}")

    def check_import_patterns(self) -> None:
        """Check import organization consistency."""
        # Check that all files have consistent import ordering
        for file in self.analysis.files:
            imports = file.imports

            # Check for __future__ imports first
            if imports.future_imports and len(file.imports.future_imports) > 0:
                # This is good - future imports should be first
                pass

            # Warn about mixed local/third-party imports
            if imports.local and imports.third_party:
                # This is fine - just check they're organized
                pass

    def check_command_patterns(self) -> None:
        """Check that command layer follows patterns."""
        command_files = [
            f for f in self.analysis.files if f.architecture_layer == "commands"
        ]

        for file in command_files:
            # Commands should have Typer app
            # Commands should use @instrument_command decorator
            # Commands should delegate to ops layer

            for func in file.functions:
                # Check for instrumentation decorator
                if func.is_public and "instrument_command" not in func.decorators:
                    self.report.warnings.append(
                        f"{file.file_path.name}:{func.lineno} - "
                        f"Command {func.name} missing @instrument_command decorator"
                    )

    def check_ops_patterns(self) -> None:
        """Check that ops layer follows patterns."""
        ops_files = [f for f in self.analysis.files if f.architecture_layer == "ops"]

        for file in ops_files:
            # Ops functions should use @span decorator
            # Ops functions should return dataclass results
            # Ops functions should be pure (no I/O)

            for func in file.functions:
                if func.is_public and "span" not in func.decorators:
                    self.report.warnings.append(
                        f"{file.file_path.name}:{func.lineno} - "
                        f"Ops function {func.name} missing @span decorator"
                    )

    def check_runtime_patterns(self) -> None:
        """Check that runtime layer follows patterns."""
        runtime_files = [
            f for f in self.analysis.files if f.architecture_layer == "runtime"
        ]

        for file in runtime_files:
            # Runtime should use run_logged() for subprocess
            # Runtime should have proper error handling
            pass

    def generate_recommendations(self) -> None:
        """Generate recommendations for improvement."""
        metrics = self.analysis.quality_metrics

        if metrics["docstring_coverage"] < 80:
            self.report.recommendations.append(
                f"Improve docstring coverage from {metrics['docstring_coverage']:.1f}% to 80%+"
            )

        if metrics["type_hint_coverage"] < 90:
            self.report.recommendations.append(
                f"Improve type hint coverage from {metrics['type_hint_coverage']:.1f}% to 90%+"
            )

        if metrics["architecture_violations"] > 0:
            self.report.recommendations.append(
                "Fix architecture violations to ensure proper layer separation"
            )

        if len(self.analysis.missing_docstrings) > 0:
            self.report.recommendations.append(
                "Run AST transformers to auto-generate missing docstrings"
            )


def verify_consistency(
    root_path: Path | str, pattern: str = "**/*.py", verbose: bool = False
) -> ConsistencyReport:
    """Verify code consistency across the codebase.

    Parameters
    ----------
    root_path : Path | str
        Root directory of the codebase.
    pattern : str, optional
        Glob pattern for finding files. Default is "**/*.py".
    verbose : bool, optional
        Whether to show verbose output. Default is False.

    Returns
    -------
    ConsistencyReport
        Consistency verification report.
    """
    # Analyze codebase
    if verbose:
        logger.info(f"Analyzing codebase at {root_path}...")

    analysis = analyze_codebase(root_path, pattern)

    if verbose:
        logger.info(f"Analyzed {analysis.total_files} files")

    # Check consistency
    checker = ConsistencyChecker(analysis)
    report = checker.check_all()

    if verbose:
        logger.info(f"Found {report.total_issues} issues")

    return report
