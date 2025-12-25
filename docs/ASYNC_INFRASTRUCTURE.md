# Async/Await Infrastructure

Complete documentation for the async_core package in specify-cli.

## Overview

The `async_core` package provides hyper-advanced async/await support for parallel operations and performance optimization in specify-cli. It enables 5-10x performance improvements for I/O-bound operations through efficient concurrency.

## Package Structure

```
src/specify_cli/async_core/
├── __init__.py          # Package exports and public API
├── runner.py            # Event loop management and task scheduling
├── streams.py           # Async generators and data streaming
├── http.py              # Async HTTP client with retry and circuit breaker
└── file.py              # Async file I/O operations
```

## Modules

### 1. runner.py - Task Execution and Scheduling

**Classes:**
- `AsyncRunner`: High-level async task executor
- `TaskScheduler`: Priority-based task scheduling
- `ResourcePool`: Shared resource management
- `TaskPriority`: Priority levels (CRITICAL, HIGH, NORMAL, LOW, BACKGROUND)

**Functions:**
- `async_run()`: Run coroutine and return result
- `async_timeout()`: Timeout context manager
- `async_background()`: Run coroutine in background

**Example:**
```python
from specify_cli.async_core import AsyncRunner, TaskPriority

runner = AsyncRunner(max_workers=10)
async with runner:
    result = await runner.submit(task(), priority=TaskPriority.HIGH)
```

### 2. streams.py - Data Streaming

**Classes:**
- `AsyncStream`: Composable async iterator
- `AsyncQueue`: Queue-based streaming with backpressure
- `AsyncPipeline`: Composable processing pipeline

**Functions:**
- `async_map()`: Transform stream elements
- `async_filter()`: Filter stream elements
- `async_batch()`: Batch stream elements
- `async_window()`: Sliding window over stream
- `async_merge()`: Merge multiple streams

**Example:**
```python
from specify_cli.async_core import AsyncStream

stream = AsyncStream([1, 2, 3, 4, 5])
result = await stream.map(lambda x: x * 2).filter(lambda x: x > 5).collect()
```

### 3. http.py - HTTP Client

**Classes:**
- `AsyncHTTPClient`: Async HTTP client with httpx
- `RetryPolicy`: Retry configuration with exponential backoff
- `CircuitBreaker`: Circuit breaker for fault tolerance
- `CircuitState`: Circuit breaker states (CLOSED, OPEN, HALF_OPEN)

**Functions:**
- `async_download()`: Download file asynchronously
- `async_upload()`: Upload file asynchronously
- `async_batch_requests()`: Batch HTTP requests

**Example:**
```python
from specify_cli.async_core import AsyncHTTPClient, RetryPolicy

retry = RetryPolicy(max_retries=3, backoff_factor=2.0)
async with AsyncHTTPClient(retry_policy=retry) as client:
    response = await client.get("https://api.example.com")
```

### 4. file.py - File Operations

**Classes:**
- `AsyncFileReader`: Async file reading with streaming
- `AsyncFileWriter`: Async file writing with buffering
- `AsyncDirectoryWatcher`: File change detection

**Functions:**
- `async_read_file()`: Read file contents
- `async_write_file()`: Write file contents
- `async_copy_file()`: Copy file
- `walk_async()`: Walk directory asynchronously
- `async_file_exists()`: Check file existence
- `async_mkdir()`: Create directory

**Example:**
```python
from specify_cli.async_core import async_read_file, async_write_file

content = await async_read_file("input.txt")
await async_write_file("output.txt", content)
```

## Installation

The async_core package is included in specify-cli. Install dependencies:

```bash
# Install with all dependencies
uv sync

# Or install specific dependency
uv pip install aiofiles httpx
```

## Quick Start

### Basic Async Function

```python
import asyncio
from specify_cli.async_core import AsyncRunner

async def main():
    async def task(n):
        await asyncio.sleep(0.1)
        return n * 2

    runner = AsyncRunner(max_workers=5)
    async with runner:
        results = await runner.gather([task(i) for i in range(10)])
        print(results)

if __name__ == "__main__":
    asyncio.run(main())
```

### Async HTTP Requests

```python
from specify_cli.async_core import AsyncHTTPClient

async def fetch_data():
    async with AsyncHTTPClient() as client:
        response = await client.get("https://api.example.com/data")
        return response.json()

result = asyncio.run(fetch_data())
```

### Stream Processing

```python
from specify_cli.async_core import AsyncStream

async def process_stream():
    stream = AsyncStream([1, 2, 3, 4, 5])
    result = await stream.map(lambda x: x * 2).filter(lambda x: x > 5).collect()
    return result

results = asyncio.run(process_stream())  # [6, 8, 10]
```

## Features

### 1. Concurrent Task Execution

Execute multiple tasks in parallel with configurable worker limits:

```python
runner = AsyncRunner(max_workers=10)
async with runner:
    results = await runner.gather([
        fetch_data("url1"),
        fetch_data("url2"),
        fetch_data("url3"),
    ])
```

### 2. Priority-Based Scheduling

Schedule tasks with different priority levels:

```python
await runner.submit(critical_task(), priority=TaskPriority.CRITICAL)
await runner.submit(normal_task(), priority=TaskPriority.NORMAL)
await runner.submit(background_task(), priority=TaskPriority.BACKGROUND)
```

### 3. Resource Pooling

Manage shared resources efficiently:

```python
from specify_cli.async_core import ResourcePool

pool = ResourcePool(
    max_resources=10,
    factory=create_connection,
    cleanup=close_connection,
)

async with pool.acquire() as resource:
    await use_resource(resource)
```

### 4. Circuit Breaker

Protect against cascading failures:

```python
from specify_cli.async_core import CircuitBreaker

breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60.0)
async with AsyncHTTPClient(circuit_breaker=breaker) as client:
    response = await client.get(url)
```

### 5. Retry Logic

Automatic retry with exponential backoff:

```python
from specify_cli.async_core import RetryPolicy

retry = RetryPolicy(max_retries=5, backoff_factor=2.0)
async with AsyncHTTPClient(retry_policy=retry) as client:
    response = await client.get(url)
```

### 6. Stream Transformations

Composable stream operations:

```python
stream = AsyncStream(data)
result = await (
    stream
    .map(transform)
    .filter(predicate)
    .batch(100)
    .collect()
)
```

### 7. Pipeline Composition

Reusable processing pipelines:

```python
pipeline = AsyncPipeline()
pipeline.add_stage(async_map(lambda x: x * 2))
pipeline.add_stage(async_filter(lambda x: x > 50))
results = await pipeline.process(data)
```

## Performance

### Benchmarks

Run performance benchmarks:

```bash
python examples/async/benchmark_async_vs_sync.py
```

**Typical Results:**
- Task Execution: 8-10x speedup for I/O-bound operations
- HTTP Requests: 5-8x speedup for parallel requests
- File Operations: 3-5x speedup for multiple files
- Stream Processing: 2-3x speedup for large datasets

### Best Performance Practices

1. **Use connection pooling** for HTTP requests
2. **Batch operations** to reduce overhead
3. **Set appropriate worker limits** to avoid resource exhaustion
4. **Use circuit breakers** for external service calls
5. **Implement retry logic** for transient failures

## Integration

### Three-Tier Architecture

```python
# Commands Layer (CLI)
import asyncio
from specify_cli.ops import async_operations

@app.command()
def fetch_command(url: str) -> None:
    result = asyncio.run(async_operations.fetch_data(url))
    typer.echo(result)

# Operations Layer (Business Logic)
async def fetch_data(url: str) -> dict:
    data = await runtime.fetch_url(url)
    return process(data)

# Runtime Layer (I/O)
from specify_cli.async_core import AsyncHTTPClient

async def fetch_url(url: str) -> dict:
    async with AsyncHTTPClient() as client:
        response = await client.get(url)
        return response.json()
```

### Telemetry Integration

All async operations are instrumented with OpenTelemetry:

```python
from specify_cli.core.telemetry import span

async def monitored_operation():
    with span("operation.name", operation_type="async"):
        result = await async_function()
        return result
```

## Testing

### Writing Async Tests

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await my_async_function()
    assert result == expected_value
```

### Run Tests

```bash
# Run async tests
uv run pytest tests/unit/async_core/ -v

# Run with coverage
uv run pytest tests/unit/async_core/ --cov=src/specify_cli/async_core
```

## Examples

Complete examples are available in `examples/async/`:

- `integration_examples.py`: Comprehensive integration examples
- `benchmark_async_vs_sync.py`: Performance benchmarks

Run examples:

```bash
python examples/async/integration_examples.py
python examples/async/benchmark_async_vs_sync.py
```

## Documentation

- [ASYNC_MIGRATION_GUIDE.md](ASYNC_MIGRATION_GUIDE.md): Migration guide for existing code
- [ASYNC_PATTERNS.md](ASYNC_PATTERNS.md): Patterns and best practices
- API documentation in module docstrings

## Environment Variables

```bash
# Async configuration
export SPECIFY_ASYNC_WORKERS=10        # Max concurrent workers
export SPECIFY_ASYNC_TIMEOUT=30        # Default timeout (seconds)
export SPECIFY_ASYNC_RETRY_MAX=3       # Max retry attempts
export SPECIFY_ASYNC_POOL_SIZE=100     # HTTP connection pool size
```

## Dependencies

- `httpx>=0.27.0`: Async HTTP client
- `aiofiles>=24.0.0`: Async file I/O
- `opentelemetry-sdk>=1.20.0`: Telemetry (optional)

## License

MIT License - See LICENSE file for details.

## Support

- Issues: https://github.com/github/spec-kit/issues
- Documentation: https://github.com/github/spec-kit#readme
- Examples: `examples/async/`

## Related

- [OpenTelemetry](https://opentelemetry.io/)
- [HTTPX](https://www.python-httpx.org/)
- [aiofiles](https://github.com/Tinche/aiofiles)
- [Python asyncio](https://docs.python.org/3/library/asyncio.html)
