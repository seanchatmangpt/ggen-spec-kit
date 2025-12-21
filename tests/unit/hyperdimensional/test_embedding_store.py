"""
Unit tests for EmbeddingStore module.

Tests cover:
- Saving and retrieving embeddings
- Metadata management
- Checksum verification
- Filtering operations
- RDF persistence (if rdflib available)
"""

from __future__ import annotations

from datetime import datetime

import numpy as np
import pytest

from specify_cli.hyperdimensional.embedding_store import (
    RDFLIB_AVAILABLE,
    EmbeddingMetadata,
    EmbeddingStore,
)


class TestEmbeddingMetadata:
    """Test EmbeddingMetadata dataclass."""

    def test_initialization(self) -> None:
        """Test metadata initialization."""
        meta = EmbeddingMetadata(
            entity_name="command:init",
            dimensions=1000,
            version="0.0.25",
        )

        assert meta.entity_name == "command:init"
        assert meta.dimensions == 1000
        assert meta.version == "0.0.25"
        assert isinstance(meta.created, datetime)
        assert len(meta.tags) == 0

    def test_with_tags(self) -> None:
        """Test metadata with tags."""
        meta = EmbeddingMetadata(
            entity_name="command:init",
            dimensions=1000,
            tags=["command", "cli", "setup"],
        )

        assert len(meta.tags) == 3
        assert "setup" in meta.tags


class TestEmbeddingStore:
    """Test EmbeddingStore class."""

    def test_initialization(self) -> None:
        """Test store initialization."""
        store = EmbeddingStore()

        assert len(store.embeddings) == 0
        assert len(store.metadata) == 0
        assert store.namespace.endswith("#")

    def test_save_embedding(self) -> None:
        """Test saving embedding."""
        store = EmbeddingStore()
        vector = np.random.randn(1000)

        store.save_embedding("command:init", vector)

        assert "command:init" in store.embeddings
        assert "command:init" in store.metadata
        assert np.allclose(store.embeddings["command:init"], vector)

    def test_save_embedding_with_metadata(self) -> None:
        """Test saving embedding with custom metadata."""
        store = EmbeddingStore()
        vector = np.random.randn(1000)

        store.save_embedding(
            "command:init",
            vector,
            metadata={"version": "0.0.25", "tags": ["command", "setup"]},
        )

        meta = store.metadata["command:init"]
        assert meta.version == "0.0.25"
        assert "setup" in meta.tags

    def test_get_embedding(self) -> None:
        """Test retrieving embedding."""
        store = EmbeddingStore()
        vector = np.random.randn(1000)

        store.save_embedding("command:init", vector)
        retrieved = store.get_embedding("command:init")

        assert retrieved is not None
        assert np.allclose(retrieved, vector)

    def test_get_embedding_missing(self) -> None:
        """Test retrieving missing embedding."""
        store = EmbeddingStore()
        retrieved = store.get_embedding("nonexistent")

        assert retrieved is None

    def test_get_metadata(self) -> None:
        """Test retrieving metadata."""
        store = EmbeddingStore()
        vector = np.random.randn(1000)

        store.save_embedding("command:init", vector)
        meta = store.get_metadata("command:init")

        assert meta is not None
        assert meta.entity_name == "command:init"

    def test_checksum_computation(self) -> None:
        """Test checksum computation."""
        store = EmbeddingStore()
        vector = np.random.randn(1000)

        store.save_embedding("command:init", vector)
        meta = store.metadata["command:init"]

        # Checksum should be non-empty hex string
        assert len(meta.checksum) == 64  # SHA256 hex length

    def test_verify_checksums(self) -> None:
        """Test checksum verification."""
        store = EmbeddingStore()
        vector = np.random.randn(1000)

        store.save_embedding("command:init", vector)
        results = store.verify_checksums()

        assert results["command:init"] is True

    def test_verify_checksums_corrupted(self) -> None:
        """Test checksum verification with corrupted data."""
        store = EmbeddingStore()
        vector = np.random.randn(1000)

        store.save_embedding("command:init", vector)

        # Corrupt the vector
        store.embeddings["command:init"][0] = 999.0

        results = store.verify_checksums()

        assert results["command:init"] is False

    def test_filter_by_prefix(self) -> None:
        """Test filtering by entity prefix."""
        store = EmbeddingStore()

        store.save_embedding("command:init", np.random.randn(100))
        store.save_embedding("command:check", np.random.randn(100))
        store.save_embedding("job:developer", np.random.randn(100))

        commands = store.filter_by_prefix("command:")

        assert len(commands) == 2
        assert "command:init" in commands
        assert "command:check" in commands
        assert "job:developer" not in commands

    def test_get_all_commands(self) -> None:
        """Test getting all command embeddings."""
        store = EmbeddingStore()

        store.save_embedding("command:init", np.random.randn(100))
        store.save_embedding("command:check", np.random.randn(100))
        store.save_embedding("job:developer", np.random.randn(100))

        commands = store.get_all_commands()

        assert len(commands) == 2

    def test_get_all_jobs(self) -> None:
        """Test getting all job embeddings."""
        store = EmbeddingStore()

        store.save_embedding("job:developer", np.random.randn(100))
        store.save_embedding("job:architect", np.random.randn(100))
        store.save_embedding("command:init", np.random.randn(100))

        jobs = store.get_all_jobs()

        assert len(jobs) == 2

    def test_get_all_outcomes(self) -> None:
        """Test getting all outcome embeddings."""
        store = EmbeddingStore()

        store.save_embedding("outcome:fast-startup", np.random.randn(100))
        store.save_embedding("outcome:reliable-builds", np.random.randn(100))
        store.save_embedding("command:init", np.random.randn(100))

        outcomes = store.get_all_outcomes()

        assert len(outcomes) == 2

    def test_get_all_features(self) -> None:
        """Test getting all feature embeddings."""
        store = EmbeddingStore()

        store.save_embedding("feature:rdf-validation", np.random.randn(100))
        store.save_embedding("feature:three-tier-arch", np.random.randn(100))
        store.save_embedding("command:init", np.random.randn(100))

        features = store.get_all_features()

        assert len(features) == 2

    def test_get_all_constraints(self) -> None:
        """Test getting all constraint embeddings."""
        store = EmbeddingStore()

        store.save_embedding("constraint:no-side-effects", np.random.randn(100))
        store.save_embedding("constraint:type-hints-required", np.random.randn(100))
        store.save_embedding("command:init", np.random.randn(100))

        constraints = store.get_all_constraints()

        assert len(constraints) == 2

    def test_clear(self) -> None:
        """Test clearing store."""
        store = EmbeddingStore()

        store.save_embedding("command:init", np.random.randn(100))
        store.save_embedding("job:developer", np.random.randn(100))

        assert len(store) == 2

        store.clear()

        assert len(store) == 0
        assert len(store.metadata) == 0

    def test_len(self) -> None:
        """Test __len__ method."""
        store = EmbeddingStore()

        assert len(store) == 0

        store.save_embedding("command:init", np.random.randn(100))
        assert len(store) == 1

        store.save_embedding("job:developer", np.random.randn(100))
        assert len(store) == 2

    def test_contains(self) -> None:
        """Test __contains__ method."""
        store = EmbeddingStore()

        store.save_embedding("command:init", np.random.randn(100))

        assert "command:init" in store
        assert "command:nonexistent" not in store


@pytest.mark.skipif(not RDFLIB_AVAILABLE, reason="rdflib not available")
@pytest.mark.xfail(reason="RDF persistence under development", strict=False)
class TestEmbeddingStoreRDF:
    """Test RDF persistence features (requires rdflib)."""

    def test_save_to_rdf(self, tmp_path: pytest.TempPathFactory) -> None:  # type: ignore[name-defined]
        """Test saving to RDF file."""
        store = EmbeddingStore()

        # Create embeddings
        store.save_embedding(
            "command:init",
            np.random.randn(100),
            metadata={"version": "0.0.25", "tags": ["command"]},
        )
        store.save_embedding("job:developer", np.random.randn(100))

        # Save to RDF
        filepath = tmp_path / "embeddings.ttl"  # type: ignore[operator]
        store.save_to_rdf(filepath)

        # File should exist
        assert filepath.exists()

        # Should contain RDF content
        content = filepath.read_text()
        assert "@prefix" in content
        assert "sk:" in content

    def test_load_from_rdf(self, tmp_path: pytest.TempPathFactory) -> None:  # type: ignore[name-defined]
        """Test loading from RDF file."""
        # Create and save store
        store1 = EmbeddingStore()
        vector1 = np.random.randn(100)

        store1.save_embedding(
            "command:init",
            vector1,
            metadata={"version": "0.0.25", "tags": ["command", "setup"]},
        )

        filepath = tmp_path / "embeddings.ttl"  # type: ignore[operator]
        store1.save_to_rdf(filepath)

        # Load into new store
        store2 = EmbeddingStore.load_from_rdf(filepath)

        assert len(store2) == 1
        assert "command:init" in store2

        # Vector should match
        vector2 = store2.get_embedding("command:init")
        assert vector2 is not None
        assert np.allclose(vector1, vector2)

        # Metadata should match
        meta = store2.get_metadata("command:init")
        assert meta is not None
        assert meta.version == "0.0.25"
        assert "setup" in meta.tags

    def test_load_from_rdf_missing_file(self, tmp_path: pytest.TempPathFactory) -> None:  # type: ignore[name-defined]
        """Test loading from missing file."""
        filepath = tmp_path / "nonexistent.ttl"  # type: ignore[operator]

        with pytest.raises(FileNotFoundError):
            EmbeddingStore.load_from_rdf(filepath)

    def test_round_trip_rdf(self, tmp_path: pytest.TempPathFactory) -> None:  # type: ignore[name-defined]
        """Test round-trip save and load."""
        store1 = EmbeddingStore()

        # Create diverse embeddings
        for entity_type, name in [
            ("command", "init"),
            ("command", "check"),
            ("job", "developer"),
            ("outcome", "fast-startup"),
            ("feature", "rdf-validation"),
            ("constraint", "no-side-effects"),
        ]:
            store1.save_embedding(
                f"{entity_type}:{name}",
                np.random.randn(100),
                metadata={"version": "0.0.25", "tags": [entity_type]},
            )

        # Save and load
        filepath = tmp_path / "embeddings.ttl"  # type: ignore[operator]
        store1.save_to_rdf(filepath)
        store2 = EmbeddingStore.load_from_rdf(filepath)

        # All entities should be present
        assert len(store2) == 6

        # Verify each entity
        for entity_type, name in [
            ("command", "init"),
            ("command", "check"),
            ("job", "developer"),
            ("outcome", "fast-startup"),
            ("feature", "rdf-validation"),
            ("constraint", "no-side-effects"),
        ]:
            entity_key = f"{entity_type}:{name}"
            assert entity_key in store2

            vec1 = store1.get_embedding(entity_key)
            vec2 = store2.get_embedding(entity_key)
            assert vec1 is not None
            assert vec2 is not None
            assert np.allclose(vec1, vec2, atol=1e-5)  # Some precision loss in RDF


@pytest.mark.skipif(RDFLIB_AVAILABLE, reason="Testing graceful degradation")
class TestEmbeddingStoreNoRDF:
    """Test graceful degradation when rdflib not available."""

    def test_save_to_rdf_without_rdflib(self, tmp_path: pytest.TempPathFactory) -> None:  # type: ignore[name-defined]
        """Test that save_to_rdf raises ImportError without rdflib."""
        store = EmbeddingStore()
        store.save_embedding("command:init", np.random.randn(100))

        filepath = tmp_path / "embeddings.ttl"  # type: ignore[operator]

        with pytest.raises(ImportError, match="rdflib required"):
            store.save_to_rdf(filepath)

    def test_load_from_rdf_without_rdflib(self, tmp_path: pytest.TempPathFactory) -> None:  # type: ignore[name-defined]
        """Test that load_from_rdf raises ImportError without rdflib."""
        filepath = tmp_path / "embeddings.ttl"  # type: ignore[operator]
        filepath.write_text("dummy content")

        with pytest.raises(ImportError, match="rdflib required"):
            EmbeddingStore.load_from_rdf(filepath)
