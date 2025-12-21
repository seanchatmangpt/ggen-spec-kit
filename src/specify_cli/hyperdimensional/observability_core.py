"""
specify_cli.hyperdimensional.observability_core
------------------------------------------------
Minimal observability wrapper for hyperdimensional operations.

This module provides OTEL instrumentation for hyperdimensional computing
operations using the existing spec-kit telemetry infrastructure.

80/20 Approach
--------------
- Uses existing OTEL setup from core.telemetry
- Tracks only essential operations (embeddings, search, validation)
- Simple span creation with basic attributes
- No custom dashboards, metrics aggregation, or visualization

Example
-------
    from specify_cli.hyperdimensional.observability_core import (
        track_embedding_operation,
        track_similarity_search,
        track_validation_check,
    )

    # Track embedding creation
    with track_embedding_operation("embed_command", vector_count=1):
        vector = embed_command("init")

    # Track similarity search
    with track_similarity_search("find_similar_features", result_count=10):
        results = search_features(query)

    # Track validation
    with track_validation_check("spec_compliance", passed=True):
        score = verify_spec_compliance(code, spec)
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING, Any

from specify_cli.core.telemetry import metric_counter, metric_histogram, span

if TYPE_CHECKING:
    from collections.abc import Generator

    # Import for type hints
    try:
        from opentelemetry.trace import Span
    except ImportError:

        class Span:  # type: ignore[no-redef]
            """Dummy span type for type checking."""


# ============================================================================
# Embedding Operations
# ============================================================================


@contextmanager
def track_embedding_operation(
    operation_name: str,
    vector_count: int = 1,
    dimensions: int | None = None,
    **attributes: Any,
) -> Generator[Any, None, None]:
    """
    Track hyperdimensional embedding operations.

    Creates an OTEL span for embedding operations with basic metrics.

    Parameters
    ----------
    operation_name : str
        Name of the embedding operation (e.g., "embed_command", "bind_vectors")
    vector_count : int, optional
        Number of vectors being processed. Default is 1.
    dimensions : int, optional
        Dimensionality of vectors, if relevant.
    **attributes
        Additional span attributes.

    Yields
    ------
    Generator
        OTEL span context.

    Example
    -------
        >>> with track_embedding_operation("embed_feature", vector_count=5, dimensions=10000):
        ...     vectors = [embed_feature(f) for f in features]
    """
    span_name = f"hyperdimensional.embedding.{operation_name}"

    attrs: dict[str, Any] = {
        "hd.operation": operation_name,
        "hd.operation.type": "embedding",
        "hd.vector.count": vector_count,
    }

    if dimensions is not None:
        attrs["hd.vector.dimensions"] = dimensions

    attrs.update(attributes)

    # Increment operation counter
    counter = metric_counter(f"hyperdimensional.embedding.{operation_name}.operations")
    counter(1)

    with span(span_name, **attrs) as current_span:  # type: ignore[var-annotated]
        try:
            yield current_span
            # Track successful completion
            success_counter = metric_counter(
                f"hyperdimensional.embedding.{operation_name}.success"
            )
            success_counter(1)
        except Exception as e:
            # Track failures
            error_counter = metric_counter(f"hyperdimensional.embedding.{operation_name}.errors")
            error_counter(1)
            current_span.set_attribute("error", True)
            current_span.set_attribute("error.type", type(e).__name__)
            raise


# ============================================================================
# Similarity Search Operations
# ============================================================================


@contextmanager
def track_similarity_search(
    query_name: str,
    result_count: int = 0,
    search_type: str = "semantic",
    **attributes: Any,
) -> Generator[Any, None, None]:
    """
    Track semantic similarity search operations.

    Creates an OTEL span for search operations with result metrics.

    Parameters
    ----------
    query_name : str
        Name/description of the search query.
    result_count : int, optional
        Number of results returned. Default is 0.
    search_type : str, optional
        Type of search (semantic, similarity, feature). Default is "semantic".
    **attributes
        Additional span attributes.

    Yields
    ------
    Generator
        OTEL span context.

    Example
    -------
        >>> with track_similarity_search("find_similar_commands", result_count=10):
        ...     results = search_by_semantic_similarity(query, k=10)
    """
    span_name = f"hyperdimensional.search.{search_type}"

    attrs: dict[str, Any] = {
        "hd.operation": query_name,
        "hd.operation.type": "search",
        "hd.search.type": search_type,
        "hd.search.result_count": result_count,
    }

    attrs.update(attributes)

    # Increment search counter
    counter = metric_counter(f"hyperdimensional.search.{search_type}.operations")
    counter(1)

    # Track result count histogram
    result_histogram = metric_histogram(
        f"hyperdimensional.search.{search_type}.result_count", unit="results"
    )

    with span(span_name, **attrs) as current_span:  # type: ignore[var-annotated]
        try:
            yield current_span
            # Record result count
            result_histogram(float(result_count))
            # Track successful completion
            success_counter = metric_counter(f"hyperdimensional.search.{search_type}.success")
            success_counter(1)
        except Exception as e:
            # Track failures
            error_counter = metric_counter(f"hyperdimensional.search.{search_type}.errors")
            error_counter(1)
            current_span.set_attribute("error", True)
            current_span.set_attribute("error.type", type(e).__name__)
            raise


# ============================================================================
# Validation Operations
# ============================================================================


@contextmanager
def track_validation_check(
    check_name: str,
    passed: bool | None = None,
    score: float | None = None,
    **attributes: Any,
) -> Generator[Any, None, None]:
    """
    Track validation and verification operations.

    Creates an OTEL span for validation checks with pass/fail metrics.

    Parameters
    ----------
    check_name : str
        Name of the validation check (e.g., "spec_compliance", "type_safety")
    passed : bool, optional
        Whether the validation passed. Set after check completes.
    score : float, optional
        Validation score (0.0 to 1.0), if applicable.
    **attributes
        Additional span attributes.

    Yields
    ------
    Generator
        OTEL span context.

    Example
    -------
        >>> with track_validation_check("spec_compliance", score=0.95) as span:
        ...     compliance_score = verify_spec_compliance(code, spec)
        ...     span.set_attribute("hd.validation.score", compliance_score)
    """
    span_name = f"hyperdimensional.validation.{check_name}"

    attrs: dict[str, Any] = {
        "hd.operation": check_name,
        "hd.operation.type": "validation",
        "hd.validation.check": check_name,
    }

    if passed is not None:
        attrs["hd.validation.passed"] = passed

    if score is not None:
        attrs["hd.validation.score"] = score

    attrs.update(attributes)

    # Increment validation counter
    counter = metric_counter(f"hyperdimensional.validation.{check_name}.checks")
    counter(1)

    # Track validation scores
    score_histogram = metric_histogram(f"hyperdimensional.validation.{check_name}.score", unit="")

    with span(span_name, **attrs) as current_span:  # type: ignore[var-annotated]
        try:
            yield current_span

            # Record score if available
            if score is not None:
                score_histogram(score)

            # Track pass/fail
            if passed is not None:
                if passed:
                    passed_counter = metric_counter(
                        f"hyperdimensional.validation.{check_name}.passed"
                    )
                    passed_counter(1)
                else:
                    failed_counter = metric_counter(
                        f"hyperdimensional.validation.{check_name}.failed"
                    )
                    failed_counter(1)

        except Exception as e:
            # Track errors
            error_counter = metric_counter(f"hyperdimensional.validation.{check_name}.errors")
            error_counter(1)
            current_span.set_attribute("error", True)
            current_span.set_attribute("error.type", type(e).__name__)
            raise


# ============================================================================
# Convenience Functions
# ============================================================================


def record_vector_stats(
    vector_count: int,
    dimensions: int,
    operation: str = "general",
) -> None:
    """
    Record basic vector statistics as metrics.

    Parameters
    ----------
    vector_count : int
        Number of vectors processed.
    dimensions : int
        Dimensionality of vectors.
    operation : str, optional
        Operation type for labeling. Default is "general".

    Example
    -------
        >>> record_vector_stats(vector_count=100, dimensions=10000, operation="bulk_embed")
    """
    counter = metric_counter(f"hyperdimensional.vectors.{operation}.d{dimensions}.processed")
    counter(vector_count)


def record_search_latency(latency_ms: float, search_type: str = "semantic") -> None:
    """
    Record search latency.

    Parameters
    ----------
    latency_ms : float
        Search latency in milliseconds.
    search_type : str, optional
        Type of search. Default is "semantic".

    Example
    -------
        >>> import time
        >>> start = time.perf_counter()
        >>> results = search_features(query)
        >>> latency_ms = (time.perf_counter() - start) * 1000
        >>> record_search_latency(latency_ms, "feature_search")
    """
    latency_histogram = metric_histogram(
        f"hyperdimensional.search.{search_type}.latency_ms", unit="ms"
    )
    latency_histogram(latency_ms)


__all__ = [
    "record_search_latency",
    "record_vector_stats",
    "track_embedding_operation",
    "track_similarity_search",
    "track_validation_check",
]
