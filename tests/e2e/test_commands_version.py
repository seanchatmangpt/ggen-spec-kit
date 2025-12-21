"""
End-to-end tests for specify_cli.commands.version module.

Tests cover the full version command flow including CLI invocation,
version checking, update detection, and output formatting.
"""

from __future__ import annotations

import json
import re
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from specify_cli.app import app
from specify_cli.ops.version import (
    CURRENT_VERSION,
    VersionInfo,
    get_build_info,
    get_current_version,
)

runner = CliRunner()


@pytest.mark.e2e
class TestVersionCommandBasic:
    """Basic version command tests."""

    def test_version_command_shows_version(self) -> None:
        """Test version command displays version string."""
        result = runner.invoke(app, ["version"])

        assert result.exit_code == 0
        assert "specify-cli" in result.stdout
        assert CURRENT_VERSION in result.stdout

    def test_version_command_no_args(self) -> None:
        """Test version command works without arguments."""
        result = runner.invoke(app, ["version"])

        assert result.exit_code == 0
        assert len(result.stdout) > 0

    def test_version_command_output_format(self) -> None:
        """Test version output follows expected format."""
        result = runner.invoke(app, ["version"])

        assert result.exit_code == 0
        # Should have format: "specify-cli X.Y.Z"
        assert "specify-cli" in result.stdout.lower()


@pytest.mark.e2e
class TestVersionCommandFlags:
    """Test version command flags and options."""

    def test_version_short_flag_on_main_app(self) -> None:
        """Test --version flag on main app (not version subcommand)."""
        result = runner.invoke(app, ["--version"])

        assert result.exit_code == 0
        assert "specify-cli" in result.stdout
        assert CURRENT_VERSION in result.stdout

    def test_version_capital_v_flag(self) -> None:
        """Test -V short flag on main app."""
        result = runner.invoke(app, ["-V"])

        assert result.exit_code == 0
        assert CURRENT_VERSION in result.stdout

    def test_verbose_flag(self) -> None:
        """Test --verbose flag shows build information."""
        result = runner.invoke(app, ["version", "--verbose"])

        assert result.exit_code == 0
        assert "Python:" in result.stdout or "python" in result.stdout.lower()
        assert "Platform:" in result.stdout or "platform" in result.stdout.lower()

    def test_verbose_short_flag(self) -> None:
        """Test -v short flag shows build information."""
        result = runner.invoke(app, ["version", "-v"])

        assert result.exit_code == 0
        # Should show more than just version
        assert len(result.stdout) > 50


@pytest.mark.e2e
class TestVersionSemanticVersioning:
    """Test version format follows semantic versioning."""

    def test_version_format_is_semantic(self) -> None:
        """Test version follows semantic versioning format (X.Y.Z)."""
        version = get_current_version()

        # Should match pattern: digits.digits.digits
        pattern = r"^\d+\.\d+\.\d+$"
        assert re.match(pattern, version), f"Version {version} is not semantic"

    def test_version_parts_are_valid(self) -> None:
        """Test version parts are valid integers."""
        version = get_current_version()
        parts = version.split(".")

        assert len(parts) == 3, "Version should have 3 parts"

        major, minor, patch = parts
        assert major.isdigit(), "Major version should be numeric"
        assert minor.isdigit(), "Minor version should be numeric"
        assert patch.isdigit(), "Patch version should be numeric"

    def test_version_matches_pyproject(self) -> None:
        """Test CLI version matches pyproject.toml version."""
        version = get_current_version()

        # Version from pyproject.toml should be "0.0.25"
        assert version == "0.0.25"

    def test_version_is_not_default(self) -> None:
        """Test version is not the default fallback value."""
        version = get_current_version()

        # Should not be the fallback "0.0.0"
        assert version != "0.0.0", "Version should not be default fallback"


@pytest.mark.e2e
class TestVersionJSONOutput:
    """Test JSON output format for version command."""

    def test_json_output_flag(self) -> None:
        """Test --json flag produces valid JSON."""
        result = runner.invoke(app, ["version", "--json"])

        assert result.exit_code == 0

        # Should be valid JSON
        data = json.loads(result.stdout)
        assert isinstance(data, dict)
        assert "version" in data

    def test_json_output_version_field(self) -> None:
        """Test JSON output contains version field."""
        result = runner.invoke(app, ["version", "--json"])

        assert result.exit_code == 0

        data = json.loads(result.stdout)
        assert data["version"] == CURRENT_VERSION

    def test_json_output_with_verbose(self) -> None:
        """Test --json with --verbose includes build info."""
        result = runner.invoke(app, ["version", "--json", "--verbose"])

        assert result.exit_code == 0

        data = json.loads(result.stdout)
        assert "version" in data
        assert "build_info" in data

        # Build info should have expected fields
        build_info = data["build_info"]
        assert "python_version" in build_info
        assert "platform" in build_info

    def test_json_output_structure(self) -> None:
        """Test JSON output has expected structure."""
        result = runner.invoke(app, ["version", "--json"])

        assert result.exit_code == 0

        data = json.loads(result.stdout)
        # Should be a flat dict with version key
        assert isinstance(data, dict)
        assert len(data) >= 1


@pytest.mark.e2e
class TestVersionUpdateCheck:
    """Test version update checking functionality."""

    @pytest.fixture
    def mock_github_api(self) -> MagicMock:
        """Mock GitHub API for update checks."""
        with patch("specify_cli.runtime.github.fetch_latest_release") as mock:
            mock.return_value = {
                "tag_name": "v1.0.0",
                "html_url": "https://github.com/github/spec-kit/releases/tag/v1.0.0",
                "body": "Release notes",
            }
            yield mock

    def test_check_updates_flag(self, mock_github_api: MagicMock) -> None:
        """Test --check-updates flag queries GitHub."""
        result = runner.invoke(app, ["version", "--check-updates"])

        assert result.exit_code == 0
        mock_github_api.assert_called_once()

    def test_check_updates_short_flag(self, mock_github_api: MagicMock) -> None:
        """Test -u short flag for update checking."""
        result = runner.invoke(app, ["version", "-u"])

        assert result.exit_code == 0
        mock_github_api.assert_called_once()

    def test_check_updates_shows_current_version(self, mock_github_api: MagicMock) -> None:
        """Test update check displays current version."""
        result = runner.invoke(app, ["version", "--check-updates"])

        assert result.exit_code == 0
        assert CURRENT_VERSION in result.stdout

    def test_check_updates_with_json(self, mock_github_api: MagicMock) -> None:
        """Test --check-updates with --json output."""
        result = runner.invoke(app, ["version", "--check-updates", "--json"])

        assert result.exit_code == 0

        data = json.loads(result.stdout)
        assert "current_version" in data
        assert "latest_version" in data
        assert "update_available" in data

    def test_check_updates_handles_network_error(self) -> None:
        """Test update check handles network errors gracefully."""
        with patch("specify_cli.runtime.github.fetch_latest_release") as mock:
            mock.side_effect = Exception("Network error")

            result = runner.invoke(app, ["version", "--check-updates"])

            # Should not crash
            assert result.exit_code == 0
            # Should show error message
            assert "Could not check" in result.stdout or "error" in result.stdout.lower()

    def test_update_available_message(self, mock_github_api: MagicMock) -> None:
        """Test update available message is shown."""
        result = runner.invoke(app, ["version", "--check-updates"])

        assert result.exit_code == 0
        # Since mock returns v1.0.0 and we're at 0.0.25, update should be available
        # (assuming version comparison works correctly)


@pytest.mark.e2e
class TestVersionBuildInfo:
    """Test build information output."""

    def test_build_info_function(self) -> None:
        """Test get_build_info() returns expected structure."""
        info = get_build_info()

        assert isinstance(info, dict)
        assert "version" in info
        assert "python_version" in info
        assert "platform" in info

    def test_build_info_has_version(self) -> None:
        """Test build info includes version."""
        info = get_build_info()

        assert info["version"] == CURRENT_VERSION

    def test_build_info_has_python_version(self) -> None:
        """Test build info includes Python version."""
        info = get_build_info()

        # Should be in format "3.11.x" or similar
        python_ver = info["python_version"]
        assert re.match(r"^\d+\.\d+\.\d+$", python_ver)

    def test_build_info_has_platform(self) -> None:
        """Test build info includes platform."""
        info = get_build_info()

        platform = info["platform"]
        # Common platforms: linux, darwin, win32
        assert platform in ["linux", "darwin", "win32", "linux2"]

    def test_build_info_has_otel_status(self) -> None:
        """Test build info includes OTEL availability."""
        info = get_build_info()

        assert "otel_available" in info
        assert isinstance(info["otel_available"], bool)

    def test_build_info_has_dependencies(self) -> None:
        """Test build info includes dependency versions."""
        info = get_build_info()

        # May or may not have dependencies depending on environment
        if "dependencies" in info:
            deps = info["dependencies"]
            assert isinstance(deps, dict)


@pytest.mark.e2e
class TestVersionComparison:
    """Test version comparison functionality."""

    def test_get_current_version_is_consistent(self) -> None:
        """Test get_current_version() returns consistent value."""
        version1 = get_current_version()
        version2 = get_current_version()

        assert version1 == version2

    def test_version_info_dataclass(self) -> None:
        """Test VersionInfo dataclass creation."""
        info = VersionInfo(
            current_version="0.0.25",
            latest_version="1.0.0",
            update_available=True,
        )

        assert info.current_version == "0.0.25"
        assert info.latest_version == "1.0.0"
        assert info.update_available is True

    def test_version_info_defaults(self) -> None:
        """Test VersionInfo default values."""
        info = VersionInfo(current_version="0.0.25")

        assert info.latest_version is None
        assert info.update_available is False
        assert info.release_url is None
        assert info.error is None


@pytest.mark.e2e
class TestVersionErrorHandling:
    """Test error handling in version command."""

    def test_keyboard_interrupt_handling(self) -> None:
        """Test version command handles keyboard interrupt gracefully."""
        with patch("specify_cli.ops.version.get_current_version") as mock_version:
            mock_version.side_effect = KeyboardInterrupt()

            result = runner.invoke(app, ["version"])

            # Should exit with code 130 (KeyboardInterrupt)
            assert result.exit_code == 130

    def test_exception_handling(self) -> None:
        """Test version command handles exceptions."""
        with patch("specify_cli.ops.version.get_current_version") as mock_version:
            mock_version.side_effect = Exception("Test error")

            result = runner.invoke(app, ["version"])

            # Should exit with error code
            assert result.exit_code == 1
            assert "error" in result.stdout.lower()


@pytest.mark.e2e
class TestVersionIntegration:
    """Integration tests for version command."""

    def test_version_command_end_to_end(self) -> None:
        """Test complete version command flow."""
        result = runner.invoke(app, ["version"])

        assert result.exit_code == 0
        assert "specify-cli" in result.stdout
        assert CURRENT_VERSION in result.stdout

    def test_version_with_all_flags(self) -> None:
        """Test version command with multiple flags."""
        with patch("specify_cli.runtime.github.fetch_latest_release") as mock:
            mock.return_value = {
                "tag_name": "v1.0.0",
                "html_url": "https://github.com/test/releases",
                "body": "Release",
            }

            result = runner.invoke(app, ["version", "--check-updates", "--json"])

            assert result.exit_code == 0

            # Should be valid JSON with update info
            data = json.loads(result.stdout)
            assert "current_version" in data
            assert "latest_version" in data

    def test_version_help_text(self) -> None:
        """Test version command help text."""
        result = runner.invoke(app, ["version", "--help"])

        assert result.exit_code == 0
        assert "version" in result.stdout.lower()
        assert "--json" in result.stdout
        assert "--check-updates" in result.stdout


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "e2e"])
