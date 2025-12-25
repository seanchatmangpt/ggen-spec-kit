# CLI Startup Optimization Report

## Executive Summary

**Current Performance**: 2.825s for `specify --help`
**Target Performance**: <1.5s
**Identified Savings**: ~1.44s (51% reduction)
**Projected Performance**: ~1.38s ✅

## Profiling Results

### Import Time Analysis

Total import time: **1.812s (64% of startup time)**

| Module | Time (s) | % of Total | Category |
|--------|----------|------------|----------|
| specify_cli | 1.021 | 56.4% | 🔴 Critical |
| specify_cli.app | 0.401 | 22.1% | 🔴 Critical |
| httpx | 0.166 | 9.2% | 🟡 High |
| rich.console | 0.101 | 5.6% | 🟢 Medium |
| typer | 0.099 | 5.5% | 🟢 Medium |

### Module-Level Bottlenecks

| Module | Time (s) | Issue |
|--------|----------|-------|
| `specify_cli/__init__.py` | 1.695 | Legacy monolithic imports |
| `specify_cli/cli/__init__.py` | 1.060 | Banner group imports |
| `specify_cli/utils/__init__.py` | 1.056 | Template utils eager load |
| `specify_cli/core/__init__.py` | 1.037 | ALL core modules imported |
| `specify_cli/core/cache.py` | 0.751 | Platformdirs + setup |
| `specify_cli/core/telemetry.py` | 0.739 | OTEL gRPC exporters |
| OTEL grpc exporters | 0.573 | Heavy protobuf/grpc |
| httpx | 0.314 | HTTP client at module level |
| numpy | 0.232 | Dashboard imports |

### cProfile Top Functions

**By Total Time**:
1. `posix.stat` - 0.669s (file system operations during import discovery)
2. `io.open_code` - 0.231s (opening .pyc files)
3. `marshal.loads` - 0.129s (loading bytecode)

**By Cumulative Time**:
1. `__import__` - 2.007s (module loading)
2. `specify_cli.__init__.<module>` - 1.695s
3. `specify_cli.cli.__init__.<module>` - 1.060s

## Root Cause Analysis

### 1. Eager OTEL Initialization (HIGH IMPACT)
**Location**: `src/specify_cli/core/telemetry.py:111-150`

**Problem**:
```python
# Lines 111-150: Imports immediately at module load
from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
# ... ~0.573s of gRPC/protobuf imports
```

Even when:
- OTEL_EXPORTER_OTLP_ENDPOINT is not set
- User just wants `--help`
- No spans/metrics will be created

**Impact**: 0.573s (31.6% of import time)

**Solution**: Lazy initialization - defer all OTEL imports until first `span()` or `metric_counter()` call.

### 2. Eager Core Module Imports (HIGH IMPACT)
**Location**: `src/specify_cli/core/__init__.py`

**Problem**:
```python
# Imports EVERYTHING immediately
from .cache import cache_key, cache_stats, clear_cache, ...
from .config import SpecifyConfig, env_or, get_cache_dir, ...
from .error_handling import ConfigurationError, ErrorCategory, ...
from .git import init_git_repo, is_git_repo
from .github import _github_auth_headers, download_template_from_github, ...
from .jtbd_measurement import FeatureEffectiveness, JTBDMetrics, ...
from .jtbd_metrics import JobCompletion, JobStatus, ...
# ... 286 lines of imports
```

Most of these are never used for simple commands like `--help`.

**Impact**: ~0.400s

**Solution**: Implement `__getattr__` for lazy module loading.

### 3. httpx at Module Level (MEDIUM IMPACT)
**Location**: Multiple files

**Problem**:
```python
# src/specify_cli/__init__.py:62
import httpx
client = httpx.Client(verify=ssl_context)  # Created at import time

# src/specify_cli/utils/templates.py:11
import httpx  # Loaded even for non-network commands
```

**Impact**: 0.166s

**Solution**: Import httpx only inside functions that need it.

### 4. Optional Heavy Imports (MEDIUM IMPACT)
**Locations**:
- `src/specify_cli/commands/dashboards.py` → numpy (0.232s)
- `src/specify_cli/commands/pm.py` → pm4py
- `src/specify_cli/dspy_commands.py` → dspy

**Problem**: All command modules imported at startup, even optional ones.

**Impact**: ~0.300s

**Solution**: Lazy command loading via Typer.

## Optimization Strategy

### Phase 1: Lazy OTEL (Highest ROI) 🚀

**File**: `src/specify_cli/core/telemetry.py`

**Changes**:
1. Move OTEL imports inside `_ensure_otel_initialized()` function
2. Call lazy init on first `span()` / `metric_counter()` / `metric_histogram()` use
3. Cache initialization state in global `_OTEL_INITIALIZED`

**Expected Savings**: **0.573s (20%)**

**Implementation**:
```python
_OTEL_INITIALIZED = False

def _ensure_otel_initialized() -> bool:
    global _OTEL_INITIALIZED
    if _OTEL_INITIALIZED:
        return True
    _OTEL_INITIALIZED = True

    try:
        # Lazy imports here
        from opentelemetry import metrics, trace
        from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
        # ... setup
        return True
    except ImportError:
        return False

@contextmanager
def span(name: str, **attrs):
    if _ensure_otel_initialized():
        # Real implementation
    else:
        # No-op
        yield None
```

**Risk**: Low - identical API, backward compatible

### Phase 2: Lazy Core Imports (High ROI) 🔥

**File**: `src/specify_cli/core/__init__.py`

**Changes**:
1. Remove all direct imports
2. Implement `__getattr__` for lazy loading
3. Cache loaded modules in globals()

**Expected Savings**: **0.400s (14%)**

**Implementation**:
```python
_LAZY_MODULES = {
    "span": "telemetry",
    "cache_key": "cache",
    "SpecifyConfig": "config",
    # ... full mapping
}

def __getattr__(name: str):
    if name in _LAZY_MODULES:
        module_name = _LAZY_MODULES[name]
        module = __import__(f"specify_cli.core.{module_name}", fromlist=[name])
        value = getattr(module, name)
        globals()[name] = value  # Cache
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
```

**Risk**: Medium - requires testing all import paths

### Phase 3: Lazy httpx (Medium ROI) ⚡

**Files**:
- `src/specify_cli/__init__.py`
- `src/specify_cli/utils/templates.py`
- `src/specify_cli/core/github.py`

**Changes**:
1. Remove module-level `import httpx`
2. Import inside functions that use it
3. Remove module-level `httpx.Client()` creation

**Expected Savings**: **0.166s (6%)**

**Implementation**:
```python
# Before
import httpx
client = httpx.Client()

# After
def download_template(...):
    import httpx  # Lazy
    client = httpx.Client()
    # ... use client
```

**Risk**: Low - straightforward refactor

### Phase 4: Lazy Commands (Medium ROI) ⚡

**File**: `src/specify_cli/app.py`

**Changes**:
1. Don't import all command modules at startup
2. Use Typer's callback mechanism for lazy loading
3. Import command modules only when invoked

**Expected Savings**: **0.300s (11%)**

**Risk**: Medium - requires Typer 0.9+ features

### Phase 5: functools.lru_cache (Low ROI)

**Files**: Various pure functions

**Changes**:
1. Add `@lru_cache(maxsize=128)` to pure functions
2. Cache `platformdirs.user_cache_dir()` results
3. Cache compiled regex patterns

**Expected Savings**: **0.050s (2%)**

**Risk**: Low - pure functions only

## Implementation Plan

### Week 1: Phase 1 - Lazy OTEL
- [x] Profile current startup time
- [x] Create optimized telemetry.py
- [ ] Replace telemetry.py with optimized version
- [ ] Run test suite
- [ ] Benchmark improvement

### Week 2: Phase 2 - Lazy Core
- [ ] Create __getattr__ implementation
- [ ] Map all exports to modules
- [ ] Replace __init__.py
- [ ] Test all import paths
- [ ] Benchmark improvement

### Week 3: Phases 3-5
- [ ] Lazy httpx imports
- [ ] Lazy command loading
- [ ] Add lru_cache decorators
- [ ] Final benchmarking

## Success Criteria

- ✅ `specify --help` runs in <1.5s
- ✅ All existing tests pass
- ✅ No API changes (backward compatible)
- ✅ OTEL still works when endpoint configured
- ✅ Memory usage stays <100MB

## Benchmark Commands

```bash
# Baseline
time uv run specify --help

# With profiling
python3 -m cProfile -o /tmp/cli.prof $(which specify) --help
python3 -c "import pstats; pstats.Stats('/tmp/cli.prof').sort_stats('cumulative').print_stats(30)"

# Import analysis
python3 scripts/analyze_imports.py

# Memory profiling
python3 -m memory_profiler $(which specify) --help
```

## Files to Modify

1. ✅ `src/specify_cli/core/telemetry.py` - Lazy OTEL init
2. ⬜ `src/specify_cli/core/__init__.py` - Lazy core imports
3. ⬜ `src/specify_cli/__init__.py` - Remove legacy imports
4. ⬜ `src/specify_cli/utils/templates.py` - Lazy httpx
5. ⬜ `src/specify_cli/core/github.py` - Lazy httpx
6. ⬜ `src/specify_cli/app.py` - Lazy commands

## Testing Strategy

### Unit Tests
- All existing tests must pass
- Add test for lazy OTEL initialization
- Add test for lazy core imports

### Integration Tests
- Test `specify --help` (no OTEL load)
- Test `specify init` (OTEL should load)
- Test with OTEL_EXPORTER_OTLP_ENDPOINT set

### Performance Tests
```python
def test_startup_time():
    """Ensure CLI starts in <1.5s."""
    import subprocess
    import time

    start = time.perf_counter()
    subprocess.run(["specify", "--help"], capture_output=True)
    elapsed = time.perf_counter() - start

    assert elapsed < 1.5, f"Startup took {elapsed:.3f}s > 1.5s"
```

## Rollback Plan

If optimizations cause issues:
1. Revert telemetry.py to original
2. Revert core/__init__.py to original
3. Deploy emergency patch
4. Investigate failures in dev environment

## Future Optimizations

### Beyond 1.5s Target

1. **Pre-compiled bytecode**: Ship .pyc files in wheel
2. **Lazy Rich imports**: Defer Rich components
3. **Import caching**: Cache import paths
4. **C extensions**: Rewrite hot paths in Cython
5. **Startup script**: Preload common paths

### Memory Optimizations

1. Use `__slots__` for dataclasses
2. Implement `__del__` for cleanup
3. Use weakref for caches
4. Clear import cache after startup

## References

- Python lazy imports: PEP 690
- Typer lazy subcommands: https://typer.tiangolo.com/
- OTEL Python SDK: https://opentelemetry.io/docs/languages/python/
- Profile optimization: https://docs.python.org/3/library/profile.html
