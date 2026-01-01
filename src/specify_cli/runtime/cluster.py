"""Distributed cluster management and coordination.

Manages multi-node clusters with service discovery, membership tracking,
and health monitoring.
"""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from specify_cli.core.shell import timed
from specify_cli.core.telemetry import metric_counter, metric_histogram, span


class NodeRole(Enum):
    """Role of node in cluster."""

    MASTER = "master"
    WORKER = "worker"
    STANDBY = "standby"
    OBSERVER = "observer"


class NodeHealth(Enum):
    """Health status of node."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNREACHABLE = "unreachable"
    DEAD = "dead"


@dataclass
class ClusterNode:
    """Represents a node in cluster."""

    node_id: str
    hostname: str
    port: int
    role: NodeRole = NodeRole.WORKER
    health: NodeHealth = NodeHealth.HEALTHY
    last_heartbeat: float = field(default_factory=time.time)
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    task_count: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    version: str = "1.0.0"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "node_id": self.node_id,
            "hostname": self.hostname,
            "port": self.port,
            "role": self.role.value,
            "health": self.health.value,
            "last_heartbeat": self.last_heartbeat,
            "cpu_usage": self.cpu_usage,
            "memory_usage": self.memory_usage,
            "disk_usage": self.disk_usage,
            "task_count": self.task_count,
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "version": self.version,
        }

    def is_alive(self, timeout_seconds: float = 30.0) -> bool:
        """Check if node is considered alive."""
        age = time.time() - self.last_heartbeat
        return age < timeout_seconds


@dataclass
class ClusterEvent:
    """Event in cluster lifecycle."""

    event_id: str
    timestamp: float
    event_type: str  # "node_joined", "node_left", "node_degraded", etc.
    node_id: str
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "node_id": self.node_id,
            "details": self.details,
        }


@dataclass
class ClusterState:
    """State of entire cluster."""

    cluster_name: str
    cluster_id: str
    created_at: float
    master_node_id: str | None = None
    total_nodes: int = 0
    healthy_nodes: int = 0
    total_capacity: float = 0.0
    used_capacity: float = 0.0
    events: list[ClusterEvent] = field(default_factory=list)


@dataclass
class ClusterMembershipResult:
    """Result of membership operation."""

    success: bool
    node_id: str | None
    message: str
    cluster_size: int
    error: str | None = None


class ClusterManager:
    """Manages distributed cluster operations."""

    def __init__(self, cluster_name: str):
        self.cluster_name = cluster_name
        self.cluster_id = str(uuid.uuid4())[:8]
        self.nodes: dict[str, ClusterNode] = {}
        self.state = ClusterState(
            cluster_name=cluster_name,
            cluster_id=self.cluster_id,
            created_at=time.time(),
        )
        self.event_handlers: dict[str, list[Callable]] = {}
        self.heartbeat_timeout_seconds = 30.0
        self.health_check_interval_seconds = 5.0

    def register_event_handler(self, event_type: str, handler: Callable) -> None:
        """Register handler for cluster events."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)

    @timed
    def add_node(
        self,
        hostname: str,
        port: int,
        role: NodeRole = NodeRole.WORKER,
        version: str = "1.0.0",
    ) -> ClusterMembershipResult:
        """Add node to cluster."""
        with span("cluster.add_node", cluster=self.cluster_name, hostname=hostname):
            node_id = f"{hostname}:{port}"

            if node_id in self.nodes:
                return ClusterMembershipResult(
                    success=False,
                    node_id=node_id,
                    message="node already exists",
                    cluster_size=len(self.nodes),
                    error="duplicate node",
                )

            node = ClusterNode(
                node_id=node_id,
                hostname=hostname,
                port=port,
                role=role,
                version=version,
            )

            self.nodes[node_id] = node
            self.state.total_nodes = len(self.nodes)

            # Update master if this is first master role
            if role == NodeRole.MASTER and self.state.master_node_id is None:
                self.state.master_node_id = node_id

            event = ClusterEvent(
                event_id=str(uuid.uuid4())[:8],
                timestamp=time.time(),
                event_type="node_joined",
                node_id=node_id,
                details={"role": role.value, "version": version},
            )
            self.state.events.append(event)

            self._emit_event("node_joined", event)

            metric_counter(
                "cluster.node_added",
                1,
                {"cluster": self.cluster_name, "role": role.value},
            )

            return ClusterMembershipResult(
                success=True,
                node_id=node_id,
                message="node added successfully",
                cluster_size=len(self.nodes),
            )

    @timed
    def remove_node(self, node_id: str) -> ClusterMembershipResult:
        """Remove node from cluster."""
        with span(
            "cluster.remove_node", cluster=self.cluster_name, node=node_id
        ):
            if node_id not in self.nodes:
                return ClusterMembershipResult(
                    success=False,
                    node_id=node_id,
                    message="node not found",
                    cluster_size=len(self.nodes),
                    error="node does not exist",
                )

            node = self.nodes.pop(node_id)
            self.state.total_nodes = len(self.nodes)

            # Update master if removed node was master
            if self.state.master_node_id == node_id:
                self.state.master_node_id = None

            event = ClusterEvent(
                event_id=str(uuid.uuid4())[:8],
                timestamp=time.time(),
                event_type="node_left",
                node_id=node_id,
                details={"role": node.role.value},
            )
            self.state.events.append(event)

            self._emit_event("node_left", event)

            metric_counter("cluster.node_removed", 1, {"cluster": self.cluster_name})

            return ClusterMembershipResult(
                success=True,
                node_id=node_id,
                message="node removed successfully",
                cluster_size=len(self.nodes),
            )

    @timed
    def heartbeat(
        self,
        node_id: str,
        cpu_usage: float = 0.0,
        memory_usage: float = 0.0,
        disk_usage: float = 0.0,
        task_count: int = 0,
        completed_tasks: int = 0,
        failed_tasks: int = 0,
    ) -> ClusterMembershipResult:
        """Process heartbeat from node."""
        with span("cluster.heartbeat", cluster=self.cluster_name, node=node_id):
            if node_id not in self.nodes:
                return ClusterMembershipResult(
                    success=False,
                    node_id=node_id,
                    message="node not found",
                    cluster_size=len(self.nodes),
                    error="unknown node",
                )

            node = self.nodes[node_id]
            old_health = node.health
            node.last_heartbeat = time.time()
            node.cpu_usage = cpu_usage
            node.memory_usage = memory_usage
            node.disk_usage = disk_usage
            node.task_count = task_count
            node.completed_tasks = completed_tasks
            node.failed_tasks = failed_tasks

            # Determine health
            if cpu_usage > 90 or memory_usage > 90 or disk_usage > 90:
                node.health = NodeHealth.DEGRADED
            else:
                node.health = NodeHealth.HEALTHY

            # Emit event if health changed
            if old_health != node.health:
                event = ClusterEvent(
                    event_id=str(uuid.uuid4())[:8],
                    timestamp=time.time(),
                    event_type="node_health_changed",
                    node_id=node_id,
                    details={
                        "old_health": old_health.value,
                        "new_health": node.health.value,
                    },
                )
                self.state.events.append(event)
                self._emit_event("node_health_changed", event)

            metric_counter(
                "cluster.heartbeat_received",
                1,
                {"cluster": self.cluster_name, "node": node_id},
            )

            self._update_cluster_health()

            return ClusterMembershipResult(
                success=True,
                node_id=node_id,
                message="heartbeat accepted",
                cluster_size=len(self.nodes),
            )

    def check_node_health(self) -> dict[str, Any]:
        """Check health of all nodes."""
        with span("cluster.check_health", cluster=self.cluster_name):
            dead_nodes = []

            for node_id, node in list(self.nodes.items()):
                if not node.is_alive(self.heartbeat_timeout_seconds):
                    dead_nodes.append(node_id)
                    node.health = NodeHealth.DEAD

                    event = ClusterEvent(
                        event_id=str(uuid.uuid4())[:8],
                        timestamp=time.time(),
                        event_type="node_dead",
                        node_id=node_id,
                        details={"timeout_seconds": self.heartbeat_timeout_seconds},
                    )
                    self.state.events.append(event)
                    self._emit_event("node_dead", event)

            self._update_cluster_health()

            return {
                "timestamp": time.time(),
                "total_nodes": len(self.nodes),
                "dead_nodes": dead_nodes,
                "healthy_nodes": self.state.healthy_nodes,
            }

    def _update_cluster_health(self) -> None:
        """Update cluster health metrics."""
        healthy = sum(
            1 for node in self.nodes.values()
            if node.health == NodeHealth.HEALTHY
        )
        self.state.healthy_nodes = healthy

        total_capacity = sum(
            100.0 for _ in self.nodes.values()
        )  # Assume 100 units per node
        used_capacity = sum(
            node.cpu_usage + node.memory_usage + node.disk_usage
            for node in self.nodes.values()
        )

        self.state.total_capacity = total_capacity
        self.state.used_capacity = used_capacity

        metric_histogram(
            "cluster.healthy_nodes",
            float(healthy),
            {"cluster": self.cluster_name},
        )

    def _emit_event(self, event_type: str, event: ClusterEvent) -> None:
        """Emit event to registered handlers."""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    metric_counter(
                        "cluster.event_handler_error",
                        1,
                        {"cluster": self.cluster_name, "event_type": event_type},
                    )

    def get_nodes_by_role(self, role: NodeRole) -> list[ClusterNode]:
        """Get all nodes with specific role."""
        return [
            node for node in self.nodes.values() if node.role == role
        ]

    def get_available_nodes(self) -> list[ClusterNode]:
        """Get all healthy available nodes."""
        return [
            node
            for node in self.nodes.values()
            if node.health == NodeHealth.HEALTHY
        ]

    def get_cluster_state(self) -> dict[str, Any]:
        """Get current cluster state."""
        return {
            "cluster_name": self.cluster_name,
            "cluster_id": self.cluster_id,
            "master_node_id": self.state.master_node_id,
            "total_nodes": self.state.total_nodes,
            "healthy_nodes": self.state.healthy_nodes,
            "total_capacity": self.state.total_capacity,
            "used_capacity": self.state.used_capacity,
            "capacity_utilization": (
                self.state.used_capacity / self.state.total_capacity
                if self.state.total_capacity > 0
                else 0.0
            ),
            "nodes": {
                node_id: node.to_dict()
                for node_id, node in self.nodes.items()
            },
            "recent_events": [
                event.to_dict()
                for event in self.state.events[-10:]
            ],
        }


_global_cluster_manager: ClusterManager | None = None


def get_cluster_manager(cluster_name: str = "primary") -> ClusterManager:
    """Get or create global cluster manager."""
    global _global_cluster_manager
    if _global_cluster_manager is None:
        _global_cluster_manager = ClusterManager(cluster_name)
    return _global_cluster_manager
