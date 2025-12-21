"""
Unit tests for specify_cli.core.process module.

Tests cover the process execution utilities with mocked subprocess calls.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

from specify_cli.core.process import run, run_command, run_logged, which


class TestRun:
    """Tests for the run() function."""

    def test_run_simple_command(self, mock_subprocess_run: MagicMock) -> None:
        """Test basic command execution."""
        mock_subprocess_run.return_value.returncode = 0
        mock_subprocess_run.return_value.stdout = None

        result = run(["echo", "hello"])

        assert result is None
        mock_subprocess_run.assert_called_once()
        # Verify list-based execution (no shell=True)
        call_args = mock_subprocess_run.call_args
        assert call_args[0][0] == ["echo", "hello"]

    def test_run_with_capture(self, mock_subprocess_run: MagicMock) -> None:
        """Test command execution with output capture."""
        mock_subprocess_run.return_value.returncode = 0
        mock_subprocess_run.return_value.stdout = "hello world"

        result = run(["echo", "hello", "world"], capture=True)

        assert result == "hello world"
        call_kwargs = mock_subprocess_run.call_args.kwargs
        assert call_kwargs.get("stdout") == subprocess.PIPE

    def test_run_with_cwd(self, mock_subprocess_run: MagicMock, tmp_path: Path) -> None:
        """Test command execution with working directory."""
        mock_subprocess_run.return_value.returncode = 0
        mock_subprocess_run.return_value.stdout = None

        run(["ls"], cwd=tmp_path)

        call_kwargs = mock_subprocess_run.call_args.kwargs
        assert call_kwargs.get("cwd") == str(tmp_path)

    def test_run_with_env(self, mock_subprocess_run: MagicMock) -> None:
        """Test command execution with custom environment."""
        mock_subprocess_run.return_value.returncode = 0
        mock_subprocess_run.return_value.stdout = None

        run(["printenv"], env={"CUSTOM_VAR": "custom_value"})

        call_kwargs = mock_subprocess_run.call_args.kwargs
        assert "env" in call_kwargs
        assert call_kwargs["env"]["CUSTOM_VAR"] == "custom_value"

    def test_run_string_command(self, mock_subprocess_run: MagicMock) -> None:
        """Test command execution with string command (shlex split)."""
        mock_subprocess_run.return_value.returncode = 0
        mock_subprocess_run.return_value.stdout = None

        run("echo hello world")

        call_args = mock_subprocess_run.call_args
        assert call_args[0][0] == ["echo", "hello", "world"]

    def test_run_dry_mode(self) -> None:
        """Test dry run mode skips execution."""
        with patch.dict(os.environ, {"SPECIFY_DRY": "1"}):
            with patch("subprocess.run") as mock_run:
                result = run(["dangerous", "command"])

                mock_run.assert_not_called()
                assert result == ""

    def test_run_quiet_mode(self, mock_subprocess_run: MagicMock) -> None:
        """Test quiet mode captures output."""
        mock_subprocess_run.return_value.returncode = 0
        mock_subprocess_run.return_value.stdout = "output"

        with patch.dict(os.environ, {"SPECIFY_QUIET": "1"}):
            run(["echo", "hello"])

        call_kwargs = mock_subprocess_run.call_args.kwargs
        assert call_kwargs.get("stdout") == subprocess.PIPE

    def test_run_check_raises_on_failure(self, mock_subprocess_run: MagicMock) -> None:
        """Test command with check=True raises on non-zero exit."""
        mock_subprocess_run.side_effect = subprocess.CalledProcessError(1, ["false"])

        with pytest.raises(subprocess.CalledProcessError) as exc_info:
            run(["false"], check=True)

        assert exc_info.value.returncode == 1

    def test_run_no_check_ignores_failure(self, mock_subprocess_run: MagicMock) -> None:
        """Test command with check=False ignores non-zero exit."""
        mock_subprocess_run.return_value.returncode = 1
        mock_subprocess_run.return_value.stdout = None

        # Should not raise
        result = run(["false"], check=False)
        assert result is None


class TestRunLogged:
    """Tests for the run_logged() function."""

    def test_run_logged_with_label(self, mock_subprocess_run: MagicMock) -> None:
        """Test logged execution displays label."""
        mock_subprocess_run.return_value.returncode = 0
        mock_subprocess_run.return_value.stdout = None

        with patch("specify_cli.core.process.colour") as mock_colour:
            run_logged(["echo", "hello"], label="Running echo")

            mock_colour.assert_called_with("-> Running echo", "cyan")

    def test_run_logged_without_label(self, mock_subprocess_run: MagicMock) -> None:
        """Test logged execution displays command when no label."""
        mock_subprocess_run.return_value.returncode = 0
        mock_subprocess_run.return_value.stdout = None

        with patch("specify_cli.core.process.colour") as mock_colour:
            run_logged(["echo", "hello"])

            mock_colour.assert_called_with("$ echo hello", "cyan")

    def test_run_logged_captures_output(self, mock_subprocess_run: MagicMock) -> None:
        """Test logged execution can capture output."""
        mock_subprocess_run.return_value.returncode = 0
        mock_subprocess_run.return_value.stdout = "captured output"

        result = run_logged(["echo", "hello"], capture=True)

        assert result == "captured output"

    def test_run_logged_propagates_exception(self, mock_subprocess_run: MagicMock) -> None:
        """Test logged execution propagates exceptions."""
        mock_subprocess_run.side_effect = subprocess.CalledProcessError(1, ["false"])

        with pytest.raises(subprocess.CalledProcessError):
            run_logged(["false"])


class TestWhich:
    """Tests for the which() function."""

    def test_which_finds_executable(self) -> None:
        """Test which() finds an existing executable."""
        with patch("shutil.which", return_value="/usr/bin/python") as mock_shutil:
            result = which("python")

            assert result == "/usr/bin/python"
            mock_shutil.assert_called_once_with("python")

    def test_which_not_found(self) -> None:
        """Test which() returns None for missing executable."""
        with patch("shutil.which", return_value=None) as mock_shutil:
            result = which("nonexistent-binary")

            assert result is None
            mock_shutil.assert_called_once_with("nonexistent-binary")


class TestRunCommandBackwardCompat:
    """Tests for the run_command() backward compatibility function."""

    def test_run_command_basic(self, mock_subprocess_run: MagicMock) -> None:
        """Test run_command basic execution."""
        mock_subprocess_run.return_value.returncode = 0
        mock_subprocess_run.return_value.stdout = None

        result = run_command(["echo", "hello"])

        assert result is None
        mock_subprocess_run.assert_called_once()

    def test_run_command_with_capture(self, mock_subprocess_run: MagicMock) -> None:
        """Test run_command with capture=True."""
        mock_subprocess_run.return_value.returncode = 0
        mock_subprocess_run.return_value.stdout = "output"

        result = run_command(["echo", "hello"], capture=True)

        assert result == "output"

    def test_run_command_shell_warning(
        self, mock_subprocess_run: MagicMock, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test run_command logs warning when shell=True is passed."""
        mock_subprocess_run.return_value.returncode = 0
        mock_subprocess_run.return_value.stdout = None

        import logging

        with caplog.at_level(logging.WARNING):
            run_command(["echo", "hello"], shell=True)

        assert "shell=True is deprecated" in caplog.text

    def test_run_command_check_return(self, mock_subprocess_run: MagicMock) -> None:
        """Test run_command check_return parameter."""
        mock_subprocess_run.side_effect = subprocess.CalledProcessError(1, ["false"])

        with pytest.raises(subprocess.CalledProcessError):
            run_command(["false"], check_return=True)

    def test_run_command_no_check(self, mock_subprocess_run: MagicMock) -> None:
        """Test run_command with check_return=False."""
        mock_subprocess_run.return_value.returncode = 1
        mock_subprocess_run.return_value.stdout = None

        # Should not raise
        run_command(["false"], check_return=False)


class TestSecurityFeatures:
    """Tests for security features in process module."""

    def test_no_shell_execution(self, mock_subprocess_run: MagicMock) -> None:
        """Verify subprocess is called without shell=True."""
        mock_subprocess_run.return_value.returncode = 0
        mock_subprocess_run.return_value.stdout = None

        run(["echo", "hello"])

        call_kwargs = mock_subprocess_run.call_args.kwargs
        assert "shell" not in call_kwargs or call_kwargs.get("shell") is False

    def test_command_list_only(self, mock_subprocess_run: MagicMock) -> None:
        """Verify commands are passed as lists, not strings with shell."""
        mock_subprocess_run.return_value.returncode = 0
        mock_subprocess_run.return_value.stdout = None

        # Even with string input, should be converted to list
        run("echo hello")

        call_args = mock_subprocess_run.call_args[0][0]
        assert isinstance(call_args, list)
        assert call_args == ["echo", "hello"]


class TestOtelIntegration:
    """Tests for OpenTelemetry integration."""

    def test_run_works_with_otel(self, mock_subprocess_run: MagicMock) -> None:
        """Test run() works with OTEL (no-op mode by default)."""
        mock_subprocess_run.return_value.returncode = 0
        mock_subprocess_run.return_value.stdout = None

        # Should execute without error, OTEL uses no-op tracer when not configured
        result = run(["echo", "hello"])

        assert result is None
        mock_subprocess_run.assert_called_once()

    def test_which_works_with_otel(self) -> None:
        """Test which() works with OTEL (no-op mode by default)."""
        with patch("shutil.which", return_value="/usr/bin/python"):
            # Should execute without error, OTEL uses no-op tracer when not configured
            result = which("python")

        assert result == "/usr/bin/python"
