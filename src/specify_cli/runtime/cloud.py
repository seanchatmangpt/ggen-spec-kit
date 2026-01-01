from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

from specify_cli.core.instrumentation import add_span_event
from specify_cli.core.process import run_logged
from specify_cli.core.shell import timed
from specify_cli.core.telemetry import metric_counter, metric_histogram, span
from specify_cli.ops.cloud import deploy_services, scale_services, DeploymentResult, ScalingResult


@timed
def execute_cloud_deployment(
    config_file: str | Path,
    *,
    provider: str,
    region: str,
    environment: str = "staging",
    dry_run: bool = False,
) -> DeploymentResult:
    with span("runtime.cloud.deployment", provider=provider, region=region):
        try:
            config_path = Path(config_file)
            if not config_path.exists():
                raise FileNotFoundError(f"Config file not found: {config_file}")

            add_span_event("deployment.start", {
                "provider": provider,
                "region": region,
                "environment": environment,
            })

            result = deploy_services(
                config_path,
                provider=provider,
                region=region,
                environment=environment,
                dry_run=dry_run,
            )

            metric_counter("deployments", 1, {
                "provider": provider,
                "environment": environment,
                "success": str(result.success),
            })

            if result.success:
                metric_histogram("deployment.resources", len(result.resources_deployed))
                metric_histogram("deployment.cost", result.total_cost_estimate)

            add_span_event("deployment.complete", {
                "deployment_id": result.deployment_id,
                "resources": len(result.resources_deployed),
            })

            return result
        except Exception as e:
            metric_counter("deployment.errors", 1, {"provider": provider})
            raise


@timed
def execute_cloud_scaling(
    provider: str,
    service_name: str,
    target_replicas: int,
    *,
    strategy: str = "rolling",
) -> ScalingResult:
    with span("runtime.cloud.scaling", provider=provider, strategy=strategy):
        try:
            add_span_event("scaling.start", {
                "service": service_name,
                "target_replicas": target_replicas,
                "strategy": strategy,
            })

            result = scale_services(
                provider,
                service_name,
                target_replicas,
                strategy=strategy,
            )

            metric_counter("scaling_operations", 1, {
                "provider": provider,
                "strategy": strategy,
                "success": str(result.success),
            })

            if result.success:
                metric_histogram("scaling.time", result.scaling_time)
                metric_histogram("scaling.affected_instances", result.affected_instances)

            add_span_event("scaling.complete", {
                "current_replicas": result.current_replicas,
                "scaling_time": result.scaling_time,
            })

            return result
        except Exception as e:
            metric_counter("scaling.errors", 1, {"strategy": strategy})
            raise


@timed
def execute_multi_cloud_deployment(
    artifact_path: str | Path,
    *,
    providers: list[str],
    regions: list[str] | None = None,
) -> dict[str, Any]:
    with span("runtime.cloud.multi_deployment", provider_count=len(providers)):
        results = {}
        start_time = time.time()

        for provider in providers:
            try:
                region = regions[providers.index(provider)] if regions else "default"
                add_span_event("multi_deployment.provider_start", {
                    "provider": provider,
                    "region": region,
                })

                deployment = execute_cloud_deployment(
                    artifact_path,
                    provider=provider,
                    region=region,
                )

                results[provider] = {
                    "success": deployment.success,
                    "deployment_id": deployment.deployment_id,
                    "endpoint": deployment.endpoint_url,
                    "cost": deployment.total_cost_estimate,
                }
            except Exception as e:
                results[provider] = {
                    "success": False,
                    "error": str(e),
                }

        results["total_duration"] = time.time() - start_time
        metric_histogram("multi_deployment.duration", results["total_duration"])

        return results
