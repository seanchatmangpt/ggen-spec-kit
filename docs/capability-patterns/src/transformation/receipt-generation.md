# 26. Receipt Generation

★★

*Trust, but verify. Receipt generation (μ₅) creates cryptographic proof that artifacts were correctly generated from their source specifications. Receipts transform assertions into evidence.*

---

## The Proof

You've transformed specifications through the complete μ pipeline—normalization, extraction, emission, canonicalization. The artifact now exists. But how do you know it was generated correctly? How can you prove it to others? How can you detect if someone modified it afterward?

Receipts provide the answer. They are cryptographic proofs that record:

- **What source** was transformed (file, hash, version)
- **What stages** it passed through (with their configurations)
- **What output** was produced (file, hash)
- **When** transformation occurred
- **How** to verify correctness

With receipts, verification becomes mechanical. You don't trust—you verify. You don't assert—you prove.

---

## The Verification Problem

**The fundamental challenge: Without proof, claims of correct transformation are merely assertions. "This was generated correctly" is not verifiable. Receipts make verification automatic, repeatable, and trustworthy.**

Let us examine why this matters:

### The Trust Gap

Developer A claims: "I regenerated the file. It's correct."
Developer B asks: "How do I know?"

Without receipts, Developer B must:
1. Re-run the transformation themselves
2. Compare output byte-by-byte
3. Trust that Developer A's environment matches theirs
4. Hope nothing changed between claim and verification

This is tedious, error-prone, and doesn't scale.

### The Tampering Question

An artifact exists in the repository. Did it come from the specification, or did someone edit it directly? Without receipts, you cannot tell:

```python
# Was this generated or hand-edited?
def validate(file: Path, extra_param: str = "maybe added manually?"):
    ...
```

With receipts, the answer is immediate: if the artifact's hash doesn't match the receipt's expected hash, it was modified.

### The Audit Requirement

Compliance audits ask: "Can you prove your documentation matches your implementation?"

Without receipts: "Trust us, we run `ggen sync` regularly."
With receipts: "Here's cryptographic proof. Verify it yourself."

### The Regression Detection

Someone accidentally commits a stale generated file. Without receipts, you might not notice until runtime. With receipts, CI catches it immediately:

```
Receipt verification failed!
Expected: sha256:abc123...
Actual:   sha256:def456...
The file was modified outside of generation.
```

---

## The Forces

Several tensions shape receipt design:

### Force: Completeness vs. Size

*Complete receipts record everything. But complete receipts are large.*

A receipt could include:
- Full source content
- Full template content
- Full output content
- Intermediate stage outputs
- Environment variables
- Tool versions

But this makes receipts larger than the artifacts themselves.

**Resolution:** Record hashes and references, not content. Keep content in source control; receipts reference it.

### Force: Verification Speed vs. Thoroughness

*Thorough verification re-runs the entire pipeline. But that's slow.*

Quick verification: Check if artifact hash matches receipt
Thorough verification: Re-run transformation, compare output

**Resolution:** Quick verification by default. Thorough verification for audits or when quick fails.

### Force: Storage Overhead

*Every artifact gets a receipt. Storage doubles.*

```
src/commands/validate.py          # 3 KB
src/commands/validate.py.receipt  # 1 KB (33% overhead)
```

**Resolution:** Accept reasonable overhead. Receipts are small compared to artifacts. Consider centralized receipt storage for extreme cases.

### Force: Receipt Staleness

*Receipts capture a moment in time. The world moves on.*

The receipt says the artifact was correct when generated. But the source might have changed since then. Is the receipt still meaningful?

**Resolution:** Receipts record source hashes. Verification checks if source has changed. Stale receipts trigger regeneration.

---

## Therefore

**Implement receipt generation (μ₅) as the final transformation stage, producing a cryptographic proof for each artifact that enables verification of correct generation.**

The receipt generation pipeline:

```
┌────────────────────────────────────────────────────────────────────┐
│  μ₅ RECEIPT                                                         │
│                                                                     │
│  1. COLLECT stage hashes                                            │
│     ├── Source file hash (from μ₁)                                 │
│     ├── Shape file hash (from μ₁)                                  │
│     ├── Query file hash (from μ₂)                                  │
│     ├── Template file hash (from μ₃)                               │
│     ├── Config hash (from μ₄)                                      │
│     └── Output hash (from μ₄)                                      │
│                                                                     │
│  2. BUILD receipt structure                                         │
│     ├── Add metadata (timestamp, generator, version)               │
│     ├── Add input references                                       │
│     ├── Add stage chain                                            │
│     └── Add output references                                      │
│                                                                     │
│  3. COMPUTE proof hash                                              │
│     └── Hash entire receipt for integrity                          │
│                                                                     │
│  4. WRITE receipt                                                   │
│     ├── Store alongside artifact, or                               │
│     └── Store in centralized location                              │
│                                                                     │
│  Input: All stage hashes + metadata                                │
│  Output: receipt.json                                              │
└────────────────────────────────────────────────────────────────────┘
```

---

## Receipt Structure

### Complete Receipt Format

```json
{
  "version": "1.0",
  "schema": "https://spec-kit.dev/schemas/receipt-v1.json",

  "metadata": {
    "timestamp": "2025-01-15T10:30:00.000Z",
    "generator": "ggen",
    "generator_version": "5.0.2",
    "hostname": "build-server-01",
    "user": "ci-bot"
  },

  "input": {
    "file": "ontology/cli-commands.ttl",
    "hash": "sha256:a1b2c3d4e5f67890abcdef1234567890abcdef1234567890abcdef1234567890",
    "size": 15234,
    "modified": "2025-01-15T09:00:00.000Z"
  },

  "pipeline": {
    "config_file": "ggen.toml",
    "config_hash": "sha256:config123...",
    "target": "python-commands"
  },

  "stages": [
    {
      "name": "normalize",
      "inputs": [
        {
          "type": "shape",
          "file": "shapes/command-shape.ttl",
          "hash": "sha256:shape123..."
        }
      ],
      "output_hash": "sha256:norm123...",
      "duration_ms": 145
    },
    {
      "name": "extract",
      "inputs": [
        {
          "type": "query",
          "file": "sparql/command-extract.rq",
          "hash": "sha256:query123..."
        }
      ],
      "output_hash": "sha256:extract123...",
      "result_count": 42,
      "duration_ms": 234
    },
    {
      "name": "emit",
      "inputs": [
        {
          "type": "template",
          "file": "templates/command.py.tera",
          "hash": "sha256:template123..."
        }
      ],
      "output_hash": "sha256:emit123...",
      "duration_ms": 89
    },
    {
      "name": "canonicalize",
      "inputs": [
        {
          "type": "config",
          "settings": {
            "line_ending": "lf",
            "trailing_whitespace": "remove"
          }
        }
      ],
      "output_hash": "sha256:canon123...",
      "duration_ms": 12
    }
  ],

  "output": {
    "file": "src/commands/validate.py",
    "hash": "sha256:wxyz7890abcdef1234567890abcdef1234567890abcdef1234567890abcdef12",
    "size": 2847
  },

  "proof": {
    "algorithm": "sha256",
    "value": "sha256:final_proof_hash_covering_entire_receipt..."
  }
}
```

### Minimal Receipt Format

For simpler use cases:

```json
{
  "version": "1.0",
  "timestamp": "2025-01-15T10:30:00Z",
  "input": {
    "file": "ontology/cli-commands.ttl",
    "hash": "sha256:a1b2c3d4..."
  },
  "output": {
    "file": "src/commands/validate.py",
    "hash": "sha256:wxyz7890..."
  },
  "proof": "sha256:proof123..."
}
```

---

## Receipt Properties

### Property 1: Completeness

Every stage that affects the output is recorded. If you change anything—source, shape, query, template, config—the receipt changes.

### Property 2: Verifiability

Hashes can be independently computed. Anyone with access to the files can verify the receipt:

```python
def verify_receipt(receipt_path: Path) -> VerificationResult:
    receipt = load_receipt(receipt_path)

    # Verify input hash
    actual_input_hash = compute_hash(receipt.input.file)
    if actual_input_hash != receipt.input.hash:
        return VerificationResult(
            valid=False,
            reason=f"Input file changed: expected {receipt.input.hash}, got {actual_input_hash}"
        )

    # Verify output hash
    actual_output_hash = compute_hash(receipt.output.file)
    if actual_output_hash != receipt.output.hash:
        return VerificationResult(
            valid=False,
            reason=f"Output file modified: expected {receipt.output.hash}, got {actual_output_hash}"
        )

    # Verify stage inputs
    for stage in receipt.stages:
        for input in stage.inputs:
            if input.type == "shape" or input.type == "query" or input.type == "template":
                actual_hash = compute_hash(input.file)
                if actual_hash != input.hash:
                    return VerificationResult(
                        valid=False,
                        reason=f"Stage input changed: {input.file}"
                    )

    # Verify proof (optional: re-compute and compare)
    expected_proof = compute_proof(receipt)
    if expected_proof != receipt.proof.value:
        return VerificationResult(
            valid=False,
            reason="Receipt proof is invalid"
        )

    return VerificationResult(valid=True)
```

### Property 3: Tamper-Evidence

Any modification to the artifact invalidates the receipt:

```
Artifact modified:
  - Hash mismatch detected
  - Proof verification fails
  - Clear indication of tampering
```

### Property 4: Traceability

Every artifact links to its exact source:

```
validate.py
  └── generated from: cli-commands.ttl@sha256:abc123
      └── using shape: command-shape.ttl@sha256:def456
      └── using query: command-extract.rq@sha256:ghi789
      └── using template: command.py.tera@sha256:jkl012
```

---

## Receipt Storage

### Alongside Artifacts

Store receipts next to their artifacts:

```
src/commands/
├── validate.py           # Generated artifact
├── validate.py.receipt   # Receipt for validate.py
├── check.py
└── check.py.receipt
```

**Pros:** Easy to find, travels with artifact
**Cons:** Clutters directory, doubles file count

### Centralized Storage

Store all receipts in a dedicated directory:

```
receipts/
├── src-commands-validate.py.json
├── src-commands-check.py.json
├── docs-commands-validate.md.json
└── manifest.json  # Index of all receipts
```

**Pros:** Clean artifact directories, easy bulk verification
**Cons:** Requires mapping between artifacts and receipts

### Git Notes

Store receipts as git notes:

```bash
git notes add -m "$(cat receipt.json)" HEAD:src/commands/validate.py
```

**Pros:** Doesn't appear in working tree, versioned with git
**Cons:** Git notes are often overlooked, harder tooling

---

## Verification Workflows

### Quick Verification

Check if artifacts match receipts:

```bash
$ ggen verify

Verifying receipts...
  src/commands/validate.py: ✓ valid
  src/commands/check.py: ✓ valid
  docs/commands/validate.md: ✗ MODIFIED
    Expected: sha256:abc123...
    Actual:   sha256:def456...

1 of 3 artifacts have been modified.
Run 'ggen sync' to regenerate.
```

### Thorough Verification

Re-run transformation and compare:

```bash
$ ggen verify --thorough

Thorough verification...
  Regenerating src/commands/validate.py...
    Source hash: ✓ matches receipt
    Output hash: ✓ matches artifact
  Regenerating src/commands/check.py...
    Source hash: ✓ matches receipt
    Output hash: ✓ matches artifact

All artifacts verified through regeneration.
```

### CI Verification

```yaml
# .github/workflows/verify.yml
jobs:
  verify-receipts:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Verify receipts
        run: |
          ggen verify --strict
          # Fails if any receipt is invalid or missing

      - name: Verify regeneration is idempotent
        run: |
          ggen sync
          git diff --exit-code
          # Fails if regeneration changes anything
```

---

## Implementation

### Receipt Generation

```python
from dataclasses import dataclass
from datetime import datetime, UTC
import hashlib
import json
from pathlib import Path

@dataclass
class Receipt:
    version: str
    timestamp: str
    input_file: Path
    input_hash: str
    output_file: Path
    output_hash: str
    stages: list[dict]
    proof: str

def generate_receipt(
    input_file: Path,
    output_file: Path,
    stages: list[StageResult],
    config: Config
) -> Receipt:
    """Generate a receipt for a transformation."""

    # Compute input hash
    input_hash = compute_file_hash(input_file)

    # Compute output hash
    output_hash = compute_file_hash(output_file)

    # Build stage records
    stage_records = []
    for stage in stages:
        stage_records.append({
            "name": stage.name,
            "inputs": [
                {"type": inp.type, "file": str(inp.file), "hash": inp.hash}
                for inp in stage.inputs
            ],
            "output_hash": stage.output_hash,
            "duration_ms": stage.duration_ms
        })

    # Build receipt
    receipt_data = {
        "version": "1.0",
        "timestamp": datetime.now(UTC).isoformat(),
        "input": {"file": str(input_file), "hash": input_hash},
        "output": {"file": str(output_file), "hash": output_hash},
        "stages": stage_records
    }

    # Compute proof (hash of entire receipt)
    proof = compute_dict_hash(receipt_data)
    receipt_data["proof"] = proof

    return Receipt(**receipt_data)


def compute_file_hash(file_path: Path, algorithm: str = "sha256") -> str:
    """Compute hash of file contents."""
    hasher = hashlib.new(algorithm)
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return f"{algorithm}:{hasher.hexdigest()}"


def compute_dict_hash(data: dict, algorithm: str = "sha256") -> str:
    """Compute hash of dictionary (canonical JSON)."""
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
    hasher = hashlib.new(algorithm)
    hasher.update(canonical.encode("utf-8"))
    return f"{algorithm}:{hasher.hexdigest()}"
```

### Receipt Storage

```python
def store_receipt(receipt: Receipt, storage: str = "alongside") -> Path:
    """Store receipt in configured location."""

    if storage == "alongside":
        receipt_path = Path(f"{receipt.output_file}.receipt")
    elif storage == "centralized":
        receipt_path = Path("receipts") / f"{receipt.output_file.name}.json"
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        raise ValueError(f"Unknown storage mode: {storage}")

    with open(receipt_path, "w") as f:
        json.dump(receipt.to_dict(), f, indent=2)

    return receipt_path
```

---

## Configuration

```toml
# ggen.toml

[receipts]
enabled = true
storage = "alongside"  # alongside | centralized
algorithm = "sha256"
include_timing = true
include_hostname = false

# What to include in receipts
[receipts.include]
stage_inputs = true
stage_outputs = true
config_snapshot = true
environment = false

# Verification settings
[receipts.verification]
on_sync = true  # Verify existing receipts during sync
strict = true   # Fail if receipts missing
```

---

## Case Study: The Compliance Audit

*A team uses receipts to pass a rigorous compliance audit.*

### The Situation

FinanceCore needed SOC 2 Type II compliance. The auditor asked:

> "Can you demonstrate that your production code matches your documented specifications?"

Traditional answer: "We have a CI pipeline that runs tests."

Auditor: "Tests verify behavior, not provenance. Can you prove the code was generated from specifications?"

### The Solution

FinanceCore had been using receipts from the start:

**Step 1: Present the Evidence**

```bash
$ ggen verify --all --report=audit

AUDIT REPORT: 2025-01-15
========================

Verified Artifacts: 847
Receipt Coverage: 100%
All Verified: YES

Sample Verification Chain:
--------------------------
src/commands/transfer.py
  ├── Source: ontology/banking-commands.ttl
  │   └── Hash: sha256:abc123... ✓
  ├── Shape: shapes/transaction-shape.ttl
  │   └── Hash: sha256:def456... ✓
  ├── Query: sparql/transfer-extract.rq
  │   └── Hash: sha256:ghi789... ✓
  ├── Template: templates/command.py.tera
  │   └── Hash: sha256:jkl012... ✓
  └── Output: sha256:mno345... ✓ matches file

Signed: ggen v5.0.2 @ 2025-01-15T10:30:00Z
```

**Step 2: Demonstrate Regeneration**

```bash
$ ggen sync --dry-run

No changes detected.
All 847 artifacts match their specifications.
```

**Step 3: Show CI History**

```
CI Run History (last 30 days):
  - 127 runs
  - 0 verification failures
  - 100% receipt compliance
```

### The Result

The auditor wrote:

> "FinanceCore demonstrates cryptographic proof of code provenance. Their specification-driven development approach with receipt verification provides high assurance that production code accurately reflects documented specifications."

SOC 2 Type II: **PASSED**

---

## Anti-Patterns

### Anti-Pattern: Optional Receipts

*"Receipts are nice to have. We'll generate them when we remember."*

Without mandatory receipts, verification is impossible. "We generated this correctly" becomes an unprovable assertion.

**Resolution:** Receipts are mandatory. Every generated artifact gets one. CI fails without them.

### Anti-Pattern: Receipts Without Verification

*"We generate receipts but never check them."*

Receipts are only valuable if verified. Unverified receipts are just extra files.

**Resolution:** CI verifies receipts on every build. Pre-commit hooks verify locally.

### Anti-Pattern: Heavyweight Receipts

*"Let's include everything in the receipt—full source, full output, environment dump."*

This creates massive receipts that are slow to generate and store.

**Resolution:** Include hashes and references, not content. The content is in source control.

### Anti-Pattern: Receipt Drift

*"The receipt was valid when created. Who knows about now?"*

Receipts can become stale if sources change without regeneration.

**Resolution:** CI regenerates and re-verifies. Stale receipts are treated as failures.

---

## Implementation Checklist

### Receipt Generation

- [ ] Define receipt schema
- [ ] Implement hash computation
- [ ] Collect stage metadata
- [ ] Generate proof hash
- [ ] Store receipts

### Verification

- [ ] Implement quick verification (hash check)
- [ ] Implement thorough verification (regeneration)
- [ ] Add verification to CI
- [ ] Add pre-commit verification hook
- [ ] Create audit report generation

### Storage

- [ ] Configure storage location
- [ ] Implement alongside storage
- [ ] Implement centralized storage (if needed)
- [ ] Create receipt manifest

### Integration

- [ ] Fail CI if receipts missing
- [ ] Fail CI if verification fails
- [ ] Generate audit reports
- [ ] Document receipt workflow

---

## Resulting Context

After implementing this pattern, you have:

- **Cryptographic proof** for each generated artifact
- **Ability to verify** artifacts haven't been modified
- **Audit trail** of all transformations
- **Compliance evidence** for regulatory requirements
- **Automatic detection** of drift or tampering
- **Foundation for trust** in the generation system

Receipts complete the μ pipeline. They transform the Constitutional Equation from a principle into a provable guarantee.

---

## Code References

The following spec-kit source files implement the receipt generation stage (μ₅):

| Reference | Description |
|-----------|-------------|
| `src/specify_cli/runtime/receipt.py:1-15` | Module docstring explaining μ₅ RECEIPT purpose |
| `src/specify_cli/runtime/receipt.py:30-37` | StageHash dataclass for intermediate stage hashes |
| `src/specify_cli/runtime/receipt.py:39-59` | Receipt dataclass with all proof fields |
| `src/specify_cli/runtime/receipt.py:112-156` | generate_receipt() function creating cryptographic proof |
| `src/specify_cli/runtime/receipt.py:159-185` | verify_receipt() function for validation |

---

## Related Patterns

- **Part of:** **[21. Constitutional Equation](./constitutional-equation.md)** — Stage μ₅
- **Follows:** **[25. Canonicalization](./canonicalization.md)** — Final content for hashing
- **Verified by:** **[36. Receipt Verification](../verification/receipt-verification.md)** — Checking receipts
- **Supports:** **[35. Drift Detection](../verification/drift-detection.md)** — Detecting changes

---

## Philosophical Note

> *"In God we trust. All others must bring data."*
> — W. Edwards Deming

Receipts are the data. They transform trust from faith to verification. When someone claims "this artifact is correctly generated," the receipt provides the evidence. When an auditor asks "can you prove compliance," the receipt answers.

In a world of assertions, receipts provide proof. In a world of trust, receipts provide verification. This is not cynicism—it is engineering. We verify not because we distrust our colleagues, but because verification makes trust scalable.

---

**Next:** With the μ pipeline complete, explore **[27. Idempotent Transform](./idempotent-transform.md)** to understand why running the transformation twice produces the same result as running it once.
