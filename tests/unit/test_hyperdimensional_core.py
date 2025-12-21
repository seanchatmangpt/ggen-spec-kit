"""
tests.unit.test_hyperdimensional_core
--------------------------------------
Comprehensive tests for minimal hyperdimensional embeddings system.

Test Coverage:
- Vector creation and dimensionality
- Determinism (same name → same vector)
- Similarity metrics correctness
- Manhattan distance computation
- Edge cases (empty strings, special chars, unicode)
- JSON serialization/deserialization
- Cache operations
- Pre-computed embeddings
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import numpy as np
import pytest

from specify_cli.hyperdimensional.core import (
    DEFAULT_DIMENSIONS,
    EmbeddingCache,
    HyperdimensionalVector,
    cosine_similarity,
    embed_entity,
    manhattan_distance,
    precompute_speckit_embeddings,
)


class TestEmbedEntity:
    """Test embed_entity function."""

    def test_creates_vector_with_correct_dimensions(self) -> None:
        """Vector has correct dimensionality."""
        vec = embed_entity("command:init")
        assert vec.dimensions == DEFAULT_DIMENSIONS
        assert len(vec.data) == DEFAULT_DIMENSIONS

    def test_creates_vector_with_custom_dimensions(self) -> None:
        """Vector respects custom dimensions parameter."""
        vec = embed_entity("command:init", dimensions=500)
        assert vec.dimensions == 500
        assert len(vec.data) == 500

    def test_determinism_same_name_same_vector(self) -> None:
        """Same entity name produces identical vector every time."""
        vec1 = embed_entity("command:init")
        vec2 = embed_entity("command:init")

        # Must be identical
        assert vec1.name == vec2.name
        assert vec1.dimensions == vec2.dimensions
        np.testing.assert_array_equal(vec1.data, vec2.data)

    def test_different_names_different_vectors(self) -> None:
        """Different entity names produce different vectors."""
        vec1 = embed_entity("command:init")
        vec2 = embed_entity("command:check")

        # Must be different
        assert vec1.name != vec2.name
        assert not np.array_equal(vec1.data, vec2.data)

    def test_vector_is_normalized(self) -> None:
        """Vector is L2-normalized (unit length)."""
        vec = embed_entity("command:init")
        norm = np.linalg.norm(vec.data)

        # Should be very close to 1.0
        assert abs(norm - 1.0) < 1e-10

    def test_handles_empty_string(self) -> None:
        """Can create embedding for empty string."""
        vec = embed_entity("")
        assert vec.name == ""
        assert vec.dimensions == DEFAULT_DIMENSIONS
        assert len(vec.data) == DEFAULT_DIMENSIONS

    def test_handles_special_characters(self) -> None:
        """Handles entity names with special characters."""
        vec = embed_entity("command:pm-discover")
        assert vec.name == "command:pm-discover"
        assert vec.dimensions == DEFAULT_DIMENSIONS

        vec2 = embed_entity("outcome:fast-startup")
        assert vec2.name == "outcome:fast-startup"

    def test_handles_unicode(self) -> None:
        """Handles unicode characters in entity names."""
        vec = embed_entity("job:developer-🚀")
        assert vec.name == "job:developer-🚀"
        assert vec.dimensions == DEFAULT_DIMENSIONS

    def test_handles_long_names(self) -> None:
        """Handles very long entity names."""
        long_name = "command:" + "x" * 1000
        vec = embed_entity(long_name)
        assert vec.name == long_name
        assert vec.dimensions == DEFAULT_DIMENSIONS


class TestCosineSimilarity:
    """Test cosine_similarity function."""

    def test_identical_vectors_similarity_one(self) -> None:
        """Identical vectors have similarity 1.0."""
        vec = embed_entity("command:init")
        similarity = cosine_similarity(vec.data, vec.data)
        assert abs(similarity - 1.0) < 1e-10

    def test_similarity_in_valid_range(self) -> None:
        """Similarity is always in [-1, 1]."""
        vec1 = embed_entity("command:init")
        vec2 = embed_entity("command:check")
        similarity = cosine_similarity(vec1.data, vec2.data)

        assert -1.0 <= similarity <= 1.0

    def test_similarity_symmetric(self) -> None:
        """Cosine similarity is symmetric."""
        vec1 = embed_entity("command:init")
        vec2 = embed_entity("command:check")

        sim_12 = cosine_similarity(vec1.data, vec2.data)
        sim_21 = cosine_similarity(vec2.data, vec1.data)

        assert abs(sim_12 - sim_21) < 1e-10

    def test_zero_vector_returns_zero_similarity(self) -> None:
        """Zero vector returns 0.0 similarity."""
        vec = embed_entity("command:init")
        zero_vec = np.zeros(DEFAULT_DIMENSIONS)

        similarity = cosine_similarity(vec.data, zero_vec)
        assert similarity == 0.0

    def test_opposite_vectors_negative_similarity(self) -> None:
        """Opposite vectors have negative similarity."""
        vec1 = np.array([1.0, 0.0, 0.0])
        vec2 = np.array([-1.0, 0.0, 0.0])

        similarity = cosine_similarity(vec1, vec2)
        assert abs(similarity - (-1.0)) < 1e-10

    def test_orthogonal_vectors_near_zero_similarity(self) -> None:
        """Orthogonal vectors have near-zero similarity."""
        vec1 = np.array([1.0, 0.0, 0.0])
        vec2 = np.array([0.0, 1.0, 0.0])

        similarity = cosine_similarity(vec1, vec2)
        assert abs(similarity) < 1e-10


class TestManhattanDistance:
    """Test manhattan_distance function."""

    def test_identical_vectors_distance_zero(self) -> None:
        """Identical vectors have distance 0.0."""
        vec = embed_entity("command:init")
        distance = manhattan_distance(vec.data, vec.data)
        assert abs(distance) < 1e-10

    def test_distance_non_negative(self) -> None:
        """Distance is always non-negative."""
        vec1 = embed_entity("command:init")
        vec2 = embed_entity("command:check")
        distance = manhattan_distance(vec1.data, vec2.data)

        assert distance >= 0.0

    def test_distance_symmetric(self) -> None:
        """Manhattan distance is symmetric."""
        vec1 = embed_entity("command:init")
        vec2 = embed_entity("command:check")

        dist_12 = manhattan_distance(vec1.data, vec2.data)
        dist_21 = manhattan_distance(vec2.data, vec1.data)

        assert abs(dist_12 - dist_21) < 1e-10

    def test_simple_distance_calculation(self) -> None:
        """Correct calculation for simple vectors."""
        vec1 = np.array([1.0, 2.0, 3.0])
        vec2 = np.array([4.0, 5.0, 6.0])

        distance = manhattan_distance(vec1, vec2)
        # |1-4| + |2-5| + |3-6| = 3 + 3 + 3 = 9
        assert abs(distance - 9.0) < 1e-10

    def test_handles_negative_values(self) -> None:
        """Correct handling of negative values."""
        vec1 = np.array([1.0, -2.0, 3.0])
        vec2 = np.array([-1.0, 2.0, -3.0])

        distance = manhattan_distance(vec1, vec2)
        # |1-(-1)| + |(-2)-2| + |3-(-3)| = 2 + 4 + 6 = 12
        assert abs(distance - 12.0) < 1e-10


class TestHyperdimensionalVector:
    """Test HyperdimensionalVector class."""

    def test_initialization(self) -> None:
        """Vector initializes correctly."""
        data = np.random.randn(DEFAULT_DIMENSIONS)
        vec = HyperdimensionalVector(name="test", data=data, dimensions=DEFAULT_DIMENSIONS)

        assert vec.name == "test"
        assert vec.dimensions == DEFAULT_DIMENSIONS
        np.testing.assert_array_equal(vec.data, data)

    def test_dimension_mismatch_raises_error(self) -> None:
        """Raises error if data length doesn't match dimensions."""
        data = np.random.randn(100)

        with pytest.raises(ValueError, match="doesn't match"):
            HyperdimensionalVector(name="test", data=data, dimensions=200)

    def test_cosine_similarity_method(self) -> None:
        """cosine_similarity method works correctly."""
        vec1 = embed_entity("command:init")
        vec2 = embed_entity("command:check")

        # Method should match function
        method_sim = vec1.cosine_similarity(vec2)
        function_sim = cosine_similarity(vec1.data, vec2.data)

        assert abs(method_sim - function_sim) < 1e-10

    def test_manhattan_distance_method(self) -> None:
        """manhattan_distance method works correctly."""
        vec1 = embed_entity("command:init")
        vec2 = embed_entity("command:check")

        # Method should match function
        method_dist = vec1.manhattan_distance(vec2)
        function_dist = manhattan_distance(vec1.data, vec2.data)

        assert abs(method_dist - function_dist) < 1e-10

    def test_to_dict_serialization(self) -> None:
        """to_dict creates valid serializable dictionary."""
        vec = embed_entity("command:init")
        vec_dict = vec.to_dict()

        assert isinstance(vec_dict, dict)
        assert vec_dict["name"] == "command:init"
        assert vec_dict["dimensions"] == DEFAULT_DIMENSIONS
        assert isinstance(vec_dict["data"], list)
        assert len(vec_dict["data"]) == DEFAULT_DIMENSIONS

    def test_from_dict_deserialization(self) -> None:
        """from_dict reconstructs vector correctly."""
        original = embed_entity("command:init")
        vec_dict = original.to_dict()
        reconstructed = HyperdimensionalVector.from_dict(vec_dict)

        assert reconstructed.name == original.name
        assert reconstructed.dimensions == original.dimensions
        np.testing.assert_array_equal(reconstructed.data, original.data)

    def test_serialization_roundtrip(self) -> None:
        """Roundtrip serialization preserves vector."""
        original = embed_entity("command:init")
        roundtrip = HyperdimensionalVector.from_dict(original.to_dict())

        assert roundtrip.name == original.name
        assert roundtrip.dimensions == original.dimensions
        np.testing.assert_array_equal(roundtrip.data, original.data)


class TestEmbeddingCache:
    """Test EmbeddingCache class."""

    def test_initialization(self) -> None:
        """Cache initializes correctly."""
        cache = EmbeddingCache(dimensions=500)
        assert cache.dimensions == 500
        assert len(cache) == 0

    def test_add_vector(self) -> None:
        """Adding vector to cache works."""
        cache = EmbeddingCache()
        vec = embed_entity("command:init")

        cache.add(vec)
        assert len(cache) == 1
        assert "command:init" in cache

    def test_get_existing_vector(self) -> None:
        """Getting existing vector returns it."""
        cache = EmbeddingCache()
        vec = embed_entity("command:init")
        cache.add(vec)

        retrieved = cache.get("command:init")
        assert retrieved is not None
        assert retrieved.name == vec.name
        np.testing.assert_array_equal(retrieved.data, vec.data)

    def test_get_nonexistent_vector(self) -> None:
        """Getting nonexistent vector returns None."""
        cache = EmbeddingCache()
        retrieved = cache.get("command:nonexistent")
        assert retrieved is None

    def test_get_or_create_existing(self) -> None:
        """get_or_create returns existing vector."""
        cache = EmbeddingCache()
        original = embed_entity("command:init")
        cache.add(original)

        retrieved = cache.get_or_create("command:init")
        assert retrieved.name == original.name
        np.testing.assert_array_equal(retrieved.data, original.data)

    def test_get_or_create_new(self) -> None:
        """get_or_create creates new vector if not found."""
        cache = EmbeddingCache()
        vec = cache.get_or_create("command:init")

        assert vec.name == "command:init"
        assert "command:init" in cache
        assert len(cache) == 1

    def test_dimension_mismatch_raises_error(self) -> None:
        """Adding vector with wrong dimensions raises error."""
        cache = EmbeddingCache(dimensions=500)
        vec = embed_entity("command:init", dimensions=1000)

        with pytest.raises(ValueError, match="don't match"):
            cache.add(vec)

    def test_find_similar(self) -> None:
        """find_similar returns top-k most similar entities."""
        cache = EmbeddingCache()

        # Add several vectors
        cache.add(embed_entity("command:init"))
        cache.add(embed_entity("command:check"))
        cache.add(embed_entity("command:version"))
        cache.add(embed_entity("job:developer"))

        query = embed_entity("command:build")
        similar = cache.find_similar(query, top_k=3)

        assert len(similar) == 3
        # Check structure
        for name, sim in similar:
            assert isinstance(name, str)
            assert isinstance(sim, float)
            assert -1.0 <= sim <= 1.0

        # Check sorted descending
        similarities = [sim for _, sim in similar]
        assert similarities == sorted(similarities, reverse=True)

    def test_save_and_load(self) -> None:
        """Saving and loading cache works correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "cache.json"

            # Create and save cache
            cache = EmbeddingCache()
            cache.add(embed_entity("command:init"))
            cache.add(embed_entity("command:check"))
            cache.save(filepath)

            # Verify file exists
            assert filepath.exists()

            # Load cache
            loaded = EmbeddingCache.load(filepath)
            assert len(loaded) == 2
            assert "command:init" in loaded
            assert "command:check" in loaded

            # Verify vectors match
            original_vec = cache.get("command:init")
            loaded_vec = loaded.get("command:init")
            assert original_vec is not None
            assert loaded_vec is not None
            np.testing.assert_array_equal(original_vec.data, loaded_vec.data)

    def test_load_nonexistent_file_raises_error(self) -> None:
        """Loading nonexistent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="not found"):
            EmbeddingCache.load("/nonexistent/path.json")

    def test_json_format_is_valid(self) -> None:
        """Saved JSON format is valid and readable."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "cache.json"

            cache = EmbeddingCache()
            cache.add(embed_entity("command:init"))
            cache.save(filepath)

            # Parse JSON directly
            with filepath.open() as f:
                data = json.load(f)

            assert "dimensions" in data
            assert "embeddings" in data
            assert isinstance(data["embeddings"], list)
            assert len(data["embeddings"]) == 1

    def test_contains_operator(self) -> None:
        """__contains__ operator works correctly."""
        cache = EmbeddingCache()
        cache.add(embed_entity("command:init"))

        assert "command:init" in cache
        assert "command:nonexistent" not in cache

    def test_len_operator(self) -> None:
        """__len__ operator works correctly."""
        cache = EmbeddingCache()
        assert len(cache) == 0

        cache.add(embed_entity("command:init"))
        assert len(cache) == 1

        cache.add(embed_entity("command:check"))
        assert len(cache) == 2


class TestPrecomputeSpeckitEmbeddings:
    """Test precompute_speckit_embeddings function."""

    def test_precomputes_all_entities(self) -> None:
        """Pre-computes embeddings for all spec-kit entities."""
        cache = precompute_speckit_embeddings()

        # Should have 13 commands + 5 jobs + 43 outcomes + 16 features + 12 constraints
        # = 89 entities minimum
        assert len(cache) >= 89

    def test_includes_all_commands(self) -> None:
        """Includes all 13 spec-kit commands."""
        cache = precompute_speckit_embeddings()

        commands = [
            "command:init",
            "command:check",
            "command:ggen-sync",
            "command:version",
            "command:pm-discover",
            "command:pm-conform",
            "command:pm-stats",
            "command:pm-filter",
            "command:pm-sample",
            "command:spiff-validate",
            "command:spiff-run-workflow",
            "command:build",
            "command:cache-clear",
        ]

        for cmd in commands:
            assert cmd in cache

    def test_includes_all_jobs(self) -> None:
        """Includes all 5 JTBD jobs."""
        cache = precompute_speckit_embeddings()

        jobs = [
            "job:developer",
            "job:architect",
            "job:product-manager",
            "job:technical-writer",
            "job:quality-engineer",
        ]

        for job in jobs:
            assert job in cache

    def test_includes_outcomes(self) -> None:
        """Includes measurable outcomes."""
        cache = precompute_speckit_embeddings()

        # Check a few key outcomes
        outcomes = [
            "outcome:fast-startup",
            "outcome:reliable-builds",
            "outcome:high-test-coverage",
            "outcome:intuitive-cli",
            "outcome:modular-design",
        ]

        for outcome in outcomes:
            assert outcome in cache

    def test_includes_features(self) -> None:
        """Includes features."""
        cache = precompute_speckit_embeddings()

        # Check a few key features
        features = [
            "feature:three-tier-architecture",
            "feature:rdf-first-development",
            "feature:opentelemetry-integration",
        ]

        for feature in features:
            assert feature in cache

    def test_includes_constraints(self) -> None:
        """Includes architectural constraints."""
        cache = precompute_speckit_embeddings()

        # Check a few key constraints
        constraints = [
            "constraint:no-side-effects-in-ops",
            "constraint:subprocess-only-in-runtime",
            "constraint:three-tier-principle",
        ]

        for constraint in constraints:
            assert constraint in cache

    def test_custom_dimensions(self) -> None:
        """Respects custom dimensions parameter."""
        cache = precompute_speckit_embeddings(dimensions=500)

        assert cache.dimensions == 500

        # Verify vectors have correct dimensions
        vec = cache.get("command:init")
        assert vec is not None
        assert vec.dimensions == 500

    def test_can_save_and_load_precomputed(self) -> None:
        """Can save and load pre-computed embeddings."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "speckit-embeddings.json"

            # Pre-compute and save
            cache = precompute_speckit_embeddings()
            cache.save(filepath)

            # Load
            loaded = EmbeddingCache.load(filepath)
            assert len(loaded) == len(cache)


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_very_small_dimensions(self) -> None:
        """Handles very small dimensions (boundary case)."""
        vec = embed_entity("command:init", dimensions=10)
        assert vec.dimensions == 10
        assert len(vec.data) == 10

    def test_very_large_dimensions(self) -> None:
        """Handles very large dimensions."""
        vec = embed_entity("command:init", dimensions=10000)
        assert vec.dimensions == 10000
        assert len(vec.data) == 10000

    def test_whitespace_names(self) -> None:
        """Handles names with whitespace."""
        vec = embed_entity("command: test  name ")
        assert vec.name == "command: test  name "
        assert vec.dimensions == DEFAULT_DIMENSIONS

    def test_multiple_colons_in_name(self) -> None:
        """Handles names with multiple colons."""
        vec = embed_entity("namespace:category:entity:detail")
        assert vec.name == "namespace:category:entity:detail"

    def test_numeric_names(self) -> None:
        """Handles numeric entity names."""
        vec = embed_entity("12345")
        assert vec.name == "12345"

    def test_similarity_of_similar_prefixes(self) -> None:
        """Vectors with similar prefixes are still different."""
        vec1 = embed_entity("command:init")
        vec2 = embed_entity("command:init-extra")

        # Should be different vectors
        similarity = vec1.cosine_similarity(vec2)
        assert similarity < 1.0  # Not identical
        # But similarity is deterministic
        assert abs(similarity - vec1.cosine_similarity(vec2)) < 1e-10


class TestDeterminismAndReproducibility:
    """Test determinism and reproducibility guarantees."""

    def test_cross_session_determinism(self) -> None:
        """Same entity name produces same vector across sessions."""
        # Create vector in "session 1"
        vec1 = embed_entity("command:init")

        # Simulate new session - create same vector again
        vec2 = embed_entity("command:init")

        # Must be identical
        np.testing.assert_array_equal(vec1.data, vec2.data)
        assert vec1.cosine_similarity(vec2) == 1.0

    def test_order_independence(self) -> None:
        """Order of creation doesn't affect vectors."""
        # Create in order A, B, C
        vec_a1 = embed_entity("command:a")
        vec_b1 = embed_entity("command:b")
        vec_c1 = embed_entity("command:c")

        # Create in different order C, A, B
        vec_c2 = embed_entity("command:c")
        vec_a2 = embed_entity("command:a")
        vec_b2 = embed_entity("command:b")

        # Must be identical
        np.testing.assert_array_equal(vec_a1.data, vec_a2.data)
        np.testing.assert_array_equal(vec_b1.data, vec_b2.data)
        np.testing.assert_array_equal(vec_c1.data, vec_c2.data)

    def test_cache_independence(self) -> None:
        """Vectors are independent of cache state."""
        cache1 = EmbeddingCache()
        vec1 = cache1.get_or_create("command:init")

        cache2 = EmbeddingCache()
        vec2 = cache2.get_or_create("command:init")

        # Must be identical
        np.testing.assert_array_equal(vec1.data, vec2.data)
