# View and Analyze Execution Traces

Learn how to use Jaeger UI to visualize and analyze OpenTelemetry execution traces from ggen spec-kit.

## Overview

Execution traces show the complete timeline of what happens when you run a command. Each operation creates a "span" (a named execution block), and spans are organized hierarchically to show nesting.

**Example trace:**
```
specify ggen sync
└─ [2.3 seconds total]
   ├─ normalize [0.2s] - SHACL validation
   ├─ extract [0.5s] - SPARQL queries
   ├─ emit [1.5s] - Template rendering (SLOWEST)
   ├─ canonicalize [0.05s] - Format output
   └─ receipt [0.05s] - Create proof
```

## Prerequisites

1. **OTEL Enabled** - Traces must be exported to Jaeger
2. **Jaeger Running** - Can use Docker Compose
3. **Command Executed** - At least one command run with OTEL enabled

## Setup: Run Jaeger Locally

### Option 1: Docker Compose

```bash
# Create docker-compose.yml in project root
cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "6831:6831/udp"
      - "16686:16686"
    environment:
      COLLECTOR_ZIPKIN_HOST_PORT: ":9411"
EOF

# Start Jaeger
docker-compose up -d jaeger

# Verify running
curl http://localhost:16686/api/services
# Should return: {"data":["specify-cli"],"total":1}
```

### Option 2: Standalone

```bash
# Download and run directly
docker run -d \
  --name jaeger \
  -p 6831:6831/udp \
  -p 16686:16686 \
  jaegertracing/all-in-one:latest

# Verify
curl http://localhost:16686/api/health
```

## Enable Trace Export

Set environment variables before running commands:

```bash
export OTEL_EXPORTER_JAEGER_ENDPOINT=http://localhost:14250
export OTEL_EXPORTER_JAEGER_AGENT_HOST=localhost
export OTEL_EXPORTER_JAEGER_AGENT_PORT=6831

# Now run a command to generate traces
specify ggen sync
```

**For Prometheus metrics:**
```bash
export OTEL_EXPORTER_PROMETHEUS_PORT=8000

# Metrics available at http://localhost:8000/metrics
```

## Open Jaeger UI

Navigate to: **http://localhost:16686**

You'll see the Jaeger UI with three main sections:
- **Service** - Select which service to trace (should see "specify-cli")
- **Operation** - Select operation to analyze
- **Search** - Filter by time range, tags, duration

## Finding Traces

### Method 1: By Service and Operation

1. Click "Service" dropdown → Select **"specify-cli"**
2. Click "Operation" dropdown → Select **"ggen_sync"** (or other operation)
3. Click **"Find Traces"**

Expected result: List of all ggen_sync executions with duration

### Method 2: By Time Range

1. Set time range (e.g., "Last 1 hour")
2. Click "Find Traces"

Shows all operations within that period

### Method 3: By Tags/Filters

```
Service: specify-cli
Tags: status=success  (or error)

Find Traces
```

## Understanding Trace View

When you click a trace, you see:

### Trace Timeline (Left Panel)

Shows the execution timeline:

```
ggen_sync [2.3ms] ✓
├─ normalize [200μs]
├─ extract [500μs]
├─ emit [1.5ms]   ← Click to expand
│  ├─ render_command.tera [800μs]
│  ├─ render_test.tera [700μs]
│  └─ render_docs.tera [0μs]
├─ canonicalize [50μs]
└─ receipt [50μs]
```

**Interpreting:**
- **[ms]** = duration
- **✓** = success
- **✗** = error/exception
- Indentation shows nesting

### Span Details (Right Panel)

Click any span to see details:

```
Span: normalize
Service: specify-cli
Duration: 200 microseconds
Start time: 2025-12-23 14:30:00.000123
Status: OK

Tags:
  rdf_file: ontology/cli-commands.ttl
  constraint_count: 45
  validation_result: passed

Logs:
  14:30:00.000 Validating against SHACL shapes
  14:30:00.185 Constraint sk:CommandShape passed
```

## Common Trace Patterns

### Pattern: Long Operation

**Problem:** One span takes much longer than expected

**Example:**
```
emit [1.5s]  ← Should be ~200ms
└─ render_command.tera [1.4s] ← Real bottleneck
```

**Action:**
- Optimize template rendering
- Check if parallelizable
- Profile actual template

### Pattern: Timeout

**Problem:** Operation takes longer than expected

**Indicates:**
- Slow external service (database, API)
- Network latency
- Optimization opportunity

**Example:**
```
ggen_sync [15s]  ← Should be ~2s
├─ normalize [0.2s] ✓
├─ extract [14s]  ← Bottleneck!
│  └─ sparql_query [13.9s]
```

### Pattern: Error/Exception

**Problem:** Span failed

**Indicated by:** ✗ mark on span

**Example:**
```
ggen_sync [1.5s] ✗ ERROR
├─ normalize [0.2s] ✓
├─ extract [0.5s] ✓
├─ emit [0.8s] ✗ ERROR
│  └─ render_command.tera [0.7s] ✓
│  └─ undefined_variable error
└─ receipt [0s] (skipped due to error)
```

**To view error:**
1. Click the failed span
2. Look for "Logs" section with error details
3. Check "Tags" section for error messages

## Trace Analysis Techniques

### 1. Find the Slowest Operations

**Goal:** Identify optimization targets

**Steps:**
1. List all traces: Click "Find Traces"
2. Sort by duration (descending)
3. Click slowest trace
4. Expand each span to find bottleneck
5. Note the slowest span name

**Example:**
```
Sorted traces (slowest first):
- ggen_sync: 12.3 seconds  ← Anomaly!
- ggen_sync: 2.1 seconds
- ggen_sync: 2.0 seconds
- ...

Click slowest: emit span took 10 seconds (usually 200ms)
```

### 2. Compare Execution Variants

**Goal:** Understand what makes some executions fast/slow

**Steps:**
1. Run same operation multiple times
2. View traces for each run
3. Compare span durations
4. Note differences

**Example:**
```
Run 1: emit = 200ms (normal)
  └─ render_command.tera = 150ms
  └─ render_test.tera = 50ms

Run 2: emit = 2,100ms (10x slower!)
  └─ render_command.tera = 2,050ms
  └─ render_test.tera = 50ms

Conclusion: render_command.tera is sometimes slow
```

### 3. Check Error Patterns

**Goal:** Understand failure modes

**Steps:**
1. Filter by: `status=error`
2. Group by operation type
3. Look for patterns
4. Check error messages in logs

**Example:**
```
Errors found:
- SHACL validation: 5 failures
  └─ All: "sk:description missing"
  └─ Fix: Add descriptions to RDF

- SPARQL query timeout: 2 failures
  └─ All: extract operation
  └─ Fix: Optimize query or increase timeout
```

### 4. Monitor Performance Degradation

**Goal:** Track if performance is getting worse

**Steps:**
1. Run command periodically (daily)
2. Record average duration
3. Plot trend
4. Alert if degrading >20%

**Example:**
```
Day 1: 2.1 seconds average
Day 2: 2.3 seconds (↑ 10%)
Day 3: 2.5 seconds (↑ 19%)
Day 4: 3.2 seconds (↑ 52%) ⚠ ALERT!

Investigation needed
```

## Advanced Features

### Custom Time Range

```
Click date/time range → Select custom dates
Example: 2025-12-20 00:00 to 2025-12-23 23:59
```

### Tag-Based Filtering

Common tags to filter by:

```
status=success
status=error

rdf_file=ontology/cli-commands.ttl

user=alice
environment=production
version=1.2

error=true
error_type=SHACL_VALIDATION
```

Example query:
```
Service: specify-cli
Operation: ggen_sync
Tags: status=error AND rdf_file=ontology/cli-commands.ttl

Find Traces
```

### Trace Comparison

View two traces side-by-side:

1. Open first trace
2. Copy trace ID from URL
3. Open second trace
4. Use "Compare" button (if available)

### Span Context

Hover over span to see:
- **Span ID** - Unique identifier
- **Parent Span ID** - Parent span identifier
- **Start time** - Absolute timestamp
- **Duration** - How long it took

Click span to see all details and logs.

## Interpreting Metrics

### Duration Breakdown

```
Total: 2.3 seconds (100%)
├─ normalize: 0.2s (9%)
├─ extract: 0.5s (22%)
├─ emit: 1.5s (65%) ← 2/3 of time!
└─ canonicalize: 0.1s (4%)
```

**Analysis:** emit is bottleneck, focus optimization there

### Success Rate

```
Total traces: 100
Successful: 95 (95%)
Failed: 5 (5%)

Error breakdown:
├─ SHACL validation: 2 (40%)
├─ SPARQL timeout: 2 (40%)
└─ Template error: 1 (20%)
```

## Exporting Data

### Export Trace Data

1. Open trace
2. Click "JSON" or similar export option
3. Save for analysis in external tools

### Export Metrics

```bash
# Get metrics from Prometheus
curl http://localhost:9090/api/v1/query?query=ggen_sync_duration_ms
```

## Troubleshooting

### No traces appearing

**Check:**
1. Is Jaeger running? `curl http://localhost:16686`
2. Is OTEL endpoint correct?
   ```bash
   echo $OTEL_EXPORTER_JAEGER_ENDPOINT
   # Should be: http://localhost:14250
   ```
3. Did you run a command? `specify ggen sync`
4. Wait 2-3 seconds for export, then refresh browser

**Fix:**
```bash
# Restart Jaeger
docker-compose down
docker-compose up -d jaeger

# Verify connection
curl http://localhost:16686/api/services

# Run command and check again
specify ggen sync
curl http://localhost:16686/api/services
# Should now show: {"data":["specify-cli"]}
```

### Traces incomplete

**Problem:** Missing expected spans

**Causes:**
- OTEL SDK not enabled
- Sampling set to 0 (disabled)
- Export batching delay

**Check:**
```bash
export OTEL_TRACES_SAMPLER=always_on
specify ggen sync

# Check sampling in OTEL environment
echo $OTEL_TRACES_SAMPLER
```

### Performance overhead too high

**Problem:** Traces slow down execution

**Solutions:**
1. Sample less frequently:
   ```bash
   export OTEL_TRACES_SAMPLER=probability
   export OTEL_TRACES_SAMPLER_ARG=0.1  # 10% sampling
   ```

2. Disable console export:
   ```bash
   unset OTEL_EXPORTER_CONSOLE_ENABLED
   ```

3. Increase batch size:
   ```bash
   export OTEL_BSP_MAX_QUEUE_SIZE=4096
   ```

## See Also

- `opentelemetry-design.md` (explanation) - Why OTEL, design rationale
- `/docs/guides/observability/setup-otel.md` - Setting up OTEL
- `/docs/reference/telemetry-api.md` - Instrumentation API
- [Jaeger official docs](https://www.jaegertracing.io/docs/) - Complete Jaeger reference
