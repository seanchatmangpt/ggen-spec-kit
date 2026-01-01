from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from specify_cli.core.shell import timed
from specify_cli.core.telemetry import metric_counter, metric_histogram, span


class WorkflowPattern(Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    LOOP = "loop"
    FORK_JOIN = "fork_join"


@dataclass
class WorkflowNode:
    node_id: str
    handler: Callable
    pattern: WorkflowPattern = WorkflowPattern.SEQUENTIAL
    condition: Callable | None = None
    loop_count: int = 1
    dependencies: list[str] = field(default_factory=list)
    timeout: float = 30.0


@dataclass
class WorkflowExecution:
    workflow_id: str
    nodes_executed: list[str] = field(default_factory=list)
    nodes_failed: list[str] = field(default_factory=list)
    results: dict[str, Any] = field(default_factory=dict)
    errors: dict[str, str] = field(default_factory=dict)
    duration: float = 0.0
    success: bool = True


class AdvancedWorkflow:
    def __init__(self, workflow_id: str):
        self.workflow_id = workflow_id
        self.nodes: dict[str, WorkflowNode] = {}
        self.execution_order = []

    def add_node(self, node: WorkflowNode) -> None:
        self.nodes[node.node_id] = node

    def _topological_sort(self) -> list[str]:
        visited = set()
        order = []

        def visit(node_id: str) -> None:
            if node_id in visited:
                return
            visited.add(node_id)

            node = self.nodes[node_id]
            for dep in node.dependencies:
                if dep in self.nodes:
                    visit(dep)

            order.append(node_id)

        for node_id in self.nodes:
            visit(node_id)

        return order

    @timed
    def execute(self) -> WorkflowExecution:
        with span("workflow.execute", workflow=self.workflow_id):
            execution = WorkflowExecution(workflow_id=self.workflow_id)
            order = self._topological_sort()

            for node_id in order:
                node = self.nodes[node_id]

                try:
                    if node.pattern == WorkflowPattern.SEQUENTIAL:
                        result = node.handler()
                    elif node.pattern == WorkflowPattern.CONDITIONAL:
                        if node.condition and node.condition():
                            result = node.handler()
                        else:
                            result = {"skipped": True}
                    elif node.pattern == WorkflowPattern.LOOP:
                        results = []
                        for _ in range(node.loop_count):
                            results.append(node.handler())
                        result = {"iterations": len(results)}
                    else:
                        result = node.handler()

                    execution.nodes_executed.append(node_id)
                    execution.results[node_id] = result

                except Exception as e:
                    execution.nodes_failed.append(node_id)
                    execution.errors[node_id] = str(e)
                    execution.success = False

                    metric_counter("workflow.node_failed", 1, {
                        "workflow": self.workflow_id,
                        "node": node_id,
                    })

            metric_histogram("workflow.nodes_executed", len(execution.nodes_executed))
            metric_counter("workflow.completed", 1, {
                "success": str(execution.success),
            })

            return execution


class ParallelWorkflowExecutor:
    def __init__(self):
        self.tasks = []

    def add_task(self, task_id: str, handler: Callable) -> None:
        self.tasks.append((task_id, handler))

    @timed
    def execute(self) -> dict[str, Any]:
        with span("parallel_workflow.execute", count=len(self.tasks)):
            results = {}
            errors = {}

            for task_id, handler in self.tasks:
                try:
                    results[task_id] = handler()
                except Exception as e:
                    errors[task_id] = str(e)

            metric_counter("parallel_workflow.completed", 1)
            metric_histogram("parallel_workflow.task_count", len(self.tasks))

            return {
                "successful_tasks": len(results),
                "failed_tasks": len(errors),
                "results": results,
                "errors": errors,
            }


class ConditionalWorkflow:
    def __init__(self):
        self.conditions: list[tuple[Callable, Callable]] = []
        self.default_handler: Callable | None = None

    def add_condition(self, condition: Callable, handler: Callable) -> None:
        self.conditions.append((condition, handler))

    def set_default(self, handler: Callable) -> None:
        self.default_handler = handler

    @timed
    def execute(self) -> Any:
        with span("conditional_workflow.execute"):
            for condition, handler in self.conditions:
                if condition():
                    return handler()

            if self.default_handler:
                return self.default_handler()

            return None


@dataclass
class AsyncWorkflowResult:
    workflow_id: str
    status: str
    results: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


class ComposableWorkflow:
    def __init__(self, workflow_id: str):
        self.workflow_id = workflow_id
        self.steps: list[tuple[str, Callable]] = []

    def add_step(self, step_id: str, handler: Callable) -> ComposableWorkflow:
        self.steps.append((step_id, handler))
        return self

    @timed
    def execute(self) -> dict[str, Any]:
        with span("composable_workflow.execute"):
            results = {}

            for step_id, handler in self.steps:
                try:
                    results[step_id] = handler()
                except Exception as e:
                    results[step_id] = {"error": str(e)}

            metric_counter("composable_workflow.steps", len(self.steps))
            return results


class PipelineWorkflow:
    def __init__(self, name: str):
        self.name = name
        self.stages: list[Callable] = []

    def add_stage(self, handler: Callable) -> PipelineWorkflow:
        self.stages.append(handler)
        return self

    @timed
    def execute(self, initial_data: Any = None) -> Any:
        with span("pipeline_workflow.execute", stages=len(self.stages)):
            data = initial_data

            for i, stage in enumerate(self.stages):
                try:
                    data = stage(data)
                except Exception as e:
                    metric_counter("pipeline.stage_failed", 1, {"stage": i})
                    raise

            metric_histogram("pipeline.stages_executed", len(self.stages))
            return data
