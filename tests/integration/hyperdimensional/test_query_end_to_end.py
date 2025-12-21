"""Integration tests for end-to-end HDQL query workflows."""

from __future__ import annotations

import pytest

# Skip entire module - HDQL not fully implemented
pytest.skip(
    "HDQL not fully implemented - tests need update",
    allow_module_level=True,
)

from specify_cli.hyperdimensional import execute_query
from specify_cli.hyperdimensional.embeddings import load_default_database
from specify_cli.hyperdimensional.results import (
    RecommendationResult,
    VectorQueryResult,
)


@pytest.fixture
def db():
    """Load default database."""
    return load_default_database()


class TestEndToEndQueries:
    """Test complete query workflows."""

    def test_simple_command_lookup(self, db) -> None:
        """Test simple command lookup."""
        result = execute_query('command("deps")', embedding_db=db)

        assert isinstance(result, VectorQueryResult)
        assert len(result.matching_entities) > 0
        assert result.matching_entities[0].entity.entity_type == "command"

    def test_relational_query_workflow(self, db) -> None:
        """Test relational query workflow."""
        result = execute_query(
            'command("*") -> job("python-developer")',
            embedding_db=db,
        )

        assert isinstance(result, VectorQueryResult)
        assert result.execution_time_ms > 0

    def test_similarity_search_workflow(self, db) -> None:
        """Test similarity search workflow."""
        result = execute_query(
            'similar_to(command("deps"), distance=0.3)',
            embedding_db=db,
            top_k=5,
        )

        assert isinstance(result, VectorQueryResult)
        assert len(result.matching_entities) <= 5

    def test_optimization_workflow(self, db) -> None:
        """Test optimization workflow."""
        result = execute_query(
            "maximize(outcome_coverage)",
            embedding_db=db,
        )

        assert isinstance(result, RecommendationResult)
        assert len(result.top_k_recommendations) > 0

    def test_complex_logical_query(self, db) -> None:
        """Test complex logical query."""
        result = execute_query(
            'command("deps") OR command("cache")',
            embedding_db=db,
        )

        assert isinstance(result, VectorQueryResult)

    def test_verbose_mode(self, db) -> None:
        """Test verbose mode execution."""
        result = execute_query(
            'command("deps")',
            embedding_db=db,
            verbose=True,
        )

        assert len(result.reasoning_trace.steps) > 0
        assert result.reasoning_trace.execution_plan != ""

    def test_top_k_limiting(self, db) -> None:
        """Test top_k result limiting."""
        result = execute_query(
            'command("*")',
            embedding_db=db,
            top_k=3,
        )

        assert len(result.top_k(3)) <= 3

    def test_wildcard_matching(self, db) -> None:
        """Test wildcard pattern matching."""
        result = execute_query(
            'command("dep*")',
            embedding_db=db,
        )

        assert isinstance(result, VectorQueryResult)

    def test_multiple_queries_same_db(self, db) -> None:
        """Test executing multiple queries on same database."""
        result1 = execute_query('command("deps")', embedding_db=db)
        result2 = execute_query('job("python-developer")', embedding_db=db)

        assert isinstance(result1, VectorQueryResult)
        assert isinstance(result2, VectorQueryResult)

    def test_result_to_dict_conversion(self, db) -> None:
        """Test converting results to dictionary."""
        result = execute_query('command("deps")', embedding_db=db)

        result_dict = result.to_dict()

        assert "matches" in result_dict
        assert "execution_time_ms" in result_dict
        assert isinstance(result_dict["matches"], list)


class TestErrorHandling:
    """Test error handling in end-to-end workflows."""

    def test_invalid_query_syntax(self, db) -> None:
        """Test handling of invalid query syntax."""
        from specify_cli.hyperdimensional.parser import ParseError

        with pytest.raises(ParseError):
            execute_query("invalid syntax @@@", embedding_db=db)

    def test_missing_entity(self, db) -> None:
        """Test querying non-existent entity."""
        result = execute_query(
            'command("nonexistent-command")',
            embedding_db=db,
        )

        # Should return empty results, not error
        assert isinstance(result, VectorQueryResult)


class TestPerformance:
    """Test performance characteristics."""

    def test_simple_query_performance(self, db) -> None:
        """Test that simple queries execute quickly."""
        result = execute_query('command("deps")', embedding_db=db)

        # Should execute in less than 1 second
        assert result.execution_time_ms < 1000

    def test_complex_query_performance(self, db) -> None:
        """Test that complex queries execute reasonably fast."""
        result = execute_query(
            "maximize(outcome_coverage - implementation_effort)",
            embedding_db=db,
        )

        # Should execute in less than 5 seconds
        assert result.execution_time_ms < 5000


class TestResultQuality:
    """Test quality of query results."""

    def test_similarity_results_ordered(self, db) -> None:
        """Test that similarity results are ordered by score."""
        result = execute_query(
            'similar_to(command("deps"), distance=0.5)',
            embedding_db=db,
            top_k=5,
        )

        scores = [m.score for m in result.matching_entities]
        assert scores == sorted(scores, reverse=True)

    def test_confidence_scores_valid(self, db) -> None:
        """Test that confidence scores are in valid range."""
        result = execute_query('command("deps")', embedding_db=db)

        for confidence in result.confidence_scores:
            assert 0.0 <= confidence <= 1.0
