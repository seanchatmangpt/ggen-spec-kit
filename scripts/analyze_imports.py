#!/usr/bin/env python3
"""
Import Time Analyzer

Analyzes which imports are taking the most time during CLI startup.
Uses Python's built-in import profiling to identify bottlenecks.
"""

import sys
import time
from pathlib import Path

# Ensure we're in the project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))


def time_import(module_name: str) -> float:
    """Time how long it takes to import a module."""
    start = time.perf_counter()
    try:
        __import__(module_name)
        elapsed = time.perf_counter() - start
        return elapsed
    except ImportError as e:
        print(f"  ❌ Failed to import {module_name}: {e}")
        return 0.0


def analyze_imports():
    """Analyze import times for all major dependencies."""
    print("=" * 80)
    print("IMPORT TIME ANALYSIS")
    print("=" * 80)

    imports_to_test = [
        # Core dependencies
        ("typer", "CLI framework"),
        ("rich", "Terminal formatting"),
        ("rich.console", "Console object"),
        ("rich.table", "Table rendering"),
        ("rich.panel", "Panel rendering"),
        ("rich.align", "Alignment utilities"),
        ("httpx", "HTTP client"),
        ("platformdirs", "Platform directories"),

        # CLI modules
        ("specify_cli", "Main CLI module"),
        ("specify_cli.cli", "Banner and helpers"),
        ("specify_cli.app", "App assembly"),
        ("specify_cli.commands", "Command handlers"),
        ("specify_cli.core", "Core utilities"),
        ("specify_cli.core.telemetry", "OpenTelemetry"),
        ("specify_cli.core.instrumentation", "Instrumentation"),

        # Optional heavy imports
        ("opentelemetry.sdk.trace", "OTEL tracing SDK"),
        ("opentelemetry.sdk.resources", "OTEL resources"),
        ("opentelemetry.sdk.trace.export", "OTEL exporters"),
    ]

    results = []
    total_time = 0.0

    print("\nMeasuring import times...\n")

    for module_name, description in imports_to_test:
        elapsed = time_import(module_name)
        if elapsed > 0:
            results.append((elapsed, module_name, description))
            total_time += elapsed
            status = "🟢" if elapsed < 0.05 else "🟡" if elapsed < 0.2 else "🔴"
            print(f"{status} {elapsed:>7.3f}s  {module_name:<40} {description}")

    print("\n" + "=" * 80)
    print(f"TOTAL IMPORT TIME: {total_time:.3f}s")
    print("=" * 80)

    # Sort by time and show top offenders
    results.sort(reverse=True)
    print("\nTop 10 slowest imports:")
    for i, (elapsed, module_name, description) in enumerate(results[:10], 1):
        pct = (elapsed / total_time * 100) if total_time > 0 else 0
        print(f"  {i:2d}. {elapsed:>7.3f}s ({pct:>5.1f}%)  {module_name}")

    return results


if __name__ == "__main__":
    analyze_imports()
