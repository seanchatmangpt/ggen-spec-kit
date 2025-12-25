"""
specify_cli.cloud.multicloud - Multi-Cloud Orchestration
========================================================

Unified multi-cloud interface and orchestration across AWS, GCP, and Azure.

This module provides:

* **Provider Abstraction**: Unified interface across cloud providers
* **Multi-Cloud Deployment**: Deploy to multiple clouds simultaneously
* **Failover Management**: Automatic cross-cloud failover
* **Cost Optimization**: Multi-cloud cost comparison and optimization
* **Data Synchronization**: Keep artifacts in sync across providers
* **Load Distribution**: Distribute workloads across clouds

Key Features
-----------
* Automatic provider selection based on cost and availability
* Cross-cloud data replication
* Unified metrics and logging aggregation
* Multi-region, multi-cloud high availability
* Cost tracking across all providers

Design Principles
----------------
* Provider-agnostic interfaces
* Graceful degradation when providers unavailable
* Comprehensive error handling
* Full OpenTelemetry instrumentation
* Type-safe interfaces

Examples
--------
    # Multi-cloud deployer
    from specify_cli.cloud.multicloud import MultiCloudDeployer
    deployer = MultiCloudDeployer(providers=["aws", "gcp", "azure"])
    results = deployer.deploy("app.tar.gz", regions=["us-east-1", "us-central1", "eastus"])

    # Unified storage interface
    from specify_cli.cloud.multicloud import UnifiedCloudStorage
    storage = UnifiedCloudStorage(primary="aws", backup=["gcp", "azure"])
    storage.upload("artifact.tar.gz", "builds/v1.0.0/artifact.tar.gz")

    # Cost comparison
    from specify_cli.cloud.multicloud import CloudCostAnalyzer
    analyzer = CloudCostAnalyzer()
    report = analyzer.compare_costs(providers=["aws", "gcp", "azure"])

See Also
--------
- :mod:`specify_cli.cloud.aws` : AWS provider
- :mod:`specify_cli.cloud.gcp` : GCP provider
- :mod:`specify_cli.cloud.azure` : Azure provider
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from specify_cli.core.telemetry import record_exception, span

if TYPE_CHECKING:
    from datetime import datetime
    from pathlib import Path

    from specify_cli.cloud.base import (
        CloudProvider,
        CloudProviderType,
        CostReport,
        DeploymentResult,
        StorageObject,
    )

from specify_cli.cloud.base import CloudProviderType, DeploymentStatus

logger = logging.getLogger(__name__)


class ProviderRegistry:
    """Registry for cloud providers."""

    def __init__(self) -> None:
        """Initialize provider registry."""
        self._providers: dict[str, CloudProvider] = {}

    def register(self, name: str, provider: CloudProvider) -> None:
        """Register a cloud provider.

        Parameters
        ----------
        name : str
            Provider name (aws, gcp, azure).
        provider : CloudProvider
            Provider instance.
        """
        self._providers[name] = provider
        logger.info(f"Registered cloud provider: {name}")

    def get(self, name: str) -> CloudProvider | None:
        """Get provider by name.

        Parameters
        ----------
        name : str
            Provider name.

        Returns
        -------
        CloudProvider | None
            Provider instance or None if not found.
        """
        return self._providers.get(name)

    def list_available(self) -> list[str]:
        """List available providers.

        Returns
        -------
        list[str]
            List of registered provider names.
        """
        return list(self._providers.keys())


# Global provider registry
_registry = ProviderRegistry()


def register_provider(name: str, provider: CloudProvider) -> None:
    """Register a cloud provider globally.

    Parameters
    ----------
    name : str
        Provider name.
    provider : CloudProvider
        Provider instance.
    """
    _registry.register(name, provider)


def get_provider(name: str) -> CloudProvider | None:
    """Get registered provider.

    Parameters
    ----------
    name : str
        Provider name.

    Returns
    -------
    CloudProvider | None
        Provider instance or None.
    """
    return _registry.get(name)


def list_providers() -> list[str]:
    """List available cloud providers.

    Returns
    -------
    list[str]
        List of provider names.
    """
    return _registry.list_available()


class UnifiedCloudStorage:
    """Unified cloud storage interface with multi-provider support."""

    def __init__(
        self,
        primary: str,
        backup: list[str] | None = None,
    ) -> None:
        """Initialize unified storage.

        Parameters
        ----------
        primary : str
            Primary cloud provider (aws, gcp, azure).
        backup : list[str], optional
            Backup cloud providers for replication.
        """
        self.primary = primary
        self.backup = backup or []

        # Get provider instances
        self.primary_provider = get_provider(primary)
        if not self.primary_provider:
            msg = f"Primary provider '{primary}' not registered"
            raise ValueError(msg)

        self.backup_providers = []
        for provider_name in self.backup:
            provider = get_provider(provider_name)
            if provider:
                self.backup_providers.append(provider)
            else:
                logger.warning(f"Backup provider '{provider_name}' not registered")

    def upload(
        self,
        local_path: Path | str,
        remote_key: str,
        *,
        metadata: dict[str, str] | None = None,
        replicate: bool = True,
    ) -> str:
        """Upload file to cloud storage with optional replication.

        Parameters
        ----------
        local_path : Path | str
            Local file path.
        remote_key : str
            Remote object key.
        metadata : dict[str, str], optional
            Object metadata.
        replicate : bool, optional
            Replicate to backup providers.

        Returns
        -------
        str
            Primary storage URL.
        """
        with span("multicloud.storage.upload", primary=self.primary, replicate=replicate):
            # Upload to primary
            storage = self.primary_provider.get_storage()  # type: ignore[union-attr]
            url = storage.upload(local_path, remote_key, metadata=metadata)
            logger.info(f"Uploaded to primary provider {self.primary}: {url}")

            # Replicate to backups
            if replicate and self.backup_providers:
                for provider in self.backup_providers:
                    try:
                        backup_storage = provider.get_storage()
                        backup_url = backup_storage.upload(local_path, remote_key, metadata=metadata)
                        logger.info(f"Replicated to backup provider {provider.name}: {backup_url}")
                    except Exception as e:
                        record_exception(e)
                        logger.error(f"Failed to replicate to {provider.name}: {e}")

            return url

    def download(self, remote_key: str, local_path: Path | str) -> Path:
        """Download file from cloud storage with failover.

        Parameters
        ----------
        remote_key : str
            Remote object key.
        local_path : Path | str
            Local destination path.

        Returns
        -------
        Path
            Downloaded file path.
        """
        from pathlib import Path

        with span("multicloud.storage.download", primary=self.primary):
            # Try primary provider
            try:
                storage = self.primary_provider.get_storage()  # type: ignore[union-attr]
                return storage.download(remote_key, local_path)
            except Exception as e:
                record_exception(e)
                logger.error(f"Failed to download from primary {self.primary}: {e}")

                # Failover to backup providers
                for provider in self.backup_providers:
                    try:
                        backup_storage = provider.get_storage()
                        path = backup_storage.download(remote_key, local_path)
                        logger.info(f"Downloaded from backup provider {provider.name}")
                        return path
                    except Exception as backup_error:
                        record_exception(backup_error)
                        logger.error(f"Failed to download from backup {provider.name}: {backup_error}")

                # All providers failed
                raise

    def list_objects(self, prefix: str = "") -> list[StorageObject]:
        """List objects from primary storage.

        Parameters
        ----------
        prefix : str, optional
            Object key prefix filter.

        Returns
        -------
        list[StorageObject]
            List of storage objects.
        """
        storage = self.primary_provider.get_storage()  # type: ignore[union-attr]
        return list(storage.list_objects(prefix))


class MultiCloudDeployer:
    """Deploy applications to multiple cloud providers simultaneously."""

    def __init__(self, providers: list[str]) -> None:
        """Initialize multi-cloud deployer.

        Parameters
        ----------
        providers : list[str]
            List of cloud provider names (aws, gcp, azure).
        """
        self.provider_names = providers
        self.providers = []

        for name in providers:
            provider = get_provider(name)
            if provider:
                self.providers.append(provider)
            else:
                logger.warning(f"Provider '{name}' not registered, skipping")

        if not self.providers:
            msg = "No valid cloud providers registered"
            raise ValueError(msg)

    def deploy(
        self,
        artifact: Path | str,
        *,
        regions: list[str],
        instance_type: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[DeploymentResult]:
        """Deploy to multiple cloud providers.

        Parameters
        ----------
        artifact : Path | str
            Artifact to deploy.
        regions : list[str]
            Regions for each provider (must match providers length).
        instance_type : str, optional
            Compute instance type.
        metadata : dict[str, Any], optional
            Deployment metadata.

        Returns
        -------
        list[DeploymentResult]
            Deployment results for each provider.
        """
        with span("multicloud.deploy", providers=self.provider_names):
            results = []

            # Deploy to each provider
            for i, provider in enumerate(self.providers):
                region = regions[i] if i < len(regions) else regions[0]

                try:
                    result = provider.deploy(
                        artifact,
                        region=region,
                        instance_type=instance_type,
                        metadata=metadata,
                    )
                    results.append(result)
                    logger.info(
                        f"Deployed to {provider.name} in {region}: "
                        f"status={result.status.value}"
                    )

                except Exception as e:
                    record_exception(e)
                    logger.error(f"Deployment to {provider.name} failed: {e}")

                    # Create failed result
                    from datetime import UTC, datetime

                    from specify_cli.cloud.base import CloudProviderType, DeploymentResult

                    # Map provider name to type
                    provider_type_map = {
                        "aws": CloudProviderType.AWS,
                        "gcp": CloudProviderType.GCP,
                        "azure": CloudProviderType.AZURE,
                    }
                    provider_type = provider_type_map.get(
                        provider.name.lower(), CloudProviderType.AWS
                    )

                    results.append(
                        DeploymentResult(
                            id=f"failed-{int(datetime.now(UTC).timestamp())}",
                            status=DeploymentStatus.FAILED,
                            provider=provider_type,
                            region=region,
                            error=str(e),
                            started_at=datetime.now(UTC),
                        )
                    )

            return results

    def get_successful_deployments(
        self, results: list[DeploymentResult]
    ) -> list[DeploymentResult]:
        """Filter successful deployments.

        Parameters
        ----------
        results : list[DeploymentResult]
            Deployment results.

        Returns
        -------
        list[DeploymentResult]
            Successful deployments only.
        """
        return [r for r in results if r.status == DeploymentStatus.DEPLOYED]


class CloudCostAnalyzer:
    """Analyze and compare costs across cloud providers."""

    def __init__(self) -> None:
        """Initialize cost analyzer."""
        self.providers = []

        for name in ["aws", "gcp", "azure"]:
            provider = get_provider(name)
            if provider:
                self.providers.append(provider)

    def compare_costs(
        self,
        *,
        start_date: datetime,
        end_date: datetime,
        providers: list[str] | None = None,
    ) -> dict[str, CostReport]:
        """Compare costs across cloud providers.

        Parameters
        ----------
        start_date : datetime
            Report start date.
        end_date : datetime
            Report end date.
        providers : list[str], optional
            Providers to compare. Defaults to all registered.

        Returns
        -------
        dict[str, CostReport]
            Cost reports by provider name.
        """
        with span("multicloud.cost.compare"):
            reports = {}

            target_providers = self.providers
            if providers:
                target_providers = [
                    p for p in self.providers if p.name in providers
                ]

            for provider in target_providers:
                try:
                    cost = provider.get_cost()
                    report = cost.get_cost_report(
                        start_date=start_date, end_date=end_date
                    )
                    reports[provider.name] = report
                    logger.info(
                        f"Cost report for {provider.name}: "
                        f"${report.total_cost:.2f}"
                    )

                except Exception as e:
                    record_exception(e)
                    logger.error(f"Failed to get cost report for {provider.name}: {e}")

            return reports

    def get_cheapest_provider(self, reports: dict[str, CostReport]) -> str | None:
        """Get provider with lowest cost.

        Parameters
        ----------
        reports : dict[str, CostReport]
            Cost reports by provider.

        Returns
        -------
        str | None
            Provider name with lowest cost.
        """
        if not reports:
            return None

        return min(reports.items(), key=lambda x: x[1].total_cost)[0]

    def get_optimization_recommendations(
        self, reports: dict[str, CostReport]
    ) -> list[str]:
        """Get cost optimization recommendations.

        Parameters
        ----------
        reports : dict[str, CostReport]
            Cost reports by provider.

        Returns
        -------
        list[str]
            Optimization recommendations.
        """
        recommendations = []

        # Collect provider-specific recommendations
        for provider_name, report in reports.items():
            for rec in report.recommendations:
                recommendations.append(f"[{provider_name}] {rec}")

        # Add cross-provider recommendations
        if len(reports) > 1:
            cheapest = self.get_cheapest_provider(reports)
            if cheapest:
                recommendations.append(
                    f"Consider migrating more workloads to {cheapest} "
                    f"for cost savings"
                )

        return recommendations


class CloudMetricsAggregator:
    """Aggregate metrics from multiple cloud providers."""

    def __init__(self, providers: list[str]) -> None:
        """Initialize metrics aggregator.

        Parameters
        ----------
        providers : list[str]
            List of cloud provider names.
        """
        self.provider_names = providers
        self.providers = []

        for name in providers:
            provider = get_provider(name)
            if provider:
                self.providers.append(provider)

    def export_metrics(
        self,
        name: str,
        value: float,
        *,
        unit: str = "count",
        dimensions: dict[str, str] | None = None,
    ) -> dict[str, bool]:
        """Export metric to all cloud providers.

        Parameters
        ----------
        name : str
            Metric name.
        value : float
            Metric value.
        unit : str, optional
            Metric unit.
        dimensions : dict[str, str], optional
            Metric dimensions.

        Returns
        -------
        dict[str, bool]
            Export success by provider name.
        """
        with span("multicloud.metrics.export", metric=name):
            results = {}

            for provider in self.providers:
                try:
                    metrics = provider.get_metrics()
                    metrics.put_metric(
                        name, value, unit=unit, dimensions=dimensions
                    )
                    results[provider.name] = True
                    logger.debug(f"Exported metric to {provider.name}")

                except Exception as e:
                    record_exception(e)
                    logger.error(f"Failed to export metric to {provider.name}: {e}")
                    results[provider.name] = False

            return results


__all__ = [
    "CloudCostAnalyzer",
    "CloudMetricsAggregator",
    "MultiCloudDeployer",
    "ProviderRegistry",
    "UnifiedCloudStorage",
    "get_provider",
    "list_providers",
    "register_provider",
]
