# Documentation Gap Analysis

**Generated:** 2025-12-23
**Status:** 23 gaps identified across critical, important, and nice-to-have categories
**Total Missing:** ~25-30 files + 65+ incomplete cross-references

---

## Quick Summary

| Severity | Count | Type | Impact |
|----------|-------|------|--------|
| 🔴 CRITICAL | 15 | 4 explanations + 11 CLI commands | Navigation broken, commands undiscoverable |
| 🟠 IMPORTANT | 37 | 7 guides + 2 references + 6 advanced ops + 2 configs + 65+ cross-refs | Feature discovery blocked, poor navigation |
| 🟡 NICE-TO-HAVE | 15+ | Ecosystem, examples, advanced tutorials, error details | Enhancement opportunities |

---

## Critical Gaps (Must Fix)

### 1. Missing Explanation Files (4 files)

These are referenced in `/docs/explanation/README.md` but don't exist:

| File | Purpose | Status |
|------|---------|--------|
| `ggen-pipeline.md` | Five-stage μ transformation walkthrough | ❌ MISSING |
| `opentelemetry-design.md` | OTEL design rationale and instrumentation philosophy | ❌ MISSING |
| `error-prevention.md` | Poka-yoke error-proof system design principles | ❌ MISSING |
| `hyperdimensional-theory.md` | Advanced info-theoretic computing concepts | ❌ MISSING |

**Impact:** Broken explanation navigation; users can't find critical concept documentation

**Fix:** Create 4 markdown files in `/docs/explanation/`

---

### 2. Missing CLI Command Documentation (11 commands)

44% of CLI commands are undocumented:

| Command | Category | Status | Impact |
|---------|----------|--------|--------|
| `check` | Utilities | ❌ MISSING | Can't discover tool |
| `dashboards` | UI | ❌ MISSING | Feature completely invisible |
| `generated` | Code Gen | ❌ MISSING | Feature invisible |
| `ggen` | Core | ❌ MISSING | CRITICAL - main command undocumented |
| `hd` | Advanced | ❌ MISSING | Hyperdimensional computing hidden |
| `hdql` | Advanced | ❌ MISSING | Hyperdimensional query language hidden |
| `init` | Core | ⚠️ SPARSE | 3-line reference only (at `/docs/reference/cli-commands.md:123`) |
| `jtbd` | Framework | ❌ MISSING | JTBD command features invisible |
| `pm` | Advanced | ❌ MISSING | Process mining completely hidden |
| `spiff` | Advanced | ❌ MISSING | Workflow automation hidden |
| `version` | Utilities | ⚠️ SPARSE | 2-line reference only (at `/docs/reference/cli-commands.md:456`) |

**Impact:** Users cannot discover or use 44% of system functionality

**Fix:** Create `/docs/commands/` folder with 11 markdown files (one per command)

---

## Important Gaps (Should Fix)

### 3. Missing How-To Guides (7 files)

| File | Topic | Status | Location |
|------|-------|--------|----------|
| `view-traces.md` | Observability | ❌ MISSING | `/docs/guides/observability/` |
| `setup-ai-agents.md` | AI Integration | ❌ MISSING | `/docs/guides/ai-integration/` |
| `token-optimization.md` | AI Integration | ❌ MISSING | `/docs/guides/ai-integration/` |
| `documentation-verification.md` | AI Integration | ❌ MISSING | `/docs/guides/ai-integration/` |
| `interpret-receipts.md` | Operations | ❌ MISSING | `/docs/guides/operations/` |
| `refactor-legacy.md` | Architecture | ❌ MISSING | `/docs/guides/architecture/` |
| `measure-outcomes.md` | JTBD | ❌ MISSING | `/docs/guides/jtbd/` |

**Impact:** Users can't learn practical how-to procedures for important workflows

**Fix:** Create 7 markdown files in appropriate `/docs/guides/*/` subdirectories

---

### 4. Missing Reference Files (2 files)

| File | Content | Status | Location |
|------|---------|--------|----------|
| `telemetry-api.md` | OpenTelemetry API reference (decorators, utilities) | ❌ MISSING | `/docs/reference/` |
| `definition-of-done.md` | Quality acceptance criteria, DoD checklist | ❌ MISSING | `/docs/reference/` |

**Impact:** Operators can't reference API documentation; quality standards not formalized

**Fix:** Create 2 markdown files in `/docs/reference/`

---

### 5. Undocumented Advanced ggen Operations (6 features)

Code exists in `/src/specify_cli/ops/` but has no documentation:

| Feature | File | Purpose | Impact |
|---------|------|---------|--------|
| Recovery Management | `ggen_recovery.py` | Handle failures, recovery steps | Users don't know failure recovery exists |
| Timeout Management | `ggen_timeout*.py` | Control transformation timeouts | No guide on timeout tuning |
| Concurrent Access | `ggen_filelock.py` | Handle concurrent transforms | Can't use parallel builds |
| Incremental Builds | `ggen_incremental.py` | Skip unchanged files | Optimization feature hidden |
| Pre-flight Validation | `ggen_preflight.py` | Validate before transform | Feature undiscovered |
| Manifest Tracking | `ggen_manifest.py` | Track transformation artifacts | No documentation |

**Impact:** Advanced operators can't discover optimization and reliability features

**Fix:** Create guides in `/docs/guides/operations/` documenting each feature

---

### 6. Incomplete Configuration Documentation (2 files)

| File | Content | Size | Gaps |
|------|---------|------|------|
| `config-files.md` | Configuration file specifications | 940 bytes | Missing pyproject.toml details, .env options, per-project vs global config |
| `ggen-config.md` | ggen.toml options | 1.6 KB | Missing detailed options, transformation config examples, incremental vs atomic modes |

**Impact:** Users can't fully configure system for their needs

**Fix:** Expand both files with complete option documentation and examples

---

### 7. Poor Cross-Reference Coverage (65+ files)

**Current Status:** Only 84 of 149 markdown files (56%) have "See Also" sections

**Impact:**
- Users can't navigate between related documents
- CLI command docs disconnected from how-to guides
- Explanation files don't link to relevant guides
- Tutorial 5 references non-existent ggen-pipeline.md

**Fix:** Add "See Also" sections to all 149 files (65 files need additions)

---

### 8. Undocumented Advanced Features (6 features)

Real functionality in source code without any documentation:

| Feature | Command | Files | Gap |
|---------|---------|-------|-----|
| Hyperdimensional Computing | `hd`, `hdql` | `/src/specify_cli/commands/hd.py`, `hdql.py` | No command docs, no guides, no tutorials |
| Process Mining | `pm` | `/src/specify_cli/commands/pm.py` | No command docs, no guides |
| Workflow Automation | `spiff` | `/src/specify_cli/commands/spiff.py` | No command docs, no guides |
| Dashboards | `dashboards` | `/src/specify_cli/commands/dashboards.py` | No command docs, no guides |
| Caching | `cache` | `/src/specify_cli/commands/cache.py` | Minimal command doc, no strategy guides |
| Dependency Management | `deps` | `/src/specify_cli/commands/deps.py` | Minimal command doc, no guides |

**Impact:** Users cannot discover or use 6 major feature areas

**Fix:** Create command docs + guides for each feature

---

## Nice-To-Have Gaps (Could Fix)

### 9. Missing Ecosystem Documentation

`/docs/ecosystem/` only contains `agi-ingestion.md` (24 KB)

**Missing:**
- Integration points with external tools
- Ecosystem partners and extensions
- Third-party tool integrations (Jaeger, Prometheus, etc.)

**Fix:** Create `/docs/ecosystem/integrations.md` and `/docs/ecosystem/partners.md`

---

### 10. Sparse/Missing Examples

`/docs/examples/` directory exists with subdirectories but minimal content:

| Directory | Status | Need |
|-----------|--------|------|
| `cli-commands/` | Sparse | Real working examples for each command |
| `python-code/` | Sparse | Implementation examples |
| `rdf-specifications/` | Sparse | Real RDF spec examples |
| `sparql-queries/` | Sparse | Working SPARQL query examples |
| `tera-templates/` | Sparse | Real template examples |

**Fix:** Create 15-20 real working examples across directories

---

### 11. Missing Advanced Tutorials (4 tutorials)

Only 7 tutorials (01-07). Missing:

| Tutorial | Topic | Why Missing |
|----------|-------|------------|
| 08-advanced-ggen.md | Recovery, incremental, timeout features | Advanced workflows not documented |
| 09-hyperdimensional.md | HD computing and HDQL | Feature completely undocumented |
| 10-process-mining.md | Process mining workflows | Feature completely undocumented |
| 11-workflow-automation.md | SpiffWorkflow integration | Feature completely undocumented |

**Fix:** Create 4 new tutorial files in `/docs/tutorials/`

---

### 12. Incomplete Error Documentation

`/docs/reference/error-codes.md` has generic templates but missing:
- Actual error messages from real operations
- Real troubleshooting guides per error code
- ggen-specific error messages (from `ggen_errors.py`)

**Fix:** Map actual error messages and add troubleshooting per error

---

## Navigation Integrity Issues

### Broken README Navigation

Three key README files reference non-existent documents:

**`/docs/explanation/README.md`** (Line 34, 45, 67, 89)
- References 4 files that don't exist
- Navigation is broken for explanation section

**`/docs/guides/README.md`** (Lines 36, 45, 54)
- References 7 guide files that don't exist
- Quick-reference table incomplete

**`/docs/reference/README.md`** (Lines 36, 42, 71)
- References telemetry-api.md (missing)
- References definition-of-done.md (missing)
- Quick lookup table incomplete

**Fix:** Update all three README files after creating missing files

---

## Priority Fix Order

### Phase 1: Critical (Fixes Navigation)
1. Create 4 missing explanation files (ggen-pipeline, opentelemetry-design, error-prevention, hyperdimensional-theory)
2. Create 11 missing CLI command documentation files
3. Update README files in explanation/, guides/, reference/

**Effort:** ~12-15 hours
**Impact:** Fixes broken navigation, enables 44% more features

### Phase 2: Important (Improves Discoverability)
4. Create 7 missing how-to guide files
5. Create 2 missing reference files
6. Document 6 advanced ggen operations
7. Expand configuration documentation
8. Add cross-references to 65+ files

**Effort:** ~15-20 hours
**Impact:** Complete feature coverage, full navigation

### Phase 3: Nice-To-Have (Enhances Learning)
9. Create ecosystem documentation
10. Expand examples directory
11. Add 4 advanced tutorials
12. Complete error documentation

**Effort:** ~8-12 hours
**Impact:** Enhanced learning and discoverability

---

## Files Affected Summary

### New Files to Create (33 total)

**Explanation** (4 files):
- `/docs/explanation/ggen-pipeline.md`
- `/docs/explanation/opentelemetry-design.md`
- `/docs/explanation/error-prevention.md`
- `/docs/explanation/hyperdimensional-theory.md`

**Commands** (11 files):
- `/docs/commands/check.md`
- `/docs/commands/dashboards.md`
- `/docs/commands/generated.md`
- `/docs/commands/ggen.md`
- `/docs/commands/hd.md`
- `/docs/commands/hdql.md`
- `/docs/commands/init.md`
- `/docs/commands/jtbd.md`
- `/docs/commands/pm.md`
- `/docs/commands/spiff.md`
- `/docs/commands/version.md`

**How-To Guides** (7 files):
- `/docs/guides/observability/view-traces.md`
- `/docs/guides/ai-integration/setup-ai-agents.md`
- `/docs/guides/ai-integration/token-optimization.md`
- `/docs/guides/ai-integration/documentation-verification.md`
- `/docs/guides/operations/interpret-receipts.md`
- `/docs/guides/architecture/refactor-legacy.md`
- `/docs/guides/jtbd/measure-outcomes.md`

**Reference** (2 files):
- `/docs/reference/telemetry-api.md`
- `/docs/reference/definition-of-done.md`

**Ecosystem** (2 files):
- `/docs/ecosystem/integrations.md`
- `/docs/ecosystem/partners.md`

### Files to Update (3+ files)

- `/docs/explanation/README.md` - Update after creating 4 missing explanation files
- `/docs/guides/README.md` - Update after creating 7 missing guide files
- `/docs/reference/README.md` - Update after creating 2 missing reference files
- 65+ markdown files - Add/update "See Also" cross-references

---

## Verification Checklist

After completing gaps:

- [ ] All 4 explanation files created
- [ ] All 11 CLI command files created
- [ ] All 7 how-to guide files created
- [ ] All 2 reference files created
- [ ] All README files updated with new content
- [ ] All 65+ files have cross-references
- [ ] Navigation testing (all links valid)
- [ ] Build documentation to verify no broken links
- [ ] Update main documentation table of contents

---

## See Also

- `DIATAXIS_REORGANIZATION_PLAN.md` - Original reorganization strategy
- `docs/explanation/README.md` - Explanation documentation index
- `docs/guides/README.md` - How-to guides index
- `docs/reference/README.md` - Reference documentation index

---

**Last Updated:** 2025-12-23
**Next Review:** After Phase 1 completion (critical gaps fixed)
