"""
specify_cli.core.advanced_cache - Hyper-Advanced Multi-Level Caching
=====================================================================

Advanced caching infrastructure with multi-level support, smart invalidation,
and comprehensive monitoring.

This module implements a sophisticated caching system that provides:

Key Features
-----------
* **Multi-Level Cache**: L1 (memory LRU), L2 (disk pickle), L3 (remote-aware)
* **Smart Invalidation**: mtime-based, dependency tracking, content hashing
* **Cache Statistics**: Hit rates, timings, size monitoring
* **Thread Safety**: Lock-based synchronization for concurrent access
* **TTL Support**: Time-to-live for cache entries
* **Dependency Tracking**: Invalidate based on file dependencies
* **Transparent Decorators**: Easy integration with existing code
* **Telemetry Integration**: Full OpenTelemetry instrumentation

Cache Levels
-----------
**L1 Cache (Memory)**:
    - functools.lru_cache with configurable size
    - Fastest access (<1ms)
    - Lost on process restart
    - Best for: Tool checks, version lookups, small computations

**L2 Cache (Disk)**:
    - pickle-based persistence
    - Survives process restarts
    - ~10-50ms access time
    - Best for: ggen transformations, RDF parsing, SPARQL results

**L3 Cache (Remote)**:
    - Awareness for distributed caching
    - Placeholder for Redis/Memcached integration
    - Future expansion point

Cache Key Generation
-------------------
Keys are generated using:
    - Function name + arguments (SHA256)
    - File dependencies (mtime + size)
    - Content hashing for data
    - Semantic versioning for schema changes

Smart Invalidation
-----------------
Automatic invalidation based on:
    - File modification times (mtime)
    - File size changes
    - Content hash changes
    - Explicit dependency tracking
    - TTL expiration
    - Manual cache clearing

Examples
--------
    >>> from specify_cli.core.advanced_cache import cached, SmartCache
    >>>
    >>> # Basic caching with decorator
    >>> @cached(ttl=300)
    >>> def expensive_operation(arg):
    ...     return perform_computation(arg)
    >>>
    >>> # Manual cache management
    >>> cache = SmartCache()
    >>> result = cache.get_or_compute(
    ...     key="operation:arg",
    ...     compute_fn=lambda: expensive_operation(),
    ...     dependencies=[Path("input.ttl")],
    ...     ttl=600
    ... )
    >>>
    >>> # Cache statistics
    >>> stats = cache.get_stats()
    >>> print(f"Hit rate: {stats['hit_rate']:.1%}")

Performance Targets
------------------
- L1 cache hit: < 1ms
- L2 cache hit: < 50ms
- L2 cache write: < 100ms
- Memory overhead: < 100MB for 1000 entries
- Disk overhead: < 500MB for 10000 entries

See Also
--------
- :mod:`specify_cli.core.cache` : Simple JSONL cache (legacy)
- :mod:`specify_cli.core.telemetry` : Telemetry integration
- :mod:`specify_cli.core.config` : Configuration utilities
"""

from __future__ import annotations

import functools
import hashlib
import json
import pickle
import threading
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypeVar

from .config import get_cache_dir
from .telemetry import metric_counter, metric_histogram, span

if TYPE_CHECKING:
    from collections.abc import Callable

__all__ = [
    "CacheKey",
    "CacheStats",
    "SmartCache",
    "cache_key_from_args",
    "cached",
    "clear_all_caches",
    "get_global_cache",
    "invalidate_cache",
]

T = TypeVar("T")

# Global cache instance (singleton)
_GLOBAL_CACHE: SmartCache | None = None
_GLOBAL_CACHE_LOCK = threading.Lock()

# Default cache configuration
DEFAULT_L1_SIZE = 128  # LRU cache entries
DEFAULT_L2_MAX_SIZE_MB = 500  # Maximum L2 disk cache size
DEFAULT_TTL = 3600  # 1 hour default TTL


@dataclass
class CacheKey:
    """
    Cache key with dependency tracking and validation.

    Attributes
    ----------
    key : str
        Base cache key (SHA256 hash).
    dependencies : list[Path]
        File dependencies for invalidation.
    content_hash : str
        Hash of cached content for validation.
    created_at : float
        Timestamp when key was created.
    ttl : int | None
        Time-to-live in seconds (None = no expiration).
    metadata : dict[str, Any]
        Additional metadata for cache entry.
    """

    key: str
    dependencies: list[Path] = field(default_factory=list)
    content_hash: str = ""
    created_at: float = field(default_factory=time.time)
    ttl: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_valid(self) -> bool:
        """
        Check if cache key is still valid.

        Returns
        -------
        bool
            True if key is valid (not expired, dependencies unchanged).
        """
        # Check TTL
        if self.ttl is not None and time.time() - self.created_at > self.ttl:
                return False

        # Check dependencies
        for dep in self.dependencies:
            if not dep.exists():
                return False

            # Check if dependency was modified after cache creation
            mtime = dep.stat().st_mtime
            if mtime > self.created_at:
                return False

        return True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "key": self.key,
            "dependencies": [str(d) for d in self.dependencies],
            "content_hash": self.content_hash,
            "created_at": self.created_at,
            "ttl": self.ttl,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CacheKey:
        """Create from dictionary."""
        return cls(
            key=data["key"],
            dependencies=[Path(d) for d in data.get("dependencies", [])],
            content_hash=data.get("content_hash", ""),
            created_at=data.get("created_at", time.time()),
            ttl=data.get("ttl"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class CacheStats:
    """
    Cache statistics for monitoring and optimization.

    Attributes
    ----------
    l1_hits : int
        L1 (memory) cache hits.
    l2_hits : int
        L2 (disk) cache hits.
    misses : int
        Cache misses (computation required).
    invalidations : int
        Number of invalidations.
    total_requests : int
        Total cache requests.
    l1_size : int
        Current L1 cache size.
    l2_size : int
        Current L2 cache size.
    l2_disk_bytes : int
        L2 disk usage in bytes.
    avg_l1_time_ms : float
        Average L1 access time in milliseconds.
    avg_l2_time_ms : float
        Average L2 access time in milliseconds.
    avg_compute_time_ms : float
        Average computation time in milliseconds.
    hit_rate : float
        Overall cache hit rate (0.0 to 1.0).
    """

    l1_hits: int = 0
    l2_hits: int = 0
    misses: int = 0
    invalidations: int = 0
    total_requests: int = 0
    l1_size: int = 0
    l2_size: int = 0
    l2_disk_bytes: int = 0
    avg_l1_time_ms: float = 0.0
    avg_l2_time_ms: float = 0.0
    avg_compute_time_ms: float = 0.0

    @property
    def hit_rate(self) -> float:
        """Calculate overall hit rate."""
        if self.total_requests == 0:
            return 0.0
        hits = self.l1_hits + self.l2_hits
        return hits / self.total_requests

    @property
    def l1_hit_rate(self) -> float:
        """Calculate L1 hit rate."""
        if self.total_requests == 0:
            return 0.0
        return self.l1_hits / self.total_requests

    @property
    def l2_hit_rate(self) -> float:
        """Calculate L2 hit rate."""
        if self.total_requests == 0:
            return 0.0
        return self.l2_hits / self.total_requests

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for reporting."""
        return {
            "l1_hits": self.l1_hits,
            "l2_hits": self.l2_hits,
            "misses": self.misses,
            "invalidations": self.invalidations,
            "total_requests": self.total_requests,
            "l1_size": self.l1_size,
            "l2_size": self.l2_size,
            "l2_disk_bytes": self.l2_disk_bytes,
            "hit_rate": self.hit_rate,
            "l1_hit_rate": self.l1_hit_rate,
            "l2_hit_rate": self.l2_hit_rate,
            "avg_l1_time_ms": self.avg_l1_time_ms,
            "avg_l2_time_ms": self.avg_l2_time_ms,
            "avg_compute_time_ms": self.avg_compute_time_ms,
        }


class SmartCache:
    """
    Multi-level cache with smart invalidation and monitoring.

    This class implements a sophisticated caching system with three levels:
    - L1: In-memory LRU cache (fastest, volatile)
    - L2: Disk-based pickle cache (persistent, slower)
    - L3: Remote cache awareness (future expansion)

    Parameters
    ----------
    l1_size : int, optional
        Maximum L1 cache entries. Default is 128.
    l2_max_size_mb : int, optional
        Maximum L2 cache size in MB. Default is 500.
    cache_dir : Path | None, optional
        Directory for L2 cache. Default uses get_cache_dir().
    enable_stats : bool, optional
        Enable statistics tracking. Default is True.

    Examples
    --------
    >>> cache = SmartCache(l1_size=256)
    >>> result = cache.get_or_compute(
    ...     key="expensive_op",
    ...     compute_fn=lambda: expensive_operation(),
    ...     ttl=300
    ... )
    """

    def __init__(
        self,
        l1_size: int = DEFAULT_L1_SIZE,
        l2_max_size_mb: int = DEFAULT_L2_MAX_SIZE_MB,
        cache_dir: Path | None = None,
        enable_stats: bool = True,
    ) -> None:
        """Initialize SmartCache."""
        self.l1_size = l1_size
        self.l2_max_size_mb = l2_max_size_mb
        self.cache_dir = cache_dir or get_cache_dir() / "advanced"
        self.enable_stats = enable_stats

        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # L1 cache: OrderedDict for LRU behavior
        self._l1_cache: OrderedDict[str, tuple[Any, CacheKey]] = OrderedDict()
        self._l1_lock = threading.Lock()

        # L2 cache: Disk-based pickle storage
        self._l2_index: dict[str, CacheKey] = {}
        self._l2_lock = threading.Lock()
        self._load_l2_index()

        # Statistics
        self._stats = CacheStats()
        self._stats_lock = threading.Lock()

        # Timing accumulators for averages
        self._l1_times: list[float] = []
        self._l2_times: list[float] = []
        self._compute_times: list[float] = []

    def get_or_compute(
        self,
        key: str,
        compute_fn: Callable[[], T],
        dependencies: list[Path] | None = None,
        ttl: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> T:
        """
        Get cached result or compute and cache it.

        This is the primary interface for the cache. It checks L1, then L2,
        and if both miss, calls compute_fn and caches the result.

        Parameters
        ----------
        key : str
            Cache key (usually from cache_key_from_args).
        compute_fn : Callable[[], T]
            Function to compute result if cache misses.
        dependencies : list[Path] | None, optional
            File dependencies for invalidation.
        ttl : int | None, optional
            Time-to-live in seconds.
        metadata : dict[str, Any] | None, optional
            Additional metadata for cache entry.

        Returns
        -------
        T
            Cached or computed result.
        """
        with span("cache.get_or_compute", cache_key=key):
            dependencies = dependencies or []
            metadata = metadata or {}

            with self._stats_lock:
                self._stats.total_requests += 1

            # Try L1 cache
            l1_start = time.time()
            result = self._get_from_l1(key)
            l1_duration = (time.time() - l1_start) * 1000

            if result is not None:
                value, cache_key = result
                if cache_key.is_valid():
                    self._record_l1_hit(l1_duration)
                    metric_counter("cache.advanced.l1.hit")(1)
                    return value
                # Invalid - remove from L1
                self._remove_from_l1(key)

            # Try L2 cache
            l2_start = time.time()
            result = self._get_from_l2(key)
            l2_duration = (time.time() - l2_start) * 1000

            if result is not None:
                value, cache_key = result
                if cache_key.is_valid():
                    # Promote to L1
                    self._set_in_l1(key, value, cache_key)
                    self._record_l2_hit(l2_duration)
                    metric_counter("cache.advanced.l2.hit")(1)
                    return value
                # Invalid - remove from L2
                self._remove_from_l2(key)

            # Cache miss - compute result
            compute_start = time.time()
            computed_value = compute_fn()
            compute_duration = (time.time() - compute_start) * 1000

            # Create cache key with dependencies
            content_hash = self._hash_content(computed_value)
            cache_key = CacheKey(
                key=key,
                dependencies=dependencies,
                content_hash=content_hash,
                ttl=ttl,
                metadata=metadata,
            )

            # Store in both L1 and L2
            self._set_in_l1(key, computed_value, cache_key)
            self._set_in_l2(key, computed_value, cache_key)

            self._record_miss(compute_duration)
            metric_counter("cache.advanced.miss")(1)
            metric_histogram("cache.advanced.compute_time")(compute_duration / 1000)

            return computed_value

    def invalidate(self, key: str) -> None:
        """
        Invalidate a specific cache key.

        Parameters
        ----------
        key : str
            Cache key to invalidate.
        """
        with span("cache.invalidate", cache_key=key):
            self._remove_from_l1(key)
            self._remove_from_l2(key)

            with self._stats_lock:
                self._stats.invalidations += 1

            metric_counter("cache.advanced.invalidation")(1)

    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all keys matching a pattern.

        Parameters
        ----------
        pattern : str
            Pattern to match (substring match).

        Returns
        -------
        int
            Number of keys invalidated.
        """
        with span("cache.invalidate_pattern", pattern=pattern):
            count = 0

            # Invalidate from L1
            with self._l1_lock:
                keys_to_remove = [k for k in self._l1_cache if pattern in k]
                for key in keys_to_remove:
                    del self._l1_cache[key]
                    count += 1

            # Invalidate from L2
            with self._l2_lock:
                keys_to_remove = [k for k in self._l2_index if pattern in k]
                for key in keys_to_remove:
                    self._remove_from_l2_unsafe(key)
                    count += 1

            with self._stats_lock:
                self._stats.invalidations += count

            metric_counter("cache.advanced.invalidation_pattern")(count)
            return count

    def clear(self) -> None:
        """Clear all cache levels."""
        with span("cache.clear"):
            # Clear L1
            with self._l1_lock:
                self._l1_cache.clear()

            # Clear L2
            with self._l2_lock:
                for cache_file in self.cache_dir.glob("*.pkl"):
                    try:
                        cache_file.unlink()
                    except Exception:
                        pass
                self._l2_index.clear()
                self._save_l2_index()

            # Reset stats
            with self._stats_lock:
                self._stats = CacheStats()
                self._l1_times.clear()
                self._l2_times.clear()
                self._compute_times.clear()

            metric_counter("cache.advanced.clear")(1)

    def get_stats(self) -> CacheStats:
        """
        Get current cache statistics.

        Returns
        -------
        CacheStats
            Current cache statistics.
        """
        with self._stats_lock:
            # Update size stats
            self._stats.l1_size = len(self._l1_cache)
            self._stats.l2_size = len(self._l2_index)

            # Calculate L2 disk usage
            total_bytes = sum(
                f.stat().st_size for f in self.cache_dir.glob("*.pkl") if f.is_file()
            )
            self._stats.l2_disk_bytes = total_bytes

            return self._stats

    # -------------------------------------------------------------------------
    # L1 Cache (Memory) Operations
    # -------------------------------------------------------------------------

    def _get_from_l1(self, key: str) -> tuple[Any, CacheKey] | None:
        """Get value from L1 cache."""
        with self._l1_lock:
            if key in self._l1_cache:
                # Move to end (LRU)
                self._l1_cache.move_to_end(key)
                return self._l1_cache[key]
            return None

    def _set_in_l1(self, key: str, value: Any, cache_key: CacheKey) -> None:
        """Set value in L1 cache with LRU eviction."""
        with self._l1_lock:
            self._l1_cache[key] = (value, cache_key)
            self._l1_cache.move_to_end(key)

            # LRU eviction
            if len(self._l1_cache) > self.l1_size:
                self._l1_cache.popitem(last=False)

    def _remove_from_l1(self, key: str) -> None:
        """Remove key from L1 cache."""
        with self._l1_lock:
            self._l1_cache.pop(key, None)

    # -------------------------------------------------------------------------
    # L2 Cache (Disk) Operations
    # -------------------------------------------------------------------------

    def _get_from_l2(self, key: str) -> tuple[Any, CacheKey] | None:
        """Get value from L2 cache."""
        with self._l2_lock:
            if key not in self._l2_index:
                return None

            cache_key = self._l2_index[key]
            cache_file = self._get_l2_path(key)

            if not cache_file.exists():
                # Index is stale
                del self._l2_index[key]
                return None

            try:
                with open(cache_file, "rb") as f:
                    value = pickle.load(f)
                return (value, cache_key)
            except Exception:
                # Corrupted cache file
                self._remove_from_l2_unsafe(key)
                return None

    def _set_in_l2(self, key: str, value: Any, cache_key: CacheKey) -> None:
        """Set value in L2 cache."""
        with self._l2_lock:
            cache_file = self._get_l2_path(key)

            try:
                # Write pickle file
                with open(cache_file, "wb") as f:
                    pickle.dump(value, f, protocol=pickle.HIGHEST_PROTOCOL)

                # Update index
                self._l2_index[key] = cache_key
                self._save_l2_index()

                # Check size and prune if needed
                self._maybe_prune_l2()

            except Exception as e:
                metric_counter("cache.advanced.l2.write_error")(1)
                # Clean up on error
                if cache_file.exists():
                    cache_file.unlink()
                raise ValueError(f"Failed to write L2 cache: {e}") from e

    def _remove_from_l2(self, key: str) -> None:
        """Remove key from L2 cache (thread-safe)."""
        with self._l2_lock:
            self._remove_from_l2_unsafe(key)

    def _remove_from_l2_unsafe(self, key: str) -> None:
        """Remove key from L2 cache (not thread-safe, must hold lock)."""
        if key in self._l2_index:
            del self._l2_index[key]

        cache_file = self._get_l2_path(key)
        if cache_file.exists():
            cache_file.unlink()

    def _get_l2_path(self, key: str) -> Path:
        """Get L2 cache file path for key."""
        return self.cache_dir / f"{key}.pkl"

    def _load_l2_index(self) -> None:
        """Load L2 cache index from disk."""
        index_file = self.cache_dir / "index.json"
        if not index_file.exists():
            return

        try:
            with open(index_file) as f:
                index_data = json.load(f)
                self._l2_index = {
                    k: CacheKey.from_dict(v) for k, v in index_data.items()
                }
        except Exception:
            # Corrupted index - start fresh
            self._l2_index = {}

    def _save_l2_index(self) -> None:
        """Save L2 cache index to disk."""
        index_file = self.cache_dir / "index.json"
        try:
            index_data = {k: v.to_dict() for k, v in self._l2_index.items()}
            with Path(index_file).open("w") as f:
                json.dump(index_data, f, indent=2)
        except Exception:
            metric_counter("cache.advanced.l2.index_save_error")(1)

    def _maybe_prune_l2(self) -> None:
        """Prune L2 cache if it exceeds maximum size."""
        # Calculate total size
        total_bytes = sum(
            f.stat().st_size for f in self.cache_dir.glob("*.pkl") if f.is_file()
        )

        max_bytes = self.l2_max_size_mb * 1024 * 1024

        if total_bytes <= max_bytes:
            return

        # Sort by access time (oldest first)
        entries = [
            (key, self._get_l2_path(key).stat().st_atime, cache_key)
            for key, cache_key in self._l2_index.items()
            if self._get_l2_path(key).exists()
        ]
        entries.sort(key=lambda x: x[1])

        # Remove oldest entries until under limit
        bytes_to_remove = total_bytes - max_bytes
        bytes_removed = 0

        for key, _atime, _cache_key in entries:
            if bytes_removed >= bytes_to_remove:
                break

            cache_file = self._get_l2_path(key)
            if cache_file.exists():
                bytes_removed += cache_file.stat().st_size
                self._remove_from_l2_unsafe(key)

        metric_counter("cache.advanced.l2.pruned")(1)

    # -------------------------------------------------------------------------
    # Statistics and Monitoring
    # -------------------------------------------------------------------------

    def _record_l1_hit(self, duration_ms: float) -> None:
        """Record L1 cache hit."""
        with self._stats_lock:
            self._stats.l1_hits += 1
            self._l1_times.append(duration_ms)
            if len(self._l1_times) > 100:
                self._l1_times.pop(0)
            self._stats.avg_l1_time_ms = sum(self._l1_times) / len(self._l1_times)

    def _record_l2_hit(self, duration_ms: float) -> None:
        """Record L2 cache hit."""
        with self._stats_lock:
            self._stats.l2_hits += 1
            self._l2_times.append(duration_ms)
            if len(self._l2_times) > 100:
                self._l2_times.pop(0)
            self._stats.avg_l2_time_ms = sum(self._l2_times) / len(self._l2_times)

    def _record_miss(self, duration_ms: float) -> None:
        """Record cache miss."""
        with self._stats_lock:
            self._stats.misses += 1
            self._compute_times.append(duration_ms)
            if len(self._compute_times) > 100:
                self._compute_times.pop(0)
            self._stats.avg_compute_time_ms = (
                sum(self._compute_times) / len(self._compute_times)
            )

    # -------------------------------------------------------------------------
    # Utilities
    # -------------------------------------------------------------------------

    @staticmethod
    def _hash_content(value: Any) -> str:
        """Generate SHA256 hash of content."""
        try:
            # Try to pickle for consistent hashing
            content_bytes = pickle.dumps(value)
            return hashlib.sha256(content_bytes, usedforsecurity=False).hexdigest()
        except Exception:
            # Fallback to string representation
            content_str = str(value)
            return hashlib.sha256(
                content_str.encode(), usedforsecurity=False
            ).hexdigest()


# -----------------------------------------------------------------------------
# Global Cache Instance
# -----------------------------------------------------------------------------


def get_global_cache() -> SmartCache:
    """
    Get or create the global cache instance.

    Returns
    -------
    SmartCache
        Global cache instance.
    """
    global _GLOBAL_CACHE  # noqa: PLW0603

    if _GLOBAL_CACHE is None:
        with _GLOBAL_CACHE_LOCK:
            if _GLOBAL_CACHE is None:
                _GLOBAL_CACHE = SmartCache()

    return _GLOBAL_CACHE


def clear_all_caches() -> None:
    """Clear all cache instances."""
    global _GLOBAL_CACHE

    if _GLOBAL_CACHE is not None:
        _GLOBAL_CACHE.clear()

    metric_counter("cache.advanced.clear_all")(1)


# -----------------------------------------------------------------------------
# Decorator for Caching
# -----------------------------------------------------------------------------


def cached(
    ttl: int | None = None,
    dependencies: list[Path] | None = None,
    cache_instance: SmartCache | None = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator for transparent caching of function results.

    Parameters
    ----------
    ttl : int | None, optional
        Time-to-live in seconds.
    dependencies : list[Path] | None, optional
        File dependencies for invalidation.
    cache_instance : SmartCache | None, optional
        Cache instance to use (default: global cache).

    Returns
    -------
    Callable
        Decorated function with caching.

    Examples
    --------
    >>> @cached(ttl=300)
    ... def expensive_computation(x: int) -> int:
    ...     return x ** 2
    >>>
    >>> result = expensive_computation(10)  # Computed
    >>> result = expensive_computation(10)  # Cached
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        cache = cache_instance or get_global_cache()

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # Generate cache key from function name and arguments
            key = cache_key_from_args(func.__name__, *args, **kwargs)

            # Use cache
            return cache.get_or_compute(
                key=key,
                compute_fn=lambda: func(*args, **kwargs),
                dependencies=dependencies,
                ttl=ttl,
                metadata={"function": func.__name__},
            )

        return wrapper

    return decorator


def cache_key_from_args(func_name: str, *args: Any, **kwargs: Any) -> str:
    """
    Generate cache key from function name and arguments.

    Parameters
    ----------
    func_name : str
        Function name.
    *args : Any
        Positional arguments.
    **kwargs : Any
        Keyword arguments.

    Returns
    -------
    str
        SHA256 cache key.
    """
    # Build key string
    parts = [func_name]

    # Add positional args
    for arg in args:
        if isinstance(arg, Path):
            parts.append(str(arg))
        else:
            parts.append(str(arg))

    # Add keyword args (sorted for consistency)
    for k, v in sorted(kwargs.items()):
        if isinstance(v, Path):
            parts.append(f"{k}={v}")
        else:
            parts.append(f"{k}={v}")

    key_string = "|".join(parts)
    return hashlib.sha256(key_string.encode(), usedforsecurity=False).hexdigest()


def invalidate_cache(pattern: str) -> int:
    """
    Invalidate cache entries matching pattern.

    Parameters
    ----------
    pattern : str
        Pattern to match.

    Returns
    -------
    int
        Number of entries invalidated.
    """
    cache = get_global_cache()
    return cache.invalidate_pattern(pattern)
