# 21. Constitutional Equation

★★

*The most important equation in specification-driven development:*

```
spec.md = μ(feature.ttl)
```

*Human-readable artifacts are generated from formal specifications. This constitutional principle eliminates drift, enables automation, and guarantees consistency.*

---

Everything you've built so far—the understanding of **[Customer Jobs](../context/customer-job.md)**, the formal **[Specifications](../specification/executable-specification.md)**, the **[Traceability Threads](../specification/traceability-thread.md)**—leads to this moment.

The Constitutional Equation inverts traditional development:

**Traditional:** Write code and docs separately, hope they stay synchronized.
**Constitutional:** Define specifications formally, generate code and docs as artifacts.

The function μ (mu) represents a deterministic transformation pipeline. Given the same input specification, μ always produces the same output artifact. This is not compilation in the traditional sense—it's materialization of intent.

**The problem: When code and documentation are authored independently, they drift apart. Drift creates bugs, confusion, and wasted reconciliation effort.**

---

**The forces at play:**

- *Convenience favors direct authoring.* It's faster to edit the output directly.

- *Consistency demands single source.* Multiple sources inevitably diverge.

- *Trust requires verification.* Artifacts must be provably correct.

- *Automation enables scale.* Manual synchronization doesn't scale.

The constitutional equation resolves these forces by making the relationship between source and artifact explicit, deterministic, and verifiable.

---

**Therefore:**

Adopt the constitutional equation as a fundamental principle: every human-readable artifact is generated from formal RDF specifications through the μ transformation.

**The equation:**

```
spec.md = μ(feature.ttl)
```

Where:
- `feature.ttl` — Source specification in RDF/Turtle
- `μ` — Deterministic transformation pipeline
- `spec.md` — Generated artifact (Markdown, code, config)

**The μ pipeline:**

```
feature.ttl → μ₁ → μ₂ → μ₃ → μ₄ → μ₅ → spec.md + receipt.json
               │     │     │     │     │
               │     │     │     │     └─ RECEIPT (hash proof)
               │     │     │     └─ CANONICALIZE (format)
               │     │     └─ EMIT (template render)
               │     └─ EXTRACT (SPARQL query)
               └─ NORMALIZE (SHACL validation)
```

**Five stages:**

1. **μ₁ NORMALIZE** — Validate source against SHACL shapes
2. **μ₂ EXTRACT** — Execute SPARQL queries to extract data
3. **μ₃ EMIT** — Render templates with extracted data
4. **μ₄ CANONICALIZE** — Normalize format (line endings, whitespace)
5. **μ₅ RECEIPT** — Generate cryptographic proof of transformation

**Implications:**

1. **Never edit generated files.** If you see something wrong in spec.md, fix feature.ttl and regenerate.

2. **Regeneration is safe.** Running μ again produces identical output (idempotent).

3. **Artifacts are traceable.** Every artifact links to its source specification.

4. **Verification is automatic.** Receipts prove transformation correctness.

**Configuration:**

```toml
# ggen.toml - transformation configuration
[[targets]]
source = "ontology/cli-commands.ttl"
query = "sparql/command-extract.rq"
template = "templates/command.py.tera"
output = "src/commands/{{ name }}.py"
shape = "shapes/command-shape.ttl"
```

---

**Resulting context:**

After applying this pattern, you have:

- A constitutional principle governing all artifact generation
- Elimination of drift between source and artifacts
- Automated, reproducible transformation
- Cryptographic verification of consistency

This pattern is implemented through the following patterns: **[Normalization Stage](./normalization-stage.md)**, **[Extraction Query](./extraction-query.md)**, **[Template Emission](./template-emission.md)**, **[Canonicalization](./canonicalization.md)**, **[Receipt Generation](./receipt-generation.md)**.

---

**Related patterns:**

- *Implemented by:* **[22-26. Pipeline stages](./normalization-stage.md)**
- *Requires:* **[10. Single Source of Truth](../specification/single-source-of-truth.md)**
- *Verified by:* **[36. Receipt Verification](../verification/receipt-verification.md)**
- *Enables:* **[27. Idempotent Transform](./idempotent-transform.md)**

---

> *"A constitution is not the act of a government, but of a people constituting a government."*
>
> — Thomas Paine

The constitutional equation is the founding principle of specification-driven development. All other patterns derive their authority from this fundamental relationship.

---

**Why "constitutional"?**

We call this equation "constitutional" because:

1. **It is foundational.** All other patterns build on this principle.

2. **It is constraining.** It limits what can be done (no direct artifact editing).

3. **It is enabling.** It enables automation, verification, and trust.

4. **It is inviolable.** Violations are detected and rejected.

Like a constitution, this equation defines the fundamental relationship that governs everything else.
