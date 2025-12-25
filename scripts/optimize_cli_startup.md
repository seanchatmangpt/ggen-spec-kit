# CLI Startup Optimization Analysis

## Current Performance
- **Baseline**: 2.825s for `specify --help`
- **Import time**: 1.812s (63% of total time)
- **Target**: <1.5s

## Key Bottlenecks Identified

### 1. OpenTelemetry Initialization (0.573s - 31.6% of imports)
**Problem**: OTEL imports grpc exporters at module import time, even when OTEL_EXPORTER_OTLP_ENDPOINT is not set.

**Location**: `src/specify_cli/core/telemetry.py:111-150`

**Solution**: Lazy initialization - only load OTEL when first span is created.

### 2. Eager Core Imports (1.037s - 57.2% of imports)
**Problem**: `src/specify_cli/core/__init__.py` imports ALL core modules at once, including heavy JTBD metrics and GitHub operations.

**Solution**: Remove eager imports from `__init__.py`, use lazy imports via `__getattr__`.

### 3. specify_cli Module (1.021s - 56.4% of imports)
**Problem**: `src/specify_cli/__init__.py` has massive imports from old monolithic module.

**Solution**: Clean up __init__.py, remove legacy imports.

### 4. httpx Import (0.166s - 9.2% of imports)
**Problem**: httpx imported at module level in templates.py and __init__.py.

**Solution**: Lazy import httpx only when making HTTP requests.

### 5. Optional Heavy Imports
**Problem**: numpy, dashboards, pm4py all loaded even for simple commands like `--help`.

**Solution**: Lazy command loading - only import commands when invoked.

## Optimization Patches

### Patch 1: Lazy OTEL Initialization
```python
# Before: telemetry.py lines 111-150 (immediate init)
# After: Lazy initialization on first use

_OTEL_INITIALIZED = False
_TRACER = None
_METER = None

def _ensure_otel_initialized():
    """Initialize OTEL on first use."""
    global _OTEL_INITIALIZED, _TRACER, _METER
    if _OTEL_INITIALIZED:
        return
    _OTEL_INITIALIZED = True

    # Load heavy imports only when needed
    from opentelemetry import metrics, trace
    from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
    # ... rest of initialization
```

### Patch 2: Lazy Core Module Imports
```python
# src/specify_cli/core/__init__.py
# Replace all direct imports with __getattr__ lazy loading

def __getattr__(name: str):
    """Lazy import core modules."""
    if name in ("span", "metric_counter", "metric_histogram", "record_exception"):
        from .telemetry import name
        return name
    elif name in ("cache_key", "get_cached", "set_cached"):
        from .cache import name
        return name
    # ... etc
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
```

### Patch 3: Lazy httpx Import
```python
# src/specify_cli/utils/templates.py
# Move httpx import inside functions

def download_and_extract_template(...):
    import httpx  # Lazy import
    # ... rest of function
```

### Patch 4: Command Lazy Loading
```python
# src/specify_cli/app.py
# Use Typer's lazy command loading

@app.command(lazy_subcommands=True)
def command():
    # Only import when invoked
    from .commands.subcommand import handler
    return handler()
```

## Expected Improvements

| Optimization | Time Saved | % Reduction |
|--------------|------------|-------------|
| Lazy OTEL    | ~0.573s    | 20%         |
| Lazy Core    | ~0.400s    | 14%         |
| Lazy httpx   | ~0.166s    | 6%          |
| Lazy Commands| ~0.300s    | 11%         |
| **TOTAL**    | **~1.44s** | **51%**     |

**Projected Time**: 2.825s - 1.44s = **1.385s** ✓ (meets <1.5s target)

## Implementation Priority

1. **HIGH**: Lazy OTEL (biggest impact, 20% reduction)
2. **HIGH**: Lazy Core imports (14% reduction)
3. **MEDIUM**: Lazy httpx (6% reduction)
4. **MEDIUM**: Lazy Commands (11% reduction)
5. **LOW**: functools.lru_cache on pure functions (marginal)

## Additional Optimizations

### Memory Caching
- Add `@lru_cache(maxsize=128)` to pure functions
- Cache module lookups
- Use `__slots__` for dataclasses

### Code Generation Caching
- Cache compiled regex patterns
- Pre-compile template strings
- Cache platformdirs results

### Deferred Rich Initialization
- Don't create Console objects at import time
- Lazy-load Rich components (Table, Panel, etc.)
