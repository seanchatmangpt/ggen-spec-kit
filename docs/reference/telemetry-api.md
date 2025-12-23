# OpenTelemetry API Reference

Complete API reference for OpenTelemetry instrumentation in ggen spec-kit.

## Overview

The telemetry API provides decorators and context managers for instrumenting code with OpenTelemetry tracing and metrics.

**Location:** `src/specify_cli/core/telemetry.py`

## Tracer API

### Decorators

#### `@timed`

Automatically create a span for a function execution.

```python
from specify_cli.core.telemetry import timed

@timed
def my_operation():
    """Operation automatically wrapped in span"""
    # Work here - timing and error handling automatic
    pass

# Usage
my_operation()
# Span "my_operation" created, tracks duration and errors
```

**Parameters:**
- None - uses function name as span name

**Example:**
```python
@timed
def ggen_sync(config: GgenConfig) -> Receipt:
    """Run complete transformation pipeline"""
    # Automatically:
    # - Creates span named "ggen_sync"
    # - Tracks total duration
    # - Records any exceptions
    # - Tags with function attributes
    pass
```

#### `@span(name, **attributes)`

Create a named span with custom attributes.

```python
from specify_cli.core.telemetry import span

@span("custom_operation", operation_type="critical")
def critical_operation():
    """Span with custom name and attributes"""
    pass
```

**Parameters:**
- `name` (str) - Span name
- `**attributes` (dict) - Key-value attributes for span

**Example:**
```python
@span("data_processing",
      data_type="csv",
      version="1.0")
def process_data(path: str):
    # Span includes: name, data_type, version attributes
    pass
```

### Context Managers

#### `with span(name, **attributes):`

Create a span block within function.

```python
from specify_cli.core.telemetry import span

def complex_operation():
    with span("setup", version="1.0"):
        # Setup code - spans named "setup"
        setup_database()

    with span("processing"):
        # Processing code - spans named "processing"
        process_data()

    with span("cleanup"):
        # Cleanup code - spans named "cleanup"
        cleanup_resources()
```

**Parameters:**
- `name` (str) - Span name
- `**attributes` (dict) - Custom attributes

**Example:**
```python
def ggen_sync(config):
    with span("normalize", rdf_file=config.rdf_source):
        result = normalize_rdf(config.rdf_source)

    with span("extract", query_count=5):
        data = extract_sparql_data(result)

    with span("emit", template_count=8):
        output = emit_templates(data)

    return output
```

#### `record_exception(exception, **attributes)`

Record an exception in the current span.

```python
from specify_cli.core.telemetry import record_exception

try:
    operation()
except Exception as e:
    record_exception(e, context="data_validation", severity="high")
    raise
```

#### `add_event(name, **attributes)`

Add event to current span.

```python
from specify_cli.core.telemetry import add_event

def operation():
    add_event("operation_started", priority="high")

    # Work...

    add_event("operation_completed", duration_ms=1234)
```

## Metrics API

### Meters

#### `get_meter(name)`

Get meter instance for custom metrics.

```python
from specify_cli.core.telemetry import get_meter

meter = get_meter(__name__)
# or
meter = get_meter("my.module.name")
```

### Counter

#### `create_counter(name, description, unit)`

Create counter metric (monotonically increasing).

```python
meter = get_meter(__name__)

command_counter = meter.create_counter(
    name="commands.executed",
    description="Total commands executed",
    unit="1"  # dimensionless
)

# Use in code
command_counter.add(1)
command_counter.add(5)  # Increment by 5
```

**Parameters:**
- `name` (str) - Metric name
- `description` (str) - Human readable description
- `unit` (str) - Unit of measurement

### Gauge

#### `create_gauge(name, description, unit, callback)`

Create gauge metric (can increase or decrease).

```python
meter = get_meter(__name__)

memory_usage = meter.create_gauge(
    name="memory.usage_bytes",
    description="Current memory usage",
    unit="By",  # Bytes
    callback=lambda: psutil.Process().memory_info().rss
)
# Gauge automatically updated by callback
```

**Parameters:**
- `name` (str) - Metric name
- `description` (str) - Description
- `unit` (str) - Unit
- `callback` (callable) - Function returning current value

### Histogram

#### `create_histogram(name, description, unit, boundaries)`

Create histogram metric (distribution of values).

```python
meter = get_meter(__name__)

sync_duration = meter.create_histogram(
    name="ggen.sync.duration_ms",
    description="Time to complete ggen sync",
    unit="ms",
    boundaries=[100, 500, 1000, 2000, 5000]
)

# Use in code
start = time.time()
ggen_sync()
duration_ms = (time.time() - start) * 1000
sync_duration.record(duration_ms)
```

**Parameters:**
- `name` (str) - Metric name
- `description` (str) - Description
- `unit` (str) - Unit
- `boundaries` (list[float]) - Histogram buckets

## Attributes

### Standard Attributes

Standard attributes automatically added:

```
service.name: "specify-cli"
service.version: "0.8.2"
telemetry.sdk.name: "opentelemetry"
telemetry.sdk.version: "1.20.0"
```

### Custom Attributes

Add custom attributes to spans:

```python
with span("operation",
          user="alice",
          environment="production",
          version="1.2.3"):
    # Attributes available in UI for filtering
    pass
```

**Best practices:**
- Use lowercase with underscores
- Keep values simple (strings, numbers)
- Don't include sensitive data
- Use semantic names

### Common Attributes

**File operations:**
```python
with span("read_file", file_path=path, file_size=bytes):
    read_data()
```

**Network operations:**
```python
with span("http_request", url=url, method="GET", status_code=200):
    fetch_data()
```

**Database operations:**
```python
with span("database_query", query=sql, rows_affected=5):
    execute_query()
```

**Data transformation:**
```python
with span("transform_data", input_rows=1000, output_rows=950, errors=50):
    transform()
```

## Environment Configuration

### Enable/Disable Telemetry

```bash
# Disable all telemetry (zero overhead)
export OTEL_SDK_DISABLED=true
specify ggen sync

# Enable with console output (development)
export OTEL_EXPORTER_CONSOLE_ENABLED=true
specify ggen sync
# Shows traces in console

# Enable with Jaeger export (production)
export OTEL_EXPORTER_JAEGER_ENDPOINT=http://localhost:14250
specify ggen sync
# Exports to Jaeger for visualization
```

### Configuration Variables

**Jaeger Export:**
```bash
OTEL_EXPORTER_JAEGER_ENDPOINT=http://localhost:14250
OTEL_EXPORTER_JAEGER_AGENT_HOST=localhost
OTEL_EXPORTER_JAEGER_AGENT_PORT=6831
OTEL_EXPORTER_JAEGER_USER=username       # Optional
OTEL_EXPORTER_JAEGER_PASSWORD=password   # Optional
```

**Batch Processing:**
```bash
OTEL_BSP_MAX_QUEUE_SIZE=2048             # Max spans to buffer
OTEL_BSP_SCHEDULE_DELAY_MILLIS=5000      # Flush interval
OTEL_BSP_EXPORT_TIMEOUT_MILLIS=30000     # Export timeout
```

**Sampling:**
```bash
OTEL_TRACES_SAMPLER=always_on            # Always sample
OTEL_TRACES_SAMPLER=always_off           # Never sample
OTEL_TRACES_SAMPLER=parentbased_always_on # Child follows parent
```

## Code Examples

### Example 1: Instrumenting a Function

```python
from specify_cli.core.telemetry import timed, span

@timed
def process_file(path: str) -> dict:
    """Process file and return results"""

    with span("validate", file_path=path):
        validate_file(path)

    with span("read", file_path=path):
        data = read_file(path)

    with span("transform", row_count=len(data)):
        result = transform_data(data)

    return result
```

**Result in Jaeger:**
```
process_file [15ms]
├─ validate [2ms]
│  └─ file_path: /data/file.csv
├─ read [8ms]
│  └─ file_path: /data/file.csv
└─ transform [5ms]
   └─ row_count: 1450
```

### Example 2: Error Tracking

```python
from specify_cli.core.telemetry import span, record_exception

def risky_operation():
    with span("operation"):
        try:
            dangerous_code()
        except Exception as e:
            record_exception(e, severity="high", context="dangerous_code")
            raise
```

**Result:**
- Exception recorded with attributes
- Visible in Jaeger as error span
- Can set alerts on error counts

### Example 3: Custom Metrics

```python
from specify_cli.core.telemetry import get_meter

meter = get_meter(__name__)

commands_executed = meter.create_counter(
    "commands.executed",
    description="Total commands executed"
)

success_count = meter.create_counter(
    "commands.success",
    description="Successful commands"
)

def execute_command(cmd):
    commands_executed.add(1)

    try:
        result = cmd.execute()
        success_count.add(1)
        return result
    except Exception:
        # Failed but counters don't count failures
        # Could add separate failure counter
        raise
```

**Metrics visible in Prometheus:**
```
commands_executed_total 145
commands_success_total 142
command_error_rate = 0.021
```

## Best Practices

### DO ✅

- Use `@timed` on public functions
- Add semantic attributes (file names, counts, statuses)
- Create spans for business logic boundaries
- Use context managers for multi-step operations
- Name spans with descriptive verbs

### DON'T ❌

- Don't instrument every line (too noisy)
- Don't include passwords/tokens in attributes
- Don't create thousands of spans per request
- Don't use high-cardinality values (timestamps, IDs)
- Don't instrument hot paths with excessive overhead

## Troubleshooting

### Traces Not Appearing

```bash
# Check if OTEL is enabled
export OTEL_SDK_DISABLED=false

# Check Jaeger endpoint
export OTEL_EXPORTER_JAEGER_ENDPOINT=http://localhost:14250

# Check if Jaeger is running
curl http://localhost:16686/api/services
# Should return list of services

# Enable console export for debugging
export OTEL_EXPORTER_CONSOLE_ENABLED=true
specify ggen sync  # Traces appear in console
```

### High Overhead

If instrumentation slows operations:

```bash
# Check sampling rate
export OTEL_TRACES_SAMPLER=always_off  # No sampling
# Run operation to measure baseline

export OTEL_TRACES_SAMPLER=always_on   # All sampling
# Compare performance

# If high overhead with all sampling, reduce span volume:
# - Remove @timed from frequently-called functions
# - Use span() only for slow operations
# - Increase batch size: OTEL_BSP_MAX_QUEUE_SIZE=4096
```

## See Also

- `opentelemetry-design.md` (explanation) - OTEL design and philosophy
- `/docs/guides/observability/setup-otel.md` - Setup guide
- `/docs/guides/observability/view-traces.md` - Viewing and analyzing traces
- Official OpenTelemetry: https://opentelemetry.io/docs/instrumentation/python/
