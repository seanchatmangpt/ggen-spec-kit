# Analyze OpenTelemetry Traces

Analyze OpenTelemetry traces and metrics for performance insights and observability coverage.

## Description
Examines OTEL instrumentation across the codebase to identify coverage gaps, performance bottlenecks, and trace quality issues.

## Usage
```bash
/analyze-otel [SPAN_NAME]
```

## Arguments
- `SPAN_NAME` (optional) - Specific span name or operation to analyze (e.g., "ggen.sync", "init.project")

## Examples
```bash
# Analyze all instrumentation
/analyze-otel

# Focus on specific operation
/analyze-otel ggen.sync

# Analyze a specific layer
/analyze-otel runtime.subprocess
```

## What This Command Does

1. **Find Instrumented Code**
   - Scans `src/specify_cli/core/telemetry.py` for telemetry infrastructure
   - Identifies all `@timed` decorated functions
   - Locates all `with span(...)` context managers
   - Maps trace hierarchy and relationships

2. **Analyze Coverage**
   - Commands layer: Should have minimal instrumentation
   - Operations layer: Should instrument business logic
   - Runtime layer: Should instrument all I/O operations

3. **Check Patterns**
   ```python
   from specify_cli.core.telemetry import span, timed

   @timed
   def operation():
       with span("operation.step", key="value"):
           # instrumented code
   ```

## Output Format

Provides structured report with:

### Coverage Summary
- Total instrumented functions
- Instrumented vs uninstrumented operations
- Layer-by-layer coverage breakdown

### Span Hierarchy
```
ggen.sync
├── ggen.normalize (SHACL validation)
├── ggen.extract (SPARQL query)
├── ggen.emit (Tera template)
├── ggen.canonicalize (formatting)
└── ggen.receipt (SHA256 hash)
```

### Attributes Captured
- Operation metadata (layer, component, command)
- Performance metrics (duration, memory)
- Error information (exceptions, stack traces)
- Context propagation (trace_id, span_id)

### Recommendations
- Missing instrumentation points
- Attribute enrichment opportunities
- Performance optimization targets
- Trace context improvements

## Integration

Works with:
- `specify_cli.core.telemetry` - Core OTEL infrastructure
- `@timed` decorator - Automatic function timing
- `span()` context manager - Manual span creation
- OpenTelemetry exporters (if configured)

## Performance Targets
- Command startup: < 500ms
- Simple operations: < 100ms
- Complex transformations: < 5s
- Memory usage: < 100MB

## Notes
- OTEL is gracefully degraded when unavailable
- All runtime operations should be instrumented
- Pure operations (ops layer) instrument logic flow only
- Commands layer has minimal instrumentation
