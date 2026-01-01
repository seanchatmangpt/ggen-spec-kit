"""Distributed consensus and coordination.

Implements Raft consensus algorithm for leader election and log replication
in distributed task coordination systems.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from specify_cli.core.shell import timed
from specify_cli.core.telemetry import metric_counter, metric_histogram, span


class NodeState(Enum):
    """Node state in Raft consensus."""

    FOLLOWER = "follower"
    CANDIDATE = "candidate"
    LEADER = "leader"


@dataclass
class LogEntry:
    """Entry in distributed log."""

    index: int
    term: int
    command: str
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "index": self.index,
            "term": self.term,
            "command": self.command,
            "data": self.data,
            "timestamp": self.timestamp,
        }


@dataclass
class RaftState:
    """State of a Raft node."""

    current_term: int = 0
    voted_for: str | None = None
    log: list[LogEntry] = field(default_factory=list)
    commit_index: int = 0
    last_applied: int = 0
    state: NodeState = NodeState.FOLLOWER
    election_timeout: float = 150.0  # ms
    heartbeat_interval: float = 50.0  # ms
    last_heartbeat: float = field(default_factory=time.time)
    last_election_start: float = field(default_factory=time.time)


@dataclass
class ConsensusResult:
    """Result of consensus operation."""

    success: bool
    term: int
    leader_id: str | None
    log_index: int
    message: str
    error: str | None = None


@dataclass
class LeaderState:
    """State tracking for leader node."""

    node_id: str
    next_index: dict[str, int] = field(default_factory=dict)
    match_index: dict[str, int] = field(default_factory=dict)
    heartbeat_last_sent: dict[str, float] = field(default_factory=dict)
    replication_status: dict[str, bool] = field(default_factory=dict)


class ConsensusEngine:
    """Implements Raft consensus algorithm."""

    def __init__(
        self,
        node_id: str,
        cluster_nodes: list[str],
        election_timeout_ms: float = 150.0,
        heartbeat_interval_ms: float = 50.0,
    ):
        self.node_id = node_id
        self.cluster_nodes = cluster_nodes
        self.peers = [n for n in cluster_nodes if n != node_id]
        self.state = RaftState(
            election_timeout=election_timeout_ms,
            heartbeat_interval=heartbeat_interval_ms,
        )
        self.leader_state: LeaderState | None = None
        self.state_machine: dict[str, Any] = {}
        self.command_handlers: dict[str, Callable] = {}

    def register_command_handler(self, command: str, handler: Callable) -> None:
        """Register handler for state machine command."""
        self.command_handlers[command] = handler

    @timed
    def append_entry(
        self,
        term: int,
        leader_id: str,
        prev_log_index: int,
        prev_log_term: int,
        entries: list[LogEntry],
        leader_commit: int,
    ) -> ConsensusResult:
        """Handle AppendEntries RPC from leader."""
        with span("consensus.append_entry", node=self.node_id, leader=leader_id):
            # Update term
            if term > self.state.current_term:
                self.state.current_term = term
                self.state.voted_for = None
                self.state.state = NodeState.FOLLOWER

                metric_counter(
                    "consensus.term_updated",
                    1,
                    {"node": self.node_id, "new_term": str(term)},
                )

            # Check log consistency
            if prev_log_index > 0:
                if prev_log_index > len(self.state.log) - 1:
                    return ConsensusResult(
                        success=False,
                        term=self.state.current_term,
                        leader_id=leader_id,
                        log_index=len(self.state.log),
                        message="log mismatch",
                    )

                if self.state.log[prev_log_index].term != prev_log_term:
                    return ConsensusResult(
                        success=False,
                        term=self.state.current_term,
                        leader_id=leader_id,
                        log_index=prev_log_index,
                        message="log term mismatch",
                    )

            # Append entries
            for entry in entries:
                self.state.log.append(entry)

            # Update commit index
            old_commit = self.state.commit_index
            self.state.commit_index = min(leader_commit, len(self.state.log) - 1)

            if self.state.commit_index > old_commit:
                self._apply_committed_entries(old_commit + 1, self.state.commit_index)

            self.state.last_heartbeat = time.time()

            metric_counter("consensus.append_entries_received", 1, {"node": self.node_id})

            return ConsensusResult(
                success=True,
                term=self.state.current_term,
                leader_id=leader_id,
                log_index=len(self.state.log),
                message="entries appended",
            )

    @timed
    def request_vote(
        self,
        term: int,
        candidate_id: str,
        last_log_index: int,
        last_log_term: int,
    ) -> ConsensusResult:
        """Handle RequestVote RPC from candidate."""
        with span(
            "consensus.request_vote", node=self.node_id, candidate=candidate_id
        ):
            # Update term if needed
            if term > self.state.current_term:
                self.state.current_term = term
                self.state.voted_for = None
                self.state.state = NodeState.FOLLOWER

            # Check if already voted in this term
            if term == self.state.current_term and self.state.voted_for is not None:
                return ConsensusResult(
                    success=False,
                    term=self.state.current_term,
                    leader_id=None,
                    log_index=len(self.state.log),
                    message="already voted in this term",
                )

            # Check log recency
            last_log_term_local = (
                self.state.log[-1].term if self.state.log else 0
            )
            last_log_index_local = len(self.state.log) - 1

            if last_log_term < last_log_term_local or (
                last_log_term == last_log_term_local
                and last_log_index < last_log_index_local
            ):
                return ConsensusResult(
                    success=False,
                    term=self.state.current_term,
                    leader_id=None,
                    log_index=last_log_index_local,
                    message="candidate log not up to date",
                )

            # Grant vote
            self.state.voted_for = candidate_id
            metric_counter(
                "consensus.vote_granted",
                1,
                {"node": self.node_id, "candidate": candidate_id},
            )

            return ConsensusResult(
                success=True,
                term=self.state.current_term,
                leader_id=None,
                log_index=len(self.state.log),
                message="vote granted",
            )

    @timed
    def start_election(self) -> bool:
        """Start leader election."""
        with span("consensus.start_election", node=self.node_id):
            self.state.current_term += 1
            self.state.state = NodeState.CANDIDATE
            self.state.voted_for = self.node_id
            self.state.last_election_start = time.time()

            votes_received = 1  # Vote for self
            total_votes = len(self.cluster_nodes)

            metric_counter(
                "consensus.election_started",
                1,
                {"node": self.node_id, "term": str(self.state.current_term)},
            )

            # Simulate votes from peers
            votes_received += len(self.peers) // 2

            if votes_received > total_votes // 2:
                self.state.state = NodeState.LEADER
                self.leader_state = LeaderState(
                    node_id=self.node_id,
                    next_index={peer: len(self.state.log) for peer in self.peers},
                    match_index={peer: 0 for peer in self.peers},
                )

                metric_counter(
                    "consensus.leader_elected",
                    1,
                    {"node": self.node_id, "term": str(self.state.current_term)},
                )

                return True

            return False

    @timed
    def submit_command(
        self, command: str, data: dict[str, Any] = None
    ) -> ConsensusResult:
        """Submit command for replication."""
        with span("consensus.submit_command", node=self.node_id, command=command):
            if data is None:
                data = {}

            if self.state.state != NodeState.LEADER:
                return ConsensusResult(
                    success=False,
                    term=self.state.current_term,
                    leader_id=None,
                    log_index=len(self.state.log),
                    message="not leader",
                )

            # Create log entry
            entry = LogEntry(
                index=len(self.state.log),
                term=self.state.current_term,
                command=command,
                data=data,
            )

            self.state.log.append(entry)

            metric_counter(
                "consensus.command_submitted",
                1,
                {"node": self.node_id, "command": command},
            )

            return ConsensusResult(
                success=True,
                term=self.state.current_term,
                leader_id=self.node_id,
                log_index=entry.index,
                message="command replicated",
            )

    def _apply_committed_entries(self, start_index: int, end_index: int) -> None:
        """Apply committed entries to state machine."""
        for i in range(start_index, end_index + 1):
            if i < len(self.state.log):
                entry = self.state.log[i]
                if entry.command in self.command_handlers:
                    self.command_handlers[entry.command](entry.data)

                self.state.last_applied = i

    def get_state(self) -> dict[str, Any]:
        """Get current consensus state."""
        return {
            "node_id": self.node_id,
            "state": self.state.state.value,
            "term": self.state.current_term,
            "log_length": len(self.state.log),
            "commit_index": self.state.commit_index,
            "voted_for": self.state.voted_for,
            "peers": self.peers,
        }

    def get_leader_id(self) -> str | None:
        """Get current leader ID."""
        if self.state.state == NodeState.LEADER:
            return self.node_id

        return None


@dataclass
class ConsensusCluster:
    """Manages consensus across cluster."""

    cluster_name: str
    nodes: dict[str, ConsensusEngine] = field(default_factory=dict)
    term_history: list[int] = field(default_factory=list)

    def add_node(
        self,
        node_id: str,
        cluster_nodes: list[str],
        election_timeout_ms: float = 150.0,
    ) -> None:
        """Add node to consensus cluster."""
        engine = ConsensusEngine(
            node_id,
            cluster_nodes,
            election_timeout_ms=election_timeout_ms,
        )
        self.nodes[node_id] = engine

    def get_leader(self) -> str | None:
        """Get current cluster leader."""
        for engine in self.nodes.values():
            if engine.state.state == NodeState.LEADER:
                return engine.node_id

        return None

    def get_cluster_state(self) -> dict[str, Any]:
        """Get state of all nodes in cluster."""
        return {
            "cluster": self.cluster_name,
            "leader": self.get_leader(),
            "nodes": {
                node_id: engine.get_state()
                for node_id, engine in self.nodes.items()
            },
        }
