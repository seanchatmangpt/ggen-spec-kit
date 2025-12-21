"""Integration tests for runtime.lint with real tool execution."""

from __future__ import annotations

from pathlib import Path

import pytest

from specify_cli.runtime.lint import (
    LintError,
    is_mypy_available,
    is_ruff_available,
    run_mypy,
    run_ruff_check,
    run_ruff_format,
)


class TestToolAvailability:
    """Test tool availability checks."""

    def test_ruff_available(self) -> None:
        """Ruff should be available in dev environment."""
        assert is_ruff_available()

    def test_mypy_available(self) -> None:
        """Mypy should be available in dev environment."""
        assert is_mypy_available()


class TestRuffCheck:
    """Test ruff check execution."""

    def test_run_ruff_check_on_self(self) -> None:
        """Run ruff check on lint.py itself."""
        lint_file = Path(__file__).parent.parent.parent / "src/specify_cli/runtime/lint.py"
        assert lint_file.exists()

        result = run_ruff_check([lint_file])

        assert isinstance(result, dict)
        assert "success" in result
        assert "violations" in result
        assert "output" in result
        assert "duration" in result
        assert isinstance(result["success"], bool)
        assert isinstance(result["duration"], float)

    def test_run_ruff_check_nonexistent_path(self) -> None:
        """Ruff check should raise error for non-existent path."""
        nonexistent = Path("/nonexistent/path/to/file.py")

        with pytest.raises(LintError, match="does not exist"):
            run_ruff_check([nonexistent])

    def test_run_ruff_check_with_json_format(self) -> None:
        """Ruff check should support JSON output format."""
        lint_file = Path(__file__).parent.parent.parent / "src/specify_cli/runtime/lint.py"

        result = run_ruff_check([lint_file], output_format="json")

        assert isinstance(result, dict)
        assert "success" in result
        assert "violations" in result
        assert isinstance(result["violations"], list)


class TestRuffFormat:
    """Test ruff format execution."""

    def test_run_ruff_format_check_on_self(self) -> None:
        """Run ruff format check on lint.py (should already be formatted)."""
        lint_file = Path(__file__).parent.parent.parent / "src/specify_cli/runtime/lint.py"
        assert lint_file.exists()

        result = run_ruff_format([lint_file], check=True)

        assert isinstance(result, dict)
        assert "success" in result
        assert "modified_files" in result
        assert "output" in result
        assert "duration" in result
        # File should already be formatted
        assert result["success"] is True

    def test_run_ruff_format_nonexistent_path(self) -> None:
        """Ruff format should raise error for non-existent path."""
        nonexistent = Path("/nonexistent/path/to/file.py")

        with pytest.raises(LintError, match="does not exist"):
            run_ruff_format([nonexistent])


class TestMypy:
    """Test mypy execution."""

    def test_run_mypy_on_self(self) -> None:
        """Run mypy on lint.py itself."""
        lint_file = Path(__file__).parent.parent.parent / "src/specify_cli/runtime/lint.py"
        assert lint_file.exists()

        result = run_mypy([lint_file])

        assert isinstance(result, dict)
        assert "success" in result
        assert "errors" in result
        assert "output" in result
        assert "duration" in result
        assert isinstance(result["success"], bool)
        assert isinstance(result["errors"], list)
        assert isinstance(result["duration"], float)

    def test_run_mypy_nonexistent_path(self) -> None:
        """Mypy should raise error for non-existent path."""
        nonexistent = Path("/nonexistent/path/to/file.py")

        with pytest.raises(LintError, match="does not exist"):
            run_mypy([nonexistent])

    def test_run_mypy_with_show_error_codes(self) -> None:
        """Mypy should support error codes in output."""
        lint_file = Path(__file__).parent.parent.parent / "src/specify_cli/runtime/lint.py"

        result = run_mypy([lint_file], show_error_codes=True)

        assert isinstance(result, dict)
        assert "success" in result
        assert "errors" in result


class TestErrorHandling:
    """Test error handling."""

    def test_lint_error_with_command(self) -> None:
        """LintError should store command."""
        cmd = ["ruff", "check", "file.py"]
        error = LintError("Test error", cmd)

        assert str(error) == "Test error"
        assert error.command == cmd

    def test_lint_error_without_command(self) -> None:
        """LintError should work without command."""
        error = LintError("Test error")

        assert str(error) == "Test error"
        assert error.command is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
