"""Unit tests for hyperdimensional reasoning engine."""

from __future__ import annotations

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal

from specify_cli.hyperdimensional.reasoning import (
    QueryExpansionResult,
    RelationshipChain,
    analogy_reasoning,
    bind_vectors,
    check_constraint_satisfaction,
    concept_refinement,
    conflict_detection,
    consistency_checking,
    constraint_relaxation,
    cosine_similarity,
    create_random_vector,
    encode_concept,
    expand_query,
    normalize_vector,
    permute_vector,
    relationship_chaining,
    unbind_vectors,
    vector_and,
    vector_distance,
    vector_implies,
    vector_not,
    vector_or,
)

# ============================================================================
# Vector Operations Tests
# ============================================================================


class TestVectorOperations:
    """Tests for basic vector operations."""

    def test_normalize_vector(self) -> None:
        """Test vector normalization."""
        vec = np.array([3.0, 4.0])
        normalized = normalize_vector(vec)

        assert_allclose(np.linalg.norm(normalized), 1.0)
        assert_allclose(normalized, np.array([0.6, 0.8]))

    def test_normalize_zero_vector(self) -> None:
        """Test normalization of near-zero vector."""
        vec = np.array([1e-12, 1e-12])
        normalized = normalize_vector(vec)

        # Should return original vector when norm is near zero
        assert_array_equal(normalized, vec)

    def test_cosine_similarity_identical(self) -> None:
        """Test cosine similarity of identical vectors."""
        v1 = np.array([1.0, 2.0, 3.0])
        v2 = np.array([1.0, 2.0, 3.0])

        similarity = cosine_similarity(v1, v2)
        assert_allclose(similarity, 1.0)

    def test_cosine_similarity_orthogonal(self) -> None:
        """Test cosine similarity of orthogonal vectors."""
        v1 = np.array([1.0, 0.0])
        v2 = np.array([0.0, 1.0])

        similarity = cosine_similarity(v1, v2)
        assert_allclose(similarity, 0.0, atol=1e-10)

    def test_cosine_similarity_opposite(self) -> None:
        """Test cosine similarity of opposite vectors."""
        v1 = np.array([1.0, 0.0])
        v2 = np.array([-1.0, 0.0])

        similarity = cosine_similarity(v1, v2)
        assert_allclose(similarity, -1.0)

    def test_vector_distance_cosine(self) -> None:
        """Test cosine distance calculation."""
        v1 = np.array([1.0, 0.0])
        v2 = np.array([1.0, 0.0])

        distance = vector_distance(v1, v2, metric="cosine")
        assert_allclose(distance, 0.0)

    def test_vector_distance_euclidean(self) -> None:
        """Test Euclidean distance calculation."""
        v1 = np.array([0.0, 0.0])
        v2 = np.array([3.0, 4.0])

        distance = vector_distance(v1, v2, metric="euclidean")
        assert_allclose(distance, 5.0)

    def test_vector_distance_manhattan(self) -> None:
        """Test Manhattan distance calculation."""
        v1 = np.array([0.0, 0.0])
        v2 = np.array([3.0, 4.0])

        distance = vector_distance(v1, v2, metric="manhattan")
        assert_allclose(distance, 7.0)

    def test_vector_distance_invalid_metric(self) -> None:
        """Test invalid metric raises error."""
        v1 = np.array([1.0, 0.0])
        v2 = np.array([0.0, 1.0])

        with pytest.raises(ValueError, match="Unsupported distance metric"):
            vector_distance(v1, v2, metric="invalid")


# ============================================================================
# Query Expansion Tests
# ============================================================================


class TestQueryExpansion:
    """Tests for query expansion functionality."""

    def test_expand_query_basic(self) -> None:
        """Test basic query expansion."""
        query = np.random.randn(100)
        database = [np.random.randn(100) for _ in range(50)]

        result = expand_query(query, database, k=5)

        assert isinstance(result, QueryExpansionResult)
        assert len(result.similar_vectors) == 5
        assert len(result.similarities) == 5
        assert len(result.indices) == 5

    def test_expand_query_empty_database(self) -> None:
        """Test query expansion with empty database."""
        query = np.random.randn(100)
        database: list[np.ndarray] = []

        result = expand_query(query, database, k=5)

        assert len(result.similar_vectors) == 0
        assert len(result.similarities) == 0

    def test_expand_query_with_threshold(self) -> None:
        """Test query expansion with similarity threshold."""
        query = np.ones(100)
        # Create database with varying similarities
        database = [
            query + np.random.randn(100) * 0.1,  # High similarity
            np.random.randn(100),  # Low similarity
        ]

        result = expand_query(query, database, k=10, threshold=0.8)

        # Should only return high similarity results
        assert len(result.similar_vectors) <= 1
        assert all(s >= 0.8 for s in result.similarities)

    def test_analogy_reasoning(self) -> None:
        """Test analogy-based reasoning (A:B :: C:D)."""
        # Create simple analogy: man:woman :: king:queen
        man = np.array([1.0, 0.0])
        woman = np.array([0.0, 1.0])
        king = np.array([2.0, 0.0])

        queen_pred = analogy_reasoning(man, woman, king)

        # queen should be close to [1.0, 1.0] normalized
        expected = normalize_vector(np.array([1.0, 1.0]))
        assert cosine_similarity(queen_pred, expected) > 0.9

    def test_relationship_chaining(self) -> None:
        """Test relationship chaining."""
        concept1 = np.random.randn(100)
        relation = np.random.randn(100)
        concept2 = np.random.randn(100)
        database = [np.random.randn(100) for _ in range(20)]

        chain = relationship_chaining(concept1, relation, concept2, database, max_depth=3)

        assert isinstance(chain, RelationshipChain)
        assert len(chain.concepts) >= 1
        assert len(chain.concepts) <= 4  # max_depth + 1

    def test_concept_refinement(self) -> None:
        """Test concept refinement."""
        broad_query = np.random.randn(100)
        database = [np.random.randn(100) for _ in range(50)]

        refined = concept_refinement(broad_query, database, num_refinements=5)

        assert len(refined) <= 5
        # First element should be the original query
        assert_array_equal(refined[0], broad_query)


# ============================================================================
# Logical Operations Tests
# ============================================================================


class TestLogicalOperations:
    """Tests for logical operations in vector space."""

    def test_vector_and_average(self) -> None:
        """Test vector AND using average method."""
        v1 = np.array([1.0, 0.0])
        v2 = np.array([0.0, 1.0])

        result = vector_and(v1, v2, method="average")

        # Should be normalized average
        expected = normalize_vector(np.array([0.5, 0.5]))
        assert_allclose(result, expected, atol=0.1)

    def test_vector_or_max(self) -> None:
        """Test vector OR using max method."""
        v1 = np.array([1.0, 0.0])
        v2 = np.array([0.0, 1.0])

        result = vector_or(v1, v2, method="max")

        # Should have both components
        assert result[0] > 0
        assert result[1] > 0

    def test_vector_not(self) -> None:
        """Test vector NOT operation."""
        vec = np.array([1.0, 0.0])

        result = vector_not(vec)

        # Should be opposite direction
        assert cosine_similarity(vec, result) < 0

    def test_vector_implies(self) -> None:
        """Test vector IF-THEN operation."""
        v_if = np.array([1.0, 0.0])
        v_then = np.array([0.0, 1.0])

        implication, confidence = vector_implies(v_if, v_then, strength=0.8)

        # Should be between if and then
        assert cosine_similarity(implication, v_if) > 0
        assert cosine_similarity(implication, v_then) > 0
        assert 0.0 <= confidence <= 1.0


# ============================================================================
# Constraint Satisfaction Tests
# ============================================================================


class TestConstraintSatisfaction:
    """Tests for constraint satisfaction."""

    def test_check_constraint_satisfaction_requires(self) -> None:
        """Test requires constraint."""
        design = {"architecture": "microservices", "gateway": "api_gateway"}
        constraints = [{"type": "requires", "if": "microservices", "then": "api_gateway"}]

        satisfied, violations = check_constraint_satisfaction(design, constraints)

        assert satisfied is True
        assert len(violations) == 0

    def test_check_constraint_violation_requires(self) -> None:
        """Test requires constraint violation."""
        design = {"architecture": "microservices"}  # Missing api_gateway in values
        constraints = [{"type": "requires", "if": "microservices", "then": "api_gateway"}]

        satisfied, violations = check_constraint_satisfaction(design, constraints)

        assert satisfied is False
        assert len(violations) == 1
        assert violations[0].constraint["type"] == "requires"

    def test_check_constraint_excludes(self) -> None:
        """Test excludes constraint."""
        design = {"architecture": "microservices", "state": "global_state"}
        constraints = [{"type": "excludes", "element": "global_state"}]

        satisfied, violations = check_constraint_satisfaction(design, constraints)

        assert satisfied is False
        assert len(violations) == 1

    def test_constraint_relaxation(self) -> None:
        """Test constraint relaxation."""
        design = {"architecture": "microservices"}
        constraints = [{"type": "requires", "if": "microservices", "then": "api_gateway"}]

        relaxed, changes = constraint_relaxation(design, constraints)

        assert "api_gateway" in str(relaxed.values())
        assert len(changes) > 0

    def test_conflict_detection(self) -> None:
        """Test conflict detection between specifications."""
        spec1 = {"consistency": "strong"}
        spec2 = {"consistency": "eventual"}

        conflicts = conflict_detection([spec1, spec2])

        assert len(conflicts) > 0

    def test_consistency_checking(self) -> None:
        """Test logical consistency checking."""
        rules = [
            {"if": "A", "then": "B"},
            {"if": "B", "then": "NOT A"},  # Creates contradiction
        ]

        inconsistencies = consistency_checking(rules)

        # Should detect circular contradiction
        assert len(inconsistencies) > 0


# ============================================================================
# Utility Functions Tests
# ============================================================================


class TestUtilityFunctions:
    """Tests for utility functions."""

    def test_create_random_vector(self) -> None:
        """Test random vector creation."""
        vec = create_random_vector(dimensions=100, seed=42)

        assert vec.shape == (100,)
        assert_allclose(np.linalg.norm(vec), 1.0)

    def test_create_random_vector_reproducible(self) -> None:
        """Test random vector reproducibility with seed."""
        vec1 = create_random_vector(dimensions=100, seed=42)
        vec2 = create_random_vector(dimensions=100, seed=42)

        assert_array_equal(vec1, vec2)

    def test_encode_concept_consistency(self) -> None:
        """Test concept encoding consistency."""
        vec1 = encode_concept("microservices", dimensions=100)
        vec2 = encode_concept("microservices", dimensions=100)

        assert_array_equal(vec1, vec2)

    def test_encode_concept_different_concepts(self) -> None:
        """Test different concepts have different vectors."""
        vec1 = encode_concept("microservices", dimensions=100)
        vec2 = encode_concept("monolith", dimensions=100)

        # Should be different (very low similarity expected)
        similarity = cosine_similarity(vec1, vec2)
        assert abs(similarity) < 0.5  # Not too similar by chance

    def test_bind_unbind_vectors(self) -> None:
        """Test binding and unbinding vectors."""
        v1 = create_random_vector(100, seed=1)
        v2 = create_random_vector(100, seed=2)

        bound = bind_vectors(v1, v2, method="circular_convolution")
        retrieved = unbind_vectors(bound, v1, method="circular_convolution")

        # Retrieved should be similar to v2 (but not exact due to noise)
        similarity = cosine_similarity(retrieved, v2)
        assert similarity > 0.5  # Should have reasonable similarity

    def test_permute_vector(self) -> None:
        """Test vector permutation."""
        vec = np.array([1, 2, 3, 4, 5])

        permuted = permute_vector(vec, shift=2)

        expected = np.array([4, 5, 1, 2, 3])
        assert_array_equal(permuted, expected)
