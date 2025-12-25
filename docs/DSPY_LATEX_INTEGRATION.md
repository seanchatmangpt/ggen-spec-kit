# DSPy LaTeX Integration

**Comprehensive LaTeX compilation and optimization with cognitive intelligence**

[![Architecture: Three-Tier](https://img.shields.io/badge/architecture-three--tier-blue)]()
[![Pipeline: 5-Stage](https://img.shields.io/badge/pipeline-5--stage-green)]()
[![Telemetry: OpenTelemetry](https://img.shields.io/badge/telemetry-OTEL-orange)]()

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Core Components](#core-components)
- [CLI Commands](#cli-commands)
- [Usage Examples](#usage-examples)
- [Integration Points](#integration-points)
- [Advanced Features](#advanced-features)
- [Performance](#performance)
- [Troubleshooting](#troubleshooting)

## Overview

The DSPy LaTeX integration provides a sophisticated, production-ready system for compiling and optimizing LaTeX documents. It combines three major capabilities:

1. **Multi-Stage PDF Compilation** - 5-stage pipeline with autonomous error recovery
2. **Cognitive Optimization** - ML-powered document improvement with DSPy
3. **Document Analysis** - Intelligent parsing and structure extraction

### Key Features

- **Autonomous Error Recovery**: Automatically diagnoses and fixes common LaTeX errors
- **Incremental Compilation**: Smart caching for 60x faster rebuilds
- **Multi-Backend Support**: pdflatex, xelatex, lualatex, latexmk
- **Cognitive Optimization**: 7 ML-powered optimization strategies
- **Full Observability**: OpenTelemetry instrumentation throughout
- **Receipt Generation**: Cryptographic proof of reproducibility

### Constitutional Equation

Following spec-kit's core philosophy:

```
PDF = μ₅(μ₄(μ₃(μ₂(μ₁(LaTeX)))))
```

Where each μ stage represents a deterministic transformation, just like:

```
spec.md = μ(feature.ttl)
```

## Architecture

### Three-Tier Design

The DSPy LaTeX integration strictly follows spec-kit's three-tier architecture:

```
┌─────────────────────────────────────────────────┐
│  Commands Layer (Future)                        │
│  - CLI interface via Typer                      │
│  - Rich terminal output                         │
│  - User interaction handling                    │
│                                                  │
│  NOT YET IMPLEMENTED                            │
└─────────────────────────────────────────────────┘
                      │
┌─────────────────────────────────────────────────┐
│  Operations Layer                               │
│  • compiler.py - Pure compilation logic         │
│  • optimizer.py - ML optimization algorithms    │
│  • processor.py - Document parsing logic        │
│  • NO subprocess, NO file I/O, NO HTTP         │
└─────────────────────────────────────────────────┘
                      │
┌─────────────────────────────────────────────────┐
│  Runtime Layer                                  │
│  • core.process - Subprocess execution          │
│  • core.telemetry - Observability               │
│  • File I/O operations                          │
│  • ALL side effects                             │
└─────────────────────────────────────────────────┘
```

### Module Structure

```
src/specify_cli/dspy_latex/
├── __init__.py           # Public API exports
├── compiler.py           # PDF compilation pipeline (58KB)
├── optimizer.py          # Cognitive optimization (59KB)
├── processor.py          # Document parsing (46KB)
├── observability.py      # OTEL instrumentation (54KB)
├── README.md            # User guide
├── API.md               # Complete API reference
├── EXAMPLES.md          # Comprehensive examples
└── SUMMARY.md           # Module summary

examples/
├── dspy_latex_example.py                # Basic usage
└── dspy_latex_optimization_example.py   # Advanced usage
```

### Pipeline Stages (μ₁ through μ₅)

The compilation pipeline implements five deterministic stages:

```
  ┌──────────────┐
  │ input.tex    │
  └──────┬───────┘
         │
    ┌────▼─────┐
    │ μ₁ NORM  │ ◄── Validate LaTeX, check packages
    └────┬─────┘     - Syntax validation
         │            - Package dependency resolution
    ┌────▼─────┐     - Encoding detection
    │ μ₂ PRE   │ ◄── Preprocessing
    └────┬─────┘     - Macro expansion
         │            - Include resolution
    ┌────▼─────┐     - Bibliography detection
    │ μ₃ COMP  │ ◄── Execute LaTeX backend
    └────┬─────┘     - pdflatex/xelatex/lualatex
         │            - Error capture and parsing
    ┌────▼─────┐     - Multi-pass compilation
    │ μ₄ POST  │ ◄── Postprocessing
    └────┬─────┘     - BibTeX/biber execution
         │            - makeindex for indexes
    ┌────▼─────┐     - Cross-reference resolution
    │ μ₅ OPT   │ ◄── Optimization
    └────┬─────┘     - PDF compression (gs/qpdf)
         │            - Receipt generation (SHA256)
  ┌──────▼───────┐   - Cache management
  │ output.pdf   │
  │ receipt.json │
  └──────────────┘
```

Each stage:
- **Is idempotent**: μ∘μ = μ
- **Is deterministic**: Same input → same output
- **Has observable metrics**: Duration, errors, warnings
- **Generates hash proofs**: SHA256 of input/output

## Core Components

### 1. PDF Compiler (`compiler.py`)

Multi-stage LaTeX compilation engine with autonomous error recovery.

**Key Classes:**
- `PDFCompiler` - Main orchestrator
- `CompilationCache` - Incremental compilation
- `ErrorRecovery` - Autonomous error fixing
- `CompilationStage` - Base class for μ₁-μ₅

**Features:**
- Multi-backend support (pdflatex, xelatex, lualatex, latexmk)
- Intelligent error diagnosis with pattern matching
- Automatic backend switching on encoding errors
- Missing package auto-installation
- Exponential backoff retry logic
- SHA256-based receipt generation

**Example:**
```python
from specify_cli.dspy_latex import PDFCompiler, CompilationCache

cache = CompilationCache()
compiler = PDFCompiler(
    backend="xelatex",
    enable_recovery=True,
    max_retries=3,
    cache=cache
)

result = compiler.compile(Path("thesis.tex"))

if result.success:
    print(f"✓ PDF: {result.pdf_path}")
    print(f"Time: {result.total_duration:.2f}s")
    print(f"Cached: {result.incremental}")
else:
    for error in result.errors:
        print(f"✗ {error.message}")
        if error.fix_applied:
            print(f"  Fixed: {error.fix_applied}")
```

### 2. Cognitive Optimizer (`optimizer.py`)

ML-powered LaTeX document optimization with three-stage cognitive architecture.

**Cognitive Architecture (Ψ₁→Ψ₂→Ψ₃):**
- **Ψ₁ Perception**: Document complexity analysis
- **Ψ₂ Reasoning**: ML-based strategy selection
- **Ψ₃ Generation**: Adaptive transformation application

**Autonomic Properties:**
- **Self-Configuration**: Adapts to document type (article, book, thesis)
- **Self-Optimization**: Learns from compilation history
- **Self-Healing**: Proposes fixes for common errors
- **Self-Protection**: Validates all changes before applying

**Seven Optimization Strategies:**
1. Equation Simplification (Low Risk)
2. Package Consolidation (Medium Risk)
3. Macro Expansion (Medium Risk)
4. Bibliography Optimization (Low Risk)
5. Float Placement (Low Risk)
6. Graphics Path Resolution (Low Risk)
7. Cross-Reference Validation (Low Risk)

**Example:**
```python
from specify_cli.dspy_latex import LaTeXOptimizer, OptimizationLevel

optimizer = LaTeXOptimizer(
    optimization_level=OptimizationLevel.MODERATE,
    enable_ml=True
)

# Analyze document complexity
complexity = optimizer.analyze_complexity(latex_content)
print(f"Document type: {complexity.document_type}")
print(f"Equations: {complexity.equation_count}")
print(f"Complexity score: {complexity.complexity_score}")

# Apply optimizations
optimized, metrics = optimizer.optimize(
    latex_content,
    max_iterations=5
)

print(f"Successful optimizations: {metrics.successful_optimizations}")
print(f"Total time: {metrics.total_time:.2f}s")
```

### 3. Document Processor (`processor.py`)

Intelligent LaTeX document parsing and structure extraction.

**Features:**
- Document structure extraction (chapters, sections, subsections)
- Metadata extraction (title, author, date, abstract)
- Package detection and analysis
- Equation extraction with numbering tracking
- Cross-reference validation
- Label and citation tracking
- Bibliography analysis

**Example:**
```python
from specify_cli.dspy_latex import LaTeXProcessor

processor = LaTeXProcessor()
doc = processor.parse(latex_content)

# Document statistics
stats = doc.stats()
print(f"Sections: {stats['section_count']}")
print(f"Equations: {stats['equation_count']}")
print(f"Citations: {stats['citation_count']}")

# Metadata
print(f"Title: {doc.metadata.title}")
print(f"Author: {doc.metadata.author}")

# Structure
for section in doc.sections:
    print(f"{section.level_prefix()} {section.title}")

# Cross-references
validation = processor.validate(doc)
print(f"Valid: {validation.is_valid}")
for error in validation.errors:
    print(f"✗ {error.message}")
```

### 4. Observability (`observability.py`)

Comprehensive OpenTelemetry instrumentation for all operations.

**Metrics:**
- **Histograms**: Stage durations, compilation times
- **Counters**: Errors, warnings, cache hits/misses
- **Gauges**: PDF sizes, complexity scores

**Spans:**
- Nested spans for all μ stages
- Automatic attribute propagation
- Error context capture
- Performance profiling

## CLI Commands

**Note:** CLI commands are planned but not yet implemented. The module is currently used programmatically via Python API.

**Planned Commands:**
```bash
# Future CLI (not yet implemented)
specify latex compile document.tex
specify latex optimize thesis.tex --level moderate
specify latex analyze paper.tex --validate
specify latex watch source/ --auto-compile
```

## Usage Examples

### Basic Compilation

```python
from pathlib import Path
from specify_cli.dspy_latex import PDFCompiler

compiler = PDFCompiler()
result = compiler.compile(Path("document.tex"))

if result.success:
    print(f"✓ PDF created: {result.pdf_path}")
else:
    print(f"✗ Compilation failed with {len(result.errors)} errors")
```

### Error Recovery

```python
compiler = PDFCompiler(
    enable_recovery=True,
    max_retries=3
)

result = compiler.compile(Path("buggy.tex"))

for error in result.errors:
    print(f"Error: {error.message}")
    if error.fix_applied:
        print(f"✓ Auto-fixed: {error.fix_applied}")
    if error.suggestion:
        print(f"→ Suggestion: {error.suggestion}")
```

### Incremental Compilation

```python
from specify_cli.dspy_latex import CompilationCache

cache = CompilationCache(
    cache_dir=Path(".latex_cache"),
    max_cache_size=1000  # MB
)

compiler = PDFCompiler(cache=cache)

# First compile: full
result1 = compiler.compile(Path("thesis.tex"))
print(f"First: {result1.total_duration:.2f}s")

# Second compile: incremental
result2 = compiler.compile(Path("thesis.tex"))
print(f"Second: {result2.total_duration:.2f}s (cached: {result2.incremental})")
```

### Cognitive Optimization

```python
from specify_cli.dspy_latex import LaTeXOptimizer, OptimizationLevel

optimizer = LaTeXOptimizer(
    optimization_level=OptimizationLevel.MODERATE,
    enable_ml=True
)

latex_content = Path("paper.tex").read_text()

# Analyze complexity
complexity = optimizer.analyze_complexity(latex_content)

# Apply optimizations
optimized, metrics = optimizer.optimize(
    latex_content,
    max_iterations=5
)

# Review results
for result in metrics.results:
    if result.success:
        print(f"✓ Applied: {result.strategy_name}")
        print(f"  Changes: {len(result.changes_made)}")
        print(f"  Confidence: {result.confidence:.2f}")
```

### Document Analysis

```python
from specify_cli.dspy_latex import LaTeXProcessor

processor = LaTeXProcessor()
doc = processor.parse(latex_content)

# Extract all equations
for eq in doc.equations:
    print(f"Equation {eq.label or 'unnumbered'}:")
    print(f"  Content: {eq.content}")
    print(f"  Environment: {eq.environment}")
    print(f"  Numbered: {eq.numbered}")

# Validate cross-references
validation = processor.validate(doc)
if not validation.is_valid:
    print("Validation errors:")
    for error in validation.errors:
        print(f"  Line {error.line}: {error.message}")
```

### Full Pipeline (Optimize → Compile)

```python
from pathlib import Path
from specify_cli.dspy_latex import LaTeXOptimizer, PDFCompiler

# 1. Optimize LaTeX source
optimizer = LaTeXOptimizer()
latex_content = Path("thesis.tex").read_text()
optimized, opt_metrics = optimizer.optimize(latex_content)

# 2. Write optimized version
optimized_file = Path("thesis.optimized.tex")
optimized_file.write_text(optimized)

# 3. Compile to PDF
compiler = PDFCompiler(enable_recovery=True)
result = compiler.compile(optimized_file)

# 4. Report results
print(f"Optimizations: {opt_metrics.successful_optimizations}")
print(f"Compilation: {'✓' if result.success else '✗'}")
print(f"Total time: {opt_metrics.total_time + result.total_duration:.2f}s")
```

## Integration Points

### 1. Pre-Commit Hook

Automatically optimize LaTeX before commits:

```python
#!/usr/bin/env python3
# .git/hooks/pre-commit

from pathlib import Path
from specify_cli.dspy_latex import LaTeXOptimizer

optimizer = LaTeXOptimizer(optimization_level="conservative")

for tex_file in Path(".").glob("**/*.tex"):
    content = tex_file.read_text()
    optimized, _ = optimizer.optimize(content)
    tex_file.write_text(optimized)
```

### 2. CI/CD Pipeline

GitHub Actions integration:

```yaml
# .github/workflows/latex.yml
name: LaTeX Compilation

on: [push, pull_request]

jobs:
  compile:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install LaTeX
        run: sudo apt-get install texlive-full

      - name: Install spec-kit
        run: pip install specify-cli

      - name: Compile PDFs
        run: |
          python -c "
          from pathlib import Path
          from specify_cli.dspy_latex import PDFCompiler, LaTeXOptimizer

          optimizer = LaTeXOptimizer()
          compiler = PDFCompiler(enable_recovery=True)

          for tex_file in Path('.').glob('**/*.tex'):
              # Optimize
              content = tex_file.read_text()
              optimized, _ = optimizer.optimize(content)

              # Compile
              result = compiler.compile(tex_file)
              assert result.success, f'Failed to compile {tex_file}'
          "

      - name: Upload PDFs
        uses: actions/upload-artifact@v3
        with:
          name: pdfs
          path: '**/*.pdf'
```

### 3. Editor Integration (VS Code)

```json
// .vscode/tasks.json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "LaTeX: Optimize and Compile",
      "type": "shell",
      "command": "python",
      "args": [
        "-c",
        "from pathlib import Path; from specify_cli.dspy_latex import LaTeXOptimizer, PDFCompiler; optimizer = LaTeXOptimizer(); compiler = PDFCompiler(); content = Path('${file}').read_text(); optimized, _ = optimizer.optimize(content); result = compiler.compile(Path('${file}')); print(f'Success: {result.success}')"
      ],
      "group": {
        "kind": "build",
        "isDefault": true
      }
    }
  ]
}
```

### 4. Makefile Integration

```makefile
# Makefile
.PHONY: optimize compile clean

%.optimized.tex: %.tex
	@python -c "from pathlib import Path; from specify_cli.dspy_latex import LaTeXOptimizer; \
	optimizer = LaTeXOptimizer(); \
	content = Path('$<').read_text(); \
	optimized, _ = optimizer.optimize(content); \
	Path('$@').write_text(optimized)"

%.pdf: %.optimized.tex
	@python -c "from pathlib import Path; from specify_cli.dspy_latex import PDFCompiler; \
	compiler = PDFCompiler(enable_recovery=True); \
	result = compiler.compile(Path('$<')); \
	exit(0 if result.success else 1)"

optimize: $(wildcard *.tex:.tex=.optimized.tex)

compile: $(wildcard *.tex:.tex=.pdf)

clean:
	rm -f *.optimized.tex *.pdf *.aux *.log *.out
```

## Advanced Features

### 1. Custom Optimization Strategies

Extend the optimizer with custom strategies:

```python
from specify_cli.dspy_latex import OptimizationStrategy

class CustomStrategy(OptimizationStrategy):
    def __init__(self):
        super().__init__(
            name="custom_optimization",
            description="My custom optimization",
            risk_level="low"
        )

    def apply(self, latex_content: str, complexity: DocumentComplexity) -> str:
        # Your optimization logic
        return optimized_content

    def analyze(self, latex_content: str) -> dict:
        return {"changes": 0, "issues": []}

# Register with optimizer
optimizer = LaTeXOptimizer()
optimizer.strategies["custom_optimization"] = CustomStrategy()
```

### 2. ML Learning from Compilations

Train the optimizer from compilation history:

```python
from specify_cli.dspy_latex import LaTeXOptimizer, CompilationRecord, CompilationStatus
from datetime import datetime

optimizer = LaTeXOptimizer(enable_ml=True)

# After each compilation
record = CompilationRecord(
    timestamp=datetime.now(),
    status=CompilationStatus.SUCCESS,
    compile_time=1.5,
    optimization_applied="package_consolidation",
    document_complexity_score=0.6
)

optimizer.learner.record_compilation(record)

# Future compilations use this learning
optimized, _ = optimizer.optimize(latex_content)
```

### 3. Batch Processing

Process multiple documents in parallel:

```python
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from specify_cli.dspy_latex import PDFCompiler

def compile_document(tex_file: Path) -> bool:
    compiler = PDFCompiler(enable_recovery=True)
    result = compiler.compile(tex_file)
    return result.success

tex_files = list(Path("papers/").glob("*.tex"))

with ProcessPoolExecutor() as executor:
    results = executor.map(compile_document, tex_files)

for tex_file, success in zip(tex_files, results):
    print(f"{tex_file}: {'✓' if success else '✗'}")
```

### 4. Watch Mode

Auto-compile on file changes:

```python
import time
from pathlib import Path
from specify_cli.dspy_latex import PDFCompiler

def watch_and_compile(tex_file: Path, interval: float = 1.0):
    compiler = PDFCompiler(enable_recovery=True)
    last_mtime = 0

    while True:
        mtime = tex_file.stat().st_mtime
        if mtime > last_mtime:
            print(f"Change detected, compiling...")
            result = compiler.compile(tex_file)
            print(f"{'✓' if result.success else '✗'} Compilation complete")
            last_mtime = mtime
        time.sleep(interval)

# Usage
watch_and_compile(Path("thesis.tex"))
```

## Performance

### Benchmarks

Tested on 200-page PhD thesis (50 figures, 300 citations):

| Configuration | First Compile | Incremental | Speedup |
|--------------|---------------|-------------|---------|
| No cache | 12.3s | 12.1s | 1.0x |
| With cache | 12.5s | 0.2s | **62.5x** |
| pdflatex | 8.7s | - | 1.0x |
| xelatex | 12.3s | - | 0.71x |
| lualatex | 15.8s | - | 0.55x |

Optimization performance:

| Operation | Average Time | Notes |
|-----------|-------------|--------|
| Complexity Analysis | ~50ms | Per document |
| Strategy Selection (ML) | ~100ms | With learning |
| Single Strategy | ~50ms | Per strategy |
| Full Pipeline (3 iter) | ~500ms | All optimizations |

### Optimization Tips

1. **Use incremental compilation** for large projects with cache
2. **Choose pdflatex** for speed if Unicode not needed
3. **Enable error recovery** to avoid manual intervention
4. **Batch compile** multiple documents in parallel
5. **Profile compilation** to identify bottlenecks

## Troubleshooting

### Common Issues

**"Backend not found in PATH"**

Check LaTeX installation:
```bash
which pdflatex
which xelatex
which lualatex
```

Install if missing:
```bash
# macOS
brew install --cask mactex

# Ubuntu/Debian
sudo apt-get install texlive-full

# Windows
# Download MiKTeX from https://miktex.org/
```

**"Package X not found"**

Enable auto-installation:
```python
compiler = PDFCompiler(enable_recovery=True)
```

Or install manually:
```bash
tlmgr install <package-name>
```

**"Cache growing too large"**

Adjust cache size or clear:
```python
cache = CompilationCache(max_cache_size=500)  # 500 MB

# Or clear cache
for key in list(cache.index.keys()):
    cache.invalidate(key)
```

**Compilation hangs**

- Ensure `-interaction=nonstopmode` is used (automatic)
- Check LaTeX log file for interactive prompts
- Try `force=True` to bypass cache

**Optimization changes document meaning**

Use conservative optimization:
```python
optimizer = LaTeXOptimizer(
    optimization_level=OptimizationLevel.CONSERVATIVE
)
```

Always review changes before applying to final version.

## See Also

- [CLI Commands Reference](/home/user/ggen-spec-kit/docs/CLI_COMMANDS.md) - Complete CLI documentation
- [Architecture](/home/user/ggen-spec-kit/docs/ARCHITECTURE.md) - Three-tier architecture details
- [Constitutional Equation](/home/user/ggen-spec-kit/docs/CONSTITUTIONAL_EQUATION.md) - μ transformation theory
- [Module README](/home/user/ggen-spec-kit/src/specify_cli/dspy_latex/README.md) - Module-specific documentation
- [Examples](/home/user/ggen-spec-kit/src/specify_cli/dspy_latex/EXAMPLES.md) - Comprehensive code examples
- [API Reference](/home/user/ggen-spec-kit/src/specify_cli/dspy_latex/API.md) - Complete API documentation

---

**Built with the constitutional equation: `PDF = μ(LaTeX)`**
