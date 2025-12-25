"""
specify_cli.cloud - Multi-Cloud Infrastructure Integration
==========================================================

Comprehensive multi-cloud support for AWS, GCP, and Azure with unified abstractions.

This package provides:

* **Cloud Storage**: Unified artifact storage across S3, Cloud Storage, Blob Storage
* **Metrics & Logging**: Cloud-native observability integration
* **Secrets Management**: Secure credential handling
* **Compute**: Serverless and VM-based execution
* **Database**: Managed database integration
* **Cost Management**: Multi-cloud cost tracking and optimization
* **Deployment**: Cross-cloud deployment automation
* **Failover**: Multi-region and cross-cloud high availability

Architecture
-----------
Each cloud provider implements a common interface while exposing provider-specific
features. The multicloud module provides abstraction and orchestration.

Examples
--------
    # AWS S3 artifact storage
    from specify_cli.cloud.aws import S3ArtifactStorage
    storage = S3ArtifactStorage(bucket="my-artifacts")
    storage.upload("artifact.tar.gz", "builds/v1.0.0/artifact.tar.gz")

    # Multi-cloud deployment
    from specify_cli.cloud.multicloud import MultiCloudDeployer
    deployer = MultiCloudDeployer(providers=["aws", "gcp", "azure"])
    deployer.deploy(artifact="app.tar.gz", regions=["us-east-1", "us-central1", "eastus"])

    # Unified metrics export
    from specify_cli.cloud.multicloud import CloudMetricsExporter
    exporter = CloudMetricsExporter()
    exporter.export_to_cloud("aws", namespace="specify-cli")

See Also
--------
- :mod:`specify_cli.cloud.aws` : AWS integrations
- :mod:`specify_cli.cloud.gcp` : GCP integrations
- :mod:`specify_cli.cloud.azure` : Azure integrations
- :mod:`specify_cli.cloud.multicloud` : Unified multi-cloud interface
"""

from __future__ import annotations

__version__ = "0.1.0"

__all__ = [
    "__version__",
]
