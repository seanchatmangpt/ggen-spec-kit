"""
specify_cli.cloud.base - Cloud Provider Base Abstractions
========================================================

Base classes and protocols for cloud provider implementations.

This module defines the common interfaces that all cloud providers must implement,
enabling unified multi-cloud operations.

Key Abstractions
---------------
* **CloudProvider**: Base cloud provider interface
* **CloudStorage**: Artifact and object storage
* **CloudMetrics**: Metrics and monitoring
* **CloudLogging**: Centralized logging
* **CloudSecrets**: Secret and credential management
* **CloudCompute**: Compute resources (serverless, VMs)
* **CloudDatabase**: Managed database services
* **CloudCost**: Cost tracking and optimization

Design Principles
----------------
* Protocol-based design for duck typing
* Graceful degradation when providers unavailable
* Comprehensive error handling
* Full OpenTelemetry instrumentation
* Type-safe interfaces

Examples
--------
    # Implement a cloud provider
    class MyCloudProvider(CloudProvider):
        name = "mycloud"

        def get_storage(self) -> CloudStorage:
            return MyCloudStorage()

        def get_metrics(self) -> CloudMetrics:
            return MyCloudMetrics()

See Also
--------
- :mod:`specify_cli.cloud.aws` : AWS implementation
- :mod:`specify_cli.cloud.gcp` : GCP implementation
- :mod:`specify_cli.cloud.azure` : Azure implementation
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from collections.abc import Iterator
    from datetime import datetime
    from pathlib import Path


class CloudProviderType(str, Enum):
    """Supported cloud provider types."""

    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    LOCAL = "local"


class DeploymentStatus(str, Enum):
    """Deployment status values."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DEPLOYED = "deployed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class CloudCredentials:
    """Cloud provider credentials."""

    provider: CloudProviderType
    access_key: str | None = None
    secret_key: str | None = None
    token: str | None = None
    region: str | None = None
    project_id: str | None = None
    subscription_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class StorageObject:
    """Cloud storage object metadata."""

    key: str
    size: int
    last_modified: datetime
    etag: str | None = None
    content_type: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass
class MetricData:
    """Cloud metric data point."""

    name: str
    value: float
    timestamp: datetime
    unit: str = "count"
    dimensions: dict[str, str] = field(default_factory=dict)


@dataclass
class LogEntry:
    """Cloud log entry."""

    timestamp: datetime
    level: str
    message: str
    source: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SecretValue:
    """Cloud secret value."""

    name: str
    value: str
    version: str | None = None
    created_at: datetime | None = None
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass
class ComputeInstance:
    """Cloud compute instance."""

    id: str
    name: str
    type: str
    status: str
    region: str
    ip_address: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DatabaseInstance:
    """Cloud database instance."""

    id: str
    name: str
    engine: str
    status: str
    endpoint: str | None = None
    port: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CostReport:
    """Cloud cost report."""

    provider: CloudProviderType
    start_date: datetime
    end_date: datetime
    total_cost: float
    currency: str = "USD"
    breakdown: dict[str, float] = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)


@dataclass
class DeploymentResult:
    """Cloud deployment result."""

    id: str
    status: DeploymentStatus
    provider: CloudProviderType
    region: str
    artifact_url: str | None = None
    endpoint: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


# --- Protocol Interfaces ---


class CloudStorage(Protocol):
    """Cloud storage interface."""

    def upload(
        self,
        local_path: Path | str,
        remote_key: str,
        *,
        metadata: dict[str, str] | None = None,
    ) -> str:
        """Upload file to cloud storage.

        Parameters
        ----------
        local_path : Path | str
            Local file path to upload.
        remote_key : str
            Remote object key/path.
        metadata : dict[str, str], optional
            Object metadata.

        Returns
        -------
        str
            Remote object URL.
        """
        ...

    def download(self, remote_key: str, local_path: Path | str) -> Path:
        """Download file from cloud storage.

        Parameters
        ----------
        remote_key : str
            Remote object key/path.
        local_path : Path | str
            Local destination path.

        Returns
        -------
        Path
            Local file path.
        """
        ...

    def list_objects(self, prefix: str = "") -> Iterator[StorageObject]:
        """List objects in storage.

        Parameters
        ----------
        prefix : str, optional
            Object key prefix filter.

        Yields
        ------
        StorageObject
            Storage object metadata.
        """
        ...

    def delete(self, remote_key: str) -> bool:
        """Delete object from storage.

        Parameters
        ----------
        remote_key : str
            Remote object key/path.

        Returns
        -------
        bool
            True if deleted successfully.
        """
        ...

    def get_url(self, remote_key: str, *, expires_in: int = 3600) -> str:
        """Get signed URL for object.

        Parameters
        ----------
        remote_key : str
            Remote object key/path.
        expires_in : int, optional
            URL expiration time in seconds.

        Returns
        -------
        str
            Signed URL.
        """
        ...


class CloudMetrics(Protocol):
    """Cloud metrics interface."""

    def put_metric(
        self,
        name: str,
        value: float,
        *,
        unit: str = "count",
        dimensions: dict[str, str] | None = None,
    ) -> None:
        """Put metric data point.

        Parameters
        ----------
        name : str
            Metric name.
        value : float
            Metric value.
        unit : str, optional
            Metric unit.
        dimensions : dict[str, str], optional
            Metric dimensions/tags.
        """
        ...

    def get_metrics(
        self,
        name: str,
        *,
        start_time: datetime,
        end_time: datetime,
        dimensions: dict[str, str] | None = None,
    ) -> list[MetricData]:
        """Get metric data points.

        Parameters
        ----------
        name : str
            Metric name.
        start_time : datetime
            Query start time.
        end_time : datetime
            Query end time.
        dimensions : dict[str, str], optional
            Dimension filters.

        Returns
        -------
        list[MetricData]
            Metric data points.
        """
        ...


class CloudLogging(Protocol):
    """Cloud logging interface."""

    def write_log(
        self,
        message: str,
        *,
        level: str = "INFO",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Write log entry.

        Parameters
        ----------
        message : str
            Log message.
        level : str, optional
            Log level.
        metadata : dict[str, Any], optional
            Additional metadata.
        """
        ...

    def query_logs(
        self,
        *,
        start_time: datetime,
        end_time: datetime,
        filter_pattern: str | None = None,
        limit: int = 100,
    ) -> list[LogEntry]:
        """Query log entries.

        Parameters
        ----------
        start_time : datetime
            Query start time.
        end_time : datetime
            Query end time.
        filter_pattern : str, optional
            Log filter pattern.
        limit : int, optional
            Maximum results.

        Returns
        -------
        list[LogEntry]
            Log entries.
        """
        ...


class CloudSecrets(Protocol):
    """Cloud secrets management interface."""

    def get_secret(self, name: str, *, version: str | None = None) -> SecretValue:
        """Get secret value.

        Parameters
        ----------
        name : str
            Secret name.
        version : str, optional
            Secret version.

        Returns
        -------
        SecretValue
            Secret value.
        """
        ...

    def put_secret(
        self,
        name: str,
        value: str,
        *,
        metadata: dict[str, str] | None = None,
    ) -> str:
        """Store secret value.

        Parameters
        ----------
        name : str
            Secret name.
        value : str
            Secret value.
        metadata : dict[str, str], optional
            Secret metadata.

        Returns
        -------
        str
            Secret version/ARN.
        """
        ...

    def delete_secret(self, name: str) -> bool:
        """Delete secret.

        Parameters
        ----------
        name : str
            Secret name.

        Returns
        -------
        bool
            True if deleted successfully.
        """
        ...


class CloudCompute(Protocol):
    """Cloud compute interface."""

    def create_instance(
        self,
        name: str,
        instance_type: str,
        *,
        image: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ComputeInstance:
        """Create compute instance.

        Parameters
        ----------
        name : str
            Instance name.
        instance_type : str
            Instance type/size.
        image : str, optional
            OS image.
        metadata : dict[str, Any], optional
            Instance metadata.

        Returns
        -------
        ComputeInstance
            Created instance.
        """
        ...

    def list_instances(self) -> list[ComputeInstance]:
        """List compute instances.

        Returns
        -------
        list[ComputeInstance]
            Compute instances.
        """
        ...

    def stop_instance(self, instance_id: str) -> bool:
        """Stop compute instance.

        Parameters
        ----------
        instance_id : str
            Instance ID.

        Returns
        -------
        bool
            True if stopped successfully.
        """
        ...

    def delete_instance(self, instance_id: str) -> bool:
        """Delete compute instance.

        Parameters
        ----------
        instance_id : str
            Instance ID.

        Returns
        -------
        bool
            True if deleted successfully.
        """
        ...


class CloudDatabase(Protocol):
    """Cloud database interface."""

    def create_database(
        self,
        name: str,
        engine: str,
        *,
        instance_type: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> DatabaseInstance:
        """Create database instance.

        Parameters
        ----------
        name : str
            Database name.
        engine : str
            Database engine (postgres, mysql, etc.).
        instance_type : str, optional
            Instance type/size.
        metadata : dict[str, Any], optional
            Database metadata.

        Returns
        -------
        DatabaseInstance
            Created database.
        """
        ...

    def list_databases(self) -> list[DatabaseInstance]:
        """List database instances.

        Returns
        -------
        list[DatabaseInstance]
            Database instances.
        """
        ...

    def delete_database(self, database_id: str) -> bool:
        """Delete database instance.

        Parameters
        ----------
        database_id : str
            Database ID.

        Returns
        -------
        bool
            True if deleted successfully.
        """
        ...


class CloudCost(Protocol):
    """Cloud cost management interface."""

    def get_cost_report(
        self,
        *,
        start_date: datetime,
        end_date: datetime,
    ) -> CostReport:
        """Get cost report.

        Parameters
        ----------
        start_date : datetime
            Report start date.
        end_date : datetime
            Report end date.

        Returns
        -------
        CostReport
            Cost report.
        """
        ...

    def get_recommendations(self) -> list[str]:
        """Get cost optimization recommendations.

        Returns
        -------
        list[str]
            Optimization recommendations.
        """
        ...


class CloudProvider(ABC):
    """Base cloud provider interface."""

    name: str

    @abstractmethod
    def get_storage(self) -> CloudStorage:
        """Get storage interface."""
        ...

    @abstractmethod
    def get_metrics(self) -> CloudMetrics:
        """Get metrics interface."""
        ...

    @abstractmethod
    def get_logging(self) -> CloudLogging:
        """Get logging interface."""
        ...

    @abstractmethod
    def get_secrets(self) -> CloudSecrets:
        """Get secrets interface."""
        ...

    @abstractmethod
    def get_compute(self) -> CloudCompute:
        """Get compute interface."""
        ...

    @abstractmethod
    def get_database(self) -> CloudDatabase:
        """Get database interface."""
        ...

    @abstractmethod
    def get_cost(self) -> CloudCost:
        """Get cost management interface."""
        ...

    @abstractmethod
    def deploy(
        self,
        artifact: Path | str,
        *,
        region: str,
        instance_type: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> DeploymentResult:
        """Deploy application to cloud.

        Parameters
        ----------
        artifact : Path | str
            Artifact to deploy.
        region : str
            Deployment region.
        instance_type : str, optional
            Compute instance type.
        metadata : dict[str, Any], optional
            Deployment metadata.

        Returns
        -------
        DeploymentResult
            Deployment result.
        """
        ...


__all__ = [
    "CloudCompute",
    "CloudCost",
    "CloudCredentials",
    "CloudDatabase",
    "CloudLogging",
    "CloudMetrics",
    "CloudProvider",
    "CloudProviderType",
    "CloudSecrets",
    "CloudStorage",
    "ComputeInstance",
    "CostReport",
    "DatabaseInstance",
    "DeploymentResult",
    "DeploymentStatus",
    "LogEntry",
    "MetricData",
    "SecretValue",
    "StorageObject",
]
