from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from specify_cli.core.shell import timed
from specify_cli.core.telemetry import metric_counter, metric_histogram, span


class AgentRole(Enum):
    ANALYZER = "analyzer"
    EXECUTOR = "executor"
    MONITOR = "monitor"
    COORDINATOR = "coordinator"


@dataclass
class AgentTask:
    task_id: str
    description: str
    required_role: AgentRole
    input_data: dict[str, Any] = field(default_factory=dict)
    output_data: dict[str, Any] = field(default_factory=dict)
    status: str = "pending"
    priority: int = 0


@dataclass
class AgentCapabilities:
    role: AgentRole
    skills: list[str] = field(default_factory=list)
    max_concurrent_tasks: int = 5
    success_rate: float = 0.95


class AutonomousAgent:
    def __init__(self, agent_id: str, capabilities: AgentCapabilities):
        self.agent_id = agent_id
        self.capabilities = capabilities
        self.task_queue = []
        self.completed_tasks = []
        self.current_task = None

    def accept_task(self, task: AgentTask) -> bool:
        if task.required_role == self.capabilities.role:
            self.task_queue.append(task)
            return True
        return False

    @timed
    def execute_task(self, task: AgentTask) -> dict[str, Any]:
        with span(f"agent.execute", agent=self.agent_id, task=task.task_id):
            self.current_task = task
            task.status = "running"

            try:
                result = self._process_task(task)
                task.status = "completed"
                task.output_data = result
                self.completed_tasks.append(task)

                metric_counter("agent.task_completed", 1, {
                    "agent": self.agent_id,
                    "role": self.capabilities.role.value,
                })

                return {"success": True, "result": result}

            except Exception as e:
                task.status = "failed"
                metric_counter("agent.task_failed", 1, {"agent": self.agent_id})
                return {"success": False, "error": str(e)}

    def _process_task(self, task: AgentTask) -> dict[str, Any]:
        if self.capabilities.role == AgentRole.ANALYZER:
            return self._analyze(task)
        elif self.capabilities.role == AgentRole.EXECUTOR:
            return self._execute(task)
        elif self.capabilities.role == AgentRole.MONITOR:
            return self._monitor(task)
        else:
            return self._coordinate(task)

    def _analyze(self, task: AgentTask) -> dict[str, Any]:
        return {
            "analysis_type": "comprehensive",
            "findings": len(task.input_data),
            "recommendations": 5,
        }

    def _execute(self, task: AgentTask) -> dict[str, Any]:
        return {
            "actions_taken": 3,
            "success_rate": self.capabilities.success_rate,
            "resources_used": 25,
        }

    def _monitor(self, task: AgentTask) -> dict[str, Any]:
        return {
            "metrics_collected": 10,
            "anomalies_detected": 1,
            "alerts_issued": 0,
        }

    def _coordinate(self, task: AgentTask) -> dict[str, Any]:
        return {
            "agents_coordinated": 3,
            "tasks_assigned": 5,
            "overall_progress": 0.85,
        }

    def get_status(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "role": self.capabilities.role.value,
            "current_task": self.current_task.task_id if self.current_task else None,
            "completed_tasks": len(self.completed_tasks),
            "pending_tasks": len(self.task_queue),
        }


@dataclass
class AgentCoordinationResult:
    success: bool
    agents_used: list[str] = field(default_factory=list)
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_duration: float = 0.0
    coordination_efficiency: float = 0.0


class MultiAgentOrchestrator:
    def __init__(self):
        self.agents: dict[str, AutonomousAgent] = {}
        self.task_log = []

    def register_agent(self, agent: AutonomousAgent) -> None:
        self.agents[agent.agent_id] = agent

    def _get_agent_for_task(self, task: AgentTask) -> AutonomousAgent | None:
        candidates = [
            a for a in self.agents.values()
            if a.capabilities.role == task.required_role
        ]

        if candidates:
            return min(candidates, key=lambda a: len(a.task_queue))
        return None

    @timed
    def dispatch_task(self, task: AgentTask) -> dict[str, Any]:
        with span("orchestration.dispatch_task", task=task.task_id):
            agent = self._get_agent_for_task(task)

            if not agent:
                return {
                    "success": False,
                    "error": f"No agent available for role {task.required_role}",
                }

            if agent.accept_task(task):
                result = agent.execute_task(task)
                self.task_log.append((task.task_id, result))
                return result

            return {"success": False, "error": "Agent rejected task"}

    @timed
    def dispatch_multiple_tasks(
        self,
        tasks: list[AgentTask],
    ) -> AgentCoordinationResult:
        with span("orchestration.dispatch_multiple", count=len(tasks)):
            result = AgentCoordinationResult(success=True)

            for task in tasks:
                dispatch_result = self.dispatch_task(task)
                if dispatch_result["success"]:
                    result.tasks_completed += 1
                    result.agents_used.append(task.task_id)
                else:
                    result.tasks_failed += 1

            result.coordination_efficiency = (
                result.tasks_completed / len(tasks) if tasks else 0
            )

            metric_counter("orchestration.tasks_dispatched", len(tasks))
            metric_histogram("orchestration.success_rate", result.coordination_efficiency)

            return result

    def get_system_status(self) -> dict[str, Any]:
        return {
            "total_agents": len(self.agents),
            "agents_by_role": self._count_by_role(),
            "tasks_completed": len(self.task_log),
            "agent_status": {
                agent_id: agent.get_status()
                for agent_id, agent in self.agents.items()
            },
        }

    def _count_by_role(self) -> dict[str, int]:
        counts = {}
        for agent in self.agents.values():
            role = agent.capabilities.role.value
            counts[role] = counts.get(role, 0) + 1
        return counts


@timed
def create_agent_team(team_config: dict[str, Any]) -> MultiAgentOrchestrator:
    with span("agent_team.creation", size=team_config.get("size", 0)):
        orchestrator = MultiAgentOrchestrator()

        analyzer = AutonomousAgent(
            "analyzer-1",
            AgentCapabilities(
                role=AgentRole.ANALYZER,
                skills=["data_analysis", "pattern_recognition", "anomaly_detection"],
            ),
        )
        orchestrator.register_agent(analyzer)

        executor = AutonomousAgent(
            "executor-1",
            AgentCapabilities(
                role=AgentRole.EXECUTOR,
                skills=["task_execution", "resource_management", "error_recovery"],
            ),
        )
        orchestrator.register_agent(executor)

        monitor = AutonomousAgent(
            "monitor-1",
            AgentCapabilities(
                role=AgentRole.MONITOR,
                skills=["metrics_collection", "health_check", "alerting"],
            ),
        )
        orchestrator.register_agent(monitor)

        coordinator = AutonomousAgent(
            "coordinator-1",
            AgentCapabilities(
                role=AgentRole.COORDINATOR,
                skills=["task_scheduling", "resource_allocation", "conflict_resolution"],
            ),
        )
        orchestrator.register_agent(coordinator)

        metric_counter("agent_team.created", 1)
        return orchestrator
