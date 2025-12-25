"""
Unit tests for advanced_cache module.

Tests the multi-level caching system with smart invalidation.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from specify_cli.core.advanced_cache import (
    CacheKey,
    CacheStats,
    SmartCache,
    cache_key_from_args,
    cached,
    clear_all_caches,
    get_global_cache,
    invalidate_cache,
)

if TYPE_CHECKING:
    from _pytest.tmpdir import TempPathFactory


@pytest.fixture
def temp_cache_dir(tmp_path_factory: TempPathFactory) -> Path:
    """Create temporary cache directory."""
    return tmp_path_factory.mktemp("cache")


@pytest.fixture
def cache(temp_cache_dir: Path) -> SmartCache:
    """Create SmartCache instance with temporary directory."""
    return SmartCache(cache_dir=temp_cache_dir, l1_size=10)


class TestCacheKey:
    """Tests for CacheKey class."""

    def test_cache_key_creation(self) -> None:
        """Test CacheKey creation."""
        key = CacheKey(key="test-key", ttl=300)
        assert key.key == "test-key"
        assert key.ttl == 300
        assert key.is_valid()

    def test_cache_key_expiration(self) -> None:
        """Test TTL expiration."""
        # Create key with 0.1s TTL
        key = CacheKey(key="test-key", ttl=0.1, created_at=time.time())
        assert key.is_valid()

        # Wait for expiration
        time.sleep(0.15)
        assert not key.is_valid()

    def test_cache_key_dependencies(self, tmp_path: Path) -> None:
        """Test dependency tracking."""
        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        # Create cache key with dependency
        key = CacheKey(key="test-key", dependencies=[test_file])
        assert key.is_valid()

        # Modify file (update mtime)
        time.sleep(0.01)  # Ensure mtime difference
        test_file.write_text("new content")

        # Key should be invalid due to modified dependency
        assert not key.is_valid()

    def test_cache_key_missing_dependency(self, tmp_path: Path) -> None:
        """Test invalid key when dependency is missing."""
        missing_file = tmp_path / "missing.txt"

        key = CacheKey(key="test-key", dependencies=[missing_file])
        assert not key.is_valid()

    def test_cache_key_serialization(self, tmp_path: Path) -> None:
        """Test to_dict and from_dict."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        key = CacheKey(
            key="test-key",
            dependencies=[test_file],
            content_hash="abc123",
            ttl=300,
            metadata={"foo": "bar"},
        )

        # Serialize and deserialize
        data = key.to_dict()
        restored = CacheKey.from_dict(data)

        assert restored.key == key.key
        assert restored.content_hash == key.content_hash
        assert restored.ttl == key.ttl
        assert restored.metadata == key.metadata


class TestCacheStats:
    """Tests for CacheStats class."""

    def test_cache_stats_hit_rate(self) -> None:
        """Test hit rate calculation."""
        stats = CacheStats(l1_hits=30, l2_hits=20, misses=50, total_requests=100)

        assert stats.hit_rate == 0.5  # (30 + 20) / 100
        assert stats.l1_hit_rate == 0.3  # 30 / 100
        assert stats.l2_hit_rate == 0.2  # 20 / 100

    def test_cache_stats_zero_requests(self) -> None:
        """Test hit rate with zero requests."""
        stats = CacheStats()
        assert stats.hit_rate == 0.0
        assert stats.l1_hit_rate == 0.0
        assert stats.l2_hit_rate == 0.0

    def test_cache_stats_to_dict(self) -> None:
        """Test stats serialization."""
        stats = CacheStats(l1_hits=10, l2_hits=5, misses=5, total_requests=20)
        data = stats.to_dict()

        assert data["l1_hits"] == 10
        assert data["l2_hits"] == 5
        assert data["misses"] == 5
        assert data["total_requests"] == 20
        assert data["hit_rate"] == 0.75


class TestSmartCache:
    """Tests for SmartCache class."""

    def test_cache_l1_hit(self, cache: SmartCache) -> None:
        """Test L1 cache hit."""
        call_count = 0

        def expensive_fn() -> int:
            nonlocal call_count
            call_count += 1
            return 42

        # First call - cache miss
        result1 = cache.get_or_compute("key1", expensive_fn)
        assert result1 == 42
        assert call_count == 1

        # Second call - L1 hit
        result2 = cache.get_or_compute("key1", expensive_fn)
        assert result2 == 42
        assert call_count == 1  # Not called again

        stats = cache.get_stats()
        assert stats.l1_hits == 1
        assert stats.misses == 1

    def test_cache_l2_hit(self, cache: SmartCache) -> None:
        """Test L2 cache hit after L1 eviction."""
        call_count = 0

        def expensive_fn(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * 2

        # Fill L1 cache beyond capacity (L1 size = 10)
        for i in range(12):
            cache.get_or_compute(f"key{i}", lambda x=i: expensive_fn(x))

        assert call_count == 12

        # Access first key again (evicted from L1, should be in L2)
        result = cache.get_or_compute("key0", lambda: expensive_fn(0))
        assert result == 0
        assert call_count == 12  # Not computed again

        stats = cache.get_stats()
        assert stats.l2_hits >= 1

    def test_cache_with_ttl(self, cache: SmartCache) -> None:
        """Test TTL expiration."""
        call_count = 0

        def expensive_fn() -> int:
            nonlocal call_count
            call_count += 1
            return 42

        # Cache with short TTL
        result1 = cache.get_or_compute("key1", expensive_fn, ttl=0.1)
        assert result1 == 42
        assert call_count == 1

        # Immediate re-access (should hit cache)
        result2 = cache.get_or_compute("key1", expensive_fn, ttl=0.1)
        assert result2 == 42
        assert call_count == 1

        # Wait for TTL expiration
        time.sleep(0.15)

        # Access after expiration (should recompute)
        result3 = cache.get_or_compute("key1", expensive_fn, ttl=0.1)
        assert result3 == 42
        assert call_count == 2

    def test_cache_with_dependencies(self, cache: SmartCache, tmp_path: Path) -> None:
        """Test dependency-based invalidation."""
        test_file = tmp_path / "input.txt"
        test_file.write_text("v1")

        call_count = 0

        def expensive_fn() -> str:
            nonlocal call_count
            call_count += 1
            return test_file.read_text()

        # Cache with dependency
        result1 = cache.get_or_compute(
            "key1", expensive_fn, dependencies=[test_file]
        )
        assert result1 == "v1"
        assert call_count == 1

        # Re-access (should hit cache)
        result2 = cache.get_or_compute(
            "key1", expensive_fn, dependencies=[test_file]
        )
        assert result2 == "v1"
        assert call_count == 1

        # Modify dependency
        time.sleep(0.01)
        test_file.write_text("v2")

        # Re-access (should recompute due to modified dependency)
        result3 = cache.get_or_compute(
            "key1", expensive_fn, dependencies=[test_file]
        )
        assert result3 == "v2"
        assert call_count == 2

    def test_cache_invalidate(self, cache: SmartCache) -> None:
        """Test manual invalidation."""
        call_count = 0

        def expensive_fn() -> int:
            nonlocal call_count
            call_count += 1
            return 42

        # Cache result
        result1 = cache.get_or_compute("key1", expensive_fn)
        assert result1 == 42
        assert call_count == 1

        # Invalidate
        cache.invalidate("key1")

        # Re-access (should recompute)
        result2 = cache.get_or_compute("key1", expensive_fn)
        assert result2 == 42
        assert call_count == 2

    def test_cache_invalidate_pattern(self, cache: SmartCache) -> None:
        """Test pattern-based invalidation."""
        # Cache multiple keys
        cache.get_or_compute("user:1:profile", lambda: "profile1")
        cache.get_or_compute("user:1:settings", lambda: "settings1")
        cache.get_or_compute("user:2:profile", lambda: "profile2")
        cache.get_or_compute("post:1", lambda: "post1")

        # Invalidate all user:1 keys
        count = cache.invalidate_pattern("user:1")
        assert count >= 2

        stats = cache.get_stats()
        assert stats.invalidations >= 2

    def test_cache_clear(self, cache: SmartCache) -> None:
        """Test clearing all caches."""
        # Cache some values
        cache.get_or_compute("key1", lambda: 1)
        cache.get_or_compute("key2", lambda: 2)
        cache.get_or_compute("key3", lambda: 3)

        stats = cache.get_stats()
        assert stats.l1_size > 0

        # Clear cache
        cache.clear()

        stats = cache.get_stats()
        assert stats.l1_size == 0
        assert stats.l2_size == 0

    def test_cache_stats(self, cache: SmartCache) -> None:
        """Test statistics tracking."""
        # Perform various operations
        cache.get_or_compute("key1", lambda: 1)  # miss
        cache.get_or_compute("key1", lambda: 1)  # L1 hit
        cache.get_or_compute("key2", lambda: 2)  # miss

        stats = cache.get_stats()
        assert stats.total_requests == 3
        assert stats.l1_hits == 1
        assert stats.misses == 2
        assert stats.hit_rate == 1 / 3

    def test_cache_l2_persistence(self, temp_cache_dir: Path) -> None:
        """Test L2 cache persistence across instances."""
        # Create first cache instance
        cache1 = SmartCache(cache_dir=temp_cache_dir)
        cache1.get_or_compute("key1", lambda: 42)

        # Create second cache instance (simulates restart)
        cache2 = SmartCache(cache_dir=temp_cache_dir)

        # Key should be in L2 (loaded from disk)
        call_count = 0

        def expensive_fn() -> int:
            nonlocal call_count
            call_count += 1
            return 99

        result = cache2.get_or_compute("key1", expensive_fn)
        assert result == 42  # From L2 cache
        assert call_count == 0  # Not computed


class TestCacheDecorator:
    """Tests for @cached decorator."""

    def test_cached_decorator(self) -> None:
        """Test basic caching with decorator."""
        call_count = 0

        @cached(ttl=300)
        def expensive_computation(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x ** 2

        # First call
        result1 = expensive_computation(10)
        assert result1 == 100
        assert call_count == 1

        # Second call (cached)
        result2 = expensive_computation(10)
        assert result2 == 100
        assert call_count == 1

        # Different argument (not cached)
        result3 = expensive_computation(20)
        assert result3 == 400
        assert call_count == 2

    def test_cached_decorator_with_dependencies(self, tmp_path: Path) -> None:
        """Test caching with file dependencies."""
        test_file = tmp_path / "input.txt"
        test_file.write_text("content")

        call_count = 0

        @cached(dependencies=[test_file])
        def read_file() -> str:
            nonlocal call_count
            call_count += 1
            return test_file.read_text()

        # First call
        result1 = read_file()
        assert result1 == "content"
        assert call_count == 1

        # Second call (cached)
        result2 = read_file()
        assert result2 == "content"
        assert call_count == 1

        # Modify file
        time.sleep(0.01)
        test_file.write_text("new content")

        # Third call (recomputed)
        result3 = read_file()
        assert result3 == "new content"
        assert call_count == 2


class TestCacheKeyGeneration:
    """Tests for cache key generation."""

    def test_cache_key_from_args(self) -> None:
        """Test cache key generation from arguments."""
        key1 = cache_key_from_args("func", 1, 2, foo="bar")
        key2 = cache_key_from_args("func", 1, 2, foo="bar")
        key3 = cache_key_from_args("func", 1, 3, foo="bar")

        # Same args should produce same key
        assert key1 == key2

        # Different args should produce different key
        assert key1 != key3

    def test_cache_key_with_path(self, tmp_path: Path) -> None:
        """Test cache key with Path arguments."""
        path = tmp_path / "test.txt"
        key = cache_key_from_args("func", path)

        assert isinstance(key, str)
        assert len(key) == 64  # SHA256 hex length


class TestGlobalCache:
    """Tests for global cache instance."""

    def test_get_global_cache(self) -> None:
        """Test global cache singleton."""
        cache1 = get_global_cache()
        cache2 = get_global_cache()

        assert cache1 is cache2

    def test_clear_all_caches(self) -> None:
        """Test clearing all caches."""
        cache = get_global_cache()
        cache.get_or_compute("key1", lambda: 1)

        clear_all_caches()

        stats = cache.get_stats()
        assert stats.l1_size == 0

    def test_invalidate_cache_function(self) -> None:
        """Test invalidate_cache helper."""
        cache = get_global_cache()
        cache.get_or_compute("prefix:key1", lambda: 1)
        cache.get_or_compute("prefix:key2", lambda: 2)
        cache.get_or_compute("other:key3", lambda: 3)

        # Invalidate prefix keys
        count = invalidate_cache("prefix:")
        assert count >= 2
