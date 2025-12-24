"""AGI system type definitions and enumerations.

Auto-generated from: ontology/agi-agent-schema.ttl
Constitutional equation: types.py = μ(agi-agent-schema.ttl)
DO NOT EDIT MANUALLY - Edit the RDF source instead.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Priority(str, Enum):
    """Task priority levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Status(str, Enum):
    """Task or agent status."""

    CREATED = "created"
    READY = "ready"
    EXECUTING = "executing"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentType(str, Enum):
    """Types of agents."""

    PLANNER = "planner"
    REASONER = "reasoner"
    IMPLEMENTER = "implementer"
    TESTER = "tester"
    SYNTHESIZER = "synthesizer"
    ORCHESTRATOR = "orchestrator"


class LanguageType(str, Enum):
    """Supported programming languages."""

    PYTHON = "python"
    TYPESCRIPT = "typescript"
    RUST = "rust"
    GO = "go"
    JAVA = "java"


@dataclass
class TaskMetadata:
    """Metadata about a task."""

    task_id: str
    task_name: str
    description: str = ""
    priority: Priority = Priority.MEDIUM
    status: Status = Status.CREATED
    tags: list[str] = field(default_factory=list)


@dataclass
class AgentCapability:
    """Capability of an agent."""

    name: str
    description: str = ""
    required_skills: list[str] = field(default_factory=list)
    version: str = "1.0.0"


@dataclass
class CodeSpecification:
    """Code generation specification."""

    module_name: str
    language: LanguageType
    requirements: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    examples: list[dict[str, str]] = field(default_factory=list)
