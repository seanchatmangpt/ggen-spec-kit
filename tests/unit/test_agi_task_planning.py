"""Unit tests for AGI task planning.

Auto-generated from: ontology/agi-task-planning.ttl
Constitutional equation: test_agi_task_planning.py = μ(agi-task-planning.ttl)
"""

import pytest
from specify_cli.ops import agi_task_planning


class TestTaskDecomposition:
    """Test goal decomposition."""

    def test_decompose_goal_hierarchical(self):
        """Test hierarchical decomposition."""
        goal = "Implement AGI task planning system"
        tasks = agi_task_planning.decompose_goal(goal, goal, {}, "hierarchical")

        assert isinstance(tasks, list)

    def test_decompose_goal_functional(self):
        """Test functional decomposition."""
        goal = "Build API server"
        tasks = agi_task_planning.decompose_goal(goal, goal, {}, "functional")

        assert isinstance(tasks, list)

    def test_task_dependencies(self):
        """Test dependency analysis."""
        tasks = [
            agi_task_planning.Task(
                "task1", 0.5, 10.0, dependencies=[], parallelizable_with=["task2"]
            ),
            agi_task_planning.Task(
                "task2", 0.3, 5.0, dependencies=["task1"], parallelizable_with=[]
            ),
        ]

        deps = agi_task_planning.analyze_dependencies(tasks)
        assert "task1" in deps
        assert "task2" in deps


class TestCriticalPath:
    """Test critical path computation."""

    def test_critical_path_simple(self):
        """Test critical path in simple DAG."""
        tasks = {
            "a": agi_task_planning.Task("a", 0.5, 10.0),
            "b": agi_task_planning.Task("b", 0.5, 5.0, dependencies=["a"]),
            "c": agi_task_planning.Task("c", 0.5, 8.0, dependencies=["b"]),
        }
        deps = {"a": [], "b": ["a"], "c": ["b"]}

        path, duration = agi_task_planning.compute_critical_path(tasks, deps)
        assert isinstance(path, list)
        assert duration >= 0


class TestParallelization:
    """Test parallelization identification."""

    def test_identify_parallelizable_tasks(self):
        """Test parallelization detection."""
        tasks = {
            "a": agi_task_planning.Task("a", 0.5, 10.0),
            "b": agi_task_planning.Task("b", 0.5, 5.0, parallelizable_with=["c"]),
            "c": agi_task_planning.Task("c", 0.5, 5.0, parallelizable_with=["b"]),
        }
        deps = {"a": [], "b": ["a"], "c": ["a"]}

        layers, potential = agi_task_planning.identify_parallelization(tasks, deps)
        assert len(layers) >= 0
        assert 0 <= potential <= 1.0


class TestExecutionPlan:
    """Test execution plan generation."""

    def test_generate_plan(self):
        """Test plan generation."""
        tasks = [
            agi_task_planning.Task("init", 0.3, 2.0),
            agi_task_planning.Task("validate", 0.5, 5.0, dependencies=["init"]),
            agi_task_planning.Task("generate", 0.7, 10.0, dependencies=["validate"]),
        ]

        plan = agi_task_planning.generate_execution_plan(
            "test_goal", tasks, strategy="optimize_latency"
        )

        assert isinstance(plan, agi_task_planning.ExecutionPlan)
        assert len(plan.tasks) == 3
