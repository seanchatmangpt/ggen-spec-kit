"""
specify_cli.core.telemetry
--------------------------
OpenTelemetry integration and telemetry utilities for specify-cli.

This module provides comprehensive telemetry capabilities:

* **Logging Setup**: Always exports ``setup_logging`` - used by CLI startup
* **Span Management**: Context-manager ``span(name, **attrs)`` for distributed tracing
* **Metrics Collection**: Functions for counters, histograms, and gauges
* **Exception Recording**: Utilities for recording exceptions with semantic conventions
* **Graceful Degradation**: No-op implementations when OpenTelemetry is not available

The module automatically initializes OpenTelemetry when the environment variable
`OTEL_EXPORTER_OTLP_ENDPOINT` is set and the `opentelemetry-sdk` package is installed.
Otherwise, it provides no-op implementations that allow the application to run normally.

Example
-------
    # Basic span usage
    with span("my_operation", operation_type="custom"):
        result = perform_operation()

    # Metrics collection
    counter = metric_counter("my.operation.calls")
    counter(1, {"operation": "add"})

    # Exception recording
    try:
        risky_operation()
    except Exception as e:
        record_exception(e, attributes={"operation": "risky"})
        raise

Environment Variables
--------------------
- OTEL_EXPORTER_OTLP_ENDPOINT : OpenTelemetry collector endpoint
- OTEL_SERVICE_NAME : Service name for telemetry (default: "specify-cli")
- OTEL_SERVICE_VERSION : Service version for telemetry
- SPECIFY_OTEL_ENABLED : Enable/disable OTEL (default: "true")

See Also
--------
- :mod:`specify_cli.core.instrumentation` : Command instrumentation decorators
- :mod:`specify_cli.core.semconv` : Semantic conventions
"""

from __future__ import annotations

import logging
import os
import platform
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable


# --------------------------------------------------------------------------- #
# Public helper: plain logging                                                #
# --------------------------------------------------------------------------- #
def setup_logging(level: str = "INFO") -> None:
    """
    Initialize root logging configuration once, idempotently.

    This function sets up the basic logging configuration for the specify-cli application.
    It's called by the CLI on startup and ensures consistent logging across
    all modules. The function is idempotent - calling it multiple times has no
    additional effect.

    Parameters
    ----------
    level : str, optional
        Logging level to use. Must be a valid logging level name
        (DEBUG, INFO, WARNING, ERROR, CRITICAL). Default is "INFO".

    Notes
    -----
    The logging configuration includes:
    - Timestamp format: HH:MM:SS
    - Level name with 8-character padding
    - Logger name
    - Message content

    Example
    -------
    >>> setup_logging("DEBUG")
    >>> logging.getLogger("specify_cli").info("Application started")
    14:30:25 INFO     specify_cli | Application started
    """
    if logging.getLogger().handlers:
        return  # already configured

    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)-8s %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )


# --------------------------------------------------------------------------- #
# Check if OTEL is explicitly disabled                                        #
# --------------------------------------------------------------------------- #
_OTEL_DISABLED = os.getenv("SPECIFY_OTEL_ENABLED", "true").lower() in ("false", "0", "no")


# --------------------------------------------------------------------------- #
# Optional OpenTelemetry                                                      #
# --------------------------------------------------------------------------- #
if not _OTEL_DISABLED:
    try:
        from opentelemetry import metrics, trace
        from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.metrics import MeterProvider
        from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        # Only initialize if OTEL endpoint is configured
        _OTEL_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
        if not _OTEL_ENDPOINT:
            raise ImportError("OTEL_EXPORTER_OTLP_ENDPOINT not set")

        _RESOURCE = Resource.create(
            {
                "service.name": os.getenv("OTEL_SERVICE_NAME", "specify-cli"),
                "service.instance.id": os.getenv("HOSTNAME", "localhost"),
                "os.type": platform.system().lower(),
            }
        )

        # Setup Traces
        _TRACE_PROVIDER = TracerProvider(resource=_RESOURCE)
        _TRACE_PROVIDER.add_span_processor(
            BatchSpanProcessor(OTLPSpanExporter(endpoint=_OTEL_ENDPOINT))
        )
        trace.set_tracer_provider(_TRACE_PROVIDER)
        _TRACER = trace.get_tracer("specify-cli")

        # Setup Metrics
        _METRIC_READER = PeriodicExportingMetricReader(
            OTLPMetricExporter(endpoint=_OTEL_ENDPOINT),
            export_interval_millis=5000,  # Export every 5 seconds
        )
        _METRIC_PROVIDER = MeterProvider(resource=_RESOURCE, metric_readers=[_METRIC_READER])
        metrics.set_meter_provider(_METRIC_PROVIDER)
        _METER = metrics.get_meter("specify-cli")

        @contextmanager
        def span(name: str, span_kind: Any | None = None, **attrs: Any) -> None:
            """Create an OTEL span with the given name and attributes."""
            kwargs: dict[str, Any] = {"attributes": attrs}
            if span_kind is not None:
                kwargs["kind"] = span_kind
            with _TRACER.start_as_current_span(name, **kwargs) as current_span:
                yield current_span

        def metric_counter(name: str) -> Callable[[int], None]:
            """Create a counter metric."""
            return _METER.create_counter(name).add

        def metric_histogram(name: str, unit: str = "s") -> Callable[[float], None]:
            """
            Create a histogram metric for recording distributions.

            Parameters
            ----------
            name : str
                The name of the histogram metric.
            unit : str, optional
                The unit of measurement. Default is "s" (seconds).

            Returns
            -------
            Callable[[float], None]
                A function that records values in the histogram.
            """
            return _METER.create_histogram(name, unit=unit).record

        def metric_gauge(name: str) -> Callable[[float], None]:
            """
            Create a gauge metric for recording current values.

            Parameters
            ----------
            name : str
                The name of the gauge metric.

            Returns
            -------
            Callable[[float], None]
                A function that updates the gauge value.
            """
            return _METER.create_up_down_counter(name).add

        def record_exception(
            e: Exception, escaped: bool = True, attributes: dict[str, Any] | None = None
        ) -> None:
            """
            Record an exception in the current span with semantic conventions.

            Parameters
            ----------
            e : Exception
                The exception to record.
            escaped : bool, optional
                Whether the exception escaped the current span. Default is True.
            attributes : dict[str, Any], optional
                Additional attributes to record with the exception.
            """
            current_span = trace.get_current_span()
            if current_span.is_recording():
                # Record the exception
                current_span.record_exception(e, escaped=escaped)

                # Add semantic convention attributes
                exc_attrs: dict[str, Any] = {
                    "exception.type": type(e).__name__,
                    "exception.message": str(e),
                    "exception.escaped": str(escaped),
                }

                # Add custom attributes if provided
                if attributes:
                    exc_attrs.update(attributes)

                # Add specific attributes for common errors
                if hasattr(e, "returncode"):  # subprocess.CalledProcessError
                    exc_attrs["process.exit_code"] = e.returncode
                    if hasattr(e, "cmd"):
                        exc_attrs["process.command"] = (
                            " ".join(e.cmd) if isinstance(e.cmd, list) else str(e.cmd)
                        )
                elif hasattr(e, "filename"):  # FileNotFoundError, IOError
                    exc_attrs["file.path"] = str(e.filename)

                # Add event with attributes
                current_span.add_event("exception", exc_attrs)

                # Set error status
                from opentelemetry.trace import Status, StatusCode

                current_span.set_status(Status(StatusCode.ERROR, str(e)))

        def get_current_span() -> Any:
            """Get the current active span."""
            return trace.get_current_span()

        def get_tracer() -> Any:
            """Get the tracer instance."""
            return _TRACER

        def set_span_status(status_code: str, description: str = "") -> None:
            """
            Set the status of the current span.

            Parameters
            ----------
            status_code : str
                The status code to set. Valid values are "OK", "ERROR", "UNSET".
            description : str, optional
                A description of the status.
            """
            from opentelemetry.trace import Status, StatusCode

            current_span = trace.get_current_span()
            if current_span.is_recording():
                if status_code == "OK":
                    current_span.set_status(Status(StatusCode.OK))
                elif status_code == "ERROR":
                    current_span.set_status(Status(StatusCode.ERROR, description))
                else:
                    current_span.set_status(Status(StatusCode.UNSET))

        # Mark OTEL as available
        OTEL_AVAILABLE = True

    except ImportError:
        # Fall through to no-op implementations
        OTEL_AVAILABLE = False
else:
    OTEL_AVAILABLE = False


# --------------------------------------------------------------------------- #
# No-op implementations when OTEL is not available                            #
# --------------------------------------------------------------------------- #
if not OTEL_AVAILABLE:

    @contextmanager
    def span(name: str, span_kind: Any | None = None, **attrs: Any):  # type: ignore[misc]
        """No-op span context manager."""

        class _NoopSpan:
            def is_recording(self) -> bool:
                return False

            def set_status(self, *args: Any, **kwargs: Any) -> None:
                pass

            def set_attribute(self, *args: Any, **kwargs: Any) -> None:
                pass

            def set_attributes(self, *args: Any, **kwargs: Any) -> None:
                pass

            def add_event(self, *args: Any, **kwargs: Any) -> None:
                pass

        yield _NoopSpan()

    def metric_counter(name: str) -> Callable[[int], None]:  # type: ignore[misc]
        """No-op counter."""

        def _noop(_: int = 1, **__: Any) -> None:
            pass

        return _noop

    def metric_histogram(name: str, unit: str = "s") -> Callable[[float], None]:  # type: ignore[misc]
        """No-op histogram."""

        def _noop(_: float, **__: Any) -> None:
            pass

        return _noop

    def metric_gauge(name: str) -> Callable[[float], None]:  # type: ignore[misc]
        """No-op gauge."""

        def _noop(_: float, **__: Any) -> None:
            pass

        return _noop

    def record_exception(
        e: Exception, escaped: bool = True, attributes: dict[str, Any] | None = None
    ) -> None:
        """No-op exception recording."""

    def get_current_span() -> Any:  # type: ignore[misc]
        """No-op get current span."""

        class _NoopSpan:
            def is_recording(self) -> bool:
                return False

            def set_status(self, *args: Any, **kwargs: Any) -> None:
                pass

            def set_attributes(self, *args: Any, **kwargs: Any) -> None:
                pass

            def add_event(self, *args: Any, **kwargs: Any) -> None:
                pass

        return _NoopSpan()

    def get_tracer() -> None:  # type: ignore[misc]
        """No-op get tracer."""
        return

    def set_span_status(status_code: str, description: str = "") -> None:
        """No-op set span status."""


__all__ = [
    "OTEL_AVAILABLE",
    "get_current_span",
    "get_tracer",
    "metric_counter",
    "metric_gauge",
    "metric_histogram",
    "record_exception",
    "set_span_status",
    "setup_logging",
    "span",
]
