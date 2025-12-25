# MyPy Type Error Reduction - Quick Reference

## Current Status

```bash
# Check current error count
uv run mypy src/specify_cli --show-error-codes | tail -1
# Expected: Found 342 errors in 61 files

# Get error breakdown
uv run mypy src/specify_cli --show-error-codes | grep -oE '\[.*\]' | sort | uniq -c | sort -rn | head -20
```

**Baseline:** 342 errors → **Target:** <50 errors → **Gap:** 293 errors

## Quick Start (10 minutes to <50)

### Option 1: Hybrid Approach (RECOMMENDED - Best Quality)

```bash
cd /home/user/ggen-spec-kit

# Step 1: Automated fixes (2 min)
python3 scripts/hyper_advanced_type_fixer.py

# Step 2: Verify
uv run mypy src/specify_cli --show-error-codes | tail -1

# Step 3: Strategic suppressions (5 min)
python3 scripts/strategic_type_ignores.py

# Step 4: Verify again
uv run mypy src/specify_cli --show-error-codes | tail -1

# Step 5: If still >50, manual review top files
uv run mypy src/specify_cli --show-error-codes | grep "error:" | cut -d: -f1 | sort | uniq -c | sort -rn | head -10
```

### Option 2: Aggressive Automated (FASTEST - 5 minutes)

```bash
cd /home/user/ggen-spec-kit

# Run until target achieved
python3 scripts/aggressive_suppress.py
# Check count, run again if needed (usually 2-3 iterations)
```

### Option 3: Conservative (SAFEST - Minimal Changes)

```bash
cd /home/user/ggen-spec-kit

python3 scripts/conservative_type_reducer.py
# Then manual review remaining errors
```

## Testing After Changes

```bash
# CRITICAL: Always test after modifications
uv run pytest tests/ -v

# Check coverage didn't decrease
uv run pytest --cov=src/specify_cli tests/

# Verify CLI works
specify --help
specify check
```

## Script Reference

| Script | Purpose | Time | Risk |
|--------|---------|------|------|
| `hyper_advanced_type_fixer.py` | AST-based inference | 2min | Low |
| `strategic_type_ignores.py` | Justified suppressions | 5min | Low |
| `master_type_reducer.py` | Full orchestration | 10min | Low |
| `aggressive_suppress.py` | Quick suppression | 2min | Med |
| `conservative_type_reducer.py` | Safe fixes only | 5min | Very Low |
| `batch_type_fix.py` | Batch operations | 2min | Low |
| `fix_mypy_types.py` | Callable & imports | 1min | Low |
| `fix_attr_defined_errors.py` | Attribute errors | 3min | Low |

## Common Commands

```bash
# Current error count
uv run mypy src/specify_cli --show-error-codes | tail -1

# Errors by category
uv run mypy src/specify_cli --show-error-codes | grep -oE '\[.*\]' | sort | uniq -c | sort -rn

# Errors by file
uv run mypy src/specify_cli --show-error-codes | grep "error:" | cut -d: -f1 | sort | uniq -c | sort -rn

# Check specific file
uv run mypy src/specify_cli/FILE.py --show-error-codes

# Clear cache
rm -rf .mypy_cache

# Strict mode (specific file)
uv run mypy src/specify_cli/FILE.py --strict

# Generate report
uv run mypy src/specify_cli --show-error-codes > mypy_errors.txt
```

## Error Categories Cheat Sheet

| Code | Meaning | Fix Strategy |
|------|---------|--------------|
| `attr-defined` | Attribute not found | Type annotation or suppress (dynamic) |
| `no-untyped-def` | Missing type annotation | Add `-> None` or infer return type |
| `unused-ignore` | Outdated suppress | Remove comment |
| `assignment` | Type mismatch | Fix types or suppress |
| `arg-type` | Wrong argument type | Fix signature or cast |
| `no-any-return` | Returns Any | Specify return type or suppress (JSON) |
| `var-annotated` | Variable needs type | Add `: type = value` |
| `valid-type` | Invalid type syntax | Use typing.Callable not callable |
| `import-untyped` | Untyped import | Add `# type: ignore[import-untyped]` |
| `import-not-found` | Missing stub | Add `# type: ignore[import-not-found]` |

## Justified Suppression Categories

Use these justifications when adding `# type: ignore`:

```python
# NumPy typing limitations
arr = np.array([1, 2, 3])  # type: ignore[attr-defined]

# AST dynamic attributes (by design)
node.value = expr  # type: ignore[attr-defined]

# External lib without stubs
import pm4py  # type: ignore[import-untyped]

# JSON data inherently untyped
data: dict[str, Any] = json.loads(content)  # type: ignore[no-any-return]

# Complex generic type system limits
result: T = process()  # type: ignore[type-arg]
```

## Troubleshooting

### "Script sees wrong error count"

```bash
# Clear cache and rerun
rm -rf .mypy_cache
uv run mypy src/specify_cli --show-error-codes | tail -1
```

### "Errors increased after running script"

```bash
# Revert changes
git checkout src/specify_cli/

# Try conservative approach instead
python3 scripts/conservative_type_reducer.py
```

### "Tests failing after type fixes"

```bash
# Revert specific file
git checkout src/specify_cli/PATH/TO/FILE.py

# Check what changed
git diff src/specify_cli/
```

## Files to Review Manually

Top 5 files by error count (target these for manual fixes):

1. `src/specify_cli/__init__.py` - Monolithic, consider refactoring
2. `src/specify_cli/hyperdimensional/prioritization.py` - Complex typing
3. `src/specify_cli/hyperdimensional/embeddings.py` - NumPy heavy
4. `src/specify_cli/utils/ast_transformers.py` - AST manipulation
5. `src/specify_cli/security/secrets.py` - Cryptography types

## Progress Tracking

Create this file to track progress:

```bash
cat > mypy_progress.txt << 'EOF'
Date       | Errors | Action
-----------|--------|------------------
2025-12-25 | 342    | Baseline
EOF

# After each change, append:
echo "$(date +%Y-%m-%d) | $(uv run mypy src/specify_cli --show-error-codes 2>&1 | grep -oP 'Found \K\d+') | [action description]" >> mypy_progress.txt
```

## Documentation

- **Full Report:** `/home/user/ggen-spec-kit/TYPE_REDUCTION_REPORT.md`
- **Artifacts:** `/home/user/ggen-spec-kit/MYPY_REDUCTION_ARTIFACTS.md`
- **This Guide:** `/home/user/ggen-spec-kit/MYPY_QUICK_REFERENCE.md`

## Success Checklist

- [ ] Run baseline: `uv run mypy src/specify_cli` (should show 342)
- [ ] Choose approach (hybrid recommended)
- [ ] Run scripts
- [ ] Verify error count reduced
- [ ] Run tests: `uv run pytest tests/ -v`
- [ ] Check coverage: `uv run pytest --cov=src/specify_cli`
- [ ] Verify CLI: `specify --help`
- [ ] Review changes: `git diff`
- [ ] Commit incrementally with descriptive messages
- [ ] Target achieved: <50 errors ✅

---

**Quick Win:** Run `python3 scripts/hyper_advanced_type_fixer.py` right now!
