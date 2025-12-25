"""
Tests for security.rate_limiting module.
"""

from __future__ import annotations

import time
import pytest

from specify_cli.security.rate_limiting import (
    TokenBucket,
    RateLimiter,
    AdaptiveRateLimiter,
)


class TestTokenBucket:
    """Tests for TokenBucket class."""

    def test_consume_tokens_available(self) -> None:
        """Test consuming tokens when available."""
        bucket = TokenBucket(capacity=10, refill_rate=1)

        # Should be able to consume tokens
        assert bucket.consume(5)
        # Use approximate equality due to time elapsed
        assert abs(bucket.get_tokens() - 5) < 0.1

    def test_consume_tokens_insufficient(self) -> None:
        """Test consuming tokens when insufficient."""
        bucket = TokenBucket(capacity=10, refill_rate=1)

        # Consume all tokens
        bucket.consume(10)

        # Should not be able to consume more
        assert not bucket.consume(1)

    def test_token_refill(self) -> None:
        """Test token refilling over time."""
        bucket = TokenBucket(capacity=10, refill_rate=10)  # 10 tokens/sec

        # Consume all tokens
        bucket.consume(10)

        # Wait for refill
        time.sleep(0.5)  # Should add 5 tokens

        # Should have some tokens now
        assert bucket.get_tokens() > 0

    def test_consume_multiple_tokens(self) -> None:
        """Test consuming multiple tokens at once."""
        bucket = TokenBucket(capacity=10, refill_rate=1)

        assert bucket.consume(3)
        # Use approximate equality due to time elapsed
        assert abs(bucket.get_tokens() - 7) < 0.1

    def test_wait_time_tokens_available(self) -> None:
        """Test wait time when tokens are available."""
        bucket = TokenBucket(capacity=10, refill_rate=1)

        wait = bucket.wait_time(5)
        assert wait == 0.0

    def test_wait_time_tokens_needed(self) -> None:
        """Test wait time when tokens need refilling."""
        bucket = TokenBucket(capacity=10, refill_rate=10)  # 10 tokens/sec

        # Consume all tokens
        bucket.consume(10)

        # Need to wait for 1 token
        wait = bucket.wait_time(1)
        assert wait > 0


class TestRateLimiter:
    """Tests for RateLimiter class."""

    def test_allow_request_within_limit(self) -> None:
        """Test allowing requests within rate limit."""
        limiter = RateLimiter(rate=10, interval=60)

        # Should allow first 10 requests
        for _ in range(10):
            assert limiter.allow_request("user123")

    def test_allow_request_exceed_limit(self) -> None:
        """Test rate limiting when limit exceeded."""
        limiter = RateLimiter(rate=5, interval=60)

        # Allow first 5 requests
        for _ in range(5):
            assert limiter.allow_request("user123")

        # 6th request should be rate limited
        assert not limiter.allow_request("user123")

    def test_get_remaining(self) -> None:
        """Test getting remaining requests."""
        limiter = RateLimiter(rate=10, interval=60)

        # Make 3 requests
        for _ in range(3):
            limiter.allow_request("user123")

        remaining = limiter.get_remaining("user123")
        assert remaining == 7

    def test_get_reset_time(self) -> None:
        """Test getting reset time."""
        limiter = RateLimiter(rate=10, interval=60)

        limiter.allow_request("user123")

        reset_time = limiter.get_reset_time("user123")
        assert reset_time > 0

    def test_get_headers(self) -> None:
        """Test getting rate limit headers."""
        limiter = RateLimiter(rate=100, interval=60)

        # Make some requests
        for _ in range(10):
            limiter.allow_request("user123")

        headers = limiter.get_headers("user123")

        assert headers["X-RateLimit-Limit"] == "100"
        assert int(headers["X-RateLimit-Remaining"]) == 90

    def test_sliding_window(self) -> None:
        """Test sliding window rate limiting."""
        limiter = RateLimiter(rate=5, interval=1)  # 5 requests per second

        # Make 5 requests
        for _ in range(5):
            assert limiter.allow_request("user123")

        # Should be rate limited
        assert not limiter.allow_request("user123")

        # Wait for window to slide
        time.sleep(1.1)

        # Should allow requests again
        assert limiter.allow_request("user123")

    def test_different_keys(self) -> None:
        """Test rate limiting with different keys."""
        limiter = RateLimiter(rate=5, interval=60)

        # User1 makes 5 requests
        for _ in range(5):
            assert limiter.allow_request("user1")

        # User2 should still be allowed
        assert limiter.allow_request("user2")


class TestAdaptiveRateLimiter:
    """Tests for AdaptiveRateLimiter class."""

    def test_allow_request_basic(self) -> None:
        """Test basic request allowing."""
        limiter = AdaptiveRateLimiter(base_rate=10, interval=60)

        # Should allow requests
        for _ in range(10):
            assert limiter.allow_request("user123")

    def test_adjust_for_high_load(self) -> None:
        """Test rate adjustment for high load."""
        limiter = AdaptiveRateLimiter(base_rate=100, interval=60)

        initial_rate = limiter.get_current_rate()

        # Adjust for high load (90%)
        limiter.adjust_for_load(0.9)

        # Rate should be reduced
        assert limiter.get_current_rate() < initial_rate

    def test_adjust_for_low_load(self) -> None:
        """Test rate adjustment for low load."""
        limiter = AdaptiveRateLimiter(base_rate=100, interval=60)

        initial_rate = limiter.get_current_rate()

        # Adjust for low load (20%)
        limiter.adjust_for_load(0.2)

        # Rate should be increased
        assert limiter.get_current_rate() > initial_rate

    def test_record_error(self) -> None:
        """Test recording errors."""
        limiter = AdaptiveRateLimiter(base_rate=100, interval=60)

        limiter.record_error()

        stats = limiter.get_statistics()
        assert stats["error_count"] == 1

    def test_get_statistics(self) -> None:
        """Test getting statistics."""
        limiter = AdaptiveRateLimiter(base_rate=100, interval=60)

        # Make some requests
        for _ in range(10):
            limiter.allow_request("user123")

        # Record some errors
        limiter.record_error()
        limiter.record_error()

        stats = limiter.get_statistics()

        assert stats["base_rate"] == 100
        assert stats["current_rate"] == 100
        assert stats["request_count"] == 10
        assert stats["error_count"] == 2

    def test_min_max_rate_constraints(self) -> None:
        """Test minimum and maximum rate constraints."""
        limiter = AdaptiveRateLimiter(
            base_rate=100,
            interval=60,
            min_rate=50,
            max_rate=200,
        )

        # Adjust for very high load (should not go below min_rate)
        limiter.adjust_for_load(1.0)
        assert limiter.get_current_rate() >= 50

        # Adjust for very low load (should not go above max_rate)
        limiter.adjust_for_load(0.0)
        assert limiter.get_current_rate() <= 200
