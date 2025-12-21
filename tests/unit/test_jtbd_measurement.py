"""
Unit tests for specify_cli.core.jtbd_measurement module.

Tests JTBD measurement, analysis, and reporting functions.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from specify_cli.core.jtbd_measurement import (
    FeatureEffectiveness,
    JTBDMetrics,
    OutcomeDeliveryAnalysis,
    analyze_feature_effectiveness,
    analyze_outcome_delivery,
    export_metrics,
    extract_jtbd_metrics,
    generate_jtbd_report,
    query_job_completions,
    query_outcome_achievements,
    query_painpoint_resolutions,
    query_satisfaction_scores,
    query_time_to_outcome,
)
from specify_cli.core.jtbd_metrics import (
    JobStatus,
    PainpointCategory,
    SatisfactionLevel,
)

# =============================================================================
# Test Data Fixtures
# =============================================================================


@pytest.fixture
def sample_trace_data() -> list[dict]:
    """Sample trace data with JTBD events."""
    return [
        # Job completion event
        {
            "name": "job_completed",
            "attributes": {
                "jtbd.job.id": "deps-add",
                "jtbd.job.persona": "python-developer",
                "jtbd.job.feature": "specify deps add",
                "jtbd.job.status": "completed",
                "jtbd.job.duration_seconds": 8.5,
            },
        },
        # Outcome achievement event
        {
            "name": "outcome_achieved",
            "attributes": {
                "jtbd.outcome.id": "faster-dependency-management",
                "jtbd.outcome.metric": "time_saved_seconds",
                "jtbd.outcome.expected": 30.0,
                "jtbd.outcome.actual": 8.5,
                "jtbd.outcome.achievement_rate": 28.3,
                "jtbd.outcome.feature": "specify deps add",
                "jtbd.outcome.persona": "python-developer",
                "jtbd.outcome.status": "achieved",
                "jtbd.outcome.exceeds_expectations": False,
            },
        },
        # Painpoint resolution event
        {
            "name": "painpoint_resolved",
            "attributes": {
                "jtbd.painpoint.id": "manual-dependency-updates",
                "jtbd.painpoint.category": "manual_effort",
                "jtbd.painpoint.description": "Manually updating pyproject.toml",
                "jtbd.painpoint.feature": "specify deps add",
                "jtbd.painpoint.persona": "python-developer",
                "jtbd.painpoint.severity_before": 8,
                "jtbd.painpoint.severity_after": 2,
                "jtbd.painpoint.resolution_effectiveness": 75.0,
            },
        },
        # Time-to-outcome event
        {
            "name": "time_to_outcome",
            "attributes": {
                "jtbd.tto.outcome_id": "faster-dependency-management",
                "jtbd.tto.persona": "python-developer",
                "jtbd.tto.feature": "specify deps add",
                "jtbd.tto.duration_seconds": 8.5,
                "jtbd.tto.steps_count": 3,
            },
        },
        # User satisfaction event
        {
            "name": "user_satisfaction",
            "attributes": {
                "jtbd.satisfaction.outcome_id": "faster-dependency-management",
                "jtbd.satisfaction.feature": "specify deps add",
                "jtbd.satisfaction.persona": "python-developer",
                "jtbd.satisfaction.level": "very_satisfied",
                "jtbd.satisfaction.met_expectations": True,
                "jtbd.satisfaction.would_recommend": True,
                "jtbd.satisfaction.effort_score": 2,
            },
        },
    ]


# =============================================================================
# Query Function Tests
# =============================================================================


class TestQueryFunctions:
    """Tests for JTBD query functions."""

    def test_query_job_completions_no_filter(self, sample_trace_data: list[dict]) -> None:
        """Test querying all job completions."""
        results = query_job_completions(sample_trace_data)

        assert len(results) == 1
        assert results[0]["jtbd.job.id"] == "deps-add"
        assert results[0]["jtbd.job.persona"] == "python-developer"

    def test_query_job_completions_by_persona(self, sample_trace_data: list[dict]) -> None:
        """Test filtering job completions by persona."""
        results = query_job_completions(sample_trace_data, persona="python-developer")
        assert len(results) == 1

        results = query_job_completions(sample_trace_data, persona="devops-engineer")
        assert len(results) == 0

    def test_query_job_completions_by_job_id(self, sample_trace_data: list[dict]) -> None:
        """Test filtering job completions by job ID."""
        results = query_job_completions(sample_trace_data, job_id="deps-add")
        assert len(results) == 1

        results = query_job_completions(sample_trace_data, job_id="nonexistent")
        assert len(results) == 0

    def test_query_job_completions_by_status(self, sample_trace_data: list[dict]) -> None:
        """Test filtering job completions by status."""
        results = query_job_completions(sample_trace_data, status=JobStatus.COMPLETED)
        assert len(results) == 1

        results = query_job_completions(sample_trace_data, status=JobStatus.FAILED)
        assert len(results) == 0

    def test_query_outcome_achievements_no_filter(self, sample_trace_data: list[dict]) -> None:
        """Test querying all outcome achievements."""
        results = query_outcome_achievements(sample_trace_data)

        assert len(results) == 1
        assert results[0]["jtbd.outcome.id"] == "faster-dependency-management"

    def test_query_outcome_achievements_by_feature(self, sample_trace_data: list[dict]) -> None:
        """Test filtering outcome achievements by feature."""
        results = query_outcome_achievements(sample_trace_data, feature="specify deps add")
        assert len(results) == 1

        results = query_outcome_achievements(sample_trace_data, feature="other-feature")
        assert len(results) == 0

    def test_query_outcome_achievements_by_min_rate(self, sample_trace_data: list[dict]) -> None:
        """Test filtering outcome achievements by minimum achievement rate."""
        results = query_outcome_achievements(sample_trace_data, min_achievement_rate=20.0)
        assert len(results) == 1

        results = query_outcome_achievements(sample_trace_data, min_achievement_rate=50.0)
        assert len(results) == 0

    def test_query_painpoint_resolutions_no_filter(self, sample_trace_data: list[dict]) -> None:
        """Test querying all painpoint resolutions."""
        results = query_painpoint_resolutions(sample_trace_data)

        assert len(results) == 1
        assert results[0]["jtbd.painpoint.id"] == "manual-dependency-updates"

    def test_query_painpoint_resolutions_by_category(self, sample_trace_data: list[dict]) -> None:
        """Test filtering painpoint resolutions by category."""
        results = query_painpoint_resolutions(
            sample_trace_data, category=PainpointCategory.MANUAL_EFFORT
        )
        assert len(results) == 1

        results = query_painpoint_resolutions(
            sample_trace_data, category=PainpointCategory.TIME_WASTED
        )
        assert len(results) == 0

    def test_query_painpoint_resolutions_by_effectiveness(
        self, sample_trace_data: list[dict]
    ) -> None:
        """Test filtering painpoint resolutions by effectiveness."""
        results = query_painpoint_resolutions(sample_trace_data, min_effectiveness=70.0)
        assert len(results) == 1

        results = query_painpoint_resolutions(sample_trace_data, min_effectiveness=80.0)
        assert len(results) == 0

    def test_query_time_to_outcome_no_filter(self, sample_trace_data: list[dict]) -> None:
        """Test querying all time-to-outcome records."""
        results = query_time_to_outcome(sample_trace_data)

        assert len(results) == 1
        assert results[0]["jtbd.tto.outcome_id"] == "faster-dependency-management"

    def test_query_time_to_outcome_by_persona(self, sample_trace_data: list[dict]) -> None:
        """Test filtering time-to-outcome by persona."""
        results = query_time_to_outcome(sample_trace_data, persona="python-developer")
        assert len(results) == 1

        results = query_time_to_outcome(sample_trace_data, persona="other-persona")
        assert len(results) == 0

    def test_query_time_to_outcome_by_max_duration(self, sample_trace_data: list[dict]) -> None:
        """Test filtering time-to-outcome by max duration."""
        results = query_time_to_outcome(sample_trace_data, max_duration=10.0)
        assert len(results) == 1

        results = query_time_to_outcome(sample_trace_data, max_duration=5.0)
        assert len(results) == 0

    def test_query_satisfaction_scores_no_filter(self, sample_trace_data: list[dict]) -> None:
        """Test querying all satisfaction scores."""
        results = query_satisfaction_scores(sample_trace_data)

        assert len(results) == 1
        assert results[0]["jtbd.satisfaction.level"] == "very_satisfied"

    def test_query_satisfaction_scores_by_feature(self, sample_trace_data: list[dict]) -> None:
        """Test filtering satisfaction scores by feature."""
        results = query_satisfaction_scores(sample_trace_data, feature="specify deps add")
        assert len(results) == 1

        results = query_satisfaction_scores(sample_trace_data, feature="other-feature")
        assert len(results) == 0

    def test_query_satisfaction_scores_by_min_level(self, sample_trace_data: list[dict]) -> None:
        """Test filtering satisfaction scores by minimum level."""
        results = query_satisfaction_scores(
            sample_trace_data, min_level=SatisfactionLevel.SATISFIED
        )
        assert len(results) == 1

        results = query_satisfaction_scores(
            sample_trace_data, min_level=SatisfactionLevel.VERY_SATISFIED
        )
        assert len(results) == 1


# =============================================================================
# Analysis Function Tests
# =============================================================================


class TestAnalysisFunctions:
    """Tests for JTBD analysis functions."""

    def test_extract_jtbd_metrics(self, sample_trace_data: list[dict]) -> None:
        """Test extracting JTBD metrics from trace data."""
        metrics = extract_jtbd_metrics(sample_trace_data)

        assert isinstance(metrics, JTBDMetrics)
        assert len(metrics.job_completions) == 1
        assert len(metrics.outcome_achievements) == 1
        assert len(metrics.painpoint_resolutions) == 1
        assert len(metrics.time_to_outcomes) == 1
        assert len(metrics.satisfaction_scores) == 1

    def test_analyze_outcome_delivery(self, sample_trace_data: list[dict]) -> None:
        """Test analyzing outcome delivery."""
        metrics = extract_jtbd_metrics(sample_trace_data)
        analysis = analyze_outcome_delivery(metrics)

        assert "faster-dependency-management" in analysis
        outcome_analysis = analysis["faster-dependency-management"]

        assert outcome_analysis.total_attempts == 1
        assert outcome_analysis.successful_deliveries == 1
        assert outcome_analysis.delivery_rate == 100.0
        assert "specify deps add" in outcome_analysis.features_used

    def test_analyze_outcome_delivery_with_filter(self, sample_trace_data: list[dict]) -> None:
        """Test analyzing outcome delivery with filters."""
        metrics = extract_jtbd_metrics(sample_trace_data)

        # Filter by outcome ID
        analysis = analyze_outcome_delivery(metrics, outcome_id="faster-dependency-management")
        assert len(analysis) == 1

        analysis = analyze_outcome_delivery(metrics, outcome_id="nonexistent")
        assert len(analysis) == 0

        # Filter by persona
        analysis = analyze_outcome_delivery(metrics, persona="python-developer")
        assert len(analysis) == 1

        analysis = analyze_outcome_delivery(metrics, persona="other-persona")
        assert len(analysis) == 0

    def test_analyze_feature_effectiveness(self, sample_trace_data: list[dict]) -> None:
        """Test analyzing feature effectiveness."""
        metrics = extract_jtbd_metrics(sample_trace_data)
        effectiveness = analyze_feature_effectiveness(metrics)

        assert "specify deps add" in effectiveness
        feature_eff = effectiveness["specify deps add"]

        assert feature_eff.total_uses == 1
        assert feature_eff.jobs_completed == 1
        assert feature_eff.outcomes_delivered == 1
        assert feature_eff.painpoints_resolved == 1
        assert feature_eff.avg_satisfaction == 5.0  # very_satisfied
        assert feature_eff.avg_effort_score == 2.0
        assert feature_eff.recommendation_rate == 100.0
        assert "python-developer" in feature_eff.personas_served
        assert feature_eff.effectiveness_score > 0


# =============================================================================
# Data Class Tests
# =============================================================================


class TestJTBDMetrics:
    """Tests for JTBDMetrics data class."""

    def test_jtbd_metrics_creation(self) -> None:
        """Test creating JTBDMetrics instance."""
        metrics = JTBDMetrics()

        assert metrics.job_completions == []
        assert metrics.outcome_achievements == []
        assert metrics.painpoint_resolutions == []
        assert metrics.time_to_outcomes == []
        assert metrics.satisfaction_scores == []

    def test_jtbd_metrics_to_dict(self) -> None:
        """Test converting JTBDMetrics to dictionary."""
        metrics = JTBDMetrics(
            job_completions=[{"id": "test"}],
            outcome_achievements=[{"id": "test"}],
        )

        metrics_dict = metrics.to_dict()

        assert isinstance(metrics_dict, dict)
        assert "job_completions" in metrics_dict
        assert "outcome_achievements" in metrics_dict


class TestOutcomeDeliveryAnalysis:
    """Tests for OutcomeDeliveryAnalysis data class."""

    def test_outcome_delivery_analysis_creation(self) -> None:
        """Test creating OutcomeDeliveryAnalysis instance."""
        analysis = OutcomeDeliveryAnalysis(outcome_id="test-outcome")

        assert analysis.outcome_id == "test-outcome"
        assert analysis.total_attempts == 0
        assert analysis.successful_deliveries == 0
        assert analysis.delivery_rate == 0.0

    def test_outcome_delivery_calculate_metrics(self) -> None:
        """Test calculating delivery metrics."""
        analysis = OutcomeDeliveryAnalysis(outcome_id="test-outcome")
        analysis.total_attempts = 10
        analysis.successful_deliveries = 8

        analysis.calculate_metrics()

        assert analysis.delivery_rate == 80.0

    def test_outcome_delivery_calculate_metrics_zero_attempts(self) -> None:
        """Test calculating metrics with zero attempts."""
        analysis = OutcomeDeliveryAnalysis(outcome_id="test-outcome")
        analysis.total_attempts = 0
        analysis.successful_deliveries = 0

        analysis.calculate_metrics()

        assert analysis.delivery_rate == 0.0


class TestFeatureEffectiveness:
    """Tests for FeatureEffectiveness data class."""

    def test_feature_effectiveness_creation(self) -> None:
        """Test creating FeatureEffectiveness instance."""
        effectiveness = FeatureEffectiveness(feature="test-feature")

        assert effectiveness.feature == "test-feature"
        assert effectiveness.total_uses == 0
        assert effectiveness.effectiveness_score == 0.0

    def test_feature_effectiveness_calculate_effectiveness(self) -> None:
        """Test calculating effectiveness score."""
        effectiveness = FeatureEffectiveness(feature="test-feature")
        effectiveness.total_uses = 10
        effectiveness.outcomes_delivered = 8
        effectiveness.painpoints_resolved = 7
        effectiveness.avg_satisfaction = 4.5
        effectiveness.avg_effort_score = 2.0

        effectiveness.calculate_effectiveness()

        # Score should be weighted average:
        # - Outcome: (8/10 * 100) * 0.4 = 32
        # - Satisfaction: (4.5/5 * 100) * 0.3 = 27
        # - Painpoint: (7/10 * 100) * 0.2 = 14
        # - Effort: ((7-2)/6 * 100) * 0.1 = 8.33
        # Total: ~81.33
        assert effectiveness.effectiveness_score > 80
        assert effectiveness.effectiveness_score < 82

    def test_feature_effectiveness_calculate_zero_uses(self) -> None:
        """Test calculating effectiveness with zero uses."""
        effectiveness = FeatureEffectiveness(feature="test-feature")
        effectiveness.total_uses = 0

        effectiveness.calculate_effectiveness()

        assert effectiveness.effectiveness_score == 0.0


# =============================================================================
# Export Function Tests
# =============================================================================


class TestExportFunctions:
    """Tests for JTBD export functions."""

    def test_export_metrics_json(self, sample_trace_data: list[dict], tmp_path: Path) -> None:
        """Test exporting metrics to JSON."""
        metrics = extract_jtbd_metrics(sample_trace_data)
        output_file = tmp_path / "metrics.json"

        export_metrics(metrics, output_file, export_format="json")

        assert output_file.exists()

        # Verify JSON content
        with output_file.open() as f:
            data = json.load(f)

        assert "job_completions" in data
        assert len(data["job_completions"]) == 1

    def test_export_metrics_csv(self, sample_trace_data: list[dict], tmp_path: Path) -> None:
        """Test exporting metrics to CSV."""
        metrics = extract_jtbd_metrics(sample_trace_data)
        output_file = tmp_path / "metrics.csv"

        export_metrics(metrics, output_file, export_format="csv")

        # CSV export creates multiple files
        assert (tmp_path / "metrics_job_completions.csv").exists()
        assert (tmp_path / "metrics_outcomes.csv").exists()
        assert (tmp_path / "metrics_painpoints.csv").exists()

    def test_export_metrics_invalid_format(
        self, sample_trace_data: list[dict], tmp_path: Path
    ) -> None:
        """Test exporting with invalid format."""
        metrics = extract_jtbd_metrics(sample_trace_data)
        output_file = tmp_path / "metrics.xyz"

        with pytest.raises(ValueError, match="Unsupported format"):
            export_metrics(metrics, output_file, export_format="xyz")

    def test_generate_jtbd_report(self, sample_trace_data: list[dict], tmp_path: Path) -> None:
        """Test generating JTBD report."""
        metrics = extract_jtbd_metrics(sample_trace_data)
        output_file = tmp_path / "report.md"

        generate_jtbd_report(metrics, output_file)

        assert output_file.exists()

        # Verify report content
        content = output_file.read_text()
        assert "# JTBD Metrics Report" in content
        assert "Total Jobs Completed: 1" in content
        assert "faster-dependency-management" in content
        assert "specify deps add" in content


# =============================================================================
# Edge Case Tests
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_query_empty_trace_data(self) -> None:
        """Test querying empty trace data."""
        results = query_job_completions([])
        assert results == []

        results = query_outcome_achievements([])
        assert results == []

    def test_extract_metrics_from_empty_data(self) -> None:
        """Test extracting metrics from empty data."""
        metrics = extract_jtbd_metrics([])

        assert len(metrics.job_completions) == 0
        assert len(metrics.outcome_achievements) == 0

    def test_analyze_outcome_delivery_empty_metrics(self) -> None:
        """Test analyzing outcome delivery with empty metrics."""
        metrics = JTBDMetrics()
        analysis = analyze_outcome_delivery(metrics)

        assert analysis == {}

    def test_analyze_feature_effectiveness_empty_metrics(self) -> None:
        """Test analyzing feature effectiveness with empty metrics."""
        metrics = JTBDMetrics()
        effectiveness = analyze_feature_effectiveness(metrics)

        assert effectiveness == {}

    def test_query_with_malformed_data(self) -> None:
        """Test querying with malformed trace data."""
        malformed_data = [
            {"name": "job_completed"},  # Missing attributes
            {"attributes": {}},  # Missing name
            {},  # Empty record
        ]

        results = query_job_completions(malformed_data)
        # Should return empty attributes dict for record with name but no job attributes
        assert len(results) <= 1  # May return empty dict from malformed data
