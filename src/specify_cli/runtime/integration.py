from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from specify_cli.core.shell import timed
from specify_cli.core.telemetry import metric_counter, metric_histogram, span
from specify_cli.runtime.agi import run_autonomous_reasoning_pipeline
from specify_cli.runtime.cloud import execute_multi_cloud_deployment
from specify_cli.runtime.observability import execute_integrated_observability_pipeline
from specify_cli.runtime.analytics import execute_analytics_pipeline


@dataclass
class IntegrationResult:
    success: bool
    phases_executed: list[str] = field(default_factory=list)
    phase_results: dict[str, Any] = field(default_factory=dict)
    total_duration: float = 0.0
    errors: list[str] = field(default_factory=list)


@timed
def execute_full_stack_integration(
    *,
    run_reasoning: bool = True,
    run_deployment: bool = True,
    run_observability: bool = True,
    run_analytics: bool = True,
    input_file: str | None = None,
    artifact_file: str | None = None,
    data_file: str | None = None,
) -> IntegrationResult:
    with span("runtime.integration.full_stack"):
        result = IntegrationResult(success=True)
        start_time = time.time()

        try:
            if run_reasoning and input_file:
                try:
                    reasoning_results = run_autonomous_reasoning_pipeline(
                        input_file,
                        use_reasoning=True,
                        use_inference=True,
                        use_planning=True,
                    )
                    result.phases_executed.append("reasoning")
                    result.phase_results["reasoning"] = reasoning_results
                    metric_counter("integration.phases", 1, {"phase": "reasoning"})
                except Exception as e:
                    result.errors.append(f"Reasoning phase failed: {str(e)}")
                    metric_counter("integration.phase_errors", 1, {"phase": "reasoning"})

            if run_deployment and artifact_file:
                try:
                    deployment_results = execute_multi_cloud_deployment(
                        artifact_file,
                        providers=["aws", "gcp"],
                        regions=["us-east-1", "us-central1"],
                    )
                    result.phases_executed.append("deployment")
                    result.phase_results["deployment"] = deployment_results
                    metric_counter("integration.phases", 1, {"phase": "deployment"})
                except Exception as e:
                    result.errors.append(f"Deployment phase failed: {str(e)}")
                    metric_counter("integration.phase_errors", 1, {"phase": "deployment"})

            if run_observability:
                try:
                    observability_results = execute_integrated_observability_pipeline(
                        analyze_traces=True,
                        analyze_metrics=True,
                        generate_dashboard=True,
                    )
                    result.phases_executed.append("observability")
                    result.phase_results["observability"] = observability_results
                    metric_counter("integration.phases", 1, {"phase": "observability"})
                except Exception as e:
                    result.errors.append(f"Observability phase failed: {str(e)}")
                    metric_counter("integration.phase_errors", 1, {"phase": "observability"})

            if run_analytics and data_file:
                try:
                    analytics_results = execute_analytics_pipeline(
                        data_file,
                        run_hdql=True,
                        run_hypotheses=True,
                        generate_dashboard=True,
                    )
                    result.phases_executed.append("analytics")
                    result.phase_results["analytics"] = analytics_results
                    metric_counter("integration.phases", 1, {"phase": "analytics"})
                except Exception as e:
                    result.errors.append(f"Analytics phase failed: {str(e)}")
                    metric_counter("integration.phase_errors", 1, {"phase": "analytics"})

        finally:
            result.total_duration = time.time() - start_time
            result.success = len(result.errors) == 0

            metric_histogram("integration.total_duration", result.total_duration)
            metric_counter("integration.executions", 1, {
                "success": str(result.success),
                "phases": str(len(result.phases_executed)),
            })

        return result


@timed
def execute_reasoning_and_deployment(
    input_file: str,
    artifact_file: str,
    *,
    providers: list[str] | None = None,
) -> IntegrationResult:
    with span("runtime.integration.reasoning_and_deployment"):
        result = IntegrationResult(success=True)
        start_time = time.time()

        try:
            reasoning_results = run_autonomous_reasoning_pipeline(
                input_file,
                use_reasoning=True,
                use_inference=True,
                use_planning=True,
            )
            result.phases_executed.append("reasoning")
            result.phase_results["reasoning"] = reasoning_results

            if reasoning_results.get("reasoning", {}).get("success"):
                deployment_results = execute_multi_cloud_deployment(
                    artifact_file,
                    providers=providers or ["aws"],
                )
                result.phases_executed.append("deployment")
                result.phase_results["deployment"] = deployment_results

                metric_counter("integration.reasoning_and_deployment", 1)

        except Exception as e:
            result.errors.append(str(e))
            result.success = False
            metric_counter("integration.reasoning_and_deployment_errors", 1)

        finally:
            result.total_duration = time.time() - start_time
            metric_histogram("integration.reasoning_and_deployment_duration", result.total_duration)

        return result


@timed
def execute_observability_and_analytics(
    data_file: str,
    *,
    service_name: str | None = None,
) -> IntegrationResult:
    with span("runtime.integration.observability_and_analytics"):
        result = IntegrationResult(success=True)
        start_time = time.time()

        try:
            observability_results = execute_integrated_observability_pipeline(
                analyze_traces=True,
                analyze_metrics=True,
                generate_dashboard=True,
                service_name=service_name,
            )
            result.phases_executed.append("observability")
            result.phase_results["observability"] = observability_results

            analytics_results = execute_analytics_pipeline(
                data_file,
                run_hdql=True,
                run_hypotheses=True,
                generate_dashboard=True,
            )
            result.phases_executed.append("analytics")
            result.phase_results["analytics"] = analytics_results

            metric_counter("integration.observability_and_analytics", 1)

        except Exception as e:
            result.errors.append(str(e))
            result.success = False
            metric_counter("integration.observability_and_analytics_errors", 1)

        finally:
            result.total_duration = time.time() - start_time
            metric_histogram("integration.observability_and_analytics_duration", result.total_duration)

        return result
