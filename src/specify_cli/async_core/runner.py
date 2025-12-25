"""
specify_cli.async_core.runner - AsyncIO Event Loop and Task Management
=======================================================================

Comprehensive async task execution with scheduling, prioritization, and resource pooling.

This module provides:

* **AsyncRunner**: Main async task executor with resource pooling
* **TaskScheduler**: Priority-based task scheduling and coordination
* **TaskPriority**: Priority levels for task execution
* **Resource Pool**: Shared resource management across async tasks
* **Background Tasks**: Long-running background task management

Features
--------
* Concurrent task execution with configurable limits
* Priority-based task scheduling
* Resource pooling and lifecycle management
* Exception handling and recovery
* Task cancellation and timeouts
* Performance monitoring and metrics
* Graceful shutdown with cleanup

Examples
--------
    >>> import asyncio
    >>> from specify_cli.async_core.runner import AsyncRunner, TaskPriority
    >>>
    >>> async def fetch_data(url):
    ...     await asyncio.sleep(1)
    ...     return f"Data from {url}"
    >>>
    >>> async def main():
    ...     runner = AsyncRunner(max_workers=5)
    ...
    ...     # Run tasks concurrently
    ...     results = await runner.gather([
    ...         fetch_data("url1"),
    ...         fetch_data("url2"),
    ...         fetch_data("url3"),
    ...     ])
    ...
    ...     # Run with priority
    ...     result = await runner.submit(
    ...         fetch_data("important"),
    ...         priority=TaskPriority.HIGH
    ...     )
    >>>
    >>> asyncio.run(main())

See Also
--------
- :mod:`specify_cli.async_core.streams` : Async data streaming
- :mod:`specify_cli.core.telemetry` : Telemetry and observability
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
from collections.abc import Callable
from contextlib import asynccontextmanager, suppress
from dataclasses import dataclass, field
from enum import IntEnum
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import uuid4

from specify_cli.core.telemetry import metric_counter, metric_histogram, span

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Coroutine

T = TypeVar("T")

__all__ = [
    "AsyncRunner",
    "ResourcePool",
    "TaskPriority",
    "TaskScheduler",
    "async_background",
    "async_run",
    "async_timeout",
]

_log = logging.getLogger("specify_cli.async_core.runner")


# ============================================================================
# Task Priority Levels
# ============================================================================


class TaskPriority(IntEnum):
    """Priority levels for task scheduling."""

    CRITICAL = 0  # Highest priority
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BACKGROUND = 4  # Lowest priority


# ============================================================================
# ============================================================================


@dataclass(order=True)
class ScheduledTask:
    """Wrapper for tasks with priority and metadata."""

    priority: int
    created_at: float = field(compare=False)
    task_id: str = field(compare=False)
    coro: Coroutine[Any, Any, Any] = field(compare=False)
    result_future: asyncio.Future[Any] = field(compare=False)
    timeout: float | None = field(default=None, compare=False)
    metadata: dict[str, Any] = field(default_factory=dict, compare=False)


# ============================================================================
# ============================================================================


class ResourcePool:
    """
    Manage shared resources across async tasks.

    Provides lifecycle management, resource acquisition, and cleanup.

    Parameters
    ----------
    max_resources : int
        Maximum number of resources in the pool.
    factory : Callable[..., Any][..., Any][[], Awaitable[Any]]
        Factory function to create new resources.
    cleanup : Callable[..., Any][..., Any][[Any], Awaitable[None]], optional
        Cleanup function for resources.

    Examples
    --------
    >>> async def create_connection():
    ...     return {"conn": "database"}
    >>>
    >>> async def close_connection(conn):
    ...     conn["closed"] = True
    >>>
    >>> pool = ResourcePool(
    ...     max_resources=10,
    ...     factory=create_connection,
    ...     cleanup=close_connection
    ... )
    """

    def __init__(
        self,
        max_resources: int,
        factory: Callable[..., Any][..., Any][[], Awaitable[Any]],  # type: ignore[valid-type]
        cleanup: Callable[..., Any][..., Any][[Any], Awaitable[None]] | None = None,  # type: ignore[valid-type]
    ) -> None:
        self.max_resources = max_resources
        self.factory = factory
        self.cleanup = cleanup
        self._pool: asyncio.Queue[Any] = asyncio.Queue(maxsize=max_resources)
        self._created = 0
        self._lock = asyncio.Lock()
        self._closed = False

    @asynccontextmanager
    async def acquire(self):
        """Acquire a resource from the pool."""
        if self._closed:
            raise RuntimeError("Resource pool is closed") from None

        resource = None
        try:
            # Try to get from pool
            resource = self._pool.get_nowait()
            metric_counter("async.resource_pool.reused")(1)
        except asyncio.QueueEmpty:
            async with self._lock:
                if self._created < self.max_resources:
                    resource = await self.factory()
                    self._created += 1
                    metric_counter("async.resource_pool.created")(1)
                else:
                    resource = await self._pool.get()
                    metric_counter("async.resource_pool.waited")(1)

        try:
            yield resource
        finally:
            if not self._closed:
                try:
                    self._pool.put_nowait(resource)
                except asyncio.QueueFull:
                    # Pool full, cleanup resource
                    if self.cleanup:
                        await self.cleanup(resource)
                        self._created -= 1

    async def close(self) -> None:
        """Close the pool and cleanup all resources."""
        self._closed = True

        # Cleanup all resources in pool
        while not self._pool.empty():
            try:
                resource = self._pool.get_nowait()
                if self.cleanup:
                    await self.cleanup(resource)
                self._created -= 1
            except asyncio.QueueEmpty:
                break


# ============================================================================
# Task Scheduler with Priority Queue
# ============================================================================


class TaskScheduler:
    """
    Priority-based task scheduler with resource limits.

    Parameters
    ----------
    max_concurrent : int
        Maximum number of concurrent tasks.
    enable_metrics : bool, optional
        Enable performance metrics. Default is True.

    Examples
    --------
    >>> scheduler = TaskScheduler(max_concurrent=5)
    >>> await scheduler.submit(some_task(), priority=TaskPriority.HIGH)
    """

    def __init__(self, max_concurrent: int = 10, enable_metrics: bool = True) -> None:
        self.max_concurrent = max_concurrent
        self.enable_metrics = enable_metrics
        self._queue: asyncio.PriorityQueue[ScheduledTask] = asyncio.PriorityQueue()
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._active_tasks: set[asyncio.Task[Any]] = set()
        self._shutdown = False
        self._worker_task: asyncio.Task[None] | None = None

    async def start(self) -> None:
        """Start the scheduler worker."""
        if self._worker_task is None:
            self._worker_task = asyncio.create_task(self._worker())

    async def submit(
        self,
        coro: Coroutine[Any, Any, T],
        priority: TaskPriority = TaskPriority.NORMAL,
        timeout: float | None = None,
        **metadata: Any,
    ) -> T:
        """
        Submit a task for execution.

        Parameters
        ----------
        coro : Coroutine
            Coroutine to execute.
        priority : TaskPriority, optional
            Task priority level.
        timeout : float, optional
            Task timeout in seconds.
        **metadata : Any
            Additional task metadata.

        Returns
        -------
        T
            Result of the coroutine execution.
        """
        task_id = str(uuid4())
        result_future: asyncio.Future[T] = asyncio.Future()

        scheduled = ScheduledTask(
            priority=int(priority),
            created_at=time.time(),
            task_id=task_id,
            coro=coro,
            result_future=result_future,
            timeout=timeout,
            metadata=metadata,
        )

        await self._queue.put(scheduled)

        if self.enable_metrics:
            metric_counter("async.scheduler.submitted")(1, {"priority": priority.name})  # type: ignore[call-arg]

        return await result_future

    async def _worker(self) -> None:
        """Background worker that processes scheduled tasks."""
        while not self._shutdown:
            try:
                # Get next task from priority queue
                scheduled = await asyncio.wait_for(self._queue.get(), timeout=1.0)

                await self._semaphore.acquire()

                # Execute task
                task = asyncio.create_task(self._execute_task(scheduled))
                self._active_tasks.add(task)
                task.add_done_callback(lambda t: self._active_tasks.discard(t))

            except TimeoutError:
                continue  # Check for shutdown
            except Exception as e:
                _log.error(f"Scheduler worker error: {e}")

    async def _execute_task(self, scheduled: ScheduledTask) -> None:
        """Execute a scheduled task with timeout and error handling."""
        start_time = time.time()

        try:
            with span(
                "async.task.execution",
                task_id=scheduled.task_id,
                priority=scheduled.priority,
            ):
                # Execute with optional timeout
                if scheduled.timeout:
                    result = await asyncio.wait_for(scheduled.coro, timeout=scheduled.timeout)
                else:
                    result = await scheduled.coro

                # Set result
                if not scheduled.result_future.done():
                    scheduled.result_future.set_result(result)

                # Record metrics
                duration = time.time() - start_time
                if self.enable_metrics:
                    metric_counter("async.task.completed")(1)
                    metric_histogram("async.task.duration")(duration)

        except TimeoutError:
            _log.warning(f"Task {scheduled.task_id} timed out after {scheduled.timeout}s")
            if not scheduled.result_future.done():
                scheduled.result_future.set_exception(
                    TimeoutError(f"Task timed out after {scheduled.timeout}s")
                )
            if self.enable_metrics:
                metric_counter("async.task.timeout")(1)

        except Exception as e:
            _log.error(f"Task {scheduled.task_id} failed: {e}")
            if not scheduled.result_future.done():
                scheduled.result_future.set_exception(e)
            if self.enable_metrics:
                metric_counter("async.task.failed")(1)

        finally:
            self._semaphore.release()

    async def shutdown(self, wait: bool = True) -> None:
        """
        Shutdown the scheduler.

        Parameters
        ----------
        wait : bool, optional
            Wait for active tasks to complete. Default is True.
        """
        self._shutdown = True

        if wait and self._active_tasks:
            await asyncio.gather(*self._active_tasks, return_exceptions=True)

        if self._worker_task:
            self._worker_task.cancel()
            with suppress(asyncio.CancelledError):
                await self._worker_task


# ============================================================================
# Main Async Runner
# ============================================================================


class AsyncRunner:
    """
    High-level async task executor with resource management.

    Parameters
    ----------
    max_workers : int, optional
        Maximum concurrent workers. Default from env or 10.
    enable_metrics : bool, optional
        Enable performance metrics. Default is True.

    Examples
    --------
    >>> runner = AsyncRunner(max_workers=5)
    >>> results = await runner.gather([task1(), task2(), task3()])
    """

    def __init__(self, max_workers: int | None = None, enable_metrics: bool = True) -> None:
        self.max_workers = max_workers or int(os.getenv("SPECIFY_ASYNC_WORKERS", "10"))
        self.enable_metrics = enable_metrics
        self.scheduler = TaskScheduler(max_concurrent=self.max_workers, enable_metrics=enable_metrics)
        self._started = False

    async def __aenter__(self) -> AsyncRunner:
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit."""
        await self.shutdown()

    async def start(self) -> None:
        """Start the async runner."""
        if not self._started:
            await self.scheduler.start()
            self._started = True

    async def gather(
        self,
        coros: list[Coroutine[Any, Any, T]],
        return_exceptions: bool = False,
    ) -> list[T | BaseException]:
        """
        Execute multiple coroutines concurrently.

        Parameters
        ----------
        coros : list[Coroutine]
            List of coroutines to execute.
        return_exceptions : bool, optional
            Return exceptions instead of raising. Default is False.

        Returns
        -------
        list[T | BaseException]
            Results from all coroutines.
        """
        if not self._started:
            await self.start()

        start_time = time.time()

        try:
            results = await asyncio.gather(*coros, return_exceptions=return_exceptions)

            duration = time.time() - start_time
            if self.enable_metrics:
                metric_counter("async.gather.completed")(1)
                metric_histogram("async.gather.duration")(duration)
                metric_counter("async.gather.tasks")(len(coros))

            return results

        except Exception:
            if self.enable_metrics:
                metric_counter("async.gather.failed")(1)
            raise

    async def submit(
        self,
        coro: Coroutine[Any, Any, T],
        priority: TaskPriority = TaskPriority.NORMAL,
        timeout: float | None = None,
    ) -> T:
        """
        Submit a single task for execution.

        Parameters
        ----------
        coro : Coroutine
            Coroutine to execute.
        priority : TaskPriority, optional
            Task priority level.
        timeout : float, optional
            Task timeout in seconds.

        Returns
        -------
        T
            Result from the coroutine.
        """
        if not self._started:
            await self.start()

        return await self.scheduler.submit(coro, priority=priority, timeout=timeout)

    async def shutdown(self, wait: bool = True) -> None:
        """
        Shutdown the runner.

        Parameters
        ----------
        wait : bool, optional
            Wait for active tasks to complete.
        """
        await self.scheduler.shutdown(wait=wait)


# ============================================================================
# Utility Functions
# ============================================================================


def async_run(coro: Coroutine[Any, Any, T]) -> T:
    """
    Run a coroutine and return the result.

    Parameters
    ----------
    coro : Coroutine
        Coroutine to execute.

    Returns
    -------
    T
        Result from the coroutine.
    """
    return asyncio.run(coro)


@asynccontextmanager  # type: ignore[float]
async def async_timeout(seconds: float) -> None:  # type: ignore[misc]
    """
    Async context manager for timeout.

    Parameters
    ----------
    seconds : float
        Timeout duration in seconds.

    Examples
    --------
    >>> async with async_timeout(5.0):
    ...     await long_running_task()
    """
    try:
        async with asyncio.timeout(seconds):
            yield
    except TimeoutError:
        metric_counter("async.timeout.exceeded")(1)
        raise


def async_background(coro: Coroutine[Any, Any, Any]) -> asyncio.Task[Any]:
    """
    Run a coroutine in the background.

    Parameters
    ----------
    coro : Coroutine
        Coroutine to execute in background.

    Returns
    -------
    asyncio.Task
        Background task handle.

    Examples
    --------
    >>> task = async_background(monitor_system())
    >>> # ... do other work ...
    >>> result = await task
    """
    task = asyncio.create_task(coro)
    metric_counter("async.background.started")(1)
    return task
