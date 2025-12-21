"""Specification reasoning for completeness, consistency, and refinement analysis.

This module provides tools for analyzing specifications to identify:
- Completeness gaps and missing requirements
- Semantic inconsistencies and contradictions
- Redundancy and unnecessary duplication
- Refinement opportunities and quality improvements
- Edge cases and potential oversight areas

Uses information-theoretic measures and semantic analysis in hyperdimensional space.

Example:
    >>> from specify_cli.hyperdimensional.specification_reasoning import (
    ...     specification_entropy,
    ...     identify_gaps,
    ...     check_semantic_consistency,
    ... )
    >>>
    >>> # Measure specification completeness
    >>> spec_vector = encode_specification(spec_document)
    >>> entropy = specification_entropy(spec_vector)  # High = incomplete
    >>>
    >>> # Find missing requirements
    >>> gaps = identify_gaps(spec_vector, requirements_db)
    >>>
    >>> # Check for contradictions
    >>> issues = check_semantic_consistency([spec1, spec2, spec3])
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import numpy as np
from numpy.typing import NDArray

from specify_cli.hyperdimensional.reasoning import (
    cosine_similarity,
)

logger = logging.getLogger(__name__)

# Type aliases
Vector = NDArray[np.float64]
VectorSet = list[Vector]
Specification = dict[str, Any]


# ============================================================================
# Completeness Analysis
# ============================================================================


def specification_entropy(
    spec_vector: Vector,
    reference_vectors: VectorSet | None = None,
) -> float:
    """Measure specification entropy (incompleteness indicator).

    Higher entropy indicates more uncertainty/incompleteness in the specification.
    Lower entropy suggests a well-constrained, complete specification.

    Args:
        spec_vector: Specification vector
        reference_vectors: Optional reference specifications for comparison

    Returns:
        Entropy value (higher = more incomplete)

    Example:
        >>> spec = encode_specification(document)
        >>> entropy = specification_entropy(spec)
        >>> if entropy > 3.0:
        ...     print("High uncertainty - specification likely incomplete")
    """
    # Compute entropy from vector component distribution
    # Normalize to probability distribution
    vec_abs = np.abs(spec_vector)
    prob_dist = vec_abs / (np.sum(vec_abs) + 1e-10)

    # Shannon entropy: H(X) = -Σ p(x) log p(x)
    # Filter out zeros to avoid log(0)
    prob_dist = prob_dist[prob_dist > 1e-10]
    entropy = -np.sum(prob_dist * np.log2(prob_dist + 1e-10))

    # If reference vectors provided, compute relative entropy
    if reference_vectors:
        # Compare to average entropy of complete specifications
        reference_entropies = [specification_entropy(ref) for ref in reference_vectors]
        avg_ref_entropy = np.mean(reference_entropies)

        # Relative entropy (higher = more incomplete than references)
        relative_entropy = entropy / (avg_ref_entropy + 1e-10)

        logger.debug(
            "Specification entropy: %.3f (relative: %.3f)",
            entropy,
            relative_entropy,
        )

        return float(relative_entropy)

    logger.debug("Specification entropy: %.3f", entropy)
    return float(entropy)


@dataclass
class SpecificationGap:
    """Represents a gap or missing element in a specification.

    Attributes:
        gap_type: Type of gap (requirement, constraint, edge_case, etc.)
        description: Human-readable description
        severity: Severity score (0.0 = minor, 1.0 = critical)
        suggested_additions: Suggested content to fill gap
        related_concepts: Related concepts that should be addressed
    """

    gap_type: str
    description: str
    severity: float
    suggested_additions: list[str] = field(default_factory=list)
    related_concepts: list[str] = field(default_factory=list)


def identify_gaps(
    spec_vector: Vector,
    requirements_db: dict[str, Vector],
    coverage_threshold: float = 0.6,
) -> list[SpecificationGap]:
    """Identify gaps and missing requirements in specification.

    Compares specification against a database of known requirements to find
    uncovered areas.

    Args:
        spec_vector: Specification vector
        requirements_db: Database mapping requirement names to vectors
        coverage_threshold: Minimum similarity to consider requirement covered

    Returns:
        List of identified gaps

    Example:
        >>> spec = encode_specification(doc)
        >>> requirements = load_requirements_database()
        >>> gaps = identify_gaps(spec, requirements, coverage_threshold=0.7)
        >>> critical_gaps = [g for g in gaps if g.severity > 0.8]
    """
    gaps: list[SpecificationGap] = []

    # Check coverage of each requirement
    for req_name, req_vector in requirements_db.items():
        similarity = cosine_similarity(spec_vector, req_vector)

        if similarity < coverage_threshold:
            # Requirement not sufficiently covered
            severity = 1.0 - similarity  # Higher severity for lower coverage

            gaps.append(
                SpecificationGap(
                    gap_type="missing_requirement",
                    description=f"Requirement '{req_name}' insufficiently covered "
                    f"(coverage: {similarity:.2f})",
                    severity=severity,
                    suggested_additions=[
                        f"Add explicit handling of {req_name}",
                        f"Define constraints for {req_name}",
                    ],
                    related_concepts=[req_name],
                )
            )

    # Sort by severity
    gaps.sort(key=lambda g: g.severity, reverse=True)

    logger.info(
        "Gap analysis: found %d gaps (threshold: %.2f)",
        len(gaps),
        coverage_threshold,
    )

    return gaps


def generate_edge_cases(
    spec_vector: Vector,
    vector_db: dict[str, Vector] | None = None,
    num_cases: int = 10,
) -> list[dict[str, Any]]:
    """Generate potential edge cases that specification should address.

    Uses semantic exploration to identify boundary conditions and corner
    cases that may not be explicitly covered.

    Args:
        spec_vector: Specification vector
        vector_db: Optional database of known edge case patterns
        num_cases: Number of edge cases to generate

    Returns:
        List of edge case descriptions

    Example:
        >>> edge_cases = generate_edge_cases(spec, num_cases=5)
        >>> for case in edge_cases:
        ...     print(f"Edge case: {case['description']}")
    """
    edge_cases = []

    # Common edge case patterns
    edge_case_patterns = [
        "empty_input",
        "null_value",
        "maximum_size",
        "minimum_size",
        "boundary_value",
        "concurrent_access",
        "network_failure",
        "timeout",
        "duplicate_request",
        "invalid_format",
    ]

    if vector_db:
        # Use vector DB to find relevant edge cases
        for pattern in edge_case_patterns[:num_cases]:
            if pattern in vector_db:
                similarity = cosine_similarity(spec_vector, vector_db[pattern])

                edge_cases.append(
                    {
                        "pattern": pattern,
                        "description": f"Edge case: {pattern.replace('_', ' ')}",
                        "coverage": similarity,
                        "priority": 1.0 - similarity,  # Low coverage = high priority
                        "test_scenarios": [
                            f"Test with {pattern.replace('_', ' ')}",
                            f"Verify behavior under {pattern.replace('_', ' ')} condition",
                        ],
                    }
                )
    else:
        # Generate synthetic edge cases
        for _i, pattern in enumerate(edge_case_patterns[:num_cases]):
            edge_cases.append(
                {
                    "pattern": pattern,
                    "description": f"Edge case: {pattern.replace('_', ' ')}",
                    "coverage": 0.5,  # Unknown coverage
                    "priority": 0.5,
                    "test_scenarios": [f"Test with {pattern.replace('_', ' ')}"],
                }
            )

    # Sort by priority
    edge_cases.sort(key=lambda c: c["priority"], reverse=True)

    logger.info("Generated %d edge cases", len(edge_cases))

    return edge_cases


def suggest_clarifications(
    spec: Specification,
    ambiguity_threshold: float = 0.3,
) -> list[dict[str, Any]]:
    """Identify ambiguous parts of specification needing clarification.

    Analyzes specification for vague language, undefined terms, and
    ambiguous requirements.

    Args:
        spec: Specification document as dict
        ambiguity_threshold: Threshold for flagging ambiguity

    Returns:
        List of clarification suggestions

    Example:
        >>> clarifications = suggest_clarifications(spec)
        >>> for clarification in clarifications:
        ...     print(f"Clarify: {clarification['element']}")
    """
    clarifications = []

    # Ambiguity indicators (would use NLP in production)
    ambiguous_terms = {
        "maybe",
        "possibly",
        "approximately",
        "around",
        "should",
        "could",
        "might",
        "generally",
        "usually",
        "typically",
    }

    vague_terms = {
        "fast",
        "slow",
        "large",
        "small",
        "many",
        "few",
        "high",
        "low",
        "good",
        "bad",
    }

    # Scan specification text
    for key, value in spec.items():
        if isinstance(value, str):
            text_lower = value.lower()

            # Check for ambiguous language
            found_ambiguous = [term for term in ambiguous_terms if term in text_lower]
            found_vague = [term for term in vague_terms if term in text_lower]

            if found_ambiguous:
                clarifications.append(
                    {
                        "element": key,
                        "type": "ambiguous_language",
                        "issue": f"Contains ambiguous terms: {', '.join(found_ambiguous)}",
                        "suggestion": "Replace with specific, measurable criteria",
                        "priority": 0.8,
                    }
                )

            if found_vague:
                clarifications.append(
                    {
                        "element": key,
                        "type": "vague_qualifier",
                        "issue": f"Contains vague qualifiers: {', '.join(found_vague)}",
                        "suggestion": "Define precise thresholds or metrics",
                        "priority": 0.7,
                    }
                )

            # Check for missing quantification
            if any(
                indicator in text_lower
                for indicator in ["performance", "scalability", "reliability"]
            ):
                if not any(char.isdigit() for char in value):
                    clarifications.append(
                        {
                            "element": key,
                            "type": "missing_quantification",
                            "issue": "Quality attribute lacks quantitative target",
                            "suggestion": "Add specific metrics (e.g., '99.9% uptime', '<100ms latency')",
                            "priority": 0.9,
                        }
                    )

    # Sort by priority
    clarifications.sort(key=lambda c: c["priority"], reverse=True)

    logger.info("Identified %d areas needing clarification", len(clarifications))

    return clarifications


# ============================================================================
# Consistency Checking
# ============================================================================


@dataclass
class ConsistencyIssue:
    """Represents a consistency issue between specifications.

    Attributes:
        issue_type: Type of issue (contradiction, conflict, incompatibility)
        description: Detailed description
        affected_specs: Indices or names of affected specifications
        severity: Issue severity (0.0 to 1.0)
        resolution_suggestions: Suggested resolutions
    """

    issue_type: str
    description: str
    affected_specs: list[str | int]
    severity: float
    resolution_suggestions: list[str] = field(default_factory=list)


def check_semantic_consistency(
    specs: list[Specification],
    vector_db: dict[str, Vector] | None = None,
) -> list[ConsistencyIssue]:
    """Check semantic consistency across multiple specifications.

    Identifies contradictions, conflicts, and incompatibilities between
    different specification documents.

    Args:
        specs: List of specification documents
        vector_db: Optional vector database for semantic analysis

    Returns:
        List of consistency issues

    Example:
        >>> issues = check_semantic_consistency([spec1, spec2, spec3])
        >>> contradictions = [i for i in issues if i.issue_type == "contradiction"]
    """
    issues: list[ConsistencyIssue] = []

    # Check pairwise consistency
    for i, spec1 in enumerate(specs):
        for j, spec2 in enumerate(specs[i + 1 :], start=i + 1):
            # Check for direct contradictions (same key, conflicting values)
            shared_keys = set(spec1.keys()) & set(spec2.keys())

            for key in shared_keys:
                val1 = spec1[key]
                val2 = spec2[key]

                # Check for contradictory values
                if isinstance(val1, str) and isinstance(val2, str):
                    # Semantic contradiction detection (simplified)
                    contradictory_pairs = [
                        ("synchronous", "asynchronous"),
                        ("strong", "eventual"),
                        ("centralized", "distributed"),
                        ("required", "optional"),
                    ]

                    val1_lower = val1.lower()
                    val2_lower = val2.lower()

                    for term1, term2 in contradictory_pairs:
                        if (term1 in val1_lower and term2 in val2_lower) or (
                            term2 in val1_lower and term1 in val2_lower
                        ):
                            issues.append(
                                ConsistencyIssue(
                                    issue_type="contradiction",
                                    description=f"Contradictory values for '{key}': "
                                    f"'{val1}' vs '{val2}'",
                                    affected_specs=[i, j],
                                    severity=0.9,
                                    resolution_suggestions=[
                                        f"Choose one approach for '{key}'",
                                        "Add conditional logic to handle both cases",
                                        "Split into separate specifications",
                                    ],
                                )
                            )

                elif val1 != val2 and not isinstance(val1, (dict, list)):
                    # Different scalar values for same key
                    issues.append(
                        ConsistencyIssue(
                            issue_type="conflict",
                            description=f"Conflicting values for '{key}': {val1} vs {val2}",
                            affected_specs=[i, j],
                            severity=0.7,
                            resolution_suggestions=[
                                "Determine which value is correct",
                                "Rename one key to differentiate contexts",
                            ],
                        )
                    )

    # Check for logical inconsistencies across all specs
    all_requirements = []
    for i, spec in enumerate(specs):
        for key, value in spec.items():
            all_requirements.append((i, key, value))

    # Detect circular dependencies
    # (Simplified - full implementation would build dependency graph)

    logger.info("Consistency check: found %d issues across %d specs", len(issues), len(specs))

    return issues


def resolve_conflicts(
    conflicting_specs: list[Specification],
    resolution_strategy: str = "merge",
) -> Specification:
    """Propose resolution for conflicting specifications.

    Args:
        conflicting_specs: List of specifications with conflicts
        resolution_strategy: Strategy to use ("merge", "prioritize_first", "strict")

    Returns:
        Resolved specification

    Example:
        >>> resolved = resolve_conflicts([spec1, spec2], resolution_strategy="merge")
    """
    if not conflicting_specs:
        return {}

    if resolution_strategy == "merge":
        # Merge all specs, later values override earlier ones
        resolved: Specification = {}
        for spec in conflicting_specs:
            resolved.update(spec)

    elif resolution_strategy == "prioritize_first":
        # First spec takes precedence
        resolved = conflicting_specs[0].copy()

    elif resolution_strategy == "strict":
        # Only include non-conflicting keys
        resolved = {}
        key_values: dict[str, list[Any]] = {}

        # Collect all values for each key
        for spec in conflicting_specs:
            for key, value in spec.items():
                if key not in key_values:
                    key_values[key] = []
                key_values[key].append(value)

        # Only include keys with consistent values
        for key, values in key_values.items():
            if len({str(v) for v in values}) == 1:
                resolved[key] = values[0]

    else:
        msg = f"Unsupported resolution strategy: {resolution_strategy}"
        raise ValueError(msg)

    logger.info(
        "Conflict resolution: merged %d specs using '%s' strategy",
        len(conflicting_specs),
        resolution_strategy,
    )

    return resolved


def detect_redundancy(specs: list[Specification]) -> list[dict[str, Any]]:
    """Detect redundant or duplicate content across specifications.

    Args:
        specs: List of specifications to analyze

    Returns:
        List of redundancy reports

    Example:
        >>> redundancies = detect_redundancy([spec1, spec2, spec3])
        >>> for redundancy in redundancies:
        ...     print(f"Duplicate: {redundancy['content']}")
    """
    redundancies = []

    # Build content index
    content_index: dict[str, list[tuple[int, str]]] = {}

    for i, spec in enumerate(specs):
        for key, value in spec.items():
            value_str = str(value)

            if value_str not in content_index:
                content_index[value_str] = []

            content_index[value_str].append((i, key))

    # Identify duplicates
    for content, locations in content_index.items():
        if len(locations) > 1:
            redundancies.append(
                {
                    "content": content[:100] + "..." if len(content) > 100 else content,
                    "occurrences": len(locations),
                    "locations": [{"spec_index": idx, "key": key} for idx, key in locations],
                    "recommendation": "Consolidate into single definition",
                }
            )

    logger.info("Redundancy detection: found %d duplicates", len(redundancies))

    return redundancies


# ============================================================================
# Refinement Suggestions
# ============================================================================


@dataclass
class RefinementSuggestion:
    """Represents a suggestion for improving specification.

    Attributes:
        suggestion_type: Type of suggestion (clarify, extend, restructure, etc.)
        description: Detailed description
        current_state: Current specification element
        suggested_state: Suggested improvement
        impact: Expected impact on quality (0.0 to 1.0)
    """

    suggestion_type: str
    description: str
    current_state: str
    suggested_state: str
    impact: float


def suggest_improvements(
    spec: Specification,
    quality_metrics: dict[str, float] | None = None,
) -> list[RefinementSuggestion]:
    """Suggest improvements to specification quality.

    Args:
        spec: Specification to improve
        quality_metrics: Optional current quality scores

    Returns:
        List of refinement suggestions

    Example:
        >>> suggestions = suggest_improvements(spec)
        >>> high_impact = [s for s in suggestions if s.impact > 0.7]
    """
    suggestions: list[RefinementSuggestion] = []

    # Check for missing standard sections
    standard_sections = {
        "requirements",
        "constraints",
        "assumptions",
        "dependencies",
        "success_criteria",
    }

    missing_sections = standard_sections - set(spec.keys())

    for section in missing_sections:
        suggestions.append(
            RefinementSuggestion(
                suggestion_type="add_section",
                description=f"Add '{section}' section for completeness",
                current_state=f"Missing '{section}' section",
                suggested_state=f"Include explicit '{section}' section with details",
                impact=0.8,
            )
        )

    # Check for vague requirements
    for key, value in spec.items():
        if isinstance(value, str):
            # Check for quantifiable but unquantified attributes
            if any(
                term in value.lower()
                for term in ["performance", "scalability", "reliability", "quality"]
            ) and not any(char.isdigit() for char in value):
                suggestions.append(
                    RefinementSuggestion(
                        suggestion_type="add_metrics",
                        description=f"Add quantitative metrics to '{key}'",
                        current_state=value,
                        suggested_state=f"{value} (e.g., specify target values)",
                        impact=0.9,
                    )
                )

    # Sort by impact
    suggestions.sort(key=lambda s: s.impact, reverse=True)

    logger.info("Generated %d improvement suggestions", len(suggestions))

    return suggestions


def quality_metrics_impact(
    spec: Specification,
    proposed_change: dict[str, Any],
) -> dict[str, float]:
    """Estimate impact of proposed change on quality metrics.

    Args:
        spec: Current specification
        proposed_change: Proposed modifications

    Returns:
        Dict mapping quality dimensions to impact scores

    Example:
        >>> change = {"add_section": "security_requirements"}
        >>> impact = quality_metrics_impact(spec, change)
        >>> impact["completeness"]
        0.15
    """
    # Baseline metrics
    {
        "completeness": len(spec) / 20.0,  # Assume 20 sections is "complete"
        "clarity": 0.5,  # Default medium clarity
        "specificity": 0.5,  # Default medium specificity
    }

    # Estimate impact of change
    impact = {}

    if "add_section" in proposed_change:
        impact["completeness"] = 1.0 / 20.0  # Each section adds ~5%

    if "add_metrics" in proposed_change:
        impact["specificity"] = 0.1  # Quantification improves specificity

    if "clarify" in proposed_change:
        impact["clarity"] = 0.1  # Clarification improves clarity

    if "remove_redundancy" in proposed_change:
        impact["clarity"] = 0.05  # Removing duplication improves clarity

    logger.debug("Quality impact analysis: %s", impact)

    return impact


def complexity_analysis(spec: Specification) -> dict[str, float]:
    """Analyze architectural complexity from specification.

    Args:
        spec: Specification document

    Returns:
        Dict with complexity metrics

    Example:
        >>> complexity = complexity_analysis(spec)
        >>> if complexity["overall"] > 0.7:
        ...     print("High complexity - consider simplification")
    """
    # Compute various complexity metrics
    metrics = {}

    # Structural complexity (number of sections/elements)
    num_elements = len(spec)
    metrics["structural"] = min(num_elements / 50.0, 1.0)  # 50+ elements = max complexity

    # Dependency complexity (count of dependencies mentioned)
    dependency_count = sum(
        1 for value in spec.values() if isinstance(value, str) and "depend" in value.lower()
    )
    metrics["dependencies"] = min(dependency_count / 10.0, 1.0)

    # Nesting depth (for nested dicts/lists)
    def max_depth(obj: Any, current_depth: int = 0) -> int:
        if isinstance(obj, dict):
            return max(
                (max_depth(v, current_depth + 1) for v in obj.values()), default=current_depth
            )
        if isinstance(obj, list):
            return max((max_depth(item, current_depth + 1) for item in obj), default=current_depth)
        return current_depth

    depth = max_depth(spec)
    metrics["nesting"] = min(depth / 5.0, 1.0)  # 5+ levels = max complexity

    # Overall complexity (weighted average)
    metrics["overall"] = (
        0.4 * metrics["structural"] + 0.3 * metrics["dependencies"] + 0.3 * metrics["nesting"]
    )

    logger.debug("Complexity analysis: overall=%.2f", metrics["overall"])

    return metrics
