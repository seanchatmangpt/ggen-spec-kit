"""
specify_cli.core.instrumentation
--------------------------------
OpenTelemetry instrumentation decorators and utilities for CLI commands.

This module provides decorators and utilities to automatically instrument CLI commands
with OpenTelemetry spans and metrics, following semantic conventions.

The module includes:

* **Command Instrumentation**: `@instrument_command` decorator for CLI commands
* **Subcommand Instrumentation**: `@instrument_subcommand` decorator for subcommands
* **Attribute Management**: Functions to add attributes and events to spans
* **Graceful Degradation**: No-op implementations when OpenTelemetry is not available

Example
-------
    @app.command()
    @instrument_command("my_command")
    def my_command(name: str, verbose: bool = False):
        add_span_attributes(custom_name=name, verbose_mode=verbose)

        with span("my_operation", operation_type="custom"):
            result = perform_operation(name)
            return result

See Also
--------
- :mod:`specify_cli.core.telemetry` : Core telemetry functions
- :mod:`specify_cli.core.semconv` : Semantic conventions
"""

from __future__ import annotations

import json
from collections.abc import Callable
from functools import wraps
from typing import Any

from .telemetry import metric_counter, record_exception, span, OTEL_AVAILABLE

# Import typer only when needed to avoid circular dependencies
try:
    import typer

    TYPER_AVAILABLE = True
except ImportError:
    TYPER_AVAILABLE = False
    typer = None  # type: ignore[assignment]

# Try to import OTEL components for type checking and constants
try:
    from opentelemetry import trace
    from opentelemetry.trace import Status, StatusCode

    HAS_OTEL = True
except ImportError:
    HAS_OTEL = False

    # Define fallback types/constants for graceful degradation
    class StatusCode:  # type: ignore[no-redef]
        OK = 0
        ERROR = 1

    class Status:  # type: ignore[no-redef]
        def __init__(self, code: int, description: str | None = None) -> None:
            self.code = code
            self.description = description

    class trace:  # type: ignore[no-redef]
        class SpanKind:
            SERVER = 1

        @staticmethod
        def get_current_span() -> Any:
            class DummySpan:
                def set_attribute(self, key: str, value: Any) -> None:
                    pass

                def set_status(self, status: Any) -> None:
                    pass

                def add_event(self, name: str, attributes: dict[str, Any] | None = None) -> None:
                    pass

                def is_recording(self) -> bool:
                    return False

            return DummySpan()


def instrument_command(
    name: str | None = None, command_type: str = "cli", track_args: bool = True
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator to instrument CLI commands with OpenTelemetry.

    This decorator automatically creates a span for the decorated function and
    adds semantic convention attributes for CLI commands.

    Parameters
    ----------
    name : str, optional
        Override name for the command. If not provided, uses the function name.
    command_type : str, optional
        Type of command for span naming. Default is "cli".
    track_args : bool, optional
        Whether to track command arguments in telemetry. Default is True.

    Returns
    -------
    Callable
        A decorator function that wraps the original function with telemetry.

    Example
    -------
    >>> @app.command()
    ... @instrument_command("add_dependency")
    ... def add_dependency(ctx: typer.Context, package: str, dev: bool = False):
    ...     pass
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            command_name = name or func.__name__
            span_name = f"{command_type}.command.{command_name}"

            # Extract meaningful attributes from args/kwargs
            attributes: dict[str, Any] = {
                "cli.command": command_name,
                "cli.module": func.__module__.split(".")[-1],
                "code.function": func.__name__,
                "code.namespace": func.__module__,
            }

            # Add CLI-specific attributes
            if track_args and args:
                attributes["cli.args.count"] = len(args)
                # Check if first arg is Typer context
                if hasattr(args[0], "__class__") and args[0].__class__.__name__ == "Context":
                    ctx = args[0]
                    if hasattr(ctx, "invoked_subcommand"):
                        attributes["cli.subcommand"] = str(ctx.invoked_subcommand)

            # Add options from kwargs if present
            if kwargs:
                # Filter out Typer context and sensitive data
                safe_options = {
                    k: str(v)
                    for k, v in kwargs.items()
                    if k not in ("ctx", "password", "token", "secret", "key", "api_key")
                }
                if safe_options:
                    attributes["cli.options"] = json.dumps(safe_options)

            with span(
                span_name,
                span_kind=trace.SpanKind.SERVER if HAS_OTEL else None,
                **attributes,
            ):
                current_span = trace.get_current_span()

                # Increment command counter metric
                metric_counter(f"cli.command.{command_name}.calls")(1)

                try:
                    # Add pre-execution event
                    current_span.add_event("command.started", {"cli.command": command_name})

                    # Execute the actual command
                    result = func(*args, **kwargs)

                    # Success - set OK status
                    current_span.set_status(Status(StatusCode.OK))
                    current_span.add_event(
                        "command.completed", {"cli.command": command_name, "cli.success": True}
                    )

                    return result

                except Exception as e:
                    # Handle typer.Exit if available
                    if TYPER_AVAILABLE and typer and isinstance(e, typer.Exit):
                        exit_code = e.exit_code
                        if exit_code == 0:
                            current_span.set_status(Status(StatusCode.OK))
                        else:
                            current_span.set_status(
                                Status(StatusCode.ERROR, f"Exit code: {exit_code}")
                            )
                        current_span.set_attribute("cli.exit_code", exit_code)
                        raise
                    else:
                        # Error - record exception and set error status
                        record_exception(e, escaped=True)
                        current_span.set_status(Status(StatusCode.ERROR, str(e)))
                        current_span.add_event(
                            "command.failed",
                            {
                                "cli.command": command_name,
                                "cli.success": False,
                                "exception.type": type(e).__name__,
                            },
                        )

                        # Increment error counter
                        metric_counter(f"cli.command.{command_name}.errors")(1)
                        raise

        return wrapper

    return decorator


def instrument_subcommand(parent_command: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator for subcommands to maintain trace hierarchy.

    Parameters
    ----------
    parent_command : str
        Name of the parent command.

    Returns
    -------
    Callable
        Decorator that instruments as a subcommand.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        return instrument_command(
            f"{parent_command}_{func.__name__}", command_type="cli.subcommand"
        )(func)

    return decorator


def add_span_attributes(**attributes: Any) -> None:
    """
    Add attributes to the current span.

    Useful for adding command-specific attributes within the command implementation.

    Parameters
    ----------
    **attributes
        Key-value pairs to add as span attributes.
    """
    if HAS_OTEL:
        current_span = trace.get_current_span()
        for key, value in attributes.items():
            current_span.set_attribute(key, value)


def add_span_event(name: str, attributes: dict[str, Any] | None = None) -> None:
    """
    Add an event to the current span.

    Parameters
    ----------
    name : str
        Event name.
    attributes : dict[str, Any], optional
        Optional event attributes.
    """
    if HAS_OTEL:
        current_span = trace.get_current_span()
        if current_span.is_recording():
            current_span.add_event(name, attributes or {})


__all__ = [
    "instrument_command",
    "instrument_subcommand",
    "add_span_attributes",
    "add_span_event",
]
