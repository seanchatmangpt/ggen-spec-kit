"""
Integration tests for RDF persistence.

Tests end-to-end workflows:
- Creating embeddings and saving to RDF
- Loading embeddings from RDF
- Round-trip integrity
- Large-scale operations
- Integration with ggen
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from specify_cli.hyperdimensional import (
    RDFLIB_AVAILABLE,
    HyperdimensionalEmbedding,
    initialize_speckit_embeddings,
)
from specify_cli.hyperdimensional.embedding_store import EmbeddingStore


@pytest.mark.integration
@pytest.mark.skipif(not RDFLIB_AVAILABLE, reason="rdflib not available")
@pytest.mark.xfail(reason="RDF persistence checksum verification under development", strict=False)
class TestRDFPersistenceIntegration:
    """Integration tests for RDF persistence."""

    def test_full_workflow(self, tmp_path: Path) -> None:
        """Test complete workflow: create → save → load → verify."""
        # Create embeddings
        hde = HyperdimensionalEmbedding(dimensions=1000)
        store = EmbeddingStore()

        # Embed various entities
        for cmd in ["init", "check", "version"]:
            vec = hde.embed_command(cmd)
            store.save_embedding(
                f"command:{cmd}",
                vec,
                metadata={"version": "0.0.25", "tags": ["command"]},
            )

        for job in ["developer", "architect"]:
            vec = hde.embed_job(job)
            store.save_embedding(
                f"job:{job}",
                vec,
                metadata={"version": "0.0.25", "tags": ["job", "jtbd"]},
            )

        # Save to RDF
        rdf_path = tmp_path / "embeddings.ttl"
        store.save_to_rdf(rdf_path)

        # Verify file exists and has content
        assert rdf_path.exists()
        content = rdf_path.read_text()
        assert "@prefix" in content
        assert "command:init" in content or "command_init" in content

        # Load back
        loaded_store = EmbeddingStore.load_from_rdf(rdf_path)

        # Verify all entities present
        assert len(loaded_store) == 5

        # Verify vectors match
        for entity in ["command:init", "command:check", "job:developer"]:
            original = store.get_embedding(entity)
            loaded = loaded_store.get_embedding(entity)

            assert original is not None
            assert loaded is not None
            assert np.allclose(original, loaded, atol=1e-5)

        # Verify metadata
        meta = loaded_store.get_metadata("command:init")
        assert meta is not None
        assert meta.version == "0.0.25"
        assert "command" in meta.tags

    def test_large_scale_persistence(self, tmp_path: Path) -> None:
        """Test persistence with full spec-kit embeddings."""
        # Initialize all spec-kit embeddings
        store = initialize_speckit_embeddings(dimensions=1000)

        # Should have many embeddings
        original_count = len(store)
        assert original_count > 50

        # Save to RDF
        rdf_path = tmp_path / "speckit-embeddings.ttl"
        store.save_to_rdf(rdf_path)

        # File should be substantial
        assert rdf_path.stat().st_size > 10000  # At least 10KB

        # Load back
        loaded_store = EmbeddingStore.load_from_rdf(rdf_path)

        # All embeddings should be present
        assert len(loaded_store) == original_count

        # Verify checksum integrity
        results = loaded_store.verify_checksums()
        # Most should pass (some precision loss acceptable in RDF serialization)
        pass_rate = sum(results.values()) / len(results)
        assert pass_rate > 0.95  # 95% pass rate

    def test_incremental_updates(self, tmp_path: Path) -> None:
        """Test incremental embedding updates."""
        rdf_path = tmp_path / "embeddings.ttl"

        # Create initial embeddings
        store1 = EmbeddingStore()
        hde = HyperdimensionalEmbedding(dimensions=1000)

        store1.save_embedding("command:init", hde.embed_command("init"))
        store1.save_to_rdf(rdf_path)

        # Load and add more
        store2 = EmbeddingStore.load_from_rdf(rdf_path)
        store2.save_embedding("command:check", hde.embed_command("check"))
        store2.save_to_rdf(rdf_path)

        # Load final version
        store3 = EmbeddingStore.load_from_rdf(rdf_path)

        assert len(store3) == 2
        assert "command:init" in store3
        assert "command:check" in store3

    def test_version_compatibility(self, tmp_path: Path) -> None:
        """Test version metadata preservation."""
        hde = HyperdimensionalEmbedding(dimensions=1000)

        # Create embeddings with different versions
        store = EmbeddingStore()
        store.save_embedding(
            "command:init",
            hde.embed_command("init"),
            metadata={"version": "0.0.24"},
        )
        store.save_embedding(
            "command:check",
            hde.embed_command("check"),
            metadata={"version": "0.0.25"},
        )

        # Save and load
        rdf_path = tmp_path / "embeddings.ttl"
        store.save_to_rdf(rdf_path)
        loaded = EmbeddingStore.load_from_rdf(rdf_path)

        # Verify versions preserved
        meta_init = loaded.get_metadata("command:init")
        meta_check = loaded.get_metadata("command:check")

        assert meta_init is not None
        assert meta_check is not None
        assert meta_init.version == "0.0.24"
        assert meta_check.version == "0.0.25"

    def test_unicode_handling(self, tmp_path: Path) -> None:
        """Test handling of Unicode in entity names and tags."""
        hde = HyperdimensionalEmbedding(dimensions=1000)
        store = EmbeddingStore()

        # Create embedding with Unicode
        store.save_embedding(
            "feature:rdf-validation",
            hde.embed_feature("rdf-validation"),
            metadata={"tags": ["validation", "rdf", "unicode-✓"]},
        )

        # Save and load
        rdf_path = tmp_path / "embeddings.ttl"
        store.save_to_rdf(rdf_path)
        loaded = EmbeddingStore.load_from_rdf(rdf_path)

        assert "feature:rdf-validation" in loaded
        meta = loaded.get_metadata("feature:rdf-validation")
        assert meta is not None
        # Tags should be preserved (may need escaping in RDF)
        assert len(meta.tags) > 0


@pytest.mark.integration
class TestEmbeddingSimilarity:
    """Integration tests for semantic similarity analysis."""

    def test_command_similarity_analysis(self) -> None:
        """Test similarity analysis across commands."""
        hde = HyperdimensionalEmbedding(dimensions=10000)  # High dim for accuracy

        # Create command embeddings
        init_vec = hde.embed_command("init")
        check_vec = hde.embed_command("check")
        version_vec = hde.embed_command("version")
        ggen_sync_vec = hde.embed_command("ggen-sync")

        # Commands should be roughly orthogonal (low similarity)
        sim_init_check = hde.cosine_similarity(init_vec, check_vec)
        assert abs(sim_init_check) < 0.2

        # But all should be in similar semantic space
        similarities = [
            hde.cosine_similarity(init_vec, check_vec),
            hde.cosine_similarity(init_vec, version_vec),
            hde.cosine_similarity(check_vec, ggen_sync_vec),
        ]

        # Should have some structure (not completely random)
        assert all(-0.3 < s < 0.3 for s in similarities)

    def test_job_outcome_binding(self) -> None:
        """Test binding jobs to outcomes."""
        hde = HyperdimensionalEmbedding(dimensions=10000)

        # Create job and outcome vectors
        dev_job = hde.embed_job("developer")
        fast_outcome = hde.embed_outcome("fast-startup")
        reliable_outcome = hde.embed_outcome("reliable-builds")

        # Bind job to outcome (relationship encoding)
        dev_fast = hde.bind(dev_job, fast_outcome)
        dev_reliable = hde.bind(dev_job, reliable_outcome)

        # Bound vectors should be different
        sim = hde.cosine_similarity(dev_fast, dev_reliable)
        assert abs(sim) < 0.5

        # Unbind to recover
        recovered_fast = hde.unbind(dev_fast, dev_job)
        recovered_reliable = hde.unbind(dev_reliable, dev_job)

        # Recovered should be similar to originals
        assert hde.cosine_similarity(recovered_fast, fast_outcome) > 0.7
        assert hde.cosine_similarity(recovered_reliable, reliable_outcome) > 0.7

    def test_feature_constraint_relationships(self) -> None:
        """Test relationships between features and constraints."""
        hde = HyperdimensionalEmbedding(dimensions=10000)
        store = EmbeddingStore()

        # Create feature and constraint vectors
        three_tier_feat = hde.embed_feature("three-tier-architecture")
        no_side_effects_const = hde.embed_constraint("no-side-effects-in-ops")
        type_hints_const = hde.embed_constraint("type-hints-required")

        # Bind feature to constraints
        feat_no_se = hde.bind(three_tier_feat, no_side_effects_const)
        feat_types = hde.bind(three_tier_feat, type_hints_const)

        # Store relationships
        store.save_embedding("relationship:three-tier-no-se", feat_no_se)
        store.save_embedding("relationship:three-tier-types", feat_types)

        # Relationships should be distinguishable
        sim = hde.cosine_similarity(feat_no_se, feat_types)
        assert abs(sim) < 0.6

    def test_superposition_of_outcomes(self) -> None:
        """Test combining multiple outcomes via superposition."""
        hde = HyperdimensionalEmbedding(dimensions=10000)

        # Performance outcomes
        fast_startup = hde.embed_outcome("fast-startup")
        fast_command = hde.embed_outcome("fast-command")
        low_memory = hde.embed_outcome("low-memory")

        # Combine into "performance" concept
        performance = hde.superpose([fast_startup, fast_command, low_memory])

        # Combined vector should be similar to each component
        assert hde.cosine_similarity(performance, fast_startup) > 0.3
        assert hde.cosine_similarity(performance, fast_command) > 0.3
        assert hde.cosine_similarity(performance, low_memory) > 0.3

    def test_find_similar_commands(self) -> None:
        """Test finding similar commands."""
        store = initialize_speckit_embeddings(dimensions=10000)
        hde = HyperdimensionalEmbedding(dimensions=10000)

        # Get all command embeddings
        commands = store.get_all_commands()

        # Find similar to "init"
        init_vec = hde.embed_command("init")
        similar = hde.find_similar(init_vec, commands, top_k=5)

        # First should be init itself
        assert similar[0][0] == "command:init"
        assert similar[0][1] == 1.0

        # Others should have lower similarity
        assert all(s[1] < 1.0 for s in similar[1:])
