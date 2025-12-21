"""Unit tests for architectural decision framework."""

from __future__ import annotations

import numpy as np

from specify_cli.hyperdimensional.decision_framework import (
    DesignAlternative,
    ParetoFrontier,
    Risk,
    evaluate_design_option,
    failure_mode_analysis,
    generate_design_alternatives,
    identify_risks,
    multi_objective_score,
    pareto_frontier,
    rank_alternatives,
    risk_mitigation_strategies,
    sensitivity_analysis,
    trade_off_visualization,
)


class TestDesignSpaceExploration:
    """Tests for design space exploration."""

    def test_generate_design_alternatives(self) -> None:
        """Test design alternative generation."""
        requirements = {"scalability": 0.9, "simplicity": 0.7}

        alternatives = generate_design_alternatives(requirements, count=10, diversity_weight=0.5)

        assert len(alternatives) == 10
        assert all(isinstance(alt, DesignAlternative) for alt in alternatives)
        assert all(alt.vector.shape[0] == 10000 for alt in alternatives)

    def test_evaluate_design_option(self) -> None:
        """Test design evaluation."""
        design = DesignAlternative(
            vector=np.random.randn(100),
            quality_scores={"performance": 0.8, "cost": 0.6},
        )

        objectives = {
            "performance": lambda d: d.quality_scores.get("performance", 0.0),
            "cost": lambda d: d.quality_scores.get("cost", 0.0),
        }

        score = evaluate_design_option(design, objectives)

        assert 0.0 <= score <= 1.0

    def test_rank_alternatives(self) -> None:
        """Test ranking of alternatives."""
        designs = [
            DesignAlternative(
                vector=np.random.randn(100),
                quality_scores={"score": 0.8},
            ),
            DesignAlternative(
                vector=np.random.randn(100),
                quality_scores={"score": 0.6},
            ),
            DesignAlternative(
                vector=np.random.randn(100),
                quality_scores={"score": 0.9},
            ),
        ]

        objectives = {"score": lambda d: d.quality_scores.get("score", 0.0)}

        ranked = rank_alternatives(designs, objectives)

        # Should be sorted by score
        assert ranked[0][1] >= ranked[1][1] >= ranked[2][1]

    def test_sensitivity_analysis(self) -> None:
        """Test sensitivity analysis."""
        design = DesignAlternative(
            vector=np.random.randn(100),
            quality_scores={"score": 0.8},
        )

        sensitivity = sensitivity_analysis(design, perturbation_magnitude=0.1, num_samples=50)

        assert "mean_score_change" in sensitivity
        assert "max_score_change" in sensitivity
        assert "std_score_change" in sensitivity
        assert "robustness" in sensitivity
        assert 0.0 <= sensitivity["robustness"] <= 1.0


class TestTradeOffAnalysis:
    """Tests for trade-off analysis."""

    def test_pareto_frontier(self) -> None:
        """Test Pareto frontier identification."""
        designs = [
            DesignAlternative(
                vector=np.random.randn(100),
                quality_scores={"performance": 0.9, "cost": 0.3},
            ),
            DesignAlternative(
                vector=np.random.randn(100),
                quality_scores={"performance": 0.3, "cost": 0.9},
            ),
            DesignAlternative(
                vector=np.random.randn(100),
                quality_scores={"performance": 0.5, "cost": 0.5},
            ),
        ]

        frontier = pareto_frontier(designs, ["performance", "cost"])

        assert isinstance(frontier, ParetoFrontier)
        assert len(frontier.designs) >= 1
        assert len(frontier.designs) + len(frontier.dominated_designs) == len(designs)

    def test_multi_objective_score(self) -> None:
        """Test multi-objective scoring."""
        design = DesignAlternative(
            vector=np.random.randn(100),
            quality_scores={"performance": 0.8, "cost": 0.6},
        )

        objectives = {"performance": 0.7, "cost": 0.3}

        scores = multi_objective_score(design, objectives, method="weighted_sum")

        assert "aggregate_score" in scores
        assert "method" in scores
        assert 0.0 <= scores["aggregate_score"] <= 1.0

    def test_trade_off_visualization(self) -> None:
        """Test trade-off visualization data generation."""
        designs = [
            DesignAlternative(
                vector=np.random.randn(100),
                quality_scores={"performance": 0.8, "cost": 0.6},
            ),
            DesignAlternative(
                vector=np.random.randn(100),
                quality_scores={"performance": 0.6, "cost": 0.8},
            ),
        ]

        viz_data = trade_off_visualization(designs, ["performance", "cost"])

        assert "objectives" in viz_data
        assert "objective_scores" in viz_data
        assert "pareto_optimal_indices" in viz_data
        assert "correlations" in viz_data
        # Check that indices are integers not arrays
        assert all(isinstance(idx, (int, np.integer)) for idx in viz_data["pareto_optimal_indices"])


class TestRiskAssessment:
    """Tests for risk assessment."""

    def test_identify_risks(self) -> None:
        """Test risk identification."""
        design = DesignAlternative(
            vector=np.random.randn(100),
            quality_scores={"complexity": 0.2, "security": 0.3},  # Low scores = high risk
        )

        risks = identify_risks(design, risk_threshold=0.5)

        assert isinstance(risks, list)
        assert all(isinstance(r, Risk) for r in risks)
        # Should have at least found complexity/security risks
        if risks:
            assert all(0.0 <= r.risk_score <= 1.0 for r in risks)

    def test_risk_mitigation_strategies(self) -> None:
        """Test risk mitigation strategy generation."""
        strategies = risk_mitigation_strategies("tight_coupling")

        assert isinstance(strategies, list)
        assert len(strategies) > 0
        assert all(isinstance(s, str) for s in strategies)

    def test_failure_mode_analysis(self) -> None:
        """Test FMEA analysis."""
        design = DesignAlternative(
            vector=np.random.randn(100),
            metadata={"components": ["api", "database"]},
        )

        fmea = failure_mode_analysis(design, components=["api", "database"])

        assert "failure_modes" in fmea
        assert "components_analyzed" in fmea
        assert "high_risk_count" in fmea
        assert fmea["components_analyzed"] == 2
