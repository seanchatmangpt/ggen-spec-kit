from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from specify_cli.core.shell import timed
from specify_cli.core.telemetry import metric_counter, span
from specify_cli.runtime.execution import track_execution
from specify_cli.runtime.integration import (
    execute_full_stack_integration,
    execute_reasoning_and_deployment,
    execute_observability_and_analytics,
)


@dataclass
class ExecutionContext:
    input_file: str | None = None
    artifact_file: str | None = None
    data_file: str | None = None
    config: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


class SpecifyCoordinator:
    def __init__(self):
        self.context = ExecutionContext()
        self._execution_history = []

    def set_context(self, context: ExecutionContext) -> None:
        self.context = context

    def set_input_file(self, path: str | Path) -> SpecifyCoordinator:
        self.context.input_file = str(path)
        return self

    def set_artifact_file(self, path: str | Path) -> SpecifyCoordinator:
        self.context.artifact_file = str(path)
        return self

    def set_data_file(self, path: str | Path) -> SpecifyCoordinator:
        self.context.data_file = str(path)
        return self

    def set_config(self, key: str, value: Any) -> SpecifyCoordinator:
        self.context.config[key] = value
        return self

    def set_metadata(self, key: str, value: Any) -> SpecifyCoordinator:
        self.context.metadata[key] = value
        return self

    @timed
    def execute_reasoning_only(self) -> dict[str, Any]:
        with span("coordinator.execute_reasoning_only"):
            if not self.context.input_file:
                raise ValueError("input_file is required for reasoning")

            result = execute_full_stack_integration(
                run_reasoning=True,
                run_deployment=False,
                run_observability=False,
                run_analytics=False,
                input_file=self.context.input_file,
            )

            self._execution_history.append(("reasoning", result))
            metric_counter("coordinator.reasoning", 1)
            return {
                "success": result.success,
                "duration": result.total_duration,
                "phases": result.phases_executed,
            }

    @timed
    def execute_deployment_only(self) -> dict[str, Any]:
        with span("coordinator.execute_deployment_only"):
            if not self.context.artifact_file:
                raise ValueError("artifact_file is required for deployment")

            result = execute_full_stack_integration(
                run_reasoning=False,
                run_deployment=True,
                run_observability=False,
                run_analytics=False,
                artifact_file=self.context.artifact_file,
            )

            self._execution_history.append(("deployment", result))
            metric_counter("coordinator.deployment", 1)
            return {
                "success": result.success,
                "duration": result.total_duration,
                "phases": result.phases_executed,
            }

    @timed
    def execute_observability_only(self) -> dict[str, Any]:
        with span("coordinator.execute_observability_only"):
            result = execute_full_stack_integration(
                run_reasoning=False,
                run_deployment=False,
                run_observability=True,
                run_analytics=False,
            )

            self._execution_history.append(("observability", result))
            metric_counter("coordinator.observability", 1)
            return {
                "success": result.success,
                "duration": result.total_duration,
                "phases": result.phases_executed,
            }

    @timed
    def execute_analytics_only(self) -> dict[str, Any]:
        with span("coordinator.execute_analytics_only"):
            if not self.context.data_file:
                raise ValueError("data_file is required for analytics")

            result = execute_full_stack_integration(
                run_reasoning=False,
                run_deployment=False,
                run_observability=False,
                run_analytics=True,
                data_file=self.context.data_file,
            )

            self._execution_history.append(("analytics", result))
            metric_counter("coordinator.analytics", 1)
            return {
                "success": result.success,
                "duration": result.total_duration,
                "phases": result.phases_executed,
            }

    @timed
    def execute_reasoning_and_deployment(self) -> dict[str, Any]:
        with span("coordinator.execute_reasoning_and_deployment"):
            if not self.context.input_file or not self.context.artifact_file:
                raise ValueError("Both input_file and artifact_file are required")

            providers = self.context.config.get("providers", ["aws"])

            result = execute_reasoning_and_deployment(
                self.context.input_file,
                self.context.artifact_file,
                providers=providers,
            )

            self._execution_history.append(("reasoning_and_deployment", result))
            metric_counter("coordinator.reasoning_and_deployment", 1)
            return {
                "success": result.success,
                "duration": result.total_duration,
                "phases": result.phases_executed,
            }

    @timed
    def execute_observability_and_analytics(self) -> dict[str, Any]:
        with span("coordinator.execute_observability_and_analytics"):
            if not self.context.data_file:
                raise ValueError("data_file is required")

            service_name = self.context.config.get("service_name")

            result = execute_observability_and_analytics(
                self.context.data_file,
                service_name=service_name,
            )

            self._execution_history.append(("observability_and_analytics", result))
            metric_counter("coordinator.observability_and_analytics", 1)
            return {
                "success": result.success,
                "duration": result.total_duration,
                "phases": result.phases_executed,
            }

    @timed
    def execute_full_pipeline(self) -> dict[str, Any]:
        with span("coordinator.execute_full_pipeline"):
            result = execute_full_stack_integration(
                run_reasoning=bool(self.context.input_file),
                run_deployment=bool(self.context.artifact_file),
                run_observability=True,
                run_analytics=bool(self.context.data_file),
                input_file=self.context.input_file,
                artifact_file=self.context.artifact_file,
                data_file=self.context.data_file,
            )

            self._execution_history.append(("full_pipeline", result))
            metric_counter("coordinator.full_pipeline", 1)
            return {
                "success": result.success,
                "duration": result.total_duration,
                "phases": result.phases_executed,
                "errors": result.errors,
            }

    def get_execution_history(self) -> list[tuple[str, Any]]:
        return self._execution_history.copy()

    def clear_execution_history(self) -> None:
        self._execution_history.clear()


_global_coordinator: SpecifyCoordinator | None = None


def get_coordinator() -> SpecifyCoordinator:
    global _global_coordinator
    if _global_coordinator is None:
        _global_coordinator = SpecifyCoordinator()
    return _global_coordinator
