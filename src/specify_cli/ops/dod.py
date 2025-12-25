"""
specify_cli.ops.dod
====================

Pure business logic layer for Definition of Done automation and checklists.

This module implements all business logic for the dod command.
No I/O operations, subprocess calls, or side effects - all delegated to runtime layer.

The ops layer:
- Validates inputs and state
- Performs pure computations
- Returns structured data
- Records telemetry events
- Raises appropriate exceptions

See Also:
- :mod:`specify_cli.commands.dod` : CLI interface
- :mod:`specify_cli.runtime.dod` : Runtime I/O operations
"""

from __future__ import annotations

import time
from typing import Any

from specify_cli.core.dod_types import DoDCheckResult, DoDGate
from specify_cli.core.instrumentation import add_span_attributes, add_span_event
from specify_cli.core.telemetry import metric_counter, metric_histogram, span
from specify_cli.runtime import dod as dod_runtime

__all__ = [
    "DoDCheckResult",
    "DoDGate",
    "check_dod",
    "validate_inputs",
]


def validate_inputs(**kwargs: Any) -> dict[str, Any]:
    """Validate inputs for dod operations.

    Parameters
    ----------
    **kwargs : Any
        Command arguments and options

    Returns
    -------
    dict[str, Any]
        Validation result with 'valid' key

    Raises
    ------
    ValueError
        If required arguments are missing or invalid.
    """
    add_span_event("dod.validate_inputs", {"operation": "dod", "arg_count": len(kwargs)})

    # Validate strict mode if provided
    if "strict" in kwargs and not isinstance(kwargs["strict"], bool):
        raise ValueError("strict option must be boolean")

    return {"valid": True, "errors": []}


def check_dod(*, strict: bool = False) -> dict[str, Any]:
    """Check Definition of Done compliance.

    Validates all DoD criteria:
    - Code Quality Gates (type safety, linting, security, documentation)
    - Testing Requirements (coverage, unit, integration, E2E)
    - Architecture Compliance (three-tier separation, OTEL, DI)
    - RDF-First Development (spec-driven, constitutional equation)
    - Documentation (CHANGELOG, API docs, examples)

    Parameters
    ----------
    strict : bool, optional
        Fail on any incomplete items. Default is False.

    Returns
    -------
    dict[str, Any]
        Check result with success status, gate details, and duration.

    Raises
    ------
    RuntimeError
        If DoD check infrastructure fails.
    """
    start_time = time.time()

    with span("dod.check_dod", strict=strict):
        add_span_event("dod.check_dod.started", {"strict": strict})

        result = DoDCheckResult(success=False, strict_mode=strict)
        gates: list[DoDGate] = []

        try:
            # 1. Code Quality Gates
            add_span_event("dod.check.code_quality.starting")

            # Type safety (mypy)
            mypy_gate = dod_runtime.check_type_safety()
            gates.append(mypy_gate)

            # Linting (ruff)
            ruff_gate = dod_runtime.check_code_linting()
            gates.append(ruff_gate)

            # Security (bandit)
            bandit_gate = dod_runtime.check_security()
            gates.append(bandit_gate)

            # Documentation
            docs_gate = dod_runtime.check_documentation()
            gates.append(docs_gate)

            # 2. Testing Requirements
            add_span_event("dod.check.testing.starting")

            # Test coverage
            coverage_gate = dod_runtime.check_test_coverage()
            gates.append(coverage_gate)

            # Unit tests (ops layer)
            unit_tests_gate = dod_runtime.check_unit_tests()
            gates.append(unit_tests_gate)

            # Integration tests
            integration_tests_gate = dod_runtime.check_integration_tests()
            gates.append(integration_tests_gate)

            # 3. Architecture Compliance
            add_span_event("dod.check.architecture.starting")

            arch_gate = dod_runtime.check_architecture_compliance()
            gates.append(arch_gate)

            # 4. RDF-First Development
            add_span_event("dod.check.rdf_first.starting")

            rdf_gate = dod_runtime.check_rdf_compliance()
            gates.append(rdf_gate)

            # 5. Documentation
            changelog_gate = dod_runtime.check_changelog()
            gates.append(changelog_gate)

            # Calculate result
            result.gates = gates
            result.total_gates = len(gates)
            result.passed_gates = sum(1 for g in gates if g.passed)
            result.failed_gates = [g for g in gates if not g.passed]
            result.success = len(result.failed_gates) == 0

            if strict and result.failed_gates:
                result.success = False

            result.duration = time.time() - start_time

            # Record metrics
            metric_counter("dod.check.completed")(1)
            metric_histogram("dod.check.duration")(result.duration)

            if result.success:
                metric_counter("dod.check.success")(1)
            else:
                metric_counter("dod.check.failed")(1)

            add_span_attributes(
                dod_total=result.total_gates,
                dod_passed=result.passed_gates,
                dod_failed=len(result.failed_gates),
                dod_success=result.success,
            )

            add_span_event(
                "dod.check_dod.completed",
                {
                    "success": result.success,
                    "total": result.total_gates,
                    "passed": result.passed_gates,
                    "failed": len(result.failed_gates),
                    "duration": result.duration,
                },
            )

            return result.to_dict()

        except Exception as e:
            result.duration = time.time() - start_time
            metric_counter("dod.check.error")(1)

            add_span_event(
                "dod.check_dod.error",
                {
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "duration": result.duration,
                },
            )

            raise RuntimeError(f"DoD check failed: {e}") from e
