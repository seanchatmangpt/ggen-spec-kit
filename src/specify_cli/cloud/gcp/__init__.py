"""
specify_cli.cloud.gcp - GCP Cloud Integration
============================================

Comprehensive Google Cloud Platform integration for Specify CLI.

This module provides full GCP integration including:

* **Cloud Storage**: Object storage and versioning
* **Cloud Logging**: Centralized logging
* **Cloud Run**: Serverless container execution
* **Cloud SQL**: Managed database services
* **Cloud IAM**: Identity and access management
* **Secret Manager**: Secure credential storage
* **Compute Engine**: Virtual machine compute
* **Cloud Monitoring**: Metrics and monitoring

Architecture
-----------
All GCP operations use google-cloud SDK with comprehensive error handling,
retry logic, and OpenTelemetry instrumentation.

Examples
--------
    # Cloud Storage artifact storage
    from specify_cli.cloud.gcp import GCPCloudStorage
    storage = GCPCloudStorage(bucket="my-artifacts")
    storage.upload("build.tar.gz", "releases/v1.0.0/build.tar.gz")

    # Cloud Monitoring metrics
    from specify_cli.cloud.gcp import GCPCloudMonitoring
    metrics = GCPCloudMonitoring(project_id="my-project")
    metrics.put_metric("operations.count", 1, dimensions={"operation": "sync"})

    # Secret Manager
    from specify_cli.cloud.gcp import GCPSecretManager
    secrets = GCPSecretManager(project_id="my-project")
    api_key = secrets.get_secret("prod-api-key")

See Also
--------
- :mod:`specify_cli.cloud.base` : Base cloud abstractions
- :mod:`specify_cli.cloud.multicloud` : Multi-cloud orchestration
"""

from __future__ import annotations

from specify_cli.cloud.gcp.provider import GCPProvider

__all__ = [
    "GCPProvider",
]
