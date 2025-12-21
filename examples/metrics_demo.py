#!/usr/bin/env python3
# ruff: noqa: T201  # Allow print statements in demo/example files
"""Demonstration of information-theoretic metrics for decision optimization.

This example shows how to use the metrics library for:
1. Feature selection via information gain
2. Specification completeness analysis via entropy
3. Multi-objective optimization in information space
4. Complexity measurement and analysis
"""

import numpy as np

from specify_cli.hyperdimensional.metrics import (
    approximate_entropy,
    entropy,
    fisher_information_matrix,
    information_gain,
    jensen_shannon_divergence,
    kolmogorov_complexity,
    kullback_leibler_divergence,
    lempel_ziv_complexity,
    mutual_information,
    normalized_mutual_information,
    redundancy_measure,
)


def demo_specification_completeness() -> None:
    """Demonstrate specification completeness analysis via entropy."""
    print("=== Specification Completeness Analysis ===\n")

    # Simulate specification states: [complete, incomplete, ambiguous]
    spec_v1 = [0.2, 0.7, 0.1]  # High uncertainty (incomplete)
    spec_v2 = [0.6, 0.3, 0.1]  # Medium uncertainty (improving)
    spec_v3 = [0.9, 0.05, 0.05]  # Low uncertainty (nearly complete)

    h1 = entropy(spec_v1)
    h2 = entropy(spec_v2)
    h3 = entropy(spec_v3)

    print(f"Spec v1 entropy: {h1:.3f} bits (high uncertainty → incomplete)")
    print(f"Spec v2 entropy: {h2:.3f} bits (medium uncertainty → improving)")
    print(f"Spec v3 entropy: {h3:.3f} bits (low uncertainty → nearly complete)")
    print(f"\nEntropy reduction: {h1 - h3:.3f} bits")
    print("Lower entropy indicates more complete, well-defined specifications.\n")


def demo_feature_selection() -> None:
    """Demonstrate feature selection using information gain."""
    print("=== Feature Selection for Decision Optimization ===\n")

    np.random.seed(42)

    # Simulate features and target
    n_samples = 200
    target = np.random.choice([0, 1], size=n_samples, p=[0.6, 0.4])

    # Relevant feature (correlated with target)
    feature_relevant = target + np.random.randn(n_samples) * 0.3

    # Irrelevant feature (independent)
    feature_irrelevant = np.random.randn(n_samples)

    # Redundant feature (copy of relevant)
    feature_redundant = feature_relevant + np.random.randn(n_samples) * 0.1

    # Calculate information gains
    ig_relevant = information_gain(feature_relevant, target, bins=10)
    ig_irrelevant = information_gain(feature_irrelevant, target, bins=10)
    ig_redundant = information_gain(feature_redundant, target, bins=10)

    print(f"Information Gain (relevant feature):   {ig_relevant:.4f} bits")
    print(f"Information Gain (irrelevant feature): {ig_irrelevant:.4f} bits")
    print(f"Information Gain (redundant feature):  {ig_redundant:.4f} bits")

    # Check redundancy
    features = np.column_stack([feature_relevant, feature_irrelevant, feature_redundant])
    redundancy_matrix = redundancy_measure(features, bins=10)

    print(f"\nRedundancy between relevant and redundant: {redundancy_matrix[0, 2]:.4f}")
    print("High redundancy → can remove redundant feature without losing information.\n")


def demo_divergence_comparison() -> None:
    """Demonstrate divergence measures for comparing distributions."""
    print("=== Divergence Measures for Distribution Comparison ===\n")

    # Spec requirement distribution vs implementation distribution
    requirement_dist = [0.5, 0.3, 0.2]
    implementation_v1 = [0.5, 0.3, 0.2]  # Perfect match
    implementation_v2 = [0.4, 0.4, 0.2]  # Close match
    implementation_v3 = [0.2, 0.3, 0.5]  # Poor match

    print("Requirement distribution: [0.5, 0.3, 0.2]")
    print("\nImplementation v1 (perfect): [0.5, 0.3, 0.2]")
    print(
        f"  KL divergence:  {kullback_leibler_divergence(requirement_dist, implementation_v1):.4f}"
    )
    print(f"  JS divergence:  {jensen_shannon_divergence(requirement_dist, implementation_v1):.4f}")

    print("\nImplementation v2 (close): [0.4, 0.4, 0.2]")
    kl_v2 = kullback_leibler_divergence(requirement_dist, implementation_v2)
    js_v2 = jensen_shannon_divergence(requirement_dist, implementation_v2)
    print(f"  KL divergence:  {kl_v2:.4f}")
    print(f"  JS divergence:  {js_v2:.4f}")

    print("\nImplementation v3 (poor): [0.2, 0.3, 0.5]")
    kl_v3 = kullback_leibler_divergence(requirement_dist, implementation_v3)
    js_v3 = jensen_shannon_divergence(requirement_dist, implementation_v3)
    print(f"  KL divergence:  {kl_v3:.4f}")
    print(f"  JS divergence:  {js_v3:.4f}")

    print("\nLower divergence indicates better alignment with requirements.\n")


def demo_complexity_analysis() -> None:
    """Demonstrate complexity measures for code and specifications."""
    print("=== Complexity Analysis ===\n")

    # Simple, repetitive specification
    simple_spec = b"AAAA" * 10
    k_simple = kolmogorov_complexity(simple_spec)
    print(f"Simple spec (repetitive):   {len(simple_spec)} bytes → {k_simple:.0f} bytes compressed")
    print(f"  Compression ratio: {k_simple / len(simple_spec):.2f}")

    # Complex, detailed specification
    complex_spec = b"The system shall handle edge cases A, B, C with fallback D..."
    k_complex = kolmogorov_complexity(complex_spec)
    print(
        f"\nComplex spec (detailed):    {len(complex_spec)} bytes → {k_complex:.0f} bytes compressed"
    )
    print(f"  Compression ratio: {k_complex / len(complex_spec):.2f}")

    # Lempel-Ziv complexity
    periodic_sequence = "01010101" * 5
    random_sequence = "011010011100101110010110"

    lz_periodic = lempel_ziv_complexity(periodic_sequence)
    lz_random = lempel_ziv_complexity(random_sequence)

    print("\nLempel-Ziv Complexity:")
    print(f"  Periodic sequence: {lz_periodic}")
    print(f"  Random sequence:   {lz_random}")
    print("  Higher LZ complexity → more patterns → potentially more edge cases to handle.\n")


def demo_mutual_information_alignment() -> None:
    """Demonstrate mutual information for job-outcome alignment."""
    print("=== Job-Outcome Alignment via Mutual Information ===\n")

    np.random.seed(42)

    # Simulate job requirements and outcomes
    n_jobs = 150

    # Scenario 1: Well-aligned job and outcome
    job_requirement = np.random.choice([0, 1, 2], size=n_jobs, p=[0.5, 0.3, 0.2])
    outcome_aligned = job_requirement + np.random.choice([-1, 0, 1], size=n_jobs, p=[0.1, 0.8, 0.1])
    outcome_aligned = np.clip(outcome_aligned, 0, 2)

    # Scenario 2: Poorly aligned job and outcome
    outcome_misaligned = np.random.choice([0, 1, 2], size=n_jobs, p=[0.3, 0.4, 0.3])

    mi_aligned = mutual_information(job_requirement, outcome_aligned, bins=3)
    mi_misaligned = mutual_information(job_requirement, outcome_misaligned, bins=3)

    nmi_aligned = normalized_mutual_information(job_requirement, outcome_aligned, bins=3)
    nmi_misaligned = normalized_mutual_information(job_requirement, outcome_misaligned, bins=3)

    print("Well-aligned job-outcome:")
    print(f"  Mutual Information:            {mi_aligned:.4f} bits")
    print(f"  Normalized Mutual Information: {nmi_aligned:.4f}")

    print("\nPoorly aligned job-outcome:")
    print(f"  Mutual Information:            {mi_misaligned:.4f} bits")
    print(f"  Normalized Mutual Information: {nmi_misaligned:.4f}")

    print("\nHigher MI indicates stronger job-outcome alignment.")
    print(f"Alignment improvement: {(nmi_aligned - nmi_misaligned):.2f}\n")


def demo_information_geometry() -> None:
    """Demonstrate information geometry for statistical manifolds."""
    print("=== Information Geometry ===\n")

    np.random.seed(42)

    # Simulate samples from two different distributions
    samples_1 = np.random.randn(500, 2)  # Standard normal
    samples_2 = np.random.randn(500, 2) * 2 + 1  # Scaled and shifted

    # Fisher Information Matrices
    fim_1 = fisher_information_matrix(samples_1)
    fim_2 = fisher_information_matrix(samples_2)

    print("Fisher Information Matrix (Distribution 1):")
    print(fim_1)
    print("\nFisher Information Matrix (Distribution 2):")
    print(fim_2)

    # Approximate entropy for regularity
    time_series_regular = np.sin(np.linspace(0, 4 * np.pi, 100))
    time_series_random = np.random.randn(100)

    apen_regular = approximate_entropy(time_series_regular, m=2)
    apen_random = approximate_entropy(time_series_random, m=2)

    print("\nApproximate Entropy:")
    print(f"  Regular time series (sine): {apen_regular:.4f}")
    print(f"  Random time series:         {apen_random:.4f}")
    print("  Lower ApEn indicates more predictable/regular patterns.\n")


def main() -> None:
    """Run all demonstrations."""
    print("\n" + "=" * 70)
    print("Information-Theoretic Metrics for Decision Optimization")
    print("=" * 70 + "\n")

    demo_specification_completeness()
    demo_feature_selection()
    demo_divergence_comparison()
    demo_complexity_analysis()
    demo_mutual_information_alignment()
    demo_information_geometry()

    print("=" * 70)
    print("Demo Complete!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
