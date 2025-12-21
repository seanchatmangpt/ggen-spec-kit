"""
specify_cli.core.semconv - Semantic Conventions
===============================================

Standard attribute names for OpenTelemetry instrumentation in specify-cli.
Follows OpenTelemetry semantic conventions while adding specify-cli specific domains.

This module provides type-safe access to semantic convention attributes for:
- CLI command instrumentation
- Process execution tracking
- Project and spec operations
- Workflow and process mining
- Cache and configuration

Examples
--------
    >>> from specify_cli.core.semconv import CliAttributes, ProcessAttributes
    >>>
    >>> # Use in span attributes
    >>> with span("my_operation", **{
    ...     CliAttributes.COMMAND: "init",
    ...     CliAttributes.EXIT_CODE: 0,
    ... }):
    ...     pass

Reference: https://opentelemetry.io/docs/specs/semconv/

See Also
--------
- :mod:`specify_cli.core.telemetry` : Telemetry and observability
- :mod:`specify_cli.core.instrumentation` : Command instrumentation
"""

from __future__ import annotations

from typing import Any, Final

__all__ = [
    # Cache Attributes
    "CacheAttributes",
    "CacheOperations",
    # CLI Attributes
    "CliAttributes",
    "CliOperations",
    # GitHub Attributes
    "GitHubAttributes",
    "GitHubOperations",
    # Process Attributes
    "ProcessAttributes",
    "ProcessOperations",
    # Project Attributes
    "ProjectAttributes",
    "ProjectOperations",
    # Spec Attributes
    "SpecAttributes",
    "SpecOperations",
    # Template Attributes
    "TemplateAttributes",
    "TemplateOperations",
    # Test Attributes
    "TestAttributes",
    "TestOperations",
    # Workflow Attributes
    "WorkflowAttributes",
    "WorkflowOperations",
    # Helper function
    "get_common_attributes",
]


# =============================================================================
# CLI Command Attributes
# =============================================================================


class CliAttributes:
    """CLI command attributes for specify-cli instrumentation."""

    # Command identification
    COMMAND: Final[str] = "cli.command"
    SUBCOMMAND: Final[str] = "cli.subcommand"
    MODULE: Final[str] = "cli.module"

    # Execution context
    OPTIONS: Final[str] = "cli.options"
    ARGS_COUNT: Final[str] = "cli.args.count"
    EXIT_CODE: Final[str] = "cli.exit_code"
    SUCCESS: Final[str] = "cli.success"

    # Code location
    CODE_FUNCTION: Final[str] = "code.function"
    CODE_NAMESPACE: Final[str] = "code.namespace"
    CODE_FILEPATH: Final[str] = "code.filepath"
    CODE_LINENO: Final[str] = "code.lineno"


class CliOperations:
    """Standard CLI operation values."""

    EXECUTE: Final[str] = "cli.execute"
    VALIDATE: Final[str] = "cli.validate"
    HELP: Final[str] = "cli.help"
    VERSION: Final[str] = "cli.version"


# =============================================================================
# Process Execution Attributes
# =============================================================================


class ProcessAttributes:
    """Process execution attributes for subprocess instrumentation."""

    # Command information
    COMMAND: Final[str] = "process.command"
    COMMAND_ARGS: Final[str] = "process.command_args"
    WORKING_DIRECTORY: Final[str] = "process.working_directory"

    # Execution mode
    CAPTURE: Final[str] = "process.capture"
    QUIET: Final[str] = "process.quiet"
    DRY_RUN: Final[str] = "process.dry_run"

    # Results
    EXIT_CODE: Final[str] = "process.exit_code"
    DURATION: Final[str] = "process.duration"
    OUTPUT_SIZE: Final[str] = "process.output_size"


class ProcessOperations:
    """Standard process operation values."""

    EXECUTE: Final[str] = "process.execute"
    LOGGED_EXECUTE: Final[str] = "process.logged_execute"
    WHICH: Final[str] = "process.which"


# =============================================================================
# Project Attributes
# =============================================================================


class ProjectAttributes:
    """Project-related attributes for specify-cli operations."""

    # Project identification
    ID: Final[str] = "project.id"
    NAME: Final[str] = "project.name"
    PATH: Final[str] = "project.path"

    # Project type and configuration
    TYPE: Final[str] = "project.type"  # "web", "cli", "library", etc.
    MANAGER: Final[str] = "project.manager"  # "uv", "pip", "poetry"
    AI_ASSISTANT: Final[str] = "project.ai_assistant"  # "claude", "cursor", etc.
    SCRIPT_TYPE: Final[str] = "project.script_type"  # "sh", "ps1", "cmd"


class ProjectOperations:
    """Standard project operation values."""

    INIT: Final[str] = "project.init"
    CHECK: Final[str] = "project.check"
    CONFIGURE: Final[str] = "project.configure"
    UPGRADE: Final[str] = "project.upgrade"


# =============================================================================
# Workflow Attributes (BPMN/SpiffWorkflow)
# =============================================================================


class WorkflowAttributes:
    """Semantic conventions for BPMN workflow execution."""

    WORKFLOW_ID = "workflow.id"
    WORKFLOW_NAME = "workflow.name"
    WORKFLOW_VERSION = "workflow.version"
    WORKFLOW_FILE = "workflow.file"
    WORKFLOW_FORMAT = "workflow.format"  # "bpmn", "dmn", etc.
    WORKFLOW_STATUS = "workflow.status"  # "created", "executing", "completed", "failed"

    TASK_ID = "task.id"
    TASK_NAME = "task.name"
    TASK_TYPE = "task.type"  # "script_task", "service_task", "user_task", etc.
    TASK_STATE = "task.state"  # "COMPLETED", "READY", "WAITING", "CANCELLED"
    TASK_ATTEMPTS = "task.attempts"
    TASK_DURATION_MS = "task.duration_ms"

    STEP_INDEX = "step.index"
    STEP_COUNT = "step.count"
    STEP_DURATION_MS = "step.duration_ms"

    LOOP_DETECTED = "workflow.loop_detected"
    LOOP_COUNT = "workflow.loop_count"
    MAX_ITERATIONS = "workflow.max_iterations"
    CURRENT_ITERATION = "workflow.current_iteration"


class WorkflowOperations:
    """Operation names for workflow instrumentation."""

    CREATE = "workflow.create"
    LOAD = "workflow.load"
    VALIDATE = "workflow.validate"
    EXECUTE = "workflow.execute"
    STEP = "workflow.step"
    TASK_EXECUTE = "task.execute"
    TASK_PROCESS = "task.process"
    PARSE = "bpmn.parse"


class TestAttributes:
    """Semantic conventions for test execution and validation."""

    # Test identification
    ID: Final[str] = "test.id"
    NAME: Final[str] = "test.name"
    TYPE: Final[str] = "test.type"  # "unit", "integration", "e2e", "validation"
    COMMAND: Final[str] = "test.command"
    STATUS: Final[str] = "test.status"  # "passed", "failed", "skipped"
    DURATION_MS: Final[str] = "test.duration_ms"
    ERROR: Final[str] = "test.error"

    # Validation attributes
    VALIDATION_ID: Final[str] = "validation.id"
    VALIDATION_TYPE: Final[str] = "validation.type"  # "otel", "integration", "conformance"
    VALIDATION_SCOPE: Final[str] = "validation.scope"  # "project", "module", "function"
    VALIDATION_RESULT: Final[str] = "validation.result"  # "success", "failure", "warning"

    # OTEL-specific validation
    OTEL_SPANS_CREATED: Final[str] = "otel.spans_created"
    OTEL_METRICS_CREATED: Final[str] = "otel.metrics_created"
    OTEL_SPAN_EVENTS: Final[str] = "otel.span_events"
    OTEL_HEALTH_STATUS: Final[str] = "otel.health_status"


class TestOperations:
    """Standard test operation values."""

    RUN: Final[str] = "test.run"
    VALIDATE: Final[str] = "test.validate"
    CHECK: Final[str] = "test.check"
    REPORT: Final[str] = "test.report"


# =============================================================================
# Spec Attributes
# =============================================================================


class SpecAttributes:
    """Semantic conventions for Spec-Kit specific operations."""

    # Spec identification
    ID: Final[str] = "spec.id"
    NAME: Final[str] = "spec.name"
    FILE: Final[str] = "spec.file"
    FORMAT: Final[str] = "spec.format"  # "rdf", "bpmn", "yaml", etc.
    STATUS: Final[str] = "spec.status"  # "draft", "active", "archived"

    # Process mining attributes
    PM_OPERATION: Final[str] = "pm.operation"  # "discover", "conform", "filter", "sample"
    PM_ALGORITHM: Final[str] = "pm.algorithm"  # "alpha", "inductive", etc.
    PM_CASES: Final[str] = "pm.cases"
    PM_EVENTS: Final[str] = "pm.events"
    PM_ACTIVITIES: Final[str] = "pm.activities"
    PM_VARIANTS: Final[str] = "pm.variants"

    # Code generation attributes
    CODEGEN_FILE: Final[str] = "codegen.file"
    CODEGEN_LINES: Final[str] = "codegen.lines"
    CODEGEN_TIME_MS: Final[str] = "codegen.time_ms"


class SpecOperations:
    """Standard spec operation values."""

    LOAD: Final[str] = "spec.load"
    PARSE: Final[str] = "spec.parse"
    VALIDATE: Final[str] = "spec.validate"
    GENERATE: Final[str] = "spec.generate"
    TRANSFORM: Final[str] = "spec.transform"


# =============================================================================
# Cache Attributes
# =============================================================================


class CacheAttributes:
    """Cache operation attributes."""

    # Cache identification
    KEY: Final[str] = "cache.key"
    PATH: Final[str] = "cache.path"
    SIZE_BYTES: Final[str] = "cache.size_bytes"
    ENTRIES: Final[str] = "cache.entries"

    # Cache status
    HIT: Final[str] = "cache.hit"
    MISS: Final[str] = "cache.miss"
    TTL: Final[str] = "cache.ttl"


class CacheOperations:
    """Standard cache operation values."""

    GET: Final[str] = "cache.get"
    SET: Final[str] = "cache.set"
    CLEAR: Final[str] = "cache.clear"
    PRUNE: Final[str] = "cache.prune"
    STATS: Final[str] = "cache.stats"


# =============================================================================
# GitHub Attributes
# =============================================================================


class GitHubAttributes:
    """GitHub API operation attributes."""

    # Repository attributes
    OWNER: Final[str] = "github.owner"
    REPO: Final[str] = "github.repo"
    BRANCH: Final[str] = "github.branch"
    TAG: Final[str] = "github.tag"

    # Release attributes
    RELEASE_ID: Final[str] = "github.release.id"
    RELEASE_NAME: Final[str] = "github.release.name"
    RELEASE_TAG: Final[str] = "github.release.tag"
    RELEASE_URL: Final[str] = "github.release.url"

    # Rate limiting
    RATE_LIMIT_REMAINING: Final[str] = "github.rate_limit.remaining"
    RATE_LIMIT_RESET: Final[str] = "github.rate_limit.reset"

    # Authentication
    AUTHENTICATED: Final[str] = "github.authenticated"


class GitHubOperations:
    """Standard GitHub operation values."""

    FETCH_RELEASE: Final[str] = "github.fetch_release"
    DOWNLOAD: Final[str] = "github.download"
    LIST_RELEASES: Final[str] = "github.list_releases"
    CHECK_RATE_LIMIT: Final[str] = "github.check_rate_limit"


# =============================================================================
# Template Attributes
# =============================================================================


class TemplateAttributes:
    """Template operation attributes."""

    # Template identification
    NAME: Final[str] = "template.name"
    VERSION: Final[str] = "template.version"
    SOURCE: Final[str] = "template.source"

    # Download attributes
    URL: Final[str] = "template.url"
    SIZE_BYTES: Final[str] = "template.size_bytes"
    DOWNLOAD_DURATION: Final[str] = "template.download_duration"

    # Extraction attributes
    DESTINATION: Final[str] = "template.destination"
    FILES_EXTRACTED: Final[str] = "template.files_extracted"


class TemplateOperations:
    """Standard template operation values."""

    DOWNLOAD: Final[str] = "template.download"
    EXTRACT: Final[str] = "template.extract"
    APPLY: Final[str] = "template.apply"
    LIST: Final[str] = "template.list"


# =============================================================================
# Helper Functions
# =============================================================================


def get_common_attributes(name: str, status: str | None = None) -> dict[str, Any]:
    """
    Create a common attribute set for any operation.

    Parameters
    ----------
    name : str
        Operation name.
    status : str, optional
        Operation status (e.g., "success", "failure").

    Returns
    -------
    dict[str, Any]
        Dictionary of standard attributes.

    Example
    -------
    >>> attrs = get_common_attributes("fetch_data", "success")
    >>> print(attrs)
    {'operation.name': 'fetch_data', 'operation.status': 'success'}
    """
    attrs: dict[str, Any] = {"operation.name": name}
    if status:
        attrs["operation.status"] = status
    return attrs
