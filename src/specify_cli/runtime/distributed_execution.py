"""Distributed execution coordinator for multi-node task distribution.

Coordinates task execution across cluster with load balancing,
task affinity, and work stealing.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from specify_cli.core.shell import timed
from specify_cli.core.telemetry import metric_counter, metric_histogram, span
from specify_cli.runtime.cluster import ClusterManager, NodeRole


class TaskState(Enum):
    """State of distributed task."""

    PENDING = "pending"
    QUEUED = "queued"
    ASSIGNED = "assigned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskSchedulingStrategy(Enum):
    """Task scheduling strategy."""

    ROUND_ROBIN = "round_robin"
    LEAST_LOADED = "least_loaded"
    AFFINITY = "affinity"
    WORK_STEALING = "work_stealing"
    FAIR_SHARE = "fair_share"


@dataclass
class DistributedTask:
    """Task for distributed execution."""

    task_id: str
    task_name: str
    handler: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict[str, Any] = field(default_factory=dict)
    priority: int = 0
    affinity_node: str | None = None
    state: TaskState = TaskState.PENDING
    assigned_node: str | None = None
    result: Any = None
    error: str | None = None
    created_at: float = field(default_factory=time.time)
    started_at: float | None = None
    completed_at: float | None = None
    execution_time: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "task_id": self.task_id,
            "task_name": self.task_name,
            "priority": self.priority,
            "affinity_node": self.affinity_node,
            "state": self.state.value,
            "assigned_node": self.assigned_node,
            "result": str(self.result) if self.result else None,
            "error": self.error,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "execution_time": self.execution_time,
        }


@dataclass
class TaskScheduleResult:
    """Result of task scheduling."""

    success: bool
    task_id: str
    assigned_node: str | None
    message: str
    error: str | None = None


@dataclass
class ExecutionStats:
    """Statistics for task execution."""

    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    pending_tasks: int = 0
    total_execution_time: float = 0.0
    average_execution_time: float = 0.0
    max_execution_time: float = 0.0
    min_execution_time: float = 0.0


class DistributedExecutor:
    """Executes tasks across distributed cluster."""

    def __init__(
        self,
        cluster_manager: ClusterManager,
        scheduling_strategy: TaskSchedulingStrategy = TaskSchedulingStrategy.LEAST_LOADED,
    ):
        self.cluster = cluster_manager
        self.strategy = scheduling_strategy
        self.tasks: dict[str, DistributedTask] = {}
        self.task_queue: list[DistributedTask] = []
        self.completed_tasks: dict[str, DistributedTask] = {}
        self.node_workloads: dict[str, int] = {}
        self.stats = ExecutionStats()

    @timed
    def submit_task(
        self,
        task_name: str,
        handler: Callable,
        *args: Any,
        affinity_node: str | None = None,
        priority: int = 0,
        **kwargs: Any,
    ) -> TaskScheduleResult:
        """Submit task for distributed execution."""
        with span(
            "distributed_execution.submit_task",
            cluster=self.cluster.cluster_name,
            task=task_name,
        ):
            task = DistributedTask(
                task_id=str(uuid.uuid4())[:8],
                task_name=task_name,
                handler=handler,
                args=args,
                kwargs=kwargs,
                priority=priority,
                affinity_node=affinity_node,
            )

            self.tasks[task.task_id] = task
            self.task_queue.append(task)
            self.task_queue.sort(key=lambda t: t.priority, reverse=True)
            self.stats.total_tasks += 1
            self.stats.pending_tasks += 1

            metric_counter(
                "distributed_execution.task_submitted",
                1,
                {
                    "cluster": self.cluster.cluster_name,
                    "task": task_name,
                    "priority": str(priority),
                },
            )

            return TaskScheduleResult(
                success=True,
                task_id=task.task_id,
                assigned_node=None,
                message="task submitted to queue",
            )

    @timed
    def schedule_task(self, task: DistributedTask) -> TaskScheduleResult:
        """Schedule task to appropriate node."""
        with span(
            "distributed_execution.schedule_task",
            cluster=self.cluster.cluster_name,
            task=task.task_id,
        ):
            # Select node based on strategy
            node_id = self._select_node(task)

            if not node_id:
                return TaskScheduleResult(
                    success=False,
                    task_id=task.task_id,
                    assigned_node=None,
                    message="no available nodes",
                    error="cluster has no healthy nodes",
                )

            task.assigned_node = node_id
            task.state = TaskState.ASSIGNED
            self.node_workloads[node_id] = self.node_workloads.get(node_id, 0) + 1

            metric_counter(
                "distributed_execution.task_scheduled",
                1,
                {
                    "cluster": self.cluster.cluster_name,
                    "node": node_id,
                    "strategy": self.strategy.value,
                },
            )

            return TaskScheduleResult(
                success=True,
                task_id=task.task_id,
                assigned_node=node_id,
                message=f"task assigned to {node_id}",
            )

    @timed
    def execute_batch(self) -> int:
        """Execute batch of pending tasks."""
        with span(
            "distributed_execution.execute_batch",
            cluster=self.cluster.cluster_name,
        ):
            executed = 0

            # Sort by priority
            self.task_queue.sort(key=lambda t: t.priority, reverse=True)

            # Schedule pending tasks
            for task in self.task_queue[:]:
                if task.state == TaskState.PENDING:
                    result = self.schedule_task(task)
                    if result.success:
                        task.state = TaskState.QUEUED

            # Execute assigned tasks
            tasks_to_execute = [
                t for t in self.tasks.values()
                if t.state == TaskState.ASSIGNED
            ]

            for task in tasks_to_execute:
                try:
                    task.state = TaskState.RUNNING
                    task.started_at = time.time()

                    result = task.handler(*task.args, **task.kwargs)
                    task.result = result
                    task.state = TaskState.COMPLETED

                    task.completed_at = time.time()
                    task.execution_time = (
                        task.completed_at - task.started_at
                    )

                    self.completed_tasks[task.task_id] = task
                    self.stats.completed_tasks += 1
                    self.stats.total_execution_time += task.execution_time
                    self.stats.pending_tasks -= 1

                    executed += 1

                    metric_counter(
                        "distributed_execution.task_completed",
                        1,
                        {
                            "cluster": self.cluster.cluster_name,
                            "task": task.task_name,
                        },
                    )

                except Exception as e:
                    task.state = TaskState.FAILED
                    task.error = str(e)
                    task.completed_at = time.time()
                    task.execution_time = (
                        task.completed_at - task.started_at
                    ) if task.started_at else 0.0

                    self.completed_tasks[task.task_id] = task
                    self.stats.failed_tasks += 1
                    self.stats.pending_tasks -= 1

                    metric_counter(
                        "distributed_execution.task_failed",
                        1,
                        {
                            "cluster": self.cluster.cluster_name,
                            "task": task.task_name,
                        },
                    )

                # Remove from queue
                if task in self.task_queue:
                    self.task_queue.remove(task)

            # Update stats
            if self.stats.completed_tasks > 0:
                self.stats.average_execution_time = (
                    self.stats.total_execution_time / self.stats.completed_tasks
                )

            metric_histogram(
                "distributed_execution.batch_size",
                float(executed),
                {"cluster": self.cluster.cluster_name},
            )

            return executed

    def _select_node(self, task: DistributedTask) -> str | None:
        """Select node for task execution."""
        available = self.cluster.get_available_nodes()

        if not available:
            return None

        # Affinity strategy
        if task.affinity_node:
            for node in available:
                if node.node_id == task.affinity_node:
                    return node.node_id

        # Round robin
        if self.strategy == TaskSchedulingStrategy.ROUND_ROBIN:
            return available[
                len(self.completed_tasks) % len(available)
            ].node_id

        # Least loaded
        elif self.strategy == TaskSchedulingStrategy.LEAST_LOADED:
            return min(
                available,
                key=lambda n: self.node_workloads.get(n.node_id, 0),
            ).node_id

        # Work stealing
        elif self.strategy == TaskSchedulingStrategy.WORK_STEALING:
            workers = self.cluster.get_nodes_by_role(NodeRole.WORKER)
            if workers:
                return min(
                    workers,
                    key=lambda n: n.task_count,
                ).node_id

        # Fair share
        elif self.strategy == TaskSchedulingStrategy.FAIR_SHARE:
            return min(
                available,
                key=lambda n: (
                    n.cpu_usage + n.memory_usage
                ) / 2,
            ).node_id

        # Default
        return available[0].node_id

    def get_task_status(self, task_id: str) -> dict[str, Any] | None:
        """Get status of task."""
        if task_id in self.tasks:
            return self.tasks[task_id].to_dict()

        if task_id in self.completed_tasks:
            return self.completed_tasks[task_id].to_dict()

        return None

    def get_execution_stats(self) -> dict[str, Any]:
        """Get execution statistics."""
        return {
            "total_tasks": self.stats.total_tasks,
            "completed_tasks": self.stats.completed_tasks,
            "failed_tasks": self.stats.failed_tasks,
            "pending_tasks": self.stats.pending_tasks,
            "total_execution_time": self.stats.total_execution_time,
            "average_execution_time": self.stats.average_execution_time,
            "success_rate": (
                self.stats.completed_tasks / self.stats.total_tasks
                if self.stats.total_tasks > 0
                else 0.0
            ),
            "node_workloads": self.node_workloads,
        }


_global_distributed_executor: DistributedExecutor | None = None


def get_distributed_executor(
    cluster_manager: ClusterManager | None = None,
) -> DistributedExecutor:
    """Get or create global distributed executor."""
    global _global_distributed_executor

    if _global_distributed_executor is None:
        if cluster_manager is None:
            from specify_cli.runtime.cluster import get_cluster_manager
            cluster_manager = get_cluster_manager()

        _global_distributed_executor = DistributedExecutor(
            cluster_manager,
            scheduling_strategy=TaskSchedulingStrategy.LEAST_LOADED,
        )

    return _global_distributed_executor
