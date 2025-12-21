"""
specify_cli.hyperdimensional.embeddings
---------------------------------------
Core hyperdimensional vector embedding engine.

This module implements a comprehensive hyperdimensional computing (HDC) system
for creating and manipulating semantic vector embeddings of domain entities.

Hyperdimensional Computing Principles
-------------------------------------
HDC operates in very high-dimensional spaces (typically 10,000+ dimensions) where:
1. **Random vectors are nearly orthogonal**: High probability of orthogonality
2. **Robust to noise**: Can tolerate errors and perturbations
3. **Compositional**: Vectors can be combined to create complex structures
4. **Distributed representation**: Information is spread across all dimensions

Key Operations
--------------
- **Binding (⊗)**: Circular convolution for encoding relationships
- **Bundling (+)**: Superposition for combining similar concepts
- **Permutation (rho)**: Role encoding via vector rotation

Classes
-------
HyperdimensionalEmbedding
    Main embedding engine with initialization, encoding, and similarity
VectorOperations
    Low-level mathematical operations on vectors

Example
-------
    >>> hde = HyperdimensionalEmbedding(dimensions=10000)
    >>> cmd_init = hde.embed_command("init")
    >>> cmd_check = hde.embed_command("check")
    >>> similarity = hde.cosine_similarity(cmd_init, cmd_check)
    >>> print(f"Similarity: {similarity:.4f}")
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np
from numpy.typing import NDArray

if TYPE_CHECKING:
    from collections.abc import Sequence

# Type aliases
Vector = NDArray[np.float64]
VectorDict = dict[str, Vector]


@dataclass
class VectorStats:
    """Statistics about a hyperdimensional vector.

    Attributes
    ----------
    mean : float
        Mean value across all dimensions
    std : float
        Standard deviation across dimensions
    norm : float
        L2 norm (Euclidean length)
    sparsity : float
        Fraction of near-zero elements (|x| < 0.01)
    entropy : float
        Shannon entropy of absolute values
    """

    mean: float
    std: float
    norm: float
    sparsity: float
    entropy: float


class VectorOperations:
    """Low-level mathematical operations on hyperdimensional vectors.

    This class provides the fundamental operations for hyperdimensional computing:
    - Binding via circular convolution
    - Bundling via element-wise addition
    - Normalization strategies
    - Similarity metrics
    - Information-theoretic measures
    """

    @staticmethod
    def normalize_l2(vector: Vector) -> Vector:
        """Normalize vector to unit L2 norm (Euclidean length = 1).

        Parameters
        ----------
        vector : Vector
            Input vector to normalize

        Returns
        -------
        Vector
            Unit-length normalized vector

        Notes
        -----
        If the input vector has zero norm, returns the original vector
        to avoid division by zero.
        """
        norm = np.linalg.norm(vector)
        if norm < 1e-10:
            return vector
        return vector / norm

    @staticmethod
    def normalize_minmax(vector: Vector) -> Vector:
        """Normalize vector to range [-1, 1] using min-max scaling.

        Parameters
        ----------
        vector : Vector
            Input vector to normalize

        Returns
        -------
        Vector
            Vector with values in [-1, 1] range
        """
        vmin = vector.min()
        vmax = vector.max()
        if abs(vmax - vmin) < 1e-10:
            return np.zeros_like(vector)
        return 2.0 * (vector - vmin) / (vmax - vmin) - 1.0

    @staticmethod
    def normalize_zscore(vector: Vector) -> Vector:
        """Normalize vector using z-score (zero mean, unit variance).

        Parameters
        ----------
        vector : Vector
            Input vector to normalize

        Returns
        -------
        Vector
            Standardized vector with mean=0, std=1
        """
        mean = vector.mean()
        std = vector.std()
        if std < 1e-10:
            return vector - mean
        return (vector - mean) / std

    @staticmethod
    def bind(vector_a: Vector, vector_b: Vector) -> Vector:
        """Bind two vectors via circular convolution (relationship encoding).

        Binding is the fundamental operation for encoding relationships in HDC.
        It creates a new vector that represents the relationship between A and B.

        Parameters
        ----------
        vector_a : Vector
            First vector (e.g., job vector)
        vector_b : Vector
            Second vector (e.g., feature vector)

        Returns
        -------
        Vector
            Bound vector representing the A→B relationship

        Notes
        -----
        Circular convolution properties:
        - Commutative: A ⊗ B = B ⊗ A
        - Associative: (A ⊗ B) ⊗ C = A ⊗ (B ⊗ C)
        - Approximate inverse: A ⊗ B ⊗ ~B ≈ A

        Example
        -------
        >>> job = hde.embed_job("developer")
        >>> feature = hde.embed_feature("rdf-validation")
        >>> relationship = VectorOperations.bind(job, feature)
        """
        # Use FFT for efficient circular convolution
        fft_a = np.fft.fft(vector_a)
        fft_b = np.fft.fft(vector_b)
        bound = np.real(np.fft.ifft(fft_a * fft_b))
        return VectorOperations.normalize_l2(bound)

    @staticmethod
    def unbind(bound_vector: Vector, vector_b: Vector) -> Vector:
        """Unbind (approximate inverse of bind).

        Given A ⊗ B and B, recover approximate A.

        Parameters
        ----------
        bound_vector : Vector
            Result of A ⊗ B
        vector_b : Vector
            Known vector B

        Returns
        -------
        Vector
            Approximation of A
        """
        # Unbind via circular correlation (conjugate in frequency domain)
        fft_bound = np.fft.fft(bound_vector)
        fft_b_conj = np.conj(np.fft.fft(vector_b))
        unbound = np.real(np.fft.ifft(fft_bound * fft_b_conj))
        return VectorOperations.normalize_l2(unbound)

    @staticmethod
    def superpose(vectors: Sequence[Vector], weights: Sequence[float] | None = None) -> Vector:
        """Combine vectors via weighted superposition (bundling).

        Superposition creates a vector that represents the combined meaning
        of multiple vectors. With uniform weights, it's a simple average.

        Parameters
        ----------
        vectors : Sequence[Vector]
            List of vectors to combine
        weights : Sequence[float], optional
            Weights for each vector (default: uniform)

        Returns
        -------
        Vector
            Combined vector representing superposition

        Example
        -------
        >>> outcomes = [hde.embed_outcome("speed"), hde.embed_outcome("reliability")]
        >>> combined = VectorOperations.superpose(outcomes)
        """
        if not vectors:
            raise ValueError("Cannot superpose empty list of vectors")

        if weights is None:
            weights = [1.0 / len(vectors)] * len(vectors)

        if len(weights) != len(vectors):
            raise ValueError("Number of weights must match number of vectors")

        result = np.zeros_like(vectors[0])
        for vec, weight in zip(vectors, weights, strict=True):
            result += weight * vec

        return VectorOperations.normalize_l2(result)

    @staticmethod
    def permute(vector: Vector, shift: int) -> Vector:
        """Permute vector by circular shift (role encoding).

        Permutation is used to encode roles or positions in a sequence.

        Parameters
        ----------
        vector : Vector
            Input vector to permute
        shift : int
            Number of positions to shift (can be negative)

        Returns
        -------
        Vector
            Permuted vector
        """
        return np.roll(vector, shift)

    @staticmethod
    def cosine_similarity(vector_a: Vector, vector_b: Vector) -> float:
        """Compute cosine similarity between two vectors.

        Returns value in [-1, 1] where:
        - 1.0: Identical vectors
        - 0.0: Orthogonal vectors
        - -1.0: Opposite vectors

        Parameters
        ----------
        vector_a : Vector
            First vector
        vector_b : Vector
            Second vector

        Returns
        -------
        float
            Cosine similarity in [-1, 1]
        """
        dot_product = np.dot(vector_a, vector_b)
        norm_a = np.linalg.norm(vector_a)
        norm_b = np.linalg.norm(vector_b)

        if norm_a < 1e-10 or norm_b < 1e-10:
            return 0.0

        similarity = dot_product / (norm_a * norm_b)
        return float(np.clip(similarity, -1.0, 1.0))

    @staticmethod
    def euclidean_distance(vector_a: Vector, vector_b: Vector) -> float:
        """Compute Euclidean (L2) distance between vectors.

        Parameters
        ----------
        vector_a : Vector
            First vector
        vector_b : Vector
            Second vector

        Returns
        -------
        float
            Euclidean distance (non-negative)
        """
        return float(np.linalg.norm(vector_a - vector_b))

    @staticmethod
    def hamming_distance(vector_a: Vector, vector_b: Vector, threshold: float = 0.0) -> int:
        """Compute Hamming distance (number of differing binary components).

        Parameters
        ----------
        vector_a : Vector
            First vector
        vector_b : Vector
            Second vector
        threshold : float, optional
            Threshold for binarization (default: 0.0)

        Returns
        -------
        int
            Number of differing bits
        """
        binary_a = (vector_a > threshold).astype(int)
        binary_b = (vector_b > threshold).astype(int)
        return int(np.sum(binary_a != binary_b))

    @staticmethod
    def information_distance(vector_a: Vector, vector_b: Vector, bins: int = 50) -> float:
        """Compute information-theoretic distance via Jensen-Shannon divergence.

        Parameters
        ----------
        vector_a : Vector
            First vector
        vector_b : Vector
            Second vector
        bins : int, optional
            Number of histogram bins (default: 50)

        Returns
        -------
        float
            Jensen-Shannon divergence in [0, 1]
        """
        # Create normalized histograms
        hist_a, _ = np.histogram(vector_a, bins=bins, density=True)
        hist_b, _ = np.histogram(vector_b, bins=bins, density=True)

        # Normalize to probabilities
        hist_a = hist_a / (hist_a.sum() + 1e-10)
        hist_b = hist_b / (hist_b.sum() + 1e-10)

        # Jensen-Shannon divergence
        m = 0.5 * (hist_a + hist_b)

        def kl_divergence(p: NDArray[np.float64], q: NDArray[np.float64]) -> float:
            # Add small epsilon to avoid log(0)
            epsilon = 1e-10
            p = p + epsilon
            q = q + epsilon
            return float(np.sum(p * np.log(p / q)))

        js_div = 0.5 * kl_divergence(hist_a, m) + 0.5 * kl_divergence(hist_b, m)
        return float(np.sqrt(js_div))  # Square root for metric property

    @staticmethod
    def vector_stats(vector: Vector) -> VectorStats:
        """Compute comprehensive statistics for a vector.

        Parameters
        ----------
        vector : Vector
            Input vector

        Returns
        -------
        VectorStats
            Statistical summary
        """
        mean = float(vector.mean())
        std = float(vector.std())
        norm = float(np.linalg.norm(vector))
        sparsity = float(np.sum(np.abs(vector) < 0.01) / len(vector))

        # Shannon entropy of absolute values
        abs_vector = np.abs(vector)
        hist, _ = np.histogram(abs_vector, bins=50, density=True)
        hist = hist / (hist.sum() + 1e-10)
        entropy = float(-np.sum(hist * np.log(hist + 1e-10)))

        return VectorStats(mean=mean, std=std, norm=norm, sparsity=sparsity, entropy=entropy)


class HyperdimensionalEmbedding:
    """Main hyperdimensional embedding engine.

    This class manages the creation, storage, and manipulation of
    hyperdimensional vector embeddings for all domain entities.

    Parameters
    ----------
    dimensions : int, optional
        Dimensionality of embedding vectors (default: 10000)
    seed : int, optional
        Random seed for reproducibility (default: 42)
    normalize : str, optional
        Normalization strategy: "l2", "minmax", "zscore" (default: "l2")

    Attributes
    ----------
    dimensions : int
        Vector dimensionality
    embeddings : VectorDict
        Cache of entity→vector mappings
    seed : int
        Random seed for reproducibility

    Example
    -------
    >>> hde = HyperdimensionalEmbedding(dimensions=10000)
    >>> init_vec = hde.embed_command("init")
    >>> check_vec = hde.embed_command("check")
    >>> similarity = hde.cosine_similarity(init_vec, check_vec)
    """

    def __init__(
        self,
        dimensions: int = 10000,
        seed: int = 42,
        normalize: str = "l2",
    ) -> None:
        """Initialize hyperdimensional embedding engine."""
        if dimensions < 100:
            raise ValueError("Dimensions must be >= 100 for effective HDC")
        if normalize not in ("l2", "minmax", "zscore"):
            raise ValueError("normalize must be 'l2', 'minmax', or 'zscore'")

        self.dimensions = dimensions
        self.seed = seed
        self.normalize_strategy = normalize
        self.embeddings: VectorDict = {}
        self._rng = np.random.RandomState(seed)

    def _get_normalization_fn(self) -> Any:
        """Get normalization function based on strategy."""
        if self.normalize_strategy == "l2":
            return VectorOperations.normalize_l2
        if self.normalize_strategy == "minmax":
            return VectorOperations.normalize_minmax
        return VectorOperations.normalize_zscore

    def _create_random_vector(self, entity_name: str) -> Vector:
        """Create deterministic random vector for entity.

        Uses entity name as seed for reproducibility.

        Parameters
        ----------
        entity_name : str
            Entity name (e.g., "command:init")

        Returns
        -------
        Vector
            Random hyperdimensional vector
        """
        # Create deterministic seed from entity name
        hash_digest = hashlib.sha256(entity_name.encode()).digest()
        seed_value = int.from_bytes(hash_digest[:4], byteorder="big")

        # Create random vector with entity-specific seed
        rng = np.random.RandomState(seed_value)
        vector = rng.randn(self.dimensions)

        # Normalize according to strategy
        normalize_fn = self._get_normalization_fn()
        return normalize_fn(vector)

    def embed_command(self, command_name: str) -> Vector:
        """Create embedding for CLI command.

        Parameters
        ----------
        command_name : str
            Command name (e.g., "init", "check", "ggen-sync")

        Returns
        -------
        Vector
            Hyperdimensional embedding vector

        Example
        -------
        >>> hde = HyperdimensionalEmbedding()
        >>> init_cmd = hde.embed_command("init")
        """
        entity_key = f"command:{command_name}"
        if entity_key not in self.embeddings:
            self.embeddings[entity_key] = self._create_random_vector(entity_key)
        return self.embeddings[entity_key]

    def embed_job(self, job_name: str) -> Vector:
        """Create embedding for JTBD persona/job.

        Parameters
        ----------
        job_name : str
            Job name (e.g., "developer", "architect", "product-manager")

        Returns
        -------
        Vector
            Hyperdimensional embedding vector
        """
        entity_key = f"job:{job_name}"
        if entity_key not in self.embeddings:
            self.embeddings[entity_key] = self._create_random_vector(entity_key)
        return self.embeddings[entity_key]

    def embed_outcome(self, outcome_name: str) -> Vector:
        """Create embedding for measurable outcome.

        Parameters
        ----------
        outcome_name : str
            Outcome name (e.g., "fast-startup", "reliable-builds")

        Returns
        -------
        Vector
            Hyperdimensional embedding vector
        """
        entity_key = f"outcome:{outcome_name}"
        if entity_key not in self.embeddings:
            self.embeddings[entity_key] = self._create_random_vector(entity_key)
        return self.embeddings[entity_key]

    def embed_feature(self, feature_name: str) -> Vector:
        """Create embedding for feature specification.

        Parameters
        ----------
        feature_name : str
            Feature name (e.g., "rdf-validation", "three-tier-arch")

        Returns
        -------
        Vector
            Hyperdimensional embedding vector
        """
        entity_key = f"feature:{feature_name}"
        if entity_key not in self.embeddings:
            self.embeddings[entity_key] = self._create_random_vector(entity_key)
        return self.embeddings[entity_key]

    def embed_constraint(self, constraint_name: str) -> Vector:
        """Create embedding for architectural constraint.

        Parameters
        ----------
        constraint_name : str
            Constraint name (e.g., "no-side-effects-in-ops", "three-tier-principle")

        Returns
        -------
        Vector
            Hyperdimensional embedding vector
        """
        entity_key = f"constraint:{constraint_name}"
        if entity_key not in self.embeddings:
            self.embeddings[entity_key] = self._create_random_vector(entity_key)
        return self.embeddings[entity_key]

    def bind(self, vector_a: Vector, vector_b: Vector) -> Vector:
        """Bind two vectors to encode relationship.

        Parameters
        ----------
        vector_a : Vector
            First vector
        vector_b : Vector
            Second vector

        Returns
        -------
        Vector
            Bound relationship vector
        """
        return VectorOperations.bind(vector_a, vector_b)

    def unbind(self, bound_vector: Vector, vector_b: Vector) -> Vector:
        """Unbind to recover original vector.

        Parameters
        ----------
        bound_vector : Vector
            Bound vector (A ⊗ B)
        vector_b : Vector
            Known vector B

        Returns
        -------
        Vector
            Approximation of A
        """
        return VectorOperations.unbind(bound_vector, vector_b)

    def superpose(
        self, vectors: Sequence[Vector], weights: Sequence[float] | None = None
    ) -> Vector:
        """Combine vectors via superposition.

        Parameters
        ----------
        vectors : Sequence[Vector]
            Vectors to combine
        weights : Sequence[float], optional
            Weights for each vector

        Returns
        -------
        Vector
            Combined vector
        """
        return VectorOperations.superpose(vectors, weights)

    def cosine_similarity(self, vector_a: Vector, vector_b: Vector) -> float:
        """Compute cosine similarity between vectors.

        Parameters
        ----------
        vector_a : Vector
            First vector
        vector_b : Vector
            Second vector

        Returns
        -------
        float
            Similarity in [-1, 1]
        """
        return VectorOperations.cosine_similarity(vector_a, vector_b)

    def semantic_distance(self, vector_a: Vector, vector_b: Vector) -> float:
        """Compute semantic distance (1 - cosine_similarity).

        Returns value in [0, 2] where:
        - 0.0: Identical vectors
        - 1.0: Orthogonal vectors
        - 2.0: Opposite vectors

        Parameters
        ----------
        vector_a : Vector
            First vector
        vector_b : Vector
            Second vector

        Returns
        -------
        float
            Semantic distance in [0, 2]
        """
        return 1.0 - self.cosine_similarity(vector_a, vector_b)

    def information_distance(self, vector_a: Vector, vector_b: Vector) -> float:
        """Compute information-theoretic distance.

        Parameters
        ----------
        vector_a : Vector
            First vector
        vector_b : Vector
            Second vector

        Returns
        -------
        float
            Information distance
        """
        return VectorOperations.information_distance(vector_a, vector_b)

    def find_similar(
        self,
        query_vector: Vector,
        candidates: VectorDict,
        top_k: int = 5,
    ) -> list[tuple[str, float]]:
        """Find most similar entities to query vector.

        Parameters
        ----------
        query_vector : Vector
            Query vector
        candidates : VectorDict
            Dictionary of entity_name → vector to search
        top_k : int, optional
            Number of top results to return (default: 5)

        Returns
        -------
        list[tuple[str, float]]
            List of (entity_name, similarity) sorted by similarity descending
        """
        similarities: list[tuple[str, float]] = []
        for entity_name, vector in candidates.items():
            sim = self.cosine_similarity(query_vector, vector)
            similarities.append((entity_name, sim))

        # Sort by similarity descending
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

    def save(self, filepath: Path | str) -> None:
        """Save embeddings to JSON file.

        Parameters
        ----------
        filepath : Path | str
            Output file path
        """
        filepath = Path(filepath)
        data = {
            "dimensions": self.dimensions,
            "seed": self.seed,
            "normalize_strategy": self.normalize_strategy,
            "embeddings": {key: vector.tolist() for key, vector in self.embeddings.items()},
        }
        with filepath.open("w") as f:
            json.dump(data, f, indent=2)

    def load(self, filepath: Path | str) -> None:
        """Load embeddings from JSON file.

        Parameters
        ----------
        filepath : Path | str
            Input file path
        """
        filepath = Path(filepath)
        with filepath.open() as f:
            data = json.load(f)

        # Validate dimensions match
        if data["dimensions"] != self.dimensions:
            raise ValueError(f"Dimension mismatch: {data['dimensions']} != {self.dimensions}")

        self.seed = data["seed"]
        self.normalize_strategy = data["normalize_strategy"]
        self.embeddings = {
            key: np.array(vector, dtype=np.float64) for key, vector in data["embeddings"].items()
        }

    def get_stats(self, entity_name: str) -> VectorStats:
        """Get statistics for entity embedding.

        Parameters
        ----------
        entity_name : str
            Full entity name (e.g., "command:init")

        Returns
        -------
        VectorStats
            Statistical summary
        """
        if entity_name not in self.embeddings:
            raise KeyError(f"No embedding found for {entity_name}")
        return VectorOperations.vector_stats(self.embeddings[entity_name])

    def clear_cache(self) -> None:
        """Clear all cached embeddings."""
        self.embeddings.clear()

    def get_all_embeddings(self) -> VectorDict:
        """Get all cached embeddings.

        Returns
        -------
        VectorDict
            Dictionary of entity_name → vector
        """
        return dict(self.embeddings)


__all__ = [
    "HyperdimensionalEmbedding",
    "Vector",
    "VectorDict",
    "VectorOperations",
    "VectorStats",
]
