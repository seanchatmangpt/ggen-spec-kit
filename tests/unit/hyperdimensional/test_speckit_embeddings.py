"""
Unit tests for spec-kit concrete embeddings.

Tests cover:
- Initialization of all spec-kit embeddings
- Command embeddings
- Job embeddings
- Outcome embeddings
- Feature embeddings
- Constraint embeddings
- Extraction functions
"""

from __future__ import annotations

from specify_cli.hyperdimensional.speckit_embeddings import (
    SPECKIT_COMMANDS,
    SPECKIT_CONSTRAINTS,
    SPECKIT_FEATURES,
    SPECKIT_JOBS,
    SPECKIT_OUTCOMES,
    get_command_embeddings,
    get_constraint_embeddings,
    get_feature_embeddings,
    get_job_embeddings,
    get_outcome_embeddings,
    initialize_speckit_embeddings,
)


class TestSpeckitEmbeddings:
    """Test spec-kit concrete embeddings."""

    def test_initialize_speckit_embeddings(self) -> None:
        """Test initialization of all spec-kit embeddings."""
        store = initialize_speckit_embeddings(dimensions=1000)

        # Should have many embeddings
        assert len(store) > 50

        # Should have embeddings from all categories
        assert len(store.get_all_commands()) > 0
        assert len(store.get_all_jobs()) > 0
        assert len(store.get_all_outcomes()) > 0
        assert len(store.get_all_features()) > 0
        assert len(store.get_all_constraints()) > 0

    def test_all_commands_present(self) -> None:
        """Test that all spec-kit commands have embeddings."""
        store = initialize_speckit_embeddings(dimensions=1000)

        for cmd in SPECKIT_COMMANDS:
            entity_key = f"command:{cmd}"
            assert entity_key in store, f"Missing embedding for {cmd}"

            # Check metadata
            meta = store.get_metadata(entity_key)
            assert meta is not None
            assert "command" in meta.tags

    def test_all_jobs_present(self) -> None:
        """Test that all JTBD jobs have embeddings."""
        store = initialize_speckit_embeddings(dimensions=1000)

        for job in SPECKIT_JOBS:
            entity_key = f"job:{job}"
            assert entity_key in store, f"Missing embedding for {job}"

            # Check metadata
            meta = store.get_metadata(entity_key)
            assert meta is not None
            assert "job" in meta.tags
            assert "jtbd" in meta.tags

    def test_all_outcomes_present(self) -> None:
        """Test that all outcomes have embeddings."""
        store = initialize_speckit_embeddings(dimensions=1000)

        for outcome in SPECKIT_OUTCOMES:
            entity_key = f"outcome:{outcome}"
            assert entity_key in store, f"Missing embedding for {outcome}"

            # Check metadata
            meta = store.get_metadata(entity_key)
            assert meta is not None
            assert "outcome" in meta.tags

    def test_outcome_category_tags(self) -> None:
        """Test that outcomes have appropriate category tags."""
        store = initialize_speckit_embeddings(dimensions=1000)

        # Performance outcomes should have performance tag
        perf_outcome = store.get_metadata("outcome:fast-startup")
        assert perf_outcome is not None
        assert "performance" in perf_outcome.tags

        # Reliability outcomes should have reliability tag
        rel_outcome = store.get_metadata("outcome:reliable-builds")
        assert rel_outcome is not None
        assert "reliability" in rel_outcome.tags

        # Quality outcomes should have quality tag
        qual_outcome = store.get_metadata("outcome:high-test-coverage")
        assert qual_outcome is not None
        assert "quality" in qual_outcome.tags

    def test_all_features_present(self) -> None:
        """Test that all features have embeddings."""
        store = initialize_speckit_embeddings(dimensions=1000)

        for feature in SPECKIT_FEATURES:
            entity_key = f"feature:{feature}"
            assert entity_key in store, f"Missing embedding for {feature}"

            # Check metadata
            meta = store.get_metadata(entity_key)
            assert meta is not None
            assert "feature" in meta.tags

    def test_all_constraints_present(self) -> None:
        """Test that all constraints have embeddings."""
        store = initialize_speckit_embeddings(dimensions=1000)

        for constraint in SPECKIT_CONSTRAINTS:
            entity_key = f"constraint:{constraint}"
            assert entity_key in store, f"Missing embedding for {constraint}"

            # Check metadata
            meta = store.get_metadata(entity_key)
            assert meta is not None
            assert "constraint" in meta.tags
            assert "architecture" in meta.tags

    def test_version_metadata(self) -> None:
        """Test that all embeddings have version metadata."""
        version = "0.0.25"
        store = initialize_speckit_embeddings(dimensions=1000, version=version)

        # Check a few embeddings
        for entity_key in ["command:init", "job:developer", "outcome:fast-startup"]:
            meta = store.get_metadata(entity_key)
            assert meta is not None
            assert meta.version == version

    def test_vector_dimensions(self) -> None:
        """Test that all vectors have correct dimensions."""
        dimensions = 1000
        store = initialize_speckit_embeddings(dimensions=dimensions)

        for entity_key in store.embeddings:
            vector = store.get_embedding(entity_key)
            assert vector is not None
            assert len(vector) == dimensions

    def test_get_command_embeddings(self) -> None:
        """Test extracting command embeddings."""
        store = initialize_speckit_embeddings(dimensions=1000)
        commands = get_command_embeddings(store)

        assert len(commands) == len(SPECKIT_COMMANDS)
        assert "command:init" in commands
        assert "command:check" in commands

    def test_get_job_embeddings(self) -> None:
        """Test extracting job embeddings."""
        store = initialize_speckit_embeddings(dimensions=1000)
        jobs = get_job_embeddings(store)

        assert len(jobs) == len(SPECKIT_JOBS)
        assert "job:developer" in jobs
        assert "job:architect" in jobs

    def test_get_outcome_embeddings(self) -> None:
        """Test extracting outcome embeddings."""
        store = initialize_speckit_embeddings(dimensions=1000)
        outcomes = get_outcome_embeddings(store)

        assert len(outcomes) == len(SPECKIT_OUTCOMES)
        assert "outcome:fast-startup" in outcomes

    def test_get_feature_embeddings(self) -> None:
        """Test extracting feature embeddings."""
        store = initialize_speckit_embeddings(dimensions=1000)
        features = get_feature_embeddings(store)

        assert len(features) == len(SPECKIT_FEATURES)
        assert "feature:three-tier-architecture" in features

    def test_get_constraint_embeddings(self) -> None:
        """Test extracting constraint embeddings."""
        store = initialize_speckit_embeddings(dimensions=1000)
        constraints = get_constraint_embeddings(store)

        assert len(constraints) == len(SPECKIT_CONSTRAINTS)
        assert "constraint:no-side-effects-in-ops" in constraints

    def test_constants_valid(self) -> None:
        """Test that all constant lists are valid."""
        # Commands should be non-empty
        assert len(SPECKIT_COMMANDS) > 10

        # Jobs should be non-empty
        assert len(SPECKIT_JOBS) > 0

        # Outcomes should be substantial (45+)
        assert len(SPECKIT_OUTCOMES) >= 45

        # Features should be non-empty
        assert len(SPECKIT_FEATURES) > 0

        # Constraints should be non-empty
        assert len(SPECKIT_CONSTRAINTS) > 0

    def test_no_duplicate_commands(self) -> None:
        """Test that command list has no duplicates."""
        assert len(SPECKIT_COMMANDS) == len(set(SPECKIT_COMMANDS))

    def test_no_duplicate_jobs(self) -> None:
        """Test that job list has no duplicates."""
        assert len(SPECKIT_JOBS) == len(set(SPECKIT_JOBS))

    def test_no_duplicate_outcomes(self) -> None:
        """Test that outcome list has no duplicates."""
        assert len(SPECKIT_OUTCOMES) == len(set(SPECKIT_OUTCOMES))

    def test_embedding_determinism(self) -> None:
        """Test that embeddings are deterministic."""
        store1 = initialize_speckit_embeddings(dimensions=1000)
        store2 = initialize_speckit_embeddings(dimensions=1000)

        # Same entity should have same vector
        vec1 = store1.get_embedding("command:init")
        vec2 = store2.get_embedding("command:init")

        assert vec1 is not None
        assert vec2 is not None

        import numpy as np

        assert np.allclose(vec1, vec2)
