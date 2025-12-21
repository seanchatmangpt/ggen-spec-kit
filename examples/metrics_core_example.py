# ruff: noqa: T201  # Allow print statements in example files
"""Example: Using information-theoretic metrics for feature selection.

This demonstrates the 80/20 approach to metrics - focusing on practical
decision-making with entropy, mutual information, and information gain.
"""

from __future__ import annotations

import random

from specify_cli.hyperdimensional.metrics_core import (
    entropy,
    feature_selection_score,
    kullback_leibler,
    mutual_information,
    normalized_mutual_information,
    redundancy_score,
)


def example_feature_selection() -> None:
    """Select best features using information gain."""
    print("=" * 60)
    print("Example 1: Feature Selection for Classification")
    print("=" * 60)

    # Target: Binary classification (0 or 1)
    target = [0, 0, 0, 0, 1, 1, 1, 1] * 10  # 80 samples

    # Feature 1: Highly correlated with target
    feature1 = [1.0, 1.5, 2.0, 2.5, 8.0, 8.5, 9.0, 9.5] * 10

    # Feature 2: Weakly correlated
    feature2 = [5.0, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7] * 10

    # Feature 3: Random (no correlation)
    random.seed(42)
    feature3 = [random.uniform(0, 10) for _ in range(80)]

    # Calculate information gain for each feature
    score1 = feature_selection_score(feature1, target, bins=5)
    score2 = feature_selection_score(feature2, target, bins=5)
    score3 = feature_selection_score(feature3, target, bins=5)

    print(f"\nFeature 1 score: {score1:.4f} (strong predictor)")
    print(f"Feature 2 score: {score2:.4f} (weak predictor)")
    print(f"Feature 3 score: {score3:.4f} (random noise)")
    print(f"\n→ Best feature: Feature 1 with {score1:.4f} bits of information")


def example_entropy_analysis() -> None:
    """Analyze uncertainty in different distributions."""
    print("\n" + "=" * 60)
    print("Example 2: Entropy Analysis")
    print("=" * 60)

    # Uniform distribution (maximum entropy)
    uniform = [25.0, 25.0, 25.0, 25.0]
    h_uniform = entropy(uniform)

    # Skewed distribution (lower entropy)
    skewed = [70.0, 20.0, 5.0, 5.0]
    h_skewed = entropy(skewed)

    # Deterministic (zero entropy)
    deterministic = [100.0, 0.0, 0.0, 0.0]
    h_deterministic = entropy(deterministic)

    print(f"\nUniform [25, 25, 25, 25]: H = {h_uniform:.4f} bits (max)")
    print(f"Skewed [70, 20, 5, 5]:    H = {h_skewed:.4f} bits")
    print(f"Deterministic [100, 0]:   H = {h_deterministic:.4f} bits (min)")


def example_mutual_information() -> None:
    """Measure dependency between variables."""
    print("\n" + "=" * 60)
    print("Example 3: Mutual Information (Dependency)")
    print("=" * 60)

    # Perfectly correlated
    x = [1, 2, 3, 4, 1, 2, 3, 4]
    y_identical = [1, 2, 3, 4, 1, 2, 3, 4]

    # Independent
    y_independent = [1, 1, 2, 2, 3, 3, 4, 4]

    mi_perfect = mutual_information(x, y_identical)
    mi_independent = mutual_information(x, y_independent)

    nmi_perfect = normalized_mutual_information(x, y_identical)
    nmi_independent = normalized_mutual_information(x, y_independent)

    print(f"\nPerfect correlation:  MI = {mi_perfect:.4f}, NMI = {nmi_perfect:.4f}")
    print(f"Independent:          MI = {mi_independent:.4f}, NMI = {nmi_independent:.4f}")


def example_divergence() -> None:
    """Compare distributions using KL divergence."""
    print("\n" + "=" * 60)
    print("Example 4: Distribution Comparison (KL Divergence)")
    print("=" * 60)

    # True distribution
    p = {"A": 0.5, "B": 0.3, "C": 0.2}

    # Close approximation
    q_close = {"A": 0.48, "B": 0.32, "C": 0.20}

    # Poor approximation
    q_poor = {"A": 0.2, "B": 0.3, "C": 0.5}

    kl_close = kullback_leibler(p, q_close)
    kl_poor = kullback_leibler(p, q_poor)

    print(f"\nTrue: P = {p}")
    print(f"Close approximation: Q1 = {q_close}")
    print(f"  D_KL(P||Q1) = {kl_close:.4f} bits")
    print(f"\nPoor approximation: Q2 = {q_poor}")
    print(f"  D_KL(P||Q2) = {kl_poor:.4f} bits")
    print("\n→ Lower KL divergence means better approximation")


def example_redundancy() -> None:
    """Identify redundant features."""
    print("\n" + "=" * 60)
    print("Example 5: Feature Redundancy Detection")
    print("=" * 60)

    # Create three features
    feature_a = [float(i % 10) for i in range(100)]
    feature_b = [float(i % 10) for i in range(100)]  # Identical to A
    feature_c = [float(i % 5) for i in range(100)]  # Different pattern

    # Calculate pairwise redundancy
    redundancy_ab = redundancy_score(feature_a, feature_b, bins=10)
    redundancy_ac = redundancy_score(feature_a, feature_c, bins=10)
    redundancy_bc = redundancy_score(feature_b, feature_c, bins=10)

    print(f"\nRedundancy(A, B) = {redundancy_ab:.4f} (identical → high)")
    print(f"Redundancy(A, C) = {redundancy_ac:.4f} (different)")
    print(f"Redundancy(B, C) = {redundancy_bc:.4f} (different)")
    print("\n→ Features A and B are redundant; keep only one")


def main() -> None:
    """Run all examples."""
    example_feature_selection()
    example_entropy_analysis()
    example_mutual_information()
    example_divergence()
    example_redundancy()

    print("\n" + "=" * 60)
    print("80/20 Metrics Summary")
    print("=" * 60)
    print("""
These 5 core metrics handle 80% of decision-making needs:

1. Entropy - Measures uncertainty/information content
2. Mutual Information - Measures dependency between variables
3. Information Gain - Feature selection for classification
4. KL Divergence - Compare/measure distance between distributions
5. Redundancy - Detect correlated/redundant features

Simple, fast, effective. Add complexity only when needed.
""")


if __name__ == "__main__":
    main()
