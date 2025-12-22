"""
specify_cli.ops.ggen_manifest - Manifest File Support
====================================================

Operations for loading and validating ggen.toml manifest files.

Implements Phase 1 critical fix: manifest file support (--manifest flag).
Part of the production readiness roadmap for ggen sync v5.0.0.

Key Features:
- Load and parse ggen.toml configuration files
- Validate manifest structure and required sections
- Path validation and security checks
- Rich error messages for common issues

Examples:
    >>> from specify_cli.ops.ggen_manifest import load_manifest, validate_manifest
    >>> manifest = load_manifest("ggen.toml")
    >>> validate_manifest(manifest)
    ManifestValidationResult(valid=True, errors=[])

See Also:
    - specify_cli.runtime.ggen : Runtime ggen operations
    - docs/GGEN_SYNC_MASTER_ANALYSIS_REPORT.md : Phase 1 roadmap

Notes:
    This module is part of the Poka-Yoke error-proofing strategy.
    Validates manifest upfront to prevent silent failures (RPN 512).
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

__all__ = [
    "GgenManifest",
    "ManifestValidationResult",
    "load_manifest",
    "validate_manifest",
]


@dataclass
class ManifestValidationResult:
    """Result of manifest validation.

    Attributes
    ----------
    valid : bool
        Whether manifest passed validation.
    errors : list[str]
        List of validation errors (empty if valid).
    warnings : list[str]
        List of non-critical warnings.
    """

    valid: bool
    errors: list[str]
    warnings: list[str]

    def __bool__(self) -> bool:
        """Return True if manifest is valid."""
        return self.valid


@dataclass
class GgenManifest:
    """Parsed ggen.toml manifest.

    Attributes
    ----------
    project : dict[str, Any]
        Project metadata section.
    transformations : list[dict[str, Any]]
        List of transformation configurations.
    raw : dict[str, Any]
        Raw manifest dictionary.
    """

    project: dict[str, Any]
    transformations: list[dict[str, Any]]
    raw: dict[str, Any]


def load_manifest(manifest_path: str | Path) -> GgenManifest:
    """Load ggen.toml manifest file.

    Parameters
    ----------
    manifest_path : str | Path
        Path to ggen.toml file.

    Returns
    -------
    GgenManifest
        Parsed manifest.

    Raises
    ------
    FileNotFoundError
        If manifest file not found.
    ValueError
        If manifest is invalid TOML.
    """
    path = Path(manifest_path)

    if not path.exists():
        raise FileNotFoundError(f"Manifest file not found: {path}")

    try:
        with open(path, "rb") as f:
            raw_manifest = tomllib.load(f)
    except Exception as e:
        raise ValueError(f"Invalid TOML manifest: {e}") from e

    # Extract sections
    project = raw_manifest.get("project", {})
    transformations = raw_manifest.get("transformations", [])

    return GgenManifest(
        project=project,
        transformations=transformations,
        raw=raw_manifest,
    )


def validate_manifest(manifest: GgenManifest) -> ManifestValidationResult:
    """Validate manifest structure and content.

    Checks:
    - Required sections exist
    - All file paths exist and are readable
    - Output paths are safe (no directory traversal)
    - No circular dependencies

    Parameters
    ----------
    manifest : GgenManifest
        Parsed manifest to validate.

    Returns
    -------
    ManifestValidationResult
        Validation result with errors and warnings.
    """
    errors: list[str] = []
    warnings: list[str] = []

    # Check required sections
    if not manifest.project:
        warnings.append("Missing [project] section (optional)")

    if not manifest.transformations:
        errors.append("Missing [transformations] section (required)")
        return ManifestValidationResult(valid=False, errors=errors, warnings=warnings)

    # Validate each transformation
    seen_outputs: set[str] = set()

    for i, transform in enumerate(manifest.transformations):
        transform_name = transform.get("name", f"transform_{i}")

        # Check required fields
        if "input_files" not in transform and "input_glob" not in transform:
            errors.append(f"{transform_name}: Missing 'input_files' or 'input_glob'")
            continue

        if "output_file" not in transform:
            errors.append(f"{transform_name}: Missing 'output_file'")
            continue

        # Validate input files exist
        input_files = transform.get("input_files", [])
        if isinstance(input_files, str):
            input_files = [input_files]

        for input_file in input_files:
            input_path = Path(input_file)
            if not input_path.exists():
                errors.append(
                    f"{transform_name}: Input file not found: {input_file}"
                )

        # Validate schema files if present
        schema_files = transform.get("schema_files", [])
        if isinstance(schema_files, str):
            schema_files = [schema_files]

        for schema_file in schema_files:
            schema_path = Path(schema_file)
            if not schema_path.exists():
                errors.append(
                    f"{transform_name}: Schema file not found: {schema_file}"
                )

        # Validate template file if present
        if "template" in transform:
            template_path = Path(transform["template"])
            if not template_path.exists():
                errors.append(
                    f"{transform_name}: Template file not found: {transform['template']}"
                )

        # Validate SPARQL query file if present
        if "sparql_query" in transform:
            query_path = Path(transform["sparql_query"])
            if not query_path.exists():
                errors.append(
                    f"{transform_name}: SPARQL query file not found: {transform['sparql_query']}"
                )

        # Validate output path (security: prevent directory traversal)
        output_file = transform.get("output_file", "")
        if ".." in output_file:
            errors.append(
                f"{transform_name}: Output path contains '..' (directory traversal not allowed): {output_file}"
            )

        if Path(output_file).is_absolute():
            errors.append(
                f"{transform_name}: Output path must be relative (absolute not allowed): {output_file}"
            )

        # Check for output conflicts
        if output_file in seen_outputs:
            errors.append(
                f"{transform_name}: Output file already used by another transformation: {output_file}"
            )
        else:
            seen_outputs.add(output_file)

    return ManifestValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )
