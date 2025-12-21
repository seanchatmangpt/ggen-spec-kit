"""
Unit tests for specify_cli.ops.jtbd module.

Tests cover JTBD operations business logic with pure functions (no I/O).

Test Coverage
-------------
- Job validation functions
- Outcome metrics calculations
- Job-feature mapping analysis
- JTBD report generation
- Satisfaction score calculations
- Painpoint pattern identification
- Edge cases and error handling

Examples
--------
    $ pytest tests/unit/test_ops_jtbd.py -v
    $ pytest tests/unit/test_ops_jtbd.py::test_validate_job_completion_valid -v
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from specify_cli.core.jtbd_metrics import (
    OutcomeAchieved,
    PainpointCategory,
    PainpointResolved,
    SatisfactionLevel,
    UserSatisfaction,
)
from specify_cli.ops.jtbd import (
    analyze_job_feature_mapping,
    calculate_outcome_metrics,
    calculate_satisfaction_scores,
    generate_jtbd_report,
    identify_painpoint_patterns,
    validate_job_completion,
)

# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def valid_job_data() -> dict[str, str]:
    """Valid job completion data for testing."""
    return {
        "job_id": "deps-add",
        "persona": "python-developer",
        "feature": "specify deps add",
    }


@pytest.fixture
def sample_jobs() -> list[dict]:
    """Sample job completion data."""
    return [
        {
            "job_id": "deps-add",
            "feature_used": "specify deps add",
            "persona": "python-developer",
            "status": "completed",
            "duration_seconds": 8.5,
        },
        {
            "job_id": "deps-add",
            "feature_used": "uv add",
            "persona": "python-developer",
            "status": "completed",
            "duration_seconds": 5.2,
        },
        {
            "job_id": "docs-generate",
            "feature_used": "specify docs generate",
            "persona": "technical-writer",
            "status": "failed",
            "duration_seconds": None,
        },
    ]


@pytest.fixture
def sample_outcomes() -> list[OutcomeAchieved]:
    """Sample outcome achievement data."""
    return [
        OutcomeAchieved(
            outcome_id="faster-dependency-management",
            metric="time_saved_seconds",
            expected_value=30.0,
            actual_value=40.0,  # Exceeds expectations
            feature="specify deps add",
            persona="python-developer",
        ),
        OutcomeAchieved(
            outcome_id="faster-dependency-management",
            metric="time_saved_seconds",
            expected_value=30.0,
            actual_value=25.0,  # Partially achieved
            feature="uv add",
            persona="python-developer",
        ),
        OutcomeAchieved(
            outcome_id="better-documentation",
            metric="quality_score",
            expected_value=8.0,
            actual_value=5.0,  # Not achieved
            feature="specify docs generate",
            persona="technical-writer",
        ),
    ]


@pytest.fixture
def sample_satisfaction() -> list[UserSatisfaction]:
    """Sample user satisfaction data."""
    return [
        UserSatisfaction(
            outcome_id="faster-dependency-management",
            feature="specify deps add",
            persona="python-developer",
            satisfaction_level=SatisfactionLevel.VERY_SATISFIED,
            met_expectations=True,
            would_recommend=True,
            effort_score=2,
        ),
        UserSatisfaction(
            outcome_id="faster-dependency-management",
            feature="uv add",
            persona="python-developer",
            satisfaction_level=SatisfactionLevel.SATISFIED,
            met_expectations=True,
            would_recommend=True,
            effort_score=3,
        ),
        UserSatisfaction(
            outcome_id="better-documentation",
            feature="specify docs generate",
            persona="technical-writer",
            satisfaction_level=SatisfactionLevel.NEUTRAL,
            met_expectations=False,
            would_recommend=False,
            effort_score=5,
        ),
    ]


@pytest.fixture
def sample_painpoints() -> list[PainpointResolved]:
    """Sample painpoint resolution data."""
    return [
        PainpointResolved(
            painpoint_id="manual-dependency-updates",
            category=PainpointCategory.MANUAL_EFFORT,
            description="Manually updating pyproject.toml",
            feature="specify deps add",
            persona="python-developer",
            severity_before=8,
            severity_after=2,
        ),
        PainpointResolved(
            painpoint_id="slow-dependency-resolution",
            category=PainpointCategory.TIME_WASTED,
            description="Slow dependency resolution",
            feature="uv add",
            persona="python-developer",
            severity_before=7,
            severity_after=3,
        ),
        PainpointResolved(
            painpoint_id="outdated-documentation",
            category=PainpointCategory.MANUAL_EFFORT,
            description="Manually updating documentation",
            feature="specify docs generate",
            persona="technical-writer",
            severity_before=9,
            severity_after=4,
        ),
    ]


# =============================================================================
# Validation Tests
# =============================================================================


class TestValidateJobCompletion:
    """Tests for validate_job_completion function."""

    def test_validate_job_completion_valid(self, valid_job_data: dict) -> None:
        """Test validation passes with valid data."""
        result = validate_job_completion(**valid_job_data)

        assert result.valid is True
        assert result.job_id == "deps-add"
        assert result.persona == "python-developer"
        assert result.feature == "specify deps add"
        assert len(result.errors) == 0
        assert "job_id_length" in result.metadata

    def test_validate_job_completion_with_context(self) -> None:
        """Test validation with context data."""
        result = validate_job_completion(
            job_id="deps-add",
            persona="python-developer",
            feature="specify deps add",
            context={"package": "httpx", "version": "0.27.0"},
        )

        assert result.valid is True
        assert result.metadata["context_keys"] == 2

    def test_validate_job_completion_empty_job_id(self) -> None:
        """Test validation fails with empty job_id."""
        result = validate_job_completion(
            job_id="",
            persona="python-developer",
            feature="specify deps add",
        )

        assert result.valid is False
        assert any("job_id is required" in e for e in result.errors)

    def test_validate_job_completion_short_job_id(self) -> None:
        """Test validation fails with too short job_id."""
        result = validate_job_completion(
            job_id="ab",
            persona="python-developer",
            feature="specify deps add",
        )

        assert result.valid is False
        assert any("at least 3 characters" in e for e in result.errors)

    def test_validate_job_completion_long_job_id(self) -> None:
        """Test validation fails with too long job_id."""
        result = validate_job_completion(
            job_id="a" * 101,
            persona="python-developer",
            feature="specify deps add",
        )

        assert result.valid is False
        assert any("at most 100 characters" in e for e in result.errors)

    def test_validate_job_completion_empty_persona(self) -> None:
        """Test validation fails with empty persona."""
        result = validate_job_completion(
            job_id="deps-add",
            persona="",
            feature="specify deps add",
        )

        assert result.valid is False
        assert any("persona is required" in e for e in result.errors)

    def test_validate_job_completion_short_persona(self) -> None:
        """Test validation fails with too short persona."""
        result = validate_job_completion(
            job_id="deps-add",
            persona="ab",
            feature="specify deps add",
        )

        assert result.valid is False
        assert any("persona must be at least 3 characters" in e for e in result.errors)

    def test_validate_job_completion_empty_feature(self) -> None:
        """Test validation fails with empty feature."""
        result = validate_job_completion(
            job_id="deps-add",
            persona="python-developer",
            feature="",
        )

        assert result.valid is False
        assert any("feature is required" in e for e in result.errors)

    def test_validate_job_completion_short_feature(self) -> None:
        """Test validation fails with too short feature."""
        result = validate_job_completion(
            job_id="deps-add",
            persona="python-developer",
            feature="ab",
        )

        assert result.valid is False
        assert any("feature must be at least 3 characters" in e for e in result.errors)

    def test_validate_job_completion_non_kebab_case_warning(self) -> None:
        """Test warning for non-kebab-case job_id."""
        result = validate_job_completion(
            job_id="deps@add",  # Invalid character
            persona="python-developer",
            feature="specify deps add",
        )

        # Should still be valid but with warning about kebab-case
        assert result.valid is True
        assert any("kebab-case" in w for w in result.warnings)

    def test_validate_job_completion_invalid_context_type(self) -> None:
        """Test validation fails with invalid context type."""
        result = validate_job_completion(
            job_id="deps-add",
            persona="python-developer",
            feature="specify deps add",
            context="invalid",  # type: ignore[arg-type]
        )

        assert result.valid is False
        assert any("context must be a dictionary" in e for e in result.errors)

    def test_validate_job_completion_multiple_errors(self) -> None:
        """Test validation collects multiple errors."""
        result = validate_job_completion(
            job_id="",
            persona="ab",
            feature="",
        )

        assert result.valid is False
        assert len(result.errors) >= 3  # All three fields have errors


# =============================================================================
# Outcome Metrics Tests
# =============================================================================


class TestCalculateOutcomeMetrics:
    """Tests for calculate_outcome_metrics function."""

    def test_calculate_outcome_metrics_basic(self, sample_outcomes: list[OutcomeAchieved]) -> None:
        """Test basic outcome metrics calculation."""
        metrics = calculate_outcome_metrics(sample_outcomes)

        assert metrics.total_outcomes == 3
        assert metrics.achieved_count == 1  # >= 100%
        assert metrics.partially_achieved_count == 1  # 75-99%
        assert metrics.not_achieved_count == 1  # < 75%
        assert metrics.exceeds_expectations_count == 1

    def test_calculate_outcome_metrics_empty_list(self) -> None:
        """Test metrics calculation with empty list."""
        metrics = calculate_outcome_metrics([])

        assert metrics.total_outcomes == 0
        assert metrics.achieved_count == 0
        assert metrics.avg_achievement_rate == 0.0
        assert metrics.median_achievement_rate == 0.0

    def test_calculate_outcome_metrics_achievement_rates(
        self, sample_outcomes: list[OutcomeAchieved]
    ) -> None:
        """Test achievement rate calculations."""
        metrics = calculate_outcome_metrics(sample_outcomes)

        # Should have average and median
        assert metrics.avg_achievement_rate > 0
        assert metrics.median_achievement_rate > 0
        assert "specify deps add" in metrics.outcomes_by_feature
        assert "uv add" in metrics.outcomes_by_feature

    def test_calculate_outcome_metrics_by_persona(
        self, sample_outcomes: list[OutcomeAchieved]
    ) -> None:
        """Test metrics grouped by persona."""
        metrics = calculate_outcome_metrics(sample_outcomes)

        assert "python-developer" in metrics.outcomes_by_persona
        assert "technical-writer" in metrics.outcomes_by_persona
        assert metrics.outcomes_by_persona["python-developer"] == 2

    def test_calculate_outcome_metrics_exceeds_expectations_rate(
        self, sample_outcomes: list[OutcomeAchieved]
    ) -> None:
        """Test exceeds expectations rate calculation."""
        metrics = calculate_outcome_metrics(sample_outcomes)

        # 1 out of 3 exceeds expectations = 33.33%
        assert metrics.exceeds_expectations_rate > 33.0
        assert metrics.exceeds_expectations_rate < 34.0

    def test_calculate_outcome_metrics_achievement_by_feature(
        self, sample_outcomes: list[OutcomeAchieved]
    ) -> None:
        """Test average achievement rates by feature."""
        metrics = calculate_outcome_metrics(sample_outcomes)

        assert "specify deps add" in metrics.achievement_rates_by_feature
        # specify deps add has 133% achievement rate (40/30 * 100)
        assert metrics.achievement_rates_by_feature["specify deps add"] > 130


# =============================================================================
# Job-Feature Mapping Tests
# =============================================================================


class TestAnalyzeJobFeatureMapping:
    """Tests for analyze_job_feature_mapping function."""

    def test_analyze_job_feature_mapping_basic(self, sample_jobs: list[dict]) -> None:
        """Test basic job-feature mapping analysis."""
        mappings = analyze_job_feature_mapping(sample_jobs)

        assert len(mappings) == 2  # deps-add and docs-generate

        # Find deps-add mapping
        deps_mapping = next(m for m in mappings if m.job_id == "deps-add")
        assert deps_mapping.usage_count == 2
        assert "specify deps add" in deps_mapping.features_used
        assert "uv add" in deps_mapping.features_used

    def test_analyze_job_feature_mapping_empty_list(self) -> None:
        """Test mapping analysis with empty list."""
        mappings = analyze_job_feature_mapping([])

        assert mappings == []

    def test_analyze_job_feature_mapping_personas(self, sample_jobs: list[dict]) -> None:
        """Test personas collection in mappings."""
        mappings = analyze_job_feature_mapping(sample_jobs)

        deps_mapping = next(m for m in mappings if m.job_id == "deps-add")
        assert "python-developer" in deps_mapping.personas

    def test_analyze_job_feature_mapping_success_rate(self, sample_jobs: list[dict]) -> None:
        """Test success rate calculation."""
        mappings = analyze_job_feature_mapping(sample_jobs)

        deps_mapping = next(m for m in mappings if m.job_id == "deps-add")
        # 2 out of 2 completed = 100%
        assert deps_mapping.success_rate == 100.0

        docs_mapping = next(m for m in mappings if m.job_id == "docs-generate")
        # 0 out of 1 completed = 0%
        assert docs_mapping.success_rate == 0.0

    def test_analyze_job_feature_mapping_avg_duration(self, sample_jobs: list[dict]) -> None:
        """Test average duration calculation."""
        mappings = analyze_job_feature_mapping(sample_jobs)

        deps_mapping = next(m for m in mappings if m.job_id == "deps-add")
        # Average of 8.5 and 5.2 = 6.85
        assert deps_mapping.avg_duration_seconds is not None
        assert abs(deps_mapping.avg_duration_seconds - 6.85) < 0.01

    def test_analyze_job_feature_mapping_most_common_feature(self, sample_jobs: list[dict]) -> None:
        """Test most common feature identification."""
        mappings = analyze_job_feature_mapping(sample_jobs)

        # Both features used once, should pick one
        deps_mapping = next(m for m in mappings if m.job_id == "deps-add")
        assert deps_mapping.most_common_feature in ["specify deps add", "uv add"]

    def test_analyze_job_feature_mapping_filter_features(self, sample_jobs: list[dict]) -> None:
        """Test filtering by specific features."""
        mappings = analyze_job_feature_mapping(sample_jobs, features=["specify deps add"])

        deps_mapping = next(m for m in mappings if m.job_id == "deps-add")
        assert "specify deps add" in deps_mapping.features_used
        assert "uv add" not in deps_mapping.features_used

    def test_analyze_job_feature_mapping_missing_job_id(self) -> None:
        """Test handling of jobs without job_id."""
        jobs = [{"feature_used": "test", "persona": "test", "status": "completed"}]

        mappings = analyze_job_feature_mapping(jobs)

        # Should skip jobs without job_id
        assert len(mappings) == 0


# =============================================================================
# Report Generation Tests
# =============================================================================


class TestGenerateJTBDReport:
    """Tests for generate_jtbd_report function."""

    def test_generate_jtbd_report_basic(
        self,
        sample_jobs: list[dict],
        sample_outcomes: list[OutcomeAchieved],
    ) -> None:
        """Test basic report generation."""
        start = datetime(2025, 1, 1, tzinfo=UTC)
        end = datetime(2025, 1, 31, tzinfo=UTC)

        report = generate_jtbd_report(
            start_date=start,
            end_date=end,
            jobs=sample_jobs,
            outcomes=sample_outcomes,
        )

        assert report.start_date == start
        assert report.end_date == end
        assert report.total_jobs == 3
        assert report.completed_jobs == 2
        assert report.failed_jobs == 1

    def test_generate_jtbd_report_empty_data(self) -> None:
        """Test report generation with no data."""
        start = datetime(2025, 1, 1, tzinfo=UTC)
        end = datetime(2025, 1, 31, tzinfo=UTC)

        report = generate_jtbd_report(start_date=start, end_date=end)

        assert report.total_jobs == 0
        assert report.completion_rate == 0.0
        assert report.outcome_metrics is None

    def test_generate_jtbd_report_completion_rate(self, sample_jobs: list[dict]) -> None:
        """Test completion rate calculation."""
        start = datetime(2025, 1, 1, tzinfo=UTC)
        end = datetime(2025, 1, 31, tzinfo=UTC)

        report = generate_jtbd_report(
            start_date=start,
            end_date=end,
            jobs=sample_jobs,
        )

        # 2 completed out of 3 = 66.67%
        assert report.completion_rate > 66.0
        assert report.completion_rate < 67.0

    def test_generate_jtbd_report_with_persona_filter(
        self,
        sample_jobs: list[dict],
        sample_outcomes: list[OutcomeAchieved],
    ) -> None:
        """Test report generation with persona filter."""
        start = datetime(2025, 1, 1, tzinfo=UTC)
        end = datetime(2025, 1, 31, tzinfo=UTC)

        report = generate_jtbd_report(
            start_date=start,
            end_date=end,
            persona="python-developer",
            jobs=sample_jobs,
            outcomes=sample_outcomes,
        )

        assert report.persona == "python-developer"
        assert report.total_jobs == 2  # Only python-developer jobs

    def test_generate_jtbd_report_with_satisfaction(
        self,
        sample_jobs: list[dict],
        sample_satisfaction: list[UserSatisfaction],
    ) -> None:
        """Test report includes satisfaction scores."""
        start = datetime(2025, 1, 1, tzinfo=UTC)
        end = datetime(2025, 1, 31, tzinfo=UTC)

        report = generate_jtbd_report(
            start_date=start,
            end_date=end,
            jobs=sample_jobs,
            satisfaction_data=sample_satisfaction,
        )

        assert "total_responses" in report.satisfaction_scores
        assert report.satisfaction_scores["total_responses"] == 3

    def test_generate_jtbd_report_with_painpoints(
        self,
        sample_jobs: list[dict],
        sample_painpoints: list[PainpointResolved],
    ) -> None:
        """Test report includes painpoint patterns."""
        start = datetime(2025, 1, 1, tzinfo=UTC)
        end = datetime(2025, 1, 31, tzinfo=UTC)

        report = generate_jtbd_report(
            start_date=start,
            end_date=end,
            jobs=sample_jobs,
            painpoints=sample_painpoints,
        )

        assert len(report.painpoint_patterns) > 0
        assert "category" in report.painpoint_patterns[0]

    def test_generate_jtbd_report_top_features(
        self,
        sample_jobs: list[dict],
        sample_outcomes: list[OutcomeAchieved],
    ) -> None:
        """Test top performing features identification."""
        start = datetime(2025, 1, 1, tzinfo=UTC)
        end = datetime(2025, 1, 31, tzinfo=UTC)

        report = generate_jtbd_report(
            start_date=start,
            end_date=end,
            jobs=sample_jobs,
            outcomes=sample_outcomes,
        )

        assert len(report.top_performing_features) > 0
        # Top feature should be "specify deps add" with highest achievement rate
        assert report.top_performing_features[0][0] == "specify deps add"


# =============================================================================
# Satisfaction Scores Tests
# =============================================================================


class TestCalculateSatisfactionScores:
    """Tests for calculate_satisfaction_scores function."""

    def test_calculate_satisfaction_scores_basic(
        self, sample_satisfaction: list[UserSatisfaction]
    ) -> None:
        """Test basic satisfaction score calculation."""
        scores = calculate_satisfaction_scores(sample_satisfaction)

        assert scores.total_responses == 3
        assert scores.avg_effort_score is not None
        assert scores.met_expectations_rate > 0
        assert scores.would_recommend_rate > 0

    def test_calculate_satisfaction_scores_empty_list(self) -> None:
        """Test scores calculation with empty list."""
        scores = calculate_satisfaction_scores([])

        assert scores.total_responses == 0
        assert scores.avg_effort_score is None
        assert scores.met_expectations_rate == 0.0
        assert scores.nps_score is None

    def test_calculate_satisfaction_scores_effort_score(
        self, sample_satisfaction: list[UserSatisfaction]
    ) -> None:
        """Test average effort score calculation."""
        scores = calculate_satisfaction_scores(sample_satisfaction)

        # Average of 2, 3, 5 = 3.33
        assert scores.avg_effort_score is not None
        assert abs(scores.avg_effort_score - 3.33) < 0.01

    def test_calculate_satisfaction_scores_met_expectations_rate(
        self, sample_satisfaction: list[UserSatisfaction]
    ) -> None:
        """Test met expectations rate calculation."""
        scores = calculate_satisfaction_scores(sample_satisfaction)

        # 2 out of 3 met expectations = 66.67%
        assert scores.met_expectations_rate > 66.0
        assert scores.met_expectations_rate < 67.0

    def test_calculate_satisfaction_scores_would_recommend_rate(
        self, sample_satisfaction: list[UserSatisfaction]
    ) -> None:
        """Test would recommend rate calculation."""
        scores = calculate_satisfaction_scores(sample_satisfaction)

        # 2 out of 3 would recommend = 66.67%
        assert scores.would_recommend_rate > 66.0
        assert scores.would_recommend_rate < 67.0

    def test_calculate_satisfaction_scores_distribution(
        self, sample_satisfaction: list[UserSatisfaction]
    ) -> None:
        """Test satisfaction level distribution."""
        scores = calculate_satisfaction_scores(sample_satisfaction)

        assert scores.satisfaction_distribution["very_satisfied"] == 1
        assert scores.satisfaction_distribution["satisfied"] == 1
        assert scores.satisfaction_distribution["neutral"] == 1

    def test_calculate_satisfaction_scores_nps(
        self, sample_satisfaction: list[UserSatisfaction]
    ) -> None:
        """Test NPS (Net Promoter Score) calculation."""
        scores = calculate_satisfaction_scores(sample_satisfaction)

        # Promoters: 1 (very_satisfied)
        # Passives: 1 (satisfied)
        # Detractors: 1 (neutral)
        # NPS = (1-1)/3 * 100 = 0
        assert scores.nps_score == 0.0
        assert scores.promoters_count == 1
        assert scores.passives_count == 1
        assert scores.detractors_count == 1

    def test_calculate_satisfaction_scores_missing_effort_scores(self) -> None:
        """Test handling of missing effort scores."""
        feedback = [
            UserSatisfaction(
                outcome_id="test",
                feature="test",
                persona="test",
                satisfaction_level=SatisfactionLevel.SATISFIED,
                met_expectations=True,
                would_recommend=True,
                effort_score=None,  # Missing
            )
        ]

        scores = calculate_satisfaction_scores(feedback)

        assert scores.avg_effort_score is None


# =============================================================================
# Painpoint Analysis Tests
# =============================================================================


class TestIdentifyPainpointPatterns:
    """Tests for identify_painpoint_patterns function."""

    def test_identify_painpoint_patterns_basic(
        self, sample_painpoints: list[PainpointResolved]
    ) -> None:
        """Test basic painpoint pattern identification."""
        analysis = identify_painpoint_patterns(sample_painpoints)

        assert analysis.total_painpoints == 3
        assert len(analysis.patterns) == 2  # MANUAL_EFFORT and TIME_WASTED

    def test_identify_painpoint_patterns_empty_list(self) -> None:
        """Test pattern identification with empty list."""
        analysis = identify_painpoint_patterns([])

        assert analysis.total_painpoints == 0
        assert len(analysis.patterns) == 0
        assert analysis.most_common_category is None
        assert analysis.avg_resolution_effectiveness == 0.0

    def test_identify_painpoint_patterns_by_category(
        self, sample_painpoints: list[PainpointResolved]
    ) -> None:
        """Test patterns grouped by category."""
        analysis = identify_painpoint_patterns(sample_painpoints)

        # Should have MANUAL_EFFORT and TIME_WASTED patterns
        categories = [p.category for p in analysis.patterns]
        assert PainpointCategory.MANUAL_EFFORT in categories
        assert PainpointCategory.TIME_WASTED in categories

    def test_identify_painpoint_patterns_most_common(
        self, sample_painpoints: list[PainpointResolved]
    ) -> None:
        """Test most common category identification."""
        analysis = identify_painpoint_patterns(sample_painpoints)

        # MANUAL_EFFORT appears twice, TIME_WASTED once
        assert analysis.most_common_category == PainpointCategory.MANUAL_EFFORT

    def test_identify_painpoint_patterns_effectiveness(
        self, sample_painpoints: list[PainpointResolved]
    ) -> None:
        """Test resolution effectiveness calculation."""
        analysis = identify_painpoint_patterns(sample_painpoints)

        assert analysis.avg_resolution_effectiveness > 0
        # All painpoints should have > 50% effectiveness
        for pattern in analysis.patterns:
            assert pattern.avg_effectiveness > 50

    def test_identify_painpoint_patterns_features(
        self, sample_painpoints: list[PainpointResolved]
    ) -> None:
        """Test features addressing painpoints."""
        analysis = identify_painpoint_patterns(sample_painpoints)

        manual_effort_pattern = next(
            p for p in analysis.patterns if p.category == PainpointCategory.MANUAL_EFFORT
        )

        assert "specify deps add" in manual_effort_pattern.features_addressing
        assert "specify docs generate" in manual_effort_pattern.features_addressing

    def test_identify_painpoint_patterns_top_features(
        self, sample_painpoints: list[PainpointResolved]
    ) -> None:
        """Test top performing features identification."""
        analysis = identify_painpoint_patterns(sample_painpoints)

        assert len(analysis.top_performing_features) > 0
        # Should be sorted by effectiveness (descending)
        if len(analysis.top_performing_features) > 1:
            assert analysis.top_performing_features[0][1] >= analysis.top_performing_features[1][1]

    def test_identify_painpoint_patterns_occurrence_count(
        self, sample_painpoints: list[PainpointResolved]
    ) -> None:
        """Test pattern occurrence counting."""
        analysis = identify_painpoint_patterns(sample_painpoints)

        manual_effort_pattern = next(
            p for p in analysis.patterns if p.category == PainpointCategory.MANUAL_EFFORT
        )

        # MANUAL_EFFORT appears twice
        assert manual_effort_pattern.occurrence_count == 2

    def test_identify_painpoint_patterns_severity_averages(
        self, sample_painpoints: list[PainpointResolved]
    ) -> None:
        """Test average severity before/after calculation."""
        analysis = identify_painpoint_patterns(sample_painpoints)

        for pattern in analysis.patterns:
            # Severity after should be less than severity before
            assert pattern.avg_severity_after < pattern.avg_severity_before

    def test_identify_painpoint_patterns_most_common_description(
        self, sample_painpoints: list[PainpointResolved]
    ) -> None:
        """Test most common description identification."""
        analysis = identify_painpoint_patterns(sample_painpoints)

        manual_effort_pattern = next(
            p for p in analysis.patterns if p.category == PainpointCategory.MANUAL_EFFORT
        )

        # Should have a description
        assert manual_effort_pattern.most_common_description is not None


# =============================================================================
# Edge Cases and Error Handling
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_calculate_outcome_metrics_single_outcome(self) -> None:
        """Test metrics calculation with single outcome."""
        outcome = OutcomeAchieved(
            outcome_id="test",
            metric="test",
            expected_value=100.0,
            actual_value=100.0,
            feature="test",
        )

        metrics = calculate_outcome_metrics([outcome])

        assert metrics.total_outcomes == 1
        assert metrics.avg_achievement_rate == 100.0
        assert metrics.median_achievement_rate == 100.0

    def test_analyze_job_feature_mapping_no_features(self) -> None:
        """Test mapping analysis with jobs missing features."""
        jobs = [
            {
                "job_id": "test",
                "persona": "test",
                "status": "completed",
            }
        ]

        mappings = analyze_job_feature_mapping(jobs)

        # Should skip jobs with no features (features_list is empty, filtered out)
        # Based on the code, if features_list is empty after filtering, it continues
        assert len(mappings) == 0

    def test_calculate_satisfaction_scores_all_promoters(self) -> None:
        """Test NPS calculation with all promoters."""
        feedback = [
            UserSatisfaction(
                outcome_id="test",
                feature="test",
                persona="test",
                satisfaction_level=SatisfactionLevel.VERY_SATISFIED,
                met_expectations=True,
                would_recommend=True,
            )
            for _ in range(5)
        ]

        scores = calculate_satisfaction_scores(feedback)

        # All promoters, no detractors = 100 NPS
        assert scores.nps_score == 100.0

    def test_calculate_satisfaction_scores_all_detractors(self) -> None:
        """Test NPS calculation with all detractors."""
        feedback = [
            UserSatisfaction(
                outcome_id="test",
                feature="test",
                persona="test",
                satisfaction_level=SatisfactionLevel.VERY_DISSATISFIED,
                met_expectations=False,
                would_recommend=False,
            )
            for _ in range(5)
        ]

        scores = calculate_satisfaction_scores(feedback)

        # All detractors, no promoters = -100 NPS
        assert scores.nps_score == -100.0

    def test_identify_painpoint_patterns_single_category(self) -> None:
        """Test pattern identification with single category."""
        painpoints = [
            PainpointResolved(
                painpoint_id=f"test-{i}",
                category=PainpointCategory.MANUAL_EFFORT,
                description="Test",
                feature="test",
                persona="test",
                severity_before=8,
                severity_after=2,
            )
            for i in range(3)
        ]

        analysis = identify_painpoint_patterns(painpoints)

        assert len(analysis.patterns) == 1
        assert analysis.patterns[0].occurrence_count == 3
