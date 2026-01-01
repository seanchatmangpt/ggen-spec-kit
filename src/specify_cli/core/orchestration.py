from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable

from specify_cli.core.instrumentation import add_span_attributes, add_span_event
from specify_cli.core.shell import timed
from specify_cli.core.telemetry import metric_counter, metric_histogram, span
from specify_cli.runtime.execution import track_execution


@dataclass
class WorkflowStep:
    name: str
    handler: Callable[..., Any]
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    skip_on_error: bool = False
    depends_on: list[str] = field(default_factory=list)


@dataclass
class WorkflowResult:
    workflow_name: str
    success: bool
    steps_executed: list[str] = field(default_factory=list)
    steps_failed: list[str] = field(default_factory=list)
    step_results: dict[str, Any] = field(default_factory=dict)
    total_duration: float = 0.0
    errors: list[str] = field(default_factory=list)


class Workflow:
    def __init__(self, name: str):
        self.name = name
        self.steps: dict[str, WorkflowStep] = {}
        self._execution_order: list[str] = []

    def add_step(self, step: WorkflowStep) -> None:
        self.steps[step.name] = step
        self._execution_order.append(step.name)

    def remove_step(self, name: str) -> None:
        if name in self.steps:
            del self.steps[name]
            self._execution_order.remove(name)

    def get_dependency_order(self) -> list[str]:
        resolved = []
        unresolved = set(self.steps.keys())

        def resolve(name: str) -> None:
            if name not in unresolved:
                return

            step = self.steps[name]
            for dep in step.depends_on:
                if dep in unresolved:
                    resolve(dep)

            unresolved.remove(name)
            resolved.append(name)

        while unresolved:
            resolve(unresolved.pop())

        return resolved

    @timed
    def execute(self) -> WorkflowResult:
        with span(f"workflow.execute", workflow=self.name):
            result = WorkflowResult(
                workflow_name=self.name,
                success=True,
            )
            start_time = time.time()

            order = self.get_dependency_order()
            completed_steps = set()

            for step_name in order:
                step = self.steps[step_name]

                try:
                    add_span_event("workflow.step.start", {
                        "step": step_name,
                        "depends_on": step.depends_on,
                    })

                    tracker = track_execution(step_name)
                    tracker.set_input({
                        "args_count": len(step.args),
                        "kwargs_count": len(step.kwargs),
                    })

                    with tracker:
                        step_result = step.handler(*step.args, **step.kwargs)
                        result.step_results[step_name] = step_result
                        result.steps_executed.append(step_name)
                        completed_steps.add(step_name)

                    metric_counter("workflow.step.completed", 1, {"workflow": self.name})

                    add_span_event("workflow.step.complete", {
                        "step": step_name,
                        "status": "success",
                    })

                except Exception as e:
                    error_msg = f"Step {step_name} failed: {str(e)}"
                    result.errors.append(error_msg)
                    result.steps_failed.append(step_name)

                    metric_counter("workflow.step.failed", 1, {"workflow": self.name})

                    add_span_event("workflow.step.failed", {
                        "step": step_name,
                        "error": str(e),
                    })

                    if not step.skip_on_error:
                        result.success = False
                        break

            result.total_duration = time.time() - start_time

            metric_histogram("workflow.total_duration", result.total_duration)
            metric_counter("workflow.executed", 1, {
                "workflow": self.name,
                "success": str(result.success),
            })

            return result


class WorkflowFactory:
    _workflows: dict[str, Workflow] = {}

    @classmethod
    def create_workflow(cls, name: str) -> Workflow:
        workflow = Workflow(name)
        cls._workflows[name] = workflow
        return workflow

    @classmethod
    def get_workflow(cls, name: str) -> Workflow | None:
        return cls._workflows.get(name)

    @classmethod
    def list_workflows(cls) -> list[str]:
        return list(cls._workflows.keys())

    @classmethod
    def clear_workflows(cls) -> None:
        cls._workflows.clear()


def create_reasoning_workflow() -> Workflow:
    workflow = WorkflowFactory.create_workflow("reasoning")

    from specify_cli.runtime.agi import (
        execute_reasoning_task,
        execute_inference_task,
        execute_task_planning,
    )

    workflow.add_step(WorkflowStep(
        name="reasoning",
        handler=execute_reasoning_task,
        kwargs={"strategy": "cot", "max_iterations": 5},
        skip_on_error=False,
    ))

    workflow.add_step(WorkflowStep(
        name="inference",
        handler=execute_inference_task,
        depends_on=["reasoning"],
        skip_on_error=True,
    ))

    workflow.add_step(WorkflowStep(
        name="planning",
        handler=execute_task_planning,
        kwargs={"strategy": "hierarchical"},
        depends_on=["inference"],
        skip_on_error=True,
    ))

    return workflow


def create_deployment_workflow() -> Workflow:
    workflow = WorkflowFactory.create_workflow("deployment")

    from specify_cli.runtime.cloud import (
        execute_cloud_deployment,
        execute_cloud_scaling,
    )

    workflow.add_step(WorkflowStep(
        name="deploy_primary",
        handler=execute_cloud_deployment,
        kwargs={"provider": "aws", "region": "us-east-1"},
        skip_on_error=False,
    ))

    workflow.add_step(WorkflowStep(
        name="scale_primary",
        handler=execute_cloud_scaling,
        kwargs={"provider": "aws", "strategy": "rolling"},
        depends_on=["deploy_primary"],
        skip_on_error=True,
    ))

    return workflow


def create_observability_workflow() -> Workflow:
    workflow = WorkflowFactory.create_workflow("observability")

    from specify_cli.runtime.observability import (
        execute_observability_analysis,
        execute_dashboard_generation,
    )

    workflow.add_step(WorkflowStep(
        name="analyze_traces",
        handler=execute_observability_analysis,
        kwargs={"metric_type": "traces"},
        skip_on_error=False,
    ))

    workflow.add_step(WorkflowStep(
        name="generate_dashboard",
        handler=execute_dashboard_generation,
        kwargs={"input_file": "metrics.json", "format": "html"},
        depends_on=["analyze_traces"],
        skip_on_error=True,
    ))

    return workflow
