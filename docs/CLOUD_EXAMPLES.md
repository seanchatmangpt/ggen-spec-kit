# Multi-Cloud Examples

Practical examples for using Specify CLI's multi-cloud support.

## Table of Contents

- [Basic Operations](#basic-operations)
- [Multi-Cloud Scenarios](#multi-cloud-scenarios)
- [Integration Examples](#integration-examples)
- [Production Deployments](#production-deployments)

## Basic Operations

### Example 1: Upload Build Artifact to AWS S3

```bash
# Build your application
uv build

# Upload to S3
specify cloud upload dist/myapp-1.0.0-py3-none-any.whl \
  --provider aws \
  --key releases/v1.0.0/myapp-1.0.0-py3-none-any.whl
```

**Expected Output:**
```
Uploading to AWS

✓ Uploaded dist/myapp-1.0.0-py3-none-any.whl to s3://specify-cli-artifacts/releases/v1.0.0/myapp-1.0.0-py3-none-any.whl

URL: s3://specify-cli-artifacts/releases/v1.0.0/myapp-1.0.0-py3-none-any.whl
Key: releases/v1.0.0/myapp-1.0.0-py3-none-any.whl
```

### Example 2: Deploy to Single Cloud

```bash
# Deploy to AWS
specify cloud deploy myapp.tar.gz \
  --providers aws \
  --regions us-east-1 \
  --instance-type t3.micro
```

**Expected Output:**
```
Multi-Cloud Deployment

Artifact: myapp.tar.gz
Providers: aws
Regions: us-east-1

Provider  Status        Region      Endpoint
AWS       ✓ Deployed    us-east-1   52.70.123.45

Success Rate: 100.0%
✓ All deployments successful
```

### Example 3: Cost Comparison

```bash
# Compare costs for last 7 days
specify cloud costs --days 7
```

**Expected Output:**
```
Cloud Cost Analysis

Period: 2024-01-20 to 2024-01-27 (7 days)

Provider  Total Cost  Currency  Top Service
AWS       $45.23      USD       EC2
GCP       $38.90      USD       Compute Engine
AZURE     $52.10      USD       Virtual Machines

Cheapest Provider: GCP

Recommendations:
  • [aws] Terminate underutilized EC2 instance: i-1234567890abcdef0
  • [gcp] Enable GCP Recommender API for cost optimization suggestions
  • [azure] Enable Azure Advisor for cost optimization recommendations
  • Consider migrating more workloads to gcp for cost savings
```

## Multi-Cloud Scenarios

### Scenario 1: High-Availability Multi-Cloud Deployment

Deploy the same application to AWS, GCP, and Azure for maximum availability.

```bash
# Initialize all providers
specify cloud init aws gcp azure

# Deploy to all three clouds
specify cloud deploy myapp.tar.gz \
  --providers aws,gcp,azure \
  --regions us-east-1,us-central1,eastus \
  --instance-type small
```

**Python API:**
```python
from specify_cli.cloud.multicloud import MultiCloudDeployer

# Initialize deployer
deployer = MultiCloudDeployer(providers=["aws", "gcp", "azure"])

# Deploy
results = deployer.deploy(
    "myapp.tar.gz",
    regions=["us-east-1", "us-central1", "eastus"],
    instance_type="small"
)

# Check results
successful = deployer.get_successful_deployments(results)
print(f"Deployed to {len(successful)}/{len(results)} clouds")

for result in successful:
    print(f"{result.provider.value}: {result.endpoint}")
```

**Expected Output:**
```
Deployed to 3/3 clouds
aws: 52.70.123.45
gcp: 35.188.45.67
azure: 40.121.89.23
```

### Scenario 2: Artifact Replication with Failover

Store artifacts in multiple clouds with automatic failover.

```python
from specify_cli.cloud.multicloud import UnifiedCloudStorage

# Primary on AWS, backup on GCP and Azure
storage = UnifiedCloudStorage(
    primary="aws",
    backup=["gcp", "azure"]
)

# Upload with automatic replication
url = storage.upload(
    "myapp-1.0.0.tar.gz",
    "releases/v1.0.0/myapp-1.0.0.tar.gz",
    replicate=True
)

print(f"Uploaded to: {url}")
print("Replicated to backup providers")

# Download with automatic failover
# If AWS fails, automatically tries GCP, then Azure
local_path = storage.download(
    "releases/v1.0.0/myapp-1.0.0.tar.gz",
    "local/myapp-1.0.0.tar.gz"
)

print(f"Downloaded to: {local_path}")
```

### Scenario 3: Cost-Optimized Deployment

Analyze costs and deploy to the cheapest provider.

```python
from specify_cli.cloud.multicloud import CloudCostAnalyzer
from datetime import datetime, timedelta

# Analyze costs
analyzer = CloudCostAnalyzer()

end = datetime.now()
start = end - timedelta(days=30)

reports = analyzer.compare_costs(start_date=start, end_date=end)

# Find cheapest provider
cheapest = analyzer.get_cheapest_provider(reports)
print(f"Cheapest provider: {cheapest}")

# Deploy to cheapest provider
from specify_cli.cloud.multicloud import MultiCloudDeployer

deployer = MultiCloudDeployer(providers=[cheapest])
results = deployer.deploy(
    "myapp.tar.gz",
    regions=["us-east-1"],  # Adjust based on provider
)

print(f"Deployed to {cheapest}: {results[0].endpoint}")
```

## Integration Examples

### Example 4: CI/CD Integration

Integrate multi-cloud deployment into your CI/CD pipeline.

**GitHub Actions:**
```yaml
name: Multi-Cloud Deploy

on:
  push:
    tags:
      - 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh

      - name: Install specify-cli with cloud support
        run: uv tool install specify-cli --with cloud

      - name: Configure AWS credentials
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          AWS_REGION: us-east-1
        run: echo "AWS configured"

      - name: Configure GCP credentials
        env:
          GCP_PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
          GOOGLE_APPLICATION_CREDENTIALS: ${{ secrets.GCP_CREDENTIALS }}
        run: |
          echo "$GOOGLE_APPLICATION_CREDENTIALS" > gcp-key.json
          export GOOGLE_APPLICATION_CREDENTIALS=gcp-key.json

      - name: Build application
        run: uv build

      - name: Deploy to multiple clouds
        run: |
          specify cloud deploy dist/*.whl \
            --providers aws,gcp \
            --regions us-east-1,us-central1
```

### Example 5: Metrics Export Integration

Export OpenTelemetry metrics to multiple cloud monitoring systems.

```python
from specify_cli.cloud.multicloud import CloudMetricsAggregator
from opentelemetry import metrics

# Initialize aggregator
aggregator = CloudMetricsAggregator(providers=["aws", "gcp", "azure"])

# Your application metrics
operation_counter = 0
operation_duration = 1.234

# Export to all cloud providers
results = aggregator.export_metrics(
    "operations.count",
    operation_counter,
    unit="count",
    dimensions={"service": "myapp", "environment": "production"}
)

results.update(aggregator.export_metrics(
    "operations.duration",
    operation_duration,
    unit="seconds",
    dimensions={"service": "myapp", "environment": "production"}
))

# Check which providers succeeded
for provider, success in results.items():
    status = "✓" if success else "✗"
    print(f"{status} {provider.upper()}")
```

### Example 6: Secret Management Across Clouds

Store and retrieve secrets from multiple cloud providers.

```python
from specify_cli.cloud.aws import AWSProvider
from specify_cli.cloud.gcp import GCPProvider
from specify_cli.cloud.azure import AzureProvider

# Initialize providers
aws = AWSProvider()
gcp = GCPProvider(project_id="my-project")
azure = AzureProvider(subscription_id="my-subscription")

# Store secret in AWS Secrets Manager
aws_secrets = aws.get_secrets()
aws_version = aws_secrets.put_secret(
    "prod/api-key",
    "sk-1234567890abcdef",
    metadata={"environment": "production"}
)
print(f"Stored in AWS: version {aws_version}")

# Store same secret in GCP Secret Manager
gcp_secrets = gcp.get_secrets()
gcp_version = gcp_secrets.put_secret(
    "prod-api-key",
    "sk-1234567890abcdef",
    metadata={"environment": "production"}
)
print(f"Stored in GCP: version {gcp_version}")

# Retrieve from AWS
aws_secret = aws_secrets.get_secret("prod/api-key")
print(f"Retrieved from AWS: {aws_secret.value[:8]}...")

# Retrieve from GCP
gcp_secret = gcp_secrets.get_secret("prod-api-key")
print(f"Retrieved from GCP: {gcp_secret.value[:8]}...")
```

## Production Deployments

### Scenario 4: Blue-Green Deployment Across Clouds

Deploy new version alongside old, then switch traffic.

```python
from specify_cli.cloud.multicloud import MultiCloudDeployer

# Deploy blue (current) version
blue_deployer = MultiCloudDeployer(providers=["aws", "gcp"])
blue_results = blue_deployer.deploy(
    "myapp-1.0.0.tar.gz",
    regions=["us-east-1", "us-central1"],
    metadata={"version": "1.0.0", "deployment": "blue"}
)

# Deploy green (new) version
green_deployer = MultiCloudDeployer(providers=["aws", "gcp"])
green_results = green_deployer.deploy(
    "myapp-1.1.0.tar.gz",
    regions=["us-east-1", "us-central1"],
    metadata={"version": "1.1.0", "deployment": "green"}
)

# Test green deployment
print("Testing green deployment...")
# ... run health checks ...

# Switch traffic to green
print("Switching traffic to green...")
# ... update load balancer / DNS ...

# Cleanup blue deployment
print("Cleaning up blue deployment...")
# ... terminate old instances ...
```

### Scenario 5: Disaster Recovery Setup

Set up cross-region, cross-cloud disaster recovery.

```python
from specify_cli.cloud.multicloud import UnifiedCloudStorage
from specify_cli.cloud.aws import AWSProvider
from specify_cli.cloud.gcp import GCPProvider

# Primary: AWS us-east-1
# DR: AWS us-west-2, GCP us-central1

# Initialize storage with replication
storage = UnifiedCloudStorage(
    primary="aws",  # us-east-1
    backup=["aws", "gcp"]  # us-west-2, us-central1
)

# Backup critical data with replication
data_files = [
    "database-backup-2024-01-27.sql.gz",
    "application-state.json",
    "configuration.toml"
]

for file in data_files:
    storage.upload(
        file,
        f"backups/{file}",
        replicate=True
    )
    print(f"Backed up {file} to all regions")

# Test DR failover
print("Testing disaster recovery...")

# Simulate primary region failure
# Download will automatically failover to backup
for file in data_files:
    local_path = storage.download(
        f"backups/{file}",
        f"dr-restore/{file}"
    )
    print(f"Restored {file} from backup")
```

### Scenario 6: Multi-Tenant Deployment

Deploy separate instances for each tenant across clouds.

```python
from specify_cli.cloud.multicloud import MultiCloudDeployer

tenants = [
    {"name": "acme", "provider": "aws", "region": "us-east-1"},
    {"name": "globex", "provider": "gcp", "region": "us-central1"},
    {"name": "initech", "provider": "azure", "region": "eastus"},
]

deployments = {}

for tenant in tenants:
    print(f"Deploying for tenant: {tenant['name']}")

    deployer = MultiCloudDeployer(providers=[tenant["provider"]])

    results = deployer.deploy(
        "myapp.tar.gz",
        regions=[tenant["region"]],
        metadata={
            "tenant": tenant["name"],
            "environment": "production"
        }
    )

    deployments[tenant["name"]] = {
        "provider": tenant["provider"],
        "region": tenant["region"],
        "endpoint": results[0].endpoint,
        "status": results[0].status.value
    }

# Print deployment summary
print("\nDeployment Summary:")
for tenant_name, info in deployments.items():
    print(f"{tenant_name}: {info['provider'].upper()} {info['region']} -> {info['endpoint']}")
```

### Scenario 7: Automated Cost Optimization

Automatically migrate workloads to cheapest provider.

```python
from specify_cli.cloud.multicloud import CloudCostAnalyzer, MultiCloudDeployer
from datetime import datetime, timedelta

# Analyze costs weekly
analyzer = CloudCostAnalyzer()

end = datetime.now()
start = end - timedelta(days=7)

reports = analyzer.compare_costs(start_date=start, end_date=end)

# Find cheapest provider
cheapest = analyzer.get_cheapest_provider(reports)
print(f"Cheapest provider this week: {cheapest}")

# Get recommendations
recommendations = analyzer.get_optimization_recommendations(reports)
for rec in recommendations:
    print(f"  • {rec}")

# Migrate non-critical workloads to cheapest provider
non_critical_workloads = ["batch-processing", "analytics", "reporting"]

for workload in non_critical_workloads:
    print(f"Migrating {workload} to {cheapest}...")

    deployer = MultiCloudDeployer(providers=[cheapest])
    results = deployer.deploy(
        f"{workload}.tar.gz",
        regions=["us-east-1"],  # Adjust based on provider
        metadata={"workload": workload, "priority": "non-critical"}
    )

    if results[0].status.value == "deployed":
        print(f"  ✓ {workload} migrated successfully")
    else:
        print(f"  ✗ {workload} migration failed: {results[0].error}")
```

## Advanced Patterns

### Pattern 1: Circuit Breaker for Cloud Operations

Prevent cascading failures with circuit breaker pattern.

```python
from specify_cli.cloud.aws import AWSProvider

class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise

    def on_success(self):
        self.failure_count = 0
        self.state = "CLOSED"

    def on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

# Usage
circuit_breaker = CircuitBreaker()
provider = AWSProvider()
storage = provider.get_storage()

try:
    url = circuit_breaker.call(
        storage.upload,
        "myfile.tar.gz",
        "uploads/myfile.tar.gz"
    )
    print(f"Uploaded: {url}")
except Exception as e:
    print(f"Upload failed: {e}")
```

### Pattern 2: Retry with Exponential Backoff

Handle transient failures with intelligent retry logic.

```python
import time
from functools import wraps

def retry_with_backoff(max_attempts=3, base_delay=1, max_delay=60):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise

                    delay = min(base_delay * (2 ** attempt), max_delay)
                    print(f"Attempt {attempt + 1} failed: {e}")
                    print(f"Retrying in {delay}s...")
                    time.sleep(delay)
        return wrapper
    return decorator

# Usage
@retry_with_backoff(max_attempts=3, base_delay=2, max_delay=30)
def upload_artifact(storage, local_path, remote_key):
    return storage.upload(local_path, remote_key)

# This will retry up to 3 times with exponential backoff
url = upload_artifact(storage, "myfile.tar.gz", "uploads/myfile.tar.gz")
```

---

For more information:
- See [MULTI_CLOUD_GUIDE.md](MULTI_CLOUD_GUIDE.md) for complete documentation
- See [CLOUD_ARCHITECTURE.md](CLOUD_ARCHITECTURE.md) for architecture details
- See API reference for Python API documentation
