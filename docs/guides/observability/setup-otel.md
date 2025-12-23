# How-to: Setup OpenTelemetry

**Goal:** Configure tracing and metrics collection
**Time:** 20-25 minutes | **Level:** Intermediate

## Enable OTEL

Set environment variables:

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317"
export OTEL_SERVICE_NAME="specify-cli"
export OTEL_EXPORTER_OTLP_PROTOCOL="grpc"
```

## Use in Code

Instrument your operations:

```python
from specify_cli.core.telemetry import timed, span, get_logger

logger = get_logger(__name__)

@timed
def my_operation(arg: str) -> str:
    logger.info("Starting operation", extra={"arg": arg})

    with span("validate", attributes={"arg_len": len(arg)}):
        if not arg:
            logger.error("Validation failed")
            raise ValueError("Empty argument")

    with span("process", attributes={"arg": arg}):
        result = f"Result: {arg}"

    logger.info("Operation complete", extra={"result": result})
    return result
```

## Jaeger for Local Development

### Docker Setup

```bash
docker run -d \
  -p 16686:16686 \
  -p 4317:4317 \
  jaegertracing/all-in-one:latest
```

### View Traces

1. Navigate to http://localhost:16686
2. Select service from dropdown
3. Click "Find Traces"
4. View execution timeline

### Metrics

Decorate functions:

```python
from specify_cli.core.telemetry import meter

counter = meter.create_counter("operation.count")
histogram = meter.create_histogram("operation.duration_ms")

@timed
def operation():
    counter.add(1)
    # timing recorded automatically
```

## Production

Export to:
- **Datadog:** Set OTEL_EXPORTER
- **AWS CloudWatch:** Use AWS exporter
- **New Relic:** Use New Relic exporter
- **Prometheus:** Use Prometheus receiver

## Best Practices

✅ Instrument critical paths
✅ Add meaningful context
✅ Use structured logging
✅ Track errors
✅ Monitor performance

See: `specify_cli/core/telemetry.py`
