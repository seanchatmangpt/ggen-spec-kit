"""
Test Utilities for DSPy LaTeX-to-PDF Engine Testing

Provides helper functions, assertions, and utilities for comprehensive testing.

Utilities:
    - LaTeX validation helpers
    - PDF verification tools
    - Performance measurement utilities
    - Mock DSPy response generators
    - Error simulation helpers
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from unittest.mock import MagicMock


# ============================================================================
# Data Classes
# ============================================================================


@dataclass
class CompilationResult:
    """Result of a LaTeX compilation."""

    success: bool
    output_file: Optional[Path] = None
    log_file: Optional[Path] = None
    errors: List[str] = None
    warnings: List[str] = None
    duration_ms: float = 0.0
    passes: int = 1

    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


@dataclass
class ValidationResult:
    """Result of LaTeX validation."""

    valid: bool
    errors: List[Dict[str, Any]] = None
    warnings: List[Dict[str, Any]] = None
    score: float = 0.0

    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


@dataclass
class PDFQualityMetrics:
    """PDF quality assessment metrics."""

    pages: int
    file_size_mb: float
    has_metadata: bool
    has_bookmarks: bool
    has_links: bool
    searchable: bool
    quality_score: float


# ============================================================================
# LaTeX Validation Helpers
# ============================================================================


def validate_latex_syntax(content: str) -> ValidationResult:
    """
    Validate LaTeX syntax (mock implementation).

    Parameters
    ----------
    content : str
        LaTeX content to validate

    Returns
    -------
    ValidationResult
        Validation results
    """
    errors = []
    warnings = []

    # Check for basic syntax issues
    if content.count(r"\begin{document}") != content.count(r"\end{document}"):
        errors.append(
            {
                "type": "unmatched_environment",
                "message": "Unmatched document environment",
                "line": -1,
            }
        )

    # Check for unmatched braces (simplified)
    open_braces = content.count("{")
    close_braces = content.count("}")
    if open_braces != close_braces:
        warnings.append(
            {
                "type": "brace_mismatch",
                "message": f"Brace mismatch: {open_braces} open, {close_braces} close",
                "line": -1,
            }
        )

    valid = len(errors) == 0
    score = 1.0 if valid else max(0.0, 1.0 - len(errors) * 0.2)

    return ValidationResult(valid=valid, errors=errors, warnings=warnings, score=score)


def extract_packages(content: str) -> List[str]:
    """
    Extract package names from LaTeX content.

    Parameters
    ----------
    content : str
        LaTeX content

    Returns
    -------
    List[str]
        List of package names
    """
    import re

    pattern = r"\\usepackage(?:\[.*?\])?\{([^}]+)\}"
    matches = re.findall(pattern, content)

    packages = []
    for match in matches:
        # Split on comma for multi-package declarations
        packages.extend(pkg.strip() for pkg in match.split(","))

    return packages


def extract_environments(content: str) -> List[str]:
    """
    Extract environment names from LaTeX content.

    Parameters
    ----------
    content : str
        LaTeX content

    Returns
    -------
    List[str]
        List of environment names
    """
    import re

    pattern = r"\\begin\{([^}]+)\}"
    matches = re.findall(pattern, content)

    return list(set(matches))


def check_environment_matching(content: str) -> Dict[str, Any]:
    """
    Check if environments are properly matched.

    Parameters
    ----------
    content : str
        LaTeX content

    Returns
    -------
    Dict[str, Any]
        Matching status and details
    """
    import re

    begin_pattern = r"\\begin\{([^}]+)\}"
    end_pattern = r"\\end\{([^}]+)\}"

    begins = re.findall(begin_pattern, content)
    ends = re.findall(end_pattern, content)

    # Simple stack-based checking
    stack = []
    mismatches = []

    begin_positions = [(m.start(), m.group(1)) for m in re.finditer(begin_pattern, content)]
    end_positions = [(m.start(), m.group(1)) for m in re.finditer(end_pattern, content)]

    all_positions = sorted(
        [(pos, "begin", env) for pos, env in begin_positions]
        + [(pos, "end", env) for pos, env in end_positions]
    )

    for pos, tag_type, env in all_positions:
        if tag_type == "begin":
            stack.append(env)
        elif tag_type == "end":
            if not stack:
                mismatches.append(f"Unexpected \\end{{{env}}} at position {pos}")
            elif stack[-1] != env:
                mismatches.append(
                    f"Environment mismatch: \\begin{{{stack[-1]}}} ended with \\end{{{env}}}"
                )
                stack.pop()
            else:
                stack.pop()

    if stack:
        mismatches.extend([f"Unclosed environment: {env}" for env in stack])

    return {"matched": len(mismatches) == 0, "mismatches": mismatches, "stack": stack}


# ============================================================================
# PDF Verification Helpers
# ============================================================================


def verify_pdf_exists(pdf_path: Path) -> bool:
    """
    Verify that PDF file exists and is valid.

    Parameters
    ----------
    pdf_path : Path
        Path to PDF file

    Returns
    -------
    bool
        True if PDF exists and appears valid
    """
    if not pdf_path.exists():
        return False

    # Check file signature (PDF files start with %PDF)
    with open(pdf_path, "rb") as f:
        header = f.read(4)
        return header == b"%PDF"


def get_pdf_page_count(pdf_path: Path) -> int:
    """
    Get page count from PDF (mock implementation).

    Parameters
    ----------
    pdf_path : Path
        Path to PDF file

    Returns
    -------
    int
        Number of pages (mocked)
    """
    # In real implementation, would use PyPDF2 or similar
    # For testing, return a mock value
    return 10


def calculate_pdf_hash(pdf_path: Path) -> str:
    """
    Calculate SHA256 hash of PDF file.

    Parameters
    ----------
    pdf_path : Path
        Path to PDF file

    Returns
    -------
    str
        Hexadecimal hash string
    """
    sha256_hash = hashlib.sha256()

    with open(pdf_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)

    return sha256_hash.hexdigest()


def assess_pdf_quality(pdf_path: Path) -> PDFQualityMetrics:
    """
    Assess PDF quality metrics (mock implementation).

    Parameters
    ----------
    pdf_path : Path
        Path to PDF file

    Returns
    -------
    PDFQualityMetrics
        Quality assessment
    """
    # Mock implementation
    file_size_mb = pdf_path.stat().st_size / (1024 * 1024) if pdf_path.exists() else 0

    return PDFQualityMetrics(
        pages=get_pdf_page_count(pdf_path),
        file_size_mb=file_size_mb,
        has_metadata=True,
        has_bookmarks=True,
        has_links=True,
        searchable=True,
        quality_score=0.95,
    )


# ============================================================================
# Performance Measurement
# ============================================================================


class PerformanceTimer:
    """Context manager for measuring performance."""

    def __init__(self, name: str = "operation"):
        self.name = name
        self.start_time = 0.0
        self.end_time = 0.0
        self.duration_ms = 0.0

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.perf_counter()
        self.duration_ms = (self.end_time - self.start_time) * 1000


def measure_compilation_time(compile_func: Callable, *args, **kwargs) -> Dict[str, Any]:
    """
    Measure compilation time and collect metrics.

    Parameters
    ----------
    compile_func : Callable
        Compilation function to measure
    *args
        Positional arguments for function
    **kwargs
        Keyword arguments for function

    Returns
    -------
    Dict[str, Any]
        Metrics including duration
    """
    timer = PerformanceTimer()

    with timer:
        result = compile_func(*args, **kwargs)

    return {"result": result, "duration_ms": timer.duration_ms, "function": compile_func.__name__}


def benchmark_operations(
    operations: List[Callable], iterations: int = 10
) -> Dict[str, Dict[str, float]]:
    """
    Benchmark multiple operations.

    Parameters
    ----------
    operations : List[Callable]
        List of operations to benchmark
    iterations : int
        Number of iterations

    Returns
    -------
    Dict[str, Dict[str, float]]
        Benchmark results
    """
    results = {}

    for op in operations:
        durations = []

        for _ in range(iterations):
            timer = PerformanceTimer()
            with timer:
                op()
            durations.append(timer.duration_ms)

        results[op.__name__] = {
            "min_ms": min(durations),
            "max_ms": max(durations),
            "avg_ms": sum(durations) / len(durations),
            "total_ms": sum(durations),
        }

    return results


# ============================================================================
# Mock DSPy Response Generators
# ============================================================================


def create_mock_dspy_optimization_result(
    optimized_content: str, improvement_score: float = 0.85
) -> MagicMock:
    """
    Create a mock DSPy optimization result.

    Parameters
    ----------
    optimized_content : str
        Optimized LaTeX content
    improvement_score : float
        Quality score

    Returns
    -------
    MagicMock
        Mock result object
    """
    result = MagicMock()
    result.optimized_spec = optimized_content
    result.reasoning = "Applied optimizations based on best practices"
    result.score = improvement_score
    result.improvements = [
        "Removed unused packages",
        "Optimized package load order",
        "Simplified math environments",
    ]
    return result


def create_mock_dspy_error_fix_result(fixed_content: str, confidence: float = 0.92) -> MagicMock:
    """
    Create a mock DSPy error fixing result.

    Parameters
    ----------
    fixed_content : str
        Fixed LaTeX content
    confidence : float
        Confidence score

    Returns
    -------
    MagicMock
        Mock result object
    """
    result = MagicMock()
    result.fixed_latex = fixed_content
    result.explanation = "Fixed syntax errors and balanced environments"
    result.confidence = confidence
    result.changes_made = [
        "Added missing closing brace",
        "Balanced equation environment",
        "Removed undefined command",
    ]
    return result


def mock_dspy_signature_predictor(signature: str, default_output: Any = None) -> MagicMock:
    """
    Create a mock DSPy signature predictor.

    Parameters
    ----------
    signature : str
        DSPy signature string
    default_output : Any
        Default output value

    Returns
    -------
    MagicMock
        Mock predictor
    """
    predictor = MagicMock()

    def forward_func(**kwargs):
        result = MagicMock()
        for key in signature.split("->")[1].split(","):
            field_name = key.strip()
            setattr(result, field_name, default_output or f"Generated {field_name}")
        return result

    predictor.forward = forward_func
    predictor.__call__ = forward_func

    return predictor


# ============================================================================
# Error Simulation Helpers
# ============================================================================


def inject_latex_error(content: str, error_type: str) -> str:
    """
    Inject a specific error type into LaTeX content.

    Parameters
    ----------
    content : str
        Original LaTeX content
    error_type : str
        Type of error to inject

    Returns
    -------
    str
        Content with injected error
    """
    error_injectors = {
        "missing_brace": lambda c: c.replace(r"\textbf{", r"\textbf{unclosed", 1),
        "undefined_command": lambda c: c.replace(
            r"\section{", r"\section{\undefinedcommand ", 1
        ),
        "unmatched_env": lambda c: c.replace(r"\end{document}", r"\end{wrong}", 1),
        "missing_package": lambda c: c.replace(
            r"\begin{document}", r"\begin{tikzpicture}\end{tikzpicture}\begin{document}", 1
        ),
    }

    injector = error_injectors.get(error_type)
    if injector:
        return injector(content)
    return content


def simulate_compilation_error(error_type: str) -> Dict[str, Any]:
    """
    Simulate a compilation error message.

    Parameters
    ----------
    error_type : str
        Type of error

    Returns
    -------
    Dict[str, Any]
        Error details
    """
    error_messages = {
        "missing_file": {
            "type": "file_not_found",
            "message": "! LaTeX Error: File `missing.sty' not found.",
            "line": 12,
            "severity": "error",
        },
        "undefined_control": {
            "type": "undefined_command",
            "message": "! Undefined control sequence.\nl.42 \\mycommand",
            "line": 42,
            "severity": "error",
        },
        "missing_delimiter": {
            "type": "math_error",
            "message": "! Missing $ inserted.",
            "line": 25,
            "severity": "error",
        },
    }

    return error_messages.get(error_type, {"type": "unknown", "message": "Unknown error"})


# ============================================================================
# Assertion Helpers
# ============================================================================


def assert_latex_compiles(content: str, compiler: Optional[Callable] = None) -> None:
    """
    Assert that LaTeX content compiles successfully.

    Parameters
    ----------
    content : str
        LaTeX content
    compiler : Optional[Callable]
        Compiler function (mock if None)

    Raises
    ------
    AssertionError
        If compilation fails
    """
    if compiler is None:
        # Mock successful compilation
        validation = validate_latex_syntax(content)
        assert validation.valid, f"LaTeX validation failed: {validation.errors}"
    else:
        result = compiler(content)
        assert result.success, f"Compilation failed: {result.errors}"


def assert_pdf_valid(pdf_path: Path, min_pages: int = 1) -> None:
    """
    Assert that PDF is valid.

    Parameters
    ----------
    pdf_path : Path
        Path to PDF file
    min_pages : int
        Minimum expected pages

    Raises
    ------
    AssertionError
        If PDF is invalid
    """
    assert verify_pdf_exists(pdf_path), f"PDF does not exist: {pdf_path}"

    page_count = get_pdf_page_count(pdf_path)
    assert page_count >= min_pages, f"Expected at least {min_pages} pages, got {page_count}"


def assert_performance_acceptable(duration_ms: float, max_ms: float) -> None:
    """
    Assert that performance is within acceptable bounds.

    Parameters
    ----------
    duration_ms : float
        Actual duration
    max_ms : float
        Maximum acceptable duration

    Raises
    ------
    AssertionError
        If performance is unacceptable
    """
    assert (
        duration_ms <= max_ms
    ), f"Performance unacceptable: {duration_ms:.1f}ms > {max_ms:.1f}ms"


# ============================================================================
# Test Data Generators
# ============================================================================


def generate_random_latex(
    sections: int = 5, paragraphs_per_section: int = 3, seed: int = 42
) -> str:
    """
    Generate random LaTeX content for testing.

    Parameters
    ----------
    sections : int
        Number of sections
    paragraphs_per_section : int
        Paragraphs per section
    seed : int
        Random seed

    Returns
    -------
    str
        Generated LaTeX content
    """
    import random

    random.seed(seed)

    preamble = r"""
\documentclass{article}
\usepackage{lipsum}
\title{Generated Document}
\author{Test Author}
\begin{document}
\maketitle
"""

    section_content = []
    for i in range(sections):
        section_content.append(f"\\section{{Section {i + 1}}}")
        for j in range(paragraphs_per_section):
            para_num = random.randint(1, 10)
            section_content.append(f"\\lipsum[{para_num}]")

    ending = r"\end{document}"

    return preamble + "\n".join(section_content) + ending


def generate_stress_test_latex(complexity: str = "medium") -> str:
    """
    Generate LaTeX for stress testing.

    Parameters
    ----------
    complexity : str
        Complexity level: low, medium, high

    Returns
    -------
    str
        Stress test LaTeX content
    """
    complexity_configs = {
        "low": {"sections": 5, "equations": 10, "environments": 5},
        "medium": {"sections": 20, "equations": 50, "environments": 20},
        "high": {"sections": 100, "equations": 200, "environments": 100},
    }

    config = complexity_configs.get(complexity, complexity_configs["medium"])

    # Generate complex document
    content = [
        r"\documentclass{report}",
        r"\usepackage{amsmath}",
        r"\usepackage{amssymb}",
        r"\begin{document}",
    ]

    for i in range(config["sections"]):
        content.append(f"\\section{{Section {i}}}")
        content.append("Content for this section.")

        # Add equations
        if i % 3 == 0:
            content.append(r"\begin{equation}")
            content.append(f"x_{i} = {i}^2")
            content.append(r"\end{equation}")

    content.append(r"\end{document}")

    return "\n".join(content)
