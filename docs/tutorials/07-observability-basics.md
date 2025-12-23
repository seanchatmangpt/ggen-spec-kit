# Tutorial 7: OpenTelemetry Basics

**Time to complete:** 15-20 minutes
**Prerequisites:** Complete [Tutorial 3: Write Your First RDF Specification](./03-first-rdf-spec.md)
**What you'll learn:** How to add observability to your code using OpenTelemetry

---

## Overview

OpenTelemetry (OTEL) is a standard way to instrument your code so you can observe what it's doing. With OTEL, you can:

- Track how long operations take
- See detailed execution traces
- Measure system performance
- Debug production issues

Spec Kit has built-in OpenTelemetry support!

---

## Step 1: Understand Observability Concepts

Observability means understanding what your code is doing. There are three pillars:

### 1. Traces
Show the complete execution flow:
```
Request received
  ├─ Parse command
  │   └─ 5ms
  ├─ Validate input
  │   └─ 2ms
  ├─ Execute operation
  │   ├─ Database query
  │   │   └─ 150ms
  │   └─ Process result
  │       └─ 10ms
  └─ Return response
      └─ 1ms
```

### 2. Metrics
Quantitative measurements:
- How many requests?
- How many errors?
- What's the response time?

### 3. Logs
Detailed event records:
```
2024-01-15 10:30:45 INFO Starting ggen sync
2024-01-15 10:30:45 DEBUG Loading ontology/cli-commands.ttl
2024-01-15 10:30:46 INFO Validation passed: 12 commands
```

---

## Step 2: Add OTEL Instrumentation to Your Code

Spec Kit provides telemetry utilities. Use the `@timed` decorator:

```python
from specify_cli.core.telemetry import timed

@timed
def hello_operation(name: str = "World") -> str:
    """Generate a greeting message."""
    return f"Hello, {name}! Welcome to Spec Kit."
```

This decorator automatically:
- ✅ Measures execution time
- ✅ Records function name
- ✅ Creates a trace span
- ✅ Records errors if they occur

---

## Step 3: Create Spans for Sub-operations

For more detailed tracing, create spans around operations:

```python
from specify_cli.core.telemetry import span

def hello_operation(name: str = "World") -> str:
    """Generate a greeting message."""

    with span("validate_input", attributes={"name": name}):
        # Validation logic
        if not name:
            raise ValueError("Name cannot be empty")

    with span("generate_greeting", attributes={"name_length": len(name)}):
        # Generation logic
        greeting = f"Hello, {name}!"
        message = f"{greeting} Welcome to Spec Kit."

    return message
```

Spans let you:
- Track specific operations
- Add metadata (attributes)
- Measure timing of each part
- See execution flow in traces

---

## Step 4: Enable OTEL in Your Project

Spec Kit's OTEL is designed for graceful degradation:
- If OTEL is configured, detailed tracing is enabled
- If not configured, everything still works (minimal overhead)

To enable OTEL export:

```bash
# Set environment variables
export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317"
export OTEL_SERVICE_NAME="my-app"
export OTEL_EXPORTER_OTLP_PROTOCOL="grpc"

# Then run your app
specify hello
```

---

## Step 5: View Traces Locally

To see traces on your machine, use Jaeger:

### Option 1: Docker

```bash
# Run Jaeger in Docker
docker run -d \
  -p 16686:16686 \
  -p 4317:4317 \
  jaegertracing/all-in-one:latest
```

Then:
1. Navigate to http://localhost:16686
2. Select your service from the dropdown
3. Click "Find Traces"
4. See your execution traces!

### Option 2: Without Docker

```bash
# Download Jaeger from https://www.jaegertracing.io/download/

# Run it
./jaeger-all-in-one

# Then visit http://localhost:16686
```

---

## Step 6: Add Metrics

Metrics measure quantities over time:

```python
from specify_cli.core.telemetry import meter

# Create a counter
command_executions = meter.create_counter(
    "command.executions",
    description="Number of command executions"
)

# Create a histogram (for measurements)
command_duration = meter.create_histogram(
    "command.duration_ms",
    description="Command execution time in milliseconds"
)

@app.command()
def hello(name: str = typer.Option("World")):
    """Greet the user."""
    start = time.time()

    try:
        message = hello_operation(name)
        command_executions.add(1, {"status": "success"})
    except Exception as e:
        command_executions.add(1, {"status": "error"})
        raise
    finally:
        duration_ms = (time.time() - start) * 1000
        command_duration.record(duration_ms)

    typer.echo(message)
```

---

## Step 7: Add Contextual Logging

Log important events with context:

```python
import logging
from specify_cli.core.telemetry import get_logger

logger = get_logger(__name__)

@timed
def hello_operation(name: str = "World") -> str:
    """Generate a greeting message."""
    logger.info("Generating greeting", extra={"name": name})

    try:
        greeting = f"Hello, {name}!"
        logger.debug("Greeting generated", extra={"greeting": greeting})
        return greeting
    except Exception as e:
        logger.error("Failed to generate greeting", exc_info=True)
        raise
```

---

## Step 8: View Metrics

Metrics can be exported to:

- **Prometheus** - Popular metrics database
- **Grafana** - Visualization dashboard
- **CloudWatch** - AWS monitoring
- **Datadog** - Application monitoring

Example Prometheus setup:

```python
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.metrics import MeterProvider

# Enable Prometheus export
prometheus_reader = PrometheusMetricReader()
meter_provider = MeterProvider(metric_readers=[prometheus_reader])

# Prometheus scrapes metrics from: http://localhost:8000/metrics
```

---

## Step 9: Test Observability in Your Project

Let's verify observability works:

```bash
# Run ggen sync with observability
export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317"
ggen sync

# If Jaeger is running, you should see traces
# Visit http://localhost:16686 to view them
```

---

## Step 10: Common OTEL Patterns

### Pattern 1: Function-Level Tracing

```python
@timed
def some_operation():
    # Entire function is traced
    pass
```

### Pattern 2: Operation-Level Spans

```python
def some_operation():
    with span("sub_operation", attributes={"key": "value"}):
        # This sub-operation is traced
        pass
```

### Pattern 3: Error Tracking

```python
try:
    result = some_operation()
except Exception as e:
    logger.error("Operation failed", exc_info=True)  # Records stack trace
    raise
```

### Pattern 4: Performance Monitoring

```python
@timed
def slow_operation():
    # Timing is automatically recorded
    # Use metrics to track if it's getting slower
    pass
```

---

## Step 11: Observability Best Practices

### ✅ Do

- Instrument critical paths
- Use meaningful attribute names
- Include relevant context in logs
- Record both successes and errors
- Use structured logging (not string formatting)

### ❌ Don't

- Instrument every line (too much noise)
- Log sensitive data (passwords, tokens)
- Use OTEL for synchronous logging (slows things down)
- Create unbounded cardinality (too many unique values)

---

## Next Steps

You've learned:
- ✅ What observability means
- ✅ How to use OpenTelemetry in Spec Kit
- ✅ How to create traces and spans
- ✅ How to export and view observability data
- ✅ Best practices for instrumentation

**Continue with:**
- **[How-to: Setup OpenTelemetry](../guides/observability/setup-otel.md)** - Advanced configuration
- **[How-to: View Traces](../guides/observability/view-traces.md)** - Analyze trace data
- **[Reference: OpenTelemetry Config](../reference/environment-variables.md)** - Configuration options

---

## Summary

OpenTelemetry helps you:
- **See what's happening** in your code
- **Measure performance** to find bottlenecks
- **Debug production issues** with detailed traces
- **Monitor health** with metrics and logs

In Spec Kit, observability is built-in! Your code is automatically instrumented when you use Spec Kit's utilities.

**Congratulations! You've completed the tutorial series.** You now understand:
- ✅ RDF-first specification-driven development
- ✅ How to create projects and write specifications
- ✅ Testing and verification
- ✅ Code generation with ggen
- ✅ Feature prioritization with JTBD
- ✅ Observability with OpenTelemetry

**Next:** Explore the [How-to Guides](../guides/) for practical tasks, or dive into the [Explanations](../explanation/) for deeper understanding!
