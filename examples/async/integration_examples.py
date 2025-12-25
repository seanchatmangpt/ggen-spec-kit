#!/usr/bin/env python3
"""
Async Integration Examples
===========================

Comprehensive examples demonstrating async/await integration in specify-cli.

Examples:
1. Async HTTP client with retry and circuit breaker
2. Async file processing pipeline
3. Async stream transformations
4. Background task management
5. Resource pooling
6. Priority-based task scheduling
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from rich.console import Console

from specify_cli.async_core import (
    AsyncHTTPClient,
    AsyncPipeline,
    AsyncRunner,
    AsyncStream,
    CircuitBreaker,
    RetryPolicy,
    TaskPriority,
    async_batch,
    async_filter,
    async_map,
    async_read_file,
    async_write_file,
)

console = Console()


# ============================================================================
# Example 1: Async HTTP Client with Retry and Circuit Breaker
# ============================================================================


async def example_http_client() -> None:
    """Demonstrate async HTTP client with retry and circuit breaker."""
    console.print("\n[bold cyan]Example 1: Async HTTP Client[/bold cyan]\n")

    # Configure retry policy
    retry_policy = RetryPolicy(
        max_retries=5,
        backoff_factor=2.0,
        retry_statuses={408, 429, 500, 502, 503, 504},
    )

    # Configure circuit breaker
    circuit_breaker = CircuitBreaker(
        failure_threshold=5,
        recovery_timeout=60.0,
        success_threshold=2,
    )

    # Create async HTTP client
    async with AsyncHTTPClient(
        retry_policy=retry_policy,
        circuit_breaker=circuit_breaker,
        timeout=30.0,
    ) as client:
        # Example: Fetch API data (simulated)
        console.print("[yellow]Fetching API data...[/yellow]")

        # In real usage, you would fetch actual URLs
        # response = await client.get("https://api.example.com/data")
        # data = response.json()

        console.print("[green]✓[/green] HTTP client configured with retry and circuit breaker")


# ============================================================================
# Example 2: Async File Processing Pipeline
# ============================================================================


async def example_file_pipeline() -> None:
    """Demonstrate async file processing pipeline."""
    console.print("\n[bold cyan]Example 2: Async File Processing Pipeline[/bold cyan]\n")

    # Create sample data
    sample_data = "\n".join([f"Line {i}: Sample data" for i in range(100)])

    # Write sample file
    temp_file = Path("/tmp/async_example.txt")
    await async_write_file(temp_file, sample_data)
    console.print(f"[green]✓[/green] Created sample file: {temp_file}")

    # Read and process file asynchronously
    from specify_cli.async_core.file import AsyncFileReader

    reader = AsyncFileReader(temp_file)

    # Stream and process lines
    processed_lines = []
    async for line in reader.stream_lines():
        # Process each line asynchronously
        processed = line.strip().upper()
        processed_lines.append(processed)

    console.print(f"[green]✓[/green] Processed {len(processed_lines)} lines asynchronously")

    # Clean up
    temp_file.unlink()


# ============================================================================
# Example 3: Async Stream Transformations
# ============================================================================


async def example_stream_transformations() -> None:
    """Demonstrate async stream transformations."""
    console.print("\n[bold cyan]Example 3: Async Stream Transformations[/bold cyan]\n")

    # Create data stream
    data = list(range(1, 101))
    stream = AsyncStream(data)

    # Chain transformations
    console.print("[yellow]Transforming stream...[/yellow]")

    result = (
        stream.map(lambda x: x * 2)  # Double each value
        .filter(lambda x: x % 10 == 0)  # Keep multiples of 10
        .batch(5)  # Batch into groups of 5
    )

    # Collect results
    batches = await result.collect()

    console.print(f"[green]✓[/green] Created {len(batches)} batches from stream")
    console.print(f"[dim]First batch: {batches[0]}[/dim]")


# ============================================================================
# Example 4: Pipeline Composition
# ============================================================================


async def example_pipeline_composition() -> None:
    """Demonstrate async pipeline composition."""
    console.print("\n[bold cyan]Example 4: Pipeline Composition[/bold cyan]\n")

    # Create processing pipeline
    pipeline = AsyncPipeline()

    # Add stages
    pipeline.add_stage(async_map(lambda x: x * 2))
    pipeline.add_stage(async_filter(lambda x: x > 50))
    pipeline.add_stage(async_batch(10))

    # Process data
    data = list(range(1, 101))
    console.print(f"[yellow]Processing {len(data)} items through pipeline...[/yellow]")

    results = await pipeline.process(data)

    console.print(f"[green]✓[/green] Pipeline produced {len(results)} batches")


# ============================================================================
# Example 5: Priority-Based Task Scheduling
# ============================================================================


async def example_priority_scheduling() -> None:
    """Demonstrate priority-based task scheduling."""
    console.print("\n[bold cyan]Example 5: Priority-Based Task Scheduling[/bold cyan]\n")

    async def task(name: str, priority: str) -> str:
        await asyncio.sleep(0.1)
        return f"Completed: {name} (priority: {priority})"

    runner = AsyncRunner(max_workers=3)

    async with runner:
        console.print("[yellow]Submitting tasks with different priorities...[/yellow]")

        # Submit tasks with different priorities
        tasks = [
            runner.submit(task("Critical Task", "CRITICAL"), priority=TaskPriority.CRITICAL),
            runner.submit(task("Normal Task", "NORMAL"), priority=TaskPriority.NORMAL),
            runner.submit(task("Low Task", "LOW"), priority=TaskPriority.LOW),
            runner.submit(task("High Task", "HIGH"), priority=TaskPriority.HIGH),
        ]

        # Wait for all tasks
        results = await asyncio.gather(*tasks)

        for result in results:
            console.print(f"[green]✓[/green] {result}")


# ============================================================================
# Example 6: Concurrent HTTP Requests
# ============================================================================


async def example_concurrent_requests() -> None:
    """Demonstrate concurrent HTTP requests."""
    console.print("\n[bold cyan]Example 6: Concurrent HTTP Requests[/bold cyan]\n")

    async def fetch_data(url: str) -> dict:
        """Simulate fetching data from URL."""
        await asyncio.sleep(0.1)  # Simulate network latency
        return {"url": url, "status": "success"}

    # Create URLs
    urls = [f"https://api.example.com/endpoint/{i}" for i in range(10)]

    console.print(f"[yellow]Fetching {len(urls)} URLs concurrently...[/yellow]")

    # Fetch all URLs concurrently
    runner = AsyncRunner(max_workers=5)

    async with runner:
        results = await runner.gather([fetch_data(url) for url in urls])

    console.print(f"[green]✓[/green] Fetched {len(results)} URLs successfully")


# ============================================================================
# Example 7: Background Task Management
# ============================================================================


async def example_background_tasks() -> None:
    """Demonstrate background task management."""
    console.print("\n[bold cyan]Example 7: Background Task Management[/bold cyan]\n")

    from specify_cli.async_core.runner import async_background

    async def background_monitor() -> str:
        """Long-running background task."""
        for i in range(5):
            await asyncio.sleep(0.2)
        return "Monitoring complete"

    console.print("[yellow]Starting background task...[/yellow]")

    # Start background task
    task = async_background(background_monitor())

    # Do other work
    console.print("[yellow]Doing other work while background task runs...[/yellow]")
    await asyncio.sleep(0.5)

    # Wait for background task
    result = await task
    console.print(f"[green]✓[/green] Background task: {result}")


# ============================================================================
# Example 8: Resource Pool Usage
# ============================================================================


async def example_resource_pool() -> None:
    """Demonstrate resource pool usage."""
    console.print("\n[bold cyan]Example 8: Resource Pool Usage[/bold cyan]\n")

    from specify_cli.async_core.runner import ResourcePool

    # Create resource pool (e.g., database connections)
    connection_id = 0

    async def create_connection() -> dict:
        """Simulate creating a database connection."""
        nonlocal connection_id
        connection_id += 1
        await asyncio.sleep(0.1)  # Simulate connection time
        return {"id": connection_id, "active": True}

    async def close_connection(conn: dict) -> None:
        """Simulate closing a connection."""
        conn["active"] = False

    pool = ResourcePool(
        max_resources=5,
        factory=create_connection,
        cleanup=close_connection,
    )

    console.print("[yellow]Acquiring resources from pool...[/yellow]")

    # Use resources from pool
    async with pool.acquire() as conn1:
        console.print(f"[green]✓[/green] Acquired connection: {conn1['id']}")

    async with pool.acquire() as conn2:
        console.print(f"[green]✓[/green] Acquired connection: {conn2['id']}")

    await pool.close()
    console.print("[green]✓[/green] Pool closed and resources cleaned up")


# ============================================================================
# Main Runner
# ============================================================================


async def run_all_examples() -> None:
    """Run all async integration examples."""
    console.print("\n[bold magenta]Async Integration Examples[/bold magenta]")
    console.print("[dim]Demonstrating async/await capabilities in specify-cli[/dim]\n")

    examples = [
        example_http_client,
        example_file_pipeline,
        example_stream_transformations,
        example_pipeline_composition,
        example_priority_scheduling,
        example_concurrent_requests,
        example_background_tasks,
        example_resource_pool,
    ]

    for example in examples:
        await example()
        await asyncio.sleep(0.5)  # Small delay between examples

    console.print("\n[bold green]All examples completed successfully![/bold green]\n")


if __name__ == "__main__":
    asyncio.run(run_all_examples())
