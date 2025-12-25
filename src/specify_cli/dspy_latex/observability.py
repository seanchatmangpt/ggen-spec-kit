"""
specify_cli.dspy_latex.observability
------------------------------------
Comprehensive observability infrastructure for LaTeX-to-PDF compilation engine.

This module provides enterprise-grade observability with:

* **OpenTelemetry Integration**: Full distributed tracing support
* **10+ Operational Metrics**: Performance, quality, and health metrics
* **Self-Aware Monitoring**: Real-time anomaly detection and alerting
* **Self-Healing**: Automatic strategy adjustment based on failure patterns
* **Dashboard Integration**: Prometheus export and visualization support

Components
----------
TelemetryCollector : Aggregate metrics and telemetry data
MetricsAnalyzer : Perform analysis and anomaly detection
AlertingSystem : Generate alerts for performance and failure issues
PerformanceDashboard : Metrics visualization and export
CompilationReport : Comprehensive execution reports

Example
-------
    from specify_cli.dspy_latex.observability import (
        TelemetryCollector,
        MetricsAnalyzer,
        CompilationReport
    )

    # Initialize telemetry
    collector = TelemetryCollector()

    # Track compilation
    with collector.track_compilation("document.tex") as context:
        # ... compilation logic ...
        context.record_metric("compilation.time", 2.5)
        context.record_metric("pdf.size_bytes", 1024000)

    # Analyze and report
    analyzer = MetricsAnalyzer(collector)
    report = analyzer.generate_report()
    print(report.to_json())

Metrics Collected
-----------------
Compilation Metrics:
    - latex.compilation.duration_seconds (P50/P95/P99)
    - latex.compilation.attempts_total
    - latex.compilation.success_total
    - latex.compilation.failure_total
    - latex.compilation.stage.duration_seconds (per stage)

Quality Metrics:
    - latex.pdf.size_bytes
    - latex.pdf.page_count
    - latex.error.count
    - latex.warning.count
    - latex.document.complexity_score

Performance Metrics:
    - latex.cache.hit_rate
    - latex.cache.miss_total
    - latex.optimization.effectiveness_ratio
    - latex.memory.usage_bytes
    - latex.cpu.usage_percent

Health Metrics:
    - latex.health.error_rate
    - latex.health.availability_percent
    - latex.strategy.effectiveness_score
    - latex.strategy.fallback_total
"""

from __future__ import annotations

import json
import logging
import statistics
import time
import uuid
from collections import defaultdict
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

from specify_cli.core.telemetry import (
    OTEL_AVAILABLE,
    metric_counter,
    metric_histogram,
    record_exception,
    span,
)

logger = logging.getLogger(__name__)


# ============================================================================
# Enums and Constants
# ============================================================================


class CompilationStage(str, Enum):
    """Compilation pipeline stages."""

    PREPROCESSING = "preprocessing"
    LATEX_COMPILE = "latex_compile"
    BIBTEX = "bibtex"
    INDEX = "index"
    POSTPROCESSING = "postprocessing"
    OPTIMIZATION = "optimization"
    VALIDATION = "validation"


class AlertSeverity(str, Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MetricType(str, Enum):
    """Metric types for classification."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


# ============================================================================
# Data Classes
# ============================================================================


@dataclass
class CompilationMetrics:
    """Metrics collected during a single compilation run."""

    # Identifiers
    compilation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    document_name: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    # Timing metrics (seconds)
    total_duration: float = 0.0
    stage_durations: dict[str, float] = field(default_factory=dict)
    preprocessing_duration: float = 0.0
    compilation_duration: float = 0.0
    postprocessing_duration: float = 0.0

    # Compilation attempts
    total_attempts: int = 0
    successful_attempts: int = 0
    failed_attempts: int = 0

    # Quality metrics
    pdf_size_bytes: int = 0
    page_count: int = 0
    error_count: int = 0
    warning_count: int = 0
    document_complexity: float = 0.0

    # Performance metrics
    cache_hits: int = 0
    cache_misses: int = 0
    memory_peak_bytes: int = 0
    cpu_usage_percent: float = 0.0

    # Strategy metrics
    strategy_used: str = ""
    fallback_triggered: bool = False
    optimization_applied: bool = False
    optimization_effectiveness: float = 0.0

    # Error tracking
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    # Additional metadata
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert metrics to dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert metrics to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class Alert:
    """Alert generated by the monitoring system."""

    alert_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    severity: AlertSeverity = AlertSeverity.INFO
    title: str = ""
    message: str = ""
    metric_name: str = ""
    metric_value: float = 0.0
    threshold: float = 0.0
    context: dict[str, Any] = field(default_factory=dict)
    recommended_action: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert alert to dictionary."""
        data = asdict(self)
        data["severity"] = self.severity.value
        return data

    def to_json(self) -> str:
        """Convert alert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class AnomalyDetection:
    """Anomaly detection result."""

    is_anomaly: bool = False
    metric_name: str = ""
    current_value: float = 0.0
    expected_range: tuple[float, float] = (0.0, 0.0)
    deviation_score: float = 0.0
    confidence: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class PerformanceThresholds:
    """Performance thresholds for quality gates."""

    # Timing thresholds (seconds)
    max_compilation_duration: float = 30.0
    max_stage_duration: float = 10.0
    target_p95_duration: float = 5.0
    target_p99_duration: float = 10.0

    # Quality thresholds
    max_error_count: int = 0
    max_warning_count: int = 10
    min_cache_hit_rate: float = 0.5

    # Performance thresholds
    max_memory_mb: float = 500.0
    max_cpu_percent: float = 80.0
    min_optimization_effectiveness: float = 0.7

    # Reliability thresholds
    min_success_rate: float = 0.95
    max_failure_rate: float = 0.05


# ============================================================================
# Telemetry Collector
# ============================================================================


class TelemetryCollector:
    """
    Aggregate and collect telemetry data for LaTeX compilation.

    This class provides the core telemetry collection infrastructure, integrating
    with OpenTelemetry for distributed tracing and metrics export.

    Attributes
    ----------
    metrics_history : list[CompilationMetrics]
        Historical compilation metrics
    active_compilations : dict[str, CompilationMetrics]
        Currently active compilation sessions

    Methods
    -------
    track_compilation(document_name: str) -> CompilationContext
        Context manager for tracking a compilation session
    record_metric(name: str, value: float, labels: dict[str, str])
        Record a metric value
    get_metrics_summary() -> dict[str, Any]
        Get summary statistics of collected metrics
    export_prometheus() -> str
        Export metrics in Prometheus format
    """

    def __init__(self) -> None:
        """Initialize telemetry collector."""
        self.metrics_history: list[CompilationMetrics] = []
        self.active_compilations: dict[str, CompilationMetrics] = {}
        self._counters: dict[str, int] = defaultdict(int)
        self._gauges: dict[str, float] = defaultdict(float)
        self._histograms: dict[str, list[float]] = defaultdict(list)

        # Initialize OpenTelemetry metrics if available
        if OTEL_AVAILABLE:
            self._init_otel_metrics()

        logger.info("TelemetryCollector initialized (OTEL_AVAILABLE=%s)", OTEL_AVAILABLE)

    def _init_otel_metrics(self) -> None:
        """Initialize OpenTelemetry metrics."""
        # Counters
        self.compilation_attempts = metric_counter("latex.compilation.attempts_total")
        self.compilation_success = metric_counter("latex.compilation.success_total")
        self.compilation_failure = metric_counter("latex.compilation.failure_total")
        self.cache_hits = metric_counter("latex.cache.hit_total")
        self.cache_misses = metric_counter("latex.cache.miss_total")
        self.fallback_triggered = metric_counter("latex.strategy.fallback_total")

        # Histograms
        self.compilation_duration = metric_histogram("latex.compilation.duration_seconds", "s")
        self.stage_duration = metric_histogram("latex.compilation.stage.duration_seconds", "s")
        self.pdf_size = metric_histogram("latex.pdf.size_bytes", "bytes")
        self.memory_usage = metric_histogram("latex.memory.usage_bytes", "bytes")

    @contextmanager
    def track_compilation(self, document_name: str) -> Iterator[CompilationContext]:
        """
        Track a compilation session with automatic metrics collection.

        Parameters
        ----------
        document_name : str
            Name of the document being compiled

        Yields
        ------
        CompilationContext
            Context manager for recording compilation metrics

        Example
        -------
        >>> collector = TelemetryCollector()
        >>> with collector.track_compilation("paper.tex") as ctx:
        ...     # Perform compilation
        ...     ctx.record_metric("pdf.size_bytes", 1024000)
        """
        metrics = CompilationMetrics(document_name=document_name)
        start_time = time.perf_counter()

        # Create OpenTelemetry span
        with span(
            "latex.compilation",
            document_name=document_name,
            compilation_id=metrics.compilation_id,
        ) as current_span:
            context = CompilationContext(
                metrics=metrics, collector=self, span=current_span, start_time=start_time
            )

            self.active_compilations[metrics.compilation_id] = metrics

            try:
                yield context
            except Exception as e:
                metrics.failed_attempts += 1
                metrics.errors.append(str(e))
                record_exception(e, attributes={"document_name": document_name})
                if OTEL_AVAILABLE:
                    self.compilation_failure(1, {"document": document_name})
                raise
            finally:
                # Calculate total duration
                metrics.total_duration = time.perf_counter() - start_time

                # Record final metrics
                if OTEL_AVAILABLE:
                    self.compilation_duration(metrics.total_duration, {"document": document_name})
                    if metrics.successful_attempts > 0:
                        self.compilation_success(1, {"document": document_name})

                # Store in history
                self.metrics_history.append(metrics)
                del self.active_compilations[metrics.compilation_id]

                logger.info(
                    "Compilation completed: %s (duration=%.2fs, success=%d, errors=%d)",
                    document_name,
                    metrics.total_duration,
                    metrics.successful_attempts,
                    len(metrics.errors),
                )

    def record_metric(
        self, name: str, value: float, metric_type: MetricType = MetricType.GAUGE
    ) -> None:
        """
        Record a metric value.

        Parameters
        ----------
        name : str
            Metric name
        value : float
            Metric value
        metric_type : MetricType
            Type of metric (counter, gauge, histogram)
        """
        if metric_type == MetricType.COUNTER:
            self._counters[name] += int(value)
        elif metric_type == MetricType.GAUGE:
            self._gauges[name] = value
        elif metric_type == MetricType.HISTOGRAM:
            self._histograms[name].append(value)

    def get_metrics_summary(self) -> dict[str, Any]:
        """
        Get summary statistics of collected metrics.

        Returns
        -------
        dict[str, Any]
            Summary statistics including counts, rates, and percentiles
        """
        if not self.metrics_history:
            return {"status": "no_data"}

        total_compilations = len(self.metrics_history)
        successful = sum(1 for m in self.metrics_history if m.successful_attempts > 0)
        failed = sum(1 for m in self.metrics_history if m.failed_attempts > 0)

        durations = [m.total_duration for m in self.metrics_history]
        errors = [m.error_count for m in self.metrics_history]
        warnings = [m.warning_count for m in self.metrics_history]

        return {
            "total_compilations": total_compilations,
            "successful_compilations": successful,
            "failed_compilations": failed,
            "success_rate": successful / total_compilations if total_compilations > 0 else 0.0,
            "duration_stats": {
                "mean": statistics.mean(durations) if durations else 0.0,
                "median": statistics.median(durations) if durations else 0.0,
                "p95": statistics.quantiles(durations, n=20)[18] if len(durations) > 1 else 0.0,
                "p99": statistics.quantiles(durations, n=100)[98] if len(durations) > 1 else 0.0,
                "min": min(durations) if durations else 0.0,
                "max": max(durations) if durations else 0.0,
            },
            "error_stats": {
                "mean": statistics.mean(errors) if errors else 0.0,
                "total": sum(errors),
            },
            "warning_stats": {
                "mean": statistics.mean(warnings) if warnings else 0.0,
                "total": sum(warnings),
            },
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
        }

    def export_prometheus(self) -> str:
        """
        Export metrics in Prometheus format.

        Returns
        -------
        str
            Metrics in Prometheus exposition format

        Example
        -------
        >>> collector = TelemetryCollector()
        >>> print(collector.export_prometheus())
        # HELP latex_compilation_total Total number of compilations
        # TYPE latex_compilation_total counter
        latex_compilation_total 42
        """
        lines = []

        # Export counters
        for name, value in self._counters.items():
            metric_name = name.replace(".", "_")
            lines.append(f"# HELP {metric_name} Counter metric")
            lines.append(f"# TYPE {metric_name} counter")
            lines.append(f"{metric_name} {value}")
            lines.append("")

        # Export gauges
        for name, value in self._gauges.items():
            metric_name = name.replace(".", "_")
            lines.append(f"# HELP {metric_name} Gauge metric")
            lines.append(f"# TYPE {metric_name} gauge")
            lines.append(f"{metric_name} {value}")
            lines.append("")

        # Export histogram summaries
        for name, values in self._histograms.items():
            if not values:
                continue

            metric_name = name.replace(".", "_")
            lines.append(f"# HELP {metric_name} Histogram metric")
            lines.append(f"# TYPE {metric_name} summary")

            sorted_values = sorted(values)
            count = len(sorted_values)
            total = sum(sorted_values)

            # Quantiles
            if count > 1:
                p50 = sorted_values[int(count * 0.5)]
                p95 = sorted_values[int(count * 0.95)]
                p99 = sorted_values[int(count * 0.99)]

                lines.append(f'{metric_name}{{quantile="0.5"}} {p50}')
                lines.append(f'{metric_name}{{quantile="0.95"}} {p95}')
                lines.append(f'{metric_name}{{quantile="0.99"}} {p99}')

            lines.append(f"{metric_name}_sum {total}")
            lines.append(f"{metric_name}_count {count}")
            lines.append("")

        return "\n".join(lines)

    def clear_history(self) -> None:
        """Clear metrics history."""
        self.metrics_history.clear()
        self._counters.clear()
        self._gauges.clear()
        self._histograms.clear()
        logger.info("Metrics history cleared")


# ============================================================================
# Compilation Context
# ============================================================================


class CompilationContext:
    """
    Context manager for tracking compilation metrics within a session.

    This class provides a convenient interface for recording metrics during
    compilation, with automatic integration to the parent TelemetryCollector.

    Attributes
    ----------
    metrics : CompilationMetrics
        Metrics being collected
    collector : TelemetryCollector
        Parent telemetry collector
    span : Any
        OpenTelemetry span (if available)
    start_time : float
        Session start time
    """

    def __init__(
        self,
        metrics: CompilationMetrics,
        collector: TelemetryCollector,
        span: Any,
        start_time: float,
    ) -> None:
        """Initialize compilation context."""
        self.metrics = metrics
        self.collector = collector
        self.span = span
        self.start_time = start_time
        self._stage_start_times: dict[str, float] = {}

    def start_stage(self, stage: CompilationStage) -> None:
        """
        Start tracking a compilation stage.

        Parameters
        ----------
        stage : CompilationStage
            Stage to track
        """
        self._stage_start_times[stage.value] = time.perf_counter()
        logger.debug("Started stage: %s", stage.value)

    def end_stage(self, stage: CompilationStage) -> None:
        """
        End tracking a compilation stage.

        Parameters
        ----------
        stage : CompilationStage
            Stage to end
        """
        if stage.value in self._stage_start_times:
            duration = time.perf_counter() - self._stage_start_times[stage.value]
            self.metrics.stage_durations[stage.value] = duration

            if OTEL_AVAILABLE and hasattr(self.collector, "stage_duration"):
                self.collector.stage_duration(duration, {"stage": stage.value})

            logger.debug("Completed stage: %s (duration=%.2fs)", stage.value, duration)

    def record_metric(self, name: str, value: float) -> None:
        """
        Record a metric value.

        Parameters
        ----------
        name : str
            Metric name
        value : float
            Metric value
        """
        # Store in metrics metadata
        self.metrics.metadata[name] = value

        # Record in span attributes
        if OTEL_AVAILABLE and self.span.is_recording():
            self.span.set_attribute(name, value)

        # Update specific metric fields
        if name == "pdf.size_bytes":
            self.metrics.pdf_size_bytes = int(value)
        elif name == "page_count":
            self.metrics.page_count = int(value)
        elif name == "error_count":
            self.metrics.error_count = int(value)
        elif name == "warning_count":
            self.metrics.warning_count = int(value)
        elif name == "memory_peak_bytes":
            self.metrics.memory_peak_bytes = int(value)
        elif name == "cpu_usage_percent":
            self.metrics.cpu_usage_percent = value

    def record_success(self) -> None:
        """Record successful compilation."""
        self.metrics.successful_attempts += 1
        self.metrics.total_attempts += 1

    def record_failure(self, error: str) -> None:
        """
        Record compilation failure.

        Parameters
        ----------
        error : str
            Error message
        """
        self.metrics.failed_attempts += 1
        self.metrics.total_attempts += 1
        self.metrics.errors.append(error)

    def record_warning(self, warning: str) -> None:
        """
        Record compilation warning.

        Parameters
        ----------
        warning : str
            Warning message
        """
        self.metrics.warnings.append(warning)
        self.metrics.warning_count += 1


# ============================================================================
# Metrics Analyzer
# ============================================================================


class MetricsAnalyzer:
    """
    Perform analysis and anomaly detection on collected metrics.

    This class provides advanced analytics including statistical analysis,
    anomaly detection, and pattern recognition for self-aware monitoring.

    Attributes
    ----------
    collector : TelemetryCollector
        Telemetry collector to analyze
    thresholds : PerformanceThresholds
        Performance thresholds for analysis

    Methods
    -------
    detect_anomalies() -> list[AnomalyDetection]
        Detect anomalies in metrics
    calculate_health_score() -> float
        Calculate overall system health score
    analyze_performance_trends() -> dict[str, Any]
        Analyze performance trends over time
    """

    def __init__(
        self,
        collector: TelemetryCollector,
        thresholds: PerformanceThresholds | None = None,
    ) -> None:
        """Initialize metrics analyzer."""
        self.collector = collector
        self.thresholds = thresholds or PerformanceThresholds()
        logger.info("MetricsAnalyzer initialized")

    def detect_anomalies(self) -> list[AnomalyDetection]:
        """
        Detect anomalies in compilation metrics using statistical methods.

        Returns
        -------
        list[AnomalyDetection]
            List of detected anomalies

        Example
        -------
        >>> analyzer = MetricsAnalyzer(collector)
        >>> anomalies = analyzer.detect_anomalies()
        >>> for anomaly in anomalies:
        ...     print(f"Anomaly detected: {anomaly.metric_name}")
        """
        anomalies = []

        if len(self.collector.metrics_history) < 10:
            logger.debug("Insufficient data for anomaly detection (need at least 10 samples)")
            return anomalies

        # Analyze compilation duration
        durations = [m.total_duration for m in self.collector.metrics_history]
        duration_anomalies = self._detect_statistical_anomalies(
            "compilation.duration", durations
        )
        anomalies.extend(duration_anomalies)

        # Analyze error rates
        error_counts = [m.error_count for m in self.collector.metrics_history]
        error_anomalies = self._detect_statistical_anomalies("error.count", error_counts)
        anomalies.extend(error_anomalies)

        # Analyze memory usage
        memory_usage = [
            m.memory_peak_bytes
            for m in self.collector.metrics_history
            if m.memory_peak_bytes > 0
        ]
        if memory_usage:
            memory_anomalies = self._detect_statistical_anomalies("memory.peak_bytes", memory_usage)
            anomalies.extend(memory_anomalies)

        logger.info("Detected %d anomalies", len(anomalies))
        return anomalies

    def _detect_statistical_anomalies(
        self, metric_name: str, values: list[float], z_threshold: float = 3.0
    ) -> list[AnomalyDetection]:
        """
        Detect anomalies using z-score method.

        Parameters
        ----------
        metric_name : str
            Name of metric
        values : list[float]
            Metric values
        z_threshold : float
            Z-score threshold for anomaly detection

        Returns
        -------
        list[AnomalyDetection]
            Detected anomalies
        """
        if len(values) < 2:
            return []

        mean_val = statistics.mean(values)
        stdev_val = statistics.stdev(values) if len(values) > 1 else 0.0

        if stdev_val == 0:
            return []

        anomalies = []
        for value in values[-5:]:  # Check last 5 values
            z_score = abs((value - mean_val) / stdev_val)

            if z_score > z_threshold:
                anomaly = AnomalyDetection(
                    is_anomaly=True,
                    metric_name=metric_name,
                    current_value=value,
                    expected_range=(mean_val - 2 * stdev_val, mean_val + 2 * stdev_val),
                    deviation_score=z_score,
                    confidence=min(z_score / z_threshold, 1.0),
                )
                anomalies.append(anomaly)

        return anomalies

    def calculate_health_score(self) -> float:
        """
        Calculate overall system health score (0.0 - 1.0).

        Returns
        -------
        float
            Health score between 0 and 1
        """
        if not self.collector.metrics_history:
            return 1.0

        # Calculate component scores
        success_score = self._calculate_success_rate_score()
        performance_score = self._calculate_performance_score()
        quality_score = self._calculate_quality_score()

        # Weighted average
        health_score = (success_score * 0.4 + performance_score * 0.3 + quality_score * 0.3)

        logger.info(
            "Health score calculated: %.2f (success=%.2f, perf=%.2f, quality=%.2f)",
            health_score,
            success_score,
            performance_score,
            quality_score,
        )

        return health_score

    def _calculate_success_rate_score(self) -> float:
        """Calculate success rate score."""
        total = len(self.collector.metrics_history)
        successful = sum(1 for m in self.collector.metrics_history if m.successful_attempts > 0)

        if total == 0:
            return 1.0

        success_rate = successful / total
        # Map to 0-1 scale with threshold at 0.95
        return float(min(success_rate / self.thresholds.min_success_rate, 1.0))

    def _calculate_performance_score(self) -> float:
        """Calculate performance score based on duration."""
        durations = [m.total_duration for m in self.collector.metrics_history]

        if not durations:
            return 1.0

        # Use P95 as performance indicator
        if len(durations) > 1:
            p95_duration = statistics.quantiles(durations, n=20)[18]
        else:
            p95_duration = durations[0]

        # Score based on threshold
        if p95_duration <= self.thresholds.target_p95_duration:
            return 1.0
        if p95_duration <= self.thresholds.max_compilation_duration:
            # Linear degradation
            ratio = (self.thresholds.max_compilation_duration - p95_duration) / (
                self.thresholds.max_compilation_duration - self.thresholds.target_p95_duration
            )
            return max(ratio, 0.0)
        return 0.0

    def _calculate_quality_score(self) -> float:
        """Calculate quality score based on errors and warnings."""
        recent_metrics = self.collector.metrics_history[-10:]  # Last 10 compilations

        if not recent_metrics:
            return 1.0

        avg_errors = statistics.mean([m.error_count for m in recent_metrics])
        avg_warnings = statistics.mean([m.warning_count for m in recent_metrics])

        # Perfect score if no errors
        if avg_errors == 0:
            error_score = 1.0
        elif self.thresholds.max_error_count == 0:
            # Strict mode: any errors = 0 score
            error_score = 0.0
        else:
            # Degrade based on error threshold
            error_score = max(1.0 - (avg_errors / self.thresholds.max_error_count), 0.0)

        # Warning score
        if avg_warnings <= self.thresholds.max_warning_count:
            warning_score = 1.0
        else:
            warning_score = max(
                1.0 - (avg_warnings - self.thresholds.max_warning_count) / 10.0, 0.0
            )

        return (error_score * 0.7 + warning_score * 0.3)

    def analyze_performance_trends(self) -> dict[str, Any]:
        """
        Analyze performance trends over time.

        Returns
        -------
        dict[str, Any]
            Performance trend analysis
        """
        if len(self.collector.metrics_history) < 5:
            return {"status": "insufficient_data", "message": "Need at least 5 compilations"}

        recent = self.collector.metrics_history[-10:]
        older = self.collector.metrics_history[-20:-10] if len(self.collector.metrics_history) >= 20 else []

        return {
            "duration_trend": self._calculate_trend(
                [m.total_duration for m in older], [m.total_duration for m in recent]
            ),
            "error_trend": self._calculate_trend(
                [m.error_count for m in older], [m.error_count for m in recent]
            ),
            "memory_trend": self._calculate_trend(
                [m.memory_peak_bytes for m in older if m.memory_peak_bytes > 0],
                [m.memory_peak_bytes for m in recent if m.memory_peak_bytes > 0],
            ),
        }


    def _calculate_trend(self, older_values: list[float], recent_values: list[float]) -> str:
        """Calculate trend direction."""
        if not older_values or not recent_values:
            return "stable"

        older_avg = statistics.mean(older_values)
        recent_avg = statistics.mean(recent_values)

        if older_avg == 0:
            return "stable"

        change_pct = ((recent_avg - older_avg) / older_avg) * 100

        if change_pct > 10:
            return "degrading"
        if change_pct < -10:
            return "improving"
        return "stable"

    def generate_report(self) -> CompilationReport:
        """
        Generate comprehensive compilation report.

        Returns
        -------
        CompilationReport
            Comprehensive report with metrics and analysis
        """
        summary = self.collector.get_metrics_summary()
        anomalies = self.detect_anomalies()
        health_score = self.calculate_health_score()
        trends = self.analyze_performance_trends()

        return CompilationReport(
            summary=summary,
            anomalies=[a.to_dict() for a in anomalies],  # type: ignore[misc]
            health_score=health_score,
            trends=trends,
            timestamp=datetime.now(UTC).isoformat(),
        )


# ============================================================================
# Alerting System
# ============================================================================


class AlertingSystem:
    """
    Generate alerts for performance and failure issues.

    This class monitors metrics and generates alerts when thresholds are exceeded
    or anomalies are detected, enabling proactive issue resolution.

    Attributes
    ----------
    analyzer : MetricsAnalyzer
        Metrics analyzer for detecting issues
    thresholds : PerformanceThresholds
        Performance thresholds for alerting
    alerts : list[Alert]
        Generated alerts

    Methods
    -------
    check_thresholds() -> list[Alert]
        Check metrics against thresholds
    generate_alerts() -> list[Alert]
        Generate alerts based on current state
    """

    def __init__(
        self, analyzer: MetricsAnalyzer, thresholds: PerformanceThresholds | None = None
    ) -> None:
        """Initialize alerting system."""
        self.analyzer = analyzer
        self.thresholds = thresholds or analyzer.thresholds
        self.alerts: list[Alert] = []
        logger.info("AlertingSystem initialized")

    def check_thresholds(self) -> list[Alert]:
        """
        Check metrics against performance thresholds.

        Returns
        -------
        list[Alert]
            Generated alerts
        """
        alerts = []

        if not self.analyzer.collector.metrics_history:
            return alerts

        recent_metrics = self.analyzer.collector.metrics_history[-1]

        # Check compilation duration
        if recent_metrics.total_duration > self.thresholds.max_compilation_duration:
            alert = Alert(
                severity=AlertSeverity.WARNING,
                title="Compilation Duration Exceeded",
                message=f"Compilation took {recent_metrics.total_duration:.2f}s, "
                f"exceeding threshold of {self.thresholds.max_compilation_duration}s",
                metric_name="compilation.duration",
                metric_value=recent_metrics.total_duration,
                threshold=self.thresholds.max_compilation_duration,
                recommended_action="Consider optimizing document or increasing timeout",
            )
            alerts.append(alert)

        # Check error count
        if recent_metrics.error_count > self.thresholds.max_error_count:
            alert = Alert(
                severity=AlertSeverity.ERROR,
                title="Compilation Errors Detected",
                message=f"Found {recent_metrics.error_count} errors, "
                f"exceeding threshold of {self.thresholds.max_error_count}",
                metric_name="error.count",
                metric_value=float(recent_metrics.error_count),
                threshold=float(self.thresholds.max_error_count),
                recommended_action="Review compilation logs and fix LaTeX errors",
                context={"errors": recent_metrics.errors[:5]},  # First 5 errors
            )
            alerts.append(alert)

        # Check memory usage
        if recent_metrics.memory_peak_bytes > self.thresholds.max_memory_mb * 1024 * 1024:
            alert = Alert(
                severity=AlertSeverity.WARNING,
                title="High Memory Usage",
                message=f"Peak memory usage: {recent_metrics.memory_peak_bytes / 1024 / 1024:.1f}MB, "
                f"exceeding threshold of {self.thresholds.max_memory_mb}MB",
                metric_name="memory.peak_bytes",
                metric_value=float(recent_metrics.memory_peak_bytes),
                threshold=self.thresholds.max_memory_mb * 1024 * 1024,
                recommended_action="Consider reducing document complexity or increasing memory limits",
            )
            alerts.append(alert)

        # Check cache hit rate
        total_cache_ops = recent_metrics.cache_hits + recent_metrics.cache_misses
        if total_cache_ops > 0:
            cache_hit_rate = recent_metrics.cache_hits / total_cache_ops
            if cache_hit_rate < self.thresholds.min_cache_hit_rate:
                alert = Alert(
                    severity=AlertSeverity.INFO,
                    title="Low Cache Hit Rate",
                    message=f"Cache hit rate: {cache_hit_rate:.1%}, "
                    f"below threshold of {self.thresholds.min_cache_hit_rate:.1%}",
                    metric_name="cache.hit_rate",
                    metric_value=cache_hit_rate,
                    threshold=self.thresholds.min_cache_hit_rate,
                    recommended_action="Review cache invalidation strategy",
                )
                alerts.append(alert)

        self.alerts.extend(alerts)
        return alerts

    def generate_alerts(self) -> list[Alert]:
        """
        Generate alerts based on anomalies and thresholds.

        Returns
        -------
        list[Alert]
            All generated alerts
        """
        alerts = []

        # Check thresholds
        threshold_alerts = self.check_thresholds()
        alerts.extend(threshold_alerts)

        # Check for anomalies
        anomalies = self.analyzer.detect_anomalies()
        for anomaly in anomalies:
            if anomaly.is_anomaly:
                alert = Alert(
                    severity=AlertSeverity.WARNING,
                    title=f"Anomaly Detected: {anomaly.metric_name}",
                    message=f"Metric {anomaly.metric_name} shows anomalous behavior. "
                    f"Current value: {anomaly.current_value:.2f}, "
                    f"Expected range: [{anomaly.expected_range[0]:.2f}, {anomaly.expected_range[1]:.2f}]",
                    metric_name=anomaly.metric_name,
                    metric_value=anomaly.current_value,
                    threshold=anomaly.expected_range[1],
                    context={
                        "deviation_score": anomaly.deviation_score,
                        "confidence": anomaly.confidence,
                    },
                    recommended_action="Investigate recent changes or environmental factors",
                )
                alerts.append(alert)

        # Check health score
        health_score = self.analyzer.calculate_health_score()
        if health_score < 0.7:
            severity = AlertSeverity.CRITICAL if health_score < 0.5 else AlertSeverity.ERROR
            alert = Alert(
                severity=severity,
                title="Low System Health Score",
                message=f"Overall health score: {health_score:.1%}. System performance degraded.",
                metric_name="system.health_score",
                metric_value=health_score,
                threshold=0.7,
                recommended_action="Review recent compilation failures and performance metrics",
            )
            alerts.append(alert)

        self.alerts.extend(alerts)
        logger.info("Generated %d alerts", len(alerts))
        return alerts

    def get_critical_alerts(self) -> list[Alert]:
        """Get only critical and error alerts."""
        return [
            a for a in self.alerts if a.severity in (AlertSeverity.CRITICAL, AlertSeverity.ERROR)
        ]

    def clear_alerts(self) -> None:
        """Clear all alerts."""
        self.alerts.clear()


# ============================================================================
# Performance Dashboard
# ============================================================================


class PerformanceDashboard:
    """
    Metrics visualization and export for dashboards.

    This class provides visualization and export capabilities for metrics,
    supporting Prometheus format and structured JSON output.

    Attributes
    ----------
    collector : TelemetryCollector
        Telemetry collector
    analyzer : MetricsAnalyzer
        Metrics analyzer

    Methods
    -------
    export_prometheus() -> str
        Export metrics in Prometheus format
    export_json() -> str
        Export metrics as JSON
    generate_dashboard_data() -> dict[str, Any]
        Generate dashboard data structure
    """

    def __init__(self, collector: TelemetryCollector, analyzer: MetricsAnalyzer) -> None:
        """Initialize performance dashboard."""
        self.collector = collector
        self.analyzer = analyzer
        logger.info("PerformanceDashboard initialized")

    def export_prometheus(self) -> str:
        """
        Export metrics in Prometheus format.

        Returns
        -------
        str
            Prometheus exposition format
        """
        return self.collector.export_prometheus()

    def export_json(self) -> str:
        """
        Export metrics as JSON.

        Returns
        -------
        str
            JSON formatted metrics
        """
        data = self.generate_dashboard_data()
        return json.dumps(data, indent=2)

    def generate_dashboard_data(self) -> dict[str, Any]:
        """
        Generate comprehensive dashboard data.

        Returns
        -------
        dict[str, Any]
            Dashboard data structure
        """
        summary = self.collector.get_metrics_summary()
        health_score = self.analyzer.calculate_health_score()
        trends = self.analyzer.analyze_performance_trends()

        # Recent compilations
        recent_compilations = [
            {
                "id": m.compilation_id,
                "document": m.document_name,
                "duration": m.total_duration,
                "success": m.successful_attempts > 0,
                "errors": m.error_count,
                "timestamp": m.timestamp,
            }
            for m in self.collector.metrics_history[-20:]
        ]

        return {
            "overview": {
                "health_score": health_score,
                "total_compilations": summary.get("total_compilations", 0),
                "success_rate": summary.get("success_rate", 0.0),
            },
            "performance": {
                "duration_stats": summary.get("duration_stats", {}),
                "trends": trends,
            },
            "quality": {
                "error_stats": summary.get("error_stats", {}),
                "warning_stats": summary.get("warning_stats", {}),
            },
            "recent_compilations": recent_compilations,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    def save_dashboard(self, output_path: Path) -> None:
        """
        Save dashboard data to file.

        Parameters
        ----------
        output_path : Path
            Output file path
        """
        data = self.generate_dashboard_data()
        output_path.write_text(json.dumps(data, indent=2))
        logger.info("Dashboard saved to %s", output_path)

    def save_prometheus_metrics(self, output_path: Path) -> None:
        """
        Save Prometheus metrics to file.

        Parameters
        ----------
        output_path : Path
            Output file path
        """
        metrics = self.export_prometheus()
        output_path.write_text(metrics)
        logger.info("Prometheus metrics saved to %s", output_path)


# ============================================================================
# Compilation Report
# ============================================================================


@dataclass
class CompilationReport:
    """
    Comprehensive compilation execution report.

    Attributes
    ----------
    summary : dict[str, Any]
        Summary statistics
    anomalies : list[dict[str, Any]]
        Detected anomalies
    health_score : float
        Overall health score
    trends : dict[str, Any]
        Performance trends
    timestamp : str
        Report generation timestamp
    """

    summary: dict[str, Any] = field(default_factory=dict)
    anomalies: list[dict[str, Any]] = field(default_factory=list)
    health_score: float = 1.0
    trends: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Convert report to dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert report to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    def to_markdown(self) -> str:
        """
        Convert report to Markdown format.

        Returns
        -------
        str
            Markdown formatted report
        """
        lines = [
            "# LaTeX Compilation Report",
            "",
            f"**Generated:** {self.timestamp}",
            f"**Health Score:** {self.health_score:.1%}",
            "",
            "## Summary",
            "",
        ]

        # Add summary stats
        if "total_compilations" in self.summary:
            lines.extend(
                [
                    f"- Total Compilations: {self.summary['total_compilations']}",
                    f"- Success Rate: {self.summary.get('success_rate', 0):.1%}",
                    f"- Failed Compilations: {self.summary.get('failed_compilations', 0)}",
                    "",
                ]
            )

        # Add duration stats
        if "duration_stats" in self.summary:
            stats = self.summary["duration_stats"]
            lines.extend(
                [
                    "## Performance",
                    "",
                    f"- Mean Duration: {stats.get('mean', 0):.2f}s",
                    f"- Median Duration: {stats.get('median', 0):.2f}s",
                    f"- P95 Duration: {stats.get('p95', 0):.2f}s",
                    f"- P99 Duration: {stats.get('p99', 0):.2f}s",
                    "",
                ]
            )

        # Add trends
        if self.trends:
            lines.extend(["## Trends", ""])
            for metric, trend in self.trends.items():
                lines.append(f"- {metric}: {trend}")
            lines.append("")

        # Add anomalies
        if self.anomalies:
            lines.extend(["## Anomalies Detected", ""])
            for anomaly in self.anomalies:
                lines.append(f"- {anomaly.get('metric_name', 'Unknown')}: {anomaly.get('deviation_score', 0):.2f} standard deviations")
            lines.append("")

        return "\n".join(lines)

    def save(self, output_path: Path, output_format: str = "json") -> None:
        """
        Save report to file.

        Parameters
        ----------
        output_path : Path
            Output file path
        output_format : str
            Output format ('json' or 'markdown')
        """
        if output_format == "json":
            content = self.to_json()
        elif output_format == "markdown":
            content = self.to_markdown()
        else:
            msg = f"Unsupported format: {output_format}"
            raise ValueError(msg)

        output_path.write_text(content)
        logger.info("Report saved to %s (format=%s)", output_path, output_format)


# ============================================================================
# Self-Healing System
# ============================================================================


class SelfHealingSystem:
    """
    Automatic strategy adjustment based on failure patterns and metrics.

    This class implements self-healing capabilities by monitoring metrics
    and automatically adjusting compilation strategies to improve success rates.

    Attributes
    ----------
    alerting_system : AlertingSystem
        Alerting system for monitoring
    analyzer : MetricsAnalyzer
        Metrics analyzer

    Methods
    -------
    analyze_failures() -> dict[str, Any]
        Analyze failure patterns
    recommend_strategy_adjustment() -> dict[str, str]
        Recommend strategy adjustments
    should_invalidate_cache() -> bool
        Determine if cache should be invalidated
    should_activate_fallback() -> bool
        Determine if fallback should be activated
    """

    def __init__(
        self, alerting_system: AlertingSystem, analyzer: MetricsAnalyzer | None = None
    ) -> None:
        """Initialize self-healing system."""
        self.alerting_system = alerting_system
        self.analyzer = analyzer or alerting_system.analyzer
        logger.info("SelfHealingSystem initialized")

    def analyze_failures(self) -> dict[str, Any]:
        """
        Analyze failure patterns to identify root causes.

        Returns
        -------
        dict[str, Any]
            Failure analysis results
        """
        recent_metrics = self.analyzer.collector.metrics_history[-10:]
        if not recent_metrics:
            return {"status": "no_data"}

        failed = [m for m in recent_metrics if m.failed_attempts > 0]
        failure_rate = len(failed) / len(recent_metrics)

        # Categorize errors
        error_categories: dict[str, int] = defaultdict(int)
        for metrics in failed:
            for error in metrics.errors:
                # Simple categorization based on keywords
                if "timeout" in error.lower():
                    error_categories["timeout"] += 1
                elif "memory" in error.lower():
                    error_categories["memory"] += 1
                elif "syntax" in error.lower() or "undefined" in error.lower():
                    error_categories["latex_error"] += 1
                else:
                    error_categories["other"] += 1

        return {
            "failure_rate": failure_rate,
            "total_failures": len(failed),
            "error_categories": dict(error_categories),
            "most_common_error": max(error_categories.items(), key=lambda x: x[1])[0]
            if error_categories
            else "none",
        }

    def recommend_strategy_adjustment(self) -> dict[str, str]:
        """
        Recommend strategy adjustments based on failure patterns.

        Returns
        -------
        dict[str, str]
            Recommended adjustments
        """
        failure_analysis = self.analyze_failures()

        if failure_analysis.get("status") == "no_data":
            return {"status": "no_recommendation"}

        recommendations = {}
        failure_rate = failure_analysis.get("failure_rate", 0.0)

        # High failure rate - recommend fallback
        if failure_rate > 0.3:
            recommendations["fallback"] = "activate"
            recommendations["reason"] = f"High failure rate: {failure_rate:.1%}"

        # Check error categories
        failure_analysis.get("error_categories", {})
        most_common = failure_analysis.get("most_common_error")

        if most_common == "timeout":
            recommendations["timeout_adjustment"] = "increase"
            recommendations["timeout_reason"] = "Frequent timeout errors detected"
        elif most_common == "memory":
            recommendations["memory_adjustment"] = "increase_limit"
            recommendations["memory_reason"] = "Memory exhaustion detected"
        elif most_common == "latex_error":
            recommendations["validation"] = "enable_strict"
            recommendations["validation_reason"] = "LaTeX syntax errors detected"

        return recommendations

    def should_invalidate_cache(self) -> bool:
        """
        Determine if cache should be invalidated based on effectiveness.

        Returns
        -------
        bool
            True if cache should be invalidated
        """
        recent_metrics = self.analyzer.collector.metrics_history[-20:]
        if not recent_metrics:
            return False

        # Calculate cache effectiveness
        total_hits = sum(m.cache_hits for m in recent_metrics)
        total_misses = sum(m.cache_misses for m in recent_metrics)

        if total_hits + total_misses == 0:
            return False

        hit_rate = total_hits / (total_hits + total_misses)

        # Invalidate if hit rate drops below threshold
        if hit_rate < self.analyzer.thresholds.min_cache_hit_rate:
            logger.warning("Cache hit rate low (%.1f%%), recommending invalidation", hit_rate * 100)
            return True

        return False

    def should_activate_fallback(self) -> bool:
        """
        Determine if fallback mechanism should be activated.

        Returns
        -------
        bool
            True if fallback should be activated
        """
        failure_analysis = self.analyze_failures()

        if failure_analysis.get("status") == "no_data":
            return False

        failure_rate = failure_analysis.get("failure_rate", 0.0)

        # Activate fallback if failure rate exceeds threshold
        if failure_rate > (1.0 - self.analyzer.thresholds.min_success_rate):
            logger.warning("High failure rate (%.1f%%), activating fallback", failure_rate * 100)
            return True

        # Check health score
        health_score = self.analyzer.calculate_health_score()
        if health_score < 0.5:
            logger.warning("Low health score (%.1f), activating fallback", health_score)
            return True

        return False

    def apply_self_healing(self) -> dict[str, Any]:
        """
        Apply self-healing actions based on current state.

        Returns
        -------
        dict[str, Any]
            Actions taken
        """
        actions = {"timestamp": datetime.now(UTC).isoformat(), "actions_taken": []}

        # Check if cache invalidation needed
        if self.should_invalidate_cache():
            actions["actions_taken"].append(
                {"action": "invalidate_cache", "reason": "Low cache hit rate"}
            )

        # Check if fallback needed
        if self.should_activate_fallback():
            actions["actions_taken"].append(
                {"action": "activate_fallback", "reason": "High failure rate or low health score"}
            )

        # Get strategy recommendations
        recommendations = self.recommend_strategy_adjustment()
        if recommendations.get("status") != "no_recommendation":
            actions["recommendations"] = recommendations

        logger.info("Self-healing analysis complete: %d actions", len(actions["actions_taken"]))
        return actions


# ============================================================================
# Exports
# ============================================================================


__all__ = [
    "Alert",
    "AlertSeverity",
    "AlertingSystem",
    "AnomalyDetection",
    # Context
    "CompilationContext",
    # Data Classes
    "CompilationMetrics",
    "CompilationReport",
    # Enums
    "CompilationStage",
    "MetricType",
    "MetricsAnalyzer",
    "PerformanceDashboard",
    "PerformanceThresholds",
    "SelfHealingSystem",
    # Core Classes
    "TelemetryCollector",
]
