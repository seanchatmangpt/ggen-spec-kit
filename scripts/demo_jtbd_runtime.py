#!/usr/bin/env python
# ruff: noqa: T201  # Allow print statements in demo scripts
"""
Demo script for JTBD runtime layer functions.

This demonstrates all the I/O operations implemented in the JTBD runtime layer.
"""

from pathlib import Path
from tempfile import TemporaryDirectory

from specify_cli.runtime.jtbd import (
    export_jtbd_metrics,
    query_jtbd_sparql,
    sync_jtbd_to_rdf,
)


def demo_export_json():
    """Demo: Export metrics to JSON."""
    print("\n=== Demo: Export to JSON ===")

    metrics = {
        "job_completion_rate": 0.85,
        "avg_outcome_achievement": 92.3,
        "total_painpoints_resolved": 15,
        "avg_time_to_outcome_seconds": 8.5,
        "satisfaction": {
            "very_satisfied": 42,
            "satisfied": 30,
            "neutral": 5,
        },
    }

    with TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "metrics.json"
        result = export_jtbd_metrics(metrics, output_path, format="json")

        print(f"Success: {result['success']}")
        print(f"Output: {result['path']}")
        print(f"Format: {result['format']}")

        if result["success"]:
            print(f"\nContent:\n{output_path.read_text()}")


def demo_export_csv():
    """Demo: Export metrics to CSV."""
    print("\n=== Demo: Export to CSV ===")

    metrics = {
        "job_completion_rate": 0.85,
        "avg_outcome_achievement": 92.3,
        "total_painpoints_resolved": 15,
    }

    with TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "metrics.csv"
        result = export_jtbd_metrics(metrics, output_path, format="csv")

        print(f"Success: {result['success']}")
        print(f"Output: {result['path']}")
        print(f"Format: {result['format']}")

        if result["success"]:
            print(f"\nContent:\n{output_path.read_text()}")


def demo_sync_to_rdf():
    """Demo: Sync metrics to RDF/Turtle."""
    print("\n=== Demo: Sync to RDF ===")

    metrics = {
        "job_completion_rate": 0.85,
        "avg_outcome_achievement": 92.3,
        "total_painpoints_resolved": 15,
    }

    with TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "jtbd-metrics.ttl"
        result = sync_jtbd_to_rdf(metrics, output_path)

        print(f"Success: {result['success']}")
        print(f"Output: {result['path']}")
        print(f"Triples: {result['triples_count']}")

        if result["success"]:
            print(f"\nContent:\n{output_path.read_text()}")


def demo_sparql_query():
    """Demo: Execute SPARQL query (placeholder)."""
    print("\n=== Demo: SPARQL Query (Placeholder) ===")

    # First create RDF data
    metrics = {"job_completion_rate": 0.85}

    with TemporaryDirectory() as tmpdir:
        rdf_path = Path(tmpdir) / "jtbd-metrics.ttl"
        sync_result = sync_jtbd_to_rdf(metrics, rdf_path)

        if sync_result["success"]:
            # Execute SPARQL query
            query = """
            SELECT ?metric ?value WHERE {
                ?s jtbd:jobcompletionrate ?value .
                BIND("job_completion_rate" AS ?metric)
            }
            """

            result = query_jtbd_sparql(query, rdf_path)

            print(f"Success: {result['success']}")
            print(f"Results count: {result['count']}")
            print(f"Results: {result['results']}")
            print("\nNote: This is a placeholder. Integrate with actual SPARQL engine.")


if __name__ == "__main__":
    print("JTBD Runtime Layer Demo")
    print("=" * 60)

    demo_export_json()
    demo_export_csv()
    demo_sync_to_rdf()
    demo_sparql_query()

    print("\n" + "=" * 60)
    print("✓ All demos completed successfully!")
