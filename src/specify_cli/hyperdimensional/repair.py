"""
specify_cli.hyperdimensional.repair
------------------------------------
Automated repair and improvement suggestions for specifications and code.

This module provides automated suggestions for:
- Improving specification completeness
- Enhancing code quality
- Adding missing requirements
- Refactoring recommendations

Example
-------
    from specify_cli.hyperdimensional.repair import (
        suggest_missing_requirements,
        recommend_refactoring
    )

    # Get improvement suggestions
    requirements = suggest_missing_requirements(spec)
    test_cases = recommend_edge_case_tests(spec)
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from specify_cli.core.telemetry import metric_counter, span

__all__ = [
    "RepairSuggestion",
    "propose_clarifications",
    "propose_metric_additions",
    "recommend_edge_case_tests",
    "recommend_refactoring",
    "suggest_missing_requirements",
    "suggest_simplifications",
]


@dataclass
class RepairSuggestion:
    """A suggested repair or improvement."""

    category: str  # "completeness", "quality", "clarity", etc.
    priority: str  # "high", "medium", "low"
    description: str
    rationale: str
    code_example: str = ""
    affected_section: str = ""


def suggest_missing_requirements(spec: str) -> list[RepairSuggestion]:
    """
    Suggest likely missing requirements in specification.

    Analyzes specification structure and content to identify
    commonly overlooked requirements.

    Parameters
    ----------
    spec : str
        Specification text to analyze.

    Returns
    -------
    list[RepairSuggestion]
        List of suggested missing requirements.

    Example
    -------
    >>> suggestions = suggest_missing_requirements(spec)
    >>> for s in suggestions:
    ...     print(f"{s.priority}: {s.description}")
    """
    with span("repair.suggest_requirements"):
        suggestions = []
        spec_lower = spec.lower()

        # Error handling
        if not any(word in spec_lower for word in ["error", "exception", "fail", "invalid"]):
            suggestions.append(
                RepairSuggestion(
                    category="completeness",
                    priority="high",
                    description="Add error handling requirements",
                    rationale="No error handling specifications found. System should define how to handle failures.",
                    code_example="""
# Example error handling requirement:
- System MUST return HTTP 400 for invalid input
- System MUST log all errors with severity level
- System MUST retry failed operations up to 3 times
                """.strip(),
                    affected_section="Error Handling",
                )
            )

        # Performance requirements
        if not any(
            word in spec_lower for word in ["performance", "latency", "throughput", "response"]
        ):
            suggestions.append(
                RepairSuggestion(
                    category="completeness",
                    priority="high",
                    description="Add performance requirements",
                    rationale="Performance expectations not specified. Define acceptable response times.",
                    code_example="""
# Example performance requirements:
- API responses MUST complete within 200ms (p95)
- System MUST handle 1000 requests per second
- Database queries MUST complete within 50ms (p99)
                """.strip(),
                    affected_section="Non-Functional Requirements",
                )
            )

        # Security considerations
        if not any(word in spec_lower for word in ["security", "auth", "encrypt", "permission"]):
            suggestions.append(
                RepairSuggestion(
                    category="completeness",
                    priority="high",
                    description="Add security requirements",
                    rationale="Security considerations not specified. Define authentication and authorization.",
                    code_example="""
# Example security requirements:
- All API endpoints MUST require authentication
- Sensitive data MUST be encrypted at rest
- User sessions MUST expire after 1 hour of inactivity
                """.strip(),
                    affected_section="Security",
                )
            )

        # Input validation
        if not any(word in spec_lower for word in ["validate", "validation", "sanitize", "check"]):
            suggestions.append(
                RepairSuggestion(
                    category="completeness",
                    priority="medium",
                    description="Add input validation requirements",
                    rationale="Input validation not specified. Define validation rules.",
                    code_example="""
# Example validation requirements:
- All user inputs MUST be validated against schema
- Email addresses MUST match RFC 5322 format
- Numeric inputs MUST be within specified range
                """.strip(),
                    affected_section="Input Validation",
                )
            )

        # Logging/Observability
        if not any(
            word in spec_lower for word in ["log", "trace", "monitor", "telemetry", "metric"]
        ):
            suggestions.append(
                RepairSuggestion(
                    category="completeness",
                    priority="medium",
                    description="Add observability requirements",
                    rationale="Observability not specified. Define logging and monitoring.",
                    code_example="""
# Example observability requirements:
- All operations MUST emit OpenTelemetry spans
- Critical errors MUST be logged with stack traces
- Business metrics MUST be recorded (counters, histograms)
                """.strip(),
                    affected_section="Observability",
                )
            )

        # Acceptance criteria
        if "acceptance" not in spec_lower:
            suggestions.append(
                RepairSuggestion(
                    category="completeness",
                    priority="medium",
                    description="Add acceptance criteria",
                    rationale="Acceptance criteria not defined. Specify how to verify completion.",
                    code_example="""
# Example acceptance criteria:
- Feature passes all automated tests
- Code coverage >= 80%
- Performance requirements met in load testing
- Security scan shows no critical vulnerabilities
                """.strip(),
                    affected_section="Acceptance Criteria",
                )
            )

        metric_counter("repair.requirements_suggested")(len(suggestions))
        return suggestions


def recommend_edge_case_tests(spec: str) -> list[RepairSuggestion]:
    """
    Recommend edge case tests to add based on specification.

    Analyzes specification to identify likely edge cases that
    should be tested.

    Parameters
    ----------
    spec : str
        Specification text.

    Returns
    -------
    list[RepairSuggestion]
        List of recommended test cases.

    Example
    -------
    >>> tests = recommend_edge_case_tests(spec)
    >>> for test in tests:
    ...     print(f"Test: {test.description}")
    """
    with span("repair.recommend_tests"):
        suggestions = []
        spec_lower = spec.lower()

        # String/input handling
        if any(word in spec_lower for word in ["input", "string", "text", "data"]):
            suggestions.append(
                RepairSuggestion(
                    category="testing",
                    priority="high",
                    description="Test empty/null inputs",
                    rationale="Specification mentions input handling. Test boundary conditions.",
                    code_example="""
def test_empty_input():
    result = process_input("")
    assert result.error == "Input cannot be empty"

def test_null_input():
    result = process_input(None)
    assert result.error == "Input cannot be null"
                """.strip(),
                    affected_section="Input Handling",
                )
            )

            suggestions.append(
                RepairSuggestion(
                    category="testing",
                    priority="medium",
                    description="Test very long inputs",
                    rationale="Test maximum input length handling.",
                    code_example="""
def test_max_length_input():
    long_input = "x" * 10000
    result = process_input(long_input)
    assert result.error == "Input exceeds maximum length"
                """.strip(),
                    affected_section="Input Validation",
                )
            )

        # Numeric handling
        if any(word in spec_lower for word in ["number", "count", "amount", "quantity"]):
            suggestions.append(
                RepairSuggestion(
                    category="testing",
                    priority="high",
                    description="Test boundary values",
                    rationale="Specification involves numeric values. Test min/max boundaries.",
                    code_example="""
def test_zero_value():
    result = calculate(0)
    assert result >= 0

def test_negative_value():
    result = calculate(-1)
    assert result.error == "Value must be positive"

def test_max_value():
    result = calculate(sys.maxsize)
    # Should handle gracefully
                """.strip(),
                    affected_section="Numeric Handling",
                )
            )

        # Collection handling
        if any(word in spec_lower for word in ["list", "array", "collection", "items"]):
            suggestions.append(
                RepairSuggestion(
                    category="testing",
                    priority="high",
                    description="Test empty collections",
                    rationale="Test behavior with empty lists/arrays.",
                    code_example="""
def test_empty_list():
    result = process_items([])
    assert result == []  # or appropriate default

def test_single_item():
    result = process_items([item])
    assert len(result) == 1
                """.strip(),
                    affected_section="Collection Handling",
                )
            )

        # Concurrency
        if any(word in spec_lower for word in ["concurrent", "parallel", "async", "thread"]):
            suggestions.append(
                RepairSuggestion(
                    category="testing",
                    priority="high",
                    description="Test race conditions",
                    rationale="Specification mentions concurrency. Test race conditions.",
                    code_example="""
@pytest.mark.asyncio
async def test_concurrent_access():
    tasks = [process_async() for _ in range(100)]
    results = await asyncio.gather(*tasks)
    assert len(results) == 100
    assert all(r.success for r in results)
                """.strip(),
                    affected_section="Concurrency",
                )
            )

        # Network/External dependencies
        if any(word in spec_lower for word in ["api", "http", "network", "external", "service"]):
            suggestions.append(
                RepairSuggestion(
                    category="testing",
                    priority="high",
                    description="Test network failures",
                    rationale="Test behavior when external dependencies fail.",
                    code_example="""
def test_network_timeout():
    with mock.patch('httpx.get', side_effect=TimeoutError):
        result = call_api()
        assert result.error == "Request timeout"

def test_service_unavailable():
    with mock.patch('httpx.get', return_value=Response(503)):
        result = call_api()
        assert result.error == "Service unavailable"
                """.strip(),
                    affected_section="External Dependencies",
                )
            )

        metric_counter("repair.tests_recommended")(len(suggestions))
        return suggestions


def propose_clarifications(spec: str) -> list[RepairSuggestion]:
    """
    Propose clarifications for ambiguous specification parts.

    Parameters
    ----------
    spec : str
        Specification text to analyze.

    Returns
    -------
    list[RepairSuggestion]
        List of clarification proposals.

    Example
    -------
    >>> clarifications = propose_clarifications(spec)
    >>> for c in clarifications:
    ...     print(f"Clarify: {c.description}")
    """
    with span("repair.propose_clarifications"):
        suggestions = []
        spec_lower = spec.lower()

        # Vague quantifiers
        vague_terms = {
            "some": ("Specify exact number or range", 'Replace "some" with "3-5" or "at least 1"'),
            "many": (
                'Define threshold for "many"',
                'Replace with "more than 10" or specific count',
            ),
            "few": ("Define exact number", 'Replace with "2-3" or specific count'),
            "quickly": ("Specify time constraint", 'Replace with "within 100ms" or specific time'),
            "large": ("Define size threshold", 'Replace with "> 1MB" or specific size'),
        }

        for term, (description, example) in vague_terms.items():
            if f" {term} " in f" {spec_lower} ":
                # Find the sentence containing the term
                sentences = spec.split(".")
                affected = next((s for s in sentences if term in s.lower()), "")

                suggestions.append(
                    RepairSuggestion(
                        category="clarity",
                        priority="high",
                        description=description,
                        rationale=f"Term '{term}' is ambiguous and not measurable.",
                        code_example=example,
                        affected_section=affected.strip()[:100],
                    )
                )

        # Modal verbs
        if "should" in spec_lower:
            suggestions.append(
                RepairSuggestion(
                    category="clarity",
                    priority="high",
                    description="Replace 'should' with 'must' or 'may'",
                    rationale="'Should' is ambiguous - unclear if required or optional.",
                    code_example='Use "MUST" for requirements, "MAY" for optional features',
                    affected_section="Modal Verbs",
                )
            )

        # Etc/ellipsis
        if "etc" in spec_lower or "..." in spec:
            suggestions.append(
                RepairSuggestion(
                    category="clarity",
                    priority="medium",
                    description="Complete incomplete lists",
                    rationale="'etc' or '...' indicates incomplete specification.",
                    code_example="List all items explicitly or define pattern for remaining items",
                    affected_section="Incomplete Lists",
                )
            )

        metric_counter("repair.clarifications_proposed")(len(suggestions))
        return suggestions


def suggest_simplifications(spec: str) -> list[RepairSuggestion]:
    """
    Suggest ways to simplify overly complex specifications.

    Parameters
    ----------
    spec : str
        Specification text.

    Returns
    -------
    list[RepairSuggestion]
        List of simplification suggestions.

    Example
    -------
    >>> simplifications = suggest_simplifications(spec)
    >>> for s in simplifications:
    ...     print(f"Simplify: {s.description}")
    """
    with span("repair.suggest_simplifications"):
        suggestions = []

        # Check for very long sentences
        sentences = [s.strip() for s in spec.split(".") if s.strip()]
        for sentence in sentences:
            word_count = len(sentence.split())
            if word_count > 40:
                suggestions.append(
                    RepairSuggestion(
                        category="quality",
                        priority="medium",
                        description="Break long sentence into multiple sentences",
                        rationale=f"Sentence has {word_count} words. Aim for < 30 words per sentence.",
                        code_example="Split into 2-3 shorter sentences with clear subjects.",
                        affected_section=sentence[:100] + "...",
                    )
                )

        # Check for redundant words
        redundant_patterns = [
            (r"\b(absolutely|completely|totally)\b", "Remove unnecessary intensifiers"),
            (r"\b(in order to)\b", 'Replace with "to"'),
            (r"\b(due to the fact that)\b", 'Replace with "because"'),
        ]

        for pattern, suggestion in redundant_patterns:
            if re.search(pattern, spec, re.IGNORECASE):
                suggestions.append(
                    RepairSuggestion(
                        category="quality",
                        priority="low",
                        description=suggestion,
                        rationale="Simplify language for better clarity.",
                        code_example="Use simpler, more direct language",
                        affected_section="Wordiness",
                    )
                )

        metric_counter("repair.simplifications_suggested")(len(suggestions))
        return suggestions


def recommend_refactoring(code: str) -> list[RepairSuggestion]:
    """
    Recommend code refactoring improvements.

    Parameters
    ----------
    code : str
        Python code to analyze.

    Returns
    -------
    list[RepairSuggestion]
        List of refactoring recommendations.

    Example
    -------
    >>> refactorings = recommend_refactoring(code)
    >>> for r in refactorings:
    ...     print(f"Refactor: {r.description}")
    """
    with span("repair.recommend_refactoring"):
        suggestions = []

        # Check for long functions
        func_pattern = r"def\s+(\w+)\s*\([^)]*\):"
        funcs = re.finditer(func_pattern, code)

        for match in funcs:
            func_name = match.group(1)
            func_start = match.end()

            # Find function end (next def or end of file)
            next_func = re.search(r"\ndef\s+", code[func_start:])
            func_end = func_start + next_func.start() if next_func else len(code)

            func_code = code[func_start:func_end]
            line_count = len(func_code.split("\n"))

            if line_count > 50:
                suggestions.append(
                    RepairSuggestion(
                        category="quality",
                        priority="medium",
                        description=f"Refactor long function {func_name}()",
                        rationale=f"Function has {line_count} lines. Aim for < 50 lines per function.",
                        code_example="""
# Extract logical sections into separate functions
def process_data(data):
    validated = _validate_data(data)
    transformed = _transform_data(validated)
    return _store_data(transformed)
                    """.strip(),
                        affected_section=func_name,
                    )
                )

        # Check for duplicated code
        lines = code.split("\n")
        seen_blocks = {}
        for i in range(len(lines) - 3):
            block = "\n".join(lines[i : i + 3])
            block_stripped = block.strip()
            if block_stripped and not block_stripped.startswith("#"):
                if block_stripped in seen_blocks:
                    suggestions.append(
                        RepairSuggestion(
                            category="quality",
                            priority="low",
                            description="Extract duplicated code",
                            rationale="Duplicated code found. Consider extracting to function.",
                            code_example="Create shared function for repeated logic",
                            affected_section=block_stripped[:100],
                        )
                    )
                    break  # Only report first duplication
                seen_blocks[block_stripped] = i

        metric_counter("repair.refactorings_recommended")(len(suggestions))
        return suggestions


def propose_metric_additions(telemetry_code: str) -> list[RepairSuggestion]:
    """
    Propose additional telemetry metrics to add.

    Parameters
    ----------
    telemetry_code : str
        Code with telemetry instrumentation.

    Returns
    -------
    list[RepairSuggestion]
        List of proposed metric additions.

    Example
    -------
    >>> metrics = propose_metric_additions(code)
    >>> for m in metrics:
    ...     print(f"Add metric: {m.description}")
    """
    with span("repair.propose_metrics"):
        suggestions = []

        # Check for error handling without error metrics
        if "except" in telemetry_code and "metric_counter" not in telemetry_code:
            suggestions.append(
                RepairSuggestion(
                    category="observability",
                    priority="high",
                    description="Add error counter metric",
                    rationale="Error handling present but no error metrics recorded.",
                    code_example="""
error_counter = metric_counter("operation.errors")

try:
    result = risky_operation()
except Exception as e:
    error_counter(1, {"error_type": type(e).__name__})
    raise
                """.strip(),
                    affected_section="Error Handling",
                )
            )

        # Check for loops without progress metrics
        if (
            any(keyword in telemetry_code for keyword in ["for ", "while "])
            and "metric_histogram" not in telemetry_code
        ):
            suggestions.append(
                RepairSuggestion(
                    category="observability",
                    priority="medium",
                    description="Add iteration duration histogram",
                    rationale="Loop present but no iteration timing recorded.",
                    code_example="""
iteration_time = metric_histogram("operation.iteration.duration")

for item in items:
    start = time.time()
    process(item)
    iteration_time(time.time() - start)
                    """.strip(),
                    affected_section="Loop Processing",
                )
            )

        # Check for business operations without business metrics
        if "def " in telemetry_code and "metric_counter" not in telemetry_code:
            suggestions.append(
                RepairSuggestion(
                    category="observability",
                    priority="medium",
                    description="Add operation counter",
                    rationale="Business operation should record call count.",
                    code_example="""
operation_counter = metric_counter("operation.calls")

def business_operation():
    operation_counter(1, {"status": "started"})
    try:
        result = perform_work()
        operation_counter(1, {"status": "success"})
        return result
    except Exception:
        operation_counter(1, {"status": "failed"})
        raise
                """.strip(),
                    affected_section="Business Operations",
                )
            )

        metric_counter("repair.metrics_proposed")(len(suggestions))
        return suggestions


def generate_repair_report(spec: str = "", code: str = "") -> dict[str, list[RepairSuggestion]]:
    """
    Generate comprehensive repair report for spec and/or code.

    Parameters
    ----------
    spec : str, optional
        Specification text to analyze.
    code : str, optional
        Python code to analyze.

    Returns
    -------
    dict[str, list[RepairSuggestion]]
        Categorized repair suggestions.

    Example
    -------
    >>> report = generate_repair_report(spec=spec_text, code=code_text)
    >>> for category, suggestions in report.items():
    ...     print(f"{category}: {len(suggestions)} suggestions")
    """
    with span("repair.generate_report"):
        report: dict[str, list[RepairSuggestion]] = {}

        if spec:
            report["missing_requirements"] = suggest_missing_requirements(spec)
            report["edge_case_tests"] = recommend_edge_case_tests(spec)
            report["clarifications"] = propose_clarifications(spec)
            report["simplifications"] = suggest_simplifications(spec)

        if code:
            report["refactoring"] = recommend_refactoring(code)
            report["metrics"] = propose_metric_additions(code)

        return report
