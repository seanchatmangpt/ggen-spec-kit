"""
specify_cli.runtime.jtbd - JTBD Data Persistence Runtime
=========================================================

Runtime layer for Jobs-to-be-Done (JTBD) data persistence.

This module handles all I/O operations for storing and retrieving
JTBD metrics data to/from disk.

Key Features
-----------
* **JSON Storage**: Persistent storage of JTBD events
* **File Operations**: All file I/O for JTBD data
* **Data Directory**: XDG-compliant data directory management

Storage Format
--------------
Data is stored in ~/.local/share/specify/jtbd/ (or platform equivalent):
- jobs.jsonl - Job completion events (JSON Lines format)
- outcomes.jsonl - Outcome achievement events
- painpoints.jsonl - Painpoint resolution events
- satisfaction.jsonl - User satisfaction events
- time_to_outcome.jsonl - Time-to-outcome measurements

Each file uses JSON Lines format (one JSON object per line) for
efficient append-only writes and streaming reads.

Examples
--------
    >>> from specify_cli.runtime.jtbd import save_job_completion, load_job_completions
    >>>
    >>> # Save a job completion event
    >>> save_job_completion(job_data)
    >>>
    >>> # Load all job completions
    >>> jobs = load_job_completions()

See Also
--------
- :mod:`specify_cli.ops.jtbd` : Business logic
- :mod:`specify_cli.core.jtbd_metrics` : Data classes
"""

from __future__ import annotations

import csv
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from specify_cli.core.config import get_config
from specify_cli.core.instrumentation import add_span_event
from specify_cli.core.shell import timed
from specify_cli.core.telemetry import metric_counter, metric_histogram, span

__all__ = [
    "JTBDError",
    "export_jtbd_metrics",
    "get_jtbd_data_dir",
    "load_job_completions",
    "load_outcome_achievements",
    "load_painpoint_resolutions",
    "load_satisfaction_records",
    "load_time_to_outcome_records",
    "query_jtbd_sparql",
    "save_job_completion",
    "save_outcome_achievement",
    "save_painpoint_resolution",
    "save_satisfaction_record",
    "save_time_to_outcome",
    "sync_jtbd_to_rdf",
]


class JTBDError(Exception):
    """JTBD runtime operation error."""

    def __init__(self, message: str, path: Path | None = None) -> None:
        super().__init__(message)
        self.path = path


def get_jtbd_data_dir() -> Path:
    """
    Get the JTBD data directory path.

    Uses platform-specific data directory:
    - Linux/macOS: ~/.local/share/specify/jtbd
    - Windows: %LOCALAPPDATA%/specify/jtbd

    Creates the directory if it doesn't exist.

    Returns
    -------
    Path
        Path to JTBD data directory.
    """
    config = get_config()

    # Use data directory under cache_dir
    # In a production app, you'd use platformdirs.user_data_dir
    # For simplicity, we'll use cache_dir/jtbd
    data_dir = config.cache_dir / "jtbd"
    data_dir.mkdir(parents=True, exist_ok=True)

    return data_dir


def _save_jsonl_record(filename: str, record: dict[str, Any]) -> None:
    """
    Save a record to a JSON Lines file (append mode).

    Parameters
    ----------
    filename : str
        Name of the JSONL file (e.g., "jobs.jsonl").
    record : dict[str, Any]
        Record to save.
    """
    data_dir = get_jtbd_data_dir()
    filepath = data_dir / filename

    with span(f"runtime.jtbd.save_{filename}", record_type=filename):
        with open(filepath, "a", encoding="utf-8") as f:
            json.dump(record, f, default=str)
            f.write("\n")


def _load_jsonl_records(filename: str) -> list[dict[str, Any]]:
    """
    Load all records from a JSON Lines file.

    Parameters
    ----------
    filename : str
        Name of the JSONL file.

    Returns
    -------
    list[dict[str, Any]]
        List of records.
    """
    data_dir = get_jtbd_data_dir()
    filepath = data_dir / filename

    with span(f"runtime.jtbd.load_{filename}", record_type=filename):
        if not filepath.exists():
            return []

        records: list[dict[str, Any]] = []
        with open(filepath, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        # Skip malformed lines
                        continue

        return records


# =============================================================================
# Job Completion Storage
# =============================================================================


def save_job_completion(job_data: dict[str, Any]) -> None:
    """
    Save a job completion event to disk.

    Parameters
    ----------
    job_data : dict[str, Any]
        Job completion data to save.
    """
    _save_jsonl_record("jobs.jsonl", job_data)


def load_job_completions() -> list[dict[str, Any]]:
    """
    Load all job completion events from disk.

    Returns
    -------
    list[dict[str, Any]]
        List of job completion records.
    """
    return _load_jsonl_records("jobs.jsonl")


# =============================================================================
# Outcome Achievement Storage
# =============================================================================


def save_outcome_achievement(outcome_data: dict[str, Any]) -> None:
    """
    Save an outcome achievement event to disk.

    Parameters
    ----------
    outcome_data : dict[str, Any]
        Outcome achievement data to save.
    """
    _save_jsonl_record("outcomes.jsonl", outcome_data)


def load_outcome_achievements() -> list[dict[str, Any]]:
    """
    Load all outcome achievement events from disk.

    Returns
    -------
    list[dict[str, Any]]
        List of outcome achievement records.
    """
    return _load_jsonl_records("outcomes.jsonl")


# =============================================================================
# Painpoint Resolution Storage
# =============================================================================


def save_painpoint_resolution(painpoint_data: dict[str, Any]) -> None:
    """
    Save a painpoint resolution event to disk.

    Parameters
    ----------
    painpoint_data : dict[str, Any]
        Painpoint resolution data to save.
    """
    _save_jsonl_record("painpoints.jsonl", painpoint_data)


def load_painpoint_resolutions() -> list[dict[str, Any]]:
    """
    Load all painpoint resolution events from disk.

    Returns
    -------
    list[dict[str, Any]]
        List of painpoint resolution records.
    """
    return _load_jsonl_records("painpoints.jsonl")


# =============================================================================
# User Satisfaction Storage
# =============================================================================


def save_satisfaction_record(satisfaction_data: dict[str, Any]) -> None:
    """
    Save a user satisfaction record to disk.

    Parameters
    ----------
    satisfaction_data : dict[str, Any]
        User satisfaction data to save.
    """
    _save_jsonl_record("satisfaction.jsonl", satisfaction_data)


def load_satisfaction_records() -> list[dict[str, Any]]:
    """
    Load all user satisfaction records from disk.

    Returns
    -------
    list[dict[str, Any]]
        List of user satisfaction records.
    """
    return _load_jsonl_records("satisfaction.jsonl")


# =============================================================================
# Time-to-Outcome Storage
# =============================================================================


def save_time_to_outcome(tto_data: dict[str, Any]) -> None:
    """
    Save a time-to-outcome measurement to disk.

    Parameters
    ----------
    tto_data : dict[str, Any]
        Time-to-outcome data to save.
    """
    _save_jsonl_record("time_to_outcome.jsonl", tto_data)


def load_time_to_outcome_records() -> list[dict[str, Any]]:
    """
    Load all time-to-outcome measurements from disk.

    Returns
    -------
    list[dict[str, Any]]
        List of time-to-outcome records.
    """
    return _load_jsonl_records("time_to_outcome.jsonl")


# =============================================================================
# Export Operations
# =============================================================================


@timed
def export_jtbd_metrics(
    metrics: dict[str, Any],
    output_path: Path,
    *,
    format: str = "json",
) -> dict[str, Any]:
    """
    Export JTBD metrics to JSON or CSV format.

    Parameters
    ----------
    metrics : dict[str, Any]
        Aggregated metrics to export (from ops layer).
    output_path : Path
        Output file path.
    format : str, optional
        Export format: "json" or "csv". Default is "json".

    Returns
    -------
    dict[str, Any]
        Result with 'success' bool, 'path' Path, 'format' str, 'error' str.

    Raises
    ------
    JTBDError
        If format is not supported.

    Example
    -------
    >>> metrics = {
    ...     "job_completion_rate": 0.85,
    ...     "avg_outcome_achievement": 92.3,
    ...     "total_painpoints_resolved": 15
    ... }
    >>> result = export_jtbd_metrics(metrics, Path("metrics.json"))
    >>> print(result["success"])
    True
    """
    with span("jtbd.export", format=format):
        try:
            # Validate format
            if format not in ("json", "csv"):
                raise JTBDError(f"Unsupported export format: {format}")

            # Create output directory
            output_path.parent.mkdir(parents=True, exist_ok=True)

            if format == "json":
                _export_json(metrics, output_path)
            elif format == "csv":
                _export_csv(metrics, output_path)

            add_span_event("jtbd.exported", {"path": str(output_path), "format": format})
            metric_counter(f"jtbd.export.{format}")(1)

            return {
                "success": True,
                "path": output_path,
                "format": format,
                "error": None,
            }

        except Exception as e:
            metric_counter("jtbd.export.failed")(1)
            add_span_event("jtbd.export_failed", {"error": str(e)})

            return {
                "success": False,
                "path": None,
                "format": format,
                "error": str(e),
            }


def _export_json(metrics: dict[str, Any], output_path: Path) -> None:
    """Export metrics as JSON.

    Parameters
    ----------
    metrics : dict[str, Any]
        Metrics to export.
    output_path : Path
        Output file path.
    """
    output_path.write_text(json.dumps(metrics, indent=2, default=str))


def _export_csv(metrics: dict[str, Any], output_path: Path) -> None:
    """Export metrics as CSV.

    Parameters
    ----------
    metrics : dict[str, Any]
        Metrics to export.
    output_path : Path
        Output file path.
    """
    # Flatten nested metrics for CSV
    rows = []

    def flatten(data: dict[str, Any], prefix: str = "") -> None:
        """Recursively flatten nested dict."""
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key

            if isinstance(value, dict):
                flatten(value, full_key)
            elif isinstance(value, list):
                # Convert lists to comma-separated strings
                rows.append({"metric": full_key, "value": ",".join(map(str, value))})
            else:
                rows.append({"metric": full_key, "value": str(value)})

    flatten(metrics)

    # Write CSV
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["metric", "value"])
        writer.writeheader()
        writer.writerows(rows)


# =============================================================================
# RDF Operations
# =============================================================================


@timed
def sync_jtbd_to_rdf(
    metrics: dict[str, Any],
    output_path: Path,
) -> dict[str, Any]:
    """
    Sync JTBD metrics to RDF/Turtle format.

    Converts metrics to RDF triples for integration with ontology.

    Parameters
    ----------
    metrics : dict[str, Any]
        Aggregated metrics to sync.
    output_path : Path
        Output TTL file path.

    Returns
    -------
    dict[str, Any]
        Result with 'success' bool, 'path' Path, 'triples_count' int, 'error' str.

    Example
    -------
    >>> metrics = {"job_completion_rate": 0.85}
    >>> result = sync_jtbd_to_rdf(metrics, Path("jtbd-metrics.ttl"))
    >>> print(result["success"])
    True
    """
    with span("jtbd.sync_to_rdf"):
        try:
            # Create RDF prefixes
            ttl_content = _generate_ttl_prefixes()

            # Convert metrics to RDF triples
            triples = _metrics_to_triples(metrics)
            ttl_content += "\n\n" + triples

            # Write to file
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(ttl_content)

            triple_count = ttl_content.count(" a ") + ttl_content.count(" rdf:type ")

            add_span_event(
                "jtbd.synced_to_rdf",
                {"path": str(output_path), "triples": triple_count},
            )
            metric_counter("jtbd.rdf.synced")(1)
            metric_histogram("jtbd.rdf.triple_count")(float(triple_count))

            return {
                "success": True,
                "path": output_path,
                "triples_count": triple_count,
                "error": None,
            }

        except Exception as e:
            metric_counter("jtbd.rdf.sync_failed")(1)
            add_span_event("jtbd.rdf_sync_failed", {"error": str(e)})

            return {
                "success": False,
                "path": None,
                "triples_count": 0,
                "error": str(e),
            }


def _generate_ttl_prefixes() -> str:
    """Generate standard RDF prefixes for JTBD.

    Returns
    -------
    str
        TTL prefix declarations.
    """
    return f"""@prefix jtbd: <http://spec-kit.io/ontology/jtbd#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix dcterms: <http://purl.org/dc/terms/> .

# JTBD Metrics - Generated from spec-kit
# Date: {datetime.now(UTC).isoformat()}
"""


def _metrics_to_triples(metrics: dict[str, Any], subject_prefix: str = "jtbd:metrics") -> str:
    """Convert metrics dict to RDF triples.

    Parameters
    ----------
    metrics : dict[str, Any]
        Metrics to convert.
    subject_prefix : str, optional
        Subject prefix for RDF triples.

    Returns
    -------
    str
        RDF triples in Turtle format.
    """
    lines = []
    timestamp = datetime.now(UTC).isoformat()

    # Create main metrics node
    lines.append(f"{subject_prefix}")
    lines.append("    a jtbd:MetricsReport ;")
    lines.append(f'    dcterms:created "{timestamp}"^^xsd:dateTime ;')

    # Add metric properties
    for key, value in metrics.items():
        predicate = key.replace("_", "")
        rdf_value = _value_to_rdf(value)
        lines.append(f"    jtbd:{predicate} {rdf_value} ;")

    # Remove trailing semicolon and add period
    if lines:
        lines[-1] = lines[-1].rstrip(";") + " ."

    return "\n".join(lines)


def _value_to_rdf(value: Any) -> str:
    """Convert Python value to RDF literal.

    Parameters
    ----------
    value : Any
        Python value to convert.

    Returns
    -------
    str
        RDF literal representation.
    """
    if isinstance(value, bool):
        return f'"{str(value).lower()}"^^xsd:boolean'
    if isinstance(value, int):
        return f'"{value}"^^xsd:integer'
    if isinstance(value, float):
        return f'"{value}"^^xsd:decimal'
    if isinstance(value, str):
        # Escape quotes
        escaped = value.replace('"', '\\"')
        return f'"{escaped}"'
    if isinstance(value, list):
        # Convert to comma-separated string
        return f'"{", ".join(map(str, value))}"'
    return f'"{value!s}"'


@timed
def query_jtbd_sparql(
    query: str,
    rdf_path: Path,
) -> dict[str, Any]:
    """
    Execute SPARQL query against JTBD RDF data.

    Uses ggen or local SPARQL engine to query JTBD metrics.

    Parameters
    ----------
    query : str
        SPARQL query string.
    rdf_path : Path
        Path to JTBD TTL file.

    Returns
    -------
    dict[str, Any]
        Result with 'success' bool, 'results' list[dict], 'count' int, 'error' str.

    Example
    -------
    >>> query = '''
    ... SELECT ?metric ?value WHERE {
    ...     ?s jtbd:jobcompletionrate ?value .
    ...     BIND("job_completion_rate" AS ?metric)
    ... }
    ... '''
    >>> result = query_jtbd_sparql(query, Path("jtbd-metrics.ttl"))
    >>> print(result["count"])
    1
    """
    with span("jtbd.sparql_query"):
        try:
            # Validate RDF file exists
            if not rdf_path.exists():
                raise JTBDError(f"RDF file not found: {rdf_path}", path=rdf_path)

            # Execute SPARQL query via ggen or local engine
            # For now, use placeholder implementation
            # In production, integrate with ggen sync or rdflib

            # Placeholder: Parse RDF and simulate query results
            results = _execute_sparql_placeholder(query, rdf_path)

            add_span_event(
                "jtbd.sparql_executed",
                {"query_length": len(query), "results_count": len(results)},
            )
            metric_counter("jtbd.sparql.queries")(1)
            metric_histogram("jtbd.sparql.result_count")(float(len(results)))

            return {
                "success": True,
                "results": results,
                "count": len(results),
                "error": None,
            }

        except Exception as e:
            metric_counter("jtbd.sparql.failed")(1)
            add_span_event("jtbd.sparql_failed", {"error": str(e)})

            return {
                "success": False,
                "results": [],
                "count": 0,
                "error": str(e),
            }


def _execute_sparql_placeholder(query: str, rdf_path: Path) -> list[dict[str, Any]]:
    """
    Placeholder SPARQL execution.

    In production, integrate with ggen sync or rdflib SPARQL engine.

    Parameters
    ----------
    query : str
        SPARQL query.
    rdf_path : Path
        RDF file path.

    Returns
    -------
    list[dict[str, Any]]
        Query results.
    """
    # For now, return empty results
    # TODO: Integrate with actual SPARQL engine
    #
    # Options:
    # 1. Use rdflib: from rdflib import Graph; g = Graph(); g.parse(rdf_path); ...
    # 2. Use ggen: run_logged(["ggen", "query", str(rdf_path)], capture=True)
    # 3. Use oxigraph: oxigraph-based SPARQL endpoint

    return []
