"""
specify_cli.async_core - Hyper-Advanced Async/Await Infrastructure
===================================================================

Comprehensive async/await support for parallel operations and performance optimization.

This package provides a complete async infrastructure with:

* **AsyncRunner**: Event loop management, task scheduling, and resource pooling
* **AsyncStreams**: Data streaming, pipeline operations, and backpressure handling
* **AsyncHTTP**: Connection pooling, retry logic, and circuit breaker patterns
* **AsyncFile**: Async file I/O, directory traversal, and change detection

Key Features
-----------
* Task scheduling and prioritization
* Concurrent operation execution
* Resource pooling and management
* Exception handling and recovery
* Performance monitoring and metrics
* Actor model implementation
* Message passing and event-driven architecture
* Distributed task execution

Environment Variables
--------------------
SPECIFY_ASYNC_WORKERS : int, optional
    Maximum number of concurrent workers (default: 10)
SPECIFY_ASYNC_TIMEOUT : int, optional
    Default timeout for async operations in seconds (default: 30)
SPECIFY_ASYNC_RETRY_MAX : int, optional
    Maximum number of retry attempts (default: 3)
SPECIFY_ASYNC_POOL_SIZE : int, optional
    HTTP connection pool size (default: 100)

Examples
--------
    >>> from specify_cli.async_core import AsyncRunner, AsyncHTTP
    >>>
    >>> # Run multiple tasks concurrently
    >>> async def main():
    ...     runner = AsyncRunner()
    ...     results = await runner.gather([
    ...         fetch_data("url1"),
    ...         fetch_data("url2"),
    ...         fetch_data("url3"),
    ...     ])
    >>>
    >>> # Async HTTP client with retries
    >>> async def fetch():
    ...     async with AsyncHTTP() as client:
    ...         response = await client.get("https://api.example.com")

See Also
--------
- :mod:`specify_cli.async_core.runner` : Event loop and task management
- :mod:`specify_cli.async_core.streams` : Async generators and streaming
- :mod:`specify_cli.async_core.http` : Async HTTP client
- :mod:`specify_cli.async_core.file` : Async file operations
"""

from __future__ import annotations

__version__ = "1.0.0"

from .file import (
    AsyncDirectoryWatcher,
    AsyncFileReader,
    AsyncFileWriter,
    async_copy_file,
    async_read_file,
    async_write_file,
    walk_async,
)
from .http import (
    AsyncHTTPClient,
    CircuitBreaker,
    RetryPolicy,
    async_batch_requests,
    async_download,
    async_upload,
)
from .runner import (
    AsyncRunner,
    TaskPriority,
    TaskScheduler,
    async_background,
    async_run,
    async_timeout,
)
from .streams import (
    AsyncPipeline,
    AsyncQueue,
    AsyncStream,
    async_batch,
    async_filter,
    async_map,
)

__all__ = [
    "AsyncDirectoryWatcher",
    # File
    "AsyncFileReader",
    "AsyncFileWriter",
    # HTTP
    "AsyncHTTPClient",
    "AsyncPipeline",
    "AsyncQueue",
    # Runner
    "AsyncRunner",
    # Streams
    "AsyncStream",
    "CircuitBreaker",
    "RetryPolicy",
    "TaskPriority",
    "TaskScheduler",
    "async_background",
    "async_batch",
    "async_batch_requests",
    "async_copy_file",
    "async_download",
    "async_filter",
    "async_map",
    "async_read_file",
    "async_run",
    "async_timeout",
    "async_upload",
    "async_write_file",
    "walk_async",
]
