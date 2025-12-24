"""AGI module - Autonomous agent orchestration and code generation.

Auto-generated from: ontology/agi-agent-schema.ttl, ontology/agi-task-planning.ttl, ontology/agi-reasoning.ttl
Constitutional equation: agi.__init__.py = μ(agi-*.ttl)
DO NOT EDIT MANUALLY - Edit the RDF source instead.

The AGI system integrates five core capabilities:

1. **Task Planning**: Goal decomposition → task graph → critical path → execution plan
2. **Reasoning**: Chain-of-thought → design alternatives → risk assessment → decision making
3. **Code Synthesis**: NL specification → RDF IR → code generation → test generation
4. **Orchestration**: Agent registration → task allocation → parallel execution → result aggregation
5. **Maximum Concurrency**: Phase-based parallelism, layer-based task execution, async/await

Examples
--------
>>> from specify_cli.ops import agi_task_planning
>>> tasks = agi_task_planning.decompose_goal("Implement feature", "Build new functionality", {})
>>> plan = agi_task_planning.generate_execution_plan("feature", tasks)
>>> print(f"Tasks: {len(plan.tasks)}, Parallelization: {plan.parallelization_potential:.2%}")

>>> from specify_cli.ops import agi_reasoning
>>> premises = [agi_reasoning.Premise("Task A is feasible")]
>>> chain = agi_reasoning.chain_of_thought("Can we execute?", premises)
>>> print(f"Reasoning steps: {len(chain.steps)}")

>>> from specify_cli.ops import agi_orchestration
>>> agent = agi_orchestration.register_agent("planner", "planner", ["planning"])
>>> print(f"Agent {agent.name} registered with {len(agent.capabilities)} capabilities")
"""

__version__ = "0.1.0"

# Import submodules
from specify_cli.ops import agi_task_planning
from specify_cli.ops import agi_reasoning
from specify_cli.ops import agi_code_synthesizer
from specify_cli.ops import agi_orchestration

from specify_cli.runtime import agi_task_executor
from specify_cli.runtime import agi_code_emission
from specify_cli.runtime import agi_orchestrator

__all__ = [
    "agi_task_planning",
    "agi_reasoning",
    "agi_code_synthesizer",
    "agi_orchestration",
    "agi_task_executor",
    "agi_code_emission",
    "agi_orchestrator",
]
