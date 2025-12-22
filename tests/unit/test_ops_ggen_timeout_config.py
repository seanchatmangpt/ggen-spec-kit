"""Unit tests for ggen timeout configuration."""

from __future__ import annotations

import pytest

from specify_cli.ops.ggen_timeout_config import (
    DEFAULT_TIMEOUT,
    get_transformation_timeout,
    parse_timeout,
)


class TestParseTimeout:
    """Tests for timeout parsing."""

    def test_parse_none_returns_default(self) -> None:
        """Test None returns default timeout."""
        assert parse_timeout(None) == DEFAULT_TIMEOUT

    def test_parse_integer(self) -> None:
        """Test parsing integer seconds."""
        assert parse_timeout(30) == 30
        assert parse_timeout(120) == 120
        assert parse_timeout(300) == 300

    def test_parse_seconds_suffix(self) -> None:
        """Test parsing with 's' suffix."""
        assert parse_timeout("30s") == 30
        assert parse_timeout("30 s") == 30
        assert parse_timeout("120s") == 120

    def test_parse_minutes_suffix(self) -> None:
        """Test parsing with 'm' suffix."""
        assert parse_timeout("5m") == 300
        assert parse_timeout("5 m") == 300
        assert parse_timeout("10m") == 600

    def test_parse_string_number(self) -> None:
        """Test parsing string without suffix."""
        assert parse_timeout("30") == 30
        assert parse_timeout("120") == 120

    def test_parse_case_insensitive(self) -> None:
        """Test case insensitivity."""
        assert parse_timeout("30S") == 30
        assert parse_timeout("5M") == 300

    def test_parse_invalid_format(self) -> None:
        """Test invalid format raises error."""
        with pytest.raises(ValueError, match="Invalid timeout format"):
            parse_timeout("invalid")

        with pytest.raises(ValueError, match="Invalid timeout format"):
            parse_timeout("30x")

    def test_parse_negative_raises_error(self) -> None:
        """Test negative values raise error."""
        with pytest.raises(ValueError, match="positive"):
            parse_timeout(-10)

        with pytest.raises(ValueError, match="positive"):
            parse_timeout("-5s")

    def test_parse_zero_raises_error(self) -> None:
        """Test zero raises error."""
        with pytest.raises(ValueError, match="positive"):
            parse_timeout(0)

        with pytest.raises(ValueError, match="positive"):
            parse_timeout("0s")

    def test_parse_wrong_type(self) -> None:
        """Test wrong type raises error."""
        with pytest.raises(ValueError, match="must be int, str, or None"):
            parse_timeout([30])  # type: ignore

        with pytest.raises(ValueError, match="must be int, str, or None"):
            parse_timeout({"timeout": 30})  # type: ignore


class TestGetTransformationTimeout:
    """Tests for transformation timeout configuration."""

    def test_transformation_specific_timeout(self) -> None:
        """Test transformation-specific timeout takes precedence."""
        transform = {"name": "test", "timeout": "30s"}
        assert get_transformation_timeout(transform) == 30

    def test_global_default_fallback(self) -> None:
        """Test fallback to global default."""
        transform = {"name": "test"}
        assert get_transformation_timeout(transform, global_default=60) == 60

    def test_builtin_default_fallback(self) -> None:
        """Test fallback to built-in default."""
        transform = {"name": "test"}
        result = get_transformation_timeout(transform)
        assert result == DEFAULT_TIMEOUT

    def test_transformation_overrides_global(self) -> None:
        """Test transformation timeout overrides global."""
        transform = {"name": "test", "timeout": "20s"}
        assert get_transformation_timeout(transform, global_default=60) == 20

    def test_invalid_timeout_in_transformation(self) -> None:
        """Test invalid timeout in transformation."""
        transform = {"name": "test", "timeout": "invalid"}
        with pytest.raises(ValueError, match="Invalid timeout format"):
            get_transformation_timeout(transform)
