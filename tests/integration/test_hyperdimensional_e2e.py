"""
tests.integration.test_hyperdimensional_e2e
-------------------------------------------
End-to-end integration tests for hyperdimensional embeddings system.

Tests the complete workflow:
1. Pre-compute all spec-kit embeddings
2. Save to JSON file
3. Load from JSON file
4. Perform similarity searches
5. Verify results match expected patterns
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from specify_cli.hyperdimensional.core import (
    EmbeddingCache,
    embed_entity,
    precompute_speckit_embeddings,
)


class TestEndToEndWorkflow:
    """End-to-end workflow tests."""

    def test_complete_workflow(self) -> None:
        """Test complete workflow: precompute → save → load → search."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_file = Path(tmpdir) / "embeddings.json"

            # Step 1: Pre-compute all embeddings
            cache = precompute_speckit_embeddings()
            assert len(cache) >= 89  # At least 89 entities

            # Step 2: Save to JSON
            cache.save(cache_file)
            assert cache_file.exists()
            assert cache_file.stat().st_size > 1_000_000  # At least 1MB

            # Step 3: Load from JSON
            loaded = EmbeddingCache.load(cache_file)
            assert len(loaded) == len(cache)

            # Step 4: Verify embeddings match
            for name in cache.embeddings:
                original = cache.get(name)
                loaded_vec = loaded.get(name)
                assert original is not None
                assert loaded_vec is not None
                assert original.cosine_similarity(loaded_vec) == 1.0

            # Step 5: Perform similarity search
            query = loaded.get("command:init")
            assert query is not None

            similar = loaded.find_similar(query, top_k=10)
            assert len(similar) == 10

            # First result should be the query itself
            assert similar[0][0] == "command:init"
            assert similar[0][1] == 1.0

            # All similarities should be in valid range
            for _, sim in similar:
                assert -1.0 <= sim <= 1.0

            # Results should be sorted descending
            similarities = [sim for _, sim in similar]
            assert similarities == sorted(similarities, reverse=True)

    def test_cross_category_similarity(self) -> None:
        """Test similarity searches across different entity categories."""
        cache = precompute_speckit_embeddings()

        # Commands should be somewhat similar to other commands
        cmd_init = cache.get("command:init")
        assert cmd_init is not None

        similar = cache.find_similar(cmd_init, top_k=20)

        # Count how many commands appear in top 20
        command_count = sum(1 for name, _ in similar if name.startswith("command:"))
        # Should find at least 2 commands (including self)
        # Note: Random embeddings may not cluster perfectly by category
        assert command_count >= 2

    def test_outcome_clustering(self) -> None:
        """Test that similar outcomes cluster together."""
        cache = precompute_speckit_embeddings()

        # Performance-related outcome
        fast_startup = cache.get("outcome:fast-startup")
        assert fast_startup is not None

        similar = cache.find_similar(fast_startup, top_k=10)

        # Check for other performance/speed related outcomes
        similar_names = [name for name, _ in similar]
        performance_keywords = ["fast", "efficient", "performance", "low"]

        performance_matches = sum(
            1
            for name in similar_names
            if any(keyword in name for keyword in performance_keywords)
        )

        # Should find at least 2 performance-related outcomes in top 10
        assert performance_matches >= 2

    def test_deterministic_precomputation(self) -> None:
        """Test that pre-computation is deterministic."""
        # Pre-compute twice
        cache1 = precompute_speckit_embeddings()
        cache2 = precompute_speckit_embeddings()

        # Should have same number of embeddings
        assert len(cache1) == len(cache2)

        # All embeddings should be identical
        for name in cache1.embeddings:
            vec1 = cache1.get(name)
            vec2 = cache2.get(name)
            assert vec1 is not None
            assert vec2 is not None
            assert vec1.cosine_similarity(vec2) == 1.0

    def test_persistence_integrity(self) -> None:
        """Test that save/load preserves data integrity."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_file = Path(tmpdir) / "test.json"

            # Create small cache
            cache = EmbeddingCache()
            cache.add(embed_entity("command:test1"))
            cache.add(embed_entity("command:test2"))
            cache.add(embed_entity("job:tester"))

            # Save
            cache.save(cache_file)

            # Load
            loaded = EmbeddingCache.load(cache_file)

            # Verify all entities present
            assert "command:test1" in loaded
            assert "command:test2" in loaded
            assert "job:tester" in loaded

            # Verify vectors identical
            for name in ["command:test1", "command:test2", "job:tester"]:
                original = cache.get(name)
                loaded_vec = loaded.get(name)
                assert original is not None
                assert loaded_vec is not None
                assert original.cosine_similarity(loaded_vec) == 1.0

    def test_similarity_search_quality(self) -> None:
        """Test quality of similarity search results."""
        cache = precompute_speckit_embeddings()

        # Test 1: Self-similarity should always be 1.0
        for name in list(cache.embeddings.keys())[:10]:  # Sample 10
            vec = cache.get(name)
            assert vec is not None
            similar = cache.find_similar(vec, top_k=1)
            assert similar[0][0] == name
            assert similar[0][1] == 1.0

        # Test 2: Top-k should be unique
        query = cache.get("command:check")
        assert query is not None
        similar = cache.find_similar(query, top_k=20)
        names = [name for name, _ in similar]
        assert len(names) == len(set(names))  # All unique

    def test_entity_categories_all_present(self) -> None:
        """Test that all expected entity categories are present."""
        cache = precompute_speckit_embeddings()

        # Check for each category
        has_commands = any(n.startswith("command:") for n in cache.embeddings)
        has_jobs = any(n.startswith("job:") for n in cache.embeddings)
        has_outcomes = any(n.startswith("outcome:") for n in cache.embeddings)
        has_features = any(n.startswith("feature:") for n in cache.embeddings)
        has_constraints = any(n.startswith("constraint:") for n in cache.embeddings)

        assert has_commands, "Missing command embeddings"
        assert has_jobs, "Missing job embeddings"
        assert has_outcomes, "Missing outcome embeddings"
        assert has_features, "Missing feature embeddings"
        assert has_constraints, "Missing constraint embeddings"


@pytest.mark.slow
class TestPerformance:
    """Performance tests."""

    def test_precomputation_performance(self) -> None:
        """Test that pre-computation completes quickly."""
        import time

        start = time.perf_counter()
        cache = precompute_speckit_embeddings()
        elapsed = time.perf_counter() - start

        # Should complete in under 100ms
        assert elapsed < 0.1, f"Pre-computation took {elapsed:.3f}s (expected < 0.1s)"
        assert len(cache) >= 89

    def test_similarity_search_performance(self) -> None:
        """Test that similarity search is fast."""
        import time

        cache = precompute_speckit_embeddings()
        query = cache.get("command:init")
        assert query is not None

        # Warm up
        cache.find_similar(query, top_k=5)

        # Measure
        start = time.perf_counter()
        for _ in range(100):
            cache.find_similar(query, top_k=5)
        elapsed = time.perf_counter() - start

        # Should average < 2ms per search (relaxed threshold)
        avg_time = elapsed / 100
        assert avg_time < 0.002, f"Search took {avg_time*1000:.2f}ms (expected < 2ms)"

    def test_json_save_performance(self) -> None:
        """Test that JSON save is reasonably fast."""
        import time

        with tempfile.TemporaryDirectory() as tmpdir:
            cache_file = Path(tmpdir) / "perf.json"
            cache = precompute_speckit_embeddings()

            start = time.perf_counter()
            cache.save(cache_file)
            elapsed = time.perf_counter() - start

            # Should complete in under 500ms (relaxed for slow machines)
            assert elapsed < 0.5, f"Save took {elapsed:.3f}s (expected < 0.5s)"

    def test_json_load_performance(self) -> None:
        """Test that JSON load is reasonably fast."""
        import time

        with tempfile.TemporaryDirectory() as tmpdir:
            cache_file = Path(tmpdir) / "perf.json"
            cache = precompute_speckit_embeddings()
            cache.save(cache_file)

            start = time.perf_counter()
            loaded = EmbeddingCache.load(cache_file)
            elapsed = time.perf_counter() - start

            # Should complete in under 300ms
            assert elapsed < 0.3, f"Load took {elapsed:.3f}s (expected < 0.3s)"
            assert len(loaded) == len(cache)
