# Tutorial 10: Process Mining Workflows

Analyze execution traces and workflow performance using process mining to discover bottlenecks and optimize processes.

**Duration:** 30 minutes
**Prerequisites:** Tutorial 5 (ggen-sync-first-time)
**Difficulty:** Advanced

## Learning Goals

- Discover process models from execution traces
- Analyze performance metrics and bottlenecks
- Compare actual vs. expected process behavior
- Identify optimization opportunities

## Part 1: Capture Execution Traces

### Enable OpenTelemetry Tracing

```bash
# Setup Jaeger (if not running)
docker-compose up -d jaeger

# Enable OTEL export
export OTEL_EXPORTER_JAEGER_ENDPOINT=http://localhost:14250

# Run ggen sync to generate traces
ggen sync

# Export traces for process mining
specify spiff export-log ggen_sync \
  --output workflow-traces.xes \
  --format xes

✓ Exported 47 events to workflow-traces.xes
```

## Part 2: Discover Process Model

### Discover from Traces

```bash
# Analyze traces and discover process model
specify pm discover workflow-traces.xes \
  --algorithm inductive \
  --output discovered-model.bpmn

✓ Discovered process model
  Activities: 6
  Variants: 3
  Traces: 47
  Model saved to: discovered-model.bpmn
```

### Visualize Discovered Model

```bash
# Export as SVG for visualization
specify pm discover workflow-traces.xes \
  --output discovered-model.svg \
  --format svg

✓ Visualization saved to discovered-model.svg
```

**What you see:**
```
[Start] → [Normalize] → [Extract] → [Emit] → [Canonicalize] → [Receipt] → [End]
            ↓                                     ↓
            └─────── Error → Manual Fix ─────────┘
```

## Part 3: Analyze Performance

### Get Performance Statistics

```bash
# Analyze process metrics
specify pm analyze workflow-traces.xes

Process Analysis Results:

Activities:
  normalize: 47 occurrences (200ms avg)
  extract: 47 occurrences (500ms avg)
  emit: 47 occurrences (1500ms avg) ← SLOW!
  canonicalize: 47 occurrences (50ms avg)
  receipt: 47 occurrences (50ms avg)

Process Statistics:
  Total traces: 47
  Variants: 3 (mostly similar)
  Avg case duration: 2.3 seconds
  Min duration: 2.0 seconds
  Max duration: 12.4 seconds ← Outliers

Performance:
  Throughput: 20.4 cases/hour
  Variance: High (some runs 6x slower)
```

## Part 4: Identify Bottlenecks

### Find the Slowest Steps

```bash
# Analyze bottlenecks
specify pm bottleneck workflow-traces.xes

Top Bottlenecks:

1. emit (Template rendering)
   Duration: 1.5 seconds (avg)
   Variance: HIGH (0.8-3.2s range)
   Impact: 65% of total time
   Problem: Some templates slow
   Recommendation: Profile template rendering

2. extract (SPARQL queries)
   Duration: 0.5 seconds (avg)
   Variance: MEDIUM (0.3-0.9s range)
   Impact: 22% of total time
   Problem: Network latency?
   Recommendation: Check SPARQL query performance

3. Rework loop
   Occurrences: 5% of cases (2 out of 47)
   Problem: Some runs have error handling
   Recommendation: Improve error detection
```

## Part 5: Compare Actual vs. Expected

### Define Expected Process

```bash
# Create ideal process model
cat > expected-model.bpmn << 'EOF'
<?xml version="1.0"?>
<bpmn2:definitions>
  <bpmn2:process id="ggen_ideal">
    <bpmn2:startEvent id="start"/>
    <bpmn2:task id="normalize"/>
    <bpmn2:task id="extract"/>
    <bpmn2:task id="emit"/>
    <bpmn2:task id="canonicalize"/>
    <bpmn2:task id="receipt"/>
    <bpmn2:endEvent id="end"/>
    <!-- No errors expected -->
  </bpmn2:process>
</bpmn2:definitions>
EOF
```

### Check Conformance

```bash
# Compare actual behavior against ideal
specify pm conformance workflow-traces.xes expected-model.bpmn

Conformance Analysis:

Activities:
  ✓ normalize: Expected, occurring
  ✓ extract: Expected, occurring
  ✓ emit: Expected, occurring
  ✓ canonicalize: Expected, occurring
  ✓ receipt: Expected, occurring
  ⚠ error_handling: Unexpected (5% of traces)

Sequences:
  Normal flow: 95% conformant
  Error handling: 5% deviations

Overall Conformance: 95%
Status: MOSTLY CONFORMANT
Issue: Occasional error paths not in spec
Recommendation: Update model to include error handling
```

## Part 6: Identify Variants

### See Different Execution Paths

```bash
# Show how process varies
specify pm variants workflow-traces.xes --limit 5

Process Variants:

1. Happy Path (90% of cases):
   normalize → extract → emit → canonicalize → receipt
   Avg duration: 2.1 seconds

2. Slow Emit (8% of cases):
   normalize → extract → [emit SLOW] → canonicalize → receipt
   Avg duration: 5.3 seconds
   Issue: Some templates render slower

3. Error Handling (2% of cases):
   normalize → extract → [error] → [revalidate] → emit → canonicalize → receipt
   Avg duration: 8.2 seconds
   Issue: Rare failures require retry

Recommendation:
  1. Investigate slow emit cases (8%)
  2. Improve error detection to prevent retries (2%)
```

## Part 7: Optimization Insights

### Analyze Results

Based on process mining, you found:

**Quick Wins:**
```
1. Fix slow template rendering
   Impact: 65% of time
   Effort: Medium (profile + optimize)
   Benefit: ~1.5 second improvement

2. Prevent error-handling paths
   Impact: 5% of cases go slow
   Effort: Low (improve validation)
   Benefit: ~0.3 second improvement for 5%

Total potential improvement: 1.8 seconds → 0.5 seconds (78% faster!)
```

## Part 8: Continuous Monitoring

### Setup Continuous Process Mining

```bash
# Script to monitor performance over time
cat > scripts/monitor-ggen.sh << 'EOF'
#!/bin/bash

# Run ggen sync
ggen sync

# Export traces
specify spiff export-log ggen_sync \
  --output "traces/ggen-$(date +%Y-%m-%d-%H-%M-%S).xes"

# Analyze latest
LATEST=$(ls -t traces/*.xes | head -1)

specify pm analyze "$LATEST" > "reports/$(date +%Y-%m-%d).txt"
specify pm bottleneck "$LATEST" >> "reports/$(date +%Y-%m-%d).txt"

echo "✓ Analysis complete"
EOF

# Schedule daily
echo "0 2 * * * /path/to/scripts/monitor-ggen.sh" | crontab -
```

### Track Performance Trends

```bash
# Compare performance over time
ggen sync  # Day 1
specify pm analyze traces-day1.xes | grep "duration"
# Avg: 2.3 seconds

ggen sync  # Day 5 (after optimization)
specify pm analyze traces-day5.xes | grep "duration"
# Avg: 0.8 seconds (65% improvement!)

ggen sync  # Day 10
specify pm analyze traces-day10.xes | grep "duration"
# Avg: 0.8 seconds (stable/optimized)
```

## Part 9: Advanced: Predictive Insights

### Identify Anomalies

```bash
# Find outlier executions
specify pm analyze workflow-traces.xes --anomaly-detection

Anomalies detected (executions > 95th percentile):

1. Trace ID: abc123
   Duration: 12.4 seconds (should be ~2.3s)
   Issue: emit stage took 9.2 seconds (6x slower)
   Cause: Large template with many variables?
   Action: Investigate that template rendering

2. Trace ID: def456
   Duration: 8.1 seconds (should be ~2.3s)
   Issue: Rework loop occurred
   Cause: Initial validation missed errors
   Action: Improve validation accuracy
```

### Predictive Modeling

```bash
# Use process data to predict future performance
specify pm predict workflow-traces.xes

Prediction Model Results:

Next 10 syncs will likely:
  - Average duration: 2.2-2.4 seconds
  - 1-2 will take > 5 seconds (variance)
  - 0-1 will need error handling/retry
  - Confidence: 85%

If you optimize emit rendering:
  - Average duration would be: 0.8-1.0 seconds
  - Error rate would stay same
  - Potential improvement: 65%
```

## Summary

**Process Discovery:** Find actual process from traces
**Performance Analysis:** Identify bottlenecks
**Conformance:** Compare actual vs. expected behavior
**Variants:** Understand execution variation paths
**Optimization:** Use mining insights to improve
**Monitoring:** Track performance over time
**Prediction:** Forecast future behavior

## Key Metrics

| Metric | What It Means | Target |
|--------|---------------|--------|
| Throughput | Cases per hour | 20+ |
| Cycle time | Avg duration | < 2.3s |
| Variance | Min-max range | < 2x |
| Conformance | Matches spec | > 95% |
| Error rate | % needing retry | < 5% |

## See Also

- `/docs/commands/pm.md` - pm command reference
- [spiff.md](../commands/spiff.md) - Workflow execution
- `/docs/guides/workflow/` - Workflow guides
