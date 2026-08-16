"""Regression tests for the AGI ops/runtime module import surface.

Background
----------
Seven ``specify_cli`` modules imported ``timed`` from
:mod:`specify_cli.core.telemetry`, which never exported it -- the decorator is
defined in :mod:`specify_cli.core.shell`. Every one of those modules therefore
raised ``ImportError`` at import time, in production as well as under pytest.

These tests use the real modules, the real decorator and real state-based
assertions (no mocking of code this repository owns).
"""

from __future__ import annotations

import importlib

import pytest

AGI_MODULES = [
    "specify_cli.ops.agi_code_synthesizer",
    "specify_cli.ops.agi_orchestration",
    "specify_cli.ops.agi_reasoning",
    "specify_cli.ops.agi_task_planning",
    "specify_cli.runtime.agi_code_emission",
    "specify_cli.runtime.agi_orchestrator",
    "specify_cli.runtime.agi_task_executor",
]


@pytest.mark.parametrize("module_name", AGI_MODULES)
def test_agi_module_is_importable(module_name: str) -> None:
    """Each AGI module imports cleanly and exposes a real module object."""
    module = importlib.import_module(module_name)
    assert module.__name__ == module_name


def test_timed_is_exported_by_core_shell_not_core_telemetry() -> None:
    """``timed`` lives in core.shell; core.telemetry must not be its source."""
    from specify_cli.core import shell, telemetry

    assert callable(shell.timed)
    assert "timed" in shell.__all__
    assert not hasattr(telemetry, "timed")
    assert "timed" not in telemetry.__all__


@pytest.mark.parametrize("module_name", AGI_MODULES)
def test_agi_module_timed_is_the_core_shell_decorator(module_name: str) -> None:
    """The ``timed`` each module binds is the identical core.shell object."""
    from specify_cli.core.shell import timed as canonical_timed

    module = importlib.import_module(module_name)
    assert module.timed is canonical_timed


def test_timed_decorator_preserves_return_value_and_identity() -> None:
    """The real decorator runs the real function and returns its real result."""
    from specify_cli.core.shell import timed

    @timed
    def add(a: int, b: int) -> int:
        """Add two integers."""
        return a + b

    assert add(2, 3) == 5
    assert add.__name__ == "add"
    assert add.__doc__ == "Add two integers."


def test_timed_decorator_propagates_exceptions() -> None:
    """Failures inside the wrapped function surface unchanged to the caller."""
    from specify_cli.core.shell import timed

    @timed
    def boom() -> None:
        raise ValueError("expected failure")

    with pytest.raises(ValueError, match="expected failure"):
        boom()
