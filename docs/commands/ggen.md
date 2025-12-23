# specify ggen

Transform RDF specifications into code, documentation, and tests.

## Usage

```bash
specify ggen [SUBCOMMAND] [OPTIONS]
```

## Description

The `ggen` command manages the RDF-to-code transformation pipeline (μ₁-μ₅). It:
1. Validates RDF specifications (μ₁ Normalize)
2. Extracts data via SPARQL (μ₂ Extract)
3. Renders Tera templates (μ₃ Emit)
4. Canonicalizes output (μ₄ Canonicalize)
5. Generates verification receipt (μ₅ Receipt)

This is the core of spec-kit's spec-driven development model.

## Subcommands

### sync

Run the complete transformation pipeline.

```bash
specify ggen sync [OPTIONS]
```

**Options:**
- `--verbose, -v` - Show detailed transformation steps
- `--config PATH` - Custom ggen.toml configuration
- `--rdf-source PATH` - Override RDF source file
- `--force` - Regenerate even if files haven't changed
- `--incremental` - Skip unchanged specifications (faster)
- `--dry-run` - Show what would be generated without writing

**Examples:**
```bash
# Standard sync
specify ggen sync
# ✓ Normalized 1 RDF file
# ✓ Extracted 5 specifications
# ✓ Generated 15 files
# ✓ Receipt saved to .ggen/receipt.json

# Verbose output
specify ggen sync --verbose
# [μ₁ Normalize] ontology/cli-commands.ttl... ✓
# [μ₂ Extract] Running 5 SPARQL queries... ✓
# [μ₃ Emit] Rendering 8 templates... ✓
# [μ₄ Canonicalize] Formatting Python code... ✓
# [μ₅ Receipt] Creating SHA256 proof... ✓

# Dry run (show what would happen)
specify ggen sync --dry-run
# Would create: src/commands/check.py (325 bytes)
# Would create: src/commands/init.py (412 bytes)
# ...
# Would modify: .ggen/receipt.json
```

### verify

Verify generated files match RDF source.

```bash
specify ggen verify [OPTIONS]
```

Compares current files against receipt hashes to detect:
- Manual edits to generated files
- Spec-code synchronization status
- Out-of-date generated artifacts

**Options:**
- `--verbose, -v` - Show all files checked
- `--strict` - Fail if any mismatch found
- `--receipt PATH` - Use custom receipt file

**Output:**
```bash
$ specify ggen verify
✓ All 15 generated files match specification
✓ Last sync: 2025-12-23 14:30:00
✓ RDF source: ontology/cli-commands.ttl (sha256:abc123...)
✓ Specification version: 1.2.0
```

```bash
$ specify ggen verify --verbose
✓ src/commands/check.py ✓
✓ src/commands/init.py ✓
✗ src/commands/cache.py ✗ MANUALLY EDITED
  Receipt hash: sha256:def456...
  Current hash: sha256:xyz789...
  Recommendation: Run 'ggen sync' to regenerate

❌ Verification failed: 1 file manually edited
```

### status

Show transformation status and statistics.

```bash
specify ggen status [OPTIONS]
```

**Example output:**
```bash
$ specify ggen status
ggen Version: 5.0.2
Configuration: ggen.toml

Transformations:
  cli-commands
    Source: ontology/cli-commands.ttl
    Generated: 15 files
    Last sync: 2025-12-23 14:30:00
    Status: ✓ Current

RDF Statistics:
  Classes: 12
  Instances: 48
  Properties: 156
  SHACL constraints: 8

Output Statistics:
  Python files: 15
  Test files: 5
  Documentation: 3
  Total size: 87 KB

Performance:
  Last sync duration: 2.3 seconds
  Files changed: 5 (regenerated), 10 (unchanged)
```

### clean

Remove all generated artifacts.

```bash
specify ggen clean [OPTIONS]
```

**Options:**
- `--verbose, -v` - Show files being removed
- `--keep-receipt` - Keep receipt.json (for verification)
- `--dry-run` - Show what would be deleted

**Example:**
```bash
$ specify ggen clean --verbose
Removing generated files:
  ✓ Deleted: src/commands/check.py
  ✓ Deleted: src/commands/init.py
  ✓ Deleted: tests/e2e/test_commands.py
✓ Removed 15 files
```

### watch

Watch RDF files and auto-sync on changes.

```bash
specify ggen watch [OPTIONS]
```

Automatically re-runs `sync` when RDF files change. Useful during specification development.

**Options:**
- `--debounce MS` - Wait for multiple changes (default: 500ms)
- `--exclude PATTERN` - Ignore files matching pattern

**Example:**
```bash
$ specify ggen watch --debounce 1000
Watching ontology/ for changes...
  ontology/cli-commands.ttl changed
  Running ggen sync...
  ✓ Generated 15 files in 2.1s
  ontology/cli-commands.ttl changed
  Running ggen sync...
  ✓ Generated 15 files in 2.0s
```

## Options (Global)

These options work with all `ggen` subcommands:

### --config PATH
**Type:** File path
**Default:** `ggen.toml`

Custom configuration file:

```bash
specify ggen sync --config custom-ggen.toml
```

### --profile NAME
**Type:** String
**Default:** `default`

Configuration profile to use:

```bash
# ggen.toml
[ggen.profiles.dev]
# Development settings

[ggen.profiles.prod]
# Production settings

specify ggen sync --profile prod
```

### --verbose, -v
**Type:** Flag

Detailed transformation output:

```bash
specify ggen sync --verbose
```

### --quiet, -q
**Type:** Flag

Suppress all output except errors:

```bash
specify ggen sync --quiet
```

## Configuration (ggen.toml)

```toml
[ggen]
version = "5.0.2"

# Timeout for transformation (seconds)
timeout = 30

# Maximum output file size (bytes)
max_output_size = 10485760  # 10 MB

# Incremental build settings
incremental = true
incremental_dir = ".ggen/incremental"

# Exporting settings
[[transformation]]
name = "cli-commands"
rdf_source = "ontology/cli-commands.ttl"
sparql_queries = ["sparql/command-extract.rq"]
templates = ["templates/command.tera"]
output_dir = "src/commands"
```

## Workflow

Typical spec-driven development workflow:

```bash
# 1. Edit RDF specification
vim ontology/cli-commands.ttl

# 2. Watch for changes and auto-sync
specify ggen watch &

# 3. Edit SPARQL queries (optional)
vim sparql/command-extract.rq

# 4. Customize Tera templates (optional)
vim templates/command.tera

# 5. Verify everything works
specify ggen verify

# 6. Run tests
uv run pytest tests/

# 7. Commit both RDF source AND generated files
git add . && git commit
```

## Advanced Features

### Incremental Builds

Only regenerate changed specifications:

```bash
specify ggen sync --incremental
# Faster if only 1 file changed
```

### Dry Run

Preview changes without writing:

```bash
specify ggen sync --dry-run
# Shows: Would create 5 files, would modify 3 files, would delete 0 files
```

### Recovery

If sync is interrupted, recovery features help:

```bash
specify ggen sync
# Interrupted by Ctrl+C

specify ggen sync --recovery
# Continues from where it stopped
```

### Timeout Control

Set custom timeout for slow transformations:

```bash
specify ggen sync --timeout 60
# Wait up to 60 seconds
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Sync successful, all files generated |
| 1 | Validation failed (bad RDF) |
| 2 | SPARQL query error |
| 3 | Template rendering error |
| 4 | Canonicalization failed |
| 5 | I/O error (permission, disk full) |
| 6 | Timeout (transformation too slow) |

## Troubleshooting

### SHACL Validation Failed
```bash
$ specify ggen sync
✗ SHACL validation failed in ontology/cli-commands.ttl

  Shape: CommandShape
  Property: sk:description
  Error: sh:minLength constraint violated
  Details: "OK" has length 2, minimum is 10
  Line: 47

💡 Fix: Edit the RDF file and add a longer description
  vim ontology/cli-commands.ttl
```

### SPARQL Query Error
```bash
$ specify ggen sync
✗ SPARQL extraction failed

  Query: sparql/command-extract.rq
  Error: Undefined variable ?name
  Line: 8

💡 Fix: Check SPARQL syntax
  cat sparql/command-extract.rq
```

### Template Rendering Error
```bash
$ specify ggen sync
✗ Template rendering failed

  Template: templates/command.tera
  Error: Unknown variable "cmd.description"
  Context: {"cmd": {"name": "check", ...}}

💡 Fix: Check variable names in template
  vim templates/command.tera
```

## See Also

- `ggen-pipeline.md` (explanation) - How the 5-stage transformation works
- `/docs/guides/operations/run-ggen-sync.md` - Detailed how-to guide
- `/docs/reference/ggen-config.md` - Configuration reference
- [Tutorial 5: ggen Sync](../tutorials/05-ggen-sync-first-time.md) - Learning guide
