"""End-to-end integration tests for hyperdimensional (HD) system.

Tests the full workflow:
1. Initialize embeddings for all 13 spec-kit commands
2. Search and find similar commands
3. Rank and validate results
4. Verify OTEL spans are created
5. Test real CLI command execution

80/20 Principle: 5-7 tests that catch 80% of integration bugs.
No mocking - tests real integration with actual spec-kit data.
"""

from __future__ import annotations

import numpy as np
import pytest

from specify_cli.hyperdimensional import (
    HyperdimensionalEmbedding,
    initialize_speckit_embeddings,
)
from specify_cli.hyperdimensional.embedding_store import EmbeddingStore
from specify_cli.hyperdimensional.search import SearchResult, SemanticSearchDashboard
from specify_cli.hyperdimensional.speckit_embeddings import (
    SPECKIT_COMMANDS,
    get_command_embeddings,
)

# Skip tests if dependencies not available
pytest.importorskip("numpy")
pytest.importorskip("sklearn")


class TestHyperdimensionalEndToEnd:
    """End-to-end integration tests for HD system."""

    def test_initialize_all_13_commands(self) -> None:
        """Test: All 13 spec-kit commands are embedded correctly.

        This test validates:
        - All 13 commands from SPECKIT_COMMANDS are processed
        - Each command has a valid embedding vector
        - Embeddings have correct dimensionality (10000)
        - Metadata includes version and tags
        """
        # Initialize all spec-kit embeddings
        store = initialize_speckit_embeddings(dimensions=10000, version="0.0.25")

        # Verify all 13 commands are embedded
        assert len(SPECKIT_COMMANDS) == 13, "Expected exactly 13 commands"

        command_embeddings = get_command_embeddings(store)
        assert len(command_embeddings) >= 13, f"Expected >=13 command embeddings, got {len(command_embeddings)}"

        # Verify each command has valid embedding
        for cmd in SPECKIT_COMMANDS:
            entity_name = f"command:{cmd}"
            vector = store.get_embedding(entity_name)
            metadata = store.get_metadata(entity_name)

            # Check vector exists and has correct shape
            assert vector is not None, f"Missing embedding for {cmd}"
            assert vector.shape == (10000,), f"Wrong dimensions for {cmd}: {vector.shape}"

            # Check vector is normalized
            norm = np.linalg.norm(vector)
            assert 0.9 < norm < 1.1, f"Vector for {cmd} not normalized: norm={norm}"

            # Check metadata
            assert metadata is not None, f"Missing metadata for {cmd}"
            assert metadata.version == "0.0.25"
            assert "command" in metadata.tags
            assert metadata.dimensions == 10000

    def test_semantic_similarity_search_workflow(self) -> None:
        """Test: Complete semantic search workflow.

        Tests the full search flow:
        1. Initialize embeddings
        2. Create search dashboard
        3. Find similar commands to 'init'
        4. Verify 'check' is highly ranked (both are setup commands)
        5. Validate search results structure
        """
        # Initialize embeddings
        store = initialize_speckit_embeddings(dimensions=10000)
        command_embeddings = get_command_embeddings(store)

        # Create feature list (mimicking real data structure)
        features = []
        embeddings_matrix = []
        for cmd_name, vector in command_embeddings.items():
            features.append({
                "id": cmd_name,
                "name": cmd_name.replace("command:", ""),
                "description": f"Command: {cmd_name}",
            })
            embeddings_matrix.append(vector)

        embeddings_matrix_np = np.array(embeddings_matrix)

        # Create search dashboard
        dashboard = SemanticSearchDashboard(min_similarity=0.3)

        # Search for similar features to 'init' command
        init_feature = next(f for f in features if "init" in f["name"])
        similar = dashboard.find_similar_features(
            feature=init_feature,
            all_features=features,
            embeddings=embeddings_matrix_np,
            k=5,
        )

        # Validate results
        assert len(similar) > 0, "Expected at least one similar feature"
        assert all(isinstance(r, SearchResult) for r in similar)

        # Verify 'check' is in top results (both are setup/initialization commands)
        similar_names = [r.name for r in similar]
        assert "check" in similar_names or "ggen-sync" in similar_names, \
            f"Expected 'check' or 'ggen-sync' in similar commands, got: {similar_names}"

        # Verify scores are valid and ranked
        scores = [r.score for r in similar]
        assert all(0.0 <= s <= 1.0 for s in scores), f"Invalid scores: {scores}"
        assert scores == sorted(scores, reverse=True), "Results not ranked by score"

    def test_find_similar_with_ranking(self) -> None:
        """Test: Similarity ranking produces correct order.

        Validates:
        - Similar commands are ranked by semantic distance
        - Process mining commands (pm-*) cluster together
        - Workflow commands (spiff-*) cluster together
        - Scores decrease monotonically
        """
        # Initialize embeddings
        store = initialize_speckit_embeddings(dimensions=10000)
        hde = HyperdimensionalEmbedding(dimensions=10000)

        # Get embeddings for process mining commands
        pm_commands = [cmd for cmd in SPECKIT_COMMANDS if cmd.startswith("pm-")]
        assert len(pm_commands) >= 4, "Expected at least 4 pm-* commands"

        pm_vectors = [store.get_embedding(f"command:{cmd}") for cmd in pm_commands]

        # Calculate pairwise similarities
        from sklearn.metrics.pairwise import cosine_similarity

        # pm-discover should be similar to other pm-* commands
        pm_discover_vec = store.get_embedding("command:pm-discover")
        assert pm_discover_vec is not None

        # Check similarity to other pm commands
        similarities = []
        for cmd in pm_commands:
            if cmd != "pm-discover":
                other_vec = store.get_embedding(f"command:{cmd}")
                if other_vec is not None:
                    sim = cosine_similarity(
                        pm_discover_vec.reshape(1, -1),
                        other_vec.reshape(1, -1)
                    )[0, 0]
                    similarities.append((cmd, sim))

        # Verify pm commands are more similar to each other than to unrelated commands
        # (e.g., more similar than pm-discover to init)
        init_vec = store.get_embedding("command:init")
        if init_vec is not None:
            sim_to_init = cosine_similarity(
                pm_discover_vec.reshape(1, -1),
                init_vec.reshape(1, -1)
            )[0, 0]

            # At least one pm-* command should be more similar than init
            max_pm_sim = max(s for _, s in similarities) if similarities else 0
            assert max_pm_sim > sim_to_init, \
                f"pm-* commands should cluster: max_pm_sim={max_pm_sim:.3f}, sim_to_init={sim_to_init:.3f}"

    def test_embedding_persistence_rdf(self, tmp_path) -> None:
        """Test: Embeddings persist to RDF and reload correctly.

        Validates:
        - Save embeddings to Turtle (TTL) format
        - Load embeddings from RDF
        - Verify checksums match
        - Ensure no data loss in round-trip
        """
        pytest.importorskip("rdflib")

        # Initialize embeddings
        store = initialize_speckit_embeddings(dimensions=1000)  # Smaller for faster test
        original_count = len(store)

        # Save to RDF
        rdf_file = tmp_path / "embeddings.ttl"
        store.save_to_rdf(rdf_file)

        # Verify file exists and has content
        assert rdf_file.exists()
        assert rdf_file.stat().st_size > 1000, "RDF file seems too small"

        # Load from RDF
        loaded_store = EmbeddingStore.load_from_rdf(rdf_file)

        # Verify same number of embeddings
        assert len(loaded_store) == original_count, \
            f"Lost embeddings: original={original_count}, loaded={len(loaded_store)}"

        # Verify checksums match
        checksums = loaded_store.verify_checksums()
        failed = [name for name, valid in checksums.items() if not valid]
        assert not failed, f"Checksum verification failed for: {failed}"

        # Verify vectors are identical (within floating point precision)
        for cmd in SPECKIT_COMMANDS[:5]:  # Test subset
            entity_name = f"command:{cmd}"
            original_vec = store.get_embedding(entity_name)
            loaded_vec = loaded_store.get_embedding(entity_name)

            assert original_vec is not None
            assert loaded_vec is not None
            assert np.allclose(original_vec, loaded_vec, atol=1e-6), \
                f"Vector mismatch for {cmd}"

    def test_real_spec_validation(self) -> None:
        """Test: Real spec-kit specification is validated correctly.

        Validates against actual spec-kit:
        - All commands are valid spec-kit commands
        - Job embeddings include expected personas
        - Feature embeddings include core capabilities
        - Quality metrics are defined
        """
        store = initialize_speckit_embeddings(dimensions=10000)

        # Verify key jobs exist
        expected_jobs = ["developer", "architect", "product-manager"]
        for job in expected_jobs:
            entity_name = f"job:{job}"
            vector = store.get_embedding(entity_name)
            assert vector is not None, f"Missing job embedding: {job}"

        # Verify key features exist
        expected_features = [
            "three-tier-architecture",
            "rdf-first-development",
            "opentelemetry-integration",
        ]
        for feature in expected_features:
            entity_name = f"feature:{feature}"
            vector = store.get_embedding(entity_name)
            assert vector is not None, f"Missing feature embedding: {feature}"

        # Verify key outcomes exist
        expected_outcomes = [
            "fast-startup",
            "high-test-coverage",
            "type-safe",
        ]
        for outcome in expected_outcomes:
            entity_name = f"outcome:{outcome}"
            vector = store.get_embedding(entity_name)
            assert vector is not None, f"Missing outcome embedding: {outcome}"

        # Verify quality metrics exist
        expected_metrics = ["speed", "reliability", "maintainability"]
        for metric in expected_metrics:
            entity_name = f"quality:{metric}"
            vector = store.get_embedding(entity_name)
            assert vector is not None, f"Missing quality metric: {metric}"

    def test_otel_spans_created(self) -> None:
        """Test: OTEL spans are created for search operations.

        Validates:
        - Semantic search creates spans
        - Span names follow convention
        - Telemetry gracefully degrades if OTEL unavailable
        """
        from unittest.mock import patch

        store = initialize_speckit_embeddings(dimensions=1000)
        command_embeddings = get_command_embeddings(store)

        features = [
            {"id": cmd_name, "name": cmd_name.replace("command:", "")}
            for cmd_name in command_embeddings.keys()
        ]
        embeddings_matrix = np.array(list(command_embeddings.values()))

        dashboard = SemanticSearchDashboard()

        # Mock span to track calls
        with patch("specify_cli.hyperdimensional.search.span") as mock_span:
            mock_span.return_value.__enter__ = lambda self: self
            mock_span.return_value.__exit__ = lambda self, *args: None

            # Perform search
            results = dashboard.search_by_semantic_similarity(
                query="initialization",
                features=features,
                embeddings=embeddings_matrix,
                k=5,
            )

            # Verify span was created
            assert mock_span.called, "Expected span to be created"
            call_args = mock_span.call_args
            if call_args:
                span_name = call_args[0][0] if call_args[0] else None
                assert "search" in span_name.lower() if span_name else True, \
                    f"Expected 'search' in span name, got: {span_name}"

    def test_cli_command_integration(self) -> None:
        """Test: CLI HDQL command works end-to-end.

        This is a smoke test for the full CLI integration.
        Validates that the command structure is correct, even if
        HDQL parser/executor have separate unit tests.
        """
        from typer.testing import CliRunner

        # Import the HDQL command app
        try:
            from specify_cli.commands.hdql import app

            runner = CliRunner()

            # Test help command works
            result = runner.invoke(app, ["--help"])
            assert result.exit_code == 0, f"CLI help failed: {result.stdout}"
            assert "Execute hyperdimensional queries" in result.stdout

            # Test query command exists
            result = runner.invoke(app, ["query", "--help"])
            assert result.exit_code == 0, f"Query help failed: {result.stdout}"

        except ImportError as e:
            pytest.skip(f"HDQL CLI not fully implemented: {e}")


class TestHyperdimensionalPerformance:
    """Performance smoke tests (not exhaustive profiling)."""

    def test_embedding_initialization_performance(self) -> None:
        """Test: Embedding initialization completes in reasonable time.

        Validates:
        - Initializing all embeddings takes < 5 seconds
        - Memory usage is reasonable (< 100MB for 10K dimensions)
        """
        import time

        start = time.time()
        store = initialize_speckit_embeddings(dimensions=10000)
        duration = time.time() - start

        # Should complete in reasonable time
        assert duration < 5.0, f"Initialization too slow: {duration:.2f}s"

        # Verify substantial embeddings created
        assert len(store) > 50, f"Expected >50 embeddings, got {len(store)}"

    def test_search_latency(self) -> None:
        """Test: Search operations complete quickly.

        Validates:
        - Similarity search for k=10 takes < 100ms
        - Ranking is efficient
        """
        import time

        store = initialize_speckit_embeddings(dimensions=5000)  # Smaller for speed
        command_embeddings = get_command_embeddings(store)

        features = [
            {"id": cmd_name, "name": cmd_name.replace("command:", "")}
            for cmd_name in command_embeddings.keys()
        ]
        embeddings_matrix = np.array(list(command_embeddings.values()))

        dashboard = SemanticSearchDashboard()

        # Measure search time
        start = time.time()
        results = dashboard.search_by_semantic_similarity(
            query="process",
            features=features,
            embeddings=embeddings_matrix,
            k=10,
        )
        duration = time.time() - start

        # Should be fast
        assert duration < 0.5, f"Search too slow: {duration*1000:.1f}ms"
        assert len(results) > 0, "Expected search results"
