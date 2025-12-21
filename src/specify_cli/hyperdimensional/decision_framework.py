"""Architectural decision framework for design space exploration and trade-off analysis.

This module implements comprehensive tools for architectural decision-making including:
- Design space exploration and alternative generation
- Multi-objective optimization and Pareto frontier analysis
- Risk assessment and mitigation strategy identification
- Trade-off visualization and sensitivity analysis

The framework operates on hyperdimensional vector representations of designs and
uses information-theoretic principles for optimization and ranking.

Example:
    >>> from specify_cli.hyperdimensional.decision_framework import (
    ...     generate_design_alternatives,
    ...     pareto_frontier,
    ...     identify_risks,
    ... )
    >>>
    >>> # Generate design alternatives from requirements
    >>> requirements = {"scalability": 0.9, "simplicity": 0.7}
    >>> alternatives = generate_design_alternatives(requirements, count=20)
    >>>
    >>> # Find Pareto-optimal designs
    >>> objectives = ["performance", "cost", "maintainability"]
    >>> optimal = pareto_frontier(alternatives, objectives)
    >>>
    >>> # Assess risks for a design
    >>> risks = identify_risks(alternatives[0])
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import numpy as np
from numpy.typing import NDArray

from specify_cli.hyperdimensional.reasoning import (
    cosine_similarity,
    normalize_vector,
)

logger = logging.getLogger(__name__)

# Type aliases
Vector = NDArray[np.float64]
VectorSet = list[Vector]
ObjectiveFunction = Callable[[Vector], float]


# ============================================================================
# Design Space Exploration
# ============================================================================


@dataclass
class DesignAlternative:
    """Represents a design alternative in the design space.

    Attributes:
        vector: Hyperdimensional vector representation
        metadata: Design metadata (name, description, etc.)
        quality_scores: Scores on various quality dimensions
        feasibility: Feasibility score (0.0 = infeasible, 1.0 = fully feasible)
    """

    vector: Vector
    metadata: dict[str, Any] = field(default_factory=dict)
    quality_scores: dict[str, float] = field(default_factory=dict)
    feasibility: float = 1.0


def generate_design_alternatives(
    requirements: dict[str, float],
    vector_db: dict[str, Vector] | None = None,
    count: int = 20,
    diversity_weight: float = 0.5,
    dimensions: int = 10000,
) -> list[DesignAlternative]:
    """Generate diverse design alternatives from requirements.

    Creates a set of design alternatives that satisfy requirements while
    maximizing diversity in the design space. Uses vector combination
    and perturbation to explore the space efficiently.

    Args:
        requirements: Dict mapping requirement names to importance weights
        vector_db: Optional database of concept vectors
        count: Number of alternatives to generate
        diversity_weight: Weight for diversity vs requirement satisfaction
        dimensions: Vector dimensionality for new designs

    Returns:
        List of DesignAlternative objects

    Example:
        >>> requirements = {"scalability": 0.9, "security": 0.8, "cost": 0.3}
        >>> alternatives = generate_design_alternatives(requirements, count=10)
        >>> len(alternatives)
        10
    """
    alternatives: list[DesignAlternative] = []

    # Create base requirement vector
    if vector_db:
        # Combine requirement vectors with weights
        req_vectors = [
            weight * vector_db.get(req, np.random.randn(dimensions))
            for req, weight in requirements.items()
        ]
        base_vector = normalize_vector(np.sum(req_vectors, axis=0))
    else:
        # Random base if no vector DB
        base_vector = normalize_vector(np.random.randn(dimensions))

    # Generate alternatives by perturbing base design
    for i in range(count):
        # Create perturbation with controlled randomness
        perturbation = np.random.randn(len(base_vector))
        perturbation = normalize_vector(perturbation)

        # Blend base with perturbation (diversity vs requirements trade-off)
        blend_factor = diversity_weight * (i / max(count - 1, 1))
        design_vector = normalize_vector(
            (1.0 - blend_factor) * base_vector + blend_factor * perturbation
        )

        # Compute quality scores
        quality_scores = {}
        for req, weight in requirements.items():
            if vector_db and req in vector_db:
                quality_scores[req] = float(cosine_similarity(design_vector, vector_db[req]))
            else:
                # Synthetic score based on vector properties
                quality_scores[req] = float(np.clip(weight * np.random.random(), 0.0, 1.0))

        alternatives.append(
            DesignAlternative(
                vector=design_vector,
                metadata={"index": i, "requirements": requirements},
                quality_scores=quality_scores,
                feasibility=1.0,
            )
        )

    logger.info(
        "Generated %d design alternatives with diversity_weight=%.2f",
        len(alternatives),
        diversity_weight,
    )

    return alternatives


def evaluate_design_option(
    design: DesignAlternative,
    objectives: dict[str, ObjectiveFunction],
    weights: dict[str, float] | None = None,
) -> float:
    """Evaluate design using multiple objective functions.

    Computes a weighted aggregate score for a design based on multiple
    objectives. Each objective is a function that scores the design.

    Args:
        design: Design alternative to evaluate
        objectives: Dict mapping objective names to scoring functions
        weights: Optional weights for each objective (default: equal weights)

    Returns:
        Weighted aggregate score (higher is better)

    Example:
        >>> def performance(d): return d.quality_scores.get("speed", 0.5)
        >>> def cost(d): return 1.0 - d.quality_scores.get("price", 0.5)
        >>> objectives = {"performance": performance, "cost": cost}
        >>> score = evaluate_design_option(design, objectives)
    """
    if weights is None:
        weights = {name: 1.0 / len(objectives) for name in objectives}

    total_score = 0.0
    for name, objective_fn in objectives.items():
        score = objective_fn(design)
        weight = weights.get(name, 1.0 / len(objectives))
        total_score += weight * score

    return total_score


def rank_alternatives(
    designs: list[DesignAlternative],
    objectives: dict[str, ObjectiveFunction],
    weights: dict[str, float] | None = None,
) -> list[tuple[DesignAlternative, float]]:
    """Rank design alternatives by weighted objective scores.

    Args:
        designs: List of design alternatives
        objectives: Dict of objective functions
        weights: Optional weights for each objective

    Returns:
        List of (design, score) tuples sorted by score (descending)

    Example:
        >>> ranked = rank_alternatives(designs, objectives)
        >>> best_design = ranked[0][0]
        >>> best_score = ranked[0][1]
    """
    scored_designs = [
        (design, evaluate_design_option(design, objectives, weights)) for design in designs
    ]

    # Sort by score descending
    scored_designs.sort(key=lambda x: x[1], reverse=True)

    logger.info(
        "Ranked %d alternatives, best score: %.3f",
        len(designs),
        scored_designs[0][1] if scored_designs else 0.0,
    )

    return scored_designs


def sensitivity_analysis(
    design: DesignAlternative,
    perturbation_magnitude: float = 0.1,
    num_samples: int = 100,
    objectives: dict[str, ObjectiveFunction] | None = None,
) -> dict[str, float]:
    """Analyze design stability under perturbations.

    Tests how sensitive a design's quality is to small changes, identifying
    which aspects are fragile vs robust.

    Args:
        design: Design to analyze
        perturbation_magnitude: Size of random perturbations
        num_samples: Number of perturbed samples to test
        objectives: Optional objective functions to evaluate

    Returns:
        Dict with sensitivity metrics

    Example:
        >>> sensitivity = sensitivity_analysis(design, perturbation_magnitude=0.05)
        >>> sensitivity["mean_score_change"]
        0.023
    """
    base_vector = design.vector
    base_score = (
        evaluate_design_option(design, objectives)
        if objectives
        else sum(design.quality_scores.values()) / max(len(design.quality_scores), 1)
    )

    score_changes = []
    for _ in range(num_samples):
        # Create small random perturbation
        perturbation = np.random.randn(len(base_vector))
        perturbation = normalize_vector(perturbation)

        # Perturb design
        perturbed_vector = normalize_vector(base_vector + perturbation_magnitude * perturbation)

        # Create perturbed design
        perturbed_design = DesignAlternative(
            vector=perturbed_vector,
            metadata=design.metadata.copy(),
            quality_scores=design.quality_scores.copy(),
            feasibility=design.feasibility,
        )

        # Evaluate perturbed design
        perturbed_score = (
            evaluate_design_option(perturbed_design, objectives)
            if objectives
            else sum(perturbed_design.quality_scores.values())
            / max(len(perturbed_design.quality_scores), 1)
        )

        score_changes.append(abs(perturbed_score - base_score))

    return {
        "mean_score_change": float(np.mean(score_changes)),
        "max_score_change": float(np.max(score_changes)),
        "std_score_change": float(np.std(score_changes)),
        "robustness": 1.0 - float(np.mean(score_changes)),
    }


# ============================================================================
# Trade-off Analysis
# ============================================================================


@dataclass
class ParetoFrontier:
    """Represents a Pareto frontier of non-dominated designs.

    Attributes:
        designs: List of Pareto-optimal designs
        dominated_designs: Designs dominated by frontier
        objective_names: Names of objectives considered
        hypervolume: Hypervolume indicator (quality metric)
    """

    designs: list[DesignAlternative]
    dominated_designs: list[DesignAlternative]
    objective_names: list[str]
    hypervolume: float = 0.0


def pareto_frontier(
    designs: list[DesignAlternative],
    objectives: list[str] | dict[str, ObjectiveFunction],
) -> ParetoFrontier:
    """Identify Pareto-optimal designs (non-dominated set).

    A design is Pareto-optimal if no other design is better in all objectives.
    This finds the set of designs representing optimal trade-offs.

    Args:
        designs: List of design alternatives
        objectives: List of objective names or dict of objective functions

    Returns:
        ParetoFrontier with optimal and dominated designs

    Example:
        >>> # Find designs optimal in performance, cost, and maintainability
        >>> frontier = pareto_frontier(designs, ["performance", "cost", "maintainability"])
        >>> optimal_designs = frontier.designs
    """
    if isinstance(objectives, list):
        # Use quality scores from designs
        objective_names = objectives

        def get_scores(d: DesignAlternative) -> list[float]:
            return [d.quality_scores.get(obj, 0.0) for obj in objective_names]

    else:
        # Use objective functions
        objective_names = list(objectives.keys())
        objective_fns = objectives

        def get_scores(d: DesignAlternative) -> list[float]:
            return [fn(d) for fn in objective_fns.values()]

    # Compute objective scores for all designs
    design_scores = [(design, get_scores(design)) for design in designs]

    # Find non-dominated designs
    pareto_designs = []
    dominated_designs = []

    for i, (design_i, scores_i) in enumerate(design_scores):
        is_dominated = False

        for j, (_, scores_j) in enumerate(design_scores):
            if i == j:
                continue

            # Check if j dominates i (j is better in all objectives)
            if all(s_j >= s_i for s_j, s_i in zip(scores_j, scores_i, strict=False)) and any(
                s_j > s_i for s_j, s_i in zip(scores_j, scores_i, strict=False)
            ):
                is_dominated = True
                break

        if is_dominated:
            dominated_designs.append(design_i)
        else:
            pareto_designs.append(design_i)

    # Compute hypervolume (simplified: volume under Pareto front)
    if pareto_designs:
        pareto_scores = [get_scores(d) for d in pareto_designs]
        # Simple hypervolume: product of normalized objective ranges
        hypervolume = float(np.prod([np.max(s) for s in zip(*pareto_scores, strict=False)]))
    else:
        hypervolume = 0.0

    logger.info(
        "Pareto frontier: %d optimal designs, %d dominated designs (hypervolume: %.3f)",
        len(pareto_designs),
        len(dominated_designs),
        hypervolume,
    )

    return ParetoFrontier(
        designs=pareto_designs,
        dominated_designs=dominated_designs,
        objective_names=objective_names,
        hypervolume=hypervolume,
    )


def multi_objective_score(
    design: DesignAlternative,
    objectives: dict[str, float],
    method: str = "weighted_sum",
) -> dict[str, float]:
    """Compute multi-objective score using various aggregation methods.

    Args:
        design: Design to score
        objectives: Dict mapping objective names to target values
        method: Aggregation method ("weighted_sum", "weighted_product", "topsis")

    Returns:
        Dict with aggregated score and per-objective scores

    Example:
        >>> objectives = {"performance": 0.9, "cost": 0.3}
        >>> scores = multi_objective_score(design, objectives, method="weighted_sum")
    """
    scores = {}
    weights = {}

    # Extract scores and weights
    for obj_name, target in objectives.items():
        score = design.quality_scores.get(obj_name, 0.0)
        scores[obj_name] = score
        weights[obj_name] = target

    # Normalize weights
    total_weight = sum(weights.values())
    if total_weight > 0:
        weights = {k: v / total_weight for k, v in weights.items()}

    # Compute aggregate score
    if method == "weighted_sum":
        aggregate = sum(weights[obj] * scores[obj] for obj in scores)

    elif method == "weighted_product":
        aggregate = np.prod([scores[obj] ** weights[obj] for obj in scores])

    elif method == "topsis":
        # TOPSIS: distance to ideal and anti-ideal solutions
        ideal = dict.fromkeys(scores, 1.0)
        anti_ideal = dict.fromkeys(scores, 0.0)

        dist_ideal = np.sqrt(sum(weights[obj] * (scores[obj] - ideal[obj]) ** 2 for obj in scores))
        dist_anti_ideal = np.sqrt(
            sum(weights[obj] * (scores[obj] - anti_ideal[obj]) ** 2 for obj in scores)
        )

        aggregate = dist_anti_ideal / (dist_ideal + dist_anti_ideal + 1e-10)

    else:
        msg = f"Unsupported multi-objective method: {method}"
        raise ValueError(msg)

    return {
        "aggregate_score": float(aggregate),
        "method": method,
        "objective_scores": scores,
        "weights": weights,
    }


def trade_off_visualization(
    designs: list[DesignAlternative],
    objectives: list[str],
) -> dict[str, Any]:
    """Generate trade-off visualization data for designs.

    Creates data structure suitable for plotting Pareto fronts and
    objective trade-offs.

    Args:
        designs: List of design alternatives
        objectives: List of objective names to visualize

    Returns:
        Dict with visualization data

    Example:
        >>> viz_data = trade_off_visualization(designs, ["performance", "cost"])
        >>> # Use viz_data to create scatter plots, Pareto fronts, etc.
    """
    # Extract objective scores for all designs
    objective_scores = {obj: [] for obj in objectives}

    for design in designs:
        for obj in objectives:
            objective_scores[obj].append(design.quality_scores.get(obj, 0.0))

    # Compute Pareto frontier
    frontier = pareto_frontier(designs, objectives)

    # Create visualization data
    # Build index mapping to avoid array comparison issues
    pareto_indices = []
    for pareto_design in frontier.designs:
        for i, design in enumerate(designs):
            if pareto_design is design:  # Use identity check instead of equality
                pareto_indices.append(i)
                break

    viz_data = {
        "objectives": objectives,
        "objective_scores": objective_scores,
        "pareto_optimal_indices": pareto_indices,
        "num_designs": len(designs),
        "num_pareto_optimal": len(frontier.designs),
        "hypervolume": frontier.hypervolume,
    }

    # Add pairwise correlations
    correlations = {}
    for i, obj1 in enumerate(objectives):
        for obj2 in objectives[i + 1 :]:
            corr = np.corrcoef(objective_scores[obj1], objective_scores[obj2])[0, 1]
            correlations[f"{obj1}_vs_{obj2}"] = float(corr)

    viz_data["correlations"] = correlations

    return viz_data


# ============================================================================
# Risk Assessment
# ============================================================================


@dataclass
class Risk:
    """Represents an identified risk in a design.

    Attributes:
        name: Risk name/identifier
        description: Detailed risk description
        probability: Likelihood of occurrence (0.0 to 1.0)
        impact: Severity if occurs (0.0 to 1.0)
        risk_score: Combined probability * impact
        category: Risk category (technical, operational, etc.)
        mitigation_strategies: Suggested mitigation approaches
    """

    name: str
    description: str
    probability: float
    impact: float
    risk_score: float
    category: str
    mitigation_strategies: list[str] = field(default_factory=list)


def identify_risks(
    design: DesignAlternative,
    vector_db: dict[str, Vector] | None = None,
    risk_threshold: float = 0.5,
) -> list[Risk]:
    """Identify potential risks in a design.

    Analyzes design for common risk patterns and anti-patterns using
    semantic similarity to known risk vectors.

    Args:
        design: Design to analyze
        vector_db: Optional database with risk pattern vectors
        risk_threshold: Minimum similarity to flag as risk

    Returns:
        List of identified risks

    Example:
        >>> risks = identify_risks(design, vector_db, risk_threshold=0.6)
        >>> critical_risks = [r for r in risks if r.risk_score > 0.7]
    """
    risks: list[Risk] = []

    # Common risk patterns (simplified - in production, use comprehensive vector DB)
    risk_patterns = {
        "complexity": {
            "description": "High architectural complexity increases maintenance burden",
            "probability": 0.7,
            "impact": 0.6,
            "category": "technical",
        },
        "tight_coupling": {
            "description": "Tight coupling reduces flexibility and testability",
            "probability": 0.6,
            "impact": 0.7,
            "category": "technical",
        },
        "single_point_failure": {
            "description": "Single point of failure threatens availability",
            "probability": 0.5,
            "impact": 0.9,
            "category": "operational",
        },
        "scalability_limit": {
            "description": "Scalability constraints may limit growth",
            "probability": 0.4,
            "impact": 0.8,
            "category": "technical",
        },
        "security_weakness": {
            "description": "Security vulnerabilities expose system to threats",
            "probability": 0.5,
            "impact": 0.9,
            "category": "security",
        },
    }

    # Check for risk patterns
    for risk_name, risk_info in risk_patterns.items():
        # In production, use vector similarity to detect risks
        # For now, use quality scores as proxy
        risk_score = 1.0 - design.quality_scores.get(risk_name.replace("_", " "), 0.5)

        if risk_score >= risk_threshold:
            probability = risk_info["probability"] * risk_score
            impact = risk_info["impact"]

            risks.append(
                Risk(
                    name=risk_name,
                    description=risk_info["description"],
                    probability=probability,
                    impact=impact,
                    risk_score=probability * impact,
                    category=risk_info["category"],
                    mitigation_strategies=risk_mitigation_strategies(risk_name),
                )
            )

    # Sort by risk score
    risks.sort(key=lambda r: r.risk_score, reverse=True)

    logger.info("Identified %d risks (threshold: %.2f)", len(risks), risk_threshold)

    return risks


def risk_mitigation_strategies(risk_name: str) -> list[str]:
    """Generate mitigation strategies for a specific risk.

    Args:
        risk_name: Name of the risk

    Returns:
        List of mitigation strategy descriptions

    Example:
        >>> strategies = risk_mitigation_strategies("tight_coupling")
        >>> strategies[0]
        'Introduce abstraction layers and dependency injection'
    """
    mitigation_map = {
        "complexity": [
            "Simplify architecture by removing unnecessary components",
            "Apply SOLID principles and design patterns",
            "Increase modularity and separation of concerns",
        ],
        "tight_coupling": [
            "Introduce abstraction layers and dependency injection",
            "Use event-driven architecture for loose coupling",
            "Apply interface segregation principle",
        ],
        "single_point_failure": [
            "Introduce redundancy and failover mechanisms",
            "Implement circuit breakers and bulkheads",
            "Deploy across multiple availability zones",
        ],
        "scalability_limit": [
            "Adopt horizontal scaling strategy",
            "Implement caching and load balancing",
            "Consider microservices architecture",
        ],
        "security_weakness": [
            "Implement defense in depth strategy",
            "Apply security best practices (encryption, authentication)",
            "Conduct regular security audits and penetration testing",
        ],
    }

    return mitigation_map.get(risk_name, ["Conduct detailed risk analysis"])


def failure_mode_analysis(
    design: DesignAlternative,
    components: list[str] | None = None,
) -> dict[str, Any]:
    """Perform Failure Mode and Effects Analysis (FMEA) on design.

    Systematically analyzes potential failure modes, their effects,
    and criticality.

    Args:
        design: Design to analyze
        components: Optional list of component names to analyze

    Returns:
        Dict with FMEA results

    Example:
        >>> fmea = failure_mode_analysis(design, components=["api", "database", "cache"])
        >>> critical_modes = [m for m in fmea["failure_modes"] if m["rpn"] > 100]
    """
    if components is None:
        # Extract components from metadata
        components = list(design.metadata.get("components", ["component_1", "component_2"]))

    failure_modes = []

    # Common failure modes per component type
    common_failures = {
        "api": [
            ("timeout", 0.3, 0.6, 0.7),
            ("rate_limit_exceeded", 0.4, 0.4, 0.5),
            ("authentication_failure", 0.2, 0.8, 0.6),
        ],
        "database": [
            ("connection_pool_exhausted", 0.3, 0.9, 0.5),
            ("query_timeout", 0.4, 0.7, 0.6),
            ("data_corruption", 0.1, 1.0, 0.3),
        ],
        "cache": [
            ("cache_miss", 0.6, 0.3, 0.8),
            ("eviction", 0.5, 0.4, 0.7),
            ("inconsistency", 0.2, 0.7, 0.4),
        ],
    }

    for component in components:
        # Get component-specific failures or use generic
        component_type = "api"  # Simplified - would parse from metadata
        failures = common_failures.get(component_type, [("generic_failure", 0.5, 0.5, 0.5)])

        for failure_name, probability, severity, detectability in failures:
            # RPN = Risk Priority Number (severity × occurrence × detection)
            # Scale: 1-10 for each factor
            severity_score = int(severity * 10)
            occurrence_score = int(probability * 10)
            detection_score = int(detectability * 10)
            rpn = severity_score * occurrence_score * detection_score

            failure_modes.append(
                {
                    "component": component,
                    "failure_mode": failure_name,
                    "severity": severity_score,
                    "occurrence": occurrence_score,
                    "detection": detection_score,
                    "rpn": rpn,
                    "recommended_actions": _get_fmea_actions(rpn),
                }
            )

    # Sort by RPN (highest risk first)
    failure_modes.sort(key=lambda x: x["rpn"], reverse=True)

    return {
        "design": design.metadata.get("name", "unnamed"),
        "components_analyzed": len(components),
        "failure_modes": failure_modes,
        "total_failure_modes": len(failure_modes),
        "high_risk_count": sum(1 for fm in failure_modes if fm["rpn"] > 100),
        "mean_rpn": float(np.mean([fm["rpn"] for fm in failure_modes])),
    }


def _get_fmea_actions(rpn: int) -> list[str]:
    """Get recommended actions based on RPN score.

    Args:
        rpn: Risk Priority Number

    Returns:
        List of recommended actions
    """
    if rpn > 200:
        return [
            "CRITICAL: Immediate action required",
            "Redesign to eliminate failure mode",
            "Implement multiple layers of protection",
        ]
    if rpn > 100:
        return [
            "HIGH: Priority mitigation needed",
            "Add monitoring and alerting",
            "Implement failover mechanisms",
        ]
    if rpn > 50:
        return [
            "MEDIUM: Plan mitigation",
            "Add error handling and recovery",
            "Monitor failure frequency",
        ]
    return [
        "LOW: Monitor only",
        "Document failure mode",
        "Include in regular reviews",
    ]
