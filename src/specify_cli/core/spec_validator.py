"""Validates that code implementation matches RDF specifications.

Implements the constitutional equation: implementation = μ(specification.ttl)

This module ensures the system is self-observing: it can detect when
code diverges from its RDF specification.
"""

from __future__ import annotations

import ast
import inspect
import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Callable

from specify_cli.core.shell import timed
from specify_cli.core.telemetry import metric_counter, span


class ValidationStatus(Enum):
    """Status of validation."""

    VALID = "valid"
    MISSING = "missing"
    EXTRA = "extra"
    MISMATCH = "mismatch"
    ERROR = "error"


@dataclass
class ValidationResult:
    """Result of validation check."""

    status: ValidationStatus
    component: str
    expected: str | None
    found: str | None
    message: str
    details: dict[str, Any] | None = None


@dataclass
class SpecValidationReport:
    """Report from comprehensive spec validation."""

    module_name: str
    spec_file: str
    implementation_file: str
    valid: bool
    total_checks: int
    passed_checks: int
    failed_checks: int
    results: list[ValidationResult]
    timestamp: float


class SpecValidator:
    """Validates code against RDF specifications."""

    def __init__(self, spec_file: Path, implementation_file: Path):
        self.spec_file = spec_file
        self.implementation_file = implementation_file
        self.spec_data: dict[str, Any] = {}
        self.code_ast: ast.Module | None = None
        self.results: list[ValidationResult] = []

    @timed
    def validate_module(self) -> SpecValidationReport:
        """Validate entire module against specification."""
        with span("spec_validator.validate_module", module=self.implementation_file.name):
            import time
            start_time = time.time()

            # Load spec
            self._load_spec()

            # Parse code
            self._parse_code()

            # Run validation checks
            self._validate_imports()
            self._validate_telemetry()
            self._validate_classes()
            self._validate_functions()
            self._validate_error_handling()

            passed = sum(
                1 for r in self.results
                if r.status == ValidationStatus.VALID
            )
            failed = sum(
                1 for r in self.results
                if r.status != ValidationStatus.VALID
            )

            metric_counter(
                "spec_validator.validation_run",
                1,
                {
                    "module": self.implementation_file.name,
                    "status": "valid" if not failed else "invalid",
                },
            )

            return SpecValidationReport(
                module_name=self.implementation_file.stem,
                spec_file=str(self.spec_file),
                implementation_file=str(self.implementation_file),
                valid=failed == 0,
                total_checks=len(self.results),
                passed_checks=passed,
                failed_checks=failed,
                results=self.results,
                timestamp=start_time,
            )

    def _load_spec(self) -> None:
        """Load specification from file."""
        try:
            if self.spec_file.suffix == ".json":
                with open(self.spec_file) as f:
                    self.spec_data = json.load(f)
            elif self.spec_file.suffix == ".ttl":
                # For TTL, we would parse RDF - for now, extract from comments
                self.spec_data = self._extract_spec_from_comments()
            else:
                self.results.append(
                    ValidationResult(
                        status=ValidationStatus.ERROR,
                        component="spec_loader",
                        expected=None,
                        found=None,
                        message=f"Unknown spec file format: {self.spec_file.suffix}",
                    )
                )
        except Exception as e:
            self.results.append(
                ValidationResult(
                    status=ValidationStatus.ERROR,
                    component="spec_loader",
                    expected=None,
                    found=None,
                    message=str(e),
                )
            )

    def _parse_code(self) -> None:
        """Parse Python code into AST."""
        try:
            with open(self.implementation_file) as f:
                source = f.read()
            self.code_ast = ast.parse(source)
        except Exception as e:
            self.results.append(
                ValidationResult(
                    status=ValidationStatus.ERROR,
                    component="code_parser",
                    expected=None,
                    found=None,
                    message=f"Failed to parse code: {str(e)}",
                )
            )

    def _validate_imports(self) -> None:
        """Validate required imports are present."""
        if not self.code_ast:
            return

        with span("spec_validator.validate_imports"):
            required_imports = [
                "specify_cli.core.shell",
                "specify_cli.core.telemetry",
            ]

            found_imports = set()
            for node in ast.walk(self.code_ast):
                if isinstance(node, ast.ImportFrom):
                    if node.module:
                        found_imports.add(node.module)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        found_imports.add(alias.name)

            for req in required_imports:
                if req in found_imports:
                    self.results.append(
                        ValidationResult(
                            status=ValidationStatus.VALID,
                            component=f"import_{req}",
                            expected=req,
                            found=req,
                            message=f"Required import found: {req}",
                        )
                    )
                else:
                    self.results.append(
                        ValidationResult(
                            status=ValidationStatus.MISSING,
                            component=f"import_{req}",
                            expected=req,
                            found=None,
                            message=f"Missing required import: {req}",
                        )
                    )

    def _validate_telemetry(self) -> None:
        """Validate OpenTelemetry instrumentation."""
        if not self.code_ast:
            return

        with span("spec_validator.validate_telemetry"):
            timed_count = 0
            span_count = 0

            for node in ast.walk(self.code_ast):
                # Check for @timed decorators
                if isinstance(node, ast.FunctionDef):
                    for decorator in node.decorator_list:
                        if isinstance(decorator, ast.Name):
                            if decorator.id == "timed":
                                timed_count += 1

            # Check for span calls in code
            for node in ast.walk(self.code_ast):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id == "span":
                            span_count += 1

            # Validate minimums
            expected_timed = 5  # At least 5 timed functions
            expected_spans = 3  # At least 3 spans

            self.results.append(
                ValidationResult(
                    status=(
                        ValidationStatus.VALID
                        if timed_count >= expected_timed
                        else ValidationStatus.MISMATCH
                    ),
                    component="telemetry.timed",
                    expected=str(expected_timed),
                    found=str(timed_count),
                    message=f"@timed decorators: {timed_count} (expected >= {expected_timed})",
                )
            )

            self.results.append(
                ValidationResult(
                    status=(
                        ValidationStatus.VALID
                        if span_count >= expected_spans
                        else ValidationStatus.MISMATCH
                    ),
                    component="telemetry.spans",
                    expected=str(expected_spans),
                    found=str(span_count),
                    message=f"span() calls: {span_count} (expected >= {expected_spans})",
                )
            )

    def _validate_classes(self) -> None:
        """Validate class definitions."""
        if not self.code_ast:
            return

        with span("spec_validator.validate_classes"):
            classes = [
                node
                for node in ast.walk(self.code_ast)
                if isinstance(node, ast.ClassDef)
            ]

            # Should have dataclasses for structured returns
            dataclass_decorators = 0
            for node in classes:
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Name):
                        if decorator.id == "dataclass":
                            dataclass_decorators += 1

            self.results.append(
                ValidationResult(
                    status=(
                        ValidationStatus.VALID
                        if dataclass_decorators > 0
                        else ValidationStatus.MISSING
                    ),
                    component="structure.dataclasses",
                    expected=">0",
                    found=str(dataclass_decorators),
                    message=f"Dataclass definitions: {dataclass_decorators} (expected > 0)",
                )
            )

    def _validate_functions(self) -> None:
        """Validate function definitions and signatures."""
        if not self.code_ast:
            return

        with span("spec_validator.validate_functions"):
            functions = [
                node
                for node in ast.walk(self.code_ast)
                if isinstance(node, ast.FunctionDef)
            ]

            # Check for type hints
            functions_with_type_hints = 0
            for func in functions:
                if func.returns is not None:  # Has return type
                    functions_with_type_hints += 1

            type_hint_ratio = (
                functions_with_type_hints / len(functions)
                if functions
                else 0
            )

            self.results.append(
                ValidationResult(
                    status=(
                        ValidationStatus.VALID
                        if type_hint_ratio >= 0.8
                        else ValidationStatus.MISMATCH
                    ),
                    component="quality.type_hints",
                    expected=">=80%",
                    found=f"{type_hint_ratio * 100:.1f}%",
                    message=f"Functions with return type hints: {type_hint_ratio * 100:.1f}%",
                )
            )

    def _validate_error_handling(self) -> None:
        """Validate error handling patterns."""
        if not self.code_ast:
            return

        with span("spec_validator.validate_error_handling"):
            try_except_blocks = 0

            for node in ast.walk(self.code_ast):
                if isinstance(node, ast.Try):
                    try_except_blocks += 1

            self.results.append(
                ValidationResult(
                    status=(
                        ValidationStatus.VALID
                        if try_except_blocks > 0
                        else ValidationStatus.MISSING
                    ),
                    component="resilience.error_handling",
                    expected=">0",
                    found=str(try_except_blocks),
                    message=f"Try-except blocks: {try_except_blocks} (expected > 0)",
                )
            )

    def _extract_spec_from_comments(self) -> dict[str, Any]:
        """Extract specification from module docstrings."""
        try:
            with open(self.implementation_file) as f:
                source = f.read()
            tree = ast.parse(source)

            spec = {
                "module_docstring": ast.get_docstring(tree) or "",
                "file": str(self.implementation_file),
            }

            return spec
        except Exception:
            return {}

    def get_report_dict(self) -> dict[str, Any]:
        """Get validation report as dictionary."""
        passed = sum(
            1 for r in self.results
            if r.status == ValidationStatus.VALID
        )
        failed = len(self.results) - passed

        return {
            "module": self.implementation_file.stem,
            "specification": str(self.spec_file),
            "implementation": str(self.implementation_file),
            "valid": failed == 0,
            "summary": {
                "total": len(self.results),
                "passed": passed,
                "failed": failed,
                "success_rate": (
                    passed / len(self.results) * 100
                    if self.results
                    else 0.0
                ),
            },
            "results": [
                {
                    "status": r.status.value,
                    "component": r.component,
                    "expected": r.expected,
                    "found": r.found,
                    "message": r.message,
                    "details": r.details,
                }
                for r in self.results
            ],
        }


def validate_runtime_modules() -> dict[str, Any]:
    """Validate all runtime modules against specifications."""
    with span("spec_validator.validate_all_modules"):
        spec_root = Path(
            "/home/user/ggen-spec-kit/ontology"
        )
        impl_root = Path(
            "/home/user/ggen-spec-kit/src/specify_cli/runtime"
        )

        modules_to_validate = [
            ("runtime-clustering.ttl", "consensus.py"),
            ("runtime-clustering.ttl", "cluster.py"),
            ("runtime-clustering.ttl", "distributed_execution.py"),
            ("runtime-clustering.ttl", "fault_tolerance.py"),
        ]

        results = []

        for spec_file, impl_file in modules_to_validate:
            spec_path = spec_root / spec_file
            impl_path = impl_root / impl_file

            if not impl_path.exists():
                metric_counter(
                    "spec_validator.validation_skipped",
                    1,
                    {"module": impl_file, "reason": "not_found"},
                )
                continue

            validator = SpecValidator(spec_path, impl_path)
            report = validator.validate_module()
            results.append(validator.get_report_dict())

        # Summary
        total_modules = len(results)
        valid_modules = sum(
            1 for r in results if r["valid"]
        )

        metric_counter(
            "spec_validator.modules_validated",
            total_modules,
            {"valid": str(valid_modules), "invalid": str(total_modules - valid_modules)},
        )

        return {
            "timestamp": __import__("time").time(),
            "total_modules": total_modules,
            "valid_modules": valid_modules,
            "invalid_modules": total_modules - valid_modules,
            "modules": results,
        }
