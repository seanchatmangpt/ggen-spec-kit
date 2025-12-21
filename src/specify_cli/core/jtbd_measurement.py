"""
specify_cli.core.jtbd_measurement
----------------------------------
JTBD measurement, analysis, and reporting framework.

This module provides tools to collect, analyze, and visualize JTBD metrics
from OpenTelemetry traces. It enables outcome-driven product development
by tracking which features successfully deliver promised outcomes.

Core Functions
--------------
- extract_jtbd_metrics: Extract JTBD data from OTEL traces
- analyze_outcome_delivery: Analyze outcome delivery rates
- analyze_feature_effectiveness: Measure feature ROI
- generate_jtbd_report: Generate comprehensive JTBD reports
- export_metrics: Export metrics to CSV/JSON

Query Functions
---------------
- query_job_completions: Query job completion data
- query_outcome_achievements: Query outcome achievement data
- query_painpoint_resolutions: Query painpoint resolution data
- query_time_to_outcome: Query time-to-outcome data
- query_satisfaction_scores: Query user satisfaction data

Example
-------
    from specify_cli.core.jtbd_measurement import (
        extract_jtbd_metrics,
        analyze_outcome_delivery,
        export_metrics
    )

    # Extract metrics from OTEL traces
    metrics = extract_jtbd_metrics(trace_data)

    # Analyze outcome delivery rates
    analysis = analyze_outcome_delivery(metrics, persona="python-developer")

    # Export to CSV for analysis
    export_metrics(metrics, "jtbd_metrics.csv", format="csv")

Reference
---------
JTBD Metrics: https://jobs-to-be-done.com/
Product-Led Growth: https://www.productled.org/
"""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .jtbd_metrics import (
    JobStatus,
    OutcomeStatus,
    PainpointCategory,
    SatisfactionLevel,
)

__all__ = [
    "FeatureEffectiveness",
    "JTBDMetrics",
    "OutcomeDeliveryAnalysis",
    "analyze_feature_effectiveness",
    "analyze_outcome_delivery",
    "export_metrics",
    "extract_jtbd_metrics",
    "generate_jtbd_report",
    "query_job_completions",
    "query_outcome_achievements",
    "query_painpoint_resolutions",
    "query_satisfaction_scores",
    "query_time_to_outcome",
]


# =============================================================================
# Data Classes for Analysis
# =============================================================================


@dataclass
class JTBDMetrics:
    """
    Aggregated JTBD metrics from traces.

    Attributes
    ----------
    job_completions : list[dict[str, Any]]
        List of job completion records.
    outcome_achievements : list[dict[str, Any]]
        List of outcome achievement records.
    painpoint_resolutions : list[dict[str, Any]]
        List of painpoint resolution records.
    time_to_outcomes : list[dict[str, Any]]
        List of time-to-outcome records.
    satisfaction_scores : list[dict[str, Any]]
        List of user satisfaction records.
    extraction_timestamp : datetime
        When metrics were extracted.
    """

    job_completions: list[dict[str, Any]] = field(default_factory=list)
    outcome_achievements: list[dict[str, Any]] = field(default_factory=list)
    painpoint_resolutions: list[dict[str, Any]] = field(default_factory=list)
    time_to_outcomes: list[dict[str, Any]] = field(default_factory=list)
    satisfaction_scores: list[dict[str, Any]] = field(default_factory=list)
    extraction_timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class OutcomeDeliveryAnalysis:
    """
    Analysis of outcome delivery effectiveness.

    Attributes
    ----------
    outcome_id : str
        Identifier for the outcome.
    total_attempts : int
        Total attempts to achieve outcome.
    successful_deliveries : int
        Number of successful outcome deliveries.
    delivery_rate : float
        Percentage of successful deliveries.
    avg_achievement_rate : float
        Average achievement rate (% of expected outcome).
    avg_time_to_outcome : float
        Average time to achieve outcome (seconds).
    features_used : dict[str, int]
        Features used and their usage counts.
    personas : dict[str, int]
        Personas and their attempt counts.
    exceeds_expectations_count : int
        Number of times outcome exceeded expectations.
    """

    outcome_id: str
    total_attempts: int = 0
    successful_deliveries: int = 0
    delivery_rate: float = 0.0
    avg_achievement_rate: float = 0.0
    avg_time_to_outcome: float = 0.0
    features_used: dict[str, int] = field(default_factory=dict)
    personas: dict[str, int] = field(default_factory=dict)
    exceeds_expectations_count: int = 0

    def calculate_metrics(self) -> None:
        """Calculate derived metrics."""
        if self.total_attempts > 0:
            self.delivery_rate = (self.successful_deliveries / self.total_attempts) * 100.0


@dataclass
class FeatureEffectiveness:
    """
    Analysis of feature effectiveness and ROI.

    Attributes
    ----------
    feature : str
        Feature identifier.
    total_uses : int
        Total number of times feature was used.
    jobs_completed : int
        Jobs completed using this feature.
    outcomes_delivered : int
        Outcomes delivered by this feature.
    painpoints_resolved : int
        Painpoints resolved by this feature.
    avg_satisfaction : float
        Average satisfaction score (1-5 scale).
    avg_effort_score : float
        Average customer effort score (1-7 scale).
    recommendation_rate : float
        Percentage of users who would recommend.
    personas_served : list[str]
        List of personas using this feature.
    effectiveness_score : float
        Overall effectiveness score (0-100).
    """

    feature: str
    total_uses: int = 0
    jobs_completed: int = 0
    outcomes_delivered: int = 0
    painpoints_resolved: int = 0
    avg_satisfaction: float = 0.0
    avg_effort_score: float = 0.0
    recommendation_rate: float = 0.0
    personas_served: list[str] = field(default_factory=list)
    effectiveness_score: float = 0.0

    def calculate_effectiveness(self) -> None:
        """
        Calculate overall effectiveness score.

        Score based on:
        - Outcome delivery rate (40%)
        - User satisfaction (30%)
        - Painpoint resolution (20%)
        - Low effort score (10%)
        """
        if self.total_uses == 0:
            self.effectiveness_score = 0.0
            return

        # Normalize components to 0-100 scale
        outcome_score = (self.outcomes_delivered / self.total_uses) * 100.0
        satisfaction_score = (self.avg_satisfaction / 5.0) * 100.0
        painpoint_score = (self.painpoints_resolved / self.total_uses) * 100.0
        # Invert effort score (lower is better)
        effort_score = ((7.0 - self.avg_effort_score) / 6.0) * 100.0

        # Weighted average
        self.effectiveness_score = (
            outcome_score * 0.4
            + satisfaction_score * 0.3
            + painpoint_score * 0.2
            + effort_score * 0.1
        )


# =============================================================================
# Query Functions
# =============================================================================


def query_job_completions(
    trace_data: list[dict[str, Any]],
    persona: str | None = None,
    job_id: str | None = None,
    status: JobStatus | None = None,
) -> list[dict[str, Any]]:
    """
    Query job completion data from traces.

    Parameters
    ----------
    trace_data : list[dict[str, Any]]
        List of trace records (spans/events).
    persona : str, optional
        Filter by persona.
    job_id : str, optional
        Filter by job ID.
    status : JobStatus, optional
        Filter by job status.

    Returns
    -------
    list[dict[str, Any]]
        Filtered job completion records.
    """
    results = []

    for record in trace_data:
        if not _is_job_completion_event(record):
            continue

        attrs = record.get("attributes", {})

        # Apply filters
        if persona and attrs.get("jtbd.job.persona") != persona:
            continue
        if job_id and attrs.get("jtbd.job.id") != job_id:
            continue
        if status and attrs.get("jtbd.job.status") != status.value:
            continue

        results.append(attrs)

    return results


def query_outcome_achievements(
    trace_data: list[dict[str, Any]],
    outcome_id: str | None = None,
    feature: str | None = None,
    min_achievement_rate: float | None = None,
) -> list[dict[str, Any]]:
    """
    Query outcome achievement data from traces.

    Parameters
    ----------
    trace_data : list[dict[str, Any]]
        List of trace records.
    outcome_id : str, optional
        Filter by outcome ID.
    feature : str, optional
        Filter by feature.
    min_achievement_rate : float, optional
        Minimum achievement rate (0-100).

    Returns
    -------
    list[dict[str, Any]]
        Filtered outcome achievement records.
    """
    results = []

    for record in trace_data:
        if not _is_outcome_achievement_event(record):
            continue

        attrs = record.get("attributes", {})

        # Apply filters
        if outcome_id and attrs.get("jtbd.outcome.id") != outcome_id:
            continue
        if feature and attrs.get("jtbd.outcome.feature") != feature:
            continue
        if (
            min_achievement_rate is not None
            and attrs.get("jtbd.outcome.achievement_rate", 0) < min_achievement_rate
        ):
            continue

        results.append(attrs)

    return results


def query_painpoint_resolutions(
    trace_data: list[dict[str, Any]],
    category: PainpointCategory | None = None,
    feature: str | None = None,
    min_effectiveness: float | None = None,
) -> list[dict[str, Any]]:
    """
    Query painpoint resolution data from traces.

    Parameters
    ----------
    trace_data : list[dict[str, Any]]
        List of trace records.
    category : PainpointCategory, optional
        Filter by painpoint category.
    feature : str, optional
        Filter by feature.
    min_effectiveness : float, optional
        Minimum resolution effectiveness (0-100).

    Returns
    -------
    list[dict[str, Any]]
        Filtered painpoint resolution records.
    """
    results = []

    for record in trace_data:
        if not _is_painpoint_resolution_event(record):
            continue

        attrs = record.get("attributes", {})

        # Apply filters
        if category and attrs.get("jtbd.painpoint.category") != category.value:
            continue
        if feature and attrs.get("jtbd.painpoint.feature") != feature:
            continue
        if (
            min_effectiveness is not None
            and attrs.get("jtbd.painpoint.resolution_effectiveness", 0) < min_effectiveness
        ):
            continue

        results.append(attrs)

    return results


def query_time_to_outcome(
    trace_data: list[dict[str, Any]],
    outcome_id: str | None = None,
    persona: str | None = None,
    max_duration: float | None = None,
) -> list[dict[str, Any]]:
    """
    Query time-to-outcome data from traces.

    Parameters
    ----------
    trace_data : list[dict[str, Any]]
        List of trace records.
    outcome_id : str, optional
        Filter by outcome ID.
    persona : str, optional
        Filter by persona.
    max_duration : float, optional
        Maximum duration in seconds.

    Returns
    -------
    list[dict[str, Any]]
        Filtered time-to-outcome records.
    """
    results = []

    for record in trace_data:
        if not _is_time_to_outcome_event(record):
            continue

        attrs = record.get("attributes", {})

        # Apply filters
        if outcome_id and attrs.get("jtbd.tto.outcome_id") != outcome_id:
            continue
        if persona and attrs.get("jtbd.tto.persona") != persona:
            continue
        if (
            max_duration is not None
            and attrs.get("jtbd.tto.duration_seconds", float("inf")) > max_duration
        ):
            continue

        results.append(attrs)

    return results


def query_satisfaction_scores(
    trace_data: list[dict[str, Any]],
    outcome_id: str | None = None,
    feature: str | None = None,
    min_level: SatisfactionLevel | None = None,
) -> list[dict[str, Any]]:
    """
    Query user satisfaction data from traces.

    Parameters
    ----------
    trace_data : list[dict[str, Any]]
        List of trace records.
    outcome_id : str, optional
        Filter by outcome ID.
    feature : str, optional
        Filter by feature.
    min_level : SatisfactionLevel, optional
        Minimum satisfaction level.

    Returns
    -------
    list[dict[str, Any]]
        Filtered satisfaction records.
    """
    results = []

    satisfaction_order = {
        SatisfactionLevel.VERY_DISSATISFIED: 1,
        SatisfactionLevel.DISSATISFIED: 2,
        SatisfactionLevel.NEUTRAL: 3,
        SatisfactionLevel.SATISFIED: 4,
        SatisfactionLevel.VERY_SATISFIED: 5,
    }

    min_order = satisfaction_order.get(min_level, 0) if min_level else 0

    for record in trace_data:
        if not _is_satisfaction_event(record):
            continue

        attrs = record.get("attributes", {})

        # Apply filters
        if outcome_id and attrs.get("jtbd.satisfaction.outcome_id") != outcome_id:
            continue
        if feature and attrs.get("jtbd.satisfaction.feature") != feature:
            continue
        if min_level:
            level_str = attrs.get("jtbd.satisfaction.level", "")
            try:
                level = SatisfactionLevel(level_str)
                if satisfaction_order.get(level, 0) < min_order:
                    continue
            except ValueError:
                continue

        results.append(attrs)

    return results


# =============================================================================
# Analysis Functions
# =============================================================================


def extract_jtbd_metrics(trace_data: list[dict[str, Any]]) -> JTBDMetrics:
    """
    Extract JTBD metrics from OpenTelemetry trace data.

    Parameters
    ----------
    trace_data : list[dict[str, Any]]
        List of trace records (spans and events).

    Returns
    -------
    JTBDMetrics
        Aggregated JTBD metrics.

    Example
    -------
    >>> trace_data = load_trace_data()
    >>> metrics = extract_jtbd_metrics(trace_data)
    >>> print(f"Jobs completed: {len(metrics.job_completions)}")
    """
    metrics = JTBDMetrics()

    metrics.job_completions = query_job_completions(trace_data)
    metrics.outcome_achievements = query_outcome_achievements(trace_data)
    metrics.painpoint_resolutions = query_painpoint_resolutions(trace_data)
    metrics.time_to_outcomes = query_time_to_outcome(trace_data)
    metrics.satisfaction_scores = query_satisfaction_scores(trace_data)

    return metrics


def analyze_outcome_delivery(
    metrics: JTBDMetrics, outcome_id: str | None = None, persona: str | None = None
) -> dict[str, OutcomeDeliveryAnalysis]:
    """
    Analyze outcome delivery rates and effectiveness.

    Parameters
    ----------
    metrics : JTBDMetrics
        JTBD metrics to analyze.
    outcome_id : str, optional
        Filter by specific outcome.
    persona : str, optional
        Filter by specific persona.

    Returns
    -------
    dict[str, OutcomeDeliveryAnalysis]
        Analysis results keyed by outcome ID.

    Example
    -------
    >>> metrics = extract_jtbd_metrics(trace_data)
    >>> analysis = analyze_outcome_delivery(metrics, persona="python-developer")
    >>> for outcome_id, result in analysis.items():
    ...     print(f"{outcome_id}: {result.delivery_rate}% delivery rate")
    """
    analyses: dict[str, OutcomeDeliveryAnalysis] = {}

    for outcome in metrics.outcome_achievements:
        oid = outcome.get("jtbd.outcome.id", "unknown")

        # Apply filters
        if outcome_id and oid != outcome_id:
            continue
        if persona and outcome.get("jtbd.outcome.persona") != persona:
            continue

        if oid not in analyses:
            analyses[oid] = OutcomeDeliveryAnalysis(outcome_id=oid)

        analysis = analyses[oid]
        analysis.total_attempts += 1

        status = outcome.get("jtbd.outcome.status")
        if status == OutcomeStatus.ACHIEVED.value:
            analysis.successful_deliveries += 1

        achievement_rate = outcome.get("jtbd.outcome.achievement_rate", 0.0)
        analysis.avg_achievement_rate = (
            analysis.avg_achievement_rate * (analysis.total_attempts - 1) + achievement_rate
        ) / analysis.total_attempts

        feature = outcome.get("jtbd.outcome.feature", "unknown")
        analysis.features_used[feature] = analysis.features_used.get(feature, 0) + 1

        persona_val = outcome.get("jtbd.outcome.persona", "unknown")
        analysis.personas[persona_val] = analysis.personas.get(persona_val, 0) + 1

        if outcome.get("jtbd.outcome.exceeds_expectations", False):
            analysis.exceeds_expectations_count += 1

    # Calculate time-to-outcome averages
    for tto in metrics.time_to_outcomes:
        oid = tto.get("jtbd.tto.outcome_id", "unknown")
        if oid in analyses:
            duration = tto.get("jtbd.tto.duration_seconds", 0.0)
            prev_avg = analyses[oid].avg_time_to_outcome
            count = analyses[oid].total_attempts
            analyses[oid].avg_time_to_outcome = ((prev_avg * (count - 1)) + duration) / count

    # Calculate derived metrics
    for analysis in analyses.values():
        analysis.calculate_metrics()

    return analyses


def analyze_feature_effectiveness(metrics: JTBDMetrics) -> dict[str, FeatureEffectiveness]:
    """
    Analyze feature effectiveness and ROI.

    Parameters
    ----------
    metrics : JTBDMetrics
        JTBD metrics to analyze.

    Returns
    -------
    dict[str, FeatureEffectiveness]
        Analysis results keyed by feature name.

    Example
    -------
    >>> metrics = extract_jtbd_metrics(trace_data)
    >>> effectiveness = analyze_feature_effectiveness(metrics)
    >>> for feature, analysis in effectiveness.items():
    ...     print(f"{feature}: {analysis.effectiveness_score:.1f} score")
    """
    features: dict[str, FeatureEffectiveness] = {}

    # Count job completions
    for job in metrics.job_completions:
        feature = job.get("jtbd.job.feature", "unknown")
        if feature not in features:
            features[feature] = FeatureEffectiveness(feature=feature)

        features[feature].total_uses += 1
        if job.get("jtbd.job.status") == JobStatus.COMPLETED.value:
            features[feature].jobs_completed += 1

        persona = job.get("jtbd.job.persona", "unknown")
        if persona not in features[feature].personas_served:
            features[feature].personas_served.append(persona)

    # Count outcome deliveries
    for outcome in metrics.outcome_achievements:
        feature = outcome.get("jtbd.outcome.feature", "unknown")
        if feature not in features:
            features[feature] = FeatureEffectiveness(feature=feature)

        if outcome.get("jtbd.outcome.status") == OutcomeStatus.ACHIEVED.value:
            features[feature].outcomes_delivered += 1

    # Count painpoint resolutions
    for painpoint in metrics.painpoint_resolutions:
        feature = painpoint.get("jtbd.painpoint.feature", "unknown")
        if feature not in features:
            features[feature] = FeatureEffectiveness(feature=feature)

        features[feature].painpoints_resolved += 1

    # Calculate satisfaction metrics
    satisfaction_totals: dict[str, list[float]] = defaultdict(list)
    effort_totals: dict[str, list[float]] = defaultdict(list)
    recommendation_counts: dict[str, dict[str, int]] = defaultdict(
        lambda: {"total": 0, "recommend": 0}
    )

    for satisfaction in metrics.satisfaction_scores:
        feature = satisfaction.get("jtbd.satisfaction.feature", "unknown")

        # Convert satisfaction level to numeric
        level = satisfaction.get("jtbd.satisfaction.level", "neutral")
        level_map = {
            "very_dissatisfied": 1.0,
            "dissatisfied": 2.0,
            "neutral": 3.0,
            "satisfied": 4.0,
            "very_satisfied": 5.0,
        }
        satisfaction_totals[feature].append(level_map.get(level, 3.0))

        # Effort score
        effort = satisfaction.get("jtbd.satisfaction.effort_score")
        if effort is not None:
            effort_totals[feature].append(float(effort))

        # Recommendation rate
        recommendation_counts[feature]["total"] += 1
        if satisfaction.get("jtbd.satisfaction.would_recommend", False):
            recommendation_counts[feature]["recommend"] += 1

    # Calculate averages
    for feature, effectiveness in features.items():
        if satisfaction_totals.get(feature):
            effectiveness.avg_satisfaction = sum(satisfaction_totals[feature]) / len(
                satisfaction_totals[feature]
            )

        if effort_totals.get(feature):
            effectiveness.avg_effort_score = sum(effort_totals[feature]) / len(
                effort_totals[feature]
            )

        if feature in recommendation_counts:
            total = recommendation_counts[feature]["total"]
            recommend = recommendation_counts[feature]["recommend"]
            effectiveness.recommendation_rate = (recommend / total * 100.0) if total > 0 else 0.0

        # Calculate overall effectiveness
        effectiveness.calculate_effectiveness()

    return features


# =============================================================================
# Export Functions
# =============================================================================


def export_metrics(
    metrics: JTBDMetrics, output_path: str | Path, export_format: str = "json"
) -> None:
    """
    Export JTBD metrics to file.

    Parameters
    ----------
    metrics : JTBDMetrics
        Metrics to export.
    output_path : str | Path
        Output file path.
    export_format : str
        Export format: "json" or "csv".

    Example
    -------
    >>> metrics = extract_jtbd_metrics(trace_data)
    >>> export_metrics(metrics, "jtbd_metrics.json", export_format="json")
    >>> export_metrics(metrics, "jtbd_metrics.csv", export_format="csv")
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if export_format == "json":
        with output_path.open("w") as f:
            json.dump(metrics.to_dict(), f, indent=2, default=str)

    elif export_format == "csv":
        # Export each metric type to separate CSV files
        base_path = output_path.with_suffix("")

        _export_csv(
            f"{base_path}_job_completions.csv",
            metrics.job_completions,
            ["jtbd.job.id", "jtbd.job.persona", "jtbd.job.feature", "jtbd.job.status"],
        )

        _export_csv(
            f"{base_path}_outcomes.csv",
            metrics.outcome_achievements,
            [
                "jtbd.outcome.id",
                "jtbd.outcome.feature",
                "jtbd.outcome.achievement_rate",
                "jtbd.outcome.status",
            ],
        )

        _export_csv(
            f"{base_path}_painpoints.csv",
            metrics.painpoint_resolutions,
            [
                "jtbd.painpoint.category",
                "jtbd.painpoint.feature",
                "jtbd.painpoint.resolution_effectiveness",
            ],
        )

    else:
        msg = f"Unsupported format: {export_format}"
        raise ValueError(msg)


def generate_jtbd_report(metrics: JTBDMetrics, output_path: str | Path) -> None:
    """
    Generate comprehensive JTBD report.

    Parameters
    ----------
    metrics : JTBDMetrics
        Metrics to report on.
    output_path : str | Path
        Output markdown file path.

    Example
    -------
    >>> metrics = extract_jtbd_metrics(trace_data)
    >>> generate_jtbd_report(metrics, "jtbd_report.md")
    """
    outcome_analysis = analyze_outcome_delivery(metrics)
    feature_effectiveness = analyze_feature_effectiveness(metrics)

    report_lines = [
        "# JTBD Metrics Report",
        f"\nGenerated: {datetime.now(UTC).isoformat()}",
        "\n## Summary",
        f"- Total Jobs Completed: {len(metrics.job_completions)}",
        f"- Total Outcomes Achieved: {len(metrics.outcome_achievements)}",
        f"- Total Painpoints Resolved: {len(metrics.painpoint_resolutions)}",
        f"- Satisfaction Responses: {len(metrics.satisfaction_scores)}",
        "\n## Outcome Delivery Analysis",
    ]

    for outcome_id, analysis in sorted(outcome_analysis.items()):
        report_lines.extend(
            [
                f"\n### {outcome_id}",
                f"- Delivery Rate: {analysis.delivery_rate:.1f}%",
                f"- Avg Achievement Rate: {analysis.avg_achievement_rate:.1f}%",
                f"- Avg Time to Outcome: {analysis.avg_time_to_outcome:.2f}s",
                f"- Exceeds Expectations: {analysis.exceeds_expectations_count} times",
                "- Features Used:",
            ]
        )
        for feature, count in sorted(
            analysis.features_used.items(), key=lambda x: x[1], reverse=True
        ):
            report_lines.append(f"  - {feature}: {count}")

    report_lines.append("\n## Feature Effectiveness")

    for feature, effectiveness in sorted(
        feature_effectiveness.items(), key=lambda x: x[1].effectiveness_score, reverse=True
    ):
        report_lines.extend(
            [
                f"\n### {feature}",
                f"- Effectiveness Score: {effectiveness.effectiveness_score:.1f}/100",
                f"- Total Uses: {effectiveness.total_uses}",
                f"- Outcomes Delivered: {effectiveness.outcomes_delivered}",
                f"- Painpoints Resolved: {effectiveness.painpoints_resolved}",
                f"- Avg Satisfaction: {effectiveness.avg_satisfaction:.2f}/5.0",
                f"- Recommendation Rate: {effectiveness.recommendation_rate:.1f}%",
                f"- Personas Served: {', '.join(effectiveness.personas_served)}",
            ]
        )

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(report_lines))


# =============================================================================
# Helper Functions
# =============================================================================


def _is_job_completion_event(record: dict[str, Any]) -> bool:
    """Check if record is a job completion event."""
    return record.get("name") == "job_completed" or "jtbd.job.id" in record.get("attributes", {})


def _is_outcome_achievement_event(record: dict[str, Any]) -> bool:
    """Check if record is an outcome achievement event."""
    return record.get("name") == "outcome_achieved" or "jtbd.outcome.id" in record.get(
        "attributes", {}
    )


def _is_painpoint_resolution_event(record: dict[str, Any]) -> bool:
    """Check if record is a painpoint resolution event."""
    return record.get("name") == "painpoint_resolved" or "jtbd.painpoint.id" in record.get(
        "attributes", {}
    )


def _is_time_to_outcome_event(record: dict[str, Any]) -> bool:
    """Check if record is a time-to-outcome event."""
    return record.get("name") == "time_to_outcome" or "jtbd.tto.outcome_id" in record.get(
        "attributes", {}
    )


def _is_satisfaction_event(record: dict[str, Any]) -> bool:
    """Check if record is a satisfaction event."""
    return record.get(
        "name"
    ) == "user_satisfaction" or "jtbd.satisfaction.outcome_id" in record.get("attributes", {})


def _export_csv(file_path: str, data: list[dict[str, Any]], columns: list[str]) -> None:
    """Export data to CSV file."""
    if not data:
        return

    csv_path = Path(file_path)
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in data:
            writer.writerow(row)
