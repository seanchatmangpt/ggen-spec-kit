"""
Pytest configuration for specify-cli test suite.

This module provides shared fixtures and configuration for the three-tier
architecture test suite:
- Unit tests: ops layer with mocked runtime
- Integration tests: runtime layer with real/mocked I/O
- E2E tests: full command layer testing

Fixtures
--------
- tmp_project_dir: Temporary directory for project tests
- mock_github_release: Mocked GitHub API response
- mock_tool_available: Mocked tool detection
- otel_test_context: OTEL testing utilities
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any, Generator
from unittest.mock import MagicMock, patch

import pytest

if TYPE_CHECKING:
    from collections.abc import Callable


# ============================================================================
# Pytest Configuration
# ============================================================================


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests (fast, no I/O)")
    config.addinivalue_line("markers", "integration: Integration tests (may have I/O)")
    config.addinivalue_line("markers", "e2e: End-to-end tests (full system)")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "requires_docker: Tests that require Docker to be running")
    config.addinivalue_line("markers", "requires_git: Tests that require git to be installed")
    config.addinivalue_line("markers", "requires_network: Tests that require network access")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Add markers based on test location."""
    for item in items:
        # Add markers based on path
        if "/unit/" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "/integration/" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "/e2e/" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)


# ============================================================================
# Directory Fixtures
# ============================================================================


@pytest.fixture
def tmp_project_dir(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a temporary directory for project tests.

    Yields
    ------
    Path
        Path to temporary project directory.
    """
    project_dir = tmp_path / "test-project"
    project_dir.mkdir(parents=True)
    yield project_dir


@pytest.fixture
def tmp_template_dir(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a temporary directory with mock template structure.

    Yields
    ------
    Path
        Path to temporary template directory with mock files.
    """
    template_dir = tmp_path / "template"
    template_dir.mkdir(parents=True)

    # Create mock template structure
    (template_dir / "spec-kit-main").mkdir()
    (template_dir / "spec-kit-main" / ".cursor").mkdir()
    (template_dir / "spec-kit-main" / ".cursor" / "rules").mkdir()

    # Create mock files
    (template_dir / "spec-kit-main" / "package.json").write_text(
        json.dumps({"name": "spec-kit-template", "version": "1.0.0"})
    )
    (template_dir / "spec-kit-main" / ".cursor" / "rules" / "README.md").write_text(
        "# Template Rules"
    )

    yield template_dir


@pytest.fixture
def original_cwd() -> Generator[Path, None, None]:
    """Save and restore the original working directory.

    Yields
    ------
    Path
        The original working directory.
    """
    original = Path.cwd()
    yield original
    os.chdir(original)


# ============================================================================
# GitHub API Fixtures
# ============================================================================


@pytest.fixture
def mock_github_release() -> dict[str, Any]:
    """Mock GitHub release API response.

    Returns
    -------
    dict
        Mock release data matching GitHub API format.
    """
    return {
        "tag_name": "v1.0.0",
        "name": "Release v1.0.0",
        "published_at": "2024-01-15T10:00:00Z",
        "html_url": "https://github.com/github/spec-kit/releases/tag/v1.0.0",
        "zipball_url": "https://api.github.com/repos/github/spec-kit/zipball/v1.0.0",
        "tarball_url": "https://api.github.com/repos/github/spec-kit/tarball/v1.0.0",
        "assets": [
            {
                "name": "spec-kit-v1.0.0.zip",
                "browser_download_url": "https://github.com/github/spec-kit/releases/download/v1.0.0/spec-kit-v1.0.0.zip",
                "size": 12345,
                "content_type": "application/zip",
            }
        ],
        "body": "Release notes for v1.0.0",
    }


@pytest.fixture
def mock_github_client(mock_github_release: dict[str, Any]) -> Generator[MagicMock, None, None]:
    """Mock httpx client for GitHub API calls.

    Yields
    ------
    MagicMock
        Mocked httpx client.
    """
    with patch("httpx.Client") as mock_client:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_github_release
        mock_response.raise_for_status = MagicMock()

        mock_instance = MagicMock()
        mock_instance.__enter__ = MagicMock(return_value=mock_instance)
        mock_instance.__exit__ = MagicMock(return_value=False)
        mock_instance.get.return_value = mock_response

        mock_client.return_value = mock_instance
        yield mock_client


# ============================================================================
# Tool Detection Fixtures
# ============================================================================


@pytest.fixture
def mock_tool_available() -> Callable[[str, bool], MagicMock]:
    """Factory fixture for mocking tool availability.

    Returns
    -------
    Callable
        Function that creates a context manager for mocking tool detection.
    """

    def _mock_tool(tool_name: str, available: bool = True) -> MagicMock:
        """Create mock for specific tool availability."""
        mock = patch("specify_cli.runtime.tools.check_tool_installed")
        mock_check = mock.start()

        def check_side_effect(name: str) -> bool:
            if name == tool_name:
                return available
            return True  # Default other tools to available

        mock_check.side_effect = check_side_effect
        return mock

    return _mock_tool


@pytest.fixture
def all_tools_available() -> Generator[MagicMock, None, None]:
    """Mock all tools as available.

    Yields
    ------
    MagicMock
        Mocked check_tool_installed function.
    """
    with patch("specify_cli.runtime.tools.check_tool_installed", return_value=True) as mock:
        yield mock


@pytest.fixture
def no_tools_available() -> Generator[MagicMock, None, None]:
    """Mock all tools as unavailable.

    Yields
    ------
    MagicMock
        Mocked check_tool_installed function.
    """
    with patch("specify_cli.runtime.tools.check_tool_installed", return_value=False) as mock:
        yield mock


# ============================================================================
# Process/Subprocess Fixtures
# ============================================================================


@pytest.fixture
def mock_run_logged() -> Generator[MagicMock, None, None]:
    """Mock the run_logged function for subprocess testing.

    Yields
    ------
    MagicMock
        Mocked run_logged function.
    """
    with patch("specify_cli.core.process.run_logged") as mock:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock.return_value = mock_result
        yield mock


@pytest.fixture
def mock_subprocess_run() -> Generator[MagicMock, None, None]:
    """Mock subprocess.run for direct subprocess testing.

    Yields
    ------
    MagicMock
        Mocked subprocess.run function.
    """
    with patch("subprocess.run") as mock:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = b""
        mock_result.stderr = b""
        mock.return_value = mock_result
        yield mock


# ============================================================================
# OpenTelemetry Testing Fixtures
# ============================================================================


@pytest.fixture
def otel_disabled() -> Generator[None, None, None]:
    """Disable OTEL for testing.

    Yields
    ------
    None
    """
    with patch.dict(os.environ, {"SPECIFY_OTEL_ENABLED": "false"}):
        yield


@pytest.fixture
def mock_tracer() -> Generator[MagicMock, None, None]:
    """Mock OTEL tracer for span testing.

    Yields
    ------
    MagicMock
        Mocked tracer with span capabilities.
    """
    mock_span = MagicMock()
    mock_span.__enter__ = MagicMock(return_value=mock_span)
    mock_span.__exit__ = MagicMock(return_value=False)
    mock_span.set_attribute = MagicMock()
    mock_span.set_status = MagicMock()
    mock_span.record_exception = MagicMock()
    mock_span.is_recording = MagicMock(return_value=True)

    mock_tracer = MagicMock()
    mock_tracer.start_as_current_span.return_value = mock_span

    # Mock the span context manager in telemetry module
    with patch("specify_cli.core.telemetry._TRACER", mock_tracer), \
         patch("specify_cli.core.telemetry.OTEL_AVAILABLE", True):
        yield mock_tracer


# ============================================================================
# CLI Testing Fixtures (Typer)
# ============================================================================


@pytest.fixture
def cli_runner():
    """Create a Typer CLI test runner.

    Returns
    -------
    CliRunner
        Typer test runner for invoking commands.
    """
    from typer.testing import CliRunner

    return CliRunner()


@pytest.fixture
def cli_app():
    """Get the main CLI app for testing.

    Returns
    -------
    Typer
        The main specify CLI application.
    """
    from specify_cli.app import app

    return app


# ============================================================================
# Configuration Fixtures
# ============================================================================


@pytest.fixture
def mock_config_file(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a mock configuration file.

    Yields
    ------
    Path
        Path to mock config file.
    """
    config_dir = tmp_path / ".config" / "specify"
    config_dir.mkdir(parents=True)
    config_file = config_dir / "config.toml"

    config_content = """
[general]
default_ai_assistant = "claude"
default_script_type = "sh"

[telemetry]
enabled = true
endpoint = "http://localhost:4317"

[cache]
enabled = true
ttl_seconds = 3600
"""
    config_file.write_text(config_content)
    yield config_file


@pytest.fixture
def clean_env() -> Generator[None, None, None]:
    """Provide a clean environment without specify-related vars.

    Yields
    ------
    None
    """
    env_vars_to_remove = [
        "SPECIFY_OTEL_ENABLED",
        "SPECIFY_DRY",
        "SPECIFY_DEBUG",
        "SPECIFY_AI_ASSISTANT",
        "GITHUB_TOKEN",
    ]
    original_env = {k: os.environ.get(k) for k in env_vars_to_remove}

    for var in env_vars_to_remove:
        os.environ.pop(var, None)

    yield

    for var, value in original_env.items():
        if value is not None:
            os.environ[var] = value
        else:
            os.environ.pop(var, None)


# ============================================================================
# Data Fixtures
# ============================================================================


@pytest.fixture
def sample_tool_info() -> dict[str, Any]:
    """Sample tool information for testing.

    Returns
    -------
    dict
        Sample tool detection results.
    """
    return {
        "git": {"name": "git", "path": "/usr/bin/git", "version": "2.42.0", "required": True},
        "claude": {
            "name": "claude",
            "path": "/usr/local/bin/claude",
            "version": "1.0.0",
            "required": False,
        },
        "ggen": {"name": "ggen", "path": None, "version": None, "required": False},
    }


@pytest.fixture
def sample_version_info() -> dict[str, Any]:
    """Sample version information for testing.

    Returns
    -------
    dict
        Sample version check results.
    """
    return {
        "current_version": "0.0.25",
        "latest_version": "0.0.26",
        "update_available": True,
        "release_url": "https://github.com/github/spec-kit/releases/tag/v0.0.26",
    }
