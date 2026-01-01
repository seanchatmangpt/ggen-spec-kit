from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from specify_cli.core.shell import timed
from specify_cli.core.telemetry import metric_counter, metric_histogram, span


class WorkerStatus(Enum):
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    SHUTDOWN = "shutdown"


@dataclass
class WorkItem:
    item_id: str
    task_handler: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict[str, Any] = field(default_factory=dict)
    priority: int = 0
    result: Any = None
    error: str | None = None
    status: str = "pending"


@dataclass
class WorkerMetrics:
    worker_id: str
    items_processed: int = 0
    items_failed: int = 0
    total_processing_time: float = 0.0
    current_status: WorkerStatus = WorkerStatus.IDLE


class Worker:
    def __init__(self, worker_id: str):
        self.worker_id = worker_id
        self.status = WorkerStatus.IDLE
        self.current_item: WorkItem | None = None
        self.metrics = WorkerMetrics(worker_id=worker_id)
        self.work_queue: list[WorkItem] = []

    def enqueue_work(self, item: WorkItem) -> None:
        self.work_queue.append(item)
        self.work_queue.sort(key=lambda x: x.priority, reverse=True)

    @timed
    def process_work(self) -> WorkItem | None:
        with span(f"worker.process", worker=self.worker_id):
            if not self.work_queue:
                self.status = WorkerStatus.IDLE
                return None

            item = self.work_queue.pop(0)
            self.current_item = item
            self.status = WorkerStatus.BUSY

            try:
                result = item.task_handler(*item.args, **item.kwargs)
                item.result = result
                item.status = "completed"
                self.metrics.items_processed += 1

                metric_counter("worker.items_processed", 1, {
                    "worker": self.worker_id,
                })

            except Exception as e:
                item.error = str(e)
                item.status = "failed"
                self.metrics.items_failed += 1
                self.status = WorkerStatus.ERROR

                metric_counter("worker.items_failed", 1, {
                    "worker": self.worker_id,
                })

            self.current_item = None
            return item

    def get_metrics(self) -> WorkerMetrics:
        self.metrics.current_status = self.status
        return self.metrics

    def shutdown(self) -> None:
        self.status = WorkerStatus.SHUTDOWN


class WorkerPool:
    def __init__(self, pool_size: int = 4):
        self.pool_size = pool_size
        self.workers: dict[str, Worker] = {}
        self.global_queue: list[WorkItem] = []
        self.completed_items: dict[str, WorkItem] = {}

        for i in range(pool_size):
            worker_id = f"worker-{i}"
            self.workers[worker_id] = Worker(worker_id)

    @timed
    def submit_work(self, task_handler: Callable, *args: Any, **kwargs: Any) -> str:
        with span("pool.submit_work"):
            item = WorkItem(
                item_id=str(uuid.uuid4())[:8],
                task_handler=task_handler,
                args=args,
                kwargs=kwargs,
                priority=kwargs.pop("priority", 0),
            )

            self.global_queue.append(item)
            metric_counter("pool.work_submitted", 1)
            return item.item_id

    def _distribute_work(self) -> None:
        self.global_queue.sort(key=lambda x: x.priority, reverse=True)

        for item in self.global_queue[:]:
            for worker in self.workers.values():
                if worker.status == WorkerStatus.IDLE:
                    worker.enqueue_work(item)
                    self.global_queue.remove(item)
                    break

    @timed
    def execute_batch(self) -> int:
        with span("pool.execute_batch"):
            self._distribute_work()

            completed = 0
            for worker in self.workers.values():
                result = worker.process_work()
                if result:
                    self.completed_items[result.item_id] = result
                    completed += 1

            metric_histogram("pool.items_completed_per_cycle", completed)
            return completed

    def get_result(self, item_id: str) -> Any:
        if item_id in self.completed_items:
            return self.completed_items[item_id].result
        return None

    def get_pool_status(self) -> dict[str, Any]:
        idle = sum(1 for w in self.workers.values() if w.status == WorkerStatus.IDLE)
        busy = sum(1 for w in self.workers.values() if w.status == WorkerStatus.BUSY)

        return {
            "pool_size": self.pool_size,
            "idle_workers": idle,
            "busy_workers": busy,
            "queued_items": len(self.global_queue),
            "completed_items": len(self.completed_items),
            "worker_metrics": [w.get_metrics() for w in self.workers.values()],
        }

    def shutdown_pool(self) -> None:
        for worker in self.workers.values():
            worker.shutdown()


_global_worker_pool: WorkerPool | None = None


def get_worker_pool(pool_size: int = 4) -> WorkerPool:
    global _global_worker_pool
    if _global_worker_pool is None:
        _global_worker_pool = WorkerPool(pool_size)
    return _global_worker_pool
