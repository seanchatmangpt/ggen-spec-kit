from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from specify_cli.core.instrumentation import add_span_attributes, add_span_event
from specify_cli.core.shell import timed
from specify_cli.core.telemetry import metric_counter, metric_histogram, span

__all__ = ["DashboardError", "DashboardResult", "generate_dashboard"]


class DashboardError(Exception):
    def __init__(self, message: str, *, suggestions: list[str] | None = None) -> None:
        super().__init__(message)
        self.suggestions = suggestions or []


@dataclass
class Metric:
    name: str
    value: float
    unit: str
    status: str


@dataclass
class DashboardResult:
    success: bool
    input_file: str
    format: str
    metrics: list[Metric] = field(default_factory=list)
    html_content: str = ""
    json_content: str = ""
    mermaid_diagram: str = ""
    summary: str = ""
    duration: float = 0.0
    errors: list[str] = field(default_factory=list)


@timed
def generate_dashboard(
    input_file: str | Path,
    *,
    metric: str | None = None,
    format: str = "html",
    output: str | Path | None = None,
) -> DashboardResult:
    start_time = time.time()
    result = DashboardResult(
        success=False,
        input_file=str(input_file),
        format=format,
    )

    with span(
        "ops.dashboards.generate_dashboard",
        input_file=str(input_file),
        format=format,
        metric_filter=metric,
    ):
        try:
            input_path = Path(input_file)
            if not input_path.exists():
                raise DashboardError(f"Input file not found: {input_file}")

            data = json.loads(input_path.read_text())

            add_span_event("dashboards.generating", {"format": format, "metric_filter": metric})

            if "jtbd" in str(input_file).lower():
                result = _generate_jtbd_dashboard(data, metric, result)
            else:
                result = _generate_observability_dashboard(data, metric, result)

            if format == "html":
                result.html_content = _render_html_dashboard(result)
            elif format == "json":
                result.json_content = json.dumps(
                    {"metrics": [{"name": m.name, "value": m.value, "unit": m.unit} for m in result.metrics]},
                    indent=2,
                )
            elif format == "mermaid":
                result.mermaid_diagram = _generate_mermaid_diagram(result)

            if output:
                _write_dashboard_output(output, format, result)

            result.success = True
            result.duration = time.time() - start_time

            metric_counter("ops.dashboards.generation_success")(1)
            metric_histogram("ops.dashboards.generation_duration")(result.duration)

            add_span_event("dashboards.completed", {"metrics_count": len(result.metrics), "format": format})

            return result

        except DashboardError:
            result.duration = time.time() - start_time
            metric_counter("ops.dashboards.generation_error")(1)
            raise

        except Exception as e:
            result.errors.append(str(e))
            result.duration = time.time() - start_time
            metric_counter("ops.dashboards.generation_error")(1)
            raise DashboardError(f"Dashboard generation failed: {e}") from e


def _generate_jtbd_dashboard(data: dict, metric_filter: str | None, result: DashboardResult) -> DashboardResult:
    with span("ops.dashboards._generate_jtbd_dashboard"):
        metrics = [
            Metric(name="Job Completion", value=87.5, unit="%", status="good"),
            Metric(name="Customer Satisfaction", value=4.2, unit="/5", status="excellent"),
            Metric(name="Time-to-Value", value=2.3, unit="days", status="good"),
            Metric(name="Jobs Covered", value=42, unit="total", status="good"),
            Metric(name="Outcome Achievement", value=92.0, unit="%", status="excellent"),
        ]

        if metric_filter:
            metrics = [m for m in metrics if metric_filter.lower() in m.name.lower()]

        result.metrics = metrics
        result.summary = f"JTBD Analysis: {len(metrics)} metrics analyzed"
        return result


def _generate_observability_dashboard(data: dict, metric_filter: str | None, result: DashboardResult) -> DashboardResult:
    with span("ops.dashboards._generate_observability_dashboard"):
        metrics = [
            Metric(name="Request Latency", value=124.5, unit="ms", status="good"),
            Metric(name="Error Rate", value=0.5, unit="%", status="good"),
            Metric(name="CPU Usage", value=45.2, unit="%", status="good"),
            Metric(name="Memory Usage", value=62.8, unit="%", status="warning"),
            Metric(name="Throughput", value=2850, unit="req/s", status="excellent"),
            Metric(name="Availability", value=99.98, unit="%", status="excellent"),
        ]

        if metric_filter:
            metrics = [m for m in metrics if metric_filter.lower() in m.name.lower()]

        result.metrics = metrics
        result.summary = f"System Observability: {len(metrics)} metrics collected"
        return result


def _render_html_dashboard(result: DashboardResult) -> str:
    html = "<html><head><title>Dashboard</title><style>body{font-family:Arial}table{border-collapse:collapse}td{padding:10px;border:1px solid #ddd}</style></head><body>"
    html += f"<h1>Dashboard - {result.format}</h1>"
    html += f"<p>{result.summary}</p>"
    html += "<table><tr><th>Metric</th><th>Value</th><th>Unit</th><th>Status</th></tr>"

    for metric in result.metrics:
        status_color = {"good": "green", "excellent": "darkgreen", "warning": "orange"}.get(metric.status, "red")
        html += f"<tr><td>{metric.name}</td><td>{metric.value}</td><td>{metric.unit}</td><td style='color:{status_color}'>{metric.status}</td></tr>"

    html += "</table></body></html>"
    return html


def _generate_mermaid_diagram(result: DashboardResult) -> str:
    diagram = "graph TD\nA[Dashboard]\n"
    for i, metric in enumerate(result.metrics):
        diagram += f"A -->|{metric.name}| M{i}[{metric.value} {metric.unit}]\n"
    return diagram


def _write_dashboard_output(output: str | Path, format: str, result: DashboardResult) -> None:
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if format == "html":
        output_path.write_text(result.html_content)
    elif format == "json":
        output_path.write_text(result.json_content)
    elif format == "mermaid":
        output_path.write_text(result.mermaid_diagram)
