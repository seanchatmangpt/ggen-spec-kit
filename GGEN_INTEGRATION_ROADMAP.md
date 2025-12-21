# ggen Integration Roadmap - Constitutional Equation Implementation

**Version**: 1.0
**Status**: Week 1 Complete - Weeks 2-4 Planned
**Target**: Complete μ₁-μ₅ pipeline for spec-kit v1.0

---

## Executive Summary

This roadmap documents the path to complete implementation of the **constitutional equation**:

```
spec.md = μ(feature.ttl)
```

Where `μ` is a five-stage deterministic transformation that guarantees:
- **Idempotence**: μ∘μ = μ (same input always produces same output)
- **Verifiability**: SHA256 receipts prove correctness
- **Automation**: RDF is single source of truth, markdown is generated artifact

**Current Status** (Week 1 Complete):
- ✅ Local ggen v5.0.0 built and available at `/Users/sac/ggen-spec-kit/tools/ggen-cli`
- ✅ Basic sync command working (μ₁, μ₂, μ₃ partial)
- ⏳ Missing μ₄ canonicalization and μ₅ receipt generation

**Goal**: Complete all five stages by Week 4, enabling full RDF-first workflow.

---

## The Five-Stage Pipeline (μ₁ → μ₂ → μ₃ → μ₄ → μ₅)

### Overview

```
┌──────────┐    μ₁     ┌──────────┐    μ₂     ┌──────────┐
│ RDF/TTL  │ ────────> │ Validated│ ────────> │ SPARQL   │
│  Input   │ Normalize │   Graph  │  Extract  │ Results  │
└──────────┘           └──────────┘           └──────────┘
                                                    │
                                                    │ μ₃
                                                    ▼
┌──────────┐    μ₅     ┌──────────┐    μ₄     ┌──────────┐
│ Receipt  │ <──────── │  Final   │ <──────── │ Rendered │
│ (SHA256) │  Receipt  │ Markdown │Canonicalize│ Markdown │
└──────────┘           └──────────┘           └──────────┘
```

### Stage μ₁: NORMALIZE - RDF Validation

**Purpose**: Load RDF, validate SHACL shapes, ensure data integrity

**Status**: ✅ **Partially Working**

**What It Does**:
1. Loads RDF/Turtle files using Oxigraph
2. Validates against SHACL shapes defined in schema
3. Reports constraint violations
4. Fails fast on validation errors (configurable)

**Files Involved**:
- **Rust**: `/Users/sac/ggen-spec-kit/tools/ggen-cli/src/main.rs` (lines 71-100, `load_ontology()`)
- **Python**: `/Users/sac/ggen-spec-kit/src/specify_cli/runtime/ggen.py` (integration point)
- **Config**: `/Users/sac/ggen-spec-kit/docs/ggen.toml` (validation settings, lines 19-23)
- **Schemas**:
  - `/Users/sac/ggen-spec-kit/ontology/spec-kit-schema.ttl`
  - `/Users/sac/ggen-spec-kit/ontology/spec-kit-docs-extension.ttl`

**Expected Output**:
- In-memory RDF graph (Oxigraph Store)
- Validation report (if SHACL validation enabled)
- Error messages for constraint violations

**How to Verify**:
```bash
# Test with valid TTL
ggen sync --from schema --to src/generated --verbose

# Test with invalid TTL (should fail)
# Create invalid.ttl with syntax error
ggen sync --from invalid-dir --to output
# Expected: Parse error or SHACL violation
```

**Current Limitations**:
- SHACL validation not yet implemented (only Turtle parsing)
- Need to add SHACL constraint checking
- Error reporting needs improvement

**Week 2 Work**:
- [ ] Add SHACL validation using oxigraph/shacl crate
- [ ] Implement detailed constraint violation reporting
- [ ] Add `--strict` flag for fail-fast mode
- [ ] Unit tests for validation edge cases

---

### Stage μ₂: EXTRACT - SPARQL Query Execution

**Purpose**: Execute SPARQL queries to extract structured data from RDF graph

**Status**: ✅ **Partially Working**

**What It Does**:
1. Executes SPARQL SELECT queries against validated RDF graph
2. Materializes query results into structured data
3. Maps RDF terms to template-friendly data structures

**Files Involved**:
- **Rust**: `/Users/sac/ggen-spec-kit/tools/ggen-cli/src/main.rs` (lines 102-170, `extract_classes()`)
- **SPARQL Queries**:
  - `/Users/sac/ggen-spec-kit/sparql/guide-query.rq`
  - `/Users/sac/ggen-spec-kit/sparql/changelog-query.rq`
  - `/Users/sac/ggen-spec-kit/sparql/config-query.rq`
  - `/Users/sac/ggen-spec-kit/sparql/principle-query.rq`
- **Config**: `/Users/sac/ggen-spec-kit/docs/ggen.toml` (transformation specs, lines 29-167)

**Expected Output**:
- Structured data (Vec<OntologyClass> with properties)
- JSON-serializable query results for template rendering

**Example SPARQL Query**:
```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX spec: <http://spec-kit.io/ontology#>

SELECT ?class ?name ?comment ?priority
WHERE {
  ?class a spec:Feature ;
         spec:featureName ?name ;
         spec:description ?comment ;
         spec:priority ?priority .
}
ORDER BY ?priority
```

**How to Verify**:
```bash
# Verbose mode shows extracted classes
ggen sync --from schema --to src/generated --verbose

# Expected output:
# 🔍 Extracting classes from ontology...
#   ✓ Found class: Feature
#   ✓ Found class: Requirement
#   ✓ Found class: Documentation
```

**Current Limitations**:
- Hardcoded class/property extraction queries
- Need configurable SPARQL query files (per transformation)
- No support for CONSTRUCT or ASK queries yet

**Week 2 Work**:
- [ ] Load SPARQL queries from external `.rq` files
- [ ] Support CONSTRUCT queries for graph transformations
- [ ] Add query timeout handling (30s default)
- [ ] Cache query results for performance

---

### Stage μ₃: EMIT - Template Rendering

**Purpose**: Render Tera templates with SPARQL query results to generate markdown

**Status**: ✅ **Working**

**What It Does**:
1. Loads Tera templates from template directory
2. Injects SPARQL results into template context
3. Renders markdown output with template logic (loops, conditionals, filters)

**Files Involved**:
- **Rust**: `/Users/sac/ggen-spec-kit/tools/ggen-cli/src/main.rs` (lines 252-318, `render_templates()`)
- **Templates**:
  - `/Users/sac/ggen-spec-kit/templates/guide.tera`
  - `/Users/sac/ggen-spec-kit/templates/changelog.tera`
  - `/Users/sac/ggen-spec-kit/templates/philosophy.tera`
  - `/Users/sac/ggen-spec-kit/templates/constitution.tera`
  - `/Users/sac/ggen-spec-kit/templates/ggen/*.tera` (code generation templates)
- **Config**: `/Users/sac/ggen-spec-kit/docs/ggen.toml` (template paths, lines 35-46)

**Expected Output**:
- Rendered markdown files (README.md, CHANGELOG.md, etc.)
- Generated code files (Rust structs, Python dataclasses, TypeScript interfaces)

**Example Template** (guide.tera):
```jinja2
# {{ guide.title }}

{{ guide.description }}

## Features

{% for feature in features %}
- **{{ feature.name }}** ({{ feature.priority }})
  {{ feature.description }}
{% endfor %}
```

**How to Verify**:
```bash
# Dry-run mode shows preview without writing files
ggen sync --from schema --to src/generated --dry-run

# Expected: First 20 lines of each rendered template printed
```

**Current Status**:
- ✅ Template loading working
- ✅ Context injection working
- ✅ Auto-escaping disabled for code generation

**Week 3 Work**:
- [ ] Add custom Tera filters (markdown_escape, code_format, etc.)
- [ ] Template inheritance/composition support
- [ ] Better error messages for template syntax errors
- [ ] Template testing framework

---

### Stage μ₄: CANONICALIZE - Output Normalization

**Purpose**: Normalize markdown output for deterministic comparison

**Status**: ❌ **Not Implemented**

**What It Does**:
1. Normalizes line endings (CRLF → LF)
2. Trims trailing whitespace from each line
3. Ensures final newline at end of file
4. Consistent encoding (UTF-8)

**Files Involved**:
- **Rust**: `/Users/sac/ggen-spec-kit/tools/ggen-cli/src/main.rs` (TODO: add `canonicalize()` function)
- **Config**: `/Users/sac/ggen-spec-kit/docs/ggen.toml` (lines 192-198)

**Expected Output**:
- Normalized markdown with consistent formatting
- Same output regardless of input line endings or trailing spaces

**Implementation Plan**:

```rust
/// Canonicalize markdown output for deterministic comparison.
fn canonicalize(content: &str) -> String {
    content
        .lines()                           // Split into lines
        .map(|line| line.trim_end())       // Remove trailing whitespace
        .collect::<Vec<_>>()
        .join("\n")                        // LF line endings
        + "\n"                             // Final newline
}
```

**How to Verify**:
```bash
# Generate markdown twice, compare hashes
ggen sync --from schema --to output1
ggen sync --from schema --to output2
sha256sum output1/README.md output2/README.md
# Expected: Identical hashes
```

**Why This Matters**:
- **Idempotence**: μ∘μ = μ requires byte-identical output
- **Git Diffs**: Clean diffs without whitespace noise
- **Receipts**: SHA256 hashing requires canonical form

**Week 2 Work**:
- [ ] Implement `canonicalize()` function in Rust
- [ ] Add configuration flags for canonicalization rules
- [ ] Test with various line ending inputs (LF, CRLF, CR)
- [ ] Verify idempotence with hash comparison tests

---

### Stage μ₅: RECEIPT - Proof Generation

**Purpose**: Generate SHA256 receipts proving spec.md = μ(feature.ttl)

**Status**: ❌ **Not Implemented**

**What It Does**:
1. Computes SHA256 hash of all input files (TTL, SPARQL, templates)
2. Computes SHA256 hash of canonical output file
3. Generates receipt JSON with input/output hashes
4. Saves receipt file alongside output markdown

**Files Involved**:
- **Rust**: `/Users/sac/ggen-spec-kit/tools/ggen-cli/src/main.rs` (TODO: add `generate_receipt()` function)
- **Config**: `/Users/sac/ggen-spec-kit/docs/ggen.toml` (lines 200-203)
- **Receipts**: `*.receipt.json` files (to be generated)

**Expected Output**: `README.md.receipt.json`

```json
{
  "version": "1.0",
  "timestamp": "2025-01-15T10:30:00Z",
  "transformation": "project-overview",
  "inputs": {
    "rdf": {
      "docs/overview.ttl": "a3f5b1c9e2d8..."
    },
    "sparql": {
      "sparql/guide-query.rq": "7d4e2f1a8b3c..."
    },
    "template": {
      "templates/guide.tera": "9e1f3a5b7c2d..."
    }
  },
  "output": {
    "README.md": "c8b3f2e1a9d7..."
  },
  "constitutional_equation": "spec.md = μ(feature.ttl)",
  "verification": "sha256sum -c README.md.receipt.json"
}
```

**Implementation Plan**:

```rust
use sha2::{Sha256, Digest};
use serde::Serialize;

#[derive(Serialize)]
struct Receipt {
    version: String,
    timestamp: String,
    transformation: String,
    inputs: HashMap<String, HashMap<String, String>>,
    output: HashMap<String, String>,
}

fn generate_receipt(
    input_files: &[PathBuf],
    output_file: &Path,
    transformation_name: &str,
) -> Result<Receipt> {
    // Hash all inputs
    let mut inputs = HashMap::new();

    for input_path in input_files {
        let content = fs::read(input_path)?;
        let hash = Sha256::digest(&content);
        let hash_hex = format!("{:x}", hash);

        let category = categorize_file(input_path); // rdf, sparql, template
        inputs.entry(category).or_insert_with(HashMap::new)
            .insert(input_path.display().to_string(), hash_hex);
    }

    // Hash output
    let output_content = fs::read(output_file)?;
    let output_hash = Sha256::digest(&output_content);
    let output_hash_hex = format!("{:x}", output_hash);

    Ok(Receipt {
        version: "1.0".to_string(),
        timestamp: chrono::Utc::now().to_rfc3339(),
        transformation: transformation_name.to_string(),
        inputs,
        output: [(output_file.display().to_string(), output_hash_hex)]
            .into_iter()
            .collect(),
    })
}
```

**How to Verify**:
```bash
# Generate receipt
ggen sync --from schema --to output

# Verify receipt
ggen verify --receipt output/README.md.receipt.json
# Expected: ✓ All hashes match - spec.md = μ(feature.ttl) verified

# Manually edit README.md, then verify again
echo "<!-- manual edit -->" >> output/README.md
ggen verify --receipt output/README.md.receipt.json
# Expected: ✗ Hash mismatch - manual edits detected
```

**Why This Matters**:
- **Proof of Correctness**: Cryptographic proof that markdown was generated from RDF
- **Detect Manual Edits**: Catch when users edit generated files directly
- **Audit Trail**: Track what inputs produced what outputs
- **CI/CD Validation**: Automated checks that specs are in sync

**Week 2 Work**:
- [ ] Implement SHA256 hashing in Rust
- [ ] Generate receipt JSON structure
- [ ] Save receipts alongside output files
- [ ] Add `ggen verify` command to check receipts

---

## Implementation Timeline

### Week 1: Foundation (✅ COMPLETE)

**Status**: Done
**Delivered**:
- ✅ Local ggen v5.0.0 built from Rust source
- ✅ Basic sync command (`ggen sync --from schema --to output`)
- ✅ RDF loading with Oxigraph
- ✅ SPARQL query execution
- ✅ Tera template rendering
- ✅ Generated code output (Rust, Python, TypeScript)

**Verification**:
```bash
cd /Users/sac/ggen-spec-kit/tools/ggen-cli
cargo build --release
./target/release/ggen --version
# Output: ggen 5.0.0

./target/release/ggen sync --from ../../schema --to ../../src/generated --verbose
# Output: ✅ Compilation complete! Generated code written to: ../../src/generated
```

---

### Week 2: Complete μ₄ and μ₅ Stages

**Goal**: Implement canonicalization and receipt generation in Rust

**Tasks**:

#### μ₄ Canonicalization
- [ ] **Day 1-2**: Implement `canonicalize()` function
  - Normalize line endings (CRLF → LF)
  - Trim trailing whitespace
  - Ensure final newline
  - Test with various inputs

- [ ] **Day 3**: Add configuration options
  - `pipeline.canonicalize.line_ending` (lf, crlf, cr)
  - `pipeline.canonicalize.trim_trailing_whitespace` (bool)
  - `pipeline.canonicalize.ensure_final_newline` (bool)

- [ ] **Day 4**: Write tests
  - Unit tests for canonicalize function
  - Integration tests for idempotence
  - Test with real ggen.toml transformations

#### μ₅ Receipt Generation
- [ ] **Day 5**: Add crypto dependencies
  - Add `sha2 = "0.10"` to Cargo.toml
  - Add `chrono = "0.4"` for timestamps
  - Add `serde_json = "1.0"` for JSON serialization

- [ ] **Day 6-7**: Implement receipt generation
  - Hash all input files (RDF, SPARQL, templates)
  - Hash canonical output files
  - Generate receipt JSON structure
  - Save receipts with `.receipt.json` extension

**Deliverables**:
- ✅ Canonicalization working and tested
- ✅ Receipts generated for all transformations
- ✅ Idempotence verified: μ∘μ = μ
- ✅ All tests passing

**Verification**:
```bash
# Test canonicalization
ggen sync --from schema --to output1
ggen sync --from schema --to output2
diff output1/README.md output2/README.md
# Expected: No differences (byte-identical)

# Test receipts
ls output1/*.receipt.json
# Expected: README.md.receipt.json, rust-struct.receipt.json, etc.

cat output1/README.md.receipt.json | jq
# Expected: Valid JSON with input/output hashes
```

---

### Week 3: Python CLI Commands

**Goal**: Expose ggen functionality through `specify` CLI

**Tasks**:

#### specify sync Command
- [ ] **Day 1**: Create `specify sync` command
  - Wrapper around `ggen sync --config docs/ggen.toml`
  - Support `--watch` flag for file watching
  - Support `--dry-run` for preview
  - Add Rich progress bars and spinners

- [ ] **Day 2**: Add telemetry
  - OTEL spans for sync operations
  - Metrics: duration, files processed, errors
  - Trace SPARQL query execution times

- [ ] **Day 3**: Error handling
  - Friendly error messages for common failures
  - Suggestions for fixing SHACL violations
  - Validation error summaries

#### specify validate-rdf Command
- [ ] **Day 4**: Create `specify validate-rdf` command
  - Run μ₁ normalization only (no code gen)
  - Report SHACL constraint violations
  - Exit code 0 for valid, 1 for invalid

#### specify verify Command
- [ ] **Day 5**: Create `specify verify` command
  - Check receipts against current files
  - Detect manual edits to generated files
  - Report which files need regeneration

#### specify watch Command
- [ ] **Day 6-7**: Create `specify watch` command
  - Watch TTL files for changes
  - Auto-run sync on file modifications
  - Debounce rapid changes (500ms)
  - Live reload feedback with Rich

**Deliverables**:
- ✅ `specify sync` - Full pipeline execution
- ✅ `specify validate-rdf` - RDF validation only
- ✅ `specify verify` - Receipt verification
- ✅ `specify watch` - File watching
- ✅ All commands with OTEL instrumentation
- ✅ Comprehensive error handling

**Files**:
- `/Users/sac/ggen-spec-kit/src/specify_cli/commands/sync.py`
- `/Users/sac/ggen-spec-kit/src/specify_cli/commands/validate_rdf.py`
- `/Users/sac/ggen-spec-kit/src/specify_cli/commands/verify.py`
- `/Users/sac/ggen-spec-kit/src/specify_cli/commands/watch.py`
- `/Users/sac/ggen-spec-kit/src/specify_cli/ops/ggen.py` (business logic)

**Verification**:
```bash
# Test sync command
specify sync --verbose
# Expected: All transformations executed, receipts generated

# Test validation
specify validate-rdf ontology/spec-kit-schema.ttl
# Expected: ✓ RDF valid - 3 classes, 12 properties

# Test verification
echo "<!-- edit -->" >> README.md
specify verify
# Expected: ✗ README.md modified - regenerate with: specify sync

# Test watch
specify watch &
# Edit memory/philosophy.ttl
# Expected: Auto-regenerates spec-driven.md
```

---

### Week 4: Testing, Documentation, and Release

**Goal**: Production-ready v1.0 release with full μ₁-μ₅ pipeline

**Tasks**:

#### Testing
- [ ] **Day 1-2**: Unit tests
  - Test each μ stage independently
  - Test canonicalization edge cases
  - Test receipt generation/verification
  - Test error handling paths

- [ ] **Day 3**: Integration tests
  - End-to-end pipeline tests
  - Test all 14 transformations in ggen.toml
  - Idempotence tests (μ∘μ = μ)
  - Receipt verification tests

- [ ] **Day 4**: Testcontainer tests
  - Update `/Users/sac/ggen-spec-kit/tests/integration/test_ggen_sync.py`
  - Test with real Docker container
  - Test cross-platform (Linux, macOS)

#### Documentation
- [ ] **Day 5**: Update docs
  - Complete `docs/GGEN_RDF_README.md`
  - Add examples to `/Users/sac/ggen-spec-kit/docs/ggen-examples/`
  - Update `README.md` with ggen workflow
  - Add architecture diagrams for μ₁-μ₅

- [ ] **Day 6**: API documentation
  - Rustdoc for ggen-cli
  - Python docstrings for specify commands
  - SPARQL query documentation
  - Template usage guide

#### Release
- [ ] **Day 7**: v1.0 release
  - Tag ggen v5.0.0 fork
  - Publish to crates.io (optional)
  - Update CHANGELOG.md
  - Create GitHub release with binaries

**Deliverables**:
- ✅ 80%+ test coverage
- ✅ All tests passing
- ✅ Complete documentation
- ✅ v1.0 release tagged
- ✅ Constitutional equation fully implemented

**Verification**:
```bash
# Run full test suite
uv run pytest tests/ -v --cov=src/specify_cli

# Expected: 80%+ coverage, all tests pass

# Verify constitutional equation
specify sync
specify verify
# Expected: ✓ All receipts valid - spec.md = μ(feature.ttl)

# Check determinism
for i in {1..10}; do
  specify sync
done
sha256sum README.md
# Expected: Same hash every time (idempotence verified)
```

---

## CLI Commands Reference

### specify sync

**Purpose**: Run full μ₁-μ₅ pipeline to generate markdown from RDF

**Usage**:
```bash
specify sync [OPTIONS]
```

**Options**:
- `--config PATH` - Path to ggen.toml (default: docs/ggen.toml)
- `--watch` - Watch files and auto-sync on changes
- `--dry-run` - Preview changes without writing files
- `--verbose` - Show detailed progress
- `--output DIR` - Override output directory
- `--transformation NAME` - Run specific transformation only

**Examples**:
```bash
# Run all transformations
specify sync

# Watch mode for development
specify sync --watch --verbose

# Preview without writing
specify sync --dry-run

# Run specific transformation
specify sync --transformation changelog
```

**What It Does**:
1. μ₁ Load and validate RDF files
2. μ₂ Execute SPARQL queries
3. μ₃ Render Tera templates
4. μ₄ Canonicalize output
5. μ₅ Generate receipts

**Output**:
```
🚀 ggen sync - Constitutional Equation Pipeline
   Config: docs/ggen.toml
   Transformations: 14

[1/14] project-overview ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100%
  μ₁ Normalize ✓
  μ₂ Extract ✓
  μ₃ Emit ✓
  μ₄ Canonicalize ✓
  μ₅ Receipt ✓
  → README.md (12.5 KB)

[2/14] changelog ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100%
  μ₁ Normalize ✓
  μ₂ Extract ✓
  μ₃ Emit ✓
  μ₄ Canonicalize ✓
  μ₅ Receipt ✓
  → CHANGELOG.md (8.2 KB)

...

✅ Sync complete! 14 transformations, 14 receipts generated
   Duration: 2.3s
   Constitutional equation verified: spec.md = μ(feature.ttl)
```

---

### specify validate-rdf

**Purpose**: Run μ₁ normalization only - validate RDF without generating code

**Usage**:
```bash
specify validate-rdf [FILES...] [OPTIONS]
```

**Options**:
- `--strict` - Fail on warnings (default: errors only)
- `--shapes PATH` - Path to SHACL shapes file
- `--format FORMAT` - Input format (ttl, rdf, owl)

**Examples**:
```bash
# Validate single file
specify validate-rdf ontology/spec-kit-schema.ttl

# Validate multiple files
specify validate-rdf memory/*.ttl

# Strict mode (fail on warnings)
specify validate-rdf --strict ontology/spec-kit-schema.ttl
```

**Output**:
```
🔍 Validating RDF files...

✓ ontology/spec-kit-schema.ttl
  - 8 classes
  - 24 properties
  - 0 SHACL violations

✓ memory/philosophy.ttl
  - 12 principles
  - 0 SHACL violations

✅ All RDF files valid
```

**Exit Codes**:
- `0` - All files valid
- `1` - Validation errors found
- `2` - Parse errors

---

### specify verify

**Purpose**: Verify receipts and detect manual edits

**Usage**:
```bash
specify verify [OPTIONS]
```

**Options**:
- `--receipt PATH` - Verify specific receipt file
- `--fix` - Regenerate files with hash mismatches
- `--all` - Check all receipt files in project

**Examples**:
```bash
# Verify all receipts
specify verify

# Verify specific receipt
specify verify --receipt README.md.receipt.json

# Auto-fix mismatches
specify verify --fix
```

**Output**:
```
🔐 Verifying receipts...

✓ README.md
  Receipt: README.md.receipt.json
  Input hash: a3f5b1c9e2d8... ✓
  Output hash: c8b3f2e1a9d7... ✓

✗ CHANGELOG.md
  Receipt: CHANGELOG.md.receipt.json
  Input hash: 7d4e2f1a8b3c... ✓
  Output hash: 9e1f3a5b7c2d... ✗ MISMATCH

  Manual edits detected. Regenerate with:
    specify sync --transformation changelog

2 receipts checked, 1 valid, 1 invalid
```

**Exit Codes**:
- `0` - All receipts valid
- `1` - Hash mismatches detected

---

### specify watch

**Purpose**: Watch RDF files and auto-sync on changes

**Usage**:
```bash
specify watch [OPTIONS]
```

**Options**:
- `--debounce MS` - Debounce delay (default: 500ms)
- `--paths GLOB` - Watch specific paths (default: memory/*.ttl, ontology/*.ttl)

**Examples**:
```bash
# Watch all RDF files
specify watch

# Custom debounce
specify watch --debounce 1000

# Watch specific directory
specify watch --paths "memory/*.ttl"
```

**Output**:
```
👀 Watching RDF files for changes...
   Paths: memory/*.ttl, ontology/*.ttl, sparql/*.rq
   Debounce: 500ms

   Press Ctrl+C to stop

[14:32:15] memory/philosophy.ttl changed
           Running sync...
           ✓ spec-driven.md regenerated (2.1s)

[14:35:42] ontology/spec-kit-schema.ttl changed
           Running sync...
           ✓ README.md regenerated (1.8s)
           ✓ 6 other files regenerated
```

---

## Testing Strategy

### Unit Tests

**Location**: `/Users/sac/ggen-spec-kit/tests/unit/`

**Coverage**:
- μ₁ Normalization
  - [ ] Valid TTL parsing
  - [ ] Invalid TTL error handling
  - [ ] SHACL constraint validation
  - [ ] Multiple input files

- μ₂ Extraction
  - [ ] SPARQL SELECT queries
  - [ ] SPARQL CONSTRUCT queries
  - [ ] Empty result handling
  - [ ] Query timeout handling

- μ₃ Emission
  - [ ] Template rendering
  - [ ] Context injection
  - [ ] Custom filters
  - [ ] Template errors

- μ₄ Canonicalization
  - [ ] Line ending normalization (CRLF → LF)
  - [ ] Trailing whitespace removal
  - [ ] Final newline enforcement
  - [ ] UTF-8 encoding

- μ₅ Receipt
  - [ ] SHA256 hashing
  - [ ] Receipt JSON generation
  - [ ] Multi-file receipts
  - [ ] Verification logic

**Example Test**:
```python
def test_canonicalize_line_endings():
    """Test that CRLF is converted to LF."""
    input_text = "Line 1\r\nLine 2\r\nLine 3\r\n"
    expected = "Line 1\nLine 2\nLine 3\n"

    result = canonicalize(input_text)

    assert result == expected
    assert "\r\n" not in result
```

---

### Integration Tests

**Location**: `/Users/sac/ggen-spec-kit/tests/integration/`

**Coverage**:
- [ ] Full μ₁-μ₅ pipeline execution
- [ ] All 14 transformations in ggen.toml
- [ ] Idempotence verification (μ∘μ = μ)
- [ ] Receipt verification after sync
- [ ] Watch mode file triggers
- [ ] Error recovery and rollback

**Example Test**:
```python
def test_constitutional_equation():
    """Verify spec.md = μ(feature.ttl)."""
    # Run sync first time
    run(["specify", "sync"])
    hash1 = sha256("README.md")

    # Run sync second time
    run(["specify", "sync"])
    hash2 = sha256("README.md")

    # Verify idempotence: μ∘μ = μ
    assert hash1 == hash2

    # Verify receipt
    result = run(["specify", "verify"])
    assert result.exit_code == 0
```

---

### Idempotence Tests

**Purpose**: Verify μ∘μ = μ (same input produces same output)

**Test Cases**:
- [ ] Run sync 10 times, check all outputs identical
- [ ] Run sync on different platforms (Linux, macOS), compare hashes
- [ ] Run sync with different ggen versions, check backward compatibility
- [ ] Modify TTL slightly, verify output changes
- [ ] Revert TTL change, verify output returns to original

**Example Test**:
```python
def test_idempotence_ten_runs():
    """Run sync 10 times and verify identical output."""
    hashes = []

    for i in range(10):
        run(["specify", "sync"])
        hash_value = sha256("README.md")
        hashes.append(hash_value)

    # All hashes should be identical
    assert len(set(hashes)) == 1, "Non-deterministic output detected"
```

---

### Compliance Tests

**Purpose**: Verify SHACL constraints are enforced

**Test Cases**:
- [ ] Missing required property → validation error
- [ ] Invalid datatype → validation error
- [ ] Out-of-range value → validation error
- [ ] Valid data → validation success

**Example Test**:
```python
def test_shacl_required_property():
    """Test that missing required property fails validation."""
    invalid_ttl = """
    @prefix spec: <http://spec-kit.io/ontology#> .

    :Feature001 a spec:Feature ;
        # Missing required spec:featureName property
        spec:priority "P1" .
    """

    write("invalid.ttl", invalid_ttl)
    result = run(["specify", "validate-rdf", "invalid.ttl"])

    assert result.exit_code == 1
    assert "Required property spec:featureName missing" in result.stderr
```

---

### Receipt Tests

**Purpose**: Verify SHA256 receipts detect changes

**Test Cases**:
- [ ] Generate receipt → verify → pass
- [ ] Manually edit output → verify → fail
- [ ] Change input TTL → verify → fail (input hash mismatch)
- [ ] Regenerate → verify → pass

**Example Test**:
```python
def test_receipt_detects_manual_edit():
    """Test that manual edits are detected by receipt verification."""
    # Generate with receipt
    run(["specify", "sync"])

    # Verify receipt (should pass)
    result = run(["specify", "verify"])
    assert result.exit_code == 0

    # Manually edit output
    with open("README.md", "a") as f:
        f.write("\n<!-- Manual edit -->")

    # Verify receipt (should fail)
    result = run(["specify", "verify"])
    assert result.exit_code == 1
    assert "Hash mismatch" in result.stderr
```

---

## Example Files

### Example 1: Feature Specification

**File**: `/Users/sac/ggen-spec-kit/docs/ggen-examples/feature.ttl`

```turtle
@prefix : <http://spec-kit.io/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

:Feature001 a :Feature ;
    :featureName "Constitutional Equation Implementation" ;
    :description "Implement μ₁-μ₅ pipeline for deterministic RDF-to-Markdown transformation" ;
    :priority "P0" ;
    :status "in-progress" ;
    :assignedTo :Team_Core ;
    :dueDate "2025-01-31"^^xsd:date ;
    :hasRequirement :Req001, :Req002, :Req003 .

:Req001 a :Requirement ;
    :requirementText "System MUST validate RDF against SHACL shapes before processing" ;
    :priority "P0" ;
    :category "validation" .

:Req002 a :Requirement ;
    :requirementText "System MUST generate SHA256 receipts for all transformations" ;
    :priority "P0" ;
    :category "verification" .

:Req003 a :Requirement ;
    :requirementText "System MUST ensure idempotence: μ∘μ = μ" ;
    :priority "P0" ;
    :category "correctness" .
```

---

### Example 2: SPARQL Query

**File**: `/Users/sac/ggen-spec-kit/docs/ggen-examples/feature-query.rq`

```sparql
PREFIX : <http://spec-kit.io/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?feature ?name ?description ?priority ?status ?dueDate
       (GROUP_CONCAT(?reqText; separator="\n") AS ?requirements)
WHERE {
  # Get feature details
  ?feature a :Feature ;
           :featureName ?name ;
           :description ?description ;
           :priority ?priority ;
           :status ?status ;
           :dueDate ?dueDate .

  # Get associated requirements
  OPTIONAL {
    ?feature :hasRequirement ?req .
    ?req :requirementText ?reqText .
  }
}
GROUP BY ?feature ?name ?description ?priority ?status ?dueDate
ORDER BY ?priority ?dueDate
```

---

### Example 3: Tera Template

**File**: `/Users/sac/ggen-spec-kit/docs/ggen-examples/feature.tera`

```jinja2
# Feature Specification

{% for feature in features %}
## {{ feature.name }}

**Priority**: {{ feature.priority }}
**Status**: {{ feature.status }}
**Due Date**: {{ feature.dueDate | date(format="%Y-%m-%d") }}

### Description

{{ feature.description }}

### Requirements

{% for req in feature.requirements | split(pat="\n") %}
- {{ req }}
{% endfor %}

---

{% endfor %}

## Constitutional Verification

This document was generated via:

```
spec.md = μ(feature.ttl)
```

Where μ is the five-stage transformation:
- μ₁ NORMALIZE: Validate RDF against SHACL shapes
- μ₂ EXTRACT: Execute SPARQL queries
- μ₃ EMIT: Render Tera templates
- μ₄ CANONICALIZE: Normalize markdown output
- μ₅ RECEIPT: Generate SHA256 proof

**Verification**: Run `specify verify` to check receipt integrity.
```

---

### Example 4: Receipt File

**File**: `/Users/sac/ggen-spec-kit/docs/ggen-examples/README.md.receipt.json`

```json
{
  "version": "1.0",
  "timestamp": "2025-01-15T10:30:00Z",
  "transformation": "project-overview",
  "inputs": {
    "rdf": {
      "docs/overview.ttl": "a3f5b1c9e2d8f7a6c1e4b9d3f2a8c5e7d1b6f4a9c2e8d5b3f7a1c6e4b9d2"
    },
    "sparql": {
      "sparql/guide-query.rq": "7d4e2f1a8b3c6e9d5f2a7c4e1b8d6f3a9c2e5d8b1f4a7c3e6d9b2f5a8c1"
    },
    "template": {
      "templates/guide.tera": "9e1f3a5b7c2d8e4f6a9c1e3d5b7f2a4c6e8d1b3f5a7c9e2d4b6f8a1c3e5"
    }
  },
  "output": {
    "README.md": "c8b3f2e1a9d7c5e4b1f8a6d3c2e9b5f1a7d4c6e2b8f3a1d5c7e9b4f2a6d8"
  },
  "constitutional_equation": "spec.md = μ(feature.ttl)",
  "verification": {
    "command": "specify verify --receipt README.md.receipt.json",
    "expected_exit_code": 0,
    "idempotence": "μ∘μ = μ"
  },
  "pipeline_stages": {
    "μ1_normalize": {
      "status": "success",
      "validation_errors": 0,
      "classes_loaded": 8,
      "properties_loaded": 24
    },
    "μ2_extract": {
      "status": "success",
      "sparql_queries": 1,
      "results_count": 12,
      "duration_ms": 45
    },
    "μ3_emit": {
      "status": "success",
      "template": "templates/guide.tera",
      "output_size_bytes": 12854,
      "duration_ms": 23
    },
    "μ4_canonicalize": {
      "status": "success",
      "line_ending": "lf",
      "trailing_whitespace_removed": true,
      "final_newline_added": true
    },
    "μ5_receipt": {
      "status": "success",
      "hash_algorithm": "sha256",
      "receipt_file": "README.md.receipt.json"
    }
  }
}
```

---

### Example 5: ggen.toml Configuration

**File**: `/Users/sac/ggen-spec-kit/docs/ggen-examples/ggen.toml`

```toml
[metadata]
name = "feature-spec"
description = "Feature specification transformation"
version = "1.0"

[validation]
shacl_shapes = ["ontology/spec-kit-schema.ttl"]
fail_on_warning = true

[[transformations.specs]]
name = "feature-spec"
description = "Generate feature specification from RDF"
input_files = ["docs/ggen-examples/feature.ttl"]
schema_files = ["ontology/spec-kit-schema.ttl"]
sparql_query = "docs/ggen-examples/feature-query.rq"
template = "docs/ggen-examples/feature.tera"
output_file = "docs/ggen-examples/FEATURE_SPEC.md"
deterministic = true

[pipeline]
stages = ["normalize", "extract", "emit", "canonicalize", "receipt"]

[pipeline.normalize]
enabled = true
fail_on_validation_error = true

[pipeline.extract]
enabled = true
timeout_seconds = 30

[pipeline.emit]
enabled = true
template_engine = "tera"

[pipeline.canonicalize]
enabled = true
line_ending = "lf"
trim_trailing_whitespace = true
ensure_final_newline = true

[pipeline.receipt]
enabled = true
hash_algorithm = "sha256"
write_manifest = true
```

---

## Success Criteria

### Technical Success

- [ ] **μ₁ Normalization**: RDF loads, SHACL validates, errors reported
- [ ] **μ₂ Extraction**: SPARQL queries execute, results materialize
- [ ] **μ₃ Emission**: Templates render correctly, output matches expected
- [ ] **μ₄ Canonicalization**: Line endings normalized, whitespace trimmed
- [ ] **μ₅ Receipt**: SHA256 hashes generated, verification works

### Functional Success

- [ ] **Idempotence**: Running sync 10 times produces identical output
- [ ] **Verification**: Receipts detect manual edits to generated files
- [ ] **Error Handling**: Graceful failures with helpful error messages
- [ ] **Performance**: Full sync completes in < 5 seconds
- [ ] **Watch Mode**: File changes trigger auto-sync within 1 second

### Quality Success

- [ ] **Test Coverage**: 80%+ code coverage
- [ ] **All Tests Passing**: 0 failures, 0 flakes
- [ ] **Documentation**: Complete with examples
- [ ] **Type Safety**: 100% type hints in Python, no `unsafe` in Rust
- [ ] **Security**: No hardcoded secrets, path validation enforced

---

## Risk Mitigation

### Risk 1: SHACL Validation Not Available in Oxigraph

**Likelihood**: Medium
**Impact**: High

**Mitigation**:
- Use `oxrdflib` with `pyshacl` for Python-based validation
- Or use `sophia` Rust crate with SHACL support
- Worst case: Manual validation in separate step

**Contingency**: Week 2 Day 2 reserved for SHACL implementation research

---

### Risk 2: Performance Degradation with Large RDF Files

**Likelihood**: Low
**Impact**: Medium

**Mitigation**:
- Use streaming RDF parser instead of loading all into memory
- Cache SPARQL query results
- Parallelize transformations with Rayon

**Contingency**: Week 4 Day 1-2 for performance optimization if needed

---

### Risk 3: Cross-Platform Canonicalization Issues

**Likelihood**: Low
**Impact**: Medium

**Mitigation**:
- Test on Linux, macOS, Windows
- Use Rust's `std::io::BufRead` for platform-agnostic line reading
- Document line ending behavior in receipts

**Contingency**: Week 4 Day 3 for cross-platform testing

---

## Next Steps

### Immediate (Week 2 Start)

1. **Create μ₄ implementation PR**
   - Branch: `feat/canonicalization`
   - Add `canonicalize()` function to `tools/ggen-cli/src/main.rs`
   - Write unit tests
   - Update ggen.toml with canonicalization config

2. **Research SHACL validation options**
   - Evaluate `oxigraph` SHACL support
   - Evaluate `sophia` crate
   - Prototype with test data

3. **Design receipt JSON schema**
   - Document receipt format
   - Create example receipts
   - Plan verification algorithm

### Short-Term (Week 2-3)

1. Complete μ₄ and μ₅ in Rust
2. Implement Python CLI commands
3. Write integration tests
4. Update documentation

### Long-Term (Week 4+)

1. Release v1.0
2. Monitor production usage
3. Optimize performance
4. Add advanced features (CONSTRUCT queries, custom filters)

---

## Conclusion

This roadmap provides a clear path from **Week 1's foundation** to **Week 4's v1.0 release** with a fully functional constitutional equation:

```
spec.md = μ(feature.ttl)
```

By implementing all five stages (μ₁-μ₅), spec-kit will achieve:
- **Deterministic**: Same input always produces same output
- **Verifiable**: SHA256 receipts prove correctness
- **Automated**: RDF is source of truth, markdown is generated
- **Testable**: Idempotence and compliance tests guarantee quality

**The constitutional equation is the foundation of RDF-first development.**

This implementation makes it real.
