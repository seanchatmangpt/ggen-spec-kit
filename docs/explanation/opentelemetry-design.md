# OpenTelemetry Instrumentation Design

OpenTelemetry (OTEL) is integrated throughout ggen spec-kit to provide comprehensive observability. This document explains why OTEL was chosen, how it's designed into the system, and what problems it solves.

## Why OpenTelemetry?

### The Problem: Black Box Operations

Before OTEL instrumentation, operations were opaque:
- ❌ You don't know what the tool is doing
- ❌ You can't see performance bottlenecks
- ❌ Failures provide no diagnostic information
- ❌ Performance regression goes undetected
- ❌ Multi-step workflows are invisible

### The Solution: Structured Observability

OpenTelemetry provides three observability signals:

| Signal | Purpose | Use Case |
|--------|---------|----------|
| **Traces** | Execution timeline | Debug slow operations, understand workflow |
| **Metrics** | Quantitative measurements | Monitor performance, alerting |
| **Logs** | Structured events | Debugging, audit trails |

ggen spec-kit implements **traces** and **metrics** for complete visibility into operations.

---

## Design Principles

### 1. Zero Overhead Default

OTEL is completely optional - if not configured, there's zero performance impact:

```python
# from src/specify_cli/core/telemetry.py

# If OTEL SDK not installed or disabled, this is a no-op
try:
    from opentelemetry import trace
    TRACER = trace.get_tracer(__name__)
except ImportError:
    # Graceful degradation - no traces, no overhead
    TRACER = NoOpTracer()
```

**Benefit:** Users without OTEL observability requirements pay no cost. Users who need visibility can enable it.

---

### 2. Layered Instrumentation

Instrumentation follows the three-tier architecture:

```
Commands Layer (Thin wrappers)
    ↓ [No instrumentation here - too thin]
    ↓
Operations Layer (Pure business logic)
    ↓ [Heavy instrumentation - business logic spans]
    ↓
Runtime Layer (I/O, subprocess)
    ↓ [Detailed instrumentation - system calls]
```

**Why this structure:**
- Operations layer shows what the program is doing (business logic)
- Runtime layer shows how it's being done (system details)
- Commands layer is omitted (too thin, low value)

---

### 3. Hierarchical Spans

Spans are organized hierarchically, showing execution flow:

```
┌─ Parent Span: "ggen_sync"
│  ├─ Child Span: "normalize_rdf"
│  │  ├─ Child Span: "parse_turtle"
│  │  └─ Child Span: "validate_shacl"
│  ├─ Child Span: "extract_data"
│  │  └─ Child Span: "execute_sparql"
│  ├─ Child Span: "emit_templates"
│  │  └─ Child Span: "render_command.tera"
│  ├─ Child Span: "canonicalize_output"
│  └─ Child Span: "write_receipt"
└─ [Total duration and status visible]
```

This hierarchy makes it easy to:
- See what took the longest
- Identify which step failed
- Understand the workflow
- Spot performance issues

---

### 4. Semantic Context

Every span includes semantic metadata:

```python
# Example from src/specify_cli/ops/ggen_ops.py

with span("ggen_sync", attributes={
    "rdf_file": "ontology/cli-commands.ttl",
    "output_count": 15,
    "transformation_stage": "complete",
    "idempotent": True,
    "errors": 0
}) as span:
    # Work happens here
    pass
```

**Benefits:**
- Easy filtering and searching in trace UI
- Quantitative data about operations
- Automatic correlation with metrics
- Rich context for debugging

---

## Four Instrumentation Levels

### Level 1: Coarse-Grained Traces

For high-level workflow visibility:

```python
@timed
def ggen_sync(self, config: GgenConfig) -> Receipt:
    """Run complete transformation pipeline (5 stages)"""
    # Decorated with @timed - automatically creates span
    # Shows total time, success/failure
```

**What you see:**
- Command completes in 2.3 seconds
- All 15 files generated successfully

---

### Level 2: Fine-Grained Spans

For detailed operation breakdown:

```python
def ggen_sync(self, config: GgenConfig) -> Receipt:
    with span("normalize", {"rdf_file": "cli-commands.ttl"}):
        # μ₁ normalization - 200ms

    with span("extract", {"query_count": 5}):
        # μ₂ extraction - 150ms

    with span("emit", {"template_count": 8}):
        # μ₃ emission - 800ms (slowest step!)
```

**What you see:**
- Emit step is bottleneck (800ms of 2.3s total)
- Easy to optimize

---

### Level 3: Subprocess Instrumentation

For external tool visibility:

```python
# From src/specify_cli/runtime/process.py

with span("subprocess", {
    "command": "python -m black",
    "args": ["src/"],
    "returncode": 0,
    "duration_ms": 450
}):
    result = run_logged(["python", "-m", "black", "src/"])
```

**What you see:**
- Every subprocess call is tracked
- Command, arguments, exit code
- Duration and resource usage

---

### Level 4: System-Level Metrics

For production monitoring:

```python
# Automatic metrics collection
meter = get_meter(__name__)

# Counter: tracks command invocations
command_counter = meter.create_counter(
    "commands.executed",
    description="Total commands executed"
)

# Gauge: tracks current state
files_counter = meter.create_counter(
    "files.generated",
    description="Total files generated in session"
)

# Histogram: tracks durations
duration_histogram = meter.create_histogram(
    "ggen.sync.duration_ms",
    description="Time to complete ggen sync",
    unit="ms"
)
```

---

## Integration Points

### 1. Jaeger Integration

Export traces to Jaeger for visualization:

```bash
# Set environment variables
export OTEL_EXPORTER_JAEGER_ENDPOINT=http://localhost:14250
export OTEL_EXPORTER_JAEGER_AGENT_HOST=localhost
export OTEL_EXPORTER_JAEGER_AGENT_PORT=6831

# Run command - traces automatically exported
specify ggen sync

# View in Jaeger UI: http://localhost:16686
```

Jaeger shows:
- Timeline of all operations
- Span duration bars
- Metadata in each span
- Service dependencies
- Error analysis

---

### 2. Prometheus Integration

Export metrics to Prometheus for alerting:

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'specify-cli'
    static_configs:
      - targets: ['localhost:8000']
```

Prometheus metrics track:
- Commands executed per minute
- Average ggen sync duration
- Error rates
- File generation volume

---

### 3. Environment Configuration

Enable/disable tracing via environment:

```bash
# Disable all tracing (zero overhead)
export OTEL_SDK_DISABLED=true
specify ggen sync

# Enable with Jaeger export
export OTEL_EXPORTER_JAEGER_ENDPOINT=http://localhost:14250
specify ggen sync

# Enable with console output (development)
export OTEL_EXPORTER_CONSOLE_ENABLED=true
specify ggen sync

# Batch size and timeout tuning
export OTEL_BSP_MAX_QUEUE_SIZE=2048
export OTEL_BSP_SCHEDULE_DELAY_MILLIS=5000
```

---

## Observability Patterns

### Pattern 1: Find Slow Operations

In Jaeger UI, find traces with long duration:

```
Service: specify-cli
Operation: ggen_sync
Min Duration: 3s
```

This shows operations taking 3+ seconds. Click through to see:
- Which step took longest
- Which subprocess calls were slow
- Optimization opportunities

---

### Pattern 2: Debug Failures

When a command fails, traces show exactly where:

```
Trace: specify init my-project
├─ parse_arguments: ✓ 10ms
├─ validate_project_name: ✓ 5ms
├─ create_directories: ✗ FAILED (Permission denied)
│  └─ subprocess mkdir /opt/my-project: Permission denied
├─ [rest skipped - earlier step failed]
```

Stack trace is clear: mkdir failed due to permissions.

---

### Pattern 3: Monitor Production

In Prometheus, set up alerts:

```
# Alert if ggen sync takes > 10 seconds
alert: SlowGgenSync
expr: histogram_quantile(0.95, ggen_sync_duration_ms) > 10000

# Alert if error rate > 5%
alert: HighErrorRate
expr: (errors_total / requests_total) > 0.05
```

---

## Architecture Decisions

### Why Not Just Logging?

Traditional logging is:
- ❌ Unstructured (grep-based searching)
- ❌ Scattered (hard to trace execution flow)
- ❌ Verbose (too much text to parse)
- ❌ Not queryable (can't slice/dice data)

Traces are:
- ✅ Structured (standardized schema)
- ✅ Hierarchical (clear execution flow)
- ✅ Sparse (only key events)
- ✅ Queryable (filter by duration, span name, etc.)

---

### Why Not Real-Time Streaming?

You might think: "Why not stream traces in real-time?"

**Reasons for batching:**
1. **Performance** - Batching is faster than per-event export
2. **Network efficiency** - One request for 1,000 traces vs. 1,000 requests
3. **Resource usage** - Batching uses less memory
4. **Reliability** - Batch failures retry as a unit

Ggen uses batching with default:
- Max queue size: 2,048 spans
- Schedule delay: 5 seconds
- Export on shutdown immediately

---

### Why Hierarchical Spans?

Flat logging is hard to follow:

```
[INFO] Starting ggen sync
[INFO] Parsing turtle
[INFO] Validating with SHACL
[DEBUG] Constraint 1 passed
[DEBUG] Constraint 2 passed
[INFO] Parsing turtle complete
[INFO] Extracting data
[DEBUG] Query 1 returned 5 results
[INFO] Extraction complete
```

Hierarchical spans make it clear:

```
ggen_sync [2.3s]
├─ parse_turtle [200ms]
├─ validate_shacl [100ms]
├─ extract_data [150ms]
│  └─ execute_query_1 [45ms]
└─ emit_templates [1.8s]
```

Much easier to understand and debug.

---

## Instrumentation Best Practices

### DO ✅

- Use spans for business logic boundaries
- Include semantic context (file paths, counts, etc.)
- Batch export (don't export per-span)
- Include errors and status in spans

```python
with span("operation", {
    "input_file": path,
    "output_count": count,
    "status": "success"
}) as s:
    # Work here
```

### DON'T ❌

- Don't instrument every line of code (too noisy)
- Don't include sensitive data (passwords, tokens)
- Don't synchronously export (blocks execution)
- Don't create thousands of spans per request

```python
# Bad - too much instrumentation
for item in items:
    with span(f"process_item_{i}"):  # Creates 1000s of spans!
        process(item)

# Good - one span covers loop
with span("process_items", {"count": len(items)}):
    for item in items:
        process(item)
```

---

## See Also

- `/docs/guides/observability/setup-otel.md` - How to configure OTEL
- `/docs/guides/observability/view-traces.md` - How to analyze traces in Jaeger
- `/docs/reference/telemetry-api.md` - OpenTelemetry API reference
- `ggen-pipeline.md` - Explains the operations being traced
- `/docs/guides/operations/run-ggen-sync.md` - Running transformations with OTEL
