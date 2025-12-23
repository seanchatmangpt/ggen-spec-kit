# 38. Observable Execution

★★

*You can't improve what you can't observe. Observable execution instruments capabilities with telemetry—traces, metrics, logs—enabling understanding, debugging, and optimization.*

---

A capability that works is good. A capability you can observe working is better.

Observable execution means:
- **Traces** — Follow a request through the system
- **Metrics** — Measure performance, errors, usage
- **Logs** — Record significant events
- **Events** — Structured notifications of state changes

With observability, you can answer:
- Why did this fail?
- How long does this take?
- How often is this used?
- What's the bottleneck?

Without observability, these questions require guesswork.

**The problem: Capabilities without observability are black boxes. Problems are discovered by users, not detected by systems.**

---

**The forces at play:**

- *Performance wants minimal overhead.* Telemetry has cost.

- *Understanding wants detail.* More data enables better analysis.

- *Debugging wants traces.* Stack traces aren't enough.

- *Privacy wants limits.* Not everything should be recorded.

The tension: comprehensive enough to enable debugging, efficient enough to run in production.

---

**Therefore:**

Instrument capabilities with OpenTelemetry, generating specifications for expected telemetry alongside code.

**Telemetry specification:**

```turtle
cli:ValidateCommand cli:emits [
    a otel:Span ;
    otel:name "validate.command" ;
    otel:attributes [
        otel:attr "file.path" ;
        otel:attr "file.size" ;
        otel:attr "validation.result"
    ]
] ;

cli:emits [
    a otel:Metric ;
    otel:name "validate.duration" ;
    otel:type "histogram" ;
    otel:unit "ms"
] ;

cli:emits [
    a otel:Metric ;
    otel:name "validate.errors" ;
    otel:type "counter"
] .
```

**Generated instrumentation:**

```python
# Generated from specification
from opentelemetry import trace
from opentelemetry import metrics
from specify_cli.core.telemetry import span, timed

tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)

validate_duration = meter.create_histogram(
    "validate.duration",
    unit="ms",
    description="Time to validate files"
)

validate_errors = meter.create_counter(
    "validate.errors",
    description="Number of validation errors"
)


@timed
def validate_command(file: Path) -> None:
    """Validate RDF files with telemetry."""
    with span("validate.command",
              attributes={"file.path": str(file),
                         "file.size": file.stat().st_size}):

        start = time.perf_counter()
        try:
            result = do_validation(file)

            # Record success
            validate_duration.record(
                (time.perf_counter() - start) * 1000,
                {"result": "success"}
            )

        except ValidationError as e:
            # Record failure
            validate_errors.add(1, {"error_type": type(e).__name__})
            validate_duration.record(
                (time.perf_counter() - start) * 1000,
                {"result": "failure"}
            )
            raise
```

**Telemetry verification:**

```python
# tests/telemetry/test_validate_telemetry.py
"""Verify validate command emits expected telemetry."""

from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export.in_memory import InMemorySpanExporter

def test_validate_emits_span(tmp_path):
    """Verify span emitted with correct attributes."""
    exporter = InMemorySpanExporter()
    # ... setup provider ...

    # Run command
    validate_command(tmp_path / "test.ttl")

    # Verify span
    spans = exporter.get_finished_spans()
    assert len(spans) == 1
    assert spans[0].name == "validate.command"
    assert "file.path" in spans[0].attributes
    assert "file.size" in spans[0].attributes

def test_validate_records_duration_metric():
    """Verify duration metric recorded."""
    # ... similar pattern ...
```

**Observability dashboard:**

With standardized telemetry:
- Query traces across commands
- Build performance dashboards
- Alert on error rates
- Analyze usage patterns

---

**Resulting context:**

After applying this pattern, you have:

- Instrumented capabilities with standard telemetry
- Ability to trace, measure, and debug
- Foundation for performance optimization
- Data for usage analysis

This completes the Verification Patterns and prepares for **[Part V: Evolution Patterns](../evolution/feedback-loop.md)**.

---

**Related patterns:**

- *Specifies:* **[11. Executable Specification](../specification/executable-specification.md)** — Telemetry specified
- *Enables:* **[40. Outcome Measurement](../evolution/outcome-measurement.md)** — Metrics for outcomes
- *Supports:* **[39. Feedback Loop](../evolution/feedback-loop.md)** — Telemetry data
- *Verified by:* **[33. Integration Reality](./integration-reality.md)** — Real telemetry

---

## Transition to Part V

You've completed the Verification Patterns. You know how to:
- Write **[Tests Before Code](./test-before-code.md)** from specifications
- Create **[Contract Tests](./contract-test.md)** for interfaces
- Verify **[Integration Reality](./integration-reality.md)** with real dependencies
- Validate **[Shapes](./shape-validation.md)** with SHACL
- Detect **[Drift](./drift-detection.md)** from constitutional equation
- Verify **[Receipts](./receipt-verification.md)** for proof
- Run **[Continuous Validation](./continuous-validation.md)** in CI
- Enable **[Observable Execution](./observable-execution.md)** with telemetry

Now it's time to learn how capabilities grow and evolve. Turn to **[Part V: Evolution Patterns](../evolution/feedback-loop.md)** to understand how to improve capabilities based on real-world feedback.
