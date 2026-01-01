from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from specify_cli.core.shell import timed
from specify_cli.core.telemetry import metric_counter, metric_histogram, span


class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Alert:
    alert_id: str
    severity: AlertSeverity
    message: str
    timestamp: float
    metadata: dict[str, Any] = field(default_factory=dict)
    acknowledged: bool = False


@dataclass
class HealthMetrics:
    timestamp: float
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    active_tasks: int = 0
    failed_tasks: int = 0
    success_rate: float = 1.0


@dataclass
class SystemSnapshot:
    snapshot_time: float
    metrics: HealthMetrics
    active_workflows: int = 0
    total_executions: int = 0
    average_latency_ms: float = 0.0
    error_rate: float = 0.0


class MonitoringSystem:
    def __init__(self):
        self.alerts: list[Alert] = []
        self.metrics_history: list[HealthMetrics] = []
        self.thresholds = {
            "cpu_warning": 0.75,
            "cpu_critical": 0.90,
            "memory_warning": 0.80,
            "memory_critical": 0.95,
            "error_rate_warning": 0.05,
            "error_rate_critical": 0.10,
        }

    def update_metrics(self, metrics: HealthMetrics) -> None:
        self.metrics_history.append(metrics)

        if metrics.cpu_usage > self.thresholds["cpu_critical"]:
            self._raise_alert(
                AlertSeverity.CRITICAL,
                f"CPU usage critical: {metrics.cpu_usage:.1%}",
            )
        elif metrics.cpu_usage > self.thresholds["cpu_warning"]:
            self._raise_alert(
                AlertSeverity.WARNING,
                f"CPU usage elevated: {metrics.cpu_usage:.1%}",
            )

        if metrics.memory_usage > self.thresholds["memory_critical"]:
            self._raise_alert(
                AlertSeverity.CRITICAL,
                f"Memory usage critical: {metrics.memory_usage:.1%}",
            )

    def _raise_alert(self, severity: AlertSeverity, message: str) -> None:
        import uuid

        alert = Alert(
            alert_id=str(uuid.uuid4())[:8],
            severity=severity,
            message=message,
            timestamp=time.time(),
        )
        self.alerts.append(alert)
        metric_counter("alerts.raised", 1, {"severity": severity.value})

    def acknowledge_alert(self, alert_id: str) -> None:
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                break

    def get_active_alerts(self) -> list[Alert]:
        return [a for a in self.alerts if not a.acknowledged]

    def get_recent_metrics(self, limit: int = 100) -> list[HealthMetrics]:
        return self.metrics_history[-limit:]

    def get_health_status(self) -> dict[str, Any]:
        if not self.metrics_history:
            return {"status": "unknown"}

        latest = self.metrics_history[-1]
        active_alerts = self.get_active_alerts()

        status = "healthy"
        if any(a.severity == AlertSeverity.CRITICAL for a in active_alerts):
            status = "critical"
        elif any(a.severity == AlertSeverity.ERROR for a in active_alerts):
            status = "unhealthy"
        elif active_alerts:
            status = "degraded"

        return {
            "status": status,
            "cpu_usage": latest.cpu_usage,
            "memory_usage": latest.memory_usage,
            "active_tasks": latest.active_tasks,
            "success_rate": latest.success_rate,
            "alerts": len(active_alerts),
        }


class DebugTracer:
    def __init__(self):
        self.traces: dict[str, list[str]] = {}
        self.enabled = False

    def enable(self) -> None:
        self.enabled = True

    def disable(self) -> None:
        self.enabled = False

    def trace(self, context: str, event: str) -> None:
        if not self.enabled:
            return

        if context not in self.traces:
            self.traces[context] = []

        self.traces[context].append(f"{time.time()}: {event}")

    def get_trace(self, context: str) -> list[str]:
        return self.traces.get(context, [])

    def clear_trace(self, context: str) -> None:
        if context in self.traces:
            del self.traces[context]

    def clear_all(self) -> None:
        self.traces.clear()


class PerformanceProfiler:
    def __init__(self):
        self.profiles: dict[str, list[float]] = {}

    @timed
    def profile_function(self, func_name: str, duration: float) -> None:
        if func_name not in self.profiles:
            self.profiles[func_name] = []

        self.profiles[func_name].append(duration)
        metric_histogram(f"profile.{func_name}", duration)

    def get_statistics(self, func_name: str) -> dict[str, float]:
        if func_name not in self.profiles or not self.profiles[func_name]:
            return {}

        durations = self.profiles[func_name]
        return {
            "count": len(durations),
            "total": sum(durations),
            "average": sum(durations) / len(durations),
            "min": min(durations),
            "max": max(durations),
            "p95": sorted(durations)[int(len(durations) * 0.95)] if durations else 0,
            "p99": sorted(durations)[int(len(durations) * 0.99)] if durations else 0,
        }

    def get_all_statistics(self) -> dict[str, dict[str, float]]:
        return {
            func_name: self.get_statistics(func_name)
            for func_name in self.profiles
        }


class EventLogger:
    def __init__(self):
        self.events: list[dict[str, Any]] = []

    def log_event(
        self,
        event_type: str,
        message: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        event = {
            "type": event_type,
            "message": message,
            "timestamp": time.time(),
            "metadata": metadata or {},
        }
        self.events.append(event)
        metric_counter("events.logged", 1, {"type": event_type})

    def get_events(
        self,
        event_type: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        events = self.events if not event_type else [
            e for e in self.events if e["type"] == event_type
        ]
        return events[-limit:]

    def clear_events(self, older_than_seconds: int = 3600) -> int:
        cutoff = time.time() - older_than_seconds
        original_count = len(self.events)
        self.events = [e for e in self.events if e["timestamp"] > cutoff]
        return original_count - len(self.events)


_global_monitoring = MonitoringSystem()
_global_tracer = DebugTracer()
_global_profiler = PerformanceProfiler()
_global_event_logger = EventLogger()


def get_monitoring_system() -> MonitoringSystem:
    return _global_monitoring


def get_debug_tracer() -> DebugTracer:
    return _global_tracer


def get_performance_profiler() -> PerformanceProfiler:
    return _global_profiler


def get_event_logger() -> EventLogger:
    return _global_event_logger


@timed
def get_system_health_report() -> dict[str, Any]:
    with span("monitoring.health_report"):
        monitoring = get_monitoring_system()
        profiler = get_performance_profiler()
        logger = get_event_logger()

        return {
            "health": monitoring.get_health_status(),
            "alerts": [
                {
                    "id": a.alert_id,
                    "severity": a.severity.value,
                    "message": a.message,
                }
                for a in monitoring.get_active_alerts()
            ],
            "performance": profiler.get_all_statistics(),
            "recent_events": logger.get_events(limit=20),
        }
