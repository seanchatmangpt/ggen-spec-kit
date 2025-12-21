"""
specify_cli.hyperdimensional.validation
----------------------------------------
Comprehensive validation framework using information-theoretic principles.

This module provides validation capabilities for:
- Specification completeness, consistency, and quality
- Code generation compliance and quality
- Constitutional equation verification
- JTBD outcome delivery validation
- Information density analysis

All functions use entropy, information theory, and statistical analysis
to provide quantitative measures of quality and completeness.

Example
-------
    from specify_cli.hyperdimensional.validation import (
        calculate_specification_entropy,
        verify_spec_compliance,
        measure_outcome_clarity
    )

    # Analyze specification
    entropy = calculate_specification_entropy(spec_text)
    gaps = identify_specification_gaps(spec_text)
    confidence = confidence_in_completeness(spec_text)

    # Validate code
    compliance = verify_spec_compliance(code, spec)
    quality = assess_maintainability(code)
"""

from __future__ import annotations

import ast
import math
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Any

from specify_cli.core.telemetry import metric_counter, metric_histogram, span

__all__ = [
    "CodeQualityReport",
    "JTBDValidation",
    "SpecificationAnalysis",
    # Data classes
    "ValidationResult",
    "assess_implementation_feasibility",
    "assess_maintainability",
    # Information-Theoretic Quality
    "calculate_code_entropy",
    # Information Density
    "calculate_information_density",
    # Specification Completeness
    "calculate_specification_entropy",
    "check_architecture_compliance",
    "check_documentation_completeness",
    "check_logical_consistency",
    "check_metric_coverage",
    "check_success_criteria_completeness",
    "check_testability",
    "confidence_in_completeness",
    # Specification Consistency
    "detect_contradictions",
    "estimate_code_generation_fidelity",
    "estimate_edge_case_coverage",
    "estimate_learning_curve",
    "estimate_maintenance_effort",
    "estimate_outcome_achievement_likelihood",
    "estimate_specification_quality",
    "identify_drift_sources",
    "identify_knowledge_gaps",
    "identify_noise",
    "identify_non_determinism_sources",
    "identify_redundancy",
    "identify_specification_gaps",
    "identify_suspicious_patterns",
    "identify_telemetry_gaps",
    "identify_unmet_job_needs",
    "measure_coherence",
    "measure_generation_consistency",
    "measure_information_density",
    "measure_job_coverage",
    "measure_outcome_clarity",
    "measure_semantic_richness",
    # Specification Quality
    "measure_specification_clarity",
    "measure_specification_drift",
    "measure_test_coverage",
    "suggest_clarifications",
    "suggest_clarifying_questions",
    "validate_attribute_completeness",
    "validate_feature_job_alignment",
    "validate_type_safety",
    # Constitutional Equation
    "verify_constitutional_equation",
    "verify_constraint_satisfaction",
    "verify_deterministic_generation",
    # JTBD Outcome Validation
    "verify_outcome_delivery",
    # OTEL Instrumentation
    "verify_span_coverage",
    # Code Generation Validation
    "verify_spec_compliance",
]


# ============================================================================
# Data Classes
# ============================================================================


@dataclass
class ValidationResult:
    """Result of a validation check."""

    passed: bool
    score: float  # 0.0 to 1.0
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    suggestions: list[str] = field(default_factory=list)


@dataclass
class SpecificationAnalysis:
    """Complete analysis of a specification."""

    entropy: float
    completeness_score: float
    consistency_score: float
    clarity_score: float
    testability_score: float
    gaps: list[str]
    contradictions: list[str]
    questions: list[str]
    redundancies: list[str]


@dataclass
class CodeQualityReport:
    """Quality report for generated code."""

    spec_compliance: float
    architecture_compliance: float
    type_safety: float
    test_coverage: float
    documentation: float
    maintainability: float
    entropy: float
    information_density: float
    suspicious_patterns: list[str]
    telemetry_gaps: list[str]


@dataclass
class JTBDValidation:
    """JTBD outcome validation results."""

    outcome_delivered: bool
    outcome_clarity: float
    success_criteria_complete: float
    achievement_likelihood: float
    job_coverage: float
    unmet_needs: list[str]
    alignment_score: float


# ============================================================================
# Specification Completeness Validation
# ============================================================================


def calculate_specification_entropy(spec: str) -> float:
    """
    Calculate information entropy of a specification text.

    Uses Shannon entropy to measure information content and complexity.
    Higher entropy indicates more diverse/complex specifications.

    Parameters
    ----------
    spec : str
        The specification text to analyze.

    Returns
    -------
    float
        Entropy value in bits. Range: 0 (trivial) to ~15 (very complex).

    Example
    -------
    >>> spec = "The system must handle user authentication..."
    >>> entropy = calculate_specification_entropy(spec)
    >>> print(f"Specification entropy: {entropy:.2f} bits")
    """
    with span("validation.calculate_entropy", validation_type="specification"):
        if not spec or not spec.strip():
            return 0.0

        # Tokenize: words, symbols, numbers
        tokens = re.findall(r"\w+|[^\w\s]", spec.lower())
        if not tokens:
            return 0.0

        # Calculate frequency distribution
        freq = Counter(tokens)
        total = len(tokens)

        # Shannon entropy: H = -Σ(p(x) * log2(p(x)))
        entropy = 0.0
        for count in freq.values():
            prob = count / total
            entropy -= prob * math.log2(prob)

        metric_histogram("validation.entropy", unit="bits")(entropy)
        return entropy


def estimate_edge_case_coverage(spec: str) -> float:
    """
    Estimate percentage of edge cases likely covered by specification.

    Analyzes specification for indicators of edge case consideration:
    - Conditional statements (if, when, unless)
    - Negative cases (not, never, except)
    - Boundary conditions (minimum, maximum, empty, null)
    - Error handling (error, fail, invalid)

    Parameters
    ----------
    spec : str
        Specification text to analyze.

    Returns
    -------
    float
        Estimated coverage percentage (0-100).

    Example
    -------
    >>> spec = "Must handle empty input. If invalid, return error."
    >>> coverage = estimate_edge_case_coverage(spec)
    >>> print(f"Edge case coverage: {coverage:.1f}%")
    """
    with span("validation.edge_case_coverage"):
        if not spec or not spec.strip():
            return 0.0

        spec_lower = spec.lower()

        # Edge case indicators
        indicators = {
            "conditionals": [r"\bif\b", r"\bwhen\b", r"\bunless\b", r"\belse\b"],
            "negatives": [r"\bnot\b", r"\bnever\b", r"\bexcept\b", r"\bno\b"],
            "boundaries": [
                r"\bempty\b",
                r"\bnull\b",
                r"\bzero\b",
                r"\bminimum\b",
                r"\bmaximum\b",
                r"\blimit\b",
                r"\bbound\b",
            ],
            "errors": [r"\berror\b", r"\bfail\b", r"\binvalid\b", r"\bexception\b", r"\btimeout\b"],
        }

        # Count occurrences
        total_indicators = 0
        for _category, patterns in indicators.items():
            for pattern in patterns:
                matches = len(re.findall(pattern, spec_lower))
                total_indicators += matches

        # Normalize by spec length (per 100 words)
        word_count = len(spec.split())
        if word_count == 0:
            return 0.0

        # Scale: 0 indicators = 0%, 10+ per 100 words = 100%
        coverage = min(100.0, (total_indicators / word_count) * 100 * 10)

        metric_histogram("validation.edge_case_coverage", unit="%")(coverage)
        return coverage


def identify_specification_gaps(spec: str) -> list[str]:
    """
    Identify missing or incomplete requirements in specification.

    Looks for:
    - Missing error handling
    - Undefined edge cases
    - Ambiguous requirements
    - Missing non-functional requirements (performance, security)
    - Incomplete acceptance criteria

    Parameters
    ----------
    spec : str
        Specification text to analyze.

    Returns
    -------
    list[str]
        List of identified gaps.

    Example
    -------
    >>> gaps = identify_specification_gaps(spec)
    >>> for gap in gaps:
    ...     print(f"Gap: {gap}")
    """
    with span("validation.identify_gaps"):
        gaps = []
        spec_lower = spec.lower()

        # Check for error handling
        if not any(word in spec_lower for word in ["error", "exception", "fail"]):
            gaps.append("Missing error handling specifications")

        # Check for performance requirements
        if not any(
            word in spec_lower for word in ["performance", "latency", "throughput", "response time"]
        ):
            gaps.append("Missing performance requirements")

        # Check for security considerations
        if not any(
            word in spec_lower
            for word in ["security", "authentication", "authorization", "encrypt"]
        ):
            gaps.append("Missing security considerations")

        # Check for input validation
        if not any(word in spec_lower for word in ["validate", "validation", "check", "verify"]):
            gaps.append("Missing input validation requirements")

        # Check for boundary conditions
        if not any(word in spec_lower for word in ["empty", "null", "minimum", "maximum", "limit"]):
            gaps.append("Missing boundary condition specifications")

        # Check for acceptance criteria
        if "acceptance" not in spec_lower and "criteria" not in spec_lower:
            gaps.append("Missing acceptance criteria")

        # Check for logging/observability
        if not any(
            word in spec_lower for word in ["log", "trace", "monitor", "observability", "telemetry"]
        ):
            gaps.append("Missing observability requirements")

        metric_counter("validation.gaps_identified")(len(gaps))
        return gaps


def suggest_clarifying_questions(spec: str) -> list[str]:
    """
    Suggest questions to clarify ambiguous specification parts.

    Analyzes specification for:
    - Vague quantifiers (some, many, few)
    - Undefined terms
    - Missing details
    - Ambiguous behavior descriptions

    Parameters
    ----------
    spec : str
        Specification text to analyze.

    Returns
    -------
    list[str]
        List of suggested clarifying questions.

    Example
    -------
    >>> questions = suggest_clarifying_questions(spec)
    >>> for q in questions:
    ...     print(f"Q: {q}")
    """
    with span("validation.suggest_questions"):
        questions = []
        spec_lower = spec.lower()

        # Vague quantifiers
        vague_terms = {
            "some": "How many/which specific instances?",
            "many": "What is the exact threshold for 'many'?",
            "few": "What is the specific number for 'few'?",
            "sometimes": "Under what specific conditions?",
            "often": "What is the frequency threshold?",
            "quickly": "What is the maximum acceptable time?",
            "slowly": "What is the expected time range?",
            "large": "What is the size threshold?",
            "small": "What defines 'small' in this context?",
        }

        for term, question in vague_terms.items():
            if f" {term} " in f" {spec_lower} ":
                questions.append(f"'{term}' is vague: {question}")

        # Missing specifics
        if "should" in spec_lower:
            questions.append("'Should' is ambiguous - is this required or optional?")

        if "appropriate" in spec_lower or "suitable" in spec_lower:
            questions.append("What criteria define 'appropriate' or 'suitable'?")

        # Undefined behavior
        if "etc" in spec_lower or "..." in spec:
            questions.append("'etc' or '...' indicates incomplete list - what are all items?")

        metric_counter("validation.questions_suggested")(len(questions))
        return questions


def confidence_in_completeness(spec: str) -> float:
    """
    Calculate confidence that specification is complete (0.0 to 1.0).

    Combines multiple metrics:
    - Entropy (complexity coverage)
    - Edge case coverage
    - Number of gaps
    - Clarity

    Parameters
    ----------
    spec : str
        Specification text to analyze.

    Returns
    -------
    float
        Confidence score (0.0 = very incomplete, 1.0 = highly complete).

    Example
    -------
    >>> confidence = confidence_in_completeness(spec)
    >>> print(f"Completeness confidence: {confidence:.1%}")
    """
    with span("validation.confidence_completeness"):
        if not spec or not spec.strip():
            return 0.0

        # Component scores
        entropy = calculate_specification_entropy(spec)
        edge_coverage = estimate_edge_case_coverage(spec) / 100.0
        gaps = identify_specification_gaps(spec)
        gap_penalty = max(0.0, 1.0 - (len(gaps) * 0.1))

        # Weighted combination
        confidence = (
            (entropy / 15.0) * 0.3  # Entropy contribution
            + edge_coverage * 0.4  # Edge case coverage
            + gap_penalty * 0.3  # Penalty for gaps
        )

        confidence = max(0.0, min(1.0, confidence))
        metric_histogram("validation.completeness_confidence", unit="ratio")(confidence)
        return confidence


# ============================================================================
# Specification Consistency Validation
# ============================================================================


def detect_contradictions(specs: list[str]) -> list[tuple[str, str, str]]:
    """
    Detect contradictory requirements across specifications.

    Looks for:
    - Direct contradictions (must/must not)
    - Conflicting requirements
    - Inconsistent terminology

    Parameters
    ----------
    specs : list[str]
        List of specification texts to check.

    Returns
    -------
    list[tuple[str, str, str]]
        List of (spec1_fragment, spec2_fragment, reason) tuples.

    Example
    -------
    >>> contradictions = detect_contradictions(all_specs)
    >>> for s1, s2, reason in contradictions:
    ...     print(f"Contradiction: {reason}")
    """
    with span("validation.detect_contradictions"):
        contradictions = []

        for i, spec1 in enumerate(specs):
            for spec2 in specs[i + 1 :]:
                # Check for must/must not conflicts
                spec1_lower = spec1.lower()
                spec2_lower = spec2.lower()

                # Extract requirements
                must_patterns = re.findall(r"must ([\w\s]+?)(?:[.,;]|$)", spec1_lower)
                must_not_patterns = re.findall(r"must not ([\w\s]+?)(?:[.,;]|$)", spec2_lower)

                for must in must_patterns:
                    for must_not in must_not_patterns:
                        # Simple similarity check
                        if len(set(must.split()) & set(must_not.split())) > 2:
                            contradictions.append(
                                (
                                    f"must {must}",
                                    f"must not {must_not}",
                                    "Direct contradiction between requirements",
                                )
                            )

        metric_counter("validation.contradictions_found")(len(contradictions))
        return contradictions


def check_logical_consistency(rules: list[str]) -> ValidationResult:
    """
    Check logical consistency of specification rules.

    Validates:
    - No tautologies (always true)
    - No contradictions (always false)
    - Satisfiability

    Parameters
    ----------
    rules : list[str]
        List of logical rules/constraints.

    Returns
    -------
    ValidationResult
        Validation result with consistency score.

    Example
    -------
    >>> result = check_logical_consistency(rules)
    >>> if not result.passed:
    ...     print(f"Inconsistent: {result.message}")
    """
    with span("validation.logical_consistency"):
        # Simple heuristic-based consistency check
        contradictions = []
        tautologies = []

        for rule in rules:
            rule_lower = rule.lower()

            # Check for obvious tautologies
            if "always" in rule_lower and "never" in rule_lower:
                tautologies.append(rule)

            # Check for contradictions
            if "must" in rule_lower and "must not" in rule_lower:
                # Same sentence has both - likely contradiction
                contradictions.append(rule)

        issues = len(contradictions) + len(tautologies)
        score = max(0.0, 1.0 - (issues * 0.2))
        passed = issues == 0

        return ValidationResult(
            passed=passed,
            score=score,
            message=f"Found {len(contradictions)} contradictions and {len(tautologies)} tautologies",
            details={
                "contradictions": contradictions,
                "tautologies": tautologies,
            },
            suggestions=[
                "Review contradictory statements",
                "Remove or clarify tautological rules",
            ]
            if not passed
            else [],
        )


def verify_constraint_satisfaction(spec: str, constraints: dict[str, Any]) -> ValidationResult:
    """
    Verify specification satisfies given constraints.

    Parameters
    ----------
    spec : str
        Specification text.
    constraints : dict[str, Any]
        Constraints to check (e.g., {"min_length": 100, "must_contain": ["error"]}).

    Returns
    -------
    ValidationResult
        Constraint satisfaction result.

    Example
    -------
    >>> constraints = {"min_length": 100, "must_contain": ["error handling"]}
    >>> result = verify_constraint_satisfaction(spec, constraints)
    """
    with span("validation.constraint_satisfaction"):
        violations = []
        spec_lower = spec.lower()

        # Check minimum length
        if "min_length" in constraints:
            min_len = constraints["min_length"]
            if len(spec) < min_len:
                violations.append(f"Spec length {len(spec)} < minimum {min_len}")

        # Check maximum length
        if "max_length" in constraints:
            max_len = constraints["max_length"]
            if len(spec) > max_len:
                violations.append(f"Spec length {len(spec)} > maximum {max_len}")

        # Check required content
        if "must_contain" in constraints:
            for required in constraints["must_contain"]:
                if required.lower() not in spec_lower:
                    violations.append(f"Missing required content: '{required}'")

        # Check forbidden content
        if "must_not_contain" in constraints:
            for forbidden in constraints["must_not_contain"]:
                if forbidden.lower() in spec_lower:
                    violations.append(f"Contains forbidden content: '{forbidden}'")

        score = max(0.0, 1.0 - (len(violations) * 0.2))
        passed = len(violations) == 0

        return ValidationResult(
            passed=passed,
            score=score,
            message=f"Constraint satisfaction: {len(violations)} violations",
            details={"violations": violations},
            suggestions=[f"Fix: {v}" for v in violations],
        )


def identify_redundancy(specs: list[str]) -> list[tuple[str, str, float]]:
    """
    Identify redundant or duplicate specifications.

    Uses text similarity to find near-duplicates.

    Parameters
    ----------
    specs : list[str]
        List of specification texts.

    Returns
    -------
    list[tuple[str, str, float]]
        List of (spec1, spec2, similarity_score) for redundant pairs.

    Example
    -------
    >>> redundancies = identify_redundancy(all_specs)
    >>> for s1, s2, similarity in redundancies:
    ...     print(f"Redundant (similarity={similarity:.2f})")
    """
    with span("validation.identify_redundancy"):
        redundancies = []

        for i, spec1 in enumerate(specs):
            for spec2 in specs[i + 1 :]:
                similarity = _calculate_text_similarity(spec1, spec2)
                if similarity > 0.7:  # High similarity threshold
                    redundancies.append((spec1, spec2, similarity))

        metric_counter("validation.redundancies_found")(len(redundancies))
        return redundancies


def measure_coherence(spec: str) -> float:
    """
    Measure internal coherence/consistency of specification.

    Analyzes:
    - Terminology consistency
    - Structural coherence
    - Logical flow

    Parameters
    ----------
    spec : str
        Specification text.

    Returns
    -------
    float
        Coherence score (0.0 = incoherent, 1.0 = highly coherent).

    Example
    -------
    >>> coherence = measure_coherence(spec)
    >>> print(f"Coherence: {coherence:.1%}")
    """
    with span("validation.measure_coherence"):
        if not spec or not spec.strip():
            return 0.0

        # Split into sentences
        sentences = re.split(r"[.!?]+", spec)
        sentences = [s.strip() for s in sentences if s.strip()]

        if len(sentences) < 2:
            return 1.0  # Single sentence is trivially coherent

        # Measure inter-sentence similarity
        similarities = []
        for i in range(len(sentences) - 1):
            sim = _calculate_text_similarity(sentences[i], sentences[i + 1])
            similarities.append(sim)

        # Average similarity indicates coherence
        coherence = sum(similarities) / len(similarities) if similarities else 0.0

        metric_histogram("validation.coherence", unit="ratio")(coherence)
        return coherence


# ============================================================================
# Specification Quality Validation
# ============================================================================


def measure_specification_clarity(spec: str) -> float:
    """
    Measure clarity of specification (inverse of ambiguity).

    Lower values indicate more ambiguous specifications.

    Parameters
    ----------
    spec : str
        Specification text.

    Returns
    -------
    float
        Clarity score (0.0 = very ambiguous, 1.0 = crystal clear).

    Example
    -------
    >>> clarity = measure_specification_clarity(spec)
    >>> print(f"Clarity: {clarity:.1%}")
    """
    with span("validation.measure_clarity"):
        if not spec or not spec.strip():
            return 0.0

        spec_lower = spec.lower()

        # Count ambiguous terms
        ambiguous_count = 0
        ambiguous_terms = [
            "maybe",
            "possibly",
            "probably",
            "should",
            "could",
            "might",
            "some",
            "many",
            "few",
            "approximately",
            "about",
            "roughly",
            "generally",
            "usually",
            "often",
        ]

        for term in ambiguous_terms:
            ambiguous_count += len(re.findall(rf"\b{term}\b", spec_lower))

        # Normalize by word count
        word_count = len(spec.split())
        if word_count == 0:
            return 0.0

        ambiguity_ratio = ambiguous_count / word_count

        # Clarity is inverse of ambiguity
        clarity = max(0.0, 1.0 - (ambiguity_ratio * 10))

        metric_histogram("validation.clarity", unit="ratio")(clarity)
        return clarity


def check_testability(spec: str) -> float:
    """
    Check how testable/measurable the specification is.

    Looks for:
    - Concrete acceptance criteria
    - Measurable outcomes
    - Observable behaviors
    - Quantitative metrics

    Parameters
    ----------
    spec : str
        Specification text.

    Returns
    -------
    float
        Testability score (0.0 = not testable, 1.0 = highly testable).

    Example
    -------
    >>> testability = check_testability(spec)
    >>> print(f"Testability: {testability:.1%}")
    """
    with span("validation.check_testability"):
        if not spec or not spec.strip():
            return 0.0

        spec_lower = spec.lower()

        # Testability indicators
        testable_indicators = 0

        # Measurable criteria
        measurable_terms = ["must", "shall", "will", "should return", "should display"]
        for term in measurable_terms:
            testable_indicators += len(re.findall(rf"\b{term}\b", spec_lower))

        # Quantitative metrics
        testable_indicators += len(re.findall(r"\d+", spec))

        # Observable outcomes
        observable_terms = ["display", "show", "return", "output", "result", "response"]
        for term in observable_terms:
            testable_indicators += len(re.findall(rf"\b{term}\b", spec_lower))

        # Acceptance criteria
        if "acceptance" in spec_lower or "criteria" in spec_lower:
            testable_indicators += 5

        # Normalize
        word_count = len(spec.split())
        if word_count == 0:
            return 0.0

        testability = min(1.0, (testable_indicators / word_count) * 5)

        metric_histogram("validation.testability", unit="ratio")(testability)
        return testability


def assess_implementation_feasibility(spec: str) -> float:
    """
    Assess how feasible the specification is to implement.

    Considers:
    - Complexity indicators
    - Technology availability
    - Resource requirements
    - Dependencies

    Parameters
    ----------
    spec : str
        Specification text.

    Returns
    -------
    float
        Feasibility score (0.0 = very difficult, 1.0 = highly feasible).

    Example
    -------
    >>> feasibility = assess_implementation_feasibility(spec)
    >>> print(f"Feasibility: {feasibility:.1%}")
    """
    with span("validation.assess_feasibility"):
        if not spec or not spec.strip():
            return 0.0

        spec_lower = spec.lower()

        # Start with neutral feasibility
        feasibility = 0.5

        # High complexity indicators (reduce feasibility)
        complexity_terms = ["real-time", "distributed", "scalable", "ml", "ai", "blockchain"]
        for term in complexity_terms:
            if term in spec_lower:
                feasibility -= 0.05

        # Feasibility boosters
        simple_terms = ["crud", "rest", "api", "web", "database"]
        for term in simple_terms:
            if term in spec_lower:
                feasibility += 0.05

        # Constraint penalties
        hard_constraints = ["real-time", "millisecond", "zero downtime", "infinite scale"]
        for constraint in hard_constraints:
            if constraint in spec_lower:
                feasibility -= 0.1

        feasibility = max(0.0, min(1.0, feasibility))

        metric_histogram("validation.feasibility", unit="ratio")(feasibility)
        return feasibility


def estimate_maintenance_effort(spec: str) -> float:
    """
    Estimate future maintenance effort for implemented system.

    Higher values indicate higher expected maintenance costs.

    Parameters
    ----------
    spec : str
        Specification text.

    Returns
    -------
    float
        Maintenance effort estimate (0.0 = low, 1.0 = very high).

    Example
    -------
    >>> effort = estimate_maintenance_effort(spec)
    >>> print(f"Maintenance effort: {effort:.1%}")
    """
    with span("validation.estimate_maintenance"):
        if not spec or not spec.strip():
            return 0.0

        spec_lower = spec.lower()

        # Start with baseline
        effort = 0.3

        # Complexity drivers (increase effort)
        complexity_drivers = [
            "integration",
            "third-party",
            "api",
            "external",
            "complex",
            "algorithm",
            "optimization",
            "caching",
        ]
        for driver in complexity_drivers:
            if driver in spec_lower:
                effort += 0.05

        # Change frequency indicators
        change_terms = ["configurable", "customizable", "flexible", "extensible"]
        for term in change_terms:
            if term in spec_lower:
                effort += 0.03

        # Maintenance reducers
        simple_terms = ["static", "readonly", "immutable", "constant"]
        for term in simple_terms:
            if term in spec_lower:
                effort -= 0.03

        effort = max(0.0, min(1.0, effort))

        metric_histogram("validation.maintenance_effort", unit="ratio")(effort)
        return effort


# ============================================================================
# Code Generation Validation
# ============================================================================


def verify_spec_compliance(generated_code: str, spec: str) -> float:
    """
    Verify how well generated code complies with specification.

    Parameters
    ----------
    generated_code : str
        Generated Python code.
    spec : str
        Original specification.

    Returns
    -------
    float
        Compliance percentage (0.0 to 1.0).

    Example
    -------
    >>> compliance = verify_spec_compliance(code, spec)
    >>> print(f"Spec compliance: {compliance:.1%}")
    """
    with span("validation.spec_compliance"):
        if not generated_code or not spec:
            return 0.0

        spec_lower = spec.lower()
        code_lower = generated_code.lower()

        # Extract key requirements from spec
        requirements = []

        # Function requirements
        func_patterns = re.findall(r"function (\w+)", spec_lower)
        requirements.extend(func_patterns)

        # Class requirements
        class_patterns = re.findall(r"class (\w+)", spec_lower)
        requirements.extend(class_patterns)

        # Method requirements
        method_patterns = re.findall(r"method (\w+)", spec_lower)
        requirements.extend(method_patterns)

        if not requirements:
            # No specific requirements extracted, do semantic similarity
            return _calculate_text_similarity(code_lower, spec_lower)

        # Check how many requirements are met
        met_requirements = 0
        for req in requirements:
            if req in code_lower:
                met_requirements += 1

        compliance = met_requirements / len(requirements) if requirements else 0.0

        metric_histogram("validation.spec_compliance", unit="ratio")(compliance)
        return compliance


def check_architecture_compliance(code: str) -> ValidationResult:
    """
    Check code compliance with three-tier architecture rules.

    Validates:
    - No subprocess in commands/ops layers
    - No file I/O in commands/ops layers
    - Proper layer separation

    Parameters
    ----------
    code : str
        Python code to check.

    Returns
    -------
    ValidationResult
        Architecture compliance result.

    Example
    -------
    >>> result = check_architecture_compliance(code)
    >>> if not result.passed:
    ...     print(f"Architecture violations: {result.message}")
    """
    with span("validation.architecture_compliance"):
        violations = []

        try:
            tree = ast.parse(code)

            # Check for subprocess usage
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name == "subprocess":
                            violations.append("Direct subprocess import (should use runtime layer)")

                elif isinstance(node, ast.ImportFrom):
                    if node.module == "subprocess":
                        violations.append(
                            "Subprocess import from runtime (should use runtime layer)"
                        )

                # Check for file I/O
                elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    if node.func.id in ["open", "read", "write"]:
                        violations.append(f"Direct file I/O: {node.func.id}()")

        except SyntaxError as e:
            violations.append(f"Syntax error: {e}")

        score = max(0.0, 1.0 - (len(violations) * 0.15))
        passed = len(violations) == 0

        return ValidationResult(
            passed=passed,
            score=score,
            message=f"Architecture compliance: {len(violations)} violations",
            details={"violations": violations},
            suggestions=[
                "Move subprocess calls to runtime layer",
                "Use runtime layer for file I/O operations",
            ]
            if not passed
            else [],
        )


def validate_type_safety(code: str) -> ValidationResult:
    """
    Validate type safety of generated code.

    Checks:
    - Type hints present
    - Consistent type usage
    - No unsafe casts

    Parameters
    ----------
    code : str
        Python code to validate.

    Returns
    -------
    ValidationResult
        Type safety validation result.

    Example
    -------
    >>> result = validate_type_safety(code)
    >>> print(f"Type safety score: {result.score:.1%}")
    """
    with span("validation.type_safety"):
        issues = []

        try:
            tree = ast.parse(code)

            # Count functions with/without type hints
            total_funcs = 0
            typed_funcs = 0

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    total_funcs += 1

                    # Check if has return type annotation
                    if node.returns is not None:
                        typed_funcs += 1

                    # Check if parameters have type annotations
                    for arg in node.args.args:
                        if arg.annotation is None and arg.arg != "self":
                            issues.append(f"Parameter '{arg.arg}' in {node.name}() lacks type hint")

            if total_funcs > 0:
                type_coverage = typed_funcs / total_funcs
            else:
                type_coverage = 1.0  # No functions = no type issues

            score = max(0.0, type_coverage - (len(issues) * 0.05))

        except SyntaxError as e:
            issues.append(f"Syntax error: {e}")
            score = 0.0

        passed = len(issues) == 0
        return ValidationResult(
            passed=passed,
            score=score,
            message=f"Type safety: {len(issues)} issues",
            details={"issues": issues},
            suggestions=["Add type hints to all function parameters and returns"],
        )


def measure_test_coverage(code: str) -> float:
    """
    Estimate test coverage from generated code.

    Looks for test functions and assertions.

    Parameters
    ----------
    code : str
        Python code (including tests).

    Returns
    -------
    float
        Estimated test coverage (0.0 to 1.0).

    Example
    -------
    >>> coverage = measure_test_coverage(code_with_tests)
    >>> print(f"Test coverage estimate: {coverage:.1%}")
    """
    with span("validation.test_coverage"):
        try:
            tree = ast.parse(code)

            # Count testable items (functions, methods)
            testable_items = 0
            test_functions = 0

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if node.name.startswith("test_"):
                        test_functions += 1
                    elif not node.name.startswith("_"):
                        testable_items += 1

            if testable_items == 0:
                return 1.0 if test_functions > 0 else 0.0

            # Estimate coverage (rough heuristic)
            coverage = min(1.0, test_functions / max(1, testable_items))

        except SyntaxError:
            coverage = 0.0

        metric_histogram("validation.test_coverage", unit="ratio")(coverage)
        return coverage


def check_documentation_completeness(code: str) -> float:
    """
    Check documentation completeness in code.

    Measures:
    - Docstring coverage
    - Comment density
    - Documentation quality

    Parameters
    ----------
    code : str
        Python code to check.

    Returns
    -------
    float
        Documentation completeness (0.0 to 1.0).

    Example
    -------
    >>> doc_completeness = check_documentation_completeness(code)
    >>> print(f"Documentation: {doc_completeness:.1%}")
    """
    with span("validation.documentation_completeness"):
        try:
            tree = ast.parse(code)

            # Count functions/classes with docstrings
            total_definitions = 0
            documented = 0

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    total_definitions += 1

                    # Check for docstring
                    if ast.get_docstring(node) is not None:
                        documented += 1

            if total_definitions == 0:
                return 1.0

            completeness = documented / total_definitions

        except SyntaxError:
            completeness = 0.0

        metric_histogram("validation.documentation", unit="ratio")(completeness)
        return completeness


# ============================================================================
# Information-Theoretic Code Quality
# ============================================================================


def calculate_code_entropy(code: str) -> float:
    """
    Calculate algorithmic complexity of code using entropy.

    Higher entropy indicates more complex/diverse code.

    Parameters
    ----------
    code : str
        Python code to analyze.

    Returns
    -------
    float
        Code entropy in bits.

    Example
    -------
    >>> entropy = calculate_code_entropy(code)
    >>> print(f"Code complexity: {entropy:.2f} bits")
    """
    with span("validation.code_entropy"):
        # Similar to specification entropy but on code tokens
        return calculate_specification_entropy(code)


def measure_information_density(code: str) -> float:
    """
    Measure information density (signal-to-noise ratio) of code.

    Higher values indicate more meaningful code per line.

    Parameters
    ----------
    code : str
        Python code to analyze.

    Returns
    -------
    float
        Information density (0.0 = low, 1.0 = high).

    Example
    -------
    >>> density = measure_information_density(code)
    >>> print(f"Information density: {density:.1%}")
    """
    with span("validation.information_density"):
        if not code or not code.strip():
            return 0.0

        lines = code.split("\n")
        total_lines = len(lines)

        # Count meaningful lines (not comments, not blank)
        meaningful_lines = 0
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                meaningful_lines += 1

        if total_lines == 0:
            return 0.0

        density = meaningful_lines / total_lines

        metric_histogram("validation.information_density", unit="ratio")(density)
        return density


def identify_suspicious_patterns(code: str) -> list[str]:
    """
    Identify suspicious code patterns that may indicate bugs.

    Looks for:
    - Unused variables
    - Hardcoded values
    - Missing error handling
    - Unsafe patterns

    Parameters
    ----------
    code : str
        Python code to analyze.

    Returns
    -------
    list[str]
        List of suspicious patterns found.

    Example
    -------
    >>> patterns = identify_suspicious_patterns(code)
    >>> for pattern in patterns:
    ...     print(f"Suspicious: {pattern}")
    """
    with span("validation.suspicious_patterns"):
        patterns = []

        try:
            tree = ast.parse(code)

            # Check for bare except clauses
            for node in ast.walk(tree):
                if isinstance(node, ast.ExceptHandler):
                    if node.type is None:
                        patterns.append("Bare except clause (catches all exceptions)")

                # Check for hardcoded credentials patterns
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and any(
                            keyword in target.id.lower()
                            for keyword in ["password", "secret", "key", "token"]
                        ):
                            patterns.append(f"Potential hardcoded credential: {target.id}")

        except SyntaxError as e:
            patterns.append(f"Syntax error: {e}")

        metric_counter("validation.suspicious_patterns")(len(patterns))
        return patterns


def assess_maintainability(code: str) -> float:
    """
    Assess code maintainability using multiple metrics.

    Considers:
    - Complexity
    - Documentation
    - Modularity
    - Code clarity

    Parameters
    ----------
    code : str
        Python code to assess.

    Returns
    -------
    float
        Maintainability score (0.0 = low, 1.0 = high).

    Example
    -------
    >>> maintainability = assess_maintainability(code)
    >>> print(f"Maintainability: {maintainability:.1%}")
    """
    with span("validation.assess_maintainability"):
        if not code or not code.strip():
            return 0.0

        # Component scores
        doc_completeness = check_documentation_completeness(code)
        info_density = measure_information_density(code)
        suspicious = len(identify_suspicious_patterns(code))

        # Penalize for excessive complexity
        lines = len(code.split("\n"))
        complexity_penalty = 0.0
        if lines > 500:
            complexity_penalty = 0.2
        elif lines > 1000:
            complexity_penalty = 0.4

        # Combine metrics
        maintainability = (
            doc_completeness * 0.4
            + info_density * 0.3
            + (1.0 - min(1.0, suspicious * 0.1)) * 0.3
            - complexity_penalty
        )

        maintainability = max(0.0, min(1.0, maintainability))

        metric_histogram("validation.maintainability", unit="ratio")(maintainability)
        return maintainability


# ============================================================================
# OTEL Instrumentation Validation
# ============================================================================


def verify_span_coverage(code: str) -> float:
    """
    Verify percentage of operations with OTEL span coverage.

    Parameters
    ----------
    code : str
        Python code to check.

    Returns
    -------
    float
        Span coverage percentage (0.0 to 1.0).

    Example
    -------
    >>> coverage = verify_span_coverage(code)
    >>> print(f"Span coverage: {coverage:.1%}")
    """
    with span("validation.span_coverage"):
        try:
            tree = ast.parse(code)

            total_operations = 0
            instrumented_operations = 0

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    total_operations += 1

                    # Check if function body has span context manager
                    for child in ast.walk(node):
                        if isinstance(child, ast.With):
                            for item in child.items:
                                if isinstance(item.context_expr, ast.Call):
                                    if isinstance(item.context_expr.func, ast.Name):
                                        if item.context_expr.func.id == "span":
                                            instrumented_operations += 1
                                            break

            if total_operations == 0:
                return 1.0

            coverage = instrumented_operations / total_operations

        except SyntaxError:
            coverage = 0.0

        metric_histogram("validation.span_coverage", unit="ratio")(coverage)
        return coverage


def check_metric_coverage(code: str) -> float:
    """
    Check percentage of operations with metric recording.

    Parameters
    ----------
    code : str
        Python code to check.

    Returns
    -------
    float
        Metric coverage percentage (0.0 to 1.0).

    Example
    -------
    >>> coverage = check_metric_coverage(code)
    >>> print(f"Metric coverage: {coverage:.1%}")
    """
    with span("validation.metric_coverage"):
        code_lower = code.lower()

        # Count metric calls
        metric_patterns = [
            "metric_counter",
            "metric_histogram",
            "metric_gauge",
            "counter.add",
            "histogram.record",
            "gauge.set",
        ]

        metric_calls = 0
        for pattern in metric_patterns:
            metric_calls += code_lower.count(pattern)

        # Estimate coverage based on function count
        func_count = code_lower.count("def ")
        if func_count == 0:
            return 1.0 if metric_calls > 0 else 0.0

        # Assume good coverage if at least 50% of functions have metrics
        coverage = min(1.0, (metric_calls / func_count) * 2)

        metric_histogram("validation.metric_coverage", unit="ratio")(coverage)
        return coverage


def validate_attribute_completeness(spans: list[dict[str, Any]]) -> float:
    """
    Validate completeness of span attributes.

    Parameters
    ----------
    spans : list[dict[str, Any]]
        List of span dictionaries with attributes.

    Returns
    -------
    float
        Attribute completeness (0.0 to 1.0).

    Example
    -------
    >>> completeness = validate_attribute_completeness(span_data)
    >>> print(f"Attribute completeness: {completeness:.1%}")
    """
    with span("validation.attribute_completeness"):
        if not spans:
            return 1.0

        # Expected attributes for quality spans
        expected_attrs = {"operation.type", "operation.name", "service.name"}

        complete_spans = 0
        for span_data in spans:
            attrs = set(span_data.get("attributes", {}).keys())
            if expected_attrs.issubset(attrs):
                complete_spans += 1

        completeness = complete_spans / len(spans)

        metric_histogram("validation.attribute_completeness", unit="ratio")(completeness)
        return completeness


def identify_telemetry_gaps(code: str) -> list[str]:
    """
    Identify missing telemetry instrumentation in code.

    Parameters
    ----------
    code : str
        Python code to analyze.

    Returns
    -------
    list[str]
        List of identified telemetry gaps.

    Example
    -------
    >>> gaps = identify_telemetry_gaps(code)
    >>> for gap in gaps:
    ...     print(f"Telemetry gap: {gap}")
    """
    with span("validation.telemetry_gaps"):
        gaps = []

        try:
            tree = ast.parse(code)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check if function has span instrumentation
                    has_span = False
                    for child in ast.walk(node):
                        if isinstance(child, ast.With):
                            for item in child.items:
                                if isinstance(item.context_expr, ast.Call):
                                    if isinstance(item.context_expr.func, ast.Name):
                                        if item.context_expr.func.id == "span":
                                            has_span = True
                                            break

                    if not has_span and not node.name.startswith("_"):
                        gaps.append(f"Function {node.name}() missing span instrumentation")

        except SyntaxError as e:
            gaps.append(f"Syntax error prevents analysis: {e}")

        metric_counter("validation.telemetry_gaps")(len(gaps))
        return gaps


# ============================================================================
# Constitutional Equation Validation
# ============================================================================


def verify_constitutional_equation(spec: str, code: str) -> ValidationResult:
    """
    Verify that spec.md = μ(feature.ttl) holds.

    Checks if generated code correctly implements specification.

    Parameters
    ----------
    spec : str
        Original specification.
    code : str
        Generated code.

    Returns
    -------
    ValidationResult
        Validation result for constitutional equation.

    Example
    -------
    >>> result = verify_constitutional_equation(spec, code)
    >>> if result.passed:
    ...     print("Constitutional equation holds!")
    """
    with span("validation.constitutional_equation"):
        # Calculate compliance metrics
        compliance = verify_spec_compliance(code, spec)
        arch_compliance = check_architecture_compliance(code)
        type_safety = validate_type_safety(code)

        # Combined score
        score = compliance * 0.5 + arch_compliance.score * 0.3 + type_safety.score * 0.2

        passed = score >= 0.8  # High bar for constitutional equation

        return ValidationResult(
            passed=passed,
            score=score,
            message=f"Constitutional equation {'holds' if passed else 'violated'} (score={score:.2f})",
            details={
                "spec_compliance": compliance,
                "architecture_compliance": arch_compliance.score,
                "type_safety": type_safety.score,
            },
            suggestions=[
                "Improve spec compliance",
                "Fix architecture violations",
                "Add missing type hints",
            ]
            if not passed
            else [],
        )


def measure_specification_drift(spec_v1: str, spec_v2: str) -> float:
    """
    Measure drift between two specification versions.

    Parameters
    ----------
    spec_v1 : str
        Original specification version.
    spec_v2 : str
        New specification version.

    Returns
    -------
    float
        Drift magnitude (0.0 = identical, 1.0 = completely different).

    Example
    -------
    >>> drift = measure_specification_drift(old_spec, new_spec)
    >>> print(f"Specification drift: {drift:.1%}")
    """
    with span("validation.spec_drift"):
        if not spec_v1 or not spec_v2:
            return 1.0

        # Calculate similarity
        similarity = _calculate_text_similarity(spec_v1, spec_v2)

        # Drift is inverse of similarity
        drift = 1.0 - similarity

        metric_histogram("validation.spec_drift", unit="ratio")(drift)
        return drift


def estimate_code_generation_fidelity(spec: str, generated: str) -> float:
    """
    Estimate how accurately code was generated from specification.

    Parameters
    ----------
    spec : str
        Original specification.
    generated : str
        Generated code.

    Returns
    -------
    float
        Fidelity percentage (0.0 to 1.0).

    Example
    -------
    >>> fidelity = estimate_code_generation_fidelity(spec, code)
    >>> print(f"Generation fidelity: {fidelity:.1%}")
    """
    with span("validation.generation_fidelity"):
        # Use spec compliance as fidelity measure
        return verify_spec_compliance(generated, spec)


def identify_drift_sources(spec: str, code: str) -> list[str]:
    """
    Identify sources of drift between spec and code.

    Parameters
    ----------
    spec : str
        Specification text.
    code : str
        Generated code.

    Returns
    -------
    list[str]
        List of identified drift sources.

    Example
    -------
    >>> sources = identify_drift_sources(spec, code)
    >>> for source in sources:
    ...     print(f"Drift source: {source}")
    """
    with span("validation.drift_sources"):
        sources = []

        spec_lower = spec.lower()

        # Extract expected elements from spec
        expected_funcs = re.findall(r"function (\w+)", spec_lower)
        expected_classes = re.findall(r"class (\w+)", spec_lower)

        # Check if present in code
        code_lower = code.lower()

        for func in expected_funcs:
            if func not in code_lower:
                sources.append(f"Missing expected function: {func}()")

        for cls in expected_classes:
            if cls not in code_lower:
                sources.append(f"Missing expected class: {cls}")

        metric_counter("validation.drift_sources")(len(sources))
        return sources


def verify_deterministic_generation(spec: str) -> bool:
    """
    Verify that specification allows deterministic code generation.

    Parameters
    ----------
    spec : str
        Specification text.

    Returns
    -------
    bool
        True if deterministic generation is possible.

    Example
    -------
    >>> is_deterministic = verify_deterministic_generation(spec)
    >>> print(f"Deterministic: {is_deterministic}")
    """
    with span("validation.deterministic_generation"):
        # Check for ambiguity that would prevent determinism
        clarity = measure_specification_clarity(spec)

        # High clarity indicates deterministic potential
        return clarity >= 0.8


def measure_generation_consistency(spec: str) -> float:
    """
    Measure potential consistency of code generation.

    Parameters
    ----------
    spec : str
        Specification text.

    Returns
    -------
    float
        Consistency score (0.0 = inconsistent, 1.0 = highly consistent).

    Example
    -------
    >>> consistency = measure_generation_consistency(spec)
    >>> print(f"Generation consistency: {consistency:.1%}")
    """
    with span("validation.generation_consistency"):
        # Use coherence as consistency proxy
        return measure_coherence(spec)


def identify_non_determinism_sources(generation_log: str) -> list[str]:
    """
    Identify sources of non-determinism in code generation.

    Parameters
    ----------
    generation_log : str
        Log of generation process.

    Returns
    -------
    list[str]
        List of non-determinism sources.

    Example
    -------
    >>> sources = identify_non_determinism_sources(log)
    >>> for source in sources:
    ...     print(f"Non-determinism: {source}")
    """
    with span("validation.non_determinism_sources"):
        sources = []

        log_lower = generation_log.lower()

        # Common non-determinism indicators
        indicators = {
            "random": "Random value generation",
            "uuid": "UUID generation",
            "timestamp": "Timestamp dependency",
            "concurrent": "Concurrent execution",
            "async": "Asynchronous execution",
        }

        for indicator, description in indicators.items():
            if indicator in log_lower:
                sources.append(description)

        return sources


# ============================================================================
# JTBD Outcome Validation
# ============================================================================


def verify_outcome_delivery(feature: str, outcome: str) -> bool:
    """
    Verify if feature delivers expected outcome.

    Parameters
    ----------
    feature : str
        Feature description.
    outcome : str
        Expected outcome description.

    Returns
    -------
    bool
        True if feature likely delivers outcome.

    Example
    -------
    >>> delivers = verify_outcome_delivery(feature_spec, expected_outcome)
    >>> print(f"Outcome delivered: {delivers}")
    """
    with span("validation.outcome_delivery"):
        # Calculate semantic similarity
        similarity = _calculate_text_similarity(feature, outcome)

        # High similarity suggests alignment
        return similarity >= 0.6


def measure_outcome_clarity(outcome: str) -> float:
    """
    Measure how clearly an outcome is defined.

    Parameters
    ----------
    outcome : str
        Outcome description.

    Returns
    -------
    float
        Clarity score (0.0 to 1.0).

    Example
    -------
    >>> clarity = measure_outcome_clarity(outcome)
    >>> print(f"Outcome clarity: {clarity:.1%}")
    """
    with span("validation.outcome_clarity"):
        return measure_specification_clarity(outcome)


def check_success_criteria_completeness(outcome: str) -> float:
    """
    Check completeness of success criteria for outcome.

    Parameters
    ----------
    outcome : str
        Outcome description with success criteria.

    Returns
    -------
    float
        Completeness score (0.0 to 1.0).

    Example
    -------
    >>> completeness = check_success_criteria_completeness(outcome)
    >>> print(f"Success criteria: {completeness:.1%}")
    """
    with span("validation.success_criteria"):
        outcome_lower = outcome.lower()

        # Look for measurable criteria
        criteria_indicators = 0

        # Quantitative measures
        criteria_indicators += len(re.findall(r"\d+", outcome))

        # Success terms
        success_terms = ["success", "complete", "achieve", "deliver", "measure"]
        for term in success_terms:
            if term in outcome_lower:
                criteria_indicators += 1

        # Criteria keywords
        if "criteria" in outcome_lower or "metric" in outcome_lower:
            criteria_indicators += 2

        # Normalize
        word_count = len(outcome.split())
        if word_count == 0:
            return 0.0

        completeness = min(1.0, (criteria_indicators / word_count) * 10)

        metric_histogram("validation.success_criteria", unit="ratio")(completeness)
        return completeness


def estimate_outcome_achievement_likelihood(feature: str) -> float:
    """
    Estimate likelihood of achieving outcome with feature.

    Parameters
    ----------
    feature : str
        Feature description.

    Returns
    -------
    float
        Likelihood estimate (0.0 to 1.0).

    Example
    -------
    >>> likelihood = estimate_outcome_achievement_likelihood(feature)
    >>> print(f"Achievement likelihood: {likelihood:.1%}")
    """
    with span("validation.outcome_likelihood"):
        # Combine multiple factors
        feasibility = assess_implementation_feasibility(feature)
        clarity = measure_specification_clarity(feature)
        completeness = confidence_in_completeness(feature)

        likelihood = feasibility * 0.4 + clarity * 0.3 + completeness * 0.3

        metric_histogram("validation.outcome_likelihood", unit="ratio")(likelihood)
        return likelihood


def measure_job_coverage(job: str, features: list[str]) -> float:
    """
    Measure how much of a job is covered by features.

    Parameters
    ----------
    job : str
        Job description.
    features : list[str]
        List of feature descriptions.

    Returns
    -------
    float
        Coverage percentage (0.0 to 1.0).

    Example
    -------
    >>> coverage = measure_job_coverage(job_spec, all_features)
    >>> print(f"Job coverage: {coverage:.1%}")
    """
    with span("validation.job_coverage"):
        if not features:
            return 0.0

        # Extract job requirements
        job_words = set(job.lower().split())

        # Calculate coverage by feature overlap
        covered_words = set()
        for feature in features:
            feature_words = set(feature.lower().split())
            covered_words.update(job_words & feature_words)

        coverage = len(covered_words) / len(job_words) if job_words else 0.0

        metric_histogram("validation.job_coverage", unit="ratio")(coverage)
        return coverage


def identify_unmet_job_needs(job: str) -> list[str]:
    """
    Identify unmet needs in a job description.

    Parameters
    ----------
    job : str
        Job description.

    Returns
    -------
    list[str]
        List of unmet needs.

    Example
    -------
    >>> needs = identify_unmet_job_needs(job)
    >>> for need in needs:
    ...     print(f"Unmet need: {need}")
    """
    with span("validation.unmet_needs"):
        # Use gap identification as proxy
        return identify_specification_gaps(job)


def validate_feature_job_alignment(feature: str, job: str) -> float:
    """
    Validate alignment between feature and job.

    Parameters
    ----------
    feature : str
        Feature description.
    job : str
        Job description.

    Returns
    -------
    float
        Alignment score (0.0 to 1.0).

    Example
    -------
    >>> alignment = validate_feature_job_alignment(feature, job)
    >>> print(f"Feature-job alignment: {alignment:.1%}")
    """
    with span("validation.feature_job_alignment"):
        # Calculate semantic similarity
        alignment = _calculate_text_similarity(feature, job)

        metric_histogram("validation.feature_job_alignment", unit="ratio")(alignment)
        return alignment


# ============================================================================
# Information Density Analysis
# ============================================================================


def calculate_information_density(spec: str) -> float:
    """
    Calculate information density (useful info per unit).

    Parameters
    ----------
    spec : str
        Specification text.

    Returns
    -------
    float
        Information density (0.0 to 1.0).

    Example
    -------
    >>> density = calculate_information_density(spec)
    >>> print(f"Information density: {density:.1%}")
    """
    with span("validation.information_density_spec"):
        return measure_information_density(spec)


def identify_noise(spec: str) -> list[str]:
    """
    Identify unnecessary complexity/noise in specification.

    Parameters
    ----------
    spec : str
        Specification text.

    Returns
    -------
    list[str]
        List of noise items.

    Example
    -------
    >>> noise = identify_noise(spec)
    >>> for item in noise:
    ...     print(f"Noise: {item}")
    """
    with span("validation.identify_noise"):
        noise = []

        # Redundant phrases
        redundant_patterns = [
            (r"\b(basically|essentially|actually)\b", "Filler word"),
            (r"\b(very|really|quite|rather)\b", "Unnecessary intensifier"),
            (r"\b(it is clear that|obviously|of course)\b", "Assumed clarity"),
        ]

        for pattern, description in redundant_patterns:
            matches = re.findall(pattern, spec, re.IGNORECASE)
            if matches:
                noise.append(f"{description}: {matches[0]}")

        return noise


def suggest_clarifications(spec: str) -> list[str]:
    """
    Suggest clarifications to reduce ambiguity.

    Parameters
    ----------
    spec : str
        Specification text.

    Returns
    -------
    list[str]
        List of clarification suggestions.

    Example
    -------
    >>> suggestions = suggest_clarifications(spec)
    >>> for suggestion in suggestions:
    ...     print(f"Clarify: {suggestion}")
    """
    with span("validation.suggest_clarifications"):
        # Reuse clarifying questions
        return suggest_clarifying_questions(spec)


def estimate_specification_quality(spec: str) -> float:
    """
    Estimate overall specification quality.

    Combines multiple quality metrics.

    Parameters
    ----------
    spec : str
        Specification text.

    Returns
    -------
    float
        Quality score (0.0 to 1.0).

    Example
    -------
    >>> quality = estimate_specification_quality(spec)
    >>> print(f"Specification quality: {quality:.1%}")
    """
    with span("validation.spec_quality"):
        # Combine all quality metrics
        completeness = confidence_in_completeness(spec)
        clarity = measure_specification_clarity(spec)
        coherence = measure_coherence(spec)
        testability = check_testability(spec)

        quality = completeness * 0.3 + clarity * 0.3 + coherence * 0.2 + testability * 0.2

        metric_histogram("validation.spec_quality", unit="ratio")(quality)
        return quality


def measure_semantic_richness(ontology: str) -> float:
    """
    Measure expressiveness of ontology/vocabulary.

    Parameters
    ----------
    ontology : str
        Ontology or vocabulary definition.

    Returns
    -------
    float
        Richness score (0.0 to 1.0).

    Example
    -------
    >>> richness = measure_semantic_richness(ontology_ttl)
    >>> print(f"Semantic richness: {richness:.1%}")
    """
    with span("validation.semantic_richness"):
        # Use entropy as richness measure
        entropy = calculate_specification_entropy(ontology)

        # Normalize entropy to 0-1 range
        richness = min(1.0, entropy / 15.0)

        metric_histogram("validation.semantic_richness", unit="ratio")(richness)
        return richness


def estimate_learning_curve(spec: str) -> float:
    """
    Estimate difficulty to understand specification.

    Parameters
    ----------
    spec : str
        Specification text.

    Returns
    -------
    float
        Learning curve difficulty (0.0 = easy, 1.0 = very difficult).

    Example
    -------
    >>> difficulty = estimate_learning_curve(spec)
    >>> print(f"Learning difficulty: {difficulty:.1%}")
    """
    with span("validation.learning_curve"):
        # Combine complexity indicators
        entropy = calculate_specification_entropy(spec)
        clarity = measure_specification_clarity(spec)

        # High entropy + low clarity = difficult
        difficulty = (entropy / 15.0) * 0.5 + (1.0 - clarity) * 0.5

        metric_histogram("validation.learning_curve", unit="ratio")(difficulty)
        return difficulty


def identify_knowledge_gaps(domain: str) -> list[str]:
    """
    Identify missing concepts in domain knowledge.

    Parameters
    ----------
    domain : str
        Domain description or ontology.

    Returns
    -------
    list[str]
        List of identified knowledge gaps.

    Example
    -------
    >>> gaps = identify_knowledge_gaps(domain_ontology)
    >>> for gap in gaps:
    ...     print(f"Knowledge gap: {gap}")
    """
    with span("validation.knowledge_gaps"):
        # Reuse specification gap identification
        return identify_specification_gaps(domain)


# ============================================================================
# Helper Functions
# ============================================================================


def _calculate_text_similarity(text1: str, text2: str) -> float:
    """
    Calculate Jaccard similarity between two texts.

    Parameters
    ----------
    text1 : str
        First text.
    text2 : str
        Second text.

    Returns
    -------
    float
        Similarity score (0.0 to 1.0).
    """
    # Tokenize
    words1 = set(re.findall(r"\w+", text1.lower()))
    words2 = set(re.findall(r"\w+", text2.lower()))

    if not words1 and not words2:
        return 1.0
    if not words1 or not words2:
        return 0.0

    # Jaccard similarity
    intersection = len(words1 & words2)
    union = len(words1 | words2)

    return intersection / union if union > 0 else 0.0


# ============================================================================
# High-Level Analysis Functions
# ============================================================================


def analyze_specification(spec: str) -> SpecificationAnalysis:
    """
    Perform complete specification analysis.

    Parameters
    ----------
    spec : str
        Specification text to analyze.

    Returns
    -------
    SpecificationAnalysis
        Complete analysis results.

    Example
    -------
    >>> analysis = analyze_specification(spec)
    >>> print(f"Completeness: {analysis.completeness_score:.1%}")
    >>> print(f"Gaps: {len(analysis.gaps)}")
    """
    with span("validation.analyze_specification"):
        return SpecificationAnalysis(
            entropy=calculate_specification_entropy(spec),
            completeness_score=confidence_in_completeness(spec),
            consistency_score=measure_coherence(spec),
            clarity_score=measure_specification_clarity(spec),
            testability_score=check_testability(spec),
            gaps=identify_specification_gaps(spec),
            contradictions=[],  # Would need multiple specs
            questions=suggest_clarifying_questions(spec),
            redundancies=[],  # Would need multiple specs
        )


def analyze_code_quality(code: str, spec: str = "") -> CodeQualityReport:
    """
    Perform complete code quality analysis.

    Parameters
    ----------
    code : str
        Python code to analyze.
    spec : str, optional
        Original specification for compliance checking.

    Returns
    -------
    CodeQualityReport
        Complete quality report.

    Example
    -------
    >>> report = analyze_code_quality(generated_code, spec)
    >>> print(f"Maintainability: {report.maintainability:.1%}")
    >>> print(f"Issues: {len(report.suspicious_patterns)}")
    """
    with span("validation.analyze_code_quality"):
        return CodeQualityReport(
            spec_compliance=verify_spec_compliance(code, spec) if spec else 0.0,
            architecture_compliance=check_architecture_compliance(code).score,
            type_safety=validate_type_safety(code).score,
            test_coverage=measure_test_coverage(code),
            documentation=check_documentation_completeness(code),
            maintainability=assess_maintainability(code),
            entropy=calculate_code_entropy(code),
            information_density=measure_information_density(code),
            suspicious_patterns=identify_suspicious_patterns(code),
            telemetry_gaps=identify_telemetry_gaps(code),
        )


def validate_jtbd_outcome(feature: str, outcome: str, job: str) -> JTBDValidation:
    """
    Validate JTBD outcome delivery.

    Parameters
    ----------
    feature : str
        Feature description.
    outcome : str
        Expected outcome.
    job : str
        Job description.

    Returns
    -------
    JTBDValidation
        JTBD validation results.

    Example
    -------
    >>> validation = validate_jtbd_outcome(feature, outcome, job)
    >>> print(f"Outcome delivered: {validation.outcome_delivered}")
    >>> print(f"Alignment: {validation.alignment_score:.1%}")
    """
    with span("validation.validate_jtbd"):
        return JTBDValidation(
            outcome_delivered=verify_outcome_delivery(feature, outcome),
            outcome_clarity=measure_outcome_clarity(outcome),
            success_criteria_complete=check_success_criteria_completeness(outcome),
            achievement_likelihood=estimate_outcome_achievement_likelihood(feature),
            job_coverage=measure_job_coverage(job, [feature]),
            unmet_needs=identify_unmet_job_needs(job),
            alignment_score=validate_feature_job_alignment(feature, job),
        )
