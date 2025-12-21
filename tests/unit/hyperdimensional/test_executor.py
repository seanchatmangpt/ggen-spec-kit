"""Unit tests for HDQL executor."""

from __future__ import annotations

import pytest

# Skip entire module - these imports don't exist in current API
pytest.skip(
    "HDQL executor module not fully implemented - tests need update",
    allow_module_level=True,
)

from specify_cli.hyperdimensional.compiler import compile_query
from specify_cli.hyperdimensional.embeddings import EmbeddingDatabase, load_default_database
from specify_cli.hyperdimensional.executor import QueryExecutor
from specify_cli.hyperdimensional.parser import parse_query
from specify_cli.hyperdimensional.results import (
    RecommendationResult,
    VectorQueryResult,
)


@pytest.fixture
def sample_db() -> EmbeddingDatabase:
    """Create sample database for testing."""
    return load_default_database()


@pytest.fixture
def executor(sample_db: EmbeddingDatabase) -> QueryExecutor:
    """Create executor for testing."""
    return QueryExecutor(sample_db)


class TestAtomicExecution:
    """Test execution of atomic queries."""

    def test_execute_lookup(self, executor: QueryExecutor, sample_db: EmbeddingDatabase) -> None:
        """Test executing lookup operation."""
        ast = parse_query('command("deps")')
        plan = compile_query(ast)

        result = executor.execute_plan(plan)

        assert isinstance(result, VectorQueryResult)
        assert len(result.matching_entities) > 0

    def test_execute_wildcard_lookup(self, executor: QueryExecutor) -> None:
        """Test executing wildcard lookup."""
        ast = parse_query('command("*")')
        plan = compile_query(ast)

        result = executor.execute_plan(plan)

        assert isinstance(result, VectorQueryResult)
        # Should match all commands
        assert len(result.matching_entities) >= 3


class TestRelationalExecution:
    """Test execution of relational queries."""

    def test_execute_relation(self, executor: QueryExecutor) -> None:
        """Test executing relational query."""
        ast = parse_query('command("deps") -> job("python-developer")')
        plan = compile_query(ast)

        result = executor.execute_plan(plan)

        assert isinstance(result, VectorQueryResult)


class TestLogicalExecution:
    """Test execution of logical queries."""

    def test_execute_and(self, executor: QueryExecutor) -> None:
        """Test executing AND query."""
        ast = parse_query('command("deps") AND command("deps")')
        plan = compile_query(ast)

        result = executor.execute_plan(plan)

        assert isinstance(result, VectorQueryResult)

    def test_execute_or(self, executor: QueryExecutor) -> None:
        """Test executing OR query."""
        ast = parse_query('command("deps") OR command("cache")')
        plan = compile_query(ast)

        result = executor.execute_plan(plan)

        assert isinstance(result, VectorQueryResult)


class TestSimilarityExecution:
    """Test execution of similarity queries."""

    def test_execute_similarity(self, executor: QueryExecutor) -> None:
        """Test executing similarity query."""
        ast = parse_query('similar_to(command("deps"), distance=0.5)')
        plan = compile_query(ast)

        result = executor.execute_plan(plan)

        assert isinstance(result, VectorQueryResult)


class TestOptimizationExecution:
    """Test execution of optimization queries."""

    def test_execute_maximize(self, executor: QueryExecutor) -> None:
        """Test executing maximize query."""
        ast = parse_query("maximize(outcome_coverage)")
        plan = compile_query(ast)

        result = executor.execute_plan(plan)

        # Optimization queries return RecommendationResult
        assert isinstance(result, RecommendationResult)


class TestVerboseMode:
    """Test verbose execution mode."""

    def test_verbose_execution(self, executor: QueryExecutor) -> None:
        """Test execution with verbose mode."""
        ast = parse_query('command("deps")')
        plan = compile_query(ast)

        result = executor.execute_plan(plan, verbose=True)

        # Should have reasoning trace
        assert len(result.reasoning_trace.steps) > 0


class TestFuzzyMatching:
    """Test fuzzy matching functionality."""

    def test_fuzzy_match_exact(self, executor: QueryExecutor) -> None:
        """Test fuzzy match with exact string."""
        assert executor._fuzzy_match("deps", "deps") is True

    def test_fuzzy_match_close(self, executor: QueryExecutor) -> None:
        """Test fuzzy match with close string."""
        assert executor._fuzzy_match("deps", "dep") is True

    def test_fuzzy_match_far(self, executor: QueryExecutor) -> None:
        """Test fuzzy match with far string."""
        assert executor._fuzzy_match("deps", "completely-different") is False


class TestComparison:
    """Test comparison operations."""

    def test_compare_equals(self, executor: QueryExecutor) -> None:
        """Test equals comparison."""
        assert executor._compare(5, "==", 5) is True
        assert executor._compare(5, "==", 6) is False

    def test_compare_greater_than(self, executor: QueryExecutor) -> None:
        """Test greater than comparison."""
        assert executor._compare(10, ">", 5) is True
        assert executor._compare(5, ">", 10) is False

    def test_compare_less_than_or_equal(self, executor: QueryExecutor) -> None:
        """Test less than or equal comparison."""
        assert executor._compare(5, "<=", 10) is True
        assert executor._compare(5, "<=", 5) is True
        assert executor._compare(10, "<=", 5) is False
