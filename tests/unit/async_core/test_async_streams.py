"""Tests for async_core.streams module."""

from __future__ import annotations

import asyncio

import pytest

from specify_cli.async_core.streams import (
    AsyncPipeline,
    AsyncQueue,
    AsyncStream,
    async_batch,
    async_filter,
    async_map,
    async_merge,
    async_window,
)


@pytest.mark.unit
class TestAsyncStream:
    """Test AsyncStream functionality."""

    @pytest.mark.asyncio
    async def test_basic_iteration(self) -> None:
        """Test basic async stream iteration."""
        stream = AsyncStream([1, 2, 3, 4, 5])
        results = []

        async for item in stream:
            results.append(item)

        assert results == [1, 2, 3, 4, 5]

    @pytest.mark.asyncio
    async def test_map_transformation(self) -> None:
        """Test map transformation."""
        stream = AsyncStream([1, 2, 3, 4, 5])
        doubled = stream.map(lambda x: x * 2)

        results = await doubled.collect()
        assert results == [2, 4, 6, 8, 10]

    @pytest.mark.asyncio
    async def test_async_map(self) -> None:
        """Test async map transformation."""
        async def async_double(x: int) -> int:
            await asyncio.sleep(0.01)
            return x * 2

        stream = AsyncStream([1, 2, 3])
        doubled = stream.map(async_double)

        results = await doubled.collect()
        assert results == [2, 4, 6]

    @pytest.mark.asyncio
    async def test_filter(self) -> None:
        """Test filter operation."""
        stream = AsyncStream([1, 2, 3, 4, 5])
        evens = stream.filter(lambda x: x % 2 == 0)

        results = await evens.collect()
        assert results == [2, 4]

    @pytest.mark.asyncio
    async def test_async_filter(self) -> None:
        """Test async filter operation."""
        async def async_is_even(x: int) -> bool:
            await asyncio.sleep(0.01)
            return x % 2 == 0

        stream = AsyncStream([1, 2, 3, 4, 5])
        evens = stream.filter(async_is_even)

        results = await evens.collect()
        assert results == [2, 4]

    @pytest.mark.asyncio
    async def test_chained_operations(self) -> None:
        """Test chained stream operations."""
        stream = AsyncStream([1, 2, 3, 4, 5, 6])
        result = stream.map(lambda x: x * 2).filter(lambda x: x > 5)

        values = await result.collect()
        assert values == [6, 8, 10, 12]

    @pytest.mark.asyncio
    async def test_batch(self) -> None:
        """Test batch operation."""
        stream = AsyncStream([1, 2, 3, 4, 5])
        batched = stream.batch(2)

        results = await batched.collect()
        assert results == [[1, 2], [3, 4], [5]]

    @pytest.mark.asyncio
    async def test_window(self) -> None:
        """Test windowing operation."""
        stream = AsyncStream([1, 2, 3, 4, 5])
        windowed = stream.window(3, step=1)

        results = await windowed.collect()
        assert len(results) == 3
        assert results[0] == [1, 2, 3]
        assert results[1] == [2, 3, 4]
        assert results[2] == [3, 4, 5]

    @pytest.mark.asyncio
    async def test_reduce(self) -> None:
        """Test reduce operation."""
        stream = AsyncStream([1, 2, 3, 4, 5])
        total = await stream.reduce(lambda acc, x: acc + x, 0)

        assert total == 15

    @pytest.mark.asyncio
    async def test_count(self) -> None:
        """Test count operation."""
        stream = AsyncStream([1, 2, 3, 4, 5])
        count = await stream.count()

        assert count == 5


@pytest.mark.unit
class TestAsyncQueue:
    """Test AsyncQueue functionality."""

    @pytest.mark.asyncio
    async def test_put_get(self) -> None:
        """Test basic put/get operations."""
        queue = AsyncQueue[int]()

        await queue.put(1)
        await queue.put(2)
        await queue.put(3)

        assert await queue.get() == 1
        assert await queue.get() == 2
        assert await queue.get() == 3

    @pytest.mark.asyncio
    async def test_maxsize(self) -> None:
        """Test queue with maximum size."""
        queue = AsyncQueue[int](maxsize=2)

        await queue.put(1)
        await queue.put(2)

        # Queue should be full
        assert queue.full()

    @pytest.mark.asyncio
    async def test_stream(self) -> None:
        """Test queue streaming."""
        queue = AsyncQueue[int]()

        # Producer
        async def producer() -> None:
            for i in range(5):
                await queue.put(i)
                await asyncio.sleep(0.01)
            await queue.close()

        # Start producer
        asyncio.create_task(producer())

        # Consume via stream
        results = []
        async for item in queue.stream():
            results.append(item)
            if len(results) >= 5:
                break

        assert results == [0, 1, 2, 3, 4]


@pytest.mark.unit
class TestAsyncPipeline:
    """Test AsyncPipeline functionality."""

    @pytest.mark.asyncio
    async def test_single_stage(self) -> None:
        """Test pipeline with single stage."""
        pipeline = AsyncPipeline()
        pipeline.add_stage(async_map(lambda x: x * 2))

        results = await pipeline.process([1, 2, 3, 4, 5])
        assert results == [2, 4, 6, 8, 10]

    @pytest.mark.asyncio
    async def test_multiple_stages(self) -> None:
        """Test pipeline with multiple stages."""
        pipeline = AsyncPipeline()
        pipeline.add_stage(async_map(lambda x: x * 2))
        pipeline.add_stage(async_filter(lambda x: x > 5))

        results = await pipeline.process([1, 2, 3, 4, 5])
        assert results == [6, 8, 10]

    @pytest.mark.asyncio
    async def test_batch_stage(self) -> None:
        """Test pipeline with batch stage."""
        pipeline = AsyncPipeline()
        pipeline.add_stage(async_batch(2))

        results = await pipeline.process([1, 2, 3, 4, 5])
        assert results == [[1, 2], [3, 4], [5]]

    @pytest.mark.asyncio
    async def test_window_stage(self) -> None:
        """Test pipeline with window stage."""
        pipeline = AsyncPipeline()
        pipeline.add_stage(async_window(3, step=2))

        results = await pipeline.process([1, 2, 3, 4, 5])
        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_pipeline_composition(self) -> None:
        """Test composing pipelines."""
        pipeline1 = AsyncPipeline()
        pipeline1.add_stage(async_map(lambda x: x * 2))

        pipeline2 = AsyncPipeline()
        pipeline2.add_stage(async_filter(lambda x: x > 5))

        composed = pipeline1.compose(pipeline2)

        results = await composed.process([1, 2, 3, 4, 5])
        assert results == [6, 8, 10]


@pytest.mark.unit
class TestUtilityFunctions:
    """Test stream utility functions."""

    @pytest.mark.asyncio
    async def test_async_map_function(self) -> None:
        """Test async_map utility function."""
        async def source():
            for i in range(5):
                yield i

        mapper = async_map(lambda x: x * 2)
        mapped = mapper(source())

        results = []
        async for item in mapped:
            results.append(item)

        assert results == [0, 2, 4, 6, 8]

    @pytest.mark.asyncio
    async def test_async_filter_function(self) -> None:
        """Test async_filter utility function."""
        async def source():
            for i in range(5):
                yield i

        filterer = async_filter(lambda x: x % 2 == 0)
        filtered = filterer(source())

        results = []
        async for item in filtered:
            results.append(item)

        assert results == [0, 2, 4]

    @pytest.mark.asyncio
    async def test_async_batch_function(self) -> None:
        """Test async_batch utility function."""
        async def source():
            for i in range(5):
                yield i

        batcher = async_batch(2)
        batched = batcher(source())

        results = []
        async for batch in batched:
            results.append(batch)

        assert results == [[0, 1], [2, 3], [4]]

    @pytest.mark.asyncio
    async def test_async_merge(self) -> None:
        """Test async_merge utility."""
        async def source1():
            for i in range(3):
                await asyncio.sleep(0.01)
                yield i

        async def source2():
            for i in range(3, 6):
                await asyncio.sleep(0.01)
                yield i

        results = []
        async for item in async_merge(source1(), source2()):
            results.append(item)

        # Should have all items (order may vary due to concurrency)
        assert sorted(results) == [0, 1, 2, 3, 4, 5]
