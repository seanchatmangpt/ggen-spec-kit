"""
Integration Tests for ggen Runtime Operations
==============================================

Comprehensive integration tests for the specify_cli.runtime.ggen module (ggen v5.0.2).

Tests verify:
1. ggen availability detection
2. ggen version checking
3. spec synchronization (ggen sync)
4. Error handling
5. Telemetry integration

Note: ggen v5.0.2 only has sync command. compile_ontology and generate_code
were part of v5.0.1 API and have been removed.

Test Strategy
-------------
- Uses real ggen v5.0.2 binary when available
- Mocks subprocess calls for unit-like isolation when needed
- Uses temporary directories for file operations
- 100% type hints and comprehensive docstrings
- Minimum 80% coverage target

Author: Claude Code
Date: 2025-12-20
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from unittest.mock import Mock, patch

import pytest

from specify_cli.runtime.ggen import (
    GgenError,
    get_ggen_version,
    is_ggen_available,
    sync_specs,
)

# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def temp_project_dir() -> Any:
    """
    Create a temporary project directory for testing.

    Yields
    ------
    Path
        Temporary project directory path.
    """
    with TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_ttl_content() -> str:
    """
    Generate sample TTL content for testing.

    Returns
    -------
    str
        Valid RDF/Turtle content.
    """
    return """
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix sk: <http://spec-kit.io/ontology#> .

sk:TestFeature a sk:Feature ;
    rdfs:label "Test Feature" ;
    sk:priority "P1" ;
    sk:status "active" .
"""


# ============================================================================
# Test: ggen Availability and Version Detection
# ============================================================================


@pytest.mark.integration
def test_is_ggen_available_when_installed() -> None:
    """
    Test is_ggen_available() returns True when ggen is installed.

    Verifies that the function correctly detects ggen installation.
    """
    # This test relies on real ggen being installed
    result = is_ggen_available()

    # Check result type
    assert isinstance(result, bool)

    # If ggen is installed, verify it's detected
    if result:
        version = get_ggen_version()
        assert version is not None


@pytest.mark.integration
def test_is_ggen_available_when_missing() -> None:
    """
    Test is_ggen_available() returns False when ggen is not installed.

    Mocks the which command to simulate missing ggen.
    """
    with patch("specify_cli.runtime.ggen.check_tool") as mock_check:
        mock_check.return_value = False

        result = is_ggen_available()

        assert result is False
        mock_check.assert_called_once_with("ggen")


@pytest.mark.integration
def test_get_ggen_version_when_installed() -> None:
    """
    Test get_ggen_version() returns version string when ggen is installed.

    Verifies version string format and content.
    """
    # Mock successful version check
    with (
        patch("specify_cli.runtime.ggen.is_ggen_available") as mock_available,
        patch("specify_cli.runtime.ggen.run") as mock_run,
    ):
        mock_available.return_value = True
        mock_run.return_value = "ggen 5.0.2"

        version = get_ggen_version()

        assert version is not None
        assert isinstance(version, str)
        assert len(version) > 0
        mock_run.assert_called_once()


@pytest.mark.integration
def test_get_ggen_version_when_missing() -> None:
    """
    Test get_ggen_version() returns None when ggen is not installed.

    Verifies graceful handling of missing ggen binary.
    """
    with patch("specify_cli.runtime.ggen.is_ggen_available") as mock_available:
        mock_available.return_value = False

        version = get_ggen_version()

        assert version is None


# ============================================================================
# Test: Spec Synchronization
# ============================================================================


@pytest.mark.integration
def test_sync_specs_basic_execution(temp_project_dir: Path) -> None:
    """
    Test sync_specs() executes ggen sync command.

    Parameters
    ----------
    temp_project_dir : Path
        Temporary directory for test project.
    """
    with (
        patch("specify_cli.runtime.ggen.is_ggen_available") as mock_available,
        patch("specify_cli.runtime.ggen.run") as mock_run,
    ):
        mock_available.return_value = True
        mock_run.return_value = ""

        result = sync_specs(temp_project_dir)

        assert result is True
        mock_run.assert_called_once()

        # Verify command structure
        call_args = mock_run.call_args
        cmd = call_args[0][0]
        assert cmd[0] == "ggen"
        assert cmd[1] == "sync"


@pytest.mark.integration
def test_sync_specs_with_watch(temp_project_dir: Path) -> None:
    """
    Test sync_specs() with watch mode enabled.

    Parameters
    ----------
    temp_project_dir : Path
        Temporary directory for test project.
    """
    with (
        patch("specify_cli.runtime.ggen.is_ggen_available") as mock_available,
        patch("specify_cli.runtime.ggen.run") as mock_run,
    ):
        mock_available.return_value = True
        mock_run.return_value = ""

        result = sync_specs(temp_project_dir, watch=True)

        assert result is True

        # Verify --watch flag
        call_args = mock_run.call_args
        cmd = call_args[0][0]
        assert "--watch" in cmd


@pytest.mark.integration
def test_sync_specs_with_verbose(temp_project_dir: Path) -> None:
    """
    Test sync_specs() with verbose mode enabled.

    Parameters
    ----------
    temp_project_dir : Path
        Temporary directory for test project.
    """
    with (
        patch("specify_cli.runtime.ggen.is_ggen_available") as mock_available,
        patch("specify_cli.runtime.ggen.run") as mock_run,
    ):
        mock_available.return_value = True
        mock_run.return_value = ""

        result = sync_specs(temp_project_dir, verbose=True)

        assert result is True

        # Verify --verbose flag
        call_args = mock_run.call_args
        cmd = call_args[0][0]
        assert "--verbose" in cmd


@pytest.mark.integration
def test_sync_specs_missing_ggen(temp_project_dir: Path) -> None:
    """
    Test sync_specs() raises GgenError when ggen is missing.

    Parameters
    ----------
    temp_project_dir : Path
        Temporary directory for test project.
    """
    with patch("specify_cli.runtime.ggen.is_ggen_available") as mock_available:
        mock_available.return_value = False

        with pytest.raises(GgenError) as exc_info:
            sync_specs(temp_project_dir)

        assert "not installed" in str(exc_info.value)


@pytest.mark.integration
def test_sync_specs_error_handling(temp_project_dir: Path) -> None:
    """
    Test sync_specs() handles sync errors.

    Parameters
    ----------
    temp_project_dir : Path
        Temporary directory for test project.
    """
    with (
        patch("specify_cli.runtime.ggen.is_ggen_available") as mock_available,
        patch("specify_cli.runtime.ggen.run") as mock_run,
    ):
        mock_available.return_value = True
        mock_run.side_effect = subprocess.CalledProcessError(1, ["ggen"], "Sync failed")

        with pytest.raises(GgenError) as exc_info:
            sync_specs(temp_project_dir)

        assert "sync failed" in str(exc_info.value).lower()


# ============================================================================
# Test: GgenError Exception
# ============================================================================


@pytest.mark.integration
def test_ggen_error_basic() -> None:
    """Test GgenError exception basic functionality."""
    error = GgenError("Test error")

    assert str(error) == "Test error"
    assert error.command is None


@pytest.mark.integration
def test_ggen_error_with_command() -> None:
    """Test GgenError exception with command information."""
    cmd = ["ggen", "sync", "--verbose"]
    error = GgenError("Test error", command=cmd)

    assert str(error) == "Test error"
    assert error.command == cmd


# ============================================================================
# Telemetry and Metrics Tests
# ============================================================================


@pytest.mark.integration
def test_sync_specs_telemetry(temp_project_dir: Path) -> None:
    """
    Test sync_specs() generates telemetry spans.

    Parameters
    ----------
    temp_project_dir : Path
        Temporary directory for test project.
    """
    with (
        patch("specify_cli.runtime.ggen.is_ggen_available") as mock_available,
        patch("specify_cli.runtime.ggen.run") as mock_run,
        patch("specify_cli.runtime.ggen.span") as mock_span,
    ):
        mock_available.return_value = True
        mock_run.return_value = ""

        # Setup mock context manager
        mock_span.return_value.__enter__ = Mock()
        mock_span.return_value.__exit__ = Mock(return_value=False)

        sync_specs(temp_project_dir)

        # Verify span was created
        mock_span.assert_called_once()
        call_args = mock_span.call_args
        assert call_args[0][0] == "ggen.sync"


# ============================================================================
# Run Tests Directly
# ============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])
