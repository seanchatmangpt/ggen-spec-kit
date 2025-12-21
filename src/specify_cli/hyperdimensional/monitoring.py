"""
specify_cli.hyperdimensional.monitoring - Real-Time Monitoring System
====================================================================

Real-time monitoring system with system observability, alert thresholds, and quality tracking.

This module provides monitoring capabilities for:
* **System Observability**: Real-time quality tracking, code generation monitoring
* **Alert Thresholds**: Configurable alerts for quality degradation
* **Quality Tracking**: Specification clarity, test coverage, requirement gaps

Examples
--------
    >>> from specify_cli.hyperdimensional.monitoring import MonitoringSystem
    >>>
    >>> monitor = MonitoringSystem()
    >>> monitor.specification_quality_monitor(specs)
    >>> monitor.alert_on_low_specification_clarity(threshold=0.7)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import numpy as np

from specify_cli.core.telemetry import metric_counter, metric_gauge, span
from specify_cli.hyperdimensional.dashboards import MetricData

__all__ = [
    "Alert",
    "MonitoringMetrics",
    "MonitoringSystem",
]


@dataclass
class Alert:
    """Alert data structure."""

    alert_type: str
    severity: str  # "info", "warning", "critical"
    message: str
    timestamp: str
    current_value: float
    threshold: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class MonitoringMetrics:
    """Monitoring metrics collection."""

    specification_quality: float
    code_generation_quality: float
    test_coverage: float
    requirement_gaps: int
    timestamp: str
    metadata: dict[str, Any] = field(default_factory=dict)


class MonitoringSystem:
    """
    Real-time monitoring system for hyperdimensional observability.

    This class provides continuous monitoring, alerting, and quality tracking
    for specifications, code generation, and system health.

    Attributes
    ----------
    alert_thresholds : dict[str, float]
        Configurable alert thresholds for different metrics.
    enable_otel : bool
        Enable OpenTelemetry metric export.
    """

    def __init__(
        self,
        alert_thresholds: dict[str, float] | None = None,
        enable_otel: bool = True,
    ) -> None:
        """
        Initialize monitoring system.

        Parameters
        ----------
        alert_thresholds : dict[str, float], optional
            Alert thresholds for metrics.
        enable_otel : bool, optional
            Enable OTEL metrics. Default is True.
        """
        self.alert_thresholds = alert_thresholds or {
            "specification_clarity": 0.7,
            "specification_drift": 0.3,
            "test_coverage": 0.8,
            "requirement_gaps": 5,
        }
        self.enable_otel = enable_otel
        self.alerts: list[Alert] = []

        # OTEL metrics
        if enable_otel:
            self._spec_quality_gauge = metric_gauge("hyperdimensional.spec_quality")
            self._code_quality_gauge = metric_gauge("hyperdimensional.code_quality")
            self._test_coverage_gauge = metric_gauge("hyperdimensional.test_coverage")
            self._alert_counter = metric_counter("hyperdimensional.alerts")

    # =========================================================================
    # System Observability
    # =========================================================================

    def specification_quality_monitor(
        self,
        specs: list[dict[str, Any]],
    ) -> list[MetricData]:
        """
        Monitor specification quality in real-time.

        Continuously tracks specification quality metrics and generates alerts
        when quality degrades.

        Parameters
        ----------
        specs : list[dict[str, Any]]
            List of specifications to monitor.

        Returns
        -------
        list[MetricData]
            Quality metrics for each specification.
        """
        with span("monitoring.specification_quality_monitor", n_specs=len(specs)):
            metrics = []

            for idx, spec in enumerate(specs):
                # Calculate quality score
                quality_score = self._calculate_spec_quality(spec)

                # Update OTEL metrics
                if self.enable_otel:
                    self._spec_quality_gauge(quality_score)

                # Create metric
                metric = MetricData(
                    name=f"spec_quality_{spec.get('id', idx)}",
                    value=quality_score,
                    unit="score",
                    threshold=self.alert_thresholds["specification_clarity"],
                    status="ok"
                    if quality_score >= 0.7
                    else "warning"
                    if quality_score >= 0.5
                    else "critical",
                    metadata={
                        "spec_id": spec.get("id", idx),
                        "completeness": self._check_completeness(spec),
                        "clarity": self._check_clarity(spec),
                    },
                )

                metrics.append(metric)

                # Generate alerts if needed
                if quality_score < self.alert_thresholds["specification_clarity"]:
                    self._generate_alert(
                        "specification_quality",
                        "warning" if quality_score >= 0.5 else "critical",
                        f"Specification quality below threshold: {quality_score:.2f}",
                        quality_score,
                        self.alert_thresholds["specification_clarity"],
                    )

            return metrics

    def _calculate_spec_quality(self, spec: dict[str, Any]) -> float:
        """Calculate overall specification quality score."""
        completeness = self._check_completeness(spec)
        clarity = self._check_clarity(spec)
        consistency = self._check_consistency(spec)

        return (completeness + clarity + consistency) / 3.0

    def _check_completeness(self, spec: dict[str, Any]) -> float:
        """Check specification completeness."""
        required_sections = {
            "overview",
            "requirements",
            "constraints",
            "acceptance_criteria",
        }
        present_sections = set(spec.keys())
        return len(present_sections & required_sections) / len(required_sections)

    def _check_clarity(self, spec: dict[str, Any]) -> float:
        """Check specification clarity based on entropy."""
        import re
        from collections import Counter

        text = spec.get("text", "")
        if not text:
            return 0.0

        # Tokenize
        tokens = re.findall(r"\w+", text.lower())
        if not tokens:
            return 0.0

        # Calculate entropy
        total = len(tokens)
        counts = Counter(tokens)
        probs = [count / total for count in counts.values()]
        entropy = -sum(p * np.log2(p) for p in probs if p > 0)

        # Normalize (max entropy for English text ~= 10)
        normalized_entropy = min(entropy / 10.0, 1.0)

        # Lower entropy = clearer (more structured)
        return 1.0 - normalized_entropy

    def _check_consistency(self, spec: dict[str, Any]) -> float:
        """Check specification consistency."""
        # Placeholder: check for contradictions, ambiguities
        # In production, use NLP techniques
        return 0.8

    def code_generation_quality_monitor(
        self,
        generations: list[dict[str, Any]],
    ) -> list[MetricData]:
        """
        Monitor code generation quality in real-time.

        Tracks fidelity of generated code to specifications.

        Parameters
        ----------
        generations : list[dict[str, Any]]
            List of code generations with specs.

        Returns
        -------
        list[MetricData]
            Quality metrics for each generation.
        """
        with span("monitoring.code_generation_quality_monitor", n_generations=len(generations)):
            metrics = []

            for idx, gen in enumerate(generations):
                # Calculate fidelity
                fidelity = self._calculate_fidelity(gen)

                # Update OTEL metrics
                if self.enable_otel:
                    self._code_quality_gauge(fidelity)

                # Create metric
                metric = MetricData(
                    name=f"code_fidelity_{gen.get('id', idx)}",
                    value=fidelity,
                    unit="ratio",
                    threshold=0.8,
                    status="ok"
                    if fidelity >= 0.8
                    else "warning"
                    if fidelity >= 0.6
                    else "critical",
                    metadata={
                        "generation_id": gen.get("id", idx),
                        "spec_id": gen.get("spec_id"),
                    },
                )

                metrics.append(metric)

            return metrics

    def _calculate_fidelity(self, generation: dict[str, Any]) -> float:
        """Calculate code generation fidelity."""
        spec = generation.get("spec", {})
        code = generation.get("code", {})

        if not spec or not code:
            return 0.0

        # Check requirement coverage
        requirements = spec.get("requirements", [])
        if isinstance(requirements, str):
            requirements = [r.strip() for r in requirements.split("\n") if r.strip()]

        code_text = code.get("text", "")
        implemented = sum(
            1
            for req in requirements
            if any(keyword in code_text.lower() for keyword in req.lower().split())
        )

        return implemented / len(requirements) if requirements else 0.0

    def test_coverage_monitor(
        self,
        test_results: dict[str, float],
    ) -> list[MetricData]:
        """
        Monitor test coverage in real-time.

        Tracks test coverage and alerts on coverage drops.

        Parameters
        ----------
        test_results : dict[str, float]
            Module names mapped to coverage percentages.

        Returns
        -------
        list[MetricData]
            Coverage metrics for each module.
        """
        with span("monitoring.test_coverage_monitor", n_modules=len(test_results)):
            metrics = []

            for module_name, coverage in test_results.items():
                # Update OTEL metrics
                if self.enable_otel:
                    self._test_coverage_gauge(coverage)

                # Create metric
                metric = MetricData(
                    name=f"test_coverage_{module_name}",
                    value=coverage,
                    unit="ratio",
                    threshold=self.alert_thresholds["test_coverage"],
                    status="ok"
                    if coverage >= 0.8
                    else "warning"
                    if coverage >= 0.6
                    else "critical",
                    metadata={"module": module_name},
                )

                metrics.append(metric)

                # Generate alerts
                if coverage < self.alert_thresholds["test_coverage"]:
                    self._generate_alert(
                        "test_coverage",
                        "warning" if coverage >= 0.6 else "critical",
                        f"Test coverage below threshold for {module_name}: {coverage:.2f}",
                        coverage,
                        self.alert_thresholds["test_coverage"],
                    )

            return metrics

    def otel_instrumentation_monitor(
        self,
        spans: list[dict[str, Any]],
    ) -> MetricData:
        """
        Monitor OpenTelemetry instrumentation completeness.

        Tracks what percentage of operations are instrumented with OTEL.

        Parameters
        ----------
        spans : list[dict[str, Any]]
            OTEL span data.

        Returns
        -------
        MetricData
            Instrumentation coverage metric.
        """
        with span("monitoring.otel_instrumentation_monitor", n_spans=len(spans)):
            # Analyze span coverage
            instrumented_operations = len({s.get("operation") for s in spans})
            total_operations = 100  # Expected total (adjust based on system)

            coverage = instrumented_operations / total_operations

            return MetricData(
                name="otel_instrumentation_coverage",
                value=coverage,
                unit="ratio",
                threshold=0.9,
                status="ok" if coverage >= 0.9 else "warning",
                metadata={
                    "instrumented_operations": instrumented_operations,
                    "total_operations": total_operations,
                },
            )

    # =========================================================================
    # Alert Thresholds
    # =========================================================================

    def alert_on_low_specification_clarity(
        self,
        specs: list[dict[str, Any]],
        threshold: float = 0.7,
    ) -> list[Alert]:
        """
        Alert when specification clarity drops below threshold.

        Parameters
        ----------
        specs : list[dict[str, Any]]
            Specifications to check.
        threshold : float, optional
            Clarity threshold. Default is 0.7.

        Returns
        -------
        list[Alert]
            Generated alerts.
        """
        with span("monitoring.alert_on_low_clarity", threshold=threshold):
            alerts = []

            for spec in specs:
                clarity = self._check_clarity(spec)

                if clarity < threshold:
                    alert = self._generate_alert(
                        "specification_clarity",
                        "warning" if clarity >= 0.5 else "critical",
                        f"Specification clarity below threshold: {clarity:.2f}",
                        clarity,
                        threshold,
                        metadata={"spec_id": spec.get("id")},
                    )
                    alerts.append(alert)

            return alerts

    def alert_on_specification_drift(
        self,
        spec_history: list[dict[str, Any]],
        max_entropy: float = 0.3,
    ) -> list[Alert]:
        """
        Alert when specification drifts significantly between versions.

        Parameters
        ----------
        spec_history : list[dict[str, Any]]
            Specification version history.
        max_entropy : float, optional
            Maximum allowed drift entropy. Default is 0.3.

        Returns
        -------
        list[Alert]
            Generated alerts for significant drift.
        """
        with span("monitoring.alert_on_spec_drift", max_entropy=max_entropy):
            alerts = []

            if len(spec_history) < 2:
                return alerts

            # Compare consecutive versions
            for i in range(1, len(spec_history)):
                prev_spec = spec_history[i - 1]
                curr_spec = spec_history[i]

                # Calculate drift
                drift = self._calculate_drift(prev_spec, curr_spec)

                if drift > max_entropy:
                    alert = self._generate_alert(
                        "specification_drift",
                        "warning" if drift < max_entropy * 2 else "critical",
                        f"Specification drift detected: {drift:.2f}",
                        drift,
                        max_entropy,
                        metadata={
                            "from_version": prev_spec.get("version"),
                            "to_version": curr_spec.get("version"),
                        },
                    )
                    alerts.append(alert)

            return alerts

    def _calculate_drift(self, spec1: dict[str, Any], spec2: dict[str, Any]) -> float:
        """Calculate drift between two specifications."""
        # Simple text-based drift calculation
        text1 = spec1.get("text", "")
        text2 = spec2.get("text", "")

        if not text1 or not text2:
            return 0.0

        # Calculate Jaccard similarity of words
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 and not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        similarity = intersection / union if union > 0 else 0.0
        return 1.0 - similarity

    def alert_on_test_coverage_drop(
        self,
        coverage_history: list[dict[str, float]],
        min_coverage: float = 0.8,
    ) -> list[Alert]:
        """
        Alert when test coverage drops below minimum.

        Parameters
        ----------
        coverage_history : list[dict[str, float]]
            Coverage history with timestamps.
        min_coverage : float, optional
            Minimum required coverage. Default is 0.8.

        Returns
        -------
        list[Alert]
            Generated alerts for coverage drops.
        """
        with span("monitoring.alert_on_coverage_drop", min_coverage=min_coverage):
            alerts = []

            if not coverage_history:
                return alerts

            latest_coverage = coverage_history[-1]

            for module, coverage in latest_coverage.items():
                if module == "timestamp":
                    continue

                if coverage < min_coverage:
                    alert = self._generate_alert(
                        "test_coverage",
                        "warning" if coverage >= 0.6 else "critical",
                        f"Test coverage dropped for {module}: {coverage:.2f}",
                        coverage,
                        min_coverage,
                        metadata={"module": module},
                    )
                    alerts.append(alert)

            return alerts

    def alert_on_unmet_requirements(
        self,
        spec: dict[str, Any],
        code: dict[str, Any],
        max_gaps: int = 5,
    ) -> list[Alert]:
        """
        Alert when too many requirements are unmet.

        Parameters
        ----------
        spec : dict[str, Any]
            Specification with requirements.
        code : dict[str, Any]
            Generated code.
        max_gaps : int, optional
            Maximum allowed unmet requirements. Default is 5.

        Returns
        -------
        list[Alert]
            Generated alerts for requirement gaps.
        """
        with span("monitoring.alert_on_unmet_requirements", max_gaps=max_gaps):
            requirements = spec.get("requirements", [])
            if isinstance(requirements, str):
                requirements = [r.strip() for r in requirements.split("\n") if r.strip()]

            code_text = code.get("text", "")

            unmet = []
            for req in requirements:
                keywords = req.lower().split()
                if not any(keyword in code_text.lower() for keyword in keywords):
                    unmet.append(req)

            gaps = len(unmet)

            if gaps > max_gaps:
                return [
                    self._generate_alert(
                        "unmet_requirements",
                        "critical",
                        f"Too many unmet requirements: {gaps}",
                        gaps,
                        max_gaps,
                        metadata={"unmet_requirements": unmet},
                    )
                ]

            return []

    def _generate_alert(
        self,
        alert_type: str,
        severity: str,
        message: str,
        current_value: float,
        threshold: float,
        metadata: dict[str, Any] | None = None,
    ) -> Alert:
        """Generate and record an alert."""
        alert = Alert(
            alert_type=alert_type,
            severity=severity,
            message=message,
            timestamp=datetime.now().isoformat(),
            current_value=current_value,
            threshold=threshold,
            metadata=metadata or {},
        )

        self.alerts.append(alert)

        # Update OTEL counter
        if self.enable_otel:
            self._alert_counter(1, {"type": alert_type, "severity": severity})

        return alert

    def get_active_alerts(self, severity: str | None = None) -> list[Alert]:
        """
        Get currently active alerts.

        Parameters
        ----------
        severity : str, optional
            Filter by severity level.

        Returns
        -------
        list[Alert]
            Active alerts.
        """
        if severity:
            return [a for a in self.alerts if a.severity == severity]
        return self.alerts

    def clear_alerts(self) -> None:
        """Clear all alerts."""
        self.alerts.clear()
