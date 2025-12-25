"""
specify_cli.cloud.azure - Azure Cloud Integration
================================================

Comprehensive Microsoft Azure cloud integration for Specify CLI.

This module provides full Azure integration including:

* **Blob Storage**: Object storage and versioning
* **Application Insights**: Telemetry and monitoring
* **Container Instances**: Serverless container execution
* **SQL Database**: Managed database services
* **Key Vault**: Secure secret storage
* **Managed Identity**: Identity and access management
* **Virtual Machines**: Compute resources
* **Cost Management**: Cost tracking and optimization

Architecture
-----------
All Azure operations use azure-sdk-for-python with comprehensive error handling,
retry logic, and OpenTelemetry instrumentation.

Examples
--------
    # Blob Storage artifact storage
    from specify_cli.cloud.azure import AzureBlobStorage
    storage = AzureBlobStorage(container="artifacts")
    storage.upload("build.tar.gz", "releases/v1.0.0/build.tar.gz")

    # Application Insights metrics
    from specify_cli.cloud.azure import AzureApplicationInsights
    metrics = AzureApplicationInsights()
    metrics.put_metric("operations.count", 1, dimensions={"operation": "sync"})

    # Key Vault secrets
    from specify_cli.cloud.azure import AzureKeyVault
    secrets = AzureKeyVault(vault_name="my-vault")
    api_key = secrets.get_secret("prod-api-key")

See Also
--------
- :mod:`specify_cli.cloud.base` : Base cloud abstractions
- :mod:`specify_cli.cloud.multicloud` : Multi-cloud orchestration
"""

from __future__ import annotations

from specify_cli.cloud.azure.provider import AzureProvider

__all__ = [
    "AzureProvider",
]
