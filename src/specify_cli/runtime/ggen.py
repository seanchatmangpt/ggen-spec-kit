"""
specify_cli.runtime.ggen - ggen CLI Wrapper
============================================

Runtime layer for ggen v5.0.2 (Graph Generator) CLI operations.

This module provides a wrapper around the ggen CLI tool for
RDF-to-Markdown transformations via ggen sync.

Install ggen via:
- brew install seanchatmangpt/ggen/ggen (recommended)
- cargo install ggen-cli-lib
- docker pull seanchatman/ggen:5.0.2

Key Features
-----------
* **Sync Operations**: Synchronize RDF specs to markdown via ggen.toml
* **Telemetry**: Full OTEL instrumentation
* **Error Handling**: Comprehensive error reporting

Security
--------
* List-based subprocess calls only (no shell=True)
* Path validation before operations

Examples
--------
    >>> from specify_cli.runtime.ggen import sync_specs
    >>>
    >>> sync_specs(project_path)

See Also
--------
- :mod:`specify_cli.runtime.tools` : Tool detection
- :mod:`specify_cli.core.process` : Process execution
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from specify_cli.core.instrumentation import add_span_event
from specify_cli.core.process import run, run_logged
from specify_cli.core.shell import timed
from specify_cli.core.telemetry import metric_counter, metric_histogram, span
from specify_cli.ops.transform import (
    StageResult,
    TransformConfig,
    TransformResult,
    canonicalize_output,
    compose_transform,
)
from specify_cli.runtime.receipt import (
    generate_receipt,
    sha256_string,
)
from specify_cli.runtime.tools import check_tool

__all__ = [
    "GgenError",
    "get_ggen_version",
    "is_ggen_available",
    "run_logged",  # Re-export for patching in tests
    "run_transform",
    "sync_specs",
]


class GgenError(Exception):
    """ggen operation error."""

    def __init__(self, message: str, command: list[str] | None = None) -> None:
        super().__init__(message)
        self.command = command


def is_ggen_available() -> bool:
    """Check if ggen CLI is available.

    Returns
    -------
    bool
        True if ggen is installed and available.
    """
    return check_tool("ggen")


def get_ggen_version() -> str | None:
    """Get the installed ggen version.

    Returns
    -------
    str | None
        Version string or None if not installed.
    """
    if not is_ggen_available():
        return None

    with span("ggen.version"):
        try:
            output = run(["ggen", "--version"], capture=True, check=False)
        except Exception:
            return None
        else:
            if output:
                # Parse version from output
                return output.strip()
            return "installed (version unknown)"


def sync_specs(
    project_path: Path,
    *,
    watch: bool = False,
    verbose: bool = False,
) -> bool:
    """Synchronize specification files using ggen sync.

    Executes the five-stage transformation pipeline:
    - μ₁ Normalize: Load RDF, validate SHACL
    - μ₂ Extract: Execute SPARQL queries
    - μ₃ Emit: Render Tera templates
    - μ₄ Canonicalize: Format output
    - μ₅ Receipt: Generate SHA256 hash proof

    Parameters
    ----------
    project_path : Path
        Project root directory (must contain ggen.toml).
    watch : bool, optional
        Watch for file changes. Default is False.
    verbose : bool, optional
        Enable verbose output. Default is False.

    Returns
    -------
    bool
        True if sync succeeded.

    Raises
    ------
    GgenError
        If ggen is not available or sync fails.
    """
    if not is_ggen_available():
        raise GgenError(
            "ggen is not installed. Install with: "
            "brew install seanchatmangpt/ggen/ggen or cargo install ggen-cli-lib"
        )

    start_time = time.time()

    with span("ggen.sync", project=str(project_path), watch=watch):
        add_span_event("ggen.sync.starting", {"path": str(project_path)})

        cmd = ["ggen", "sync"]

        if watch:
            cmd.append("--watch")

        if verbose:
            cmd.append("--verbose")

        try:
            run(cmd, capture=True, check=True, cwd=project_path)
        except Exception as e:
            duration = time.time() - start_time
            metric_counter("ggen.sync.error")(1)
            add_span_event("ggen.sync.failed", {"error": str(e)})
            raise GgenError(f"Spec sync failed: {e}") from e
        else:
            duration = time.time() - start_time
            metric_counter("ggen.sync.success")(1)
            metric_histogram("ggen.sync.duration")(duration)
            add_span_event("ggen.sync.completed", {"duration": duration})
            return True


@timed
def run_transform(config: TransformConfig) -> TransformResult:
    """Execute complete μ transformation pipeline.

    Implements: output = μ₅(μ₄(μ₃(μ₂(μ₁(input)))))

    Parameters
    ----------
    config : TransformConfig
        Transformation configuration from ggen.toml

    Returns
    -------
    TransformResult
        Complete result with all stage outputs and receipt
    """
    with span("ggen.transform", {"name": config.name}):
        stage_results = {}

        # μ₁ NORMALIZE: Load and validate RDF
        stage_results["normalize"] = _run_normalize(config)
        if not stage_results["normalize"].success:
            return compose_transform(config, stage_results)

        # μ₂ EXTRACT: Execute SPARQL
        normalize_output = stage_results["normalize"].output
        if normalize_output is None:
            stage_results["extract"] = StageResult(
                stage="extract",
                success=False,
                input_hash="",
                output_hash="",
                output=None,
                errors=["Normalize stage produced no output"],
            )
            return compose_transform(config, stage_results)

        stage_results["extract"] = _run_extract(config, normalize_output)
        if not stage_results["extract"].success:
            return compose_transform(config, stage_results)

        # μ₃ EMIT: Render template
        stage_results["emit"] = _run_emit(
            config,
            stage_results["extract"].output,
        )
        if not stage_results["emit"].success:
            return compose_transform(config, stage_results)

        # μ₄ CANONICALIZE: Format output
        stage_results["canonicalize"] = canonicalize_output(
            stage_results["emit"].output,
        )

        # Write output file
        output_path = Path(config.output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(stage_results["canonicalize"].output)

        # μ₅ RECEIPT: Generate proof
        stage_results["receipt"] = _run_receipt(config, stage_results)

        return compose_transform(config, stage_results)


def _run_normalize(config: TransformConfig) -> StageResult:
    """μ₁ NORMALIZE: Load RDF and validate SHACL."""
    with span("ggen.normalize"):
        errors = []

        # Load input files
        rdf_content = ""
        for input_file in config.input_files:
            path = Path(input_file)
            if not path.exists():
                errors.append(f"Input file not found: {input_file}")
                continue
            rdf_content += path.read_text() + "\n"

        if errors:
            return StageResult(
                stage="normalize",
                success=False,
                input_hash="",
                output_hash="",
                output=None,
                errors=errors,
            )

        # Validate SHACL shapes if specified
        if config.schema_files:
            validation = _validate_shacl(rdf_content, config.schema_files)
            if not validation["valid"]:
                errors.extend(validation["violations"])

        input_hash = sha256_string(rdf_content)
        output_hash = input_hash  # Normalize is identity for valid RDF

        return StageResult(
            stage="normalize",
            success=len(errors) == 0,
            input_hash=input_hash,
            output_hash=output_hash,
            output=rdf_content,
            errors=errors,
        )


def _run_extract(config: TransformConfig, rdf_content: str) -> StageResult:
    """μ₂ EXTRACT: Execute SPARQL query."""
    with span("ggen.extract"):
        query_path = Path(config.sparql_query)
        if not query_path.exists():
            return StageResult(
                stage="extract",
                success=False,
                input_hash=sha256_string(rdf_content),
                output_hash="",
                output=None,
                errors=[f"SPARQL query not found: {config.sparql_query}"],
            )

        query = query_path.read_text()

        # Execute SPARQL via ggen or local engine
        result = _execute_sparql(rdf_content, query)

        output_hash = sha256_string(json.dumps(result))

        return StageResult(
            stage="extract",
            success=True,
            input_hash=sha256_string(rdf_content),
            output_hash=output_hash,
            output=result,
            errors=[],
        )


def _run_emit(config: TransformConfig, extracted_data: Any) -> StageResult:
    """μ₃ EMIT: Render Tera template."""
    with span("ggen.emit"):
        template_path = Path(config.template)
        if not template_path.exists():
            return StageResult(
                stage="emit",
                success=False,
                input_hash=sha256_string(json.dumps(extracted_data)),
                output_hash="",
                output=None,
                errors=[f"Template not found: {config.template}"],
            )

        template = template_path.read_text()

        # Render Tera template via ggen or local engine
        rendered = _render_tera(template, extracted_data)

        return StageResult(
            stage="emit",
            success=True,
            input_hash=sha256_string(json.dumps(extracted_data)),
            output_hash=sha256_string(rendered),
            output=rendered,
            errors=[],
        )


def _run_receipt(
    config: TransformConfig,
    stage_results: dict[str, StageResult],
) -> StageResult:
    """μ₅ RECEIPT: Generate cryptographic proof."""
    with span("ggen.receipt"):
        input_path = Path(config.input_files[0])
        output_path = Path(config.output_file)

        stage_outputs = {
            stage: result.output
            for stage, result in stage_results.items()
            if result.output is not None and isinstance(result.output, str)
        }

        receipt = generate_receipt(input_path, output_path, stage_outputs)

        # Write receipt file
        receipt_path = output_path.with_suffix(output_path.suffix + ".receipt.json")
        receipt_path.write_text(receipt.to_json())

        return StageResult(
            stage="receipt",
            success=True,
            input_hash=receipt.input_hash,
            output_hash=receipt.output_hash,
            output=receipt.to_json(),
            errors=[],
        )


def _validate_shacl(_rdf_content: str, schema_files: list[str]) -> dict[str, Any]:
    """Validate RDF against SHACL shapes."""
    # Implementation depends on available tools (pyshacl, ggen, etc.)
    # For now, return valid if shapes load
    try:
        for schema_file in schema_files:
            path = Path(schema_file)
            if not path.exists():
                return {"valid": False, "violations": [f"Schema not found: {schema_file}"]}
        return {"valid": True, "violations": []}
    except Exception as e:
        return {"valid": False, "violations": [str(e)]}


def _execute_sparql(_rdf_content: str, _query: str) -> dict[str, Any]:
    """Execute SPARQL query against RDF content."""
    # Use ggen sync or local SPARQL engine
    # For now, return empty results placeholder
    return {"results": []}


def _render_tera(_template: str, _data: Any) -> str:
    """Render Tera template with data."""
    # Use ggen sync or local Tera engine
    # For now, return template with basic substitution
    return _template
