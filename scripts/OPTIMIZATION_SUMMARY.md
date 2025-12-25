# CLI Startup Optimization - Complete Analysis

## 🎯 Objective
Optimize `specify` CLI startup time from **2.825s** to **<1.5s** using advanced profiling and caching strategies.

## 📊 Profiling Results

### Current Performance
```bash
$ time uv run specify --help
real    0m2.825s
user    0m2.640s
sys     0m1.110s
```

### Import Time Breakdown
```
Total imports: 1.812s (64% of startup time)

specify_cli           1.021s  █████████████████████████████  56.4%
specify_cli.app       0.401s  ███████████                    22.1%
httpx                 0.166s  ████                            9.2%
rich.console          0.101s  ██                              5.6%
typer                 0.099s  ██                              5.5%
other                 0.024s  ▌                               1.2%
```

### Module Loading Bottlenecks
```
Module                                          Time      Issue
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
specify_cli/__init__.py                         1.695s    Legacy monolithic imports
specify_cli/cli/__init__.py                     1.060s    Banner + utils eager load
specify_cli/utils/__init__.py                   1.056s    Template utils
specify_cli/core/__init__.py                    1.037s    ALL core modules
specify_cli/core/cache.py                       0.751s    Platformdirs setup
specify_cli/core/telemetry.py                   0.739s    🔴 OTEL gRPC exporters
opentelemetry/exporter/otlp/proto/grpc/...     0.573s    🔴 Protobuf + gRPC
httpx/__init__.py                               0.314s    🟡 HTTP client
numpy/__init__.py                               0.232s    🟡 Dashboard imports
```

## 🔍 Root Causes

### 1. **Eager OTEL Initialization** (🔴 CRITICAL - 31.6% of imports)
**File**: `src/specify_cli/core/telemetry.py:111-150`

**Problem**:
```python
# Lines 111-150: Heavy imports happen immediately at module load
if not _OTEL_DISABLED:
    try:
        from opentelemetry import metrics, trace
        from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        # ... MORE HEAVY IMPORTS (~0.573s)

        # Initialization happens even when:
        # - OTEL_EXPORTER_OTLP_ENDPOINT is not set
        # - User just wants --help
        # - No spans will ever be created
```

**Impact**: **0.573s** wasted on every CLI invocation, including `--help`

### 2. **Eager Core Module Imports** (🔴 CRITICAL - 22.1%)
**File**: `src/specify_cli/core/__init__.py`

**Problem**:
```python
# Imports 286 lines of modules immediately
from .cache import cache_key, cache_stats, clear_cache, ...      # 0.751s
from .config import SpecifyConfig, env_or, ...                   # ...
from .error_handling import ConfigurationError, ...              # ...
from .git import init_git_repo, is_git_repo                      # ...
from .github import download_template_from_github, ...           # ...
from .jtbd_measurement import FeatureEffectiveness, ...          # Heavy!
from .jtbd_metrics import JobCompletion, JobStatus, ...          # Heavy!
from .process import run, run_command, run_logged, which
from .semconv import CacheAttributes, CliAttributes, ...
from .shell import colour, colour_stderr, dump_json, ...
from .telemetry import span, metric_counter, ...                 # 0.739s

# TOTAL: ~1.037s to import core module
# Used by: Simple --help command
# Actually needed: None of these modules!
```

**Impact**: **0.400s+** for importing modules never used

### 3. **httpx Module-Level Import** (🟡 HIGH - 9.2%)
**Files**:
- `src/specify_cli/__init__.py:62`
- `src/specify_cli/utils/templates.py:11`

**Problem**:
```python
# src/specify_cli/__init__.py
import httpx                              # 0.166s import
client = httpx.Client(verify=ssl_context) # Created at import time

# Used by: init command (network operations)
# Loaded for: EVERY command including --help
```

**Impact**: **0.166s**

### 4. **Optional Heavy Imports** (🟡 MEDIUM - 11%)
**Files**:
- `src/specify_cli/commands/dashboards.py` → numpy (0.232s)
- `src/specify_cli/commands/pm.py` → pm4py
- `src/specify_cli/dspy_commands.py` → dspy

**Problem**: All command modules imported at app startup

**Impact**: **~0.300s**

## ✨ Optimization Strategy

### Phase 1: Lazy OTEL Initialization (🚀 HIGHEST ROI)
**Expected Savings**: **0.573s (20% reduction)**

**Implementation**:
```python
# File: src/specify_cli/core/telemetry.py

_OTEL_INITIALIZED = False
_OTEL_AVAILABLE = False

def _ensure_otel_initialized() -> bool:
    """Initialize OTEL only when first span/metric is created."""
    global _OTEL_INITIALIZED, _OTEL_AVAILABLE
    if _OTEL_INITIALIZED:
        return _OTEL_AVAILABLE

    _OTEL_INITIALIZED = True

    try:
        # LAZY IMPORT: Load these ONLY when first span() is called
        from opentelemetry import metrics, trace
        from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
        # ... setup OTEL
        _OTEL_AVAILABLE = True
        return True
    except ImportError:
        _OTEL_AVAILABLE = False
        return False

@contextmanager
def span(name: str, **attrs):
    """Create span with lazy OTEL initialization."""
    if _ensure_otel_initialized():
        # Real OTEL span
        with _TRACER.start_as_current_span(name, **attrs) as s:
            yield s
    else:
        # No-op when OTEL unavailable
        yield None
```

**Benefits**:
- ✅ `--help` command: OTEL never loaded (0.573s saved)
- ✅ `init` command: OTEL loads on first span (same behavior)
- ✅ No API changes (backward compatible)

**Status**: ✅ Implementation ready in `telemetry_optimized.py`

### Phase 2: Lazy Core Imports (🔥 HIGH ROI)
**Expected Savings**: **0.400s (14% reduction)**

**Implementation**:
```python
# File: src/specify_cli/core/__init__.py

# Replace all direct imports with lazy loading

def __getattr__(name: str):
    """Lazy import core modules on first access."""

    # Map exports to their modules
    _MODULE_MAP = {
        "span": "telemetry",
        "metric_counter": "telemetry",
        "cache_key": "cache",
        "SpecifyConfig": "config",
        "SpecifyError": "error_handling",
        # ... full mapping
    }

    if name in _MODULE_MAP:
        module_name = _MODULE_MAP[name]
        module = __import__(f"specify_cli.core.{module_name}", fromlist=[name])
        value = getattr(module, name)
        globals()[name] = value  # Cache for subsequent access
        return value

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
```

**Benefits**:
- ✅ Only loads modules actually used
- ✅ One-time cost on first access
- ✅ Cached in globals() for speed

### Phase 3: Lazy httpx (⚡ MEDIUM ROI)
**Expected Savings**: **0.166s (6% reduction)**

**Implementation**:
```python
# Before (src/specify_cli/__init__.py:62)
import httpx
client = httpx.Client(verify=ssl_context)

# After: Move inside init() function
def init(...):
    import httpx  # Lazy import
    client = httpx.Client(verify=ssl_context)
    # ... use client
```

### Phase 4: Lazy Commands (⚡ MEDIUM ROI)
**Expected Savings**: **0.300s (11% reduction)**

**Implementation**: Use Typer's callback mechanism for lazy loading

### Phase 5: functools.lru_cache (💎 LOW ROI)
**Expected Savings**: **0.050s (2% reduction)**

**Implementation**: Add `@lru_cache` to pure functions

## 📈 Expected Results

### Performance Projections
```
Optimization                 Savings    % Reduction
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Lazy OTEL                    0.573s     20%
Lazy Core                    0.400s     14%
Lazy httpx                   0.166s      6%
Lazy Commands                0.300s     11%
functools.lru_cache          0.050s      2%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOTAL SAVINGS                1.489s     51%

Baseline:    2.825s
Optimized:   1.336s  ✅ (meets <1.5s target)
```

### Before/After Comparison
```
Command: specify --help

BEFORE (current)                 AFTER (optimized)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Import specify_cli    1.695s     Import specify_cli     0.200s ⚡
  └─ core             1.037s       └─ core (lazy)       0.000s ⚡
     └─ telemetry     0.739s          └─ telemetry      0.000s ⚡
        └─ OTEL grpc  0.573s             └─ OTEL        NOT LOADED ⚡
  └─ httpx            0.166s       └─ httpx             NOT LOADED ⚡
  └─ commands         0.300s       └─ commands (lazy)   0.000s ⚡
Other Python          1.130s     Other Python           1.136s

TOTAL: 2.825s                    TOTAL: 1.336s (-53%)
```

## 🛠️ Implementation Files

### Created Files
```
scripts/
├── profile_cli_startup.py          # cProfile profiling script
├── analyze_imports.py               # Import time analysis
├── apply_optimizations.py           # Optimization application script
├── verify_optimizations.sh          # Verification and benchmarking
├── optimize_cli_startup.md          # Detailed optimization guide
├── OPTIMIZATION_REPORT.md           # Full technical report
└── OPTIMIZATION_SUMMARY.md          # This file

src/specify_cli/core/
└── telemetry_optimized.py          # ✅ Ready to deploy (lazy OTEL)
```

### Files to Modify (Manual Patches Required)
```
1. src/specify_cli/core/telemetry.py       # Replace with telemetry_optimized.py
2. src/specify_cli/core/__init__.py        # Add __getattr__ lazy loading
3. src/specify_cli/__init__.py             # Remove eager httpx import
4. src/specify_cli/utils/templates.py      # Lazy httpx import
5. src/specify_cli/app.py                  # Lazy command loading
```

## 🚀 Quick Start Guide

### 1. Review Analysis
```bash
# View profiling results
cat scripts/OPTIMIZATION_REPORT.md

# View import analysis
python3 scripts/analyze_imports.py
```

### 2. Apply Phase 1 (Lazy OTEL)
```bash
# Backup original
cp src/specify_cli/core/telemetry.py src/specify_cli/core/telemetry.py.bak

# Apply optimized version
cp src/specify_cli/core/telemetry_optimized.py src/specify_cli/core/telemetry.py

# Run tests
uv run pytest tests/

# Benchmark
time uv run specify --help  # Should be ~2.25s (0.573s saved)
```

### 3. Verify
```bash
# Run full verification suite
./scripts/verify_optimizations.sh
```

### 4. Apply Remaining Phases
See `scripts/optimize_cli_startup.md` for detailed implementation of phases 2-5.

## 📋 Testing Strategy

### Performance Tests
```bash
# Baseline
for i in {1..10}; do time uv run specify --help 2>&1; done | grep real

# With optimizations
for i in {1..10}; do time uv run specify --help 2>&1; done | grep real
```

### Functional Tests
```bash
# All existing tests must pass
uv run pytest tests/ -v

# OTEL still works when configured
export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317"
uv run specify init test-project --ai claude
```

## 🎯 Success Criteria

- [x] Profiling analysis complete
- [x] Bottlenecks identified and documented
- [x] Optimization strategy created
- [x] Phase 1 implementation ready (lazy OTEL)
- [ ] All phases implemented
- [ ] `specify --help` runs in <1.5s
- [ ] All tests pass
- [ ] No API breakage
- [ ] Memory usage <100MB

## 📚 Key Learnings

### Import Time Matters
- 64% of startup time is imports
- Module-level code executes on every import
- Lazy loading is essential for CLI tools

### OTEL is Heavy
- gRPC exporters: 0.573s (20% of total time!)
- Only needed when actively tracing
- Perfect candidate for lazy initialization

### Typer Best Practices
- Don't import all commands at startup
- Use callbacks for lazy loading
- Keep entry point minimal

### Python Import System
- `__getattr__` enables lazy module loading
- functools.lru_cache speeds up repeated calls
- importlib.util.find_spec checks without importing

## 🔗 References

- cProfile documentation: https://docs.python.org/3/library/profile.html
- PEP 690 (Lazy Imports): https://peps.python.org/pep-0690/
- OTEL Python SDK: https://opentelemetry.io/docs/languages/python/
- Typer documentation: https://typer.tiangolo.com/

## 📝 Notes

- **Profiling date**: 2025-12-25
- **Python version**: 3.11
- **Platform**: Linux 4.4.0
- **Baseline measurement**: Average of 5 runs
- **Analysis tool**: cProfile + pstats + custom scripts

---

**Next Steps**: Apply Phase 1 (Lazy OTEL) and verify 0.573s improvement! 🚀
