"""
specify_cli.hyperdimensional.core
----------------------------------
Minimal viable hyperdimensional embeddings system (80/20 principle).

This module provides a streamlined implementation focusing on:
- Deterministic hash-based vector generation
- Cosine similarity and Manhattan distance metrics
- Simple JSON persistence
- Pre-computed embeddings for all spec-kit entities

Deliberately excluded for MVP (YAGNI):
- FFT circular convolution (bind/unbind)
- RDF persistence
- Complex normalization strategies
- Information-theoretic distances

Classes
-------
HyperdimensionalVector
    Core vector class with similarity metrics
EmbeddingCache
    Simple JSON-based persistence

Example
-------
    >>> from specify_cli.hyperdimensional.core import embed_entity, cosine_similarity
    >>> cmd_init = embed_entity("command:init")
    >>> cmd_check = embed_entity("command:check")
    >>> similarity = cosine_similarity(cmd_init, cmd_check)
    >>> print(f"Similarity: {similarity:.4f}")
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
from numpy.typing import NDArray

if TYPE_CHECKING:
    pass

# Type alias
Vector = NDArray[np.float64]

# Default dimensionality (1000 is sufficient for spec-kit scale)
DEFAULT_DIMENSIONS = 1000


@dataclass
class HyperdimensionalVector:
    """Hyperdimensional vector with built-in similarity operations.

    This is a minimal implementation focusing on the 20% of features
    that provide 80% of value for spec-kit use cases.

    Attributes
    ----------
    name : str
        Entity name (e.g., "command:init", "job:developer")
    data : Vector
        Numpy array of shape (dimensions,)
    dimensions : int
        Vector dimensionality (default: 1000)

    Methods
    -------
    cosine_similarity(other)
        Compute cosine similarity with another vector
    manhattan_distance(other)
        Compute Manhattan (L1) distance to another vector
    to_dict()
        Serialize to dictionary for JSON storage
    """

    name: str
    data: Vector
    dimensions: int = DEFAULT_DIMENSIONS

    def __post_init__(self) -> None:
        """Validate vector dimensions."""
        if len(self.data) != self.dimensions:
            raise ValueError(
                f"Vector data length {len(self.data)} doesn't match "
                f"dimensions {self.dimensions}"
            )

    def cosine_similarity(self, other: HyperdimensionalVector) -> float:
        """Compute cosine similarity with another vector.

        Returns value in [-1, 1] where:
        - 1.0: Identical vectors
        - 0.0: Orthogonal vectors
        - -1.0: Opposite vectors

        Parameters
        ----------
        other : HyperdimensionalVector
            Vector to compare against

        Returns
        -------
        float
            Cosine similarity in [-1, 1]
        """
        return cosine_similarity(self.data, other.data)

    def manhattan_distance(self, other: HyperdimensionalVector) -> float:
        """Compute Manhattan (L1) distance to another vector.

        Manhattan distance is the sum of absolute differences across all dimensions.
        For normalized vectors, this is often more interpretable than Euclidean.

        Parameters
        ----------
        other : HyperdimensionalVector
            Vector to compare against

        Returns
        -------
        float
            Manhattan distance (non-negative)
        """
        return manhattan_distance(self.data, other.data)

    def to_dict(self) -> dict[str, object]:
        """Serialize vector to dictionary for JSON storage.

        Returns
        -------
        dict[str, object]
            Dictionary with 'name', 'dimensions', 'data' keys
        """
        return {
            "name": self.name,
            "dimensions": self.dimensions,
            "data": self.data.tolist(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> HyperdimensionalVector:
        """Deserialize vector from dictionary.

        Parameters
        ----------
        data : dict[str, object]
            Dictionary with 'name', 'dimensions', 'data' keys

        Returns
        -------
        HyperdimensionalVector
            Reconstructed vector
        """
        return cls(
            name=str(data["name"]),
            dimensions=int(data["dimensions"]),
            data=np.array(data["data"], dtype=np.float64),
        )


def embed_entity(name: str, dimensions: int = DEFAULT_DIMENSIONS) -> HyperdimensionalVector:
    """Create deterministic hyperdimensional embedding for entity.

    Uses SHA256 hash of entity name as seed for reproducible random vector generation.
    All vectors are L2-normalized to unit length for consistent similarity metrics.

    This function is the core 20% that enables 80% of use cases:
    - Deterministic (same name → same vector always)
    - Fast (O(dimensions) time)
    - No external dependencies
    - Simple to test

    Parameters
    ----------
    name : str
        Entity name (e.g., "command:init", "job:developer", "outcome:fast-startup")
    dimensions : int, optional
        Vector dimensionality (default: 1000)

    Returns
    -------
    HyperdimensionalVector
        Normalized hyperdimensional vector

    Example
    -------
    >>> init_cmd = embed_entity("command:init")
    >>> check_cmd = embed_entity("command:check")
    >>> similarity = init_cmd.cosine_similarity(check_cmd)
    """
    # Create deterministic seed from entity name using SHA256
    hash_digest = hashlib.sha256(name.encode()).digest()
    seed_value = int.from_bytes(hash_digest[:4], byteorder="big")

    # Generate random vector with entity-specific seed
    rng = np.random.RandomState(seed_value)
    vector = rng.randn(dimensions)

    # L2 normalization (unit length)
    norm = np.linalg.norm(vector)
    if norm > 1e-10:
        vector = vector / norm

    return HyperdimensionalVector(name=name, data=vector, dimensions=dimensions)


def cosine_similarity(vec_a: Vector, vec_b: Vector) -> float:
    """Compute cosine similarity between two vectors.

    Returns value in [-1, 1] where:
    - 1.0: Identical vectors
    - 0.0: Orthogonal vectors
    - -1.0: Opposite vectors

    Parameters
    ----------
    vec_a : Vector
        First vector
    vec_b : Vector
        Second vector

    Returns
    -------
    float
        Cosine similarity in [-1, 1]

    Example
    -------
    >>> v1 = embed_entity("command:init").data
    >>> v2 = embed_entity("command:check").data
    >>> sim = cosine_similarity(v1, v2)
    """
    dot_product = np.dot(vec_a, vec_b)
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)

    if norm_a < 1e-10 or norm_b < 1e-10:
        return 0.0

    similarity = dot_product / (norm_a * norm_b)
    return float(np.clip(similarity, -1.0, 1.0))


def manhattan_distance(vec_a: Vector, vec_b: Vector) -> float:
    """Compute Manhattan (L1) distance between vectors.

    Manhattan distance is sum of absolute differences across all dimensions.

    Parameters
    ----------
    vec_a : Vector
        First vector
    vec_b : Vector
        Second vector

    Returns
    -------
    float
        Manhattan distance (non-negative)

    Example
    -------
    >>> v1 = embed_entity("job:developer").data
    >>> v2 = embed_entity("job:architect").data
    >>> dist = manhattan_distance(v1, v2)
    """
    return float(np.sum(np.abs(vec_a - vec_b)))


class EmbeddingCache:
    """Simple JSON-based cache for pre-computed embeddings.

    This replaces the complex RDF persistence with a minimal JSON approach
    that's sufficient for spec-kit's scale (100s of entities, not millions).

    Parameters
    ----------
    dimensions : int, optional
        Vector dimensionality (default: 1000)

    Attributes
    ----------
    embeddings : dict[str, HyperdimensionalVector]
        Cache of entity_name → vector mappings
    dimensions : int
        Vector dimensionality

    Example
    -------
    >>> cache = EmbeddingCache()
    >>> cache.add(embed_entity("command:init"))
    >>> cache.add(embed_entity("command:check"))
    >>> cache.save("embeddings.json")
    >>> loaded = EmbeddingCache.load("embeddings.json")
    """

    def __init__(self, dimensions: int = DEFAULT_DIMENSIONS) -> None:
        """Initialize empty embedding cache."""
        self.embeddings: dict[str, HyperdimensionalVector] = {}
        self.dimensions = dimensions

    def add(self, vector: HyperdimensionalVector) -> None:
        """Add vector to cache.

        Parameters
        ----------
        vector : HyperdimensionalVector
            Vector to cache
        """
        if vector.dimensions != self.dimensions:
            raise ValueError(
                f"Vector dimensions {vector.dimensions} don't match "
                f"cache dimensions {self.dimensions}"
            )
        self.embeddings[vector.name] = vector

    def get(self, name: str) -> HyperdimensionalVector | None:
        """Retrieve vector by name.

        Parameters
        ----------
        name : str
            Entity name

        Returns
        -------
        HyperdimensionalVector | None
            Cached vector or None if not found
        """
        return self.embeddings.get(name)

    def get_or_create(self, name: str) -> HyperdimensionalVector:
        """Get cached vector or create new one.

        Parameters
        ----------
        name : str
            Entity name

        Returns
        -------
        HyperdimensionalVector
            Cached or newly created vector
        """
        if name in self.embeddings:
            return self.embeddings[name]

        vector = embed_entity(name, dimensions=self.dimensions)
        self.add(vector)
        return vector

    def find_similar(
        self, query: HyperdimensionalVector, top_k: int = 5
    ) -> list[tuple[str, float]]:
        """Find most similar entities to query vector.

        Parameters
        ----------
        query : HyperdimensionalVector
            Query vector
        top_k : int, optional
            Number of top results to return (default: 5)

        Returns
        -------
        list[tuple[str, float]]
            List of (entity_name, similarity) sorted by similarity descending
        """
        similarities: list[tuple[str, float]] = []
        for name, vector in self.embeddings.items():
            sim = query.cosine_similarity(vector)
            similarities.append((name, sim))

        # Sort by similarity descending
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

    def save(self, filepath: Path | str) -> None:
        """Save cache to JSON file.

        Parameters
        ----------
        filepath : Path | str
            Output file path
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "dimensions": self.dimensions,
            "embeddings": [vec.to_dict() for vec in self.embeddings.values()],
        }

        with filepath.open("w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, filepath: Path | str) -> EmbeddingCache:
        """Load cache from JSON file.

        Parameters
        ----------
        filepath : Path | str
            Input file path

        Returns
        -------
        EmbeddingCache
            Loaded cache

        Raises
        ------
        FileNotFoundError
            If file doesn't exist
        ValueError
            If file format is invalid
        """
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"Embedding cache not found: {filepath}")

        with filepath.open() as f:
            data = json.load(f)

        cache = cls(dimensions=int(data["dimensions"]))

        for vec_data in data["embeddings"]:
            vector = HyperdimensionalVector.from_dict(vec_data)
            cache.add(vector)

        return cache

    def __len__(self) -> int:
        """Return number of cached embeddings."""
        return len(self.embeddings)

    def __contains__(self, name: str) -> bool:
        """Check if entity is cached."""
        return name in self.embeddings


def precompute_speckit_embeddings(dimensions: int = DEFAULT_DIMENSIONS) -> EmbeddingCache:
    """Pre-compute embeddings for all spec-kit entities.

    This function generates embeddings for:
    - 13 CLI commands
    - 5 JTBD jobs
    - 50+ measurable outcomes
    - Features, constraints, and quality metrics

    Parameters
    ----------
    dimensions : int, optional
        Vector dimensionality (default: 1000)

    Returns
    -------
    EmbeddingCache
        Cache with all spec-kit embeddings

    Example
    -------
    >>> cache = precompute_speckit_embeddings()
    >>> print(f"Pre-computed {len(cache)} embeddings")
    >>> cache.save("data/speckit-embeddings.json")
    """
    cache = EmbeddingCache(dimensions=dimensions)

    # Commands (13 total)
    commands = [
        "init",
        "check",
        "ggen-sync",
        "version",
        "pm-discover",
        "pm-conform",
        "pm-stats",
        "pm-filter",
        "pm-sample",
        "spiff-validate",
        "spiff-run-workflow",
        "build",
        "cache-clear",
    ]

    for cmd in commands:
        cache.add(embed_entity(f"command:{cmd}", dimensions))

    # Jobs (5 total)
    jobs = [
        "developer",
        "architect",
        "product-manager",
        "technical-writer",
        "quality-engineer",
    ]

    for job in jobs:
        cache.add(embed_entity(f"job:{job}", dimensions))

    # Outcomes (50+ total)
    outcomes = [
        # Performance
        "fast-startup",
        "fast-command",
        "fast-transform",
        "low-memory",
        "efficient-caching",
        # Reliability
        "reliable-builds",
        "reliable-tests",
        "reliable-transforms",
        "graceful-degradation",
        "error-recovery",
        # Quality
        "high-test-coverage",
        "type-safe",
        "well-documented",
        "linted-code",
        "secure-code",
        # Usability
        "intuitive-cli",
        "helpful-errors",
        "rich-output",
        "interactive-prompts",
        "comprehensive-help",
        # Maintainability
        "modular-design",
        "testable-code",
        "extensible-arch",
        "minimal-coupling",
        "clear-contracts",
        # Observability
        "full-tracing",
        "metric-collection",
        "error-tracking",
        "performance-monitoring",
        "telemetry-export",
        # Integration
        "git-integration",
        "github-integration",
        "ggen-integration",
        "rdf-integration",
        "pm4py-integration",
        # Development experience
        "fast-feedback",
        "easy-debugging",
        "good-defaults",
        "flexible-config",
        "reproducible-builds",
        # Documentation
        "living-docs",
        "versioned-docs",
        "searchable-docs",
        "example-driven",
        "tutorial-coverage",
    ]

    for outcome in outcomes:
        cache.add(embed_entity(f"outcome:{outcome}", dimensions))

    # Features (16 total)
    features = [
        "three-tier-architecture",
        "rdf-first-development",
        "constitutional-equation",
        "opentelemetry-integration",
        "process-mining",
        "workflow-automation",
        "type-safety",
        "quality-enforcement",
        "semantic-specifications",
        "jtbd-framework",
        "rich-cli",
        "interactive-init",
        "cache-management",
        "git-workflows",
        "github-api",
        "external-tools",
    ]

    for feature in features:
        cache.add(embed_entity(f"feature:{feature}", dimensions))

    # Constraints (12 total)
    constraints = [
        "no-side-effects-in-ops",
        "subprocess-only-in-runtime",
        "three-tier-principle",
        "no-circular-imports",
        "type-hints-required",
        "test-coverage-80-percent",
        "no-hardcoded-secrets",
        "path-validation-required",
        "list-based-commands",
        "graceful-otel-fallback",
        "dependency-minimalism",
        "optional-heavy-deps",
    ]

    for constraint in constraints:
        cache.add(embed_entity(f"constraint:{constraint}", dimensions))

    return cache


__all__ = [
    "DEFAULT_DIMENSIONS",
    "EmbeddingCache",
    "HyperdimensionalVector",
    "Vector",
    "cosine_similarity",
    "embed_entity",
    "manhattan_distance",
    "precompute_speckit_embeddings",
]
