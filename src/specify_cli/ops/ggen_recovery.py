"""
specify_cli.ops.ggen_recovery - Error Recovery and Cleanup
========================================================

Error recovery procedures for ggen sync operations.

Implements Phase 1 critical fix: error recovery to enable safe recovery
from failures (RPN 400). Automatic cleanup on failures and recovery
instructions for operators.

Key Features:
- Record sync attempts for debugging
- Automatic cleanup on failure
- Recovery instructions for operators
- Transaction status tracking

Examples:
    >>> from specify_cli.ops.ggen_recovery import RecoveryManager
    >>> recovery = RecoveryManager(\"output/\")
    >>> recovery.record_attempt(manifest)
    >>> try:
    ...     # Sync operations
    ... except Exception as e:
    ...     recovery.handle_failure(e)

See Also:
    - specify_cli.ops.ggen_atomic : Atomic writes
    - specify_cli.ops.ggen_filelock : File locking
    - docs/GGEN_SYNC_OPERATIONAL_RUNBOOKS.md : Recovery procedures

Notes:
    Enables safe recovery from failures. Tracks what was attempted
    for debugging. Provides instructions for manual recovery.
"""

from __future__ import annotations

import json
import shutil
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path

__all__ = [
    "RecoveryManager",
    "SyncAttempt",
]


@dataclass
class SyncAttempt:
    """Record of a sync attempt.

    Attributes
    ----------
    timestamp : str
        ISO format timestamp.
    status : str
        "in_progress", "success", or "failed".
    transformations : list[str]
        Names of transformations attempted.
    error : str | None
        Error message if failed.
    output_dir : str
        Target output directory.
    recovery_steps : list[str]
        Instructions for recovery if failed.
    """

    timestamp: str
    status: str
    transformations: list[str]
    output_dir: str
    error: str | None = None
    recovery_steps: list[str] = field(default_factory=list)


class RecoveryManager:
    """Manage error recovery and cleanup.

    Parameters
    ----------
    output_dir : str | Path
        Output directory for sync.
    """

    def __init__(self, output_dir: str | Path) -> None:
        """Initialize recovery manager.

        Parameters
        ----------
        output_dir : str | Path
            Target output directory.
        """
        self.output_dir = Path(output_dir)
        self.metadata_dir = self.output_dir / ".ggen-recovery"
        self.metadata_dir.mkdir(parents=True, exist_ok=True)

        self.attempt: SyncAttempt | None = None

    def record_attempt(self, transformation_names: list[str]) -> None:
        """Record start of sync attempt.

        Parameters
        ----------
        transformation_names : list[str]
            Names of transformations being attempted.
        """
        self.attempt = SyncAttempt(
            timestamp=datetime.now(tz=UTC).isoformat(),
            status="in_progress",
            transformations=transformation_names,
            output_dir=str(self.output_dir),
        )

        # Save attempt record
        attempt_file = self.metadata_dir / "current-attempt.json"
        attempt_file.write_text(json.dumps(asdict(self.attempt), indent=2))

    def record_success(self) -> None:
        """Record successful completion of sync."""
        if self.attempt:
            self.attempt.status = "success"

            # Save success record
            success_file = (
                self.metadata_dir / f"success-{self.attempt.timestamp}.json"
            )
            success_file.write_text(json.dumps(asdict(self.attempt), indent=2))

            # Clean up current attempt
            current_file = self.metadata_dir / "current-attempt.json"
            if current_file.exists():
                current_file.unlink()

    def handle_failure(self, error: Exception) -> list[str]:
        """Handle failure and generate recovery instructions.

        Parameters
        ----------
        error : Exception
            Exception that occurred.

        Returns
        -------
        list[str]
            Recovery instructions for operator.
        """
        if not self.attempt:
            return []

        self.attempt.status = "failed"
        self.attempt.error = str(error)

        # Generate recovery steps based on error type
        recovery_steps = _generate_recovery_steps(str(error), self.output_dir)
        self.attempt.recovery_steps = recovery_steps

        # Save failed attempt
        failed_file = (
            self.metadata_dir / f"failed-{self.attempt.timestamp}.json"
        )
        failed_file.write_text(json.dumps(asdict(self.attempt), indent=2))

        # Save as current for investigation
        current_file = self.metadata_dir / "current-attempt.json"
        current_file.write_text(json.dumps(asdict(self.attempt), indent=2))

        return recovery_steps

    def cleanup(self) -> None:
        """Clean up temporary files.

        Removes staging directories and temporary files.
        """
        # Remove staging directory
        staging_dir = self.output_dir / ".ggen-staging"
        if staging_dir.exists():
            shutil.rmtree(staging_dir)

        # Remove lock file
        lock_file = self.output_dir / ".ggen.lock"
        if lock_file.exists():
            lock_file.unlink()


def _generate_recovery_steps(error_msg: str, output_dir: Path) -> list[str]:
    """Generate recovery instructions based on error.

    Parameters
    ----------
    error_msg : str
        Error message.
    output_dir : Path
        Output directory.

    Returns
    -------
    list[str]
        Recovery instructions.
    """
    steps: list[str] = []

    error_lower = error_msg.lower()

    if "permission" in error_lower or "access denied" in error_lower:
        steps.extend([
            "1. Check output directory permissions: chmod 755 " + str(output_dir),
            "2. Verify user ownership: chown $USER " + str(output_dir),
            "3. Retry sync operation",
        ])

    elif "disk" in error_lower or "space" in error_lower:
        steps.extend([
            "1. Check available disk space: df -h " + str(output_dir),
            "2. Clean up old files or expand disk",
            "3. Retry sync operation",
        ])

    elif "timeout" in error_lower:
        steps.extend([
            "1. Review SPARQL query complexity",
            "2. Break query into smaller parts if possible",
            "3. Increase timeout in configuration",
            "4. Retry sync operation",
        ])

    elif "manifest" in error_lower or "config" in error_lower:
        steps.extend([
            "1. Check ggen.toml syntax: ggen validate ggen.toml",
            "2. Verify all referenced files exist",
            "3. Review manifest for errors",
            "4. Retry sync operation",
        ])

    else:
        steps.extend([
            "1. Review error message above",
            "2. Check ggen.toml configuration",
            "3. Verify all input files exist and are readable",
            "4. Check output directory permissions",
            "5. Review debug logs in " + str(output_dir / ".ggen-recovery"),
            "6. Retry sync operation",
        ])

    # Common cleanup step
    steps.append(f"\n7. Manual cleanup if needed: rm -rf {output_dir}/.ggen-staging")

    return steps
