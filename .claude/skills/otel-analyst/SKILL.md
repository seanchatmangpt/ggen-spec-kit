---
name: otel-analyst
description: Analyze OpenTelemetry traces and metrics for observability insights. Use when checking instrumentation coverage, analyzing performance, or debugging telemetry issues.
allowed-tools: Read, Glob, Grep, Bash, LSP
---

# OpenTelemetry Analyst

Analyze OpenTelemetry traces and metrics to understand system behavior.

## Trigger Conditions

- Performance analysis requirements
- Instrumentation coverage gaps
- Bottleneck identification
- Span hierarchy validation

## Key Capabilities

- Trace hierarchy analysis
- Metrics extraction (counters, histograms)
- OTEL best practices enforcement
- Coverage assessment

## Integration

**ggen v5.0.2**: Profiles ggen sync performance and instrumentation
**Architecture**: Validates Commands/Ops/Runtime span hierarchies

## Instructions

1. Examine span hierarchies and attributes
2. Analyze metrics (counters, histograms)
3. Identify performance bottlenecks
4. Find uninstrumented code paths
5. Ensure OTEL best practices

## Expected Span Hierarchy

```
specify.command (commands layer)
  └─ specify.operation (ops layer)
      ├─ specify.runtime.subprocess (runtime)
      ├─ specify.runtime.io (runtime)
      └─ specify.runtime.http (runtime)
```

## Analysis Commands

```bash
# Check instrumentation coverage
grep -rn "@span\|@timed\|with span" src/specify_cli/

# Check commands layer
grep -rn "instrument_command\|span" src/specify_cli/commands/

# Check ops layer
grep -rn "@timed\|span" src/specify_cli/ops/

# Check runtime layer
grep -rn "span\|run_logged" src/specify_cli/runtime/
```

## Key Metrics

```python
"specify.commands.total"      # Counter
"specify.commands.duration"   # Histogram
"specify.commands.errors"     # Counter
"specify.operations.duration" # Histogram
```

## Best Practices

### Span Naming
```python
# ✅ Good: Hierarchical
"specify.init.validate_name"

# ❌ Bad: Vague
"operation"
```

### Error Recording
```python
span.set_status(Status(StatusCode.ERROR, str(e)))
span.record_exception(e)
```

## Output Format

```markdown
## OTEL Analysis Report

### Instrumentation Coverage
- Commands: X/Y (X%)
- Operations: X/Y (X%)
- Runtime: X/Y (X%)

### Performance Insights
- Slowest: `operation` (Xms)

### Gaps Identified
1. Missing @timed on function

### Recommendations
1. Add span to X
```
