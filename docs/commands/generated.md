# specify generated

Manage and inspect generated files from RDF specifications.

## Usage

```bash
specify generated [SUBCOMMAND] [OPTIONS]
```

## Description

The `generated` command provides utilities to:
- List all generated files
- Verify files match specifications
- Check generation status
- Inspect generated file details
- Compare versions
- Clean up outdated files

## Subcommands

### list

List all generated files.

```bash
specify generated list [OPTIONS]
```

**Options:**
- `--type` - Filter by type (code, test, doc, all)
- `--category` - Filter by category (commands, operations, runtime, tests)
- `--verbose` - Show details (file size, date)
- `--tree` - Show as tree structure

**Example:**
```bash
specify generated list --verbose

Generated Files (15 total):

src/commands/
  ├─ check.py (325 bytes, 2025-12-23 14:30)
  ├─ init.py (412 bytes, 2025-12-23 14:30)
  ├─ ggen.py (680 bytes, 2025-12-23 14:30)
  └─ ...

tests/e2e/
  ├─ test_commands_check.py (456 bytes, 2025-12-23 14:30)
  ├─ test_commands_init.py (623 bytes, 2025-12-23 14:30)
  └─ ...

docs/
  ├─ commands.md (1.2 KB, 2025-12-23 14:30)
  └─ ...

Total: 15 files, 87 KB
Generated: 2025-12-23 14:30:00
```

### stat

Show statistics about generated files.

```bash
specify generated stat [OPTIONS]
```

Overview and metrics:

```bash
specify generated stat

Generation Statistics:

Files: 15 total
  Code: 8 files (56 KB)
  Tests: 5 files (18 KB)
  Docs: 2 files (13 KB)

Code Lines:
  Total: 1,247 lines
  Commands: 523 lines
  Operations: 487 lines
  Tests: 237 lines

Generation:
  Time: 2.3 seconds
  RDF source: ontology/cli-commands.ttl (4 KB)
  Compression: 87 KB from 4 KB source (22x)

Last sync: 2025-12-23 14:30:00
Status: Current (matches specification)
```

### show

Show content of generated file.

```bash
specify generated show FILEPATH [OPTIONS]
```

Display generated file content:

```bash
specify generated show src/commands/check.py

# Shows file content with syntax highlighting
# (truncated here for space)
def check() -> None:
    """Check that all required tools are available."""

    result = ops.check_impl()
    console.print_result(result)
```

### diff

Compare generated file with source.

```bash
specify generated diff FILEPATH [OPTIONS]
```

Shows what would be regenerated:

```bash
specify generated diff src/commands/check.py

Diff with generated version:

 def check() -> None:
-    """Check that all required tools are available."""
+    """Check all required tools."""

     result = ops.check_impl()
     console.print_result(result)

Status: Source has changed
Recommendation: Run 'ggen sync' to update
```

### verify

Verify file matches specification.

```bash
specify generated verify [FILEPATH] [OPTIONS]
```

Check if file matches generation source:

**Options:**
- `--strict` - Fail on any mismatch
- `--show-hash` - Show file hash
- `--detailed` - Show comparison details

**Example:**
```bash
# Verify all files
specify generated verify

✓ src/commands/check.py ✓ (sha256:abc123...)
✓ src/commands/init.py ✓ (sha256:def456...)
✓ tests/e2e/test_commands.py ✓ (sha256:ghi789...)
⚠ src/commands/cache.py ✗ MANUALLY EDITED
  Expected hash: sha256:xyz789...
  Actual hash: sha256:modified...
  Recommendation: Run 'ggen sync' to regenerate

Overall: 14 of 15 files match specification
Status: NEEDS SYNC (1 file manually edited)
```

### hash

Show hash of generated file.

```bash
specify generated hash FILEPATH
```

Display SHA256 hash:

```bash
specify generated hash src/commands/check.py
abc123def456789... (SHA256)
```

### history

Show version history of generated file.

```bash
specify generated history FILEPATH [OPTIONS]
```

Shows past generations:

```bash
specify generated history src/commands/check.py --limit 5

Generation History (5 recent):

1. 2025-12-23 14:30:00
   Hash: abc123...
   Source: ontology/cli-commands.ttl (v1.2)
   Changes: Updated docstring

2. 2025-12-20 09:15:00
   Hash: def456...
   Source: ontology/cli-commands.ttl (v1.1)
   Changes: Added --verbose option

3. 2025-12-15 16:40:00
   Hash: ghi789...
   Source: ontology/cli-commands.ttl (v1.0)
   Changes: Initial generation

...
```

### receipt

Show receipt information for generation.

```bash
specify generated receipt [OPTIONS]
```

Details about the generation proof:

```bash
specify generated receipt

Generation Receipt:

Generated: 2025-12-23 14:30:00 UTC
ggen version: 5.0.2
Transformation time: 2.3 seconds

RDF Source:
  File: ontology/cli-commands.ttl
  Hash: rdf-abc123...
  Validation: PASSED (SHACL)

Generated Files (15):
  src/commands/check.py: sha256:abc123...
  src/commands/init.py: sha256:def456...
  src/commands/ggen.py: sha256:xyz789...
  ... (12 more)

Verification:
  All files present: ✓
  All hashes match: ✓
  Idempotent: ✓ (generation is repeatable)
  Status: VALID

Reproducibility:
  Same input produces same output: ✓
  Can be regenerated identically: ✓
```

### clean

Remove generated files.

```bash
specify generated clean [OPTIONS]
```

Delete all generated files:

**Options:**
- `--type TYPE` - Only clean specific type (code, test, doc)
- `--dry-run` - Show what would be deleted
- `--except` - Keep specific files/patterns

**Example:**
```bash
specify generated clean --dry-run

Would delete:
  src/commands/check.py (325 bytes)
  src/commands/init.py (412 bytes)
  src/commands/ggen.py (680 bytes)
  ... (12 more files)

Total: 15 files, 87 KB to be deleted

# Actually delete
specify generated clean

✓ Deleted 15 generated files
  87 KB freed
```

### compare

Compare two generations.

```bash
specify generated compare FILE1 FILE2 [OPTIONS]
```

Show differences between versions:

```bash
specify generated compare \
  src/commands/check.py.old \
  src/commands/check.py

Differences:

 def check(self) -> None:
-    """Check tool availability"""
+    """Check that all required tools are available"""

     logger.info("Checking environment...")

+    # Enhanced checks
+    if not verify_python():
+        raise EnvironmentError("Python check failed")
+
     return ops.check_impl()

Changes:
  - Updated docstring (+14 words)
  - Added validation function
  - 3 new lines added
```

## Integration with ggen

### Typical Workflow

```bash
# 1. Edit RDF specification
vim ontology/cli-commands.ttl

# 2. Generate code
specify ggen sync

# 3. Check what was generated
specify generated list --verbose
specify generated show src/commands/check.py

# 4. Verify against specification
specify generated verify

# 5. Run tests on generated code
uv run pytest tests/

# 6. Commit both RDF and generated files
git add . && git commit
```

### Detecting Manual Edits

```bash
# Someone manually edited generated file
vim src/commands/check.py
# (user makes changes)

# Detect the change
specify generated verify
✗ src/commands/check.py ✗ MISMATCH

# Restore from specification
specify ggen sync

# File restored from RDF source
```

## Performance Tips

### Large Projects

For projects with many generated files:

```bash
# Quick status (no verification)
specify generated list

# Full verification (slower)
specify generated verify --strict

# Incremental check (only changed)
specify generated verify --incremental
```

### Caching

Generation results are cached:

```bash
# Clear cache if needed
specify ggen clean --cache-only

# Regenerate (from cache)
specify ggen sync --fast
```

## Troubleshooting

### File Manually Edited But Shouldn't Be

```bash
specify generated verify
✗ src/commands/check.py manually edited

# To restore:
specify ggen sync

# Or just that file:
specify ggen sync --force-files src/commands/check.py
```

### Unsure What Was Generated

```bash
# List all generated files with categories
specify generated list --tree --verbose

# Show which RDF generated which file
specify generated show src/commands/check.py --show-source
# Points to: ontology/cli-commands.ttl (command definition)
```

## See Also

- [ggen.md](./ggen.md) - Generate files from RDF
- `/docs/guides/operations/run-ggen-sync.md` - Full generation workflow
- `/docs/reference/cli-commands.md` - Commands reference
