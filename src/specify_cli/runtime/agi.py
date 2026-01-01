from __future__ import annotations

import json
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

from specify_cli.core.instrumentation import add_span_event
from specify_cli.core.process import run_logged
from specify_cli.core.shell import timed
from specify_cli.core.telemetry import metric_counter, metric_histogram, span
from specify_cli.ops.agi import reason_over_rdf, ReasoningResult
from specify_cli.ops.agi_reasoner import run_reasoning, InferenceResult
from specify_cli.ops.agi_task_planner import plan_goal_decomposition, TaskPlan


@timed
def execute_reasoning_task(
    input_file: str | Path,
    *,
    strategy: str = "cot",
    max_iterations: int = 5,
    temperature: float = 0.7,
) -> ReasoningResult:
    with span("runtime.agi.execute_reasoning_task", strategy=strategy):
        try:
            input_path = Path(input_file)
            if not input_path.exists():
                raise FileNotFoundError(f"Input file not found: {input_file}")

            add_span_event("reasoning.start", {"file": str(input_path)})

            result = reason_over_rdf(
                str(input_path),
                strategy=strategy,
                max_iterations=max_iterations,
                temperature=temperature,
            )

            metric_counter("reasoning.executions", 1, {"strategy": strategy})
            metric_histogram("reasoning.inferred_triples", result.inferred_triples)

            add_span_event("reasoning.complete", {"inferred": result.inferred_triples})

            return result
        except Exception as e:
            metric_counter("reasoning.errors", 1, {"strategy": strategy})
            raise


@timed
def execute_inference_task(
    input_file: str | Path,
    *,
    rules_file: str | Path | None = None,
    inference_type: str = "owl",
) -> InferenceResult:
    with span("runtime.agi.execute_inference_task", inference_type=inference_type):
        try:
            input_path = Path(input_file)
            rules_path = Path(rules_file) if rules_file else None

            if not input_path.exists():
                raise FileNotFoundError(f"Input RDF file not found: {input_file}")

            if rules_path and not rules_path.exists():
                raise FileNotFoundError(f"Rules file not found: {rules_file}")

            add_span_event("inference.start", {"type": inference_type})

            result = run_reasoning(
                str(input_path),
                rules_file=str(rules_path) if rules_path else None,
                inference_type=inference_type,
            )

            metric_counter("inference.executions", 1, {"type": inference_type})
            metric_histogram("inference.output_triples", result.output_triple_count)

            return result
        except Exception as e:
            metric_counter("inference.errors", 1, {"type": inference_type})
            raise


@timed
def execute_task_planning(
    goal_spec: str,
    *,
    strategy: str = "hierarchical",
    max_depth: int = 5,
) -> TaskPlan:
    with span("runtime.agi.execute_task_planning", strategy=strategy):
        try:
            add_span_event("planning.start", {"strategy": strategy})

            result = plan_goal_decomposition(
                goal_spec,
                decomposition_strategy=strategy,
                max_depth=max_depth,
                parallel_analysis=True,
            )

            if result.root_task:
                metric_counter("planning.tasks", result.total_tasks)
                metric_histogram("planning.critical_path", result.critical_path_length)

            add_span_event("planning.complete", {
                "tasks": result.total_tasks,
                "parallelizable": result.parallelizable_segments,
            })

            return result
        except Exception as e:
            metric_counter("planning.errors", 1)
            raise


@timed
def run_autonomous_reasoning_pipeline(
    input_file: str | Path,
    *,
    use_reasoning: bool = True,
    use_inference: bool = True,
    use_planning: bool = False,
) -> dict[str, Any]:
    with span("runtime.agi.autonomous_pipeline"):
        results = {}
        start_time = time.time()

        try:
            if use_reasoning:
                add_span_event("pipeline.reasoning_stage")
                reasoning_result = execute_reasoning_task(input_file)
                results["reasoning"] = {
                    "success": reasoning_result.success,
                    "inferred_triples": reasoning_result.inferred_triples,
                    "duration": reasoning_result.duration,
                }

            if use_inference:
                add_span_event("pipeline.inference_stage")
                inference_result = execute_inference_task(input_file)
                results["inference"] = {
                    "success": inference_result.success,
                    "output_triples": inference_result.output_triple_count,
                    "duration": inference_result.duration,
                }

            if use_planning:
                add_span_event("pipeline.planning_stage")
                goal = f"Analyze {Path(input_file).stem}"
                planning_result = execute_task_planning(goal)
                results["planning"] = {
                    "success": planning_result.success,
                    "total_tasks": planning_result.total_tasks,
                    "critical_path": planning_result.critical_path_length,
                }

            results["total_duration"] = time.time() - start_time
            metric_histogram("pipeline.total_duration", results["total_duration"])

            return results
        except Exception as e:
            metric_counter("pipeline.errors", 1)
            raise
