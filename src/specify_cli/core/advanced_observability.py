"""
specify_cli.core.advanced_observability
---------------------------------------
Advanced OpenTelemetry instrumentation with metrics, distributed tracing, and anomaly detection.

This module provides hyper-advanced observability capabilities:

* **Performance Metrics**: P50, P95, P99 percentiles for all operations
* **Anomaly Detection**: Statistical analysis to detect performance regressions
* **Distributed Tracing**: Context propagation and trace correlation
* **Resource Tracking**: CPU, memory, disk I/O monitoring
* **Dashboards**: Automatic dashboard generation for visualization
* **Baselines**: Performance baseline tracking and validation

The module integrates seamlessly with the existing telemetry infrastructure
while adding advanced features for production-grade observability.

Example
-------
    from specify_cli.core.advanced_observability import (
        track_performance,
        detect_anomalies,
        PerformanceTracker,
    )

    # Track command performance
    tracker = PerformanceTracker("my_command")
    with tracker:
        perform_operation()

    # Detect anomalies
    anomalies = detect_anomalies("my_command")
    if anomalies:
        print(f"Performance regression detected: {anomalies}")

Environment Variables
--------------------
- SPECIFY_METRICS_ENABLED : Enable advanced metrics (default: "true")
- SPECIFY_BASELINE_PATH : Path to performance baselines (default: .specify/baselines)
- SPECIFY_ANOMALY_THRESHOLD : Z-score threshold for anomaly detection (default: 2.0)

See Also
--------
- :mod:`specify_cli.core.telemetry` : Core telemetry functions
- :mod:`specify_cli.core.instrumentation` : Command instrumentation
- :mod:`specify_cli.core.semconv` : Semantic conventions
"""

from __future__ import annotations

import json
import os
import threading
import time
from collections import defaultdict, deque
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from .telemetry import (
    OTEL_AVAILABLE,
    get_current_span,
    metric_counter,
    metric_histogram,
)

# Check if scipy is available for advanced statistical analysis
try:
    from scipy import stats

    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


# --------------------------------------------------------------------------- #
# Configuration                                                                #
# --------------------------------------------------------------------------- #

METRICS_ENABLED = os.getenv("SPECIFY_METRICS_ENABLED", "true").lower() not in (
    "false",
    "0",
    "no",
)
BASELINE_PATH = Path(os.getenv("SPECIFY_BASELINE_PATH", ".specify/baselines"))
ANOMALY_THRESHOLD = float(os.getenv("SPECIFY_ANOMALY_THRESHOLD", "2.0"))
METRICS_WINDOW_SIZE = int(os.getenv("SPECIFY_METRICS_WINDOW_SIZE", "1000"))


# --------------------------------------------------------------------------- #
# Data Structures                                                              #
# --------------------------------------------------------------------------- #


@dataclass
class PerformanceMetrics:
    """Performance metrics for a single operation."""

    operation: str
    duration_seconds: float
    timestamp: float = field(default_factory=time.time)
    success: bool = True
    error_type: str | None = None
    resource_usage: dict[str, float] = field(default_factory=dict)
    custom_attributes: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class PerformanceBaseline:
    """Performance baseline for an operation."""

    operation: str
    mean_duration: float
    std_duration: float
    p50: float
    p95: float
    p99: float
    sample_count: int
    last_updated: float = field(default_factory=time.time)
    min_duration: float = 0.0
    max_duration: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PerformanceBaseline:
        """Create from dictionary."""
        return cls(**data)


@dataclass
class AnomalyResult:
    """Result of anomaly detection."""

    operation: str
    is_anomaly: bool
    z_score: float
    current_duration: float
    baseline_mean: float
    baseline_std: float
    threshold: float
    deviation_pct: float
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


# --------------------------------------------------------------------------- #
# In-Memory Metrics Store                                                     #
# --------------------------------------------------------------------------- #


class MetricsStore:
    """Thread-safe in-memory metrics store with rolling windows."""

    def __init__(self, window_size: int = METRICS_WINDOW_SIZE):
        """Initialize metrics store.

        Parameters
        ----------
        window_size : int
            Maximum number of metrics to keep per operation.
        """
        self._metrics: dict[str, deque[PerformanceMetrics]] = defaultdict(
            lambda: deque(maxlen=window_size)
        )
        self._baselines: dict[str, PerformanceBaseline] = {}
        self._lock = threading.RLock()
        self._success_counts: dict[str, int] = defaultdict(int)
        self._failure_counts: dict[str, int] = defaultdict(int)
        self._error_types: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    def record(self, metric: PerformanceMetrics) -> None:
        """Record a performance metric.

        Parameters
        ----------
        metric : PerformanceMetrics
            The metric to record.
        """
        with self._lock:
            self._metrics[metric.operation].append(metric)

            # Update success/failure counts
            if metric.success:
                self._success_counts[metric.operation] += 1
            else:
                self._failure_counts[metric.operation] += 1
                if metric.error_type:
                    self._error_types[metric.operation][metric.error_type] += 1

            # Record OTEL metrics if available
            if OTEL_AVAILABLE:
                metric_histogram(f"advanced.{metric.operation}.duration")(
                    metric.duration_seconds
                )
                metric_counter(f"advanced.{metric.operation}.calls")(1)
                if not metric.success:
                    metric_counter(f"advanced.{metric.operation}.errors")(1)

    def get_metrics(self, operation: str) -> list[PerformanceMetrics]:
        """Get all metrics for an operation.

        Parameters
        ----------
        operation : str
            The operation name.

        Returns
        -------
        list[PerformanceMetrics]
            List of metrics.
        """
        with self._lock:
            return list(self._metrics.get(operation, []))

    def get_durations(self, operation: str) -> list[float]:
        """Get all durations for an operation.

        Parameters
        ----------
        operation : str
            The operation name.

        Returns
        -------
        list[float]
            List of durations in seconds.
        """
        metrics = self.get_metrics(operation)
        return [m.duration_seconds for m in metrics]

    def get_success_rate(self, operation: str) -> float:
        """Get success rate for an operation.

        Parameters
        ----------
        operation : str
            The operation name.

        Returns
        -------
        float
            Success rate between 0.0 and 1.0.
        """
        with self._lock:
            total = self._success_counts[operation] + self._failure_counts[operation]
            if total == 0:
                return 1.0
            return self._success_counts[operation] / total

    def get_error_distribution(self, operation: str) -> dict[str, int]:
        """Get error type distribution for an operation.

        Parameters
        ----------
        operation : str
            The operation name.

        Returns
        -------
        dict[str, int]
            Error type to count mapping.
        """
        with self._lock:
            return dict(self._error_types.get(operation, {}))

    def update_baseline(self, operation: str) -> PerformanceBaseline | None:
        """Update performance baseline for an operation.

        Parameters
        ----------
        operation : str
            The operation name.

        Returns
        -------
        PerformanceBaseline | None
            Updated baseline or None if insufficient data.
        """
        durations = self.get_durations(operation)
        if len(durations) < 10:  # Need at least 10 samples
            return None

        with self._lock:
            arr = np.array(durations)
            baseline = PerformanceBaseline(
                operation=operation,
                mean_duration=float(np.mean(arr)),
                std_duration=float(np.std(arr)),
                p50=float(np.percentile(arr, 50)),
                p95=float(np.percentile(arr, 95)),
                p99=float(np.percentile(arr, 99)),
                sample_count=len(durations),
                min_duration=float(np.min(arr)),
                max_duration=float(np.max(arr)),
            )
            self._baselines[operation] = baseline
            return baseline

    def get_baseline(self, operation: str) -> PerformanceBaseline | None:
        """Get performance baseline for an operation.

        Parameters
        ----------
        operation : str
            The operation name.

        Returns
        -------
        PerformanceBaseline | None
            Baseline or None if not available.
        """
        with self._lock:
            return self._baselines.get(operation)

    def get_all_operations(self) -> list[str]:
        """Get all tracked operations.

        Returns
        -------
        list[str]
            List of operation names.
        """
        with self._lock:
            return list(self._metrics.keys())


# Global metrics store
_GLOBAL_STORE = MetricsStore()


# --------------------------------------------------------------------------- #
# Performance Tracking                                                         #
# --------------------------------------------------------------------------- #


class PerformanceTracker:
    """Context manager for tracking operation performance."""

    def __init__(
        self,
        operation: str,
        *,
        track_resources: bool = False,
        auto_baseline: bool = True,
        detect_anomalies: bool = True,
        **custom_attributes: Any,
    ):
        """Initialize performance tracker.

        Parameters
        ----------
        operation : str
            The operation name.
        track_resources : bool, optional
            Whether to track resource usage. Default is False.
        auto_baseline : bool, optional
            Whether to automatically update baselines. Default is True.
        detect_anomalies : bool, optional
            Whether to detect anomalies. Default is True.
        **custom_attributes
            Custom attributes to attach to the metric.
        """
        self.operation = operation
        self.track_resources = track_resources
        self.auto_baseline = auto_baseline
        self.detect_anomalies_flag = detect_anomalies
        self.custom_attributes = custom_attributes
        self.start_time: float = 0.0
        self.metric: PerformanceMetrics | None = None

    def __enter__(self) -> PerformanceTracker:
        """Enter context."""
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context."""
        duration = time.time() - self.start_time
        success = exc_type is None

        # Create metric
        self.metric = PerformanceMetrics(
            operation=self.operation,
            duration_seconds=duration,
            success=success,
            error_type=exc_type.__name__ if exc_type else None,
            custom_attributes=self.custom_attributes,
        )

        # Track resources if enabled
        if self.track_resources:
            self.metric.resource_usage = get_resource_usage()

        # Record metric
        if METRICS_ENABLED:
            _GLOBAL_STORE.record(self.metric)

            # Update baseline periodically
            if self.auto_baseline:
                metrics_count = len(_GLOBAL_STORE.get_metrics(self.operation))
                if metrics_count % 100 == 0:  # Update every 100 samples
                    _GLOBAL_STORE.update_baseline(self.operation)

            # Detect anomalies
            if self.detect_anomalies_flag and success:
                anomaly = detect_anomaly(self.operation, duration)
                if anomaly and anomaly.is_anomaly:
                    # Record anomaly event in OTEL
                    if OTEL_AVAILABLE:
                        current_span = get_current_span()
                        if current_span.is_recording():
                            current_span.add_event(
                                "performance.anomaly",
                                {
                                    "operation": self.operation,
                                    "z_score": anomaly.z_score,
                                    "deviation_pct": anomaly.deviation_pct,
                                    "current": duration,
                                    "baseline_mean": anomaly.baseline_mean,
                                },
                            )


@contextmanager
def track_performance(operation: str, **attributes: Any):
    """Context manager for tracking operation performance.

    Parameters
    ----------
    operation : str
        The operation name.
    **attributes
        Custom attributes to attach.

    Yields
    ------
    PerformanceTracker
        The performance tracker instance.
    """
    tracker = PerformanceTracker(operation, **attributes)
    with tracker:
        yield tracker


# --------------------------------------------------------------------------- #
# Anomaly Detection                                                            #
# --------------------------------------------------------------------------- #


def detect_anomaly(operation: str, duration: float) -> AnomalyResult | None:
    """Detect if a duration is anomalous based on baseline.

    Parameters
    ----------
    operation : str
        The operation name.
    duration : float
        The duration to check.

    Returns
    -------
    AnomalyResult | None
        Anomaly result or None if no baseline available.
    """
    baseline = _GLOBAL_STORE.get_baseline(operation)
    if not baseline or baseline.std_duration == 0:
        return None

    # Calculate z-score
    z_score = abs((duration - baseline.mean_duration) / baseline.std_duration)
    is_anomaly = z_score > ANOMALY_THRESHOLD

    # Calculate deviation percentage
    deviation_pct = ((duration - baseline.mean_duration) / baseline.mean_duration) * 100

    return AnomalyResult(
        operation=operation,
        is_anomaly=is_anomaly,
        z_score=z_score,
        current_duration=duration,
        baseline_mean=baseline.mean_duration,
        baseline_std=baseline.std_duration,
        threshold=ANOMALY_THRESHOLD,
        deviation_pct=deviation_pct,
    )


def detect_anomalies(operation: str | None = None) -> list[AnomalyResult]:
    """Detect anomalies in recent metrics.

    Parameters
    ----------
    operation : str, optional
        The operation to check. If None, checks all operations.

    Returns
    -------
    list[AnomalyResult]
        List of detected anomalies.
    """
    operations = [operation] if operation else _GLOBAL_STORE.get_all_operations()
    anomalies: list[AnomalyResult] = []

    for op in operations:
        metrics = _GLOBAL_STORE.get_metrics(op)
        if not metrics:
            continue

        # Check last 10 metrics
        recent = metrics[-10:]
        for metric in recent:
            if not metric.success:
                continue

            result = detect_anomaly(op, metric.duration_seconds)
            if result and result.is_anomaly:
                anomalies.append(result)

    return anomalies


# --------------------------------------------------------------------------- #
# Resource Tracking                                                            #
# --------------------------------------------------------------------------- #


def get_resource_usage() -> dict[str, float]:
    """Get current resource usage.

    Returns
    -------
    dict[str, float]
        Resource usage metrics.
    """
    try:
        import psutil

        process = psutil.Process()
        return {
            "cpu_percent": process.cpu_percent(),
            "memory_mb": process.memory_info().rss / 1024 / 1024,
            "num_threads": process.num_threads(),
        }
    except ImportError:
        return {}


# --------------------------------------------------------------------------- #
# Baseline Management                                                          #
# --------------------------------------------------------------------------- #


def save_baselines(path: Path | None = None) -> None:
    """Save performance baselines to disk.

    Parameters
    ----------
    path : Path, optional
        Path to save baselines. Default is BASELINE_PATH.
    """
    path = path or BASELINE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)

    baselines = {
        op: _GLOBAL_STORE.get_baseline(op).to_dict()
        for op in _GLOBAL_STORE.get_all_operations()
        if _GLOBAL_STORE.get_baseline(op)
    }

    with Path(path).open("w") as f:
        json.dump(baselines, f, indent=2)


def load_baselines(path: Path | None = None) -> None:
    """Load performance baselines from disk.

    Parameters
    ----------
    path : Path, optional
        Path to load baselines from. Default is BASELINE_PATH.
    """
    path = path or BASELINE_PATH
    if not path.exists():
        return

    with open(path) as f:
        baselines = json.load(f)

    for op, data in baselines.items():
        baseline = PerformanceBaseline.from_dict(data)
        _GLOBAL_STORE._baselines[op] = baseline


def update_all_baselines() -> dict[str, PerformanceBaseline]:
    """Update baselines for all operations.

    Returns
    -------
    dict[str, PerformanceBaseline]
        Updated baselines.
    """
    baselines = {}
    for op in _GLOBAL_STORE.get_all_operations():
        baseline = _GLOBAL_STORE.update_baseline(op)
        if baseline:
            baselines[op] = baseline
    return baselines


# --------------------------------------------------------------------------- #
# Statistics and Reporting                                                     #
# --------------------------------------------------------------------------- #


def get_performance_stats(operation: str) -> dict[str, Any]:
    """Get comprehensive performance statistics for an operation.

    Parameters
    ----------
    operation : str
        The operation name.

    Returns
    -------
    dict[str, Any]
        Performance statistics.
    """
    durations = _GLOBAL_STORE.get_durations(operation)
    if not durations:
        return {"error": "No data available"}

    arr = np.array(durations)
    baseline = _GLOBAL_STORE.get_baseline(operation)

    stats: dict[str, Any] = {
        "operation": operation,
        "sample_count": len(durations),
        "mean": float(np.mean(arr)),
        "std": float(np.std(arr)),
        "min": float(np.min(arr)),
        "max": float(np.max(arr)),
        "p50": float(np.percentile(arr, 50)),
        "p95": float(np.percentile(arr, 95)),
        "p99": float(np.percentile(arr, 99)),
        "success_rate": _GLOBAL_STORE.get_success_rate(operation),
        "error_distribution": _GLOBAL_STORE.get_error_distribution(operation),
    }

    if baseline:
        stats["baseline"] = baseline.to_dict()

    # Advanced statistics if scipy available
    if SCIPY_AVAILABLE and len(durations) > 1:
        stats["skewness"] = float(stats.skew(arr))
        stats["kurtosis"] = float(stats.kurtosis(arr))

    return stats


def get_all_stats() -> dict[str, dict[str, Any]]:
    """Get performance statistics for all operations.

    Returns
    -------
    dict[str, dict[str, Any]]
        Statistics for all operations.
    """
    return {op: get_performance_stats(op) for op in _GLOBAL_STORE.get_all_operations()}


def get_critical_path(operations: list[str]) -> dict[str, Any]:
    """Analyze critical path across operations.

    Parameters
    ----------
    operations : list[str]
        List of operations in the path.

    Returns
    -------
    dict[str, Any]
        Critical path analysis.
    """
    path_stats = []
    total_mean = 0.0
    total_p95 = 0.0

    for op in operations:
        stats = get_performance_stats(op)
        if "error" not in stats:
            path_stats.append(
                {"operation": op, "mean": stats["mean"], "p95": stats["p95"]}
            )
            total_mean += stats["mean"]
            total_p95 += stats["p95"]

    return {
        "operations": path_stats,
        "total_mean_duration": total_mean,
        "total_p95_duration": total_p95,
        "bottleneck": max(path_stats, key=lambda x: x["p95"]) if path_stats else None,
    }


__all__ = [
    "METRICS_ENABLED",
    "AnomalyResult",
    "PerformanceBaseline",
    "PerformanceMetrics",
    "PerformanceTracker",
    "detect_anomalies",
    "detect_anomaly",
    "get_all_stats",
    "get_critical_path",
    "get_performance_stats",
    "get_resource_usage",
    "load_baselines",
    "save_baselines",
    "track_performance",
    "update_all_baselines",
]
