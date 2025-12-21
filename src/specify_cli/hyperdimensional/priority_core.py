"""
specify_cli.hyperdimensional.priority_core
------------------------------------------
Essential feature prioritization using 80/20 value/effort ratio.

This module provides stupidly simple feature prioritization based on ROI:
- Value = job_frequency * outcome_importance
- Effort = manual estimate (1=small, 2=medium, 3=large)
- Priority = value / effort
- Quick wins = features where value/effort > 2.0

No complex optimization, no Pareto frontiers, no sensitivity analysis.
Just practical prioritization that actually works for decision-making.

Example
-------
    from specify_cli.hyperdimensional.priority_core import (
        prioritize_features,
        quick_wins,
        estimate_feature_value,
        estimate_feature_effort,
    )

    features = {
        "deps-add": {
            "job_frequency": 0.9,  # 90% of users need this
            "outcome_importance": 0.8,  # High importance
            "complexity": "small",
        },
        "ggen-sync": {
            "job_frequency": 0.7,
            "outcome_importance": 0.9,
            "complexity": "medium",
        },
    }

    # Get ranked list
    ranked = prioritize_features(features, objectives=["speed", "ease"])

    # Get quick wins (value/effort > 2.0)
    wins = quick_wins(features)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "FeaturePriority",
    "estimate_feature_effort",
    "estimate_feature_value",
    "prioritize_features",
    "quick_wins",
    "top_n_features",
]


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class FeaturePriority:
    """
    Feature prioritization result with value, effort, and priority score.

    Attributes
    ----------
    feature_id : str
        Unique identifier for the feature.
    value : float
        Calculated value score (job_frequency * importance).
    effort : float
        Effort estimate (1=small, 2=medium, 3=large).
    priority : float
        Priority score (value / effort).
    metadata : dict[str, Any]
        Additional feature metadata.
    """

    feature_id: str
    value: float
    effort: float
    priority: float
    metadata: dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        """Readable representation."""
        return (
            f"FeaturePriority(id={self.feature_id!r}, "
            f"value={self.value:.2f}, effort={self.effort:.1f}, "
            f"priority={self.priority:.2f})"
        )


# =============================================================================
# Core Estimation Functions
# =============================================================================


def estimate_feature_value(feature: dict[str, Any]) -> float:
    """
    Estimate feature value using job frequency × outcome importance.

    This is the 80/20 metric: how often users need it × how important it is.

    Parameters
    ----------
    feature : dict[str, Any]
        Feature data with:
        - job_frequency (float): 0.0-1.0, how often users need this
        - outcome_importance (float): 0.0-1.0, importance of outcome

    Returns
    -------
    float
        Value score (0.0-1.0).

    Examples
    --------
    >>> feature = {"job_frequency": 0.9, "outcome_importance": 0.8}
    >>> estimate_feature_value(feature)
    0.72

    >>> feature = {"job_frequency": 0.3, "outcome_importance": 0.5}
    >>> estimate_feature_value(feature)
    0.15
    """
    job_freq = feature.get("job_frequency", 0.5)
    importance = feature.get("outcome_importance", 0.5)

    # Clamp to valid range
    job_freq = max(0.0, min(1.0, job_freq))
    importance = max(0.0, min(1.0, importance))

    return job_freq * importance


def estimate_feature_effort(feature: dict[str, Any]) -> float:
    """
    Estimate feature effort using simple heuristic.

    Effort mapping:
    - "small" / "trivial" / "easy" → 1.0
    - "medium" / "moderate" → 2.0
    - "large" / "complex" / "hard" → 3.0
    - numeric value → used directly (clamped to 1.0-3.0)

    Parameters
    ----------
    feature : dict[str, Any]
        Feature data with:
        - complexity (str | float): complexity indicator
        - effort (float, optional): explicit effort score

    Returns
    -------
    float
        Effort score (1.0-3.0).

    Examples
    --------
    >>> feature = {"complexity": "small"}
    >>> estimate_feature_effort(feature)
    1.0

    >>> feature = {"complexity": "large"}
    >>> estimate_feature_effort(feature)
    3.0

    >>> feature = {"effort": 2.5}
    >>> estimate_feature_effort(feature)
    2.5
    """
    # Explicit effort overrides complexity
    if "effort" in feature:
        effort_val = float(feature["effort"])
        return max(1.0, min(3.0, effort_val))

    # Map complexity to effort
    complexity = feature.get("complexity", "medium")

    if isinstance(complexity, (int, float)):
        return max(1.0, min(3.0, float(complexity)))

    complexity_map = {
        "small": 1.0,
        "trivial": 1.0,
        "easy": 1.0,
        "low": 1.0,
        "medium": 2.0,
        "moderate": 2.0,
        "normal": 2.0,
        "large": 3.0,
        "complex": 3.0,
        "hard": 3.0,
        "high": 3.0,
    }

    return complexity_map.get(str(complexity).lower(), 2.0)


# =============================================================================
# Prioritization Functions
# =============================================================================


def prioritize_features(
    features: dict[str, dict[str, Any]],
    objectives: list[str] | None = None,
) -> list[FeaturePriority]:
    """
    Prioritize features by value/effort ratio.

    Simple ROI-based prioritization:
    1. Calculate value = job_frequency × importance
    2. Estimate effort (1-3 scale)
    3. Priority = value / effort
    4. Sort descending by priority

    Parameters
    ----------
    features : dict[str, dict[str, Any]]
        Feature data keyed by feature_id.
    objectives : list[str], optional
        Objectives to optimize for (currently unused, reserved for future).

    Returns
    -------
    list[FeaturePriority]
        Features sorted by priority (highest first).

    Examples
    --------
    >>> features = {
    ...     "f1": {"job_frequency": 0.9, "outcome_importance": 0.8, "complexity": "small"},
    ...     "f2": {"job_frequency": 0.5, "outcome_importance": 0.6, "complexity": "large"},
    ... }
    >>> ranked = prioritize_features(features)
    >>> ranked[0].feature_id
    'f1'
    >>> ranked[0].priority > ranked[1].priority
    True
    """
    results: list[FeaturePriority] = []

    for feature_id, feature_data in features.items():
        value = estimate_feature_value(feature_data)
        effort = estimate_feature_effort(feature_data)

        # Priority = value / effort (ROI)
        # Add small epsilon to avoid division by zero
        priority = value / max(effort, 0.1)

        results.append(
            FeaturePriority(
                feature_id=feature_id,
                value=value,
                effort=effort,
                priority=priority,
                metadata=feature_data,
            )
        )

    # Sort by priority descending
    results.sort(key=lambda x: x.priority, reverse=True)

    return results


def quick_wins(
    features: dict[str, dict[str, Any]],
    threshold: float = 2.0,
) -> list[FeaturePriority]:
    """
    Identify quick wins where value/effort > threshold.

    Quick wins are features with high ROI - low effort, high value.
    Default threshold of 2.0 means value must be at least 2× effort.

    Parameters
    ----------
    features : dict[str, dict[str, Any]]
        Feature data keyed by feature_id.
    threshold : float, optional
        Minimum priority ratio to qualify as quick win. Default is 2.0.

    Returns
    -------
    list[FeaturePriority]
        Quick win features sorted by priority (highest first).

    Examples
    --------
    >>> features = {
    ...     "high_roi": {"job_frequency": 0.8, "outcome_importance": 0.9, "complexity": "small"},
    ...     "low_roi": {"job_frequency": 0.3, "outcome_importance": 0.4, "complexity": "large"},
    ... }
    >>> wins = quick_wins(features, threshold=2.0)
    >>> len(wins) >= 1
    True
    >>> wins[0].priority > 2.0
    True
    """
    all_features = prioritize_features(features)
    return [f for f in all_features if f.priority > threshold]


def top_n_features(
    features: dict[str, dict[str, Any]],
    n: int = 5,
) -> list[FeaturePriority]:
    """
    Get top N features by priority.

    Convenience function to get the highest-priority features.

    Parameters
    ----------
    features : dict[str, dict[str, Any]]
        Feature data keyed by feature_id.
    n : int, optional
        Number of top features to return. Default is 5.

    Returns
    -------
    list[FeaturePriority]
        Top N features sorted by priority (highest first).

    Examples
    --------
    >>> features = {
    ...     f"f{i}": {"job_frequency": 0.5, "outcome_importance": 0.5, "complexity": "medium"}
    ...     for i in range(10)
    ... }
    >>> top = top_n_features(features, n=3)
    >>> len(top)
    3
    """
    all_features = prioritize_features(features)
    return all_features[:n]
