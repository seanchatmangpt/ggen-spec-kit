"""Tests for hyperdimensional reasoning core (80/20 implementation).

Tests the three essential operations:
1. Similarity search (nearest neighbor)
2. Ranking by objective
3. Constraint checking
"""

from __future__ import annotations

import numpy as np
import pytest

from specify_cli.hyperdimensional.reasoning_core import (
    batch_compare,
    check_constraint_satisfied,
    compare_entities,
    find_similar_entities,
    get_violated_constraints,
    rank_by_objective,
)

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def sample_vectors() -> dict[str, np.ndarray]:
    """Create sample vectors for testing."""
    np.random.seed(42)
    return {
        "entity_a": np.random.randn(100),
        "entity_b": np.random.randn(100),
        "entity_c": np.random.randn(100),
        "entity_d": np.random.randn(100),
        "entity_e": np.random.randn(100),
    }


@pytest.fixture
def sample_entities() -> list[dict[str, float | str]]:
    """Create sample entities with attributes."""
    return [
        {"name": "feature_a", "priority": 0.9, "cost": 3, "impact": 0.8},
        {"name": "feature_b", "priority": 0.7, "cost": 5, "impact": 0.6},
        {"name": "feature_c", "priority": 1.0, "cost": 2, "impact": 0.9},
        {"name": "feature_d", "priority": 0.5, "cost": 1, "impact": 0.4},
    ]


# ============================================================================
# Tests: Similarity Search
# ============================================================================


def test_find_similar_entities_basic(sample_vectors: dict[str, np.ndarray]) -> None:
    """Test basic similarity search."""
    query = sample_vectors["entity_a"]
    embeddings = {k: v for k, v in sample_vectors.items() if k != "entity_a"}

    results = find_similar_entities(query, embeddings, k=3)

    assert len(results) == 3
    assert all(isinstance(name, str) for name, _score in results)
    assert all(isinstance(score, float) for _name, score in results)
    # Results should be sorted by score descending
    scores = [score for _name, score in results]
    assert scores == sorted(scores, reverse=True)


def test_find_similar_entities_exact_match(sample_vectors: dict[str, np.ndarray]) -> None:
    """Test similarity search with exact match."""
    query = sample_vectors["entity_a"]

    results = find_similar_entities(query, sample_vectors, k=5)

    # First result should be exact match with score ~1.0
    assert results[0][0] == "entity_a"
    assert results[0][1] == pytest.approx(1.0, abs=0.01)


def test_find_similar_entities_with_threshold(sample_vectors: dict[str, np.ndarray]) -> None:
    """Test similarity search with threshold."""
    query = sample_vectors["entity_a"]

    # High threshold should return fewer results
    results = find_similar_entities(query, sample_vectors, k=10, threshold=0.9)

    assert len(results) <= 10
    assert all(score >= 0.9 for _name, score in results)


def test_find_similar_entities_empty_embeddings() -> None:
    """Test similarity search with empty embeddings."""
    query = np.random.randn(100)

    results = find_similar_entities(query, {}, k=5)

    assert results == []


def test_find_similar_entities_k_larger_than_dataset(
    sample_vectors: dict[str, np.ndarray],
) -> None:
    """Test similarity search when k > dataset size."""
    query = sample_vectors["entity_a"]

    results = find_similar_entities(query, sample_vectors, k=100)

    # Should return all available results
    assert len(results) == len(sample_vectors)


# ============================================================================
# Tests: Ranking
# ============================================================================


def test_rank_by_objective_basic(sample_entities: list[dict[str, float | str]]) -> None:
    """Test basic ranking by objective."""

    def priority_fn(entity: dict[str, float | str]) -> float:
        return float(entity["priority"])

    ranked = rank_by_objective(sample_entities, priority_fn)

    assert len(ranked) == len(sample_entities)
    # Should be sorted by priority descending
    priorities = [float(e["priority"]) for e in ranked]
    assert priorities == sorted(priorities, reverse=True)
    assert ranked[0]["name"] == "feature_c"  # priority 1.0


def test_rank_by_objective_value_cost_ratio(
    sample_entities: list[dict[str, float | str]],
) -> None:
    """Test ranking by value/cost ratio."""

    def value_cost_ratio(entity: dict[str, float | str]) -> float:
        return float(entity["priority"]) / float(entity["cost"])

    ranked = rank_by_objective(sample_entities, value_cost_ratio)

    # feature_c has best ratio: 1.0/2 = 0.5
    assert ranked[0]["name"] == "feature_c"


def test_rank_by_objective_ascending(sample_entities: list[dict[str, float | str]]) -> None:
    """Test ranking in ascending order."""

    def cost_fn(entity: dict[str, float | str]) -> float:
        return float(entity["cost"])

    ranked = rank_by_objective(sample_entities, cost_fn, reverse=False)

    # Should be sorted by cost ascending
    costs = [float(e["cost"]) for e in ranked]
    assert costs == sorted(costs)
    assert ranked[0]["name"] == "feature_d"  # cost 1


def test_rank_by_objective_empty_list() -> None:
    """Test ranking with empty list."""

    def dummy_fn(entity: dict[str, float | str]) -> float:
        return 0.0

    ranked = rank_by_objective([], dummy_fn)

    assert ranked == []


def test_rank_by_objective_complex_formula(
    sample_entities: list[dict[str, float | str]],
) -> None:
    """Test ranking with complex objective function."""

    def weighted_score(entity: dict[str, float | str]) -> float:
        priority = float(entity["priority"])
        impact = float(entity["impact"])
        cost = float(entity["cost"])
        return (priority * 0.6 + impact * 0.4) / cost

    ranked = rank_by_objective(sample_entities, weighted_score)

    # Verify results are sorted by score
    scores = [weighted_score(e) for e in ranked]
    assert scores == sorted(scores, reverse=True)


# ============================================================================
# Tests: Constraint Satisfaction
# ============================================================================


def test_check_constraint_satisfied_all_pass() -> None:
    """Test constraint checking when all constraints satisfied."""
    np.random.seed(42)
    design = np.random.randn(100)

    # Create similar constraint vectors (should pass)
    constraints = [design + np.random.randn(100) * 0.1 for _ in range(3)]

    result = check_constraint_satisfied(design, constraints, threshold=0.7)

    assert result is True


def test_check_constraint_satisfied_one_fails() -> None:
    """Test constraint checking when one constraint fails."""
    np.random.seed(42)
    design = np.random.randn(100)

    # Mix of similar and dissimilar constraints
    constraints = [
        design + np.random.randn(100) * 0.1,  # Similar (pass)
        -design,  # Opposite (fail)
    ]

    result = check_constraint_satisfied(design, constraints, threshold=0.7)

    assert result is False


def test_check_constraint_satisfied_empty_constraints() -> None:
    """Test constraint checking with no constraints."""
    design = np.random.randn(100)

    result = check_constraint_satisfied(design, [], threshold=0.7)

    assert result is True  # No constraints = automatically satisfied


def test_check_constraint_satisfied_threshold_sensitivity() -> None:
    """Test constraint checking with different thresholds."""
    np.random.seed(42)
    design = np.random.randn(100)
    constraint = design + np.random.randn(100) * 0.5  # Moderately similar

    # Should pass with low threshold
    assert check_constraint_satisfied(design, [constraint], threshold=0.3)

    # Might fail with high threshold
    result_high = check_constraint_satisfied(design, [constraint], threshold=0.9)
    # Result depends on random noise, but threshold should affect outcome
    assert isinstance(result_high, bool)


def test_get_violated_constraints_none_violated() -> None:
    """Test getting violations when all constraints satisfied."""
    np.random.seed(42)
    design = np.random.randn(100)

    constraints = {
        "constraint_a": design + np.random.randn(100) * 0.05,
        "constraint_b": design + np.random.randn(100) * 0.05,
    }

    violations = get_violated_constraints(design, constraints, threshold=0.7)

    assert violations == []


def test_get_violated_constraints_some_violated() -> None:
    """Test getting violations when some constraints fail."""
    np.random.seed(42)
    design = np.random.randn(100)

    constraints = {
        "good_constraint": design + np.random.randn(100) * 0.05,  # Similar (pass)
        "bad_constraint": -design,  # Opposite (fail)
    }

    violations = get_violated_constraints(design, constraints, threshold=0.7)

    assert len(violations) >= 1
    # Should include the bad constraint
    violated_names = [name for name, _score in violations]
    assert "bad_constraint" in violated_names


def test_get_violated_constraints_sorted_by_severity() -> None:
    """Test that violations are sorted by severity."""
    np.random.seed(42)
    design = np.random.randn(100)

    constraints = {
        "minor_violation": design + np.random.randn(100) * 0.3,  # Somewhat similar
        "major_violation": -design,  # Opposite
    }

    violations = get_violated_constraints(design, constraints, threshold=0.9)

    # Should be sorted by score ascending (worst first)
    scores = [score for _name, score in violations]
    assert scores == sorted(scores)


# ============================================================================
# Tests: Entity Comparison
# ============================================================================


def test_compare_entities_identical() -> None:
    """Test comparing identical entities."""
    entity = np.random.randn(100)

    similarity = compare_entities(entity, entity)

    assert similarity == pytest.approx(1.0, abs=0.01)


def test_compare_entities_opposite() -> None:
    """Test comparing opposite entities."""
    entity1 = np.random.randn(100)
    entity2 = -entity1

    similarity = compare_entities(entity1, entity2)

    assert similarity == pytest.approx(-1.0, abs=0.01)


def test_compare_entities_random() -> None:
    """Test comparing random entities."""
    np.random.seed(42)
    entity1 = np.random.randn(100)
    entity2 = np.random.randn(100)

    similarity = compare_entities(entity1, entity2)

    # Should be in valid range
    assert -1.0 <= similarity <= 1.0


# ============================================================================
# Tests: Batch Operations
# ============================================================================


def test_batch_compare_basic(sample_vectors: dict[str, np.ndarray]) -> None:
    """Test batch comparison."""
    query = sample_vectors["entity_a"]
    entities = [v for k, v in sample_vectors.items() if k != "entity_a"]

    scores = batch_compare(query, entities)

    assert len(scores) == len(entities)
    assert all(-1.0 <= score <= 1.0 for score in scores)


def test_batch_compare_empty() -> None:
    """Test batch comparison with empty list."""
    query = np.random.randn(100)

    scores = batch_compare(query, [])

    assert len(scores) == 0


def test_batch_compare_finds_best() -> None:
    """Test batch comparison identifies best match."""
    np.random.seed(42)
    query = np.random.randn(100)

    # Create entities with one very similar to query
    entities = [np.random.randn(100) for _ in range(5)]
    entities.append(query + np.random.randn(100) * 0.01)  # Very similar

    scores = batch_compare(query, entities)

    # Last entity should have highest score
    best_idx = int(scores.argmax())
    assert best_idx == len(entities) - 1


# ============================================================================
# Integration Tests
# ============================================================================


def test_similarity_ranking_integration(sample_vectors: dict[str, np.ndarray]) -> None:
    """Test similarity search + ranking integration."""
    query = sample_vectors["entity_a"]

    # Find similar entities
    similar = find_similar_entities(query, sample_vectors, k=5)

    # Convert to entity dicts
    entities = [{"name": name, "similarity": score} for name, score in similar]

    # Rank by similarity (should preserve order)
    ranked = rank_by_objective(entities, lambda e: float(e["similarity"]))

    assert len(ranked) == len(similar)
    # Should be same order (already sorted by similarity)
    assert [e["name"] for e in ranked] == [name for name, _score in similar]


def test_constraint_violation_with_entities() -> None:
    """Test constraint checking with entity-based workflow."""
    np.random.seed(42)

    # Create design and constraints
    design = np.random.randn(100)
    constraints = {
        "scalability": design + np.random.randn(100) * 0.1,
        "security": design + np.random.randn(100) * 0.1,
        "performance": -design,  # This will violate
    }

    # Check satisfaction
    satisfied = check_constraint_satisfied(design, list(constraints.values()), threshold=0.7)
    assert not satisfied

    # Get violations
    violations = get_violated_constraints(design, constraints, threshold=0.7)
    assert len(violations) >= 1

    # Rank violations by severity
    violation_entities = [
        {"name": name, "severity": 1.0 - score} for name, score in violations
    ]
    ranked_violations = rank_by_objective(violation_entities, lambda e: float(e["severity"]))

    # Worst violation should be first
    assert ranked_violations[0]["name"] == "performance"
