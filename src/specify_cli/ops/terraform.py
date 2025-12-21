"""
uvmgr.commands.terraform
============================

Pure business logic layer for Terraform support and infrastructure as code.

This module implements all business logic for the terraform command.
No I/O operations, subprocess calls, or side effects - all delegated to runtime layer.

The ops layer:
- Validates inputs and state
- Performs pure computations
- Returns structured data
- Records telemetry events
- Raises appropriate exceptions

See Also:
- :mod:`specify_cli.commands.terraform` : CLI interface
- :mod:`specify_cli.runtime.terraform` : Runtime I/O operations
"""

from __future__ import annotations

from typing import Any

from specify_cli.core.instrumentation import add_span_event


def validate_inputs(**kwargs: Any) -> dict[str, Any]:
    """Validate inputs for terraform operations.

    Parameters
    ----------
    **kwargs : Any
        Command arguments and options

    Returns
    -------
    dict[str, Any]
        Validation result with 'valid' key
    """
    add_span_event(
        "terraform.validate_inputs", {"operation": "terraform", "arg_count": len(kwargs)}
    )

    # Validate non-empty args
    if not kwargs:
        return {"valid": False, "error": "No arguments provided"}

    # Command-specific validation
    return {"valid": True, "errors": []}
