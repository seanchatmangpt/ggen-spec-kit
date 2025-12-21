#!/usr/bin/env python3
"""
demo_hyperdimensional.py
-------------------------
Demonstration script for minimal hyperdimensional embeddings system.

Shows how to:
1. Create embeddings for spec-kit entities
2. Compute similarity metrics
3. Find similar commands/jobs/outcomes
4. Save and load pre-computed embeddings

Usage:
    python scripts/demo_hyperdimensional.py
"""

from __future__ import annotations

from pathlib import Path

from specify_cli.hyperdimensional.core import (
    embed_entity,
    precompute_speckit_embeddings,
)


def demo_basic_embeddings() -> None:
    """Demonstrate basic embedding creation and similarity."""
    print("=" * 70)
    print("DEMO 1: Basic Embeddings and Similarity")
    print("=" * 70)

    # Create embeddings for commands
    cmd_init = embed_entity("command:init")
    cmd_check = embed_entity("command:check")
    cmd_version = embed_entity("command:version")

    print(f"\n1. Created embeddings:")
    print(f"   - {cmd_init.name} (dimensions: {cmd_init.dimensions})")
    print(f"   - {cmd_check.name} (dimensions: {cmd_check.dimensions})")
    print(f"   - {cmd_version.name} (dimensions: {cmd_version.dimensions})")

    # Compute similarities
    sim_init_check = cmd_init.cosine_similarity(cmd_check)
    sim_init_version = cmd_init.cosine_similarity(cmd_version)
    sim_check_version = cmd_check.cosine_similarity(cmd_version)

    print(f"\n2. Cosine similarities:")
    print(f"   - init ↔ check:   {sim_init_check:.4f}")
    print(f"   - init ↔ version: {sim_init_version:.4f}")
    print(f"   - check ↔ version: {sim_check_version:.4f}")

    # Compute Manhattan distances
    dist_init_check = cmd_init.manhattan_distance(cmd_check)
    dist_init_version = cmd_init.manhattan_distance(cmd_version)

    print(f"\n3. Manhattan distances:")
    print(f"   - init ↔ check:   {dist_init_check:.2f}")
    print(f"   - init ↔ version: {dist_init_version:.2f}")

    # Verify determinism
    cmd_init_2 = embed_entity("command:init")
    deterministic = cmd_init.cosine_similarity(cmd_init_2) == 1.0

    print(f"\n4. Determinism check:")
    print(f"   - Same entity twice: {deterministic} (similarity = 1.0)")


def demo_job_outcome_similarity() -> None:
    """Demonstrate job and outcome embeddings."""
    print("\n" + "=" * 70)
    print("DEMO 2: Job and Outcome Similarity")
    print("=" * 70)

    # Create job embeddings
    job_dev = embed_entity("job:developer")
    job_arch = embed_entity("job:architect")
    job_pm = embed_entity("job:product-manager")

    print(f"\n1. Created job embeddings:")
    print(f"   - {job_dev.name}")
    print(f"   - {job_arch.name}")
    print(f"   - {job_pm.name}")

    # Create outcome embeddings
    outcome_fast = embed_entity("outcome:fast-startup")
    outcome_reliable = embed_entity("outcome:reliable-builds")
    outcome_modular = embed_entity("outcome:modular-design")

    print(f"\n2. Created outcome embeddings:")
    print(f"   - {outcome_fast.name}")
    print(f"   - {outcome_reliable.name}")
    print(f"   - {outcome_modular.name}")

    # Job similarities
    sim_dev_arch = job_dev.cosine_similarity(job_arch)
    sim_dev_pm = job_dev.cosine_similarity(job_pm)

    print(f"\n3. Job similarities:")
    print(f"   - developer ↔ architect:       {sim_dev_arch:.4f}")
    print(f"   - developer ↔ product-manager: {sim_dev_pm:.4f}")


def demo_precomputed_embeddings() -> None:
    """Demonstrate pre-computed embeddings cache."""
    print("\n" + "=" * 70)
    print("DEMO 3: Pre-computed Embeddings")
    print("=" * 70)

    # Pre-compute all spec-kit embeddings
    cache = precompute_speckit_embeddings()

    print(f"\n1. Pre-computed {len(cache)} embeddings")

    # Count by category
    commands = sum(1 for name in cache.embeddings if name.startswith("command:"))
    jobs = sum(1 for name in cache.embeddings if name.startswith("job:"))
    outcomes = sum(1 for name in cache.embeddings if name.startswith("outcome:"))
    features = sum(1 for name in cache.embeddings if name.startswith("feature:"))
    constraints = sum(1 for name in cache.embeddings if name.startswith("constraint:"))

    print(f"\n2. Breakdown by category:")
    print(f"   - Commands:    {commands}")
    print(f"   - Jobs:        {jobs}")
    print(f"   - Outcomes:    {outcomes}")
    print(f"   - Features:    {features}")
    print(f"   - Constraints: {constraints}")


def demo_find_similar() -> None:
    """Demonstrate similarity search."""
    print("\n" + "=" * 70)
    print("DEMO 4: Find Similar Entities")
    print("=" * 70)

    # Pre-compute embeddings
    cache = precompute_speckit_embeddings()

    # Find similar commands to "init"
    query_cmd = cache.get("command:init")
    if query_cmd:
        print(f"\n1. Top 5 entities similar to '{query_cmd.name}':")
        similar = cache.find_similar(query_cmd, top_k=5)
        for i, (name, sim) in enumerate(similar, 1):
            print(f"   {i}. {name:40s} (similarity: {sim:.4f})")

    # Find similar outcomes to "fast-startup"
    query_outcome = cache.get("outcome:fast-startup")
    if query_outcome:
        print(f"\n2. Top 5 entities similar to '{query_outcome.name}':")
        similar = cache.find_similar(query_outcome, top_k=5)
        for i, (name, sim) in enumerate(similar, 1):
            print(f"   {i}. {name:40s} (similarity: {sim:.4f})")


def demo_persistence() -> None:
    """Demonstrate JSON persistence."""
    print("\n" + "=" * 70)
    print("DEMO 5: JSON Persistence")
    print("=" * 70)

    # Create cache directory
    cache_dir = Path("data/hyperdimensional")
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / "speckit-embeddings.json"

    # Pre-compute and save
    print(f"\n1. Pre-computing embeddings...")
    cache = precompute_speckit_embeddings()
    print(f"   - Created {len(cache)} embeddings")

    print(f"\n2. Saving to {cache_file}...")
    cache.save(cache_file)
    file_size = cache_file.stat().st_size / 1024 / 1024  # MB
    print(f"   - Saved {file_size:.2f} MB")

    print(f"\n3. Loading from {cache_file}...")
    loaded_cache = cache.__class__.load(cache_file)
    print(f"   - Loaded {len(loaded_cache)} embeddings")

    # Verify integrity
    original_vec = cache.get("command:init")
    loaded_vec = loaded_cache.get("command:init")

    if original_vec and loaded_vec:
        similarity = original_vec.cosine_similarity(loaded_vec)
        print(f"\n4. Integrity check:")
        print(f"   - Original vs Loaded similarity: {similarity:.10f}")
        print(f"   - Vectors match: {similarity == 1.0}")


def main() -> None:
    """Run all demonstrations."""
    print("\n" + "🚀 " * 35)
    print("Hyperdimensional Embeddings System - Demonstration")
    print("🚀 " * 35)

    demo_basic_embeddings()
    demo_job_outcome_similarity()
    demo_precomputed_embeddings()
    demo_find_similar()
    demo_persistence()

    print("\n" + "=" * 70)
    print("✓ All demonstrations completed successfully!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
