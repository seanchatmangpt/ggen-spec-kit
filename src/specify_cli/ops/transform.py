"""
specify_cli.ops.transform - Specification Transformation Operations
===================================================================

Pure business logic for the constitutional equation: spec.md = μ(feature.ttl)

The μ transformation consists of 5 stages:
- μ₁ NORMALIZE: Load RDF, validate SHACL shapes
- μ₂ EXTRACT: Execute SPARQL queries
- μ₃ EMIT: Render Tera templates
- μ₄ CANONICALIZE: Format output (line endings, whitespace)
- μ₅ RECEIPT: Generate SHA256 proof

This module contains PURE FUNCTIONS - all I/O is in the runtime layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class StageResult:
    """Result of a single μ stage.

    Parameters
    ----------
    stage : str
        Stage name: "normalize", "extract", "emit", "canonicalize", "receipt"
    success : bool
        Whether stage completed successfully
    input_hash : str
        SHA256 hash of stage input
    output_hash : str
        SHA256 hash of stage output
    output : str | None
        Intermediate output for debugging
    errors : list[str]
        Error messages from this stage
    """

    stage: str
    success: bool
    input_hash: str
    output_hash: str
    output: str | None
    errors: list[str]


@dataclass
class TransformResult:
    """Result of a μ transformation.

    Parameters
    ----------
    success : bool
        Whether entire transformation succeeded
    input_file : str
        Path to input RDF file
    output_file : str
        Path to output file (Markdown or Python)
    input_hash : str
        SHA256 hash of input
    output_hash : str
        SHA256 hash of output (the "receipt")
    stage_results : dict[str, StageResult]
        Results from each μ stage
    errors : list[str]
        All errors across stages
    warnings : list[str]
        Non-fatal warnings
    """

    success: bool
    input_file: str
    output_file: str
    input_hash: str
    output_hash: str
    stage_results: dict[str, StageResult]
    errors: list[str]
    warnings: list[str] = field(default_factory=list)


@dataclass
class TransformConfig:
    """Configuration for a transformation.

    Parameters
    ----------
    name : str
        Transformation name
    description : str
        Human-readable description
    input_files : list[str]
        Input RDF/Turtle files
    schema_files : list[str]
        SHACL shape files for validation
    sparql_query : str
        Path to SPARQL query file
    template : str
        Path to Tera template file
    output_file : str
        Path to output file
    deterministic : bool
        Whether to enforce deterministic output
    """

    name: str
    description: str
    input_files: list[str]
    schema_files: list[str]
    sparql_query: str
    template: str
    output_file: str
    deterministic: bool = True


def validate_transform_config(config: dict[str, Any]) -> TransformConfig:
    """Validate transformation configuration from ggen.toml.

    Parameters
    ----------
    config : dict[str, Any]
        Raw configuration from TOML

    Returns
    -------
    TransformConfig
        Validated configuration

    Raises
    ------
    ValueError
        If configuration is invalid or missing required fields
    """
    required = ["name", "input_files", "sparql_query", "template", "output_file"]
    missing = [field for field in required if field not in config]

    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

    # Validate input_files is non-empty list
    if not isinstance(config["input_files"], list) or not config["input_files"]:
        raise ValueError("input_files must be a non-empty list")

    return TransformConfig(
        name=config["name"],
        description=config.get("description", ""),
        input_files=config["input_files"],
        schema_files=config.get("schema_files", []),
        sparql_query=config["sparql_query"],
        template=config["template"],
        output_file=config["output_file"],
        deterministic=config.get("deterministic", True),
    )


def normalize_rdf(rdf_content: str, shacl_shapes: str | None = None) -> StageResult:
    """μ₁ NORMALIZE: Validate RDF against SHACL shapes.

    This is pure validation metadata - runtime layer does actual parsing.

    Parameters
    ----------
    rdf_content : str
        Raw RDF/Turtle content
    shacl_shapes : str, optional
        SHACL shapes for validation

    Returns
    -------
    StageResult
        Validation result with any constraint violations
    """
    errors = []

    # Basic validation (runtime does actual RDF parsing)
    if not rdf_content.strip():
        errors.append("Empty RDF content")

    # Check for basic Turtle syntax markers
    if "@prefix" not in rdf_content and "@base" not in rdf_content:
        if not rdf_content.strip().startswith("<"):
            errors.append("No @prefix or @base declarations found")

    return StageResult(
        stage="normalize",
        success=len(errors) == 0,
        input_hash="",  # Set by runtime
        output_hash="",  # Set by runtime
        output=rdf_content,  # Normalized RDF
        errors=errors,
    )


def extract_data(
    normalized_rdf: str,
    sparql_query: str,
) -> StageResult:
    """μ₂ EXTRACT: Execute SPARQL query against RDF.

    Pure transformation metadata - runtime executes actual SPARQL.

    Parameters
    ----------
    normalized_rdf : str
        Normalized RDF from μ₁
    sparql_query : str
        SPARQL query to execute

    Returns
    -------
    StageResult
        Query results metadata (JSON results set by runtime)
    """
    errors = []

    # Basic validation
    if not sparql_query.strip():
        errors.append("Empty SPARQL query")

    # Check for SELECT/CONSTRUCT/ASK
    query_upper = sparql_query.upper()
    if not any(kw in query_upper for kw in ["SELECT", "CONSTRUCT", "ASK", "DESCRIBE"]):
        errors.append("Invalid SPARQL query: missing SELECT/CONSTRUCT/ASK/DESCRIBE")

    return StageResult(
        stage="extract",
        success=len(errors) == 0,
        input_hash="",
        output_hash="",
        output=None,  # JSON results set by runtime
        errors=errors,
    )


def emit_template(
    extracted_data: dict[str, Any],
    template: str,
) -> StageResult:
    """μ₃ EMIT: Render Tera template with extracted data.

    Pure transformation metadata - runtime does actual rendering.

    Parameters
    ----------
    extracted_data : dict[str, Any]
        JSON data from μ₂
    template : str
        Tera template content

    Returns
    -------
    StageResult
        Rendering metadata (content set by runtime)
    """
    errors = []

    # Basic validation
    if not template.strip():
        errors.append("Empty template")

    # Check for basic Tera syntax
    if "{{" not in template and "{%" not in template:
        errors.append("Template appears to have no Tera syntax")

    return StageResult(
        stage="emit",
        success=len(errors) == 0,
        input_hash="",
        output_hash="",
        output=None,  # Rendered content set by runtime
        errors=errors,
    )


def canonicalize_output(content: str) -> StageResult:
    """μ₄ CANONICALIZE: Normalize output format.

    - Convert line endings to LF
    - Trim trailing whitespace
    - Ensure final newline

    Parameters
    ----------
    content : str
        Raw output from μ₃

    Returns
    -------
    StageResult
        Canonicalized content
    """
    # Normalize line endings
    normalized = content.replace("\r\n", "\n").replace("\r", "\n")

    # Trim trailing whitespace per line
    lines = [line.rstrip() for line in normalized.split("\n")]
    trimmed = "\n".join(lines)

    # Ensure exactly one final newline
    canonical = trimmed.rstrip() + "\n" if trimmed else ""

    return StageResult(
        stage="canonicalize",
        success=True,
        input_hash="",
        output_hash="",
        output=canonical,
        errors=[],
    )


def generate_receipt(content: str, input_hash: str) -> StageResult:
    """μ₅ RECEIPT: Generate SHA256 proof of transformation.

    This creates cryptographic proof of the transformation chain.

    Parameters
    ----------
    content : str
        Canonicalized content from μ₄
    input_hash : str
        SHA256 hash of original input

    Returns
    -------
    StageResult
        Receipt with output hash
    """
    import hashlib

    output_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

    return StageResult(
        stage="receipt",
        success=True,
        input_hash=input_hash,
        output_hash=output_hash,
        output=content,
        errors=[],
    )


def compose_transform(
    config: TransformConfig,
    stage_results: dict[str, StageResult],
) -> TransformResult:
    """Compose μ₁ through μ₅ into complete transformation.

    Implements: output = μ₅(μ₄(μ₃(μ₂(μ₁(input)))))

    Parameters
    ----------
    config : TransformConfig
        Transformation configuration
    stage_results : dict[str, StageResult]
        Results from each μ stage

    Returns
    -------
    TransformResult
        Complete transformation result
    """
    all_success = all(r.success for r in stage_results.values())
    all_errors = []
    for r in stage_results.values():
        all_errors.extend(r.errors)

    # Get hashes from first and last stages
    first_stage = stage_results.get("normalize", StageResult("", False, "", "", None, []))
    last_stage = stage_results.get(
        "receipt",
        stage_results.get("canonicalize", StageResult("", False, "", "", None, [])),
    )

    return TransformResult(
        success=all_success,
        input_file=config.input_files[0] if config.input_files else "",
        output_file=config.output_file,
        input_hash=first_stage.input_hash,
        output_hash=last_stage.output_hash,
        stage_results=stage_results,
        errors=all_errors,
        warnings=[],
    )


def validate_stage_sequence(stages: list[str]) -> list[str]:
    """Validate that stages are in correct μ₁→μ₂→μ₃→μ₄→μ₅ order.

    Parameters
    ----------
    stages : list[str]
        Stage names to validate

    Returns
    -------
    list[str]
        Error messages (empty if valid)
    """
    expected_order = ["normalize", "extract", "emit", "canonicalize", "receipt"]
    errors = []

    # Check all stages are valid
    invalid = [s for s in stages if s not in expected_order]
    if invalid:
        errors.append(f"Invalid stages: {', '.join(invalid)}")

    # Check order
    stage_indices = {s: i for i, s in enumerate(expected_order)}
    for i in range(len(stages) - 1):
        current_idx = stage_indices[stages[i]]
        next_idx = stage_indices[stages[i + 1]]
        if next_idx <= current_idx:
            errors.append(f"Stages out of order: {stages[i]} must come before {stages[i + 1]}")

    return errors
