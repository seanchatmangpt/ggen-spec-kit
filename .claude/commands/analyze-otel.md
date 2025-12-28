# Analyze OpenTelemetry Traces

Analyze OpenTelemetry traces and metrics for performance insights.

## Usage
```
/analyze-otel [SPAN_NAME]
```

## Arguments
- `$1` - Span name or operation to analyze (optional)

## Instructions

Analyze OpenTelemetry instrumentation and traces.

If a span name is provided, focus on that operation: `$1`

Investigation steps:
1. Find instrumented code in `src/specify_cli/core/telemetry.py`
2. Identify all `@timed` decorated functions
3. Find all `with span(...)` blocks
4. Check trace context propagation

Report:
- Instrumentation coverage
- Span hierarchy and relationships
- Attributes being captured
- Performance metrics if available
- Recommendations for additional instrumentation

Look for patterns like:
```python
from specify_cli.core.telemetry import span, timed

@timed
def operation():
    with span("operation.step", key="value"):
        # instrumented code
```
