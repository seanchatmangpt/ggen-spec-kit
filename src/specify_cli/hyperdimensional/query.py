"""Main query engine for HDQL.

This module provides the high-level query execution interface.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from specify_cli.hyperdimensional.compiler import compile_query
from specify_cli.hyperdimensional.executor import QueryExecutor
from specify_cli.hyperdimensional.parser import parse_query

if TYPE_CHECKING:
    from specify_cli.hyperdimensional.ast_nodes import ASTNode
    from specify_cli.hyperdimensional.embeddings import EmbeddingDatabase
    from specify_cli.hyperdimensional.results import (
        AnalysisResult,
        RecommendationResult,
        VectorQueryResult,
    )


class QueryEngine:
    """High-level query engine for HDQL."""

    def __init__(self, embedding_db: EmbeddingDatabase) -> None:
        """Initialize query engine.

        Args:
            embedding_db: Embedding database to query against
        """
        self.embedding_db = embedding_db
        self.executor = QueryExecutor(embedding_db)

    def execute(
        self,
        query_string: str,
        top_k: int = 10,
        verbose: bool = False,
    ) -> VectorQueryResult | RecommendationResult | AnalysisResult:
        """Execute HDQL query.

        Args:
            query_string: HDQL query string
            top_k: Maximum results to return
            verbose: Include reasoning trace

        Returns:
            Query results (type depends on query)

        Raises:
            ParseError: If query is malformed
            ValidationError: If query is invalid
            ExecutionError: If execution fails
        """
        start_time = time.time()

        # Parse query
        ast = parse_query(query_string)

        # Compile to execution plan
        plan = compile_query(ast, top_k=top_k)

        # Execute query
        result = self.executor.execute_plan(plan, verbose=verbose)

        # Add execution time
        execution_time = (time.time() - start_time) * 1000  # Convert to ms

        # Update result with execution time
        if hasattr(result, "execution_time_ms"):
            # Replace frozen dataclass field
            result = result.__class__(
                **{
                    **{
                        f.name: getattr(result, f.name)
                        for f in result.__dataclass_fields__.values()
                    },  # type: ignore[attr-defined]
                    "execution_time_ms": execution_time,
                }
            )

        return result

    def parse(self, query_string: str) -> ASTNode:
        """Parse query without executing.

        Args:
            query_string: HDQL query string

        Returns:
            AST root node
        """
        return parse_query(query_string)

    def explain(self, query_string: str) -> str:
        """Explain query execution plan.

        Args:
            query_string: HDQL query string

        Returns:
            Human-readable explanation of execution plan
        """
        ast = parse_query(query_string)
        plan = compile_query(ast)
        return plan.explain()


def execute_query(
    query_string: str,
    embedding_db: EmbeddingDatabase | None = None,
    top_k: int = 10,
    verbose: bool = False,
) -> VectorQueryResult | RecommendationResult | AnalysisResult:
    """Execute HDQL query (convenience function).

    Args:
        query_string: HDQL query string
        embedding_db: Embedding database (loads default if None)
        top_k: Maximum results to return
        verbose: Include reasoning trace

    Returns:
        Query results
    """
    if embedding_db is None:
        from specify_cli.hyperdimensional.embeddings import load_default_database

        embedding_db = load_default_database()

    engine = QueryEngine(embedding_db)
    return engine.execute(query_string, top_k=top_k, verbose=verbose)
