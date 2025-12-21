"""
specify_cli.core - Core Infrastructure
======================================

Core utilities and infrastructure for the specify-cli package.

This module provides foundational components for:
- OpenTelemetry instrumentation and telemetry
- Command instrumentation decorators
- Process execution with security and observability
- Shell utilities for Rich terminal output
- Configuration management
- Result caching
- Error handling
- Semantic conventions

Layer Architecture
-----------------
The core layer provides infrastructure used by all other layers:

    Commands Layer → Ops Layer → Runtime Layer
          ↓              ↓             ↓
                    Core Layer
          (telemetry, config, cache, errors)

Examples
--------
    >>> from specify_cli.core import span, colour, get_config
    >>>
    >>> with span("my_operation"):
    ...     colour("Starting operation...", "cyan")
    ...     config = get_config()

See Also
--------
- :mod:`specify_cli.runtime` : Runtime execution layer
- :mod:`specify_cli.ops` : Operations/business logic layer
- :mod:`specify_cli.commands` : CLI commands layer
"""

from __future__ import annotations

# Cache - Result caching
from .cache import (
    cache_key,
    cache_stats,
    clear_cache,
    get_cached,
    set_cached,
)

# Configuration - Settings management
from .config import (
    SpecifyConfig,
    env_or,
    get_cache_dir,
    get_config,
    get_config_dir,
)

# Error Handling - Error management
from .error_handling import (
    ConfigurationError,
    ErrorCategory,
    ErrorSeverity,
    ExitCode,
    NetworkError,
    SpecifyError,
    ToolNotFoundError,
    ValidationError,
    format_error_message,
    handle_cli_error,
    with_error_handling,
)

# Git operations (legacy, moved to runtime in future)
from .git import init_git_repo, is_git_repo

# GitHub operations (legacy, moved to runtime in future)
from .github import (
    _format_rate_limit_error,
    _github_auth_headers,
    _github_token,
    _parse_rate_limit_headers,
    download_template_from_github,
)

# Instrumentation - Command decorators
from .instrumentation import (
    add_span_attributes,
    add_span_event,
    instrument_command,
    instrument_subcommand,
)

# JTBD Measurement - Analysis and reporting
from .jtbd_measurement import (
    FeatureEffectiveness,
    JTBDMetrics,
    OutcomeDeliveryAnalysis,
    analyze_feature_effectiveness,
    analyze_outcome_delivery,
    export_metrics,
    extract_jtbd_metrics,
    generate_jtbd_report,
    query_job_completions,
    query_outcome_achievements,
    query_painpoint_resolutions,
    query_satisfaction_scores,
    query_time_to_outcome,
)

# JTBD Metrics - Jobs-to-be-Done tracking
from .jtbd_metrics import (
    JobCompletion,
    JobStatus,
    OutcomeAchieved,
    OutcomeStatus,
    PainpointCategory,
    PainpointResolved,
    SatisfactionLevel,
    TimeToOutcome,
    UserSatisfaction,
    track_job_completion,
    track_outcome_achieved,
    track_painpoint_resolved,
    track_time_to_outcome,
    track_user_satisfaction,
)

# Process - Subprocess execution
from .process import run, run_command, run_logged, which

# Semantic Conventions - OTEL attribute names
from .semconv import (
    CacheAttributes,
    CacheOperations,
    CliAttributes,
    CliOperations,
    GitHubAttributes,
    GitHubOperations,
    ProcessAttributes,
    ProcessOperations,
    ProjectAttributes,
    ProjectOperations,
    SpecAttributes,
    SpecOperations,
    TemplateAttributes,
    TemplateOperations,
    TestAttributes,
    TestOperations,
    WorkflowAttributes,
    WorkflowOperations,
    get_common_attributes,
)

# Shell - Rich terminal output
from .shell import (
    colour,
    colour_stderr,
    dump_json,
    install_rich,
    markdown,
    progress_bar,
    rich_table,
    timed,
)

# Telemetry - OpenTelemetry instrumentation
from .telemetry import (
    OTEL_AVAILABLE,
    metric_counter,
    metric_histogram,
    record_exception,
    span,
)

__all__ = [
    "OTEL_AVAILABLE",
    "CacheAttributes",
    "CacheOperations",
    # Semantic Conventions
    "CliAttributes",
    "CliOperations",
    "ConfigurationError",
    "ErrorCategory",
    "ErrorSeverity",
    "ExitCode",
    # JTBD Measurement
    "FeatureEffectiveness",
    "GitHubAttributes",
    "GitHubOperations",
    # JTBD Metrics
    "JTBDMetrics",
    "JobCompletion",
    "JobStatus",
    "NetworkError",
    "OutcomeAchieved",
    "OutcomeDeliveryAnalysis",
    "OutcomeStatus",
    "PainpointCategory",
    "PainpointResolved",
    "ProcessAttributes",
    "ProcessOperations",
    "ProjectAttributes",
    "ProjectOperations",
    "SatisfactionLevel",
    "SpecAttributes",
    "SpecOperations",
    "SpecifyConfig",
    # Error Handling
    "SpecifyError",
    "TemplateAttributes",
    "TemplateOperations",
    "TestAttributes",
    "TestOperations",
    "TimeToOutcome",
    "ToolNotFoundError",
    "UserSatisfaction",
    "ValidationError",
    "WorkflowAttributes",
    "WorkflowOperations",
    "_format_rate_limit_error",
    "_github_auth_headers",
    # GitHub (legacy)
    "_github_token",
    "_parse_rate_limit_headers",
    "add_span_attributes",
    "add_span_event",
    "analyze_feature_effectiveness",
    "analyze_outcome_delivery",
    # Cache
    "cache_key",
    "cache_stats",
    "clear_cache",
    # Shell
    "colour",
    "colour_stderr",
    "download_template_from_github",
    "dump_json",
    "env_or",
    "export_metrics",
    "extract_jtbd_metrics",
    "format_error_message",
    "generate_jtbd_report",
    "get_cache_dir",
    "get_cached",
    "get_common_attributes",
    # Configuration
    "get_config",
    "get_config_dir",
    "handle_cli_error",
    "init_git_repo",
    "install_rich",
    # Instrumentation
    "instrument_command",
    "instrument_subcommand",
    # Git (legacy)
    "is_git_repo",
    "markdown",
    "metric_counter",
    "metric_histogram",
    "progress_bar",
    "query_job_completions",
    "query_outcome_achievements",
    "query_painpoint_resolutions",
    "query_satisfaction_scores",
    "query_time_to_outcome",
    "record_exception",
    "rich_table",
    # Process
    "run",
    "run_command",
    "run_logged",
    "set_cached",
    # Telemetry
    "span",
    "timed",
    "track_job_completion",
    "track_outcome_achieved",
    "track_painpoint_resolved",
    "track_time_to_outcome",
    "track_user_satisfaction",
    "which",
    "with_error_handling",
]
