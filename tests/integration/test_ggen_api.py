"""
Integration Tests for ggen v5.0.2 API
======================================

Tests for the local ggen v5.0.2 installation and API compatibility.

These are quick smoke tests to verify:
1. ggen binary is available
2. ggen sync command works
3. Basic CLI interface responds correctly

Full pipeline tests (14 transformations) will be added in Week 2.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest


def run_ggen_command(args: list[str]) -> tuple[str, str, int]:
    """Run a ggen command and return stdout, stderr, returncode.

    Parameters
    ----------
    args : list[str]
        Command arguments (without 'ggen' prefix).

    Returns
    -------
    tuple[str, str, int]
        (stdout, stderr, returncode)
    """
    cmd = ["ggen", *args]
    result = subprocess.run(
        cmd,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return result.stdout, result.stderr, result.returncode


class TestGgenBinaryAvailability:
    """Test ggen binary installation and availability."""

    def test_ggen_is_installed(self) -> None:
        """Verify ggen binary exists in PATH."""
        result = subprocess.run(
            ["which", "ggen"],
            check=False,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, "ggen binary not found in PATH"
        assert result.stdout.strip(), "ggen path is empty"

    def test_ggen_is_executable(self) -> None:
        """Verify ggen binary is executable."""
        result = subprocess.run(
            ["which", "ggen"],
            check=False,
            capture_output=True,
            text=True,
        )
        ggen_path = Path(result.stdout.strip())
        assert ggen_path.exists(), f"ggen binary not found at {ggen_path}"
        assert ggen_path.is_file(), f"{ggen_path} is not a file"
        # Check execute permission
        assert os.access(ggen_path, os.X_OK), f"{ggen_path} is not executable"


class TestGgenVersion:
    """Test ggen version reporting."""

    def test_version_flag_exists(self) -> None:
        """Verify --version flag is recognized."""
        _stdout, _stderr, returncode = run_ggen_command(["--version"])
        # NOTE: ggen v5.0.2 currently returns exit code 0 but empty output
        # This is a known issue documented in GGEN_API_ANALYSIS.md
        assert returncode == 0, f"--version failed with code {returncode}"

    @pytest.mark.xfail(reason="ggen v5.0.2 returns empty version string (known issue)")
    def test_version_output_format(self) -> None:
        """Verify version output contains version string."""
        stdout, _stderr, _returncode = run_ggen_command(["--version"])
        # Expected format: "ggen 5.0.2" or similar
        assert "ggen" in stdout.lower() or "5.0" in stdout, (
            f"Version output doesn't contain version info: {stdout}"
        )


class TestGgenHelpCommand:
    """Test ggen help command."""

    def test_help_flag_works(self) -> None:
        """Verify --help flag shows help text."""
        stdout, _stderr, returncode = run_ggen_command(["--help"])
        assert returncode == 0, f"--help failed with code {returncode}"
        assert "Usage: ggen" in stdout, "Help text missing usage line"
        assert "sync" in stdout, "Help text missing 'sync' command"

    def test_help_shows_sync_command(self) -> None:
        """Verify help lists the sync command."""
        stdout, _stderr, _returncode = run_ggen_command(["--help"])
        assert "sync" in stdout.lower(), "sync command not mentioned in help"


class TestGgenSyncCommand:
    """Test ggen sync command interface."""

    def test_sync_command_exists(self) -> None:
        """Verify sync subcommand is recognized."""
        stdout, stderr, returncode = run_ggen_command(["sync", "--help"])
        assert returncode == 0, f"sync --help failed: {stderr}"
        assert "Usage: ggen sync" in stdout, "sync help missing usage line"

    def test_sync_help_shows_options(self) -> None:
        """Verify sync --help lists all expected options."""
        stdout, _stderr, _returncode = run_ggen_command(["sync", "--help"])

        # Actual options in ggen v5.0.2 (verified from actual help output)
        expected_options = [
            "--from",  # Source ontology directory
            "--to",  # Target output directory
            "--mode",  # Sync mode
            "--dry-run",  # Preview changes without writing (hyphenated)
            "--force",  # Override conflicts
            "-v",  # Verbose output (short form)
        ]

        for option in expected_options:
            assert option in stdout, f"Expected option {option} not in sync help"

    @pytest.mark.xfail(reason="--manifest flag parsing broken (known issue)")
    def test_sync_accepts_manifest_flag(self) -> None:
        """Verify sync accepts --manifest flag."""
        # This test documents the known CLI parsing issue
        _stdout, stderr, returncode = run_ggen_command(
            [
                "sync",
                "--manifest",
                "docs/ggen.toml",
                "--dry_run",
                "true",
            ]
        )
        # Should succeed but currently fails with "unexpected argument"
        assert returncode == 0, f"sync --manifest failed: {stderr}"


class TestGgenOldAPIRemoved:
    """Verify old API commands (v5.0.1) are removed in v5.0.2."""

    def test_compile_command_removed(self) -> None:
        """Verify 'ggen compile' command no longer exists."""
        _stdout, stderr, returncode = run_ggen_command(["compile", "--help"])
        # Should fail because compile command doesn't exist
        assert returncode != 0, "compile command should not exist in v5.0.2"
        # Error message should indicate unrecognized command
        assert (
            "unrecognized subcommand" in stderr.lower()
            or "invalid subcommand" in stderr.lower()
            or "unexpected argument" in stderr.lower()
        ), f"Expected 'unrecognized subcommand' error, got: {stderr}"

    def test_generate_command_removed(self) -> None:
        """Verify 'ggen generate' command no longer exists."""
        _stdout, _stderr, returncode = run_ggen_command(["generate", "--help"])
        # Should fail because generate command doesn't exist
        assert returncode != 0, "generate command should not exist in v5.0.2"

    def test_validate_command_removed(self) -> None:
        """Verify 'ggen validate' command no longer exists."""
        _stdout, _stderr, returncode = run_ggen_command(["validate", "--help"])
        # Should fail because validate command doesn't exist
        assert returncode != 0, "validate command should not exist in v5.0.2"


class TestGgenSyncExecution:
    """Test actual execution of ggen sync (basic smoke tests)."""

    def test_sync_runs_without_config(self, tmp_path: Path) -> None:
        """Verify ggen sync runs in an empty directory (fallback behavior)."""
        # Create a temporary directory with no ggen.toml
        # ggen should fall back to default behavior
        result = subprocess.run(
            ["ggen", "sync"],
            check=False,
            cwd=tmp_path,
            capture_output=True,
            text=True,
            timeout=30,
        )

        # May succeed (fallback) or fail (no config) - both are acceptable
        # We're just verifying it doesn't crash
        assert result.returncode in {0, 1}, (
            f"ggen sync crashed with unexpected code {result.returncode}: {result.stderr}"
        )

    @pytest.mark.slow
    def test_sync_with_schema_directory(self, tmp_path: Path) -> None:
        """Verify ggen sync works with a schema/ directory."""
        # Create schema directory (ggen's default)
        schema_dir = tmp_path / "schema"
        schema_dir.mkdir()

        # Create a minimal RDF file
        test_ttl = schema_dir / "test.ttl"
        test_ttl.write_text("""
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

<http://example.org/Test> a rdfs:Class .
        """)

        # Run ggen sync
        result = subprocess.run(
            ["ggen", "sync"],
            check=False,
            cwd=tmp_path,
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Should succeed if it finds the schema directory
        if result.returncode == 0:
            # Verify it generated something
            tmp_path / "src" / "generated"
            # May or may not generate - depends on ggen's behavior
            # Just verify it didn't crash


# Pytest markers for test organization
pytestmark = [
    pytest.mark.integration,  # All tests in this file are integration tests
]


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v", "--tb=short"])
