"""
specify_cli.ops.ggen_filelock - File Locking for Concurrent Access
==================================================================

File locking mechanism to prevent concurrent ggen sync operations.

Implements Phase 1 critical fix: file locking to prevent concurrent
access corruption (RPN 288). Uses lock files with process IDs for
debugging.

Key Features:
- Simple lock file mechanism
- PID-based ownership for debugging
- Timeout support
- Safe cleanup
- Cross-platform (uses tempfile for atomicity)

Examples:
    >>> from specify_cli.ops.ggen_filelock import FileLock
    >>> lock = FileLock(".ggen.lock", timeout=30)
    >>> lock.acquire()
    >>> try:
    ...     # Do work
    ... finally:
    ...     lock.release()

    >>> # Or use as context manager
    >>> with FileLock(".ggen.lock", timeout=30):
    ...     # Work here, auto-released

See Also:
    - specify_cli.ops.ggen_atomic : Atomic writes
    - docs/GGEN_SYNC_POKA_YOKE.md : Error-proofing design

Notes:
    Uses simple file-based locking. PID stored for debugging
    (to identify which process holds lock).
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

__all__ = [
    "FileLock",
    "LockTimeoutError",
]


class LockTimeoutError(Exception):
    """Raised when lock acquisition times out."""

    def __init__(self, lock_file: str, timeout: float, owner_pid: int | None = None) -> None:
        """Initialize timeout error.

        Parameters
        ----------
        lock_file : str
            Path to lock file.
        timeout : float
            Timeout in seconds.
        owner_pid : int | None
            PID of process holding lock (if available).
        """
        owner_msg = f" (held by PID {owner_pid})" if owner_pid else ""
        super().__init__(
            f"Could not acquire lock on {lock_file} within {timeout}s{owner_msg}"
        )
        self.lock_file = lock_file
        self.timeout = timeout
        self.owner_pid = owner_pid


class FileLock:
    """Simple file-based lock.

    Uses lock file to serialize access. PID is stored in lock file
    for debugging concurrent access issues.

    Parameters
    ----------
    lock_file : str | Path
        Path to lock file.
    timeout : float
        Timeout in seconds (0 = no timeout).
    """

    def __init__(self, lock_file: str | Path, timeout: float = 30) -> None:
        """Initialize file lock.

        Parameters
        ----------
        lock_file : str | Path
            Path to lock file.
        timeout : float
            Timeout in seconds (0 = no timeout).
        """
        self.lock_file = Path(lock_file)
        self.timeout = timeout
        self.acquired = False

    def acquire(self) -> None:
        """Acquire lock, blocking until available or timeout.

        Raises
        ------
        LockTimeoutError
            If lock cannot be acquired within timeout.
        """
        start_time = time.time()
        poll_interval = 0.1

        while True:
            try:
                # Try to create lock file (atomic on most systems)
                # Using O_EXCL for atomicity
                fd = os.open(
                    str(self.lock_file),
                    os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                    0o644,
                )
                # Write current PID for debugging
                os.write(fd, str(os.getpid()).encode())
                os.close(fd)

                self.acquired = True
                return

            except FileExistsError:
                # Lock already held
                elapsed = time.time() - start_time

                if self.timeout > 0 and elapsed > self.timeout:
                    # Try to read owner PID for error message
                    owner_pid = None
                    try:
                        if self.lock_file.exists():
                            content = self.lock_file.read_text()
                            owner_pid = int(content.strip())
                    except (ValueError, OSError):
                        pass

                    raise LockTimeoutError(str(self.lock_file), self.timeout, owner_pid)

                # Wait a bit before retrying
                time.sleep(poll_interval)

    def release(self) -> None:
        """Release lock.

        Safe to call even if lock not held.
        """
        if self.lock_file.exists():
            try:
                self.lock_file.unlink()
                self.acquired = False
            except OSError:
                # Best effort - ignore errors on cleanup
                pass

    def __enter__(self) -> FileLock:
        """Context manager entry."""
        self.acquire()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """Context manager exit.

        Parameters
        ----------
        exc_type : type[BaseException] | None
            Exception type.
        exc_val : BaseException | None
            Exception value.
        exc_tb : Any
            Traceback.
        """
        self.release()

    def __del__(self) -> None:
        """Ensure lock is released on garbage collection."""
        if self.acquired:
            self.release()
