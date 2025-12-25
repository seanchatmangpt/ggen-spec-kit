# Multi-Cloud Architecture

Technical architecture documentation for Specify CLI's multi-cloud integration.

## Table of Contents

- [Overview](#overview)
- [Architecture Layers](#architecture-layers)
- [Provider Abstraction](#provider-abstraction)
- [Multi-Cloud Orchestration](#multi-cloud-orchestration)
- [Data Flow](#data-flow)
- [Error Handling](#error-handling)
- [Telemetry](#telemetry)
- [Security Model](#security-model)

## Overview

The multi-cloud integration follows Specify CLI's three-tier architecture:

```
┌─────────────────────────────────────────────────────┐
│  Commands Layer (commands/cloud.py)                 │
│  • Typer CLI interface                              │
│  • Argument parsing and validation                  │
│  • Rich output formatting                           │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│  Operations Layer (ops/cloud.py)                    │
│  • Pure business logic                              │
│  • Provider initialization                          │
│  • Deployment orchestration                         │
│  • Cost analysis                                    │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│  Cloud Package (cloud/)                             │
│  ├─ base.py: Protocol interfaces                    │
│  ├─ multicloud.py: Unified orchestration            │
│  ├─ aws/: AWS provider implementation               │
│  ├─ gcp/: GCP provider implementation               │
│  └─ azure/: Azure provider implementation           │
└─────────────────────────────────────────────────────┘
```

## Architecture Layers

### 1. Base Abstractions (cloud/base.py)

**Protocol-based design** for duck typing and flexibility:

```python
class CloudStorage(Protocol):
    """Unified storage interface."""
    def upload(self, local_path, remote_key) -> str: ...
    def download(self, remote_key, local_path) -> Path: ...
    def list_objects(self, prefix) -> Iterator[StorageObject]: ...
    def delete(self, remote_key) -> bool: ...
    def get_url(self, remote_key, expires_in) -> str: ...

class CloudMetrics(Protocol):
    """Unified metrics interface."""
    def put_metric(self, name, value, unit, dimensions) -> None: ...
    def get_metrics(self, name, start_time, end_time) -> list[MetricData]: ...

class CloudProvider(ABC):
    """Base provider interface."""
    @abstractmethod
    def get_storage(self) -> CloudStorage: ...
    @abstractmethod
    def get_metrics(self) -> CloudMetrics: ...
    @abstractmethod
    def get_logging(self) -> CloudLogging: ...
    @abstractmethod
    def get_secrets(self) -> CloudSecrets: ...
    @abstractmethod
    def get_compute(self) -> CloudCompute: ...
    @abstractmethod
    def get_database(self) -> CloudDatabase: ...
    @abstractmethod
    def get_cost(self) -> CloudCost: ...
    @abstractmethod
    def deploy(self, artifact, region) -> DeploymentResult: ...
```

**Key Design Principles:**
- **Protocol-based interfaces**: No inheritance required
- **Duck typing**: Any object implementing the protocol works
- **Type-safe**: Full type hints and mypy validation
- **Extensible**: Easy to add new providers

### 2. Provider Implementations

Each cloud provider implements the full CloudProvider interface:

#### AWS Provider (cloud/aws/provider.py)

```python
class AWSProvider(CloudProvider):
    name = "aws"

    def get_storage(self) -> CloudStorage:
        return AWSS3Storage(bucket=..., region=...)

    def get_metrics(self) -> CloudMetrics:
        return AWSCloudWatchMetrics(namespace=..., region=...)

    # ... other methods
```

**AWS Services:**
- Storage: S3 with versioning
- Metrics: CloudWatch
- Logging: CloudWatch Logs
- Secrets: Secrets Manager
- Compute: EC2
- Database: RDS
- Cost: Cost Explorer

#### GCP Provider (cloud/gcp/provider.py)

```python
class GCPProvider(CloudProvider):
    name = "gcp"

    def get_storage(self) -> CloudStorage:
        return GCPCloudStorage(bucket=..., project_id=...)

    def get_metrics(self) -> CloudMetrics:
        return GCPCloudMonitoring(project_id=...)

    # ... other methods
```

**GCP Services:**
- Storage: Cloud Storage
- Metrics: Cloud Monitoring
- Logging: Cloud Logging
- Secrets: Secret Manager
- Compute: Compute Engine
- Database: Cloud SQL
- Cost: BigQuery billing export

#### Azure Provider (cloud/azure/provider.py)

```python
class AzureProvider(CloudProvider):
    name = "azure"

    def get_storage(self) -> CloudStorage:
        return AzureBlobStorage(container=...)

    def get_metrics(self) -> CloudMetrics:
        return AzureApplicationInsights()

    # ... other methods
```

**Azure Services:**
- Storage: Blob Storage
- Metrics: Application Insights
- Logging: Monitor Logs
- Secrets: Key Vault
- Compute: Virtual Machines
- Database: SQL Database
- Cost: Cost Management

### 3. Multi-Cloud Orchestration (cloud/multicloud.py)

**Unified interfaces across providers:**

#### Provider Registry

```python
class ProviderRegistry:
    """Global provider registry."""
    def register(self, name: str, provider: CloudProvider) -> None: ...
    def get(self, name: str) -> CloudProvider | None: ...
    def list_available(self) -> list[str]: ...

# Global instance
_registry = ProviderRegistry()
```

#### Unified Storage

```python
class UnifiedCloudStorage:
    """Storage with automatic failover."""

    def __init__(self, primary: str, backup: list[str]):
        self.primary_provider = get_provider(primary)
        self.backup_providers = [get_provider(b) for b in backup]

    def upload(self, local_path, remote_key, replicate=True):
        # Upload to primary
        url = self.primary_provider.get_storage().upload(...)

        # Replicate to backups
        if replicate:
            for provider in self.backup_providers:
                provider.get_storage().upload(...)

        return url

    def download(self, remote_key, local_path):
        # Try primary, then failover to backups
        try:
            return self.primary_provider.get_storage().download(...)
        except Exception:
            for provider in self.backup_providers:
                try:
                    return provider.get_storage().download(...)
                except Exception:
                    continue
            raise
```

#### Multi-Cloud Deployer

```python
class MultiCloudDeployer:
    """Deploy to multiple clouds simultaneously."""

    def deploy(self, artifact, regions, instance_type):
        results = []

        # Deploy to each provider in parallel
        for provider, region in zip(self.providers, regions):
            result = provider.deploy(
                artifact,
                region=region,
                instance_type=instance_type
            )
            results.append(result)

        return results
```

## Provider Abstraction

### Interface Hierarchy

```
CloudProvider (ABC)
├─ CloudStorage (Protocol)
│  ├─ AWSS3Storage
│  ├─ GCPCloudStorage
│  └─ AzureBlobStorage
├─ CloudMetrics (Protocol)
│  ├─ AWSCloudWatchMetrics
│  ├─ GCPCloudMonitoring
│  └─ AzureApplicationInsights
├─ CloudLogging (Protocol)
│  ├─ AWSCloudWatchLogs
│  ├─ GCPCloudLogging
│  └─ AzureMonitorLogs
├─ CloudSecrets (Protocol)
│  ├─ AWSSecretsManager
│  ├─ GCPSecretManager
│  └─ AzureKeyVault
├─ CloudCompute (Protocol)
│  ├─ AWSEC2Compute
│  ├─ GCPComputeEngine
│  └─ AzureVirtualMachines
├─ CloudDatabase (Protocol)
│  ├─ AWSRDSDatabase
│  ├─ GCPCloudSQL
│  └─ AzureSQLDatabase
└─ CloudCost (Protocol)
   ├─ AWSCostExplorer
   ├─ GCPCostManagement
   └─ AzureCostManagement
```

### Adding New Providers

To add a new cloud provider:

1. **Implement CloudProvider interface:**
```python
class NewCloudProvider(CloudProvider):
    name = "newcloud"

    def get_storage(self) -> CloudStorage:
        return NewCloudStorage(...)

    # ... implement all abstract methods
```

2. **Implement service interfaces:**
```python
class NewCloudStorage:
    def upload(self, local_path, remote_key, metadata=None):
        # Implementation using provider SDK
        ...

    def download(self, remote_key, local_path):
        # Implementation
        ...

    # ... other methods
```

3. **Register provider:**
```python
from specify_cli.cloud.multicloud import register_provider

provider = NewCloudProvider()
register_provider("newcloud", provider)
```

## Multi-Cloud Orchestration

### Deployment Flow

```
User Command
    │
    ▼
┌─────────────────────┐
│ specify cloud deploy│
└──────────┬──────────┘
           │
           ▼
┌──────────────────────────────┐
│ ops.cloud.deploy_multicloud  │
│  • Validate inputs           │
│  • Initialize deployer       │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│ MultiCloudDeployer.deploy    │
│  • Upload artifact            │
│  • Create compute instances   │
│  • Configure networking       │
└──────────┬───────────────────┘
           │
           ▼
    ┌──────┴──────┐
    │             │
    ▼             ▼
AWS Deploy    GCP Deploy    Azure Deploy
    │             │             │
    ▼             ▼             ▼
  Result        Result        Result
    │             │             │
    └─────────┬───┴─────────────┘
              ▼
    ┌──────────────────┐
    │ Aggregate Results│
    └────────┬─────────┘
             ▼
    ┌──────────────────┐
    │ Return to CLI    │
    └──────────────────┘
```

### Storage Replication Flow

```
Upload Request
    │
    ▼
┌──────────────────────────────┐
│ UnifiedCloudStorage.upload   │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│ Primary Provider Upload      │
│  • Upload to S3/GCS/Blob     │
│  • Get URL                   │
└──────────┬───────────────────┘
           │
           ▼
    ┌─────┴─────┐
    │ Replicate?│
    └─────┬─────┘
          │ Yes
          ▼
┌──────────────────────────────┐
│ Backup Provider Uploads      │
│  • Upload to each backup     │
│  • Log results               │
└──────────┬───────────────────┘
           │
           ▼
    ┌─────────────┐
    │ Return URL  │
    └─────────────┘
```

### Cost Analysis Flow

```
Cost Request
    │
    ▼
┌──────────────────────────────┐
│ CloudCostAnalyzer.compare    │
└──────────┬───────────────────┘
           │
           ▼
    ┌──────┴──────┐
    │             │
    ▼             ▼
AWS Cost      GCP Cost      Azure Cost
Explorer      BigQuery      Management
    │             │             │
    ▼             ▼             ▼
  Report        Report        Report
    │             │             │
    └─────────┬───┴─────────────┘
              ▼
    ┌──────────────────┐
    │ Aggregate Reports│
    │  • Total costs   │
    │  • Breakdowns    │
    │  • Recommendations│
    └────────┬─────────┘
             ▼
    ┌──────────────────┐
    │ Find Cheapest    │
    └────────┬─────────┘
             ▼
    ┌──────────────────┐
    │ Return Analysis  │
    └──────────────────┘
```

## Data Flow

### Upload Flow

```
Local File
    │
    ▼
┌────────────────┐
│ Read File Data │
└────────┬───────┘
         │
         ▼
┌────────────────┐
│ Provider SDK   │
│  • boto3 (AWS) │
│  • google-cloud│
│  • azure-sdk   │
└────────┬───────┘
         │
         ▼
┌────────────────┐
│ Cloud Storage  │
│  • S3          │
│  • GCS         │
│  • Blob        │
└────────┬───────┘
         │
         ▼
┌────────────────┐
│ Return URL     │
└────────────────┘
```

### Download Flow with Failover

```
Remote Key
    │
    ▼
┌──────────────────┐
│ Try Primary      │
└────┬─────────────┘
     │
     ▼
┌──────────┐
│ Success? │
└──┬───┬───┘
   │   │ No
   │   ▼
   │ ┌──────────────┐
   │ │ Try Backup 1 │
   │ └──┬───────────┘
   │    │
   │    ▼
   │ ┌──────────┐
   │ │ Success? │
   │ └──┬───┬───┘
   │    │   │ No
   │    │   ▼
   │    │ ┌──────────────┐
   │    │ │ Try Backup 2 │
   │    │ └──┬───────────┘
   │    │    │
   │    │    ▼
   │    │ ┌──────────┐
   │    │ │ Success? │
   │    │ └──┬───┬───┘
   │    │    │   │ No
   │    │    │   ▼
   │    │    │ ┌──────┐
   │    │    │ │ Fail │
   │    │    │ └──────┘
   │    │    │
   │ Yes│ Yes│ Yes
   └────┴────┴──┐
                ▼
         ┌────────────┐
         │ Local File │
         └────────────┘
```

## Error Handling

### Error Hierarchy

```
CloudError (Base)
├─ ProviderNotAvailableError
│  └─ Raised when cloud SDK not installed
├─ ProviderNotInitializedError
│  └─ Raised when provider not registered
├─ CredentialsError
│  └─ Raised when credentials invalid/missing
├─ StorageError
│  ├─ UploadError
│  ├─ DownloadError
│  └─ DeleteError
├─ DeploymentError
│  └─ Raised when deployment fails
└─ CostAnalysisError
   └─ Raised when cost data unavailable
```

### Error Handling Strategy

1. **Graceful Degradation**
```python
try:
    import boto3
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
    logger.warning("boto3 not available - AWS integration disabled")
```

2. **Retry Logic**
```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def upload_with_retry(self, local_path, remote_key):
    return self.s3.upload_file(...)
```

3. **Comprehensive Logging**
```python
try:
    provider.deploy(...)
except Exception as e:
    record_exception(e)  # OTEL
    logger.error(f"Deployment failed: {e}")
    raise
```

## Telemetry

### OpenTelemetry Integration

All cloud operations are fully instrumented:

```python
@span("aws.s3.upload", bucket=self.bucket, key=remote_key)
def upload(self, local_path, remote_key):
    try:
        self.s3.upload_file(...)
        # Success
    except Exception as e:
        record_exception(e)
        raise
```

### Metrics

Exported metrics:
- `cloud.upload.count`: Upload operations
- `cloud.upload.duration`: Upload latency
- `cloud.upload.bytes`: Bytes uploaded
- `cloud.download.count`: Download operations
- `cloud.deploy.count`: Deployments
- `cloud.deploy.duration`: Deployment latency
- `cloud.cost.total`: Total costs

### Traces

Distributed tracing across:
- CLI commands
- Operations layer
- Cloud provider SDKs
- Network requests

### Example Trace

```
specify cloud deploy
├─ ops.cloud.deploy_multicloud
│  ├─ multicloud.deployer.deploy
│  │  ├─ aws.s3.upload
│  │  │  └─ boto3.upload_file
│  │  ├─ aws.ec2.create_instance
│  │  │  └─ boto3.run_instances
│  │  ├─ gcp.storage.upload
│  │  │  └─ google.cloud.upload
│  │  └─ gcp.compute.create_instance
│  │     └─ google.cloud.insert
│  └─ ops.cloud.aggregate_results
└─ commands.cloud.format_output
```

## Security Model

### Credential Management

**Never stored in code:**
- Environment variables
- Cloud provider CLI configuration
- Instance metadata service
- Secret management services

**Encryption:**
- At rest: Cloud provider encryption (SSE, CMEK, Storage Encryption)
- In transit: TLS 1.2+ for all API calls
- Secrets: Dedicated secret management (Secrets Manager, Secret Manager, Key Vault)

### IAM Permissions

**Minimum required permissions:**

**AWS:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket",
        "cloudwatch:PutMetricData",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "ec2:RunInstances",
        "ec2:DescribeInstances"
      ],
      "Resource": "*"
    }
  ]
}
```

**GCP:**
```yaml
roles:
  - roles/storage.objectAdmin
  - roles/monitoring.metricWriter
  - roles/logging.logWriter
  - roles/compute.instanceAdmin.v1
```

**Azure:**
```yaml
roles:
  - Storage Blob Data Contributor
  - Application Insights Component Contributor
  - Virtual Machine Contributor
```

### Audit Logging

All operations logged:
- Who: User/service account
- What: Operation (upload, deploy, etc.)
- When: Timestamp
- Where: Provider, region
- Result: Success/failure

---

For implementation examples, see [CLOUD_EXAMPLES.md](CLOUD_EXAMPLES.md).
For usage guide, see [MULTI_CLOUD_GUIDE.md](MULTI_CLOUD_GUIDE.md).
