"""
specify_cli.core.dod_types
==========================

Shared types for Definition of Done checking.

This module defines the data structures used by the DoD checking system
to avoid circular imports between ops and runtime layers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "DoDCheckResult",
    "DoDGate",
]


@dataclass
class DoDGate:
    """Result of a single Definition of Done gate/criterion."""

    name: str
    category: str
    passed: bool
    details: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


@dataclass
class DoDCheckResult:
    """Result of complete Definition of Done check."""

    success: bool
    total_gates: int = 0
    passed_gates: int = 0
    failed_gates: list[DoDGate] = field(default_factory=list)
    gates: list[DoDGate] = field(default_factory=list)
    duration: float = 0.0
    strict_mode: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert result to dictionary.

        Returns
        -------
        dict[str, Any]
            Dictionary representation of result.
        """
        return {
            "success": self.success,
            "total": self.total_gates,
            "completed": self.passed_gates,
            "failed": len(self.failed_gates),
            "duration": self.duration,
            "strict": self.strict_mode,
            "gates": [
                {
                    "name": g.name,
                    "category": g.category,
                    "passed": g.passed,
                    "details": g.details,
                    "error": g.error,
                }
                for g in self.gates
            ],
        }
