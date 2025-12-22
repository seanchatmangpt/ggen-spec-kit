"""
specify_cli.ops.ggen_errors - Comprehensive Error Messages
========================================================

Error message formatting and clarity.

Implements Phase 1 critical fix: comprehensive error messages to make
errors obvious and actionable (Poka-Yoke feedback dimension).

Key Features:
- Structured error messages with context
- Suggested next steps for each error type
- Color-coded severity levels
- Error categorization for debugging

Examples:
    >>> from specify_cli.ops.ggen_errors import format_error
    >>> msg = format_error(
    ...     \"input_not_found\",
    ...     {\"file\": \"ontology/spec.ttl\", \"reason\": \"File deleted\"}
    ... )
    >>> print(msg)

See Also:
    - specify_cli.ops.ggen_recovery : Recovery procedures
    - specify_cli.core.shell : Output formatting
    - docs/GGEN_SYNC_POKA_YOKE.md : Error-proofing design

Notes:
    Part of Poka-Yoke feedback layer. Makes errors obvious with
    clear suggestions for resolution.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

__all__ = [
    "ErrorType",
    "format_error_message",
    "format_warning_message",
]


class ErrorType(Enum):
    """Error type enumeration."""

    MANIFEST_NOT_FOUND = "manifest_not_found"
    MANIFEST_INVALID = "manifest_invalid"
    INPUT_FILE_NOT_FOUND = "input_file_not_found"
    OUTPUT_PERMISSION_DENIED = "output_permission_denied"
    OUTPUT_DISK_FULL = "output_disk_full"
    SPARQL_TIMEOUT = "sparql_timeout"
    SPARQL_SYNTAX_ERROR = "sparql_syntax_error"
    RDF_INVALID = "rdf_invalid"
    TEMPLATE_NOT_FOUND = "template_not_found"
    SCHEMA_INVALID = "schema_invalid"
    PATH_TRAVERSAL = "path_traversal"
    LOCK_TIMEOUT = "lock_timeout"
    UNKNOWN = "unknown"


ERROR_MESSAGES = {
    ErrorType.MANIFEST_NOT_FOUND: {
        "title": "Manifest File Not Found",
        "description": "The ggen.toml configuration file was not found.",
        "context_keys": ["file", "cwd"],
        "suggestions": [
            "Make sure ggen.toml exists in the current directory",
            "Use --manifest flag to specify a custom path",
            "Create a new manifest: ggen init ggen.toml",
        ],
    },
    ErrorType.MANIFEST_INVALID: {
        "title": "Invalid Manifest Configuration",
        "description": "The ggen.toml file has syntax errors or invalid configuration.",
        "context_keys": ["error", "line"],
        "suggestions": [
            "Check TOML syntax (brackets, quotes, etc.)",
            "Validate with: ggen validate ggen.toml",
            "Verify all file paths exist",
        ],
    },
    ErrorType.INPUT_FILE_NOT_FOUND: {
        "title": "Input File Not Found",
        "description": "Required input file for transformation is missing.",
        "context_keys": ["file", "transformation"],
        "suggestions": [
            "Check that the file path in ggen.toml is correct",
            "Verify the file actually exists: ls -la {file}",
            "Check file permissions: stat {file}",
        ],
    },
    ErrorType.OUTPUT_PERMISSION_DENIED: {
        "title": "Output Directory Not Writable",
        "description": "Cannot write to output directory (permission denied).",
        "context_keys": ["directory", "user"],
        "suggestions": [
            "Check directory permissions: ls -ld {directory}",
            "Grant write access: chmod u+w {directory}",
            "Verify owner: chown $USER {directory}",
            "Try different output directory",
        ],
    },
    ErrorType.OUTPUT_DISK_FULL: {
        "title": "Disk Space Exhausted",
        "description": "Cannot write output - disk is full or nearly full.",
        "context_keys": ["directory", "available_mb"],
        "suggestions": [
            "Check disk usage: df -h {directory}",
            "Free up space on the filesystem",
            "Use different output directory on different disk",
            "Reduce size of input files if possible",
        ],
    },
    ErrorType.SPARQL_TIMEOUT: {
        "title": "SPARQL Query Timeout",
        "description": "SPARQL query took too long and was interrupted.",
        "context_keys": ["timeout_seconds", "query_file"],
        "suggestions": [
            "Simplify the SPARQL query if possible",
            "Break into multiple smaller queries",
            "Increase timeout in configuration",
            "Reduce input dataset size",
            "Review query for performance issues: EXPLAIN {query_file}",
        ],
    },
    ErrorType.SPARQL_SYNTAX_ERROR: {
        "title": "SPARQL Syntax Error",
        "description": "SPARQL query has syntax errors.",
        "context_keys": ["error", "query_file", "line"],
        "suggestions": [
            "Review SPARQL syntax at {query_file}:{line}",
            "Check SPARQL grammar reference",
            "Use SPARQL validator: ggen validate {query_file}",
            "Test query in SPARQL playground",
        ],
    },
    ErrorType.RDF_INVALID: {
        "title": "Invalid RDF/Turtle Data",
        "description": "RDF input is not valid Turtle format.",
        "context_keys": ["file", "error", "line"],
        "suggestions": [
            "Check Turtle syntax at {file}:{line}",
            "Validate RDF: rdflib validate {file}",
            "Check prefix declarations are valid",
            "Verify encoding is UTF-8",
        ],
    },
    ErrorType.TEMPLATE_NOT_FOUND: {
        "title": "Template File Not Found",
        "description": "Tera template file is missing.",
        "context_keys": ["file", "transformation"],
        "suggestions": [
            "Verify template path in ggen.toml: {file}",
            "Check file exists: ls -la {file}",
            "Check file is readable: stat {file}",
        ],
    },
    ErrorType.SCHEMA_INVALID: {
        "title": "Invalid Schema/SHACL Shapes",
        "description": "SHACL schema is invalid or malformed.",
        "context_keys": ["file", "error"],
        "suggestions": [
            "Check SHACL syntax at {file}",
            "Validate shapes: ggen validate {file}",
            "Review SHACL specification",
            "Test with simpler shapes first",
        ],
    },
    ErrorType.PATH_TRAVERSAL: {
        "title": "Invalid Path (Security Check)",
        "description": "Output path contains directory traversal (..) or is absolute.",
        "context_keys": ["path"],
        "suggestions": [
            "Use only relative paths in output_file",
            "Remove '..' sequences from path",
            "Use canonical paths without /",
            "Review path in ggen.toml: {path}",
        ],
    },
    ErrorType.LOCK_TIMEOUT: {
        "title": "Another ggen sync Is Running",
        "description": "Could not acquire lock - another process is syncing.",
        "context_keys": ["owner_pid", "timeout_seconds"],
        "suggestions": [
            "Wait for other ggen sync to complete (PID {owner_pid})",
            "Check if process is stuck: ps -p {owner_pid}",
            "Kill stuck process if needed: kill {owner_pid}",
            "Remove lock file: rm -f .ggen.lock",
        ],
    },
}


def format_error_message(
    error_type: ErrorType | str,
    context: dict[str, Any] | None = None,
    include_suggestions: bool = True,
) -> str:
    """Format comprehensive error message.

    Parameters
    ----------
    error_type : ErrorType | str
        Type of error.
    context : dict[str, Any] | None
        Context variables for message formatting.
    include_suggestions : bool
        Whether to include suggested next steps.

    Returns
    -------
    str
        Formatted error message.
    """
    if isinstance(error_type, str):
        try:
            error_type = ErrorType(error_type)
        except ValueError:
            error_type = ErrorType.UNKNOWN

    context = context or {}

    # Get error template
    if error_type not in ERROR_MESSAGES:
        return f"Error: {error_type.value}"

    template = ERROR_MESSAGES[error_type]

    # Build message
    lines = [
        f"[red bold]{template['title']}[/red bold]",
        f"{template['description']}",
        "",
    ]

    # Add context
    if context:
        lines.append("[dim]Context:[/dim]")
        for key, value in context.items():
            if key in template.get("context_keys", []):
                lines.append(f"  {key}: {value}")

    # Add suggestions
    if include_suggestions:
        lines.append("")
        lines.append("[yellow]Suggested Next Steps:[/yellow]")
        for i, suggestion in enumerate(template["suggestions"], 1):
            # Format suggestion with context variables
            formatted = suggestion
            for key, value in context.items():
                formatted = formatted.replace(f"{{{key}}}", str(value))
            lines.append(f"  {i}. {formatted}")

    return "\n".join(lines)


def format_warning_message(
    message: str,
    context: dict[str, Any] | None = None,
) -> str:
    """Format warning message.

    Parameters
    ----------
    message : str
        Warning message.
    context : dict[str, Any] | None
        Context variables.

    Returns
    -------
    str
        Formatted warning message.
    """
    context = context or {}

    # Format message with context
    formatted = message
    for key, value in context.items():
        formatted = formatted.replace(f"{{{key}}}", str(value))

    return f"[yellow]Warning:[/yellow] {formatted}"
