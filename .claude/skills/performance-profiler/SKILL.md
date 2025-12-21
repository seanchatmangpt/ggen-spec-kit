---
name: performance-profiler
description: Profile and optimize application performance using traces and metrics. Use when measuring execution time, identifying bottlenecks, or optimizing slow operations.
allowed-tools: Read, Glob, Grep, Bash, LSP
---

# Performance Profiler

Profile performance, identify bottlenecks, and recommend optimizations.

## Instructions

1. Measure execution time and resources
2. Find slow operations
3. Recommend improvements
4. Create benchmarks
5. Set up monitoring

## Performance Targets

- **Command startup**: < 500ms
- **Simple operations**: < 100ms
- **Complex transformations**: < 5s
- **Memory usage**: < 100MB

## Profiling Commands

```bash
# Time a command
time specify check

# Profile with cProfile
uv run python -m cProfile -s cumtime -m specify_cli check

# Memory profiling
uv pip install memory_profiler
uv run python -m memory_profiler script.py
```

## Benchmarking

```bash
# Install hyperfine
brew install hyperfine

# Benchmark CLI
hyperfine --warmup 3 'specify check'

# Compare implementations
hyperfine 'specify check' 'python old_check.py'
```

## Common Bottlenecks

### Subprocess Overhead
```python
# ❌ Multiple calls
for file in files:
    subprocess.run(["process", file])

# ✅ Batch
subprocess.run(["process", *files])
```

### Synchronous I/O
```python
# ❌ Sequential
for url in urls:
    download(url)

# ✅ Concurrent
import asyncio
await asyncio.gather(*[download(u) for u in urls])
```

### String Concatenation
```python
# ❌ O(n²)
result = ""
for item in items:
    result += str(item)

# ✅ O(n)
result = "".join(str(item) for item in items)
```

## Optimization Strategies

1. **Lazy Loading**: Import heavy modules when needed
2. **Caching**: Use `@lru_cache` for repeated calls
3. **Parallelism**: `ThreadPoolExecutor` for I/O
4. **Generators**: Yield instead of building lists

## Output Format

```markdown
## Performance Profile Report

### Timing Summary
| Metric | Value |
|--------|-------|
| Startup | 245ms |
| Execution | 380ms |
| Total | 625ms |

### Hotspots
| Function | Time | % Total |
|----------|------|---------|
| subprocess.run | 180ms | 29% |

### Bottlenecks
1. **Subprocess overhead** - Batch into single call

### Recommendations
1. Batch calls: -150ms estimated
```
