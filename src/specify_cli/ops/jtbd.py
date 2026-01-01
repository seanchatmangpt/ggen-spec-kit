from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from specify_cli.core.instrumentation import add_span_attributes, add_span_event
from specify_cli.core.shell import timed
from specify_cli.core.telemetry import metric_counter, metric_histogram, span

__all__ = ["JtbdError", "JobAnalysis", "analyze_jobs"]


class JtbdError(Exception):
    def __init__(self, message: str, *, suggestions: list[str] | None = None) -> None:
        super().__init__(message)
        self.suggestions = suggestions or []


@dataclass
class Job:
    name: str
    description: str
    persona: str
    frequency: str
    importance_score: float


@dataclass
class Outcome:
    desired_state: str
    success_metric: str
    importance: int


@dataclass
class JobAnalysis:
    success: bool
    spec_file: str
    analysis_type: str
    jobs: list[Job] = field(default_factory=list)
    outcomes: list[Outcome] = field(default_factory=list)
    total_satisfaction_score: float = 0.0
    roi_estimate: float = 0.0
    personas_identified: int = 0
    duration: float = 0.0
    errors: list[str] = field(default_factory=list)


@timed
def analyze_jobs(
    spec_file: str | Path,
    *,
    analysis_type: str = "complete",
    persona: str | None = None,
    metrics_only: bool = False,
    output_format: str = "json",
) -> JobAnalysis:
    start_time = time.time()
    analysis = JobAnalysis(
        success=False,
        spec_file=str(spec_file),
        analysis_type=analysis_type,
    )

    with span(
        "ops.jtbd.analyze_jobs",
        analysis_type=analysis_type,
        persona_filter=persona,
    ):
        try:
            spec_path = Path(spec_file)
            if not spec_path.exists():
                raise JtbdError(f"Spec file not found: {spec_file}")

            spec_data = json.loads(spec_path.read_text())

            add_span_event("jtbd.starting_analysis", {"analysis_type": analysis_type})

            if analysis_type in ("jobs", "complete"):
                analysis = _extract_jobs(spec_data, analysis, persona)

            if analysis_type in ("outcomes", "complete"):
                analysis = _extract_outcomes(spec_data, analysis)

            if analysis_type in ("satisfaction", "complete"):
                analysis.total_satisfaction_score = _calculate_satisfaction(analysis.jobs)

            if analysis_type in ("roi", "complete"):
                analysis.roi_estimate = _estimate_roi(analysis.jobs, analysis.outcomes)

            analysis.personas_identified = len(set(job.persona for job in analysis.jobs))

            analysis.success = True
            analysis.duration = time.time() - start_time

            metric_counter("ops.jtbd.analysis_success")(1)
            metric_histogram("ops.jtbd.analysis_duration")(analysis.duration)
            metric_histogram("ops.jtbd.jobs_identified")(len(analysis.jobs))

            add_span_event(
                "jtbd.analysis_completed",
                {
                    "jobs": len(analysis.jobs),
                    "personas": analysis.personas_identified,
                    "satisfaction": analysis.total_satisfaction_score,
                },
            )

            return analysis

        except JtbdError:
            analysis.duration = time.time() - start_time
            metric_counter("ops.jtbd.analysis_error")(1)
            raise

        except Exception as e:
            analysis.errors.append(str(e))
            analysis.duration = time.time() - start_time
            metric_counter("ops.jtbd.analysis_error")(1)
            raise JtbdError(f"Analysis failed: {e}") from e


def _extract_jobs(data: dict, analysis: JobAnalysis, persona_filter: str | None) -> JobAnalysis:
    with span("ops.jtbd._extract_jobs"):
        jobs_data = data.get("jobs", [])

        for job_data in jobs_data:
            persona = job_data.get("persona", "general")
            if persona_filter and persona.lower() != persona_filter.lower():
                continue

            job = Job(
                name=job_data.get("name", "Unknown Job"),
                description=job_data.get("description", ""),
                persona=persona,
                frequency=job_data.get("frequency", "daily"),
                importance_score=float(job_data.get("importance", 5)) / 10.0,
            )
            analysis.jobs.append(job)

        return analysis


def _extract_outcomes(data: dict, analysis: JobAnalysis) -> JobAnalysis:
    with span("ops.jtbd._extract_outcomes"):
        outcomes_data = data.get("outcomes", [])

        for outcome_data in outcomes_data:
            outcome = Outcome(
                desired_state=outcome_data.get("desired_state", "Unknown"),
                success_metric=outcome_data.get("metric", "Unknown"),
                importance=int(outcome_data.get("importance", 1)),
            )
            analysis.outcomes.append(outcome)

        return analysis


def _calculate_satisfaction(jobs: list[Job]) -> float:
    if not jobs:
        return 0.0
    avg_satisfaction = sum(job.importance_score for job in jobs) / len(jobs) * 100
    return min(100.0, avg_satisfaction)


def _estimate_roi(jobs: list[Job], outcomes: list[Outcome]) -> float:
    base_roi = len(jobs) * 5.0
    outcome_multiplier = len(outcomes) * 1.5
    return base_roi * outcome_multiplier
