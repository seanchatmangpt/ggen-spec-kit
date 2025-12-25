# Async/Await Patterns and Best Practices

Comprehensive guide to async/await patterns in specify-cli.

## Table of Contents

1. [Core Patterns](#core-patterns)
2. [Advanced Patterns](#advanced-patterns)
3. [Best Practices](#best-practices)
4. [Architecture Integration](#architecture-integration)
5. [Performance Patterns](#performance-patterns)
6. [Error Handling](#error-handling)

## Core Patterns

### Pattern: Async Function Definition

```python
async def fetch_data(url: str) -> dict:
    """
    Async function that fetches data from URL.

    Parameters
    ----------
    url : str
        URL to fetch from.

    Returns
    -------
    dict
        Fetched data.
    """
    from specify_cli.async_core import AsyncHTTPClient

    async with AsyncHTTPClient() as client:
        response = await client.get(url)
        return response.json()
```

**Key Points:**
- Use `async def` to define async functions
- Use `await` to call async functions
- Type hints work the same as sync functions
- Docstrings follow NumPy style (same as sync)

### Pattern: Concurrent Execution with gather()

```python
async def fetch_multiple(urls: list[str]) -> list[dict]:
    """Fetch multiple URLs concurrently."""
    from specify_cli.async_core import AsyncHTTPClient

    async with AsyncHTTPClient() as client:
        # All requests execute in parallel
        results = await asyncio.gather(*[client.get(url) for url in urls])
        return [r.json() for r in results]
```

**Use When:**
- Multiple independent async operations
- All operations must complete
- Order of results matters

### Pattern: Task Runner for Complex Scheduling

```python
async def scheduled_processing() -> None:
    """Process tasks with priority scheduling."""
    from specify_cli.async_core import AsyncRunner, TaskPriority

    runner = AsyncRunner(max_workers=10)

    async with runner:
        # Submit high-priority task
        critical = await runner.submit(
            critical_task(),
            priority=TaskPriority.CRITICAL,
        )

        # Submit normal tasks
        results = await runner.gather([
            normal_task_1(),
            normal_task_2(),
            normal_task_3(),
        ])
```

**Use When:**
- Need priority-based execution
- Want to limit concurrent workers
- Complex task scheduling required

### Pattern: Stream Processing

```python
async def process_data_stream(data: list[int]) -> list[int]:
    """Process data using async stream operations."""
    from specify_cli.async_core import AsyncStream

    stream = AsyncStream(data)

    # Chain operations
    result = (
        stream
        .map(lambda x: x * 2)          # Transform
        .filter(lambda x: x > 10)       # Filter
        .batch(10)                      # Batch
    )

    return await result.collect()
```

**Use When:**
- Processing large datasets
- Need transformation pipelines
- Want lazy evaluation

### Pattern: Pipeline Composition

```python
async def composed_pipeline() -> list[Any]:
    """Compose multiple processing stages into pipeline."""
    from specify_cli.async_core import (
        AsyncPipeline,
        async_map,
        async_filter,
        async_batch,
    )

    # Define pipeline stages
    pipeline = AsyncPipeline()
    pipeline.add_stage(async_map(lambda x: x * 2))
    pipeline.add_stage(async_filter(lambda x: x > 50))
    pipeline.add_stage(async_batch(10))

    # Process data through pipeline
    data = list(range(1, 101))
    return await pipeline.process(data)
```

**Use When:**
- Reusable processing stages
- Complex data transformations
- Need composable pipelines

## Advanced Patterns

### Pattern: Resource Pooling

```python
async def use_connection_pool() -> None:
    """Use resource pool for database connections."""
    from specify_cli.async_core import ResourcePool

    async def create_connection() -> dict:
        """Create database connection."""
        # Simulate connection creation
        return {"conn": "database", "id": 1}

    async def close_connection(conn: dict) -> None:
        """Close database connection."""
        conn["closed"] = True

    # Create pool
    pool = ResourcePool(
        max_resources=10,
        factory=create_connection,
        cleanup=close_connection,
    )

    try:
        # Acquire connection from pool
        async with pool.acquire() as conn:
            # Use connection
            result = await execute_query(conn, "SELECT * FROM users")
    finally:
        await pool.close()
```

**Use When:**
- Managing expensive resources (DB connections, file handles)
- Need resource reuse
- Want automatic cleanup

### Pattern: Circuit Breaker for Fault Tolerance

```python
async def resilient_api_call(url: str) -> dict:
    """Make resilient API call with circuit breaker."""
    from specify_cli.async_core import AsyncHTTPClient, CircuitBreaker

    # Configure circuit breaker
    breaker = CircuitBreaker(
        failure_threshold=5,      # Open after 5 failures
        recovery_timeout=60.0,     # Try recovery after 60s
        success_threshold=2,       # Close after 2 successes
    )

    async with AsyncHTTPClient(circuit_breaker=breaker) as client:
        response = await client.get(url)
        return response.json()
```

**Use When:**
- Calling unreliable external services
- Need to prevent cascading failures
- Want automatic recovery

### Pattern: Retry with Exponential Backoff

```python
async def fetch_with_retry(url: str) -> dict:
    """Fetch data with retry and exponential backoff."""
    from specify_cli.async_core import AsyncHTTPClient, RetryPolicy

    # Configure retry policy
    retry = RetryPolicy(
        max_retries=5,
        backoff_factor=2.0,  # 1s, 2s, 4s, 8s, 16s
        retry_statuses={408, 429, 500, 502, 503, 504},
    )

    async with AsyncHTTPClient(retry_policy=retry) as client:
        response = await client.get(url)
        return response.json()
```

**Use When:**
- Transient failures expected
- Network instability
- Rate limiting possible

### Pattern: Background Task Management

```python
async def run_with_background_tasks() -> None:
    """Run background tasks while doing other work."""
    from specify_cli.async_core.runner import async_background

    # Start background task
    monitor_task = async_background(monitor_system())

    # Do main work
    await process_main_work()

    # Wait for background task if needed
    result = await monitor_task
```

**Use When:**
- Long-running monitoring tasks
- Background data collection
- Concurrent system operations

### Pattern: Async Context Managers

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def managed_resource():
    """Create async context manager for resource."""
    # Setup
    resource = await create_resource()

    try:
        yield resource
    finally:
        # Cleanup
        await cleanup_resource(resource)

# Usage
async with managed_resource() as resource:
    await use_resource(resource)
```

**Use When:**
- Resource lifecycle management
- Guaranteed cleanup required
- Setup/teardown needed

## Best Practices

### 1. Always Use Context Managers

✅ **Good:**
```python
async with AsyncHTTPClient() as client:
    response = await client.get(url)
```

❌ **Bad:**
```python
client = AsyncHTTPClient()
response = await client.get(url)
# Client never closed!
```

### 2. Avoid Blocking Operations

✅ **Good:**
```python
await asyncio.sleep(1)  # Non-blocking
```

❌ **Bad:**
```python
time.sleep(1)  # Blocks entire event loop!
```

### 3. Handle Errors Properly

✅ **Good:**
```python
try:
    result = await risky_operation()
except SpecificError as e:
    # Handle specific error
    logger.error(f"Operation failed: {e}")
    raise
```

❌ **Bad:**
```python
result = await risky_operation()  # Unhandled errors
```

### 4. Use Timeouts

✅ **Good:**
```python
from specify_cli.async_core import async_timeout

async with async_timeout(30.0):
    result = await long_operation()
```

❌ **Bad:**
```python
result = await long_operation()  # Could hang forever
```

### 5. Prefer Gather for Multiple Operations

✅ **Good:**
```python
results = await asyncio.gather(
    operation1(),
    operation2(),
    operation3(),
)
```

❌ **Bad:**
```python
results = []
results.append(await operation1())  # Sequential!
results.append(await operation2())
results.append(await operation3())
```

### 6. Use Type Hints

✅ **Good:**
```python
async def fetch_data(url: str) -> dict[str, Any]:
    """Fetch data from URL."""
    async with AsyncHTTPClient() as client:
        response = await client.get(url)
        return response.json()
```

❌ **Bad:**
```python
async def fetch_data(url):  # No type hints
    async with AsyncHTTPClient() as client:
        response = await client.get(url)
        return response.json()
```

## Architecture Integration

### Three-Tier Architecture with Async

```
┌─────────────────────────────────────┐
│         Commands Layer              │
│  (CLI Interface - Thin Wrappers)    │
│                                     │
│  async def command():               │
│      result = await ops.operation() │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│       Operations Layer              │
│   (Pure Business Logic)             │
│                                     │
│  async def operation():             │
│      data = await runtime.fetch()   │
│      return process(data)           │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│         Runtime Layer               │
│  (I/O, HTTP, Subprocess)            │
│                                     │
│  async def fetch():                 │
│      async with AsyncHTTPClient()   │
│          return await client.get()  │
└─────────────────────────────────────┘
```

### Example: Async Commands

```python
# src/specify_cli/commands/async_example.py
import typer
from specify_cli.core.telemetry import span
from specify_cli.ops import async_ops

app = typer.Typer()

@app.command()
def fetch_data(url: str) -> None:
    """Fetch data from URL asynchronously."""
    import asyncio

    with span("command.fetch_data"):
        result = asyncio.run(async_ops.fetch_data(url))
        typer.echo(f"Fetched: {result}")
```

```python
# src/specify_cli/ops/async_ops.py
async def fetch_data(url: str) -> dict:
    """Fetch data from URL (ops layer)."""
    from specify_cli.runtime import async_runtime

    data = await async_runtime.fetch_url(url)
    return process_data(data)

def process_data(data: dict) -> dict:
    """Process data (pure function)."""
    return {"processed": data}
```

```python
# src/specify_cli/runtime/async_runtime.py
from specify_cli.async_core import AsyncHTTPClient

async def fetch_url(url: str) -> dict:
    """Fetch URL (runtime layer)."""
    async with AsyncHTTPClient() as client:
        response = await client.get(url)
        return response.json()
```

## Performance Patterns

### Pattern: Batching for Efficiency

```python
async def batch_process(items: list[Any]) -> list[Any]:
    """Process items in optimally-sized batches."""
    from specify_cli.async_core import AsyncStream

    stream = AsyncStream(items)
    batched = stream.batch(100)  # Optimal batch size

    results = []
    async for batch in batched:
        # Process batch concurrently
        batch_results = await asyncio.gather(*[process_item(item) for item in batch])
        results.extend(batch_results)

    return results
```

### Pattern: Connection Pooling

```python
async def efficient_http_calls(urls: list[str]) -> list[dict]:
    """Make HTTP calls with connection pooling."""
    from specify_cli.async_core import AsyncHTTPClient

    # Connection pool reuses connections
    async with AsyncHTTPClient(max_connections=100) as client:
        results = await asyncio.gather(*[client.get(url) for url in urls])
        return [r.json() for r in results]
```

### Pattern: Semaphore for Rate Limiting

```python
async def rate_limited_calls(urls: list[str], max_concurrent: int = 10) -> list[dict]:
    """Make HTTP calls with rate limiting."""
    from specify_cli.async_core import AsyncHTTPClient

    semaphore = asyncio.Semaphore(max_concurrent)

    async def fetch_with_limit(url: str) -> dict:
        async with semaphore:
            async with AsyncHTTPClient() as client:
                response = await client.get(url)
                return response.json()

    return await asyncio.gather(*[fetch_with_limit(url) for url in urls])
```

## Error Handling

### Pattern: Graceful Error Handling

```python
async def robust_operation() -> dict | None:
    """Perform operation with graceful error handling."""
    try:
        async with async_timeout(30.0):
            result = await risky_operation()
            return result

    except asyncio.TimeoutError:
        logger.warning("Operation timed out")
        return None

    except SpecificError as e:
        logger.error(f"Specific error: {e}")
        return None

    except Exception as e:
        logger.exception("Unexpected error")
        raise  # Re-raise unexpected errors
```

### Pattern: Error Recovery with Retries

```python
async def operation_with_recovery(url: str) -> dict:
    """Perform operation with automatic recovery."""
    from specify_cli.async_core import AsyncHTTPClient, RetryPolicy, CircuitBreaker

    retry = RetryPolicy(max_retries=3, backoff_factor=2.0)
    breaker = CircuitBreaker(failure_threshold=5)

    async with AsyncHTTPClient(retry_policy=retry, circuit_breaker=breaker) as client:
        try:
            response = await client.get(url)
            return response.json()
        except Exception as e:
            # Log and re-raise
            logger.error(f"Failed after retries: {e}")
            raise
```

### Pattern: Partial Failures in Gather

```python
async def handle_partial_failures(urls: list[str]) -> list[dict | Exception]:
    """Handle partial failures in concurrent operations."""
    from specify_cli.async_core import AsyncHTTPClient

    async def safe_fetch(url: str) -> dict | Exception:
        try:
            async with AsyncHTTPClient() as client:
                response = await client.get(url)
                return response.json()
        except Exception as e:
            return e  # Return exception instead of raising

    # return_exceptions=True to handle failures gracefully
    results = await asyncio.gather(
        *[safe_fetch(url) for url in urls],
        return_exceptions=True,
    )

    # Filter out errors
    successes = [r for r in results if not isinstance(r, Exception)]
    failures = [r for r in results if isinstance(r, Exception)]

    logger.info(f"Successes: {len(successes)}, Failures: {len(failures)}")

    return successes
```

## Summary

### Quick Reference

| Pattern | Use Case |
|---------|----------|
| `async def` + `await` | Basic async functions |
| `asyncio.gather()` | Concurrent operations |
| `AsyncRunner` | Task scheduling |
| `AsyncStream` | Data streaming |
| `AsyncPipeline` | Pipeline composition |
| `ResourcePool` | Resource management |
| `CircuitBreaker` | Fault tolerance |
| `RetryPolicy` | Error recovery |
| `async_timeout()` | Operation timeouts |
| `async with` | Resource cleanup |

### When to Use What

- **I/O-bound operations**: Use async/await
- **CPU-bound operations**: Use multiprocessing
- **Simple operations**: Keep synchronous
- **Multiple independent calls**: Use `asyncio.gather()`
- **Complex scheduling**: Use `AsyncRunner`
- **Data processing**: Use `AsyncStream`
- **External APIs**: Add retry + circuit breaker

### Next Steps

1. Review [ASYNC_MIGRATION_GUIDE.md](ASYNC_MIGRATION_GUIDE.md)
2. Run examples: `python examples/async/integration_examples.py`
3. Run benchmarks: `python examples/async/benchmark_async_vs_sync.py`
4. Explore API docs in [async_core/](../src/specify_cli/async_core/)
