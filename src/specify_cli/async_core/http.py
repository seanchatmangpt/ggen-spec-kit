"""
specify_cli.async_core.http - Async HTTP Client and Connection Pooling
=======================================================================

Comprehensive async HTTP client with retry logic, circuit breaker, and connection pooling.

This module provides:

* **AsyncHTTPClient**: High-performance async HTTP client with httpx
* **RetryPolicy**: Configurable retry with exponential backoff
* **CircuitBreaker**: Circuit breaker pattern for fault tolerance
* **Connection Pooling**: Automatic connection reuse and management
* **Streaming**: Request/response streaming support

Features
--------
* Async HTTP operations (GET, POST, PUT, DELETE, etc.)
* Automatic retries with exponential backoff
* Circuit breaker for fault tolerance
* Connection pooling and keep-alive
* Request/response streaming
* Progress tracking for uploads/downloads
* Comprehensive error handling
* Performance metrics and monitoring

Examples
--------
    >>> from specify_cli.async_core.http import AsyncHTTPClient, RetryPolicy
    >>>
    >>> async def fetch_api():
    ...     async with AsyncHTTPClient() as client:
    ...         response = await client.get("https://api.example.com/data")
    ...         return response.json()
    >>>
    >>> # With retry policy
    >>> retry_policy = RetryPolicy(max_retries=5, backoff_factor=2.0)
    >>> async with AsyncHTTPClient(retry_policy=retry_policy) as client:
    ...     data = await client.get("https://api.example.com/data")

See Also
--------
- :mod:`specify_cli.async_core.runner` : Task execution and scheduling
- :mod:`specify_cli.core.telemetry` : Telemetry and observability
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any

import httpx

from specify_cli.core.telemetry import metric_counter, metric_histogram, span

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

__all__ = [
    "AsyncHTTPClient",
    "CircuitBreaker",
    "CircuitState",
    "RetryPolicy",
    "async_batch_requests",
    "async_download",
    "async_upload",
]

_log = logging.getLogger("specify_cli.async_core.http")


# ============================================================================
# Circuit Breaker State
# ============================================================================


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, rejecting requests
    HALF_OPEN = "half_open"  # Testing recovery


# ============================================================================
# Retry Policy Configuration
# ============================================================================


@dataclass
class RetryPolicy:
    """
    Retry policy configuration with exponential backoff.

    Parameters
    ----------
    max_retries : int
        Maximum number of retry attempts.
    backoff_factor : float
        Exponential backoff multiplier.
    retry_statuses : set[int]
        HTTP status codes to retry.
    retry_exceptions : tuple
        Exception types to retry.

    Examples
    --------
    >>> policy = RetryPolicy(
    ...     max_retries=5,
    ...     backoff_factor=2.0,
    ...     retry_statuses={408, 429, 500, 502, 503, 504}
    ... )
    """

    max_retries: int = 3
    backoff_factor: float = 1.0
    retry_statuses: set[int] = None  # type: ignore[assignment]
    retry_exceptions: tuple[type[Exception], ...] = (
        httpx.TimeoutException,
        httpx.NetworkError,
    )

    def __post_init__(self) -> None:
        """Initialize default retry statuses."""
        if self.retry_statuses is None:
            self.retry_statuses = {408, 429, 500, 502, 503, 504}

    def get_backoff_delay(self, attempt: int) -> float:
        """
        Calculate backoff delay for a retry attempt.

        Parameters
        ----------
        attempt : int
            Current retry attempt (0-indexed).

        Returns
        -------
        float
            Delay in seconds.
        """
        return self.backoff_factor * (2**attempt)  # type: ignore[no-any-return]


# ============================================================================
# Circuit Breaker Implementation
# ============================================================================


class CircuitBreaker:
    """
    Circuit breaker for fault tolerance.

    Parameters
    ----------
    failure_threshold : int
        Number of failures before opening circuit.
    recovery_timeout : float
        Time to wait before attempting recovery.
    success_threshold : int
        Successes needed to close circuit.

    Examples
    --------
    >>> breaker = CircuitBreaker(
    ...     failure_threshold=5,
    ...     recovery_timeout=60.0,
    ...     success_threshold=2
    ... )
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        success_threshold: int = 2,
    ) -> None:
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = 0.0

    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        return self._state

    async def call(self, func: Any, *args: Any, **kwargs: Any) -> Any:
        """
        Execute function through circuit breaker.

        Parameters
        ----------
        func : Callable[..., Any][..., Any]
            Function to execute.
        *args : Any
            Positional arguments.
        **kwargs : Any
            Keyword arguments.

        Returns
        -------
        Any
            Function result.

        Raises
        ------
        RuntimeError
            If circuit is open.
        """
        # Check if circuit is open
        if self._state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if time.time() - self._last_failure_time >= self.recovery_timeout:
                self._state = CircuitState.HALF_OPEN
                self._success_count = 0
                metric_counter("async.circuit_breaker.half_open")(1)
            else:
                metric_counter("async.circuit_breaker.rejected")(1)
                raise RuntimeError("Circuit breaker is OPEN")

        try:
            # Execute function
            result = await func(*args, **kwargs)

            # Record success
            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self.success_threshold:
                    self._state = CircuitState.CLOSED
                    self._failure_count = 0
                    metric_counter("async.circuit_breaker.closed")(1)

            return result

        except Exception:
            # Record failure
            self._failure_count += 1
            self._last_failure_time = time.time()

            if self._state == CircuitState.HALF_OPEN or self._failure_count >= self.failure_threshold:
                self._state = CircuitState.OPEN
                metric_counter("async.circuit_breaker.opened")(1)

            raise


# ============================================================================
# Async HTTP Client
# ============================================================================


class AsyncHTTPClient:
    """
    High-performance async HTTP client with retry and circuit breaker.

    Parameters
    ----------
    retry_policy : RetryPolicy, optional
        Retry configuration.
    circuit_breaker : CircuitBreaker, optional
        Circuit breaker for fault tolerance.
    timeout : float, optional
        Request timeout in seconds.
    max_connections : int, optional
        Maximum number of connections.
    enable_metrics : bool, optional
        Enable performance metrics.

    Examples
    --------
    >>> async with AsyncHTTPClient() as client:
    ...     response = await client.get("https://api.example.com")
    ...     data = response.json()
    """

    def __init__(
        self,
        retry_policy: RetryPolicy | None = None,
        circuit_breaker: CircuitBreaker | None = None,
        timeout: float = 30.0,
        max_connections: int = 100,
        enable_metrics: bool = True,
    ) -> None:
        self.retry_policy = retry_policy or RetryPolicy()
        self.circuit_breaker = circuit_breaker
        self.timeout = timeout
        self.max_connections = max_connections
        self.enable_metrics = enable_metrics

        # Initialize httpx client (will be created in __aenter__)
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> AsyncHTTPClient:
        """Async context manager entry."""
        self._client = httpx.AsyncClient(
            timeout=self.timeout,
            limits=httpx.Limits(
                max_connections=self.max_connections,
                max_keepalive_connections=self.max_connections // 2,
            ),
        )
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()

    async def _request_with_retry(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """Execute HTTP request with retry logic."""
        last_exception = None

        for attempt in range(self.retry_policy.max_retries + 1):
            try:
                # Execute request
                if self._client is None:
                    raise RuntimeError("Client not initialized. Use async with statement.")

                response = await self._client.request(method, url, **kwargs)

                # Check if response should be retried
                if response.status_code not in self.retry_policy.retry_statuses:
                    return response

                last_exception = httpx.HTTPStatusError(
                    f"Status {response.status_code}",
                    request=response.request,
                    response=response,
                )

            except self.retry_policy.retry_exceptions as e:
                last_exception = e  # type: ignore[assignment]

            # Calculate backoff delay
            if attempt < self.retry_policy.max_retries:
                delay = self.retry_policy.get_backoff_delay(attempt)
                _log.warning(
                    f"Request to {url} failed (attempt {attempt + 1}). "
                    f"Retrying in {delay:.2f}s..."
                )
                await asyncio.sleep(delay)

                if self.enable_metrics:
                    metric_counter("async.http.retry")(1, {"method": method})  # type: ignore[call-arg]

        # All retries exhausted
        if self.enable_metrics:
            metric_counter("async.http.failed")(1, {"method": method})  # type: ignore[call-arg]

        raise last_exception or RuntimeError("Request failed")

    async def request(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Execute HTTP request with circuit breaker and retry.

        Parameters
        ----------
        method : str
            HTTP method (GET, POST, etc.).
        url : str
            Request URL.
        **kwargs : Any
            Additional request parameters.

        Returns
        -------
        httpx.Response
            HTTP response.
        """
        start_time = time.time()

        with span(
            "async.http.request",
            http_method=method,
            http_url=url,
        ):
            try:
                # Execute with circuit breaker if configured
                if self.circuit_breaker:
                    response = await self.circuit_breaker.call(
                        self._request_with_retry,
                        method,
                        url,
                        **kwargs,
                    )
                else:
                    response = await self._request_with_retry(method, url, **kwargs)

                # Record metrics
                duration = time.time() - start_time
                if self.enable_metrics:
                    metric_counter("async.http.request.success")(1, method=method)
                    metric_histogram("async.http.request.duration")(duration)

                return response  # type: ignore[no-any-return]

            except Exception:
                duration = time.time() - start_time
                if self.enable_metrics:
                    metric_counter("async.http.request.error")(1, method=method)
                    metric_histogram("async.http.request.duration")(duration)
                raise

    async def get(self, url: str, **kwargs: Any) -> httpx.Response:
        """Execute GET request."""
        return await self.request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs: Any) -> httpx.Response:
        """Execute POST request."""
        return await self.request("POST", url, **kwargs)

    async def put(self, url: str, **kwargs: Any) -> httpx.Response:
        """Execute PUT request."""
        return await self.request("PUT", url, **kwargs)

    async def delete(self, url: str, **kwargs: Any) -> httpx.Response:
        """Execute DELETE request."""
        return await self.request("DELETE", url, **kwargs)

    async def stream(self, method: str, url: str, **kwargs: Any) -> AsyncIterator[bytes]:
        """
        Stream response data.

        Parameters
        ----------
        method : str
            HTTP method.
        url : str
            Request URL.
        **kwargs : Any
            Additional request parameters.

        Yields
        ------
        bytes
            Response data chunks.
        """
        if self._client is None:
            raise RuntimeError("Client not initialized")

        async with self._client.stream(method, url, **kwargs) as response:
            async for chunk in response.aiter_bytes():
                yield chunk


# ============================================================================
# Utility Functions
# ============================================================================


async def async_download(
    url: str,
    destination: Path,
    chunk_size: int = 8192,
    client: AsyncHTTPClient | None = None,
) -> None:
    """
    Download file asynchronously.

    Parameters
    ----------
    url : str
        URL to download from.
    destination : Path
        Destination file path.
    chunk_size : int, optional
        Download chunk size.
    client : AsyncHTTPClient, optional
        HTTP client to use.
    """
    close_client = client is None
    if client is None:
        client = AsyncHTTPClient()
        await client.__aenter__()

    try:
        with destination.open("wb") as f:
            async for chunk in client.stream("GET", url):
                f.write(chunk)
                metric_counter("async.download.bytes")(len(chunk))
    finally:
        if close_client and client:
            await client.__aexit__()


async def async_upload(
    url: str,
    file_path: Path,
    client: AsyncHTTPClient | None = None,
) -> httpx.Response:
    """
    Upload file asynchronously.

    Parameters
    ----------
    url : str
        Upload URL.
    file_path : Path
        File to upload.
    client : AsyncHTTPClient, optional
        HTTP client to use.

    Returns
    -------
    httpx.Response
        Upload response.
    """
    close_client = client is None
    if client is None:
        client = AsyncHTTPClient()
        await client.__aenter__()

    try:
        with file_path.open("rb") as f:
            files = {"file": f}
            return await client.post(url, files=files)
    finally:
        if close_client and client:
            await client.__aexit__()


async def async_batch_requests(
    urls: list[str],
    max_concurrent: int = 10,
) -> list[httpx.Response]:
    """
    Execute batch HTTP requests concurrently.

    Parameters
    ----------
    urls : list[str]
        URLs to fetch.
    max_concurrent : int, optional
        Maximum concurrent requests.

    Returns
    -------
    list[httpx.Response]
        Responses from all URLs.
    """
    async with AsyncHTTPClient() as client:
        semaphore = asyncio.Semaphore(max_concurrent)

        async def fetch_with_semaphore(url: str) -> httpx.Response:
            async with semaphore:
                return await client.get(url)

        return await asyncio.gather(*[fetch_with_semaphore(url) for url in urls])
