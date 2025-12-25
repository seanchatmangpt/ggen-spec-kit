"""
specify_cli.ops.ggen_timeout - SPARQL Query Timeout Handling
===========================================================

Timeout handling for SPARQL query execution.

Implements Phase 1 critical fix: SPARQL timeout to prevent query hangs
(RPN 350). Prevents pipeline blockage from infinite queries or exponential
backtracking.

Key Features:
- Configurable timeout for SPARQL queries
- Default 30-second timeout
- Thread-based execution with timeout
- Clear timeout error messages

Examples:
    >>> from specify_cli.ops.ggen_timeout import execute_sparql_with_timeout
    >>> results = execute_sparql_with_timeout(
    ...     graph, query,
    ...     timeout_seconds=30
    ... )

See Also:
    - specify_cli.runtime.ggen : Runtime ggen operations
    - docs/GGEN_SYNC_POKA_YOKE.md : Error-proofing design

Notes:
    Prevents SPARQL query hangs which can block entire pipelines.
    Uses thread-based timeout that works across platforms.
"""

from __future__ import annotations

import threading
from typing import Any, TypeVar

__all__ = [
    "SPARQLTimeoutError",
    "execute_with_timeout",
]

T = TypeVar("T")


class SPARQLTimeoutError(Exception):
    """Raised when SPARQL query execution times out."""

    def __init__(self, timeout_seconds: float, query: str | None = None) -> None:
        """Initialize timeout error.

        Parameters
        ----------
        timeout_seconds : float
            Timeout duration in seconds.
        query : str | None
            Optional query string for debugging.
        """
        query_preview = ""
        if query:
            preview = query[:80].replace("\n", " ")
            query_preview = f"\nQuery: {preview}..."

        super().__init__(
            f"SPARQL query execution timed out after {timeout_seconds}s{query_preview}"
        )
        self.timeout_seconds = timeout_seconds


def execute_with_timeout(
    func: Callable[..., Any],
    *args: Any,
    timeout_seconds: float = 30,
    **kwargs: Any,
) -> Any:
    """Execute function with timeout.

    Parameters
    ----------
    func : callable
        Function to execute.
    *args : Any
        Positional arguments for function.
    timeout_seconds : float
        Timeout in seconds (0 = no timeout).
    **kwargs : Any
        Keyword arguments for function.

    Returns
    -------
    Any
        Function result.

    Raises
    ------
    SPARQLTimeoutError
        If function execution times out.
    """
    if timeout_seconds <= 0:
        # No timeout - just call function
        return func(*args, **kwargs)

    result: list[Any] = []
    exception: list[BaseException] = []

    def target() -> None:
        """Execute function and store result."""
        try:
            result.append(func(*args, **kwargs))
        except BaseException as e:
            exception.append(e)

    # Start execution in thread
    thread = threading.Thread(target=target, daemon=True)
    thread.start()

    # Wait for completion or timeout
    thread.join(timeout=timeout_seconds)

    # Check if thread finished
    if thread.is_alive():
        # Thread still running - timeout occurred
        raise SPARQLTimeoutError(
            timeout_seconds,
            query=kwargs.get("query") or str(args[0] if args else ""),
        )

    # Check for exceptions
    if exception:
        raise exception[0]

    # Return result
    if not result:
        raise SPARQLTimeoutError(timeout_seconds)

    return result[0]


def sparql_execute_with_timeout(
    graph: Any,
    query: str,
    timeout_seconds: float = 30,
) -> Any:
    """Execute SPARQL query with timeout.

    Wrapper for rdflib graph.query() with timeout support.

    Parameters
    ----------
    graph : Any
        rdflib Graph object.
    query : str
        SPARQL query string.
    timeout_seconds : float
        Timeout in seconds (default 30).

    Returns
    -------
    Any
        Query results.

    Raises
    ------
    SPARQLTimeoutError
        If query times out.
    """
    return execute_with_timeout(
        graph.query,
        query,
        timeout_seconds=timeout_seconds,
    )
