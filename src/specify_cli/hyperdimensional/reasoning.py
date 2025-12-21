"""Semantic reasoning engine for hyperdimensional architectural decision-making.

This module implements a comprehensive reasoning framework based on hyperdimensional
computing (HDC) principles for architectural analysis, constraint satisfaction, and
logical inference in high-dimensional semantic spaces.

Architecture:
- Query expansion using nearest-neighbor search in semantic space
- Analogy-based reasoning (A:B :: C:D)
- Relationship chaining for transitive inference
- Constraint satisfaction with conflict detection
- Logical operations (AND, OR, NOT, IF-THEN) in vector space
- Consistency checking and redundancy detection

The reasoning engine operates on vectors in high-dimensional space (typically 10,000+
dimensions) where semantic similarity is preserved through geometric relationships.

Example:
    >>> import numpy as np
    >>> from specify_cli.hyperdimensional.reasoning import (
    ...     expand_query,
    ...     analogy_reasoning,
    ...     check_constraint_satisfaction,
    ... )
    >>>
    >>> # Expand query to find similar concepts
    >>> query_vec = np.random.randn(10000)
    >>> similar = expand_query(query_vec, vectors, k=10)
    >>>
    >>> # Analogy: microservices:scalability :: monolith:?
    >>> A = microservices_vec
    >>> B = scalability_vec
    >>> C = monolith_vec
    >>> D = analogy_reasoning(A, B, C)  # D ≈ simplicity_vec
    >>>
    >>> # Check design constraints
    >>> design = {"architecture": "microservices", "consistency": "eventual"}
    >>> constraints = [{"type": "requires", "if": "microservices", "then": "api_gateway"}]
    >>> satisfied = check_constraint_satisfaction(design, constraints)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import numpy as np
from numpy.typing import NDArray

logger = logging.getLogger(__name__)

# Type aliases for clarity
Vector = NDArray[np.float64]
VectorSet = list[Vector]
Constraint = dict[str, Any]
ConstraintSet = list[Constraint]
Design = dict[str, Any]


# ============================================================================
# Core Vector Operations
# ============================================================================


def normalize_vector(vec: Vector) -> Vector:
    """Normalize vector to unit length.

    Args:
        vec: Input vector to normalize

    Returns:
        Unit-length normalized vector

    Example:
        >>> v = np.array([3.0, 4.0])
        >>> normalized = normalize_vector(v)
        >>> np.linalg.norm(normalized)  # Should be 1.0
        1.0
    """
    norm = np.linalg.norm(vec)
    if norm < 1e-10:
        logger.warning("Near-zero vector encountered in normalization")
        return vec
    return vec / norm


def cosine_similarity(v1: Vector, v2: Vector) -> float:
    """Compute cosine similarity between two vectors.

    Args:
        v1: First vector
        v2: Second vector

    Returns:
        Cosine similarity in range [-1, 1]

    Example:
        >>> v1 = np.array([1.0, 0.0])
        >>> v2 = np.array([1.0, 0.0])
        >>> cosine_similarity(v1, v2)
        1.0
    """
    v1_norm = normalize_vector(v1)
    v2_norm = normalize_vector(v2)
    return float(np.dot(v1_norm, v2_norm))


def vector_distance(v1: Vector, v2: Vector, metric: str = "cosine") -> float:
    """Compute distance between vectors using specified metric.

    Args:
        v1: First vector
        v2: Second vector
        metric: Distance metric ("cosine", "euclidean", "manhattan")

    Returns:
        Distance value (lower = more similar)

    Raises:
        ValueError: If metric is not supported

    Example:
        >>> v1 = np.array([1.0, 0.0])
        >>> v2 = np.array([0.0, 1.0])
        >>> vector_distance(v1, v2, "cosine")
        1.0
    """
    if metric == "cosine":
        return 1.0 - cosine_similarity(v1, v2)
    if metric == "euclidean":
        return float(np.linalg.norm(v1 - v2))
    if metric == "manhattan":
        return float(np.sum(np.abs(v1 - v2)))
    msg = f"Unsupported distance metric: {metric}"
    raise ValueError(msg)


# ============================================================================
# Query Expansion
# ============================================================================


@dataclass
class QueryExpansionResult:
    """Result from query expansion operation.

    Attributes:
        original_query: Original query vector
        similar_vectors: List of similar vectors found
        similarities: Similarity scores for each result
        indices: Original indices in the vector database
        metadata: Optional metadata associated with results
    """

    original_query: Vector
    similar_vectors: VectorSet
    similarities: list[float]
    indices: list[int]
    metadata: dict[str, Any] = field(default_factory=dict)


def expand_query(
    query_vector: Vector,
    vector_database: VectorSet,
    k: int = 10,
    metric: str = "cosine",
    threshold: float | None = None,
) -> QueryExpansionResult:
    """Expand query using k-nearest neighbors in semantic space.

    Finds the k most similar vectors to the query vector, optionally filtering
    by similarity threshold. This enables semantic search and concept expansion.

    Args:
        query_vector: Query vector to expand
        vector_database: Database of vectors to search
        k: Number of neighbors to return
        metric: Distance metric to use
        threshold: Optional similarity threshold (only return results above this)

    Returns:
        QueryExpansionResult with similar vectors and metadata

    Example:
        >>> query = np.random.randn(100)
        >>> database = [np.random.randn(100) for _ in range(1000)]
        >>> result = expand_query(query, database, k=5)
        >>> len(result.similar_vectors)
        5
    """
    if not vector_database:
        return QueryExpansionResult(
            original_query=query_vector,
            similar_vectors=[],
            similarities=[],
            indices=[],
        )

    # Compute distances to all vectors
    distances = np.array([vector_distance(query_vector, v, metric) for v in vector_database])

    # Convert to similarities (for cosine metric)
    if metric == "cosine":
        similarities = 1.0 - distances
    else:
        # For other metrics, use inverse distance as similarity
        similarities = 1.0 / (1.0 + distances)

    # Get top-k indices
    top_k_indices = np.argsort(distances)[: min(k, len(vector_database))]

    # Filter by threshold if provided
    if threshold is not None:
        mask = similarities[top_k_indices] >= threshold
        top_k_indices = top_k_indices[mask]

    # Extract results
    similar_vectors = [vector_database[i] for i in top_k_indices]
    similar_scores = similarities[top_k_indices].tolist()

    logger.info(
        "Query expansion: found %d similar vectors (k=%d, threshold=%s)",
        len(similar_vectors),
        k,
        threshold,
    )

    return QueryExpansionResult(
        original_query=query_vector,
        similar_vectors=similar_vectors,
        similarities=similar_scores,
        indices=top_k_indices.tolist(),
        metadata={"metric": metric, "k": k, "threshold": threshold},
    )


def analogy_reasoning(vec_a: Vector, vec_b: Vector, vec_c: Vector) -> Vector:
    """Perform analogy-based reasoning: A:B :: C:D, solve for D.

    Uses vector arithmetic to find D such that the relationship between A and B
    is analogous to the relationship between C and D. This implements the classic
    word2vec analogy pattern: king - man + woman ≈ queen.

    Args:
        vec_a: First concept (A)
        vec_b: Related concept (B)
        vec_c: Third concept (C)

    Returns:
        Vector D such that A:B :: C:D

    Example:
        >>> # microservices:scalability :: monolith:?
        >>> A = microservices_vec
        >>> B = scalability_vec
        >>> C = monolith_vec
        >>> D = analogy_reasoning(A, B, C)
        >>> # D should be similar to "simplicity" or "maintainability"
    """
    # D = B - A + C
    # This encodes: "Take the relationship from A to B, and apply it to C"
    vec_d = vec_b - vec_a + vec_c

    logger.debug(
        "Analogy reasoning: ||B-A|| = %.3f, ||D-C|| = %.3f",
        np.linalg.norm(vec_b - vec_a),
        np.linalg.norm(vec_d - vec_c),
    )

    return normalize_vector(vec_d)


@dataclass
class RelationshipChain:
    """Represents a chain of relationships in semantic space.

    Attributes:
        concepts: Ordered list of concept vectors in the chain
        relations: List of relation vectors connecting concepts
        confidence_scores: Confidence score for each link
        path_length: Total length of the chain
    """

    concepts: VectorSet
    relations: VectorSet
    confidence_scores: list[float]
    path_length: float


def relationship_chaining(
    concept1: Vector,
    relation: Vector,
    concept2: Vector,
    vector_database: VectorSet,
    max_depth: int = 3,
) -> RelationshipChain:
    """Find transitive relationship chains between concepts.

    Discovers multi-hop relationships by chaining relation vectors. For example,
    finding that "service A" → "uses" → "database B" → "stores" → "customer data".

    Args:
        concept1: Starting concept
        relation: Relationship type (as vector)
        concept2: Target concept
        vector_database: Database of concept vectors
        max_depth: Maximum chain length to explore

    Returns:
        RelationshipChain connecting concepts via intermediate relations

    Example:
        >>> chain = relationship_chaining(
        ...     service_a_vec,
        ...     uses_relation_vec,
        ...     customer_data_vec,
        ...     database,
        ...     max_depth=3
        ... )
        >>> len(chain.concepts)  # Number of intermediate concepts
        4
    """
    # Simple implementation: direct path
    # In production, this would use graph search algorithms
    current = concept1
    concepts = [concept1]
    relations = []
    confidence_scores = []
    total_distance = 0.0

    for depth in range(max_depth):
        # Apply relation to current concept
        next_concept = current + relation

        # Find nearest neighbor in database
        if vector_database:
            distances = [vector_distance(next_concept, v) for v in vector_database]
            nearest_idx = int(np.argmin(distances))
            nearest_vec = vector_database[nearest_idx]
            distance = distances[nearest_idx]

            concepts.append(nearest_vec)
            relations.append(relation)
            confidence_scores.append(1.0 / (1.0 + distance))
            total_distance += distance

            # Check if we reached target
            if vector_distance(nearest_vec, concept2) < 0.1:
                logger.info("Relationship chain found at depth %d", depth + 1)
                break

            current = nearest_vec
        else:
            # No database, use simple vector addition
            concepts.append(next_concept)
            relations.append(relation)
            confidence_scores.append(0.5)
            current = next_concept

    return RelationshipChain(
        concepts=concepts,
        relations=relations,
        confidence_scores=confidence_scores,
        path_length=total_distance,
    )


def concept_refinement(
    broad_query: Vector,
    vector_database: VectorSet,
    num_refinements: int = 5,
    specialization_factor: float = 0.7,
) -> VectorSet:
    """Refine broad query into specialized sub-queries.

    Takes a general concept and generates more specific variants by moving
    in the direction of related specialized concepts.

    Args:
        broad_query: General query vector to refine
        vector_database: Database of concept vectors
        num_refinements: Number of specialized queries to generate
        specialization_factor: How much to specialize (0.0 = no change, 1.0 = full)

    Returns:
        List of specialized query vectors

    Example:
        >>> broad = architecture_vec  # General "architecture" concept
        >>> refined = concept_refinement(broad, database, num_refinements=5)
        >>> # refined might include: microservices_vec, event_driven_vec, etc.
    """
    if not vector_database:
        return [broad_query]

    # Find diverse neighbors using clustering
    expansion = expand_query(broad_query, vector_database, k=num_refinements * 3)

    # Select diverse subset using angular distance
    refined_queries = [broad_query]
    candidates = expansion.similar_vectors

    for candidate in candidates:
        # Check diversity: ensure it's different from existing refinements
        if (
            all(vector_distance(candidate, existing) > 0.3 for existing in refined_queries)
            and len(refined_queries) < num_refinements
        ):
            # Blend with original query to maintain some generality
            specialized = (
                specialization_factor * candidate + (1.0 - specialization_factor) * broad_query
            )
            refined_queries.append(normalize_vector(specialized))

    logger.info(
        "Concept refinement: generated %d specialized queries from broad query",
        len(refined_queries) - 1,
    )

    return refined_queries


# ============================================================================
# Logical Operations in Vector Space
# ============================================================================


def vector_and(v1: Vector, v2: Vector, method: str = "average") -> Vector:
    """Logical AND operation in vector space (intersection).

    Represents the semantic intersection of two concepts. Multiple methods
    are supported for different semantic interpretations.

    Args:
        v1: First vector
        v2: Second vector
        method: Intersection method ("average", "min", "product")

    Returns:
        Vector representing AND(v1, v2)

    Example:
        >>> secure = secure_vec
        >>> scalable = scalable_vec
        >>> secure_and_scalable = vector_and(secure, scalable)
    """
    if method == "average":
        # Average blends both concepts equally
        result = (v1 + v2) / 2.0
    elif method == "min":
        # Element-wise minimum (conservative intersection)
        result = np.minimum(v1, v2)
    elif method == "product":
        # Element-wise product (multiplicative combination)
        result = v1 * v2
    else:
        msg = f"Unsupported AND method: {method}"
        raise ValueError(msg)

    return normalize_vector(result)


def vector_or(v1: Vector, v2: Vector, method: str = "max") -> Vector:
    """Logical OR operation in vector space (union).

    Represents the semantic union of two concepts, capturing either or both.

    Args:
        v1: First vector
        v2: Second vector
        method: Union method ("max", "sum", "probabilistic")

    Returns:
        Vector representing OR(v1, v2)

    Example:
        >>> rest = rest_api_vec
        >>> graphql = graphql_vec
        >>> api_layer = vector_or(rest, graphql)
    """
    if method == "max":
        # Element-wise maximum (inclusive union)
        result = np.maximum(v1, v2)
    elif method == "sum":
        # Additive combination
        result = v1 + v2
    elif method == "probabilistic":
        # Probabilistic OR: P(A or B) = P(A) + P(B) - P(A)P(B)
        # Normalize to [0,1] range first
        v1_norm = (v1 - v1.min()) / (v1.max() - v1.min() + 1e-10)
        v2_norm = (v2 - v2.min()) / (v2.max() - v2.min() + 1e-10)
        result = v1_norm + v2_norm - v1_norm * v2_norm
    else:
        msg = f"Unsupported OR method: {method}"
        raise ValueError(msg)

    return normalize_vector(result)


def vector_not(vec: Vector, reference_space: Vector | None = None) -> Vector:
    """Logical NOT operation in vector space (complement).

    Computes the semantic negation of a concept. If reference_space is provided,
    negation is relative to that context; otherwise, simple inversion is used.

    Args:
        vec: Vector to negate
        reference_space: Optional reference context for negation

    Returns:
        Vector representing NOT(vec)

    Example:
        >>> synchronous = synchronous_vec
        >>> asynchronous = vector_not(synchronous)
    """
    if reference_space is not None:
        # Negation as orthogonal component in reference space
        # NOT(v) = reference - projection(v onto reference)
        projection = np.dot(vec, reference_space) / np.dot(reference_space, reference_space)
        result = reference_space - projection * vec
    else:
        # Simple inversion
        result = -vec

    return normalize_vector(result)


def vector_implies(v_if: Vector, v_then: Vector, strength: float = 0.8) -> tuple[Vector, float]:
    """Logical IF-THEN operation in vector space (conditional).

    Represents conditional probability/implication: IF v_if THEN v_then.
    The strength parameter controls how strongly the implication holds.

    Args:
        v_if: Condition vector (antecedent)
        v_then: Consequent vector
        strength: Implication strength in [0, 1]

    Returns:
        Tuple of (implication_vector, confidence)

    Example:
        >>> microservices = microservices_vec
        >>> needs_api_gateway = api_gateway_vec
        >>> rule, confidence = vector_implies(microservices, needs_api_gateway, strength=0.9)
    """
    # IF-THEN can be modeled as: NOT(IF) OR THEN
    # Or as weighted direction from IF toward THEN
    direction = v_then - v_if
    implication = v_if + strength * direction

    # Confidence based on semantic coherence
    confidence = float(np.clip(cosine_similarity(v_if, v_then), 0.0, 1.0))

    return normalize_vector(implication), confidence * strength


# ============================================================================
# Constraint Satisfaction
# ============================================================================


@dataclass
class ConstraintViolation:
    """Represents a constraint violation in a design.

    Attributes:
        constraint: The violated constraint
        design_element: Design element causing violation
        severity: Violation severity (0.0 = minor, 1.0 = critical)
        explanation: Human-readable explanation
        suggested_fix: Optional suggestion for resolution
    """

    constraint: Constraint
    design_element: str
    severity: float
    explanation: str
    suggested_fix: str | None = None


def check_constraint_satisfaction(
    design: Design,
    constraints: ConstraintSet,
    vector_db: dict[str, Vector] | None = None,
) -> tuple[bool, list[ConstraintViolation]]:
    """Check if design satisfies all constraints.

    Evaluates a design against a set of constraints, identifying violations
    and their severity. Supports multiple constraint types including requires,
    excludes, implies, and custom semantic constraints.

    Args:
        design: Design specification as key-value dict
        constraints: List of constraint specifications
        vector_db: Optional vector database for semantic constraint checking

    Returns:
        Tuple of (all_satisfied: bool, violations: list)

    Example:
        >>> design = {"architecture": "microservices", "data": "eventual_consistency"}
        >>> constraints = [
        ...     {"type": "requires", "if": "microservices", "then": "api_gateway"},
        ...     {"type": "excludes", "element": "global_state"},
        ... ]
        >>> satisfied, violations = check_constraint_satisfaction(design, constraints)
    """
    violations: list[ConstraintViolation] = []

    for constraint in constraints:
        constraint_type = constraint.get("type", "unknown")

        if constraint_type == "requires":
            # IF condition THEN requirement
            condition = constraint.get("if")
            requirement = constraint.get("then")

            if condition in design.values() and requirement not in design.values():
                violations.append(
                    ConstraintViolation(
                        constraint=constraint,
                        design_element=str(condition),
                        severity=0.9,
                        explanation=f"Design includes '{condition}' but missing required '{requirement}'",
                        suggested_fix=f"Add '{requirement}' to design",
                    )
                )

        elif constraint_type == "excludes":
            # Element must not be present
            excluded = constraint.get("element")
            if excluded in design.values():
                violations.append(
                    ConstraintViolation(
                        constraint=constraint,
                        design_element=str(excluded),
                        severity=0.8,
                        explanation=f"Design includes excluded element '{excluded}'",
                        suggested_fix=f"Remove '{excluded}' from design",
                    )
                )

        elif constraint_type == "one_of":
            # Exactly one element from set must be present
            options = constraint.get("options", [])
            matches = sum(1 for opt in options if opt in design.values())

            if matches == 0:
                violations.append(
                    ConstraintViolation(
                        constraint=constraint,
                        design_element="missing_choice",
                        severity=0.7,
                        explanation=f"Must select one of: {options}",
                        suggested_fix=f"Add one of {options} to design",
                    )
                )
            elif matches > 1:
                violations.append(
                    ConstraintViolation(
                        constraint=constraint,
                        design_element="multiple_choices",
                        severity=0.6,
                        explanation=f"Multiple selections from exclusive set: {options}",
                        suggested_fix="Keep only one option",
                    )
                )

        elif constraint_type == "semantic" and vector_db:
            # Semantic similarity constraint
            concept1 = constraint.get("concept1")
            concept2 = constraint.get("concept2")
            min_similarity = constraint.get("min_similarity", 0.7)

            if concept1 in vector_db and concept2 in vector_db:
                similarity = cosine_similarity(vector_db[concept1], vector_db[concept2])

                if similarity < min_similarity:
                    violations.append(
                        ConstraintViolation(
                            constraint=constraint,
                            design_element=f"{concept1}, {concept2}",
                            severity=1.0 - similarity,
                            explanation=f"Semantic conflict: '{concept1}' and '{concept2}' "
                            f"have low compatibility ({similarity:.2f} < {min_similarity:.2f})",
                            suggested_fix="Reconsider design choices for compatibility",
                        )
                    )

    all_satisfied = len(violations) == 0
    logger.info(
        "Constraint satisfaction check: %d/%d satisfied, %d violations",
        len(constraints) - len(violations),
        len(constraints),
        len(violations),
    )

    return all_satisfied, violations


def constraint_relaxation(
    design: Design,
    constraints: ConstraintSet,
    vector_db: dict[str, Vector] | None = None,
    max_iterations: int = 10,
) -> tuple[Design, list[str]]:
    """Relax constraints to make infeasible design feasible.

    Iteratively modifies design to satisfy constraints, prioritizing critical
    constraints and making minimal changes.

    Args:
        design: Initial (possibly infeasible) design
        constraints: Set of constraints to satisfy
        vector_db: Optional vector database for semantic reasoning
        max_iterations: Maximum relaxation iterations

    Returns:
        Tuple of (relaxed_design, list of changes made)

    Example:
        >>> design = {"architecture": "microservices"}  # Missing api_gateway
        >>> constraints = [{"type": "requires", "if": "microservices", "then": "api_gateway"}]
        >>> relaxed, changes = constraint_relaxation(design, constraints)
        >>> "api_gateway" in relaxed.values()
        True
    """
    current_design = design.copy()
    changes: list[str] = []

    for iteration in range(max_iterations):
        satisfied, violations = check_constraint_satisfaction(
            current_design, constraints, vector_db
        )

        if satisfied:
            logger.info("Design became feasible after %d relaxation iterations", iteration)
            break

        # Sort violations by severity (fix critical ones first)
        violations.sort(key=lambda v: v.severity, reverse=True)

        if not violations:
            break

        # Fix the most severe violation
        violation = violations[0]

        if violation.constraint.get("type") == "requires":
            # Add missing requirement
            requirement = violation.constraint.get("then")
            if requirement:
                # Find appropriate key for the requirement
                key = f"added_requirement_{len(changes)}"
                current_design[key] = requirement
                changes.append(f"Added required '{requirement}'")

        elif violation.constraint.get("type") == "excludes":
            # Remove excluded element
            excluded = violation.constraint.get("element")
            keys_to_remove = [k for k, v in current_design.items() if v == excluded]
            for key in keys_to_remove:
                del current_design[key]
                changes.append(f"Removed excluded '{excluded}'")

        # Prevent infinite loops
        if len(changes) > max_iterations:
            logger.warning("Constraint relaxation reached max changes limit")
            break

    return current_design, changes


def conflict_detection(specifications: list[Design]) -> list[tuple[int, int, str]]:
    """Detect conflicts between multiple specifications.

    Identifies contradictions between different specification documents,
    such as incompatible requirements or overlapping responsibilities.

    Args:
        specifications: List of specification documents

    Returns:
        List of (spec1_idx, spec2_idx, conflict_description) tuples

    Example:
        >>> spec1 = {"consistency": "strong", "availability": "100%"}
        >>> spec2 = {"consistency": "eventual", "partition_tolerance": "required"}
        >>> conflicts = conflict_detection([spec1, spec2])
        >>> len(conflicts)  # CAP theorem violation
        1
    """
    conflicts: list[tuple[int, int, str]] = []

    # Check pairwise conflicts
    for i, spec1 in enumerate(specifications):
        for j, spec2 in enumerate(specifications[i + 1 :], start=i + 1):
            # Check for direct contradictions (same key, different values)
            for key in set(spec1.keys()) & set(spec2.keys()):
                if spec1[key] != spec2[key]:
                    conflicts.append(
                        (
                            i,
                            j,
                            f"Contradictory values for '{key}': '{spec1[key]}' vs '{spec2[key]}'",
                        )
                    )

            # Check for semantic conflicts (would need vector DB for full implementation)
            # For now, check for known conflicting patterns
            if "strong_consistency" in spec1.values() and "high_availability" in spec2.values():
                conflicts.append(
                    (
                        i,
                        j,
                        "Potential CAP theorem violation: strong consistency vs high availability",
                    )
                )

    logger.info(
        "Conflict detection: found %d conflicts across %d specs",
        len(conflicts),
        len(specifications),
    )

    return conflicts


def consistency_checking(rules: list[dict[str, Any]]) -> list[str]:
    """Detect logical inconsistencies in a rule set.

    Identifies circular dependencies, contradictions, and unreachable states
    in a set of logical rules.

    Args:
        rules: List of rule specifications

    Returns:
        List of inconsistency descriptions

    Example:
        >>> rules = [
        ...     {"if": "A", "then": "B"},
        ...     {"if": "B", "then": "C"},
        ...     {"if": "C", "then": "NOT A"},  # Circular contradiction
        ... ]
        >>> inconsistencies = consistency_checking(rules)
        >>> len(inconsistencies)
        1
    """
    inconsistencies: list[str] = []

    # Build implication graph
    implications: dict[str, set[str]] = {}
    negations: dict[str, set[str]] = {}

    for rule in rules:
        antecedent = rule.get("if")
        consequent = rule.get("then")

        if not antecedent or not consequent:
            continue

        # Handle negations
        if isinstance(consequent, str) and consequent.startswith("NOT "):
            neg_consequent = consequent[4:]
            if antecedent not in negations:
                negations[antecedent] = set()
            negations[antecedent].add(neg_consequent)
        else:
            if antecedent not in implications:
                implications[antecedent] = set()
            implications[antecedent].add(consequent)

    # Check for circular implications with negations
    for start in implications:
        visited = {start}
        queue = [start]

        while queue:
            current = queue.pop(0)

            # Check if we can reach a negation of start
            if start in negations.get(current, set()):
                inconsistencies.append(
                    f"Circular contradiction: {start} implies {current} implies NOT {start}"
                )

            # Explore further implications
            for next_node in implications.get(current, set()):
                if next_node not in visited:
                    visited.add(next_node)
                    queue.append(next_node)

    # Check for direct contradictions
    for antecedent in implications:
        positives = implications[antecedent]
        negatives = negations.get(antecedent, set())

        conflicts = positives & negatives
        for conflict in conflicts:
            inconsistencies.append(
                f"Direct contradiction: {antecedent} implies both {conflict} and NOT {conflict}"
            )

    logger.info(
        "Consistency checking: found %d inconsistencies in %d rules",
        len(inconsistencies),
        len(rules),
    )

    return inconsistencies


# ============================================================================
# Utility Functions
# ============================================================================


def create_random_vector(dimensions: int = 10000, seed: int | None = None) -> Vector:
    """Create a random hyperdimensional vector.

    Args:
        dimensions: Vector dimensionality (default: 10000)
        seed: Optional random seed for reproducibility

    Returns:
        Random unit vector

    Example:
        >>> vec = create_random_vector(dimensions=100, seed=42)
        >>> vec.shape
        (100,)
    """
    if seed is not None:
        np.random.seed(seed)

    vec = np.random.randn(dimensions)
    return normalize_vector(vec)


def encode_concept(
    name: str,
    dimensions: int = 10000,
    seed: int | None = None,
) -> Vector:
    """Encode a named concept as a random hyperdimensional vector.

    Uses consistent hashing to ensure same concept always gets same vector.

    Args:
        name: Concept name
        dimensions: Vector dimensionality
        seed: Base random seed (modified by concept name hash)

    Returns:
        Consistent vector representation for the concept

    Example:
        >>> vec1 = encode_concept("microservices", dimensions=100)
        >>> vec2 = encode_concept("microservices", dimensions=100)
        >>> np.allclose(vec1, vec2)  # Same concept = same vector
        True
    """
    # Hash concept name to get consistent seed
    concept_seed = hash(name) % (2**31)
    if seed is not None:
        concept_seed = (concept_seed + seed) % (2**31)

    return create_random_vector(dimensions=dimensions, seed=concept_seed)


def bind_vectors(v1: Vector, v2: Vector, method: str = "circular_convolution") -> Vector:
    """Bind two vectors to create a composite representation.

    Binding creates a new vector that represents the combination of two concepts
    in a way that can be unbound later (lossy compression).

    Args:
        v1: First vector to bind
        v2: Second vector to bind
        method: Binding operation ("circular_convolution", "xor", "product")

    Returns:
        Bound vector representing the combination

    Example:
        >>> service = encode_concept("service")
        >>> database = encode_concept("database")
        >>> service_database = bind_vectors(service, database)
    """
    if method == "circular_convolution":
        # Use FFT-based circular convolution for efficiency
        from numpy.fft import fft, ifft

        result = np.real(ifft(fft(v1) * fft(v2)))
    elif method == "xor":
        # XOR-like operation: element-wise product with sign
        result = np.sign(v1) * np.sign(v2) * np.sqrt(np.abs(v1 * v2))
    elif method == "product":
        result = v1 * v2
    else:
        msg = f"Unsupported binding method: {method}"
        raise ValueError(msg)

    return normalize_vector(result)


def unbind_vectors(bound: Vector, v1: Vector, method: str = "circular_convolution") -> Vector:
    """Unbind a composite vector to retrieve the other component.

    Given bound = bind(v1, v2), unbind(bound, v1) ≈ v2.

    Args:
        bound: Bound composite vector
        v1: Known component vector
        method: Unbinding operation (must match binding method)

    Returns:
        Approximate reconstruction of the other component

    Example:
        >>> service = encode_concept("service")
        >>> database = encode_concept("database")
        >>> bound = bind_vectors(service, database)
        >>> retrieved = unbind_vectors(bound, service)
        >>> cosine_similarity(retrieved, database)  # Should be high
        0.95
    """
    if method == "circular_convolution":
        from numpy.fft import fft, ifft

        # Unbind using inverse: v2 ≈ ifft(fft(bound) / fft(v1))
        v1_fft = fft(v1)
        # Avoid division by zero
        v1_fft_safe = np.where(np.abs(v1_fft) < 1e-10, 1e-10, v1_fft)
        result = np.real(ifft(fft(bound) / v1_fft_safe))
    elif method in {"xor", "product"}:
        # For XOR and product, unbinding is the same as binding
        result = bind_vectors(bound, v1, method=method)
    else:
        msg = f"Unsupported unbinding method: {method}"
        raise ValueError(msg)

    return normalize_vector(result)


def permute_vector(vec: Vector, shift: int = 1) -> Vector:
    """Permute (rotate) vector elements.

    Useful for representing ordered sequences or temporal relationships.

    Args:
        vec: Vector to permute
        shift: Number of positions to rotate

    Returns:
        Permuted vector

    Example:
        >>> vec = np.array([1, 2, 3, 4, 5])
        >>> permuted = permute_vector(vec, shift=2)
        >>> permuted
        array([4, 5, 1, 2, 3])
    """
    return np.roll(vec, shift)
