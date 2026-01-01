from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from specify_cli.core.shell import timed
from specify_cli.core.telemetry import metric_counter, metric_histogram, span


class LoadBalancingStrategy(Enum):
    ROUND_ROBIN = "round_robin"
    LEAST_LOADED = "least_loaded"
    RANDOM = "random"
    WEIGHTED = "weighted"


@dataclass
class Endpoint:
    endpoint_id: str
    address: str
    port: int
    capacity: int = 100
    current_load: int = 0
    weight: float = 1.0
    healthy: bool = True

    def is_available(self) -> bool:
        return self.healthy and self.current_load < self.capacity

    def available_capacity(self) -> int:
        return self.capacity - self.current_load


@dataclass
class Request:
    request_id: str
    endpoint: Endpoint
    payload: dict[str, Any]
    timestamp: float
    status: str = "pending"
    response: Any | None = None
    error: str | None = None


class LoadBalancer:
    def __init__(self, strategy: LoadBalancingStrategy = LoadBalancingStrategy.LEAST_LOADED):
        self.endpoints: list[Endpoint] = []
        self.strategy = strategy
        self.requests: dict[str, Request] = {}
        self.round_robin_index = 0

    def register_endpoint(self, endpoint: Endpoint) -> None:
        self.endpoints.append(endpoint)

    def deregister_endpoint(self, endpoint_id: str) -> None:
        self.endpoints = [e for e in self.endpoints if e.endpoint_id != endpoint_id]

    def _select_endpoint(self) -> Endpoint | None:
        available = [e for e in self.endpoints if e.is_available()]

        if not available:
            return None

        if self.strategy == LoadBalancingStrategy.ROUND_ROBIN:
            selected = available[self.round_robin_index % len(available)]
            self.round_robin_index += 1
            return selected

        elif self.strategy == LoadBalancingStrategy.LEAST_LOADED:
            return min(available, key=lambda e: e.current_load)

        elif self.strategy == LoadBalancingStrategy.WEIGHTED:
            total_weight = sum(e.weight for e in available)
            weights = [e.weight / total_weight for e in available]
            import random

            return random.choices(available, weights=weights)[0]

        else:
            import random

            return random.choice(available)

    @timed
    def route_request(self, payload: dict[str, Any]) -> str:
        with span("lb.route_request"):
            endpoint = self._select_endpoint()

            if not endpoint:
                raise RuntimeError("No available endpoints")

            request = Request(
                request_id=str(uuid.uuid4())[:8],
                endpoint=endpoint,
                payload=payload,
                timestamp=__import__("time").time(),
            )

            endpoint.current_load += 1
            self.requests[request.request_id] = request

            metric_counter("lb.requests_routed", 1)
            metric_histogram("lb.endpoint_load", endpoint.current_load)

            return request.request_id

    def complete_request(self, request_id: str, response: Any | None = None) -> None:
        if request_id in self.requests:
            request = self.requests[request_id]
            request.status = "completed"
            request.response = response
            request.endpoint.current_load -= 1

    def fail_request(self, request_id: str, error: str) -> None:
        if request_id in self.requests:
            request = self.requests[request_id]
            request.status = "failed"
            request.error = error
            request.endpoint.current_load -= 1

    def get_status(self) -> dict[str, Any]:
        return {
            "total_endpoints": len(self.endpoints),
            "healthy_endpoints": sum(1 for e in self.endpoints if e.healthy),
            "total_load": sum(e.current_load for e in self.endpoints),
            "total_capacity": sum(e.capacity for e in self.endpoints),
            "pending_requests": sum(
                1 for r in self.requests.values() if r.status == "pending"
            ),
        }


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout_seconds: float = 60.0):
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"

    def is_open(self) -> bool:
        if self.state == "open":
            import time

            if (
                self.last_failure_time
                and time.time() - self.last_failure_time > self.timeout_seconds
            ):
                self.state = "half_open"
                return False

            return True

        return False

    def record_success(self) -> None:
        self.failure_count = 0
        self.state = "closed"

    def record_failure(self) -> None:
        import time

        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = "open"

    @timed
    def execute(self, func: Callable, *args: Any, **kwargs: Any) -> Any:
        with span("circuit_breaker.execute", state=self.state):
            if self.is_open():
                raise RuntimeError("Circuit breaker is open")

            try:
                result = func(*args, **kwargs)
                self.record_success()
                return result
            except Exception as e:
                self.record_failure()
                raise


class RateLimitingGateway:
    def __init__(self, max_requests_per_second: int = 1000):
        self.max_requests_per_second = max_requests_per_second
        self.request_times: list[float] = []

    @timed
    def check_rate_limit(self) -> bool:
        import time

        now = time.time()
        self.request_times = [t for t in self.request_times if now - t < 1.0]

        if len(self.request_times) < self.max_requests_per_second:
            self.request_times.append(now)
            return True

        return False

    def get_current_rate(self) -> int:
        import time

        now = time.time()
        return len([t for t in self.request_times if now - t < 1.0])


@dataclass
class APIGatewayConfig:
    max_endpoints: int = 10
    load_balancing_strategy: LoadBalancingStrategy = LoadBalancingStrategy.LEAST_LOADED
    circuit_breaker_threshold: int = 5
    rate_limit_per_second: int = 1000


class APIGateway:
    def __init__(self, config: APIGatewayConfig):
        self.config = config
        self.load_balancer = LoadBalancer(config.load_balancing_strategy)
        self.circuit_breaker = CircuitBreaker(config.circuit_breaker_threshold)
        self.rate_limiter = RateLimitingGateway(config.rate_limit_per_second)

    @timed
    def handle_request(self, payload: dict[str, Any]) -> dict[str, Any]:
        with span("gateway.handle_request"):
            if not self.rate_limiter.check_rate_limit():
                metric_counter("gateway.rate_limited", 1)
                return {"error": "Rate limit exceeded"}

            try:
                request_id = self.load_balancer.route_request(payload)

                def process():
                    return {"request_id": request_id, "status": "processed"}

                result = self.circuit_breaker.execute(process)
                self.load_balancer.complete_request(request_id, result)

                metric_counter("gateway.requests_handled", 1)
                return result

            except Exception as e:
                metric_counter("gateway.errors", 1)
                raise

    def get_status(self) -> dict[str, Any]:
        return {
            "load_balancer": self.load_balancer.get_status(),
            "circuit_breaker": {
                "state": self.circuit_breaker.state,
                "failures": self.circuit_breaker.failure_count,
            },
            "rate_limiter": {
                "current_rate": self.rate_limiter.get_current_rate(),
                "max_rate": self.rate_limiter.max_requests_per_second,
            },
        }
