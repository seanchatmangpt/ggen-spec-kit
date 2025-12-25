"""
specify_cli.ops.cloud - Cloud Operations
=======================================

Business logic for multi-cloud operations.

This module contains pure business logic for cloud operations including:

* **Provider Management**: Initialize and configure cloud providers
* **Storage Operations**: Upload, download, list artifacts
* **Deployment Operations**: Deploy to single or multiple clouds
* **Cost Analysis**: Compare costs across providers
* **Metrics Export**: Export metrics to cloud monitoring

Key Features
-----------
* Pure functions (same input → same output)
* No direct I/O (delegates to cloud providers)
* Fully testable with mocked providers
* Returns structured results for commands to format

Design Principles
----------------
* Provider-agnostic business logic
* Graceful error handling
* Comprehensive validation
* Full OpenTelemetry instrumentation

Examples
--------
    >>> from specify_cli.ops.cloud import initialize_providers, deploy_multicloud
    >>>
    >>> providers = initialize_providers(["aws", "gcp"])
    >>> result = deploy_multicloud("app.tar.gz", providers=["aws", "gcp"])

See Also
--------
- :mod:`specify_cli.cloud` : Cloud provider implementations
- :mod:`specify_cli.commands.cloud` : CLI command handlers
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from specify_cli.core.telemetry import record_exception, span

logger = logging.getLogger(__name__)


@dataclass
class CloudProviderStatus:
    """Cloud provider initialization status."""

    name: str
    available: bool
    error: str | None = None
    config: dict[str, Any] = field(default_factory=dict)


@dataclass
class CloudOperationResult:
    """Result of a cloud operation."""

    success: bool
    provider: str
    operation: str
    message: str
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


@dataclass
class MultiCloudDeploymentResult:
    """Result of multi-cloud deployment."""

    success: bool
    deployments: list[CloudOperationResult] = field(default_factory=list)
    failed_providers: list[str] = field(default_factory=list)
    total_providers: int = 0

    @property
    def success_rate(self) -> float:
        """Get deployment success rate."""
        if self.total_providers == 0:
            return 0.0
        successful = self.total_providers - len(self.failed_providers)
        return successful / self.total_providers


def initialize_providers(
    provider_names: list[str],
    *,
    region: str | None = None,
) -> dict[str, CloudProviderStatus]:
    """Initialize cloud providers.

    Parameters
    ----------
    provider_names : list[str]
        List of provider names (aws, gcp, azure).
    region : str, optional
        Default region for providers.

    Returns
    -------
    dict[str, CloudProviderStatus]
        Provider initialization status by name.
    """
    with span("ops.cloud.initialize_providers", providers=provider_names):
        statuses = {}

        for name in provider_names:
            try:
                status = _initialize_single_provider(name, region=region)
                statuses[name] = status
            except Exception as e:
                record_exception(e)
                logger.error(f"Failed to initialize provider {name}: {e}")
                statuses[name] = CloudProviderStatus(
                    name=name, available=False, error=str(e)
                )

        return statuses


def _initialize_single_provider(
    name: str, *, region: str | None = None
) -> CloudProviderStatus:
    """Initialize a single cloud provider.

    Parameters
    ----------
    name : str
        Provider name.
    region : str, optional
        Default region.

    Returns
    -------
    CloudProviderStatus
        Provider status.
    """
    from specify_cli.cloud import multicloud

    try:
        if name == "aws":
            from specify_cli.cloud.aws import AWSProvider

            aws_region = region or os.getenv("AWS_REGION", "us-east-1")
            provider = AWSProvider(region=aws_region)
            multicloud.register_provider("aws", provider)

            return CloudProviderStatus(
                name="aws",
                available=True,
                config={"region": aws_region},
            )

        elif name == "gcp":  # noqa: RET505
            from specify_cli.cloud.gcp import GCPProvider

            project_id = os.getenv("GCP_PROJECT_ID")
            if not project_id:
                return CloudProviderStatus(
                    name="gcp",
                    available=False,
                    error="GCP_PROJECT_ID not set",
                )

            gcp_region = region or "us-central1"
            provider = GCPProvider(project_id=project_id, region=gcp_region)  # type: ignore[assignment]
            multicloud.register_provider("gcp", provider)

            return CloudProviderStatus(
                name="gcp",
                available=True,
                config={"project_id": project_id, "region": gcp_region},
            )

        elif name == "azure":
            from specify_cli.cloud.azure import AzureProvider

            subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
            if not subscription_id:
                return CloudProviderStatus(
                    name="azure",
                    available=False,
                    error="AZURE_SUBSCRIPTION_ID not set",
                )

            azure_region = region or "eastus"
            provider = AzureProvider(subscription_id=subscription_id, region=azure_region)  # type: ignore[assignment]
            multicloud.register_provider("azure", provider)

            return CloudProviderStatus(
                name="azure",
                available=True,
                config={"subscription_id": subscription_id, "region": azure_region},
            )

        else:
            return CloudProviderStatus(
                name=name,
                available=False,
                error=f"Unknown provider: {name}",
            )

    except ImportError as e:
        return CloudProviderStatus(
            name=name,
            available=False,
            error=f"Provider libraries not installed: {e}",
        )


def upload_artifact(
    provider: str,
    local_path: Path | str,
    remote_key: str,
    *,
    metadata: dict[str, str] | None = None,
) -> CloudOperationResult:
    """Upload artifact to cloud storage.

    Parameters
    ----------
    provider : str
        Cloud provider name.
    local_path : Path | str
        Local file path.
    remote_key : str
        Remote storage key.
    metadata : dict[str, str], optional
        Object metadata.

    Returns
    -------
    CloudOperationResult
        Upload operation result.
    """
    with span("ops.cloud.upload_artifact", provider=provider):
        from specify_cli.cloud import multicloud

        try:
            cloud_provider = multicloud.get_provider(provider)
            if not cloud_provider:
                return CloudOperationResult(
                    success=False,
                    provider=provider,
                    operation="upload",
                    message=f"Provider {provider} not initialized",
                    error=f"Provider {provider} not found",
                )

            storage = cloud_provider.get_storage()
            url = storage.upload(local_path, remote_key, metadata=metadata)

            return CloudOperationResult(
                success=True,
                provider=provider,
                operation="upload",
                message=f"Uploaded {local_path} to {url}",
                data={"url": url, "key": remote_key},
            )

        except Exception as e:
            record_exception(e)
            logger.error(f"Upload failed: {e}")
            return CloudOperationResult(
                success=False,
                provider=provider,
                operation="upload",
                message=f"Upload failed: {e}",
                error=str(e),
            )


def deploy_multicloud(
    artifact: Path | str,
    *,
    providers: list[str],
    regions: list[str] | None = None,
    instance_type: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> MultiCloudDeploymentResult:
    """Deploy to multiple cloud providers.

    Parameters
    ----------
    artifact : Path | str
        Artifact to deploy.
    providers : list[str]
        List of provider names.
    regions : list[str], optional
        Regions for each provider.
    instance_type : str, optional
        Compute instance type.
    metadata : dict[str, Any], optional
        Deployment metadata.

    Returns
    -------
    MultiCloudDeploymentResult
        Multi-cloud deployment result.
    """
    with span("ops.cloud.deploy_multicloud", providers=providers):
        from specify_cli.cloud.multicloud import MultiCloudDeployer

        try:
            # Initialize deployer
            deployer = MultiCloudDeployer(providers)

            # Default regions if not provided
            if not regions:
                default_regions = {
                    "aws": "us-east-1",
                    "gcp": "us-central1",
                    "azure": "eastus",
                }
                regions = [default_regions.get(p, "us-east-1") for p in providers]

            # Deploy
            results = deployer.deploy(
                artifact,
                regions=regions,
                instance_type=instance_type,
                metadata=metadata,
            )

            # Convert to operation results
            deployments = []
            failed_providers = []

            for result in results:
                if result.status.value == "deployed":
                    deployments.append(
                        CloudOperationResult(
                            success=True,
                            provider=result.provider.value,
                            operation="deploy",
                            message=f"Deployed to {result.region}",
                            data={
                                "id": result.id,
                                "region": result.region,
                                "endpoint": result.endpoint,
                                "artifact_url": result.artifact_url,
                            },
                        )
                    )
                else:
                    failed_providers.append(result.provider.value)
                    deployments.append(
                        CloudOperationResult(
                            success=False,
                            provider=result.provider.value,
                            operation="deploy",
                            message=f"Deployment failed: {result.error}",
                            error=result.error,
                        )
                    )

            success = len(failed_providers) == 0

            return MultiCloudDeploymentResult(
                success=success,
                deployments=deployments,
                failed_providers=failed_providers,
                total_providers=len(providers),
            )

        except Exception as e:
            record_exception(e)
            logger.error(f"Multi-cloud deployment failed: {e}")
            return MultiCloudDeploymentResult(
                success=False,
                failed_providers=providers,
                total_providers=len(providers),
            )


def compare_costs(
    *,
    providers: list[str] | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> dict[str, dict[str, Any]]:
    """Compare costs across cloud providers.

    Parameters
    ----------
    providers : list[str], optional
        Providers to compare. Defaults to all.
    start_date : datetime, optional
        Report start date. Defaults to 30 days ago.
    end_date : datetime, optional
        Report end date. Defaults to now.

    Returns
    -------
    dict[str, dict[str, Any]]
        Cost data by provider.
    """
    from datetime import timedelta

    from specify_cli.cloud.multicloud import CloudCostAnalyzer

    with span("ops.cloud.compare_costs", providers=providers):
        # Default date range
        if not end_date:
            from datetime import UTC, datetime

            end_date = datetime.now(UTC)
        if not start_date:
            start_date = end_date - timedelta(days=30)

        try:
            analyzer = CloudCostAnalyzer()
            reports = analyzer.compare_costs(
                start_date=start_date,
                end_date=end_date,
                providers=providers,
            )

            # Convert to dict format
            cost_data = {}
            for provider_name, report in reports.items():
                cost_data[provider_name] = {
                    "total_cost": report.total_cost,
                    "currency": report.currency,
                    "breakdown": report.breakdown,
                    "recommendations": report.recommendations,
                }

            # Add cheapest provider
            cheapest = analyzer.get_cheapest_provider(reports)
            if cheapest:
                cost_data["_analysis"] = {
                    "cheapest": cheapest,
                    "recommendations": analyzer.get_optimization_recommendations(reports),
                }

            return cost_data

        except Exception as e:
            record_exception(e)
            logger.error(f"Cost comparison failed: {e}")
            return {}


def export_metrics_to_cloud(
    provider: str,
    *,
    metrics: dict[str, float],
    namespace: str = "SpecifyCLI",
    dimensions: dict[str, str] | None = None,
) -> CloudOperationResult:
    """Export metrics to cloud provider.

    Parameters
    ----------
    provider : str
        Cloud provider name.
    metrics : dict[str, float]
        Metrics to export (name -> value).
    namespace : str, optional
        Metrics namespace.
    dimensions : dict[str, str], optional
        Metric dimensions.

    Returns
    -------
    CloudOperationResult
        Export operation result.
    """
    with span("ops.cloud.export_metrics", provider=provider):
        from specify_cli.cloud import multicloud

        try:
            cloud_provider = multicloud.get_provider(provider)
            if not cloud_provider:
                return CloudOperationResult(
                    success=False,
                    provider=provider,
                    operation="export_metrics",
                    message=f"Provider {provider} not initialized",
                    error=f"Provider {provider} not found",
                )

            metrics_client = cloud_provider.get_metrics()

            # Export each metric
            exported = 0
            for name, value in metrics.items():
                try:
                    metrics_client.put_metric(name, value, dimensions=dimensions)
                    exported += 1
                except Exception as e:
                    logger.warning(f"Failed to export metric {name}: {e}")

            return CloudOperationResult(
                success=exported > 0,
                provider=provider,
                operation="export_metrics",
                message=f"Exported {exported}/{len(metrics)} metrics",
                data={"exported": exported, "total": len(metrics)},
            )

        except Exception as e:
            record_exception(e)
            logger.error(f"Metrics export failed: {e}")
            return CloudOperationResult(
                success=False,
                provider=provider,
                operation="export_metrics",
                message=f"Metrics export failed: {e}",
                error=str(e),
            )


__all__ = [
    "CloudOperationResult",
    "CloudProviderStatus",
    "MultiCloudDeploymentResult",
    "compare_costs",
    "deploy_multicloud",
    "export_metrics_to_cloud",
    "initialize_providers",
    "upload_artifact",
]
