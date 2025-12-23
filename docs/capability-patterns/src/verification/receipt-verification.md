# 36. Receipt Verification

★★

*Receipts are proofs. Receipt verification checks those proofs, confirming that artifacts were correctly generated from their claimed sources.*

---

**[Receipt Generation](../transformation/receipt-generation.md)** creates cryptographic proofs. Receipt verification checks them.

A receipt claims:
- This artifact was generated from this source
- Through these stages
- At this time
- With this hash

Verification confirms these claims are true—or reveals they're false.

**The problem: Receipts without verification are just claims. Verification makes them proofs.**

---

**The forces at play:**

- *Trust wants assurance.* Is this really generated correctly?

- *Performance wants speed.* Full verification can be slow.

- *Completeness wants thoroughness.* Every claim should be checked.

- *Practicality wants usability.* Verification should be easy to run.

The tension: thorough enough to be trustworthy, fast enough to run regularly.

---

**Therefore:**

Implement receipt verification at multiple levels—from quick hash checks to full regeneration comparison.

**Verification levels:**

**Level 1: Hash check (fast)**
```python
def verify_artifact_hash(artifact_path: str) -> bool:
    """Verify artifact matches receipt hash."""
    receipt = load_receipt(artifact_path)
    current_hash = compute_sha256(artifact_path)
    return current_hash == receipt['output']['hash']
```

**Level 2: Source check (medium)**
```python
def verify_source_unchanged(artifact_path: str) -> bool:
    """Verify source hasn't changed since generation."""
    receipt = load_receipt(artifact_path)
    current_source_hash = compute_sha256(receipt['input']['file'])
    return current_source_hash == receipt['input']['hash']
```

**Level 3: Full regeneration (slow)**
```python
def verify_by_regeneration(artifact_path: str) -> bool:
    """Regenerate and compare."""
    receipt = load_receipt(artifact_path)

    # Regenerate to temporary location
    regenerated = regenerate_to_temp(receipt['input']['file'])

    # Compare
    current_hash = compute_sha256(artifact_path)
    regenerated_hash = compute_sha256(regenerated)

    return current_hash == regenerated_hash
```

**Verification report:**

```
$ ggen verify --thorough

Receipt Verification Report
═══════════════════════════════════════════════════════════

Artifact: src/commands/validate.py
───────────────────────────────────────────────────────────
  Source:     ontology/cli-commands.ttl
  Generated:  2025-01-15T10:30:00Z
  Generator:  ggen v5.0.2

  Checks:
    ✓ Artifact hash matches receipt
    ✓ Source file exists
    ✓ Source hash matches (unchanged since generation)
    ✓ Template hash matches
    ✓ Shape hash matches
    ✓ Regeneration produces identical output

  Status: VERIFIED ✓

Artifact: src/commands/check.py
───────────────────────────────────────────────────────────
  Source:     ontology/cli-commands.ttl
  Generated:  2025-01-15T10:30:00Z
  Generator:  ggen v5.0.2

  Checks:
    ✓ Artifact hash matches receipt
    ✓ Source file exists
    ✗ Source hash CHANGED since generation

  Status: STALE - regeneration needed

  Recommendation: Run 'ggen sync' to update

═══════════════════════════════════════════════════════════
Summary: 1 verified, 1 stale, 0 invalid
```

**CI integration:**

```yaml
# .github/workflows/verify.yml
jobs:
  verify-receipts:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Quick verification (Level 1)
        run: ggen verify --level hash

      - name: Full verification (Level 3)
        if: github.event_name == 'release'
        run: ggen verify --level regenerate
```

**Verification modes:**

| Mode | Speed | Checks | Use Case |
|------|-------|--------|----------|
| hash | Fast | Artifact hash only | Every commit |
| source | Medium | + source unchanged | Pull requests |
| regenerate | Slow | + full regeneration | Releases |

---

**Resulting context:**

After applying this pattern, you have:

- Verified proofs for all generated artifacts
- Multiple verification levels for different contexts
- Clear reports of verification status
- Foundation for trusted artifact supply chain

This verifies **[26. Receipt Generation](../transformation/receipt-generation.md)** and supports **[37. Continuous Validation](./continuous-validation.md)**.

---

**Related patterns:**

- *Verifies:* **[26. Receipt Generation](../transformation/receipt-generation.md)** — Receipts checked
- *Complements:* **[35. Drift Detection](./drift-detection.md)** — Different approach
- *Enables:* **[37. Continuous Validation](./continuous-validation.md)** — CI verification
- *Part of:* **[21. Constitutional Equation](../transformation/constitutional-equation.md)** — Equation verified

---

> *"The proof of the pudding is in the eating."*

The proof of generation is in the verification. Receipts claim correctness; verification proves it.
