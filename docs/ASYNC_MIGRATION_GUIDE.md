# Async/Await Migration Guide

Guide for migrating existing synchronous code to async/await patterns in specify-cli.

## Table of Contents

1. [Overview](#overview)
2. [When to Use Async](#when-to-use-async)
3. [Migration Patterns](#migration-patterns)
4. [Step-by-Step Migration](#step-by-step-migration)
5. [Common Pitfalls](#common-pitfalls)
6. [Performance Optimization](#performance-optimization)
7. [Testing Async Code](#testing-async-code)

## Overview

The async_core package provides comprehensive async/await infrastructure for high-performance parallel operations in specify-cli.

### Benefits of Async

- **Concurrency**: Execute multiple I/O-bound operations simultaneously
- **Performance**: 5-10x speedup for I/O-bound operations
- **Resource Efficiency**: Better CPU and memory utilization
- **Scalability**: Handle thousands of concurrent operations

### When NOT to Use Async

- CPU-bound operations (use multiprocessing instead)
- Simple sequential operations
- Code that doesn't benefit from parallelism

## When to Use Async

### Good Use Cases

✅ **HTTP API Calls**
```python
# Multiple API requests in parallel
async with AsyncHTTPClient() as client:
    results = await asyncio.gather(
        client.get("https://api1.example.com"),
        client.get("https://api2.example.com"),
        client.get("https://api3.example.com"),
    )
```

✅ **File I/O Operations**
```python
# Read multiple files concurrently
from specify_cli.async_core import async_read_file

files = ["file1.txt", "file2.txt", "file3.txt"]
contents = await asyncio.gather(*[async_read_file(f) for f in files])
```

✅ **Database Queries**
```python
# Parallel database queries
async with ResourcePool(max_resources=10, factory=create_db_connection) as pool:
    async with pool.acquire() as conn:
        results = await conn.execute(query)
```

✅ **Stream Processing**
```python
# Process data streams asynchronously
stream = AsyncStream(data)
results = await stream.map(transform).filter(predicate).collect()
```

### Bad Use Cases

❌ **CPU-Intensive Calculations**
```python
# DON'T use async for CPU-bound work
def calculate_fibonacci(n):  # Use regular function
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)
```

❌ **Simple Sequential Operations**
```python
# DON'T use async for simple operations
# BEFORE (Good - no async needed)
result = process_data(data)

# AFTER (Bad - unnecessary complexity)
result = await async_process_data(data)  # No benefit
```

## Migration Patterns

### Pattern 1: Convert Sync Function to Async

**Before (Sync):**
```python
def fetch_data(url: str) -> dict:
    import requests
    response = requests.get(url)
    return response.json()
```

**After (Async):**
```python
async def fetch_data(url: str) -> dict:
    from specify_cli.async_core import AsyncHTTPClient

    async with AsyncHTTPClient() as client:
        response = await client.get(url)
        return response.json()
```

### Pattern 2: Parallel Execution

**Before (Sync - Sequential):**
```python
def fetch_all(urls: list[str]) -> list[dict]:
    results = []
    for url in urls:
        data = fetch_data(url)  # Blocking
        results.append(data)
    return results
```

**After (Async - Parallel):**
```python
async def fetch_all(urls: list[str]) -> list[dict]:
    from specify_cli.async_core import AsyncRunner

    runner = AsyncRunner(max_workers=10)
    async with runner:
        results = await runner.gather([fetch_data(url) for url in urls])
    return results
```

### Pattern 3: File Operations

**Before (Sync):**
```python
def process_files(file_paths: list[Path]) -> list[str]:
    contents = []
    for path in file_paths:
        with open(path) as f:
            contents.append(f.read())
    return contents
```

**After (Async):**
```python
async def process_files(file_paths: list[Path]) -> list[str]:
    from specify_cli.async_core import async_read_file

    contents = await asyncio.gather(*[async_read_file(path) for path in file_paths])
    return contents
```

### Pattern 4: Stream Processing

**Before (Sync):**
```python
def process_stream(data: list[int]) -> list[int]:
    return [x * 2 for x in data if x > 10]
```

**After (Async):**
```python
async def process_stream(data: list[int]) -> list[int]:
    from specify_cli.async_core import AsyncStream

    stream = AsyncStream(data)
    return await stream.map(lambda x: x * 2).filter(lambda x: x > 20).collect()
```

## Step-by-Step Migration

### Step 1: Identify Async Opportunities

1. **Find I/O-bound operations**
   - HTTP requests
   - File reading/writing
   - Database queries
   - Network operations

2. **Find parallel opportunities**
   - Multiple independent operations
   - Batch processing
   - Data pipelines

### Step 2: Add Async Infrastructure

```python
# Add async imports
from specify_cli.async_core import (
    AsyncRunner,
    AsyncHTTPClient,
    AsyncStream,
    async_read_file,
    async_write_file,
)
```

### Step 3: Convert Functions

1. **Add `async` keyword**
```python
def my_function():  # Before
    pass

async def my_function():  # After
    pass
```

2. **Add `await` to async calls**
```python
result = sync_call()  # Before
result = await async_call()  # After
```

3. **Update return types**
```python
from collections.abc import Coroutine

def func() -> int:  # Before
    return 42

async def func() -> int:  # After (async functions return coroutines)
    return 42
```

### Step 4: Update Callers

```python
# Before
result = my_function()

# After
result = await my_function()  # In async context
# OR
result = asyncio.run(my_function())  # In sync context
```

### Step 5: Add Error Handling

```python
async def fetch_with_retry(url: str) -> dict:
    from specify_cli.async_core import AsyncHTTPClient, RetryPolicy

    retry_policy = RetryPolicy(max_retries=3, backoff_factor=2.0)

    async with AsyncHTTPClient(retry_policy=retry_policy) as client:
        try:
            response = await client.get(url)
            return response.json()
        except Exception as e:
            # Handle errors
            raise
```

## Common Pitfalls

### Pitfall 1: Forgetting `await`

❌ **Wrong:**
```python
async def bad_example():
    result = async_function()  # Missing await!
    print(result)  # Prints coroutine object, not result
```

✅ **Correct:**
```python
async def good_example():
    result = await async_function()  # Properly awaited
    print(result)  # Prints actual result
```

### Pitfall 2: Blocking in Async Functions

❌ **Wrong:**
```python
async def bad_example():
    time.sleep(1)  # Blocks entire event loop!
```

✅ **Correct:**
```python
async def good_example():
    await asyncio.sleep(1)  # Non-blocking
```

### Pitfall 3: Not Using Context Managers

❌ **Wrong:**
```python
async def bad_example():
    client = AsyncHTTPClient()
    response = await client.get(url)
    # Client not properly closed!
```

✅ **Correct:**
```python
async def good_example():
    async with AsyncHTTPClient() as client:
        response = await client.get(url)
    # Client properly closed
```

### Pitfall 4: Sequential Instead of Parallel

❌ **Wrong:**
```python
async def bad_example(urls):
    results = []
    for url in urls:
        result = await fetch(url)  # Sequential!
        results.append(result)
    return results
```

✅ **Correct:**
```python
async def good_example(urls):
    # Parallel execution
    results = await asyncio.gather(*[fetch(url) for url in urls])
    return results
```

## Performance Optimization

### 1. Use Connection Pooling

```python
from specify_cli.async_core import AsyncHTTPClient

# Connection pool reuses connections
async with AsyncHTTPClient(max_connections=100) as client:
    # Multiple requests reuse connections
    await client.get(url1)
    await client.get(url2)
```

### 2. Batch Operations

```python
from specify_cli.async_core import AsyncStream

stream = AsyncStream(large_dataset)
batches = stream.batch(100)  # Process in batches of 100

async for batch in batches:
    await process_batch(batch)
```

### 3. Set Worker Limits

```python
from specify_cli.async_core import AsyncRunner

# Limit concurrent workers to avoid overwhelming resources
runner = AsyncRunner(max_workers=10)
async with runner:
    results = await runner.gather(tasks)
```

### 4. Use Circuit Breakers

```python
from specify_cli.async_core import CircuitBreaker

breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60.0)

async with AsyncHTTPClient(circuit_breaker=breaker) as client:
    # Circuit breaker protects against cascading failures
    response = await client.get(url)
```

## Testing Async Code

### Basic Async Test

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await my_async_function()
    assert result == expected_value
```

### Testing with Mocks

```python
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_with_mock(mocker):
    mock_client = AsyncMock()
    mock_client.get.return_value = {"data": "test"}

    mocker.patch("specify_cli.async_core.AsyncHTTPClient", return_value=mock_client)

    result = await fetch_data("https://api.example.com")
    assert result["data"] == "test"
```

### Testing Error Handling

```python
@pytest.mark.asyncio
async def test_error_handling():
    with pytest.raises(ValueError):
        await failing_async_function()
```

## Migration Checklist

- [ ] Identify I/O-bound operations
- [ ] Add async imports
- [ ] Convert functions to async
- [ ] Add await keywords
- [ ] Update callers
- [ ] Add error handling
- [ ] Add retry logic
- [ ] Configure connection pooling
- [ ] Add circuit breakers
- [ ] Write async tests
- [ ] Run performance benchmarks
- [ ] Update documentation

## Next Steps

1. Review [ASYNC_PATTERNS.md](ASYNC_PATTERNS.md) for advanced patterns
2. Run benchmarks: `python examples/async/benchmark_async_vs_sync.py`
3. Explore examples: `python examples/async/integration_examples.py`
4. Read API documentation in [async_core/](../src/specify_cli/async_core/)

## Resources

- [Python asyncio documentation](https://docs.python.org/3/library/asyncio.html)
- [Real Python: Async IO in Python](https://realpython.com/async-io-python/)
- [HTTPX Async Client](https://www.python-httpx.org/async/)
