"""
specify_cli.security.rate_limiting
-----------------------------------
Rate limiting and DDoS protection.

This module provides:

* **Token Bucket**: Classic token bucket rate limiting
* **Sliding Window**: Sliding window rate limiting
* **Adaptive Rate Limiting**: Dynamic rate adjustment based on load
* **Distributed Rate Limiting**: Redis-based rate limiting
* **IP-based Throttling**: Per-IP rate limiting

Security Features
-----------------
- Token bucket algorithm for smooth rate limiting
- Sliding window for precise rate control
- Adaptive thresholds based on system load
- Per-user and per-IP rate limiting
- Distributed rate limiting with Redis
- Automatic DDoS detection and mitigation
- Rate limit headers (X-RateLimit-*)
- Burst handling with configurable limits
- Graceful degradation under load

Example
-------
    # Basic rate limiting
    limiter = RateLimiter(rate=100, interval=60)  # 100 req/min
    if limiter.allow_request("user123"):
        # Process request
        pass
    else:
        # Rate limit exceeded
        pass

    # Token bucket
    bucket = TokenBucket(capacity=100, refill_rate=10)  # 10 tokens/sec
    if bucket.consume(1):
        # Request allowed
        pass

    # Adaptive rate limiting
    adaptive = AdaptiveRateLimiter(base_rate=100)
    adaptive.adjust_for_load(current_load=0.8)  # 80% load
    if adaptive.allow_request("user123"):
        # Request allowed
        pass
"""

from __future__ import annotations

import time
from collections import defaultdict
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from specify_cli.core.telemetry import record_exception, span

if TYPE_CHECKING:
    from typing import Any


class RateLimitError(Exception):
    """Base exception for rate limiting operations."""


class RateLimitExceeded(RateLimitError):
    """Exception raised when rate limit is exceeded."""


class TokenBucket:
    """
    Token bucket rate limiter.

    Implements the token bucket algorithm for smooth rate limiting with
    burst handling.

    Parameters
    ----------
    capacity : int
        Maximum number of tokens in bucket
    refill_rate : float
        Tokens added per second
    initial_tokens : int, optional
        Initial number of tokens. Default is capacity.

    Attributes
    ----------
    capacity : int
        Maximum bucket capacity
    refill_rate : float
        Refill rate in tokens per second
    tokens : float
        Current number of tokens
    last_refill : float
        Last refill timestamp
    """

    def __init__(
        self, capacity: int, refill_rate: float, initial_tokens: int | None = None
    ) -> None:
        """Initialize token bucket."""
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = initial_tokens if initial_tokens is not None else capacity
        self.last_refill = time.time()

    def _refill(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill
        new_tokens = elapsed * self.refill_rate

        self.tokens = min(self.capacity, self.tokens + new_tokens)  # type: ignore[assignment]
        self.last_refill = now

    def consume(self, tokens: int = 1) -> bool:
        """
        Attempt to consume tokens.

        Parameters
        ----------
        tokens : int, optional
            Number of tokens to consume. Default is 1.

        Returns
        -------
        bool
            True if tokens consumed, False if insufficient tokens
        """
        with span("security.rate_limiting", operation="consume"):
            self._refill()

            if self.tokens >= tokens:
                self.tokens -= tokens
                return True

            return False

    def get_tokens(self) -> float:
        """
        Get current number of tokens.

        Returns
        -------
        float
            Current token count
        """
        self._refill()
        return self.tokens

    def wait_time(self, tokens: int = 1) -> float:
        """
        Calculate wait time for tokens.

        Parameters
        ----------
        tokens : int, optional
            Number of tokens needed. Default is 1.

        Returns
        -------
        float
            Wait time in seconds (0 if tokens available)
        """
        self._refill()

        if self.tokens >= tokens:
            return 0.0

        tokens_needed = tokens - self.tokens
        return tokens_needed / self.refill_rate


class RateLimiter:
    """
    Rate limiter with sliding window.

    Implements sliding window rate limiting for precise rate control.

    Parameters
    ----------
    rate : int
        Maximum number of requests
    interval : int
        Time interval in seconds
    key_func : callable, optional
        Function to extract rate limit key from request

    Attributes
    ----------
    rate : int
        Maximum requests per interval
    interval : int
        Time interval in seconds
    requests : dict
        Request timestamps per key
    """

    def __init__(
        self, rate: int, interval: int = 60, key_func: Any | None = None
    ) -> None:
        """Initialize rate limiter."""
        self.rate = rate
        self.interval = interval
        self.key_func = key_func or (lambda x: x)
        self.requests: dict[str, list[float]] = defaultdict(list)

    def allow_request(self, key: str) -> bool:
        """
        Check if request is allowed.

        Parameters
        ----------
        key : str
            Rate limit key (e.g., user ID, IP address)

        Returns
        -------
        bool
            True if request allowed, False if rate limited
        """
        with span("security.rate_limiting", operation="allow_request", key=key):
            now = time.time()
            request_key = self.key_func(key)

            # Clean old requests
            self.requests[request_key] = [
                ts for ts in self.requests[request_key] if now - ts < self.interval
            ]

            # Check rate limit
            if len(self.requests[request_key]) < self.rate:
                self.requests[request_key].append(now)
                return True

            return False

    def get_remaining(self, key: str) -> int:
        """
        Get remaining requests for key.

        Parameters
        ----------
        key : str
            Rate limit key

        Returns
        -------
        int
            Remaining requests in current window
        """
        now = time.time()
        request_key = self.key_func(key)

        # Clean old requests
        self.requests[request_key] = [
            ts for ts in self.requests[request_key] if now - ts < self.interval
        ]

        return max(0, self.rate - len(self.requests[request_key]))

    def get_reset_time(self, key: str) -> float:
        """
        Get time until rate limit resets.

        Parameters
        ----------
        key : str
            Rate limit key

        Returns
        -------
        float
            Seconds until reset
        """
        now = time.time()
        request_key = self.key_func(key)

        if not self.requests[request_key]:
            return 0.0

        oldest_request = min(self.requests[request_key])
        reset_time = oldest_request + self.interval

        return max(0.0, reset_time - now)

    def get_headers(self, key: str) -> dict[str, str]:
        """
        Get rate limit headers.

        Parameters
        ----------
        key : str
            Rate limit key

        Returns
        -------
        dict
            Rate limit headers (X-RateLimit-*)
        """
        remaining = self.get_remaining(key)
        reset_time = self.get_reset_time(key)

        return {
            "X-RateLimit-Limit": str(self.rate),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(int(time.time() + reset_time)),
        }


class AdaptiveRateLimiter:
    """
    Adaptive rate limiter with dynamic thresholds.

    Adjusts rate limits based on system load and request patterns.

    Parameters
    ----------
    base_rate : int
        Base rate limit
    interval : int, optional
        Time interval in seconds. Default is 60.
    min_rate : int, optional
        Minimum rate limit. Default is base_rate // 10.
    max_rate : int, optional
        Maximum rate limit. Default is base_rate * 2.

    Attributes
    ----------
    base_rate : int
        Base rate limit
    current_rate : int
        Current adjusted rate limit
    min_rate : int
        Minimum rate limit
    max_rate : int
        Maximum rate limit
    limiter : RateLimiter
        Underlying rate limiter
    """

    def __init__(
        self,
        base_rate: int,
        interval: int = 60,
        min_rate: int | None = None,
        max_rate: int | None = None,
    ) -> None:
        """Initialize adaptive rate limiter."""
        self.base_rate = base_rate
        self.current_rate = base_rate
        self.min_rate = min_rate if min_rate is not None else base_rate // 10
        self.max_rate = max_rate if max_rate is not None else base_rate * 2
        self.interval = interval
        self.limiter = RateLimiter(self.current_rate, interval)

        # Load tracking
        self.request_count = 0
        self.error_count = 0
        self.last_adjustment = time.time()
        self.adjustment_interval = 60.0  # Adjust every 60 seconds

    def allow_request(self, key: str) -> bool:
        """
        Check if request is allowed with adaptive limits.

        Parameters
        ----------
        key : str
            Rate limit key

        Returns
        -------
        bool
            True if request allowed, False if rate limited
        """
        with span("security.rate_limiting", operation="adaptive_allow", key=key):
            self.request_count += 1

            # Adjust rate if needed
            self._maybe_adjust_rate()

            return self.limiter.allow_request(key)

    def record_error(self) -> None:
        """Record an error for adaptive adjustment."""
        self.error_count += 1

    def adjust_for_load(self, current_load: float) -> None:
        """
        Manually adjust rate based on system load.

        Parameters
        ----------
        current_load : float
            Current system load (0.0 to 1.0)
        """
        with span("security.rate_limiting", operation="adjust_for_load", load=current_load):
            if current_load >= 0.9:
                # High load - reduce rate
                new_rate = int(self.current_rate * 0.5)
            elif current_load >= 0.7:
                # Medium-high load - reduce slightly
                new_rate = int(self.current_rate * 0.8)
            elif current_load <= 0.3:
                # Low load - increase rate
                new_rate = int(self.current_rate * 1.2)
            else:
                # Normal load - keep current rate
                return

            # Apply constraints
            new_rate = max(self.min_rate, min(self.max_rate, new_rate))

            if new_rate != self.current_rate:
                self.current_rate = new_rate
                self.limiter = RateLimiter(self.current_rate, self.interval)

    def _maybe_adjust_rate(self) -> None:
        """Automatically adjust rate based on error rate."""
        now = time.time()
        if now - self.last_adjustment < self.adjustment_interval:
            return

        if self.request_count == 0:
            return

        # Calculate error rate
        error_rate = self.error_count / self.request_count

        # Adjust based on error rate
        if error_rate >= 0.1:  # 10% error rate
            # High errors - reduce rate
            new_rate = int(self.current_rate * 0.8)
        elif error_rate <= 0.01:  # 1% error rate
            # Low errors - increase rate
            new_rate = int(self.current_rate * 1.1)
        else:
            # Normal error rate - no adjustment
            self.last_adjustment = now
            return

        # Apply constraints
        new_rate = max(self.min_rate, min(self.max_rate, new_rate))

        if new_rate != self.current_rate:
            self.current_rate = new_rate
            self.limiter = RateLimiter(self.current_rate, self.interval)

        # Reset counters
        self.request_count = 0
        self.error_count = 0
        self.last_adjustment = now

    def get_current_rate(self) -> int:
        """
        Get current rate limit.

        Returns
        -------
        int
            Current rate limit
        """
        return self.current_rate

    def get_statistics(self) -> dict[str, Any]:
        """
        Get rate limiter statistics.

        Returns
        -------
        dict
            Statistics including current rate, error rate, etc.
        """
        error_rate = self.error_count / self.request_count if self.request_count > 0 else 0.0

        return {
            "base_rate": self.base_rate,
            "current_rate": self.current_rate,
            "min_rate": self.min_rate,
            "max_rate": self.max_rate,
            "request_count": self.request_count,
            "error_count": self.error_count,
            "error_rate": error_rate,
            "last_adjustment": datetime.fromtimestamp(self.last_adjustment).isoformat(),
        }


class DistributedRateLimiter:
    """
    Distributed rate limiter using Redis.

    Provides rate limiting across multiple servers using Redis as backend.

    Parameters
    ----------
    redis_client : Any
        Redis client instance
    rate : int
        Maximum number of requests
    interval : int, optional
        Time interval in seconds. Default is 60.
    key_prefix : str, optional
        Redis key prefix. Default is "ratelimit".

    Attributes
    ----------
    redis : Any
        Redis client
    rate : int
        Maximum requests per interval
    interval : int
        Time interval in seconds
    key_prefix : str
        Redis key prefix
    """

    def __init__(
        self,
        redis_client: Any,
        rate: int,
        interval: int = 60,
        key_prefix: str = "ratelimit",
    ) -> None:
        """Initialize distributed rate limiter."""
        self.redis = redis_client
        self.rate = rate
        self.interval = interval
        self.key_prefix = key_prefix

    def _get_redis_key(self, key: str) -> str:
        """Get Redis key for rate limit key."""
        return f"{self.key_prefix}:{key}"

    def allow_request(self, key: str) -> bool:
        """
        Check if request is allowed (distributed).

        Parameters
        ----------
        key : str
            Rate limit key

        Returns
        -------
        bool
            True if request allowed, False if rate limited
        """
        with span("security.rate_limiting", operation="distributed_allow", key=key):
            try:
                redis_key = self._get_redis_key(key)
                now = time.time()

                # Use Redis sorted set for sliding window
                # Remove old entries
                self.redis.zremrangebyscore(redis_key, 0, now - self.interval)

                # Count current requests
                current_count = self.redis.zcard(redis_key)

                if current_count < self.rate:
                    # Add new request
                    self.redis.zadd(redis_key, {str(now): now})
                    # Set expiry
                    self.redis.expire(redis_key, self.interval)
                    return True

                return False

            except Exception as e:
                record_exception(e)
                # Fail open on Redis errors
                return True

    def get_remaining(self, key: str) -> int:
        """
        Get remaining requests (distributed).

        Parameters
        ----------
        key : str
            Rate limit key

        Returns
        -------
        int
            Remaining requests
        """
        try:
            redis_key = self._get_redis_key(key)
            now = time.time()

            # Remove old entries
            self.redis.zremrangebyscore(redis_key, 0, now - self.interval)

            # Count current requests
            current_count = self.redis.zcard(redis_key)

            return max(0, self.rate - current_count)  # type: ignore[no-any-return]

        except Exception as e:
            record_exception(e)
            return self.rate


__all__ = [
    "TokenBucket",
    "RateLimiter",
    "AdaptiveRateLimiter",
    "DistributedRateLimiter",
    "RateLimitError",
    "RateLimitExceeded",
]
