# Hyperdimensional Observability - Quick Reference

## Import

```python
from specify_cli.hyperdimensional import (
    track_embedding_operation,
    track_similarity_search,
    track_validation_check,
    record_vector_stats,
    record_search_latency,
)
```

## Track Embedding Operations

```python
with track_embedding_operation(
    operation_name="embed_command",  # Required: operation name
    vector_count=1,                  # Optional: number of vectors (default: 1)
    dimensions=10000,                # Optional: vector dimensions
    custom_attr="value"              # Optional: any custom attributes
):
    vector = hde.embed_command("init")
```

**Metrics:** `hyperdimensional.embedding.{operation}.operations/success/errors`

**Attributes:** `hd.operation`, `hd.operation.type`, `hd.vector.count`, `hd.vector.dimensions`

## Track Similarity Search

```python
with track_similarity_search(
    query_name="find_similar_features",  # Required: search query name
    result_count=10,                     # Optional: number of results (default: 0)
    search_type="semantic",              # Optional: search type (default: "semantic")
    min_similarity=0.8                   # Optional: any custom attributes
):
    results = search_by_semantic_similarity(query, k=10)
```

**Metrics:** `hyperdimensional.search.{type}.operations/success/errors/result_count/latency_ms`

**Attributes:** `hd.operation`, `hd.operation.type`, `hd.search.type`, `hd.search.result_count`

## Track Validation Checks

```python
with track_validation_check(
    check_name="spec_compliance",  # Required: check name
    passed=True,                   # Optional: pass/fail result
    score=0.95,                    # Optional: numeric score (0.0-1.0)
    spec_sections=10               # Optional: any custom attributes
) as span:
    # Can update during validation
    compliance = verify_spec_compliance(code, spec)
    span.set_attribute("spec.complete", True)
```

**Metrics:** `hyperdimensional.validation.{check}.checks/passed/failed/score`

**Attributes:** `hd.operation`, `hd.operation.type`, `hd.validation.check`, `hd.validation.passed`, `hd.validation.score`

## Record Vector Stats (Quick)

```python
record_vector_stats(
    vector_count=100,     # Required: number of vectors
    dimensions=10000,     # Required: vector dimensions
    operation="bulk_embed"  # Optional: operation name (default: "general")
)
```

**Metrics:** `hyperdimensional.vectors.{operation}.d{dimensions}.processed`

## Record Search Latency (Quick)

```python
import time
start = time.perf_counter()
results = search_features(query)
latency_ms = (time.perf_counter() - start) * 1000

record_search_latency(
    latency_ms=latency_ms,        # Required: latency in milliseconds
    search_type="feature_search"  # Optional: search type (default: "semantic")
)
```

**Metrics:** `hyperdimensional.search.{type}.latency_ms`

## Configuration

### Enable/Disable OTEL

```bash
# Enable (default)
export SPECIFY_OTEL_ENABLED=true

# Disable
export SPECIFY_OTEL_ENABLED=false
```

### Set OTEL Endpoint

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
export OTEL_SERVICE_NAME=specify-cli
```

### No Configuration (Graceful Degradation)

If no OTEL endpoint is set, all functions work as no-ops:
- No errors
- No warnings
- Zero overhead

## Query Examples

### Jaeger/Tempo (Traces)

```
# Find all hyperdimensional operations
service="specify-cli" AND name LIKE "hyperdimensional.*"

# Filter by type
hd.operation.type="embedding"
hd.operation.type="search"
hd.operation.type="validation"

# Find slow searches
name="hyperdimensional.search.semantic" AND duration > 1s
```

### Prometheus (Metrics)

```promql
# Operation rate
rate(hyperdimensional_embedding_embed_command_operations_total[5m])

# Search latency (95th percentile)
histogram_quantile(0.95,
  rate(hyperdimensional_search_semantic_latency_ms_bucket[5m])
)

# Validation pass rate
rate(hyperdimensional_validation_spec_compliance_passed_total[5m])
/
rate(hyperdimensional_validation_spec_compliance_checks_total[5m])

# Average result count
rate(hyperdimensional_search_semantic_result_count_sum[5m])
/
rate(hyperdimensional_search_semantic_result_count_count[5m])
```

## Common Patterns

### Batch Embedding

```python
with track_embedding_operation("batch_embed", vector_count=len(items), dimensions=10000):
    vectors = [hde.embed_feature(item) for item in items]
```

### Search with Latency

```python
import time
start = time.perf_counter()

with track_similarity_search("find_top_k", result_count=k) as span:
    results = search_features(query, k=k)
    latency_ms = (time.perf_counter() - start) * 1000
    span.set_attribute("hd.search.latency_ms", latency_ms)
```

### Validation with Dynamic Score

```python
with track_validation_check("completeness") as span:
    score = calculate_completeness(spec)
    passed = score >= 0.80
    span.set_attribute("hd.validation.score", score)
    span.set_attribute("hd.validation.passed", passed)
```

## Error Handling

Exceptions are automatically recorded:

```python
try:
    with track_embedding_operation("risky_operation"):
        result = risky_embedding_operation()
except Exception as e:
    # Exception is recorded in span with:
    # - error: True
    # - error.type: exception class name
    # - error counter incremented
    handle_error(e)
```

## Performance

- **Overhead**: Negligible (<0.1ms per operation)
- **No OTEL**: Zero overhead (no-op)
- **Memory**: Minimal (reuses existing OTEL infrastructure)
- **Network**: Batched exports (5-second intervals)

## Examples

See `/examples/hyperdimensional_observability_demo.py` for complete examples.

## Documentation

- Full Guide: `/docs/hyperdimensional-observability.md`
- Implementation Summary: `/docs/observability-implementation-summary.md`
- Core Telemetry: `/src/specify_cli/core/telemetry.py`
