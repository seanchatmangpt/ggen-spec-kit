# 35. Drift Detection

★★

*Generated artifacts should match their source. Drift detection identifies when artifacts have been modified outside the transformation pipeline—catching violations of the constitutional equation.*

---

The **[Constitutional Equation](../transformation/constitutional-equation.md)** promises that artifacts are generated from specifications. But what if someone edits an artifact directly? What if a merge conflict corrupts a generated file? What if a developer doesn't know a file is generated?

These situations create drift—divergence between source specification and generated artifact. Drift is insidious. The artifact works differently than the specification describes. Documentation doesn't match behavior. Tests don't test what's actually implemented.

Drift detection catches these violations before they cause harm.

**The problem: Manual edits to generated files violate the constitutional equation. Without detection, drift accumulates silently.**

---

**The forces at play:**

- *Convenience tempts editing.* "Just fix this one line" is easy.

- *Ignorance enables drift.* Not everyone knows which files are generated.

- *Time pressure accelerates drift.* "Regenerate later" becomes never.

- *Tooling can prevent drift.* Detection is the first step.

The tension: allow legitimate changes while catching illegitimate ones.

---

**Therefore:**

Implement drift detection that compares generated artifacts against their receipts and regenerated output.

**Detection methods:**

**1. Receipt verification**

Compare artifact hash against receipt:

```python
def check_drift_by_receipt(artifact_path: str) -> bool:
    """Check if artifact matches its receipt."""
    receipt_path = f"{artifact_path}.receipt"
    if not os.path.exists(receipt_path):
        return False  # No receipt = can't verify

    receipt = load_json(receipt_path)
    current_hash = compute_sha256(artifact_path)
    recorded_hash = receipt['output']['hash']

    return current_hash == recorded_hash
```

**2. Regeneration comparison**

Regenerate and compare:

```bash
# Save current state
cp output.py output.py.current

# Regenerate
ggen sync

# Compare
if diff output.py output.py.current > /dev/null; then
    echo "No drift ✓"
else
    echo "DRIFT DETECTED!"
    diff output.py output.py.current
fi
```

**3. Header check**

Verify generated header present:

```python
def has_generated_header(file_path: str) -> bool:
    """Check if file has 'do not edit' header."""
    with open(file_path) as f:
        header = f.read(500)  # First 500 chars
    return "AUTO-GENERATED" in header or "DO NOT EDIT" in header
```

**CI integration:**

```yaml
# .github/workflows/drift.yml
- name: Check for drift
  run: |
    # Regenerate all artifacts
    ggen sync

    # Check if anything changed
    if ! git diff --exit-code; then
      echo "⚠️  DRIFT DETECTED"
      echo "Generated files don't match their sources."
      echo "Either:"
      echo "  1. Someone edited a generated file (fix by regenerating)"
      echo "  2. Source changed but artifacts weren't regenerated (run ggen sync)"
      git diff --stat
      exit 1
    fi

    echo "✓ No drift detected"
```

**Developer feedback:**

```
$ ggen verify

Checking artifacts for drift...

src/commands/validate.py
  Receipt: VALID ✓
  Content: MATCHES ✓

src/commands/check.py
  Receipt: VALID ✓
  Content: DRIFT DETECTED ⚠️

  Lines changed: 3
  Diff:
    -    """Check tool availability."""
    +    """Check tool availability. (Modified for testing)"""

  This file appears to have been manually edited.
  To fix: Run 'ggen sync' to regenerate from source.

docs/commands/validate.md
  Receipt: MISSING (no receipt file)
  Content: UNKNOWN

Summary: 1 drifted, 1 unverified, 1 clean
```

**Preventing drift:**

| Prevention | How |
|------------|-----|
| Clear headers | Mark generated files obviously |
| .gitattributes | Warn on editing generated files |
| Pre-commit hooks | Verify no drift before commit |
| IDE plugins | Highlight generated files |
| Documentation | Educate team on process |

---

**Resulting context:**

After applying this pattern, you have:

- Detection of manually-edited generated files
- CI enforcement of constitutional equation
- Clear feedback when drift occurs
- Foundation for trusted automation

This verifies **[21. Constitutional Equation](../transformation/constitutional-equation.md)** and supports **[37. Continuous Validation](./continuous-validation.md)**.

---

**Related patterns:**

- *Verifies:* **[21. Constitutional Equation](../transformation/constitutional-equation.md)** — Equation enforced
- *Uses:* **[26. Receipt Generation](../transformation/receipt-generation.md)** — Receipts enable detection
- *Enables:* **[37. Continuous Validation](./continuous-validation.md)** — CI drift checks
- *Supports:* **[27. Idempotent Transform](../transformation/idempotent-transform.md)** — Regeneration safe

---

> *"Trust, but verify."*

Drift detection is the verification. The constitutional equation is trusted; drift detection ensures it's honored.
