"""
tests.unit.test_hyperdimensional_priority_core
----------------------------------------------
Unit tests for lean feature prioritization (80/20 value/effort).

Tests cover:
- Value estimation (job_frequency * importance)
- Effort estimation (complexity mapping)
- Priority ranking (value/effort ratio)
- Quick wins detection
- Edge cases (zero values, invalid data)
"""

from __future__ import annotations

import pytest

from specify_cli.hyperdimensional.priority_core import (
    FeaturePriority,
    estimate_feature_effort,
    estimate_feature_value,
    prioritize_features,
    quick_wins,
    top_n_features,
)

# =============================================================================
# Value Estimation Tests
# =============================================================================


def test_estimate_feature_value_basic() -> None:
    """Test basic value calculation: frequency * importance."""
    feature = {
        "job_frequency": 0.8,
        "outcome_importance": 0.9,
    }
    value = estimate_feature_value(feature)
    assert value == pytest.approx(0.72, abs=0.01)


def test_estimate_feature_value_defaults() -> None:
    """Test value calculation with missing fields uses 0.5 default."""
    feature: dict[str, float] = {}
    value = estimate_feature_value(feature)
    assert value == pytest.approx(0.25, abs=0.01)  # 0.5 * 0.5


def test_estimate_feature_value_clamping() -> None:
    """Test value calculation clamps to 0.0-1.0 range."""
    feature = {
        "job_frequency": 1.5,  # Too high
        "outcome_importance": -0.2,  # Too low
    }
    value = estimate_feature_value(feature)
    assert 0.0 <= value <= 1.0


def test_estimate_feature_value_zero() -> None:
    """Test value calculation with zero frequency or importance."""
    feature1 = {"job_frequency": 0.0, "outcome_importance": 0.8}
    assert estimate_feature_value(feature1) == 0.0

    feature2 = {"job_frequency": 0.8, "outcome_importance": 0.0}
    assert estimate_feature_value(feature2) == 0.0


def test_estimate_feature_value_perfect() -> None:
    """Test value calculation with maximum values."""
    feature = {"job_frequency": 1.0, "outcome_importance": 1.0}
    assert estimate_feature_value(feature) == 1.0


# =============================================================================
# Effort Estimation Tests
# =============================================================================


def test_estimate_feature_effort_small() -> None:
    """Test effort estimation for small complexity."""
    assert estimate_feature_effort({"complexity": "small"}) == 1.0
    assert estimate_feature_effort({"complexity": "trivial"}) == 1.0
    assert estimate_feature_effort({"complexity": "easy"}) == 1.0
    assert estimate_feature_effort({"complexity": "low"}) == 1.0


def test_estimate_feature_effort_medium() -> None:
    """Test effort estimation for medium complexity."""
    assert estimate_feature_effort({"complexity": "medium"}) == 2.0
    assert estimate_feature_effort({"complexity": "moderate"}) == 2.0
    assert estimate_feature_effort({"complexity": "normal"}) == 2.0


def test_estimate_feature_effort_large() -> None:
    """Test effort estimation for large complexity."""
    assert estimate_feature_effort({"complexity": "large"}) == 3.0
    assert estimate_feature_effort({"complexity": "complex"}) == 3.0
    assert estimate_feature_effort({"complexity": "hard"}) == 3.0
    assert estimate_feature_effort({"complexity": "high"}) == 3.0


def test_estimate_feature_effort_default() -> None:
    """Test effort estimation with missing or unknown complexity."""
    assert estimate_feature_effort({}) == 2.0
    assert estimate_feature_effort({"complexity": "unknown"}) == 2.0


def test_estimate_feature_effort_numeric() -> None:
    """Test effort estimation with numeric complexity."""
    assert estimate_feature_effort({"complexity": 1.5}) == 1.5
    assert estimate_feature_effort({"complexity": 2.7}) == 2.7


def test_estimate_feature_effort_explicit() -> None:
    """Test effort estimation with explicit effort field."""
    feature = {
        "complexity": "large",  # Would be 3.0
        "effort": 1.5,  # But explicit effort overrides
    }
    assert estimate_feature_effort(feature) == 1.5


def test_estimate_feature_effort_clamping() -> None:
    """Test effort estimation clamps to 1.0-3.0 range."""
    assert estimate_feature_effort({"effort": 0.5}) == 1.0
    assert estimate_feature_effort({"effort": 5.0}) == 3.0


# =============================================================================
# Prioritization Tests
# =============================================================================


def test_prioritize_features_basic() -> None:
    """Test basic feature prioritization."""
    features = {
        "high_value_low_effort": {
            "job_frequency": 0.9,
            "outcome_importance": 0.8,
            "complexity": "small",
        },
        "low_value_high_effort": {
            "job_frequency": 0.3,
            "outcome_importance": 0.4,
            "complexity": "large",
        },
    }

    ranked = prioritize_features(features)

    assert len(ranked) == 2
    assert ranked[0].feature_id == "high_value_low_effort"
    assert ranked[1].feature_id == "low_value_high_effort"
    assert ranked[0].priority > ranked[1].priority


def test_prioritize_features_sorting() -> None:
    """Test features are sorted by priority descending."""
    features = {
        f"f{i}": {
            "job_frequency": 0.5 + (i * 0.1),
            "outcome_importance": 0.6,
            "complexity": "medium",
        }
        for i in range(5)
    }

    ranked = prioritize_features(features)

    # Check descending order
    for i in range(len(ranked) - 1):
        assert ranked[i].priority >= ranked[i + 1].priority


def test_prioritize_features_priority_calculation() -> None:
    """Test priority = value / effort calculation."""
    features = {
        "test_feature": {
            "job_frequency": 0.8,
            "outcome_importance": 0.9,
            "complexity": "medium",
        }
    }

    ranked = prioritize_features(features)
    result = ranked[0]

    expected_value = 0.8 * 0.9  # 0.72
    expected_effort = 2.0  # medium
    expected_priority = expected_value / expected_effort  # 0.36

    assert result.value == pytest.approx(expected_value, abs=0.01)
    assert result.effort == pytest.approx(expected_effort, abs=0.01)
    assert result.priority == pytest.approx(expected_priority, abs=0.01)


def test_prioritize_features_metadata() -> None:
    """Test feature metadata is preserved in results."""
    features = {
        "test_feature": {
            "job_frequency": 0.7,
            "outcome_importance": 0.8,
            "complexity": "small",
            "description": "Test feature",
            "owner": "team-a",
        }
    }

    ranked = prioritize_features(features)
    result = ranked[0]

    assert result.metadata["description"] == "Test feature"
    assert result.metadata["owner"] == "team-a"


def test_prioritize_features_empty() -> None:
    """Test prioritization with empty features."""
    ranked = prioritize_features({})
    assert ranked == []


# =============================================================================
# Quick Wins Tests
# =============================================================================


def test_quick_wins_detection() -> None:
    """Test quick wins detection with default threshold."""
    features = {
        "quick_win": {
            "job_frequency": 0.9,
            "outcome_importance": 0.8,
            "complexity": "small",  # value=0.72, effort=1.0, priority=0.72
        },
        "not_quick_win": {
            "job_frequency": 0.5,
            "outcome_importance": 0.6,
            "complexity": "large",  # value=0.3, effort=3.0, priority=0.1
        },
    }

    wins = quick_wins(features, threshold=2.0)

    # Only features with priority > 2.0 should appear
    assert len(wins) == 0  # Both have priority < 2.0 in this case


def test_quick_wins_custom_threshold() -> None:
    """Test quick wins with custom threshold."""
    features = {
        "medium_roi": {
            "job_frequency": 0.6,
            "outcome_importance": 0.7,
            "complexity": "medium",  # value=0.42, effort=2.0, priority=0.21
        },
        "high_roi": {
            "job_frequency": 0.8,
            "outcome_importance": 0.9,
            "complexity": "small",  # value=0.72, effort=1.0, priority=0.72
        },
    }

    wins = quick_wins(features, threshold=0.5)

    # Only high_roi should qualify
    assert len(wins) == 1
    assert wins[0].feature_id == "high_roi"


def test_quick_wins_empty() -> None:
    """Test quick wins with no qualifying features."""
    features = {
        "low_priority": {
            "job_frequency": 0.2,
            "outcome_importance": 0.3,
            "complexity": "large",
        }
    }

    wins = quick_wins(features, threshold=5.0)
    assert len(wins) == 0


def test_quick_wins_sorting() -> None:
    """Test quick wins are sorted by priority."""
    features = {
        f"win{i}": {
            "job_frequency": 0.7 + (i * 0.05),
            "outcome_importance": 0.8,
            "complexity": "small",
        }
        for i in range(3)
    }

    wins = quick_wins(features, threshold=0.4)

    # Check descending order
    for i in range(len(wins) - 1):
        assert wins[i].priority >= wins[i + 1].priority


# =============================================================================
# Top N Features Tests
# =============================================================================


def test_top_n_features_basic() -> None:
    """Test getting top N features."""
    features = {
        f"f{i}": {
            "job_frequency": 0.5 + (i * 0.1),
            "outcome_importance": 0.6,
            "complexity": "medium",
        }
        for i in range(10)
    }

    top = top_n_features(features, n=3)

    assert len(top) == 3
    # Verify descending order
    assert top[0].priority >= top[1].priority >= top[2].priority


def test_top_n_features_fewer_than_n() -> None:
    """Test getting top N when fewer features exist."""
    features = {
        "f1": {"job_frequency": 0.7, "outcome_importance": 0.8, "complexity": "small"}
    }

    top = top_n_features(features, n=5)

    assert len(top) == 1


def test_top_n_features_default() -> None:
    """Test top N features with default n=5."""
    features = {
        f"f{i}": {
            "job_frequency": 0.5,
            "outcome_importance": 0.6,
            "complexity": "medium",
        }
        for i in range(10)
    }

    top = top_n_features(features)

    assert len(top) == 5


# =============================================================================
# Edge Cases
# =============================================================================


def test_feature_priority_repr() -> None:
    """Test FeaturePriority string representation."""
    priority = FeaturePriority(
        feature_id="test",
        value=0.72,
        effort=2.0,
        priority=0.36,
    )

    repr_str = repr(priority)
    assert "test" in repr_str
    assert "0.72" in repr_str
    assert "2.0" in repr_str
    assert "0.36" in repr_str


def test_zero_effort_protection() -> None:
    """Test division by zero protection in priority calculation."""
    features = {
        "zero_effort": {
            "job_frequency": 0.8,
            "outcome_importance": 0.9,
            "effort": 0.0,  # Should use epsilon to avoid division by zero
        }
    }

    ranked = prioritize_features(features)

    # Should not raise exception
    assert len(ranked) == 1
    assert ranked[0].priority > 0  # Uses epsilon, so priority is very high


def test_case_insensitive_complexity() -> None:
    """Test complexity mapping is case-insensitive."""
    assert estimate_feature_effort({"complexity": "SMALL"}) == 1.0
    assert estimate_feature_effort({"complexity": "Medium"}) == 2.0
    assert estimate_feature_effort({"complexity": "LARGE"}) == 3.0
