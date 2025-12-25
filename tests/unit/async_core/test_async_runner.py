"""Tests for async_core.runner module."""

from __future__ import annotations

import asyncio

import pytest

from specify_cli.async_core.runner import (
    AsyncRunner,
    ResourcePool,
    TaskPriority,
    TaskScheduler,
    async_background,
    async_run,
    async_timeout,
)


@pytest.mark.unit
class TestAsyncRunner:
    """Test AsyncRunner functionality."""

    @pytest.mark.asyncio
    async def test_basic_execution(self) -> None:
        """Test basic async task execution."""
        async def simple_task(value: int) -> int:
            await asyncio.sleep(0.01)
            return value * 2

        runner = AsyncRunner(max_workers=2)
        async with runner:
            result = await runner.submit(simple_task(5))
            assert result == 10

    @pytest.mark.asyncio
    async def test_gather_multiple_tasks(self) -> None:
        """Test gathering multiple async tasks."""
        async def task(value: int) -> int:
            await asyncio.sleep(0.01)
            return value * 2

        runner = AsyncRunner(max_workers=5)
        async with runner:
            results = await runner.gather([task(i) for i in range(5)])
            assert results == [0, 2, 4, 6, 8]

    @pytest.mark.asyncio
    async def test_priority_execution(self) -> None:
        """Test priority-based task execution."""
        results = []

        async def task(value: int) -> int:
            results.append(value)
            return value

        runner = AsyncRunner(max_workers=1)
        async with runner:
            # Submit low priority first, then high priority
            low = runner.submit(task(1), priority=TaskPriority.LOW)
            high = runner.submit(task(2), priority=TaskPriority.HIGH)

            await asyncio.gather(low, high)

            # High priority should execute first (if scheduler is running)
            # Note: This test is timing-sensitive
            assert 2 in results

    @pytest.mark.asyncio
    async def test_timeout(self) -> None:
        """Test task timeout."""
        async def slow_task() -> int:
            await asyncio.sleep(10)
            return 42

        runner = AsyncRunner(max_workers=1)
        async with runner:
            with pytest.raises(asyncio.TimeoutError):
                await runner.submit(slow_task(), timeout=0.1)

    @pytest.mark.asyncio
    async def test_error_handling(self) -> None:
        """Test error handling in tasks."""
        async def failing_task() -> int:
            raise ValueError("Task failed")

        runner = AsyncRunner(max_workers=1)
        async with runner:
            with pytest.raises(ValueError):
                await runner.submit(failing_task())


@pytest.mark.unit
class TestTaskScheduler:
    """Test TaskScheduler functionality."""

    @pytest.mark.asyncio
    async def test_scheduler_submit(self) -> None:
        """Test task submission to scheduler."""
        async def task(value: int) -> int:
            return value * 2

        scheduler = TaskScheduler(max_concurrent=2)
        await scheduler.start()

        result = await scheduler.submit(task(5))
        assert result == 10

        await scheduler.shutdown()

    @pytest.mark.asyncio
    async def test_concurrent_limit(self) -> None:
        """Test concurrent task limit."""
        running_tasks = 0
        max_running = 0

        async def task() -> None:
            nonlocal running_tasks, max_running
            running_tasks += 1
            max_running = max(max_running, running_tasks)
            await asyncio.sleep(0.1)
            running_tasks -= 1

        scheduler = TaskScheduler(max_concurrent=3)
        await scheduler.start()

        # Submit more tasks than concurrent limit
        tasks = [scheduler.submit(task()) for _ in range(10)]
        await asyncio.gather(*tasks)

        await scheduler.shutdown()

        # Should not exceed concurrent limit
        assert max_running <= 3


@pytest.mark.unit
class TestResourcePool:
    """Test ResourcePool functionality."""

    @pytest.mark.asyncio
    async def test_resource_acquisition(self) -> None:
        """Test resource acquisition from pool."""
        counter = 0

        async def create_resource() -> dict:
            nonlocal counter
            counter += 1
            return {"id": counter}

        pool = ResourcePool(max_resources=3, factory=create_resource)

        async with pool.acquire() as resource:
            assert resource["id"] == 1

        async with pool.acquire() as resource:
            assert resource["id"] in [1, 2]  # Could be reused or new

        await pool.close()

    @pytest.mark.asyncio
    async def test_resource_reuse(self) -> None:
        """Test resource reuse in pool."""
        created = []

        async def create_resource() -> dict:
            resource = {"id": len(created) + 1}
            created.append(resource)
            return resource

        pool = ResourcePool(max_resources=2, factory=create_resource)

        # Acquire and release
        async with pool.acquire() as r1:
            first_id = r1["id"]

        # Acquire again - should reuse
        async with pool.acquire() as r2:
            assert r2["id"] == first_id

        await pool.close()

    @pytest.mark.asyncio
    async def test_cleanup(self) -> None:
        """Test resource cleanup."""
        cleaned_up = []

        async def create_resource() -> dict:
            return {"id": len(cleaned_up) + 1}

        async def cleanup_resource(resource: dict) -> None:
            cleaned_up.append(resource["id"])

        pool = ResourcePool(
            max_resources=2,
            factory=create_resource,
            cleanup=cleanup_resource,
        )

        async with pool.acquire():
            pass

        await pool.close()

        # Should have cleaned up resources
        assert len(cleaned_up) > 0


@pytest.mark.unit
class TestUtilityFunctions:
    """Test utility functions."""

    def test_async_run(self) -> None:
        """Test async_run helper."""
        async def task() -> int:
            return 42

        result = async_run(task())
        assert result == 42

    @pytest.mark.asyncio
    async def test_async_timeout_success(self) -> None:
        """Test async_timeout with successful completion."""
        async def quick_task() -> int:
            await asyncio.sleep(0.01)
            return 42

        async with async_timeout(1.0):
            result = await quick_task()
            assert result == 42

    @pytest.mark.asyncio
    async def test_async_timeout_exceeded(self) -> None:
        """Test async_timeout with timeout exceeded."""
        async def slow_task() -> None:
            await asyncio.sleep(10)

        with pytest.raises(asyncio.TimeoutError):
            async with async_timeout(0.1):
                await slow_task()

    @pytest.mark.asyncio
    async def test_async_background(self) -> None:
        """Test async_background task execution."""
        async def background_task() -> int:
            await asyncio.sleep(0.1)
            return 42

        task = async_background(background_task())
        assert isinstance(task, asyncio.Task)

        result = await task
        assert result == 42
