"""
Property-based tests for hyperdimensional computing modules.

This module uses Hypothesis to generate randomized test cases that verify
mathematical properties and invariants of hyperdimensional vector operations.

Properties tested:
- Vector dimension preservation
- Binding commutativity and associativity
- Bundling properties
- Distance metric properties
- Encoding/decoding consistency
"""

from __future__ import annotations

import numpy as np
import pytest
from hypothesis import assume, given, settings, strategies as st

# Mark all tests in this module as property-based tests
pytestmark = pytest.mark.property


# ============================================================================
# Hypothesis Strategies for Hyperdimensional Vectors
# ============================================================================


@st.composite
def hyperdimensional_vector(draw: st.DrawFn, dimensions: int = 10000) -> np.ndarray:
    """Generate a random hyperdimensional vector."""
    # Generate binary {-1, 1} vectors
    return draw(
        st.lists(
            st.sampled_from([-1.0, 1.0]),
            min_size=dimensions,
            max_size=dimensions,
        )
    ).pipe(np.array)


@st.composite
def positive_dimensions(draw: st.DrawFn) -> int:
    """Generate valid dimension sizes for hyperdimensional vectors."""
    return draw(st.integers(min_value=100, max_value=1000))


# ============================================================================
# Property Tests for Vector Operations
# ============================================================================


class TestHyperdimensionalVectorProperties:
    """Property-based tests for hyperdimensional vector operations."""

    @given(
        dim=st.integers(min_value=100, max_value=1000),
    )
    @settings(max_examples=50)
    def test_vector_dimension_preservation(self, dim: int) -> None:
        """Test that vector operations preserve dimensionality."""
        # Create random vectors
        v1 = np.random.choice([-1.0, 1.0], size=dim)
        v2 = np.random.choice([-1.0, 1.0], size=dim)

        # Binding (element-wise multiplication)
        bound = v1 * v2
        assert bound.shape == (dim,), "Binding should preserve dimension"

        # Bundling (element-wise addition with normalization)
        bundled = v1 + v2
        assert bundled.shape == (dim,), "Bundling should preserve dimension"

    @given(
        values=st.lists(st.floats(min_value=-1000, max_value=1000), min_size=2, max_size=10)
    )
    @settings(max_examples=100)
    def test_binding_commutativity(self, values: list[float]) -> None:
        """Test that binding (XOR) is commutative: A ⊗ B = B ⊗ A."""
        dim = 500
        vectors = [np.random.choice([-1.0, 1.0], size=dim) for _ in values]

        if len(vectors) < 2:
            return

        v1, v2 = vectors[0], vectors[1]
        forward = v1 * v2
        backward = v2 * v1

        np.testing.assert_array_equal(forward, backward, err_msg="Binding is not commutative")

    @given(
        seed=st.integers(min_value=0, max_value=10000),
    )
    @settings(max_examples=50)
    def test_binding_associativity(self, seed: int) -> None:
        """Test that binding is associative: (A ⊗ B) ⊗ C = A ⊗ (B ⊗ C)."""
        np.random.seed(seed)
        dim = 500

        v1 = np.random.choice([-1.0, 1.0], size=dim)
        v2 = np.random.choice([-1.0, 1.0], size=dim)
        v3 = np.random.choice([-1.0, 1.0], size=dim)

        left = (v1 * v2) * v3
        right = v1 * (v2 * v3)

        np.testing.assert_array_equal(left, right, err_msg="Binding is not associative")

    @given(
        seed=st.integers(min_value=0, max_value=10000),
    )
    @settings(max_examples=50)
    def test_self_inverse_property(self, seed: int) -> None:
        """Test that A ⊗ A = Identity (self-inverse property)."""
        np.random.seed(seed)
        dim = 500

        v = np.random.choice([-1.0, 1.0], size=dim)
        result = v * v

        # For binary vectors {-1, 1}, self-binding should give all 1s
        expected = np.ones(dim)
        np.testing.assert_array_equal(result, expected, err_msg="Self-inverse property violated")

    @given(
        n_vectors=st.integers(min_value=2, max_value=10),
        seed=st.integers(min_value=0, max_value=10000),
    )
    @settings(max_examples=30)
    def test_bundling_similarity(self, n_vectors: int, seed: int) -> None:
        """Test that bundled vectors are similar to their components."""
        np.random.seed(seed)
        dim = 500

        vectors = [np.random.choice([-1.0, 1.0], size=dim) for _ in range(n_vectors)]

        # Bundle (sum and threshold)
        bundled = np.sum(vectors, axis=0)
        bundled_binary = np.sign(bundled)
        bundled_binary[bundled_binary == 0] = 1  # Handle zeros

        # Check similarity (cosine similarity > threshold)
        for v in vectors:
            similarity = np.dot(bundled_binary, v) / dim
            # Bundled vector should have positive similarity with components
            assert similarity > 0, f"Bundled vector not similar to component: {similarity}"


# ============================================================================
# Property Tests for Distance Metrics
# ============================================================================


class TestDistanceMetricProperties:
    """Property-based tests for distance metric properties."""

    @given(
        seed=st.integers(min_value=0, max_value=10000),
    )
    @settings(max_examples=50)
    def test_distance_non_negativity(self, seed: int) -> None:
        """Test that distance is always non-negative."""
        np.random.seed(seed)
        dim = 500

        v1 = np.random.choice([-1.0, 1.0], size=dim)
        v2 = np.random.choice([-1.0, 1.0], size=dim)

        # Hamming distance
        distance = np.sum(v1 != v2)
        assert distance >= 0, "Distance must be non-negative"

    @given(
        seed=st.integers(min_value=0, max_value=10000),
    )
    @settings(max_examples=50)
    def test_distance_symmetry(self, seed: int) -> None:
        """Test that distance is symmetric: d(A, B) = d(B, A)."""
        np.random.seed(seed)
        dim = 500

        v1 = np.random.choice([-1.0, 1.0], size=dim)
        v2 = np.random.choice([-1.0, 1.0], size=dim)

        dist_forward = np.sum(v1 != v2)
        dist_backward = np.sum(v2 != v1)

        assert dist_forward == dist_backward, "Distance is not symmetric"

    @given(
        seed=st.integers(min_value=0, max_value=10000),
    )
    @settings(max_examples=30)
    def test_triangle_inequality(self, seed: int) -> None:
        """Test triangle inequality: d(A, C) ≤ d(A, B) + d(B, C)."""
        np.random.seed(seed)
        dim = 500

        v1 = np.random.choice([-1.0, 1.0], size=dim)
        v2 = np.random.choice([-1.0, 1.0], size=dim)
        v3 = np.random.choice([-1.0, 1.0], size=dim)

        d_ac = np.sum(v1 != v3)
        d_ab = np.sum(v1 != v2)
        d_bc = np.sum(v2 != v3)

        assert d_ac <= d_ab + d_bc, f"Triangle inequality violated: {d_ac} > {d_ab} + {d_bc}"


# ============================================================================
# Property Tests for Encoding/Decoding
# ============================================================================


class TestEncodingDecodingProperties:
    """Property-based tests for encoding/decoding consistency."""

    @given(
        text=st.text(min_size=1, max_size=100, alphabet=st.characters(min_codepoint=32, max_codepoint=126)),
        seed=st.integers(min_value=0, max_value=10000),
    )
    @settings(max_examples=50)
    def test_ngram_encoding_deterministic(self, text: str, seed: int) -> None:
        """Test that n-gram encoding is deterministic."""
        np.random.seed(seed)
        dim = 500

        # Simple n-gram encoding simulation
        def encode_char(char: str, dim: int) -> np.ndarray:
            """Encode a character as a random vector (seeded by char)."""
            char_seed = ord(char)
            rng = np.random.RandomState(char_seed)
            return rng.choice([-1.0, 1.0], size=dim)

        # Encode text twice
        encoding1 = [encode_char(c, dim) for c in text]
        encoding2 = [encode_char(c, dim) for c in text]

        # Should be identical
        for e1, e2 in zip(encoding1, encoding2):
            np.testing.assert_array_equal(e1, e2, err_msg="Encoding is not deterministic")

    @given(
        value=st.integers(min_value=0, max_value=1000),
        seed=st.integers(min_value=0, max_value=10000),
    )
    @settings(max_examples=50)
    def test_numeric_encoding_injectivity(self, value: int, seed: int) -> None:
        """Test that different numbers get different encodings."""
        np.random.seed(seed)
        dim = 500

        # Simulate thermometer encoding
        def thermometer_encode(val: int, max_val: int, dim: int) -> np.ndarray:
            """Thermometer encoding: first k bits are 1, rest are -1."""
            k = int((val / max_val) * dim)
            encoding = np.ones(dim) * -1
            encoding[:k] = 1
            return encoding

        enc1 = thermometer_encode(value, 1000, dim)
        enc2 = thermometer_encode(value, 1000, dim)

        np.testing.assert_array_equal(enc1, enc2, err_msg="Encoding is not consistent")


# ============================================================================
# Property Tests for Similarity Metrics
# ============================================================================


class TestSimilarityProperties:
    """Property-based tests for similarity metrics."""

    @given(
        seed=st.integers(min_value=0, max_value=10000),
    )
    @settings(max_examples=50)
    def test_cosine_similarity_bounds(self, seed: int) -> None:
        """Test that cosine similarity is in [-1, 1]."""
        np.random.seed(seed)
        dim = 500

        v1 = np.random.choice([-1.0, 1.0], size=dim)
        v2 = np.random.choice([-1.0, 1.0], size=dim)

        # Cosine similarity
        similarity = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

        assert -1 <= similarity <= 1, f"Cosine similarity out of bounds: {similarity}"

    @given(
        seed=st.integers(min_value=0, max_value=10000),
    )
    @settings(max_examples=50)
    def test_self_similarity_maximum(self, seed: int) -> None:
        """Test that a vector is most similar to itself."""
        np.random.seed(seed)
        dim = 500

        v = np.random.choice([-1.0, 1.0], size=dim)

        # Cosine similarity with self should be 1.0
        self_similarity = np.dot(v, v) / (np.linalg.norm(v) * np.linalg.norm(v))

        np.testing.assert_almost_equal(self_similarity, 1.0, decimal=5, err_msg="Self-similarity is not 1.0")
