"""
specify_cli.ops.jtbd - Jobs-to-be-Done Operations
==================================================

Business logic for JTBD metrics analysis and reporting.

This module contains pure business logic for analyzing Jobs-to-be-Done
outcomes, tracking job completion, and generating JTBD insights.

Key Features
-----------
* **Job Validation**: Validate job tracking inputs
* **Metrics Calculation**: Calculate aggregate outcome metrics
* **Job-Feature Mapping**: Map jobs to features used
* **Report Generation**: Generate comprehensive JTBD reports
* **Satisfaction Analysis**: Calculate user satisfaction scores
* **Painpoint Patterns**: Identify common painpoint patterns

Design Principles
----------------
* Pure functions (same input → same output)
* No direct I/O (delegates to runtime layer)
* Fully testable with mocked data
* Returns structured results for commands to format

Examples
--------
    >>> from specify_cli.ops.jtbd import validate_job_completion
    >>>
    >>> result = validate_job_completion(
    ...     job_id="deps-add",
    ...     persona="python-developer",
    ...     feature="specify deps add",
    ...     context={"package": "httpx"}
    ... )
    >>> assert result.valid is True

See Also
--------
- :mod:`specify_cli.core.jtbd_metrics` : Core JTBD dataclasses
- :mod:`specify_cli.commands.jtbd` : CLI command handlers
"""

from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from statistics import mean, median
from typing import Any

from specify_cli.core.instrumentation import add_span_attributes, add_span_event
from specify_cli.core.jtbd_metrics import (
    OutcomeAchieved,
    PainpointCategory,
    PainpointResolved,
    SatisfactionLevel,
    UserSatisfaction,
)
from specify_cli.core.telemetry import metric_counter, metric_histogram, span

__all__ = [
    "DashboardMetrics",
    "JTBDReport",
    "JobFeatureMapping",
    "JobValidationResult",
    "OutcomeMetrics",
    "PainpointAnalysis",
    "PainpointPattern",
    "SatisfactionScores",
    "TrackJobResult",
    "TrackOutcomeResult",
    "analyze_job_feature_mapping",
    "calculate_outcome_metrics",
    "calculate_satisfaction_scores",
    "create_job_completion",
    "create_outcome_achievement",
    "generate_dashboard_metrics",
    "generate_jtbd_report",
    "identify_painpoint_patterns",
    "validate_job_completion",
]


# =============================================================================
# Result Data Classes
# =============================================================================


@dataclass
class TrackJobResult:
    """Result of tracking a job completion."""

    success: bool
    job_id: str
    message: str
    job_data: dict[str, Any] = field(default_factory=dict)


@dataclass
class TrackOutcomeResult:
    """Result of tracking an outcome achievement."""

    success: bool
    outcome_id: str
    message: str
    achievement_rate: float = 0.0
    outcome_data: dict[str, Any] = field(default_factory=dict)


@dataclass
class JobValidationResult:
    """Result of job completion validation."""

    valid: bool
    job_id: str
    persona: str
    feature: str
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class OutcomeMetrics:
    """Aggregate outcome metrics calculation."""

    total_outcomes: int
    achieved_count: int
    partially_achieved_count: int
    not_achieved_count: int
    avg_achievement_rate: float
    median_achievement_rate: float
    exceeds_expectations_count: int
    exceeds_expectations_rate: float
    outcomes_by_feature: dict[str, int]
    outcomes_by_persona: dict[str, int]
    achievement_rates_by_feature: dict[str, float] = field(default_factory=dict)


@dataclass
class JobFeatureMapping:
    """Mapping of jobs to features used."""

    job_id: str
    features_used: list[str]
    usage_count: int
    personas: list[str]
    success_rate: float  # Percentage of successful completions
    avg_duration_seconds: float | None = None
    most_common_feature: str | None = None


@dataclass
class JTBDReport:
    """Comprehensive JTBD metrics report."""

    start_date: datetime
    end_date: datetime
    persona: str | None
    total_jobs: int
    completed_jobs: int
    failed_jobs: int
    completion_rate: float
    outcome_metrics: OutcomeMetrics | None = None
    job_feature_mappings: list[JobFeatureMapping] = field(default_factory=list)
    satisfaction_scores: dict[str, Any] = field(default_factory=dict)
    painpoint_patterns: list[dict[str, Any]] = field(default_factory=list)
    top_performing_features: list[tuple[str, float]] = field(default_factory=list)
    underperforming_features: list[tuple[str, float]] = field(default_factory=list)
    generated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class SatisfactionScores:
    """User satisfaction score calculations."""

    total_responses: int
    avg_effort_score: float | None  # 1-7 scale (lower is better)
    met_expectations_rate: float  # Percentage
    would_recommend_rate: float  # Percentage (NPS)
    satisfaction_distribution: dict[str, int]  # Count by satisfaction level
    nps_score: float | None  # Net Promoter Score (-100 to 100)
    promoters_count: int = 0  # Very satisfied
    passives_count: int = 0  # Satisfied
    detractors_count: int = 0  # Neutral, dissatisfied, very dissatisfied


@dataclass
class PainpointPattern:
    """Identified painpoint pattern."""

    category: PainpointCategory
    occurrence_count: int
    avg_severity_before: float
    avg_severity_after: float
    avg_effectiveness: float
    features_addressing: list[str]
    personas_affected: list[str]
    most_common_description: str | None = None


@dataclass
class PainpointAnalysis:
    """Complete painpoint analysis."""

    total_painpoints: int
    patterns: list[PainpointPattern]
    most_common_category: PainpointCategory | None
    avg_resolution_effectiveness: float
    top_performing_features: list[tuple[str, float]] = field(default_factory=list)


@dataclass
class DashboardMetrics:
    """Real-time dashboard metrics aggregation."""

    # Job metrics
    total_jobs: int
    completed_jobs: int
    failed_jobs: int
    completion_rate: float

    # Outcome metrics (optional)
    outcomes_summary: dict[str, Any] | None = None

    # Satisfaction metrics (optional)
    satisfaction_summary: dict[str, Any] | None = None

    # Feature performance
    top_features: list[tuple[str, float]] = field(default_factory=list)

    # Painpoint summary
    painpoint_summary: list[dict[str, Any]] = field(default_factory=list)

    # Metadata
    start_date: datetime = field(default_factory=lambda: datetime.now(UTC))
    end_date: datetime = field(default_factory=lambda: datetime.now(UTC))
    persona: str | None = None
    generated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


# =============================================================================
# Validation Operations
# =============================================================================


def validate_job_completion(
    job_id: str,
    persona: str,
    feature: str,
    context: dict[str, Any] | None = None,
) -> JobValidationResult:
    """Validate job completion tracking inputs.

    Pure validation logic that checks required fields and data quality
    without performing any I/O operations.

    Parameters
    ----------
    job_id : str
        Unique identifier for the job type.
    persona : str
        User persona completing the job.
    feature : str
        Feature/command used to complete the job.
    context : dict[str, Any], optional
        Additional context about the job execution.

    Returns
    -------
    JobValidationResult
        Validation result with errors and warnings.

    Examples
    --------
    >>> result = validate_job_completion(
    ...     job_id="deps-add",
    ...     persona="python-developer",
    ...     feature="specify deps add",
    ...     context={"package": "httpx"}
    ... )
    >>> assert result.valid is True
    """
    with span("ops.jtbd.validate_job", job_id=job_id, persona=persona):
        errors: list[str] = []
        warnings: list[str] = []

        # Validate required fields
        if not job_id or not job_id.strip():
            errors.append("job_id is required and cannot be empty")
        elif len(job_id) < 3:
            errors.append("job_id must be at least 3 characters")
        elif len(job_id) > 100:
            errors.append("job_id must be at most 100 characters")

        if not persona or not persona.strip():
            errors.append("persona is required and cannot be empty")
        elif len(persona) < 3:
            errors.append("persona must be at least 3 characters")

        if not feature or not feature.strip():
            errors.append("feature is required and cannot be empty")
        elif len(feature) < 3:
            errors.append("feature must be at least 3 characters")

        # Validate job_id format (should be kebab-case)
        if job_id and not errors:
            if not all(c.isalnum() or c in ("-", "_") for c in job_id):
                warnings.append("job_id should use kebab-case (e.g., 'deps-add')")

        # Validate context
        context_dict = context or {}
        if not isinstance(context_dict, dict):
            errors.append("context must be a dictionary")

        # Build metadata
        metadata = {
            "job_id_length": len(job_id),
            "persona_length": len(persona),
            "feature_length": len(feature),
            "context_keys": len(context_dict),
        }

        valid = len(errors) == 0

        add_span_attributes(
            validation_valid=valid,
            validation_errors=len(errors),
            validation_warnings=len(warnings),
        )

        if not valid:
            add_span_event("validation.failed", {"errors": errors})
        else:
            add_span_event("validation.passed", metadata)

        metric_counter("ops.jtbd.validations")(1)
        if not valid:
            metric_counter("ops.jtbd.validation_failures")(1)

        return JobValidationResult(
            valid=valid,
            job_id=job_id,
            persona=persona,
            feature=feature,
            errors=errors,
            warnings=warnings,
            metadata=metadata,
        )


def create_job_completion(
    job_id: str,
    persona: str,
    feature_used: str,
    status: str = "completed",
    context: dict[str, Any] | None = None,
) -> TrackJobResult:
    """
    Create and track a job completion event.

    Parameters
    ----------
    job_id : str
        Unique identifier for the job type.
    persona : str
        User persona completing the job.
    feature_used : str
        Feature/command used to complete the job.
    status : str, optional
        Job status ("started", "completed", "failed"). Default is "completed".
    context : dict[str, Any], optional
        Additional context about the job.

    Returns
    -------
    TrackJobResult
        Result of the tracking operation.
    """
    from specify_cli.core.jtbd_metrics import JobCompletion, JobStatus, track_job_completion
    from specify_cli.runtime import jtbd as jtbd_runtime

    start_time = time.time()

    with span("ops.jtbd.create_job", job_id=job_id, persona=persona):
        try:
            from dataclasses import asdict

            # Create JobCompletion instance
            job = JobCompletion(
                job_id=job_id,
                persona=persona,
                feature_used=feature_used,
                status=JobStatus(status),
                context=context or {},
            )

            # Auto-complete if status is "completed"
            if status == "completed":
                job.complete()

            # Track with OTEL
            track_job_completion(job)

            # Serialize to dict for storage
            job_data = asdict(job)

            # Save to disk
            jtbd_runtime.save_job_completion(job_data)

            # Record metrics
            duration = time.time() - start_time
            metric_counter("ops.jtbd.job_tracked")(1)
            metric_histogram("ops.jtbd.track_duration")(duration)

            add_span_event(
                "job_tracked",
                {
                    "job_id": job_id,
                    "persona": persona,
                    "status": status,
                },
            )

            return TrackJobResult(
                success=True,
                job_id=job_id,
                message=f"Job '{job_id}' tracked successfully",
                job_data=job_data,
            )

        except Exception as e:
            add_span_attributes(error=str(e))
            return TrackJobResult(
                success=False,
                job_id=job_id,
                message=f"Failed to track job: {e}",
            )


def create_outcome_achievement(
    outcome_id: str,
    metric: str,
    expected_value: float,
    actual_value: float,
    feature: str,
    persona: str | None = None,
    context: dict[str, Any] | None = None,
) -> TrackOutcomeResult:
    """
    Create and track an outcome achievement event.

    Parameters
    ----------
    outcome_id : str
        Unique identifier for the outcome type.
    metric : str
        Metric being measured.
    expected_value : float
        Expected/target value.
    actual_value : float
        Actual value achieved.
    feature : str
        Feature that delivered the outcome.
    persona : str, optional
        User persona achieving the outcome.
    context : dict[str, Any], optional
        Additional context.

    Returns
    -------
    TrackOutcomeResult
        Result of the tracking operation.
    """
    from specify_cli.core.jtbd_metrics import track_outcome_achieved
    from specify_cli.runtime import jtbd as jtbd_runtime

    start_time = time.time()

    with span("ops.jtbd.create_outcome", outcome_id=outcome_id):
        try:
            from dataclasses import asdict

            # Create OutcomeAchieved instance
            outcome = OutcomeAchieved(
                outcome_id=outcome_id,
                metric=metric,
                expected_value=expected_value,
                actual_value=actual_value,
                feature=feature,
                persona=persona,
                context=context or {},
            )

            # Determine status based on achievement rate
            outcome.status = outcome.determine_status()

            # Track with OTEL
            track_outcome_achieved(outcome)

            # Serialize to dict for storage
            outcome_data = asdict(outcome)

            # Save to disk
            jtbd_runtime.save_outcome_achievement(outcome_data)

            # Record metrics
            duration = time.time() - start_time
            metric_counter("ops.jtbd.outcome_tracked")(1)
            metric_histogram("ops.jtbd.track_duration")(duration)

            add_span_event(
                "outcome_tracked",
                {
                    "outcome_id": outcome_id,
                    "achievement_rate": outcome.achievement_rate,
                    "status": outcome.status.value,
                },
            )

            return TrackOutcomeResult(
                success=True,
                outcome_id=outcome_id,
                message=f"Outcome '{outcome_id}' tracked successfully",
                achievement_rate=outcome.achievement_rate,
                outcome_data=outcome_data,
            )

        except Exception as e:
            add_span_attributes(error=str(e))
            return TrackOutcomeResult(
                success=False,
                outcome_id=outcome_id,
                message=f"Failed to track outcome: {e}",
            )


# =============================================================================
# Metrics Calculation Operations
# =============================================================================


def calculate_outcome_metrics(outcomes: list[OutcomeAchieved]) -> OutcomeMetrics:
    """Calculate aggregate outcome metrics.

    Pure calculation of outcome statistics without any I/O operations.

    Parameters
    ----------
    outcomes : list[OutcomeAchieved]
        List of outcome achievement data.

    Returns
    -------
    OutcomeMetrics
        Aggregate outcome metrics.

    Examples
    --------
    >>> from specify_cli.core.jtbd_metrics import OutcomeAchieved
    >>> outcomes = [
    ...     OutcomeAchieved(
    ...         outcome_id="faster-deps",
    ...         metric="time_saved",
    ...         expected_value=30.0,
    ...         actual_value=8.5,
    ...         feature="specify deps add"
    ...     )
    ... ]
    >>> metrics = calculate_outcome_metrics(outcomes)
    >>> assert metrics.total_outcomes == 1
    """
    start_time = time.time()

    with span("ops.jtbd.calculate_metrics", outcomes_count=len(outcomes)):
        if not outcomes:
            return OutcomeMetrics(
                total_outcomes=0,
                achieved_count=0,
                partially_achieved_count=0,
                not_achieved_count=0,
                avg_achievement_rate=0.0,
                median_achievement_rate=0.0,
                exceeds_expectations_count=0,
                exceeds_expectations_rate=0.0,
                outcomes_by_feature={},
                outcomes_by_persona={},
            )

        # Count by status
        achieved = sum(1 for o in outcomes if o.achievement_rate >= 100)
        partially = sum(1 for o in outcomes if 75 <= o.achievement_rate < 100)
        not_achieved = sum(1 for o in outcomes if o.achievement_rate < 75)
        exceeds = sum(1 for o in outcomes if o.exceeds_expectations)

        # Calculate achievement rates
        achievement_rates = [o.achievement_rate for o in outcomes]
        avg_rate = mean(achievement_rates)
        median_rate = median(achievement_rates)

        # Group by feature
        by_feature: dict[str, int] = defaultdict(int)
        for outcome in outcomes:
            by_feature[outcome.feature] += 1

        # Group by persona
        by_persona: dict[str, int] = defaultdict(int)
        for outcome in outcomes:
            if outcome.persona:
                by_persona[outcome.persona] += 1

        # Calculate average achievement rate by feature
        feature_rates: dict[str, list[float]] = defaultdict(list)
        for outcome in outcomes:
            feature_rates[outcome.feature].append(outcome.achievement_rate)

        avg_by_feature = {feature: mean(rates) for feature, rates in feature_rates.items()}

        duration = time.time() - start_time

        metrics = OutcomeMetrics(
            total_outcomes=len(outcomes),
            achieved_count=achieved,
            partially_achieved_count=partially,
            not_achieved_count=not_achieved,
            avg_achievement_rate=avg_rate,
            median_achievement_rate=median_rate,
            exceeds_expectations_count=exceeds,
            exceeds_expectations_rate=(exceeds / len(outcomes)) * 100,
            outcomes_by_feature=dict(by_feature),
            outcomes_by_persona=dict(by_persona),
            achievement_rates_by_feature=avg_by_feature,
        )

        add_span_attributes(
            metrics_total=metrics.total_outcomes,
            metrics_achieved=metrics.achieved_count,
            metrics_avg_rate=metrics.avg_achievement_rate,
            calculation_duration=duration,
        )

        metric_counter("ops.jtbd.metrics_calculated")(1)
        metric_histogram("ops.jtbd.calculation_duration")(duration)

        return metrics


def analyze_job_feature_mapping(
    jobs: list[dict[str, Any]],
    features: list[str] | None = None,
) -> list[JobFeatureMapping]:
    """Map jobs to features used.

    Pure analysis of which features are used for each job type without
    any I/O operations.

    Parameters
    ----------
    jobs : list[dict[str, Any]]
        List of job completion dictionaries with keys:
        - job_id: str
        - feature_used: str
        - persona: str
        - status: str (completed, failed, etc.)
        - duration_seconds: float (optional)
    features : list[str], optional
        Filter to specific features.

    Returns
    -------
    list[JobFeatureMapping]
        List of job-feature mappings.

    Examples
    --------
    >>> jobs = [
    ...     {
    ...         "job_id": "deps-add",
    ...         "feature_used": "specify deps add",
    ...         "persona": "python-developer",
    ...         "status": "completed",
    ...         "duration_seconds": 8.5
    ...     }
    ... ]
    >>> mappings = analyze_job_feature_mapping(jobs)
    >>> assert len(mappings) > 0
    """
    start_time = time.time()

    with span("ops.jtbd.analyze_mapping", jobs_count=len(jobs)):
        if not jobs:
            return []

        # Group by job_id
        job_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for job in jobs:
            job_id = job.get("job_id", "")
            if job_id:
                job_groups[job_id].append(job)

        mappings: list[JobFeatureMapping] = []

        for job_id, job_list in job_groups.items():
            # Collect features
            features_list = [j.get("feature_used", "") for j in job_list if j.get("feature_used")]

            # Filter if requested
            if features:
                features_list = [f for f in features_list if f in features]

            if not features_list:
                continue

            # Collect personas
            personas_list = list({j.get("persona", "") for j in job_list if j.get("persona")})

            # Calculate success rate
            completed = sum(1 for j in job_list if j.get("status") == "completed")
            success_rate = (completed / len(job_list)) * 100 if job_list else 0.0

            # Calculate average duration
            durations = [
                j["duration_seconds"]
                for j in job_list
                if "duration_seconds" in j and j["duration_seconds"] is not None
            ]
            avg_duration = mean(durations) if durations else None

            # Find most common feature
            feature_counts: dict[str, int] = defaultdict(int)
            for feature in features_list:
                feature_counts[feature] += 1

            most_common = (
                max(feature_counts.items(), key=lambda x: x[1])[0] if feature_counts else None
            )

            mapping = JobFeatureMapping(
                job_id=job_id,
                features_used=list(set(features_list)),
                usage_count=len(job_list),
                personas=personas_list,
                success_rate=success_rate,
                avg_duration_seconds=avg_duration,
                most_common_feature=most_common,
            )
            mappings.append(mapping)

        duration = time.time() - start_time

        add_span_attributes(
            mappings_count=len(mappings),
            unique_jobs=len(job_groups),
            analysis_duration=duration,
        )

        metric_counter("ops.jtbd.mappings_analyzed")(1)
        metric_histogram("ops.jtbd.mapping_duration")(duration)

        return mappings


# =============================================================================
# Report Generation Operations
# =============================================================================


def generate_jtbd_report(
    start_date: datetime,
    end_date: datetime,
    persona: str | None = None,
    jobs: list[dict[str, Any]] | None = None,
    outcomes: list[OutcomeAchieved] | None = None,
    satisfaction_data: list[UserSatisfaction] | None = None,
    painpoints: list[PainpointResolved] | None = None,
) -> JTBDReport:
    """Generate comprehensive JTBD metrics report.

    Pure report generation logic that aggregates all JTBD metrics
    without performing any I/O operations.

    Parameters
    ----------
    start_date : datetime
        Report start date.
    end_date : datetime
        Report end date.
    persona : str, optional
        Filter to specific persona.
    jobs : list[dict[str, Any]], optional
        Job completion data.
    outcomes : list[OutcomeAchieved], optional
        Outcome achievement data.
    satisfaction_data : list[UserSatisfaction], optional
        User satisfaction data.
    painpoints : list[PainpointResolved], optional
        Painpoint resolution data.

    Returns
    -------
    JTBDReport
        Comprehensive JTBD report.

    Examples
    --------
    >>> from datetime import datetime, UTC
    >>> report = generate_jtbd_report(
    ...     start_date=datetime(2025, 1, 1, tzinfo=UTC),
    ...     end_date=datetime(2025, 1, 31, tzinfo=UTC),
    ...     persona="python-developer"
    ... )
    >>> assert report.persona == "python-developer"
    """
    start_time = time.time()

    with span("ops.jtbd.generate_report", persona=persona or "all"):
        jobs_list = jobs or []
        outcomes_list = outcomes or []
        satisfaction_list = satisfaction_data or []
        painpoints_list = painpoints or []

        # Filter by persona if specified
        if persona:
            jobs_list = [j for j in jobs_list if j.get("persona") == persona]
            outcomes_list = [o for o in outcomes_list if o.persona == persona]
            satisfaction_list = [s for s in satisfaction_list if s.persona == persona]
            painpoints_list = [p for p in painpoints_list if p.persona == persona]

        # Calculate job statistics
        total_jobs = len(jobs_list)
        completed = sum(1 for j in jobs_list if j.get("status") == "completed")
        failed = sum(1 for j in jobs_list if j.get("status") == "failed")
        completion_rate = (completed / total_jobs * 100) if total_jobs > 0 else 0.0

        # Calculate outcome metrics
        outcome_metrics_obj = None
        if outcomes_list:
            outcome_metrics_obj = calculate_outcome_metrics(outcomes_list)

        # Calculate job-feature mappings
        mappings = analyze_job_feature_mapping(jobs_list) if jobs_list else []

        # Calculate satisfaction scores
        satisfaction_scores_dict: dict[str, Any] = {}
        if satisfaction_list:
            satisfaction_scores_obj = calculate_satisfaction_scores(satisfaction_list)
            satisfaction_scores_dict = {
                "total_responses": satisfaction_scores_obj.total_responses,
                "avg_effort_score": satisfaction_scores_obj.avg_effort_score,
                "met_expectations_rate": satisfaction_scores_obj.met_expectations_rate,
                "would_recommend_rate": satisfaction_scores_obj.would_recommend_rate,
                "nps_score": satisfaction_scores_obj.nps_score,
                "distribution": satisfaction_scores_obj.satisfaction_distribution,
            }

        # Identify painpoint patterns
        painpoint_patterns_list: list[dict[str, Any]] = []
        if painpoints_list:
            analysis = identify_painpoint_patterns(painpoints_list)
            painpoint_patterns_list = [
                {
                    "category": p.category.value,
                    "count": p.occurrence_count,
                    "avg_effectiveness": p.avg_effectiveness,
                    "features": p.features_addressing,
                }
                for p in analysis.patterns
            ]

        # Identify top/underperforming features
        top_features: list[tuple[str, float]] = []
        under_features: list[tuple[str, float]] = []

        if outcome_metrics_obj and outcome_metrics_obj.achievement_rates_by_feature:
            sorted_features = sorted(
                outcome_metrics_obj.achievement_rates_by_feature.items(),
                key=lambda x: x[1],
                reverse=True,
            )
            top_features = sorted_features[:5]  # Top 5
            under_features = sorted_features[-5:]  # Bottom 5

        duration = time.time() - start_time

        report = JTBDReport(
            start_date=start_date,
            end_date=end_date,
            persona=persona,
            total_jobs=total_jobs,
            completed_jobs=completed,
            failed_jobs=failed,
            completion_rate=completion_rate,
            outcome_metrics=outcome_metrics_obj,
            job_feature_mappings=mappings,
            satisfaction_scores=satisfaction_scores_dict,
            painpoint_patterns=painpoint_patterns_list,
            top_performing_features=top_features,
            underperforming_features=under_features,
        )

        add_span_attributes(
            report_jobs=total_jobs,
            report_completed=completed,
            report_completion_rate=completion_rate,
            report_duration=duration,
        )

        metric_counter("ops.jtbd.reports_generated")(1)
        metric_histogram("ops.jtbd.report_duration")(duration)

        return report


# =============================================================================
# Satisfaction Analysis Operations
# =============================================================================


def calculate_satisfaction_scores(
    feedback_data: list[UserSatisfaction],
) -> SatisfactionScores:
    """Calculate user satisfaction scores.

    Pure calculation of satisfaction metrics including NPS (Net Promoter Score)
    without any I/O operations.

    Parameters
    ----------
    feedback_data : list[UserSatisfaction]
        List of user satisfaction data.

    Returns
    -------
    SatisfactionScores
        Calculated satisfaction scores.

    Examples
    --------
    >>> from specify_cli.core.jtbd_metrics import UserSatisfaction, SatisfactionLevel
    >>> feedback = [
    ...     UserSatisfaction(
    ...         outcome_id="faster-deps",
    ...         feature="specify deps add",
    ...         persona="python-developer",
    ...         satisfaction_level=SatisfactionLevel.VERY_SATISFIED,
    ...         met_expectations=True,
    ...         would_recommend=True,
    ...         effort_score=2
    ...     )
    ... ]
    >>> scores = calculate_satisfaction_scores(feedback)
    >>> assert scores.total_responses == 1
    """
    start_time = time.time()

    with span("ops.jtbd.calculate_satisfaction", responses=len(feedback_data)):
        if not feedback_data:
            return SatisfactionScores(
                total_responses=0,
                avg_effort_score=None,
                met_expectations_rate=0.0,
                would_recommend_rate=0.0,
                satisfaction_distribution={},
                nps_score=None,
            )

        # Calculate effort scores
        effort_scores = [f.effort_score for f in feedback_data if f.effort_score is not None]
        avg_effort = mean(effort_scores) if effort_scores else None

        # Calculate met expectations rate
        met_expectations = sum(1 for f in feedback_data if f.met_expectations)
        met_rate = (met_expectations / len(feedback_data)) * 100

        # Calculate would recommend rate
        would_recommend = sum(1 for f in feedback_data if f.would_recommend)
        recommend_rate = (would_recommend / len(feedback_data)) * 100

        # Count by satisfaction level
        distribution: dict[str, int] = defaultdict(int)
        for feedback in feedback_data:
            distribution[feedback.satisfaction_level.value] += 1

        # Calculate NPS (Net Promoter Score)
        # Promoters: Very Satisfied (9-10)
        # Passives: Satisfied (7-8)
        # Detractors: Neutral, Dissatisfied, Very Dissatisfied (0-6)
        promoters = distribution.get(SatisfactionLevel.VERY_SATISFIED.value, 0)
        passives = distribution.get(SatisfactionLevel.SATISFIED.value, 0)
        detractors = (
            distribution.get(SatisfactionLevel.NEUTRAL.value, 0)
            + distribution.get(SatisfactionLevel.DISSATISFIED.value, 0)
            + distribution.get(SatisfactionLevel.VERY_DISSATISFIED.value, 0)
        )

        total = len(feedback_data)
        nps = ((promoters - detractors) / total * 100) if total > 0 else None

        duration = time.time() - start_time

        scores = SatisfactionScores(
            total_responses=len(feedback_data),
            avg_effort_score=avg_effort,
            met_expectations_rate=met_rate,
            would_recommend_rate=recommend_rate,
            satisfaction_distribution=dict(distribution),
            nps_score=nps,
            promoters_count=promoters,
            passives_count=passives,
            detractors_count=detractors,
        )

        add_span_attributes(
            satisfaction_responses=scores.total_responses,
            satisfaction_nps=nps or 0.0,
            satisfaction_met_rate=met_rate,
            calculation_duration=duration,
        )

        metric_counter("ops.jtbd.satisfaction_calculated")(1)
        metric_histogram("ops.jtbd.satisfaction_duration")(duration)

        return scores


# =============================================================================
# Painpoint Analysis Operations
# =============================================================================


def identify_painpoint_patterns(
    painpoints: list[PainpointResolved],
) -> PainpointAnalysis:
    """Identify common painpoint patterns.

    Pure analysis of painpoint data to identify patterns and trends
    without any I/O operations.

    Parameters
    ----------
    painpoints : list[PainpointResolved]
        List of painpoint resolution data.

    Returns
    -------
    PainpointAnalysis
        Identified painpoint patterns and analysis.

    Examples
    --------
    >>> from specify_cli.core.jtbd_metrics import PainpointResolved, PainpointCategory
    >>> painpoints = [
    ...     PainpointResolved(
    ...         painpoint_id="manual-deps",
    ...         category=PainpointCategory.MANUAL_EFFORT,
    ...         description="Manual dependency updates",
    ...         feature="specify deps add",
    ...         persona="python-developer",
    ...         severity_before=8,
    ...         severity_after=2
    ...     )
    ... ]
    >>> analysis = identify_painpoint_patterns(painpoints)
    >>> assert analysis.total_painpoints == 1
    """
    start_time = time.time()

    with span("ops.jtbd.identify_patterns", painpoints_count=len(painpoints)):
        if not painpoints:
            return PainpointAnalysis(
                total_painpoints=0,
                patterns=[],
                most_common_category=None,
                avg_resolution_effectiveness=0.0,
            )

        # Group by category
        by_category: dict[PainpointCategory, list[PainpointResolved]] = defaultdict(list)
        for painpoint in painpoints:
            by_category[painpoint.category].append(painpoint)

        # Build patterns
        patterns: list[PainpointPattern] = []

        for category, painpoint_list in by_category.items():
            # Calculate averages
            avg_before = mean([p.severity_before for p in painpoint_list])
            avg_after = mean([p.severity_after for p in painpoint_list])

            effectiveness_values = [
                p.resolution_effectiveness
                for p in painpoint_list
                if p.resolution_effectiveness is not None
            ]
            avg_effectiveness = mean(effectiveness_values) if effectiveness_values else 0.0

            # Collect features
            features = list({p.feature for p in painpoint_list})

            # Collect personas
            personas = list({p.persona for p in painpoint_list})

            # Find most common description
            descriptions = [p.description for p in painpoint_list]
            description_counts: dict[str, int] = defaultdict(int)
            for desc in descriptions:
                description_counts[desc] += 1

            most_common_desc = (
                max(description_counts.items(), key=lambda x: x[1])[0]
                if description_counts
                else None
            )

            pattern = PainpointPattern(
                category=category,
                occurrence_count=len(painpoint_list),
                avg_severity_before=avg_before,
                avg_severity_after=avg_after,
                avg_effectiveness=avg_effectiveness,
                features_addressing=features,
                personas_affected=personas,
                most_common_description=most_common_desc,
            )
            patterns.append(pattern)

        # Sort patterns by occurrence count
        patterns.sort(key=lambda p: p.occurrence_count, reverse=True)

        # Find most common category
        most_common_cat = patterns[0].category if patterns else None

        # Calculate overall effectiveness
        all_effectiveness = [
            p.resolution_effectiveness for p in painpoints if p.resolution_effectiveness is not None
        ]
        overall_effectiveness = mean(all_effectiveness) if all_effectiveness else 0.0

        # Find top performing features
        feature_effectiveness: dict[str, list[float]] = defaultdict(list)
        for painpoint in painpoints:
            if painpoint.resolution_effectiveness is not None:
                feature_effectiveness[painpoint.feature].append(painpoint.resolution_effectiveness)

        feature_avg = {feature: mean(scores) for feature, scores in feature_effectiveness.items()}
        top_features = sorted(feature_avg.items(), key=lambda x: x[1], reverse=True)[:5]

        duration = time.time() - start_time

        analysis = PainpointAnalysis(
            total_painpoints=len(painpoints),
            patterns=patterns,
            most_common_category=most_common_cat,
            avg_resolution_effectiveness=overall_effectiveness,
            top_performing_features=top_features,
        )

        add_span_attributes(
            patterns_identified=len(patterns),
            total_painpoints=len(painpoints),
            avg_effectiveness=overall_effectiveness,
            analysis_duration=duration,
        )

        metric_counter("ops.jtbd.patterns_identified")(1)
        metric_histogram("ops.jtbd.pattern_duration")(duration)

        return analysis


# =============================================================================
# Dashboard Metrics Operations
# =============================================================================


def generate_dashboard_metrics(
    start_date: datetime,
    end_date: datetime,
    persona: str | None = None,
    jobs: list[dict[str, Any]] | None = None,
    outcomes: list[OutcomeAchieved] | None = None,
    satisfaction_data: list[UserSatisfaction] | None = None,
    painpoints: list[PainpointResolved] | None = None,
) -> DashboardMetrics:
    """Generate real-time dashboard metrics.

    Pure aggregation of JTBD metrics for dashboard display
    without performing any I/O operations.

    Parameters
    ----------
    start_date : datetime
        Dashboard start date.
    end_date : datetime
        Dashboard end date.
    persona : str, optional
        Filter to specific persona.
    jobs : list[dict[str, Any]], optional
        Job completion data.
    outcomes : list[OutcomeAchieved], optional
        Outcome achievement data.
    satisfaction_data : list[UserSatisfaction], optional
        User satisfaction data.
    painpoints : list[PainpointResolved], optional
        Painpoint resolution data.

    Returns
    -------
    DashboardMetrics
        Aggregated dashboard metrics.

    Examples
    --------
    >>> from datetime import datetime, UTC
    >>> dashboard = generate_dashboard_metrics(
    ...     start_date=datetime(2025, 1, 1, tzinfo=UTC),
    ...     end_date=datetime(2025, 1, 31, tzinfo=UTC),
    ...     persona="python-developer"
    ... )
    >>> assert dashboard.persona == "python-developer"
    """
    start_time = time.time()

    with span("ops.jtbd.generate_dashboard", persona=persona or "all"):
        jobs_list = jobs or []
        outcomes_list = outcomes or []
        satisfaction_list = satisfaction_data or []
        painpoints_list = painpoints or []

        # Filter by persona if specified
        if persona:
            jobs_list = [j for j in jobs_list if j.get("persona") == persona]
            outcomes_list = [o for o in outcomes_list if o.persona == persona]
            satisfaction_list = [s for s in satisfaction_list if s.persona == persona]
            painpoints_list = [p for p in painpoints_list if p.persona == persona]

        # Calculate job statistics
        total_jobs = len(jobs_list)
        completed = sum(1 for j in jobs_list if j.get("status") == "completed")
        failed = sum(1 for j in jobs_list if j.get("status") == "failed")
        completion_rate = (completed / total_jobs * 100) if total_jobs > 0 else 0.0

        # Calculate outcome summary
        outcomes_summary_dict: dict[str, Any] | None = None
        if outcomes_list:
            outcome_metrics = calculate_outcome_metrics(outcomes_list)
            outcomes_summary_dict = {
                "total": outcome_metrics.total_outcomes,
                "achieved": outcome_metrics.achieved_count,
                "avg_achievement": outcome_metrics.avg_achievement_rate,
            }

        # Calculate satisfaction summary
        satisfaction_summary_dict: dict[str, Any] | None = None
        if satisfaction_list:
            satisfaction_scores = calculate_satisfaction_scores(satisfaction_list)
            satisfaction_summary_dict = {
                "responses": satisfaction_scores.total_responses,
                "nps_score": satisfaction_scores.nps_score,
                "met_expectations": satisfaction_scores.met_expectations_rate,
            }

        # Identify top features
        top_features_list: list[tuple[str, float]] = []
        if outcomes_list:
            outcome_metrics = calculate_outcome_metrics(outcomes_list)
            if outcome_metrics.achievement_rates_by_feature:
                sorted_features = sorted(
                    outcome_metrics.achievement_rates_by_feature.items(),
                    key=lambda x: x[1],
                    reverse=True,
                )
                top_features_list = sorted_features[:10]  # Top 10

        # Painpoint summary
        painpoint_summary_list: list[dict[str, Any]] = []
        if painpoints_list:
            analysis = identify_painpoint_patterns(painpoints_list)
            painpoint_summary_list = [
                {
                    "category": p.category.value,
                    "count": p.occurrence_count,
                    "effectiveness": p.avg_effectiveness,
                }
                for p in analysis.patterns
            ]

        duration = time.time() - start_time

        dashboard = DashboardMetrics(
            total_jobs=total_jobs,
            completed_jobs=completed,
            failed_jobs=failed,
            completion_rate=completion_rate,
            outcomes_summary=outcomes_summary_dict,
            satisfaction_summary=satisfaction_summary_dict,
            top_features=top_features_list,
            painpoint_summary=painpoint_summary_list,
            start_date=start_date,
            end_date=end_date,
            persona=persona,
        )

        add_span_attributes(
            dashboard_jobs=total_jobs,
            dashboard_completed=completed,
            dashboard_completion_rate=completion_rate,
            dashboard_duration=duration,
        )

        metric_counter("ops.jtbd.dashboards_generated")(1)
        metric_histogram("ops.jtbd.dashboard_duration")(duration)

        return dashboard
