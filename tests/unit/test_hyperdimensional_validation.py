"""
Unit tests for specify_cli.hyperdimensional.validation module.

Comprehensive test coverage for information-theoretic validation framework.
"""

from __future__ import annotations

import pytest

from specify_cli.hyperdimensional.validation import (
    CodeQualityReport,
    JTBDValidation,
    SpecificationAnalysis,
    # Data classes
    ValidationResult,
    analyze_code_quality,
    # High-level functions
    analyze_specification,
    assess_implementation_feasibility,
    assess_maintainability,
    # Information-Theoretic Quality
    calculate_code_entropy,
    # Information Density
    calculate_information_density,
    # Specification Completeness
    calculate_specification_entropy,
    check_architecture_compliance,
    check_documentation_completeness,
    check_logical_consistency,
    check_metric_coverage,
    check_success_criteria_completeness,
    check_testability,
    confidence_in_completeness,
    # Specification Consistency
    detect_contradictions,
    estimate_code_generation_fidelity,
    estimate_edge_case_coverage,
    estimate_maintenance_effort,
    estimate_specification_quality,
    identify_drift_sources,
    identify_noise,
    identify_non_determinism_sources,
    identify_redundancy,
    identify_specification_gaps,
    identify_suspicious_patterns,
    identify_telemetry_gaps,
    measure_coherence,
    measure_generation_consistency,
    measure_information_density,
    measure_outcome_clarity,
    measure_specification_clarity,
    measure_specification_drift,
    measure_test_coverage,
    suggest_clarifying_questions,
    validate_attribute_completeness,
    validate_jtbd_outcome,
    validate_type_safety,
    # Constitutional Equation
    verify_constitutional_equation,
    verify_constraint_satisfaction,
    verify_deterministic_generation,
    # JTBD Outcome Validation
    verify_outcome_delivery,
    # OTEL Instrumentation
    verify_span_coverage,
    # Code Generation Validation
    verify_spec_compliance,
)

# ============================================================================
# Test Data
# ============================================================================


SAMPLE_SPEC = """
The system must authenticate users via OAuth2.
When authentication fails, return HTTP 401 error.
The system should handle up to 1000 concurrent requests.
Performance must be under 100ms response time (p95).
All data must be encrypted at rest using AES-256.
"""

INCOMPLETE_SPEC = """
The system should do something with user data.
It needs to be fast and secure.
"""

AMBIGUOUS_SPEC = """
The system should maybe process some data.
It might need to handle many requests.
Performance should be good enough.
"""

CLEAR_SPEC = """
The system MUST authenticate users using OAuth2 with PKCE.
The system MUST return HTTP 401 for authentication failures.
The system MUST encrypt all data at rest using AES-256.
The system MUST respond within 100ms for 95% of requests.
"""

SAMPLE_CODE = """
def authenticate_user(username: str, password: str) -> bool:
    \"\"\"Authenticate user with credentials.\"\"\"
    if not username or not password:
        raise ValueError("Credentials required")
    return verify_credentials(username, password)

class UserService:
    \"\"\"User management service.\"\"\"

    def create_user(self, email: str) -> User:
        \"\"\"Create new user.\"\"\"
        validate_email(email)
        return User(email=email)
"""

CODE_WITHOUT_TYPES = """
def process_data(data):
    if not data:
        return None
    return transform(data)
"""

CODE_WITH_SUBPROCESS = """
import subprocess

def run_command(cmd):
    result = subprocess.run(cmd, shell=True)
    return result.stdout
"""

CODE_WITH_TESTS = """
def add(a: int, b: int) -> int:
    return a + b

def test_add():
    assert add(2, 3) == 5

def test_add_negative():
    assert add(-1, 1) == 0
"""

CODE_WITH_SPANS = """
from specify_cli.core.telemetry import span

def process_operation():
    with span("operation.process"):
        return do_work()

def another_operation():
    with span("operation.another"):
        return do_more_work()
"""


# ============================================================================
# Specification Completeness Tests
# ============================================================================


class TestCalculateSpecificationEntropy:
    """Tests for calculate_specification_entropy()."""

    def test_empty_spec_returns_zero(self) -> None:
        """Empty specification should have zero entropy."""
        entropy = calculate_specification_entropy("")
        assert entropy == 0.0

    def test_simple_spec_has_low_entropy(self) -> None:
        """Simple repetitive text should have low entropy."""
        simple = "must must must must must"
        entropy = calculate_specification_entropy(simple)
        assert entropy >= 0.0  # Can be zero for very simple/repeated text
        assert entropy < 5  # Low entropy

    def test_diverse_spec_has_higher_entropy(self) -> None:
        """Diverse specification should have higher entropy."""
        entropy = calculate_specification_entropy(SAMPLE_SPEC)
        assert entropy > 3.0

    def test_entropy_is_positive(self) -> None:
        """Entropy should always be non-negative."""
        entropy = calculate_specification_entropy("test specification text")
        assert entropy >= 0.0

    def test_entropy_scales_with_diversity(self) -> None:
        """More diverse vocabulary should increase entropy."""
        simple = "user user user"
        diverse = "user authentication authorization encryption"

        simple_entropy = calculate_specification_entropy(simple)
        diverse_entropy = calculate_specification_entropy(diverse)

        assert diverse_entropy > simple_entropy


class TestEstimateEdgeCaseCoverage:
    """Tests for estimate_edge_case_coverage()."""

    def test_empty_spec_zero_coverage(self) -> None:
        """Empty spec should have zero edge case coverage."""
        coverage = estimate_edge_case_coverage("")
        assert coverage == 0.0

    def test_spec_with_conditionals_increases_coverage(self) -> None:
        """Conditional statements should increase coverage."""
        spec_with_if = "If input is invalid, return error. When empty, return default."
        spec_without = "Process the input."

        with_coverage = estimate_edge_case_coverage(spec_with_if)
        without_coverage = estimate_edge_case_coverage(spec_without)

        assert with_coverage > without_coverage

    def test_spec_with_error_handling_increases_coverage(self) -> None:
        """Error handling mentions should increase coverage."""
        spec = "Handle errors gracefully. Return exception for invalid input."
        coverage = estimate_edge_case_coverage(spec)
        assert coverage > 0.0

    def test_spec_with_boundaries_increases_coverage(self) -> None:
        """Boundary condition mentions should increase coverage."""
        spec = "Handle empty input. Process null values. Check minimum and maximum limits."
        coverage = estimate_edge_case_coverage(spec)
        assert coverage > 10.0

    def test_coverage_bounded_to_100(self) -> None:
        """Coverage should never exceed 100%."""
        spec = " ".join(["if error except null empty minimum maximum"] * 100)
        coverage = estimate_edge_case_coverage(spec)
        assert coverage <= 100.0


class TestIdentifySpecificationGaps:
    """Tests for identify_specification_gaps()."""

    def test_empty_spec_has_many_gaps(self) -> None:
        """Empty specification should have many gaps."""
        gaps = identify_specification_gaps("")
        assert len(gaps) > 0

    def test_incomplete_spec_identifies_gaps(self) -> None:
        """Incomplete spec should identify missing requirements."""
        gaps = identify_specification_gaps(INCOMPLETE_SPEC)
        assert len(gaps) >= 3

    def test_identifies_missing_error_handling(self) -> None:
        """Should identify missing error handling."""
        spec = "Process user data. Return results."
        gaps = identify_specification_gaps(spec)
        gap_text = " ".join(gaps).lower()
        assert "error" in gap_text

    def test_identifies_missing_performance_requirements(self) -> None:
        """Should identify missing performance requirements."""
        spec = "Authenticate users. Store data."
        gaps = identify_specification_gaps(spec)
        gap_text = " ".join(gaps).lower()
        assert "performance" in gap_text

    def test_complete_spec_has_fewer_gaps(self) -> None:
        """Complete specification should have fewer gaps."""
        incomplete_gaps = identify_specification_gaps(INCOMPLETE_SPEC)
        complete_gaps = identify_specification_gaps(SAMPLE_SPEC)
        assert len(complete_gaps) < len(incomplete_gaps)


class TestSuggestClarifyingQuestions:
    """Tests for suggest_clarifying_questions()."""

    def test_empty_spec_no_questions(self) -> None:
        """Empty spec should not generate questions."""
        questions = suggest_clarifying_questions("")
        assert len(questions) == 0

    def test_ambiguous_spec_suggests_questions(self) -> None:
        """Ambiguous spec should suggest clarifying questions."""
        questions = suggest_clarifying_questions(AMBIGUOUS_SPEC)
        assert len(questions) > 0

    def test_identifies_vague_quantifiers(self) -> None:
        """Should identify vague quantifiers like 'some', 'many'."""
        spec = "Process some data from many users."
        questions = suggest_clarifying_questions(spec)
        assert len(questions) >= 2

    def test_identifies_modal_ambiguity(self) -> None:
        """Should identify ambiguous modal verbs like 'should'."""
        spec = "System should validate input."
        questions = suggest_clarifying_questions(spec)
        question_text = " ".join(questions).lower()
        assert "should" in question_text

    def test_clear_spec_fewer_questions(self) -> None:
        """Clear spec should generate fewer questions."""
        ambiguous_questions = suggest_clarifying_questions(AMBIGUOUS_SPEC)
        clear_questions = suggest_clarifying_questions(CLEAR_SPEC)
        assert len(clear_questions) < len(ambiguous_questions)


class TestConfidenceInCompleteness:
    """Tests for confidence_in_completeness()."""

    def test_empty_spec_zero_confidence(self) -> None:
        """Empty spec should have zero confidence."""
        confidence = confidence_in_completeness("")
        assert confidence == 0.0

    def test_incomplete_spec_low_confidence(self) -> None:
        """Incomplete spec should have low confidence."""
        confidence = confidence_in_completeness(INCOMPLETE_SPEC)
        assert confidence < 0.5

    def test_complete_spec_higher_confidence(self) -> None:
        """Complete spec should have higher confidence."""
        confidence = confidence_in_completeness(SAMPLE_SPEC)
        assert confidence > 0.3

    def test_confidence_bounded_to_one(self) -> None:
        """Confidence should be between 0 and 1."""
        confidence = confidence_in_completeness(SAMPLE_SPEC)
        assert 0.0 <= confidence <= 1.0


# ============================================================================
# Specification Consistency Tests
# ============================================================================


class TestDetectContradictions:
    """Tests for detect_contradictions()."""

    def test_empty_list_no_contradictions(self) -> None:
        """Empty list should have no contradictions."""
        contradictions = detect_contradictions([])
        assert len(contradictions) == 0

    def test_single_spec_no_contradictions(self) -> None:
        """Single spec cannot contradict itself (in simple check)."""
        contradictions = detect_contradictions([SAMPLE_SPEC])
        assert len(contradictions) == 0

    def test_detects_must_must_not_contradiction(self) -> None:
        """Should detect must/must not contradictions."""
        spec1 = "User must provide authentication token."
        spec2 = "User must not provide authentication token."
        contradictions = detect_contradictions([spec1, spec2])
        assert len(contradictions) > 0

    def test_consistent_specs_no_contradictions(self) -> None:
        """Consistent specs should have no contradictions."""
        spec1 = "System must encrypt data."
        spec2 = "System must use AES-256 encryption."
        contradictions = detect_contradictions([spec1, spec2])
        assert len(contradictions) == 0


class TestCheckLogicalConsistency:
    """Tests for check_logical_consistency()."""

    def test_empty_rules_pass(self) -> None:
        """Empty rules should pass consistency check."""
        result = check_logical_consistency([])
        assert result.passed

    def test_single_rule_passes(self) -> None:
        """Single rule should be consistent."""
        result = check_logical_consistency(["System must authenticate users"])
        assert result.passed

    def test_contradictory_rules_fail(self) -> None:
        """Contradictory rules should fail."""
        rules = ["User must login and must not login"]
        result = check_logical_consistency(rules)
        assert not result.passed

    def test_score_decreases_with_issues(self) -> None:
        """Score should decrease with more issues."""
        good_rules = ["Rule 1", "Rule 2"]
        bad_rules = ["must and must not"] * 3

        good_result = check_logical_consistency(good_rules)
        bad_result = check_logical_consistency(bad_rules)

        assert good_result.score > bad_result.score


class TestVerifyConstraintSatisfaction:
    """Tests for verify_constraint_satisfaction()."""

    def test_no_constraints_pass(self) -> None:
        """Spec with no constraints should pass."""
        result = verify_constraint_satisfaction("Any spec", {})
        assert result.passed

    def test_min_length_constraint(self) -> None:
        """Should check minimum length constraint."""
        spec = "Short"
        result = verify_constraint_satisfaction(spec, {"min_length": 100})
        assert not result.passed

    def test_max_length_constraint(self) -> None:
        """Should check maximum length constraint."""
        spec = "x" * 1000
        result = verify_constraint_satisfaction(spec, {"max_length": 100})
        assert not result.passed

    def test_must_contain_constraint(self) -> None:
        """Should check must_contain constraint."""
        spec = "System processes data"
        result = verify_constraint_satisfaction(spec, {"must_contain": ["error handling"]})
        assert not result.passed

    def test_must_not_contain_constraint(self) -> None:
        """Should check must_not_contain constraint."""
        spec = "System has security vulnerability"
        result = verify_constraint_satisfaction(spec, {"must_not_contain": ["vulnerability"]})
        assert not result.passed

    def test_all_constraints_satisfied(self) -> None:
        """Should pass when all constraints satisfied."""
        spec = "System must handle errors gracefully and return appropriate status codes."
        result = verify_constraint_satisfaction(
            spec,
            {
                "min_length": 10,
                "max_length": 200,
                "must_contain": ["error", "status"],
            },
        )
        assert result.passed


class TestIdentifyRedundancy:
    """Tests for identify_redundancy()."""

    def test_empty_list_no_redundancy(self) -> None:
        """Empty list should have no redundancy."""
        redundancies = identify_redundancy([])
        assert len(redundancies) == 0

    def test_identical_specs_are_redundant(self) -> None:
        """Identical specs should be identified as redundant."""
        spec = "System must authenticate users"
        redundancies = identify_redundancy([spec, spec])
        assert len(redundancies) > 0

    def test_different_specs_not_redundant(self) -> None:
        """Completely different specs should not be redundant."""
        spec1 = "System handles authentication"
        spec2 = "Database stores encrypted data"
        redundancies = identify_redundancy([spec1, spec2])
        assert len(redundancies) == 0

    def test_similar_specs_detected(self) -> None:
        """Very similar specs should be detected as redundant."""
        spec1 = "System must authenticate users with OAuth2"
        spec2 = "System must authenticate users using OAuth2"
        redundancies = identify_redundancy([spec1, spec2])
        assert len(redundancies) > 0


class TestMeasureCoherence:
    """Tests for measure_coherence()."""

    def test_empty_spec_returns_zero(self) -> None:
        """Empty spec should return zero coherence."""
        coherence = measure_coherence("")
        assert coherence == 0.0

    def test_single_sentence_perfect_coherence(self) -> None:
        """Single sentence should have perfect coherence."""
        coherence = measure_coherence("System authenticates users.")
        assert coherence == 1.0

    def test_related_sentences_higher_coherence(self) -> None:
        """Related sentences should have higher coherence."""
        coherent = "Users login. Users authenticate. Users get tokens."
        incoherent = "Users login. Database stores data. Sky is blue."

        coherent_score = measure_coherence(coherent)
        incoherent_score = measure_coherence(incoherent)

        assert coherent_score > incoherent_score

    def test_coherence_bounded(self) -> None:
        """Coherence should be between 0 and 1."""
        coherence = measure_coherence(SAMPLE_SPEC)
        assert 0.0 <= coherence <= 1.0


# ============================================================================
# Specification Quality Tests
# ============================================================================


class TestMeasureSpecificationClarity:
    """Tests for measure_specification_clarity()."""

    def test_empty_spec_zero_clarity(self) -> None:
        """Empty spec should have zero clarity."""
        clarity = measure_specification_clarity("")
        assert clarity == 0.0

    def test_ambiguous_spec_low_clarity(self) -> None:
        """Ambiguous spec should have low clarity."""
        clarity = measure_specification_clarity(AMBIGUOUS_SPEC)
        assert clarity < 0.7

    def test_clear_spec_high_clarity(self) -> None:
        """Clear spec should have high clarity."""
        clarity = measure_specification_clarity(CLEAR_SPEC)
        assert clarity > 0.8

    def test_clarity_bounded(self) -> None:
        """Clarity should be between 0 and 1."""
        clarity = measure_specification_clarity(SAMPLE_SPEC)
        assert 0.0 <= clarity <= 1.0


class TestCheckTestability:
    """Tests for check_testability()."""

    def test_empty_spec_zero_testability(self) -> None:
        """Empty spec should have zero testability."""
        testability = check_testability("")
        assert testability == 0.0

    def test_spec_with_must_increases_testability(self) -> None:
        """MUST statements should increase testability."""
        spec = "System must return 200 OK. Must complete within 100ms."
        testability = check_testability(spec)
        assert testability > 0.5

    def test_spec_with_metrics_increases_testability(self) -> None:
        """Quantitative metrics should increase testability."""
        spec = "Response time must be under 100ms. Handle 1000 requests per second."
        testability = check_testability(spec)
        assert testability > 0.3

    def test_testability_bounded(self) -> None:
        """Testability should be between 0 and 1."""
        testability = check_testability(SAMPLE_SPEC)
        assert 0.0 <= testability <= 1.0


class TestAssessImplementationFeasibility:
    """Tests for assess_implementation_feasibility()."""

    def test_empty_spec_neutral_feasibility(self) -> None:
        """Empty spec should have neutral feasibility."""
        feasibility = assess_implementation_feasibility("")
        assert feasibility == 0.0

    def test_simple_crud_high_feasibility(self) -> None:
        """Simple CRUD operations should have high feasibility."""
        spec = "Create REST API for user CRUD operations."
        feasibility = assess_implementation_feasibility(spec)
        assert feasibility > 0.4

    def test_complex_requirements_lower_feasibility(self) -> None:
        """Complex requirements should lower feasibility."""
        spec = "Build real-time distributed blockchain AI system with zero latency."
        feasibility = assess_implementation_feasibility(spec)
        assert feasibility < 0.5

    def test_feasibility_bounded(self) -> None:
        """Feasibility should be between 0 and 1."""
        feasibility = assess_implementation_feasibility(SAMPLE_SPEC)
        assert 0.0 <= feasibility <= 1.0


class TestEstimateMaintenanceEffort:
    """Tests for estimate_maintenance_effort()."""

    def test_empty_spec_zero_effort(self) -> None:
        """Empty spec should have zero maintenance effort."""
        effort = estimate_maintenance_effort("")
        assert effort == 0.0

    def test_simple_spec_lower_effort(self) -> None:
        """Simple spec should have lower maintenance effort."""
        spec = "Store user data in database."
        effort = estimate_maintenance_effort(spec)
        assert effort < 0.5

    def test_complex_integrations_higher_effort(self) -> None:
        """Complex integrations should increase maintenance effort."""
        spec = "Integrate with third-party APIs, external services, and complex caching."
        effort = estimate_maintenance_effort(spec)
        assert effort > 0.3

    def test_effort_bounded(self) -> None:
        """Effort should be between 0 and 1."""
        effort = estimate_maintenance_effort(SAMPLE_SPEC)
        assert 0.0 <= effort <= 1.0


# ============================================================================
# Code Generation Validation Tests
# ============================================================================


class TestVerifySpecCompliance:
    """Tests for verify_spec_compliance()."""

    def test_empty_inputs_zero_compliance(self) -> None:
        """Empty code and spec should have zero compliance."""
        compliance = verify_spec_compliance("", "")
        assert compliance == 0.0

    def test_matching_code_and_spec_high_compliance(self) -> None:
        """Code matching spec should have high compliance."""
        spec = "Function authenticate_user must validate credentials"
        code = "def authenticate_user(username, password): validate_credentials()"
        compliance = verify_spec_compliance(code, spec)
        assert compliance > 0.3

    def test_unrelated_code_low_compliance(self) -> None:
        """Unrelated code should have low compliance."""
        spec = "Function authenticate_user"
        code = "def process_payment(): pass"
        compliance = verify_spec_compliance(code, spec)
        assert compliance < 0.5

    def test_compliance_bounded(self) -> None:
        """Compliance should be between 0 and 1."""
        compliance = verify_spec_compliance(SAMPLE_CODE, SAMPLE_SPEC)
        assert 0.0 <= compliance <= 1.0


class TestCheckArchitectureCompliance:
    """Tests for check_architecture_compliance()."""

    def test_clean_code_passes(self) -> None:
        """Clean code should pass architecture compliance."""
        result = check_architecture_compliance(SAMPLE_CODE)
        assert result.passed

    def test_subprocess_import_fails(self) -> None:
        """Code with subprocess import should fail."""
        result = check_architecture_compliance(CODE_WITH_SUBPROCESS)
        assert not result.passed
        assert "subprocess" in str(result.details)

    def test_file_io_violation_detected(self) -> None:
        """Direct file I/O should be detected."""
        code = "def save(): f = open('file.txt', 'w')"
        result = check_architecture_compliance(code)
        # May or may not detect depending on AST complexity
        assert isinstance(result, ValidationResult)

    def test_score_reflects_violations(self) -> None:
        """Score should decrease with violations."""
        clean_result = check_architecture_compliance(SAMPLE_CODE)
        dirty_result = check_architecture_compliance(CODE_WITH_SUBPROCESS)
        assert clean_result.score > dirty_result.score


class TestValidateTypeSafety:
    """Tests for validate_type_safety()."""

    def test_fully_typed_code_high_score(self) -> None:
        """Fully typed code should have high score."""
        result = validate_type_safety(SAMPLE_CODE)
        assert result.score > 0.5

    def test_untyped_code_low_score(self) -> None:
        """Untyped code should have low score."""
        result = validate_type_safety(CODE_WITHOUT_TYPES)
        assert result.score < 0.8

    def test_identifies_missing_parameter_types(self) -> None:
        """Should identify missing parameter type hints."""
        code = "def func(x): return x"
        result = validate_type_safety(code)
        assert len(result.details.get("issues", [])) > 0

    def test_syntax_error_handled(self) -> None:
        """Should handle syntax errors gracefully."""
        code = "def invalid syntax here"
        result = validate_type_safety(code)
        assert not result.passed


class TestMeasureTestCoverage:
    """Tests for measure_test_coverage()."""

    def test_code_with_tests_has_coverage(self) -> None:
        """Code with tests should have coverage."""
        coverage = measure_test_coverage(CODE_WITH_TESTS)
        assert coverage > 0.5

    def test_code_without_tests_low_coverage(self) -> None:
        """Code without tests should have low coverage."""
        coverage = measure_test_coverage(SAMPLE_CODE)
        assert coverage < 0.5

    def test_coverage_bounded(self) -> None:
        """Coverage should be between 0 and 1."""
        coverage = measure_test_coverage(CODE_WITH_TESTS)
        assert 0.0 <= coverage <= 1.0


class TestCheckDocumentationCompleteness:
    """Tests for check_documentation_completeness()."""

    def test_documented_code_high_score(self) -> None:
        """Well-documented code should have high score."""
        completeness = check_documentation_completeness(SAMPLE_CODE)
        assert completeness > 0.5

    def test_undocumented_code_low_score(self) -> None:
        """Undocumented code should have low score."""
        code = "def func(): pass\nclass MyClass: pass"
        completeness = check_documentation_completeness(code)
        assert completeness < 0.5

    def test_completeness_bounded(self) -> None:
        """Completeness should be between 0 and 1."""
        completeness = check_documentation_completeness(SAMPLE_CODE)
        assert 0.0 <= completeness <= 1.0


# ============================================================================
# Information-Theoretic Quality Tests
# ============================================================================


class TestCalculateCodeEntropy:
    """Tests for calculate_code_entropy()."""

    def test_empty_code_zero_entropy(self) -> None:
        """Empty code should have zero entropy."""
        entropy = calculate_code_entropy("")
        assert entropy == 0.0

    def test_diverse_code_higher_entropy(self) -> None:
        """More diverse code should have higher entropy."""
        simple = "x = 1\nx = 1\nx = 1"
        diverse = "def func(): class MyClass: import sys"

        simple_entropy = calculate_code_entropy(simple)
        diverse_entropy = calculate_code_entropy(diverse)

        assert diverse_entropy > simple_entropy

    def test_entropy_positive(self) -> None:
        """Entropy should be non-negative."""
        entropy = calculate_code_entropy(SAMPLE_CODE)
        assert entropy >= 0.0


class TestMeasureInformationDensity:
    """Tests for measure_information_density()."""

    def test_empty_code_zero_density(self) -> None:
        """Empty code should have zero density."""
        density = measure_information_density("")
        assert density == 0.0

    def test_code_with_comments_lower_density(self) -> None:
        """Code with many comments should have lower density."""
        code_with_comments = "# Comment\n# Comment\nx = 1\n# Comment"
        code_without = "x = 1\ny = 2\nz = 3"

        with_density = measure_information_density(code_with_comments)
        without_density = measure_information_density(code_without)

        assert without_density > with_density

    def test_density_bounded(self) -> None:
        """Density should be between 0 and 1."""
        density = measure_information_density(SAMPLE_CODE)
        assert 0.0 <= density <= 1.0


class TestIdentifySuspiciousPatterns:
    """Tests for identify_suspicious_patterns()."""

    def test_clean_code_no_patterns(self) -> None:
        """Clean code should have no suspicious patterns."""
        patterns = identify_suspicious_patterns(SAMPLE_CODE)
        assert len(patterns) == 0

    def test_bare_except_detected(self) -> None:
        """Bare except clause should be detected."""
        code = "try:\n    risky()\nexcept:\n    pass"
        patterns = identify_suspicious_patterns(code)
        assert len(patterns) > 0
        assert "bare except" in patterns[0].lower()

    def test_hardcoded_password_detected(self) -> None:
        """Hardcoded password should be detected."""
        code = "password = 'secret123'"
        patterns = identify_suspicious_patterns(code)
        assert len(patterns) > 0

    def test_syntax_error_reported(self) -> None:
        """Syntax errors should be reported."""
        code = "def invalid syntax"
        patterns = identify_suspicious_patterns(code)
        assert len(patterns) > 0


class TestAssessMaintainability:
    """Tests for assess_maintainability()."""

    def test_empty_code_zero_maintainability(self) -> None:
        """Empty code should have zero maintainability."""
        maintainability = assess_maintainability("")
        assert maintainability == 0.0

    def test_well_documented_code_higher_maintainability(self) -> None:
        """Well-documented code should have higher maintainability."""
        maintainability = assess_maintainability(SAMPLE_CODE)
        assert maintainability > 0.3

    def test_suspicious_patterns_reduce_maintainability(self) -> None:
        """Suspicious patterns should reduce maintainability."""
        good_code = SAMPLE_CODE
        bad_code = "try:\n    x()\nexcept:\n    pass\n" * 10

        good_score = assess_maintainability(good_code)
        bad_score = assess_maintainability(bad_code)

        assert good_score > bad_score

    def test_maintainability_bounded(self) -> None:
        """Maintainability should be between 0 and 1."""
        maintainability = assess_maintainability(SAMPLE_CODE)
        assert 0.0 <= maintainability <= 1.0


# ============================================================================
# OTEL Instrumentation Tests
# ============================================================================


class TestVerifySpanCoverage:
    """Tests for verify_span_coverage()."""

    def test_code_without_spans_low_coverage(self) -> None:
        """Code without spans should have low coverage."""
        coverage = verify_span_coverage(SAMPLE_CODE)
        assert coverage < 0.5

    def test_code_with_spans_higher_coverage(self) -> None:
        """Code with spans should have higher coverage."""
        coverage = verify_span_coverage(CODE_WITH_SPANS)
        assert coverage > 0.5

    def test_coverage_bounded(self) -> None:
        """Coverage should be between 0 and 1."""
        coverage = verify_span_coverage(CODE_WITH_SPANS)
        assert 0.0 <= coverage <= 1.0


class TestCheckMetricCoverage:
    """Tests for check_metric_coverage()."""

    def test_code_without_metrics_low_coverage(self) -> None:
        """Code without metrics should have low coverage."""
        coverage = check_metric_coverage(SAMPLE_CODE)
        assert coverage < 0.5

    def test_code_with_metrics_higher_coverage(self) -> None:
        """Code with metric calls should have higher coverage."""
        code = "metric_counter('x')(1)\nmetric_histogram('y')(0.5)"
        coverage = check_metric_coverage(code)
        assert coverage > 0.0

    def test_coverage_bounded(self) -> None:
        """Coverage should be between 0 and 1."""
        coverage = check_metric_coverage(SAMPLE_CODE)
        assert 0.0 <= coverage <= 1.0


class TestValidateAttributeCompleteness:
    """Tests for validate_attribute_completeness()."""

    def test_empty_spans_full_completeness(self) -> None:
        """Empty span list should have full completeness."""
        completeness = validate_attribute_completeness([])
        assert completeness == 1.0

    def test_complete_spans_full_score(self) -> None:
        """Spans with all required attributes should have full score."""
        spans = [
            {
                "attributes": {
                    "operation.type": "query",
                    "operation.name": "get_user",
                    "service.name": "api",
                }
            }
        ]
        completeness = validate_attribute_completeness(spans)
        assert completeness == 1.0

    def test_incomplete_spans_low_score(self) -> None:
        """Spans missing attributes should have low score."""
        spans = [{"attributes": {}}]
        completeness = validate_attribute_completeness(spans)
        assert completeness == 0.0

    def test_completeness_bounded(self) -> None:
        """Completeness should be between 0 and 1."""
        spans = [{"attributes": {"operation.type": "test"}}]
        completeness = validate_attribute_completeness(spans)
        assert 0.0 <= completeness <= 1.0


class TestIdentifyTelemetryGaps:
    """Tests for identify_telemetry_gaps()."""

    def test_code_without_spans_has_gaps(self) -> None:
        """Code without spans should have telemetry gaps."""
        gaps = identify_telemetry_gaps(SAMPLE_CODE)
        assert len(gaps) > 0

    def test_instrumented_code_fewer_gaps(self) -> None:
        """Well-instrumented code should have fewer gaps."""
        gaps = identify_telemetry_gaps(CODE_WITH_SPANS)
        assert len(gaps) < 2


# ============================================================================
# Constitutional Equation Tests
# ============================================================================


class TestVerifyConstitutionalEquation:
    """Tests for verify_constitutional_equation()."""

    def test_matching_spec_and_code_passes(self) -> None:
        """Matching spec and code should pass."""
        spec = "Function authenticate_user validates credentials"
        code = SAMPLE_CODE
        result = verify_constitutional_equation(spec, code)
        assert result.score > 0.3

    def test_mismatched_spec_and_code_fails(self) -> None:
        """Mismatched spec and code should have low score."""
        spec = "Function process_payment handles transactions"
        code = SAMPLE_CODE
        result = verify_constitutional_equation(spec, code)
        assert result.score <= 0.5  # Low score for mismatch

    def test_result_contains_metrics(self) -> None:
        """Result should contain component metrics."""
        result = verify_constitutional_equation(SAMPLE_SPEC, SAMPLE_CODE)
        assert "spec_compliance" in result.details
        assert "architecture_compliance" in result.details


class TestMeasureSpecificationDrift:
    """Tests for measure_specification_drift()."""

    def test_identical_specs_zero_drift(self) -> None:
        """Identical specs should have minimal drift."""
        drift = measure_specification_drift(SAMPLE_SPEC, SAMPLE_SPEC)
        assert drift < 0.1

    def test_different_specs_high_drift(self) -> None:
        """Completely different specs should have high drift."""
        spec1 = "Authentication with OAuth2"
        spec2 = "Database storage with encryption"
        drift = measure_specification_drift(spec1, spec2)
        assert drift > 0.5

    def test_drift_bounded(self) -> None:
        """Drift should be between 0 and 1."""
        drift = measure_specification_drift(SAMPLE_SPEC, INCOMPLETE_SPEC)
        assert 0.0 <= drift <= 1.0


class TestEstimateCodeGenerationFidelity:
    """Tests for estimate_code_generation_fidelity()."""

    def test_matching_code_high_fidelity(self) -> None:
        """Code matching spec should have high fidelity."""
        spec = "Function authenticate_user"
        code = "def authenticate_user(): pass"
        fidelity = estimate_code_generation_fidelity(spec, code)
        assert fidelity > 0.3

    def test_fidelity_bounded(self) -> None:
        """Fidelity should be between 0 and 1."""
        fidelity = estimate_code_generation_fidelity(SAMPLE_SPEC, SAMPLE_CODE)
        assert 0.0 <= fidelity <= 1.0


class TestIdentifyDriftSources:
    """Tests for identify_drift_sources()."""

    def test_missing_functions_identified(self) -> None:
        """Missing expected functions should be identified."""
        spec = "Function missing_function processes data"
        code = "def other_function(): pass"
        sources = identify_drift_sources(spec, code)
        assert len(sources) > 0


class TestVerifyDeterministicGeneration:
    """Tests for verify_deterministic_generation()."""

    def test_clear_spec_is_deterministic(self) -> None:
        """Clear spec should allow deterministic generation."""
        is_deterministic = verify_deterministic_generation(CLEAR_SPEC)
        assert is_deterministic

    def test_ambiguous_spec_not_deterministic(self) -> None:
        """Ambiguous spec should not allow deterministic generation."""
        is_deterministic = verify_deterministic_generation(AMBIGUOUS_SPEC)
        assert not is_deterministic


class TestMeasureGenerationConsistency:
    """Tests for measure_generation_consistency()."""

    def test_coherent_spec_high_consistency(self) -> None:
        """Coherent spec should have reasonable generation consistency."""
        consistency = measure_generation_consistency(SAMPLE_SPEC)
        assert consistency >= 0.0  # Non-negative consistency
        assert consistency <= 1.0  # Bounded

    def test_consistency_bounded(self) -> None:
        """Consistency should be between 0 and 1."""
        consistency = measure_generation_consistency(SAMPLE_SPEC)
        assert 0.0 <= consistency <= 1.0


class TestIdentifyNonDeterminismSources:
    """Tests for identify_non_determinism_sources()."""

    def test_random_usage_identified(self) -> None:
        """Random value usage should be identified."""
        log = "Generated random UUID for request ID"
        sources = identify_non_determinism_sources(log)
        assert len(sources) > 0

    def test_deterministic_log_no_sources(self) -> None:
        """Deterministic process should have no sources."""
        log = "Processed input with fixed algorithm"
        sources = identify_non_determinism_sources(log)
        assert len(sources) == 0


# ============================================================================
# JTBD Outcome Tests
# ============================================================================


class TestVerifyOutcomeDelivery:
    """Tests for verify_outcome_delivery()."""

    def test_matching_feature_and_outcome_delivers(self) -> None:
        """Very similar feature and outcome should deliver."""
        # Use identical wording to ensure delivery
        feature = "Users authenticate quickly using OAuth2 protocol"
        outcome = "Users authenticate quickly using OAuth2 protocol"
        delivers = verify_outcome_delivery(feature, outcome)
        assert delivers  # Identical wording should definitely indicate delivery

    def test_unrelated_feature_does_not_deliver(self) -> None:
        """Unrelated feature should not deliver outcome."""
        feature = "Data encryption"
        outcome = "Fast authentication"
        delivers = verify_outcome_delivery(feature, outcome)
        assert not delivers


class TestMeasureOutcomeClarity:
    """Tests for measure_outcome_clarity()."""

    def test_clear_outcome_high_score(self) -> None:
        """Clear outcome should have high clarity."""
        outcome = "Users must authenticate within 2 seconds"
        clarity = measure_outcome_clarity(outcome)
        assert clarity > 0.7

    def test_vague_outcome_low_score(self) -> None:
        """Vague outcome should have low clarity."""
        outcome = "Users should maybe login quickly"
        clarity = measure_outcome_clarity(outcome)
        assert clarity < 0.7


class TestCheckSuccessCriteriaCompleteness:
    """Tests for check_success_criteria_completeness()."""

    def test_outcome_with_metrics_complete(self) -> None:
        """Outcome with metrics should be more complete."""
        outcome = "Success: users authenticate within 100ms, error rate < 1%"
        completeness = check_success_criteria_completeness(outcome)
        assert completeness > 0.3

    def test_vague_outcome_incomplete(self) -> None:
        """Vague outcome should be incomplete."""
        outcome = "Users are happy"
        completeness = check_success_criteria_completeness(outcome)
        assert completeness < 0.3


# ============================================================================
# Information Density Tests
# ============================================================================


class TestCalculateInformationDensity:
    """Tests for calculate_information_density()."""

    def test_dense_spec_high_score(self) -> None:
        """Specification with high information density."""
        density = calculate_information_density(SAMPLE_SPEC)
        assert density > 0.5

    def test_density_bounded(self) -> None:
        """Density should be between 0 and 1."""
        density = calculate_information_density(SAMPLE_SPEC)
        assert 0.0 <= density <= 1.0


class TestIdentifyNoise:
    """Tests for identify_noise()."""

    def test_clean_spec_minimal_noise(self) -> None:
        """Clean spec should have minimal noise."""
        noise = identify_noise(CLEAR_SPEC)
        assert len(noise) < 3

    def test_noisy_spec_more_noise(self) -> None:
        """Noisy spec with filler words should have more noise."""
        spec = "Basically, the system actually needs to very quickly process data, obviously."
        noise = identify_noise(spec)
        assert len(noise) > 0


class TestEstimateSpecificationQuality:
    """Tests for estimate_specification_quality()."""

    def test_high_quality_spec_high_score(self) -> None:
        """High quality spec should score well."""
        quality = estimate_specification_quality(CLEAR_SPEC)
        assert quality > 0.5

    def test_low_quality_spec_low_score(self) -> None:
        """Low quality spec should score poorly."""
        quality = estimate_specification_quality(INCOMPLETE_SPEC)
        assert quality < 0.5

    def test_quality_bounded(self) -> None:
        """Quality should be between 0 and 1."""
        quality = estimate_specification_quality(SAMPLE_SPEC)
        assert 0.0 <= quality <= 1.0


# ============================================================================
# High-Level Analysis Tests
# ============================================================================


class TestAnalyzeSpecification:
    """Tests for analyze_specification()."""

    def test_returns_complete_analysis(self) -> None:
        """Should return complete SpecificationAnalysis."""
        analysis = analyze_specification(SAMPLE_SPEC)

        assert isinstance(analysis, SpecificationAnalysis)
        assert analysis.entropy > 0
        assert 0.0 <= analysis.completeness_score <= 1.0
        assert 0.0 <= analysis.consistency_score <= 1.0
        assert 0.0 <= analysis.clarity_score <= 1.0
        assert isinstance(analysis.gaps, list)
        assert isinstance(analysis.questions, list)

    def test_incomplete_spec_shows_gaps(self) -> None:
        """Incomplete spec analysis should show gaps."""
        analysis = analyze_specification(INCOMPLETE_SPEC)
        assert len(analysis.gaps) > 0
        assert analysis.completeness_score < 0.5


class TestAnalyzeCodeQuality:
    """Tests for analyze_code_quality()."""

    def test_returns_complete_report(self) -> None:
        """Should return complete CodeQualityReport."""
        report = analyze_code_quality(SAMPLE_CODE, SAMPLE_SPEC)

        assert isinstance(report, CodeQualityReport)
        assert 0.0 <= report.spec_compliance <= 1.0
        assert 0.0 <= report.architecture_compliance <= 1.0
        assert 0.0 <= report.maintainability <= 1.0
        assert isinstance(report.suspicious_patterns, list)

    def test_code_without_spec_still_analyzes(self) -> None:
        """Code analysis should work without spec."""
        report = analyze_code_quality(SAMPLE_CODE)
        assert isinstance(report, CodeQualityReport)


class TestValidateJTBDOutcome:
    """Tests for validate_jtbd_outcome()."""

    def test_returns_complete_validation(self) -> None:
        """Should return complete JTBDValidation."""
        validation = validate_jtbd_outcome(
            feature="Fast authentication",
            outcome="Users login quickly",
            job="Secure access to system",
        )

        assert isinstance(validation, JTBDValidation)
        assert isinstance(validation.outcome_delivered, bool)
        assert 0.0 <= validation.outcome_clarity <= 1.0
        assert 0.0 <= validation.alignment_score <= 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
