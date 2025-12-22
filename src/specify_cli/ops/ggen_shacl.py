"""
specify_cli.ops.ggen_shacl - SHACL Validation Layer
=================================================

SHACL shape validation for RDF data.

Implements Phase 1 critical fix: SHACL validation to prevent invalid RDF
processing (RPN 378). Validates RDF data against SHACL shapes before
SPARQL processing.

Key Features:
- Validate RDF against SHACL shapes
- Report violations with clear messages
- Graceful degradation if pyshacl unavailable
- Support for multiple shape files

Examples:
    >>> from specify_cli.ops.ggen_shacl import validate_rdf
    >>> result = validate_rdf(
    ...     rdf_files=["ontology/spec.ttl"],
    ...     shapes_files=["ontology/shapes.ttl"]
    ... )
    >>> if not result.valid:
    ...     for violation in result.violations:
    ...         print(violation)

See Also:
    - specify_cli.runtime.ggen : Runtime ggen operations
    - docs/GGEN_SYNC_POKA_YOKE.md : Error-proofing design

Notes:
    Uses pyshacl for validation if available. Gracefully degrades to
    basic RDF syntax checking if pyshacl not installed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

__all__ = [
    "SHACLValidationResult",
    "validate_rdf",
]


@dataclass
class SHACLValidationResult:
    """Result of SHACL validation.

    Attributes
    ----------
    valid : bool
        Whether RDF conforms to SHACL shapes.
    violations : list[str]
        List of violation descriptions.
    warnings : list[str]
        Non-critical warnings.
    details : dict[str, Any]
        Additional validation details.
    """

    valid: bool
    violations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)


def validate_rdf(
    rdf_files: list[str] | None = None,
    rdf_content: str | None = None,
    shapes_files: list[str] | None = None,
    shapes_content: str | None = None,
) -> SHACLValidationResult:
    """Validate RDF against SHACL shapes.

    Parameters
    ----------
    rdf_files : list[str] | None
        List of RDF files to validate.
    rdf_content : str | None
        RDF content as string (used if rdf_files not provided).
    shapes_files : list[str] | None
        List of SHACL shape files.
    shapes_content : str | None
        SHACL shapes as string (used if shapes_files not provided).

    Returns
    -------
    SHACLValidationResult
        Validation result with violations and warnings.
    """
    # If no shapes provided, cannot validate
    if not shapes_files and not shapes_content:
        return SHACLValidationResult(
            valid=True,
            warnings=["No SHACL shapes provided - skipping validation"],
            details={"skipped": True, "reason": "no_shapes"},
        )

    # Load RDF content
    if rdf_content is None:
        if not rdf_files:
            return SHACLValidationResult(
                valid=False,
                violations=["No RDF files or content provided"],
            )

        try:
            rdf_content = ""
            for file_path in rdf_files:
                path = Path(file_path)
                if not path.exists():
                    return SHACLValidationResult(
                        valid=False,
                        violations=[f"RDF file not found: {file_path}"],
                    )
                rdf_content += path.read_text() + "\n"
        except Exception as e:
            return SHACLValidationResult(
                valid=False,
                violations=[f"Error reading RDF files: {e}"],
            )

    # Load SHACL shapes content
    if shapes_content is None:
        if not shapes_files:
            return SHACLValidationResult(
                valid=True,
                warnings=["No SHACL shapes provided - skipping validation"],
                details={"skipped": True},
            )

        try:
            shapes_content = ""
            for file_path in shapes_files:
                path = Path(file_path)
                if not path.exists():
                    return SHACLValidationResult(
                        valid=False,
                        violations=[f"SHACL shape file not found: {file_path}"],
                    )
                shapes_content += path.read_text() + "\n"
        except Exception as e:
            return SHACLValidationResult(
                valid=False,
                violations=[f"Error reading SHACL shapes: {e}"],
            )

    # Try to validate with pyshacl
    try:
        from rdflib import Graph  # noqa: PLC0415

        try:
            import pyshacl  # noqa: PLC0415

            # Parse graphs
            data_graph = Graph()
            data_graph.parse(data=rdf_content, format="turtle")

            shapes_graph = Graph()
            shapes_graph.parse(data=shapes_content, format="turtle")

            # Run validation
            conforms, _, report_text = pyshacl.validate(
                data_graph,
                shacl_graph=shapes_graph,
                inference="rdfs",
                abort_on_first=False,
            )

            if conforms:
                return SHACLValidationResult(
                    valid=True,
                    details={
                        "triples": len(data_graph),
                        "validator": "pyshacl",
                    },
                )
            violations = _parse_shacl_report(report_text)
            return SHACLValidationResult(
                valid=False,
                violations=violations,
                details={
                    "triples": len(data_graph),
                    "validator": "pyshacl",
                    "report": report_text[:500],  # First 500 chars
                },
            )

        except ImportError:
            # pyshacl not available - basic RDF validation only
            data_graph = Graph()
            data_graph.parse(data=rdf_content, format="turtle")

            return SHACLValidationResult(
                valid=True,
                warnings=[
                    "pyshacl not installed - basic RDF syntax check only. "
                    "Install with: pip install pyshacl"
                ],
                details={
                    "triples": len(data_graph),
                    "validator": "basic",
                },
            )

    except Exception as e:
        return SHACLValidationResult(
            valid=False,
            violations=[f"Validation error: {e}"],
            details={"error_type": type(e).__name__},
        )


def _parse_shacl_report(report_text: str) -> list[str]:
    """Parse SHACL validation report text into violations.

    Parameters
    ----------
    report_text : str
        SHACL validation report (Turtle format).

    Returns
    -------
    list[str]
        List of violation descriptions.
    """
    violations: list[str] = []

    # Simple parsing of SHACL report
    lines = report_text.split("\n")
    for line in lines:
        if "sh:resultMessage" in line or "violation" in line.lower():
            # Extract message
            if '"' in line:
                parts = line.split('"')
                if len(parts) >= 2:
                    message = parts[1]
                    if message and message not in violations:
                        violations.append(message)

    # If no violations extracted, return generic message
    if not violations:
        violations.append("SHACL validation failed (see report for details)")

    return violations
