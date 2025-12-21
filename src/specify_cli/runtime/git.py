"""
specify_cli.runtime.git - Git Operations
=========================================

Runtime layer for Git repository operations.

This module isolates all Git subprocess calls with comprehensive
OpenTelemetry instrumentation. Uses list-based commands only
for security (no shell=True).

Key Features
-----------
* **Repository Detection**: Check if path is a git repository
* **Repository Initialization**: Initialize new repositories
* **Initial Commit**: Create initial commit from template
* **Telemetry**: Full OTEL instrumentation

Security
--------
* List-based subprocess calls only (no shell=True)
* Path validation before operations
* No command injection vulnerabilities

Examples
--------
    >>> from specify_cli.runtime.git import is_repo, init_repo
    >>>
    >>> if not is_repo(project_path):
    ...     init_repo(project_path, commit_message="Initial commit")

See Also
--------
- :mod:`specify_cli.core.process` : Process execution utilities
- :mod:`specify_cli.core.telemetry` : Telemetry utilities
"""

from __future__ import annotations

import time
from pathlib import Path

from specify_cli.core.instrumentation import add_span_attributes, add_span_event
from specify_cli.core.process import run
from specify_cli.core.telemetry import metric_counter, metric_histogram, span

__all__ = [
    "is_repo",
    "init_repo",
    "add_all",
    "commit",
    "get_current_branch",
    "GitError",
]


class GitError(Exception):
    """Git operation error."""

    def __init__(self, message: str, command: list[str] | None = None) -> None:
        super().__init__(message)
        self.command = command


def is_repo(path: Path | None = None) -> bool:
    """Check if the specified path is inside a git repository.

    Parameters
    ----------
    path : Path, optional
        Path to check. Defaults to current working directory.

    Returns
    -------
    bool
        True if path is inside a git repository.
    """
    if path is None:
        path = Path.cwd()

    if not path.is_dir():
        return False

    with span("git.is_repo", path=str(path)):
        try:
            run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                capture=True,
                check=True,
                cwd=path,
            )
            metric_counter("git.is_repo.true")(1)
            add_span_attributes(is_repo=True)
            return True
        except Exception:
            metric_counter("git.is_repo.false")(1)
            add_span_attributes(is_repo=False)
            return False


def init_repo(
    path: Path,
    *,
    initial_branch: str = "main",
    commit_message: str = "Initial commit from Specify template",
    add_all: bool = True,
    create_commit: bool = True,
) -> bool:
    """Initialize a git repository in the specified path.

    Parameters
    ----------
    path : Path
        Path to initialize git repository in.
    initial_branch : str, optional
        Name for the initial branch. Default is "main".
    commit_message : str, optional
        Message for initial commit.
    add_all : bool, optional
        Whether to add all files. Default is True.
    create_commit : bool, optional
        Whether to create initial commit. Default is True.

    Returns
    -------
    bool
        True if initialization succeeded.

    Raises
    ------
    GitError
        If git initialization fails.
    """
    start_time = time.time()

    with span(
        "git.init_repo",
        path=str(path),
        initial_branch=initial_branch,
    ):
        add_span_event("git.init.starting", {"path": str(path)})

        try:
            # Initialize repository
            run(
                ["git", "init", "-b", initial_branch],
                capture=True,
                check=True,
                cwd=path,
            )
            add_span_event("git.init.completed", {"branch": initial_branch})

            if add_all:
                # Add all files
                run(
                    ["git", "add", "."],
                    capture=True,
                    check=True,
                    cwd=path,
                )
                add_span_event("git.add.completed", {})

            if create_commit:
                # Create initial commit (allow empty if no files)
                run(
                    ["git", "commit", "--allow-empty", "-m", commit_message],
                    capture=True,
                    check=True,
                    cwd=path,
                )
                add_span_event("git.commit.completed", {"message": commit_message})

            duration = time.time() - start_time

            # Record metrics
            metric_counter("git.init.success")(1)
            metric_histogram("git.init.duration")(duration)

            add_span_attributes(
                success=True,
                duration=duration,
            )

            return True

        except Exception as e:
            duration = time.time() - start_time

            metric_counter("git.init.error")(1)
            metric_histogram("git.init.duration")(duration)

            add_span_event(
                "git.init.failed",
                {
                    "error": str(e),
                    "duration": duration,
                },
            )

            raise GitError(f"Failed to initialize git repository: {e}") from e


def add_all(path: Path) -> None:
    """Add all files to git staging.

    Parameters
    ----------
    path : Path
        Repository path.

    Raises
    ------
    GitError
        If git add fails.
    """
    with span("git.add", path=str(path)):
        try:
            run(
                ["git", "add", "."],
                capture=True,
                check=True,
                cwd=path,
            )
            metric_counter("git.add.success")(1)
        except Exception as e:
            metric_counter("git.add.error")(1)
            raise GitError(f"Failed to add files: {e}") from e


def commit(path: Path, message: str, *, allow_empty: bool = False) -> None:
    """Create a git commit.

    Parameters
    ----------
    path : Path
        Repository path.
    message : str
        Commit message.
    allow_empty : bool, optional
        Allow empty commits. Default is False.

    Raises
    ------
    GitError
        If git commit fails.
    """
    with span("git.commit", path=str(path), message=message):
        try:
            cmd = ["git", "commit", "-m", message]
            if allow_empty:
                cmd.insert(2, "--allow-empty")
            run(
                cmd,
                capture=True,
                check=True,
                cwd=path,
            )
            metric_counter("git.commit.success")(1)
        except Exception as e:
            metric_counter("git.commit.error")(1)
            raise GitError(f"Failed to commit: {e}") from e


def get_current_branch(path: Path | None = None) -> str | None:
    """Get the current git branch name.

    Parameters
    ----------
    path : Path, optional
        Repository path. Defaults to current directory.

    Returns
    -------
    str | None
        Branch name or None if not in a repo or detached HEAD.
    """
    if path is None:
        path = Path.cwd()

    with span("git.current_branch", path=str(path)):
        try:
            result = run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture=True,
                check=True,
                cwd=path,
            )
            branch = result.strip() if result else None
            add_span_attributes(branch=branch or "")
            return branch
        except Exception:
            return None
