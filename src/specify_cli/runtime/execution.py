from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Callable, TypeVar

from specify_cli.core.shell import timed
from specify_cli.core.telemetry import metric_counter, span
from specify_cli.runtime.state import ExecutionState, get_state_store

T = TypeVar("T")


class ExecutionTracker:
    def __init__(self, phase: str):
        self.phase = phase
        self.execution_id = str(uuid.uuid4())[:8]
        self.store = get_state_store()
        self.state = ExecutionState(
            execution_id=self.execution_id,
            phase=phase,
            status="initialized",
            start_time=datetime.now().isoformat(),
        )

    def __enter__(self) -> ExecutionTracker:
        self.state.status = "running"
        self.state.start_time = datetime.now().isoformat()
        metric_counter("execution.started", 1, {"phase": self.phase})
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.state.end_time = datetime.now().isoformat()

        if exc_type is not None:
            self.state.status = "failed"
            self.state.errors.append(str(exc_val))
            metric_counter("execution.failed", 1, {"phase": self.phase})
        else:
            self.state.status = "completed"
            metric_counter("execution.completed", 1, {"phase": self.phase})

        start = datetime.fromisoformat(self.state.start_time)
        end = datetime.fromisoformat(self.state.end_time)
        self.state.duration = (end - start).total_seconds()

        self.store.save_execution(self.state)

    def set_input(self, data: dict[str, Any]) -> None:
        self.state.input_data.update(data)

    def set_output(self, data: dict[str, Any]) -> None:
        self.state.output_data.update(data)

    def add_error(self, error: str) -> None:
        self.state.errors.append(error)

    def set_metadata(self, key: str, value: Any) -> None:
        self.state.metadata[key] = value


@timed
def track_execution(phase: str) -> ExecutionTracker:
    return ExecutionTracker(phase)


def execute_with_tracking(
    phase: str,
    func: Callable[..., T],
    *args: Any,
    **kwargs: Any,
) -> T:
    with span(f"execution.tracked_{phase}"):
        tracker = track_execution(phase)
        tracker.set_input({"args": len(args), "kwargs": len(kwargs)})

        with tracker:
            try:
                result = func(*args, **kwargs)
                tracker.set_output({"success": True, "type": type(result).__name__})
                return result
            except Exception as e:
                tracker.add_error(str(e))
                raise


def get_execution_report(execution_id: str) -> dict[str, Any] | None:
    store = get_state_store()
    state = store.get_execution(execution_id)

    if not state:
        return None

    return {
        "execution_id": state.execution_id,
        "phase": state.phase,
        "status": state.status,
        "duration": state.duration,
        "start_time": state.start_time,
        "end_time": state.end_time,
        "input_count": len(state.input_data),
        "output_count": len(state.output_data),
        "error_count": len(state.errors),
        "errors": state.errors,
        "metadata_keys": list(state.metadata.keys()),
    }


def get_phase_report(phase: str) -> dict[str, Any]:
    store = get_state_store()
    executions = store.get_phase_executions(phase)

    total_count = len(executions)
    successful = sum(1 for e in executions if e.status == "completed")
    failed = sum(1 for e in executions if e.status == "failed")
    avg_duration = sum(e.duration for e in executions) / total_count if total_count > 0 else 0

    return {
        "phase": phase,
        "total_executions": total_count,
        "successful": successful,
        "failed": failed,
        "success_rate": successful / total_count if total_count > 0 else 0,
        "average_duration": avg_duration,
        "recent_executions": [
            {
                "id": e.execution_id,
                "status": e.status,
                "duration": e.duration,
                "errors": len(e.errors),
            }
            for e in executions[:10]
        ],
    }


def get_overall_report() -> dict[str, Any]:
    store = get_state_store()
    history = store.get_execution_history(limit=1000)

    phases = set(e.phase for e in history)
    total_executions = len(history)
    successful = sum(1 for e in history if e.status == "completed")
    failed = sum(1 for e in history if e.status == "failed")
    avg_duration = sum(e.duration for e in history) / total_executions if total_executions > 0 else 0

    return {
        "total_executions": total_executions,
        "successful": successful,
        "failed": failed,
        "success_rate": successful / total_executions if total_executions > 0 else 0,
        "average_duration": avg_duration,
        "phases_executed": list(phases),
        "phase_reports": {
            phase: get_phase_report(phase)
            for phase in phases
        },
    }
