# LaTeX-to-PDF Observability Infrastructure

> **Comprehensive OpenTelemetry-based monitoring, metrics, and self-healing for LaTeX compilation**

## Overview

The LaTeX observability infrastructure provides enterprise-grade monitoring with:

- **OpenTelemetry Integration**: Full distributed tracing and metrics
- **10+ Operational Metrics**: Performance, quality, and health tracking
- **Self-Aware Monitoring**: Real-time anomaly detection
- **Self-Healing**: Automatic strategy adjustment based on failure patterns
- **Dashboard Support**: Prometheus export and visualization

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Compilation Pipeline                       │
│                                                              │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │ μ₁ VALIDATE│─▶│ μ₂ COMPILE │─▶│ μ₃ OPTIMIZE│            │
│  └────────────┘  └────────────┘  └────────────┘            │
│         │               │               │                   │
└─────────┼───────────────┼───────────────┼───────────────────┘
          │               │               │
          ▼               ▼               ▼
┌─────────────────────────────────────────────────────────────┐
│                  TelemetryCollector                          │
│  • Metrics aggregation                                       │
│  • OpenTelemetry spans                                       │
│  • Structured logging                                        │
└──────────────────┬───────────────────────────────────────────┘
                   │
          ┌────────┴────────┐
          │                 │
          ▼                 ▼
┌──────────────────┐  ┌──────────────────┐
│ MetricsAnalyzer  │  │ AlertingSystem   │
│ • Anomaly detect │  │ • Threshold check│
│ • Health score   │  │ • Alert gen      │
│ • Trend analysis │  │ • Severity class │
└────────┬─────────┘  └─────────┬────────┘
         │                      │
         ▼                      ▼
┌──────────────────────────────────────────┐
│        SelfHealingSystem                 │
│ • Failure analysis                       │
│ • Strategy recommendation                │
│ • Automatic cache invalidation           │
│ • Fallback activation                    │
└──────────────────────────────────────────┘
```

## Metrics Collected

### Compilation Metrics

| Metric | Type | Description | Unit |
|--------|------|-------------|------|
| `latex.compilation.duration_seconds` | Histogram | Total compilation time | seconds |
| `latex.compilation.attempts_total` | Counter | Number of compilation attempts | count |
| `latex.compilation.success_total` | Counter | Successful compilations | count |
| `latex.compilation.failure_total` | Counter | Failed compilations | count |
| `latex.compilation.stage.duration_seconds` | Histogram | Duration per stage (μ₁-μ₅) | seconds |

**Performance Targets:**
- P50: < 2s
- P95: < 5s
- P99: < 10s
- Max: < 30s

### Quality Metrics

| Metric | Type | Description | Unit |
|--------|------|-------------|------|
| `latex.pdf.size_bytes` | Histogram | Output PDF file size | bytes |
| `latex.pdf.page_count` | Gauge | Number of pages | count |
| `latex.error.count` | Gauge | LaTeX errors in compilation | count |
| `latex.warning.count` | Gauge | LaTeX warnings | count |
| `latex.document.complexity_score` | Gauge | Document complexity (0-1) | ratio |

**Quality Gates:**
- Errors: 0 (strict)
- Warnings: ≤ 10 (acceptable)
- Complexity: ≤ 0.8 (optimal)

### Performance Metrics

| Metric | Type | Description | Unit |
|--------|------|-------------|------|
| `latex.cache.hit_rate` | Gauge | Cache effectiveness | ratio |
| `latex.cache.miss_total` | Counter | Cache misses | count |
| `latex.optimization.effectiveness_ratio` | Gauge | PDF optimization gain | ratio |
| `latex.memory.usage_bytes` | Histogram | Peak memory usage | bytes |
| `latex.cpu.usage_percent` | Gauge | CPU utilization | percent |

**Performance Targets:**
- Cache hit rate: > 50%
- Memory: < 500MB
- CPU: < 80%
- Optimization: > 70% effective

### Health Metrics

| Metric | Type | Description | Unit |
|--------|------|-------------|------|
| `latex.health.error_rate` | Gauge | Failure rate (rolling window) | ratio |
| `latex.health.availability_percent` | Gauge | System availability | percent |
| `latex.strategy.effectiveness_score` | Gauge | Strategy success rate | ratio |
| `latex.strategy.fallback_total` | Counter | Fallback activations | count |

**Health Targets:**
- Error rate: < 5%
- Availability: > 95%
- Health score: > 0.7

## Usage Examples

### Basic Telemetry Collection

```python
from specify_cli.dspy_latex.observability import (
    TelemetryCollector,
    CompilationStage,
)

# Initialize collector
collector = TelemetryCollector()

# Track compilation
with collector.track_compilation("thesis.tex") as ctx:
    # Stage 1: Preprocessing
    ctx.start_stage(CompilationStage.PREPROCESSING)
    # ... preprocessing logic ...
    ctx.end_stage(CompilationStage.PREPROCESSING)

    # Stage 2: LaTeX compilation
    ctx.start_stage(CompilationStage.LATEX_COMPILE)
    # ... compile logic ...
    ctx.end_stage(CompilationStage.LATEX_COMPILE)

    # Record metrics
    ctx.record_metric("pdf.size_bytes", 2048000)
    ctx.record_metric("page_count", 150)
    ctx.record_metric("error_count", 0)
    ctx.record_metric("warning_count", 5)

    # Record success
    ctx.record_success()

# Get summary
summary = collector.get_metrics_summary()
print(f"Success rate: {summary['success_rate']:.1%}")
print(f"Mean duration: {summary['duration_stats']['mean']:.2f}s")
```

### Metrics Analysis and Anomaly Detection

```python
from specify_cli.dspy_latex.observability import (
    MetricsAnalyzer,
    PerformanceThresholds,
)

# Initialize analyzer with custom thresholds
thresholds = PerformanceThresholds(
    max_compilation_duration=20.0,
    max_error_count=0,
    min_cache_hit_rate=0.6,
)

analyzer = MetricsAnalyzer(collector, thresholds=thresholds)

# Detect anomalies
anomalies = analyzer.detect_anomalies()
for anomaly in anomalies:
    if anomaly.is_anomaly:
        print(f"⚠️  Anomaly: {anomaly.metric_name}")
        print(f"   Current: {anomaly.current_value:.2f}")
        print(f"   Expected: [{anomaly.expected_range[0]:.2f}, {anomaly.expected_range[1]:.2f}]")
        print(f"   Confidence: {anomaly.confidence:.1%}")

# Calculate health score
health_score = analyzer.calculate_health_score()
print(f"System health: {health_score:.1%}")

# Analyze trends
trends = analyzer.analyze_performance_trends()
print(f"Duration trend: {trends['duration_trend']}")  # improving/stable/degrading
```

### Alerting System

```python
from specify_cli.dspy_latex.observability import AlertingSystem

# Initialize alerting
alerting = AlertingSystem(analyzer)

# Generate alerts
alerts = alerting.generate_alerts()

# Process alerts by severity
critical_alerts = alerting.get_critical_alerts()
for alert in critical_alerts:
    print(f"🚨 {alert.severity.value.upper()}: {alert.title}")
    print(f"   {alert.message}")
    print(f"   Action: {alert.recommended_action}")

# Export alerts
import json
alerts_json = json.dumps([a.to_dict() for a in alerts], indent=2)
```

### Self-Healing System

```python
from specify_cli.dspy_latex.observability import SelfHealingSystem

# Initialize self-healing
healing = SelfHealingSystem(alerting, analyzer)

# Analyze failures
failure_analysis = healing.analyze_failures()
print(f"Failure rate: {failure_analysis['failure_rate']:.1%}")
print(f"Most common error: {failure_analysis['most_common_error']}")

# Get recommendations
recommendations = healing.recommend_strategy_adjustment()
if recommendations.get("fallback") == "activate":
    print(f"⚡ Activating fallback: {recommendations['reason']}")

# Check if cache should be invalidated
if healing.should_invalidate_cache():
    print("🔄 Cache invalidation recommended")
    # ... invalidate cache ...

# Check if fallback needed
if healing.should_activate_fallback():
    print("🛡️  Fallback mechanism activated")
    # ... activate fallback strategy ...

# Apply self-healing
actions = healing.apply_self_healing()
print(f"Self-healing actions: {len(actions['actions_taken'])}")
```

### Dashboard and Reporting

```python
from specify_cli.dspy_latex.observability import (
    PerformanceDashboard,
    CompilationReport,
)
from pathlib import Path

# Create dashboard
dashboard = PerformanceDashboard(collector, analyzer)

# Export to Prometheus
prometheus_metrics = dashboard.export_prometheus()
Path("metrics.prom").write_text(prometheus_metrics)

# Export to JSON
dashboard_json = dashboard.export_json()
Path("dashboard.json").write_text(dashboard_json)

# Generate comprehensive report
report = analyzer.generate_report()

# Save in multiple formats
report.save(Path("report.json"), format="json")
report.save(Path("report.md"), format="markdown")

# Print report
print(report.to_markdown())
```

### Complete Integration Example

```python
from specify_cli.dspy_latex.observability import (
    TelemetryCollector,
    MetricsAnalyzer,
    AlertingSystem,
    SelfHealingSystem,
    PerformanceDashboard,
    CompilationStage,
)

class LatexCompiler:
    def __init__(self):
        # Initialize observability stack
        self.collector = TelemetryCollector()
        self.analyzer = MetricsAnalyzer(self.collector)
        self.alerting = AlertingSystem(self.analyzer)
        self.healing = SelfHealingSystem(self.alerting)
        self.dashboard = PerformanceDashboard(self.collector, self.analyzer)

    def compile(self, tex_file: str) -> dict:
        """Compile LaTeX with full observability."""

        # Check if self-healing needed
        if self.healing.should_activate_fallback():
            print("Using fallback strategy due to recent failures")
            # ... use fallback ...

        # Track compilation
        with self.collector.track_compilation(tex_file) as ctx:
            try:
                # Stage 1: Validation
                ctx.start_stage(CompilationStage.VALIDATION)
                self._validate_latex(tex_file)
                ctx.end_stage(CompilationStage.VALIDATION)

                # Stage 2: Compilation
                ctx.start_stage(CompilationStage.LATEX_COMPILE)
                pdf_path = self._run_pdflatex(tex_file)
                ctx.end_stage(CompilationStage.LATEX_COMPILE)

                # Stage 3: Optimization
                ctx.start_stage(CompilationStage.OPTIMIZATION)
                optimized_pdf = self._optimize_pdf(pdf_path)
                ctx.end_stage(CompilationStage.OPTIMIZATION)

                # Record metrics
                pdf_size = Path(optimized_pdf).stat().st_size
                ctx.record_metric("pdf.size_bytes", pdf_size)
                ctx.record_success()

                return {"success": True, "pdf": optimized_pdf}

            except Exception as e:
                ctx.record_failure(str(e))
                return {"success": False, "error": str(e)}

    def get_dashboard_data(self) -> dict:
        """Get current dashboard data."""
        return self.dashboard.generate_dashboard_data()

    def generate_report(self) -> str:
        """Generate markdown report."""
        report = self.analyzer.generate_report()
        return report.to_markdown()
```

## Prometheus Integration

### Metrics Endpoint

```python
from flask import Flask, Response
from specify_cli.dspy_latex.observability import TelemetryCollector

app = Flask(__name__)
collector = TelemetryCollector()

@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint."""
    prometheus_data = collector.export_prometheus()
    return Response(prometheus_data, mimetype='text/plain')

if __name__ == '__main__':
    app.run(port=9090)
```

### Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'latex-compiler'
    static_configs:
      - targets: ['localhost:9090']
    metrics_path: '/metrics'
```

### Grafana Dashboard

Query examples for Grafana:

```promql
# P95 compilation duration
histogram_quantile(0.95, rate(latex_compilation_duration_seconds_bucket[5m]))

# Success rate
rate(latex_compilation_success_total[5m])
  / rate(latex_compilation_attempts_total[5m])

# Error rate
rate(latex_compilation_failure_total[5m])

# Cache hit rate
rate(latex_cache_hit_total[5m])
  / (rate(latex_cache_hit_total[5m]) + rate(latex_cache_miss_total[5m]))
```

## OpenTelemetry Integration

### Environment Configuration

```bash
# Enable OpenTelemetry
export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317"
export OTEL_SERVICE_NAME="latex-compiler"
export OTEL_SERVICE_VERSION="1.0.0"
export SPECIFY_OTEL_ENABLED="true"

# Run compilation with tracing
python -m specify_cli.dspy_latex.compiler document.tex
```

### Trace Visualization

Traces include:
- **Compilation span**: Overall compilation operation
- **Stage spans**: Individual μ₁-μ₅ stages
- **Attributes**: document name, compilation ID, metrics
- **Events**: Errors, warnings, state transitions
- **Status**: Success/failure with error details

### Jaeger Integration

```bash
# Start Jaeger
docker run -d --name jaeger \
  -p 16686:16686 \
  -p 4317:4317 \
  jaegertracing/all-in-one:latest

# View traces at http://localhost:16686
```

## Self-Aware Capabilities

### Anomaly Detection

The system uses **statistical z-score analysis** to detect anomalies:

1. **Baseline establishment**: Calculate mean and standard deviation over historical data
2. **Real-time monitoring**: Compare current values against baseline
3. **Threshold detection**: Flag values beyond 3σ (configurable)
4. **Confidence scoring**: Based on deviation magnitude

```python
# Automatic anomaly detection
anomalies = analyzer.detect_anomalies()

# Manual threshold configuration
custom_anomaly = analyzer._detect_statistical_anomalies(
    metric_name="compilation.duration",
    values=[1.2, 1.5, 1.3, 10.5],  # 10.5 is anomaly
    z_threshold=2.0  # More sensitive
)
```

### Health Scoring

Health score (0.0 - 1.0) is calculated from:

- **Success rate** (40% weight): Compilation success rate vs. threshold
- **Performance** (30% weight): P95 duration vs. targets
- **Quality** (30% weight): Error and warning counts

```python
health_score = analyzer.calculate_health_score()

if health_score < 0.5:
    print("🚨 CRITICAL: System health degraded")
elif health_score < 0.7:
    print("⚠️  WARNING: Performance issues detected")
else:
    print("✅ HEALTHY: System operating normally")
```

### Trend Analysis

Tracks performance trends over time:

- **Improving**: Recent performance better than historical baseline (-10% or more)
- **Stable**: Performance within ±10% of baseline
- **Degrading**: Recent performance worse than baseline (+10% or more)

```python
trends = analyzer.analyze_performance_trends()

print(f"Duration: {trends['duration_trend']}")  # improving/stable/degrading
print(f"Errors: {trends['error_trend']}")
print(f"Memory: {trends['memory_trend']}")
```

## Self-Healing Mechanisms

### Cache Invalidation

Automatically invalidates cache when effectiveness drops:

```python
if healing.should_invalidate_cache():
    # Cache hit rate < 50%
    cache.invalidate_all()
    logger.info("Cache invalidated due to low effectiveness")
```

### Fallback Activation

Activates fallback strategies when:
- Failure rate > 5% (configurable)
- Health score < 0.5
- Consecutive failures detected

```python
if healing.should_activate_fallback():
    # Switch to robust compilation mode
    compiler.use_fallback_strategy()
    logger.info("Fallback strategy activated")
```

### Strategy Recommendations

Provides actionable recommendations:

```python
recommendations = healing.recommend_strategy_adjustment()

# Example output:
# {
#   "fallback": "activate",
#   "reason": "High failure rate: 35.0%",
#   "timeout_adjustment": "increase",
#   "timeout_reason": "Frequent timeout errors detected"
# }
```

## Performance Targets

| Metric | Target | Critical |
|--------|--------|----------|
| P50 Duration | < 2s | < 5s |
| P95 Duration | < 5s | < 15s |
| P99 Duration | < 10s | < 30s |
| Success Rate | > 95% | > 90% |
| Error Rate | < 5% | < 10% |
| Cache Hit Rate | > 50% | > 30% |
| Memory Usage | < 500MB | < 1GB |
| Health Score | > 0.7 | > 0.5 |

## Best Practices

### 1. Always Use Context Managers

```python
# ✅ GOOD: Automatic metric collection
with collector.track_compilation("doc.tex") as ctx:
    compile_document()

# ❌ BAD: Manual metric management
metrics = CompilationMetrics()
# ... easy to forget cleanup ...
```

### 2. Record Granular Stage Metrics

```python
# ✅ GOOD: Track each stage
ctx.start_stage(CompilationStage.PREPROCESSING)
preprocess()
ctx.end_stage(CompilationStage.PREPROCESSING)

# ❌ BAD: Only total time
compile_all()  # No stage visibility
```

### 3. Enable OpenTelemetry in Production

```bash
# Production configuration
export OTEL_EXPORTER_OTLP_ENDPOINT="https://otel-collector.prod:4317"
export OTEL_SERVICE_NAME="latex-compiler-prod"
```

### 4. Regular Health Checks

```python
# Add to monitoring cron
def health_check():
    analyzer = MetricsAnalyzer(collector)
    health = analyzer.calculate_health_score()

    if health < 0.7:
        alert_ops_team(health)
```

### 5. Export Metrics Periodically

```python
# Every hour
import schedule

def export_metrics():
    dashboard.save_prometheus_metrics(Path("/var/metrics/latest.prom"))
    dashboard.save_dashboard(Path("/var/dashboards/current.json"))

schedule.every().hour.do(export_metrics)
```

## Troubleshooting

### No Metrics Collected

**Problem**: `get_metrics_summary()` returns `{"status": "no_data"}`

**Solution**:
```python
# Ensure compilations complete successfully
with collector.track_compilation("test.tex") as ctx:
    ctx.record_success()  # ← Must call this
```

### OpenTelemetry Not Working

**Problem**: Spans not appearing in Jaeger/trace backend

**Check**:
```bash
# Verify environment
echo $OTEL_EXPORTER_OTLP_ENDPOINT
echo $SPECIFY_OTEL_ENABLED

# Check collector availability
curl $OTEL_EXPORTER_OTLP_ENDPOINT/healthz

# Enable debug logging
export OTEL_LOG_LEVEL=debug
```

### High Memory Usage

**Problem**: Metrics history growing unbounded

**Solution**:
```python
# Periodic cleanup
if len(collector.metrics_history) > 1000:
    collector.metrics_history = collector.metrics_history[-500:]

# Or clear entirely
collector.clear_history()
```

### Anomaly False Positives

**Problem**: Too many anomaly alerts

**Solution**:
```python
# Increase z-score threshold
anomalies = analyzer._detect_statistical_anomalies(
    "metric_name",
    values,
    z_threshold=4.0  # Less sensitive (default: 3.0)
)

# Or require more historical data
if len(collector.metrics_history) >= 50:
    anomalies = analyzer.detect_anomalies()
```

## API Reference

See module docstrings for complete API documentation:

```python
help(TelemetryCollector)
help(MetricsAnalyzer)
help(AlertingSystem)
help(SelfHealingSystem)
```

## License

MIT License - See LICENSE file for details.
