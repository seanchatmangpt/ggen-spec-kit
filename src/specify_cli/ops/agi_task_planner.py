from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from specify_cli.core.instrumentation import add_span_attributes, add_span_event
from specify_cli.core.shell import timed
from specify_cli.core.telemetry import metric_counter, metric_histogram, span

__all__ = ["PlannerError", "Task", "TaskPlan", "plan_goal_decomposition"]


class PlannerError(Exception):
    def __init__(self, message: str, *, suggestions: list[str] | None = None) -> None:
        super().__init__(message)
        self.suggestions = suggestions or []


@dataclass
class Task:
    id: str
    name: str
    description: str
    estimated_effort: float
    dependencies: list[str] = field(default_factory=list)
    subtasks: list[Task] = field(default_factory=list)
    can_parallelize: bool = False


@dataclass
class TaskPlan:
    success: bool
    goal: str
    root_task: Task | None = None
    total_tasks: int = 0
    critical_path_length: float = 0.0
    parallelizable_segments: int = 0
    strategy: str = "hierarchical"
    max_depth: int = 0
    output_format: str = "json"
    cost_estimate: float = 0.0
    duration: float = 0.0
    errors: list[str] = field(default_factory=list)


@timed
def plan_goal_decomposition(
    goal_spec: str | Path,
    *,
    decomposition_strategy: str = "hierarchical",
    max_depth: int = 5,
    parallel_analysis: bool = True,
    cost_model: str = "uniform",
    output_format: str = "json",
) -> TaskPlan:
    start_time = time.time()
    plan = TaskPlan(
        success=False,
        goal=str(goal_spec),
        strategy=decomposition_strategy,
        max_depth=max_depth,
        output_format=output_format,
    )

    with span(
        "ops.agi_task_planner.plan_goal_decomposition",
        strategy=decomposition_strategy,
        max_depth=max_depth,
    ):
        try:
            goal_path = Path(goal_spec) if isinstance(goal_spec, (str, Path)) and Path(goal_spec).exists() else None
            goal_text = goal_path.read_text() if goal_path else goal_spec

            add_span_event("planner.starting_decomposition", {"strategy": decomposition_strategy})

            if decomposition_strategy == "hierarchical":
                plan.root_task = _hierarchical_decomposition(goal_text, max_depth)
            elif decomposition_strategy == "functional":
                plan.root_task = _functional_decomposition(goal_text, max_depth)
            elif decomposition_strategy == "data-flow":
                plan.root_task = _dataflow_decomposition(goal_text, max_depth)
            else:
                raise PlannerError(f"Unknown strategy: {decomposition_strategy}")

            _count_tasks(plan.root_task, plan)
            _compute_critical_path(plan.root_task, plan)

            if parallel_analysis:
                _analyze_parallelization(plan.root_task, plan)

            if cost_model == "weighted":
                _apply_weighted_cost(plan.root_task)
            elif cost_model == "time-based":
                _apply_time_based_cost(plan.root_task)

            plan.cost_estimate = _calculate_total_cost(plan.root_task) if plan.root_task else 0.0
            plan.success = True
            plan.duration = time.time() - start_time

            metric_counter("ops.agi_task_planner.success")(1)
            metric_histogram("ops.agi_task_planner.duration")(plan.duration)
            metric_histogram("ops.agi_task_planner.total_tasks")(plan.total_tasks)

            add_span_event(
                "planner.decomposition_completed",
                {
                    "success": True,
                    "total_tasks": plan.total_tasks,
                    "critical_path": plan.critical_path_length,
                    "duration": plan.duration,
                },
            )

            return plan

        except PlannerError:
            plan.duration = time.time() - start_time
            metric_counter("ops.agi_task_planner.error")(1)
            raise

        except Exception as e:
            plan.errors.append(str(e))
            plan.duration = time.time() - start_time
            metric_counter("ops.agi_task_planner.error")(1)
            raise PlannerError(f"Goal decomposition failed: {e}") from e


def _hierarchical_decomposition(goal: str, max_depth: int) -> Task:
    root = Task(id="goal_1", name="Root Goal", description=goal, estimated_effort=1.0)
    _build_hierarchy(root, 1, max_depth)
    return root


def _functional_decomposition(goal: str, max_depth: int) -> Task:
    root = Task(
        id="goal_1",
        name="Execute Goal (Functional)",
        description=goal,
        estimated_effort=1.0,
    )

    functions = [
        Task(id="func_1", name="Input Processing", description="Process inputs", estimated_effort=0.5),
        Task(id="func_2", name="Core Logic", description="Execute main logic", estimated_effort=1.5, dependencies=["func_1"]),
        Task(id="func_3", name="Output Generation", description="Generate outputs", estimated_effort=0.5, dependencies=["func_2"]),
    ]

    root.subtasks = functions
    return root


def _dataflow_decomposition(goal: str, max_depth: int) -> Task:
    root = Task(id="goal_1", name="Data Flow Goal", description=goal, estimated_effort=1.0)

    stages = [
        Task(id="stage_1", name="Data Source", description="Identify data sources", estimated_effort=0.3),
        Task(
            id="stage_2",
            name="Data Transform",
            description="Transform data",
            estimated_effort=1.0,
            dependencies=["stage_1"],
        ),
        Task(
            id="stage_3",
            name="Data Analysis",
            description="Analyze data",
            estimated_effort=0.8,
            dependencies=["stage_2"],
        ),
        Task(
            id="stage_4",
            name="Result Output",
            description="Output results",
            estimated_effort=0.4,
            dependencies=["stage_3"],
        ),
    ]

    root.subtasks = stages
    return root


def _build_hierarchy(parent: Task, depth: int, max_depth: int) -> None:
    if depth >= max_depth:
        return

    for i in range(2):
        child = Task(
            id=f"{parent.id}_{i}",
            name=f"{parent.name} - Subtask {i + 1}",
            description=f"Subtask for {parent.name}",
            estimated_effort=parent.estimated_effort / 2,
        )
        parent.subtasks.append(child)
        _build_hierarchy(child, depth + 1, max_depth)


def _count_tasks(task: Task | None, plan: TaskPlan) -> int:
    if not task:
        return 0
    count = 1
    for subtask in task.subtasks:
        count += _count_tasks(subtask, plan)
    plan.total_tasks = max(plan.total_tasks, count)
    return count


def _compute_critical_path(task: Task | None, plan: TaskPlan) -> float:
    if not task:
        return 0.0

    max_path = task.estimated_effort
    for subtask in task.subtasks:
        subtask_path = _compute_critical_path(subtask, plan)
        max_path = max(max_path, task.estimated_effort + subtask_path)

    plan.critical_path_length = max(plan.critical_path_length, max_path)
    return max_path


def _analyze_parallelization(task: Task | None, plan: TaskPlan) -> None:
    if not task:
        return

    independent_subtasks = sum(1 for st in task.subtasks if not st.dependencies)
    if independent_subtasks > 1:
        plan.parallelizable_segments += 1
        for subtask in task.subtasks:
            if not subtask.dependencies:
                subtask.can_parallelize = True

    for subtask in task.subtasks:
        _analyze_parallelization(subtask, plan)


def _apply_weighted_cost(task: Task | None) -> None:
    if not task:
        return

    task.estimated_effort *= 1.2

    for subtask in task.subtasks:
        _apply_weighted_cost(subtask)


def _apply_time_based_cost(task: Task | None) -> None:
    if not task:
        return

    task.estimated_effort = task.estimated_effort * len(task.dependencies or []) + 0.5

    for subtask in task.subtasks:
        _apply_time_based_cost(subtask)


def _calculate_total_cost(task: Task | None) -> float:
    if not task:
        return 0.0

    total = task.estimated_effort
    for subtask in task.subtasks:
        total += _calculate_total_cost(subtask)

    return total
