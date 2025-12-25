# CLI Commands Reference

Complete reference for all `specify` CLI commands, including planned DSPy LaTeX commands.

## Table of Contents

- [Overview](#overview)
- [Core Commands](#core-commands)
- [DSPy LaTeX Commands](#dspy-latex-commands-planned)
- [Workflow Commands](#workflow-commands)
- [Development Commands](#development-commands)
- [Global Options](#global-options)

## Overview

The `specify` CLI follows the three-tier architecture pattern and uses Typer for command definition. Commands are either:

1. **Generated from RDF** - Following the constitutional equation `spec.md = μ(feature.ttl)`
2. **Manually implemented** - For runtime operations and core tooling

## Core Commands

### `specify init`

Initialize a new spec-kit project with RDF ontology scaffolding.

**Usage:**
```bash
specify init <project-name> [OPTIONS]
specify init . [OPTIONS]
specify init --here [OPTIONS]
```

**Arguments:**
- `<project-name>` - Name for new project directory (optional if using `--here` or `.`)

**Options:**
- `--ai <agent>` - AI assistant to configure
  - Choices: `claude`, `gemini`, `copilot`, `cursor-agent`, `qwen`, `opencode`, `codex`, `windsurf`, `kilocode`, `auggie`, `roo`, `codebuddy`, `amp`, `shai`, `q`, `bob`, `qoder`
- `--script <type>` - Script variant (`sh` or `ps`)
- `--ignore-agent-tools` - Skip AI agent tool checks
- `--no-git` - Skip git repository initialization
- `--here` - Initialize in current directory
- `--force` - Force overwrite without confirmation
- `--skip-tls` - Skip SSL/TLS verification (not recommended)
- `--debug` - Enable detailed debug output
- `--github-token <token>` - GitHub API token

**Examples:**
```bash
# Create new project
specify init my-project --ai claude

# Initialize in current directory
specify init . --ai claude
specify init --here --ai claude

# Force merge into non-empty directory
specify init . --force --ai claude
specify init --here --force --ai claude

# With PowerShell scripts
specify init my-project --ai copilot --script ps

# Debug mode
specify init my-project --ai claude --debug
```

### `specify check`

Check for installed tools required by spec-kit.

**Usage:**
```bash
specify check
```

**Checks for:**
- git
- ggen (v5.0.2)
- uv
- Python 3.11+
- AI agent tools (claude, gemini, etc.)

**Example Output:**
```
✓ git: /usr/bin/git (version 2.39.0)
✓ ggen: /usr/local/bin/ggen (version 5.0.2)
✓ uv: /usr/local/bin/uv (version 0.5.13)
✓ python: /usr/bin/python3.11 (version 3.11.5)
✗ claude: not found
```

### `specify version`

Show version and build information.

**Usage:**
```bash
specify version
```

**Output:**
```
specify-cli version 0.5.0
Python 3.11.5
Platform: linux
Architecture: x86_64
```

## DSPy LaTeX Commands (Planned)

**Note:** These commands are planned but not yet implemented. The DSPy LaTeX functionality is currently available via Python API only.

### `specify latex compile`

Compile LaTeX documents to PDF with autonomous error recovery.

**Usage:**
```bash
specify latex compile <input-file> [OPTIONS]
```

**Arguments:**
- `<input-file>` - LaTeX file to compile (`.tex`)

**Options:**
- `--backend <engine>` - LaTeX engine (default: `pdflatex`)
  - Choices: `pdflatex`, `xelatex`, `lualatex`, `latexmk`
- `--output-dir <dir>` - Output directory (default: same as input)
- `--enable-recovery / --no-recovery` - Enable error recovery (default: enabled)
- `--max-retries <n>` - Maximum retry attempts (default: 3)
- `--cache / --no-cache` - Use incremental compilation (default: enabled)
- `--compress / --no-compress` - Compress PDF output (default: enabled)
- `--force` - Force recompilation (bypass cache)
- `--receipt` - Generate cryptographic receipt
- `--verbose` - Show detailed compilation output

**Examples:**
```bash
# Basic compilation
specify latex compile document.tex

# With XeLaTeX (for Unicode)
specify latex compile thesis.tex --backend xelatex

# Disable error recovery
specify latex compile paper.tex --no-recovery

# Force recompilation
specify latex compile thesis.tex --force

# Verbose output with receipt
specify latex compile document.tex --verbose --receipt
```

**Expected Output:**
```
Compiling: document.tex
μ₁ NORMALIZE  ✓ 0.1s  (validation)
μ₂ PREPROCESS ✓ 0.2s  (macro expansion)
μ₃ COMPILE    ✓ 8.5s  (pdflatex)
μ₄ POSTPROCESS ✓ 1.2s (bibtex, refs)
μ₅ OPTIMIZE   ✓ 0.3s  (compression)

✓ PDF created: document.pdf
Total time: 10.3s
PDF size: 1.2 MB
Receipt: document.receipt.json
```

**Error Scenarios:**
```bash
# Missing package (auto-recovered)
specify latex compile paper.tex
μ₁ NORMALIZE  ✗ Missing package: booktabs
              ✓ Auto-installed: booktabs
μ₁ NORMALIZE  ✓ 0.2s (retry successful)

# Encoding error (auto-switched backend)
specify latex compile unicode.tex
μ₃ COMPILE    ✗ Encoding error with pdflatex
              → Switching to xelatex
μ₃ COMPILE    ✓ 9.1s (xelatex)
```

### `specify latex optimize`

Optimize LaTeX documents with ML-powered cognitive strategies.

**Usage:**
```bash
specify latex optimize <input-file> [OPTIONS]
```

**Arguments:**
- `<input-file>` - LaTeX file to optimize (`.tex`)

**Options:**
- `--level <level>` - Optimization level (default: `moderate`)
  - Choices: `conservative`, `moderate`, `aggressive`
- `--output <file>` - Output file (default: `<input>.optimized.tex`)
- `--max-iterations <n>` - Maximum optimization iterations (default: 3)
- `--enable-ml / --no-ml` - Use ML learning (default: enabled)
- `--dry-run` - Show what would be optimized without applying
- `--interactive` - Review each optimization before applying
- `--strategies <list>` - Specific strategies to apply (comma-separated)
- `--verbose` - Show detailed optimization reasoning

**Examples:**
```bash
# Basic optimization
specify latex optimize thesis.tex

# Conservative (minimal changes)
specify latex optimize paper.tex --level conservative

# Aggressive with specific strategies
specify latex optimize document.tex --level aggressive \
  --strategies equation_simplification,package_consolidation

# Dry run to preview changes
specify latex optimize thesis.tex --dry-run

# Interactive mode
specify latex optimize paper.tex --interactive
```

**Expected Output:**
```
Analyzing: thesis.tex

Ψ₁ PERCEPTION
  Document type: phd_thesis
  Equations: 127
  Figures: 45
  Citations: 312
  Complexity score: 0.78

Ψ₂ REASONING
  Selected strategies (ML-ranked):
    1. package_consolidation (probability: 0.92)
    2. equation_simplification (probability: 0.85)
    3. cross_reference_validation (probability: 0.73)

Ψ₃ GENERATION
  ✓ package_consolidation: 12 changes (confidence: 0.94)
  ✓ equation_simplification: 8 changes (confidence: 0.88)
  ✓ cross_reference_validation: 3 warnings (confidence: 0.91)

✓ Optimized: thesis.optimized.tex
Total optimizations: 3
Total time: 0.5s
```

**Interactive Mode:**
```bash
specify latex optimize paper.tex --interactive

Strategy: package_consolidation
Changes:
  - Remove duplicate: \usepackage{amsmath} (line 15)
  - Replace obsolete: \usepackage{epsfig} → \usepackage{graphicx} (line 23)

Apply this optimization? [y/N/s(kip all)]: y
✓ Applied

Strategy: equation_simplification
Changes:
  - Simplify nested fractions in equation eq:complex (line 145)

Apply this optimization? [y/N/s(kip all)]: y
✓ Applied
```

### `specify latex analyze`

Analyze LaTeX document structure and quality.

**Usage:**
```bash
specify latex analyze <input-file> [OPTIONS]
```

**Arguments:**
- `<input-file>` - LaTeX file to analyze (`.tex`)

**Options:**
- `--validate` - Run validation checks
- `--check-refs` - Check cross-references
- `--check-citations` - Check citations
- `--format <format>` - Output format (default: `table`)
  - Choices: `table`, `json`, `markdown`
- `--verbose` - Show detailed analysis

**Examples:**
```bash
# Basic analysis
specify latex analyze document.tex

# With validation
specify latex analyze thesis.tex --validate

# JSON output
specify latex analyze paper.tex --format json > analysis.json
```

**Expected Output:**
```
Document Analysis: thesis.tex

Metadata:
  Title: My PhD Thesis
  Author: Claude Code
  Date: 2024-12-24

Structure:
  Chapters: 7
  Sections: 45
  Subsections: 128

Content:
  Equations: 127 (115 numbered, 12 unnumbered)
  Figures: 45
  Tables: 23
  Citations: 312

Packages:
  amsmath, graphicx, hyperref, booktabs, natbib
  (18 packages total)

Cross-References:
  Labels: 143
  References: 287
  ✓ All references resolved

Validation:
  ✓ No errors
  ⚠ 3 warnings
    - Line 145: Consider using \eqref instead of \ref for equations
    - Line 267: Float placement [h] too restrictive
    - Line 412: Unused label: fig:old_diagram
```

### `specify latex watch`

Watch LaTeX files and auto-compile on changes.

**Usage:**
```bash
specify latex watch <input-file-or-directory> [OPTIONS]
```

**Arguments:**
- `<input-file-or-directory>` - File or directory to watch

**Options:**
- `--interval <seconds>` - Polling interval (default: 1.0)
- `--pattern <glob>` - File pattern to watch (default: `*.tex`)
- `--backend <engine>` - LaTeX engine (default: `pdflatex`)
- `--optimize` - Auto-optimize before compiling
- `--quiet` - Suppress output except errors

**Examples:**
```bash
# Watch single file
specify latex watch thesis.tex

# Watch directory
specify latex watch chapters/ --pattern "*.tex"

# With optimization
specify latex watch paper.tex --optimize

# Quiet mode
specify latex watch thesis.tex --quiet
```

**Expected Output:**
```
Watching: thesis.tex
Press Ctrl+C to stop

[2024-12-24 10:30:15] Change detected
Compiling...
✓ PDF created (10.2s)

[2024-12-24 10:35:42] Change detected
Compiling...
✓ PDF created (0.3s, cached)
```

### `specify latex batch`

Compile multiple LaTeX documents in parallel.

**Usage:**
```bash
specify latex batch <pattern-or-files> [OPTIONS]
```

**Arguments:**
- `<pattern-or-files>` - Glob pattern or file list

**Options:**
- `--workers <n>` - Number of parallel workers (default: CPU count)
- `--backend <engine>` - LaTeX engine (default: `pdflatex`)
- `--continue-on-error` - Continue if one fails
- `--summary` - Show summary table

**Examples:**
```bash
# Compile all .tex files
specify latex batch "papers/*.tex"

# Multiple specific files
specify latex batch paper1.tex paper2.tex paper3.tex

# Parallel with 4 workers
specify latex batch "chapters/*.tex" --workers 4

# Continue on errors
specify latex batch "*.tex" --continue-on-error --summary
```

**Expected Output:**
```
Compiling 12 documents with 4 workers...

✓ chapter1.tex (8.5s)
✓ chapter2.tex (9.1s)
✗ chapter3.tex (failed: missing package)
✓ chapter4.tex (7.8s)
...

Summary:
  Total: 12
  Success: 11
  Failed: 1
  Total time: 45.3s
  Average: 4.1s per document
```

## Workflow Commands

### `specify wf validate`

Execute full OTEL validation workflow.

**Usage:**
```bash
specify wf validate [OPTIONS]
```

**Options:**
- `-i, --iterations <n>` - Validation iterations (default: 3)
- `-v, --verbose` - Verbose output
- `--export-json <file>` - Export results to JSON

**Example:**
```bash
specify wf validate -i 5 --verbose --export-json results.json
```

### `specify wf discover-projects`

Discover Python projects in directory tree.

**Usage:**
```bash
specify wf discover-projects [OPTIONS]
```

**Options:**
- `-p, --path <path>` - Root path to search (default: current)
- `-d, --depth <n>` - Max search depth (default: 5)
- `-c, --confidence <level>` - Min confidence (default: medium)

**Example:**
```bash
specify wf discover-projects -p ~/projects -d 3 -c high
```

### `specify wf batch-validate`

Validate multiple projects in batch.

**Usage:**
```bash
specify wf batch-validate [OPTIONS]
```

**Options:**
- `-p, --path <path>` - Root path (default: current)
- `--parallel / --no-parallel` - Parallel execution (default: enabled)
- `-w, --workers <n>` - Worker count (default: CPU count)
- `--export-json <file>` - Export results

**Example:**
```bash
specify wf batch-validate -p ~/projects --parallel -w 4
```

## Development Commands

### `specify build`

Build documentation and assets.

**Usage:**
```bash
specify build [OPTIONS]
```

**Options:**
- `--docs` - Build documentation only
- `--clean` - Clean before building

### `specify lint`

Run code quality checks.

**Usage:**
```bash
specify lint [OPTIONS]
```

**Options:**
- `--fix` - Auto-fix issues
- `--strict` - Strict mode (fail on warnings)

### `specify tests`

Run test suite.

**Usage:**
```bash
specify tests [OPTIONS]
```

**Options:**
- `--coverage` - Generate coverage report
- `--watch` - Watch mode
- `--pattern <pattern>` - Test file pattern

## Global Options

These options are available for all commands:

- `--help` - Show help message
- `--version` - Show version information
- `--verbose` - Enable verbose output
- `--quiet` - Suppress non-error output
- `--no-color` - Disable colored output
- `--log-level <level>` - Set logging level (debug, info, warning, error)

**Examples:**
```bash
# Verbose mode
specify latex compile thesis.tex --verbose

# Quiet mode (errors only)
specify latex compile paper.tex --quiet

# Debug logging
specify latex compile document.tex --log-level debug
```

## Configuration

Commands can be configured via:

1. **Environment variables:**
   ```bash
   export SPECIFY_LATEX_BACKEND=xelatex
   export SPECIFY_LATEX_CACHE_DIR=/tmp/latex-cache
   export SPECIFY_LOG_LEVEL=debug
   ```

2. **Config file** (`.specify.toml`):
   ```toml
   [latex]
   backend = "xelatex"
   enable_recovery = true
   max_retries = 3
   cache_dir = ".latex_cache"

   [latex.optimize]
   level = "moderate"
   enable_ml = true
   max_iterations = 5
   ```

3. **Command-line options** (highest priority)

## Exit Codes

All commands return standard exit codes:

- `0` - Success
- `1` - General error
- `2` - Compilation/validation failed
- `3` - Missing dependencies
- `4` - Invalid arguments
- `130` - Interrupted (Ctrl+C)

## See Also

- [DSPy LaTeX Integration](/home/user/ggen-spec-kit/docs/DSPY_LATEX_INTEGRATION.md) - Complete integration guide
- [Architecture](/home/user/ggen-spec-kit/docs/ARCHITECTURE.md) - Three-tier architecture
- [Examples](/home/user/ggen-spec-kit/src/specify_cli/dspy_latex/EXAMPLES.md) - Code examples

---

**Commands follow the constitutional equation: Generated from RDF specifications**
