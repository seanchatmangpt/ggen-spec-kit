"""Tests for async_core.http module."""

from __future__ import annotations

import asyncio
from pathlib import Path

import httpx
import pytest

from specify_cli.async_core.http import (
    AsyncHTTPClient,
    CircuitBreaker,
    CircuitState,
    RetryPolicy,
    async_batch_requests,
)


@pytest.mark.unit
class TestRetryPolicy:
    """Test RetryPolicy functionality."""

    def test_default_configuration(self) -> None:
        """Test default retry policy configuration."""
        policy = RetryPolicy()

        assert policy.max_retries == 3
        assert policy.backoff_factor == 1.0
        assert 500 in policy.retry_statuses
        assert 502 in policy.retry_statuses

    def test_custom_configuration(self) -> None:
        """Test custom retry policy configuration."""
        policy = RetryPolicy(
            max_retries=5,
            backoff_factor=2.0,
            retry_statuses={408, 503},
        )

        assert policy.max_retries == 5
        assert policy.backoff_factor == 2.0
        assert policy.retry_statuses == {408, 503}

    def test_backoff_calculation(self) -> None:
        """Test backoff delay calculation."""
        policy = RetryPolicy(backoff_factor=2.0)

        assert policy.get_backoff_delay(0) == 2.0
        assert policy.get_backoff_delay(1) == 4.0
        assert policy.get_backoff_delay(2) == 8.0


@pytest.mark.unit
class TestCircuitBreaker:
    """Test CircuitBreaker functionality."""

    @pytest.mark.asyncio
    async def test_initial_state(self) -> None:
        """Test circuit breaker initial state."""
        breaker = CircuitBreaker()
        assert breaker.state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_successful_call(self) -> None:
        """Test successful call through circuit breaker."""
        breaker = CircuitBreaker()

        async def successful_func() -> int:
            return 42

        result = await breaker.call(successful_func)
        assert result == 42
        assert breaker.state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_failure_opens_circuit(self) -> None:
        """Test that failures open the circuit."""
        breaker = CircuitBreaker(failure_threshold=3)

        async def failing_func() -> int:
            raise RuntimeError("Failed")

        # Fail enough times to open circuit
        for _ in range(3):
            with pytest.raises(RuntimeError):
                await breaker.call(failing_func)

        assert breaker.state == CircuitState.OPEN

    @pytest.mark.asyncio
    async def test_open_circuit_rejects_calls(self) -> None:
        """Test that open circuit rejects calls."""
        breaker = CircuitBreaker(failure_threshold=1)

        async def failing_func() -> int:
            raise RuntimeError("Failed")

        # Open the circuit
        with pytest.raises(RuntimeError):
            await breaker.call(failing_func)

        # Circuit should be open and reject calls
        assert breaker.state == CircuitState.OPEN
        with pytest.raises(RuntimeError, match="Circuit breaker is OPEN"):
            await breaker.call(failing_func)


@pytest.mark.unit
@pytest.mark.asyncio
class TestAsyncHTTPClient:
    """Test AsyncHTTPClient functionality."""

    async def test_client_initialization(self) -> None:
        """Test client initialization and cleanup."""
        async with AsyncHTTPClient() as client:
            assert client._client is not None

    async def test_get_request_mock(self, mocker) -> None:
        """Test GET request with mocked httpx."""
        # Mock httpx.AsyncClient
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}

        mock_client = mocker.Mock()
        mock_client.request = mocker.AsyncMock(return_value=mock_response)
        mock_client.aclose = mocker.AsyncMock()

        mocker.patch("httpx.AsyncClient", return_value=mock_client)

        async with AsyncHTTPClient() as client:
            response = await client.get("https://api.example.com/test")
            assert response.status_code == 200

    async def test_retry_on_failure(self, mocker) -> None:
        """Test retry logic on failures."""
        call_count = 0

        async def mock_request(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise httpx.NetworkError("Connection failed")
            mock_response = mocker.Mock()
            mock_response.status_code = 200
            return mock_response

        mock_client = mocker.Mock()
        mock_client.request = mock_request
        mock_client.aclose = mocker.AsyncMock()

        mocker.patch("httpx.AsyncClient", return_value=mock_client)

        retry_policy = RetryPolicy(max_retries=3, backoff_factor=0.01)
        async with AsyncHTTPClient(retry_policy=retry_policy) as client:
            response = await client.get("https://api.example.com/test")
            assert response.status_code == 200
            assert call_count == 3  # Failed twice, succeeded on third

    async def test_timeout_configuration(self, mocker) -> None:
        """Test timeout configuration."""
        captured_timeout = None

        def capture_timeout(*args, **kwargs):
            nonlocal captured_timeout
            captured_timeout = kwargs.get("timeout")
            mock = mocker.Mock()
            mock.aclose = mocker.AsyncMock()
            return mock

        mocker.patch("httpx.AsyncClient", side_effect=capture_timeout)

        async with AsyncHTTPClient(timeout=60.0):
            pass

        assert captured_timeout == 60.0

    async def test_post_request(self, mocker) -> None:
        """Test POST request."""
        mock_response = mocker.Mock()
        mock_response.status_code = 201

        mock_client = mocker.Mock()
        mock_client.request = mocker.AsyncMock(return_value=mock_response)
        mock_client.aclose = mocker.AsyncMock()

        mocker.patch("httpx.AsyncClient", return_value=mock_client)

        async with AsyncHTTPClient() as client:
            response = await client.post(
                "https://api.example.com/test",
                json={"data": "test"},
            )
            assert response.status_code == 201


@pytest.mark.unit
@pytest.mark.asyncio
class TestUtilityFunctions:
    """Test HTTP utility functions."""

    async def test_batch_requests(self, mocker) -> None:
        """Test batch HTTP requests."""
        mock_responses = []
        for i in range(3):
            mock_resp = mocker.Mock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {"id": i}
            mock_responses.append(mock_resp)

        call_count = 0

        async def mock_request(*args, **kwargs):
            nonlocal call_count
            response = mock_responses[call_count]
            call_count += 1
            return response

        mock_client = mocker.Mock()
        mock_client.request = mock_request
        mock_client.aclose = mocker.AsyncMock()

        mocker.patch("httpx.AsyncClient", return_value=mock_client)

        urls = [
            "https://api.example.com/1",
            "https://api.example.com/2",
            "https://api.example.com/3",
        ]

        responses = await async_batch_requests(urls, max_concurrent=2)
        assert len(responses) == 3
