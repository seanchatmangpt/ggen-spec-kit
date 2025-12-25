# Ruff Violation Cleanup - Quick Reference

## Current Status
- **Before:** 1,002 violations
- **After:** 960 violations  
- **Fixed:** 42 violations (4.2% reduction)
- **Test Pass Rate:** 98.1%

## Top 10 Remaining Violations

| Rank | Code | Count | Description | Fix Strategy |
|------|------|-------|-------------|--------------|
| 1 | PLC0415 | 222 | import-outside-top-level | ACCEPT (intentional) |
| 2 | TRY300 | 103 | try-consider-else | Refactor exception handling |
| 3 | ARG001 | 95 | unused-function-argument | Prefix with _ |
| 4 | G004 | 75 | logging-f-string | Convert to % formatting |
| 5 | B008 | 71 | function-call-in-default-argument | ACCEPT (Typer pattern) |
| 6 | TRY301 | 51 | raise-within-try | Extract to functions |
| 7 | ARG002 | 42 | unused-method-argument | Prefix with _ |
| 8 | PTH123 | 42 | builtin-open | Use Path.open() |
| 9 | TRY400 | 42 | error-instead-of-exception | Use specific exceptions |
| 10 | PLR0912 | 28 | too-many-branches | ACCEPT (complex logic) |

## Critical Fixes Needed (High Priority)

```bash
# 1. Fix undefined names (20 violations) - CRITICAL
uv run ruff check src/specify_cli --select F821

# 2. Fix raise-from violations (14 violations) - HIGH
uv run ruff check src/specify_cli --select B904

# 3. Fix datetime timezone (28 violations) - HIGH  
uv run ruff check src/specify_cli --select DTZ005,DTZ003
```

## Quick Wins (Easy Fixes)

```bash
# 1. Apply remaining 8 safe auto-fixes
uv run ruff check src/specify_cli --fix

# 2. Fix datetime timezone with unsafe fixes
uv run ruff check src/specify_cli --select UP017 --fix --unsafe-fixes

# 3. Sort imports
uv run ruff check src/specify_cli --select I001 --fix
```

## Accepted Violations (Don't Fix)

| Code | Count | Reason |
|------|-------|--------|
| PLC0415 | 222 | Lazy imports for optional deps (pm4py, coverage) |
| B008 | 71 | Typer framework requirement |
| PLR0912/PLR0915 | 56 | Complex but necessary business logic |
| SLF001 | 5 | Framework integration (_specify_tracker_active) |

## File-Specific Hotspots

### Most Violations Per File
1. `src/specify_cli/__init__.py` - ~50 violations (init function complexity)
2. `src/specify_cli/utils/templates.py` - ~40 violations (template complexity)
3. `src/specify_cli/dspy_latex/optimizer.py` - ~35 violations
4. `src/specify_cli/ops/process_mining.py` - ~30 violations

### Files to Prioritize
- Files with F821 (undefined names) - causes runtime errors
- Files with B904 (raise-from) - improves debugging
- Files with DTZ violations - prevents timezone bugs

## Automated Fix Commands

```bash
# Safe fixes only
uv run ruff check src/specify_cli --fix

# Include unsafe fixes (review changes)
uv run ruff check src/specify_cli --fix --unsafe-fixes

# Fix specific categories
uv run ruff check src/specify_cli --select I001,UP017,UP035 --fix

# Check impact before fixing
uv run ruff check src/specify_cli --select ARG001 --statistics
```

## Testing After Fixes

```bash
# Quick test
uv run pytest tests/unit -q --tb=no

# Full test with coverage
uv run pytest tests/ -v --cov=src/specify_cli

# Specific module test
uv run pytest tests/unit/test_core_process.py -v
```

## Progress Tracking

```bash
# Get current statistics
uv run ruff check src/specify_cli --statistics

# Count violations
uv run ruff check src/specify_cli 2>&1 | grep "Found" 

# Check specific file
uv run ruff check src/specify_cli/__init__.py
```

## Target Milestones

- **Day 1:** 890 violations (fix F821, B904, DTZ)
- **Week 1:** 480 violations (fix ARG, G004, PTH)  
- **Month 1:** <100 violations (refactor TRY, complexity)

---

**Last Updated:** 2025-12-25
**Current:** 960 violations
**Target:** <100 violations
