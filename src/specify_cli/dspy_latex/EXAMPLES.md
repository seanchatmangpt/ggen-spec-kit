# LaTeX PDF Compilation Engine - Examples

This document provides comprehensive examples of using the multi-stage PDF compilation engine.

## Table of Contents

1. [Basic Usage](#basic-usage)
2. [Error Recovery](#error-recovery)
3. [Incremental Compilation](#incremental-compilation)
4. [Custom Backends](#custom-backends)
5. [Advanced Features](#advanced-features)
6. [Integration Examples](#integration-examples)

---

## Basic Usage

### Simple Compilation

```python
from pathlib import Path
from specify_cli.dspy_latex import PDFCompiler

# Create compiler with default settings (pdflatex)
compiler = PDFCompiler()

# Compile a LaTeX document
result = compiler.compile(Path("document.tex"))

# Check result
if result.success:
    print(f"✓ PDF created: {result.pdf_path}")
    print(f"  Duration: {result.total_duration:.2f}s")
    print(f"  Size: {result.metrics['pdf_size'] / 1024:.1f} KB")
else:
    print("✗ Compilation failed")
    for error in result.errors:
        print(f"  Error at line {error.line}: {error.message}")
```

### With Progress Tracking

```python
from specify_cli.dspy_latex import PDFCompiler, StageType

compiler = PDFCompiler()
result = compiler.compile(Path("thesis.tex"))

# Show stage-by-stage progress
for stage, stage_result in result.stage_results.items():
    status = "✓" if stage_result.success else "✗"
    print(f"{status} {stage.value:12s} {stage_result.duration:.2f}s")

# Example output:
# ✓ normalize    0.05s
# ✓ preprocess   0.12s
# ✓ compile      2.34s
# ✓ postprocess  0.87s
# ✓ optimize     0.45s
```

---

## Error Recovery

### Autonomous Error Fixing

```python
from specify_cli.dspy_latex import PDFCompiler

# Enable error recovery with retries
compiler = PDFCompiler(
    enable_recovery=True,
    max_retries=3
)

result = compiler.compile(Path("buggy_document.tex"))

# Check what errors were encountered and fixed
for error in result.errors:
    print(f"Error: {error.message}")
    if error.suggestion:
        print(f"  Suggestion: {error.suggestion}")
    if error.fix_applied:
        print(f"  ✓ Auto-fixed: {error.fix_applied}")
```

### Custom Error Recovery

```python
from specify_cli.dspy_latex import (
    PDFCompiler,
    ErrorRecovery,
    LaTeXError,
    ErrorSeverity
)

# Create custom error recovery
recovery = ErrorRecovery(enable_dspy=True, max_fix_attempts=5)

# Diagnose errors
errors = [
    LaTeXError(
        severity=ErrorSeverity.ERROR,
        message="Undefined control sequence \\mycustomcommand",
        line=42
    )
]

diagnosed = recovery.diagnose(errors, context={})
for error in diagnosed:
    print(f"Suggestion: {error.suggestion}")

# Attempt fixes
success, fixes = recovery.attempt_fix(diagnosed, context={})
print(f"Fixes applied: {fixes}")
```

---

## Incremental Compilation

### Using Cache for Fast Rebuilds

```python
from specify_cli.dspy_latex import PDFCompiler, CompilationCache
from pathlib import Path

# Create persistent cache
cache = CompilationCache(
    cache_dir=Path(".latex_cache"),
    max_cache_size=1000  # MB
)

# Create compiler with cache
compiler = PDFCompiler(cache=cache)

# First compilation (full)
result1 = compiler.compile(Path("thesis.tex"))
print(f"First compile: {result1.total_duration:.2f}s")

# Second compilation (cached)
result2 = compiler.compile(Path("thesis.tex"))
print(f"Cached compile: {result2.total_duration:.2f}s")
print(f"Speedup: {result1.total_duration / result2.total_duration:.1f}x")

# Force recompilation
result3 = compiler.compile(Path("thesis.tex"), force=True)
print(f"Forced recompile: {result3.total_duration:.2f}s")
```

### Cache Management

```python
from specify_cli.dspy_latex import CompilationCache

cache = CompilationCache()

# Get cache statistics
print(f"Cache directory: {cache.cache_dir}")
print(f"Max size: {cache.max_cache_size / (1024**2):.0f} MB")
print(f"Entries: {len(cache.index)}")

# Invalidate specific entry
cache.invalidate("abc123...")

# Clear all cache
for key in list(cache.index.keys()):
    cache.invalidate(key)
```

---

## Custom Backends

### XeLaTeX for Unicode Support

```python
from specify_cli.dspy_latex import PDFCompiler, CompilationBackend

# Use XeLaTeX for Unicode documents
compiler = PDFCompiler(backend=CompilationBackend.XELATEX)

result = compiler.compile(Path("unicode_document.tex"))
```

### LuaLaTeX for Advanced Typography

```python
from specify_cli.dspy_latex import PDFCompiler, CompilationBackend

# Use LuaLaTeX
compiler = PDFCompiler(backend=CompilationBackend.LUALATEX)

result = compiler.compile(Path("complex_typography.tex"))
```

### Automatic Backend Selection

```python
from specify_cli.dspy_latex import PDFCompiler, CompilationBackend
from pathlib import Path

def smart_compile(tex_file: Path):
    """Choose backend based on document content."""
    content = tex_file.read_text()
    
    # Check for Unicode requirements
    if "\\usepackage{fontspec}" in content or "\\usepackage{polyglossia}" in content:
        backend = CompilationBackend.XELATEX
    # Check for LuaTeX-specific packages
    elif "\\usepackage{luacode}" in content:
        backend = CompilationBackend.LUALATEX
    else:
        backend = CompilationBackend.PDFLATEX
    
    compiler = PDFCompiler(backend=backend)
    return compiler.compile(tex_file)

result = smart_compile(Path("auto_detect.tex"))
print(f"Used backend: {result.backend.value}")
```

---

## Advanced Features

### PDF Optimization

```python
from specify_cli.dspy_latex import PDFCompiler

# Enable PDF compression
compiler = PDFCompiler(compress_pdf=True)

result = compiler.compile(Path("large_document.tex"))

if result.success:
    original_size = result.metrics.get("original_size", 0)
    compressed_size = result.metrics["pdf_size"]
    compression = result.metrics["compression_ratio"]
    
    print(f"Original size: {original_size / 1024:.1f} KB")
    print(f"Compressed size: {compressed_size / 1024:.1f} KB")
    print(f"Compression: {(1 - compression) * 100:.1f}% reduction")
```

### Receipt Generation (Reproducibility)

```python
from specify_cli.dspy_latex import PDFCompiler
import json

compiler = PDFCompiler()
result = compiler.compile(Path("document.tex"))

# Load receipt
if result.receipt_path:
    receipt = json.loads(result.receipt_path.read_text())
    
    print("Cryptographic Receipt:")
    print(f"  Input hash:  {receipt['input_hash'][:16]}...")
    print(f"  Output hash: {receipt['output_hash'][:16]}...")
    print(f"  Timestamp:   {receipt['timestamp']}")
    print(f"  Backend:     {receipt['backend']}")
    
    # Verify reproducibility
    print("\nStage Hashes:")
    for stage, hashes in receipt['stages'].items():
        print(f"  {stage:12s} {hashes['output_hash'][:16]}...")
```

### Metrics Collection

```python
from specify_cli.dspy_latex import PDFCompiler, CompilationMetrics

compiler = PDFCompiler()
result = compiler.compile(Path("document.tex"))

# Access detailed metrics
metrics = CompilationMetrics(**result.metrics)

print("Compilation Metrics:")
print(f"  Total duration: {metrics.total_duration:.2f}s")
print(f"  Errors: {metrics.error_count}")
print(f"  Warnings: {metrics.warning_count}")
print(f"  PDF size: {metrics.pdf_size / 1024:.1f} KB")
print(f"  Cache hits: {metrics.cache_hits}")
print(f"  Cache misses: {metrics.cache_misses}")
print(f"  Attempts: {metrics.attempts}")

print("\nStage Durations:")
for stage, duration in metrics.stage_durations.items():
    pct = (duration / metrics.total_duration) * 100
    print(f"  {stage.value:12s} {duration:5.2f}s ({pct:4.1f}%)")
```

---

## Integration Examples

### Batch Compilation

```python
from specify_cli.dspy_latex import PDFCompiler, CompilationCache
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

def compile_batch(tex_files: list[Path], max_workers: int = 4):
    """Compile multiple documents in parallel."""
    cache = CompilationCache()
    
    def compile_one(tex_file: Path):
        compiler = PDFCompiler(cache=cache)
        return tex_file, compiler.compile(tex_file)
    
    results = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(compile_one, f): f for f in tex_files}
        
        for future in as_completed(futures):
            tex_file, result = future.result()
            results[tex_file] = result
            
            status = "✓" if result.success else "✗"
            print(f"{status} {tex_file.name:30s} {result.total_duration:.2f}s")
    
    return results

# Compile all .tex files in directory
tex_files = list(Path("papers/").glob("*.tex"))
results = compile_batch(tex_files)

# Summary
success_count = sum(1 for r in results.values() if r.success)
print(f"\nCompiled {success_count}/{len(results)} documents successfully")
```

### CI/CD Integration

```python
from specify_cli.dspy_latex import PDFCompiler
from pathlib import Path
import sys

def ci_compile(tex_file: Path) -> int:
    """Compile for CI/CD pipeline with exit code."""
    compiler = PDFCompiler(
        enable_recovery=True,
        max_retries=3,
        compress_pdf=True
    )
    
    result = compiler.compile(tex_file)
    
    if result.success:
        print(f"✓ PDF created: {result.pdf_path}")
        print(f"  Duration: {result.total_duration:.2f}s")
        print(f"  Warnings: {len(result.warnings)}")
        
        # Fail on warnings in strict mode
        if result.warnings and sys.argv.count("--strict"):
            print("✗ Warnings present in strict mode")
            return 1
        
        return 0
    else:
        print(f"✗ Compilation failed")
        for error in result.errors:
            print(f"  {error.severity.value.upper()}: {error.message}")
            if error.line:
                print(f"    at line {error.line}")
        return 1

# Usage in CI
if __name__ == "__main__":
    tex_file = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("document.tex")
    sys.exit(ci_compile(tex_file))
```

### Watch Mode (Auto-Recompile)

```python
from specify_cli.dspy_latex import PDFCompiler, CompilationCache
from pathlib import Path
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class LaTeXWatcher(FileSystemEventHandler):
    """Auto-recompile on file changes."""
    
    def __init__(self, tex_file: Path):
        self.tex_file = tex_file
        self.cache = CompilationCache()
        self.compiler = PDFCompiler(cache=self.cache)
        self.last_compile = 0
        
    def on_modified(self, event):
        # Debounce: wait 1s between compilations
        if time.time() - self.last_compile < 1:
            return
        
        if event.src_path.endswith(".tex"):
            print(f"\n{time.strftime('%H:%M:%S')} - File changed, recompiling...")
            self.last_compile = time.time()
            
            result = self.compiler.compile(self.tex_file)
            
            if result.success:
                print(f"✓ Compiled in {result.total_duration:.2f}s")
            else:
                print(f"✗ Compilation failed ({len(result.errors)} errors)")

def watch_and_compile(tex_file: Path):
    """Watch LaTeX file and auto-recompile on changes."""
    watcher = LaTeXWatcher(tex_file)
    observer = Observer()
    observer.schedule(watcher, str(tex_file.parent), recursive=False)
    observer.start()
    
    print(f"Watching {tex_file} for changes... (Ctrl+C to stop)")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

# Usage
watch_and_compile(Path("document.tex"))
```

### DSPy-Powered Error Diagnosis (Future)

```python
# Placeholder for future DSPy integration

from specify_cli.dspy_latex import PDFCompiler, ErrorRecovery

# When DSPy is fully integrated:
compiler = PDFCompiler(enable_recovery=True)
compiler.error_recovery = ErrorRecovery(enable_dspy=True)

# DSPy will:
# 1. Analyze LaTeX errors with LLM
# 2. Suggest context-aware fixes
# 3. Learn from successful recoveries
# 4. Optimize fix strategies over time

result = compiler.compile(Path("complex_error.tex"))

# DSPy-suggested fixes will appear in error.suggestion
for error in result.errors:
    if error.suggestion:
        print(f"AI-suggested fix: {error.suggestion}")
```

---

## Performance Tips

### 1. Use Caching for Large Projects

```python
# DO: Use persistent cache
cache = CompilationCache(cache_dir=Path(".cache"))
compiler = PDFCompiler(cache=cache)

# DON'T: Recreate compiler each time
for file in files:
    compiler = PDFCompiler()  # ✗ No cache reuse
    result = compiler.compile(file)
```

### 2. Enable Incremental Compilation

```python
# For multi-chapter books
compiler = PDFCompiler(cache=CompilationCache())

# Compile individual chapters
for chapter in Path("chapters/").glob("chapter*.tex"):
    result = compiler.compile(chapter)  # Cached if unchanged
```

### 3. Choose the Right Backend

```python
# PDFLaTeX: Fastest for simple documents
# XeLaTeX: Unicode support, slightly slower
# LuaLaTeX: Most features, slowest

# For speed-critical builds
compiler = PDFCompiler(backend=CompilationBackend.PDFLATEX)
```

---

## Troubleshooting

### Common Issues

**Issue: "Backend not found in PATH"**
```python
# Solution: Check backend availability
from specify_cli.core.process import which

backends = ["pdflatex", "xelatex", "lualatex"]
for backend in backends:
    path = which(backend)
    print(f"{backend:10s} {'✓' if path else '✗'} {path or 'not found'}")
```

**Issue: "Package not found"**
```python
# Solution: Auto-install via recovery
compiler = PDFCompiler(enable_recovery=True)
result = compiler.compile(Path("document.tex"))
# Will attempt to install missing packages via tlmgr
```

**Issue: "Cache growing too large"**
```python
# Solution: Limit cache size
cache = CompilationCache(max_cache_size=500)  # 500 MB limit

# Or clear periodically
if cache_dir.stat().st_size > 1_000_000_000:  # 1 GB
    for key in list(cache.index.keys()):
        cache.invalidate(key)
```

---

## Complete Example: Academic Thesis

```python
from specify_cli.dspy_latex import (
    PDFCompiler,
    CompilationCache,
    CompilationBackend,
    CompilationMetrics
)
from pathlib import Path
import json

def compile_thesis(main_file: Path, output_dir: Path):
    """
    Compile academic thesis with full pipeline:
    - Caching for incremental builds
    - XeLaTeX for Unicode
    - PDF optimization
    - Receipt generation
    - Comprehensive metrics
    """
    
    # Setup cache
    cache = CompilationCache(
        cache_dir=output_dir / ".cache",
        max_cache_size=2000  # 2 GB
    )
    
    # Configure compiler
    compiler = PDFCompiler(
        backend=CompilationBackend.XELATEX,  # Unicode support
        enable_recovery=True,
        max_retries=3,
        cache=cache,
        compress_pdf=True,
        output_dir=output_dir
    )
    
    # Compile
    print(f"Compiling {main_file.name}...")
    result = compiler.compile(main_file)
    
    if not result.success:
        print("\n✗ Compilation failed!")
        print(f"  Errors: {len(result.errors)}")
        for i, error in enumerate(result.errors[:5], 1):  # Show first 5
            print(f"\n  Error {i}:")
            print(f"    {error.message}")
            if error.line:
                print(f"    at line {error.line}")
            if error.suggestion:
                print(f"    Suggestion: {error.suggestion}")
        return False
    
    # Success - show summary
    print("\n✓ Compilation successful!")
    print(f"\nPDF: {result.pdf_path}")
    print(f"Size: {result.metrics['pdf_size'] / 1024:.1f} KB")
    print(f"Duration: {result.total_duration:.2f}s")
    
    # Stage breakdown
    print("\nPipeline Stages:")
    for stage, stage_result in result.stage_results.items():
        print(f"  {stage.value:12s} {stage_result.duration:5.2f}s")
    
    # Warnings summary
    if result.warnings:
        print(f"\nWarnings: {len(result.warnings)}")
        for warning in result.warnings[:3]:
            print(f"  - {warning}")
    
    # Save metrics
    metrics_file = output_dir / "compilation_metrics.json"
    metrics_file.write_text(json.dumps(result.metrics, indent=2))
    print(f"\nMetrics saved to: {metrics_file}")
    
    # Receipt for reproducibility
    if result.receipt_path:
        print(f"Receipt: {result.receipt_path}")
        receipt = json.loads(result.receipt_path.read_text())
        print(f"  Output hash: {receipt['output_hash'][:16]}...")
    
    return True

# Run
if __name__ == "__main__":
    success = compile_thesis(
        main_file=Path("thesis/main.tex"),
        output_dir=Path("thesis/build")
    )
    exit(0 if success else 1)
```

This example demonstrates all major features in a real-world scenario.
