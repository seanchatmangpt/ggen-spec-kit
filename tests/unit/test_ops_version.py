"""
Unit tests for specify_cli.ops.version module.

Tests cover version checking business logic with mocked runtime calls.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from specify_cli.ops.version import (
    CURRENT_VERSION,
    VersionInfo,
    _is_newer_version,
    _parse_version,
    check_for_updates,
    get_build_info,
    get_current_version,
    get_version_info,
)


class TestGetVersion:
    """Tests for get_current_version() function."""

    def test_get_version_returns_string(self) -> None:
        """Test get_current_version returns version string."""
        version = get_current_version()

        assert isinstance(version, str)
        assert version == CURRENT_VERSION

    def test_version_format_valid(self) -> None:
        """Test version string follows semantic versioning format."""
        version = get_current_version()

        # Should match semantic versioning (e.g., "0.0.25")
        parts = version.split(".")
        assert len(parts) >= 2
        assert all(part.split("-")[0].isdigit() for part in parts if part)

    def test_version_matches_pyproject(self) -> None:
        """Test version matches pyproject.toml declaration."""
        import tomllib
        from pathlib import Path

        # Read version from pyproject.toml
        pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"

        if pyproject_path.exists():
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)
                expected_version = data["project"]["version"]

            assert get_current_version() == expected_version


class TestParseVersion:
    """Tests for _parse_version() function."""

    def test_parse_simple_version(self) -> None:
        """Test parsing simple semantic version."""
        result = _parse_version("1.2.3")

        assert result == (1, 2, 3)

    def test_parse_version_with_v_prefix(self) -> None:
        """Test parsing version with 'v' prefix."""
        result = _parse_version("v1.2.3")

        assert result == (1, 2, 3)

    def test_parse_version_with_prerelease(self) -> None:
        """Test parsing version with prerelease tag strips non-numeric parts."""
        result = _parse_version("1.2.3-alpha.1")

        # "1.2.3-alpha.1" splits by '.' to ["1", "2", "3-alpha", "1"]
        # Each part then splits by '-' and '+', so we get (1, 2, 3, 1)
        # The numeric "1" from the prerelease suffix is included
        assert result == (1, 2, 3, 1)

    def test_parse_version_with_build_metadata(self) -> None:
        """Test parsing version with build metadata strips metadata prefix."""
        result = _parse_version("1.2.3+build.123")

        # "1.2.3+build.123" splits by '.' to ["1", "2", "3+build", "123"]
        # Each part splits by '+', so we get (1, 2, 3, 123)
        assert result == (1, 2, 3, 123)

    def test_parse_invalid_version(self) -> None:
        """Test parsing invalid version returns (0,)."""
        result = _parse_version("invalid")

        assert result == (0,)

    def test_parse_two_part_version(self) -> None:
        """Test parsing two-part version."""
        result = _parse_version("1.0")

        assert result == (1, 0)

    def test_parse_empty_string(self) -> None:
        """Test parsing empty string."""
        result = _parse_version("")

        assert result == (0,)


class TestIsNewerVersion:
    """Tests for _is_newer_version() function."""

    def test_newer_major_version(self) -> None:
        """Test newer major version is detected."""
        result = _is_newer_version("1.0.0", "2.0.0")

        assert result is True

    def test_newer_minor_version(self) -> None:
        """Test newer minor version is detected."""
        result = _is_newer_version("1.0.0", "1.1.0")

        assert result is True

    def test_newer_patch_version(self) -> None:
        """Test newer patch version is detected."""
        result = _is_newer_version("1.0.0", "1.0.1")

        assert result is True

    def test_same_version(self) -> None:
        """Test same version is not newer."""
        result = _is_newer_version("1.0.0", "1.0.0")

        assert result is False

    def test_older_version(self) -> None:
        """Test older version is not newer."""
        result = _is_newer_version("2.0.0", "1.0.0")

        assert result is False

    def test_different_length_versions(self) -> None:
        """Test comparing versions with different lengths."""
        result = _is_newer_version("1.0", "1.0.1")

        assert result is True

    def test_version_with_prefix(self) -> None:
        """Test comparing versions with 'v' prefix."""
        result = _is_newer_version("v1.0.0", "v1.1.0")

        assert result is True


class TestVersionInfo:
    """Tests for VersionInfo dataclass."""

    def test_default_values(self) -> None:
        """Test default values are set correctly."""
        info = VersionInfo(current_version="1.0.0")

        assert info.current_version == "1.0.0"
        assert info.latest_version is None
        assert info.update_available is False
        assert info.release_url is None
        assert info.release_notes is None
        assert info.check_time == 0.0
        assert info.error is None

    def test_full_values(self) -> None:
        """Test all values can be set."""
        info = VersionInfo(
            current_version="1.0.0",
            latest_version="1.1.0",
            update_available=True,
            release_url="https://github.com/repo/releases/tag/v1.1.0",
            release_notes="Bug fixes and improvements",
            check_time=0.5,
        )

        assert info.latest_version == "1.1.0"
        assert info.update_available is True
        assert info.release_url == "https://github.com/repo/releases/tag/v1.1.0"
        assert info.release_notes == "Bug fixes and improvements"
        assert info.check_time == 0.5

    def test_error_state(self) -> None:
        """Test error state can be set."""
        info = VersionInfo(
            current_version="1.0.0",
            error="Network timeout",
        )

        assert info.error == "Network timeout"
        assert info.update_available is False


class TestCheckForUpdates:
    """Tests for check_for_updates() function."""

    @pytest.fixture
    def mock_github(self) -> MagicMock:
        """Mock the github runtime module."""
        with patch("specify_cli.ops.version.github") as mock:
            yield mock

    def test_update_available(self, mock_github: MagicMock) -> None:
        """Test when update is available."""
        mock_github.fetch_latest_release.return_value = {
            "tag_name": "v1.1.0",
            "html_url": "https://github.com/repo/releases/tag/v1.1.0",
            "body": "Release notes",
        }

        with patch("specify_cli.ops.version.CURRENT_VERSION", "1.0.0"):
            info = check_for_updates()

        assert info.current_version == "1.0.0"
        assert info.latest_version == "1.1.0"
        assert info.update_available is True
        assert info.release_url == "https://github.com/repo/releases/tag/v1.1.0"
        assert info.release_notes == "Release notes"
        assert info.check_time > 0

    def test_no_update_available(self, mock_github: MagicMock) -> None:
        """Test when no update is available."""
        mock_github.fetch_latest_release.return_value = {
            "tag_name": "v1.0.0",
            "html_url": "https://github.com/repo/releases/tag/v1.0.0",
            "body": "Current release",
        }

        with patch("specify_cli.ops.version.CURRENT_VERSION", "1.0.0"):
            info = check_for_updates()

        assert info.update_available is False
        assert info.latest_version == "1.0.0"

    def test_custom_repo(self, mock_github: MagicMock) -> None:
        """Test checking custom repository."""
        mock_github.fetch_latest_release.return_value = {
            "tag_name": "v2.0.0",
            "html_url": "https://github.com/custom/repo/releases/tag/v2.0.0",
            "body": "",
        }

        info = check_for_updates(owner="custom", repo="repo")

        mock_github.fetch_latest_release.assert_called_once_with(
            owner="custom",
            repo="repo",
            token=None,
        )
        assert info.latest_version == "2.0.0"

    def test_with_github_token(self, mock_github: MagicMock) -> None:
        """Test using GitHub token for authentication."""
        mock_github.fetch_latest_release.return_value = {
            "tag_name": "v1.0.0",
            "html_url": "https://github.com/repo/releases",
            "body": "",
        }

        check_for_updates(token="ghp_test_token_12345")

        mock_github.fetch_latest_release.assert_called_once_with(
            owner="github",
            repo="spec-kit",
            token="ghp_test_token_12345",
        )

    def test_error_handling(self, mock_github: MagicMock) -> None:
        """Test error during update check is handled."""
        mock_github.fetch_latest_release.side_effect = Exception("API rate limit exceeded")

        info = check_for_updates()

        assert info.error == "API rate limit exceeded"
        assert info.latest_version is None
        assert info.update_available is False
        assert info.check_time > 0

    def test_missing_tag_name(self, mock_github: MagicMock) -> None:
        """Test handling missing tag_name in response."""
        mock_github.fetch_latest_release.return_value = {
            "html_url": "https://github.com/repo/releases",
            "body": "",
        }

        info = check_for_updates()

        assert info.latest_version == ""
        assert info.update_available is False


class TestGetVersionInfo:
    """Tests for get_version_info() function."""

    @pytest.fixture
    def mock_check_updates(self) -> MagicMock:
        """Mock check_for_updates function."""
        with patch("specify_cli.ops.version.check_for_updates") as mock:
            yield mock

    def test_with_update_check(self, mock_check_updates: MagicMock) -> None:
        """Test getting version info with update check."""
        expected_info = VersionInfo(
            current_version="1.0.0",
            latest_version="1.1.0",
            update_available=True,
        )
        mock_check_updates.return_value = expected_info

        info = get_version_info(check_updates=True)

        assert info == expected_info
        mock_check_updates.assert_called_once_with(token=None)

    def test_without_update_check(self, mock_check_updates: MagicMock) -> None:
        """Test getting version info without update check."""
        info = get_version_info(check_updates=False)

        assert info.current_version == CURRENT_VERSION
        assert info.latest_version is None
        assert info.update_available is False
        mock_check_updates.assert_not_called()

    def test_with_token(self, mock_check_updates: MagicMock) -> None:
        """Test passing GitHub token to update check."""
        mock_check_updates.return_value = VersionInfo(current_version="1.0.0")

        get_version_info(check_updates=True, token="test_token")

        mock_check_updates.assert_called_once_with(token="test_token")


class TestGetBuildInfo:
    """Tests for get_build_info() function."""

    def test_returns_dict(self) -> None:
        """Test returns dictionary with expected keys."""
        info = get_build_info()

        assert isinstance(info, dict)
        assert "version" in info
        assert "python_version" in info
        assert "platform" in info

    def test_includes_version(self) -> None:
        """Test includes current version."""
        info = get_build_info()

        assert info["version"] == CURRENT_VERSION

    def test_includes_python_version(self) -> None:
        """Test includes Python version."""
        import sys

        info = get_build_info()

        expected = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        assert info["python_version"] == expected

    def test_includes_platform(self) -> None:
        """Test includes platform information."""
        import sys

        info = get_build_info()

        assert info["platform"] == sys.platform

    def test_includes_dependencies(self) -> None:
        """Test includes dependency versions when available."""
        info = get_build_info()

        assert "dependencies" in info
        # Dependencies dict may be empty if packages not installed
        assert isinstance(info["dependencies"], dict)

    def test_includes_otel_status(self) -> None:
        """Test includes OTEL availability status."""
        info = get_build_info()

        assert "otel_available" in info
        assert isinstance(info["otel_available"], bool)

    def test_handles_missing_dependencies_gracefully(self) -> None:
        """Test gracefully handles missing dependency information."""
        with patch("specify_cli.ops.version.get_pkg_version") as mock_version:
            mock_version.side_effect = Exception("Package not found")

            info = get_build_info()

            # Should still return info even if dependencies can't be determined
            assert "dependencies" in info
            assert isinstance(info["dependencies"], dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
