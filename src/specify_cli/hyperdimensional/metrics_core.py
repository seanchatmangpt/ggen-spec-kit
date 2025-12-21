"""Essential information-theoretic metrics for decision-making (80/20 approach).

This module provides the core metrics that deliver 80% of value:
- Shannon entropy
- Mutual information (frequency-based)
- Information gain (feature selection)
- KL divergence (simplified)

Deliberately simple: No numerical stability, no edge cases, no optimization.
Add complexity later only if needed.
"""

from __future__ import annotations

import math
from collections import Counter
from typing import Any

import numpy as np
import numpy.typing as npt

FloatArray = npt.NDArray[np.floating[Any]]


def entropy(data: list[float]) -> float:
    """Shannon entropy in bits."""
    total = sum(data)
    if total == 0:
        return 0.0
    probs = [x / total for x in data if x > 0]
    return -sum(p * math.log2(p) for p in probs)


def mutual_information(x: list[Any], y: list[Any]) -> float:
    """Mutual information I(X;Y) using frequency counts."""
    if len(x) != len(y):
        raise ValueError("x and y must have same length")

    n = len(x)
    # Joint and marginal counts
    xy_counts = Counter(zip(x, y, strict=False))
    x_counts = Counter(x)
    y_counts = Counter(y)

    mi = 0.0
    for (xi, yi), count_xy in xy_counts.items():
        p_xy = count_xy / n
        p_x = x_counts[xi] / n
        p_y = y_counts[yi] / n
        mi += p_xy * math.log2(p_xy / (p_x * p_y))

    return mi


def information_gain(feature_values: list[Any], target_values: list[Any]) -> float:
    """Information gain for feature selection."""
    return mutual_information(feature_values, target_values)


def kullback_leibler(p: dict[Any, float], q: dict[Any, float]) -> float:
    """KL divergence D_KL(P||Q) in bits."""
    kl = 0.0
    for key, p_val in p.items():
        if p_val > 0:
            q_val = q.get(key, 1e-10)  # Avoid log(0)
            kl += p_val * math.log2(p_val / q_val)
    return kl


def entropy_from_samples(samples: list[float], bins: int = 10) -> float:
    """Entropy from continuous samples using histogram."""
    hist, _ = np.histogram(samples, bins=bins)
    return entropy([float(x) for x in hist])


def joint_entropy(x: list[Any], y: list[Any]) -> float:
    """Joint entropy H(X,Y)."""
    if len(x) != len(y):
        raise ValueError("x and y must have same length")

    xy_counts = Counter(zip(x, y, strict=False))
    counts = list(xy_counts.values())
    return entropy([float(c) for c in counts])


def conditional_entropy(x: list[Any], y: list[Any]) -> float:
    """Conditional entropy H(Y|X) = H(X,Y) - H(X)."""
    h_xy = joint_entropy(x, y)
    x_counts = Counter(x)
    h_x = entropy([float(c) for c in x_counts.values()])
    return h_xy - h_x


def normalized_mutual_information(x: list[Any], y: list[Any]) -> float:
    """Normalized MI in [0,1]: I(X;Y) / sqrt(H(X)*H(Y))."""
    mi = mutual_information(x, y)

    x_counts = Counter(x)
    y_counts = Counter(y)
    h_x = entropy([float(c) for c in x_counts.values()])
    h_y = entropy([float(c) for c in y_counts.values()])

    if h_x == 0 or h_y == 0:
        return 0.0

    return mi / math.sqrt(h_x * h_y)


def discretize(values: list[float], bins: int = 10) -> list[int]:
    """Discretize continuous values into bins."""
    if not values:
        return []
    arr = np.array(values)
    _, bin_edges = np.histogram(arr, bins=bins)
    digitized = np.digitize(arr, bin_edges[:-1])
    return [int(x) for x in digitized]


def feature_selection_score(
    feature: list[float],
    target: list[Any],
    bins: int = 10,
) -> float:
    """Score feature by information gain (higher = better)."""
    feature_discrete = discretize(feature, bins=bins)
    return information_gain(feature_discrete, target)


def redundancy_score(feature1: list[float], feature2: list[float], bins: int = 10) -> float:
    """Measure redundancy between features (higher = more redundant)."""
    f1_discrete = discretize(feature1, bins=bins)
    f2_discrete = discretize(feature2, bins=bins)
    return mutual_information(f1_discrete, f2_discrete)


def jensen_shannon_divergence(p: dict[Any, float], q: dict[Any, float]) -> float:
    """Jensen-Shannon divergence (symmetric version of KL)."""
    # Mixture distribution
    all_keys = set(p.keys()) | set(q.keys())
    m = {k: 0.5 * (p.get(k, 0) + q.get(k, 0)) for k in all_keys}

    return 0.5 * kullback_leibler(p, m) + 0.5 * kullback_leibler(q, m)


def cross_entropy(p: dict[Any, float], q: dict[Any, float]) -> float:
    """Cross-entropy H(P,Q) = -Σ p(x) log q(x)."""
    ce = 0.0
    for key, p_val in p.items():
        if p_val > 0:
            q_val = q.get(key, 1e-10)
            ce -= p_val * math.log2(q_val)
    return ce


def gini_impurity(counts: list[int]) -> float:
    """Gini impurity for decision trees."""
    total = sum(counts)
    if total == 0:
        return 0.0
    return 1.0 - sum((c / total) ** 2 for c in counts)


def gini_gain(
    feature_values: list[Any],
    target_values: list[Any],
) -> float:
    """Gini-based information gain."""
    if len(feature_values) != len(target_values):
        raise ValueError("feature and target must have same length")

    # Overall gini
    target_counts = Counter(target_values)
    gini_total = gini_impurity(list(target_counts.values()))

    # Weighted gini per feature value
    n_total = len(target_values)
    feature_groups: dict[Any, list[Any]] = {}
    for fv, tv in zip(feature_values, target_values, strict=False):
        if fv not in feature_groups:
            feature_groups[fv] = []
        feature_groups[fv].append(tv)

    gini_weighted = 0.0
    for targets in feature_groups.values():
        weight = len(targets) / n_total
        counts = Counter(targets)
        gini_weighted += weight * gini_impurity(list(counts.values()))

    return gini_total - gini_weighted


def perplexity(distribution: dict[Any, float]) -> float:
    """Perplexity = 2^H(P) measures effective vocabulary size."""
    h = 0.0
    for p_val in distribution.values():
        if p_val > 0:
            h -= p_val * math.log2(p_val)
    return 2**h


def variation_of_information(x: list[Any], y: list[Any]) -> float:
    """Variation of Information VI(X;Y) = H(X|Y) + H(Y|X)."""
    return conditional_entropy(x, y) + conditional_entropy(y, x)
