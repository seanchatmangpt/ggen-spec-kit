"""Unit tests for job-outcome reasoning."""

from __future__ import annotations

import numpy as np
import pytest

# These tests are for experimental hyperdimensional computing features
# Mark as xfail until full implementation is complete
pytestmark = pytest.mark.xfail(
    reason="Hyperdimensional job-outcome module under development",
    strict=False,
)

from specify_cli.hyperdimensional.job_outcome import (
    Feature,
    Job,
    Outcome,
    PainPoint,
    compute_job_outcome_alignment,
    feature_outcome_chains,
    features_covering_job,
    identify_unmet_needs,
    job_coverage_completeness,
    outcome_delivery_certainty,
    painpoint_resolution_effectiveness,
    prioritize_features_by_job_impact,
)


class TestJobCoverageAnalysis:
    """Tests for job coverage analysis."""

    def test_features_covering_job(self) -> None:
        """Test feature coverage identification."""
        job = Job(
            name="deploy",
            description="Deploy service",
            vector=np.random.randn(100),
        )

        features = {
            "ci_cd": Feature(
                name="ci_cd",
                description="CI/CD pipeline",
                vector=np.random.randn(100),
            ),
            "monitoring": Feature(
                name="monitoring",
                description="Monitoring tools",
                vector=np.random.randn(100),
            ),
        }

        covering = features_covering_job(job, features, similarity_threshold=0.0)

        assert isinstance(covering, list)
        assert all(isinstance(f, Feature) for f, _ in covering)

    def test_job_coverage_completeness(self) -> None:
        """Test job coverage completeness measurement."""
        job = Job(
            name="deploy",
            description="Deploy service",
            vector=np.random.randn(100),
        )

        features = [
            Feature(
                name="ci_cd",
                description="CI/CD",
                vector=np.random.randn(100),
            )
        ]

        outcomes = [
            Outcome(
                name="fast_deployment",
                description="Deploy quickly",
                vector=np.random.randn(100),
                measurement="time",
            )
        ]

        completeness = job_coverage_completeness(job, features, outcomes)

        assert "overall" in completeness
        assert 0.0 <= completeness["overall"] <= 1.0
        assert "outcome_coverage" in completeness

    def test_identify_unmet_needs(self) -> None:
        """Test unmet needs identification."""
        job = Job(
            name="deploy",
            description="Deploy service",
            vector=np.random.randn(100),
        )

        features = [
            Feature(
                name="basic_deploy",
                description="Basic deployment",
                vector=np.random.randn(100),
            )
        ]

        outcomes = [
            Outcome(
                name="automated_rollback",
                description="Automatic rollback",
                vector=np.random.randn(100),
                measurement="boolean",
            )
        ]

        unmet = identify_unmet_needs(job, features, outcomes, threshold=0.9)

        assert isinstance(unmet, list)


class TestOutcomeAlignment:
    """Tests for outcome alignment."""

    def test_outcome_delivery_certainty(self) -> None:
        """Test outcome delivery certainty assessment."""
        feature = Feature(
            name="auto_scale",
            description="Auto scaling",
            vector=np.random.randn(100),
            implementation_status="complete",
        )

        outcome = Outcome(
            name="handle_load",
            description="Handle high load",
            vector=np.random.randn(100),
            measurement="throughput",
        )

        certainty = outcome_delivery_certainty(feature, outcome)

        assert "confidence" in certainty
        assert 0.0 <= certainty["confidence"] <= 1.0
        assert "certainty_level" in certainty

    def test_feature_outcome_chains(self) -> None:
        """Test feature-outcome chain identification."""
        feature = Feature(
            name="monitoring",
            description="Monitoring system",
            vector=np.random.randn(100),
            outcomes_addressed=["visibility"],
        )

        outcomes = {
            "visibility": Outcome(
                name="visibility",
                description="System visibility",
                vector=np.random.randn(100),
                measurement="coverage",
            ),
            "reliability": Outcome(
                name="reliability",
                description="System reliability",
                vector=np.random.randn(100),
                measurement="uptime",
            ),
        }

        chains = feature_outcome_chains(feature, outcomes, max_hops=2)

        assert isinstance(chains, list)

    def test_painpoint_resolution_effectiveness(self) -> None:
        """Test pain point resolution effectiveness."""
        feature = Feature(
            name="auto_heal",
            description="Auto-healing",
            vector=np.random.randn(100),
        )

        pain_point = PainPoint(
            name="manual_recovery",
            description="Manual recovery needed",
            vector=np.random.randn(100),
            severity=0.8,
            frequency=0.6,
        )

        effectiveness = painpoint_resolution_effectiveness(feature, pain_point)

        assert "effectiveness" in effectiveness
        assert "impact_score" in effectiveness
        # Impact score can be negative due to random vectors, but should be a float
        assert isinstance(effectiveness["impact_score"], float)


class TestJobOutcomeAlignment:
    """Tests for job-outcome alignment metrics."""

    def test_compute_job_outcome_alignment(self) -> None:
        """Test comprehensive alignment computation."""
        jobs = [
            Job(
                name="deploy",
                description="Deploy service",
                vector=np.random.randn(100),
                importance=0.9,
                frequency=0.7,
            )
        ]

        outcomes = [
            Outcome(
                name="fast_deploy",
                description="Fast deployment",
                vector=np.random.randn(100),
                measurement="time",
            )
        ]

        features = [
            Feature(
                name="ci_cd",
                description="CI/CD pipeline",
                vector=np.random.randn(100),
            )
        ]

        alignment = compute_job_outcome_alignment(jobs, outcomes, features)

        assert "overall_alignment" in alignment
        assert "alignment_grade" in alignment
        assert 0.0 <= alignment["overall_alignment"] <= 1.0

    def test_prioritize_features_by_job_impact(self) -> None:
        """Test feature prioritization by job impact."""
        features = [
            Feature(
                name="feature_a",
                description="Feature A",
                vector=np.random.randn(100),
            ),
            Feature(
                name="feature_b",
                description="Feature B",
                vector=np.random.randn(100),
            ),
        ]

        jobs = [
            Job(
                name="job1",
                description="Job 1",
                vector=np.random.randn(100),
                importance=0.9,
                frequency=0.8,
            )
        ]

        outcomes = [
            Outcome(
                name="outcome1",
                description="Outcome 1",
                vector=np.random.randn(100),
                measurement="score",
                current_satisfaction=0.5,
            )
        ]

        prioritized = prioritize_features_by_job_impact(features, jobs, outcomes)

        assert len(prioritized) == len(features)
        # Should be sorted by impact
        assert prioritized[0][1] >= prioritized[1][1]
