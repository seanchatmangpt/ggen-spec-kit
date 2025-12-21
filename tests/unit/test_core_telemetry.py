"""
Unit tests for specify_cli.core.telemetry module.

Tests cover telemetry utilities including graceful degradation when OTEL is unavailable.
"""

from __future__ import annotations

import logging
import os
from unittest.mock import MagicMock, patch

import pytest


class TestSetupLogging:
    """Tests for setup_logging() function."""

    def test_setup_logging_default_level(self) -> None:
        """Test setup_logging with default INFO level."""
        # Clear any existing handlers
        root_logger = logging.getLogger()
        original_handlers = root_logger.handlers[:]
        for handler in original_handlers:
            root_logger.removeHandler(handler)

        try:
            from specify_cli.core.telemetry import setup_logging

            setup_logging()

            assert root_logger.level == logging.INFO or len(root_logger.handlers) > 0
        finally:
            # Restore original handlers
            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)
            for handler in original_handlers:
                root_logger.addHandler(handler)

    def test_setup_logging_custom_level(self) -> None:
        """Test setup_logging with custom DEBUG level."""
        root_logger = logging.getLogger()
        original_handlers = root_logger.handlers[:]
        for handler in original_handlers:
            root_logger.removeHandler(handler)

        try:
            from specify_cli.core.telemetry import setup_logging

            setup_logging("DEBUG")

            # Verify handlers were added
            assert len(root_logger.handlers) > 0
        finally:
            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)
            for handler in original_handlers:
                root_logger.addHandler(handler)

    def test_setup_logging_idempotent(self) -> None:
        """Test setup_logging is idempotent."""
        root_logger = logging.getLogger()
        original_handlers = root_logger.handlers[:]

        # Clear and setup once
        for handler in original_handlers:
            root_logger.removeHandler(handler)

        try:
            from specify_cli.core.telemetry import setup_logging

            setup_logging()
            handler_count_1 = len(root_logger.handlers)

            setup_logging()  # Second call
            handler_count_2 = len(root_logger.handlers)

            # Should not add duplicate handlers
            assert handler_count_2 == handler_count_1
        finally:
            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)
            for handler in original_handlers:
                root_logger.addHandler(handler)


class TestNoopImplementations:
    """Tests for no-op implementations when OTEL is unavailable."""

    def test_span_noop(self, otel_disabled: None) -> None:
        """Test span context manager works as no-op."""
        # Re-import to get no-op version
        import importlib

        import specify_cli.core.telemetry as telemetry_module

        # Force reload with OTEL disabled
        with patch.dict(os.environ, {"SPECIFY_OTEL_ENABLED": "false"}):
            importlib.reload(telemetry_module)

            with telemetry_module.span("test_span", attr1="value1") as span:
                # No-op span should have is_recording() method
                assert hasattr(span, "is_recording")
                assert span.is_recording() is False

                # Should be able to call methods without error
                span.set_attribute("key", "value")
                span.set_status(None)
                span.add_event("event")

    def test_metric_counter_noop(self, otel_disabled: None) -> None:
        """Test metric_counter returns no-op function."""
        import importlib

        import specify_cli.core.telemetry as telemetry_module

        with patch.dict(os.environ, {"SPECIFY_OTEL_ENABLED": "false"}):
            importlib.reload(telemetry_module)

            counter = telemetry_module.metric_counter("test.counter")

            # Should not raise
            counter(1)
            counter(5)

    def test_metric_histogram_noop(self, otel_disabled: None) -> None:
        """Test metric_histogram returns no-op function."""
        import importlib

        import specify_cli.core.telemetry as telemetry_module

        with patch.dict(os.environ, {"SPECIFY_OTEL_ENABLED": "false"}):
            importlib.reload(telemetry_module)

            histogram = telemetry_module.metric_histogram("test.histogram")

            # Should not raise
            histogram(1.5)
            histogram(3.14)

    def test_metric_gauge_noop(self, otel_disabled: None) -> None:
        """Test metric_gauge returns no-op function."""
        import importlib

        import specify_cli.core.telemetry as telemetry_module

        with patch.dict(os.environ, {"SPECIFY_OTEL_ENABLED": "false"}):
            importlib.reload(telemetry_module)

            gauge = telemetry_module.metric_gauge("test.gauge")

            # Should not raise
            gauge(42.0)
            gauge(-10.0)

    def test_record_exception_noop(self, otel_disabled: None) -> None:
        """Test record_exception works as no-op."""
        import importlib

        import specify_cli.core.telemetry as telemetry_module

        with patch.dict(os.environ, {"SPECIFY_OTEL_ENABLED": "false"}):
            importlib.reload(telemetry_module)

            # Should not raise
            telemetry_module.record_exception(ValueError("test error"))
            telemetry_module.record_exception(
                RuntimeError("another error"), attributes={"key": "value"}
            )

    def test_get_current_span_noop(self, otel_disabled: None) -> None:
        """Test get_current_span returns no-op span."""
        import importlib

        import specify_cli.core.telemetry as telemetry_module

        with patch.dict(os.environ, {"SPECIFY_OTEL_ENABLED": "false"}):
            importlib.reload(telemetry_module)

            span = telemetry_module.get_current_span()

            assert hasattr(span, "is_recording")
            assert span.is_recording() is False

    def test_get_tracer_noop(self, otel_disabled: None) -> None:
        """Test get_tracer returns None when OTEL disabled."""
        import importlib

        import specify_cli.core.telemetry as telemetry_module

        with patch.dict(os.environ, {"SPECIFY_OTEL_ENABLED": "false"}):
            importlib.reload(telemetry_module)

            tracer = telemetry_module.get_tracer()

            assert tracer is None

    def test_set_span_status_noop(self, otel_disabled: None) -> None:
        """Test set_span_status works as no-op."""
        import importlib

        import specify_cli.core.telemetry as telemetry_module

        with patch.dict(os.environ, {"SPECIFY_OTEL_ENABLED": "false"}):
            importlib.reload(telemetry_module)

            # Should not raise
            telemetry_module.set_span_status("OK")
            telemetry_module.set_span_status("ERROR", "Something went wrong")
            telemetry_module.set_span_status("UNSET")


class TestOtelAvailableFlag:
    """Tests for OTEL_AVAILABLE flag."""

    def test_otel_available_when_disabled(self, otel_disabled: None) -> None:
        """Test OTEL_AVAILABLE is False when explicitly disabled."""
        import importlib

        import specify_cli.core.telemetry as telemetry_module

        with patch.dict(os.environ, {"SPECIFY_OTEL_ENABLED": "false"}):
            importlib.reload(telemetry_module)

            assert telemetry_module.OTEL_AVAILABLE is False

    def test_otel_disabled_variations(self) -> None:
        """Test various ways to disable OTEL."""
        import importlib

        import specify_cli.core.telemetry as telemetry_module

        for value in ["false", "0", "no", "False", "FALSE", "NO"]:
            with patch.dict(os.environ, {"SPECIFY_OTEL_ENABLED": value}):
                importlib.reload(telemetry_module)
                assert telemetry_module.OTEL_AVAILABLE is False, f"Failed for value: {value}"


class TestSpanContextManager:
    """Tests for span context manager behavior."""

    def test_span_with_attributes(self, otel_disabled: None) -> None:
        """Test span accepts keyword attributes."""
        import importlib

        import specify_cli.core.telemetry as telemetry_module

        with patch.dict(os.environ, {"SPECIFY_OTEL_ENABLED": "false"}):
            importlib.reload(telemetry_module)

            with telemetry_module.span(
                "test_span",
                operation="test",
                component="telemetry",
                value=42,
            ) as span:
                assert span is not None

    def test_span_with_kind(self, otel_disabled: None) -> None:
        """Test span accepts span_kind parameter."""
        import importlib

        import specify_cli.core.telemetry as telemetry_module

        with patch.dict(os.environ, {"SPECIFY_OTEL_ENABLED": "false"}):
            importlib.reload(telemetry_module)

            with telemetry_module.span("test_span", span_kind="internal") as span:
                assert span is not None

    def test_span_exception_propagation(self, otel_disabled: None) -> None:
        """Test exceptions propagate through span."""
        import importlib

        import specify_cli.core.telemetry as telemetry_module

        with patch.dict(os.environ, {"SPECIFY_OTEL_ENABLED": "false"}):
            importlib.reload(telemetry_module)

            with pytest.raises(ValueError, match="test error"):
                with telemetry_module.span("failing_span"):
                    raise ValueError("test error")


class TestModuleExports:
    """Tests for module __all__ exports."""

    def test_all_exports(self) -> None:
        """Test all expected functions are exported."""
        from specify_cli.core import telemetry

        expected_exports = [
            "setup_logging",
            "span",
            "metric_counter",
            "metric_histogram",
            "metric_gauge",
            "record_exception",
            "get_current_span",
            "get_tracer",
            "set_span_status",
            "OTEL_AVAILABLE",
        ]

        for export in expected_exports:
            assert hasattr(telemetry, export), f"Missing export: {export}"

    def test_all_attribute_matches_exports(self) -> None:
        """Test __all__ contains all expected exports."""
        from specify_cli.core import telemetry

        expected_exports = {
            "setup_logging",
            "span",
            "metric_counter",
            "metric_histogram",
            "metric_gauge",
            "record_exception",
            "get_current_span",
            "get_tracer",
            "set_span_status",
            "OTEL_AVAILABLE",
        }

        assert set(telemetry.__all__) == expected_exports
