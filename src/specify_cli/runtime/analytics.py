from __future__ import annotations

import time
from typing import Any

from specify_cli.core.instrumentation import add_span_event
from specify_cli.core.shell import timed
from specify_cli.core.telemetry import metric_counter, metric_histogram, span
from specify_cli.ops.hdql import execute_query, QueryResult
from specify_cli.ops.hd import manage_hypothesis, HypothesisResult
from specify_cli.ops.dashboards import generate_dashboard, DashboardResult


@timed
def execute_hdql_query(
    query_file: str,
    *,
    data_source: str | None = None,
    explain: bool = False,
) -> QueryResult:
    with span("runtime.analytics.hdql", explain=explain):
        try:
            add_span_event("hdql.execution.start", {
                "query_file": query_file,
                "data_source": data_source or "default",
                "explain": explain,
            })

            result = execute_query(
                query_file,
                data_source=data_source,
                explain=explain,
            )

            metric_counter("hdql.queries", 1, {"explain": str(explain)})

            if result.success:
                metric_histogram("hdql.result_rows", result.rows)
                metric_histogram("hdql.result_columns", result.columns)

            add_span_event("hdql.execution.complete", {
                "rows": result.rows,
                "columns": result.columns,
            })

            return result
        except Exception as e:
            metric_counter("hdql.errors", 1)
            raise


@timed
def execute_hypothesis_action(
    action: str,
    hypothesis_file: str | None = None,
    *,
    hypothesis_id: str | None = None,
    priority: str = "medium",
) -> HypothesisResult:
    with span("runtime.analytics.hypothesis", action=action):
        try:
            add_span_event("hypothesis.action.start", {
                "action": action,
                "file": hypothesis_file or "default",
            })

            result = manage_hypothesis(
                action,
                hypothesis_file=hypothesis_file,
                priority=priority,
            )

            metric_counter("hypothesis.actions", 1, {"action": action})

            add_span_event("hypothesis.action.complete", {
                "action": action,
                "hypothesis": result.hypothesis_id or "none",
            })

            return result
        except Exception as e:
            metric_counter("hypothesis.errors", 1, {"action": action})
            raise


@timed
def execute_analytics_pipeline(
    data_file: str,
    *,
    run_hdql: bool = True,
    run_hypotheses: bool = True,
    generate_dashboard: bool = True,
) -> dict[str, Any]:
    with span("runtime.analytics.pipeline"):
        results = {}
        start_time = time.time()

        try:
            if run_hdql:
                add_span_event("pipeline.hdql_stage")
                try:
                    query_result = execute_hdql_query(data_file)
                    results["hdql"] = {
                        "success": query_result.success,
                        "rows": query_result.rows,
                        "columns": query_result.columns,
                    }
                except Exception as e:
                    results["hdql"] = {
                        "success": False,
                        "error": str(e),
                    }

            if run_hypotheses:
                add_span_event("pipeline.hypothesis_stage")
                try:
                    hyp_result = execute_hypothesis_action("list", data_file)
                    results["hypotheses"] = {
                        "success": hyp_result.success,
                        "hypothesis": hyp_result.hypothesis_id,
                    }
                except Exception as e:
                    results["hypotheses"] = {
                        "success": False,
                        "error": str(e),
                    }

            if generate_dashboard:
                add_span_event("pipeline.dashboard_stage")
                try:
                    dashboard_result = generate_dashboard(data_file, format="json")
                    results["dashboard"] = {
                        "success": dashboard_result.success,
                        "metrics": len(dashboard_result.metrics),
                    }
                except Exception as e:
                    results["dashboard"] = {
                        "success": False,
                        "error": str(e),
                    }

            results["total_duration"] = time.time() - start_time
            metric_histogram("analytics_pipeline.duration", results["total_duration"])

            return results
        except Exception as e:
            metric_counter("analytics_pipeline.errors", 1)
            raise
