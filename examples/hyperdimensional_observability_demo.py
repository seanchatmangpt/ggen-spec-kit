#!/usr/bin/env python3
"""
Hyperdimensional Observability Demo
====================================

Demonstrates minimal OTEL instrumentation for hyperdimensional operations.

This script shows how to use the observability wrappers with the existing
spec-kit OTEL infrastructure. All telemetry data is sent to the configured
OTEL collector endpoint.

Usage
-----
    # Set OTEL endpoint (if not already set)
    export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317

    # Run the demo
    python examples/hyperdimensional_observability_demo.py

Requirements
------------
- OTEL collector running at configured endpoint
- OpenTelemetry SDK installed (part of spec-kit dependencies)

What Gets Tracked
-----------------
1. Embedding operations: vector creation, binding, bundling
2. Similarity searches: semantic search, feature finding
3. Validation checks: spec compliance, type safety, completeness

Metrics Available
-----------------
- hyperdimensional.embedding.{operation}.operations
- hyperdimensional.embedding.{operation}.success
- hyperdimensional.embedding.{operation}.errors
- hyperdimensional.search.{type}.operations
- hyperdimensional.search.{type}.result_count
- hyperdimensional.search.{type}.success
- hyperdimensional.search.{type}.latency_ms
- hyperdimensional.validation.{check}.checks
- hyperdimensional.validation.{check}.score
- hyperdimensional.validation.{check}.passed/failed

Query Examples (OTEL Backend)
------------------------------
# Count embedding operations
SELECT COUNT(*) FROM spans WHERE name LIKE 'hyperdimensional.embedding.%'

# Average search latency
SELECT AVG(duration) FROM spans WHERE name = 'hyperdimensional.search.semantic'

# Validation pass rate
SELECT
  SUM(CASE WHEN hd.validation.passed = true THEN 1 ELSE 0 END) / COUNT(*)
FROM spans WHERE name LIKE 'hyperdimensional.validation.%'
"""

import time

from specify_cli.hyperdimensional import (
    HyperdimensionalEmbedding,
    record_search_latency,
    record_vector_stats,
    track_embedding_operation,
    track_similarity_search,
    track_validation_check,
)


def demo_embedding_tracking() -> None:
    """Demonstrate embedding operation tracking."""
    print("\n1. Embedding Operations")
    print("=" * 60)

    # Create embedding engine
    hde = HyperdimensionalEmbedding(dimensions=10000)

    # Track single embedding
    with track_embedding_operation("embed_command", vector_count=1, dimensions=10000):
        cmd_vector = hde.embed_command("init")
        print(f"✓ Tracked embedding: init command (shape={cmd_vector.shape})")

    # Track batch embedding
    commands = ["check", "sync", "validate", "compile"]
    with track_embedding_operation(
        "batch_embed_commands", vector_count=len(commands), dimensions=10000
    ):
        vectors = [hde.embed_command(cmd) for cmd in commands]
        print(f"✓ Tracked batch embedding: {len(vectors)} commands")

    # Track vector operations
    with track_embedding_operation("bind_vectors", vector_count=2, dimensions=10000):
        bound = hde.bind(cmd_vector, vectors[0])
        print(f"✓ Tracked vector binding (shape={bound.shape})")

    # Record stats
    record_vector_stats(vector_count=len(vectors), dimensions=10000, operation="demo_batch")
    print(f"✓ Recorded vector stats: {len(vectors)} vectors @ 10k dimensions")


def demo_search_tracking() -> None:
    """Demonstrate similarity search tracking."""
    print("\n2. Similarity Search")
    print("=" * 60)

    hde = HyperdimensionalEmbedding(dimensions=10000)

    # Create some test vectors
    features = ["feature_a", "feature_b", "feature_c", "feature_d"]
    feature_vectors = {feat: hde.embed_feature(feat) for feat in features}

    # Track semantic search
    query = hde.embed_feature("test_feature")
    start = time.perf_counter()

    with track_similarity_search("find_similar_features", result_count=2, search_type="semantic"):
        # Simulate search
        similarities = {
            feat: hde.cosine_similarity(query, vec) for feat, vec in feature_vectors.items()
        }
        top_2 = sorted(similarities.items(), key=lambda x: x[1], reverse=True)[:2]
        print(f"✓ Tracked semantic search: found {len(top_2)} similar features")
        for feat, sim in top_2:
            print(f"  - {feat}: {sim:.4f}")

    # Record search latency
    latency_ms = (time.perf_counter() - start) * 1000
    record_search_latency(latency_ms, search_type="semantic")
    print(f"✓ Recorded search latency: {latency_ms:.2f}ms")


def demo_validation_tracking() -> None:
    """Demonstrate validation check tracking."""
    print("\n3. Validation Checks")
    print("=" * 60)

    # Track successful validation
    with track_validation_check("spec_compliance", passed=True, score=0.95) as span:
        # Simulate validation
        time.sleep(0.01)
        span.set_attribute("spec.sections", 10)
        span.set_attribute("spec.complete", True)
        print("✓ Tracked spec compliance check: PASSED (score=0.95)")

    # Track failed validation
    with track_validation_check("type_safety", passed=False, score=0.42) as span:
        # Simulate validation
        span.set_attribute("type.errors", 5)
        span.set_attribute("type.warnings", 12)
        print("✓ Tracked type safety check: FAILED (score=0.42)")

    # Track validation without immediate result
    with track_validation_check("completeness_check") as span:
        # Compute score during validation
        completeness_score = 0.88
        span.set_attribute("hd.validation.score", completeness_score)
        span.set_attribute("hd.validation.passed", completeness_score >= 0.80)
        print(f"✓ Tracked completeness check: score={completeness_score:.2f}")


def main() -> None:
    """Run observability demo."""
    print("\nHyperdimensional Observability Demo")
    print("=" * 60)
    print("This demo shows OTEL instrumentation for hyperdimensional operations.")
    print("\nAll spans and metrics are sent to the configured OTEL endpoint.")
    print("View traces in your OTEL backend (Jaeger, Tempo, etc.)")

    try:
        demo_embedding_tracking()
        demo_search_tracking()
        demo_validation_tracking()

        print("\n" + "=" * 60)
        print("✓ Demo complete!")
        print("\nView telemetry data in your OTEL backend:")
        print("  - Traces: Search for 'hyperdimensional.*' spans")
        print("  - Metrics: Query 'hyperdimensional.*' counters/histograms")
        print("  - Attributes: Filter by hd.operation, hd.search.type, etc.")

    except Exception as e:
        print(f"\n✗ Demo failed: {e}")
        print("\nNote: OTEL gracefully degrades when not configured.")
        print("Set OTEL_EXPORTER_OTLP_ENDPOINT to enable telemetry.")
        raise


if __name__ == "__main__":
    main()
