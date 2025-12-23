# 27. Idempotent Transform

★★

*μ ∘ μ = μ. Running the transformation twice produces the same result as running it once. Idempotence enables safe regeneration, confident CI, and predictable workflows.*

---

The **[Constitutional Equation](./constitutional-equation.md)** promises that artifacts are generated from specifications. But what happens when you regenerate? Does output change? Does regeneration introduce variation?

Idempotence is the property that regeneration is stable:

```
μ(specification) = μ(μ(specification))
```

Or more practically: running `ggen sync` twice produces identical output. The second run doesn't change anything.

This property is essential for:
- **Safe regeneration:** "Just regenerate to be sure" is always safe
- **CI pipelines:** Verify no changes after regeneration
- **Team workflows:** Different team members get identical results
- **Debugging:** Regenerate without fear of side effects

**The problem: Non-idempotent transformations create drift, break CI, and erode confidence in the generation system.**

---

**The forces at play:**

- *Timestamps want currency.* Generated-at timestamps change each run.

- *Randomness wants variation.* UUIDs, random orders introduce variation.

- *Environments differ.* Different platforms produce different output.

- *Stability wants determinism.* Same input should yield same output.

The tension: include useful metadata without breaking idempotence.

---

**Therefore:**

Design transformations to be idempotent by eliminating all sources of variation.

**Sources of non-idempotence and solutions:**

| Source | Problem | Solution |
|--------|---------|----------|
| Timestamps | Change each run | Use source file mtime, not generation time |
| Random values | UUIDs, random order | Deterministic generation, sorted output |
| Environment | Platform differences | Canonicalization normalizes |
| Floating-point | Representation varies | Use string/decimal representations |
| Dictionary order | Varies by Python version | Sort keys explicitly |
| File system order | Varies by OS | Sort file lists explicitly |

**Timestamp handling:**

```python
# Non-idempotent (bad)
generated_at = datetime.now().isoformat()

# Idempotent (good)
source_mtime = os.path.getmtime(source_file)
generated_at = datetime.fromtimestamp(source_mtime).isoformat()
```

**Ordered output:**

```python
# Non-idempotent (bad)
for item in items:  # Order may vary
    emit(item)

# Idempotent (good)
for item in sorted(items, key=lambda x: x['name']):
    emit(item)
```

**SPARQL query ordering:**

```sparql
# Non-idempotent (bad)
SELECT ?name ?value WHERE { ?s ?p ?o }

# Idempotent (good)
SELECT ?name ?value WHERE { ?s ?p ?o }
ORDER BY ?name ?value
```

**Verification:**

```bash
# Verify idempotence
ggen sync
HASH1=$(sha256sum output.py)

ggen sync  # Run again
HASH2=$(sha256sum output.py)

if [ "$HASH1" = "$HASH2" ]; then
    echo "Idempotent ✓"
else
    echo "NOT IDEMPOTENT - output changed!"
    diff <(ggen sync --dry-run) output.py
fi
```

**CI check:**

```yaml
# .github/workflows/verify.yml
- name: Verify generation is idempotent
  run: |
    ggen sync
    git diff --exit-code || (echo "Generation produced changes!" && exit 1)
```

---

**Resulting context:**

After applying this pattern, you have:

- Safe regeneration at any time
- CI that verifies no drift
- Team consistency across environments
- Confidence in the transformation system

This supports **[Drift Detection](../verification/drift-detection.md)** and enables **[Continuous Validation](../verification/continuous-validation.md)**.

---

**Related patterns:**

- *Property of:* **[21. Constitutional Equation](./constitutional-equation.md)** — μ must be idempotent
- *Requires:* **[25. Canonicalization](./canonicalization.md)** — Consistent formatting
- *Enables:* **[35. Drift Detection](../verification/drift-detection.md)** — Compare regenerated
- *Supports:* **[37. Continuous Validation](../verification/continuous-validation.md)** — CI checks

---

> *"Idempotence is the property that makes distributed systems tractable."*

It also makes generation systems trustworthy. When regeneration is always safe, you can regenerate with confidence.
