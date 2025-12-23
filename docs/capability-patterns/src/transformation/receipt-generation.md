# 26. Receipt Generation

★★

*Trust, but verify. Receipt generation (μ₅) creates cryptographic proof that artifacts were correctly generated from their source specifications.*

---

You've transformed specification to artifact through normalization, extraction, emission, and canonicalization. How do you know it was done correctly? How can others verify?

Receipts provide the answer. They're cryptographic proofs that record:
- What source was transformed
- What stages it passed through
- What output was produced
- When transformation occurred

With receipts, you can verify that any artifact matches its claimed source. You can detect tampering. You can audit the transformation history.

**The problem: Without proof, claims of correct transformation are just assertions. Receipts make verification automatic and trustworthy.**

---

**The forces at play:**

- *Trust wants assurance.* How do I know this was generated correctly?

- *Performance wants speed.* Cryptographic operations have cost.

- *Storage wants efficiency.* Receipts add to repository size.

- *Verification wants simplicity.* Complex proofs are hard to check.

The tension: thorough enough to provide real assurance, practical enough to use routinely.

---

**Therefore:**

Implement receipt generation (μ₅) as the final transformation stage, producing a cryptographic proof for each artifact.

**Receipt structure:**

```json
{
  "version": "1.0",
  "timestamp": "2025-01-15T10:30:00Z",
  "transformer": "ggen v5.0.2",

  "input": {
    "file": "ontology/cli-commands.ttl",
    "hash": "sha256:a1b2c3d4e5f6..."
  },

  "stages": [
    {
      "stage": "normalize",
      "shape": "shapes/command-shape.ttl",
      "shape_hash": "sha256:1234abcd...",
      "output_hash": "sha256:5678efgh..."
    },
    {
      "stage": "extract",
      "query": "sparql/command-extract.rq",
      "query_hash": "sha256:9abc1234...",
      "output_hash": "sha256:def56789..."
    },
    {
      "stage": "emit",
      "template": "templates/command.py.tera",
      "template_hash": "sha256:ghij2345...",
      "output_hash": "sha256:klmn6789..."
    },
    {
      "stage": "canonicalize",
      "config_hash": "sha256:opqr3456...",
      "output_hash": "sha256:stuv7890..."
    }
  ],

  "output": {
    "file": "src/commands/validate.py",
    "hash": "sha256:wxyz1234..."
  },

  "proof": "sha256:final_proof_hash..."
}
```

**Receipt properties:**

1. **Completeness** — Every stage recorded with inputs and outputs
2. **Verifiability** — Hashes can be independently computed
3. **Tamper-evidence** — Any modification invalidates the proof
4. **Traceability** — Links artifact to exact source version

**Verification process:**

```python
def verify_receipt(receipt_path: str, artifact_path: str) -> bool:
    """Verify artifact matches its receipt."""
    receipt = load_json(receipt_path)

    # 1. Verify artifact hash
    actual_hash = compute_sha256(artifact_path)
    if actual_hash != receipt['output']['hash']:
        return False  # Artifact was modified

    # 2. Verify source exists and matches
    source_hash = compute_sha256(receipt['input']['file'])
    if source_hash != receipt['input']['hash']:
        return False  # Source changed since generation

    # 3. Verify stage chain
    for stage in receipt['stages']:
        # Each stage's output should be recomputable
        # (Optional: re-run stage and compare)
        pass

    return True
```

**Receipt storage:**

```
src/commands/
├── validate.py           # Generated artifact
├── validate.py.receipt   # Receipt for validate.py
├── check.py
└── check.py.receipt
```

Or centralized:

```
receipts/
├── src-commands-validate.py.receipt
├── src-commands-check.py.receipt
└── docs-validate.md.receipt
```

---

**Resulting context:**

After applying this pattern, you have:

- Cryptographic proof for each generated artifact
- Ability to verify artifacts haven't been modified
- Audit trail of all transformations
- Foundation for **[Receipt Verification](../verification/receipt-verification.md)**

This completes the μ pipeline and enables **[Drift Detection](../verification/drift-detection.md)**.

---

**Related patterns:**

- *Part of:* **[21. Constitutional Equation](./constitutional-equation.md)** — Stage μ₅
- *Follows:* **[25. Canonicalization](./canonicalization.md)** — Final stage
- *Verified by:* **[36. Receipt Verification](../verification/receipt-verification.md)** — Checking receipts
- *Supports:* **[35. Drift Detection](../verification/drift-detection.md)** — Detecting changes

---

> *"In God we trust. All others must bring data."*
>
> — W. Edwards Deming

Receipts are the data. They transform trust from faith to verification.
