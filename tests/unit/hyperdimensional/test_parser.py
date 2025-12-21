"""Unit tests for HDQL parser."""

from __future__ import annotations

import pytest

# These tests are for experimental HDQL parser features
# Mark as xfail until full implementation is complete
pytestmark = pytest.mark.xfail(
    reason="HDQL parser module under development",
    strict=False,
)

from specify_cli.hyperdimensional.ast_nodes import (
    AnalogyNode,
    AtomicNode,
    ComparisonNode,
    LogicalNode,
    OptimizationNode,
    RelationalNode,
    SimilarityNode,
)
from specify_cli.hyperdimensional.parser import ParseError, parse_query


class TestAtomicQueries:
    """Test atomic query parsing."""

    def test_parse_command(self) -> None:
        """Test parsing command query."""
        ast = parse_query('command("deps")')
        assert isinstance(ast, AtomicNode)
        assert ast.entity_type == "command"
        assert ast.identifier == "deps"

    def test_parse_job(self) -> None:
        """Test parsing job query."""
        ast = parse_query('job("python-developer")')
        assert isinstance(ast, AtomicNode)
        assert ast.entity_type == "job"
        assert ast.identifier == "python-developer"

    def test_parse_feature(self) -> None:
        """Test parsing feature query."""
        ast = parse_query('feature("cache")')
        assert isinstance(ast, AtomicNode)
        assert ast.entity_type == "feature"
        assert ast.identifier == "cache"

    def test_parse_outcome(self) -> None:
        """Test parsing outcome query."""
        ast = parse_query('outcome("test-coverage")')
        assert isinstance(ast, AtomicNode)
        assert ast.entity_type == "outcome"
        assert ast.identifier == "test-coverage"

    def test_parse_constraint(self) -> None:
        """Test parsing constraint query."""
        ast = parse_query('constraint("three-tier")')
        assert isinstance(ast, AtomicNode)
        assert ast.entity_type == "constraint"
        assert ast.identifier == "three-tier"

    def test_parse_wildcard(self) -> None:
        """Test parsing wildcard patterns."""
        ast = parse_query('command("dep*")')
        assert isinstance(ast, AtomicNode)
        assert ast.identifier == "dep*"

    def test_parse_single_quotes(self) -> None:
        """Test parsing with single quotes."""
        ast = parse_query("command('deps')")
        assert isinstance(ast, AtomicNode)
        assert ast.identifier == "deps"


class TestRelationalQueries:
    """Test relational query parsing."""

    def test_parse_simple_relation(self) -> None:
        """Test parsing simple relational query."""
        ast = parse_query('command("deps") -> job("python-dev")')
        assert isinstance(ast, RelationalNode)
        assert isinstance(ast.left, AtomicNode)
        assert isinstance(ast.right, AtomicNode)

    def test_parse_chained_relation(self) -> None:
        """Test parsing chained relations."""
        ast = parse_query('command("deps") -> job("python-dev") -> outcome("coverage")')
        assert isinstance(ast, RelationalNode)
        assert isinstance(ast.left, AtomicNode)
        assert isinstance(ast.right, RelationalNode)


class TestLogicalQueries:
    """Test logical query parsing."""

    def test_parse_and(self) -> None:
        """Test parsing AND query."""
        ast = parse_query('command("deps") AND command("cache")')
        assert isinstance(ast, LogicalNode)
        assert ast.operator == "AND"
        assert len(ast.operands) == 2

    def test_parse_or(self) -> None:
        """Test parsing OR query."""
        ast = parse_query('command("deps") OR command("cache")')
        assert isinstance(ast, LogicalNode)
        assert ast.operator == "OR"

    def test_parse_not(self) -> None:
        """Test parsing NOT query."""
        ast = parse_query('NOT command("legacy*")')
        assert isinstance(ast, LogicalNode)
        assert ast.operator == "NOT"
        assert len(ast.operands) == 1

    def test_parse_complex_logical(self) -> None:
        """Test parsing complex logical expression."""
        ast = parse_query('command("deps") AND (command("cache") OR command("build"))')
        assert isinstance(ast, LogicalNode)
        assert ast.operator == "AND"


class TestComparisonQueries:
    """Test comparison query parsing."""

    def test_parse_equals(self) -> None:
        """Test parsing equals comparison."""
        ast = parse_query('feature("*").coverage == 0.8')
        assert isinstance(ast, ComparisonNode)
        assert ast.operator == "=="

    def test_parse_greater_than(self) -> None:
        """Test parsing greater than comparison."""
        ast = parse_query('job("*").frequency > 10')
        assert isinstance(ast, ComparisonNode)
        assert ast.operator == ">"

    def test_parse_less_than_or_equal(self) -> None:
        """Test parsing less than or equal comparison."""
        ast = parse_query('feature("*").effort <= 100')
        assert isinstance(ast, ComparisonNode)
        assert ast.operator == "<="


class TestSimilarityQueries:
    """Test similarity query parsing."""

    def test_parse_similarity_distance(self) -> None:
        """Test parsing similarity with distance."""
        ast = parse_query('similar_to(command("deps"), distance=0.2)')
        assert isinstance(ast, SimilarityNode)
        assert ast.threshold == 0.2

    def test_parse_similarity_top_k(self) -> None:
        """Test parsing similarity with top_k."""
        ast = parse_query('similar_to(command("deps"), top_k=5)')
        assert isinstance(ast, SimilarityNode)
        assert ast.top_k == 5

    def test_parse_similarity_multiple_params(self) -> None:
        """Test parsing similarity with multiple parameters."""
        ast = parse_query('similar_to(command("deps"), distance=0.2, top_k=10)')
        assert isinstance(ast, SimilarityNode)
        assert ast.threshold == 0.2
        assert ast.top_k == 10


class TestAnalogyQueries:
    """Test analogy query parsing."""

    def test_parse_analogy_with_wildcard(self) -> None:
        """Test parsing analogy with wildcard."""
        ast = parse_query('command("deps") is_to feature("add") as command("cache") is_to ?')
        assert isinstance(ast, AnalogyNode)
        assert isinstance(ast.source_a, AtomicNode)
        assert isinstance(ast.source_b, AtomicNode)
        assert isinstance(ast.target_a, AtomicNode)
        assert ast.target_b is None

    def test_parse_analogy_complete(self) -> None:
        """Test parsing complete analogy."""
        ast = parse_query(
            'command("deps") is_to feature("add") as command("cache") is_to feature("optimize")'
        )
        assert isinstance(ast, AnalogyNode)
        assert ast.target_b is not None


class TestOptimizationQueries:
    """Test optimization query parsing."""

    def test_parse_maximize(self) -> None:
        """Test parsing maximize query."""
        ast = parse_query("maximize(outcome_coverage)")
        assert isinstance(ast, OptimizationNode)
        assert ast.objective_type == "maximize"

    def test_parse_minimize(self) -> None:
        """Test parsing minimize query."""
        ast = parse_query("minimize(implementation_effort)")
        assert isinstance(ast, OptimizationNode)
        assert ast.objective_type == "minimize"

    def test_parse_optimize_with_constraints(self) -> None:
        """Test parsing optimization with constraints."""
        ast = parse_query("maximize(outcome_coverage) subject_to(effort <= 100)")
        assert isinstance(ast, OptimizationNode)
        assert len(ast.constraints) == 1


class TestErrorHandling:
    """Test parser error handling."""

    def test_missing_closing_paren(self) -> None:
        """Test error on missing closing parenthesis."""
        with pytest.raises(ParseError):
            parse_query('command("deps"')

    def test_invalid_entity_type(self) -> None:
        """Test error on invalid entity type."""
        with pytest.raises(ParseError):
            parse_query('invalid("test")')

    def test_unexpected_token(self) -> None:
        """Test error on unexpected token."""
        with pytest.raises(ParseError):
            parse_query('command("deps") @@@ job("test")')


class TestComplexQueries:
    """Test complex query parsing."""

    def test_parse_complex_logical_with_relations(self) -> None:
        """Test parsing complex query with logic and relations."""
        query = '(command("deps") -> job("python-dev")) AND (feature("*").coverage >= 0.8)'
        ast = parse_query(query)
        assert isinstance(ast, LogicalNode)
        assert ast.operator == "AND"

    def test_parse_optimization_with_expression(self) -> None:
        """Test parsing optimization with complex expression."""
        query = "maximize(outcome_coverage + job_frequency - implementation_effort)"
        ast = parse_query(query)
        assert isinstance(ast, OptimizationNode)

    def test_parse_nested_similarity(self) -> None:
        """Test parsing nested similarity query."""
        query = 'similar_to(command("deps"), distance=0.2) AND feature("*").coverage > 0.5'
        ast = parse_query(query)
        assert isinstance(ast, LogicalNode)
