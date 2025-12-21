"""
Integration tests for specify_cli.runtime.git module.

Tests cover git operations with real subprocess calls where possible.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from specify_cli.runtime.git import commit, init_repo, is_repo


class TestIsRepo:
    """Tests for is_repo() function."""

    def test_is_repo_true(self, tmp_path: Path) -> None:
        """Test is_repo returns True for git repository."""
        # Initialize a git repo
        subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)

        result = is_repo(tmp_path)

        assert result is True

    def test_is_repo_false(self, tmp_path: Path) -> None:
        """Test is_repo returns False for non-git directory."""
        result = is_repo(tmp_path)

        assert result is False

    def test_is_repo_nonexistent_dir(self, tmp_path: Path) -> None:
        """Test is_repo returns False for nonexistent directory."""
        nonexistent = tmp_path / "nonexistent"

        result = is_repo(nonexistent)

        assert result is False


class TestInitRepo:
    """Tests for init_repo() function."""

    @pytest.mark.requires_git
    def test_init_repo_creates_git_dir(self, tmp_path: Path) -> None:
        """Test init_repo creates .git directory."""
        project_dir = tmp_path / "test-project"
        project_dir.mkdir()

        init_repo(project_dir)

        assert (project_dir / ".git").exists()
        assert (project_dir / ".git").is_dir()

    @pytest.mark.requires_git
    def test_init_repo_is_valid_repo(self, tmp_path: Path) -> None:
        """Test init_repo creates valid git repository."""
        project_dir = tmp_path / "test-project"
        project_dir.mkdir()

        init_repo(project_dir)

        # Verify it's a valid repo
        result = subprocess.run(
            ["git", "status"],
            check=False, cwd=project_dir,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

    @pytest.mark.requires_git
    def test_init_repo_existing_repo(self, tmp_path: Path) -> None:
        """Test init_repo on existing repo doesn't fail."""
        project_dir = tmp_path / "test-project"
        project_dir.mkdir()

        # Initialize twice
        init_repo(project_dir)
        init_repo(project_dir)  # Should not raise

        assert (project_dir / ".git").exists()

    def test_init_repo_dry_run(self, tmp_path: Path) -> None:
        """Test init_repo in dry run mode."""
        project_dir = tmp_path / "test-project"
        project_dir.mkdir()

        with patch.dict("os.environ", {"SPECIFY_DRY": "1"}):
            init_repo(project_dir)

        # .git should not exist in dry run
        assert not (project_dir / ".git").exists()


class TestCommit:
    """Tests for commit() function."""

    @pytest.fixture
    def git_repo(self, tmp_path: Path) -> Path:
        """Create a git repository with initial setup."""
        repo = tmp_path / "test-repo"
        repo.mkdir()

        # Initialize repo
        subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)

        # Configure git user for commits
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=repo,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=repo,
            check=True,
            capture_output=True,
        )

        return repo

    @pytest.mark.requires_git
    def test_commit_with_message(self, git_repo: Path) -> None:
        """Test commit with message."""
        # Create a file to commit
        test_file = git_repo / "test.txt"
        test_file.write_text("Hello, World!")

        # Stage the file
        subprocess.run(["git", "add", "."], cwd=git_repo, check=True)

        # Commit
        commit(git_repo, "Initial commit")

        # Verify commit exists
        result = subprocess.run(
            ["git", "log", "--oneline", "-1"],
            check=False, cwd=git_repo,
            capture_output=True,
            text=True,
        )
        assert "Initial commit" in result.stdout

    @pytest.mark.requires_git
    def test_commit_nothing_to_commit(self, git_repo: Path) -> None:
        """Test commit when nothing to commit."""
        # No files added, should handle gracefully with allow_empty
        commit(git_repo, "Empty commit", allow_empty=True)

        # Verify empty commit was created
        result = subprocess.run(
            ["git", "log", "--oneline", "-1"],
            check=False, cwd=git_repo,
            capture_output=True,
            text=True,
        )
        assert "Empty commit" in result.stdout

    def test_commit_dry_run(self, git_repo: Path) -> None:
        """Test commit in dry run mode."""
        test_file = git_repo / "test.txt"
        test_file.write_text("Hello, World!")
        subprocess.run(["git", "add", "."], cwd=git_repo, check=True)

        with patch.dict("os.environ", {"SPECIFY_DRY": "1"}):
            commit(git_repo, "Dry run commit")

        # Verify no commit was made
        result = subprocess.run(
            ["git", "log", "--oneline"],
            check=False, cwd=git_repo,
            capture_output=True,
            text=True,
        )
        assert "Dry run commit" not in result.stdout


class TestOtelIntegration:
    """Tests for OpenTelemetry integration in git module."""

    def test_init_repo_works_with_otel(
        self, tmp_path: Path
    ) -> None:
        """Test init_repo works with OTEL (no-op mode by default)."""
        project_dir = tmp_path / "test-project"
        project_dir.mkdir()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            # Should execute without error, OTEL uses no-op tracer when not configured
            init_repo(project_dir)

        # Verify subprocess was called (git init)
        mock_run.assert_called()

    def test_is_repo_works_with_otel(
        self, tmp_path: Path
    ) -> None:
        """Test is_repo works with OTEL (no-op mode by default)."""
        # Should execute without error, OTEL uses no-op tracer when not configured
        result = is_repo(tmp_path)

        # Should return False for non-repo directory
        assert isinstance(result, bool)
