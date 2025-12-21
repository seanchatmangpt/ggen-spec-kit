"""Unit tests for hyperdimensional decision support module."""

from __future__ import annotations

import pytest

from specify_cli.hyperdimensional.decision_support import (
    DecisionSupportSystem,
    Recommendation,
    RiskAssessment,
    TradeOffAnalysis,
)


@pytest.fixture
def dss():
    """Create decision support system instance."""
    return DecisionSupportSystem(min_confidence=0.7, enable_explanations=True)


@pytest.fixture
def sample_objectives():
    """Create sample objectives."""
    return {
        "performance": 0.8,
        "reliability": 0.9,
        "maintainability": 0.7,
    }


@pytest.fixture
def sample_features():
    """Create sample features."""
    return [
        {
            "id": "feat1",
            "name": "Feature 1",
            "addresses_objectives": ["performance", "reliability"],
            "benefits": ["Fast", "Stable"],
        },
        {
            "id": "feat2",
            "name": "Feature 2",
            "addresses_objectives": ["maintainability"],
            "benefits": ["Clean code"],
        },
        {
            "id": "feat3",
            "name": "Feature 3",
            "addresses_objectives": ["performance", "maintainability"],
            "benefits": ["Optimized", "Documented"],
        },
    ]


# =================================================================
# Recommendation Engine Tests
# =================================================================


def test_show_recommended_features(dss, sample_objectives, sample_features):
    """Test feature recommendation."""
    recommendations = dss.show_recommended_features(
        sample_objectives,
        sample_features,
        top_k=2,
    )

    assert len(recommendations) <= 2
    assert all(isinstance(r, Recommendation) for r in recommendations)
    assert all(r.confidence >= dss.min_confidence for r in recommendations)

    # Verify sorting by score
    if len(recommendations) > 1:
        assert recommendations[0].score >= recommendations[1].score


def test_recommend_features_low_confidence_filtered(dss):
    """Test that low confidence recommendations are filtered."""
    objectives = {"obj1": 1.0}
    features = [
        {"id": "f1", "name": "Feature 1", "addresses_objectives": []},  # No match = low confidence
    ]

    recommendations = dss.show_recommended_features(objectives, features)

    # Should be filtered due to low confidence
    assert len(recommendations) == 0


def test_explain_recommendation(dss):
    """Test recommendation explanation."""
    recommendation = Recommendation(
        feature_name="Test Feature",
        score=0.85,
        reasoning="This feature aligns well with objectives.",
        confidence=0.9,
        alternatives=["Alt 1", "Alt 2"],
        metadata={"matched_objectives": ["obj1", "obj2"]},
    )

    explanation = dss.explain_recommendation(recommendation)

    assert isinstance(explanation, str)
    assert "Test Feature" in explanation
    assert "0.85" in explanation
    assert "obj1" in explanation


def test_show_trade_offs(dss):
    """Test trade-off analysis."""
    options = [
        {
            "name": "Option A",
            "speed": 0.9,
            "reliability": 0.6,
            "simplicity": 0.8,
        },
        {
            "name": "Option B",
            "speed": 0.5,
            "reliability": 0.9,
            "simplicity": 0.9,
        },
    ]

    dimensions = ["speed", "reliability", "simplicity"]

    analyses = dss.show_trade_offs(options, dimensions)

    assert len(analyses) == len(options)
    assert all(isinstance(a, TradeOffAnalysis) for a in analyses)

    # Verify overall scores are calculated
    for analysis in analyses:
        assert 0.0 <= analysis.overall_score <= 1.0
        assert len(analysis.dimensions) == len(dimensions)


def test_cost_benefit_analysis(dss):
    """Test cost-benefit analysis."""
    option = {
        "name": "Test Option",
        "costs": {"development": 100, "maintenance": 50},
        "benefits": {"revenue": 300, "efficiency": 100},
    }

    result = dss.cost_benefit_analysis(option)

    assert result["option_name"] == "Test Option"
    assert result["total_cost"] == 150
    assert result["total_benefit"] == 400
    assert result["net_benefit"] == 250
    assert result["roi_percentage"] > 0
    assert result["recommendation"] == "approve"


# =================================================================
# Priority Visualization Tests
# =================================================================


def test_priority_matrix(dss):
    """Test priority matrix generation."""
    tasks = [
        {"name": "Task 1", "urgency": 0.8, "importance": 0.9},
        {"name": "Task 2", "urgency": 0.3, "importance": 0.7},
        {"name": "Task 3", "urgency": 0.6, "importance": 0.4},
    ]

    viz = dss.priority_matrix(tasks, dimensions=("urgency", "importance"))

    assert viz.chart_type == "scatter"
    assert len(viz.data["x"]) == len(tasks)
    assert len(viz.data["quadrants"]) == len(tasks)


def test_impact_effort_chart(dss):
    """Test impact vs effort chart."""
    tasks = [
        {"name": "Quick Win", "impact": 0.9, "effort": 0.2},
        {"name": "Major Project", "impact": 0.9, "effort": 0.9},
        {"name": "Fill In", "impact": 0.2, "effort": 0.2},
    ]

    viz = dss.impact_effort_chart(tasks)

    assert viz.chart_type == "scatter"
    assert "quick_wins" in viz.data["categories"]
    assert viz.metadata["quick_wins"] >= 1


def test_critical_path_visualization(dss):
    """Test critical path analysis."""
    tasks = [
        {"name": "Task A", "duration": 5},
        {"name": "Task B", "duration": 3},
        {"name": "Task C", "duration": 4},
    ]

    dependencies = [
        ("Task A", "Task B"),
        ("Task B", "Task C"),
    ]

    viz = dss.critical_path_visualization(tasks, dependencies)

    assert viz.chart_type == "gantt"
    assert len(viz.data["critical_tasks"]) > 0
    assert viz.metadata["total_duration"] >= 0


# =================================================================
# Risk Assessment Tests
# =================================================================


def test_risk_heatmap(dss):
    """Test risk heatmap generation."""
    designs = [
        {
            "name": "Design A",
            "vulnerabilities": ["risk1"],
        },
        {
            "name": "Design B",
            "vulnerabilities": ["risk1", "risk2"],
        },
    ]

    risks = [
        {"id": "risk1", "name": "Risk 1", "probability": 0.7, "impact": 0.8},
        {"id": "risk2", "name": "Risk 2", "probability": 0.5, "impact": 0.6},
    ]

    viz = dss.risk_heatmap(designs, risks)

    assert viz.chart_type == "heatmap"
    assert len(viz.data["designs"]) == len(designs)
    assert len(viz.data["risks"]) == len(risks)


def test_failure_mode_visualization(dss):
    """Test failure mode visualization."""
    system = {
        "components": [
            {
                "name": "Component A",
                "failure_modes": [
                    {
                        "name": "Mode 1",
                        "probability": 0.8,
                        "impact": 0.9,
                        "mitigations": ["Mitigation 1"],
                    },
                ],
            },
        ],
    }

    assessments = dss.failure_mode_visualization(system)

    assert len(assessments) > 0
    assert all(isinstance(a, RiskAssessment) for a in assessments)
    assert assessments[0].severity == "critical"  # High probability * high impact


def test_mitigation_strategy_recommender(dss):
    """Test mitigation strategy recommendation."""
    risk = RiskAssessment(
        risk_name="High Risk",
        probability=0.9,
        impact=0.8,
        severity="critical",
        mitigation_strategies=["Existing mitigation"],
    )

    strategies = dss.mitigation_strategy_recommender(risk)

    assert len(strategies) > 0
    assert any(s["type"] == "prevention" for s in strategies)
    assert any(s["type"] == "impact_reduction" for s in strategies)
    assert any(s["type"] == "monitoring" for s in strategies)


# =================================================================
# Edge Cases
# =================================================================


def test_empty_objectives(dss):
    """Test with empty objectives."""
    recommendations = dss.show_recommended_features(
        {},
        [{"id": "f1", "name": "Feature 1", "addresses_objectives": []}],
    )

    assert len(recommendations) == 0


def test_empty_features(dss, sample_objectives):
    """Test with no available features."""
    recommendations = dss.show_recommended_features(
        sample_objectives,
        [],
    )

    assert len(recommendations) == 0


def test_negative_roi(dss):
    """Test cost-benefit with negative ROI."""
    option = {
        "name": "Bad Option",
        "costs": 200,
        "benefits": 50,
    }

    result = dss.cost_benefit_analysis(option)

    assert result["net_benefit"] < 0
    assert result["roi_percentage"] < 0
    assert result["recommendation"] == "reject"
