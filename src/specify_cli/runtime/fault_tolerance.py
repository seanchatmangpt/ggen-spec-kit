"""Fault tolerance, recovery, and resilience mechanisms.

Implements health checking, automatic failover, and recovery strategies
for distributed systems.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from specify_cli.core.shell import timed
from specify_cli.core.telemetry import metric_counter, metric_histogram, span


class RecoveryStrategy(Enum):
    """Strategy for recovering from failures."""

    IMMEDIATE_RETRY = "immediate_retry"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    ADAPTIVE_RETRY = "adaptive_retry"
    CIRCUIT_BREAKER = "circuit_breaker"
    FALLBACK = "fallback"


class HealthCheckType(Enum):
    """Type of health check."""

    PING = "ping"
    CUSTOM = "custom"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"


@dataclass
class HealthCheckResult:
    """Result of health check."""

    check_id: str
    timestamp: float
    check_type: HealthCheckType
    target_id: str
    success: bool
    latency_ms: float
    details: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "check_id": self.check_id,
            "timestamp": self.timestamp,
            "check_type": self.check_type.value,
            "target_id": self.target_id,
            "success": self.success,
            "latency_ms": self.latency_ms,
            "details": self.details,
            "error": self.error,
        }


@dataclass
class CircuitBreakerState:
    """State of circuit breaker."""

    target_id: str
    state: str = "closed"  # closed, open, half_open
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: float | None = None
    last_success_time: float | None = None
    threshold: int = 5
    success_threshold: int = 2
    timeout_seconds: float = 60.0

    def is_available(self) -> bool:
        """Check if target is available."""
        if self.state == "closed":
            return True
        elif self.state == "open":
            if self.last_failure_time:
                age = time.time() - self.last_failure_time
                if age > self.timeout_seconds:
                    self.state = "half_open"
                    self.success_count = 0
                    return True
            return False
        elif self.state == "half_open":
            return True

        return False

    def record_success(self) -> None:
        """Record successful operation."""
        self.last_success_time = time.time()

        if self.state == "half_open":
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self.state = "closed"
                self.failure_count = 0
                self.success_count = 0
        elif self.state == "closed":
            self.failure_count = max(0, self.failure_count - 1)

    def record_failure(self) -> None:
        """Record failed operation."""
        self.last_failure_time = time.time()
        self.failure_count += 1

        if self.state == "closed" and self.failure_count >= self.threshold:
            self.state = "open"
        elif self.state == "half_open":
            self.state = "open"
            self.success_count = 0


@dataclass
class RetryPolicy:
    """Policy for retrying failed operations."""

    strategy: RecoveryStrategy = RecoveryStrategy.EXPONENTIAL_BACKOFF
    max_attempts: int = 3
    initial_delay_ms: float = 100.0
    max_delay_ms: float = 30000.0
    multiplier: float = 2.0
    jitter_factor: float = 0.1
    timeout_ms: float = 30000.0


@dataclass
class RecoveryAttempt:
    """Record of recovery attempt."""

    attempt_id: str
    timestamp: float
    target_id: str
    attempt_number: int
    strategy: RecoveryStrategy
    success: bool
    error: str | None = None
    recovery_time_ms: float = 0.0


class HealthChecker:
    """Performs health checks on system components."""

    def __init__(self, check_interval_seconds: float = 30.0):
        self.check_interval_seconds = check_interval_seconds
        self.health_checks: dict[str, Callable] = {}
        self.last_check_time: dict[str, float] = {}
        self.check_results: dict[str, list[HealthCheckResult]] = {}
        self.failed_targets: set[str] = set()

    def register_health_check(
        self,
        target_id: str,
        check_func: Callable,
        check_type: HealthCheckType = HealthCheckType.CUSTOM,
    ) -> None:
        """Register health check for target."""
        self.health_checks[target_id] = (check_func, check_type)
        self.check_results[target_id] = []

    @timed
    def check_health(self, target_id: str) -> HealthCheckResult:
        """Perform health check on target."""
        with span("fault_tolerance.check_health", target=target_id):
            if target_id not in self.health_checks:
                return HealthCheckResult(
                    check_id=str(uuid.uuid4())[:8],
                    timestamp=time.time(),
                    check_type=HealthCheckType.PING,
                    target_id=target_id,
                    success=False,
                    latency_ms=0.0,
                    error="no health check registered",
                )

            check_func, check_type = self.health_checks[target_id]
            start_time = time.time()

            try:
                result = check_func()
                latency_ms = (time.time() - start_time) * 1000

                health_result = HealthCheckResult(
                    check_id=str(uuid.uuid4())[:8],
                    timestamp=time.time(),
                    check_type=check_type,
                    target_id=target_id,
                    success=result if isinstance(result, bool) else True,
                    latency_ms=latency_ms,
                    details=(
                        result if isinstance(result, dict) else {}
                    ),
                )

                if not health_result.success:
                    self.failed_targets.add(target_id)
                else:
                    self.failed_targets.discard(target_id)

                self.check_results[target_id].append(health_result)
                self.last_check_time[target_id] = time.time()

                metric_counter(
                    "fault_tolerance.health_check",
                    1,
                    {
                        "target": target_id,
                        "status": "pass" if health_result.success else "fail",
                    },
                )

                return health_result

            except Exception as e:
                latency_ms = (time.time() - start_time) * 1000

                health_result = HealthCheckResult(
                    check_id=str(uuid.uuid4())[:8],
                    timestamp=time.time(),
                    check_type=check_type,
                    target_id=target_id,
                    success=False,
                    latency_ms=latency_ms,
                    error=str(e),
                )

                self.failed_targets.add(target_id)
                self.check_results[target_id].append(health_result)

                metric_counter(
                    "fault_tolerance.health_check",
                    1,
                    {"target": target_id, "status": "error"},
                )

                return health_result

    def check_all_targets(self) -> dict[str, HealthCheckResult]:
        """Check health of all registered targets."""
        with span("fault_tolerance.check_all_targets"):
            results = {}

            for target_id in self.health_checks.keys():
                results[target_id] = self.check_health(target_id)

            return results

    def get_health_summary(self) -> dict[str, Any]:
        """Get summary of health across all targets."""
        total = len(self.health_checks)
        failed = len(self.failed_targets)
        healthy = total - failed

        return {
            "total_targets": total,
            "healthy_targets": healthy,
            "failed_targets": list(self.failed_targets),
            "health_percentage": (
                healthy / total * 100 if total > 0 else 0.0
            ),
        }


class FaultTolerance:
    """Manages fault tolerance and recovery."""

    def __init__(self, health_checker: HealthChecker | None = None):
        self.health_checker = health_checker or HealthChecker()
        self.circuit_breakers: dict[str, CircuitBreakerState] = {}
        self.recovery_attempts: list[RecoveryAttempt] = []
        self.retry_policies: dict[str, RetryPolicy] = {}
        self.fallback_handlers: dict[str, Callable] = {}

    def register_circuit_breaker(
        self,
        target_id: str,
        threshold: int = 5,
        timeout_seconds: float = 60.0,
    ) -> None:
        """Register circuit breaker for target."""
        self.circuit_breakers[target_id] = CircuitBreakerState(
            target_id=target_id,
            threshold=threshold,
            timeout_seconds=timeout_seconds,
        )

    def register_retry_policy(
        self,
        target_id: str,
        policy: RetryPolicy,
    ) -> None:
        """Register retry policy for target."""
        self.retry_policies[target_id] = policy

    def register_fallback(
        self,
        target_id: str,
        handler: Callable,
    ) -> None:
        """Register fallback handler for target."""
        self.fallback_handlers[target_id] = handler

    @timed
    def execute_with_fallback(
        self,
        target_id: str,
        operation: Callable,
        *args: Any,
        **kwargs: Any,
    ) -> tuple[bool, Any]:
        """Execute operation with fallback on failure."""
        with span(
            "fault_tolerance.execute_with_fallback", target=target_id
        ):
            # Check circuit breaker
            if target_id in self.circuit_breakers:
                breaker = self.circuit_breakers[target_id]
                if not breaker.is_available():
                    if target_id in self.fallback_handlers:
                        try:
                            result = self.fallback_handlers[target_id](
                                *args, **kwargs
                            )
                            return (True, result)
                        except Exception as e:
                            return (False, str(e))
                    else:
                        return (False, "circuit breaker open")

            # Get retry policy
            policy = self.retry_policies.get(
                target_id,
                RetryPolicy(),
            )

            # Execute with retries
            attempt = 0
            last_error = None
            start_time = time.time()

            while attempt < policy.max_attempts:
                try:
                    result = operation(*args, **kwargs)

                    if target_id in self.circuit_breakers:
                        self.circuit_breakers[target_id].record_success()

                    return (True, result)

                except Exception as e:
                    last_error = str(e)
                    attempt += 1

                    if target_id in self.circuit_breakers:
                        self.circuit_breakers[target_id].record_failure()

                    metric_counter(
                        "fault_tolerance.operation_failed",
                        1,
                        {
                            "target": target_id,
                            "attempt": str(attempt),
                        },
                    )

                    if attempt < policy.max_attempts:
                        delay = self._calculate_delay(
                            attempt,
                            policy,
                        )
                        time.sleep(delay / 1000.0)

            # All retries exhausted, use fallback
            if target_id in self.fallback_handlers:
                try:
                    result = self.fallback_handlers[target_id](
                        *args, **kwargs
                    )
                    recovery_time_ms = (
                        (time.time() - start_time) * 1000
                    )

                    self.recovery_attempts.append(
                        RecoveryAttempt(
                            attempt_id=str(uuid.uuid4())[:8],
                            timestamp=time.time(),
                            target_id=target_id,
                            attempt_number=attempt,
                            strategy=policy.strategy,
                            success=True,
                            recovery_time_ms=recovery_time_ms,
                        )
                    )

                    return (True, result)
                except Exception as e:
                    last_error = str(e)

            recovery_time_ms = (time.time() - start_time) * 1000
            self.recovery_attempts.append(
                RecoveryAttempt(
                    attempt_id=str(uuid.uuid4())[:8],
                    timestamp=time.time(),
                    target_id=target_id,
                    attempt_number=attempt,
                    strategy=policy.strategy,
                    success=False,
                    error=last_error,
                    recovery_time_ms=recovery_time_ms,
                )
            )

            return (False, last_error)

    def _calculate_delay(
        self,
        attempt: int,
        policy: RetryPolicy,
    ) -> float:
        """Calculate delay for retry."""
        if policy.strategy == RecoveryStrategy.IMMEDIATE_RETRY:
            return 0.0
        elif policy.strategy == RecoveryStrategy.EXPONENTIAL_BACKOFF:
            delay = (
                policy.initial_delay_ms
                * (policy.multiplier ** (attempt - 1))
            )
            delay = min(delay, policy.max_delay_ms)

            # Add jitter
            import random
            jitter = delay * policy.jitter_factor * random.random()
            return delay + jitter
        else:
            return policy.initial_delay_ms

    def get_fault_tolerance_status(self) -> dict[str, Any]:
        """Get overall fault tolerance status."""
        breaker_states = {
            target_id: breaker.state
            for target_id, breaker in self.circuit_breakers.items()
        }

        return {
            "circuit_breakers": breaker_states,
            "health_summary": self.health_checker.get_health_summary(),
            "recovery_attempts": len(self.recovery_attempts),
            "last_recovery_attempt": (
                self.recovery_attempts[-1].to_dict()
                if self.recovery_attempts
                else None
            ),
        }


def create_fault_tolerance() -> FaultTolerance:
    """Create fault tolerance instance."""
    health_checker = HealthChecker(check_interval_seconds=30.0)
    return FaultTolerance(health_checker)
