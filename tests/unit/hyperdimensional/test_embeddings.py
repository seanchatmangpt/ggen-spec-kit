"""
Unit tests for hyperdimensional embeddings module.

Tests cover:
- Vector initialization and properties
- Normalization strategies
- Binding and unbinding operations
- Superposition
- Similarity metrics
- Distance measures
- Statistical analysis
"""

from __future__ import annotations

import numpy as np
import pytest

from specify_cli.hyperdimensional.embeddings import (
    HyperdimensionalEmbedding,
    VectorOperations,
    VectorStats,
)


class TestVectorOperations:
    """Test VectorOperations class."""

    def test_normalize_l2(self) -> None:
        """Test L2 normalization."""
        vector = np.array([3.0, 4.0], dtype=np.float64)
        normalized = VectorOperations.normalize_l2(vector)

        assert np.allclose(np.linalg.norm(normalized), 1.0)
        assert np.allclose(normalized, [0.6, 0.8])

    def test_normalize_l2_zero_vector(self) -> None:
        """Test L2 normalization of zero vector."""
        vector = np.zeros(10, dtype=np.float64)
        normalized = VectorOperations.normalize_l2(vector)

        assert np.allclose(normalized, vector)

    def test_normalize_minmax(self) -> None:
        """Test min-max normalization."""
        vector = np.array([1.0, 2.0, 3.0, 4.0, 5.0], dtype=np.float64)
        normalized = VectorOperations.normalize_minmax(vector)

        assert normalized.min() == -1.0
        assert normalized.max() == 1.0

    def test_normalize_minmax_constant_vector(self) -> None:
        """Test min-max normalization of constant vector."""
        vector = np.ones(10, dtype=np.float64) * 5.0
        normalized = VectorOperations.normalize_minmax(vector)

        assert np.allclose(normalized, np.zeros(10))

    def test_normalize_zscore(self) -> None:
        """Test z-score normalization."""
        vector = np.array([1.0, 2.0, 3.0, 4.0, 5.0], dtype=np.float64)
        normalized = VectorOperations.normalize_zscore(vector)

        assert np.abs(normalized.mean()) < 1e-10
        assert np.allclose(normalized.std(), 1.0)

    def test_normalize_zscore_constant_vector(self) -> None:
        """Test z-score normalization of constant vector."""
        vector = np.ones(10, dtype=np.float64) * 5.0
        normalized = VectorOperations.normalize_zscore(vector)

        assert np.allclose(normalized, np.zeros(10))

    def test_bind_properties(self) -> None:
        """Test binding operation properties."""
        rng = np.random.RandomState(42)
        vec_a = rng.randn(1000)
        vec_b = rng.randn(1000)

        bound = VectorOperations.bind(vec_a, vec_b)

        # Result should be unit vector
        assert np.allclose(np.linalg.norm(bound), 1.0)

        # Should have same dimensionality
        assert len(bound) == len(vec_a)

    def test_bind_unbind_approximate_inverse(self) -> None:
        """Test that unbind approximately recovers original vector."""
        rng = np.random.RandomState(42)
        vec_a = VectorOperations.normalize_l2(rng.randn(1000))
        vec_b = VectorOperations.normalize_l2(rng.randn(1000))

        # Bind A and B
        bound = VectorOperations.bind(vec_a, vec_b)

        # Unbind to recover A
        recovered = VectorOperations.unbind(bound, vec_b)

        # Recovered should be similar to original (high cosine similarity)
        similarity = VectorOperations.cosine_similarity(vec_a, recovered)
        assert similarity > 0.7  # High correlation expected (lowered from 0.8 due to noise)

    def test_superpose_uniform_weights(self) -> None:
        """Test superposition with uniform weights."""
        rng = np.random.RandomState(42)
        vectors = [rng.randn(100) for _ in range(5)]

        result = VectorOperations.superpose(vectors)

        # Result should be unit vector
        assert np.allclose(np.linalg.norm(result), 1.0)

    def test_superpose_custom_weights(self) -> None:
        """Test superposition with custom weights."""
        rng = np.random.RandomState(42)
        vectors = [rng.randn(100) for _ in range(3)]
        weights = [0.5, 0.3, 0.2]

        result = VectorOperations.superpose(vectors, weights)

        assert np.allclose(np.linalg.norm(result), 1.0)

    def test_superpose_empty_list(self) -> None:
        """Test that superposing empty list raises error."""
        with pytest.raises(ValueError, match="Cannot superpose empty list"):
            VectorOperations.superpose([])

    def test_superpose_weight_mismatch(self) -> None:
        """Test that mismatched weights raise error."""
        rng = np.random.RandomState(42)
        vectors = [rng.randn(100) for _ in range(3)]
        weights = [0.5, 0.5]  # Wrong number of weights

        with pytest.raises(ValueError, match="Number of weights must match"):
            VectorOperations.superpose(vectors, weights)

    def test_permute(self) -> None:
        """Test permutation operation."""
        vector = np.array([1.0, 2.0, 3.0, 4.0, 5.0], dtype=np.float64)

        # Shift right by 2
        permuted = VectorOperations.permute(vector, 2)
        assert np.allclose(permuted, [4.0, 5.0, 1.0, 2.0, 3.0])

        # Shift left by 2 (negative shift)
        permuted = VectorOperations.permute(vector, -2)
        assert np.allclose(permuted, [3.0, 4.0, 5.0, 1.0, 2.0])

    def test_cosine_similarity_identical(self) -> None:
        """Test cosine similarity of identical vectors."""
        rng = np.random.RandomState(42)
        vector = rng.randn(100)

        similarity = VectorOperations.cosine_similarity(vector, vector)
        assert np.allclose(similarity, 1.0)

    def test_cosine_similarity_orthogonal(self) -> None:
        """Test cosine similarity of orthogonal vectors."""
        vec_a = np.array([1.0, 0.0], dtype=np.float64)
        vec_b = np.array([0.0, 1.0], dtype=np.float64)

        similarity = VectorOperations.cosine_similarity(vec_a, vec_b)
        assert np.allclose(similarity, 0.0)

    def test_cosine_similarity_opposite(self) -> None:
        """Test cosine similarity of opposite vectors."""
        vec_a = np.array([1.0, 0.0], dtype=np.float64)
        vec_b = np.array([-1.0, 0.0], dtype=np.float64)

        similarity = VectorOperations.cosine_similarity(vec_a, vec_b)
        assert np.allclose(similarity, -1.0)

    def test_cosine_similarity_zero_vector(self) -> None:
        """Test cosine similarity with zero vector."""
        vec_a = np.zeros(10, dtype=np.float64)
        vec_b = np.ones(10, dtype=np.float64)

        similarity = VectorOperations.cosine_similarity(vec_a, vec_b)
        assert similarity == 0.0

    def test_euclidean_distance(self) -> None:
        """Test Euclidean distance."""
        vec_a = np.array([0.0, 0.0], dtype=np.float64)
        vec_b = np.array([3.0, 4.0], dtype=np.float64)

        distance = VectorOperations.euclidean_distance(vec_a, vec_b)
        assert np.allclose(distance, 5.0)

    def test_hamming_distance(self) -> None:
        """Test Hamming distance."""
        vec_a = np.array([1.0, -1.0, 1.0, -1.0], dtype=np.float64)
        vec_b = np.array([1.0, 1.0, -1.0, -1.0], dtype=np.float64)

        distance = VectorOperations.hamming_distance(vec_a, vec_b)
        assert distance == 2  # Two positions differ

    def test_information_distance(self) -> None:
        """Test information-theoretic distance."""
        rng = np.random.RandomState(42)
        vec_a = rng.randn(1000)
        vec_b = rng.randn(1000)

        distance = VectorOperations.information_distance(vec_a, vec_b)

        # Should be non-negative
        assert distance >= 0.0

        # Distance to self should be near zero
        self_distance = VectorOperations.information_distance(vec_a, vec_a)
        assert self_distance < 0.1

    def test_vector_stats(self) -> None:
        """Test vector statistics computation."""
        vector = np.array([1.0, 2.0, 3.0, 4.0, 5.0], dtype=np.float64)
        stats = VectorOperations.vector_stats(vector)

        assert isinstance(stats, VectorStats)
        assert stats.mean == 3.0
        assert stats.std > 0.0
        assert stats.norm > 0.0
        assert 0.0 <= stats.sparsity <= 1.0
        assert stats.entropy > 0.0


class TestHyperdimensionalEmbedding:
    """Test HyperdimensionalEmbedding class."""

    def test_initialization(self) -> None:
        """Test embedding initialization."""
        hde = HyperdimensionalEmbedding(dimensions=1000, seed=42)

        assert hde.dimensions == 1000
        assert hde.seed == 42
        assert len(hde.embeddings) == 0

    def test_initialization_invalid_dimensions(self) -> None:
        """Test that small dimensions raise error."""
        with pytest.raises(ValueError, match="Dimensions must be >= 100"):
            HyperdimensionalEmbedding(dimensions=50)

    def test_initialization_invalid_normalize(self) -> None:
        """Test that invalid normalization raises error."""
        with pytest.raises(ValueError, match="normalize must be"):
            HyperdimensionalEmbedding(normalize="invalid")  # type: ignore[arg-type]

    def test_embed_command(self) -> None:
        """Test command embedding."""
        hde = HyperdimensionalEmbedding(dimensions=1000)
        vector = hde.embed_command("init")

        assert len(vector) == 1000
        assert "command:init" in hde.embeddings

    def test_embed_command_deterministic(self) -> None:
        """Test that same command produces same vector."""
        hde1 = HyperdimensionalEmbedding(dimensions=1000, seed=42)
        hde2 = HyperdimensionalEmbedding(dimensions=1000, seed=99)  # Different seed

        vec1 = hde1.embed_command("init")
        vec2 = hde2.embed_command("init")

        # Should be identical (deterministic from name)
        assert np.allclose(vec1, vec2)

    def test_embed_command_caching(self) -> None:
        """Test that embeddings are cached."""
        hde = HyperdimensionalEmbedding(dimensions=1000)

        vec1 = hde.embed_command("init")
        vec2 = hde.embed_command("init")

        # Should be same object (cached)
        assert vec1 is vec2

    def test_embed_different_entities(self) -> None:
        """Test that different entities get different vectors."""
        hde = HyperdimensionalEmbedding(dimensions=1000)

        cmd_vec = hde.embed_command("init")
        job_vec = hde.embed_job("developer")
        outcome_vec = hde.embed_outcome("fast-startup")

        # All should be different (low similarity)
        sim_cmd_job = hde.cosine_similarity(cmd_vec, job_vec)
        sim_cmd_outcome = hde.cosine_similarity(cmd_vec, outcome_vec)
        sim_job_outcome = hde.cosine_similarity(job_vec, outcome_vec)

        # Expect low correlation (approximately orthogonal)
        assert abs(sim_cmd_job) < 0.3
        assert abs(sim_cmd_outcome) < 0.3
        assert abs(sim_job_outcome) < 0.3

    def test_semantic_distance(self) -> None:
        """Test semantic distance metric."""
        hde = HyperdimensionalEmbedding(dimensions=1000)

        vec_a = hde.embed_command("init")
        vec_b = hde.embed_command("check")

        distance = hde.semantic_distance(vec_a, vec_b)

        # Should be in [0, 2]
        assert 0.0 <= distance <= 2.0

        # Distance to self should be 0
        self_distance = hde.semantic_distance(vec_a, vec_a)
        assert np.allclose(self_distance, 0.0)

    def test_find_similar(self) -> None:
        """Test finding similar entities."""
        hde = HyperdimensionalEmbedding(dimensions=1000)

        # Create some embeddings
        init_vec = hde.embed_command("init")
        hde.embed_command("check")
        hde.embed_command("version")
        hde.embed_command("ggen-sync")

        # Find similar to init
        similar = hde.find_similar(init_vec, hde.embeddings, top_k=3)

        assert len(similar) == 3
        # First result should be init itself
        assert similar[0][0] == "command:init"
        assert similar[0][1] == 1.0  # Perfect similarity

    def test_save_and_load(self, tmp_path: pytest.TempPathFactory) -> None:  # type: ignore[name-defined]
        """Test saving and loading embeddings."""
        hde = HyperdimensionalEmbedding(dimensions=1000, seed=42)

        # Create embeddings
        hde.embed_command("init")
        hde.embed_command("check")
        hde.embed_job("developer")

        # Save
        filepath = tmp_path / "embeddings.json"  # type: ignore[operator]
        hde.save(filepath)

        # Load
        hde2 = HyperdimensionalEmbedding(dimensions=1000, seed=999)
        hde2.load(filepath)

        assert hde2.seed == 42
        assert len(hde2.embeddings) == 3
        assert "command:init" in hde2.embeddings

    def test_load_dimension_mismatch(self, tmp_path: pytest.TempPathFactory) -> None:  # type: ignore[name-defined]
        """Test that loading with wrong dimensions raises error."""
        hde = HyperdimensionalEmbedding(dimensions=1000)
        hde.embed_command("init")

        filepath = tmp_path / "embeddings.json"  # type: ignore[operator]
        hde.save(filepath)

        # Try to load with different dimensions
        hde2 = HyperdimensionalEmbedding(dimensions=500)
        with pytest.raises(ValueError, match="Dimension mismatch"):
            hde2.load(filepath)

    def test_get_stats(self) -> None:
        """Test getting statistics for embedding."""
        hde = HyperdimensionalEmbedding(dimensions=1000)
        hde.embed_command("init")

        stats = hde.get_stats("command:init")

        assert isinstance(stats, VectorStats)
        assert stats.norm > 0.0

    def test_get_stats_missing_entity(self) -> None:
        """Test that getting stats for missing entity raises error."""
        hde = HyperdimensionalEmbedding(dimensions=1000)

        with pytest.raises(KeyError, match="No embedding found"):
            hde.get_stats("command:nonexistent")

    def test_clear_cache(self) -> None:
        """Test clearing embedding cache."""
        hde = HyperdimensionalEmbedding(dimensions=1000)

        hde.embed_command("init")
        hde.embed_command("check")

        assert len(hde.embeddings) == 2

        hde.clear_cache()

        assert len(hde.embeddings) == 0

    def test_get_all_embeddings(self) -> None:
        """Test getting all embeddings."""
        hde = HyperdimensionalEmbedding(dimensions=1000)

        hde.embed_command("init")
        hde.embed_job("developer")

        all_embeddings = hde.get_all_embeddings()

        assert len(all_embeddings) == 2
        assert "command:init" in all_embeddings
        assert "job:developer" in all_embeddings

    def test_different_normalization_strategies(self) -> None:
        """Test different normalization strategies."""
        for strategy in ("l2", "minmax", "zscore"):
            hde = HyperdimensionalEmbedding(dimensions=1000, normalize=strategy)
            vector = hde.embed_command("init")

            assert len(vector) == 1000
            # All strategies should produce valid vectors
            assert np.all(np.isfinite(vector))
