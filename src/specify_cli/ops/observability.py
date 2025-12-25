"""
specify_cli.ops.observability - Observability Operations
========================================================

Business logic for observability dashboards and metrics.

This module contains pure business logic for generating dashboards,
collecting metrics, and detecting performance anomalies.

Key Features
-----------
* **Dashboard Generation**: Create HTML dashboards for visualization
* **Statistics Collection**: Gather performance metrics and statistics
* **Anomaly Detection**: Detect performance regressions
* **Baseline Management**: Save/load performance baselines

Design Principles
----------------
* Pure functions (same input → same output)
* Delegates I/O to runtime or core modules
* Fully testable
* Returns structured results for commands to format

Examples
--------
    >>> from specify_cli.ops.observability import get_all_stats
    >>>
    >>> stats = get_all_stats()
    >>> for op, metrics in stats.items():
    ...     print(f"{op}: {metrics['mean']:.3f}s")

See Also
--------
- :mod:`specify_cli.core.advanced_observability` : Metrics collection
- :mod:`specify_cli.core.observability_dashboards` : Dashboard generation
- :mod:`specify_cli.commands.observability` : CLI command handler
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from specify_cli.core.advanced_observability import (
    AnomalyResult,
    PerformanceBaseline,
    detect_anomalies as core_detect_anomalies,
    get_all_stats as core_get_all_stats,
    get_performance_stats as core_get_performance_stats,
    load_baselines as core_load_baselines,
    save_baselines as core_save_baselines,
    update_all_baselines as core_update_all_baselines,
)
from specify_cli.core.observability_dashboards import (
    export_metrics_json,
    generate_all_dashboards,
)
from specify_cli.core.telemetry import span

__all__ = [
    "detect_anomalies",
    "export_metrics",
    "generate_dashboards",
    "get_all_stats",
    "get_stats",
    "load_baselines",
    "save_baselines",
    "update_baselines",
]


def generate_dashboards(output_dir: Path) -> dict[str, Path]:
    """Generate observability dashboards.

    Parameters
    ----------
    output_dir : Path
        Output directory for dashboards.

    Returns
    -------
    dict[str, Path]
        Mapping of dashboard names to file paths.
    """
    with span("ops.observability.generate_dashboards", output_dir=str(output_dir)):
        return generate_all_dashboards(output_dir)


def get_stats(operation: str) -> dict[str, Any]:
    """Get performance statistics for an operation.

    Parameters
    ----------
    operation : str
        The operation name.

    Returns
    -------
    dict[str, Any]
        Performance statistics.
    """
    with span("ops.observability.get_stats", operation=operation):
        return core_get_performance_stats(operation)


def get_all_stats() -> dict[str, dict[str, Any]]:
    """Get performance statistics for all operations.

    Returns
    -------
    dict[str, dict[str, Any]]
        Statistics for all operations.
    """
    with span("ops.observability.get_all_stats"):
        return core_get_all_stats()


def detect_anomalies(operation: str | None = None) -> list[AnomalyResult]:
    """Detect performance anomalies.

    Parameters
    ----------
    operation : str, optional
        The operation to check. If None, checks all operations.

    Returns
    -------
    list[AnomalyResult]
        List of detected anomalies.
    """
    with span("ops.observability.detect_anomalies", operation=operation or "all"):
        return core_detect_anomalies(operation)


def export_metrics(output_path: Path) -> None:
    """Export metrics as JSON.

    Parameters
    ----------
    output_path : Path
        Output path for JSON file.
    """
    with span("ops.observability.export_metrics", output_path=str(output_path)):
        export_metrics_json(output_path)


def save_baselines(path: Path | None = None) -> None:
    """Save performance baselines to disk.

    Parameters
    ----------
    path : Path, optional
        Path to save baselines. Default is .specify/baselines.
    """
    with span("ops.observability.save_baselines", path=str(path) if path else "default"):
        core_save_baselines(path)


def load_baselines(path: Path | None = None) -> None:
    """Load performance baselines from disk.

    Parameters
    ----------
    path : Path, optional
        Path to load baselines from. Default is .specify/baselines.
    """
    with span("ops.observability.load_baselines", path=str(path) if path else "default"):
        core_load_baselines(path)


def update_baselines() -> dict[str, PerformanceBaseline]:
    """Update baselines for all operations.

    Returns
    -------
    dict[str, PerformanceBaseline]
        Updated baselines.
    """
    with span("ops.observability.update_baselines"):
        return core_update_all_baselines()
