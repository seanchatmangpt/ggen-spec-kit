"""
specify_cli.async_core.streams - Async Data Streaming and Pipelines
====================================================================

Comprehensive async streaming with generators, queues, and pipeline operations.

This module provides:

* **AsyncStream**: Async generator wrapper with transformation operations
* **AsyncQueue**: Queue-based async data streaming
* **AsyncPipeline**: Composable async data processing pipelines
* **Backpressure**: Automatic backpressure handling
* **Stream Operators**: map, filter, batch, window, merge operations

Features
--------
* Async generator composition
* Streaming transformations (map, filter, reduce)
* Batching and windowing operations
* Queue-based processing with backpressure
* Pipeline composition and chaining
* Error handling and recovery
* Performance monitoring

Examples
--------
    >>> from specify_cli.async_core.streams import AsyncStream, async_map
    >>>
    >>> # Stream processing
    >>> async def process_data():
    ...     stream = AsyncStream([1, 2, 3, 4, 5])
    ...     async for item in stream.map(lambda x: x * 2).filter(lambda x: x > 4):
    ...         print(item)  # 6, 8, 10
    >>>
    >>> # Pipeline composition
    >>> pipeline = AsyncPipeline()
    >>> pipeline.add_stage(async_map(lambda x: x * 2))
    >>> pipeline.add_stage(async_filter(lambda x: x > 5))
    >>> results = await pipeline.process([1, 2, 3, 4, 5])

See Also
--------
- :mod:`specify_cli.async_core.runner` : Task execution and scheduling
- :mod:`specify_cli.core.telemetry` : Telemetry and observability
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator, Callable
from typing import TYPE_CHECKING, Any, TypeVar

from specify_cli.core.telemetry import metric_counter

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

T = TypeVar("T")
U = TypeVar("U")

__all__ = [
    "AsyncPipeline",
    "AsyncQueue",
    "AsyncStream",
    "async_batch",
    "async_filter",
    "async_map",
    "async_merge",
    "async_window",
]

_log = logging.getLogger("specify_cli.async_core.streams")


# ============================================================================
# Async Stream - Composable Async Iterators
# ============================================================================


class AsyncStream:
    """
    Async iterator wrapper with streaming operations.

    Parameters
    ----------
    source : AsyncIterator[T] | list[T]
        Source iterator or list to stream.

    Examples
    --------
    >>> async def numbers():
    ...     for i in range(5):
    ...         yield i
    >>>
    >>> stream = AsyncStream(numbers())
    >>> doubled = stream.map(lambda x: x * 2)
    >>> async for item in doubled:
    ...     print(item)
    """

    def __init__(self, source: AsyncIterator[T] | list[T]) -> None:
        if isinstance(source, list):
            # Convert list to async iterator
            async def list_iterator():
                for item in source:
                    yield item

            self._source = list_iterator()
        else:
            self._source = source

    def __aiter__(self) -> AsyncIterator[T]:
        """Return async iterator."""
        return self._source  # type: ignore[T]

    async def __anext__(self) -> T:
        """Get next item from stream."""
        return await self._source.__anext__()  # type: ignore[no-any-return]

    def map(self, func: Callable[..., Any][..., Any][[T], U | Awaitable[U]]) -> AsyncStream[U]:  # type: ignore[type-arg,valid-type]
        """
        Transform each item in the stream.

        Parameters
        ----------
        func : Callable[..., Any][..., Any][[T], U | Awaitable[U]]
            Transformation function (sync or async).

        Returns
        -------
        AsyncStream[U]
            New stream with transformed items.
        """
        async def mapped():
            async for item in self._source:
                if asyncio.iscoroutinefunction(func):
                    yield await func(item)
                else:
                    yield func(item)

        return AsyncStream(mapped())

    def filter(self, predicate: Callable[..., Any][..., Any][[T], bool | Awaitable[bool]]) -> AsyncStream[T]:  # type: ignore[type-arg,valid-type]
        """
        Filter items in the stream.

        Parameters
        ----------
        predicate : Callable[..., Any][..., Any][[T], bool | Awaitable[bool]]
            Filter predicate (sync or async).

        Returns
        -------
        AsyncStream[T]
            New stream with filtered items.
        """
        async def filtered():
            async for item in self._source:
                if asyncio.iscoroutinefunction(predicate):
                    if await predicate(item):
                        yield item
                elif predicate(item):
                    yield item

        return AsyncStream(filtered())

    def batch(self, size: int) -> AsyncStream[list[T]]:  # type: ignore[type-arg]
        """
        Batch items into groups.

        Parameters
        ----------
        size : int
            Batch size.

        Returns
        -------
        AsyncStream[list[T]]
            Stream of batches.
        """
        async def batched():
            batch: list[T] = []
            async for item in self._source:
                batch.append(item)
                if len(batch) >= size:
                    yield batch
                    batch = []
            if batch:
                yield batch

        return AsyncStream(batched())

    def window(self, size: int, step: int = 1) -> AsyncStream[list[T]]:  # type: ignore[type-arg]
        """
        Create sliding windows over the stream.

        Parameters
        ----------
        size : int
            Window size.
        step : int, optional
            Step size between windows. Default is 1.

        Returns
        -------
        AsyncStream[list[T]]
            Stream of windows.
        """
        async def windowed():
            window: list[T] = []
            async for item in self._source:
                window.append(item)
                if len(window) >= size:
                    yield window.copy()
                    # Slide window
                    window = window[step:]

        return AsyncStream(windowed())

    async def collect(self) -> list[T]:
        """
        Collect all items into a list.

        Returns
        -------
        list[T]
            All items from the stream.
        """
        items = []
        async for item in self._source:
            items.append(item)
        return items

    async def reduce(
        self,
        func: Callable[..., Any][..., Any][[U, T], U | Awaitable[U]],  # type: ignore[valid-type]
        initial: U,
    ) -> U:
        """
        Reduce stream to a single value.

        Parameters
        ----------
        func : Callable[..., Any][..., Any][[U, T], U | Awaitable[U]]
            Reduction function.
        initial : U
            Initial accumulator value.

        Returns
        -------
        U
            Final reduced value.
        """
        accumulator = initial
        async for item in self._source:
            if asyncio.iscoroutinefunction(func):
                accumulator = await func(accumulator, item)
            else:
                accumulator = func(accumulator, item)
        return accumulator

    async def count(self) -> int:
        """
        Count items in the stream.

        Returns
        -------
        int
            Number of items.
        """
        count = 0
        async for _ in self._source:
            count += 1
        return count


# ============================================================================
# Async Queue - Queue-Based Streaming
# ============================================================================


class AsyncQueue:
    """
    Async queue with backpressure handling.

    Parameters
    ----------
    maxsize : int, optional
        Maximum queue size. Default is 0 (unbounded).
    enable_metrics : bool, optional
        Enable performance metrics. Default is True.

    Examples
    --------
    >>> queue = AsyncQueue(maxsize=10)
    >>> await queue.put("item1")
    >>> item = await queue.get()
    """

    def __init__(self, maxsize: int = 0, enable_metrics: bool = True) -> None:
        self._queue: asyncio.Queue[T] = asyncio.Queue(maxsize=maxsize)  # type: ignore[valid-type]
        self.enable_metrics = enable_metrics
        self._closed = False

    async def put(self, item: T) -> None:
        """
        Put item in queue.

        Parameters
        ----------
        item : T
            Item to add to queue.
        """
        if self._closed:
            raise RuntimeError("Queue is closed") from None

        await self._queue.put(item)

        if self.enable_metrics:
            metric_counter("async.queue.put")(1)
            metric_counter("async.queue.size")(self._queue.qsize())

    async def get(self) -> T:
        """
        Get item from queue.

        Returns
        -------
        T
            Next item from queue.
        """
        item = await self._queue.get()

        if self.enable_metrics:
            metric_counter("async.queue.get")(1)

        return item

    def put_nowait(self, item: T) -> None:
        """Put item without waiting."""
        if self._closed:
            raise RuntimeError("Queue is closed") from None

        self._queue.put_nowait(item)

        if self.enable_metrics:
            metric_counter("async.queue.put_nowait")(1)

    def get_nowait(self) -> T:  # type: ignore[type-var]
        """Get item without waiting."""
        item = self._queue.get_nowait()

        if self.enable_metrics:
            metric_counter("async.queue.get_nowait")(1)

        return item

    def qsize(self) -> int:
        """Get current queue size."""
        return self._queue.qsize()

    def empty(self) -> bool:
        """Check if queue is empty."""
        return self._queue.empty()

    def full(self) -> bool:
        """Check if queue is full."""
        return self._queue.full()

    async def close(self) -> None:
        """Close the queue."""
        self._closed = True

    def stream(self) -> AsyncStream[T]:  # type: ignore[type-arg]
        """
        Create a stream from the queue.

        Returns
        -------
        AsyncStream[T]
            Stream of queue items.
        """
        async def queue_iterator():
            while not self._closed or not self._queue.empty():
                try:
                    yield await asyncio.wait_for(self._queue.get(), timeout=0.1)
                except TimeoutError:
                    if self._closed:
                        break

        return AsyncStream(queue_iterator())


# ============================================================================
# Async Pipeline - Composable Processing Stages
# ============================================================================


class AsyncPipeline:
    """
    Composable async data processing pipeline.

    Examples
    --------
    >>> pipeline = AsyncPipeline()
    >>> pipeline.add_stage(async_map(lambda x: x * 2))
    >>> pipeline.add_stage(async_filter(lambda x: x > 5))
    >>> results = await pipeline.process([1, 2, 3, 4, 5])
    """

    def __init__(self) -> None:
        self.stages: list[Callable[[AsyncIterator[Any]], AsyncIterator[Any]]] = []

    def add_stage(
        self,
        stage: Callable[..., Any][..., Any][[AsyncIterator[T]], AsyncIterator[U]],  # type: ignore[valid-type]
    ) -> AsyncPipeline:
        """
        Add a processing stage to the pipeline.

        Parameters
        ----------
        stage : Callable[..., Any][..., Any]
            Stage function that transforms an async iterator.

        Returns
        -------
        AsyncPipeline
            Self for chaining.
        """
        self.stages.append(stage)
        return self

    async def process(self, source: AsyncIterator[T] | list[T]) -> list[Any]:
        """
        Process data through the pipeline.

        Parameters
        ----------
        source : AsyncIterator[T] | list[T]
            Source data to process.

        Returns
        -------
        list[Any]
            Processed results.
        """
        stream = AsyncStream(source)

        # Apply each stage
        for stage in self.stages:
            stream = AsyncStream(stage(stream))

        # Collect results
        return await stream.collect()

    def compose(self, other: AsyncPipeline) -> AsyncPipeline:
        """
        Compose this pipeline with another.

        Parameters
        ----------
        other : AsyncPipeline
            Pipeline to compose with.

        Returns
        -------
        AsyncPipeline
            New composed pipeline.
        """
        new_pipeline = AsyncPipeline()
        new_pipeline.stages = self.stages + other.stages
        return new_pipeline


# ============================================================================
# Stream Utility Functions
# ============================================================================


def async_map(func: Callable[..., Any][..., Any][[T], U | Awaitable[U]]) -> Callable[[AsyncIterator[T]], AsyncIterator[U]]:  # type: ignore[valid-type]
    """
    Create a map stage for pipelines.

    Parameters
    ----------
    func : Callable[..., Any][..., Any][[T], U | Awaitable[U]]
        Transformation function.

    Returns
    -------
    Callable
        Pipeline stage function.
    """
    async def mapper(source: AsyncIterator[T]) -> AsyncIterator[U]:
        async for item in source:
            if asyncio.iscoroutinefunction(func):
                yield await func(item)
            else:
                yield func(item)

    return mapper


def async_filter(
    predicate: Callable[..., Any][..., Any][[T], bool | Awaitable[bool]],  # type: ignore[valid-type]
) -> Callable[[AsyncIterator[T]], AsyncIterator[T]]:
    """
    Create a filter stage for pipelines.

    Parameters
    ----------
    predicate : Callable[..., Any][..., Any][[T], bool | Awaitable[bool]]
        Filter predicate.

    Returns
    -------
    Callable
        Pipeline stage function.
    """
    async def filterer(source: AsyncIterator[T]) -> AsyncIterator[T]:
        async for item in source:
            if asyncio.iscoroutinefunction(predicate):
                if await predicate(item):
                    yield item
            elif predicate(item):
                yield item

    return filterer


def async_batch(size: int) -> Callable[[AsyncIterator[T]], AsyncIterator[list[T]]]:
    """
    Create a batch stage for pipelines.

    Parameters
    ----------
    size : int
        Batch size.

    Returns
    -------
    Callable
        Pipeline stage function.
    """
    async def batcher(source: AsyncIterator[T]) -> AsyncIterator[list[T]]:
        batch: list[T] = []
        async for item in source:
            batch.append(item)
            if len(batch) >= size:
                yield batch
                batch = []
        if batch:
            yield batch

    return batcher


def async_window(
    size: int,
    step: int = 1,
) -> Callable[[AsyncIterator[T]], AsyncIterator[list[T]]]:
    """
    Create a windowing stage for pipelines.

    Parameters
    ----------
    size : int
        Window size.
    step : int, optional
        Step size between windows.

    Returns
    -------
    Callable
        Pipeline stage function.
    """
    async def windower(source: AsyncIterator[T]) -> AsyncIterator[list[T]]:
        window: list[T] = []
        async for item in source:
            window.append(item)
            if len(window) >= size:
                yield window.copy()
                window = window[step:]

    return windower


async def async_merge(*streams: AsyncIterator[T]) -> AsyncIterator[T]:
    """
    Merge multiple async iterators into one.

    Parameters
    ----------
    *streams : AsyncIterator[T]
        Streams to merge.

    Yields
    ------
    T
        Items from all streams.
    """
    tasks = [asyncio.create_task(stream.__anext__()) for stream in streams]  # type: ignore[T,unused-ignore]
    pending = set(tasks)

    while pending:
        done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)

        for task in done:
            try:
                yield task.result()
                idx = tasks.index(task)
                tasks[idx] = asyncio.create_task(streams[idx].__anext__())  # type: ignore[T]
                pending.add(tasks[idx])
            except StopAsyncIteration:
                # Stream exhausted
                continue
