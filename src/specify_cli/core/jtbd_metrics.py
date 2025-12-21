"""
specify_cli.core.jtbd_metrics
------------------------------
Jobs-to-be-Done (JTBD) metrics collection framework for spec-kit.

This module provides comprehensive tracking of JTBD outcomes, measuring:
- Job completion rates by persona
- Outcome achievement metrics
- Painpoint resolution tracking
- Time-to-outcome measurements
- User satisfaction scores

The framework integrates with OpenTelemetry to provide distributed tracing
of user outcomes across the entire customer journey.

Core Classes
------------
- JobCompletion: Track which jobs are completed by users
- OutcomeAchieved: Measure outcome delivery and success
- PainpointResolved: Track painpoint elimination
- TimeToOutcome: Measure time required to achieve outcomes
- UserSatisfaction: Capture satisfaction with outcome delivery

Example
-------
    from specify_cli.core.jtbd_metrics import (
        JobCompletion, OutcomeAchieved, track_job_completion
    )

    # Track a job completion
    job = JobCompletion(
        job_id="deps-add",
        persona="python-developer",
        feature_used="specify deps add",
        context={"package": "httpx"}
    )
    track_job_completion(job)

    # Track outcome achievement
    outcome = OutcomeAchieved(
        outcome_id="faster-dependency-management",
        metric="time_saved_seconds",
        expected_value=30.0,
        actual_value=8.5,
        feature="specify deps add"
    )
    track_outcome_achieved(outcome)

Reference
---------
JTBD Framework: https://jobs-to-be-done.com/
Outcome-Driven Innovation: https://strategyn.com/outcome-driven-innovation/
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from .instrumentation import add_span_event
from .semconv import JTBDAttributes, JTBDOperations
from .telemetry import (
    get_current_span,
    metric_counter,
    metric_gauge,
    metric_histogram,
)

__all__ = [
    "JTBDMetricsCollector",
    "JobCompletion",
    "JobStatus",
    "OutcomeAchieved",
    "OutcomeStatus",
    "PainpointCategory",
    "PainpointResolved",
    "SatisfactionLevel",
    "TimeToOutcome",
    "UserSatisfaction",
    "get_jtbd_metrics_collector",
    "track_job_completion",
    "track_outcome_achieved",
    "track_painpoint_resolved",
    "track_time_to_outcome",
    "track_user_satisfaction",
]


# =============================================================================
# Enums
# =============================================================================


class JobStatus(str, Enum):
    """Job completion status."""

    STARTED = "started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ABANDONED = "abandoned"


class OutcomeStatus(str, Enum):
    """Outcome achievement status."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    ACHIEVED = "achieved"
    PARTIALLY_ACHIEVED = "partially_achieved"
    NOT_ACHIEVED = "not_achieved"


class PainpointCategory(str, Enum):
    """Categories of painpoints that features resolve."""

    TIME_WASTED = "time_wasted"  # Inefficient processes
    COGNITIVE_LOAD = "cognitive_load"  # Mental complexity
    MANUAL_EFFORT = "manual_effort"  # Repetitive tasks
    ERROR_PRONE = "error_prone"  # Quality/reliability issues
    LACK_OF_CONTROL = "lack_of_control"  # Limited flexibility
    LACK_OF_VISIBILITY = "lack_of_visibility"  # Poor observability
    INTEGRATION_FRICTION = "integration_friction"  # Tool compatibility
    LEARNING_CURVE = "learning_curve"  # Difficulty to learn


class SatisfactionLevel(str, Enum):
    """User satisfaction with outcome delivery."""

    VERY_DISSATISFIED = "very_dissatisfied"
    DISSATISFIED = "dissatisfied"
    NEUTRAL = "neutral"
    SATISFIED = "satisfied"
    VERY_SATISFIED = "very_satisfied"


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class JobCompletion:
    """
    Track which job was completed by a user.

    A "job" is a high-level task the user wants to accomplish (e.g., "add dependency",
    "generate documentation", "validate RDF specs").

    Attributes
    ----------
    job_id : str
        Unique identifier for the job type.
    persona : str
        User persona completing the job (e.g., "python-developer", "devops-engineer").
    feature_used : str
        Feature/command used to complete the job.
    status : JobStatus
        Current status of the job.
    context : dict[str, Any]
        Additional context about the job execution.
    started_at : datetime
        When the job started.
    completed_at : datetime, optional
        When the job completed.
    duration_seconds : float, optional
        Time taken to complete the job.
    """

    job_id: str
    persona: str
    feature_used: str
    status: JobStatus = JobStatus.STARTED
    context: dict[str, Any] = field(default_factory=dict)
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None
    duration_seconds: float | None = None

    def complete(self) -> None:
        """Mark the job as completed and calculate duration."""
        self.status = JobStatus.COMPLETED
        self.completed_at = datetime.now(UTC)
        self.duration_seconds = (self.completed_at - self.started_at).total_seconds()

    def fail(self, reason: str | None = None) -> None:
        """Mark the job as failed."""
        self.status = JobStatus.FAILED
        if reason:
            self.context["failure_reason"] = reason


@dataclass
class OutcomeAchieved:
    """
    Track outcome achievement and measure against success criteria.

    An "outcome" is a measurable result the user wants (e.g., "faster dependency
    management", "higher code quality", "better observability").

    Attributes
    ----------
    outcome_id : str
        Unique identifier for the outcome type.
    metric : str
        Metric being measured (e.g., "time_saved_seconds", "error_reduction_percent").
    expected_value : float
        Expected/target value for the outcome.
    actual_value : float
        Actual value achieved.
    feature : str
        Feature that delivered the outcome.
    persona : str, optional
        User persona achieving the outcome.
    status : OutcomeStatus
        Status of outcome achievement.
    context : dict[str, Any]
        Additional context about outcome delivery.
    measured_at : datetime
        When the outcome was measured.
    """

    outcome_id: str
    metric: str
    expected_value: float
    actual_value: float
    feature: str
    persona: str | None = None
    status: OutcomeStatus = OutcomeStatus.ACHIEVED
    context: dict[str, Any] = field(default_factory=dict)
    measured_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def achievement_rate(self) -> float:
        """
        Calculate achievement rate as a percentage.

        Returns
        -------
        float
            Percentage of expected outcome achieved.
        """
        if self.expected_value == 0:
            return 100.0 if self.actual_value >= 0 else 0.0
        return (self.actual_value / self.expected_value) * 100.0

    @property
    def exceeds_expectations(self) -> bool:
        """Check if outcome exceeded expectations."""
        return self.actual_value > self.expected_value

    def determine_status(self) -> OutcomeStatus:
        """
        Determine outcome status based on achievement rate.

        Returns
        -------
        OutcomeStatus
            Status based on achievement percentage.
        """
        rate = self.achievement_rate
        if rate >= 100:
            return OutcomeStatus.ACHIEVED
        if rate >= 75:
            return OutcomeStatus.PARTIALLY_ACHIEVED
        if rate > 0:
            return OutcomeStatus.IN_PROGRESS
        return OutcomeStatus.NOT_ACHIEVED


@dataclass
class PainpointResolved:
    """
    Track which painpoints were resolved by a feature.

    Painpoints are specific problems/frustrations users experience that
    features aim to eliminate.

    Attributes
    ----------
    painpoint_id : str
        Unique identifier for the painpoint.
    category : PainpointCategory
        Category of painpoint.
    description : str
        Human-readable description of the painpoint.
    feature : str
        Feature that resolved the painpoint.
    persona : str
        User persona experiencing the painpoint.
    severity_before : int
        Severity rating before resolution (1-10).
    severity_after : int
        Severity rating after resolution (1-10).
    resolution_effectiveness : float, optional
        Calculated effectiveness of resolution.
    context : dict[str, Any]
        Additional context about painpoint resolution.
    resolved_at : datetime
        When the painpoint was resolved.
    """

    painpoint_id: str
    category: PainpointCategory
    description: str
    feature: str
    persona: str
    severity_before: int  # 1-10 scale
    severity_after: int  # 1-10 scale
    resolution_effectiveness: float | None = None
    context: dict[str, Any] = field(default_factory=dict)
    resolved_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        """Calculate resolution effectiveness."""
        if self.severity_before > 0:
            reduction = self.severity_before - self.severity_after
            self.resolution_effectiveness = (reduction / self.severity_before) * 100.0
        else:
            self.resolution_effectiveness = 0.0


@dataclass
class TimeToOutcome:
    """
    Measure time required to achieve an outcome.

    Tracks the entire customer journey from job start to outcome achievement.

    Attributes
    ----------
    outcome_id : str
        Identifier for the outcome being measured.
    persona : str
        User persona achieving the outcome.
    feature : str
        Feature used to achieve the outcome.
    start_time : float
        Start timestamp (Unix time).
    end_time : float, optional
        End timestamp (Unix time).
    duration_seconds : float, optional
        Total time to achieve outcome.
    steps : list[str]
        Steps taken to achieve the outcome.
    context : dict[str, Any]
        Additional context about the journey.
    """

    outcome_id: str
    persona: str
    feature: str
    start_time: float = field(default_factory=time.time)
    end_time: float | None = None
    duration_seconds: float | None = None
    steps: list[str] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)

    def add_step(self, step: str) -> None:
        """Add a step to the journey."""
        self.steps.append(step)

    def complete(self) -> None:
        """Mark the outcome as achieved and calculate duration."""
        self.end_time = time.time()
        self.duration_seconds = self.end_time - self.start_time


@dataclass
class UserSatisfaction:
    """
    Track user satisfaction with outcome achievement.

    Captures whether the feature/outcome met user expectations.

    Attributes
    ----------
    outcome_id : str
        Identifier for the outcome.
    feature : str
        Feature that delivered the outcome.
    persona : str
        User persona providing feedback.
    satisfaction_level : SatisfactionLevel
        Overall satisfaction rating.
    met_expectations : bool
        Whether outcome met expectations.
    would_recommend : bool
        Whether user would recommend the feature.
    effort_score : int, optional
        Customer Effort Score (1-7, lower is better).
    feedback_text : str, optional
        Qualitative feedback from user.
    context : dict[str, Any]
        Additional context about satisfaction.
    recorded_at : datetime
        When satisfaction was recorded.
    """

    outcome_id: str
    feature: str
    persona: str
    satisfaction_level: SatisfactionLevel
    met_expectations: bool
    would_recommend: bool
    effort_score: int | None = None  # 1-7 (Customer Effort Score)
    feedback_text: str | None = None
    context: dict[str, Any] = field(default_factory=dict)
    recorded_at: datetime = field(default_factory=lambda: datetime.now(UTC))


# =============================================================================
# JTBD Metrics Collector
# =============================================================================


class JTBDMetricsCollector:
    """
    Centralized collector for JTBD metrics with OpenTelemetry integration.

    This class manages all JTBD-specific OTEL metrics and provides a unified
    interface for tracking jobs, outcomes, painpoints, time-to-outcome, and
    satisfaction across the entire customer journey.

    Attributes
    ----------
    job_completion_counter : Callable
        Counter for total job completions.
    job_duration_histogram : Callable
        Histogram for job completion durations.
    outcome_achievement_counter : Callable
        Counter for outcome achievements.
    outcome_achievement_rate_histogram : Callable
        Histogram for outcome achievement rates.
    painpoint_resolution_counter : Callable
        Counter for painpoint resolutions.
    painpoint_effectiveness_histogram : Callable
        Histogram for painpoint resolution effectiveness.
    time_to_outcome_histogram : Callable
        Histogram for time-to-outcome measurements.
    satisfaction_counter : Callable
        Counter for satisfaction responses.
    satisfaction_score_gauge : Callable
        Gauge for current satisfaction scores.
    effort_score_histogram : Callable
        Histogram for customer effort scores.

    Example
    -------
    >>> collector = get_jtbd_metrics_collector()
    >>> collector.record_job_completion("deps-add", 5.2)
    >>> collector.record_outcome_achievement("faster-deps", 95.0)
    """

    def __init__(self) -> None:
        """Initialize JTBD metrics collector with OTEL metrics."""
        # Job metrics
        self.job_completion_counter = metric_counter("jtbd.job.completion.count")
        self.job_duration_histogram = metric_histogram("jtbd.job.duration.seconds", unit="s")
        self.job_failure_counter = metric_counter("jtbd.job.failure.count")

        # Outcome metrics
        self.outcome_achievement_counter = metric_counter("jtbd.outcome.achievement.count")
        self.outcome_achievement_rate_histogram = metric_histogram(
            "jtbd.outcome.achievement.rate", unit="%"
        )
        self.outcome_exceeds_expectations_counter = metric_counter(
            "jtbd.outcome.exceeds_expectations.count"
        )

        # Painpoint metrics
        self.painpoint_resolution_counter = metric_counter("jtbd.painpoint.resolution.count")
        self.painpoint_effectiveness_histogram = metric_histogram(
            "jtbd.painpoint.resolution.effectiveness", unit="%"
        )

        # Time-to-Outcome metrics
        self.time_to_outcome_histogram = metric_histogram("jtbd.time_to_outcome.seconds", unit="s")
        self.tto_steps_histogram = metric_histogram("jtbd.time_to_outcome.steps")

        # Satisfaction metrics
        self.satisfaction_counter = metric_counter("jtbd.satisfaction.response.count")
        self.satisfaction_score_gauge = metric_gauge("jtbd.satisfaction.score")
        self.effort_score_histogram = metric_histogram("jtbd.satisfaction.effort_score")
        self.recommendation_counter = metric_counter("jtbd.satisfaction.would_recommend.count")
        self.expectations_met_counter = metric_counter("jtbd.satisfaction.met_expectations.count")

    def record_job_completion(
        self,
        job_id: str,  # noqa: ARG002 - Reserved for future per-job metrics
        duration_seconds: float | None = None,
        status: str = "completed",
    ) -> None:
        """
        Record a job completion event.

        Parameters
        ----------
        job_id : str
            Unique identifier for the job type.
        duration_seconds : float, optional
            Time taken to complete the job.
        status : str, optional
            Job completion status. Default is "completed".
        """
        self.job_completion_counter(1)
        if duration_seconds is not None:
            self.job_duration_histogram(duration_seconds)
        if status == "failed":
            self.job_failure_counter(1)

    def record_outcome_achievement(
        self,
        outcome_id: str,  # noqa: ARG002 - Reserved for future per-outcome metrics
        achievement_rate: float,
        exceeds_expectations: bool = False,
    ) -> None:
        """
        Record an outcome achievement event.

        Parameters
        ----------
        outcome_id : str
            Unique identifier for the outcome.
        achievement_rate : float
            Percentage of expected outcome achieved (0-100+).
        exceeds_expectations : bool, optional
            Whether outcome exceeded expectations. Default is False.
        """
        self.outcome_achievement_counter(1)
        self.outcome_achievement_rate_histogram(achievement_rate)
        if exceeds_expectations:
            self.outcome_exceeds_expectations_counter(1)

    def record_painpoint_resolution(
        self,
        painpoint_id: str,  # noqa: ARG002 - Reserved for future per-painpoint metrics
        effectiveness: float | None = None,
    ) -> None:
        """
        Record a painpoint resolution event.

        Parameters
        ----------
        painpoint_id : str
            Unique identifier for the painpoint.
        effectiveness : float, optional
            Resolution effectiveness percentage (0-100).
        """
        self.painpoint_resolution_counter(1)
        if effectiveness is not None:
            self.painpoint_effectiveness_histogram(effectiveness)

    def record_time_to_outcome(
        self,
        outcome_id: str,  # noqa: ARG002 - Reserved for future per-outcome TTO metrics
        duration_seconds: float,
        steps: int,
    ) -> None:
        """
        Record a time-to-outcome measurement.

        Parameters
        ----------
        outcome_id : str
            Unique identifier for the outcome.
        duration_seconds : float
            Time taken to achieve the outcome.
        steps : int
            Number of steps in the journey.
        """
        self.time_to_outcome_histogram(duration_seconds)
        self.tto_steps_histogram(float(steps))

    def record_satisfaction(
        self,
        outcome_id: str,  # noqa: ARG002 - Reserved for future per-outcome satisfaction metrics
        satisfaction_score: float,
        effort_score: int | None = None,
        met_expectations: bool = False,
        would_recommend: bool = False,
    ) -> None:
        """
        Record user satisfaction metrics.

        Parameters
        ----------
        outcome_id : str
            Unique identifier for the outcome.
        satisfaction_score : float
            Satisfaction score (1-5 scale mapped to 1-100).
        effort_score : int, optional
            Customer effort score (1-7, lower is better).
        met_expectations : bool, optional
            Whether outcome met expectations. Default is False.
        would_recommend : bool, optional
            Whether user would recommend. Default is False.
        """
        self.satisfaction_counter(1)
        self.satisfaction_score_gauge(satisfaction_score)
        if effort_score is not None:
            self.effort_score_histogram(float(effort_score))
        if met_expectations:
            self.expectations_met_counter(1)
        if would_recommend:
            self.recommendation_counter(1)


# Global singleton instance
_JTBD_METRICS_COLLECTOR: JTBDMetricsCollector | None = None


def get_jtbd_metrics_collector() -> JTBDMetricsCollector:
    """
    Get the global JTBD metrics collector instance.

    Returns
    -------
    JTBDMetricsCollector
        The singleton metrics collector instance.

    Example
    -------
    >>> collector = get_jtbd_metrics_collector()
    >>> collector.record_job_completion("deps-add", 5.2)
    """
    global _JTBD_METRICS_COLLECTOR  # noqa: PLW0603 - Singleton pattern for OTEL metrics
    if _JTBD_METRICS_COLLECTOR is None:
        _JTBD_METRICS_COLLECTOR = JTBDMetricsCollector()
    return _JTBD_METRICS_COLLECTOR


# =============================================================================
# Tracking Functions
# =============================================================================


def track_job_completion(job: JobCompletion) -> None:
    """
    Track job completion with OpenTelemetry.

    Creates span events and metrics for job completion tracking.

    Parameters
    ----------
    job : JobCompletion
        Job completion data to track.

    Example
    -------
    >>> job = JobCompletion(
    ...     job_id="deps-add",
    ...     persona="python-developer",
    ...     feature_used="specify deps add"
    ... )
    >>> track_job_completion(job)
    """
    # Create span event using semantic conventions
    event_attrs: dict[str, Any] = {
        JTBDAttributes.JOB_ID: job.job_id,
        JTBDAttributes.JOB_PERSONA: job.persona,
        JTBDAttributes.JOB_FEATURE: job.feature_used,
        JTBDAttributes.JOB_STATUS: job.status.value,
    }

    if job.duration_seconds is not None:
        event_attrs[JTBDAttributes.JOB_DURATION_SECONDS] = job.duration_seconds

    if job.started_at:
        event_attrs[JTBDAttributes.JOB_STARTED_AT] = job.started_at.isoformat()

    if job.completed_at:
        event_attrs[JTBDAttributes.JOB_COMPLETED_AT] = job.completed_at.isoformat()

    # Add context
    event_attrs.update({f"jtbd.job.context.{k}": str(v) for k, v in job.context.items()})

    add_span_event(JTBDOperations.JOB_COMPLETE, event_attrs)

    # Add attributes to current span
    current_span = get_current_span()
    if current_span.is_recording():
        for key, value in event_attrs.items():
            current_span.set_attribute(key, value)

    # Update metrics via collector
    collector = get_jtbd_metrics_collector()
    collector.record_job_completion(job.job_id, job.duration_seconds, status=job.status.value)


def track_outcome_achieved(outcome: OutcomeAchieved) -> None:
    """
    Track outcome achievement with OpenTelemetry.

    Parameters
    ----------
    outcome : OutcomeAchieved
        Outcome achievement data to track.

    Example
    -------
    >>> outcome = OutcomeAchieved(
    ...     outcome_id="faster-dependency-management",
    ...     metric="time_saved_seconds",
    ...     expected_value=30.0,
    ...     actual_value=8.5,
    ...     feature="specify deps add"
    ... )
    >>> track_outcome_achieved(outcome)
    """
    # Create span event using semantic conventions
    event_attrs: dict[str, Any] = {
        JTBDAttributes.OUTCOME_ID: outcome.outcome_id,
        JTBDAttributes.OUTCOME_METRIC: outcome.metric,
        JTBDAttributes.OUTCOME_EXPECTED: outcome.expected_value,
        JTBDAttributes.OUTCOME_ACTUAL: outcome.actual_value,
        JTBDAttributes.OUTCOME_ACHIEVEMENT_RATE: outcome.achievement_rate,
        JTBDAttributes.OUTCOME_FEATURE: outcome.feature,
        JTBDAttributes.OUTCOME_STATUS: outcome.status.value,
        JTBDAttributes.OUTCOME_EXCEEDS_EXPECTATIONS: outcome.exceeds_expectations,
    }

    if outcome.persona:
        event_attrs[JTBDAttributes.OUTCOME_PERSONA] = outcome.persona

    # Add context
    event_attrs.update({f"jtbd.outcome.context.{k}": str(v) for k, v in outcome.context.items()})

    add_span_event(JTBDOperations.OUTCOME_ACHIEVE, event_attrs)

    # Add attributes to current span
    current_span = get_current_span()
    if current_span.is_recording():
        for key, value in event_attrs.items():
            current_span.set_attribute(key, value)

    # Update metrics via collector
    collector = get_jtbd_metrics_collector()
    collector.record_outcome_achievement(
        outcome.outcome_id, outcome.achievement_rate, outcome.exceeds_expectations
    )


def track_painpoint_resolved(painpoint: PainpointResolved) -> None:
    """
    Track painpoint resolution with OpenTelemetry.

    Parameters
    ----------
    painpoint : PainpointResolved
        Painpoint resolution data to track.

    Example
    -------
    >>> painpoint = PainpointResolved(
    ...     painpoint_id="manual-dependency-updates",
    ...     category=PainpointCategory.MANUAL_EFFORT,
    ...     description="Manually updating pyproject.toml",
    ...     feature="specify deps add",
    ...     persona="python-developer",
    ...     severity_before=8,
    ...     severity_after=2
    ... )
    >>> track_painpoint_resolved(painpoint)
    """
    # Create span event using semantic conventions
    event_attrs: dict[str, Any] = {
        JTBDAttributes.PAINPOINT_ID: painpoint.painpoint_id,
        JTBDAttributes.PAINPOINT_CATEGORY: painpoint.category.value,
        JTBDAttributes.PAINPOINT_DESCRIPTION: painpoint.description,
        JTBDAttributes.PAINPOINT_FEATURE: painpoint.feature,
        JTBDAttributes.PAINPOINT_PERSONA: painpoint.persona,
        JTBDAttributes.PAINPOINT_SEVERITY_BEFORE: painpoint.severity_before,
        JTBDAttributes.PAINPOINT_SEVERITY_AFTER: painpoint.severity_after,
    }

    if painpoint.resolution_effectiveness is not None:
        event_attrs[JTBDAttributes.PAINPOINT_RESOLUTION_EFFECTIVENESS] = (
            painpoint.resolution_effectiveness
        )

    # Add context
    event_attrs.update(
        {f"jtbd.painpoint.context.{k}": str(v) for k, v in painpoint.context.items()}
    )

    add_span_event(JTBDOperations.PAINPOINT_RESOLVE, event_attrs)

    # Add attributes to current span
    current_span = get_current_span()
    if current_span.is_recording():
        for key, value in event_attrs.items():
            current_span.set_attribute(key, value)

    # Update metrics via collector
    collector = get_jtbd_metrics_collector()
    collector.record_painpoint_resolution(
        painpoint.painpoint_id, painpoint.resolution_effectiveness
    )


def track_time_to_outcome(time_to_outcome: TimeToOutcome) -> None:
    """
    Track time-to-outcome measurement with OpenTelemetry.

    Parameters
    ----------
    time_to_outcome : TimeToOutcome
        Time-to-outcome data to track.

    Example
    -------
    >>> tto = TimeToOutcome(
    ...     outcome_id="dependency-added",
    ...     persona="python-developer",
    ...     feature="specify deps add"
    ... )
    >>> tto.add_step("parse_args")
    >>> tto.add_step("validate_package")
    >>> tto.complete()
    >>> track_time_to_outcome(tto)
    """
    if time_to_outcome.duration_seconds is None:
        return

    # Create span event using semantic conventions
    event_attrs: dict[str, Any] = {
        JTBDAttributes.TTO_OUTCOME_ID: time_to_outcome.outcome_id,
        JTBDAttributes.TTO_PERSONA: time_to_outcome.persona,
        JTBDAttributes.TTO_FEATURE: time_to_outcome.feature,
        JTBDAttributes.TTO_DURATION_SECONDS: time_to_outcome.duration_seconds,
        JTBDAttributes.TTO_STEPS_COUNT: len(time_to_outcome.steps),
    }

    # Add steps
    for i, step in enumerate(time_to_outcome.steps, 1):
        event_attrs[f"jtbd.tto.step_{i}"] = step

    # Add context
    event_attrs.update(
        {f"jtbd.tto.context.{k}": str(v) for k, v in time_to_outcome.context.items()}
    )

    add_span_event(JTBDOperations.TTO_COMPLETE, event_attrs)

    # Add attributes to current span
    current_span = get_current_span()
    if current_span.is_recording():
        for key, value in event_attrs.items():
            current_span.set_attribute(key, value)

    # Update metrics via collector
    collector = get_jtbd_metrics_collector()
    collector.record_time_to_outcome(
        time_to_outcome.outcome_id,
        time_to_outcome.duration_seconds,
        len(time_to_outcome.steps),
    )


def track_user_satisfaction(satisfaction: UserSatisfaction) -> None:
    """
    Track user satisfaction with OpenTelemetry.

    Parameters
    ----------
    satisfaction : UserSatisfaction
        User satisfaction data to track.

    Example
    -------
    >>> satisfaction = UserSatisfaction(
    ...     outcome_id="faster-dependency-management",
    ...     feature="specify deps add",
    ...     persona="python-developer",
    ...     satisfaction_level=SatisfactionLevel.VERY_SATISFIED,
    ...     met_expectations=True,
    ...     would_recommend=True,
    ...     effort_score=2
    ... )
    >>> track_user_satisfaction(satisfaction)
    """
    # Create span event using semantic conventions
    event_attrs: dict[str, Any] = {
        JTBDAttributes.SATISFACTION_OUTCOME_ID: satisfaction.outcome_id,
        JTBDAttributes.SATISFACTION_FEATURE: satisfaction.feature,
        JTBDAttributes.SATISFACTION_PERSONA: satisfaction.persona,
        JTBDAttributes.SATISFACTION_LEVEL: satisfaction.satisfaction_level.value,
        JTBDAttributes.SATISFACTION_MET_EXPECTATIONS: satisfaction.met_expectations,
        JTBDAttributes.SATISFACTION_WOULD_RECOMMEND: satisfaction.would_recommend,
    }

    if satisfaction.effort_score is not None:
        event_attrs[JTBDAttributes.SATISFACTION_EFFORT_SCORE] = satisfaction.effort_score

    if satisfaction.feedback_text:
        event_attrs[JTBDAttributes.SATISFACTION_FEEDBACK] = satisfaction.feedback_text

    # Add context
    event_attrs.update(
        {f"jtbd.satisfaction.context.{k}": str(v) for k, v in satisfaction.context.items()}
    )

    add_span_event(JTBDOperations.SATISFACTION_RECORD, event_attrs)

    # Add attributes to current span
    current_span = get_current_span()
    if current_span.is_recording():
        for key, value in event_attrs.items():
            current_span.set_attribute(key, value)

    # Map satisfaction level to numeric score (1-5 scale to 1-100)
    satisfaction_score_map = {
        SatisfactionLevel.VERY_DISSATISFIED: 20.0,
        SatisfactionLevel.DISSATISFIED: 40.0,
        SatisfactionLevel.NEUTRAL: 60.0,
        SatisfactionLevel.SATISFIED: 80.0,
        SatisfactionLevel.VERY_SATISFIED: 100.0,
    }
    satisfaction_score = satisfaction_score_map.get(satisfaction.satisfaction_level, 60.0)

    # Update metrics via collector
    collector = get_jtbd_metrics_collector()
    collector.record_satisfaction(
        satisfaction.outcome_id,
        satisfaction_score,
        satisfaction.effort_score,
        satisfaction.met_expectations,
        satisfaction.would_recommend,
    )
