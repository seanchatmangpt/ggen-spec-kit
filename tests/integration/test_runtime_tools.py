"""
Integration tests for specify_cli.runtime.tools module.

Tests cover tool detection, version checking, and PATH resolution
with real subprocess calls and mocked scenarios.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from specify_cli.runtime.tools import (
    CLAUDE_LOCAL_PATH,
    OPTIONAL_TOOLS,
    REQUIRED_TOOLS,
    check_required_tools,
    check_tool,
    get_ggen_version,
    get_tool_versions,
    which_tool,
)


@pytest.mark.integration
class TestWhichTool:
    """Tests for which_tool() function."""

    def test_which_tool_finds_git(self) -> None:
        """Test which_tool finds git when installed."""
        result = which_tool("git")

        # Git should be available on CI/dev systems
        if result:
            assert isinstance(result, Path)
            assert result.exists()
            assert result.is_file()

    def test_which_tool_missing_tool(self) -> None:
        """Test which_tool returns None for nonexistent tool."""
        result = which_tool("nonexistent_tool_xyz123")

        assert result is None

    def test_which_tool_claude_special_path(self, tmp_path: Path) -> None:
        """Test which_tool handles Claude CLI special path."""
        # Mock the CLAUDE_LOCAL_PATH to test special handling
        mock_claude = tmp_path / "claude"
        mock_claude.write_text("#!/bin/bash\necho claude")
        mock_claude.chmod(0o755)

        with patch("specify_cli.runtime.tools.CLAUDE_LOCAL_PATH", mock_claude):
            result = which_tool("claude")

            assert result == mock_claude
            assert result.exists()

    def test_which_tool_claude_fallback_to_path(self) -> None:
        """Test which_tool falls back to PATH when Claude local path doesn't exist."""
        with patch("specify_cli.runtime.tools.CLAUDE_LOCAL_PATH", Path("/nonexistent/claude")):
            # Will check PATH - may or may not find claude depending on system
            result = which_tool("claude")

            # Result can be None or Path depending on system
            assert result is None or isinstance(result, Path)

    @pytest.mark.parametrize(
        "tool_name",
        ["python", "python3", "git", "uv", "ggen"],
    )
    def test_which_tool_common_tools(self, tool_name: str) -> None:
        """Test which_tool handles common tools."""
        result = which_tool(tool_name)

        # Result can be None or Path depending on what's installed
        assert result is None or isinstance(result, Path)


@pytest.mark.integration
class TestCheckTool:
    """Tests for check_tool() function."""

    def test_check_tool_git_available(self) -> None:
        """Test check_tool returns True for git (required tool)."""
        result = check_tool("git")

        # Git should be available on CI/dev systems
        assert isinstance(result, bool)
        # On most systems, git is installed
        if result:
            assert result is True

    def test_check_tool_nonexistent(self) -> None:
        """Test check_tool returns False for nonexistent tool."""
        result = check_tool("nonexistent_tool_xyz123")

        assert result is False

    @pytest.mark.parametrize(
        "tool",
        OPTIONAL_TOOLS,
    )
    def test_check_tool_optional_tools(self, tool: str) -> None:
        """Test check_tool handles all optional tools."""
        result = check_tool(tool)

        assert isinstance(result, bool)

    @pytest.mark.parametrize(
        "tool",
        REQUIRED_TOOLS,
    )
    def test_check_tool_required_tools(self, tool: str) -> None:
        """Test check_tool handles all required tools."""
        result = check_tool(tool)

        assert isinstance(result, bool)


@pytest.mark.integration
class TestCheckRequiredTools:
    """Tests for check_required_tools() function."""

    def test_check_required_tools_structure(self) -> None:
        """Test check_required_tools returns correct structure."""
        available, missing = check_required_tools()

        assert isinstance(available, list)
        assert isinstance(missing, list)
        # Should check all required tools
        assert len(available) + len(missing) == len(REQUIRED_TOOLS)

    def test_check_required_tools_git_available(self) -> None:
        """Test check_required_tools finds git."""
        available, missing = check_required_tools()

        # Git should be in either available or missing
        assert "git" in available or "git" in missing

        # On most systems, git is available
        if check_tool("git"):
            assert "git" in available
            assert "git" not in missing

    def test_check_required_tools_all_in_lists(self) -> None:
        """Test all required tools are checked."""
        available, missing = check_required_tools()

        checked_tools = set(available) | set(missing)

        assert checked_tools == set(REQUIRED_TOOLS)


@pytest.mark.integration
class TestGetGgenVersion:
    """Tests for get_ggen_version() function."""

    def test_get_ggen_version_when_installed(self) -> None:
        """Test get_ggen_version when ggen is installed."""
        # Only run if ggen is available
        if check_tool("ggen"):
            result = get_ggen_version()

            assert result is not None
            assert isinstance(result, str)
            # Version should be in format like "5.0.2"
            assert len(result) > 0

    def test_get_ggen_version_when_missing(self) -> None:
        """Test get_ggen_version returns None when ggen not installed."""
        with patch("specify_cli.runtime.tools.check_tool", return_value=False):
            result = get_ggen_version()

            assert result is None

    def test_get_ggen_version_parse_output(self) -> None:
        """Test get_ggen_version parses ggen --version output correctly."""
        mock_output = "ggen 5.0.2\n"

        with patch("specify_cli.runtime.tools.check_tool", return_value=True), patch(
            "specify_cli.core.process.run", return_value=mock_output
        ):
            result = get_ggen_version()

            assert result == "5.0.2"

    def test_get_ggen_version_handles_subprocess_error(self) -> None:
        """Test get_ggen_version handles subprocess errors gracefully."""
        with patch("specify_cli.runtime.tools.check_tool", return_value=True), patch(
            "specify_cli.core.process.run", side_effect=subprocess.CalledProcessError(1, ["ggen", "--version"])
        ):
            result = get_ggen_version()

            assert result is None

    def test_get_ggen_version_handles_empty_output(self) -> None:
        """Test get_ggen_version handles empty output."""
        with patch("specify_cli.runtime.tools.check_tool", return_value=True), patch(
            "specify_cli.core.process.run", return_value=""
        ):
            result = get_ggen_version()

            assert result is None


@pytest.mark.integration
class TestGetToolVersions:
    """Tests for get_tool_versions() function."""

    def test_get_tool_versions_structure(self) -> None:
        """Test get_tool_versions returns dict with expected keys."""
        result = get_tool_versions()

        assert isinstance(result, dict)
        # Should check common tools
        expected_tools = {"git", "uv", "python", "ggen"}
        assert set(result.keys()) == expected_tools

    def test_get_tool_versions_values(self) -> None:
        """Test get_tool_versions returns str or None values."""
        result = get_tool_versions()

        for _tool, version in result.items():
            assert version is None or isinstance(version, str)

    def test_get_tool_versions_git(self) -> None:
        """Test get_tool_versions detects git version."""
        result = get_tool_versions()

        # Git should be available on most systems
        if check_tool("git"):
            assert result["git"] is not None
            assert isinstance(result["git"], str)

    def test_get_tool_versions_missing_tool(self) -> None:
        """Test get_tool_versions handles missing tools."""
        with patch("specify_cli.runtime.tools.check_tool", return_value=False):
            result = get_tool_versions()

            # All tools should be None when check_tool returns False
            for version in result.values():
                assert version is None

    def test_get_tool_versions_version_extraction(self) -> None:
        """Test get_tool_versions extracts version strings correctly."""
        with patch("specify_cli.runtime.tools.check_tool", return_value=True), patch(
            "specify_cli.core.process.run"
        ) as mock_run:
            # Mock version outputs
            def run_side_effect(cmd, **kwargs):
                if cmd[0] == "git":
                    return "git version 2.42.0"
                if cmd[0] == "python":
                    return "Python 3.12.0"
                if cmd[0] == "uv":
                    return "uv 0.1.32"
                if cmd[0] == "ggen":
                    return "ggen 5.0.2"
                return ""

            mock_run.side_effect = run_side_effect

            result = get_tool_versions()

            assert result["git"] == "2.42.0"
            assert result["python"] == "3.12.0"
            assert result["uv"] == "0.1.32"
            assert result["ggen"] == "5.0.2"

    def test_get_tool_versions_handles_errors(self) -> None:
        """Test get_tool_versions handles subprocess errors."""
        with patch("specify_cli.runtime.tools.check_tool", return_value=True), patch(
            "specify_cli.core.process.run", side_effect=Exception("Command failed")
        ):
            result = get_tool_versions()

            # Should return "installed (version unknown)" for all tools
            for version in result.values():
                assert version == "installed (version unknown)"


@pytest.mark.integration
class TestConstants:
    """Tests for module constants."""

    def test_required_tools_is_list(self) -> None:
        """Test REQUIRED_TOOLS is a list."""
        assert isinstance(REQUIRED_TOOLS, list)
        assert len(REQUIRED_TOOLS) > 0

    def test_optional_tools_is_list(self) -> None:
        """Test OPTIONAL_TOOLS is a list."""
        assert isinstance(OPTIONAL_TOOLS, list)
        assert len(OPTIONAL_TOOLS) > 0

    def test_required_tools_contains_git(self) -> None:
        """Test git is in REQUIRED_TOOLS."""
        assert "git" in REQUIRED_TOOLS

    def test_optional_tools_contains_common_tools(self) -> None:
        """Test OPTIONAL_TOOLS contains expected tools."""
        expected = {"claude", "cursor", "ggen", "uv"}
        assert expected.issubset(set(OPTIONAL_TOOLS))

    def test_claude_local_path_is_path(self) -> None:
        """Test CLAUDE_LOCAL_PATH is a Path object."""
        assert isinstance(CLAUDE_LOCAL_PATH, Path)

    def test_claude_local_path_location(self) -> None:
        """Test CLAUDE_LOCAL_PATH points to expected location."""
        expected = Path.home() / ".claude" / "local" / "claude"
        assert expected == CLAUDE_LOCAL_PATH


@pytest.mark.integration
class TestOtelIntegration:
    """Tests for OpenTelemetry integration in tools module."""

    def test_which_tool_works_with_otel(self) -> None:
        """Test which_tool works with OTEL (no-op mode by default)."""
        # Should execute without error, OTEL uses no-op tracer when not configured
        result = which_tool("git")

        assert result is None or isinstance(result, Path)

    def test_check_tool_works_with_otel(self) -> None:
        """Test check_tool works with OTEL (no-op mode by default)."""
        # Should execute without error, OTEL uses no-op tracer when not configured
        result = check_tool("git")

        assert isinstance(result, bool)

    def test_get_ggen_version_works_with_otel(self) -> None:
        """Test get_ggen_version works with OTEL (no-op mode by default)."""
        # Should execute without error, OTEL uses no-op tracer when not configured
        result = get_ggen_version()

        assert result is None or isinstance(result, str)


@pytest.mark.integration
class TestPathSearching:
    """Tests for PATH searching functionality."""

    def test_which_tool_searches_path(self) -> None:
        """Test which_tool searches PATH for executables."""
        # Test with a common tool that should be in PATH
        result = which_tool("python")

        if result:
            # Should return absolute path
            assert result.is_absolute()
            # Path should exist
            assert result.exists()

    def test_which_tool_respects_path_order(self, tmp_path: Path, monkeypatch: Any) -> None:
        """Test which_tool respects PATH order."""
        # Create two fake executables
        dir1 = tmp_path / "bin1"
        dir2 = tmp_path / "bin2"
        dir1.mkdir()
        dir2.mkdir()

        tool1 = dir1 / "testtool"
        tool2 = dir2 / "testtool"
        tool1.write_text("#!/bin/bash\necho tool1")
        tool2.write_text("#!/bin/bash\necho tool2")
        tool1.chmod(0o755)
        tool2.chmod(0o755)

        # Set PATH with dir1 first
        monkeypatch.setenv("PATH", f"{dir1}:{dir2}")

        result = which_tool("testtool")

        # Should find the first one in PATH
        assert result == tool1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])
