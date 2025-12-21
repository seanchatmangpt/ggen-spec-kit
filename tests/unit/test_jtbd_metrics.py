"""
Unit tests for specify_cli.core.jtbd_metrics module.

Tests JTBD metrics collection, tracking, and OpenTelemetry integration.
"""

from __future__ import annotations

import time
from datetime import datetime
from unittest.mock import MagicMock, patch

from specify_cli.core.jtbd_metrics import (
    JobCompletion,
    JobStatus,
    OutcomeAchieved,
    OutcomeStatus,
    PainpointCategory,
    PainpointResolved,
    SatisfactionLevel,
    TimeToOutcome,
    UserSatisfaction,
    track_job_completion,
    track_outcome_achieved,
    track_painpoint_resolved,
    track_time_to_outcome,
    track_user_satisfaction,
)

# =============================================================================
# JobCompletion Tests
# =============================================================================


class TestJobCompletion:
    """Tests for JobCompletion class."""

    def test_job_completion_creation(self) -> None:
        """Test creating a JobCompletion instance."""
        job = JobCompletion(
            job_id="deps-add",
            persona="python-developer",
            feature_used="specify deps add",
            context={"package": "httpx"},
        )

        assert job.job_id == "deps-add"
        assert job.persona == "python-developer"
        assert job.feature_used == "specify deps add"
        assert job.status == JobStatus.STARTED
        assert job.context == {"package": "httpx"}
        assert isinstance(job.started_at, datetime)
        assert job.completed_at is None
        assert job.duration_seconds is None

    def test_job_completion_complete(self) -> None:
        """Test completing a job."""
        job = JobCompletion(
            job_id="deps-add", persona="python-developer", feature_used="specify deps add"
        )

        time.sleep(0.01)  # Small delay to ensure duration > 0
        job.complete()

        assert job.status == JobStatus.COMPLETED
        assert job.completed_at is not None
        assert job.duration_seconds is not None
        assert job.duration_seconds > 0

    def test_job_completion_fail(self) -> None:
        """Test failing a job."""
        job = JobCompletion(
            job_id="deps-add", persona="python-developer", feature_used="specify deps add"
        )

        job.fail(reason="Package not found")

        assert job.status == JobStatus.FAILED
        assert job.context["failure_reason"] == "Package not found"

    def test_job_completion_fail_no_reason(self) -> None:
        """Test failing a job without reason."""
        job = JobCompletion(
            job_id="deps-add", persona="python-developer", feature_used="specify deps add"
        )

        job.fail()

        assert job.status == JobStatus.FAILED
        assert "failure_reason" not in job.context


# =============================================================================
# OutcomeAchieved Tests
# =============================================================================


class TestOutcomeAchieved:
    """Tests for OutcomeAchieved class."""

    def test_outcome_achieved_creation(self) -> None:
        """Test creating an OutcomeAchieved instance."""
        outcome = OutcomeAchieved(
            outcome_id="faster-dependency-management",
            metric="time_saved_seconds",
            expected_value=30.0,
            actual_value=8.5,
            feature="specify deps add",
            persona="python-developer",
        )

        assert outcome.outcome_id == "faster-dependency-management"
        assert outcome.metric == "time_saved_seconds"
        assert outcome.expected_value == 30.0
        assert outcome.actual_value == 8.5
        assert outcome.feature == "specify deps add"
        assert outcome.persona == "python-developer"
        assert outcome.status == OutcomeStatus.ACHIEVED

    def test_outcome_achievement_rate(self) -> None:
        """Test achievement rate calculation."""
        outcome = OutcomeAchieved(
            outcome_id="faster-dependency-management",
            metric="time_saved_seconds",
            expected_value=30.0,
            actual_value=15.0,
            feature="specify deps add",
        )

        assert outcome.achievement_rate == 50.0

    def test_outcome_achievement_rate_zero_expected(self) -> None:
        """Test achievement rate with zero expected value."""
        outcome = OutcomeAchieved(
            outcome_id="test",
            metric="count",
            expected_value=0.0,
            actual_value=5.0,
            feature="test",
        )

        assert outcome.achievement_rate == 100.0

    def test_outcome_exceeds_expectations(self) -> None:
        """Test exceeds_expectations property."""
        outcome1 = OutcomeAchieved(
            outcome_id="test",
            metric="speed",
            expected_value=30.0,
            actual_value=50.0,
            feature="test",
        )
        assert outcome1.exceeds_expectations is True

        outcome2 = OutcomeAchieved(
            outcome_id="test",
            metric="speed",
            expected_value=30.0,
            actual_value=20.0,
            feature="test",
        )
        assert outcome2.exceeds_expectations is False

    def test_outcome_determine_status(self) -> None:
        """Test status determination based on achievement rate."""
        # 100%+ = ACHIEVED
        outcome1 = OutcomeAchieved(
            outcome_id="test",
            metric="speed",
            expected_value=30.0,
            actual_value=30.0,
            feature="test",
        )
        assert outcome1.determine_status() == OutcomeStatus.ACHIEVED

        # 75-99% = PARTIALLY_ACHIEVED
        outcome2 = OutcomeAchieved(
            outcome_id="test",
            metric="speed",
            expected_value=30.0,
            actual_value=25.0,
            feature="test",
        )
        assert outcome2.determine_status() == OutcomeStatus.PARTIALLY_ACHIEVED

        # 1-74% = IN_PROGRESS
        outcome3 = OutcomeAchieved(
            outcome_id="test",
            metric="speed",
            expected_value=30.0,
            actual_value=10.0,
            feature="test",
        )
        assert outcome3.determine_status() == OutcomeStatus.IN_PROGRESS

        # 0% = NOT_ACHIEVED
        outcome4 = OutcomeAchieved(
            outcome_id="test",
            metric="speed",
            expected_value=30.0,
            actual_value=0.0,
            feature="test",
        )
        assert outcome4.determine_status() == OutcomeStatus.NOT_ACHIEVED


# =============================================================================
# PainpointResolved Tests
# =============================================================================


class TestPainpointResolved:
    """Tests for PainpointResolved class."""

    def test_painpoint_resolved_creation(self) -> None:
        """Test creating a PainpointResolved instance."""
        painpoint = PainpointResolved(
            painpoint_id="manual-dependency-updates",
            category=PainpointCategory.MANUAL_EFFORT,
            description="Manually updating pyproject.toml",
            feature="specify deps add",
            persona="python-developer",
            severity_before=8,
            severity_after=2,
        )

        assert painpoint.painpoint_id == "manual-dependency-updates"
        assert painpoint.category == PainpointCategory.MANUAL_EFFORT
        assert painpoint.description == "Manually updating pyproject.toml"
        assert painpoint.feature == "specify deps add"
        assert painpoint.persona == "python-developer"
        assert painpoint.severity_before == 8
        assert painpoint.severity_after == 2

    def test_painpoint_resolution_effectiveness(self) -> None:
        """Test resolution effectiveness calculation."""
        painpoint = PainpointResolved(
            painpoint_id="test",
            category=PainpointCategory.MANUAL_EFFORT,
            description="Test painpoint",
            feature="test",
            persona="test",
            severity_before=10,
            severity_after=2,
        )

        assert painpoint.resolution_effectiveness == 80.0

    def test_painpoint_resolution_effectiveness_zero_before(self) -> None:
        """Test resolution effectiveness with zero severity before."""
        painpoint = PainpointResolved(
            painpoint_id="test",
            category=PainpointCategory.MANUAL_EFFORT,
            description="Test painpoint",
            feature="test",
            persona="test",
            severity_before=0,
            severity_after=0,
        )

        assert painpoint.resolution_effectiveness == 0.0


# =============================================================================
# TimeToOutcome Tests
# =============================================================================


class TestTimeToOutcome:
    """Tests for TimeToOutcome class."""

    def test_time_to_outcome_creation(self) -> None:
        """Test creating a TimeToOutcome instance."""
        tto = TimeToOutcome(
            outcome_id="dependency-added",
            persona="python-developer",
            feature="specify deps add",
        )

        assert tto.outcome_id == "dependency-added"
        assert tto.persona == "python-developer"
        assert tto.feature == "specify deps add"
        assert tto.start_time > 0
        assert tto.end_time is None
        assert tto.duration_seconds is None
        assert tto.steps == []

    def test_time_to_outcome_add_step(self) -> None:
        """Test adding steps to journey."""
        tto = TimeToOutcome(
            outcome_id="dependency-added",
            persona="python-developer",
            feature="specify deps add",
        )

        tto.add_step("parse_args")
        tto.add_step("validate_package")
        tto.add_step("update_pyproject")

        assert tto.steps == ["parse_args", "validate_package", "update_pyproject"]

    def test_time_to_outcome_complete(self) -> None:
        """Test completing time-to-outcome measurement."""
        tto = TimeToOutcome(
            outcome_id="dependency-added",
            persona="python-developer",
            feature="specify deps add",
        )

        time.sleep(0.01)  # Small delay
        tto.complete()

        assert tto.end_time is not None
        assert tto.duration_seconds is not None
        assert tto.duration_seconds > 0


# =============================================================================
# UserSatisfaction Tests
# =============================================================================


class TestUserSatisfaction:
    """Tests for UserSatisfaction class."""

    def test_user_satisfaction_creation(self) -> None:
        """Test creating a UserSatisfaction instance."""
        satisfaction = UserSatisfaction(
            outcome_id="faster-dependency-management",
            feature="specify deps add",
            persona="python-developer",
            satisfaction_level=SatisfactionLevel.VERY_SATISFIED,
            met_expectations=True,
            would_recommend=True,
            effort_score=2,
            feedback_text="Great feature!",
        )

        assert satisfaction.outcome_id == "faster-dependency-management"
        assert satisfaction.feature == "specify deps add"
        assert satisfaction.persona == "python-developer"
        assert satisfaction.satisfaction_level == SatisfactionLevel.VERY_SATISFIED
        assert satisfaction.met_expectations is True
        assert satisfaction.would_recommend is True
        assert satisfaction.effort_score == 2
        assert satisfaction.feedback_text == "Great feature!"

    def test_user_satisfaction_minimal(self) -> None:
        """Test creating minimal UserSatisfaction instance."""
        satisfaction = UserSatisfaction(
            outcome_id="test",
            feature="test",
            persona="test",
            satisfaction_level=SatisfactionLevel.NEUTRAL,
            met_expectations=False,
            would_recommend=False,
        )

        assert satisfaction.effort_score is None
        assert satisfaction.feedback_text is None


# =============================================================================
# Tracking Function Tests
# =============================================================================


class TestTrackingFunctions:
    """Tests for JTBD tracking functions."""

    @patch("specify_cli.core.jtbd_metrics.add_span_event")
    @patch("specify_cli.core.jtbd_metrics.get_current_span")
    @patch("specify_cli.core.jtbd_metrics.metric_counter")
    @patch("specify_cli.core.jtbd_metrics.metric_histogram")
    @patch("specify_cli.core.jtbd_metrics.metric_gauge")
    def test_track_job_completion(
        self,
        mock_gauge: MagicMock,
        mock_histogram: MagicMock,
        mock_counter: MagicMock,
        mock_span: MagicMock,
        mock_event: MagicMock,
    ) -> None:
        """Test tracking job completion."""
        # Setup mocks
        mock_span_obj = MagicMock()
        mock_span_obj.is_recording.return_value = True
        mock_span.return_value = mock_span_obj

        mock_counter_func = MagicMock()
        mock_counter.return_value = mock_counter_func

        mock_histogram_func = MagicMock()
        mock_histogram.return_value = mock_histogram_func

        mock_gauge_func = MagicMock()
        mock_gauge.return_value = mock_gauge_func

        # Create and track job
        job = JobCompletion(
            job_id="deps-add",
            persona="python-developer",
            feature_used="specify deps add",
            context={"package": "httpx"},
        )
        job.complete()

        track_job_completion(job)

        # Verify event was added
        mock_event.assert_called_once()
        event_name, event_attrs = mock_event.call_args[0]
        assert event_name == "jtbd.job.complete"  # Semantic convention name
        assert event_attrs["jtbd.job.id"] == "deps-add"
        assert event_attrs["jtbd.job.persona"] == "python-developer"
        assert event_attrs["jtbd.job.feature"] == "specify deps add"

        # Verify counter was called (metrics collector creates several counters)
        assert mock_counter.call_count >= 1

    @patch("specify_cli.core.jtbd_metrics._JTBD_METRICS_COLLECTOR", None)
    @patch("specify_cli.core.jtbd_metrics.add_span_event")
    @patch("specify_cli.core.jtbd_metrics.get_current_span")
    @patch("specify_cli.core.jtbd_metrics.metric_counter")
    @patch("specify_cli.core.jtbd_metrics.metric_histogram")
    @patch("specify_cli.core.jtbd_metrics.metric_gauge")
    def test_track_outcome_achieved(
        self,
        mock_gauge: MagicMock,
        mock_histogram: MagicMock,
        mock_counter: MagicMock,
        mock_span: MagicMock,
        mock_event: MagicMock,
    ) -> None:
        """Test tracking outcome achievement."""
        # Setup mocks
        mock_span_obj = MagicMock()
        mock_span_obj.is_recording.return_value = True
        mock_span.return_value = mock_span_obj

        mock_counter_func = MagicMock()
        mock_counter.return_value = mock_counter_func

        mock_histogram_func = MagicMock()
        mock_histogram.return_value = mock_histogram_func

        mock_gauge_func = MagicMock()
        mock_gauge.return_value = mock_gauge_func

        # Create and track outcome
        outcome = OutcomeAchieved(
            outcome_id="faster-dependency-management",
            metric="time_saved_seconds",
            expected_value=30.0,
            actual_value=8.5,
            feature="specify deps add",
            persona="python-developer",
        )

        track_outcome_achieved(outcome)

        # Verify event was added
        mock_event.assert_called_once()
        event_name, event_attrs = mock_event.call_args[0]
        assert event_name == "jtbd.outcome.achieve"  # Semantic convention name
        assert event_attrs["jtbd.outcome.id"] == "faster-dependency-management"
        assert event_attrs["jtbd.outcome.actual"] == 8.5

        # Verify metrics were called (collector creates several)
        assert mock_counter.call_count >= 1
        assert mock_histogram.call_count >= 1

    @patch("specify_cli.core.jtbd_metrics._JTBD_METRICS_COLLECTOR", None)
    @patch("specify_cli.core.jtbd_metrics.add_span_event")
    @patch("specify_cli.core.jtbd_metrics.get_current_span")
    @patch("specify_cli.core.jtbd_metrics.metric_counter")
    @patch("specify_cli.core.jtbd_metrics.metric_histogram")
    @patch("specify_cli.core.jtbd_metrics.metric_gauge")
    def test_track_painpoint_resolved(
        self,
        mock_gauge: MagicMock,
        mock_histogram: MagicMock,
        mock_counter: MagicMock,
        mock_span: MagicMock,
        mock_event: MagicMock,
    ) -> None:
        """Test tracking painpoint resolution."""
        # Setup mocks
        mock_span_obj = MagicMock()
        mock_span_obj.is_recording.return_value = True
        mock_span.return_value = mock_span_obj

        mock_counter_func = MagicMock()
        mock_counter.return_value = mock_counter_func

        mock_histogram_func = MagicMock()
        mock_histogram.return_value = mock_histogram_func

        mock_gauge_func = MagicMock()
        mock_gauge.return_value = mock_gauge_func

        # Create and track painpoint
        painpoint = PainpointResolved(
            painpoint_id="manual-dependency-updates",
            category=PainpointCategory.MANUAL_EFFORT,
            description="Manually updating pyproject.toml",
            feature="specify deps add",
            persona="python-developer",
            severity_before=8,
            severity_after=2,
        )

        track_painpoint_resolved(painpoint)

        # Verify event was added
        mock_event.assert_called_once()
        event_name, event_attrs = mock_event.call_args[0]
        assert event_name == "jtbd.painpoint.resolve"  # Semantic convention name
        assert event_attrs["jtbd.painpoint.id"] == "manual-dependency-updates"
        assert event_attrs["jtbd.painpoint.category"] == "manual_effort"

        # Verify metrics were called (collector creates several)
        assert mock_counter.call_count >= 1
        assert mock_histogram.call_count >= 1

    @patch("specify_cli.core.jtbd_metrics._JTBD_METRICS_COLLECTOR", None)
    @patch("specify_cli.core.jtbd_metrics.add_span_event")
    @patch("specify_cli.core.jtbd_metrics.get_current_span")
    @patch("specify_cli.core.jtbd_metrics.metric_counter")
    @patch("specify_cli.core.jtbd_metrics.metric_histogram")
    @patch("specify_cli.core.jtbd_metrics.metric_gauge")
    def test_track_time_to_outcome(
        self,
        mock_gauge: MagicMock,
        mock_histogram: MagicMock,
        mock_counter: MagicMock,
        mock_span: MagicMock,
        mock_event: MagicMock,
    ) -> None:
        """Test tracking time-to-outcome."""
        # Setup mocks
        mock_span_obj = MagicMock()
        mock_span_obj.is_recording.return_value = True
        mock_span.return_value = mock_span_obj

        mock_histogram_func = MagicMock()
        mock_histogram.return_value = mock_histogram_func

        mock_gauge_func = MagicMock()
        mock_gauge.return_value = mock_gauge_func

        mock_counter_func = MagicMock()
        mock_counter.return_value = mock_counter_func

        # Create and track time-to-outcome
        tto = TimeToOutcome(
            outcome_id="dependency-added",
            persona="python-developer",
            feature="specify deps add",
        )
        tto.add_step("parse_args")
        tto.add_step("validate_package")
        tto.complete()

        track_time_to_outcome(tto)

        # Verify event was added
        mock_event.assert_called_once()
        event_name, event_attrs = mock_event.call_args[0]
        assert event_name == "jtbd.tto.complete"  # Semantic convention name
        assert event_attrs["jtbd.tto.outcome_id"] == "dependency-added"
        assert event_attrs["jtbd.tto.steps_count"] == 2

        # Verify histogram was called (collector creates several)
        assert mock_histogram.call_count >= 1

    @patch("specify_cli.core.jtbd_metrics._JTBD_METRICS_COLLECTOR", None)
    @patch("specify_cli.core.jtbd_metrics.add_span_event")
    @patch("specify_cli.core.jtbd_metrics.get_current_span")
    @patch("specify_cli.core.jtbd_metrics.metric_counter")
    @patch("specify_cli.core.jtbd_metrics.metric_histogram")
    @patch("specify_cli.core.jtbd_metrics.metric_gauge")
    def test_track_time_to_outcome_not_completed(
        self,
        mock_gauge: MagicMock,
        mock_histogram: MagicMock,
        mock_counter: MagicMock,
        mock_span: MagicMock,
        mock_event: MagicMock,
    ) -> None:
        """Test tracking time-to-outcome that hasn't completed."""
        tto = TimeToOutcome(
            outcome_id="dependency-added",
            persona="python-developer",
            feature="specify deps add",
        )

        # Don't complete it
        track_time_to_outcome(tto)

        # Should not add event if not completed
        mock_event.assert_not_called()

    @patch("specify_cli.core.jtbd_metrics._JTBD_METRICS_COLLECTOR", None)
    @patch("specify_cli.core.jtbd_metrics.add_span_event")
    @patch("specify_cli.core.jtbd_metrics.get_current_span")
    @patch("specify_cli.core.jtbd_metrics.metric_counter")
    @patch("specify_cli.core.jtbd_metrics.metric_histogram")
    @patch("specify_cli.core.jtbd_metrics.metric_gauge")
    def test_track_user_satisfaction(
        self,
        mock_gauge: MagicMock,
        mock_histogram: MagicMock,
        mock_counter: MagicMock,
        mock_span: MagicMock,
        mock_event: MagicMock,
    ) -> None:
        """Test tracking user satisfaction."""
        # Setup mocks
        mock_span_obj = MagicMock()
        mock_span_obj.is_recording.return_value = True
        mock_span.return_value = mock_span_obj

        mock_counter_func = MagicMock()
        mock_counter.return_value = mock_counter_func

        mock_histogram_func = MagicMock()
        mock_histogram.return_value = mock_histogram_func

        mock_gauge_func = MagicMock()
        mock_gauge.return_value = mock_gauge_func

        # Create and track satisfaction
        satisfaction = UserSatisfaction(
            outcome_id="faster-dependency-management",
            feature="specify deps add",
            persona="python-developer",
            satisfaction_level=SatisfactionLevel.VERY_SATISFIED,
            met_expectations=True,
            would_recommend=True,
            effort_score=2,
        )

        track_user_satisfaction(satisfaction)

        # Verify event was added
        mock_event.assert_called_once()
        event_name, event_attrs = mock_event.call_args[0]
        assert event_name == "jtbd.satisfaction.record"  # Semantic convention name
        assert event_attrs["jtbd.satisfaction.level"] == "very_satisfied"
        assert event_attrs["jtbd.satisfaction.met_expectations"] is True

        # Verify metrics were called (collector creates several)
        assert mock_counter.call_count >= 1
        assert mock_histogram.call_count >= 1


# =============================================================================
# Integration Tests
# =============================================================================


class TestJTBDMetricsIntegration:
    """Integration tests for JTBD metrics."""

    @patch("specify_cli.core.jtbd_metrics.add_span_event")
    @patch("specify_cli.core.jtbd_metrics.get_current_span")
    @patch("specify_cli.core.jtbd_metrics.metric_counter")
    @patch("specify_cli.core.jtbd_metrics.metric_histogram")
    @patch("specify_cli.core.jtbd_metrics.metric_gauge")
    def test_complete_jtbd_flow(
        self,
        mock_gauge: MagicMock,
        mock_histogram: MagicMock,
        mock_counter: MagicMock,
        mock_span: MagicMock,
        mock_event: MagicMock,
    ) -> None:
        """Test complete JTBD tracking flow."""
        # Setup mocks
        mock_span_obj = MagicMock()
        mock_span_obj.is_recording.return_value = True
        mock_span.return_value = mock_span_obj

        mock_counter_func = MagicMock()
        mock_counter.return_value = mock_counter_func

        mock_histogram_func = MagicMock()
        mock_histogram.return_value = mock_histogram_func

        # 1. Start job
        job = JobCompletion(
            job_id="deps-add",
            persona="python-developer",
            feature_used="specify deps add",
        )

        # 2. Start time-to-outcome tracking
        tto = TimeToOutcome(
            outcome_id="dependency-added",
            persona="python-developer",
            feature="specify deps add",
        )
        tto.add_step("parse_args")
        tto.add_step("validate_package")

        # 3. Complete job
        job.complete()
        track_job_completion(job)

        # 4. Track outcome achievement
        outcome = OutcomeAchieved(
            outcome_id="faster-dependency-management",
            metric="time_saved_seconds",
            expected_value=30.0,
            actual_value=8.5,
            feature="specify deps add",
            persona="python-developer",
        )
        track_outcome_achieved(outcome)

        # 5. Track painpoint resolution
        painpoint = PainpointResolved(
            painpoint_id="manual-dependency-updates",
            category=PainpointCategory.MANUAL_EFFORT,
            description="Manually updating pyproject.toml",
            feature="specify deps add",
            persona="python-developer",
            severity_before=8,
            severity_after=2,
        )
        track_painpoint_resolved(painpoint)

        # 6. Complete time-to-outcome
        tto.complete()
        track_time_to_outcome(tto)

        # 7. Track satisfaction
        satisfaction = UserSatisfaction(
            outcome_id="faster-dependency-management",
            feature="specify deps add",
            persona="python-developer",
            satisfaction_level=SatisfactionLevel.VERY_SATISFIED,
            met_expectations=True,
            would_recommend=True,
            effort_score=2,
        )
        track_user_satisfaction(satisfaction)

        # Verify all events were tracked (semantic convention names)
        assert mock_event.call_count == 5
        event_names = [call[0][0] for call in mock_event.call_args_list]
        assert "jtbd.job.complete" in event_names
        assert "jtbd.outcome.achieve" in event_names
        assert "jtbd.painpoint.resolve" in event_names
        assert "jtbd.tto.complete" in event_names
        assert "jtbd.satisfaction.record" in event_names
