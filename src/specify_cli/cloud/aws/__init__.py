"""
specify_cli.cloud.aws - AWS Cloud Integration
============================================

Comprehensive AWS cloud services integration for Specify CLI.

This module provides full AWS integration including:

* **S3**: Artifact storage and versioning
* **CloudWatch**: Metrics, logs, and monitoring
* **Lambda**: Serverless function execution
* **RDS**: Managed database services
* **IAM**: Access control and identity management
* **Secrets Manager**: Secure credential storage
* **EC2**: Virtual machine compute
* **Cost Explorer**: Cost tracking and optimization

Architecture
-----------
All AWS operations use boto3 SDK with comprehensive error handling,
retry logic, and OpenTelemetry instrumentation.

Examples
--------
    # S3 artifact storage
    from specify_cli.cloud.aws import AWSS3Storage
    storage = AWSS3Storage(bucket="my-artifacts")
    storage.upload("build.tar.gz", "releases/v1.0.0/build.tar.gz")

    # CloudWatch metrics
    from specify_cli.cloud.aws import AWSCloudWatchMetrics
    metrics = AWSCloudWatchMetrics(namespace="SpecifyCLI")
    metrics.put_metric("operations.count", 1, dimensions={"operation": "sync"})

    # Secrets Manager
    from specify_cli.cloud.aws import AWSSecretsManager
    secrets = AWSSecretsManager()
    api_key = secrets.get_secret("prod/api-key")

See Also
--------
- :mod:`specify_cli.cloud.base` : Base cloud abstractions
- :mod:`specify_cli.cloud.multicloud` : Multi-cloud orchestration
"""

from __future__ import annotations

from specify_cli.cloud.aws.provider import AWSProvider

__all__ = [
    "AWSProvider",
]
