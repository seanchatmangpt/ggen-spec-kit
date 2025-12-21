#!/usr/bin/env python3
# ruff: noqa: T201  # Allow print statements in demo files
"""
Demo: 80/20 Feature Prioritization
-----------------------------------
Shows how to use priority_core for stupidly simple feature prioritization.

Value = job_frequency × outcome_importance
Effort = 1 (small), 2 (medium), 3 (large)
Priority = value / effort (ROI)
"""

from specify_cli.hyperdimensional import (
    FeaturePriority,
    estimate_feature_effort,
    estimate_feature_value,
    prioritize_features,
    quick_wins,
    top_n_features,
)


def main() -> None:
    """Run prioritization demo."""
    # Define features with JTBD metrics
    features = {
        "deps-add": {
            "job_frequency": 0.9,  # 90% of users need this
            "outcome_importance": 0.8,  # High importance
            "complexity": "small",
            "description": "Add dependencies to pyproject.toml",
        },
        "ggen-sync": {
            "job_frequency": 0.7,  # 70% of users need this
            "outcome_importance": 0.9,  # Very important
            "complexity": "medium",
            "description": "Transform RDF to Markdown",
        },
        "terraform-deploy": {
            "job_frequency": 0.3,  # 30% of users need this
            "outcome_importance": 0.7,  # Moderately important
            "complexity": "large",
            "description": "Deploy infrastructure",
        },
        "check-tools": {
            "job_frequency": 0.95,  # 95% of users need this
            "outcome_importance": 0.6,  # Moderate importance
            "complexity": "trivial",
            "description": "Check tool availability",
        },
        "jtbd-analytics": {
            "job_frequency": 0.4,  # 40% of users need this
            "outcome_importance": 0.8,  # High importance
            "complexity": "complex",
            "description": "Analyze job-outcome metrics",
        },
    }

    print("=" * 80)
    print("80/20 Feature Prioritization Demo")
    print("=" * 80)

    # Example 1: Individual value/effort estimation
    print("\n1. Individual Feature Analysis")
    print("-" * 80)
    for feature_id, feature_data in list(features.items())[:2]:
        value = estimate_feature_value(feature_data)
        effort = estimate_feature_effort(feature_data)
        priority = value / effort

        print(f"\nFeature: {feature_id}")
        print(f"  Description: {feature_data['description']}")
        print(f"  Value:       {value:.2f} (freq={feature_data['job_frequency']:.1f} × imp={feature_data['outcome_importance']:.1f})")
        print(f"  Effort:      {effort:.1f} ({feature_data['complexity']})")
        print(f"  Priority:    {priority:.2f} (value/effort)")

    # Example 2: Full prioritization
    print("\n\n2. Full Feature Ranking")
    print("-" * 80)
    ranked = prioritize_features(features)

    print(f"\n{'Rank':<6} {'Feature':<20} {'Value':<8} {'Effort':<8} {'Priority':<10} {'Description'}")
    print("-" * 80)
    for i, feature in enumerate(ranked, 1):
        print(
            f"{i:<6} {feature.feature_id:<20} {feature.value:<8.2f} "
            f"{feature.effort:<8.1f} {feature.priority:<10.2f} "
            f"{feature.metadata['description']}"
        )

    # Example 3: Quick wins
    print("\n\n3. Quick Wins (Priority > 0.3)")
    print("-" * 80)
    wins = quick_wins(features, threshold=0.3)

    if wins:
        print(f"\nFound {len(wins)} quick win(s):\n")
        for feature in wins:
            print(f"  • {feature.feature_id:<20} (priority={feature.priority:.2f})")
            print(f"    {feature.metadata['description']}")
            print()
    else:
        print("\nNo quick wins found with threshold > 0.3")

    # Example 4: Top N features
    print("\n\n4. Top 3 Features to Build Next")
    print("-" * 80)
    top = top_n_features(features, n=3)

    print("\nRecommended build order:\n")
    for i, feature in enumerate(top, 1):
        print(f"{i}. {feature.feature_id}")
        print(f"   Priority: {feature.priority:.2f} (value={feature.value:.2f}, effort={feature.effort:.1f})")
        print(f"   Why: {feature.metadata['description']}")
        print()

    # Example 5: Decision-making guidance
    print("\n\n5. Decision Guidance")
    print("-" * 80)
    print("\nWhat should we build next?")
    print(f"→ Start with: {ranked[0].feature_id}")
    print(f"  Reason: Highest ROI ({ranked[0].priority:.2f})")
    print(f"  Impact: Reaches {features[ranked[0].feature_id]['job_frequency']*100:.0f}% of users")

    high_freq = max(ranked, key=lambda f: f.metadata["job_frequency"])
    print(f"\n→ Most users need: {high_freq.feature_id}")
    print(f"  Frequency: {high_freq.metadata['job_frequency']*100:.0f}% of users")
    print(f"  Priority rank: #{ranked.index(high_freq) + 1}")

    low_effort = min(ranked, key=lambda f: f.effort)
    print(f"\n→ Easiest to build: {low_effort.feature_id}")
    print(f"  Effort: {low_effort.effort:.1f} ({low_effort.metadata['complexity']})")
    print(f"  Priority rank: #{ranked.index(low_effort) + 1}")

    print("\n" + "=" * 80)
    print("Summary: Use priority_core for practical ROI-based feature ranking!")
    print("=" * 80)


if __name__ == "__main__":
    main()
