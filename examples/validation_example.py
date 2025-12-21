#!/usr/bin/env python3
"""
Example usage of validation_core module.

Demonstrates the 80/20 validation approach:
1. Check spec completeness
2. Check code-to-spec fidelity
3. Check architecture compliance
"""

from specify_cli.hyperdimensional.validation_core import (
    check_architecture_compliance,
    check_code_fidelity,
    check_spec_completeness,
    estimate_edge_case_coverage,
    identify_specification_gaps,
    quick_spec_metrics,
    validate_specification,
)

# Example specifications
SHORT_SPEC = "System authenticates users."

MEDIUM_SPEC = """
The system must authenticate users via OAuth2.
Authentication failures return HTTP 401.
Response time must be under 100ms (p95).
"""

COMPLETE_SPEC = """
The system MUST authenticate users using OAuth2 with PKCE flow.

Requirements:
- Authentication failures MUST return HTTP 401 with error details
- Response time MUST be under 100ms for 95% of requests
- All data MUST be encrypted at rest using AES-256
- System MUST handle up to 1000 concurrent requests
- Invalid tokens MUST be rejected with clear error messages

Error Handling:
- Handle network timeouts with retry logic (max 3 retries)
- Handle invalid credentials gracefully
- Handle empty or null input parameters

Edge Cases:
- Empty username or password
- Expired tokens
- Malformed authentication headers
- Rate limiting (max 10 requests/second per user)

Testing:
- Unit tests for authentication logic
- Integration tests for OAuth2 flow
- Load tests for concurrent requests

Performance:
- Target: 50ms average response time
- Maximum: 100ms p95 response time
"""

# Example code
GOOD_CODE = """
def authenticate_user(username: str, password: str) -> dict:
    '''Authenticate user with OAuth2 credentials.'''
    if not username or not password:
        raise ValueError("Credentials required")

    # Call OAuth2 service
    token = oauth2_authenticate(username, password)
    return {"token": token, "user": username}
"""

BAD_CODE = """
import subprocess

def run_command(cmd: str) -> str:
    # BAD: shell=True is a security risk
    result = subprocess.run(cmd, shell=True, capture_output=True)
    return result.stdout.decode()

# BAD: Hardcoded password
password = "secret123"
"""


def example_1_spec_completeness() -> None:
    """Example 1: Check specification completeness."""
    print("=" * 60)
    print("EXAMPLE 1: Spec Completeness")
    print("=" * 60)

    specs = {
        "Short": SHORT_SPEC,
        "Medium": MEDIUM_SPEC,
        "Complete": COMPLETE_SPEC,
    }

    for name, spec in specs.items():
        score = check_spec_completeness(spec)
        print(f"\n{name} spec:")
        print(f"  Word count: {len(spec.split())}")
        print(f"  Completeness: {score:.2%}")

        if score < 0.3:
            print(f"  ⚠️  Too short - needs more detail")
        elif score < 0.5:
            print(f"  ⚠️  Could be more detailed")
        else:
            print(f"  ✅ Good completeness")


def example_2_code_fidelity() -> None:
    """Example 2: Check code-to-spec fidelity."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Code Fidelity")
    print("=" * 60)

    spec = "authenticate user using OAuth2 credentials and return token"

    codes = {
        "Good": GOOD_CODE,
        "Mismatched": "def process_payment(): return charge_card()",
    }

    for name, code in codes.items():
        fidelity = check_code_fidelity(spec, code)
        print(f"\n{name} code:")
        print(f"  Fidelity: {fidelity:.2%}")

        if fidelity < 0.3:
            print(f"  ❌ Code doesn't match spec")
        elif fidelity < 0.5:
            print(f"  ⚠️  Partial match")
        else:
            print(f"  ✅ Good match")


def example_3_architecture_compliance() -> None:
    """Example 3: Check architecture compliance."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Architecture Compliance")
    print("=" * 60)

    codes = {
        "Good": GOOD_CODE,
        "Bad (security issues)": BAD_CODE,
    }

    for name, code in codes.items():
        compliant = check_architecture_compliance(code)
        print(f"\n{name}:")
        print(f"  Compliant: {compliant}")

        if compliant:
            print(f"  ✅ Architecture OK")
        else:
            print(f"  ❌ Architecture violations detected")


def example_4_edge_cases() -> None:
    """Example 4: Check edge case coverage."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Edge Case Coverage")
    print("=" * 60)

    coverage = estimate_edge_case_coverage(COMPLETE_SPEC)
    print(f"\nComplete spec edge case coverage: {coverage:.0f}%")

    if coverage < 30:
        print("  ⚠️  Low edge case coverage")
    elif coverage < 60:
        print("  ⚠️  Medium edge case coverage")
    else:
        print("  ✅ Good edge case coverage")


def example_5_identify_gaps() -> None:
    """Example 5: Identify specification gaps."""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Specification Gaps")
    print("=" * 60)

    gaps = identify_specification_gaps(MEDIUM_SPEC)
    print(f"\nGaps found in medium spec: {len(gaps)}")

    for gap in gaps:
        print(f"  - {gap}")

    print("\nComplete spec gaps:")
    complete_gaps = identify_specification_gaps(COMPLETE_SPEC)
    print(f"  Gaps found: {len(complete_gaps)}")

    if complete_gaps:
        for gap in complete_gaps:
            print(f"  - {gap}")
    else:
        print("  ✅ No gaps detected")


def example_6_quick_metrics() -> None:
    """Example 6: Get quick metrics."""
    print("\n" + "=" * 60)
    print("EXAMPLE 6: Quick Metrics")
    print("=" * 60)

    metrics = quick_spec_metrics(COMPLETE_SPEC)

    print(f"\nMetrics for complete spec:")
    print(f"  Word count: {metrics['word_count']}")
    print(f"  Completeness: {metrics['completeness']:.2%}")
    print(f"  Edge coverage: {metrics['edge_coverage']:.2%}")
    print(f"  Has MUST statements: {metrics['has_must_statements']}")
    print(f"  Has SHALL statements: {metrics['has_shall_statements']}")
    print(f"  Gaps: {len(metrics['gaps'])}")


def example_7_full_validation() -> None:
    """Example 7: Full validation report."""
    print("\n" + "=" * 60)
    print("EXAMPLE 7: Full Validation Report")
    print("=" * 60)

    # Good example
    print("\n--- Good Spec + Good Code ---")
    report = validate_specification(COMPLETE_SPEC, GOOD_CODE)

    print(f"Completeness: {report.completeness_score:.2%}")
    print(f"Fidelity: {report.fidelity_score:.2%}")
    print(f"Architecture OK: {report.architecture_ok}")
    print(f"Issues: {len(report.issues)}")

    if report.issues:
        for issue in report.issues:
            print(f"  - {issue}")

    if report.recommendations:
        print(f"Recommendations:")
        for rec in report.recommendations:
            print(f"  - {rec}")

    # Bad example
    print("\n--- Short Spec + Bad Code ---")
    report = validate_specification(SHORT_SPEC, BAD_CODE)

    print(f"Completeness: {report.completeness_score:.2%}")
    print(f"Fidelity: {report.fidelity_score:.2%}")
    print(f"Architecture OK: {report.architecture_ok}")
    print(f"Issues: {len(report.issues)}")

    if report.issues:
        for issue in report.issues:
            print(f"  - {issue}")

    if report.recommendations:
        print(f"Recommendations:")
        for rec in report.recommendations:
            print(f"  - {rec}")


if __name__ == "__main__":
    example_1_spec_completeness()
    example_2_code_fidelity()
    example_3_architecture_compliance()
    example_4_edge_cases()
    example_5_identify_gaps()
    example_6_quick_metrics()
    example_7_full_validation()

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)
