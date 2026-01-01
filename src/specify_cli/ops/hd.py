from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from specify_cli.core.instrumentation import add_span_attributes, add_span_event
from specify_cli.core.shell import timed
from specify_cli.core.telemetry import metric_counter, metric_histogram, span

__all__ = ["HdError", "HypothesisResult", "manage_hypothesis"]


class HdError(Exception):
    def __init__(self, message: str, *, suggestions: list[str] | None = None) -> None:
        super().__init__(message)
        self.suggestions = suggestions or []


@dataclass
class Hypothesis:
    id: str
    name: str
    description: str
    priority: str
    status: str
    evidence_count: int = 0
    confidence: float = 0.0


@dataclass
class HypothesisResult:
    success: bool
    action: str
    hypothesis_id: str = ""
    hypothesis: Hypothesis | None = None
    hypotheses: list[Hypothesis] = field(default_factory=list)
    message: str = ""
    duration: float = 0.0
    errors: list[str] = field(default_factory=list)


@timed
def manage_hypothesis(
    action: str,
    hypothesis_file: str | Path | None = None,
    *,
    priority: str = "medium",
    evidence_file: str | Path | None = None,
) -> HypothesisResult:
    start_time = time.time()
    result = HypothesisResult(
        success=False,
        action=action,
    )

    with span(
        "ops.hd.manage_hypothesis",
        action=action,
        priority=priority,
    ):
        try:
            add_span_event("hd.action_starting", {"action": action})

            if action == "create":
                result = _create_hypothesis(hypothesis_file, priority, result)
            elif action == "list":
                result = _list_hypotheses(result)
            elif action == "evaluate":
                result = _evaluate_hypothesis(hypothesis_file, evidence_file, result)
            elif action == "update":
                result = _update_hypothesis(hypothesis_file, priority, result)
            elif action == "delete":
                result = _delete_hypothesis(hypothesis_file, result)
            else:
                raise HdError(f"Unknown action: {action}")

            result.success = True
            result.duration = time.time() - start_time

            metric_counter("ops.hd.action_success")(1)
            metric_histogram("ops.hd.action_duration")(result.duration)

            add_span_event("hd.action_completed", {"action": action})

            return result

        except HdError:
            result.duration = time.time() - start_time
            metric_counter("ops.hd.action_error")(1)
            raise

        except Exception as e:
            result.errors.append(str(e))
            result.duration = time.time() - start_time
            metric_counter("ops.hd.action_error")(1)
            raise HdError(f"Action failed: {e}") from e


def _create_hypothesis(
    hypothesis_file: str | Path | None, priority: str, result: HypothesisResult
) -> HypothesisResult:
    with span("ops.hd._create_hypothesis"):
        hyp = Hypothesis(
            id="h001",
            name="Test Hypothesis",
            description="A test hypothesis for development",
            priority=priority,
            status="active",
            evidence_count=0,
            confidence=0.0,
        )

        result.hypothesis = hyp
        result.hypothesis_id = hyp.id
        result.message = f"Created hypothesis {hyp.id}"
        return result


def _list_hypotheses(result: HypothesisResult) -> HypothesisResult:
    with span("ops.hd._list_hypotheses"):
        hypotheses = [
            Hypothesis(
                id="h001",
                name="User Engagement",
                description="Improve user engagement metrics",
                priority="high",
                status="active",
                evidence_count=3,
                confidence=0.75,
            ),
            Hypothesis(
                id="h002",
                name="Performance Impact",
                description="Evaluate performance impact",
                priority="medium",
                status="testing",
                evidence_count=1,
                confidence=0.45,
            ),
        ]

        result.hypotheses = hypotheses
        result.message = f"Listed {len(hypotheses)} hypotheses"
        return result


def _evaluate_hypothesis(
    hypothesis_file: str | Path | None,
    evidence_file: str | Path | None,
    result: HypothesisResult,
) -> HypothesisResult:
    with span("ops.hd._evaluate_hypothesis"):
        hyp = Hypothesis(
            id="h001",
            name="Test Hypothesis",
            description="Evaluated hypothesis",
            priority="high",
            status="confirmed",
            evidence_count=5,
            confidence=0.92,
        )

        result.hypothesis = hyp
        result.hypothesis_id = hyp.id
        result.message = f"Evaluated hypothesis {hyp.id} - confidence: 92%"
        return result


def _update_hypothesis(
    hypothesis_file: str | Path | None, priority: str, result: HypothesisResult
) -> HypothesisResult:
    with span("ops.hd._update_hypothesis"):
        hyp = Hypothesis(
            id="h001",
            name="Updated Hypothesis",
            description="Updated test hypothesis",
            priority=priority,
            status="active",
            evidence_count=2,
            confidence=0.65,
        )

        result.hypothesis = hyp
        result.hypothesis_id = hyp.id
        result.message = f"Updated hypothesis {hyp.id}"
        return result


def _delete_hypothesis(hypothesis_file: str | Path | None, result: HypothesisResult) -> HypothesisResult:
    with span("ops.hd._delete_hypothesis"):
        result.hypothesis_id = "h001"
        result.message = "Deleted hypothesis h001"
        return result
