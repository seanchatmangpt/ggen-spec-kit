# 38. Observable Execution

★★

*You can't improve what you can't observe. Observable execution instruments capabilities with telemetry—traces, metrics, logs—enabling understanding, debugging, and optimization. This completes the verification story: not just testing what should work, but observing what actually happens.*

---

## The Observability Imperative

A capability that works is good. A capability you can observe working is better.

Tests verify that capabilities work correctly under test conditions. Observability reveals how they work in production conditions—with real data, real users, real scale, real complexity.

Observable execution means:
- **Traces**: Follow a request through the system, step by step
- **Metrics**: Measure performance, errors, usage patterns
- **Logs**: Record significant events with context
- **Events**: Structured notifications of state changes

With observability, you can answer:
- Why did this fail for that user?
- How long does validation take on large files?
- Which commands are used most often?
- Where is the bottleneck in transformation?

Without observability, these questions require guesswork, reproduction, or hope.

---

## The Observation Problem

**The fundamental problem: Capabilities without observability are black boxes. Problems are discovered by users, not detected by systems. Performance degrades silently. Errors hide in plain sight.**

### The Black Box

```
             ┌─────────────────┐
Input ───────▶│   Black Box     │────────▶ Output
             │   ?????????     │
             └─────────────────┘

What happened inside? 🤷
```

Without observability, you see inputs and outputs, but not the process. When something goes wrong, you reconstruct from evidence.

### The Observable System

```
             ┌─────────────────────────────────────┐
             │   Observable System                  │
             │                                      │
Input ───────▶│  ┌─────┐  ┌─────┐  ┌─────┐        │────────▶ Output
             │  │Step1│──▶│Step2│──▶│Step3│        │
             │  │ 10ms│  │ 45ms│  │  5ms│        │
             │  └──┬──┘  └──┬──┘  └──┬──┘        │
             │     │        │        │            │
             └─────┼────────┼────────┼────────────┘
                   │        │        │
                   ▼        ▼        ▼
               Traces   Metrics   Logs

Everything visible. Problems found immediately.
```

---

## The Forces

### Force: Performance vs. Insight

*Telemetry has cost. Every span, every metric, every log adds overhead.*

Heavy instrumentation can measurably slow your system. But insufficient instrumentation leaves you blind.

**Resolution:** Instrument strategically. High-value spans (entry points, slow operations). Efficient metrics (counters, histograms). Sampled traces for high-volume paths.

### Force: Detail vs. Noise

*More detail aids debugging. But too much detail is noise.*

Recording everything is overwhelming. Recording nothing is useless.

**Resolution:** Log at appropriate levels. Debug-level for detailed tracing. Info-level for significant events. Error-level for problems. Configure levels per environment.

### Force: Privacy vs. Debugging

*Detailed context aids debugging. But some context is sensitive.*

Including user data in logs helps reproduce issues. But it risks privacy violations.

**Resolution:** Scrub sensitive data. Use IDs instead of PII. Implement data retention policies. Follow privacy regulations.

---

## Therefore

**Instrument capabilities with OpenTelemetry, generating specifications for expected telemetry alongside code. Telemetry becomes part of the capability contract—specified, generated, verified.**

Observability architecture:

```
┌─────────────────────────────────────────────────────────────────────────┐
│  OBSERVABILITY ARCHITECTURE                                              │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ TRACES (Distributed tracing)                                        │ │
│  │                                                                     │ │
│  │  Span: validate.command                                            │ │
│  │    └─ Span: validate.load_file (10ms)                              │ │
│  │    └─ Span: validate.parse_rdf (45ms)                              │ │
│  │    └─ Span: validate.shacl_check (120ms)                           │ │
│  │         └─ Span: shacl.load_shapes (5ms)                           │ │
│  │         └─ Span: shacl.validate (110ms)                            │ │
│  │    └─ Span: validate.format_results (5ms)                          │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ METRICS (Quantitative measurements)                                 │ │
│  │                                                                     │ │
│  │  Counter:   validate.invocations_total                             │ │
│  │  Counter:   validate.errors_total                                  │ │
│  │  Histogram: validate.duration_seconds                              │ │
│  │  Histogram: validate.file_size_bytes                               │ │
│  │  Gauge:     validate.concurrent_operations                         │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ LOGS (Structured events)                                            │ │
│  │                                                                     │ │
│  │  INFO:  validation.started file=test.ttl size=1234                 │ │
│  │  WARN:  validation.slow_operation duration=2.5s threshold=1.0s     │ │
│  │  ERROR: validation.failed reason="Invalid syntax" line=42          │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Telemetry Specification

### Specifying Expected Telemetry

```turtle
@prefix otel: <https://opentelemetry.io/ontology#> .
@prefix cli: <https://spec-kit.org/cli#> .
@prefix sk: <https://spec-kit.org/ontology#> .

# Validate command telemetry specification
cli:ValidateCommand otel:emits [
    a otel:Span ;
    otel:name "validate.command" ;
    sk:description "Root span for validate command execution" ;
    otel:attributes [
        otel:attr "file.path" ;
        otel:attr "file.size" ;
        otel:attr "validation.result"
    ]
] ;

otel:emits [
    a otel:Span ;
    otel:name "validate.parse_rdf" ;
    sk:description "Time spent parsing RDF file" ;
    otel:parent "validate.command"
] ;

otel:emits [
    a otel:Span ;
    otel:name "validate.shacl_check" ;
    sk:description "Time spent on SHACL validation" ;
    otel:parent "validate.command"
] ;

otel:emits [
    a otel:Metric ;
    otel:name "validate.duration" ;
    otel:type "histogram" ;
    otel:unit "seconds" ;
    sk:description "Duration of validation operations"
] ;

otel:emits [
    a otel:Metric ;
    otel:name "validate.errors" ;
    otel:type "counter" ;
    sk:description "Number of validation errors encountered"
] ;

otel:emits [
    a otel:Metric ;
    otel:name "validate.file_size" ;
    otel:type "histogram" ;
    otel:unit "bytes" ;
    sk:description "Size of validated files"
] .
```

---

## Instrumentation Implementation

### OpenTelemetry Setup

```python
# src/specify_cli/core/telemetry.py
"""OpenTelemetry instrumentation for specify-cli."""

import functools
import time
from contextlib import contextmanager
from typing import Any, Callable, Optional, TypeVar

from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

# Global tracer and meter
_tracer: Optional[trace.Tracer] = None
_meter: Optional[metrics.Meter] = None


def setup_telemetry(service_name: str = "specify-cli") -> None:
    """Initialize OpenTelemetry instrumentation."""
    global _tracer, _meter

    # Setup tracing
    trace_provider = TracerProvider()
    trace_provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter())
    )
    trace.set_tracer_provider(trace_provider)
    _tracer = trace.get_tracer(service_name)

    # Setup metrics
    metric_reader = PeriodicExportingMetricReader(OTLPMetricExporter())
    meter_provider = MeterProvider(metric_readers=[metric_reader])
    metrics.set_meter_provider(meter_provider)
    _meter = metrics.get_meter(service_name)


def get_tracer() -> trace.Tracer:
    """Get the global tracer, initializing if needed."""
    global _tracer
    if _tracer is None:
        # Graceful fallback: no-op tracer if not configured
        return trace.get_tracer("specify-cli")
    return _tracer


def get_meter() -> metrics.Meter:
    """Get the global meter, initializing if needed."""
    global _meter
    if _meter is None:
        return metrics.get_meter("specify-cli")
    return _meter


@contextmanager
def span(name: str, attributes: Optional[dict] = None):
    """Context manager for creating spans.

    Usage:
        with span("validate.parse", {"file.path": str(path)}):
            # instrumented code
    """
    tracer = get_tracer()
    with tracer.start_as_current_span(name, attributes=attributes) as s:
        yield s


T = TypeVar('T')


def timed(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to automatically instrument a function with timing.

    Creates a span and records duration.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> T:
        with span(f"{func.__module__}.{func.__name__}"):
            return func(*args, **kwargs)
    return wrapper


def instrument_command(command_name: str):
    """Decorator to instrument CLI commands.

    Creates root span and records standard metrics.
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        meter = get_meter()

        # Create metrics
        duration_histogram = meter.create_histogram(
            f"{command_name}.duration",
            unit="seconds",
            description=f"Duration of {command_name} command"
        )
        invocation_counter = meter.create_counter(
            f"{command_name}.invocations",
            description=f"Number of {command_name} invocations"
        )
        error_counter = meter.create_counter(
            f"{command_name}.errors",
            description=f"Number of {command_name} errors"
        )

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            invocation_counter.add(1)
            start_time = time.perf_counter()

            try:
                with span(f"{command_name}.command") as s:
                    result = func(*args, **kwargs)
                    s.set_attribute("command.result", "success")
                    return result

            except Exception as e:
                error_counter.add(1, {"error.type": type(e).__name__})
                raise

            finally:
                duration = time.perf_counter() - start_time
                duration_histogram.record(duration)

        return wrapper
    return decorator
```

### Instrumented Command

```python
# src/specify_cli/commands/validate.py
"""Validate command with full instrumentation."""

import typer
from pathlib import Path
from typing import Optional

from specify_cli.core.telemetry import (
    instrument_command, span, get_meter
)
from specify_cli import ops

app = typer.Typer()
meter = get_meter()

# Create command-specific metrics
file_size_histogram = meter.create_histogram(
    "validate.file_size",
    unit="bytes",
    description="Size of validated files"
)


@app.command()
@instrument_command("validate")
def validate(
    file: Path = typer.Argument(..., help="File to validate"),
    shapes: Optional[Path] = typer.Option(None, "--shapes", "-s"),
    strict: bool = typer.Option(False, "--strict"),
) -> None:
    """Validate RDF files against SHACL shapes."""

    # Record file size
    file_size = file.stat().st_size
    file_size_histogram.record(file_size)

    # Parse RDF with instrumentation
    with span("validate.parse_rdf", {"file.path": str(file), "file.size": file_size}):
        graph = ops.parse_rdf(file)

    # Load shapes with instrumentation
    with span("validate.load_shapes"):
        shapes_graph = ops.load_shapes(shapes)

    # SHACL validation with instrumentation
    with span("validate.shacl_check", {"shapes.count": len(shapes_graph)}):
        result = ops.validate_shacl(graph, shapes_graph)

    # Format and display results
    with span("validate.format_results"):
        display_result(result, strict)
```

---

## Telemetry Verification

### Testing Expected Telemetry

```python
# tests/telemetry/test_validate_telemetry.py
"""Tests verifying validate command emits expected telemetry."""

import pytest
from pathlib import Path
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export.in_memory import InMemorySpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import InMemoryMetricReader
from opentelemetry import trace, metrics

from specify_cli.commands.validate import validate


@pytest.fixture
def telemetry_capture():
    """Capture telemetry for verification."""
    # Setup span capture
    span_exporter = InMemorySpanExporter()
    trace_provider = TracerProvider()
    trace_provider.add_span_processor(
        SimpleSpanProcessor(span_exporter)
    )
    trace.set_tracer_provider(trace_provider)

    # Setup metric capture
    metric_reader = InMemoryMetricReader()
    meter_provider = MeterProvider(metric_readers=[metric_reader])
    metrics.set_meter_provider(meter_provider)

    yield {
        "spans": span_exporter,
        "metrics": metric_reader
    }

    span_exporter.clear()


class TestValidateTelemetry:
    """Verify validate command emits specified telemetry."""

    def test_emits_root_span(self, telemetry_capture, tmp_path):
        """Verify root span emitted with correct name."""
        test_file = tmp_path / "test.ttl"
        test_file.write_text("@prefix ex: <http://example.org/> . ex:a ex:b ex:c .")

        validate(test_file)

        spans = telemetry_capture["spans"].get_finished_spans()
        root_span = next(s for s in spans if s.name == "validate.command")

        assert root_span is not None
        assert root_span.attributes.get("command.result") == "success"

    def test_emits_parse_span(self, telemetry_capture, tmp_path):
        """Verify parse span emitted with file attributes."""
        test_file = tmp_path / "test.ttl"
        test_file.write_text("@prefix ex: <http://example.org/> . ex:a ex:b ex:c .")

        validate(test_file)

        spans = telemetry_capture["spans"].get_finished_spans()
        parse_span = next(s for s in spans if s.name == "validate.parse_rdf")

        assert parse_span is not None
        assert "file.path" in parse_span.attributes
        assert "file.size" in parse_span.attributes

    def test_emits_shacl_span(self, telemetry_capture, tmp_path):
        """Verify SHACL validation span emitted."""
        test_file = tmp_path / "test.ttl"
        test_file.write_text("@prefix ex: <http://example.org/> . ex:a ex:b ex:c .")

        validate(test_file)

        spans = telemetry_capture["spans"].get_finished_spans()
        shacl_span = next(s for s in spans if s.name == "validate.shacl_check")

        assert shacl_span is not None

    def test_records_duration_metric(self, telemetry_capture, tmp_path):
        """Verify duration metric recorded."""
        test_file = tmp_path / "test.ttl"
        test_file.write_text("@prefix ex: <http://example.org/> . ex:a ex:b ex:c .")

        validate(test_file)

        metrics_data = telemetry_capture["metrics"].get_metrics_data()
        duration_metric = find_metric(metrics_data, "validate.duration")

        assert duration_metric is not None
        assert duration_metric.data.data_points[0].sum > 0

    def test_records_file_size_metric(self, telemetry_capture, tmp_path):
        """Verify file size metric recorded."""
        test_file = tmp_path / "test.ttl"
        content = "@prefix ex: <http://example.org/> . ex:a ex:b ex:c ."
        test_file.write_text(content)

        validate(test_file)

        metrics_data = telemetry_capture["metrics"].get_metrics_data()
        size_metric = find_metric(metrics_data, "validate.file_size")

        assert size_metric is not None
        assert size_metric.data.data_points[0].sum == len(content)

    def test_increments_invocation_counter(self, telemetry_capture, tmp_path):
        """Verify invocation counter incremented."""
        test_file = tmp_path / "test.ttl"
        test_file.write_text("@prefix ex: <http://example.org/> . ex:a ex:b ex:c .")

        validate(test_file)
        validate(test_file)

        metrics_data = telemetry_capture["metrics"].get_metrics_data()
        invocation_metric = find_metric(metrics_data, "validate.invocations")

        assert invocation_metric is not None
        assert invocation_metric.data.data_points[0].value == 2
```

---

## Observability in Practice

### Dashboard Queries

```sql
-- Average validation duration by file size bucket
SELECT
    CASE
        WHEN file_size < 1000 THEN 'small (<1KB)'
        WHEN file_size < 100000 THEN 'medium (1-100KB)'
        ELSE 'large (>100KB)'
    END as size_bucket,
    AVG(duration_seconds) as avg_duration,
    COUNT(*) as count
FROM validate_metrics
GROUP BY size_bucket;

-- Error rate over time
SELECT
    DATE_TRUNC('hour', timestamp) as hour,
    SUM(CASE WHEN error_type IS NOT NULL THEN 1 ELSE 0 END)::float / COUNT(*) as error_rate
FROM validate_traces
GROUP BY hour
ORDER BY hour;

-- Slowest validation operations
SELECT
    file_path,
    duration_seconds,
    file_size
FROM validate_traces
WHERE duration_seconds > 5
ORDER BY duration_seconds DESC
LIMIT 10;
```

### Alerting Rules

```yaml
# prometheus-rules.yml
groups:
  - name: specify-cli
    rules:
      - alert: HighValidationErrorRate
        expr: rate(validate_errors_total[5m]) / rate(validate_invocations_total[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High validation error rate"
          description: "Error rate is {{ $value | humanizePercentage }}"

      - alert: SlowValidation
        expr: histogram_quantile(0.99, validate_duration_seconds) > 10
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Validation p99 latency too high"
          description: "p99 latency is {{ $value }}s"
```

---

## Anti-Patterns

### Anti-Pattern: No Instrumentation

*"We'll add telemetry when we need it."*

When you need telemetry, it's too late. The incident is happening, and you have no data.

**Resolution:** Instrument from the start. Basic telemetry has low overhead and high value.

### Anti-Pattern: Log Everything

*"More data is always better."*

Logging everything creates noise, cost, and privacy risk.

**Resolution:** Log what matters. Use appropriate log levels. Sample high-volume events.

### Anti-Pattern: Metrics Without Context

*"We have metrics but can't explain the numbers."*

Metrics tell you what. Traces tell you why.

**Resolution:** Correlate metrics with traces. When a metric spikes, trace to understand.

---

## Implementation Checklist

### Instrumentation

- [ ] Set up OpenTelemetry SDK
- [ ] Create telemetry helper functions
- [ ] Instrument entry points with root spans
- [ ] Add child spans for significant operations
- [ ] Record duration, size, and count metrics
- [ ] Add structured logging

### Testing

- [ ] Test expected spans are emitted
- [ ] Test metrics are recorded
- [ ] Verify attribute completeness
- [ ] Test error path instrumentation

### Operations

- [ ] Export telemetry to backend
- [ ] Create dashboards
- [ ] Configure alerts
- [ ] Document metric meanings

---

## Resulting Context

After implementing this pattern, you have:

- **Instrumented capabilities** with standard telemetry
- **Ability to trace, measure, and debug** production systems
- **Foundation for performance optimization** through metrics
- **Data for usage analysis** and capacity planning
- **Verified telemetry** as part of the capability contract

Observable execution completes the verification story: specifications define behavior, tests verify behavior, telemetry reveals behavior in production.

---

## Code References

The following spec-kit source files implement observable execution:

| Reference | Description |
|-----------|-------------|
| `src/specify_cli/core/telemetry.py:1-50` | OpenTelemetry span and timed decorators |
| `src/specify_cli/core/jtbd_metrics.py:1-100` | JTBD-specific metrics instrumentation |
| `templates/command.tera:56` | instrument_command import in generated code |
| `templates/command.tera:88` | @instrument_command decorator in generated commands |

---

## Related Patterns

- **Specifies:** **[11. Executable Specification](../specification/executable-specification.md)** — Telemetry specified
- **Enables:** **[40. Outcome Measurement](../evolution/outcome-measurement.md)** — Metrics enable outcome tracking
- **Supports:** **[39. Feedback Loop](../evolution/feedback-loop.md)** — Telemetry data for feedback
- **Verified by:** **[33. Integration Reality](./integration-reality.md)** — Test real telemetry

---

## Part V Transition

You've completed the Verification Patterns. You now know how to:

- Write **[Tests Before Code](./test-before-code.md)** from specifications
- Create **[Contract Tests](./contract-test.md)** for interfaces
- Verify **[Integration Reality](./integration-reality.md)** with real dependencies
- Validate **[Shapes](./shape-validation.md)** with SHACL
- Detect **[Drift](./drift-detection.md)** from the constitutional equation
- Verify **[Receipts](./receipt-verification.md)** as proofs
- Run **[Continuous Validation](./continuous-validation.md)** in CI
- Enable **[Observable Execution](./observable-execution.md)** with telemetry

The capability is specified, transformed, and verified. But capabilities must evolve. User needs change. Requirements expand. Technology advances. How do you evolve capabilities while maintaining the benefits of specification-driven development?

Turn to **[Part V: Evolution Patterns](../evolution/feedback-loop.md)** to learn how capabilities grow and improve over time.

---

## Philosophical Note

> *"Without data, you're just another person with an opinion."*
> — W. Edwards Deming

Observable execution transforms opinion into data. Instead of "I think validation is slow," you have "validation p99 is 2.3 seconds." Instead of "users seem to have problems," you have "error rate spiked 300% after the last deploy."

Data enables improvement. You can't optimize what you can't measure. You can't fix what you can't see. You can't prove improvement without before-and-after numbers.

Observability isn't just about debugging incidents. It's about understanding your system, making informed decisions, and proving that changes actually improve things.

---

**This completes Part IV: Verification Patterns.**

**Next:** Begin Part V with **[39. Feedback Loop](../evolution/feedback-loop.md)** to learn how observations and metrics drive capability evolution.
