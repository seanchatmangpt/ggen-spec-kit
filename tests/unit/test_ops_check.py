"""
Unit tests for specify_cli.ops.check module.

Tests cover tool checking business logic with mocked runtime calls.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from specify_cli.ops.check import (
    CheckResult,
    ToolStatus,
    check_all_tools,
    check_tool,
    get_environment_info,
    get_tool_status,
)


class TestToolStatus:
    """Tests for ToolStatus dataclass."""

    def test_default_values(self) -> None:
        """Test default values are set correctly."""
        status = ToolStatus(name="git", available=True, required=True)

        assert status.name == "git"
        assert status.available is True
        assert status.required is True
        assert status.path is None
        assert status.version is None
        assert status.error is None

    def test_full_values(self) -> None:
        """Test all values can be set."""
        status = ToolStatus(
            name="git",
            available=True,
            required=True,
            path="/usr/bin/git",
            version="2.42.0",
        )

        assert status.path == "/usr/bin/git"
        assert status.version == "2.42.0"

    def test_unavailable_with_error(self) -> None:
        """Test unavailable status with error."""
        status = ToolStatus(
            name="ggen",
            available=False,
            required=False,
            error="Not found in PATH",
        )

        assert status.available is False
        assert status.error == "Not found in PATH"


class TestCheckResult:
    """Tests for CheckResult dataclass."""

    def test_default_values(self) -> None:
        """Test default values are set correctly."""
        result = CheckResult(success=True)

        assert result.success is True
        assert result.available == []
        assert result.missing == []
        assert result.warnings == []
        assert result.duration == 0.0

    def test_all_required_available(self) -> None:
        """Test all_required_available property."""
        result = CheckResult(
            success=True,
            available=[ToolStatus(name="git", available=True, required=True)],
            missing=[ToolStatus(name="ggen", available=False, required=False)],
        )

        assert result.all_required_available is True

    def test_required_missing(self) -> None:
        """Test all_required_available when required tool is missing."""
        result = CheckResult(
            success=False,
            available=[],
            missing=[ToolStatus(name="git", available=False, required=True)],
        )

        assert result.all_required_available is False

    def test_tool_count(self) -> None:
        """Test tool_count property."""
        result = CheckResult(
            success=False,
            available=[
                ToolStatus(name="git", available=True, required=True),
                ToolStatus(name="python", available=True, required=True),
            ],
            missing=[
                ToolStatus(name="ggen", available=False, required=False),
                ToolStatus(name="cargo", available=False, required=True),
            ],
        )

        counts = result.tool_count
        assert counts["available"] == 2
        assert counts["missing"] == 2
        assert counts["required_missing"] == 1


class TestCheckTool:
    """Tests for check_tool() function."""

    def test_tool_available(self) -> None:
        """Test checking an available tool."""
        with patch("specify_cli.ops.check.tools.which_tool") as mock_which:
            mock_which.return_value = "/usr/bin/git"

            status = check_tool("git", required=True)

            assert status.available is True
            assert status.path == "/usr/bin/git"
            assert status.required is True
            mock_which.assert_called_once_with("git")

    def test_tool_not_available(self) -> None:
        """Test checking an unavailable tool."""
        with patch("specify_cli.ops.check.tools.which_tool") as mock_which:
            mock_which.return_value = None

            status = check_tool("ggen", required=False)

            assert status.available is False
            assert status.path is None
            assert status.required is False

    def test_tool_check_error(self) -> None:
        """Test error during tool check."""
        with patch("specify_cli.ops.check.tools.which_tool") as mock_which:
            mock_which.side_effect = Exception("Permission denied")

            status = check_tool("git")

            assert status.available is False
            assert status.error == "Permission denied"


class TestGetToolStatus:
    """Tests for get_tool_status() function."""

    def test_available_with_version(self) -> None:
        """Test status includes version when available."""
        with patch("specify_cli.ops.check.tools.which_tool") as mock_which, patch(
            "specify_cli.ops.check.tools.get_tool_versions"
        ) as mock_versions, patch(
            "specify_cli.ops.check.tools.REQUIRED_TOOLS", ["git"]
        ):
            mock_which.return_value = "/usr/bin/git"
            mock_versions.return_value = {"git": "2.42.0"}

            status = get_tool_status("git")

            assert status.available is True
            assert status.version == "2.42.0"

    def test_unavailable_no_version(self) -> None:
        """Test status has no version when unavailable."""
        with patch("specify_cli.ops.check.tools.which_tool") as mock_which, patch(
            "specify_cli.ops.check.tools.REQUIRED_TOOLS", []
        ):
            mock_which.return_value = None

            status = get_tool_status("ggen")

            assert status.available is False
            assert status.version is None


class TestCheckAllTools:
    """Tests for check_all_tools() function."""

    @pytest.fixture
    def mock_tools(self) -> MagicMock:
        """Mock the tools module."""
        with patch("specify_cli.ops.check.tools") as mock:
            mock.REQUIRED_TOOLS = ["git"]
            mock.OPTIONAL_TOOLS = ["claude", "ggen", "uv"]
            yield mock

    def test_all_tools_available(self, mock_tools: MagicMock) -> None:
        """Test when all tools are available."""
        mock_tools.which_tool.return_value = "/usr/bin/tool"

        result = check_all_tools()

        assert result.success is True
        assert len(result.available) == 4  # 1 required + 3 optional
        assert len(result.missing) == 0

    def test_required_tool_missing(self, mock_tools: MagicMock) -> None:
        """Test when required tool is missing."""

        def which_side_effect(name: str) -> str | None:
            if name == "git":
                return None
            return f"/usr/bin/{name}"

        mock_tools.which_tool.side_effect = which_side_effect

        result = check_all_tools()

        assert result.success is False
        assert any(t.name == "git" for t in result.missing)
        assert result.tool_count["required_missing"] == 1

    def test_optional_tool_missing(self, mock_tools: MagicMock) -> None:
        """Test when optional tool is missing (still success)."""

        def which_side_effect(name: str) -> str | None:
            if name == "ggen":
                return None
            return f"/usr/bin/{name}"

        mock_tools.which_tool.side_effect = which_side_effect

        result = check_all_tools()

        assert result.success is True  # Still success (only optional missing)
        assert any(t.name == "ggen" for t in result.missing)

    def test_exclude_optional(self, mock_tools: MagicMock) -> None:
        """Test excluding optional tools."""
        mock_tools.which_tool.return_value = "/usr/bin/tool"

        result = check_all_tools(include_optional=False)

        assert result.success is True
        assert len(result.available) == 1  # Only required

    def test_additional_tools(self, mock_tools: MagicMock) -> None:
        """Test checking additional tools."""
        mock_tools.which_tool.return_value = "/usr/bin/tool"

        result = check_all_tools(additional_tools=["custom-tool"])

        # Should include the additional tool
        assert any(t.name == "custom-tool" for t in result.available)

    def test_duration_recorded(self, mock_tools: MagicMock) -> None:
        """Test duration is recorded."""
        mock_tools.which_tool.return_value = "/usr/bin/tool"

        result = check_all_tools()

        assert result.duration > 0


class TestGetEnvironmentInfo:
    """Tests for get_environment_info() function."""

    def test_returns_dict(self) -> None:
        """Test returns dictionary with expected keys."""
        with patch("specify_cli.core.config.get_config") as mock_config:
            mock_config.return_value = MagicMock(
                cache_dir="/tmp/cache",
                config_dir="/tmp/config",
                otel_enabled=False,
            )

            info = get_environment_info()

            assert isinstance(info, dict)
            assert "python" in info
            assert "platform" in info
            assert "specify" in info
            assert "environment" in info

    def test_python_info(self) -> None:
        """Test Python info is included."""
        with patch("specify_cli.core.config.get_config") as mock_config:
            mock_config.return_value = MagicMock(
                cache_dir="/tmp/cache",
                config_dir="/tmp/config",
                otel_enabled=False,
            )

            info = get_environment_info()

            assert "version" in info["python"]
            assert "executable" in info["python"]

    def test_platform_info(self) -> None:
        """Test platform info is included."""
        with patch("specify_cli.core.config.get_config") as mock_config:
            mock_config.return_value = MagicMock(
                cache_dir="/tmp/cache",
                config_dir="/tmp/config",
                otel_enabled=False,
            )

            info = get_environment_info()

            assert "system" in info["platform"]
            assert "release" in info["platform"]
            assert "machine" in info["platform"]

    def test_path_truncated(self) -> None:
        """Test PATH is truncated for readability."""
        with patch("specify_cli.core.config.get_config") as mock_config, patch.dict(
            "os.environ", {"PATH": "a" * 500}
        ):
            mock_config.return_value = MagicMock(
                cache_dir="/tmp/cache",
                config_dir="/tmp/config",
                otel_enabled=False,
            )

            info = get_environment_info()

            assert len(info["environment"]["PATH"]) < 300
            assert info["environment"]["PATH"].endswith("...")
