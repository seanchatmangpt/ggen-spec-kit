"""Unit tests for specification reasoning."""

from __future__ import annotations

import numpy as np

from specify_cli.hyperdimensional.specification_reasoning import (
    ConsistencyIssue,
    RefinementSuggestion,
    SpecificationGap,
    check_semantic_consistency,
    complexity_analysis,
    detect_redundancy,
    generate_edge_cases,
    identify_gaps,
    quality_metrics_impact,
    resolve_conflicts,
    specification_entropy,
    suggest_clarifications,
    suggest_improvements,
)


class TestCompletenessAnalysis:
    """Tests for specification completeness analysis."""

    def test_specification_entropy(self) -> None:
        """Test entropy calculation."""
        spec_vector = np.random.randn(100)

        entropy = specification_entropy(spec_vector)

        assert isinstance(entropy, float)
        assert entropy > 0

    def test_identify_gaps(self) -> None:
        """Test gap identification."""
        spec_vector = np.random.randn(100)
        requirements_db = {
            "security": np.random.randn(100),
            "scalability": np.random.randn(100),
        }

        gaps = identify_gaps(spec_vector, requirements_db, coverage_threshold=0.8)

        assert isinstance(gaps, list)
        assert all(isinstance(g, SpecificationGap) for g in gaps)

    def test_generate_edge_cases(self) -> None:
        """Test edge case generation."""
        spec_vector = np.random.randn(100)

        edge_cases = generate_edge_cases(spec_vector, num_cases=5)

        assert len(edge_cases) == 5
        assert all("description" in case for case in edge_cases)
        assert all("priority" in case for case in edge_cases)

    def test_suggest_clarifications(self) -> None:
        """Test clarification suggestions."""
        spec = {
            "performance": "should be fast",  # Vague
            "reliability": "maybe 99% uptime",  # Ambiguous
        }

        clarifications = suggest_clarifications(spec)

        assert isinstance(clarifications, list)
        assert len(clarifications) > 0


class TestConsistencyChecking:
    """Tests for consistency checking."""

    def test_check_semantic_consistency(self) -> None:
        """Test semantic consistency checking."""
        spec1 = {"approach": "synchronous"}
        spec2 = {"approach": "asynchronous"}

        issues = check_semantic_consistency([spec1, spec2])

        assert isinstance(issues, list)
        # Should detect contradiction
        assert len(issues) > 0
        assert all(isinstance(i, ConsistencyIssue) for i in issues)

    def test_resolve_conflicts_merge(self) -> None:
        """Test conflict resolution with merge strategy."""
        spec1 = {"feature_a": "value1"}
        spec2 = {"feature_b": "value2"}

        resolved = resolve_conflicts([spec1, spec2], resolution_strategy="merge")

        assert "feature_a" in resolved
        assert "feature_b" in resolved

    def test_detect_redundancy(self) -> None:
        """Test redundancy detection."""
        spec1 = {"feature": "authentication"}
        spec2 = {"feature": "authentication"}  # Duplicate

        redundancies = detect_redundancy([spec1, spec2])

        assert isinstance(redundancies, list)
        assert len(redundancies) > 0


class TestRefinementSuggestions:
    """Tests for refinement suggestions."""

    def test_suggest_improvements(self) -> None:
        """Test improvement suggestions."""
        spec = {
            "performance": "should be fast",  # Missing quantification
        }

        suggestions = suggest_improvements(spec)

        assert isinstance(suggestions, list)
        assert all(isinstance(s, RefinementSuggestion) for s in suggestions)

    def test_quality_metrics_impact(self) -> None:
        """Test quality metrics impact analysis."""
        spec = {"feature_a": "value1"}
        change = {"add_section": "security"}

        impact = quality_metrics_impact(spec, change)

        assert isinstance(impact, dict)
        if "completeness" in impact:
            assert 0.0 <= impact["completeness"] <= 1.0

    def test_complexity_analysis(self) -> None:
        """Test complexity analysis."""
        spec = {
            "level1": {
                "level2": {"level3": "deep nesting"},
            },
            "dependencies": "depends on A, B, C",
        }

        complexity = complexity_analysis(spec)

        assert "overall" in complexity
        assert "structural" in complexity
        assert 0.0 <= complexity["overall"] <= 1.0
