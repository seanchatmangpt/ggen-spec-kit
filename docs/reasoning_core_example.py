#!/usr/bin/env python3
# ruff: noqa: T201  # Allow print statements in example files
"""Example: Using reasoning_core for 80/20 semantic reasoning.

Demonstrates the three essential operations:
1. Similarity search - Find similar commands
2. Ranking - Prioritize features by value
3. Constraint checking - Validate architecture
"""

from specify_cli.hyperdimensional import (
    HyperdimensionalEmbedding,
    check_constraint_satisfied,
    find_similar_entities,
    get_violated_constraints,
    rank_by_objective,
)


def main() -> None:
    """Run reasoning examples."""
    print("=" * 70)
    print("Reasoning Core Examples (80/20 Implementation)")
    print("=" * 70)

    # Initialize embedding engine
    hde = HyperdimensionalEmbedding(dimensions=1000, seed=42)

    # ========================================================================
    # Example 1: Similarity Search
    # ========================================================================
    print("\n1. SIMILARITY SEARCH - Find similar commands")
    print("-" * 70)

    # Create command embeddings
    commands = ["init", "check", "version", "sync", "validate", "build"]
    command_embeddings = {f"command:{cmd}": hde.embed_command(cmd) for cmd in commands}

    # Find similar commands to "init"
    query = hde.embed_command("init")
    similar = find_similar_entities(query, command_embeddings, k=3)

    print("Commands most similar to 'init':")
    for name, score in similar:
        print(f"  {name:20s} similarity: {score:.3f}")

    # ========================================================================
    # Example 2: Ranking by Objective
    # ========================================================================
    print("\n2. RANKING - Prioritize features by value/cost ratio")
    print("-" * 70)

    # Create feature entities
    features = [
        {"name": "rdf-validation", "priority": 0.9, "cost": 3, "impact": 0.8},
        {"name": "three-tier-arch", "priority": 1.0, "cost": 5, "impact": 0.9},
        {"name": "telemetry", "priority": 0.7, "cost": 2, "impact": 0.6},
        {"name": "cli-polish", "priority": 0.5, "cost": 1, "impact": 0.4},
    ]

    # Rank by value/cost ratio (ROI)
    def roi_metric(feat: dict[str, float | str]) -> float:
        return float(feat["priority"]) * float(feat["impact"]) / float(feat["cost"])

    ranked = rank_by_objective(features, roi_metric)

    print("Features ranked by ROI (priority × impact / cost):")
    for feat in ranked:
        roi = roi_metric(feat)
        print(f"  {feat['name']:20s} ROI: {roi:.3f}")

    # ========================================================================
    # Example 3: Constraint Satisfaction
    # ========================================================================
    print("\n3. CONSTRAINT CHECKING - Validate architecture")
    print("-" * 70)

    # Define design and constraints
    design = hde.embed_feature("microservices")

    constraints_dict = {
        "api-gateway": hde.embed_constraint("api-gateway-required"),
        "service-discovery": hde.embed_constraint("service-discovery-needed"),
        "circuit-breaker": hde.embed_constraint("fault-tolerance"),
        "no-shared-state": hde.embed_constraint("stateless-services"),
    }

    # Check if design satisfies constraints
    satisfied = check_constraint_satisfied(design, list(constraints_dict.values()), threshold=0.6)

    print(f"Design satisfies all constraints: {satisfied}")

    # Get detailed violations
    violations = get_violated_constraints(design, constraints_dict, threshold=0.7)

    if violations:
        print("\nConstraint violations (severity ordered):")
        for name, score in violations:
            severity = 1.0 - score
            print(f"  {name:25s} score: {score:.3f} (severity: {severity:.3f})")
    else:
        print("\n✓ All constraints satisfied!")

    # ========================================================================
    # Example 4: Combined Workflow
    # ========================================================================
    print("\n4. COMBINED WORKFLOW - Find + Rank + Validate")
    print("-" * 70)

    # Find features similar to "validation"
    validation_query = hde.embed_feature("validation")
    feature_embeddings = {
        "rdf-validation": hde.embed_feature("rdf-validation"),
        "shacl-validation": hde.embed_feature("shacl-validation"),
        "schema-validation": hde.embed_feature("schema-validation"),
        "data-quality": hde.embed_feature("data-quality"),
        "type-checking": hde.embed_feature("type-checking"),
    }

    similar_features = find_similar_entities(validation_query, feature_embeddings, k=3)

    print("Features similar to 'validation':")
    for name, score in similar_features:
        print(f"  {name:25s} similarity: {score:.3f}")

    # Rank them by implementation priority
    feature_entities = [
        {"name": name, "similarity": score, "effort": 3 - score}  # Inverse effort
        for name, score in similar_features
    ]

    ranked_features = rank_by_objective(
        feature_entities, lambda f: float(f["similarity"]) / float(f["effort"])
    )

    print("\nRanked by value/effort ratio:")
    for feat in ranked_features:
        ratio = float(feat["similarity"]) / float(feat["effort"])
        print(f"  {feat['name']:25s} ratio: {ratio:.3f}")

    print("\n" + "=" * 70)
    print("✓ All examples completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
