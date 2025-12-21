"""Unit tests for HDQL compiler."""

from __future__ import annotations

from specify_cli.hyperdimensional.compiler import compile_query
from specify_cli.hyperdimensional.parser import parse_query


class TestAtomicCompilation:
    """Test compilation of atomic queries."""

    def test_compile_atomic_command(self) -> None:
        """Test compiling atomic command query."""
        ast = parse_query('command("deps")')
        plan = compile_query(ast)

        # Should have lookup + collect operations
        assert len(plan.operations) >= 2
        assert any(op.op_type == "lookup" for op in plan.operations)
        assert plan.operations[-1].op_type == "collect_results"

    def test_compile_atomic_with_wildcard(self) -> None:
        """Test compiling atomic query with wildcard."""
        ast = parse_query('command("dep*")')
        plan = compile_query(ast)

        lookup_op = next(op for op in plan.operations if op.op_type == "lookup")
        assert lookup_op.parameters["identifier"] == "dep*"


class TestRelationalCompilation:
    """Test compilation of relational queries."""

    def test_compile_simple_relation(self) -> None:
        """Test compiling simple relational query."""
        ast = parse_query('command("deps") -> job("python-dev")')
        plan = compile_query(ast)

        # Should have two lookups and a bind operation
        assert sum(1 for op in plan.operations if op.op_type == "lookup") >= 2
        assert any(op.op_type == "bind_relation" for op in plan.operations)


class TestLogicalCompilation:
    """Test compilation of logical queries."""

    def test_compile_and(self) -> None:
        """Test compiling AND query."""
        ast = parse_query('command("deps") AND command("cache")')
        plan = compile_query(ast)

        assert any(
            op.op_type == "logical" and op.parameters.get("operator") == "AND"
            for op in plan.operations
        )

    def test_compile_or(self) -> None:
        """Test compiling OR query."""
        ast = parse_query('command("deps") OR command("cache")')
        plan = compile_query(ast)

        assert any(
            op.op_type == "logical" and op.parameters.get("operator") == "OR"
            for op in plan.operations
        )

    def test_compile_not(self) -> None:
        """Test compiling NOT query."""
        ast = parse_query('NOT command("legacy*")')
        plan = compile_query(ast)

        assert any(
            op.op_type == "logical" and op.parameters.get("operator") == "NOT"
            for op in plan.operations
        )


class TestComparisonCompilation:
    """Test compilation of comparison queries."""

    def test_compile_comparison(self) -> None:
        """Test compiling comparison query."""
        ast = parse_query('feature("*").coverage >= 0.8')
        plan = compile_query(ast)

        assert any(op.op_type == "filter" for op in plan.operations)
        filter_op = next(op for op in plan.operations if op.op_type == "filter")
        assert filter_op.parameters["operator"] == ">="


class TestSimilarityCompilation:
    """Test compilation of similarity queries."""

    def test_compile_similarity(self) -> None:
        """Test compiling similarity query."""
        ast = parse_query('similar_to(command("deps"), distance=0.2)')
        plan = compile_query(ast)

        assert any(op.op_type == "similarity" for op in plan.operations)
        sim_op = next(op for op in plan.operations if op.op_type == "similarity")
        assert sim_op.parameters["threshold"] == 0.2


class TestOptimizationCompilation:
    """Test compilation of optimization queries."""

    def test_compile_maximize(self) -> None:
        """Test compiling maximize query."""
        ast = parse_query("maximize(outcome_coverage)")
        plan = compile_query(ast)

        assert any(op.op_type == "optimize" for op in plan.operations)
        opt_op = next(op for op in plan.operations if op.op_type == "optimize")
        assert opt_op.parameters["objective_type"] == "maximize"


class TestCostEstimation:
    """Test query cost estimation."""

    def test_cost_estimation(self) -> None:
        """Test that plan has cost estimate."""
        ast = parse_query('command("deps") -> job("python-dev")')
        plan = compile_query(ast)

        assert plan.estimated_cost > 0

    def test_complex_query_higher_cost(self) -> None:
        """Test that complex queries have higher cost."""
        simple_ast = parse_query('command("deps")')
        complex_ast = parse_query("maximize(outcome_coverage) subject_to(effort <= 100)")

        simple_plan = compile_query(simple_ast)
        complex_plan = compile_query(complex_ast)

        assert complex_plan.estimated_cost > simple_plan.estimated_cost


class TestIndexHints:
    """Test index hint generation."""

    def test_similarity_index_hint(self) -> None:
        """Test that similarity queries generate index hints."""
        ast = parse_query('similar_to(command("deps"), distance=0.2)')
        plan = compile_query(ast)

        # Should suggest HNSW index for similarity
        assert any("HNSW" in hint or "similarity" in hint for hint in plan.index_hints)

    def test_lookup_index_hint(self) -> None:
        """Test that lookup queries generate index hints."""
        ast = parse_query('command("deps")')
        plan = compile_query(ast)

        # Should suggest hash index for exact lookups
        assert any("hash" in hint or "lookup" in hint for hint in plan.index_hints)
