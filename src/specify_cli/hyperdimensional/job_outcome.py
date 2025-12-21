"""Job-outcome reasoning for Jobs-to-be-Done framework analysis.

This module implements reasoning capabilities for analyzing job-outcome alignment,
feature coverage, and outcome delivery confidence using hyperdimensional computing
and information-theoretic principles.

Based on the Jobs-to-be-Done (JTBD) framework:
- Jobs: Tasks users are trying to accomplish
- Outcomes: Measurable success criteria for jobs
- Features: Product capabilities that deliver outcomes
- Pain Points: Obstacles preventing outcome achievement

Example:
    >>> from specify_cli.hyperdimensional.job_outcome import (
    ...     features_covering_job,
    ...     job_coverage_completeness,
    ...     outcome_delivery_certainty,
    ... )
    >>>
    >>> # Find features that address a job
    >>> job = "deploy microservice to production"
    >>> features = features_covering_job(job, feature_db)
    >>>
    >>> # Measure coverage completeness
    >>> completeness = job_coverage_completeness(job, features, outcomes)
    >>>
    >>> # Assess outcome delivery confidence
    >>> confidence = outcome_delivery_certainty(feature, outcome, evidence_db)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import numpy as np
from numpy.typing import NDArray

from specify_cli.hyperdimensional.reasoning import (
    cosine_similarity,
    normalize_vector,
)

logger = logging.getLogger(__name__)

# Type aliases
Vector = NDArray[np.float64]
VectorSet = list[Vector]


# ============================================================================
# Job-Outcome Data Structures
# ============================================================================


@dataclass
class Job:
    """Represents a job-to-be-done.

    Attributes:
        name: Job name/identifier
        description: Detailed job description
        vector: Hyperdimensional representation
        context: Contextual information (user type, situation, etc.)
        frequency: How often job occurs (0.0 to 1.0)
        importance: Job importance to users (0.0 to 1.0)
    """

    name: str
    description: str
    vector: Vector
    context: dict[str, Any] = field(default_factory=dict)
    frequency: float = 0.5
    importance: float = 0.5


@dataclass
class Outcome:
    """Represents a desired outcome for a job.

    Attributes:
        name: Outcome name
        description: Detailed description
        vector: Hyperdimensional representation
        measurement: How outcome is measured
        target_value: Target value for success
        current_satisfaction: Current user satisfaction (0.0 to 1.0)
    """

    name: str
    description: str
    vector: Vector
    measurement: str
    target_value: float | None = None
    current_satisfaction: float = 0.5


@dataclass
class Feature:
    """Represents a product feature.

    Attributes:
        name: Feature name
        description: Detailed description
        vector: Hyperdimensional representation
        implementation_status: Status (planned, in_progress, complete)
        outcomes_addressed: Outcomes this feature delivers
        pain_points_resolved: Pain points this feature resolves
    """

    name: str
    description: str
    vector: Vector
    implementation_status: str = "planned"
    outcomes_addressed: list[str] = field(default_factory=list)
    pain_points_resolved: list[str] = field(default_factory=list)


@dataclass
class PainPoint:
    """Represents an obstacle preventing outcome achievement.

    Attributes:
        name: Pain point name
        description: Detailed description
        vector: Hyperdimensional representation
        severity: How severe the pain is (0.0 to 1.0)
        frequency: How often it occurs (0.0 to 1.0)
        related_job: Associated job
    """

    name: str
    description: str
    vector: Vector
    severity: float = 0.5
    frequency: float = 0.5
    related_job: str | None = None


# ============================================================================
# Job Coverage Analysis
# ============================================================================


def features_covering_job(
    job: Job | str,
    feature_db: dict[str, Feature],
    similarity_threshold: float = 0.6,
) -> list[tuple[Feature, float]]:
    """Identify features that cover a specific job.

    Args:
        job: Job object or job name
        feature_db: Database of features
        similarity_threshold: Minimum similarity to consider relevant

    Returns:
        List of (feature, relevance_score) tuples, sorted by relevance

    Example:
        >>> job = Job(name="deploy", description="Deploy service", vector=job_vec)
        >>> features = features_covering_job(job, feature_db, similarity_threshold=0.7)
        >>> for feature, score in features:
        ...     print(f"{feature.name}: {score:.2f}")
    """
    if isinstance(job, str):
        # Simple string job - create placeholder vector
        job_vector = normalize_vector(np.random.randn(10000))
    else:
        job_vector = job.vector

    # Find relevant features
    relevant_features = []

    for _feature_name, feature in feature_db.items():
        similarity = cosine_similarity(job_vector, feature.vector)

        if similarity >= similarity_threshold:
            relevant_features.append((feature, similarity))

    # Sort by relevance
    relevant_features.sort(key=lambda x: x[1], reverse=True)

    logger.info(
        "Found %d features covering job (threshold: %.2f)",
        len(relevant_features),
        similarity_threshold,
    )

    return relevant_features


def job_coverage_completeness(
    job: Job,
    features: list[Feature],
    outcomes: list[Outcome],
) -> dict[str, float]:
    """Measure how completely features cover job outcomes.

    Args:
        job: Job to analyze
        features: Features available
        outcomes: Desired outcomes for the job

    Returns:
        Dict with completeness metrics

    Example:
        >>> completeness = job_coverage_completeness(job, features, outcomes)
        >>> if completeness["overall"] < 0.8:
        ...     print("Incomplete coverage - add more features")
    """
    if not outcomes:
        return {"overall": 0.0, "outcome_coverage": {}}

    outcome_coverage = {}

    # For each outcome, find best covering feature
    for outcome in outcomes:
        best_coverage = 0.0

        for feature in features:
            # Measure how well feature delivers outcome
            coverage = cosine_similarity(feature.vector, outcome.vector)
            best_coverage = max(best_coverage, coverage)

        outcome_coverage[outcome.name] = best_coverage

    # Overall completeness: average coverage across all outcomes
    overall_completeness = sum(outcome_coverage.values()) / len(outcome_coverage)

    # Identify gaps (outcomes with low coverage)
    gaps = [name for name, cov in outcome_coverage.items() if cov < 0.6]

    result = {
        "overall": overall_completeness,
        "outcome_coverage": outcome_coverage,
        "num_outcomes": len(outcomes),
        "num_covered": sum(1 for cov in outcome_coverage.values() if cov >= 0.6),
        "gaps": gaps,
        "completeness_score": overall_completeness,
    }

    logger.info(
        "Job coverage: %.1f%% complete (%d/%d outcomes covered)",
        overall_completeness * 100,
        result["num_covered"],
        len(outcomes),
    )

    return result


def identify_unmet_needs(
    job: Job,
    current_features: list[Feature],
    desired_outcomes: list[Outcome],
    threshold: float = 0.6,
) -> list[dict[str, Any]]:
    """Identify unmet needs (outcomes not adequately delivered by features).

    Args:
        job: Job being analyzed
        current_features: Currently available features
        desired_outcomes: Desired outcomes for the job
        threshold: Minimum coverage to consider outcome met

    Returns:
        List of unmet need descriptions

    Example:
        >>> unmet = identify_unmet_needs(job, features, outcomes, threshold=0.7)
        >>> for need in unmet:
        ...     print(f"Unmet: {need['outcome']}")
    """
    unmet_needs = []

    for outcome in desired_outcomes:
        # Find best coverage from current features
        best_coverage = 0.0
        best_feature = None

        for feature in current_features:
            coverage = cosine_similarity(feature.vector, outcome.vector)
            if coverage > best_coverage:
                best_coverage = coverage
                best_feature = feature

        # Check if outcome is unmet
        if best_coverage < threshold:
            gap = threshold - best_coverage

            unmet_needs.append(
                {
                    "outcome": outcome.name,
                    "description": outcome.description,
                    "current_coverage": best_coverage,
                    "gap": gap,
                    "best_feature": best_feature.name if best_feature else "none",
                    "suggested_action": _suggest_feature_for_outcome(outcome),
                }
            )

    # Sort by gap size (largest gaps first)
    unmet_needs.sort(key=lambda x: x["gap"], reverse=True)

    logger.info("Identified %d unmet needs (threshold: %.2f)", len(unmet_needs), threshold)

    return unmet_needs


def _suggest_feature_for_outcome(outcome: Outcome) -> str:
    """Suggest a feature to deliver an outcome.

    Args:
        outcome: Outcome needing coverage

    Returns:
        Feature suggestion description
    """
    # Simple rule-based suggestions (would use ML in production)
    outcome_lower = outcome.name.lower()

    if "deploy" in outcome_lower:
        return "Add deployment automation feature"
    if "monitor" in outcome_lower:
        return "Add monitoring and observability feature"
    if "secure" in outcome_lower or "security" in outcome_lower:
        return "Add security controls feature"
    if "scale" in outcome_lower:
        return "Add auto-scaling feature"

    return f"Add feature to deliver '{outcome.name}'"


# ============================================================================
# Outcome Alignment
# ============================================================================


def outcome_delivery_certainty(
    feature: Feature,
    outcome: Outcome,
    evidence_db: dict[str, Any] | None = None,
) -> dict[str, float]:
    """Assess confidence that feature will deliver outcome.

    Args:
        feature: Feature to evaluate
        outcome: Desired outcome
        evidence_db: Optional database of empirical evidence

    Returns:
        Dict with certainty metrics

    Example:
        >>> certainty = outcome_delivery_certainty(feature, outcome)
        >>> if certainty["confidence"] > 0.8:
        ...     print("High confidence in outcome delivery")
    """
    # Base confidence from semantic similarity
    semantic_similarity = cosine_similarity(feature.vector, outcome.vector)

    # Adjust based on implementation status
    status_multipliers = {
        "complete": 1.0,
        "in_progress": 0.7,
        "planned": 0.4,
        "proposed": 0.2,
    }

    status_multiplier = status_multipliers.get(feature.implementation_status, 0.5)

    # Check if outcome is explicitly listed
    explicit_match = outcome.name in feature.outcomes_addressed
    explicit_bonus = 0.2 if explicit_match else 0.0

    # Combine factors
    base_confidence = semantic_similarity * status_multiplier + explicit_bonus
    base_confidence = min(base_confidence, 1.0)

    # Adjust based on evidence if available
    if evidence_db:
        evidence_key = f"{feature.name}_{outcome.name}"
        empirical_success_rate = evidence_db.get(evidence_key, 0.5)

        # Weighted average: 70% semantic, 30% empirical
        final_confidence = 0.7 * base_confidence + 0.3 * empirical_success_rate
    else:
        final_confidence = base_confidence

    result = {
        "confidence": final_confidence,
        "semantic_similarity": semantic_similarity,
        "status_factor": status_multiplier,
        "explicit_match": explicit_match,
        "certainty_level": _categorize_certainty(final_confidence),
    }

    logger.debug(
        "Outcome delivery certainty: %.2f (%s)",
        final_confidence,
        result["certainty_level"],
    )

    return result


def _categorize_certainty(confidence: float) -> str:
    """Categorize confidence level.

    Args:
        confidence: Confidence score

    Returns:
        Category label
    """
    if confidence >= 0.9:
        return "very_high"
    if confidence >= 0.7:
        return "high"
    if confidence >= 0.5:
        return "medium"
    if confidence >= 0.3:
        return "low"
    return "very_low"


def feature_outcome_chains(
    feature: Feature,
    outcome_db: dict[str, Outcome],
    max_hops: int = 3,
) -> list[list[str]]:
    """Identify chains of value delivery from feature to outcomes.

    Traces how a feature delivers value through intermediate outcomes
    to final user outcomes.

    Args:
        feature: Starting feature
        outcome_db: Database of outcomes
        max_hops: Maximum chain length

    Returns:
        List of outcome chains (each chain is list of outcome names)

    Example:
        >>> chains = feature_outcome_chains(feature, outcomes, max_hops=2)
        >>> for chain in chains:
        ...     print(" -> ".join(chain))
    """
    chains = []

    # Start with direct outcomes
    direct_outcomes = [name for name in feature.outcomes_addressed if name in outcome_db]

    for outcome_name in direct_outcomes:
        # Build chain from this outcome
        chain = [outcome_name]
        current_vec = outcome_db[outcome_name].vector

        # Extend chain by finding related outcomes
        for _hop in range(max_hops - 1):
            # Find most similar unvisited outcome
            best_similarity = 0.0
            best_outcome = None

            for next_name, next_outcome in outcome_db.items():
                if next_name not in chain:
                    similarity = cosine_similarity(current_vec, next_outcome.vector)

                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_outcome = next_name

            # Add to chain if similar enough
            if best_outcome and best_similarity > 0.6:
                chain.append(best_outcome)
                current_vec = outcome_db[best_outcome].vector
            else:
                break

        if len(chain) > 1:
            chains.append(chain)

    logger.info("Identified %d outcome chains for feature '%s'", len(chains), feature.name)

    return chains


def painpoint_resolution_effectiveness(
    feature: Feature,
    pain_point: PainPoint,
) -> dict[str, float]:
    """Assess how effectively feature resolves a pain point.

    Args:
        feature: Feature to evaluate
        pain_point: Pain point to resolve

    Returns:
        Dict with effectiveness metrics

    Example:
        >>> effectiveness = painpoint_resolution_effectiveness(feature, pain_point)
        >>> if effectiveness["impact_score"] > 0.7:
        ...     print("Feature effectively resolves pain point")
    """
    # Semantic similarity between feature and pain point
    similarity = cosine_similarity(feature.vector, pain_point.vector)

    # Check if pain point is explicitly addressed
    explicit_match = pain_point.name in feature.pain_points_resolved
    explicit_bonus = 0.3 if explicit_match else 0.0

    # Base resolution effectiveness
    base_effectiveness = float(min(similarity + explicit_bonus, 1.0))

    # Impact score = effectiveness * pain severity * pain frequency
    impact_score = float(base_effectiveness * pain_point.severity * pain_point.frequency)

    result = {
        "effectiveness": base_effectiveness,
        "semantic_similarity": float(similarity),
        "explicit_match": explicit_match,
        "pain_severity": float(pain_point.severity),
        "pain_frequency": float(pain_point.frequency),
        "impact_score": impact_score,
        "roi_estimate": float(impact_score * 100),  # Rough ROI percentage
    }

    logger.debug(
        "Pain point resolution: %.2f effectiveness, %.2f impact",
        base_effectiveness,
        impact_score,
    )

    return result


# ============================================================================
# Job-Outcome Alignment Metrics
# ============================================================================


def compute_job_outcome_alignment(
    jobs: list[Job],
    outcomes: list[Outcome],
    features: list[Feature],
) -> dict[str, Any]:
    """Compute comprehensive job-outcome alignment metrics.

    Args:
        jobs: List of jobs
        outcomes: List of desired outcomes
        features: List of available features

    Returns:
        Dict with alignment metrics and analysis

    Example:
        >>> alignment = compute_job_outcome_alignment(jobs, outcomes, features)
        >>> print(f"Overall alignment: {alignment['overall_alignment']:.1%}")
    """
    # Job coverage by features
    job_coverage = {}
    for job in jobs:
        covered_features = features_covering_job(job, {f.name: f for f in features})
        coverage_score = len(covered_features) / max(len(features), 1)
        job_coverage[job.name] = coverage_score

    # Outcome delivery by features
    outcome_delivery = {}
    for outcome in outcomes:
        best_delivery = 0.0
        for feature in features:
            certainty = outcome_delivery_certainty(feature, outcome)
            best_delivery = max(best_delivery, certainty["confidence"])
        outcome_delivery[outcome.name] = best_delivery

    # Overall alignment score
    avg_job_coverage = sum(job_coverage.values()) / max(len(job_coverage), 1)
    avg_outcome_delivery = sum(outcome_delivery.values()) / max(len(outcome_delivery), 1)
    overall_alignment = (avg_job_coverage + avg_outcome_delivery) / 2.0

    # Identify gaps
    poorly_covered_jobs = [name for name, score in job_coverage.items() if score < 0.5]
    poorly_delivered_outcomes = [name for name, score in outcome_delivery.items() if score < 0.5]

    result = {
        "overall_alignment": overall_alignment,
        "job_coverage": job_coverage,
        "outcome_delivery": outcome_delivery,
        "avg_job_coverage": avg_job_coverage,
        "avg_outcome_delivery": avg_outcome_delivery,
        "num_jobs": len(jobs),
        "num_outcomes": len(outcomes),
        "num_features": len(features),
        "poorly_covered_jobs": poorly_covered_jobs,
        "poorly_delivered_outcomes": poorly_delivered_outcomes,
        "alignment_grade": _grade_alignment(overall_alignment),
    }

    logger.info(
        "Job-outcome alignment: %.1f%% (%s grade)",
        overall_alignment * 100,
        result["alignment_grade"],
    )

    return result


def _grade_alignment(score: float) -> str:
    """Convert alignment score to letter grade.

    Args:
        score: Alignment score (0.0 to 1.0)

    Returns:
        Letter grade (A+ to F)
    """
    if score >= 0.95:
        return "A+"
    if score >= 0.9:
        return "A"
    if score >= 0.85:
        return "A-"
    if score >= 0.8:
        return "B+"
    if score >= 0.75:
        return "B"
    if score >= 0.7:
        return "B-"
    if score >= 0.65:
        return "C+"
    if score >= 0.6:
        return "C"
    if score >= 0.5:
        return "C-"
    if score >= 0.4:
        return "D"
    return "F"


def prioritize_features_by_job_impact(
    features: list[Feature],
    jobs: list[Job],
    outcomes: list[Outcome],
) -> list[tuple[Feature, float]]:
    """Prioritize features by their impact on job success.

    Args:
        features: List of features to prioritize
        jobs: List of jobs
        outcomes: List of desired outcomes

    Returns:
        List of (feature, impact_score) tuples, sorted by impact

    Example:
        >>> prioritized = prioritize_features_by_job_impact(features, jobs, outcomes)
        >>> top_feature = prioritized[0][0]
        >>> print(f"Top priority: {top_feature.name}")
    """
    feature_impacts = []

    for feature in features:
        total_impact = 0.0

        # Impact on jobs
        for job in jobs:
            similarity = cosine_similarity(feature.vector, job.vector)
            job_impact = similarity * job.importance * job.frequency
            total_impact += job_impact

        # Impact on outcomes
        for outcome in outcomes:
            certainty = outcome_delivery_certainty(feature, outcome)
            outcome_impact = certainty["confidence"] * (1.0 - outcome.current_satisfaction)
            total_impact += outcome_impact

        # Normalize by number of jobs and outcomes
        avg_impact = total_impact / (len(jobs) + len(outcomes))
        feature_impacts.append((feature, avg_impact))

    # Sort by impact
    feature_impacts.sort(key=lambda x: x[1], reverse=True)

    logger.info("Prioritized %d features by job impact", len(features))

    return feature_impacts
