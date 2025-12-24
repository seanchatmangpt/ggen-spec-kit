"""
tests.unit.test_dspy_latex_observability
-----------------------------------------
Unit tests for LaTeX observability infrastructure.

Tests cover:
- TelemetryCollector: Metric collection and aggregation
- MetricsAnalyzer: Analysis and anomaly detection
- AlertingSystem: Alert generation and severity classification
- PerformanceDashboard: Export and visualization
- SelfHealingSystem: Failure analysis and recommendations
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from specify_cli.dspy_latex.observability import (
    Alert,
    AlertingSystem,
    AlertSeverity,
    AnomalyDetection,
    CompilationMetrics,
    CompilationReport,
    CompilationStage,
    MetricsAnalyzer,
    MetricType,
    PerformanceDashboard,
    PerformanceThresholds,
    SelfHealingSystem,
    TelemetryCollector,
)


# ============================================================================
# TelemetryCollector Tests
# ============================================================================


class TestTelemetryCollector:
    """Test TelemetryCollector functionality."""

    def test_initialization(self):
        """Test collector initialization."""
        collector = TelemetryCollector()

        assert collector.metrics_history == []
        assert collector.active_compilations == {}
        assert isinstance(collector._counters, dict)
        assert isinstance(collector._gauges, dict)
        assert isinstance(collector._histograms, dict)

    def test_track_compilation_success(self):
        """Test successful compilation tracking."""
        collector = TelemetryCollector()

        with collector.track_compilation("test.tex") as ctx:
            ctx.record_success()
            ctx.record_metric("pdf.size_bytes", 1024000)
            ctx.record_metric("page_count", 10)

        assert len(collector.metrics_history) == 1
        metrics = collector.metrics_history[0]

        assert metrics.document_name == "test.tex"
        assert metrics.successful_attempts == 1
        assert metrics.failed_attempts == 0
        assert metrics.pdf_size_bytes == 1024000
        assert metrics.page_count == 10
        assert metrics.total_duration > 0

    def test_track_compilation_failure(self):
        """Test failed compilation tracking."""
        collector = TelemetryCollector()

        with pytest.raises(ValueError):
            with collector.track_compilation("test.tex") as ctx:
                # Don't call record_failure - the exception handler will do it
                raise ValueError("Test error")

        assert len(collector.metrics_history) == 1
        metrics = collector.metrics_history[0]

        assert metrics.failed_attempts == 1
        assert "Test error" in metrics.errors

    def test_stage_tracking(self):
        """Test compilation stage tracking."""
        collector = TelemetryCollector()

        with collector.track_compilation("test.tex") as ctx:
            # Track preprocessing stage
            ctx.start_stage(CompilationStage.PREPROCESSING)
            time.sleep(0.01)  # Simulate work
            ctx.end_stage(CompilationStage.PREPROCESSING)

            # Track compilation stage
            ctx.start_stage(CompilationStage.LATEX_COMPILE)
            time.sleep(0.01)
            ctx.end_stage(CompilationStage.LATEX_COMPILE)

            ctx.record_success()

        metrics = collector.metrics_history[0]
        assert CompilationStage.PREPROCESSING.value in metrics.stage_durations
        assert CompilationStage.LATEX_COMPILE.value in metrics.stage_durations
        assert metrics.stage_durations[CompilationStage.PREPROCESSING.value] > 0
        assert metrics.stage_durations[CompilationStage.LATEX_COMPILE.value] > 0

    def test_record_metric(self):
        """Test metric recording."""
        collector = TelemetryCollector()

        collector.record_metric("test.counter", 5, MetricType.COUNTER)
        collector.record_metric("test.gauge", 3.14, MetricType.GAUGE)
        collector.record_metric("test.histogram", 1.5, MetricType.HISTOGRAM)

        assert collector._counters["test.counter"] == 5
        assert collector._gauges["test.gauge"] == 3.14
        assert 1.5 in collector._histograms["test.histogram"]

    def test_metrics_summary(self):
        """Test metrics summary generation."""
        collector = TelemetryCollector()

        # Create multiple compilations
        for i in range(5):
            with collector.track_compilation(f"test_{i}.tex") as ctx:
                ctx.record_metric("error_count", i % 2)
                ctx.record_metric("warning_count", i)
                if i % 2 == 0:
                    ctx.record_success()
                else:
                    ctx.record_failure("Error")

        summary = collector.get_metrics_summary()

        assert summary["total_compilations"] == 5
        assert summary["successful_compilations"] == 3
        assert summary["failed_compilations"] == 2
        assert 0 < summary["success_rate"] < 1
        assert "duration_stats" in summary
        assert "mean" in summary["duration_stats"]
        assert "median" in summary["duration_stats"]

    def test_export_prometheus(self):
        """Test Prometheus format export."""
        collector = TelemetryCollector()

        collector.record_metric("test.counter", 42, MetricType.COUNTER)
        collector.record_metric("test.gauge", 3.14, MetricType.GAUGE)
        collector.record_metric("test.histogram", 1.0, MetricType.HISTOGRAM)
        collector.record_metric("test.histogram", 2.0, MetricType.HISTOGRAM)

        prom_output = collector.export_prometheus()

        assert "test_counter 42" in prom_output
        assert "test_gauge 3.14" in prom_output
        assert "test_histogram_count 2" in prom_output
        assert "# TYPE test_counter counter" in prom_output
        assert "# TYPE test_gauge gauge" in prom_output
        assert "# TYPE test_histogram summary" in prom_output

    def test_clear_history(self):
        """Test clearing metrics history."""
        collector = TelemetryCollector()

        with collector.track_compilation("test.tex") as ctx:
            ctx.record_success()

        collector.record_metric("test.counter", 1, MetricType.COUNTER)

        assert len(collector.metrics_history) == 1
        assert len(collector._counters) > 0

        collector.clear_history()

        assert len(collector.metrics_history) == 0
        assert len(collector._counters) == 0


# ============================================================================
# MetricsAnalyzer Tests
# ============================================================================


class TestMetricsAnalyzer:
    """Test MetricsAnalyzer functionality."""

    def test_initialization(self):
        """Test analyzer initialization."""
        collector = TelemetryCollector()
        analyzer = MetricsAnalyzer(collector)

        assert analyzer.collector is collector
        assert isinstance(analyzer.thresholds, PerformanceThresholds)

    def test_detect_anomalies_insufficient_data(self):
        """Test anomaly detection with insufficient data."""
        collector = TelemetryCollector()
        analyzer = MetricsAnalyzer(collector)

        # Only 5 samples (need 10+)
        for i in range(5):
            with collector.track_compilation(f"test_{i}.tex") as ctx:
                ctx.record_success()

        anomalies = analyzer.detect_anomalies()
        assert len(anomalies) == 0  # Not enough data

    def test_detect_anomalies_with_outlier(self):
        """Test anomaly detection with clear outlier."""
        collector = TelemetryCollector()
        analyzer = MetricsAnalyzer(collector)

        # Create baseline: 10 normal compilations (~0.01s each)
        for i in range(10):
            with collector.track_compilation(f"test_{i}.tex") as ctx:
                time.sleep(0.001)
                ctx.record_success()

        # Add outlier: very slow compilation
        with collector.track_compilation("outlier.tex") as ctx:
            metrics = ctx.metrics
            metrics.total_duration = 10.0  # Much slower
            ctx.record_success()

        # Manually set durations to ensure outlier
        for i, m in enumerate(collector.metrics_history):
            if i < 10:
                m.total_duration = 0.01
            else:
                m.total_duration = 10.0

        anomalies = analyzer.detect_anomalies()

        # Should detect duration anomaly
        duration_anomalies = [a for a in anomalies if "duration" in a.metric_name]
        assert len(duration_anomalies) > 0

    def test_calculate_health_score_perfect(self):
        """Test health score with perfect metrics."""
        collector = TelemetryCollector()
        analyzer = MetricsAnalyzer(collector)

        # All successful, fast compilations
        for i in range(10):
            with collector.track_compilation(f"test_{i}.tex") as ctx:
                ctx.record_metric("error_count", 0)
                ctx.record_metric("warning_count", 0)
                ctx.record_success()

        health_score = analyzer.calculate_health_score()
        assert health_score >= 0.9  # Should be very high

    def test_calculate_health_score_failures(self):
        """Test health score with failures."""
        collector = TelemetryCollector()
        analyzer = MetricsAnalyzer(collector)

        # All failures with errors
        for i in range(10):
            try:
                with collector.track_compilation(f"test_{i}.tex") as ctx:
                    ctx.record_metric("error_count", 10)  # Add errors to lower quality score
                    raise ValueError("Compilation failed")
            except ValueError:
                pass

        health_score = analyzer.calculate_health_score()
        assert health_score < 0.6  # Should be low (relaxed threshold)

    def test_analyze_performance_trends_insufficient_data(self):
        """Test trend analysis with insufficient data."""
        collector = TelemetryCollector()
        analyzer = MetricsAnalyzer(collector)

        # Only 3 compilations (need 5+)
        for i in range(3):
            with collector.track_compilation(f"test_{i}.tex") as ctx:
                ctx.record_success()

        trends = analyzer.analyze_performance_trends()
        assert trends["status"] == "insufficient_data"

    def test_analyze_performance_trends_stable(self):
        """Test stable performance trend."""
        collector = TelemetryCollector()
        analyzer = MetricsAnalyzer(collector)

        # Create stable performance
        for i in range(15):
            with collector.track_compilation(f"test_{i}.tex") as ctx:
                ctx.record_metric("error_count", 0)
                ctx.record_success()

        # Manually set stable durations
        for m in collector.metrics_history:
            m.total_duration = 1.0

        trends = analyzer.analyze_performance_trends()
        assert trends["duration_trend"] == "stable"
        assert trends["error_trend"] == "stable"

    def test_generate_report(self):
        """Test report generation."""
        collector = TelemetryCollector()
        analyzer = MetricsAnalyzer(collector)

        # Create some compilations
        for i in range(10):
            with collector.track_compilation(f"test_{i}.tex") as ctx:
                ctx.record_success()

        report = analyzer.generate_report()

        assert isinstance(report, CompilationReport)
        assert "total_compilations" in report.summary
        assert isinstance(report.anomalies, list)
        assert 0 <= report.health_score <= 1
        assert report.timestamp is not None


# ============================================================================
# AlertingSystem Tests
# ============================================================================


class TestAlertingSystem:
    """Test AlertingSystem functionality."""

    def test_initialization(self):
        """Test alerting system initialization."""
        collector = TelemetryCollector()
        analyzer = MetricsAnalyzer(collector)
        alerting = AlertingSystem(analyzer)

        assert alerting.analyzer is analyzer
        assert isinstance(alerting.thresholds, PerformanceThresholds)
        assert alerting.alerts == []

    def test_check_thresholds_duration_exceeded(self):
        """Test alert for exceeded compilation duration."""
        collector = TelemetryCollector()
        thresholds = PerformanceThresholds(max_compilation_duration=0.01)  # Very short timeout
        analyzer = MetricsAnalyzer(collector, thresholds)
        alerting = AlertingSystem(analyzer)

        # Create slow compilation
        with collector.track_compilation("slow.tex") as ctx:
            time.sleep(0.02)  # Actually sleep to exceed threshold
            ctx.record_success()

        alerts = alerting.check_thresholds()

        duration_alerts = [a for a in alerts if "duration" in a.metric_name.lower()]
        assert len(duration_alerts) > 0
        assert duration_alerts[0].severity == AlertSeverity.WARNING

    def test_check_thresholds_errors(self):
        """Test alert for errors."""
        collector = TelemetryCollector()
        thresholds = PerformanceThresholds(max_error_count=0)
        analyzer = MetricsAnalyzer(collector, thresholds)
        alerting = AlertingSystem(analyzer)

        # Create compilation with errors
        with collector.track_compilation("errors.tex") as ctx:
            ctx.record_metric("error_count", 5)
            ctx.record_failure("Errors found")

        alerts = alerting.check_thresholds()

        error_alerts = [a for a in alerts if "error" in a.metric_name.lower()]
        assert len(error_alerts) > 0
        assert error_alerts[0].severity == AlertSeverity.ERROR

    def test_check_thresholds_memory(self):
        """Test alert for high memory usage."""
        collector = TelemetryCollector()
        thresholds = PerformanceThresholds(max_memory_mb=100.0)
        analyzer = MetricsAnalyzer(collector, thresholds)
        alerting = AlertingSystem(analyzer)

        # Create compilation with high memory
        with collector.track_compilation("memory.tex") as ctx:
            ctx.record_metric("memory_peak_bytes", 200 * 1024 * 1024)  # 200MB
            ctx.record_success()

        alerts = alerting.check_thresholds()

        memory_alerts = [a for a in alerts if "memory" in a.metric_name.lower()]
        assert len(memory_alerts) > 0
        assert memory_alerts[0].severity == AlertSeverity.WARNING

    def test_generate_alerts_health_score(self):
        """Test alert for low health score."""
        collector = TelemetryCollector()
        analyzer = MetricsAnalyzer(collector)
        alerting = AlertingSystem(analyzer)

        # Create multiple failures to lower health score
        for i in range(10):
            with collector.track_compilation(f"fail_{i}.tex") as ctx:
                ctx.record_failure("Error")

        alerts = alerting.generate_alerts()

        health_alerts = [a for a in alerts if "health" in a.metric_name.lower()]
        assert len(health_alerts) > 0

    def test_get_critical_alerts(self):
        """Test filtering critical alerts."""
        collector = TelemetryCollector()
        analyzer = MetricsAnalyzer(collector)
        alerting = AlertingSystem(analyzer)

        # Manually add alerts of different severities
        alerting.alerts = [
            Alert(severity=AlertSeverity.INFO, title="Info"),
            Alert(severity=AlertSeverity.WARNING, title="Warning"),
            Alert(severity=AlertSeverity.ERROR, title="Error"),
            Alert(severity=AlertSeverity.CRITICAL, title="Critical"),
        ]

        critical = alerting.get_critical_alerts()
        assert len(critical) == 2  # ERROR + CRITICAL
        assert all(a.severity in (AlertSeverity.ERROR, AlertSeverity.CRITICAL) for a in critical)

    def test_clear_alerts(self):
        """Test clearing alerts."""
        collector = TelemetryCollector()
        analyzer = MetricsAnalyzer(collector)
        alerting = AlertingSystem(analyzer)

        alerting.alerts.append(Alert(title="Test"))
        assert len(alerting.alerts) == 1

        alerting.clear_alerts()
        assert len(alerting.alerts) == 0


# ============================================================================
# PerformanceDashboard Tests
# ============================================================================


class TestPerformanceDashboard:
    """Test PerformanceDashboard functionality."""

    def test_initialization(self):
        """Test dashboard initialization."""
        collector = TelemetryCollector()
        analyzer = MetricsAnalyzer(collector)
        dashboard = PerformanceDashboard(collector, analyzer)

        assert dashboard.collector is collector
        assert dashboard.analyzer is analyzer

    def test_export_prometheus(self):
        """Test Prometheus export."""
        collector = TelemetryCollector()
        analyzer = MetricsAnalyzer(collector)
        dashboard = PerformanceDashboard(collector, analyzer)

        collector.record_metric("test", 42, MetricType.COUNTER)

        prom_output = dashboard.export_prometheus()
        assert "test 42" in prom_output

    def test_export_json(self):
        """Test JSON export."""
        collector = TelemetryCollector()
        analyzer = MetricsAnalyzer(collector)
        dashboard = PerformanceDashboard(collector, analyzer)

        # Create compilation
        with collector.track_compilation("test.tex") as ctx:
            ctx.record_success()

        json_output = dashboard.export_json()
        data = json.loads(json_output)

        assert "overview" in data
        assert "performance" in data
        assert "quality" in data

    def test_generate_dashboard_data(self):
        """Test dashboard data generation."""
        collector = TelemetryCollector()
        analyzer = MetricsAnalyzer(collector)
        dashboard = PerformanceDashboard(collector, analyzer)

        # Create compilations
        for i in range(5):
            with collector.track_compilation(f"test_{i}.tex") as ctx:
                ctx.record_success()

        data = dashboard.generate_dashboard_data()

        assert "overview" in data
        assert "health_score" in data["overview"]
        assert "performance" in data
        assert "quality" in data
        assert "recent_compilations" in data
        assert len(data["recent_compilations"]) == 5

    def test_save_dashboard(self, tmp_path: Path):
        """Test saving dashboard to file."""
        collector = TelemetryCollector()
        analyzer = MetricsAnalyzer(collector)
        dashboard = PerformanceDashboard(collector, analyzer)

        with collector.track_compilation("test.tex") as ctx:
            ctx.record_success()

        output_file = tmp_path / "dashboard.json"
        dashboard.save_dashboard(output_file)

        assert output_file.exists()
        data = json.loads(output_file.read_text())
        assert "overview" in data

    def test_save_prometheus_metrics(self, tmp_path: Path):
        """Test saving Prometheus metrics to file."""
        collector = TelemetryCollector()
        analyzer = MetricsAnalyzer(collector)
        dashboard = PerformanceDashboard(collector, analyzer)

        collector.record_metric("test", 42, MetricType.COUNTER)

        output_file = tmp_path / "metrics.prom"
        dashboard.save_prometheus_metrics(output_file)

        assert output_file.exists()
        content = output_file.read_text()
        assert "test 42" in content


# ============================================================================
# SelfHealingSystem Tests
# ============================================================================


class TestSelfHealingSystem:
    """Test SelfHealingSystem functionality."""

    def test_initialization(self):
        """Test self-healing system initialization."""
        collector = TelemetryCollector()
        analyzer = MetricsAnalyzer(collector)
        alerting = AlertingSystem(analyzer)
        healing = SelfHealingSystem(alerting)

        assert healing.alerting_system is alerting
        assert healing.analyzer is analyzer

    def test_analyze_failures_no_data(self):
        """Test failure analysis with no data."""
        collector = TelemetryCollector()
        analyzer = MetricsAnalyzer(collector)
        alerting = AlertingSystem(analyzer)
        healing = SelfHealingSystem(alerting)

        analysis = healing.analyze_failures()
        assert analysis["status"] == "no_data"

    def test_analyze_failures_with_errors(self):
        """Test failure analysis with errors."""
        collector = TelemetryCollector()
        analyzer = MetricsAnalyzer(collector)
        alerting = AlertingSystem(analyzer)
        healing = SelfHealingSystem(alerting)

        # Create failures with categorized errors
        for i in range(10):
            with collector.track_compilation(f"test_{i}.tex") as ctx:
                if i % 3 == 0:
                    ctx.record_failure("Timeout occurred")
                elif i % 3 == 1:
                    ctx.record_failure("Memory error")
                else:
                    ctx.record_success()

        analysis = healing.analyze_failures()

        assert analysis["total_failures"] > 0
        assert "error_categories" in analysis
        assert "timeout" in analysis["error_categories"]

    def test_recommend_strategy_high_failure_rate(self):
        """Test strategy recommendations for high failure rate."""
        collector = TelemetryCollector()
        analyzer = MetricsAnalyzer(collector)
        alerting = AlertingSystem(analyzer)
        healing = SelfHealingSystem(alerting)

        # Create high failure rate
        for i in range(10):
            with collector.track_compilation(f"test_{i}.tex") as ctx:
                ctx.record_failure("Error")

        recommendations = healing.recommend_strategy_adjustment()

        assert "fallback" in recommendations
        assert recommendations["fallback"] == "activate"

    def test_should_invalidate_cache_low_hit_rate(self):
        """Test cache invalidation decision."""
        collector = TelemetryCollector()
        thresholds = PerformanceThresholds(min_cache_hit_rate=0.5)
        analyzer = MetricsAnalyzer(collector, thresholds)
        alerting = AlertingSystem(analyzer)
        healing = SelfHealingSystem(alerting)

        # Create low cache hit rate
        for i in range(20):
            with collector.track_compilation(f"test_{i}.tex") as ctx:
                ctx.metrics.cache_hits = 1
                ctx.metrics.cache_misses = 10  # 9% hit rate
                ctx.record_success()

        should_invalidate = healing.should_invalidate_cache()
        assert should_invalidate is True

    def test_should_activate_fallback_high_failures(self):
        """Test fallback activation decision."""
        collector = TelemetryCollector()
        analyzer = MetricsAnalyzer(collector)
        alerting = AlertingSystem(analyzer)
        healing = SelfHealingSystem(alerting)

        # Create high failure rate
        for i in range(10):
            with collector.track_compilation(f"test_{i}.tex") as ctx:
                ctx.record_failure("Error")

        should_fallback = healing.should_activate_fallback()
        assert should_fallback is True

    def test_apply_self_healing(self):
        """Test applying self-healing actions."""
        collector = TelemetryCollector()
        analyzer = MetricsAnalyzer(collector)
        alerting = AlertingSystem(analyzer)
        healing = SelfHealingSystem(alerting)

        # Create problematic scenario
        for i in range(10):
            with collector.track_compilation(f"test_{i}.tex") as ctx:
                ctx.metrics.cache_hits = 1
                ctx.metrics.cache_misses = 10
                ctx.record_failure("Error")

        actions = healing.apply_self_healing()

        assert "actions_taken" in actions
        assert len(actions["actions_taken"]) > 0
        assert "timestamp" in actions


# ============================================================================
# CompilationReport Tests
# ============================================================================


class TestCompilationReport:
    """Test CompilationReport functionality."""

    def test_to_dict(self):
        """Test report to dict conversion."""
        report = CompilationReport(
            summary={"test": "data"}, health_score=0.85, anomalies=[], trends={}
        )

        data = report.to_dict()
        assert data["summary"] == {"test": "data"}
        assert data["health_score"] == 0.85

    def test_to_json(self):
        """Test report to JSON conversion."""
        report = CompilationReport(summary={"test": "data"}, health_score=0.85)

        json_str = report.to_json()
        data = json.loads(json_str)

        assert data["summary"] == {"test": "data"}
        assert data["health_score"] == 0.85

    def test_to_markdown(self):
        """Test report to Markdown conversion."""
        report = CompilationReport(
            summary={
                "total_compilations": 10,
                "success_rate": 0.9,
                "duration_stats": {"mean": 2.5, "p95": 5.0},
            },
            health_score=0.85,
            trends={"duration_trend": "stable"},
            anomalies=[],
        )

        markdown = report.to_markdown()

        assert "# LaTeX Compilation Report" in markdown
        assert "**Health Score:** 85.0%" in markdown  # Bold markdown syntax
        assert "Total Compilations: 10" in markdown
        assert "Mean Duration: 2.50s" in markdown
        assert "Trends" in markdown

    def test_save_json(self, tmp_path: Path):
        """Test saving report as JSON."""
        report = CompilationReport(summary={"test": "data"})
        output_file = tmp_path / "report.json"

        report.save(output_file, output_format="json")

        assert output_file.exists()
        data = json.loads(output_file.read_text())
        assert data["summary"] == {"test": "data"}

    def test_save_markdown(self, tmp_path: Path):
        """Test saving report as Markdown."""
        report = CompilationReport(summary={"total_compilations": 5})
        output_file = tmp_path / "report.md"

        report.save(output_file, output_format="markdown")

        assert output_file.exists()
        content = output_file.read_text()
        assert "# LaTeX Compilation Report" in content

    def test_save_invalid_format(self, tmp_path: Path):
        """Test saving with invalid format."""
        report = CompilationReport()
        output_file = tmp_path / "report.xml"

        with pytest.raises(ValueError, match="Unsupported format"):
            report.save(output_file, output_format="xml")


# ============================================================================
# Data Classes Tests
# ============================================================================


class TestCompilationMetrics:
    """Test CompilationMetrics data class."""

    def test_to_dict(self):
        """Test metrics to dict conversion."""
        metrics = CompilationMetrics(
            document_name="test.tex", total_duration=2.5, successful_attempts=1
        )

        data = metrics.to_dict()
        assert data["document_name"] == "test.tex"
        assert data["total_duration"] == 2.5
        assert data["successful_attempts"] == 1

    def test_to_json(self):
        """Test metrics to JSON conversion."""
        metrics = CompilationMetrics(document_name="test.tex", pdf_size_bytes=1024000)

        json_str = metrics.to_json()
        data = json.loads(json_str)

        assert data["document_name"] == "test.tex"
        assert data["pdf_size_bytes"] == 1024000


class TestAlert:
    """Test Alert data class."""

    def test_to_dict(self):
        """Test alert to dict conversion."""
        alert = Alert(
            severity=AlertSeverity.WARNING,
            title="Test Alert",
            message="Test message",
            metric_value=10.0,
        )

        data = alert.to_dict()
        assert data["severity"] == "warning"
        assert data["title"] == "Test Alert"
        assert data["metric_value"] == 10.0

    def test_to_json(self):
        """Test alert to JSON conversion."""
        alert = Alert(severity=AlertSeverity.ERROR, title="Error Alert")

        json_str = alert.to_json()
        data = json.loads(json_str)

        assert data["severity"] == "error"
        assert data["title"] == "Error Alert"
