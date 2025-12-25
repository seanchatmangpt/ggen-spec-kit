# Advanced Observability Guide

Advanced OpenTelemetry instrumentation with metrics, distributed tracing, and anomaly detection for specify-cli.

## Overview

The advanced observability system provides:

- **Performance Metrics**: P50, P95, P99 percentiles for all operations
- **Anomaly Detection**: Statistical analysis to detect performance regressions
- **Distributed Tracing**: Context propagation and trace correlation
- **Dashboards**: HTML dashboards for visualization
- **Baselines**: Performance baseline tracking and validation

## Quick Start

### 1. View Performance Statistics

```bash
# Show all operation statistics
specify observability stats

# Show stats for specific operation
specify observability stats ops.check.all_tools

# Export as JSON
specify observability stats --json
```

### 2. Detect Performance Anomalies

```bash
# Detect anomalies in all operations
specify observability anomalies

# Check specific operation
specify observability anomalies ops.check.all_tools

# Export as JSON
specify observability anomalies --json
```

### 3. Generate Dashboards

```bash
# Generate all dashboards
specify observability dashboards

# Custom output directory
specify observability dashboards -o ./my-reports
```

### 4. Manage Performance Baselines

```bash
# Update baselines from recent metrics
specify observability baselines update

# Save baselines to disk
specify observability baselines save

# Load baselines from disk
specify observability baselines load

# Custom baseline file
specify observability baselines save --path custom-baselines.json
```

### 5. Export Metrics

```bash
# Export all metrics as JSON
specify observability export metrics.json

# Export with timestamp
specify observability export metrics-$(date +%Y%m%d).json
```

## Architecture

### Three-Layer Design

```
┌─────────────────────────────────────┐
│ Commands Layer                       │
│ (specify_cli/commands/observability) │
│ • CLI argument parsing               │
│ • Rich output formatting             │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│ Operations Layer                     │
│ (specify_cli/ops/observability)      │
│ • Pure business logic                │
│ • No side effects                    │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│ Core Layer                           │
│ (specify_cli/core/*)                 │
│ • advanced_observability.py          │
│   - Metrics collection               │
│   - Anomaly detection                │
│   - Statistical analysis             │
│ • observability_dashboards.py        │
│   - Dashboard generation             │
│   - HTML report creation             │
└──────────────────────────────────────┘
```

## Core Features

### 1. Performance Metrics Collection

The system automatically tracks:

- **Execution Time**: Mean, P50, P95, P99 durations
- **Success Rates**: Per-operation success/failure tracking
- **Error Distribution**: Breakdown of error types
- **Resource Usage**: CPU, memory, thread count (optional)

**Usage in Code:**

```python
from specify_cli.core.advanced_observability import track_performance

# Automatic tracking
with track_performance("my_operation"):
    perform_operation()

# With custom attributes
with track_performance("my_operation", user_id="123", feature="export"):
    perform_operation()
```

### 2. Anomaly Detection

Statistical anomaly detection using z-score analysis:

- **Z-Score Threshold**: Configurable via `SPECIFY_ANOMALY_THRESHOLD` (default: 2.0)
- **Baseline Comparison**: Compares current performance against historical baseline
- **Automatic Detection**: Detects anomalies in real-time during operation execution

**How It Works:**

1. System maintains rolling window of performance metrics (default: 1000 samples)
2. Calculates statistical baseline (mean, standard deviation)
3. Compares new measurements against baseline using z-score
4. Flags anomalies when z-score exceeds threshold

**Example:**

```bash
$ specify observability anomalies

Performance Anomalies
┌────────────────────────┬──────────┬──────────┬───────────┬─────────┐
│ Operation              │ Current  │ Baseline │ Deviation │ Z-Score │
├────────────────────────┼──────────┼──────────┼───────────┼─────────┤
│ ops.check.all_tools    │ 2.450s   │ 0.850s   │ +188.2%   │ 3.45    │
│ ops.ggen.sync          │ 5.200s   │ 3.100s   │ +67.7%    │ 2.15    │
└────────────────────────┴──────────┴──────────┴───────────┴─────────┘

⚠ 2 anomalies detected
```

### 3. Dashboard Generation

Generates HTML dashboards with embedded visualizations:

**Dashboard Types:**

1. **CLI Performance Dashboard**: All command execution metrics
2. **ggen Transformation Dashboard**: RDF transformation performance
3. **Test Suite Health Dashboard**: Test execution and coverage
4. **Resource Usage Dashboard**: CPU, memory, I/O metrics

**Dashboard Contents:**

- Summary metrics (total operations, samples, success rates)
- Performance anomaly alerts
- Operation performance table (mean, P50, P95, P99, success rate)
- Time-series visualizations (when available)

**Output Structure:**

```
reports/observability/
├── index.html                 # Dashboard index
├── cli-performance.html       # CLI metrics
├── ggen-transformation.html   # ggen metrics
├── test-suite-health.html     # Test metrics
└── resource-usage.html        # Resource metrics
```

### 4. Performance Baselines

Baselines are used for:

- **Anomaly Detection**: Detecting performance regressions
- **Capacity Planning**: Understanding normal operation ranges
- **Performance Validation**: Ensuring operations meet targets

**Baseline Structure:**

```json
{
  "ops.check.all_tools": {
    "operation": "ops.check.all_tools",
    "mean_duration": 0.850,
    "std_duration": 0.125,
    "p50": 0.820,
    "p95": 1.050,
    "p99": 1.200,
    "sample_count": 1000,
    "min_duration": 0.650,
    "max_duration": 1.400,
    "last_updated": 1735132800.0
  }
}
```

**Update Strategy:**

- Baselines auto-update every 100 samples by default
- Manual updates via `specify observability baselines update`
- Requires minimum 10 samples before creating baseline

## Configuration

### Environment Variables

```bash
# Enable/disable metrics collection
export SPECIFY_METRICS_ENABLED=true

# Performance baseline path
export SPECIFY_BASELINE_PATH=.specify/baselines

# Z-score threshold for anomaly detection
export SPECIFY_ANOMALY_THRESHOLD=2.0

# Metrics window size (samples to keep per operation)
export SPECIFY_METRICS_WINDOW_SIZE=1000
```

### Metrics Export Configuration

**Prometheus Integration (Optional):**

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'specify-cli'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

**Jaeger Integration (Optional):**

```bash
# Enable OTEL export to Jaeger
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
export OTEL_SERVICE_NAME=specify-cli
export SPECIFY_OTEL_ENABLED=true
```

## Advanced Usage

### 1. Custom Performance Tracking

```python
from specify_cli.core.advanced_observability import PerformanceTracker

tracker = PerformanceTracker(
    operation="custom_operation",
    track_resources=True,      # Track CPU/memory
    auto_baseline=True,        # Auto-update baselines
    detect_anomalies=True,     # Enable anomaly detection
    custom_key="value"         # Custom attributes
)

with tracker:
    # Your code here
    perform_custom_operation()

# Access metrics
if tracker.metric:
    print(f"Duration: {tracker.metric.duration_seconds}s")
    print(f"Success: {tracker.metric.success}")
```

### 2. Manual Baseline Management

```python
from specify_cli.core.advanced_observability import (
    save_baselines,
    load_baselines,
    update_all_baselines,
)

# Update all baselines
baselines = update_all_baselines()
print(f"Updated {len(baselines)} baselines")

# Save to custom location
save_baselines(Path("./custom-baselines.json"))

# Load from custom location
load_baselines(Path("./custom-baselines.json"))
```

### 3. Programmatic Access to Statistics

```python
from specify_cli.core.advanced_observability import get_performance_stats, get_all_stats

# Get stats for specific operation
stats = get_performance_stats("ops.check.all_tools")
print(f"Mean: {stats['mean']:.3f}s")
print(f"P95: {stats['p95']:.3f}s")
print(f"Success Rate: {stats['success_rate']*100:.1f}%")

# Get all operations
all_stats = get_all_stats()
for op, metrics in all_stats.items():
    if "error" not in metrics:
        print(f"{op}: {metrics['p95']:.3f}s (P95)")
```

### 4. Critical Path Analysis

```python
from specify_cli.core.advanced_observability import get_critical_path

# Analyze critical path for workflow
operations = [
    "ops.check.all_tools",
    "ops.ggen.sync",
    "ops.tests.run",
]

analysis = get_critical_path(operations)
print(f"Total mean duration: {analysis['total_mean_duration']:.3f}s")
print(f"Total P95 duration: {analysis['total_p95_duration']:.3f}s")
print(f"Bottleneck: {analysis['bottleneck']['operation']}")
```

## Performance Targets

Default performance targets for specify-cli:

| Operation | Target P95 | Target P99 |
|-----------|-----------|-----------|
| Command startup | < 500ms | < 1s |
| Simple operations | < 100ms | < 200ms |
| ggen transformations | < 5s | < 10s |
| Test execution | < 30s | < 60s |

**Memory Usage Target:** < 100MB

## Troubleshooting

### No Metrics Available

**Symptom:** `specify observability stats` shows no data

**Solution:**
- Run some commands first to generate metrics
- Check `SPECIFY_METRICS_ENABLED=true` is set
- Verify operations are using `track_performance()`

### Baselines Not Updating

**Symptom:** Baselines remain stale

**Solution:**
- Need minimum 10 samples before baseline is created
- Baselines auto-update every 100 samples
- Manually run `specify observability baselines update`

### Anomalies Not Detected

**Symptom:** No anomalies shown despite slow performance

**Solution:**
- Check baseline exists for the operation
- Verify `SPECIFY_ANOMALY_THRESHOLD` (lower = more sensitive)
- Ensure sufficient baseline samples (minimum 10)

### Dashboard Generation Fails

**Symptom:** `specify observability dashboards` errors

**Solution:**
- Check numpy is installed (core dependency)
- Verify write permissions for output directory
- Ensure sufficient metrics data available

## Best Practices

### 1. Establish Baselines Early

Run workloads to establish baselines:

```bash
# Run operations multiple times
for i in {1..50}; do
  specify check
  specify ggen sync
done

# Save baselines
specify observability baselines save
```

### 2. Regular Baseline Updates

Update baselines as system evolves:

```bash
# Weekly baseline update
specify observability baselines update
specify observability baselines save
```

### 3. Monitor Anomalies

Set up automated monitoring:

```bash
#!/bin/bash
# check-performance.sh

anomalies=$(specify observability anomalies --json | jq 'length')
if [ "$anomalies" -gt 0 ]; then
  echo "Performance regression detected: $anomalies anomalies"
  specify observability anomalies
  exit 1
fi
```

### 4. Export Metrics Regularly

```bash
# Daily metrics export
specify observability export metrics-$(date +%Y%m%d).json

# Retention: keep last 30 days
find . -name "metrics-*.json" -mtime +30 -delete
```

### 5. Dashboard Reviews

```bash
# Generate dashboards weekly
specify observability dashboards -o ./reports/week-$(date +%U)

# Review for:
# - Performance trends
# - Success rate changes
# - Anomaly patterns
```

## Integration Examples

### CI/CD Performance Gates

```yaml
# .github/workflows/performance.yml
name: Performance Check

on: [push, pull_request]

jobs:
  performance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run tests with tracking
        run: |
          export SPECIFY_METRICS_ENABLED=true
          specify tests run

      - name: Check for anomalies
        run: |
          anomalies=$(specify observability anomalies --json)
          if [ "$(echo $anomalies | jq 'length')" -gt 0 ]; then
            echo "Performance regression detected"
            specify observability anomalies
            exit 1
          fi

      - name: Generate dashboards
        run: specify observability dashboards

      - name: Upload dashboards
        uses: actions/upload-artifact@v3
        with:
          name: observability-dashboards
          path: ./reports/observability/
```

### Performance Regression Testing

```python
import pytest
from specify_cli.core.advanced_observability import detect_anomaly

def test_no_performance_regression():
    """Ensure operations haven't regressed."""
    operations = [
        "ops.check.all_tools",
        "ops.ggen.sync",
        "ops.tests.run",
    ]

    for op in operations:
        stats = get_performance_stats(op)
        if "error" in stats:
            continue

        # Check P95 hasn't increased more than 20%
        baseline = get_baseline(op)
        if baseline:
            increase = (stats["p95"] - baseline.p95) / baseline.p95
            assert increase < 0.20, f"{op} P95 increased {increase*100:.1f}%"
```

## API Reference

See module docstrings for complete API:

- `specify_cli.core.advanced_observability`
- `specify_cli.core.observability_dashboards`
- `specify_cli.ops.observability`
- `specify_cli.commands.observability`

## Further Reading

- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [Statistical Process Control](https://en.wikipedia.org/wiki/Statistical_process_control)
- [Performance Testing Best Practices](https://martinfowler.com/articles/performance-testing.html)
