from __future__ import annotations

import time
from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable, TypeVar

from specify_cli.core.shell import timed
from specify_cli.core.telemetry import metric_histogram, span

T = TypeVar("T")


@dataclass
class CacheEntry:
    value: Any
    timestamp: float
    ttl: float = 300.0

    def is_expired(self) -> bool:
        return time.time() - self.timestamp > self.ttl


class CacheManager:
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache: dict[str, CacheEntry] = {}
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Any | None:
        if key in self.cache:
            entry = self.cache[key]
            if not entry.is_expired():
                self.hits += 1
                return entry.value
            else:
                del self.cache[key]

        self.misses += 1
        return None

    def set(self, key: str, value: Any, ttl: float = 300.0) -> None:
        if len(self.cache) >= self.max_size:
            oldest_key = min(
                self.cache.keys(),
                key=lambda k: self.cache[k].timestamp,
            )
            del self.cache[oldest_key]

        self.cache[key] = CacheEntry(value=value, timestamp=time.time(), ttl=ttl)

    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    def clear(self) -> None:
        self.cache.clear()
        self.hits = 0
        self.misses = 0

    def cleanup_expired(self) -> int:
        expired_keys = [
            k for k, v in self.cache.items() if v.is_expired()
        ]
        for key in expired_keys:
            del self.cache[key]
        return len(expired_keys)


_global_cache = CacheManager()


def get_cache() -> CacheManager:
    return _global_cache


def cached(ttl: float = 300.0) -> Callable:
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            cache_key = f"{func.__name__}:{args}:{kwargs}"

            cached_value = _global_cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            result = func(*args, **kwargs)
            _global_cache.set(cache_key, result, ttl)
            return result

        return wrapper

    return decorator


class BatchProcessor:
    def __init__(self, batch_size: int = 100):
        self.batch_size = batch_size
        self.queue = []

    def add_item(self, item: Any) -> None:
        self.queue.append(item)

    @timed
    def process(self, handler: Callable) -> list[Any]:
        with span("batch.process", size=len(self.queue)):
            results = []

            for i in range(0, len(self.queue), self.batch_size):
                batch = self.queue[i:i + self.batch_size]
                batch_results = handler(batch)
                results.extend(batch_results)

            metric_histogram("batch.items_processed", len(self.queue))
            return results


class RateLimiter:
    def __init__(self, max_calls: int, time_window: float):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []

    def is_allowed(self) -> bool:
        now = time.time()
        self.calls = [t for t in self.calls if now - t < self.time_window]

        if len(self.calls) < self.max_calls:
            self.calls.append(now)
            return True

        return False

    def wait_if_needed(self) -> None:
        while not self.is_allowed():
            time.sleep(0.1)


@timed
def parallelize_computation(
    items: list[Any],
    handler: Callable[[Any], Any],
    max_workers: int = 4,
) -> list[Any]:
    with span("compute.parallelize", count=len(items)):
        results = []

        for i in range(0, len(items), max_workers):
            batch = items[i:i + max_workers]
            batch_results = [handler(item) for item in batch]
            results.extend(batch_results)

        metric_histogram("compute.items_processed", len(items))
        return results


class AdaptiveThrottler:
    def __init__(self, initial_rate: float = 1.0):
        self.rate = initial_rate
        self.last_adjustment = time.time()

    def adjust_rate(self, success_rate: float) -> None:
        if success_rate > 0.95:
            self.rate *= 1.1
        elif success_rate < 0.8:
            self.rate *= 0.9

        self.last_adjustment = time.time()

    @timed
    def execute_with_throttling(self, handler: Callable) -> Any:
        with span("throttle.execute"):
            result = handler()
            return result


@timed
def memoize_expensive_computation(
    key: str,
    computation: Callable[[], T],
) -> T:
    with span("compute.memoize", key=key):
        cache = get_cache()
        cached = cache.get(key)

        if cached is not None:
            return cached

        result = computation()
        cache.set(key, result, ttl=600.0)
        return result
