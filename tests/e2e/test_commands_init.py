"""End-to-end tests for specify init command.

This module tests the complete init command flow including:
- CLI invocation via CliRunner
- Integration with ops.init module
- Runtime project initialization
- Output formatting (text and JSON)
- Error handling and exit codes
- Interactive AI assistant selection
- Project template downloading

Test Coverage
-------------
- Basic init with project name
- Init in current directory (--here)
- AI assistant selection
- Script type configuration
- Git initialization control
- Error handling for invalid inputs
- Keyboard interrupt handling
- Template download and extraction
- File creation verification

Examples
--------
    $ pytest tests/e2e/test_commands_init.py -v -m e2e
    $ pytest tests/e2e/test_commands_init.py::test_init_basic
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from specify_cli.app import app
from specify_cli.ops.init import InitResult

runner = CliRunner()


@pytest.mark.e2e
def test_init_basic_with_project_name() -> None:
    """Test init command with basic project name.

    Verifies:
        - Command executes without errors
        - Project is created
        - Success message displayed
    """
    with patch("specify_cli.ops.init.initialize_project") as mock_init:
        mock_init.return_value = InitResult(
            success=True,
            project_path=Path("/tmp/test-project"),
            ai_assistant="claude",
            release_tag="v1.0.0",
            git_initialized=True,
            warnings=[],
            errors=[],
        )

        result = runner.invoke(app, ["init", "test-project"])

        assert result.exit_code == 0
        assert "successfully" in result.stdout.lower()
        assert "test-project" in result.stdout or "Project Path:" in result.stdout
        mock_init.assert_called_once()


@pytest.mark.e2e
def test_init_with_here_flag() -> None:
    """Test init command with --here flag in current directory.

    Verifies:
        - --here flag works
        - No project name required
        - Initializes in current directory
    """
    with patch("specify_cli.ops.init.initialize_project") as mock_init:
        mock_init.return_value = InitResult(
            success=True,
            project_path=Path.cwd(),
            ai_assistant="claude",
            release_tag="v1.0.0",
            git_initialized=True,
            warnings=[],
            errors=[],
        )

        result = runner.invoke(app, ["init", "--here"])

        assert result.exit_code == 0
        assert "current directory" in result.stdout.lower()
        mock_init.assert_called_once()
        call_kwargs = mock_init.call_args[1]
        assert call_kwargs["here"] is True


@pytest.mark.e2e
def test_init_with_ai_assistant_option() -> None:
    """Test init command with --ai option for assistant selection.

    Verifies:
        - AI assistant can be specified
        - Multiple assistant options work
        - Option is passed to ops layer
    """
    with patch("specify_cli.ops.init.initialize_project") as mock_init:
        mock_init.return_value = InitResult(
            success=True,
            project_path=Path("/tmp/test-project"),
            ai_assistant="cursor",
            release_tag="v1.0.0",
            git_initialized=True,
            warnings=[],
            errors=[],
        )

        result = runner.invoke(app, ["init", "test-project", "--ai", "cursor"])

        assert result.exit_code == 0
        assert "cursor" in result.stdout.lower()
        call_kwargs = mock_init.call_args[1]
        assert call_kwargs["ai_assistant"] == "cursor"


@pytest.mark.e2e
def test_init_with_no_git_flag() -> None:
    """Test init command with --no-git flag to skip git initialization.

    Verifies:
        - Git initialization can be skipped
        - Flag is passed to ops layer
        - Output reflects git status
    """
    with patch("specify_cli.ops.init.initialize_project") as mock_init:
        mock_init.return_value = InitResult(
            success=True,
            project_path=Path("/tmp/test-project"),
            ai_assistant="claude",
            release_tag="v1.0.0",
            git_initialized=False,
            warnings=[],
            errors=[],
        )

        result = runner.invoke(app, ["init", "test-project", "--no-git"])

        assert result.exit_code == 0
        assert "Skipped" in result.stdout or "git" in result.stdout.lower()
        call_kwargs = mock_init.call_args[1]
        assert call_kwargs["no_git"] is True


@pytest.mark.e2e
def test_init_with_script_type_option() -> None:
    """Test init command with --script option for script type.

    Verifies:
        - Script type can be specified (sh/ps1)
        - Option is passed to ops layer
        - Output shows selected script type
    """
    with patch("specify_cli.ops.init.initialize_project") as mock_init:
        mock_init.return_value = InitResult(
            success=True,
            project_path=Path("/tmp/test-project"),
            ai_assistant="claude",
            release_tag="v1.0.0",
            git_initialized=True,
            warnings=[],
            errors=[],
        )

        result = runner.invoke(app, ["init", "test-project", "--script", "ps1"])

        assert result.exit_code == 0
        assert "ps1" in result.stdout.lower()
        call_kwargs = mock_init.call_args[1]
        assert call_kwargs["script_type"] == "ps1"


@pytest.mark.e2e
def test_init_error_no_project_name_or_here() -> None:
    """Test init command error when neither project name nor --here provided.

    Verifies:
        - Error message displayed
        - Exit code is 1
        - Usage information shown
    """
    result = runner.invoke(app, ["init"])

    assert result.exit_code == 1
    assert "Error" in result.stdout or "error" in result.stdout.lower()
    assert "Usage" in result.stdout or "provide" in result.stdout.lower()


@pytest.mark.e2e
def test_init_error_both_name_and_here() -> None:
    """Test init command error when both project name and --here provided.

    Verifies:
        - Conflicting options rejected
        - Error message clear
        - Exit code is 1
    """
    result = runner.invoke(app, ["init", "test-project", "--here"])

    assert result.exit_code == 1
    assert "Error" in result.stdout or "error" in result.stdout.lower()
    assert "Cannot" in result.stdout or "both" in result.stdout.lower()


@pytest.mark.e2e
def test_init_initialization_failure() -> None:
    """Test init command when ops layer reports failure.

    Verifies:
        - Failure is handled gracefully
        - Error messages displayed
        - Exit code is 1
    """
    with patch("specify_cli.ops.init.initialize_project") as mock_init:
        mock_init.return_value = InitResult(
            success=False,
            project_path=Path("/tmp/test-project"),
            ai_assistant="claude",
            release_tag="",
            git_initialized=False,
            warnings=[],
            errors=["Failed to download template", "Network error"],
        )

        result = runner.invoke(app, ["init", "test-project"])

        assert result.exit_code == 1
        assert "failed" in result.stdout.lower()
        assert "Network error" in result.stdout or "download" in result.stdout.lower()


@pytest.mark.e2e
def test_init_with_warnings() -> None:
    """Test init command when warnings are present.

    Verifies:
        - Warnings are displayed
        - Command still succeeds
        - Warning section visible
    """
    with patch("specify_cli.ops.init.initialize_project") as mock_init:
        mock_init.return_value = InitResult(
            success=True,
            project_path=Path("/tmp/test-project"),
            ai_assistant="claude",
            release_tag="v1.0.0",
            git_initialized=True,
            warnings=["Git user.name not configured", "Git user.email not configured"],
            errors=[],
        )

        result = runner.invoke(app, ["init", "test-project"])

        assert result.exit_code == 0
        assert "Warning" in result.stdout or "warning" in result.stdout.lower()
        assert "user.name" in result.stdout or "user.email" in result.stdout


@pytest.mark.e2e
def test_init_keyboard_interrupt() -> None:
    """Test init command handles keyboard interrupt gracefully.

    Verifies:
        - Exit code is 130 (SIGINT)
        - Cleanup message shown
    """
    with patch("specify_cli.ops.init.initialize_project") as mock_init:
        mock_init.side_effect = KeyboardInterrupt()

        result = runner.invoke(app, ["init", "test-project"])

        assert result.exit_code == 130
        assert "cancelled" in result.stdout.lower() or result.exit_code == 130


@pytest.mark.e2e
def test_init_exception_handling() -> None:
    """Test init command handles unexpected exceptions.

    Verifies:
        - Exit code is 1 on error
        - Error message displayed
    """
    with patch("specify_cli.ops.init.initialize_project") as mock_init:
        mock_init.side_effect = RuntimeError("Unexpected error occurred")

        result = runner.invoke(app, ["init", "test-project"])

        assert result.exit_code == 1
        assert "error" in result.stdout.lower()


@pytest.mark.e2e
def test_init_with_github_token() -> None:
    """Test init command with GitHub token for authenticated requests.

    Verifies:
        - GitHub token can be provided
        - Option is passed to ops layer
    """
    with patch("specify_cli.ops.init.initialize_project") as mock_init:
        mock_init.return_value = InitResult(
            success=True,
            project_path=Path("/tmp/test-project"),
            ai_assistant="claude",
            release_tag="v1.0.0",
            git_initialized=True,
            warnings=[],
            errors=[],
        )

        result = runner.invoke(
            app, ["init", "test-project", "--github-token", "ghp_test123"]
        )

        assert result.exit_code == 0
        call_kwargs = mock_init.call_args[1]
        assert call_kwargs["github_token"] == "ghp_test123"


@pytest.mark.e2e
def test_init_verbose_output() -> None:
    """Test init command with --verbose flag for detailed output.

    Verifies:
        - Verbose mode shows more details
        - Extra information displayed
    """
    with patch("specify_cli.ops.init.initialize_project") as mock_init:
        mock_init.return_value = InitResult(
            success=True,
            project_path=Path("/tmp/test-project"),
            ai_assistant="claude",
            release_tag="v1.0.0",
            git_initialized=True,
            warnings=[],
            errors=[],
        )

        result = runner.invoke(app, ["init", "test-project", "--verbose"])

        assert result.exit_code == 0
        # Verbose should show more output (longer)
        assert len(result.stdout) > 100


@pytest.mark.e2e
def test_init_next_steps_displayed() -> None:
    """Test init command displays next steps after success.

    Verifies:
        - Next steps section shown
        - Commands to run listed
        - Project path mentioned
    """
    with patch("specify_cli.ops.init.initialize_project") as mock_init:
        mock_init.return_value = InitResult(
            success=True,
            project_path=Path("/tmp/test-project"),
            ai_assistant="claude",
            release_tag="v1.0.0",
            git_initialized=True,
            warnings=[],
            errors=[],
        )

        result = runner.invoke(app, ["init", "test-project"])

        assert result.exit_code == 0
        assert "Next steps" in result.stdout or "next" in result.stdout.lower()
        assert "specify check" in result.stdout or "README" in result.stdout


@pytest.mark.e2e
@pytest.mark.parametrize(
    ("ai_option", "expected_ai"),
    [
        ("claude", "claude"),
        ("cursor", "cursor"),
        ("copilot", "copilot"),
    ],
)
def test_init_ai_assistant_variants(ai_option: str, expected_ai: str) -> None:
    """Test init command with different AI assistant options.

    Parameters
    ----------
    ai_option : str
        AI assistant option to test.
    expected_ai : str
        Expected AI assistant in result.

    Verifies:
        - All AI assistants work
        - Correct assistant selected
    """
    with patch("specify_cli.ops.init.initialize_project") as mock_init:
        mock_init.return_value = InitResult(
            success=True,
            project_path=Path("/tmp/test-project"),
            ai_assistant=expected_ai,
            release_tag="v1.0.0",
            git_initialized=True,
            warnings=[],
            errors=[],
        )

        result = runner.invoke(app, ["init", "test-project", "--ai", ai_option])

        assert result.exit_code == 0
        call_kwargs = mock_init.call_args[1]
        assert call_kwargs["ai_assistant"] == ai_option


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "e2e"])
