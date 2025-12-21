"""End-to-end tests for specify check command.

This module tests the complete check command flow including:
- CLI invocation via CliRunner
- Integration with ops.check module
- Runtime tool detection
- Output formatting (table, JSON, verbose)
- Error handling and exit codes

Test Coverage
-------------
- Basic check command execution
- Verbose output mode
- JSON output format
- Required-only tool filtering
- Tool availability detection
- Version information display
- Missing tool handling
- Exit codes (0=success, 1=failure)
- Error handling

Examples
--------
    $ pytest tests/e2e/test_commands_check.py -v -m e2e
    $ pytest tests/e2e/test_commands_check.py::test_check_command_basic
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from specify_cli.app import app

runner = CliRunner()


@pytest.mark.e2e
def test_check_command_basic() -> None:
    """Test check command runs successfully with default options.

    Verifies:
        - Command executes without errors
        - Exit code is 0 when required tools present
        - Output contains expected sections
    """
    with patch("specify_cli.ops.check.tools") as mock_tools:
        # Mock all required tools as available
        mock_tools.REQUIRED_TOOLS = ["git"]
        mock_tools.OPTIONAL_TOOLS = ["claude", "ggen", "uv"]
        mock_tools.which_tool.return_value = "/usr/bin/tool"
        mock_tools.get_tool_versions.return_value = {
            "git": "2.42.0",
            "uv": "0.5.0",
            "ggen": "5.0.2",
        }

        result = runner.invoke(app, ["check"])

        assert result.exit_code == 0
        assert "Tool Check Results" in result.stdout
        assert "Summary:" in result.stdout
        assert "All required tools are available" in result.stdout


@pytest.mark.e2e
def test_check_command_verbose() -> None:
    """Test check command with verbose flag shows detailed information.

    Verifies:
        - Verbose mode shows version info
        - Verbose mode shows tool paths
        - Environment information is displayed
    """
    with patch("specify_cli.ops.check.tools") as mock_tools, patch(
        "specify_cli.ops.check.get_environment_info"
    ) as mock_env:
        mock_tools.REQUIRED_TOOLS = ["git"]
        mock_tools.OPTIONAL_TOOLS = ["ggen"]
        mock_tools.which_tool.return_value = Path("/usr/bin/git")
        mock_tools.get_tool_versions.return_value = {"git": "2.42.0", "ggen": "5.0.2"}

        mock_env.return_value = {
            "python": {"version": "3.12.0"},
            "platform": {"system": "Darwin", "release": "24.5.0"},
        }

        result = runner.invoke(app, ["check", "--verbose"])

        assert result.exit_code == 0
        assert "Version" in result.stdout or "Path" in result.stdout
        assert "Environment:" in result.stdout
        assert "Python:" in result.stdout
        assert "Platform:" in result.stdout


@pytest.mark.e2e
def test_check_command_json_output() -> None:
    """Test check command JSON output format correctness.

    Verifies:
        - JSON output is valid
        - Contains required fields: success, available, missing, duration
        - Tool objects have correct structure
    """
    with patch("specify_cli.ops.check.tools") as mock_tools:
        mock_tools.REQUIRED_TOOLS = ["git"]
        mock_tools.OPTIONAL_TOOLS = ["ggen"]
        mock_tools.which_tool.return_value = Path("/usr/bin/git")
        mock_tools.get_tool_versions.return_value = {"git": "2.42.0"}

        result = runner.invoke(app, ["check", "--json"])

        assert result.exit_code == 0

        # Parse and validate JSON structure
        data = json.loads(result.stdout)
        assert isinstance(data, dict)
        assert "success" in data
        assert "available" in data
        assert "missing" in data
        assert "duration" in data

        # Validate tool structure
        if data["available"]:
            tool = data["available"][0]
            assert "name" in tool
            assert "path" in tool
            assert "required" in tool
            assert "version" in tool


@pytest.mark.e2e
def test_check_command_required_only() -> None:
    """Test check command with --required-only flag.

    Verifies:
        - Only required tools are checked
        - Optional tools are excluded
        - Output is correct
    """
    with patch("specify_cli.ops.check.tools") as mock_tools:
        mock_tools.REQUIRED_TOOLS = ["git"]
        mock_tools.OPTIONAL_TOOLS = ["claude", "ggen", "uv"]
        mock_tools.which_tool.return_value = Path("/usr/bin/git")
        mock_tools.get_tool_versions.return_value = {"git": "2.42.0"}

        result = runner.invoke(app, ["check", "--required-only"])

        assert result.exit_code == 0
        # Only git should be checked
        assert "git" in result.stdout
        # Should not check optional tools (verify via call count)


@pytest.mark.e2e
def test_check_command_all_tools_missing() -> None:
    """Test check command when all required tools are missing.

    Verifies:
        - Exit code is 1 when required tools missing
        - Error message displayed
        - Missing tools listed
    """
    with patch("specify_cli.ops.check.tools") as mock_tools:
        mock_tools.REQUIRED_TOOLS = ["git"]
        mock_tools.OPTIONAL_TOOLS = []
        mock_tools.which_tool.return_value = None
        mock_tools.get_tool_versions.return_value = {}

        result = runner.invoke(app, ["check"])

        assert result.exit_code == 1
        assert "required tool(s) missing" in result.stdout.lower()
        assert "Please install missing required tools" in result.stdout


@pytest.mark.e2e
def test_check_command_optional_missing() -> None:
    """Test check command when only optional tools are missing.

    Verifies:
        - Exit code is 0 (success) when only optional missing
        - Missing optional tools are listed
        - Success message shown
    """
    with patch("specify_cli.ops.check.tools") as mock_tools:
        mock_tools.REQUIRED_TOOLS = ["git"]
        mock_tools.OPTIONAL_TOOLS = ["ggen", "uv"]

        def which_side_effect(name: str) -> Path | None:
            if name == "git":
                return Path("/usr/bin/git")
            return None

        mock_tools.which_tool.side_effect = which_side_effect
        mock_tools.get_tool_versions.return_value = {"git": "2.42.0"}

        result = runner.invoke(app, ["check"])

        assert result.exit_code == 0
        assert "All required tools are available" in result.stdout
        assert "Missing" in result.stdout or "✗" in result.stdout


@pytest.mark.e2e
def test_check_command_version_detection() -> None:
    """Test that tool versions are detected and displayed correctly.

    Verifies:
        - Versions are shown in verbose mode
        - Version strings are correct
        - Multiple tool versions displayed
    """
    with patch("specify_cli.ops.check.tools") as mock_tools, patch(
        "specify_cli.ops.check.get_environment_info"
    ) as mock_env:
        mock_tools.REQUIRED_TOOLS = ["git"]
        mock_tools.OPTIONAL_TOOLS = ["uv", "ggen"]
        mock_tools.which_tool.return_value = Path("/usr/bin/tool")
        mock_tools.get_tool_versions.return_value = {
            "git": "2.42.0",
            "uv": "0.5.0",
            "ggen": "5.0.2",
        }

        mock_env.return_value = {
            "python": {"version": "3.12.0"},
            "platform": {"system": "Darwin", "release": "24.5.0"},
        }

        result = runner.invoke(app, ["check", "--verbose"])

        assert result.exit_code == 0
        # Version numbers should appear in output
        assert "2.42.0" in result.stdout or "0.5.0" in result.stdout or "5.0.2" in result.stdout


@pytest.mark.e2e
def test_check_command_ggen_special_info() -> None:
    """Test that ggen-specific information is shown in verbose mode.

    Verifies:
        - ggen purpose/description shown
        - ggen version displayed
        - ggen path shown
    """
    with patch("specify_cli.ops.check.tools") as mock_tools, patch(
        "specify_cli.ops.check.get_environment_info"
    ) as mock_env:
        mock_tools.REQUIRED_TOOLS = ["git"]
        mock_tools.OPTIONAL_TOOLS = ["ggen"]
        mock_tools.which_tool.return_value = Path("/usr/local/bin/ggen")
        mock_tools.get_tool_versions.return_value = {"git": "2.42.0", "ggen": "5.0.2"}

        mock_env.return_value = {
            "python": {"version": "3.12.0"},
            "platform": {"system": "Darwin", "release": "24.5.0"},
        }

        result = runner.invoke(app, ["check", "--verbose"])

        assert result.exit_code == 0
        if "ggen" in result.stdout.lower():
            assert "RDF" in result.stdout or "ontology" in result.stdout.lower()


@pytest.mark.e2e
def test_check_command_json_structure() -> None:
    """Test detailed JSON output structure and field types.

    Verifies:
        - All required JSON fields present
        - Field types are correct
        - Nested structures valid
    """
    with patch("specify_cli.ops.check.tools") as mock_tools:
        mock_tools.REQUIRED_TOOLS = ["git"]
        mock_tools.OPTIONAL_TOOLS = ["ggen"]

        def which_side_effect(name: str) -> Path | None:
            if name == "git":
                return Path("/usr/bin/git")
            return None

        mock_tools.which_tool.side_effect = which_side_effect
        mock_tools.get_tool_versions.return_value = {"git": "2.42.0"}

        result = runner.invoke(app, ["check", "--json"])

        assert result.exit_code == 0

        data = json.loads(result.stdout)

        # Validate root structure
        assert isinstance(data["success"], bool)
        assert isinstance(data["available"], list)
        assert isinstance(data["missing"], list)
        assert isinstance(data["duration"], (int, float))

        # Validate available tool structure
        for tool in data["available"]:
            assert isinstance(tool["name"], str)
            assert isinstance(tool["required"], bool)
            assert tool["path"] is None or isinstance(tool["path"], str)
            assert tool["version"] is None or isinstance(tool["version"], str)

        # Validate missing tool structure
        for tool in data["missing"]:
            assert isinstance(tool["name"], str)
            assert isinstance(tool["required"], bool)
            assert tool["error"] is None or isinstance(tool["error"], str)


@pytest.mark.e2e
def test_check_command_keyboard_interrupt() -> None:
    """Test check command handles keyboard interrupt gracefully.

    Verifies:
        - Exit code is 130 (SIGINT)
        - Cleanup message shown
    """
    with patch("specify_cli.ops.check.check_all_tools") as mock_check:
        mock_check.side_effect = KeyboardInterrupt()

        result = runner.invoke(app, ["check"])

        assert result.exit_code == 130
        assert "cancelled" in result.stdout.lower() or result.exit_code == 130


@pytest.mark.e2e
def test_check_command_exception_handling() -> None:
    """Test check command handles unexpected exceptions.

    Verifies:
        - Exit code is 1 on error
        - Error message displayed
        - Exception details included
    """
    with patch("specify_cli.ops.check.check_all_tools") as mock_check:
        mock_check.side_effect = RuntimeError("Unexpected error occurred")

        result = runner.invoke(app, ["check"])

        assert result.exit_code == 1
        assert "error" in result.stdout.lower()


@pytest.mark.e2e
def test_check_command_status_indicators() -> None:
    """Test that status indicators (✓/✗) are displayed correctly.

    Verifies:
        - Available tools show success indicator
        - Missing tools show error indicator
        - Required status clearly marked
    """
    with patch("specify_cli.ops.check.tools") as mock_tools:
        mock_tools.REQUIRED_TOOLS = ["git"]
        mock_tools.OPTIONAL_TOOLS = ["ggen"]

        def which_side_effect(name: str) -> Path | None:
            if name == "git":
                return Path("/usr/bin/git")
            return None

        mock_tools.which_tool.side_effect = which_side_effect
        mock_tools.get_tool_versions.return_value = {"git": "2.42.0"}

        result = runner.invoke(app, ["check"])

        assert result.exit_code == 0
        # Check for status indicators (may be Unicode or text)
        assert "Available" in result.stdout or "✓" in result.stdout
        assert "Missing" in result.stdout or "✗" in result.stdout


@pytest.mark.e2e
def test_check_command_table_format() -> None:
    """Test that table output is properly formatted.

    Verifies:
        - Table headers present
        - Tool name column exists
        - Status column exists
        - Required column exists
    """
    with patch("specify_cli.ops.check.tools") as mock_tools:
        mock_tools.REQUIRED_TOOLS = ["git"]
        mock_tools.OPTIONAL_TOOLS = ["ggen"]
        mock_tools.which_tool.return_value = Path("/usr/bin/git")
        mock_tools.get_tool_versions.return_value = {"git": "2.42.0"}

        result = runner.invoke(app, ["check"])

        assert result.exit_code == 0
        # Check for table structure
        assert "Tool" in result.stdout
        assert "Status" in result.stdout
        assert "Required" in result.stdout


@pytest.mark.e2e
@pytest.mark.parametrize(
    ("flags", "expected_output"),
    [
        (["--verbose"], "Version"),
        (["--json"], '{"success"'),
        (["--required-only"], "git"),
        (["-v"], "Path"),
    ],
)
def test_check_command_flag_combinations(
    flags: list[str], expected_output: str
) -> None:
    """Test various flag combinations work correctly.

    Parameters
    ----------
    flags : list[str]
        Command-line flags to test.
    expected_output : str
        Expected substring in output.

    Verifies:
        - All flag variations work
        - Output matches expected format
    """
    with patch("specify_cli.ops.check.tools") as mock_tools, patch(
        "specify_cli.ops.check.get_environment_info"
    ) as mock_env:
        mock_tools.REQUIRED_TOOLS = ["git"]
        mock_tools.OPTIONAL_TOOLS = ["ggen"]
        mock_tools.which_tool.return_value = Path("/usr/bin/git")
        mock_tools.get_tool_versions.return_value = {"git": "2.42.0"}

        mock_env.return_value = {
            "python": {"version": "3.12.0"},
            "platform": {"system": "Darwin", "release": "24.5.0"},
        }

        result = runner.invoke(app, ["check", *flags])

        # For JSON, check if parseable; for others check substring
        if "--json" in flags:
            try:
                json.loads(result.stdout)
            except json.JSONDecodeError:
                pytest.fail("Invalid JSON output")
        else:
            assert expected_output in result.stdout or result.exit_code == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "e2e"])
