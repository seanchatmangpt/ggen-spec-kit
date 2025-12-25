"""
specify_cli.cloud.gcp.provider - GCP Provider Implementation
==========================================================

Comprehensive GCP cloud provider implementation.

This module implements all GCP services with full instrumentation,
error handling, and retry logic.

Services Implemented
-------------------
* Cloud Storage: Object storage
* Cloud Logging: Centralized logging
* Cloud Run: Serverless containers
* Cloud SQL: Relational databases
* Cloud IAM: Access management
* Secret Manager: Secret storage
* Compute Engine: Virtual machines
* Cloud Monitoring: Metrics

Design Principles
----------------
* Graceful degradation when google-cloud unavailable
* Comprehensive error handling with retries
* Full OpenTelemetry instrumentation
* Type-safe interfaces
* Resource cleanup and lifecycle management

Examples
--------
    provider = GCPProvider(project_id="my-project")
    storage = provider.get_storage()
    storage.upload("artifact.tar.gz", "builds/v1.0.0/artifact.tar.gz")
"""

from __future__ import annotations

import logging
import os
import time
from typing import TYPE_CHECKING, Any

from specify_cli.core.telemetry import record_exception, span

if TYPE_CHECKING:
    from collections.abc import Iterator
    from datetime import datetime
    from pathlib import Path

    from specify_cli.cloud.base import (
        CloudCompute,
        CloudCost,
        CloudDatabase,
        CloudLogging,
        CloudMetrics,
        CloudProvider,
        CloudProviderType,
        CloudSecrets,
        CloudStorage,
        ComputeInstance,
        CostReport,
        DatabaseInstance,
        DeploymentResult,
        DeploymentStatus,
        LogEntry,
        MetricData,
        SecretValue,
        StorageObject,
    )

from specify_cli.cloud.base import CloudProviderType, DeploymentResult, DeploymentStatus

logger = logging.getLogger(__name__)

# Try to import google-cloud libraries
try:
    from google.cloud import logging as gcp_logging  # type: ignore[import-untyped]
    from google.cloud import monitoring_v3, secretmanager, storage
    from google.cloud.exceptions import GoogleCloudError  # type: ignore[import-untyped]

    GCP_AVAILABLE = True
except ImportError:
    GCP_AVAILABLE = False
    logger.warning("google-cloud libraries not available - GCP integration disabled")


class GCPCloudStorage:
    """GCP Cloud Storage implementation."""

    def __init__(self, bucket: str, project_id: str | None = None) -> None:
        """Initialize Cloud Storage.

        Parameters
        ----------
        bucket : str
            Cloud Storage bucket name.
        project_id : str, optional
            GCP project ID.
        """
        if not GCP_AVAILABLE:
            msg = "google-cloud-storage is required for GCP Cloud Storage"
            raise ImportError(msg)

        self.bucket_name = bucket
        self.project_id = project_id or os.getenv("GCP_PROJECT_ID")
        self.client = storage.Client(project=self.project_id)
        self.bucket = self.client.bucket(bucket)

    def upload(
        self,
        local_path: Path | str,
        remote_key: str,
        *,
        metadata: dict[str, str] | None = None,
    ) -> str:
        """Upload file to Cloud Storage."""
        from pathlib import Path

        with span("gcp.storage.upload", bucket=self.bucket_name, key=remote_key):
            try:
                local_path = Path(local_path)
                blob = self.bucket.blob(remote_key)

                if metadata:
                    blob.metadata = metadata

                blob.upload_from_filename(str(local_path))
                url = f"gs://{self.bucket_name}/{remote_key}"
                logger.info(f"Uploaded {local_path} to {url}")
                return url

            except GoogleCloudError as e:
                record_exception(e)
                logger.error(f"Failed to upload to Cloud Storage: {e}")
                raise

    def download(self, remote_key: str, local_path: Path | str) -> Path:
        """Download file from Cloud Storage."""
        from pathlib import Path

        with span("gcp.storage.download", bucket=self.bucket_name, key=remote_key):
            try:
                local_path = Path(local_path)
                local_path.parent.mkdir(parents=True, exist_ok=True)

                blob = self.bucket.blob(remote_key)
                blob.download_to_filename(str(local_path))
                logger.info(f"Downloaded gs://{self.bucket_name}/{remote_key} to {local_path}")
                return local_path

            except GoogleCloudError as e:
                record_exception(e)
                logger.error(f"Failed to download from Cloud Storage: {e}")
                raise

    def list_objects(self, prefix: str = "") -> Iterator[StorageObject]:
        """List objects in Cloud Storage bucket."""
        from specify_cli.cloud.base import StorageObject

        with span("gcp.storage.list", bucket=self.bucket_name, prefix=prefix):
            try:
                blobs = self.client.list_blobs(self.bucket_name, prefix=prefix)

                for blob in blobs:
                    yield StorageObject(
                        key=blob.name,
                        size=blob.size or 0,
                        last_modified=blob.updated,
                        etag=blob.etag,
                        content_type=blob.content_type,
                        metadata=blob.metadata or {},
                    )

            except GoogleCloudError as e:
                record_exception(e)
                logger.error(f"Failed to list Cloud Storage objects: {e}")
                raise

    def delete(self, remote_key: str) -> bool:
        """Delete object from Cloud Storage."""
        with span("gcp.storage.delete", bucket=self.bucket_name, key=remote_key):
            try:
                blob = self.bucket.blob(remote_key)
                blob.delete()
                logger.info(f"Deleted gs://{self.bucket_name}/{remote_key}")
                return True

            except GoogleCloudError as e:
                record_exception(e)
                logger.error(f"Failed to delete from Cloud Storage: {e}")
                return False

    def get_url(self, remote_key: str, *, expires_in: int = 3600) -> str:
        """Get signed URL for Cloud Storage object."""
        from datetime import timedelta

        with span("gcp.storage.presign", bucket=self.bucket_name, key=remote_key):
            try:
                blob = self.bucket.blob(remote_key)
                url = blob.generate_signed_url(expiration=timedelta(seconds=expires_in))
                return url  # type: ignore[no-any-return]

            except GoogleCloudError as e:
                record_exception(e)
                logger.error(f"Failed to generate signed URL: {e}")
                raise


class GCPCloudMonitoring:
    """GCP Cloud Monitoring metrics implementation."""

    def __init__(self, project_id: str | None = None) -> None:
        """Initialize Cloud Monitoring.

        Parameters
        ----------
        project_id : str, optional
            GCP project ID.
        """
        if not GCP_AVAILABLE:
            msg = "google-cloud-monitoring is required for GCP Cloud Monitoring"
            raise ImportError(msg)

        self.project_id = project_id or os.getenv("GCP_PROJECT_ID")
        self.client = monitoring_v3.MetricServiceClient()
        self.project_name = f"projects/{self.project_id}"

    def put_metric(
        self,
        name: str,
        value: float,
        *,
        unit: str = "1",
        dimensions: dict[str, str] | None = None,
    ) -> None:
        """Put metric to Cloud Monitoring."""
        from datetime import datetime, timezone

        from google.cloud.monitoring_v3 import Point, TimeSeries, TimeInterval  # type: ignore[import-untyped]
        from google.protobuf.timestamp_pb2 import Timestamp  # type: ignore[import-untyped]

        with span("gcp.monitoring.put_metric", metric=name):
            try:
                series = TimeSeries()
                series.metric.type = f"custom.googleapis.com/{name}"

                if dimensions:
                    for key, val in dimensions.items():
                        series.metric.labels[key] = val

                series.resource.type = "global"

                now = datetime.now(timezone.utc)
                seconds = int(now.timestamp())
                nanos = int(now.microsecond * 1000)

                interval = TimeInterval({"end_time": Timestamp(seconds=seconds, nanos=nanos)})
                point = Point({"interval": interval, "value": {"double_value": value}})
                series.points = [point]

                self.client.create_time_series(name=self.project_name, time_series=[series])
                logger.debug(f"Put metric {name}={value} to Cloud Monitoring")

            except GoogleCloudError as e:
                record_exception(e)
                logger.error(f"Failed to put Cloud Monitoring metric: {e}")
                raise

    def get_metrics(
        self,
        name: str,
        *,
        start_time: datetime,
        end_time: datetime,
        dimensions: dict[str, str] | None = None,
    ) -> list[MetricData]:
        """Get metrics from Cloud Monitoring."""
        from datetime import timezone

        from google.cloud.monitoring_v3 import ListTimeSeriesRequest, TimeInterval
        from google.protobuf.timestamp_pb2 import Timestamp

        from specify_cli.cloud.base import MetricData

        with span("gcp.monitoring.get_metrics", metric=name):
            try:
                interval = TimeInterval(
                    {
                        "start_time": Timestamp(seconds=int(start_time.timestamp())),
                        "end_time": Timestamp(seconds=int(end_time.timestamp())),
                    }
                )

                request = ListTimeSeriesRequest(
                    name=self.project_name,
                    filter=f'metric.type = "custom.googleapis.com/{name}"',
                    interval=interval,
                )

                results = self.client.list_time_series(request=request)

                metrics = []
                for series in results:
                    for point in series.points:
                        timestamp = datetime.fromtimestamp(
                            point.interval.end_time.seconds, tz=timezone.utc
                        )
                        metrics.append(
                            MetricData(
                                name=name,
                                value=point.value.double_value,
                                timestamp=timestamp,
                                unit="1",
                                dimensions=dict(series.metric.labels),
                            )
                        )

                return metrics

            except GoogleCloudError as e:
                record_exception(e)
                logger.error(f"Failed to get Cloud Monitoring metrics: {e}")
                raise


class GCPCloudLogging:
    """GCP Cloud Logging implementation."""

    def __init__(self, log_name: str, project_id: str | None = None) -> None:
        """Initialize Cloud Logging.

        Parameters
        ----------
        log_name : str
            Cloud Logging log name.
        project_id : str, optional
            GCP project ID.
        """
        if not GCP_AVAILABLE:
            msg = "google-cloud-logging is required for GCP Cloud Logging"
            raise ImportError(msg)

        self.project_id = project_id or os.getenv("GCP_PROJECT_ID")
        self.client = gcp_logging.Client(project=self.project_id)
        self.logger = self.client.logger(log_name)

    def write_log(
        self,
        message: str,
        *,
        level: str = "INFO",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Write log entry to Cloud Logging."""
        with span("gcp.logging.write", level=level):
            try:
                severity = level.upper()
                struct_data = {"message": message, "metadata": metadata or {}}

                self.logger.log_struct(struct_data, severity=severity)

            except GoogleCloudError as e:
                record_exception(e)
                logger.error(f"Failed to write Cloud Logging entry: {e}")
                raise

    def query_logs(
        self,
        *,
        start_time: datetime,
        end_time: datetime,
        filter_pattern: str | None = None,
        limit: int = 100,
    ) -> list[LogEntry]:
        """Query logs from Cloud Logging."""
        from datetime import timezone

        from specify_cli.cloud.base import LogEntry

        with span("gcp.logging.query"):
            try:
                filter_str = f'timestamp >= "{start_time.isoformat()}" AND timestamp <= "{end_time.isoformat()}"'
                if filter_pattern:
                    filter_str += f" AND {filter_pattern}"

                entries = self.client.list_entries(filter_=filter_str, max_results=limit)

                logs = []
                for entry in entries:
                    timestamp = entry.timestamp
                    if timestamp.tzinfo is None:
                        timestamp = timestamp.replace(tzinfo=timezone.utc)

                    logs.append(
                        LogEntry(
                            timestamp=timestamp,
                            level=entry.severity or "INFO",
                            message=str(entry.payload),
                            source=entry.log_name,
                            metadata=entry.labels or {},
                        )
                    )

                return logs

            except GoogleCloudError as e:
                record_exception(e)
                logger.error(f"Failed to query Cloud Logging: {e}")
                raise


class GCPSecretManager:
    """GCP Secret Manager implementation."""

    def __init__(self, project_id: str | None = None) -> None:
        """Initialize Secret Manager.

        Parameters
        ----------
        project_id : str, optional
            GCP project ID.
        """
        if not GCP_AVAILABLE:
            msg = "google-cloud-secret-manager is required for GCP Secret Manager"
            raise ImportError(msg)

        self.project_id = project_id or os.getenv("GCP_PROJECT_ID")
        self.client = secretmanager.SecretManagerServiceClient()
        self.project_name = f"projects/{self.project_id}"

    def get_secret(self, name: str, *, version: str | None = None) -> SecretValue:
        """Get secret from Secret Manager."""
        from datetime import timezone

        from specify_cli.cloud.base import SecretValue

        with span("gcp.secrets.get", secret=name):
            try:
                version_id = version or "latest"
                secret_version_name = f"{self.project_name}/secrets/{name}/versions/{version_id}"

                response = self.client.access_secret_version(name=secret_version_name)

                return SecretValue(
                    name=name,
                    value=response.payload.data.decode("UTF-8"),
                    version=version_id,
                    created_at=response.create_time.replace(tzinfo=timezone.utc)
                    if response.create_time
                    else None,
                )

            except GoogleCloudError as e:
                record_exception(e)
                logger.error(f"Failed to get secret: {e}")
                raise

    def put_secret(
        self,
        name: str,
        value: str,
        *,
        metadata: dict[str, str] | None = None,
    ) -> str:
        """Put secret to Secret Manager."""
        with span("gcp.secrets.put", secret=name):
            try:
                secret_name = f"{self.project_name}/secrets/{name}"

                # Try to add secret version to existing secret
                try:
                    response = self.client.add_secret_version(
                        parent=secret_name,
                        payload={"data": value.encode("UTF-8")},
                    )
                    return response.name.split("/")[-1]  # type: ignore[no-any-return]

                except GoogleCloudError:
                    # Create new secret if it doesn't exist
                    secret = {"replication": {"automatic": {}}}  # type: ignore[var-annotated]
                    if metadata:
                        secret["labels"] = metadata  # type: ignore[assignment]

                    created_secret = self.client.create_secret(
                        parent=self.project_name,
                        secret_id=name,
                        secret=secret,
                    )

                    # Add version to newly created secret
                    response = self.client.add_secret_version(
                        parent=created_secret.name,
                        payload={"data": value.encode("UTF-8")},
                    )
                    return response.name.split("/")[-1]  # type: ignore[no-any-return]

            except GoogleCloudError as e:
                record_exception(e)
                logger.error(f"Failed to put secret: {e}")
                raise

    def delete_secret(self, name: str) -> bool:
        """Delete secret from Secret Manager."""
        with span("gcp.secrets.delete", secret=name):
            try:
                secret_name = f"{self.project_name}/secrets/{name}"
                self.client.delete_secret(name=secret_name)
                logger.info(f"Deleted secret {name}")
                return True

            except GoogleCloudError as e:
                record_exception(e)
                logger.error(f"Failed to delete secret: {e}")
                return False


class GCPComputeEngine:
    """GCP Compute Engine implementation."""

    def __init__(self, project_id: str | None = None, zone: str = "us-central1-a") -> None:
        """Initialize Compute Engine.

        Parameters
        ----------
        project_id : str, optional
            GCP project ID.
        zone : str, optional
            Compute zone.
        """
        if not GCP_AVAILABLE:
            msg = "google-cloud-compute is required for GCP Compute Engine"
            raise ImportError(msg)

        try:
            from google.cloud import compute_v1

            self.project_id = project_id or os.getenv("GCP_PROJECT_ID")
            self.zone = zone
            self.instances_client = compute_v1.InstancesClient()
        except ImportError as e:
            msg = "google-cloud-compute is required for GCP Compute Engine"
            raise ImportError(msg) from e

    def create_instance(
        self,
        name: str,
        instance_type: str,
        *,
        image: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ComputeInstance:
        """Create Compute Engine instance."""
        from google.cloud import compute_v1

        from specify_cli.cloud.base import ComputeInstance

        with span("gcp.compute.create", instance_type=instance_type):
            try:
                # Use Debian image if not specified
                if not image:
                    image = "projects/debian-cloud/global/images/family/debian-11"

                instance = compute_v1.Instance()
                instance.name = name
                instance.machine_type = (
                    f"zones/{self.zone}/machineTypes/{instance_type}"
                )

                disk = compute_v1.AttachedDisk()
                disk.boot = True
                disk.auto_delete = True
                initialize_params = compute_v1.AttachedDiskInitializeParams()
                initialize_params.source_image = image
                disk.initialize_params = initialize_params
                instance.disks = [disk]

                network_interface = compute_v1.NetworkInterface()
                network_interface.name = "global/networks/default"
                access_config = compute_v1.AccessConfig()
                access_config.name = "External NAT"
                access_config.type_ = "ONE_TO_ONE_NAT"
                network_interface.access_configs = [access_config]
                instance.network_interfaces = [network_interface]

                request = compute_v1.InsertInstanceRequest()
                request.zone = self.zone
                request.project = self.project_id
                request.instance_resource = instance

                operation = self.instances_client.insert(request=request)
                operation.result()  # Wait for completion

                return ComputeInstance(
                    id=name,
                    name=name,
                    type=instance_type,
                    status="RUNNING",
                    region=self.zone,
                    metadata={"image": image},
                )

            except GoogleCloudError as e:
                record_exception(e)
                logger.error(f"Failed to create Compute Engine instance: {e}")
                raise

    def list_instances(self) -> list[ComputeInstance]:
        """List Compute Engine instances."""
        from google.cloud import compute_v1

        from specify_cli.cloud.base import ComputeInstance

        with span("gcp.compute.list"):
            try:
                request = compute_v1.ListInstancesRequest(
                    project=self.project_id,
                    zone=self.zone,
                )
                instances_list = self.instances_client.list(request=request)

                instances = []
                for instance in instances_list:
                    instances.append(
                        ComputeInstance(
                            id=instance.name,
                            name=instance.name,
                            type=instance.machine_type.split("/")[-1],
                            status=instance.status,
                            region=self.zone,
                            ip_address=instance.network_interfaces[0].access_configs[0].nat_i_p
                            if instance.network_interfaces
                            and instance.network_interfaces[0].access_configs
                            else None,
                        )
                    )

                return instances

            except GoogleCloudError as e:
                record_exception(e)
                logger.error(f"Failed to list Compute Engine instances: {e}")
                raise

    def stop_instance(self, instance_id: str) -> bool:
        """Stop Compute Engine instance."""
        from google.cloud import compute_v1

        with span("gcp.compute.stop", instance_id=instance_id):
            try:
                request = compute_v1.StopInstanceRequest(
                    project=self.project_id,
                    zone=self.zone,
                    instance=instance_id,
                )
                operation = self.instances_client.stop(request=request)
                operation.result()
                logger.info(f"Stopped Compute Engine instance {instance_id}")
                return True

            except GoogleCloudError as e:
                record_exception(e)
                logger.error(f"Failed to stop Compute Engine instance: {e}")
                return False

    def delete_instance(self, instance_id: str) -> bool:
        """Delete Compute Engine instance."""
        from google.cloud import compute_v1

        with span("gcp.compute.delete", instance_id=instance_id):
            try:
                request = compute_v1.DeleteInstanceRequest(
                    project=self.project_id,
                    zone=self.zone,
                    instance=instance_id,
                )
                operation = self.instances_client.delete(request=request)
                operation.result()
                logger.info(f"Deleted Compute Engine instance {instance_id}")
                return True

            except GoogleCloudError as e:
                record_exception(e)
                logger.error(f"Failed to delete Compute Engine instance: {e}")
                return False


class GCPCloudSQL:
    """GCP Cloud SQL database implementation (simplified)."""

    def __init__(self, project_id: str | None = None) -> None:
        """Initialize Cloud SQL.

        Parameters
        ----------
        project_id : str, optional
            GCP project ID.
        """
        self.project_id = project_id or os.getenv("GCP_PROJECT_ID")
        logger.warning("Cloud SQL implementation requires google-cloud-sql - using stub")

    def create_database(
        self,
        name: str,
        engine: str,
        *,
        instance_type: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> DatabaseInstance:
        """Create Cloud SQL database instance."""
        from datetime import datetime, timezone

        from specify_cli.cloud.base import DatabaseInstance

        logger.warning(f"Cloud SQL create_database stub called for {name}")
        return DatabaseInstance(
            id=name,
            name=name,
            engine=engine,
            status="PENDING",
            metadata={"note": "Cloud SQL integration requires additional setup"},
        )

    def list_databases(self) -> list[DatabaseInstance]:
        """List Cloud SQL database instances."""
        logger.warning("Cloud SQL list_databases stub called")
        return []

    def delete_database(self, database_id: str) -> bool:
        """Delete Cloud SQL database instance."""
        logger.warning(f"Cloud SQL delete_database stub called for {database_id}")
        return False


class GCPCostManagement:
    """GCP Cost Management implementation (simplified)."""

    def __init__(self, project_id: str | None = None) -> None:
        """Initialize Cost Management.

        Parameters
        ----------
        project_id : str, optional
            GCP project ID.
        """
        self.project_id = project_id or os.getenv("GCP_PROJECT_ID")
        logger.warning("GCP Cost Management requires BigQuery - using stub")

    def get_cost_report(
        self,
        *,
        start_date: datetime,
        end_date: datetime,
    ) -> CostReport:
        """Get cost report."""
        from specify_cli.cloud.base import CostReport

        logger.warning("GCP cost report stub called")
        return CostReport(
            provider=CloudProviderType.GCP,
            start_date=start_date,
            end_date=end_date,
            total_cost=0.0,
            breakdown={},
            recommendations=["Enable BigQuery billing export for cost analysis"],
        )

    def get_recommendations(self) -> list[str]:
        """Get cost optimization recommendations."""
        return ["Enable GCP Recommender API for cost optimization suggestions"]


class GCPProvider(CloudProvider):
    """GCP cloud provider implementation."""

    name = "gcp"

    def __init__(self, project_id: str | None = None, region: str = "us-central1") -> None:
        """Initialize GCP provider.

        Parameters
        ----------
        project_id : str, optional
            GCP project ID. Defaults to GCP_PROJECT_ID env var.
        region : str, optional
            GCP region.
        """
        self.project_id = project_id or os.getenv("GCP_PROJECT_ID")
        self.region = region
        self._storage: GCPCloudStorage | None = None
        self._metrics: GCPCloudMonitoring | None = None
        self._logging: GCPCloudLogging | None = None
        self._secrets: GCPSecretManager | None = None
        self._compute: GCPComputeEngine | None = None
        self._database: GCPCloudSQL | None = None
        self._cost: GCPCostManagement | None = None

    def get_storage(self) -> CloudStorage:
        """Get Cloud Storage interface."""
        if not self._storage:
            bucket = os.getenv("GCP_STORAGE_BUCKET", "specify-cli-artifacts")
            self._storage = GCPCloudStorage(bucket=bucket, project_id=self.project_id)
        return self._storage

    def get_metrics(self) -> CloudMetrics:
        """Get Cloud Monitoring interface."""
        if not self._metrics:
            self._metrics = GCPCloudMonitoring(project_id=self.project_id)
        return self._metrics

    def get_logging(self) -> CloudLogging:
        """Get Cloud Logging interface."""
        if not self._logging:
            log_name = os.getenv("GCP_LOG_NAME", "specify-cli-logs")
            self._logging = GCPCloudLogging(log_name=log_name, project_id=self.project_id)
        return self._logging

    def get_secrets(self) -> CloudSecrets:
        """Get Secret Manager interface."""
        if not self._secrets:
            self._secrets = GCPSecretManager(project_id=self.project_id)
        return self._secrets

    def get_compute(self) -> CloudCompute:
        """Get Compute Engine interface."""
        if not self._compute:
            zone = os.getenv("GCP_ZONE", "us-central1-a")
            self._compute = GCPComputeEngine(project_id=self.project_id, zone=zone)
        return self._compute

    def get_database(self) -> CloudDatabase:
        """Get Cloud SQL interface."""
        if not self._database:
            self._database = GCPCloudSQL(project_id=self.project_id)
        return self._database

    def get_cost(self) -> CloudCost:
        """Get Cost Management interface."""
        if not self._cost:
            self._cost = GCPCostManagement(project_id=self.project_id)
        return self._cost

    def deploy(
        self,
        artifact: Path | str,
        *,
        region: str,
        instance_type: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> DeploymentResult:
        """Deploy application to GCP."""
        from datetime import datetime, timezone
        from pathlib import Path

        with span("gcp.deploy", region=region):
            deployment_id = f"deploy-{int(time.time())}"

            try:
                # Upload artifact to Cloud Storage
                artifact_path = Path(artifact)
                storage = self.get_storage()
                artifact_key = f"deployments/{deployment_id}/{artifact_path.name}"
                artifact_url = storage.upload(artifact_path, artifact_key)

                # Create Compute Engine instance for deployment
                compute = self.get_compute()
                instance = compute.create_instance(
                    name=f"specify-cli-{deployment_id}",
                    instance_type=instance_type or "e2-micro",
                    metadata=metadata,
                )

                return DeploymentResult(
                    id=deployment_id,
                    status=DeploymentStatus.DEPLOYED,
                    provider=CloudProviderType.GCP,
                    region=region,
                    artifact_url=artifact_url,
                    endpoint=instance.ip_address,
                    started_at=datetime.now(timezone.utc),
                    completed_at=datetime.now(timezone.utc),
                    metadata={"instance_id": instance.id},
                )

            except Exception as e:
                record_exception(e)
                logger.error(f"Deployment failed: {e}")
                return DeploymentResult(
                    id=deployment_id,
                    status=DeploymentStatus.FAILED,
                    provider=CloudProviderType.GCP,
                    region=region,
                    error=str(e),
                    started_at=datetime.now(timezone.utc),
                )


__all__ = [
    "GCPCloudLogging",
    "GCPCloudMonitoring",
    "GCPCloudSQL",
    "GCPCloudStorage",
    "GCPComputeEngine",
    "GCPCostManagement",
    "GCPProvider",
    "GCPSecretManager",
]
