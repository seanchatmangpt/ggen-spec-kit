# Multi-Cloud Integration Guide

Comprehensive guide to using Specify CLI's multi-cloud support for AWS, GCP, and Azure.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Cloud Providers](#cloud-providers)
- [Common Operations](#common-operations)
- [Advanced Features](#advanced-features)
- [Configuration](#configuration)
- [Security](#security)
- [Cost Management](#cost-management)
- [Troubleshooting](#troubleshooting)

## Overview

Specify CLI provides comprehensive multi-cloud support with unified abstractions across:

- **AWS** (Amazon Web Services)
- **GCP** (Google Cloud Platform)
- **Azure** (Microsoft Azure)

### Key Features

- **Unified Interface**: Same API across all cloud providers
- **Multi-Cloud Deployment**: Deploy to multiple clouds simultaneously
- **Automatic Failover**: Cross-cloud high availability
- **Cost Optimization**: Compare costs and get recommendations
- **Metrics Export**: Export OpenTelemetry metrics to cloud monitoring
- **Secret Management**: Secure credential storage across clouds
- **Storage Sync**: Keep artifacts synchronized across providers

## Installation

### Install Cloud Dependencies

```bash
# Install all cloud providers
uv sync --group cloud

# Or install specific providers
pip install boto3  # AWS only
pip install google-cloud-storage  # GCP only
pip install azure-storage-blob  # Azure only
```

### Verify Installation

```bash
specify cloud init aws gcp azure
```

## Quick Start

### 1. Configure Credentials

#### AWS
```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_REGION="us-east-1"
```

#### GCP
```bash
export GCP_PROJECT_ID="your-project-id"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
```

#### Azure
```bash
export AZURE_SUBSCRIPTION_ID="your-subscription-id"
export AZURE_STORAGE_ACCOUNT="your-storage-account"
export AZURE_STORAGE_CONNECTION_STRING="your-connection-string"
```

### 2. Initialize Providers

```bash
# Initialize all providers
specify cloud init aws gcp azure

# Initialize with custom region
specify cloud init aws --region us-west-2
```

### 3. Upload Artifacts

```bash
# Upload to AWS S3
specify cloud upload myapp.tar.gz --provider aws

# Upload with custom key
specify cloud upload build.zip \
  --key releases/v1.0.0/build.zip \
  --provider gcp
```

### 4. Deploy to Cloud

```bash
# Deploy to single cloud
specify cloud deploy app.tar.gz --providers aws

# Multi-cloud deployment
specify cloud deploy app.tar.gz \
  --providers aws,gcp,azure \
  --regions us-east-1,us-central1,eastus
```

### 5. Compare Costs

```bash
# Compare costs across all providers
specify cloud costs

# Compare specific providers
specify cloud costs --providers aws,gcp --days 7
```

## Cloud Providers

### AWS (Amazon Web Services)

**Supported Services:**
- **S3**: Object storage and versioning
- **CloudWatch**: Metrics, logs, and monitoring
- **Lambda**: Serverless function execution
- **RDS**: Managed relational databases
- **IAM**: Identity and access management
- **Secrets Manager**: Secure credential storage
- **EC2**: Virtual machine compute
- **Cost Explorer**: Cost tracking and optimization

**Configuration:**
```bash
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_REGION="us-east-1"
export AWS_S3_BUCKET="specify-cli-artifacts"
export AWS_CLOUDWATCH_NAMESPACE="SpecifyCLI"
export AWS_LOG_GROUP="/specify-cli/logs"
```

### GCP (Google Cloud Platform)

**Supported Services:**
- **Cloud Storage**: Object storage and versioning
- **Cloud Logging**: Centralized logging
- **Cloud Run**: Serverless container execution
- **Cloud SQL**: Managed relational databases
- **Cloud IAM**: Identity and access management
- **Secret Manager**: Secure credential storage
- **Compute Engine**: Virtual machine compute
- **Cloud Monitoring**: Metrics and monitoring

**Configuration:**
```bash
export GCP_PROJECT_ID="my-project"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
export GCP_STORAGE_BUCKET="specify-cli-artifacts"
export GCP_LOG_NAME="specify-cli-logs"
export GCP_ZONE="us-central1-a"
```

### Azure (Microsoft Azure)

**Supported Services:**
- **Blob Storage**: Object storage and versioning
- **Application Insights**: Telemetry and monitoring
- **Container Instances**: Serverless container execution
- **SQL Database**: Managed relational databases
- **Key Vault**: Secure secret storage
- **Managed Identity**: Identity and access management
- **Virtual Machines**: Compute resources
- **Cost Management**: Cost tracking and optimization

**Configuration:**
```bash
export AZURE_SUBSCRIPTION_ID="..."
export AZURE_RESOURCE_GROUP="specify-cli"
export AZURE_STORAGE_ACCOUNT="..."
export AZURE_STORAGE_CONNECTION_STRING="..."
export AZURE_STORAGE_CONTAINER="specify-cli-artifacts"
export AZURE_KEY_VAULT_NAME="my-vault"
```

## Common Operations

### Artifact Management

#### Upload Artifacts
```bash
# Upload to default location
specify cloud upload myapp.tar.gz --provider aws

# Upload with metadata
specify cloud upload myapp.tar.gz \
  --key builds/$(date +%Y%m%d)/myapp.tar.gz \
  --provider aws
```

#### Download Artifacts
Use the Python API:
```python
from specify_cli.cloud.multicloud import UnifiedCloudStorage

storage = UnifiedCloudStorage(primary="aws", backup=["gcp"])
storage.download("builds/20240101/myapp.tar.gz", "local/myapp.tar.gz")
```

### Multi-Cloud Deployment

#### Deploy to Multiple Clouds
```bash
# Deploy to all clouds with default regions
specify cloud deploy app.tar.gz --providers aws,gcp,azure

# Deploy with specific regions and instance types
specify cloud deploy app.tar.gz \
  --providers aws,gcp \
  --regions us-east-1,us-central1 \
  --instance-type t3.micro
```

#### Monitor Deployments
```bash
# Get deployment status (JSON output)
specify cloud deploy app.tar.gz \
  --providers aws,gcp,azure \
  --json > deployment.json
```

### Metrics and Logging

#### Export Metrics
```bash
# Export metrics to AWS CloudWatch
specify cloud export-metrics --provider aws

# Export to GCP Cloud Monitoring
specify cloud export-metrics --provider gcp --namespace MyApp
```

#### Query Logs
Use the Python API:
```python
from specify_cli.cloud.aws import AWSProvider
from datetime import datetime, timedelta

provider = AWSProvider()
logging = provider.get_logging()

end = datetime.now()
start = end - timedelta(hours=1)

logs = logging.query_logs(start_time=start, end_time=end)
for log in logs:
    print(f"{log.timestamp}: {log.message}")
```

## Advanced Features

### Cross-Cloud Replication

Automatically replicate artifacts across multiple clouds:

```python
from specify_cli.cloud.multicloud import UnifiedCloudStorage

# Primary on AWS, backup on GCP and Azure
storage = UnifiedCloudStorage(
    primary="aws",
    backup=["gcp", "azure"]
)

# Uploads to all three clouds
storage.upload("app.tar.gz", "releases/v1.0.0/app.tar.gz", replicate=True)
```

### Automatic Failover

Downloads automatically failover to backup providers:

```python
# If AWS fails, automatically tries GCP, then Azure
storage = UnifiedCloudStorage(primary="aws", backup=["gcp", "azure"])
storage.download("releases/v1.0.0/app.tar.gz", "local/app.tar.gz")
```

### Multi-Region Deployment

Deploy to multiple regions across multiple clouds:

```python
from specify_cli.cloud.multicloud import MultiCloudDeployer

deployer = MultiCloudDeployer(providers=["aws", "gcp", "azure"])

results = deployer.deploy(
    "app.tar.gz",
    regions=["us-east-1", "us-central1", "eastus"],
    instance_type="small"
)

# Check success rate
successful = deployer.get_successful_deployments(results)
print(f"Deployed to {len(successful)}/{len(results)} regions")
```

### Cost Optimization

Compare costs and get recommendations:

```python
from specify_cli.cloud.multicloud import CloudCostAnalyzer
from datetime import datetime, timedelta

analyzer = CloudCostAnalyzer()

end = datetime.now()
start = end - timedelta(days=30)

reports = analyzer.compare_costs(start_date=start, end_date=end)

# Find cheapest provider
cheapest = analyzer.get_cheapest_provider(reports)
print(f"Cheapest provider: {cheapest}")

# Get optimization recommendations
recommendations = analyzer.get_optimization_recommendations(reports)
for rec in recommendations:
    print(f"  • {rec}")
```

### Metrics Aggregation

Export metrics to multiple cloud providers:

```python
from specify_cli.cloud.multicloud import CloudMetricsAggregator

aggregator = CloudMetricsAggregator(providers=["aws", "gcp", "azure"])

# Export to all providers
results = aggregator.export_metrics(
    "operations.count",
    42.0,
    dimensions={"operation": "sync"}
)

# Check which succeeded
for provider, success in results.items():
    status = "✓" if success else "✗"
    print(f"{status} {provider}")
```

## Configuration

### Environment Variables

**Common:**
- `SPECIFY_CLOUD_DEFAULT_PROVIDER`: Default cloud provider (aws, gcp, azure)
- `SPECIFY_CLOUD_FAILOVER_ENABLED`: Enable automatic failover (true/false)
- `SPECIFY_CLOUD_REPLICATION_ENABLED`: Enable automatic replication (true/false)

**AWS:**
- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `AWS_REGION`: Default AWS region
- `AWS_S3_BUCKET`: S3 bucket for artifacts
- `AWS_CLOUDWATCH_NAMESPACE`: CloudWatch namespace
- `AWS_LOG_GROUP`: CloudWatch log group

**GCP:**
- `GCP_PROJECT_ID`: GCP project ID
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to service account key
- `GCP_STORAGE_BUCKET`: Cloud Storage bucket
- `GCP_LOG_NAME`: Cloud Logging log name
- `GCP_ZONE`: Compute zone

**Azure:**
- `AZURE_SUBSCRIPTION_ID`: Azure subscription ID
- `AZURE_RESOURCE_GROUP`: Resource group name
- `AZURE_STORAGE_ACCOUNT`: Storage account name
- `AZURE_STORAGE_CONNECTION_STRING`: Storage connection string
- `AZURE_STORAGE_CONTAINER`: Blob container name
- `AZURE_KEY_VAULT_NAME`: Key Vault name

### Configuration File

Create `.specify/cloud.toml`:

```toml
[cloud]
default_provider = "aws"
failover_enabled = true
replication_enabled = true

[cloud.aws]
region = "us-east-1"
s3_bucket = "my-artifacts"
namespace = "SpecifyCLI"

[cloud.gcp]
project_id = "my-project"
storage_bucket = "my-artifacts"
zone = "us-central1-a"

[cloud.azure]
subscription_id = "..."
resource_group = "specify-cli"
storage_container = "artifacts"
```

## Security

### Credential Management

**Never hardcode credentials!** Use one of these methods:

1. **Environment Variables** (recommended for development)
2. **Cloud Provider CLI** (aws configure, gcloud auth, az login)
3. **Instance Metadata** (for cloud VMs)
4. **Secret Management Services** (AWS Secrets Manager, GCP Secret Manager, Azure Key Vault)

### Encryption

All data is encrypted:
- **At Rest**: Using cloud provider encryption (S3 SSE, Cloud Storage CMEK, Azure Storage Encryption)
- **In Transit**: TLS/HTTPS for all API calls
- **Secrets**: Stored in dedicated secret management services

### IAM Best Practices

1. **Use least-privilege IAM roles**
2. **Enable MFA for production accounts**
3. **Rotate credentials regularly**
4. **Use managed identities when possible**
5. **Audit access logs regularly**

## Cost Management

### Monitor Costs

```bash
# View costs for last 30 days
specify cloud costs --days 30

# Compare specific providers
specify cloud costs --providers aws,gcp --days 7

# JSON output for analysis
specify cloud costs --days 30 --json > costs.json
```

### Cost Optimization Tips

1. **Use appropriate instance types**
   - Development: t3.micro (AWS), e2-micro (GCP), B1s (Azure)
   - Production: Match workload requirements

2. **Implement auto-scaling**
   - Scale down during off-hours
   - Use serverless for variable workloads

3. **Clean up unused resources**
   - Delete old artifacts
   - Terminate idle instances
   - Remove unused databases

4. **Use reserved instances for predictable workloads**
   - AWS Reserved Instances
   - GCP Committed Use Discounts
   - Azure Reserved VM Instances

5. **Enable cost allocation tags**
   - Tag resources by project, environment, team
   - Track costs by category

### Example Cost Analysis

```python
from specify_cli.cloud.multicloud import CloudCostAnalyzer
from datetime import datetime, timedelta

analyzer = CloudCostAnalyzer()

end = datetime.now()
start = end - timedelta(days=30)

reports = analyzer.compare_costs(start_date=start, end_date=end)

print("Cost Comparison (30 days):")
for provider, report in reports.items():
    print(f"\n{provider.upper()}:")
    print(f"  Total: ${report.total_cost:.2f} {report.currency}")
    print(f"  Top Services:")
    for service, cost in sorted(report.breakdown.items(), key=lambda x: x[1], reverse=True)[:3]:
        print(f"    - {service}: ${cost:.2f}")
```

## Troubleshooting

### Common Issues

#### 1. Provider Not Available

**Error:** `Provider 'aws' not initialized`

**Solution:**
```bash
# Ensure credentials are configured
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."

# Initialize provider
specify cloud init aws
```

#### 2. Upload Failed

**Error:** `Failed to upload to Cloud Storage: 403 Forbidden`

**Solution:**
- Check IAM permissions
- Verify bucket exists
- Ensure credentials are valid

#### 3. Deployment Failed

**Error:** `Deployment to gcp failed: Project ID not set`

**Solution:**
```bash
export GCP_PROJECT_ID="your-project-id"
specify cloud init gcp
```

### Debug Mode

Enable debug logging:

```bash
export SPECIFY_LOG_LEVEL=DEBUG
specify cloud deploy app.tar.gz --providers aws,gcp
```

### Getting Help

1. **Check logs**: Look for detailed error messages
2. **Verify configuration**: Double-check environment variables
3. **Test connectivity**: Ensure network access to cloud APIs
4. **Review IAM permissions**: Verify required permissions are granted
5. **Consult documentation**: See cloud provider docs for specific issues

## Next Steps

- See [CLOUD_ARCHITECTURE.md](CLOUD_ARCHITECTURE.md) for architecture details
- See [CLOUD_EXAMPLES.md](CLOUD_EXAMPLES.md) for more usage examples
- See [API Reference](api/cloud.md) for Python API documentation

---

**Note:** Cloud services incur costs. Always monitor your usage and set up billing alerts to avoid unexpected charges.
