# ggen sync: Failure Mode and Effects Analysis (FMEA)

**Version**: 5.0.0
**Date**: 2025-12-21
**Standard**: ISO/IEC 60812 FMEA (modified for software)
**Status**: PRODUCTION RISK ASSESSMENT

---

## Executive Summary

**RPN Analysis** (Risk Priority Number = Severity × Occurrence × Detection):

- **Critical RPN (>350)**: 8 failure modes
- **High RPN (200-350)**: 12 failure modes
- **Medium RPN (100-200)**: 8 failure modes
- **Low RPN (<100)**: 4 failure modes

**Overall Risk Assessment**: HIGH - Multiple critical failure modes not adequately detected or prevented.

---

## FMEA Table: Critical Failure Modes (RPN > 350)

### 1. Invalid RDF Input Not Detected

| Attribute | Value |
|-----------|-------|
| **Failure Mode** | Invalid RDF/Turtle syntax passed to SPARQL engine |
| **Effect on System** | SPARQL query fails silently; incorrect output generated |
| **Effect on User** | Corrupted output files; data loss potential |
| **Severity (S)** | 9 (Data corruption) |
| **Current Detection** | Parser errors only; schema validation absent |
| **Occurrence (O)** | 7 (Common with manual RDF editing) |
| **Detection (D)** | 6 (User must inspect output manually) |
| **RPN** | **378** |
| **Root Causes** | No SHACL shape validation; minimal error reporting |
| **Prevention** | Implement SHACL validation pre-processing |
| **Detection Improvement** | Add SPARQL result validation; diff preview |
| **Mitigation** | Dry-run with strict validation; mandatory review |

### 2. Silent Data Corruption on Partial Failure

| Attribute | Value |
|-----------|-------|
| **Failure Mode** | Transformation fails mid-stream; partial output written |
| **Effect on System** | Incomplete/inconsistent output in filesystem |
| **Effect on User** | Corrupted code/docs; build failures in CI/CD |
| **Severity (S)** | 10 (Critical data corruption) |
| **Current Detection** | Exit code returned; no artifact cleanup |
| **Occurrence (O)** | 6 (Rare but happens on disk full, network issues) |
| **Detection (D)** | 7 (User sees partial files; hard to detect programmatically) |
| **RPN** | **420** |
| **Root Causes** | No transaction semantics; no atomic writes; no rollback |
| **Prevention** | Implement staging directory + atomic moves |
| **Detection Improvement** | Checksum validation; manifest file |
| **Mitigation** | Always use --dry-run first; manual verification |

### 3. SPARQL Query Hangs Indefinitely

| Attribute | Value |
|-----------|-------|
| **Failure Mode** | Complex SPARQL query causes infinite loop or exponential backtracking |
| **Effect on System** | Process consumes 100% CPU; blocks pipeline indefinitely |
| **Effect on User** | Build/CI pipeline stuck; manual intervention required |
| **Severity (S)** | 8 (Pipeline blockage) |
| **Current Detection** | None (no timeout mechanism) |
| **Occurrence (O)** | 5 (Depends on query complexity; can happen with large datasets) |
| **Detection (D)** | 7 (User must manually kill process) |
| **RPN** | **280** | ❌ **UPDATED to 350+** if OOM occurs

| Attribute | Value |
|-----------|-------|
| **Prevention** | Hardcode 30-second SPARQL timeout (per pipeline config) |
| **Detection Improvement** | Progress indicator; resource monitoring |
| **Mitigation** | Pre-test SPARQL queries on sample data; set max execution time |

### 4. Conflicting Output Not Resolved

| Attribute | Value |
|-----------|-------|
| **Failure Mode** | Multiple transformations write same output file; no conflict resolution |
| **Effect on System** | Last write wins; earlier files overwritten silently |
| **Effect on User** | Lost work; confusing output; manual merge required |
| **Severity (S)** | 8 (Data loss) |
| **Current Detection** | --force flag available but silently overwrites |
| **Occurrence (O)** | 6 (Common in concurrent CI/CD) |
| **Detection (D)** | 8 (User may not notice until testing) |
| **RPN** | **384** |
| **Root Causes** | No file locking; no merge strategy; limited conflict reporting |
| **Prevention** | Content-hash tracking; detect overwrites before writing |
| **Detection Improvement** | Detailed conflict report with --force option |
| **Mitigation** | Use --dry-run to preview conflicts; implement manifest versioning |

### 5. Out-of-Memory on Large Inputs

| Attribute | Value |
|-----------|-------|
| **Failure Mode** | Large SPARQL result set loaded entirely into memory |
| **Effect on System** | OOM exception; process killed by OS; incomplete output |
| **Effect on User** | Transformation fails mysteriously; no clear error |
| **Severity (S)** | 9 (Service unavailable) |
| **Current Detection** | System OOM killer; no application-level limits |
| **Occurrence (O)** | 5 (Depends on input size; 100MB+ RDF triggers) |
| **Detection (D)** | 6 (vague "Process killed" message) |
| **RPN** | **270** | ❌ **UPDATED to 360** if OOM doesn't report clearly

| Attribute | Value |
|-----------|-------|
| **Prevention** | Implement streaming SPARQL results; memory limits |
| **Detection Improvement** | Explicit OOM error message; resource warnings |
| **Mitigation** | Monitor memory; limit SPARQL result size; process in batches |

### 6. Transformation Dependency Ordering Wrong

| Attribute | Value |
|-----------|-------|
| **Failure Mode** | Transformation A depends on output from B, but B runs after A |
| **Effect on System** | Incorrect/incomplete output; build failures |
| **Effect on User** | Broken code generation; debugging nightmare |
| **Severity (S)** | 9 (Correctness failure) |
| **Current Detection** | None (no dependency tracking) |
| **Occurrence (O)** | 7 (Common when adding new transformations) |
| **Detection (D)** | 5 (Only apparent during testing) |
| **RPN** | **315** | ❌ **UPDATED to 400+** without dependency graph

| Attribute | Value |
|-----------|-------|
| **Prevention** | Build dependency graph; topological sort transformations |
| **Detection Improvement** | Explicit dependency validation; DAG check |
| **Mitigation** | Manual ordering in manifest; pre-run validation |

### 7. Template Rendering Produces Invalid Code

| Attribute | Value |
|-----------|-------|
| **Failure Mode** | Tera template rendering produces syntactically invalid code |
| **Effect on System** | Generated code fails to parse; build breaks |
| **Effect on User** | Broken output; requires manual fixes |
| **Severity (S)** | 7 (Output invalid) |
| **Current Detection** | Downstream build/compiler catches it |
| **Occurrence (O)** | 6 (Template bugs; schema changes) |
| **Detection (D)** | 3 (Build system catches immediately) |
| **RPN** | **126** | ❌ **UPDATED to 300+** if no build validation

| Attribute | Value |
|-----------|-------|
| **Prevention** | Validate output syntax immediately after rendering |
| **Detection Improvement** | Built-in language-specific validators |
| **Mitigation** | Mandatory --dry-run with validation; code review templates |

### 8. Configuration Manifest Not Found or Broken

| Attribute | Value |
|-----------|-------|
| **Failure Mode** | ggen.toml missing or malformed; transformations skipped silently |
| **Effect on System** | No transformations run; users unaware |
| **Effect on User** | Missing generated files; broken pipeline |
| **Severity (S)** | 8 (Silent failure) |
| **Current Detection** | --manifest flag broken; silently ignored |
| **Occurrence (O)** | 8 (Very common: manifest move, deletion, typo) |
| **Detection (D)** | 8 (User discovers on testing phase) |
| **RPN** | **512** |
| **Root Causes** | --manifest flag not implemented; no validation |
| **Prevention** | Fix --manifest flag; validate manifest format upfront |
| **Detection Improvement** | Clear error message if manifest missing/invalid |
| **Mitigation** | Fail fast with detailed error; check file existence first |

---

## FMEA Table: High RPN Failure Modes (200-350)

### 9. SPARQL Query Returns Unexpected Results

| RPN | Severity | Occurrence | Detection |
|-----|----------|-----------|-----------|
| 280 | 7 | 8 | 5 |

**Failure Mode**: SPARQL query logic incorrect; returns wrong data
**Prevention**: Unit test SPARQL queries; validate against schema
**Detection**: Query result validation; sample output verification
**Mitigation**: Dry-run + manual review; SPARQL linting

### 10. File Permissions Prevent Output Write

| RPN | Severity | Occurrence | Detection |
|-----|----------|-----------|-----------|
| 224 | 8 | 7 | 4 |

**Failure Mode**: Target directory read-only or missing write permission
**Prevention**: Pre-flight permission checks; fallback directories
**Detection**: Clear permission error message
**Mitigation**: Check permissions before start; use temp directory

### 11. Disk Space Exhaustion

| RPN | Severity | Occurrence | Detection |
|-----|----------|-----------|-----------|
| 240 | 8 | 6 | 5 |

**Failure Mode**: Output directory full; write fails mid-stream
**Prevention**: Check available space before starting
**Detection**: Explicit disk full error
**Mitigation**: Monitor disk space; implement cleanup

### 12. Schema File Path Not Found

| RPN | Severity | Occurrence | Detection |
|-----|----------|-----------|-----------|
| 252 | 9 | 7 | 4 |

**Failure Mode**: Referenced schema file doesn't exist; silently skipped
**Prevention**: Validate all file paths exist before processing
**Detection**: Clear file not found error
**Mitigation**: Absolute paths; path verification

### 13. Template File Missing or Broken

| RPN | Severity | Occurrence | Detection |
|-----|----------|-----------|-----------|
| 210 | 7 | 6 | 5 |

**Failure Mode**: Tera template file missing, invalid syntax, or circular includes
**Prevention**: Validate template syntax upfront; check existence
**Detection**: Clear template error message with line number
**Mitigation**: Template linting; dry-run validation

### 14. SPARQL Timeout Not Handled

| RPN | Severity | Occurrence | Detection |
|-----|----------|-----------|-----------|
| 280 | 8 | 7 | 5 |

**Failure Mode**: SPARQL query takes too long; process hangs
**Prevention**: Implement configurable timeout (default 30s)
**Detection**: Timeout error message with query name
**Mitigation**: Monitor execution time; pre-test complex queries

### 15. Concurrent ggen sync Invocations

| RPN | Severity | Occurrence | Detection |
|-----|----------|-----------|-----------|
| 288 | 8 | 8 | 4.5 |

**Failure Mode**: Two ggen sync processes run simultaneously; file corruption
**Prevention**: Lock file mechanism; queue transformations
**Detection**: Lock acquisition failure with helpful message
**Mitigation**: Serial execution; use file locks or process locks

### 16. Environment Variable Not Set

| RPN | Severity | Occurrence | Detection |
|-----|----------|-----------|-----------|
| 196 | 7 | 7 | 4 |

**Failure Mode**: Required env var (HOME, USER, etc.) missing; path resolution fails
**Prevention**: Validate required env vars at startup
**Detection**: Clear missing env var error
**Mitigation**: Default values for optional vars; explicit validation

### 17. Incompatible ggen Version

| RPN | Severity | Occurrence | Detection |
|-----|----------|-----------|-----------|
| 224 | 8 | 7 | 4 |

**Failure Mode**: ggen.toml built for v5.0.2 but v5.0.0 running
**Prevention**: Check version compatibility upfront
**Detection**: Clear version mismatch error
**Mitigation**: Version pinning in manifest; migration guides

### 18. Template Encoding Issues (UTF-8)

| RPN | Severity | Occurrence | Detection |
|-----|----------|-----------|-----------|
| 168 | 7 | 6 | 4 |

**Failure Mode**: Non-UTF8 characters in template cause corruption
**Prevention**: Enforce UTF-8 validation on input/output
**Detection**: Clear encoding error message
**Mitigation**: Validate file encodings; normalize input

### 19. Path Traversal in Output File

| RPN | Severity | Occurrence | Detection |
|-----|----------|-----------|-----------|
| 252 | 9 | 7 | 4 |

**Failure Mode**: Malicious manifest specifies output like ../../../etc/passwd
**Prevention**: Validate output paths; reject absolute/parent traversal
**Detection**: Path validation error
**Mitigation**: Sandboxed output directory; path canonicalization

### 20. Silent SPARQL Timeout

| RPN | Severity | Occurrence | Detection |
|-----|----------|-----------|-----------|
| 280 | 8 | 7 | 5 |

**Failure Mode**: Query times out but returns partial empty results
**Prevention**: Explicit timeout handling; don't silently return empty
**Detection**: Timeout error vs empty result distinction
**Mitigation**: Require minimum result validation

---

## Medium RPN Failure Modes (100-200)

| Rank | Failure Mode | RPN | Mitigation |
|------|--------------|-----|-----------|
| 21 | Schema validation too strict/lenient | 168 | SHACL tuning; test coverage |
| 22 | Output formatting inconsistent | 144 | Format validation; style checks |
| 23 | Large file handling (>100MB) | 140 | Streaming; memory management |
| 24 | Unicode normalization issues | 126 | Normalization on I/O; tests |
| 25 | Relative path resolution broken | 156 | Path normalization; tests |
| 26 | SPARQL query cache poisoning | 132 | Cache invalidation; versioning |
| 27 | Missing dependencies in manifest | 144 | Dependency validation; docs |
| 28 | Circular template includes | 108 | Include tracking; cycle detection |

---

## Low RPN Failure Modes (<100)

| Rank | Failure Mode | RPN | Mitigation |
|------|--------------|-----|-----------|
| 29 | Color output in CI/CD logs | 42 | Detect TTY; disable colors |
| 30 | Help text doesn't explain modes | 56 | Improve --help documentation |
| 31 | Verbose flag doesn't show enough | 63 | Structured JSON logging option |
| 32 | Error recovery too aggressive | 48 | Configurable recovery strategy |

---

## Risk Priority Matrix

```
SEVERITY (Y-AXIS) vs OCCURRENCE (X-AXIS)

CRITICAL (S=9-10)
  ■■ Config manifest (RPN 512)
  ■■ Silent data corruption (RPN 420)
  ■■ Invalid RDF undetected (RPN 378)

HIGH (S=7-8)
  ■■ Path traversal (RPN 252)
  ■■ Concurrent access (RPN 288)
  ■■ Version incompatibility (RPN 224)

MEDIUM (S=5-6)
  ■ Output formatting (RPN 144)
  ■ Large file handling (RPN 140)
```

---

## Recommended Action Plan

### IMMEDIATE (Week 1)
1. Fix --manifest flag (enable ggen.toml loading)
2. Add file existence validation
3. Implement file locking for concurrent access
4. Add pre-flight directory/permission checks

### SHORT-TERM (Weeks 2-4)
5. Implement SHACL validation
6. Add transaction semantics (atomic writes)
7. Implement SPARQL timeout (30s default)
8. Add comprehensive input validation

### MEDIUM-TERM (Month 2)
9. Add error recovery and cleanup
10. Implement output validation
11. Add structured logging
12. Document all error scenarios

### LONG-TERM (Q2-Q3 2025)
13. Implement incremental mode
14. Add observability/OTEL
15. Create test suite for FMEA scenarios
16. Security audit for path traversal

---

## Conclusion

**Risk Assessment**: ggen sync has **8 critical failure modes** that could cause:
- Silent data corruption
- Pipeline blockage
- Data loss
- Security vulnerabilities

**Recommendation**: Address RPN > 300 failures before production use. Implement manifest validation, SHACL checking, and transaction semantics immediately.

