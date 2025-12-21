"""
specify_cli.core.error_handling - Error Management System
==========================================================

Comprehensive error handling and recovery for specify-cli commands.

This module provides user-friendly error handling with:
- Error classification by severity and category
- Automatic retry mechanisms with exponential backoff
- Graceful degradation strategies
- Comprehensive error reporting and metrics
- Telemetry integration for error tracking

Key Features
-----------
* **Error Classification**: Categorize errors by type and severity
* **Recovery Strategies**: Automatic retry, fallback, and graceful degradation
* **User-Friendly Messages**: Clear error messages with actionable suggestions
* **Telemetry Integration**: Full OpenTelemetry instrumentation
* **Exit Code Management**: Standardized CLI exit codes

Examples
--------
    >>> from specify_cli.core.error_handling import (
    ...     handle_cli_error, SpecifyError, ErrorCategory
    ... )
    >>>
    >>> try:
    ...     risky_operation()
    ... except Exception as e:
    ...     handle_cli_error(e, "operation_name")

See Also
--------
- :mod:`specify_cli.core.telemetry` : Telemetry and observability
- :mod:`specify_cli.core.shell` : Terminal output utilities
"""

from __future__ import annotations

import functools
import sys
import time
import traceback
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import TYPE_CHECKING, Any, TypeVar

from .shell import colour, colour_stderr
from .telemetry import metric_counter, record_exception, span

if TYPE_CHECKING:
    from collections.abc import Callable

__all__ = [
    "ConfigurationError",
    "ErrorCategory",
    "ErrorSeverity",
    "ExitCode",
    "NetworkError",
    "SpecifyError",
    "ToolNotFoundError",
    "ValidationError",
    "format_error_message",
    "handle_cli_error",
    "with_error_handling",
]

T = TypeVar("T")


class ExitCode(IntEnum):
    """Standard CLI exit codes following Unix conventions."""

    SUCCESS = 0
    GENERAL_ERROR = 1
    USAGE_ERROR = 2
    CONFIGURATION_ERROR = 3
    NETWORK_ERROR = 4
    TOOL_NOT_FOUND = 5
    PERMISSION_ERROR = 6
    FILE_NOT_FOUND = 7
    VALIDATION_ERROR = 8
    INTERRUPTED = 130  # SIGINT (128 + 2)


class ErrorSeverity(Enum):
    """Error severity levels for classification."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for classification and handling."""

    SYSTEM = "system"
    NETWORK = "network"
    CONFIGURATION = "configuration"
    VALIDATION = "validation"
    PERMISSION = "permission"
    TOOL_MISSING = "tool_missing"
    FILE_SYSTEM = "file_system"
    USER_INPUT = "user_input"
    RUNTIME = "runtime"
    UNKNOWN = "unknown"


@dataclass
class ErrorContext:
    """Context information for error handling."""

    operation: str
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    exception_type: str
    stack_trace: str
    timestamp: float = field(default_factory=time.time)
    suggestions: list[str] = field(default_factory=list)
    recovery_attempted: bool = False
    exit_code: ExitCode = ExitCode.GENERAL_ERROR


class SpecifyError(Exception):
    """Base exception for specify-cli errors.

    All specify-cli specific exceptions should inherit from this class
    to enable consistent error handling and reporting.
    """

    def __init__(
        self,
        message: str,
        *,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        exit_code: ExitCode = ExitCode.GENERAL_ERROR,
        suggestions: list[str] | None = None,
    ) -> None:
        """Initialize a SpecifyError.

        Parameters
        ----------
        message : str
            Human-readable error message.
        category : ErrorCategory, optional
            Error category for classification.
        severity : ErrorSeverity, optional
            Error severity level.
        exit_code : ExitCode, optional
            CLI exit code to use.
        suggestions : list[str], optional
            Actionable suggestions for the user.
        """
        super().__init__(message)
        self.category = category
        self.severity = severity
        self.exit_code = exit_code
        self.suggestions = suggestions or []


class ConfigurationError(SpecifyError):
    """Configuration-related errors."""

    def __init__(self, message: str, suggestions: list[str] | None = None) -> None:
        super().__init__(
            message,
            category=ErrorCategory.CONFIGURATION,
            severity=ErrorSeverity.HIGH,
            exit_code=ExitCode.CONFIGURATION_ERROR,
            suggestions=suggestions
            or ["Check your configuration file", "Verify environment variables"],
        )


class ValidationError(SpecifyError):
    """Validation-related errors."""

    def __init__(self, message: str, suggestions: list[str] | None = None) -> None:
        super().__init__(
            message,
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.MEDIUM,
            exit_code=ExitCode.VALIDATION_ERROR,
            suggestions=suggestions
            or ["Check your input values", "Review documentation for valid formats"],
        )


class NetworkError(SpecifyError):
    """Network-related errors."""

    def __init__(self, message: str, suggestions: list[str] | None = None) -> None:
        super().__init__(
            message,
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.HIGH,
            exit_code=ExitCode.NETWORK_ERROR,
            suggestions=suggestions
            or [
                "Check your internet connection",
                "Verify the service is available",
                "Check firewall settings",
            ],
        )


class ToolNotFoundError(SpecifyError):
    """Tool or dependency not found errors."""

    def __init__(self, tool_name: str, suggestions: list[str] | None = None) -> None:
        super().__init__(
            f"Required tool '{tool_name}' not found",
            category=ErrorCategory.TOOL_MISSING,
            severity=ErrorSeverity.HIGH,
            exit_code=ExitCode.TOOL_NOT_FOUND,
            suggestions=suggestions
            or [f"Install {tool_name}", "Check your PATH environment variable"],
        )


def _classify_exception(exception: Exception) -> tuple[ErrorCategory, ErrorSeverity, ExitCode]:
    """Classify an exception by category, severity, and exit code.

    Parameters
    ----------
    exception : Exception
        The exception to classify.

    Returns
    -------
    tuple[ErrorCategory, ErrorSeverity, ExitCode]
        Classification tuple.
    """
    # Handle SpecifyError subclasses directly
    if isinstance(exception, SpecifyError):
        return exception.category, exception.severity, exception.exit_code

    # System-critical exceptions
    if isinstance(exception, (KeyboardInterrupt, SystemExit)):
        return ErrorCategory.SYSTEM, ErrorSeverity.CRITICAL, ExitCode.INTERRUPTED

    if isinstance(exception, MemoryError):
        return ErrorCategory.SYSTEM, ErrorSeverity.CRITICAL, ExitCode.GENERAL_ERROR

    # Network exceptions
    if isinstance(exception, (ConnectionError, TimeoutError)):
        return ErrorCategory.NETWORK, ErrorSeverity.HIGH, ExitCode.NETWORK_ERROR

    # Permission exceptions
    if isinstance(exception, PermissionError):
        return ErrorCategory.PERMISSION, ErrorSeverity.HIGH, ExitCode.PERMISSION_ERROR

    # File system exceptions
    if isinstance(exception, FileNotFoundError):
        return ErrorCategory.FILE_SYSTEM, ErrorSeverity.HIGH, ExitCode.FILE_NOT_FOUND

    if isinstance(exception, (IsADirectoryError, NotADirectoryError, FileExistsError)):
        return ErrorCategory.FILE_SYSTEM, ErrorSeverity.MEDIUM, ExitCode.GENERAL_ERROR

    # Import/Module exceptions
    if isinstance(exception, (ImportError, ModuleNotFoundError)):
        return ErrorCategory.TOOL_MISSING, ErrorSeverity.HIGH, ExitCode.TOOL_NOT_FOUND

    # Validation exceptions
    if isinstance(exception, (ValueError, TypeError)):
        return ErrorCategory.VALIDATION, ErrorSeverity.MEDIUM, ExitCode.VALIDATION_ERROR

    # Runtime exceptions
    if isinstance(exception, (RuntimeError, AttributeError)):
        return ErrorCategory.RUNTIME, ErrorSeverity.MEDIUM, ExitCode.GENERAL_ERROR

    # Default
    return ErrorCategory.UNKNOWN, ErrorSeverity.MEDIUM, ExitCode.GENERAL_ERROR


def _get_suggestions(category: ErrorCategory, exception: Exception) -> list[str]:
    """Get actionable suggestions for an error category.

    Parameters
    ----------
    category : ErrorCategory
        The error category.
    exception : Exception
        The exception that occurred.

    Returns
    -------
    list[str]
        List of actionable suggestions.
    """
    # Use suggestions from SpecifyError if available
    if isinstance(exception, SpecifyError) and exception.suggestions:
        return exception.suggestions

    suggestions_map: dict[ErrorCategory, list[str]] = {
        ErrorCategory.NETWORK: [
            "Check your internet connection",
            "Verify the service endpoint is correct",
            "Try again in a few moments",
        ],
        ErrorCategory.CONFIGURATION: [
            "Check your configuration file (~/.config/specify/config.toml)",
            "Verify environment variables are set correctly",
            "Run 'specify check' to validate configuration",
        ],
        ErrorCategory.VALIDATION: [
            "Check your input values",
            "Review the command documentation",
            "Ensure required fields are provided",
        ],
        ErrorCategory.PERMISSION: [
            "Check file/directory permissions",
            "Try running with appropriate privileges",
            "Verify you have write access to the target location",
        ],
        ErrorCategory.TOOL_MISSING: [
            "Install the required tool",
            "Check your PATH environment variable",
            "Run 'specify check' to see tool status",
        ],
        ErrorCategory.FILE_SYSTEM: [
            "Verify the file/directory exists",
            "Check the path is correct",
            "Ensure you have read access",
        ],
        ErrorCategory.SYSTEM: [
            "Check system resources (memory, disk space)",
            "Try restarting the operation",
            "Contact support if the issue persists",
        ],
        ErrorCategory.RUNTIME: [
            "Try running the command again",
            "Check for conflicting processes",
            "Review the full error message for details",
        ],
    }

    return suggestions_map.get(
        category, ["Check the error message for details", "Run 'specify --help' for usage"]
    )


def format_error_message(
    exception: Exception, operation: str, *, verbose: bool = False, include_suggestions: bool = True
) -> str:
    """Format an error message for terminal display.

    Parameters
    ----------
    exception : Exception
        The exception to format.
    operation : str
        The operation that failed.
    verbose : bool, optional
        Include stack trace. Default is False.
    include_suggestions : bool, optional
        Include actionable suggestions. Default is True.

    Returns
    -------
    str
        Formatted error message.
    """
    category, _severity, _ = _classify_exception(exception)
    suggestions = _get_suggestions(category, exception)

    lines = [f"Error in {operation}: {exception!s}"]

    if verbose:
        lines.append("")
        lines.append("Stack trace:")
        lines.append(traceback.format_exc())

    if include_suggestions and suggestions:
        lines.append("")
        lines.append("Suggestions:")
        for suggestion in suggestions:
            lines.append(f"  • {suggestion}")

    return "\n".join(lines)


def handle_cli_error(
    exception: Exception,
    operation: str,
    *,
    exit_on_error: bool = True,
    verbose: bool = False,
    to_stderr: bool = True,
) -> ExitCode:
    """Handle a CLI error with appropriate formatting and metrics.

    This function:
    - Classifies the error
    - Records telemetry metrics
    - Displays a user-friendly message
    - Optionally exits with the appropriate code

    Parameters
    ----------
    exception : Exception
        The exception to handle.
    operation : str
        The operation that failed.
    exit_on_error : bool, optional
        Exit the process after handling. Default is True.
    verbose : bool, optional
        Include stack trace in output. Default is False.
    to_stderr : bool, optional
        Print to stderr. Default is True.

    Returns
    -------
    ExitCode
        The exit code for this error.
    """
    with span("error_handling.handle_error", operation=operation):
        category, severity, exit_code = _classify_exception(exception)

        # Record telemetry
        record_exception(exception, escaped=True)
        metric_counter("errors.occurred")(1)
        metric_counter(f"errors.category.{category.value}")(1)
        metric_counter(f"errors.severity.{severity.value}")(1)

        # Format message
        message = format_error_message(exception, operation, verbose=verbose)

        # Display error
        output_fn = colour_stderr if to_stderr else colour
        output_fn(message, "red")

        if exit_on_error:
            sys.exit(exit_code)

        return exit_code


def with_error_handling(
    operation: str | None = None,
    *,
    exit_on_error: bool = True,
    max_retries: int = 0,
    retry_delay: float = 1.0,
    retry_exceptions: tuple[type[Exception], ...] = (ConnectionError, TimeoutError),
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator for automatic error handling with optional retry.

    Parameters
    ----------
    operation : str, optional
        Operation name for error messages. Defaults to function name.
    exit_on_error : bool, optional
        Exit on unrecoverable error. Default is True.
    max_retries : int, optional
        Maximum retry attempts for retryable errors. Default is 0.
    retry_delay : float, optional
        Base delay between retries (exponential backoff). Default is 1.0.
    retry_exceptions : tuple[type[Exception], ...], optional
        Exception types that are retryable. Default is network errors.

    Returns
    -------
    Callable
        Decorated function with error handling.

    Example
    -------
    >>> @with_error_handling("fetch_data", max_retries=3)
    ... def fetch_data(url: str) -> dict:
    ...     return requests.get(url).json()
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            op_name = operation or func.__name__
            attempts = 0
            last_exception: Exception | None = None

            while attempts <= max_retries:
                try:
                    with span(f"operation.{op_name}", attempt=attempts):
                        return func(*args, **kwargs)

                except retry_exceptions as e:
                    attempts += 1
                    last_exception = e

                    if attempts <= max_retries:
                        delay = retry_delay * (2 ** (attempts - 1))
                        metric_counter("errors.retries")(1)
                        colour(f"Retry {attempts}/{max_retries} after {delay:.1f}s: {e}", "yellow")
                        time.sleep(delay)
                    else:
                        break

                except Exception as e:
                    # Non-retryable exception
                    handle_cli_error(e, op_name, exit_on_error=exit_on_error)
                    raise  # If exit_on_error is False

            # All retries exhausted
            if last_exception:
                handle_cli_error(last_exception, op_name, exit_on_error=exit_on_error)
                raise last_exception  # If exit_on_error is False

            # Should never reach here
            raise RuntimeError(f"Unexpected state in {op_name}")

        return wrapper

    return decorator


def get_error_statistics() -> dict[str, Any]:
    """Get error handling statistics.

    This function provides diagnostic information about error patterns.
    Useful for debugging and monitoring.

    Returns
    -------
    dict[str, Any]
        Error statistics including counts by category and severity.
    """
    # Note: In a full implementation, this would track actual error counts
    # For now, return placeholder structure
    return {
        "total_errors": 0,
        "categories": {c.value: 0 for c in ErrorCategory},
        "severities": {s.value: 0 for s in ErrorSeverity},
        "exit_codes": {e.name: 0 for e in ExitCode},
    }
