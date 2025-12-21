"""Essential semantic reasoning operations (80/20 implementation).

This module provides the three core reasoning operations needed for 80% of use cases:
1. Similarity search - Find similar entities using nearest neighbor
2. Ranking - Sort entities by objective metrics
3. Constraint checking - Validate designs against constraints

Philosophy: Keep it stupid simple. No complex logic, no fancy indexing,
just the essential operations that solve real problems.

Example:
    >>> from specify_cli.hyperdimensional.reasoning_core import (
    ...     find_similar_entities,
    ...     rank_by_objective,
    ...     check_constraint_satisfied,
    ... )
    >>>
    >>> # Find similar commands
    >>> similar = find_similar_entities(query_vec, embeddings, k=5)
    >>>
    >>> # Rank features by value metric
    >>> ranked = rank_by_objective(features, lambda f: f["priority"] * f["impact"])
    >>>
    >>> # Check architectural constraint
    >>> satisfied = check_constraint_satisfied(design_vec, constraint_vecs)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

import numpy as np
from numpy.typing import NDArray

if TYPE_CHECKING:
    from collections.abc import Sequence

# Type aliases
Vector = NDArray[np.float64]
VectorDict = dict[str, Vector]


# ============================================================================
# Core Operation 1: Similarity Search (Nearest Neighbor)
# ============================================================================


def find_similar_entities(
    query_vector: Vector,
    embeddings: VectorDict,
    k: int = 5,
    threshold: float | None = None,
) -> list[tuple[str, float]]:
    """Find k most similar entities to query using cosine similarity.

    Uses simple linear search - no fancy indexing. Good enough for
    thousands of entities. If you need millions, add FAISS later.

    Parameters
    ----------
    query_vector : Vector
        Query vector to find similar entities for
    embeddings : VectorDict
        Dictionary mapping entity names to vectors
    k : int, optional
        Number of results to return (default: 5)
    threshold : float, optional
        Minimum similarity threshold (default: None = no threshold)

    Returns
    -------
    list[tuple[str, float]]
        List of (entity_name, similarity_score) sorted by similarity descending

    Example
    -------
    >>> query = hde.embed_command("init")
    >>> similar = find_similar_entities(query, all_embeddings, k=5)
    >>> for name, score in similar:
    ...     print(f"{name}: {score:.3f}")
    command:check: 0.856
    command:version: 0.742
    """
    if not embeddings:
        return []

    # Normalize query vector
    query_norm = _normalize(query_vector)

    # Compute similarity to all entities (linear search - simple!)
    similarities: list[tuple[str, float]] = []
    for name, vec in embeddings.items():
        vec_norm = _normalize(vec)
        similarity = float(np.dot(query_norm, vec_norm))

        # Apply threshold filter if specified
        if threshold is None or similarity >= threshold:
            similarities.append((name, similarity))

    # Sort by similarity descending
    similarities.sort(key=lambda x: x[1], reverse=True)

    # Return top k results
    return similarities[:k]


# ============================================================================
# Core Operation 2: Ranking by Objective
# ============================================================================


def rank_by_objective(
    entities: Sequence[dict[str, Any]],
    objective_fn: Callable[[dict[str, Any]], float],
    reverse: bool = True,
) -> list[dict[str, Any]]:
    """Rank entities by objective metric (simple sorting).

    No complex multi-objective optimization - just sort by a single
    objective function. Want multi-objective? Call this multiple times.

    Parameters
    ----------
    entities : Sequence[dict[str, Any]]
        List of entities to rank (any dict with attributes)
    objective_fn : Callable[[dict[str, Any]], float]
        Function that computes objective score for each entity
    reverse : bool, optional
        Sort descending (True) or ascending (False) (default: True)

    Returns
    -------
    list[dict[str, Any]]
        Entities sorted by objective score

    Example
    -------
    >>> features = [
    ...     {"name": "rdf-validation", "priority": 0.9, "cost": 3},
    ...     {"name": "three-tier", "priority": 1.0, "cost": 5},
    ... ]
    >>> # Rank by value/cost ratio
    >>> ranked = rank_by_objective(features, lambda f: f["priority"] / f["cost"])
    >>> ranked[0]["name"]
    'rdf-validation'
    """
    if not entities:
        return []

    # Compute scores
    scored = [(entity, objective_fn(entity)) for entity in entities]

    # Sort by score
    scored.sort(key=lambda x: x[1], reverse=reverse)

    # Return just the entities
    return [entity for entity, _score in scored]


# ============================================================================
# Core Operation 3: Constraint Satisfaction
# ============================================================================


def check_constraint_satisfied(
    design_vector: Vector,
    constraint_vectors: Sequence[Vector],
    threshold: float = 0.7,
) -> bool:
    """Check if design satisfies all constraints using dot product.

    Simple constraint checking: design must have high similarity (dot product)
    with ALL constraint vectors. No complex logic - just threshold checking.

    Parameters
    ----------
    design_vector : Vector
        Design to check
    constraint_vectors : Sequence[Vector]
        List of constraint vectors (ALL must be satisfied)
    threshold : float, optional
        Minimum dot product to consider constraint satisfied (default: 0.7)

    Returns
    -------
    bool
        True if all constraints satisfied, False otherwise

    Example
    -------
    >>> design = hde.embed_feature("microservices")
    >>> constraints = [
    ...     hde.embed_constraint("api-gateway-required"),
    ...     hde.embed_constraint("service-discovery-needed"),
    ... ]
    >>> satisfied = check_constraint_satisfied(design, constraints)
    >>> if not satisfied:
    ...     print("Design violates constraints!")
    """
    if not constraint_vectors:
        # No constraints = automatically satisfied
        return True

    # Normalize design vector once
    design_norm = _normalize(design_vector)

    # Check each constraint
    for constraint in constraint_vectors:
        constraint_norm = _normalize(constraint)
        similarity = float(np.dot(design_norm, constraint_norm))

        # If ANY constraint fails, return False immediately
        if similarity < threshold:
            return False

    # All constraints passed
    return True


def get_violated_constraints(
    design_vector: Vector,
    constraint_dict: dict[str, Vector],
    threshold: float = 0.7,
) -> list[tuple[str, float]]:
    """Identify which specific constraints are violated.

    Same as check_constraint_satisfied but returns details about violations
    instead of just True/False. Useful for debugging.

    Parameters
    ----------
    design_vector : Vector
        Design to check
    constraint_dict : dict[str, Vector]
        Dictionary mapping constraint names to vectors
    threshold : float, optional
        Minimum similarity to consider constraint satisfied (default: 0.7)

    Returns
    -------
    list[tuple[str, float]]
        List of (constraint_name, similarity_score) for violated constraints

    Example
    -------
    >>> design = hde.embed_feature("monolith")
    >>> constraints = {
    ...     "scalability": hde.embed_constraint("horizontal-scaling"),
    ...     "reliability": hde.embed_constraint("fault-tolerance"),
    ... }
    >>> violations = get_violated_constraints(design, constraints)
    >>> for name, score in violations:
    ...     print(f"Violated: {name} (score: {score:.3f})")
    """
    violations: list[tuple[str, float]] = []

    # Normalize design once
    design_norm = _normalize(design_vector)

    # Check each constraint
    for name, constraint in constraint_dict.items():
        constraint_norm = _normalize(constraint)
        similarity = float(np.dot(design_norm, constraint_norm))

        # If constraint violated, add to list
        if similarity < threshold:
            violations.append((name, similarity))

    # Sort by severity (lowest similarity = worst violation)
    violations.sort(key=lambda x: x[1])

    return violations


# ============================================================================
# Utility Functions (Internal)
# ============================================================================


def _normalize(vector: Vector) -> Vector:
    """Normalize vector to unit length (internal helper).

    Parameters
    ----------
    vector : Vector
        Vector to normalize

    Returns
    -------
    Vector
        Unit-length normalized vector
    """
    norm = np.linalg.norm(vector)
    if norm < 1e-10:
        return vector
    return vector / norm


# ============================================================================
# Bonus: Simple Entity Comparison
# ============================================================================


def compare_entities(
    entity1: Vector,
    entity2: Vector,
) -> float:
    """Compare two entities and return similarity score.

    Dead simple utility for pairwise comparison. Just cosine similarity.

    Parameters
    ----------
    entity1 : Vector
        First entity vector
    entity2 : Vector
        Second entity vector

    Returns
    -------
    float
        Similarity score in [-1, 1] (1 = identical, -1 = opposite)

    Example
    -------
    >>> cmd1 = hde.embed_command("init")
    >>> cmd2 = hde.embed_command("check")
    >>> similarity = compare_entities(cmd1, cmd2)
    >>> print(f"Commands are {similarity:.1%} similar")
    """
    norm1 = _normalize(entity1)
    norm2 = _normalize(entity2)
    return float(np.dot(norm1, norm2))


# ============================================================================
# Bonus: Batch Operations
# ============================================================================


def batch_compare(
    query_vector: Vector,
    entity_vectors: Sequence[Vector],
) -> NDArray[np.float64]:
    """Compare query to multiple entities efficiently.

    Returns raw similarity scores without sorting. Use when you need
    all scores and will do custom processing.

    Parameters
    ----------
    query_vector : Vector
        Query vector
    entity_vectors : Sequence[Vector]
        List of entity vectors to compare against

    Returns
    -------
    NDArray[np.float64]
        Array of similarity scores (same order as entity_vectors)

    Example
    -------
    >>> query = hde.embed_command("init")
    >>> all_cmds = [hde.embed_command(c) for c in ["check", "sync", "validate"]]
    >>> scores = batch_compare(query, all_cmds)
    >>> best_idx = scores.argmax()
    """
    if not entity_vectors:
        return np.array([], dtype=np.float64)

    # Normalize query once
    query_norm = _normalize(query_vector)

    # Stack all entity vectors and normalize
    entity_matrix = np.vstack([_normalize(v) for v in entity_vectors])

    # Batch dot product (fast!)
    similarities = entity_matrix @ query_norm

    return similarities


__all__ = [
    "find_similar_entities",
    "rank_by_objective",
    "check_constraint_satisfied",
    "get_violated_constraints",
    "compare_entities",
    "batch_compare",
]
