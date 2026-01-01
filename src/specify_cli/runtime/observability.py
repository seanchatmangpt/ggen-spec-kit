from __future__ import annotations

import json
import time
from typing import Any

from specify_cli.core.instrumentation import add_span_event
from specify_cli.core.shell import timed
from specify_cli.core.telemetry import metric_counter, metric_histogram, span
from specify_cli.ops.observability import analyze_observability, ObservabilityAnalysis
from specify_cli.ops.dashboards import generate_dashboard, DashboardResult
from specify_cli.ops.jtbd import analyze_jobs, JobAnalysis


@timed
def execute_observability_analysis(
    *,
    metric_type: str = "traces",
    service_name: str | None = None,
    time_range: str = "1h",
    otel_endpoint: str | None = None,
) -> ObservabilityAnalysis:
    with span("runtime.observability.analysis", metric_type=metric_type):
        try:
            add_span_event("analysis.start", {
                "metric_type": metric_type,
                "service": service_name or "all",
                "time_range": time_range,
            })

            result = analyze_observability(
                metric_type=metric_type,
                service_name=service_name,
                time_range=time_range,
                otel_endpoint=otel_endpoint,
            )

            metric_counter("observability.analyses", 1, {"type": metric_type})

            if metric_type == "traces":
                metric_histogram("observability.spans", result.total_spans)
                metric_histogram("observability.latency_ms", result.avg_latency_ms)
            elif metric_type == "metrics":
                metric_histogram("observability.error_rate", result.error_rate)

            add_span_event("analysis.complete", {
                "spans": result.total_spans,
                "avg_latency": result.avg_latency_ms,
            })

            return result
        except Exception as e:
            metric_counter("observability.errors", 1, {"type": metric_type})
            raise


@timed
def execute_dashboard_generation(
    input_file: str,
    *,
    metric_type: str | None = None,
    format: str = "html",
) -> DashboardResult:
    with span("runtime.observability.dashboard", format=format):
        try:
            add_span_event("dashboard.generation.start", {
                "input": input_file,
                "format": format,
            })

            result = generate_dashboard(
                input_file,
                metric=metric_type,
                format=format,
            )

            metric_counter("dashboards.generated", 1, {"format": format})

            if result.success:
                metric_histogram("dashboard.metrics_count", len(result.metrics))

            add_span_event("dashboard.generation.complete", {
                "metrics": len(result.metrics),
                "format": format,
            })

            return result
        except Exception as e:
            metric_counter("dashboard.errors", 1)
            raise


@timed
def execute_jtbd_analysis(
    spec_file: str,
    *,
    analysis_type: str = "complete",
    persona: str | None = None,
) -> JobAnalysis:
    with span("runtime.jtbd.analysis", analysis_type=analysis_type):
        try:
            add_span_event("jtbd.analysis.start", {
                "spec": spec_file,
                "analysis_type": analysis_type,
                "persona": persona or "all",
            })

            result = analyze_jobs(
                spec_file,
                analysis_type=analysis_type,
                persona=persona,
            )

            metric_counter("jtbd.analyses", 1, {"type": analysis_type})

            if result.success:
                metric_histogram("jtbd.jobs_identified", len(result.jobs))
                metric_histogram("jtbd.satisfaction_score", result.total_satisfaction_score)
                metric_histogram("jtbd.roi_estimate", result.roi_estimate)

            add_span_event("jtbd.analysis.complete", {
                "jobs": len(result.jobs),
                "satisfaction": result.total_satisfaction_score,
                "roi": result.roi_estimate,
            })

            return result
        except Exception as e:
            metric_counter("jtbd.errors", 1)
            raise


@timed
def execute_integrated_observability_pipeline(
    *,
    analyze_traces: bool = True,
    analyze_metrics: bool = True,
    generate_dashboard: bool = True,
    service_name: str | None = None,
) -> dict[str, Any]:
    with span("runtime.observability.integrated_pipeline"):
        results = {}
        start_time = time.time()

        try:
            if analyze_traces:
                add_span_event("pipeline.traces_analysis")
                traces_result = execute_observability_analysis(
                    metric_type="traces",
                    service_name=service_name,
                )
                results["traces"] = {
                    "success": traces_result.success,
                    "spans": traces_result.total_spans,
                    "latency_ms": traces_result.avg_latency_ms,
                }

            if analyze_metrics:
                add_span_event("pipeline.metrics_analysis")
                metrics_result = execute_observability_analysis(
                    metric_type="metrics",
                    service_name=service_name,
                )
                results["metrics"] = {
                    "success": metrics_result.success,
                    "error_rate": metrics_result.error_rate,
                }

            if generate_dashboard:
                add_span_event("pipeline.dashboard_generation")
                dashboard_result = execute_dashboard_generation(
                    "metrics.json",
                    format="html",
                )
                results["dashboard"] = {
                    "success": dashboard_result.success,
                    "metrics_count": len(dashboard_result.metrics),
                }

            results["total_duration"] = time.time() - start_time
            metric_histogram("observability_pipeline.duration", results["total_duration"])

            return results
        except Exception as e:
            metric_counter("observability_pipeline.errors", 1)
            raise
