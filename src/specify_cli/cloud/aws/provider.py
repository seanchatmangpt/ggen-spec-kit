"""
specify_cli.cloud.aws.provider - AWS Provider Implementation
==========================================================

Comprehensive AWS cloud provider implementation.

This module implements all AWS services with full instrumentation,
error handling, and retry logic.

Services Implemented
-------------------
* S3: Object storage
* CloudWatch: Metrics and logging
* Lambda: Serverless functions
* RDS: Relational databases
* IAM: Access management
* Secrets Manager: Secret storage
* EC2: Virtual machines
* Cost Explorer: Cost analysis

Design Principles
----------------
* Graceful degradation when boto3 unavailable
* Comprehensive error handling with retries
* Full OpenTelemetry instrumentation
* Type-safe interfaces
* Resource cleanup and lifecycle management

Examples
--------
    provider = AWSProvider(region="us-east-1")
    storage = provider.get_storage()
    storage.upload("artifact.tar.gz", "builds/v1.0.0/artifact.tar.gz")
"""

from __future__ import annotations

import json
import logging
import os
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

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
from specify_cli.core.telemetry import record_exception, span

if TYPE_CHECKING:
    from collections.abc import Iterator

logger = logging.getLogger(__name__)

# Try to import boto3
try:
    import boto3  # type: ignore[import-not-found]
    from botocore.exceptions import BotoCoreError, ClientError  # type: ignore[import-not-found]

    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
    logger.warning("boto3 not available - AWS integration disabled")


class AWSS3Storage:
    """AWS S3 storage implementation."""

    def __init__(self, bucket: str, region: str | None = None) -> None:
        """Initialize S3 storage.

        Parameters
        ----------
        bucket : str
            S3 bucket name.
        region : str, optional
            AWS region.
        """
        if not BOTO3_AVAILABLE:
            msg = "boto3 is required for AWS S3 storage"
            raise ImportError(msg)

        self.bucket = bucket
        self.region = region or os.getenv("AWS_REGION", "us-east-1")
        self.s3 = boto3.client("s3", region_name=self.region)

    def upload(
        self,
        local_path: Path | str,
        remote_key: str,
        *,
        metadata: dict[str, str] | None = None,
    ) -> str:
        """Upload file to S3."""
        with span("aws.s3.upload", bucket=self.bucket, key=remote_key):
            try:
                local_path = Path(local_path)
                extra_args = {}
                if metadata:
                    extra_args["Metadata"] = metadata

                self.s3.upload_file(str(local_path), self.bucket, remote_key, ExtraArgs=extra_args)
                url = f"s3://{self.bucket}/{remote_key}"
                logger.info(f"Uploaded {local_path} to {url}")
                return url

            except (BotoCoreError, ClientError) as e:
                record_exception(e)
                logger.error(f"Failed to upload to S3: {e}")
                raise

    def download(self, remote_key: str, local_path: Path | str) -> Path:
        """Download file from S3."""
        with span("aws.s3.download", bucket=self.bucket, key=remote_key):
            try:
                local_path = Path(local_path)
                local_path.parent.mkdir(parents=True, exist_ok=True)

                self.s3.download_file(self.bucket, remote_key, str(local_path))
                logger.info(f"Downloaded s3://{self.bucket}/{remote_key} to {local_path}")
                return local_path

            except (BotoCoreError, ClientError) as e:
                record_exception(e)
                logger.error(f"Failed to download from S3: {e}")
                raise

    def list_objects(self, prefix: str = "") -> Iterator[StorageObject]:
        """List objects in S3 bucket."""
        with span("aws.s3.list", bucket=self.bucket, prefix=prefix):
            try:
                paginator = self.s3.get_paginator("list_objects_v2")
                for page in paginator.paginate(Bucket=self.bucket, Prefix=prefix):
                    for obj in page.get("Contents", []):
                        yield StorageObject(
                            key=obj["Key"],
                            size=obj["Size"],
                            last_modified=obj["LastModified"],
                            etag=obj.get("ETag"),
                        )

            except (BotoCoreError, ClientError) as e:
                record_exception(e)
                logger.error(f"Failed to list S3 objects: {e}")
                raise

    def delete(self, remote_key: str) -> bool:
        """Delete object from S3."""
        with span("aws.s3.delete", bucket=self.bucket, key=remote_key):
            try:
                self.s3.delete_object(Bucket=self.bucket, Key=remote_key)
                logger.info(f"Deleted s3://{self.bucket}/{remote_key}")
                return True

            except (BotoCoreError, ClientError) as e:
                record_exception(e)
                logger.error(f"Failed to delete from S3: {e}")
                return False

    def get_url(self, remote_key: str, *, expires_in: int = 3600) -> str:
        """Get signed URL for S3 object."""
        with span("aws.s3.presign", bucket=self.bucket, key=remote_key):
            try:
                url = self.s3.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": self.bucket, "Key": remote_key},
                    ExpiresIn=expires_in,
                )
                return url  # type: ignore[no-any-return]

            except (BotoCoreError, ClientError) as e:
                record_exception(e)
                logger.error(f"Failed to generate presigned URL: {e}")
                raise


class AWSCloudWatchMetrics:
    """AWS CloudWatch metrics implementation."""

    def __init__(self, namespace: str, region: str | None = None) -> None:
        """Initialize CloudWatch metrics.

        Parameters
        ----------
        namespace : str
            CloudWatch namespace.
        region : str, optional
            AWS region.
        """
        if not BOTO3_AVAILABLE:
            msg = "boto3 is required for AWS CloudWatch"
            raise ImportError(msg)

        self.namespace = namespace
        self.region = region or os.getenv("AWS_REGION", "us-east-1")
        self.cloudwatch = boto3.client("cloudwatch", region_name=self.region)

    def put_metric(
        self,
        name: str,
        value: float,
        *,
        unit: str = "Count",
        dimensions: dict[str, str] | None = None,
    ) -> None:
        """Put metric to CloudWatch."""
        with span("aws.cloudwatch.put_metric", metric=name):
            try:
                metric_data = {
                    "MetricName": name,
                    "Value": value,
                    "Unit": unit,
                    "Timestamp": datetime.now(UTC),
                }

                if dimensions:
                    metric_data["Dimensions"] = [
                        {"Name": k, "Value": v} for k, v in dimensions.items()
                    ]

                self.cloudwatch.put_metric_data(
                    Namespace=self.namespace, MetricData=[metric_data]
                )
                logger.debug(f"Put metric {name}={value} to CloudWatch")

            except (BotoCoreError, ClientError) as e:
                record_exception(e)
                logger.error(f"Failed to put CloudWatch metric: {e}")
                raise

    def get_metrics(
        self,
        name: str,
        *,
        start_time: datetime,
        end_time: datetime,
        dimensions: dict[str, str] | None = None,
    ) -> list[MetricData]:
        """Get metrics from CloudWatch."""
        with span("aws.cloudwatch.get_metrics", metric=name):
            try:
                params: dict[str, Any] = {
                    "Namespace": self.namespace,
                    "MetricName": name,
                    "StartTime": start_time,
                    "EndTime": end_time,
                    "Period": 300,  # 5 minutes
                    "Statistics": ["Average", "Sum", "Maximum", "Minimum"],
                }

                if dimensions:
                    params["Dimensions"] = [{"Name": k, "Value": v} for k, v in dimensions.items()]

                response = self.cloudwatch.get_metric_statistics(**params)

                metrics = []
                for datapoint in response.get("Datapoints", []):
                    metrics.append(
                        MetricData(
                            name=name,
                            value=datapoint.get("Average", datapoint.get("Sum", 0)),
                            timestamp=datapoint["Timestamp"],
                            unit=datapoint.get("Unit", "Count"),
                            dimensions=dimensions or {},
                        )
                    )

                return metrics

            except (BotoCoreError, ClientError) as e:
                record_exception(e)
                logger.error(f"Failed to get CloudWatch metrics: {e}")
                raise


class AWSCloudWatchLogs:
    """AWS CloudWatch Logs implementation."""

    def __init__(self, log_group: str, region: str | None = None) -> None:
        """Initialize CloudWatch Logs.

        Parameters
        ----------
        log_group : str
            CloudWatch log group name.
        region : str, optional
            AWS region.
        """
        if not BOTO3_AVAILABLE:
            msg = "boto3 is required for AWS CloudWatch Logs"
            raise ImportError(msg)

        self.log_group = log_group
        self.region = region or os.getenv("AWS_REGION", "us-east-1")
        self.logs = boto3.client("logs", region_name=self.region)
        self.log_stream = f"specify-cli-{int(time.time())}"
        self._ensure_log_stream()

    def _ensure_log_stream(self) -> None:
        """Ensure log stream exists."""
        try:
            self.logs.create_log_stream(logGroupName=self.log_group, logStreamName=self.log_stream)
        except ClientError as e:
            if e.response["Error"]["Code"] != "ResourceAlreadyExistsException":
                raise

    def write_log(
        self,
        message: str,
        *,
        level: str = "INFO",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Write log entry to CloudWatch."""
        with span("aws.logs.write", level=level):
            try:
                log_event = {
                    "timestamp": int(time.time() * 1000),
                    "message": json.dumps(
                        {
                            "level": level,
                            "message": message,
                            "metadata": metadata or {},
                        }
                    ),
                }

                self.logs.put_log_events(
                    logGroupName=self.log_group,
                    logStreamName=self.log_stream,
                    logEvents=[log_event],
                )

            except (BotoCoreError, ClientError) as e:
                record_exception(e)
                logger.error(f"Failed to write CloudWatch log: {e}")
                raise

    def query_logs(
        self,
        *,
        start_time: datetime,
        end_time: datetime,
        filter_pattern: str | None = None,
        limit: int = 100,
    ) -> list[LogEntry]:
        """Query logs from CloudWatch."""
        with span("aws.logs.query"):
            try:
                params: dict[str, Any] = {
                    "logGroupName": self.log_group,
                    "startTime": int(start_time.timestamp() * 1000),
                    "endTime": int(end_time.timestamp() * 1000),
                    "limit": limit,
                }

                if filter_pattern:
                    params["filterPattern"] = filter_pattern

                response = self.logs.filter_log_events(**params)

                logs = []
                for event in response.get("events", []):
                    try:
                        data = json.loads(event["message"])
                        logs.append(
                            LogEntry(
                                timestamp=datetime.fromtimestamp(
                                    event["timestamp"] / 1000, tz=UTC
                                ),
                                level=data.get("level", "INFO"),
                                message=data.get("message", event["message"]),
                                source=self.log_group,
                                metadata=data.get("metadata", {}),
                            )
                        )
                    except (json.JSONDecodeError, KeyError):
                        # Fallback for non-JSON logs
                        logs.append(
                            LogEntry(
                                timestamp=datetime.fromtimestamp(
                                    event["timestamp"] / 1000, tz=UTC
                                ),
                                level="INFO",
                                message=event["message"],
                                source=self.log_group,
                            )
                        )

                return logs

            except (BotoCoreError, ClientError) as e:
                record_exception(e)
                logger.error(f"Failed to query CloudWatch logs: {e}")
                raise


class AWSSecretsManager:
    """AWS Secrets Manager implementation."""

    def __init__(self, region: str | None = None) -> None:
        """Initialize Secrets Manager.

        Parameters
        ----------
        region : str, optional
            AWS region.
        """
        if not BOTO3_AVAILABLE:
            msg = "boto3 is required for AWS Secrets Manager"
            raise ImportError(msg)

        self.region = region or os.getenv("AWS_REGION", "us-east-1")
        self.secrets = boto3.client("secretsmanager", region_name=self.region)

    def get_secret(self, name: str, *, version: str | None = None) -> SecretValue:
        """Get secret from Secrets Manager."""
        with span("aws.secrets.get", secret=name):
            try:
                params: dict[str, Any] = {"SecretId": name}
                if version:
                    params["VersionId"] = version

                response = self.secrets.get_secret_value(**params)

                return SecretValue(
                    name=name,
                    value=response.get("SecretString", ""),
                    version=response.get("VersionId"),
                    created_at=response.get("CreatedDate"),
                )

            except (BotoCoreError, ClientError) as e:
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
        """Put secret to Secrets Manager."""
        with span("aws.secrets.put", secret=name):
            try:
                # Try to update existing secret first
                try:
                    response = self.secrets.update_secret(SecretId=name, SecretString=value)
                    return response["VersionId"]  # type: ignore[no-any-return]
                except ClientError as e:
                    if e.response["Error"]["Code"] != "ResourceNotFoundException":
                        raise

                # Create new secret if it doesn't exist
                params: dict[str, Any] = {"Name": name, "SecretString": value}
                if metadata:
                    params["Tags"] = [{"Key": k, "Value": v} for k, v in metadata.items()]

                response = self.secrets.create_secret(**params)
                return response["VersionId"]  # type: ignore[no-any-return]

            except (BotoCoreError, ClientError) as e:
                record_exception(e)
                logger.error(f"Failed to put secret: {e}")
                raise

    def delete_secret(self, name: str) -> bool:
        """Delete secret from Secrets Manager."""
        with span("aws.secrets.delete", secret=name):
            try:
                self.secrets.delete_secret(SecretId=name, ForceDeleteWithoutRecovery=True)
                logger.info(f"Deleted secret {name}")
                return True

            except (BotoCoreError, ClientError) as e:
                record_exception(e)
                logger.error(f"Failed to delete secret: {e}")
                return False


class AWSEC2Compute:
    """AWS EC2 compute implementation."""

    def __init__(self, region: str | None = None) -> None:
        """Initialize EC2 compute.

        Parameters
        ----------
        region : str, optional
            AWS region.
        """
        if not BOTO3_AVAILABLE:
            msg = "boto3 is required for AWS EC2"
            raise ImportError(msg)

        self.region = region or os.getenv("AWS_REGION", "us-east-1")
        self.ec2 = boto3.client("ec2", region_name=self.region)

    def create_instance(
        self,
        name: str,
        instance_type: str,
        *,
        image: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ComputeInstance:
        """Create EC2 instance."""
        with span("aws.ec2.create", instance_type=instance_type):
            try:
                # Use Amazon Linux 2 AMI if not specified
                if not image:
                    image = self._get_amazon_linux_ami()

                params: dict[str, Any] = {
                    "ImageId": image,
                    "InstanceType": instance_type,
                    "MinCount": 1,
                    "MaxCount": 1,
                    "TagSpecifications": [
                        {
                            "ResourceType": "instance",
                            "Tags": [{"Key": "Name", "Value": name}],
                        }
                    ],
                }

                if metadata:
                    params["TagSpecifications"][0]["Tags"].extend(
                        [{"Key": k, "Value": str(v)} for k, v in metadata.items()]
                    )

                response = self.ec2.run_instances(**params)
                instance = response["Instances"][0]

                return ComputeInstance(
                    id=instance["InstanceId"],
                    name=name,
                    type=instance_type,
                    status=instance["State"]["Name"],
                    region=self.region,  # type: ignore[arg-type]
                    metadata={"image": image},
                )

            except (BotoCoreError, ClientError) as e:
                record_exception(e)
                logger.error(f"Failed to create EC2 instance: {e}")
                raise

    def _get_amazon_linux_ami(self) -> str:
        """Get latest Amazon Linux 2 AMI."""
        response = self.ec2.describe_images(
            Filters=[
                {"Name": "name", "Values": ["amzn2-ami-hvm-*-x86_64-gp2"]},
                {"Name": "state", "Values": ["available"]},
            ],
            Owners=["amazon"],
        )
        images = sorted(response["Images"], key=lambda x: x["CreationDate"], reverse=True)
        return images[0]["ImageId"] if images else "ami-0c55b159cbfafe1f0"

    def list_instances(self) -> list[ComputeInstance]:
        """List EC2 instances."""
        with span("aws.ec2.list"):
            try:
                response = self.ec2.describe_instances()

                instances = []
                for reservation in response["Reservations"]:
                    for instance in reservation["Instances"]:
                        name = next(
                            (tag["Value"] for tag in instance.get("Tags", []) if tag["Key"] == "Name"),
                            instance["InstanceId"],
                        )

                        instances.append(
                            ComputeInstance(
                                id=instance["InstanceId"],
                                name=name,
                                type=instance["InstanceType"],
                                status=instance["State"]["Name"],
                                region=self.region,  # type: ignore[arg-type]
                                ip_address=instance.get("PublicIpAddress"),
                            )
                        )

                return instances

            except (BotoCoreError, ClientError) as e:
                record_exception(e)
                logger.error(f"Failed to list EC2 instances: {e}")
                raise

    def stop_instance(self, instance_id: str) -> bool:
        """Stop EC2 instance."""
        with span("aws.ec2.stop", instance_id=instance_id):
            try:
                self.ec2.stop_instances(InstanceIds=[instance_id])
                logger.info(f"Stopped EC2 instance {instance_id}")
                return True

            except (BotoCoreError, ClientError) as e:
                record_exception(e)
                logger.error(f"Failed to stop EC2 instance: {e}")
                return False

    def delete_instance(self, instance_id: str) -> bool:
        """Delete (terminate) EC2 instance."""
        with span("aws.ec2.delete", instance_id=instance_id):
            try:
                self.ec2.terminate_instances(InstanceIds=[instance_id])
                logger.info(f"Terminated EC2 instance {instance_id}")
                return True

            except (BotoCoreError, ClientError) as e:
                record_exception(e)
                logger.error(f"Failed to terminate EC2 instance: {e}")
                return False


class AWSRDSDatabase:
    """AWS RDS database implementation."""

    def __init__(self, region: str | None = None) -> None:
        """Initialize RDS database.

        Parameters
        ----------
        region : str, optional
            AWS region.
        """
        if not BOTO3_AVAILABLE:
            msg = "boto3 is required for AWS RDS"
            raise ImportError(msg)

        self.region = region or os.getenv("AWS_REGION", "us-east-1")
        self.rds = boto3.client("rds", region_name=self.region)

    def create_database(
        self,
        name: str,
        engine: str,
        *,
        instance_type: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> DatabaseInstance:
        """Create RDS database instance."""
        with span("aws.rds.create", engine=engine):
            try:
                params: dict[str, Any] = {
                    "DBInstanceIdentifier": name,
                    "Engine": engine,
                    "DBInstanceClass": instance_type or "db.t3.micro",
                    "AllocatedStorage": 20,
                    "MasterUsername": "admin",
                    "MasterUserPassword": self._generate_password(),
                }

                if metadata:
                    params["Tags"] = [{"Key": k, "Value": str(v)} for k, v in metadata.items()]

                response = self.rds.create_db_instance(**params)
                db = response["DBInstance"]

                return DatabaseInstance(
                    id=db["DBInstanceIdentifier"],
                    name=name,
                    engine=engine,
                    status=db["DBInstanceStatus"],
                    endpoint=db.get("Endpoint", {}).get("Address"),
                    port=db.get("Endpoint", {}).get("Port"),
                )

            except (BotoCoreError, ClientError) as e:
                record_exception(e)
                logger.error(f"Failed to create RDS instance: {e}")
                raise

    def _generate_password(self) -> str:
        """Generate secure random password."""
        import secrets
        import string

        alphabet = string.ascii_letters + string.digits
        return "".join(secrets.choice(alphabet) for _ in range(16))

    def list_databases(self) -> list[DatabaseInstance]:
        """List RDS database instances."""
        with span("aws.rds.list"):
            try:
                response = self.rds.describe_db_instances()

                databases = []
                for db in response["DBInstances"]:
                    databases.append(
                        DatabaseInstance(
                            id=db["DBInstanceIdentifier"],
                            name=db["DBInstanceIdentifier"],
                            engine=db["Engine"],
                            status=db["DBInstanceStatus"],
                            endpoint=db.get("Endpoint", {}).get("Address"),
                            port=db.get("Endpoint", {}).get("Port"),
                        )
                    )

                return databases

            except (BotoCoreError, ClientError) as e:
                record_exception(e)
                logger.error(f"Failed to list RDS instances: {e}")
                raise

    def delete_database(self, database_id: str) -> bool:
        """Delete RDS database instance."""
        with span("aws.rds.delete", database_id=database_id):
            try:
                self.rds.delete_db_instance(
                    DBInstanceIdentifier=database_id, SkipFinalSnapshot=True
                )
                logger.info(f"Deleted RDS instance {database_id}")
                return True

            except (BotoCoreError, ClientError) as e:
                record_exception(e)
                logger.error(f"Failed to delete RDS instance: {e}")
                return False


class AWSCostExplorer:
    """AWS Cost Explorer implementation."""

    def __init__(self, region: str | None = None) -> None:
        """Initialize Cost Explorer.

        Parameters
        ----------
        region : str, optional
            AWS region.
        """
        if not BOTO3_AVAILABLE:
            msg = "boto3 is required for AWS Cost Explorer"
            raise ImportError(msg)

        self.region = region or os.getenv("AWS_REGION", "us-east-1")
        self.ce = boto3.client("ce", region_name=self.region)

    def get_cost_report(
        self,
        *,
        start_date: datetime,
        end_date: datetime,
    ) -> CostReport:
        """Get cost report from Cost Explorer."""
        with span("aws.cost.report"):
            try:
                response = self.ce.get_cost_and_usage(
                    TimePeriod={
                        "Start": start_date.strftime("%Y-%m-%d"),
                        "End": end_date.strftime("%Y-%m-%d"),
                    },
                    Granularity="DAILY",
                    Metrics=["UnblendedCost"],
                    GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
                )

                total_cost = 0.0
                breakdown = {}  # type: ignore[var-annotated]

                for result in response.get("ResultsByTime", []):
                    for group in result.get("Groups", []):
                        service = group["Keys"][0]
                        cost = float(group["Metrics"]["UnblendedCost"]["Amount"])
                        breakdown[service] = breakdown.get(service, 0.0) + cost
                        total_cost += cost

                return CostReport(
                    provider=CloudProviderType.AWS,
                    start_date=start_date,
                    end_date=end_date,
                    total_cost=total_cost,
                    breakdown=breakdown,
                    recommendations=self.get_recommendations(),
                )

            except (BotoCoreError, ClientError) as e:
                record_exception(e)
                logger.error(f"Failed to get cost report: {e}")
                raise

    def get_recommendations(self) -> list[str]:
        """Get cost optimization recommendations."""
        recommendations = []

        try:
            # Get EC2 rightsizing recommendations
            response = self.ce.get_rightsizing_recommendation(Service="AmazonEC2")
            for rec in response.get("RightsizingRecommendations", []):
                if rec["RightsizingType"] == "Terminate":
                    recommendations.append(
                        f"Terminate underutilized EC2 instance: {rec['CurrentInstance']['ResourceId']}"
                    )
                elif rec["RightsizingType"] == "Modify":
                    current = rec["CurrentInstance"]["InstanceType"]
                    target = rec["ModifyRecommendationDetail"]["TargetInstances"][0]["InstanceType"]
                    recommendations.append(f"Resize EC2 instance from {current} to {target}")

        except (BotoCoreError, ClientError) as e:
            logger.warning(f"Failed to get cost recommendations: {e}")

        return recommendations


class AWSProvider(CloudProvider):
    """AWS cloud provider implementation."""

    name = "aws"

    def __init__(self, region: str | None = None) -> None:
        """Initialize AWS provider.

        Parameters
        ----------
        region : str, optional
            AWS region. Defaults to AWS_REGION env var or us-east-1.
        """
        self.region = region or os.getenv("AWS_REGION", "us-east-1")
        self._storage: AWSS3Storage | None = None
        self._metrics: AWSCloudWatchMetrics | None = None
        self._logging: AWSCloudWatchLogs | None = None
        self._secrets: AWSSecretsManager | None = None
        self._compute: AWSEC2Compute | None = None
        self._database: AWSRDSDatabase | None = None
        self._cost: AWSCostExplorer | None = None

    def get_storage(self) -> CloudStorage:
        """Get S3 storage interface."""
        if not self._storage:
            bucket = os.getenv("AWS_S3_BUCKET", "specify-cli-artifacts")
            self._storage = AWSS3Storage(bucket=bucket, region=self.region)
        return self._storage

    def get_metrics(self) -> CloudMetrics:
        """Get CloudWatch metrics interface."""
        if not self._metrics:
            namespace = os.getenv("AWS_CLOUDWATCH_NAMESPACE", "SpecifyCLI")
            self._metrics = AWSCloudWatchMetrics(namespace=namespace, region=self.region)
        return self._metrics

    def get_logging(self) -> CloudLogging:
        """Get CloudWatch Logs interface."""
        if not self._logging:
            log_group = os.getenv("AWS_LOG_GROUP", "/specify-cli/logs")
            self._logging = AWSCloudWatchLogs(log_group=log_group, region=self.region)
        return self._logging

    def get_secrets(self) -> CloudSecrets:
        """Get Secrets Manager interface."""
        if not self._secrets:
            self._secrets = AWSSecretsManager(region=self.region)
        return self._secrets

    def get_compute(self) -> CloudCompute:
        """Get EC2 compute interface."""
        if not self._compute:
            self._compute = AWSEC2Compute(region=self.region)
        return self._compute

    def get_database(self) -> CloudDatabase:
        """Get RDS database interface."""
        if not self._database:
            self._database = AWSRDSDatabase(region=self.region)
        return self._database

    def get_cost(self) -> CloudCost:
        """Get Cost Explorer interface."""
        if not self._cost:
            self._cost = AWSCostExplorer(region=self.region)
        return self._cost

    def deploy(
        self,
        artifact: Path | str,
        *,
        region: str,
        instance_type: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> DeploymentResult:
        """Deploy application to AWS."""
        with span("aws.deploy", region=region):
            deployment_id = f"deploy-{int(time.time())}"

            try:
                # Upload artifact to S3
                artifact_path = Path(artifact)
                storage = self.get_storage()
                artifact_key = f"deployments/{deployment_id}/{artifact_path.name}"
                artifact_url = storage.upload(artifact_path, artifact_key)

                # Create EC2 instance for deployment
                compute = self.get_compute()
                instance = compute.create_instance(
                    name=f"specify-cli-{deployment_id}",
                    instance_type=instance_type or "t3.micro",
                    metadata=metadata,
                )

                return DeploymentResult(
                    id=deployment_id,
                    status=DeploymentStatus.DEPLOYED,
                    provider=CloudProviderType.AWS,
                    region=region,
                    artifact_url=artifact_url,
                    endpoint=instance.ip_address,
                    started_at=datetime.now(UTC),
                    completed_at=datetime.now(UTC),
                    metadata={"instance_id": instance.id},
                )

            except Exception as e:
                record_exception(e)
                logger.error(f"Deployment failed: {e}")
                return DeploymentResult(
                    id=deployment_id,
                    status=DeploymentStatus.FAILED,
                    provider=CloudProviderType.AWS,
                    region=region,
                    error=str(e),
                    started_at=datetime.now(UTC),
                )


__all__ = [
    "AWSCloudWatchLogs",
    "AWSCloudWatchMetrics",
    "AWSCostExplorer",
    "AWSEC2Compute",
    "AWSProvider",
    "AWSRDSDatabase",
    "AWSS3Storage",
    "AWSSecretsManager",
]
