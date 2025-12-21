# Hyperdimensional Observability

Minimal OTEL instrumentation for hyperdimensional computing operations in spec-kit.

## Overview

The `observability_core` module provides lightweight OpenTelemetry wrappers for tracking hyperdimensional operations without adding complexity. It follows the 80/20 principle:

- **80% value**: Core OTEL spans + basic metrics using existing infrastructure
- **20% skipped**: Custom dashboards, aggregation, visualization (add later if needed)

## Quick Start

```python
from specify_cli.hyperdimensional import (
    track_embedding_operation,
    track_similarity_search,
    track_validation_check,
    record_vector_stats,
    record_search_latency,
)

# Track embedding creation
with track_embedding_operation("embed_command", vector_count=1, dimensions=10000):
    vector = hde.embed_command("init")

# Track similarity search
with track_similarity_search("find_similar", result_count=10):
    results = search_features(query, k=10)

# Track validation
with track_validation_check("spec_compliance", score=0.95, passed=True):
    compliance = verify_spec_compliance(code, spec)
```

## Features

### 1. Embedding Operations

Track vector creation, binding, bundling, and transformations:

```python
with track_embedding_operation(
    "bind_vectors",
    vector_count=2,
    dimensions=10000,
    custom_attr="value"
):
    result = hde.bind(vector_a, vector_b)
```

**Metrics created:**
- `hyperdimensional.embedding.{operation}.operations` (counter)
- `hyperdimensional.embedding.{operation}.success` (counter)
- `hyperdimensional.embedding.{operation}.errors` (counter)

**Span attributes:**
- `hd.operation` - Operation name
- `hd.operation.type` - "embedding"
- `hd.vector.count` - Number of vectors
- `hd.vector.dimensions` - Dimensionality

### 2. Similarity Search

Track semantic search operations:

```python
with track_similarity_search(
    "feature_search",
    result_count=10,
    search_type="semantic"
):
    results = search_by_semantic_similarity(query, k=10)
```

**Metrics created:**
- `hyperdimensional.search.{type}.operations` (counter)
- `hyperdimensional.search.{type}.result_count` (histogram)
- `hyperdimensional.search.{type}.success` (counter)
- `hyperdimensional.search.{type}.latency_ms` (histogram)

**Span attributes:**
- `hd.operation` - Search query name
- `hd.operation.type` - "search"
- `hd.search.type` - Search type (semantic, similarity, feature)
- `hd.search.result_count` - Number of results

### 3. Validation Checks

Track validation and verification:

```python
with track_validation_check(
    "spec_compliance",
    passed=True,
    score=0.95
) as span:
    # Can update during validation
    span.set_attribute("spec.sections", 10)
```

**Metrics created:**
- `hyperdimensional.validation.{check}.checks` (counter)
- `hyperdimensional.validation.{check}.score` (histogram)
- `hyperdimensional.validation.{check}.passed` (counter)
- `hyperdimensional.validation.{check}.failed` (counter)

**Span attributes:**
- `hd.operation` - Check name
- `hd.operation.type` - "validation"
- `hd.validation.check` - Check identifier
- `hd.validation.passed` - Boolean result
- `hd.validation.score` - Numeric score (0.0-1.0)

### 4. Convenience Functions

Quick metric recording without spans:

```python
# Record vector processing stats
record_vector_stats(
    vector_count=100,
    dimensions=10000,
    operation="bulk_embed"
)

# Record search latency
import time
start = time.perf_counter()
results = search(query)
latency_ms = (time.perf_counter() - start) * 1000
record_search_latency(latency_ms, search_type="semantic")
```

## Configuration

Uses existing spec-kit OTEL infrastructure - no additional configuration needed.

### Environment Variables

```bash
# Enable OTEL (default: true)
export SPECIFY_OTEL_ENABLED=true

# Set OTEL collector endpoint
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317

# Set service name (default: specify-cli)
export OTEL_SERVICE_NAME=specify-cli
```

### Graceful Degradation

When OTEL is not configured or disabled:
- All functions work normally (no-op)
- No errors or warnings
- Zero performance overhead

## Querying Telemetry

### Traces (Jaeger/Tempo)

Find hyperdimensional operations:
```
service="specify-cli" AND name LIKE "hyperdimensional.*"
```

Filter by operation type:
```
hd.operation.type="embedding"
hd.operation.type="search"
hd.operation.type="validation"
```

### Metrics (Prometheus)

Count operations:
```promql
rate(hyperdimensional_embedding_embed_command_operations_total[5m])
rate(hyperdimensional_search_semantic_operations_total[5m])
```

Average search latency:
```promql
histogram_quantile(0.95,
  rate(hyperdimensional_search_semantic_latency_ms_bucket[5m])
)
```

Validation pass rate:
```promql
rate(hyperdimensional_validation_spec_compliance_passed_total[5m])
/
rate(hyperdimensional_validation_spec_compliance_checks_total[5m])
```

## Design Decisions

### Why Minimal?

Following the 80/20 principle:

**Included (80% value):**
- ✅ OTEL spans for distributed tracing
- ✅ Basic counters and histograms
- ✅ Standard semantic attributes
- ✅ Existing infrastructure reuse
- ✅ Graceful degradation

**Excluded (20% value, can add later):**
- ❌ Custom dashboards (use OTEL backend tools)
- ❌ Complex metrics aggregation (use Prometheus)
- ❌ Real-time monitoring UI (use Grafana)
- ❌ Custom exporters (use OTLP standard)

### Integration Points

The observability module integrates with:

1. **Core Telemetry** (`core/telemetry.py`)
   - Uses existing `span()` context manager
   - Uses existing `metric_counter()` and `metric_histogram()`
   - Shares OTEL configuration

2. **Hyperdimensional Operations**
   - Wraps key operations (embeddings, search, validation)
   - Minimal overhead (context manager only)
   - No code changes required in existing modules

3. **OTEL Backend**
   - Standard OTLP protocol
   - Works with any OTEL-compatible backend
   - No vendor lock-in

## Examples

See `/examples/hyperdimensional_observability_demo.py` for complete examples.

## Future Enhancements

If needed (based on actual usage):

1. **Dashboards**: Pre-built Grafana dashboards
2. **Alerts**: Prometheus alerting rules
3. **Anomaly Detection**: Statistical anomaly detection
4. **Performance Profiling**: Detailed latency breakdown
5. **Cost Analysis**: Resource usage tracking

## References

- OpenTelemetry Specification: https://opentelemetry.io/docs/specs/otel/
- spec-kit Telemetry: `/src/specify_cli/core/telemetry.py`
- Semantic Conventions: `/src/specify_cli/core/semconv.py`
