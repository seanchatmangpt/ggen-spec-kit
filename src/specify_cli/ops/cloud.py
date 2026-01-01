from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from specify_cli.core.instrumentation import add_span_attributes, add_span_event
from specify_cli.core.shell import timed
from specify_cli.core.telemetry import metric_counter, metric_histogram, span

__all__ = ["CloudError", "DeploymentResult", "ScalingResult", "deploy_services", "scale_services"]


class CloudError(Exception):
    def __init__(self, message: str, *, suggestions: list[str] | None = None) -> None:
        super().__init__(message)
        self.suggestions = suggestions or []


@dataclass
class Resource:
    name: str
    type: str
    status: str
    region: str
    cost_per_hour: float


@dataclass
class DeploymentResult:
    success: bool
    provider: str
    region: str
    environment: str
    service_name: str
    deployment_id: str = ""
    resources_deployed: list[Resource] = field(default_factory=list)
    total_cost_estimate: float = 0.0
    deployment_time: float = 0.0
    endpoint_url: str = ""
    errors: list[str] = field(default_factory=list)
    duration: float = 0.0


@dataclass
class ScalingResult:
    success: bool
    provider: str
    service_name: str
    target_replicas: int
    current_replicas: int
    scaling_strategy: str
    scaling_time: float = 0.0
    affected_instances: int = 0
    errors: list[str] = field(default_factory=list)
    duration: float = 0.0


@timed
def deploy_services(
    config_file: str | Path,
    *,
    provider: str,
    region: str,
    environment: str = "staging",
    dry_run: bool = False,
    auto_approve: bool = False,
) -> DeploymentResult:
    start_time = time.time()
    result = DeploymentResult(
        success=False,
        provider=provider,
        region=region,
        environment=environment,
        service_name="",
    )

    with span(
        "ops.cloud.deploy_services",
        provider=provider,
        region=region,
        environment=environment,
        dry_run=dry_run,
    ):
        try:
            config_path = Path(config_file)
            if not config_path.exists():
                raise CloudError(f"Config file not found: {config_file}")

            config = json.loads(config_path.read_text())
            service_name = config.get("service", {}).get("name", "unknown")
            result.service_name = service_name

            add_span_event("cloud.deploy.starting", {"provider": provider, "service": service_name})

            if dry_run:
                result = _simulate_deployment(provider, region, environment, config, result)
                result.deployment_id = f"DRY_RUN_{int(time.time())}"
            else:
                result = _execute_deployment(provider, region, environment, config, result, auto_approve)

            result.deployment_time = time.time() - start_time
            result.success = True
            result.duration = time.time() - start_time

            metric_counter("ops.cloud.deployment_success")(1)
            metric_histogram("ops.cloud.deployment_duration")(result.duration)
            metric_histogram("ops.cloud.resources_deployed")(len(result.resources_deployed))

            add_span_event(
                "cloud.deploy.completed",
                {
                    "success": True,
                    "service": service_name,
                    "resources": len(result.resources_deployed),
                },
            )

            return result

        except CloudError:
            result.duration = time.time() - start_time
            metric_counter("ops.cloud.deployment_error")(1)
            raise

        except Exception as e:
            result.errors.append(str(e))
            result.duration = time.time() - start_time
            metric_counter("ops.cloud.deployment_error")(1)
            raise CloudError(f"Deployment failed: {e}") from e


@timed
def scale_services(
    provider: str,
    service_name: str,
    target_replicas: int,
    *,
    strategy: str = "rolling",
) -> ScalingResult:
    start_time = time.time()
    result = ScalingResult(
        success=False,
        provider=provider,
        service_name=service_name,
        target_replicas=target_replicas,
        current_replicas=0,
        scaling_strategy=strategy,
    )

    with span(
        "ops.cloud.scale_services",
        provider=provider,
        service=service_name,
        replicas=target_replicas,
        strategy=strategy,
    ):
        try:
            add_span_event("cloud.scaling.starting", {"service": service_name, "target_replicas": target_replicas})

            result.current_replicas = _get_current_replicas(provider, service_name)

            if strategy == "rolling":
                result = _rolling_scale(provider, service_name, target_replicas, result)
            elif strategy == "blue-green":
                result = _blue_green_scale(provider, service_name, target_replicas, result)
            elif strategy == "canary":
                result = _canary_scale(provider, service_name, target_replicas, result)
            else:
                raise CloudError(f"Unknown scaling strategy: {strategy}")

            result.success = True
            result.duration = time.time() - start_time

            metric_counter("ops.cloud.scaling_success")(1)
            metric_histogram("ops.cloud.scaling_duration")(result.duration)

            add_span_event(
                "cloud.scaling.completed",
                {
                    "service": service_name,
                    "from_replicas": result.current_replicas,
                    "to_replicas": target_replicas,
                },
            )

            return result

        except CloudError:
            result.duration = time.time() - start_time
            metric_counter("ops.cloud.scaling_error")(1)
            raise

        except Exception as e:
            result.errors.append(str(e))
            result.duration = time.time() - start_time
            metric_counter("ops.cloud.scaling_error")(1)
            raise CloudError(f"Scaling failed: {e}") from e


def _simulate_deployment(
    provider: str, region: str, environment: str, config: dict, result: DeploymentResult
) -> DeploymentResult:
    with span("ops.cloud._simulate_deployment"):
        resources = config.get("resources", [])

        for res in resources:
            resource = Resource(
                name=res.get("name", "resource"),
                type=res.get("type", "compute"),
                status="planned",
                region=region,
                cost_per_hour=res.get("cost", 0.5),
            )
            result.resources_deployed.append(resource)
            result.total_cost_estimate += resource.cost_per_hour * 24 * 30

        result.endpoint_url = f"https://{config.get('service', {}).get('name', 'app')}.{region}.cloud"
        return result


def _execute_deployment(
    provider: str,
    region: str,
    environment: str,
    config: dict,
    result: DeploymentResult,
    auto_approve: bool,
) -> DeploymentResult:
    with span("ops.cloud._execute_deployment"):
        resources = config.get("resources", [])

        for res in resources:
            resource = Resource(
                name=res.get("name", "resource"),
                type=res.get("type", "compute"),
                status="deployed",
                region=region,
                cost_per_hour=res.get("cost", 0.5),
            )
            result.resources_deployed.append(resource)
            result.total_cost_estimate += resource.cost_per_hour * 24 * 30

        result.endpoint_url = f"https://{config.get('service', {}).get('name', 'app')}.{region}.cloud"
        result.deployment_id = f"{provider}_{int(time.time())}"
        return result


def _get_current_replicas(provider: str, service_name: str) -> int:
    return 3


def _rolling_scale(
    provider: str, service_name: str, target_replicas: int, result: ScalingResult
) -> ScalingResult:
    with span("ops.cloud._rolling_scale"):
        result.affected_instances = abs(target_replicas - result.current_replicas)
        result.scaling_time = result.affected_instances * 0.5
        return result


def _blue_green_scale(
    provider: str, service_name: str, target_replicas: int, result: ScalingResult
) -> ScalingResult:
    with span("ops.cloud._blue_green_scale"):
        result.affected_instances = target_replicas + result.current_replicas
        result.scaling_time = 2.0
        return result


def _canary_scale(
    provider: str, service_name: str, target_replicas: int, result: ScalingResult
) -> ScalingResult:
    with span("ops.cloud._canary_scale"):
        result.affected_instances = max(1, (target_replicas - result.current_replicas) // 3 or 1)
        result.scaling_time = 1.5
        return result
