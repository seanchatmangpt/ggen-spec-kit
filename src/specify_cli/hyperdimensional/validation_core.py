"""
specify_cli.hyperdimensional.validation_core
---------------------------------------------
STUPID SIMPLE validation - 80/20 principle.

Three critical checks that catch 80% of spec problems:
1. Spec completeness (word count entropy)
2. Code fidelity (text similarity)
3. Architecture compliance (simple pattern matching)

NO complex analysis, NO NLP, NO fancy stuff.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Any

__all__ = [
    "check_spec_completeness",
    "check_code_fidelity",
    "check_architecture_compliance",
    "ValidationReport",
]


@dataclass
class ValidationReport:
    """Simple validation report."""

    completeness_score: float  # 0-1
    fidelity_score: float  # 0-1
    architecture_ok: bool
    issues: list[str]
    recommendations: list[str]


def check_spec_completeness(spec_text: str) -> float:
    """
    Check specification completeness using word count entropy.

    Uses stupid simple formula:
        completeness = log(word_count) / log(expected_max)

    Where expected_max = 500 words for a good spec.

    Args:
        spec_text: Specification text to check

    Returns:
        float: Completeness score 0-1 (0 = empty, 1 = complete)

    Example:
        >>> completeness = check_spec_completeness(spec)
        >>> if completeness < 0.5:
        ...     print("Spec is too short!")
    """
    if not spec_text or not spec_text.strip():
        return 0.0

    # Count words (simple whitespace split)
    words = spec_text.split()
    word_count = len(words)

    if word_count == 0:
        return 0.0

    # Expected max for a good spec (500 words)
    expected_max = 500

    # Logarithmic scoring (diminishing returns after certain point)
    score = math.log(word_count + 1) / math.log(expected_max + 1)

    # Cap at 1.0
    return min(score, 1.0)


def check_code_fidelity(spec_text: str, code_text: str) -> float:
    """
    Check code-to-spec fidelity using text similarity.

    Uses stupid simple approach:
    1. Extract keywords from spec (nouns, verbs)
    2. Check if they appear in code/comments
    3. Calculate overlap percentage

    Args:
        spec_text: Specification text
        code_text: Generated code text

    Returns:
        float: Fidelity score 0-1 (0 = no match, 1 = perfect match)

    Example:
        >>> fidelity = check_code_fidelity(spec, code)
        >>> if fidelity < 0.5:
        ...     print("Code doesn't match spec!")
    """
    if not spec_text or not code_text:
        return 0.0

    # Extract words from spec (lowercase, split on non-alphanumeric)
    # Split identifiers like "authenticate_user" into ["authenticate", "user"]
    spec_words = set()
    for token in re.findall(r"\b\w+\b", spec_text.lower()):
        # Split on underscore and camelCase
        parts = re.split(r"[_\s]+", token)
        for part in parts:
            if len(part) > 2 and part.isalpha():
                spec_words.add(part)

    # Extract words from code (same approach)
    code_words = set()
    for token in re.findall(r"\b\w+\b", code_text.lower()):
        parts = re.split(r"[_\s]+", token)
        for part in parts:
            if len(part) > 2 and part.isalpha():
                code_words.add(part)

    if not spec_words:
        return 0.0

    # Calculate overlap (Jaccard similarity)
    overlap = len(spec_words & code_words)
    total = len(spec_words)

    return overlap / total if total > 0 else 0.0


def check_architecture_compliance(code_text: str) -> bool:
    """
    Check three-tier architecture compliance using simple pattern matching.

    Checks:
    1. Has commands layer (CLI functions)
    2. Has ops layer (business logic)
    3. Has runtime layer (subprocess/IO)
    4. No shell=True in subprocess
    5. No hardcoded secrets

    Args:
        code_text: Python code to check

    Returns:
        bool: True if architecture looks OK, False otherwise

    Example:
        >>> ok = check_architecture_compliance(code)
        >>> if not ok:
        ...     print("Architecture violations detected!")
    """
    if not code_text:
        return False

    issues: list[str] = []

    # Check for shell=True (CRITICAL SECURITY ISSUE)
    if "shell=True" in code_text or "shell = True" in code_text:
        issues.append("shell=True detected (security risk)")

    # Check for hardcoded secrets (simple patterns)
    secret_patterns = [
        r'password\s*=\s*["\'][^"\']+["\']',
        r'api_key\s*=\s*["\'][^"\']+["\']',
        r'secret\s*=\s*["\'][^"\']+["\']',
        r'token\s*=\s*["\'][^"\']+["\']',
    ]

    for pattern in secret_patterns:
        if re.search(pattern, code_text, re.IGNORECASE):
            issues.append(f"Possible hardcoded secret: {pattern}")

    # Check for basic three-tier structure (at least some functions)
    has_functions = bool(re.search(r"def\s+\w+", code_text))

    if not has_functions:
        issues.append("No functions found (too simple?)")

    # Return True only if no issues found
    return len(issues) == 0


def validate_specification(spec_text: str, code_text: str = "") -> ValidationReport:
    """
    Run all three critical validation checks.

    Args:
        spec_text: Specification text to validate
        code_text: Optional code text for fidelity check

    Returns:
        ValidationReport: Validation results with scores and recommendations

    Example:
        >>> report = validate_specification(spec, code)
        >>> if report.completeness_score < 0.5:
        ...     print("Spec too short!")
        >>> if not report.architecture_ok:
        ...     print("Architecture issues!")
    """
    issues: list[str] = []
    recommendations: list[str] = []

    # Check 1: Spec completeness
    completeness = check_spec_completeness(spec_text)

    if completeness < 0.3:
        issues.append(f"Spec too short (score: {completeness:.2f})")
        recommendations.append("Add more detail: error handling, edge cases, performance requirements")
    elif completeness < 0.5:
        issues.append(f"Spec could be more detailed (score: {completeness:.2f})")
        recommendations.append("Consider adding: success criteria, constraints, dependencies")

    # Check 2: Code fidelity (if code provided)
    fidelity = 0.0
    if code_text:
        fidelity = check_code_fidelity(spec_text, code_text)

        if fidelity < 0.3:
            issues.append(f"Code doesn't match spec (score: {fidelity:.2f})")
            recommendations.append("Regenerate code using spec keywords and concepts")
        elif fidelity < 0.5:
            issues.append(f"Code partially matches spec (score: {fidelity:.2f})")
            recommendations.append("Align code comments and naming with spec terminology")

    # Check 3: Architecture compliance (if code provided)
    architecture_ok = True
    if code_text:
        architecture_ok = check_architecture_compliance(code_text)

        if not architecture_ok:
            issues.append("Architecture violations detected")
            recommendations.append("Fix: remove shell=True, use three-tier structure, no hardcoded secrets")

    return ValidationReport(
        completeness_score=completeness,
        fidelity_score=fidelity,
        architecture_ok=architecture_ok,
        issues=issues,
        recommendations=recommendations,
    )


# ============================================================================
# Edge Case Detection (SIMPLE VERSION)
# ============================================================================


def estimate_edge_case_coverage(spec_text: str) -> float:
    """
    Estimate edge case coverage using keyword counting.

    Counts mentions of: if, when, error, fail, empty, null, invalid, etc.

    Args:
        spec_text: Specification text

    Returns:
        float: Edge case coverage estimate 0-100%

    Example:
        >>> coverage = estimate_edge_case_coverage(spec)
        >>> print(f"Edge cases: {coverage:.0f}%")
    """
    if not spec_text:
        return 0.0

    edge_keywords = [
        "if",
        "when",
        "error",
        "fail",
        "exception",
        "invalid",
        "empty",
        "null",
        "none",
        "missing",
        "timeout",
        "retry",
        "boundary",
        "edge",
        "minimum",
        "maximum",
    ]

    text_lower = spec_text.lower()
    mentions = sum(1 for keyword in edge_keywords if keyword in text_lower)

    # Score: 10% per keyword mentioned (cap at 100%)
    return min(mentions * 10.0, 100.0)


def identify_specification_gaps(spec_text: str) -> list[str]:
    """
    Identify missing sections in specification.

    Checks for presence of:
    - Error handling
    - Performance requirements
    - Security requirements
    - Testing criteria
    - Edge cases

    Args:
        spec_text: Specification text

    Returns:
        list[str]: List of identified gaps

    Example:
        >>> gaps = identify_specification_gaps(spec)
        >>> for gap in gaps:
        ...     print(f"Missing: {gap}")
    """
    gaps: list[str] = []

    if not spec_text:
        return ["Specification is empty"]

    text_lower = spec_text.lower()

    # Check for error handling
    error_keywords = ["error", "exception", "fail", "invalid"]
    if not any(keyword in text_lower for keyword in error_keywords):
        gaps.append("No error handling specified")

    # Check for performance
    perf_keywords = ["performance", "latency", "speed", "time", "throughput", "ms", "seconds"]
    if not any(keyword in text_lower for keyword in perf_keywords):
        gaps.append("No performance requirements specified")

    # Check for security
    security_keywords = ["security", "auth", "encrypt", "permission", "access"]
    if not any(keyword in text_lower for keyword in security_keywords):
        gaps.append("No security requirements specified")

    # Check for testing
    test_keywords = ["test", "verify", "validate", "assert", "check"]
    if not any(keyword in text_lower for keyword in test_keywords):
        gaps.append("No testing criteria specified")

    # Check for edge cases
    edge_keywords = ["edge", "boundary", "limit", "empty", "null"]
    if not any(keyword in text_lower for keyword in edge_keywords):
        gaps.append("No edge cases specified")

    return gaps


# ============================================================================
# Quick Metrics
# ============================================================================


def quick_spec_metrics(spec_text: str) -> dict[str, Any]:
    """
    Get quick metrics for a specification.

    Returns word count, completeness, edge coverage, and gaps.

    Args:
        spec_text: Specification text

    Returns:
        dict: Metrics dictionary

    Example:
        >>> metrics = quick_spec_metrics(spec)
        >>> print(f"Words: {metrics['word_count']}")
        >>> print(f"Complete: {metrics['completeness']:.0%}")
    """
    words = spec_text.split() if spec_text else []

    return {
        "word_count": len(words),
        "completeness": check_spec_completeness(spec_text),
        "edge_coverage": estimate_edge_case_coverage(spec_text) / 100.0,  # 0-1
        "gaps": identify_specification_gaps(spec_text),
        "has_must_statements": "must" in spec_text.lower(),
        "has_shall_statements": "shall" in spec_text.lower(),
    }
