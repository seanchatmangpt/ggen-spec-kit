#!/usr/bin/env python3
"""Validation script for HYPERDIMENSIONAL_QUICKSTART.md examples.

This script runs all 4 examples from the quickstart to ensure they work correctly.
"""

print("=" * 70)
print("Hyperdimensional Computing Quick Start - Example Validation")
print("=" * 70)
print()

# Example 1: Measure Specification Quality
print("Example 1: Measure Specification Quality")
print("-" * 70)

from specify_cli.hyperdimensional.metrics import entropy

spec_v1 = [0.2, 0.7, 0.1]
spec_v2 = [0.9, 0.05, 0.05]

entropy_v1 = entropy(spec_v1)
entropy_v2 = entropy(spec_v2)

print(f"Incomplete spec: {entropy_v1:.3f} bits (high uncertainty)")
print(f"Complete spec:   {entropy_v2:.3f} bits (low uncertainty)")
print(f"Entropy reduction: {entropy_v1 - entropy_v2:.3f} bits")
print("✓ Example 1 passed")
print()

# Example 2: Prioritize Features by Information Gain
print("Example 2: Prioritize Features by Information Gain")
print("-" * 70)

from specify_cli.hyperdimensional.prioritization import Feature, rank_features_by_gain

features = [
    Feature(
        name="User Authentication",
        requirements=["login", "logout", "password_reset", "2fa"],
        complexity="medium",
        impact="critical",
    ),
    Feature(
        name="Dark Mode",
        requirements=["theme_toggle"],
        complexity="low",
        impact="low",
    ),
    Feature(
        name="Payment Processing",
        requirements=["stripe", "paypal", "refunds", "invoices"],
        complexity="high",
        impact="critical",
    ),
]

ranked = rank_features_by_gain(features, objective="quality")

for item in ranked:
    print(f"{item.rank}. {item.item.name}")
    print(f"   Score: {item.score:.3f}")

print("✓ Example 2 passed")
print()

# Example 3: Find Similar Features
print("Example 3: Find Similar Features (Semantic Search)")
print("-" * 70)

from specify_cli.hyperdimensional.search import SemanticSearchDashboard
import numpy as np

search = SemanticSearchDashboard()

features_data = [
    {"name": "Login API", "type": "authentication"},
    {"name": "OAuth Integration", "type": "authentication"},
    {"name": "Password Reset", "type": "authentication"},
    {"name": "Shopping Cart", "type": "ecommerce"},
]

np.random.seed(42)  # For reproducible results
embeddings = np.random.rand(4, 1024)

results = search.search_by_semantic_similarity(
    query=embeddings[0], features=features_data, embeddings=embeddings, k=3
)

for result in results:
    print(f"{result.rank}. {result.name}")
    print(f"   Similarity: {result.score:.3f}")

print("✓ Example 3 passed")
print()

# Example 4: Prioritize Tasks by Multiple Objectives
print("Example 4: Prioritize Tasks by Multiple Objectives")
print("-" * 70)

from specify_cli.hyperdimensional.prioritization import Task, prioritize_tasks

tasks = [
    Task(
        id="TASK-001",
        name="Fix critical security bug",
        estimated_effort=2.0,
        impact=95.0,
        uncertainty=0.1,
        complexity=30.0,
    ),
    Task(
        id="TASK-002",
        name="Add new payment method",
        estimated_effort=40.0,
        impact=70.0,
        uncertainty=0.6,
        complexity=80.0,
    ),
    Task(
        id="TASK-003",
        name="Improve button styling",
        estimated_effort=1.0,
        impact=10.0,
        uncertainty=0.1,
        complexity=5.0,
    ),
]

ranked_tasks = prioritize_tasks(
    tasks,
    objectives=["impact", "effort", "uncertainty"],
    weights={"impact": 0.5, "effort": 0.3, "uncertainty": 0.2},
)

for item in ranked_tasks:
    task = item.item
    print(f"{item.rank}. {task.name}")
    print(f"   Score: {item.score:.3f}")
    print(f"   Effort: {task.estimated_effort}h")
    print(f"   Impact: {task.impact}/100")

print("✓ Example 4 passed")
print()

print("=" * 70)
print("All examples validated successfully!")
print("=" * 70)
