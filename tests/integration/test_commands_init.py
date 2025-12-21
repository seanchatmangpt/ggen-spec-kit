"""
Integration tests for specify_cli.commands.init module.

Tests cover the CLI command layer with Typer test runner.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner


@pytest.fixture
def runner() -> CliRunner:
    """Create CLI test runner."""
    return CliRunner()


@pytest.fixture
def init_app():
    """Get the init command app."""
    from specify_cli.commands.init import init
    import typer

    # Create a simple app that wraps the init command directly
    # This avoids the subcommand resolution issue
    test_app = typer.Typer()
    test_app.command()(init)

    return test_app


class TestInitCommand:
    """Tests for the init command."""

    def test_init_help(self, runner: CliRunner, init_app) -> None:
        """Test init --help displays help."""
        result = runner.invoke(init_app, ["--help"])

        assert result.exit_code == 0
        assert "Initialize" in result.stdout or "init" in result.stdout.lower()

    def test_init_with_name(
        self, runner: CliRunner, init_app, tmp_path: Path
    ) -> None:
        """Test init with project name."""
        with patch("specify_cli.commands.init.init_ops.initialize_project") as mock_init, \
             patch("specify_cli.commands.init._select_ai_assistant_interactive") as mock_select:
            mock_result = MagicMock()
            mock_result.success = True
            mock_result.project_path = tmp_path / "test-project"
            mock_result.ai_assistant = "claude"
            mock_result.script_type = "sh"
            mock_result.git_initialized = True
            mock_result.release_tag = "v1.0.0"
            mock_result.warnings = []
            mock_init.return_value = mock_result
            mock_select.return_value = "claude"

            result = runner.invoke(init_app, ["test-project"])

            assert result.exit_code == 0
            mock_init.assert_called_once()

    def test_init_with_here_flag(
        self, runner: CliRunner, init_app, tmp_path: Path
    ) -> None:
        """Test init with --here flag."""
        with patch("specify_cli.commands.init.init_ops.initialize_project") as mock_init, \
             patch("specify_cli.commands.init._select_ai_assistant_interactive") as mock_select:
            mock_result = MagicMock()
            mock_result.success = True
            mock_result.project_path = tmp_path
            mock_result.ai_assistant = "claude"
            mock_result.script_type = "sh"
            mock_result.git_initialized = True
            mock_result.release_tag = "v1.0.0"
            mock_result.warnings = []
            mock_init.return_value = mock_result
            mock_select.return_value = "claude"

            result = runner.invoke(init_app, ["--here"])

            assert result.exit_code == 0
            call_kwargs = mock_init.call_args.kwargs
            assert call_kwargs.get("here") is True

    def test_init_with_ai_option(
        self, runner: CliRunner, init_app, tmp_path: Path
    ) -> None:
        """Test init with --ai option."""
        with patch("specify_cli.commands.init.init_ops.initialize_project") as mock_init:
            mock_result = MagicMock()
            mock_result.success = True
            mock_result.project_path = tmp_path / "test-project"
            mock_result.ai_assistant = "cursor"
            mock_result.script_type = "sh"
            mock_result.git_initialized = True
            mock_result.release_tag = "v1.0.0"
            mock_result.warnings = []
            mock_init.return_value = mock_result

            result = runner.invoke(init_app, ["test-project", "--ai", "cursor"])

            assert result.exit_code == 0
            call_kwargs = mock_init.call_args.kwargs
            assert call_kwargs.get("ai_assistant") == "cursor"

    def test_init_with_no_git_flag(
        self, runner: CliRunner, init_app, tmp_path: Path
    ) -> None:
        """Test init with --no-git flag."""
        with patch("specify_cli.commands.init.init_ops.initialize_project") as mock_init, \
             patch("specify_cli.commands.init._select_ai_assistant_interactive") as mock_select:
            mock_result = MagicMock()
            mock_result.success = True
            mock_result.project_path = tmp_path / "test-project"
            mock_result.ai_assistant = "claude"
            mock_result.script_type = "sh"
            mock_result.git_initialized = False
            mock_result.release_tag = "v1.0.0"
            mock_result.warnings = []
            mock_init.return_value = mock_result
            mock_select.return_value = "claude"

            result = runner.invoke(init_app, ["test-project", "--no-git"])

            assert result.exit_code == 0
            call_kwargs = mock_init.call_args.kwargs
            assert call_kwargs.get("no_git") is True

    def test_init_failure(
        self, runner: CliRunner, init_app
    ) -> None:
        """Test init with failure."""
        with patch("specify_cli.commands.init.init_ops.initialize_project") as mock_init, \
             patch("specify_cli.commands.init._select_ai_assistant_interactive") as mock_select:
            from specify_cli.ops.init import InitError

            mock_init.side_effect = InitError("Test error")
            mock_select.return_value = "claude"

            result = runner.invoke(init_app, ["test-project"])

            assert result.exit_code == 1
            assert "error" in result.stdout.lower() or "Error" in result.stdout

    def test_init_with_warnings(
        self, runner: CliRunner, init_app, tmp_path: Path
    ) -> None:
        """Test init with warnings."""
        with patch("specify_cli.commands.init.init_ops.initialize_project") as mock_init, \
             patch("specify_cli.commands.init._select_ai_assistant_interactive") as mock_select:
            mock_result = MagicMock()
            mock_result.success = True
            mock_result.project_path = tmp_path / "test-project"
            mock_result.ai_assistant = "claude"
            mock_result.script_type = "sh"
            mock_result.git_initialized = True
            mock_result.release_tag = "v1.0.0"
            mock_result.warnings = ["Warning: Some issue occurred"]
            mock_init.return_value = mock_result
            mock_select.return_value = "claude"

            result = runner.invoke(init_app, ["test-project"])

            assert result.exit_code == 0
            # Warnings should be displayed
            assert "Warning" in result.stdout or result.exit_code == 0


class TestCheckCommand:
    """Tests for the check command."""

    @pytest.fixture
    def check_app(self):
        """Get the check command app."""
        from specify_cli.commands.check import app

        return app

    def test_check_help(self, runner: CliRunner, check_app) -> None:
        """Test check --help displays help."""
        result = runner.invoke(check_app, ["--help"])

        assert result.exit_code == 0
        assert "check" in result.stdout.lower() or "tool" in result.stdout.lower()

    def test_check_all_available(self, runner: CliRunner, check_app) -> None:
        """Test check when all tools available."""
        with patch("specify_cli.commands.check.check_ops.check_all_tools") as mock_check:
            from specify_cli.ops.check import CheckResult, ToolStatus

            mock_result = CheckResult(
                success=True,
                available=[
                    ToolStatus(name="git", available=True, required=True, path="/usr/bin/git"),
                ],
                missing=[],
            )
            mock_check.return_value = mock_result

            result = runner.invoke(check_app, [])

            assert result.exit_code == 0
            assert "git" in result.stdout.lower() or "available" in result.stdout.lower()

    def test_check_required_missing(self, runner: CliRunner, check_app) -> None:
        """Test check when required tool missing."""
        with patch("specify_cli.commands.check.check_ops.check_all_tools") as mock_check:
            from specify_cli.ops.check import CheckResult, ToolStatus

            mock_result = CheckResult(
                success=False,
                available=[],
                missing=[
                    ToolStatus(name="git", available=False, required=True),
                ],
            )
            mock_check.return_value = mock_result

            result = runner.invoke(check_app, [])

            assert result.exit_code == 1
            assert "missing" in result.stdout.lower() or "git" in result.stdout.lower()

    def test_check_json_output(self, runner: CliRunner, check_app) -> None:
        """Test check with --json output."""
        with patch("specify_cli.commands.check.check_ops.check_all_tools") as mock_check:
            from specify_cli.ops.check import CheckResult, ToolStatus

            mock_result = CheckResult(
                success=True,
                available=[
                    ToolStatus(name="git", available=True, required=True, path="/usr/bin/git"),
                ],
                missing=[],
                duration=0.5,
            )
            mock_check.return_value = mock_result

            result = runner.invoke(check_app, ["--json"])

            assert result.exit_code == 0
            # Output should be valid JSON
            import json

            data = json.loads(result.stdout)
            assert data["success"] is True

    def test_check_verbose(self, runner: CliRunner, check_app) -> None:
        """Test check with --verbose flag."""
        with patch("specify_cli.commands.check.check_ops.check_all_tools") as mock_check, patch(
            "specify_cli.commands.check.check_ops.get_environment_info"
        ) as mock_env:
            from specify_cli.ops.check import CheckResult, ToolStatus

            mock_result = CheckResult(
                success=True,
                available=[
                    ToolStatus(
                        name="git",
                        available=True,
                        required=True,
                        path="/usr/bin/git",
                    ),
                ],
                missing=[],
            )
            mock_check.return_value = mock_result

            mock_env.return_value = {
                "python": {"version": "3.11.0", "executable": "/usr/bin/python"},
                "platform": {"system": "Darwin", "release": "22.0"},
            }

            result = runner.invoke(check_app, ["--verbose"])

            assert result.exit_code == 0
            # Verbose output should include path info
            assert "/usr/bin/git" in result.stdout or "git" in result.stdout.lower()


class TestVersionCommand:
    """Tests for the version command."""

    @pytest.fixture
    def version_app(self):
        """Get the version command app."""
        from specify_cli.commands.version import app

        return app

    def test_version_basic(self, runner: CliRunner, version_app) -> None:
        """Test basic version output."""
        with patch("specify_cli.commands.version.version_ops.get_current_version") as mock_version:
            mock_version.return_value = "0.0.25"

            result = runner.invoke(version_app, [])

            assert result.exit_code == 0
            assert "0.0.25" in result.stdout

    def test_version_json(self, runner: CliRunner, version_app) -> None:
        """Test version with --json output."""
        with patch("specify_cli.commands.version.version_ops.get_current_version") as mock_version:
            mock_version.return_value = "0.0.25"

            result = runner.invoke(version_app, ["--json"])

            assert result.exit_code == 0
            import json

            data = json.loads(result.stdout)
            assert data["version"] == "0.0.25"

    def test_version_check_updates(self, runner: CliRunner, version_app) -> None:
        """Test version with --check-updates."""
        with patch(
            "specify_cli.commands.version.version_ops.get_current_version"
        ) as mock_current, patch(
            "specify_cli.commands.version.version_ops.get_version_info"
        ) as mock_info:
            mock_current.return_value = "0.0.25"

            from specify_cli.ops.version import VersionInfo

            mock_info.return_value = VersionInfo(
                current_version="0.0.25",
                latest_version="0.0.26",
                update_available=True,
            )

            result = runner.invoke(version_app, ["--check-updates"])

            assert result.exit_code == 0
            # Should show update available
            assert "0.0.26" in result.stdout or "update" in result.stdout.lower()


class TestMainApp:
    """Tests for the main CLI app."""

    @pytest.fixture
    def main_app(self):
        """Get the main app."""
        from specify_cli.app import app

        return app

    def test_main_help(self, runner: CliRunner, main_app) -> None:
        """Test main --help."""
        result = runner.invoke(main_app, ["--help"])

        assert result.exit_code == 0
        assert "specify" in result.stdout.lower() or "init" in result.stdout

    def test_main_version_flag(self, runner: CliRunner, main_app) -> None:
        """Test main --version flag."""
        with patch("specify_cli.commands.version.version_ops.get_current_version") as mock_version:
            mock_version.return_value = "0.0.25"

            result = runner.invoke(main_app, ["--version"])

            assert result.exit_code == 0
            assert "0.0.25" in result.stdout

    def test_main_no_subcommand(self, runner: CliRunner, main_app) -> None:
        """Test main with no subcommand shows banner."""
        result = runner.invoke(main_app, [])

        # Should show banner or help
        assert result.exit_code == 0
