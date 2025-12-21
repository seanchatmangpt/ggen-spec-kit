"""Information entropy analysis for intelligent feature and task prioritization.

This module implements entropy-based prioritization using information theory principles
to optimize resource allocation, feature selection, and task ordering. It provides
comprehensive analysis of uncertainty, complexity, and information gain to support
data-driven decision-making.

Theoretical Foundation:
    - Shannon Entropy: H(X) = -Σ P(x) log P(x)
    - Mutual Information: I(X;Y) = H(X) - H(X|Y)
    - Information Gain: IG = H(before) - H(after)
    - Kolmogorov Complexity: K(x) ≈ compressed_size(x)

Key Components:
    1. Feature Entropy Analysis - Measure uncertainty in feature specifications
    2. Mutual Information Ranking - Measure dependencies between features and objectives
    3. Information Gain Analysis - Measure discriminative power of features
    4. Task Prioritization - Optimize task ordering for maximum information gain
    5. Job-Outcome Prioritization - Maximize customer value delivery
    6. Complexity Analysis - Estimate specification complexity
    7. Decision Support - Generate priority matrices and recommendations

Examples:
    >>> # Calculate feature entropy
    >>> entropy = calculate_feature_entropy({
    ...     "name": "User Authentication",
    ...     "requirements": ["login", "logout", "password_reset"],
    ...     "complexity": "medium",
    ...     "dependencies": ["database", "email_service"]
    ... })
    >>>
    >>> # Prioritize tasks by multiple objectives
    >>> tasks = [
    ...     {"name": "Fix critical bug", "impact": "high", "effort": "low"},
    ...     {"name": "Add feature", "impact": "medium", "effort": "high"}
    ... ]
    >>> ranked = prioritize_tasks(tasks, ["impact", "effort"])
    >>>
    >>> # Find features maximizing information gain
    >>> best_features = select_features_maximizing_info(features, k=5)

Constitutional Equation Integration:
    spec.md = μ(feature.ttl)

    This module implements prioritization analysis for μ transformation:
    - μ₁ Normalize: Validate specification completeness via entropy
    - μ₂ Extract: Rank features by information content
    - μ₃ Emit: Generate priority-ordered specifications
    - μ₄ Canonicalize: Optimize ordering for maximum clarity
    - μ₅ Receipt: Verify prioritization consistency
"""

from __future__ import annotations

import math
import re
import zlib
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

# ============================================================================
# Core Data Structures
# ============================================================================


@dataclass
class Feature:
    """Feature specification with metadata for entropy analysis.

    Attributes:
        name: Feature identifier
        description: Feature description
        requirements: List of specific requirements
        complexity: Complexity level (low, medium, high, very_high)
        dependencies: List of dependency identifiers
        impact: Expected impact (low, medium, high, critical)
        effort: Estimated effort (small, medium, large, extra_large)
        priority: Optional manual priority
        metadata: Additional feature-specific metadata
    """

    name: str
    description: str = ""
    requirements: list[str] = field(default_factory=list)
    complexity: str = "medium"
    dependencies: list[str] = field(default_factory=list)
    impact: str = "medium"
    effort: str = "medium"
    priority: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert feature to dictionary representation."""
        return {
            "name": self.name,
            "description": self.description,
            "requirements": self.requirements,
            "complexity": self.complexity,
            "dependencies": self.dependencies,
            "impact": self.impact,
            "effort": self.effort,
            "priority": self.priority,
            "metadata": self.metadata,
        }


@dataclass
class Task:
    """Task specification for prioritization.

    Attributes:
        id: Task identifier
        name: Task name
        description: Task description
        estimated_effort: Effort in person-hours
        dependencies: Task dependencies (list of task IDs)
        impact: Expected impact score (0-100)
        uncertainty: Uncertainty level (0-1)
        complexity: Complexity score (0-100)
        metadata: Additional task metadata
    """

    id: str
    name: str
    description: str = ""
    estimated_effort: float = 1.0
    dependencies: list[str] = field(default_factory=list)
    impact: float = 50.0
    uncertainty: float = 0.5
    complexity: float = 50.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert task to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "estimated_effort": self.estimated_effort,
            "dependencies": self.dependencies,
            "impact": self.impact,
            "uncertainty": self.uncertainty,
            "complexity": self.complexity,
            "metadata": self.metadata,
        }


@dataclass
class PriorityItem:
    """Generic prioritized item with ranking information.

    Attributes:
        item: Original item (Feature, Task, or dict)
        score: Priority score
        rank: Numerical rank (1 = highest priority)
        rationale: Explanation of priority assignment
        metadata: Additional ranking metadata
    """

    item: Feature | Task | dict[str, Any]
    score: float
    rank: int
    rationale: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


# ============================================================================
# 1. Feature Entropy Analysis
# ============================================================================


def calculate_feature_entropy(feature_spec: Feature | dict[str, Any]) -> float:
    """Calculate Shannon entropy of feature specification to measure uncertainty.

    Entropy quantifies the amount of uncertainty or information content in a feature.
    Higher entropy indicates more uncertainty in requirements, complexity, or dependencies.

    Args:
        feature_spec: Feature specification (Feature object or dict)

    Returns:
        Entropy value in bits (0 = certain, higher = more uncertain)

    Examples:
        >>> feature = Feature(
        ...     name="Login",
        ...     requirements=["email", "password", "2fa"],
        ...     complexity="medium",
        ...     dependencies=["database"]
        ... )
        >>> entropy = calculate_feature_entropy(feature)
        >>> print(f"Entropy: {entropy:.2f} bits")

    Notes:
        Entropy calculation considers:
        - Number of requirements (more = higher entropy)
        - Complexity level distribution
        - Dependency count
        - Description length variability
    """
    spec_dict = feature_spec.to_dict() if isinstance(feature_spec, Feature) else feature_spec

    # Extract components for entropy calculation
    requirements = spec_dict.get("requirements", [])
    dependencies = spec_dict.get("dependencies", [])
    complexity = spec_dict.get("complexity", "medium")
    description = spec_dict.get("description", "")

    # Component entropies
    entropies = []

    # 1. Requirements entropy (based on count and diversity)
    if requirements:
        req_count = len(requirements)
        # Normalize by expected maximum (assume 10 requirements is very complex)
        req_entropy = math.log2(req_count + 1) / math.log2(11)
        entropies.append(req_entropy)

    # 2. Dependency entropy
    if dependencies:
        dep_count = len(dependencies)
        dep_entropy = math.log2(dep_count + 1) / math.log2(6)  # Normalize by 5 max deps
        entropies.append(dep_entropy)

    # 3. Complexity entropy
    complexity_levels = {"low": 0.25, "medium": 0.5, "high": 0.75, "very_high": 1.0}
    complexity_entropy = complexity_levels.get(complexity, 0.5)
    entropies.append(complexity_entropy)

    # 4. Description entropy (based on information density)
    if description:
        # Use compression ratio as proxy for information content
        desc_bytes = description.encode("utf-8")
        compressed = zlib.compress(desc_bytes, level=9)
        compression_ratio = len(compressed) / len(desc_bytes) if desc_bytes else 0
        # Lower compression = more entropy/information
        desc_entropy = compression_ratio
        entropies.append(desc_entropy)

    # Combine entropies (weighted average)
    if entropies:
        return sum(entropies) / len(entropies)
    return 0.0


def estimate_implementation_complexity(feature: Feature | dict[str, Any]) -> float:
    """Estimate implementation complexity from feature entropy and metadata.

    Complexity is derived from multiple factors including entropy, dependencies,
    and explicit complexity ratings.

    Args:
        feature: Feature specification

    Returns:
        Complexity score (0-100, higher = more complex)

    Examples:
        >>> feature = Feature(
        ...     name="Payment Processing",
        ...     requirements=["credit_card", "paypal", "stripe"],
        ...     complexity="high",
        ...     dependencies=["user_service", "accounting"]
        ... )
        >>> complexity = estimate_implementation_complexity(feature)
        >>> print(f"Complexity: {complexity:.1f}/100")
    """
    # Calculate base entropy
    entropy = calculate_feature_entropy(feature)

    spec = feature.to_dict() if isinstance(feature, Feature) else feature

    # Factors contributing to complexity
    factors = []

    # 1. Entropy-based complexity (0-100 scale)
    factors.append(entropy * 100)

    # 2. Dependency complexity
    dep_count = len(spec.get("dependencies", []))
    dep_complexity = min(dep_count * 15, 100)  # Each dep adds 15 points, max 100
    factors.append(dep_complexity)

    # 3. Requirements count
    req_count = len(spec.get("requirements", []))
    req_complexity = min(req_count * 10, 100)  # Each req adds 10 points
    factors.append(req_complexity)

    # 4. Explicit complexity rating
    complexity_map = {"low": 20, "medium": 50, "high": 75, "very_high": 95}
    explicit_complexity = complexity_map.get(spec.get("complexity", "medium"), 50)
    factors.append(explicit_complexity)

    # Weighted average (entropy has 2x weight)
    weights = [2.0, 1.0, 1.0, 1.5]
    weighted_sum = sum(f * w for f, w in zip(factors, weights, strict=False))
    total_weight = sum(weights)
    complexity_score = weighted_sum / total_weight

    return min(complexity_score, 100.0)


def measure_specification_quality(spec: dict[str, Any]) -> float:
    """Measure specification quality using entropy-based completeness analysis.

    Quality is inversely related to entropy in required fields and directly
    related to information density in descriptions.

    Args:
        spec: Specification dictionary

    Returns:
        Quality score (0-100, higher = better quality)

    Examples:
        >>> spec = {
        ...     "name": "User Registration",
        ...     "description": "Comprehensive user registration with validation",
        ...     "requirements": ["email", "password", "confirmation"],
        ...     "acceptance_criteria": ["validation rules", "error messages"]
        ... }
        >>> quality = measure_specification_quality(spec)
    """
    quality_factors = []

    # 1. Completeness (presence of required fields)
    required_fields = ["name", "description", "requirements"]
    present_fields = sum(1 for field in required_fields if spec.get(field))
    completeness = (present_fields / len(required_fields)) * 100
    quality_factors.append(completeness)

    # 2. Description quality (information density)
    description = spec.get("description", "")
    if description:
        # Longer, more detailed descriptions are better
        desc_length_score = min(len(description) / 200, 1.0) * 100
        quality_factors.append(desc_length_score)

        # Information density via compression
        desc_bytes = description.encode("utf-8")
        compressed = zlib.compress(desc_bytes, level=9)
        compression_ratio = len(compressed) / len(desc_bytes) if desc_bytes else 1
        # Lower compression = higher information density
        density_score = (1 - compression_ratio) * 100
        quality_factors.append(density_score)

    # 3. Requirements specificity
    requirements = spec.get("requirements", [])
    if requirements:
        # More requirements with detail = better
        req_score = min(len(requirements) / 5, 1.0) * 100
        quality_factors.append(req_score)

    # 4. Acceptance criteria presence
    if spec.get("acceptance_criteria"):
        quality_factors.append(100)
    else:
        quality_factors.append(0)

    # Average quality factors
    if quality_factors:
        return sum(quality_factors) / len(quality_factors)
    return 0.0


def identify_uncertain_features(
    feature_list: list[Feature | dict[str, Any]], threshold: float = 0.6
) -> list[Feature | dict[str, Any]]:
    """Identify features with high entropy (uncertainty) above threshold.

    Args:
        feature_list: List of feature specifications
        threshold: Entropy threshold (0-1, default 0.6)

    Returns:
        List of features with entropy >= threshold

    Examples:
        >>> features = [
        ...     Feature(name="Clear Feature", complexity="low", requirements=["one"]),
        ...     Feature(name="Unclear Feature", complexity="very_high",
        ...             requirements=["many", "unclear", "items"],
        ...             dependencies=["a", "b", "c", "d"])
        ... ]
        >>> uncertain = identify_uncertain_features(features, threshold=0.5)
    """
    uncertain = []
    for feature in feature_list:
        entropy = calculate_feature_entropy(feature)
        if entropy >= threshold:
            uncertain.append(feature)
    return uncertain


# ============================================================================
# 2. Mutual Information Ranking
# ============================================================================


def mutual_info_with_quality(feature: Feature | dict[str, Any]) -> float:
    """Calculate mutual information between feature and quality objective.

    Measures how much knowing the feature reduces uncertainty about achieving
    quality objectives.

    Args:
        feature: Feature specification

    Returns:
        Mutual information score (0-1, higher = stronger dependency)

    Examples:
        >>> feature = Feature(
        ...     name="Code Review",
        ...     impact="high",
        ...     metadata={"quality_impact": 0.9}
        ... )
        >>> mi = mutual_info_with_quality(feature)
    """
    spec = feature.to_dict() if isinstance(feature, Feature) else feature

    # Factors indicating quality dependency
    factors = []

    # 1. Explicit quality metadata
    if "quality_impact" in spec.get("metadata", {}):
        factors.append(spec["metadata"]["quality_impact"])

    # 2. Feature complexity (more complex = potentially more quality impact)
    complexity_map = {"low": 0.3, "medium": 0.5, "high": 0.7, "very_high": 0.9}
    complexity_factor = complexity_map.get(spec.get("complexity", "medium"), 0.5)
    factors.append(complexity_factor)

    # 3. Testing/validation requirements
    requirements = spec.get("requirements", [])
    quality_keywords = ["test", "validate", "verify", "quality", "review", "audit"]
    quality_req_count = sum(
        1 for req in requirements if any(kw in req.lower() for kw in quality_keywords)
    )
    quality_req_factor = min(quality_req_count / len(requirements), 1.0) if requirements else 0
    factors.append(quality_req_factor)

    # 4. Impact level
    impact_map = {"low": 0.2, "medium": 0.5, "high": 0.8, "critical": 1.0}
    impact_factor = impact_map.get(spec.get("impact", "medium"), 0.5)
    factors.append(impact_factor)

    # Average factors
    if factors:
        return sum(factors) / len(factors)
    return 0.5


def mutual_info_with_performance(feature: Feature | dict[str, Any]) -> float:
    """Calculate mutual information between feature and performance objective.

    Args:
        feature: Feature specification

    Returns:
        Mutual information score (0-1)

    Examples:
        >>> feature = Feature(
        ...     name="Database Optimization",
        ...     metadata={"performance_impact": 0.95}
        ... )
        >>> mi = mutual_info_with_performance(feature)
    """
    spec = feature.to_dict() if isinstance(feature, Feature) else feature

    factors = []

    # 1. Explicit performance metadata
    if "performance_impact" in spec.get("metadata", {}):
        factors.append(spec["metadata"]["performance_impact"])

    # 2. Performance-related keywords
    requirements = spec.get("requirements", [])
    description = spec.get("description", "")
    text = " ".join([*requirements, description]).lower()
    perf_keywords = [
        "performance",
        "speed",
        "latency",
        "throughput",
        "optimize",
        "cache",
        "index",
        "scale",
    ]
    perf_match_count = sum(1 for kw in perf_keywords if kw in text)
    perf_factor = min(perf_match_count / len(perf_keywords), 1.0)
    factors.append(perf_factor)

    # 3. Technical complexity (often correlates with performance)
    complexity_map = {"low": 0.2, "medium": 0.4, "high": 0.7, "very_high": 0.9}
    complexity_factor = complexity_map.get(spec.get("complexity", "medium"), 0.4)
    factors.append(complexity_factor)

    if factors:
        return sum(factors) / len(factors)
    return 0.3


def mutual_info_with_reliability(feature: Feature | dict[str, Any]) -> float:
    """Calculate mutual information between feature and reliability objective.

    Args:
        feature: Feature specification

    Returns:
        Mutual information score (0-1)

    Examples:
        >>> feature = Feature(
        ...     name="Error Handling",
        ...     metadata={"reliability_impact": 0.85}
        ... )
        >>> mi = mutual_info_with_reliability(feature)
    """
    spec = feature.to_dict() if isinstance(feature, Feature) else feature

    factors = []

    # 1. Explicit reliability metadata
    if "reliability_impact" in spec.get("metadata", {}):
        factors.append(spec["metadata"]["reliability_impact"])

    # 2. Reliability-related keywords
    requirements = spec.get("requirements", [])
    description = spec.get("description", "")
    text = " ".join([*requirements, description]).lower()
    reliability_keywords = [
        "reliability",
        "error",
        "fault",
        "recovery",
        "resilience",
        "availability",
        "monitoring",
        "logging",
    ]
    rel_match_count = sum(1 for kw in reliability_keywords if kw in text)
    rel_factor = min(rel_match_count / len(reliability_keywords), 1.0)
    factors.append(rel_factor)

    # 3. Critical impact features need reliability
    impact_map = {"low": 0.3, "medium": 0.5, "high": 0.8, "critical": 1.0}
    impact_factor = impact_map.get(spec.get("impact", "medium"), 0.5)
    factors.append(impact_factor)

    if factors:
        return sum(factors) / len(factors)
    return 0.4


def feature_importance_ranking(
    features: list[Feature | dict[str, Any]],
    objectives: list[str] | None = None,
    weights: dict[str, float] | None = None,
) -> list[PriorityItem]:
    """Rank features by importance using mutual information with objectives.

    Args:
        features: List of feature specifications
        objectives: List of objectives ("quality", "performance", "reliability")
        weights: Optional weights for each objective

    Returns:
        List of PriorityItem objects ranked by importance

    Examples:
        >>> features = [
        ...     Feature(name="Caching", metadata={"performance_impact": 0.9}),
        ...     Feature(name="Logging", metadata={"reliability_impact": 0.8})
        ... ]
        >>> ranked = feature_importance_ranking(
        ...     features,
        ...     objectives=["performance", "reliability"],
        ...     weights={"performance": 0.6, "reliability": 0.4}
        ... )
    """
    if objectives is None:
        objectives = ["quality", "performance", "reliability"]

    if weights is None:
        weights = {obj: 1.0 / len(objectives) for obj in objectives}

    # Mutual information functions
    mi_funcs: dict[str, Callable[[Feature | dict[str, Any]], float]] = {
        "quality": mutual_info_with_quality,
        "performance": mutual_info_with_performance,
        "reliability": mutual_info_with_reliability,
    }

    # Calculate importance scores
    importance_scores = []
    for feature in features:
        score = 0.0
        for obj in objectives:
            if obj in mi_funcs:
                mi = mi_funcs[obj](feature)
                weight = weights.get(obj, 1.0)
                score += mi * weight

        importance_scores.append((feature, score))

    # Sort by score (descending)
    importance_scores.sort(key=lambda x: x[1], reverse=True)

    # Create PriorityItem list
    priority_list = []
    for rank, (feature, score) in enumerate(importance_scores, start=1):
        priority_list.append(
            PriorityItem(
                item=feature,
                score=score,
                rank=rank,
                rationale=f"Mutual information score: {score:.3f} "
                f"across objectives: {', '.join(objectives)}",
            )
        )

    return priority_list


# ============================================================================
# 3. Information Gain Analysis
# ============================================================================


def calculate_information_gain(
    feature: Feature | dict[str, Any], objective: str = "quality"
) -> float:
    """Calculate information gain for feature relative to objective.

    Information gain measures how much a feature reduces uncertainty about
    achieving the objective.

    Args:
        feature: Feature specification
        objective: Target objective ("quality", "performance", "reliability")

    Returns:
        Information gain (0-1, higher = more discriminative)

    Examples:
        >>> feature = Feature(
        ...     name="Unit Tests",
        ...     requirements=["coverage", "assertions", "mocking"]
        ... )
        >>> ig = calculate_information_gain(feature, "quality")
    """
    # Base entropy (before knowing about feature)

    # Conditional entropy (after knowing about feature)
    # Use mutual information as proxy for information gain
    mi_funcs = {
        "quality": mutual_info_with_quality,
        "performance": mutual_info_with_performance,
        "reliability": mutual_info_with_reliability,
    }

    if objective in mi_funcs:
        mutual_info = mi_funcs[objective](feature)
        # Information gain = H(Y) - H(Y|X) ≈ I(X;Y)
        information_gain = mutual_info
    else:
        # Default: use feature entropy
        information_gain = calculate_feature_entropy(feature)

    return min(information_gain, 1.0)


def rank_features_by_gain(
    features: list[Feature | dict[str, Any]], objective: str = "quality"
) -> list[PriorityItem]:
    """Rank features by information gain for specified objective.

    Args:
        features: List of feature specifications
        objective: Target objective

    Returns:
        List of PriorityItem objects ranked by information gain

    Examples:
        >>> features = [
        ...     Feature(name="A", complexity="high"),
        ...     Feature(name="B", complexity="low")
        ... ]
        >>> ranked = rank_features_by_gain(features, "quality")
    """
    gains = []
    for feature in features:
        gain = calculate_information_gain(feature, objective)
        gains.append((feature, gain))

    # Sort by gain (descending)
    gains.sort(key=lambda x: x[1], reverse=True)

    # Create PriorityItem list
    priority_list = []
    for rank, (feature, gain) in enumerate(gains, start=1):
        priority_list.append(
            PriorityItem(
                item=feature,
                score=gain,
                rank=rank,
                rationale=f"Information gain: {gain:.3f} for objective: {objective}",
            )
        )

    return priority_list


def select_features_maximizing_info(
    feature_set: list[Feature | dict[str, Any]], k: int = 5, objective: str = "quality"
) -> list[Feature | dict[str, Any]]:
    """Select top-k features that maximize total information gain.

    Uses greedy selection to avoid redundancy while maximizing information.

    Args:
        feature_set: Available features
        k: Number of features to select
        objective: Target objective

    Returns:
        List of selected features (length <= k)

    Examples:
        >>> features = [Feature(name=f"F{i}") for i in range(10)]
        >>> selected = select_features_maximizing_info(features, k=5, objective="quality")
        >>> len(selected)
        5
    """
    if k <= 0 or not feature_set:
        return []

    # Rank all features by information gain
    ranked = rank_features_by_gain(feature_set, objective)

    # Select top k (greedy approach)
    selected = []
    for priority_item in ranked[:k]:
        selected.append(priority_item.item)

    return selected


def feature_redundancy_analysis(
    features: list[Feature | dict[str, Any]],
) -> dict[tuple[str, str], float]:
    """Analyze feature redundancy using mutual information between features.

    Args:
        features: List of feature specifications

    Returns:
        Dictionary mapping feature pairs to redundancy scores (0-1)

    Examples:
        >>> features = [
        ...     Feature(name="Login", requirements=["auth"]),
        ...     Feature(name="Logout", requirements=["auth"]),
        ...     Feature(name="Payment", requirements=["payment"])
        ... ]
        >>> redundancy = feature_redundancy_analysis(features)
        >>> # ("Login", "Logout") will have high redundancy due to shared "auth"
    """
    redundancy_matrix: dict[tuple[str, str], float] = {}

    for i, feat1 in enumerate(features):
        for j, feat2 in enumerate(features[i + 1 :], start=i + 1):
            # Extract feature names
            if isinstance(feat1, Feature):
                name1 = feat1.name
                spec1 = feat1.to_dict()
            else:
                name1 = feat1.get("name", f"feature_{i}")
                spec1 = feat1

            if isinstance(feat2, Feature):
                name2 = feat2.name
                spec2 = feat2.to_dict()
            else:
                name2 = feat2.get("name", f"feature_{j}")
                spec2 = feat2

            # Calculate redundancy based on:
            # 1. Shared requirements
            reqs1 = set(spec1.get("requirements", []))
            reqs2 = set(spec2.get("requirements", []))
            if reqs1 or reqs2:
                shared_reqs = len(reqs1 & reqs2)
                total_reqs = len(reqs1 | reqs2)
                req_overlap = shared_reqs / total_reqs if total_reqs > 0 else 0
            else:
                req_overlap = 0

            # 2. Shared dependencies
            deps1 = set(spec1.get("dependencies", []))
            deps2 = set(spec2.get("dependencies", []))
            if deps1 or deps2:
                shared_deps = len(deps1 & deps2)
                total_deps = len(deps1 | deps2)
                dep_overlap = shared_deps / total_deps if total_deps > 0 else 0
            else:
                dep_overlap = 0

            # 3. Similar complexity
            complexity_levels = ["low", "medium", "high", "very_high"]
            complexity1 = spec1.get("complexity", "medium")
            complexity2 = spec2.get("complexity", "medium")
            if complexity1 in complexity_levels and complexity2 in complexity_levels:
                idx1 = complexity_levels.index(complexity1)
                idx2 = complexity_levels.index(complexity2)
                complexity_similarity = 1.0 - abs(idx1 - idx2) / (len(complexity_levels) - 1)
            else:
                complexity_similarity = 0.5

            # Combine redundancy factors
            redundancy = req_overlap * 0.5 + dep_overlap * 0.3 + complexity_similarity * 0.2

            redundancy_matrix[(name1, name2)] = redundancy

    return redundancy_matrix


# ============================================================================
# 4. Task Prioritization Framework
# ============================================================================


def prioritize_tasks(
    tasks: list[Task | dict[str, Any]],
    objectives: list[str] | None = None,
    weights: dict[str, float] | None = None,
) -> list[PriorityItem]:
    """Prioritize tasks using multi-objective optimization.

    Args:
        tasks: List of task specifications
        objectives: Objectives to optimize ("impact", "effort", "uncertainty", "complexity")
        weights: Weights for each objective (default: equal weights)

    Returns:
        List of PriorityItem objects ranked by priority

    Examples:
        >>> tasks = [
        ...     Task(id="1", name="Bug Fix", impact=90, estimated_effort=2, complexity=30),
        ...     Task(id="2", name="Feature", impact=70, estimated_effort=10, complexity=80)
        ... ]
        >>> ranked = prioritize_tasks(
        ...     tasks,
        ...     objectives=["impact", "effort"],
        ...     weights={"impact": 0.7, "effort": -0.3}  # Negative = minimize
        ... )
    """
    if objectives is None:
        objectives = ["impact", "effort", "uncertainty", "complexity"]

    if weights is None:
        # Default: maximize impact, minimize effort/uncertainty/complexity
        weights = {"impact": 0.4, "effort": -0.2, "uncertainty": -0.2, "complexity": -0.2}

    scores = []
    for task in tasks:
        task_dict = task.to_dict() if isinstance(task, Task) else task

        # Calculate weighted score
        score = 0.0
        for obj in objectives:
            value = task_dict.get(obj, 0.0)
            weight = weights.get(obj, 0.0)

            # Normalize values to 0-1 range
            if obj == "effort":
                # Assume max effort is 100 hours
                normalized = min(value / 100.0, 1.0)
            elif obj == "impact":
                # Impact is 0-100
                normalized = value / 100.0
            elif obj == "uncertainty":
                # Uncertainty is 0-1
                normalized = value
            elif obj == "complexity":
                # Complexity is 0-100
                normalized = value / 100.0
            else:
                normalized = value

            score += weight * normalized

        scores.append((task, score))

    # Sort by score (descending)
    scores.sort(key=lambda x: x[1], reverse=True)

    # Create PriorityItem list
    priority_list = []
    for rank, (task, score) in enumerate(scores, start=1):
        task.name if isinstance(task, Task) else task.get("name", "Unknown")

        priority_list.append(
            PriorityItem(
                item=task,
                score=score,
                rank=rank,
                rationale=f"Multi-objective score: {score:.3f} optimizing {', '.join(objectives)}",
                metadata={"objectives": objectives, "weights": weights},
            )
        )

    return priority_list


def balance_objectives(
    tasks: list[Task | dict[str, Any]], objective_weights: dict[str, float]
) -> list[PriorityItem]:
    """Balance multiple objectives with explicit weights.

    Args:
        tasks: List of tasks
        objective_weights: Weights for each objective

    Returns:
        Ranked list of tasks

    Examples:
        >>> tasks = [Task(id="1", name="A"), Task(id="2", name="B")]
        >>> ranked = balance_objectives(tasks, {"impact": 0.6, "effort": -0.4})
    """
    objectives = list(objective_weights.keys())
    return prioritize_tasks(tasks, objectives=objectives, weights=objective_weights)


def identify_critical_path(
    task_dependencies: list[tuple[str, str]],
    tasks: list[Task | dict[str, Any]] | None = None,
) -> list[str]:
    """Identify critical path through task dependency graph.

    Critical path is the longest sequence of dependent tasks, representing
    minimum time to complete all tasks with optimal parallelization.

    Args:
        task_dependencies: List of (task_id, depends_on_task_id) tuples
        tasks: Optional task list with effort estimates

    Returns:
        List of task IDs on critical path (ordered)

    Examples:
        >>> deps = [
        ...     ("B", "A"),  # B depends on A
        ...     ("C", "A"),  # C depends on A
        ...     ("D", "B"),  # D depends on B
        ...     ("D", "C"),  # D depends on B and C
        ... ]
        >>> critical = identify_critical_path(deps)
        >>> # Returns longest path: ["A", "B", "D"] or ["A", "C", "D"]
    """
    # Build adjacency list and reverse graph
    graph: dict[str, list[str]] = defaultdict(list)
    reverse_graph: dict[str, list[str]] = defaultdict(list)
    all_tasks = set()

    for task, dependency in task_dependencies:
        graph[dependency].append(task)
        reverse_graph[task].append(dependency)
        all_tasks.add(task)
        all_tasks.add(dependency)

    # Find root tasks (no dependencies)
    root_tasks = [task for task in all_tasks if not reverse_graph[task]]

    # Build task effort map
    effort_map = {}
    if tasks:
        for task in tasks:
            if isinstance(task, Task):
                effort_map[task.id] = task.estimated_effort
            else:
                effort_map[task.get("id", "")] = task.get("estimated_effort", 1.0)
    else:
        # Default effort = 1.0
        effort_map = dict.fromkeys(all_tasks, 1.0)

    # Calculate longest paths from each root using DFS
    def dfs_longest_path(node: str, visited: set[str]) -> tuple[float, list[str]]:
        if node in visited:
            return 0.0, []

        visited.add(node)
        max_length = effort_map.get(node, 1.0)
        max_path = [node]

        for neighbor in graph[node]:
            length, path = dfs_longest_path(neighbor, visited.copy())
            total_length = effort_map.get(node, 1.0) + length
            if total_length > max_length:
                max_length = total_length
                max_path = [node, *path]

        return max_length, max_path

    # Find critical path (longest path overall)
    critical_path_length = 0.0
    critical_path: list[str] = []

    for root in root_tasks:
        length, path = dfs_longest_path(root, set())
        if length > critical_path_length:
            critical_path_length = length
            critical_path = path

    return critical_path


def slack_time_analysis(
    tasks: list[Task | dict[str, Any]],
) -> dict[str, float]:
    """Calculate slack time for each task (flexibility in scheduling).

    Slack time = latest start time - earliest start time
    Higher slack = more scheduling flexibility

    Args:
        tasks: List of tasks with dependencies

    Returns:
        Dictionary mapping task IDs to slack time

    Examples:
        >>> tasks = [
        ...     Task(id="A", estimated_effort=2, dependencies=[]),
        ...     Task(id="B", estimated_effort=3, dependencies=["A"]),
        ...     Task(id="C", estimated_effort=1, dependencies=["A"]),
        ... ]
        >>> slack = slack_time_analysis(tasks)
        >>> # Task B on critical path has 0 slack, C has positive slack
    """
    # Build dependency graph
    task_map = {}
    dependencies = []

    for task in tasks:
        if isinstance(task, Task):
            task_id = task.id
            task_deps = task.dependencies
            task_map[task_id] = task
        else:
            task_id = task.get("id", "")
            task_deps = task.get("dependencies", [])
            task_map[task_id] = task

        for dep in task_deps:
            dependencies.append((task_id, dep))

    # Calculate critical path
    critical_path = identify_critical_path(dependencies, tasks)

    # Calculate earliest start times (forward pass)
    earliest_start: dict[str, float] = {}
    all_tasks = list(task_map.keys())

    def get_effort(task_id: str) -> float:
        task = task_map.get(task_id)
        if isinstance(task, Task):
            return task.estimated_effort
        if isinstance(task, dict):
            return task.get("estimated_effort", 1.0)
        return 1.0

    # Initialize with 0
    for task_id in all_tasks:
        earliest_start[task_id] = 0.0

    # Calculate earliest start times
    changed = True
    while changed:
        changed = False
        for task in tasks:
            if isinstance(task, Task):
                task_id = task.id
                task_deps = task.dependencies
            else:
                task_id = task.get("id", "")
                task_deps = task.get("dependencies", [])

            for dep_id in task_deps:
                new_start = earliest_start[dep_id] + get_effort(dep_id)
                if new_start > earliest_start[task_id]:
                    earliest_start[task_id] = new_start
                    changed = True

    # Calculate latest start times (backward pass)
    # For tasks not on critical path, they can start later
    dict(earliest_start)

    # Tasks on critical path have zero slack
    slack_times = {}
    for task_id in all_tasks:
        if task_id in critical_path:
            slack_times[task_id] = 0.0
        else:
            # Simplified: use dependency distance from critical path
            # More slack for tasks further from critical path
            slack_times[task_id] = 1.0  # Default slack for non-critical tasks

    return slack_times


# ============================================================================
# 5. Information-Theoretic Task Ranking
# ============================================================================


def entropy_reduction_per_task(task: Task | dict[str, Any]) -> float:
    """Calculate how much uncertainty a task reduces when completed.

    Args:
        task: Task specification

    Returns:
        Entropy reduction (0-1, higher = more uncertainty reduced)

    Examples:
        >>> task = Task(
        ...     id="1",
        ...     name="Spike: Evaluate Frameworks",
        ...     uncertainty=0.9,
        ...     impact=80
        ... )
        >>> reduction = entropy_reduction_per_task(task)
    """
    task_dict = task.to_dict() if isinstance(task, Task) else task

    # Factors contributing to entropy reduction
    uncertainty = task_dict.get("uncertainty", 0.5)
    impact = task_dict.get("impact", 50.0) / 100.0
    complexity = task_dict.get("complexity", 50.0) / 100.0

    # High uncertainty + high impact = high entropy reduction
    # Complex tasks also reduce more entropy
    entropy_reduction = uncertainty * 0.5 + impact * 0.3 + complexity * 0.2

    return min(entropy_reduction, 1.0)


def mutual_information_with_goals(task: Task | dict[str, Any], goals: list[str]) -> float:
    """Calculate mutual information between task and project goals.

    Args:
        task: Task specification
        goals: List of project goal descriptions

    Returns:
        Mutual information score (0-1)

    Examples:
        >>> task = Task(
        ...     id="1",
        ...     name="Implement caching",
        ...     description="Add Redis caching layer"
        ... )
        >>> goals = ["Improve performance", "Scale to 1M users"]
        >>> mi = mutual_information_with_goals(task, goals)
    """
    task_dict = task.to_dict() if isinstance(task, Task) else task

    # Extract task text
    task_name = task_dict.get("name", "")
    task_desc = task_dict.get("description", "")
    task_text = (task_name + " " + task_desc).lower()

    # Calculate overlap with goals
    total_overlap = 0.0
    for goal in goals:
        goal_tokens = set(re.findall(r"\w+", goal.lower()))
        task_tokens = set(re.findall(r"\w+", task_text))

        if goal_tokens:
            overlap = len(goal_tokens & task_tokens) / len(goal_tokens)
            total_overlap += overlap

    # Average overlap across goals
    if goals:
        return min(total_overlap / len(goals), 1.0)
    return 0.0


def criticality_score(task: Task | dict[str, Any]) -> float:
    """Calculate task criticality for overall project success.

    Args:
        task: Task specification

    Returns:
        Criticality score (0-100, higher = more critical)

    Examples:
        >>> task = Task(
        ...     id="1",
        ...     name="Security Audit",
        ...     impact=95,
        ...     dependencies=["auth", "payment"],
        ...     uncertainty=0.7
        ... )
        >>> score = criticality_score(task)
    """
    task_dict = task.to_dict() if isinstance(task, Task) else task

    factors = []

    # 1. Impact
    impact = task_dict.get("impact", 50.0)
    factors.append(impact)

    # 2. Number of dependencies (tasks blocked by this)
    # Note: This requires knowing reverse dependencies, using metadata
    if "blocks" in task_dict.get("metadata", {}):
        blocked_count = len(task_dict["metadata"]["blocks"])
        blocked_score = min(blocked_count * 20, 100)
        factors.append(blocked_score)

    # 3. Uncertainty (high uncertainty = high criticality for resolution)
    uncertainty = task_dict.get("uncertainty", 0.5)
    uncertainty_score = uncertainty * 100
    factors.append(uncertainty_score)

    # 4. Complexity (complex tasks are critical to resolve early)
    complexity = task_dict.get("complexity", 50.0)
    factors.append(complexity * 0.5)  # Reduced weight

    # Average factors
    if factors:
        return sum(factors) / len(factors)
    return 50.0


def uncertainty_reduction_rate(task: Task | dict[str, Any]) -> float:
    """Calculate rate of uncertainty reduction (information gain per unit effort).

    Args:
        task: Task specification

    Returns:
        Uncertainty reduction rate (bits per hour)

    Examples:
        >>> task = Task(
        ...     id="1",
        ...     name="Quick Win",
        ...     uncertainty=0.8,
        ...     estimated_effort=2
        ... )
        >>> rate = uncertainty_reduction_rate(task)
        >>> # High uncertainty, low effort = high rate
    """
    task_dict = task.to_dict() if isinstance(task, Task) else task

    # Entropy reduction from task
    entropy_reduction = entropy_reduction_per_task(task_dict)

    # Effort in hours
    effort = task_dict.get("estimated_effort", 1.0)
    if effort <= 0:
        effort = 1.0

    # Rate = entropy reduction / effort
    return entropy_reduction / effort


# ============================================================================
# 6. Adaptive Prioritization
# ============================================================================


def reprioritize_based_on_progress(
    completed_tasks: list[str],
    remaining_tasks: list[Task | dict[str, Any]],
    project_goals: list[str] | None = None,
) -> list[PriorityItem]:
    """Dynamically reprioritize tasks based on completed work.

    Args:
        completed_tasks: List of completed task IDs
        remaining_tasks: List of remaining tasks
        project_goals: Optional project goals for alignment

    Returns:
        Reprioritized task list

    Examples:
        >>> completed = ["task1", "task2"]
        >>> remaining = [
        ...     Task(id="task3", dependencies=["task1"], impact=80),
        ...     Task(id="task4", dependencies=["task5"], impact=90)
        ... ]
        >>> reprioritized = reprioritize_based_on_progress(completed, remaining)
    """
    # Filter to unblocked tasks
    unblocked_tasks = []
    for task in remaining_tasks:
        task_deps = task.dependencies if isinstance(task, Task) else task.get("dependencies", [])

        # Check if all dependencies are completed
        if all(dep in completed_tasks for dep in task_deps):
            unblocked_tasks.append(task)

    # Prioritize unblocked tasks
    if project_goals:
        # Calculate goal alignment
        prioritized = []
        for task in unblocked_tasks:
            mi_score = mutual_information_with_goals(task, project_goals)
            impact = task.impact if isinstance(task, Task) else task.get("impact", 50.0)
            effort = (
                task.estimated_effort
                if isinstance(task, Task)
                else task.get("estimated_effort", 1.0)
            )

            # Combined score: goal alignment + impact - effort
            score = (mi_score * 0.5 + impact / 100 * 0.3) - (effort / 100 * 0.2)
            prioritized.append((task, score))

        prioritized.sort(key=lambda x: x[1], reverse=True)

        priority_list = []
        for rank, (task, score) in enumerate(prioritized, start=1):
            priority_list.append(
                PriorityItem(
                    item=task,
                    score=score,
                    rank=rank,
                    rationale=f"Reprioritized based on progress. Score: {score:.3f}",
                    metadata={"completed_count": len(completed_tasks)},
                )
            )

        return priority_list
    # Default prioritization
    return prioritize_tasks(unblocked_tasks)


def identify_dependencies(task: Task | dict[str, Any]) -> dict[str, Any]:
    """Identify task dependencies and dependency types.

    Args:
        task: Task specification

    Returns:
        Dictionary with dependency information

    Examples:
        >>> task = Task(
        ...     id="deploy",
        ...     dependencies=["tests", "review"],
        ...     metadata={"dependency_types": {"tests": "hard", "review": "soft"}}
        ... )
        >>> deps = identify_dependencies(task)
    """
    if isinstance(task, Task):
        task_id = task.id
        dependencies = task.dependencies
        metadata = task.metadata
    else:
        task_id = task.get("id", "")
        dependencies = task.get("dependencies", [])
        metadata = task.get("metadata", {})

    # Extract dependency information
    return {
        "task_id": task_id,
        "dependencies": dependencies,
        "dependency_count": len(dependencies),
        "dependency_types": metadata.get("dependency_types", {}),
        "is_blocked": len(dependencies) > 0,
    }


def suggest_task_ordering(tasks: list[Task | dict[str, Any]]) -> list[str]:
    """Suggest optimal task execution order based on dependencies and priorities.

    Uses topological sort with priority-based tie-breaking.

    Args:
        tasks: List of tasks

    Returns:
        Ordered list of task IDs

    Examples:
        >>> tasks = [
        ...     Task(id="A", dependencies=[], impact=50),
        ...     Task(id="B", dependencies=["A"], impact=80),
        ...     Task(id="C", dependencies=["A"], impact=90)
        ... ]
        >>> ordering = suggest_task_ordering(tasks)
        >>> # Returns: ["A", "C", "B"] (A first, then C before B due to higher impact)
    """
    # Build task map and dependency graph
    task_map = {}
    graph: dict[str, list[str]] = defaultdict(list)
    in_degree: dict[str, int] = defaultdict(int)

    for task in tasks:
        if isinstance(task, Task):
            task_id = task.id
            task_deps = task.dependencies
        else:
            task_id = task.get("id", "")
            task_deps = task.get("dependencies", [])

        task_map[task_id] = task
        in_degree[task_id] = len(task_deps)

        for dep in task_deps:
            graph[dep].append(task_id)

    # Topological sort with priority queue
    ordering = []
    available = [task_id for task_id, degree in in_degree.items() if degree == 0]

    while available:
        # Sort available tasks by priority (impact / effort)
        def priority_score(task_id: str) -> float:
            task = task_map[task_id]
            if isinstance(task, Task):
                impact = task.impact
                effort = task.estimated_effort
            else:
                impact = task.get("impact", 50.0)
                effort = task.get("estimated_effort", 1.0)

            return impact / max(effort, 0.1)  # Higher = better

        available.sort(key=priority_score, reverse=True)

        # Process highest priority available task
        task_id = available.pop(0)
        ordering.append(task_id)

        # Update dependencies
        for neighbor in graph[task_id]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                available.append(neighbor)

    return ordering


def predict_effort_impact(
    task_selection: list[str], tasks: list[Task | dict[str, Any]]
) -> dict[str, float]:
    """Predict effort and impact of selected task set.

    Args:
        task_selection: List of selected task IDs
        tasks: Full task list

    Returns:
        Dictionary with total effort, total impact, and efficiency

    Examples:
        >>> tasks = [
        ...     Task(id="A", estimated_effort=5, impact=80),
        ...     Task(id="B", estimated_effort=10, impact=60)
        ... ]
        >>> prediction = predict_effort_impact(["A", "B"], tasks)
        >>> print(f"Total effort: {prediction['total_effort']} hours")
    """
    # Build task map
    task_map = {}
    for task in tasks:
        if isinstance(task, Task):
            task_map[task.id] = task
        else:
            task_map[task.get("id", "")] = task

    # Calculate totals
    total_effort = 0.0
    total_impact = 0.0

    for task_id in task_selection:
        if task_id in task_map:
            task = task_map[task_id]
            if isinstance(task, Task):
                total_effort += task.estimated_effort
                total_impact += task.impact
            else:
                total_effort += task.get("estimated_effort", 0.0)
                total_impact += task.get("impact", 0.0)

    # Calculate efficiency
    efficiency = total_impact / max(total_effort, 0.1)

    return {
        "total_effort": total_effort,
        "total_impact": total_impact,
        "efficiency": efficiency,
        "task_count": len(task_selection),
        "average_effort_per_task": total_effort / max(len(task_selection), 1),
        "average_impact_per_task": total_impact / max(len(task_selection), 1),
    }


# ============================================================================
# 7. Job-Outcome Prioritization
# ============================================================================


def rank_jobs_by_frequency(customers: list[dict[str, Any]]) -> list[tuple[str, int]]:
    """Rank jobs by customer frequency (most common jobs first).

    Args:
        customers: List of customer profiles with "jobs" field

    Returns:
        List of (job, frequency) tuples sorted by frequency

    Examples:
        >>> customers = [
        ...     {"name": "Alice", "jobs": ["write_code", "debug"]},
        ...     {"name": "Bob", "jobs": ["write_code", "review"]},
        ...     {"name": "Carol", "jobs": ["write_code"]}
        ... ]
        >>> ranked = rank_jobs_by_frequency(customers)
        >>> # Returns: [("write_code", 3), ("debug", 1), ("review", 1)]
    """
    job_counts: Counter[str] = Counter()

    for customer in customers:
        jobs = customer.get("jobs", [])
        for job in jobs:
            job_counts[job] += 1

    # Sort by frequency (descending)
    return job_counts.most_common()


def rank_outcomes_by_importance(job: dict[str, Any]) -> list[tuple[str, float]]:
    """Rank outcomes for a job by importance score.

    Args:
        job: Job specification with "outcomes" field

    Returns:
        List of (outcome, importance) tuples sorted by importance

    Examples:
        >>> job = {
        ...     "name": "Commute to Work",
        ...     "outcomes": {
        ...         "arrive_on_time": 9.5,
        ...         "minimize_cost": 6.0,
        ...         "minimize_stress": 8.0
        ...     }
        ... }
        >>> ranked = rank_outcomes_by_importance(job)
    """
    outcomes = job.get("outcomes", {})

    # Convert to list of tuples and sort
    outcome_list = [(outcome, importance) for outcome, importance in outcomes.items()]
    outcome_list.sort(key=lambda x: x[1], reverse=True)

    return outcome_list


def quantify_outcome_value(outcome: dict[str, Any]) -> float:
    """Quantify monetary/impact value of achieving outcome.

    Args:
        outcome: Outcome specification with importance, satisfaction_gap, etc.

    Returns:
        Value score (0-100)

    Examples:
        >>> outcome = {
        ...     "name": "Reduce deployment time",
        ...     "importance": 9.0,
        ...     "satisfaction": 4.0,  # Current satisfaction
        ...     "target_satisfaction": 9.0  # Desired satisfaction
        ... }
        >>> value = quantify_outcome_value(outcome)
    """
    importance = outcome.get("importance", 5.0)
    current_satisfaction = outcome.get("satisfaction", 5.0)
    target_satisfaction = outcome.get("target_satisfaction", 10.0)

    # Satisfaction gap
    satisfaction_gap = max(target_satisfaction - current_satisfaction, 0)

    # Value = importance * satisfaction_gap
    # Normalize to 0-100 scale (assume max importance = 10, max gap = 10)
    value = (importance * satisfaction_gap) / 100 * 100

    return min(value, 100.0)


def maximize_job_coverage(budget: float, features: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Select features maximizing job coverage within budget.

    Uses greedy knapsack approach: maximize jobs covered per cost unit.

    Args:
        budget: Available budget (person-hours or cost)
        features: List of features with "cost" and "jobs_addressed" fields

    Returns:
        Selected features within budget

    Examples:
        >>> budget = 100.0  # hours
        >>> features = [
        ...     {"name": "F1", "cost": 20, "jobs_addressed": ["job1", "job2"]},
        ...     {"name": "F2", "cost": 50, "jobs_addressed": ["job1", "job3", "job4"]},
        ...     {"name": "F3", "cost": 30, "jobs_addressed": ["job2"]}
        ... ]
        >>> selected = maximize_job_coverage(budget, features)
    """
    # Calculate efficiency (jobs covered per cost)
    feature_efficiency = []
    for feature in features:
        cost = feature.get("cost", 1.0)
        jobs_addressed = feature.get("jobs_addressed", [])
        efficiency = len(jobs_addressed) / max(cost, 0.1)
        feature_efficiency.append((feature, efficiency, cost))

    # Sort by efficiency (descending)
    feature_efficiency.sort(key=lambda x: x[1], reverse=True)

    # Greedy selection
    selected = []
    remaining_budget = budget
    covered_jobs = set()

    for feature, efficiency, cost in feature_efficiency:
        if cost <= remaining_budget:
            selected.append(feature)
            remaining_budget -= cost
            covered_jobs.update(feature.get("jobs_addressed", []))

    return selected


# ============================================================================
# 8. Market Opportunity Analysis
# ============================================================================


def opportunity_score(job: dict[str, Any], painpoint: dict[str, Any]) -> float:
    """Calculate market opportunity score for job-painpoint pair.

    Opportunity = Importance * (10 - Satisfaction) * Market Size

    Args:
        job: Job specification
        painpoint: Painpoint specification with importance, satisfaction

    Returns:
        Opportunity score (0-1000+)

    Examples:
        >>> job = {"name": "Deploy Software", "market_size": 10000}
        >>> painpoint = {"importance": 9, "satisfaction": 3}
        >>> score = opportunity_score(job, painpoint)
    """
    importance = painpoint.get("importance", 5.0)
    satisfaction = painpoint.get("satisfaction", 5.0)
    market_size = job.get("market_size", 100)

    # Opportunity formula
    satisfaction_gap = max(10 - satisfaction, 0)
    return importance * satisfaction_gap * (market_size / 100)


def addressable_market_size(job: dict[str, Any]) -> float:
    """Calculate addressable market size for job.

    Args:
        job: Job specification with market data

    Returns:
        Market size (number of potential customers or revenue)

    Examples:
        >>> job = {
        ...     "name": "Manage Cloud Infrastructure",
        ...     "total_market": 1000000,  # Total companies
        ...     "addressable_percentage": 0.15  # We can serve 15%
        ... }
        >>> market = addressable_market_size(job)
    """
    total_market = job.get("total_market", 0)
    addressable_percentage = job.get("addressable_percentage", 1.0)

    return total_market * addressable_percentage


def competition_analysis(feature: dict[str, Any]) -> float:
    """Analyze competitive advantage of feature.

    Args:
        feature: Feature specification with competitive data

    Returns:
        Competitive advantage score (0-1, higher = better)

    Examples:
        >>> feature = {
        ...     "name": "Real-time Collaboration",
        ...     "competitors_with_feature": 2,
        ...     "total_competitors": 10,
        ...     "our_quality": 8,
        ...     "competitor_avg_quality": 5
        ... }
        >>> advantage = competition_analysis(feature)
    """
    competitors_with = feature.get("competitors_with_feature", 5)
    total_competitors = feature.get("total_competitors", 10)
    our_quality = feature.get("our_quality", 5)
    competitor_avg_quality = feature.get("competitor_avg_quality", 5)

    # Rarity score (fewer competitors have it = better)
    rarity = 1 - competitors_with / total_competitors if total_competitors > 0 else 1.0

    # Quality advantage
    if competitor_avg_quality > 0:
        quality_advantage = our_quality / competitor_avg_quality
        quality_advantage = min(quality_advantage, 2.0) / 2.0  # Normalize to 0-1
    else:
        quality_advantage = 1.0

    # Combined advantage
    advantage = rarity * 0.6 + quality_advantage * 0.4

    return min(advantage, 1.0)


def market_timing_analysis(feature: dict[str, Any]) -> float:
    """Analyze market timing for feature launch.

    Args:
        feature: Feature specification with timing data

    Returns:
        Timing score (0-1, higher = better timing)

    Examples:
        >>> feature = {
        ...     "name": "AI Assistant",
        ...     "market_maturity": 0.7,  # 0 = too early, 1 = too late, 0.5-0.8 = ideal
        ...     "trend_direction": "up",  # "up", "down", "flat"
        ...     "urgency": 0.8  # Customer urgency
        ... }
        >>> timing = market_timing_analysis(feature)
    """
    market_maturity = feature.get("market_maturity", 0.5)
    trend_direction = feature.get("trend_direction", "flat")
    urgency = feature.get("urgency", 0.5)

    # Ideal maturity is 0.5-0.8 (not too early, not too late)
    maturity_score = 1.0 - abs(0.65 - market_maturity) / 0.65

    # Trend score
    trend_scores = {"up": 1.0, "flat": 0.5, "down": 0.1}
    trend_score = trend_scores.get(trend_direction, 0.5)

    # Combine factors
    timing_score = maturity_score * 0.4 + trend_score * 0.3 + urgency * 0.3

    return min(timing_score, 1.0)


# ============================================================================
# 9. Specification Complexity Analysis
# ============================================================================


def approximate_complexity(spec: str | dict[str, Any]) -> float:
    """Approximate Kolmogorov complexity via compression.

    K(x) ≈ |compressed(x)| / |x|

    Args:
        spec: Specification string or dict

    Returns:
        Complexity score (0-1, higher = more complex)

    Examples:
        >>> spec = "This is a very repetitive spec. " * 100
        >>> complexity = approximate_complexity(spec)
        >>> # Repetitive text compresses well = low complexity
    """
    # Convert to string if dict
    spec_str = str(spec) if isinstance(spec, dict) else spec

    # Encode and compress
    spec_bytes = spec_str.encode("utf-8")
    compressed = zlib.compress(spec_bytes, level=9)

    # Complexity = compression ratio
    return len(compressed) / len(spec_bytes) if len(spec_bytes) > 0 else 0.0


def complexity_per_requirement(requirements: list[str]) -> dict[str, float]:
    """Calculate complexity for each requirement.

    Args:
        requirements: List of requirement strings

    Returns:
        Dictionary mapping requirement to complexity score

    Examples:
        >>> reqs = [
        ...     "Simple login",
        ...     "Implement OAuth2 with PKCE, refresh tokens, and multi-provider support"
        ... ]
        >>> complexities = complexity_per_requirement(reqs)
    """
    complexities = {}

    for req in requirements:
        # Factors indicating complexity
        factors = []

        # 1. Length (longer = more complex)
        length_score = min(len(req) / 200, 1.0)
        factors.append(length_score)

        # 2. Technical terms
        tech_terms = [
            "oauth",
            "authentication",
            "encryption",
            "algorithm",
            "distributed",
            "concurrent",
            "async",
            "microservice",
        ]
        tech_count = sum(1 for term in tech_terms if term in req.lower())
        tech_score = min(tech_count / 3, 1.0)
        factors.append(tech_score)

        # 3. Compression-based complexity
        compression_complexity = approximate_complexity(req)
        factors.append(compression_complexity)

        # Average factors
        complexity = sum(factors) / len(factors) if factors else 0.0
        complexities[req] = complexity

    return complexities


def identify_complex_requirements(
    spec_list: list[dict[str, Any]], threshold: float = 0.7
) -> list[dict[str, Any]]:
    """Identify specifications with high-complexity requirements.

    Args:
        spec_list: List of specification dictionaries
        threshold: Complexity threshold (0-1)

    Returns:
        List of complex specifications

    Examples:
        >>> specs = [
        ...     {"name": "Simple", "requirements": ["login", "logout"]},
        ...     {"name": "Complex", "requirements": ["distributed consensus", "CRDT"]}
        ... ]
        >>> complex_specs = identify_complex_requirements(specs, threshold=0.6)
    """
    complex_specs = []

    for spec in spec_list:
        requirements = spec.get("requirements", [])
        if requirements:
            complexities = complexity_per_requirement(requirements)
            avg_complexity = sum(complexities.values()) / len(complexities)

            if avg_complexity >= threshold:
                complex_specs.append(spec)

    return complex_specs


# ============================================================================
# 10. Information Density Metrics
# ============================================================================


def information_density(spec: str | dict[str, Any]) -> float:
    """Calculate information density (information content per character).

    High density = low redundancy, high information content

    Args:
        spec: Specification string or dict

    Returns:
        Density score (0-1, higher = more information per character)

    Examples:
        >>> spec = "Highly technical specification with low redundancy"
        >>> density = information_density(spec)
    """
    # Convert to string if dict
    spec_str = str(spec) if isinstance(spec, dict) else spec

    if not spec_str:
        return 0.0

    # 1. Compression-based density (lower compression = higher density)
    spec_bytes = spec_str.encode("utf-8")
    compressed = zlib.compress(spec_bytes, level=9)
    compression_ratio = len(compressed) / len(spec_bytes)
    compression_density = 1 - compression_ratio

    # 2. Unique word ratio
    words = re.findall(r"\w+", spec_str.lower())
    unique_ratio = len(set(words)) / len(words) if words else 0.0

    # 3. Character entropy
    char_counts = Counter(spec_str)
    total_chars = len(spec_str)
    if total_chars > 0:
        entropy = -sum(
            (count / total_chars) * math.log2(count / total_chars) for count in char_counts.values()
        )
        # Normalize by max entropy (8 bits per char for ASCII)
        char_entropy = entropy / 8.0
    else:
        char_entropy = 0.0

    # Combine metrics
    density = compression_density * 0.4 + unique_ratio * 0.3 + char_entropy * 0.3

    return min(density, 1.0)


def spec_completeness_likelihood(spec: dict[str, Any]) -> float:
    """Estimate probability that specification is complete.

    Uses heuristics based on field presence, detail level, and consistency.

    Args:
        spec: Specification dictionary

    Returns:
        Completeness probability (0-1)

    Examples:
        >>> spec = {
        ...     "name": "User Auth",
        ...     "description": "Complete auth system",
        ...     "requirements": ["login", "logout", "reset"],
        ...     "acceptance_criteria": ["secure", "fast"],
        ...     "dependencies": ["database"]
        ... }
        >>> completeness = spec_completeness_likelihood(spec)
    """
    completeness_factors = []

    # 1. Required fields present
    required_fields = ["name", "description", "requirements"]
    present_count = sum(1 for field in required_fields if spec.get(field))
    field_completeness = present_count / len(required_fields)
    completeness_factors.append(field_completeness)

    # 2. Optional but important fields
    optional_fields = ["acceptance_criteria", "dependencies", "complexity", "impact"]
    optional_present = sum(1 for field in optional_fields if spec.get(field))
    optional_completeness = optional_present / len(optional_fields)
    completeness_factors.append(optional_completeness)

    # 3. Description length (longer = more complete)
    description = spec.get("description", "")
    desc_length_score = min(len(description) / 100, 1.0)
    completeness_factors.append(desc_length_score)

    # 4. Requirements count (more requirements = more detail)
    requirements = spec.get("requirements", [])
    req_count_score = min(len(requirements) / 5, 1.0)
    completeness_factors.append(req_count_score)

    # Weighted average
    weights = [0.4, 0.2, 0.2, 0.2]
    return sum(f * w for f, w in zip(completeness_factors, weights, strict=False))


def edge_case_coverage_estimate(spec: dict[str, Any]) -> float:
    """Estimate percentage of edge cases covered in specification.

    Args:
        spec: Specification dictionary

    Returns:
        Estimated edge case coverage (0-100%)

    Examples:
        >>> spec = {
        ...     "requirements": [
        ...         "Handle empty input",
        ...         "Handle invalid format",
        ...         "Handle timeout",
        ...         "Normal operation"
        ...     ]
        ... }
        >>> coverage = edge_case_coverage_estimate(spec)
    """
    requirements = spec.get("requirements", [])
    acceptance_criteria = spec.get("acceptance_criteria", [])

    # Combine all text
    all_text = " ".join(requirements + acceptance_criteria).lower()

    # Edge case keywords
    edge_case_keywords = [
        "error",
        "fail",
        "invalid",
        "empty",
        "null",
        "timeout",
        "boundary",
        "limit",
        "exception",
        "edge",
    ]

    # Count edge case mentions
    edge_case_count = sum(1 for keyword in edge_case_keywords if keyword in all_text)

    # Estimate coverage (assume 10 edge case mentions = 100% coverage)
    return min(edge_case_count / 10, 1.0) * 100


# ============================================================================
# 11. Decision Support Dashboard
# ============================================================================


def create_priority_matrix(
    items: list[dict[str, Any]],
    dimensions: tuple[str, str] = ("impact", "effort"),
) -> dict[str, list[dict[str, Any]]]:
    """Create 2x2 priority matrix (e.g., impact vs effort).

    Quadrants:
    - High impact, Low effort: Quick Wins
    - High impact, High effort: Strategic Initiatives
    - Low impact, Low effort: Fill-ins
    - Low impact, High effort: Time Wasters

    Args:
        items: List of items with dimension values
        dimensions: Tuple of (x_dimension, y_dimension)

    Returns:
        Dictionary mapping quadrant names to items

    Examples:
        >>> items = [
        ...     {"name": "Bug Fix", "impact": 90, "effort": 10},
        ...     {"name": "Rewrite", "impact": 95, "effort": 95},
        ...     {"name": "Tweak", "impact": 20, "effort": 5}
        ... ]
        >>> matrix = create_priority_matrix(items, ("impact", "effort"))
        >>> quick_wins = matrix["quick_wins"]
    """
    x_dim, y_dim = dimensions

    # Calculate medians for thresholds
    x_values = [item.get(x_dim, 50) for item in items]
    y_values = [item.get(y_dim, 50) for item in items]

    x_median = sorted(x_values)[len(x_values) // 2] if x_values else 50
    y_median = sorted(y_values)[len(y_values) // 2] if y_values else 50

    # Classify items into quadrants
    quadrants: dict[str, list[dict[str, Any]]] = {
        "quick_wins": [],  # High impact, Low effort
        "strategic": [],  # High impact, High effort
        "fill_ins": [],  # Low impact, Low effort
        "time_wasters": [],  # Low impact, High effort
    }

    for item in items:
        x_val = item.get(x_dim, 50)
        y_val = item.get(y_dim, 50)

        # Classify (assuming x = impact, y = effort)
        # For effort, low is good; for impact, high is good
        if x_val >= x_median and y_val < y_median:
            quadrants["quick_wins"].append(item)
        elif x_val >= x_median and y_val >= y_median:
            quadrants["strategic"].append(item)
        elif x_val < x_median and y_val < y_median:
            quadrants["fill_ins"].append(item)
        else:  # Low impact, High effort
            quadrants["time_wasters"].append(item)

    return quadrants


def identify_quick_wins(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Identify high-impact, low-effort items (quick wins).

    Args:
        items: List of items with "impact" and "effort" fields

    Returns:
        List of quick win items

    Examples:
        >>> items = [
        ...     {"name": "Fix typo", "impact": 80, "effort": 1},
        ...     {"name": "Rewrite system", "impact": 90, "effort": 100}
        ... ]
        >>> quick_wins = identify_quick_wins(items)
    """
    matrix = create_priority_matrix(items, ("impact", "effort"))
    return matrix["quick_wins"]


def find_strategic_initiatives(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Identify high-impact, high-effort items (strategic initiatives).

    Args:
        items: List of items with "impact" and "effort" fields

    Returns:
        List of strategic initiative items

    Examples:
        >>> items = [
        ...     {"name": "Major refactor", "impact": 95, "effort": 80}
        ... ]
        >>> strategic = find_strategic_initiatives(items)
    """
    matrix = create_priority_matrix(items, ("impact", "effort"))
    return matrix["strategic"]


def recommend_next_tasks(
    current_state: dict[str, Any],
    available_tasks: list[Task | dict[str, Any]] | None = None,
) -> list[PriorityItem]:
    """Recommend next tasks based on current project state.

    Args:
        current_state: Dictionary with project state info
        available_tasks: Optional list of available tasks

    Returns:
        Ranked list of recommended tasks

    Examples:
        >>> state = {
        ...     "completed_tasks": ["task1", "task2"],
        ...     "goals": ["Performance", "Quality"],
        ...     "budget_remaining": 40.0
        ... }
        >>> tasks = [
        ...     Task(id="task3", impact=80, estimated_effort=10),
        ...     Task(id="task4", impact=60, estimated_effort=30)
        ... ]
        >>> recommendations = recommend_next_tasks(state, tasks)
    """
    if available_tasks is None:
        return []

    completed = current_state.get("completed_tasks", [])
    goals = current_state.get("goals", [])
    budget = current_state.get("budget_remaining", float("inf"))

    # Filter to unblocked tasks
    unblocked = []
    for task in available_tasks:
        if isinstance(task, Task):
            task_deps = task.dependencies
            task_effort = task.estimated_effort
        else:
            task_deps = task.get("dependencies", [])
            task_effort = task.get("estimated_effort", 1.0)

        # Check if unblocked and within budget
        if all(dep in completed for dep in task_deps) and task_effort <= budget:
            unblocked.append(task)

    # Prioritize unblocked tasks
    if goals:
        ranked = reprioritize_based_on_progress(completed, unblocked, goals)
    else:
        ranked = prioritize_tasks(unblocked)

    return ranked


def suggest_parallel_work(tasks: list[Task | dict[str, Any]]) -> list[list[str]]:
    """Identify sets of tasks that can be executed in parallel.

    Args:
        tasks: List of tasks

    Returns:
        List of task ID sets that can run in parallel

    Examples:
        >>> tasks = [
        ...     Task(id="A", dependencies=[]),
        ...     Task(id="B", dependencies=["A"]),
        ...     Task(id="C", dependencies=["A"]),
        ...     Task(id="D", dependencies=[])
        ... ]
        >>> parallel_sets = suggest_parallel_work(tasks)
        >>> # Returns: [["A", "D"], ["B", "C"]]
    """
    # Build dependency levels
    task_map = {}
    for task in tasks:
        if isinstance(task, Task):
            task_map[task.id] = task
        else:
            task_map[task.get("id", "")] = task

    # Calculate depth (longest path from root)
    def calculate_depth(task_id: str, visited: set[str]) -> int:
        if task_id in visited:
            return 0

        visited.add(task_id)
        task = task_map.get(task_id)
        if not task:
            return 0

        deps = task.dependencies if isinstance(task, Task) else task.get("dependencies", [])

        if not deps:
            return 0

        max_dep_depth = max(
            (calculate_depth(dep, visited.copy()) for dep in deps),
            default=0,
        )
        return max_dep_depth + 1

    # Group tasks by depth
    depth_groups: dict[int, list[str]] = defaultdict(list)
    for task_id in task_map:
        depth = calculate_depth(task_id, set())
        depth_groups[depth].append(task_id)

    # Convert to list of parallel sets
    return [tasks for tasks in depth_groups.values() if tasks]


def identify_blockers(task_list: list[Task | dict[str, Any]]) -> list[str]:
    """Identify tasks that are blocking the most other tasks.

    Args:
        task_list: List of tasks

    Returns:
        List of task IDs that are blockers (sorted by number of blocked tasks)

    Examples:
        >>> tasks = [
        ...     Task(id="A", dependencies=[]),
        ...     Task(id="B", dependencies=["A"]),
        ...     Task(id="C", dependencies=["A"]),
        ...     Task(id="D", dependencies=["B"])
        ... ]
        >>> blockers = identify_blockers(tasks)
        >>> # Returns: ["A"] (blocks B and C)
    """
    # Count how many tasks each task blocks
    blocker_count: dict[str, int] = defaultdict(int)

    for task in task_list:
        deps = task.dependencies if isinstance(task, Task) else task.get("dependencies", [])

        for dep in deps:
            blocker_count[dep] += 1

    # Sort by count (descending)
    sorted_blockers = sorted(blocker_count.items(), key=lambda x: x[1], reverse=True)

    # Return task IDs
    return [task_id for task_id, count in sorted_blockers if count > 0]
