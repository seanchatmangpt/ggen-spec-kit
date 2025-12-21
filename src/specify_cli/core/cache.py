"""
specify_cli.core.cache - Result Caching System
===============================================

SHA1-based caching system for specify-cli command results.

This module provides a simple but effective caching system that stores
command execution results in a JSONL file for fast retrieval on repeated
operations.

Key Features
-----------
* **SHA1 Hashing**: Commands are hashed for unique cache keys
* **JSONL Storage**: Append-only format for reliability
* **Hit/Miss Tracking**: Metrics for cache performance analysis
* **Bounded Size**: Automatic pruning to prevent resource exhaustion
* **Telemetry Integration**: Full OpenTelemetry instrumentation

Cache Location
-------------
Default: ~/.cache/specify/runs.jsonl
Override: Set SPECIFY_CACHE_DIR environment variable

Examples
--------
    >>> from specify_cli.core.cache import get_cached, set_cached, cache_key
    >>>
    >>> # Generate cache key
    >>> key = cache_key("deps", "add", "requests")
    >>>
    >>> # Check cache
    >>> result = get_cached(key)
    >>> if result is None:
    ...     result = execute_command()
    ...     set_cached(key, result)

See Also
--------
- :mod:`specify_cli.core.config` : Configuration utilities
- :mod:`specify_cli.core.telemetry` : Telemetry and observability
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any

from .config import get_cache_dir
from .telemetry import metric_counter, metric_histogram, span

__all__ = [
    "cache_key",
    "get_cached",
    "set_cached",
    "clear_cache",
    "cache_stats",
]

# Maximum cache entries before pruning
_MAX_CACHE_ENTRIES = 1000

# Cache file name
_CACHE_FILE = "runs.jsonl"


def _get_cache_path() -> Path:
    """Get the path to the cache file."""
    cache_dir = get_cache_dir()
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / _CACHE_FILE


def cache_key(*args: Any) -> str:
    """
    Generate a SHA1 cache key from arguments.

    Parameters
    ----------
    *args : Any
        Arguments to hash into a cache key.

    Returns
    -------
    str
        SHA1 hash string.

    Example
    -------
    >>> key = cache_key("deps", "add", "requests")
    >>> print(key)
    'a1b2c3d4e5f6...'
    """
    # Convert all args to strings and join
    key_string = "|".join(str(arg) for arg in args)
    return hashlib.sha1(key_string.encode()).hexdigest()


def get_cached(key: str) -> dict[str, Any] | None:
    """
    Retrieve a cached result by key.

    Parameters
    ----------
    key : str
        Cache key (typically from cache_key()).

    Returns
    -------
    dict[str, Any] | None
        Cached result if found, None otherwise.
    """
    with span("cache.get", cache_key=key):
        cache_path = _get_cache_path()

        if not cache_path.exists():
            metric_counter("cache.miss.no_file")(1)
            return None

        try:
            # Read cache file and find matching entry
            with open(cache_path, "r") as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        if entry.get("key") == key:
                            metric_counter("cache.hit")(1)
                            return entry.get("value")
                    except json.JSONDecodeError:
                        continue

            metric_counter("cache.miss.not_found")(1)
            return None

        except Exception as e:
            metric_counter("cache.error.read")(1)
            return None


def set_cached(key: str, value: dict[str, Any], ttl: int | None = None) -> None:
    """
    Store a result in the cache.

    Parameters
    ----------
    key : str
        Cache key (typically from cache_key()).
    value : dict[str, Any]
        Value to cache.
    ttl : int, optional
        Time-to-live in seconds (not currently enforced).
    """
    with span("cache.set", cache_key=key):
        cache_path = _get_cache_path()

        entry = {
            "key": key,
            "value": value,
            "timestamp": time.time(),
            "ttl": ttl,
        }

        try:
            # Append to cache file
            with open(cache_path, "a") as f:
                f.write(json.dumps(entry) + "\n")

            metric_counter("cache.set")(1)

            # Check if pruning needed
            _maybe_prune_cache(cache_path)

        except Exception as e:
            metric_counter("cache.error.write")(1)


def clear_cache() -> int:
    """
    Clear all cached data.

    Returns
    -------
    int
        Number of entries cleared.
    """
    with span("cache.clear"):
        cache_path = _get_cache_path()

        if not cache_path.exists():
            return 0

        try:
            # Count entries
            with open(cache_path, "r") as f:
                count = sum(1 for _ in f)

            # Remove file
            cache_path.unlink()

            metric_counter("cache.cleared")(count)
            return count

        except Exception as e:
            metric_counter("cache.error.clear")(1)
            return 0


def cache_stats() -> dict[str, Any]:
    """
    Get cache statistics.

    Returns
    -------
    dict[str, Any]
        Cache statistics including size, entries, and path.
    """
    with span("cache.stats"):
        cache_path = _get_cache_path()

        if not cache_path.exists():
            return {
                "path": str(cache_path),
                "exists": False,
                "entries": 0,
                "size_bytes": 0,
            }

        try:
            # Count entries and measure size
            with open(cache_path, "r") as f:
                entries = sum(1 for _ in f)

            size = cache_path.stat().st_size

            return {
                "path": str(cache_path),
                "exists": True,
                "entries": entries,
                "size_bytes": size,
            }

        except Exception as e:
            return {
                "path": str(cache_path),
                "exists": True,
                "entries": -1,
                "size_bytes": -1,
                "error": str(e),
            }


def _maybe_prune_cache(cache_path: Path) -> None:
    """Prune cache if it exceeds maximum size."""
    try:
        with open(cache_path, "r") as f:
            lines = f.readlines()

        if len(lines) > _MAX_CACHE_ENTRIES:
            # Keep only the most recent entries
            lines_to_keep = lines[-(_MAX_CACHE_ENTRIES // 2) :]

            with open(cache_path, "w") as f:
                f.writelines(lines_to_keep)

            pruned = len(lines) - len(lines_to_keep)
            metric_counter("cache.pruned")(pruned)

    except Exception:
        # Ignore pruning errors
        pass
