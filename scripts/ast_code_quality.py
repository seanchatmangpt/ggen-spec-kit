#!/usr/bin/env python3
"""
AST Code Quality Automation Script
===================================

Hyper-advanced AST manipulation for code consistency and auto-generation.

This script uses the AST analyzer, transformers, and consistency checker
to analyze the codebase, identify issues, and automatically improve code
quality.

Usage
-----
    # Analysis only (safe)
    python scripts/ast_code_quality.py --analyze

    # Generate consistency report
    python scripts/ast_code_quality.py --report

    # Dry run transformations (shows what would change)
    python scripts/ast_code_quality.py --transform --dry-run

    # Apply transformations (modifies files)
    python scripts/ast_code_quality.py --transform --apply

    # Full workflow
    python scripts/ast_code_quality.py --full

Examples
--------
    # Analyze codebase
    $ python scripts/ast_code_quality.py --analyze
    Analyzing 156 Python files...
    Found 23 missing docstrings
    Found 45 missing type hints
    Code quality score: 87.3%

    # Apply improvements
    $ python scripts/ast_code_quality.py --transform --apply
    Applying transformations...
    Modified 23 files
    Added 23 docstrings
    Organized imports in 15 files
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from specify_cli.utils.ast_analyzer import analyze_codebase
from specify_cli.utils.ast_transformers import apply_transformations
from specify_cli.utils.consistency_checker import verify_consistency

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def analyze_mode(root_path: Path, pattern: str = "src/**/*.py") -> None:
    """Run analysis mode - show codebase statistics.

    Parameters
    ----------
    root_path : Path
        Root path of the codebase.
    pattern : str, optional
        Glob pattern for files to analyze.
    """
    print("\n" + "=" * 70)
    print("AST CODEBASE ANALYSIS")
    print("=" * 70)
    print()

    logger.info("Analyzing codebase at %s...", root_path)
    logger.info("Pattern: %s", pattern)
    print()

    # Run analysis
    results = analyze_codebase(root_path, pattern)

    # Display results
    print(f"Files analyzed:       {results.total_files}")
    print(f"Total functions:      {results.total_functions}")
    print(f"Total classes:        {results.total_classes}")
    print()

    # Quality metrics
    metrics = results.quality_metrics
    print("QUALITY METRICS")
    print("-" * 70)
    print(f"  Docstring coverage:       {metrics['docstring_coverage']:>6.1f}%")
    print(f"  Type hint coverage:       {metrics['type_hint_coverage']:>6.1f}%")
    print(f"  Architecture violations:  {metrics['architecture_violations']:>6}")
    print(f"  Parse errors:             {metrics['parse_errors']:>6}")
    print()

    # Missing docstrings
    missing_docs = results.missing_docstrings
    if missing_docs:
        print(f"MISSING DOCSTRINGS ({len(missing_docs)} total)")
        print("-" * 70)
        for path, name, lineno in missing_docs[:10]:
            print(f"  {path.name}:{lineno:>4}  {name}")
        if len(missing_docs) > 10:
            print(f"  ... and {len(missing_docs) - 10} more")
        print()

    # Missing type hints
    missing_types = results.missing_type_hints
    if missing_types:
        print(f"MISSING TYPE HINTS ({len(missing_types)} total)")
        print("-" * 70)
        for path, name, lineno in missing_types[:10]:
            print(f"  {path.name}:{lineno:>4}  {name}")
        if len(missing_types) > 10:
            print(f"  ... and {len(missing_types) - 10} more")
        print()

    # Architecture violations
    violations = results.architecture_violations
    if violations:
        print(f"ARCHITECTURE VIOLATIONS ({len(violations)} total)")
        print("-" * 70)
        for path, violation in violations:
            print(f"  {path.name}: {violation}")
        print()

    # Overall score
    overall_score = (
        metrics["docstring_coverage"] * 0.4 + metrics["type_hint_coverage"] * 0.4
    ) + (20 if metrics["architecture_violations"] == 0 else 0)

    print("OVERALL CODE QUALITY SCORE")
    print("-" * 70)
    print(f"  {overall_score:.1f}%")
    print()

    if overall_score >= 90:
        print("  ✓ EXCELLENT - Code quality is outstanding!")
    elif overall_score >= 80:
        print("  ✓ GOOD - Code quality is solid")
    elif overall_score >= 70:
        print("  ⚠ FAIR - Some improvements needed")
    else:
        print("  ✗ POOR - Significant improvements needed")
    print()


def report_mode(root_path: Path, pattern: str = "src/**/*.py", detailed: bool = False) -> None:
    """Run report mode - generate consistency report.

    Parameters
    ----------
    root_path : Path
        Root path of the codebase.
    pattern : str, optional
        Glob pattern for files to analyze.
    detailed : bool, optional
        Whether to show detailed report.
    """
    logger.info("Generating consistency report...")
    print()

    report = verify_consistency(root_path, pattern, verbose=True)

    if detailed:
        print(report.detailed_report())
    else:
        print(report.summary())


def transform_mode(
    root_path: Path,
    pattern: str = "src/**/*.py",
    dry_run: bool = True,
    add_docstrings: bool = True,
    add_type_hints: bool = False,
) -> None:
    """Run transform mode - apply AST transformations.

    Parameters
    ----------
    root_path : Path
        Root path of the codebase.
    pattern : str, optional
        Glob pattern for files to transform.
    dry_run : bool, optional
        If True, don't write changes to disk.
    add_docstrings : bool, optional
        Whether to add docstrings.
    add_type_hints : bool, optional
        Whether to add type hints.
    """
    print("\n" + "=" * 70)
    print("AST CODE TRANSFORMATIONS")
    print("=" * 70)
    print()

    if dry_run:
        print("MODE: DRY RUN (no files will be modified)")
    else:
        print("MODE: APPLY (files WILL be modified)")
    print()

    logger.info("Running transformations...")
    logger.info("  Add docstrings: %s", add_docstrings)
    logger.info("  Add type hints: %s", add_type_hints)
    logger.info("  Normalize imports: True")
    print()

    results = apply_transformations(
        root_path,
        pattern=pattern,
        dry_run=dry_run,
        add_docstrings=add_docstrings,
        add_type_hints=add_type_hints,
        normalize_imports=True,
    )

    # Display results
    print("TRANSFORMATION RESULTS")
    print("-" * 70)
    print(f"  Files processed:      {results['files_processed']}")
    print(f"  Files modified:       {results['files_modified']}")
    print(f"  Total modifications:  {results['total_modifications']}")
    print(f"  Errors:               {len(results['errors'])}")
    print()

    if results["modified_files"]:
        print(f"MODIFIED FILES ({len(results['modified_files'])} total)")
        print("-" * 70)
        for item in results["modified_files"][:20]:
            path = Path(item["path"]).name
            mods = item["modifications"]
            print(f"  {path:<40}  {mods:>3} changes")
        if len(results["modified_files"]) > 20:
            print(f"  ... and {len(results['modified_files']) - 20} more files")
        print()

    if results["errors"]:
        print("ERRORS")
        print("-" * 70)
        for error in results["errors"]:
            print(f"  {error['path']}: {error['error']}")
        print()

    if not dry_run:
        print("✓ Transformations applied successfully!")
        print()
        print("NEXT STEPS:")
        print("  1. Review the changes: git diff")
        print("  2. Run tests: uv run pytest tests/")
        print("  3. Run linters: uv run ruff check src/")
        print("  4. Commit if satisfied: git add . && git commit")
        print()
    else:
        print("⚠ This was a DRY RUN - no files were modified")
        print()
        print("To apply these transformations, run:")
        print("  python scripts/ast_code_quality.py --transform --apply")
        print()


def full_workflow(root_path: Path, pattern: str = "src/**/*.py") -> None:
    """Run full workflow - analyze, report, transform.

    Parameters
    ----------
    root_path : Path
        Root path of the codebase.
    pattern : str, optional
        Glob pattern for files.
    """
    print("\n" + "=" * 70)
    print("FULL AST CODE QUALITY WORKFLOW")
    print("=" * 70)
    print()

    # Step 1: Analysis
    print("STEP 1: ANALYSIS")
    print("-" * 70)
    analyze_mode(root_path, pattern)

    # Step 2: Consistency Report
    print("\nSTEP 2: CONSISTENCY REPORT")
    print("-" * 70)
    report_mode(root_path, pattern, detailed=False)

    # Step 3: Dry Run Transformations
    print("\nSTEP 3: DRY RUN TRANSFORMATIONS")
    print("-" * 70)
    transform_mode(root_path, pattern, dry_run=True)

    print("\n" + "=" * 70)
    print("WORKFLOW COMPLETE")
    print("=" * 70)
    print()
    print("Review the analysis above and decide:")
    print("  1. Apply transformations: --transform --apply")
    print("  2. Get detailed report: --report --detailed")
    print("  3. Analyze specific files: --analyze --pattern 'ops/**/*.py'")
    print()


def export_metrics(root_path: Path, pattern: str = "src/**/*.py", output: Path | None = None) -> None:
    """Export metrics to JSON file.

    Parameters
    ----------
    root_path : Path
        Root path of the codebase.
    pattern : str, optional
        Glob pattern for files.
    output : Path, optional
        Output file path for JSON.
    """
    logger.info("Exporting metrics to JSON...")

    results = analyze_codebase(root_path, pattern)
    metrics = results.quality_metrics

    # Build JSON structure
    export_data = {
        "timestamp": str(Path(__file__).stat().st_mtime),
        "root_path": str(root_path),
        "pattern": pattern,
        "metrics": metrics,
        "missing_docstrings": len(results.missing_docstrings),
        "missing_type_hints": len(results.missing_type_hints),
        "architecture_violations": len(results.architecture_violations),
        "files": [
            {
                "path": str(f.file_path.relative_to(root_path)),
                "module": f.module_name,
                "layer": f.architecture_layer,
                "functions": len(f.functions),
                "classes": len(f.classes),
                "code_lines": f.code_lines,
                "complexity": f.complexity_score,
            }
            for f in results.files
        ],
    }

    # Write JSON
    output_path = output or root_path / "code_quality_metrics.json"
    output_path.write_text(json.dumps(export_data, indent=2), encoding="utf-8")

    logger.info("Metrics exported to %s", output_path)
    print(f"\n✓ Metrics exported to {output_path}\n")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="AST-based code quality analysis and transformation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # Modes
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Run analysis mode (show statistics)",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate consistency report",
    )
    parser.add_argument(
        "--transform",
        action="store_true",
        help="Run transformation mode",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Run full workflow (analyze + report + transform dry-run)",
    )
    parser.add_argument(
        "--export",
        action="store_true",
        help="Export metrics to JSON",
    )

    # Options
    parser.add_argument(
        "--pattern",
        default="src/**/*.py",
        help="Glob pattern for files to process (default: src/**/*.py)",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).parent.parent,
        help="Root path of the codebase",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply transformations (default is dry-run)",
    )
    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Show detailed report",
    )
    parser.add_argument(
        "--add-type-hints",
        action="store_true",
        help="Add missing type hints (experimental)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output file for JSON export",
    )

    args = parser.parse_args()

    # Determine mode
    if args.full:
        full_workflow(args.root, args.pattern)
    elif args.analyze:
        analyze_mode(args.root, args.pattern)
    elif args.report:
        report_mode(args.root, args.pattern, detailed=args.detailed)
    elif args.transform:
        transform_mode(
            args.root,
            args.pattern,
            dry_run=not args.apply,
            add_type_hints=args.add_type_hints,
        )
    elif args.export:
        export_metrics(args.root, args.pattern, args.output)
    else:
        # Default: run analysis
        analyze_mode(args.root, args.pattern)


if __name__ == "__main__":
    main()
