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

# Telemetry - OpenTelemetry instrumentation
from .telemetry import (
    OTEL_AVAILABLE,
    metric_counter,
    metric_histogram,
    record_exception,
    span,
)

# Instrumentation - Command decorators
from .instrumentation import (
    add_span_attributes,
    add_span_event,
    instrument_command,
    instrument_subcommand,
)

# Process - Subprocess execution
from .process import run, run_command, run_logged, which

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

# Configuration - Settings management
from .config import (
    SpecifyConfig,
    env_or,
    get_cache_dir,
    get_config,
    get_config_dir,
)

# Cache - Result caching
from .cache import (
    cache_key,
    cache_stats,
    clear_cache,
    get_cached,
    set_cached,
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

# Semantic Conventions - OTEL attribute names
from .semconv import (
    CacheAttributes,
    CacheOperations,
    CliAttributes,
    CliOperations,
    get_common_attributes,
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

__all__ = [
    # Telemetry
    "span",
    "metric_counter",
    "metric_histogram",
    "record_exception",
    "OTEL_AVAILABLE",
    # Instrumentation
    "instrument_command",
    "instrument_subcommand",
    "add_span_attributes",
    "add_span_event",
    # Process
    "run",
    "run_logged",
    "run_command",
    "which",
    # Shell
    "colour",
    "colour_stderr",
    "dump_json",
    "markdown",
    "timed",
    "rich_table",
    "progress_bar",
    "install_rich",
    # Configuration
    "get_config",
    "get_cache_dir",
    "get_config_dir",
    "env_or",
    "SpecifyConfig",
    # Cache
    "cache_key",
    "get_cached",
    "set_cached",
    "clear_cache",
    "cache_stats",
    # Error Handling
    "SpecifyError",
    "ConfigurationError",
    "ValidationError",
    "NetworkError",
    "ToolNotFoundError",
    "ErrorSeverity",
    "ErrorCategory",
    "ExitCode",
    "handle_cli_error",
    "format_error_message",
    "with_error_handling",
    # Semantic Conventions
    "CliAttributes",
    "CliOperations",
    "ProcessAttributes",
    "ProcessOperations",
    "ProjectAttributes",
    "ProjectOperations",
    "WorkflowAttributes",
    "WorkflowOperations",
    "TestAttributes",
    "TestOperations",
    "SpecAttributes",
    "SpecOperations",
    "CacheAttributes",
    "CacheOperations",
    "GitHubAttributes",
    "GitHubOperations",
    "TemplateAttributes",
    "TemplateOperations",
    "get_common_attributes",
    # Git (legacy)
    "is_git_repo",
    "init_git_repo",
    # GitHub (legacy)
    "_github_token",
    "_github_auth_headers",
    "_parse_rate_limit_headers",
    "_format_rate_limit_error",
    "download_template_from_github",
]
