"""
specify_cli.ops.ggen_validation - Output Syntax Validation
==========================================================

Output validation for generated files (Phase 2 quality).

Validates generated Markdown, JSON, Python, and JavaScript output
to catch transformation errors early.

Key Features:
- Markdown syntax validation
- JSON schema validation
- Python syntax checking
- JavaScript syntax checking
- Clear error messages with line numbers

Examples:
    >>> from specify_cli.ops.ggen_validation import validate_markdown
    >>> result = validate_markdown(\"docs/output.md\")
    >>> if not result.valid:
    ...     print(f\"Validation failed: {result.errors}\")

See Also:
    - specify_cli.ops.ggen_manifest : Manifest validation
    - docs/GGEN_SYNC_OPERATIONAL_RUNBOOKS.md : Quality procedures

Notes:
    Catches common transformation errors (invalid JSON, broken links, etc).
"""

from __future__ import annotations

import ast
import json
import re
from dataclasses import dataclass
from pathlib import Path

__all__ = [
    "ValidationResult",
    "validate_javascript",
    "validate_json",
    "validate_markdown",
    "validate_python",
]


@dataclass
class ValidationResult:
    """Result of output validation.

    Attributes
    ----------
    valid : bool
        Whether output passed validation.
    errors : list[str]
        List of validation errors.
    warnings : list[str]
        List of non-critical warnings.
    """

    valid: bool
    errors: list[str]
    warnings: list[str]

    def __bool__(self) -> bool:
        """Return True if valid."""
        return self.valid


def validate_markdown(file_path: str | Path) -> ValidationResult:
    """Validate Markdown syntax.

    Parameters
    ----------
    file_path : str | Path
        Path to Markdown file.

    Returns
    -------
    ValidationResult
        Validation result.
    """
    path = Path(file_path)
    errors: list[str] = []
    warnings: list[str] = []

    if not path.exists():
        return ValidationResult(valid=False, errors=[f"File not found: {path}"], warnings=[])

    try:
        content = path.read_text(encoding="utf-8")

        # Check for common Markdown issues
        lines = content.split("\n")

        # Check for unclosed code blocks
        code_block_count = content.count("```")
        if code_block_count % 2 != 0:
            errors.append("Unclosed code block (odd number of ```)")

        # Check for broken links
        link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"
        for i, line in enumerate(lines, 1):
            matches = re.findall(link_pattern, line)
            for _text, url in matches:
                if url.startswith(("#", "http://", "https://", "/")):
                    continue
                # Check if relative link exists
                link_path = path.parent / url
                if not link_path.exists():
                    warnings.append(f"Line {i}: Broken link: {url}")

        # Check for duplicate headings
        heading_pattern = r"^#+\s+(.+)$"
        headings = []
        for i, line in enumerate(lines, 1):
            match = re.match(heading_pattern, line)
            if match:
                heading = match.group(1)
                if heading in headings:
                    warnings.append(f"Line {i}: Duplicate heading: {heading}")
                headings.append(heading)

    except Exception as e:
        errors.append(f"Markdown validation error: {e}")

    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )


def validate_json(file_path: str | Path) -> ValidationResult:
    """Validate JSON syntax.

    Parameters
    ----------
    file_path : str | Path
        Path to JSON file.

    Returns
    -------
    ValidationResult
        Validation result.
    """
    path = Path(file_path)
    errors: list[str] = []
    warnings: list[str] = []

    if not path.exists():
        return ValidationResult(valid=False, errors=[f"File not found: {path}"], warnings=[])

    try:
        content = path.read_text(encoding="utf-8")
        json.loads(content)

        # Check size
        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > 10:
            warnings.append(f"Large JSON file: {size_mb:.1f}MB")

    except json.JSONDecodeError as e:
        errors.append(f"JSON parse error: {e.msg} at line {e.lineno}, column {e.colno}")
    except Exception as e:
        errors.append(f"JSON validation error: {e}")

    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )


def validate_python(file_path: str | Path) -> ValidationResult:
    """Validate Python syntax.

    Parameters
    ----------
    file_path : str | Path
        Path to Python file.

    Returns
    -------
    ValidationResult
        Validation result.
    """
    path = Path(file_path)
    errors: list[str] = []
    warnings: list[str] = []

    if not path.exists():
        return ValidationResult(valid=False, errors=[f"File not found: {path}"], warnings=[])

    try:
        content = path.read_text(encoding="utf-8")
        ast.parse(content)

        # Check for common Python issues
        if "import *" in content:
            warnings.append("Uses 'import *' (wildcard imports)")

    except SyntaxError as e:
        errors.append(f"Python syntax error at line {e.lineno}: {e.msg}")
    except Exception as e:
        errors.append(f"Python validation error: {e}")

    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )


def validate_javascript(file_path: str | Path) -> ValidationResult:
    """Validate JavaScript syntax (basic).

    Parameters
    ----------
    file_path : str | Path
        Path to JavaScript file.

    Returns
    -------
    ValidationResult
        Validation result.
    """
    path = Path(file_path)
    errors: list[str] = []
    warnings: list[str] = []

    if not path.exists():
        return ValidationResult(valid=False, errors=[f"File not found: {path}"], warnings=[])

    try:
        content = path.read_text(encoding="utf-8")

        # Check for balanced braces/parentheses
        if content.count("{") != content.count("}"):
            errors.append("Unbalanced curly braces")

        if content.count("[") != content.count("]"):
            errors.append("Unbalanced square brackets")

        if content.count("(") != content.count(")"):
            errors.append("Unbalanced parentheses")

        # Check for unterminated strings
        single_quotes = content.count("'") - content.count("\\'")
        double_quotes = content.count('"') - content.count('\\"')

        if single_quotes % 2 != 0:
            errors.append("Unterminated single-quoted string")

        if double_quotes % 2 != 0:
            errors.append("Unterminated double-quoted string")

    except Exception as e:
        errors.append(f"JavaScript validation error: {e}")

    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )
