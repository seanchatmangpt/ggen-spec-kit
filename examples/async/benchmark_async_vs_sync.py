#!/usr/bin/env python3
"""
Performance Benchmark: Async vs Sync Operations
================================================

Comprehensive benchmarks comparing async and sync implementations.

Usage:
    python examples/async/benchmark_async_vs_sync.py

Results are displayed in a rich table with performance metrics.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any

from rich.console import Console
from rich.table import Table

from specify_cli.async_core import AsyncHTTPClient, AsyncRunner, AsyncStream

console = Console()


# ============================================================================
# Benchmark Utilities
# ============================================================================


def benchmark(name: str, func: Any, *args: Any, iterations: int = 100) -> dict[str, Any]:
    """
    Benchmark a function execution.

    Parameters
    ----------
    name : str
        Benchmark name.
    func : Callable
        Function to benchmark.
    *args : Any
        Function arguments.
    iterations : int, optional
        Number of iterations.

    Returns
    -------
    dict[str, Any]
        Benchmark results.
    """
    times = []

    for _ in range(iterations):
        start = time.perf_counter()

        if asyncio.iscoroutinefunction(func):
            asyncio.run(func(*args))
        else:
            func(*args)

        duration = time.perf_counter() - start
        times.append(duration)

    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)

    return {
        "name": name,
        "avg_ms": avg_time * 1000,
        "min_ms": min_time * 1000,
        "max_ms": max_time * 1000,
        "total_s": sum(times),
    }


# ============================================================================
# Task Execution Benchmarks
# ============================================================================


def sync_sequential_tasks(n: int = 10) -> None:
    """Execute tasks sequentially (sync)."""
    def task(x: int) -> int:
        time.sleep(0.01)  # Simulate I/O
        return x * 2

    results = [task(i) for i in range(n)]
    assert len(results) == n


async def async_parallel_tasks(n: int = 10) -> None:
    """Execute tasks in parallel (async)."""
    async def task(x: int) -> int:
        await asyncio.sleep(0.01)  # Simulate async I/O
        return x * 2

    runner = AsyncRunner(max_workers=n)
    async with runner:
        results = await runner.gather([task(i) for i in range(n)])
        assert len(results) == n


# ============================================================================
# Stream Processing Benchmarks
# ============================================================================


def sync_stream_processing(n: int = 100) -> None:
    """Process data stream synchronously."""
    data = list(range(n))

    # Map and filter
    results = [x * 2 for x in data if x % 2 == 0]
    assert len(results) > 0


async def async_stream_processing(n: int = 100) -> None:
    """Process data stream asynchronously."""
    stream = AsyncStream(list(range(n)))

    # Map and filter
    results = await stream.map(lambda x: x * 2).filter(lambda x: x % 4 == 0).collect()
    assert len(results) > 0


# ============================================================================
# HTTP Request Benchmarks
# ============================================================================


def sync_http_requests(n: int = 10) -> None:
    """Execute HTTP requests synchronously (simulated)."""
    def fetch(url: str) -> dict:
        time.sleep(0.1)  # Simulate network latency
        return {"url": url, "data": "response"}

    urls = [f"https://api.example.com/{i}" for i in range(n)]
    results = [fetch(url) for url in urls]
    assert len(results) == n


async def async_http_requests(n: int = 10) -> None:
    """Execute HTTP requests asynchronously (simulated)."""
    async def fetch(url: str) -> dict:
        await asyncio.sleep(0.1)  # Simulate async network latency
        return {"url": url, "data": "response"}

    urls = [f"https://api.example.com/{i}" for i in range(n)]
    runner = AsyncRunner(max_workers=n)

    async with runner:
        results = await runner.gather([fetch(url) for url in urls])
        assert len(results) == n


# ============================================================================
# Data Batching Benchmarks
# ============================================================================


def sync_batch_processing(n: int = 1000, batch_size: int = 10) -> None:
    """Process data in batches synchronously."""
    data = list(range(n))
    batches = [data[i : i + batch_size] for i in range(0, len(data), batch_size)]

    results = []
    for batch in batches:
        results.extend([x * 2 for x in batch])

    assert len(results) == n


async def async_batch_processing(n: int = 1000, batch_size: int = 10) -> None:
    """Process data in batches asynchronously."""
    stream = AsyncStream(list(range(n)))
    batched = stream.batch(batch_size)

    results = []
    async for batch in batched:
        results.extend([x * 2 for x in batch])

    assert len(results) == n


# ============================================================================
# Main Benchmark Runner
# ============================================================================


def run_benchmarks() -> None:
    """Run all benchmarks and display results."""
    console.print("\n[bold cyan]Async vs Sync Performance Benchmarks[/bold cyan]\n")

    benchmarks = [
        # Task execution
        ("Sequential Tasks (Sync)", sync_sequential_tasks, 10),
        ("Parallel Tasks (Async)", async_parallel_tasks, 10),
        # Stream processing
        ("Stream Processing (Sync)", sync_stream_processing, 100),
        ("Stream Processing (Async)", async_stream_processing, 100),
        # HTTP requests
        ("HTTP Requests (Sync)", sync_http_requests, 5),
        ("HTTP Requests (Async)", async_http_requests, 5),
        # Batch processing
        ("Batch Processing (Sync)", sync_batch_processing, 1000),
        ("Batch Processing (Async)", async_batch_processing, 1000),
    ]

    results = []

    for name, func, arg in benchmarks:
        console.print(f"Running: [yellow]{name}[/yellow]...")
        result = benchmark(name, func, arg, iterations=10)
        results.append(result)

    # Display results table
    table = Table(title="Benchmark Results")
    table.add_column("Benchmark", style="cyan", no_wrap=True)
    table.add_column("Avg (ms)", justify="right", style="green")
    table.add_column("Min (ms)", justify="right", style="blue")
    table.add_column("Max (ms)", justify="right", style="red")
    table.add_column("Total (s)", justify="right", style="magenta")

    for result in results:
        table.add_row(
            result["name"],
            f"{result['avg_ms']:.2f}",
            f"{result['min_ms']:.2f}",
            f"{result['max_ms']:.2f}",
            f"{result['total_s']:.3f}",
        )

    console.print("\n")
    console.print(table)
    console.print("\n")

    # Calculate speedup for async vs sync
    console.print("[bold green]Performance Analysis:[/bold green]\n")

    # Task execution speedup
    sync_tasks = next(r for r in results if "Sequential Tasks" in r["name"])
    async_tasks = next(r for r in results if "Parallel Tasks" in r["name"])
    speedup = sync_tasks["avg_ms"] / async_tasks["avg_ms"]
    console.print(f"Task Execution Speedup: [bold]{speedup:.2f}x[/bold]")

    # HTTP requests speedup
    sync_http = next(r for r in results if "HTTP Requests (Sync)" in r["name"])
    async_http = next(r for r in results if "HTTP Requests (Async)" in r["name"])
    speedup = sync_http["avg_ms"] / async_http["avg_ms"]
    console.print(f"HTTP Requests Speedup: [bold]{speedup:.2f}x[/bold]")

    console.print("\n[dim]Note: Async provides significant speedup for I/O-bound operations[/dim]\n")


if __name__ == "__main__":
    run_benchmarks()
