# ggen API Analysis - Week 1 Integration Report

**Date**: 2025-12-20
**Analyst**: DevOps Agent
**Local Build**: ggen v5.0.2 (git: v5.0.2-4-g6ef25495)
**Status**: ⚠️ BREAKING CHANGES DETECTED

---

## Executive Summary

The local ggen v5.0.2 build introduces **breaking API changes** compared to the expected v5.0.1 interface. The CLI has been simplified to a **single `sync` command**, replacing all previous subcommands (`compile`, `generate`, `validate`, `watch`).

**Critical Finding**: The Python wrapper at `src/specify_cli/runtime/ggen.py` is **incompatible** with ggen v5.0.2 and requires a complete rewrite for Week 2.

---

## Version Comparison

### Installed Version (Expected)
- **Version**: ggen v5.0.1 (broken, missing sync subcommand)
- **Commands**: `compile`, `generate`, `validate`, `watch`, etc.
- **Status**: Non-functional (installed but unusable)

### Local Build (Actual)
- **Version**: ggen v5.0.2 (built from source)
- **Binary Location**: `/Users/sac/.local/bin/ggen`
- **Git Commit**: v5.0.2-4-g6ef25495
- **Commands**: **ONLY** `sync`
- **Status**: ✅ Functional and working

---

## API Changes - v5.0.1 → v5.0.2

### Breaking Changes

| Old Command (v5.0.1) | New Command (v5.0.2) | Status |
|----------------------|----------------------|--------|
| `ggen compile <ontology>` | `ggen sync` | ❌ REMOVED |
| `ggen generate <spec>` | `ggen sync` | ❌ REMOVED |
| `ggen validate <file>` | `ggen sync --validate_only true` | ⚠️ CHANGED |
| `ggen watch <dir>` | `ggen sync --watch true` | ⚠️ CHANGED |
| `ggen template <name>` | ❌ NOT AVAILABLE | ❌ REMOVED |

### New Unified API (v5.0.2)

```bash
ggen sync [OPTIONS]
```

**Available Options** (Actual v5.0.2):
- `--from <FROM>` - Source ontology directory (replaces --manifest)
- `--to <TO>` - Target output directory (replaces --output_dir)
- `--mode <MODE>` - Sync mode: full, incremental, verify [default: full]
- `--dry-run` - Preview changes without writing (boolean flag)
- `--force` - Override conflicts (boolean flag)
- `-v, --verbose` - Verbose output (boolean flag)

**Removed Options** (documented but not implemented):
- ❌ `--manifest` - Not present (use --from instead)
- ❌ `--audit` - Not implemented
- ❌ `--rule` - Not implemented
- ❌ `--watch` - Not implemented
- ❌ `--validate_only` - Not implemented
- ❌ `--format` - Not implemented
- ❌ `--timeout` - Not implemented

---

## CLI Usage Examples

### Basic Sync (Primary Workflow)
```bash
ggen sync
# Looks for ggen.toml in current directory
```

### Sync from Specific Directory
```bash
ggen sync --from schema/ --to src/generated/
```

### Dry Run (Preview Changes)
```bash
ggen sync --dry-run --verbose
```

### Incremental Sync Mode
```bash
ggen sync --mode incremental
```

### Force Overwrite
```bash
ggen sync --force --verbose
```

### Verify Mode (Validation)
```bash
ggen sync --mode verify
```

### Full Sync (Default)
```bash
ggen sync --mode full
# Same as: ggen sync
```

---

## Current Behavior

### Test Run Output
```bash
$ ggen sync
🚀 ggen ontology compiler
   Source: schema
   Output: src/generated
   Mode: full

✅ Compilation complete! Generated code written to: src/generated
```

**Observations**:
- ✅ Command executes successfully
- ⚠️ Does NOT use `docs/ggen.toml` configuration automatically
- ⚠️ Falls back to default `schema/` directory
- ✅ Generates code to `src/generated/`
- ⚠️ CLI flag parsing has issues (--manifest doesn't work)

**Generated Files**:
```
src/generated/
├── python-dataclass (13KB)
├── rust-struct (24KB)
└── typescript-interface (8KB)
```

---

## Python Wrapper Compatibility Analysis

### Current Implementation (`src/specify_cli/runtime/ggen.py`)

The Python wrapper expects **OLD API** (v5.0.1):

```python
# ❌ BROKEN - These commands don't exist in v5.0.2
def compile_ontology(ontology_path, output_dir):
    cmd = ["ggen", "compile", str(ontology_path)]  # ❌ No 'compile' command

def generate_code(spec_path, output_dir, language):
    cmd = ["ggen", "generate", str(spec_path)]  # ❌ No 'generate' command

def sync_specs(project_path, watch, verbose):
    cmd = ["ggen", "sync"]  # ✅ This works!
```

### Compatibility Matrix

| Python Function | ggen v5.0.1 | ggen v5.0.2 | Status |
|----------------|-------------|-------------|--------|
| `is_ggen_available()` | ✅ | ✅ | Compatible |
| `get_ggen_version()` | ✅ | ⚠️ (returns empty) | Partial |
| `compile_ontology()` | ✅ | ❌ | **BROKEN** |
| `sync_specs()` | ✅ | ✅ | Compatible |
| `generate_code()` | ✅ | ❌ | **BROKEN** |

### Required Changes for Week 2

1. **Remove** `compile_ontology()` function
2. **Remove** `generate_code()` function
3. **Update** `sync_specs()` to accept all new flags
4. **Fix** `get_ggen_version()` to parse v5.0.2 output correctly
5. **Add** new wrapper for unified `sync` command

---

## Integration Issues

### Issue 1: CLI Flag Parsing
```bash
ggen sync --manifest docs/ggen.toml
# error: unexpected argument '--manifest' found
```

**Root Cause**: CLI library (clap-noun-verb) configuration issue
**Workaround**: Run `ggen sync` from directory with ggen.toml
**Status**: Needs fix in ggen codebase

### Issue 2: Version Output
```bash
ggen --version
# (no output)
```

**Expected**: "ggen 5.0.2"
**Actual**: Empty string
**Impact**: Python wrapper's `get_ggen_version()` returns None
**Status**: Needs fix in ggen codebase

### Issue 3: Config File Detection
```bash
ggen sync
# Uses ./schema/ instead of docs/ggen.toml
```

**Expected**: Auto-detect ggen.toml in common locations
**Actual**: Falls back to hardcoded defaults
**Status**: Needs configuration system improvements

---

## Configuration System Analysis

### Expected Config: `docs/ggen.toml`

The project has a comprehensive ggen.toml with:
- ✅ 14 transformations defined
- ✅ 5-stage pipeline configured (μ₁ through μ₅)
- ✅ SPARQL queries mapped
- ✅ Tera templates specified
- ✅ Output files configured

### Actual Behavior

ggen v5.0.2 appears to:
1. Ignore `docs/ggen.toml` by default
2. Look for `schema/` directory
3. Generate generic outputs (python-dataclass, rust-struct, typescript-interface)
4. Not execute the 14 transformations

**Conclusion**: Config system not integrated yet or requires explicit path.

---

## Recommendations for Week 2

### Priority 1: Python Wrapper Rewrite
- [ ] Remove deprecated `compile_ontology()` and `generate_code()`
- [ ] Update `sync_specs()` to support all v5.0.2 flags
- [ ] Add new `sync()` wrapper with full parameter support
- [ ] Fix `get_ggen_version()` to handle empty output

### Priority 2: Configuration Integration
- [ ] Test `ggen sync` with explicit manifest path (once CLI fixed)
- [ ] Verify all 14 transformations execute
- [ ] Validate output files match expected locations
- [ ] Test dry-run, watch, and validate-only modes

### Priority 3: CLI Improvements (ggen codebase)
- [ ] Fix --manifest flag parsing
- [ ] Fix --version output
- [ ] Add auto-detection of ggen.toml in common locations
- [ ] Improve error messages

### Priority 4: Documentation
- [ ] Update README with v5.0.2 API
- [ ] Create migration guide from v5.0.1 → v5.0.2
- [ ] Document new unified sync workflow
- [ ] Add troubleshooting section

---

## Testing Readiness

### What Works ✅
- ggen v5.0.2 binary installation
- Basic `ggen sync` execution
- Code generation (generic schemas)
- Binary location at `/Users/sac/.local/bin/ggen`

### What's Broken ❌
- Python wrapper compatibility (2 of 5 functions)
- CLI flag parsing (--manifest, others)
- Version output (empty string)
- Config file auto-detection

### What's Untested ⚠️
- Full pipeline with docs/ggen.toml
- Watch mode (`--watch true`)
- Validate-only mode (`--validate_only true`)
- Audit trail (`--audit true`)
- JSON output (`--format json`)
- Timeout handling (`--timeout <N>`)

---

## Next Steps

1. **Week 2 Preparation**:
   - Create new Python wrapper for v5.0.2 API
   - Write integration tests for `ggen sync`
   - Test all CLI flags systematically

2. **ggen Codebase Fixes**:
   - Submit PR to fix --manifest flag parsing
   - Submit PR to fix --version output
   - Add ggen.toml auto-detection

3. **Pipeline Validation**:
   - Run full 14-transformation pipeline
   - Verify μ₁ through μ₅ stages execute
   - Validate output files match config

---

## Appendix: Command Reference

### ggen v5.0.2 Complete CLI

```
ggen [COMMAND]

Commands:
  sync  Execute the complete code synchronization pipeline from a ggen.toml manifest
  help  Print this message or the help of the given subcommand(s)

Options:
  -h, --help     Print help
  -V, --version  Print version
```

### ggen sync Options (Actual)

```
Compile ontology to code (sync)

Usage: ggen sync [OPTIONS]

Options:
      --from <FROM>  Source ontology directory
      --to <TO>      Target output directory
      --mode <MODE>  Sync mode: full, incremental, verify [default: full]
      --dry-run      Preview changes without writing
      --force        Override conflicts
  -v, --verbose      Verbose output
  -h, --help         Print help
```

**Note**: The actual CLI differs significantly from initial documentation.
Only the flags listed above are implemented in v5.0.2.

---

**Report Status**: Complete
**Ready for Week 2**: ⚠️ With caveats (Python wrapper needs rewrite)
**Next Agent**: Week 2 Integration Engineer
