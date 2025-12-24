# Interpret and Verify ggen Receipts

Learn how to read and verify SHA256 receipts that prove your code matches your RDF specifications.

## What is a Receipt?

A **receipt** is a cryptographic proof that your generated code comes from a specific RDF specification. It contains:

- **SHA256 hash** of your RDF source
- **SHA256 hashes** of every generated file
- **Timestamp** of generation
- **ggen version** used
- **Metadata** about the transformation

**Location:** `.ggen/receipt.json`

## Reading a Receipt

### View Receipt

```bash
cat .ggen/receipt.json | jq
```

**Example output:**

```json
{
  "ggen_version": "5.0.2",
  "timestamp": "2025-12-23T14:30:00.000Z",
  "rdf_source": {
    "file": "ontology/cli-commands.ttl",
    "hash": "sha256:abc123def456789..."
  },
  "generated_files": {
    "src/commands/check.py": {
      "hash": "sha256:xyz789abc123...",
      "size_bytes": 325,
      "type": "code"
    },
    "src/commands/init.py": {
      "hash": "sha256:def456xyz789...",
      "size_bytes": 412,
      "type": "code"
    },
    "tests/e2e/test_commands.py": {
      "hash": "sha256:ghi789def456...",
      "size_bytes": 623,
      "type": "test"
    }
  },
  "statistics": {
    "total_files_generated": 15,
    "total_size_bytes": 87234,
    "code_files": 8,
    "test_files": 5,
    "doc_files": 2
  },
  "verification": {
    "idempotent": true,
    "all_files_present": true,
    "all_hashes_match": true,
    "status": "VALID"
  }
}
```

### Parse Specific Fields

```bash
# Get generation timestamp
jq '.timestamp' .ggen/receipt.json

# Get ggen version
jq '.ggen_version' .ggen/receipt.json

# Get RDF source hash
jq '.rdf_source.hash' .ggen/receipt.json

# Get all file hashes
jq '.generated_files | keys[]' .ggen/receipt.json

# Get verification status
jq '.verification' .ggen/receipt.json
```

## Verify Code Matches Specification

### Verify All Files

```bash
specify generated verify

✓ src/commands/check.py ✓ (sha256:abc123...)
✓ src/commands/init.py ✓ (sha256:def456...)
✓ tests/e2e/test_commands.py ✓ (sha256:ghi789...)
... (12 more files)

Overall: 15 of 15 files match specification
Status: CURRENT (matches specification)
```

### Verify Single File

```bash
# Check one file against receipt
specify generated verify src/commands/check.py

✓ src/commands/check.py matches specification
```

### Detect Manual Edits

```bash
specify generated verify

✓ src/commands/check.py ✓
✗ src/commands/cache.py ✗ MANUALLY EDITED
  Receipt hash: sha256:def456...
  Current hash: sha256:modified...
  Recommendation: Run 'ggen sync' to regenerate
```

**Warning:** Manual edits to generated files will break spec-code sync.

## What the Hashes Prove

### Proof of Origin

Receipt proves: "This code came from this specific RDF specification"

```
Receipt shows: RDF hash = abc123...
Your RDF file: md5sum ontology/cli-commands.ttl
  Result: abc123...
          ↑ Matches!

Conclusion: Code was generated from your RDF
```

### Proof of Integrity

Receipt proves: "Generated code hasn't been modified"

```
Receipt shows: src/commands/check.py = sha256:xyz789...
Current file: sha256sum src/commands/check.py
  Result: xyz789...
          ↑ Matches!

Conclusion: File hasn't been modified (byte-for-byte identical)
```

### Proof of Reproducibility

Receipt proves: "You can regenerate identical code"

```bash
# Delete generated files
rm src/commands/*.py

# Regenerate
ggen sync

# Check hashes
sha256sum src/commands/check.py
# xyz789...
# ↑ Same hash as receipt!

Conclusion: Generation is reproducible and deterministic
```

## Understanding Receipt Status

### VALID

```json
"verification": {
  "status": "VALID",
  "all_files_present": true,
  "all_hashes_match": true,
  "idempotent": true
}
```

**Meaning:** Everything matches. Code is in sync with spec.

**Action:** No action needed. Safe to proceed.

### MISMATCH

```json
"verification": {
  "status": "MISMATCH",
  "all_files_present": true,
  "all_hashes_match": false,
  "mismatches": [
    "src/commands/check.py"
  ]
}
```

**Meaning:** One or more files have been modified.

**Causes:**
1. Manual edits to generated file
2. Someone ran ggen sync and changes weren't committed
3. RDF was updated but code wasn't regenerated

**Action:**
```bash
# To restore from RDF:
ggen sync

# Or manually:
git checkout src/commands/check.py
```

### MISSING

```json
"verification": {
  "status": "MISSING",
  "all_files_present": false,
  "missing_files": [
    "src/commands/cache.py",
    "tests/e2e/test_commands_cache.py"
  ]
}
```

**Meaning:** Some generated files are gone.

**Causes:**
1. Someone deleted generated files
2. Files weren't committed to git
3. Incomplete checkout/clone

**Action:**
```bash
# Regenerate missing files
ggen sync

# Commit them
git add .
git commit
```

## Compare Receipts

### Compare Two Generations

```bash
# Save current receipt
cp .ggen/receipt.json receipt-before.json

# Make changes
vim ontology/cli-commands.ttl

# Regenerate
ggen sync

# Compare receipts
diff receipt-before.json .ggen/receipt.json
```

**Example output:**

```diff
< "timestamp": "2025-12-23T14:30:00.000Z",
> "timestamp": "2025-12-23T15:45:00.000Z",

< "ontology/cli-commands.ttl":
<   "hash": "sha256:abc123..."
> "ontology/cli-commands.ttl":
>   "hash": "sha256:new456..."

< "src/commands/ggen.py":
<   "hash": "sha256:old789..."
> "src/commands/ggen.py":
>   "hash": "sha256:new789..."
```

**Interpretation:**
- Timestamp changed → Generation happened
- RDF hash changed → Specification was updated
- File hashes changed → Code was regenerated

### Track Receipt History

```bash
# Keep receipt history
mkdir -p .ggen/history

# Save each receipt with date
cp .ggen/receipt.json ".ggen/history/receipt-$(date +%Y-%m-%d-%H-%M-%S).json"

# View history
ls -lt .ggen/history/

# Compare two points in time
diff ".ggen/history/receipt-2025-12-20-10-00-00.json" \
     ".ggen/history/receipt-2025-12-23-15-45-00.json"
```

## Idempotence Verification

### What Idempotence Means

**Idempotent operation:** Running twice gives same result as running once.

```
μ(μ(x)) = μ(x)
```

### Verify Idempotence

```bash
# Generate once
ggen sync

# Save receipt
cp .ggen/receipt.json receipt-1.json

# Generate again (without changing anything)
ggen sync

# Save receipt
cp .ggen/receipt.json receipt-2.json

# Compare
diff receipt-1.json receipt-2.json

# Should be identical (except timestamp)
```

**Expected:**
```
Only difference: timestamp field
Everything else identical
```

**If different:**
- ⚠️ Generation is NOT idempotent
- ⚠️ Bug in ggen or RDF
- ⚠️ Should never happen for valid specs

### Why Idempotence Matters

**Benefits:**
1. **Predictable** - Know what you'll get
2. **Safe** - Can regenerate anytime
3. **Verifiable** - Can prove it matches spec
4. **Debuggable** - Can compare runs to find issues

## Using Receipts in CI/CD

### GitHub Actions Example

```yaml
name: Verify Specification Sync

on: [push, pull_request]

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Regenerate code
        run: ggen sync

      - name: Verify no changes
        run: |
          git diff --exit-code \
            || (echo "Code out of sync with spec!" && exit 1)

      - name: Check receipt
        run: specify generated verify
```

### Automated Receipt Validation

```bash
#!/bin/bash
# scripts/validate-receipt.sh

# 1. Check receipt exists
if [ ! -f ".ggen/receipt.json" ]; then
  echo "ERROR: No receipt found"
  exit 1
fi

# 2. Check all files present
while read -r file; do
  if [ ! -f "$file" ]; then
    echo "ERROR: Missing file: $file"
    exit 1
  fi
done < <(jq -r '.generated_files | keys[]' .ggen/receipt.json)

# 3. Verify all hashes
for file in $(jq -r '.generated_files | keys[]' .ggen/receipt.json); do
  expected=$(jq -r ".generated_files.\"$file\".hash" .ggen/receipt.json | sed 's/sha256://')
  actual=$(sha256sum "$file" | awk '{print $1}')

  if [ "$expected" != "$actual" ]; then
    echo "ERROR: Hash mismatch for $file"
    exit 1
  fi
done

echo "✓ All files verified against receipt"
```

## Troubleshooting

### Receipt Not Found

```bash
$ .ggen/receipt.json: No such file or directory

# Fix: Run ggen sync to generate receipt
ggen sync
```

### Hash Mismatch

```bash
$ Receipt hash: sha256:abc123...
$ File hash:    sha256:xyz789...

# Causes:
# 1. File was manually edited
# 2. Different ggen version used
# 3. RDF was updated without regenerating

# Fix: Regenerate
ggen sync
```

### Idempotence Failed

```bash
$ Run 1: Receipt hash = abc123...
$ Run 2: Receipt hash = xyz789...

# Problem: Generation is not deterministic!

# Investigation:
# - Check if RDF changed between runs
# - Check if random data is being used
# - Check for timestamp-dependent generation
# - Report as bug: generation should be deterministic
```

## See Also

- [ggen.md](../../commands/ggen.md) - ggen command reference
- `/docs/explanation/constitutional-equation.md` - Receipt theory
- `/docs/guides/operations/run-ggen-sync.md` - Running ggen sync
- `/docs/reference/definition-of-done.md` - Code quality standards
