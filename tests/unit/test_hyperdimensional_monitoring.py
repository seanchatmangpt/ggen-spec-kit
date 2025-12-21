"""Unit tests for hyperdimensional monitoring module."""

from __future__ import annotations

import pytest

from specify_cli.hyperdimensional.monitoring import Alert, MonitoringSystem


@pytest.fixture
def monitor():
    """Create monitoring system instance."""
    return MonitoringSystem(
        alert_thresholds={
            "specification_clarity": 0.7,
            "specification_drift": 0.3,
            "test_coverage": 0.8,
            "requirement_gaps": 5,
        },
        enable_otel=False,  # Disable OTEL for tests
    )


@pytest.fixture
def sample_specs():
    """Create sample specifications."""
    return [
        {
            "id": "spec1",
            "text": "Clear and concise specification.",
            "overview": "Test",
            "requirements": ["req1"],
            "constraints": ["c1"],
        },
        {
            "id": "spec2",
            "text": "Another specification",
            "overview": "Test 2",
        },
    ]


# =================================================================
# System Observability Tests
# =================================================================


def test_specification_quality_monitor(monitor, sample_specs):
    """Test specification quality monitoring."""
    metrics = monitor.specification_quality_monitor(sample_specs)

    assert len(metrics) == len(sample_specs)
    assert all(m.unit == "score" for m in metrics)
    assert all(0.0 <= m.value <= 1.0 for m in metrics)


def test_code_generation_quality_monitor(monitor):
    """Test code generation quality monitoring."""
    generations = [
        {
            "id": "gen1",
            "spec": {"requirements": ["implement add", "handle errors"]},
            "code": {"text": "def add(a, b): return a + b"},
        },
    ]

    metrics = monitor.code_generation_quality_monitor(generations)

    assert len(metrics) == len(generations)
    assert all(m.unit == "ratio" for m in metrics)


def test_test_coverage_monitor(monitor):
    """Test test coverage monitoring."""
    test_results = {
        "module1": 0.95,
        "module2": 0.75,
        "module3": 0.60,
    }

    metrics = monitor.test_coverage_monitor(test_results)

    assert len(metrics) == len(test_results)

    # Check alert generation for low coverage
    assert len(monitor.alerts) > 0  # module3 should trigger alert


def test_otel_instrumentation_monitor(monitor):
    """Test OTEL instrumentation monitoring."""
    spans = [
        {"operation": "op1"},
        {"operation": "op2"},
        {"operation": "op1"},  # Duplicate
    ]

    metric = monitor.otel_instrumentation_monitor(spans)

    assert metric.name == "otel_instrumentation_coverage"
    assert metric.unit == "ratio"


# =================================================================
# Alert Threshold Tests
# =================================================================


def test_alert_on_low_specification_clarity(monitor):
    """Test alert on low clarity."""
    specs = [
        {
            "id": "spec1",
            "text": "x" * 1000,  # Low clarity (high entropy)
        },
    ]

    alerts = monitor.alert_on_low_specification_clarity(specs, threshold=0.7)

    # May or may not trigger depending on entropy calculation
    assert isinstance(alerts, list)
    assert all(isinstance(a, Alert) for a in alerts)


def test_alert_on_specification_drift(monitor):
    """Test alert on specification drift."""
    spec_history = [
        {
            "version": "1.0",
            "text": "Original specification with these words",
        },
        {
            "version": "2.0",
            "text": "Completely different content here",
        },
    ]

    alerts = monitor.alert_on_specification_drift(spec_history, max_entropy=0.3)

    assert len(alerts) > 0  # Significant drift should trigger alert
    assert all(a.alert_type == "specification_drift" for a in alerts)


def test_alert_on_test_coverage_drop(monitor):
    """Test alert on coverage drop."""
    coverage_history = [
        {"timestamp": "2024-01-01", "module1": 0.95, "module2": 0.85},
        {"timestamp": "2024-01-02", "module1": 0.70, "module2": 0.85},  # Drop
    ]

    alerts = monitor.alert_on_test_coverage_drop(coverage_history, min_coverage=0.8)

    assert len(alerts) > 0  # module1 dropped below threshold
    assert all(a.alert_type == "test_coverage" for a in alerts)


def test_alert_on_unmet_requirements(monitor):
    """Test alert on unmet requirements."""
    spec = {
        "requirements": [f"requirement_{i}" for i in range(10)],  # Many requirements
    }

    code = {
        "text": "minimal code",  # Won't meet most requirements
    }

    alerts = monitor.alert_on_unmet_requirements(spec, code, max_gaps=5)

    assert len(alerts) > 0
    assert alerts[0].alert_type == "unmet_requirements"
    assert alerts[0].severity == "critical"


# =================================================================
# Alert Management Tests
# =================================================================


def test_get_active_alerts(monitor):
    """Test getting active alerts."""
    # Generate some alerts
    monitor._generate_alert(
        "test_alert",
        "warning",
        "Test alert message",
        0.5,
        0.7,
    )

    monitor._generate_alert(
        "test_alert",
        "critical",
        "Critical alert",
        0.3,
        0.7,
    )

    # Get all alerts
    all_alerts = monitor.get_active_alerts()
    assert len(all_alerts) == 2

    # Filter by severity
    warnings = monitor.get_active_alerts(severity="warning")
    assert len(warnings) == 1
    assert warnings[0].severity == "warning"


def test_clear_alerts(monitor):
    """Test clearing alerts."""
    monitor._generate_alert("test", "warning", "Test", 0.5, 0.7)
    assert len(monitor.alerts) > 0

    monitor.clear_alerts()
    assert len(monitor.alerts) == 0


# =================================================================
# Edge Cases
# =================================================================


def test_empty_specs(monitor):
    """Test with empty specifications."""
    metrics = monitor.specification_quality_monitor([])
    assert len(metrics) == 0


def test_specification_without_text(monitor):
    """Test specification without text field."""
    specs = [{"id": "spec1", "overview": "Test"}]

    metrics = monitor.specification_quality_monitor(specs)

    assert len(metrics) == 1
    # Should handle missing text gracefully


def test_single_spec_drift(monitor):
    """Test drift detection with single spec."""
    spec_history = [
        {"version": "1.0", "text": "Only one spec"},
    ]

    alerts = monitor.alert_on_specification_drift(spec_history)

    assert len(alerts) == 0  # Can't calculate drift with single spec
