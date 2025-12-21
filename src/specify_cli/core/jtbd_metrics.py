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
from .telemetry import (
    get_current_span,
    metric_counter,
    metric_histogram,
)

__all__ = [
    "JobCompletion",
    "JobStatus",
    "OutcomeAchieved",
    "OutcomeStatus",
    "PainpointCategory",
    "PainpointResolved",
    "SatisfactionLevel",
    "TimeToOutcome",
    "UserSatisfaction",
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
    # Create span event
    event_attrs: dict[str, Any] = {
        "jtbd.job.id": job.job_id,
        "jtbd.job.persona": job.persona,
        "jtbd.job.feature": job.feature_used,
        "jtbd.job.status": job.status.value,
    }

    if job.duration_seconds is not None:
        event_attrs["jtbd.job.duration_seconds"] = job.duration_seconds

    # Add context
    event_attrs.update({f"jtbd.job.context.{k}": str(v) for k, v in job.context.items()})

    add_span_event("job_completed", event_attrs)

    # Add attributes to current span
    current_span = get_current_span()
    if current_span.is_recording():
        for key, value in event_attrs.items():
            current_span.set_attribute(key, value)

    # Update metrics
    counter = metric_counter(f"jtbd.job.{job.job_id}.completions")
    counter(1)

    if job.duration_seconds is not None:
        histogram = metric_histogram(f"jtbd.job.{job.job_id}.duration", unit="s")
        histogram(job.duration_seconds)


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
    # Create span event
    event_attrs: dict[str, Any] = {
        "jtbd.outcome.id": outcome.outcome_id,
        "jtbd.outcome.metric": outcome.metric,
        "jtbd.outcome.expected": outcome.expected_value,
        "jtbd.outcome.actual": outcome.actual_value,
        "jtbd.outcome.achievement_rate": outcome.achievement_rate,
        "jtbd.outcome.feature": outcome.feature,
        "jtbd.outcome.status": outcome.status.value,
        "jtbd.outcome.exceeds_expectations": outcome.exceeds_expectations,
    }

    if outcome.persona:
        event_attrs["jtbd.outcome.persona"] = outcome.persona

    # Add context
    event_attrs.update({f"jtbd.outcome.context.{k}": str(v) for k, v in outcome.context.items()})

    add_span_event("outcome_achieved", event_attrs)

    # Add attributes to current span
    current_span = get_current_span()
    if current_span.is_recording():
        for key, value in event_attrs.items():
            current_span.set_attribute(key, value)

    # Update metrics
    counter = metric_counter(f"jtbd.outcome.{outcome.outcome_id}.achievements")
    counter(1)

    histogram = metric_histogram(f"jtbd.outcome.{outcome.outcome_id}.achievement_rate", unit="%")
    histogram(outcome.achievement_rate)


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
    # Create span event
    event_attrs: dict[str, Any] = {
        "jtbd.painpoint.id": painpoint.painpoint_id,
        "jtbd.painpoint.category": painpoint.category.value,
        "jtbd.painpoint.description": painpoint.description,
        "jtbd.painpoint.feature": painpoint.feature,
        "jtbd.painpoint.persona": painpoint.persona,
        "jtbd.painpoint.severity_before": painpoint.severity_before,
        "jtbd.painpoint.severity_after": painpoint.severity_after,
    }

    if painpoint.resolution_effectiveness is not None:
        event_attrs["jtbd.painpoint.resolution_effectiveness"] = painpoint.resolution_effectiveness

    # Add context
    event_attrs.update(
        {f"jtbd.painpoint.context.{k}": str(v) for k, v in painpoint.context.items()}
    )

    add_span_event("painpoint_resolved", event_attrs)

    # Add attributes to current span
    current_span = get_current_span()
    if current_span.is_recording():
        for key, value in event_attrs.items():
            current_span.set_attribute(key, value)

    # Update metrics
    counter = metric_counter("jtbd.painpoint.resolutions")
    counter(1)

    if painpoint.resolution_effectiveness is not None:
        histogram = metric_histogram("jtbd.painpoint.effectiveness", unit="%")
        histogram(painpoint.resolution_effectiveness)


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

    # Create span event
    event_attrs: dict[str, Any] = {
        "jtbd.tto.outcome_id": time_to_outcome.outcome_id,
        "jtbd.tto.persona": time_to_outcome.persona,
        "jtbd.tto.feature": time_to_outcome.feature,
        "jtbd.tto.duration_seconds": time_to_outcome.duration_seconds,
        "jtbd.tto.steps_count": len(time_to_outcome.steps),
    }

    # Add steps
    for i, step in enumerate(time_to_outcome.steps, 1):
        event_attrs[f"jtbd.tto.step_{i}"] = step

    # Add context
    event_attrs.update(
        {f"jtbd.tto.context.{k}": str(v) for k, v in time_to_outcome.context.items()}
    )

    add_span_event("time_to_outcome", event_attrs)

    # Add attributes to current span
    current_span = get_current_span()
    if current_span.is_recording():
        for key, value in event_attrs.items():
            current_span.set_attribute(key, value)

    # Update metrics
    histogram = metric_histogram(f"jtbd.tto.{time_to_outcome.outcome_id}.duration", unit="s")
    histogram(time_to_outcome.duration_seconds)


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
    # Create span event
    event_attrs: dict[str, Any] = {
        "jtbd.satisfaction.outcome_id": satisfaction.outcome_id,
        "jtbd.satisfaction.feature": satisfaction.feature,
        "jtbd.satisfaction.persona": satisfaction.persona,
        "jtbd.satisfaction.level": satisfaction.satisfaction_level.value,
        "jtbd.satisfaction.met_expectations": satisfaction.met_expectations,
        "jtbd.satisfaction.would_recommend": satisfaction.would_recommend,
    }

    if satisfaction.effort_score is not None:
        event_attrs["jtbd.satisfaction.effort_score"] = satisfaction.effort_score

    if satisfaction.feedback_text:
        event_attrs["jtbd.satisfaction.feedback"] = satisfaction.feedback_text

    # Add context
    event_attrs.update(
        {f"jtbd.satisfaction.context.{k}": str(v) for k, v in satisfaction.context.items()}
    )

    add_span_event("user_satisfaction", event_attrs)

    # Add attributes to current span
    current_span = get_current_span()
    if current_span.is_recording():
        for key, value in event_attrs.items():
            current_span.set_attribute(key, value)

    # Update metrics
    counter = metric_counter(f"jtbd.satisfaction.{satisfaction.outcome_id}.responses")
    counter(1)

    if satisfaction.effort_score is not None:
        histogram = metric_histogram("jtbd.satisfaction.effort_score")
        histogram(float(satisfaction.effort_score))
