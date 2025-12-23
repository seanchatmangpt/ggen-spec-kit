# specify pm

Process mining and workflow analysis for understanding execution patterns and bottlenecks.

## Usage

```bash
specify pm [SUBCOMMAND] [OPTIONS]
```

## Description

The `pm` command provides process mining capabilities using pm4py library:
- Analyze event logs and execution traces
- Discover process models from actual behavior
- Detect bottlenecks and inefficiencies
- Compare defined vs. actual processes
- Generate insights from workflow data

## Subcommands

### discover

Discover process model from event log.

```bash
specify pm discover LOG_FILE [OPTIONS]
```

Automatically discovers the process model from traces:

**Options:**
- `--algorithm` - Discovery algorithm (inductive, heuristic, alpha)
- `--output` - Output format (bpmn, petri, dot, json)
- `--threshold` - Minimum occurrence threshold (default: 0.1)

**Example:**
```bash
specify pm discover traces.xes --algorithm inductive --output model.bpmn

✓ Discovered process model
  Activities: 8
  Variants: 12
  Traces: 1,450
  Execution patterns identified
```

### analyze

Analyze process characteristics from log.

```bash
specify pm analyze LOG_FILE [OPTIONS]
```

Shows statistics and metrics:

```bash
specify pm analyze traces.xes

Process Analysis Results:

Activities:
  Process Data: 1,450 occurrences (avg: 2.3s)
  Validate Data: 1,449 occurrences (avg: 1.1s)
  Transform Data: 1,448 occurrences (avg: 4.7s)  ← BOTTLENECK
  Save Results: 1,447 occurrences (avg: 0.8s)

Process Statistics:
  Total traces: 630
  Variants: 12
  Avg case duration: 8.9 seconds
  Min duration: 5.2s
  Max duration: 45.3s

Performance:
  Throughput: 70.7 cases/hour
  Utilization: 85%
```

### bottleneck

Identify bottlenecks in process.

```bash
specify pm bottleneck LOG_FILE [OPTIONS]
```

Highlights slowest activities and decision points:

```bash
specify pm bottleneck traces.xes

Top Bottlenecks:

1. Transform Data
   Duration: 4.7 seconds (avg)
   Variance: High (0.8-12s range)
   Impact: 52% of total case time
   Recommendation: Parallelize or optimize

2. Validate Data → Transform Data transition
   Wait time: 0.3s average
   Impact: Handoff delay
   Recommendation: Pipeline execution

3. Rework loops
   5% of cases loop back to validation
   Recommendation: Improve upstream validation
```

### conformance

Check if execution matches defined process.

```bash
specify pm conformance LOG_FILE PROCESS_MODEL [OPTIONS]
```

Compares actual behavior against specification:

```bash
specify pm conformance traces.xes expected-model.bpmn

Conformance Analysis:

Activities:
  ✓ Process Data: Expected, occurring as planned
  ✓ Validate Data: Expected, occurring as planned
  ⚠ Transform Data: Extra handling (not in model)
  ✗ Manual Review: Unexpected activity (5% of traces)

Sequences:
  ✓ Data Flow 1: 85% conformant
  ⚠ Data Flow 2: 95% conformant (occasional variations)
  ✗ Data Flow 3: 45% conformant (significant deviations)

Overall Conformance: 78%
Recommendation: Update process model to match reality
```

### metrics

Calculate process performance metrics.

```bash
specify pm metrics LOG_FILE [OPTIONS]
```

Comprehensive KPI measurement:

```bash
specify pm metrics traces.xes

Key Performance Indicators:

Cycle Time:
  Average: 8.9 seconds
  Median: 8.1 seconds
  P95: 15.2 seconds
  Trend: ↑ Increasing (degrading)

Throughput:
  Cases per hour: 70.7
  Trend: ↓ Declining

Resource Efficiency:
  Average resources per case: 2.3
  Variance: High (1-5 range)
  Recommendation: Better load balancing

Rework Rate:
  Percentage of cases with rework: 5.1%
  Recommendation: Improve first-pass quality
```

### compare

Compare two process logs or models.

```bash
specify pm compare LOG_FILE1 LOG_FILE2 [OPTIONS]
```

Shows differences in behavior:

```bash
specify pm compare traces-before.xes traces-after.xes

Comparison Results:

Activities (difference):
  Process Data: 1,450 → 1,448 (-0.1%)
  Validate Data: 1,449 → 1,448 (-0.1%)
  Transform Data: 1,448 → 1,200 (-17.1%) ✓ IMPROVED
  Save Results: 1,447 → 1,447 (0%)

Performance:
  Avg case duration: 8.9s → 7.2s (-19%) ✓ IMPROVED
  Throughput: 70.7 → 83.3 cases/hour ✓ IMPROVED

Conclusion: Optimization successful!
```

### export

Export process model in different formats.

```bash
specify pm export LOG_FILE --format FORMAT [OPTIONS]
```

**Formats:**
- `bpmn` - BPMN 2.0 XML (executable)
- `petri` - Petri net format
- `dot` - Graphviz (visualization)
- `json` - JSON structured format
- `svg` - Scalable vector graphic

**Example:**
```bash
specify pm export traces.xes --format bpmn --output process.bpmn
specify pm export traces.xes --format svg --output process.svg

✓ Exported to process.bpmn (BPMN 2.0)
✓ Exported to process.svg (graphical)
```

### variants

Show execution variants (different execution paths).

```bash
specify pm variants LOG_FILE [OPTIONS]
```

Lists different ways process can execute:

```bash
specify pm variants traces.xes --limit 10

Process Variants:

1. Variant (85% of cases):
   Process Data → Validate Data → Transform Data → Save Results
   Avg duration: 8.1 seconds

2. Variant (10% of cases):
   Process Data → Validate Data → [FIX ERRORS] → Validate Data → Transform Data → Save
   Avg duration: 12.5 seconds

3. Variant (4% of cases):
   Process Data → Validate Data → Manual Review → Transform Data → Save
   Avg duration: 18.3 seconds

4. Variant (1% of cases):
   Process Data → [SKIP VALIDATION] → Transform Data → [REWORK] → Validate → Save
   Avg duration: 15.7 seconds
```

## Examples

### Analyzing Actual Workflow

```bash
# Discover model from traces
specify pm discover workflow-log.xes --output discovered-model.bpmn

# Analyze current performance
specify pm analyze workflow-log.xes

# Find bottlenecks
specify pm bottleneck workflow-log.xes

# Export visualization
specify pm export workflow-log.xes --format svg --output workflow.svg
```

### Comparing Before/After

```bash
# Log before optimization
specify pm metrics traces-v1.xes > before.txt

# Make improvements...
# Collect new logs...

# Log after optimization
specify pm metrics traces-v2.xes > after.txt

# Compare
specify pm compare traces-v1.xes traces-v2.xes
# Shows improvement metrics
```

### Compliance Verification

```bash
# Check if real process matches defined process
specify pm conformance actual-traces.xes defined-process.bpmn

# If conformance low, understand why
specify pm variants actual-traces.xes
# Shows what actually happened

# Update process model if needed
specify pm discover actual-traces.xes --output updated-model.bpmn
```

## Integration with Workflows

### With SpiffWorkflow

```bash
# Export executed workflow
specify spiff export-log workflow.bpmn --output workflow-log.xes

# Analyze
specify pm analyze workflow-log.xes

# Discover optimized variant
specify pm discover workflow-log.xes --output optimized.bpmn

# Use optimized variant
specify spiff update-workflow optimized.bpmn
```

### With ggen

```bash
# Define process as part of RDF spec
specify ggen sync

# Monitor actual execution
specify pm analyze execution-traces.xes

# Compare defined vs. actual
specify pm conformance traces.xes expected-model.bpmn

# If gaps found, update RDF spec
vim ontology/process-specs.ttl
specify ggen sync
```

## Performance Recommendations

Based on analysis output, common improvements:

| Finding | Action |
|---------|--------|
| Bottleneck activity | Optimize/parallelize/automate |
| High variance in duration | Add checks/validation upstream |
| Rework loops | Improve quality/automation |
| Long wait times | Reduce batch sizes, pipeline |
| Non-conformance | Update model or fix process |

## See Also

- [spiff.md](./spiff.md) - Workflow execution (generates event logs)
- `/docs/guides/process-mining/` - How-to guides
- `/docs/reference/pm-metrics.md` - Metric definitions
