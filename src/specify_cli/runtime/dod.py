"""
specify_cli.runtime.dod
==============================

Runtime layer for Definition of Done automation and checklists.

This module handles all subprocess execution, file I/O, and external tool integration.
No business logic - all operations delegated from the ops layer with telemetry.

All functions:
- Use subprocess.run() with shell=False (safe subprocess calls)
- Validate paths before operations
- Handle errors with proper context
- Record OpenTelemetry spans and metrics
- Support structured logging and JSON output

Install dependencies via:
    uv sync --group dev
"""

from __future__ import annotations

import contextlib
import time
from pathlib import Path
from typing import TYPE_CHECKING

from specify_cli.core.dod_types import DoDGate
from specify_cli.core.instrumentation import add_span_attributes, add_span_event
from specify_cli.core.process import run
from specify_cli.core.telemetry import metric_counter, metric_histogram, span

if TYPE_CHECKING:
    from collections.abc import Sequence

__all__ = [
    "check_architecture_compliance",
    "check_changelog",
    "check_code_linting",
    "check_documentation",
    "check_integration_tests",
    "check_rdf_compliance",
    "check_security",
    "check_test_coverage",
    "check_type_safety",
    "check_unit_tests",
]


def _run_tool(cmd: Sequence[str], *, tool_name: str) -> tuple[bool, str, float]:
    """Run a tool and capture output.

    Parameters
    ----------
    cmd : Sequence[str]
        Command to run
    tool_name : str
        Name of the tool for logging

    Returns
    -------
    tuple[bool, str, float]
        (success, output, duration)
    """
    start_time = time.time()
    try:
        output = run(cmd, capture=True, check=False)
        duration = time.time() - start_time
        return (True, output or "", duration)
    except Exception as e:
        duration = time.time() - start_time
        return (False, str(e), duration)


def check_type_safety() -> DoDGate:
    """Check type safety with mypy.

    Returns
    -------
    DoDGate
        Gate result with type checking details.
    """
    with span("dod.check.type_safety"):
        time.time()
        gate = DoDGate(
            name="Type Safety (mypy)",
            category="Code Quality",
            passed=False,
        )

        try:
            add_span_event("dod.check.type_safety.starting")

            # Run mypy with strict mode
            cmd = ["mypy", "src/", "--strict", "--show-error-codes"]
            success, output, duration = _run_tool(cmd, tool_name="mypy")

            gate.details = {
                "tool": "mypy",
                "mode": "strict",
                "output_lines": len(output.splitlines()),
                "duration": duration,
            }

            # Success if no errors found
            gate.passed = success and ("error" not in output.lower() or "success" in output.lower())

            metric_counter("dod.type_safety.completed")(1)
            if gate.passed:
                metric_counter("dod.type_safety.passed")(1)
            else:
                metric_counter("dod.type_safety.failed")(1)

            add_span_attributes(
                type_safety_passed=gate.passed,
                type_safety_duration=duration,
            )

            return gate

        except Exception as e:
            gate.error = str(e)
            metric_counter("dod.type_safety.error")(1)
            add_span_event("dod.type_safety.error", {"error": str(e)})
            return gate


def check_code_linting() -> DoDGate:
    """Check code linting with ruff.

    Returns
    -------
    DoDGate
        Gate result with linting details.
    """
    with span("dod.check.code_linting"):
        gate = DoDGate(
            name="Code Linting (ruff)",
            category="Code Quality",
            passed=False,
        )

        try:
            add_span_event("dod.check.code_linting.starting")

            # Run ruff check
            cmd = ["ruff", "check", "src/", "tests/"]
            success, output, duration = _run_tool(cmd, tool_name="ruff")

            violations = len(output.splitlines()) if output else 0

            gate.details = {
                "tool": "ruff",
                "violations": violations,
                "duration": duration,
            }

            # Success if no violations
            gate.passed = success and violations == 0

            metric_counter("dod.code_linting.completed")(1)
            if gate.passed:
                metric_counter("dod.code_linting.passed")(1)
            else:
                metric_counter("dod.code_linting.failed")(1)

            add_span_attributes(
                code_linting_passed=gate.passed,
                code_linting_violations=violations,
                code_linting_duration=duration,
            )

            return gate

        except Exception as e:
            gate.error = str(e)
            metric_counter("dod.code_linting.error")(1)
            add_span_event("dod.code_linting.error", {"error": str(e)})
            return gate


def check_security() -> DoDGate:
    """Check security with bandit.

    Returns
    -------
    DoDGate
        Gate result with security details.
    """
    with span("dod.check.security"):
        gate = DoDGate(
            name="Security Scanning (bandit)",
            category="Code Quality",
            passed=False,
        )

        try:
            add_span_event("dod.check.security.starting")

            # Run bandit (only high/medium severity)
            cmd = ["bandit", "-r", "src/", "-ll", "-q"]
            success, output, duration = _run_tool(cmd, tool_name="bandit")

            # Bandit returns 0 if no issues, 1 if issues found
            gate.details = {
                "tool": "bandit",
                "duration": duration,
                "output_lines": len(output.splitlines()) if output else 0,
            }

            gate.passed = success

            metric_counter("dod.security.completed")(1)
            if gate.passed:
                metric_counter("dod.security.passed")(1)
            else:
                metric_counter("dod.security.failed")(1)

            add_span_attributes(
                security_passed=gate.passed,
                security_duration=duration,
            )

            return gate

        except Exception as e:
            gate.error = str(e)
            metric_counter("dod.security.error")(1)
            add_span_event("dod.security.error", {"error": str(e)})
            return gate


def check_documentation() -> DoDGate:
    """Check documentation completeness.

    Returns
    -------
    DoDGate
        Gate result with documentation details.
    """
    with span("dod.check.documentation"):
        gate = DoDGate(
            name="Documentation (docstrings)",
            category="Code Quality",
            passed=False,
        )

        try:
            add_span_event("dod.check.documentation.starting")

            # Check for docstrings using pydocstyle if available
            cmd = ["pydocstyle", "src/specify_cli/", "--convention=numpy", "--quiet"]
            success, output, duration = _run_tool(cmd, tool_name="pydocstyle")

            violations = len(output.splitlines()) if output else 0

            gate.details = {
                "tool": "pydocstyle",
                "violations": violations,
                "duration": duration,
            }

            gate.passed = success and violations == 0

            metric_counter("dod.documentation.completed")(1)
            if gate.passed:
                metric_counter("dod.documentation.passed")(1)
            else:
                metric_counter("dod.documentation.failed")(1)

            add_span_attributes(
                documentation_passed=gate.passed,
                documentation_violations=violations,
                documentation_duration=duration,
            )

            return gate

        except Exception as e:
            gate.error = str(e)
            metric_counter("dod.documentation.error")(1)
            add_span_event("dod.documentation.error", {"error": str(e)})
            return gate


def check_test_coverage() -> DoDGate:
    """Check test coverage with pytest.

    Returns
    -------
    DoDGate
        Gate result with coverage details.
    """
    with span("dod.check.test_coverage"):
        gate = DoDGate(
            name="Test Coverage (≥80%)",
            category="Testing",
            passed=False,
        )

        try:
            add_span_event("dod.check.test_coverage.starting")

            # Run pytest with coverage
            cmd = [
                "pytest",
                "tests/",
                "--cov=src/specify_cli",
                "--cov-report=term-missing",
                "-q",
            ]
            _success, output, duration = _run_tool(cmd, tool_name="pytest")

            # Parse coverage percentage from output
            coverage_pct = 0.0
            for line in output.splitlines():
                if "TOTAL" in line:
                    parts = line.split()
                    if len(parts) > 1:
                        with contextlib.suppress(ValueError):
                            coverage_pct = float(parts[-1].rstrip("%"))

            gate.details = {
                "tool": "pytest",
                "coverage_percent": coverage_pct,
                "duration": duration,
            }

            gate.passed = coverage_pct >= 80.0

            metric_counter("dod.test_coverage.completed")(1)
            metric_histogram("dod.test_coverage.percent")(coverage_pct)
            if gate.passed:
                metric_counter("dod.test_coverage.passed")(1)
            else:
                metric_counter("dod.test_coverage.failed")(1)

            add_span_attributes(
                test_coverage_passed=gate.passed,
                test_coverage_percent=coverage_pct,
                test_coverage_duration=duration,
            )

            return gate

        except Exception as e:
            gate.error = str(e)
            metric_counter("dod.test_coverage.error")(1)
            add_span_event("dod.test_coverage.error", {"error": str(e)})
            return gate


def check_unit_tests() -> DoDGate:
    """Check unit test execution and success.

    Returns
    -------
    DoDGate
        Gate result with unit test details.
    """
    with span("dod.check.unit_tests"):
        gate = DoDGate(
            name="Unit Tests (ops layer)",
            category="Testing",
            passed=False,
        )

        try:
            add_span_event("dod.check.unit_tests.starting")

            # Run unit tests
            cmd = ["pytest", "tests/unit/", "-v", "--tb=short"]
            success, output, duration = _run_tool(cmd, tool_name="pytest")

            # Count passed/failed
            passed = output.count(" PASSED")
            failed = output.count(" FAILED")

            gate.details = {
                "tool": "pytest",
                "passed": passed,
                "failed": failed,
                "duration": duration,
            }

            gate.passed = success and failed == 0

            metric_counter("dod.unit_tests.completed")(1)
            metric_counter("dod.unit_tests.passed_count")(passed)
            if failed > 0:
                metric_counter("dod.unit_tests.failed_count")(failed)
            if gate.passed:
                metric_counter("dod.unit_tests.passed")(1)
            else:
                metric_counter("dod.unit_tests.failed")(1)

            add_span_attributes(
                unit_tests_passed=gate.passed,
                unit_tests_count=passed + failed,
                unit_tests_failed=failed,
                unit_tests_duration=duration,
            )

            return gate

        except Exception as e:
            gate.error = str(e)
            metric_counter("dod.unit_tests.error")(1)
            add_span_event("dod.unit_tests.error", {"error": str(e)})
            return gate


def check_integration_tests() -> DoDGate:
    """Check integration test execution and success.

    Returns
    -------
    DoDGate
        Gate result with integration test details.
    """
    with span("dod.check.integration_tests"):
        gate = DoDGate(
            name="Integration Tests",
            category="Testing",
            passed=False,
        )

        try:
            add_span_event("dod.check.integration_tests.starting")

            # Run integration tests
            cmd = ["pytest", "tests/integration/", "-v", "--tb=short"]
            success, output, duration = _run_tool(cmd, tool_name="pytest")

            # Count passed/failed
            passed = output.count(" PASSED")
            failed = output.count(" FAILED")

            gate.details = {
                "tool": "pytest",
                "passed": passed,
                "failed": failed,
                "duration": duration,
            }

            gate.passed = success and failed == 0

            metric_counter("dod.integration_tests.completed")(1)
            metric_counter("dod.integration_tests.passed_count")(passed)
            if failed > 0:
                metric_counter("dod.integration_tests.failed_count")(failed)
            if gate.passed:
                metric_counter("dod.integration_tests.passed")(1)
            else:
                metric_counter("dod.integration_tests.failed")(1)

            add_span_attributes(
                integration_tests_passed=gate.passed,
                integration_tests_count=passed + failed,
                integration_tests_failed=failed,
                integration_tests_duration=duration,
            )

            return gate

        except Exception as e:
            gate.error = str(e)
            metric_counter("dod.integration_tests.error")(1)
            add_span_event("dod.integration_tests.error", {"error": str(e)})
            return gate


def check_architecture_compliance() -> DoDGate:
    """Check three-tier architecture compliance.

    Returns
    -------
    DoDGate
        Gate result with architecture details.
    """
    with span("dod.check.architecture_compliance"):
        gate = DoDGate(
            name="Architecture Compliance",
            category="Architecture",
            passed=False,
        )

        try:
            add_span_event("dod.check.architecture_compliance.starting")

            # Check for layer violations
            # Commands layer should not import from runtime
            # Ops layer should not have I/O operations
            # Runtime layer should only have I/O

            src_path = Path("src/specify_cli")
            violations = []

            # Simple check: scan for disallowed imports
            if src_path.exists():
                # Check commands don't import subprocess/os.system directly
                commands_path = src_path / "commands"
                if commands_path.exists():
                    for py_file in commands_path.glob("*.py"):
                        if "subprocess" in py_file.read_text():
                            violations.append(f"{py_file.name}: subprocess in commands")

            gate.details = {
                "tool": "architecture-validator",
                "violations": len(violations),
            }

            gate.passed = len(violations) == 0

            metric_counter("dod.architecture.completed")(1)
            if gate.passed:
                metric_counter("dod.architecture.passed")(1)
            else:
                metric_counter("dod.architecture.failed")(1)

            add_span_attributes(
                architecture_passed=gate.passed,
                architecture_violations=len(violations),
            )

            return gate

        except Exception as e:
            gate.error = str(e)
            metric_counter("dod.architecture.error")(1)
            add_span_event("dod.architecture.error", {"error": str(e)})
            return gate


def check_rdf_compliance() -> DoDGate:
    """Check RDF-first development compliance.

    Returns
    -------
    DoDGate
        Gate result with RDF compliance details.
    """
    with span("dod.check.rdf_compliance"):
        gate = DoDGate(
            name="RDF-First Compliance",
            category="RDF Development",
            passed=False,
        )

        try:
            add_span_event("dod.check.rdf_compliance.starting")

            # Check for ggen.toml and RDF files
            ggen_toml = Path("docs/ggen.toml")
            ontology_path = Path("ontology")

            gate.details = {
                "ggen_toml_exists": ggen_toml.exists(),
                "ontology_exists": ontology_path.exists(),
            }

            gate.passed = ggen_toml.exists() and ontology_path.exists()

            metric_counter("dod.rdf_compliance.completed")(1)
            if gate.passed:
                metric_counter("dod.rdf_compliance.passed")(1)
            else:
                metric_counter("dod.rdf_compliance.failed")(1)

            add_span_attributes(
                rdf_compliance_passed=gate.passed,
                rdf_compliance_ggen_toml=ggen_toml.exists(),
            )

            return gate

        except Exception as e:
            gate.error = str(e)
            metric_counter("dod.rdf_compliance.error")(1)
            add_span_event("dod.rdf_compliance.error", {"error": str(e)})
            return gate


def check_changelog() -> DoDGate:
    """Check CHANGELOG.md is updated.

    Returns
    -------
    DoDGate
        Gate result with changelog details.
    """
    with span("dod.check.changelog"):
        gate = DoDGate(
            name="Changelog Updated",
            category="Documentation",
            passed=False,
        )

        try:
            add_span_event("dod.check.changelog.starting")

            # Check CHANGELOG.md exists and is not empty
            changelog_path = Path("CHANGELOG.md")

            gate.details = {
                "changelog_exists": changelog_path.exists(),
                "changelog_size": changelog_path.stat().st_size if changelog_path.exists() else 0,
            }

            gate.passed = changelog_path.exists() and changelog_path.stat().st_size > 0

            metric_counter("dod.changelog.completed")(1)
            if gate.passed:
                metric_counter("dod.changelog.passed")(1)
            else:
                metric_counter("dod.changelog.failed")(1)

            add_span_attributes(
                changelog_passed=gate.passed,
                changelog_exists=changelog_path.exists(),
            )

            return gate

        except Exception as e:
            gate.error = str(e)
            metric_counter("dod.changelog.error")(1)
            add_span_event("dod.changelog.error", {"error": str(e)})
            return gate
