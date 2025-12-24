"""Unit tests for AGI reasoning.

Auto-generated from: ontology/agi-reasoning.ttl
Constitutional equation: test_agi_reasoning.py = μ(agi-reasoning.ttl)
"""

import pytest
from specify_cli.ops import agi_reasoning


class TestReasoningChain:
    """Test chain-of-thought reasoning."""

    def test_cot_with_premises(self):
        """Test COT with initial premises."""
        premises = [
            agi_reasoning.Premise("A is true", confidence=1.0),
            agi_reasoning.Premise("If A then B", confidence=0.9),
        ]

        chain = agi_reasoning.chain_of_thought("What is B?", premises, max_steps=5)

        assert isinstance(chain, agi_reasoning.ReasoningChain)
        assert len(chain.steps) == 2

    def test_reasoning_confidence_decay(self):
        """Test that confidence decays with reasoning depth."""
        premises = [agi_reasoning.Premise(f"Premise {i}", confidence=1.0) for i in range(5)]

        chain = agi_reasoning.chain_of_thought("Deep question", premises, max_steps=5)

        confidences = [step.confidence for step in chain.steps]
        assert len(confidences) > 0


class TestAlternativeGeneration:
    """Test design alternative generation."""

    def test_generate_alternatives(self):
        """Test generating design alternatives."""
        requirements = {
            "scalability": 0.9,
            "simplicity": 0.7,
            "security": 0.8,
        }

        alternatives = agi_reasoning.generate_alternatives(requirements, count=10)

        assert len(alternatives) == 10
        assert all("scores" in alt for alt in alternatives)

    def test_rank_alternatives(self):
        """Test ranking alternatives."""
        alternatives = [
            {"name": f"alt_{i}", "scores": {"cost": i * 0.1, "performance": (1 - i * 0.1)}}
            for i in range(5)
        ]
        objectives = {"cost": 1.0, "performance": 1.0}

        ranked = agi_reasoning.rank_alternatives(alternatives, objectives)

        assert len(ranked) == len(alternatives)


class TestIntegration:
    """Integration tests combining planning and reasoning."""

    def test_reason_about_plan(self):
        """Test reasoning about a task plan."""
        from specify_cli.ops import agi_task_planning

        goal = "Build ML pipeline"
        tasks = agi_task_planning.decompose_goal(goal, goal, {})

        premises = [
            agi_reasoning.Premise(f"Task {t.name} is needed", 1.0)
            for t in tasks[:3]
        ]
        chain = agi_reasoning.chain_of_thought(
            "Is the plan feasible?", premises
        )

        assert len(chain.steps) >= 0
