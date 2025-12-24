# Tutorial 8: Advanced ggen Features

Learn advanced ggen features for optimizing transformations: incremental builds, recovery, timeout handling, and file locking.

**Duration:** 25 minutes
**Prerequisites:** Tutorial 5 (ggen-sync-first-time)
**Difficulty:** Advanced

## Learning Goals

After this tutorial, you'll understand:
- Incremental builds (faster regeneration)
- Recovery from interrupted transformations
- Timeout configuration and tuning
- Concurrent access control via file locking
- Preflight validation
- Manifest tracking

## Part 1: Incremental Builds

### The Problem

Every `ggen sync` regenerates ALL files, even unchanged specs:

```bash
$ ggen sync
[μ₁ Normalize] ontology/cli-commands.ttl... ✓
[μ₂ Extract] Running 5 SPARQL queries... ✓
[μ₃ Emit] Rendering 8 templates... ✓ (slow!)
[μ₄ Canonicalize] Formatting output... ✓
[μ₅ Receipt] Creating proof... ✓

Duration: 2.3 seconds
Files changed: 0 (nothing new)
```

**Issue:** Wasted 2.3 seconds even though nothing changed!

### Solution: Incremental Mode

```bash
# Enable incremental builds
export GGEN_INCREMENTAL=true

# Or in ggen.toml
[ggen]
incremental = true
incremental_dir = ".ggen/incremental"

# Now run sync
ggen sync

[μ₁ Normalize] (unchanged, skipping)
[μ₂ Extract] (unchanged, skipping)
[μ₃ Emit] (unchanged, skipping)
[μ₄ Canonicalize] (unchanged, skipping)
[μ₅ Receipt] Creating proof... ✓

Duration: 0.1 seconds (23x faster!)
Files changed: 0
```

### How It Works

```
First run (full):
  Save spec hashes to .ggen/incremental/
  Generate all files
  Create receipt

Second run (incremental):
  Compare spec hashes against .ggen/incremental/
  Unchanged? Skip that stage!
  Only changed specs → regen affected files
```

### When to Use Incremental

```
✓ Use incremental:
  - During development (frequent syncs)
  - CI/CD (many builds)
  - Large projects with many specs

✗ Don't use incremental:
  - First build (need full generation)
  - After dependency changes (might miss effects)
  - When you want to verify reproducibility
```

## Part 2: Recovery from Interruption

### The Problem

What if `ggen sync` gets interrupted?

```bash
$ ggen sync
[μ₁ Normalize] ...✓
[μ₂ Extract] ...✓
[μ₃ Emit] ...✓
^C  # User interrupted!

# Some files generated, others incomplete
# How to continue safely?
```

### Solution: Recovery Mode

```bash
# Resume interrupted build
ggen sync --recovery

[Checking state from .ggen/state.json]
[Last completed stage: Emit]
[Resuming from Canonicalize]

[μ₄ Canonicalize] (resuming)... ✓
[μ₅ Receipt] Creating proof... ✓

Duration: 0.5 seconds
Completed: Yes
```

### How It Works

```
During generation:
  Save state after each stage to .ggen/state.json

If interrupted:
  Next run: Check .ggen/state.json
  Resume from last completed stage
  Skip earlier stages
  Continue cleanly
```

### State Inspection

```bash
# View current state
cat .ggen/state.json | jq

{
  "status": "in_progress",
  "last_completed_stage": "emit",
  "timestamp": "2025-12-23T14:35:00.000Z",
  "files_generated": 12,
  "files_remaining": 3
}

# Clear state if needed
rm .ggen/state.json

# Next sync will start fresh
```

## Part 3: Timeout Configuration

### The Problem

Some transformations are slow:

```bash
ggen sync

[μ₂ Extract] Running SPARQL queries...
(waiting... 5 seconds...)
(waiting... 10 seconds...)
(waiting... 30 seconds...)
(still waiting!)

# Hung process, no timeout!
```

### Solution: Configure Timeouts

```toml
# ggen.toml
[ggen]
# Transformation timeout (seconds)
timeout = 30

# Individual stage timeouts
timeout_normalize = 5
timeout_extract = 15
timeout_emit = 10
timeout_canonicalize = 5
timeout_receipt = 5
```

Or via environment:

```bash
export GGEN_TIMEOUT=30
export GGEN_TIMEOUT_EXTRACT=15

ggen sync
```

### Timeout Behavior

```bash
ggen sync

[μ₂ Extract] Running SPARQL queries...
[... 15 seconds pass ...]
[✗ TIMEOUT] Extract stage exceeded 15 seconds

[Cancelling remaining queries]
[Rolling back partial results]
[Saving error state to .ggen/error.json]

Error: Transform failed: Extract stage timeout
Exit code: 6 (timeout)
```

### Handling Timeouts

**Option 1: Increase timeout**
```bash
ggen sync --timeout 60
```

**Option 2: Optimize query**
```bash
# View slow query
cat .ggen/error.json | jq '.slow_queries'

# Optimize it
vim sparql/extract.rq

# Try again
ggen sync
```

**Option 3: Split work**
```
# Instead of extracting everything:
[ggen.extractors]
[[ ggen.extractors.commands ]]
rdf_source = "ontology/cli-commands.ttl"

[[ggen.extractors.docs]]
rdf_source = "memory/*.ttl"

# Now: ggen sync
# Runs extractors in parallel, faster!
```

## Part 4: File Locking for Concurrent Access

### The Problem

Multiple processes running `ggen sync` simultaneously:

```bash
# Terminal 1
$ ggen sync
[μ₃ Emit] Rendering src/commands/init.py...

# Terminal 2 (same time!)
$ ggen sync
[μ₃ Emit] Rendering src/commands/init.py...

# Both writing same file! Corruption risk!
```

### Solution: File Locking

```bash
# ggen.toml
[ggen]
use_file_lock = true
lock_file = ".ggen/ggen.lock"
lock_timeout = 60
```

Now only one process at a time:

```bash
# Terminal 1
$ ggen sync
[Acquiring lock... ✓]
[μ₁ Normalize] ...
[μ₂ Extract] ...
[μ₃ Emit] ...
[μ₄ Canonicalize] ...
[μ₅ Receipt] ...
[Releasing lock]

Duration: 2.3 seconds

# Terminal 2
$ ggen sync (same time)
[Waiting for lock...]
[Lock acquired by terminal 1, waiting...]
[Lock released after 2.3 seconds]
[Acquiring lock... ✓]
[Skipped (unchanged, incremental)]
[Releasing lock]

Duration: 0.1 seconds
```

### Lock Debugging

```bash
# Check lock status
cat .ggen/ggen.lock

{
  "locked": true,
  "process_id": 12345,
  "process_name": "ggen",
  "acquired_at": "2025-12-23T14:35:00.000Z",
  "expires_at": "2025-12-23T14:36:00.000Z" (60s timeout)
}

# Stuck lock? Force release
rm .ggen/ggen.lock  # ⚠️ Use only if process actually dead
```

## Part 5: Preflight Validation

### The Problem

Transformation fails after starting:

```bash
ggen sync
[μ₁ Normalize] ... ✓
[μ₂ Extract] ... ✓
[μ₃ Emit] ... (starts writing files)
[✗ ERROR] Template syntax error in templates/command.tera
[Partial files written, incomplete output]
```

### Solution: Preflight Check

```bash
# Validate before transforming
ggen preflight

✓ RDF syntax valid
✓ SHACL validation passes
✓ All SPARQL queries valid
✓ All templates have valid Tera syntax
✓ All output directories writable
✓ Disk space available: 2.3 GB

Status: READY TO SYNC

# If problems found:
ggen preflight --verbose

✗ Template error: templates/command.tera
  Line 42: Undefined variable `cmd.description`

Fix: Check template for typo or missing variable
```

### Preflight Integration

```bash
# Automatically run preflight before sync
ggen sync --preflight

[Preflight check]
✓ All checks passed

[ggen sync]
[μ₁ Normalize] ... ✓
[μ₂ Extract] ... ✓
...
```

## Part 6: Manifest Tracking

### What's a Manifest?

A manifest tracks all files involved in generation:

```json
{
  "inputs": {
    "rdf_sources": [
      "ontology/cli-commands.ttl",
      "ontology/spec-kit-schema.ttl"
    ],
    "sparql_queries": [
      "sparql/command-extract.rq"
    ],
    "templates": [
      "templates/command.tera",
      "templates/test.tera"
    ]
  },
  "outputs": [
    "src/commands/check.py",
    "src/commands/init.py",
    "tests/e2e/test_commands.py"
  ]
}
```

### Use Manifests

**Dependency tracking:**
```bash
# What inputs affect which outputs?
ggen manifest graph

src/commands/check.py depends on:
  - ontology/cli-commands.ttl
  - templates/command.tera

# If either changes, must regenerate src/commands/check.py
```

**Incremental decisions:**
```bash
# What changed since last sync?
ggen manifest diff

Changed inputs:
  - ontology/cli-commands.ttl (+5 lines)

Affected outputs:
  - src/commands/check.py
  - src/commands/init.py
  - tests/e2e/test_commands.py

Must regenerate: 3 files out of 15
Unchanged: 12 files (skip)
```

## Part 7: Complete Advanced Example

```bash
# .env - Development environment
export GGEN_INCREMENTAL=true
export GGEN_TIMEOUT=60
export GGEN_USE_FILE_LOCK=true
export GGEN_PREFLIGHT=true

# ggen.toml - Configuration
[ggen]
version = "5.0.2"
incremental = true
incremental_dir = ".ggen/incremental"
timeout = 60
use_file_lock = true
lock_file = ".ggen/ggen.lock"
preflight = true

# Now: Advanced workflow
$ ggen sync

[Preflight check]
✓ All checks passed

[Acquiring lock for exclusive access]
✓ Lock acquired

[Incremental build]
[μ₁ Normalize] ontology/cli-commands.ttl (unchanged, skip)
[μ₂ Extract] (unchanged, skip)
[μ₃ Emit] Rendering templates...
  ontology/cli-commands.ttl changed
  → Regenerate: src/commands/cache.py
  → Regenerate: tests/e2e/test_commands_cache.py
  → Skip: src/commands/check.py (unchanged)
[μ₄ Canonicalize] Formatting 2 files...
[μ₅ Receipt] Updating proof...

[Releasing lock]

Duration: 0.8 seconds (incremental)
Files generated: 2 out of 15
Files unchanged: 13 (skipped)
Status: ✓ SUCCESS
```

## Summary

**Incremental builds:** Skip unchanged specs (23x faster)
**Recovery:** Resume interrupted transformations
**Timeouts:** Prevent hanging with configurable limits
**File locking:** Serialize concurrent access safely
**Preflight validation:** Catch errors before transformation
**Manifest tracking:** Understand dependencies

## See Also

- Tutorial 5: ggen-sync-first-time.md
- `/docs/commands/ggen.md` - ggen command reference
- `/docs/guides/operations/run-ggen-sync.md` - Full guide
- `/docs/explanation/ggen-pipeline.md` - Transformation stages
- `/docs/reference/ggen-config.md` - Configuration reference
