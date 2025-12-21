"""
specify_cli.spiff.ops - SPIFF Operations Layer

Business logic for BPMN workflow management, OTEL validation, and external
project validation, separated from CLI layer for testability and reusability.
"""

from .external_projects import (
    ExternalProjectInfo,
    ExternalValidationResult,
    batch_validate_external_projects,
    discover_external_projects,
    run_8020_external_project_validation,
    validate_external_project_with_spiff,
)
from .otel_validation import (
    OTELValidationResult,
    TestValidationStep,
    create_otel_validation_workflow,
    execute_otel_validation_workflow,
    run_8020_otel_validation,
)

__all__ = [
    # External projects
    "ExternalProjectInfo",
    "ExternalValidationResult",
    # OTEL validation
    "OTELValidationResult",
    "TestValidationStep",
    "batch_validate_external_projects",
    "create_otel_validation_workflow",
    "discover_external_projects",
    "execute_otel_validation_workflow",
    "run_8020_external_project_validation",
    "run_8020_otel_validation",
    "validate_external_project_with_spiff",
]
